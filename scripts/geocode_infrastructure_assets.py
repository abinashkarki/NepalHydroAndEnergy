#!/usr/bin/env python3
"""Deterministically geocode grid substations and spatial energy registries.

Only fills BLANK coordinates; existing coordinates are never overwritten.

Sources, in priority order (all local, no network):

1. ``data/processed/maps/rpgcl_substation_nodes.geojson`` -- substation symbols
   (EXISTING / UNDER_CONSTRUCTION / FUTURE S/S markers) read from the official
   RPGCL "Nepal Power Transmission Network Map" GeoPDF, each paired with its
   map label by mutual-nearest-neighbour matching. Rebuilt from the gitignored
   PDF with ``--refresh-rpgcl-nodes``; otherwise the committed GeoJSON is used.
   Matches are tagged ``official-map-node``.
2. ``data/processed/maps/place_anchor_index.geojson`` -- curated place anchors
   (Nominatim place-level matches); tagged ``approximate-place``.
3. ``data/raw/maps/nepal-osm-free.shp.zip`` -- Geofabrik OpenStreetMap places
   with a Latin-script name; tagged ``approximate-place``.

Matching is conservative:
* names are normalised (case, diacritics, punctuation, generic words such as
  'substation'/'hub'/'switching') plus a small, explicit spelling-variant table;
* a candidate is accepted only when it is the single candidate left after the
  district filter -- the candidate point must fall inside the row's district
  polygon (OSM admin_level 6). Rows without a district accept only an RPGCL
  node whose name is unique on the whole map;
* the georeference uses the GeoPDF's own Transverse Mercator (MUTM, CM 84)
  measure dictionary, not a lat/lon bilinear fit.

Usage:
    python scripts/geocode_infrastructure_assets.py                 # dry-run report
    python scripts/geocode_infrastructure_assets.py --write         # update CSVs
    python scripts/geocode_infrastructure_assets.py --refresh-rpgcl-nodes \
        --rpgcl-pdf /path/to/nepal_transmission_network_map_revised1.pdf --write
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import os
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(os.environ.get("NEPAL_ENERGY_ROOT", Path(__file__).resolve().parent.parent))
MAPS = ROOT / "data" / "processed" / "maps"
RPGCL_PDF = ROOT / "data" / "raw" / "corridor_tracing" / "rpgcl" / "nepal_transmission_network_map_revised1.pdf"
RPGCL_NODES = MAPS / "rpgcl_substation_nodes.geojson"
PLACE_ANCHORS = MAPS / "place_anchor_index.geojson"
OSM_ZIP = ROOT / "data" / "raw" / "maps" / "nepal-osm-free.shp.zip"

SUBSTATIONS_CSV = ROOT / "data" / "substation_specs.csv"
INDUSTRIAL_CSV = ROOT / "data" / "industrial_load_anchors.csv"
FOSSIL_CSV = ROOT / "data" / "fossil_infrastructure.csv"
STORAGE_CSV = ROOT / "data" / "storage_non_dam_specs.csv"

RUN_DATE = "2026-11-25"
SCRIPT_TAG = "scripts/geocode_infrastructure_assets.py"
COORD_COLUMNS = ["latitude", "longitude", "coordinate_precision"]

# ---------------------------------------------------------------------------
# Canonical district names (Tier B canonical-geography lookup).
# OSM admin_level-6 polygons are named in Devanagari; this maps them to the
# Latin spellings used in the repository CSVs.
# ---------------------------------------------------------------------------
OSM_DISTRICT_NAMES: dict[str, str] = {
    "अछाम": "Achham", "अर्घाखाँची": "Arghakhanchi", "इलाम": "Ilam", "उदयपुर": "Udayapur",
    "ओखलढुङ्गा": "Okhaldhunga", "कञ्चनपुर": "Kanchanpur", "कपिलवस्तु": "Kapilvastu",
    "काठमाडौं": "Kathmandu", "काभ्रेपलाञ्चोक": "Kavrepalanchok", "कालीकोट": "Kalikot",
    "कास्की": "Kaski", "कैलाली": "Kailali", "खोटाङ": "Khotang", "गुल्मी": "Gulmi",
    "गोरखा": "Gorkha", "चितवन": "Chitwan", "जाजरकोट": "Jajarkot", "झापा": "Jhapa",
    "डडेलधुरा": "Dadeldhura", "डोटी": "Doti", "डोल्पा": "Dolpa", "तनहुँ": "Tanahun",
    "ताप्लेजुङ": "Taplejung", "तेह्रथुम": "Terhathum", "दाङ": "Dang", "दार्चुला": "Darchula",
    "दैलेख": "Dailekh", "दोलखा": "Dolakha", "धनकुटा": "Dhankuta", "धनुषा": "Dhanusha",
    "धादिङ": "Dhading", "नुवाकोट": "Nuwakot", "पर्वत": "Parbat", "पर्सा": "Parsa",
    "पश्चिमी रुकुम": "Rukum West", "पाँचथर": "Panchthar", "पाल्पा": "Palpa",
    "पूर्वी रुकुम": "Rukum East", "प्युठान": "Pyuthan", "बझाङ": "Bajhang", "बर्दिया": "Bardiya",
    "बाँके": "Banke", "बागलुङ": "Baglung", "बाजुरा": "Bajura", "बारा": "Bara", "बैतडी": "Baitadi",
    "भक्तपुर": "Bhaktapur", "भोजपुर": "Bhojpur", "मकवानपुर": "Makwanpur", "मनाङ": "Manang",
    "महोत्तरी": "Mahottari", "मुगु": "Mugu", "मुस्ताङ": "Mustang", "मोरङ": "Morang",
    "म्याग्दी": "Myagdi", "रसुवा": "Rasuwa", "रामेछाप": "Ramechhap", "रुपन्देही": "Rupandehi",
    "रोल्पा": "Rolpa", "रौतहट": "Rautahat", "लमजुङ": "Lamjung", "ललितपुर": "Lalitpur",
    "सङ्खुवासभा": "Sankhuwasabha", "सप्तरी": "Saptari", "सर्लाही": "Sarlahi", "सल्यान": "Salyan",
    "सिन्धुपाल्चोक": "Sindhupalchok", "सिन्धुली": "Sindhuli", "सिराहा": "Siraha",
    "सुनसरी": "Sunsari", "सुर्खेत": "Surkhet", "सोलुखुम्बु": "Solukhumbu", "स्याङ्जा": "Syangja",
    "हुम्ला": "Humla", "Jumla": "Jumla", "Nawalparasi W": "Nawalparasi West",
    "Nawalpur District": "Nawalparasi East",
}

# Variant district spellings found in repository CSVs -> canonical name.
DISTRICT_ALIASES = {
    "nawalparasi (susta paschim)": "Nawalparasi West",
    "nawalparasi susta paschim": "Nawalparasi West",
    "parasi": "Nawalparasi West",
    "nawalpur": "Nawalparasi East",
    "kavre": "Kavrepalanchok",
    "kabhrepalanchok": "Kavrepalanchok",
    "sindhupalchowk": "Sindhupalchok",
    "makawanpur": "Makwanpur",
    "illam": "Ilam",
    "dhanusa": "Dhanusha",
    "tanahu": "Tanahun",
    "rukum (west)": "Rukum West",
    "western rukum": "Rukum West",
}

# Explicit spelling variants (applied to both sides after normalisation).
# Each entry is a transliteration variant of the same place name, never a
# different place.
NAME_VARIANTS = {
    "atariya": "attariya",
    "attaria": "attariya",
    "newatariya": "newattariya",
    "shyangja": "syangja",
    "tamghash": "tamghas",
    "lumki": "lamki",
    "kusma": "kushma",
    "panckkhal": "panchkhal",  # RPGCL map typo
    "lapsephedi": "lapsiphedi",
    "bafikot": "banfikot",
    "dhungesanu": "dhungesanghu",
    "dandakhet": "dadakhet",
    "illam": "ilam",
    "raxual": "raxaul",
    "bardaghat": "bardghat",
    "sunawal": "sunwal",
    "pahalwanpur": "pahalmanpur",
    "chandranigahapur": "chandranigahpur",
}

GENERIC_WORDS = re.compile(
    r"\b(substation|sub-station|sub station|s/s|ss|hub|switching|switchyard|grid|gis|ais|kv|lilo)\b",
    re.IGNORECASE,
)


def normalize_name(text: str) -> str:
    text = unicodedata.normalize("NFKD", text or "")
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = re.sub(r"\([^)]*\)", " ", text)  # drop parenthetical qualifiers
    text = re.sub(r"\d+\s*/\s*\d+(?:\s*/\s*\d+)?\s*kv", " ", text, flags=re.IGNORECASE)
    text = GENERIC_WORDS.sub(" ", text)
    key = re.sub(r"[^a-z0-9]", "", text.lower())
    return NAME_VARIANTS.get(key, key)


def canonical_district(text: str) -> str:
    raw = (text or "").strip()
    if not raw:
        return ""
    return DISTRICT_ALIASES.get(raw.lower(), raw)


def round6(value: float) -> str:
    return f"{value:.6f}".rstrip("0").rstrip(".")


# ---------------------------------------------------------------------------
# RPGCL GeoPDF substation nodes
# ---------------------------------------------------------------------------
SS_SYMBOL_COLORS = {15539236: "existing", 42576: "under-construction", 25251: "future"}
LABEL_FONT = "Arial-Black"
LABEL_MIN_SIZE = 10.0
MAX_LABEL_DISTANCE = 10.0  # PDF points from the marker centre to the label box


# The georeference lives in scripts/rpgcl_georef.py (shared with extract_rpgcl_transmission_vectors.py).
sys.path.insert(0, str(Path(__file__).resolve().parent))
from rpgcl_georef import georef_factory  # noqa: E402


def _box_distance(px: float, py: float, box: tuple[float, float, float, float]) -> float:
    x0, y0, x1, y1 = box
    dx = max(x0 - px, 0.0, px - x1)
    dy = max(y0 - py, 0.0, py - y1)
    return math.hypot(dx, dy)


def extract_rpgcl_substation_nodes(pdf_path: Path) -> list[dict[str, Any]]:
    import fitz
    from pypdf import PdfReader

    reader = PdfReader(str(pdf_path))
    page0 = reader.pages[0]
    page_height = float(page0.mediabox.height)
    viewports: dict[str, dict[str, Any]] = {}
    for vp_ref in page0["/VP"]:
        vp = vp_ref.get_object()
        measure = vp["/Measure"].get_object()
        gcs = measure["/GCS"].get_object()
        viewports[str(vp["/Name"])] = {
            "bbox": [float(v) for v in vp["/BBox"]],
            "gpts": [float(v) for v in measure["/GPTS"]],
            "wkt": str(gcs["/WKT"]),
        }
    main, inset = viewports["Layers"], viewports["New Data Frame"]
    to_geo_main = georef_factory(main["bbox"], main["gpts"], main["wkt"], page_height)
    to_geo_inset = georef_factory(inset["bbox"], inset["gpts"], inset["wkt"], page_height)
    ix1, iy1, ix2, iy2 = inset["bbox"]
    inset_fitz = (min(ix1, ix2), page_height - max(iy1, iy2), max(ix1, ix2), page_height - min(iy1, iy2))
    mx1, my1, mx2, my2 = main["bbox"]
    main_fitz = (min(mx1, mx2), page_height - max(my1, my2), max(mx1, mx2), page_height - min(my1, my2))
    inset_lats = inset["gpts"][0::2]
    inset_lons = inset["gpts"][1::2]
    inset_geo = (min(inset_lons), min(inset_lats), max(inset_lons), max(inset_lats))

    def frame_of(x: float, y: float) -> str | None:
        if inset_fitz[0] <= x <= inset_fitz[2] and inset_fitz[1] <= y <= inset_fitz[3]:
            return "inset"
        if main_fitz[0] <= x <= main_fitz[2] and main_fitz[1] <= y <= main_fitz[3]:
            return "main"
        return None

    page = fitz.open(str(pdf_path))[0]
    markers: list[dict[str, Any]] = []
    labels: list[dict[str, Any]] = []
    for block in page.get_text("dict")["blocks"]:
        for line in block.get("lines", []):
            for span in line["spans"]:
                text = span["text"].replace("\x00", "")
                x0, y0, x1, y1 = span["bbox"]
                cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
                frame = frame_of(cx, cy)
                if frame is None:
                    continue
                if span["font"] == "ESRIDefaultMarker" and text == '"' and span["color"] in SS_SYMBOL_COLORS:
                    markers.append({"x": cx, "y": cy, "frame": frame, "symbol": SS_SYMBOL_COLORS[span["color"]]})
                elif span["font"] == LABEL_FONT and span["size"] >= LABEL_MIN_SIZE and len(text.strip()) > 1:
                    labels.append({"text": " ".join(text.split()), "box": (x0, y0, x1, y1), "frame": frame})

    # Mutual nearest neighbour pairing, per frame.
    nodes: list[dict[str, Any]] = []
    for frame in ("main", "inset"):
        fm = [m for m in markers if m["frame"] == frame]
        fl = [lab for lab in labels if lab["frame"] == frame]
        if not fm or not fl:
            continue
        nearest_label = {}
        for i, m in enumerate(fm):
            dists = sorted((_box_distance(m["x"], m["y"], lab["box"]), j) for j, lab in enumerate(fl))
            nearest_label[i] = dists[0]
        nearest_marker = {}
        for j, lab in enumerate(fl):
            dists = sorted((_box_distance(m["x"], m["y"], lab["box"]), i) for i, m in enumerate(fm))
            nearest_marker[j] = dists[0]
        for i, m in enumerate(fm):
            dist, j = nearest_label[i]
            if dist > MAX_LABEL_DISTANCE or nearest_marker[j][1] != i:
                continue
            to_geo = to_geo_inset if frame == "inset" else to_geo_main
            lon, lat = to_geo(m["x"], m["y"])
            if frame == "main" and inset_geo[0] <= lon <= inset_geo[2] and inset_geo[1] <= lat <= inset_geo[3]:
                # Kathmandu-valley symbols on the 1:~1.9M main map are too cluttered to
                # pair reliably; the large-scale inset covers this extent instead.
                continue
            nodes.append({
                "label": fl[j]["text"],
                "symbol": m["symbol"],
                "frame": frame,
                "page_x": round(m["x"], 2),
                "page_y": round(m["y"], 2),
                "label_distance_pt": round(dist, 2),
                "lon": lon,
                "lat": lat,
            })
    nodes.sort(key=lambda n: (n["frame"], n["label"], n["page_x"], n["page_y"]))
    return nodes


def write_rpgcl_nodes(nodes: list[dict[str, Any]], districts: "DistrictIndex | None") -> None:
    features = []
    for idx, n in enumerate(nodes, start=1):
        props = {
            "node_id": f"rpgcl_ss_{idx:03d}",
            "label": n["label"],
            "name_key": normalize_name(n["label"]),
            "symbol_status": n["symbol"],
            "map_frame": n["frame"],
            "page_x": n["page_x"],
            "page_y": n["page_y"],
            "label_distance_pt": n["label_distance_pt"],
            "district": districts.lookup(n["lon"], n["lat"]) if districts else "",
            "source_pdf": RPGCL_PDF.name,
            "basis": "RPGCL Nepal Power Transmission Network Map substation symbol paired with its map label "
                     "(mutual nearest neighbour); georeferenced with the GeoPDF MUTM measure dictionary",
        }
        features.append({
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [round(n["lon"], 6), round(n["lat"], 6)]},
            "properties": props,
        })
    payload = {"type": "FeatureCollection", "name": "rpgcl_substation_nodes", "features": features}
    RPGCL_NODES.write_text(json.dumps(payload, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


def load_rpgcl_nodes() -> list[dict[str, Any]]:
    if not RPGCL_NODES.exists():
        return []
    data = json.loads(RPGCL_NODES.read_text(encoding="utf-8"))
    out = []
    for f in data["features"]:
        p = f["properties"]
        lon, lat = f["geometry"]["coordinates"]
        out.append({**p, "lon": lon, "lat": lat})
    return out


# ---------------------------------------------------------------------------
# OSM district polygons and places
# ---------------------------------------------------------------------------
class DistrictIndex:
    def __init__(self, osm_zip: Path):
        import shapefile
        from shapely.geometry import shape
        from shapely.strtree import STRtree

        reader = shapefile.Reader(f"{osm_zip}/gis_osm_adminareas_a_free_1.shp")
        geoms, names = [], []
        for sr in reader.iterShapeRecords():
            if sr.record["fclass"] != "admin_level6":
                continue
            raw = (sr.record["name"] or "").replace(" जिल्ला", "").strip()
            if raw not in OSM_DISTRICT_NAMES:
                raise SystemExit(f"unmapped OSM district name: {raw!r}")
            geoms.append(shape(sr.shape.__geo_interface__))
            names.append(OSM_DISTRICT_NAMES[raw])
        if len(set(names)) != 77:
            raise SystemExit(f"expected 77 OSM districts, found {len(set(names))}")
        self._geoms = geoms
        self._names = names
        self._tree = STRtree(geoms)

    def lookup(self, lon: float, lat: float) -> str:
        from shapely.geometry import Point

        pt = Point(lon, lat)
        hits = [self._names[i] for i in self._tree.query(pt) if self._geoms[i].covers(pt)]
        return hits[0] if len(set(hits)) == 1 else ""

    def distance_km(self, lon: float, lat: float, district: str) -> float:
        """Approximate distance (km) from a point to the named district polygon (0 if inside)."""
        from shapely.geometry import Point
        from shapely.ops import nearest_points

        pt = Point(lon, lat)
        best = float("inf")
        for geom, name in zip(self._geoms, self._names):
            if name != district:
                continue
            if geom.covers(pt):
                return 0.0
            near = nearest_points(geom, pt)[0]
            best = min(best, _km(lat, lon, near.y, near.x))
        return best


# Loose phonetic key shared by Latin and Devanagari spellings: vowels and
# aspiration dropped, dental/retroflex and b/v merged, doubled letters collapsed.
DEVANAGARI_CONSONANTS = {
    "क": "k", "ख": "k", "ग": "g", "घ": "g", "ङ": "n", "च": "c", "छ": "c", "ज": "j", "झ": "j",
    "ञ": "n", "ट": "t", "ठ": "t", "ड": "d", "ढ": "d", "ण": "n", "त": "t", "थ": "t", "द": "d",
    "ध": "d", "न": "n", "प": "p", "फ": "p", "ब": "b", "भ": "b", "म": "m", "य": "y", "र": "r",
    "ल": "l", "व": "b", "श": "s", "ष": "s", "स": "s", "ह": "h", "ऋ": "r", "ृ": "r", "ड़": "r", "ढ़": "r",
}
DEVANAGARI_RE = re.compile(r"[\u0900-\u097F]")


def _collapse(key: str) -> str:
    return re.sub(r"(.)\1+", r"\1", key)


def loose_key_latin(text: str) -> str:
    t = normalize_name(text)
    t = re.sub(r"[0-9]", "", t)
    t = t.replace("chh", "c").replace("ch", "c").replace("ph", "p").replace("f", "p")
    t = t.replace("v", "b").replace("w", "b").replace("z", "j").replace("q", "k").replace("x", "ks")
    t = re.sub(r"(?<=[kgcjtdpbs])h", "", t)
    t = re.sub(r"[aeiou]", "", t)
    return _collapse(t)


def loose_key_devanagari(text: str) -> str:
    text = unicodedata.normalize("NFC", text or "")
    text = re.sub(r"\s*(बजार|बजा़र)$", "", text.strip())
    out = []
    for ch in text:
        if ch in DEVANAGARI_CONSONANTS:
            out.append(DEVANAGARI_CONSONANTS[ch])
    return _collapse("".join(out))


LATIN_NAME = re.compile(r"[A-Za-z][A-Za-z .'\-()]*")
OSM_PLACE_CLASSES = {"national_capital", "city", "town", "village", "suburb", "locality", "hamlet"}


OSM_DEVANAGARI_CLASSES = {"national_capital", "city", "town", "village", "suburb"}


def load_osm_places(osm_zip: Path) -> tuple[dict[str, list[dict[str, Any]]], dict[str, list[dict[str, Any]]]]:
    """Return (exact Latin-name index, loose phonetic index of Devanagari-named places)."""
    import shapefile

    reader = shapefile.Reader(f"{osm_zip}/gis_osm_places_free_1.shp")
    by_key: dict[str, list[dict[str, Any]]] = defaultdict(list)
    by_loose: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for sr in reader.iterShapeRecords():
        rec = sr.record
        name = (rec["name"] or "").strip()
        lon, lat = sr.shape.points[0]
        entry = {"name": name, "fclass": rec["fclass"], "osm_id": rec["osm_id"], "lon": lon, "lat": lat}
        if rec["fclass"] in OSM_PLACE_CLASSES and LATIN_NAME.fullmatch(name):
            by_key[normalize_name(name)].append(entry)
        elif rec["fclass"] in OSM_DEVANAGARI_CLASSES and DEVANAGARI_RE.search(name) and " " not in name.strip():
            key = loose_key_devanagari(name)
            if len(key) >= 3:
                by_loose[key].append({**entry, "phonetic": True})
    return by_key, by_loose


LAKE_WORDS = re.compile(r"\b(tal|taal|lake|daha|pokhari|tso|tsho|cho)\b", re.IGNORECASE)


def load_osm_lakes(osm_zip: Path) -> dict[str, list[dict[str, Any]]]:
    """OSM water polygons with a Latin-script name, keyed without 'Tal'/'Lake'."""
    import shapefile
    from shapely.geometry import shape

    reader = shapefile.Reader(f"{osm_zip}/gis_osm_water_a_free_1.shp")
    by_key: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for sr in reader.iterShapeRecords():
        rec = sr.record
        name = (rec["name"] or "").strip()
        if rec["fclass"] not in {"water", "reservoir"} or not LATIN_NAME.fullmatch(name):
            continue
        pt = shape(sr.shape.__geo_interface__).representative_point()
        by_key[normalize_name(LAKE_WORDS.sub(" ", name))].append(
            {"name": name, "fclass": f"water polygon ({rec['fclass']})", "osm_id": rec["osm_id"],
             "lon": pt.x, "lat": pt.y}
        )
    return by_key


def load_place_anchors() -> dict[str, list[dict[str, Any]]]:
    by_key: dict[str, list[dict[str, Any]]] = defaultdict(list)
    data = json.loads(PLACE_ANCHORS.read_text(encoding="utf-8"))
    for f in data["features"]:
        p = f["properties"]
        if "Nominatim" not in (p.get("basis") or ""):
            continue  # RPGCL-derived anchors are superseded by rpgcl_substation_nodes
        lon, lat = f["geometry"]["coordinates"]
        by_key[normalize_name(p.get("label") or p["id"])].append({
            "id": p["id"], "lon": lon, "lat": lat,
            "is_substation": bool(re.search(r"substation|सबस्टेशन", p.get("display_name") or "", re.IGNORECASE)),
        })
    return by_key


# ---------------------------------------------------------------------------
# Matching
# ---------------------------------------------------------------------------
def name_keys(name: str) -> list[str]:
    """Normalised keys for a registry name; 'A / B' yields both parts."""
    parts = [name] + [p for p in re.split(r"\s*/\s*", name) if p != name]
    keys = []
    for part in parts:
        key = normalize_name(part)
        if key and key not in keys:
            keys.append(key)
    return keys


def pick(
    candidates: list[dict[str, Any]],
    district: str,
    districts: DistrictIndex | None,
    allow_no_district: bool,
    border_tolerance_km: float = 0.0,
) -> tuple[dict[str, Any] | None, str]:
    """Pick one candidate consistent with the row's district.

    ``border_tolerance_km`` (used only for RPGCL substation symbols, whose stated precision is
    ~1 km) also accepts a candidate whose point lies in a neighbouring district but within that
    distance of the row's district polygon, i.e. a symbol drawn on the district border.
    """
    if not candidates:
        return None, "no candidate"
    if district:
        if districts is None:
            return None, "district check unavailable (OSM zip missing)"
        kept = []
        for c in candidates:
            got = c.get("district") or districts.lookup(c["lon"], c["lat"])
            if got == district or (
                border_tolerance_km > 0
                and districts.distance_km(c["lon"], c["lat"], district) <= border_tolerance_km
            ):
                kept.append(c)
        if len(kept) == 1:
            return kept[0], "ok"
        if not kept:
            return None, f"district mismatch ({len(candidates)} candidate(s))"
        # Several same-name points in one district: accept only if they coincide (< ~1.5 km).
        lat0, lon0 = kept[0]["lat"], kept[0]["lon"]
        if all(abs(c["lat"] - lat0) < 0.0135 and abs(c["lon"] - lon0) < 0.015 for c in kept):
            return kept[0], "ok (coincident duplicates)"
        return None, f"ambiguous ({len(kept)} candidates in district)"
    if not allow_no_district:
        return None, "row has no district"
    if len(candidates) == 1:
        return candidates[0], "ok (unique, no district on row)"
    return None, f"ambiguous ({len(candidates)} candidates, no district on row)"


def osm_pick(osm, names: list[str], district: str, districts) -> tuple[dict[str, Any] | None, str]:
    """Exact Latin-name match first; Devanagari phonetic match only if no exact candidate exists."""
    exact_idx, loose_idx = osm if osm else ({}, {})
    keys = [normalize_name(n) for n in names]
    cands = [p for k in keys for p in exact_idx.get(k, [])]
    chosen, reason = pick(cands, district, districts, allow_no_district=False)
    if chosen or reason.startswith("ambiguous"):
        return chosen, reason
    loose = [loose_key_latin(n) for n in names]
    cands = [p for k in loose if len(k) >= 3 for p in loose_idx.get(k, [])]
    chosen, reason = pick(cands, district, districts, allow_no_district=False)
    return chosen, (reason if not chosen else reason + " (phonetic)")


def osm_basis(chosen: dict[str, Any], query: str, district: str) -> str:
    how = ("Devanagari name, phonetic match" if chosen.get("phonetic") else "Latin name match")
    return (f"coordinates: OpenStreetMap {chosen['fclass']} '{chosen['name']}' ({how} for '{query}'; osm node "
            f"{chosen['osm_id']}, Geofabrik extract 2026-04-12) inside {district} district; place-level, "
            f"not the asset footprint")


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    # Preserve the file's existing line endings to keep diffs minimal.
    terminator = "\r\n" if path.exists() and b"\r\n" in path.read_bytes()[:4096] else "\n"
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator=terminator)
        writer.writeheader()
        writer.writerows(rows)


def append_note(row: dict[str, str], key: str, note: str) -> None:
    existing = (row.get(key) or "").strip()
    row[key] = f"{existing}; {note}" if existing else note


def rpgcl_basis(node: dict[str, Any]) -> str:
    return (
        f"coordinates: RPGCL official transmission network map {node['symbol_status']} S/S symbol labelled "
        f"'{node['label']}' ({node['map_frame']} map frame; data/processed/maps/rpgcl_substation_nodes.geojson "
        f"{node['node_id']}), symbol-level precision ~1 km; via {SCRIPT_TAG} {RUN_DATE}"
    )


def _km(a_lat: float, a_lon: float, b_lat: float, b_lon: float) -> float:
    return math.hypot((a_lat - b_lat) * 111.0, (a_lon - b_lon) * 111.0 * math.cos(math.radians(a_lat)))


LEGACY_RPGCL_TOLERANCE_KM = 3.0
RPGCL_BORDER_TOLERANCE_KM = 1.0  # = stated RPGCL symbol precision; see pick()


def geocode_substations(rows, nodes, anchors, osm_places, districts, report) -> int:
    """Fill blank substation coordinates; re-derive legacy RPGCL-node coordinates.

    Rows already tagged ``official-map-node`` came from place_anchor_index RPGCL anchors that were
    georeferenced with a lat/lon bilinear fit (~0.07-0.12 deg south bias). Rows with no symbol match
    take the anchor's current (corrected) value from place_anchor_index. When the same substation
    symbol is matched here and differs by more than LEGACY_RPGCL_TOLERANCE_KM, the coordinates are
    replaced and the previous value is recorded in notes.
    """
    nodes_by_key: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for n in nodes:
        nodes_by_key[n["name_key"]].append(n)
    used_points = {(r["latitude"].strip(), r["longitude"].strip()) for r in rows if (r.get("latitude") or "").strip()}
    used_nodes: set[str] = set()
    filled = 0
    rpgcl_anchors: dict[str, tuple[float, float]] = {}
    for f in json.loads(PLACE_ANCHORS.read_text(encoding="utf-8"))["features"]:
        if (f["properties"].get("basis") or "").startswith("RPGCL"):
            rpgcl_anchors[f["properties"]["id"]] = tuple(f["geometry"]["coordinates"])

    # Pass 1: legacy official-map-node rows.
    for row in rows:
        if (row.get("coordinate_precision") or "") != "official-map-node" or SCRIPT_TAG in (row.get("notes") or ""):
            continue
        district = canonical_district(row.get("district", ""))
        cands = [n for k in name_keys(row["substation_name"]) for n in nodes_by_key.get(k, [])]
        chosen, reason = pick(cands, district, districts, allow_no_district=True,
                              border_tolerance_km=RPGCL_BORDER_TOLERANCE_KM)
        if not chosen:
            # No symbol match: if the coordinates were copied from a place_anchor_index RPGCL anchor,
            # take that anchor's current value (re-derived with the corrected georeference).
            m = re.search(r"place_anchor_index\.geojson id '([^']+)' \(RPGCL official vector/map node\)",
                          row.get("notes") or "")
            anchor = rpgcl_anchors.get(m.group(1)) if m else None
            if anchor is None:
                report.append(("substation", row["slug"], row["highest_voltage_kv"], "LEGACY-KEPT", f"rpgcl: {reason}"))
                continue
            old_lat, old_lon = float(row["latitude"]), float(row["longitude"])
            dist = _km(old_lat, old_lon, anchor[1], anchor[0])
            if dist <= LEGACY_RPGCL_TOLERANCE_KM:
                report.append(("substation", row["slug"], row["highest_voltage_kv"], "LEGACY-OK", f"{dist:.1f} km"))
                continue
            used_points.discard((row["latitude"].strip(), row["longitude"].strip()))
            row["latitude"], row["longitude"] = round6(anchor[1]), round6(anchor[0])
            used_points.add((row["latitude"], row["longitude"]))
            append_note(row, "notes", (
                f"coordinates: place_anchor_index.geojson id '{m.group(1)}' re-derived with the corrected RPGCL "
                f"georeference (scripts/rpgcl_georef.py); replaces previous {old_lat}, {old_lon} ({dist:.1f} km off; "
                f"legacy lat/lon-bilinear RPGCL georeference bias); via {SCRIPT_TAG} {RUN_DATE}"))
            row["last_updated"] = RUN_DATE
            report.append(("substation", row["slug"], row["highest_voltage_kv"], "LEGACY-CORRECTED-ANCHOR", f"{dist:.1f} km"))
            continue
        used_nodes.add(chosen["node_id"])
        old_lat, old_lon = float(row["latitude"]), float(row["longitude"])
        dist = _km(old_lat, old_lon, chosen["lat"], chosen["lon"])
        if dist <= LEGACY_RPGCL_TOLERANCE_KM:
            report.append(("substation", row["slug"], row["highest_voltage_kv"], "LEGACY-OK", f"{dist:.1f} km"))
            continue
        used_points.discard((row["latitude"].strip(), row["longitude"].strip()))
        row["latitude"], row["longitude"] = round6(chosen["lat"]), round6(chosen["lon"])
        used_points.add((row["latitude"], row["longitude"]))
        append_note(row, "notes", rpgcl_basis(chosen) + (
            f"; replaces previous {old_lat}, {old_lon} ({dist:.1f} km off; legacy lat/lon-bilinear RPGCL "
            "georeference bias)"))
        row["last_updated"] = RUN_DATE
        report.append(("substation", row["slug"], row["highest_voltage_kv"], "LEGACY-CORRECTED", f"{dist:.1f} km"))

    # Pass 2: blank rows.
    for row in rows:
        if (row.get("latitude") or "").strip():
            continue
        district = canonical_district(row.get("district", ""))
        keys = name_keys(row["substation_name"])
        precision, basis = "", ""
        cands = [n for k in keys for n in nodes_by_key.get(k, []) if n["node_id"] not in used_nodes]
        chosen, reason = pick(cands, district, districts, allow_no_district=True,
                              border_tolerance_km=RPGCL_BORDER_TOLERANCE_KM)
        if chosen:
            precision, basis = "official-map-node", rpgcl_basis(chosen)
            used_nodes.add(chosen["node_id"])
        else:
            reasons = [f"rpgcl: {reason}"]
            # Place-level fallbacks need a district, must not reuse another row's point, and are
            # skipped when the substation is simply named after its district.
            named_after_district = normalize_name(row["substation_name"]) == normalize_name(district)
            if named_after_district:
                reasons.append("place fallback skipped: name equals district")
            else:
                cands = [a for k in keys for a in anchors.get(k, [])
                         if (round6(a["lat"]), round6(a["lon"])) not in used_points]
                chosen, reason = pick(cands, district, districts, allow_no_district=False)
                if chosen:
                    precision = "approximate-place"
                    basis = (f"coordinates: place_anchor_index.geojson id '{chosen['id']}' (Nominatim place-level "
                             f"match, not the substation footprint); via {SCRIPT_TAG} {RUN_DATE}")
                else:
                    reasons.append(f"anchor: {reason}")
                    parts = [p for p in re.split(r"\s*/\s*", row["substation_name"]) if p]
                    chosen, reason = osm_pick(osm_places, parts, district, districts)
                    if chosen and (round6(chosen["lat"]), round6(chosen["lon"])) in used_points:
                        chosen, reason = None, "point already used by another row"
                    if chosen:
                        precision = "approximate-place"
                        basis = osm_basis(chosen, row["substation_name"], district) + f"; via {SCRIPT_TAG} {RUN_DATE}"
                    else:
                        reasons.append(f"osm: {reason}")
            reason = "; ".join(reasons)
        if chosen:
            row["latitude"], row["longitude"] = round6(chosen["lat"]), round6(chosen["lon"])
            used_points.add((row["latitude"], row["longitude"]))
            row["coordinate_precision"] = precision
            append_note(row, "notes", basis)
            row["last_updated"] = RUN_DATE
            filled += 1
            report.append(("substation", row["slug"], row["highest_voltage_kv"], precision, basis.split(";")[0]))
        else:
            report.append(("substation", row["slug"], row["highest_voltage_kv"], "UNMATCHED", reason))
    return filled


# Explicit place queries for registries whose names are not bare place names.
# Value: (place name to look up, district constraint or '' to use the row's).
# Corridors spanning several towns, multi-district sites and unnamed sites are
# deliberately absent and stay blank.
INDUSTRIAL_PLACES = {
    "simara-sez": ("Simara", ""),
    "birgunj-industrial-area": ("Birgunj", ""),
    "bhumahi-bhairahawa-industrial-corridor": ("Bhumahi", ""),
    "nepalgunj-industrial-area": ("Nepalgunj", ""),
    "eastern-industrial-corridor-sunsari": ("Inaruwa", ""),
    "industrial-district-balaju": ("Balaju", ""),
    "industrial-district-patan": ("Lalitpur", ""),  # Patan = Lalitpur metropolitan city
    "industrial-district-hetauda": ("Hetauda", ""),
    "industrial-district-pokhara": ("Pokhara", ""),
    "industrial-district-butwal": ("Butwal", ""),
    "industrial-district-dharan": ("Dharan", ""),
    "industrial-district-nepalgunj": ("Nepalgunj", ""),
    "industrial-district-bhaktapur": ("Bhaktapur", ""),
    "industrial-district-birendranagar": ("Birendranagar", ""),
    "industrial-district-gajendranarayan": ("Rajbiraj", ""),
    "bhairahawa-sez": ("Siddharthanagar", ""),  # Bhairahawa = Siddharthanagar municipality
}

# NOC depots are tabulated by town; endpoints of the pipeline by town too.
FOSSIL_PLACES = {
    "noc-storage-amlekhgunj": ("Amlekhgunj", "Bara"),
    "noc-storage-bhadrapur": ("Bhadrapur", "Jhapa"),
    "noc-storage-bhairahawa": ("Siddharthanagar", "Rupandehi"),  # Bhairahawa = Siddharthanagar
    "noc-storage-biratnagar": ("Biratnagar", "Morang"),
    "noc-storage-dhangadi": ("Dhangadhi", "Kailali"),
    "noc-storage-dipayal": ("Dipayal", "Doti"),
    "noc-storage-janakpur": ("Janakpur", "Dhanusha"),
    "noc-storage-kathmandu": ("Kathmandu", "Kathmandu"),
    "noc-storage-manthali": ("Manthali", "Ramechhap"),
    "noc-storage-nepalgunj": ("Nepalgunj", "Banke"),
    "noc-storage-pokhara": ("Pokhara", "Kaski"),
    "noc-storage-simara": ("Simara", "Bara"),
    "noc-storage-surkhet": ("Birendranagar", "Surkhet"),
    # Nepal-side terminal of the Motihari-Amlekhgunj line is the Amlekhgunj depot.
    "pipeline-motihari-amlekhgunj": ("Amlekhgunj", "Bara"),
}

# Only sites the source names as a single place. The Karnali PV+BESS rows name a
# district only, Hulingtar-Dumkim spans two districts and Begnas-Rupa two lakes,
# so they stay blank. 'lake:' looks the name up in OSM water polygons.
STORAGE_PLACES = {
    "syarpu-lake-psh": ("lake:Syarpu", "Rukum West"),
    "kulekhani-sisneri-psh": ("Lambagar", "Makwanpur"),
}


def geocode_named_places(
    rows: list[dict[str, str]],
    id_key: str,
    places_map: dict[str, tuple[str, str]],
    anchors, osm_places, districts, report, label: str, note_key: str | None,
    osm_lakes: dict[str, list[dict[str, Any]]] | None = None,
) -> int:
    osm_lakes = osm_lakes or {}
    filled = 0
    for row in rows:
        rid = row[id_key]
        if (row.get("latitude") or "").strip():
            continue
        if rid not in places_map:
            report.append((label, rid, "", "UNMATCHED", "no single named place (corridor, multi-district or unnamed site)"))
            continue
        place, district = places_map[rid]
        district = canonical_district(district or row.get("district", ""))
        if place.startswith("lake:"):
            place = place[5:]
            chosen, reason = pick(osm_lakes.get(normalize_name(place), []), district, districts, False)
            src = "osm"
        else:
            key = normalize_name(place)
            # Anchors that Nominatim resolved to a substation are not the town/asset itself.
            town_anchors = [a for a in anchors.get(key, []) if not a["is_substation"]]
            chosen, reason = pick(town_anchors, district, districts, allow_no_district=False)
            src = "anchor"
            if not chosen:
                chosen, reason = osm_pick(osm_places, [place], district, districts)
                src = "osm"
        if not chosen:
            report.append((label, rid, "", "UNMATCHED", f"{place}: {reason}"))
            continue
        if src == "anchor":
            basis = (f"coordinates: place_anchor_index.geojson id '{chosen['id']}' (Nominatim place-level match "
                     f"for '{place}'), not the asset footprint")
        else:
            basis = osm_basis(chosen, place, district)
        basis += f"; via {SCRIPT_TAG} {RUN_DATE}"
        row["latitude"], row["longitude"] = round6(chosen["lat"]), round6(chosen["lon"])
        row["coordinate_precision"] = "approximate-place"
        if note_key:
            append_note(row, note_key, basis)
        filled += 1
        report.append((label, rid, "", "approximate-place", basis.split(";")[0]))
    return filled


def ensure_coord_columns(fieldnames: list[str], anchor_col: str | None) -> list[str]:
    if all(c in fieldnames for c in COORD_COLUMNS):
        return fieldnames
    out = [c for c in fieldnames if c not in COORD_COLUMNS]
    pos = out.index(anchor_col) + 1 if anchor_col and anchor_col in out else len(out)
    return out[:pos] + COORD_COLUMNS + out[pos:]


def coverage_by_voltage(rows: Iterable[dict[str, str]]) -> dict[str, tuple[int, int]]:
    total, have = Counter(), Counter()
    for r in rows:
        kv = r["highest_voltage_kv"]
        total[kv] += 1
        if (r.get("latitude") or "").strip():
            have[kv] += 1
    return {kv: (have[kv], total[kv]) for kv in sorted(total, key=int, reverse=True)}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--write", action="store_true", help="write updated CSVs (default: dry run)")
    parser.add_argument("--refresh-rpgcl-nodes", action="store_true",
                        help="re-extract and write rpgcl_substation_nodes.geojson from the RPGCL GeoPDF")
    parser.add_argument("--rpgcl-pdf", type=Path, default=RPGCL_PDF)
    parser.add_argument("--osm-zip", type=Path, default=OSM_ZIP)
    parser.add_argument("--verbose", action="store_true", help="print every row decision")
    args = parser.parse_args(argv)

    districts = DistrictIndex(args.osm_zip) if args.osm_zip.exists() else None
    if districts is None:
        print(f"warning: {args.osm_zip} missing; district checks and OSM place matches disabled", file=sys.stderr)

    if args.refresh_rpgcl_nodes:
        if not args.rpgcl_pdf.exists():
            raise SystemExit(f"RPGCL PDF not found: {args.rpgcl_pdf}")
        extracted = extract_rpgcl_substation_nodes(args.rpgcl_pdf)
        write_rpgcl_nodes(extracted, districts)
        print(f"wrote {RPGCL_NODES.relative_to(ROOT)} ({len(extracted)} nodes)")
    nodes = load_rpgcl_nodes()
    anchors = load_place_anchors()
    osm_places = load_osm_places(args.osm_zip) if args.osm_zip.exists() else None
    report: list[tuple[str, str, str, str, str]] = []

    sub_fields, sub_rows = read_csv(SUBSTATIONS_CSV)
    before = coverage_by_voltage(sub_rows)
    n_sub = geocode_substations(sub_rows, nodes, anchors, osm_places, districts, report)
    after = coverage_by_voltage(sub_rows)

    ind_fields, ind_rows = read_csv(INDUSTRIAL_CSV)
    ind_fields = ensure_coord_columns(ind_fields, "province")
    n_ind = geocode_named_places(ind_rows, "anchor_id", INDUSTRIAL_PLACES, anchors, osm_places, districts,
                                 report, "industrial", "reliability_or_feeder_notes")

    fos_fields, fos_rows = read_csv(FOSSIL_CSV)
    fos_fields = ensure_coord_columns(fos_fields, "location")
    n_fos = geocode_named_places(fos_rows, "asset_id", FOSSIL_PLACES, anchors, osm_places, districts,
                                 report, "fossil", "notes")

    sto_fields, sto_rows = read_csv(STORAGE_CSV)
    sto_fields = ensure_coord_columns(sto_fields, "province")
    n_sto = geocode_named_places(sto_rows, "slug", STORAGE_PLACES, anchors, osm_places, districts,
                                 report, "storage", "notes",
                                 osm_lakes=load_osm_lakes(args.osm_zip) if args.osm_zip.exists() else {})

    for entry in report:
        if args.verbose or entry[3] not in {"UNMATCHED", "LEGACY-OK"}:
            print(" | ".join(entry))
    print("\nsubstation coverage by highest_voltage_kv (geocoded/total):")
    for kv, (have, total) in after.items():
        print(f"  {kv:>3} kV: {before[kv][0]:>3} -> {have:>3} / {total}")
    total_have = sum(h for h, _ in after.values())
    total_rows = sum(t for _, t in after.values())
    print(f"  all   : {sum(h for h, _ in before.values())} -> {total_have} / {total_rows}  (+{n_sub})")
    print(f"industrial_load_anchors: +{n_ind} -> {sum(1 for r in ind_rows if r.get('latitude'))}/{len(ind_rows)}")
    print(f"fossil_infrastructure:   +{n_fos} -> {sum(1 for r in fos_rows if r.get('latitude'))}/{len(fos_rows)}")
    print(f"storage_non_dam_specs:   +{n_sto} -> {sum(1 for r in sto_rows if r.get('latitude'))}/{len(sto_rows)}")

    if args.write:
        write_csv(SUBSTATIONS_CSV, sub_fields, sub_rows)
        write_csv(INDUSTRIAL_CSV, ind_fields, ind_rows)
        write_csv(FOSSIL_CSV, fos_fields, fos_rows)
        write_csv(STORAGE_CSV, sto_fields, sto_rows)
        print("CSV files updated.")
    else:
        print("dry run: no files written (pass --write)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
