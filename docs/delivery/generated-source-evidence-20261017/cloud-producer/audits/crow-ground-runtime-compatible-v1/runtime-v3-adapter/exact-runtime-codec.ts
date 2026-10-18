// Exact extracted runtime codec functions; no body edits. Type-only aliases below are erased by Node24.
import { PermanentStageError } from './contract-snapshot/src/lib/server/pipeline/canonical.ts';
type PixelRectangle={x:number;y:number;width:number;height:number;color:number};
type PixelAnimationSource={frames:{rgba:number[]}[];logicalPixelSize:number;paletteLimit:number};
function invalid(reason: string): never {
  throw new PermanentStageError(reason);
}


function component(bytes: readonly number[], offset: number): number {
  const value = bytes[offset];
  if (value === undefined) return invalid('Truncated RGBA frame');
  return value;
}


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
