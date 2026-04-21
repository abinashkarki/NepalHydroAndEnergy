# Explorer Tour Implementation Blueprint

This file defines an implementation-ready model for turning the current wiki-map explorer into a guided narrative experience with three lengths: `short`, `deep`, and `expansive`.

The key design principle is:

- one canonical storyline
- one shared stop graph
- three pacing layers (copy depth + optional modules)

This avoids maintaining three separate products.

## 1) Data model

Use `shared/tour-manifest.json` as the canonical source.

Top-level fields:

- `default_tour`, `default_mode`
- `modes` metadata (`short`, `deep`, `expansive`)
- `tours.<tour_id>.steps[]`

Each step contains:

- routing: `id`, `title`, `page`, optional `preset`
- map context: optional `layers_on`, optional `focus`
- narrative text by mode: `mode_copy.short|deep|expansive`
- research hooks: `questions[]`

### Step contract (runtime)

At runtime, convert each step into a normalized object:

```js
{
  id, title, page, preset, layers_on, focus,
  narrative: mode_copy[selectedMode] || mode_copy.short,
  questions: []
}
```

## 2) URL state model

Extend existing URL state (`preset`, `page`) with tour params:

- `tour=<tour_id>`
- `mode=<short|deep|expansive>`
- `step=<step_id>`
- `autoplay=1` (optional future use)

Priority order at init:

1. URL params
2. localStorage (`explorer.tour`, `explorer.tourMode`, `explorer.tourStep`)
3. manifest defaults

## 3) UI shell additions

Add a compact floating tour rail (map-right or center-bottom):

- tour selector (`master-thesis` initially)
- mode selector (`Short | Deep | Expansive`)
- progress (`Step 3 of 8`)
- controls (`Prev`, `Next`, `Exit tour`)

Center pane additions when tour active:

- step header block: title + narrative copy
- optional "Key questions" disclosure
- optional "Read method" link (expansive only)

## 4) State flow

Use a single state object:

```js
const tourState = {
  active: false,
  tourId: null,
  mode: "short",
  stepIndex: 0
};
```

Core transitions:

- `startTour(tourId, mode, stepId?)`
- `nextStep()`
- `prevStep()`
- `goToStep(stepId)`
- `setMode(mode)` (keep same step id if possible)
- `exitTour()`

### Step activation algorithm

When activating a step:

1. resolve step from manifest
2. apply preset (`applyPreset(step.preset)`) if present
3. ensure step layers are on (`lm.add` for missing `layers_on`)
4. open page (`openWikiPage(step.page, { fromTour: true })`)
5. apply camera focus:
   - if `step.focus` exists: fly to it
   - else rely on existing page-binding focus behavior
6. update URL + localStorage
7. render tour header with `mode_copy[mode]`

## 5) Integration points in existing code

`index.html` already has the necessary primitives:

- `applyPreset(key)`
- `openWikiPage(slug)`
- `lm.add(layerKey)`
- URL syncing + map fly logic

Recommended integration:

- load `shared/tour-manifest.json` during `init()`
- append a `tourController` module near the existing preset/nav logic
- keep current behavior untouched when `tourState.active === false`

Important:

- preserve additive layer behavior
- do not clear user-selected overlays unless step explicitly requires it
- keep feature click -> page open working while in tour

## 6) Content production workflow

For each step, prepare assets in this order:

1. **Claim sentence** (one-line assertion)
2. **Visual proof** (map + page assets already in explorer)
3. **Metric proof** (2-4 numbers maximum per step)
4. **Confidence note** (high/medium/low, concise)
5. **Deep module** (method + caveats for deep/expansive)

This keeps `short` crisp while letting `deep` and `expansive` unfold naturally.

## 7) QA checklist

Functional:

- step navigation always updates page + map + URL coherently
- mode switch does not reset tour progress unexpectedly
- deep-link opens exact tour state from shared URL

Narrative:

- every step answers one clear sub-question
- transitions are causal, not just topical
- synthesis step ranks bottlenecks and implies action sequence

Performance:

- no visible lag when stepping forward/back
- semantic index loads independently from tour controls

## 8) Next implementation slice

Minimal first merge (safe scope):

1. load tour manifest
2. add basic floating controls
3. implement `start/next/prev/exit`
4. route step activation through current `openWikiPage` + `applyPreset`
5. persist + restore tour URL state

Then expand with:

- chapter chips
- optional autoplay with reader-controlled pace
- "evidence panel" for deep/expansive
