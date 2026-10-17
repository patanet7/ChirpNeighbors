import { z } from 'zod';
import {
  imageStageSequenceSchema,
  imageQaPolicySchema,
  losslessPixelPolicySchema,
  type ImageStageFrame,
  type ImageStageSequence,
} from '../../assets/image-stage-contracts';
import { assetPackagingInputV2Schema } from '../../assets/intake-v2';
import { digest, PermanentStageError } from '../pipeline/canonical';
import { bytesSha256 } from './reference-stage';
import { normalizeDecodedPixels } from './package';
import { supportedPackagingInputV2 } from './package-v2';

function fail(message: string): never {
  throw new PermanentStageError(message);
}

/** Check the total budget before Zod copies channel arrays or a typed buffer is allocated. */
function assertSequenceBudget(value: unknown): void {
  const envelope = z
    .object({
      canvas: z.object({
        width: z.number().int().min(1).max(256),
        height: z.number().int().min(1).max(256),
      }),
      frames: z.array(z.unknown()).min(1).max(64),
    })
    .parse(value);
  if (envelope.canvas.width * envelope.canvas.height * envelope.frames.length > 65_536)
    fail('Image sequence exceeds decoded pixel budget');
  const pixels = envelope.canvas.width * envelope.canvas.height;
  for (const value of envelope.frames) {
    // z.unknown checks the envelope without cloning any channel array.
    const frame = z
      .object({
        sourceRgba: z.unknown(),
        matte: z.object({ alpha: z.unknown() }),
        foreground: z.object({ rgb: z.unknown() }),
        segmentation: z.object({ values: z.unknown() }).nullable(),
      })
      .parse(value);
    const channels: [unknown, number][] = [
      [frame.sourceRgba, pixels * 4],
      [frame.matte.alpha, pixels],
      [frame.foreground.rgb, pixels * 3],
    ];
    if (frame.segmentation) channels.push([frame.segmentation.values, pixels]);
    for (const [channel, expectedLength] of channels)
      if (!Array.isArray(channel) || channel.length !== expectedLength)
        fail('Image channel dimensions do not match canvas before payload parsing');
  }
}

/** Portable hash encoding for logits; rejects values that change when encoded as float32. */
export function logitsSha256(values: readonly number[]): string {
  if (!values.length || values.length > 65_536) fail('Logit channel exceeds pixel budget');
  const bytes = new Uint8Array(values.length * 4),
    view = new DataView(bytes.buffer);
  for (const [index, value] of values.entries()) {
    if (
      !Number.isFinite(value) ||
      Object.is(value, -0) ||
      Math.abs(value) > 1_000_000 ||
      Math.fround(value) !== value
    )
      fail('Logits must be finite exact float32 values');
    view.setFloat32(index * 4, value, true);
  }
  return bytesSha256(bytes);
}

export function validateImageSequence(value: unknown): ImageStageSequence {
  assertSequenceBudget(value);
  const sequence = imageStageSequenceSchema.parse(value);
  for (const frame of sequence.frames) {
    if (
      bytesSha256(Uint8Array.from(frame.sourceRgba)) !== frame.sourceSha256 ||
      bytesSha256(Uint8Array.from(frame.matte.alpha)) !== frame.matte.sha256 ||
      bytesSha256(Uint8Array.from(frame.foreground.rgb)) !== frame.foreground.sha256
    )
      fail('Frame source, matte or foreground bytes do not match their hashes');
    if (frame.segmentation) {
      const actual =
        frame.segmentation.encoding === 'logits-f32-le'
          ? logitsSha256(frame.segmentation.values)
          : bytesSha256(Uint8Array.from(frame.segmentation.values));
      if (actual !== frame.segmentation.sha256) fail('Segmentation bytes do not match their hash');
    }
    if (frame.foreground.alphaMode === 'premultiplied')
      for (let index = 0; index < frame.matte.alpha.length; index++)
        for (let channel = 0; channel < 3; channel++)
          if ((frame.foreground.rgb[index * 3 + channel] ?? 256) > (frame.matte.alpha[index] ?? -1))
            fail('Premultiplied foreground has color greater than alpha');
  }
  return sequence;
}

const backgroundSchema = z.tuple([
  z.number().int().min(0).max(255),
  z.number().int().min(0).max(255),
  z.number().int().min(0).max(255),
]);

/** Composite supplied foreground. This does not recover foreground from contaminated source RGB. */
export function compositeImageFrame(
  value: unknown,
  frameIndex: number,
  backgroundValue: unknown,
): Uint8Array {
  const sequence = validateImageSequence(value),
    background = backgroundSchema.parse(backgroundValue);
  const frame = sequence.frames[frameIndex];
  if (!Number.isInteger(frameIndex) || !frame) fail('Composite frame index is unavailable');
  const output = new Uint8Array(sequence.canvas.width * sequence.canvas.height * 3);
  for (let pixel = 0; pixel < frame.matte.alpha.length; pixel++) {
    const alpha = (frame.matte.alpha[pixel] ?? 0) / 255;
    for (let channel = 0; channel < 3; channel++) {
      const color = frame.foreground.rgb[pixel * 3 + channel] ?? 0;
      const foreground = frame.foreground.alphaMode === 'straight' ? color * alpha : color;
      output[pixel * 3 + channel] = Math.round(
        foreground + (background[channel] ?? 0) * (1 - alpha),
      );
    }
  }
  return output;
}

function edgePixels(
  frame: ImageStageFrame,
  canvas: ImageStageSequence['canvas'],
  threshold: number,
): Set<string> {
  const { width, height } = canvas,
    result = new Set<string>();
  const opaque = (x: number, y: number) =>
    x >= 0 &&
    x < width &&
    y >= 0 &&
    y < height &&
    (frame.matte.alpha[y * width + x] ?? 0) >= threshold;
  for (let y = 0; y < height; y++)
    for (let x = 0; x < width; x++)
      if (
        opaque(x, y) &&
        (!opaque(x - 1, y) || !opaque(x + 1, y) || !opaque(x, y - 1) || !opaque(x, y + 1))
      )
        result.add(`${x - frame.anchor.x},${y - frame.anchor.y}`);
  return result;
}

/** Translation compensated by declared anchors; not optical flow or a quality/fidelity score. */
export function measureImageSequence(value: unknown, policyValue: unknown) {
  const sequence = validateImageSequence(value),
    policy = imageQaPolicySchema.parse(policyValue);
  const edges = sequence.frames.map((frame) =>
    edgePixels(frame, sequence.canvas, policy.edgeAlphaThreshold),
  );
  const emptyFrames = edges.flatMap((pixels, index) => (pixels.size ? [] : [index]));
  const compare = (from: number, to: number, seam: boolean) => {
    const first = sequence.frames[from],
      next = sequence.frames[to],
      left = edges[from],
      right = edges[to];
    if (!first || !next || !left || !right) return fail('Temporal comparison frame is unavailable');
    const union = new Set([...left, ...right]);
    let changedEdges = 0;
    for (const edge of union) if (left.has(edge) !== right.has(edge)) changedEdges++;
    const changedEdgeFraction = union.size ? changedEdges / union.size : 0;
    const contactSetChanged =
      first.contacts.length !== next.contacts.length ||
      first.contacts.some((contact) => !next.contacts.some((other) => other.kind === contact.kind));
    let maxContactDriftPixels = 0;
    for (const contact of first.contacts) {
      const other = next.contacts.find((point) => point.kind === contact.kind);
      if (other)
        maxContactDriftPixels = Math.max(
          maxContactDriftPixels,
          Math.hypot(
            contact.x - first.anchor.x - (other.x - next.anchor.x),
            contact.y - first.anchor.y - (other.y - next.anchor.y),
          ),
        );
    }
    return {
      from,
      to,
      seam,
      comparedEdges: union.size,
      changedEdges,
      changedEdgeFraction,
      contactSetChanged,
      maxContactDriftPixels,
      passes:
        changedEdgeFraction <= policy.maxChangedEdgeFraction &&
        maxContactDriftPixels <= policy.maxContactDriftPixels &&
        (!contactSetChanged || policy.allowContactSetChange),
    };
  };
  const comparisons = sequence.frames
    .slice(1)
    .map((_frame, index) => compare(index, index + 1, false));
  if (sequence.loop) comparisons.push(compare(sequence.frames.length - 1, 0, true));
  return {
    schemaVersion: 1 as const,
    method: 'anchor-translation-edge-set-v1' as const,
    fixture: sequence.fixture,
    policy,
    frameCount: sequence.frames.length,
    timeline: sequence.frames.map(({ id, timestampUs, durationUs }) => ({
      id,
      timestampUs,
      durationUs,
    })),
    comparisons,
    emptyFrames,
    passes: emptyFrames.length === 0 && comparisons.every((comparison) => comparison.passes),
    limitation:
      'Mechanical translation/contact QA only; not optical flow, temporal matting or species fidelity.',
  };
}

/** Requires already binary alpha and an exact palette/grid. No thresholding, color approximation,
 * largest-component removal, hole fill, frame interpolation, or synthetic image generation. */
export function normalizeImageSequence(value: unknown, policyValue: unknown) {
  const sequence = validateImageSequence(value),
    policy = losslessPixelPolicySchema.parse(policyValue);
  const { width, height } = sequence.canvas,
    grid = policy.logicalPixelSize;
  if (width % grid || height % grid) fail('Source canvas does not align to the reviewed grid');
  let left = width,
    top = height,
    right = 0,
    bottom = 0;
  const rgbaFrames = sequence.frames.map((frame) => {
    const rgba = new Array<number>(width * height * 4).fill(0);
    for (let index = 0; index < width * height; index++) {
      const alpha = frame.matte.alpha[index];
      if (alpha !== 0 && alpha !== 255)
        fail('Soft alpha requires explicit cleanup/review before binary sprite packaging');
      if (!alpha) continue;
      const x = index % width,
        y = Math.floor(index / width);
      left = Math.min(left, x);
      top = Math.min(top, y);
      right = Math.max(right, x + 1);
      bottom = Math.max(bottom, y + 1);
      for (let channel = 0; channel < 3; channel++)
        rgba[index * 4 + channel] = frame.foreground.rgb[index * 3 + channel] ?? 0;
      rgba[index * 4 + 3] = 255;
    }
    for (const point of [frame.anchor, ...frame.contacts]) {
      left = Math.min(left, point.x);
      top = Math.min(top, point.y);
      right = Math.max(right, point.x);
      bottom = Math.max(bottom, point.y);
    }
    return { rgba };
  });
  // Validate full source cells and per-frame transparency before cropping can hide defects.
  normalizeDecodedPixels({
    canvas: sequence.canvas,
    frames: rgbaFrames,
    logicalPixelSize: grid,
    paletteLimit: policy.paletteLimit,
  });
  left = Math.floor(left / grid) * grid;
  top = Math.floor(top / grid) * grid;
  right = Math.ceil(right / grid) * grid;
  bottom = Math.ceil(bottom / grid) * grid;
  const canvas = { width: right - left, height: bottom - top };
  const frames = rgbaFrames.map(({ rgba }) => {
    const cropped: number[] = [];
    for (let y = top; y < bottom; y++)
      for (let x = left; x < right; x++)
        cropped.push(...rgba.slice((y * width + x) * 4, (y * width + x) * 4 + 4));
    return { rgba: cropped };
  });
  normalizeDecodedPixels({
    canvas,
    frames,
    logicalPixelSize: grid,
    paletteLimit: policy.paletteLimit,
  });
  const translate = (point: { x: number; y: number }) => ({ x: point.x - left, y: point.y - top });
  return {
    pixels: {
      schemaVersion: 2 as const,
      format: 'rgba8-frames' as const,
      canvas,
      logicalPixelSize: grid,
      paletteLimit: policy.paletteLimit,
      frames,
    },
    report: {
      schemaVersion: 1 as const,
      algorithm: 'lossless-stable-union-v1' as const,
      policy,
      sourceCanvas: sequence.canvas,
      crop: { x: left, y: top, ...canvas },
      fixture: sequence.fixture,
      referenceIds: sequence.referenceIds,
      frames: sequence.frames.map((frame, index) => ({
        id: frame.id,
        timestampUs: frame.timestampUs,
        durationUs: frame.durationUs,
        sourceSha256: frame.sourceSha256,
        matteSha256: frame.matte.sha256,
        foregroundSha256: frame.foreground.sha256,
        outputSha256: bytesSha256(Uint8Array.from(frames[index]?.rgba ?? [])),
        anchor: translate(frame.anchor),
        contacts: frame.contacts.map((contact) => ({ ...contact, ...translate(contact) })),
      })),
    },
  };
}

/** Existing reviewed-package bridge. The caller retains sequence/report alongside this candidate.
 * This does not persist, approve, pin, or make an unconfigured generation strategy runnable.
 * Source timestamps stay in the audit; authored clip ticks are preserved exactly, never inferred. */
export function prepareLosslessPackagingCandidate(
  inputValue: unknown,
  sequenceValue: unknown,
  policyValue: unknown,
) {
  if (inputValue && typeof inputValue === 'object' && 'shape' in inputValue)
    fail(
      'Normalize pixels before adding reviewed shape geometry; existing shape lineage cannot be cropped',
    );
  const input = supportedPackagingInputV2(inputValue),
    sequence = validateImageSequence(sequenceValue);
  if (
    (input.source.source === 'deterministic_fixture') !== sequence.fixture ||
    input.pixels.canvas.width !== sequence.canvas.width ||
    input.pixels.canvas.height !== sequence.canvas.height ||
    input.pixels.frames.length !== sequence.frames.length
  )
    fail('Packaging source and image-stage sequence do not describe the same frames');
  const referenceIds = input.source.references.map((reference) => reference.id);
  if (
    referenceIds.length !== sequence.referenceIds.length ||
    referenceIds.some((id) => !sequence.referenceIds.includes(id))
  )
    fail('Image-stage reference IDs do not match the pinned packaging references');
  for (const [index, frame] of input.pixels.frames.entries())
    if (bytesSha256(Uint8Array.from(frame.rgba)) !== sequence.frames[index]?.sourceSha256)
      fail('Packaging source bytes do not match image-stage source hashes');
  const normalized = normalizeImageSequence(sequence, policyValue),
    { x, y } = normalized.report.crop;
  const clips = structuredClone(input.clips);
  for (const clip of Object.values(clips))
    for (const pose of clip?.poses ?? []) {
      const source = sequence.frames[pose.frame];
      if (
        !source ||
        pose.pivot.x !== source.anchor.x ||
        pose.pivot.y !== source.anchor.y ||
        pose.contacts.length !== source.contacts.length ||
        pose.contacts.some(
          (contact) =>
            !source.contacts.some(
              (point) =>
                point.kind === contact.kind && point.x === contact.x && point.y === contact.y,
            ),
        )
      )
        fail('Pose pivot/contact must match the exact source frame annotations before crop');
      pose.pivot = { x: pose.pivot.x - x, y: pose.pivot.y - y };
      pose.contacts = pose.contacts.map((contact) => ({
        ...contact,
        x: contact.x - x,
        y: contact.y - y,
      }));
    }
  const candidate = assetPackagingInputV2Schema.parse({
    ...input,
    pixels: normalized.pixels,
    clips,
  });
  const report = {
    ...normalized.report,
    inputDigest: digest(input),
    candidateDigest: digest(candidate),
    timing: 'original-microseconds-retained; authored-clip-ticks-unchanged' as const,
  };
  return { input: candidate, report };
}
