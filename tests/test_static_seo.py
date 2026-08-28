from __future__ import annotations

import json
import threading
import subprocess
import unittest
import xml.etree.ElementTree as ET
from functools import partial
from html.parser import HTMLParser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import parse_qs, urljoin, urlparse
from urllib.request import urlopen


ROOT = Path(__file__).resolve().parent.parent
WIKI = ROOT / "wiki"
CONFIG = json.loads((WIKI / "seo-pilot-slugs.json").read_text(encoding="utf-8"))
APPROVED_PILOT_SLUGS = [
    "glof-risk",
    "rasuwagadhi",
    "icimod-ndrrma-thame-glof-2024",
    "ndrrma-rasuwa-glacial-flood-sitrep-2025",
    "nea-engineering-annual-report-2081-82",
]
PAGE_META = json.loads((WIKI / "explorer/shared/wiki-page-meta.json").read_text(encoding="utf-8"))
META_BY_SLUG = {page["slug"]: page for page in PAGE_META["pages"]}
MANIFEST_PATH = WIKI / "seo-pilot-manifest.json"
SITEMAP_PATH = WIKI / "seo-pilot-sitemap.xml"
EXPLORER_SOURCE = (WIKI / "explorer/index.html").read_text(encoding="utf-8")
BINDINGS = json.loads((WIKI / "explorer/shared/bindings.json").read_text(encoding="utf-8"))


class SeoDocumentParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.title_parts: list[str] = []
        self.h1_parts: list[str] = []
        self.json_ld_parts: list[str] = []
        self.in_title = False
        self.in_h1 = False
        self.in_json_ld = False
        self.title_count = 0
        self.h1_count = 0
        self.json_ld_count = 0
        self.metas: dict[str, list[str]] = {}
        self.canonicals: list[str] = []
        self.links: list[dict[str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key: value or "" for key, value in attrs}
        if tag == "title":
            self.in_title = True
            self.title_count += 1
        elif tag == "h1":
            self.in_h1 = True
            self.h1_count += 1
        elif tag == "script" and values.get("type") == "application/ld+json":
            self.in_json_ld = True
            self.json_ld_count += 1
        elif tag == "meta":
            key = values.get("name") or values.get("property")
            if key:
                self.metas.setdefault(key, []).append(values.get("content", ""))
        elif tag == "link" and "canonical" in values.get("rel", "").split():
            self.canonicals.append(values.get("href", ""))
        elif tag == "a":
            self.links.append(values)

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self.in_title = False
        elif tag == "h1":
            self.in_h1 = False
        elif tag == "script" and self.in_json_ld:
            self.in_json_ld = False

    def handle_data(self, data: str) -> None:
        if self.in_title:
            self.title_parts.append(data)
        if self.in_h1:
            self.h1_parts.append(data)
        if self.in_json_ld:
            self.json_ld_parts.append(data)

    @property
    def title(self) -> str:
        return "".join(self.title_parts).strip()

    @property
    def h1(self) -> str:
        return "".join(self.h1_parts).strip()

    @property
    def json_ld(self) -> dict:
        return json.loads("".join(self.json_ld_parts))


class StaticSeoPilotTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.slugs = CONFIG["slugs"]
        cls.manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        cls.documents: dict[str, tuple[str, SeoDocumentParser]] = {}
        for slug in cls.slugs:
            html = (WIKI / slug / "index.html").read_text(encoding="utf-8")
            parser = SeoDocumentParser()
            parser.feed(html)
            cls.documents[slug] = (html, parser)

    def test_pilot_inventory_is_exact_and_generated(self) -> None:
        self.assertEqual(APPROVED_PILOT_SLUGS, self.slugs)
        self.assertEqual(5, len(self.slugs))
        self.assertEqual(len(self.slugs), len(set(self.slugs)))
        self.assertEqual("unified-explorer-route-pilot", self.manifest["mode"])
        self.assertEqual(
            "approved-five-page-production-pilot",
            self.manifest["discovery_status"],
        )
        self.assertEqual(self.slugs, [page["slug"] for page in self.manifest["pages"]])
        self.assertEqual(5, self.manifest["generated_pages"])
        for slug in self.slugs:
            self.assertTrue((WIKI / slug / "index.html").is_file())
            self.assertIn(slug, META_BY_SLUG)

    def test_metadata_is_complete_unique_and_source_aligned(self) -> None:
        titles: set[str] = set()
        descriptions: set[str] = set()
        canonicals: set[str] = set()
        required_meta = {
            "description",
            "robots",
            "og:type",
            "og:site_name",
            "og:title",
            "og:description",
            "og:url",
            "twitter:card",
            "twitter:title",
            "twitter:description",
        }
        for slug, (_html, doc) in self.documents.items():
            with self.subTest(slug=slug):
                expected_title = f"{META_BY_SLUG[slug]['title']} · {CONFIG['site_name']}"
                expected_canonical = f"{CONFIG['canonical_base']}/{slug}/"
                self.assertEqual(1, doc.title_count)
                self.assertEqual(1, doc.h1_count)
                self.assertEqual(1, doc.json_ld_count)
                self.assertEqual(expected_title, doc.title)
                self.assertEqual(META_BY_SLUG[slug]["title"], doc.h1)
                self.assertEqual(required_meta, required_meta & set(doc.metas))
                for key in required_meta:
                    self.assertEqual(1, len(doc.metas[key]), f"duplicate {key} on {slug}")
                description = doc.metas["description"][0]
                self.assertGreaterEqual(len(description), 60)
                self.assertLessEqual(len(description), 160)
                self.assertEqual([expected_canonical], doc.canonicals)
                self.assertEqual(expected_canonical, doc.metas["og:url"][0])
                self.assertEqual(expected_title, doc.metas["og:title"][0])
                self.assertEqual(description, doc.metas["og:description"][0])
                self.assertNotIn("?", expected_canonical)
                titles.add(doc.title)
                descriptions.add(description)
                canonicals.add(expected_canonical)
        self.assertEqual(5, len(titles))
        self.assertEqual(5, len(descriptions))
        self.assertEqual(5, len(canonicals))

    def test_json_ld_matches_visible_page_and_canonical(self) -> None:
        for slug, (_html, doc) in self.documents.items():
            with self.subTest(slug=slug):
                data = doc.json_ld
                self.assertEqual("https://schema.org", data["@context"])
                graph = data["@graph"]
                self.assertEqual(3, len(graph))
                self.assertEqual(1, sum(item.get("@type") == "WebPage" for item in graph))
                self.assertEqual(1, sum(item.get("@type") == "BreadcrumbList" for item in graph))
                self.assertEqual(1, sum(item.get("@type") in {"Article", "Report"} for item in graph))
                web_page = next(item for item in graph if item.get("@type") == "WebPage")
                breadcrumbs = next(item for item in graph if item.get("@type") == "BreadcrumbList")
                article = next(item for item in graph if item.get("@type") in {"Article", "Report"})
                self.assertEqual(doc.canonicals[0], web_page["url"])
                self.assertEqual(doc.canonicals[0], web_page["@id"])
                self.assertEqual(doc.canonicals[0], article["url"])
                self.assertEqual(f"{doc.canonicals[0]}#article", article["@id"])
                self.assertEqual(doc.h1, article["headline"])
                self.assertEqual(doc.metas["description"][0], web_page["description"])
                positions = [item["position"] for item in breadcrumbs["itemListElement"]]
                self.assertEqual([1, 2], positions)
                self.assertEqual(doc.canonicals[0], breadcrumbs["itemListElement"][-1]["item"])

    def test_generated_pages_are_the_existing_explorer_shell(self) -> None:
        for slug, (html, _doc) in self.documents.items():
            with self.subTest(slug=slug):
                self.assertIn('<base href="/wiki/explorer/"', html)
                self.assertIn('id="layout"', html)
                self.assertIn('id="nav"', html)
                self.assertIn('id="page"', html)
                self.assertIn('id="map"', html)
                self.assertIn('src="shared/leaflet-init.js', html)
                self.assertIn('src="shared/wiki-loader.js', html)
                self.assertIn('src="shared/wiki-search.js', html)
                self.assertIn(f'data-prerendered-slug="{slug}"', html)
                bootstrap = f'window.__WIKI_ROUTE_BOOTSTRAP__ = {{"mode":"subject","slug":"{slug}"'
                self.assertIn(bootstrap, html)

    def test_explorer_bootstrap_runtime_contract(self) -> None:
        required_fragments = (
            "const routeBootstrap = window.__WIKI_ROUTE_BOOTSTRAP__ || null",
            "(routeBootstrap && routeBootstrap.slug) || params.get(\"page\") || null",
            "window.openWikiPage(url.page, { initialLoad: true })",
            "location.assign(wikiPageHref(slug))",
            "const isBootstrappedSubject = Boolean(routeBootstrap && currentSlug === routeBootstrap.slug)",
            "getCurrentSlug: () => currentSlug",
        )
        for fragment in required_fragments:
            self.assertIn(fragment, EXPLORER_SOURCE)

    def test_clean_route_identity_wins_over_conflicting_legacy_query(self) -> None:
        authoritative_expression = (
            '(routeBootstrap && routeBootstrap.slug) || params.get("page") || null'
        )
        conflicting_expression = (
            'params.get("page") || (routeBootstrap && routeBootstrap.slug) || null'
        )
        self.assertIn(authoritative_expression, EXPLORER_SOURCE)
        self.assertNotIn(conflicting_expression, EXPLORER_SOURCE)

    def test_spatial_and_non_spatial_binding_contract(self) -> None:
        pages = BINDINGS["pages"]
        self.assertEqual("koshi_system", pages["glof-risk"]["features"][0]["id"])
        rasuwagadhi = pages["rasuwagadhi"]
        self.assertEqual("hydropower_points", rasuwagadhi["features"][0]["layer"])
        self.assertEqual("Rasuwagadhi", rasuwagadhi["features"][0]["match"]["value"])
        for slug in APPROVED_PILOT_SLUGS[2:]:
            self.assertNotIn(slug, pages, f"source page {slug} must not invent map focus")

    def test_links_are_crawlable_and_static_routes_resolve(self) -> None:
        for slug, (html, doc) in self.documents.items():
            with self.subTest(slug=slug):
                start = html.index("<!-- wiki-route-prerender:start -->")
                end = html.index("<!-- wiki-route-prerender:end -->")
                article_source = html[start:end]
                self.assertNotIn("[[", article_source)
                self.assertNotIn("javascript:", article_source.lower())
                self.assertGreater(len(article_source), 500)
                canonical_page_links = 0
                for link in doc.links:
                    href = link.get("href", "")
                    self.assertTrue(href, f"empty href on {slug}")
                    parsed = urlparse(href)
                    if parsed.path.startswith("/wiki/explorer/"):
                        query = parse_qs(parsed.query)
                        if query:
                            self.assertIn(link.get("data-route"), {"interactive-explorer", "explorer-fallback"})
                            self.assertEqual({"page"}, set(query))
                        continue
                    parts = parsed.path.strip("/").split("/")
                    if len(parts) == 2 and parts[0] == "wiki":
                        target = parts[1]
                        self.assertIn(target, self.slugs)
                        self.assertTrue((WIKI / target / "index.html").is_file())
                        self.assertEqual("canonical-page", link.get("data-route"))
                        canonical_page_links += 1
                    if link.get("data-route") == "explorer-fallback":
                        self.assertTrue(href.startswith("/wiki/explorer/?page="))
                self.assertGreater(canonical_page_links, 0, f"no canonical article link on {slug}")

    def test_nested_assets_legacy_route_and_unknown_route_http_contract(self) -> None:
        class QuietHandler(SimpleHTTPRequestHandler):
            def log_message(self, _format: str, *_args: object) -> None:
                return

        handler = partial(QuietHandler, directory=str(ROOT))
        server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        origin = f"http://127.0.0.1:{server.server_port}"
        try:
            for slug in self.slugs:
                with urlopen(f"{origin}/wiki/{slug}/") as response:
                    self.assertEqual(200, response.status)
                    self.assertIn("text/html", response.headers.get("content-type", ""))
                    response.read()
            for path in (
                "/wiki/explorer/shared/style.css",
                "/wiki/explorer/shared/wiki-loader.js",
                "/wiki/explorer/shared/wiki-page-index.json",
                "/wiki/pages/entities/rasuwagadhi.md",
                "/data/processed/maps/hydropower_project_display_points.geojson",
            ):
                with urlopen(origin + path) as response:
                    self.assertEqual(200, response.status, path)
                    response.read()
            with urlopen(f"{origin}/wiki/explorer/?page=glof-risk") as response:
                self.assertEqual(200, response.status)
                response.read()
            with self.assertRaises(HTTPError) as missing:
                urlopen(f"{origin}/wiki/not-a-real-page/")
            self.assertEqual(404, missing.exception.code)
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)

    def test_route_base_resolves_shared_assets_to_explorer(self) -> None:
        for slug, (_html, doc) in self.documents.items():
            with self.subTest(slug=slug):
                base_url = f"https://transparentgov.ai/wiki/explorer/"
                self.assertEqual(
                    "https://transparentgov.ai/wiki/explorer/shared/style.css?v=public-launch-11",
                    urljoin(base_url, "shared/style.css?v=public-launch-11"),
                )
                self.assertEqual(
                    "https://transparentgov.ai/wiki/pages/entities/rasuwagadhi.md",
                    urljoin(base_url, "../pages/entities/rasuwagadhi.md"),
                )
                self.assertEqual(1, len(doc.canonicals))

    def test_source_pages_show_provenance(self) -> None:
        source_slugs = [page["slug"] for page in self.manifest["pages"] if page["category"] == "sources"]
        self.assertEqual(3, len(source_slugs))
        for slug in source_slugs:
            html, _doc = self.documents[slug]
            self.assertIn('class="provenance"', html)
            self.assertIn("Open the original source", html)
            self.assertIn("Used By", html)

    def test_pilot_sitemap_is_valid_but_not_query_based(self) -> None:
        tree = ET.parse(SITEMAP_PATH)
        namespace = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        locations = [node.text for node in tree.findall("sm:url/sm:loc", namespace)]
        expected = [f"{CONFIG['canonical_base']}/{slug}/" for slug in self.slugs]
        self.assertEqual(expected, locations)
        self.assertEqual(len(locations), len(set(locations)))
        self.assertTrue(all("?" not in location and "#" not in location for location in locations))
        manifest_by_canonical = {page["canonical"]: page for page in self.manifest["pages"]}
        self.assertEqual(set(expected), set(manifest_by_canonical))
        for location in locations:
            page = manifest_by_canonical[location]
            output = ROOT / page["output"]
            self.assertTrue(output.is_file())
            _html, doc = self.documents[page["slug"]]
            self.assertEqual(location, doc.canonicals[0])

    def test_generated_outputs_are_current(self) -> None:
        result = subprocess.run(
            ["node", "scripts/build_wiki_seo.js", "--check"],
            cwd=ROOT,
            check=False,
            text=True,
            capture_output=True,
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
