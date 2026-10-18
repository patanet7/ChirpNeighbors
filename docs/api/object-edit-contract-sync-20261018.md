# Object edit contract synchronization — 2026-10-18

The runtime-owned `object-inventory-command-v1` adds `undo-return`, also embedded
in `dev-workbench-request-v1`. An undo carries its own immutable request UUID and
current expected placement, plus the original object's ID, return request UUID
and exact `returnedFrom` placement. Structural validation does not prove history:
the receiving owner repository reconstructs the original return command and
requires its digest, result object and latest object receipt to match. It also
checks current layout, scene, stock and placement before restoring the original
identity and position. Exact retries use the existing immutable receipt path.

The two new V1 envelopes are intentionally separate from resolved animation
assets: `yard-layout-read-v1` contains `{ snapshot }`, and
`yard-layout-command-response-v1` adds a bounded nonempty `message`. They serve
the explicit `/api/yard?view=layout` response view. The snapshot remains private
owner data, including durable receipts; these are not public projections. The
normal client retains its existing asset packages. Authentication, document
session binding, receipt proof and cross-record semantics remain server rules.

The existing private additive V1 compatibility policy requires synchronized
reader upgrades. A stale strict reader rejects the new operation rather than
silently discarding it; old operations and backups retain their existing wire
shapes. No backup version, Python-owned audio authority, asset bytes or Python
generated declaration changes are required. Both new response wrappers inherit
the existing unique-object-ID semantic refinement. The property corpus records
exactly those two new duplicate-ID exceptions while preserving all 424 prior
exceptions in order; portable structural validation is not semantic admission.

The official UI exporter mirrors the four affected schemas and boundary goldens.
`check_contract_corpus.py` explicitly registers the two new schema names. The
existing fresh cross-reader probe adds fourteen cases using in-memory synthetic
owners: actual return/undo and receipt retention, original identity/position,
exact retry, stale/forged/cross-owner rejection without state mutation, strict
acknowledgments and malformed requests. Its fixed CI corpus retains the previous
44 cases unchanged and appends the fourteen additions. No browser, desktop,
service, owner dataset or native task state is involved.

Run from this repository using Node 24, the UI's locked dependencies and the
existing pinned Python contract environment:

```sh
node scripts/check_runtime_contract_sync.mjs /path/to/UI /path/to/python
python scripts/check_runtime_sync_corpus.py contracts/fixtures/runtime-contract-sync-v1.json
python scripts/generate_python_contracts.py --check
```

From the UI, run `scripts/export-contract.ts --check --main-repo PATH`, the
compatibility/inventory checks and existing cross-language property gate. The
bookkeeping update changes eight compatibility digests and only the existing
`/api/yard` GET/POST inventory rows; endpoint and inventory counts stay unchanged.
