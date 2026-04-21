#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
import re
import time
from collections import Counter
from datetime import date
from pathlib import Path
from typing import Any

from pdf_atlas_lib import (
    ASSETS_DIR,
    ROOT,
    SOURCES,
    WIKI_INDEX_PATH,
    WIKI_PAGES,
    asset_filename_for,
    clamp_bbox_to_page,
    decision_signature,
    decision_slug,
    get_source,
    low_signal_stub_slugs_for_source,
    parse_decisions_text,
    source_abs_path,
    source_page_url_for_assets,
    title_from_slug,
)


TODAY = date.today().isoformat()


def split_frontmatter(text: str) -> tuple[list[str], str]:
    if not text.startswith("---\n"):
        raise ValueError("missing frontmatter")
    end = text.find("\n---\n", 4)
    if end == -1:
        raise ValueError("unterminated frontmatter")
    frontmatter = text[4:end].splitlines()
    body = text[end + 5 :]
    return frontmatter, body


def join_frontmatter(frontmatter: list[str], body: str) -> str:
    return "---\n" + "\n".join(frontmatter) + "\n---\n\n" + body.lstrip("\n")


def parse_bracket_list(line: str) -> list[str]:
    match = re.match(r"^([a-z_]+):\s*\[(.*)\]\s*$", line.strip())
    if not match:
        return []
    inner = match.group(2).strip()
    if not inner:
        return []
    return [part.strip().strip('"').strip("'") for part in inner.split(",") if part.strip()]


def format_bracket_list(key: str, values: list[str]) -> str:
    return f"{key}: [{', '.join(values)}]"


def ensure_source_slug(text: str, source_slug: str) -> str:
    frontmatter, body = split_frontmatter(text)
    for idx, line in enumerate(frontmatter):
        if line.startswith("sources:"):
            items = parse_bracket_list(line)
            if source_slug not in items:
                items.append(source_slug)
                frontmatter[idx] = format_bracket_list("sources", items)
            return join_frontmatter(frontmatter, body)

    insert_at = next((i for i, line in enumerate(frontmatter) if line.startswith("tags:")), len(frontmatter))
    frontmatter.insert(insert_at, format_bracket_list("sources", [source_slug]))
    return join_frontmatter(frontmatter, body)


def remove_source_slug_if_unused(text: str, source_slug: str, asset_prefix: str) -> str:
    if source_slug not in text:
        return text
    if f"{asset_prefix}-" in text:
        return text

    frontmatter, body = split_frontmatter(text)
    for idx, line in enumerate(frontmatter):
        if not line.startswith("sources:"):
            continue
        items = [item for item in parse_bracket_list(line) if item != source_slug]
        if items:
            frontmatter[idx] = format_bracket_list("sources", items)
        else:
            del frontmatter[idx]
        break
    return join_frontmatter(frontmatter, body)


def yaml_quote(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def append_frontmatter_image(text: str, entry: dict[str, str]) -> str:
    frontmatter, body = split_frontmatter(text)
    src_line = f"src: {entry['src']}"
    if src_line in "\n".join(frontmatter):
        return text

    block = [
        f"  - src: {entry['src']}",
        f"    caption: {yaml_quote(entry['caption'])}",
        f"    credit: {yaml_quote(entry['credit'])}",
        f"    license: {entry['license']}",
        f"    source_url: {yaml_quote(entry['source_url'])}",
    ]

    image_idx = next((i for i, line in enumerate(frontmatter) if line.startswith("images:")), None)
    if image_idx is not None:
        if frontmatter[image_idx].strip() == "images: []":
            frontmatter[image_idx] = "images:"
        end_idx = image_idx + 1
        while end_idx < len(frontmatter) and (frontmatter[end_idx].startswith("  ") or frontmatter[end_idx].strip() == ""):
            end_idx += 1
        frontmatter[end_idx:end_idx] = block
        return join_frontmatter(frontmatter, body)

    insert_at = next((i for i, line in enumerate(frontmatter) if line.startswith("generator:")), len(frontmatter))
    frontmatter[insert_at:insert_at] = ["images:"] + block
    return join_frontmatter(frontmatter, body)


def remove_frontmatter_image(text: str, src: str) -> str:
    frontmatter, body = split_frontmatter(text)
    needle = f"  - src: {src}"
    start = next((i for i, line in enumerate(frontmatter) if line == needle), None)
    if start is None:
        return text

    end = start + 1
    while end < len(frontmatter) and (frontmatter[end].startswith("    ") or frontmatter[end].strip() == ""):
        end += 1
    del frontmatter[start:end]

    image_idx = next((i for i, line in enumerate(frontmatter) if line.startswith("images:")), None)
    if image_idx is not None:
        block_end = image_idx + 1
        has_entries = False
        while block_end < len(frontmatter) and (frontmatter[block_end].startswith("  ") or frontmatter[block_end].strip() == ""):
            if frontmatter[block_end].startswith("  - src: "):
                has_entries = True
            block_end += 1
        if not has_entries:
            del frontmatter[image_idx:block_end]

    return join_frontmatter(frontmatter, body)


def build_inline_figure_block(src: str, caption: str) -> str:
    alt = caption or Path(src).stem.replace("-", " ")
    return (
        '<figure class="wiki-inline-figure">\n'
        f'  <img src="../assets/images/{src}" alt="{alt}">\n'
        f"  <figcaption>{caption}</figcaption>\n"
        "</figure>\n"
    )


def insert_inline_figure(text: str, figure_block: str, src: str, paragraph_anchor: str) -> str:
    if src in text:
        return text

    if paragraph_anchor and paragraph_anchor in text:
        anchor_idx = text.index(paragraph_anchor)
        para_end = text.find("\n\n", anchor_idx)
        if para_end != -1:
            insert_at = para_end + 2
            return text[:insert_at] + figure_block + "\n" + text[insert_at:]

    see_also_idx = text.find("\n## See also")
    if see_also_idx != -1:
        return text[:see_also_idx].rstrip() + "\n\n" + figure_block + "\n" + text[see_also_idx:]

    return text.rstrip() + "\n\n" + figure_block + "\n"


def remove_inline_figure(text: str, src: str) -> str:
    needle = f'../assets/images/{src}"'
    src_idx = text.find(needle)
    if src_idx == -1:
        return text

    start = text.rfind('<figure class="wiki-inline-figure">', 0, src_idx)
    end = text.find("</figure>", src_idx)
    if start == -1 or end == -1:
        return text
    end += len("</figure>")
    if end < len(text) and text[end] == "\n":
        end += 1
    updated = text[:start].rstrip() + "\n\n" + text[end:].lstrip("\n")
    return re.sub(r"\n{3,}", "\n\n", updated)


def merge_provenance(existing: dict[str, Any] | None, incoming: dict[str, Any], slug: str) -> dict[str, Any]:
    base = existing or {"slug": slug, "entries": []}
    entries = list(base.get("entries", []))
    if any(item.get("src") == incoming.get("src") for item in entries):
        return {"slug": slug, "entries": entries}
    entries.append(incoming)
    entries.sort(key=lambda item: item.get("src", ""))
    return {"slug": slug, "entries": entries}


def remove_provenance_entry(existing: dict[str, Any] | None, src: str, slug: str) -> dict[str, Any] | None:
    base = existing or {"slug": slug, "entries": []}
    entries = [item for item in base.get("entries", []) if item.get("src") != src]
    if not entries:
        return None
    entries.sort(key=lambda item: item.get("src", ""))
    return {"slug": slug, "entries": entries}


def build_new_node_page(
    slug: str,
    title: str,
    caption: str,
    source_slug: str,
    related_links: list[str],
    asset_prefix: str,
) -> str:
    related = [link for link in related_links if link]
    if source_slug not in related:
        related.append(source_slug)
    seen: list[str] = []
    for item in related:
        if item not in seen:
            seen.append(item)
    related = seen[:3]
    link_lines = "\n".join(f"- [[{link}]]" for link in related)
    summary = caption or f"Imported PDF image node for {title}."
    return (
        "---\n"
        f"title: {title}\n"
        "type: entity\n"
        f"created: {TODAY}\n"
        f"updated: {TODAY}\n"
        f"sources: [{source_slug}]\n"
        f"tags: [{asset_prefix}, auto-import]\n"
        "---\n\n"
        f"# {title}\n\n"
        f"{summary} This placeholder page was created from the PDF image decisions manifest and still needs hand narration.\n\n"
        f"The current page exists so the extracted figure has a stable wiki home and can be linked back to {', '.join(f'[[{link}]]' for link in related[:2])}.\n\n"
        "## See also\n\n"
        f"{link_lines}\n"
    )


def load_module_from_path(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if not spec or not spec.loader:
        raise RuntimeError(f"could not import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_atlas_map(source: dict[str, str]) -> dict[tuple[int, int], dict[str, Any]]:
    rows = json.loads(source_abs_path(source, "atlas_json").read_text(encoding="utf-8"))
    return {(int(row["page"]), int(row["image_index"])): row for row in rows}


def load_wiki_index() -> dict[str, Any]:
    return json.loads(WIKI_INDEX_PATH.read_text(encoding="utf-8"))


def page_path_for_slug(slug: str, wiki_index: dict[str, Any], *, allow_new_entity: bool = False) -> Path:
    category = wiki_index["slugToCategory"].get(slug)
    if category:
        return WIKI_PAGES / category / f"{slug}.md"
    for category_dir in WIKI_PAGES.iterdir():
        candidate = category_dir / f"{slug}.md"
        if candidate.exists():
            return candidate
    if allow_new_entity:
        return WIKI_PAGES / "entities" / f"{slug}.md"
    raise KeyError(f"unknown slug: {slug}")


def extract_crop_image(pdf_path: Path, page_num: int, bbox: list[float], dest: Path, dry_run: bool) -> bool:
    if dest.exists():
        return False
    if dry_run:
        return True
    import pdfplumber

    dest.parent.mkdir(parents=True, exist_ok=True)
    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[page_num - 1]
        safe_bbox = clamp_bbox_to_page(bbox, page.width, page.height)
        if safe_bbox is None:
            raise ValueError("crop bbox collapsed after clamping to page bounds")
        cropped = page.crop(tuple(safe_bbox))
        cropped.to_image(resolution=200).save(dest)
    return True


def render_page_image(pdf_path: Path, page_num: int, dest: Path, dry_run: bool) -> bool:
    if dest.exists():
        return False
    if dry_run:
        return True
    module = load_module_from_path(ROOT / "scripts" / "build_project_image_assets.py", "build_project_image_assets")
    dest.parent.mkdir(parents=True, exist_ok=True)
    module.render_pdf_page(pdf_path, page_num, dest)
    module._trim_whitespace(dest)
    return True


def image_dimensions(path: Path) -> tuple[int, int]:
    from PIL import Image

    with Image.open(path) as img:
        return img.width, img.height


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, text: str, dry_run: bool) -> bool:
    if path.exists() and read_text(path) == text:
        return False
    if dry_run:
        return True
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return True


def write_json(path: Path, data: dict[str, Any], dry_run: bool) -> bool:
    text = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
    if path.exists() and path.read_text(encoding="utf-8") == text:
        return False
    if dry_run:
        return True
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return True


def delete_path(path: Path, dry_run: bool) -> bool:
    if not path.exists():
        return False
    if dry_run:
        return True
    if path.is_dir():
        for child in sorted(path.iterdir(), reverse=True):
            delete_path(child, dry_run=False)
        path.rmdir()
        return True
    path.unlink()
    return True


def candidate_links_from_record(record: dict[str, Any], source_slug: str) -> list[str]:
    links = [item["slug"] for item in record.get("candidate_slugs", []) if item.get("slug")]
    if source_slug not in links:
        links.append(source_slug)
    deduped: list[str] = []
    for link in links:
        if link not in deduped:
            deduped.append(link)
    return deduped[:3]


def record_matches_filters(entry: dict[str, Any], only_slug: str | None, only_page: int | None) -> bool:
    if only_page is not None and int(entry["page"]) != only_page:
        return False
    if only_slug is None:
        return True
    target = str(entry.get("target_slug") or "")
    proposed = str(entry.get("proposed_slug") or "")
    return target == only_slug or proposed == only_slug


def ensure_page_exists_for_new_node(
    slug: str,
    record: dict[str, Any],
    source: dict[str, str],
    dry_run: bool,
    stats: Counter,
) -> tuple[Path, str | None]:
    wiki_index = load_wiki_index()
    path = page_path_for_slug(slug, wiki_index, allow_new_entity=True)
    if path.exists():
        return path, None
    title = title_from_slug(slug)
    caption = str(record.get("nearest_caption", ""))
    text = build_new_node_page(
        slug=slug,
        title=title,
        caption=caption,
        source_slug=source["wiki_source_slug"],
        related_links=candidate_links_from_record(record, source["wiki_source_slug"]),
        asset_prefix=source["asset_prefix"],
    )
    changed = write_text(path, text, dry_run)
    if changed:
        stats["new_entity_pages"] += 1
    return path, text if dry_run else None


def add_filmstrip_entry(
    page_path: Path,
    image_entry: dict[str, str],
    source: dict[str, str],
    dry_run: bool,
    stats: Counter,
    initial_text: str | None = None,
) -> None:
    text = initial_text if initial_text is not None else read_text(page_path)
    updated = append_frontmatter_image(text, image_entry)
    updated = ensure_source_slug(updated, source["wiki_source_slug"])
    if updated != text:
        if f"src: {image_entry['src']}" in updated and f"src: {image_entry['src']}" not in text:
            stats["filmstrip_images_added"] += 1
        if source["wiki_source_slug"] in updated and source["wiki_source_slug"] not in text:
            stats["sources_updated"] += 1
        write_text(page_path, updated, dry_run)


def add_inline_figure(
    page_path: Path,
    src: str,
    caption: str,
    paragraph_anchor: str,
    source: dict[str, str],
    dry_run: bool,
    stats: Counter,
    initial_text: str | None = None,
) -> None:
    text = initial_text if initial_text is not None else read_text(page_path)
    updated = ensure_source_slug(text, source["wiki_source_slug"])
    figure = build_inline_figure_block(src, caption)
    updated = insert_inline_figure(updated, figure, src, paragraph_anchor)
    if updated != text:
        if src in updated and src not in text:
            stats["inline_figures_inserted"] += 1
        if source["wiki_source_slug"] in updated and source["wiki_source_slug"] not in text:
            stats["sources_updated"] += 1
        write_text(page_path, updated, dry_run)


def merge_provenance_file(
    slug: str,
    src: str,
    filename: str,
    caption: str,
    page_num: int,
    image_index: int,
    action: str,
    bbox: list[float],
    source: dict[str, str],
    dry_run: bool,
    stats: Counter,
) -> None:
    path = ASSETS_DIR / slug / source["provenance_filename"]
    existing = json.loads(path.read_text(encoding="utf-8")) if path.exists() else None
    width = height = 0
    asset_path = ASSETS_DIR / src
    if asset_path.exists():
        width, height = image_dimensions(asset_path)
    incoming = {
        "src": src,
        "filename": filename,
        "caption": caption,
        "credit": source["credit"],
        "license": source["license"],
        "source_url": source_page_url_for_assets(source),
        "source_page": page_num,
        "image_index": image_index,
        "action": action,
        "bbox": bbox,
        "width": width,
        "height": height,
        "fetched_at": int(time.time()),
    }
    merged = merge_provenance(existing, incoming, slug)
    if write_json(path, merged, dry_run):
        stats["provenance_files_updated"] += 1


def remove_provenance_file_entry(slug: str, src: str, source: dict[str, str], dry_run: bool, stats: Counter) -> None:
    path = ASSETS_DIR / slug / source["provenance_filename"]
    if not path.exists():
        return
    existing = json.loads(path.read_text(encoding="utf-8"))
    updated = remove_provenance_entry(existing, src, slug)
    if updated is None:
        if delete_path(path, dry_run):
            stats["provenance_files_deleted"] += 1
        return
    if write_json(path, updated, dry_run):
        stats["provenance_entries_removed"] += 1


def remove_asset_file(src: str, dry_run: bool, stats: Counter) -> None:
    path = ASSETS_DIR / src
    if delete_path(path, dry_run):
        stats["asset_files_deleted"] += 1
        parent = path.parent
        if parent.exists() and not any(parent.iterdir()):
            delete_path(parent, dry_run)


def remove_decision_application(entry: dict[str, Any], source: dict[str, str], dry_run: bool, stats: Counter) -> None:
    slug = decision_slug(entry)
    if not slug:
        return

    wiki_index = load_wiki_index()
    allow_new_entity = entry["action"] == "new_node"
    try:
        page_path = page_path_for_slug(slug, wiki_index, allow_new_entity=allow_new_entity)
    except KeyError:
        page_path = WIKI_PAGES / "entities" / f"{slug}.md"

    asset_rel = f"{slug}/{asset_filename_for(source, entry)}"
    if page_path.exists():
        text = read_text(page_path)
        updated = remove_frontmatter_image(text, asset_rel)
        updated = remove_inline_figure(updated, asset_rel)
        updated = remove_source_slug_if_unused(updated, source["wiki_source_slug"], source["asset_prefix"])
        if updated != text:
            if asset_rel in text:
                if f"src: {asset_rel}" in text:
                    stats["filmstrip_images_removed"] += 1
                if f'../assets/images/{asset_rel}"' in text:
                    stats["inline_figures_removed"] += 1
            if source["wiki_source_slug"] in text and source["wiki_source_slug"] not in updated:
                stats["sources_removed"] += 1
            write_text(page_path, updated, dry_run)

    remove_provenance_file_entry(slug, asset_rel, source, dry_run, stats)
    remove_asset_file(asset_rel, dry_run, stats)


def cleanup_low_signal_stubs(source_id: str, target_entries: list[dict[str, Any]], dry_run: bool, stats: Counter) -> None:
    keep = {decision_slug(entry) for entry in target_entries}
    for slug in sorted(low_signal_stub_slugs_for_source(source_id)):
        if slug in keep:
            continue
        page_path = WIKI_PAGES / "entities" / f"{slug}.md"
        if delete_path(page_path, dry_run):
            stats["stub_pages_deleted"] += 1
        asset_dir = ASSETS_DIR / slug
        if delete_path(asset_dir, dry_run):
            stats["stub_asset_dirs_deleted"] += 1


def execute_decisions(source: dict[str, str], entries: list[dict[str, Any]], *, dry_run: bool) -> Counter:
    wiki_index = load_wiki_index()
    atlas_map = load_atlas_map(source)
    stats: Counter = Counter()
    pdf_path = source_abs_path(source, "pdf_path")

    for entry in entries:
        key = (int(entry["page"]), int(entry["image_index"]))
        record = atlas_map.get(key)
        if not record:
            stats["skipped_missing_atlas"] += 1
            continue

        action = entry["action"]
        if action == "drop":
            continue
        slug = decision_slug(entry)
        if not slug:
            stats["skipped_missing_slug"] += 1
            continue

        if action == "new_node":
            page_path, initial_text = ensure_page_exists_for_new_node(slug, record, source, dry_run, stats)
            action = "inline_figure"
            entry = dict(entry)
            entry["target_slug"] = slug
            entry["paragraph_anchor"] = str(entry.get("paragraph_anchor") or "")
        else:
            page_path = page_path_for_slug(slug, wiki_index, allow_new_entity=False)
            initial_text = None

        filename = asset_filename_for(source, entry)
        asset_rel = f"{slug}/{filename}"
        asset_path = ASSETS_DIR / asset_rel
        caption = str(entry.get("caption") or record.get("nearest_caption") or f"PDF image from page {entry['page']}.")

        if action == "page_render":
            asset_changed = render_page_image(pdf_path, int(entry["page"]), asset_path, dry_run)
        else:
            try:
                asset_changed = extract_crop_image(pdf_path, int(entry["page"]), record["bbox"], asset_path, dry_run)
            except ValueError:
                stats["skipped_invalid_crop"] += 1
                continue

        if action == "crop":
            if asset_changed:
                stats["crop_assets_written"] += 1
            merge_provenance_file(
                slug,
                asset_rel,
                filename,
                caption,
                int(entry["page"]),
                int(entry["image_index"]),
                action,
                record["bbox"],
                source,
                dry_run,
                stats,
            )
            continue

        if action == "page_render":
            if asset_changed:
                stats["page_render_assets_written"] += 1
            merge_provenance_file(
                slug,
                asset_rel,
                filename,
                caption,
                int(entry["page"]),
                int(entry["image_index"]),
                action,
                record["bbox"],
                source,
                dry_run,
                stats,
            )
            continue

        image_entry = {
            "src": asset_rel,
            "caption": caption,
            "credit": source["credit"],
            "license": source["license"],
            "source_url": source_page_url_for_assets(source),
        }

        if action == "filmstrip":
            add_filmstrip_entry(page_path, image_entry, source, dry_run, stats, initial_text=initial_text)
        elif action == "inline_figure":
            add_inline_figure(page_path, asset_rel, caption, str(entry.get("paragraph_anchor", "")), source, dry_run, stats, initial_text=initial_text)
        else:
            stats["skipped_unknown_action"] += 1
            continue

        if asset_changed:
            stats["asset_files_written"] += 1
        merge_provenance_file(
            slug,
            asset_rel,
            filename,
            caption,
            int(entry["page"]),
            int(entry["image_index"]),
            action,
            record["bbox"],
            source,
            dry_run,
            stats,
        )

    return stats


def load_decisions(path: Path) -> list[dict[str, Any]]:
    return parse_decisions_text(path.read_text(encoding="utf-8"))


def reconcile_decisions(source_id: str, source: dict[str, str], previous: list[dict[str, Any]], current: list[dict[str, Any]], *, dry_run: bool) -> Counter:
    stats: Counter = Counter()
    prev_map = {(int(entry["page"]), int(entry["image_index"])): entry for entry in previous}
    curr_map = {(int(entry["page"]), int(entry["image_index"])): entry for entry in current}

    for key, old_entry in prev_map.items():
        new_entry = curr_map.get(key)
        if new_entry is not None and decision_signature(old_entry) == decision_signature(new_entry):
            continue
        remove_decision_application(old_entry, source, dry_run, stats)

    apply_stats = execute_decisions(source, current, dry_run=dry_run)
    stats.update(apply_stats)
    cleanup_low_signal_stubs(source_id, current, dry_run, stats)
    return stats


def plan_summary(entries: list[dict[str, Any]]) -> str:
    counts = Counter(str(entry["action"]) for entry in entries)
    lines = ["Plan:"]
    for action, count in sorted(counts.items()):
        lines.append(f"  {action}: {count}")
    for entry in entries[:12]:
        slug = decision_slug(entry) or "?"
        lines.append(f"  p{int(entry['page']):03d} img{int(entry['image_index']):02d} -> {entry['action']} {slug}")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-id", required=True, choices=sorted(SOURCES.keys()))
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--decisions", type=Path)
    parser.add_argument("--reconcile", action="store_true")
    parser.add_argument("--reconcile-from", type=Path)
    parser.add_argument("--only-slug")
    parser.add_argument("--only-page", type=int)
    args = parser.parse_args()

    source = get_source(args.source_id)
    decisions_path = args.decisions or source_abs_path(source, "decisions_v2_yaml")
    reconcile_from = args.reconcile_from or decisions_path

    entries = load_decisions(decisions_path)
    filtered = [entry for entry in entries if record_matches_filters(entry, args.only_slug, args.only_page)]
    print(plan_summary(filtered))
    if args.reconcile:
        previous = load_decisions(reconcile_from)
        previous = [entry for entry in previous if record_matches_filters(entry, args.only_slug, args.only_page)]
        stats = reconcile_decisions(args.source_id, source, previous, filtered, dry_run=args.dry_run)
    else:
        stats = execute_decisions(source, filtered, dry_run=args.dry_run)
    if not stats:
        print("no pending changes")
        return
    print("Results:")
    for key in sorted(stats):
        print(f"  {key}: {stats[key]}")


if __name__ == "__main__":
    main()
