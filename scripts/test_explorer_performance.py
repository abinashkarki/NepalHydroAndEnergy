import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
INDEX_HTML = ROOT / "wiki" / "explorer" / "index.html"
LEAFLET_INIT = ROOT / "wiki" / "explorer" / "shared" / "leaflet-init.js"
MANIFEST = ROOT / "wiki" / "explorer" / "shared" / "layer-manifest.json"
PRESETS = ROOT / "wiki" / "explorer" / "shared" / "presets.json"
MAP_DIR = ROOT / "data" / "processed" / "maps"


class ExplorerPerformanceGuardrails(unittest.TestCase):
    def test_layer_control_does_not_preload_all_overlays(self) -> None:
        html = INDEX_HTML.read_text(encoding="utf-8")
        match = re.search(r"async function buildLayerControl\(\) \{(?P<body>.*?)\n      \}", html, re.S)
        self.assertIsNotNone(match, "buildLayerControl() not found")
        body = match.group("body")
        self.assertNotIn("await lm.preload(key)", body)
        self.assertIn("overlayPlaceholders", body)

    def test_json_cache_buster_is_stable(self) -> None:
        html = INDEX_HTML.read_text(encoding="utf-8")
        leaflet = LEAFLET_INIT.read_text(encoding="utf-8")
        self.assertIn('meta name="np-build"', html)
        self.assertNotIn("return String(Date.now())", leaflet)

    def test_shared_geojson_sources_are_cached_by_path(self) -> None:
        leaflet = LEAFLET_INIT.read_text(encoding="utf-8")
        self.assertIn("this.sourceCache", leaflet)
        self.assertIn("this.sourceCache[path] = loadJSON(path)", leaflet)

    def test_default_startup_map_payload_budget(self) -> None:
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        presets = json.loads(PRESETS.read_text(encoding="utf-8"))
        default = presets["presets"][presets["default_preset"]]
        startup_layers = set(default.get("layers_on", [])) | {"country_outline"}
        total = 0
        for key in startup_layers:
            rel = manifest["layers"][key]["path"]
            total += (MAP_DIR / Path(rel).name).stat().st_size
        self.assertLess(total, 2_200_000)

    def test_country_outline_is_simplified_for_startup(self) -> None:
        self.assertLess((MAP_DIR / "nepal_country_outline.geojson").stat().st_size, 250_000)


if __name__ == "__main__":
    unittest.main()
