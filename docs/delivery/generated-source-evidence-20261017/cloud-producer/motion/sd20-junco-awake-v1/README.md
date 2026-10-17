# Oregon Junco awake/blink correction

One native OpenAI image edit produced two actual new drawings of the existing adult Oregon-type Dark-eyed Junco. The prior sleepy pair remains a rest/failed-awake attempt, not a successful blink. Source completion file timestamp:2026-10-17T21:44:57.304889Z; tool elapsed31.5seconds. No retry or rigged body bobbing.

The awake source has a round black eye with a visible catchlight; the closed source has a thin closed lid. Exact enlarged source eye/contact crops and normal-yard-size playback are in `review.html`. The eye-region catchlight diagnostic is22bright pixels versus0, which supports the inspection but is not itself a semantic acceptance test.

## Intake and scale

Animated: `idle-blink-atlas192.png` + `texture-review-manifest.json`. Neutral fallback: `awake192.png` + `static-review-manifest.json`. At30Hz the loop holds awake60ticks, closed3ticks, awake27ticks:3seconds total,100ms closed. Original192px RGBA tiles use density32/13 and a78world-unit canvas; visible width is52world units in both poses. The yard-scale APNG and GIF show a78px canvas. No per-frame resizing or alpha/palette changes.

Sources occupy the same1024px canvas, copied from native1774x887 atlas cells with integer registration64,29 and63,29. Positive offsets preserve all native alpha samples, including faint margin residue. `registration-diagnostic-receipt.json` retains the earlier export issue without counting derivative registrations as new drawings.

Declared output pivot122,150; shared positive-alpha foot reference pixels114,146 and143,146. These meet the technical data contract, not a claim of anatomically exact sole contact. Fixed-region foot centroid changes by at most0.346output pixels,0.141world units. Raw lowest claw/tip row changes by up to2output pixels,0.8125world units; retain this diagnostic and review visible contact at yard size. Exact full-body RGBA equality is not a natural-blink quality gate.

## Verification and remaining work

Six source/hash/registration/export/contact/timing checks pass. Chromium sampled native APNG playback ten times at78CSSpx, observed two distinct states and no page errors. Browser captures are not saved or bundled. Continuous human/owner review remains distinct from sampled playback verification.

Independent review is required before sealing the final Library ZIP. Mac must create the real Sharp canonical receipt and verify actual yard placement, scale and playback. No app, physics or locomotion/feeding/preening/flight binding is claimed. Coordinator owns global frame-bank/queue registration and source-only PR publication.

`PRIMARY-SOURCE-MANIFEST.json` is the ingest authority. Source/prompt hashes, output manifests and rights/reference provenance are retained. External factual references remain unreviewed for rights; no external photograph pixels were supplied to this call.
