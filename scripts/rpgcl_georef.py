"""Shared georeference for the RPGCL "Nepal Power Transmission Network Map" GeoPDF.

The GeoPDF carries one ISO 32000 geospatial viewport per map frame (``/VP``):

* ``/BBox`` is in PDF user space (origin bottom-left, y up), written as
  ``[x1, y1, x2, y2]`` with ``y1`` > ``y2`` for this file.
* ``/Measure /LPTS`` = ``[0,1, 0,0, 1,0, 1,1]`` are unit coordinates relative to
  ``(x1, y1)``-``(x2, y2)``; ``/GPTS`` give the matching (lat, lon) pairs.
* ``/Measure /GCS /WKT`` is the frame's projected CRS (MUTM, Transverse Mercator).

PyMuPDF (fitz) reports text and drawings in a y-down page space, so every BBox
must be flipped with the page height before it is compared with fitz
coordinates, and the frame is a rectangle in *projected* metres, so the
unit -> ground mapping is an affine fit in that CRS (not a bilinear blend of
latitude/longitude).

An earlier implementation in ``extract_rpgcl_transmission_vectors.py`` skipped
the y flip (a 30 pt ≈ 6 km shift on this sheet) and interpolated in lat/lon,
placing derived features roughly 7-14 km south of their true positions and
mis-locating the inset-frame exclusion box. Both scripts now use this module.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Callable


def load_viewports(pdf_path: Path) -> tuple[dict[str, dict[str, Any]], float]:
    """Return ({viewport_name: {bbox, gpts, wkt}}, page_height) for page 1."""
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
    return viewports, page_height


def fitz_frame(bbox: list[float], page_height: float) -> tuple[float, float, float, float]:
    """Convert a PDF-user-space viewport BBox to a fitz (y-down) (x0, y0, x1, y1) box."""
    x1, y1, x2, y2 = bbox
    return (min(x1, x2), page_height - max(y1, y2), max(x1, x2), page_height - min(y1, y2))


def in_frame(x: float, y: float, frame: tuple[float, float, float, float]) -> bool:
    return frame[0] <= x <= frame[2] and frame[1] <= y <= frame[3]


def _tm_transformer(wkt: str):
    from pyproj import CRS, Transformer

    crs = CRS.from_wkt(wkt)
    geog = crs.geodetic_crs
    fwd = Transformer.from_crs(geog, crs, always_xy=True)
    inv = Transformer.from_crs(crs, geog, always_xy=True)
    return fwd, inv


def georef_factory(
    bbox: list[float], gpts: list[float], wkt: str, page_height: float
) -> Callable[[float, float], tuple[float, float]]:
    """Return f(x_fitz, y_fitz) -> (lon, lat) for one GeoPDF viewport.

    An affine fit from LPTS unit coordinates to projected metres is solved by
    least squares over the four GPTS corners, then inverted to geographic
    coordinates with the viewport's own CRS.
    """
    import numpy as np

    fwd, inv = _tm_transformer(wkt)
    x1, y1, x2, y2 = bbox
    lpts = [(0, 1), (0, 0), (1, 0), (1, 1)]
    rows, east, north = [], [], []
    for (u, v), (lat, lon) in zip(lpts, zip(gpts[0::2], gpts[1::2])):
        e, n = fwd.transform(lon, lat)
        rows.append([u, v, 1.0])
        east.append(e)
        north.append(n)
    a = np.array(rows)
    ce, *_ = np.linalg.lstsq(a, np.array(east), rcond=None)
    cn, *_ = np.linalg.lstsq(a, np.array(north), rcond=None)

    def to_geo(x: float, y_fitz: float) -> tuple[float, float]:
        y_pdf = page_height - y_fitz
        u = (x - x1) / (x2 - x1)
        v = (y_pdf - y1) / (y2 - y1)
        e = ce[0] * u + ce[1] * v + ce[2]
        n = cn[0] * u + cn[1] * v + cn[2]
        lon, lat = inv.transform(e, n)
        return float(lon), float(lat)

    return to_geo


def legacy_point_to_geo_factory(bbox: list[float], gpts: list[float]) -> Callable[[float, float], tuple[float, float]]:
    """The superseded (biased) mapping, kept only to correct values derived from it.

    It treated the PDF-user-space BBox as fitz coordinates (no y flip) and
    blended latitude/longitude bilinearly between the GPTS corners.
    """
    left, bottom, right, top = bbox
    g = gpts
    top_left, top_right, bottom_right, bottom_left = (g[2], g[3]), (g[4], g[5]), (g[6], g[7]), (g[0], g[1])

    def point_to_geo(x: float, y: float) -> tuple[float, float]:
        u = (x - left) / (right - left)
        v = (y - top) / (bottom - top)
        lat = (1 - u) * (1 - v) * top_left[0] + u * (1 - v) * top_right[0] + u * v * bottom_right[0] + (1 - u) * v * bottom_left[0]
        lon = (1 - u) * (1 - v) * top_left[1] + u * (1 - v) * top_right[1] + u * v * bottom_right[1] + (1 - u) * v * bottom_left[1]
        return lon, lat

    return point_to_geo


def legacy_correction_factory(pdf_path: Path, viewport_name: str = "Layers") -> Callable[[float, float], tuple[float, float]]:
    """Return f(lon, lat) that maps a coordinate produced by the legacy mapping to the corrected one.

    The legacy page -> geo mapping is inverted by Newton iteration to recover the
    original page position, which is then georeferenced correctly.
    """
    viewports, page_height = load_viewports(pdf_path)
    return legacy_correction_from_viewport(viewports[viewport_name], page_height)


def legacy_correction_from_viewport(vp: dict[str, Any], page_height: float) -> Callable[[float, float], tuple[float, float]]:
    """As legacy_correction_factory, for an already-loaded viewport {bbox, gpts, wkt}."""
    legacy = legacy_point_to_geo_factory(vp["bbox"], vp["gpts"])
    correct = georef_factory(vp["bbox"], vp["gpts"], vp["wkt"], page_height)
    x1, _, x2, _ = vp["bbox"]

    def correct_legacy(lon: float, lat: float) -> tuple[float, float]:
        x, y = (x1 + x2) / 2, page_height / 2
        for _ in range(50):
            lo, la = legacy(x, y)
            h = 1e-3
            lo_x, la_x = legacy(x + h, y)
            lo_y, la_y = legacy(x, y + h)
            j11, j12 = (lo_x - lo) / h, (lo_y - lo) / h
            j21, j22 = (la_x - la) / h, (la_y - la) / h
            det = j11 * j22 - j12 * j21
            dlo, dla = lon - lo, lat - la
            dx = (j22 * dlo - j12 * dla) / det
            dy = (-j21 * dlo + j11 * dla) / det
            x, y = x + dx, y + dy
            if abs(dx) < 1e-9 and abs(dy) < 1e-9:
                break
        return correct(x, y)

    return correct_legacy
