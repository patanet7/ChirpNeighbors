# Independent archived-history review

The reviewed implementation has no remaining blocking finding after the three corrections below. This is a local source and focused-service review of the uncommitted worktree based on `6f23d988a788a29de509f92af7c1f24f7e63c6b4`, not approval of a final frozen aggregate or publication.

Reviewed repository: `/workspace/archive-history/birdsong-yard-sprites`; paired contract/checklist: `/workspace/archive-history/ChirpNeighbors`. Exact final source hashes, 56 embedded probe-input comparisons and limitations are in `review-receipt.json`. Product files, actual local data and Git refs were not modified by this reviewer. No app server, browser, network call or full test suite was run.

## Concrete findings

| ID | Severity | Defect and path | Disposition |
| --- | --- | --- | --- |
| ARCH-01 | P2 | `/api/asset-lifecycle/packages` was absent from `src/lib/server/operations/request-budget.ts`'s private-read allowlist, bypassing the existing owner/global read admission limits for a route that performs dependency reads inside a transaction. | Fixed. Both GET and HEAD now classify as `reads`; the exact-route regression rejects unrelated methods/routes. Independently re-executed both classifier controls. |
| ARCH-02 | P2 | `src/lib/server/assets/lifecycle.ts:packageDependencies` preflight used SQLite `length(input_json)`. This counts text characters and stops at embedded NUL, unlike the repository's UTF-8 byte limit. Oversized corrupt NUL/Unicode rows reached `JobRepository.get` and its `SELECT *` hydration. Related artifact/aggregate queries used the same character-count convention. | Fixed. Input, artifact and aggregate queries now measure `length(CAST(... AS BLOB))` while retaining their numeric limits. Independent ASCII, NUL and Unicode probes now reject all three before `get`. Initial failure remains in `hydration-r1.json`; corrected results are in `hydration-r2.json`. |
| ARCH-03 | P3 | `src/lib/components/AssetLifecycle.svelte:save` rejected every action while `history.loading`, but Unpin, Restore previous pin and Retry pending change buttons remained enabled. Clicking an apparently available action during a slow history read silently did nothing. | Fixed by matching those disabled predicates to the save guard. Verified by source diff; actual browser interaction remains part of the parent verification. |

## Safety and correctness assessment

- History uses a separate additive `asset-package-history-v1` response and an authenticated owner resolved by the endpoint. Every page explicitly has `referenceScan: 'not-run'`, `purgeEnabled: false`, mandatory pipeline/incomplete-scan retention reasons and `cleanupEligible: false`. It never substitutes a page for the owner-wide reference graph. Six existing lifecycle schema files remain byte-identical; the new main/UI schema mirrors match exactly.
- Membership uses the existing signed owner/scope/page-size cursor and immutable insertion watermark. The new `asset-packages` scope prevents reusing job-list cursors. No caller-supplied owner, offsets or mutable archive-status filter are added. Cursor restart is required after a server restart or to include newly inserted jobs.
- Page membership, live archive revisions, retention metadata and dependency reads share one database transaction. The page has at most ten entries; exact dependency checks retain the existing depth/node/artifact budgets. Corrupt or missing dependencies conservatively block selection while leaving metadata visible. Metadata accounting measures retained bytes without returning source pixels. These bounds are not a performance proof for a heavily interconnected dependency graph.
- Archive ownership, compare-and-set revision checks and idempotent request receipts remain authoritative on the server. Existing pin resolution and purge behavior are not replaced. Independent probes verify live archive state under an old traversal cursor, exact retry, stale revision rejection, cross-owner mutation rejection and an unchanged fixture yard snapshot. Real pinned-renderer integration remains covered by the parent service/browser runs, not by these metadata-only probes.
- The component retains confirmed rows after read failure, uses the bounded shared navigation helper, aborts/discards superseded reads, and destroys that helper on unmount. Browser account changes also rely on the existing immutable document-session binding; the new read does not bypass `checkedRequest`/`sessionFetch`.
- A matching successful write receipt clears the pending command before refreshing the current history cursor. A history refresh failure is caught by navigation and cannot turn that confirmed write into a pending mutation. It leaves visible stale package actions disabled until a successful read. Lost/invalid write responses keep the exact request for retry. Existing overview/pin authority stays separate.
- `PageControls` provides named navigation, keyboard buttons, a live loading/page status, an error alert, exact-request retry and bounded previous-page history. Existing focus restoration is retained. Responsive layout, actual focus transitions and account-switch behavior still require browser verification.

## Focused evidence

`semantic-r2.json` records **22 passing controls** using disposable SQLite and controllable transport promises: frozen membership, response limits, new traversal, owner isolation, owner/limit/signature/scope rejection, live archive state, idempotency, cross-owner/CAS rejection, unchanged yard state, unchanged response envelope, conservative retention, contract negatives, stale-response fencing, retained rows, exact retry and unmount.

`hydration-r2.json` records **three corrected pre-hydration controls** and **two route-budget classifier controls**. These are separate from the 22 semantic controls. The embedded sources in both executed R2 bundles match the inspected filesystem inputs, as recorded in the receipt. R1 probe files/results remain preserved rather than relabeled as passing evidence.

## Remaining scope

The parent must complete the actual 513+ package/browser journey, renderer/pin regression, paired contract gates, type/lint/build checks and any final frozen-source binding. The existing Workshop new-selection gate still conservatively uses the legacy overview, so this repair restores archive/history reachability without promising selection of every off-overview package. No deletion, purge, new retention authority, generation provider, art fidelity, publication or deployment is claimed.
