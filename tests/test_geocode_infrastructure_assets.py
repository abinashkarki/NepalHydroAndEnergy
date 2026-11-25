from __future__ import annotations

import csv
import json
import unittest

from scripts import geocode_infrastructure_assets as geo

MAIN_VIEWPORT = {
    "bbox": [28.80035, 2404.80043, 4291.25214, 14.42393],
    "gpts": [26.31348, 79.98472, 30.48856, 79.82382, 30.47998, 88.43548, 26.30627, 88.26467],
}
MUTM_WKT = (
    'PROJCS["MUTM_EVEREST_1830",GEOGCS["GCS_Everest_Bangladesh",DATUM["D_Everest_Bangladesh",'
    'SPHEROID["Everest_Adjustment_1937",6377276.345,300.8017]],PRIMEM["Greenwich",0.0],'
    'UNIT["Degree",0.0174532925199433]],PROJECTION["Transverse_Mercator"],PARAMETER["False_Easting",500000.0],'
    'PARAMETER["False_Northing",0.0],PARAMETER["Central_Meridian",84.0],PARAMETER["Scale_Factor",0.9999],'
    'PARAMETER["Latitude_Of_Origin",0.0],UNIT["Meter",1.0]]'
)
PAGE_HEIGHT = 2448.0


class NameMatchingTests(unittest.TestCase):
    def test_normalize_strips_generic_words_and_applies_variants(self) -> None:
        self.assertEqual(geo.normalize_name("Ghorahi s/s"), "ghorahi")
        self.assertEqual(geo.normalize_name("Trishuli 3B Hub"), "trishuli3b")
        self.assertEqual(geo.normalize_name("Panckkhal"), geo.normalize_name("Panchkhal"))
        self.assertEqual(geo.normalize_name("NEW ATARIYA"), geo.normalize_name("New Attariya"))
        self.assertEqual(geo.normalize_name("Baneshwor (Koshi Corridor)"), "baneshwor")
        self.assertNotEqual(geo.normalize_name("New Kohalpur"), geo.normalize_name("Kohalpur"))

    def test_name_keys_split_slash_names(self) -> None:
        self.assertEqual(geo.name_keys("Philim / Gumda"), ["philimgumda", "philim", "gumda"])

    def test_loose_keys_match_latin_and_devanagari_spellings(self) -> None:
        pairs = [("Birgunj", "वीरगञ्ज"), ("Nepalgunj", "नेपालगञ्ज"), ("Butwal", "बुटवल"),
                 ("Bhaktapur", "भक्तपुर"), ("Rajbiraj", "राजविराज"), ("Dhangadhi", "धनगढी")]
        for latin, dev in pairs:
            self.assertEqual(geo.loose_key_latin(latin), geo.loose_key_devanagari(dev), latin)
        self.assertNotEqual(geo.loose_key_latin("Damak"), geo.loose_key_devanagari("धरान"))

    def test_canonical_district_aliases(self) -> None:
        self.assertEqual(geo.canonical_district("Nawalparasi (Susta Paschim)"), "Nawalparasi West")
        self.assertEqual(geo.canonical_district("Banke"), "Banke")
        self.assertEqual(len(set(geo.OSM_DISTRICT_NAMES.values())), 77)


class FakeDistricts:
    def __init__(self, mapping: dict[tuple[float, float], str]):
        self.mapping = mapping

    def lookup(self, lon: float, lat: float) -> str:
        return self.mapping.get((lon, lat), "")


class PickTests(unittest.TestCase):
    def test_district_filter_disambiguates_and_rejects_mismatch(self) -> None:
        a = {"lon": 85.3, "lat": 27.7}
        b = {"lon": 87.2, "lat": 27.3}
        d = FakeDistricts({(85.3, 27.7): "Kathmandu", (87.2, 27.3): "Sankhuwasabha"})
        self.assertIs(geo.pick([a, b], "Sankhuwasabha", d, True)[0], b)
        chosen, reason = geo.pick([a], "Lalitpur", d, True)
        self.assertIsNone(chosen)
        self.assertTrue(reason.startswith("district mismatch"))

    def test_rows_without_district_need_a_unique_candidate(self) -> None:
        a = {"lon": 85.3, "lat": 27.7}
        b = {"lon": 87.2, "lat": 27.3}
        self.assertIs(geo.pick([a], "", None, True)[0], a)
        self.assertIsNone(geo.pick([a, b], "", None, True)[0])
        self.assertIsNone(geo.pick([a], "", None, False)[0])


class GeoreferenceTests(unittest.TestCase):
    def test_viewport_corners_round_trip_to_gpts(self) -> None:
        to_geo = geo.georef_factory(MAIN_VIEWPORT["bbox"], MAIN_VIEWPORT["gpts"], MUTM_WKT, PAGE_HEIGHT)
        x1, y1, x2, y2 = MAIN_VIEWPORT["bbox"]
        g = MAIN_VIEWPORT["gpts"]
        # LPTS (0,0) is (x1, y1) in PDF space -> GPTS pair 2 (north-west corner).
        lon, lat = to_geo(x1, PAGE_HEIGHT - y1)
        self.assertAlmostEqual(lat, g[2], places=3)
        self.assertAlmostEqual(lon, g[3], places=3)
        lon, lat = to_geo(x2, PAGE_HEIGHT - y2)
        self.assertAlmostEqual(lat, g[6], places=3)
        self.assertAlmostEqual(lon, g[7], places=3)


class RepositoryOutputTests(unittest.TestCase):
    def test_rpgcl_nodes_are_inside_nepal_and_labelled(self) -> None:
        data = json.loads(geo.RPGCL_NODES.read_text(encoding="utf-8"))
        self.assertGreaterEqual(len(data["features"]), 100)
        for f in data["features"]:
            lon, lat = f["geometry"]["coordinates"]
            self.assertTrue(80.0 <= lon <= 88.3 and 26.0 <= lat <= 30.6, f["properties"]["label"])
            self.assertIn(f["properties"]["symbol_status"], {"existing", "under-construction", "future"})

    def test_registry_coordinates_carry_precision_tags(self) -> None:
        for path in (geo.SUBSTATIONS_CSV, geo.INDUSTRIAL_CSV, geo.FOSSIL_CSV, geo.STORAGE_CSV):
            with path.open(newline="", encoding="utf-8") as handle:
                reader = csv.DictReader(handle)
                self.assertTrue(set(geo.COORD_COLUMNS) <= set(reader.fieldnames or []), path.name)
                for row in reader:
                    has = bool((row["latitude"] or "").strip())
                    self.assertEqual(has, bool((row["longitude"] or "").strip()), path.name)
                    if has:
                        self.assertIn(row["coordinate_precision"], {"official-map-node", "approximate-place"})
                        self.assertTrue(26.0 <= float(row["latitude"]) <= 30.6)
                        self.assertTrue(80.0 <= float(row["longitude"]) <= 88.3)
                    else:
                        self.assertEqual(row["coordinate_precision"], "", path.name)


if __name__ == "__main__":
    unittest.main()
