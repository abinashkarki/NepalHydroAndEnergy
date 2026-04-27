#!/usr/bin/env node
/**
 * Warm Technical / Living Atlas — Phase 4 Screenshot Suite
 * Captures all required validation screenshots.
 */
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const BASE_URL = 'http://localhost:8080/index.html';
const OUT_DIR = path.join(__dirname, 'screenshots-phase4');

// Ensure output directory exists
if (!fs.existsSync(OUT_DIR)) fs.mkdirSync(OUT_DIR, { recursive: true });

const SHOTS = [
  { name: '01-power-light-national', preset: 'power', basemap: 'Carto Positron', zoom: 6, desc: 'Power preset — light — national zoom' },
  { name: '02-power-light-regional', preset: 'power', basemap: 'Carto Positron', zoom: 8, desc: 'Power preset — light — regional zoom' },
  { name: '03-power-terrain-regional', preset: 'power', basemap: 'Topographic', zoom: 8, desc: 'Power preset — terrain — regional zoom' },
  { name: '04-power-satellite-regional', preset: 'power', basemap: 'Satellite', zoom: 8, desc: 'Power preset — satellite — regional zoom' },
  { name: '05-solar-light-regional', preset: 'solar', basemap: 'Carto Positron', zoom: 8, desc: 'Solar preset — light — regional zoom' },
  { name: '06-solar-satellite-regional', preset: 'solar', basemap: 'Satellite', zoom: 8, desc: 'Solar preset — satellite — regional zoom' },
  { name: '07-geopolitics-downstream', preset: 'geopolitics', basemap: 'Carto Positron', zoom: 7, desc: 'Geopolitics — downstream India view' },
  { name: '08-minimal-clean', preset: 'minimal', basemap: 'Carto Positron', zoom: 7, desc: 'Minimal preset — clean orientation' },
];

async function capture(page, shot) {
  console.log(`\n📸 ${shot.name}: ${shot.desc}`);

  // Navigate with preset
  await page.goto(`${BASE_URL}?preset=${shot.preset}`, { waitUntil: 'networkidle' });

  // Wait for app init
  await page.waitForFunction(() => window._explorer && window._explorer.map, { timeout: 15000 });

  // Set basemap
  await page.evaluate((basemap) => {
    const ex = window._explorer;
    const layers = ex.lm.baseLayers;
    if (layers[basemap]) {
      ex.map.eachLayer(l => { if (l instanceof L.TileLayer) ex.map.removeLayer(l); });
      layers[basemap].addTo(ex.map);
      ex.lm._basemap = basemap;
      ex.lm._applyBasemapToMarkers();
    }
  }, shot.basemap);

  // Set zoom and center on Nepal
  await page.evaluate((zoom) => {
    window._explorer.map.setView([28.2, 84.0], zoom);
  }, shot.zoom);

  // Wait for tiles and markers
  await page.waitForTimeout(2000);

  // Gather metadata
  const meta = await page.evaluate(() => ({
    preset: window._explorer.lm._preset,
    basemap: window._explorer.lm._basemap,
    markerMode: window._explorer.lm._markerMode,
    zoom: window._explorer.map.getZoom(),
    badgeCount: document.querySelectorAll('.np-marker-badge').length,
    activeLayers: window._explorer.lm.activeKeys(),
  }));

  console.log(`   preset: ${meta.preset} | basemap: ${meta.basemap} | mode: ${meta.markerMode} | zoom: ${meta.zoom} | badges: ${meta.badgeCount} | layers: ${meta.activeLayers.length}`);

  // Take screenshot
  const filePath = path.join(OUT_DIR, `${shot.name}.png`);
  await page.screenshot({ path: filePath, fullPage: false });
  console.log(`   → ${filePath}`);

  // Save metadata
  fs.writeFileSync(path.join(OUT_DIR, `${shot.name}.json`), JSON.stringify({ ...shot, ...meta }, null, 2));

  return { shot, meta, filePath };
}

(async () => {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({ viewport: { width: 1440, height: 900 } });
  const page = await context.newPage();

  const results = [];
  for (const shot of SHOTS) {
    try {
      const result = await capture(page, shot);
      results.push(result);
    } catch (e) {
      console.error(`   ❌ FAILED: ${e.message}`);
      results.push({ shot, error: e.message });
    }
  }

  await browser.close();

  // Summary report
  console.log('\n' + '='.repeat(60));
  console.log('PHASE 4 SCREENSHOT REPORT');
  console.log('='.repeat(60));
  for (const r of results) {
    const status = r.error ? '❌ FAIL' : '✅ OK';
    console.log(`${status} ${r.shot.name}: ${r.shot.desc}`);
    if (r.meta) {
      console.log(`      zoom=${r.meta.zoom} badges=${r.meta.badgeCount} layers=${r.meta.activeLayers?.length || 0}`);
    }
    if (r.error) console.log(`      Error: ${r.error}`);
  }
  console.log(`\nOutput: ${OUT_DIR}/`);
})();
