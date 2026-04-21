# MCP Assessment For Nepal Tributary Visualization

## Best-fit MCP for this task

For this specific task, the best-fit MCP is **QGIS MCP** because it is the only option I found that is designed to let an AI agent load vector layers, manipulate GIS projects, execute spatial processing, and render maps directly inside a real GIS application.

Why it fits best:

- it can create and save GIS projects
- it can add vector and raster layers
- it can run QGIS processing algorithms
- it can render maps from the current project
- it is purpose-built for layer-accurate cartography rather than only search/routing use cases

Primary source:

- `jjsantos01/qgis_mcp` README states that it allows prompt-assisted project creation, layer loading, processing execution, and map rendering, and requires QGIS 3.x plus the QGIS plugin and MCP server components.

## Why I did not use QGIS MCP here

I checked the local environment first. QGIS is not installed in this workspace environment, so the required desktop-side plugin/server stack is not available here.

Local checks run:

- `which qgis || which qgis-bin || which qgis-ltr`
- `qgis --version || qgis-bin --version || qgis-ltr --version`

All returned command-not-found results.

## Best official hosted MCP alternatives

Two official mapping MCPs are stronger than most unofficial geospatial options, but they are worse fits for this exact custom tributary-mapping task:

### Mapbox MCP Server

Strengths:

- officially maintained by Mapbox
- supports geocoding, routing, isochrones, static maps, and geospatial calculations
- hosted MCP endpoint available

Limits for this task:

- requires a Mapbox access token
- optimized for Mapbox API workflows, not for loading and styling arbitrary local tributary/border layers in a full GIS workflow

### TomTom MCP Server

Strengths:

- official hosted MCP in public preview
- supports geocoding, routing, static maps, and dynamic map widgets
- can render interactive map widgets in supported clients

Limits for this task:

- requires a TomTom API key
- stronger for location-services workflows than for custom basin/tributary cartography with local analytical layers

## Practical decision

Because QGIS MCP is the best conceptual fit but not available in this environment, and both official hosted MCPs require keys not present here, I built the tributary visualization directly with local geospatial scripting and open data instead.

That fallback is not a downgrade in map quality. It only means the map build is reproducible in this workspace without depending on a missing desktop GIS or unavailable API credentials.

## Sources

- QGIS MCP: https://github.com/jjsantos01/qgis_mcp
- Mapbox MCP Server: https://github.com/mapbox/mcp-server
- TomTom MCP Server: https://github.com/tomtom-international/tomtom-mcp
