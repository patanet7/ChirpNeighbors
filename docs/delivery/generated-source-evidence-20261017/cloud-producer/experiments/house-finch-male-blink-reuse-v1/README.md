# House Finch male blink references and quiet-idle reuse check

This checks **three already-retained drawings** from canonical House Finch male idle v1: open neutral, half blink and closed blink. File hashes and decodedRGBA frame IDs match committed source bytes from the checkpoint merged into main3c43f1465453cb401be44c2ec26010e78dcdd4e0. Exact source atlas/prompt, component extraction and prior integer registration are referenced in `manifest.json`.

**No new image call, drawing, pixel assembly or production clip.** Proposed timing has five phases but only three distinct existing frame IDs; repeated half/open references are timing/reuse, not new images. Global frame bank stays64drawings and verified production reuse stays0. All36matrix slots remain unaccepted.

**Criteria correction:** The natural-blink interpretation and next action below are superseded by [runtime-scale assessment](../house-finch-male-blink-runtime-assessment-v2/README.md). Exact body equality applies only to fixed-body rig promises; changed source pixels do not establish perceptual rejection. Historical source measurements are preserved. The new packet provides a96px straightRGBA30Hz opt-in candidate and independent review.

## Historical feasibility result

An unchanged male neutral is technically suitable as an **idle reduced-motion still fallback**, conditional on source and Mac admission. It preserves its own body/feet exactly and adds no animation. The actual canonical UI2e2f724f `sampleClip` function was read and its TypeScript syntax erased for a dependency-free source-function test: six reduced-motion samples stay on the first neutral; two normal-mode controls select other poses. This is a logical test carrier, not an admitted manifest or actual renderer run. No alternate sampler/engine is added.

The blink drawings are useful reference candidates. They visibly supply different eyelid states, but **direct whole-frame swapping fails the strict fixed-body reuse gate**:

|Reference|Foot heuristic drift from open, sourcepx|Body-band width change|Protected maskIoU|Protected changed pixels|
|---|---:|---:|---:|---:|
|Open|0|0|1|0|
|Half|1.00|2.10%|0.94685|51,975|
|Closed|2.24|2.31%|0.95031|51,257|

These are retained registered1024px coordinates, not raw generator-layout compliance or anatomical foot tracking. The source pack previously applied integer translations to place silhouettes; no rescale/fitting was applied in this check. Pixel equality among visible protected body areas is only about0.0092%/0.0046% for half/closed. The exact rig equality test remains unchanged. Its source pixel counts are not semantic animation-quality scores; runtime-scale visual assessment is separate.

`review.html` is self-contained with96px whole-canvas references, source eye-detail crops and proposed1400/80/90/80/650ms timing. The GIF demonstrates reference ordering only; it is not a newly produced or admitted blink clip. Seven evidence checks pass, including source identities, canonical blob agreement, count honesty and retention of the reuse failure.

## Admission requirements

`admission-requirements.json` is a derived checklist subordinate to the queue and existing app contract. It requires source male likeness/eye/plumage/style approval; verified geometry/contacts and physical scale; unmasked drift review or a separately authorized fixed-neutral eyelid extraction; actual loop/transition/timing review; compatible shared export/palette/alpha; canonical species/reference/rights pins; and Mac existing-validator plus normal/reduced-motion/mirrored-yard playback. Git storage proves recoverability, not admission. No half/closed eye patch was extracted or edited here.

Reproduce within the complete canonical source archive (which already contains the referenced frame bank/PNGs):

```sh
python3 build_reference_set.py
node verify_quiet_sampler.mjs
python3 verify_reference_set.py
```

The canonical cloud checkout is consulted for an additional committed-byte check when available; other environments report that optional verification as skipped rather than inventing a success. No model/runtime dependency install occurs.

Current next action: existing Mac RGBA intake and opt-in yard review of the actual three-drawing blink in runtime-assessment-v2. The separate female phase1 jaw/phase3 overlap remains pending owner review; no further seam edit or generation occurred in this slice.
