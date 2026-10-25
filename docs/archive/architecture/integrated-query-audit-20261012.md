# Integrated architecture and query audit — 2026-10-12

The local engine has real shared authorities across authentication, owner storage, findings/residents, yard inventory, reviewed assets, job leases and recovery. It is **not uniformly optimized or reliable at every accepted data size**. The clearest outstanding correctness failure is that a valid stored yard can produce a response exceeding the client's 16 MiB bound. Passing functional tests alone do not establish performance or production readiness.

This record reconciles four independent audits. It is evidence, not another backlog: the [canonical task index](../../delivery/product-behavior-and-ideas.md#architecture-follow-up) owns status through its PB/EN entries. The archive-history implementation and verification receipt are [recorded separately](../delivery/archive-history-local-20261012.md). This task stays local; no publication, deployment, provider, credential, original data or visual-shell changes are implied.

## Findings and ownership

| Evidence alias | Result / canonical task |
| --- | --- |
| JA-02 / ARCH-01–04 | Archived history repaired locally: separate bounded read, authenticated cursor, byte guards, request admission and accessible retries. [PB-022-A](../../product/artwork-and-assets.md#pb-022-a--keep-archived-history-reachable) owns final acceptance. |
| JAQ-01 | Added exact owner/job artifact index with old-store/reopen/lock/isolation/query-plan tests. Further per-request work belongs to [PB-014-A](../../product/artwork-and-assets.md#pb-014-a--reuse-retained-asset-validation-within-one-request). |
| JAQ-02 | Standalone lifecycle reads use `BEGIN`, with mutations and nested command projection retaining their write transaction. Independently verified committed reads during a second WAL writer. [PB-022-A](../../product/artwork-and-assets.md#pb-022-a--keep-archived-history-reachable). |
| JAQ-04 | Deep cursor reads now use one concrete rowid ceiling; no nullable-OR filtering. Existing cursor and byte-truncation semantics retained. [PB-022-A](../../product/artwork-and-assets.md#pb-022-a--keep-archived-history-reachable). |
| EI-004 | Exact shared catalog key/release/hash checked at the common browser response boundary, with negative cases. Server authority was already exact. [EN-001](../engineering-roadmap.md#en-001--single-contract-authority-generated-consumers-and-strict-compatibility-gates). |
| EI-005 | Unreadable initial jobs no longer prevent a valid yard/retention panel from loading. Explicit existing page controls offer working refresh/retry; invalid jobs remain unadmitted. [PB-022-A](../../product/artwork-and-assets.md#pb-022-a--keep-archived-history-reachable). |
| CSA-04 / RQ01 | **Open P1:** stored-data and transport budget mismatch. [EN-003-E](../engineering-roadmap.md#en-003-e--bound-yard-responses-without-losing-retained-history). |
| EI-001 | Open P2: repeated retained-source resolution per selected artwork. [PB-014-A](../../product/artwork-and-assets.md#pb-014-a--reuse-retained-asset-validation-within-one-request). |
| JAQ-03 / EI-002 | Open P2: repeated whole-graph hydration/reverse-reference scans. [PB-022-B](../../product/artwork-and-assets.md#pb-022-b--project-lifecycle-state-from-one-bounded-graph). |
| EI-003 | Open P2: equal-byte asset responses invalidate renderer geometry. [PB-011-D](../../product/yard-and-behavior.md#pb-011-d--retain-unchanged-render-assets-within-one-owner-epoch). |
| RQ02 | Open P2: repeated whole-owner snapshot/projection/validation, resident-origin scans and empty arrivals. [EN-003-F](../engineering-roadmap.md#en-003-f--reduce-repeated-owner-snapshot-work). |
| RQ03 | Open P2: duplicate import/correction scans and unchanged inventory retry writes. [EN-003-G](../engineering-roadmap.md#en-003-g--index-event-identities-within-each-import-transaction). |
| RQ04 | Open P2: synchronous writer contention blocks unrelated work for 5 seconds. [EN-003-H](../engineering-roadmap.md#en-003-h--bound-synchronous-writer-waits-and-preserve-retries). |
| CSA-03 | Existing open streaming admission-lifetime task remains [EN-003-C](../engineering-roadmap.md#en-003-c--hold-read-admission-through-stream-completion). Not a newly discovered duplicate. |

## Measured results and limits

Shared cloud environment: AMD EPYC 9V74, five visible CPUs with a **four-core cgroup quota**, **16 GiB RAM**, Linux 6.18.44, Node 24.19.0 / SQLite 3.53.3. Runtime probes used tmpfs; jobs used disposable local SQLite WAL files. Some measurements overlapped other engineering work. These are instrumented warm synthetic observations, not production SLOs, cold-disk tests or physical GPU/mobile results. SQL counts are executed statements/returned rows, not VM rows visited. Each report records sample counts, bundles/source hashes and query plans.

| Isolated probe | Evidence |
| --- | --- |
| Ten jobs, 8,192 retained jobs/artifacts | Same-data artifact index A/B: median **317.35 → 29.77 ms**; 64 SQL statements and 82 returned rows unchanged. Exact owner+job search replaces owner-wide artifact lookup/temp sort. |
| Ten package-history entries, same database | Median **272.10 → 22.32 ms**; 105 SQL statements / 92 returned rows unchanged. The index fixes lookup work, not repeated validation. |
| Lifecycle overview, 256 packages | Still **4,103 statements**, about **1.27 s** indexed median. At larger byte budgets, the conservative scan refuses hydration; an empty incomplete overview is not a scaling success. |
| Deep cursor ID query, 8,192 rows | Conditional-bound median **0.2932 ms** versus concrete-ceiling candidate **0.0112 ms**. Application SQL now uses that concrete bound; traversal tests prove semantics. |
| Accepted large yard, two independent reproducers | 45k-event stored state **14,220,847 B** yields **20,161,126 B** read response. Separate 30k-event shape stores **12,459,063 B**, commits rename, then yields **17,117,200 B** success response, rejected by the actual **16,777,216 B** client limit. No assets are needed to reproduce. |
| Owner row / JSON work | Owner lookup already uses the primary key. At 10k events, repository snapshot ~**240 ms**, page-boundary validation ~**1.14 s**, rename ~**482 ms**. A constant one-row SQL count still hydrates growing history. |
| Duplicate import | 1k exact retries against 10k events took **4.21 s** inside the write transaction. No new events were needed to trigger repeated scans/full rewrite. |
| Contention | Separate-owner synchronous writer wait ~**5,009 ms** at normal busy timeout; WAL read ~**2.5 ms**. New lifecycle read-lock fix separately sees committed revision 1 while another connection holds uncommitted revision 2. Mutation remains blocked under the probe lock. |
| Renderer entry reconciliation | Equal-byte replace changes registry keys; 8 warm entries ~**0.006 ms** versus clone/replace/validation ~**23.2 ms** before GPU work. Contended pre-index measurements support the mechanism, not a device-jank claim. |

A first full UI run during parallel auditing passed 2,129 tests and hit one existing ancestry-depth timeout. Audits were stopped, and the test passed in the quiet focused rerun without raising its timeout. Final frozen results are recorded in the delivery receipt. Do not combine historic and final counts into a claim of a new complete 97-gate system run.

## End-to-end trace

| Flow | Actual working local boundary | Explicit remaining boundary |
| --- | --- | --- |
| Auth → owner | Maintained auth, server-derived owner, same-origin/session binding, owner predicates and safe shared projection. Synthetic account/HTTP/session tests and owner/CAS probes passed. | Real mail/OIDC operations and production setup remain external; no credentials were changed. |
| Findings → residents → yard/inventory | One transactional owner aggregate, validated findings, stable residents, placement CAS and idempotent inventory receipts. Concurrent updates preserve committed state. | Full-history JSON cost and oversized response failure remain open; manual/fixture evidence is not real model identification. |
| Reviewed assets/references → resident renderer | Separate source/manifest reviews, immutable private pins, rights/provenance, exact dependency checks, manifest V2/V3/V4, explicit missing/corrupt fallback and density-aware geometry. | Actual approved art/photographs, species fidelity and physical hardware acceptance remain unavailable. Shared catalog supports V2; private V4 does not authorize public V4 release. |
| Jobs → lease/restart/recovery | Versioned pipeline definitions, owner scope, write-serialized claim/complete, token/expiry fences, atomic immutable artifacts and receipt-backed recovery. Local fixture/diagnostic execution is real. | The original independent autonomous worker and real provider/model execution are not integrated proof. No fabricated Cornell integration or new provider calls. |
| Recovery → retained authority | Hash/schema/lineage checks and explicit reference-authority restore path; missing authority fails closed without replacing the source. | Latest independently retained receipt custody and stopped-writer operating procedure remain necessary. |

## Preserved evidence

- [Contracts/storage/auth report](../delivery/query-audit-20261012/audit-contracts-storage-auth.md), including 170 targeted UI tests, 17 Python authority tests, 751 cross-language cases, SQLite/CAS and transport-limit probes.
- [Jobs/assets/recovery report](../delivery/query-audit-20261012/audit-jobs-assets.md), with 32/256/2,048/8,192-job samples, EXPLAIN plans, index A/B and read-lock proof.
- [Engine integration report](../delivery/query-audit-20261012/audit-engine-integration.md), with captured pre-index source and exact shared-pin/boot/caching probes.
- [Runtime query report](../delivery/query-audit-20261012/audit-runtime-queries.md), with four history sizes, batch/no-op/owner-contention and decoder evidence.
- [Evidence manifest](../delivery/query-audit-20261012/evidence-sha256.json). Audit reports describe the inspected snapshot; the finding table above distinguishes later local repairs from still-open work.
