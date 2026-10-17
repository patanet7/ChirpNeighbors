import { z } from 'zod';
import {
  parseTextureReviewManifest,
  textureReviewClientPackageSchema,
  TEXTURE_REVIEW_LIMITS,
  type TextureReviewClientPackage,
} from '../workbench/texture-profile';
import { texturePreviewGeometry, verifyTexturePreviewPackage } from '../workbench/texture-preview';

/** One optional review paint root. These limits add no actor, slot or physical authority. */
export const YARD_REVIEW_TEXTURE_LIMITS = Object.freeze({ assets: 1, primitives: 8 });
export interface YardReviewTexture {
  packageData: TextureReviewClientPackage;
  placement: { x: number; y: number };
  clipId: 'idle';
  showContacts: boolean;
}
export interface ReviewTextureBounds {
  left: number;
  top: number;
  right: number;
  bottom: number;
}
export interface CheckedYardReviewTexture extends Readonly<YardReviewTexture> {
  readonly depthY: number;
  readonly bounds: Readonly<ReviewTextureBounds>;
  readonly contacts: readonly Readonly<{ id: string; x: number; y: number }>[];
  readonly idleFrameIds: readonly string[];
  /** Distinct source-frame RGBA digests, not a fidelity or animation-quality approval. */
  readonly uniqueIdleFrameCount: number;
  readonly animated: boolean;
  readonly canonicalVerification: 'required-before-upload';
}
export interface ReviewTextureAdmission {
  status: 'absent' | 'accepted' | 'rejected';
  reason: string | null;
  texture: CheckedYardReviewTexture | null;
  primitiveCount: number;
}
const wrapper = z
  .object({
    packageData: textureReviewClientPackageSchema,
    placement: z
      .object({ x: z.number().finite().min(0).max(960), y: z.number().finite().min(0).max(540) })
      .strict(),
    clipId: z.literal('idle'),
    showContacts: z.boolean(),
  })
  .strict();
const admitted = new WeakSet<object>();
const record = (value: unknown): Record<string, unknown> | null =>
  value !== null && typeof value === 'object' && !Array.isArray(value)
    ? (value as Record<string, unknown>)
    : null;

/** Reject collection/transport oversize before schema traversal or allocation. */
function withinEnvelope(value: unknown): boolean {
  const raw = record(value),
    pkg = record(raw?.packageData),
    manifest = record(pkg?.manifest),
    receipt = record(pkg?.receipt);
  if (
    !raw ||
    !pkg ||
    !manifest ||
    !receipt ||
    typeof pkg.canonicalPngBase64 !== 'string' ||
    pkg.canonicalPngBase64.length > Math.ceil(TEXTURE_REVIEW_LIMITS.encodedBytes / 3) * 4 ||
    !Array.isArray(manifest.frames) ||
    manifest.frames.length > TEXTURE_REVIEW_LIMITS.frames ||
    !Array.isArray(manifest.clips) ||
    manifest.clips.length > TEXTURE_REVIEW_LIMITS.clips ||
    !Array.isArray(receipt.frameDigests) ||
    receipt.frameDigests.length > TEXTURE_REVIEW_LIMITS.frames
  )
    return false;
  let steps = 0;
  for (const clip of manifest.clips) {
    const entry = record(clip);
    if (
      !entry ||
      !Array.isArray(entry.frames) ||
      entry.frames.length > TEXTURE_REVIEW_LIMITS.sequenceSteps
    )
      return false;
    steps += entry.frames.length;
  }
  if (steps > TEXTURE_REVIEW_LIMITS.sequenceSteps) return false;
  for (const frame of manifest.frames) {
    const entry = record(frame);
    if (!entry || !Array.isArray(entry.contacts) || entry.contacts.length > 4) return false;
  }
  return true;
}
function freezeKnown<T>(value: T): T {
  if (value !== null && typeof value === 'object') {
    for (const item of Object.values(value)) freezeKnown(item);
    Object.freeze(value);
  }
  return value;
}
function project(
  frame: TextureReviewClientPackage['manifest']['frames'][number],
  placement: YardReviewTexture['placement'],
) {
  const geometry = texturePreviewGeometry(frame);
  return {
    sourceRect: { ...frame.sourceRect },
    canvas: { ...frame.canvas },
    trim: { ...frame.trim },
    pivot: { ...frame.pivot },
    sourceScale: geometry.sourceScale,
    bounds: {
      left: placement.x + geometry.bounds.left,
      top: placement.y + geometry.bounds.top,
      right: placement.x + geometry.bounds.right,
      bottom: placement.y + geometry.bounds.bottom,
    },
    contacts: geometry.contacts.map((point) => ({
      id: point.id,
      x: placement.x + point.x,
      y: placement.y + point.y,
    })),
    depthY: placement.y,
  };
}

/** Structural admission only; canonical verification is mandatory before Image/GPU allocation.
 * paintScale affects only the world-fit check about placement. Checked source geometry stays
 * unscaled, so a renderer must apply the same paint scale to its root container. */
export function reviewTextureAdmission(value: unknown, paintScale = 1): ReviewTextureAdmission {
  const reject = (reason: string): ReviewTextureAdmission => ({
    status: 'rejected',
    reason,
    texture: null,
    primitiveCount: 0,
  });
  if (!Number.isFinite(paintScale) || paintScale < 0.25 || paintScale > 2)
    return reject('Local texture paint scale must be finite and between 0.25 and 2.');
  if (value === undefined || value === null)
    return { status: 'absent', reason: null, texture: null, primitiveCount: 0 };
  let parsed: YardReviewTexture;
  try {
    if (!withinEnvelope(value))
      return reject(
        'Yard texture exceeds or does not match the single-asset bounded texture envelope.',
      );
    parsed = wrapper.parse(value);
    parseTextureReviewManifest(parsed.packageData.manifest);
  } catch {
    return reject(
      'Yard texture must match the strict unapproved RGBA profile, idle-only placement and contact-overlay contract.',
    );
  }
  const manifest = parsed.packageData.manifest,
    clip = manifest.clips.find((entry) => entry.id === 'idle');
  if (!clip) return reject('Yard texture requires an explicit idle clip; no fallback is invented.');
  const frameIds = [...new Set(clip.frames.map((entry) => entry.frameId))];
  const first = manifest.frames.find((frame) => frame.id === frameIds[0])!;
  const registration = (frame: typeof first) =>
    JSON.stringify([
      frame.canvas,
      frame.world,
      frame.sourcePixelsPerWorldUnit,
      frame.pivot,
      [...frame.contacts]
        .sort((a, b) => a.id.localeCompare(b.id))
        .map(({ id, x, y }) => ({ id, x, y })),
    ]);
  const reference = registration(first);
  for (const id of frameIds) {
    const frame = manifest.frames.find((entry) => entry.id === id)!;
    if (registration(frame) !== reference)
      return reject(
        'Idle frames must retain the same canvas, world size, density, pivot and declared contact registration.',
      );
    const { bounds } = project(frame, parsed.placement);
    const x = parsed.placement.x,
      y = parsed.placement.y;
    if (
      x + (bounds.left - x) * paintScale < 0 ||
      y + (bounds.top - y) * paintScale < 0 ||
      x + (bounds.right - x) * paintScale > 960 ||
      y + (bounds.bottom - y) * paintScale > 540
    )
      return reject('The full projected idle canvas must fit inside the 960×540 yard.');
  }
  const uniqueIdleFrameCount = new Set(
    frameIds.map(
      (id) => parsed.packageData.receipt.frameDigests.find((entry) => entry.id === id)!.rgbaSha256,
    ),
  ).size;
  const projected = project(first, parsed.placement);
  const texture = freezeKnown({
    ...parsed,
    depthY: parsed.placement.y,
    bounds: projected.bounds,
    contacts: projected.contacts,
    idleFrameIds: frameIds,
    uniqueIdleFrameCount,
    animated: uniqueIdleFrameCount > 1,
    canonicalVerification: 'required-before-upload' as const,
  });
  admitted.add(texture);
  return {
    status: 'accepted',
    reason: null,
    texture,
    primitiveCount: YARD_REVIEW_TEXTURE_LIMITS.primitives,
  };
}

/** Conservative reserve remains until the caller explicitly clears a rejected asynchronous upload. */
export function yardReviewTexturePrimitiveReserve(value: unknown): number {
  return reviewTextureAdmission(value).primitiveCount;
}
export function projectReviewTextureFrame(texture: CheckedYardReviewTexture, frameId: string) {
  if (!admitted.has(texture) || !texture.idleFrameIds.includes(frameId))
    throw new Error('Only an admitted selected idle frame can be projected.');
  return project(
    texture.packageData.manifest.frames.find((frame) => frame.id === frameId)!,
    texture.placement,
  );
}
/** Hash integrity is not a rights, fidelity, alpha-contact or physical-geometry approval. */
export async function verifyYardReviewTexture(
  texture: CheckedYardReviewTexture,
  signal?: AbortSignal,
) {
  if (!admitted.has(texture)) throw new Error('Yard texture was not structurally admitted.');
  const verified = await verifyTexturePreviewPackage(texture.packageData, signal);
  return { packageData: texture.packageData, bytes: verified.bytes };
}

