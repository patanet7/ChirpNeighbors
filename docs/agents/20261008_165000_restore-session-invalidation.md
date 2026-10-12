# Restore auth invalidation and final operations review evidence

The integration owner authorized a concrete fix for restoring old authentication state.
The backup/source databases remain immutable inputs; only a new isolated restore directory
can be changed. No live owner directory, account, credential or provider was used.

UI commits after the earlier operations checkpoints:

- `f71cbea6036dbcc0a506fa74ad013aa7cd5da438`: shared private directory/database guard;
  ten tests preserve rows/bytes/parent permissions while enforcing 0700/0600 and refusing
  symlinks, nonregular files and orphan WAL. Eight operations and six compatibility tests
  also pass; rebuilt app passes sixteen health assertions.
- `494dd9940a3caaf589dbd59001c82d86eb2e40d3`: optional internal-only audio compose profile.
- `56c64ce07dc9c7ccb42cf3d8d7f328d4d94515e8`: fixed BFF origin exactly matches the app's
  `http://localhost:8080` origin; optional model/proxy variables remain commented placeholders.
  Six composition isolation/origin assertions pass.
- `12b0f7db87ccbc0c252688173b5d3de293883207`: isolated restore validates auth schema marker
  1 and exact reviewed entity columns, refuses unknown triggers, then atomically clears
  `session` and `verification`. Accounts, users, encrypted provider tokens and rate limits
  remain intact. Unknown schema also rejects a dry run before any destination is created.
- `64ecf135cba9e0617d10a1c468db276e6bf18151`: real Better Auth library regression, authored
  as a disjoint test in the same-workspace `system-smoke` checkout with auth owner's consent.
  A mocked email creates an actual cookie/session and one-use link. Neither works in the
  restored copy; original session still works; account/user rows and checkpoint/source bytes
  stay unchanged. This test and its strict TypeScript/lint checks pass.

Recovery CLI now passes **19 Python tests**, strict mypy and Ruff lint/format. The added
real-library regression passes separately. Run it from the integrated UI repo with
`npx vitest run src/lib/server/operations/restore-auth.test.ts`. The review used
`CHIRP_BACKUP_TOOL_PATH` pointing at the operations worktree's updated CLI; after both
commits are integrated it defaults to `scripts/private_backup.py`.

The earlier note that restore lacked automatic session invalidation is superseded by this
fix. Manual filesystem copies bypass this protection. It does not revoke Google tokens,
reconcile media deleted after the checkpoint, encrypt backups or provide secure erase.
Fresh login and the documented retention/deletion recovery procedure remain necessary.

Audio review issue status: owner commit `4936bb8dd96162498fc1e212daa0eb91c6086100` fixes
retryable-result caching and network I/O under the global service lock. Owner commit
`534e5dbc38cf44ad63a4ab38c4c1b7519d30e13b` checks provider/model gates before private byte
download and adds the separate optional ONNX adapter. Those are owner-verified results,
not independently rerun by this reviewer. Durable result commits remain generation-fenced
storage integration work; there is no autonomous worker loop here.

Companion container checkpoint is `03df8f9a74a031a30b028bbca9f09555566014a8`. Core audio
image intentionally packages the Python 3.11 request API without optional ONNX dependencies
or model weights. Model-enabled packaging requires a reviewed Python 3.12+ image/profile.
Image builds remain unverified after the prior Docker DNS failure; no repeated blocked
builds, service launch, deployment or publication occurred during this review.
