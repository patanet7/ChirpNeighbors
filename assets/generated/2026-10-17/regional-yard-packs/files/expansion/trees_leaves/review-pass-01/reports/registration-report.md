# Engelmann oak registration review01

**Precise branch attachment: HOLD.** Common-canvas placement is verified. The broad static composition remains a coherent candidate. No production transform, new sprite, new art generation or edit to the frozen Engelmann oak batch was made.

The reviewed variants are `plant.engelmann_oak / wood_scaffold` and `plant.engelmann_oak / canopy_healthy`. Both are 1254×1254 RGBA images on the same identity placement with root pivot (680,1157). Re-compositing the exact source layers reproduces the frozen composite pixel-for-pixel. The preserved source metadata includes placement/contact ellipse, scale, seasonal needs, wind attachments, exact earlier prompts and original generation lineage. All 10 declared production originals/derivatives/style-reference files and four previously frozen archive hashes still match their recorded values. The frozen source manifest also matches the copy taken at review start.

Full-resolution source pixels and six enlarged regional triptychs were inspected, followed by audited marker crops. The canopy carries its own brown shoot strokes. Some upper/inner forks have apparent counterparts with differing local offsets; left and outer bough regions contain ambiguous or differing daughter-branch patterns. The wood and canopy are independently authored images, so nominal counterpart selection is an interpretation rather than ground-truth shared geometry. Natural exposed twig tips alone are insufficient to establish a defect. The HOLD concerns local shoot/junction inconsistency and missing unique correspondences.

Three nominal visible fork centers were retained after enlarged marker review. One proposed left-upper correspondence was rejected because its local fork topology was not uniquely comparable. Left/right outer regions were also excluded from point scoring and remain visual attachment holds. Excluding them does not establish alignment there.

| Nominal fork | Wood point(x,y) | Canopy point(x,y) | Required canopy-to-wood shift | Identity residual |
|---|---|---|---|---|
| U: upper |568,328|558,278|+10,+50|51.0px|
| C: central inner-left |529,574|523,581|+6,−7|9.2px|
| R: right upper |913,542|938,536|−25,+6|25.7px|

Manual picking uses an assumed conservative radial 6px tolerance per image, giving a 12px positional difference bound. This is a working annotation tolerance, not a statistical confidence interval or measured inter-rater accuracy. Semantic correspondence ambiguity remains separate. The values describe these three nominal picks only; they are not a population estimate of every attachment in the crown.

For those three picks, identity RMS distance is 33.3966px. Their least-squares common translation is (−3,+16.3333)px; residual RMS becomes 28.9751px, a 13.24% reduction. The mean distance changes only 28.64→28.47px. Required local translation vectors differ pairwise by 33.6–57.1px. Radius 12px tolerance disks around those required shifts do not intersect. Thus one global translation cannot satisfy even this limited annotated set within the assumed picking tolerance. The diagnostic JPEG uses the rounded shift (−3,+16) only to show the tradeoff; it is not a production derivative or an approved placement.

No unconstrained affine fit is claimed. Three point pairs can be exactly interpolated with six affine parameters; doing so would overfit these ambiguous nominal landmarks and would not establish matching branch identity, hidden geometry or daughter-branch topology. There is insufficient evidence to deliver an affine revision as a fix. A global transform also cannot remove extra authored shoot strokes or create missing shared branch anatomy.

Alpha overlap is recorded only as an occlusion diagnostic. Leaves and canopy-authored shoots both contribute alpha, so overlap is not a branch correspondence or attachment metric. The decision combines manually audited source features, local topology, uncertainty and diagnostic residuals. No scalar score changes the HOLD to a pass.

Evidence files: `analysis/landmarks.json` contains exact picks, uncertainty, rejected-pair rationale and excluded regions; `reports/registration-metrics.json` contains reproducible arithmetic and preserved source geometry/generation metadata; `overlays/landmark-vectors.jpg` locates measured picks; `overlays/identity-vs-translation.jpg` shows the unapproved global-shift diagnostic; regional triptychs and marker crops show the underlying pixels. These composites and overlays are derived review evidence, not independently generated art or additional sprite variants.

To reproduce the arithmetic and principal overlays, run `python analysis/measure_registration.py` from this package. Pillow and NumPy are required. All required source PNGs, frozen metadata, nominal landmarks and expected composite RGBA hash are included; a live original workspace is optional. The script reads a live frozen source location if it exists and writes only within the extracted review package. Re-running changes the report timestamp but preserves the numerical inputs/method.

The production lesson is to lock woody geometry and author foliage masks against it, rather than relying on a generated overlay to reproduce branch structure. A future controlled revision should remove or explicitly reconcile the canopy's second shoot network, inspect the same regional forks and add unambiguous correspondence evidence before claiming precise registration. This review does not perform that art revision.

Botanical identity, strict pixel-art style approval and owner acceptance remain pending. State/wind/emitter fields remain metadata, with no physics, animation or runtime integration added. Root coordinator inspected U/C/R marker crops and regional triptychs, independently reproduced the RMS arithmetic, and agreed with the attachment HOLD. Canonical intake of this review evidence remains pending through parent/Mac. No image-generation call was submitted, retried or left running in this pass. No Git/application/index changes were made.
