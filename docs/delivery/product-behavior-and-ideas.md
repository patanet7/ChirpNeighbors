# Product behavior and ideas register

This register records product intent without treating tentative ideas as approval.
The [task tree](visual-task-tree-20261008.md) owns implementation sequencing and
acceptance detail; this register owns stable product decisions and unresolved
ideas. The [delivery matrix](matrix.json) and retained checkpoint
reports own verification evidence. Update these links and statuses together;
do not create a competing roadmap.

Source types: **user decision**, **tentative user idea**, **assistant proposal**.
Statuses: **proposed**, **agreed**, **implemented**, **verified**, **blocked**,
**deferred**. “Implemented” means local code exists, not all gates passed.
“Verified” always refers to named test evidence, never biological validity,
production readiness or unperformed deployment. Fixture art remains fixture art.

| Stable ID | Description | Source type | Status | Dependencies and task/contract links | Concrete acceptance and remaining decisions |
| --- | --- | --- | --- | --- | --- |
| PB-001 | Preserve source Findings with stable dedupe and append-only corrections. | user decision | verified | V5–V6; UI `domain/evidence.ts`, `domain/yard.ts`, SQLite repository; [contracts](../../contracts) | Exact retries/imports do not duplicate events; changed same-ID input conflicts; corrections preserve source evidence and distinguish observed, uploaded and model intervals. Owner isolation and backup roundtrips pass. New arrival hooks must preserve these rules. |
| PB-002 | Recent eligible Findings create temporary species visitors; owners explicitly keep and name residents. | user decision | verified | PB-001; V5–V6, I5; `BirdInstance` and visitor policy | Unknown/future/old evidence cannot invent a recent visit. Expiry, explicit promotion, reload and names are stable. A decorative resident is not recognition of an individual wild bird. Existing observation-driven expiry behavior remains authoritative. |
| PB-003 | Shared canonical species/style/version assets are built lazily as species arrive; later variants are added as needed. | user decision | agreed | G1–G2; reviewed immutable manifest/source, taxonomy, rights and future catalog release | One canonical missing-asset request rather than one generation per owner/sighting. Explicit placeholder until reviewed release. Do not prebuild the full catalog, reinterpret private manifests as public assets, or share raw private media. Durable request contracts/queue are implemented; the application hook and shared release rendering remain pending. |
| PB-004 | Autonomous idle, move, hop, fly, perch, sing, feed, bathe, sleep, play and nest-building routines. | user decision | verified | V1–V4, I2–I4; animation registry, pose clips and simulation | World travel stays separate from in-place authored action. Missing clips use documented still/idle fallback; valid bounds/timing/support/occupancy persist across direction and object edits. Existing fixture routines do not establish real species likeness or biologically correct motion. Full authored species clips await reviewed art. |
| PB-005 | Species-level illustrative tuning and fictional individual personality are different concepts. | user decision | agreed | I3, C1; bounded species profile contract; future traits contract | Biological knowledge, illustrative simulation tuning, fictional persistent traits and observed evidence are separate labelled fields. Profiles are bounded and deterministic. Persistent individual traits need a versioned model and migration before implementation; do not infer personality from private recordings or recognize individuals. |
| PB-006 | Earned companionship and levels should support attachment without pressure. | user decision | agreed | C1; PB-002, PB-005; progression contract pending | Specify interactions, bounded rewards, storage/migration and accessible alternatives before code. No missed-day punishment, starvation, guilt, paid affection or loss of birds. Exact progression rates, levels and rewards are unresolved. |
| PB-007 | Free per-owner object inventory separates owned stock from placed perch, feeder, bath and nest instances. | user decision | verified | I1; `domain/object-inventory.ts`, placement snapshot/CAS, SQLite receipts | Place/return/move are transactional and idempotent; stock never becomes negative; legacy objects survive deterministic migration. Lost-response retry preserves exact intent UUID, reload/restart/restore and owner isolation. Pointer/keyboard integration and the complete 70-gate checkpoint pass. No currency or purchasing is included. |
| PB-008 | Initial safe positions vary by session while persisted identities and yard layout stay stable. | user decision | verified | I2; uint32 session seed, occupancy, per-tab owner UI helper | Explicit seed reproduces initial positions; rerender/navigation/reload within the session does not reseed unexpectedly. Different seeds may vary positions without altering residents/layout; collision, perch capacity and reduced-motion fallback remain safe. Integrated behavior browser evidence passes in the 70-gate checkpoint. |
| PB-009 | A decorative nonviolent predator/hawk visit can approach, scatter birds, return them and enter cooldown. | user decision | verified | I3–I4; finite simulation phases and reservation cleanup | Bounded coalesced triggers, cleanup on hidden/quiet/removed-object transitions and safe return. No injury, deletion, evidence creation or persistence of alarm state. Current visitor is a labelled generic fixture, not replacement hawk art. Actual integrated playback/cancellation evidence passes in the 70-gate checkpoint. |
| PB-010 | A newly confirmed eligible sighting may receive one fly-in and an accessible banner; keeping remains optional. | user decision | verified | I5; trusted server admission, durable receipt, arrival controller and scene cue | Consume before cue, bounded notices, retry/reload/tab dedupe, correction/restore cancellation, keyboard/mobile and reduced-motion placement. Native manual entry is the initial trusted path. Generic JSON imports and technical audio fixtures cannot grant real notices. Genuinely confirmed observations from future authorized import/audio adapters may qualify through the same reviewed server-owned admission policy; raw candidates, unknown times and duplicate replays remain ineligible. Central wiring and arrival browser evidence pass; real adapters remain unavailable. |
| PB-011 | Visually simple regional yards use separate ground, objects, birds and foreground layers, weather and time. | user decision | verified | V2; scene manifests, weather state, I1 | Preserve layer order, walkable zones, placeable objects and weather/time controls in Pixi and static SVG. Shared views omit location. Current regional scenes remain fixtures; no live location/weather provider is configured. |
| PB-012 | Private recording playback leads to analysis candidates, explicit confirmation and a saved Finding. | user decision | verified | V5–V6; audio contracts, immutable recording/analysis receipts | No autoplay or fabricated model score; distinguish intervals and timestamps; validate owner/model/input provenance. Deleted/revoked media cannot be revived by retries/restore. Technical model output remains explicitly technical and cannot be presented as verified biological identification. Real providers remain future adapters. |
| PB-013 | Private accounts, media and owner data are the default; optional shares are safe view-only projections. | user decision | verified | S1; verified sessions, owner repositories, recording lifecycle and share projection | Never trust supplied owner IDs. Shared output contains no owner location, recordings, Findings or private asset refs. Revoke/expiry/restore invalidate capabilities. Cross-tab account-switch protection, bound backup download and new routes pass independent review and the complete 70-gate checkpoint. |
| PB-014 | Reviewed source rights, provenance and immutable shape/animation workbench precede reusable artwork. | user decision | verified | V1–V4, P1–P4; source, manifest, shape and image-stage schemas | Exact source/pin/pose binding, raw frame inspection, bounded geometry, clip fallbacks, licensing/attribution and separate approval/pinning. Corrupt/missing assets fail visibly and safely. Approved concept pixels are unavailable; no replacement art or fidelity claim. Photo decoding, real segmentation/generation and external fetching remain unconfigured. |
| PB-015 | First-party analytics answer coarse product-use questions only after explicit consent. | user decision | verified | A1, S1; closed event/batch/consent schemas and separate stores | Off by default; no owner, species, media, Findings, location, URL, IP, token, referrer or freeform event dimensions. Independent server validation, bounded buffers, revoke/regrant fencing, purge and retention. Internal reports are restricted; event ratios do not claim unique-user retention. Policy/retention choices and local web-vitals dependency review remain unresolved. No external collector or real-user activation. |
| PB-016 | Minimal restricted security audit is separate from optional product analytics. | user decision | agreed | A1, S1; coarse fixed-code security events | No raw request/identity/evidence payloads. Default disabled, explicit retention and operator cleanup; do not imply consent to product analytics from necessary security work. Hook selection and actual operational policy remain review gates. |
| PB-017 | Sustainability may include voluntary support, premium themes, daily credits or small ads. | tentative user idea | proposed | C1, G1–G2; future economic/privacy review | Compare costs, accessibility, owner control and privacy before choosing. No credits, currency, purchases, ads, billing SDK or paid affection is authorized as implementation by this entry. No option is selected or promised. |
| PB-018 | Track generation resource usage and unknown costs accurately. | user decision | implemented | G1; usage schema, safe recipe fingerprints and owner-scoped private dedupe | Actual dispatch attempts/duration/classes, cache reuse and accepted/rejected output are distinct from human review. Unmeasured cost stays unknown. Contract-only instrumentation must not claim a real provider ran; durable budgets/cancellation/retry enforcement precede future execution. |
| PB-019 | Protect progress against restored consent and presentation rollback. | assistant proposal | verified | A1, I5; offline restore tools | Restore should default analytics consent off and invalidate restored pending arrival notices. Offline restore copies now cancel pending notices, revoke consent and discard optional aggregate counters; original backups/evidence stay intact. Two focused real backup/restore tests cover stores with and without a recording deletion ledger. The complete 70-gate checkpoint verifies the integrated recovery mechanics. |

## Missing decisions and superseded approaches

- PB-005/PB-006: individual trait dimensions, companionship levels, earning rates and
  accessibility alternatives remain open. Species tuning is not a substitute.
- PB-003: shared render payload/public release contract, reviewed initial artwork and
  real execution adapters remain unavailable; private V3 lineage must not be relabelled.
- PB-015/PB-016: jurisdiction/policy review, final retention periods and operator
  access/cleanup requirements remain open. Voluntary DNT/GPC defaults are not a
  legal-compliance claim; minimum counts are not an anonymity guarantee.
- PB-017: all sustainability options are tentative; none enables an economy.
- Superseded: use of old main as the engineering base. Work derives from the
  published foundation-review branches and preserves prior checkpoints.
- Rejected for current scope: paid services, external providers, replacement art,
  credential changes, fabricated integrations, production activation and publication.
- Superseded implementation assumption: an animation clip selector alone is enough
  to approve a package. Reviewers must inspect every packaged frame, including unused ones.
- Rejected security assumption: same-origin cookies alone protect an old tab across
  account replacement. Verified document/session binding is required.

## Evidence and update policy

The prior contracts checkpoint is retained in
[contracts-verified-20261008](contracts-verified-20261008). The visual wave's first
aggregate retained 60/65 at `/tmp/chirp-visual-system-20261008-r1`; the corrected
complete rerun passed 65/65, recorded in
[visual verification](visual-verified-20261008.md). Interactive/privacy/catalog
code must not borrow that visual checkpoint's verification status. Its own
complete 70-gate run passed; see [interactive verification](interactive-verified-20261008.md)
for exact tested revisions, retained failures, counts and remaining dependencies.
