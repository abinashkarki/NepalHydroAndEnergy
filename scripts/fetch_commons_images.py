#!/usr/bin/env python3
"""Fetch CC-licensed images from Wikimedia Commons and wire them into
a wiki page's ``images:`` frontmatter block.

Workflow modes:

1. **Fetch**  — search Commons, download matching CC images, write a
   per-slug ``_commons.json`` manifest in the image folder, and patch
   the page's frontmatter to reference the newly-added files.

   ``python3 scripts/fetch_commons_images.py --slug arun-3 \\
       --query "Arun III hydroelectric" --limit 6``

2. **Sync**   — don't fetch anything new; just reconcile the disk state
   with the frontmatter block (remove entries for deleted files,
   re-add entries the manifest still knows about).

   ``python3 scripts/fetch_commons_images.py --slug arun-3 --sync``

3. **Batch**  — run a predefined ``{slug: query}`` map. Useful for
   seeding several projects in one pass.

   ``python3 scripts/fetch_commons_images.py --batch``

Design notes:
-   Commons file metadata (``extmetadata``) is parsed for license,
    artist and description. Only permissive licenses are accepted by
    default; the full set is controlled via ``--licenses``.
-   Downloaded filenames are slug-sanitized so ``src:`` values stay
    shell-friendly. The original Commons filename is preserved in the
    manifest for traceability.
-   Frontmatter patching is regex-based but respectful: it preserves
    all non-``images:`` frontmatter keys verbatim, and only touches
    entries it can match by ``src``. Hand-written ``caption:`` /
    ``credit:`` values survive a ``--sync`` roundtrip.
-   The script is safe to re-run. New images append; deleted files
    prune; already-downloaded files are skipped.

No new Python dependencies — uses only stdlib + ``requests``, which is
already present in the project's environment.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import time
import unicodedata
from pathlib import Path
from urllib.parse import quote

import requests  # noqa: F401  (checked at import so failures are loud)


ROOT = Path(__file__).resolve().parent.parent
PAGES_DIR = ROOT / "wiki" / "pages" / "entities"
ASSETS_DIR = ROOT / "wiki" / "assets" / "images"
API = "https://commons.wikimedia.org/w/api.php"
UA = "NepalEnergy-WikiBot/0.1 (https://github.com/local; contact@local)"

DEFAULT_LICENSES = {
    # The canonical LicenseShortName values returned by Commons'
    # ``extmetadata`` for the licenses we're willing to embed.
    "CC0",
    "Public domain",
    "CC BY 2.0",
    "CC BY 2.5",
    "CC BY 3.0",
    "CC BY 4.0",
    "CC BY-SA 2.0",
    "CC BY-SA 2.5",
    "CC BY-SA 3.0",
    "CC BY-SA 4.0",
}

# Curated default batch — keeps initial sweep reproducible. Queries
# bias toward geographic features (rivers, districts, landscapes) rather
# than plant-specific strings, because Commons has rich coverage of the
# former and almost none of the latter for pre-commissioned projects.
# Revise freely; this is not a schema.
BATCH_QUERIES: dict[str, str] = {
    "arun-3":                   "Arun river Sankhuwasabha Nepal",
    "kali-gandaki-a":           "Kaligandaki A Hydroelectric Syangja",
    "tanahu-hydropower":        "Seti river Tanahun Nepal",
    "dudhkoshi-storage":        "Dudh Koshi river Solukhumbu Nepal",
    "upper-karnali":            "Karnali river Surkhet Nepal",
    "mugu-karnali-storage-hep": "Karnali river Mugu Nepal",
    "upper-tamakoshi":          "Upper Tamakoshi Dolakha Nepal",
    "budhigandaki":             "Budhi Gandaki river Nepal",
    "west-seti":                "Seti river Bajhang Nepal",
    "pancheshwar":              "Mahakali river Darchula Nepal",
    "koshi-basin":              "Koshi river Nepal",
    "gandaki-basin":            "Gandaki river Nepal",
    "karnali-basin":            "Karnali river Nepal",
    "mahakali-basin":           "Mahakali river Nepal",
    "kulekhani-cascade":        "Kulekhani Makwanpur Nepal",
}


# ---------------------------------------------------------------------
# Commons API
# ---------------------------------------------------------------------

def commons_search(query: str, limit: int, session: requests.Session) -> list[str]:
    """Return a list of ``File:...`` titles matching ``query``."""
    r = session.get(
        API,
        params={
            "action": "query",
            "format": "json",
            "list": "search",
            "srsearch": f"{query} filemime:image",
            "srnamespace": 6,
            "srlimit": max(limit * 3, 10),
        },
        headers={"User-Agent": UA},
        timeout=30,
    )
    r.raise_for_status()
    hits = r.json().get("query", {}).get("search", [])
    return [h["title"] for h in hits]


def commons_fileinfo(titles: list[str], session: requests.Session) -> dict[str, dict]:
    """Fetch imageinfo (url, metadata, extmetadata) for a batch of
    Commons file titles. Commons accepts up to 50 titles per call."""
    out: dict[str, dict] = {}
    for i in range(0, len(titles), 50):
        chunk = titles[i : i + 50]
        r = session.get(
            API,
            params={
                "action": "query",
                "format": "json",
                "prop": "imageinfo",
                "iiprop": "url|size|mime|extmetadata",
                "iiurlwidth": 1600,
                "titles": "|".join(chunk),
            },
            headers={"User-Agent": UA},
            timeout=30,
        )
        r.raise_for_status()
        pages = r.json().get("query", {}).get("pages", {})
        for p in pages.values():
            ii = (p.get("imageinfo") or [{}])[0]
            if ii:
                out[p["title"]] = ii
    return out


# ---------------------------------------------------------------------
# License + metadata parsing
# ---------------------------------------------------------------------

_HTML_TAG_RE = re.compile(r"<[^>]+>")


def _plain(text: str | None) -> str:
    if not text:
        return ""
    t = _HTML_TAG_RE.sub("", text)
    t = re.sub(r"\s+", " ", t).strip()
    return t


def parse_extmetadata(ii: dict) -> dict:
    """Pluck license, artist, description, and source_url out of a
    Commons ``imageinfo`` entry. All values are plain text (HTML stripped).
    Any missing keys come back as empty strings."""
    em = ii.get("extmetadata") or {}

    def _v(key: str) -> str:
        return _plain((em.get(key) or {}).get("value", ""))

    return {
        "license": _v("LicenseShortName"),
        "license_url": _v("LicenseUrl"),
        "artist": _v("Artist"),
        "credit_raw": _v("Credit"),
        "description": _v("ImageDescription"),
        "object_name": _v("ObjectName"),
        "usage_terms": _v("UsageTerms"),
    }


def license_ok(license_name: str, allowed: set[str]) -> bool:
    return license_name in allowed


# ---------------------------------------------------------------------
# Filesystem / naming
# ---------------------------------------------------------------------

_SLUG_RE = re.compile(r"[^a-z0-9]+")


def slugify_filename(commons_title: str) -> str:
    """Turn ``File:Kali Gandaki A Powerhouse.jpg`` into
    ``kali-gandaki-a-powerhouse.jpg``."""
    base = commons_title.removeprefix("File:").strip()
    name, _, ext = base.rpartition(".")
    name = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode("ascii")
    name = _SLUG_RE.sub("-", name.lower()).strip("-")
    ext = ext.lower() or "jpg"
    return f"{name or 'image'}.{ext}"


def download_image(url: str, dest: Path, session: requests.Session) -> int:
    dest.parent.mkdir(parents=True, exist_ok=True)
    with session.get(url, stream=True, headers={"User-Agent": UA}, timeout=60) as r:
        r.raise_for_status()
        total = 0
        with open(dest, "wb") as fh:
            for chunk in r.iter_content(chunk_size=64 * 1024):
                if chunk:
                    fh.write(chunk)
                    total += len(chunk)
        return total


# ---------------------------------------------------------------------
# Frontmatter patching
# ---------------------------------------------------------------------

IMAGES_BLOCK_RE = re.compile(
    # Matches either ``images: []``, ``images:`` followed by indented
    # list items, or a missing ``images:`` key (None => insert).
    # Trailing newline is optional so this also matches when the key
    # is the last line of the frontmatter body (our split_frontmatter
    # strips the trailing newline).
    r"^images:[ \t]*(\[[ \t]*\][ \t]*)?(?:\n"
    r"((?:[ \t]+-[^\n]*\n?(?:[ \t]{2,}[^\n]*\n?)*)*))?",
    re.MULTILINE,
)


def split_frontmatter(text: str) -> tuple[str, str]:
    if not text.startswith("---"):
        return "", text
    end = text.find("\n---", 4)
    if end == -1:
        return "", text
    return text[4:end].lstrip("\n"), text[end + 4 :].lstrip("\n")


def _yaml_escape(v: str) -> str:
    """Escape a plain string value for inline YAML. We use double
    quotes whenever the value contains characters that would force
    block scalar mode, keeping the frontmatter single-line-per-field."""
    if v == "":
        return '""'
    if re.search(r"[:\#\n\"']", v):
        return '"' + v.replace("\\", "\\\\").replace('"', '\\"') + '"'
    return v


def serialize_images(entries: list[dict]) -> str:
    """Render an ``images:`` block from a list of dicts. Omits keys
    with empty values so the file stays readable."""
    if not entries:
        return "images: []\n"
    lines = ["images:"]
    for e in entries:
        lines.append(f"  - src: {_yaml_escape(e['src'])}")
        for k in ("caption", "credit", "license", "license_url", "source_url"):
            v = e.get(k, "")
            if v:
                lines.append(f"    {k}: {_yaml_escape(v)}")
    return "\n".join(lines) + "\n"


IMAGE_ITEM_RE = re.compile(
    r"-\s+src:\s*(?P<src>[^\s\"]+|\"[^\"]+\")"
    r"(?P<rest>(?:\n[ \t]{2,}\w+:[^\n]*)*)",
)
KV_RE = re.compile(r"^[ \t]+(?P<k>\w+):\s*(?P<v>.*)$", re.MULTILINE)


def parse_images_block(block: str | None) -> list[dict]:
    """Parse an existing ``images:`` block body into a list of dicts.
    Preserves unknown keys so we don't clobber hand-edited values."""
    if not block:
        return []
    entries: list[dict] = []
    for m in IMAGE_ITEM_RE.finditer(block):
        src = m.group("src").strip().strip('"')
        entry = {"src": src}
        for kv in KV_RE.finditer(m.group("rest")):
            entry[kv.group("k")] = kv.group("v").strip().strip('"')
        entries.append(entry)
    return entries


def patch_frontmatter(page_path: Path, entries: list[dict]) -> bool:
    """Replace (or insert) the ``images:`` block in ``page_path`` with
    ``entries``. Returns True if the file changed."""
    text = page_path.read_text(encoding="utf-8")
    fm, body = split_frontmatter(text)
    if not fm:
        raise SystemExit(f"{page_path}: no frontmatter found")

    new_block = serialize_images(entries).rstrip("\n")
    # Search on ``fm + "\n"`` so a trailing ``images: []`` line (stripped
    # of its newline by split_frontmatter) still matches.
    fm_for_match = fm + ("\n" if not fm.endswith("\n") else "")
    m = IMAGES_BLOCK_RE.search(fm_for_match)
    if m:
        before = fm_for_match[: m.start()]
        after = fm_for_match[m.end() :]
        new_fm = before + new_block + ("\n" if not new_block.endswith("\n") else "") + after
    else:
        new_fm = fm.rstrip() + "\n" + new_block + "\n"

    new_text = "---\n" + new_fm.strip("\n") + "\n---\n\n" + body.lstrip("\n")
    if new_text == text:
        return False
    page_path.write_text(new_text, encoding="utf-8")
    return True


# ---------------------------------------------------------------------
# Per-slug manifest
# ---------------------------------------------------------------------

def load_manifest(slug_dir: Path) -> dict:
    f = slug_dir / "_commons.json"
    if f.exists():
        return json.loads(f.read_text(encoding="utf-8"))
    return {"slug": slug_dir.name, "entries": []}


def save_manifest(slug_dir: Path, manifest: dict) -> None:
    slug_dir.mkdir(parents=True, exist_ok=True)
    f = slug_dir / "_commons.json"
    f.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")


def caption_from_metadata(meta: dict) -> str:
    """Prefer a short, readable caption. Commons ``ImageDescription``
    is often essay-length; truncate at the first sentence."""
    text = meta.get("description") or meta.get("object_name") or ""
    text = text.strip()
    if not text:
        return ""
    # Split on the first period followed by a space or end-of-string.
    m = re.match(r"(.+?[.!?])(\s|$)", text)
    short = m.group(1) if m else text
    if len(short) > 180:
        short = short[:177].rstrip() + "\u2026"
    return short


def credit_from_metadata(meta: dict) -> str:
    artist = meta.get("artist") or ""
    return artist or meta.get("credit_raw") or "Unknown"


# ---------------------------------------------------------------------
# Core operations
# ---------------------------------------------------------------------

def fetch_for_slug(
    slug: str,
    query: str,
    limit: int,
    allowed_licenses: set[str],
    min_width: int,
    dry_run: bool,
    session: requests.Session,
) -> list[dict]:
    """Search Commons, download CC-licensed matches, return new manifest
    entries (not yet written to disk)."""
    slug_dir = ASSETS_DIR / slug
    manifest = load_manifest(slug_dir)
    known_titles = {e["commons_title"] for e in manifest["entries"]}

    titles = commons_search(query, limit, session)
    if not titles:
        print(f"  no search hits for '{query}'")
        return manifest["entries"]
    info = commons_fileinfo(titles, session)

    # Commons often returns multiple near-identical shots from the same
    # contributor (e.g. "... Rajesh Dhungana (1).jpg", "(2).jpg",
    # "(3).jpg"). Collapse such runs by the normalized stem so the
    # filmstrip shows variety, not the same subject four times.
    def _stem_key(title: str) -> str:
        t = title.removeprefix("File:")
        t = re.sub(r"\s*\(\d+\)\s*", " ", t)
        t = re.sub(r"\.\w+$", "", t).lower()
        return re.sub(r"\s+", " ", t).strip()[:48]

    seen_stems: set[str] = set()
    added = 0
    for title in titles:
        if added >= limit:
            break
        if title in known_titles:
            continue
        stem = _stem_key(title)
        if stem in seen_stems:
            print(f"  skip (near-duplicate of earlier hit): {title}")
            continue
        seen_stems.add(stem)
        ii = info.get(title)
        if not ii:
            continue
        meta = parse_extmetadata(ii)
        if not license_ok(meta["license"], allowed_licenses):
            print(f"  skip (license={meta['license'] or '?'}): {title}")
            continue
        if ii.get("width", 0) < min_width:
            print(f"  skip (width={ii.get('width', 0)} < {min_width}): {title}")
            continue

        url = ii.get("thumburl") or ii.get("url")
        filename = slugify_filename(title)
        dest = slug_dir / filename
        if dest.exists():
            print(f"  already on disk: {filename}")
        elif dry_run:
            print(f"  would download: {title} -> {filename}")
        else:
            try:
                size = download_image(url, dest, session)
                print(f"  downloaded ({size//1024} KB): {title} -> {filename}")
            except Exception as e:
                print(f"  FAILED: {title}: {e}")
                continue

        manifest["entries"].append(
            {
                "commons_title": title,
                "src": f"{slug}/{filename}",
                "filename": filename,
                "caption": caption_from_metadata(meta),
                "credit": credit_from_metadata(meta),
                "license": meta["license"],
                "license_url": meta["license_url"],
                "source_url": f"https://commons.wikimedia.org/wiki/{quote(title.replace(' ', '_'))}",
                "width": ii.get("width"),
                "height": ii.get("height"),
                "fetched_at": int(time.time()),
            }
        )
        added += 1
        known_titles.add(title)

    if not dry_run:
        save_manifest(slug_dir, manifest)
    return manifest["entries"]


def sync_frontmatter(slug: str) -> bool:
    """Reconcile disk state with frontmatter. Returns True if the page
    file changed."""
    slug_dir = ASSETS_DIR / slug
    manifest = load_manifest(slug_dir)
    page_path = PAGES_DIR / f"{slug}.md"
    if not page_path.exists():
        raise SystemExit(f"no page at {page_path}")

    # Keep only entries whose file still exists on disk. This is how the
    # user communicates "I don't want this one": delete the file, re-run
    # --sync, the frontmatter entry disappears too.
    live_entries = []
    for e in manifest["entries"]:
        if (slug_dir / e["filename"]).exists():
            live_entries.append(e)
        else:
            print(f"  prune (missing on disk): {e['filename']}")
    if len(live_entries) != len(manifest["entries"]):
        manifest["entries"] = live_entries
        save_manifest(slug_dir, manifest)

    # Build the frontmatter entries; preserve any hand-edited caption /
    # credit values already in the file.
    existing = {}
    text = page_path.read_text(encoding="utf-8")
    fm, _ = split_frontmatter(text)
    if fm:
        m = IMAGES_BLOCK_RE.search(fm)
        if m:
            for e in parse_images_block(m.group(2)):
                existing[e["src"]] = e

    out_entries = []
    for e in live_entries:
        prev = existing.get(e["src"], {})
        out_entries.append(
            {
                "src": e["src"],
                "caption": prev.get("caption") or e.get("caption", ""),
                "credit": prev.get("credit") or e.get("credit", ""),
                "license": prev.get("license") or e.get("license", ""),
                "source_url": prev.get("source_url") or e.get("source_url", ""),
            }
        )

    changed = patch_frontmatter(page_path, out_entries)
    if changed:
        print(f"  patched {page_path.relative_to(ROOT)} ({len(out_entries)} images)")
    else:
        print(f"  no changes to {page_path.relative_to(ROOT)}")
    return changed


# ---------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--slug", help="target page slug (e.g. arun-3)")
    ap.add_argument("--query", help="Commons search query")
    ap.add_argument("--limit", type=int, default=6, help="max images to keep")
    ap.add_argument("--min-width", type=int, default=800,
                    help="discard images narrower than this")
    ap.add_argument("--licenses", nargs="*", default=sorted(DEFAULT_LICENSES),
                    help="allowed Commons LicenseShortName values")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--sync", action="store_true",
                    help="skip download; just reconcile frontmatter with disk")
    ap.add_argument("--batch", action="store_true",
                    help="iterate the built-in BATCH_QUERIES map")
    args = ap.parse_args()

    allowed = set(args.licenses)
    session = requests.Session()

    if args.batch:
        if args.sync:
            print("batch + --sync: syncing all known slugs")
        for slug, query in BATCH_QUERIES.items():
            print(f"\n=== {slug} ===")
            if args.sync:
                sync_frontmatter(slug)
                continue
            fetch_for_slug(
                slug, query, args.limit, allowed,
                args.min_width, args.dry_run, session,
            )
            if not args.dry_run:
                sync_frontmatter(slug)
        return 0

    if not args.slug:
        ap.error("--slug is required (or use --batch)")

    if args.sync:
        sync_frontmatter(args.slug)
        return 0

    if not args.query:
        # Fall back to BATCH_QUERIES if we know this slug
        args.query = BATCH_QUERIES.get(args.slug)
        if not args.query:
            ap.error("--query is required when slug has no BATCH_QUERIES entry")

    print(f"=== {args.slug} ===")
    fetch_for_slug(
        args.slug, args.query, args.limit, allowed,
        args.min_width, args.dry_run, session,
    )
    if not args.dry_run:
        sync_frontmatter(args.slug)
    return 0


if __name__ == "__main__":
    sys.exit(main())
