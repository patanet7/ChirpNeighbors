# Contract and animation work checklist — 2026-10-08

This local wave continues from the reviewed branches and preserves both failed
readiness attempts. Attempt 2 finished 56/57 gates at UI `305cbea` / companion
`c46735b`; its routines browser reload timed out. The unchanged routines journey
passed 17/17 in an isolated check. Neither result is an all-pass combined run.

| Task | Dependencies | Concrete acceptance | Current state |
| --- | --- | --- | --- |
| Enumerate actual boundaries | Svelte routes/hooks, Python route declarations, stores, jobs, configuration | New/removed runtime routes fail an AST-backed inventory gate; one source authority per boundary; closed private/public SSR aggregates | Implemented locally |
| Validate runtime admission/egress | Inventory; generated Python identity guard | Reject corrupt SQLite rows, unsafe IDs/counts/times, malformed auth settings, mismatched recording metadata/receipts and impossible audio windows; preserve private owner state on failures | Implemented locally |
| Bound transport and recovery | Existing response/error schemas and lifecycle ledgers | Finite fetch/body reads, byte ceilings, strict UTF-8, cancellation and safe status parity; expired/revoked/restored shares remain unavailable | Session/media paths implemented; generic command transport followup in progress |
| Generate and test counterpart contracts | Canonical Zod/Pydantic models | Regeneration must be clean; preserve literal schema-looking data; reject remote/unsupported references; exact goldens and deterministic mutations; reviewed structural digest changes fail automatically | Implemented; v3 exports pending final producer integration |
| Version pose manifests | Existing v2 manifests, catalog, technical fixture pixels | Keep v2 behavior; v3 unequal durations, pivots/contacts, exact pose graph and pinned references, bounded binary-alpha/grid/palette/loop metrics; malformed geometry rejects before allocation | Schema and renderer integrated; producer integration in progress |
| Preserve private source lifecycle | Existing owner SQLite artifact/review model | Distinct immutable RGBA artifact; source/reference digest and approval rechecked at render; absent source fails to fixture fallback; approval never changes a resident pin | In progress |
| Run combined frozen verification | All source and generated changes committed; other heavy jobs stopped | Full retained browser/HTTP/unit/type/lint/build/generator suite completes on unchanged clean revisions; preserve failure reports and exact source IDs | Pending |

Art remains technical fixture content. Provider-independent contracts describe
unsupported future capabilities explicitly; no image model, replacement art,
real bird weights, paid service or external provider is configured by this work.
Contact metadata is review evidence and renderer diagnostics, not inverse
kinematics. Public snapshots use the safe built-in catalog only.

Focused evidence is retained in each boundary audit and in temporary check
outputs. Final aggregate counts and exact commit IDs will be recorded after the
complete run. Account-wide deletion, real photo decoding, licensed evaluation
inputs, real import/weather adapters and deployment remain distinct gaps.

The approved worker/device Library handoff failed its supported local download
twice. No archive bytes were obtained, so its digest/contents/commit ancestry
cannot be verified and neither implementation is integrated or recreated. See
[the exact handoff blocker](approved-handoff-blocker-20261008.md).
