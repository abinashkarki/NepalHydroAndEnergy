#!/usr/bin/env python3
"""Build chunk-level vectors for the explorer's progressive Seek boost.

This is intentionally a build-time tool. The browser only embeds the user's
query and compares it with this compact int8 vector file.
"""
from __future__ import annotations

import argparse
import base64
import json
import re
import time
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parent.parent
META = ROOT / "wiki" / "explorer" / "shared" / "wiki-page-meta.json"
OUT = ROOT / "wiki" / "explorer" / "shared" / "wiki-vector-index.json"
WIKI_PAGES = ROOT / "wiki" / "pages"
CATEGORIES = ["sources", "entities", "concepts", "syntheses", "claims", "data"]
DEFAULT_MODEL = "mixedbread-ai/mxbai-embed-xsmall-v1"
DEFAULT_BROWSER_MODEL = "mixedbread-ai/mxbai-embed-xsmall-v1"

FRONTMATTER_RE = re.compile(r"^---\n.*?\n---\n", re.S)
HEADING_SPLIT_RE = re.compile(r"(?m)^(#{1,4})\s+(.+?)\s*$")
MD_LINK_RE = re.compile(r"\[([^\]]+)\]\([^)]+\)")
WIKILINK_RE = re.compile(r"\[\[([^\]|]+)(?:\|[^\]]+)?\]\]")
HTML_RE = re.compile(r"<[^>]+>")


def strip_frontmatter(text: str) -> str:
    return FRONTMATTER_RE.sub("", text, count=1)


def clean_markdown(text: str) -> str:
    text = WIKILINK_RE.sub(r"\1", text)
    text = MD_LINK_RE.sub(r"\1", text)
    text = HTML_RE.sub(" ", text)
    text = re.sub(r"`([^`]+)`", r"\1", text)
    text = re.sub(r"[*_]{1,3}", "", text)
    text = re.sub(r"!\[[^\]]*\]\([^)]+\)", " ", text)
    text = re.sub(r"^[>*+\-|]\s*", "", text, flags=re.M)
    return re.sub(r"\s+", " ", text).strip()


def split_sections(body: str) -> list[tuple[str, str]]:
    matches = list(HEADING_SPLIT_RE.finditer(body))
    if not matches:
        return [("", clean_markdown(body))]
    sections: list[tuple[str, str]] = []
    lead = clean_markdown(body[: matches[0].start()])
    if lead:
        sections.append(("", lead))
    for idx, match in enumerate(matches):
        start = match.end()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(body)
        heading = clean_markdown(match.group(2))
        text = clean_markdown(body[start:end])
        if heading or text:
            sections.append((heading, text))
    return sections


def window_text(text: str, max_chars: int = 1400, overlap: int = 180) -> list[str]:
    if len(text) <= max_chars:
        return [text]
    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = min(len(text), start + max_chars)
        if end < len(text):
            boundary = max(text.rfind(". ", start, end), text.rfind("; ", start, end), text.rfind(" ", start, end))
            if boundary > start + 500:
                end = boundary + 1
        chunks.append(text[start:end].strip())
        if end >= len(text):
            break
        start = max(0, end - overlap)
    return [c for c in chunks if c]


def page_path(category: str, slug: str) -> Path:
    return WIKI_PAGES / category / f"{slug}.md"


def build_chunks(meta: dict, max_chunks_per_page: int = 10) -> tuple[list[dict], list[str]]:
    pages = meta["pages"]
    chunks: list[dict] = []
    texts: list[str] = []
    slug_to_id = {p["slug"]: idx for idx, p in enumerate(pages)}
    for page in pages:
        path = page_path(page["category"], page["slug"])
        if path.exists():
            body = strip_frontmatter(path.read_text(encoding="utf-8"))
        else:
            body = page.get("body_text", "")
        tags = ", ".join(page.get("tags") or [])
        title = page.get("title") or page["slug"]
        summary = ". ".join(
            part
            for part in [
                title,
                tags,
                page.get("excerpt", ""),
                ". ".join((page.get("headings") or [])[:6]),
            ]
            if part
        )
        page_chunks: list[tuple[str, str, str]] = [("Overview", summary, page.get("excerpt", ""))]
        for heading, section in split_sections(body):
            if not section and not heading:
                continue
            label = heading or "Body"
            for piece in window_text(section):
                page_chunks.append((label, piece, piece[:260]))
        for heading, content, snippet in page_chunks[:max_chunks_per_page]:
            text = f"{title}. {tags}. {heading}. {content}"
            chunks.append({
                "p": slug_to_id[page["slug"]],
                "h": heading[:96],
                "s": clean_markdown(snippet)[:280],
            })
            texts.append(text)
    return chunks, texts


def encode_texts(texts: list[str], model_id: str, batch_size: int, local_files_only: bool) -> np.ndarray:
    from sentence_transformers import SentenceTransformer

    model = SentenceTransformer(model_id, trust_remote_code=True, local_files_only=local_files_only)
    embeddings = model.encode(
        texts,
        batch_size=batch_size,
        normalize_embeddings=True,
        show_progress_bar=True,
    )
    return np.asarray(embeddings, dtype=np.float32)


def quantize_int8(embeddings: np.ndarray) -> list[str]:
    clipped = np.clip(np.rint(embeddings * 127), -127, 127).astype(np.int8)
    return [base64.b64encode(row.tobytes()).decode("ascii") for row in clipped]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--browser-model", default=DEFAULT_BROWSER_MODEL)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--local-files-only", action="store_true")
    args = parser.parse_args()

    meta = json.loads(META.read_text(encoding="utf-8"))
    chunks, texts = build_chunks(meta)
    started = time.time()
    embeddings = encode_texts(texts, args.model, args.batch_size, args.local_files_only)
    dim = int(embeddings.shape[1])
    vectors = quantize_int8(embeddings)
    # Quantization drift sanity: normalized int8 vectors should stay close.
    approx = np.asarray([np.frombuffer(base64.b64decode(v), dtype=np.int8).astype(np.float32) / 127 for v in vectors])
    norms = np.linalg.norm(approx, axis=1)
    mean_norm = round(float(np.mean(norms)), 4) if len(norms) else None
    out = {
        "version": 1,
        "model": {
            "id": args.model,
            "browser_id": args.browser_model,
            "dim": dim,
            "dtype": "int8_unit",
            "pooling": "mean",
            "normalize": True,
            "query_prefix": "Represent this sentence for searching relevant passages: ",
        },
        "stats": {
            "pages": len(meta["pages"]),
            "chunks": len(chunks),
            "built_at": int(time.time()),
            "build_seconds": round(time.time() - started, 2),
            "mean_quantized_norm": mean_norm,
        },
        "chunks": [{**chunk, "v": vector} for chunk, vector in zip(chunks, vectors)],
    }
    OUT.write_text(json.dumps(out, separators=(",", ":"), ensure_ascii=False), encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)} ({len(chunks)} chunks, dim={dim}, model={args.model})")


if __name__ == "__main__":
    main()
