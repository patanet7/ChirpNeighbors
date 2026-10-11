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

Implementation and focused verification are in progress. No new passing aggregate
is claimed until its complete report is retained. The prior 96-gate checkpoint
remains historical evidence, not verification of this work.

Cursor signatures use an in-memory process key, not a new credential or key file.
Restarting the server requires restarting traversal. Cursors are not authority;
every query independently constrains the authenticated owner. These retained
tables have no supported row deletion/reinsertion path. General database migration
or distributed cursor continuity is not promised. Mutable job state is read live;
only list membership/order is frozen.

Retention remains a separately bounded whole-owner dependency scan. Its 512-job,
64-file and 32 MB scan bounds and fail-closed incomplete status are unchanged;
this work does not claim unlimited retention scale or paginate away dependencies.
