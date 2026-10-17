import { z } from 'zod';
import {
  TEXTURE_REVIEW_LIMITS,
  textureReviewClientPackageSchema,
  type TextureReviewClientPackage,
} from './texture-profile';
import { verifyTexturePreviewPackage } from './texture-preview';

export const TEXTURE_REVIEW_EXPORT_LIMITS = Object.freeze({
  bytes: Math.ceil(TEXTURE_REVIEW_LIMITS.encodedBytes / 3) * 8 + 131_072,
  references: 8,
  depth: 32,
  nodes: 20_000,
});
const digest = z.string().regex(/^[a-f0-9]{64}$/);
const reference = z
  .object({
    libraryFileId: z.string().regex(/^libfile_[a-f0-9]{32}$/),
    version: z.string().regex(/^(0|[1-9][0-9]{0,19})$/),
    sha256: digest,
    relationship: z.enum(['original-input', 'reference-declaration-only']),
  })
  .strict();
export type TextureReviewExportReference = z.infer<typeof reference>;
const base64 = z
  .string()
  .min(4)
  .max(Math.ceil(TEXTURE_REVIEW_LIMITS.encodedBytes / 3) * 4)
  .regex(/^[A-Za-z0-9+/]*={0,2}$/)
  .refine((value) => value.length % 4 === 0, 'Invalid base64 length.');
export const textureReviewExportSchema = z
  .object({
    schemaVersion: z.literal(1),
    kind: z.literal('texture-review-export'),
    scope: z.literal('review-only'),
    approval: z.literal('unreviewed'),
    activation: z.literal('none'),
    packageData: textureReviewClientPackageSchema,
    originalPngBase64: base64,
    references: z.array(reference).max(TEXTURE_REVIEW_EXPORT_LIMITS.references),
    contentDigest: digest,
  })
  .strict()
  .superRefine((value, context) => {
    const ids = value.references.map((entry) => `${entry.libraryFileId}:${entry.version}`);
    if (new Set(ids).size !== ids.length)
      context.addIssue({ code: 'custom', message: 'Source reference identities must be unique.' });
    if (
      value.references.some(
        (entry) =>
          entry.relationship === 'original-input' &&
          entry.sha256 !== value.packageData.receipt.original.sha256,
      )
    )
      context.addIssue({
        code: 'custom',
        message: 'Original input reference must match the retained source PNG.',
      });
    const padding = value.originalPngBase64.endsWith('==')
      ? 2
      : value.originalPngBase64.endsWith('=')
        ? 1
        : 0;
    if (
      (value.originalPngBase64.length / 4) * 3 - padding !==
      value.packageData.receipt.original.bytes
    )
      context.addIssue({ code: 'custom', message: 'Retained original PNG byte count mismatch.' });
  });
export type TextureReviewExportArtifact = z.infer<typeof textureReviewExportSchema>;

/** Separate larger envelope; the existing pipeline canonicalizer retains its 1 MB ceiling. */
function stableJson(value: unknown): string {
  let nodes = 0;
  const seen = new Set<object>();
  const visit = (item: unknown, depth: number): string => {
    if (++nodes > TEXTURE_REVIEW_EXPORT_LIMITS.nodes || depth > TEXTURE_REVIEW_EXPORT_LIMITS.depth)
      throw new Error('Review export structure exceeds its bounded envelope.');
    if (
      item === null ||
      typeof item === 'string' ||
      typeof item === 'boolean' ||
      (typeof item === 'number' && Number.isFinite(item))
    )
      return JSON.stringify(item);
    if (!item || typeof item !== 'object' || seen.has(item))
      throw new Error('Review export requires finite acyclic JSON.');
    seen.add(item);
    let result: string;
    if (Array.isArray(item))
      result = '[' + item.map((entry) => visit(entry, depth + 1)).join(',') + ']';
    else {
      if (Object.getPrototypeOf(item) !== Object.prototype && Object.getPrototypeOf(item) !== null)
        throw new Error('Review export requires plain JSON objects.');
      const entries: [string, unknown][] = Object.entries(item);
      result =
        '{' +
        entries
          .sort(([a], [b]) => (a < b ? -1 : a > b ? 1 : 0))
          .map(([key, entry]) => JSON.stringify(key) + ':' + visit(entry, depth + 1))
          .join(',') +
        '}';
    }
    seen.delete(item);
    return result;
  };
  const result = visit(value, 0);
  if (
    result.length > TEXTURE_REVIEW_EXPORT_LIMITS.bytes ||
    new TextEncoder().encode(result).length > TEXTURE_REVIEW_EXPORT_LIMITS.bytes
  )
    throw new Error('Review export exceeds its byte envelope.');
  return result;
}
async function sha256(bytes: Uint8Array, signal?: AbortSignal) {
  signal?.throwIfAborted();
  const hash = new Uint8Array(await crypto.subtle.digest('SHA-256', new Uint8Array(bytes).buffer));
  signal?.throwIfAborted();
  return [...hash].map((byte) => byte.toString(16).padStart(2, '0')).join('');
}
function encode(bytes: Uint8Array) {
  let binary = '';
  for (let offset = 0; offset < bytes.length; offset += 8192)
    binary += String.fromCharCode(...bytes.subarray(offset, offset + 8192));
  return btoa(binary);
}
function decode(value: string) {
  const binary = atob(value),
    bytes = new Uint8Array(binary.length);
  for (let index = 0; index < binary.length; index++) bytes[index] = binary.charCodeAt(index);
  return bytes;
}
function checkHeader(bytes: Uint8Array, packageData: TextureReviewClientPackage) {
  if (bytes.length < 33 || bytes.length > TEXTURE_REVIEW_LIMITS.encodedBytes)
    throw new Error('Review PNG exceeds its byte envelope.');
  const view = new DataView(bytes.buffer, bytes.byteOffset, bytes.byteLength);
  if (
    view.getUint32(0) !== 0x89504e47 ||
    view.getUint32(4) !== 0x0d0a1a0a ||
    view.getUint32(8) !== 13 ||
    view.getUint32(12) !== 0x49484452 ||
    view.getUint32(16) !== packageData.manifest.atlas.width ||
    view.getUint32(20) !== packageData.manifest.atlas.height ||
    bytes[24] !== 8 ||
    bytes[25] !== 6 ||
    bytes[26] !== 0 ||
    bytes[27] !== 0 ||
    bytes[28] !== 0
  )
    throw new Error('Review PNG header is not the declared straight RGBA8 atlas.');
}
async function verifyOriginal(
  packageData: TextureReviewClientPackage,
  original: Uint8Array,
  signal?: AbortSignal,
) {
  checkHeader(original, packageData);
  if (
    original.length !== packageData.receipt.original.bytes ||
    (await sha256(original, signal)) !== packageData.receipt.original.sha256
  )
    throw new Error('Retained original PNG identity mismatch.');
}
/** The digest covers all content/identities except explicitly volatile CPU wall timings. */
async function contentDigest(artifact: TextureReviewExportArtifact, signal?: AbortSignal) {
  const { contentDigest: omittedDigest, packageData, ...content } = artifact;
  const { timings: omittedTimings, ...receipt } = packageData.receipt;
  void omittedDigest;
  void omittedTimings;
  return sha256(
    new TextEncoder().encode(stableJson({ ...content, packageData: { ...packageData, receipt } })),
    signal,
  );
}
export async function createTextureReviewExport(
  value: TextureReviewClientPackage,
  originalPng: Uint8Array,
  references: TextureReviewExportReference[] = [],
  signal?: AbortSignal,
) {
  const verified = await verifyTexturePreviewPackage(value, signal);
  checkHeader(verified.bytes, verified.packageData);
  // Own a bounded copy before awaits so caller mutation cannot change the exported source.
  if (originalPng.byteLength > TEXTURE_REVIEW_LIMITS.encodedBytes)
    throw new Error('Original PNG exceeds its byte envelope.');
  const original = new Uint8Array(originalPng);
  await verifyOriginal(verified.packageData, original, signal);
  const artifact = textureReviewExportSchema.parse({
    schemaVersion: 1,
    kind: 'texture-review-export',
    scope: 'review-only',
    approval: 'unreviewed',
    activation: 'none',
    packageData: verified.packageData,
    originalPngBase64: encode(original),
    references,
    contentDigest: '0'.repeat(64),
  });
  artifact.contentDigest = await contentDigest(artifact, signal);
  const json = stableJson(artifact);
  return {
    artifact,
    json,
    contentDigest: artifact.contentDigest,
    bytes: new TextEncoder().encode(json).length,
  };
}
/** Verifies saved identities/header/digest only; existing server admission must decode again. */
export async function parseTextureReviewExport(text: string, signal?: AbortSignal) {
  signal?.throwIfAborted();
  if (
    text.length > TEXTURE_REVIEW_EXPORT_LIMITS.bytes ||
    new TextEncoder().encode(text).length > TEXTURE_REVIEW_EXPORT_LIMITS.bytes
  )
    throw new Error('Review export exceeds its byte envelope.');
  const candidate: unknown = JSON.parse(text),
    artifact = textureReviewExportSchema.parse(candidate);
  if ((await contentDigest(artifact, signal)) !== artifact.contentDigest)
    throw new Error('Review export content digest mismatch.');
  const verified = await verifyTexturePreviewPackage(artifact.packageData, signal),
    originalPng = decode(artifact.originalPngBase64);
  checkHeader(verified.bytes, verified.packageData);
  await verifyOriginal(verified.packageData, originalPng, signal);
  return {
    artifact,
    packageData: verified.packageData,
    originalPng,
    canonicalPng: verified.bytes,
    contentDigest: artifact.contentDigest,
  };
}
export type TextureReviewExportImport = Awaited<ReturnType<typeof parseTextureReviewExport>>;
/** Payload for the existing same-origin guarded POST; this helper makes no request. */
export function textureReviewRevalidationForm(imported: TextureReviewExportImport) {
  const form = new FormData();
  form.set('manifest', JSON.stringify(imported.packageData.manifest));
  form.set(
    'file',
    new Blob([new Uint8Array(imported.originalPng).buffer], { type: 'image/png' }),
    'texture-review-original.png',
  );
  return form;
}
export async function verifyTextureReviewRoundTrip(
  imported: TextureReviewExportImport,
  response: TextureReviewClientPackage,
  signal?: AbortSignal,
) {
  const verified = await verifyTexturePreviewPackage(response, signal),
    before = imported.packageData,
    after = verified.packageData;
  if (
    stableJson(before.manifest) !== stableJson(after.manifest) ||
    stableJson(before.receipt.original) !== stableJson(after.receipt.original) ||
    stableJson(before.receipt.canonical) !== stableJson(after.receipt.canonical) ||
    stableJson(before.receipt.frameDigests) !== stableJson(after.receipt.frameDigests)
  )
    throw new Error('Revalidated texture identities, source manifest or frame pixels changed.');
  return {
    scope: 'review-only' as const,
    activation: 'none' as const,
    matches: true as const,
    originalSha256: after.receipt.original.sha256,
    canonicalPngSha256: after.receipt.canonical.sha256,
    rgbaSha256: after.receipt.canonical.rgbaSha256,
    frameDigests: after.receipt.frameDigests,
  };
}

