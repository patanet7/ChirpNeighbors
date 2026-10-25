# Whole-scene resources and PNG recovery — verified local checkpoint

> Historical checkpoint: task/checklist statuses and local-only instructions below describe the recorded source revision. Preserve this evidence; current remaining work, dependencies and acceptance live in the [PB/EN task index](../../delivery/product-behavior-and-ideas.md), including its architecture follow-up.

**80/80 frozen gates pass**, finished `2026-10-10T02:54:09.715007+00:00`, with clean unchanged source revisions:

- Main: `2928fecb551b15fda133fbc356d90b47b2232cf5`
- UI: `5f9507ddaa624f9e12dcf04c984ebdf5c9b19660`
- [Full report](LOCAL-EVIDENCE.md), SHA-256 `8ceb7be23f17188d41ca1522f408c8d34feec0f5896c8e2f194219215eb87880`
- [Derived counts](LOCAL-EVIDENCE.md): 1667 UI tests across 103 files, including 26 new resource tests; 19 tooling tests; 1106 assertions across 33 browser/HTTP reports; 55 additional local auth assertions. Overlapping focused checks are not added as unique tests. All 79 preceding gates remain, plus `browser-resources`. Execution took 1687.56 gate-seconds.

Branches remain local `codex/scene-resource-local`, preserving the previous main `10f5dd28a9636f897b19f60d52eea5378e0f2b9f` / UI `375ee15869491f934cccb67c52865848073eb399` checkpoint. No push, PR, remote merge, deployment, provider connection, credential change or spend occurred. Existing real owner data was not used or deleted. UI documentation commit `fe1eb18845220b6cd059be639ce2e0d8455b13b0` follows the tested source without implementation/test changes; this main evidence record is also subsequent documentation.

## Completed work and acceptance

| Task | Code and observable acceptance | Evidence |
| --- | --- | --- |
| Shared scene admission | Pixi and SVG use the same stable membership. At most 96 candidates are resolved/simulated; selected and active-arrival birds have priority. All saved birds and controls remain. | [UI checklist](https://github.com/patanet7/birdsong-yard-sprites/blob/main/docs/scene-resource-budget.md), policy/renderer tests, [18 resource assertions](LOCAL-EVIDENCE.md). A 100-resident yard keeps all 100 controls: 96 actors, 36 views, 60 waiting, 4 deferred. |
| Geometry and lifecycle limits | Reserve every manifest's largest frame and complete decoded-frame count; registry fallback/version replacement remains. Waiting actors own no bird Graphics/Text/container; eviction/destruction releases owned state. | Exact primitive and retained-frame boundaries; 7 dense assets admitted/23 deferred; three actual Pixi teardown cycles balance views and clear graph/cache/canvas. |
| Bounded canvas and existing behavior | Backing edge ≤4096, pixels ≤4194304, DPR ≤2. Host CSS and opaque-pixel hit mapping remain correct after large resize. Existing visible held arrivals are not replayed. | Actual oversized resize/pointer/visibility tests; existing 84-resident ontology, weather, arrangement, arrival and fallback suites all pass. |
| PNG list recovery, GAP-01 | Separate accessible loading/empty/error/retry states; cancellable generation-fenced reads. Retry preserves draft, preview, independent review errors and mutation IDs. Stale owner responses and disposed continuations cannot restore private UI. | [45 PNG assertions](LOCAL-EVIDENCE.md), including 10 added checks. |
| Honest tooling and audit | Official local Svelte analyzer: 30 files, 0 issues, 75 individually reviewed advisories. All 14 changed YardScene advisory rationales/evidence were independently rereviewed. | [Advisory review](LOCAL-EVIDENCE.md), fresh passing integrated analyzer and CSS gates; [final independent review](LOCAL-EVIDENCE.md). |

Implementation commits: UI `ad38f8d97f7aecb0cbf5d1dd5ca11451afbe5b08`; harness corrections `e45b899bbc02298f2388d1996ffff9a7c4aa1f96` and `5f9507ddaa624f9e12dcf04c984ebdf5c9b19660`. The main source commit wires the additional gate into the aggregate/matrix and retains the initial reconciliation.

## Findings and remaining tasks

The [initial reconciliation](LOCAL-EVIDENCE.md) retains all 55 register entries (original 44 plus 11 tooling entries), all 75 advisory rationales and all 36 authoritative requirements. Initial dispositions were 33 resolved, 6 justified no-change, 3 immediately implementable and 13 dependency/unselected/mixed entries. The [final disposition record](LOCAL-EVIDENCE.md) is:

- **34 fixed/resolved** entries, including GAP-01; this includes code, tooling and documented resolution, not 34 product defects.
- **6 justified no-change** advisory/scope entries, with individual rationale preserved.
- **1 remaining directly implementable entry:** STATIC-03, targeted static coverage of handwritten declarations, tools/harnesses and experimental Python scripts.
- **1 partial entry:** GAP-03's resource limits now pass; worst-case animation smoothness and device/real-art performance acceptance remain open.
- **13 dependency/unselected/mixed entries:** sound/design/licensing, species art/biology, ESP32 production auth/TLS/hardware, real inference/import/weather/future providers, original worker integration, operating/erasure policy, unselected progression/certification and live auth/mail. These are not all technically impossible; local subparts can be selected independently without claiming the broader outcomes.

The **75 Svelte advisories are not 75 unresolved defects**. They retain per-occurrence reasons and source hashes; no blanket suppression or refactoring for a zero-suggestion count was applied.

Next bounded tasks: profile active geometry/render work and set performance targets; extend STATIC-03's exact coverage inventory; integrate the original worker only when its authorized source is available. The original `c08624d3` is absent from both Git object databases and both approved transfer directories are empty. [Worker state evidence](LOCAL-EVIDENCE.md) retains the already-failed authorized transfer. No replacement scheduler or blocked transfer retry was attempted.

## Limits and retained failures

Engineering bounds are 96 presentation candidates, 32768 reserved primitive units, and 262144 retained decoded rectangles **per registry**. Text is an object count, not a font atlas byte estimate. Transient candidate parsing, source entries, complete saved lists/DOM controls, tessellation and total heap/VRAM remain outside these counters. Component and renderer own separate registries. Stable admission is selection driven; it does not promise automatic rotation or a physical place for every admitted bird.

**Heavy active stress is slow:** the integrated software Chromium sample measured **199.9 ms p95**, and the focused run **216.6 ms**, over 30 frame intervals with seven deliberately dense assets on an oversized canvas. These results establish no smooth-playback or 60 FPS claim. Quiet desktop/mobile samples have stopped tickers and are not animation throughput measurements. Physical-device and approved-art acceptance remain unverified. Tests duplicate existing fixture rectangles; no new art, biological fidelity or approved-reference viewing is claimed.

The retained attempts distinguish failures from final proof: initial compiler rejection of a stale narrowed visibility comparison; expected stale advisory hash before individual review; PNG r1 missing actual session-binding headers in fault injection; PNG r2 ambiguous navigation selector. R2 also received a late test-helper assertion during execution and is not frozen evidence. The corrected PNG r3 passes 45/45; resource r2 passes 18/18; then the full unchanged 80-gate run passes. [Focused review](LOCAL-EVIDENCE.md) and raw focused logs remain alongside the integrated evidence.
