// The canonical approved-art layout (docs/ASSETS.md): paths, metadata files and the manifest.
// Shared by scripts/art-sync.mjs and scripts/approved-art-check.mjs.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { fileURLToPath } from 'node:url';
import { decodePng, feetPoint } from './png.mjs';

export const REPO = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..');
export const APPROVED = path.join(REPO, 'assets', 'approved');
export const MANIFEST = path.join(APPROVED, 'approved.json');
export const REGEN_QUEUE = path.join(APPROVED, 'regen-queue.json');
export const SCHEMA = 'chirp-approved-art/2';

/** lowercase snake_case id: `feeder.cedar` -> `feeder_cedar`. */
export const snake = (id) => id.toLowerCase().replace(/[^a-z0-9]+/g, '_').replace(/^_|_$/g, '');
export const pad = (n) => String(n).padStart(2, '0');
export const birdDir = (species) => `birds/${species}`;
export const canonPath = (species) => `birds/${species}/canon.png`;
export const clipDir = (species, action, variant = 'v1') => `birds/${species}/clips/${action}/${variant}`;
export const framePath = (species, action, variant, index) =>
  `${clipDir(species, action, variant)}/${pad(index + 1)}.png`;
export const objectDir = (objectId) => `objects/${snake(objectId)}`;
export const objectPath = (objectId, variant) => `${objectDir(objectId)}/${variant}.png`;

/** Actions that play once and hand back to idle; every other clip loops. */
const ONCE = new Set(['blink', 'look', 'takeoff', 'landing']);
export const loopFor = (action) => !ONCE.has(action);

export const sha256 = (bytes) => crypto.createHash('sha256').update(bytes).digest('hex');

/** First date written in a source path (20261017 or 2026-10-17), as YYYY-MM-DD. */
export function dateFromPath(p) {
  const m = String(p ?? '').match(/(20\d\d)-?([01]\d)-?([0-3]\d)/);
  return m ? `${m[1]}-${m[2]}-${m[3]}` : null;
}

/** Write only when the bytes differ (idempotent runs leave files and mtimes alone). */
export function writeIfChanged(abs, bytes) {
  const buf = Buffer.isBuffer(bytes) ? bytes : Buffer.from(bytes);
  if (fs.existsSync(abs) && fs.readFileSync(abs).equals(buf)) return false;
  fs.mkdirSync(path.dirname(abs), { recursive: true });
  fs.writeFileSync(abs, buf);
  return true;
}
export const json = (value) => JSON.stringify(value, null, 2) + '\n';

/** File record for the manifest. */
export function fileRecord(rel, bytes) {
  const img = decodePng(bytes);
  return { path: rel, sha256: sha256(bytes), width: img.width, height: img.height };
}

/**
 * clip.json for one clip variant. `anchor` is the feet point of frame 01 (mean x of the lowest two
 * opaque rows, y = the row below them) in this clip's own pixels; `groundRow` is its y.
 */
export function clipJson({ action, frames, fps = null, frameMs = null }) {
  const first = frames[0];
  const feet = feetPoint(first);
  return {
    action,
    frames: frames.length,
    canvas: { width: first.width, height: first.height },
    ...(frameMs ? { frameMs } : { fps: fps ?? 8 }),
    loop: loopFor(action),
    anchor: feet,
    groundRow: feet ? feet.y : null,
    events: {},
  };
}

export function readManifest() {
  if (!fs.existsSync(MANIFEST)) return { schema: SCHEMA, layout: 'docs/ASSETS.md', entries: [] };
  const m = JSON.parse(fs.readFileSync(MANIFEST, 'utf8'));
  if (m.schema !== SCHEMA)
    throw Error(`approved.json is not ${SCHEMA}; migrate it to the canonical layout first (docs/ASSETS.md).`);
  return m;
}

/** Stable order: kind, then species/object, then action, then variant. */
export function sortEntries(entries) {
  return [...entries].sort((a, b) => a.id.localeCompare(b.id));
}
