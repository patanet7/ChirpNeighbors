# Private reference admission — local implementation and status

Private PNG/JPEG reference admission is implemented: bounded original/decoded byte
retention, separate explicit rights/species/pose reviews, terminal revocation and exact
reference pins consumed by a local diagnostic provider through the existing runner.
The private workbench connects these steps. The output is a **non-renderable 4×4 digest
grid**, not bird artwork. Existing species fixtures and resident artwork selection are
unchanged. Approved real-species/concept pixels and image-generation models remain absent.

Branches: `codex/reference-admission-local`. The tested frozen source commits are main
`7279b5626f290d8fab24ed632f6a6e57d2f2e477` and UI
`53e414077799384ba2f56340235424016a309324`. The **replacement aggregate (r2) passed 95/95 frozen gates**, completed
`2026-10-11T18:51:04.665366+00:00`. [Integrated report](LOCAL-EVIDENCE.md), [counts](LOCAL-EVIDENCE.md).
Report SHA-256: `e2c96e45510851456b4641b9a2b2092814e8b4c70dfbded1a73614afae6376e9`. Documentation/evidence
commits follow tested source commits and are reported separately in the final delivery
and Git history. Starting heads remain main `d2d0e0ed35706c762b7c69439f92cf2fbdd1618d`
and UI `a7e44323e1ff718b45fe12e4d12d2b61ac89e54a`.

The [36-entry product index](product-behavior-and-ideas.md) and
[55-finding register](audit-findings-20261009.json) retain every stable ID and historical
proof. **BUILT/TESTED** below describes a connected local boundary with named focused or
preceding integrated evidence; **FIXTURE-ONLY** describes its content/validity;
**LIVE-UNVERIFIED** describes external, physical or production acceptance; **ABSENT**
means missing implementation/input; **BLOCKED** names a concrete unavailable dependency.
There is no product-completion percentage.

## Current completion matrix

| Area | Status and actual boundary | Highest-value next dependency |
| --- | --- | --- |
| Reference photos, review and source identity — PB-014/020/021 | BUILT/TESTED bounded PNG/JPEG originals, canonical previews, immutable owner reviews, exact content/review pins and terminal revocation. Tests use technical image bytes; approved actual-species imagery is ABSENT. | Obtain authorized actual-species/concept inputs and named biological/art review; upload alone grants no rights. [Admission service](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/src/lib/server/reference-admission/service.ts), [decoder](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/src/lib/server/reference-admission/decode.ts). |
| Planning, discovery and generation — PB-021 | BUILT/TESTED versioned recipes, prompts, persisted discovery, acquisition authority and local diagnostic execution. Commons live lookup BLOCKED; real image-generation adapter/model and reviewed sprites ABSENT. Nine clips / 60 frames remain proposals, with zero produced species-art frames. | Resolve approved inputs/model contract before a real generation adapter. [Acquisition](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/src/lib/server/reference-acquisition.ts), [local bridge](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/src/lib/server/asset-pipeline/reference-generation.ts). |
| Yard and shared artwork — PB-003/004/008/009/010 | BUILT/TESTED manifests, exact releases/pins, cache/fallbacks, autonomous nine-state routines, arrivals/scatter and replay. Art is FIXTURE-ONLY: five frames / six clips; sleep/play/nest still fall back. | Review actual clip pixels/contact/loop/transition quality before production promotion. [Simulation](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/src/lib/engine/simulation.ts), [catalog selection](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/src/lib/server/assets/catalog-selection.ts). |
| Traits, objects, scenery and weather — PB-005/007/011/023/024 | BUILT/TESTED strict illustrative traits, fictional personality, four object kinds, layers/supports and procedural weather. Validated biology, persistent trait variants, arbitrary new kinds/theme IDs/world-region graph and real weather adapters are ABSENT. | Add one versioned definition/selection/storage extension with consumer/replay tests when its product need is selected. [Traits](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/src/lib/engine/behavior-profiles.ts), [scene authority](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/src/lib/scenes/manifest.ts). |
| Privacy, storage and recovery — PB-001/013/015/019/022; EN-003/011 | BUILT/TESTED private owner bytes, location-free revocable sharing, consent-off analytics, ordinary restart and existing media recovery. Reference-bearing cold restore is deliberately BLOCKED, including after store initialization before the first upload. Account-wide erasure/security-hook operation is ABSENT. | Define a reference revocation recovery protocol retaining the newest external authority before enabling reference-store restore. [Recovery refusal](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/src/lib/server/operations/lifecycle-recovery.ts), [backup CLI](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/scripts/private_backup.py). |
| Accounts and bird-audio recognition — EN-002/004 | BUILT/TESTED local auth/session flows, private WAV handling and optional ONNX execution on synthetic graphs. Actual Google/SMTP delivery LIVE-UNVERIFIED; licensed trained bird model/accuracy ABSENT. | Operator configuration and live callback/mail acceptance separately; approved audio weights/taxonomy/data plus independent accuracy evaluation. [Auth](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/src/lib/server/auth/service.ts), [ONNX adapter](../../backend-inference/app/audio_onnx/provider.py). |
| Worker and accounting — EN-005/006; PB-018 | BUILT/TESTED manually advanced durable runner and pure usage/fingerprint helpers; original autonomous worker source BLOCKED. Durable provider usage ledger/live metering and distributed platform are ABSENT. | Obtain the exact original worker archive/bundle below; do not recreate it. Add accounting alongside separately scoped real execution. [Runner](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/src/lib/server/pipeline/runner.ts), [usage foundation](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/src/lib/server/pipeline/generation-usage.ts). |
| Firmware — EN-007 | Original history integrated locally; simulator tooling/14 host tests in the preceding aggregate and eight earlier direct native tests BUILT/TESTED. Board/static and QEMU firmware scenarios BLOCKED; physical device/I2S/radio/private enrollment/TLS LIVE-UNVERIFIED. | Supported pinned board toolchain and original scenario execution, then physical acceptance. QEMU startup alone is not a firmware test. [Firmware](../../esp32-client/src/main.cpp). |
| Contracts, CI and publication — EN-001/010 | New strict additive reference contracts and gate wiring implemented; previous 94-gate checkpoint BUILT/TESTED, current 95/95 frozen aggregate BUILT/TESTED. Remote CI/deployment LIVE-UNVERIFIED; publication remains excluded. | Retain the frozen report and independent review; keep local evidence commits distinct from publication and deployment. [Aggregate runner](../../scripts/verify_system.py), [compatibility](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/src/lib/server/storage/compatibility.ts). |
| Performance and unselected outcomes — GAP-02/03/04/05; PB-006/017; EN-012 | BUILT/TESTED renderer allocation limits/cache reuse; physical-device frame time/real-art load LIVE-UNVERIFIED. Yard sound, progression, economy and operating MLOps are ABSENT/unselected. | Measure a named workload/device after real art exists; choose each product outcome and its acceptance before implementation. [Scene limits](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/src/lib/engine/scene-resource-budget.ts). |

## Concrete task checklist

| Task | Dependency | Acceptance and implementation | Current status |
| --- | --- | --- | --- |
| RA-01: Reconcile actual status and capabilities | Existing 36 requirements / 55 findings and retained source/evidence | Distinguish consumers, fixtures, unavailable providers and missing integrations; preserve exact IDs and prior proof. | Completed assessment and register reconciliation. |
| RA-02: Define versioned reference records and exact pins | RA-01; existing shared contract authorities | Separate original/canonical identity, private owner scope, catalog species, intended-use rights and explicit species/pose reviews; reject unknown keys/versions; generated contracts preserve old versions. | Implemented; additive strict contracts and focused boundary tests. Included in the complete frozen 95 compatibility run. |
| RA-03: Admit private PNG/JPEG originals and previews | RA-02; maintained decoder/private-file patterns | Enforce signature/structure, metadata, decode deadline and allocation limits; retain immutable original/canonical/RGBA hashes; reject corrupt/truncated/oversized/multipage inputs; private paths and owner-only previews. | Implemented; focused technical-image tests. No approved actual-species photo acceptance. |
| RA-04: Persist immutable review and terminal revocation | RA-02–03 | Rights, supported species and pose/action/viewpoint scope are separate owner assertions; approval cannot bypass retained source restrictions; request identity/idempotency and external tombstones fence revoked pins and stale DB state. | Implemented; focused denial/retry/restart/corruption tests. Whole-store cold restore remains blocked. |
| RA-05: Resolve exact references through the existing runner | RA-04; durable job/provider seams | Recheck live owner, hashes, all reviews and action plus direction/viewpoint scope at queue/execution/completion/review; reject missing/corrupt/revoked dependencies and late outputs; preserve bounded retry and immutable job identity. | Implemented; ENG-01 corrected with explicit left/right scope for current mirrorable side-view plans; 41 provider tests pass. |
| RA-06: Local diagnostic candidate | RA-05; strict provider/result authority | Explicit `local-fake` registry only; bounded diagnostic pixels, private provenance and `renderable:false`; approval grants no sprite pin/shared release; no network/model calls by the fake adapter. | Implemented; deterministic one-frame 4×4 digest grid. Zero species-art frames generated. |
| RA-07: Private workbench and lifecycle boundary | RA-03–06; owner/auth/privacy paths | Upload/inspect/review/revoke/select exact references; source acquisition resolves an owned saved discovery instead of caller URLs; preserve private sharing/telemetry and existing yard/artwork authority. Reject unsupported reference-store recovery before mutation. | Implemented. Clean focused browser flow passes 72/72 with front-only UI/API rejection; current R5 security/engine review and the complete frozen 95 run are recorded under RA-08. |
| RA-08: Frozen regression and independent verification | RA-02–07 frozen source | Strict types/lint/build, old/new contract compatibility, owner/version/action/viewpoint/revocation/corruption/late-output cases, actual private browser flow and renderer regressions bound to exact commits. | Retained 50 admission controls; updated 41 provider tests; clean 72/72 browser flow; R5 13 original plus six separate viewpoint controls pass. Complete frozen 95 r2 passed; r1 remains interrupted, not passed. |
| RA-09: Local evidence and register reconciliation | RA-08 | Retain failures/logs/source/network audit, exact totals and commits; reconcile the same 36/55 IDs; local delivery only. | Exact raw evidence archived and registers reconciled; the local documentation/evidence commit follows tested sources. |

## Verification boundaries and retained attempts

**95/95 frozen gates passed**, completed `2026-10-11T18:51:04.665366+00:00`. 1,967 UI tests / 118 files; 682 cross-language goldens; 16,955 deterministic mutations; 1,536 assertions in 36 browser/HTTP reports; 55 additional local auth assertions. These are overlapping named scopes, not a summed unique-test total.

[Integrated report](LOCAL-EVIDENCE.md), [counts](LOCAL-EVIDENCE.md). Report SHA-256: `e2c96e45510851456b4641b9a2b2092814e8b4c70dfbded1a73614afae6376e9`.

Current focused proof is separated by scope:

- **41 provider tests** pass after six viewpoint cases were added: four rejected
  front/back/three-quarter/other-only reviews and two admitted left/right reviews.
  The [provider log](LOCAL-EVIDENCE.md)
  is the updated result; the earlier 35-test log remains historical.
- **72/72 browser checks** pass at the replacement UI commit with unchanged clean
  source, no runtime errors and zero external requests. The
  [focused report](LOCAL-EVIDENCE.md) uses the
  actual development app with temporary owners/SQLite and technical PNG/JPEG bytes.
  Fully approved front-only history stays visible, while UI queueing and a direct API
  attempt are rejected without jobs/stages/artifacts or yard changes.
  [Focused media review](LOCAL-EVIDENCE.md) inspected
  six screenshots and decoded the full 257-frame video. Its final section has gray
  padding; the standalone candidate image is readable. [Integrated media review](LOCAL-EVIDENCE.md)
  separately verified all six integrated screenshots and the 260-frame, 10.40-second
  VP8 capture at 1024×768; its full decode passed. The focused 257-frame capture
  remains separately retained.
- [R5 security review](LOCAL-EVIDENCE.md)
  replays the original **13 controls** and adds **six separate viewpoint controls** at
  the new source. These are distinct from the six added provider unit cases.
  [Exact binding](LOCAL-EVIDENCE.md).
  [Engine review](LOCAL-EVIDENCE.md) closes ENG-01.
- The retained [admission receipt](LOCAL-EVIDENCE.md)
  includes **50 admission controls** (20 decoder, 20 service, 10 discovery) and the
  then-current 35 provider tests, for **85 at that earlier source**. It transcribes
  observed tool output with later source binding; it is not a fabricated raw log or
  a fresh 91-test suite. The admission implementation is unchanged by the viewpoint
  correction. The complete aggregate reran applicable suites at the replacement commit.

**Retained attempts and correction:** the first browser attempt had 57 functional
checks pass and its source-freeze guard fail (58 checks); its
[report](LOCAL-EVIDENCE.md) is not a completed
frozen browser pass. The first aggregate at UI `033c0ce17772532a58294e2481459e8fbb57b811`
was deliberately stopped after **60 recorded passing gates** when independent engine
review found ENG-01: pose action permission was enforced but viewpoint permission was
not. Its active audio gate finished **53 passing checks** and cleaned up before the
scheduler terminated; those checks are not an additional recorded aggregate gate or
full pass. [Interruption receipt](LOCAL-EVIDENCE.md).
No source changed during that partial run. Original R4 security proof is preserved:
its 13 controls did not detect the viewpoint gap, so it does not verify the correction.

The replacement shared consumer and private UI now require an explicit reviewed
`left` or `right` view for the current `right-facing-mirrorable` recipe. A front/back/
three-quarter/other-only review cannot authorize that plan, and unsupported future
directions fail closed. Approved history is still retained. The correction reaches
queue, execution, transactional completion and artifact review through the same live
consumer. The **95/95 frozen r2 aggregate passed** at the replacement source; focused
proof remains separately retained rather than substituted for aggregate completion.

Additional root acquisition/lifecycle/compatibility controls overlap these suites and
the full unit run. Final aggregate counts come from the retained [counts](LOCAL-EVIDENCE.md); do not
sum focused/unit/browser/security scopes as unique tests. Source/type/lint/format
checks do not prove actual species fidelity or successful live retrieval.

The [preceding complete checkpoint](animation-planning-20261011.md) remains **94/94**
at main `7311d2496f66074bdc5fcfd70abfaec7a0127115` and UI
`e389a1f83e15057a8625dc7b7a10ca011442db6e`: 1,823 UI tests, 35 browser/HTTP reports with
1,464 recorded assertions and 55 additional local auth-provider assertions. Its
107-assertion planning flow uses synthetic Commons metadata in the actual app.
These historical scopes overlap and do not verify the new reference source commits.

Reference recovery is an explicit residual requirement. Ordinary process restart and
same-store revocation checks are implemented. The supported cold-restore path refuses
initialized/partial reference schemas and nonempty reference storage, including dry
runs, before installing an older database. Replacing both a database and its external
revocation files from an old complete filesystem is not secured by this implementation.
The recording-deletion export retains its old scope; it is not a reference-revocation
export. Existing no-reference backup/restore remains supported.

## Next priorities and required inputs

1. Define reference recovery before relying on backup restore for admitted references:
   versioned newest-authority export/import, source/store identity binding, stale or
   missing authority refusal, idempotent full/dry-run recovery and late-output fences.
   This depends on an explicit operator/offline-copy policy; it cannot infer the newest
   revocation state from an older snapshot alone.
2. Supply authorized actual-species reference/concept material and a selected local
   model bundle. Require immutable weights digest, per-file model/input/output rights,
   task and tensor/preprocessing/output contract, resource/deadline limits and named
   biological/art reviewer. Decoder/runtime libraries do not provide trained models.
   New frame production must separately prove alpha, species identity, anchors/contact,
   action/pose/direction coverage, loop/transition consistency and provenance before
   any production manifest or shared release. The diagnostic candidate grants none of
   these approvals.
3. Obtain the original worker source: `ChirpNeighbors-code-handoff-20261008.zip`,
   reported **41,686 bytes**, SHA-256
   `09634e2479d6709daefb4a79c8d8b14c71ac1fec9d3b79a154fede581f32109a`, or an original
   Git bundle containing commit `c08624d3db5050603a513c73b00bb2d1697abefc` with its exact
   base and handoff instructions. Verify identity before integration; do not recreate
   a substitute worker or retry the blocked Library materialization.
4. Keep live auth/mail, licensed audio-model evaluation, real import/weather adapters,
   board/QEMU/physical hardware, production security/erasure, runtime usage accounting
   and real-art performance as separately accepted work with their named inputs.

The [bounded network diagnostic](LOCAL-EVIDENCE.md)
records direct Commons/GitHub DNS failures and ordinary Commons HTTPS proxy **403
Forbidden**. This is blocked transport, not a successful empty lookup. No bypass or
network/credential/security setting change was attempted. A separately configured Git
transport listed remote heads, but an isolated fetch of the original worker commit
returned `not our ref`; it supplied no missing source. No readable approved archive
was found. [Worker/source audit](LOCAL-EVIDENCE.md).

The [capability inventory](LOCAL-EVIDENCE.md) found
maintained image decoders and CPU inference libraries, with only packaged model
fixtures in accessible candidate locations. Restricted caches were unreadable; this
is not a universal claim about inaccessible files. No approved image model was
executed or downloaded. This slice changes no credentials, paid services, trained
weights, firmware or publication state.
