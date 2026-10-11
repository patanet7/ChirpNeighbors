# Animation planning and tooling cleanup — local work

Source checkpoints: main `ba627f13dc3d92f1427708ad6f15f69c4a943a3c` and UI `0d96e09a12b2c5c6315db7e28910eda28c21ec84`. Work continues on `codex/animation-planning-local`; the preceding TypeScript checkpoint remains unchanged. No publication or deployment is authorized.

## Evidence-based starting status

The preceding frozen run built the application and passed 93/93 gates, including production HTTP, Chromium, Pixi/SVG, owner isolation, reviewed asset loading, PNG intake, arrival/scatter and illustrative environment flows. This establishes local implementation and browser execution, not production operation. Exact reports remain in [the TypeScript checkpoint](typescript-migration-20261011.md).

Actual built-in bird art comprises five existing fixture frames and six clips. The engine supports nine action states; sleep, play and nest-building use explicit still fallbacks. Direction is right-facing with runtime left mirroring. Arrival/scatter reuse moving poses. There is no approved species artwork or new art generation in this work.

The local pipeline implements durable jobs, reference/source declarations, bounded PNG decoding, normalization/packaging, separate source and manifest review, immutable pins and renderer fallbacks. Image-stage segmentation/matte/foreground helpers validate supplied channels; no model creates those channels. The image generation adapter is unconfigured. No real image provider/model, photo-to-animation process or separately absent autonomous worker has run.

## Concrete task checklist

| Task | Dependency | Acceptance | Status |
| --- | --- | --- | --- |
| AP-01: Audit nineteen shims | Preserved TypeScript checkpoint | Classify every wrapper and active caller; demonstrate each retained external requirement; distinguish six generated validators. | In progress |
| AP-02: Remove avoidable wrappers | AP-01 | Migrate callers to actual TypeScript, delete unnecessary aliases, preserve strict discovery and failure/import semantics; focused negative controls pass. | In progress |
| AP-03: Inventory animation requirements and actual assets | Existing manifest/engine/pipeline source | Record all nine actions, directions, actual frame/timing counts, missing clips, arrival/scatter/environment effects, and implemented versus designed/never-run stages. | In progress |
| AP-04: Typed production specifications and prompts | AP-03; existing contract authorities | Deterministic versioned per-clip proposals fit existing frame/pixel budgets; exact catalog identity and supplied-reference consistency; alpha, anchors/contact, loops/transitions, rights and human review requirements explicit. No generated-art claims. | In progress |
| AP-05: Local planning workflow | AP-04 | Durable private plan job, inspectable prompts and readiness blockers; plan cannot be selected as artwork; owner isolation, retry/restart and existing yard data preserved. | Pending |
| AP-06: App and browser evidence | AP-02–05; frozen source | Actual production build, focused Workshop/yard flow plus relevant existing browser regressions; screenshots/video from temporary test owners only. | Pending |
| AP-07: Aggregate verification and independent review | AP-06 | Strict types, lint/format, contracts/compatibility, unit and complete aggregate gates; adversarial identity/provenance/budget/pinning controls. | Pending |
| AP-08: Retained delivery | AP-07 | Reconcile product/task register; retain hashes, screenshots/video and exact commits; save requested visuals through supported Library if available. | Pending |

Proposed canvas sizes and frame budgets are engineering proposals within current decoder limits. They are not approved artistic requirements or completed assets. Detailed species-correct birds still depend on approved references, licensing and biological/art review. Models, providers, paid services, credentials, external asset uploads, hardware and publication remain outside this turn.

## Environment

The fresh workspace retained Node 24, npm dependencies, Chromium and system FFmpeg but lost the temporary Python environments. The repository-pinned core, intake and optional ONNX environments were restored successfully; dependency consistency checks passed. Browser video uses the already installed system FFmpeg through a local Playwright executable link; no media download was attempted.

## Added requirements: content hierarchy and automatic reference discovery

The user added these requirements before final verification completed. The first aggregate was stopped after 33 recorded gates because a reviewed Svelte source hash needed renewal. The corrected second attempt passed all 61 recorded gates and was deliberately stopped when this new scope arrived. Neither partial run is a completed aggregate. Their original reports remain retained; final verification must use the extended source revisions.

| Task | Dependency | Concrete acceptance | Status |
| --- | --- | --- | --- |
| EX-01: Hierarchy and extension audit | Current source and existing manifest/scene/provider contracts | Map species identity, illustrative traits, observations and presentation separately; name reusable definitions, validated overrides and exact remaining switch/registration gaps. | In progress |
| EX-02: Typed recipe and content extensions | EX-01; unchanged v1 definitions | New versioned recipe/default/override composition; representative clip/trait and scene/object variants consumed by existing runtime paths; reject unknown versions/definitions and invalid overrides; preserve fallback and deterministic replay. | In progress |
| EX-03: Public reference discovery | Verified official Wikimedia API/licensing guidance | Typed source registry and Commons adapter; canonical public taxonomy queries, bounded pagination/retries/bytes, safe fixed transport, separate identity/pose/rights results, exact per-file metadata and intended-use policy; supplied references skip requests. | In progress |
| EX-04: Private persisted discovery workflow | EX-02–03; persisted runner/lifecycle | Preserve planning-v1; new v2 validates, discovers when references are absent, then compiles a plan. Retain discovery metadata separately, never promote it to approved artwork or image-generation permission; preserve owner privacy, retry, cancellation and existing yard pins. | In progress |
| EX-05: Contract and live-read evidence | EX-02–04 | Additive exports/goldens; mocked missing/denied/rate-limited/disambiguation/duplicate/invalid-source tests; bounded live read if available, distinguishing metadata searched, original fetched and model-used. | In progress |
| EX-06: Final extended verification and delivery | EX-01–05 | Focused and full frozen static/build/contracts/browser checks, independent review, updated task/register evidence and local commits; retain previous partial runs. | Pending |

Official sources checked on 2026-10-11: [Imageinfo](https://www.mediawiki.org/wiki/API:Imageinfo), [Search](https://www.mediawiki.org/wiki/API:Search), [API etiquette](https://www.mediawiki.org/wiki/API:Etiquette), [Commons reuse](https://commons.wikimedia.org/wiki/Commons:Reusing_content_outside_Wikimedia), [Commons licensing](https://commons.wikimedia.org/wiki/Commons:Licensing) and [User-Agent policy](https://foundation.wikimedia.org/wiki/Policy:User-Agent_policy). Commons hosting is not a per-file rights decision; the adapter retains creator and license declarations for review against intended use. Metadata, taxon text matches and pose suitability remain distinct from permission to generate or redistribute.

The first bounded live API request used only the public name `Erithacus rubecula`. Workspace DNS resolution failed before an HTTP response; no metadata or image was returned, and no model was used. The denied/unavailable path remains a supported outcome. The separate three-file Library evidence save also failed during hosted-tool discovery networking, with zero confirmed saves; original local screenshots/video are preserved.
