"""Regression tests for the RPGCL GeoPDF georeference (scripts/rpgcl_georef.py)."""
from __future__ import annotations

import json
import math
import re
import unittest
from pathlib import Path

from scripts import rpgcl_georef as rg
from tests.test_geocode_infrastructure_assets import MAIN_VIEWPORT, MUTM_WKT, PAGE_HEIGHT

ROOT = Path(__file__).resolve().parent.parent
VP = {**MAIN_VIEWPORT, "wkt": MUTM_WKT}


def km(a: tuple[float, float], b: tuple[float, float]) -> float:
    (lo1, la1), (lo2, la2) = a, b
    return math.hypot((la1 - la2) * 111.0, (lo1 - lo2) * 111.0 * math.cos(math.radians(la1)))


class GeorefTests(unittest.TestCase):
    def setUp(self) -> None:
        self.to_geo = rg.georef_factory(VP["bbox"], VP["gpts"], MUTM_WKT, PAGE_HEIGHT)
        self.frame = rg.fitz_frame(VP["bbox"], PAGE_HEIGHT)

    def test_fitz_frame_flips_pdf_user_space(self) -> None:
        x0, y0, x1, y1 = self.frame
        self.assertAlmostEqual(y0, PAGE_HEIGHT - 2404.80043, places=4)
        self.assertAlmostEqual(y1, PAGE_HEIGHT - 14.42393, places=4)
        self.assertLess(x0, x1)

    def test_frame_corners_hit_gpts(self) -> None:
        x0, y0, x1, y1 = self.frame
        g = VP["gpts"]
        # fitz top-left = LPTS (0,0) = GPTS pair 2 (north-west corner)
        for (fx, fy), (lat, lon) in [((x0, y0), (g[2], g[3])), ((x0, y1), (g[0], g[1])), ((x1, y0), (g[4], g[5]))]:
            lon_c, lat_c = self.to_geo(fx, fy)
            self.assertLess(km((lon_c, lat_c), (lon, lat)), 0.5)

    def test_legacy_mapping_was_biased_south(self) -> None:
        legacy = rg.legacy_point_to_geo_factory(VP["bbox"], VP["gpts"])
        x0, y0, x1, y1 = self.frame
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        (lo_old, la_old), (lo_new, la_new) = legacy(cx, cy), self.to_geo(cx, cy)
        self.assertLess(la_old, la_new)
        self.assertGreater(km((lo_old, la_old), (lo_new, la_new)), 5.0)

    def test_legacy_correction_round_trips(self) -> None:
        legacy = rg.legacy_point_to_geo_factory(VP["bbox"], VP["gpts"])
        fix = rg.legacy_correction_from_viewport(VP, PAGE_HEIGHT)
        for fx, fy in [(500.0, 600.0), (2100.0, 1300.0), (3900.0, 2200.0)]:
            corrected = fix(*legacy(fx, fy))
            expected = self.to_geo(fx, fy)
            self.assertLess(km(corrected, expected), 1e-6)


class CommittedOutputsTests(unittest.TestCase):
    """Guard against re-committing coordinates from the legacy (biased) georeference."""

    def test_rpgcl_anchors_in_build_tributary_maps_are_corrected(self) -> None:
        text = (ROOT / "scripts" / "build_tributary_maps.py").read_text(encoding="utf-8")
        rpgcl_bases = re.findall(r'"basis": "(RPGCL 2021[^"]*)"', text)
        self.assertGreaterEqual(len(rpgcl_bases), 16)
        for basis in rpgcl_bases:
            self.assertIn("corrected RPGCL georeference", basis)

    def test_labels_agree_with_rpgcl_substation_symbols(self) -> None:
        labels = json.loads((ROOT / "data/processed/maps/rpgcl_transmission_official_labels.geojson").read_text())
        nodes = json.loads((ROOT / "data/processed/maps/rpgcl_substation_nodes.geojson").read_text())
        by_text: dict[str, list[tuple[float, float]]] = {}
        for f in labels["features"]:
            by_text.setdefault(f["properties"]["text"].strip().lower(), []).append(tuple(f["geometry"]["coordinates"]))
        dists = sorted(
            min(km(tuple(n["geometry"]["coordinates"]), p) for p in by_text[key])
            for n in nodes["features"]
            if (key := n["properties"]["label"].strip().lower()) in by_text
        )
        self.assertGreater(len(dists), 100)
        self.assertLess(dists[len(dists) // 2], 4.0)  # legacy median was ~13 km


if __name__ == "__main__":
    unittest.main()
