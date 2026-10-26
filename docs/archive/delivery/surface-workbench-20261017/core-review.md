# Independent review: isolated surface core and clock

2026-10-17. **Verdict: approve the reviewed code for the bounded, fixed-domain pure-core experiment. No unresolved blocker was found within that scope after the clock repair and numerical guard hardening.** This is not approval to migrate the live renderer or a claim of physical calibration or production acceptance. The [architecture proposal](../../../architecture/surface-weather-model.md) and [checkpoint receipt](README.md) retain those distinctions. `U:` denotes the paired `birdsong-yard-sprites` checkout.

## Scope and evidence

Reviewed actual `U:src/lib/engine/surface-hydrology.ts`, `surface-clock.ts`, their tests and `surface-coupling.test.ts`. The reviewer made no simulation-code or service changes. Final independent execution with pinned Node 24.19.0 passed **33 tests in three files**: 13 hydrology, 18 clock and 2 coupling tests. This is a focused result, not a full repository quality pass.

```sh
npx --no-install vitest run src/lib/engine/surface-hydrology.test.ts src/lib/engine/surface-clock.test.ts src/lib/engine/surface-coupling.test.ts
```

Across the review, separate read-only probes exercised 70 hydrology cases, including 60 seeded eight-store histories totaling 6,000 randomized steps. Checks included per-store closure, global balance, nonnegativity, partitioned roof/ground precipitation, finite overflow chains, atomic invalid forcing, aliases/extra cyclic properties, forged state/model rejection, SI-depth overflow and strict finite melt demand. The worst observed global step residual was **6.302e-16 m³**; worst independently computed per-store residual was **9.571e-17 m³**. A further 100-step paired trajectory matched complete state after store/edge permutation and edge reversal.

Independent clock probes covered 111 cases: ten cadences including 59/60/1000 Hz with zero-time admissions, 100 seeded irregular interval histories, and held/overloaded debt. Maximum observed difference between supplied time and committed-plus-pending time was **2.132e-14 s**. These finite synthetic cases are evidence, not an exhaustive numerical proof.

## Findings resolved before approval

- **Clock boundary defect:** three ordinary 1/60-second advances followed by `admitSurfaceTime(clock, 0)` could produce `pendingTicks=-1` and `remainderSeconds=dt`. A snapped boundary retained stale positive Kahan compensation. The owner now clears compensation at normalization, preserves debt on zero admission and rejects invalid computed debt. Permanent regressions cover 59/60/1000 Hz; the added seeded cadence/hold suite also passes.
- **Finite-input overflow policy:** a melt demand could overflow before the available-pack minimum and still yield finite output. Although positive saturation need not violate conservation, that contradicted the strict numerical-guard policy. The final core rejects nonfinite melt requests before limiting; a bounded 0.006 m³ pack with huge finite temperature rejects atomically. Initial/final SI depth/head and transfer-buffer guards were also inspected and probed.
- **Bounded admission and authority:** resource lengths are checked before collection copying/traversal; the frozen model copies declared fields rather than arbitrary caller properties. Prepared topology is frozen, and process-local model/state identity rejects forged or restored copies. Tests and probes confirm rejected steps preserve the accepted state.

The implemented snapshot face transfers, fixed-conductance admission bound, SWE-to-liquid debit/credit, proportional sinks and bounded DAG overflow agree with the selected first-slice design. The permanent analytic/refinement tests execute against the actual core. Coupling tests establish equal complete state across 15/30/60 Hz and stuttered admissions, and retain model state plus clock debt on solver rejection.

## Limits and remaining gates

Exposure is an **authored catchment partition**, not geometric roof-intersection discovery. The core receives explicit precipitation phase fractions; it does not select a calibrated rain/snow classifier. Snow is a ripe-pack temperature-index approximation. Routing has no momentum, waves, groundwater, refreezing or calibrated yard terrain.

Topology edits, event deduplication, checkpoint restoration, an authored scene/projection adapter, water-aware bird eligibility/contact effects and UI migration remain deferred. The clock requires a synchronous transactional solver callback. Its bounded overload policy reports unadmitted time rather than claiming that time was simulated. The diagnostic digest is not a cryptographic checkpoint authority.

Keep the working prototype labeled experimental. A later integration requires its separate geometry/versioning, exposure, wet-bowl/slot-revision, rendering/fallback and storage/privacy checks. Headless numerical timings cannot establish browser/GPU performance or physical mobile-device qualification; benchmark budgets and release performance remain separate gates.

## Reviewed source hashes

Final test execution reported these SHA-256 values:

| UI source | SHA-256 |
| --- | --- |
| `src/lib/engine/surface-hydrology.ts` | `e5a36d86f71e3b187dcbe6faa102b095c72f2adea31348c702b0fb25df48ad2c` |
| `src/lib/engine/surface-clock.ts` | `7da92126d23fadb0fbdbb77cbfaa115344a00ebe082522634cf823f9529bef45` |
| `src/lib/engine/surface-hydrology.test.ts` | `01af88ccc6b5e6695ba36b5c15045a3d1cab3bebb8334152dfbbc8fe7c831216` |
| `src/lib/engine/surface-clock.test.ts` | `91e6456ff4b5d72b40dfecb923a02bd4c18edc2e19c4ef785efa32609cba5116` |
| `src/lib/engine/surface-coupling.test.ts` | `202d15e1621bd03ea35e2347f4dc55ddf87d658cd4715e28220d3d7e890179d8` |
