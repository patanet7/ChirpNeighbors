import { integration10ContainsFootprint } from '../scenes/integration10-ground.ts';
import { z } from 'zod';
import {
  canonicalObjectIdSchema,
  canonicalYardEntry,
  canonicalObjectDefinition,
  type CanonicalObjectId,
} from './canonical-yard.ts';
import { YardValidationError } from './validation-error.ts';
import { idSchema } from './primitives.ts';
import { fixtureScene, legacyScenePin } from '../scenes/catalog.ts';
import {
  sceneSettingSchema,
  scenePinSchema,
  type SceneManifest,
  type SceneSetting,
  type ScenePin,
} from '../scenes/manifest.ts';
export {
  WORLD_WIDTH,
  WORLD_HEIGHT,
  sceneSettingSchema,
  type SceneSetting,
} from '../scenes/manifest.ts';
import { WORLD_WIDTH, WORLD_HEIGHT, containsBounds } from '../scenes/manifest.ts';
export type SceneInput = SceneSetting | SceneManifest;
export const sceneManifestOf = (input: SceneInput): SceneManifest =>
  typeof input === 'string' ? fixtureScene(input) : input;

export const MAX_OBJECTS = 12;
export const OBJECT_CLEARANCE = 8;
export const SCENE_LAYERS = [
  'background',
  'ground',
  'objects',
  'residents',
  'foreground',
  'weather-lighting',
] as const;
export type SceneLayer = (typeof SCENE_LAYERS)[number];
/** Objects and birds share physical depth ordering even though their semantic categories differ. */
export const RENDER_LAYERS = [
  'background',
  'ground',
  'objects-and-residents',
  'foreground',
  'weather-lighting',
] as const;
export const objectKindSchema = z.enum(['perch', 'feeder', 'bath', 'nest', 'plant']);
export type ObjectKind = z.infer<typeof objectKindSchema>;
export type ObjectCapability = 'play' | 'nest-building';
export interface ObjectSlot {
  id: string;
  affordance: 'perch' | 'feed' | 'bath' | 'nest';
  dx: number;
  dy: number;
  /** Explicit decorative daytime use; the same physical slot still arbitrates all claims. */
  capability?: ObjectCapability;
}
export interface ObjectDefinition {
  label: string;
  /** Ground footprint centered at x,y. Height extends upwards from y. */
  width: number;
  depth: number;
  height: number;
  slots: readonly ObjectSlot[];
}
export const OBJECT_CATALOG: Readonly<Record<ObjectKind, ObjectDefinition>> = {
  perch: {
    label: 'Perch',
    width: 96,
    depth: 30,
    height: 130,
    slots: [
      { id: 'left', affordance: 'perch', dx: -25, dy: -115 },
      { id: 'right', affordance: 'perch', dx: 25, dy: -115, capability: 'play' },
    ],
  },
  feeder: {
    label: 'Feeder',
    width: 84,
    depth: 46,
    height: 74,
    slots: [
      { id: 'left', affordance: 'feed', dx: -18, dy: -24 },
      { id: 'right', affordance: 'feed', dx: 18, dy: -24 },
    ],
  },
  bath: {
    label: 'Birdbath',
    width: 100,
    depth: 54,
    height: 80,
    slots: [
      { id: 'left', affordance: 'bath', dx: -18, dy: -68 },
      { id: 'right', affordance: 'bath', dx: 18, dy: -68 },
    ],
  },
  plant: { label: 'California bush sunflower', width: 52, depth: 36, height: 100, slots: [] },
  nest: {
    label: 'Nest',
    width: 72,
    depth: 36,
    height: 50,
    slots: [{ id: 'center', affordance: 'nest', dx: 0, dy: -30, capability: 'nest-building' }],
  },
};
export const yardObjectSchema = z
  .object({
    id: idSchema,
    kind: objectKindSchema,
    catalogId: canonicalObjectIdSchema.optional(),
    x: z.number().finite().min(0).max(WORLD_WIDTH),
    y: z.number().finite().min(0).max(WORLD_HEIGHT),
  })
  .strict()
  .superRefine((object, ctx) => {
    if (object.catalogId && canonicalYardEntry(object.catalogId).kind !== object.kind)
      ctx.addIssue({
        code: 'custom',
        message: 'Canonical object must match its owned inventory kind.',
      });
  });
export type YardObject = z.infer<typeof yardObjectSchema>;
export function objectDefinition(object: YardObject): ObjectDefinition {
  return canonicalObjectDefinition(object) ?? OBJECT_CATALOG[object.kind];
}
export const yardObjectsSchema = z
  .array(yardObjectSchema)
  .max(MAX_OBJECTS)
  .superRefine((objects, ctx) => {
    if (new Set(objects.map((object) => object.id)).size !== objects.length)
      ctx.addIssue({ code: 'custom', message: 'Yard object IDs must be unique.' });
  });
/** Expected layout for compare-and-set placement. Unrelated observations/weather do not conflict. */
export const placementSnapshotSchema = z
  .object({
    scene: sceneSettingSchema,
    scenePin: scenePinSchema.nullable().optional(),
    objects: yardObjectsSchema,
  })
  .strict();
export type PlacementSnapshot = z.infer<typeof placementSnapshotSchema>;
export function placementKey(
  scene: SceneSetting,
  objects: readonly YardObject[],
  pin?: ScenePin | null,
): string {
  return JSON.stringify([
    scene,
    pin ?? legacyScenePin(scene),
    [...objects]
      .sort((a, b) => a.id.localeCompare(b.id))
      .map(({ id, kind, x, y, catalogId }) =>
        catalogId ? [id, kind, x, y, catalogId] : [id, kind, x, y],
      ),
  ]);
}
export interface PlacementBounds {
  left: number;
  right: number;
  top: number;
  bottom: number;
}
/** Ground zones keep complete footprints away from scenery edges and structural foreground. */
export const PLACEMENT_BOUNDS: Readonly<Record<SceneSetting, PlacementBounds>> = {
  garden: placementBounds('garden'),
  courtyard: placementBounds('courtyard'),
};
function placementBounds(setting: SceneSetting): PlacementBounds {
  const first = fixtureScene(setting).zones.placement[0];
  if (!first) throw new Error('Fixture scene requires a placement zone');
  return first;
}
/** Whole visual canvas supplies arrangement hit areas; collision still uses the ground footprint. */
export function objectVisualBounds(object: YardObject): PlacementBounds {
  if (object.catalogId) {
    const entry = canonicalYardEntry(object.catalogId);
    return {
      left: -entry.pivot.x,
      right: entry.width - entry.pivot.x,
      top: -entry.pivot.y,
      bottom: entry.height - entry.pivot.y,
    };
  }
  const definition = objectDefinition(object);
  return {
    left: -definition.width / 2,
    right: definition.width / 2,
    top: -definition.height,
    bottom: definition.depth / 2,
  };
}
export function objectFootprint(object: YardObject): PlacementBounds {
  const definition = objectDefinition(object);
  return {
    left: object.x - definition.width / 2,
    right: object.x + definition.width / 2,
    top: object.y - definition.depth / 2,
    bottom: object.y + definition.depth / 2,
  };
}
export function objectsOverlap(first: YardObject, second: YardObject): boolean {
  const a = objectFootprint(first),
    b = objectFootprint(second);
  return (
    a.left < b.right + OBJECT_CLEARANCE &&
    a.right + OBJECT_CLEARANCE > b.left &&
    a.top < b.bottom + OBJECT_CLEARANCE &&
    a.bottom + OBJECT_CLEARANCE > b.top
  );
}
export function isPlacementValid(
  object: YardObject,
  objects: readonly YardObject[],
  setting: SceneInput,
): boolean {
  const manifest = sceneManifestOf(setting),
    bounds = objectFootprint(object);
  return (
    (manifest.schemaVersion === 2
      ? integration10ContainsFootprint(bounds)
      : manifest.zones.placement.some((area) => containsBounds(area, bounds))) &&
    object.y - objectDefinition(object).height >= 24 &&
    (object.catalogId
      ? canonicalSpriteInBounds(object)
      : object.kind !== 'plant' ||
        (object.x >= 59 && object.x <= WORLD_WIDTH - 58 && object.y <= WORLD_HEIGHT - 5)) &&
    !objects.some((other) => other.id !== object.id && objectsOverlap(object, other))
  );
}
export function validateObjects(input: unknown, setting: SceneInput): YardObject[] {
  const objects = yardObjectsSchema.parse(input);
  for (const object of objects)
    if (!isPlacementValid(object, objects, setting))
      throw new YardValidationError('objectPlacement');
  return objects;
}
export function defaultObjects(setting: SceneInput = 'garden'): YardObject[] {
  const objects: YardObject[] = [
    { id: 'fixture-perch', kind: 'perch', x: 180, y: 420 },
    { id: 'fixture-feeder', kind: 'feeder', x: 400, y: 465 },
    { id: 'fixture-bath', kind: 'bath', x: 700, y: 445 },
    { id: 'fixture-nest', kind: 'nest', x: 820, y: 475 },
  ];
  return validateObjects(objects, setting);
}
function canonicalSpriteInBounds(object: YardObject): boolean {
  const entry = canonicalYardEntry(object.catalogId!);
  return (
    object.x >= entry.pivot.x &&
    object.x + entry.width - entry.pivot.x <= WORLD_WIDTH &&
    object.y >= entry.pivot.y + 24 &&
    object.y + entry.height - entry.pivot.y <= WORLD_HEIGHT
  );
}
function placementCandidates(
  kind: ObjectKind,
  setting: SceneInput,
  desired: { x: number; y: number },
  catalogId?: CanonicalObjectId,
): { x: number; y: number }[] {
  const definition = catalogId ? canonicalObjectDefinition({ catalogId })! : OBJECT_CATALOG[kind];
  const candidates: { x: number; y: number }[] = [];
  const clamp = (value: number, min: number, max: number) => Math.min(max, Math.max(min, value));
  for (const area of sceneManifestOf(setting).zones.placement) {
    const minX = area.left + definition.width / 2,
      maxX = area.right - definition.width / 2;
    const minY = area.top + definition.depth / 2,
      maxY = area.bottom - definition.depth / 2;
    if (minX > maxX || minY > maxY) continue;
    candidates.push({ x: clamp(desired.x, minX, maxX), y: clamp(desired.y, minY, maxY) });
    for (let y = minY; y <= maxY; y += 8)
      for (let x = minX; x <= maxX; x += 8) candidates.push({ x, y });
  }
  return candidates.sort(
    (a, b) =>
      (a.x - desired.x) ** 2 +
        (a.y - desired.y) ** 2 -
        ((b.x - desired.x) ** 2 + (b.y - desired.y) ** 2) ||
      a.y - b.y ||
      a.x - b.x,
  );
}
/** Finds a new position without moving any existing objects. */
export function findObjectPlacement(
  kind: ObjectKind,
  objects: readonly YardObject[],
  setting: SceneInput,
  desired = { x: WORLD_WIDTH / 2, y: 430 },
  catalogId?: CanonicalObjectId,
): { x: number; y: number } | null {
  objectKindSchema.parse(kind);
  for (const point of placementCandidates(kind, setting, desired, catalogId)) {
    const candidate: YardObject = {
      id: 'placement-candidate',
      kind,
      ...point,
      ...(catalogId ? { catalogId } : {}),
    };
    if (
      isPlacementValid(
        candidate,
        objects.filter((object) => object.id !== 'placement-candidate'),
        setting,
      ) &&
      !objects.some((other) => objectsOverlap(candidate, other))
    )
      return point;
  }
  return null;
}
/** Clamp then search a deterministic nearest grid; identities/kinds and input order are preserved. */
export function reanchorObjects(input: readonly YardObject[], setting: SceneInput): YardObject[] {
  const objects = yardObjectsSchema.parse(input);
  let placed: YardObject[] = objects.filter((object) => isPlacementValid(object, objects, setting));
  const retained = new Set(placed.map((object) => object.id));
  // Larger objects first makes crowded scene switches stable without moving any bird identity.
  const ordered = [...objects].sort(
    (a, b) =>
      objectDefinition(b).width * objectDefinition(b).depth -
        objectDefinition(a).width * objectDefinition(a).depth || a.id.localeCompare(b.id),
  );
  for (const object of ordered) {
    if (retained.has(object.id)) continue;
    const position = findObjectPlacement(object.kind, placed, setting, object, object.catalogId);
    if (!position) {
      placed = [];
      break;
    }
    placed.push({ ...object, ...position });
  }
  // A crowded layout can strand a greedy search. A 7×2 worst-footprint grid fits the 12-object cap.
  if (placed.length !== objects.length) {
    const areas = sceneManifestOf(setting).zones.placement;
    const width = Math.max(...Object.values(OBJECT_CATALOG).map((definition) => definition.width));
    const depth = Math.max(...Object.values(OBJECT_CATALOG).map((definition) => definition.depth));
    const cells: { x: number; y: number }[] = [];
    for (const bounds of areas)
      for (
        let y = bounds.top + depth / 2;
        y <= bounds.bottom - depth / 2;
        y += depth + OBJECT_CLEARANCE
      )
        for (
          let x = bounds.left + width / 2;
          x <= bounds.right - width / 2;
          x += width + OBJECT_CLEARANCE
        )
          cells.push({ x, y });
    for (const object of ordered) {
      cells.sort(
        (a, b) =>
          (a.x - object.x) ** 2 +
            (a.y - object.y) ** 2 -
            ((b.x - object.x) ** 2 + (b.y - object.y) ** 2) ||
          a.y - b.y ||
          a.x - b.x,
      );
      const position = cells.find((point) =>
        isPlacementValid({ ...object, ...point }, placed, setting),
      );
      if (!position) throw new YardValidationError('sceneCapacity');
      placed.push({ ...object, ...position });
    }
  }
  const byId = new Map(placed.map((object) => [object.id, object]));
  return validateObjects(
    objects.map((object) => byId.get(object.id)!),
    setting,
  );
}
