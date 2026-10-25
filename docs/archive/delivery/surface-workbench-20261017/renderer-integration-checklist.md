# Bounded SI renderer and actual-slot interaction acceptance

**Authority:** The [single current task index](../product-behavior-and-ideas.md#current-work-and-evidence--2026-10-17) owns task status under PB-023-B. This document is its supporting scenario/evidence protocol, not a separate task list.

**Status:** Pending current-source independent review and browser acceptance. Focused checks are reported in the current checkpoint; scenario results below remain pending until their own evidence exists. This is
the checklist for the newly authorized opt-in local extension, not evidence that
these scenarios already pass. Preserve the separately reviewed [isolated core
checkpoint](si-core-checkpoint.md), [prior code review](core-review.md) and
[design](../../architecture/surface-weather-model.md). Their hashes/counts do not
automatically cover new withdrawals, controller, simulation seams or renderer code.

| Scenario | Required outcome / evidence | Current status |
| --- | --- | --- |
| Exact revision | Record new core/runtime/controller/simulation/component/route hashes, focused tests, independent review, actual URL/captures and source-specific failure history | Pending |
| Main-yard default | Default main yard uses prior mode; sidebar/navigation, existing residents/names, placements, inventory, findings/art pins and saved weather remain intact; no external requests/provider/device calls | Pending |
| One-bath admission | Select the actual placed bath ID; physical catchment is authored 2 m² (1.88 ground + 0.12 bowl), not sprite-derived dimensions; missing/unsupported selection is explicit | Pending |
| Water level and rendering | Project actual accepted volume/depth into wet mask/level at current bath coordinates and ground-y depth; empty bowl cannot display full water, wet impacts or splash; ground/foreground occlusion is inspected in actual Pixi | Pending |
| Forcing / snow / melt | Physical ticks use one precipitation partition and SI ledger; snow SWE, limited melt and exact receiver transfer remain balanced while rendering respects bounded geometry; old illustrative overlay is not double-counted | Pending |
| Wet availability | Verify dry at/below 0.0005 m, wet admission at/above 0.001 m, stable hysteresis between, positive-volume requirement and no oscillating claims; thresholds labeled synthetic | Pending |
| Arrival and occupancy | Existing robin takes a valid route to an actual free bath slot; an in-flight reservation counts; occupied slots/footprint/clearance block safely; action begins only at valid settled contact | Pending |
| Drink mass | Over two settled-contact seconds request at most 0.0000005 m³ (0.5 mL); apply exact available-volume receipt once, including partial shortage; no consumption while traveling, blocked, paused or sampled at `dt=0` | Pending |
| Duplicate/stale requests | Same receipt replay does not increase totals; wrong action, object generation or geometry revision cannot consume water; new run uses fresh identity and old commands/effects cannot reappear | Pending |
| Clip truth | Public nine-state `Behavior` contract stays unchanged; local drink diagnostic shows missing authored drinking clip and idle fallback, never a false feeding/drinking animation claim; bath selects actual existing clip | Pending |
| Bath effect | Three-second cosmetic contact causes no water export/spill; optional core spill requests, if tested, use a separately named external sink with exact ledger and are not implied by visual drops | Pending |
| Move while active | Bath move preserves SI arrays/liquid/SWE/cumulative ledger, changes projection revision, cancels/invalidate old contact/effect safely and preserves actor identity; no stale-coordinate splash | Pending |
| Remove / re-add | Removing selected bath cancels its local claims and holds entire physical clock/state with `held-bath-removed`, not a fabricated export; same-ID re-add preserves storage with new generation; a different selection requires explicit replay | Pending |
| Initial litres / replay | Editing an initial-litre parameter does not refill active state; explicit replay creates one new initial-mass run with prior summary; no hidden reactive/array reset masquerades as rainfall or melt | Pending |
| Holds and resume | Disable, pause, hidden tab and reduced motion hold accepted state/debt; repeated render samples do not mutate; resume does not catch up a held interval; test real visibility where available and label synthetic handlers separately | Pending |
| Numerical overload | Fixed-step budget/debt ceiling and rejected interval remain explicit; accepted time/forcing is not silently dropped; failed solver commit preserves model state and clock debt | Pending |
| Environment interruption | Night/shelter/dryness/remove/generation change cancel safely, release only this action's claims and re-route/reconcile without teleport, orphan reservations or deleting other actors | Pending |
| Normal/reduced/fallback | Inspect normal animation, quiet/held state, keyboard controls, narrow/wide Mac viewports, Pixi and truthful static fallback; do not report a physical phone, full accessibility audit or live context restoration from viewport tests | Pending |
| Cost / cleanup | Measure complete integrated work separately from prior headless solver benchmark; bounded buffers/effects, repeated opt-in/mount/disposal and listener/resource ownership; default step ceiling is not a frame-time guarantee | Pending |
| Final scope | Explicitly state local synthetic model, no drinking artwork, no general topology/checkpoint persistence, no biological calibration, freezing/sloshing/full CFD, production art or real hardware/provider sync | Pending |

Keep unit/model evidence, actual rendering evidence and independent review separate.
Mark a row verified only with named current-source evidence; preserve failed attempts
and leave unsupported scenarios pending. No public wire/storage schema migration,
production publication, user-photo processing or external service is included.
