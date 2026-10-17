import { z } from 'zod';
import { animationStates } from '../assets/manifest-v2';

/** Experimental, opt-in review envelope. This does not alter any published asset profile. */
export const TEXTURE_REVIEW_PROFILE = 'chirp-texture-review-v1' as const;
export const TEXTURE_REVIEW_LIMITS = Object.freeze({
  encodedBytes: 4_194_304,
  atlasEdge: 1_024,
  atlasPixels: 1_048_576,
  decodedRgbaBytes: 4_194_304,
  frameEdge: 512,
  frames: 64,
  clips: 16,
  sequenceSteps: 256,
  manifestBytes: 65_536,
  pngChunks: 1_024,
  metadataBytes: 16_384,
  concurrentDecodes: 1,
  decodeSeconds: 2,
});
const id = z
  .string()
  .min(1)
  .max(80)
  .regex(/^[a-zA-Z0-9][a-zA-Z0-9._-]*$/);
const coordinate = z.number().int().min(0).max(TEXTURE_REVIEW_LIMITS.atlasEdge);
const point = z.object({ x: coordinate, y: coordinate }).strict();
const frame = z
  .object({
    id,
    sourceRect: z
      .object({
        x: coordinate,
        y: coordinate,
        width: z.number().int().positive().max(512),
        height: z.number().int().positive().max(512),
      })
      .strict(),
    canvas: z
      .object({
        width: z.number().int().positive().max(512),
        height: z.number().int().positive().max(512),
      })
      .strict(),
    trim: point,
    pivot: point,
    contacts: z.array(point.extend({ id }).strict()).min(1).max(4),
    world: z
      .object({ width: z.number().positive().max(2_048), height: z.number().positive().max(2_048) })
      .strict(),
    sourcePixelsPerWorldUnit: z.number().min(0.25).max(8),
  })
  .strict();
export const textureReviewManifestSchema = z
  .object({
    schemaVersion: z.literal(1),
    profile: z.literal(TEXTURE_REVIEW_PROFILE),
    scope: z.literal('review-only'),
    approval: z.literal('unreviewed'),
    activation: z.literal('none'),
    source: z
      .object({
        sha256: z.string().regex(/^[a-f0-9]{64}$/),
        creator: z.string().min(1).max(160),
        tool: z.string().min(1).max(160),
        toolVersion: z.string().min(1).max(80),
        rights: z.literal('unreviewed'),
        fidelity: z.literal('unreviewed'),
      })
      .strict(),
    atlas: z
      .object({
        width: z.number().int().positive().max(TEXTURE_REVIEW_LIMITS.atlasEdge),
        height: z.number().int().positive().max(TEXTURE_REVIEW_LIMITS.atlasEdge),
        alpha: z.literal('straight-rgba8'),
        colorSpace: z.literal('srgb'),
      })
      .strict(),
    frames: z.array(frame).min(1).max(TEXTURE_REVIEW_LIMITS.frames),
    clips: z
      .array(
        z
          .object({
            id: z.enum(animationStates),
            tickRate: z.literal(30),
            loop: z.boolean(),
            frames: z
              .array(
                z.object({ frameId: id, durationTicks: z.number().int().min(1).max(300) }).strict(),
              )
              .min(1)
              .max(TEXTURE_REVIEW_LIMITS.sequenceSteps),
          })
          .strict(),
      )
      .min(1)
      .max(TEXTURE_REVIEW_LIMITS.clips),
  })
  .strict()
  .superRefine((value, context) => {
    const fail = (message: string) => context.addIssue({ code: 'custom', message });
    if (value.atlas.width * value.atlas.height > TEXTURE_REVIEW_LIMITS.atlasPixels)
      fail('Atlas pixel budget exceeded.');
    if (
      new Set(value.frames.map((entry) => entry.id)).size !== value.frames.length ||
      new Set(value.clips.map((entry) => entry.id)).size !== value.clips.length
    )
      fail('Frame and clip identifiers must be unique.');
    const ids = new Set(value.frames.map((entry) => entry.id));
    let steps = 0;
    for (const clip of value.clips) {
      steps += clip.frames.length;
      if (clip.frames.some((entry) => !ids.has(entry.frameId)))
        fail('Clip references an absent frame.');
    }
    if (steps > TEXTURE_REVIEW_LIMITS.sequenceSteps) fail('Total sequence-step budget exceeded.');
    for (const entry of value.frames) {
      const r = entry.sourceRect;
      if (r.x + r.width > value.atlas.width || r.y + r.height > value.atlas.height)
        fail('Frame source rectangle exceeds atlas bounds.');
      if (
        entry.trim.x + r.width > entry.canvas.width ||
        entry.trim.y + r.height > entry.canvas.height
      )
        fail('Trimmed source exceeds untrimmed canvas.');
      if (entry.pivot.x > entry.canvas.width || entry.pivot.y > entry.canvas.height)
        fail('Pivot exceeds canvas bounds.');
      if (new Set(entry.contacts.map((contact) => contact.id)).size !== entry.contacts.length)
        fail('Contact identifiers must be unique.');
      for (const contact of entry.contacts)
        if (
          contact.x < entry.trim.x ||
          contact.y < entry.trim.y ||
          contact.x >= entry.trim.x + r.width ||
          contact.y >= entry.trim.y + r.height
        )
          fail('Contact must address a pixel in the trimmed source.');
      if (
        Math.abs(entry.world.width * entry.sourcePixelsPerWorldUnit - entry.canvas.width) > 1e-8 ||
        Math.abs(entry.world.height * entry.sourcePixelsPerWorldUnit - entry.canvas.height) > 1e-8
      )
        fail('Source density must match the untrimmed world canvas.');
    }
    for (let a = 0; a < value.frames.length; a++)
      for (let b = a + 1; b < value.frames.length; b++) {
        const x = value.frames[a]!.sourceRect,
          y = value.frames[b]!.sourceRect;
        if (
          x.x < y.x + y.width &&
          x.x + x.width > y.x &&
          x.y < y.y + y.height &&
          x.y + x.height > y.y
        )
          fail('Unique frame source rectangles must not overlap; reuse frame IDs in clips.');
      }
  });
export type TextureReviewManifest = z.infer<typeof textureReviewManifestSchema>;
export type TextureReviewFrame = TextureReviewManifest['frames'][number];
export function parseTextureReviewManifest(value: unknown): TextureReviewManifest {
  const encoded = JSON.stringify(value);
  if (!encoded || new TextEncoder().encode(encoded).length > TEXTURE_REVIEW_LIMITS.manifestBytes)
    throw new z.ZodError([
      { code: 'custom', path: [], message: 'Texture manifest exceeds its byte budget.' },
    ]);
  return textureReviewManifestSchema.parse(value);
}
/** Playback lookup only. Does not create a bird state or run an animation loop. */
export function textureReviewFrameAt(
  manifest: TextureReviewManifest,
  clipId: string,
  elapsedMs: number,
): TextureReviewFrame {
  const clip = manifest.clips.find((entry) => entry.id === clipId);
  if (!clip || !Number.isFinite(elapsedMs) || elapsedMs < 0)
    throw new Error('Invalid texture clip playback request.');
  const total = clip.frames.reduce((sum, entry) => sum + entry.durationTicks, 0);
  const raw = Math.floor((elapsedMs / 1_000) * clip.tickRate);
  let tick = clip.loop ? raw % total : Math.min(raw, total - 1);
  for (const entry of clip.frames) {
    if (tick < entry.durationTicks)
      return manifest.frames.find((candidate) => candidate.id === entry.frameId)!;
    tick -= entry.durationTicks;
  }
  throw new Error('Texture clip has no playable frame.');
}

const digestSchema = z.string().regex(/^[a-f0-9]{64}$/);
const imageIdentity = z
  .object({
    sha256: digestSchema,
    bytes: z.number().int().min(1).max(TEXTURE_REVIEW_LIMITS.encodedBytes),
  })
  .strict();
const pixelCount = z.number().int().min(0).max(TEXTURE_REVIEW_LIMITS.atlasPixels);
export const textureReviewReceiptSchema = z
  .object({
    profile: z.literal(TEXTURE_REVIEW_PROFILE),
    activation: z.literal('none'),
    approved: z.literal(false),
    original: imageIdentity,
    canonical: imageIdentity
      .extend({
        rgbaSha256: digestSchema,
        width: z.number().int().min(1).max(TEXTURE_REVIEW_LIMITS.atlasEdge),
        height: z.number().int().min(1).max(TEXTURE_REVIEW_LIMITS.atlasEdge),
      })
      .strict(),
    alpha: z.literal('straight-rgba8'),
    normalization: z.literal('zero-hidden-rgb-only-v1'),
    contactRule: z.literal('alpha-greater-than-zero-only-not-physical-review'),
    metrics: z
      .object({
        partialAlphaPixels: pixelCount,
        transparentPixels: pixelCount,
        hiddenRgbPixelsZeroed: pixelCount,
        visibleRgbColors: pixelCount,
        frames: z.number().int().min(1).max(64),
        uniqueSourceFramePixels: z.number().int().min(1).max(64),
        knownDecodedRgbaBytes: z
          .number()
          .int()
          .positive()
          .max(TEXTURE_REVIEW_LIMITS.decodedRgbaBytes),
        knownSanitizedPngBytes: z.number().int().positive().max(TEXTURE_REVIEW_LIMITS.encodedBytes),
        pngChunks: z.number().int().min(3).max(TEXTURE_REVIEW_LIMITS.pngChunks),
        knownCanonicalPngBytes: z.number().int().positive().max(TEXTURE_REVIEW_LIMITS.encodedBytes),
      })
      .strict(),
    frameDigests: z
      .array(z.object({ id, rgbaSha256: digestSchema }).strict())
      .min(1)
      .max(64),
    decoder: z
      .object({
        id: z.literal('sharp'),
        version: z.string().min(1).max(40),
        libvips: z.string().min(1).max(40),
      })
      .strict(),
    timings: z
      .object({
        scope: z.literal('cpu-wall-time-not-gpu-or-peak-memory'),
        decodeMs: z.number().finite().nonnegative(),
        validationMs: z.number().finite().nonnegative(),
        encodeMs: z.number().finite().nonnegative(),
        totalMs: z.number().finite().nonnegative(),
      })
      .strict(),
  })
  .strict();
export const textureReviewClientPackageSchema = z
  .object({
    manifest: textureReviewManifestSchema,
    receipt: textureReviewReceiptSchema,
    canonicalPngBase64: z
      .string()
      .min(4)
      .max(Math.ceil(TEXTURE_REVIEW_LIMITS.encodedBytes / 3) * 4)
      .regex(/^[A-Za-z0-9+/]*={0,2}$/),
  })
  .strict()
  .superRefine((value, context) => {
    const { manifest, receipt, canonicalPngBase64: encoded } = value;
    const fail = (message: string) => context.addIssue({ code: 'custom', message });
    const padding = encoded.endsWith('==') ? 2 : encoded.endsWith('=') ? 1 : 0;
    if (encoded.length % 4 !== 0 || (encoded.length / 4) * 3 - padding !== receipt.canonical.bytes)
      fail('Canonical PNG transport length mismatch.');
    if (
      receipt.original.sha256 !== manifest.source.sha256 ||
      receipt.canonical.width !== manifest.atlas.width ||
      receipt.canonical.height !== manifest.atlas.height
    )
      fail('Texture package provenance or atlas identity mismatch.');
    if (
      receipt.metrics.frames !== manifest.frames.length ||
      receipt.frameDigests.length !== manifest.frames.length ||
      receipt.frameDigests.some((frame, index) => frame.id !== manifest.frames[index]?.id)
    )
      fail('Texture package frame identities mismatch.');
    if (
      receipt.metrics.knownDecodedRgbaBytes !== manifest.atlas.width * manifest.atlas.height * 4 ||
      receipt.metrics.knownCanonicalPngBytes !== receipt.canonical.bytes ||
      receipt.metrics.partialAlphaPixels + receipt.metrics.transparentPixels >
        manifest.atlas.width * manifest.atlas.height ||
      receipt.metrics.hiddenRgbPixelsZeroed > receipt.metrics.transparentPixels
    )
      fail('Texture package allocation or alpha accounting mismatch.');
    if (
      receipt.metrics.uniqueSourceFramePixels !==
      new Set(receipt.frameDigests.map((frame) => frame.rgbaSha256)).size
    )
      fail('Texture package frame uniqueness mismatch.');
  });
export type TextureReviewClientPackage = z.infer<typeof textureReviewClientPackageSchema>;
export type TextureReviewReceipt = z.infer<typeof textureReviewReceiptSchema>;

