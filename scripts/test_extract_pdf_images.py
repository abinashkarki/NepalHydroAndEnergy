#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = ROOT / "scripts"
EXTRACT_MODULE_PATH = ROOT / "scripts" / "extract_pdf_images.py"
DECISIONS_MODULE_PATH = ROOT / "scripts" / "build_pdf_image_decisions_v2.py"
LIB_MODULE_PATH = ROOT / "scripts" / "pdf_atlas_lib.py"

if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))


def load_module(module_path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, module_path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ExtractPdfImagesTests(unittest.TestCase):
    def test_parse_decisions_text(self) -> None:
        module = load_module(LIB_MODULE_PATH, "pdf_atlas_lib")
        raw = """
- page: 2
  image_index: 1
  action: inline_figure
  target_slug: "nea"
  proposed_slug: ""
  caption: "Dhalkebar \\u2013 Muzaffarpur"
  paragraph_anchor: "grid operator"
  source_page: 2
- page: 3
  image_index: 0
  action: new_node
  target_slug: ""
  proposed_slug: "foo-bar"
  caption: ""
  paragraph_anchor: ""
  source_page: 3
  candidate_slugs: ["foo", "bar", "baz"]
""".strip()
        rows = module.parse_decisions_text(raw)
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["target_slug"], "nea")
        self.assertEqual(rows[0]["caption"], "Dhalkebar – Muzaffarpur")
        self.assertEqual(rows[1]["proposed_slug"], "foo-bar")
        self.assertEqual(rows[1]["candidate_slugs"], ["foo", "bar", "baz"])

    def test_ensure_source_slug_is_idempotent(self) -> None:
        module = load_module(EXTRACT_MODULE_PATH, "extract_pdf_images")
        text = """---
title: Sample
type: entity
sources: [foo]
tags: [bar]
---

# Sample
"""
        updated = module.ensure_source_slug(text, "nea-transmission-annual-book-2077")
        self.assertIn("sources: [foo, nea-transmission-annual-book-2077]", updated)
        updated_again = module.ensure_source_slug(updated, "nea-transmission-annual-book-2077")
        self.assertEqual(updated_again.count("nea-transmission-annual-book-2077"), 1)

    def test_append_frontmatter_image_is_idempotent(self) -> None:
        module = load_module(EXTRACT_MODULE_PATH, "extract_pdf_images")
        text = """---
title: Sample
type: entity
sources: [foo]
tags: [bar]
images:
  - src: sample/one.png
    caption: "One"
    credit: "Credit"
    license: CC
    source_url: "https://example.com"
---

# Sample
"""
        entry = {
            "src": "sample/two.png",
            "caption": "Two",
            "credit": "Credit",
            "license": "gov-permissive",
            "source_url": "../../../data/raw/corridor_tracing/nea/nea_transmission_annual_book_2077.pdf",
        }
        updated = module.append_frontmatter_image(text, entry)
        self.assertIn("src: sample/two.png", updated)
        updated_again = module.append_frontmatter_image(updated, entry)
        self.assertEqual(updated_again.count("sample/two.png"), 1)

    def test_append_frontmatter_image_replaces_empty_list_form(self) -> None:
        module = load_module(EXTRACT_MODULE_PATH, "extract_pdf_images")
        text = """---
title: Sample
type: entity
sources: [foo]
tags: [bar]
images: []
---

# Sample
"""
        entry = {
            "src": "sample/two.png",
            "caption": "Two",
            "credit": "Credit",
            "license": "gov-permissive",
            "source_url": "../../../data/raw/corridor_tracing/nea/nea_transmission_annual_book_2077.pdf",
        }
        updated = module.append_frontmatter_image(text, entry)
        self.assertIn("images:\n  - src: sample/two.png", updated)
        self.assertNotIn("images: []", updated)

    def test_insert_inline_figure_uses_anchor_and_is_idempotent(self) -> None:
        module = load_module(EXTRACT_MODULE_PATH, "extract_pdf_images")
        text = """---
title: Sample
type: entity
sources: [foo]
tags: [bar]
---

# Sample

First paragraph.

This is the grid operator paragraph with the keyword inside it.

## See also

- [[nea]]
"""
        figure = module.build_inline_figure_block("sample/foo.png", "Foo figure")
        updated = module.insert_inline_figure(text, figure, "sample/foo.png", "grid operator")
        self.assertIn(figure.strip(), updated)
        self.assertLess(updated.index(figure.strip()), updated.index("## See also"))
        updated_again = module.insert_inline_figure(updated, figure, "sample/foo.png", "grid operator")
        self.assertEqual(updated_again.count("sample/foo.png"), 1)

    def test_merge_provenance_entry_is_idempotent(self) -> None:
        module = load_module(EXTRACT_MODULE_PATH, "extract_pdf_images")
        existing = {
            "slug": "nea",
            "entries": [
                {
                    "src": "nea/existing.png",
                    "filename": "existing.png",
                    "caption": "Existing",
                }
            ],
        }
        incoming = {
            "src": "nea/new.png",
            "filename": "new.png",
            "caption": "New",
        }
        merged = module.merge_provenance(existing, incoming, "nea")
        self.assertEqual(len(merged["entries"]), 2)
        merged_again = module.merge_provenance(merged, incoming, "nea")
        self.assertEqual(len(merged_again["entries"]), 2)

    def test_remove_frontmatter_image_is_idempotent(self) -> None:
        module = load_module(EXTRACT_MODULE_PATH, "extract_pdf_images")
        text = """---
title: Sample
type: entity
sources: [nea-transmission-annual-book-2077]
images:
  - src: sample/one.png
    caption: "One"
    credit: "Credit"
    license: gov-permissive
    source_url: "../../../data/raw/corridor_tracing/nea/nea_transmission_annual_book_2077.pdf"
  - src: sample/two.png
    caption: "Two"
    credit: "Credit"
    license: gov-permissive
    source_url: "../../../data/raw/corridor_tracing/nea/nea_transmission_annual_book_2077.pdf"
tags: [bar]
---

# Sample
"""
        updated = module.remove_frontmatter_image(text, "sample/two.png")
        self.assertIn("sample/one.png", updated)
        self.assertNotIn("sample/two.png", updated)
        updated_again = module.remove_frontmatter_image(updated, "sample/two.png")
        self.assertEqual(updated, updated_again)

    def test_remove_inline_figure_and_strip_source_when_unused(self) -> None:
        module = load_module(EXTRACT_MODULE_PATH, "extract_pdf_images")
        text = """---
title: Sample
type: entity
sources: [foo, nea-transmission-annual-book-2077]
tags: [bar]
---

# Sample

<figure class="wiki-inline-figure">
  <img src="../assets/images/sample/nea2077-p001-img01.png" alt="Foo">
  <figcaption>Foo</figcaption>
</figure>

## See also
"""
        updated = module.remove_inline_figure(text, "sample/nea2077-p001-img01.png")
        self.assertNotIn("sample/nea2077-p001-img01.png", updated)
        stripped = module.remove_source_slug_if_unused(updated, "nea-transmission-annual-book-2077", "nea2077")
        self.assertNotIn("nea-transmission-annual-book-2077", stripped)

    def test_remove_source_slug_keeps_source_when_other_source_assets_remain(self) -> None:
        module = load_module(EXTRACT_MODULE_PATH, "extract_pdf_images")
        text = """---
title: Sample
type: entity
sources: [foo, nea-transmission-annual-book-2077]
images:
  - src: sample/nea2077-p002-img01.png
    caption: "One"
    credit: "Credit"
    license: gov-permissive
    source_url: "../../../data/raw/corridor_tracing/nea/nea_transmission_annual_book_2077.pdf"
tags: [bar]
---

# Sample
"""
        updated = module.remove_source_slug_if_unused(text, "nea-transmission-annual-book-2077", "nea2077")
        self.assertIn("nea-transmission-annual-book-2077", updated)

    def test_remove_provenance_entry_returns_none_when_empty(self) -> None:
        module = load_module(EXTRACT_MODULE_PATH, "extract_pdf_images")
        existing = {
            "slug": "nea",
            "entries": [
                {
                    "src": "nea/nea2077-p001-img01.png",
                    "filename": "nea2077-p001-img01.png",
                }
            ],
        }
        updated = module.remove_provenance_entry(existing, "nea/nea2077-p001-img01.png", "nea")
        self.assertIsNone(updated)

    def test_build_new_node_page_contains_required_links(self) -> None:
        module = load_module(EXTRACT_MODULE_PATH, "extract_pdf_images")
        text = module.build_new_node_page(
            slug="foo-bar",
            title="Foo Bar",
            caption="Caption",
            source_slug="nea-transmission-annual-book-2077",
            related_links=["nea", "nepal-transmission-landscape-2025"],
            asset_prefix="nea2077",
        )
        self.assertIn("sources: [nea-transmission-annual-book-2077]", text)
        self.assertIn("[[nea]]", text)
        self.assertIn("[[nepal-transmission-landscape-2025]]", text)

    def test_clamp_bbox_to_page_bounds(self) -> None:
        module = load_module(LIB_MODULE_PATH, "pdf_atlas_lib")
        bbox = [-10.0, -5.0, 650.0, 900.0]
        clamped = module.clamp_bbox_to_page(bbox, 617.953, 864.567)
        self.assertEqual(clamped, [0.0, 0.0, 617.95, 864.57])

    def test_clamp_bbox_returns_none_when_area_collapses(self) -> None:
        module = load_module(LIB_MODULE_PATH, "pdf_atlas_lib")
        bbox = [900.0, 149.55, 950.0, 432.38]
        clamped = module.clamp_bbox_to_page(bbox, 617.953, 864.567)
        self.assertIsNone(clamped)

    def test_asset_filename_uses_source_specific_prefixes(self) -> None:
        lib = load_module(LIB_MODULE_PATH, "pdf_atlas_lib")
        nea2425 = lib.get_source("nea-annual-report-fy2024-25")
        ipsdp = lib.get_source("moewri-ipsdp-exec-summary-2025")
        entry = {"page": 12, "image_index": 3, "action": "filmstrip"}
        self.assertEqual(lib.asset_filename_for(nea2425, entry), "nea2425-p012-img03.png")
        self.assertEqual(lib.asset_filename_for(ipsdp, entry), "ipsdp2025-p012-img03.png")

    def test_source_registry_exposes_multi_source_paths(self) -> None:
        lib = load_module(LIB_MODULE_PATH, "pdf_atlas_lib")
        nea2425 = lib.get_source("nea-annual-report-fy2024-25")
        ipsdp = lib.get_source("moewri-ipsdp-exec-summary-2025")
        self.assertTrue(str(lib.page_index_path_for_source(nea2425)).endswith("nea_annual_report_2024_2025_page_index.json"))
        self.assertTrue(str(lib.source_abs_path(ipsdp, "atlas_json")).endswith("moewri_ipsdp_exec_summary_2025_image_atlas.json"))
        self.assertEqual(nea2425["provenance_filename"], "_nea2425.json")
        self.assertEqual(ipsdp["provenance_filename"], "_ipsdp2025.json")

    def test_claim_or_data_auto_route_drops_with_reviewer_context(self) -> None:
        module = load_module(DECISIONS_MODULE_PATH, "build_pdf_image_decisions_v2")
        source = load_module(LIB_MODULE_PATH, "pdf_atlas_lib").get_source("moewri-ipsdp-exec-summary-2025")
        row = {
            "page": 1,
            "image_index": 0,
            "action": "filmstrip",
            "target_slug": "claim-power-exports",
            "proposed_slug": "",
            "caption": "Power exports surpass imports.",
            "paragraph_anchor": "",
            "source_page": 1,
            "note": "",
            "raw_caption": "Power exports surpass imports.",
            "candidate_slugs": ["claim-power-exports", "nea", "ipsdp"],
        }
        record = {
            "page": 1,
            "image_index": 0,
            "nearest_caption": "Power exports surpass imports.",
            "page_text_excerpt": "Exports surpass imports.",
            "candidate_slugs": [{"slug": "claim-power-exports"}, {"slug": "nea"}, {"slug": "ipsdp"}],
        }
        updated = module.maybe_apply_guardrails(
            "moewri-ipsdp-exec-summary-2025",
            source,
            row,
            record,
            is_override=False,
            counts_by_target=module.Counter(),
        )
        self.assertEqual(updated["action"], "drop")
        self.assertEqual(updated["note"], "skipped:auto-routed-to-claim-or-data")
        self.assertEqual(updated["candidate_slugs"], ["claim-power-exports", "nea", "ipsdp"])

    def test_new_node_bad_shape_is_dropped(self) -> None:
        module = load_module(DECISIONS_MODULE_PATH, "build_pdf_image_decisions_v2")
        source = load_module(LIB_MODULE_PATH, "pdf_atlas_lib").get_source("nea-annual-report-fy2024-25")
        row = {
            "page": 2,
            "image_index": 1,
            "action": "new_node",
            "target_slug": "",
            "proposed_slug": "nea2425-page-001",
            "caption": "",
            "paragraph_anchor": "",
            "source_page": 2,
            "note": "",
            "raw_caption": "Cover image.",
            "candidate_slugs": ["nea", "cover", "report"],
        }
        record = {
            "page": 2,
            "image_index": 1,
            "nearest_caption": "Cover image.",
            "page_text_excerpt": "Cover image.",
            "candidate_slugs": [{"slug": "nea"}, {"slug": "cover"}, {"slug": "report"}],
        }
        updated = module.maybe_apply_guardrails(
            "nea-annual-report-fy2024-25",
            source,
            row,
            record,
            is_override=False,
            counts_by_target=module.Counter(),
        )
        self.assertEqual(updated["action"], "drop")
        self.assertEqual(updated["note"], "skipped:new-node-shape-rejected")

    def test_source_page_auto_route_drops(self) -> None:
        module = load_module(DECISIONS_MODULE_PATH, "build_pdf_image_decisions_v2")
        source = load_module(LIB_MODULE_PATH, "pdf_atlas_lib").get_source("jica-ipsdp-main-report-vol2")
        row = {
            "page": 10,
            "image_index": 0,
            "action": "filmstrip",
            "target_slug": "wb-nepal-power-sector-reform-2022",
            "proposed_slug": "",
            "caption": "World Bank reform diagram.",
            "paragraph_anchor": "",
            "source_page": 10,
            "note": "",
            "raw_caption": "World Bank reform diagram.",
            "candidate_slugs": ["wb-nepal-power-sector-reform-2022", "nea"],
        }
        record = {
            "page": 10,
            "image_index": 0,
            "nearest_caption": "World Bank reform diagram.",
            "page_text_excerpt": "World Bank reform diagram.",
            "candidate_slugs": [{"slug": "wb-nepal-power-sector-reform-2022"}, {"slug": "nea"}],
        }
        updated = module.maybe_apply_guardrails(
            "jica-ipsdp-main-report-vol2",
            source,
            row,
            record,
            is_override=False,
            counts_by_target=module.Counter(),
        )
        self.assertEqual(updated["action"], "drop")
        self.assertEqual(updated["note"], "skipped:auto-routed-to-source")

    def test_source_page_routing_to_own_source_is_allowed(self) -> None:
        module = load_module(DECISIONS_MODULE_PATH, "build_pdf_image_decisions_v2")
        source = load_module(LIB_MODULE_PATH, "pdf_atlas_lib").get_source("jica-ipsdp-main-report-vol2")
        row = {
            "page": 1,
            "image_index": 0,
            "action": "inline_figure",
            "target_slug": "jica-ipsdp-main-report-vol2",
            "proposed_slug": "",
            "caption": "IPSDP cover figure.",
            "paragraph_anchor": "",
            "source_page": 1,
            "note": "",
            "raw_caption": "IPSDP cover figure.",
            "candidate_slugs": ["jica-ipsdp-main-report-vol2", "nea"],
        }
        record = {
            "page": 1,
            "image_index": 0,
            "nearest_caption": "IPSDP cover figure.",
            "page_text_excerpt": "IPSDP cover figure.",
            "candidate_slugs": [{"slug": "jica-ipsdp-main-report-vol2"}, {"slug": "nea"}],
        }
        updated = module.maybe_apply_guardrails(
            "jica-ipsdp-main-report-vol2",
            source,
            row,
            record,
            is_override=False,
            counts_by_target=module.Counter(),
        )
        self.assertEqual(updated["action"], "inline_figure")
        self.assertEqual(updated["target_slug"], "jica-ipsdp-main-report-vol2")

    def test_per_target_cap_drops_sixth_prefill(self) -> None:
        module = load_module(DECISIONS_MODULE_PATH, "build_pdf_image_decisions_v2")
        source = load_module(LIB_MODULE_PATH, "pdf_atlas_lib").get_source("nea-annual-report-fy2024-25")
        counts = module.Counter({"khudi-220-132kv-substation": 5})
        row = {
            "page": 10,
            "image_index": 0,
            "action": "filmstrip",
            "target_slug": "khudi-220-132kv-substation",
            "proposed_slug": "",
            "caption": "Khudi substation.",
            "paragraph_anchor": "",
            "source_page": 10,
            "note": "",
            "raw_caption": "Khudi substation.",
            "candidate_slugs": ["khudi-220-132kv-substation", "nea", "substation"],
        }
        record = {
            "page": 10,
            "image_index": 0,
            "nearest_caption": "Khudi substation.",
            "page_text_excerpt": "Khudi substation.",
            "candidate_slugs": [{"slug": "khudi-220-132kv-substation"}, {"slug": "nea"}, {"slug": "substation"}],
        }
        updated = module.maybe_apply_guardrails(
            "nea-annual-report-fy2024-25",
            source,
            row,
            record,
            is_override=False,
            counts_by_target=counts,
        )
        self.assertEqual(updated["action"], "drop")
        self.assertEqual(updated["note"], "skipped:per-target-cap-reached")


if __name__ == "__main__":
    unittest.main()
