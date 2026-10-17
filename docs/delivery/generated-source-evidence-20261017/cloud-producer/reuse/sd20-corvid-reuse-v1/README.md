# Existing corvids for the20species starter

**Best provisional candidate: Common Raven idle/blink/look.** Its four existing drawings make a recognizable heavy-billed, shaggy-throated raven at the proposed normal output size. `common_raven/atlas.png` plus `common_raven/texture-review-manifest.json` are ready for Mac's existing candidate-yard/texture review intake. The six clip steps reuse those four drawings; no new generation or drawings occurred.

The crow fallback is one held corrected-charcoal stride pose, not a newly drawn neutral stand. It is usable for provisional visual placement, but does not complete standing/look/movement/interaction coverage. `american_crow/moving-draft-atlas.png` and its separate `moving-draft-texture-review-manifest.json` expose the four existing leg poses for a bounded movement trial; world contact and weak near/far alternation remain unresolved. Keep that draft opt-in.

## Scale and visible issues

Crow:192×192 output/world canvas, visible152×92px; root pivot[127,150]. Raven:216×216 output/world canvas, visible201×134px; root pivot[144,174]. Both propose1outputpx/worldunit and1CSSpx/worldunit in this standalone review. The rendered first-pose width ratio is1.322, close to the preserved Cornell midpoint-length reference ratio1.344. Pose, tail foreshortening and the proposed yard camera still affect apparent scale; these are presentation proposals, not biological size approval.

Raven real pose changes remain readable at normal size. Head and tail feather details vary across views. The output foot-core raster's per-foot bottom changes1px across the head turns, and its pixel centroid changes at most1.346px. These alpha-mask proxies are not anatomical toe tracks or proof of physical support. The common declared contact pixels have positive alpha in all idle frames; that is a technical intake check. There is no invented exact-body-pixel equality gate for this naturally drawn animation.

The existing raven hop source is preserved in `sources/raven-hop.source.png`, with a normal-size four-pose contact sheet in `initial-output-review.png`. It visibly includes crouch/lift/airborne/landing differences, but the wing spread and posture changes are large. It remains an exploratory movement source; this batch does not promote it to admitted hop behavior. No bobbing or other runtime transform is presented as newly drawn animation.

## Honest behavior coverage

| Species | Export prepared | Planned, not bound | Actually verified in yard |
|---|---|---|---|
| American Crow | Static corrected-stride pause; separate four-pose movement draft | Standing/look replacement, locomotion contact path, stop-and-inspect object behavior | None |
| Common Raven | Drawn idle/blink/head-look sequence | Hop/short movement and stop-and-inspect object behavior | None |

Owner's provisional acceptance of minor normal-size flaws permits these review exports. It is not final acceptance of all20species or all36prior slots. Obvious anatomy/contact/scale/flicker defects remain issues.

## Source preservation and intake

All reused bytes came from canonical commit`63654eae4538f79420b1f802ec12ca49b385054d` in`patanet7/ChirpNeighbors`. `sources/*.source.png` retain the exact original-input PNG bytes embedded in the already committed candidate-yard JSON exports. `sources/*.metadata.json` retain their historical metadata and receipts with base64 payloads omitted; those receipts apply only to their original source exports. Canonical full image-generation originals and prompts remain in`assets/generated/2026-10-17/packs/chirp-corvid-candidates-v2/corvid_candidates/`; their preserved SHA256 register and selected exact prompts are copied in`sources/`.

Per-candidate`source-lineage.json` records decodedRGBA content IDs for the exact existing384px source canvases and every derived output PNG/hash. These are content-addressed references, not newly registered bank drawings. Exporting uses one fixed whole-canvas nearest scale per species: crow1/2, raven9/16. No source painting, recoloring, alpha/palette threshold, per-frame fitting or warped in-betweens.

Run Mac's current canonical Sharp intake on each supplied atlas/manifest. No new Sharp receipt, runtime binding, persistence/catalog authority or default activation is claimed here. The old source Sharp receipts cannot be reused for these resized atlases. All manifests retain review-only/unreviewed/activation-none labels.

`review.html` is self-contained: primary APNG/static previews at actual proposed size and2× inspection. `idle.gif` files are convenience previews with10ms timing quantization; manifest30Hz ticks and APNG rational timing are authoritative. Crow is deliberately a single-image hold; its `.apng` is a static PNG. `verify_exports.py` checks hashes, exact nearest exports, declared contacts, budgets and decoded timings. `verify_browser.py` checks actual Chromium APNG playback at the proposed CSS size using six in-memory raster samples; it is not continuous human video review or app-yard verification. No screenshots were saved or published.

No generation calls, paid services, credentials, hardware changes, application edits, Git changes or publication were performed by this worker. The parent owns integration/publication and the single production queue.
