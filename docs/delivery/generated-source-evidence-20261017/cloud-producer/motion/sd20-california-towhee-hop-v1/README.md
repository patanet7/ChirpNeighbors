# California Towhee: one backward ground hop

One native image edit completed at **2026-10-17 21:46:18 UTC** after starting at21:45:09 UTC. It produced four genuinely new body-and-leg drawings: crouch/compression, airborne tuck, descending reach, and supported settle. The existing neutral is reused separately. Trajectory transforms and resampled derivatives are not additional drawings. No further generation is running.

Open **review.html** for normal yard-scale one-shot playback, explicit replay/reset, a tick slider, root/contact overlay and enlarged feet. The yard preview uses1CSS pixel per world unit; neutral visible width is78world units at the existing density67/78output pixels per world unit. Source canvases are96², with corresponding registered1024² PNGs. `source-poses.apng` and `source-poses-once.gif` show only the poses on a fixed canvas. `traveled-once.apng` / `traveled-once.gif` include the separate travel trajectory. APNG timing is exact; GIF timing is approximate. Both traveled previews play once. No seamless looping or reset teleport is claimed.

## Scope and timing

The29tick sequence at30Hz is: neutral6ticks, crouch3, airborne tuck4, descending reach4, supported settle3, neutral9. Total duration is966.667ms. Root starts atworld[190,130], moves24world units backward to[166,130] only while unplanted, and remains at the landed location. The8airborne tick samples use linear horizontal travel and a designed8world-unit parabolic rise (sampled maximum7.837). The source drawings themselves also change body height and leg articulation. A browser renderer can hold the exact30Hz samples; do not interpolate root movement through planted states.

[Cornell's California Towhee account](https://www.allaboutbirds.org/guide/California_Towhee/lifehistory) describes backward hopping during ground double-scratch foraging. This packet contains one backward hop, not a complete double-scratch, scratching leaves, a peck or a feeding interaction. Chosen timing and distance are product animation values, not measured biological frequency or kinematics.

## Sources and extraction

`PRIMARY-SOURCE-MANIFEST.json` is the primary source/admission index. It includes exactly4new source-frame IDs,1reused neutral, exact original/prompt hashes, registration and output paths. `original.png` retains the native1254² sheet unchanged. The native2×2 layout did not leave clean equal-cell margins: the descending beak crosses the centre divider. Simple square cropping would cut it.

Four large alpha-positive connected components identify the four birds. Every positive-alpha atlas pixel, including detached alpha1residue, is assigned to the nearest bird seed; its RGBA bytes are retained verbatim on a full1254² source canvas. Other birds become transparent zero in each isolated source PNG. This is non-destructive sprite extraction with the original retained, not a paint repair. Verification proves every positive-alpha original pixel is assigned exactly once and all four bird cores survive registration.

One common scale736/627=1.17384370016 is applied to every new drawing. Each full native source canvas becomes1472² before integer placement on1024² registered canvases; all use the same whole-canvas3/32 nearest export to96². No per-pose scale or fit, source repaint, foot warp, alpha quantization or local body distortion is used. Off-canvas very-low-alpha residue may be cropped by the common registered canvas; zero alpha128 bird pixels are lost. Source and output hashes remain distinct.

The neutral source is `frame.sha256.8d2819dc208be7c398b643e4ae53e1f0d3f0345896b868f11b1ccc9107761d0a`. New source drawing IDs are:

- crouch: `frame.sha256.11ff542f52df9fe4a069841698d5c9077948c0d7df7048e8edc61d46d0852a0e`
- airborne tuck: `frame.sha256.22f45de72101a40c6fefa9a9bd1c3f5de482a1bf014bb602d9bcb99b07da19d1`
- descending reach: `frame.sha256.b302a2734645b9f1f096e9fc3713898374d22b1139e088bb915c50b426589915`
- supported settle: `frame.sha256.50af562220259cf5127f0236e82a0bae12b9ec36dad80fae52f9f224f7b9f78c`

## Contact and visual limits

All grounded frames have an actual alpha128 toe pixel atoutput[55,75]. Its bottom-centre boundary[55.5,76] is the common support proxy; the virtual root is[57,76]. Integer frame registration aligns this one boundary without altering foot pixels. Grounded root/primary-support positions are constant within the pre-hop and post-hop phases. Atworld groundY130 the model support boundary error is0. Airborne toes have no support contact; their zero-root-height clearance is5 and4output pixels respectively.

This is one primary support boundary, not proof that every anatomical toe is fixed. Grounded toe silhouettes change: the combined lower-foot mask centroid changes by up to1.634output pixels (~1.902world units), and its mask Hausdorff distance reaches3.162output pixels. These are shape proxies, not tracked rigid foot translation. Normal-size foot flicker/slide, curled airborne-toe anatomy and the strong compression/settle silhouette need independent visual review. The model's exact boundary is distinct from raster preview rounding of roughly1screen pixel. Whole-body source pixel equality is not an invented natural-animation gate.

The shared bird remains brown with the existing rust face/undertail, short conical bill and long tail. New output visible widths are63–66px versus67px neutral (roughly73–78world units); the same export scale is used despite those pose projections. Relative biological scale remains provisional. Quiet normal-size readability is the intended assessment size; enlarged feet are supplied to make issues reviewable.

## Contracts and verification

`motion-manifest.json` is a **custom source-review motion packet**, explicitly not a canonical app action contract. It includes trajectory samples, states, anchors, atlas mapping and timing. `neutral-idle96.png` plus `neutral-idle-review-manifest.json` retain the existing static `chirp-texture-review-v1` idle-only review packet. Airborne hop poses are not smuggled into an idle-only same-contact manifest. No canonical Sharp receipt, resident/actor binding, full action set or actual app-yard verification is fabricated.

Local verification covers original/prompt/PNG/RGBA hashes, exact extraction partition, common scale and nearest exports, root/contact model, one-shot timing and the static idle packet hash. Chromium verification samples the actual source viewer's render clock and canvas hashes, with no page errors; no browser captures are stored, embedded or uploaded. This is not continuous human playback review or actual app-yard validation.

Source rights and fidelity remain unreviewed. No third-party reference photograph was copied; the visual reference is existing project generated art. The coordinator owns independent visual review, global inventory reconciliation, source-only Git publication and one Library ZIP after the exact review hash is accepted. This worker made no global bank, queue, app or Git edits.

Next queued action after this review: a purposeful Towhee double-scratch/peck continuation, if prioritized by the coordinator. It is planned only; no additional native call has started.
