# Measured renderer performance — local checkpoint

> Historical checkpoint: task/checklist statuses and local-only instructions below describe the recorded source revision. Preserve this evidence; current remaining work, dependencies and acceptance live in the [PB/EN task index](../../delivery/product-behavior-and-ideas.md), including its architecture follow-up.

The selected implementation reuses bounded immutable bird geometry and preserves Pixi automatic batching. It reduces measured rectangle construction and synchronous render duration. Frame-time results remain workload-dependent; this checkpoint does not claim a universal frame-rate improvement.

The preserved resource checkpoint is main `706d878be756aef1f474bbebfcf8c2b21022bf0d` / UI `fe1eb18845220b6cd059be639ce2e0d8455b13b0`, with its original [80-gate report](LOCAL-EVIDENCE.md). Both current local branches retain the user-specified published review commits as ancestors. The new implementation and evidence are local; artwork, providers and private owner storage are unchanged.

## Concrete dependency and acceptance checklist

PERF-01 through PERF-07 are complete for this bounded local slice. Remaining product and performance work is listed below.

| ID | Task | Depends on | Acceptance |
| --- | --- | --- | --- |
| PERF-01 | Preserve source and measure actual work | E-RES | Exact baseline preserved; ordinary 3/12, legacy dense 96, valid dense geometry and oversized surface measured at DPR 1/2. Actual owner components separately cover 3/12/96 saved residents. Inputs, admissions, backend, backing pixels, warmup, sample arrays and source fingerprints retained. |
| PERF-02 | Reuse immutable sampled geometry | PERF-01 | Renderer-local version/frame/pivot cache, explicit leases, unused-entry eviction and version retirement. At most 256 contexts and 65,536 rectangle commands. Existing admission, timing, transformations, hit testing and quality preserved. |
| PERF-03 | Separate optimization effects | PERF-01 | Original, cache-only, batching-only and combined variants use the same scenarios. Six predeclared balanced blocks compare the oversized DPR 2 surface, with trial-level paired uncertainty. Forced batching is retained only as an experiment; no unmeasured size policy is selected. |
| PERF-04 | Prove exact behavior and pixels | PERF-02 | 65 fixed-ticker state/image pairs, 67,179,016 decoded pixels per comparison, zero differences. Coverage includes seeded species scales, waiting transitions, pivots, mirrors, rotations, fractional sizes, DPR, contacts, depth, fallbacks, replacement and concurrent ownership. |
| PERF-05 | Retain both gains and regressions | PERF-03, PERF-04 | Complete original/final matrices and four-arm follow-up retained. Synchronous render duration, sampled GC, rAF pacing and nested native spans remain separate measurements. No quality/admission reduction or mobile extrapolation. |
| PERF-06 | Freeze complete verification | PERF-02, PERF-04, PERF-05 | Complete 81/81 frozen gates pass; 1684 UI tests / 105 files and 19 tooling tests; counts and exact sources below. |
| PERF-07 | Reconcile evidence and remaining scope | PERF-06 | Exact tested revisions, file hashes, audit dispositions and source inventory retained. GAP-03 and STATIC-03 remain explicitly open. |

## Implementation and tradeoffs

`SharedGeometryCache` uses the existing sampled geometry key, including asset identity, exact pin/status, registry revision, frame and pivot. Matching residents and returning frames share immutable ordered vector instructions. Asset replacement retires prior entries; active users keep leases until their display objects switch. Renderer teardown releases its own geometry without destroying another renderer's global Pixi resources. The renderer also disposes its private shadow and ring contexts explicitly.

Unused frames stay resident within the entry/rectangle budgets, trading bounded retention for less repeated construction and garbage collection. These source-command limits are not byte-level heap or GPU-memory guarantees. The historical `birdGeometryBuilds` counter still counts resident frame assignments; `geometryCache.builds` counts actual shared-context construction. The two must not be confused.

The existing scene limits remain: 96 presentation candidates, 32,768 reserved primitive units, and 262,144 retained decoded rectangles per registry. Canvas backing edges remain at most 4,096 pixels, total backing pixels at most 4,194,304, and DPR at most 2. Component and renderer registries are separate; these counters do not bound all saved data, transient parsing, tessellation, font atlases, total heap or VRAM. The [prior resource acceptance](scene-resources-20261010.md) defines that scope; this slice does not tighten admission or reduce resolution to improve its measurements.

## Measured outcome and selected policy

The selected change is **cache-only with existing automatic batching**. The [matched engine/component comparison](LOCAL-EVIDENCE.md) retains all original/final timing rows, inputs and profiles. Synchronous `app.render` elapsed time per counted render falls from 0.824 to 0.518 ms (12 residents), 4.667 to 1.237 ms (96), and 22.554 to 1.023 ms (valid 3,000-rectangle geometry stress). Draw submissions stay 28/196/24. The wrapper measures elapsed synchronous render work; it is distinct from V8 samples, native spans and hardware CPU counters.

Frame pacing is mixed. Original/final pooled p95 is 166.6→150.1 ms for direct dense96 at DPR2, 266.6→250.0 for geometry stress, and 416.7→449.9 for oversized DPR2. Ordinary tails are largely unchanged; the actual seeded owner component with 96 saved residents is 166.6→166.7 ms with the same 40 visible / 56 waiting initially and 44/52 afterward. Timing comparisons do not imply identical real-rAF trajectories because the existing simulation delta clamp remains in place.

The [bounded four-arm follow-up](LOCAL-EVIDENCE.md) separates baseline, cache-only, batching-only and combined effects. Historical ordinary12/dense96/geometry subsets retain two repeats per DPR and separate profiles. The stronger oversized DPR2 comparison uses six predeclared balanced blocks, fresh storage/server/browser/context for each trial, 120 intervals after 2 s warmup, and exactly 24 trials. All 72 initial/before/after resource snapshots retain 96 candidates → 10 visible / 86 deferred / 0 waiting and 2747×1526 = 4,191,922 backing pixels.

| Oversized DPR2 paired trial-p95 contrast | Mean difference | Descriptive 95% block-bootstrap interval | Six signs |
| --- | ---: | ---: | --- |
| Cache-only minus baseline | −19.4ms | [−47.2,+2.8]ms | −,−,+,0,+,− |
| Batching-only minus baseline | −138.9ms | [−158.4,−119.5]ms | All six negative |
| Combined minus baseline | −13.9ms | [−61.1,+33.3]ms | Three negative, three positive |
| Combined minus batching-only | +125.0ms | [+75.1,+174.9]ms | All six positive |

The earlier cache surface regression was not consistently reproduced; the primary interval crosses zero, so neither equivalence nor a general tail gain is established. Cache-only secondary median/mean intervals improve in all six blocks. Batching-only's surface-tail gain is retained, but historical dense DPR 2 p95 worsens 166.6→200.0 ms, ordinary 12 DPR 1 p95 worsens 50.1→66.6 ms, and synchronous packing work rises despite fewer draws. The combined effects are not additive. This supports retaining the cache's geometry-work reduction with original batching, not a blanket forced-batch change or an unmeasured surface/size policy. No outcome-driven extra trials or tuning were performed.

The bootstrap enumerates 46,656 resamples of **six paired block contrasts**, not 2,880 independent frames. Six sequential blocks can retain time/load dependence and understate tail uncertainty; these are descriptive intervals, not significance or hardware-generalization claims. All timings use Vite **development mode**, Chromium 151.0.7922.173, WebGL2 ANGLE/Vulkan SwiftShader, Linux AMD EPYC with 4 CPU quota and 16 GiB limit. Production-build correctness is separately tested below; production-build performance and physical GPUs are unmeasured.

[Four-arm visual review](LOCAL-EVIDENCE.md) proves exact fixed-ticker state and decoded pixels separately. Every variant matches the baseline through 65 captures and 67,179,016 compared pixels with zero differences, including seeded scales, waiting transitions, transforms, contact/depth/hit state, replacement/fallback and concurrent ownership. This is fixture correctness, not biological fidelity.

## Verification and evidence

The fresh complete [integration report](LOCAL-EVIDENCE.md) passes **81/81 gates**, finished `2026-10-10T06:04:40.963710+00:00`, at clean frozen main `2792f19b9bd84fff00bd322faa35f7b8d4575421` / UI `a5cf659b3f8f81a1ca3560ea5cf1333c795c289b`. [Derived counts](LOCAL-EVIDENCE.md): **1684 UI tests in 105 files**, 19 tooling tests, **1357 recorded assertions across 34 browser/HTTP reports**, plus 55 local auth assertions. Groups overlap and are not summed into a unique-test total. Strict types, typed lint, supplementary official local Svelte analysis, formatting, production build, manifest/import/resident/privacy/weather/arrangement/arrival and renderer/browser gates pass. The 17 new geometry tests are included, not added to the UI total.

The integrated mechanical Pixi gate passes independently of a cross-revision baseline. The retained separate before/after candidate proof passes 393 checks across 65 exact state/image pairs; baseline repeat and both batching variants also pass their own parity runs. Performance evidence is separate from correctness gates: matched original/final lanes contain 212 checks, 52 timed trials, 6,240 intervals and 12 profiles; the two intermediate subsets remain separate. The new batching-only/surface follow-up adds 239 checks, 36 trials, 4,320 intervals and 3 profiles. All favorable and unfavorable results, early harness failures and source bindings remain in the hashed [raw evidence manifest](LOCAL-EVIDENCE.md).

The first 81-gate attempt was deliberately interrupted after 10 passing gates to run the requested bounded comparison; its [unfinished report](LOCAL-EVIDENCE.md) and interruption record are retained and are not called a pass.

The subsequent [r2 attempt](LOCAL-EVIDENCE.md) recorded 65 passing gates and one recording-UI failure before being stopped at 66 recorded gates. Real cookie removal produced 401 and the session guard legitimately unmounted the Refresh button during Playwright actionability; the test now dispatches that optional click atomically and keeps every expiry/private-content assertion. The [independent repair review](LOCAL-EVIDENCE.md) and [34/34 focused result](LOCAL-EVIDENCE.md) are retained. Production code was unchanged by this repair.

The complete frozen [r3 attempt](LOCAL-EVIDENCE.md) then passed 80/81 gates, including recording expiry and the mechanical renderer gate, but failed an immediate mobile scroll-centering read after viewport resize. A seven-line test-only change waits at most five seconds for the same connected scroll element to satisfy the unchanged centering predicate and tolerance. It does not write scroll state or suppress failure. The [shape repair review](LOCAL-EVIDENCE.md) and [focused full shape journey](LOCAL-EVIDENCE.md) retain the result. Its first preflight correctly refused a dirty checkout before any browser journey; the focused run used the committed repair. The fresh r4 run above is the complete pass; no earlier attempt is counted as one. The earlier complete 80-gate resource checkpoint remains unchanged.

[Independent factorial review](LOCAL-EVIDENCE.md) reconciles 24 ordered reports, 72 resource snapshots, all 2,880 raw intervals and 18 paired contrasts. Twenty corruption/arithmetic controls pass. The measured driver remains SHA `ffa53f3707303390391e91850596c9528e536d9b756c2b87ec1a3f62fb837925`; the committed guard-hardened helper is SHA `10fcee0b81d0c1ed0819ea7c39e3843cee86e3b6eb4d8753023d1cbd2ae96c08`. Its [exact diff](LOCAL-EVIDENCE.md) adds evidence guards/analysis identity after measurement; original timing and statistic code remain unchanged. Reanalysis reproduces every original metric/contrast, while recording its distinct analysis hash. The shared benchmark library remains SHA `08e32b4865f13f13afcfab417f6e7b8f814491d45b0075f312e798a5176a8ee5`.

These are tested source revisions. Later local delivery commits contain documentation/evidence only and do not retroactively change the revisions recorded by the frozen run. [Final archive/count review](LOCAL-EVIDENCE.md) reconciles the retained artifacts and final scope.

## Remaining work

GAP-03 remains partial: large surfaces, software rasterization and some dense-yard tails remain slow. Approved species art, actual mobile GPU testing and production-build performance measurements remain unavailable/unperformed. A texture/atlas path could reduce vertices and submissions, but needs its own exact rotation, fractional-scale, edge-coverage, lifetime and memory acceptance. Viewport scissoring/tiling also needs exact-output and lifecycle proof; this slice neither crops the surface nor drops additional birds.

The actual Svelte component profiles do not identify a dominant duplicate-render loop: explicit update-triggered renders cost only about 1.8/2.4/10.2 ms over the separate five-second 3/12/96-resident baseline windows. Existing clock/weather updates and diagnostic refreshes remain unchanged.

[STATIC-03 exact inventory](LOCAL-EVIDENCE.md) now records **527 active source files: 459 UI + 68 main**, including the new comparison helper. It remains open: 45 handwritten JS/MJS files have recommended lint but no broad static types; 37 UI Python files lack strict mypy (four recovery tools are typed); seven nonempty backend tests lack strict mypy; `src/app.d.ts` and six generated validator declarations retain `skipLibCheck` internal-check limits; six generated validator JS files use drift/runtime guards; two experimental simulator Python scripts lack configured static gates. Three unsupported legacy and nine empty historical exclusions are separately identified. Applicable scopes are 360 compiler TS/Svelte inputs plus 7 declarations, 367 typed-lint plus 45 JS inputs, and 56 Ruff targets; these overlapping file counts are not test totals. No environment/proxy cause or universal static-coverage claim is made.

The 55-entry audit register remains 34 resolved, 6 justified, 1 partial (GAP-03), 1 directly implementable (STATIC-03), 13 blocked/unselected/mixed. This slice refreshes only the two affected entries and preserves prior per-entry review; it does not claim a fresh individual rereview of all 55 findings or all 75 Svelte advisories.

All sprites are fixtures. Providers, real generation, approved concept pixels, biological fidelity, the original unavailable worker, board/toolchain validation and publication remain outside this bounded local result. Existing privacy/import/resident/weather/arrangement/arrival layers and saved owner data are preserved.
