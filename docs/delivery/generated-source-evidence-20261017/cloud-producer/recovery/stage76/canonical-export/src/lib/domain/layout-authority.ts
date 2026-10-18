import { isIntegration10Pin } from '../scenes/integration10-scene.ts';
import { INTEGRATION10_GROUND_RELEASE } from '../scenes/integration10-ground.ts';
import { z } from 'zod';
import { regionalBackgroundSchema, regionalSourceExportDigests } from './regional-yard.ts';
import { idSchema } from './primitives.ts';
import { placementKey, placementSnapshotSchema } from './scene.ts';
import type { YardSnapshot } from './yard.ts';

const digest = z.string().regex(/^[a-f0-9]{64}$/);
/** Release identity only. This schema grants no geometry or source admission. */
export const groundReleaseBindingSchema = z
  .object({
    id: idSchema,
    version: z.number().int().positive().max(1_000_000),
    sourceReleaseDigest: digest,
    geometryDigest: digest,
    calibrationDigest: digest,
  })
  .strict();
/** Independently versioned reader: V1 positions and published schemas keep their meaning. */
export const placementSnapshotV2Schema = placementSnapshotSchema
  .extend({
    schemaVersion: z.literal(2),
    ownerId: idSchema,
    source: z.object({ id: regionalBackgroundSchema, revision: digest }).strict().nullable(),
    ground: groundReleaseBindingSchema.nullable(),
  })
  .strict();
export const placementSnapshotReaderSchema = z.union([
  placementSnapshotSchema,
  placementSnapshotV2Schema,
]);
export type PlacementSnapshotReader = z.infer<typeof placementSnapshotReaderSchema>;
export type PlacementSnapshotV2 = z.infer<typeof placementSnapshotV2Schema>;
export function capturePlacement(
  ownerId: string,
  snapshot: Pick<YardSnapshot, 'preferences' | 'environment'>,
): PlacementSnapshotV2 {
  return placementContext(
    ownerId,
    snapshot.preferences.scene,
    snapshot.environment.objects,
    snapshot.preferences.scenePin,
    snapshot.preferences.candidateRegionalBackground ?? null,
  );
}
export function placementContext(
  ownerId: string,
  scene: PlacementSnapshotV2['scene'],
  objects: readonly PlacementSnapshotV2['objects'][number][],
  scenePin: PlacementSnapshotV2['scenePin'] = null,
  source: z.infer<typeof regionalBackgroundSchema> | null = null,
): PlacementSnapshotV2 {
  return placementSnapshotV2Schema.parse({
    schemaVersion: 2,
    ownerId,
    scene,
    scenePin,
    objects,
    source: source ? { id: source, revision: regionalSourceExportDigests[source] } : null,
    ground:
      scene === 'garden' && isIntegration10Pin(scenePin) ? INTEGRATION10_GROUND_RELEASE : null,
  });
}

export function samePlacementAuthority(
  first: PlacementSnapshotReader,
  second: PlacementSnapshotReader,
): boolean {
  if (
    placementKey(first.scene, [], first.scenePin) !==
    placementKey(second.scene, [], second.scenePin)
  )
    return false;
  if ('schemaVersion' in first && 'schemaVersion' in second)
    return (
      first.ownerId === second.ownerId &&
      first.source?.id === second.source?.id &&
      first.source?.revision === second.source?.revision &&
      first.ground?.id === second.ground?.id &&
      first.ground?.version === second.ground?.version &&
      first.ground?.sourceReleaseDigest === second.ground?.sourceReleaseDigest &&
      first.ground?.geometryDigest === second.ground?.geometryDigest &&
      first.ground?.calibrationDigest === second.ground?.calibrationDigest
    );
  const versioned = 'schemaVersion' in first ? first : 'schemaVersion' in second ? second : null;
  // A legacy/null context cannot bypass a source- or geometry-bound yard.
  return !versioned || (versioned.source === null && versioned.ground === null);
}
export function samePlacement(
  first: PlacementSnapshotReader,
  second: PlacementSnapshotReader,
): boolean {
  return (
    samePlacementAuthority(first, second) &&
    placementKey(first.scene, first.objects, first.scenePin) ===
      placementKey(second.scene, second.objects, second.scenePin)
  );
}
