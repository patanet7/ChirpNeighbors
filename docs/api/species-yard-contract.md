> Mirror of `birdsong-yard-sprites/docs/species-yard-contract.md`. Code paths below refer to that UI repository. The portable schema is in this repository’s `contracts/` directory.

# Version-2 yard and identification contract

Executable definitions live in `src/lib/domain/yard.ts`; durable operations live in `src/lib/server/storage/repository.ts`. This document describes the local SvelteKit foundation, not a deployed service or working detector.

## Records and ownership

| Record | Meaning |
| --- | --- |
| `Species` | Stable taxon ID and labels. Conflicting IDs/scientific names require explicit resolution. |
| `IdentificationEvent` | Immutable source evidence, observed time or `null`, server ingestion time and provenance. A model candidate is not a confirmed sighting. |
| `Finding` | Derived grouping by species with event IDs, count and known time range; raw events remain intact. |
| `CollectionEntry` | A species deliberately kept in the owner's collection, independently of yard residency. |
| `BirdInstance` | Named temporary/permanent display instance with its own ID and optional immutable artwork pin. This does not identify an individual wild animal. |
| `Artwork` | Species-bound ID/version, display image, representation and provenance; fixture or reviewed status remains explicit. |

Every repository operation requires an owner supplied by the server session. Ownership is not accepted inside imports or backups. SQLite stores one validated version-2 aggregate per owner with transactional mutations; pipeline tables use a separate schema ledger in the same database. Unsupported future yard database versions fail rather than being silently downgraded. Development identity is explicitly opt-in and unavailable in production builds.

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

## Visitors, collection and assets

The provisional visitor policy uses the observation timestamp plus the configured lifetime (default 24 hours, range 1–2,160). Only currently recent evidence can create a visitor. Unknown/future/expired observations remain in Findings without creating one. New recent evidence refreshes an existing temporary visitor; duplicate imports do not extend expiry. Changing the lifetime affects subsequent observations, not existing expiration timestamps.

Automatic admission defaults to one active instance per species. Explicitly adding another permanent instance is supported. Promotion preserves the visitor ID, name and artwork pin, clears expiry, and ensures collection membership. Expired instances and their evidence remain in storage. Removing an instance deletes only that instance; collection, evidence and artworks remain. Scene/palette changes do not recreate these records.

Artwork IDs and per-species versions are immutable. A bird without art receives the first registered version; later registrations preserve existing pins. Images are limited to local paths or embedded PNG/JPEG/WebP; arbitrary external URLs are rejected. Legacy reviewed art and photo provenance survive migration. The current Pixi scene still renders authored fixture frames: storing an artwork or approving a pipeline artifact does not yet load a generated animation bundle into the renderer.

Simulation is independent of persistence and rendering. Scene slots provide navigation and feed/bath/perch affordances with occupancy arbitration. Idle, movement, perching, singing, feeding and bathing run locally; sleeping, playing and nesting are reserved states. These decorative behaviors are not recorded as real observed behavior.

## Jobs and generation

Pipeline definitions and hierarchical stage paths have pinned versions. Owner-scoped idempotency keys, durable leases, bounded retries/backoff and cancellation fences protect local execution. Artifact payloads/provenance and review records are immutable; publishing another result creates another version. The workbench advances one stage on request, not through a continuously running hosted worker. See `birdsong-yard-sprites/src/lib/server/pipeline/README.md` for pipeline contracts and limitations.

The fixture pipeline prepares a labeled manifest for review with no generated frames. `photo-to-animation` stops at an unconfigured provider. Actual source-photo acquisition, taxon review, AI engine choice, costs, external execution and final animation attachment remain unfinished; fixture success must never be relabeled as generation success.

## Backup, migration and public boundary

`GET /api/backup` exports `{ format: "chirpneighbors-yard", version: 2, exportedAt, data }` for the current owner. A confirmed restore replaces only that owner's yard after full validation. Raw version-1 React backups are accepted through explicit migration, preserving event/resident IDs, art pins, reference metadata and preferences. The legacy browser key is `chirpneighbors.yard.v1`; importing it is explicit, not an automatic server-side merge. Pipeline jobs and recording bytes are not part of this yard backup.

The development aggregate limit is 16 MiB per owner; the yard command body limit is 20 MB to allow restore, while observation imports retain their 2 MB limit. The SQLite file survives server restart. These limits and persistence do not constitute a production backup/retention strategy.

`GET /api/share-preview` is authenticated and creates no public token or share. Its separate allowlist includes only scene/palette, ordinal display keys, trusted catalog taxon labels and safe catalog keys. It excludes location (including coarse region), audio, EXIF/GPS, private/source IDs, observation times, user names, free-text species labels, URLs and provenance. Unknown taxa receive a generic label. Private data is removed from the response itself, not merely hidden in the UI.

Email/Google sign-in, initial US hosting and owner-private recordings with deletion are selected directions, not provisioned capabilities. Recording upload/storage/deletion, account deletion/export across all services, backup retention, sharing authorization/revocation and hosted-worker deployment need explicit integration. No hardware, provider, real authentication or public-sharing service is connected by this contract.
