# Runtime and owner-query audit — 2026-10-12

The most consequential reproduced defect is a storage/transport budget mismatch: a valid 12,459,063-byte yard accepted a rename, but its 17,117,200-byte success response was rejected by the real client decoder's 16 MiB limit. The owner lookup itself uses its primary-key index. Most measured cost is synchronous validation, history projection, and repeated whole-owner processing after that lookup.

This is read-only audit evidence and proposed work, not a second canonical backlog or a claim that fixes have landed. No application source, existing owner data, providers, credentials, or publication were changed.

The paired [canonical requirements index](../../delivery/product-behavior-and-ideas.md) remains authoritative: reconcile accepted work under PB-001 (evidence/corrections), PB-002 (residents), PB-007 (inventory), PB-010 (arrivals) and EN-003 (runtime/recovery), rather than treating the RQ labels below as new product requirements.

## Scope and reproducibility

- UI checkout inspected: `birdsong-yard-sprites`, HEAD `6f23d988a788a29de509f92af7c1f24f7e63c6b4`; paired documentation checkout: `ChirpNeighbors`, HEAD `b73abeaa06d7ecb67850dc9da8492090890729eb`.
- Other agents were editing archive/assets/request-budget code concurrently. The benchmark bundled the exact repository/domain code before executing; [source hashes](runtime-query-evidence/source-hashes.json) and [bundle/evidence hashes](runtime-query-evidence/evidence-sha256.json) bind this receipt. A later change to `src/lib/client/contracts.ts` added a catalog-pin comparison in the asset loop; both benchmarks use `assets: []`, and the relevant yard/query code stayed unchanged. This is not a clean-checkout or full-system verification claim.
- Measured actual `YardRepository`, `ArrivalRepository`, domain/page validators, and client `parseResponse`, using disposable SQLite files under the recorded `/tmp/chirp-query-audit-*` directory. No HTTP server or browser was started. Client rejection used real `Response` objects and the actual decoder, not a replacement decoder.
- Node **24.19.0**, bundled SQLite **3.53.3**, Linux x86_64, AMD EPYC 9V74, five visible vCPUs with cgroup quota **4 CPU cores**, cgroup memory maximum **16 GiB**, `/tmp` **tmpfs**. Other engineering processes were active. Timings are warm local observations; disk-storage behavior, production concurrency, hardware performance and an SLO are not established.
- Four valid synthetic histories: 100 / 1,000 / 10,000 / 30,000 observations, one species, one resident with a valid origin, four default yard objects, no assets/jobs, initially no corrections or arrival rows. Each seed passed the actual stored-data schema and was below the actual write budget. Direct SQL seed insertion only accelerates setup; measured reads/mutations execute the real repository. Mutations revalidate and enforce its size cap.
- Ordinary timing rows use one discarded warm-up and seven measured repetitions; snapshot/page boundary validation uses three repetitions after warm-up. Batch and contention rows are individual reproductions, not percentile estimates. SQL instrumentation records executed statements and returned rows/text bytes, without changing SQL or transaction scope. Resident-origin probes are separately labeled synthetic stress shapes.

Evidence: [measurements.json](runtime-query-evidence/measurements.json), [probes.json](runtime-query-evidence/probes.json), [environment.json](runtime-query-evidence/environment.json), [benchmark source](runtime-query-evidence/bench.ts), [probe source](runtime-query-evidence/probes.ts). Reproduce with existing installed UI dependencies and a new output directory:

```sh
node /workspace/archive-history/runtime-query-evidence/run-audit.mjs /tmp/chirp-query-audit-reproduction-01
```

The reproduction runner bundles sources into the new evidence directory, records source hashes, and runs only isolated measurements. It does not install dependencies, edit either repo, start services, or access existing databases. Its syntax was checked; the component benchmark/probe commands were executed successfully for this receipt.

## What the schema and query plans actually do

`src/lib/server/storage/repository.ts:119` creates one `yard_owners(owner_id TEXT PRIMARY KEY, schema_version, data CHECK(json_valid(data)))` row per owner. Findings, observations, corrections, residents, inventory and receipts are arrays inside `data`; there are no independent SQLite indexes or SQL pages for those arrays.

Actual owner plan:

```text
SEARCH yard_owners USING INDEX sqlite_autoindex_yard_owners_1 (owner_id=?)
```

A snapshot executes **one SELECT, returning one row**, but hydrates every observation and returns every event plus derived effective-evidence rows and finding event IDs. At 30,000 events that one row contains 12,458,891 bytes before later probe mutations. A resident rename, preference update, duplicate import and exact inventory retry execute **BEGIN IMMEDIATE → SELECT → full-data UPSERT → COMMIT**. Statement count is constant; payload and CPU work are not.

`yard_arrivals` has owner/event primary key, owner/arrival unique key, and `yard_arrivals_pending(owner_id,state,retain_until)`. Actual pending-list plan:

```text
SEARCH yard_arrivals USING INDEX yard_arrivals_pending (owner_id=? AND state=?)
USE TEMP B-TREE FOR ORDER BY
```

The sort/filter uses JSON `eligibleUntil`/`admittedAt`, so that index does not satisfy ordering. Normal admission is already bounded to **256 ledger rows / 20 pending arrivals**, and the SELECT has LIMIT 20 and a bounded payload projection. This is not evidence for prioritizing another arrivals index. The expensive part of an empty arrival list is the unconditional complete yard snapshot before the bounded SELECT.

Median milliseconds, measured separately (do not sum them as an HTTP latency prediction):

| Events | Stored bytes | Snapshot response bytes | SQL row read | Repository snapshot | Page-boundary validation | Empty arrivals list | Rename | Exact inventory retry |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 100 | 42,088 | 57,391 | 0.022 | 3.46 | 11.33 | 3.45 | 4.93 | 7.81 |
| 1,000 | 412,889 | 564,993 | 0.165 | 23.37 | 97.03 | 22.37 | 46.92 | 52.58 |
| 10,000 | 4,138,890 | 5,676,995 | 1.643 | 239.53 | 1,140.89 | 247.29 | 482.45 | 489.88 |
| 30,000 | 12,458,891 | 17,116,996 | 6.357 | 1,238.02 | 6,203.50 | 1,299.02 | 2,689.89 | 1,449.99 |

At 10,000 events, raw JSON parse was 10.29 ms, stored-data validation 205.54 ms, snapshot derivation 8.57 ms, and response JSON serialization 10.61 ms. Validation, rather than SQLite lookup or JSON serialization alone, dominates this shape. At 30,000 events snapshot samples ranged 1,083.55–1,535.47 ms and page validation 5,259.28–7,283.72 ms; GC/shared-host effects mean these are not deterministic latency guarantees.

## Findings and bounded acceptance work

### RQ-01 — P1: accepted owner data can exceed the client response budget

**Reproduction:** the real repository accepted `rename('audit-owner', 'audit-bird', ...)` with a persisted 12,459,063-byte yard. Its full snapshot was 17,117,168 bytes; adding the normal command message made 17,117,200 bytes. `parseResponse` rejected both GET and command representations with `InvalidServiceResponse`, both with and without a declared Content-Length. Reading SQLite confirmed the new name had committed. All four 100-event positive controls passed. The guard remains correct; the producer and consumer budgets do not compose.

**Locations:** `src/lib/server/storage/repository.ts:176` caps only stored JSON at 16 MiB; `src/lib/domain/yard.ts:359` adds duplicated derived history; `src/routes/api/yard/+server.ts:9` and `:144` return full snapshots; `src/lib/client/service.ts:17` and `:56` enforce the same 16 MiB limit on the larger wire response. `src/lib/components/FindingHistory.svelte:60` also creates an option for every effective-evidence row; browser cost was not measured here.

**Proposed bounded fix:** first make admission and the complete response envelope share an explicit budget, so an accepted mutation cannot become an unreadable success. Preserve recovery/export access for already accepted oversized yards. Follow with a versioned, bounded yard projection and owner-scoped findings/history pages; keeping all arrays inside the same serialized snapshot while adding only a visual pager would not reduce this cost. Do not silently truncate evidence, discard old data, or merely weaken the decoder's bound.

**Acceptance:** replay the exact 30,000-event fixture through actual GET and rename/restore paths; every successful command must decode and confirm the committed state. If an admission is rejected, assert pre/post storage equality and an actionable typed response. Test both Content-Length and streamed bodies around the agreed envelope budget, and recovery of a pre-existing oversized yard. A future page contract must preserve stable evidence/correction identities, owner isolation, legacy backups and access to oldest history while bounding returned rows and bytes.

**Dependencies:** producer/client contract agreement and migration/recovery design; no new SQLite index solves this alone. Coordinate schema export and compatibility fixtures with the contracts owner, separately from the archive fix.

### RQ-02 — P2: page hydration repeats full-history validation and reads an empty arrival queue expensively

**Reproduction:** an empty `ArrivalRepository.list` ran two SELECTs, returned the complete owner row plus zero arrival rows, and cost 247 ms at 10,000 events / 1,299 ms at 30,000. `yardPageDataSchema.parse` alone cost 1,141 ms / 6,203 ms respectively, with zero jobs/assets/arrivals.

**Locations:** `src/routes/+page.server.ts:6` obtains a snapshot, then `:26` calls arrivals; `src/lib/server/arrivals/repository.ts:241` hydrates another snapshot before querying whether any pending arrival exists. `src/lib/client/yard-page.ts:14` parses `yardSnapshotSchema`, then `:45` parses the same snapshot through `yardReadResponseSchema`. Each `yardSnapshotSchema` also parses raw yard data again in `src/lib/domain/yard.ts:423`, recomputes projections and canonicalizes both compared sides. The page boundary therefore deeply parses the history four times; root yard/arrival reads add two further stored-state validations before it. These guards protect real invariants, so removal without replacement is not a safe optimization.

**Proposed bounded fix:** extract/reuse validation of the asset-to-snapshot relationship after the snapshot has already been admitted; retain exactly the same schema rejection behavior. Query the bounded arrival rows first and avoid hydrating a yard for an empty result. Permit trusted root assembly to reuse its current owner snapshot for eligibility only through an internal ownership/clock-safe API. Avoid an unversioned cross-request cache.

**Acceptance:** instrumentation demonstrates one snapshot admission at the page boundary, no second complete history validation solely to validate asset relationships, and zero yard hydrations for an empty arrival list. Non-empty root page assembly reuses one admitted snapshot and still rejects changed owner, corrected/expired evidence, stale arrivals, corrupt stored rows and mismatched pins. Re-run the 100/10,000/30,000 shapes and publish samples/query counts; establish any latency target only after an agreed deployment measurement.

**Dependencies:** validator refactoring and arrivals semantics; preserve the concurrent catalog-pin comparison fix. This can be completed before a storage migration.

### RQ-03 — P2: duplicate batches repeat history scans while holding the global SQLite writer lock

**Reproduction:** on the 10,000-event yard, exact duplicate imports of 1 / 100 / 1,000 events took **509.60 / 857.14 / 4,210.13 ms**, with zero inserted events. Each executed a full-data UPSERT inside BEGIN IMMEDIATE. The 1,000-event request is within the documented input batch bound. One / 100 corrections took 521.82 / 650.65 ms; the latter repeatedly rebuilt the full effective-evidence array.

**Locations:** `src/lib/server/storage/repository.ts:229` performs `state.events.find` for each incoming event and recomputes both source keys during the scan. `:307` scans corrections for each correction; `:317` calls `effectiveEvidenceOf(state)` per item. `src/lib/domain/yard.ts:267` also uses an event-array scan for each linked resident origin. A separate schema-valid stress probe with 10,000 events and 1,000 residents measured median validation 191.87 ms with null origins versus 313.23 ms with distinct late-history origins; this illustrates the extra scan, not a typical production resident population.

**Proposed bounded fix:** build event-ID/source-key/species and correction/effective-revision maps once per transaction, update them as accepted items are appended, and use the already constructed event-ID set for resident origin checks. Preserve encounter order and conflict semantics when an ID and source identity point to different existing evidence. For proven exact retries/no-change batches, skip the write and changed hook while still checking the current transaction state and returning the current snapshot.

**Acceptance:** duplicate replay, conflicting ID/source key, later-in-batch conflict, within-batch duplicate and multi-step corrections preserve today's atomic rollback and immutable identity rules. Instrumented element/source-key visits scale with retained history plus batch length, rather than their product. An exact inventory retry still returns the latest layout and receipt, but `total_changes()` stays unchanged and the hook is not re-fired. Re-run large duplicate batches and retained-history fixtures; no absolute millisecond promise is implied by this report.

**Dependencies:** local repository/domain changes and existing findings/inventory regressions. No table migration is needed for these bounded improvements. They reduce lock duration but do not solve RQ-01 or the synchronous wait in RQ-04.

### RQ-04 — P2: SQLite busy wait synchronously stalls unrelated owners on the Node event loop

**Reproduction:** an independent worker connection held BEGIN IMMEDIATE after updating synthetic owner A; the main process attempted the real repository rename for owner B. With a 250 ms hold, the rename took 336.00 ms and a scheduled 10 ms timer ran after 337.42 ms. With a 5,500 ms hold, rename waited **5,008.72 ms**, raised `ERR_SQLITE_ERROR` / SQLite code **5** (`database is locked`), and the timer ran after **5,008.77 ms**. A direct owner-B read during each writer hold succeeded in roughly **2.5 ms** under WAL. Both attempts left `isTransaction === false` afterward. This demonstrates event-loop blocking, not lost updates or an isolation failure.

**Locations:** `src/lib/server/storage/repository.ts:102` uses `DatabaseSync` and sets `busy_timeout=5000`; `:145` obtains BEGIN IMMEDIATE synchronously. The runtime creates the yard at `src/lib/server/runtime.ts:54` and shares its connection with arrivals at `:65`. For POST handlers, `src/lib/server/http.ts:100` treats an unrecognized SQLite exception as the generic command error; `src/lib/http/command-error-contracts.ts:44` maps that to 500. The mapping is code inspection, not an HTTP test in this audit.

**Proposed bounded fix:** choose an explicit local contention policy: short/no synchronous busy wait and an allowlisted retryable response before admission, with bounded asynchronous retry scheduling only where command idempotency is known. Moving synchronous database work into an owned worker is a larger alternative if deployment measurements require it. Keep transactions atomic; do not hold one open across arbitrary async/provider work or automatically replay an uncertain committed command.

**Acceptance:** hold a writer from another connection, concurrently submit a mutation and an unrelated read/health request, and prove the latter can make progress before the lock is released. A retryable rejection occurs before mutation, returns a validated response without SQL/path disclosure, and leaves no open transaction. Releasing the lock permits an explicit safe retry with exactly one intended change. Cover separate owners, nested savepoints, rollback, busy expiry and shutdown. Select the actual timeout policy with the runtime owner; this audit invents no service SLO.

**Dependencies:** runtime/error-contract agreement and a worker/retry ownership decision. Avoid overlapping the currently edited request-budget code until its owner coordinates integration.

## Bounds already present and residual gaps

- Owner reads are indexed and scoped; no cross-owner table scan or missing owner-key index was reproduced. No index recommendation is made from a mere large wall time.
- Imports cap each batch at 1,000; corrections cap a request at 100 and retained corrections at 10,000; inventory caps active objects at 12 and durable operation receipts at 4,096. These bounds are real but do not bound total observation hydration or full response bytes.
- Exact inventory retries are semantically idempotent but still executed an UPSERT and incremented SQLite `total_changes()` by one at every history size. That is statement/lock/CPU evidence, not proof of equal physical WAL growth; unchanged-page write elision was not measured.
- WAL allowed concurrent reads in the contention fixture, and transactions/savepoints left no transaction open after the observed busy failure. No data corruption was reproduced.
- Existing private owner/auth, export/restore and reviewed-manifest behavior must remain intact in any fix. Shared views must retain their explicit public allowlist; paging must not introduce location or private evidence into public projections.
- This audit deliberately excludes job/artifact hydration, asset lookup/index work and archive pagination owned by the other reviewer. No full route/request count, browser DOM profile, real disk/fsync test, cold-cache run, production deployment benchmark, or owner data migration was performed. Browser history rendering and resident-origin worst-case scaling remain follow-up measurements, not additional claimed production failures.

Executed evidence comprises **four history sizes**, **ten batch cases**, **two contention cases**, **eight actual client decoder cases** (four positive/four reproducing rejection), and **six resident-origin validation shapes**. Both benchmark processes exited zero; that means reproductions completed, not that the defects are fixed. Proposed priorities are RQ-01 correctness first, then the local RQ-02/RQ-03 reductions, followed by the coordinated RQ-04 runtime policy and bounded history contract.
