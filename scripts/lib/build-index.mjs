// `assets index`: (re)builds assets/index.jsonl. Approved art comes from approved.json, owner
// "make new" verdicts from regen-queue.json, stray files from a scan of approved/. Subjects and
// wanted slots come from the rows already in the index plus optional seeds:
//   --app <birdsong-yard-sprites checkout>   object/plant ids in the app catalog (read at origin/main)
//   --plants <plants/candidates.json>        plant species, tags and state slots
//   --review <review-data.json>              bird species and the review page's slot ids
// Seeds are only needed once; afterwards the index is the truth and keeps those rows.
import fs from 'node:fs';
import path from 'node:path';
import { execFileSync } from 'node:child_process';
import {
  APPROVED, readManifest, REGEN_QUEUE, snake, BIRD_SLOTS, ACTS, candidateVersion, plantSlot, sceneSlot,
  reviewToSlot, CORRECTED_REVIEW_SLOTS, isSlotRow, parseId, parseStateSuffix, sha256,
} from './layout.mjs';
import { readIndex } from './index-io.mjs';
import { pngSize } from './png.mjs';

const IMAGE = /\.(png|apng|gif|jpe?g|webp|svg)$/i;
const walk = (dir) =>
  fs.existsSync(dir)
    ? fs.readdirSync(dir, { withFileTypes: true }).flatMap((d) => (d.isDirectory() ? walk(path.join(dir, d.name)) : [path.join(dir, d.name)]))
    : [];

// ------------------------------------------------------------------ approved.json -> art rows
export function approvedArtId(e) {
  if (e.kind === 'bird-canon') return `birds/${e.species}/canon/v1`;
  if (e.kind === 'scene') return `${e.id}/v1`;
  return e.id; // bird clips and objects already follow subject/slot/vN
}

export function approvedArtRows(manifest) {
  return manifest.entries.map((e) => {
    const id = approvedArtId(e);
    const row = {
      id,
      row: 'art',
      status: 'approved',
      slot: id.replace(/\/v\d+$/, ''),
      files: e.files,
      default: e.kind === 'bird-canon' || e.kind === 'scene' ? true : !!e.default,
      from: e.source?.candidate ? `c${e.source.candidate}` : undefined,
      made: { from: e.source?.path ?? null, pack: e.source?.pack ?? null, on: e.generated ?? null, prompt: e.prompt ?? null },
      decidedAt: e.approved ?? null,
      review: e.reviewSlot ?? null,
      note: e.decision ?? e.note ?? undefined,
      displayCrop: e.displayCrop,
    };
    if (e.kind === 'bird-clip') row.frames = e.files.length;
    return row;
  });
}

// ------------------------------------------------------------------ seeds
function gitShow(repo, ref, file) {
  return execFileSync('git', ['-C', repo, 'show', `${ref}:${file}`], { encoding: 'utf8', maxBuffer: 64 << 20 });
}

/** Plant form (slot grammar) and habit (tag) from the plant batch's free-text form. */
export function plantFormHabit(form, origin) {
  const f = String(form ?? '').toLowerCase();
  const potted = origin === 'houseplant' || /pot|container/.test(f);
  let habit = null;
  if (/\btree\b/.test(f) && !/shrub/.test(f)) habit = 'tree';
  else if (/shrub/.test(f)) habit = 'shrub';
  else if (/grass/.test(f)) habit = 'grass';
  else if (/succulent/.test(f)) habit = 'succulent';
  else if (/perennial|wildflower/.test(f)) habit = 'perennial';
  return { form: potted ? 'potted' : 'mature', habit };
}

const SD_NATIVE_RANGE = ['epa3:85', 'epa3:8'];
const SD_NATIVE_SOURCE =
  'plants/candidates.json lists it as "native" in the San Diego plant batch; every San Diego native maps to the Southern California Coast (EPA III 85) and Southern California Mountains (EPA III 8) ecoregions (lead, 2026-10-25). Narrow per species when range data is researched.';
const CULTIVATION = { native: 'wild', nursery: 'nursery', houseplant: 'houseplant' };

/** Variant state words in plants/candidates.json -> slot season/state (null = not a slot, a part). */
export function plantVariantSlot(v) {
  const s = String(v.state ?? '').toLowerCase();
  if (v.kind === 'component' || /canopy|wind-module/.test(s)) return { season: 'all', state: null, part: s === 'wind-module' ? 'wind-module' : 'canopy' };
  if (['spring', 'summer', 'autumn', 'winter'].includes(s)) return { season: s, state: s === 'winter' ? 'bare' : null };
  const p = parseStateSuffix(`x__${s}`);
  return { season: 'all', state: p.state && p.state !== 'base' ? p.state : null, part: s === 'wind' ? 'wind-frames' : undefined };
}

export function plantSeed(doc) {
  const rows = [];
  for (const sp of doc.species) {
    const name = sp.slot.replace(/^plant\./, '');
    const { form, habit } = plantFormHabit(sp.form, sp.origin);
    const cultivation = CULTIVATION[sp.origin] ?? null;
    const needs = ['gives', 'food'];
    const subject = {
      id: `plants/${name}`,
      row: 'subject',
      kind: 'plants',
      name,
      label: sp.common,
      scientific: sp.scientific,
      cultivation,
      setting: sp.origin === 'houseplant' ? 'indoor' : 'yard',
      habit: habit ?? undefined,
      nativeRange: sp.origin === 'native' ? SD_NATIVE_RANGE : [],
      nativeRangeSource: sp.origin === 'native' ? SD_NATIVE_SOURCE : undefined,
      metres: sp.metres,
      potBakedIn: sp.potBakedIn || undefined,
    };
    if (sp.origin !== 'native') needs.unshift('nativeRange');
    if (!habit) needs.push('habit');
    subject.needs = needs;
    rows.push(subject);
    const slots = new Set([plantSlot(name, form)]);
    for (const v of sp.variants ?? []) {
      const { season, state } = plantVariantSlot(v);
      slots.add(plantSlot(name, form, season, state));
    }
    for (const id of slots) rows.push({ id, row: 'slot', review: sp.existingReviewSlot && id === plantSlot(name, form) ? [sp.slot] : [] });
  }
  return rows;
}

/** App catalog (canonical-yard-data.json at origin/main): objects and plants the game uses. */
export function appSeed(catalog, approvedObjects) {
  const rows = [];
  // approved/objects/<name>/object.json names the app id each version serves
  const byAppId = new Map();
  for (const [name, meta] of approvedObjects)
    for (const [v, info] of Object.entries(meta.variants ?? {})) if (info.appCatalogId) byAppId.set(info.appCatalogId, { name, v });
  const GIVES = { feeder: ['food'], bath: ['water'], perch: ['perch'], nest: ['cover'] };
  for (const o of catalog) {
    const fromApproved = String(o.sourcePath ?? '').match(/^assets\/approved\/objects\/([a-z0-9_]+)\/(v\d+)\.png$/);
    const hit = byAppId.get(o.id) ?? (fromApproved ? { name: fromApproved[1], v: fromApproved[2] } : null);
    const isPlant = String(o.assetId ?? '').startsWith('plant.');
    const kind = isPlant ? 'plants' : 'objects';
    const name = hit && !isPlant ? hit.name : snake(o.id);
    const row = {
      id: `${kind}/${name}`,
      row: 'subject',
      kind,
      name,
      label: hit ? undefined : o.label,
      app: { [o.id]: { uses: hit?.v ?? null, source: o.sourcePath ?? null, sha256: o.sourceSha256 ?? null, kind: o.kind, assetId: o.assetId } },
    };
    if (!isPlant && GIVES[o.kind]) row.gives = GIVES[o.kind];
    if (o.feederStyle) row.feeder = o.feederStyle;
    rows.push(row);
  }
  return rows;
}

/** Review page data: bird species, and every review slot id mapped through the legacy table. */
export function reviewSeed(review, plantForm) {
  const rows = [];
  const species = new Map();
  for (const s of review.slots) if (s.species) species.set(s.species, s.name ?? s.species);
  for (const [sp, label] of species) {
    rows.push({ id: `birds/${sp}`, row: 'subject', kind: 'birds', name: sp, label: String(label).replace(/\s*·.*$/, '') });
    for (const slot of BIRD_SLOTS) rows.push({ id: `birds/${sp}/${slot}`, row: 'slot', review: [`${sp}.${slot === 'canon' ? 'canon' : slot.slice(6)}`] });
  }
  const unmapped = [];
  for (const s of review.slots) {
    if (s.species) continue;
    const id = reviewToSlot(s.id, plantForm);
    if (!id) {
      unmapped.push(s.id);
      continue;
    }
    if (CORRECTED_REVIEW_SLOTS[s.id]) continue; // its art moves to the real slot; the id retires
    const p = parseId(id);
    if (p.kind === 'objects') rows.push({ id, row: 'subject', kind: 'objects', name: p.name, label: s.label, review: [s.id] });
    else {
      rows.push({ id: p.subject, row: 'subject', kind: p.kind, name: p.name });
      rows.push({ id, row: 'slot', review: [s.id] });
    }
  }
  return { rows, unmapped };
}

/** Painted yards: what approved/scenes/<yard> shows (read from the winter composites, 2026-10-25). */
export const YARDS = {
  coastal: { label: 'Coastal garden', landscape: ['coastal', 'urban'], fence: 'stucco_wall', ground: 'lawn', app: 'scene.san_diego_coastal_urban' },
  oak: { label: 'Oak shade', landscape: ['forest'], fence: 'none', ground: 'dirt', app: 'scene.san_diego_oak_riparian_shade_pocket', edging: 'fieldstone' },
  courtyard: { label: 'Courtyard', landscape: ['urban'], fence: 'stucco_wall', ground: 'flagstone', app: 'scene.san_diego_compact_marine_courtyard' },
  inland: { label: 'Inland canyon', landscape: ['valley', 'mountain'], fence: 'wire_ranch', ground: 'dirt', app: 'scene.san_diego_inland_canyon' },
  patio: { label: 'Patio with a view', landscape: ['coastal', 'urban'], fence: 'stucco_parapet', ground: 'tile', app: 'scene.san_diego_managed_patio' },
};
/** Weather and ground states every yard should have; wanted until art exists, so the gaps show. */
export const WEATHER_SLOTS = [
  ['winter', 'snow', 'snow on the far hills and mountains, frost on the ground'],
  ['winter', 'wet', 'rain-soaked ground and walls, puddles'],
  ['spring', 'wet', 'spring rain, wet ground'],
  ['summer', 'dry', 'dry, gold grass and dusty ground'],
  ['autumn', 'leaves', 'autumn leaf litter on the ground'],
];
const LAYER_DEPTH = { composite: 'all', background: 'far', ground: 'ground', foreground: 'near', overlay: 'all' };

export function sceneSeed() {
  const rows = [];
  for (const [yard, t] of Object.entries(YARDS)) {
    rows.push({
      id: `scenes/${yard}`,
      row: 'subject',
      kind: 'scenes',
      name: yard,
      label: t.label,
      landscape: t.landscape,
      ecoregions: ['epa3:85'],
      ecoregionsSource: `painted San Diego yard (app ${t.app})`,
      fence: t.fence,
      ground: t.ground,
      edging: t.edging,
      layers: Object.fromEntries(Object.entries(LAYER_DEPTH).filter(([l]) => l !== 'overlay').map(([l, depth]) => [l, { depth }])),
    });
    for (const season of ['spring', 'summer', 'autumn', 'winter']) rows.push({ id: sceneSlot(yard, season, null, 'composite'), row: 'slot' });
    for (const [season, state, note] of WEATHER_SLOTS) rows.push({ id: sceneSlot(yard, season, state, 'composite'), row: 'slot', note });
  }
  rows.push({ id: 'scenes/weather', row: 'subject', kind: 'scenes', name: 'weather', label: 'Weather overlays', layers: { overlay: { depth: 'all' } } });
  rows.push({ id: 'scenes/seasonal', row: 'subject', kind: 'scenes', name: 'seasonal', label: 'Seasonal plates (no yard yet)' });
  return rows;
}

// ------------------------------------------------------------------ merge + statuses
/** Merge seed rows into rows by id: arrays (review, app keys) union, other fields fill blanks. */
export function mergeRows(base, add) {
  const map = new Map(base.map((r) => [r.id, { ...r }]));
  for (const r of add) {
    const cur = map.get(r.id);
    if (!cur) {
      map.set(r.id, { ...r });
      continue;
    }
    for (const [k, v] of Object.entries(r)) {
      if (v === undefined) continue;
      if (k === 'review' || k === 'copies') cur[k] = [...new Set([...(cur[k] ?? []), ...v])];
      else if (k === 'app') cur.app = { ...(cur.app ?? {}), ...v };
      else if (k === 'row' && cur.row === 'subject' && v === 'slot') continue;
      else if (cur[k] === undefined || cur[k] === null || (Array.isArray(cur[k]) && !cur[k].length && k !== 'nativeRange')) cur[k] = v;
    }
  }
  return [...map.values()];
}

/** Every art row's slot and subject exist; slot status follows its art and the regen queue. */
export function settleStatuses(rows, regen = new Map()) {
  const byId = new Map(rows.map((r) => [r.id, r]));
  const ensure = (id) => {
    if (byId.has(id)) return;
    const p = parseId(id);
    if (!byId.has(p.subject)) {
      const r = { id: p.subject, row: 'subject', kind: p.kind, name: p.name };
      rows.push(r);
      byId.set(r.id, r);
    }
    if (id !== p.subject) {
      const r = { id, row: 'slot' };
      rows.push(r);
      byId.set(id, r);
    }
  };
  const art = new Map();
  for (const r of rows.filter((x) => x.row === 'art')) {
    if (!r.slot) continue;
    ensure(r.slot);
    if (!art.has(r.slot)) art.set(r.slot, []);
    art.get(r.slot).push(r);
  }
  for (const r of rows) {
    if (!isSlotRow(r)) continue;
    const a = art.get(r.id) ?? [];
    const g = regen.get(r.id);
    if (g) r.regen = g;
    else delete r.regen;
    r.status = a.some((x) => x.status === 'approved')
      ? 'approved'
      : g
        ? 'wanted'
        : a.some((x) => x.status === 'candidate')
          ? 'candidate'
          : 'wanted';
  }
  return rows;
}

/** Owner "make new" verdicts by new slot id. */
export function regenBySlot(queue, plantForm) {
  const out = new Map();
  for (const it of queue.items ?? []) {
    if (it.verdict !== 'regenerate') continue;
    const id = reviewToSlot(it.slot, plantForm);
    if (id) out.set(id, { decidedAt: it.decidedAt, note: it.note || it.reason || '' });
  }
  return out;
}

// ------------------------------------------------------------------ the command
export function buildIndex({ app, plants, review, existing = readIndex() } = {}) {
  const manifest = readManifest();
  let rows = existing.filter((r) => r.id !== '#' && !(r.row === 'art' && r.status === 'approved'));
  const approved = approvedArtRows(manifest);
  rows.push(...approved);
  const report = { seeds: [], unmapped: [], stray: [] };

  // plant forms known so far (for review ids -> plant slots)
  const plantDoc = plants ? JSON.parse(fs.readFileSync(plants, 'utf8')) : null;
  const forms = new Map();
  for (const r of rows) if (r.row === 'slot' && r.id.startsWith('plants/')) forms.set(parseId(r.id).name, parseId(r.id).form);
  if (plantDoc) for (const sp of plantDoc.species) forms.set(sp.slot.replace(/^plant\./, ''), plantFormHabit(sp.form, sp.origin).form);
  const plantForm = (name) => forms.get(name) ?? 'mature';

  const seeds = [];
  // approved objects and birds are subjects even with no other seed
  const approvedObjects = new Map();
  for (const dir of fs.existsSync(path.join(APPROVED, 'objects')) ? fs.readdirSync(path.join(APPROVED, 'objects')) : []) {
    const f = path.join(APPROVED, 'objects', dir, 'object.json');
    if (!fs.existsSync(f)) continue;
    const meta = JSON.parse(fs.readFileSync(f, 'utf8'));
    approvedObjects.set(dir, meta);
    const v1 = Object.values(meta.variants ?? {})[0];
    const GIVES = { feeder: ['food'], bath: ['water'], perch: ['perch'], nest: ['cover'] };
    seeds.push({ id: `objects/${dir}`, row: 'subject', kind: 'objects', name: dir, label: v1?.label, review: meta.reviewSlot ? [meta.reviewSlot] : [], gives: GIVES[meta.kind] });
  }
  for (const e of manifest.entries.filter((x) => x.kind === 'bird-canon' || x.kind === 'bird-clip')) {
    seeds.push({ id: `birds/${e.species}`, row: 'subject', kind: 'birds', name: e.species });
    for (const slot of BIRD_SLOTS) seeds.push({ id: `birds/${e.species}/${slot}`, row: 'slot', review: [`${e.species}.${slot === 'canon' ? 'canon' : slot.slice(6)}`] });
  }
  seeds.push(...sceneSeed());
  if (plantDoc) {
    seeds.push(...plantSeed(plantDoc));
    report.seeds.push(`plants: ${plantDoc.species.length} species from ${plants}`);
  }
  if (app) {
    const catalog = JSON.parse(gitShow(app, 'origin/main', 'src/lib/domain/canonical-yard-data.json'));
    const appRows = appSeed(catalog, approvedObjects);
    // a plant in the app gets its base slot
    for (const r of appRows) if (r.kind === 'plants') appRows.push({ id: plantSlot(r.name, plantForm(r.name)), row: 'slot' });
    seeds.push(...appRows);
    report.seeds.push(`app: ${catalog.length} catalog ids from ${app} (origin/main)`);
  }
  if (review) {
    const doc = JSON.parse(fs.readFileSync(review, 'utf8'));
    const { rows: rr, unmapped } = reviewSeed(doc, plantForm);
    seeds.push(...rr);
    report.unmapped = unmapped;
    report.seeds.push(`review: ${doc.slots.length} slots from ${review}`);
  }
  rows = mergeRows(rows, seeds);

  // stray files in approved/ (not in approved.json) become new art
  const listed = new Set(approved.flatMap((a) => a.files.map((f) => f.path)));
  for (const abs of walk(APPROVED)) {
    const rel = path.relative(APPROVED, abs).split(path.sep).join('/');
    if (!/\.(png|apng|gif|jpe?g|webp|svg)$/i.test(rel) || listed.has(rel)) continue;
    const bytes = fs.readFileSync(abs);
    const sha = sha256(bytes);
    let size = {};
    try {
      size = pngSize(bytes);
    } catch {}
    rows.push({ id: `inbox/${candidateVersion(sha)}`, row: 'art', status: 'new', files: [{ path: `approved/${rel}`, sha256: sha, ...size }], made: { from: `assets/approved/${rel}` } });
    report.stray.push(rel);
  }

  const queue = fs.existsSync(REGEN_QUEUE) ? JSON.parse(fs.readFileSync(REGEN_QUEUE, 'utf8')) : { items: [] };
  settleStatuses(rows, regenBySlot(queue, plantForm));
  return { rows, report };
}

export { IMAGE, ACTS };
