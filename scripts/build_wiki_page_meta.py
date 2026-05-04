#!/usr/bin/env python3
"""Build a per-page metadata file for the explorer:
- title, category, subcategory (inferred), tags
- cleaned plain-text body, headings, first-paragraph excerpt
- token list (lowercased, deduped, no stopwords) for BM25 scoring

Output: wiki/explorer/shared/wiki-page-meta.json
"""
from __future__ import annotations
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WIKI_PAGES = ROOT / "wiki" / "pages"
OUT = ROOT / "wiki" / "explorer" / "shared" / "wiki-page-meta.json"

CATEGORIES = ["sources", "entities", "concepts", "syntheses", "claims", "data", "interventions"]

# Light English stopword list -- enough for BM25 over a focused KB.
STOPWORDS = set("""
a an the and or but if else for of in on at to from by with as is are was were be been being have has had do does did
not no nor so very can could should would may might must will shall this that these those it its i you he she they we
us them his her him their our your my me one two three some any all most more less than then also too here there when where why how
which what who whom whose into onto over under between within across about against amongst per via while during after before since until
also although still yet only just even ever never really often always sometimes maybe perhaps because however therefore thus hence such
each both either neither many few several other another same different new old high low big small large great good bad first second next last
own out up down off above below near far inside outside through throughout off through s t d m re ve ll
""".split())

TITLE_RE = re.compile(r"^title:\s*(.+?)\s*$", re.MULTILINE)
TAGS_RE = re.compile(r"^tags:\s*\[(.+?)\]\s*$", re.MULTILINE)
TYPE_RE = re.compile(r"^type:\s*(.+?)\s*$", re.MULTILINE)
IMAGES_BLOCK_RE = re.compile(r"^images:\s*\n((?:\s+-\s.*\n?|\s{2,}.*\n?)+)", re.MULTILINE)
IMAGE_ITEM_RE = re.compile(r"-\s*src\s*:\s*(\S+)")
GENERATOR_RE = re.compile(r"^generator:\s*(.+?)\s*$", re.MULTILINE)
UPDATED_RE = re.compile(r"^updated:\s*(.+?)\s*$", re.MULTILINE)
SUPERSEDED_RE = re.compile(r"<!--\s*superseded-by:\s*(\S+)\s*-->")
HEADING_RE = re.compile(r"^#{1,4}\s+(.+?)\s*$", re.MULTILINE)
WIKILINK_RE = re.compile(r"\[\[([^\]|]+?)(?:\|[^\]]+)?\]\]")
MD_LINK_RE = re.compile(r"\[([^\]]+)\]\([^)]+\)")
INLINE_CODE_RE = re.compile(r"`[^`]+`")
HTML_RE = re.compile(r"<[^>]+>")
TOKEN_RE = re.compile(r"[a-z0-9][a-z0-9\-_/]+")


def split_frontmatter(text: str) -> tuple[str, str]:
    if not text.startswith("---"):
        return "", text
    end = text.find("\n---", 4)
    if end == -1:
        return "", text
    return text[4:end].strip(), text[end + 4 :].lstrip("\n")


def clean_body(body: str) -> str:
    """Strip markdown formatting to plain text suitable for snippet display + tokenization."""
    body = WIKILINK_RE.sub(r"\1", body)
    body = MD_LINK_RE.sub(r"\1", body)
    body = INLINE_CODE_RE.sub(" ", body)
    body = HTML_RE.sub(" ", body)
    body = re.sub(r"^[#>*\-+|]\s*", "", body, flags=re.MULTILINE)
    body = re.sub(r"\*\*?", "", body)
    body = re.sub(r"\s+", " ", body).strip()
    return body


def first_paragraph(body: str) -> str:
    body = WIKILINK_RE.sub(r"\1", body)
    body = MD_LINK_RE.sub(r"\1", body)
    paras = [p.strip() for p in re.split(r"\n\n+", body) if p.strip()]
    for p in paras:
        if p.startswith("#") or p.startswith("---") or p.startswith("|"):
            continue
        return clean_body(p)[:280]
    return ""


def tokenize(text: str) -> list[str]:
    return [t for t in TOKEN_RE.findall(text.lower()) if t not in STOPWORDS and len(t) > 2]


def infer_subcategory(slug: str, category: str, tags: list[str]) -> str:
    """For entities only -- assign a sub-bucket so the nav can show structure."""
    if category != "entities":
        return ""
    s = slug.lower()
    tagset = {t.strip().lower() for t in tags}
    if s.endswith("-basin") or "basin" in tagset:
        return "basins"
    if any(t in tagset for t in ["institution", "agency", "regulator", "utility"]):
        return "institutions"
    if s in {"nea", "wecs"} or "nea" in s or "wecs" in s or "ministry" in s:
        return "institutions"
    if "trade-route" in s or "interconnection" in s or "trade" in tagset or "geopolitics" in tagset or "treaty" in tagset:
        return "geopolitics"
    if "model" in s or s.startswith("bhutan-") or s.startswith("india-") or s.startswith("bangladesh-"):
        return "geopolitics"
    if "profile" in s or "profile" in tagset:
        return "profiles"
    if any(t in tagset for t in ["project", "hydropower", "storage", "cascade"]) or "project" in s or "storage" in s or "cascade" in s or "hydropower" in s:
        return "projects"
    return "other"


def parse_tags(fm: str) -> list[str]:
    m = TAGS_RE.search(fm)
    if not m:
        return []
    raw = m.group(1)
    return [t.strip().strip('"').strip("'") for t in raw.split(",") if t.strip()]


def main() -> None:
    pages: list[dict] = []
    df: Counter[str] = Counter()  # document frequency for IDF

    for cat in CATEGORIES:
        d = WIKI_PAGES / cat
        if not d.exists():
            continue
        for md in sorted(d.glob("*.md")):
            slug = md.stem
            text = md.read_text(encoding="utf-8")
            fm, body = split_frontmatter(text)
            title_m = TITLE_RE.search(fm)
            type_m = TYPE_RE.search(fm)
            tags = parse_tags(fm)
            headings = HEADING_RE.findall(body)
            cleaned = clean_body(body)
            excerpt = first_paragraph(body)
            tokens = tokenize(f"{title_m.group(1) if title_m else slug} {' '.join(tags)} {' '.join(headings)} {cleaned}")
            unique = sorted(set(tokens))
            for t in unique:
                df[t] += 1
            img_block_m = IMAGES_BLOCK_RE.search(fm)
            image_count = 0
            if img_block_m:
                image_count = len(IMAGE_ITEM_RE.findall(img_block_m.group(1)))
            gen_m = GENERATOR_RE.search(fm)
            up_m = UPDATED_RE.search(fm)
            sup_m = SUPERSEDED_RE.search(body)
            pages.append({
                "slug": slug,
                "title": title_m.group(1).strip() if title_m else slug,
                "category": cat,
                "type": type_m.group(1).strip() if type_m else cat[:-1] if cat.endswith("s") else cat,
                "subcategory": infer_subcategory(slug, cat, tags),
                "tags": tags,
                "headings": headings,
                "excerpt": excerpt,
                "body_text": cleaned,
                "token_freq": dict(Counter(tokens)),
                "image_count": image_count,
                "is_stub": (gen_m.group(1).strip() == "auto-stub") if gen_m else False,
                "updated": up_m.group(1).strip() if up_m else None,
                "superseded_by": sup_m.group(1).strip() if sup_m else None,
            })

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({
        "pages": pages,
        "doc_freq": dict(df),
        "total_pages": len(pages),
    }, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)} ({len(pages)} pages, {len(df)} unique tokens)")
    # Quick subcategory report.
    sub = Counter(p["subcategory"] for p in pages if p["category"] == "entities")
    print(f"  entities subcategories: {dict(sub)}")

    # Write slim version for explorer startup — slug-indexed, ~50KB not ~2MB.
    slim = {}
    for p in pages:
        entry = {
            "t": p["title"],
            "c": p["category"],
            "e": p["excerpt"],
            "g": p["tags"],
            "s": p["is_stub"],
            "u": p["updated"],
            "b": p["superseded_by"],
            "sc": p.get("subcategory", ""),
        }
        # Strip None values and empty strings to save bytes
        slim[p["slug"]] = {k: v for k, v in entry.items() if v is not None and v != ""}
    slim_out = OUT.parent / "wiki-page-meta-slim.json"
    slim_out.write_text(json.dumps(slim, separators=(",", ":"), ensure_ascii=False), encoding="utf-8")
    print(f"wrote {slim_out.relative_to(ROOT)} ({len(slim)} slugs, {slim_out.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
