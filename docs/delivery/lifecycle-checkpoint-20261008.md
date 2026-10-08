# Durable lifecycle implementation checkpoint — 2026-10-08

This local wave follows the previous 50-gate checkpoint. It uses isolated synthetic
data and technical pixels, preserves the published review-branch ancestry, and
contains no publication, deployment, credential changes or external media transfer.

## Completed scope

1. **Delete source and raw derived output durably.** Recording migration 3 adds
   database lineage, immutable deletion intents, a lease-fenced cleanup outbox and
   bounded owner-private JSON outputs. Access revocation and generation increments
   commit together. Late output, stale acknowledgement and expired live-upload
   races cannot recreate readable media or report premature completion.
2. **Recover into a new copy with retained deletion decisions.** Cold export reads
   copied SQLite/WAL data, and restore validates the authoritative cumulative
   ledger, lineage and history. Restored source/output cleanup must complete before
   installing the new directory. Existing originals and unrelated yard history
   remain intact; restored account sessions and one-time links are invalidated.
3. **Persist audio outcomes and explicitly confirm Findings.** Canonical command
   digests make completed requests immutable. An exact configured model SHA-256
   supports restart replay while inference is offline. The owner selects a stored
   candidate, attests to the identification and chooses a time or preserves unknown
   time. Its independent human Finding and retry receipt commit atomically.
4. **Show truthful private lifecycle states.** Retained, deleting and deleted
   history includes durable progress and explicit retry. Raw results reload from
   private storage and analysis admission refreshes derived counts. Raw results
   never automatically become Findings or residents.
5. **Complete owner asset intake and real boundary audits.** Workshop accepts
   bounded source/license bundles, previews declarations and handles interrupted
   queue responses idempotently. Actual local app journeys cover review/version
   replay, exact Pixi/SVG pins, wrong species, restore, owner isolation and missing
   artifacts. Email uses actual TLS SMTP locally; Google uses signed local provider
   responses through the real callback and session implementation.

## Verification

All **55 gates have passing evidence**: the complete run passed 54, then a
selector-only browser-test correction passed its targeted rerun. The old upload
status selector also matched the newly added saved-analysis loading status; its
scoped replacement retains the same assertion. No application code changed after
the full run. The original failure and rerun are retained in the
[machine-readable evidence](lifecycle-verification-20261008.json).

- 554 UI unit tests in 42 files; 136 Python tests; 10 generator tests.
- 129 cross-language cases and deterministic schema/client drift checks.
- 460 renderer/browser assertions across 16 suites; 44 additional actual
  Svelte/FastAPI/CPU ONNX/browser/confirmation assertions.
- 33 actual local SMTP/signed-Google-mock assertions, 14 restore HTTP assertions,
  39 core audio HTTP checks, 16 health/operations assertions and 6 compose checks.
- TypeScript: zero errors/warnings. Strict core/optional/recovery Python typing,
  typed ESLint, Ruff, formatting, locked dependency consistency and build pass.

Raw full-run logs/screenshots are retained at
`/tmp/chirp-lifecycle-system-20261008`; the 26-assertion affected-suite rerun is at
`/tmp/chirp-lifecycle-status-rerun-20261008`. Browser screenshots were inspected.
The two retained report files identify exact commands, exit codes and revisions.

Tested code revisions:

- UI `70a04886cc03c05556cf8380b412b9b618d20829`
- Companion `633bcbeb34aa6ad77aad74cf653d58e186d81b23`

Documentation-only evidence commits follow these code heads. The exact wave
history is in [lifecycle-commits-20261008.md](lifecycle-commits-20261008.md).
The complete command and dependency isolation requirements are in [quality.md](quality.md).

## Remaining acceptance gates

- Retain the latest complete deletion ledger independently of old checkpoints.
  A coherently stale export cannot prove its freshness, and pre-identity backups
  cannot prove lineage. Offline copies, filesystem snapshots and forensic erasure
  are outside the implemented guarantee. Account-wide deletion orchestration is
  separate work.
- The tested executor is explicit and local. The independently blocked worker
  `c08624d3` and ESP32 `c693ed0` remain unintegrated; neither was recreated. A future
  independent worker requires storage-level fencing for concurrent uploads.
- The generated ONNX arithmetic graph proves preprocessing, HTTP, persistence and
  confirmation mechanics only. It is not a bird classifier. Reviewed model
  weights, licensed representative recordings and biological calibration remain
  absent. Approved species art is also unavailable; fixture pixels remain labeled.
- Production email needs operator SMTP host/port/TLS/from and optional credentials;
  account auth needs a stable secret and HTTPS base URL. Google additionally needs
  operator client ID/secret, console callback and consent configuration. Real
  external mail delivery, Google account consent and production hosting were not
  exercised. No credential setup occurred.
- Photo decoding/storage, real sprite-generation and external weather/data
  providers remain explicit adapters. No Cornell integration is claimed.
- Docker image execution remains unverified after the previously recorded registry
  DNS failure. This wave did not retry publication or Docker builds. Host checks
  pass independently of that outstanding environment gate.
