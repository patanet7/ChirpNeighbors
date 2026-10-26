# Verified environment animation checkpoint — 2026-10-09

The complete **75/75 strict gates passed** on clean, unchanged sources at
2026-10-09T18:12:10.904706+00:00, with 1,645.54 seconds of gate execution.

- Main tested: `8a7a4f078d838a0fb07f8ed62c3d28bb4b3f2916`.
- UI tested: `a6da5e9b415bc3a122a38985a1c8d408d0f77b4f`.
- [Full report](LOCAL-EVIDENCE.md), [counts](LOCAL-EVIDENCE.md), gate logs and browser/HTTP reports are retained. The report SHA-256 is `046cefee4f248cf4314ef86e79a158fa1bf3c760524f05619c5e976ad7886991`.
- Both local branches are `codex/environment-animation-local`. The prior clean ontology checkpoint remains at main `32a7f2d837b6b56424470646475fe8017ca1d931` and UI `81e7a890cbda3f1245f847be7056a42b42a7ff21` on `codex/behavior-ontology-local`.

## Completed tasks and acceptance

| Task | Dependencies and verified result |
| --- | --- |
| Versioned environment state | Existing saved weather clock/settings; additive strict v1 preview/frame schemas, pure explicit-time resolution, continuous visible solar motion and lighting, pre-epoch/midnight handling and neutral unconfigured providers. Persisted weather/yard/backup contracts remain unchanged. |
| Shared renderer playback | Existing Pixi elapsed time and scene layers; separate smooth hour/effect interpolation, interrupted fades, deterministic clouds/rain/snow/fog/wind, shared SVG geometry/colors, bounded 20Hz sampling and at most 154 rectangles within the 160 cap. Lighting does not rebuild bird pixels. |
| Owner controls and accessibility | Temporary preset/hour/effect/transition controls, seeded effect restart, queued edits while paused, static reduced motion and explicit edits, held hidden state and smooth resume. Leaving/reloading resets previews; no saved layout or shared projection writes. GPU loss holds the current blended frame across automatic clock updates. |
| Bird behavior and explanation | Existing traits, capability, occupancy and routine queues; actual blended effect strengths drive hysteresis, night rest, quieter dusk/fog and adverse-weather activity restrictions. Compatible fitting roofed feeder seats are preferred with safe, explained fallback. Arrival cancellation/settlement, capacity, FIFO recovery and legacy phase-only callers remain covered. The workbench exposes applied rules and illustrative/unvalidated provenance. |
| Actual browser and strict regression proof | 47/47 environment assertions in both the dedicated completed run and full suite, actual changed pixels, desktop/320px screenshots, video samples, phase/seed replay, public/account isolation, fallback and every prior gate. [Independent source/evidence review](LOCAL-EVIDENCE.md) preceded the final checkpoint. |

The [implementation checklist](https://github.com/patanet7/birdsong-yard-sprites/blob/main/docs/archive/environment-animation-checklist.md)
records dependencies and concrete acceptance; the [authoritative task index](../../delivery/product-behavior-and-ideas.md)
retains 36 stable entries, including PB-023/PB-024. The [visual audit](https://github.com/patanet7/birdsong-yard-sprites/blob/main/docs/archive/environment-visual-audit-20261009.md)
identifies inspected images, numeric comparisons and limits.

## Verification and preserved attempts

The aggregate passes **1,564 UI tests across 98 files**, including **45 new tests**:
16 environment contract/resolver, 18 behavior, 10 visual/playback and one workbench
diagnostic case. Type checking reports zero errors/warnings; typed lint, formatting
and a fresh production build pass. Canonical checks pass 429 cross-language goldens,
12,724 mutations, 866 source-valid inputs, 235 unchanged semantic exceptions,
201 structural digests and 678 Python-authoritative boundary cases. The inventory
covers 52 HTTP/SSR operations and 94 boundaries with 24 explicit residual gaps.
Independent review approved only four additive mirror digests; all 197 old digests
remain unchanged. The exact two Python corpus allowlist additions do not relax validation.

All 32 retained browser/HTTP reports pass, with 1,063 recorded assertions across those reports. The new gate independently measures
rendered pixels in an empty yard before adding fixtures. Actual [dawn transition](LOCAL-EVIDENCE.md),
[rain/snow crossfade](LOCAL-EVIDENCE.md),
[320px controls](LOCAL-EVIDENCE.md),
[workbench explanation](LOCAL-EVIDENCE.md)
and [captured SVG fallback](LOCAL-EVIDENCE.md)
are retained with the full run. The dedicated r4 evidence additionally retains
45 screenshot PNGs, three extracted video frames and two WebMs.

[Earlier attempts](LOCAL-EVIDENCE.md) remain complete as
recorded: r1 reached 41/42 before a real navigation reset defect; r2 reached 43/44
before reading hidden disclosure text; r3 reached 36/37 before an unmeasured fixed
resume-time bound. The reset now eagerly tracks navigation, status assertions open
the panel, and resume checks capture the visibility event, first held 20Hz sample
and actual browser-active interval. No failed or incomplete run is counted as a pass.
The existing sleep gate now starts at manual clear noon to isolate sleep/wake from
an unrelated simultaneous storm fade; all its assertions remain. Focused type/lint,
corpus and oversized-fixture test corrections are retained too.

The tool connection refreshed during aggregate execution. The running verifier,
commits and temporary evidence survived; the final report confirms all 75 gates
finished with unchanged hashes and clean worktrees. It was not substituted with
combined partial results.

## Remaining limits and next work

- All pixels remain existing technical fixtures. Approved species references/art,
  rights review and photo-to-sprite/generation adapters remain unavailable. No
  replacement bird art or biological fidelity is claimed.
- Environment rules and the fixed solar path are authored illustration. Real
  weather/astronomy providers and location remain unconfigured. A roofed feeder
  seat is not validated full-body shelter. In-flight bird silhouettes may cross.
- Mobile controls fit, but birds are tiny at 320px. Performance evidence is bounded
  software-rendered Chromium measurement, not hardware/mobile certification.
  Native headless tab occlusion stayed visible; the actual visibility handler was
  exercised with a disclosed synthetic event. Its first held sample is quantized
  at 20Hz; renderer source explicitly discards the first resumed delta.
- SVG is static and preserves the captured environment; arbitrary moving actor-state
  recovery is outside the existing fallback contract. Advanced previews are transient.
- The separate background UI worker remains unintegrated. The user-reported ESP32
  branch at `99c01c6b41de67e2f5e11b46e8e7488a1a33aa4c` is authorized for normal Git
  inspection and local integration **after this checkpoint**; it has not yet been
  inspected/imported here. No Library retry or duplicated firmware implementation.

Only documentation/evidence changes follow the tested revisions. No push, PR,
remote publication merge, deployment, flashing, credential change, paid service or
external product-provider activation occurred in this environment slice.
