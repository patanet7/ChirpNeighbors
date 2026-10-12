# Engineering and external dependencies

Canonical requirements and acceptance for this topic. Stable IDs, decisions, dependencies and named evidence are retained from the [task index](../delivery/product-behavior-and-ideas.md). U: paths refer to the UI repository; M: paths refer to ChirpNeighbors. Evidence labels resolve through the [verification ledger](../delivery/verification-ledger.md). Current GitHub publication is tracked separately in the [release record](../publication/20261011/README.md).

Lettered IDs below are implementation subtasks of the existing requirement, not new competing requirements. Their status is recorded as of the 2026-10-12 [architecture review](../architecture/architecture-review-20261012.md). “In progress” does not claim a completed fix, integrated verification, hosted pass or deployment. Update status here after the exact candidate's acceptance is established; dated review/checkpoint documents remain evidence.

### EN-001 — Single contract authority, generated consumers and strict compatibility gates

**Source / decision:** Architecture/delivery record; not new user authorization; Established architecture constraint. **Implementation:** Implemented. **Integration:** Local integrated checkpoint including four additive ontology authorities (E-INT). **Release / production:** See [current release status](../publication/20261011/README.md); historical local integration is not production validation.

**Architecture:** U:contracts/authority-inventory-v1.json; U:scripts/contract-tools; M:contracts; M:scripts/verify_system.py.

**Behavioral acceptance:** One Zod/Pydantic authority per actual boundary; deterministic exports/types and independent semantic admission; bidirectional golden/property tests reject drift; explicitly version changed reader behavior and inventory each HTTP/SSR/store/config boundary.

**Tests and evidence:** [U:scripts/contract-tools/boundary-inventory.test.ts](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/scripts/contract-tools/boundary-inventory.test.ts); [U:scripts/contract-tools/compatibility.test.ts](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/scripts/contract-tools/compatibility.test.ts); [M:backend-inference/tests/test_schema_document.py](../../backend-inference/tests/test_schema_document.py). [E-CAT:contract-inventory.log](../delivery/LOCAL-EVIDENCE.md); [E-CAT:contract-compatibility.log](../delivery/LOCAL-EVIDENCE.md); [E-CAT:zod-python-roundtrips.log](../delivery/LOCAL-EVIDENCE.md); [E-FOCUS](../delivery/LOCAL-EVIDENCE.md).

**Corrected integrated evidence:** [E-INT:ui-unit.log](../delivery/LOCAL-EVIDENCE.md); [E-INT:contract-inventory.log](../delivery/LOCAL-EVIDENCE.md); [E-INT:contract-compatibility.log](../delivery/LOCAL-EVIDENCE.md); [E-INT:zod-python-roundtrips.log](../delivery/LOCAL-EVIDENCE.md); [E-INT:zod-python-properties.log](../delivery/LOCAL-EVIDENCE.md); [E-INT:pydantic-typescript-roundtrips.log](../delivery/LOCAL-EVIDENCE.md); [E-INT:pydantic-typescript-properties.log](../delivery/LOCAL-EVIDENCE.md).

**Representative exact current assertions:** [ontology-contracts.test.ts](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/src/lib/engine/ontology-contracts.test.ts): “rejects biological claims and observation metadata”; `ontology-contracts.test.ts`: “admits maximal derived scene slot identities without private source fields”; `ontology-contracts.test.ts`: “limits developer experiments to closed transient presets”.

**Dependencies:** None. **Remaining gap:** Structural validation is not owner/review authorization; inventory proves declarations/paths, not every runtime branch. Ontology adds four authorities, not biology validation. **Next action:** Keep exact authority inventory/semantic exceptions reviewed before future schemas.

**Additive planning/discovery authorities (E-PLAN):** New recipe, planning-input-v2 and reference request/result/candidate/policy/receipt contracts derive from shared validators and extend generated compatibility evidence. Existing planning v1 schema/plan bytes and unknown-version rejection remain preserved. Definitions/defaults/overrides compose bounded content; new taxonomy, object kinds, palettes and world inheritance still require deliberate storage and consumer admission.

**Recovery authority extension (E-REC; local integrated checkpoint):** One strict versioned reference-authority export composes existing admission records and request/review/revocation semantics. Schema export, cross-language agreement and runtime validation must cover every row; an outer hash alone is insufficient. No new taxonomy or parallel review authority is introduced.

### EN-002 — Session-bound email-link/Google identity and production provider setup

**Source / decision:** Architecture/delivery record; not new user authorization; Selected direction; credentials/operating policy external. **Implementation:** Maintained-library boundaries and labelled mocks implemented. **Integration:** Local protocol integration; production provider unavailable. **Release / production:** See [current release status](../publication/20261011/README.md); historical local integration is not production validation.

**Architecture:** U:src/lib/server/auth; U:src/hooks.server.ts; M:backend-inference/app/models/session_verifier.py.

**Behavioral acceptance:** Library-backed email/OIDC flow rejects replay/expiry/bad PKCE/signature; persistent sessions/logout/linking isolate owners; missing real configuration fails closed; actual app/local SMTP/signed Google mocks remain labelled.

**Tests and evidence:** [U:src/lib/server/auth/service.test.ts](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/src/lib/server/auth/service.test.ts); [U:src/lib/server/auth/email.test.ts](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/src/lib/server/auth/email.test.ts); [U:scripts/auth-integration.ts](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/scripts/auth-integration.ts); [U:scripts/auth-browser-checks.py](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/scripts/auth-browser-checks.py). [E-CAT:auth-provider-integration.log](../delivery/LOCAL-EVIDENCE.md); [E-CAT:auth/auth-browser-results.json](../delivery/LOCAL-EVIDENCE.md).

**Dependencies:** EN-001, PB-013. **Remaining gap:** No real mail/OIDC provider credentials/callback/transport verification; old PRD password JWT endpoint is not active application authority. **Next action:** Operator-owned provider/configuration review in a separate task; do not change credentials here.

### EN-003 — Local operations, recovery and eventual US hosting/rollback

**Source / decision:** Architecture/delivery record; not new user authorization; Local reliability agreed; US hosting direction selected, deployment excluded. **Implementation:** Host health/readiness/log/backup/recovery implemented; containers unverified. **Integration:** Local host integration; no deployed environment. **Release / production:** See [current release status](../publication/20261011/README.md); historical local integration is not production validation.

**Architecture:** U:src/lib/server/operations; U:scripts/private_backup.py; U:docs/local-operations.md.

**Behavioral acceptance:** Restricted structured logs omit private payloads; readiness/request budgets and graceful shutdown behave predictably; new-directory backup/restore verifies schema/hash/lineage and revokes restored capabilities; before deployment prove region, encryption, restore and rollback on actual built images.

**Tests and evidence:** [U:src/lib/server/operations/operations.test.ts](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/src/lib/server/operations/operations.test.ts); [U:src/lib/server/operations/request-budget.test.ts](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/src/lib/server/operations/request-budget.test.ts); [U:scripts/tests/test_private_backup.py](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/scripts/tests/test_private_backup.py). [E-CAT:operations-http.log](../delivery/LOCAL-EVIDENCE.md); [E-CAT:private-recovery-tests.log](../delivery/LOCAL-EVIDENCE.md).

**Dependencies:** EN-001, EN-002, EN-011. **Remaining gap:** Docker image execution previously blocked by registry network/DNS; no fresh container success claimed. Hosting, encryption and real restore/rollback remain unperformed. E-REF deliberately refuses cold restore of initialized/partial reference authority or retained reference files before mutation; ordinary no-reference media recovery remains supported. **Next action:** Establish independently retained latest-receipt custody and offline-writer procedure for the bounded E-REC path; verify built containers/US infrastructure only in separately scoped work.

**Current recovery work (E-REC; local integrated checkpoint):** `export-references SOURCE DEST --offline` and explicit `restore --references FILE --expected-reference-sha256 DIGEST` now extend the existing CLI. The digest must be independently retained as the latest receipt. All writers must be stopped, source/backup admissions must match exactly, and all bytes/rows/tombstones must validate before atomic no-clobber directory publication. Missing/invalid authority, post-backup admissions and destination conflicts must preserve the source and existing destination unchanged. E-REF refusal remains the historical default; production recovery and dishonest-receipt rollback remain unproven.

#### EN-003-A — Reject served private data roots

**Status / priority:** In progress; confirmed high-severity configuration defect, acceptance pending. **Review:** CSA-01. **Dependencies:** PB-013; existing private-root and build/startup boundaries. No provider or artwork input is needed.

**Work:** Reject application data paths within source/generated served roots, including prospective paths and symlink aliases, before creation/chmod/open and before a built server listens. Retained files are served ahead of lazy application hooks; do not move/delete operator data to repair configuration.

**Acceptance tests:** Fresh and retained `public`/`build/client` roots fail without byte/permission changes; symlink/nonexistent ancestors cannot bypass validation; sibling private roots remain valid. Built-server unauthenticated requests after restart cannot download DB/WAL/SHM/journal or private media. Ordinary private startup, owner isolation and restore still work. [Reproduction evidence](../architecture/architecture-review-20261012.md#contracts-storage-authentication-and-privacy).

#### EN-003-B — Repeatable loopback development lifecycle

**Status / priority:** In progress; high-priority fixture exposure repair plus bounded developer experience. **Reviews:** CSA-02, RDX-001, RDX-002, RDX-005. **Dependencies:** EN-003-A for safe storage validation; existing Node/SvelteKit app. Node-only yard startup does not depend on Python services, the original worker, providers or approved art.

**Work:** Pin supported mise tools and compose bootstrap/check/test/build/dev/status/stop around existing authorities. Default to loopback and explicit fixture identity, validate ports and report the actual origin, separate optional receiver/service tasks, and preserve local data. Dynamic allocation must use the actual bound address. Use a live owned controller for shutdown; no kill-by-port, stale-PID targeting, automatic tunnel or OS service. The [UI setup guide](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/runtime-safety-20261012/docs/setup.md) owns executable startup instructions.

**Acceptance tests:** Fresh and warm bootstrap; normal fixture sign-in/sample yard; persistence and session re-selection after restart; simultaneous same-checkout launch admits only one controller; isolated dynamic instances have distinct working origins. Occupied/invalid ports leave unrelated listeners intact. Missing dependencies, bad storage and readiness timeout fail with bounded owned cleanup. Ctrl-C/SIGTERM/stop release HTTP/HMR and are idempotent. Private state is excluded from Git/static serving; forms/session binding use the actual origin; production fixture login remains closed. Check/test/build failures propagate. State clearly which operating systems were executed and whether a preview is user-accessible. [Review basis](../architecture/architecture-review-20261012.md#runtime-developer-experience-and-ci).

#### EN-003-C — Hold read admission through stream completion

**Status / priority:** Open, confirmed medium-severity resource-budget defect. **Review:** CSA-03. **Dependencies:** PB-012; existing request budget and recording blob cleanup; no external input.

**Work:** Retain read admission for the response body's lifetime, or add an equivalent bounded playback lease. Release exactly once on completion/error/cancel and propagate cancellation to the original body. Preserve immediate cleanup for HEAD/no-body failures.

**Acceptance tests:** Hold 16 owner streams and reject the 17th until release; exercise 64 global streams across owners. Finish, cancel, disconnect, read failure and deletion-midstream close the blob and release one permit. HEAD/error responses cannot leak capacity. Include a built-server slow-reader test, not only a counter unit test. [20-open-stream reproduction](../architecture/architecture-review-20261012.md#contracts-storage-authentication-and-privacy).

#### EN-003-D — Reproduce verification from explicit environments

**Status / priority:** Documentation corrected here; clean-install/runtime acceptance remains open, P2. **Review:** RDX-003. **Dependencies:** exact declared tool/dependency pins, supported browser libraries; EN-003-B for optional task wrappers.

**Work:** [Aggregate setup](../delivery/quality.md) separates core, browser, ONNX and intake interpreters, installs complete browser requirements including Pillow, and passes all interpreter paths. Preserve core/model isolation and explicit browser OS prerequisites. Keep ordinary UI startup lightweight.

**Acceptance tests:** A clean supported machine follows the documented commands without inherited packages; imports/version checks confirm the intended packages in each environment and NumPy/ONNX remain absent from core. Warm bootstrap is idempotent; failed installs create no success marker. `verify_system.py --list` resolves the same commands/interpreters, then a committed frozen run records its actual result. Syntax/command inspection alone does not close clean-platform acceptance.

### EN-004 — Real audio model accuracy, taxonomy calibration and independent ML execution

**Source / decision:** Architecture/delivery record; not new user authorization; Real identification goal agreed; old numeric targets unvalidated proposals. **Implementation:** Validation/chunking/fixture/optional local ONNX adapters implemented. **Integration:** Technical cross-process integration only. **Release / production:** See [current release status](../publication/20261011/README.md); historical local integration is not production validation.

**Architecture:** M:backend-inference/app/audio_pipeline; M:backend-inference/tests/optional; M:docs/architecture/audio-pipeline.md.

**Behavioral acceptance:** Bound actual audio bytes/duration/chunks; exact licensed model/digest/taxonomy pin and unconfigured state; synthetic graph proves loading/inference mechanics only. Real acceptance needs representative licensed withheld recordings, reviewed thresholds and per-species error/calibration report before accuracy claims.

**Tests and evidence:** [M:backend-inference/tests/test_audio_api.py](../../backend-inference/tests/test_audio_api.py); [M:backend-inference/tests/test_audio_pipeline.py](../../backend-inference/tests/test_audio_pipeline.py); [M:backend-inference/tests/optional/test_audio_onnx.py](../../backend-inference/tests/optional/test_audio_onnx.py); [M:backend-inference/tests/optional/test_technical_fixture.py](../../backend-inference/tests/optional/test_technical_fixture.py). [E-CAT:python-audio-tests.log](../delivery/LOCAL-EVIDENCE.md); [E-CAT:onnx-technical-tests.log](../delivery/LOCAL-EVIDENCE.md); [E-CAT:synthetic-audio-evaluation.log](../delivery/LOCAL-EVIDENCE.md).

**Dependencies:** PB-012, EN-001, EN-006. **Remaining gap:** No approved compatible bird weights or real biological validation. Historical ≥92% top-5, <600ms and 50RPS targets are neither measurements nor approved release gates. **Next action:** Select and license compatible model/dataset, then define representative evaluation; no model download/provider activation in this slice.

### EN-005 — Autonomous delivery, WebSocket scaling and legacy coordinator/gateway alternatives

**Source / decision:** Architecture/delivery record; not new user authorization; Legacy architecture proposal; current implementation choice not reaffirmed. **Implementation:** Only current local service boundaries implemented. **Integration:** Proposed distributed/realtime architecture not integrated. **Release / production:** See [current release status](../publication/20261011/README.md); historical local integration is not production validation.

**Architecture:** M:docs/architecture/product-requirements.md sections 1–4, 7–8; current SvelteKit BFF/FastAPI audio boundary.

**Behavioral acceptance:** Before real-time/distributed expansion choose transport and replay/ack/backpressure/tenancy contract; test reconnect, missed-event recovery, cancellation and user-visible updates under an agreed measured load. Preserve nonblocking UI and explicit human confirmation.

**Tests and evidence:** No executable acceptance test for this requested outcome. No passing outcome evidence or tested implementation commit.

**Dependencies:** EN-001, EN-006, EN-007, EN-003. **Remaining gap:** Original SQLModel/JWT coordinator, C++23 Asio TLS/gRPC gateway, Redis/NATS fanout, 100/10k socket targets, 500-device generator and numerical latency/RSS SLOs are historical proposals, not current proven system. No equivalent full-scale benchmark found. **Next action:** Re-decide smallest needed topology and acceptance load from actual requirements; do not implement a competing backend from stale PRD.

### EN-006 — Integrate the original separately completed autonomous worker

**Source / decision:** Architecture/delivery record; not new user authorization; Transfer already authorized; transport technically blocked. **Implementation:** Reported external artifact unavailable locally. **Integration:** Unintegrated. **Release / production:** See [current release status](../publication/20261011/README.md); historical local integration is not production validation.

**Architecture:** M:docs/delivery/approved-handoff-blocker-20261008.md; existing manually advanced fixture runner.

**Behavioral acceptance:** After readable original artifact arrives, validate exact digest/archive/base ancestry, inspect original worker, then prove single lease claim across workers, crash/backoff/cancel/late-output fences, review pause and graceful shutdown without duplicate provider calls.

**Tests and evidence:** No executable acceptance test for this requested outcome. [E-HANDOFF](../delivery/approved-handoff-blocker-20261008.md).

**Dependencies:** EN-001, PB-012, PB-018. **Remaining gap:** Worker c08624d3 not materialized; supported preparation/download failed twice before bytes. Network transport class known; underlying DNS/TLS cause unknown. No worker execution proof in this checkout. **Next action:** Repair supported artifact materialization through owning task; do not recreate worker or retry transfer here.

**Current source audit (E-REF):** The original exact commit is absent locally; a fresh isolated fetch through the configured Git transport returned `not our ref` after remote-head listing succeeded. No readable approved handoff archive was found. Required input: `ChirpNeighbors-code-handoff-20261008.zip` (reported 41,686 bytes), SHA-256 `09634e2479d6709daefb4a79c8d8b14c71ac1fec9d3b79a154fede581f32109a`, or an original Git bundle containing `c08624d3db5050603a513c73b00bb2d1697abefc` with its declared base/instructions. Do not infer that a generic network retry supplies that source. No original worker was recreated and no Library retry was performed.

### EN-007 — Integrate the original published ESP32/device history without duplication

**Source / decision:** user-authorized normal Git inspection and local integration after the completed environment checkpoint. **Implementation:** Original four-commit branch fetched and reviewed at the exact reported head; runtime code unchanged from it. **Integration:** Locally merged with passing scoped host/native/regression evidence (E-ESP); board/static/simulator reruns blocked by toolchain setup. **Release / production:** See [current release status](../publication/20261011/README.md); historical local integration is not production validation.

**Architecture:** Original device-to-backend boundary in [M:app/main.py](../../backend-inference/app/main.py), [packet/capture/transport modules](../../backend-inference/app/services), and [firmware protocol](../../esp32-client/include/audio_protocol.h). The separate loopback-default development receiver does not call the authenticated private recording API, identify species or admit residents. `intake-quality.toml` isolates its strict checks while the existing core `pyproject.toml` remains unchanged.

**Behavioral acceptance:** Exact reported head/ancestor, preserved environment branches and normal two-parent local merge; review actual framing/endian/limits, loss/duplicate/wrap/gaps, bounded queues, cancellation/reconnect and unchanged ownership boundaries. Run explicit intake/native and relevant existing regressions on frozen sources. Hardware, authenticated device-to-owner recording admission and biological model accuracy remain separate acceptance scopes.

**Tests and evidence:** [E-ESP checkpoint](../delivery/esp32-integrated-20261009.md), [source hashes](../delivery/LOCAL-EVIDENCE.md), [host checks](../delivery/LOCAL-EVIDENCE.md), [firmware checks/setup failures](../delivery/LOCAL-EVIDENCE.md) and [25-gate selected report](../delivery/LOCAL-EVIDENCE.md). Main `4ce5fb535c38f67a3f31caf3a2c7ebfb988a9ceb` / UI `03574ee8509e7e45d79e0e745b6ef38fd042aca4`: 52 host tests, 96% coverage, eight native tests with ASan/UBSan, formatting and 205 browser/HTTP assertions pass. All incoming runtime sources match `99c01c6b41de67e2f5e11b46e8e7488a1a33aa4c`. Historical upstream emulator results are not counted as new local passes.

**Dependencies:** Completed PB-023/PB-024 checkpoint; EN-001, EN-004, EN-005. **Remaining gap:** PlatformIO registry proxy CONNECT 403 prevents metadata resolution and compilation. The prior successful workspace used a separate cache that is absent here. QEMU now starts after a verified temporary official Debian `libslirp0` repair; this is not a firmware scenario pass. See the [exact diagnosis](../delivery/LOCAL-EVIDENCE.md). Board static checks and protocol/control simulator reruns remain unrun here. Physical I2S/radio/stack/slow-peer/settings behavior, device authentication/TLS/owner binding, short-burst policy and remote CI remain unverified. EN-006's original worker transfer is separately unresolved. **Next action:** Restore supported pinned toolchain access and rerun original board/static/simulator checks with retained failure evidence; then validate hardware and design the authenticated private recording adapter. No Library retry, replacement firmware, publication or flash is authorized by this checkpoint.

**Verification-scope clarification:** E-PLAN includes simulator Python-tooling checks and 14 host tests, plus static negative controls; earlier E-ESP retains eight direct native tests. These are separate from ESP32 board compilation/cppcheck, QEMU firmware scenario execution and physical-device validation, which remain blocked or unverified. The complete 94-gate label does not convert host simulator tests into firmware execution.

### EN-008 — One authorized real source import and trusted arrival adapter

**Source / decision:** Architecture/delivery record; not new user authorization; Agreed future adapter boundary. **Implementation:** Generic import/manual path implemented; real adapter absent. **Integration:** Real source not integrated. **Release / production:** See [current release status](../publication/20261011/README.md); historical local integration is not production validation.

**Architecture:** U:src/lib/domain/evidence.ts; U:src/lib/server/arrivals; U:docs/pending-arrival-adapters.md.

**Behavioral acceptance:** An authorized representative eBird personal-data artifact (distinct from eBird API 2.0), or another explicitly documented selected source, preserves source/taxonomy IDs and observed/unknown time; preview/errors visible; replay dedupes; only server-reviewed genuine confirmation can admit arrival receipt; unsupported data stays unknown.

**Tests and evidence:** [U:src/lib/server/arrivals/adapter-eligibility.test.ts](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/src/lib/server/arrivals/adapter-eligibility.test.ts); [U:src/lib/server/storage/findings.test.ts](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/src/lib/server/storage/findings.test.ts). [E-CAT:ui-unit.log](../delivery/LOCAL-EVIDENCE.md).

**Dependencies:** PB-001, PB-010, PB-013. **Remaining gap:** Tests cover eligibility contracts/generic imports only, not a real Cornell integration. No representative authorized format/provider adapter exists. Merlin documents owner audio sharing and independent confirmation, not an established structured detection API/export here; BirdWeather is not a selected adapter. **Next action:** Obtain a permitted sample and exact source semantics, then implement one bounded adapter; do not fabricate API access. The [connection inventory](../delivery/LOCAL-EVIDENCE.md) separates those interfaces and rights.

### EN-009 — Real regional weather and explicit coarse-location consent

**Source / decision:** Architecture/delivery record; not new user authorization; Future adapter direction; provider/location approval absent. **Implementation:** Simulated/manual/unconfigured provider boundaries implemented. **Integration:** Real weather not integrated. **Release / production:** See [current release status](../publication/20261011/README.md); historical local integration is not production validation.

**Architecture:** U:src/lib/server/weather/provider.ts; U:src/lib/weather; U:src/lib/domain/scene.ts.

**Behavioral acceptance:** Offline manual/simulated weather remains usable; real provider requires explicit owner coarse-location consent, bounded timeout/cache/stale/error states and no location in shared/render payloads.

**Tests and evidence:** [U:src/lib/server/weather/provider.test.ts](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/src/lib/server/weather/provider.test.ts); [U:src/lib/weather/weather.test.ts](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/src/lib/weather/weather.test.ts); [U:scripts/layered-browser-checks.py](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/scripts/layered-browser-checks.py). [E-CAT:layered/layered-browser-results.json](../delivery/LOCAL-EVIDENCE.md); [E-CAT:ui-unit.log](../delivery/LOCAL-EVIDENCE.md).

**Dependencies:** PB-011, PB-013. **Remaining gap:** No real provider/geolocation exercised; a region preference is not live weather or a precise-location grant. **Next action:** Choose authorized provider/coarsening policy in a separate task, then test actual failure/revocation semantics.

**Integrated environment extension (E-ENV; separate from E-INT):** PB-023/PB-024 add local illustrative rendering and behavior without a real provider or location consent. The [environment browser report](../delivery/LOCAL-EVIDENCE.md) verifies neutral unconfigured real weather, transient saved-clock previews and unchanged private/public state. Persisted weather contracts and external provider dependencies remain unchanged; the local pass does not establish real weather integration.

### EN-010 — Publication/PR and production checkpoint

**Source / decision:** The original local task excluded publication; subsequent user instructions authorized engine PRs/merges and later the separately reviewed documentation PRs/merges. **Implementation:** Engine review branches published. **Integration:** Both engine PRs merged; subsequent documentation/runtime candidates require their own exact source/check review. **Release / production:** See [current release status](../publication/20261011/README.md); no deployment is established by a Git merge.

**Architecture:** Git/review/release boundary; source user delegation, historical publication log.

**Behavioral acceptance:** Verify exact reviewed/tested heads, remote ancestry and applicable required reviews/checks before each authorized merge; preserve actual hosted failures even where policy does not require the check. A local commit is never reported as pushed/merged, and a merge is not production validation. Authorized local ESP32 integration is separately recorded under EN-007.

**Tests and evidence:** [Current engine PR URLs, merge SHAs and hosted outcomes](../publication/20261011/README.md); [E-PUBLICATION](../agents/20261007_183500_publication-checks.md) retains the earlier blocked attempt. Publication acceptance is repository/CI/source evidence, not an application unit-test result.

**Dependencies:** Exact candidate verification, repository checks/reviews and the user's action-specific authority. **Remaining gap:** The UI engine job failed twice at startup without recorded steps; the cause remains unestablished in the retained evidence. Local proof does not turn it into a hosted pass. Documentation merges are now authorized but this documentation change does not attest their execution. Deployment remains separate and unperformed. **Next action:** EN-010-A establishes hosted outcome, EN-010-B reconciles coverage, EN-010-C keeps task status singular; record each actual merge in the [release record](../publication/20261011/README.md).

**Subsequent local integration (E-ESP; separate from E-ENV):** The actual fetched ESP32 branch is now locally merged and scoped verification is retained. This does not publish the environment/ontology workstream or establish remote CI, a PR, remote merge, deployment or flashing. No publication retry or Library workaround occurred.

#### EN-010-A — Establish the hosted UI job outcome

**Status / priority:** Open external diagnosis; no established code or account cause. **Dependencies:** permitted exact-run/head/workflow/job metadata or logs. No spending, credential, permission or deployment change is implied.

**Acceptance:** Identify the actual runner/platform/account or executed-step failure from permitted evidence; make only the supported in-scope repair and retain original failures. A verified success requires completed checks on the exact candidate. If evidence confirms an account/access blocker, record its precise message and smallest user action; do not repeat blind retries or bypass a denied endpoint. [Retained failure scope](../architecture/architecture-review-20261012.md#runtime-developer-experience-and-ci).

#### EN-010-B — Reconcile hosted and local suite coverage

**Status / priority:** Open, P2 coverage drift; no hosted pass claimed. **Review:** RDX-004. **Dependencies:** EN-003-D environments; classify UI-only versus paired-service scripts before workflow changes. Hosted execution additionally depends on EN-010-A.

**Acceptance tests:** A checked inventory classifies every intended browser suite as included or deliberately excluded with a reason. Cover the reviewed ontology/retention/catalog/environment omissions; explicitly scope animation-planning/reference-admission/reference-recovery/audio-lifecycle prerequisites. Build failure blocks browser execution; shared-port/GPU suites stay sequential. Local wrappers and CI use one suite authority or a checked mapping. Separate per-repository CI from cross-repository agreement in reports.

#### EN-010-C — Maintain one current task authority

**Status / priority:** In progress, P2; main review findings/status links consolidated here, paired UI historical-label reconciliation and integrated review pending. **Review:** RDX-006. **Dependencies:** actual reviewed code/CI evidence from each implementation owner.

**Acceptance:** Every review finding maps to one PB/EN requirement/subtask with current status, dependencies and observable acceptance. Historical task tables remain dated evidence, preserving unique requirements/provenance and failed attempts, with links to the canonical index. Main/UI setup links resolve; stale ESP32/publication checkboxes do not masquerade as current blockers. Do not mark another branch's planned fix complete before receiving its commit and verification evidence.

### EN-011 — Account-wide erasure, offline retention and deletion-history operating policy

**Source / decision:** Architecture/delivery record; not new user authorization; Remaining privacy/operations requirement; destructive policy not selected. **Implementation:** Bounded media tombstones/cleanup/archive/recovery implemented. **Integration:** Account-wide/distributed deletion not integrated. **Release / production:** See [current release status](../publication/20261011/README.md); historical local integration is not production validation.

**Architecture:** U:src/lib/server/recordings/lifecycle-storage.ts; U:src/lib/server/operations/lifecycle-recovery.ts; U:scripts/private_backup.py.

**Behavioral acceptance:** Existing tombstones fence reads/new permits/late outputs; restore uses complete newest retained deletion ledger. Future erasure must enumerate account/derived/backup/download copies and prove bounded failure/retry/recovery without silently resurrecting content.

**Tests and evidence:** [U:src/lib/server/recordings/lifecycle.test.ts](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/src/lib/server/recordings/lifecycle.test.ts); [U:src/lib/server/operations/lifecycle-recovery.test.ts](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/src/lib/server/operations/lifecycle-recovery.test.ts); [U:scripts/tests/test_private_backup.py](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/scripts/tests/test_private_backup.py). [E-CAT:recording-lifecycle/recording-lifecycle-browser-results.json](../delivery/LOCAL-EVIDENCE.md); [E-CAT:lifecycle-recovery-http.log](../delivery/LOCAL-EVIDENCE.md).

**Dependencies:** PB-012, PB-013, PB-022, EN-003, EN-006. **Remaining gap:** No automatic discovery/erasure of offline copies, account-wide orchestrator, production purge or guarantee of newest ledger; archive is not deletion authorization. E-REF adds terminal reference revocation for the current store, but cannot secure rollback of both database and external tombstones from an older entire filesystem; supported reference-store cold restore is deliberately refused. Recording-deletion export is not a reference-revocation export. **Next action:** Establish latest-receipt custody and owner/operator retention/erasure policy; preserve the E-REC freshness limit. Original worker integration precedes distributed cleanup.

**Bounded reference cold recovery (E-REC; local integrated checkpoint):** Complete current review/revocation/idempotency authority may reconcile only a backup with the same immutable admission set. The independently retained latest digest binds bytes but cannot prove newestness when both authority and receipt roll back. Loss of genuine authority or the trusted receipt remains blocked. Existing recording-deletion evidence stays separate; this introduces no purge, erasure policy or discovery of offline copies.

### EN-012 — MLOps/model registry, training, monitoring and numeric performance ideas

**Source / decision:** Architecture/delivery record; not new user authorization; Legacy architecture proposals; tools/SLOs not adopted by this task. **Implementation:** Not implemented as an operating platform. **Integration:** Not integrated. **Release / production:** See [current release status](../publication/20261011/README.md); historical local integration is not production validation.

**Architecture:** M:docs/architecture/product-requirements.md sections 5–8; M:docs/architecture/audio-pipeline.md.

**Behavioral acceptance:** If adopted, first approve datasets/licenses, dataset/model/preprocessing versions, reproducible held-out evaluation and rollout/rollback criteria; test actual model registry, backups, drift metrics and resource budgets on the chosen runtime.

**Tests and evidence:** No executable acceptance test for this requested outcome. No passing outcome evidence or tested implementation commit.

**Dependencies:** EN-003, EN-004, PB-018, PB-021. **Remaining gap:** MLflow/DVC/Great Expectations/Grafana/GitOps/Terraform, fine-tuning/LoRA, GPU autoscaling, blue/green rollout, nightly validation/chaos and original GPU/CPU latency/accuracy targets are unvalidated proposals, not enabled services or paid-service permission. **Next action:** Select only justified tooling after real data/runtime needs are known; retain all cost/provider limits.
