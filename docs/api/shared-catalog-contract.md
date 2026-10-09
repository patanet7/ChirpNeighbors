# Shared species catalog contract — local fixture architecture

This slice adds a generic species pack boundary beside private image manifests.
Existing catalog request, pending request and release descriptor authorities remain
unchanged. A catalog request pins the application taxonomy authority/version,
species ID, style/version, asset version and canonical or explicit variant identity.
The current authority is `chirp-display-catalog` version 1, not an external taxonomy
service or a claim that fixture pixels are biologically accurate.

`catalog-pin-v1` contains only `catalogKey`, `releaseVersion` and `renderSha256`.
It cannot contain a private job or artifact ID. `public-catalog-render-v1` contains
that request identity, generic species scope, bounded inline pixel rectangles and
V2 clips, explicit fixture/fidelity flags and public provenance. It excludes named
individual birds, owners, observations, location, photos, prompts, conditioning,
source artifact references and arbitrary metadata. The existing renderer receives
validated geometry through an in-memory V2 adapter; the shared source is not a
private pipeline manifest. Missing behaviors keep the existing explicit idle or
still-pose fallback rules.

Public provenance has fixed fields: source, creator, source version, license,
usage and attribution. There is no reference array or arbitrary extension map.
Structural validation alone cannot decide whether a free-text attribution contains
private information or whether redistribution rights are valid. Current internal
promotion therefore accepts only exact built-in fixture commands under a trusted
local development policy. Fixture releases declare development-only usage and no
taxon fidelity review. Production promotion remains disabled; a future reviewed
rights and taxonomy authority must be implemented explicitly.

`catalog-entry-v1` binds the descriptor to its exact pin, public provenance and
availability revision. Available revision 0 requires verified provenance; revoked
revision 1 preserves identity. Unavailable entries may omit provenance when bytes
cannot be verified. Neither an update nor an unavailable/revoked release selects a
different version for an existing resident. Shared art is generic; private resident
names and observations stay in the owner yard.

The internal `catalog-promotion-command-v1` and
`catalog-revocation-command-v1` authorities describe local fixture tests only.
There is no public promotion/revocation route or new admin credential. Immutable
`catalog-publication-receipt-v1` records bind request ID, command digest, exact pin
and action/status revision. Monotonic revocation compares revision 0; an exact
request retry replays its receipt instead of applying a new transition. Runtime
storage additionally verifies canonical request keys, render SHA256/byte length,
public attribution digest, exact fixture content and transaction consistency.

`catalog-pin-command-v1` is an owner-bound request with a UUID, resident ID, exact
expected prior artwork (including null) and target pin. The owner is supplied by
the authenticated session. `catalog-selection-receipt-v1` persists the command,
its digest and resulting artwork identity under a separate trusted owner key.
`catalog-command-response-v1` returns that receipt projection plus the current
`catalog-overview-v1`. A retry receipt can intentionally name an older pin than the
current overview; replay never reapplies the old selection over a later choice.

The overview lists only trusted catalog taxon IDs, authoritative public names,
pending demand or available/revoked/unavailable releases, and owner-scoped resident
selection status. Unknown imported IDs do not infer taxonomy from a filename or
label. Trusted IDs with contradictory scientific labels remain unsupported until
explicitly corrected. Public and private pins are mutually exclusive. Legacy
private manifests and unannotated backups remain readable; a newer backup carrying
catalog fields requires a compatible consumer and is not universally readable by
old closed clients.

The generated portable schemas are structural authorities only. They do not
replace ownership, session/origin checks, revision compare-and-swap, canonical
hash verification, immutable storage ledgers, exact rights review or renderer
availability checks. The contract corpus retains source-only semantic exceptions
explicitly and freezes reviewed structural digests separately from regeneration.


## Contract verification checkpoint

Independent review approved ten new authorities, twenty new mirrored digests and
the optional catalog pin extension to both backup schema mirrors. All 281 prior
goldens and all 186 prior semantic exceptions remain. The focused contract checks
pass 349 goldens, 11,368 mutations (714 source-valid, 227 explicit source-only
exceptions), 189 reviewed digests and 12 reader-boundary tests. The final inventory
check covers 52 HTTP/SSR operations, 92 authority boundaries and 22 explicit gaps. Full system
verification is recorded separately by the integration owner.
