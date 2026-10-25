# Integrated engine audit — 2026-10-12

Read-only audit of UI `6f23d988a788a29de509f92af7c1f24f7e63c6b4` and main `b73abeaa06d7ecb67850dc9da8492090890729eb` **plus the concurrent working-tree changes present during inspection**. The UI/main status snapshots and hashes of the key inspected files are retained in [evidence](audit-engine-integration-evidence/). This audit changed no repository source, private data, artwork, credentials or publication state and made no commits. All probe mutations used disposable SQLite `:memory:` databases and existing technical fixture pixels.

Five concrete follow-ups were identified: repeated server asset hydration, repeated lifecycle graph hydration, unnecessary renderer cache replacement, missing shared-catalog pin comparison at the client response boundary, and coupling initial yard rendering to corrupt unrelated workshop metadata. The parent's concurrently added artifact index is a useful narrower improvement; it does not remove these repeated schema/JSON/hash/packing passes. No new owner-isolation failure or silent server-side pin substitution was demonstrated.

## Execution evidence and limits

- Node `v24.19.0`, Linux x86_64; container reports AMD EPYC 9V74, 5 logical CPUs and 18,440,136 kB host-visible memory. These are environment observations, not an allocated hardware guarantee.
- [Benchmark source](audit-engine-integration-evidence/chirp-audit-engine-bench.ts), [captured bundled implementation](audit-engine-integration-evidence/chirp-audit-engine-bench.cjs), [raw completed samples](audit-engine-integration-evidence/chirp-audit-engine-results.json), and [log](audit-engine-integration-evidence/chirp-audit-engine-bench.log) are retained. One warm-up, then three synchronous samples per group; counters wrap actual SQLite statement `get/all/run` executions and actual `JobRepository.artifacts/get` calls. Results serialization occurs after timing. Registry replacement timing includes `structuredClone` as a conservative stand-in for fresh transport objects.
- Flat presentation snapshots use distinct selected artwork IDs assembled from real reviewed/pinned rows. They are explicitly synthetic presentation inputs, not claimed real accounts with 24 authored species. The lifecycle measurements use actual retained jobs; only one real resident is selected in that database. Every package reuses the existing fixture's pixels, retains source frames, and passes both source and manifest reviews through the actual runner.
- **Timing contention:** parent full tests overlapped these probes. Millisecond values below describe this run and cannot establish an SLO, speedup, hardware recommendation or production capacity. Statement and hydration counts are the more reliable evidence. The benchmark bundle was captured before the parent's additive `pip_artifacts_owner_job` index edit. No post-index performance claim is made.
- Stopped only the audit benchmark PID on the parent's request to permit a quiet test retry. 18 completed sample groups / 54 measured calls are preserved. The chain-8 lifecycle overview (9 retained jobs including the base reference) completed immediately before termination and is included; chain-12 measurements are incomplete and excluded. No broad test suite or new browser server was launched for this audit; parent owns integrated regression verification.
- [Small correctness probes](audit-engine-integration-evidence/chirp-audit-integration-probes.ts) and their [actual results](audit-engine-integration-evidence/chirp-audit-integration-probes.json) demonstrate the shared pin mismatch, equal-byte cache-key change, and corrupt-workshop isolation seam. These are repository/schema/registry probes, not screenshot or GPU tests.

| Actual operation | Median ms, contended | SQL executions | Full artifact hydrations | Job reads | Returned JSON bytes |
| --- | ---: | ---: | ---: | ---: | ---: |
| flat 1 selected V4 packages sharing one V2 ancestor: yardAssets | 180.9 | 7 | 3 | 1 | 17,004 |
| flat 2 retained jobs: lifecycle.overview | 224.8 | 45 | 5 | 7 | 950 |
| flat 8 selected V4 packages sharing one V2 ancestor: yardAssets | 1,704.3 | 56 | 24 | 8 | 136,025 |
| flat 9 retained jobs: lifecycle.overview | 1,811.0 | 213 | 26 | 35 | 3,281 |
| flat 24 selected V4 packages sharing one V2 ancestor: yardAssets | 8,623.5 | 168 | 72 | 24 | 408,103 |
| flat 25 retained jobs: lifecycle.overview | 8,461.9 | 597 | 74 | 99 | 8,609 |
| chain 1 V4 + V2 ancestor, one selected: yardAssets | 197.9 | 7 | 3 | 1 | 17,004 |
| chain 2 retained jobs: lifecycle.overview | 243.5 | 45 | 5 | 7 | 950 |
| chain 4 V4 + V2 ancestor, one selected: yardAssets | 741.7 | 22 | 9 | 4 | 17,004 |
| chain 5 retained jobs: lifecycle.overview | 1,435.4 | 165 | 20 | 25 | 2,021 |
| chain 8 V4 + V2 ancestor, one selected: yardAssets | 1,402.0 | 42 | 17 | 8 | 17,004 |
| chain 9 retained jobs: lifecycle.overview | 4,299.8 | 437 | 54 | 63 | 3,449 |

The flat 24-asset response was only 408,103 bytes, yet performed 72 full artifact-list hydrations. A single selected package with eight V4 source ancestors required 17 artifact-list hydrations. The lifecycle graph rereads are visible even at five retained jobs (20 artifact-list hydrations).

## Findings and actionable acceptance

### EI-001 — P2: every yard read/command reconstructs each selected private asset independently

**Exact source:** UI `src/lib/server/assets/resolve.ts:36–59,85–100,138–173,200–220`; `src/lib/server/pipeline/repository.ts:304–338` (final inspected lines after the additive index); `src/routes/api/yard/+server.ts:9–14,144–157`; `src/lib/server/image-files/service.ts:424–442`.

`yardAssets` deduplicates a shared artwork ID correctly, but calls `resolveArtwork` with a fresh traversal context for every distinct selected artwork. Manifest and source reads separately call `jobs.artifacts`, each parsing and hashing the complete artifact list of that job. Source validation parses/normalizes retained bytes and reconstructs the package for comparison; shared ancestors are repeated across roots. For file-backed packages, source validation and reference validation both call the file authority, which verifies the retained blobs and extracts frames again. The latter extra file reads were traced, not timed in this fixture-only benchmark.

**Reproduction:** 1/8/24 independently reviewed V4 packages with one common reviewed V2 ancestor produced 7/56/168 SQL executions and 3/24/72 full artifact hydrations. This work runs for rename, object move, preferences and weather commands because each returns a full `yardAssets` response. These synchronous calls occupy the serving Node event loop. The client-only 96-actor admission does not bound server hydration or transport: `scene-resource-budget.ts:43–61` runs after the server has already resolved all selected assets.

**Smallest next slice:** a request-scoped, owner-bound resolution session with shared exact-artifact reads and checked-source/package results across all selected roots. Keep ancestry/path limits distinct from memoized completed nodes, and preserve corruption, unavailable-file, review, owner and exact-pin checks. Prefer this before any process-wide cache with revocation/restoration invalidation obligations. The parent's query-only index reduces row lookup work, but cannot remove repeated parsing, hashing or reconstruction.

**Acceptance:** a count-based 1/8/24 shared-ancestor regression reads each unique job/artifact payload once per response; one changed/rejected/missing dependency affects exactly the dependent entries; identical artwork selected by 96 residents resolves once; distinct owners never share request memo entries; corrupt/missing PNG/source and 32-depth/64-visit rejections remain fail-closed. Explicitly decide a bounded server/transport presentation policy for retained yards larger than the renderer budget without deleting residents or silently discarding selected pins.

**Dependencies:** PB-014, PB-020, PB-011-B and EN-003; no art/provider/GPU decision required. The existing PNG authority and generic V2/V3/V4 readers remain authoritative.

### EI-002 — P2: lifecycle overview repeatedly scans a graph it has already hydrated

**Exact source:** UI `src/lib/server/assets/lifecycle.ts:107–163,201–220,261–337,339–394`.

`graph()` already visits each retained package and validates its input/artifacts. `overview()` then calls `selectablePackage()` independently for every package, opening another complete dependency traversal. It also reruns label reads and retained-size queries per package. For a linear ancestry, the same sources are hydrated once for graph construction plus repeatedly for every descendant. This is distinct from API paging: adding an archived-history page does not change `overview`'s internal graph walk.

**Reproduction:** 2 retained jobs require 5 artifact hydrations / 45 SQL statements; 5 jobs in a chain require 20 / 165. For 25 flat retained jobs sharing one ancestor, overview alone requires 74 hydrations / 597 statements. All data was valid and within existing graph limits. This is repeated work, not a claim that any per-row read is automatically unacceptable.

**Smallest next slice:** derive selectability, dependency reasons and reverse-reference counts from one transactionally consistent graph; memoize package state once per overview and batch size/label reads. Retain explicit unavailable/incomplete scan status. Do not mistake archive for delete or reject an already retained pin because new selection is blocked.

**Acceptance:** linear-chain/diamond-graph counters grow with unique packages/edges, not sum of ancestry lengths; 512-job/32 MB and depth/cycle behavior unchanged; archives block new selection while existing pinned rendering stays available; unavailable/corrupt nodes give the same retention and cleanup decisions; owner A's graph cannot affect owner B. A test should verify both rendering retention and new-pin refusal after archiving a dependency.

**Dependencies:** PB-022/PB-022-A and EN-003. Coordinate with the parent's archive-history and admission changes; this report does not edit that work.

### EI-003 — P2: an unchanged asset response discards renderer caches

**Exact source:** UI `src/routes/+page.svelte:323–326`; `src/lib/components/YardScene.svelte:155–159`; `src/lib/engine/renderer.ts:815–817,602–612`; `src/lib/assets/registry.ts:60–63,89–99,113–125`.

Every ordinary yard command assigns fresh deserialized `assets`. Renderer update compares only array identity, replaces the registry and invalidates geometry. Registry replacement increments the revision included in every key even when the pin/status/manifest bytes are unchanged. The fallback registry is also recreated from the new assets value. Thus rename/move/weather updates cause avoidable schema work and new geometry acquisition for existing poses. This is cache churn, not a demonstrated stale-version rendering bug or a resource leak.

**Reproduction:** the correctness probe records `identicalAssetReplacementChangesRendererKey: true`. For 24 already-resolved fixture assets, warm resolution median was 0.008 ms; equal-byte clone/replacement/resolve was 66.3 ms before any GraphicsContext/GPU work. Eight assets were 0.006 versus 23.2 ms. These CPU figures are contended and include cloning; they do not measure browser jank or GPU upload duration.

**Smallest next slice:** identity-preserving reconciliation of validated entries within the same owner epoch; retain unchanged registry/geometry entries and invalidate only changed exact content/status. Do not merely suppress `replace` using artwork ID: same-ID corrupt content, changed density/version, revoked catalogs, removed assets, restored data and account transitions all need correct invalidation.

**Acceptance:** an actual-Pixi resource regression for a rename-equivalent equal response preserves the context and does not increase geometry build count; changed manifest/version/density invalidates and updates bounds; revoked/missing assets fall back; removal releases resources; owner switch clears old entries; concurrent renderer teardown stays isolated. Repeat with mounted SVG fallback to prove presentation parity. Preserve fixture-only labeling and all current allocation limits.

**Dependencies:** PB-011-B/PB-011-C; source-density contracts and reviewed context teardown. This audit makes no visual approval or physical-device performance claim.

### EI-004 — P2: client response guards accept a different shared catalog release than the retained pin

**Exact source:** UI `src/lib/client/contracts.ts:16–40`; contrast the correct server exact matching at `src/lib/server/assets/catalog-selection.ts:190–219` and the structural-only entry validation at `src/lib/assets/registry.ts:17–41,84–99`.

`validateAssets` checks ready entries' species and `animationPin` against the snapshot artwork. It does not compare `catalogPin`. Both animation pins are undefined for shared entries, so the check passes when the response carries a different shared release for the same artwork ID/species. The registry accepts that structurally valid entry as ready.

**Reproduction:** the probe created actual local fixture releases 1 and 2 using the existing trusted fixture test adapter in an in-memory database, selected release 1, retained its snapshot, then obtained a real ready release-2 response and substituted its entry under the first artwork ID. Both `yardReadResponseSchema` and `yardCommandResponseSchema` accepted the mismatch; registry resolution returned `ready`. Retained/rendered SHA values and release numbers are preserved in the JSON evidence. No source pixels were invented. The server resolver itself correctly rejects a forged artwork/pin pairing, so this demonstrates a client malformed-response guard defect, not a server authorization bypass.

**Smallest next slice:** compare the correct mutually exclusive exact pin family against the retained artwork at the common client yard-response boundary; validate ready catalog availability consistently without changing shared catalog production eligibility.

**Acceptance:** retain a valid release-1 response; reject changed `catalogKey`, `releaseVersion` or `renderSha256` independently; reject swapping private/catalog pin families; preserve valid private V2/V3/V4, shared V2, unavailable/revoked/legacy responses and owner-switch behavior. Exercise the same guard through command, GET and page-data validation.

**Dependencies:** PB-003, EN-001. No external release authority or real art is required to fix this guard. Private V4 support does not authorize publishing V4 into the current shared V2 catalog contract.

### EI-005 — P3 recovery isolation: an unrelated corrupt workshop job prevents initial yard rendering

**Exact source:** UI `src/routes/+page.server.ts:5–8`; `src/lib/server/workbench/jobs.ts:8–10,29–46,49–62`; `src/lib/server/pipeline/repository.ts:173–194`; existing committed-command isolation at `src/lib/server/runtime.ts:163–174`.

Initial page load obtains `workbenchPage` before returning the yard. `workbenchJob` obtains/validates the job outside its artifact fallback catch. One damaged retained job input digest therefore throws through page load even when the yard and selected assets are intact. The already implemented `confirmedWorkbenchPage` fallback protects mutation acknowledgement, but is not used for boot. This is a recovery containment issue under damaged storage, not a demonstrated normal API command that can corrupt a job.

**Reproduction:** in the disposable database only, change an unrelated queued job's `input_digest` to a different 64-hex string. `jobPage` throws `Pipeline input digest mismatch`; `yard.snapshot` remains readable and selected shared asset resolution remains ready. No artifact/review trigger was disabled and no real data was touched.

**Smallest next slice:** a typed initial-workshop-unavailable state that preserves valid yard/auth data and reports a bounded refresh error; do not silently turn a corrupt job into valid metadata or relax its digest check.

**Acceptance:** bad input digest, oversized/corrupt job metadata and corrupt artifact scenarios leave the yard usable with explicit workshop error; jobs remain retained and inaccessible to wrong owners; repeated refresh cannot overwrite valid browser state; restoring a valid job page recovers. Existing committed-command refresh-error behavior remains intact.

**Dependencies:** EN-003 and PB-014/PB-022; no external input required.

## Integration trace and supported boundaries

| Boundary | Actual local authority and integration | Evidence / limits |
| --- | --- | --- |
| Auth → owner state | `hooks.server.ts:81–119` resolves verified account or opt-in development identity, session binding and request admission. `server/http.ts:13–23,86–99` supplies the owner from locals and bounds same-origin JSON commands. Pipeline and image reads filter by owner. | No owner IDs are taken from the yard command as authorization. Account mail/OIDC provider setup is an external configuration dependency; this audit did not activate it. |
| Findings → residents | `server/storage/repository.ts:155–206,269,396,433` owns read/transaction/write and stable resident operations; `domain/yard.ts:359–403` derives findings from retained evidence/corrections and projects temporary expiry. Manual findings do not assert model detection. | This is functioning local domain storage. Not a verified Merlin/eBird/Cornell source adapter, biological identity proof or real detection claim. |
| Audio → manual confirmation | `server/recordings/confirmation.ts:31–50,143–223` requires retained approved real-recording provenance, explicit owner confirmation and one shared SQLite transaction for event plus receipt; replay detects restored-away evidence. Main `backend-inference/app/audio_pipeline/service.py:223–247` checks current recording/model/license before reading private bytes. | Main `audio_pipeline/api.py:143–159,297–327` defaults to unconfigured model and loads optional ONNX only from explicit configuration. Synthetic providers cannot process ordinary recordings. No compatible real model/weights or biological accuracy were demonstrated here. |
| Residents → objects/yard | UI `/api/yard` routes ordinary mutations to one YardRepository. `storage/repository.ts:510,559` keeps arrangement and inventory in private owner state; callers validate stale placements/receipt semantics before replacing browser state. | Local inventory, arrangement, routines and illustrative weather remain intact. The audit did not change the visual shell or saved state. Server asset work currently lengthens unrelated mutation responses (EI-001). |
| Assets → renderer | `assets/resolve.ts` derives exact approved private pins, verifies owner/species/digests/provenance/source equality and returns unavailable on damaged or missing content while preserving selected pins. `manifest.ts:13–17` admits V2/V3/V4; `manifest.ts:25–40` explicitly falls back missing/unknown behavior to idle and still fallback for sleep/play/nest. | Registry cannot by itself prove repository review; the server owns that decision. Shared release identity has its own authority and currently supports V2; its incompatibility with private V4 is explicit. EI-004 is the client shared-pin comparison gap. |
| Source density → Pixi/SVG | `pose-geometry.ts:8–24,38–89,108–109` applies V4 density to physical clearance, support/pivot transforms and hit inversion; legacy versions retain their mapping. `presentation.ts:5–33` keeps V4 scaling separate from fixture illustrative profiles. | Local contracts support detail independent of physical extent. No 32px or other art canvas is user-approved; diagnostic geometry and fixture bird pixels do not establish anatomical/plumage fidelity. |
| Resource bounds → presentation | `scene-resource-budget.ts:12–19,43–96,130–154` limits 96 candidates, 32,768 primitives, 262,144 retained rectangles, 4,096 backing edge, 4,194,304 backing pixels and DPR 2. Private clip/frame/package limits remain in manifest/intake schemas. | These are protective allocation budgets. They are not a measured physical GPU capacity, authored-art quality target or proof of 60 FPS. Server hydration and response bodies are a separate boundary. |
| References → generation jobs | `server/runtime.ts:77–78,138–147` registers Commons metadata discovery and a local diagnostic generation provider, with separate admission/review/completion authority. Ref generation endpoint requires owner and only admits the exact versioned pipeline. | Real local reference retention/review/revocation and diagnostic execution exist. Commons network availability, approved concept pixels, licensed production generation, fidelity review and GPU/model choice remain separate inputs. No artwork generation/provider/network search ran in this audit. |
| Jobs → restart/recovery | `pipeline/runner.ts:43–85` requires the exact definition/provider, persists version identity and deadlines; repository claim/complete paths fence leases. Runner advances are explicit requests, not evidence of a distributed autonomous scheduler. `operations/lifecycle-recovery.ts:37–62,67–135` validates image/lifecycle/catalog/arrival authorities and reconciles a separately supplied, digest-pinned reference authority when available. | An initialized reference store still refuses cold restore without that explicit authority. Current source supports the bounded receipt path; older documentation claiming all reference restore unsupported is narrower/outdated. Freshest external receipt custody, stopped writers and distributed worker cleanup remain operating dependencies, not accomplished by a local contract test. |

## Concrete next-work checklist

1. **Finish the parent's current bounded index/read-admission slice and quiet regression retry.** Review the new index's query plan and old-store reopen behavior separately; do not claim it fixes whole-graph hydration. Preserve the timeout observed under parallel load rather than relabeling it as a pass.
2. **EI-004: close shared catalog response pin validation.** Smallest correctness change, existing contracts, negative release/hash/family probes; no provider dependency.
3. **EI-001/EI-002: request-scoped unique-source reads and one lifecycle graph.** Freeze deterministic query/hydration count tests first; preserve authority/rollback/archive semantics. Measure again in a quiet, controlled run after the index before choosing a response/admission budget.
4. **EI-003: keep unchanged render assets stable.** Requires actual-Pixi plus Svelte/fallback integration and owner/version/revocation tests. Treat this as a separate reviewed change because cache invalidation crosses presentation and account boundaries.
5. **EI-005: isolate initial workshop failure.** Requires typed page error state and browser boot recovery fixture; retain all storage integrity checks.
6. **Keep product/external gaps explicit.** PB-021-B actual species art/fidelity remains unaccepted; PB-011-B physical-device measurements, EN-004 real audio models, EN-006 original autonomous worker, EN-008 real source import, EN-009 live weather and provider/account operations are not established by this audit. None requires replacement placeholder art in this engineering slice.
