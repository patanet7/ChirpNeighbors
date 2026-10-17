# Isolated SI core and shared clock checkpoint

2026-10-17. This implements the fixed-domain numerical slice of the [reviewed design](../../architecture/surface-weather-model.md). It does **not** replace the live `/art-lab` prototype. Model parameters and the 2 m × 1 m domain are explicitly synthetic; no physical yard calibration, momentum/waves, energy-balance snow, sensor integration or production acceptance is claimed.

## What exists

`U:src/lib/engine/surface-hydrology.ts` admits copied/frozen authored stores, finite positive areas, fixed face conductance/sills, fully partitioned catchments, exact liquid/SWE initial storage and an acyclic finite-store overflow graph. It enforces `dt sum(G)/A <= 0.5` and rejects invalid inputs/over-budget topology before numerical work. States are immutable and bound to the admitted model in this process; restoring arbitrary JSON is deliberately unsupported.

One atomic tick partitions precipitation once, melts limited SWE into its exact authored liquid receiver, adds inflows, allocates limited sinks proportionally, routes equal-and-opposite face transfers from a common snapshot, then passes overflow in topological order. Snow is uncapped by visual height. Per-store and global ledgers distinguish internal melt/routing from external inputs/outputs. Finite numerical guards and residual gates reject the entire tentative tick without changing accepted state. A 256-summary ring and diagnostic digest bound retained history; the FNV digest is not cryptographic authority or a checkpoint protocol.

`U:src/lib/engine/surface-clock.ts` admits one simulation-time stream, keeps integer tick debt plus a sub-tick remainder, and commits a tick only after a synchronous successful solver callback. Intentional holds preserve old debt without admitting held time. Overload rejects a new interval explicitly and requires resume; admitted debt remains drainable. The maximum debt is 2,000 ticks, and a scheduler turn processes a configurable 1–20 steps. This is a work bound, not a frame-time guarantee.

`U:src/lib/engine/surface-coupling.test.ts` actually composes both modules. The first clock callback is commit tick 1 over `[0,dt)` while forcing uses the model's current tick 0. Tick-aligned cold/warm forcing, precipitation and melt produce identical complete model states at 15/30/60 FPS and irregular stutters after draining the same admitted target. Failed solver steps leave both accepted model state and clock tick unchanged with debt retained.

No topology commands, event deduplication/checkpoint protocol, scene/pixel geometry adapter, water-aware bathing eligibility or revision-bound bird effects are implemented in this slice. Those remain required before renderer migration. Catchments are authored partitions; their geometric exposure must be validated by a future adapter, not inferred from these scalar fractions.

## Tests and independent review

The pure experiment passes 33 tests: 13 hydrology, 18 clock and two composition tests. They include dimensional rain/SWE and melt scenarios, exact receiver accounting, sink/overflow conservation, randomized positivity/mass/energy checks, lake-at-rest and dry-sill cases, input permutation, analytic timestep/grid refinement, atomic invalid/overflow rejection, bounded retention, hold/overload/retry, and permanent seeded irregular-cadence checks. These verify this simplified storage law on specified synthetic cases, not arbitrary-terrain accuracy or empirical calibration.

Independent code review [approved the isolated experiment](core-review.md), with no unresolved blocker in this slice. The reviewer caught a real clock boundary defect: compensation retained after snapping a tick could make a later zero-time admission produce negative pending debt. The owner corrected it and added regression tests, including 59/60/1,000-FPS boundaries. Acceptance remains limited to this isolated experimental slice; the live renderer and production gates remain open.

## Reproducible numerical cost

Actual [numerical reference results](numerical-reference-results.json) bind the working-tree solver SHA-256 and use the actual module, not a copied solver. In the two-cell linear case at 60 s, depth errors for `dt=0.05/0.025/0.0125 s` are `5.942e-7/2.970e-7/1.485e-7 m`, with error-halving ratios approximately 2.0002 and 2.0001. Donor limiting stays inactive.

The closed 2 m strip uses exact cell-average initialization and a smaller `dt=0.005 s` to isolate spatial error. At 8/16/32 cells, maximum cell-average errors are `7.957e-6/2.032e-6/5.078e-7 m`; successive maximum-error ratios are 3.9165 and 4.0007. Mean absolute-error ratios are 3.9932 and 4.0201. The temporal contribution is below `4e-9 m` in these cases, measured against the analytical semidiscrete eigenmode. These pass the declared synthetic thresholds, including the 32-cell error below `1e-6 m`. They establish expected first-order time and second-order space behavior for this linear flat reference, not general nonlinear terrain or real hydrological accuracy.

Run in the paired UI checkout using its pinned Node environment:

```sh
node scripts/benchmark-surface-weather.ts core > si-core-benchmark.json
npx --no-install vitest run src/lib/engine/surface-hydrology.test.ts src/lib/engine/surface-clock.test.ts src/lib/engine/surface-coupling.test.ts
```

The [raw receipt](si-core-benchmark.json) identifies Node 24.19.0 on an Apple M5 Pro, macOS arm64. Each case warms up 500 ticks and measures 4,000 ticks (200 simulated seconds at `dt=0.05 s`). The final state includes warmup: 4,500 ticks/225 seconds. Cases use fixed synthetic 2 × 1 m flat grids, 2 mm/hour total water-equivalent precipitation partitioned half rain/half snow, 2 °C and a synthetic 3 mm/(°C·day) degree-day factor. All stores receive exact authored catchment shares and retain their uncapped SWE; no sink or boundary export is configured.

| Grid | 12 × 8 | 24 × 16 | 32 × 32 |
| --- | ---: | ---: | ---: |
| Cells / face edges | 96 / 172 | 384 / 728 | 1,024 / 1,984 |
| Single-step CPU p50 | 0.0718 ms | 0.2235 ms | 0.5980 ms |
| Single-step CPU p95 / p99 | 0.1364 / 0.2248 ms | 0.3240 / 0.4821 ms | 0.8939 / 1.1342 ms |
| Twenty-step burst p95 | 2.3279 ms | 5.3690 ms | 15.5833 ms |
| Twenty-step burst p99 / maximum | 3.7735 / 4.7596 ms | 7.1629 / 7.1790 ms | 17.4013 / 18.0494 ms |
| Sampled heap high-water | 24,304,744 B | 73,339,304 B | 75,042,152 B |
| Post-GC heap delta | 93,976 B | 43,000 B | 41,304 B |
| Process RSS after case | 110,542,848 B | 213,221,376 B | 215,171,072 B |
| Maximum absolute local residual | 2.54e-16 m³ | 8.98e-16 m³ | 2.61e-15 m³ |
| Sum of absolute local residuals | 4.61e-13 m³ | 1.56e-12 m³ | 7.48e-13 m³ |

All three retain 256 diagnostics and end with approximately 0.04625 m³ water-equivalent storage; approximately 0.00025 m³ is added precipitation and 0.00003125 m³ melts internally over the full run. Per-step residual and cumulative residual are different diagnostics; small signed final cancellation does not erase the reported absolute residual sum.

These measurements cover pure core validation/updates, immutable state, ledgers, current-step receipts and bounded history. They exclude the browser, renderer, GPU, other yard work, scheduler integration and physical mobile devices. Samples run sequentially on this Mac with other applications present. Heap is sampled once per burst and includes benchmark buffers/runtime allocation; process RSS includes the VM and is not model-only memory. Post-GC deltas are not a leak test. Repeated runs vary: an earlier largest-grid burst p95 was about 17.5 ms. No universal performance threshold is earned by choosing the faster receipt.

The largest 20-step burst can exceed an entire 60-Hz frame before drawing. Keep this experiment outside the live renderer, begin integration with a bounded smaller domain and smaller scheduler budget, and measure full-scene frame/CPU/memory behavior on identified target devices. The 1,024-cell admission ceiling is a correctness/resource ceiling, not a release recommendation.

## Remaining gates

The architecture's authored scene/catchment geometry, event/topology/checkpoint authority, wet/revision-bound bird contact, versioned adapter, actual Pixi/SVG rendering and device qualification gates remain open. The current live snow/rain controls continue to use the explicitly labeled dimensionless visual prototype. No production migration, saved-yard mutation, new bird action or deployment occurred.
