# Readiness implementation checkpoint — 2026-10-08

This is a preserved local implementation and verification checkpoint, **not a
complete all-pass claim**. Work continued into a separately owned deep contract
hardening wave after the user changed priorities.

Completed implementation includes opt-in immutable snapshot sharing, anonymous
static rendering, capability expiry/revocation and restore invalidation; effective
persisted auth limits; bounded request admission and bodies; safe typed errors;
confirmation deadlines and same-request gateway recovery; and finite drained
session polling. Existing species manifests/reviewed pins, yard layers, import,
resident, weather, recording and private evidence behavior remain regression targets.

## Exact verification state

- First clean frozen run: **55/57 gates passed**. Invalid yard placement returned
  500 after error hardening; four reviewed validation failures now have explicit
  domain types and safe400 responses. The other failure was routines reload.
- Second clean frozen run: **56/57 gates passed**. Source/test revisions remained
  fixed throughout. The routines journey again timed out waiting for networkidle
  after its first13 behavior assertions. No remaining full pass is claimed from
  isolated or partial reruns.
- The session-poll diagnosis found a real unread response-body leak. Its bounded
  drain/cancellation fix passed10 helper tests and an unchanged isolated17-check
  routines journey. The full-run reload timeout still requires timing/resource
  diagnosis; parallel heavy checks were paused on this four-CPU workspace.
- Second-run counts:635 UI tests in51files,140 Python tests,10 generator tests,
  155 cross-language cases,494 completed browser assertions across17 suites
  (the routines suite stopped early),52 actual local audio-confirmation checks,
  35 local SMTP/signed-provider-mock checks,25 abuse HTTP checks,18 restore HTTP
  checks,39 core audio HTTP checks and16 operations HTTP checks.

Reports preserve commands, exit codes, exact revisions and failed logs:
[attempt1](readiness-attempt-1-20261008.json),
[attempt2](readiness-attempt-2-20261008.json).
Raw evidence lives in `/tmp/chirp-readiness-system-20261008` and its `-r2` sibling.

Second-run source and test heads:

- UI: `305cbeabfbd08767907bb71d7bb0cb69719ef8de`
- Companion: `c46735bac08c77fd4f8689fc032fddc8199b3851`

The original lifecycle history remains intact:54passes in its complete55-gate
run, then the selector-only affected-suite rerun. Neither historical run has been
rewritten into a fictitious single all-pass result.

## Continuing work and boundaries

Deep contract work is isolated until integrated: canonical runtime guards for
persistence/provider/HTTP/config boundaries, deterministic generated counterparts,
semantic versus structural parity and breaking-change checks. A final combined
run will use frozen integrated sources with heavy browser work scheduled exclusively.

The approved code handoff remains technically blocked, documented in
[the exact transfer record](approved-handoff-blocker-20261008.md). No local ZIP
bytes exist, so worker/ESP integration is unverified. Existing art remains fixtures;
no model generation, device work, providers, credentials, publication or deployment
was performed. Peer research stays outside both repositories.
