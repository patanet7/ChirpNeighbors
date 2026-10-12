# Targeted contracts, storage and authentication audit — 2026-10-12

One new medium-severity correctness defect was reproduced: a yard can fit the accepted storage limit while its response exceeds the browser client's limit. No new owner-isolation or session-authentication defect was found in the inspected paths. The new archive endpoint initially lacked an authority-inventory entry; the implementation agent corrected it during this audit and the final inventory check passes.

Scope: UI `/workspace/archive-history/birdsong-yard-sprites` at HEAD `6f23d988a788a29de509f92af7c1f24f7e63c6b4`; main `/workspace/archive-history/ChirpNeighbors` at HEAD `b73abeaa06d7ecb67850dc9da8492090890729eb`, including concurrently edited archive-history work. These were not frozen source trees. Exact inspected core-source hashes and unchanged-baseline evidence are in [the receipt](audit-contracts-storage-auth-receipt.json). No repository source edits, commits, publication, production data or external calls were made by this reviewer. Probe code and evidence live outside both repositories.

## CSA-04 — Medium — Accepted yard states produce responses the client cannot read

**Source:** UI `src/lib/server/storage/repository.ts:179` permits a serialized owner aggregate up to 16 MiB. `src/lib/domain/yard.ts:394` includes that aggregate plus derived effective evidence and Finding event-ID lists in a snapshot. `src/routes/api/yard/+server.ts:13` and `:144` return the entire snapshot; its POST body limit at `:17` is 20,000,000 bytes. The browser independently rejects response bodies over 16 MiB at `src/lib/client/service.ts:17` and `:73`.

**Reproduction:** The standalone [probe](audit-storage-probe.ts) uses the real `YardRepository`, snapshot code and client `parseResponse`, with an in-memory database and synthetic fixture events whose observation times are unknown. A valid 45,000-event backup restores successfully:

| Measurement | Bytes / result |
|---|---:|
| Accepted stored data | 14,220,847 bytes |
| Derived `{snapshot, assets: []}` response | 20,161,126 bytes |
| Client response budget | 16,777,216 bytes |
| Real client decoder | `InvalidServiceResponse` |
| Later preference change | Committed `reducedMotion=true` |
| Later command response | 20,161,157 bytes; exceeds the same decoder budget |

The backup fits both the storage ceiling and the restore request ceiling. No assets are required to trigger the issue. Another synthetic owner's events remained empty. This creates successful writes followed by an apparent client failure, and ordinary API refresh cannot repair the client view. The demonstration used the actual repository and decoder without starting an HTTP server; the route's response construction was inspected directly.

**Acceptance:** Restore the above valid backup and successfully load its evidence/residents through the supported client. A preference, manual-finding or inventory command must have an admissible acknowledgement and current state after committing. Test bodies with and without `Content-Length`, plus exact replay of an uncertain inventory command. Every accepted state must have a bounded readable representation, or admission must fail before mutation with a clear error. Existing retained evidence and backups must remain accessible; do not silently truncate them or merely disable the client bound.

**Dependencies / next slice:** PB-001, PB-002, PB-007, EN-001 and EN-003. Coordinate server projection/pagination, client reconciliation and versioned shared response contracts. A Findings page/query boundary separated from the lightweight yard state is a coherent direction; the current aggregate has no SQL index that can solve this serialized-response mismatch.

**Evidence:** [Results](audit-storage-probe-results.json), [log](audit-storage-probe.log), [probe source](audit-storage-probe.ts). This defect was reported promptly to the integration owner and remains unfixed in this audit.

## What the inspected flow actually enforces

- **Session → owner:** `src/lib/server/auth/service.ts:230` asks the pinned auth library to verify the cookie and read its store with cookie-cache disabled; only a verified email yields `user:<verified user id>`. `src/lib/server/http.ts:15` derives the owner from verified locals. Yard commands are strict schemas and do not accept an owner field. The Python audio verifier uses a fixed BFF origin, validates the shared session response and rejects development identities unless explicitly enabled; it does not trust a browser owner header.
- **Document session fence:** `src/lib/server/auth/session-binding.ts:28` rejects stale or missing bindings on authenticated private API mutations. `src/lib/auth/session-client.ts` keeps an immutable document binding and aborts pending headers/bodies when it changes. These fences supplement authentication; the binding alone cannot authenticate. Tests cover stale sessions, owner changes, malformed bindings and cancellation. Real SMTP/OIDC credentials and transport acceptance are not established by the synthetic provider tests.
- **Findings → residents:** `repository.ts:229` binds source identity to immutable evidence and rejects conflicting batches atomically. Manual insertion invokes the trusted arrival hook within the same transaction. Corrections use expected revision plus immutable retry identity (`:299`) and deliberately do not create visits or alter residents. Unknown/future/historical timestamps do not create a recent visitor (`:349`); promotion is explicit. Raw imports cannot self-grant trusted arrival authority. These are functioning local paths, not evidence of a real Cornell adapter or validated model output.
- **Inventory and write isolation:** Each aggregate mutation reads after `BEGIN IMMEDIATE` and writes before commit (`repository.ts:131`, `:190`). Nested operations use savepoints. Inventory checks the immutable request receipt before the placement CAS (`:558`), so exact retries survive later state changes, conflicting retries fail, and fresh stale intents are rejected. This is semantic CAS for inventory/evidence; legacy add/move/remove, rename/preferences and explicit pin commands do not all share a global revision CAS. Do not claim every mutation has one.
- **Backward compatibility:** Older persisted V2 environment data hydrates missing inventory/receipts; current response schemas require explicit fields. Tests cover legacy placement retention, explicit zero stock, migration/version refusal, corrupt rows and unchanged other owners. Application preflight validates all bounded migration-ledger rows before repository initialization; auth startup verifies its schema marker and the pinned library's actual schema. This is known-version compatibility, not automatic migration of unknown future schemas.
- **Privacy:** Evidence, source metadata and location remain in private aggregates. Shared views use the explicit safe projection; imported private species labels do not become public catalog identities. No new privacy bypass was found in this scope. Production account policy, account-wide erasure, offline-copy custody and provider/model/hardware acceptance remain distinct dependencies.

## Isolated concurrency and query evidence

The [concurrency probe](audit-storage-concurrency-probe.ts) used two real repository connections and a worker thread holding a SQLite write transaction for 300 ms on a disposable file. WAL mode and a 5,000 ms busy timeout were confirmed. A reader returned the previously committed palette in **1.16 ms** while the writer held its reservation. The next repository write waited **369.55 ms**, then retained the worker's committed palette as well as its own preference change. It did not overwrite a stale aggregate.

A stale inventory intent from the other connection returned `STALE_PLACEMENT`; changed-content reuse of its request ID returned `CONFLICT`; exact retry retained one receipt and did not repeat the return operation. Another owner's receipt count stayed zero. [Results](audit-storage-concurrency-results.json). This proves the exercised locking/retry cases, not multi-process throughput or a fairness/latency SLO. Synchronous SQLite waits still occupy the calling Node thread. The first probe setup used an invalid palette and was rejected before the lock experiment; that setup failure is retained in `audit-storage-concurrency-invalid-fixture.log`.

`EXPLAIN QUERY PLAN` confirmed:

- Owner aggregate reads use `sqlite_autoindex_yard_owners_1 (owner_id=?)`.
- Arrival deduplication uses the covering `(owner_id,event_id)` primary index.
- Pending arrivals use `yard_arrivals_pending (owner_id,state)` then a temporary sort for JSON `admittedAt`. The per-owner ledger is capped at 256 and the result at 20. This bounded sort did not justify another index in the inspected workload.

The synthetic 1k/10k/45k-event snapshot reads took approximately **43/125/799 ms**; restore took **45/419/1,895 ms**. These are single-run diagnostic measurements on this shared workspace, not production benchmarks. They show the cost of parsing/projecting the entire JSON aggregate; adding relational indexes alone cannot address it. The 45k mutation plus subsequent read took about 2.45 seconds in the probe.

## Contract authority and verification

| Check | Result / scope |
|---|---|
| UI storage/session/arrival tests | 119 passed, 8 files |
| UI synthetic auth/HTTP/development identity tests | 51 passed, 3 files |
| Python Finding/session-verifier authority tests | 17 passed |
| Zod/Ajv/Python/lossless roundtrips | 751 golden cases passed |
| Paired deterministic contract export | Passed in both repositories |
| Compatibility baseline | 273 digests passed; existing baseline entries unchanged, only two entries for the new paired history schema added |
| Final authority inventory | 63 HTTP/SSR operations, 115 boundaries, 34 explicitly declared residual gaps |
| Cross-repository JSON comparison | All 149 common contract JSON files byte-identical; six additional main-only audio schema/fixture files |

The initial inventory gate correctly failed on the new `src/routes/api/asset-lifecycle/packages/+server.ts#GET`. Its declaration was added by the implementation agent and the final gate passed; this is closed in-progress integration bookkeeping, not a remaining runtime finding. Both logs are retained. Inventory counts prove declared coverage, not that every semantic branch or real provider works. The golden count is not added to the unit-test count as an interchangeable quality score.

Logs: `audit-storage-representative-tests.log`, `audit-auth-authority-tests.log`, `audit-python-authority-tests.log`, `audit-contract-roundtrips.log`, `audit-contract-exports.log`, `audit-contract-compatibility.log`, `audit-contract-inventory.log`, `audit-contract-inventory-final.log`.

**Existing open limitation:** CSA-03 / EN-003-C remains visible in `src/hooks.server.ts:131`: request admission is released when the response object is returned, before a streaming response finishes. The prior streaming reproduction is documented in the canonical architecture backlog. This audit reconfirmed the source path and did not repeat or count that older experiment as a new pass.

No full quality/build/browser/production gate was run for this audit, and no approved species-art, real model, real import-provider or hardware claims follow from these results. The parent owns frozen verification of the concurrently edited archive feature.
