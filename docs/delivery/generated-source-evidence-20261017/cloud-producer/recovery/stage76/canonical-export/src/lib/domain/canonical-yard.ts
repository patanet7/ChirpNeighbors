import { z } from 'zod';
import data from './canonical-yard-data.json' with { type: 'json' };
import type { ObjectDefinition, ObjectKind, YardObject } from './scene';

export const CANONICAL_YARD_SOURCE_COMMIT = 'd4697d34772824d1bb86aa19f0ba8e1b057d7238';
export const canonicalObjectIdSchema = z.enum([
  'california_bush_sunflower',
  'san_diego_monkeyflower',
  'blue_eyed_grass',
  'crassula_ovata',
  'hollyleaf_cherry',
  'torrey_pine',
  'cedar_feeder',
  'platform_feeder',
  'bench',
  'pedestal_birdbath',
  'cedar_fence',
]);
export type CanonicalObjectId = z.infer<typeof canonicalObjectIdSchema>;
export interface CanonicalYardEntry {
  id: CanonicalObjectId;
  assetId: string;
  variantId: string;
  label: string;
  kind: ObjectKind;
  sourcePath: string;
  sourceSha256: string;
  sourceWidth: number;
  sourceHeight: number;
  width: number;
  height: number;
  pivot: { x: number; y: number };
  footprint: { width: number; depth: number };
  slots: ObjectDefinition['slots'];
  note: string;
}
/** Exact source identities plus authored runtime geometry. This is private candidate admission,
 * not source rights/owner acceptance. Inventory remains the existing five owned categories. */
export const CANONICAL_YARD_OBJECTS = data as readonly CanonicalYardEntry[];
export function canonicalYardEntry(id: CanonicalObjectId): CanonicalYardEntry {
  const entry = CANONICAL_YARD_OBJECTS.find((item) => item.id === id);
  if (!entry) throw new Error('Unknown canonical yard object.');
  return entry;
}
export const SAN_DIEGO_OBJECT_DEFAULTS: Partial<Record<ObjectKind, CanonicalObjectId>> = {
  plant: 'california_bush_sunflower',
  feeder: 'cedar_feeder',
  perch: 'bench',
  bath: 'pedestal_birdbath',
};
export function canonicalObjectDefinition(
  object: Pick<YardObject, 'catalogId'>,
): ObjectDefinition | null {
  if (!object.catalogId) return null;
  const entry = canonicalYardEntry(object.catalogId);
  return { label: entry.label, ...entry.footprint, height: entry.pivot.y, slots: entry.slots };
}
