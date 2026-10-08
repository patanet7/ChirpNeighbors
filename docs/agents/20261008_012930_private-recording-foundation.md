# Local owner-private recording foundation

Implemented independently on `codex/species-manifest-local`; no publication,
provider configuration, credential changes, real capture/inference or worker edits.

Retained heads before this slice:

- UI: `58483315e59c943643e0da95344cb824595bf19a`.
- Companion: `cf537266d3a9448f28f96faab41b2a42af23988e`.

The supplied review bases remain ancestors: UI
`1d2ddcd844002dd2e989b29c71419156ba0d0cf5`, companion
`a2705af75b63acddacd9bdf8c1d721252a1f7456`.

## Completed code and boundary

UI commit **`ac42c8ee8e4c476dbacc3cb629f26290c5622e97`** adds a separate
versioned recording metadata repository and private byte-store interface/local
adapter. Existing development owners can upload, list, inspect, play ranges/HEAD,
delete and explicitly retry cleanup. Production authentication remains fail-closed.

Uploads stream canonical PCM16 WAV, at most 30 seconds/6 MiB, mono/stereo 8–48 kHz,
with size/frame/duration validation, SHA-256, bounded read lifetime and active count.
Generated IDs, no-follow/exclusive file operations, restrictive permissions,
public-root refusal and Vite denial protect private bytes. Original filenames and
filesystem paths are not metadata. Foreign/missing/deleted IDs are indistinguishable.

Staging is unreadable. Delete commits a permanent generation tombstone before I/O;
playback and new processing permits fail immediately, subsequent stream pulls stop,
and a synchronous same-database guard rejects simulated stale-result commits.
Cleanup failures remain retryable. Restart requeues tombstones to recover late
writes interrupted after concurrent deletion. Directory fsync precedes completion.
This is not an integration with the independently owned worker.

Yard JSON backups retain raw recording references but contain no media ledger,
bytes or tombstones; restoring a yard cannot resurrect media. The shared projection
omits private evidence and recording references. Existing raw import, resident,
weather, scene, animation and yard-backup semantics remain intact.

This companion commit mirrors the structural recording metadata schema, adds six
Python contract tests and updates the integration document. It does not implement
a Python media adapter or change ESP32/inference/worker code. Existing schema files
are unchanged. The existing portable-contract CI pattern discovers the new tests.

## Verification

- **283 TypeScript tests / 22 files**, including **45 recording tests**.
- **302 browser checks / 9 suites**: recording **64**, scene **29**, findings **33**,
  routine **17**, arrangement **30**, sleep **10**, manifest **16**,
  core/production **66**, layered **37**. All 238 earlier browser checks rerun.
- **34 Python contract tests**: identification **15**, findings **7**, scene **6**,
  recording **6**. Run from `backend-inference` with
  `PYTHONDONTWRITEBYTECODE=1 /tmp/chirp-contract-venv/bin/python -m unittest discover -s tests -p 'test_*contract.py'`.
- Type check: zero errors/warnings. ESLint, changed-code Prettier, new Python
  Ruff check/format, production build and generated-contract comparison pass.
- Zero browser runtime exceptions and zero external browser requests. Synthetic
  silence only, temporary data directories, no existing local yard/backup replacement.
- HTTP regression caught and fixed reuse of connections containing unread rejected
  upload bodies. An oversized sender continuing after refusal can still see a reset;
  rejection never drains an unbounded body.

Evidence lives in `/tmp/chirp-recordings/verification-summary.json`,
`/tmp/chirp-recordings/recordings-browser-results.json`, and the matching suite
reports under `/tmp/chirp-{scenes,findings,routines,arrangement,sleep,manifests,foundation,layered}`.
The UI's `docs/recordings-checkpoint.md`, `docs/recordings.md` and updated
`docs/engine-task-checklist.md` contain concrete acceptance criteria and limits.

## Residual dependencies

Capture UI, authorized real-format samples, production accounts/private hosting,
rate/total-disk quotas, backup-retention policy and actual derived-output cleanup
remain future work. Cleanup is explicit and batch-limited, not an autonomous service.
Tombstones persist indefinitely; local unlink is not encryption or secure erasure,
and cannot revoke external snapshots or downloaded copies. Restoring an entire old
filesystem snapshot needs the latest deletion ledger. Approved species/scene art
remains unavailable; fixture art was neither replaced nor described as reviewed
visual fidelity. No push, PR, merge, deployment or blocked publication retry.
