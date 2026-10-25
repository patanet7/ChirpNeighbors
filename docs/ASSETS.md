# Assets: where art lives and what a deliverable looks like

One fixed home per piece of art, by **what it is**, never by date or batch. Dates, prompts, sources and
batches are fields in the manifest. Approved art is in `assets/approved/`; nothing else counts as approved.

## Source of truth

- **Individual RGBA PNG frames**, transparent background, at the **native pixel grid**: 1 art pixel =
  1 file pixel. Never store a pre-upscaled copy (`approved-art-check` rejects block-upscaled files;
  `art:sync` brings them back down).
- GIFs, strips and contact sheets are **previews** (generated for the review page), never source.
- Atlases and sprite sheets the app builds are **build outputs**, never committed as source.
- Ids are lowercase `snake_case`. Frames are `01.png`, `02.png`, … (zero-padded, 1-based).

## Layout

```
assets/approved/
  approved.json                         one manifest for everything below
  regen-queue.json                      slots to (re)generate, with the reason
  birds/<species>/
    bird.json                           species id, app species id, length cm, facing, canon canvas + anchor
    canon.png                           the approved canon (clean side view)
    clips/<action>/<variant>/           variant = v1, v2, … (several approved takes of one action)
      01.png 02.png …                   frames
      clip.json                         timing, loop, canvas, anchor
  objects/<object>/
    object.json                         per-variant geometry (crop, pivot, ground polygon, size in metres, mount, supports)
    v1.png v2.png …                     every approved variant
  scenes/<yard>/<season>/<layer>.png    painted yards (geometry in the app: REGIONAL_YARD_SCENES)
  plants/<plant>/…                      reserved
```

### Bird

`bird.json`
```json
{ "id": "house_finch", "appSpeciesId": "cn-species-haemorhous-mexicanus", "lengthCm": 13.5,
  "facing": "right", "canvas": { "width": 1024, "height": 1024 }, "anchor": { "x": 522, "y": 800 },
  "palette": null }
```
- `facing` is always `right`; the runtime mirrors.
- `canvas`/`anchor` are the canon's size and feet point (mean x of the two lowest opaque rows, y below them).

`clips/<action>/<variant>/clip.json`
```json
{ "action": "takeoff", "frames": 5, "canvas": { "width": 76, "height": 64 },
  "frameMs": [200, 100, 100, 100, 100], "loop": false,
  "anchor": { "x": 33, "y": 58 }, "groundRow": 58, "events": {} }
```
- Timing is `fps` or per-frame `frameMs`. `loop` is false for blink, look, takeoff, landing.
- `events` names frames that matter to behaviour, e.g. `{ "contact": 3, "peck": 4 }` (filled by hand when known).
- Actions: canon, idle, blink, look, hop, walk, takeoff, flight, landing, feed, drink, bathe, preen, sing, sleep.

**Deviation from "one canvas per bird" (stated reason).** The owner's spec asks for one canvas and anchor
shared by every clip so clips swap without jumping. Today's approved clips were drawn at different sizes by
different producers (house finch: canon 1024 px, idle 96 px, preen 512 px, rig flight 76 px). Putting them
on one canvas would resample pixel art, which breaks the native-grid rule. So each `clip.json` carries its
own `canvas` and feet `anchor`; the app registers every clip to the bird by that anchor and the standing
height, so swaps still do not jump. New art for a bird is generated on the bird's canvas, and then
`clip.json` canvas equals `bird.json` canvas.

### Object

`objects/<object>/<variant>.png` + one `object.json`:
```json
{ "id": "perch", "reviewSlot": "object.perch", "kind": "perch",
  "variants": { "v2": { "appCatalogId": "driftwood_log", "crop": { "x": 13, "y": 12, "width": 648, "height": 298 },
    "metres": { "height": 0.35 }, "pivot": { "x": 352, "y": 272 }, "groundPolygon": [...],
    "mount": null, "supports": [{ "id": "top", "point": { "x": 272, "y": 120 } }] } } }
```
Geometry is in source-file pixels. `crop` exists because some approved picks are direction boards holding
several objects; new object art should be one object per file (then `crop` is the whole image).

### Scene

`scenes/<yard>/<season>/<layer>.png` (layer: composite, background, ground, foreground, …), manifest kind
`scene` with `yard`, `season`, `layer` and an optional `displayCrop`. Owned by the scenes track. Yard geometry
(ground polygon, horizon, perch lines) is defined in the app (`REGIONAL_YARD_SCENES`), so no `scene.json` is
stored; add one here only for geometry the app does not hold.

## Manifest: `approved.json`

`{ "schema": "chirp-approved-art/2", "layout": "docs/ASSETS.md", "entries": [...] }`, one entry per canon,
clip variant and object variant:

| field | meaning |
|---|---|
| `id` | the folder (clips) or file stem: `birds/house_finch/clips/idle/v1`, `birds/house_finch/canon`, `objects/perch/v2` |
| `kind` | `bird-canon`, `bird-clip`, `object`, `scene` |
| `species`, `action` / `object`, `variant` / `yard`, `season`, `layer` | what it is |
| `default` | the variant the app uses when it has no reason to pick another |
| `files[]` | `path`, `sha256`, `width`, `height` |
| `fps` / `frameMs`, `loop` | clips |
| `source` | `candidate` (review-page pick id), `pack`, `path` (original location), `derivation` (cells cut, scale brought down, GIF replaced by its frames) |
| `prompt` | path of the prompt that made it, when the producer kept one |
| `generated` | date the source was generated (from its original path) |
| `approved` | when the owner approved it |
| `reviewSlot`, `reviewUrl` | the decision this came from |

`regen-queue.json` items: `slot`, `verdict`, `note`, `decidedAt`, `reason`, `bestCandidate` (id, preview,
pack, source) and `removedFromApproved` when a slot left the library. Generation consumes this queue once a
provider exists.

## Candidates (not approved)

New generations go to `assets/candidates/<kind>/<id>/<action>/<candidate-id>/…` in the **same shape** as
approved art (frames + `clip.json`, or `<variant>.png` + `object.json`), so promotion is a copy plus a
manifest entry, not a reformat. Existing generated packs stay where they are (`assets/generated/<date>/…`,
`docs/delivery/…`) as archive until they are migrated; `approved.json` records their original paths.

## The index: `assets/index.jsonl`

One JSON row per subject (what the art is, with its tags), slot (one place art can fill) and art file
set, sorted by id; the first row documents the grammar and every tag. The id is the path:
`subject ["/" slot] ["/" version]`, e.g. `birds/house_finch/clips/hop/v1`,
`plants/coast_live_oak/mature.winter.bare`, `scenes/inland/winter.snow/composite`. `vN` is approved,
`c<sha8>` a candidate. Wanted slots (every bird × the 15 acts, every object and plant the app uses, each
yard's seasons plus weather states: snow, wet, dry, autumn leaves) show what is missing.

```sh
node scripts/assets.mjs find                      # coverage per kind: approved · candidates · unsorted · wanted
node scripts/assets.mjs find --wanted --kind plants
node scripts/assets.mjs index                     # rebuild (keeps subjects/slots already in the index)
node scripts/assets.mjs check                     # approved/ + the index; warns on images outside approved/candidates/inbox/references
node --test scripts/assets.test.mjs
```

Plants carry `nativeRange` (ecoregion ids from `assets/regions/regions.json`: EPA Level III > II > I for
North America, WWF as the global fallback; empty plus `needs: ["nativeRange"]` until researched) and
`cultivation` (wild, nursery, houseplant). No "native" label is stored: the game computes nativeness from the
yard's location at runtime. Native NEVER restricts placement; it is a likelihood weight for the birds that use
the plant and a classification for the shelf and field guide. Scenes carry `landscape` (coastal, valley,
mountain, desert, forest, prairie, urban), `ecoregions` when they depict a real place, `fence` and per-layer
`depth`.

## Commands

After the owner decides on the review page (lead exports the decisions to JSON):
```sh
# 1. ChirpNeighbors: copy approved picks in, queue regenerations
node scripts/art-sync.mjs --decisions <owner-decisions-export.json>
node scripts/assets.mjs index   # refresh assets/index.jsonl from approved.json
node scripts/assets.mjs check   # was approved-art-check.mjs (kept as a shim)
# commit assets/approved, PR, merge
# 2. App (birdsong-yard-sprites): admit approved birds into the yard
git -C <ChirpNeighbors> archive origin/main assets/approved | tar -x -C <tmp>
npm run birds:admit -- --approved <tmp>/assets/approved --rig <rig-output-dir>
```
`art-sync` is idempotent (a slot whose approved candidates already match the decision is left alone) and
needs only node. Its inputs default to the review workspace (`--work ~/GitHub/personal/_chirp-work`:
review-data.json, the candidate catalog with original locations, the asset index, rig outputs); each can be
overridden (`--review`, `--catalog`, `--index`, `--rig`, `--codex-root`). `--dry-run` prints the plan.
