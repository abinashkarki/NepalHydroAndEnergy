# 3D Terrain PoC Test Log

## Current Status

Working in the in-app browser on `http://localhost:8765/wiki/explorer/3d-terrain.html`.

Verified:

- Cesium viewer initializes without the previous `setDynamicLighting` crash.
- Satellite imagery renders from Esri World Imagery.
- Terrain provider initializes from Esri `WorldElevation3D/Terrain3D`.
- Existing GeoJSON layers load.
- Layer panel reports `49 features`, checkboxes update datasource visibility, and Focus buttons use deterministic camera presets.
- Camera controls for zoom, top-down, oblique, and rotation are present and native Cesium mouse/touch camera interaction is enabled.
- Elevation profile samples terrain and reports a range of `134-487 m` for the current HDDI sample.
- Narrow viewport no longer collapses the Cesium canvas to `0px` width.

## Bugs Fixed

| Bug | Cause | Fix |
|---|---|---|
| Black canvas with render-stopped modal | Direct `new ArcGisMapServerImageryProvider(...)` path crashed in Cesium 1.116 while deriving tile resources | Switched to `UrlTemplateImageryProvider` using Esri's direct tile endpoint |
| Unhandled terrain `404` | The STK terrain URL `https://assets.agi.com/stk-terrain/v1/tilesets/world/tiles` is dead | Replaced with Esri `WorldElevation3D/Terrain3D` |
| Misleading fatal error overlay | Diagnostic hook displayed nonfatal tile/request rejections as page-breaking errors | Kept fatal render/init reporting only |
| Zero-width canvas in narrow test viewport | Sidebar consumed the whole flex row | Added a responsive stacked layout below `720px` |
| Weak/non-obvious layer toggles | Datasources loaded, but imported overlays were too subtle and focus used unreliable datasource bounds | Strengthened overlay styles, disabled terrain depth testing for overlays, added feature counts, and replaced datasource focus with deterministic camera presets |
| Limited interaction affordance | Cesium camera interaction was technically available but all visible camera widgets were disabled | Added explicit zoom, pitch, and rotate controls and re-enabled camera controller capabilities |

## Test Environment

- Local server already running on port `8765`.
- Browser verification used the in-app browser.
- Visual check confirmed rendered satellite/terrain imagery.

## Remaining Caveat

This is still a light PoC. The terrain and imagery depend on external Esri services, so offline use would need hosted/local terrain and imagery tiles.
