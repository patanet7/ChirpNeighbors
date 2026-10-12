# Verification ledger and historical scope

This is historical provenance, not the current task list or a claim that old totals apply to new code. The [release record](../publication/20261011/README.md) identifies the current 97-gate checkpoint and GitHub status. The [task index](product-behavior-and-ideas.md) links current acceptance.

## Status and evidence rules

- **Planned**: acceptance/design exists; required runtime implementation does not.
- **Implemented**: code exists; this alone does not establish tested behavior.
- **Locally verified**: named tests or browser assertions passed at a stated revision, within their explicit fixture/mock scope.
- **Local integrated checkpoint**: the bounded implementation and named evidence also appear in a complete frozen suite. This is still local, not merged/published/deployed.
- **Published** and **production validated** are separate states. The local ontology/environment workstream has not published, remotely merged or deployed its changes. **EN-007 is an explicit exception to any blanket unpublished label:** the separately published ESP32 branch was fetched at its reported exact head and integrated by local Git merge under E-ESP. This does not establish remote CI, a PR, remote merge, deployment, flashing or production validation. Existing published foundation bases are ancestry only; later local checkpoints are not publication evidence.
- **Blocked** states name the missing input or technical dependency, not an invented request for renewed permission. Legacy design alternatives remain proposals unless a later decision explicitly adopts them.

The corrected ontology integration is recorded in **E-INT**, a complete frozen passing run of **74/74** gates at the exact source revisions below. This verifies the bounded illustrative engine/workbench and named regression assertions; it does not certify biological correctness, finished species artwork or production readiness. The initial **72/74** attempt remains retained in [system-r1/report.json](LOCAL-EVIDENCE.md): `browser-scenes` exposed SVG/Pixi phase divergence and `browser-behavior` exposed an invalid pairwise seed-diversity expectation. The corrected suite verifies day/night static parity and the complete fixed eight-seed matrix plus exact replay; no failed attempt is counted as a pass. The [second attempt](LOCAL-EVIDENCE.md) recorded 48 passes and one core-browser capture failure before intentional interruption. Source review found that a background GET could consume its one-shot POST observer; the original failure did not retain the intercepted method. The final harness explicitly exercises GET-before-POST and forwards the one captured POST unchanged. Neither failed nor interrupted runs establish completion.

The environment-animation slice has a **complete local integrated checkpoint, 75/75 gates passed**, on `codex/environment-animation-local` in both repositories. E-ENV records the tested main `8a7a4f078d838a0fb07f8ed62c3d28bb4b3f2916` / UI `a6da5e9b415bc3a122a38985a1c8d408d0f77b4f`. PB-023 implements continuous illustrative lighting/weather rendering and transient owner preview controls; PB-024 implements explicit authored environment-to-bird/shelter rules. Existing persisted weather schemas, saved settings and scene-clock authority remain unchanged. E-INT remains historical ontology proof; the new bounded fixture proof, independent review and residual limits are recorded in the [environment checkpoint](environment-verified-20261009.md).

The subsequent [product/connection audit](product-audit-20261009.md) records four concrete fixes, official dependency/connection documentation, current browser journeys and engine resource/sound gaps. E-AUD now records a complete 75/75 frozen run with the original ESP integration present. Focused evidence and prior E-ENV/E-ESP proof remain separately retained at their exact revisions. The 36 stable entries below remain the authority; the audit task breakdown maps follow-up acceptance back to them.

The completed [bounded transport/static-check slice](external-transport-20261009.md) closes NET-01 with application-controlled Google/JWKS/SMTP and reciprocal audio lifetimes, preserves wire/auth authority, and extends first-party lint/type coverage. Its [consolidated findings](audit-findings-20261009.json) record severity, owner, fix/status, regression and review. Dedicated Svelte MCP is unavailable; compiler/static diagnostics are reported separately. E-NET supplies the corrected 76/76 frozen proof; the initial failed attempt and focused repair remain retained, not inferred from E-AUD.

The [official local Svelte CLI/CSS slice](svelte-autofixer-20261010.md) corrects the earlier unrun-CLI assessment. Its pinned official analyzer checks 30 components with zero issues and 75 individually reviewed intentional advisories; it adds bounded failure propagation and global CSS checking. Independent source review and 19 tooling tests pass. The complete frozen suite passes 79/79 gates under E-TOOL; no visual fidelity claim or product decision changes.


The preceding complete [animation planning, content composition and reference discovery](animation-planning-20261011.md) checkpoint implements deterministic private production plans, versioned recipes/strict overrides, illustrative trait composition and a configured bounded Commons metadata adapter. E-PLAN records Local integrated checkpoint at its exact revisions. Nine default clips and 60 frames remain proposals with zero generated pixels. Real image-generation providers, approved species artwork, new object kinds and a general world/region hierarchy remain open. The [animation inventory](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/docs/animation-production-inventory.md) and [extension boundaries](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/docs/extensibility-and-content-definitions.md) distinguish implemented seams from those dependencies.

The preceding [private reference-admission checklist](reference-admission-20261011.md) records implemented bounded PNG/JPEG retention, explicit rights/species/pose review, terminal revocation and exact pins consumed by a local diagnostic provider through the existing runner. Focused admission/provider controls pass within technical-image scope. The corrected side-view consumer has 41 focused provider tests and a 72/72 clean browser pass; R5 replays 13 prior security controls plus six separate viewpoint controls. The complete 95/95 frozen r2 aggregate passed at the exact E-REF source revisions below ([Integrated report](LOCAL-EVIDENCE.md), [counts](LOCAL-EVIDENCE.md)). R1 was interrupted after independent finding ENG-01; its 60 recorded passes are not a completed run. Candidates remain non-renderable. Initialized reference-store cold restore is deliberately refused pending a newest-revocation recovery protocol. E-PLAN remains the preceding complete 94-gate checkpoint and does not verify these new source commits.

The preceding [private reference cold-recovery workstream](reference-recovery-20261011.md) implements offline full-authority export and explicit restore evidence: an independently retained latest SHA-256 receipt, the same exact backup admission set, and validation of all rows, bytes, reviews, terminal revocations and retries before atomic no-clobber publication. Default restore still refuses missing or invalid evidence. A hash cannot prove newestness if authority and receipt roll back together; genuine authority/receipt loss remains blocked. **Complete frozen 96/96 local aggregate passed**. Finished `2026-10-11T20:22:29.123693+00:00`; report SHA-256 `488b282da542eb9262231c2064b5c85fa87c66a5fa963a3ec6bf0178b4349081`. [Report](LOCAL-EVIDENCE.md), [counts](LOCAL-EVIDENCE.md), [evidence index](LOCAL-EVIDENCE.md). E-REF remains unchanged historical proof.

The current [owner workbench pagination checkpoint](workbench-pagination-20261011.md)
passes **97/97 frozen local gates** under E-PAG. Owner-scoped bounded pages freeze
insertion membership, preserve off-page selections and exact renderer pins, and
retain confirmed rows through failed or superseded navigation. Heavy/corrupt job
details get a bounded explicit unavailable representation. Whole-owner retention
authority remains separately bounded. Matching updated UI/server versions are
required; retained legacy-envelope reading does not imply mixed-version wire
compatibility. [Evidence and review](LOCAL-EVIDENCE.md)
retain R1/R2 interruptions and the failed 95/97 R3 separately from passing R4.

## Exact evidence ledger

| Code | Source revision(s), scope and retained evidence |
| --- | --- |
| E-CAT | main `ef67223f52448dcdbf2bef05283146a01bceda06`; ui `db931a2beb8e62dc012a981d478e27749062fd4a`. Complete local integrated 73-gate checkpoint; applicability only to named assertions and bounded scope. [docs/delivery/catalog-verified-20261009](LOCAL-EVIDENCE.md) |
| E-ONT | ui `31585edfbb0de7fa1f04fd036a84a54428a52284`; main `Not a main-code aggregate`. Dedicated 38-check browser gate only; not full active integration. [docs/delivery/ontology-attempts-20261009/browser-r3](LOCAL-EVIDENCE.md) |
| E-FOCUS | ui `Per-log focused working-tree runs; not a substitute frozen commit`; main `Per-log focused runs`. Historical focused contract/engine evidence only; these logs are not a frozen integrated pass. E-INT records the later complete integration. [docs/delivery/ontology-attempts-20261009/focused](LOCAL-EVIDENCE.md) |
| E-INT | main `6841630e3acc3ef64495cee17947ce4d3d00b6c9`; ui `1b87d62d5c99fa4936d213d44c44f56886671c36`. Complete frozen corrected ontology run, 74/74 gates; the retained report has `finished`, `completeSuite`, `frozenWorktrees` and `passed` true and unchanged final revisions. [Final report](LOCAL-EVIDENCE.md); [checkpoint](ontology-verified-20261009.md). |
| E-ENV | main `8a7a4f078d838a0fb07f8ed62c3d28bb4b3f2916`; UI `a6da5e9b415bc3a122a38985a1c8d408d0f77b4f`. Complete frozen environment run, **75/75 gates**, finished `2026-10-09T18:12:10.904706+00:00` after 1,645.54 seconds of gate execution; `finished`, `completeSuite`, `frozenWorktrees` and `passed` are true with unchanged final revisions. [Full report](LOCAL-EVIDENCE.md); [counts](LOCAL-EVIDENCE.md); [checkpoint](environment-verified-20261009.md). |
| E-ESP | **Actual Git fetch and local integration**, following the user-reported publication of [`codex/esp32-s3-verified-stream`](https://github.com/patanet7/ChirpNeighbors/tree/codex/esp32-s3-verified-stream): fetched head `99c01c6b41de67e2f5e11b46e8e7488a1a33aa4c` and ancestor `f0a71cb997a75f6383814a17c277f8855fe18cf9` independently verified. Local merge/tested main `4ce5fb535c38f67a3f31caf3a2c7ebfb988a9ceb`, tested UI `03574ee8509e7e45d79e0e745b6ef38fd042aca4`: 52 intake tests, eight native tests, 25/25 frozen selected regression gates and 205 browser/HTTP assertions. [Checkpoint](esp32-integrated-20261009.md); [counts](LOCAL-EVIDENCE.md). Full board/static/simulator reruns are blocked by local toolchain setup; remote CI and hardware remain unverified. This is not a new full-suite pass or a publication action. |
| E-AUD | Main `22c405092f6fdeac7a42f5d3d8e840a2c7a1829b` / UI `65d5776eea463d9521b1fb4f29c40481539ae20b`. Complete frozen product/connection audit, **75/75 gates**, finished `2026-10-09T20:57:38.043861+00:00`; unchanged worktrees/revisions. 1,579 UI tests, 1,073 assertions in 32 browser/HTTP reports plus 39 local auth-provider assertions; separate seven-command/52-test intake check passes with 96% coverage. [Report](LOCAL-EVIDENCE.md), [counts](LOCAL-EVIDENCE.md), [checkpoint](product-audit-20261009.md). Board/simulator/hardware and live providers remain outside this proof. |
| E-NET | Main `12ef15273868c49e50e7bb797f298ae9ed841e11` / UI `8907328476675e64c62c12af3489a0c981f52d88`. Corrected complete frozen transport/static checkpoint, **76/76 gates**, finished `2026-10-09T22:08:52.276999+00:00`; unchanged clean revisions. 1,641 UI tests/101 files, 1,078 assertions in 32 browser/HTTP reports plus 55 local auth-provider assertions. Separate intake 7 commands/52 tests/96% combined coverage; independent 16 adversarial tests and 4 negative static probes. [Report](LOCAL-EVIDENCE.md), [counts](LOCAL-EVIDENCE.md), [checkpoint](external-transport-20261009.md). Initial 47-gate incomplete attempt retains 46 passes/1 harness failure; corrected fixture targets actual async gateway. Dedicated Svelte MCP, live providers and hardware remain unverified. |
| E-TOOL | Main `33218ebf527ab40ff2e82af6932e880ac6657b24` / UI `375ee15869491f934cccb67c52865848073eb399`. Complete frozen Svelte CLI/CSS checkpoint, **79/79 gates**, finished `2026-10-10T00:51:21.172330+00:00`. 1,641 UI tests, 19 tooling tests, 1,078 assertions in 32 browser/HTTP reports plus 55 local auth-provider assertions. Official CLI0.1.26:30files/0issues/75reviewed advisories; CSS752declarations/0findings. [Report](LOCAL-EVIDENCE.md), [counts](LOCAL-EVIDENCE.md), [checkpoint](svelte-autofixer-20261010.md). No attached MCP server or hosted source analysis; art/providers/hardware remain outside this proof. |
| E-STATIC | Main `6f3c378049bdac2bc38cfaa5fdcbfd28235a1e34` / UI `c32cdfbba0760a90bf8a5a97aacf0fffab874bc6`. Complete frozen **93/93** first-party typing closure; all 45 JavaScript and seven backend-test gaps resolved, with explicit historical/generated/dependency/firmware boundaries. [Checkpoint](first-party-types-20261010.md), [report](LOCAL-EVIDENCE.md), [563-file inventory](LOCAL-EVIDENCE.md). Prior [88-gate checkpoint](static-03-20261010.md) and [report](LOCAL-EVIDENCE.md) remain unchanged. |
| E-TS | Main `9d553e4c6e0e1dbaeeec904ffa5ea6b462f54be3` / UI `70123b013bf5538599ad018b9f15dea19d2e45f7`. Complete frozen **93/93** real TypeScript migration: all 52 active handwritten JavaScript implementations converted, 19 exact forwarders and generated/history boundaries explicit. 1684 UI tests, 63 tooling controls and 33 independent controls pass. [Checklist](typescript-migration-20261011.md), [report](LOCAL-EVIDENCE.md), [language inventory](LOCAL-EVIDENCE.md). E-STATIC remains the unchanged preceding checkpoint. |
| E-PLAN | Local integrated checkpoint: tested main `7311d2496f66074bdc5fcfd70abfaec7a0127115` / UI `e389a1f83e15057a8625dc7b7a10ca011442db6e`; 94/94 frozen gates, completed `2026-10-11T17:01:29.962358+00:00`. [Checkpoint](animation-planning-20261011.md), [report](LOCAL-EVIDENCE.md), [counts](LOCAL-EVIDENCE.md), [review](LOCAL-EVIDENCE.md). Typed recipes/prompts, composed content variants, bounded Commons metadata discovery and private V2 persistence; planning v1 preserved. Actual adapter live result is blocked/network-unavailable, with zero admitted bytes, original downloads and model calls. No generated species artwork or publication. Earlier 33/61-gate partial attempts remain historical evidence. |
| E-REF | Local integrated checkpoint: tested main `7279b5626f290d8fab24ed632f6a6e57d2f2e477` / UI `53e414077799384ba2f56340235424016a309324`. 95/95 frozen gates, completed `2026-10-11T18:51:04.665366+00:00`. [Integrated report](LOCAL-EVIDENCE.md), [counts](LOCAL-EVIDENCE.md), [checklist](reference-admission-20261011.md), [evidence index](LOCAL-EVIDENCE.md). 1,967 UI tests / 118 files; 682 cross-language goldens; 16,955 deterministic mutations; 1,536 assertions in 36 browser/HTTP reports; 55 additional local auth assertions. Report SHA-256 `e2c96e45510851456b4641b9a2b2092814e8b4c70dfbded1a73614afae6376e9`. ENG-01 viewpoint permission corrected; earlier r1 retained 60 passes/interruption and historical 85/R4 proof remain separate. R5 replays 13 original plus six separate viewpoint controls. Technical PNG/JPEG references and local non-renderable diagnostic only; zero generated species-art frames. Reference cold restore, approved art/model/live retrieval and publication remain outside completion. Documentation/evidence commits follow tested source. |
| E-REC | Local integrated checkpoint, 96/96 frozen gates passed. Main `82a45ca8e62c8c9847df92d0bf7dc6034d3bb26b` / UI `bd23e784397d7b5e0b01c0c2d12e6d000fefa1c0`. [Recovery checklist](reference-recovery-20261011.md). [Report](LOCAL-EVIDENCE.md), [counts](LOCAL-EVIDENCE.md), [evidence](LOCAL-EVIDENCE.md). Finished `2026-10-11T20:22:29.123693+00:00`; report SHA-256 `488b282da542eb9262231c2064b5c85fa87c66a5fa963a3ec6bf0178b4349081`. 2,047 UI tests/120 files; 714 goldens; 17,155 mutations; 1,596 assertions in 37 browser/HTTP reports plus 55 local auth assertions. Same-admission-set recovery only; trusted latest receipt and offline writers remain operator obligations. Historical E-REF proof unchanged; no production/art/model/publication claim. |
| E-PAG | Local integrated checkpoint, **97/97 frozen gates passed**. Main `ca8f9cd9cb072245b3dfe81a68fc1bf7f9db66ca` / UI `269183ff6d333a125f0fee5fb0dfcb80aafe5a38`. [Checklist](workbench-pagination-20261011.md), [report](LOCAL-EVIDENCE.md), [counts](LOCAL-EVIDENCE.md), [evidence/review](LOCAL-EVIDENCE.md). Finished `2026-10-11T22:32:56.266888+00:00`; report SHA-256 `1981aa8c08a23e959a6e6d9e075a2cfd21b99f8c7d4c66b7ac9ab2b9fa94e24e`. 2,072 UI tests/122 files; 718 goldens; 17,315 mutations; 1,625 assertions in 38 browser/HTTP reports plus 55 local auth assertions. Independent 20 runtime controls and 10 compatibility comparisons are source-bound, not a second full aggregate. Fixture-only local proof, zero new art frames; docs/evidence commits follow tested sources. |
| E-HANDOFF | No passing source execution claim. Retained transport-failure record, not execution evidence. [docs/delivery/approved-handoff-blocker-20261008.md](approved-handoff-blocker-20261008.md) |
| E-PUBLICATION | No passing source execution claim. Historical foundation record only. Current stalled/excluded status comes from explicit 2026-10-09 user delegation; precise cause not available. [docs/agents/20261007_183500_publication-checks.md](../agents/20261007_183500_publication-checks.md) |

Preserved complete checkpoint commits are main `a3c5ec6d03d405dd11724cbe14356e1d99b5ea37` / UI `b7e1ddb6f38429fa88dedcf659f45b3eb5e4aa95`; these retain E-CAT and are distinct from its tested source commits. The first active frozen candidate is main `5420c2e32a97536fc5d848f96cbd0ae49b9ed4bc` / UI `3938a260c5190ec488f637c9210f7cb37be46225`. Its attempt is retained as the failed [initial aggregate](LOCAL-EVIDENCE.md), distinct from the corrected E-INT tested sources.

## Verified local resource/retry slice

[Scene resource and PNG retry work](scene-resources-20261010.md), **E-RES**, passes the complete frozen **80/80** suite at main `2928fecb551b15fda133fbc356d90b47b2232cf5` / UI `5f9507ddaa624f9e12dcf04c984ebdf5c9b19660`, finished `2026-10-10T02:54:09.715007+00:00`. Evidence: [report](LOCAL-EVIDENCE.md), [counts](LOCAL-EVIDENCE.md), [acceptance checklist](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/docs/scene-resource-budget.md). 1667 UI tests/103 files, 19 tooling tests, 1106 assertions in 33 browser/HTTP reports plus 55 local auth assertions pass. This adds resource limits/lifetime and PNG recovery to PB-005/PB-008/PB-014/PB-020 while preserving the 84-resident ontology and weather/arrangement/arrival regressions.

[Measured renderer work](renderer-performance-20261010.md), **E-PERF**, passes complete frozen **81/81** verification at main `2792f19b9bd84fff00bd322faa35f7b8d4575421` / UI `a5cf659b3f8f81a1ca3560ea5cf1333c795c289b`. [Report](LOCAL-EVIDENCE.md) and [counts](LOCAL-EVIDENCE.md) record 1684 UI tests / 105 files, 19 tooling tests, 1357 assertions across 34 browser/HTTP reports plus 55 local auth assertions. Bounded immutable geometry reuse preserves 65 exact state/image pairs and 67,179,016 pixels; automatic batching remains unchanged. The [four-arm comparison](LOCAL-EVIDENCE.md) retains mixed frame times: cache surface-p95 difference −19.4 ms with descriptive interval [−47.2, +2.8]; standalone batching wins that surface test but worsens historical dense tails. CPU/geometry savings are not a universal FPS claim. STATIC-03's [historical 527-file inventory](LOCAL-EVIDENCE.md) is retained; The subsequent [88-gate checkpoint](static-03-20261010.md) retains its [539-file inventory](LOCAL-EVIDENCE.md); E-STATIC now supplies the completed remaining typing closure and [563-file applicability inventory](LOCAL-EVIDENCE.md). Earlier E-RES timing numbers use a different stress protocol and are historical, not direct before/after comparisons with E-PERF.

GAP-01 is fixed. GAP-03 is partial: allocation/geometry/canvas bounds pass, while heavy active software stress is slow (199.9 ms p95 integrated; 216.6 ms focused), and worst-case smoothness/physical-device/real-art acceptance remains open. The local [workbench pagination continuation](workbench-pagination-20261011.md) bounds job/source pages and preserves off-page pins; its own complete 97/97 frozen verification and independent review are retained under E-PAG. Retention still uses its separate bounded whole-owner graph, and saved controls retain their existing presentation. All 55 register entries remain accounted for: 35 resolved, 6 justified no-change, 0 remaining directly implementable typing entries (STATIC-03 closed for the current active first-party scope), 1 partial performance entry, 13 dependency/unselected/mixed entries. The current analyzer checks 35 files with zero issues and 77 individually reviewed advisories; the older 75-advisory E-TOOL count remains historical. Original worker source remains absent; no replacement or blocked transfer retry was attempted.

## Coverage summary

There are **36 stable entries: 24 product decisions/ideas and 12 architecture/dependency entries**. Of the product entries, 22 are user decisions, PB-017 is a tentative user idea and PB-019 is an assistant proposal. PB-023/PB-024 are implemented with bounded local integrated fixture proof under E-ENV. Under the former broad register labels, 16 bounded product slices had complete historical local verification; PB-005 has bounded local integrated proof under E-INT and its environment extension under E-ENV; PB-018 has tested pure helpers only; PB-006/PB-021 remain unimplemented at the product-outcome level; PB-016 has tested disabled helpers but unresolved operating integration; PB-017 remains unselected. These are overlapping evidence scopes, not a percentage of product readiness.

E-ENV retains 1,564 UI tests across 98 files, including 45 new tests; 429 cross-language goldens; 12,724 mutations; 866 source-valid inputs; 235 unchanged semantic exceptions; 201 structural digests (all 197 old digests unchanged); and 678 Python boundary cases. The inventory records 52 HTTP/SSR operations, 94 boundaries and 24 explicit residual gaps. All 32 browser/HTTP reports pass, including the new [47/47 environment gate](LOCAL-EVIDENCE.md). Independent source/evidence review and the [visual audit](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/docs/environment-visual-audit-20261009.md) retain their exact scope: dedicated r4 UI `bbaeafb517b66fde25ad209ffe8a27b195922e4c`, 45 screenshots, three extracted video frames and two WebMs. [Failed attempts](LOCAL-EVIDENCE.md) remain separate; sampled video review does not certify every frame, physical mobile performance or native OS occlusion.

## Reconciliation of prior task lists and architecture claims

| Prior document / stale or orphaned claim | Authoritative reconciliation |
| --- | --- |
| Original `architecture/product-requirements.md` names JWT/SQLModel coordinator, automatic inference→art, WS query-token auth and broad scaling targets as if current | Historical architecture proposal. Current owner application is SvelteKit/SQLite/session-bound BFF and reviewed FastAPI audio boundary; candidates require human confirmation. EN-002/004/005/012 record unimplemented alternatives and unvalidated targets. Do not turn old examples into current deployment instructions. |
| Delivery README says “authorize transfer” | EN-006 retains the already-authorized worker transfer whose supported download failed twice before bytes. EN-007 is superseded for ESP32 by the latest user-reported published branch at E-ESP; actual Git fetch and local merge are complete with scoped E-ESP verification and explicit toolchain/hardware gaps; no Library retry. |
| Matrix `lazy-shared-assets` and UI `generation-cost-foundation.md` say application hook/public payload are absent | PB-003 and later shared-catalog checkpoint supersede that statement for the bounded fixture path. PB-018 runtime metering, real provider execution and production publication remain absent. |
| Engine checklist H and row 11 refer to pending image-v3/sharing combined proof | E-CAT includes named `browser-image-v3` and `browser-sharing` passes. These older statuses are historical, not current blockers. E-INT separately reruns the complete ontology-era suite; retain E-CAT source revisions unchanged. |
| Older visual task tree points to PNG branch as “current verified” | Checkpoint-specific history. E-CAT remains a preserved complete checkpoint; E-INT is the later corrected local integration. Neither checkpoint means publication or production validation. Preserve earlier exact revisions rather than rewriting their results. |
| Broad PB-004/011 “verified” plus initial scene failure | The failed 72/74 report remains retained. E-INT separately verifies the corrected phase parity and whole-suite integration at exact source revisions; the older fixture pass was never used to erase that failure. |
| PB-008 pairwise random-seed diversity assertion | Finite valid placement allows seed collisions. E-INT retains every case for eight fixed seeds and every replay; the full matrix must vary, and every seed must replay its exact actor state without changing private data. |
| PB-016 described only as “agreed” despite helper tests | Helper exists and is tested disabled; operational hooks/retention policy remain unintegrated. Neither “all planned” nor “operational monitoring complete” is accurate. |
| PB-018 wording could imply real dispatch instrumentation | Only schemas/fingerprints/pure summaries are tested. No runtime caller, durable ledger, budget enforcement or billable measurement exists. |
| Svelte MCP/autofixer requested in older work | No dedicated callable Svelte MCP tool was available. Installed `svelte-check`, typed lint, build and actual Chromium checks are evidence; no MCP pass or connection is claimed. |
| Tests not represented by product-only rows | EN-001 maps generators/contracts; EN-002 auth providers; EN-003 request budgets/health/recovery; EN-004 ONNX/synthetic evaluation; EN-011 deletion recovery. Unit/browser counts remain subordinate to these named behaviors. |
| Product outcomes with no complete outcome proof | PB-006 progression, PB-017 economics, PB-021 real species fidelity; EN-005 scale/realtime, EN-006 worker, EN-007 board/simulator/hardware and private device admission, EN-008 real import, EN-009 live weather and EN-012 MLOps remain unverified at their requested outcome level. PB-023/PB-024 now have bounded illustrative fixture proof under E-ENV; physical mobile/native OS occlusion, real providers and biological/art validation remain outside it. E-ESP proves the fetched history, local merge and named host/native/regression assertions; it does not close hardware or real private-device admission gaps. |

## Source inventory and maintenance

Reviewed source groups: the original architecture PRD and audio architecture; delivery README/matrix, visual task tree, all retained wave/checkpoint summaries and transfer record; UI engine, ontology, PNG, retention and catalog checklists; contract authority/differential inventories; generation usage, image/source/shape, authentication, private recordings/recovery, sharing, analytics, arrivals, scene/weather and local operations documents. Historical agent logs and checkpoint counts remain evidence, not new decisions. No competitor or OSS peer analysis is included.

The subordinate historical [discovery and traceability audit](task-index-coverage.json) records 113 documentation files and 143 test-like files attributed to the earlier 34-entry index, with zero missing named test/evidence paths at that snapshot. It predates PB-023/PB-024 and their new source/tests; its counts are not current environment coverage. This is file discovery and sampled traceability, not 143 passing test suites or complete case coverage. The legacy `backend-inference/tests/test_endpoints.py` is a manual device client and is explicitly excluded from automated gate claims. The independent reviewer checked all 159 then-existing relative links, the 34 stable IDs and sampled catalog/privacy/usage source assertions against retained evidence, and approved the bounded claims after narrowing physical-footprint guarantees.

On each bounded slice, update this index's affected stable IDs, exact tested revision and explicit residual gap; link the detailed slice evidence rather than cloning acceptance tables into another roadmap. A focused test pass may change local-verification state, but only a complete frozen passing report changes integration state for the active candidate. Publication and production validation require their own evidence and never follow from local integration. Independent review must challenge at least one source→test→evidence link and a remaining gap before a new completed claim.

## 50-gate foundation checkpoint

[Original checkpoint](https://github.com/patanet7/ChirpNeighbors/blob/ac11610289a927b8b9bf83b4ddea4ee8a2bc17e6/docs/delivery/checkpoint-20261008.md). Historical limits below remain dated; later changes do not rewrite these results.

## Integrated local checkpoint · 2026-10-08

The 50-gate aggregate command passed against these frozen code revisions:

- UI/application: `9c50399e9e2192a0c71b31137648bfa71df43bc7`.
- Companion/audio: `21731ae2a1e683a6a37bd85e91f218952dd7d6bb`.

Subsequent commits update only README/checklist/evidence documents. Both preserve
the requested review ancestors and the consolidated checkpoints. All work is on
local `codex/species-manifest-local` branches; nothing was pushed, proposed for
remote review, merged remotely or deployed.

### Verification

| Check | Result |
| --- | --- |
| Aggregate gates | 50/50 passed, approximately 477 seconds |
| UI units | 469 tests in 35 files |
| Python units | 127: 44 contracts + 49 core audio/API + 10 ONNX + 5 dependency + 19 recovery |
| Generator tests | 10 |
| Cross-language cases | 107: 37 Zod-owned + 70 Python-owned |
| Browser regressions | 410 assertions across 14 suites |
| Actual Svelte/FastAPI smoke | 39 assertions |
| Health HTTP smoke | 16 assertions |
| Compose isolation | 6 configuration assertions; images not executed |
| Type/lint/format/build | TypeScript zero errors/warnings; typed ESLint, Prettier, production build, strict mypy, Ruff all pass |
| Strict Python scope | 31 core files, 3 optional-model files, and 2 recovery scripts |

The browser suites retain yard/layer/manifest/sleep/arrangement/routine/finding/
scene/recording/consolidation/auth/asset/recording-UI/analysis checks. Completed
reports contain no runtime errors or external requests. Desktop/mobile yard,
Workshop packaging and mobile candidate screenshots were inspected. Tests use
synthetic media, temporary owner stores and technical pixels; existing local
application data was not used as test data.

Persistent [verification summary](verification-20261008.json),
[exact commit ledger](commits-20261008.md), [task checklist](README.md), and
[reproduction instructions](quality.md) accompany this checkpoint. Detailed logs
and screenshots are currently in `/tmp/chirp-system-final-20261008`; compose
assertions are in `/tmp/chirp-system-integration/compose-assertions.json`.

### Explicit remaining limits

Approved species art, real licensed audio, compatible reviewed model weights and
biological evaluation are unavailable. Production identity/mail, weather/image
providers and hosting require operator configuration. No Cornell integration,
external generation, paid service or provider success is claimed.

Worker `c08624d3` and ESP32 `c693ed0` remain unavailable pending approved transfer;
their independent loop/packet work was not recreated. Request idempotency is
process-local; durable worker results and full derived/account-deletion lifecycle
are not integrated. Old full snapshots require media deletion/retention
reconciliation, and raw filesystem copies bypass the restore CLI's auth policy.
These gaps remain visible as partial work in the matrix.

Docker could not resolve the public package registry during image builds. Host
builds and compose validation passed; container image execution remains unverified.
No blocked publication action was retried.

## Lifecycle checkpoint: complete run and separate repair

[Original checkpoint](https://github.com/patanet7/ChirpNeighbors/blob/ac11610289a927b8b9bf83b4ddea4ee8a2bc17e6/docs/delivery/lifecycle-checkpoint-20261008.md). Historical limits below remain dated; later changes do not rewrite these results.

## Durable lifecycle implementation checkpoint — 2026-10-08

This local wave follows the previous 50-gate checkpoint. It uses isolated synthetic
data and technical pixels, preserves the published review-branch ancestry, and
contains no publication, deployment, credential changes or external media transfer.

### Verification

All **55 gates have passing evidence**: the complete run passed 54, then a
selector-only browser-test correction passed its targeted rerun. The old upload
status selector also matched the newly added saved-analysis loading status; its
scoped replacement retains the same assertion. No application code changed after
the full run. The original failure and rerun are retained in the
[machine-readable evidence](lifecycle-verification-20261008.json).

- 554 UI unit tests in 42 files; 136 Python tests; 10 generator tests.
- 129 cross-language cases and deterministic schema/client drift checks.
- 460 renderer/browser assertions across 16 suites; 44 additional actual
  Svelte/FastAPI/CPU ONNX/browser/confirmation assertions.
- 33 actual local SMTP/signed-Google-mock assertions, 14 restore HTTP assertions,
  39 core audio HTTP checks, 16 health/operations assertions and 6 compose checks.
- TypeScript: zero errors/warnings. Strict core/optional/recovery Python typing,
  typed ESLint, Ruff, formatting, locked dependency consistency and build pass.

Raw full-run logs/screenshots are retained at
`/tmp/chirp-lifecycle-system-20261008`; the 26-assertion affected-suite rerun is at
`/tmp/chirp-lifecycle-status-rerun-20261008`. Browser screenshots were inspected.
The two retained report files identify exact commands, exit codes and revisions.

Tested code revisions:

- UI `70a04886cc03c05556cf8380b412b9b618d20829`
- Companion `633bcbeb34aa6ad77aad74cf653d58e186d81b23`

Documentation-only evidence commits follow these code heads. The exact wave
history is in [lifecycle-commits-20261008.md](lifecycle-commits-20261008.md).
The complete command and dependency isolation requirements are in [quality.md](quality.md).

### Remaining acceptance gates

- Retain the latest complete deletion ledger independently of old checkpoints.
  A coherently stale export cannot prove its freshness, and pre-identity backups
  cannot prove lineage. Offline copies, filesystem snapshots and forensic erasure
  are outside the implemented guarantee. Account-wide deletion orchestration is
  separate work.
- The tested executor is explicit and local. The independently blocked worker
  `c08624d3` and ESP32 `c693ed0` remain unintegrated; neither was recreated. A future
  independent worker requires storage-level fencing for concurrent uploads.
- The generated ONNX arithmetic graph proves preprocessing, HTTP, persistence and
  confirmation mechanics only. It is not a bird classifier. Reviewed model
  weights, licensed representative recordings and biological calibration remain
  absent. Approved species art is also unavailable; fixture pixels remain labeled.
- Production email needs operator SMTP host/port/TLS/from and optional credentials;
  account auth needs a stable secret and HTTPS base URL. Google additionally needs
  operator client ID/secret, console callback and consent configuration. Real
  external mail delivery, Google account consent and production hosting were not
  exercised. No credential setup occurred.
- Photo decoding/storage, real sprite-generation and external weather/data
  providers remain explicit adapters. No Cornell integration is claimed.
- Docker image execution remains unverified after the previously recorded registry
  DNS failure. This wave did not retry publication or Docker builds. Host checks
  pass independently of that outstanding environment gate.

## Readiness attempts: incomplete historical runs

[Original checkpoint](https://github.com/patanet7/ChirpNeighbors/blob/ac11610289a927b8b9bf83b4ddea4ee8a2bc17e6/docs/delivery/readiness-checkpoint-20261008.md). Historical limits below remain dated; later changes do not rewrite these results.

## Readiness implementation checkpoint — 2026-10-08

This is a preserved local implementation and verification checkpoint, **not a
complete all-pass claim**. Work continued into a separately owned deep contract
hardening wave after the user changed priorities.

Completed implementation includes opt-in immutable snapshot sharing, anonymous
static rendering, capability expiry/revocation and restore invalidation; effective
persisted auth limits; bounded request admission and bodies; safe typed errors;
confirmation deadlines and same-request gateway recovery; and finite drained
session polling. Existing species manifests/reviewed pins, yard layers, import,
resident, weather, recording and private evidence behavior remain regression targets.

### Exact verification state

- First clean frozen run: **55/57 gates passed**. Invalid yard placement returned
  500 after error hardening; four reviewed validation failures now have explicit
  domain types and safe400 responses. The other failure was routines reload.
- Second clean frozen run: **56/57 gates passed**. Source/test revisions remained
  fixed throughout. The routines journey again timed out waiting for networkidle
  after its first13 behavior assertions. No remaining full pass is claimed from
  isolated or partial reruns.
- The session-poll diagnosis found a real unread response-body leak. Its bounded
  drain/cancellation fix passed10 helper tests and an unchanged isolated17-check
  routines journey. The full-run reload timeout still requires timing/resource
  diagnosis; parallel heavy checks were paused on this four-CPU workspace.
- Second-run counts:635 UI tests in51files,140 Python tests,10 generator tests,
  155 cross-language cases,494 completed browser assertions across17 suites
  (the routines suite stopped early),52 actual local audio-confirmation checks,
  35 local SMTP/signed-provider-mock checks,25 abuse HTTP checks,18 restore HTTP
  checks,39 core audio HTTP checks and16 operations HTTP checks.

Reports preserve commands, exit codes, exact revisions and failed logs:
[attempt1](readiness-attempt-1-20261008.json),
[attempt2](readiness-attempt-2-20261008.json).
Raw evidence lives in `/tmp/chirp-readiness-system-20261008` and its `-r2` sibling.

Second-run source and test heads:

- UI: `305cbeabfbd08767907bb71d7bb0cb69719ef8de`
- Companion: `c46735bac08c77fd4f8689fc032fddc8199b3851`

The original lifecycle history remains intact:54passes in its complete55-gate
run, then the selector-only affected-suite rerun. Neither historical run has been
rewritten into a fictitious single all-pass result.

### Continuing work and boundaries

Deep contract work is isolated until integrated: canonical runtime guards for
persistence/provider/HTTP/config boundaries, deterministic generated counterparts,
semantic versus structural parity and breaking-change checks. A final combined
run will use frozen integrated sources with heavy browser work scheduled exclusively.

The approved code handoff remains technically blocked, documented in
[the exact transfer record](approved-handoff-blocker-20261008.md). No local ZIP
bytes exist, so worker/ESP integration is unverified. Existing art remains fixtures;
no model generation, device work, providers, credentials, publication or deployment
was performed. Peer research stays outside both repositories.

## 65-gate visual checkpoint

[Original checkpoint](https://github.com/patanet7/ChirpNeighbors/blob/ac11610289a927b8b9bf83b4ddea4ee8a2bc17e6/docs/delivery/visual-verified-20261008.md). Historical limits below remain dated; later changes do not rewrite these results.

## Verified local visual checkpoint — 2026-10-08

All **65/65 aggregate gates passed** with both source trees frozen and clean.

- Main tested: `9d48ed6a99edae1fac740c79d6e292cf564cab8a`.
- UI tested: `dab7ab5eec07c995813d37cdd86ad3cd623b1af5`.
- Full report/logs: [retained evidence](LOCAL-EVIDENCE.md).
- Prior 60/65 failure remains in [attempt 1](visual-attempt-1-20261008.json).
- Raw output/screenshots: `/tmp/chirp-visual-system-20261008-r2`.

This includes 1,053 UI unit tests, strict Svelte/TypeScript, typed ESLint,
formatting, production build, cross-language schema/property/compatibility checks,
Python services and actual renderer/browser regressions. Shape29 and evidence34
checks pass. All original raw-frame inspection browser checks pass again; clip
progress is ordinary text rather than an implicit live status announcement.

The next inventory/session/arrival/privacy/catalog integration remains isolated
on `codex/interactive-yard-root` and requires its own complete verification. This
visual checkpoint does not verify later code. No publication, external provider,
model download or new artwork was performed; current pixels remain fixtures.
