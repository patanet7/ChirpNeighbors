# Artwork and reusable assets

Canonical requirements and acceptance for this topic. Stable IDs, decisions, dependencies and named evidence are retained from the [task index](../delivery/product-behavior-and-ideas.md). U: paths refer to the UI repository; M: paths refer to ChirpNeighbors. Evidence labels resolve through the [verification ledger](../delivery/verification-ledger.md). Current GitHub publication is tracked separately in the [release record](../publication/20261011/README.md).

The photo-conditioned species-art acceptance in PB-021 excludes a plain downsampled photograph: that does not satisfy the promised reusable species-art workflow. Reviewed anatomy, plumage, silhouette, contacts and animation consistency remain necessary.

### PB-003 — Shared canonical species/style/version assets are built lazily as species arrive; optional later variants may be added as needed.

**Source / decision:** user decision; Agreed. **Implementation:** Bounded fixture catalog implemented. **Integration:** Local integrated checkpoint. **Release / production:** See [current release status](../publication/20261011/README.md); historical local integration is not production validation.

**Architecture:** U:src/lib/server/assets/catalog-requests.ts; U:src/lib/server/assets/catalog-releases.ts; U:src/lib/server/assets/catalog-selection.ts; U:src/lib/server/runtime.ts.

**Behavioral acceptance:** Two owners requesting the same supported arriving species dedupe one owner-free canonical identity; immutable explicit releases and per-resident exact pins survive version publication, revocation, missing bytes and restart; private inputs never enter shared catalog records.

**Tests and evidence:** [U:src/lib/server/assets/catalog-releases.test.ts](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/src/lib/server/assets/catalog-releases.test.ts); [U:src/lib/server/assets/catalog-selection.test.ts](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/src/lib/server/assets/catalog-selection.test.ts); [U:scripts/shared-catalog-browser-checks.py](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/scripts/shared-catalog-browser-checks.py). [E-CAT:shared-catalog/shared-catalog-browser-results.json](../delivery/LOCAL-EVIDENCE.md); [E-CAT:ui-unit.log](../delivery/LOCAL-EVIDENCE.md).

**Representative exact assertions:** catalog-selection.test.ts: “shares one approved render between two named residents without copying private sources or observations”; catalog-selection.test.ts: “keeps publication disabled on the authenticated selection service even in local mode”; E-CAT browser result: “Publishing fixture version two leaves both residents pinned to version one”.

**Dependencies:** PB-001, PB-013, PB-014, EN-001. **Remaining gap:** Production promotion authority, approved rights/art and provider execution are unavailable; optional variants are contract identities without enabled authoring. **Next action:** Keep default-deny production promotion; obtain PB-021 inputs before enabling real releases.

### PB-014 — Reviewed source rights, provenance and immutable shape/animation workbench precede reusable artwork.

**Source / decision:** user decision; Agreed. **Implementation:** Reviewed manifest/shape pipeline implemented. **Integration:** Local integrated fixture checkpoint. **Release / production:** See [current release status](../publication/20261011/README.md); historical local integration is not production validation.

**Architecture:** U:src/lib/assets; U:src/lib/server/asset-pipeline; U:src/lib/server/assets/resolve.ts.

**Behavioral acceptance:** Validate exact species/source/pin/pose provenance, frame bounds/durations and clip fallback; inspect every frame including unused ones; approval never implicitly pins; immutable geometry revisions preserve pixels and invalidate caches by owner/version/review; missing/corrupt dependencies retain identity and explicit fallback.

**Tests and evidence:** [U:src/lib/assets/manifest.test.ts](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/src/lib/assets/manifest.test.ts); [U:src/lib/assets/manifest-v3.test.ts](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/src/lib/assets/manifest-v3.test.ts); [U:src/lib/assets/pose-geometry.test.ts](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/src/lib/assets/pose-geometry.test.ts); [U:src/lib/server/asset-pipeline/revise-shape.test.ts](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/src/lib/server/asset-pipeline/revise-shape.test.ts); [U:scripts/manifest-browser-checks.py](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/scripts/manifest-browser-checks.py); [U:scripts/shape-browser-checks.py](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/scripts/shape-browser-checks.py). [E-CAT:manifests/manifest-browser-results.json](../delivery/LOCAL-EVIDENCE.md); [E-CAT:shapes/shape-browser-results.json](../delivery/LOCAL-EVIDENCE.md); [E-CAT:image-v3/image-v3-browser-results.json](../delivery/LOCAL-EVIDENCE.md).

**Current renderer evidence:** [E-PERF](../delivery/renderer-performance-20261010.md) adds renderer-local revision/frame/pivot cache keys, explicit leases, retirement on replacement and concurrent-owner disposal. Corrupt/missing/replaced assets and clip fallback retain exact fixed-ticker pixels and state; 65 pairs pass. This does not certify fixture species fidelity.

**Dependencies:** EN-001, PB-013, PB-020. **Remaining gap:** V2 compatibility is backward reading, not universal old-client acceptance of V3. Private PNG/JPEG reference admission is implemented under E-REF; approved concept/species pixels, real generation/segmentation and fidelity acceptance remain unavailable. **Next action:** Acquire reviewed inputs under PB-021; do not certify fidelity from fixture mechanics.

**Planning/review boundary (E-PLAN):** Versioned production plans and reference-discovery snapshots are separate retained private metadata artifact kinds. Immutable approval cannot make either an animation manifest. Existing reviewed source/manifest pin and cache authorities remain the only renderable path; archive/restore and owner tests preserve current pins and yard data.

**Current admission slice (E-REF; local integrated checkpoint):** Independent private reference-file authority now retains bounded original/canonical bytes, explicit rights/species/pose owner assertions, terminal revocation and exact reference pins. Queue, execution, completion and candidate review recheck current action and direction/viewpoint authority through the existing runner; late results and stale/missing/corrupt dependencies cannot advance. [Service tests](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/src/lib/server/reference-admission/service.test.ts) and [provider tests](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/src/lib/server/asset-pipeline/reference-generation.test.ts) cover the bounded path. For the current right-facing-mirrorable recipe, a left or right reviewed viewpoint is required; front/back/three-quarter/other alone cannot authorize it. Owner review is not automatic biological/legal certification; even approved diagnostic candidates cannot become renderable manifests, resident pins or shared artwork.

**All asset families, one lifecycle:** The user’s pipeline requirement covers bird clips, catalog objects, foliage, season/state variants, decorations and weather layers. PB-014/020 own shared bounded byte intake, immutable source/derivative provenance, rights review, candidate/package review, exact version identity and explicit selection/pinning; PB-021-B and PB-011-E/F/PB-023 retain family-specific visual/runtime acceptance. Reuse those authorities and runner/cancellation/retry boundaries rather than build a bird-only research path or a parallel generic production contract. Common stages are source intake → exact lineage/rights review → family-specific plan/validation → bounded packaging → actual-runtime review → explicit immutable selection/release. Approval of a source, diagnostic, plan or review export is never automatic production approval or a render pin.

| Asset family | Family-specific contract and acceptance |
| --- | --- |
| Bird clips | Existing species V2/V3/V4 canvas/frame/palette budgets, authored direction, pivots/pose contacts, timing/loop/transition and missing-clip fallback; actual-species fidelity stays separately reviewed. A bird atlas cannot enter through scenery limits. |
| Catalog objects | Existing kind/dimensions, ground pivot, physical footprint, slot/contact/capability identity and ground-y depth; cosmetic skins preserve stable placed instances. Geometry changes require explicit validated support/collision/placement transactions. |
| Foliage | Separate scenery or explicitly admitted object family; reviewed layer/occlusion, pivot and bounded wind displacement. Paint cannot silently add walkable ground, shelter, perches, collision or species identity. |
| Season/state variants | Independent selectors with compatibility and deterministic base fallback, exact variant provenance and unchanged cosmetic geometry. Do not require a full Cartesian product or silently change capabilities. |
| Decorations/addable items | Decorative layer content and inventory-backed placed items stay distinct. New kinds need bounded placement/inventory/migration/capability authority; images alone cannot add objects. |
| Weather layers/effects | Explicit layer/depth, time/seed/replay, primitive/palette bounds and held/reduced-motion behavior. Procedural effects, authored frames and SI mass remain separate; no weather measurement or ecological claim is implied. |

**Current bounded implementation slice (source verified; browser acceptance pending):** Explicit family guards, deterministic review export, cancel/retry sessions and truthful clip-transition diagnostics are implemented at UI `d4130c5c424199ad53c5e59b29643dd232de4827`, committed/pushed on the working branch with 22 source hashes matched to committed blobs. The [pipeline/texture source receipt](../delivery/surface-workbench-20261017/pipeline-texture-verification.json) records the exact affected **67/67 tests in five files**: 21 family/package, 10 session, 15 transition, 13 texture-profile and 8 preview cases. Full units are **2,310 passed / 32 exact baseline failures of 2,342**, zero pending/introduced failures; the full suite is not green. Svelte, strict typing/declarations, lint/format/analyzers, contracts/clients and build pass. Independent asset-page 9 and texture-page 5 race probes passed with no remaining findings; HTTP checks pass 19/19 development and 4/4 expected production refusals/guards. Source/race review is complete for this checkpoint; actual GPU/browser/visual approval remains pending. Admit only families actually supported by that schema; reject unsupported/wrong-family payloads rather than route bird/foliage/effect content through looser object/layer limits. Identical admitted inputs and options must yield identical review-export bytes/order/digests and retain `unreviewed`/`productionApproved: false`. Cancel/replace/retry must fence late results, preserve prior accepted selection and owner scope, and avoid duplicated exports or implicit jobs/provider dispatch. Export is a review artifact, not persisted pin/publication; restoration/pinning for additional families requires the existing explicit versioned authority. Retain named source/test/HTTP/browser evidence before expanding a verified status beyond these reported focused checks.

#### PB-014-A — Reuse retained asset validation within one request

**Status / priority:** Open P2 for repeated source hydration; the measured owner/job artifact index is implemented locally. **Evidence:** JAQ-01 / EI-001 in the [integrated query audit](../architecture/integrated-query-audit-20261012.md). **Dependencies:** EN-001, PB-014. This supplies shared request-local validation for PB-022-B.

**Work:** Share exact verified source/dependency results within one request snapshot across selected artwork, preserving graph visit/depth limits and review/rights checks. Current per-package resolution rereads a shared ancestor. Use request-local validated data, not a global authority cache. Existing startup index migration is nonunique and leaves v1 rows/contracts unchanged.

**Acceptance:** Instrument 1/8/24 selected packages sharing an ancestor and branching/deep graphs. Hydrations should track unique retained nodes/edges, with identical pixels/pins/status. Corruption, review rejection, foreign owner, revoked rights, archive/new-selection distinction and version changes remain enforced. Upgrade/reopen/busy/query-plan tests preserve every source/review/version byte. Re-measure in a quiet run after the index; pre-index shared-cloud timings are not final SLO evidence.

### PB-018 — Track generation resource usage and unknown costs accurately.

**Source / decision:** user decision; Agreed. **Implementation:** Contracts and pure helpers implemented. **Integration:** Helper tests verified; runtime dispatch accounting absent. **Release / production:** See [current release status](../publication/20261011/README.md); historical local integration is not production validation.

**Architecture:** U:src/lib/pipeline/generation-usage.ts; U:src/lib/server/pipeline/generation-usage.ts.

**Behavioral acceptance:** Synthetic usage summaries separate adapter attempts, elapsed duration, cache/admission/review and unknown costs; reject overflow and spoofed provenance; shared/private fingerprints keep owner scope distinct. Future dispatch must durably record actual attempts and settle budgets/cancellation/retries.

**Tests and evidence:** [U:src/lib/server/pipeline/generation-usage.test.ts](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/src/lib/server/pipeline/generation-usage.test.ts). [E-CAT:ui-unit.log](../delivery/LOCAL-EVIDENCE.md).

**Representative exact assertions:** generation-usage.test.ts: “defaults monetary costs to unknown, including local fixture compute”; generation-usage.test.ts: “does not count blocked stages, cache hits, admission or review as dispatches”.

**Dependencies:** PB-003, PB-013, PB-014, EN-006. **Remaining gap:** No runtime caller of summarizeGenerationUsage/privateGenerationFingerprint/sharedGenerationFingerprint; no durable usage ledger, live metering, budget enforcement or actual provider dispatch. Stage claims are not provider calls. **Next action:** Implement durable accounting alongside a separately authorized real execution adapter; retain unknown monetary cost.

### PB-020 — Owner-supplied local PNG bytes become reusable animation candidates through separate file, source and manifest reviews, then an explicit resident pin.

**Source / decision:** user decision; Agreed. **Implementation:** Bounded local PNG intake implemented. **Integration:** Local integrated fixture checkpoint. **Release / production:** See [current release status](../publication/20261011/README.md); historical local integration is not production validation.

**Architecture:** U:src/lib/server/image-files; U:src/lib/server/asset-pipeline; U:src/lib/assets.

**Behavioral acceptance:** Real private PNG bytes pass maintained bounded decoder, dimensions/inflate/grid limits, metadata stripping and hidden-RGB removal; separate per-file rights/source/manifest reviews precede explicit immutable resident pin; owner switch/retry/restart/backup/corruption and Pixi/SVG paths pass.

**Tests and evidence:** [U:src/lib/server/image-files/decode.test.ts](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/src/lib/server/image-files/decode.test.ts); [U:src/lib/server/image-files/service.test.ts](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/src/lib/server/image-files/service.test.ts); [U:scripts/png-intake-browser-checks.py](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/scripts/png-intake-browser-checks.py). [E-CAT:png-intake/png-intake-browser-results.json](../delivery/LOCAL-EVIDENCE.md); [E-CAT:ui-unit.log](../delivery/LOCAL-EVIDENCE.md).

**Dependencies:** PB-013, PB-014. **Remaining gap:** Upload alone grants no reuse/derivative rights. Existing displayed pixels are fixtures; bounded PNG/JPEG reference-file admission now exists under E-REF, while real generation, approved actual-species artwork and account erasure remain absent. **Next action:** Use reviewed actual-species inputs only after PB-021 dependencies; preserve per-file rights gates.

**Current admission slice (E-REF; local integrated checkpoint):** Private PNG/JPEG reference intake is an implemented separate profile from the PNG sprite-atlas path: 2 MiB original, 2,048 edge and 1,048,576 decoded-pixel limits, bounded supported formats/metadata/decode work, private immutable original/canonical/RGBA hashes and owner-only canonical previews. Tests use technical images, not approved species photographs. This path preserves atlas limits and grants no artwork pin. Ordinary restart is supported; initialized reference-store cold restore is refused until an explicit revocation recovery protocol exists. [Decoder](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/src/lib/server/reference-admission/decode.ts), [workbench](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/src/routes/references/+page.svelte), [recovery controls](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/src/lib/server/operations/reference-recovery.test.ts).

**Recovery extension (E-REC; local integrated checkpoint):** An explicit full reference-authority export and independently retained latest digest now extend the existing offline backup/restore path. The backup and latest authority must contain the same admissions; later reviews/revocations/retry receipts are reconciled only after complete validation. Default refusal, private owner isolation and the separate atlas/artwork authority remain intact. This does not validate actual-species imagery or enable generation.

**PB-020 family boundary:** The shared exact-byte decoder/provenance/rights machinery may serve multiple asset families through their own bounded admission profiles. Reusing machinery does not make the bird animation manifest an object/scene/effect contract or authorize a scenery review package as a resident asset. Retain original/canonical/RGBA and derived-package identities, owner isolation, cancellation/retry and revocation lineage across families; keep current private/public and production-promotion refusals intact. Additional family packaging, persisted pins and reader migrations are planned unless current implementation evidence explicitly establishes them.

### PB-021 — Actual-species reference photos should guide highly detailed species-correct reusable sprites and animations, paired with visually simple regional yards.

**Source / decision:** user decision; Agreed. **Implementation:** Fixture mechanics, versioned planning/public source discovery, private PNG/JPEG admission and a local diagnostic bridge; production artwork absent. **Integration:** Planning/discovery Local integrated checkpoint under E-PLAN; E-REF supplies a complete frozen local reference/diagnostic checkpoint. Actual-art workflow remains unintegrated. **Release / production:** See [current release status](../publication/20261011/README.md); historical local integration is not production validation.

**Architecture:** U:src/lib/server/asset-pipeline/image-stage.ts; U:src/lib/assets; P1–P4 in visual task tree.

**Behavioral acceptance:** Authorized actual-species references and per-file rights bind each master/frame/action; reviewer verifies anatomy, plumage, silhouette, contacts and temporal consistency against available approved references before shared reusable release; simple regional scenery remains separate.

**Tests and evidence:** [U:src/lib/server/asset-pipeline/image-stage.test.ts](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/src/lib/server/asset-pipeline/image-stage.test.ts); [U:src/lib/server/asset-pipeline/pipeline-v2.test.ts](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/src/lib/server/asset-pipeline/pipeline-v2.test.ts). [E-CAT:ui-unit.log](../delivery/LOCAL-EVIDENCE.md).

**Dependencies:** PB-003, PB-004, PB-011, PB-014, PB-020. **Remaining gap:** Tests cover fixture mechanics, deterministic plans, source metadata discovery and pipeline boundaries, not actual artwork acceptance. Approved reference/concept pixels were unavailable and not viewed. Local photo-format admission and saved-discovery acquisition authority exist, but successful live original-image retrieval, approved actual-species/concept inputs, image-generation adapters, biological review, model/output licensing and reviewed art remain unavailable. **Next action:** Obtain authorized inputs and named fidelity review before real frame production; do not create replacement art in this task.

**Planning and discovery extension (E-PLAN):** The shared [specification/recipe authority](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/src/lib/assets/animation-specification.ts), [compiler](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/src/lib/server/asset-pipeline/animation-planning.ts) and [persisted v2 definition](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/src/lib/server/asset-pipeline/animation-planning-v2.ts) implement nine default action proposals, 60 proposed frames, per-clip/frame prompts, exact input/specification hashes and strict overrides. V1 remains unchanged. Supplied declarations skip search; otherwise the configured Commons adapter searches public scientific identity and retains per-file rights/identity/pose metadata separately. Metadata candidates are not reviewed references or image-generation permission. Restart reuses discovery; corrupt request binding rejects; both metadata artifact kinds remain unpinnable even when approved. The normal workflow downloads no original images and produces zero pixels. [V2 persistence tests](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/src/lib/server/asset-pipeline/animation-planning-v2.test.ts), [discovery tests](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/src/lib/server/reference-discovery/discovery.test.ts) and [browser evidence](../delivery/LOCAL-EVIDENCE.md) establish this bounded workflow. Actual live discovery returned blocked/network-unavailable; approved reference/concept pixels, successful acquisition, a generation provider and fidelity review remain dependencies. This does not close PB-021 artwork acceptance.

**Current local work (E-REF; local integrated checkpoint):** Exact private reference bytes → explicit rights/species/pose owner reviews → immutable reference pin → registered local diagnostic provider is connected through the existing runner and private workbench. ENG-01 exposed missing viewpoint enforcement in UI 033c0ce; UI 53e4140 now requires an explicit left/right view for every current mirrorable side-view plan at server admission and UI readiness. Front-only approval remains valid history but cannot queue; six new unit cases and the clean 72-check browser flow cover the correction. The one-frame 4×4 output is a deterministic digest grid marked fixture/non-renderable, with zero external/model calls; it is not bird art and cannot pin into the renderer, even after candidate approval. Nine clips / 60 frames remain production proposals with zero species-art frames generated. The current Commons diagnostic records DNS failure and ordinary HTTPS proxy 403 denial without bypass; live source acquisition, approved actual-species/concept material and a reviewed model bundle/provider remain later dependencies. [Local bridge](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/src/lib/server/asset-pipeline/reference-generation.ts), [acquisition authority](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/src/lib/server/reference-acquisition.ts).

#### PB-021-A — Stop discovery at cancelled request boundaries

**Status / priority:** Implemented and verified locally on Linux; the frozen UI quality and bounded integration receipt is complete for `926ab9f02d4f50f0349d00a2d11cc7a9477db0d5`. The original cancellation defect was P2. **Review:** JA-01. **Dependencies:** existing runner/discovery interfaces and EN-001 semantics. This bounded fix does not depend on obtaining EN-006's original worker, approved art, providers or GPU selection. Local integration `cea846388f4f67a3858dce00c690623419c5cc3e` and four added cancellation regressions are recorded in the [local follow-up](../architecture/architecture-review-20261012.md#local-implementation-follow-up); no publication is claimed.

**Work:** Propagate persisted cooperative cancellation into every discovery page/retry dispatch boundary while preserving per-job isolation, deadlines, lease fencing and late-output rejection. Cancellation cannot undo a request already sent; do not promise in-flight abort without testing it.

**Implemented limit:** Persisted cancellation is observed at bounded request/admission/retry boundaries. A fetch/read or delay already awaiting completion is not synchronously interrupted by a database status change; the existing AbortSignal/deadline still bounds it. No later page/retry dispatch occurs once cancellation is observed.

**Acceptance tests:** Pause page one, cancel the job, then release the page with a next cursor; no next page/retry may dispatch and no output may commit. Cover simultaneous independent owners/jobs, cancellation after completion, deadline abort, ordinary multiple-page success and late completion fencing. [Two-call stub reproduction and source locations](../architecture/architecture-review-20261012.md#jobs-providers-and-asset-lifecycle).

#### PB-021-B — Review actual species art and action clips

**Status / priority:** Visual acceptance **failed by the user** for the delivered fixture-art screenshot. Four approved direction-reference boards and provenance/specification/pose-contract material are now privately materialized; they are reference inputs, not admitted production packs. The usable target is **960×540 side-view**; initial dimetric/isometric cloud studies are incompatible runtime art. Fidelity acceptance remains blocked on actual compatible art, rights and visual review; P2 product acceptance, not a routine-engine regression. **Review:** RG-003, retained jobs/assets input gaps and the user's subsequent visual rejection. **Dependencies:** PB-014/020 rights/provenance, retrieval of the approved concept/actual-species pixels, a separately selected compatible execution adapter and named biological/art review. GPU choice remains pending; no purchase or provider activation is implied.

**Acceptance tests:** Deliver an immutable reviewed species manifest with the approved action/clip scope; verify every frame/pose bound, timing/contact/geometry, license/provenance and version fallback. Review actual normal/reduced-motion/Pixi/SVG output for anatomy, plumage, silhouette and temporal consistency against approved references. Nine engine states or sixty proposed frames are not delivered authored clips. Plain photo downsampling and diagnostic grids do not satisfy this acceptance. Keep PB-003 production promotion default-deny until its rights/release authority is met. [Observed fixture limits](../architecture/architecture-review-20261012.md#renderer-simulation-and-game-behavior).

**Current visual direction:** The bounded source-density/layout implementation is recorded under [PB-011-C](yard-and-behavior.md#pb-011-c--separate-artwork-detail-from-world-size-and-restrain-the-ui). Source pixel detail and on-screen world size are separate decisions. There is **no user approval of a 32px art canvas or world footprint**; a fixture dimension is not design authority. Reference transfer does not establish matching species/scene pixels or an admitted runtime pack; descriptions and technical test success cannot establish that match.

**Local art-lab follow-up (planning and engine integration, unpublished):**
`U:src/lib/workbench/production-plan.ts` supplies versioned local planning metadata
for `/art-lab`, reusing existing species/animation, scene and object authorities.
The bounded target is one European robin, one layered garden and a feeder, with
idle/moving/feeding contact and depth acceptance before expanding the clip pack.
Garden/courtyard concepts and perch/feed/bath/nest anchor comparisons are planning
inputs; existing five-frame/six-clip fixture art and absent sleep/play/nest clips
stay disclosed. No new production pixels or approval is implied.

**New review-only input boundary:** The asset owner is implementing an ephemeral development validator/actual-yard preview after the frozen 03:42 checkpoint. Reuse the exact scene/species parsers, resource budgets, world projection, pivots/contact anchors, provenance and seasonal declarations; reject incompatible side-view/world metadata and arbitrary extra fields. Keep review-only rectangles/layers and separate object art at unchanged world footprints; approval, persisted resident/scene pin and public canonical publication remain separate existing PB-014/020/003 decisions. No production art exists to approve yet. Normalized rectangle preview cannot stand in for general raster intake or a production scene extension, and cannot relax private V4/public V2 limits.

**Current review-package draft (not yet a verified release):** `U:src/lib/workbench/asset-package.ts` specifies strict `schemaVersion: 1`, `kind: workbench-review-package`, `scope: local-review-only`, `approval: unreviewed`, `productionApproved: false`, `projection: side-view-orthographic` and world 960×540. `validateReviewAssetPackage(metadata, files)` receives explicit declared PNG bytes rather than a path/URL/archive; metadata retains exact source/output SHA-256, creator/tool/version, unreviewed rights/license evidence and derivation operations. Layers are 240×135 source pixels projected ×4 for this bounded review slice; object PNGs match exact catalog dimensions, bottom-center pivots and slot anchors. This source grid is a tool constraint, not approved art direction or a change to world size. Explicit `base/spring/summer/autumn/winter` assets resolve by base then requested-season override; missing roles keep the existing fixture rather than inventing art. The draft review envelope is 12 files, 32,768 manifest bytes, 4,194,304 compressed bytes, 262,144 aggregate decoded pixels, 16,384 rectangles and 64 shared palette colors; these local scenery/object review limits do not relax species manifest limits. Partial alpha, undeclared files, digest/dimension/anchor mismatches and duplicate seasonal roles must reject. Named tests, route guards and actual pixels remain a separate current-source acceptance gate.

**Release boundary and future coordinated content:** The current local review delivery is unapproved and supports the four existing catalog kinds, three layers and explicit seasonal fallback at fixed pivots/anchors; it does not implement theme packs, object-state art, new decorations/items or plant identification. Record those future requirements under PB-011-E/F and this PB-021-B review authority rather than a parallel backlog. Theme/region, applicable season, state, weather response and decoration should compose independently with bounded reusable assets and deterministic fallback, not require every Cartesian-product image. A source metadata/theme/style flag is an unreviewed claim, not art approval, license clearance or permission for unknown parser fields. Preserve stable instance identity and geometry for cosmetic variants; geometry-changing states require separately reviewed collision/support/placement updates and safe reconciliation. Future owner plant references/photos need private provenance, uncertain candidates, human confirmation and distinct canonical/custom-art association; no external identification service is present. Source/species evidence and cosmetic selection must not be conflated.

Private V4 source density 1/2/4 does not bypass the 65,536 decoded-pixel/64-frame
bound or the 256-pixel source edge. The shared catalog public render path remains
V2-only, so globally reusable high-detail V4 assets need coordinated publication
and reader-contract evolution under PB-003. Preserve exact old pins and default-deny
production promotion. Canvas, frame reuse, proportions, palette and lighting need
actual visual review; neither the 32×32/60-frame proposal nor the padded fixture
canvas is approved direction. Reference rights/species review, separate bird/yard/
object production, bounded packaging, actual-yard interaction checks and immutable
catalog release remain the existing PB-014/020/021 gates. Explicit simulation can
exercise these engine behaviors but cannot establish real detection syncing.

**Quality/research scope:** Continue the all-family implementation under the shared PB-014/020 lifecycle, while PB-021-B retains actual bird fidelity and PB-011-E/F/PB-023 retain object/yard/foliage/variant/decoration/weather quality gates. The user’s prior quality rejection remains open: mechanically valid packages, style/theme metadata, research summaries and test passes do not approve pixels. The coordinator has now read both complete research/plan documents through Library. The earlier helper/materialization blocker is now resolved: both private documents were downloaded and size/SHA-256/version-0 metadata verified (35,514 and 7,021 bytes). A six-master bundle (7,078,683 bytes) was likewise hash/version-0/ZIP-CRC verified; only its README, admission and mask proposal were read, with no bundled instructions/code executed or assets activated. Detailed research, identifiers and competitor analysis remain in private custody. The bounded decision is to evaluate offline editor-owned authoring (Pixelorama is a candidate) and a manual-versus-controlled-keypose/motion comparison; no editor installation/selection, model execution, measured quality result or license clearance is established. No automatic model execution, paid generation, provider activation or dependency installation follows from the pipeline scope.

**Bounded pilot and texture-profile evaluation — PB-011-C/PB-021-B:** The active pilot stays one European robin with idle/moving/feeding coverage. Research suggestions for idle/hop/takeoff are comparison ideas, not a scope override. Evaluate a separately versioned, isolated RGBA texture profile against current rectangle rendering before any production admission decision. The coordinator reports five-run synthetic CPU-profile probe medians: 16×128×128 frames in a 512×512 atlas, 1 MiB RGBA / 235,052 PNG bytes, **22.87 ms**; 16×256×256 frames in a 1024×1024 atlas, 4 MiB RGBA / 906,871 PNG bytes, **78.04 ms**. These are CPU probe results, not GPU/render-frame timing, peak-memory measurements, art acceptance or a default-profile decision. Report decode/upload/cache/sample/render and memory scopes separately with identified hardware/backend and held/reduced-motion behavior before promotion. The [pipeline/texture source receipt](../delivery/surface-workbench-20261017/pipeline-texture-verification.json) now verifies the integrated source and exact affected 67-test scope, including all 13 profile cases; actual browser/GPU acceptance remains pending. Preserve every legacy manifest/pin, current limit, default renderer and public projection; the implemented isolated `chirp-texture-review-v1` profile bounds original/canonical PNGs and decoded RGBA at 4 MiB, atlas edge 1,024 / 1,048,576 pixels, frame edge 512, 64 stored frames and 256 sequence steps at 30 ticks/s. It retains straight RGBA8 with zero hidden RGB and one intended GPU premultiplication boundary. These experimental limits do not alter legacy manifests or approve production/public readers; compatible promotion/migration remains future work. Existing 64-color and 65,536-pixel limits are engineering guardrails, not user-approved quality requirements; the unapproved 32px proposal must not constrain the visual conclusion. Actual species identity/temporal/contact review, licensing and browser/GPU acceptance remain separate from synthetic cost and research recommendations.

**Next executable artwork task:** Prepare one deliberate European robin idle/moving/feeding candidate under a selected reviewed profile, retaining exact source, timing, pivot, foot/beak contact and transition metadata. Validate and preview it, then obtain actual visual/fidelity/rights/contact approval before any package pin/release. There is no approved art or automatic model run, editor installation, default change or resident pin from this source checkpoint.

#### Retained raven production case: reusable method, separate asset contract

The user-delivered [raven report and materialization receipt](../delivery/raven-production-20261017/README.md)
are now readable locally; the complete original and private identifiers were
preserved outside Git. The public report is explicitly redacted, with separate
original-source and public-copy size/SHA-256 records. This resolves **report access**, not access/validation of
the approved Chirp species concept. The raven case's final atlas and optional archive
were not downloaded here. Its reported completed rows, validation, motion metrics
and user acceptance are source statements, not independently checked atlas evidence
in this checkout. The mascot is pixel-art-adjacent illustration, not reviewed actual-
species anatomy or a demonstrated strict-grid/palette Chirp pack. It grants no new
source/model/output rights or production publication authority.

**Reuse within PB-014/020/021, without rebuilding the existing pipeline:**

- Freeze an approved canonical identity/reference revision before generating action
  variants; separately identify species, style, pose and layout reference roles.
  Keep exact source bytes/hashes, prompt revisions, accepted/rejected candidates and
  repair history. The report records actual descriptive prompts, magenta source
  generation with `transparent_background: false`, then reference-grounded state
  calls; underlying model/seed/resolution controls were not exposed. Preserve that
  limit rather than promising byte-identical regeneration from a prompt.
- Extract complete connected poses **before** equal-cell cropping or mirroring.
  Group detached toes/feather tips with their bird; the largest component alone can
  amputate anatomy. Register with stable anatomical/body scale, grounded baseline,
  pivots, padding and intentional airborne displacement. Do not independently fit
  every pose envelope: extended wings must not shrink the torso.
- Review chroma extraction against light/dark/saturated backgrounds. The case used
  RGB `(255,0,255)` source backing; antialiased edge mixtures require inspection,
  not indiscriminate colour-distance deletion. Chirp's binary-alpha/grid/palette
  admission remains a distinct deliberate conversion/review gate. No automatic
  chroma-key implementation or art replacement is supplied by this documentation.
- Retain anatomy/temporal failure cases and repairs: clipped tails required new
  complete source poses, handlike waiting gestures required natural wing mechanics,
  spread-wing hop fitting shrank the body, premature fixed-slot mirroring cut poses,
  and gaze generation reversed the body until head/neck motion was constrained
  separately. Empty-padding/edge tests cannot prove a source tail was never clipped.
  Foot gaps may be legitimate anatomy rather than holes to fill.
- Inspect contact sheets **and motion** at actual display size. The report records
  a 28-source-pixel hop, zero landing offset, 1.5-pixel gaze-centre drift and a 1.109
  gaze-width ratio; these are case measurements, not Chirp acceptance thresholds.
  Retain the ambiguous 292.5° vertical-gaze warning rather than converting a labeled
  acceptance into uniform blind-review success. Keep preview timing separate from
  runtime action binding; the report explicitly could not verify automatic event
  activation. Chirp still needs its actual sampler, support and transition review.

**Packaging boundary:** The report describes 73 populated pet frames in a
1536×2288 atlas with 192×208 cells. Its row names, sixteen gaze angles and pet
lifecycle are not Chirp's closed nine-action/right-facing-mirrorable contracts.
In particular the pet's `running` work/thinking row is not automatically locomotion.
The whole atlas exceeds Chirp's 256-pixel source edge; although an individual
192×208 cell fits that edge, 73 such frames total 2,915,328 decoded pixels and exceed
both the 64-frame and 65,536-pixel private pack limits (even two native cells exceed
the pixel budget). Repacking alone does not solve this. Review actual species
inputs, canvas/clip scope/frame reuse, palette/alpha and any separately versioned
resource/public-catalog extension before admission. Do not downsample the mascot
and claim species fidelity, pet-format compatibility or approved 32px direction.

**Next acceptance:** Reuse these extraction/registration/review techniques in the
existing one-species vertical slice only after exact input bytes and rights are
available. Bind accepted frames, timing, pivots, contacts and lineage to the existing
immutable manifests; run actual normal/reduced-motion/Pixi/SVG and fallback tests.
No raven media, pet identifier/selection, generation provider or new Chirp artwork
pin was installed by importing this report.

### PB-022 — Owners can reversibly archive private uploads/packages and unpin or restore resident artwork, with explicit retention reasons.

**Source / decision:** user decision; Agreed. **Implementation:** Reversible lifecycle implemented. **Integration:** Local integrated checkpoint. **Release / production:** See [current release status](../publication/20261011/README.md); historical local integration is not production validation.

**Architecture:** U:src/lib/server/assets/lifecycle.ts; U:src/lib/server/assets/lifecycle-storage.ts; U:src/lib/server/assets/resolve.ts.

**Behavioral acceptance:** Archive retains bytes/existing pins but fences all new selections/derivations including restore/automatic assignment; unpin/undo uses revision/pin CAS and durable receipts; incomplete reference graph fails closed; owner/session races, interruption and cold recovery preserve evidence.

**Tests and evidence:** [U:src/lib/server/assets/lifecycle.test.ts](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/src/lib/server/assets/lifecycle.test.ts); [U:scripts/asset-retention-browser-checks.py](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/scripts/asset-retention-browser-checks.py). [E-CAT:asset-retention/asset-retention-browser-results.json](../delivery/LOCAL-EVIDENCE.md); [E-CAT:ui-unit.log](../delivery/LOCAL-EVIDENCE.md).

**Dependencies:** PB-013, PB-014, PB-020. **Remaining gap:** No live purge, expiry job, account-wide erasure or authorization to destroy retained evidence; shared catalog read-only. History reachability repair is implemented locally (PB-022-A), with final verification recorded in its delivery receipt. **Next action:** Reduce repeated graph work without weakening conservative dependency scans; specify retention/erasure separately under EN-011.

#### PB-022-A — Keep archived history reachable

**Status / priority:** Implemented and verified locally; 18 dedicated history checks plus existing retention/renderer/core regressions pass. No publication is included. **Review:** JA-02 / ARCH-01–04 / JAQ-02 / JAQ-04 / EI-005. **Dependencies:** EN-001 versioned response/consumer compatibility and the existing owner-bound keyset pagination pattern. No provider/art input is required.

**Work:** Separate bounded visible lifecycle history from conservative whole-graph reference completeness. Provide versioned cursor pagination or exact-target retrieval, preserving archive/restore CAS, existing pins and old-reader compatibility. Raising the full-graph limit is not the repair.

**Acceptance tests:** With at least 513 valid jobs, restore the oldest archived package through the UI; exercise source metadata beyond the 32 MB graph budget as well. Cover tampered/cross-owner/stale-restart cursors, concurrent insertion, missing/corrupt dependencies, idempotent retry and account switching. An incomplete graph must never authorize purge or discard resident pins. [513-job reproduction and unexecuted overflow distinction](../architecture/architecture-review-20261012.md#jobs-providers-and-asset-lifecycle).

**Local implementation:** Separate owner-bound `asset-package-history-v1` pages retain all package rows independently of the full-graph scan. Standalone reads avoid the writer lock; byte guards and request admission fail closed; archive/restore CAS, pins, old overview/commands and the restored sidebar remain intact. A corrupt initial job list leaves the valid yard and retention controls accessible with working refresh/retry. [Implementation and exact verification](../delivery/archive-history-local-20261012.md). The older workshop's new-selection gate still conservatively reads the bounded overview; a future exact-target status read should remove that omission without weakening server admission.

#### PB-022-B — Project lifecycle state from one bounded graph

**Status / priority:** Open P2. **Evidence:** JAQ-03 / EI-002 in the [integrated query audit](../architecture/integrated-query-audit-20261012.md). **Dependencies:** PB-022-A, PB-014-A, EN-003.

**Work:** Reuse validated package, archive and dependency state within one transactionally consistent overview; construct reverse-reference reasons once. Current graph construction and per-entry selectability repeatedly hydrate the same data, extending write-lock tenure when a command returns overview. Preserve exact-target checks when the global scan is incomplete.

**Acceptance:** On 32/256/512-package flat, chain and diamond graphs, count unique input/artifact hydration and reverse-edge work; avoid repeated hydration per node within one projection. Old/new entries and cleanup decisions must agree for complete/incomplete scans, cycles, depth/visit caps, corrupt/missing/foreign dependencies, 32 MB overflow and archived sources. Existing rendering pins stay retained; new selection remains blocked where appropriate. Include rollback/idempotent command response and measure lock tenure without a guessed latency target.
