#!/usr/bin/env python3
"""
Warm Technical / Living Atlas — Phase 4 Screenshot Suite
Captures all required validation screenshots.
"""
import asyncio
import json
from pathlib import Path
from playwright.async_api import async_playwright

BASE_URL = "http://localhost:8081/wiki/explorer/index.html"
OUT_DIR = Path(__file__).parent / "screenshots-phase4"
OUT_DIR.mkdir(exist_ok=True)

SHOTS = [
    {"name": "01-power-light-national", "preset": "power_system", "basemap": "Carto Positron", "zoom": 6,
     "desc": "Power preset — light — national zoom"},
    {"name": "02-power-light-regional", "preset": "power_system", "basemap": "Carto Positron", "zoom": 8,
     "desc": "Power preset — light — regional zoom"},
    {"name": "03-power-terrain-regional", "preset": "power_system", "basemap": "Topographic", "zoom": 8,
     "desc": "Power preset — terrain — regional zoom"},
    {"name": "04-power-satellite-regional", "preset": "power_system", "basemap": "Satellite", "zoom": 8,
     "desc": "Power preset — satellite — regional zoom"},
    {"name": "05-solar-light-regional", "preset": "solar_system", "basemap": "Carto Positron", "zoom": 8,
     "desc": "Solar preset — light — regional zoom"},
    {"name": "06-solar-satellite-regional", "preset": "solar_system", "basemap": "Satellite", "zoom": 8,
     "desc": "Solar preset — satellite — regional zoom"},
    {"name": "07-geopolitics-downstream", "preset": "geopolitics", "basemap": "Carto Positron", "zoom": 7,
     "desc": "Geopolitics — downstream India view"},
    {"name": "08-wiki-clean", "preset": "wiki", "basemap": "Carto Positron", "zoom": 7,
     "desc": "Wiki preset — clean orientation"},
]


async def capture(page, shot):
    print(f"\n📸 {shot['name']}: {shot['desc']}")

    # Navigate with preset
    await page.goto(f"{BASE_URL}?preset={shot['preset']}", wait_until="domcontentloaded")
    
    # Wait for async init
    await page.wait_for_timeout(8000)

    # Minimize left and center panes — float map to full viewport
    await page.evaluate("""() => {
        // Hide sidebars and splitters
        document.querySelectorAll('.pane.left, .pane.center, .splitter').forEach(el => {
            el.style.display = 'none';
        });
        // Float right pane to full viewport
        const right = document.querySelector('.pane.right');
        if (right) {
            right.style.position = 'fixed';
            right.style.top = '39px';
            right.style.left = '0';
            right.style.width = '100vw';
            right.style.height = 'calc(100vh - 39px)';
            right.style.zIndex = '9999';
        }
        const mapEl = document.getElementById('map');
        if (mapEl) {
            mapEl.style.width = '100%';
            mapEl.style.height = '100%';
        }
        // Also hide layer-panel and preset-bar so they don't overlay
        const lp = document.getElementById('layer-panel');
        if (lp) lp.style.display = 'none';
        const pb = document.getElementById('preset-bar');
        if (pb) pb.style.display = 'none';
        // Trigger Leaflet resize
        if (window._explorer && window._explorer.map) {
            window._explorer.map.invalidateSize();
        }
    }""")
    await page.wait_for_timeout(1000)

    # Check if init succeeded
    has_map = await page.evaluate("() => !!window._explorer?.map")
    if not has_map:
        print("   ❌ Init failed - no map")
        # Try screenshot anyway
        await page.screenshot(path=str(OUT_DIR / f"{shot['name']}_FAIL.png"), full_page=False)
        return {"shot": shot, "error": "Init failed"}

    # Set basemap — use app function if available for clean switch
    await page.evaluate(
        """(basemap) => {
            const ex = window._explorer;
            // Try app's setBaseLayer first (cleans old tiles properly)
            if (window.setBaseLayer) {
                window.setBaseLayer(basemap);
            } else if (ex.baseLayers && ex.baseLayers[basemap]) {
                ex.map.eachLayer(l => { if (l instanceof L.TileLayer) ex.map.removeLayer(l); });
                ex.baseLayers[basemap].addTo(ex.map);
                ex.lm.setBasemap(basemap);
            }
        }""",
        shot["basemap"]
    )

    # Wait for tiles: terrain needs longer
    tileWait = 5000 if shot["basemap"] == "Topographic" else 3000
    await page.wait_for_timeout(tileWait)

    # Set zoom and center
    await page.evaluate(
        """(zoom) => {
            window._explorer.map.setView([28.2, 84.0], zoom);
        }""",
        shot["zoom"]
    )

    # Wait for markers to settle after zoom
    await page.wait_for_timeout(3000)

    # Gather metadata
    meta = await page.evaluate("""() => {
        const ex = window._explorer;
        const activeLayers = ex.lm.activeKeys();
        // Log which layers are active for debugging
        console.log("Active layers:", activeLayers);
        return {
            preset: ex.lm._preset,
            basemap: ex.lm._basemap,
            markerMode: ex.lm._markerMode,
            zoom: ex.map.getZoom(),
            badgeCount: document.querySelectorAll('.np-marker-badge').length,
            activeLayers: activeLayers,
        };
    }""")

    print(f"   preset: {meta['preset']} | basemap: {meta['basemap']} | mode: {meta['markerMode']} | zoom: {meta['zoom']} | badges: {meta['badgeCount']} | layers: {len(meta['activeLayers'])}")

    # Take screenshot
    file_path = OUT_DIR / f"{shot['name']}.png"
    await page.screenshot(path=str(file_path), full_page=False)
    print(f"   → {file_path}")

    # Save metadata
    meta_path = OUT_DIR / f"{shot['name']}.json"
    meta_path.write_text(json.dumps({**shot, **meta}, indent=2))

    return {"shot": shot, "meta": meta, "file_path": str(file_path)}


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1440, "height": 900})
        page = await context.new_page()

        results = []
        for shot in SHOTS:
            try:
                result = await capture(page, shot)
                results.append(result)
            except Exception as e:
                print(f"   ❌ FAILED: {e}")
                results.append({"shot": shot, "error": str(e)})

        await browser.close()

    # Summary
    print("\n" + "=" * 60)
    print("PHASE 4 SCREENSHOT REPORT")
    print("=" * 60)
    for r in results:
        status = "✅ OK" if "error" not in r else "❌ FAIL"
        print(f"{status} {r['shot']['name']}: {r['shot']['desc']}")
        if "meta" in r:
            print(f"      zoom={r['meta']['zoom']} badges={r['meta']['badgeCount']} layers={len(r['meta']['activeLayers'])}")
        if "error" in r:
            print(f"      Error: {r['error']}")
    print(f"\nOutput: {OUT_DIR}/")


if __name__ == "__main__":
    asyncio.run(main())
