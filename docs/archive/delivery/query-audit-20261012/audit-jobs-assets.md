# Jobs, assets, references and recovery query audit

The highest-value measured fix is the artifact index on `(owner_id, job_id, created_at, version)`: a ten-job page over 8,192 retained jobs fell from **317.35 ms to 29.77 ms**, and the new package-history page from **272.10 ms to 22.32 ms**, in the same synthetic database. Read-only lifecycle calls also unnecessarily acquired the SQLite writer lock; the parent's correction was independently verified. The remaining larger cost is repeated full-graph hydration in lifecycle overview, not a missing index alone.

This reviewer made **no application source edits or publication actions**. All writes were isolated synthetic SQLite databases and audit artifacts under [audit-jobs-assets](audit-jobs-assets/). The parent is implementing fixes separately. No real owner data, external service, model or artwork was used.

## Sources, method and limits

- UI base HEAD: `6f23d988a788a29de509f92af7c1f24f7e63c6b4`; main HEAD: `b73abeaa06d7ecb67850dc9da8492090890729eb`. The UI already had uncommitted package-history work, and the parent changed it during this audit. Measurements use bundled source snapshots with [initial source hashes](audit-jobs-assets/source-binding.json), [reference/recovery source hashes](audit-jobs-assets/references-source-binding.json), and [read-lock-fix source hashes](audit-jobs-assets/lockfix-source-binding.json). Those distinguish measured revisions from later edits.
- Hardware visible in this shared cloud container: AMD EPYC 9V74, five visible CPUs; cgroup quota **four CPU cores**, **16 GiB RAM**, no swap. Linux `6.18.44`, Node `24.19.0`, SQLite `3.53.3`. The host reports about 18 GB memory; the cgroup limit is the applicable bound.
- Jobs: 32, 256, 2,048 and 8,192 owner-scoped jobs, each with two persisted stages, two runs, one approved artifact and one review. A real built-in fixture job was prepared/reviewed once, then valid synthetic rows were cloned with fresh identities, versions and timestamps. Fixture manifest/provenance bytes total approximately 0.87, 6.98, 55.82 and 223.28 MB respectively. Largest database was 248.65 MB before the later archive-preflight phase. These are mechanics fixtures, not generated bird art.
- Actual `jobPage`, `packageHistory`, `overview`, reference list/export and lifecycle recovery functions were exercised. SQL executions and returned rows were instrumented by wrapping SQLite statements. Query counts include `BEGIN`/`COMMIT` for job/lifecycle measurements; they count SQL statements, not internal subqueries. Returned rows include repeated hydration of the same record; **VM rows visited were not instrumented**. `EXPLAIN QUERY PLAN` supplies access-path evidence.
- Two warmups followed by nine samples for page reads; overview had two warmups and three samples; raw cursor queries had 101 samples. Tables show medians. Reference/recovery runs used one warmup and nine samples. This is warm local-file/shared-cloud evidence with instrumentation overhead and possible concurrent contention, **not production SLOs, cold-disk evidence or realistic maximum-image timing**. Nine-sample p95 in raw JSON is the sample maximum, not a reliable production tail estimate.
- Large audit runs are finished. The parent observed an existing broad-suite timeout during concurrent work; no causal claim is made, and audit load was stopped before its isolated rerun.

## JAQ-01 — P2: missing artifact owner/job index

Affected reads are [`workbench/jobs.ts:14`](../../../../birdsong-yard-sprites/src/lib/server/workbench/jobs.ts#L14), [`pipeline/repository.ts:326`](../../../../birdsong-yard-sprites/src/lib/server/pipeline/repository.ts#L326), and [`assets/lifecycle.ts:117`](../../../../birdsong-yard-sprites/src/lib/server/assets/lifecycle.ts#L117), including retained-byte queries in package history. The old only-useful artifact index is the uniqueness index on `(owner_id, family, version)`. SQLite uses just its owner prefix to find one job's artifacts.

Observed plans:

```text
Before: SEARCH a USING INDEX sqlite_autoindex_pip_artifacts_2 (owner_id=?)
        SEARCH r USING INDEX sqlite_autoindex_pip_reviews_1 (artifact_id=?) LEFT-JOIN
        USE TEMP B-TREE FOR ORDER BY
After:  SEARCH a USING INDEX audit_artifacts_owner_job (owner_id=? AND job_id=?)
        SEARCH r USING INDEX sqlite_autoindex_pip_reviews_1 (artifact_id=?) LEFT-JOIN
```

The bounded byte/count query also changes from owner-only to owner-and-job lookup. At 8,192 jobs, the last baseline page sample spent approximately 185 ms in ten budget statements and 92 ms in ten artifact reads; indexed total SQL time was about 0.92 ms. Response hydration/validation still accounts for much of the remaining approximately 30 ms.

| Owner jobs / artifacts | Jobs page before → indexed, ms | Package history before → indexed, ms | SQL statements per page | Response entries |
| ---: | ---: | ---: | ---: | ---: |
| 32 | 33.65 → 32.65 | 42.37 → 37.86 | 64 / 105 | 10 / 10 |
| 256 | 58.22 → 29.70 | 44.31 → 23.30 | 64 / 105 | 10 / 10 |
| 2,048 | 82.68 → 51.22 | 81.20 → 22.94 | 64 / 105 | 10 / 10 |
| 8,192 | 317.35 → 29.77 | 272.10 → 22.32 | 64 / 105 | 10 / 10 |

Jobs pages return 82 SQLite rows across their statements, package pages 92, for the same ten response entries. This does not count internal rows scanned. Results and detailed plans: [results.json](audit-jobs-assets/results.json).

**Bounded repair:**

```sql
CREATE INDEX IF NOT EXISTS pip_artifacts_owner_job
  ON pip_artifacts(owner_id, job_id, created_at, version);
```

The parent added this exact column order under the production index name while the audit ran. The measured A/B used the equivalent `audit_artifacts_owner_job` only in synthetic databases. Final integration/upgrade tests belong to the parent; no claim is made that the new production source was fully re-benchmarked here.

**Compatibility:** Keep `UNIQUE(owner_id,family,version)`, immutable triggers, migration-1 row shape and wire contracts unchanged. An additive nonunique index is compatible with existing readers and can be created on reopening old stores. Building it once takes a writer lock and scans retained artifacts; test startup contention under the existing timeout. `IF NOT EXISTS` alone does not validate a same-name index with unexpected columns. No pipeline-index whitelist was found in existing backup/preflight code. The separate runtime preflight validates migration ledgers; do not infer a direct `JobRepository` constructor has equivalent future-version protection.

**Acceptance:** Open a populated pre-index v1 database; add exactly one correctly shaped index; reopen idempotently; compare every source/artifact/review byte and version before/after. Explain the actual budget and ordered artifact queries and require owner+job search without a temp artifact sort. Preserve foreign-owner denial, family version allocation and immutable review behavior. Re-run a fixed ten-entry page over small/large retained history and compare identical results and stable lookup work. PB-014/PB-022, EN-001/EN-003.

## JAQ-02 — P2, corrected in current parent source: lifecycle reads took the writer lock

The original [`AssetLifecycleService.transaction`](../../../../birdsong-yard-sprites/src/lib/server/assets/lifecycle.ts#L81) always opened `BEGIN IMMEDIATE`, including standalone `overview` and `packageHistory`. A second WAL connection holding a writer transaction allowed `jobPage` to read, but both lifecycle reads failed `SQLITE_BUSY` after approximately 76 ms when the isolated probe timeout was set to 75 ms. The ordinary repository timeout is **5,000 ms**; Node's synchronous SQLite wait can occupy the server thread. This is writer contention, not CPU computation or a missing data index.

The parent changed standalone read calls to `BEGIN`, preserving an existing caller transaction and leaving mutations on `BEGIN IMMEDIATE`. Independent new-source [lock-fix probe](audit-jobs-assets/lockfix-results.json) established:

- With an uncommitted archive flip and revision 2 held on the second connection, package history and overview succeeded.
- Both saw only committed `archived=true`, revision 1; uncommitted changes stayed invisible.
- An archive mutation remained blocked with SQLite error 5 after 76.24 ms at the 75 ms probe timeout.

These are concurrency assertions; their individual elapsed times are not directly comparable to the earlier latency table because this phase had archived the synthetic targets and was not a repeated timing run.

**Acceptance retained:** Standalone reads continue during a separate WAL writer; no dirty archive state; mutations retain CAS/idempotency and writer serialization; nested command response assembly retains the caller's snapshot; read errors roll back cleanly. PB-022, EN-003.

## JAQ-03 — P2 follow-up: lifecycle overview repeatedly hydrates the same dependency data

[`graph`](../../../../birdsong-yard-sprites/src/lib/server/assets/lifecycle.ts#L261) calls `packageDependencies` once for every scanned job. `overview` then calls `selectablePackage` again for each active entry ([line 357](../../../../birdsong-yard-sprites/src/lib/server/assets/lifecycle.ts#L357)), which re-reads archive state, input, artifacts and dependencies. It also scans all dependency sets to compute each entry's reverse-reference reason ([line 379](../../../../birdsong-yard-sprites/src/lib/server/assets/lifecycle.ts#L379)). Dependency traversal budgets are valuable safety controls, but the current presentation repeats work within one snapshot.

| Packages actually included | Overview median before / indexed | SQL statements | SQLite rows returned |
| ---: | ---: | ---: | ---: |
| 32 | 230.66 / 186.51 ms | 519 | 481 |
| 256 | 1,440.82 / 1,269.93 ms | 4,103 | 3,841 |

At 256 jobs, the indexed last sample spent only about 42 ms inside measured SQL statements; the remaining time includes schema parsing, JSON/digest work, iteration, preparation and instrumentation. An index alone does not fix this cost. The old/new command path also assembles overview while its mutation transaction is still active, extending writer-lock tenure.

At 2,048/8,192 fixtures, total metadata exceeds the conservative 32 MB graph budget, so overview returns **zero package entries** with incomplete reference scan in approximately 9/45 ms. That is a deliberate refusal to hydrate the graph, **not evidence that overview scales better**. The new package-history path still returns ten entries. The already identified byte-length and route-budget fixes were owned by the parent/reviewer and are not counted as new findings here.

**Bounded next slice:** Reuse validated per-package/dependency/selection data within the current request snapshot, and construct a reverse-dependency map once. Preserve exact-target checks when the whole graph is incomplete; never turn an incomplete scan into cleanup permission. Avoid a process-global authority cache. Separately consider using the existing paged history for everyday presentation rather than constructing full graph entries after every archive action.

**Acceptance:** Instrument 32/256/512 bounded graphs and require no duplicate input/artifact hydration per visited package in one overview; response and retention reasons match the existing implementation. Include shared dependencies, cycles, depth/visit budget edges, archived dependencies, corruption, owners, retained pins, byte overflow and mutation rollback/idempotency. Record reduced query counts and lock tenure without setting an arbitrary production latency gate. PB-022/PB-014, EN-003.

## JAQ-04 — P3: cursor query retains avoidable depth-dependent filtering

The page SQL at [`workbench/pagination.ts:109`](../../../../birdsong-yard-sprites/src/lib/server/workbench/pagination.ts#L109) combines the watermark range with `(? IS NULL OR rowid<?)`. The index can use the watermark range, while the second bound remains conditional. With the cursor at about 20% of the retained rowid range, the measured raw ID query grew with history:

| Owner rows | Current conditional query median | Explicit `rowid < before` candidate |
| ---: | ---: | ---: |
| 32 | 0.0114 ms | 0.0089 ms |
| 256 | 0.0213 ms | 0.0110 ms |
| 2,048 | 0.0840 ms | 0.0111 ms |
| 8,192 | 0.2932 ms | 0.0112 ms |

Both plans print an owner-and-rowid range; these timings and predicate structure support the depth-filtering finding, not an exact VM row-visit count. This is much smaller than the artifact lookup cost. A bounded repair can branch first/subsequent page SQL or compute `min(watermark, before - 1)` and use one inclusive upper bound. Preserve the signed owner/scope/limit binding and frozen watermark. Test no duplicates/skips, backdated concurrent insert, owner/scope tampering, restart invalidation, empty pages and byte-truncated pages. No new wire schema is necessary. PB-022, EN-001.

## References, offline recovery and lease observations

| Read path / synthetic size | Median | SQL statements | Bound |
| --- | ---: | ---: | --- |
| One owner's reference list, 1 file | 0.84 ms | 4 | 16 files per owner |
| One owner's reference list, 16 files | 13.89 ms | 49 | Same |
| Same 16-file owner among 64 global files | 10.90 ms | 49 | 64 globally |
| Full reference authority export, 1 / 16 / 64 files | 1.04 / 6.92 / 12.23 ms | 6 each | 64 global files |
| Asset lifecycle preflight, 32 / 256 archives | 1.40 / 8.40 ms | 72 / 520 | 16,384 global archive records |
| Asset lifecycle preflight, 2,048 / 8,192 archives | 182.70 / 446.71 ms | 4,104 / 16,392 | Same |

Reference tests admitted real synthetic one-pixel PNG bytes through the existing decoder, with unreviewed metadata. They did **not** measure full-size photographs, every review combination or maximum recovery byte volume. Reference list performs one ID query plus three reads per file and repeated private-directory/identity/tombstone checks. Plans use primary/owner indexes; list sorting and owner-prefix review lookup are bounded at present caps. No high-priority new reference index was justified. Full recovery scans are intentional authority validation, not owner-facing list queries; retain their completeness, byte verification and corruption refusal. [Reference evidence](audit-jobs-assets/references-results.json) · [Recovery evidence](audit-jobs-assets/recovery-results.json).

`pip_stages` uses its `(job_id,path)` primary key for claims/outputs, with a bounded in-job ordinal sort. Lease claim and completion retain `BEGIN IMMEDIATE`, exact live token, expiry/status checks and atomic artifact commit. There is no global overdue-job scan or scheduler query in this workbench; the original-worker gap is not an index defect. Existing tests cover separate-connection single claim, lease expiry/backoff, late completion fences and cancellation, but this audit did not rerun those tests during the parent's broad suite.

Two secondary plans deserve attention **before enabling a larger autonomous worker**, rather than immediate speculative changes: `runs(jobId)` scans `pip_runs` and sorts (all current source callers found were tests), and descendant cancellation filters children using only an owner-prefix job index. Candidate indexes are `(job_id,started_at,attempt)` for run history/updates and `(owner_id,parent_job_id)` for recursive children. They were **not A/B benchmarked** here and are not claimed equivalent to the measured artifact fix. Test representative valid job trees and cancellation transaction duration first. EN-006/EN-005.

The paired main audio service retains bounded process-local owner/request cache and in-flight sets and obtains recording authority through its gateway; it does not issue these SQLite queries. Durable generation-fenced result admission remains in the Svelte service. No database behavior is attributed to the unavailable original worker.

## Executable evidence

- [Main benchmark source](audit-jobs-assets/benchmark.ts), [bundler](audit-jobs-assets/build.mjs), [frozen executable](audit-jobs-assets/benchmark.mjs), [results/plans](audit-jobs-assets/results.json), [run log](audit-jobs-assets/run.log).
- [Reference/recovery benchmark](audit-jobs-assets/references.ts), [bundler](audit-jobs-assets/build-references.mjs), [reference results](audit-jobs-assets/references-results.json), [recovery results](audit-jobs-assets/recovery-results.json).
- [Independent lock correction probe](audit-jobs-assets/lockfix.ts), [bundler](audit-jobs-assets/build-lockfix.mjs), [results](audit-jobs-assets/lockfix-results.json).

Scripts use explicit isolated paths. Their initial seed phases expect new empty dataset directories; **do not rerun them against the retained populated datasets** without selecting fresh audit paths. Bundled executables preserve measured application code while the parent continues editing source. SQLite files and PNGs are wholly synthetic and remain available for inspection. No further benchmark process remains running.
