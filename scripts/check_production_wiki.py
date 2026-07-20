#!/usr/bin/env python3
"""Probe the deployed Nepal Energy Wiki's static publication contract.

The check intentionally uses only the Python standard library so it can run in
CI, from an operator laptop, or immediately after a Coolify deployment.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import statistics
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BASE_URL = "https://transparentgov.ai/wiki/explorer/"
DEFAULT_MIN_PAGES = 400
DEFAULT_TIMEOUT_SECONDS = 20.0
DEFAULT_LATENCY_WARNING_SECONDS = 2.0

CORE_SLUGS = (
    "start-here",
    "state-of-the-system",
    "seasonal-mismatch",
    "hydropower-system",
    "transmission-and-cross-border-trade",
    "distribution-and-reliability",
    "solar-system",
    "storage-and-flexibility",
    "demand-and-electrification",
    "institutions-finance-and-project-delivery",
    "environmental-and-social-impacts",
    "climate-resilience-and-decarbonization",
    "master-thesis",
    "unresolved-questions",
)

STATIC_ASSETS = (
    "index.html",
    "shared/style.css",
    "shared/wiki-loader.js",
    "shared/wiki-search.js",
    "shared/wiki-page-index.json",
    "shared/wiki-page-meta-slim.json",
    "shared/wiki-search-index.json",
    "shared/wiki-fact-index.json",
    "shared/wiki-vector-index.json",
    "shared/layer-manifest.json",
    "shared/presets.json",
)

LOCAL_IDENTITY_ASSETS = {
    "index.html": ROOT / "wiki/explorer/index.html",
    "shared/wiki-loader.js": ROOT / "wiki/explorer/shared/wiki-loader.js",
    "shared/wiki-page-index.json": ROOT / "wiki/explorer/shared/wiki-page-index.json",
    "shared/layer-manifest.json": ROOT / "wiki/explorer/shared/layer-manifest.json",
}


@dataclass
class Response:
    url: str
    status: int
    body: bytes
    headers: dict[str, str]
    elapsed_seconds: float


class Results:
    def __init__(self) -> None:
        self.failures: list[str] = []
        self.warnings: list[str] = []
        self.observations: list[str] = []
        self.responses: list[Response] = []

    def fail(self, message: str) -> None:
        self.failures.append(message)

    def warn(self, message: str) -> None:
        self.warnings.append(message)

    def observe(self, message: str) -> None:
        self.observations.append(message)


def normalized_base_url(value: str) -> str:
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise argparse.ArgumentTypeError("base URL must be an absolute http(s) URL")
    return value.rstrip("/") + "/"


def request(url: str, timeout: float, results: Results) -> Response:
    req = Request(
        url,
        headers={
            "Accept-Encoding": "identity",
            "User-Agent": "NepalEnergyWikiProductionCheck/1.0",
        },
    )
    started = time.monotonic()
    try:
        with urlopen(req, timeout=timeout) as opened:
            response = Response(
                url=url,
                status=opened.status,
                body=opened.read(),
                headers={key.lower(): value for key, value in opened.headers.items()},
                elapsed_seconds=time.monotonic() - started,
            )
    except HTTPError as error:
        response = Response(
            url=url,
            status=error.code,
            body=error.read(),
            headers={key.lower(): value for key, value in error.headers.items()},
            elapsed_seconds=time.monotonic() - started,
        )
    except (URLError, TimeoutError, OSError) as error:
        raise RuntimeError(f"request failed for {url}: {error}") from error
    results.responses.append(response)
    return response


def fetch_required(url: str, timeout: float, results: Results) -> Response | None:
    try:
        response = request(url, timeout, results)
    except RuntimeError as error:
        results.fail(str(error))
        return None
    if response.status != 200:
        results.fail(f"expected HTTP 200, got {response.status}: {url}")
        return None
    if not response.body:
        results.fail(f"empty response body: {url}")
        return None
    return response


def parse_json(response: Response, results: Results, label: str) -> Any | None:
    try:
        return json.loads(response.body)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        results.fail(f"invalid JSON for {label}: {error}")
        return None


def check_headers(response: Response, results: Results) -> None:
    content_type = response.headers.get("content-type", "")
    suffix = urlparse(response.url).path.rsplit("/", 1)[-1]
    if suffix.endswith(".json") and "json" not in content_type:
        results.fail(f"JSON has unexpected Content-Type {content_type!r}: {response.url}")
    if not (response.headers.get("etag") or response.headers.get("last-modified")):
        results.warn(f"no ETag or Last-Modified cache validator: {response.url}")


def sha256(body: bytes) -> str:
    return hashlib.sha256(body).hexdigest()


def percentile(values: list[float], proportion: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = min(len(ordered) - 1, max(0, round((len(ordered) - 1) * proportion)))
    return ordered[index]


def run_checks(args: argparse.Namespace) -> Results:
    results = Results()
    base_url = args.base_url
    fetched_assets: dict[str, Response] = {}

    for relative_path in STATIC_ASSETS:
        response = fetch_required(urljoin(base_url, relative_path), args.timeout, results)
        if response is None:
            continue
        fetched_assets[relative_path] = response
        check_headers(response, results)

    page_index_response = fetched_assets.get("shared/wiki-page-index.json")
    page_index = (
        parse_json(page_index_response, results, "wiki page index")
        if page_index_response
        else None
    )
    slug_to_category: dict[str, str] = {}
    if isinstance(page_index, dict):
        all_slugs = page_index.get("allSlugs")
        slug_to_category = page_index.get("slugToCategory", {})
        total_pages = page_index.get("totalPages")
        if not isinstance(all_slugs, list) or not isinstance(slug_to_category, dict):
            results.fail("wiki page index is missing allSlugs or slugToCategory")
        else:
            if total_pages != len(all_slugs):
                results.fail(
                    f"page index totalPages={total_pages!r} but allSlugs has {len(all_slugs)} entries"
                )
            if len(all_slugs) < args.min_pages:
                results.fail(
                    f"page index has {len(all_slugs)} pages; expected at least {args.min_pages}"
                )
            results.observe(f"page index: {len(all_slugs)} pages")
    elif page_index is not None:
        results.fail("wiki page index root must be an object")

    search_response = fetched_assets.get("shared/wiki-search-index.json")
    search_index = (
        parse_json(search_response, results, "wiki search index") if search_response else None
    )
    if isinstance(search_index, dict) and isinstance(search_index.get("pages"), list):
        search_pages = search_index["pages"]
        if isinstance(page_index, dict) and len(search_pages) != page_index.get("totalPages"):
            results.fail(
                f"search index has {len(search_pages)} pages; page index reports "
                f"{page_index.get('totalPages')}"
            )
        results.observe(f"search index: {len(search_pages)} pages")
    elif search_index is not None:
        results.fail("wiki search index is missing its pages array")

    fact_response = fetched_assets.get("shared/wiki-fact-index.json")
    fact_index = parse_json(fact_response, results, "wiki fact index") if fact_response else None
    if isinstance(fact_index, dict) and isinstance(fact_index.get("facts"), list):
        if not fact_index["facts"]:
            results.fail("wiki fact index is empty")
        results.observe(f"structured fact index: {len(fact_index['facts'])} facts")
    elif fact_index is not None:
        results.fail("wiki fact index is missing its facts array")

    vector_response = fetched_assets.get("shared/wiki-vector-index.json")
    vector_index = (
        parse_json(vector_response, results, "wiki vector index") if vector_response else None
    )
    if isinstance(vector_index, dict) and isinstance(vector_index.get("chunks"), list):
        if not vector_index["chunks"]:
            results.fail("wiki vector index is empty")
        vector_page_count = vector_index.get("stats", {}).get("pages")
        if isinstance(page_index, dict) and vector_page_count != page_index.get("totalPages"):
            results.fail(
                f"vector index covers {vector_page_count!r} pages; page index reports "
                f"{page_index.get('totalPages')}"
            )
        results.observe(f"vector search index: {len(vector_index['chunks'])} chunks")
    elif vector_index is not None:
        results.fail("wiki vector index is missing its chunks array")

    for slug in CORE_SLUGS:
        category = slug_to_category.get(slug)
        if not category:
            results.fail(f"core page is absent from page index: {slug}")
            continue
        page_url = urljoin(base_url, f"../pages/{category}/{slug}.md")
        response = fetch_required(page_url, args.timeout, results)
        if response is not None:
            check_headers(response, results)
            if len(response.body) < 250:
                results.fail(f"core page is unexpectedly small ({len(response.body)} bytes): {page_url}")

    manifest_response = fetched_assets.get("shared/layer-manifest.json")
    manifest = (
        parse_json(manifest_response, results, "layer manifest")
        if manifest_response
        else None
    )
    unique_map_urls: dict[str, list[str]] = {}
    if isinstance(manifest, dict) and isinstance(manifest.get("layers"), dict):
        for layer_id, layer in manifest["layers"].items():
            if not isinstance(layer, dict) or not isinstance(layer.get("path"), str):
                results.fail(f"layer {layer_id!r} has no path")
                continue
            map_url = urljoin(base_url, layer["path"])
            unique_map_urls.setdefault(map_url, []).append(layer_id)
        map_content_type_gaps: list[str] = []
        for map_url, layer_ids in unique_map_urls.items():
            response = fetch_required(map_url, args.timeout, results)
            if response is None:
                results.fail(f"map asset used by layers {', '.join(layer_ids)} is unavailable")
                continue
            check_headers(response, results)
            if not any(
                token in response.headers.get("content-type", "")
                for token in ("json", "geo+json")
            ):
                map_content_type_gaps.append(map_url)
            geojson = parse_json(response, results, f"map layers {', '.join(layer_ids)}")
            if not isinstance(geojson, dict) or geojson.get("type") not in {
                "FeatureCollection",
                "Feature",
            }:
                results.fail(f"map asset is not a GeoJSON Feature or FeatureCollection: {map_url}")
            elif geojson.get("type") == "FeatureCollection" and not isinstance(
                geojson.get("features"), list
            ):
                results.fail(f"map FeatureCollection has no features array: {map_url}")
            elif geojson.get("type") == "Feature" and not isinstance(
                geojson.get("geometry"), dict
            ):
                results.fail(f"map Feature has no geometry object: {map_url}")
        results.observe(
            f"map registry: {len(manifest['layers'])} layers, {len(unique_map_urls)} unique assets"
        )
        if map_content_type_gaps:
            results.warn(
                f"{len(map_content_type_gaps)}/{len(unique_map_urls)} GeoJSON assets are served "
                "as text/plain instead of a JSON media type"
            )
    elif manifest is not None:
        results.fail("layer manifest is missing its layers object")

    index_response = fetched_assets.get("index.html")
    style_response = fetched_assets.get("shared/style.css")
    if index_response:
        html = index_response.body.decode("utf-8", errors="replace")
        if not re.search(
            r'<meta[^>]+name=["\']viewport["\'][^>]+content=["\'][^"\']*width=device-width',
            html,
            flags=re.IGNORECASE,
        ):
            results.fail("explorer HTML is missing a device-width viewport declaration")
    if style_response:
        css = style_response.body.decode("utf-8", errors="replace")
        mobile_breakpoints = re.findall(r"@media\s*\([^)]*max-width\s*:", css, re.IGNORECASE)
        if not mobile_breakpoints:
            results.fail("explorer CSS has no max-width mobile breakpoint")
        else:
            results.observe(f"responsive CSS: {len(mobile_breakpoints)} max-width breakpoint(s)")

    missing_url = urljoin(base_url, "shared/__production_probe_expected_404__.json")
    try:
        missing_response = request(missing_url, args.timeout, results)
        if missing_response.status != 404:
            results.fail(
                f"missing-asset control returned {missing_response.status}, expected 404: {missing_url}"
            )
    except RuntimeError as error:
        results.fail(str(error))

    if args.expect_local:
        for relative_path, local_path in LOCAL_IDENTITY_ASSETS.items():
            response = fetched_assets.get(relative_path)
            if response is None:
                continue
            if not local_path.is_file():
                results.fail(f"local release-identity file is missing: {local_path}")
                continue
            local_digest = sha256(local_path.read_bytes())
            remote_digest = sha256(response.body)
            if local_digest != remote_digest:
                results.fail(
                    f"production differs from local {relative_path}: "
                    f"remote {remote_digest[:12]}, local {local_digest[:12]}"
                )
        results.observe(f"release identity: compared {len(LOCAL_IDENTITY_ASSETS)} assets")

    successful = [response for response in results.responses if response.status == 200]
    latencies = [response.elapsed_seconds for response in successful]
    slow = [
        response
        for response in successful
        if response.elapsed_seconds > args.latency_warning
    ]
    for response in slow:
        results.warn(
            f"response took {response.elapsed_seconds:.2f}s "
            f"(warning threshold {args.latency_warning:.2f}s): {response.url}"
        )
    if latencies:
        results.observe(
            "HTTP timing: "
            f"median {statistics.median(latencies):.3f}s, "
            f"p95 {percentile(latencies, 0.95):.3f}s, "
            f"max {max(latencies):.3f}s across {len(latencies)} successful requests"
        )

    validator_count = sum(
        bool(response.headers.get("etag") or response.headers.get("last-modified"))
        for response in successful
    )
    cache_control_count = sum(
        bool(response.headers.get("cache-control")) for response in successful
    )
    if successful:
        results.observe(
            f"cache metadata: {validator_count}/{len(successful)} validators, "
            f"{cache_control_count}/{len(successful)} explicit Cache-Control headers"
        )
        if cache_control_count == 0:
            results.warn(
                "production sends validators but no explicit Cache-Control policy; "
                "browser and intermediary freshness therefore depends on default behavior"
            )

    return results


def report(results: Results, as_json: bool) -> None:
    status = "FAIL" if results.failures else "PASS"
    payload = {
        "status": status,
        "failures": results.failures,
        "warnings": results.warnings,
        "observations": results.observations,
        "requests": len(results.responses),
    }
    if as_json:
        print(json.dumps(payload, indent=2))
        return
    print(f"Production wiki check: {status}")
    for message in results.observations:
        print(f"  OK   {message}")
    for message in results.warnings:
        print(f"  WARN {message}")
    for message in results.failures:
        print(f"  FAIL {message}")
    print(f"  INFO {len(results.responses)} HTTP requests")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", type=normalized_base_url, default=DEFAULT_BASE_URL)
    parser.add_argument("--min-pages", type=int, default=DEFAULT_MIN_PAGES)
    parser.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT_SECONDS)
    parser.add_argument(
        "--latency-warning", type=float, default=DEFAULT_LATENCY_WARNING_SECONDS
    )
    parser.add_argument(
        "--expect-local",
        action="store_true",
        help="also require selected deployed assets to match this checkout byte-for-byte",
    )
    parser.add_argument("--json", action="store_true", help="emit a machine-readable summary")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.min_pages < 1 or args.timeout <= 0 or args.latency_warning <= 0:
        print("numeric arguments must be positive", file=sys.stderr)
        return 2
    results = run_checks(args)
    report(results, args.json)
    return 1 if results.failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
