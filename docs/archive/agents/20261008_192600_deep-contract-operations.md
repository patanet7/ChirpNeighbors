# Deep contract operations audit — 2026-10-08

Scope: local `codex/contracts-deep-ops` worktrees, UI base `351dd68`, companion base `47ae8ee`. No publication, providers, devices, credential changes, worker recreation, or real owner data. Executable changes live in the sibling birdsong-yard-sprites repository; this companion record preserves the handoff.

Completed checklist:

- [x] Versioned closed shared command errors and strict client/status handling; unknown SQL/validator/proxy text stays redacted while reviewed placement/legacy 400 responses remain usable.
- [x] Exact JSON media type and fatal UTF-8 ingress; bounded safe reader configuration; no changes to route-owned body ceilings.
- [x] Sharing numeric expiry, bounded coherent SQLite rows, revocation postcondition, operation-specific 201/200 confirmation, 16 KiB client response reads, and invalid-command versus corrupt-storage classification.
- [x] Public SSR and JSON egress schema checks with opaque 404 and preserved auth independence/no-referrer/no-store behavior.
- [x] Read-only sharing PRAGMA columns/index checks and reviewed SQL constraints; harmless whitespace/double-quoted identifier spelling accepted, unknown triggers/constraints refused.
- [x] Complete migration-ledger-row validation and copied, validated process-budget overrides; no migration/version-ceiling changes.
- [x] Private backup v1 strict duplicate-free bounded JSON, UTC timestamp/path/size validation, pre-hash declared bounds and pre-copy file/aggregate bounds; only new restored copies are changed.

UI commits, in order:

1. `191be50e9a4a56962a34c253a139605bada88734` — sharing expiry/capability invariants.
2. `1249e4672c137ef930c6471c6da23add72031b2f` — shared HTTP and error contracts.
3. `c7659aa6ca5875f50575283218a3e969883e641f` — sharing operation/status correction, admission configuration, startup ledger rows, actual HTTP regressions.
4. `30d707ceb320a62d270179a40c02b50746f37724` — strict bounded backup manifests.
5. `ccacac04bf75f85c8fd1d96a57eaa7b8a7f89dee` — public page/API egress contracts.
6. `b2df9cfcafea2c117a1f6bbfa248f9996735a1c6` — sharing schema compatibility refinements and detailed boundary inventory.

Verification: 187 distinct focused TypeScript cases passed across selected runs (68 added), 32 Python backup tests (6 added), 32 actual HTTP checks (7 added), and 38 sharing browser checks including production/auth-unconfigured/JavaScript-disabled reads and token-free referrers/logs. Final typecheck reported zero errors/warnings; changed-file ESLint, Ruff, formatting and production build passed. Browser evidence: `/tmp/chirp-contract-ops-sharing/share-browser-results.json`; build log: `/tmp/chirp-contract-ops-build.log`. Exclusive browser window released; no test services left running by the harness.

The UI `docs/contracts-operations-audit.md` maps each route/artifact to its canonical owner and acceptance checks. Central contract metadata/generated exports/breaking gates remain with contracts_platform/root. Domain schemas remain with auth/media/image/audio owners. Generic command parsing retains native JavaScript duplicate-key semantics; generic yard/workshop success transport bytes still need an owner-approved aggregate ceiling. Recovery artifacts already reject duplicates. Process admission remains single-process; hashes do not prove ledger freshness or erase offline copies.

Environment corrections: generated Svelte config required `npm run prepare`; existing default Python supplied Playwright. Two browser attempts found an overly narrow SQL-spelling comparison and an obsolete expiry fixture; both were fixed before the final 38-check pass. No dependency installation or infrastructure changes were needed.
