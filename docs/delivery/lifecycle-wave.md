# Recording lifecycle and real-journey implementation wave

Start from clean UI `83837529722ce48e210ed224e74cfbaf2f72881b` and companion
`084b33dfac1160e1cc9b2db9336b0a16b9c4a831`. The previous 50-gate checkpoint stays
intact. Work is local on isolated same-workspace branches; no worker/device
transfer, credentials, paid providers, publication or existing owner-data use.

| Owner | Concrete work | Acceptance / dependency |
| --- | --- | --- |
| contracts_platform | Zod-owned lifecycle/ledger/cleanup contracts, migration, immutable deletion intent, lease-fenced outbox, atomic bounded derived JSON admission, explicit executor | Existing metadata/delete API compatibility; deletion rejects late output; leases/retries/reopen/owner isolation; publish schema first for media and ops |
| media_frontend | Private retained/deleting/deleted status and cleanup retry UI | Actual app/SQLite/storage failures and restart; no completion while cleanup remains pending; no claim about offline copies; depends on lifecycle schema |
| reliability_ops | Readonly cumulative deletion-ledger export and isolated restore reconciliation | Matching lineage/high-watermark, old checkpoint cannot restore ledger-known deleted audio/output; originals unchanged; wrong/stale/unsupported ledgers refused; depends on lifecycle repository/schema |
| root | Durable audio result admission/retry and explicit candidate-to-Finding confirmation | Fetch stored owner result, generation fence and atomic transaction; no client-supplied result trust; stable retry receipt; unknown time preserved; raw candidates never auto-confirm |
| audio_pipeline | Actual Svelte/FastAPI/local-ONNX/confirmation audit and bounded fixes | Generated arithmetic model and synthetic WAV traverse real local services, including deletion/restart/retry; clearly no bird-accuracy claim |
| auth_sessions | Actual email delivery/link/session and signed Google mock journeys | Real loopback SMTP + actual application callback/session paths; replay/logout/expiry/restart and state/PKCE/signature failures; precise external-config checklist |
| image_pipeline | Owner source/license intake and actual review-to-resident-pin audit | Existing technical pixels only; invalid/unreviewed licensing rejected, immutable review/pin versions, owner isolation and restart |

- [x] Commit lifecycle schemas and additive migrations; preserve prior owner rows.
- [x] Exercise durable cleanup without adding an autonomous worker loop.
- [x] Admit/revoke/purge derived outputs and show truthful owner statuses.
- [x] Export retained deletion decisions and reconcile only new restore copies.
- [x] Complete explicit human confirmation of a stored analysis candidate.
- [x] Run actual auth, image and audio journeys; fix concrete boundary gaps.
- [x] Expand and pass the complete verification inventory, inspect evidence, commit locally.

Deletion of a recording removes managed source bytes and raw derived outputs. A
Finding explicitly confirmed by the owner is a separate human observation; its
retention must be disclosed rather than silently deleting residents/history.
Offline backup copies cannot be remotely erased. Reconciliation can enforce only
the retained ledger supplied by the operator; it must not invent missing history
or assert that an old export is the latest one.

Final evidence: [lifecycle checkpoint](lifecycle-checkpoint-20261008.md), [verification](lifecycle-verification-20261008.json), and [exact local commits](lifecycle-commits-20261008.md). All 55 gates have passing evidence across the full run and the targeted selector-fix rerun.
