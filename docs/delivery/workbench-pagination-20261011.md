# Owner workbench pagination

Local continuation from main `8a9ff3e2f6a702342c8028547adcc39aa24dc2b0`
and UI `bd23e784397d7b5e0b01c0c2d12e6d000fefa1c0`, on
`codex/workbench-pagination-local`. Publication, model downloads/providers,
network bypass, new rendering budgets and replacement of the missing original
worker are outside this workstream.

| Task | Dependencies | Concrete acceptance |
| --- | --- | --- |
| WP-01 — Owner page contract | Existing session binding and SQLite authority | Strict bounded query/cursor; reject duplicate/unknown parameters, oversized limit, altered signature, changed limit, foreign owner and wrong list scope. Optional page metadata preserves parsing of retained legacy fixtures. |
| WP-02 — Stable storage traversal | WP-01 | Five rows by default, maximum ten; immutable insertion order and frozen rowid ceiling. New, tied and backdated inserts appear only after restart. Previous/retry repeats the same page; status/review changes remain live. |
| WP-03 — Bounded hydration and responses | WP-02 | Cap response at 8 MiB before serialization, including UTF-8 and cursor reserve. Preflight heavy job payloads; oversized/corrupt details produce an explicit bounded unavailable display, never rewrite stored jobs or renderer pins. SQL filters diagnostic jobs before LIMIT. |
| WP-04 — Independent selections and retention | Existing exact renderer pins and global bounded dependency scan; WP-02 | Page navigation keeps selected PNG/preview and immutable resident pins, including selections/dependencies outside the current page. A visible page never becomes retention authority; archived dependencies still deny new use. |
| WP-05 — Accessible resilient navigation | WP-01–04 | Distinct keyboard controls, live loading/error/page status and retained focus at first/last/empty pages. Failed requests retain confirmed rows; latest intent wins even if abort is ignored; unmount/owner change rejects late results. Confirmed mutation remains confirmed when its separate page read fails. |
| WP-06 — Inventory reconciliation | Completed E-REF and E-REC evidence | Inventory describes current PNG/JPEG admission, diagnostic-only generation and receipt-bound cold recovery. Proposed 32×32/60-frame recipe is explicitly unapproved for art quality. |
| WP-07 — Frozen verification and independent review | WP-01–06 | Focused server/contract/client/browser adversarial controls, full local aggregate with exact committed heads, independent final review and retained failed attempts. No publication. |

All seven tasks are complete within the bounded scope below. **97/97 frozen
gates passed** at main `ca8f9cd9cb072245b3dfe81a68fc1bf7f9db66ca` / UI
`269183ff6d333a125f0fee5fb0dfcb80aafe5a38`. [Evidence index](LOCAL-EVIDENCE.md),
[report](LOCAL-EVIDENCE.md) and
[counts](LOCAL-EVIDENCE.md) retain the exact source,
independent review, corrections and failed attempts. The prior 96-gate checkpoint
remains historical evidence.

| Completed acceptance | Named evidence |
| --- | --- |
| WP-01–03: signed owner/scope limits, frozen insertion membership, live state, UTF-8 bounds and corrupt/oversized hydration | `src/lib/server/workbench/pagination.test.ts`; independent 20-control runtime review; `contract-compatibility`, `zod-python-roundtrips` and `zod-python-properties` gates |
| WP-04: off-page selections, previews, renderer pins and whole-owner retention authority | `scripts/workbench-pagination-browser-checks.py`: “Off-page selected PNG and canonical preview are retained”, “All page operations preserve exact renderer assets and saved artwork pins”, “Pinned older-page artwork still loads through Pixi”; existing asset-retention browser gate and independent archived-dependency control |
| WP-05: exact retry, keyboard focus, failure retention and stale result fencing | `src/lib/client/page-navigation.test.ts` (7 tests); pagination browser (27 checks), including repeated exact PNG cursor retry and delayed page response defeated by Restart |
| WP-06: current admission/recovery/animation boundaries | UI `docs/animation-production-inventory.md`; E-REF/E-REC remain historical source evidence |
| WP-07: frozen regression and review | Complete 97-gate R4 report; 2,072 UI tests; 718 goldens; 17,315 mutations; 20 independent runtime controls and 10 independent compatibility comparisons |

Server test paths and browser scripts above are in the sibling UI repository.
Diagnostic-job scope is tested at the server boundary; its separate reference-page
Next/Previous controls are not independently exercised by a browser journey.

Cursor signatures use an in-memory process key, not a new credential or key file.
Restarting the server requires restarting traversal. Cursors are not authority;
every query independently constrains the authenticated owner. These retained
tables have no supported row deletion/reinsertion path. General database migration
or distributed cursor continuity is not promised. Mutable job state is read live;
only list membership/order is frozen.

Retention remains a separately bounded whole-owner dependency scan. Its 512-job,
64-file and 32 MB scan bounds and fail-closed incomplete status are unchanged;
this work does not claim unlimited retention scale or paginate away dependencies.

Compatibility is backward reading of retained list envelopes. Old strict clients
reject added page metadata, and old list consumers may assume arrays are complete.
This local unpublished slice requires the matching updated server/UI and a reload
of old UI sessions. Independently deployed old clients would need a versioned or
negotiated endpoint; returning truncated arrays without metadata is not a legacy
adapter. Only the reviewed PNG-list digest entries changed; no compatibility
checker rule was relaxed.
