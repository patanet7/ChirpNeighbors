# Fixed-body finch cutout: bounded executable control proof

This CPU experiment is implemented and tested. It reuses one retained generated female House Finch neutral as an engineering source. Five160ms phases use three distinct rigid cutout states; **zero new generation calls, zero newly drawn frames, zero verified production reuses, no app integration**. It demonstrates control of existing pixels, not a preening/walking cycle or accepted bird anatomy.

Run from this directory, using existing Python3 with Pillow+NumPy and Node (no installs/downloads):

```sh
python3 run_proof.py
python3 -m http.server 8765 --bind 127.0.0.1
# Open http://127.0.0.1:8765/review.html
```

`run_proof.py` rebuilds layers, five source PNG assemblies, five512px contour guides, APNG/GIF diagnostics and runtime review HTML; verifies exact pixels and the retained renderer coordinate functions. Optional `python3 verify_browser.py` uses already-installed Playwright and /usr/bin/chromium; no browser/model installation is performed. It was run in this environment. `research-private/` is deliberately absent from this public source package.

## What was controlled and measured

- Source file SHA and decoded neutral identity are fixed. Body/feet region `[0,600,1024,1024]` is restored from source after composition. All five frames have0 changed protected RGBA pixels, including both heuristic foot neighborhoods. This100% protected-region identity is enforced by copying; it is not a diffusion result.
- Head/neck is a provisional hand-authored polygon around one actual source drawing. Rotation is nearest inverse rigid sampling around `[560,516]`, at scale1. Neutral is copied intact. No painted in-between or new anatomical drawing is created.
- Both foot-A `[483,792]` and foot-B `[535,800]` stay fixed. They are silhouette heuristics, with anatomical left/right unassigned. Native foot-height difference is retained; no invented common toe baseline is imposed.
- The exact retained `frameToWorld` and `worldToFrame` function bodies from UI commit6f23d988a788a29de509f92af7c1f24f7e63c6b4 are evaluated in a dependency-free harness.20 contact samples over five phases/two facings give0 world-slip and0 roundtrip error. A two-world-unit body shift and a scale change are detected. This is actual source-function execution, not full Pixi/SVG rendering or current Mac validation.
- Diagnostic density4 source pixels/world unit is an inspected V4 option, **not approved biological scale**. Original body source dimensions/scale stay fixed. No cross-species calibration has been invented.
- Eight retained-source checks pass. Browser runtime10 phase/facing samples show six distinct visual states with no page errors. Browser bytes use browser-decoded source colors; native exact RGBA checks are on separate source PNGs.

## Art and compatibility failures remain visible

The polygon is not approved anatomical segmentation. At the two rotated states, up to948 alpha>=128 source pixels in the rest head-mask area become uncovered. Not every changed silhouette pixel is necessarily an objectionable seam, but this is a useful conservative exposure signal. The neck/base needs manually authored underpaint, a better overlap mask and artist review. The pose is a small head pivot, not a true backward preen, wing motion, flight or gait.

Lower-body identity is exact. Full species likeness, head shape after raster sampling, anatomical contact, lighting/plumage approval and motion quality remain open. Source assets themselves have no production art approval. The inspected app supports whole-frame pivots/contacts/rotation, not this arbitrary-part runtime schema. A bake/export adapter or a reviewed renderer extension is required; neither was added. Native1024 dimensions, five full decoded frames, continuous alpha and unrestricted palette do not meet the older256edge/65,536decodedpixel/binary-alpha/64color profile. No per-frame fitting or silent admission is performed.

## Two distinct possible pipelines

**Retained/generated articulated source layers + deterministic rig:** Approved head/neck, torso/wing, legs/toes and occlusion-underpaint layers would be drawn once, then transformed with explicit joints/contacts. Existing neutral pixels can supply the fixed body and some parts. Deterministic copying/transforms can enforce protected source pixels and foot trajectories. Rig output remains assembled motion, not newly drawn frames. This proof supplies the fixed-body mechanism; reviewed masks/underpaint, multi-part anatomy, actual action choreography and Mac admission are still missing.

**Structure-conditioned new drawings:** Use approved bird-shaped silhouettes plus interior bill/wing/leg lines and authored contacts, then a compatible ControlNet lineart/Canny checkpoint and whole-bird reference adapter. The stored private conditioning research was read in full and used here. Official [ControlNet](https://github.com/lllyasviel/ControlNet), [SD1.5 lineart model card](https://huggingface.co/lllyasviel/control_v11p_sd15_lineart) and [IP-Adapter](https://github.com/tencent-ailab/IP-Adapter) were checked. Our binary black-on-white guides contain exterior contours only; interior structure and geometry approval remain missing. They are not semantic labels, depth, or human/animal-pose keypoints. Diffusion would still redraw and may drift; a protected-pixel compositor could guarantee only the copied final region, not the unmasked generated candidate. Score raw candidate and final composite separately. No diffusion inference has been run or approved.

Current capability check finds no PyTorch, Diffusers or Transformers, no visible /dev/nvidia devices and no measured accelerator memory. Model weights, compatible base/control/reference revisions and licensing have not been inspected locally. Native image tools expose neither a hard edit mask nor ControlNet input. No install, weights download, paid compute or new generation occurs. No inference VRAM minimum is invented.

## Concrete next step

Replace `head-mask.png`/`manualHeadPolygon` and supply a reviewed neutral neck-underpaint/overlap layer in the same1024 canvas, without touching protected y>=600. Review the two rotated states at native and intended display size. Rerun `python3 run_proof.py`; retain exact body/feet gates and reject gaps, duplicated contour, bill/eye distortion or changed protected pixels. This is the next queued **manual art/mask** task, not an active generation job. After that passes, author a real preen key pose/contacts; do not call this head pivot a completed action. Current Mac source/profile and canonical action mapping must be supplied before any export or app test. Structure-conditioned generation stays blocked until an actual compatible control interface/engine is available and tested.
