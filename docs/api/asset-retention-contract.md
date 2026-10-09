> Mirror of `birdsong-yard-sprites/docs/asset-retention-contract.md`; code paths below refer to the UI repository.

# Private asset retention contract

The source authority is `src/lib/assets/lifecycle-contracts.ts`. The lifecycle
service owns admission and transactions; generated JSON Schema defines portable
structure only. `GET /api/asset-lifecycle` returns the authenticated owner's
overview. `POST` accepts bounded same-origin JSON for three reversible operations:

| Command | Required concurrency evidence | Result |
| --- | --- | --- |
| `set-archive` | Target kind/UUID, expected archive revision, request UUID | Archive or restore a private PNG/package without removing bytes, review history or existing pins. |
| `unpin` | Bird ID, exact expected artwork ID, request UUID | Clear that selection and retain the former artwork identity in an immutable receipt. |
| `restore-pin` | Prior unpin request UUID, new request UUID | Restore the receipt's former selection only while its bird is still unpinned and current admission allows it. |

Each target is either `private-file` or `private-package`; the shared catalog is
explicitly read-only and cannot be named as a private lifecycle target. An archive
blocks new selection and derived intake through its dependency graph. Existing
pins retain their original resolution and fallback behavior. Restoring an archive
does not automatically change a bird's pin. An unpin receipt is evidence for a
possible reversal, not permission to overwrite a later selection or to bypass an
archived dependency.

The owner comes from the verified session, never a command field. Archive and pin
changes share the same SQLite transaction with the immutable owner/request receipt.
Exact retries return current overview plus `replayed: true`; conflicting reuse of
a request UUID fails. Stored receipt digests, row identity, exact schema/trigger
compatibility and retained references are checked by the canonical storage code.
An interrupted transaction cannot leave a change without its receipt.

## Eligibility is diagnostic

The overview says `purgeEnabled: false`. Archive is reversible; there is no purge
command and no destructive scheduled job. Only an archived private file with no
retention reasons and a complete reference scan can be cleanup-eligible. Package
history remains retained. The UI distinguishes current selection availability from
retention reasons, including active assets, pinned birds, retained artwork,
package dependencies, immutable file-review evidence and pipeline history.

Unknown, missing, malformed, cyclic or over-budget reference graphs fail closed.
An incomplete scan cannot make an asset eligible. Eligibility does not authorize
unlinking, revoke a license, remove provenance or erase evidence. Account-wide
erasure, production purge execution and retention for backups/downloaded copies
remain separate work. Purge and interrupted-cleanup exercises use disposable
fixtures only.

## Portable interfaces and semantic limits

Seven schema authorities are exported to both repositories:

- `asset-lifecycle-target-v1`
- `asset-archive-state-v1`
- `asset-lifecycle-command-v1`
- `asset-lifecycle-receipt-v1`
- `asset-lifecycle-entry-v1`
- `asset-lifecycle-overview-v1`
- `asset-lifecycle-response-v1`

They add no fields to pre-existing wire formats. Legacy stores with no lifecycle
tables remain active by default; schema initialization is separate from archive
state. Existing strict clients can continue using existing endpoints. New clients
must not infer lifecycle support from an older endpoint or reinterpret archive as
deletion. Yard JSON backups do not carry this separate private lifecycle ledger;
whole-store recovery validates it alongside retained files and pipeline evidence.

Zod refinements additionally enforce initial-state revision/timestamp consistency,
exact unpin receipt identity, archive/selection/eligibility coherence, unique
retention reasons and overview identities, and incomplete-scan refusal. The
portable schema deliberately does not pretend to encode all those relationships.
Named adversarial goldens and the reviewed property-semantic baseline make the
difference executable. Ownership, current revisions, cryptographic digest equality,
dependency authority and atomic writes require server checks beyond both schemas.

The extension adds 49 synthetic cases to the existing corpus (281 total), including
17 explicit structural-acceptance/source-rejection probes. Cross-language checks
compile temporary standalone Ajv validators and compare Python JSON Schema
roundtrips. No Python application consumes these new interfaces, so no unused SDK
or second handwritten wire model is introduced.

`contracts/authority-inventory-v1.json` adds explicit GET, POST and persisted-store
boundaries, naming the canonical schemas, service, storage preflight/recovery,
browser consumer and adversarial evidence. Inventory source coverage does not
substitute for behavior tests or prove that every runtime branch is exercised.

The independent lifecycle reviewer inspected and approved the compatibility
baseline additions before they were applied: all 155 previous structural digests
remain unchanged and seven new schemas per repository bring the total to 169.
The property baseline retains all 160 prior semantic exceptions and adds 26
lifecycle-only cases (186 total). The deterministic differential check covers
9,544 mutations with 651 source-valid inputs preserved. These are contract-level
results; the integration owner's strict suite separately verifies runtime and
browser behavior.
