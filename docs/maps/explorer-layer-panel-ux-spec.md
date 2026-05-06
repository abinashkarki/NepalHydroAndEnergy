# Explorer Layer Panel UX Spec

## Goals

- Respect explicit user layer selection.
- Avoid silent failure when a selected layer is hidden at broad map scale.
- Organize layers around user tasks rather than source taxonomy.
- Keep dense or specialist layers discoverable without overwhelming first-time visitors.

## Selection vs visibility

- A layer toggle means **selected**, not necessarily **currently renderable**.
- If a selected layer is suppressed at the current map scale, the panel must keep the row visibly on.
- The panel must explain the state with plain language:
  - `Zoom in more to view`
- The UI should not expose numeric zoom thresholds.

## Zoom-gated state

- Use a single reader-facing state for scale-suppressed layers:
  - `On`
  - `On · Zoom in more to view`
- This state applies both to explicit manual toggles and preset-selected layers.
- The map may still suppress rendering for clutter/performance reasons, but the panel must not make the selection look broken.

## Layer group structure

- `Basemap`
- `Overview`
- `Projects & Storage`
- `Grid & Trade`
- `Rivers & Downstream`
- `Scenarios & Advanced`

## Panel content rules

- Important public-facing layers must appear in the main panel, not only in hidden technical groupings.
- Specialist or scenario layers may remain in a collapsible advanced section.
- Grid hubs/substations are part of the core grid mental model and should not be buried in advanced-only placement.
- Storage shortlist and top-capacity project overlays belong with project interpretation, not hidden diagnostics.

## Current implementation choices

- No numeric zoom labels are shown.
- `Zoom in more to view` is the standard hint for selected-but-hidden layers.
- Core grid, storage, and project context layers are promoted into user-facing sections.
