# Surface water and snow: reviewed-core design proposal

**Status:** Independently reviewed specification and bounded fixed-domain pure-core experiment, 2026-10-17. That checkpoint passed 33 focused tests and received code-review approval for its exact isolated source hashes. A separately authorized bounded opt-in renderer/local-interaction extension is now in progress; its fresh tests/review/browser acceptance are pending below. The last verified live `/art-lab` receipt covers the exploratory dimensionless prototype, not that extension. The full architecture, physical calibration and production acceptance remain unimplemented/unearned. [PB-023-B](../product/yard-and-behavior.md#pb-023-b--exercise-opt-in-basin-water-and-exposed-surface-snow-in-the-existing-yard-renderer) owns task status. No provider, production artwork or persisted yard migration is included. `U:` paths refer to the paired UI repository. Keep the established yard/sidebar available and shared component defaults opt-in.

The [checkpoint receipt](../delivery/surface-workbench-20261017/README.md) separates prototype tests/browser labels from the new pure experiment. The [SI-core benchmark data](../delivery/surface-workbench-20261017/si-core-benchmark.json) measures fixed-domain CPU work only, not Pixi, gameplay, GPU or physical mobile hardware.

Current integration WIP has a fresh focused 114-test/13-file pass and zero Svelte
errors/warnings, but its independent review and browser acceptance remain pending.
The 33-test approval and numerical/benchmark results cited below retain their
earlier exact source scope; they are not certification of later modifications.

The [isolated-core checkpoint](../delivery/surface-workbench-20261017/si-core-checkpoint.md),
[actual numerical reference results](../delivery/surface-workbench-20261017/numerical-reference-results.json)
and [independent code review](../delivery/surface-workbench-20261017/core-review.md)
retain exact scope, source hashes, repaired findings and deferred gates. Approval
does not authorize renderer migration or certify field predictions.

The independent specification review accepts the dimensional fixed-conductance law and proposed gates for an isolated fixed-domain implementation; it does not certify calibrated hydrology. The review required explicit overflow DAG semantics, tick-aligned event ordering/receipts, wet/revision-bound bath effects, numerical references, bounded history/backlog and separate local/cumulative residual tolerances. These clarifications are incorporated below. The first experiment is limited to new pure hydrology and clock modules/tests; topology/event-deduplication/checkpoint protocols, authored scene adapters, behavior availability, bird effects and browser integration remain future work even though those isolated modules pass their focused tests.

## Existing evidence and selected scope

The inspected authorities are `U:src/lib/engine/water.ts`, `surface-weather.ts`, their tests and `renderer.ts` coupling. Useful visual/slot tests do not establish physical accuracy:

| Current prototype | Engineering gap |
| --- | --- |
| 12×8 fixed basin; volume sums relative depths | No cell area/metre scale or authored catchment relation; total rain varies with cell count |
| In-place ordered `0.18 × head difference` donor-clipped transfers | Relative pair conservation/positivity, but no explicit time/face geometry; traversal bias is not numerical accuracy |
| Fixed inflow/outlet/melt indices and everywhere depth cap | Recorded spill is useful accounting, but cap clipping is not routing through an authored rim/outfall |
| Snow depth in visual units; four silhouette segments/object, twelve ground bands | No SWE/density/horizontal area; own-object top scanning does not mask covered ground or other objects |
| Melt normalized by total visual capacity, then clamped into one water cell | Layout/object count changes conversion; not snow-to-liquid mass conservation |
| Snow caps and deletion of absent object keys | Excess snowfall and removed-object snow disappear without a transfer/export ledger |
| Water helper clamps calls to 0.25 s; snow helper uses up to 1 s and a separate speed | Composition can admit different durations; current renderer additionally clamps ticker deltas to 0.15 s, so this is not proof the UI normally loses half its melt. Dropped wall time and freeze/backlog policy still need explicit treatment |
| Bath effects follow occupied slots/bathing actors | Good presentation seam; always-visible bowl has no stored water/rim/drain model; drinking action absent |

Select a bounded conservative **passive head-routing heightfield** for slow ponding/runoff first. This is an intentionally overdamped finite-volume storage network, not a shallow-water momentum solver, splash hydrodynamics or full CFD. EPA SWMM separates precipitation, surface storage, infiltration, evaporation and routing; that motivates explicit process accounting, not equivalence to SWMM. [EPA SWMM overview](https://www.epa.gov/water-research/storm-water-management-model-swmm)

Physical transient waves require another reviewed model choice. Shallow-water equations conserve depth and momentum with depth/velocity-dependent wave speeds; head-only routing cannot reproduce that behavior. No HLL/Riemann solver or hydrostatic reconstruction is selected here. [Clawpack authors’ shallow-water chapter](https://www.clawpack.org/riemann_book/html/Shallow_water.html)

## Domain and units

Version a synthetic physical domain independently from the 960×540 pixel scene. Its dimensions are authored assumptions, never measurements inferred from a photo. Replay receipts retain model/version, domain/forcing digests, parameter provenance and clock policy. Scene V1 is technical-fixture-only; reviewed persistence/production geometry requires compatible contract evolution.

| Quantity | Unit / definition |
| --- | --- |
| `z`, `h`, `H=z+h` | Ground elevation, liquid depth and head in m, with explicit local datum |
| `A`; face width/distance | Horizontal cell area in m²; lengths in m, independent of pixels |
| `V=A h` | Liquid volume in m³; authoritative state, not rounded display height |
| `S`; `A S` | Snow water equivalent (SWE) depth in m; equivalent volume in m³ |
| `P`, infiltration/evaporation capacities | Liquid-water-equivalent m/s, including snowfall input; UI mm/hour converted explicitly |
| `Q` | Edge/inlet/drain discharge in m³/s; transfers in m³ |
| `T`, `T_base`; `DDF` | °C; degree-day factor in m/(°C·day), with 86,400 s/day |
| Simulation `t`, fixed `dt` | s; independent of render cadence, wall time and illustrative daylight |

Author cells, materials, connections/barriers/sills, boundary types, inlets, finite stores and rim/outfall receivers. Object surfaces need stable IDs, horizontal collection areas, capacity curves where needed and explicit runoff receivers. Partition overlapping horizontal exposure: roofs intercept their fraction; ground receives the remainder/runoff. Never apply full precipitation to both roof and covered ground. Sprite colour/width is not physical terrain or catchment data.

Projection maps physical cells/surfaces into existing masks/depth/anchors. Quantization, visual snow-height caps and detail level change drawing only; mass remains in the state/diagnostics. Snow drawing depth needs an explicitly assumed density. HEC-HMS defines SWE as melted-water height and relates it to snow depth through density. [HEC-HMS snow properties](https://www.hec.usace.army.mil/confluence/hmsdocs/hmstrm/snow-accumulation-and-melt/snow-properties)

## Coupled conservative step

One pure `step(domain,state,forcingInterval,topologyEvents,dt)` owns snow and liquid. Rendering reads snapshots and cannot emit physical mass. Reject nonfinite/invalid input before mutation. Transfers carry `{step,sourceId,destinationId,volumeM3,reason}`; destination is storage or a named external ledger, never a pixel cell.

The first core accepts topology/forcing changes only at integer tick boundaries. At tick `k`, apply topology events first, sorted by the accepted monotonic sequence; then run stages 1–6 and atomically commit state/ledgers at `k+1`. Reject off-grid events rather than silently snapping them. Bound each run to 1,024 total accepted events, including queued and applied events. Within the active run, use `(runId,eventId)` deduplication with immutable payload digests and retained receipts; identical retry returns its receipt, changed payload rejects. A checkpoint binds last committed tick, next sequence, the complete bounded event/receipt authority, forcing/domain versions, state hash and cumulative ledger. Restore/retry cannot repeat transfers. At the event limit reject new commands until an explicit new run; never evict applied-event authority to make room. Resetting creates a new run with explicit initial storage, retaining one prior terminal summary; previous-run commands reject as stale rather than claiming an old receipt is retained indefinitely. No hidden mid-step topology mutation is allowed.

1. Integrate one precipitation forcing over `[t,t+dt)`. A declared phase fraction partitions `P_s=fSnow(T)P`, `P_r=(1-fSnow(T))P`; their sum is exactly `P`. A reviewed threshold/transition replaces independent full rain/snow sources. Apply interception once.
2. Update SWE and limited melt; debit snow and credit the exact equivalent volume to its authored liquid receiver once in the same step. Melt is internal, not additional precipitation. Add admitted rain/inlet/topology imports.
3. Compute infiltration, evaporation and drain requests from the same liquid snapshot after sources. If their sum exceeds available volume, scale all requests by the same available/requested ratio and record each actual sink separately; this proportional allocation is a declared synthetic policy. Initially infiltration exits the surface domain into a cumulative soil-export ledger; no soil moisture/groundwater solution is claimed. Finite soil capacity, if enabled, needs its own authored state. Zero sinks are explicit configuration.
4. Evaluate each undirected face once from the same pre-routing snapshot. Proposed law: `Q_ij=G_ij[max(0,H_i-s_ij)-max(0,H_j-s_ij)]`, where `G_ij≥0` is in m²/s and `s_ij≥max(z_i,z_j)` is the sill. One parameterization is `G=D_eff×faceWidth/centreDistance`, with authored `D_eff` in m²/s. This is project synthetic conductance, not measured soil conductivity or a verified Manning/diffusion-wave law.
5. Request `|Q|dt` per donor; if all outgoing requests exceed available volume, scale them together. Apply equal/opposite deltas simultaneously. New receipts cannot be respent in the same pass. Stable ID ordering controls floating-point summation only, not the mathematical update.
6. Route excess capacity through an explicit rim/overflow receiver or named boundary export. For the first core require the overflow graph to be acyclic with one declared receiver per store; reject cycles/missing receivers at admission. Process once in topological order: retain `min(V,capacity)`, pass the exact excess downstream or out of domain, recording each transfer. This separate bounded overflow pass may forward a newly received excess; stage 5's no-respending rule applies to face routing only. Each node/edge is visited once, so there is no iterative overflow loop. No silent clamp loss. Numerical guard overflow rejects/stops the step at the last valid state; it is not physical runoff.

Require conservation **and** nonnegativity plus behavioral accuracy. For fixed/frozen conductances use the proposed conservative margin `dt×sum(G_ij)/A_i≤0.5`; derive/check the actual solver's admissible step after adding sills, nonlinear coefficients, sources and limiters. This bound is not a proof for every extension. Persistent donor limiting reports an oversized step/configuration, not success. Test constant-head lake-at-rest, dry-sill blocking, symmetry, decay of discrete energy `sum(A(h²/2+zh))` in the closed no-source test domains, and step/grid refinement. Individual cells need not approach equilibrium monotonically. Do not tune away an order bias with a visually attractive constant.

Initial numerical scope is fixed nonnegative conductance and positive fixed areas; variable/nonlinear conductance requires a later reviewed stability bound. On unlimited-capacity/no-sink test domains satisfying the fixed-conductance bound, require donor limiting to remain inactive: a donor's head above the sill is no greater than its own depth, bounding requested outflow by available volume. Limiting is a safety mechanism, not an alternative integrator.

## Snow model and calibration limits

First slice: single-layer temperature-index **SWE accounting**, assuming a ripe pack, negligible cold content and immediate melt release:

`meltSWE=min(S_old+snowfallSWE,max(0,T_air-T_base)×DDF×dt/86400)`

`S_new=S_old+snowfallSWE-meltSWE`; liquid receives exactly `A×meltSWE` m³. Visual-height caps never delete SWE. Rain/snow classification and melt base are distinct parameters. HEC-HMS uses temperature-index melt factors alongside cold-content/liquid-water states; a simple factor does not reproduce that complete model. [HEC-HMS temperature-index method](https://www.hec.usace.army.mil/confluence/hmsdocs/hmstrm/snow-accumulation-and-melt/temperature-index-method)

Record phase thresholds, DDF, density-for-rendering, sink and conductance parameters with units/ranges and synthetic-authoring provenance. A literature range is not calibration of this yard. Physical predictions require identified calibration/validation data and applicable conditions. Roof radiation, cold-pack delay, rain-on-snow energy, compaction, wind redistribution, refreezing and sublimation remain excluded/zero-by-contract or later reviewed stores/fluxes. A cold-content/liquid-retention extension must add states and energy assumptions before claiming freezing/thermal accuracy.

## Mass ledger and topology

Every committed step balances in water-equivalent m³:

`W=sum(liquid V)+sum(snow A S)`

`residual=W_new-W_old-precipitation-externalInflow-topologyImport+infiltration+evaporation+drainExport+spillExport+drinkingExport+bathingSpillExport+topologyExport`

Melt and object-to-ground transfers cancel internally. Retain cumulative/per-step signed ledgers with domain/forcing/version IDs. Keep current-step transfer buffers, per-store cumulative totals and a 256-step diagnostic ring plus rolling digest; do not retain every face receipt forever. Detailed test traces are explicitly bounded exports, disabled in the ordinary renderer. Never count a transfer as both internal receipt and external loss. All sinks are bounded by available storage; no post-hoc mass repair or negative snow/water.

Proposed synthetic edit policy: moving the same object retains its SWE/bowl volumes and physical surface identity; projection and receivers change at a timestamped event. Removal carries stored mass out as `topologyExport`, with a receipt. An explicit empty/spill command would instead transfer to named ground storage first. Kind/area/capacity edits need a volume-preserving remap or recorded import/export; reject ambiguous changes. Never delete state keys because a sprite disappeared. Replay reset starts a new run with recorded initial storage. These are deliberate assumptions, not claims about natural snow movement.

### Authorized bounded renderer/interaction extension — verification pending

The next local slice is authorized to integrate the existing pure SI modules into
an opt-in `/art-lab` renderer and one selected actual bath, with local water-aware
drinking/bathing. This section is its admission/acceptance design, **not a claim of
completed runtime or browser verification**. The earlier 33-test independent code
approval applies to the exact pre-extension source hashes in its receipt; withdrawal,
runtime, controller and renderer changes need fresh tests/review/captures.

The authored physical catchment remains 2 m²: 1.88 m² ground plus a 0.12 m² bowl.
It is synthetic metric authoring, not dimensions inferred from pixel geometry.
Pixel projection uses the selected real placed object's current coordinates,
ground-y depth and actual bath-slot anchors. Admit a single selected bath identity;
unsupported/missing selections do not silently borrow another object's store.
Source forcing remains SI water-equivalent precipitation with an explicit phase
fraction, temperature-index snow and the shared fixed clock. Controls may map
wall time to one declared simulation speed; no second snow speed is allowed.
Initial bath litres apply at creation/explicit replay only, never as an unledgered
live refill when an ordinary control/reactive update runs.

**Bounded topology policy:** A move of that same bath preserves opaque SI state,
liquid/SWE and cumulative ledgers, changing projection revision and invalidating
stale effects/contact claims. Removing it holds the **entire physical experiment**
with a visible `held-bath-removed` status and retained state/clock debt/ledger.
This first slice commits no physical store-removal edit and therefore emits no
invented removal export. Re-adding the same selected ID retains storage but gets a
new object generation, invalidating old controller/effect identities. Selecting a
different object requires an explicit replay/new run, with one retained prior-run
summary and new initial mass. This conservative hold is a deliberate temporary
alternative to the future `topologyExport` protocol above; general topology
transfers, persistent edit receipts and checkpoint restoration remain unimplemented.

**Withdrawal extension:** The proposed forcing interface carries at most 128
bounded per-step requests `{id,storeId,volumeM3,reason}`, where reason is `drinking`
or `bathing-spill`; actual receipts also carry `actualVolumeM3`. Reject invalid/
duplicate IDs within a forcing tick, nonfinite/negative demands and unknown stores
before mutation. Environmental infiltration/evaporation/drain sinks run first with
their existing proportional-shortage rule. Interaction requests then share remaining
liquid proportionally per store, before snapshot face routing. This class priority
is a declared synthetic policy, not a physiological claim. Debit only actual volume
and record `drinkingExportM3` / `bathingSpillExportM3` as named external boundaries
in local/per-store/run accounting; requested shortfalls are not consumed water.
An external spill is not a modeled splash returning to ground. The initial bath
animation is cosmetic and requests **zero** bathing-spill volume.

**Actual-slot controller:** Use existing simulation route, footprint clearance,
slot availability, in-flight reservation and occupancy authority for the existing
European robin actor; no teleport or separate pretend occupancy table. Wet hysteresis
uses synthetic 0.001 m entry and 0.0005 m exit depths, with positive volume required.
The local action diagnostic is separate from the closed public nine-value `Behavior`
enum. A requested drink uses an explicit missing-authored-drinking-clip/idle fallback;
an existing bathing clip can render the bath action. Do not relabel feeding pixels
as authored drinking or imply a new wire state. Other residents and saved evidence
retain their existing identities and authority.

The planned drink requests at most 0.0000005 m³ (0.5 mL) per action, at
0.00000025 m³/s for two settled-contact seconds. These are product test amounts,
not measured needs or biology. Bath is a three-second cosmetic contact with no mass
withdrawal. Generate withdrawals on admitted physical ticks only; zero-delta render/
contact checks cannot consume water. Count each actual matching request receipt at
most once; wrong-action/stale-generation/replayed receipts cannot inflate totals.
Dryness, night/shelter, moved revision, removed selection or generation mismatch
must cancel the local action and release its own claims through safe existing
reconciliation, preserving actors and other residents' claims. Empty/occupied/
unavailable states need explicit diagnostics and must not create a splash or debit.

**State and time:** Disabled, paused, hidden and reduced-motion views hold the
accepted model/clock state rather than recreating water arrays or refilling the
bowl. A pure sample cannot mutate mass. Overload remains explicit bounded admission
pause/backlog, not wall-time truncation. Only replay creates fresh initial state.
The main yard/sidebar and its default renderer retain their existing behavior;
physical mode is opt-in and must be mutually clear with the old illustrative
water/snow overlay so the same input is not counted or drawn twice.

The [integration acceptance checklist](../delivery/surface-workbench-20261017/renderer-integration-checklist.md)
owns the concrete pending scenarios and evidence boundary for this extension.
No full fluid/momentum, freezing, sloshing, thermal/biological calibration,
production artwork or real provider claim is authorized by this slice.

## Bird, time and performance interfaces

Reuse current object/occupied-slot IDs, pose/contact anchors and ground-y ordering. A bounded timestamped `bath-contact` event can trigger cosmetic ripples/splashes without mass change. Physical displacement/spillage needs a distinct volume transfer; an animation cannot invent consumption or water. Bind effects to object-instance generation and geometry/topology revision plus slot-local coordinates; recompute projection or invalidate at a move, and invalidate on removal. Re-adding a reused ID cannot resurrect old effects. Validate current slot ownership/geometry. The authorized bounded local-action extension above does not change the public nine-state behavior enum or add physiological/detection claims; its withdrawal/controller integration requires fresh acceptance.

The adapter must require an actually wet liquid surface at the modeled level before drawing a water-contact effect; a slot alone cannot splash an empty bowl. The bounded local controller above proposes explicit hysteresis and interruption/reservation checks under PB-004/024. General species-wide water availability, physiological scheduling and persisted policy remain separate future work. The earlier prototype's independently scheduled bathing is not evidence for the new water-aware integration.

Use integer ticks and one forcing/event timeline. Render arbitrary cadences from snapshots; interpolate presentation only. Speed controls map wall time to a declared simulation target, not a second snow clock. Explicit pause/hidden/reduced-motion hold the experiment clock; numerical overload is different. Retain deterministic backlog and report lag, or explicitly pause when a CPU step budget is exceeded. Never truncate admitted simulation time. For the first core all forcing/event changes are tick-aligned; integrating off-grid series requires a separately defined deterministic substep policy. Resume an intentional hold without catch-up; ordinary slow frames still reach the same target ticks.

Use bounded arrays and authored domain limits before considering a CFD/GPU rewrite. Initial proposed ceilings: 1,024 cells, 2,048 undirected face edges, 24 auxiliary object/catchment stores, 1,024 accepted input events per run (queued plus applied with receipts), 8,192 current-step transfers and 256 diagnostic summaries. Admission rejects excess/overflow before mutation. At `dt=0.05 s`, process at most 20 model steps per scheduler turn; retain up to 2,000 pending ticks (100 simulated seconds). Before a wall-time target would exceed that queue, explicitly pause admission and report unadmitted time/required attention while preserving existing debt. Do not claim the paused interval was simulated; clearing/resuming or resetting is explicit. Memory/backlog remains bounded without silently losing an admitted forcing interval. Test ordinary 15/30/60 Hz and finite long-frame replay by draining the same admitted target before comparison.

Simulation resolution is independent of sprite detail/effect caps. These ceilings are proposed test limits, not performance guarantees: measure p50/p95/p99 CPU time and allocations on identified devices before setting a release budget. No unmeasured mobile/GPU promise. The current 96-cell/768-water-primitive and 156-surface-primitive budgets are prototype limits, not measured performance of this core. Keep private V3/V4 artwork limits (65,536 decoded pixels/64 frames) and public V2-only catalog migration separate from numerical resources.

## Acceptance before promotion

These are proposed gates, not passing evidence:

| Gate | Concrete checks |
| --- | --- |
| Units / exposure | 1 m² × 2 mm/hour × 3 hours = 0.006 m³ (6 L) precipitation/SWE; same total after subdivision; no roof/ground double collection |
| Snow coupling | Synthetic DDF 3 mm/(°C·day), 4°C above base for 6 hours melts 0.003 m SWE (3 L/m²), limited by pack; receiver gets that exact volume once |
| Balance | Closed/no-source mass invariant; every source/sink/topology edit balances. Per-step Float64 residual limit `max(1e-12 m³,1e-9×max(W_old,W_new,stepInputs,stepOutputs,1e-6 m³))`. Separately bound run residual by `max(1e-12 m³,1e-9×max(initial W,cumulative external inputs,cumulative outputs,1e-6 m³))`; report maximum and sum of absolute local residuals so signed cancellation cannot certify conservation. Tighten proposed gates where measured arithmetic permits |
| Numerics | Lake-at-rest, dry sill, rotated/symmetric basin, edge-order permutation, wet/dry positivity, rim/drain cases, `dt`/grid-refinement error against declared references, limiter/stability diagnostics |
| Time / edits | Same target ticks/forcing at 15/30/60 Hz, irregular long frames and retained backlog; hold/resume, move/remove/re-add/kind/area policy, deterministic checkpoint/restart/hash |
| Actual rendering | Occupied wet bath contacts, empty-bowl/rim exclusion, move/remove/re-add during a live effect, stale-revision rejection, exposure masks, snow beyond display cap, ground/object depth, Pixi/held SVG, default-yard/sidebar/storage/privacy regression |
| Review / performance | Independent dimensional/numerical review, exact-source ledger traces and browser evidence, fixed-domain CPU/memory/effect measurements. Physical calibration and device qualification explicitly separate |

The initial synthetic reference suite fixes `dt=0.05 s` and Float64 arithmetic. For a two-cell analytical check use `A_0=A_1=0.25 m²`, flat zero bed/sill, `G=0.001 m²/s`, initial depths 0.03/0.01 m, no forcing/sinks/caps. At 60 s compare to `h_0,1=0.02±0.01 exp(-2Gt/A)`; require maximum depth error below `1e-6 m`, inactive limiter and error reduction 1.8–2.2 when halving `dt`. This verifies the chosen linear routing law, not real flow.

For spatial refinement use a 2 m × 1 m flat, closed 1D strip, `D_eff=0.001 m²/s`, 8/16/32 equal-area cells, no forcing/sinks/caps and `h(x,0)=0.02+0.005 cos(pi x/2)` m. Initialize **exact cell averages**, not centre samples: the cosine average is `cos(k x_center)×sinc(k dx/2)`, where `k=pi/2` and `sinc(a)=sin(a)/a`. Compare cell averages at 60 s to the no-flux diffusion solution `h(x,t)=0.02+0.005 cos(pi x/2) exp(-D_eff(pi/2)²t)`. Require maximum cell-average error below `1e-6 m` at 32 cells and successive L1/L∞ error ratios 3.5–4.5; record temporal-error contribution and tighten `dt` if needed to isolate spatial error. Add nonflat constant-head/dry-sill and finite-capacity overflow tests separately. These thresholds are proposed executable acceptance for a synthetic model; empirical calibration and arbitrary-terrain convergence remain unearned.

## Current isolated implementation checkpoint

`U:src/lib/engine/surface-hydrology.ts` supplies immutable admitted fixed-domain
stores/areas/conductances, supplied phase-partitioned water-equivalent forcing,
SWE/melt transfer, proportional sinks, snapshot face routing, liquid overflow DAG,
per-store/cumulative ledgers and bounded diagnostics. Its 13 focused tests cover
the two-cell/time and exact-cell-average spatial references, 6 L precipitation/
3 L melt cases, exposure subdivision, mixed phase, overflow/sinks, lake-at-rest/
dry sill, seeded mass/positivity/energy, orientation/order and atomic admission/
resource/numerical guards. Snow fraction is supplied by the test forcing; this
does not implement a weather/temperature classification adapter or calibration.

`U:src/lib/engine/surface-clock.ts` supplies the standalone fixed-tick clock,
fractional-time retention, hold/explicit resume, bounded debt and rejected-interval
reporting. Its 18 tests cover varied/irregular cadence, zero/sub-roundoff intervals,
limits, hold/overload and failed solver commits. `maxStepsPerTurn` is configurable
from 1 to 20 (default 20); that ceiling is not a frame-latency guarantee. Two tests
in `U:src/lib/engine/surface-coupling.test.ts` compose the real modules with explicit
clock/model tick matching and tick-aligned cold/warm rain/snow forcing at
15/30/60 FPS plus stutters, and verify rejection preserves both accepted model
state and clock debt. All 33 tests passed under pinned Node 24.19.0 locally.

This is a process-local opaque-state experiment with no restoration protocol.
Its FNV diagnostic digest is noncryptographic and cannot stand in for immutable
replay/checkpoint authority. The broader topology/removal event ledger, command
deduplication/receipts, persisted checkpoints, authored geometry/versioned scene
adapter, wet-bowl effects, water-aware bathing policy and renderer integration
described above remain unimplemented. No existing prototype algorithm or live yard
was replaced. The [independent code review](../delivery/surface-workbench-20261017/core-review.md)
approved this bounded code after clock-boundary and finite-demand guard repairs;
it does not close any deferred integration or physical-validation gate.

The retained benchmark measures 96/384/1,024-cell synthetic domains on the Mac.
At 1,024 cells a 20-step burst has p95 15.5833 ms and maximum 18.0494 ms before
any browser/Pixi work; default burst size cannot be assumed to fit a release frame
budget. Use measured workload/device budgets and a smaller deterministic work
ceiling where selected. There is no browser/GPU/mobile or empirical-hydrology
qualification. A source citation, a test suite or a balanced ledger alone is not
validated hydrology or approved production art. Keep the live prototype labeled
until a separately reviewed adapter and actual integration gates pass.

Primary sources were read on 2026-10-17. Continuity diagnostics and time-step sensitivity are also discussed in the [EPA SWMM 5.2 User’s Manual, section 8.5](https://www.epa.gov/system/files/documents/2022-04/swmm-users-manual-version-5.2.pdf). The conductance law, policies, tolerances and test domain here are project design choices requiring review, not implementations claimed from those manuals.
