# Northern Mockingbird closed-eye candidate

One native edit started at2026-10-17 22:14:41 UTC and completed at22:15:36 UTC. It produced one new fully closed-eye drawing. The existing awake1024²source and192²output PNG are reused byte-for-byte. No new neutral, look pose, rigged drawing or body-bob transform was created. No generation is running.

Open `review.html` for open/closed/open playback at the existing declared world size, on light and dark backgrounds, with optional root/contact overlay and enlarged eye/feet inspection. This is a candidate/study pending independent visual compatibility review, not an accepted blink slot. If texture, silhouette or foot changes distract at this size, retain the source as a held study rather than mark blink complete. Do not retry automatically.

## Exact sources and conversion

`PRIMARY-SOURCE-MANIFEST.json` contains exactly one new source frame and one reused awake frame. `frame-to-action-map.json` explicitly names and hashes the atlas and intake manifest, maps each primary source ID to its render frame ID, atlas rectangle, output PNG/hash and decoded output ID, and records the30Hz schedule. The unchanged existing look action remains outside this packet.

- Reused awake source: `frame.sha256.bd7184a468371d79989a4875534e987db18997845190ba90c2ee11051f844855`, `reused-open-source1024.png`.
- New native closure: `frame.sha256.b3f3357a14cfcc73eb8f457252d119f25a6b17d1e883b259d23b26792996bd6c`, `original.png`.

The tool returned1254²instead of the requested1024². One explicit whole-canvas nearest1254→1024 conversion gives `closed-source1024.png`; the common whole-canvas1024→192 nearest export gives `closed192.png`. There is no translation, per-pose fit, local rescale, source repaint, foot warp, alpha cleanup or palette quantization. The native→registered scale is0.8165869218500797; registered→output scale is3/16; the product is192/1254. Derivative frame hashes are not additional drawings.

`prompt.txt` retains the exact2072UTF-8 bytes submitted. `native-call-arguments.json` retains the exact argument object used. `native-prompt-audit.json` verifies the byte match. `original.png` is untouched. Rights/fidelity remain unreviewed, and no third-party image reference was introduced.

## Size, timing and limits

The existing density1.225output pixels per world unit is unchanged. Both canvases are192², displaying at156.734694CSS pixels when1CSS pixel represents1world unit. The open bird is80world units wide; the closed bird is81.632653wide. Both visible heights are72output pixels, or58.775510world units. The visible tail-edge width difference is retained, not hidden by fitting.

The30Hz loop uses open60ticks, closed3ticks, open27ticks:3seconds overall and100ms closed. The endpoints reuse the exact same awake drawing. These are product timings, not a measured biological blink rate. Reduced-motion fallback should hold the existing awake frame through the existing runtime contract; this worker did not bind it in the app.

The eye reads closed in the enlarged crop. The native edit also redrew non-eye pixels: at192²output the alpha128 silhouette IoU is0.957709, and the visible outside-eye mean absolute RGB difference is15.6085/255. These integrity/appearance diagnostics do not impose a universal body-pixel equality gate. Independent review must assess actual-size flicker, recognizability and contact continuity.

The original declared positive-alpha contacts[113,148] and[115,149] are present in both output frames. The combined lower-foot alpha128 mask keeps its bottom boundary at150, while its centroid changes0.546666output pixels (~0.446258world units) and its mask Hausdorff distance is1.414214output pixels. These are shape proxies, not anatomically tracked toes or contact approval. Root/pivot remains[114,150] with no motion transform.

## Intake and verification

Use `blink-atlas192.png` with `texture-review-manifest.json`, indexed explicitly by `frame-to-action-map.json`. This is the existing `chirp-texture-review-v1` unreviewed, inactive, idle-only review profile. No canonical Sharp receipt, actor/resident binding, owner acceptance or actual-yard verification is fabricated.

Local checks verify exact source IDs/PNG hashes, unchanged awake bytes, whole-canvas exports, atlas tiles, declared scale, contact pixels, explicit filename/action mapping and exact APNG rational timing. Chromium source-viewer verification observes open/closed/open at the declared156.734pxCSS canvas width, on light/dark surfaces, with seven seeks and seven actual clock samples. Receipts contain numeric state and raw canvas RGBA hashes only. No browser capture bytes are stored, embedded or uploaded; all preview images are source composites.

`blink.apng` is the exact-timing standalone source animation; `blink-approx.gif` uses the same100ms closure (GIF format retains its usual limitations). `normal-light-dark-eye-feet.png` and `crops/` expose the actual-size comparison and enlarged source eye/feet. The HTML source canvas clock is a review aid, not actual app execution or continuous human video judgment.

The next queued step is independent review of this exact frozen packet, then either provisional source intake or a study hold. No additional native call, global bank/queue edit, app change or Git publication is authorized for this worker batch. The coordinator owns later admission, inventory reconciliation, source-only publication and one Library ZIP after exact-hash review.
