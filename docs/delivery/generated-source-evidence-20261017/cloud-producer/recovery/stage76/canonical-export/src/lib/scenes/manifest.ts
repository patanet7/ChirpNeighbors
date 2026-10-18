import { z } from 'zod';
import type { RegisteredSceneManifestV2 } from './integration10-scene.ts';
import { idSchema } from '../domain/primitives.ts';

/** V1 intentionally retains the existing renderer/placement coordinate system. */
export const WORLD_WIDTH = 960;
export const WORLD_HEIGHT = 540;
export const sceneSettingSchema = z.enum(['garden', 'courtyard']);
export type SceneSetting = z.infer<typeof sceneSettingSchema>;
export const scenePinSchema = z
  .object({ id: idSchema, version: z.number().int().min(1).max(1000000) })
  .strict();
export type ScenePin = z.infer<typeof scenePinSchema>;
/** Optional continent-scale preference, never inferred from a device or sent to a provider. */
export const regionPreferenceSchema = z.enum([
  'unspecified',
  'europe',
  'north-america',
  'south-america',
  'africa',
  'asia',
  'oceania',
]);
export const paletteColorSchema = z.enum([
  'sky',
  'skyLow',
  'grass',
  'grassLight',
  'leaf',
  'leafLight',
  'trunk',
  'wood',
  'wall',
  'stone',
  'water',
  'flower',
  'glow',
]);
export const pixelRectSchema = z
  .object({
    x: z.number().finite().int().min(0),
    y: z.number().finite().int().min(0),
    width: z.number().finite().int().min(1),
    height: z.number().finite().int().min(1),
    color: paletteColorSchema,
    alpha: z.number().finite().min(0).max(1).optional(),
  })
  .strict();
export type ScenePixelRect = z.infer<typeof pixelRectSchema>;
export const boundsSchema = z
  .object({
    left: z.number().finite().min(0),
    right: z.number().finite().max(WORLD_WIDTH),
    top: z.number().finite().min(0),
    bottom: z.number().finite().max(WORLD_HEIGHT),
  })
  .strict()
  .refine((b) => b.left < b.right && b.top < b.bottom, 'Zones must have positive area.');
export type SceneBounds = z.infer<typeof boundsSchema>;
export const containsPoint = (b: SceneBounds, x: number, y: number) =>
  x >= b.left && x <= b.right && y >= b.top && y <= b.bottom;
export const containsBounds = (outer: SceneBounds, inner: SceneBounds) =>
  containsPoint(outer, inner.left, inner.top) && containsPoint(outer, inner.right, inner.bottom);
const point = z.object({ id: idSchema, x: z.number().finite(), y: z.number().finite() }).strict();
const layer = (order: 0 | 1 | 3) =>
  z.object({ order: z.literal(order), assetId: idSchema }).strict();
export const sceneManifestSchema = z
  .object({
    schemaVersion: z.literal(1),
    id: idSchema,
    version: scenePinSchema.shape.version,
    publicSceneId: sceneSettingSchema,
    label: z.string().min(1).max(80),
    representation: z.literal('technical-fixture'),
    provenance: z
      .object({
        kind: z.literal('existing-authored-geometry'),
        approvedRegionalArt: z.literal(false),
      })
      .strict(),
    world: z.object({ width: z.literal(WORLD_WIDTH), height: z.literal(WORLD_HEIGHT) }).strict(),
    assets: z
      .array(
        z
          .object({
            id: idSchema,
            kind: z.literal('inline-palette-rectangles'),
            rectangles: z.array(pixelRectSchema).min(1).max(512),
          })
          .strict(),
      )
      .min(3)
      .max(3),
    layers: z.object({ background: layer(0), ground: layer(1), foreground: layer(3) }).strict(),
    depth: z
      .object({
        order: z.literal(2),
        sort: z.literal('ground-y'),
        actorOffset: z.literal(0.25),
        weatherOrder: z.literal(4),
      })
      .strict(),
    zones: z
      .object({
        placement: z.array(boundsSchema).min(1).max(8),
        walkable: z.array(boundsSchema).min(1).max(8),
      })
      .strict(),
    navigation: z
      .object({
        mode: z.literal('flight-corridors'),
        groundSlots: z.array(point).min(1).max(128),
        roaming: boundsSchema,
        overflow: z
          .object({ left: z.number().finite(), right: z.number().finite(), y: z.number().finite() })
          .strict(),
      })
      .strict(),
  })
  .strict()
  .superRefine((manifest, ctx) => {
    const fail = (message: string) => ctx.addIssue({ code: 'custom', message });
    const assets = new Map(manifest.assets.map((asset) => [asset.id, asset]));
    if (assets.size !== manifest.assets.length) fail('Scene asset IDs must be unique.');
    const references = Object.values(manifest.layers).map((value) => value.assetId);
    if (new Set(references).size !== 3 || references.some((id) => !assets.has(id)))
      fail('Each required scene layer needs its own valid asset.');
    for (const asset of manifest.assets)
      for (const rect of asset.rectangles)
        if (
          rect.x + rect.width > manifest.world.width ||
          rect.y + rect.height > manifest.world.height
        )
          fail('Scene asset pixels must fit the world bounds.');
    const { groundSlots, roaming, overflow } = manifest.navigation;
    if (new Set(groundSlots.map((slot) => slot.id)).size !== groundSlots.length)
      fail('Ground slot IDs must be unique.');
    if (
      groundSlots.some(
        (slot) =>
          !slot.id.startsWith('ground:') ||
          !manifest.zones.walkable.some((zone) => containsPoint(zone, slot.x, slot.y)),
      )
    )
      fail('Ground slots must be named ground:* and lie in walkable zones.');
    if (!manifest.zones.walkable.some((zone) => containsBounds(zone, roaming)))
      fail('Roaming bounds must fit a walkable zone.');
    if (
      overflow.left >= overflow.right ||
      !manifest.zones.walkable.some(
        (zone) =>
          containsPoint(zone, overflow.left, overflow.y) &&
          containsPoint(zone, overflow.right, overflow.y),
      )
    )
      fail('Overflow anchors must fit a walkable zone.');
    if (
      manifest.zones.placement.some(
        (zone) =>
          overflow.y >= zone.top - 12 &&
          overflow.y <= zone.bottom + 12 &&
          overflow.right >= zone.left - 20 &&
          overflow.left <= zone.right + 20,
      )
    )
      fail('Overflow anchors must remain clear of placeable footprints.');
  });
export type SceneManifestV1 = z.infer<typeof sceneManifestSchema>;
export type SceneManifest = SceneManifestV1 | RegisteredSceneManifestV2;
export const sceneLayers = (manifest: SceneManifest) =>
  [
    ['background', manifest.layers.background.order],
    ['ground', manifest.layers.ground.order],
    ['objects-and-residents', manifest.depth.order],
    ['foreground', manifest.layers.foreground.order],
    ['weather-lighting', manifest.depth.weatherOrder],
  ]
    .sort((a, b) => Number(a[1]) - Number(b[1]))
    .map(([name]) => String(name));
export function layerPrimitives(manifest: SceneManifest, name: keyof SceneManifest['layers']) {
  if (manifest.schemaVersion === 2) return [];
  return manifest.assets.find((asset) => asset.id === manifest.layers[name].assetId)!.rectangles;
}
