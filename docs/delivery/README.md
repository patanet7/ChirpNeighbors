# Executable full-system delivery matrix

`matrix.json` is the owned, versioned delivery graph. Its status is implementation
status in these local checkouts, not a production readiness percentage. Each
workstream has an owner, dependencies, acceptance criteria and evidence list.
`implemented_local` means the bounded local slice has passed its declared checks.
`partial_local` retains an explicit unmet acceptance criterion in `remaining`;
storage retention and container execution are not silently called complete.
The [integrated checkpoint](checkpoint-20261008.md) records exact verification.

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

Worker `c08624d3` and ESP32 `c693ed0` remain outside this workspace pending approved
transfer. This task will not reproduce their independent work to evade that gate.
Approved species artwork, real-source samples, production identity/mail credentials,
model licenses and external provider/hosting configuration remain explicit external
gates. Local coding, synthetic fixtures and ordinary package dependencies proceed.

## Concrete task checklist

The implementation below exists locally; final integrated verification is recorded
in the checkpoint report. Dependencies are also encoded in `matrix.json`.

- [x] Contract platform: authoritative Zod or Pydantic models, generated counterpart
  types/runtime guards, deterministic drift checks and strict optional/indexed
  access. Accept when both corpora agree on all 107 valid/invalid cases and generated
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
  22 auth unit cases and 19 synthetic provider/browser checks; missing production
  configuration must fail closed. Depends on contract and storage boundaries.
- [x] Frontend: checked server responses, lost-response reconciliation, private
  upload/play/delete, typed analysis configuration and transient candidate UI.
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

- [ ] Complete durable worker/derived-output lifecycle and deletion/retention
  reconciliation across historical media backups. The current request API keeps
  results transient and idempotency process-local. Restoring an old full snapshot
  cannot reconstruct later deletion decisions; the restored-auth invalidation
  fix does not establish a full media-retention guarantee.

- [ ] Obtain and review actual species art and animation references. Acceptance:
  human-approved species fidelity, licensing/provenance, complete sheet/clip
  validation and browser cache/version regression. Current art remains fixtures.
- [ ] Supply a reviewed compatible model bundle and representative licensed audio.
  Acceptance: digest/license/taxonomy checks plus species-level evaluation on
  withheld real recordings. Technical synthetic tests cannot establish accuracy.
- [ ] Configure production identity/mail and any weather/image providers through
  operator-owned secrets and explicit adapters; verify real callbacks, transport,
  regional behavior and failure/revocation without exposing private locations.
- [ ] Authorize transfer of worker `c08624d3` and ESP32 `c693ed0`, then integrate
  and rerun their real execution/hardware acceptance tests. Do not recreate these
  blocked artifacts in this task.
- [ ] Resolve Docker build-network access and verify built images/composition.
  Publication, hosting and deployment remain outside this local task.
