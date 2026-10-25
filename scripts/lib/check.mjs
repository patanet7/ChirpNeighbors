// `assets check`: the approved-art checks (formerly scripts/approved-art-check.mjs) plus the index.
import fs from 'node:fs';
import path from 'node:path';
import {
  APPROVED as root, MANIFEST, REGEN_QUEUE, SCHEMA, sha256, canonPath, clipDir, framePath, objectPath,
  ASSETS, ART_HOMES, INDEX, REGIONS, INDEX_SCHEMA, STATUSES, parseId, isSlotRow,
} from './layout.mjs';
import { decodePng, blockFactor } from './png.mjs';
import { readIndex } from './index-io.mjs';
import { approvedArtId } from './build-index.mjs';

const walk = (dir) =>
  fs.existsSync(dir)
    ? fs.readdirSync(dir, { withFileTypes: true }).flatMap((d) => (d.isDirectory() ? walk(path.join(dir, d.name)) : [path.join(dir, d.name)]))
    : [];

/**
 * assets/approved against approved.json and the canonical layout (docs/ASSETS.md): every listed
 * file exists with its sha256, sits at its canonical path, is a decodable PNG at its native pixel
 * grid (not block-upscaled); every bird has bird.json, every clip clip.json with a matching frame
 * count, every object object.json and one default variant; no unlisted art files.
 */
export function checkApproved() {
  const manifest = JSON.parse(fs.readFileSync(MANIFEST, 'utf8'));
  const errors = [];
  if (manifest.schema !== SCHEMA) errors.push(`approved.json schema is ${manifest.schema}, expected ${SCHEMA}`);
  const listed = new Set();
  const ids = new Set();
  const ID = /^[a-z0-9_]+$/;
  const DATE = /20\d\d-?[01]\d-?[0-3]\d/;
  for (const e of manifest.entries ?? []) {
    if (ids.has(e.id)) errors.push(`duplicate id ${e.id}`);
    ids.add(e.id);
    if (DATE.test(e.id)) errors.push(`${e.id}: a date in a path (dates are manifest fields)`);
    const expected =
      e.kind === 'bird-canon'
        ? [canonPath(e.species)]
        : e.kind === 'bird-clip'
          ? e.files.map((_, i) => framePath(e.species, e.action, e.variant, i))
          : e.kind === 'object'
            ? [objectPath(e.object, e.variant)]
            : e.kind === 'scene'
              ? [`scenes/${e.yard}/${e.season}/${e.layer}.png`]
              : null;
    for (const word of [e.species, e.action, e.object, e.yard, e.season, e.layer].filter(Boolean))
      if (!ID.test(word)) errors.push(`${e.id}: "${word}" is not a lowercase snake_case id`);
    if (e.kind === 'bird-clip' || e.kind === 'object')
      if (!/^v\d+$/.test(e.variant ?? '')) errors.push(`${e.id}: variant must be v1, v2, …`);
    e.files.forEach((f, i) => {
      listed.add(f.path);
      if (expected && expected[i] !== f.path) errors.push(`${e.id}: ${f.path} is not at its canonical path ${expected[i]}`);
      const abs = path.join(root, f.path);
      if (!fs.existsSync(abs)) return errors.push(`missing: ${f.path}`);
      const bytes = fs.readFileSync(abs);
      if (sha256(bytes) !== f.sha256) errors.push(`sha256 mismatch: ${f.path}`);
      let img;
      try {
        img = decodePng(bytes);
      } catch (err) {
        return errors.push(`${f.path}: not a decodable PNG (${err.message})`);
      }
      if (img.width !== f.width || img.height !== f.height) errors.push(`${f.path}: size differs from approved.json`);
      const k = blockFactor(img);
      if (k > 1) errors.push(`${f.path}: upscaled ${k}x (store art at its native pixel grid)`);
    });
    if (e.kind === 'bird-clip') {
      const clipFile = path.join(root, clipDir(e.species, e.action, e.variant), 'clip.json');
      if (!fs.existsSync(clipFile)) errors.push(`${e.id}: no clip.json`);
      else {
        const clip = JSON.parse(fs.readFileSync(clipFile, 'utf8'));
        if (clip.frames !== e.files.length) errors.push(`${e.id}: clip.json says ${clip.frames} frames, ${e.files.length} listed`);
        if (clip.frameMs && clip.frameMs.length !== e.files.length) errors.push(`${e.id}: frameMs length != frames`);
      }
    }
  }
  const kindOf = (kind) => (manifest.entries ?? []).filter((e) => e.kind === kind);
  for (const species of new Set(kindOf('bird-canon').map((e) => e.species)))
    if (!fs.existsSync(path.join(root, 'birds', species, 'bird.json'))) errors.push(`birds/${species}: no bird.json`);
  for (const species of new Set(kindOf('bird-clip').map((e) => e.species)))
    if (!kindOf('bird-canon').some((e) => e.species === species)) errors.push(`birds/${species}: clips without an approved canon`);
  for (const object of new Set(kindOf('object').map((e) => e.object))) {
    if (!fs.existsSync(path.join(root, 'objects', object, 'object.json'))) errors.push(`objects/${object}: no object.json`);
    const defaults = kindOf('object').filter((e) => e.object === object && e.default).length;
    if (defaults !== 1) errors.push(`objects/${object}: ${defaults} default variants (want 1)`);
  }
  const META = new Set(['bird.json', 'clip.json', 'object.json', 'plant.json']);
  for (const abs of walk(root)) {
    const rel = path.relative(root, abs).split(path.sep).join('/');
    if (['approved.json', 'README.md', path.basename(REGEN_QUEUE)].includes(rel)) continue;
    if (META.has(path.basename(rel))) continue;
    if (!listed.has(rel)) errors.push(`not in manifest: ${rel}`);
  }
  const queue = fs.existsSync(REGEN_QUEUE) ? JSON.parse(fs.readFileSync(REGEN_QUEUE, 'utf8')).items : [];
  return { errors, manifest, summary: `approved: ${manifest.entries.length} entries, ${listed.size} files, ${queue.length} in regen queue` };
}

const VOCAB = {
  cultivation: ['wild', 'nursery', 'houseplant'],
  setting: ['yard', 'indoor'],
  habit: ['tree', 'shrub', 'grass', 'perennial', 'succulent', 'vine', 'groundcover'],
  gives: ['food', 'water', 'perch', 'cover', 'light'],
  food: ['seed', 'berry', 'nectar', 'insect', 'fruit'],
  landscape: ['coastal', 'valley', 'mountain', 'desert', 'forest', 'prairie', 'urban'],
  wind: ['rigid', 'sway', 'swing', 'frames'],
};

/** The index: header, grammar, order, statuses, tags, and agreement with approved.json. */
export function checkIndex(manifest) {
  const errors = [];
  if (!fs.existsSync(INDEX)) return { errors: ['assets/index.jsonl is missing (run: node scripts/assets.mjs index)'], rows: [] };
  const rows = readIndex();
  if (rows[0]?.id !== '#' || rows[0]?.schema !== INDEX_SCHEMA) errors.push(`index.jsonl: first row must be the ${INDEX_SCHEMA} header`);
  const regions = fs.existsSync(path.join(REGIONS, 'regions.json'))
    ? new Set(JSON.parse(fs.readFileSync(path.join(REGIONS, 'regions.json'), 'utf8')).regions.map((r) => r.id))
    : new Set();
  const seen = new Set();
  const allIds = new Set(rows.map((r) => r.id));
  let prev = '';
  for (const r of rows.slice(1)) {
    if (seen.has(r.id)) errors.push(`index: duplicate id ${r.id}`);
    seen.add(r.id);
    if (r.id < prev) errors.push(`index: not sorted at ${r.id}`);
    prev = r.id;
    let p;
    try {
      p = parseId(r.id);
    } catch (err) {
      errors.push(`index: ${err.message}`);
      continue;
    }
    if (!['subject', 'slot', 'art', 'evidence'].includes(r.row)) errors.push(`${r.id}: row must be subject, slot, art or evidence`);
    if (r.row === 'subject' && r.id !== p.subject) errors.push(`${r.id}: a subject row's id is kind/name`);
    if (r.row === 'slot' && (!p.slot || p.version)) errors.push(`${r.id}: a slot row's id is subject/slot without a version`);
    if (isSlotRow(r) && !['wanted', 'candidate', 'approved', 'rejected', 'retired'].includes(r.status)) errors.push(`${r.id}: slot status ${r.status}`);
    if (r.row === 'art') {
      if (!STATUSES.includes(r.status) || r.status === 'wanted') errors.push(`${r.id}: art status ${r.status}`);
      if (!r.files?.length) errors.push(`${r.id}: art without files`);
      if (r.status === 'approved' && !/^v\d+$/.test(p.version ?? '')) errors.push(`${r.id}: approved art needs a vN version`);
      if (r.status !== 'approved' && p.version && !/^c[0-9a-f]{8}$/.test(p.version)) errors.push(`${r.id}: unapproved art needs a c<sha8> version`);
      if (r.slot && !allIds.has(r.slot)) errors.push(`${r.id}: slot ${r.slot} has no row`);
    }
    for (const [tag, allowed] of Object.entries(VOCAB))
      for (const v of [r[tag]].flat().filter((x) => x != null))
        if (!allowed.includes(v)) errors.push(`${r.id}: ${tag} "${v}" is not one of ${allowed.join(', ')}`);
    for (const reg of [...(r.nativeRange ?? []), ...(r.ecoregions ?? [])])
      if (!regions.has(reg)) errors.push(`${r.id}: region ${reg} is not in assets/regions/regions.json`);
    if (r.row === 'subject' && r.kind === 'plants' && !r.nativeRange?.length && !r.needs?.includes('nativeRange'))
      errors.push(`${r.id}: empty nativeRange must list needs: nativeRange`);
    for (const banned of ['origin', 'native', 'region'])
      if (banned in r) errors.push(`${r.id}: "${banned}" is not stored (native is computed from the yard location; use nativeRange/landscape)`);
  }
  // approved.json and the index agree
  const byId = new Map(rows.map((r) => [r.id, r]));
  for (const e of manifest.entries) {
    const r = byId.get(approvedArtId(e));
    if (!r || r.status !== 'approved') {
      errors.push(`index: approved ${e.id} has no approved art row (run: node scripts/assets.mjs index)`);
      continue;
    }
    if (r.files.map((f) => f.sha256).join() !== e.files.map((f) => f.sha256).join()) errors.push(`index: ${r.id} files differ from approved.json`);
  }
  const approvedRows = rows.filter((r) => r.row === 'art' && r.status === 'approved').length;
  if (approvedRows !== manifest.entries.length) errors.push(`index: ${approvedRows} approved art rows, approved.json has ${manifest.entries.length}`);
  return { errors, rows };
}

/** Images under assets/ outside approved/candidates/inbox/references (the old tree, until PR 3). */
export function strayImages() {
  const out = new Map();
  for (const top of fs.existsSync(ASSETS) ? fs.readdirSync(ASSETS) : []) {
    if (ART_HOMES.includes(top)) continue;
    const abs = path.join(ASSETS, top);
    const files = fs.statSync(abs).isDirectory() ? walk(abs) : [abs];
    const n = files.filter((f) => /\.(png|apng|gif|jpe?g|webp|svg)$/i.test(f)).length;
    if (n) out.set(`assets/${top}`, n);
  }
  return out;
}
