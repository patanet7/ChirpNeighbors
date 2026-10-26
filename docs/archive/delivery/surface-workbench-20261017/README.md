# Surface workbench engineering checkpoint

**Public checkpoint / current WIP:** The 33/97-test runs, code review, screenshots
and benchmark receipts below describe their recorded pre-integration source scope;
they do not certify the modified withdrawal/runtime/renderer work. A fresh focused
run passes 114 tests in 13 files and Svelte checking reports zero errors/warnings;
independent review and current browser acceptance for that integration are still
pending. This is a preservation checkpoint, not production approval.

Public text logs and test JSON in this directory are redacted copies: personal
checkout/home paths use portable placeholders. Complete originals are preserved
privately outside Git. Test outcomes remain retained, but these public copies are
not byte-for-byte raw originals. No local database, credential or backup payload
is included. The dated isolated-core receipt retains its original source hashes.

2026-10-17. This checkpoint measures and characterizes the existing local `/art-lab` prototype. It does **not** accept a physically calibrated water/snow model. The [canonical architecture proposal](../../../architecture/surface-weather-model.md) owns the proposed SI-unit replacement and its acceptance gates.

## Reproduce

In the paired `birdsong-yard-sprites` checkout, use its pinned Node 24.19 tool environment:

```sh
node scripts/benchmark-surface-weather.ts > prototype-benchmark.json
npx --no-install vitest run src/lib/engine/water.test.ts src/lib/engine/surface-weather.test.ts src/lib/engine/surface-model-characterization.test.ts src/lib/engine/renderer-resources.test.ts src/lib/engine/scene-resource-budget.test.ts src/lib/workbench/production-plan.test.ts src/lib/workbench/runtime.test.ts src/lib/gallery/catalog.test.ts
```

The benchmark launcher uses the already installed, locked esbuild to bundle browser-model imports into an isolated temporary directory, runs that bundle in Node with explicit garbage collection, and removes the temporary bundle. No external service or new dependency is needed.

## Measured scope and cost

The [raw machine-readable receipt](prototype-benchmark.json) identifies Node 24.19.0 on this Apple M5 Pro, macOS Darwin 25.6.0 arm64. Each case warms up for 500 samples, then measures 4,000 samples at 20 Hz: 200 supplied/water seconds and approximately 2,400 separate stylized snow seconds at speed 12. Full snow/rain intensities run simultaneously as intentional stress inputs with alternating cold/warm setpoints; this is not a physically partitioned storm or unified simulation clock. Timing covers snow surface extraction, both model updates, impact handoff and water/snow rectangle generation. It excludes the browser, Pixi geometry upload/drawing, layout, GPU time, other yard simulation, and total application memory. These are logical compact/crowded workloads on the same Mac; neither is a physical mobile-device measurement.

| Workload | Compact | Crowded |
| --- | ---: | ---: |
| Objects / synthetic contact actors | 4 / 8 | 12 / 96 |
| Water cells / retained snow surfaces | 96 / 16 | 96 / 24 |
| CPU sample p50 | 0.0418 ms | 0.1063 ms |
| CPU sample p95 | 0.0922 ms | 0.1543 ms |
| CPU sample p99 / maximum | 0.1576 / 0.6761 ms | 0.1981 / 0.7089 ms |
| Mean measured loop time | 0.0518 ms | 0.1152 ms |
| Maximum water / snow rectangle count | 317 / 63 | 321 / 117 |
| Maximum retained effects | 32 | 32 |
| Post-GC heap delta | 42,120 bytes | 67,152 bytes |
| Sampled heap high-water mark | 12,575,576 bytes | 14,008,720 bytes |
| Process RSS after case | 82,804,736 bytes | 102,645,760 bytes |

Actor inputs deliberately repeat occupied bath anchors to stress bounded effect admission; they are synthetic contact load, not a valid 96-bird slot-reservation simulation. Grid resolution is fixed in the prototype, so these measurements establish no resolution-scaling or convergence result. Cases run sequentially and the Mac was running other work. Timings vary with contention/JIT/GC and one receipt is not a confidence interval or device qualification. Heap is sampled every 64 iterations, not continuously; post-GC deltas include benchmark sample buffers/runtime caches. RSS includes the whole Node process and retained VM pages. Neither metric proves absence of leaks. A browser/mobile/GPU performance gate remains open.

## Tests and engineering limits

The [recorded pre-integration focused aggregate](focused-tests-final.txt) passed **97 tests in 11 files**: the 64 prototype/workbench/gallery/resource tests below plus 33 SI-core, shared-clock and composition tests. Its recorded Svelte check had zero errors/warnings; scoped ESLint, strict native tooling, formatting and production build passed for that checkpoint. These results do not certify modified integration code or turn the broader recovery/SMTP suite green. See the [isolated SI checkpoint](si-core-checkpoint.md) and [independent code review](core-review.md) for their precise source scope.

The [focused run](focused-tests.txt) passes 64 tests across eight files. Seven new tests in `U:src/lib/engine/surface-model-characterization.test.ts` distinguish invariants from known limitations:

- A level wet/dry lake remains at rest over the synthetic terrain.
- Twenty-four deterministic randomized initial states and forcing schedules remain finite/nonnegative and balance relative input/output within 1e-9 units.
- Matching forcing at 15/30/60 calls per second gives identical fixed-step water arrays and accounting.
- Repeated render-only samples do not mutate water state.
- A one-second stutter admits only five water ticks versus twenty smooth ticks. This records dropped time; it does not approve that clock policy for the replacement.
- Saturated snow stops recording additional precipitation, and deleting objects removes stored cover without an export ledger. These known deficits remain reproducible.
- Identical ground melt receives a different normalized liquid signal when empty objects change total visual capacity. This proves the existing coupling is not an absolute water-equivalent transfer.

The current model has no physical cell areas, SWE, precipitation depth units, authored terrain drainage or bath reservoir. Relative accounting passes cannot satisfy the proposed physical mass ledger. Snow caps, removal, interception, topology and a shared conserved clock must be addressed in the replacement. Physical-unit scenarios, grid/timestep refinement, exact snow-to-water transfers, overflow routing, bath storage and analytic reference gates are specified in the architecture proposal and are **not implemented/passing** here.

The broader repository quality run remains non-green: 32 failures across recovery/SMTP suites, including unavailable atomic no-replace publication on this Mac, private reference-directory behavior and SMTP peer timing. Existing Python 3.12 eliminated the earlier Apple Python SQLite serialization incompatibility but not those failures. No unrelated suite code was altered. Focused checks, typechecking and a production build are separate evidence and must not be described as a full green quality run.

## Live preview

Local yard: `http://127.0.0.1:5187/`; art/engine lab: `http://127.0.0.1:5187/art-lab`; species gallery: `http://127.0.0.1:5187/gallery`. Development Alice/Bob fixture access is required. This fixture environment uses isolated local storage and no live provider/hardware input. Server remains running for exploration. In the enclosing task directory, `.chirp-tools/chirp status`, `.chirp-tools/chirp dev` and `.chirp-tools/chirp stop` control only this app's documented controller. The launcher log is `.chirp-runtime/dev.log`.

The live page explicitly labels dimensionless water, pixel snow, normalized visual melt and blocked production acceptance. Browser verification found those labels, a live Pixi yard and no warning/error logs in the verification tab. This supplements earlier navigation, saved fixture placement, layer toggles, hold/replay and responsive-layout checks; it does not prove physical hydrology or end-to-end bathing animation.

![Live prototype status and controls](prototype-status.jpg)

## Independent review and remaining evidence

### Independent design review and isolated-core experiment

An independent skeptical engineering review accepted the
[surface-weather specification](../../../architecture/surface-weather-model.md)
for a bounded pure-core experiment after resolving dimensional/numerical and
bounded-lifecycle questions. The fixed-conductance law has consistent units;
snapshot equal-and-opposite transfers, its fixed-G step bound and the analytical
gates are a defensible testable first slice. The accepted design explicitly avoids
claiming shallow-water momentum physics or physical calibration.

Exact review verdict: “Approve revised surface-weather-model.md as a proposed
specification for bounded pure-core implementation/tests only; no remaining design
blocker from independent review. Approval does not establish implementation success,
renderer/gameplay integration, physical calibration, device qualification or
production acceptance.” The separate actual-code verdict is retained in
[core-review.md](core-review.md): approval for the bounded fixed-domain experiment
after clock-boundary and strict numerical-guard repairs, with no unresolved blocker
inside that scope. The review independently reran the 33 focused tests and records
additional synthetic probes and exact hashes; it does not approve live integration.

Review changes specified finite overflow DAG handling, exact tick/event ordering,
bounded applied-event receipts, geometry-revision/wet-bowl effect checks, exact-cell-
average numerical references, local versus run residual gates and bounded backlog/
diagnostic retention. This is **specification review**, not a passing code review,
physical validation or authorization to enable the model in the live renderer.

The separately authorized pure experiment now passes 33 focused tests: 13 fixed-
domain hydrology, 18 clock and 2 actual module-composition replay/rejection tests.
Run `npx --no-install vitest run src/lib/engine/surface-hydrology.test.ts src/lib/engine/surface-clock.test.ts src/lib/engine/surface-coupling.test.ts`
with the same pinned Node 24.19.0 environment. The [raw SI-core benchmark](si-core-benchmark.json)
measures separate 96/384/1,024-cell synthetic workloads. At 1,024 cells the 20-step
burst p95 is 15.5833 ms and maximum 18.0494 ms before rendering; no default burst
size is qualified as a release frame budget. The [isolated-core checkpoint](si-core-checkpoint.md)
and [actual numerical reference results](numerical-reference-results.json) retain
the experiment's test/performance evidence separately from this prototype section.
Independent code review approved the isolated scope; topology edits, event
deduplication, checkpoint protocol, authored scene
adapter, availability-aware bird behavior/effects and UI migration are not completed.
The existing prototype and all earlier measurements above retain their original
scope. Passing isolated core tests does not replace or physically validate `/art-lab`.

The recorded pre-integration aggregate passed **97 tests in 11 files** (the 33
pure-experiment tests plus the preceding 64 focused checks). That application check
reported zero errors/warnings; scoped ESLint and the native TypeScript aggregate passed. This
does not turn the separately recorded broad recovery/SMTP failures into a full
green repository quality run. The independent review and refreshed source digests
bind the final 18-test clock revision.

The separate [raven production report](../raven-production-20261017/README.md) is now
materialized locally and read in full. Its full original and private identifiers
are preserved outside Git; the public copy is explicitly redacted and has its own
byte count/hash distinct from the original-source hash. Reusable extraction,
registration and review lessons are reconciled
into PB-021-B and paired UI animation inventory. Its final atlas and optional archive
were not downloaded/validated here. ChatGPT pet layout/lifecycle, mascot art and
reported measurements remain separate from Chirp species contracts, rights and
animation admission; report access is not species-art acceptance.

## Next authorized opt-in integration — verification pending

The [bounded SI renderer/actual-slot checklist](renderer-integration-checklist.md)
records the newly authorized extension. It requires a fresh source-bound review,
withdrawal/slot/controller tests, actual rendering and hold/move/removal preservation
evidence. None of the prior 33/97-test or independent-review claims automatically
covers changed core withdrawals, renderer, simulation seams or local controller.
The source-hashed isolated-core receipt above remains its historical checkpoint;
live integration must earn and record its own verification.
