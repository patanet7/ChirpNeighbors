import { createHash } from 'node:crypto';
import { performance } from 'node:perf_hooks';
import { crc32, inflateSync } from 'node:zlib';
import sharp from 'sharp';
import { YardError } from '../server/storage/repository';
import {
  parseTextureReviewManifest,
  textureReviewClientPackageSchema,
  TEXTURE_REVIEW_LIMITS as limits,
  TEXTURE_REVIEW_PROFILE,
  type TextureReviewManifest,
} from './texture-profile';

const hash = (bytes: Uint8Array) => createHash('sha256').update(bytes).digest('hex');
const signature = Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]);
const srgbChromaticity = [31270, 32900, 64000, 33000, 30000, 60000, 15000, 6000];
function invalid(message: string): never {
  throw new YardError('INVALID', message);
}
/** Separate admission parser: no mutation or relaxation of the existing PNG intake. */
export function preflightTextureReviewPng(value: Uint8Array) {
  if (value.byteLength < 57 || value.byteLength > limits.encodedBytes)
    invalid('Experimental texture PNG exceeds its 4 MiB byte envelope.');
  const bytes = Buffer.from(value);
  if (!bytes.subarray(0, 8).equals(signature)) invalid('Only PNG bytes are accepted.');
  let offset = 8,
    chunks = 0,
    width = 0,
    height = 0,
    metadata = 0,
    idat = false,
    afterIdat = false,
    ended = false;
  const seen = new Set<string>(),
    data: Buffer[] = [],
    clean: Buffer[] = [signature];
  while (offset < bytes.length) {
    if (++chunks > limits.pngChunks || offset + 12 > bytes.length)
      invalid('PNG chunk budget or structure is invalid.');
    const length = bytes.readUInt32BE(offset),
      end = offset + 12 + length;
    if (end > bytes.length) invalid('PNG is truncated.');
    const type = bytes.toString('ascii', offset + 4, offset + 8),
      payload = bytes.subarray(offset + 8, end - 4);
    if (!/^[A-Za-z]{4}$/.test(type) || type[2] !== type[2]?.toUpperCase())
      invalid('Invalid PNG chunk type.');
    if (crc32(bytes.subarray(offset + 4, end - 4)) !== bytes.readUInt32BE(end - 4))
      invalid('PNG checksum mismatch.');
    if (chunks === 1 && type !== 'IHDR') invalid('PNG must begin with IHDR.');
    if (seen.has(type) && type !== 'IDAT' && !['tEXt', 'eXIf'].includes(type))
      invalid('Duplicate PNG metadata.');
    if (idat && type !== 'IDAT') afterIdat = true;
    if (type === 'IHDR') {
      if (length !== 13) invalid('Invalid PNG header.');
      width = payload.readUInt32BE(0);
      height = payload.readUInt32BE(4);
      if (
        !width ||
        !height ||
        width > limits.atlasEdge ||
        height > limits.atlasEdge ||
        width * height > limits.atlasPixels
      )
        invalid('Experimental texture atlas exceeds its pixel envelope.');
      if (
        payload[8] !== 8 ||
        payload[9] !== 6 ||
        payload[10] !== 0 ||
        payload[11] !== 0 ||
        payload[12] !== 0
      )
        invalid('Only non-interlaced 8-bit RGBA PNG is supported.');
      clean.push(bytes.subarray(offset, end));
    } else if (type === 'IDAT') {
      if (afterIdat || !length) invalid('PNG image data must be contiguous and nonempty.');
      idat = true;
      data.push(payload);
      clean.push(bytes.subarray(offset, end));
    } else if (type === 'IEND') {
      if (!idat || length !== 0 || end !== bytes.length)
        invalid('PNG has missing data or trailing bytes.');
      ended = true;
      clean.push(bytes.subarray(offset, end));
    } else if (['sRGB', 'gAMA', 'cHRM'].includes(type)) {
      if (idat) invalid('PNG color declarations must precede data.');
      if (type === 'sRGB' && (length !== 1 || payload[0]! > 3))
        invalid('Invalid PNG sRGB declaration.');
      if (type === 'gAMA' && (length !== 4 || payload.readUInt32BE(0) !== 45455))
        invalid('Only sRGB PNG color is supported.');
      if (
        type === 'cHRM' &&
        (length !== 32 || srgbChromaticity.some((v, i) => payload.readUInt32BE(i * 4) !== v))
      )
        invalid('Only sRGB PNG color is supported.');
    } else if (['tEXt', 'eXIf', 'pHYs', 'tIME'].includes(type)) {
      metadata += length;
      if (metadata > limits.metadataBytes) invalid('PNG metadata budget exceeded.');
    } else invalid('Unsupported PNG chunks, animation or color profile.');
    seen.add(type);
    offset = end;
  }
  if (!ended) invalid('PNG end marker missing.');
  const compressed = Buffer.concat(data),
    expected = height * (1 + width * 4);
  try {
    const inflated: unknown = inflateSync(compressed, {
      maxOutputLength: expected + 1,
      info: true,
    });
    if (
      !inflated ||
      typeof inflated !== 'object' ||
      !('buffer' in inflated) ||
      !Buffer.isBuffer(inflated.buffer) ||
      !('engine' in inflated) ||
      !inflated.engine ||
      typeof inflated.engine !== 'object' ||
      !('bytesWritten' in inflated.engine) ||
      inflated.buffer.length !== expected ||
      inflated.engine.bytesWritten !== compressed.length
    )
      invalid('PNG decompression length mismatch.');
    for (let y = 0; y < height; y++)
      if (inflated.buffer[y * (1 + width * 4)]! > 4) invalid('Invalid PNG scanline filter.');
  } catch {
    invalid('PNG compressed data exceeds bounds or is invalid.');
  }
  return { input: Buffer.concat(clean), width, height, chunks };
}
let decoding = 0;
export async function validateTextureReviewPng(value: Uint8Array, candidate: unknown) {
  if (decoding >= limits.concurrentDecodes) invalid('Experimental texture decoder is busy.');
  decoding++;
  const started = performance.now();
  try {
    const manifest = parseTextureReviewManifest(candidate),
      checked = preflightTextureReviewPng(value),
      originalSha256 = hash(value);
    if (originalSha256 !== manifest.source.sha256)
      invalid('Original PNG hash does not match source provenance.');
    if (checked.width !== manifest.atlas.width || checked.height !== manifest.atlas.height)
      invalid('PNG dimensions do not match the declared atlas.');
    const decodeStarted = performance.now();
    const { data, info } = await sharp(checked.input, {
      failOn: 'warning',
      limitInputPixels: limits.atlasPixels,
      limitInputChannels: 4,
      unlimited: false,
      ignoreIcc: true,
    })
      .timeout({ seconds: limits.decodeSeconds })
      .toColourspace('srgb')
      .ensureAlpha()
      .raw({ depth: 'uchar' })
      .toBuffer({ resolveWithObject: true })
      .catch(() => invalid('Texture PNG decoding failed. Check the supported format and size.'));
    if (
      info.width !== checked.width ||
      info.height !== checked.height ||
      info.channels !== 4 ||
      data.length !== checked.width * checked.height * 4 ||
      data.length > limits.decodedRgbaBytes
    )
      invalid('Decoded RGBA allocation differs from the validated header.');
    const decodeMs = performance.now() - decodeStarted,
      validationStarted = performance.now(),
      colors = new Set<number>();
    let partialAlphaPixels = 0,
      transparentPixels = 0,
      hiddenRgbPixelsZeroed = 0;
    for (let i = 0; i < data.length; i += 4) {
      const alpha = data[i + 3]!;
      if (!alpha) {
        transparentPixels++;
        if (data[i] || data[i + 1] || data[i + 2]) hiddenRgbPixelsZeroed++;
        data.fill(0, i, i + 3);
      } else {
        colors.add((data[i]! << 16) | (data[i + 1]! << 8) | data[i + 2]!);
        if (alpha < 255) partialAlphaPixels++;
      }
    }
    for (const frame of manifest.frames)
      for (const contact of frame.contacts) {
        const x = frame.sourceRect.x + contact.x - frame.trim.x,
          y = frame.sourceRect.y + contact.y - frame.trim.y;
        if (!data[(y * checked.width + x) * 4 + 3])
          invalid('Declared contact addresses an alpha-zero source pixel.');
      }
    const frameDigests = manifest.frames.map((frame) => {
      const digest = createHash('sha256');
      for (let y = 0; y < frame.sourceRect.height; y++) {
        const start = ((frame.sourceRect.y + y) * checked.width + frame.sourceRect.x) * 4;
        digest.update(data.subarray(start, start + frame.sourceRect.width * 4));
      }
      return { id: frame.id, rgbaSha256: digest.digest('hex') };
    });
    const validationMs = performance.now() - validationStarted,
      encodeStarted = performance.now();
    // PNG is straight alpha by specification; no premultiplication is applied here.
    // A mislabeled artist-premultiplied source cannot be detected from arbitrary samples.
    const canonicalPng = await sharp(data, {
      raw: { width: info.width, height: info.height, channels: 4, premultiplied: false },
    })
      .timeout({ seconds: limits.decodeSeconds })
      .png({ palette: false, compressionLevel: 6, progressive: false, adaptiveFiltering: true })
      .toBuffer();
    if (canonicalPng.length > limits.encodedBytes)
      invalid('Canonical texture PNG exceeds its byte envelope.');
    const encodeMs = performance.now() - encodeStarted;
    return {
      manifest,
      canonicalPng,
      receipt: {
        profile: TEXTURE_REVIEW_PROFILE,
        activation: 'none' as const,
        approved: false as const,
        original: { sha256: originalSha256, bytes: value.byteLength },
        canonical: {
          sha256: hash(canonicalPng),
          rgbaSha256: hash(data),
          bytes: canonicalPng.length,
          width: info.width,
          height: info.height,
        },
        alpha: 'straight-rgba8' as const,
        normalization: 'zero-hidden-rgb-only-v1' as const,
        contactRule: 'alpha-greater-than-zero-only-not-physical-review' as const,
        metrics: {
          partialAlphaPixels,
          transparentPixels,
          hiddenRgbPixelsZeroed,
          visibleRgbColors: colors.size,
          frames: manifest.frames.length,
          uniqueSourceFramePixels: new Set(frameDigests.map((frame) => frame.rgbaSha256)).size,
          knownDecodedRgbaBytes: data.length,
          knownSanitizedPngBytes: checked.input.length,
          pngChunks: checked.chunks,
          knownCanonicalPngBytes: canonicalPng.length,
        },
        frameDigests,
        decoder: {
          id: 'sharp' as const,
          version: sharp.versions.sharp,
          libvips: sharp.versions.vips,
        },
        timings: {
          scope: 'cpu-wall-time-not-gpu-or-peak-memory' as const,
          decodeMs,
          validationMs,
          encodeMs,
          totalMs: performance.now() - started,
        },
      },
    };
  } finally {
    decoding--;
  }
}
export type TextureReviewPackage = Awaited<ReturnType<typeof validateTextureReviewPng>>;
/** Bounded base64 transport; never serializes a raw RGBA numeric array. */
export function textureReviewClientPackage(pack: TextureReviewPackage) {
  return textureReviewClientPackageSchema.parse({
    manifest: pack.manifest,
    receipt: pack.receipt,
    canonicalPngBase64: pack.canonicalPng.toString('base64'),
  });
}
export async function createSyntheticTextureReviewBaseline(frameEdge: 128 | 256 = 256) {
  if (frameEdge !== 128 && frameEdge !== 256)
    invalid('Synthetic baseline edge must be 128 or 256.');
  const width = frameEdge * 4,
    height = frameEdge * 4,
    rgba = Buffer.alloc(width * height * 4);
  for (let y = 0; y < height; y++)
    for (let x = 0; x < width; x++) {
      const i = (y * width + x) * 4,
        frameSeed = Math.floor(x / frameEdge) + Math.floor(y / frameEdge) * 4;
      rgba.set(
        [
          (x * 17 + y * 3 + frameSeed * 5) & 255,
          (x * 7 + y * 29 + frameSeed * 11) & 255,
          (x ^ y) & 255,
          (x + y) % 17 === 0 ? 0 : 64 + ((x * 11 + y * 13) % 192),
        ],
        i,
      );
    }
  const frames = Array.from({ length: 16 }, (_, i) => ({
    id: `synthetic-${i}`,
    sourceRect: {
      x: (i % 4) * frameEdge,
      y: Math.floor(i / 4) * frameEdge,
      width: frameEdge,
      height: frameEdge,
    },
    canvas: { width: frameEdge, height: frameEdge },
    trim: { x: 0, y: 0 },
    pivot: { x: frameEdge / 2, y: frameEdge },
    contacts: [{ id: 'synthetic-support', x: frameEdge / 2, y: frameEdge - 1 }],
    world: { width: 128, height: 128 },
    sourcePixelsPerWorldUnit: frameEdge / 128,
  }));
  // Keep declared support samples visible; this establishes no biological contact claim.
  for (const frame of frames) {
    const x = frame.sourceRect.x + frame.contacts[0]!.x,
      y = frame.sourceRect.y + frame.contacts[0]!.y;
    rgba[(y * width + x) * 4 + 3] = 255;
  }
  const source = await sharp(rgba, { raw: { width, height, channels: 4, premultiplied: false } })
    .png({ palette: false, compressionLevel: 6, adaptiveFiltering: true })
    .toBuffer();
  const manifest: TextureReviewManifest = {
    schemaVersion: 1,
    profile: TEXTURE_REVIEW_PROFILE,
    scope: 'review-only',
    approval: 'unreviewed',
    activation: 'none',
    source: {
      sha256: hash(source),
      creator: 'deterministic synthetic baseline',
      tool: 'sharp',
      toolVersion: sharp.versions.sharp,
      rights: 'unreviewed',
      fidelity: 'unreviewed',
    },
    atlas: { width, height, alpha: 'straight-rgba8', colorSpace: 'srgb' },
    frames,
    clips: [
      {
        id: 'idle',
        tickRate: 30,
        loop: true,
        frames: frames.map((frame) => ({ frameId: frame.id, durationTicks: 3 })),
      },
    ],
  };
  const pack = await validateTextureReviewPng(source, manifest);
  return {
    ...pack,
    baseline: {
      kind: 'synthetic-detail-not-bird-art' as const,
      frameEdge,
      uniqueFrames: 16,
      sourceRgbaAllocationBytes: rgba.length,
      encodedInputBytes: source.length,
      estimatedSingleAtlasRgbaUploadBytes: rgba.length,
      gpuMeasurement: false as const,
    },
  };
}

