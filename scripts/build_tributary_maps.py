from __future__ import annotations

import csv
import html
import json
import math
import re
import time
import zipfile
from pathlib import Path
from typing import Any

import folium
import requests
import shapefile
from folium import plugins
from shapely.geometry import LineString, MultiLineString, Point, box, shape
from shapely.geometry.base import BaseGeometry
from shapely.ops import unary_union


ROOT = Path("/Users/hi/projects/nepalEnergy")
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed" / "maps"
DOCS = ROOT / "docs" / "maps"
TRACED_SEGMENTS_PATH = PROCESSED / "transmission_corridor_traced_segments.geojson"
TRACED_NETWORK_PATH = PROCESSED / "transmission_corridor_traced_network.geojson"
CROSS_BORDER_LINES_PATH = PROCESSED / "cross_border_interconnection_lines.geojson"
TRACE_GAP_PATH = PROCESSED / "transmission_trace_gap_report.geojson"
CLIP_BOUNDS = (78.0, 24.0, 89.5, 31.5)
CLIP_BOX = box(*CLIP_BOUNDS)
GEOPOLITICS_BOUNDS = (77.0, 22.0, 90.5, 31.8)
GEOPOLITICS_BOX = box(*GEOPOLITICS_BOUNDS)
NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
USER_AGENT = "Codex NepalEnergy mapping task"
HYDROBASINS_LEVEL6_URL = "https://data.hydrosheds.org/file/HydroBASINS/standard/hybas_as_lev06_v1c.zip"
HYDROBASINS_DIR = RAW / "maps" / "hydrobasins" / "hybas_as_lev06_v1c"
HYDROBASINS_SHP = HYDROBASINS_DIR / "hybas_as_lev06_v1c.shp"
HYDRORIVERS_URL = "https://data.hydrosheds.org/file/HydroRIVERS/HydroRIVERS_v10_as_shp.zip"
HYDRORIVERS_ROOT = RAW / "maps" / "hydrorivers"
HYDRORIVERS_ZIP = HYDRORIVERS_ROOT / "HydroRIVERS_v10_as_shp.zip"
HYDRORIVERS_DIR = HYDRORIVERS_ROOT / "HydroRIVERS_v10_as_shp"
HYDRORIVERS_SHP = HYDRORIVERS_DIR / "HydroRIVERS_v10_as.shp"
HYDRORIVERS_LOAD_BOUNDS = (77.0, 24.0, 90.5, 32.0)
HYDRORIVERS_LOAD_BOX = box(*HYDRORIVERS_LOAD_BOUNDS)
RIVER_REVIEW_OVERRIDES_PATH = RAW / "maps" / "river_network_review_overrides.json"
RIVER_NETWORK_QA_REPORT_PATH = PROCESSED / "river_network_qa_report.json"
RIVER_REVIEW_PREVIEW_DIR = ROOT / "tmp" / "river_review"
RIVER_REVIEW_PREVIEW_INDEX = RIVER_REVIEW_PREVIEW_DIR / "review_index.json"
RIVER_GEOMETRY_SOURCE = "HydroRIVERS v10 Asia"
RIVER_REFERENCE_BUFFER_DEG = 0.08
RIVER_ROUTE_EXIT_MISSES = 4
RIVER_ENDPOINT_SNAP_DEG = 0.12
RIVER_PARENT_JOIN_DEG = 0.05
RIVER_PROJECT_SANITY_DEG = 0.15
RIVER_LINE_JOIN_TOLERANCE_DEG = 0.0025
MAP_ZOOM = 7
LABEL_SAMPLE_FRACTIONS = [0.30, 0.40, 0.50, 0.60, 0.70]
LABEL_OFFSETS = [(0, -12), (0, 12), (12, -10), (-12, -10), (16, 0), (-16, 0), (18, 8), (-18, 8)]
MAJOR_LABEL_IDS = {
    "koshi_main",
    "arun",
    "tamor",
    "sunkoshi",
    "narayani",
    "kaligandaki",
    "marsyangdi",
    "budhigandaki",
    "trishuli",
    "karnali",
    "bheri",
    "mahakali",
}
MANUAL_LABEL_OFFSETS = {
    "sunkoshi": (16, -10),
    "dudhkoshi": (18, 10),
    "tamakoshi": (18, -8),
    "bhotekoshi": (12, -16),
    "indrawati": (14, 10),
    "likhu": (16, 16),
    "balephi": (20, 0),
    "kaligandaki": (-16, -10),
    "marsyangdi": (12, -8),
    "budhigandaki": (16, 14),
    "trishuli": (-14, -10),
}

BASIN_COLORS = {
    "Koshi": "#1d70a2",
    "Gandaki": "#2f8f6b",
    "Karnali": "#c4691f",
    "Mahakali": "#9b2d30",
    "Medium basins": "#6d4ea5",
}

LICENSE_COLORS = {
    "Operation": "#0f766e",
    "Generation": "#d97706",
    "Survey": "#2563eb",
}

PROJECT_PRECISION_STYLES = {
    "site": {"fill_opacity": 0.82, "weight": 1.2, "radius_scale": 1.0},
    "river_reference": {"fill_opacity": 0.42, "weight": 1.6, "radius_scale": 0.95},
    "raw_reference": {"fill_opacity": 0.14, "weight": 1.4, "radius_scale": 0.9},
}

PROJECT_PRECISION_LABELS = {
    "site": "Higher-confidence site point",
    "river_reference": "River-aligned project reference",
    "raw_reference": "Low-confidence registry reference",
}

PROJECT_RIVER_SNAP_THRESHOLDS_DEG = {
    "Generation": 0.02,
    "Survey": 0.03,
}

PROJECT_RIVER_CONTEXT_THRESHOLD_DEG = 0.02
PROJECT_RIVER_SEARCH_DEG = 0.08
PROJECT_SNAP_MIN_SHIFT_DEG = 0.0005
PROJECT_OFFSET_LINE_MIN_M = 120.0

PROJECT_WATERWAY_NAME_ALIASES = {
    "arun": ["अरुण नदी", "Arun River", "Arun Khola"],
    "karnali": ["कर्णाली", "Karnali"],
}

ANNOTATION_OFFSETS = [
    (8, -10),
    (10, 8),
    (-12, -10),
    (14, 0),
    (-14, 8),
    (16, -14),
]

BASIN_SEASONALITY_RIVER_IDS = {
    "Mahakali": "mahakali",
    "Karnali": "karnali",
    "Gandaki": "narayani",
    "Koshi": "koshi_main",
    "Babai": "babai",
    "Kamala": "kamala",
    "Kankai": "kankai",
    "Bagmati": "bagmati",
}

MANUAL_POINT_ANCHORS = {
    "West Rapti": {
        "lat": 27.8389630,
        "lon": 82.4895166,
        "basis": "Named West Rapti / Rapti River anchor from Nominatim near Dang",
    },
    "Kokhajor-1": {
        "lat": 27.3446438,
        "lon": 85.5783271,
        "basis": "Kokhajor Khola river anchor from Nominatim",
    },
}

STORAGE_SHORTLIST_ANCHORS = {
    "Kulekhani I-III": {"project_prefix": "Kulekhani", "confidence": "cluster_centroid"},
    "Tanahu": {"project_name": "Tanahu HEP", "confidence": "exact_project_point"},
    "Dudhkoshi Storage": {"river_id": "dudhkoshi", "confidence": "river_anchor"},
    "Nalsyau Gad": {"project_name": "Nalsyau Gad Storage HEP", "confidence": "exact_project_point"},
    "Lower Badigad": {"project_name": "Badigad Khola HPP", "confidence": "project_point_as_river_anchor"},
    "Naumure (W. Rapti)": {"point_name": "West Rapti", "confidence": "basin_anchor"},
    "Sun Koshi No.3": {"river_id": "sunkoshi", "confidence": "river_anchor"},
    "Madi": {"river_id": "madi", "confidence": "river_anchor"},
    "Andhi Khola": {"project_name": "Andhi Khola", "confidence": "project_point_as_river_anchor"},
    "Kokhajor-1": {"point_name": "Kokhajor-1", "confidence": "river_anchor"},
    "Lower Jhimruk": {"project_name": "Jhimruk Khola", "confidence": "project_point_as_river_anchor"},
}

TOP_PROJECT_LIMIT = 10

PRIORITY_PROJECT_GROUP_STYLES = {
    "priority_operating": {"color": "#14532d", "label": "Priority operating / buildout"},
    "radar_survey": {"color": "#9a3412", "label": "Radar survey"},
}

PRIORITY_PROJECTS = [
    {
        "id": "upper_bhotekoshi_priority",
        "project_name": "Upper Bhotekoshi",
        "group": "priority_operating",
        "label_title": "Upper Bhotekoshi",
        "label_subtitle": "45 MW · operating",
        "priority_read": "Existing Bhote Koshi valley plant; useful as a reality-check site where imagery and river geometry are both legible.",
        "source_note": "Naxa / DoED-linked public hydropower project dataset",
    },
    {
        "id": "kali_gandaki_a_priority",
        "project_name": "Kali Gandaki A",
        "group": "priority_operating",
        "label_title": "Kali Gandaki A",
        "label_subtitle": "144 MW · operating",
        "priority_read": "One of Nepal's most important operating anchor plants and a good benchmark for marker honesty in the Gandaki corridor.",
        "source_note": "Naxa / DoED-linked public hydropower project dataset",
    },
    {
        "id": "andhi_khola_priority",
        "project_name": "Andhi Khola",
        "group": "priority_operating",
        "label_title": "Andhi Khola",
        "label_subtitle": "9 MW · operating",
        "priority_read": "Small plant, but the site is visible and it already anchors one of the promising-storage comparisons in the current narrative.",
        "source_note": "Naxa / DoED-linked public hydropower project dataset",
    },
    {
        "id": "upper_tamakoshi_priority",
        "project_name": "Upper Tamakoshi HPP",
        "group": "priority_operating",
        "label_title": "Upper Tamakoshi",
        "label_subtitle": "456 MW · buildout",
        "priority_read": "The largest commissioned domestic project in the current stack; deserves a dedicated watch-layer marker instead of only appearing in the top-MW list.",
        "source_note": "Naxa / DoED-linked public hydropower project dataset",
    },
    {
        "id": "tanahu_priority",
        "project_name": "Tanahu HEP",
        "storage_annotation_name": "Tanahu",
        "group": "priority_operating",
        "label_title": "Tanahu",
        "label_subtitle": "140 MW · storage build",
        "priority_read": "Most practical near-term storage addition in the checked official set; this stays on the watch layer even when the broader project cloud is off.",
        "source_note": "NEA annual report FY 2024/25 and current project registry",
    },
    {
        "id": "upper_trishuli_priority",
        "project_name": "Upper Trishuli-1",
        "group": "priority_operating",
        "label_title": "Upper Trishuli-1",
        "label_subtitle": "216 MW · buildout",
        "priority_read": "High-value central-north project tied to the Trishuli evacuation corridor; worth keeping visible in the grid-first map.",
        "source_note": "Naxa / DoED-linked public hydropower project dataset",
    },
    {
        "id": "nalsyau_gad_radar",
        "project_name": "Nalsyau Gad Storage HEP",
        "storage_annotation_name": "Nalsyau Gad",
        "group": "radar_survey",
        "label_title": "Nalsyau Gad",
        "label_subtitle": "410 MW · radar survey",
        "priority_read": "Best dry-energy performer in the JICA promising-storage set, so it belongs on the survey radar even before a full site-grade document pass.",
        "source_note": "JICA/NEA storage master plan volume 2 plus current project registry",
    },
    {
        "id": "mugu_karnali_storage_radar",
        "project_name": "Mugu Karnali Storage HEP",
        "group": "radar_survey",
        "label_title": "Mugu Karnali Storage",
        "label_subtitle": "1,902 MW · radar survey",
        "priority_read": "Largest survey-stage project in the registry; strategically important enough to stay visible despite lower locational confidence.",
        "source_note": "VUCL MKHEP project page and current project registry",
    },
    {
        "id": "arun3_radar",
        "project_name": "Arun 3",
        "group": "radar_survey",
        "label_title": "Arun 3",
        "label_subtitle": "900 MW · radar survey",
        "priority_read": "National-scale eastern corridor project; included as an on-radar survey reference even though the registry point is still approximate.",
        "source_note": "SAPDC resettlement plan and current project registry",
    },
    {
        "id": "upper_karnali_radar",
        "project_name": "Upper Karnali",
        "group": "radar_survey",
        "label_title": "Upper Karnali",
        "label_subtitle": "900 MW · radar survey",
        "priority_read": "Too strategically important to bury inside the general survey cloud, even though the current public coordinate remains low-confidence.",
        "source_note": "IBN Energy Sector Profile, DoED survey-license extent, and current project registry",
    },
    {
        "id": "betan_karnali_radar",
        "project_name": "Betan Karnali HP",
        "group": "radar_survey",
        "label_title": "Betan Karnali",
        "label_subtitle": "688 MW · radar survey",
        "priority_read": "Large Karnali-basin survey project that matters for the storage-and-seasonality story; kept visible as a radar candidate.",
        "source_note": "BKSHCL EOI document and current project registry",
    },
    {
        "id": "phukot_karnali_radar",
        "project_name": "Phukot Karnali",
        "group": "radar_survey",
        "label_title": "Phukot Karnali",
        "label_subtitle": "426 MW · radar survey",
        "priority_read": "Another major Karnali-basin survey project worth tracking explicitly while the map still distinguishes approximate survey references from site points.",
        "source_note": "VUCL PKHEP status report and current project registry",
    },
]

PRIORITY_PROJECT_ANCHOR_OVERRIDES = {
    "Arun 3": {
        "lat": 27.5651158,
        "lon": 87.2747066,
        "basis": "Document-backed Arun dam-site vicinity near Num, snapped to the named Arun reach",
    },
    "Betan Karnali HP": {
        "lat": 28.914973,
        "lon": 81.2475872,
        "basis": "Document-backed powerhouse-village vicinity at Tatalighat, snapped to the named Karnali reach",
    },
    "Upper Karnali": {
        "lat": 28.9005555556,
        "lon": 81.4444444444,
        "basis": "Document-backed powerhouse vicinity near Tallo Balde Khola from the IBN Energy Sector Profile",
    },
}

PROJECT_DISPLAY_OVERRIDES = {
    "Upper Karnali": {
        "lat": 28.9005555556,
        "lon": 81.4444444444,
        "precision_tier": "river_reference",
        "location_basis": "Document-backed powerhouse vicinity from the IBN Energy Sector Profile, within the official DoED survey-license envelope",
        "map_match_basis": "IBN Energy Sector Profile and DoED survey-license extent",
    },
    "Phukot Karnali": {
        "location_basis": "Official project-area center from the VUCL PKHEP status report, already close to the mapped Karnali reach",
        "map_match_basis": "VUCL PKHEP status report",
    },
    "Mugu Karnali Storage HEP": {
        "location_basis": "Official project-area center from the VUCL MKHEP project page, snapped to the mapped Karnali reach",
        "map_match_basis": "VUCL MKHEP project page",
    },
}

GRID_STATUS_STYLES = {
    "Operational": {"color": "#166534", "dash_array": None},
    "Partially operational": {"color": "#a16207", "dash_array": "8 6"},
    "Under construction": {"color": "#c2410c", "dash_array": "10 6"},
    "Implementation setup": {"color": "#1d4ed8", "dash_array": "8 8"},
    "Planned": {"color": "#7c3aed", "dash_array": "4 10"},
}

TRANSMISSION_LINE_STYLES = {
    "Operational": {"color": "#2f343b", "weight": 2.2, "opacity": 0.52, "dash_array": "12 7"},
    "Partially operational": {"color": "#3f3f46", "weight": 2.25, "opacity": 0.58, "dash_array": "8 6"},
    "Under construction": {"color": "#3f3f46", "weight": 2.3, "opacity": 0.6, "dash_array": "6 8"},
    "Implementation setup": {"color": "#52525b", "weight": 2.2, "opacity": 0.56, "dash_array": "3 8"},
    "Planned": {"color": "#71717a", "weight": 2.0, "opacity": 0.42, "dash_array": "2 10"},
}

TRANSMISSION_LABEL_ACCENT = "#374151"
TRANSMISSION_NODE_COLORS = {
    "hub": "#111827",
    "gateway": "#9a3412",
}

PLACE_ANCHORS = {
    "hetauda": {"label": "Hetauda", "queries": ["Hetauda Substation, Nepal", "Hetauda Nepal"]},
    "dhalkebar": {"label": "Dhalkebar", "queries": ["Dhalkebar Nepal"]},
    "inaruwa": {"label": "Inaruwa", "queries": ["Inaruwa Substation, Nepal", "Inaruwa Nepal"]},
    "bharatpur": {"label": "Bharatpur", "queries": ["Bharatpur Nepal"]},
    "bardaghat": {"label": "Bardaghat", "queries": ["Bardaghat Nepal"]},
    "khimti": {"label": "Khimti", "queries": ["Khimti Nepal"]},
    "tingla": {"label": "Tingla", "queries": ["Tingla Nepal"]},
    "mirchaiya": {"label": "Mirchaiya", "queries": ["Mirchaiya Nepal"]},
    "dana": {
        "label": "Dana substation",
        "lat": 28.42186786278833,
        "lon": 83.6520159781521,
        "basis": "RPGCL 2021 official-vector Dana-Kushma 220 kV terminal; NEA FY2019/20 and FY2024/25 source control.",
        "queries": ["Dana Myagdi Nepal"],
    },
    "kushma": {
        "label": "Kushma substation",
        "lat": 28.1280642459853,
        "lon": 83.65060885791756,
        "basis": "RPGCL 2021 official-vector Dana-Kushma/Kushma-New Butwal 220 kV junction; NEA FY2019/20 and FY2024/25 source control.",
        "queries": ["Kushma Nepal"],
    },
    "butwal": {
        "label": "New Butwal substation",
        "lat": 27.460784986382116,
        "lon": 83.69052298786728,
        "basis": "RPGCL 2021 official-vector Kushma-New Butwal 220 kV terminal; NEA FY2024/25 identifies New Butwal at Sunwal-13, Nawalparasi.",
        "queries": ["Butwal Nepal"],
    },
    "butwal_132": {
        "label": "Butwal 132 kV hub",
        "lat": 27.556542431092055,
        "lon": 83.47321851682389,
        "basis": "RPGCL 2021 map label on the existing western 132 kV backbone; NEA FY2024/25 existing-line inventory names Butwal-Shivapur-Lamahi-Kohalpur.",
        "queries": ["Butwal Nepal"],
    },
    "shivapur": {
        "label": "Shivapur",
        "lat": 27.514,
        "lon": 82.8646,
        "basis": "RPGCL 2021 map label on the Butwal-Shivapur-Lamahi-Kohalpur 132 kV backbone.",
        "queries": ["Shivapur Nepal"],
    },
    "lamahi": {
        "label": "Lamahi",
        "lat": 27.7536,
        "lon": 82.5599,
        "basis": "RPGCL 2021 map label on the Butwal-Shivapur-Lamahi-Kohalpur 132 kV backbone.",
        "queries": ["Lamahi Nepal"],
    },
    "kohalpur": {
        "label": "Kohalpur",
        "lat": 28.0743,
        "lon": 81.6741,
        "basis": "RPGCL 2021 map label; NEA FY2024/25 identifies Kohalpur as a grid branch office and western 132 kV hub.",
        "queries": ["Kohalpur Nepal"],
    },
    "bhurigaun": {
        "label": "Bhurigaun",
        "lat": 28.388423153007594,
        "lon": 81.318370969382,
        "basis": "RPGCL 2021 official-vector junction on the Kohalpur-Bhurigaun-Lamki 132 kV line; NEA FY2024/25 existing-line inventory names Kohalpur-Bhurigaun-Lumki.",
        "queries": ["Bhurigaun Nepal"],
    },
    "ratmate": {"label": "Ratmate", "queries": ["Ratmate Nuwakot Nepal"]},
    "lapsiphedi": {"label": "Lapsiphedi", "queries": ["Lapsiphedi Nepal"]},
    "damauli": {"label": "Damauli", "queries": ["Damauli Nepal"]},
    "udipur": {"label": "Udipur", "queries": ["Udipur Lamjung Nepal"]},
    "muzaffarpur": {"label": "Muzaffarpur", "queries": ["Muzaffarpur Bihar India"]},
    "kushaha": {"label": "Kushaha", "queries": ["Kushaha Nepal"]},
    "parwanipur": {"label": "Parwanipur", "queries": ["Parwanipur Nepal"]},
    "mainahiya": {"label": "Mainahiya", "queries": ["Mainahiya Rupandehi Nepal", "Mainahiya Nepal"]},
    "gaddachauki": {"label": "Gaddachauki", "queries": ["Gaddachauki Nepal"]},
    "jamunaha": {"label": "Jamunaha", "queries": ["Jamunaha Nepal"]},
    "belahiya": {"label": "Belahiya", "queries": ["Belahiya Nepal"]},
    "lamki": {
        "label": "Lamki / Dododhara",
        "lat": 28.54114421639382,
        "lon": 81.15880776919326,
        "basis": "RPGCL 2021 official-vector junction for the western 132 kV backbone and Lamki/Dododhara export planning area.",
        "queries": ["Lamki Nepal", "Dododhara Nepal"],
    },
    "pahalwanpur": {
        "label": "Pahalwanpur",
        "lat": 28.6145,
        "lon": 80.8777,
        "basis": "RPGCL 2021 map label on the Lamki-Pahalwanpur-Attariya-Mahendranagar 132 kV line.",
        "queries": ["Pahalwanpur Nepal"],
    },
    "attariya": {
        "label": "Attariya",
        "lat": 28.735364655748388,
        "lon": 80.55398409703626,
        "basis": "RPGCL 2021 official-vector junction for the western 132 kV backbone and Chameliya-Syaule-Attariya line.",
        "queries": ["Attariya Nepal"],
    },
    "purnea": {"label": "Purnea", "queries": ["Purnea Bihar India"]},
    "bareilly": {"label": "Bareilly", "queries": ["Bareilly India", "Bareli India"]},
    "chameliya": {
        "label": "Chameliya",
        "lat": 29.613418786265093,
        "lon": 80.64439891503855,
        "basis": "RPGCL 2021 official-vector northern terminal of the Chameliya-Syaule-Attariya 132 kV line.",
        "queries": ["Chameliya Nepal"],
    },
    "syaule": {
        "label": "Syaule",
        "lat": 29.2367,
        "lon": 80.662,
        "basis": "RPGCL 2021 map label on the Chameliya-Syaule-Attariya 132 kV line.",
        "queries": ["Syaule Darchula Nepal"],
    },
    "jauljibi": {"label": "Jauljibi", "queries": ["Jauljibi India"]},
    "mahendranagar": {
        "label": "Mahendranagar",
        "lat": 28.946220417499394,
        "lon": 80.09452366380923,
        "basis": "RPGCL 2021 official-vector western terminal of the Lamki-Pahalwanpur-Attariya-Mahendranagar 132 kV line.",
        "queries": ["Mahendranagar Kanchanpur Nepal", "Bhimdatta Nepal"],
    },
    "surkhet": {
        "label": "Surkhet",
        "lat": 28.4516,
        "lon": 81.652,
        "basis": "RPGCL 2021 map label and NEA FY2024/25 Kohalpur-Surkhet-Dailekh 132 kV project narrative.",
        "queries": ["Surkhet Nepal"],
    },
    "dailekh": {
        "label": "Dailekh",
        "lat": 28.74,
        "lon": 81.71,
        "basis": "RPGCL 2021 map label and NEA FY2024/25 Kohalpur-Surkhet-Dailekh 132 kV project narrative.",
        "queries": ["Dailekh Nepal"],
    },
    "nautanwa": {"label": "New Nautanwa / Sunauli", "queries": ["Sunauli India"]},
}

TRANSMISSION_CORRIDORS = [
    {
        "id": "hddi_400",
        "name": "Hetauda-Dhalkebar-Inaruwa 400 kV backbone",
        "short_label": "Hetauda-Dhalkebar-Inaruwa 400 kV",
        "status": "Partially operational",
        "category": "Domestic backbone",
        "voltage_kv": "400",
        "anchor_ids": ["hetauda", "dhalkebar", "inaruwa"],
        "components": ["Hetauda-Dhalkebar", "Dhalkebar-Inaruwa"],
        "source_note": "NEA annual report FY 2024/25 line inventory and project status; World Bank HDDTL RAP route description and Figure 1.",
        "importance": "Core 400 kV east-west transfer spine and the backbone behind large-scale export readiness.",
        "geometry_basis": "Indicative substation spine using official line names and geocoded grid nodes.",
    },
    {
        "id": "hetauda_bharatpur_bardaghat_220",
        "name": "Hetauda-Bharatpur-Bardaghat 220 kV corridor",
        "short_label": "Hetauda-Bharatpur-Bardaghat 220 kV",
        "status": "Operational",
        "category": "Domestic backbone",
        "voltage_kv": "220",
        "anchor_ids": ["hetauda", "bharatpur", "bardaghat"],
        "components": ["New Bharatpur-New Hetauda", "Bharatpur-Bardaghat"],
        "source_note": "NEA annual report FY 2024/25 existing 220 kV line inventory.",
        "importance": "Main central-to-western transfer corridor tying Hetauda load and export centers to the west.",
        "geometry_basis": "Indicative substation spine using official line names and geocoded grid nodes.",
    },
    {
        "id": "khimti_dhalkebar_220",
        "name": "Khimti-Dhalkebar 220 kV hydro corridor",
        "short_label": "Khimti-Dhalkebar 220 kV",
        "status": "Operational",
        "category": "Hydro evacuation",
        "voltage_kv": "220",
        "anchor_ids": ["khimti", "dhalkebar"],
        "components": ["Khimti-Dhalkebar"],
        "source_note": "NEA annual report FY 2024/25 existing 220 kV line inventory.",
        "importance": "Eastern hill hydropower evacuation path into the Dhalkebar hub.",
        "geometry_basis": "Indicative substation spine using official line names and geocoded grid nodes.",
    },
    {
        "id": "solu_tingla_mirchaiya_132",
        "name": "Solu Corridor Tingla-Mirchaiya 132 kV",
        "short_label": "Solu Corridor 132 kV",
        "status": "Operational",
        "category": "Hydro evacuation",
        "voltage_kv": "132",
        "anchor_ids": ["tingla", "mirchaiya"],
        "components": ["Solu Corridor (Tingla-Mirchaiya)"],
        "source_note": "NEA Grid 2076 and NEA annual report FY 2024/25.",
        "importance": "Dedicated eastern evacuation corridor for Solu basin projects.",
        "geometry_basis": "Indicative spine between the named terminal substations in official NEA documents.",
    },
    {
        "id": "dana_kushma_butwal_220",
        "name": "Dana-Kushma-New Butwal 220 kV corridor",
        "short_label": "Dana-Kushma-New Butwal 220 kV",
        "status": "Operational",
        "category": "Hydro evacuation",
        "voltage_kv": "220",
        "anchor_ids": ["dana", "kushma", "butwal"],
        "components": ["Dana-Kushma", "Kushma-New Butwal"],
        "source_note": "NEA annual report FY 2024/25 existing 220 kV line inventory.",
        "importance": "Key Kali Gandaki / western Gandaki evacuation route into the Butwal node.",
        "geometry_basis": "Indicative substation spine using official line names and geocoded grid nodes.",
    },
    {
        "id": "udipur_damauli_bharatpur_220",
        "name": "Udipur-Damauli-Bharatpur 220 kV reinforcement",
        "short_label": "Udipur-Damauli-Bharatpur 220 kV",
        "status": "Under construction",
        "category": "Hydro evacuation",
        "voltage_kv": "220",
        "anchor_ids": ["udipur", "damauli", "bharatpur"],
        "components": ["Khudi-Udipur", "Udipur-Bharatpur"],
        "source_note": "NEA annual report FY 2024/25 under-construction tables and NEA tender/award references for the Marsyangdi corridor.",
        "importance": "Mid-western reinforcement for the Marsyangdi / Lamjung hydro cluster into the Bharatpur load-transfer zone.",
        "geometry_basis": "Indicative corridor spine based on named substations and reinforcement packages.",
    },
    {
        "id": "mca_central_400",
        "name": "Lapsiphedi-Ratmate-Hetauda-Damauli-Butwal 400 kV central corridor",
        "short_label": "MCA central 400 kV corridor",
        "status": "Under construction",
        "category": "Domestic backbone",
        "voltage_kv": "400",
        "anchor_ids": ["lapsiphedi", "ratmate", "hetauda", "damauli", "butwal"],
        "components": [
            "Lapsiphedi-Ratmate",
            "Ratmate-Hetauda",
            "Ratmate-Damauli",
            "Damauli-Butwal",
        ],
        "source_note": "MCA-Nepal alignment maps and ADB SASEC operational plan update; Ratmate is the current hub nomenclature.",
        "importance": "High-priority central 400 kV expansion meant to unlock new export and domestic transfer capacity.",
        "geometry_basis": "Indicative compact spine using MCA current segment names and geocoded hub nodes.",
    },
]

CROSS_BORDER_INTERCONNECTIONS = [
    {
        "id": "dhalkebar_muzaffarpur",
        "name": "Dhalkebar-Muzaffarpur",
        "short_label": "Dhalkebar-Muzaffarpur",
        "status": "Operational",
        "voltage_kv": "400",
        "location_anchor_id": "dhalkebar",
        "india_anchor_id": "muzaffarpur",
        "nepal_node": "Dhalkebar",
        "india_node": "Muzaffarpur",
        "location_basis": "Nepal-side interconnection node",
        "timeline_note": "Full-capacity charging on November 11, 2020; Dhalkebar substation operational from February 1, 2021.",
        "source_note": "Embassy of India commerce brief and April 2, 2026 PIB Lok Sabha reply; World Bank restructuring paper and DoED Nepal-segment registry.",
    },
    {
        "id": "kataiya_kushaha",
        "name": "Kataiya-Kushaha",
        "short_label": "Kataiya-Kushaha",
        "status": "Operational",
        "voltage_kv": "132",
        "location_anchor_id": "kushaha",
        "india_anchor_id": None,
        "nepal_node": "Kushaha",
        "india_node": "Kataiya",
        "location_basis": "Nepal-side interconnection node",
        "timeline_note": "Second circuit inaugurated on January 4, 2024; PIB now lists three circuits in service.",
        "source_note": "Embassy of India JSC release, April 2, 2026 PIB Lok Sabha reply, and DoED transmission-line registry.",
    },
    {
        "id": "raxaul_parwanipur",
        "name": "Raxaul-Parwanipur",
        "short_label": "Raxaul-Parwanipur",
        "status": "Operational",
        "voltage_kv": "132",
        "location_anchor_id": "parwanipur",
        "india_anchor_id": None,
        "nepal_node": "Parwanipur",
        "india_node": "Raxaul",
        "location_basis": "Nepal-side interconnection node",
        "timeline_note": "Second circuit inaugurated on January 4, 2024.",
        "source_note": "Embassy of India JSC release, April 2, 2026 PIB Lok Sabha reply, and DoED transmission-line registry.",
    },
    {
        "id": "nautanwa_mainahiya",
        "name": "New Nautanwa-Mainahiya",
        "short_label": "New Nautanwa-Mainahiya",
        "status": "Operational",
        "voltage_kv": "132",
        "location_anchor_id": "mainahiya",
        "india_anchor_id": "nautanwa",
        "nepal_node": "Mainahiya",
        "india_node": "New Nautanwa / Sunauli",
        "location_basis": "Nepal-side interconnection node",
        "timeline_note": "Inaugurated on January 4, 2024 as Nepal's first direct power connection to Uttar Pradesh.",
        "source_note": "Embassy of India JSC release and April 2, 2026 PIB Lok Sabha reply.",
    },
    {
        "id": "tanakpur_mahendranagar",
        "name": "Tanakpur-Mahendranagar",
        "short_label": "Tanakpur-Mahendranagar",
        "status": "Operational",
        "voltage_kv": "132",
        "location_anchor_id": "gaddachauki",
        "india_anchor_id": None,
        "nepal_node": "Mahendranagar / Gaddachauki",
        "india_node": "Tanakpur",
        "location_basis": "Border-gate node",
        "timeline_note": "Long-standing existing interconnection; still listed as operational in the April 2, 2026 Lok Sabha reply.",
        "source_note": "CEA Draft National Electricity Plan 2016 and April 2, 2026 PIB Lok Sabha reply.",
    },
    {
        "id": "nepalgunj_nanpara",
        "name": "Nepalgunj-Nanpara",
        "short_label": "Nepalgunj-Nanpara",
        "status": "Under construction",
        "voltage_kv": "132",
        "location_anchor_id": "jamunaha",
        "india_anchor_id": "nanpara",
        "nepal_node": "Nepalgunj / Jamunaha",
        "india_node": "Nanpara",
        "location_basis": "Border-gate node",
        "timeline_note": "Listed in NEA FY 2024/25 under-construction 132 kV transmission lines.",
        "source_note": "NEA annual report FY 2024/25 under-construction line tables.",
    },
    {
        "id": "gorakhpur_new_butwal",
        "name": "Gorakhpur-New Butwal",
        "short_label": "Gorakhpur-New Butwal",
        "status": "Under construction",
        "voltage_kv": "400",
        "location_anchor_id": "belahiya",
        "india_anchor_id": None,
        "nepal_node": "New Butwal / Belahiya border corridor",
        "india_node": "Gorakhpur",
        "location_basis": "Border-corridor node",
        "timeline_note": "Groundbreaking took place on June 2, 2023; MCC FY 2025 reports active contractor mobilization.",
        "source_note": "Embassy of India commerce brief, MCC compact / FY 2025 report, and MoEWRI IPSDP executive summary.",
    },
    {
        "id": "inaruwa_purnea",
        "name": "Inaruwa-Purnea",
        "short_label": "Inaruwa-Purnea",
        "status": "Implementation setup",
        "voltage_kv": "400",
        "location_anchor_id": "inaruwa",
        "india_anchor_id": "purnea",
        "nepal_node": "Inaruwa",
        "india_node": "New Purnea / Purnia",
        "location_basis": "Nepal-side interconnection node",
        "timeline_note": "JV and shareholders' agreements were signed on October 29, 2025 after the bilateral implementation MoU in April 2025.",
        "source_note": "PIB October 29, 2025 implementation note, Embassy of India commerce brief, and MoEWRI IPSDP executive summary.",
    },
    {
        "id": "lamki_bareilly",
        "name": "Lamki-Bareilly",
        "short_label": "Lamki-Bareilly",
        "status": "Implementation setup",
        "voltage_kv": "400",
        "location_anchor_id": "lamki",
        "india_anchor_id": "bareilly",
        "nepal_node": "Lamki / Dododhara",
        "india_node": "Bareilly",
        "location_basis": "Nepal-side interconnection node",
        "timeline_note": "JV and shareholders' agreements were signed on October 29, 2025 after the bilateral implementation MoU in April 2025.",
        "source_note": "PIB October 29, 2025 implementation note, Embassy of India commerce brief, and MoEWRI IPSDP executive summary.",
    },
    {
        "id": "chameliya_jauljibi",
        "name": "Chameliya-Jauljibi",
        "short_label": "Chameliya-Jauljibi",
        "status": "Planned",
        "voltage_kv": "220",
        "location_anchor_id": "chameliya",
        "india_anchor_id": "jauljibi",
        "nepal_node": "Chameliya",
        "india_node": "Jauljibi",
        "location_basis": "Nepal-side corridor node",
        "timeline_note": "Officially listed future cross-border corridor as of April 2, 2026.",
        "source_note": "April 2, 2026 PIB Lok Sabha reply and DoED Chameliya-Jauljibi cross-border registry.",
    },
]

COMPARISON_BASINS = [
    {
        "id": "yamuna_basin",
        "name": "Yamuna Basin",
        "river_id": "yamuna",
        "fraction": 0.65,
        "comparison_group": "India-origin comparison",
        "note": "Large northern Indian basin with major downstream relevance but no Nepal-origin control over its headwaters.",
    },
    {
        "id": "ramganga_basin",
        "name": "Ramganga Basin",
        "river_id": "ramganga",
        "fraction": 0.65,
        "comparison_group": "India-origin comparison",
        "note": "Useful Himalayan comparison basin on the Indian side, showing that not every mountain-fed Gangetic tributary runs through Nepal.",
    },
    {
        "id": "gomti_basin",
        "name": "Gomti Basin",
        "river_id": "gomti",
        "fraction": 0.65,
        "comparison_group": "India-origin comparison",
        "note": "Plains-origin comparison basin with a very different gradient and leverage profile from Nepal-linked Himalayan systems.",
    },
    {
        "id": "son_basin",
        "name": "Son Basin",
        "river_id": "son",
        "fraction": 0.65,
        "comparison_group": "India-origin comparison",
        "note": "Large non-Nepal basin useful for comparing scale with Nepal-linked tributary systems entering the Ganges plain from the north.",
    },
]

INDIA_REFERENCE_RIVERS = [
    {"id": "ganga", "name": "Ganga", "query": "Ganga, India"},
    {"id": "yamuna", "name": "Yamuna", "query": "Yamuna, India"},
    {"id": "ghaghara", "name": "Ghaghara", "query": "Ghaghara River, India"},
    {"id": "gandak", "name": "Gandak", "query": "Gandak, India"},
    {"id": "kosi_india", "name": "Kosi", "query": "Kosi River, India"},
    {"id": "rapti_india", "name": "Rapti", "query": "Rapti River, India"},
    {"id": "mahakali_india", "name": "Mahakali / Sharda", "query": "Mahakali River, India"},
    {"id": "gomti", "name": "Gomti", "query": "Gomti River, India"},
    {"id": "son", "name": "Son", "query": "Son River, India"},
    {"id": "ramganga", "name": "Ramganga", "query": "Ramganga River, India"},
    {"id": "mahananda", "name": "Mahananda", "query": "Mahananda River, India"},
]

DOWNSTREAM_SYSTEMS = [
    {
        "id": "koshi_system",
        "name": "Koshi-Kosi System",
        "basin": "Koshi",
        "nepal_ids": [
            "koshi_main",
            "arun",
            "tamor",
            "sunkoshi",
            "dudhkoshi",
            "tamakoshi",
            "bhotekoshi",
            "indrawati",
            "likhu",
            "balephi",
        ],
        "india_query": "Kosi River, India",
        "india_id": "kosi_india",
        "outlet_fraction": 0.15,
        "downstream_name": "Kosi",
        "annual_discharge_m3s": 1827,
        "annual_runoff_bcm": 57.6,
        "monsoon_share_pct": 73,
        "impact_note": "Major Nepal-origin contributor to the Ganges system, with strong monsoon dominance and high downstream sediment significance.",
    },
    {
        "id": "gandaki_system",
        "name": "Gandaki-Narayani-Gandak System",
        "basin": "Gandaki",
        "nepal_ids": [
            "narayani",
            "kaligandaki",
            "marsyangdi",
            "budhigandaki",
            "trishuli",
            "setigandaki",
            "madi",
            "eastrapti",
        ],
        "india_query": "Gandak, India",
        "india_id": "gandak",
        "outlet_fraction": 0.15,
        "downstream_name": "Gandak / Narayani",
        "annual_discharge_m3s": 1952,
        "annual_runoff_bcm": 61.6,
        "monsoon_share_pct": 74,
        "impact_note": "Nepal's strongest measured border discharge among the main basins in the 2024 basin plans.",
    },
    {
        "id": "karnali_system",
        "name": "Karnali-Ghaghara System",
        "basin": "Karnali",
        "nepal_ids": [
            "karnali",
            "bheri",
            "humlakarnali",
            "mugukarnali",
            "tila",
        ],
        "india_query": "Ghaghara River, India",
        "india_id": "ghaghara",
        "outlet_fraction": 0.15,
        "downstream_name": "Ghaghara",
        "annual_discharge_m3s": 1256,
        "annual_runoff_bcm": 39.6,
        "monsoon_share_pct": 72,
        "impact_note": "Large western Himalayan system with substantial undeveloped power potential relative to its strategic value.",
    },
    {
        "id": "mahakali_system",
        "name": "Mahakali-Sharda System",
        "basin": "Mahakali",
        "nepal_ids": ["mahakali"],
        "india_query": "Mahakali River, India",
        "india_id": "mahakali_india",
        "outlet_fraction": 0.15,
        "downstream_name": "Mahakali / Sharda",
        "annual_discharge_m3s": None,
        "annual_runoff_bcm": None,
        "monsoon_share_pct": 73,
        "impact_note": "Border-river system with strong geopolitical importance, but the public source stack here did not yield a clean annual discharge figure.",
    },
]

RIVER_DEFS = [
    {
        "id": "koshi_main",
        "name": "Koshi River",
        "basin": "Koshi",
        "parent": None,
        "variants": ["Koshi River", "Koshi", "koshi river"],
        "wecs_mw": None,
        "note": "Main trunk of the Koshi system downstream of the Arun–Tamor–Sunkoshi confluence.",
    },
    {
        "id": "arun",
        "name": "Arun River",
        "basin": "Koshi",
        "parent": "Koshi River",
        "variants": ["Arun Khola"],
        "wecs_mw": 10893,
        "note": "Largest tributary contribution in the WECS gross-potential breakdown for Koshi.",
    },
    {
        "id": "tamor",
        "name": "Tamor River",
        "basin": "Koshi",
        "parent": "Koshi River",
        "variants": ["Tamor River", "Tamor Nadi", "Tamur"],
        "wecs_mw": 6348,
        "note": "Major eastern Koshi tributary with strong gross potential.",
    },
    {
        "id": "sunkoshi",
        "name": "Sun Koshi River",
        "basin": "Koshi",
        "parent": "Koshi River",
        "variants": ["Sun Koshi"],
        "wecs_mw": 2670,
        "note": "Core central-eastern tributary corridor feeding the Koshi system.",
    },
    {
        "id": "dudhkoshi",
        "name": "Dudh Koshi River",
        "basin": "Koshi",
        "parent": "Sun Koshi River",
        "variants": ["Dudh Koshi", "Dudh Kosi"],
        "wecs_mw": 3657,
        "note": "Important tributary and storage corridor with major project interest.",
    },
    {
        "id": "tamakoshi",
        "name": "Tama Koshi River",
        "basin": "Koshi",
        "parent": "Sun Koshi River",
        "variants": ["Tamakoshi", "Tamakoshi Nadi"],
        "wecs_mw": 3103,
        "note": "High-value hydropower corridor including Upper Tamakoshi.",
    },
    {
        "id": "bhotekoshi",
        "name": "Bhote Koshi River",
        "basin": "Koshi",
        "parent": "Sun Koshi River",
        "variants": ["Bhote Koshi", "波达柯西河 Bhote Koshi"],
        "wecs_mw": None,
        "note": "Steep trans-Himalayan tributary with dense existing hydropower development.",
    },
    {
        "id": "indrawati",
        "name": "Indrawati River",
        "basin": "Koshi",
        "parent": "Sun Koshi River",
        "variants": ["Indrawati River", "Indrawati Nadi", "Indrawati river", "Indrawati Khola"],
        "wecs_mw": None,
        "note": "Important eastern-central tributary and part of the broader Sunkoshi corridor.",
    },
    {
        "id": "likhu",
        "name": "Likhu Khola",
        "basin": "Koshi",
        "parent": "Sun Koshi River",
        "variants": ["Likhu Khola", "Likhu River", "Likhu"],
        "wecs_mw": None,
        "note": "Smaller but hydropower-relevant Koshi tributary.",
    },
    {
        "id": "balephi",
        "name": "Balephi Khola",
        "basin": "Koshi",
        "parent": "Sun Koshi River",
        "variants": ["Balephi Khola", "Balephi River", "Balephi"],
        "wecs_mw": None,
        "note": "Hydropower-relevant tributary within the Sunkoshi sub-system.",
    },
    {
        "id": "narayani",
        "name": "Narayani River",
        "basin": "Gandaki",
        "parent": None,
        "variants": ["Narayani"],
        "wecs_mw": None,
        "note": "Main trunk of the Gandaki system in the plains and middle hills.",
    },
    {
        "id": "kaligandaki",
        "name": "Kali Gandaki River",
        "basin": "Gandaki",
        "parent": "Narayani River",
        "variants": ["Kali Gandaki", "Kaligandaki river"],
        "wecs_mw": 5735,
        "note": "Largest gross-potential tributary within the Gandaki basin in WECS 2019.",
    },
    {
        "id": "marsyangdi",
        "name": "Marsyangdi River",
        "basin": "Gandaki",
        "parent": "Narayani River",
        "variants": ["Marsyangdi River", "Marsyangdi"],
        "wecs_mw": 4614,
        "note": "Dense existing hydropower corridor in central Nepal.",
    },
    {
        "id": "budhigandaki",
        "name": "Budhi Gandaki River",
        "basin": "Gandaki",
        "parent": "Narayani River",
        "variants": ["Budhi Gandaki"],
        "wecs_mw": 4042,
        "note": "Major tributary and proposed large storage corridor.",
    },
    {
        "id": "trishuli",
        "name": "Trishuli River",
        "basin": "Gandaki",
        "parent": "Narayani River",
        "variants": ["Trishuli River", "Trisuli", "Trisuli Khola", "Trishuli Ganga River"],
        "wecs_mw": 3309,
        "note": "Central corridor tributary with major generation and transmission relevance.",
    },
    {
        "id": "setigandaki",
        "name": "Seti Gandaki River",
        "basin": "Gandaki",
        "parent": "Narayani River",
        "variants": ["Seti Gandaki River"],
        "wecs_mw": 926,
        "note": "Western-central Gandaki tributary with storage and peaking relevance.",
    },
    {
        "id": "madi",
        "name": "Madi River",
        "basin": "Gandaki",
        "parent": "Narayani River",
        "variants": ["Madi Khola"],
        "wecs_mw": None,
        "note": "Secondary but still relevant tributary in the Gandaki system.",
    },
    {
        "id": "eastrapti",
        "name": "East Rapti River",
        "basin": "Gandaki",
        "parent": "Narayani River",
        "variants": ["East Rapti River", "Rapti River", "East Rapti"],
        "wecs_mw": None,
        "note": "Gandaki-connected Rapti tributary with hydropower and floodplain relevance.",
    },
    {
        "id": "karnali",
        "name": "Karnali River",
        "basin": "Karnali",
        "parent": None,
        "variants": ["Karnali"],
        "wecs_mw": 3401,
        "note": "Main western Himalayan trunk and one of Nepal's most strategic undeveloped power systems.",
    },
    {
        "id": "bheri",
        "name": "Bheri River",
        "basin": "Karnali",
        "parent": "Karnali River",
        "variants": ["Bheri River", "Bheri", "Bheri Nadi"],
        "wecs_mw": 7993,
        "note": "Largest gross-potential tributary in the Karnali system according to WECS.",
    },
    {
        "id": "westseti",
        "name": "West Seti River",
        "basin": "Karnali",
        "parent": "Karnali River",
        "variants": ["West Seti"],
        "wecs_mw": 3833,
        "note": "Long-discussed storage and export-oriented corridor.",
    },
    {
        "id": "humlakarnali",
        "name": "Humla Karnali River",
        "basin": "Karnali",
        "parent": "Karnali River",
        "variants": ["Humla Karnali River", "Humla Karnali"],
        "wecs_mw": 2296,
        "note": "Upper western Himalayan tributary with high head and strong strategic potential.",
    },
    {
        "id": "mugukarnali",
        "name": "Mugu Karnali River",
        "basin": "Karnali",
        "parent": "Karnali River",
        "variants": ["Mugu Karnali Nadi", "Mugu karnali Nadi"],
        "wecs_mw": 2011,
        "note": "Upper western tributary relevant to long-term storage and peaking options.",
    },
    {
        "id": "tila",
        "name": "Tila River",
        "basin": "Karnali",
        "parent": "Karnali River",
        "variants": ["Tila Nadi"],
        "wecs_mw": None,
        "note": "Mid-sized Karnali tributary with ongoing project interest.",
    },
    {
        "id": "mahakali",
        "name": "Mahakali River",
        "basin": "Mahakali",
        "parent": None,
        "variants": ["Mahakali River", "Kali River", "Sharda River", "Mahakali"],
        "wecs_mw": 2120,
        "note": "Western border river and site of the long-discussed Pancheshwar multipurpose project.",
    },
    {
        "id": "chameliya",
        "name": "Chameliya River",
        "basin": "Mahakali",
        "parent": "Mahakali River",
        "variants": ["Chameliya River", "Chameliya Khola", "Chameliya"],
        "wecs_mw": None,
        "note": "Mahakali tributary with an existing peaking run-of-river project.",
    },
    {
        "id": "westrapti",
        "name": "West Rapti River",
        "basin": "Medium basins",
        "parent": None,
        "variants": ["West Rapti River", "Rapti River", "West Rapti"],
        "wecs_mw": 745,
        "note": "Medium basin important to western Nepal and to the non-Himalayan hydropower envelope.",
    },
    {
        "id": "babai",
        "name": "Babai River",
        "basin": "Medium basins",
        "parent": None,
        "variants": ["Babai Khola"],
        "wecs_mw": 264,
        "note": "Medium basin with more development-facing than export-facing significance.",
    },
    {
        "id": "bagmati",
        "name": "Bagmati River",
        "basin": "Medium basins",
        "parent": None,
        "variants": ["Bagmati River (बागमती नदी)", "Bagmati Nadi (बागमती नदी)"],
        "wecs_mw": 437,
        "note": "Central medium basin with high urban and environmental relevance.",
    },
    {
        "id": "kamala",
        "name": "Kamala River",
        "basin": "Medium basins",
        "parent": None,
        "variants": ["Kamala River", "Kamala"],
        "wecs_mw": 261,
        "note": "Eastern medium basin with strong seasonal characteristics.",
    },
    {
        "id": "kankai",
        "name": "Kankai River",
        "basin": "Medium basins",
        "parent": None,
        "variants": ["Kankai"],
        "wecs_mw": 394,
        "note": "Eastern medium basin with hydropower value but limited large-system significance.",
    },
    {
        "id": "tinau",
        "name": "Tinau River",
        "basin": "Medium basins",
        "parent": None,
        "variants": ["Tinau River", "Tinau Khola"],
        "wecs_mw": 184,
        "note": "Smaller basin included in the WECS nationwide potential screening.",
    },
    {
        "id": "mechi",
        "name": "Mechi River",
        "basin": "Medium basins",
        "parent": None,
        "variants": ["Mechi River", "Mechi"],
        "wecs_mw": 62,
        "note": "Eastern border basin with limited gross hydropower potential in the national total.",
    },
]


def normalize_river_name(value: str) -> str:
    text = re.sub(r"\(.*?\)", " ", value.lower())
    text = re.sub(r"\b(river|khola|nadi|ganga)\b", " ", text)
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return " ".join(text.split())


def river_network_class(defn: dict[str, Any]) -> str:
    if defn["basin"] == "Medium basins":
        return "medium_basin"
    if defn["parent"] is None:
        return "main_stem"
    return "tributary"


def river_min_length_km(defn: dict[str, Any]) -> float:
    river_class = river_network_class(defn)
    if river_class == "main_stem":
        return 45.0
    if river_class == "tributary":
        return 25.0
    return 18.0


def build_river_network_specs() -> list[dict[str, Any]]:
    specs: list[dict[str, Any]] = []
    for river in RIVER_DEFS:
        aliases = list(dict.fromkeys([river["name"], *river["variants"]]))
        normalized_aliases = sorted({normalize_river_name(alias) for alias in aliases if normalize_river_name(alias)})
        specs.append(
            {
                **river,
                "aliases": aliases,
                "normalized_aliases": normalized_aliases,
                "river_class": river_network_class(river),
                "min_length_km": river_min_length_km(river),
                "reference_buffer_deg": RIVER_REFERENCE_BUFFER_DEG,
                "upstream_seed": None,
                "downstream_seed": None,
                "inclusion_anchors": [],
                "project_aliases": normalized_aliases,
            }
        )
    return specs


RIVER_NETWORK_SPECS = build_river_network_specs()


def read_geojson(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def read_geojson_if_exists(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return read_geojson(path)


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def parse_optional_float(value: Any) -> float | None:
    if value in (None, "", "NA"):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def normalize_project_name(name: str) -> str:
    text = name.lower()
    text = re.sub(r"\b(hydropower|hydro|project|hep|hpp|storage)\b", " ", text)
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return " ".join(text.split())


def project_capacity_value(row: dict[str, Any]) -> float:
    value = row.get("capacity_mw")
    if isinstance(value, (int, float)):
        return float(value)
    return parse_optional_float(value) or 0.0


def short_project_name(name: str, limit: int = 26) -> str:
    text = " ".join(name.split())
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "…"


def find_feature_by_name(fc: dict[str, Any], feature_name: str) -> dict[str, Any] | None:
    for feature in fc["features"]:
        if feature["properties"].get("name") == feature_name:
            return feature
    return None


def load_waterway_records() -> list[dict[str, Any]]:
    shp_path = RAW / "maps" / "nepal_osm_waterways" / "gis_osm_waterways_free_1.shp"
    reader = shapefile.Reader(str(shp_path))
    rows: list[dict[str, Any]] = []
    for sr in reader.iterShapeRecords():
        rec = sr.record.as_dict()
        if rec.get("fclass") not in {"river", "stream"}:
            continue
        if not rec.get("name"):
            continue
        points = sr.shape.points
        if len(points) < 2:
            continue
        parts = list(sr.shape.parts) + [len(points)]
        for idx in range(len(parts) - 1):
            segment = points[parts[idx] : parts[idx + 1]]
            if len(segment) < 2:
                continue
            rows.append(
                {
                    "name": rec["name"],
                    "fclass": rec["fclass"],
                    "geometry": LineString(segment),
                }
            )
    return rows


def bbox_overlaps(left: tuple[float, float, float, float], right: tuple[float, float, float, float]) -> bool:
    return not (left[2] < right[0] or left[0] > right[2] or left[3] < right[1] or left[1] > right[3])


def clip_geometry(geom: BaseGeometry) -> BaseGeometry | None:
    clipped = geom.intersection(CLIP_BOX)
    if clipped.is_empty:
        return None
    if clipped.geom_type == "GeometryCollection":
        parts = [g for g in clipped.geoms if g.geom_type in {"LineString", "MultiLineString"} and not g.is_empty]
        if not parts:
            return None
        clipped = unary_union(parts)
    return clipped


def ensure_hydrorivers_asia() -> None:
    HYDRORIVERS_ROOT.mkdir(parents=True, exist_ok=True)
    if not HYDRORIVERS_ZIP.exists():
        response = requests.get(HYDRORIVERS_URL, stream=True, timeout=120)
        response.raise_for_status()
        with HYDRORIVERS_ZIP.open("wb") as handle:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    handle.write(chunk)
    if not HYDRORIVERS_SHP.exists():
        HYDRORIVERS_DIR.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(HYDRORIVERS_ZIP) as zf:
            zf.extractall(HYDRORIVERS_ROOT)


def load_hydrorivers_reaches() -> tuple[list[dict[str, Any]], dict[int, dict[str, Any]]]:
    ensure_hydrorivers_asia()
    reader = shapefile.Reader(str(HYDRORIVERS_SHP))
    reaches: list[dict[str, Any]] = []
    for sr in reader.iterShapeRecords():
        shape_bbox = tuple(sr.shape.bbox)
        if not bbox_overlaps(shape_bbox, HYDRORIVERS_LOAD_BOUNDS):
            continue
        rec = sr.record.as_dict()
        geom = LineString(sr.shape.points)
        if geom.is_empty or len(geom.coords) < 2:
            continue
        reaches.append(
            {
                "id": int(rec["HYRIV_ID"]),
                "next_down": int(rec["NEXT_DOWN"]),
                "main_riv": int(rec["MAIN_RIV"]),
                "length_km": float(rec["LENGTH_KM"]),
                "dist_dn_km": float(rec["DIST_DN_KM"]),
                "dist_up_km": float(rec["DIST_UP_KM"]),
                "ord_stra": int(rec["ORD_STRA"]),
                "ord_clas": int(rec["ORD_CLAS"]),
                "ord_flow": int(rec["ORD_FLOW"]),
                "dis_av_cms": float(rec["DIS_AV_CMS"]),
                "geometry": geom,
                "bbox": shape_bbox,
            }
        )
    lookup = {reach["id"]: reach for reach in reaches}
    return reaches, lookup


def load_river_review_overrides() -> dict[str, Any]:
    if not RIVER_REVIEW_OVERRIDES_PATH.exists():
        return {}
    return json.loads(RIVER_REVIEW_OVERRIDES_PATH.read_text())


def load_nominatim_cache() -> dict[str, Any]:
    path = PROCESSED / "nominatim_river_cache.json"
    if path.exists():
        return json.loads(path.read_text())
    return {}


def save_nominatim_cache(cache: dict[str, Any]) -> None:
    path = PROCESSED / "nominatim_river_cache.json"
    path.write_text(json.dumps(cache, indent=2))


def load_nominatim_place_cache() -> dict[str, Any]:
    path = PROCESSED / "nominatim_place_cache.json"
    if path.exists():
        return json.loads(path.read_text())
    return {}


def save_nominatim_place_cache(cache: dict[str, Any]) -> None:
    path = PROCESSED / "nominatim_place_cache.json"
    path.write_text(json.dumps(cache, indent=2))


def fetch_nominatim_point(
    query: str,
    cache: dict[str, Any],
    headers: dict[str, str],
) -> dict[str, Any] | None:
    if query in cache:
        candidates = cache[query]
    else:
        response = requests.get(
            NOMINATIM_URL,
            params={"q": query, "format": "jsonv2", "limit": 5},
            headers=headers,
            timeout=60,
        )
        response.raise_for_status()
        candidates = response.json()
        cache[query] = candidates
        save_nominatim_place_cache(cache)
        time.sleep(1.1)

    for candidate in candidates:
        lat = candidate.get("lat")
        lon = candidate.get("lon")
        if lat is None or lon is None:
            continue
        try:
            parsed_lat = float(lat)
            parsed_lon = float(lon)
        except (TypeError, ValueError):
            continue
        if not (GEOPOLITICS_BOUNDS[1] <= parsed_lat <= GEOPOLITICS_BOUNDS[3]):
            continue
        if not (GEOPOLITICS_BOUNDS[0] <= parsed_lon <= GEOPOLITICS_BOUNDS[2]):
            continue
        return {
            "lat": parsed_lat,
            "lon": parsed_lon,
            "display_name": candidate.get("display_name", query),
            "query": query,
            "osm_type": candidate.get("osm_type"),
            "osm_id": candidate.get("osm_id"),
        }
    return None


def build_place_anchor_index() -> tuple[dict[str, dict[str, Any]], list[dict[str, Any]]]:
    cache = load_nominatim_place_cache()
    headers = {"User-Agent": USER_AGENT}
    anchors: dict[str, dict[str, Any]] = {}
    report: list[dict[str, Any]] = []

    for anchor_id, definition in PLACE_ANCHORS.items():
        if "lat" in definition and "lon" in definition:
            anchors[anchor_id] = {
                "id": anchor_id,
                "label": definition["label"],
                "lat": definition["lat"],
                "lon": definition["lon"],
                "display_name": definition["label"],
                "query": "; ".join(definition.get("queries", [])),
                "basis": definition.get("basis", "Manual source-controlled grid anchor"),
            }
            report.append(
                {
                    "id": anchor_id,
                    "label": definition["label"],
                    "status": "ok_manual_source_anchor",
                    "query": anchors[anchor_id]["query"],
                    "display_name": definition["label"],
                }
            )
            continue
        found = None
        for query in definition["queries"]:
            found = fetch_nominatim_point(query, cache, headers)
            if found is not None:
                anchors[anchor_id] = {
                    "id": anchor_id,
                    "label": definition["label"],
                    "lat": found["lat"],
                    "lon": found["lon"],
                    "display_name": found["display_name"],
                    "query": found["query"],
                    "basis": "Nominatim place match",
                }
                report.append(
                    {
                        "id": anchor_id,
                        "label": definition["label"],
                        "status": "ok",
                        "query": found["query"],
                        "display_name": found["display_name"],
                    }
                )
                break
        if found is None:
            report.append(
                {
                    "id": anchor_id,
                    "label": definition["label"],
                    "status": "not_found",
                    "queries": definition["queries"],
                }
            )
    return anchors, report


def fetch_nominatim_lines(defs: list[dict[str, str]]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    cache = load_nominatim_cache()
    features: list[dict[str, Any]] = []
    report: list[dict[str, Any]] = []
    headers = {"User-Agent": USER_AGENT}

    for item in defs:
        query = item["query"]
        if query in cache:
            candidates = cache[query]
        else:
            response = requests.get(
                NOMINATIM_URL,
                params={"q": query, "format": "jsonv2", "limit": 10, "polygon_geojson": 1},
                headers=headers,
                timeout=60,
            )
            response.raise_for_status()
            candidates = response.json()
            cache[query] = candidates
            save_nominatim_cache(cache)
            time.sleep(1.1)

        best = None
        best_geom = None
        best_length = -1.0
        for candidate in candidates:
            geojson = candidate.get("geojson")
            if not geojson:
                continue
            if geojson.get("type") not in {"LineString", "MultiLineString"}:
                continue
            geom = clip_geometry(shape(geojson))
            if geom is None:
                continue
            length = geom.length
            if length > best_length:
                best = candidate
                best_geom = geom
                best_length = length

        if best is None or best_geom is None:
            report.append({"id": item["id"], "name": item["name"], "status": "no_geometry", "query": query})
            continue

        label_lat, label_lon = midpoint_for_label(best_geom)
        features.append(
            {
                "type": "Feature",
                "properties": {
                    "id": item["id"],
                    "name": item["name"],
                    "query": query,
                    "display_name": best.get("display_name"),
                    "osm_type": best.get("osm_type"),
                    "osm_id": best.get("osm_id"),
                    "label_lat": label_lat,
                    "label_lon": label_lon,
                },
                "geometry": best_geom.__geo_interface__,
            }
        )
        report.append(
            {
                "id": item["id"],
                "name": item["name"],
                "status": "ok",
                "query": query,
                "chosen_osm_type": best.get("osm_type"),
                "chosen_osm_id": best.get("osm_id"),
            }
        )
    return {"type": "FeatureCollection", "features": features}, report


def merged_geometry(lines: list[LineString]) -> BaseGeometry | None:
    if not lines:
        return None
    geom = unary_union(lines)
    if geom.is_empty:
        return None
    if geom.geom_type == "GeometryCollection":
        parts = [g for g in geom.geoms if g.geom_type in {"LineString", "MultiLineString"} and not g.is_empty]
        if not parts:
            return None
        geom = unary_union(parts)
    return geom


def clip_line_geometry_to_box(geom: BaseGeometry, clip_box: BaseGeometry) -> BaseGeometry | None:
    clipped = geom.intersection(clip_box)
    if clipped.is_empty:
        return None
    if clipped.geom_type == "GeometryCollection":
        parts = [g for g in clipped.geoms if g.geom_type in {"LineString", "MultiLineString"} and not g.is_empty]
        if not parts:
            return None
        clipped = unary_union(parts)
    return clipped


def line_components(geom: BaseGeometry | None) -> list[LineString]:
    if geom is None or geom.is_empty:
        return []
    if geom.geom_type == "LineString":
        return [geom]
    if geom.geom_type == "MultiLineString":
        return list(geom.geoms)
    return []


def build_waterway_name_lookup(rows: list[dict[str, Any]]) -> dict[str, list[LineString]]:
    lookup: dict[str, list[LineString]] = {}
    for row in rows:
        lookup.setdefault(row["name"], []).append(row["geometry"])
    return lookup


def build_reference_geometry(
    spec: dict[str, Any],
    waterway_lookup: dict[str, list[LineString]],
) -> tuple[BaseGeometry | None, list[str]]:
    lines: list[LineString] = []
    matched_aliases: list[str] = []
    for alias in spec["aliases"]:
        alias_lines = waterway_lookup.get(alias, [])
        if alias_lines:
            matched_aliases.append(alias)
            lines.extend(alias_lines)
    geom = merged_geometry(lines)
    if geom is None:
        return None, matched_aliases
    clipped = clip_line_geometry_to_box(geom, GEOPOLITICS_BOX)
    return clipped, matched_aliases


def reference_endpoints(geom: BaseGeometry | None) -> list[Point]:
    endpoints: list[Point] = []
    for line in line_components(geom):
        coords = list(line.coords)
        if len(coords) < 2:
            continue
        endpoints.append(Point(coords[0]))
        endpoints.append(Point(coords[-1]))
    return endpoints


def point_from_seed(seed: dict[str, Any] | None) -> Point | None:
    if not seed:
        return None
    lat = seed.get("lat")
    lon = seed.get("lon")
    if lat is None or lon is None:
        return None
    return Point(float(lon), float(lat))


def find_candidate_reaches_for_reference(
    reference_geom: BaseGeometry | None,
    reaches: list[dict[str, Any]],
    buffer_deg: float,
    extra_points: list[Point] | None = None,
) -> tuple[list[dict[str, Any]], BaseGeometry | None]:
    if reference_geom is None and not extra_points:
        return [], None

    reference_buffer = reference_geom.buffer(buffer_deg) if reference_geom is not None else None
    candidate_bounds = list(reference_buffer.bounds) if reference_buffer is not None else [999.0, 999.0, -999.0, -999.0]
    for point in extra_points or []:
        px, py = point.x, point.y
        candidate_bounds[0] = min(candidate_bounds[0], px - buffer_deg)
        candidate_bounds[1] = min(candidate_bounds[1], py - buffer_deg)
        candidate_bounds[2] = max(candidate_bounds[2], px + buffer_deg)
        candidate_bounds[3] = max(candidate_bounds[3], py + buffer_deg)
    candidate_bbox = tuple(candidate_bounds)

    candidates: list[dict[str, Any]] = []
    for reach in reaches:
        if not bbox_overlaps(reach["bbox"], candidate_bbox):
            continue
        ref_distance = reach["geometry"].distance(reference_geom) if reference_geom is not None else 999.0
        point_distance = min((point.distance(reach["geometry"]) for point in extra_points or []), default=999.0)
        if reference_geom is not None and ref_distance <= buffer_deg:
            candidates.append({**reach, "reference_distance_deg": ref_distance, "seed_distance_deg": point_distance})
            continue
        if extra_points and point_distance <= buffer_deg:
            candidates.append({**reach, "reference_distance_deg": ref_distance, "seed_distance_deg": point_distance})
    return candidates, reference_buffer


def snap_point_to_candidates(
    point: Point | None,
    candidates: list[dict[str, Any]],
    max_distance_deg: float,
) -> dict[str, Any] | None:
    if point is None:
        return None
    best: tuple[float, dict[str, Any]] | None = None
    for reach in candidates:
        distance = point.distance(reach["geometry"])
        if distance > max_distance_deg:
            continue
        if best is None or distance < best[0]:
            best = (distance, reach)
    return best[1] if best else None


def choose_upstream_reach(
    candidates: list[dict[str, Any]],
    upstream_seed: Point | None,
) -> dict[str, Any] | None:
    snapped = snap_point_to_candidates(upstream_seed, candidates, RIVER_ENDPOINT_SNAP_DEG)
    if snapped is not None:
        return snapped
    if not candidates:
        return None
    return max(
        candidates,
        key=lambda reach: (
            reach["dist_dn_km"],
            -reach.get("reference_distance_deg", 999.0),
            -reach.get("seed_distance_deg", 999.0),
        ),
    )


def chain_descendants(
    start_reach: dict[str, Any],
    reach_lookup: dict[int, dict[str, Any]],
    limit: int = 5000,
) -> set[int]:
    descendants: set[int] = set()
    current = start_reach
    steps = 0
    while current is not None and current["id"] not in descendants and steps < limit:
        descendants.add(current["id"])
        steps += 1
        current = reach_lookup.get(current["next_down"])
    return descendants


def choose_downstream_reach(
    endpoint_candidates: list[dict[str, Any]],
    downstream_seed: Point | None,
    candidates: list[dict[str, Any]],
    upstream_reach: dict[str, Any] | None,
    reach_lookup: dict[int, dict[str, Any]],
) -> dict[str, Any] | None:
    if upstream_reach is None:
        return None
    descendants = chain_descendants(upstream_reach, reach_lookup)
    snapped = snap_point_to_candidates(downstream_seed, candidates, RIVER_ENDPOINT_SNAP_DEG)
    if snapped is not None and snapped["id"] in descendants:
        return snapped
    downstream_candidates = [
        reach for reach in endpoint_candidates if reach["id"] in descendants and reach["id"] != upstream_reach["id"]
    ]
    if not downstream_candidates:
        return None
    return min(
        downstream_candidates,
        key=lambda reach: (
            reach["dist_dn_km"],
            reach.get("reference_distance_deg", 999.0),
            reach.get("seed_distance_deg", 999.0),
        ),
    )


def trace_reach_chain(
    upstream_reach: dict[str, Any] | None,
    downstream_reach: dict[str, Any] | None,
    reference_geom: BaseGeometry | None,
    reference_buffer: BaseGeometry | None,
    reach_lookup: dict[int, dict[str, Any]],
    route_exit_misses: int = RIVER_ROUTE_EXIT_MISSES,
) -> tuple[list[dict[str, Any]], bool]:
    if upstream_reach is None:
        return [], False

    route: list[dict[str, Any]] = []
    seen: set[int] = set()
    current = upstream_reach
    misses = 0
    last_close_index = 0
    downstream_index = 0

    while current is not None and current["id"] not in seen and len(route) < 5000:
        seen.add(current["id"])
        route.append(current)

        close_to_reference = False
        if reference_geom is not None:
            if reference_buffer is not None and current["geometry"].intersects(reference_buffer):
                close_to_reference = True
            elif current["geometry"].distance(reference_geom) <= RIVER_REFERENCE_BUFFER_DEG:
                close_to_reference = True

        if close_to_reference:
            last_close_index = len(route)
            misses = 0
        else:
            misses += 1

        if downstream_reach is not None and current["id"] == downstream_reach["id"]:
            downstream_index = len(route)

        next_reach = reach_lookup.get(current["next_down"])
        if next_reach is None:
            break
        if misses >= route_exit_misses and (downstream_index == 0 or last_close_index >= downstream_index):
            break
        current = next_reach

    cut_index = last_close_index or downstream_index or len(route)
    if downstream_index:
        cut_index = max(cut_index, downstream_index)
    return route[:cut_index], downstream_index > 0 and cut_index >= downstream_index


def join_route_geometry(route: list[dict[str, Any]]) -> tuple[BaseGeometry | None, int, list[str]]:
    if not route:
        return None, 0, ["empty_route"]

    lines: list[LineString] = []
    current_coords: list[tuple[float, float]] = []
    issues: list[str] = []

    for reach in route:
        seg_coords = list(reach["geometry"].coords)
        if len(seg_coords) < 2:
            continue
        if not current_coords:
            current_coords = seg_coords[:]
            continue

        previous_end = current_coords[-1]
        first_delta = math.hypot(previous_end[0] - seg_coords[0][0], previous_end[1] - seg_coords[0][1])
        last_delta = math.hypot(previous_end[0] - seg_coords[-1][0], previous_end[1] - seg_coords[-1][1])
        if first_delta <= RIVER_LINE_JOIN_TOLERANCE_DEG:
            current_coords.extend(seg_coords[1:])
        elif last_delta <= RIVER_LINE_JOIN_TOLERANCE_DEG:
            seg_coords.reverse()
            current_coords.extend(seg_coords[1:])
        else:
            if len(current_coords) >= 2:
                lines.append(LineString(current_coords))
            current_coords = seg_coords[:]
            issues.append(f"disconnected_at_{reach['id']}")

    if len(current_coords) >= 2:
        lines.append(LineString(current_coords))

    if not lines:
        return None, 0, issues or ["empty_lines"]
    if len(lines) == 1:
        return lines[0], 1, issues
    return MultiLineString(lines), len(lines), issues


def midpoint_for_label(geom: BaseGeometry) -> tuple[float, float]:
    if geom.geom_type == "LineString":
        point = geom.interpolate(geom.length * 0.5)
        return point.y, point.x
    if geom.geom_type == "MultiLineString":
        longest = max(list(geom.geoms), key=lambda g: g.length)
        point = longest.interpolate(longest.length * 0.5)
        return point.y, point.x
    pt = geom.representative_point()
    return pt.y, pt.x


def clip_polygon_geometry(geom: BaseGeometry, clip_box: BaseGeometry) -> BaseGeometry | None:
    clipped = geom.intersection(clip_box)
    if clipped.is_empty:
        return None
    if clipped.geom_type == "GeometryCollection":
        parts = [g for g in clipped.geoms if g.geom_type in {"Polygon", "MultiPolygon"} and not g.is_empty]
        if not parts:
            return None
        clipped = unary_union(parts)
    return clipped


def ensure_hydrobasins_level6() -> None:
    zip_path = HYDROBASINS_DIR.parent / "hybas_as_lev06_v1c.zip"
    HYDROBASINS_DIR.parent.mkdir(parents=True, exist_ok=True)
    if not zip_path.exists():
        response = requests.get(HYDROBASINS_LEVEL6_URL, stream=True, timeout=120)
        response.raise_for_status()
        with zip_path.open("wb") as handle:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    handle.write(chunk)
    if not HYDROBASINS_SHP.exists():
        HYDROBASINS_DIR.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(zip_path) as zf:
            zf.extractall(HYDROBASINS_DIR)


def load_hydrobasins() -> list[dict[str, Any]]:
    ensure_hydrobasins_level6()
    reader = shapefile.Reader(str(HYDROBASINS_SHP))
    rows: list[dict[str, Any]] = []
    for sr in reader.iterShapeRecords():
        geom = shape(sr.shape.__geo_interface__)
        if geom.is_empty:
            continue
        rows.append({"properties": sr.record.as_dict(), "geometry": geom})
    return rows


def longest_line_geometry(geom: BaseGeometry) -> LineString:
    if geom.geom_type == "LineString":
        return geom
    if geom.geom_type == "MultiLineString":
        return max(list(geom.geoms), key=lambda g: g.length)
    raise ValueError(f"Expected line geometry, got {geom.geom_type}")


def point_on_longest_line(geom: BaseGeometry, fraction: float) -> tuple[float, float]:
    line = longest_line_geometry(geom)
    point = line.interpolate(line.length * fraction)
    return point.x, point.y


def web_mercator_pixel(lat: float, lon: float, zoom: int = MAP_ZOOM) -> tuple[float, float]:
    lat = max(min(lat, 85.05112878), -85.05112878)
    scale = 256 * (2**zoom)
    x = (lon + 180.0) / 360.0 * scale
    sin_lat = math.sin(math.radians(lat))
    y = (0.5 - math.log((1 + sin_lat) / (1 - sin_lat)) / (4 * math.pi)) * scale
    return x, y


def short_river_label(name: str) -> str:
    text = name.replace(" River", "").replace(" Khola", "")
    return text.replace("Narayani", "Narayani").strip()


def label_bbox(lat: float, lon: float, text: str, dx: int, dy: int, zoom: int = MAP_ZOOM) -> tuple[float, float, float, float]:
    x, y = web_mercator_pixel(lat, lon, zoom)
    width = 7 * len(text) + 12
    height = 14
    left = x + dx
    top = y + dy
    return left, top, left + width, top + height


def bbox_intersects(a: tuple[float, float, float, float], b: tuple[float, float, float, float]) -> bool:
    return not (a[2] < b[0] or a[0] > b[2] or a[3] < b[1] or a[1] > b[3])


def label_center(bbox: tuple[float, float, float, float]) -> tuple[float, float]:
    return ((bbox[0] + bbox[2]) / 2.0, (bbox[1] + bbox[3]) / 2.0)


def river_label_priority(props: dict[str, Any]) -> float:
    priority = 0.0
    if props["id"] in MAJOR_LABEL_IDS:
        priority += 1000
    if props.get("parent") is None:
        priority += 400
    mw = props.get("wecs_mw")
    if isinstance(mw, (int, float)):
        priority += mw / 10
    if props.get("basin") == "Medium basins":
        priority -= 150
    return priority


def choose_river_label_placement(
    feature: dict[str, Any],
    used_boxes: list[tuple[float, float, float, float]],
) -> dict[str, Any] | None:
    props = feature["properties"]
    geom = shape(feature["geometry"])
    text = short_river_label(props["name"])
    candidate_points = [point_on_longest_line(geom, fraction) for fraction in LABEL_SAMPLE_FRACTIONS]
    offsets = []
    if props["id"] in MANUAL_LABEL_OFFSETS:
        offsets.append(MANUAL_LABEL_OFFSETS[props["id"]])
    offsets.extend([offset for offset in LABEL_OFFSETS if offset not in offsets])

    best: dict[str, Any] | None = None
    for lon, lat in candidate_points:
        for dx, dy in offsets:
            bbox = label_bbox(lat, lon, text, dx, dy)
            if any(bbox_intersects(bbox, existing) for existing in used_boxes):
                continue
            edge_penalty = min(
                lon - CLIP_BOUNDS[0],
                CLIP_BOUNDS[2] - lon,
                lat - CLIP_BOUNDS[1],
                CLIP_BOUNDS[3] - lat,
            )
            center = label_center(bbox)
            spacing = min(
                ((center[0] - other[0]) ** 2 + (center[1] - other[1]) ** 2) for other in map(label_center, used_boxes)
            ) if used_boxes else 1e12
            score = spacing + edge_penalty * 1e5
            if best is None or score > best["score"]:
                best = {
                    "lat": lat,
                    "lon": lon,
                    "text": text,
                    "dx": dx,
                    "dy": dy,
                    "bbox": bbox,
                    "score": score,
                }
    return best


def build_label_icon(text: str, color: str, dx: int, dy: int, font_size: int = 10) -> folium.DivIcon:
    width = 7 * len(text) + 12
    height = font_size + 6
    return folium.DivIcon(
        icon_size=(width, height),
        icon_anchor=(0, 0),
        html=(
            f"<div style=\"font-size:{font_size}px;font-weight:700;color:{color};"
            "text-shadow:0 0 2px white, 0 0 6px white;white-space:nowrap;"
            f"transform:translate({dx}px,{dy}px);\">{html.escape(text)}</div>"
        ),
    )


def build_box_label_icon(
    title: str,
    subtitle: str,
    accent_color: str,
    dx: int,
    dy: int,
    width: int = 170,
) -> folium.DivIcon:
    return folium.DivIcon(
        icon_size=(width, 44),
        icon_anchor=(0, 0),
        html=(
            f"<div style=\"transform:translate({dx}px,{dy}px);max-width:{width}px;"
            "font-family:Arial,sans-serif;white-space:normal;line-height:1.2;\">"
            f"<div style=\"background:rgba(255,255,255,0.92);border-left:4px solid {accent_color};"
            "padding:4px 6px;border-radius:4px;box-shadow:0 0 6px rgba(255,255,255,0.85);\">"
            f"<div style=\"font-size:10px;font-weight:700;color:#111827;\">{html.escape(title)}</div>"
            f"<div style=\"font-size:9px;font-weight:600;color:#374151;margin-top:1px;\">{html.escape(subtitle)}</div>"
            "</div></div>"
        ),
    )


def transmission_style_for_status(status: str, traced: bool = False) -> dict[str, Any]:
    base = TRANSMISSION_LINE_STYLES.get(status, TRANSMISSION_LINE_STYLES["Planned"]).copy()
    if traced:
        base["weight"] = round(base["weight"] + 0.5, 2)
        base["opacity"] = min(0.82, base["opacity"] + 0.12)
    return base


def connected_transmission_style(props: dict[str, Any]) -> dict[str, Any]:
    style = transmission_style_for_status(props.get("status", "Planned"), traced=True)
    role = props.get("geometry_role")
    voltage = parse_voltage_kv(props.get("voltage_kv"))
    if voltage is not None and voltage <= 132:
        style["weight"] = max(1.6, style["weight"] - 0.45)
        style["opacity"] = min(style["opacity"], 0.58)
    if role == "manual_trace":
        style["weight"] = max(1.8, style["weight"] - 0.2)
        style["opacity"] = min(style["opacity"], 0.68)
    elif role == "inferred_connector":
        style["weight"] = 1.4
        style["opacity"] = 0.38
        style["dash_array"] = "2 6"
    elif role == "gateway_stub":
        style["weight"] = 1.6
        style["opacity"] = 0.42
        style["dash_array"] = "3 8"
    return style


def cross_border_line_style(props: dict[str, Any]) -> dict[str, Any]:
    status = props.get("status", "Planned")
    base = GRID_STATUS_STYLES.get(status, GRID_STATUS_STYLES["Planned"]).copy()
    role = props.get("connection_scope")
    opacity = 0.82 if status == "Operational" else 0.55
    if role == "gateway_stub":
        opacity = min(opacity, 0.42)
    return {
        "color": base["color"],
        "weight": 2.4 if status == "Operational" else 2.0,
        "opacity": opacity,
        "dash_array": base["dash_array"] if status != "Operational" or role == "gateway_stub" else None,
    }


def parse_voltage_kv(value: Any) -> int | None:
    if value is None:
        return None
    match = re.search(r"\d+", str(value))
    if not match:
        return None
    return int(match.group())


def basin_control_class(nepal_share_pct: float | None, linked_to_nepal: bool) -> str:
    if not linked_to_nepal:
        return "No Nepal-origin control"
    if nepal_share_pct is None:
        return "Nepal-linked system"
    if nepal_share_pct >= 60:
        return "Mostly Nepal-linked basin"
    if nepal_share_pct >= 15:
        return "Shared Himalayan basin routed through Nepal"
    return "Nepal-linked corridor with limited catchment share in Nepal"


def aggregate_upstream_hybasin(
    outlet_point: Point,
    hydrobasins: list[dict[str, Any]],
    clip_box: BaseGeometry,
    country_geom: BaseGeometry,
) -> tuple[BaseGeometry, dict[str, Any]] | None:
    by_id: dict[int, dict[str, Any]] = {}
    upstream_lookup: dict[int, list[int]] = {}
    target_row: dict[str, Any] | None = None

    for row in hydrobasins:
        props = row["properties"]
        basin_id = int(props["HYBAS_ID"])
        by_id[basin_id] = row
        next_down = int(props["NEXT_DOWN"])
        if next_down:
            upstream_lookup.setdefault(next_down, []).append(basin_id)
        if target_row is None and (row["geometry"].contains(outlet_point) or row["geometry"].touches(outlet_point)):
            target_row = row

    if target_row is None:
        return None

    target_id = int(target_row["properties"]["HYBAS_ID"])
    include_ids: set[int] = set()
    stack = [target_id]
    while stack:
        basin_id = stack.pop()
        if basin_id in include_ids:
            continue
        include_ids.add(basin_id)
        stack.extend(upstream_lookup.get(basin_id, []))

    merged = unary_union([by_id[basin_id]["geometry"] for basin_id in include_ids])
    display_geom = clip_polygon_geometry(merged, clip_box)
    if display_geom is None:
        return None

    area_total = merged.area
    nepal_share_pct = None
    if area_total > 0:
        nepal_share_pct = round((merged.intersection(country_geom).area / area_total) * 100, 1)

    return display_geom, {
        "target_hybas_id": target_id,
        "upstream_area_km2": target_row["properties"]["UP_AREA"],
        "sub_basin_area_km2": target_row["properties"]["SUB_AREA"],
        "pfaf_id": target_row["properties"]["PFAF_ID"],
        "nepal_share_pct": nepal_share_pct,
    }


def build_basin_polygons(
    country: dict[str, Any],
    downstream_systems: dict[str, Any],
    india_rivers: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    hydrobasins = load_hydrobasins()
    country_geom = shape(country["geometry"])
    downstream_lookup = features_by_id(downstream_systems)
    india_lookup = features_by_id(india_rivers)
    nepal_features: list[dict[str, Any]] = []
    comparison_features: list[dict[str, Any]] = []
    callout_features: list[dict[str, Any]] = []

    for system in DOWNSTREAM_SYSTEMS:
        india_feature = india_lookup.get(system["india_id"])
        downstream_feature = downstream_lookup.get(system["id"])
        if not india_feature or not downstream_feature:
            continue
        outlet_lon, outlet_lat = point_on_longest_line(shape(india_feature["geometry"]), system.get("outlet_fraction", 0.15))
        aggregated = aggregate_upstream_hybasin(Point(outlet_lon, outlet_lat), hydrobasins, GEOPOLITICS_BOX, country_geom)
        if aggregated is None:
            continue
        basin_geom, meta = aggregated
        props = {
            "id": system["id"],
            "name": system["name"],
            "downstream_name": system["downstream_name"],
            "basin": system["basin"],
            "origin_group": "Nepal-linked basin",
            "control_class": basin_control_class(meta["nepal_share_pct"], linked_to_nepal=True),
            "upstream_area_km2": meta["upstream_area_km2"],
            "nepal_share_pct": meta["nepal_share_pct"],
            "annual_discharge_m3s": system["annual_discharge_m3s"],
            "monsoon_share_pct": system["monsoon_share_pct"],
            "note": system["impact_note"],
        }
        nepal_features.append({"type": "Feature", "properties": props, "geometry": basin_geom.__geo_interface__})
        callout_features.append(
            {
                "type": "Feature",
                "properties": props,
                "geometry": {
                    "type": "Point",
                    "coordinates": [
                        downstream_feature["properties"]["label_lon"],
                        downstream_feature["properties"]["label_lat"],
                    ],
                },
            }
        )

    for item in COMPARISON_BASINS:
        river_feature = india_lookup.get(item["river_id"])
        if not river_feature:
            continue
        outlet_lon, outlet_lat = point_on_longest_line(shape(river_feature["geometry"]), item["fraction"])
        aggregated = aggregate_upstream_hybasin(Point(outlet_lon, outlet_lat), hydrobasins, GEOPOLITICS_BOX, country_geom)
        if aggregated is None:
            continue
        basin_geom, meta = aggregated
        props = {
            "id": item["id"],
            "name": item["name"],
            "downstream_name": river_feature["properties"]["name"],
            "basin": "India-origin comparison",
            "origin_group": item["comparison_group"],
            "control_class": basin_control_class(meta["nepal_share_pct"], linked_to_nepal=False),
            "upstream_area_km2": meta["upstream_area_km2"],
            "nepal_share_pct": meta["nepal_share_pct"],
            "annual_discharge_m3s": None,
            "monsoon_share_pct": None,
            "note": item["note"],
        }
        comparison_features.append({"type": "Feature", "properties": props, "geometry": basin_geom.__geo_interface__})
        callout_features.append(
            {
                "type": "Feature",
                "properties": props,
                "geometry": {
                    "type": "Point",
                    "coordinates": [
                        river_feature["properties"]["label_lon"],
                        river_feature["properties"]["label_lat"],
                    ],
                },
            }
        )

    return (
        {"type": "FeatureCollection", "features": nepal_features},
        {"type": "FeatureCollection", "features": comparison_features},
        {"type": "FeatureCollection", "features": callout_features},
    )


def matching_projects_for_spec(spec: dict[str, Any], projects: list[dict[str, Any]]) -> list[dict[str, Any]]:
    aliases = set(spec["project_aliases"])
    matches: list[dict[str, Any]] = []
    for row in projects:
        river_name = row.get("river") or ""
        if normalize_river_name(river_name) in aliases:
            matches.append(row)
    return matches


def point_on_geometry(point: Point, geom: BaseGeometry | None, tolerance_deg: float = 1e-9) -> bool:
    return geom is not None and not geom.is_empty and point.distance(geom) <= tolerance_deg


def build_river_candidate(
    spec: dict[str, Any],
    waterway_lookup: dict[str, list[LineString]],
    hydrorivers: list[dict[str, Any]],
    hydroriver_lookup: dict[int, dict[str, Any]],
    projects: list[dict[str, Any]],
    overrides: dict[str, Any],
) -> dict[str, Any]:
    override = overrides.get(spec["id"], {})
    spec_for_reference = spec
    alias_override = override.get("aliases")
    if alias_override:
        aliases = [str(alias) for alias in alias_override if str(alias).strip()]
        if aliases:
            spec_for_reference = {
                **spec,
                "aliases": aliases,
                "normalized_aliases": sorted(
                    {normalize_river_name(alias) for alias in aliases if normalize_river_name(alias)}
                ),
            }
    reference_geom, matched_aliases = build_reference_geometry(spec_for_reference, waterway_lookup)
    reference_buffer_deg = float(override.get("reference_buffer_deg") or spec["reference_buffer_deg"])
    route_exit_misses = int(override.get("route_exit_misses") or spec.get("route_exit_misses") or RIVER_ROUTE_EXIT_MISSES)
    upstream_seed = point_from_seed(override.get("upstream_seed") or spec.get("upstream_seed"))
    downstream_seed = point_from_seed(override.get("downstream_seed") or spec.get("downstream_seed"))
    extra_points = [point for point in [upstream_seed, downstream_seed] if point is not None]
    candidates, reference_buffer = find_candidate_reaches_for_reference(
        reference_geom,
        hydrorivers,
        reference_buffer_deg,
        extra_points=extra_points,
    )

    endpoint_reaches: list[dict[str, Any]] = []
    for endpoint in reference_endpoints(reference_geom):
        snapped = snap_point_to_candidates(endpoint, candidates, RIVER_ENDPOINT_SNAP_DEG)
        if snapped is not None:
            endpoint_reaches.append(snapped)

    explicit_upstream_id = override.get("upstream_reach_id")
    explicit_upstream = hydroriver_lookup.get(int(explicit_upstream_id)) if explicit_upstream_id is not None else None
    if explicit_upstream is None:
        explicit_upstream = snap_point_to_candidates(upstream_seed, candidates, RIVER_ENDPOINT_SNAP_DEG)
    if explicit_upstream is not None:
        upstream_reach = explicit_upstream
    elif endpoint_reaches:
        upstream_reach = max(endpoint_reaches, key=lambda reach: reach["dist_dn_km"])
    else:
        upstream_reach = choose_upstream_reach(candidates, None)

    explicit_downstream_id = override.get("downstream_reach_id")
    if explicit_downstream_id is not None:
        downstream_reach = hydroriver_lookup.get(int(explicit_downstream_id))
    else:
        downstream_reach = choose_downstream_reach(
            endpoint_reaches,
            downstream_seed,
            candidates,
            upstream_reach,
            hydroriver_lookup,
        )
    route, downstream_reached = trace_reach_chain(
        upstream_reach,
        downstream_reach,
        reference_geom,
        reference_buffer,
        hydroriver_lookup,
        route_exit_misses=route_exit_misses,
    )
    route_geometry, component_count, route_geometry_issues = join_route_geometry(route)
    display_geometry = clip_line_geometry_to_box(route_geometry, CLIP_BOX) if route_geometry is not None else None
    network_length_km = round(sum(reach["length_km"] for reach in route), 1)

    label_override = override.get("label_anchor")
    if label_override:
        label_lat = float(label_override["lat"])
        label_lon = float(label_override["lon"])
    elif display_geometry is not None:
        label_lat, label_lon = midpoint_for_label(display_geometry)
    elif route_geometry is not None:
        label_lat, label_lon = midpoint_for_label(route_geometry)
    else:
        label_lat = None
        label_lon = None

    label_ok = False
    if label_lat is not None and label_lon is not None:
        label_ok = point_on_geometry(Point(label_lon, label_lat), display_geometry or route_geometry)

    matched_projects = matching_projects_for_spec(spec, projects)
    closest_project_distance_deg = None
    if route_geometry is not None and matched_projects:
        closest_project_distance_deg = min(
            Point(project["lon"], project["lat"]).distance(route_geometry) for project in matched_projects
        )

    project_ok = closest_project_distance_deg is None or closest_project_distance_deg <= RIVER_PROJECT_SANITY_DEG
    control_points_ok = upstream_reach is not None and downstream_reach is not None and downstream_reached
    length_ok = route_geometry is not None and network_length_km >= spec["min_length_km"]
    component_ok = route_geometry is not None and component_count == 1
    reference_ok = reference_geom is not None and bool(matched_aliases)
    review_status = override.get("review_status", "pending")
    suppress = bool(override.get("suppress", False) or review_status == "suppress")

    return {
        "id": spec["id"],
        "name": spec["name"],
        "basin": spec["basin"],
        "parent": spec["parent"],
        "wecs_mw": spec["wecs_mw"],
        "note": spec["note"],
        "river_class": spec["river_class"],
        "min_length_km": spec["min_length_km"],
        "reference_buffer_deg": reference_buffer_deg,
        "route_exit_misses": route_exit_misses,
        "matched_aliases": matched_aliases,
        "reference_geometry": reference_geom,
        "reference_component_count": len(line_components(reference_geom)),
        "upstream_reach": upstream_reach,
        "downstream_reach": downstream_reach,
        "downstream_reached": downstream_reached,
        "route_reaches": route,
        "route_geometry": route_geometry,
        "display_geometry": display_geometry,
        "route_geometry_issues": route_geometry_issues,
        "network_length_km": network_length_km,
        "component_count": component_count,
        "label_lat": label_lat,
        "label_lon": label_lon,
        "label_ok": label_ok,
        "matched_projects": matched_projects,
        "closest_project_distance_deg": closest_project_distance_deg,
        "project_ok": project_ok,
        "review_status": review_status,
        "review_note": override.get("note", ""),
        "suppress": suppress,
        "qa_checks": {
            "reference_geometry": reference_ok,
            "control_points": control_points_ok,
            "component_count": component_ok,
            "min_length_km": length_ok,
            "label_anchor": label_ok,
            "project_proximity": project_ok,
            "parent_continuity": spec["parent"] is None,
        },
        "geometry_source": RIVER_GEOMETRY_SOURCE,
        "source_ids": [reach["id"] for reach in route],
    }


def finalize_river_candidates(
    candidates: list[dict[str, Any]],
    hydroriver_lookup: dict[int, dict[str, Any]],
) -> None:
    name_to_id = {candidate["name"]: candidate["id"] for candidate in candidates}
    candidate_lookup = {candidate["id"]: candidate for candidate in candidates}

    for candidate in candidates:
        parent_name = candidate["parent"]
        parent_ok = parent_name is None
        parent_distance_deg = None
        parent_id = None
        if parent_name is not None:
            parent_id = name_to_id.get(parent_name)
            parent_candidate = candidate_lookup.get(parent_id) if parent_id else None
            if parent_candidate and candidate["downstream_reach"] is not None:
                descendants = chain_descendants(candidate["downstream_reach"], hydroriver_lookup)
                parent_sources = set(parent_candidate["source_ids"])
                parent_ok = bool(parent_sources & descendants)
                if parent_candidate["route_geometry"] is not None and candidate["route_geometry"] is not None:
                    child_end = Point(list(longest_line_geometry(candidate["route_geometry"]).coords)[-1])
                    parent_distance_deg = child_end.distance(parent_candidate["route_geometry"])
        candidate["parent_id"] = parent_id
        candidate["parent_distance_deg"] = parent_distance_deg
        candidate["qa_checks"]["parent_continuity"] = parent_ok
        candidate["qa_status"] = "pass" if all(candidate["qa_checks"].values()) else "fail"
        if candidate["suppress"]:
            candidate["confidence"] = "low"
        elif candidate["qa_status"] == "pass" and candidate["review_status"] == "pass":
            candidate["confidence"] = "high"
        elif candidate["qa_status"] == "pass":
            candidate["confidence"] = "medium"
        else:
            candidate["confidence"] = "low"
        candidate["published"] = (
            candidate["qa_status"] == "pass" and candidate["review_status"] == "pass" and not candidate["suppress"]
        )


def plot_line_geometry(ax: Any, geom: BaseGeometry | None, color: str, linewidth: float, alpha: float) -> None:
    for line in line_components(geom):
        xs, ys = line.xy
        ax.plot(xs, ys, color=color, linewidth=linewidth, alpha=alpha)


def preview_bounds(candidate: dict[str, Any]) -> tuple[float, float, float, float]:
    xs: list[float] = []
    ys: list[float] = []
    for geom in [candidate["reference_geometry"], candidate["display_geometry"] or candidate["route_geometry"]]:
        for line in line_components(geom):
            x_values, y_values = line.xy
            xs.extend(x_values)
            ys.extend(y_values)
    for project in candidate["matched_projects"]:
        xs.append(project["lon"])
        ys.append(project["lat"])
    if not xs or not ys:
        return CLIP_BOUNDS
    pad = 0.12
    return (min(xs) - pad, min(ys) - pad, max(xs) + pad, max(ys) + pad)


def build_review_previews(candidates: list[dict[str, Any]]) -> list[str]:
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        return []

    RIVER_REVIEW_PREVIEW_DIR.mkdir(parents=True, exist_ok=True)
    ordered = sorted(candidates, key=lambda candidate: (candidate["basin"], candidate["name"]))
    page_paths: list[str] = []
    index_rows: list[dict[str, Any]] = []
    per_page = 6
    columns = 3
    rows = 2

    for page_no, start in enumerate(range(0, len(ordered), per_page), start=1):
        page_candidates = ordered[start : start + per_page]
        fig, axes = plt.subplots(rows, columns, figsize=(15, 9))
        axes_list = list(axes.flatten())
        for ax, candidate in zip(axes_list, page_candidates):
            ax.set_facecolor("#f8fafc")
            plot_line_geometry(ax, candidate["reference_geometry"], "#94a3b8", 1.5, 0.9)
            plot_line_geometry(ax, candidate["display_geometry"] or candidate["route_geometry"], "#2563eb", 2.2, 0.95)
            if candidate["matched_projects"]:
                ax.scatter(
                    [project["lon"] for project in candidate["matched_projects"]],
                    [project["lat"] for project in candidate["matched_projects"]],
                    s=12,
                    color="#7c3aed",
                    alpha=0.85,
                )
            minx, miny, maxx, maxy = preview_bounds(candidate)
            ax.set_xlim(minx, maxx)
            ax.set_ylim(miny, maxy)
            ax.set_xticks([])
            ax.set_yticks([])
            ax.set_title(
                f"{candidate['name']}\nqa={candidate['qa_status']} review={candidate['review_status']} "
                f"len={candidate['network_length_km']:.1f}km",
                fontsize=9,
            )
            index_rows.append(
                {
                    "id": candidate["id"],
                    "name": candidate["name"],
                    "page": page_no,
                    "qa_status": candidate["qa_status"],
                    "review_status": candidate["review_status"],
                    "published": candidate["published"],
                }
            )
        for ax in axes_list[len(page_candidates) :]:
            ax.axis("off")
        page_path = RIVER_REVIEW_PREVIEW_DIR / f"river_review_page_{page_no:02d}.png"
        fig.tight_layout()
        fig.savefig(page_path, dpi=180)
        plt.close(fig)
        page_paths.append(str(page_path))

    RIVER_REVIEW_PREVIEW_INDEX.write_text(json.dumps({"pages": page_paths, "rivers": index_rows}, indent=2))
    return page_paths


def candidate_to_public_feature(candidate: dict[str, Any]) -> dict[str, Any]:
    props = {
        "id": candidate["id"],
        "name": candidate["name"],
        "basin": candidate["basin"],
        "parent": candidate["parent"],
        "wecs_mw": candidate["wecs_mw"],
        "note": candidate["note"],
        "label_lat": candidate["label_lat"],
        "label_lon": candidate["label_lon"],
        "geometry_source": candidate["geometry_source"],
        "source_ids": candidate["source_ids"],
        "network_length_km": candidate["network_length_km"],
        "component_count": candidate["component_count"],
        "qa_status": candidate["qa_status"],
        "review_status": candidate["review_status"],
        "confidence": candidate["confidence"],
        "reference_aliases": candidate["matched_aliases"],
        "project_match_count": len(candidate["matched_projects"]),
    }
    return {
        "type": "Feature",
        "properties": props,
        "geometry": candidate["display_geometry"].__geo_interface__,
    }


def candidate_to_report_entry(candidate: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": candidate["id"],
        "name": candidate["name"],
        "basin": candidate["basin"],
        "parent": candidate["parent"],
        "geometry_source": candidate["geometry_source"],
        "matched_aliases": candidate["matched_aliases"],
        "reference_component_count": candidate["reference_component_count"],
        "reference_buffer_deg": candidate["reference_buffer_deg"],
        "route_exit_misses": candidate["route_exit_misses"],
        "source_ids": candidate["source_ids"],
        "network_length_km": candidate["network_length_km"],
        "component_count": candidate["component_count"],
        "qa_checks": candidate["qa_checks"],
        "qa_status": candidate["qa_status"],
        "review_status": candidate["review_status"],
        "confidence": candidate["confidence"],
        "published": candidate["published"],
        "suppress": candidate["suppress"],
        "review_note": candidate["review_note"],
        "upstream_reach_id": candidate["upstream_reach"]["id"] if candidate["upstream_reach"] else None,
        "downstream_reach_id": candidate["downstream_reach"]["id"] if candidate["downstream_reach"] else None,
        "downstream_reached": candidate["downstream_reached"],
        "parent_id": candidate.get("parent_id"),
        "parent_distance_deg": candidate.get("parent_distance_deg"),
        "closest_project_distance_km": round(candidate["closest_project_distance_deg"] * 111.0, 2)
        if candidate["closest_project_distance_deg"] is not None
        else None,
        "project_match_count": len(candidate["matched_projects"]),
        "label_lat": candidate["label_lat"],
        "label_lon": candidate["label_lon"],
        "route_geometry_issues": candidate["route_geometry_issues"],
    }


def build_compatibility_report(candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for candidate in candidates:
        if candidate["published"]:
            status = "ok"
        elif candidate["qa_status"] != "pass":
            status = "failed_qa"
        elif candidate["review_status"] != "pass":
            status = "pending_review"
        else:
            status = "suppressed"
        rows.append(
            {
                "id": candidate["id"],
                "name": candidate["name"],
                "status": status,
                "geometry_source": candidate["geometry_source"],
                "review_status": candidate["review_status"],
                "qa_status": candidate["qa_status"],
                "source_reaches": len(candidate["source_ids"]),
            }
        )
    return rows


def fetch_tributaries(projects: list[dict[str, Any]]) -> tuple[dict[str, Any], dict[str, Any], list[dict[str, Any]]]:
    waterway_lookup = build_waterway_name_lookup(load_waterway_records())
    hydrorivers, hydroriver_lookup = load_hydrorivers_reaches()
    overrides = load_river_review_overrides()
    candidates: list[dict[str, Any]] = []

    for spec in RIVER_NETWORK_SPECS:
        try:
            candidate = build_river_candidate(
                spec,
                waterway_lookup,
                hydrorivers,
                hydroriver_lookup,
                projects,
                overrides,
            )
            candidates.append(candidate)
            print(
                f"[route] {spec['name']} qa={candidate['qa_checks']} "
                f"review={candidate['review_status']} len={candidate['network_length_km']}"
            )
        except Exception as exc:  # noqa: BLE001
            candidates.append(
                {
                    "id": spec["id"],
                    "name": spec["name"],
                    "basin": spec["basin"],
                    "parent": spec["parent"],
                    "wecs_mw": spec["wecs_mw"],
                    "note": spec["note"],
                    "geometry_source": RIVER_GEOMETRY_SOURCE,
                    "reference_geometry": None,
                    "matched_aliases": [],
                    "reference_component_count": 0,
                    "source_ids": [],
                    "network_length_km": 0.0,
                    "component_count": 0,
                    "qa_checks": {
                        "reference_geometry": False,
                        "control_points": False,
                        "component_count": False,
                        "min_length_km": False,
                        "label_anchor": False,
                        "project_proximity": False,
                        "parent_continuity": False,
                    },
                    "qa_status": "fail",
                    "review_status": overrides.get(spec["id"], {}).get("review_status", "pending"),
                    "confidence": "low",
                    "published": False,
                    "suppress": False,
                    "review_note": str(exc),
                    "upstream_reach": None,
                    "downstream_reach": None,
                    "downstream_reached": False,
                    "matched_projects": [],
                    "closest_project_distance_deg": None,
                    "label_lat": None,
                    "label_lon": None,
                    "route_geometry_issues": [f"error:{exc}"],
                    "route_geometry": None,
                    "display_geometry": None,
                }
            )
            print(f"[err] {spec['name']}: {exc}")

    finalize_river_candidates(candidates, hydroriver_lookup)
    preview_pages = build_review_previews(candidates)
    public_features = [candidate_to_public_feature(candidate) for candidate in candidates if candidate["published"]]
    qa_report = {
        "summary": {
            "total_specs": len(RIVER_NETWORK_SPECS),
            "published_count": len(public_features),
            "qa_pass_count": sum(1 for candidate in candidates if candidate["qa_status"] == "pass"),
            "review_pass_count": sum(1 for candidate in candidates if candidate["review_status"] == "pass"),
            "preview_pages": preview_pages,
        },
        "rivers": [candidate_to_report_entry(candidate) for candidate in candidates],
    }
    compatibility_report = build_compatibility_report(candidates)
    return {"type": "FeatureCollection", "features": public_features}, qa_report, compatibility_report


def features_by_id(fc: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {feature["properties"]["id"]: feature for feature in fc["features"]}


def approx_point_distance_m(left: Point, right: Point) -> float:
    lat_mid = math.radians((left.y + right.y) / 2.0)
    dx = (left.x - right.x) * 111_320.0 * math.cos(lat_mid)
    dy = (left.y - right.y) * 110_540.0
    return math.hypot(dx, dy)


def point_on_linear_geometry(point: Point, geom: BaseGeometry) -> Point:
    best_point: Point | None = None
    best_distance = float("inf")
    for line in line_components(geom):
        candidate = line.interpolate(line.project(point))
        distance = point.distance(candidate)
        if distance < best_distance:
            best_distance = distance
            best_point = candidate
    if best_point is None:
        return point
    return best_point


def build_tributary_alias_lookup(tributaries: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    public_lookup = features_by_id(tributaries)
    spec_lookup = {spec["id"]: spec for spec in RIVER_NETWORK_SPECS}
    alias_lookup: dict[str, list[dict[str, Any]]] = {}
    for river_id, feature in public_lookup.items():
        spec = spec_lookup.get(river_id)
        if spec is None:
            continue
        for alias in spec["normalized_aliases"]:
            alias_lookup.setdefault(alias, []).append(feature)
    return alias_lookup


def project_waterway_aliases(river_name: str) -> list[str]:
    aliases: list[str] = []
    base_name = (river_name or "").strip()
    if base_name:
        aliases.append(base_name)
    aliases.extend(PROJECT_WATERWAY_NAME_ALIASES.get(normalize_river_name(river_name or ""), []))
    return list(dict.fromkeys(alias for alias in aliases if alias))


def nearest_named_tributary_match(
    point: Point,
    river_name: str,
    alias_lookup: dict[str, list[dict[str, Any]]],
) -> dict[str, Any] | None:
    normalized = normalize_river_name(river_name or "")
    matches = alias_lookup.get(normalized, [])
    best: dict[str, Any] | None = None
    for feature in matches:
        geometry = shape(feature["geometry"])
        snapped = point_on_linear_geometry(point, geometry)
        distance_deg = point.distance(snapped)
        candidate = {
            "source": "published_tributary",
            "source_label": feature["properties"]["name"],
            "geometry": geometry,
            "snapped_point": snapped,
            "distance_deg": distance_deg,
        }
        if best is None or distance_deg < best["distance_deg"]:
            best = candidate
    return best


def nearest_named_osm_waterway_match(
    point: Point,
    river_name: str,
    waterway_lookup: dict[str, list[LineString]],
    search_deg: float,
) -> dict[str, Any] | None:
    best: dict[str, Any] | None = None
    for alias in project_waterway_aliases(river_name):
        for geometry in waterway_lookup.get(alias, []):
            snapped = point_on_linear_geometry(point, geometry)
            distance_deg = point.distance(snapped)
            if distance_deg > search_deg:
                continue
            candidate = {
                "source": "osm_waterway",
                "source_label": f"OSM {alias}",
                "geometry": geometry,
                "snapped_point": snapped,
                "distance_deg": distance_deg,
            }
            if best is None or distance_deg < best["distance_deg"]:
                best = candidate
    return best


def nearest_hydrorivers_match(
    point: Point,
    reaches: list[dict[str, Any]],
    search_deg: float,
) -> dict[str, Any] | None:
    query_bbox = (point.x - search_deg, point.y - search_deg, point.x + search_deg, point.y + search_deg)
    best: dict[str, Any] | None = None
    for reach in reaches:
        if not bbox_overlaps(reach["bbox"], query_bbox):
            continue
        snapped = point_on_linear_geometry(point, reach["geometry"])
        distance_deg = point.distance(snapped)
        if distance_deg > search_deg:
            continue
        candidate = {
            "source": "hydrorivers",
            "source_label": f"HydroRIVERS order {reach['ord_stra']}",
            "geometry": reach["geometry"],
            "snapped_point": snapped,
            "distance_deg": distance_deg,
            "ord_stra": reach["ord_stra"],
            "hyriv_id": reach["id"],
        }
        if best is None or distance_deg < best["distance_deg"]:
            best = candidate
    return best


def choose_project_river_match(
    point: Point,
    river_name: str,
    alias_lookup: dict[str, list[dict[str, Any]]],
    waterway_lookup: dict[str, list[LineString]],
    reaches: list[dict[str, Any]],
) -> dict[str, Any] | None:
    candidates = [
        nearest_named_tributary_match(point, river_name, alias_lookup),
        nearest_named_osm_waterway_match(point, river_name, waterway_lookup, PROJECT_RIVER_SEARCH_DEG),
        nearest_hydrorivers_match(point, reaches, PROJECT_RIVER_SEARCH_DEG),
    ]
    candidates = [candidate for candidate in candidates if candidate is not None]
    if not candidates:
        return None
    return min(candidates, key=lambda candidate: candidate["distance_deg"])


def apply_project_display_anchor(
    row: dict[str, Any],
    match: dict[str, Any] | None,
) -> None:
    raw_point = Point(row["raw_lon"], row["raw_lat"])
    match_distance_m = approx_point_distance_m(raw_point, match["snapped_point"]) if match is not None else None
    snapped_allowed = row["license_type"] in PROJECT_RIVER_SNAP_THRESHOLDS_DEG
    snap_threshold_deg = PROJECT_RIVER_SNAP_THRESHOLDS_DEG.get(row["license_type"], 0.0)

    display_point = raw_point
    precision_tier = "raw_reference"
    location_basis = "Low-confidence raw registry reference point"
    match_basis = None
    offset_m = 0.0

    if row["license_type"] == "Operation":
        precision_tier = "site"
        if match is not None and match["distance_deg"] <= PROJECT_RIVER_CONTEXT_THRESHOLD_DEG:
            location_basis = "Operating-project registry point near mapped river"
        else:
            location_basis = "Operating-project registry point with weak river context"
    elif snapped_allowed and match is not None and match["distance_deg"] <= snap_threshold_deg:
        snapped_point = match["snapped_point"]
        offset_m = approx_point_distance_m(raw_point, snapped_point)
        if raw_point.distance(snapped_point) >= PROJECT_SNAP_MIN_SHIFT_DEG:
            display_point = snapped_point
            precision_tier = "river_reference"
            location_basis = "River-aligned project reference derived from registry point"
        elif match["source"] in {"published_tributary", "osm_waterway"}:
            precision_tier = "river_reference"
            location_basis = "Registry point already sits close to mapped river"
        else:
            location_basis = "Registry point already sits close to mapped reach"
    elif row["license_type"] == "Generation":
        location_basis = "Generation-stage raw registry project reference point"

    if precision_tier == "site":
        offset_m = approx_point_distance_m(raw_point, display_point)

    if match is not None:
        if match["source"] == "published_tributary":
            match_basis = f"Published tributary geometry: {match['source_label']}"
        elif match["source"] == "osm_waterway":
            match_basis = match["source_label"]
        else:
            match_basis = match["source_label"]

    row["display_lat"] = display_point.y
    row["display_lon"] = display_point.x
    row["precision_tier"] = precision_tier
    row["precision_label"] = PROJECT_PRECISION_LABELS[precision_tier]
    row["location_basis"] = location_basis
    row["map_match_basis"] = match_basis
    row["nearest_river_distance_m"] = match_distance_m
    row["display_offset_m"] = offset_m
    row["display_mode"] = "snapped" if precision_tier == "river_reference" else "raw"


def build_project_display_anchors(
    projects: list[dict[str, Any]],
    tributaries: dict[str, Any],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    alias_lookup = build_tributary_alias_lookup(tributaries)
    waterway_lookup = build_waterway_name_lookup(load_waterway_records())
    hydrorivers, _ = load_hydrorivers_reaches()
    tier_counts = {"site": 0, "river_reference": 0, "raw_reference": 0}
    snap_examples: list[dict[str, Any]] = []

    for row in projects:
        raw_point = Point(row["raw_lon"], row["raw_lat"])
        match = choose_project_river_match(raw_point, row.get("river", ""), alias_lookup, waterway_lookup, hydrorivers)
        apply_project_display_anchor(row, match)
        override = PROJECT_DISPLAY_OVERRIDES.get(row["project"])
        if override is not None:
            if "lat" in override and "lon" in override:
                display_point = Point(float(override["lon"]), float(override["lat"]))
                row["display_lat"] = display_point.y
                row["display_lon"] = display_point.x
                row["display_offset_m"] = approx_point_distance_m(raw_point, display_point)
            row["precision_tier"] = override.get("precision_tier", row["precision_tier"])
            row["precision_label"] = PROJECT_PRECISION_LABELS[row["precision_tier"]]
            row["location_basis"] = override.get("location_basis", row["location_basis"])
            row["map_match_basis"] = override.get("map_match_basis", row.get("map_match_basis"))
            row["display_mode"] = "snapped" if row["precision_tier"] == "river_reference" else "raw"
        tier_counts[row["precision_tier"]] += 1
        if row["precision_tier"] == "river_reference" and len(snap_examples) < 20:
            snap_examples.append(
                {
                    "project": row["project"],
                    "license_type": row["license_type"],
                    "river": row.get("river"),
                    "offset_m": round(row["display_offset_m"], 1),
                    "map_match_basis": row["map_match_basis"],
                }
            )

    return projects, {"tier_counts": tier_counts, "snap_examples": snap_examples}


def hydropower_display_points_geojson(projects: list[dict[str, Any]]) -> dict[str, Any]:
    features: list[dict[str, Any]] = []
    for row in projects:
        features.append(
            {
                "type": "Feature",
                "properties": {
                    "project": row["project"],
                    "license_type": row["license_type"],
                    "capacity_mw": row["capacity_mw"],
                    "river": row["river"],
                    "district": row["district"],
                    "municipality": row.get("municipality"),
                    "province": row["province"],
                    "precision_tier": row["precision_tier"],
                    "precision_label": row["precision_label"],
                    "location_basis": row["location_basis"],
                    "map_match_basis": row.get("map_match_basis"),
                    "nearest_river_distance_m": row.get("nearest_river_distance_m"),
                    "display_offset_m": row.get("display_offset_m"),
                    "raw_lat": row["raw_lat"],
                    "raw_lon": row["raw_lon"],
                },
                "geometry": {"type": "Point", "coordinates": [row["display_lon"], row["display_lat"]]},
            }
        )
    return {"type": "FeatureCollection", "features": features}


def build_downstream_systems(
    tributaries: dict[str, Any], india_rivers: dict[str, Any]
) -> tuple[dict[str, Any], dict[str, Any]]:
    nepal_lookup = features_by_id(tributaries)
    india_lookup = features_by_id(india_rivers)
    system_features: list[dict[str, Any]] = []
    hydrology_features: list[dict[str, Any]] = []

    for system in DOWNSTREAM_SYSTEMS:
        parts: list[BaseGeometry] = []
        for rid in system["nepal_ids"]:
            feat = nepal_lookup.get(rid)
            if feat:
                parts.append(shape(feat["geometry"]))
        india_geom = None
        india_id = system.get("india_id")
        if india_id and india_id in india_lookup:
            india_geom = shape(india_lookup[india_id]["geometry"])
            parts.append(india_geom)

        if not parts:
            continue
        merged = unary_union(parts)
        if merged.is_empty:
            continue
        label_geom = india_geom if india_geom is not None else merged
        label_lat, label_lon = midpoint_for_label(label_geom)

        system_features.append(
            {
                "type": "Feature",
                "properties": {
                    "id": system["id"],
                    "name": system["name"],
                    "basin": system["basin"],
                    "downstream_name": system["downstream_name"],
                    "annual_discharge_m3s": system["annual_discharge_m3s"],
                    "annual_runoff_bcm": system["annual_runoff_bcm"],
                    "monsoon_share_pct": system["monsoon_share_pct"],
                    "impact_note": system["impact_note"],
                    "label_lat": label_lat,
                    "label_lon": label_lon,
                },
                "geometry": merged.__geo_interface__,
            }
        )

        nepal_parts = [shape(nepal_lookup[rid]["geometry"]) for rid in system["nepal_ids"] if rid in nepal_lookup]
        nepal_geom = unary_union(nepal_parts) if nepal_parts else merged
        south_point = None
        if nepal_geom.geom_type == "LineString":
            coords = list(nepal_geom.coords)
            south_point = min(coords, key=lambda c: c[1])
        elif nepal_geom.geom_type == "MultiLineString":
            coords = [pt for geom in nepal_geom.geoms for pt in geom.coords]
            if coords:
                south_point = min(coords, key=lambda c: c[1])
        if south_point:
            hydrology_features.append(
                {
                    "type": "Feature",
                    "properties": {
                        "id": system["id"],
                        "name": system["name"],
                        "basin": system["basin"],
                        "annual_discharge_m3s": system["annual_discharge_m3s"],
                        "annual_runoff_bcm": system["annual_runoff_bcm"],
                        "monsoon_share_pct": system["monsoon_share_pct"],
                        "impact_note": system["impact_note"],
                    },
                    "geometry": {"type": "Point", "coordinates": [south_point[0], south_point[1]]},
                }
            )

    return (
        {"type": "FeatureCollection", "features": system_features},
        {"type": "FeatureCollection", "features": hydrology_features},
    )


def build_country_outline(provinces: dict[str, Any]) -> dict[str, Any]:
    province_shapes = [shape(feature["geometry"]) for feature in provinces["features"]]
    union = unary_union(province_shapes)
    return {"type": "Feature", "properties": {"name": "Nepal"}, "geometry": union.__geo_interface__}


def province_name_lookup(provinces: dict[str, Any]) -> dict[str, str]:
    lookup: dict[str, str] = {}
    for feature in provinces["features"]:
        props = feature["properties"]
        province_code = props.get("PROVINCE")
        province_name = props.get("PR_NAME")
        if province_code is not None and province_name:
            lookup[str(province_code)] = province_name
    return lookup


def load_projects() -> list[dict[str, Any]]:
    data = read_geojson(RAW / "projects_storage" / "naxa_hydropower_projects.geojson")
    province_lookup = province_name_lookup(read_geojson(RAW / "maps" / "nepal_provinces.geojson"))
    rows: list[dict[str, Any]] = []
    for feature in data["features"]:
        props = feature["properties"]
        lon, lat = feature["geometry"]["coordinates"]
        province_code = str(props.get("province_name") or props.get("province") or "")
        province_name = province_lookup.get(province_code, province_code or "Unknown")
        rows.append(
            {
                "project": props["project"],
                "capacity_mw": props["capacity"],
                "river": props["river"],
                "district": props["district_name"],
                "municipality": props.get("gapanapa_name"),
                "province": province_name,
                "license_type": props["license_type"],
                "promoter": props["promoter"],
                "lat": lat,
                "lon": lon,
                "raw_lat": lat,
                "raw_lon": lon,
            }
        )
    return rows


def basin_color_for_name(basin_name: str) -> str:
    return BASIN_COLORS.get(basin_name, BASIN_COLORS["Medium basins"])


def annotation_anchor_from_feature(feature: dict[str, Any], basis: str) -> dict[str, Any]:
    props = feature["properties"]
    return {
        "lat": props["label_lat"],
        "lon": props["label_lon"],
        "basis": basis,
    }


def build_basin_seasonality_annotations(tributaries: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    rows = read_csv_rows(ROOT / "data" / "processed" / "tables" / "nepal_basin_seasonality_baseline.csv")
    tributary_lookup = features_by_id(tributaries)
    features: list[dict[str, Any]] = []
    skipped: list[dict[str, str]] = []

    for index, row in enumerate(rows):
        basin = row["basin"]
        anchor: dict[str, Any] | None = None
        river_id = BASIN_SEASONALITY_RIVER_IDS.get(basin)
        if river_id and river_id in tributary_lookup:
            anchor = annotation_anchor_from_feature(tributary_lookup[river_id], "river label anchor")
        elif basin in MANUAL_POINT_ANCHORS:
            point = MANUAL_POINT_ANCHORS[basin]
            anchor = {"lat": point["lat"], "lon": point["lon"], "basis": point["basis"]}

        if anchor is None:
            skipped.append({"basin": basin, "reason": "no_anchor"})
            continue

        monsoon_text = row["monsoon_metric"]
        monsoon_pct_match = re.search(r"(\d+(?:\.\d+)?)%", monsoon_text)
        label_subtitle = (
            f"{monsoon_pct_match.group(1)}% monsoon" if monsoon_pct_match else short_project_name(monsoon_text, limit=24)
        )
        dx, dy = ANNOTATION_OFFSETS[index % len(ANNOTATION_OFFSETS)]
        features.append(
            {
                "type": "Feature",
                "properties": {
                    "id": f"basin_{normalize_project_name(basin).replace(' ', '_')}",
                    "theme": "basin_seasonality",
                    "name": basin,
                    "label_title": basin,
                    "label_subtitle": label_subtitle,
                    "marker_color": basin_color_for_name(basin if basin in BASIN_COLORS else "Medium basins"),
                    "dx": dx,
                    "dy": dy,
                    "basin_type": row["basin_type"],
                    "catchment_area_km2": row["catchment_area_km2"],
                    "annual_rainfall_mm": row["annual_rainfall_mm"],
                    "annual_discharge_or_runoff": row["annual_discharge_or_runoff"],
                    "monsoon_metric": row["monsoon_metric"],
                    "post_monsoon_metric": row["post_monsoon_metric"],
                    "winter_metric": row["winter_metric"],
                    "pre_monsoon_metric": row["pre_monsoon_metric"],
                    "dry_season_note": row["dry_season_note"],
                    "source_note": row["source_note"],
                    "caution": row["caution"],
                    "location_basis": anchor["basis"],
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": [anchor["lon"], anchor["lat"]],
                },
            }
        )

    return {"type": "FeatureCollection", "features": features}, {"skipped": skipped}


def build_top_capacity_project_annotations(projects: list[dict[str, Any]]) -> dict[str, Any]:
    ranked = sorted(projects, key=project_capacity_value, reverse=True)[:TOP_PROJECT_LIMIT]
    features: list[dict[str, Any]] = []
    for index, row in enumerate(ranked, start=1):
        capacity = project_capacity_value(row)
        dx, dy = ANNOTATION_OFFSETS[(index - 1) % len(ANNOTATION_OFFSETS)]
        features.append(
            {
                "type": "Feature",
                "properties": {
                    "id": f"top_project_{index}",
                    "theme": "top_capacity_project",
                    "rank": index,
                    "name": row["project"],
                    "label_title": short_project_name(row["project"]),
                    "label_subtitle": f"{capacity:,.0f} MW · {row['license_type']}",
                    "marker_color": LICENSE_COLORS.get(row["license_type"], "#475569"),
                    "dx": dx,
                    "dy": dy,
                    "project": row["project"],
                    "capacity_mw": capacity,
                    "river": row["river"],
                    "district": row["district"],
                    "province": row["province"],
                    "license_type": row["license_type"],
                    "promoter": row["promoter"],
                    "source_note": "Naxa / DoED-linked public hydropower project dataset",
                    "location_basis": row.get("location_basis", "Project point"),
                    "precision_label": row.get("precision_label"),
                    "display_offset_m": row.get("display_offset_m"),
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": [row.get("display_lon", row["lon"]), row.get("display_lat", row["lat"])],
                },
            }
        )
    return {"type": "FeatureCollection", "features": features}


def project_lookup_by_name(projects: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {row["project"]: row for row in projects}


def annotation_lookup_by_project_name(feature_collection: dict[str, Any]) -> dict[str, dict[str, Any]]:
    lookup: dict[str, dict[str, Any]] = {}
    for feature in feature_collection["features"]:
        name = feature["properties"].get("project")
        if name:
            lookup[name] = feature
    return lookup


def build_priority_project_watchlist(
    projects: list[dict[str, Any]],
    storage_annotations: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    project_lookup = project_lookup_by_name(projects)
    storage_lookup = annotation_lookup_by_project_name(storage_annotations)
    features: list[dict[str, Any]] = []
    skipped: list[dict[str, str]] = []

    for index, definition in enumerate(PRIORITY_PROJECTS):
        project = project_lookup.get(definition["project_name"])
        storage_feature = (
            storage_lookup.get(definition["storage_annotation_name"]) if definition.get("storage_annotation_name") else None
        )
        anchor_override = PRIORITY_PROJECT_ANCHOR_OVERRIDES.get(definition["project_name"])
        if project is None and storage_feature is None:
            skipped.append({"id": definition["id"], "reason": "missing_project"})
            continue

        props: dict[str, Any]
        lon: float
        lat: float
        if storage_feature is not None:
            storage_props = storage_feature["properties"]
            lon, lat = storage_feature["geometry"]["coordinates"]
            props = {
                "capacity_mw": storage_props.get("installed_mw"),
                "river": project.get("river") if project else None,
                "district": project.get("district") if project else None,
                "province": project.get("province") if project else None,
                "license_type": project.get("license_type") if project else "Survey",
                "location_basis": storage_props.get("location_basis"),
                "precision_label": project.get("precision_label") if project else None,
                "display_offset_m": project.get("display_offset_m") if project else None,
            }
        else:
            lon = float(project.get("display_lon", project["lon"]))
            lat = float(project.get("display_lat", project["lat"]))
            props = {
                "capacity_mw": project_capacity_value(project),
                "river": project.get("river"),
                "district": project.get("district"),
                "province": project.get("province"),
                "license_type": project.get("license_type"),
                "location_basis": project.get("location_basis"),
                "precision_label": project.get("precision_label"),
                "display_offset_m": project.get("display_offset_m"),
            }

        if anchor_override is not None:
            lon = float(anchor_override["lon"])
            lat = float(anchor_override["lat"])
            props["location_basis"] = anchor_override["basis"]
            if project is not None:
                props["display_offset_m"] = approx_point_distance_m(Point(project["raw_lon"], project["raw_lat"]), Point(lon, lat))

        style = PRIORITY_PROJECT_GROUP_STYLES[definition["group"]]
        dx, dy = ANNOTATION_OFFSETS[index % len(ANNOTATION_OFFSETS)]
        features.append(
            {
                "type": "Feature",
                "properties": {
                    "id": definition["id"],
                    "theme": "priority_project_watchlist",
                    "group": definition["group"],
                    "group_label": style["label"],
                    "name": definition["label_title"],
                    "label_title": definition["label_title"],
                    "label_subtitle": definition["label_subtitle"],
                    "marker_color": style["color"],
                    "dx": dx,
                    "dy": dy,
                    "project": definition["project_name"],
                    "capacity_mw": props["capacity_mw"],
                    "river": props["river"],
                    "district": props["district"],
                    "province": props["province"],
                    "license_type": props["license_type"],
                    "location_basis": props["location_basis"],
                    "precision_label": props["precision_label"],
                    "display_offset_m": props["display_offset_m"],
                    "priority_read": definition["priority_read"],
                    "source_note": definition["source_note"],
                },
                "geometry": {"type": "Point", "coordinates": [lon, lat]},
            }
        )

    return {"type": "FeatureCollection", "features": features}, {"skipped": skipped}


def resolve_storage_anchor(
    storage_row: dict[str, str],
    projects: list[dict[str, Any]],
    tributaries: dict[str, Any],
) -> dict[str, Any] | None:
    hint = STORAGE_SHORTLIST_ANCHORS.get(storage_row["project"])
    if not hint:
        return None

    if "project_name" in hint:
        matches = [row for row in projects if row["project"] == hint["project_name"]]
        if matches:
            row = matches[0]
            return {
                "lat": row.get("display_lat", row["lat"]),
                "lon": row.get("display_lon", row["lon"]),
                "basis": row.get("location_basis", hint["confidence"].replace("_", " ")),
            }

    if "project_prefix" in hint:
        matches = [row for row in projects if row["project"].startswith(hint["project_prefix"])]
        if matches:
            lat = sum(row.get("display_lat", row["lat"]) for row in matches) / len(matches)
            lon = sum(row.get("display_lon", row["lon"]) for row in matches) / len(matches)
            return {
                "lat": lat,
                "lon": lon,
                "basis": "cluster centroid of matched project points",
            }

    if "river_id" in hint:
        tributary_lookup = features_by_id(tributaries)
        feature = tributary_lookup.get(hint["river_id"])
        if feature:
            anchor = annotation_anchor_from_feature(feature, "river anchor")
            return anchor

    if "point_name" in hint and hint["point_name"] in MANUAL_POINT_ANCHORS:
        point = MANUAL_POINT_ANCHORS[hint["point_name"]]
        return {
            "lat": point["lat"],
            "lon": point["lon"],
            "basis": point["basis"],
        }

    return None


def build_storage_shortlist_annotations(
    projects: list[dict[str, Any]],
    tributaries: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    rows = read_csv_rows(ROOT / "data" / "processed" / "tables" / "nepal_storage_dry_energy_shortlist.csv")
    features: list[dict[str, Any]] = []
    skipped: list[dict[str, str]] = []

    for index, row in enumerate(rows):
        anchor = resolve_storage_anchor(row, projects, tributaries)
        if anchor is None:
            skipped.append({"project": row["project"], "reason": "no_reliable_anchor"})
            continue

        installed_mw = parse_optional_float(row["installed_mw"])
        dry_energy_gwh = parse_optional_float(row["dry_energy_gwh"])
        dry_share_pct = parse_optional_float(row["dry_share_pct"])
        dx, dy = ANNOTATION_OFFSETS[index % len(ANNOTATION_OFFSETS)]
        subtitle = (
            f"{dry_energy_gwh:,.0f} dry GWh · {installed_mw:,.0f} MW"
            if dry_energy_gwh is not None and installed_mw is not None
            else f"{installed_mw:,.0f} MW" if installed_mw is not None else row["category"].replace("_", " ")
        )
        basin_name = row["basin"] if row["basin"] in BASIN_COLORS else "Medium basins"
        features.append(
            {
                "type": "Feature",
                "properties": {
                    "id": f"storage_{normalize_project_name(row['project']).replace(' ', '_')}",
                    "theme": "storage_shortlist",
                    "name": row["project"],
                    "label_title": short_project_name(row["project"]),
                    "label_subtitle": subtitle,
                    "marker_color": basin_color_for_name(basin_name),
                    "dx": dx,
                    "dy": dy,
                    "project": row["project"],
                    "category": row["category"],
                    "basin": row["basin"],
                    "installed_mw": installed_mw,
                    "total_storage_mcm": parse_optional_float(row["total_storage_mcm"]),
                    "effective_storage_mcm": parse_optional_float(row["effective_storage_mcm"]),
                    "annual_energy_gwh": parse_optional_float(row["annual_energy_gwh"]),
                    "dry_energy_gwh": dry_energy_gwh,
                    "dry_share_pct": dry_share_pct,
                    "priority_read": row["priority_read"],
                    "source_note": row["source_note"],
                    "location_basis": anchor["basis"],
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": [anchor["lon"], anchor["lat"]],
                },
            }
        )

    return {"type": "FeatureCollection", "features": features}, {"skipped": skipped}


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    radius_km = 6371.0
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return 2 * radius_km * math.asin(math.sqrt(a))


def build_transmission_corridors(
    anchors: dict[str, dict[str, Any]],
) -> tuple[dict[str, Any], dict[str, Any]]:
    features: list[dict[str, Any]] = []
    skipped: list[dict[str, Any]] = []

    for index, definition in enumerate(TRANSMISSION_CORRIDORS):
        anchor_points: list[dict[str, Any]] = []
        missing = [anchor_id for anchor_id in definition["anchor_ids"] if anchor_id not in anchors]
        if missing:
            skipped.append({"id": definition["id"], "reason": "missing_anchor", "anchors": missing})
            continue

        for anchor_id in definition["anchor_ids"]:
            anchor_points.append(anchors[anchor_id])

        geometry = LineString([(anchor["lon"], anchor["lat"]) for anchor in anchor_points])
        label_lat, label_lon = midpoint_for_label(geometry)
        total_km = 0.0
        for left, right in zip(anchor_points, anchor_points[1:]):
            total_km += haversine_km(left["lat"], left["lon"], right["lat"], right["lon"])
        dx, dy = ANNOTATION_OFFSETS[index % len(ANNOTATION_OFFSETS)]
        features.append(
            {
                "type": "Feature",
                "properties": {
                    "id": definition["id"],
                    "name": definition["name"],
                    "short_label": definition["short_label"],
                    "status": definition["status"],
                    "category": definition["category"],
                    "voltage_kv": definition["voltage_kv"],
                    "components": definition["components"],
                    "source_note": definition["source_note"],
                    "importance": definition["importance"],
                    "geometry_basis": definition["geometry_basis"],
                    "anchor_chain": [anchor["label"] for anchor in anchor_points],
                    "label_lat": label_lat,
                    "label_lon": label_lon,
                    "dx": dx,
                    "dy": dy,
                    "spine_length_km": total_km,
                    "marker_color": GRID_STATUS_STYLES[definition["status"]]["color"],
                    "dash_array": GRID_STATUS_STYLES[definition["status"]]["dash_array"],
                },
                "geometry": geometry.__geo_interface__,
            }
        )

    return {"type": "FeatureCollection", "features": features}, {"skipped": skipped}


def build_cross_border_interconnections(
    anchors: dict[str, dict[str, Any]],
) -> tuple[dict[str, Any], dict[str, Any]]:
    features: list[dict[str, Any]] = []
    skipped: list[dict[str, Any]] = []

    for index, definition in enumerate(CROSS_BORDER_INTERCONNECTIONS):
        anchor = anchors.get(definition["location_anchor_id"])
        if anchor is None:
            skipped.append(
                {
                    "id": definition["id"],
                    "reason": "missing_anchor",
                    "anchors": [definition["location_anchor_id"]],
                }
            )
            continue

        india_anchor = anchors.get(definition["india_anchor_id"]) if definition.get("india_anchor_id") else None
        dx, dy = ANNOTATION_OFFSETS[index % len(ANNOTATION_OFFSETS)]
        features.append(
            {
                "type": "Feature",
                "properties": {
                    "id": definition["id"],
                    "name": definition["name"],
                    "short_label": definition["short_label"],
                    "status": definition["status"],
                    "voltage_kv": definition["voltage_kv"],
                    "nepal_node": definition["nepal_node"],
                    "india_node": definition["india_node"],
                    "location_basis": definition["location_basis"],
                    "timeline_note": definition["timeline_note"],
                    "source_note": definition["source_note"],
                    "anchor_label": anchor["label"],
                    "anchor_display_name": anchor["display_name"],
                    "india_anchor_display_name": india_anchor["display_name"] if india_anchor else None,
                    "label_lat": anchor["lat"],
                    "label_lon": anchor["lon"],
                    "dx": dx,
                    "dy": dy,
                    "marker_color": GRID_STATUS_STYLES[definition["status"]]["color"],
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": [anchor["lon"], anchor["lat"]],
                },
            }
        )

    return {"type": "FeatureCollection", "features": features}, {"skipped": skipped}


def annotation_popup_html(props: dict[str, Any]) -> str:
    theme = props["theme"]
    if theme == "basin_seasonality":
        return (
            f"<div style='width:310px'>"
            f"<h4 style='margin:0 0 6px 0'>{html.escape(props['name'])}</h4>"
            f"<b>Theme:</b> Basin seasonality<br>"
            f"<b>Monsoon metric:</b> {html.escape(props['monsoon_metric'])}<br>"
            f"<b>Post-monsoon:</b> {html.escape(props['post_monsoon_metric'])}<br>"
            f"<b>Winter:</b> {html.escape(props['winter_metric'])}<br>"
            f"<b>Pre-monsoon:</b> {html.escape(props['pre_monsoon_metric'])}<br>"
            f"<b>Annual discharge / runoff:</b> {html.escape(props['annual_discharge_or_runoff'])}<br>"
            f"<b>Dry-season note:</b> {html.escape(props['dry_season_note'])}<br>"
            f"<b>Anchor basis:</b> {html.escape(props['location_basis'])}<br>"
            f"<b>Source:</b> {html.escape(props['source_note'])}"
            f"</div>"
        )
    if theme == "top_capacity_project":
        basis_line = f"<b>Map basis:</b> {html.escape(props['location_basis'])}<br>" if props.get("location_basis") else ""
        precision_line = f"<b>Precision tier:</b> {html.escape(props['precision_label'])}<br>" if props.get("precision_label") else ""
        offset = props.get("display_offset_m")
        offset_line = f"<b>Offset from raw registry point:</b> {offset:,.0f} m<br>" if isinstance(offset, (int, float)) and offset >= 1 else ""
        return (
            f"<div style='width:300px'>"
            f"<h4 style='margin:0 0 6px 0'>#{props['rank']} {html.escape(props['project'])}</h4>"
            f"<b>Capacity:</b> {props['capacity_mw']:,.0f} MW<br>"
            f"<b>License stage:</b> {html.escape(props['license_type'])}<br>"
            f"{basis_line}"
            f"{precision_line}"
            f"{offset_line}"
            f"<b>River:</b> {html.escape(props['river'] or 'Unknown')}<br>"
            f"<b>District:</b> {html.escape(props['district'] or 'Unknown')}<br>"
            f"<b>Province:</b> {html.escape(props['province'] or 'Unknown')}<br>"
            f"<b>Promoter:</b> {html.escape(props['promoter'] or 'Unknown')}<br>"
            f"<b>Source:</b> {html.escape(props['source_note'])}"
            f"</div>"
        )
    if theme == "priority_project_watchlist":
        basis_line = f"<b>Map basis:</b> {html.escape(props['location_basis'])}<br>" if props.get("location_basis") else ""
        precision_line = f"<b>Precision tier:</b> {html.escape(props['precision_label'])}<br>" if props.get("precision_label") else ""
        offset = props.get("display_offset_m")
        offset_line = f"<b>Offset from raw registry point:</b> {offset:,.0f} m<br>" if isinstance(offset, (int, float)) and offset >= 1 else ""
        capacity = props.get("capacity_mw")
        capacity_line = f"<b>Capacity:</b> {capacity:,.0f} MW<br>" if isinstance(capacity, (int, float)) else ""
        stage_line = f"<b>Stage:</b> {html.escape(props['license_type'])}<br>" if props.get("license_type") else ""
        return (
            f"<div style='width:320px'>"
            f"<h4 style='margin:0 0 6px 0'>{html.escape(props['label_title'])}</h4>"
            f"<b>Watchlist group:</b> {html.escape(props['group_label'])}<br>"
            f"{capacity_line}"
            f"{stage_line}"
            f"{basis_line}"
            f"{precision_line}"
            f"{offset_line}"
            f"<b>River:</b> {html.escape(props['river'] or 'Unknown')}<br>"
            f"<b>District:</b> {html.escape(props['district'] or 'Unknown')}<br>"
            f"<b>Province:</b> {html.escape(props['province'] or 'Unknown')}<br>"
            f"<b>Why it matters:</b> {html.escape(props['priority_read'])}<br>"
            f"<b>Source:</b> {html.escape(props['source_note'])}"
            f"</div>"
        )
    annual = props.get("annual_energy_gwh")
    dry_energy = props.get("dry_energy_gwh")
    dry_share = props.get("dry_share_pct")
    total_storage = props.get("total_storage_mcm")
    effective_storage = props.get("effective_storage_mcm")
    installed = props.get("installed_mw")
    annual_line = f"<b>Annual energy:</b> {annual:,.1f} GWh<br>" if isinstance(annual, (int, float)) else ""
    dry_line = f"<b>Dry energy:</b> {dry_energy:,.1f} GWh<br>" if isinstance(dry_energy, (int, float)) else ""
    share_line = f"<b>Dry-energy share:</b> {dry_share:.1f}%<br>" if isinstance(dry_share, (int, float)) else ""
    total_storage_line = f"<b>Total storage:</b> {total_storage:,.1f} MCM<br>" if isinstance(total_storage, (int, float)) else ""
    effective_storage_line = (
        f"<b>Effective storage:</b> {effective_storage:,.1f} MCM<br>" if isinstance(effective_storage, (int, float)) else ""
    )
    installed_line = f"<b>Installed capacity:</b> {installed:,.1f} MW<br>" if isinstance(installed, (int, float)) else ""
    return (
        f"<div style='width:320px'>"
        f"<h4 style='margin:0 0 6px 0'>{html.escape(props['project'])}</h4>"
        f"<b>Theme:</b> Storage shortlist<br>"
        f"<b>Basin:</b> {html.escape(props['basin'])}<br>"
        f"<b>Category:</b> {html.escape(props['category'].replace('_', ' '))}<br>"
        f"{installed_line}"
        f"{total_storage_line}"
        f"{effective_storage_line}"
        f"{annual_line}"
        f"{dry_line}"
        f"{share_line}"
        f"<b>Anchor basis:</b> {html.escape(props['location_basis'])}<br>"
        f"<b>Why it matters:</b> {html.escape(props['priority_read'])}<br>"
        f"<b>Source:</b> {html.escape(props['source_note'])}"
        f"</div>"
    )


def add_annotation_layer(
    m: folium.Map,
    feature_collection: dict[str, Any],
    layer_name: str,
    show: bool = False,
) -> None:
    group = folium.FeatureGroup(name=layer_name, show=show)
    for feature in feature_collection["features"]:
        props = feature["properties"]
        lon, lat = feature["geometry"]["coordinates"]
        color = props["marker_color"]
        tooltip = props["label_title"]
        if props.get("label_subtitle"):
            tooltip = f"{tooltip} | {props['label_subtitle']}"
        folium.CircleMarker(
            location=[lat, lon],
            radius=6,
            color=color,
            weight=2,
            fill=True,
            fill_color=color,
            fill_opacity=0.9,
            tooltip=tooltip,
            popup=folium.Popup(annotation_popup_html(props), max_width=340),
        ).add_to(group)
        folium.Marker(
            location=[lat, lon],
            icon=build_box_label_icon(
                props["label_title"],
                props["label_subtitle"],
                color,
                props["dx"],
                props["dy"],
            ),
            popup=folium.Popup(annotation_popup_html(props), max_width=340),
        ).add_to(group)
    group.add_to(m)


def transmission_corridor_popup_html(props: dict[str, Any]) -> str:
    components = "<br>".join(html.escape(component) for component in props["components"])
    chain = " → ".join(html.escape(item) for item in props["anchor_chain"])
    return (
        f"<div style='width:320px'>"
        f"<h4 style='margin:0 0 6px 0'>{html.escape(props['name'])}</h4>"
        f"<b>Status:</b> {html.escape(props['status'])}<br>"
        f"<b>Category:</b> {html.escape(props['category'])}<br>"
        f"<b>Voltage:</b> {html.escape(props['voltage_kv'])} kV<br>"
        f"<b>Indicative spine length:</b> {props['spine_length_km']:,.0f} km<br>"
        f"<b>Anchor chain:</b> {chain}<br>"
        f"<b>Named segments:</b><br>{components}<br>"
        f"<b>Importance:</b> {html.escape(props['importance'])}<br>"
        f"<b>Geometry basis:</b> {html.escape(props['geometry_basis'])}<br>"
        f"<b>Source:</b> {html.escape(props['source_note'])}"
        f"</div>"
    )


def interconnection_popup_html(props: dict[str, Any]) -> str:
    india_display = props.get("india_anchor_display_name")
    india_basis = f"<b>Indian endpoint match:</b> {html.escape(india_display)}<br>" if india_display else ""
    return (
        f"<div style='width:320px'>"
        f"<h4 style='margin:0 0 6px 0'>{html.escape(props['name'])}</h4>"
        f"<b>Status:</b> {html.escape(props['status'])}<br>"
        f"<b>Voltage:</b> {html.escape(props['voltage_kv'])} kV<br>"
        f"<b>Nepal node:</b> {html.escape(props['nepal_node'])}<br>"
        f"<b>India node:</b> {html.escape(props['india_node'])}<br>"
        f"<b>Map location basis:</b> {html.escape(props['location_basis'])}<br>"
        f"<b>Anchor match:</b> {html.escape(props['anchor_display_name'])}<br>"
        f"{india_basis}"
        f"<b>Timeline note:</b> {html.escape(props['timeline_note'])}<br>"
        f"<b>Source:</b> {html.escape(props['source_note'])}"
        f"</div>"
    )


def status_rank(status: str) -> int:
    order = {
        "Operational": 4,
        "Partially operational": 3,
        "Under construction": 3,
        "Implementation setup": 2,
        "Planned": 1,
    }
    return order.get(status, 0)


def add_transmission_nodes(
    m: folium.Map,
    anchors: dict[str, dict[str, Any]],
    show_nodes: bool = False,
    show_labels: bool = False,
) -> None:
    node_group = folium.FeatureGroup(name="Transmission nodes", show=show_nodes)
    label_group = folium.FeatureGroup(name="Transmission node labels", show=show_labels)
    node_meta: dict[str, dict[str, Any]] = {}

    for definition in TRANSMISSION_CORRIDORS:
        for anchor_id in definition["anchor_ids"]:
            anchor = anchors.get(anchor_id)
            if not anchor:
                continue
            existing = node_meta.get(anchor_id)
            candidate = {
                "id": anchor_id,
                "label": anchor["label"],
                "lat": anchor["lat"],
                "lon": anchor["lon"],
                "display_name": anchor["display_name"],
                "category": "hub",
                "status": definition["status"],
                "voltage_kv": definition["voltage_kv"],
            }
            if existing is None or status_rank(candidate["status"]) > status_rank(existing["status"]):
                node_meta[anchor_id] = candidate

    for definition in CROSS_BORDER_INTERCONNECTIONS:
        anchor_id = definition["location_anchor_id"]
        anchor = anchors.get(anchor_id)
        if not anchor:
            continue
        existing = node_meta.get(anchor_id)
        candidate = {
            "id": anchor_id,
            "label": anchor["label"],
            "lat": anchor["lat"],
            "lon": anchor["lon"],
            "display_name": anchor["display_name"],
            "category": "gateway",
            "status": definition["status"],
            "voltage_kv": definition["voltage_kv"],
        }
        if existing is None or existing.get("category") != "gateway" or status_rank(candidate["status"]) > status_rank(existing["status"]):
            node_meta[anchor_id] = candidate

    for node in node_meta.values():
        status_color = GRID_STATUS_STYLES.get(node["status"], GRID_STATUS_STYLES["Planned"])["color"]
        outline = TRANSMISSION_NODE_COLORS["gateway"] if node["category"] == "gateway" else TRANSMISSION_NODE_COLORS["hub"]
        popup_html = (
            f"<div style='width:280px'>"
            f"<h4 style='margin:0 0 6px 0'>{html.escape(node['label'])}</h4>"
            f"<b>Category:</b> {'Cross-border gateway' if node['category'] == 'gateway' else 'Transmission hub'}<br>"
            f"<b>Status class:</b> {html.escape(node['status'])}<br>"
            f"<b>Highest mapped voltage:</b> {html.escape(str(node['voltage_kv']))} kV<br>"
            f"<b>Anchor match:</b> {html.escape(node['display_name'])}"
            f"</div>"
        )
        if node["category"] == "gateway":
            folium.RegularPolygonMarker(
                location=[node["lat"], node["lon"]],
                number_of_sides=4,
                rotation=45,
                radius=8,
                color=outline,
                weight=2,
                fill=True,
                fill_color=status_color,
                fill_opacity=0.92,
                tooltip=f"{node['label']} | gateway",
                popup=folium.Popup(popup_html, max_width=320),
            ).add_to(node_group)
        else:
            folium.CircleMarker(
                location=[node["lat"], node["lon"]],
                radius=6,
                color=outline,
                weight=2,
                fill=True,
                fill_color=status_color,
                fill_opacity=0.88,
                tooltip=f"{node['label']} | grid hub",
                popup=folium.Popup(popup_html, max_width=320),
            ).add_to(node_group)
        folium.Marker(
            location=[node["lat"], node["lon"]],
            icon=build_box_label_icon(
                node["label"],
                "gateway" if node["category"] == "gateway" else "grid hub",
                TRANSMISSION_LABEL_ACCENT,
                10,
                -12,
                width=130,
            ),
            popup=folium.Popup(popup_html, max_width=320),
        ).add_to(label_group)

    node_group.add_to(m)
    label_group.add_to(m)


def add_transmission_corridors(
    m: folium.Map,
    corridors: dict[str, Any],
    show_lines: bool = False,
    show_labels: bool = False,
    min_label_voltage_kv: int | None = None,
) -> None:
    group = folium.FeatureGroup(name="Context · corridor sketch", show=show_lines)
    label_group = folium.FeatureGroup(name="Transmission labels", show=show_labels)
    for feature in corridors["features"]:
        props = feature["properties"]
        line_style = transmission_style_for_status(props["status"], traced=False)

        def style_function(_: Any, line_style: dict[str, Any] = line_style) -> dict[str, Any]:
            return {
                "color": line_style["color"],
                "weight": line_style["weight"],
                "opacity": line_style["opacity"],
                "dashArray": line_style["dash_array"],
            }

        folium.GeoJson(
            feature,
            style_function=style_function,
            tooltip=f"{props['short_label']} | {props['status']}",
            popup=folium.Popup(transmission_corridor_popup_html(props), max_width=340),
        ).add_to(group)
        voltage_kv = parse_voltage_kv(props.get("voltage_kv"))
        if min_label_voltage_kv is not None and (voltage_kv is None or voltage_kv < min_label_voltage_kv):
            continue
        folium.Marker(
            location=[props["label_lat"], props["label_lon"]],
            icon=build_box_label_icon(
                props["short_label"],
                f"{props['voltage_kv']} kV · {props['status']}",
                TRANSMISSION_LABEL_ACCENT,
                props["dx"],
                props["dy"],
            ),
            popup=folium.Popup(transmission_corridor_popup_html(props), max_width=340),
        ).add_to(label_group)
    group.add_to(m)
    label_group.add_to(m)


def connected_transmission_popup_html(props: dict[str, Any]) -> str:
    notes = props.get("notes") or ""
    return (
        f"<div style='width:330px'>"
        f"<h4 style='margin:0 0 6px 0'>{html.escape(props.get('segment_name') or props.get('name') or '')}</h4>"
        f"<b>Corridor:</b> {html.escape(props.get('corridor_id', ''))}<br>"
        f"<b>Status:</b> {html.escape(props.get('status', 'Unknown'))}<br>"
        f"<b>Voltage:</b> {html.escape(str(props.get('voltage_kv', '')))} kV<br>"
        f"<b>Geometry role:</b> {html.escape(props.get('geometry_role', ''))}<br>"
        f"<b>Trace confidence:</b> {html.escape(props.get('trace_confidence', ''))}<br>"
        f"<b>Source:</b> {html.escape(props.get('source_id', ''))}<br>"
        f"<b>Length:</b> {float(props.get('length_km') or 0):,.1f} km<br>"
        f"<b>Basis:</b> {html.escape(props.get('geometry_basis', ''))}<br>"
        f"{'<b>Notes:</b> ' + html.escape(notes) if notes else ''}"
        f"</div>"
    )


def add_connected_transmission_network(
    m: folium.Map,
    network: dict[str, Any] | None,
    show_lines: bool = True,
    show_labels: bool = False,
) -> None:
    if not network or not network.get("features"):
        return

    group = folium.FeatureGroup(name="Major transmission network", show=show_lines)
    label_group = folium.FeatureGroup(name="Transmission labels", show=show_labels)
    by_corridor: dict[str, list[dict[str, Any]]] = {}
    for feature in network["features"]:
        props = feature["properties"]
        by_corridor.setdefault(props["corridor_id"], []).append(feature)
        line_style = connected_transmission_style(props)
        tooltip_role = props.get("geometry_role", "network")
        folium.GeoJson(
            feature,
            style_function=lambda _, line_style=line_style: {
                "color": line_style["color"],
                "weight": line_style["weight"],
                "opacity": line_style["opacity"],
                "dashArray": line_style["dash_array"],
            },
            tooltip=f"{props.get('segment_name', props.get('corridor_id'))} | {tooltip_role}",
            popup=folium.Popup(connected_transmission_popup_html(props), max_width=360),
        ).add_to(group)

    for corridor_id, features in by_corridor.items():
        source_features = [feature for feature in features if feature["properties"].get("geometry_role") != "inferred_connector"]
        geometries = [shape(feature["geometry"]) for feature in source_features or features]
        merged = unary_union(geometries)
        label_lat, label_lon = midpoint_for_label(merged)
        first_props = features[0]["properties"]
        folium.Marker(
            location=[label_lat, label_lon],
            icon=build_box_label_icon(
                first_props.get("name", corridor_id),
                f"{first_props.get('voltage_kv', '')} kV · connected trace",
                TRANSMISSION_LABEL_ACCENT,
                8,
                -10,
                width=160,
            ),
            popup=folium.Popup(connected_transmission_popup_html(first_props), max_width=360),
        ).add_to(label_group)

    group.add_to(m)
    label_group.add_to(m)


def add_cross_border_interconnection_lines(
    m: folium.Map,
    linework: dict[str, Any] | None,
    show_lines: bool = True,
) -> None:
    if not linework or not linework.get("features"):
        return
    group = folium.FeatureGroup(name="Cross-border links", show=show_lines)
    for feature in linework["features"]:
        props = feature["properties"]
        line_style = cross_border_line_style(props)
        folium.GeoJson(
            feature,
            style_function=lambda _, line_style=line_style: {
                "color": line_style["color"],
                "weight": line_style["weight"],
                "opacity": line_style["opacity"],
                "dashArray": line_style["dash_array"],
            },
            tooltip=f"{props.get('name')} | {props.get('status')} | {props.get('connection_scope')}",
            popup=folium.Popup(
                (
                    f"<div style='width:320px'>"
                    f"<h4 style='margin:0 0 6px 0'>{html.escape(props.get('name', ''))}</h4>"
                    f"<b>Status:</b> {html.escape(props.get('status', 'Unknown'))}<br>"
                    f"<b>Voltage:</b> {html.escape(str(props.get('voltage_kv', '')))} kV<br>"
                    f"<b>Connection scope:</b> {html.escape(props.get('connection_scope', ''))}<br>"
                    f"<b>Source:</b> {html.escape(props.get('source_id', ''))}<br>"
                    f"<b>Length shown:</b> {float(props.get('length_km') or 0):,.1f} km<br>"
                    f"<b>Basis:</b> {html.escape(props.get('geometry_basis', ''))}<br>"
                    f"{html.escape(props.get('notes', ''))}"
                    f"</div>"
                ),
                max_width=350,
            ),
        ).add_to(group)
    group.add_to(m)


def add_cross_border_interconnections(
    m: folium.Map,
    interconnections: dict[str, Any],
    show_points: bool = False,
    show_labels: bool = False,
) -> None:
    group = folium.FeatureGroup(name="Cross-border gateways", show=show_points)
    label_group = folium.FeatureGroup(name="Cross-border gateway labels", show=show_labels)
    for feature in interconnections["features"]:
        props = feature["properties"]
        lon, lat = feature["geometry"]["coordinates"]
        color = props["marker_color"]
        folium.RegularPolygonMarker(
            location=[lat, lon],
            number_of_sides=4,
            rotation=45,
            radius=9,
            color=color,
            weight=2,
            fill=True,
            fill_color=color,
            fill_opacity=0.88,
            tooltip=f"{props['short_label']} | {props['status']}",
            popup=folium.Popup(interconnection_popup_html(props), max_width=340),
        ).add_to(group)
        folium.Marker(
            location=[props["label_lat"], props["label_lon"]],
            icon=build_box_label_icon(
                props["short_label"],
                f"{props['voltage_kv']} kV · {props['status']}",
                TRANSMISSION_LABEL_ACCENT,
                props["dx"],
                props["dy"],
            ),
            popup=folium.Popup(interconnection_popup_html(props), max_width=340),
        ).add_to(label_group)
    group.add_to(m)
    label_group.add_to(m)


def add_base_layers(m: folium.Map) -> None:
    folium.TileLayer(
        tiles="CartoDB positron",
        name="Carto Positron",
        control=True,
        overlay=False,
        show=True,
        detect_retina=True,
    ).add_to(m)
    folium.TileLayer(
        tiles="OpenTopoMap",
        name="Topographic",
        control=True,
        overlay=False,
        show=False,
        attr="Map data: OpenStreetMap contributors, SRTM | Map style: OpenTopoMap",
    ).add_to(m)
    folium.TileLayer(
        tiles=(
            "https://server.arcgisonline.com/ArcGIS/rest/services/"
            "World_Imagery/MapServer/tile/{z}/{y}/{x}"
        ),
        name="Satellite",
        attr="Tiles © Esri",
        control=True,
        overlay=False,
        show=False,
    ).add_to(m)


def add_boundaries(m: folium.Map, provinces: dict[str, Any], country: dict[str, Any]) -> None:
    country_group = folium.FeatureGroup(name="Nepal border", show=True)
    folium.GeoJson(
        country,
        interactive=False,
        style_function=lambda _: {
            "color": "#151515",
            "weight": 3.2,
            "fillOpacity": 0.0,
        },
    ).add_to(country_group)
    country_group.add_to(m)

    province_group = folium.FeatureGroup(name="Province borders", show=True)
    folium.GeoJson(
        provinces,
        interactive=False,
        style_function=lambda _: {
            "color": "#666666",
            "weight": 1.0,
            "fillColor": "#ffffff",
            "fillOpacity": 0.02,
        },
    ).add_to(province_group)
    province_group.add_to(m)

    province_labels = folium.FeatureGroup(name="Province labels", show=False)
    for feature in provinces["features"]:
        geom = shape(feature["geometry"])
        point: Point = geom.representative_point()
        folium.Marker(
            location=[point.y, point.x],
            icon=folium.DivIcon(
                html=(
                    "<div style=\"font-size:11px;font-weight:700;color:#222;"
                    "background:rgba(255,255,255,0.75);padding:1px 4px;"
                    "border-radius:4px;white-space:nowrap;\">"
                    f"{feature['properties']['PR_NAME']}</div>"
                )
            ),
        ).add_to(province_labels)
    province_labels.add_to(m)


def river_popup_html(props: dict[str, Any]) -> str:
    mw = props.get("wecs_mw")
    mw_line = f"<b>WECS gross potential:</b> {mw:,} MW<br>" if isinstance(mw, (int, float)) else ""
    parent = props.get("parent") or "Main stem"
    length_line = (
        f"<b>Published network length:</b> {props['network_length_km']:.1f} km<br>"
        if isinstance(props.get("network_length_km"), (int, float))
        else ""
    )
    return (
        f"<div style='width:280px'>"
        f"<h4 style='margin:0 0 6px 0'>{props['name']}</h4>"
        f"<b>Basin:</b> {props['basin']}<br>"
        f"<b>Parent:</b> {parent}<br>"
        f"{mw_line}"
        f"{length_line}"
        f"<b>Geometry source:</b> {html.escape(props.get('geometry_source', 'Unknown'))}<br>"
        f"<b>Confidence:</b> {html.escape(props.get('confidence', 'unknown'))}<br>"
        f"<b>Context:</b> {props['note']}<br>"
        f"<b>Hydro reaches:</b> {len(props.get('source_ids', []))}"
        f"</div>"
    )


def india_river_popup_html(props: dict[str, Any]) -> str:
    display_name = html.escape(props.get("display_name") or props["name"])
    return (
        f"<div style='width:270px'>"
        f"<h4 style='margin:0 0 6px 0'>{html.escape(props['name'])}</h4>"
        f"<b>Reference role:</b> Northern Gangetic plain comparison river<br>"
        f"<b>OSM / Nominatim match:</b> {display_name}<br>"
        f"<b>Purpose:</b> Use this layer to compare Nepal-origin systems against major northern Indian rivers that do not originate in Nepal."
        f"</div>"
    )


def downstream_popup_html(props: dict[str, Any]) -> str:
    discharge = props.get("annual_discharge_m3s")
    runoff = props.get("annual_runoff_bcm")
    monsoon = props.get("monsoon_share_pct")
    dry_share = 100 - monsoon if isinstance(monsoon, (int, float)) else None
    impact_ratio = (monsoon / dry_share) if dry_share not in (None, 0) else None

    discharge_line = (
        f"<b>Indicative annual discharge:</b> {int(discharge):,} m3/s<br>" if isinstance(discharge, (int, float)) else ""
    )
    runoff_line = f"<b>Indicative annual runoff:</b> {runoff:.1f} BCM<br>" if isinstance(runoff, (int, float)) else ""
    season_line = (
        (
            f"<b>Monsoon share:</b> {monsoon:.0f}%<br>"
            f"<b>Dry-season share:</b> {dry_share:.0f}%<br>"
            f"<b>Monsoon:dry ratio:</b> {impact_ratio:.1f}x<br>"
        )
        if isinstance(monsoon, (int, float)) and isinstance(dry_share, (int, float))
        else ""
    )

    return (
        f"<div style='width:300px'>"
        f"<h4 style='margin:0 0 6px 0'>{html.escape(props['name'])}</h4>"
        f"<b>Downstream trunk:</b> {html.escape(props['downstream_name'])}<br>"
        f"<b>Basin:</b> {html.escape(props['basin'])}<br>"
        f"{discharge_line}"
        f"{runoff_line}"
        f"{season_line}"
        f"<b>Interpretation:</b> {html.escape(props['impact_note'])}"
        f"</div>"
    )


def hydropower_popup_html(row: dict[str, Any]) -> str:
    capacity = row.get("capacity_mw")
    capacity_line = f"{capacity:g} MW" if isinstance(capacity, (int, float)) else "Capacity not listed"
    municipality_line = (
        f"<b>Municipality:</b> {html.escape(row['municipality'])}<br>" if row.get("municipality") else ""
    )
    basis_line = (
        f"<b>Map location basis:</b> {html.escape(row['location_basis'])}<br>" if row.get("location_basis") else ""
    )
    precision_line = (
        f"<b>Precision tier:</b> {html.escape(row['precision_label'])}<br>" if row.get("precision_label") else ""
    )
    offset_m = row.get("display_offset_m")
    offset_line = (
        f"<b>Offset from raw registry point:</b> {offset_m:,.0f} m<br>"
        if isinstance(offset_m, (int, float)) and offset_m >= 1
        else ""
    )
    river_match_distance = row.get("nearest_river_distance_m")
    river_match_line = (
        f"<b>Nearest mapped river:</b> {html.escape(row['map_match_basis'])} (~{river_match_distance:,.0f} m)<br>"
        if row.get("map_match_basis") and isinstance(river_match_distance, (int, float))
        else ""
    )
    return (
        f"<div style='width:295px'>"
        f"<h4 style='margin:0 0 6px 0'>{html.escape(row['project'])}</h4>"
        f"<b>License stage:</b> {html.escape(row['license_type'])}<br>"
        f"<b>Capacity:</b> {capacity_line}<br>"
        f"{basis_line}"
        f"{precision_line}"
        f"{offset_line}"
        f"{river_match_line}"
        f"<b>River:</b> {html.escape(row['river'] or 'Unknown')}<br>"
        f"<b>District:</b> {html.escape(row['district'] or 'Unknown')}<br>"
        f"{municipality_line}"
        f"<b>Province:</b> {html.escape(row['province'] or 'Unknown')}<br>"
        f"<b>Promoter:</b> {html.escape(row['promoter'] or 'Unknown')}"
        f"</div>"
    )


def basin_popup_html(props: dict[str, Any]) -> str:
    area = props.get("upstream_area_km2")
    share = props.get("nepal_share_pct")
    monsoon = props.get("monsoon_share_pct")
    area_line = f"<b>Upstream basin area:</b> {area:,.0f} km²<br>" if isinstance(area, (int, float)) else ""
    share_line = f"<b>Approx. Nepal area share:</b> {share:.1f}%<br>" if isinstance(share, (int, float)) else ""
    monsoon_line = f"<b>Monsoon share:</b> {monsoon:.0f}%<br>" if isinstance(monsoon, (int, float)) else ""
    return (
        f"<div style='width:310px'>"
        f"<h4 style='margin:0 0 6px 0'>{html.escape(props['name'])}</h4>"
        f"<b>Type:</b> {html.escape(props['origin_group'])}<br>"
        f"<b>Control class:</b> {html.escape(props['control_class'])}<br>"
        f"{area_line}"
        f"{share_line}"
        f"{monsoon_line}"
        f"<b>Context:</b> {html.escape(props['note'])}"
        f"</div>"
    )


def callout_popup_html(props: dict[str, Any]) -> str:
    return basin_popup_html(props)


def add_rivers(
    m: folium.Map,
    tributaries: dict[str, Any],
    downstream_systems: dict[str, Any] | None = None,
    show_lines: bool = True,
    label_show: bool = True,
) -> None:
    basin_groups: dict[str, folium.FeatureGroup] = {
        basin: folium.FeatureGroup(name=f"{basin} tributaries", show=show_lines) for basin in BASIN_COLORS
    }
    major_label_group = folium.FeatureGroup(name="Major river labels", show=label_show)
    detail_label_group = folium.FeatureGroup(name="Detailed tributary labels", show=False)
    used_boxes: list[tuple[float, float, float, float]] = []
    placements: dict[str, dict[str, Any]] = {}

    sorted_features = sorted(tributaries["features"], key=lambda feature: river_label_priority(feature["properties"]), reverse=True)
    for feature in sorted_features:
        placement = choose_river_label_placement(feature, used_boxes)
        if placement is None:
            continue
        placements[feature["properties"]["id"]] = placement
        used_boxes.append(placement["bbox"])

    for feature in tributaries["features"]:
        props = feature["properties"]
        basin = props["basin"]
        color = BASIN_COLORS[basin]
        weight = 4 if props["parent"] is None else 3
        folium.GeoJson(
            feature,
            style_function=lambda _, color=color, weight=weight: {
                "color": color,
                "weight": weight,
                "opacity": 0.95,
            },
            tooltip=folium.GeoJsonTooltip(fields=["name", "basin"], aliases=["River", "Basin"]),
            popup=folium.Popup(river_popup_html(props), max_width=320),
        ).add_to(basin_groups[basin])

        placement = placements.get(props["id"])
        if placement:
            label_group = major_label_group if props["id"] in MAJOR_LABEL_IDS else detail_label_group
            folium.Marker(
                location=[placement["lat"], placement["lon"]],
                icon=build_label_icon(placement["text"], "#1f1f1f", placement["dx"], placement["dy"]),
            ).add_to(label_group)

    if downstream_systems:
        for feature in downstream_systems["features"]:
            props = feature["properties"]
            basin = props["basin"]
            if basin not in basin_groups:
                continue
            color = BASIN_COLORS[basin]
            folium.GeoJson(
                feature,
                style_function=lambda _, color=color: {
                    "color": color,
                    "weight": 4.8,
                    "opacity": 0.78,
                },
                tooltip=folium.GeoJsonTooltip(fields=["name", "downstream_name"], aliases=["System", "Downstream trunk"]),
                popup=folium.Popup(downstream_popup_html(props), max_width=320),
            ).add_to(basin_groups[basin])

    for group in basin_groups.values():
        group.add_to(m)
    major_label_group.add_to(m)
    detail_label_group.add_to(m)


def add_india_reference_rivers(
    m: folium.Map,
    india_rivers: dict[str, Any],
    show_lines: bool = False,
    show_labels: bool = False,
) -> None:
    group = folium.FeatureGroup(name="Northern Gangetic plains rivers", show=show_lines)
    label_group = folium.FeatureGroup(name="Northern plains river labels", show=show_labels)
    for feature in india_rivers["features"]:
        props = feature["properties"]
        folium.GeoJson(
            feature,
            style_function=lambda _: {
                "color": "#6b7280",
                "weight": 2.4,
                "opacity": 0.8,
            },
            tooltip=folium.GeoJsonTooltip(fields=["name"], aliases=["River"]),
            popup=folium.Popup(india_river_popup_html(props), max_width=300),
        ).add_to(group)
        folium.Marker(
            location=[props["label_lat"], props["label_lon"]],
            icon=folium.DivIcon(
                html=(
                    "<div style=\"font-size:10px;font-weight:700;color:#374151;"
                    "text-shadow:0 0 2px white, 0 0 5px white;white-space:nowrap;\">"
                    f"{html.escape(props['name'])}</div>"
                )
            ),
        ).add_to(label_group)
    group.add_to(m)
    label_group.add_to(m)


def add_downstream_systems(
    m: folium.Map,
    downstream_systems: dict[str, Any],
    hydrology_markers: dict[str, Any],
    show_systems: bool = True,
    show_impact_markers: bool = True,
) -> None:
    system_group = folium.FeatureGroup(name="Nepal-origin downstream systems", show=show_systems)
    label_group = folium.FeatureGroup(name="Downstream system labels", show=False)
    monsoon_group = folium.FeatureGroup(name="Monsoon dominance overlay", show=False)
    dry_group = folium.FeatureGroup(name="Dry-season share overlay", show=False)
    impact_group = folium.FeatureGroup(name="Downstream impact markers", show=show_impact_markers)

    marker_lookup = {
        feature["properties"]["id"]: feature["properties"] | {"coordinates": feature["geometry"]["coordinates"]}
        for feature in hydrology_markers["features"]
    }

    for feature in downstream_systems["features"]:
        props = feature["properties"]
        color = BASIN_COLORS[props["basin"]]
        monsoon = props.get("monsoon_share_pct") or 0
        dry_share = max(0, 100 - monsoon)
        impact_ratio = (monsoon / dry_share) if dry_share else None
        discharge = props.get("annual_discharge_m3s") or 0
        monsoon_weight = max(3.5, min(8.0, monsoon / 12))
        dry_weight = max(2.0, min(5.5, dry_share / 6))

        folium.GeoJson(
            feature,
            style_function=lambda _, color=color: {
                "color": color,
                "weight": 4.8,
                "opacity": 0.95,
            },
            tooltip=folium.GeoJsonTooltip(fields=["name", "downstream_name"], aliases=["System", "Downstream trunk"]),
            popup=folium.Popup(downstream_popup_html(props), max_width=320),
        ).add_to(system_group)

        folium.GeoJson(
            feature,
            style_function=lambda _, weight=monsoon_weight: {
                "color": "#ef4444",
                "weight": weight,
                "opacity": 0.55,
                "dashArray": "8 6",
            },
            tooltip=(
                f"{props['name']}: monsoon share {monsoon:.0f}% "
                f"({'n/a' if impact_ratio is None else f'{impact_ratio:.1f}x dry-season share'})"
            ),
            popup=folium.Popup(downstream_popup_html(props), max_width=320),
        ).add_to(monsoon_group)

        folium.GeoJson(
            feature,
            style_function=lambda _, weight=dry_weight: {
                "color": "#0f766e",
                "weight": weight,
                "opacity": 0.75,
                "dashArray": "4 8",
            },
            tooltip=f"{props['name']}: dry-season share {dry_share:.0f}%",
            popup=folium.Popup(downstream_popup_html(props), max_width=320),
        ).add_to(dry_group)

        folium.Marker(
            location=[props["label_lat"], props["label_lon"]],
            icon=folium.DivIcon(
                html=(
                    "<div style=\"font-size:10px;font-weight:700;color:#111827;"
                    "text-shadow:0 0 2px white, 0 0 6px white;white-space:nowrap;\">"
                    f"{html.escape(props['downstream_name'])}</div>"
                )
            ),
        ).add_to(label_group)

        marker = marker_lookup.get(props["id"])
        if marker:
            marker_radius = max(5, min(13, math.sqrt(discharge) / 4)) if discharge else 5
            tooltip_text = (
                f"{props['name']} | {int(discharge):,} m3/s | monsoon {monsoon:.0f}%"
                if discharge
                else f"{props['name']} | monsoon {monsoon:.0f}%"
            )
            folium.CircleMarker(
                location=[marker["coordinates"][1], marker["coordinates"][0]],
                radius=marker_radius,
                color=color,
                weight=2,
                fill=True,
                fill_color=color,
                fill_opacity=0.85,
                tooltip=tooltip_text,
                popup=folium.Popup(downstream_popup_html(props), max_width=320),
            ).add_to(impact_group)

    system_group.add_to(m)
    label_group.add_to(m)
    monsoon_group.add_to(m)
    dry_group.add_to(m)
    impact_group.add_to(m)


def add_basin_polygons(
    m: folium.Map,
    nepal_basins: dict[str, Any],
    comparison_basins: dict[str, Any],
    callouts: dict[str, Any],
    show_polygons: bool = False,
    show_callouts: bool = False,
) -> None:
    nepal_group = folium.FeatureGroup(name="Nepal-linked basin polygons", show=show_polygons)
    comparison_group = folium.FeatureGroup(name="India-origin comparison basins", show=show_polygons)
    callout_group = folium.FeatureGroup(name="Origin comparison callouts", show=show_callouts)

    for feature in nepal_basins["features"]:
        props = feature["properties"]
        color = BASIN_COLORS[props["basin"]]
        folium.GeoJson(
            feature,
            style_function=lambda _, color=color: {
                "color": color,
                "weight": 1.6,
                "fillColor": color,
                "fillOpacity": 0.12,
            },
            tooltip=folium.GeoJsonTooltip(fields=["name", "control_class"], aliases=["Basin", "Control"]),
            popup=folium.Popup(basin_popup_html(props), max_width=330),
        ).add_to(nepal_group)

    for feature in comparison_basins["features"]:
        props = feature["properties"]
        folium.GeoJson(
            feature,
            style_function=lambda _: {
                "color": "#475569",
                "weight": 1.4,
                "fillColor": "#94a3b8",
                "fillOpacity": 0.10,
            },
            tooltip=folium.GeoJsonTooltip(fields=["name", "control_class"], aliases=["Basin", "Control"]),
            popup=folium.Popup(basin_popup_html(props), max_width=330),
        ).add_to(comparison_group)

    for feature in callouts["features"]:
        props = feature["properties"]
        lon, lat = feature["geometry"]["coordinates"]
        color = BASIN_COLORS.get(props.get("basin"), "#475569")
        if props["origin_group"] == "India-origin comparison":
            color = "#475569"
        label = props["name"].replace(" Basin", "").replace(" System", "")
        folium.CircleMarker(
            location=[lat, lon],
            radius=7,
            color=color,
            weight=2,
            fill=True,
            fill_color=color,
            fill_opacity=0.9,
            tooltip=f"{label} | {props['control_class']}",
            popup=folium.Popup(callout_popup_html(props), max_width=330),
        ).add_to(callout_group)
        folium.Marker(
            location=[lat, lon],
            icon=build_label_icon(label, "#111827", 10, -16, font_size=9),
        ).add_to(callout_group)

    nepal_group.add_to(m)
    comparison_group.add_to(m)
    callout_group.add_to(m)


def add_ganga_receiver_trunk(m: folium.Map, india_rivers: dict[str, Any], show: bool = True) -> None:
    river_lookup = features_by_id(india_rivers)
    ganga = river_lookup.get("ganga")
    if not ganga:
        return
    group = folium.FeatureGroup(name="Ganga receiver trunk", show=show)
    props = ganga["properties"]
    folium.GeoJson(
        ganga,
        style_function=lambda _: {
            "color": "#111827",
            "weight": 3.6,
            "opacity": 0.9,
            "dashArray": "10 6",
        },
        tooltip="Ganga receiver trunk",
        popup=folium.Popup(india_river_popup_html(props), max_width=300),
    ).add_to(group)
    folium.Marker(
        location=[props["label_lat"], props["label_lon"]],
        icon=build_label_icon("Ganga receiver trunk", "#111827", 8, -12, font_size=10),
    ).add_to(group)
    group.add_to(m)


def add_hydropower_overlay(
    m: folium.Map,
    projects: list[dict[str, Any]],
    show_sites: bool = False,
    show_references: bool = False,
    show_raw_references: bool = False,
) -> None:
    site_group = plugins.MarkerCluster(name="Hydropower sites (higher confidence)", show=show_sites)
    river_reference_group = plugins.MarkerCluster(
        name="Hydropower projects (river-aligned references)", show=show_references
    )
    raw_reference_group = plugins.MarkerCluster(
        name="Hydropower projects (raw registry references)", show=show_raw_references
    )
    offset_group = folium.FeatureGroup(name="Hydropower raw-vs-display offsets", show=False)
    for row in projects:
        capacity = row.get("capacity_mw")
        color = LICENSE_COLORS.get(row["license_type"], "#7c3aed")
        radius = 4.5
        if isinstance(capacity, (int, float)) and capacity > 0:
            radius = max(4.5, min(10.5, math.sqrt(capacity) * 0.85))
        style = PROJECT_PRECISION_STYLES[row.get("precision_tier", "raw_reference")]
        radius *= style["radius_scale"]
        location = [row.get("display_lat", row["lat"]), row.get("display_lon", row["lon"])]
        tooltip = f"{row['project']} | {row['license_type']} | {row.get('precision_label', 'Project point')}"
        target_group = raw_reference_group
        if row.get("precision_tier") == "site":
            target_group = site_group
        elif row.get("precision_tier") == "river_reference":
            target_group = river_reference_group
        folium.CircleMarker(
            location=location,
            radius=radius,
            color=color,
            weight=style["weight"],
            fill=True,
            fill_color=color,
            fill_opacity=style["fill_opacity"],
            tooltip=tooltip,
            popup=folium.Popup(hydropower_popup_html(row), max_width=320),
        ).add_to(target_group)

        offset_m = row.get("display_offset_m")
        if (
            row.get("precision_tier") == "river_reference"
            and isinstance(offset_m, (int, float))
            and offset_m >= PROJECT_OFFSET_LINE_MIN_M
        ):
            folium.PolyLine(
                locations=[[row["raw_lat"], row["raw_lon"]], [row["display_lat"], row["display_lon"]]],
                color="#64748b",
                weight=1.2,
                opacity=0.45,
                dash_array="4 6",
                tooltip=f"{row['project']} offset from raw registry point",
            ).add_to(offset_group)

    site_group.add_to(m)
    river_reference_group.add_to(m)
    raw_reference_group.add_to(m)
    offset_group.add_to(m)


def add_layout_enhancements(m: folium.Map, title_html: str, body_html: str) -> None:
    plugins.Fullscreen().add_to(m)
    plugins.MeasureControl(position="topleft", primary_length_unit="kilometers").add_to(m)
    plugins.MousePosition(position="bottomright").add_to(m)
    legend_html = f"""
    <div style="
        position: fixed;
        top: 12px; left: 60px; z-index: 9999;
        background: rgba(255,255,255,0.92);
        padding: 12px 14px;
        border: 1px solid #bbb;
        border-radius: 8px;
        max-width: 400px;
        font-family: Arial, sans-serif;
        box-shadow: 0 1px 8px rgba(0,0,0,0.18);
    ">
      {title_html}
      <div style="font-size:12px; line-height:1.45; margin-top:6px;">{body_html}</div>
      <div style="font-size:11px; line-height:1.45; margin-top:8px;">
        Basin colors: Koshi <span style="color:{BASIN_COLORS['Koshi']};font-weight:700;">&#9632;</span>,
        Gandaki <span style="color:{BASIN_COLORS['Gandaki']};font-weight:700;">&#9632;</span>,
        Karnali <span style="color:{BASIN_COLORS['Karnali']};font-weight:700;">&#9632;</span>,
        Mahakali <span style="color:{BASIN_COLORS['Mahakali']};font-weight:700;">&#9632;</span>,
        Medium basins <span style="color:{BASIN_COLORS['Medium basins']};font-weight:700;">&#9632;</span>.
      </div>
      <div style="font-size:11px; line-height:1.4; margin-top:8px;">
        Grey-blue basin polygons = India-origin comparison basins with no meaningful Nepal-origin control.
      </div>
      <div style="font-size:11px; line-height:1.4; margin-top:8px;">
        License colors: Operation <span style="color:{LICENSE_COLORS['Operation']};font-weight:700;">&#9632;</span>,
        Generation <span style="color:{LICENSE_COLORS['Generation']};font-weight:700;">&#9632;</span>,
        Survey <span style="color:{LICENSE_COLORS['Survey']};font-weight:700;">&#9632;</span>.
      </div>
      <div style="font-size:11px; line-height:1.4; margin-top:8px;">
        Marker precision: solid = higher-confidence site point, semi-filled = river-aligned reference,
        faint = raw registry reference. Dashed grey offsets show where snapped display anchors differ from the raw registry point.
      </div>
      <div style="font-size:11px; line-height:1.4; margin-top:8px;">
        Power-node status colors: Operational <span style="color:{GRID_STATUS_STYLES['Operational']['color']};font-weight:700;">&#9632;</span>,
        Under construction <span style="color:{GRID_STATUS_STYLES['Under construction']['color']};font-weight:700;">&#9632;</span>,
        Implementation setup <span style="color:{GRID_STATUS_STYLES['Implementation setup']['color']};font-weight:700;">&#9632;</span>,
        Planned <span style="color:{GRID_STATUS_STYLES['Planned']['color']};font-weight:700;">&#9632;</span>.
      </div>
      <div style="font-size:11px; line-height:1.4; margin-top:8px;">
        Transmission is drawn as a neutral dashed network overlay; hubs use circle nodes and cross-border gateways use diamond nodes.
      </div>
      <div style="font-size:11px; line-height:1.4; margin-top:8px;">
        Sources: Open Knowledge Nepal boundaries, Geofabrik / OpenStreetMap waterways, Nominatim river geometries,
        Naxa / DoED-linked hydropower project data, NEA transmission inventories, MCA-Nepal alignment maps,
        and official Nepal-India power-trade source documents.
      </div>
    </div>
    """
    m.get_root().html.add_child(folium.Element(legend_html))


def make_explorer_map(
    provinces: dict[str, Any],
    country: dict[str, Any],
    tributaries: dict[str, Any],
    india_rivers: dict[str, Any],
    downstream_systems: dict[str, Any],
    hydrology_markers: dict[str, Any],
    nepal_basins: dict[str, Any],
    comparison_basins: dict[str, Any],
    callouts: dict[str, Any],
    basin_annotations: dict[str, Any],
    top_project_annotations: dict[str, Any],
    priority_watchlist: dict[str, Any],
    storage_annotations: dict[str, Any],
    place_anchors: dict[str, dict[str, Any]],
    transmission_corridors: dict[str, Any],
    interconnections: dict[str, Any],
    projects: list[dict[str, Any]],
    include_hydro: bool,
    out_path: Path,
    title: str,
) -> None:
    m = folium.Map(
        location=[28.3, 84.1],
        zoom_start=MAP_ZOOM,
        control_scale=True,
        tiles=None,
    )
    add_base_layers(m)
    add_boundaries(m, provinces, country)
    add_rivers(m, tributaries, downstream_systems=downstream_systems, show_lines=True, label_show=True)
    add_india_reference_rivers(m, india_rivers, show_lines=False, show_labels=False)
    add_downstream_systems(m, downstream_systems, hydrology_markers, show_systems=True, show_impact_markers=True)
    add_basin_polygons(m, nepal_basins, comparison_basins, callouts, show_polygons=False, show_callouts=False)
    add_annotation_layer(m, basin_annotations, "Basin seasonality annotations", show=False)
    add_annotation_layer(m, priority_watchlist, "Priority projects + radar surveys", show=False)
    add_annotation_layer(m, storage_annotations, "Storage shortlist annotations", show=False)
    add_transmission_corridors(m, transmission_corridors, show_lines=False, show_labels=False)
    add_transmission_nodes(m, place_anchors, show_nodes=False, show_labels=False)
    add_cross_border_interconnections(m, interconnections, show_points=False, show_labels=False)
    if include_hydro:
        add_hydropower_overlay(m, projects, show_sites=False, show_references=False, show_raw_references=False)
        add_annotation_layer(m, top_project_annotations, "Top capacity projects (top 10 MW)", show=False)

    title_html = f"<div style='font-size:18px;font-weight:700'>{title}</div>"
    body_html = (
        "Nepal tributaries, northern Gangetic comparison rivers, basin polygons, and cross-border downstream "
        "systems are combined here. Basin seasonality labels, the curated priority/radar project watchlist, storage "
        "shortlist annotations, transmission corridors, India interconnection nodes, and top-capacity project labels "
        "can be switched on as separate interpretation layers when you want more than the base river geometry."
    )
    add_layout_enhancements(m, title_html, body_html)
    folium.LayerControl(collapsed=False).add_to(m)
    m.fit_bounds([[24.2, 78.0], [31.3, 89.5]])
    out_path.write_text(m.get_root().render())


def make_geopolitics_map(
    provinces: dict[str, Any],
    country: dict[str, Any],
    tributaries: dict[str, Any],
    india_rivers: dict[str, Any],
    downstream_systems: dict[str, Any],
    hydrology_markers: dict[str, Any],
    nepal_basins: dict[str, Any],
    comparison_basins: dict[str, Any],
    callouts: dict[str, Any],
    basin_annotations: dict[str, Any],
    priority_watchlist: dict[str, Any],
    storage_annotations: dict[str, Any],
    place_anchors: dict[str, dict[str, Any]],
    transmission_corridors: dict[str, Any],
    interconnections: dict[str, Any],
    out_path: Path,
) -> None:
    m = folium.Map(
        location=[27.2, 83.8],
        zoom_start=MAP_ZOOM,
        control_scale=True,
        tiles=None,
    )
    add_base_layers(m)
    add_boundaries(m, provinces, country)
    add_rivers(m, tributaries, downstream_systems=downstream_systems, show_lines=True, label_show=True)
    add_india_reference_rivers(m, india_rivers, show_lines=False, show_labels=False)
    add_downstream_systems(m, downstream_systems, hydrology_markers, show_systems=True, show_impact_markers=True)
    add_basin_polygons(m, nepal_basins, comparison_basins, callouts, show_polygons=True, show_callouts=True)
    add_annotation_layer(m, basin_annotations, "Basin seasonality annotations", show=False)
    add_annotation_layer(m, priority_watchlist, "Priority projects + radar surveys", show=False)
    add_annotation_layer(m, storage_annotations, "Storage shortlist annotations", show=False)
    add_transmission_corridors(m, transmission_corridors, show_lines=False, show_labels=False)
    add_transmission_nodes(m, place_anchors, show_nodes=False, show_labels=False)
    add_cross_border_interconnections(m, interconnections, show_points=False, show_labels=False)
    add_ganga_receiver_trunk(m, india_rivers, show=True)

    title_html = "<div style='font-size:18px;font-weight:700'>Nepal River Geopolitics Explorer</div>"
    body_html = (
        "This view asks a narrower question: which Gangetic-plain river systems are materially routed through Nepal, "
        "which are not, and how much of each upstream basin lies inside Nepal's borders. Nepal-linked basin polygons, "
        "India-origin comparison basins, and origin/control callouts are on by default; the curated priority/radar "
        "project watchlist stays available as optional context alongside the broader power-system layers."
    )
    add_layout_enhancements(m, title_html, body_html)
    folium.LayerControl(collapsed=False).add_to(m)
    m.fit_bounds([[GEOPOLITICS_BOUNDS[1], GEOPOLITICS_BOUNDS[0]], [GEOPOLITICS_BOUNDS[3], GEOPOLITICS_BOUNDS[2]]])
    out_path.write_text(m.get_root().render())


def make_power_system_map(
    provinces: dict[str, Any],
    country: dict[str, Any],
    tributaries: dict[str, Any],
    india_rivers: dict[str, Any],
    downstream_systems: dict[str, Any],
    hydrology_markers: dict[str, Any],
    basin_annotations: dict[str, Any],
    top_project_annotations: dict[str, Any],
    priority_watchlist: dict[str, Any],
    storage_annotations: dict[str, Any],
    place_anchors: dict[str, dict[str, Any]],
    transmission_corridors: dict[str, Any],
    traced_network: dict[str, Any] | None,
    interconnections: dict[str, Any],
    cross_border_lines: dict[str, Any] | None,
    projects: list[dict[str, Any]],
    out_path: Path,
) -> None:
    m = folium.Map(
        location=[28.1, 84.6],
        zoom_start=MAP_ZOOM,
        control_scale=True,
        tiles=None,
    )
    add_base_layers(m)
    add_boundaries(m, provinces, country)
    add_rivers(m, tributaries, downstream_systems=downstream_systems, show_lines=False, label_show=False)
    add_india_reference_rivers(m, india_rivers, show_lines=False, show_labels=False)
    add_downstream_systems(m, downstream_systems, hydrology_markers, show_systems=False, show_impact_markers=False)
    add_annotation_layer(m, basin_annotations, "Basin seasonality annotations", show=False)
    add_annotation_layer(m, priority_watchlist, "Priority projects + radar surveys", show=True)
    add_annotation_layer(m, storage_annotations, "Storage shortlist annotations", show=True)
    add_transmission_corridors(
        m,
        transmission_corridors,
        show_lines=False,
        show_labels=True,
        min_label_voltage_kv=220,
    )
    add_connected_transmission_network(m, traced_network, show_lines=True, show_labels=False)
    add_transmission_nodes(m, place_anchors, show_nodes=True, show_labels=False)
    add_cross_border_interconnection_lines(m, cross_border_lines, show_lines=True)
    add_cross_border_interconnections(m, interconnections, show_points=True, show_labels=False)
    add_hydropower_overlay(m, projects, show_sites=True, show_references=True, show_raw_references=False)
    add_annotation_layer(m, top_project_annotations, "Top capacity projects (top 10 MW)", show=False)

    title_html = "<div style='font-size:18px;font-weight:700'>Nepal Power System Explorer</div>"
    body_html = (
        "This view makes the grid the main subject. The major transmission network, grid hubs and substations, cross-border "
        "gateways and conservative cross-border links, the priority/radar project watchlist, and storage shortlist markers "
        "are on first; river layers remain available but start muted. Source trace fragments and QA gaps stay available as "
        "audit layers."
    )
    add_layout_enhancements(m, title_html, body_html)
    folium.LayerControl(collapsed=False).add_to(m)
    m.fit_bounds([[25.4, 80.5], [30.6, 88.6]])
    out_path.write_text(m.get_root().render())


def main() -> None:
    PROCESSED.mkdir(parents=True, exist_ok=True)
    DOCS.mkdir(parents=True, exist_ok=True)

    provinces = read_geojson(RAW / "maps" / "nepal_provinces.geojson")
    country = build_country_outline(provinces)
    projects = load_projects()
    tributaries, qa_report, compatibility_report = fetch_tributaries(projects)
    projects, project_anchor_report = build_project_display_anchors(projects, tributaries)
    india_rivers, india_report = fetch_nominatim_lines(INDIA_REFERENCE_RIVERS)
    downstream_systems, hydrology_markers = build_downstream_systems(tributaries, india_rivers)
    nepal_basins, comparison_basins, callouts = build_basin_polygons(country, downstream_systems, india_rivers)
    basin_annotations, basin_annotation_report = build_basin_seasonality_annotations(tributaries)
    top_project_annotations = build_top_capacity_project_annotations(projects)
    storage_annotations, storage_annotation_report = build_storage_shortlist_annotations(projects, tributaries)
    priority_watchlist, priority_watchlist_report = build_priority_project_watchlist(projects, storage_annotations)
    place_anchors, place_anchor_report = build_place_anchor_index()
    transmission_corridors, transmission_report = build_transmission_corridors(place_anchors)
    traced_corridors = read_geojson_if_exists(TRACED_SEGMENTS_PATH)
    traced_network = read_geojson_if_exists(TRACED_NETWORK_PATH)
    cross_border_lines = read_geojson_if_exists(CROSS_BORDER_LINES_PATH)
    trace_gaps = read_geojson_if_exists(TRACE_GAP_PATH)
    interconnections, interconnection_report = build_cross_border_interconnections(place_anchors)

    (PROCESSED / "nepal_relevant_tributaries.geojson").write_text(json.dumps(tributaries))
    RIVER_NETWORK_QA_REPORT_PATH.write_text(json.dumps(qa_report, indent=2))
    (PROCESSED / "tributary_fetch_report.json").write_text(json.dumps(compatibility_report, indent=2))
    (PROCESSED / "nepal_country_outline.geojson").write_text(json.dumps(country))
    (PROCESSED / "india_reference_rivers.geojson").write_text(json.dumps(india_rivers))
    (PROCESSED / "india_reference_rivers_report.json").write_text(json.dumps(india_report, indent=2))
    (PROCESSED / "nepal_origin_downstream_systems.geojson").write_text(json.dumps(downstream_systems))
    (PROCESSED / "downstream_hydrology_markers.geojson").write_text(json.dumps(hydrology_markers))
    (PROCESSED / "hydropower_project_display_points.geojson").write_text(json.dumps(hydropower_display_points_geojson(projects)))
    (PROCESSED / "hydropower_project_anchor_report.json").write_text(json.dumps(project_anchor_report, indent=2))
    (PROCESSED / "nepal_linked_basin_polygons.geojson").write_text(json.dumps(nepal_basins))
    (PROCESSED / "india_comparison_basin_polygons.geojson").write_text(json.dumps(comparison_basins))
    (PROCESSED / "river_influence_callouts.geojson").write_text(json.dumps(callouts))
    (PROCESSED / "basin_seasonality_annotations.geojson").write_text(json.dumps(basin_annotations))
    (PROCESSED / "top_capacity_project_annotations.geojson").write_text(json.dumps(top_project_annotations))
    (PROCESSED / "priority_project_watchlist.geojson").write_text(json.dumps(priority_watchlist))
    (PROCESSED / "storage_shortlist_annotations.geojson").write_text(json.dumps(storage_annotations))
    (PROCESSED / "place_anchor_index.geojson").write_text(
        json.dumps(
            {
                "type": "FeatureCollection",
                "features": [
                    {
                        "type": "Feature",
                        "properties": {
                            "id": anchor["id"],
                            "label": anchor["label"],
                            "display_name": anchor["display_name"],
                            "query": anchor["query"],
                            "basis": anchor["basis"],
                        },
                        "geometry": {"type": "Point", "coordinates": [anchor["lon"], anchor["lat"]]},
                    }
                    for anchor in place_anchors.values()
                ],
            }
        )
    )
    (PROCESSED / "transmission_corridors.geojson").write_text(json.dumps(transmission_corridors))
    (PROCESSED / "cross_border_interconnections.geojson").write_text(json.dumps(interconnections))
    (PROCESSED / "annotation_build_report.json").write_text(
        json.dumps(
            {
                "basin_seasonality": {
                    "feature_count": len(basin_annotations["features"]),
                    "skipped": basin_annotation_report["skipped"],
                },
                "top_capacity_projects": {
                    "feature_count": len(top_project_annotations["features"]),
                    "limit": TOP_PROJECT_LIMIT,
                },
                "priority_watchlist": {
                    "feature_count": len(priority_watchlist["features"]),
                    "skipped": priority_watchlist_report["skipped"],
                },
                "storage_shortlist": {
                    "feature_count": len(storage_annotations["features"]),
                    "skipped": storage_annotation_report["skipped"],
                },
            },
            indent=2,
        )
    )
    (PROCESSED / "power_system_build_report.json").write_text(
        json.dumps(
            {
                "place_anchors": {
                    "feature_count": len(place_anchors),
                    "matches": place_anchor_report,
                },
                "transmission_corridors": {
                    "feature_count": len(transmission_corridors["features"]),
                    "skipped": transmission_report["skipped"],
                },
                "cross_border_interconnections": {
                    "feature_count": len(interconnections["features"]),
                    "skipped": interconnection_report["skipped"],
                },
                "priority_watchlist": {
                    "feature_count": len(priority_watchlist["features"]),
                    "skipped": priority_watchlist_report["skipped"],
                },
                "hydropower_project_anchors": project_anchor_report,
                "traced_transmission_segments": {
                    "feature_count": len(traced_corridors["features"]) if traced_corridors else 0,
                    "path": str(TRACED_SEGMENTS_PATH),
                },
                "connected_transmission_network": {
                    "feature_count": len(traced_network["features"]) if traced_network else 0,
                    "path": str(TRACED_NETWORK_PATH),
                },
                "cross_border_interconnection_lines": {
                    "feature_count": len(cross_border_lines["features"]) if cross_border_lines else 0,
                    "path": str(CROSS_BORDER_LINES_PATH),
                },
                "transmission_trace_gaps": {
                    "feature_count": len(trace_gaps["features"]) if trace_gaps else 0,
                    "path": str(TRACE_GAP_PATH),
                },
            },
            indent=2,
        )
    )

    make_explorer_map(
        provinces,
        country,
        tributaries,
        india_rivers,
        downstream_systems,
        hydrology_markers,
        nepal_basins,
        comparison_basins,
        callouts,
        basin_annotations,
        top_project_annotations,
        priority_watchlist,
        storage_annotations,
        place_anchors,
        transmission_corridors,
        interconnections,
        projects,
        include_hydro=True,
        out_path=DOCS / "nepal_tributary_explorer.html",
        title="Nepal Cross-Border Tributary Explorer",
    )
    make_explorer_map(
        provinces,
        country,
        tributaries,
        india_rivers,
        downstream_systems,
        hydrology_markers,
        nepal_basins,
        comparison_basins,
        callouts,
        basin_annotations,
        top_project_annotations,
        priority_watchlist,
        storage_annotations,
        place_anchors,
        transmission_corridors,
        interconnections,
        projects,
        include_hydro=False,
        out_path=DOCS / "nepal_tributary_network.html",
        title="Nepal Cross-Border Tributary Network",
    )
    make_geopolitics_map(
        provinces,
        country,
        tributaries,
        india_rivers,
        downstream_systems,
        hydrology_markers,
        nepal_basins,
        comparison_basins,
        callouts,
        basin_annotations,
        priority_watchlist,
        storage_annotations,
        place_anchors,
        transmission_corridors,
        interconnections,
        out_path=DOCS / "nepal_geopolitics_river_influence.html",
    )
    make_power_system_map(
        provinces,
        country,
        tributaries,
        india_rivers,
        downstream_systems,
        hydrology_markers,
        basin_annotations,
        top_project_annotations,
        priority_watchlist,
        storage_annotations,
        place_anchors,
        transmission_corridors,
        traced_network,
        interconnections,
        cross_border_lines,
        projects,
        out_path=DOCS / "nepal_power_system_explorer.html",
    )


if __name__ == "__main__":
    main()
