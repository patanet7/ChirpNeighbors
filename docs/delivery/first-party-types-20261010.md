# STATIC-03 — remaining first-party typing closure

This local continuation starts from main `e27bcf0393e5c295e672648832025b76480f9671` and UI `a87168f5cba7105c76c59b2c06f67d166d9c5e37`. Both are preserved on `codex/static-03-88-checkpoint`; implementation uses `codex/first-party-types-local`. The previous [88-gate report](LOCAL-EVIDENCE.md) remains immutable with SHA-256 `a95fa1e5b7d47121096cce36f9ee516b62b4fead3c6a845bd3caec71af9cb0be`.

The [539-file inventory](LOCAL-EVIDENCE.md) identifies 45 older handwritten JavaScript files and seven nonempty backend tests without strict typing. This slice closes those specific gaps while retaining runtime behavior, public CLI paths, generated-schema authorities and interpreter isolation.

## Task checklist and acceptance

| Task | Dependency | Acceptance | State |
| --- | --- | --- | --- |
| TYPE-01: preserve checkpoint and classify files | Verified 539-file baseline | Exact path/role/strategy inventory; no removed baseline source or rewritten historical evidence | Implemented; final review pending |
| TYPE-02: strict-check Node tooling and configuration | TYPE-01 | Strict JSDoc/checkJs with indexed-access and optional-property checks; original `.mjs` and config entry paths execute under Node 24 | Implemented; final review pending |
| TYPE-03: type contract authorities, fixtures and generators | TYPE-01 | Types derive from actual schemas/producer exports; generation remains byte-identical; invalid golden cases remain intentional unknown inputs | Implemented; final review pending |
| TYPE-04: type auth and operator fixtures | TYPE-01 | Precise mock/transport interfaces, unchanged local fixture-provider and operator behavior, no owner-data mutation | Implemented; final review pending |
| TYPE-05: strict backend test coverage | TYPE-01 | All seven tests and new support tools checked in the appropriate core/intake environment; actual fixture/mocking contracts and runtime assertions retained | Implemented; final review pending |
| TYPE-06: discovery and negative controls | TYPE-02–05 | New files discovered; missing/symlinked paths and weakened settings rejected; representative type defects fail alongside clean positive controls | Implemented; final review pending |
| TYPE-07: independent inventory and boundary review | TYPE-02–06 | Every active first-party source mapped to applicable checks or an explicit reason a check does not apply; no blanket Any, broad suppressions, handwritten generated output or duplicate schemas | Pending |
| TYPE-08: frozen full regression | TYPE-07 | Complete runtime, browser, build, lint, formatting, contract drift and static gates pass on committed clean revisions; failures retained | Pending |
| TYPE-09: local delivery | TYPE-08 | Findings, counts, inventory, evidence and exact tested/final commits recorded; no publication or deployment | Pending |

## Compatibility decisions

The remaining JavaScript files are Node ESM command adapters, contract/golden-case tooling, test fixtures, style checks and build/lint configuration. Strict JSDoc checking preserves their public extensions, import paths and direct Node execution, avoiding a compilation step for operators. Shared types must refer to the actual schema or producer signature. An invalid runtime-contract fixture is intentionally `unknown` at the validation boundary; it is not a reason to erase types throughout the tools.

The backend tests use strict Python annotations with concrete fixture and mock interfaces. Optional intake and ONNX dependencies stay in their existing environments; the core service must still import without model packages. Empty historical placeholders, unsupported legacy tools, dependency declaration internals and generated validator runtimes retain individually documented boundaries rather than being presented as newly typed code.

Disjoint implementation ownership covers style/config/discovery, contract core/adapters, contract authorities/golden cases, auth/operator tools and backend tests. An independent reviewer owns the complete source reconciliation and adversarial controls. Root owns package commands, aggregate integration, final evidence and the single full browser/build run.

## Verification status

Implementation and focused checks are complete except the final JavaScript probe/review pass. Backend tests are committed at `d3ef730d0835d5e507e9d8e9257852445b8ab225`. The aggregate retains all 88 original gates and adds five: strict JavaScript, JavaScript negative probes, backend test typing/probes, source applicability, and applicability failure controls. The planned full run therefore has 93 gates. The previous 88-gate pass is a preserved checkpoint, not a claim that this new slice has passed its full regression. No publication, deployment, credential change, external model request or blocked toolchain retry is part of this work.
