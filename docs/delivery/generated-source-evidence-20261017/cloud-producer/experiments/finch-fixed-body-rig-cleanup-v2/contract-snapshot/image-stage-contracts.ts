import { z } from 'zod';
import { taxonomyIdentitySchema } from './manifest-v3.ts';

const id = z
  .string()
  .min(1)
  .max(160)
  .regex(/^[a-zA-Z0-9][a-zA-Z0-9._:@-]*$/);
const sha256 = z.string().regex(/^[a-f0-9]{64}$/);
const text = z
  .string()
  .min(1)
  .max(2000)
  .refine((value) => value === value.trim(), 'Reference metadata must already be normalized')
  .refine(
    (value) =>
      [...value].every(
        (character) =>
          character >= ' ' && character !== '\u007f' && character !== '<' && character !== '>',
      ),
    'Reference metadata must be plain text',
  );
const https = z
  .string()
  .max(2048)
  // Portable ASCII HTTPS identifiers (percent-encode other characters); no optional URI codec.
  // The URL parser below remains the authoritative host/credential check.
  .regex(/^https:\/\/[!-~]+(?![\s\S])/)
  .refine((value) => {
    try {
      const url = new URL(value);
      return url.protocol === 'https:' && !url.username && !url.password;
    } catch {
      return false;
    }
  }, 'Only credential-free HTTPS source identifiers are allowed');
const pointInTime = z.string().datetime();
const review = z.object({ reviewerId: id, evidenceId: id, reviewedAt: pointInTime }).strict();

/** Local evidence, not a fetch request, automatic rights clearance, or runnable adapter. */
export const localReferenceSchema = z
  .object({
    schemaVersion: z.literal(1),
    id,
    fixture: z.boolean(),
    source: z
      .object({
        kind: z.enum(['local-file', 'archive-file', 'technical-fixture']),
        fileIdentity: text,
        originalUrl: https.nullable(),
        descriptionPageUrl: https.nullable(),
        author: text,
        uploader: text.nullable(),
        attribution: text,
        description: text.nullable(),
        sourceTimestamp: pointInTime.nullable(),
        remoteHash: z
          .object({
            algorithm: z.enum(['sha1', 'sha256']),
            value: z.string().regex(/^[a-f0-9]{40}([a-f0-9]{24})?$/),
          })
          .strict()
          .nullable(),
      })
      .strict(),
    original: z
      .object({
        bytes: z.number().int().min(1).max(16_777_216),
        sha256,
        mime: z.enum(['image/png', 'image/jpeg', 'application/x-chirp-rgba8']),
      })
      .strict(),
    decoded: z
      .object({
        format: z.literal('rgba8-straight'),
        width: z.number().int().min(1).max(256),
        height: z.number().int().min(1).max(256),
        sha256,
        decoder: z.object({ id, version: id }).strict(),
        derivation: z.enum(['raw-identity', 'declared-unverified']),
      })
      .strict(),
    rights: z
      .object({
        licenseId: id,
        licenseVersion: id,
        licenseUrl: https.nullable(),
        status: z.enum(['pending', 'approved', 'denied', 'conflicting']),
        restrictions: z.array(text).max(16),
        referenceUseAllowed: z.boolean(),
        derivativesAllowed: z.boolean(),
        redistributionAllowed: z.boolean(),
        generationPermission: z.enum(['not-reviewed', 'allowed', 'denied']),
        review: review.nullable(),
      })
      .strict(),
    taxonomy: z
      .object({
        application: taxonomyIdentitySchema,
        declaredScientificName: text,
        aliases: z
          .array(
            z.object({ authority: id, version: id, taxonId: id, scientificName: text }).strict(),
          )
          .max(16),
        externalEvidence: z
          .array(
            z
              .object({
                authority: id,
                version: id,
                entityId: id,
                statement: z.enum(['scientific-name', 'rank', 'parent-taxon', 'image', 'depicts']),
                value: text,
                status: z.literal('candidate-evidence'),
              })
              .strict(),
          )
          .max(32),
        review: review.nullable(),
      })
      .strict(),
    annotations: z
      .object({
        sex: z.enum(['female', 'male', 'unknown']),
        age: z.enum(['juvenile', 'adult', 'unknown']),
        plumage: text.nullable(),
        viewpoint: z.enum([
          'left',
          'right',
          'front',
          'back',
          'above',
          'below',
          'oblique',
          'unknown',
        ]),
      })
      .strict(),
  })
  .strict()
  .superRefine((value, context) => {
    const fail = (message: string) => context.addIssue({ code: 'custom', message });
    if ((value.source.kind === 'technical-fixture') !== value.fixture)
      fail('Technical fixture status must match source kind.');
    if (
      value.source.kind === 'archive-file' &&
      (!value.source.originalUrl || !value.source.descriptionPageUrl)
    )
      fail('Archive files require original and description-page identifiers.');
    const remote = value.source.remoteHash;
    if (remote && remote.value.length !== (remote.algorithm === 'sha1' ? 40 : 64))
      fail('Remote hash length does not match its algorithm.');
    const aliases = value.taxonomy.aliases.map(
      (alias) => `${alias.authority}/${alias.version}/${alias.taxonId}`,
    );
    if (new Set(aliases).size !== aliases.length) fail('Taxonomy alias pins must be unique.');
    if (value.fixture && value.taxonomy.review !== null)
      fail('A technical fixture cannot claim reviewed species fidelity.');
    if (
      (value.original.mime === 'application/x-chirp-rgba8') !==
      (value.decoded.derivation === 'raw-identity')
    )
      fail(
        'Encoded photo decoding remains an unverified declaration until an adapter is implemented.',
      );
  });

export const referencePolicySchema = z
  .object({
    schemaVersion: z.literal(1),
    id,
    version: id,
    use: z.enum(['reference-only', 'derived-sprite']),
    allowedLicenses: z.array(z.object({ id, version: id, url: https.nullable() }).strict()).max(32),
    allowTechnicalFixtures: z.boolean(),
  })
  .strict();

export type LocalReference = z.infer<typeof localReferenceSchema>;

const byte = z.number().int().min(0).max(255);
const channel = z.array(byte).min(1).max(65_536);
const coordinates = z
  .object({ x: z.number().int().min(0).max(256), y: z.number().int().min(0).max(256) })
  .strict();
const contact = coordinates
  .extend({ kind: z.enum(['left-foot', 'right-foot', 'ground', 'perch']) })
  .strict();
const stageIdentity = z.object({ id, version: id }).strict();

/** A segmentation value is never an alpha matte. Float hashes use little-endian float32 bytes. */
export const segmentationStageSchema = z.discriminatedUnion('encoding', [
  z
    .object({
      encoding: z.literal('binary-mask-u8'),
      values: z
        .array(z.union([z.literal(0), z.literal(255)]))
        .min(1)
        .max(65_536),
      sha256,
      adapter: stageIdentity,
    })
    .strict(),
  z
    .object({
      encoding: z.literal('logits-f32-le'),
      values: z.array(z.number().finite().min(-1_000_000).max(1_000_000)).min(1).max(65_536),
      sha256,
      adapter: stageIdentity,
    })
    .strict(),
]);
export const matteStageSchema = z
  .object({
    encoding: z.literal('alpha-u8'),
    alpha: channel,
    sha256,
    origin: z.enum(['supplied-matte', 'technical-fixture']),
    adapter: stageIdentity,
  })
  .strict();
export const foregroundStageSchema = z
  .object({
    encoding: z.literal('rgb8'),
    rgb: z
      .array(byte)
      .min(3)
      .max(65_536 * 3),
    sha256,
    alphaMode: z.enum(['straight', 'premultiplied']),
    recovery: z.enum(['supplied-recovered', 'technical-fixture']),
    adapter: stageIdentity,
  })
  .strict();
const imageFrameSchema = z
  .object({
    id,
    timestampUs: z.number().int().min(0).max(Number.MAX_SAFE_INTEGER),
    durationUs: z.number().int().min(1).max(60_000_000),
    sourceRgba: z
      .array(byte)
      .min(4)
      .max(65_536 * 4),
    sourceSha256: sha256,
    anchor: coordinates,
    contacts: z.array(contact).max(4),
    segmentation: segmentationStageSchema.nullable(),
    matte: matteStageSchema,
    foreground: foregroundStageSchema,
  })
  .strict();
export const imageStageSequenceSchema = z
  .object({
    schemaVersion: z.literal(1),
    fixture: z.boolean(),
    canvas: z
      .object({ width: z.number().int().min(1).max(256), height: z.number().int().min(1).max(256) })
      .strict(),
    frames: z.array(imageFrameSchema).min(1).max(64),
    loop: z.boolean(),
    // These are audit identities, not URLs, invocation settings, or an execution capability.
    referenceIds: z.array(id).min(1).max(16),
    modelSlot: z.literal('unconfigured'),
  })
  .strict()
  .superRefine((sequence, context) => {
    const fail = (message: string) => context.addIssue({ code: 'custom', message });
    const { width, height } = sequence.canvas,
      pixels = width * height;
    if (pixels * sequence.frames.length > 65_536)
      fail('Image sequence exceeds decoded pixel budget.');
    if (new Set(sequence.referenceIds).size !== sequence.referenceIds.length)
      fail('Reference IDs must be unique.');
    if (new Set(sequence.frames.map((frame) => frame.id)).size !== sequence.frames.length)
      fail('Frame IDs must be unique.');
    for (const [index, frame] of sequence.frames.entries()) {
      if (
        frame.sourceRgba.length !== pixels * 4 ||
        frame.matte.alpha.length !== pixels ||
        frame.foreground.rgb.length !== pixels * 3 ||
        (frame.segmentation && frame.segmentation.values.length !== pixels)
      )
        fail('Every image stage must exactly match canvas dimensions.');
      if (
        frame.anchor.x > width ||
        frame.anchor.y > height ||
        frame.contacts.some((point) => point.x > width || point.y > height)
      )
        fail('Frame anchor/contact is outside its canvas.');
      if (new Set(frame.contacts.map((point) => point.kind)).size !== frame.contacts.length)
        fail('Contact kinds must be unique.');
      if (!Number.isSafeInteger(frame.timestampUs + frame.durationUs))
        fail('Frame end timestamp exceeds safe integer range.');
      const previous = sequence.frames[index - 1];
      if (previous && frame.timestampUs !== previous.timestampUs + previous.durationUs)
        fail('Frame timestamps must preserve contiguous original durations/order.');
      if (
        sequence.fixture !== (frame.matte.origin === 'technical-fixture') ||
        sequence.fixture !== (frame.foreground.recovery === 'technical-fixture')
      )
        fail('Fixture stages cannot claim recovered photographic foreground.');
    }
  });

/** Explicit thresholds are mechanical review policy, never biological or visual approval. */
export const imageQaPolicySchema = z
  .object({
    schemaVersion: z.literal(1),
    id,
    version: id,
    edgeAlphaThreshold: byte.min(1),
    maxChangedEdgeFraction: z.number().min(0).max(1),
    maxContactDriftPixels: z.number().min(0).max(512),
    allowContactSetChange: z.boolean(),
  })
  .strict();

export const losslessPixelPolicySchema = z
  .object({
    schemaVersion: z.literal(1),
    id,
    version: id,
    alpha: z.literal('binary-required'),
    palette: z.literal('preserve'),
    logicalPixelSize: z.number().int().min(1).max(16),
    paletteLimit: z.number().int().min(1).max(64),
    crop: z.literal('stable-union-including-anchors'),
  })
  .strict();

export type ImageStageSequence = z.infer<typeof imageStageSequenceSchema>;
export type ImageStageFrame = ImageStageSequence['frames'][number];
export type LosslessPixelPolicy = z.infer<typeof losslessPixelPolicySchema>;
