# Executable full-system delivery matrix

The [consolidated task index](product-behavior-and-ideas.md) owns current decisions,
requirement status, architecture boundaries, behavioral acceptance, exact tested
revisions and residual gaps. `matrix.json` is its executable delivery graph, not a
competing product roadmap or production-readiness percentage. Matrix implementation
labels must be read with the named checkpoint and active-wave state; implemented
code or an older passing aggregate does not verify a changed candidate.

The historical [environment checkpoint](environment-verified-20261009.md) records
its complete 75-gate passing run, exact source commits and retained failed attempts.
The prior [74-gate ontology checkpoint](ontology-verified-20261009.md) remains preserved.
The [subsequent ESP32 integration](esp32-integrated-20261009.md) records the actual fetched head, local merge, 52 host tests, eight native tests and 25/25 selected regression gates. Board/simulator setup remains blocked; this selected run does not replace the complete environment proof. The index limits completion to named behavior and fixture scope.

The current [animation/content/reference-discovery checkpoint](animation-planning-20261011.md)
records 94/94 frozen gates and its exact tested source revisions.
Versioned recipe composition and bounded Commons metadata discovery remain separate
from image-generation providers and approved species artwork. The 33- and 61-gate
interrupted attempts remain partial; later documentation/evidence commits are
reported separately from tested source commits.

The historical checklist below records earlier bounded waves and their original
counts. Later checkpoint links and the authoritative index supersede stale current-
status wording without rewriting historical evidence. The [initial integrated
checkpoint](checkpoint-20261008.md) retains its exact original verification.

```sh
python3 scripts/delivery_matrix.py --check
python3 scripts/delivery_matrix.py --run baseline --ui-repo ../birdsong-yard-sprites
python3 scripts/delivery_matrix.py --run combined-browser --ui-repo ../birdsong-yard-sprites
```

The implementation waves assigned contract generation/quality, auth/session,
private media/frontend, audio pipeline, image pipeline and reliability/operations
to separate same-workspace agents and local branches. The integration owner owns
this matrix, aggregate gates, shared package/config changes and final integration.
Generated files are owned by their generator's workstream. Coordinate dependency
changes before editing shared manifests. Agents must inspect existing contracts
and preserve existing yard/media storage; no replacement application is planned.

Existing Zod yard/finding/scene/recording boundaries remain authoritative. New
Python-owned audio service boundaries use Pydantic v2 and generated JSON Schema/
TypeScript counterparts. Do not hand-maintain equivalent wire models in both
languages. The UI's `docs/contract-platform.md` records ownership; executable
cross-language tests enforce the exported boundary behavior.

Worker `c08624d3` remains outside this workspace after the approved supported transfer failed before bytes. The original ESP32 branch was fetched at `99c01c6b41de67e2f5e11b46e8e7488a1a33aa4c` and locally merged at `4ce5fb535c38f67a3f31caf3a2c7ebfb988a9ceb` after the environment checkpoint. See EN-006/EN-007 in the [current index](product-behavior-and-ideas.md) and the [integration evidence](esp32-integrated-20261009.md); the [original handoff blocker](approved-handoff-blocker-20261008.md) is historical for ESP32. Neither implementation was duplicated.
Approved species artwork, real-source samples, production identity/mail credentials,
model licenses and external provider/hosting configuration remain explicit external
gates. Local coding, synthetic fixtures and ordinary package dependencies proceed.

## Concrete task checklist

The implementation below exists locally; final integrated verification is recorded
in the checkpoint report. Dependencies are also encoded in `matrix.json`.

- [x] Contract platform: authoritative Zod or Pydantic models, generated counterpart
  types/runtime guards, deterministic drift checks and strict optional/indexed
  access. Accept when both corpora agree on all 129 valid/invalid cases and generated
  output is unchanged. This is the prerequisite for every service/client boundary.
- [x] Species assets: versioned manifests, clip/frame bounds, explicit still-idle
  fallbacks, content/version cache keys, provenance/license intake, deterministic
  packaging, review/reject/pin workflow and renderer lookup through reviewed pins.
  Accept corrupt/missing manifests and animations without losing actors or owner
  state; run the manifest and asset-pipeline browser suites plus asset unit tests.
- [x] Owner persistence: transactional migrations, retry-safe upload receipts,
  bounded pagination, tombstones, private files and generation fences. Accept the
  recording/browser tests, reopen tests and interrupted-migration recovery without
  changing existing rows or allowing a foreign owner to read media.
- [x] Identity: durable library-backed email-link/Google protocol boundaries,
  sessions, logout, replay/expiry and atomic private auth initialization. Accept
  22 auth unit cases, 19 provider/browser checks and 33 actual app/local-SMTP/signed-Google-mock assertions; missing production
  configuration must fail closed. Depends on contract and storage boundaries.
- [x] Frontend: checked server responses, lost-response reconciliation, private
  upload/play/delete, typed analysis configuration, restored raw candidate UI and explicit confirmation.
  Accept mobile/keyboard, cancellation, retry, malformed result, session loss and
  unchanged findings/residents in the recording/analysis browser suites.
- [x] Audio request service: authenticated fixed-origin BFF verification, private
  permit/media loading, bounded PCM validation/preprocessing/chunking, pinned
  adapters, candidate/provenance normalization, cancellation and retry semantics.
  Accept 49 core API/pipeline tests and the synthetic evaluation. No worker loop
  or real model is implied. Depends on contracts, sessions and recording permits.
- [x] Complete the optional local ONNX bundle adapter and its isolated synthetic
  graph tests; keep the core dependency lock free of model runtime packages.
- [x] Complete real app/Python cross-process smoke checks for foreign owner,
  expired session, deletion and honest provider-blocked results.
- [x] Complete restore-time auth-session/token invalidation in a new restored
  directory while preserving source snapshots and account rows.
- [x] Run the [aggregate system gate](quality.md) from frozen integrated sources,
  inspect browser evidence and commit the final matrix/checkpoint locally.

## Remaining dependencies and integration gaps

- [x] Complete bounded durable recording/derived-output deletion, generation fences,
  explicit cleanup, truthful owner lifecycle UI and retained-ledger reconciliation
  into new restore copies. Accept failure/restart/late-result tests, 23 lifecycle
  browser checks and 14 recovery HTTP assertions. See [lifecycle wave](lifecycle-wave.md).
- [x] Persist reviewed request outcomes and atomically confirm owner-selected
  candidates into independent human Findings. Accept actual Svelte/FastAPI/CPU ONNX
  mechanics journey including offline restart replay, model-digest invalidation
  and confirmation/deletion races. No bird accuracy claim follows.
- [x] Provide owner source/license bundle intake and actual review-to-renderer pin
  regression, including retry, owner isolation and immutable reviewed versions.
- [ ] Retain the newest deletion ledger outside older checkpoints; supply it on
  recovery. This local tool cannot erase offline copies or reconstruct missing
  post-checkpoint decisions. Pre-identity checkpoints cannot prove lineage.
- [ ] Integrate the separately blocked autonomous worker and account-wide deletion
  orchestration. Existing explicit cleanup is local; distributed upload/storage
  fencing and live worker execution remain outside this completed slice.

- [ ] Obtain and review actual species art and animation references. Acceptance:
  human-approved species fidelity, licensing/provenance, complete sheet/clip
  validation and browser cache/version regression. Current art remains fixtures.
- [ ] Supply a reviewed compatible model bundle and representative licensed audio.
  Acceptance: digest/license/taxonomy checks plus species-level evaluation on
  withheld real recordings. Technical synthetic tests cannot establish accuracy.
- [ ] Configure production identity/mail and any weather/image providers through
  operator-owned secrets and explicit adapters; verify real callbacks, transport,
  regional behavior and failure/revocation without exposing private locations.
- [ ] Repair the supported materialization path for the already-authorized worker
  `c08624d3`; preserve its original implementation and separately verify execution.
- [x] Fetch and locally integrate the original ESP32 branch at its exact reported
  head; retain conflict review, host/native checks and frozen relevant regressions.
- [ ] Restore ESP32 toolchain access and QEMU runtime dependencies, rerun the
  original board/static/simulator checks, and separately validate physical hardware
  and authenticated private recording admission. See the integration checkpoint.
- [ ] Resolve Docker build-network access and verify built images/composition.
  Publication, hosting and deployment remain outside this local task.

The later lifecycle wave is recorded in [its checkpoint](verification-ledger.md#lifecycle-checkpoint-complete-run-and-separate-repair), [55-gate evidence](lifecycle-verification-20261008.json) and [commit ledger](lifecycle-commits-20261008.md). The earlier checkpoint remains intact.

The [local Svelte CLI and CSS audit](svelte-autofixer-20261010.md) corrects the earlier setup assessment and adds three repeatable bounded gates. Full verification status is recorded in that checkpoint.
