# Animation planning and tooling cleanup — local work

> Historical checkpoint: task/checklist statuses and local-only instructions below describe the recorded source revision. Preserve this evidence; current remaining work, dependencies and acceptance live in the [PB/EN task index](product-behavior-and-ideas.md), including its architecture follow-up.

Starting source checkpoints (historical): main `ba627f13dc3d92f1427708ad6f15f69c4a943a3c` and UI `0d96e09a12b2c5c6315db7e28910eda28c21ec84`. Work continues on `codex/animation-planning-local`; the preceding TypeScript checkpoint remains unchanged. No publication or deployment is authorized.

## Evidence-based starting status

The preceding frozen run built the application and passed 93/93 gates, including production HTTP, Chromium, Pixi/SVG, owner isolation, reviewed asset loading, PNG intake, arrival/scatter and illustrative environment flows. This establishes local implementation and browser execution, not production operation. Exact reports remain in [the TypeScript checkpoint](typescript-migration-20261011.md).

Actual built-in bird art comprises five existing fixture frames and six clips. The engine supports nine action states; sleep, play and nest-building use explicit still fallbacks. Direction is right-facing with runtime left mirroring. Arrival/scatter reuse moving poses. There is no approved species artwork or new art generation in this work.

The local pipeline implements durable jobs, reference/source declarations, bounded PNG decoding, normalization/packaging, separate source and manifest review, immutable pins and renderer fallbacks. Image-stage segmentation/matte/foreground helpers validate supplied channels; no model creates those channels. The image generation adapter is unconfigured. No real image provider/model, photo-to-animation process or separately absent autonomous worker has run.

## Concrete task checklist

| Task | Dependency | Acceptance | Status |
| --- | --- | --- | --- |
| AP-01: Audit nineteen shims | Preserved TypeScript checkpoint | Classify every wrapper and active caller; demonstrate each retained external requirement; distinguish six generated validators. | Implemented; focused verified; Local integrated checkpoint |
| AP-02: Remove avoidable wrappers | AP-01 | Migrate callers to actual TypeScript, delete unnecessary aliases, preserve strict discovery and failure/import semantics; focused negative controls pass. | Implemented; focused verified; Local integrated checkpoint |
| AP-03: Inventory animation requirements and actual assets | Existing manifest/engine/pipeline source | Record all nine actions, directions, actual frame/timing counts, missing clips, arrival/scatter/environment effects, and implemented versus designed/never-run stages. | Implemented; focused verified; Local integrated checkpoint |
| AP-04: Typed production specifications and prompts | AP-03; existing contract authorities | Deterministic versioned per-clip proposals fit existing frame/pixel budgets; exact catalog identity and supplied-reference consistency; alpha, anchors/contact, loops/transitions, rights and human review requirements explicit. No generated-art claims. | Implemented; focused verified; Local integrated checkpoint |
| AP-05: Local planning workflow | AP-04 | Durable private plan job, inspectable prompts and readiness blockers; plan cannot be selected as artwork; owner isolation, retry/restart and existing yard data preserved. | Implemented; focused verified; Local integrated checkpoint |
| AP-06: App and browser evidence | AP-02–05; frozen source | Actual production build, focused Workshop/yard flow plus relevant existing browser regressions; screenshots/video from temporary test owners only. | Locally verified in the complete frozen checkpoint; see named browser report |
| AP-07: Aggregate verification and independent review | AP-06 | Strict types, lint/format, contracts/compatibility, unit and complete aggregate gates; adversarial identity/provenance/budget/pinning controls. | Local integrated checkpoint |
| AP-08: Retained delivery | AP-07 | Reconcile product/task register; retain hashes, screenshots/video and exact commits; save requested visuals through supported Library if available. | Local evidence and documentation retained; no publication; Library save blocked, zero confirmed saves |

Proposed canvas sizes and frame budgets are engineering proposals within current decoder limits. They are not approved artistic requirements or completed assets. Detailed species-correct birds still depend on approved references, licensing and biological/art review. Image-generation model/provider execution, paid services, credential changes, external asset uploads, hardware and publication remain outside this turn. Public metadata discovery is the separately implemented EX-03 adapter below.

## Environment

The fresh workspace retained Node 24, npm dependencies, Chromium and system FFmpeg but lost the temporary Python environments. The repository-pinned core, intake and optional ONNX environments were restored successfully; dependency consistency checks passed. Browser video uses the already installed system FFmpeg through a local Playwright executable link; no media download was attempted.

## Added requirements: content hierarchy and automatic reference discovery

The user added these requirements before final verification completed. The first aggregate was stopped after 33 recorded gates because a reviewed Svelte source hash needed renewal. The corrected second attempt passed all 61 recorded gates and was deliberately stopped when this new scope arrived. Neither partial run is a completed aggregate. Their original reports remain retained; final verification must use the extended source revisions.

| Task | Dependency | Concrete acceptance | Status |
| --- | --- | --- | --- |
| EX-01: Hierarchy and extension audit | Current source and existing manifest/scene/provider contracts | Map species identity, illustrative traits, observations and presentation separately; name reusable definitions, validated overrides and exact remaining switch/registration gaps. | Implemented; focused verified; Local integrated checkpoint |
| EX-02: Typed recipe and content extensions | EX-01; unchanged v1 definitions | New versioned recipe/default/override composition; representative clip/trait and scene/object variants consumed by existing runtime paths; reject unknown versions/definitions and invalid overrides; preserve fallback and deterministic replay. | Implemented; focused verified; Local integrated checkpoint |
| EX-03: Public reference discovery | Verified official Wikimedia API/licensing guidance | Typed source registry and Commons adapter; canonical public taxonomy queries, bounded pagination/retries/bytes, safe fixed transport, separate identity/pose/rights results, exact per-file metadata and intended-use policy; supplied references skip requests. | Implemented; focused verified; Local integrated checkpoint |
| EX-04: Private persisted discovery workflow | EX-02–03; persisted runner/lifecycle | Preserve planning-v1; new v2 validates, discovers when references are absent, then compiles a plan. Retain discovery metadata separately, never promote it to approved artwork or image-generation permission; preserve owner privacy, retry, cancellation and existing yard pins. | Implemented; focused verified; Local integrated checkpoint |
| EX-05: Contract and live-read evidence | EX-02–04 | Additive exports/goldens; mocked missing/denied/rate-limited/disambiguation/duplicate/invalid-source tests; bounded live read if available, distinguishing metadata searched, original fetched and model-used. | Implemented and focused verified; additive compatibility retained; actual live metadata access blocked |
| EX-06: Final extended verification and delivery | EX-01–05 | Focused and full frozen static/build/contracts/browser checks, independent review, updated task/register evidence and local commits; retain previous partial runs. | Local integrated checkpoint; Local evidence and documentation retained; no publication |

Official sources checked on 2026-10-11: [Imageinfo](https://www.mediawiki.org/wiki/API:Imageinfo), [Search](https://www.mediawiki.org/wiki/API:Search), [API etiquette](https://www.mediawiki.org/wiki/API:Etiquette), [Commons reuse](https://commons.wikimedia.org/wiki/Commons:Reusing_content_outside_Wikimedia), [Commons licensing](https://commons.wikimedia.org/wiki/Commons:Licensing) and [User-Agent policy](https://foundation.wikimedia.org/wiki/Policy:User-Agent_policy). Commons hosting is not a per-file rights decision; the adapter retains creator and license declarations for review against intended use. Metadata, taxon text matches and pose suitability remain distinct from permission to generate or redistribute.

The first bounded live API request used only the public name `Erithacus rubecula`. Workspace DNS resolution failed before an HTTP response; no metadata or image was returned, and no model was used. The denied/unavailable path remains a supported outcome. The separate three-file Library evidence save also failed during hosted-tool discovery networking, with zero confirmed saves; original local screenshots/video are preserved.


## Implemented phases and exact verification boundary

Phase 1 removes eighteen avoidable command forwarders while retaining the one-line
Svelte analyzer discovery export and six generated validators. It adds the actual
fixture/behavior inventory and private deterministic planning: nine proposed clips,
60 proposed frames on a 32×32 canvas, 61,440 decoded pixels, **zero generated frames**.
The preserved `animation-planning@1` definition still has two local stages and its
original full-plan bytes for all three catalog species.

Phase 2 adds strict versioned recipe pins and explicit clip/frame overrides,
canonical input/specification hashes, and composed illustrative trait defaults.
Representative tests add a known-species trait variant, an optional existing-state
clip reusing fixture pixels, a scene with different existing palette-role assignments,
and another existing-kind bath through actual registry, placement, sampler and replay
consumers. All three original trait outputs remain exact. This is composition through
validated definitions; it does not admit arbitrary taxons, object kinds, palette IDs,
world/region graphs or persisted owner trait variants.

The configured Commons reference adapter is separate from image generation.
`animation-planning@2` persists `animation/plan/validate@2`,
`animation/reference/discover@1`, then `animation/plan/compile@2`. Supplied reference
declarations skip source access. Missing references trigger a bounded public taxonomy
search; unavailable/empty results still produce a blocked production brief. Discovery
and planning remain separate private metadata artifacts. Restart reuses the saved
discovery snapshot without rescanning; changed request digests reject. Neither artifact
becomes renderable art after approval. Owner isolation and archive/restore preserve
existing reviewed resident pins and local yard data.

The normal planning path downloads no original image and invokes no model. The separate
optional original-fetch helper validates current per-file metadata, intended-use policy,
source identity, host/redirect limits, bounded bytes and hashes before invoking an
optional writer. Its mock/loopback controls do not establish actual image acquisition,
approved reference bootstrap, biological identity, pose suitability or generation rights.
Image-stage helpers validate/composite supplied channels; no segmentation, matte or
foreground-recovery model creates those channels. Existing synthetic audio/ONNX proof
is unaffected and does not constitute image-generation proof.

Focused retained evidence: **52** recipe/specification/compiler tests, **56** discovery
tests, **11** persisted V2 integration tests, **18** new content-consumer tests, and
**70** independent compatibility/extension controls (39 prior + 31 new), and the
actual focused browser run passes **107** assertions. These are
named focused scopes with overlap, not a summed unique-test or full-suite total.
The 107-assertion run uses the actual Vite development application with process-only
synthetic Commons metadata injection: zero runtime errors, external requests, real
reference-image downloads or model calls. Production build and wider renderer/browser
coverage are separate gates in the final aggregate report.
See [focused evidence](LOCAL-EVIDENCE.md) and [independent review](LOCAL-EVIDENCE.md).

Final extended verification: **94/94** gates at tested main
`7311d2496f66074bdc5fcfd70abfaec7a0127115` / UI `e389a1f83e15057a8625dc7b7a10ca011442db6e`, completed `2026-10-11T17:01:29.962358+00:00`.
The [full report](LOCAL-EVIDENCE.md), [counts](LOCAL-EVIDENCE.md), and
[actual browser evidence](LOCAL-EVIDENCE.md) own their exact scope. Final local delivery
commit IDs belong in the final delivery response; source-tested and later documentation/
evidence commits must remain distinguishable. The two earlier
33- and 61-gate partial attempts remain retained and are not counted as complete passes.
The r2 browser-core dev server survived interruption and appended hot-reload messages
until its orphaned process group was terminated. Its report remains unchanged at 61
recorded gates; that mutable dev-server log is not completed frozen browser proof.
The original log and separate cleanup receipt are retained with the interrupted run.

The unmodified default Commons adapter was also invoked once through the actual discovery
service on 2026-10-11. It returned `blocked/network-unavailable`: one request attempt,
zero candidates, zero admitted response bytes, zero original downloads and zero model
invocations. The earlier separate probe failed DNS resolution. The unavailable result
is not a successful lookup or evidence that Commons has no matching species images.
See [actual adapter receipt](LOCAL-EVIDENCE.md). The three requested Library media saves
remained blocked during hosted `tools/list` network discovery, with zero confirmed saves;
local screenshots/video and the original failure evidence remain retained.

## Next bounded tasks and dependencies

| Task mapped to the existing product register | Required dependency | Concrete acceptance |
| --- | --- | --- |
| PB-021 / PB-014: admit one actual reference into the reviewed private pipeline | Authorized original pixels; intended-use/license decision; actual successful source acquisition or owner upload | Recheck source metadata and hash/byte binding, retain original/decoded provenance and human identity/rights review; missing/denied/changed bytes fail; no metadata candidate becomes approval automatically |
| PB-021: approve art direction and produce the first species pack | Approved concept pixels, reference rights, named biological/art reviewer, selected authorized image model/output license | Verify anatomy/plumage/silhouette, binary alpha, all frame bounds and poses, support contacts, timing/loop seams and transitions; exact source/manifest reviews and explicit pin; state generation only after actual execution |
| PB-004 / PB-014: expand motion beyond the existing action/direction contract | Reviewed takeoff/landing/turn/interaction needs and resource budget | Version schemas/sampler/scheduler together; test interruption, reduced motion, occupancy and deterministic replay; preserve labeled missing-clip fallback and old exact pins |
| PB-005 / EN-001: persist/select a content variant or add a species identity | Product decision on editor scope, exact variant pin, approved catalog/taxonomy mapping | Reject identity/provenance/version overrides; preserve three defaults, owner observations and fictional-personality separation; restart/backup/public projection remain compatible |
| PB-007 / PB-011 / EN-001: new object kind, skin or theme | Versioned physical/visual definition and stock/selection migration | Admit geometry, support slots, capabilities and palette roles together; placement/removal/occupancy, inventory CAS, keyboard flows and Pixi/SVG agree; no scene theme recolors species pixels |
| PB-011 / EN-009: world→region→yard composition | Explicit region semantics and privacy-preserving scene inheritance rules | Exact pins and deterministic defaults; cycles/missing parents/unknown versions reject; old yards remain loadable and no location is inferred or shared |
| EN-006: integrate the original autonomous worker | Original authorized source becomes available | Review and integrate its actual queue/lease/retry/cancellation contract against current pipelines; do not claim manual stage advancement is autonomous execution |

No new product or finding IDs are created by this checklist. It refines dependencies
of the existing 36 product/architecture entries; all 55 findings remain accounted for.
