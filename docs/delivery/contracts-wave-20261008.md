# Contract and animation work checklist — 2026-10-08

This local wave continues from the reviewed branches and preserves both failed
readiness attempts. Attempt 2 finished 56/57 gates at UI `305cbea` / companion
`c46735b`; its routines browser reload timed out. The unchanged routines journey
passed 17/17 in an isolated check. Neither result is an all-pass combined run.

| Task | Dependencies | Concrete acceptance | Current state |
| --- | --- | --- | --- |
| Enumerate actual boundaries | Svelte routes/hooks, Python route declarations, stores, jobs, configuration | New/removed runtime routes fail an AST-backed inventory gate; one source authority per boundary; closed private/public SSR aggregates | Implemented locally |
| Validate runtime admission/egress | Inventory; generated Python identity guard | Reject corrupt SQLite rows, unsafe IDs/counts/times, malformed auth settings, mismatched recording metadata/receipts and impossible audio windows; preserve private owner state on failures | Implemented locally |
| Bound transport and recovery | Existing response/error schemas and lifecycle ledgers | Finite fetch/body reads, byte ceilings, strict UTF-8, cancellation and safe status parity; expired/revoked/restored shares remain unavailable | Implemented locally, including placement/finding reconciliation and share preview |
| Generate and test counterpart contracts | Canonical Zod/Pydantic models | Regeneration must be clean; preserve literal schema-looking data; reject remote/unsupported references; exact goldens and deterministic mutations; reviewed structural digest changes fail automatically | Implemented and generated; final integrated gate pending |
| Version pose manifests | Existing v2 manifests, catalog, technical fixture pixels | Keep v2 behavior; v3 unequal durations, pivots/contacts, exact pose graph and pinned references, bounded binary-alpha/grid/palette/loop metrics; malformed geometry rejects before allocation | Schema, producer and renderer integrated; 29 focused browser assertions passed |
| Preserve private source lifecycle | Existing owner SQLite artifact/review model | Distinct immutable RGBA artifact; source/reference digest and approval rechecked at render; absent source fails to fixture fallback; approval never changes a resident pin | Implemented locally; 18 source lifecycle tests and the focused browser journey passed |
| Run combined frozen verification | All source and generated changes committed; other heavy jobs stopped | Full retained browser/HTTP/unit/type/lint/build/generator suite completes on unchanged clean revisions; preserve failure reports and exact source IDs | Pending |

Art remains technical fixture content. Provider-independent contracts describe
unsupported future capabilities explicitly; no image model, replacement art,
real bird weights, paid service or external provider is configured by this work.
Contact metadata is review evidence and renderer diagnostics, not inverse
kinematics. Public snapshots use the safe built-in catalog only.

Focused evidence is retained in each boundary audit and in temporary check
outputs. Final aggregate counts and exact commit IDs will be recorded after the
complete run. Account-wide deletion, real photo decoding, licensed evaluation
inputs, real import/weather adapters and deployment remain distinct gaps.

The approved worker/device Library handoff failed its supported local download
twice. No archive bytes were obtained, so its digest/contents/commit ancestry
cannot be verified and neither implementation is integrated or recreated. See
[the exact handoff blocker](approved-handoff-blocker-20261008.md).


The first complete contract-wave run finished **62/63** gates with clean frozen
revisions UI `8b88f605fae4de32a509b4983c1d4095ace70ebe` and companion
`c377c0d2e498a13b8461eb372530bf5d8668da13`. All 938 UI tests, 157 Python tests,
contract gates and other browser journeys passed, including the unchanged
17-assertion routines journey. The arrangement browser mock supplied an untyped
HTTP 500 object containing arbitrary error text and expected that text to appear.
The closed client error guard correctly hid it and retained the saved yard.

The followup changes only that browser expectation: require the safe rejection,
assert the unreviewed text is absent, and retain the saved-position check. No
application code changes for this failure. The complete original report is
[retained here](contracts-attempt-1-20261008.json); a second full frozen run is
required rather than presenting a selective rerun as an all-pass aggregate.


A second report survived the workspace restart with 33 completed gates and
`finished: false`; no runner or test services remained active after recovery.
Its exact source revisions are UI `fe7016c52f1737cbaa2e8c4a92bb312c35f64e53`
and companion `1ef72bc4031789db2fbd15adc13401c9098c3244`. This is interrupted
verification, not a complete result. The [partial report](contracts-attempt-2-interrupted-20261008.json)
is preserved, and a fresh complete run uses a new evidence directory.


The post-recovery third run completed **62/63** gates at UI
`fe7016c52f1737cbaa2e8c4a92bb312c35f64e53` and companion
`95808ce1ab1394c24b694a8e7e7b44ee2d2a0f1c`, with both worktrees frozen.
The corrected arrangement journey passed all 31 checks. Routines again timed
out at its existing reduced-motion reload (`Page.reload`, 30 seconds,
`networkidle`) after 13 successful checks, despite an exclusive browser window.
This recurrence means competing jobs alone do not explain it. The unchanged
application completed this journey in the first contract run, so the failure
is intermittent. [The full third report](contracts-attempt-3-20261008.json) is
preserved. Reload timing and outstanding requests are being investigated in an
isolated checkout; no timeout widening or assertion removal is approved by this
checkpoint. There is still no complete all-pass combined run.


The fourth run completed **63/63 gates, all passed**, at UI
`6dca7c1d607639612543f3c49c0911a0c2b273c8` and companion
`22e105ae06eb7520f3b179da8d8f69ab3a581d09`; both worktrees remained frozen.
The routines launcher now uses WebGL-only SwiftShader after a traced software
GPU compositor stall; all original assertions/timeouts remain. See the UI
`docs/routines-browser-diagnosis.md`. The [complete passing report](contracts-attempt-4-20261008.json)
is retained independently of subsequent review.

Independent review then identified a correctness gap the existing tests had
accepted: reference validation during packaging omitted the prospective manifest
root from visit/depth budgets. A boundary candidate could complete both reviews
but fail loading/pinning because loading counted that root. This is being fixed
with last-admitted/first-rejected regressions before the final reviewed checkpoint.
The passing fourth report does not claim coverage of that later fix.


The independent review also found a pre-existing placement reconciliation bug:
a typed server error could follow a committed move, but the browser treated it
as definitive failure even after a valid fresh read confirmed the saved placement.
The repair keeps 5xx results uncertain until that read; definitive 4xx rejection,
owner boundaries, validation and one-POST behavior remain. The review dispositions
and focused evidence are recorded in [the independent review](independent-review-20261008.md).
The latest requested moving-bird/workbench/reference work is a
[queued hierarchical task tree](visual-task-tree-20261008.md), not implemented
features in this checkpoint. A final full frozen run must cover both review fixes.
