// Minimal PNG codec (node built-ins only): decode any non-interlaced 8/16-bit or palette PNG to
// RGBA8, encode RGBA8 deterministically. Used by the art scripts; no npm dependencies.
import zlib from 'node:zlib';

const SIG = Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]);
const CRC_TABLE = Array.from({ length: 256 }, (_, n) => {
  let c = n;
  for (let k = 0; k < 8; k++) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1;
  return c >>> 0;
});
const crc32 = (buf) => {
  let c = 0xffffffff;
  for (const b of buf) c = CRC_TABLE[(c ^ b) & 0xff] ^ (c >>> 8);
  return (c ^ 0xffffffff) >>> 0;
};

export const isPng = (buf) => buf.length > 8 && buf.subarray(0, 8).equals(SIG);

/** Width/height from the IHDR without decoding. */
export const pngSize = (buf) => ({ width: buf.readUInt32BE(16), height: buf.readUInt32BE(20) });

/** Decode to { width, height, data: Uint8Array RGBA8 }. */
export function decodePng(buf) {
  if (!isPng(buf)) throw Error('not a PNG');
  let off = 8;
  let ihdr;
  let palette;
  let trns;
  const idat = [];
  while (off < buf.length) {
    const len = buf.readUInt32BE(off);
    const type = buf.toString('latin1', off + 4, off + 8);
    const body = buf.subarray(off + 8, off + 8 + len);
    if (type === 'IHDR')
      ihdr = {
        width: body.readUInt32BE(0),
        height: body.readUInt32BE(4),
        depth: body[8],
        color: body[9],
        interlace: body[12],
      };
    else if (type === 'PLTE') palette = body;
    else if (type === 'tRNS') trns = body;
    else if (type === 'IDAT') idat.push(body);
    else if (type === 'IEND') break;
    off += 12 + len;
  }
  const { width, height, depth, color, interlace } = ihdr;
  if (interlace) throw Error('interlaced PNG not supported');
  const channels = { 0: 1, 2: 3, 3: 1, 4: 2, 6: 4 }[color];
  const bpp = Math.max(1, (channels * depth) >> 3);
  const stride = Math.ceil((width * channels * depth) / 8);
  const raw = zlib.inflateSync(Buffer.concat(idat));
  const rows = Buffer.alloc(stride * height);
  let prev = Buffer.alloc(stride);
  for (let y = 0; y < height; y++) {
    const f = raw[y * (stride + 1)];
    const line = raw.subarray(y * (stride + 1) + 1, (y + 1) * (stride + 1));
    const out = rows.subarray(y * stride, (y + 1) * stride);
    for (let i = 0; i < stride; i++) {
      const a = i >= bpp ? out[i - bpp] : 0;
      const b = prev[i];
      const c = i >= bpp ? prev[i - bpp] : 0;
      let v = line[i];
      if (f === 1) v += a;
      else if (f === 2) v += b;
      else if (f === 3) v += (a + b) >> 1;
      else if (f === 4) {
        const p = a + b - c;
        const pa = Math.abs(p - a), pb = Math.abs(p - b), pc = Math.abs(p - c);
        v += pa <= pb && pa <= pc ? a : pb <= pc ? b : c;
      }
      out[i] = v & 0xff;
    }
    prev = out;
  }
  const data = new Uint8Array(width * height * 4);
  const sample = (row, index) => {
    // index-th sample in the row at this bit depth
    if (depth === 8) return row[index];
    if (depth === 16) return row[index * 2];
    const perByte = 8 / depth;
    const byte = row[Math.floor(index / perByte)];
    const shift = 8 - depth * ((index % perByte) + 1);
    return (byte >> shift) & ((1 << depth) - 1);
  };
  const scale = depth < 8 && color !== 3 ? 255 / ((1 << depth) - 1) : 1;
  for (let y = 0; y < height; y++) {
    const row = rows.subarray(y * stride, (y + 1) * stride);
    for (let x = 0; x < width; x++) {
      const o = (y * width + x) * 4;
      if (color === 3) {
        const p = sample(row, x);
        data[o] = palette[p * 3];
        data[o + 1] = palette[p * 3 + 1];
        data[o + 2] = palette[p * 3 + 2];
        data[o + 3] = trns && p < trns.length ? trns[p] : 255;
      } else if (color === 0 || color === 4) {
        const g = Math.round(sample(row, x * channels) * scale);
        data[o] = data[o + 1] = data[o + 2] = g;
        data[o + 3] = color === 4 ? sample(row, x * channels + 1) : 255;
        if (color === 0 && trns && depth === 8 && g === trns.readUInt16BE(0)) data[o + 3] = 0;
      } else {
        data[o] = sample(row, x * channels);
        data[o + 1] = sample(row, x * channels + 1);
        data[o + 2] = sample(row, x * channels + 2);
        data[o + 3] = color === 6 ? sample(row, x * channels + 3) : 255;
      }
    }
  }
  return { width, height, data };
}

function chunk(type, body) {
  const head = Buffer.alloc(8);
  head.writeUInt32BE(body.length, 0);
  head.write(type, 4, 'latin1');
  const crc = Buffer.alloc(4);
  crc.writeUInt32BE(crc32(Buffer.concat([head.subarray(4), body])), 0);
  return Buffer.concat([head, body, crc]);
}

/** Encode RGBA8 (deterministic: filter 0, zlib level 9). */
export function encodePng({ width, height, data }) {
  const ihdr = Buffer.alloc(13);
  ihdr.writeUInt32BE(width, 0);
  ihdr.writeUInt32BE(height, 4);
  ihdr[8] = 8;
  ihdr[9] = 6;
  const raw = Buffer.alloc((width * 4 + 1) * height);
  for (let y = 0; y < height; y++)
    Buffer.from(data.buffer, data.byteOffset + y * width * 4, width * 4).copy(raw, y * (width * 4 + 1) + 1);
  return Buffer.concat([
    SIG,
    chunk('IHDR', ihdr),
    chunk('IDAT', zlib.deflateSync(raw, { level: 9 })),
    chunk('IEND', Buffer.alloc(0)),
  ]);
}

/** Crop a rectangle. */
export function crop(img, x0, y0, w, h) {
  const data = new Uint8Array(w * h * 4);
  for (let y = 0; y < h; y++)
    data.set(img.data.subarray(((y0 + y) * img.width + x0) * 4, ((y0 + y) * img.width + x0 + w) * 4), y * w * 4);
  return { width: w, height: h, data };
}

/**
 * Largest integer k ≥ 1 such that the image is made of uniform k×k blocks (offset 0): an image
 * that was nearest-neighbour upscaled by k. 1 = already at its native pixel grid.
 */
export function blockFactor(img) {
  const same = (a, b) =>
    img.data[a] === img.data[b] &&
    img.data[a + 1] === img.data[b + 1] &&
    img.data[a + 2] === img.data[b + 2] &&
    img.data[a + 3] === img.data[b + 3];
  const uniform = (k) => {
    if (img.width % k || img.height % k) return false;
    for (let y = 0; y < img.height; y++)
      for (let x = 0; x < img.width; x++) {
        const bx = x - (x % k), by = y - (y % k);
        if (!same((y * img.width + x) * 4, (by * img.width + bx) * 4)) return false;
      }
    return true;
  };
  for (let k = Math.min(img.width, img.height, 16); k >= 2; k--) if (uniform(k)) return k;
  return 1;
}

/** Nearest-neighbour downsample by an exact block factor (lossless for block-upscaled art). */
export function downsample(img, k) {
  const width = img.width / k, height = img.height / k;
  const data = new Uint8Array(width * height * 4);
  for (let y = 0; y < height; y++)
    for (let x = 0; x < width; x++)
      data.set(img.data.subarray(((y * k) * img.width + x * k) * 4, ((y * k) * img.width + x * k) * 4 + 4), (y * width + x) * 4);
  return { width, height, data };
}

/** Bounding box of pixels with alpha ≥ 128, or null. */
export function opaqueBox(img, threshold = 128) {
  let x0 = Infinity, y0 = Infinity, x1 = -1, y1 = -1;
  for (let y = 0; y < img.height; y++)
    for (let x = 0; x < img.width; x++)
      if (img.data[(y * img.width + x) * 4 + 3] >= threshold) {
        if (x < x0) x0 = x;
        if (y < y0) y0 = y;
        if (x + 1 > x1) x1 = x + 1;
        if (y + 1 > y1) y1 = y + 1;
      }
  return x1 < 0 ? null : { x0, y0, x1, y1 };
}

/** Feet point: mean x of opaque pixels on the lowest two opaque rows, y = bottom edge. */
export function feetPoint(img) {
  const b = opaqueBox(img);
  if (!b) return null;
  let sum = 0, n = 0;
  for (let y = b.y1 - 2; y < b.y1; y++)
    for (let x = 0; x < img.width; x++)
      if (img.data[(y * img.width + x) * 4 + 3] >= 128) {
        sum += x;
        n++;
      }
  return { x: Math.round(sum / n), y: b.y1 };
}

/** True when every pixel of column x is (near) transparent. */
export function columnClear(img, x) {
  for (let y = 0; y < img.height; y++) if (img.data[(y * img.width + x) * 4 + 3] >= 16) return false;
  return true;
}

/** Fraction of pixels that are fully opaque (a flat baked background reads ~1). */
export function opaqueFraction(img) {
  let n = 0;
  for (let i = 3; i < img.data.length; i += 4) if (img.data[i] === 255) n++;
  return n / (img.width * img.height);
}
