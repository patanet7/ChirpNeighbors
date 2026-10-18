import { z } from 'zod';
import { sceneManifestSchema } from './manifest.ts';
import {
  INTEGRATION10_GROUND_RELEASE,
  INTEGRATION10_GROUND_REVIEW,
} from './integration10-ground.ts';

export const INTEGRATION10_SCENE_PIN = Object.freeze({
  id: 'sd-inland-layered-spring-v2',
  version: 2,
});
export function isIntegration10Pin(pin: { id: string; version: number } | null | undefined) {
  return pin?.id === INTEGRATION10_SCENE_PIN.id && pin.version === INTEGRATION10_SCENE_PIN.version;
}
/** Separate grammar: V1's three inline fixture layers and geometry never change. */
const exactBounds = (left: number, right: number, top: number, bottom: number) =>
  z
    .object({
      left: z.literal(left),
      right: z.literal(right),
      top: z.literal(top),
      bottom: z.literal(bottom),
    })
    .strict();
export const registeredSceneManifestV2Schema = sceneManifestSchema
  .innerType()
  .omit({
    schemaVersion: true,
    id: true,
    version: true,
    representation: true,
    provenance: true,
    assets: true,
    layers: true,
  })
  .extend({
    schemaVersion: z.literal(2),
    zones: z
      .object({
        placement: z.tuple([exactBounds(0, 960, 208.75, 540)]),
        walkable: z.tuple([exactBounds(24, 936, 224, 532)]),
      })
      .strict(),
    navigation: z
      .object({
        mode: z.literal('flight-corridors'),
        groundSlots: z
          .array(
            z
              .object({
                id: z
                  .string()
                  .min(1)
                  .max(80)
                  .regex(/^ground:[A-Za-z0-9:_-]+$/),
                x: z.number().finite().min(24).max(936),
                y: z.number().finite().min(224).max(532),
              })
              .strict(),
          )
          .min(1)
          .max(128),
        roaming: exactBounds(24, 936, 228, 518),
        overflow: z
          .object({ left: z.literal(24), right: z.literal(936), y: z.literal(530) })
          .strict(),
      })
      .strict(),
    publicSceneId: z.literal('garden'),
    id: z.literal(INTEGRATION10_SCENE_PIN.id),
    version: z.literal(2),
    representation: z.literal('source-registered-planar-yard'),
    provenance: z
      .object({
        kind: z.literal('inspected-integration10-source'),
        approvedRegionalArt: z.literal(false),
        sourceReleaseDigest: z.literal(INTEGRATION10_GROUND_RELEASE.sourceReleaseDigest),
      })
      .strict(),
    assets: z.tuple([
      z.object({ id: z.literal('sky'), kind: z.literal('retained-source-raster') }).strict(),
      z.object({ id: z.literal('mountains'), kind: z.literal('retained-source-raster') }).strict(),
      z
        .object({ id: z.literal('ground-spring'), kind: z.literal('retained-source-raster') })
        .strict(),
      z.object({ id: z.literal('fence'), kind: z.literal('retained-source-raster') }).strict(),
    ]),
    layers: z
      .object({
        background: z.object({ order: z.literal(0), assetId: z.literal('sky') }).strict(),
        ground: z.object({ order: z.literal(1), assetId: z.literal('ground-spring') }).strict(),
        foreground: z.object({ order: z.literal(3), assetId: z.null() }).strict(),
      })
      .strict(),
  })
  .strict();
export type RegisteredSceneManifestV2 = z.infer<typeof registeredSceneManifestV2Schema>;
export const integration10Scene: RegisteredSceneManifestV2 = registeredSceneManifestV2Schema.parse({
  schemaVersion: 2,
  ...INTEGRATION10_SCENE_PIN,
  publicSceneId: 'garden',
  label: 'San Diego inland layered spring yard',
  representation: 'source-registered-planar-yard',
  provenance: {
    kind: 'inspected-integration10-source',
    approvedRegionalArt: false,
    sourceReleaseDigest: INTEGRATION10_GROUND_RELEASE.sourceReleaseDigest,
  },
  world: { width: 960, height: 540 },
  assets: ['sky', 'mountains', 'ground-spring', 'fence'].map((id) => ({
    id,
    kind: 'retained-source-raster',
  })),
  layers: {
    background: { order: 0, assetId: 'sky' },
    ground: { order: 1, assetId: 'ground-spring' },
    foreground: { order: 3, assetId: null },
  },
  depth: { order: 2, sort: 'ground-y', actorOffset: 0.25, weatherOrder: 4 },
  zones: {
    placement: [INTEGRATION10_GROUND_REVIEW.worldFloor],
    walkable: [{ left: 24, right: 936, top: 224, bottom: 532 }],
  },
  navigation: {
    mode: 'flight-corridors',
    groundSlots: Array.from({ length: 40 }, (_, i) => ({
      id: `ground:inland:${i}`,
      x: 64 + (i % 8) * 118,
      y: 240 + Math.floor(i / 8) * 60,
    })),
    roaming: { left: 24, right: 936, top: 228, bottom: 518 },
    overflow: { left: 24, right: 936, y: 530 },
  },
});
