import { z } from 'zod';

export const animationStates = [
  'idle',
  'moving',
  'perching',
  'singing',
  'feeding',
  'bathing',
  'sleeping',
  'playing',
  'nesting',
] as const;
export type AnimationState = (typeof animationStates)[number];
const identifier = z.string().min(1).max(160);
const integer = z.number().int().nonnegative();
export const animationPinSchema = z
  .object({
    jobId: identifier,
    artifactId: identifier,
    version: z.number().int().positive().max(Number.MAX_SAFE_INTEGER),
    contentDigest: z.string().regex(/^[a-f0-9]{64}$/),
  })
  .strict();
export type AnimationPin = z.infer<typeof animationPinSchema>;
const rectangle = z
  .object({
    x: integer,
    y: integer,
    width: z.number().int().min(1).max(256),
    height: z.number().int().min(1).max(256),
    color: z.number().int().min(0).max(0xffffff),
  })
  .strict();
const clip = z
  .object({
    frames: z.array(integer).min(1).max(256),
    ticksPerFrame: z.number().int().min(1).max(300),
    loop: z.boolean(),
    /** Optional authored pose transform, also frozen to the first pose in quiet mode. */
    rotations: z.array(z.number().min(-0.5).max(0.5)).max(256).optional(),
  })
  .strict();
export const speciesManifestV2Schema = z
  .object({
    schemaVersion: z.literal(2),
    speciesId: identifier,
    representation: z.string().min(1).max(200),
    fixture: z.boolean(),
    taxonFidelityReviewed: z.boolean(),
    format: z.literal('pixel-rects'),
    canvas: z
      .object({
        width: z.number().int().min(1).max(256),
        height: z.number().int().min(1).max(256),
        anchorX: integer,
        anchorY: integer,
      })
      .strict(),
    frames: z.array(z.array(rectangle).min(1).max(4096)).min(1).max(64),
    clips: z
      .object(
        Object.fromEntries(
          animationStates.map((state) => [state, state === 'idle' ? clip : clip.optional()]),
        ) as { idle: typeof clip } & Record<
          Exclude<AnimationState, 'idle'>,
          z.ZodOptional<typeof clip>
        >,
      )
      .strict(),
    provenance: z
      .object({
        source: z.enum(['deterministic_fixture', 'provider', 'user_upload']),
        creator: identifier,
        sourceVersion: identifier,
        references: z.array(identifier).max(32),
        license: z.string().min(1).max(200),
        usage: z.enum(['development-only', 'cleared']),
        attribution: z.string().min(1).max(300),
      })
      .strict(),
  })
  .strict()
  .superRefine((value, context) => {
    const fail = (message: string) => context.addIssue({ code: 'custom', message });
    if (value.canvas.anchorX > value.canvas.width || value.canvas.anchorY > value.canvas.height)
      fail('Anchor exceeds canvas bounds');
    if (value.frames.reduce((sum, frame) => sum + frame.length, 0) > 16384)
      fail('Manifest exceeds total rectangle budget');
    if (
      value.frames.some((frame) =>
        frame.some(
          (rect) =>
            rect.x + rect.width > value.canvas.width || rect.y + rect.height > value.canvas.height,
        ),
      )
    )
      fail('Frame exceeds canvas bounds');
    for (const entry of Object.values(value.clips)) {
      if (!entry) continue;
      if (entry.frames.some((index) => index >= value.frames.length))
        fail('Clip frame index exceeds frame count');
      if (entry.rotations && entry.rotations.length !== entry.frames.length)
        fail('Clip pose count must match frames');
    }
    if (
      value.fixture &&
      (value.taxonFidelityReviewed ||
        value.provenance.source !== 'deterministic_fixture' ||
        value.provenance.usage !== 'development-only')
    )
      fail('Fixture cannot claim fidelity review or cleared production usage');
    if (
      !value.fixture &&
      (!value.taxonFidelityReviewed ||
        value.provenance.source === 'deterministic_fixture' ||
        value.provenance.usage !== 'cleared')
    )
      fail('Non-fixture art requires fidelity review and cleared usage');
  });
export type SpeciesManifestV2 = z.infer<typeof speciesManifestV2Schema>;
export type PixelRectangle = SpeciesManifestV2['frames'][number][number];
