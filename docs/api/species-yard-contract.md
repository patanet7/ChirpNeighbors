> Mirror of `birdsong-yard-sprites/docs/species-yard-contract.md`. Code paths below refer to that UI repository. The portable schemas are in this repository’s `contracts/` directory.

# Version-2 yard and identification contract

Executable definitions live in `src/lib/domain/yard.ts`; durable operations live in `src/lib/server/storage/repository.ts`. This document describes the local SvelteKit foundation, not a deployed service or working detector.

## Records and ownership

| Record | Meaning |
| --- | --- |
| `Species` | Stable taxon ID and labels. Conflicting IDs/scientific names require explicit resolution. |
| `IdentificationEvent` | Immutable source evidence, observed time or `null`, server ingestion time and provenance. A model candidate is not a confirmed sighting. |
| `Finding` | Derived grouping by effective corrected species/time with event IDs and count; raw events remain intact. |
| `EvidenceCorrection` | Owner-private version-1 append-only species/time change with expected revision, reason and server timestamp; never a new observation. |
| `CollectionEntry` | A species deliberately kept in the owner's collection, independently of yard residency. |
| `BirdInstance` | Named temporary/permanent display instance with its own ID and optional immutable artwork pin. This does not identify an individual wild animal. |
| `Artwork` | Species-bound ID/version, display image, representation and provenance; fixture or reviewed status remains explicit. |

Every repository operation requires an owner supplied by the server session. Ownership is not accepted inside imports or backups. SQLite stores one validated version-2 aggregate per owner with transactional mutations; pipeline tables use a separate schema ledger in the same database. Before initializing repositories, the application checks the existing yard, pipeline and recording migration ledgers through a read-only connection. Unsupported or malformed ledger versions refuse startup before repository writes. This local application preflight does not coordinate migrations across future workers or hosts. Development identity is explicitly opt-in and unavailable in production builds.

## Source-neutral intake

The UI accepts one event or an array, at most 1,000 events and 2 MB per import. `POST /api/yard` wraps them as `{ "action": "import", "events": ... }`; it requires an authenticated session and same-origin JSON request.

```json
{
  "schemaVersion": 2,
  "id": "example:observation-001",
  "species": {
    "id": "cn-species-erithacus-rubecula",
    "commonName": "European Robin",
    "scientificName": "Erithacus rubecula"
  },
  "observedAt": null,
  "source": {
    "kind": "fixture",
    "label": "Synthetic contract example, not a real observation",
    "provider": "contract-fixtures",
    "sourceEventId": "example:observation-001"
  }
}
```

`source.kind` is `fixture`, `manual`, `model` or `external`; the source also carries a stable `sourceEventId` and optional provider/model version. `confidence` is optional and bounded to 0–1. `recordingId`, reference-photo metadata and arbitrary JSON `metadata` are private references/evidence, not instructions to fetch media. Unknown observation time stays `null`; missing confidence is omitted. The receiving server overwrites any supplied `ingestedAt` with its own timestamp.

IDs use ASCII letters/digits and `._:-`, start with a letter/digit and have at most 160 characters; reserved object names are rejected. Fixture species IDs are application IDs, not proof of an eBird taxonomy connection.

Both event ID and `(source.kind, source.provider, source.sourceEventId)` participate in duplicate detection. Canonical equality ignores object-key order and ingestion time. Identical repeats are no-ops; conflicting reuse rejects the entire batch. No correction/deletion of existing evidence is implied by another import. Metadata stays private and does not authorize location collection.

`npm run contracts:export -- --main-repo ../ChirpNeighbors` derives the checked-in `contracts/identification-v2.schema.json` and fixture in both repositories. `contracts:check` detects drift. Main-repository Python validation consumes this generated schema; admission, ownership, idempotency and cross-record invariants remain receiving-server responsibilities. This adapter does not establish live inference, Merlin synchronization or ESP32 capture.

## Structured manual findings and corrections

The collapsed manual form uses catalog IDs already known to the application or owner;
no provider taxon ID is inferred. Unknown observation time remains null; an explicit
UTC time is required otherwise. Each draft retains its UUID through reload and exact
retry. Raw evidence uses `manual:<uuid>` for both event/source identity, so repeat forms
and re-import cannot extend visitor expiry. Private session drafts are keyed by owner.

Correction commands append species/time replacements with a reason, an immutable
submission UUID and expected prior revision. A mismatch returns 409 for explicit
before/after conflict review; no silent rebasing occurs. Correction batches are atomic.
Raw events, notes/provenance and resident/collection/art records remain unchanged.
Findings and effective evidence reflect the latest valid revision. Corrections do not
create or refresh visitors, including unknown-to-recent time changes. See the UI's
`docs/manual-findings.md` for fields, retry behavior, limits and client flow.

Generated `finding-command-v1.schema.json` and `yard-backup-v2.schema.json` accompany
the unchanged identification schema in both repositories. Structural schema validation
is supplemented by owner, catalog, receipt and history-chain checks in the repository.

## Visitors, collection and assets

The provisional visitor policy uses the observation timestamp plus the configured lifetime (default 24 hours, range 1–2,160). Only currently recent evidence can create a visitor. Unknown/future/expired observations remain in Findings without creating one. New recent evidence refreshes an existing temporary visitor; duplicate imports do not extend expiry. Changing the lifetime affects subsequent observations, not existing expiration timestamps.

Automatic admission defaults to one active instance per species. Explicitly adding another permanent instance is supported. Promotion preserves the visitor ID, name and artwork pin, clears expiry, and ensures collection membership. Expired instances and their evidence remain in storage. Removing an instance deletes only that instance; collection, evidence and artworks remain. Scene/palette changes do not recreate these records.

Artwork IDs and per-species versions are immutable. A bird without art receives the first registered version; later registrations preserve existing pins. Images are limited to local paths or embedded PNG/JPEG/WebP; arbitrary external URLs are rejected. Legacy reviewed art and photo provenance survive migration. Pixi and SVG resolve explicitly selected, reviewed versioned manifests from exact resident pins. Approval alone does not select an asset. Missing/corrupt assets retain pins and use labeled fixtures; real generated species artwork remains unavailable.

Simulation is independent of persistence and rendering. Scene slots provide navigation and feed/bath/perch affordances with occupancy arbitration. Idle, movement, perching, singing, feeding, bathing, phase-driven sleep/wake, and bounded decorative play/nest-building run locally with explicit slot capabilities and reservations. These decorative behaviors are not recorded as real observed behavior.

## Versioned scene selection and private region preference

`preferences.scenePin` stores an exact catalog `{ id, version }` or legacy `null`;
`regionPreference` is an optional private continent-scale enum defaulting to
`unspecified`. Legacy garden/courtyard resolves fixed version 1, never latest.
Selecting scenes reanchors objects atomically from manifest placement zones without
changing residents, art pins, collection, evidence/corrections or visitor expiry.
Expected placement snapshots now optionally include the pin to reject stale gestures
across manifest changes. Region does not select artwork, request location or call weather.

`scene-manifest-v1.schema.json` defines the retained 960×540 technical-fixture format:
bounded inline palette assets, required background/ground/foreground layers, shared
object/resident ground depth, walkable/placement zones and explicit navigation points.
The renderer and simulation consume the selected validated geometry. Pixi/SVG ordering
agrees; approved regional artwork is not present. Invalid/missing catalog entries show
a labeled existing fixture while retaining the saved pin. Explicit owner replacement
is required; malformed or incompatible restore data rejects atomically.

Backup-v2 preference extensions default for old data and round-trip new selections;
v1 migration is unchanged. Shared projection exposes only the allowlisted resolved
`garden`/`courtyard` identifier, never region, pin or private manifest. Portable schema
checks are supplemented by application reference/geometry validation. See UI
`docs/scene-manifests.md` and `docs/scene-manifests-checkpoint.md` for behavior and evidence.

## Private recording storage foundation

The UI's local recording service uses separate version-1 SQLite metadata and a
private byte-store interface. Authenticated development owners can upload canonical
PCM16 WAV (mono/stereo 8–48 kHz, 30 seconds, 6 MiB), inspect their metadata, play
single byte ranges/HEAD, delete, and explicitly retry cleanup. Production identity
remains unconfigured and all media routes fail closed. There is no capture UI,
inference call, provider transfer or worker integration.

`recording-metadata-v1.schema.json` is a structural private response contract;
ownership, frame/byte/duration agreement, lifecycle, file integrity and generation
fences require the receiving service. Filenames, paths, location and media bytes
are not contract fields. It is not an upload authorization or a public projection.

Deletion commits a permanent tombstone before file removal. New playback and
processing permits fail immediately; stale simulated results cannot commit through
the synchronous same-database generation guard. Cleanup is a bounded explicit local
retry, not an autonomous worker. Actual derived-output cleanup remains a separate
integration. Failed deletion keeps its capacity reservation until cleanup succeeds;
restart requeues tombstones and may require explicit cleanup before new uploads.
Raw private `recordingId` evidence references are retained.

Yard JSON backups contain no media ledger, bytes or tombstones. Restoring a yard
cannot revive deleted media or remove its tombstone. Whole-filesystem backups and
downloaded copies require their own retention/deletion policy; local unlink is not
secure erasure. Sharing excludes recording references, metadata and private evidence.
See UI `docs/recordings.md` and `docs/recordings-checkpoint.md` for limits and recovery.

## Jobs and generation

Pipeline definitions and hierarchical stage paths have pinned versions. Owner-scoped idempotency keys, durable leases, bounded retries/backoff and cancellation fences protect local execution. Artifact payloads/provenance and review records are immutable; publishing another result creates another version. The workbench advances one stage on request, not through a continuously running hosted worker. See [pipeline contracts and limitations](../src/lib/server/pipeline/README.md).

The fixture pipeline prepares a labeled renderable manifest from existing authored pixels for technical review; this is not generated artwork. `photo-to-animation` stops at an unconfigured provider. Actual source-photo acquisition, taxon review, AI engine choice, costs, external execution and final animation attachment remain unfinished; fixture success must never be relabeled as generation success.

## Backup, migration and public boundary

`GET /api/backup` exports `{ format: "chirpneighbors-yard", version: 2, exportedAt, data }` for the current owner. A confirmed restore replaces only that owner's yard after full validation. Raw version-1 React backups are accepted through explicit migration, preserving event/resident IDs, art pins, reference metadata and preferences. The legacy browser key is `chirpneighbors.yard.v1`; importing it is explicit, not an automatic server-side merge. Pipeline jobs and recording bytes are not part of this yard backup. Version-2 data now includes optional `corrections`, defaulting to an empty array for older data/backups. Version-1 correction records preserve expected parent/value, replacement, reason and server time. Restore validates the complete chain and rejects gaps, forks or missing references atomically. Confirmed replacement restore includes the saved history; old strict readers may reject the new field rather than discard it.

The development aggregate limit is 16 MiB per owner; the yard command body limit is 20 MB to allow restore, while observation imports retain their 2 MB limit. The SQLite file survives server restart. These limits and persistence do not constitute a production backup/retention strategy.

`GET /api/share-preview` is authenticated and creates no public token or share. Its separate allowlist includes only scene/palette, ordinal display keys, trusted catalog taxon labels and safe catalog keys. It excludes location (including coarse region), audio, EXIF/GPS, private/source IDs, observation times, user names, free-text species labels, URLs and provenance. Unknown taxa receive a generic label. Private data is removed from the response itself, not merely hidden in the UI.

Email/Google sign-in and initial US hosting are selected directions, not provisioned capabilities. Local recording APIs do not provide hosted delivery, capture UI, cross-service derived deletion, account deletion/export, backup retention, sharing authorization/revocation or hosted-worker deployment. No hardware, provider, production authentication or public-sharing service is connected by this contract.
