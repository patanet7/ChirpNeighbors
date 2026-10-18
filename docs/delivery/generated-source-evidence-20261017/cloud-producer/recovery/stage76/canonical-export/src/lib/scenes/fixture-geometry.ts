/** Existing authored fixture geometry, moved unchanged from engine/visuals. No new art. */
import type { ScenePixelRect as PixelRect, SceneSetting } from './manifest.ts';
const shape = (
  x: number,
  y: number,
  width: number,
  height: number,
  color: PixelRect['color'],
  alpha?: number,
): PixelRect => ({ x, y, width, height, color, ...(alpha === undefined ? {} : { alpha }) });
/** Background geometry contains no interactive object or bird pixels. */
export function backgroundPrimitives(setting: SceneSetting): PixelRect[] {
  const result = [shape(0, 0, 960, 540, 'sky'), shape(0, 145, 960, 145, 'skyLow')];
  // A neighbor's modest roof, hedge and fence make this an ordinary backyard.
  result.push(
    shape(40, 204, 196, 96, 'wall'),
    shape(30, 195, 216, 11, 'trunk'),
    shape(42, 184, 192, 11, 'trunk'),
    shape(60, 173, 156, 11, 'wood'),
    shape(73, 218, 44, 38, 'sky'),
    shape(93, 218, 4, 38, 'wood'),
  );
  for (let i = 0; i < 13; i++) {
    const y = 247 - ((i * 17) % 30);
    result.push(
      shape(i * 80, y, 85, 310 - y, 'leaf'),
      shape(i * 80 + 9, y - 8, 61, 10, 'leafLight'),
    );
  }
  const fenceY = setting === 'courtyard' ? 283 : 281;
  result.push(shape(0, fenceY + 21, 960, 9, 'wood'), shape(0, fenceY + 58, 960, 8, 'wood'));
  for (let x = 0; x < 960; x += 28)
    result.push(shape(x, fenceY, 22, 74, 'wood'), shape(x + 3, fenceY + 3, 3, 68, 'glow', 0.14));
  return result;
}

export function groundPrimitives(setting: SceneSetting): PixelRect[] {
  const result = [shape(0, 354, 960, 186, 'grassLight'), shape(0, 354, 960, 14, 'grass')];
  if (setting === 'courtyard') {
    result.push(shape(44, 366, 72, 174, 'stone'), shape(844, 366, 72, 174, 'stone'));
    for (let y = 380; y < 540; y += 28)
      result.push(shape(44, y, 72, 2, 'trunk', 0.16), shape(844, y, 72, 2, 'trunk', 0.16));
  }
  for (let i = 0; i < 52; i++) {
    const x = 30 + ((i * 107) % 900),
      y = 379 + ((i * 47) % 150);
    result.push(shape(x, y, 3, 5, 'grass', 0.65), shape(x + 5, y - 2, 2, 7, 'grass', 0.65));
  }
  return result;
}

export function foregroundPrimitives(): PixelRect[] {
  const result: PixelRect[] = [];
  for (const x of [0, 25, 920, 943])
    result.push(shape(x, 510, 25, 30, 'leaf'), shape(x + 5, 501, 17, 12, 'leafLight'));
  for (const x of [13, 39, 927, 950])
    result.push(shape(x, 500, 3, 18, 'leaf'), shape(x - 4, 497, 11, 7, 'flower'));
  return result;
}
