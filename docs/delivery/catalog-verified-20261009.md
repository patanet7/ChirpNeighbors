# Verified shared canonical catalog checkpoint — 2026-10-09

All **73/73 aggregate gates passed** on clean, frozen source trees. The single
complete run finished at **03:17:15 UTC**, with 1,308.47 seconds of recorded gate
execution. No duplicate full suite was launched.

- Main tested: `ef67223f52448dcdbf2bef05283146a01bceda06`.
- UI tested: `db931a2beb8e62dc012a981d478e27749062fd4a`.
- [Complete report](LOCAL-EVIDENCE.md),
  [counts](LOCAL-EVIDENCE.md), and all gate logs are retained.
- Original output: `/tmp/chirp-catalog-system-20261009-r1`.
- Both new local branches are `codex/shared-catalog-local`. The prior
  `codex/asset-retention-local` branches remain at main
  `0128f0fb78241540ded36a78abd128f76fd757aa` and UI
  `f70a5cac70ce97f5bc160e58edec3468543cb9ca`. Both histories retain the supplied
  published foundation-review bases; no published branch was overwritten.

## Concrete completed slice

| Task | Dependencies and acceptance now verified |
| --- | --- |
| Safe shared identity and render contract | Existing taxonomy/request identity and V2 frame/clip validators. Ten strict authorities cover generic species payloads, exact pins, release availability, promotion/revocation receipts and owner selection. Explicit `chirp-display-catalog@1` identity, style/version/variant, public provenance and technical review metadata; no filename inference, private source lineage or mixed private/shared pins. |
| Immutable reviewed fixture releases | Canonical contracts and SQLite transactions. Default-deny promotion plus an exact internal fixture allowlist, immutable versions, append-only revocation, durable UUID retries, bounded stores and read-only recovery verification. Process interruption and independent connection tests pass. Version two changes timing only and reuses existing pixels. |
| Incremental demand and private resident selection | Trusted species identity, request/release stores and authenticated owners. Present collected/resident species deduplicate one global request across accounts. Unknown or mismatched scientific identity cannot request/select a pack. Explicit expected-artwork CAS changes one resident, with immutable owner retry receipts; private names, observations and source data stay private. |
| Manifest-driven rendering and fallback | Shared pins, current registry and yard admission. Two accounts resolve identical reviewed manifest geometry. New releases never replace saved pins. Revoked, missing or corrupt content preserves the exact pin with explicit generic fallback in Pixi and SVG, clears stale cache on refresh, and blocks new pin/automatic assignment/backup/undo admission. Legacy and private assets retain compatibility. |
| Owner controls | Typed authenticated overview/command routes and session guards. Collection controls separate generic packs from named residents, expose version/taxonomy/provenance and fixture review limits, and require an explicit version choice. Lost-response exact retry survives tab navigation; keyboard focus, 320px layout and delayed former-owner response fencing pass. No HTTP promotion/admin endpoint exists. |
| Recovery and regression coverage | Complete integration and independent review. Legacy absent overlays remain valid; wrong-type, partial, future or corrupt catalog stores fail closed. Cold restart/backup preserves releases, revocations, owner receipts and exact pins. Existing yard/import/resident/weather/object, recording, private asset and sharing layers pass the full strict suite. |

The application display taxonomy is not an external biological authority or Cornell
integration. Generic artwork does not identify an individual wild bird. Shared
render data uses safe V2 geometry; owner-private V3 source manifests are not
relabeled or copied into the shared catalog.

Only local development fixture selection is enabled. Even the runtime development
release repository denies promotion by default; local tests instantiate a separate
trusted internal fixture authority. Fixture approval/rights flags cannot authorize
production publication or certify biological fidelity. Existing owner records are
not migrated or rewritten: new tables are an additive overlay, and explicit
selection creates owner artwork references. Existing automatic assignment only
uses currently eligible artwork already retained in that owner's yard.

## Verification and independent review

The complete run passes **1,496 UI unit tests**, including **65 added tests**:
29 release, 21 owner-selection, 12 reader/registry and 3 additional request-store
cases. Focused storage runs pass 58 request/release tests in total. The suite also
passes zero Svelte/type errors or warnings, typed lint, formatting and a fresh
production build.

Canonical checks pass **349 goldens**, **11,368 deterministic mutations**,
**714 source-valid inputs**, **227 reviewed semantic exceptions**, **189 structural
digests**, **678 Python-authoritative boundary cases**, and **52 HTTP/SSR operations
across 92 inventoried boundaries**. All 281 previous goldens and prior semantic
exceptions remain. The 22 explicit residual contract gaps are documented; bounded
property probes are not exhaustive proof.

The new browser gate passes **44/44 assertions** both in the dedicated completed
attempt and in the full aggregate. It verifies real two-account reuse, private
PNG/source isolation, exact version changes, concurrent CAS, stale/idempotent
commands, origin/session checks, keyboard response-loss retry, owner switching,
Pixi/SVG revocation/missing/corrupt fallbacks and cold recovery. There were no
browser runtime errors or external browser requests. All prior browser gates pass,
including the 38-check private retention gate and 35-check PNG gate. Existing
technical model fixtures remain technical; no real provider was configured.

Actual parallel workers owned contracts, storage, UI, the browser gate and
independent read-only review. Root owned service/runtime/renderer/recovery
integration and serialized heavy verification. Review approved the exact baseline
additions and closed three findings: validating artwork before exact-pin reuse,
rejecting wrong-type recovery objects, and refusing a revoked shared pin mislabeled
as legacy rendering. No material source findings remain. See UI
`docs/shared-catalog-review-20261009.md` and `docs/shared-catalog-checklist.md`.

## Retained attempts and visual evidence

[Focused attempts](LOCAL-EVIDENCE.md) retain incomplete runs and corrected
failures. Browser r1 stopped after 14 assertions on a Python async-generator
assertion. Browser r2 stopped after 20 assertions because keyboard retry ran before
the remounted control was enabled. Awaiting the response before the assertion and
waiting for confirmed response loss/readiness/focus corrected the harness without
weakening its exact-command or replay checks. Browser r3 passed all 44, then the
single complete aggregate passed all 73 gates. Earlier source type fixes and
fixture/test lint failures are documented with their final passing evidence.
Incomplete attempts are not counted as passes.

The [320px catalog view](LOCAL-EVIDENCE.md),
[Pixi yard](LOCAL-EVIDENCE.md), and
[SVG fallback](LOCAL-EVIDENCE.md) preserve
existing fixture pixels. The catalog/mobile and yard previews were visually
inspected. No replacement artwork or species-correctness claim is made.

## Remaining dependencies

1. Approved reference/concept pixels, per-file rights and frame-level biological
   review remain unavailable. Real photo, segmentation and sprite-generation
   adapters are future work; current fixtures prove mechanics only.
2. Production publication/administration authority, rights policy, taxonomy
   adapters and distribution infrastructure remain unconfigured and fail closed.
   Optional variants have explicit identities but no enabled production workflow.
3. Real import/audio/weather providers, generation execution budgets, production
   identity/infrastructure and operational policy retain their existing gaps.
4. Personality/companionship, funding choices, account-wide erasure and retention
   policy remain separate decisions. Archive retains bytes; no purge is authorized.
5. Pending UI intent survives tab navigation, not full document reload; committed
   server retry receipts remain durable. ESP32 work remains separate and was not
   duplicated or assumed integrated.

The [product register](product-behavior-and-ideas.md) contains 22 stable entries:
**16 verified, 4 agreed, 1 implemented, 1 proposed**. PB-003 verifies these bounded
fixture mechanics; PB-021 retains the longer-term real-art goal. The
[delivery matrix](matrix.json) preserves the prior 72-gate checkpoint separately.
Final evidence/documentation commits after the tested revisions change no runtime
code. No push, PR, merge, deploy, credential change, paid service, external provider,
Library retry or blocked publication/transfer retry occurred.
