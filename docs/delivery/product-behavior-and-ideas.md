# Consolidated product, architecture and delivery task index

This is the **single authoritative task index** for current intent, decisions, implementation and remaining gaps across the two local repositories. It retains PB-001–PB-022 and adds EN-001–EN-012 for architecture, operational and external dependencies that were previously scattered. EN entries do not convert a historical proposal into user approval. Detailed [task tree](visual-task-tree-20261008.md), UI slice checklists, [delivery matrix](matrix.json) and retained reports remain supporting execution/evidence records, not competing completion authorities.

Paths prefixed **U:** belong to sibling `birdsong-yard-sprites`; **M:** belongs to `ChirpNeighbors`. Every requirement below records its decision, implementation, integration, architecture boundary, observable acceptance, named tests, exact evidence revision, dependencies, gap and next action. A missing test is written as missing; aggregate counts never establish a requirement by themselves.

## Status and evidence rules

- **Planned**: acceptance/design exists; required runtime implementation does not.
- **Implemented**: code exists; this alone does not establish tested behavior.
- **Locally verified**: named tests or browser assertions passed at a stated revision, within their explicit fixture/mock scope.
- **Local integrated checkpoint**: the bounded implementation and named evidence also appear in a complete frozen suite. This is still local, not merged/published/deployed.
- **Published** and **production validated** are separate states. **Every row below is unpublished by this local workstream and not production validated.** Existing published foundation bases are ancestry only; later local checkpoints are not publication evidence.
- **Blocked** states name the missing input or technical dependency, not an invented request for renewed permission. Legacy design alternatives remain proposals unless a later decision explicitly adopts them.

The last complete passing aggregate is E-CAT. Active ontology source is implemented and has E-ONT focused browser proof, and the first frozen aggregate finished **72/74**: `browser-scenes` failed on SVG fallback phase versus Pixi night; `browser-behavior` failed on a random-seed pairwise-diversity assertion. The ontology browser gate passed 38 checks in that run. There is **no active complete-pass claim** at this checkpoint. The integration owner must replace this paragraph only with the actual final report and exact source commits.

## Exact evidence ledger

| Code | Source revision(s), scope and retained evidence |
| --- | --- |
| E-CAT | main `ef67223f52448dcdbf2bef05283146a01bceda06`; ui `db931a2beb8e62dc012a981d478e27749062fd4a`. Complete local integrated 73-gate checkpoint; applicability only to named assertions and bounded scope. [docs/delivery/catalog-verified-20261009](../../docs/delivery/catalog-verified-20261009) |
| E-ONT | ui `31585edfbb0de7fa1f04fd036a84a54428a52284`; main `Not a main-code aggregate`. Dedicated 38-check browser gate only; not full active integration. [docs/delivery/ontology-attempts-20261009/browser-r3](LOCAL-EVIDENCE.md) |
| E-FOCUS | ui `Per-log focused working-tree runs; not a substitute frozen commit`; main `Per-log focused runs`. Focused contract/engine evidence; exact frozen integration pending. [docs/delivery/ontology-attempts-20261009/focused](LOCAL-EVIDENCE.md) |
| E-HANDOFF | No passing source execution claim. Retained transport-failure record, not execution evidence. [docs/delivery/approved-handoff-blocker-20261008.md](../../docs/delivery/approved-handoff-blocker-20261008.md) |
| E-PUBLICATION | No passing source execution claim. Historical foundation record only. Current stalled/excluded status comes from explicit 2026-10-09 user delegation; precise cause not available. [docs/agents/20261007_183500_publication-checks.md](../../docs/agents/20261007_183500_publication-checks.md) |

Preserved complete checkpoint commits are main `a3c5ec6d03d405dd11724cbe14356e1d99b5ea37` / UI `b7e1ddb6f38429fa88dedcf659f45b3eb5e4aa95`; these retain E-CAT and are distinct from its tested source commits. The first active frozen candidate is main `5420c2e32a97536fc5d848f96cbd0ae49b9ed4bc` / UI `3938a260c5190ec488f637c9210f7cb37be46225`. Its attempt is not a passing checkpoint.

## Coverage summary

There are **34 stable entries: 22 product decisions/ideas and 12 architecture/dependency entries**. Of the original product entries, 20 are user decisions, PB-017 is a tentative user idea and PB-019 is an assistant proposal. Under the former broad register labels, 16 bounded product slices had complete historical local verification; PB-005 is implemented with dedicated browser proof awaiting full integration; PB-018 has tested pure helpers only; PB-006/PB-021 remain unimplemented at the product-outcome level; PB-016 has tested disabled helpers but unresolved operating integration; PB-017 remains unselected. These are overlapping evidence scopes, not a percentage of product readiness.

## Product requirements and ideas

### PB-001 — Preserve source Findings with stable dedupe and append-only corrections.

**Source / decision:** user decision; Agreed. **Implementation:** Implemented. **Integration:** Local integrated checkpoint. **Publication / production:** unpublished in this workstream / not validated.

**Architecture:** U:src/lib/domain/evidence.ts; U:src/lib/domain/yard.ts; U:src/lib/server/storage.

**Behavioral acceptance:** Exact import/form retries preserve one raw event; conflicting same-ID inputs roll back; corrections append without replacing source or resident pins; unknown, observed, uploaded and model intervals stay distinct.

**Tests and evidence:** [U:src/lib/server/storage/findings.test.ts](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/src/lib/server/storage/findings.test.ts); [U:src/lib/server/storage/repository.test.ts](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/src/lib/server/storage/repository.test.ts); [U:scripts/findings-browser-checks.py](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/scripts/findings-browser-checks.py). [E-CAT:findings/findings-browser-results.json](LOCAL-EVIDENCE.md); [E-CAT:ui-unit.log](LOCAL-EVIDENCE.md).

**Dependencies:** EN-001, PB-013. **Remaining gap:** Real source adapters are absent; a stored Finding is not model validation. **Next action:** Preserve dedupe and append-only correction assertions when adding EN-008 adapters.

### PB-002 — Recent eligible Findings create temporary species visitors; owners explicitly keep and name residents.

**Source / decision:** user decision; Agreed. **Implementation:** Implemented. **Integration:** Local integrated checkpoint. **Publication / production:** unpublished in this workstream / not validated.

**Architecture:** U:src/lib/domain/yard.ts; U:src/lib/server/storage/repository.ts; U:src/lib/components/ResidentCard.svelte.

**Behavioral acceptance:** Unknown/future/historical evidence creates no recent visit; only new eligible evidence refreshes expiry; Keep/name is explicit and preserves decorative identity across reopen/reload.

**Tests and evidence:** [U:src/lib/server/storage/repository.test.ts](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/src/lib/server/storage/repository.test.ts); [U:scripts/consolidation-browser-checks.py](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/scripts/consolidation-browser-checks.py). [E-CAT:consolidation/consolidation-browser-results.json](LOCAL-EVIDENCE.md); [E-CAT:ui-unit.log](LOCAL-EVIDENCE.md).

**Dependencies:** PB-001, PB-013. **Remaining gap:** Keeping a decorative bird does not recognize an actual individual. **Next action:** Retain expiry/promotion invariants in future arrival adapters.

### PB-003 — Shared canonical species/style/version assets are built lazily as species arrive; optional later variants may be added as needed.

**Source / decision:** user decision; Agreed. **Implementation:** Bounded fixture catalog implemented. **Integration:** Local integrated checkpoint. **Publication / production:** unpublished in this workstream / not validated.

**Architecture:** U:src/lib/server/assets/catalog-requests.ts; U:src/lib/server/assets/catalog-releases.ts; U:src/lib/server/assets/catalog-selection.ts; U:src/lib/server/runtime.ts.

**Behavioral acceptance:** Two owners requesting the same supported arriving species dedupe one owner-free canonical identity; immutable explicit releases and per-resident exact pins survive version publication, revocation, missing bytes and restart; private inputs never enter shared catalog records.

**Tests and evidence:** [U:src/lib/server/assets/catalog-releases.test.ts](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/src/lib/server/assets/catalog-releases.test.ts); [U:src/lib/server/assets/catalog-selection.test.ts](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/src/lib/server/assets/catalog-selection.test.ts); [U:scripts/shared-catalog-browser-checks.py](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/scripts/shared-catalog-browser-checks.py). [E-CAT:shared-catalog/shared-catalog-browser-results.json](LOCAL-EVIDENCE.md); [E-CAT:ui-unit.log](LOCAL-EVIDENCE.md).

**Representative exact assertions:** catalog-selection.test.ts: “shares one approved render between two named residents without copying private sources or observations”; catalog-selection.test.ts: “keeps publication disabled on the authenticated selection service even in local mode”; E-CAT browser result: “Publishing fixture version two leaves both residents pinned to version one”.

**Dependencies:** PB-001, PB-013, PB-014, EN-001. **Remaining gap:** Production promotion authority, approved rights/art and provider execution are unavailable; optional variants are contract identities without enabled authoring. **Next action:** Keep default-deny production promotion; obtain PB-021 inputs before enabling real releases.

### PB-004 — Autonomous idle, move, hop, fly, perch, sing, feed, bathe, sleep, play and nest-building routines.

**Source / decision:** user decision; Agreed. **Implementation:** Fixture engine implemented; ontology extension implemented. **Integration:** Historical local integration; active extension pending. **Publication / production:** unpublished in this workstream / not validated.

**Architecture:** U:src/lib/engine/simulation.ts; U:src/lib/engine/behavior-policy.ts; U:src/lib/assets/manifest.ts; U:src/lib/engine/renderer.ts; U:src/lib/components/YardScene.svelte.

**Behavioral acceptance:** Actual actors travel and enter allowed idle/move/perch/sing/feed/bath/sleep/play/nest states; hop/flight selection obeys route safety; routines reserve supported slots, terminate and yield fairly. Requested action and sampled clip differ explicitly when authored clips are absent; removed objects and no-space states preserve safe settled/reserved ground footprints and explicit waiting. In-flight silhouettes may cross; this is not a continuous multi-agent collision solver.

**Tests and evidence:** [U:src/lib/engine/routines.test.ts](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/src/lib/engine/routines.test.ts); [U:src/lib/engine/behavior-policy.test.ts](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/src/lib/engine/behavior-policy.test.ts); [U:src/lib/engine/behavior-diagnostics.test.ts](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/src/lib/engine/behavior-diagnostics.test.ts); [U:scripts/routines-browser-checks.py](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/scripts/routines-browser-checks.py); [U:scripts/ontology-browser-checks.py](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/scripts/ontology-browser-checks.py). [E-CAT:routines/routines-browser-results.json](LOCAL-EVIDENCE.md); [E-CAT:sleep/sleep-browser-results.json](LOCAL-EVIDENCE.md); [E-ONT:ontology-browser-results.json](LOCAL-EVIDENCE.md).

**Dependencies:** PB-005, PB-007, PB-014. **Remaining gap:** Current sleep/play/nest frames fall back to still idle; authored species clips and biological motion remain unreviewed. Active full aggregate is not yet passing. **Next action:** Resolve current scene-phase regression, freeze, and pass the entire active suite; then review real clips under PB-021.

### PB-005 — Species-level illustrative tuning and fictional individual personality are different concepts.

**Source / decision:** user decision; Agreed. **Implementation:** Bounded versioned traits/personality/workbench implemented. **Integration:** Focused and browser verified; full integration pending. **Publication / production:** unpublished in this workstream / not validated.

**Architecture:** U:src/lib/engine/ontology-contracts.ts; U:src/lib/engine/behavior-profiles.ts; U:src/lib/engine/behavior-policy.ts; U:src/lib/engine/simulation.ts; U:src/lib/components/BehaviorWorkbench.svelte.

**Behavioral acceptance:** Authored unvalidated species traits stay separate from deterministic fictional curiosity/sociability/boldness derived only from decorative ID. Same resident changes ground/perch placement under transient presets; disabled bathing/routines become ineligible; spacing/caution and locomotion change actual choices. Workbench shows candidate rejection, chosen support, transition, requested/rendered clip and visual override without saving observations or experiments.

**Tests and evidence:** [U:src/lib/engine/ontology-contracts.test.ts](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/src/lib/engine/ontology-contracts.test.ts); [U:src/lib/engine/behavior-policy.test.ts](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/src/lib/engine/behavior-policy.test.ts); [U:src/lib/engine/behavior-diagnostics.test.ts](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/src/lib/engine/behavior-diagnostics.test.ts); [U:scripts/ontology-browser-checks.py](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/scripts/ontology-browser-checks.py). [E-ONT:ontology-browser-results.json](LOCAL-EVIDENCE.md); [E-FOCUS](LOCAL-EVIDENCE.md).

**Dependencies:** PB-004, PB-007, PB-014, EN-001. **Remaining gap:** Three known illustrative profiles only (European Robin, House Sparrow and Blue Jay); unknown species retain legacy behavior. No validated biology, observed-individual inference, editable/persisted personality or progression migration. **Next action:** Complete frozen active integration, then decide persistent/editable personality separately from PB-006.

### PB-006 — Earned companionship and levels should support attachment without pressure.

**Source / decision:** user decision; Agreed. **Implementation:** Planned. **Integration:** Not integrated. **Publication / production:** unpublished in this workstream / not validated.

**Architecture:** U:src/lib/domain/yard.ts future progression boundary; no progression storage/API.

**Behavioral acceptance:** Before implementation define earning events, bounded rewards, migrations and accessible equivalent interactions; enforce no missed-day punishment, starvation, guilt, paid affection or lost birds.

**Tests and evidence:** No executable acceptance test for this requested outcome. No passing outcome evidence or tested implementation commit.

**Dependencies:** PB-002, PB-005, EN-001. **Remaining gap:** No executable progression acceptance tests, rates, levels, reward rules or storage exist. **Next action:** Specify a bounded progression contract and behavioral tests before implementation.

### PB-007 — Free per-owner object inventory separates owned stock from placed perch, feeder, bath and nest instances.

**Source / decision:** user decision; Agreed. **Implementation:** Implemented. **Integration:** Local integrated checkpoint. **Publication / production:** unpublished in this workstream / not validated.

**Architecture:** U:src/lib/domain/object-inventory.ts; U:src/lib/server/storage/repository.ts; U:src/lib/arrangement.

**Behavioral acceptance:** Free owner stock differs from placed instances; place/return/move are transactional, owner-bound and exact-retry idempotent; quantities cannot become negative; legacy migration, lost-response retry, keyboard/pointer/mobile, restart/restore and occupancy preserve identity.

**Tests and evidence:** [U:src/lib/server/storage/object-inventory.test.ts](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/src/lib/server/storage/object-inventory.test.ts); [U:src/lib/client/save-inventory.test.ts](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/src/lib/client/save-inventory.test.ts); [U:scripts/inventory-browser-checks.py](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/scripts/inventory-browser-checks.py); [U:scripts/arrangement-browser-checks.py](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/scripts/arrangement-browser-checks.py). [E-CAT:inventory/inventory-browser-results.json](LOCAL-EVIDENCE.md); [E-CAT:arrangement/arrangement-browser-results.json](LOCAL-EVIDENCE.md).

**Dependencies:** EN-001, PB-013. **Remaining gap:** No currency, purchases or stock economy; new ontology density behavior separately pending full verification. **Next action:** Preserve capabilities and inventory CAS when adding authored objects.

### PB-008 — Initial safe positions vary by session while persisted identities and yard layout stay stable.

**Source / decision:** user decision; Agreed. **Implementation:** Implemented. **Integration:** Local integrated checkpoint; placement extension pending. **Publication / production:** unpublished in this workstream / not validated.

**Architecture:** U:src/lib/engine/simulation.ts; U:src/lib/engine/behavior-contracts.ts; U:src/lib/components/YardScene.svelte.

**Behavioral acceptance:** Explicit uint32 seed reproduces positions; per-tab owner seed remains stable through rerender/navigation; changed seed can vary safe positions while persisted identity/layout stay unchanged; dense footprint-aware placements wait when no clear space exists.

**Tests and evidence:** [U:src/lib/engine/behavior.test.ts](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/src/lib/engine/behavior.test.ts); [U:src/lib/engine/behavior-policy.test.ts](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/src/lib/engine/behavior-policy.test.ts); [U:scripts/behavior-browser-checks.py](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/scripts/behavior-browser-checks.py); [U:scripts/ontology-browser-checks.py](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/scripts/ontology-browser-checks.py). [E-CAT:behavior/behavior-browser-results.json](LOCAL-EVIDENCE.md); [E-ONT:ontology-browser-results.json](LOCAL-EVIDENCE.md).

**Dependencies:** PB-005, PB-007. **Remaining gap:** Dense waiting protects settled/reserved support footprints; in-flight silhouettes may overlap. This is not a continuous collision solver or a finished dense-yard design. **Next action:** Finish active aggregate and preserve deterministic seed/personality separation.

### PB-009 — A decorative nonviolent predator/hawk visit can approach, scatter birds, return them and enter cooldown.

**Source / decision:** user decision; Agreed. **Implementation:** Implemented. **Integration:** Local integrated checkpoint; trait response extension pending. **Publication / production:** unpublished in this workstream / not validated.

**Architecture:** U:src/lib/engine/simulation.ts; U:src/lib/engine/behavior-policy.ts; U:src/lib/engine/renderer.ts.

**Behavioral acceptance:** Coalesced decorative predator trigger approaches/scatters/returns/cools down with bounded timing; caution and fictional boldness affect response delay; hidden/reduced-motion/object-removal cancellation clears reservations and never writes evidence or deletes birds.

**Tests and evidence:** [U:src/lib/engine/visits.test.ts](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/src/lib/engine/visits.test.ts); [U:src/lib/engine/behavior-policy.test.ts](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/src/lib/engine/behavior-policy.test.ts); [U:scripts/behavior-browser-checks.py](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/scripts/behavior-browser-checks.py); [U:scripts/ontology-browser-checks.py](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/scripts/ontology-browser-checks.py). [E-CAT:behavior/behavior-browser-results.json](LOCAL-EVIDENCE.md); [E-ONT:ontology-browser-results.json](LOCAL-EVIDENCE.md).

**Dependencies:** PB-005, PB-008. **Remaining gap:** Generic labelled fixture visitor, no approved hawk art or biological predator-response claim. **Next action:** Complete active aggregate; preserve nonviolent finite cancellation and no persistence.

### PB-010 — A newly confirmed eligible sighting may receive one fly-in and an accessible banner; keeping remains optional.

**Source / decision:** user decision; Agreed. **Implementation:** Native manual arrival path implemented. **Integration:** Local integrated checkpoint. **Publication / production:** unpublished in this workstream / not validated.

**Architecture:** U:src/lib/server/arrivals; U:src/lib/arrivals/controller.ts; U:src/lib/engine/simulation.ts.

**Behavioral acceptance:** Consume a durable trusted arrival receipt before one fly-in/banner; exact retry/reload/tab dedupe prevents replay; correction/restore/session loss cancels stale notices; reduced motion places directly; keep stays optional. Raw imports/technical model candidates cannot self-grant arrival authority.

**Tests and evidence:** [U:src/lib/server/arrivals/adapter-eligibility.test.ts](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/src/lib/server/arrivals/adapter-eligibility.test.ts); [U:src/lib/server/arrivals/integration.test.ts](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/src/lib/server/arrivals/integration.test.ts); [U:scripts/arrivals-browser-checks.py](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/scripts/arrivals-browser-checks.py). [E-CAT:arrivals/arrivals-browser-results.json](LOCAL-EVIDENCE.md).

**Dependencies:** PB-001, PB-002, PB-013. **Remaining gap:** Real authorized import/audio arrival adapters are unconfigured; tested admission does not mean real sightings were produced. **Next action:** Implement one EN-008 adapter only after reviewed source semantics.

### PB-011 — Visually simple regional yards use separate ground, objects, birds and foreground layers, weather and time.

**Source / decision:** user decision; Agreed. **Implementation:** Layered fixture scenes implemented. **Integration:** Historical local integration; active scene regression open. **Publication / production:** unpublished in this workstream / not validated.

**Architecture:** U:src/lib/scenes; U:src/lib/engine/scenes.ts; U:src/lib/domain/scene.ts; U:src/lib/components/YardScene.svelte; U:src/lib/server/weather.

**Behavioral acceptance:** Preserve separate background/ground/object/bird/foreground/weather layers; palette and phase controls change rendering, object capability edits preserve safe actors; Pixi and SVG agree on layer/depth/support semantics; region/location remains private.

**Tests and evidence:** [U:src/lib/engine/layers.test.ts](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/src/lib/engine/layers.test.ts); [U:src/lib/scenes/manifest.test.ts](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/src/lib/scenes/manifest.test.ts); [U:scripts/scenes-browser-checks.py](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/scripts/scenes-browser-checks.py); [U:scripts/layered-browser-checks.py](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/scripts/layered-browser-checks.py); [U:scripts/ontology-browser-checks.py](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/scripts/ontology-browser-checks.py). [E-CAT:scenes/scenes-browser-results.json](LOCAL-EVIDENCE.md); [E-CAT:layered/layered-browser-results.json](LOCAL-EVIDENCE.md); [E-ONT:ontology-browser-results.json](LOCAL-EVIDENCE.md).

**Dependencies:** PB-007, PB-013, EN-009. **Remaining gap:** Active first aggregate detected fallback phase mismatch; prior passing scene proof does not verify current HEAD. Regional scenes and weather remain simulated fixtures. **Next action:** Fix and reverify SVG/Pixi phase parity; configure real weather only under EN-009.

### PB-012 — Private recording playback leads to analysis candidates, explicit confirmation and a saved Finding.

**Source / decision:** user decision; Agreed. **Implementation:** Private playback, candidates and explicit confirmation implemented. **Integration:** Local integrated technical checkpoint. **Publication / production:** unpublished in this workstream / not validated.

**Architecture:** U:src/lib/server/recordings; U:src/lib/recordings; M:backend-inference/app/audio_pipeline.

**Behavioral acceptance:** Private bounded PCM recording upload/playback never autoplays; analysis retains exact model/input/time provenance; candidates require explicit human confirmation into a Finding; deleted/revoked media cannot revive through retry or restore; fixture scores stay labelled technical.

**Tests and evidence:** [U:src/lib/server/recordings/confirmation.test.ts](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/src/lib/server/recordings/confirmation.test.ts); [U:src/lib/server/recordings/lifecycle.test.ts](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/src/lib/server/recordings/lifecycle.test.ts); [U:scripts/evidence-browser-checks.py](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/scripts/evidence-browser-checks.py); [U:scripts/audio-lifecycle-browser-checks.py](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/scripts/audio-lifecycle-browser-checks.py); [M:backend-inference/tests/test_audio_pipeline.py](../../backend-inference/tests/test_audio_pipeline.py). [E-CAT:evidence/evidence-browser-results.json](LOCAL-EVIDENCE.md); [E-CAT:audio-lifecycle/results.json](LOCAL-EVIDENCE.md); [E-CAT:system-audio/system-audio-results.json](LOCAL-EVIDENCE.md).

**Dependencies:** PB-001, PB-013, EN-002, EN-004. **Remaining gap:** Real bird-model weights/calibration and durable autonomous Python execution are absent; saved manual Findings do not invent an unretained model backlink. **Next action:** Review real compatible model/dataset under EN-004; integrate original worker under EN-006.

### PB-013 — Private accounts, media and owner data are the default; optional shares are safe view-only projections.

**Source / decision:** user decision; Agreed. **Implementation:** Private defaults and opt-in projection implemented. **Integration:** Local integrated checkpoint. **Publication / production:** unpublished in this workstream / not validated.

**Architecture:** U:src/lib/server/auth/session-binding.ts; U:src/lib/server/sharing; U:src/lib/sharing/display.ts; U:src/lib/server/storage.

**Behavioral acceptance:** Cookie/session authority defeats owner-ID spoofing and old-tab account replacement; shared capability is opt-in, frozen, view-only and revoke/expiry/restore-fenced. Projection omits names/location/Findings/recordings/private pins; shared renderer uses builtin safe fixtures and no owner ontology workbench.

**Tests and evidence:** [U:src/lib/server/auth/session-binding.test.ts](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/src/lib/server/auth/session-binding.test.ts); [U:src/lib/server/sharing/sharing.test.ts](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/src/lib/server/sharing/sharing.test.ts); [U:src/lib/server/sharing/egress.test.ts](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/src/lib/server/sharing/egress.test.ts); [U:scripts/session-binding-browser-checks.py](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/scripts/session-binding-browser-checks.py); [U:scripts/share-browser-checks.py](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/scripts/share-browser-checks.py). [E-CAT:session-binding/session-binding-browser-results.json](LOCAL-EVIDENCE.md); [E-CAT:sharing/share-browser-results.json](LOCAL-EVIDENCE.md); [E-ONT:ontology-browser-results.json](LOCAL-EVIDENCE.md).

**Representative exact assertions:** sharing.test.ts: “invalidates every capability in an older backup without changing owner yard data”; E-CAT browser result: “public view performs no API or private image requests”; E-CAT catalog browser result: “Shared view still excludes private resident names, observations, local source job and location”.

**Dependencies:** EN-001, EN-002. **Remaining gap:** Production provider/account policies and account-wide erasure remain external; shared views do not show private reviewed artwork or live owner ontology. **Next action:** Preserve narrow share projection and use EN-011 for erasure scope.

### PB-014 — Reviewed source rights, provenance and immutable shape/animation workbench precede reusable artwork.

**Source / decision:** user decision; Agreed. **Implementation:** Reviewed manifest/shape pipeline implemented. **Integration:** Local integrated fixture checkpoint. **Publication / production:** unpublished in this workstream / not validated.

**Architecture:** U:src/lib/assets; U:src/lib/server/asset-pipeline; U:src/lib/server/assets/resolve.ts.

**Behavioral acceptance:** Validate exact species/source/pin/pose provenance, frame bounds/durations and clip fallback; inspect every frame including unused ones; approval never implicitly pins; immutable geometry revisions preserve pixels and invalidate caches by owner/version/review; missing/corrupt dependencies retain identity and explicit fallback.

**Tests and evidence:** [U:src/lib/assets/manifest.test.ts](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/src/lib/assets/manifest.test.ts); [U:src/lib/assets/manifest-v3.test.ts](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/src/lib/assets/manifest-v3.test.ts); [U:src/lib/assets/pose-geometry.test.ts](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/src/lib/assets/pose-geometry.test.ts); [U:src/lib/server/asset-pipeline/revise-shape.test.ts](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/src/lib/server/asset-pipeline/revise-shape.test.ts); [U:scripts/manifest-browser-checks.py](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/scripts/manifest-browser-checks.py); [U:scripts/shape-browser-checks.py](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/scripts/shape-browser-checks.py). [E-CAT:manifests/manifest-browser-results.json](LOCAL-EVIDENCE.md); [E-CAT:shapes/shape-browser-results.json](LOCAL-EVIDENCE.md); [E-CAT:image-v3/image-v3-browser-results.json](LOCAL-EVIDENCE.md).

**Dependencies:** EN-001, PB-013, PB-020. **Remaining gap:** V2 compatibility is backward reading, not universal old-client acceptance of V3. Approved concept pixels, real generation/segmentation, species fidelity and general reference-photo adapters unavailable. **Next action:** Acquire reviewed inputs under PB-021; do not certify fidelity from fixture mechanics.

### PB-015 — First-party analytics answer coarse product-use questions only after explicit consent.

**Source / decision:** user decision; Agreed. **Implementation:** Default-off consented analytics foundation implemented. **Integration:** Local integrated checkpoint; operational activation absent. **Publication / production:** unpublished in this workstream / not validated.

**Architecture:** U:src/lib/analytics; U:src/lib/server/analytics; U:src/lib/server/auth/session-binding.ts.

**Behavioral acceptance:** No collection without explicit current consent; closed coarse events omit identity/species/evidence/media/location/URLs/IP/referrer/free text; separate stores, bounded admission, revoke/regrant fences and purge/retention fail safely; collector failure never blocks yard/login.

**Tests and evidence:** [U:src/lib/server/analytics/analytics.test.ts](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/src/lib/server/analytics/analytics.test.ts); [U:src/lib/analytics/client.test.ts](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/src/lib/analytics/client.test.ts); [U:scripts/analytics-browser-checks.py](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/scripts/analytics-browser-checks.py). [E-CAT:analytics/results.json](LOCAL-EVIDENCE.md); [E-CAT:ui-unit.log](LOCAL-EVIDENCE.md).

**Dependencies:** PB-013, EN-001. **Remaining gap:** No real-user activation, external collector, unique-user retention claim or legal-compliance claim. Final policy/retention/operator review and real web-vitals dependency remain open. **Next action:** Review operating policy and retention before any activation; keep default off.

### PB-016 — Minimal restricted security audit is separate from optional product analytics.

**Source / decision:** user decision; Agreed. **Implementation:** Disabled fixed-code helper and tests implemented. **Integration:** Helper verified; operational hooks/policy not integrated. **Publication / production:** unpublished in this workstream / not validated.

**Architecture:** U:src/lib/server/analytics/security-audit.ts; U:src/lib/server/analytics/maintenance.ts.

**Behavioral acceptance:** Security purpose remains separate from consented product analytics; fixed-code records exclude raw identity/evidence/request payloads and are disabled by default; independent retention/maintenance cannot imply consent.

**Tests and evidence:** [U:src/lib/server/analytics/analytics.test.ts](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/src/lib/server/analytics/analytics.test.ts). [E-CAT:ui-unit.log](LOCAL-EVIDENCE.md).

**Dependencies:** PB-013, PB-015. **Remaining gap:** No selected operational hook set or approved retention/access policy. Helper tests do not demonstrate deployed security monitoring. **Next action:** Specify reviewed events/operator policy before enabling concrete hooks.

### PB-017 — Sustainability may include voluntary support, paid/premium themes, daily credits, small ads or monetized customization.

**Source / decision:** tentative user idea; Tentative; no option selected. **Implementation:** Not implemented. **Integration:** Not integrated. **Publication / production:** unpublished in this workstream / not validated.

**Architecture:** Future product/economic boundary; no billing/ad/currency routes.

**Behavioral acceptance:** If selected later, assess costs, accessibility, control and privacy before technical design; no credits, currency, ads, billing or paid affection is authorized by this idea.

**Tests and evidence:** No executable acceptance test for this requested outcome. No passing outcome evidence or tested implementation commit.

**Dependencies:** PB-006, PB-015, PB-018. **Remaining gap:** Voluntary support, premium themes, daily credits, small ads and monetized customization are unselected ideas, not approved implementation. **Next action:** Obtain a product decision before selecting any economic mechanism.

### PB-018 — Track generation resource usage and unknown costs accurately.

**Source / decision:** user decision; Agreed. **Implementation:** Contracts and pure helpers implemented. **Integration:** Helper tests verified; runtime dispatch accounting absent. **Publication / production:** unpublished in this workstream / not validated.

**Architecture:** U:src/lib/pipeline/generation-usage.ts; U:src/lib/server/pipeline/generation-usage.ts.

**Behavioral acceptance:** Synthetic usage summaries separate adapter attempts, elapsed duration, cache/admission/review and unknown costs; reject overflow and spoofed provenance; shared/private fingerprints keep owner scope distinct. Future dispatch must durably record actual attempts and settle budgets/cancellation/retries.

**Tests and evidence:** [U:src/lib/server/pipeline/generation-usage.test.ts](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/src/lib/server/pipeline/generation-usage.test.ts). [E-CAT:ui-unit.log](LOCAL-EVIDENCE.md).

**Representative exact assertions:** generation-usage.test.ts: “defaults monetary costs to unknown, including local fixture compute”; generation-usage.test.ts: “does not count blocked stages, cache hits, admission or review as dispatches”.

**Dependencies:** PB-003, PB-013, PB-014, EN-006. **Remaining gap:** No runtime caller of summarizeGenerationUsage/privateGenerationFingerprint/sharedGenerationFingerprint; no durable usage ledger, live metering, budget enforcement or actual provider dispatch. Stage claims are not provider calls. **Next action:** Implement durable accounting alongside a separately authorized real execution adapter; retain unknown monetary cost.

### PB-019 — Protect progress against restored consent and presentation rollback.

**Source / decision:** assistant proposal; Assistant proposal implemented locally; not recorded as new user decision. **Implementation:** Implemented. **Integration:** Local integrated checkpoint. **Publication / production:** unpublished in this workstream / not validated.

**Architecture:** U:src/lib/server/operations/restore-optional-state.test.ts; U:scripts/private_backup.py; U:src/lib/server/analytics/recovery.ts.

**Behavioral acceptance:** Restore to a new directory cancels copied pending arrival notices, revokes copied analytics consent and discards optional aggregates while preserving original backup/evidence; cover stores with and without deletion ledger.

**Tests and evidence:** [U:src/lib/server/operations/restore-optional-state.test.ts](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/src/lib/server/operations/restore-optional-state.test.ts); [U:scripts/tests/test_private_backup.py](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/scripts/tests/test_private_backup.py). [E-CAT:ui-unit.log](LOCAL-EVIDENCE.md); [E-CAT:private-recovery-tests.log](LOCAL-EVIDENCE.md).

**Dependencies:** PB-010, PB-015, EN-003. **Remaining gap:** Does not erase offline copies or guarantee the supplied deletion ledger is newest. **Next action:** Retain explicit offline-copy/operator limits under EN-011.

### PB-020 — Owner-supplied local PNG bytes become reusable animation candidates through separate file, source and manifest reviews, then an explicit resident pin.

**Source / decision:** user decision; Agreed. **Implementation:** Bounded local PNG intake implemented. **Integration:** Local integrated fixture checkpoint. **Publication / production:** unpublished in this workstream / not validated.

**Architecture:** U:src/lib/server/image-files; U:src/lib/server/asset-pipeline; U:src/lib/assets.

**Behavioral acceptance:** Real private PNG bytes pass maintained bounded decoder, dimensions/inflate/grid limits, metadata stripping and hidden-RGB removal; separate per-file rights/source/manifest reviews precede explicit immutable resident pin; owner switch/retry/restart/backup/corruption and Pixi/SVG paths pass.

**Tests and evidence:** [U:src/lib/server/image-files/decode.test.ts](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/src/lib/server/image-files/decode.test.ts); [U:src/lib/server/image-files/service.test.ts](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/src/lib/server/image-files/service.test.ts); [U:scripts/png-intake-browser-checks.py](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/scripts/png-intake-browser-checks.py). [E-CAT:png-intake/png-intake-browser-results.json](LOCAL-EVIDENCE.md); [E-CAT:ui-unit.log](LOCAL-EVIDENCE.md).

**Dependencies:** PB-013, PB-014. **Remaining gap:** Upload alone grants no reuse/derivative rights. Existing pixels are fixtures; general photos/real generation and account erasure absent. **Next action:** Use reviewed actual-species inputs only after PB-021 dependencies; preserve per-file rights gates.

### PB-021 — Actual-species reference photos should guide highly detailed species-correct reusable sprites and animations, paired with visually simple regional yards.

**Source / decision:** user decision; Agreed. **Implementation:** Contracts/fixture mechanics only; production artwork absent. **Integration:** Real-art workflow not integrated. **Publication / production:** unpublished in this workstream / not validated.

**Architecture:** U:src/lib/server/asset-pipeline/image-stage.ts; U:src/lib/assets; P1–P4 in visual task tree.

**Behavioral acceptance:** Authorized actual-species references and per-file rights bind each master/frame/action; reviewer verifies anatomy, plumage, silhouette, contacts and temporal consistency against available approved references before shared reusable release; simple regional scenery remains separate.

**Tests and evidence:** [U:src/lib/server/asset-pipeline/image-stage.test.ts](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/src/lib/server/asset-pipeline/image-stage.test.ts); [U:src/lib/server/asset-pipeline/pipeline-v2.test.ts](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/src/lib/server/asset-pipeline/pipeline-v2.test.ts). [E-CAT:ui-unit.log](LOCAL-EVIDENCE.md).

**Dependencies:** PB-003, PB-004, PB-011, PB-014, PB-020. **Remaining gap:** Tests cover fixture contracts/normalization only, not this artwork acceptance. Approved reference/concept pixels were unavailable and not viewed; real adapters, biological review, model/licensing and reviewed art remain absent. **Next action:** Obtain authorized inputs and named fidelity review before real frame production; do not create replacement art in this task.

### PB-022 — Owners can reversibly archive private uploads/packages and unpin or restore resident artwork, with explicit retention reasons.

**Source / decision:** user decision; Agreed. **Implementation:** Reversible lifecycle implemented. **Integration:** Local integrated checkpoint. **Publication / production:** unpublished in this workstream / not validated.

**Architecture:** U:src/lib/server/assets/lifecycle.ts; U:src/lib/server/assets/lifecycle-storage.ts; U:src/lib/server/assets/resolve.ts.

**Behavioral acceptance:** Archive retains bytes/existing pins but fences all new selections/derivations including restore/automatic assignment; unpin/undo uses revision/pin CAS and durable receipts; incomplete reference graph fails closed; owner/session races, interruption and cold recovery preserve evidence.

**Tests and evidence:** [U:src/lib/server/assets/lifecycle.test.ts](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/src/lib/server/assets/lifecycle.test.ts); [U:scripts/asset-retention-browser-checks.py](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/scripts/asset-retention-browser-checks.py). [E-CAT:asset-retention/asset-retention-browser-results.json](LOCAL-EVIDENCE.md); [E-CAT:ui-unit.log](LOCAL-EVIDENCE.md).

**Dependencies:** PB-013, PB-014, PB-020. **Remaining gap:** No live purge, expiry job, account-wide erasure or authorization to destroy retained evidence; shared catalog read-only. **Next action:** Specify retention/erasure separately under EN-011; preserve archive semantics.

## Architecture, operations and external dependencies

### EN-001 — Single contract authority, generated consumers and strict compatibility gates

**Source / decision:** Architecture/delivery record; not new user authorization; Established architecture constraint. **Implementation:** Implemented. **Integration:** Local integrated checkpoint; four ontology additions pending full integration. **Publication / production:** unpublished in this workstream / not validated.

**Architecture:** U:contracts/authority-inventory-v1.json; U:scripts/contract-tools; M:contracts; M:scripts/verify_system.py.

**Behavioral acceptance:** One Zod/Pydantic authority per actual boundary; deterministic exports/types and independent semantic admission; bidirectional golden/property tests reject drift; explicitly version changed reader behavior and inventory each HTTP/SSR/store/config boundary.

**Tests and evidence:** [U:scripts/contract-tools/boundary-inventory.test.mjs](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/scripts/contract-tools/boundary-inventory.test.mjs); [U:scripts/contract-tools/compatibility.test.mjs](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/scripts/contract-tools/compatibility.test.mjs); [M:backend-inference/tests/test_schema_document.py](../../backend-inference/tests/test_schema_document.py). [E-CAT:contract-inventory.log](LOCAL-EVIDENCE.md); [E-CAT:contract-compatibility.log](LOCAL-EVIDENCE.md); [E-CAT:zod-python-roundtrips.log](LOCAL-EVIDENCE.md); [E-FOCUS](LOCAL-EVIDENCE.md).

**Dependencies:** None. **Remaining gap:** Structural validation is not owner/review authorization; inventory proves declarations/paths, not every runtime branch. Ontology adds four authorities, not biology validation. **Next action:** Keep exact authority inventory/semantic exceptions reviewed before future schemas.

### EN-002 — Session-bound email-link/Google identity and production provider setup

**Source / decision:** Architecture/delivery record; not new user authorization; Selected direction; credentials/operating policy external. **Implementation:** Maintained-library boundaries and labelled mocks implemented. **Integration:** Local protocol integration; production provider unavailable. **Publication / production:** unpublished in this workstream / not validated.

**Architecture:** U:src/lib/server/auth; U:src/hooks.server.ts; M:backend-inference/app/models/session_verifier.py.

**Behavioral acceptance:** Library-backed email/OIDC flow rejects replay/expiry/bad PKCE/signature; persistent sessions/logout/linking isolate owners; missing real configuration fails closed; actual app/local SMTP/signed Google mocks remain labelled.

**Tests and evidence:** [U:src/lib/server/auth/service.test.ts](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/src/lib/server/auth/service.test.ts); [U:src/lib/server/auth/email.test.ts](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/src/lib/server/auth/email.test.ts); [U:scripts/auth-integration.mjs](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/scripts/auth-integration.mjs); [U:scripts/auth-browser-checks.py](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/scripts/auth-browser-checks.py). [E-CAT:auth-provider-integration.log](LOCAL-EVIDENCE.md); [E-CAT:auth/auth-browser-results.json](LOCAL-EVIDENCE.md).

**Dependencies:** EN-001, PB-013. **Remaining gap:** No real mail/OIDC provider credentials/callback/transport verification; old PRD password JWT endpoint is not active application authority. **Next action:** Operator-owned provider/configuration review in a separate task; do not change credentials here.

### EN-003 — Local operations, recovery and eventual US hosting/rollback

**Source / decision:** Architecture/delivery record; not new user authorization; Local reliability agreed; US hosting direction selected, deployment excluded. **Implementation:** Host health/readiness/log/backup/recovery implemented; containers unverified. **Integration:** Local host integration; no deployed environment. **Publication / production:** unpublished in this workstream / not validated.

**Architecture:** U:src/lib/server/operations; U:scripts/private_backup.py; U:docs/local-operations.md.

**Behavioral acceptance:** Restricted structured logs omit private payloads; readiness/request budgets and graceful shutdown behave predictably; new-directory backup/restore verifies schema/hash/lineage and revokes restored capabilities; before deployment prove region, encryption, restore and rollback on actual built images.

**Tests and evidence:** [U:src/lib/server/operations/operations.test.ts](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/src/lib/server/operations/operations.test.ts); [U:src/lib/server/operations/request-budget.test.ts](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/src/lib/server/operations/request-budget.test.ts); [U:scripts/tests/test_private_backup.py](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/scripts/tests/test_private_backup.py). [E-CAT:operations-http.log](LOCAL-EVIDENCE.md); [E-CAT:private-recovery-tests.log](LOCAL-EVIDENCE.md).

**Dependencies:** EN-001, EN-002, EN-011. **Remaining gap:** Docker image execution previously blocked by registry network/DNS; no fresh container success claimed. Hosting, encryption and real restore/rollback remain unperformed. **Next action:** Preserve host proof; verify built containers/US infrastructure only in separately scoped work.

### EN-004 — Real audio model accuracy, taxonomy calibration and independent ML execution

**Source / decision:** Architecture/delivery record; not new user authorization; Real identification goal agreed; old numeric targets unvalidated proposals. **Implementation:** Validation/chunking/fixture/optional local ONNX adapters implemented. **Integration:** Technical cross-process integration only. **Publication / production:** unpublished in this workstream / not validated.

**Architecture:** M:backend-inference/app/audio_pipeline; M:backend-inference/tests/optional; M:docs/architecture/audio-pipeline.md.

**Behavioral acceptance:** Bound actual audio bytes/duration/chunks; exact licensed model/digest/taxonomy pin and unconfigured state; synthetic graph proves loading/inference mechanics only. Real acceptance needs representative licensed withheld recordings, reviewed thresholds and per-species error/calibration report before accuracy claims.

**Tests and evidence:** [M:backend-inference/tests/test_audio_api.py](../../backend-inference/tests/test_audio_api.py); [M:backend-inference/tests/test_audio_pipeline.py](../../backend-inference/tests/test_audio_pipeline.py); [M:backend-inference/tests/optional/test_audio_onnx.py](../../backend-inference/tests/optional/test_audio_onnx.py); [M:backend-inference/tests/optional/test_technical_fixture.py](../../backend-inference/tests/optional/test_technical_fixture.py). [E-CAT:python-audio-tests.log](LOCAL-EVIDENCE.md); [E-CAT:onnx-technical-tests.log](LOCAL-EVIDENCE.md); [E-CAT:synthetic-audio-evaluation.log](LOCAL-EVIDENCE.md).

**Dependencies:** PB-012, EN-001, EN-006. **Remaining gap:** No approved compatible bird weights or real biological validation. Historical ≥92% top-5, <600ms and 50RPS targets are neither measurements nor approved release gates. **Next action:** Select and license compatible model/dataset, then define representative evaluation; no model download/provider activation in this slice.

### EN-005 — Autonomous delivery, WebSocket scaling and legacy coordinator/gateway alternatives

**Source / decision:** Architecture/delivery record; not new user authorization; Legacy architecture proposal; current implementation choice not reaffirmed. **Implementation:** Only current local service boundaries implemented. **Integration:** Proposed distributed/realtime architecture not integrated. **Publication / production:** unpublished in this workstream / not validated.

**Architecture:** M:docs/architecture/product-requirements.md sections 1–4, 7–8; current SvelteKit BFF/FastAPI audio boundary.

**Behavioral acceptance:** Before real-time/distributed expansion choose transport and replay/ack/backpressure/tenancy contract; test reconnect, missed-event recovery, cancellation and user-visible updates under an agreed measured load. Preserve nonblocking UI and explicit human confirmation.

**Tests and evidence:** No executable acceptance test for this requested outcome. No passing outcome evidence or tested implementation commit.

**Dependencies:** EN-001, EN-006, EN-007, EN-003. **Remaining gap:** Original SQLModel/JWT coordinator, C++23 Asio TLS/gRPC gateway, Redis/NATS fanout, 100/10k socket targets, 500-device generator and numerical latency/RSS SLOs are historical proposals, not current proven system. No equivalent full-scale benchmark found. **Next action:** Re-decide smallest needed topology and acceptance load from actual requirements; do not implement a competing backend from stale PRD.

### EN-006 — Integrate the original separately completed autonomous worker

**Source / decision:** Architecture/delivery record; not new user authorization; Transfer already authorized; transport technically blocked. **Implementation:** Reported external artifact unavailable locally. **Integration:** Unintegrated. **Publication / production:** unpublished in this workstream / not validated.

**Architecture:** M:docs/delivery/approved-handoff-blocker-20261008.md; existing manually advanced fixture runner.

**Behavioral acceptance:** After readable original artifact arrives, validate exact digest/archive/base ancestry, inspect original worker, then prove single lease claim across workers, crash/backoff/cancel/late-output fences, review pause and graceful shutdown without duplicate provider calls.

**Tests and evidence:** No executable acceptance test for this requested outcome. [E-HANDOFF](../../docs/delivery/approved-handoff-blocker-20261008.md).

**Dependencies:** EN-001, PB-012, PB-018. **Remaining gap:** Worker c08624d3 not materialized; supported preparation/download failed twice before bytes. Network transport class known; underlying DNS/TLS cause unknown. No worker execution proof in this checkout. **Next action:** Repair supported artifact materialization through owning task; do not recreate worker or retry transfer here.

### EN-007 — Reconcile separate ESP32/device work without duplication

**Source / decision:** Architecture/delivery record; not new user authorization; Separate active workstream; no authority to duplicate. **Implementation:** Reported external commits absent here. **Integration:** Unintegrated; hardware unverified. **Publication / production:** unpublished in this workstream / not validated.

**Architecture:** M:docs/delivery/approved-handoff-blocker-20261008.md; UI engine checklist row 9; separate ESP environment.

**Behavioral acceptance:** Integrate exact owner-supplied original artifact only after ancestry/contract review; verify packet endian/length/sequence/truncation/replay, source dedupe and real hardware-to-backend semantics independently from audio-model accuracy.

**Tests and evidence:** No executable acceptance test for this requested outcome. [E-HANDOFF](../../docs/delivery/approved-handoff-blocker-20261008.md).

**Dependencies:** EN-001, EN-004, EN-005. **Remaining gap:** Reported c693ed02ca29b4cb538c94ff7c434ae8a11adad9 and 39 external tests are not local evidence; newer separate ESP work may exist but is not imported or assumed. **Next action:** Coordinate with separate owner when exact supported transfer is available; do not edit/reimplement firmware here.

### EN-008 — One authorized real source import and trusted arrival adapter

**Source / decision:** Architecture/delivery record; not new user authorization; Agreed future adapter boundary. **Implementation:** Generic import/manual path implemented; real adapter absent. **Integration:** Real source not integrated. **Publication / production:** unpublished in this workstream / not validated.

**Architecture:** U:src/lib/domain/evidence.ts; U:src/lib/server/arrivals; U:docs/pending-arrival-adapters.md.

**Behavioral acceptance:** Authorized representative Merlin/eBird export preserves source/taxonomy IDs and observed/unknown time; preview/errors visible; replay dedupes; only server-reviewed genuine confirmation can admit arrival receipt; unsupported data stays unknown.

**Tests and evidence:** [U:src/lib/server/arrivals/adapter-eligibility.test.ts](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/src/lib/server/arrivals/adapter-eligibility.test.ts); [U:src/lib/server/storage/findings.test.ts](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/src/lib/server/storage/findings.test.ts). [E-CAT:ui-unit.log](LOCAL-EVIDENCE.md).

**Dependencies:** PB-001, PB-010, PB-013. **Remaining gap:** Tests cover eligibility contracts/generic imports only, not a real Cornell integration. No representative authorized format/provider adapter exists. **Next action:** Obtain permitted sample and source semantics, then implement one bounded adapter; do not fabricate API access.

### EN-009 — Real regional weather and explicit coarse-location consent

**Source / decision:** Architecture/delivery record; not new user authorization; Future adapter direction; provider/location approval absent. **Implementation:** Simulated/manual/unconfigured provider boundaries implemented. **Integration:** Real weather not integrated. **Publication / production:** unpublished in this workstream / not validated.

**Architecture:** U:src/lib/server/weather/provider.ts; U:src/lib/weather; U:src/lib/domain/scene.ts.

**Behavioral acceptance:** Offline manual/simulated weather remains usable; real provider requires explicit owner coarse-location consent, bounded timeout/cache/stale/error states and no location in shared/render payloads.

**Tests and evidence:** [U:src/lib/server/weather/provider.test.ts](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/src/lib/server/weather/provider.test.ts); [U:src/lib/weather/weather.test.ts](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/src/lib/weather/weather.test.ts); [U:scripts/layered-browser-checks.py](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/scripts/layered-browser-checks.py). [E-CAT:layered/layered-browser-results.json](LOCAL-EVIDENCE.md); [E-CAT:ui-unit.log](LOCAL-EVIDENCE.md).

**Dependencies:** PB-011, PB-013. **Remaining gap:** No real provider/geolocation exercised; a region preference is not live weather or a precise-location grant. **Next action:** Choose authorized provider/coarsening policy in a separate task, then test actual failure/revocation semantics.

### EN-010 — Publication/PR and production checkpoint

**Source / decision:** Architecture/delivery record; not new user authorization; Explicitly excluded from this delegated local task. **Implementation:** Local commits only. **Integration:** Current changes not published or deployed. **Publication / production:** unpublished in this workstream / not validated.

**Architecture:** Git/review/release boundary; source user delegation, historical publication log.

**Behavioral acceptance:** If the owning publication task later resumes, verify exact local reviewed/tested heads, remote ancestry and required review/CI before any separately authorized release; local commit is never reported as pushed, merged or production validated.

**Tests and evidence:** No executable acceptance test for this requested outcome. [E-PUBLICATION](../../docs/agents/20261007_183500_publication-checks.md).

**Dependencies:** All intended release requirements; current complete frozen run. **Remaining gap:** User reports prior publication task stalled. Precise failure/cause is unavailable in this workspace and is not inferred. Published foundation bases do not mean these later local slices were published. **Next action:** Keep local work independent; no push, PR, merge, deploy or blocked-publication retry here.

### EN-011 — Account-wide erasure, offline retention and deletion-history operating policy

**Source / decision:** Architecture/delivery record; not new user authorization; Remaining privacy/operations requirement; destructive policy not selected. **Implementation:** Bounded media tombstones/cleanup/archive/recovery implemented. **Integration:** Account-wide/distributed deletion not integrated. **Publication / production:** unpublished in this workstream / not validated.

**Architecture:** U:src/lib/server/recordings/lifecycle-storage.ts; U:src/lib/server/operations/lifecycle-recovery.ts; U:scripts/private_backup.py.

**Behavioral acceptance:** Existing tombstones fence reads/new permits/late outputs; restore uses complete newest retained deletion ledger. Future erasure must enumerate account/derived/backup/download copies and prove bounded failure/retry/recovery without silently resurrecting content.

**Tests and evidence:** [U:src/lib/server/recordings/lifecycle.test.ts](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/src/lib/server/recordings/lifecycle.test.ts); [U:src/lib/server/operations/lifecycle-recovery.test.ts](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/src/lib/server/operations/lifecycle-recovery.test.ts); [U:scripts/tests/test_private_backup.py](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/scripts/tests/test_private_backup.py). [E-CAT:recording-lifecycle/recording-lifecycle-browser-results.json](LOCAL-EVIDENCE.md); [E-CAT:lifecycle-recovery-http.log](LOCAL-EVIDENCE.md).

**Dependencies:** PB-012, PB-013, PB-022, EN-003, EN-006. **Remaining gap:** No automatic discovery/erasure of offline copies, account-wide orchestrator, production purge or guarantee of newest ledger; archive is not deletion authorization. **Next action:** Define owner/operator retention and erasure policy; original worker integration precedes distributed cleanup.

### EN-012 — MLOps/model registry, training, monitoring and numeric performance ideas

**Source / decision:** Architecture/delivery record; not new user authorization; Legacy architecture proposals; tools/SLOs not adopted by this task. **Implementation:** Not implemented as an operating platform. **Integration:** Not integrated. **Publication / production:** unpublished in this workstream / not validated.

**Architecture:** M:docs/architecture/product-requirements.md sections 5–8; M:docs/architecture/audio-pipeline.md.

**Behavioral acceptance:** If adopted, first approve datasets/licenses, dataset/model/preprocessing versions, reproducible held-out evaluation and rollout/rollback criteria; test actual model registry, backups, drift metrics and resource budgets on the chosen runtime.

**Tests and evidence:** No executable acceptance test for this requested outcome. No passing outcome evidence or tested implementation commit.

**Dependencies:** EN-003, EN-004, PB-018, PB-021. **Remaining gap:** MLflow/DVC/Great Expectations/Grafana/GitOps/Terraform, fine-tuning/LoRA, GPU autoscaling, blue/green rollout, nightly validation/chaos and original GPU/CPU latency/accuracy targets are unvalidated proposals, not enabled services or paid-service permission. **Next action:** Select only justified tooling after real data/runtime needs are known; retain all cost/provider limits.

## Active ontology: input → actual effect → exact acceptance

These claims are about illustrative authored product rules and decorative fiction. They are not biological knowledge or actual observations. E-ONT names the dedicated browser revision; the current full aggregate remains separate.

| Input / boundary | Actual engine/rendering effect | Named behavioral test and visual evidence | Limit / next action |
| --- | --- | --- | --- |
| Species size | Fixture presentation scale changes transform/hit/legacy clearance; reviewed physical geometry retains authority | `behavior-policy.test.ts`: “never changes reviewed physical footprint when applying a developer behavior experiment”; `shape-occupancy.test.ts`: reserved support overlap; E-ONT 1×/4× pixel previews | Fractional responsive yard scaling is disclosed; native preview is separate. No anatomy approval. |
| Speed/hop bias | Safe-ground travel changes hop/flight mode while keeping destination; unsafe routes fly | `behavior-policy.test.ts`: “locomotion bias changes actual safe-ground travel while retaining the same destination”; E-ONT actual moving transitions | Illustrative defaults for three catalog species only. |
| Ground/perch/roost affinity | Initial placement, ordinary support choice and night support use trait eligibility and safe fallback | `behavior-policy.test.ts`: initial ground/perch affinity and night-compatible roost tests; E-ONT same resident moves perch→ground→perch | Current aggregate scene-phase regression must pass before integrated claim. |
| Feed/bath/nest/play/sing | Activities with zero priority are ineligible; object capability, fit and finite FIFO fairness constrain actual targets | `behavior-policy.test.ts`: disabled bathing, ineligible queue heads, unplaceable heads and legal nest move tests; E-ONT no-bathing/no-routines and nest removal | Missing authored sleep/play/nest clips deliberately use still idle; no breeding evidence. |
| Social spacing / fictional sociability | Bounded modifier changes clearance; no-space actors wait visibly in owner controls without drawing/reserving unsafe coordinates | `behavior-policy.test.ts`: priorities/spacing/response and waits-without-overlap tests; E-ONT 84 identities / 29 placed / 55 waiting sample | Finite sample is not arbitrary-density aesthetic approval. |
| Caution / fictional boldness | Bounded decorative response delay changes; trigger/cancel retains identities and clears reservations | `behavior-policy.test.ts`: species/personality response; `visits.test.ts`; E-ONT cautious preset and quiet cancellation | Nonviolent generic fixture predator, no observed response inference. |
| Stable fictional personality | Decorative ID only; rename/session/reorder preserves values; observations are not inputs | `behavior-policy.test.ts`: stability and no owner-evidence rewrite tests; E-ONT stable personality/unchanged owner snapshot | No editable persistence, recognition or progression. |
| Requested behavior / clip | Shared diagnostic reports selected intent, current state, sample, missing clips and quiet/static override | Three `behavior-diagnostics.test.ts` cases; E-ONT missing-routine still fallback and workbench trace | Displayed sleep pose does not imply simulated roost relocation. |
| Contacts / layers / accessibility | Reviewed shared transforms/footprints; opaque-hit depth ordering; keyboard controls, quiet mode, 320px layout, static SVG | E-CAT `shapes/shape-browser-results.json` and `scenes/scenes-browser-results.json`; E-ONT screenshots and assertions | Generic fixture feet lack reviewed anatomy/contact authority; at 320px birds remain tiny and dense controls long. |

Visual audit and actual screenshot interpretation: [UI behavior visual audit](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/docs/behavior-visual-audit-20261009.md). Independent source findings and repairs: [UI ontology review](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/docs/behavior-ontology-review-20261009.md). Original approved reference pixels were unavailable and were not viewed; no replacement artwork or final style/fidelity approval is claimed.

## Reconciliation of prior task lists and architecture claims

| Prior document / stale or orphaned claim | Authoritative reconciliation |
| --- | --- |
| Original `architecture/product-requirements.md` names JWT/SQLModel coordinator, automatic inference→art, WS query-token auth and broad scaling targets as if current | Historical architecture proposal. Current owner application is SvelteKit/SQLite/session-bound BFF and reviewed FastAPI audio boundary; candidates require human confirmation. EN-002/004/005/012 record unimplemented alternatives and unvalidated targets. Do not turn old examples into current deployment instructions. |
| Delivery README says “authorize transfer” | EN-006/007 and retained handoff evidence: transfer was already authorized; actual supported download failed twice before bytes. No new permission request or workaround is implied. |
| Matrix `lazy-shared-assets` and UI `generation-cost-foundation.md` say application hook/public payload are absent | PB-003 and later shared-catalog checkpoint supersede that statement for the bounded fixture path. PB-018 runtime metering, real provider execution and production publication remain absent. |
| Engine checklist H and row 11 refer to pending image-v3/sharing combined proof | E-CAT includes named `browser-image-v3` and `browser-sharing` passes. These older statuses are historical, not current blockers; no claim extends them to the active ontology candidate. |
| Older visual task tree points to PNG branch as “current verified” | Checkpoint-specific history. E-CAT is the last complete verified aggregate; active ontology has separate pending integration. Preserve earlier exact revisions rather than rewriting their results. |
| Broad PB-004/011 “verified” plus active scene failure | Historical fixture engine/layers pass is retained. Active ontology candidate is implemented/focused-tested, not completely integrated until repaired and re-run. |
| PB-016 described only as “agreed” despite helper tests | Helper exists and is tested disabled; operational hooks/retention policy remain unintegrated. Neither “all planned” nor “operational monitoring complete” is accurate. |
| PB-018 wording could imply real dispatch instrumentation | Only schemas/fingerprints/pure summaries are tested. No runtime caller, durable ledger, budget enforcement or billable measurement exists. |
| Svelte MCP/autofixer requested in older work | No dedicated callable Svelte MCP tool was available. Installed `svelte-check`, typed lint, build and actual Chromium checks are evidence; no MCP pass or connection is claimed. |
| Tests not represented by product-only rows | EN-001 maps generators/contracts; EN-002 auth providers; EN-003 request budgets/health/recovery; EN-004 ONNX/synthetic evaluation; EN-011 deletion recovery. Unit/browser counts remain subordinate to these named behaviors. |
| Product outcomes with no outcome test | PB-006 progression, PB-017 economics, PB-021 real species fidelity; EN-005 scale/realtime, EN-006 worker, EN-007 hardware, EN-008 real import, EN-009 live weather, EN-010 release, EN-012 MLOps. Fixture/helper tests do not close these gaps. |

## Source inventory and maintenance

Reviewed source groups: the original architecture PRD and audio architecture; delivery README/matrix, visual task tree, all retained wave/checkpoint summaries and transfer record; UI engine, ontology, PNG, retention and catalog checklists; contract authority/differential inventories; generation usage, image/source/shape, authentication, private recordings/recovery, sharing, analytics, arrivals, scene/weather and local operations documents. Historical agent logs and checkpoint counts remain evidence, not new decisions. No competitor or OSS peer analysis is included.

The subordinate [discovery and traceability audit](task-index-coverage.json) records 113 documentation files and 143 test-like files attributed to requirement families, with zero missing named test/evidence paths. This is file discovery and sampled traceability, not 143 passing test suites or complete case coverage. The legacy `backend-inference/tests/test_endpoints.py` is a manual device client and is explicitly excluded from automated gate claims. The independent reviewer checked all 158 relative links, the 34 stable IDs and sampled catalog/privacy/usage source assertions against retained evidence, and approved the bounded claims after narrowing physical-footprint guarantees.

On each bounded slice, update this index's affected stable IDs, exact tested revision and explicit residual gap; link the detailed slice evidence rather than cloning acceptance tables into another roadmap. A focused test pass may change local-verification state, but only a complete frozen passing report changes integration state for the active candidate. Publication and production validation require their own evidence and never follow from local integration. Independent review must challenge at least one source→test→evidence link and a remaining gap before a new completed claim.
