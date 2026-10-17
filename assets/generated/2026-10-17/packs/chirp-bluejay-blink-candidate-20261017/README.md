# ChirpNeighbors blue jay blink candidate

Actual source-based blink: original open eye, half blink, fully closed, reopening. All frames are 1536×1024 RGBA. No global motion, scaling, warping, registration correction, masking or repainting has been applied to the source frames. Three frames were edited with the built-in image generator from the same original; these are new pixels, not a translated copy of one picture.

## Review result

Light and dark alpha-composited contact sheets show a recognizable blue jay with blue crest, black facial collar, white cheek, barred blue/black/white wings and long tail. The opaque-looking raw RGB haze is not a visible halo in these alpha composites. The half and closed eye differ clearly at larger size. At an approximately 72px silhouette width the blink is subtle and the wing detail is dense; do not call this a finished game-readable animation.

The same visible framing and foot positions are retained closely, but imagegen changes pixels outside the eye. Thus exact pixel lock fails. No frame has fully opaque alpha (max 254), inherited from the source's unusual alpha. Feet/body appearance remains similar, but is not byte-identical. This is a bounded animation candidate, not production-approved runtime art or proof of integration.

## Preview

- `preview.html`: local unchanged-image animation and fixed-scale light/dark comparisons; open after extracting archive. No network dependencies. Browser execution was blocked in this cloud environment by sandbox socket restrictions, so this HTML was not execution-verified here.
- `contact-sheet.png`: independently rendered light/dark composites and approximate 72px silhouettes, inspected visually. Row order: light, dark, small light. Columns: open, half, closed, reopen.
- `blink-preview.gif`: flattened light-background 300×200 animation preview; not a source asset.
- `blink-unchanged-frames.apng`: full-canvas RGBA frame assembly with no geometric edits. Decoder timing may round to source timebase; inspect timing metadata before runtime use.

Proposed timing: open 2200ms, half 70ms, closed 100ms, reopen 70ms, repeat. Proposed shared source pivot (1000,970), contacts (905,945) and (1060,975), from previous pack manual estimates; not a measured contact solver. All frames must use the same registration and scale 72/1315. Do not independently trim or center frames.

## Preserved evidence

Source open image is copied byte-for-byte from blue-jay-standing-v2.png in pack [private-source-reference-retained-locally], archive SHA256 88b4a740ad2d31fc9189101b4b27108b84b41910fe027b3a39066401f64cf5ab. Original generation outputs are in raw/. Prompt and QA measurements are in manifest.json. No user computer access or external paid model was used.

Next gate: choose whether this subtle blink is sufficient at 72px, then explicitly authorize a deterministic registration/alpha pipeline if needed. Integrate only as a candidate with runtime approval false until visual approval and actual runtime tests pass.

## Registration measurements

At alpha >128, whole-silhouette bounding-box edges differ by at most 1 source pixel; feet-region bounding-box edges differ by at most 1 pixel. Feet-region foreground centroids shift at most 1.033px horizontally and 0.171px vertically, approximately 0.057px and 0.009px at target scale. This measures masks, not exact corresponding foot contact landmarks. Non-eye pixels still change substantially, so exact pixel lock fails. See manifest per frame. APNG is preview only: runtime input is the four separate PNGs and durations.
