# San Diego regional yard source packs

This source-only publication preserves the completed San Diego starter and expansion work under existing asset IDs. It adds missing generated originals, individual sprites/layers, exact non-sensitive prompts, contact/review images and portable metadata. Files already present in the canonical repository are reused by SHA-256; no application, saved-yard store, active catalog or resident pin is changed.

Start with `manifest.json`. Every `canonical_path` is relative to the repository root and resolves to actual file bytes; aliases may point into earlier canonical packs. Each entry records the original source hash and the published hash. Generated image bytes and safe prompts are unchanged. Public metadata copies remove private transport/conversation locators and replace machine-specific paths. ZIP wrappers, private analysis, proprietary reference images and local transport helpers are excluded. HTML image data is extracted exactly and referenced through relative canonical files, rather than embedding another art copy.

## Delivered batch coverage

| Track | Covered deliveries | Review boundary |
|---|---|---|
| Objects | Original 12 objects; 20 theme variants; eight wave03 variants; one revised glazed pedestal variant; functional/readability evidence | 41 variant records across 38 primary IDs. Native and registered revision PNGs are one variant. Feeder/bath/fountain points and footprints are proposed metadata, with runtime calibration pending. |
| Plants | Original nine entries; eight expansion entries plus four dry/spent alternatives; eight wave03 entries; revised needlegrass; starter compatibility catalog/contact sheets | 30 delivered whole-plant variant records. Original needlegrass morphology hold and revised candidate qualifications remain. Healthy/dry variants are mutually exclusive states per instance. |
| Trees/leaves | Seven sycamore variants; nine Torrey pine variants; six Engelmann oak variants; attachment review; foliage-method pilot and rejected history | 22 production variant records. Engelmann canopy attachment remains held. Four experimental leaf clusters are method evidence and count as zero production assets. |
| Backgrounds | Original three yards; courtyard proof01; coastal wave04; oak wave05; Mediterranean wave05; readability and offline wind evidence; starter foundations and previews | 20 generated original images across those static scene batches, including held/history. Three clean starter foundations are available. Render plates may contain flattened scenery; no universal per-plant editability is claimed. |
| Starter | Three background choices, six existing plant sprites and three existing object sprites; compatible regional/patio option groups | Nine reused whole sprites, no new placeable primary IDs. Catalog distinguishes 19 outdoor/patio families from six interior-only families. |

The per-track `coverage/*.json` files preserve source identities, state needs and detailed batch/file mappings. The reconciliation index counts source records and aliases, not distinct usable assets or completed generation calls. Stored prompt records also include queued design text; publication generated no new art.

## Use the clean starter foundations

The repository-ready starter selection is in `starter-intake.json`; its source copy is retained at `files/expansion/starter-pack/root/ChirpNeighbors-San-Diego-Starter-Intake.json`. The offline movable-sprite art preview is `files/expansion/starter-pack/root/ChirpNeighbors-San-Diego-Editable-Asset-Preview.html`; open it within the checkout so its relative image references resolve. Its save controls use browser-local storage only. JavaScript syntax and exact static image replays are checked; interactive browser execution remains unverified in the cloud environment.

- Coastal wave04: registered distance coverage plus ground; omit both optional near pot/trunk and foliage plates. Distant scenery and painted ground texture remain fixed.
- Oak wave05: corrected distance r2 plus ground; omit optional compound oak dressing. The opaque r2 also contains flattened soil/stone scenery. The optional foliage output contains major wood, so it stays static and held for leaf-only wind separation.
- Mediterranean wave05: sky plus clean architecture/paving with empty planting space. Place foreground plants/pots/furniture using independent shared sprites.

The original three yard bases and courtyard proof01 retain baked local vegetation. Omitting their optional overlays does not make that vegetation editable. No usable independent oak sprite is presently included in the audited local packs; held Engelmann parts and static oak scene dressing are not substitutes.

All three starter sources use 1536×1024. The declared review mapping crops `[0,160,1536,1024]`, then scales uniformly to 960×540 or 384×216. Full originals are preserved. This is a review contract; actual Mac fitting, source-to-world scale, plant editing/save mappings, functional contacts, occlusion and owner acceptance remain pending.

## Publication and next work

Source storage does not accept art or implement animation/physics. Generated/reviewed candidate states remain distinct from application staging, integration and acceptance. Minor visual imperfections may be provisionally usable at normal small display size; existing obvious contact or attachment holds remain explicit.

No new background samples are running. After publication is verified, prioritize canonical Mac intake, independent oak attachment, actual branch/foliage/grass masks and rigs, and regional healthy/dry/seasonal states. Other regions/themes remain queued after the first San Diego customer milestone. The previous offline wind preview moves one compound branch only; it is not a full wind hierarchy.

Run `python3 assets/generated/2026-10-17/regional-yard-packs/verify_publication.py` from the repository checkout to check canonical file hashes, unchanged safe prompts, portable image references, privacy exclusions and duplicate source bytes.
