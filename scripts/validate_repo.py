#!/usr/bin/env python3
"""Lightweight repository validation for portfolio-facing hygiene."""
from __future__ import annotations

import csv as csv_module
import difflib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WIKI_PAGES = ROOT / "wiki" / "pages"
INDEX = ROOT / "wiki" / "explorer" / "shared" / "wiki-page-index.json"
SEARCH_INDEX = ROOT / "wiki" / "explorer" / "shared" / "wiki-search-index.json"
FACT_INDEX = ROOT / "wiki" / "explorer" / "shared" / "wiki-fact-index.json"
VECTOR_INDEX = ROOT / "wiki" / "explorer" / "shared" / "wiki-vector-index.json"
BACKLINKS = ROOT / "wiki" / "explorer" / "shared" / "wiki-backlinks.json"
MANIFEST = ROOT / "wiki" / "explorer" / "shared" / "layer-manifest.json"
WIKI_INDEX_MD = ROOT / "wiki" / "index.md"
PUBLIC_TEXT_FILES = [
    ROOT / "README.md",
    ROOT / "wiki" / "index.md",
    ROOT / "wiki" / "schema.md",
    ROOT / "wiki" / "log.md",
]

WIKILINK_RE = re.compile(r"\[\[([^\]|]+)(?:\|[^\]]+)?\]\]")
FENCED_RE = re.compile(r"```.*?```", re.DOTALL)
INLINE_CODE_RE = re.compile(r"`[^`\n]+`")
PAGE_CATEGORIES = ["sources", "entities", "concepts", "syntheses", "claims", "data", "interventions"]
FORBIDDEN_TRACKED_PREFIXES = (
    ".playwright-cli/",
    "output/playwright/",
    "tmp/",
    "wiki/explorer/shots/",
    "wiki/explorer/lib/cesium/",
)
FORBIDDEN_TRACKED_SUFFIXES = (
    ".DS_Store",
    ".404-stub.bak",
)
FORBIDDEN_TRACKED_EXACT = {
    "wiki/explorer/3d-terrain.html",
    "wiki/explorer/3d-terrain.README.md",
    "wiki/explorer/3d-terrain.TESTLOG.md",
}
PUBLIC_FORBIDDEN_PATTERNS = {
    "personal wiki": re.compile(r"\bpersonal wiki\b", re.I),
    "video essay": re.compile(r"\bvideo essay\b", re.I),
    "DeepResearch": re.compile(r"\bDeepResearch\b"),
    "AI provider label": re.compile(r"\b(Hermes|Claude|Codex|Gemini)\b"),
    "auto-generated stub": re.compile(r"\bauto-generated stub\b", re.I),
    "draft instruction": re.compile(r"\badd narrative\b", re.I),
    "internal consistency": re.compile(r"\bfor internal consistency\b", re.I),
    "wiki-internal": re.compile(r"\bwiki-internal\b", re.I),
}


def fail(message: str) -> None:
    print(f"FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        fail(f"{path.relative_to(ROOT)} is not valid JSON: {exc}")


def strip_ignored_markdown(text: str) -> str:
    text = FENCED_RE.sub(" ", text)
    return INLINE_CODE_RE.sub(" ", text)


def wiki_page_slugs() -> set[str]:
    slugs: set[str] = set()
    for category in PAGE_CATEGORIES:
        for page in (WIKI_PAGES / category).glob("*.md"):
            slugs.add(page.stem)
    return slugs


def validate_wiki_links(slugs: set[str]) -> None:
    broken: list[str] = []
    for category in PAGE_CATEGORIES:
        for page in sorted((WIKI_PAGES / category).glob("*.md")):
            text = strip_ignored_markdown(page.read_text(encoding="utf-8"))
            for match in WIKILINK_RE.finditer(text):
                target = match.group(1).strip()
                if target not in slugs:
                    broken.append(f"{page.relative_to(ROOT)} -> [[{target}]]")
    if broken:
        fail("broken wikilinks:\n" + "\n".join(broken[:50]))


def validate_caches(slugs: set[str]) -> None:
    index = load_json(INDEX)
    if index.get("totalPages") != len(slugs):
        fail(f"wiki-page-index totalPages={index.get('totalPages')} but found {len(slugs)} pages")

    search = load_json(SEARCH_INDEX)
    search_slugs = {p.get("s") for p in search.get("pages", [])}
    if search_slugs != slugs:
        missing = sorted(slugs - search_slugs)
        extra = sorted(search_slugs - slugs)
        msg = []
        if missing:
            msg.append("missing: " + ", ".join(missing[:20]))
        if extra:
            msg.append("extra: " + ", ".join(extra[:20]))
        fail("wiki-search-index slugs do not match wiki pages (" + "; ".join(msg) + ")")
    if search.get("version") != 1 or not search.get("postings") or not search.get("neighbors"):
        fail("wiki-search-index is missing required static search fields")

    facts = load_json(FACT_INDEX)
    if facts.get("version") != 1 or not facts.get("facts"):
        fail("wiki-fact-index is missing required fact fields")
    for fact in facts.get("facts", []):
        slug = fact.get("slug")
        if slug and slug not in slugs:
            fail(f"wiki-fact-index points to missing slug: {slug}")

    vector = load_json(VECTOR_INDEX)
    if vector.get("version") != 1 or not vector.get("chunks"):
        fail("wiki-vector-index is missing required vector fields")
    if vector.get("model", {}).get("dtype") != "int8_unit":
        fail("wiki-vector-index must ship quantized int8 unit vectors")
    vector_pages = {search["pages"][chunk.get("p", -1)]["s"] for chunk in vector.get("chunks", []) if 0 <= chunk.get("p", -1) < len(search["pages"])}
    if not slugs.issubset(vector_pages):
        missing = sorted(slugs - vector_pages)
        fail("wiki-vector-index has no chunks for pages: " + ", ".join(missing[:20]))

    backlinks = load_json(BACKLINKS).get("backlinks", {})
    broken_refs = [
        f"{target} <- {ref.get('slug')}"
        for target, refs in backlinks.items()
        for ref in refs
        if not ref.get("target_exists", False)
    ]
    if broken_refs:
        fail("cached backlinks contain broken refs:\n" + "\n".join(broken_refs[:50]))


def validate_public_index(slugs: set[str]) -> None:
    text = WIKI_INDEX_MD.read_text(encoding="utf-8")
    match = re.search(r"currently indexes\s+(\d+)\s+wiki pages", text)
    if not match:
        fail("wiki/index.md must state the current indexed wiki page count")
    count = int(match.group(1))
    if count != len(slugs):
        fail(f"wiki/index.md says {count} pages but found {len(slugs)} pages")


def validate_public_language() -> None:
    files = list(PUBLIC_TEXT_FILES)
    for category in PAGE_CATEGORIES:
        files.extend(sorted((WIKI_PAGES / category).glob("*.md")))
    offenders: list[str] = []
    for path in files:
        text = path.read_text(encoding="utf-8")
        for label, pattern in PUBLIC_FORBIDDEN_PATTERNS.items():
            for match in pattern.finditer(text):
                line_no = text.count("\n", 0, match.start()) + 1
                offenders.append(f"{path.relative_to(ROOT)}:{line_no}: {label}")
                break
    if offenders:
        fail("public-facing internal/draft language:\n" + "\n".join(offenders[:80]))


def validate_map_manifest() -> None:
    manifest = load_json(MANIFEST)
    layers = manifest.get("layers", {})
    for layer_id, layer in layers.items():
        rel = layer.get("path")
        if not rel or not rel.startswith("../../../"):
            continue
        target = ROOT / rel.replace("../../../", "")
        if not target.exists():
            fail(f"manifest layer {layer_id} points to missing file {target.relative_to(ROOT)}")
        if target.suffix in {".json", ".geojson"}:
            load_json(target)


def validate_tracked_hygiene() -> None:
    tracked = subprocess.check_output(["git", "ls-files"], cwd=ROOT, text=True).splitlines()
    offenders = [
        path
        for path in tracked
        if path in FORBIDDEN_TRACKED_EXACT
        or path.startswith(FORBIDDEN_TRACKED_PREFIXES)
        or path.endswith(FORBIDDEN_TRACKED_SUFFIXES)
    ]
    if offenders:
        fail("tracked generated/clutter files:\n" + "\n".join(offenders[:50]))


SPECS_CSV_PATH = ROOT / "data" / "project_specs.csv"
SCHEMA_PATH = ROOT / "wiki" / "specs-schema.json"

STATUS_ENUM = [
    "operating", "under-construction", "survey", "pre-construction",
    "stalled", "cancelled", "conceptual",
]

STATUS_TABLE_RE = re.compile(r"\|\s*Status\s*\|\s*(.+?)\s*\|")
STATUS_TO_ENUM: dict[str, str] = {
    "operating": "operating", "operational": "operating", "commissioned": "operating",
    "generating": "operating",
    "under construction": "under-construction",
    "under-construction": "under-construction",
    "construction": "under-construction",
    "survey": "survey", "survey licence": "survey", "feasibility": "survey",
    "pre-construction": "pre-construction", "pre construction": "pre-construction",
    "stalled": "stalled",
    "cancelled": "cancelled", "canceled": "cancelled", "abandoned": "cancelled",
    "conceptual": "conceptual",
}

ENTITY_FRONTMATTER_END_RE = re.compile(r"\n---\s*\n", re.MULTILINE)


def normalized_token(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", value.lower())


def entity_pages() -> list[Path]:
    return sorted((WIKI_PAGES / "entities").glob("*.md"))


def read_frontmatter_text(text: str) -> str:
    if not text.startswith("---\n"):
        return ""
    match = ENTITY_FRONTMATTER_END_RE.search(text, 4)
    if not match:
        return ""
    return text[4:match.start()]


def extract_frontmatter_list(text: str, key: str) -> list[str]:
    fm = read_frontmatter_text(text)
    if not fm:
        return []
    match = re.search(rf"^{re.escape(key)}:\s*\[(.*?)\]\s*$", fm, re.MULTILINE)
    if not match:
        return []
    raw = match.group(1).strip()
    if not raw:
        return []
    return [s.strip().strip("'\"") for s in raw.split(",") if s.strip()]


def extract_generator(text: str) -> str:
    fm = read_frontmatter_text(text)
    if not fm:
        return ""
    match = re.search(r"^generator:\s*(.+?)\s*$", fm, re.MULTILINE)
    return match.group(1).strip() if match else ""


def extract_title(text: str, fallback: str) -> str:
    match = re.search(r"^title:\s*(.+?)\s*$", text, re.MULTILINE)
    return match.group(1).strip().strip("'\"") if match else fallback


def warn(message: str) -> None:
    print(f"WARNING: {message}", file=sys.stderr)


def read_specs_csv() -> list[dict[str, str]] | None:
    if not SPECS_CSV_PATH.exists():
        return None
    with SPECS_CSV_PATH.open(newline="", encoding="utf-8-sig") as f:
        return list(csv_module.DictReader(f))


def validate_duplicate_entities(slugs: set[str]) -> None:
    corpus_collisions: list[str] = []
    title_index: dict[str, list[str]] = {}
    for page in entity_pages():
        text = page.read_text(encoding="utf-8")
        title = extract_title(text, page.stem)
        key = normalized_token(title)
        if not key:
            continue
        title_index.setdefault(key, []).append(f"{page.stem} ({title})")
    for key, items in sorted(title_index.items()):
        if len(items) > 1:
            corpus_collisions.append(" / ".join(items))
    if corpus_collisions:
        fail("duplicate/colliding entity titles in wiki/pages/entities:\n  "
             + "\n  ".join(corpus_collisions[:25]))

    rows = read_specs_csv()
    if not rows:
        return
    # Check duplicate slugs
    slug_counter: dict[str, int] = {}
    for row in rows:
        s = (row.get("slug") or "").strip()
        if s:
            slug_counter[s] = slug_counter.get(s, 0) + 1
    dupes = {k: v for k, v in slug_counter.items() if v > 1}
    if dupes:
        fail("duplicate slugs in project_specs.csv: " + ", ".join(
            f"{k} ({v}x)" for k, v in sorted(dupes.items())))
    # Fuzzy-duplicate names
    names = [(row.get("slug") or "").strip() for row in rows]
    names = [n for n in names if n]
    seen: list[str] = []
    fuzzy_dupes: list[str] = []
    for name in names:
        close = difflib.get_close_matches(name, [s for s in seen if s != name], n=1, cutoff=0.75)
        if close:
            fuzzy_dupes.append(f"{name} ~ {close[0]}")
        seen.append(name)
    if fuzzy_dupes:
        warn("fuzzy-duplicate entity names in CSV: " + ", ".join(fuzzy_dupes[:20]))


def validate_page_generator(slugs: set[str]) -> None:
    missing: list[str] = []
    for page in entity_pages():
        text = page.read_text(encoding="utf-8")
        if not extract_generator(text):
            missing.append(page.stem)
    if missing:
        fail(f"{len(missing)} entity pages missing 'generator:' frontmatter field: "
             + ", ".join(missing[:30]))


def validate_source_blocks() -> None:
    source_pages = {
        p.stem for p in (WIKI_PAGES / "sources").glob("*.md")
    }

    missing_section: list[str] = []
    empty_frontmatter: list[str] = []
    no_primary_source: list[str] = []
    placeholder_blocks: list[str] = []

    for path in entity_pages():
        text = path.read_text(encoding="utf-8")
        slug = path.stem
        generator = extract_generator(text)
        if generator not in {"specs-refresh", "manual"}:
            continue
        tags = set(extract_frontmatter_list(text, "tags"))
        if "project" not in tags:
            continue
        # Check for ## Sources markdown section
        if not re.search(r"^## Sources\s*$", text, re.MULTILINE):
            missing_section.append(slug)
        # Check sources: frontmatter is non-empty
        source_slugs = extract_frontmatter_list(text, "sources")
        if not source_slugs:
            empty_frontmatter.append(slug)
        elif not any(s in source_pages for s in source_slugs):
            no_primary_source.append(slug)
        if "_No primary sources have been linked yet._" in text:
            placeholder_blocks.append(slug)

    if missing_section:
        fail(f"{len(missing_section)} flagship entities missing '## Sources' section: "
             + ", ".join(missing_section[:25]))
    if empty_frontmatter:
        fail(f"{len(empty_frontmatter)} flagship entities have empty 'sources:' frontmatter: "
             + ", ".join(empty_frontmatter[:25]))
    if no_primary_source:
        fail(f"{len(no_primary_source)} flagship entities have no primary source from "
             f"wiki/pages/sources/: " + ", ".join(no_primary_source[:25]))
    if placeholder_blocks:
        fail(f"{len(placeholder_blocks)} flagship entities still show placeholder source blocks: "
             + ", ".join(placeholder_blocks[:25]))


def validate_status_consistency() -> None:
    rows = read_specs_csv()
    if not rows:
        return
    # Validate CSV status values match schema enum
    invalid_status: list[str] = []
    for row in rows:
        slug = (row.get("slug") or "").strip()
        status = (row.get("status") or "").strip()
        if status and status not in STATUS_ENUM:
            invalid_status.append(f"{slug}: '{status}'")
    if invalid_status:
        fail("invalid status values in project_specs.csv (must match schema enum):\n  "
             + "\n  ".join(invalid_status[:25]))

    # Check entity page spec tables for stale/inconsistent status declarations
    mismatches: list[str] = []
    for row in rows:
        slug = (row.get("slug") or "").strip()
        csv_status = (row.get("status") or "").strip().lower()
        if not slug or not csv_status:
            continue
        path = WIKI_PAGES / "entities" / f"{slug}.md"
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        # Look for explicit Status table row: | Status | <value> |
        for m in STATUS_TABLE_RE.finditer(text):
            page_status_raw = m.group(1).strip().lower()
            # Remove parenthetical notes like "(Generation licence)"
            page_status_raw = re.sub(r"\(.*?\)", "", page_status_raw).strip()
            page_status_enum = STATUS_TO_ENUM.get(page_status_raw)
            if page_status_enum and page_status_enum != csv_status:
                mismatches.append(
                    f"{slug}: CSV says '{csv_status}' but spec table says "
                    f"'{page_status_raw}' → maps to '{page_status_enum}'"
                )
                break  # One mismatch per page is enough
    if mismatches:
        fail(f"{len(mismatches)} entities with status mismatch between CSV and spec "
             f"table:\n  " + "\n  ".join(mismatches[:30]))


def validate_specs_csv(slugs: set[str]) -> None:
    rows = read_specs_csv()
    if not rows:
        return
    if not rows:
        fail("data/project_specs.csv is empty")
    fieldnames = set(rows[0].keys())
    if "slug" not in fieldnames:
        fail("data/project_specs.csv missing required 'slug' column")
    # Check required schema columns
    required_cols = {"slug", "gross_head_m", "annual_design_energy_gwh", "project_type"}
    missing = required_cols - fieldnames
    if missing:
        fail(f"data/project_specs.csv missing columns: {', '.join(sorted(missing))}")
    # Collect referenced slugs and check against wiki pages
    spec_slugs = {row.get("slug", "").strip() for row in rows if row.get("slug", "").strip()}
    orphaned = spec_slugs - slugs
    if orphaned:
        print(f"WARNING: {len(orphaned)} specs CSV slugs with no wiki page: {', '.join(sorted(orphaned)[:20])}")
    print(f"specs CSV: {len(spec_slugs)} project slugs, {len(fieldnames)} columns")


def main() -> None:
    slugs = wiki_page_slugs()
    validate_wiki_links(slugs)
    validate_caches(slugs)
    validate_public_index(slugs)
    validate_public_language()
    validate_map_manifest()
    validate_tracked_hygiene()
    validate_specs_csv(slugs)
    validate_duplicate_entities(slugs)
    validate_page_generator(slugs)
    validate_source_blocks()
    validate_status_consistency()
    print(f"OK: {len(slugs)} wiki pages, caches valid, map manifest valid, tracked hygiene clean")


if __name__ == "__main__":
    main()
