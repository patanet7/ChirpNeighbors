# Finch rig neck-layer cleanup — bounded source checkpoint

This is an explicit editable layer cleanup of the prior deterministic cutout proof. It is **rigged source reuse, zero new drawings/calls**, not a completed action/species pack. Original source and prior proof remain unchanged. No model install, inference, new renderer, app activation or dependency install occurred.

## Reproduce and inspect

Existing Python3/Pillow/NumPy/jsonschema and Node are sufficient in this environment:

```sh
python3 run_cleanup.py
python3 -m http.server 8765 --bind 127.0.0.1
# Open http://127.0.0.1:8765/review.html
```

The self-contained HTML offers before/after96px whole-canvas views,2x source neck zooms, all five phases, playback and opaque cream / transparent checker / dark backgrounds. Three PNG comparison sheets retain those inspections; separate native RGBA PNGs retain real alpha. `owner-review-jaw-phase01.png` annotates a review location only. It is not part of the artwork.96px is a proposed review canvas, not an approved normal-yard scale.

`head-mask.png` is the prior head mask. `neck-underpaint-mask.png` is a separately editable binary mask inside `[445,475,635,575]`. The underpaint clones original pixels at identicalXY behind the moving head, with no synthesized colors. `mask-edit-journal.json` records the neck-overlap addition and explicit old-bill exclusion `[595,465,650,492]`; this exclusion avoids a duplicate stationary bill seen in the first overlap inspection. Layers are body base → cloned neck underpaint → rigid head, with hard pixel ownership. Neutral phases use the exact original. No soft blending or per-frame body fitting disguises the cut.

## Measurements and remaining art judgment

All five native1024 frames keep the entire protected y>=600 region and both foot neighborhoods byte-identical. Every visible native RGBA tuple comes from the original source. The unchanged negative control detects100 altered protected pixels. Current canonical UI coordinate functions give0 slip/roundtrip error across20 contact samples/two facings; source scale remains1. This exact-copy property is a deterministic layer constraint, not diffusion identity or approved biological scale.

Same original alpha>=128 neck-test rectangle is retained throughout:

| Phase | Angle rad | Before uncovered | After uncovered | Whole rest-mask uncovered after |
|---|---:|---:|---:|---:|
|0|0|0|0|0|
|1|-0.12|416|144|676|
|2|0|0|0|0|
|3|0.12|655|0|292|
|4|0|0|0|0|

Large neck cutout gaps are covered. **Phase1 still needs owner judgment at native rectangle `[607,475,633,492]`:144 source pixels remain uncovered after excluding the old bill.** Do not put the original bill back merely to force that count to0. A small stepped jaw/neck edge and possible stale/doubled feather contour remain. Review the broader `[445,465,650,580]` neck/shoulder region, particularly phase3 overlap, on all backgrounds. Numerical gap closure would still not approve anatomy, feather direction or lighting.

Occlusion is head-over-neck in all phases. Neutral0/2/4 is exact source; phase1 tilts the existing head one way, phase3 the other. No front/back depth switch, wing/body occlusion change, hidden neck reconstruction, large turn, true preen, gait or generated in-between is established. Uncovered whole-rest-mask pixels include changed crown/bill silhouette and remain recorded rather than relabeled as success. Eleven source/export integrity checks and15 browser phase/background samples pass; these are not art acceptance.

## Export to the existing contract

Five relevant TypeScript contract sources, the image-stage validator, and three exported JSON schemas were freshly read from canonical UI main **2e2f724f7b952179495e91f06f0d2d4575569595**. The five core files match prior snapshot bytes. `contract-binding.json` retains hashes. Mac uncommitted work was not inspected.

`export96/image-stage-sequence.json` uses the existing **ImageStageSequenceV1** shape:5 frames,96x96, straight RGBA/source hashes, supplied alpha/matte hashes, supplied RGB/foreground hashes, contiguous160,000us durations, anchor[48,75], one ground contact[50,75], reference identity and modelSlot unconfigured. It validates against the actual canonical JSON schema; local checks also cover its cross-field budgets, hashes, timing, dimensions, origins and unique IDs/contact kinds.5x96²=46,080 decoded pixels meets65,536 budget. No left/right foot anatomy is invented; separate foot-A/B projection metadata retains exact fractional positions and maximum0.3763px rounding.

The96px PNG derivative uses one common3/32 nearest-neighbor whole-canvas scale, fixed neutral palette of at most63 visible colors and alpha128 threshold. **It is explicitly lossy**, with original palette preservation false. Native source is unaffected and the derived protected region is identical across phases. Format conformance does not grant the original lossless-palette policy, art approval or runtime admission.

`export-metadata.json` maps source/root/contact/phase/palette/alpha/timing provenance. It keeps runtimeManifest, canonical species mapping, sourcePixelsPerWorldUnit and durationTicks null. Parent/Mac owns those approvals and reference/rights/taxonomy pins. Proposed action is idle attention only; never label it preening. No replacement asset engine was added.

Parent/Mac can run the application's existing validator, with its own installed dependencies:

```sh
node validate_with_existing_app.mjs /absolute/path/to/canonical/UI
```

This simply calls existing `validateImageSequence`. The cloud attempt is retained in `app-validator-receipt.json`: blocked by missingzod, exit1; no install/fallback engine attempted. Actual Mac Zod validation, packaging/admission and normal-yard playback are pending. JSON-schema plus local refinements passed here; full app validation is not claimed.

## Next queued work

Owner/art review of the marked phase1 lower-jaw mask and phase3 feather overlap, followed by the same strict native pixel/contact checks. Parent relays the96px image-stage candidate and metadata to Mac for existing-validator/tick/scale/reference intake. Do not repeat generation, alter planted feet, broaden angles, loosen tolerances or promote any of the36 species-slot rows to accepted on this checkpoint.
