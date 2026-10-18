import {
  speciesManifestV2Schema,
  type PixelRectangle,
  type SpeciesManifestV2,
} from '../../assets/manifest-v2';
import { assetSourceIssues } from '../../assets/source-review';
import { PermanentStageError } from '../pipeline/canonical';
import {
  assetPackagingInputSchema,
  assetSourceSchema,
  pixelAnimationSourceSchema,
  type AssetSource,
  type PixelAnimationSource,
} from './contracts';

function invalid(reason: string): never {
  throw new PermanentStageError(reason);
}

/** Declaration validation supplements the final owner-scoped immutable review record. */
export function validateAssetSource(input: unknown): AssetSource {
  const parsed = assetSourceSchema.safeParse(input);
  if (!parsed.success) return invalid('Invalid asset source contract');
  const source = parsed.data;
  const issue = assetSourceIssues(source)[0];
  if (issue) invalid(issue);
  return source;
}

function component(bytes: readonly number[], offset: number): number {
  const value = bytes[offset];
  if (value === undefined) return invalid('Truncated RGBA frame');
  return value;
}

/** Canonical transparent pixels erase hidden RGB. Partial alpha is rejected, not silently flattened. */
function pixel(bytes: readonly number[], offset: number): number | null {
  const alpha = component(bytes, offset + 3);
  if (alpha === 0) return null;
  if (alpha !== 255) return invalid('Only transparent or opaque pixels are supported');
  return (
    (component(bytes, offset) << 16) |
    (component(bytes, offset + 1) << 8) |
    component(bytes, offset + 2)
  );
}

/** Deterministic horizontal runs, then adjacent equal runs merged vertically. No resampling or invented colors. */
export function normalizePixelFrames(input: unknown): {
  pixels: PixelAnimationSource;
  frames: PixelRectangle[][];
} {
  const parsed = pixelAnimationSourceSchema.safeParse(input);
  if (!parsed.success) return invalid('Invalid pixel source contract');
  const pixels = parsed.data;
  return { pixels, frames: normalizeDecodedPixels(pixels) };
}

/** Shared lossless pixel normalization; timing and pivots are validated by their versioned contracts. */
export function normalizeDecodedPixels(
  pixels: Pick<PixelAnimationSource, 'frames' | 'logicalPixelSize' | 'paletteLimit'> & {
    canvas: { width: number; height: number };
  },
): PixelRectangle[][] {
  const { width, height } = pixels.canvas;
  if (width * height * pixels.frames.length > 65_536)
    invalid('Decoded animation exceeds pixel budget');
  if (width % pixels.logicalPixelSize || height % pixels.logicalPixelSize)
    invalid('Canvas must align to the declared logical pixel grid');
  const colors = new Set<number>();
  let rectangles = 0;
  const frames = pixels.frames.map(({ rgba }) => {
    if (rgba.length !== width * height * 4)
      invalid('RGBA length must exactly match canvas dimensions');
    for (let y = 0; y < height; y++)
      for (let x = 0; x < width; x++) {
        const color = pixel(rgba, (y * width + x) * 4);
        const gridX = x - (x % pixels.logicalPixelSize),
          gridY = y - (y % pixels.logicalPixelSize);
        if (color !== pixel(rgba, (gridY * width + gridX) * 4))
          invalid('Pixels disagree within logical grid cell');
        if (color !== null) colors.add(color);
        if (colors.size > pixels.paletteLimit) invalid('Animation exceeds palette budget');
      }
    const result: PixelRectangle[] = [];
    let previous = new Map<string, PixelRectangle>();
    for (let y = 0; y < height; y++) {
      const current = new Map<string, PixelRectangle>();
      for (let x = 0; x < width;) {
        const color = pixel(rgba, (y * width + x) * 4),
          start = x++;
        if (color === null) continue;
        while (x < width && pixel(rgba, (y * width + x) * 4) === color) x++;
        const key = `${start}/${x - start}/${color}`,
          above = previous.get(key);
        if (above) {
          above.height++;
          current.set(key, above);
        } else {
          const rect = { x: start, y, width: x - start, height: 1, color };
          result.push(rect);
          current.set(key, rect);
          rectangles++;
          if (result.length > 4096 || rectangles > 16_384)
            invalid('Normalized rectangle budget exceeded');
        }
      }
      previous = current;
    }
    if (!result.length) invalid('An animation frame cannot be entirely transparent');
    return result;
  });
  return frames;
}

export function packageAsset(input: unknown): SpeciesManifestV2 {
  const parsed = assetPackagingInputSchema.safeParse(input);
  if (!parsed.success) return invalid('Invalid asset packaging contract');
  const source = validateAssetSource(parsed.data.source);
  const { pixels, frames } = normalizePixelFrames(parsed.data.pixels);
  const manifest = speciesManifestV2Schema.safeParse({
    schemaVersion: 2,
    speciesId: source.speciesId,
    representation: source.representation,
    fixture: source.source === 'deterministic_fixture',
    taxonFidelityReviewed: source.fidelityReview !== null,
    format: 'pixel-rects',
    canvas: pixels.canvas,
    frames,
    clips: pixels.clips,
    provenance: {
      source: source.source,
      creator: source.creator,
      sourceVersion: source.sourceVersion,
      references: source.references.map((reference) => reference.id),
      license: source.license.id,
      usage: source.source === 'deterministic_fixture' ? 'development-only' : 'cleared',
      attribution: source.license.attribution,
    },
  });
  if (!manifest.success) return invalid('Packaged animation failed manifest and clip validation');
  return manifest.data;
}
