# Private reference admission — local task and status

The local application and contract/review pipeline are implemented and broadly tested.
The next bounded step is private **PNG/JPEG reference admission, explicit rights/species/
pose approval, terminal revocation and exact reference pins consumed by a local fake
generator through the existing runner**. Its output is a non-renderable candidate;
existing species fixtures, resident artwork pins and owner data remain unchanged.
This document records scope and acceptance, not a completed new implementation.

Branches: `codex/reference-admission-local`. Starting heads are main
`d2d0e0ed35706c762b7c69439f92cf2fbdd1618d` and UI
`a7e44323e1ff718b45fe12e4d12d2b61ac89e54a`. The [preceding complete checkpoint](animation-planning-20261011.md)
passed **94/94** at tested main `7311d2496f66074bdc5fcfd70abfaec7a0127115` and UI
`e389a1f83e15057a8625dc7b7a10ca011442db6e`; changes from those tested sources to the
starting heads are documentation/evidence only. That historical proof does not verify
new reference-admission code. No new test counts or passing implementation are claimed here.

The [36-entry product index](product-behavior-and-ideas.md) and
[55-finding register](audit-findings-20261009.json) remain authoritative. Statuses below
apply to named boundaries: **BUILT/TESTED** local connected implementation;
**FIXTURE-ONLY** content/validity, not fake app execution; **LIVE-UNVERIFIED** external,
physical or deployed acceptance; **ABSENT** missing integration; **BLOCKED** concrete
unavailable input/access. There is no product-completion percentage.

## Completed status assessment at the starting checkpoint

| Area and register IDs | Current status and actual boundary | Code authority / next dependency |
| --- | --- | --- |
| Auth/login — EN-002 | BUILT/TESTED email-link/Google/session mechanics; LIVE-UNVERIFIED actual Google consent and SMTP mailbox | [Auth service](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/src/lib/server/auth/service.ts), [strict config](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/src/lib/server/auth/config.ts); operator config and live callback/mail test |
| Uploads/storage — PB-012/020/022, EN-003/011 | BUILT/TESTED real private WAV/PNG bytes, SQLite/files, review/pins/archive/delete ledger and restart/backup recovery; general reference photos and account-wide erasure ABSENT | [PNG service](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/src/lib/server/image-files/service.ts), [recordings](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/src/lib/server/recordings/service.ts), [lifecycle](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/src/lib/server/assets/lifecycle.ts); exact reference admission next |
| Audio identification — PB-012, EN-004 | BUILT/TESTED audio transport/confirmation and optional ONNX execution; FIXTURE-ONLY model accuracy; trained/licensed bird bundle ABSENT | [ONNX adapter](../../backend-inference/app/audio_onnx/provider.py); authorized model/data and withheld real-recording evaluation |
| Reference discovery — PB-021 | BUILT/TESTED Commons adapter, bounded transport, persisted metadata; actual live request BLOCKED/network-unavailable | [Discovery service](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/src/lib/server/reference-discovery/service.ts); successful source retrieval is separate from image identity/rights review |
| Image-generation/art — PB-014/021 | Planner/packaging BUILT/TESTED; approved species artwork and actual image model ABSENT. Default 9 clips / 60 frames are proposals, generated 0 | [V2 planner](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/src/lib/server/asset-pipeline/animation-planning-v2.ts), [image stage](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/src/lib/server/asset-pipeline/image-stage.ts); reviewed references/concept direction and provider/output licenses |
| Shared canonical assets/variants — PB-003 | BUILT/TESTED request dedupe/exact releases/pins; runtime FIXTURE-ONLY/default-deny promotion. Shared optional variant authoring ABSENT | [Catalog selection](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/src/lib/server/assets/catalog-selection.ts); approved production reference/art and explicit promotion authority |
| Autonomous yard motion — PB-004/008/009/010 | BUILT/TESTED nine-state routines, movement/support/fairness, seed replay, arrival/scatter; FIXTURE-ONLY 5 frames / 6 clips, sleep/play/nest still fallback | [Simulation](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/src/lib/engine/simulation.ts), [sampler](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/src/lib/assets/manifest.ts); actual reviewed clips before claiming visual completion |
| Traits/personality — PB-005 | BUILT/TESTED strict data composition and transient variants; FIXTURE-ONLY illustrative biology. Persisted trait selection ABSENT | [Profiles](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/src/lib/engine/behavior-profiles.ts); distinct scientific facts, private observations, fictional personality and presentation |
| Objects/themes/regions — PB-007/011 | BUILT/TESTED four kinds, inventory, layered scenes/palette roles and real-consumer variant tests. New kinds/theme IDs/world-region graph ABSENT | [Scene kinds](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/src/lib/domain/scene.ts), [scene manifest](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/src/lib/scenes/manifest.ts); versioned definition/selection/storage admission |
| Weather — PB-023/024, EN-009 | BUILT/TESTED procedural visuals and illustrative shelter policy; FIXTURE-ONLY environment; real provider/location authorization ABSENT | [Policy](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/src/lib/engine/environment-policy.ts), [disabled provider](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/src/lib/server/weather/provider.ts); chosen provider/coarse-consent policy |
| Privacy/sharing/analytics — PB-001/013/015/016/019 | BUILT/TESTED private defaults, narrow revocable location-free shares, consent-off analytics and restore fences. Security helper tested but operational hooks ABSENT | [Projection](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/src/lib/domain/yard.ts:502), [analytics config](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/src/lib/server/analytics/config.ts), [security helper](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/src/lib/server/analytics/security-audit.ts); retention/erasure/operator policy |
| Worker/dispatch/accounting — EN-005/006, PB-018 | Durable manually advanced jobs BUILT/TESTED; original worker BLOCKED before source transfer. Distributed architecture and runtime usage ledger ABSENT | [Runner](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/src/lib/server/pipeline/runner.ts), [usage helpers](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/src/lib/server/pipeline/generation-usage.ts); obtain original source, do not recreate it |
| Firmware — EN-007 | Original history locally integrated; simulator Python tooling/14 host tests in the 94-gate run BUILT/TESTED, with eight direct native tests retained from earlier scoped proof. Board compile/static and QEMU firmware scenarios BLOCKED; physical device/private enrollment/TLS LIVE-UNVERIFIED | [Firmware](../../esp32-client/src/main.cpp), [CI definition](../../.github/workflows/firmware.yml); supported toolchain then physical acceptance |
| Contracts/CI/publication — EN-001/010 | Contract consumers, compatibility and local94-gate suite BUILT/TESTED; remoteCI/deployment LIVE-UNVERIFIED; publication excluded/separately stalled | [Compatibility](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/src/lib/server/storage/compatibility.ts), [corpus](../../scripts/check_contract_corpus.py); no push/PR/merge/deploy here |
| Performance — GAP-03/04/05 | Actor/geometry/canvas budgets and reuse BUILT/TESTED; stress frame time, physical devices, real-art load LIVE-UNVERIFIED; SVG is static fallback | [Budget consumer](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/src/lib/engine/renderer.ts:137), [limits](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/src/lib/engine/scene-resource-budget.ts); measured workload/target and physical-device validation |
| Sound, progression, economy, MLOps — PB-006/017, GAP-02, EN-012 | ABSENT or unselected ideas; no yard mixer/sound catalog, progression, payments or operating training platform | Existing native recording playback is not yard sound; product/license/runtime decisions precede implementation |


The 94-gate report covers 1,823 UI tests, 35 browser/HTTP reports with 1,464 recorded
assertions, plus 55 additional local auth-provider assertions. Counts overlap; they
are not a summed unique-test count. Pixi and SVG consume the real asset registry,
clip sampler and scene admission; the local app is more than a collection of contracts.
The 107-assertion planning browser flow uses synthetic Commons metadata in the actual
development app. Neither that flow nor the complete aggregate proves real species
fidelity, successful live source retrieval, live account/mail delivery, physical
hardware, production performance, remote CI or publication.

Generation usage is a **built contract/estimator/fingerprint foundation** in
[the usage helpers](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/src/lib/server/pipeline/generation-usage.ts),
with tests; no runtime caller of its summaries/fingerprints, durable execution ledger,
actual model metering or budget enforcement was found. A pipeline stage record is
not evidence of a billable provider invocation.

Whole-scene allocation guards are already implemented and consumed by both renderers:
96 actors, 32,768 primitives, 262,144 retained rectangles and 4,194,304 backing pixels,
with a 4,096 edge cap. GAP-03 remains open for active frame-time stress, real-art loads
and physical devices; it no longer means allocation budgets are absent.

## Why this slice comes next

[Reference discovery](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/src/lib/server/reference-discovery/service.ts)
currently retains metadata, and its optional original-fetch helper can validate bytes
before an optional writer. Normal planning does not retain these as an independent
reviewed private reference authority. Existing
[PNG intake](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/src/lib/server/image-files/service.ts)
is an atlas path with distinct bounded decoding and source/manifest reviews. In
[V2 conditioning](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/src/lib/server/assets/resolve.ts),
nonfixture production references must already be approved species animation manifests.
A photo-reference record is missing; legacy V1 declaration-based packaging is not
proof that actual photo bytes, identity and rights were independently reviewed.

The new slice connects actual private file bytes to explicit review and a real local
consumer. It preserves existing V1/V2 contracts by deliberate additive admission,
keeps reference records and fake outputs non-renderable, and does not require an
image model or network availability to prove its mechanics. It does not relax the
existing sprite-atlas or taxonomy boundaries.

## Concrete task checklist

| Task | Dependency | Acceptance | Current status |
| --- | --- | --- | --- |
| RA-01: Reconcile actual status and capabilities | Existing36requirements/55findings, source and retained94-gate proof | Distinguish built consumers from fixtures, live/unavailable providers and absent integrations; retain exact IDs, old evidence and source revisions | Completed read-only assessment; no new implementation proof |
| RA-02: Define versioned reference records and exact pins | RA-01; existing shared contract authorities | Separate original/decoded identity, private owner, catalog species, intended-use rights and independent species/pose review; reject unknown versions/keys and conflicting identities; generated counterparts agree | In progress; source and tests pending |
| RA-03: Admit private PNG/JPEG originals and preview bytes | RA-02; maintained decoder/private-file patterns | Explicit byte/dimension/pixel/metadata limits; signature/format checks; malformed/truncated/oversized inputs reject before publication; original/decoded hashes bind immutable private storage; no public paths or URL-fetch bypass | Planned within current implementation scope |
| RA-04: Persist immutable approval and terminal revocation | RA-02–03 | Rights, species and pose are explicit gates; caller booleans cannot fabricate server approval; revoked identity cannot be restored/reapproved under the same exact pin; wrong owner/version/hash fails; retained evidence remains inspectable | Planned within current implementation scope |
| RA-05: Resolve exact approved references into existing runner | RA-04; existing durable jobs/provider seam | Queue/execute recheck owner, exact digest/version and current approval; revoke/missing/corrupt dependencies fail before local fake execution; retry/restart/idempotency preserve source identity; no time-of-check bypass | Planned within current implementation scope |
| RA-06: Local fake generation candidate | RA-05; strict provider/result authority | Invoke only the explicitly local fake provider through the existing runner; retained output clearly fixture/synthetic and non-renderable; review cannot make it a resident manifest or shared release; no art/model-output claim | Planned within current implementation scope |
| RA-07: Private UI and lifecycle integration | RA-03–06; current owner/auth/privacy paths | Upload/inspect/review/revoke/select exact references; two-owner isolation; reload/restart and revoked-state display; shares/analytics omit private files and source metadata; present yard/media/pins unchanged | Planned within current implementation scope |
| RA-08: Contract, regression and independent verification | RA-02–07 frozen source | Applicable strict types/lint/build, contract compatibility, meaningful corrupt/version/owner/revocation/late-result tests and actual browser flow; full suite and review bound to exact new commits | Pending; preceding94pass is historical |
| RA-09: Local evidence and task reconciliation | RA-08 | Preserve failures/logs/network/source audit, exact counts and commits; reconcile same36/55IDs; local commits only, no publication | Pending |

Fake generation is an execution-boundary test. It is not a new species sprite,
segmentation model, biological classifier, paid service or production generator.
The user-facing language must distinguish reference approval, model eligibility,
synthetic execution, candidate review and renderable artwork selection.

## Current external and source constraints

The bounded [network diagnostic](/tmp/chirp-admission-network/initial-diagnostic.json)
records direct DNS failures for Commons and GitHub, and an ordinary Commons HTTPS
request denied by the proxy with **403 Forbidden**. No DNS/proxy/security settings
were changed and no bypass was attempted. This is a transport failure, not a successful
empty search. Keep local admission useful without silently substituting external data.

The [worker audit](/tmp/chirp-admission-worker/worker-source-audit.json) confirms original
commit `c08624d3db5050603a513c73b00bb2d1697abefc` is absent from both local object stores.
The separately configured Git transport could list current remote heads, but an
isolated exact-commit fetch returned `not our ref`; this does not contradict the direct
DNS diagnostic or establish access to the missing worker. Approved handoff directories
contain no readable archive. The minimal source dependency is the original handoff ZIP
at its recorded digest or a Git bundle containing that exact commit with base/handoff
instructions. No original worker was recreated and no Library retry occurred.

The [capability inventory](/tmp/chirp-admission-worker/capability-inventory.json) finds
maintained image-decoder and CPU inference libraries; accessible model-file candidates
are packaged library fixtures. Restricted caches were not readable, so the inventory
does not assert universal absence of files outside accessible roots. Installed Sharp,
Pillow or ONNX runtimes are not approved trained image models. Real image inference
still needs a selected local task/model, immutable weights digest, model/input/output
license evidence, preprocessing/tensor contract and resource/deadline limits.

Auth configuration, a licensed bird-audio model, real observation/weather adapters,
original worker source, board/QEMU toolchain access, physical devices, production
retention/erasure policy and approved reference/concept pixels remain separate
requirements. This scope changes no credentials, providers, paid services, model
weights, firmware or publication state.
