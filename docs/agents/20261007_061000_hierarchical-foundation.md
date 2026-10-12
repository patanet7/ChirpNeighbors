# Agent Log: Hierarchical application foundation

**Timestamp**: 2026-10-07
**Agent Type**: implementation coordinator with authorized parallel implementation
> Historical checkpoint; verification and publication status below describe this stage only.

**Goal**: Deliver a runnable engine/storage/animation foundation in the two cloud checkouts.

## Task Summary

Completed the bounded local foundation. No pushes, PRs or deployments.

## Project Analysis

The prior React checkpoint persisted browser data but had no server ownership, autonomous simulation or durable jobs. The main repository's hardware/inference paths were not verified as live. The new UI separates typed domain/storage, simulation, renderer, server identity and pipelines. This main-repository change supplies the shared integration boundary without modifying existing inference endpoints, firmware or infrastructure.

## Actions Completed

- Implemented SvelteKit/Svelte 5 with Node 24 built-in SQLite; preserved React source/config under `legacy-react`.
- Completed import → grouped Finding → temporary visitor → name/promote → permanent resident, preserving IDs, evidence, collection and artwork versions across reload/restart. Explicit additional instances and v1 restore are supported.
- Added deterministic idle/move/perch/sing/feed/bathe behavior, scene navigation/slot arbitration, Pixi rendering, reduced motion, keyboard selection and graphics fallback. Art/scenery remain authored fixtures.
- Added owner-scoped durable jobs, hierarchical stages, idempotency, leases, bounded retries, cancellation, immutable artifacts/provenance and review. Fixture work advances one stage per request; real generation stops at an unconfigured provider.
- Exported the same version-2 event JSON Schema from the UI Zod source to both repositories. Added Python validation/model-candidate adapter with explicit schema path, private JSON copying, source provenance and unknown time/confidence preservation.
- Added lightweight Python contract CI and updated UI CI. Replaced the stale v1 prose contract with the current implementation contract.
- Inspected desktop/mobile Chromium, fixed muted text contrast, exposed mobile identity switching, corrected streamed request rejection and open-page visitor expiry.

## Files Modified

Main repository: `contracts/`, `backend-inference/app/models/identification.py`, `backend-inference/tests/test_identification_contract.py`, `backend-inference/requirements-contract.txt`, `.github/workflows/contracts.yml`, `README.md`, `docs/api/species-yard-contract.md`, and this log. UI changes and exact boundaries are recorded in that repository's `docs/foundation-checkpoint.md`.

## Verification

- Fresh isolated `npm ci`: passed, including prepare.
- UI check/lint: passed with zero Svelte diagnostics.
- UI unit tests: 37 passed (13 storage, 14 pipeline, 8 simulation, 2 identity).
- UI build: passed. Node adapter externalizes the built-in `node:sqlite` module; Node 24 production startup was exercised.
- Generated schema check: both repositories match, including UTC-only timestamps, reserved IDs and recursive JSON.
- Python adapter: 15 `unittest` cases passed using pinned lightweight dependencies, no model installation.
- Browser: 66 checks passed with actual process restart, owner isolation, backup/v1 migration, live expiry, motion, fixture pipeline/review, provider refusal/cancel, safe sharing projection, request limits and production auth refusal even with the development flag set.
- Additional renderer: 12 browser checks passed, including WebGL pixel motion/freeze, lifecycle cleanup and context-loss fallback.
- axe 4.11.0: no reported selected WCAG A/AA violations in five desktop and mobile views; not a complete accessibility certification.
- No browser runtime errors, external requests, or horizontal overflow at 1440/390/320 px. Git whitespace checks pass. Remote CI was not triggered.

Browser, renderer, accessibility and clean-install reports plus representative screenshots were retained outside the repository.

## Remaining Boundaries / Next Steps

Real email/Google authentication, initial US deployment, private audio ingestion/storage/deletion, real identification adapters, reviewed generated animation, generated regional scenes, external execution and public sharing are not connected. Alice/Bob are explicit development profiles; production fails closed. SQLite is a local bounded single-host foundation, not hosted multi-user production infrastructure. Pipeline advances are manual, not an always-on worker; no provider charge or external call was made.

The next useful integration is one real identification source against the generated schema, including taxonomy mapping and correction handling. Email mechanism and worker/provider execution choices remain necessary before those production integrations. No device was flashed and no provisioning script was executed.

**Agent Status**: Completed
