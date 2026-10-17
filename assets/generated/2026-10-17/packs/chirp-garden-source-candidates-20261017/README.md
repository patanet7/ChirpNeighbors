# ChirpNeighbors quiet garden: source-art candidates

Six original transparent PNG masters are included: one standing European-robin-like bird, a filled limestone bath, its empty variant, a seeded timber tray feeder, and a generic broadleaf tree in summer and autumn. All six are persisted in Library; IDs, hashes, canvas sizes and prompts are in `candidate-manifest.json`.

**Admitted runtime sprites: zero.** These are selected visual source candidates, not a production asset pack. They have not been integrated or activated. The 960 × 540 side-view yard and existing object/behavior contracts remain unchanged.

## What can be reviewed now

- Individual source PNGs and the consistent limestone/timber/foliage direction.
- A single standing bird pose. Its appearance suggests European robin; species identity is unverified. There are no animation clips.
- Empty-bath material and shape plus `bath-mask-proposal-v1.json`, a proposed water area and front-rim occlusion annotation. There is no final raster water mask.
- Summer/autumn appearance. The canvas and bottom ground extent agree, with zero best translational shift in the tested trunk/root mask regions. Exact branch landmarks and contacts are unverified. No tree perches are defined.

## Hard acceptance gaps

1. Every raw master is over 512 KiB, has excessive dimensions for admitted bird frames, and retains partial alpha. The robin has 422,141 partially transparent pixels and no fully opaque pixels. These PNGs are not binary-alpha sprites or verified limited-palette art. The visual pixel-art style does not establish technical pixel-art compliance.
2. A targeted halo-removal generation did not solve the robin edge halo. Its output is excluded from the selected pack; the better original is preserved. No further cleanup loop ran.
3. The filled bath contains baked water. It cannot serve as a custom physical-water bath skin. Empty and filled images have similar silhouettes, but they are not identical registered layers. Parent-reported local audit found only 0.57% exact RGBA agreement (audit ROI/denominator not supplied here). The water mask, occlusion, shared transform and foot supports need local visual/physics review.
4. Uniformly fitting the bath to width 100 gives approximately 68.7 world units of silhouette height, not the catalog's height 80. Current bath supports remain ±18, −68. No accepted transform has been selected.
5. Full foliage overlap is not the sole seasonal registration gate. Separate root/trunk metrics are in `reports/pack-inspection.json`; major branches, a shared root pivot and occupied contacts need independent checks. There are currently no occupied tree contact anchors.
6. The intended packed/world frame sizes in the manifest are proposals. No packed frames are included. Trees are foliage candidates, not bird-format submissions. Proposed tree size must be reconciled with the eventual foliage media contract.
7. The light/dark scale study is `review/index.html`. It uses original PNGs unchanged with explicit CSS frame sizes. The cloud browser screenshot failed at launch due to sandbox restrictions; native-size frame acceptance is therefore **not claimed**. Individual masters were visually inspected at source-preview scale.

## Exact artifacts and reproducibility

- `sources/`: six unchanged selected image-generation outputs.
- `prompts/`: original creation/edit prompts. Model name and seed were not exposed. Generation is not bit-deterministically reproducible; the exact stored masters are preserved by SHA-256.
- `candidate-manifest.json`: provenance, native Library IDs, proposed sizes, composable theme/region/season/state, optional future plant identity, and explicit pending status. This is a review sidecar, not an alternative runtime schema.
- `bath-mask-proposal-v1.json`: approximate source-coordinate water/rim metadata and proposed review tolerances, not approved physics geometry.
- `inspect_pack.py`: read-only hash/alpha/root-region checks; requires existing Pillow and NumPy. It does not write or change image pixels.
- `build_review.mjs`: local HTML scale-study generation and optional Chromium screenshot; requires existing Playwright/Chromium. The HTML is already included. No install or external provider is needed.
- `execution-ledger.jsonl`: timestamped verification/render attempts, outputs, elapsed time, exit status and actual state. Historical generation timing was unavailable after workspace replacement and has not been invented.

Run `python inspect_pack.py` from this directory to repeat verification. The reference and prior runtime-handoff Library bundle IDs remain in the manifest. No prior Blender art or failed halo repair is included in these six selected sources.

## Next gate

Have the local Chirp lane select one visual candidate, then approve its crop/scale, palette, alpha treatment and contacts under the existing native validator. Follow `admission-proposal.md`. Do not create more oversized variants until this conversion and display-size gate works. The future pack scope remains restrained themes, seasonal foliage, object states and decorations; owner-supplied plant identity would be a separate reviewed metadata input.
