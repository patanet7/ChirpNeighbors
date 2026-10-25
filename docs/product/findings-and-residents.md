# Findings and residents

Canonical requirements and acceptance for this topic. Stable IDs, decisions, dependencies and named evidence are retained from the [task index](../delivery/product-behavior-and-ideas.md). U: paths refer to the UI repository; M: paths refer to ChirpNeighbors. Evidence labels resolve through the [verification ledger](../delivery/verification-ledger.md). Current GitHub publication is tracked separately in the [release record](../archive/publication/20261011/README.md).

### PB-001 — Preserve source Findings with stable dedupe and append-only corrections.

**Source / decision:** user decision; Agreed. **Implementation:** Implemented. **Integration:** Local integrated checkpoint. **Release / production:** See [current release status](../archive/publication/20261011/README.md); historical local integration is not production validation.

**Architecture:** U:src/lib/domain/evidence.ts; U:src/lib/domain/yard.ts; U:src/lib/server/storage.

**Behavioral acceptance:** Exact import/form retries preserve one raw event; conflicting same-ID inputs roll back; corrections append without replacing source or resident pins; unknown, observed, uploaded and model intervals stay distinct.

**Tests and evidence:** [U:src/lib/server/storage/findings.test.ts](https://github.com/patanet7/birdsong-yard-sprites/blob/main/src/lib/server/storage/findings.test.ts); [U:src/lib/server/storage/repository.test.ts](https://github.com/patanet7/birdsong-yard-sprites/blob/main/src/lib/server/storage/repository.test.ts); [U:scripts/findings-browser-checks.py](https://github.com/patanet7/birdsong-yard-sprites/blob/main/scripts/findings-browser-checks.py). [E-CAT:findings/findings-browser-results.json](../archive/delivery/LOCAL-EVIDENCE.md); [E-CAT:ui-unit.log](../archive/delivery/LOCAL-EVIDENCE.md).

**Dependencies:** EN-001, PB-013. **Remaining gap:** Real source adapters are absent; a stored Finding is not model validation. **Next action:** Preserve dedupe and append-only correction assertions when adding EN-008 adapters.

### PB-002 — Recent eligible Findings create temporary species visitors; owners explicitly keep and name residents.

**Source / decision:** user decision; Agreed. **Implementation:** Implemented. **Integration:** Local integrated checkpoint. **Release / production:** See [current release status](../archive/publication/20261011/README.md); historical local integration is not production validation.

**Architecture:** U:src/lib/domain/yard.ts; U:src/lib/server/storage/repository.ts; U:src/lib/components/ResidentCard.svelte.

**Behavioral acceptance:** Unknown/future/historical evidence creates no recent visit; only new eligible evidence refreshes expiry; Keep/name is explicit and preserves decorative identity across reopen/reload.

**Tests and evidence:** [U:src/lib/server/storage/repository.test.ts](https://github.com/patanet7/birdsong-yard-sprites/blob/main/src/lib/server/storage/repository.test.ts); [U:scripts/consolidation-browser-checks.py](https://github.com/patanet7/birdsong-yard-sprites/blob/main/scripts/consolidation-browser-checks.py). [E-CAT:consolidation/consolidation-browser-results.json](../archive/delivery/LOCAL-EVIDENCE.md); [E-CAT:ui-unit.log](../archive/delivery/LOCAL-EVIDENCE.md).

**Dependencies:** PB-001, PB-013. **Remaining gap:** Keeping a decorative bird does not recognize an actual individual. **Next action:** Retain expiry/promotion invariants in future arrival adapters.

### PB-008 — Initial safe positions vary by session while persisted identities and yard layout stay stable.

**Source / decision:** user decision; Agreed. **Implementation:** Implemented. **Integration:** Local integrated placement and deterministic seed-matrix checkpoint (E-INT). **Release / production:** See [current release status](../archive/publication/20261011/README.md); historical local integration is not production validation.

**Architecture:** U:src/lib/engine/simulation.ts; U:src/lib/engine/behavior-contracts.ts; U:src/lib/components/YardScene.svelte.

**Behavioral acceptance:** Explicit uint32 seed reproduces positions; per-tab owner seed remains stable through rerender/navigation; changed seed can vary safe positions while persisted identity/layout stay unchanged; dense footprint-aware placements wait when no clear space exists.

**Tests and evidence:** [U:src/lib/engine/behavior.test.ts](https://github.com/patanet7/birdsong-yard-sprites/blob/main/src/lib/engine/behavior.test.ts); [U:src/lib/engine/behavior-policy.test.ts](https://github.com/patanet7/birdsong-yard-sprites/blob/main/src/lib/engine/behavior-policy.test.ts); [U:scripts/behavior-browser-checks.py](https://github.com/patanet7/birdsong-yard-sprites/blob/main/scripts/behavior-browser-checks.py); [U:scripts/ontology-browser-checks.py](https://github.com/patanet7/birdsong-yard-sprites/blob/main/scripts/ontology-browser-checks.py). [E-CAT:behavior/behavior-browser-results.json](../archive/delivery/LOCAL-EVIDENCE.md); [E-ONT:ontology-browser-results.json](../archive/delivery/LOCAL-EVIDENCE.md).

**Corrected integrated evidence:** [E-INT:ui-unit.log](../archive/delivery/LOCAL-EVIDENCE.md); [E-INT:behavior/behavior-browser-results.json](../archive/delivery/LOCAL-EVIDENCE.md); [E-INT:behavior/seed-matrix.json](../archive/delivery/LOCAL-EVIDENCE.md); [E-INT:ontology/ontology-browser-results.json](../archive/delivery/LOCAL-EVIDENCE.md).

**Representative exact current assertions:** `behavior-policy.test.ts`: “retains real variation across a fixed trait-enabled seed matrix and exactly replays every outcome”; `behavior-browser-checks.py`: “The complete fixed seed matrix produces actual transient placement variation”; `behavior-browser-checks.py`: “Every fixed seed reproduces its exact initial actor state on replay”; `behavior-browser-checks.py`: “Every seed and replay preserves the complete private yard and observation evidence”; `ontology-browser-checks.py`: “Every waiting resident carries a clearance explanation and no reserved target”.

**Dependencies:** PB-005, PB-007. **Remaining gap:** Dense waiting protects settled/reserved support footprints; in-flight silhouettes may overlap. This is not a continuous collision solver or a finished dense-yard design. **Next action:** Preserve complete-matrix variation and exact per-seed replay, including legal seed collisions, without changing persisted identities or personality.

**Current audit fix:** Asymmetric reviewed bodies now reserve clearance for either facing, including ground/world bounds and hop corridors. Eight new regressions pass in the focused 132-test engine run; full current-source integration is recorded separately in the [audit](../archive/delivery/product-audit-20261009.md). Conservative waiting preserves residents. E-RES supplies explicit actor/geometry/canvas admission bounds, and E-PERF adds bounded immutable geometry ownership with exact seeded waiting-state parity; continuous in-flight collision solving and worst-case smoothness remain open.

### PB-010 — A newly confirmed eligible sighting may receive one fly-in and an accessible banner; keeping remains optional.

**Source / decision:** user decision; Agreed. **Implementation:** Native manual arrival path implemented. **Integration:** Local integrated checkpoint. **Release / production:** See [current release status](../archive/publication/20261011/README.md); historical local integration is not production validation.

**Architecture:** U:src/lib/server/arrivals; U:src/lib/arrivals/controller.ts; U:src/lib/engine/simulation.ts.

**Behavioral acceptance:** Consume a durable trusted arrival receipt before one fly-in/banner; exact retry/reload/tab dedupe prevents replay; correction/restore/session loss cancels stale notices; reduced motion places directly; keep stays optional. Raw imports/technical model candidates cannot self-grant arrival authority.

**Tests and evidence:** [U:src/lib/server/arrivals/adapter-eligibility.test.ts](https://github.com/patanet7/birdsong-yard-sprites/blob/main/src/lib/server/arrivals/adapter-eligibility.test.ts); [U:src/lib/server/arrivals/integration.test.ts](https://github.com/patanet7/birdsong-yard-sprites/blob/main/src/lib/server/arrivals/integration.test.ts); [U:scripts/arrivals-browser-checks.py](https://github.com/patanet7/birdsong-yard-sprites/blob/main/scripts/arrivals-browser-checks.py). [E-CAT:arrivals/arrivals-browser-results.json](../archive/delivery/LOCAL-EVIDENCE.md).

**Dependencies:** PB-001, PB-002, PB-013. **Remaining gap:** Real authorized import/audio arrival adapters are unconfigured; tested admission does not mean real sightings were produced. **Next action:** Implement one EN-008 adapter only after reviewed source semantics.

### PB-012 — Private recording playback leads to analysis candidates, explicit confirmation and a saved Finding.

**Source / decision:** user decision; Agreed. **Implementation:** Private playback, candidates and explicit confirmation implemented. **Integration:** Local integrated technical checkpoint. **Release / production:** See [current release status](../archive/publication/20261011/README.md); historical local integration is not production validation.

**Architecture:** U:src/lib/server/recordings; U:src/lib/recordings; M:backend-inference/app/audio_pipeline.

**Behavioral acceptance:** Private bounded PCM recording upload/playback never autoplays; analysis retains exact model/input/time provenance; candidates require explicit human confirmation into a Finding; deleted/revoked media cannot revive through retry or restore; fixture scores stay labelled technical.

**Tests and evidence:** [U:src/lib/server/recordings/confirmation.test.ts](https://github.com/patanet7/birdsong-yard-sprites/blob/main/src/lib/server/recordings/confirmation.test.ts); [U:src/lib/server/recordings/lifecycle.test.ts](https://github.com/patanet7/birdsong-yard-sprites/blob/main/src/lib/server/recordings/lifecycle.test.ts); [U:scripts/evidence-browser-checks.py](https://github.com/patanet7/birdsong-yard-sprites/blob/main/scripts/evidence-browser-checks.py); [U:scripts/audio-lifecycle-browser-checks.py](https://github.com/patanet7/birdsong-yard-sprites/blob/main/scripts/audio-lifecycle-browser-checks.py); [M:backend-inference/tests/test_audio_pipeline.py](../../backend-inference/tests/test_audio_pipeline.py). [E-CAT:evidence/evidence-browser-results.json](../archive/delivery/LOCAL-EVIDENCE.md); [E-CAT:audio-lifecycle/results.json](../archive/delivery/LOCAL-EVIDENCE.md); [E-CAT:system-audio/system-audio-results.json](../archive/delivery/LOCAL-EVIDENCE.md).

**Dependencies:** PB-001, PB-013, EN-002, EN-004. **Remaining gap:** Real bird-model weights/calibration and durable autonomous Python execution are absent; saved manual Findings do not invent an unretained model backlink. **Next action:** Review real compatible model/dataset under EN-004; integrate original worker under EN-006.

**Current audit fix:** Upload cancellation keeps the exact idempotent retry receipt, distinguishes uncertain server completion, aborts on navigation and fences stale-owner responses. Focused client/browser evidence is 15/15 and 34/34; see the [journey audit](../archive/delivery/LOCAL-EVIDENCE.md).
