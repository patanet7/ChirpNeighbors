// The asset system layout and id grammar (docs/ASSETS.md, design: asset-system-design.md).
// Extends approved-layout.mjs (approved/) with candidates/, inbox/, references/, regions/ and the
// index (assets/index.jsonl). Pure functions only; the commands live in scripts/assets.mjs.
import path from 'node:path';
import { REPO, APPROVED } from './approved-layout.mjs';
import { isPng, decodePng } from './png.mjs';

export * from './approved-layout.mjs';

export const ASSETS = path.join(REPO, 'assets');
export const INDEX = path.join(ASSETS, 'index.jsonl');
export const CANDIDATES = path.join(ASSETS, 'candidates');
export const INBOX = path.join(ASSETS, 'inbox');
export const REFERENCES = path.join(ASSETS, 'references');
export const REGIONS = path.join(ASSETS, 'regions');
/** Folders under assets/ where an image may live once the old tree is gone (PR 3). */
export const ART_HOMES = ['approved', 'candidates', 'inbox', 'references'];
export { APPROVED };
export const INDEX_SCHEMA = 'chirp-assets/1';

// ---------------------------------------------------------------- vocabulary
export const KINDS = ['birds', 'objects', 'plants', 'scenes', 'packs'];
/** The 15 bird slots: the canon still plus 14 clip acts. */
export const ACTS = ['idle', 'blink', 'look', 'hop', 'walk', 'takeoff', 'flight', 'landing', 'feed', 'drink', 'bathe', 'preen', 'sing', 'sleep'];
export const BIRD_SLOTS = ['canon', ...ACTS.map((a) => `clips/${a}`)];
export const FORMS = ['young', 'mature', 'potted', 'hedge'];
export const SEASONS = ['spring', 'summer', 'autumn', 'winter', 'all'];
/** Plant/object/scene states. bloom..wet are the design's; leaves, rain, fog and wind are the
 * weather overlays and ground states the review page already has slots for. Omitted = base. */
export const STATES = ['bloom', 'fruit', 'dry', 'bare', 'snow', 'wet', 'leaves', 'rain', 'fog', 'wind'];
export const LAYERS = ['composite', 'background', 'ground', 'foreground', 'overlay'];
export const DEPTHS = ['far', 'mid', 'near', 'ground', 'all'];
export const STATUSES = ['wanted', 'new', 'candidate', 'approved', 'rejected', 'retired'];

const NAME = /^[a-z0-9_]+$/;
const VERSION = /^(v[1-9]\d*|c[0-9a-f]{8})$/;

/** Candidate version from a sha256: `c` + first 8 hex. */
export const candidateVersion = (sha256) => `c${String(sha256).slice(0, 8)}`;

/**
 * Parse an asset id. Returns { id, kind, name, subject, slot, version, ... } or throws.
 *   id      = subject ["/" slot] ["/" version]
 *   subject = kind "/" name
 *   slot    = birds: canon | clips/<act>; plants: form.season[.state]; objects: [state];
 *             scenes: season[.state]/layer
 *   version = vN (approved) | c<sha8> (candidate)
 * `inbox/c<sha8>` (art nobody can name yet) and `evidence/c<sha8>` (previews, not art) are the
 * two id spaces outside the kinds.
 */
export function parseId(id) {
  const parts = String(id).split('/');
  const fail = (why) => {
    throw Error(`bad id "${id}": ${why}`);
  };
  if (parts[0] === 'inbox' || parts[0] === 'evidence') {
    if (parts.length !== 2 || !/^c[0-9a-f]{8}$/.test(parts[1])) fail(`${parts[0]}/c<sha8>`);
    return { id, kind: parts[0], name: null, subject: null, slot: null, version: parts[1] };
  }
  const [kind, name, ...rest] = parts;
  if (!KINDS.includes(kind)) fail(`kind must be one of ${KINDS.join(', ')}`);
  if (!name || !NAME.test(name)) fail('name must be [a-z0-9_]+');
  const out = { id, kind, name, subject: `${kind}/${name}`, slot: null, version: null };
  if (rest.length && VERSION.test(rest[rest.length - 1])) out.version = rest.pop();
  if (!rest.length) return out;
  if (kind === 'birds') {
    if (rest.length === 1 && rest[0] === 'canon') out.act = 'canon';
    else if (rest.length === 2 && rest[0] === 'clips' && ACTS.includes(rest[1])) out.act = rest[1];
    else fail('bird slot is canon or clips/<act>');
  } else if (kind === 'plants') {
    if (rest.length !== 1) fail('plant slot is form.season[.state]');
    const [form, season, state, ...extra] = rest[0].split('.');
    if (!FORMS.includes(form)) fail(`form must be one of ${FORMS.join(', ')}`);
    if (!SEASONS.includes(season)) fail(`season must be one of ${SEASONS.join(', ')}`);
    if (state !== undefined && !STATES.includes(state)) fail(`state must be one of ${STATES.join(', ')}`);
    if (extra.length) fail('plant slot has at most three parts');
    Object.assign(out, { form, season, state: state ?? null });
  } else if (kind === 'objects') {
    if (rest.length !== 1 || !STATES.includes(rest[0])) fail('object slot is a state');
    out.state = rest[0];
  } else if (kind === 'scenes') {
    if (rest.length !== 2) fail('scene slot is season[.state]/layer');
    const [season, state, ...extra] = rest[0].split('.');
    if (!SEASONS.includes(season)) fail(`season must be one of ${SEASONS.join(', ')}`);
    if (state !== undefined && !STATES.includes(state)) fail(`state must be one of ${STATES.join(', ')}`);
    if (extra.length) fail('scene season has at most two parts');
    if (!LAYERS.includes(rest[1])) fail(`layer must be one of ${LAYERS.join(', ')}`);
    Object.assign(out, { season, state: state ?? null, layer: rest[1] });
  } else fail(`${kind} have no slots`);
  out.slot = rest.join('/');
  return out;
}

export const isValidId = (id) => {
  try {
    parseId(id);
    return true;
  } catch {
    return false;
  }
};

/** The slot an id belongs to (id without its version). */
export const slotOf = (id) => {
  const p = parseId(id);
  return p.slot ? `${p.subject}/${p.slot}` : p.subject;
};

export const plantSlot = (name, form, season = 'all', state = null) =>
  `plants/${name}/${form}.${season}${state ? `.${state}` : ''}`;
export const sceneSlot = (yard, season, state, layer) =>
  `scenes/${yard}/${season}${state ? `.${state}` : ''}/${layer}`;

// ---------------------------------------------------------------- state suffixes
const STATE_WORDS = {
  healthy: 'base', base: 'base', evergreen: 'base', static: 'base',
  dry: 'dry', spent: 'dry', stress: 'dry', stressed: 'dry', drought: 'dry', wilted: 'dry', dormant_dry: 'dry',
  bloom: 'bloom', blooming: 'bloom', flowering: 'bloom', flower: 'bloom', flowers: 'bloom',
  fruit: 'fruit', fruiting: 'fruit', berries: 'fruit', berry: 'fruit', seeding: 'fruit', seedheads: 'fruit',
  bare: 'bare', leafless: 'bare', dormant: 'bare',
  snow: 'snow', snowy: 'snow', wet: 'wet', rain: 'rain', fog: 'fog', wind: 'wind', leaves: 'leaves',
};
const SEASON_WORDS = { spring: 'spring', summer: 'summer', autumn: 'autumn', fall: 'autumn', winter: 'winter' };

/**
 * State and season from a file name's `__suffix` (`arrowwood__dry_spent.png` -> dry,
 * `x__mild_dry_stress` -> dry, `y__healthy_seed_morphology_r01` -> base). The first word that
 * names a state wins; season words set the season. Without `__`, only a final `-word`/`_word`
 * that is exactly a state or season word counts (`maple-autumn-foliage` -> no: last word is
 * foliage). Returns { state: null | 'base' | STATE, season: null | SEASON, suffix }.
 */
export function parseStateSuffix(file) {
  const base = path.basename(String(file)).replace(/\.[a-z0-9]+$/i, '').toLowerCase();
  const at = base.indexOf('__');
  let words;
  let suffix = null;
  if (at >= 0) {
    suffix = base.slice(at + 2);
    words = suffix.split(/[_\-.]+/).filter(Boolean);
  } else {
    const last = base.split(/[-_.]+/).filter(Boolean).pop();
    words = last && (STATE_WORDS[last] || SEASON_WORDS[last]) ? [last] : [];
    if (words.length) suffix = last;
  }
  let state = null;
  let season = null;
  for (const w of words) {
    if (!state && STATE_WORDS[w]) state = STATE_WORDS[w];
    if (!season && SEASON_WORDS[w]) season = SEASON_WORDS[w];
  }
  return { state, season, suffix };
}

// ---------------------------------------------------------------- art vs evidence
/** PNG chunk types present (without decoding pixels). */
function pngChunks(buf) {
  const types = new Set();
  let off = 8;
  while (off + 8 <= buf.length) {
    const len = buf.readUInt32BE(off);
    const type = buf.toString('latin1', off + 4, off + 8);
    types.add(type);
    if (type === 'IHDR') types.color = buf[off + 8 + 9];
    if (type === 'IEND') break;
    off += 12 + len;
  }
  return types;
}

/**
 * What classifyImage needs from the bytes: decodable, animated (APNG acTL), whether there is an
 * alpha channel (colour type 4/6 or tRNS), and the share of pixels with alpha < 250.
 */
export function imageInfo(bytes) {
  if (!isPng(bytes)) return { decodable: false };
  const chunks = pngChunks(bytes);
  const hasAlphaChannel = chunks.color === 4 || chunks.color === 6 || chunks.has('tRNS');
  const info = { decodable: true, animated: chunks.has('acTL'), hasAlphaChannel };
  if (!hasAlphaChannel) return { ...info, transparentFraction: 0 };
  try {
    const img = decodePng(bytes);
    let clear = 0;
    for (let i = 3; i < img.data.length; i += 4) if (img.data[i] < 250) clear++;
    return { ...info, width: img.width, height: img.height, transparentFraction: clear / (img.width * img.height) };
  } catch {
    return { decodable: false };
  }
}

const EVIDENCE_EXT = {
  gif: 'animated GIF preview',
  apng: 'animated PNG preview',
  jpg: 'JPEG has no alpha (photo or opaque render)',
  jpeg: 'JPEG has no alpha (photo or opaque render)',
  svg: 'vector diagram, not raster art',
  webp: 'WebP preview',
};
/** Words that mark a preview/QA image, matched as whole words of the file name or a folder name. */
const EVIDENCE_NAME_WORDS = new Set(['contact', 'contactsheet', 'montage', 'compare', 'comparison', 'screenshot', 'collage', 'lineup', 'overview', 'thumb', 'thumbnail', 'grid', 'board', 'storyboard', 'before', 'after', 'diff', 'debug', 'qa', 'guide', 'mask', 'matte', 'silhouette', 'onion', 'heatmap', 'chart']);
const EVIDENCE_DIR_WORDS = new Set(['screenshots', 'screenshot', 'contact', 'contacts', 'contact-sheets', 'contact_sheets', 'thumbs', 'index-thumbs', 'qa', 'debug', 'masks', 'mask', 'overlays', 'diffs', 'compare', 'comparison', 'comparisons', 'guides', 'embedded', 'zoom', 'inspection']);
/** Folders whose opaque images are renders of something, not the art itself. */
const PREVIEW_DIR_WORDS = new Set(['previews', 'preview', 'review', 'reviews', 'inspect', 'inspection', 'cohort', 'preflight', 'decoded']);
/** Opaque display variants of a yard (greyscale, mobile crop, light/dark checks). */
const DISPLAY_WORDS = new Set(['gray', 'grey', 'greyscale', 'grayscale', 'mobile', '16x9', 'light', 'dark', 'normal', 'caption']);
/** Folder or file words that say an opaque image is a background/scene (scenes are opaque). */
const SCENE_WORDS = new Set(['backgrounds', 'background', 'scenes', 'scene', 'sky', 'seasons', 'yards', 'yard', 'terrain', 'backdrop', 'foreground', 'ground', 'coastal', 'oak', 'courtyard', 'inland', 'patio', 'mediterranean', 'canyon']);
const words = (s) => s.split(/[-_.\s]+/).filter(Boolean);

/**
 * Art or evidence, and why. `info` is what png.mjs could read: { decodable, animated,
 * hasAlphaChannel, transparentFraction } (transparentFraction = share of pixels with alpha < 250).
 * Decided by file type, alpha and the file/folder name; never by the subject.
 */
export function classifyImage(file, info = {}) {
  const p = String(file).toLowerCase();
  const ext = p.split('.').pop();
  const base = path.posix.basename(p).replace(/\.[a-z0-9]+$/, '');
  const dirs = path.posix.dirname(p).split('/');
  const dirWords = dirs.filter((seg) => seg !== 'regional-yard-packs').flatMap(words);
  const baseWords = words(base);
  if (EVIDENCE_EXT[ext]) return { class: 'evidence', why: EVIDENCE_EXT[ext] };
  if (ext !== 'png') return { class: 'evidence', why: `.${ext} is not an art format` };
  if (info.animated) return { class: 'evidence', why: 'animated PNG preview (the frames are the art)' };
  if (info.decodable === false) return { class: 'evidence', why: 'not a decodable PNG' };
  if (/review[-_]only/.test(base)) return { class: 'evidence', why: 'file name says REVIEW-ONLY (a review crop, not art)' };
  const n = baseWords.find((w) => EVIDENCE_NAME_WORDS.has(w));
  if (n) return { class: 'evidence', why: `file name says "${n}" (preview/QA image, not art)` };
  const d = dirs.find((seg) => EVIDENCE_DIR_WORDS.has(seg) || /[-_]masks?$/.test(seg));
  if (d) return { class: 'evidence', why: `in a "${d}" folder (QA image, not art)` };
  const opaque = info.hasAlphaChannel === false || (info.transparentFraction ?? 1) < 0.01;
  if (!opaque) return { class: 'art', why: 'transparent PNG (RGBA cut-out)' };
  const pd = dirs.find((seg) => PREVIEW_DIR_WORDS.has(seg));
  if (pd) return { class: 'evidence', why: `opaque render in a "${pd}" folder` };
  const dw = baseWords.find((w) => DISPLAY_WORDS.has(w));
  if (dw) return { class: 'evidence', why: `opaque display variant ("${dw}")` };
  const sw = [...dirWords.filter((w) => w !== 'ground'), ...baseWords].find((w) => SCENE_WORDS.has(w));
  if (sw) return { class: 'art', why: `opaque background/scene ("${sw}" in its path)` };
  return { class: 'evidence', why: info.hasAlphaChannel === false ? 'opaque render (no alpha channel)' : 'opaque render (alpha channel all solid)' };
}

// ---------------------------------------------------------------- legacy review slot ids
/** Bird action names used by the review page; `canon` is the still. */
const REVIEW_BIRD = new RegExp(`^([a-z0-9_]+)\\.(canon|${ACTS.join('|')})$`);
/** Review slot ids that were wrong names: plant.healthy and plant.corrected are coast live oak
 * canopies (plants/candidates.json: "the same canopies under wrong slot names"). */
export const CORRECTED_REVIEW_SLOTS = {
  'plant.healthy': { slot: 'plants/coast_live_oak/mature.all', part: 'canopy', why: 'oak canopy filed under a wrong slot name' },
  'plant.corrected': { slot: 'plants/coast_live_oak/mature.all', part: 'canopy', why: 'oak canopy filed under a wrong slot name' },
};
/** Review yards that are the same yard under the app's subject name. */
export const YARD_ALIASES = { coastal_urban: 'coastal', inland_canyon: 'inland', managed_patio: 'patio' };

/**
 * New slot id for a review-page slot id (the one mapping table, design §1). `plantForm(name)`
 * returns the form for a plant (default mature). Returns null when the id is not recognised.
 */
export function reviewToSlot(reviewId, plantForm = () => 'mature') {
  if (CORRECTED_REVIEW_SLOTS[reviewId]) return CORRECTED_REVIEW_SLOTS[reviewId].slot;
  let m = reviewId.match(REVIEW_BIRD);
  if (m) return m[2] === 'canon' ? `birds/${m[1]}/canon` : `birds/${m[1]}/clips/${m[2]}`;
  m = reviewId.match(/^object\.([a-z0-9_.]+)$/);
  if (m) return `objects/${m[1].replace(/\./g, '_')}`;
  m = reviewId.match(/^plant\.([a-z0-9_]+?)(?:_(spring|summer|autumn|winter))?$/);
  if (m) return plantSlot(m[1], plantForm(m[1]), m[2] ?? 'all');
  m = reviewId.match(/^scene\.([a-z0-9_]+)\.(spring|summer|autumn|winter)$/);
  if (m) return sceneSlot(YARD_ALIASES[m[1]] ?? m[1], m[2], null, 'composite');
  m = reviewId.match(/^scene\.([a-z0-9_]+)\.(composite|background|ground|foreground)$/);
  if (m) return sceneSlot(YARD_ALIASES[m[1]] ?? m[1], 'all', null, m[2]);
  m = reviewId.match(/^scene\.concept\.([a-z0-9_]+)$/);
  if (m) return sceneSlot(`concept_${m[1]}`, 'all', null, 'composite');
  m = reviewId.match(/^season\.(spring|summer|autumn|winter)$/);
  if (m) return sceneSlot('seasonal', m[1], null, 'composite');
  m = reviewId.match(/^weather\.(rain|snow|wind|fog)$/);
  if (m) return sceneSlot('weather', 'all', m[1], 'overlay');
  return null;
}

// ---------------------------------------------------------------- index rows
/** Stable order: the header (`#`) first, then by id. */
export const sortRows = (rows) => [...rows].sort((a, b) => (a.id < b.id ? -1 : a.id > b.id ? 1 : 0));

/** Rows that are a slot (objects' subject row is also their base slot). */
export const isSlotRow = (r) => r.row === 'slot' || (r.row === 'subject' && r.kind === 'objects');

/** One JSONL line per row, keys in a stable order. */
const KEY_ORDER = ['id', 'row', 'kind', 'name', 'label', 'status', 'slot'];
export function rowLine(row) {
  const keys = [...KEY_ORDER.filter((k) => k in row), ...Object.keys(row).filter((k) => !KEY_ORDER.includes(k)).sort()];
  const o = {};
  for (const k of keys) if (row[k] !== undefined) o[k] = row[k];
  return JSON.stringify(o);
}
