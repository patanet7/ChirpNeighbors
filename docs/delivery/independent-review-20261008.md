# Independent architecture review — 2026-10-08

Three read-only reviewers inspected actual changes after the complete fourth
63-gate pass. The reviewed revisions were UI
`6dca7c1d607639612543f3c49c0911a0c2b273c8` and companion
`22e105ae06eb7520f3b179da8d8f69ab3a581d09`, against the prior readiness
checkpoint (`305cbea` / `c46735b`). Review was independent of the slice authors;
reviewers did not edit files or run competing builds/browser suites.

| Reviewer scope | Finding | Resolution and evidence |
| --- | --- | --- |
| Architecture/dataflow and a separate asset/renderer reviewer | P2: packaging omitted the prospective root from dependency visit/depth limits, allowing a fully approved but unpinnable artifact | Reserve one visit and one depth level during packaging validation; keep loader limits at 64/32. Tests now load/pin the last admitted boundary and reject the first over-limit graph before any source artifact. `85160a9b8fc820bc13f239298546ee03d6745b8e`; 19 focused tests passed. Architect independently approved the repair diff. |
| Runtime contracts/auth/storage/transport | Pre-existing P2: a typed 5xx after a committed move was considered definitive failure despite a fresh validated read confirming it | Treat 5xx as uncertain until the existing exact placement/scene/pin comparison succeeds. Preserve decoded 4xx rejection and no POST replay. The author's `b7c8b4d7111fe5d95261e14afdc87883cea14435` adds eight regressions, including an actual SQLite commit before the failed response; 71 focused tests passed. The runtime reviewer independently approved the exact repair diff. |

The first new depth regression repeatedly decoded full fixture sheets and hit its
unchanged 5-second test deadline. It was narrowed to one copied opaque fixture
pixel because the test concerns dependency depth, then passed in 3.3 seconds.
No production limit or test timeout was increased. This diagnostic failure is
separate from the retained fourth complete aggregate.

No additional material defects were found in the inspected owner-scoped review →
source/reference hashes → immutable manifest → pin → private SSR → registry →
Pixi/SVG path. Review also checked structural-versus-semantic contract authority,
legacy V2 admission, private/public projections and relevant persisted-row guards.
This is a scoped code review, not a proof of universal correctness.

Remaining limitations are explicit: pose contacts are diagnostic metadata, not
physical collision/placement geometry; browser analysis has caller cancellation
but no deadline/byte ceiling, and confirmation has a deadline but no body-byte
ceiling. These are queued followups, not claims of universal transport coverage.
Real art/models/providers, account-wide deletion and the unavailable worker/device
handoff remain outside the verified local capability.

The final full frozen aggregate must cover the integrated fixes. Focused tests
and the earlier passing report do not substitute for that result.
