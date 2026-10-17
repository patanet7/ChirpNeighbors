import { z } from 'zod';
import { TEXTURE_REVIEW_LIMITS } from '../workbench/texture-profile';
import type { YardObject } from '../domain/scene';
import type { SceneManifest } from '../scenes/manifest';
import { SCENE_RESOURCE_LIMITS, selectScenePresentation } from './scene-resource-budget';
import {
  reviewTextureAdmission,
  projectReviewTextureFrame,
  YARD_REVIEW_TEXTURE_LIMITS,
  type CheckedYardReviewTexture,
  type YardReviewTexture,
  type ReviewTextureBounds,
} from './review-texture';

/** A local review paint collection; layers confer no object, actor, slot or physical authority. */
export const YARD_REVIEW_TEXTURE_PACK_LIMITS = Object.freeze({
  assets: 6,
  decodedRgbaBytes: TEXTURE_REVIEW_LIMITS.decodedRgbaBytes,
  primitives: 6 * YARD_REVIEW_TEXTURE_LIMITS.primitives,
});
export type YardReviewTextureLayer = 'background' | 'ground' | 'objects' | 'foreground';
export interface YardReviewTexturePack {
  schemaVersion: 1;
  entries: {
    id: string;
    layer: YardReviewTextureLayer;
    texture: YardReviewTexture;
    scale?: number;
  }[];
}
export interface CheckedYardReviewTexturePack {
  readonly schemaVersion: 1;
  readonly entries: readonly Readonly<{
    id: string;
    layer: YardReviewTextureLayer;
    texture: CheckedYardReviewTexture;
    scale: number;
    bounds: Readonly<ReviewTextureBounds>;
  }>[];
  readonly totalDecodedRgbaBytes: number;
  readonly primitiveCount: number;
}
export interface ReviewTexturePackAdmission {
  status: 'absent' | 'accepted' | 'rejected';
  pack: CheckedYardReviewTexturePack | null;
  primitiveCount: number;
  reason: string | null;
}
const packSchema = z
  .object({
    schemaVersion: z.literal(1),
    entries: z
      .array(
        z
          .object({
            id: z
              .string()
              .min(1)
              .max(80)
              .regex(/^[A-Za-z0-9][A-Za-z0-9._-]*$/),
            layer: z.enum(['background', 'ground', 'objects', 'foreground']),
            texture: z.unknown(),
            scale: z.number().finite().min(0.25).max(2).default(1),
          })
          .strict(),
      )
      .min(1)
      .max(YARD_REVIEW_TEXTURE_PACK_LIMITS.assets),
  })
  .strict();
const record = (value: unknown): Record<string, unknown> | null =>
  value !== null && typeof value === 'object' && !Array.isArray(value)
    ? (value as Record<string, unknown>)
    : null;

/** Preflight reads at most six atlas declarations, before walking any package/frame/PNG data. */
function boundedAggregate(
  value: unknown,
): { raw: Record<string, unknown>; entries: unknown[] } | null {
  const raw = record(value),
    inputEntries = raw?.entries;
  if (
    !raw ||
    !Array.isArray(inputEntries) ||
    inputEntries.length < 1 ||
    inputEntries.length > YARD_REVIEW_TEXTURE_PACK_LIMITS.assets
  )
    return null;
  const count = inputEntries.length,
    entries: unknown[] = [];
  let bytes = 0;
  // Index the captured bounded array: a caller-supplied iterator must not control the work bound.
  for (let i = 0; i < count; i++) {
    const item: unknown = inputEntries[i];
    const entry = record(item),
      texture = record(entry?.texture),
      pkg = record(texture?.packageData),
      manifest = record(pkg?.manifest),
      atlas = record(manifest?.atlas),
      width = atlas?.width,
      height = atlas?.height;
    if (
      typeof width !== 'number' ||
      typeof height !== 'number' ||
      !Number.isInteger(width) ||
      !Number.isInteger(height) ||
      width < 1 ||
      height < 1 ||
      width > TEXTURE_REVIEW_LIMITS.atlasEdge ||
      height > TEXTURE_REVIEW_LIMITS.atlasEdge
    )
      return null;
    bytes += width * height * 4;
    if (bytes > YARD_REVIEW_TEXTURE_PACK_LIMITS.decodedRgbaBytes) return null;
    entries.push(item);
  }
  return { raw, entries };
}

/** Structural admission only. Each checked texture STILL requires canonical verification before
 * Image/GPU allocation. The renderer must reserve the complete pack alongside other surfaces/art
 * BEFORE actor admission; one invalid entry rejects the entire pack, never a truncated subset. */
export function reviewTexturePackAdmission(value: unknown): ReviewTexturePackAdmission {
  const reject = (reason: string): ReviewTexturePackAdmission => ({
    status: 'rejected',
    pack: null,
    primitiveCount: 0,
    reason,
  });
  if (value === undefined || value === null)
    return { status: 'absent', pack: null, primitiveCount: 0, reason: null };
  try {
    const bounded = boundedAggregate(value);
    if (!bounded)
      return reject(
        'Yard texture pack must contain one to six assets with at most 4 MiB aggregate decoded atlas RGBA.',
      );
    const parsed = packSchema.parse({ ...bounded.raw, entries: bounded.entries });
    if (new Set(parsed.entries.map((entry) => entry.id)).size !== parsed.entries.length)
      return reject('Yard texture pack entry identities must be unique.');
    const entries: CheckedYardReviewTexturePack['entries'][number][] = [];
    let totalDecodedRgbaBytes = 0;
    for (const entry of parsed.entries) {
      const child = reviewTextureAdmission(entry.texture, entry.scale);
      if (child.status !== 'accepted' || !child.texture)
        return reject(
          `Yard texture entry ${entry.id} rejected: ${child.reason ?? 'An explicit texture is required.'}`,
        );
      const scaleBounds = (bounds: Readonly<ReviewTextureBounds>): ReviewTextureBounds => ({
        left: child.texture!.placement.x + (bounds.left - child.texture!.placement.x) * entry.scale,
        top: child.texture!.placement.y + (bounds.top - child.texture!.placement.y) * entry.scale,
        right:
          child.texture!.placement.x + (bounds.right - child.texture!.placement.x) * entry.scale,
        bottom:
          child.texture!.placement.y + (bounds.bottom - child.texture!.placement.y) * entry.scale,
      });
      for (const frameId of child.texture.idleFrameIds) {
        const bounds = scaleBounds(projectReviewTextureFrame(child.texture, frameId).bounds);
        if (bounds.left < 0 || bounds.top < 0 || bounds.right > 960 || bounds.bottom > 540)
          return reject(
            `Yard texture entry ${entry.id} scaled full canvas must fit inside the 960×540 yard.`,
          );
      }
      const atlas = child.texture.packageData.manifest.atlas;
      totalDecodedRgbaBytes += atlas.width * atlas.height * 4;
      // Recheck the owned, parsed texture so mutable input getters cannot evade the preflight.
      if (totalDecodedRgbaBytes > YARD_REVIEW_TEXTURE_PACK_LIMITS.decodedRgbaBytes)
        return reject('Yard texture pack exceeds 4 MiB aggregate decoded atlas RGBA.');
      // Preserve the exact WeakSet-admitted child identity; cloning it would invalidate hash upload.
      entries.push(
        Object.freeze({
          id: entry.id,
          layer: entry.layer,
          texture: child.texture,
          scale: entry.scale,
          bounds: Object.freeze(scaleBounds(child.texture.bounds)),
        }),
      );
    }
    const primitiveCount = entries.length * YARD_REVIEW_TEXTURE_LIMITS.primitives;
    const pack = Object.freeze({
      schemaVersion: 1 as const,
      entries: Object.freeze(entries),
      totalDecodedRgbaBytes,
      primitiveCount,
    });
    return { status: 'accepted', pack, primitiveCount, reason: null };
  } catch {
    return reject(
      'Yard texture pack must match the strict local review-only entry, layer and texture contracts.',
    );
  }
}

export function yardReviewTexturePackPrimitiveReserve(value: unknown): number {
  return reviewTexturePackAdmission(value).primitiveCount;
}

/** Shared component/renderer gate. Other reservations exclude this pack and include all accepted
 * art/surfaces. Check the complete baseline before actor admission or any asynchronous allocation. */
export function reviewTexturePackSceneAdmission(input: {
  pack?: unknown;
  scene: SceneManifest;
  objects: readonly YardObject[];
  additionalPrimitives: number;
}): ReviewTexturePackAdmission {
  const admission = reviewTexturePackAdmission(input.pack);
  if (admission.status !== 'accepted') return admission;
  const reject = (reason: string): ReviewTexturePackAdmission => ({
    status: 'rejected',
    pack: null,
    primitiveCount: 0,
    reason,
  });
  if (
    !Number.isSafeInteger(input.additionalPrimitives) ||
    input.additionalPrimitives < 0 ||
    input.additionalPrimitives > SCENE_RESOURCE_LIMITS.primitives
  )
    return reject('Invalid complete scene resource reservation for yard texture pack.');
  try {
    const baseline = selectScenePresentation({
      birds: [],
      scene: input.scene,
      objects: input.objects,
      additionalPrimitives: input.additionalPrimitives,
      registry: {
        retain() {},
        resolve() {
          throw new Error('Empty pack admission must not resolve actors.');
        },
      },
    }).stats.basePrimitiveCount;
    if (baseline + admission.primitiveCount > SCENE_RESOURCE_LIMITS.primitives)
      return reject('Whole yard texture pack exceeds the scene primitive budget.');
    return admission;
  } catch {
    return reject(
      'Could not establish a bounded scene primitive reservation for yard texture pack.',
    );
  }
}

