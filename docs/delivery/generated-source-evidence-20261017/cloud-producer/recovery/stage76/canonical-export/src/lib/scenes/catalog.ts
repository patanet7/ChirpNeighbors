import { z } from 'zod';
import { integration10Scene, registeredSceneManifestV2Schema } from './integration10-scene.ts';
import {
  backgroundPrimitives,
  groundPrimitives,
  foregroundPrimitives,
} from './fixture-geometry.ts';
import {
  sceneManifestSchema,
  scenePinSchema,
  type SceneManifest,
  type SceneManifestV1,
  type ScenePin,
  type SceneSetting,
  type ScenePixelRect,
} from './manifest.ts';

/** Clip legacy edge pixels to the same canvas boundary; visible artwork is unchanged. */
function clip(rectangles: ScenePixelRect[]): ScenePixelRect[] {
  return rectangles
    .map((rect) => ({
      ...rect,
      width: Math.min(rect.width, 960 - rect.x),
      height: Math.min(rect.height, 540 - rect.y),
    }))
    .filter((rect) => rect.width > 0 && rect.height > 0);
}
function fixture(setting: SceneSetting): SceneManifestV1 {
  return sceneManifestSchema.parse({
    schemaVersion: 1,
    id: `fixture-${setting}`,
    version: 1,
    publicSceneId: setting,
    label: `${setting === 'garden' ? 'Garden' : 'Courtyard'} technical fixture`,
    representation: 'technical-fixture',
    provenance: { kind: 'existing-authored-geometry', approvedRegionalArt: false },
    world: { width: 960, height: 540 },
    assets: [
      {
        id: 'background',
        kind: 'inline-palette-rectangles',
        rectangles: clip(backgroundPrimitives(setting)),
      },
      {
        id: 'ground',
        kind: 'inline-palette-rectangles',
        rectangles: clip(groundPrimitives(setting)),
      },
      {
        id: 'foreground',
        kind: 'inline-palette-rectangles',
        rectangles: clip(foregroundPrimitives()),
      },
    ],
    layers: {
      background: { order: 0, assetId: 'background' },
      ground: { order: 1, assetId: 'ground' },
      foreground: { order: 3, assetId: 'foreground' },
    },
    depth: { order: 2, sort: 'ground-y', actorOffset: 0.25, weatherOrder: 4 },
    zones: {
      placement: [
        setting === 'garden'
          ? { left: 40, right: 920, top: 340, bottom: 510 }
          : { left: 90, right: 870, top: 355, bottom: 495 },
      ],
      walkable: [
        { left: 70, right: 890, top: 360, bottom: 510 },
        { left: 70, right: 890, top: 520, bottom: 532 },
      ],
    },
    navigation: {
      mode: 'flight-corridors',
      groundSlots: Array.from({ length: 24 }, (_, i) => ({
        id: `ground:${Math.floor(i / 8)}:${i % 8}`,
        x: 100 + (i % 8) * 108,
        y: 370 + Math.floor(i / 8) * 64,
      })),
      roaming: { left: 70, right: 890, top: 375, bottom: 507 },
      overflow: { left: 90, right: 870, y: 525 },
    },
  });
}
function freeze<T>(value: T): T {
  if (value && typeof value === 'object') {
    for (const child of Object.values(value)) freeze(child);
    Object.freeze(value);
  }
  return value;
}
const fixtures = freeze({ garden: fixture('garden'), courtyard: fixture('courtyard') });
export const SCENE_CATALOG: readonly SceneManifest[] = Object.freeze([
  ...Object.values(fixtures),
  freeze(integration10Scene),
]);
export const fixtureScene = (setting: SceneSetting) => fixtures[setting];
export const legacyScenePin = (setting: SceneSetting): ScenePin => ({
  id: fixtures[setting].id,
  version: 1,
});
export interface ResolvedScene {
  requested: ScenePin;
  manifest: SceneManifest;
  status: 'ready' | 'unavailable';
  message: string;
  /** Includes validated payload; even an incorrectly replaced catalog entry cannot reuse stale geometry. */
  key: string;
}
/** Bundled allowlist only. No filesystem/URL/device/provider lookup or implicit newest-version lookup. */
export function resolveScene(
  setting: SceneSetting,
  pin?: ScenePin | null,
  catalog: readonly unknown[] = SCENE_CATALOG,
): ResolvedScene {
  const requested = pin ?? legacyScenePin(setting);
  const candidates = catalog.filter(
    (entry): entry is Record<string, unknown> =>
      !!entry &&
      typeof entry === 'object' &&
      'id' in entry &&
      'version' in entry &&
      entry.id === requested.id &&
      entry.version === requested.version,
  );
  const parsed =
    candidates.length === 1
      ? z.union([sceneManifestSchema, registeredSceneManifestV2Schema]).safeParse(candidates[0])
      : undefined;
  const ready =
    scenePinSchema.safeParse(requested).success &&
    parsed?.success &&
    parsed.data.publicSceneId === setting;
  const manifest = ready && parsed?.success ? parsed.data : fixtureScene(setting);
  const status = ready ? 'ready' : 'unavailable';
  return {
    requested: { ...requested },
    manifest,
    status,
    message: ready
      ? `${manifest.label}. ${manifest.schemaVersion === 2 ? 'Inspected planar floor; source paint remains a development candidate.' : 'Regional artwork is not reviewed.'}`
      : 'Selected scene manifest is unavailable or invalid. Showing the existing technical fixture; your saved scene selection is retained.',
    key: JSON.stringify([requested, status, manifest]),
  };
}
