from __future__ import annotations

import json
import re
import subprocess
import unittest
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
WIKI = ROOT / "wiki"
SITE = WIKI / "site"
CONFIG = json.loads((WIKI / "site-config.json").read_text(encoding="utf-8"))
PAGE_INDEX = json.loads((WIKI / "explorer/shared/wiki-page-index.json").read_text(encoding="utf-8"))
PAGE_META = json.loads((WIKI / "explorer/shared/wiki-page-meta.json").read_text(encoding="utf-8"))
META_BY_SLUG = {page["slug"]: page for page in PAGE_META["pages"]}
EXPLORER_SOURCE = (WIKI / "explorer/index.html").read_text(encoding="utf-8")
BASE = CONFIG["canonical_base"].rstrip("/")


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.h1: list[str] = []
        self.in_h1 = False
        self.canonicals: list[str] = []
        self.robots = ""
        self.json_ld: list[str] = []
        self.in_json_ld = False
        self.hrefs: list[str] = []
        self.scripts = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key: value or "" for key, value in attrs}
        if tag == "h1":
            self.in_h1 = True
            self.h1.append("")
        elif tag == "link" and values.get("rel") == "canonical":
            self.canonicals.append(values.get("href", ""))
        elif tag == "meta" and values.get("name") == "robots":
            self.robots = values.get("content", "")
        elif tag == "script":
            if values.get("type") == "application/ld+json":
                self.in_json_ld = True
                self.json_ld.append("")
            else:
                self.scripts += 1
        elif tag == "a" and values.get("href"):
            self.hrefs.append(values["href"])

    def handle_endtag(self, tag: str) -> None:
        if tag == "h1":
            self.in_h1 = False
        elif tag == "script":
            self.in_json_ld = False

    def handle_data(self, data: str) -> None:
        if self.in_h1:
            self.h1[-1] += data
        if self.in_json_ld:
            self.json_ld[-1] += data


def parse(path: Path) -> PageParser:
    parser = PageParser()
    parser.feed(path.read_text(encoding="utf-8"))
    return parser


class StaticSiteTests(unittest.TestCase):
    def test_generated_outputs_are_current(self) -> None:
        result = subprocess.run(
            ["node", "scripts/build_wiki_site.js", "--check"], cwd=ROOT, capture_output=True, text=True, check=False,
        )
        self.assertEqual(0, result.returncode, result.stderr or result.stdout)

    def test_every_page_has_one_static_article(self) -> None:
        slugs = set(PAGE_INDEX["allSlugs"])
        generated = {path.parent.name for path in SITE.glob("*/index.html")}
        self.assertEqual(slugs, generated)

    def test_article_metadata_is_canonical_and_indexable(self) -> None:
        for slug in ["master-thesis", "claim-ror-dominance", "india-cbte-2018", "rasuwagadhi"]:
            with self.subTest(slug=slug):
                page = parse(SITE / slug / "index.html")
                self.assertEqual([f"{BASE}/{slug}/"], page.canonicals)
                self.assertTrue(page.robots.startswith("index"))
                self.assertEqual([META_BY_SLUG[slug]["title"]], [text.strip() for text in page.h1])
                graph = json.loads(page.json_ld[0])["@graph"]
                self.assertEqual(f"{BASE}/{slug}/#article", graph[0]["@id"])
                self.assertEqual(0, page.scripts, "static articles must not need JavaScript")

    def test_internal_links_resolve_to_generated_pages(self) -> None:
        known = set(PAGE_INDEX["allSlugs"])
        broken: list[str] = []
        for path in SITE.glob("*/index.html"):
            for href in parse(path).hrefs:
                match = re.fullmatch(r"/wiki/([^/?#]+)/", href)
                if match and match.group(1) not in known | {"explorer"}:
                    broken.append(f"{path.parent.name} -> {href}")
        self.assertEqual([], broken[:20])

    def test_home_lists_every_page_and_reader_questions(self) -> None:
        home = parse(SITE / "index.html")
        linked = {match.group(1) for href in home.hrefs if (match := re.fullmatch(r"/wiki/([^/?#]+)/", href))}
        self.assertTrue(set(PAGE_INDEX["allSlugs"]) <= linked)
        self.assertEqual([f"{BASE}/"], home.canonicals)
        text = (SITE / "index.html").read_text(encoding="utf-8")
        for question in CONFIG["home"]["questions"]:
            self.assertIn(question["title"].replace("’", "&#39;").replace("'", "&#39;"), text.replace("’", "&#39;"))

    def test_sitemap_lists_home_and_every_page(self) -> None:
        tree = ET.parse(SITE / "sitemap.xml")
        ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        locs = [node.text for node in tree.getroot().findall("s:url/s:loc", ns)]
        expected = [f"{BASE}/"] + [f"{BASE}/{slug}/" for slug in sorted(PAGE_INDEX["allSlugs"])]
        self.assertEqual(expected, locs)

    def test_not_found_page_is_noindex(self) -> None:
        page = parse(SITE / "404.html")
        self.assertEqual("noindex", page.robots)
        self.assertEqual([], page.canonicals)

    def test_overdue_review_is_disclosed(self) -> None:
        today = CONFIG["as_of"]
        for path in sorted((WIKI / "pages").rglob("*.md")):
            match = re.search(r"^review_due:\s*(\d{4}-\d{2}-\d{2})\s*$", path.read_text(encoding="utf-8"), re.M)
            if match and match.group(1) < today:
                html = (SITE / path.stem / "index.html").read_text(encoding="utf-8")
                self.assertIn("Review overdue", html, path.stem)
                return

    def test_explorer_points_search_engines_at_static_pages(self) -> None:
        self.assertIn('<link rel="canonical" id="canonical-link" href="https://transparentgov.ai/wiki/explorer/" />', EXPLORER_SOURCE)
        self.assertIn("https://transparentgov.ai/wiki/${encodeURIComponent(currentSlug)}/", EXPLORER_SOURCE)
        self.assertNotIn("__WIKI_CLEAN_ROUTE_SLUGS__ = Object.freeze", EXPLORER_SOURCE)


if __name__ == "__main__":
    unittest.main()
