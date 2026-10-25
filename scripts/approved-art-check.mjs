#!/usr/bin/env node
// Verifies assets/approved against approved.json and the canonical layout (docs/ASSETS.md):
// every listed file exists with its sha256, sits at its canonical path, is a decodable PNG at its
// native pixel grid (not block-upscaled); every bird has bird.json, every clip clip.json with a
// matching frame count, every object object.json and one default variant; no unlisted art files.
// scenes/ belongs to the scenes track and is only checked when its files are listed.
import fs from 'node:fs';
import path from 'node:path';
import {
  APPROVED as root,
  MANIFEST,
  REGEN_QUEUE,
  SCHEMA,
  sha256,
  canonPath,
  clipDir,
  framePath,
  objectPath,
} from './lib/approved-layout.mjs';
import { decodePng, blockFactor } from './lib/png.mjs';

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
          : null;
  for (const word of [e.species, e.action, e.object].filter(Boolean))
    if (!ID.test(word)) errors.push(`${e.id}: "${word}" is not a lowercase snake_case id`);
  if (e.kind === 'bird-clip' || e.kind === 'object')
    if (!/^v\d+$/.test(e.variant ?? '')) errors.push(`${e.id}: variant must be v1, v2, …`);
  e.files.forEach((f, i) => {
    listed.add(f.path);
    if (expected && expected[i] !== f.path)
      errors.push(`${e.id}: ${f.path} is not at its canonical path ${expected[i]}`);
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
      if (clip.frames !== e.files.length)
        errors.push(`${e.id}: clip.json says ${clip.frames} frames, ${e.files.length} listed`);
      if (clip.frameMs && clip.frameMs.length !== e.files.length) errors.push(`${e.id}: frameMs length != frames`);
    }
  }
}
const kindOf = (kind) => (manifest.entries ?? []).filter((e) => e.kind === kind);
for (const species of new Set(kindOf('bird-canon').map((e) => e.species)))
  if (!fs.existsSync(path.join(root, 'birds', species, 'bird.json'))) errors.push(`birds/${species}: no bird.json`);
for (const species of new Set(kindOf('bird-clip').map((e) => e.species)))
  if (!kindOf('bird-canon').some((e) => e.species === species))
    errors.push(`birds/${species}: clips without an approved canon`);
for (const object of new Set(kindOf('object').map((e) => e.object))) {
  if (!fs.existsSync(path.join(root, 'objects', object, 'object.json')))
    errors.push(`objects/${object}: no object.json`);
  const defaults = kindOf('object').filter((e) => e.object === object && e.default).length;
  if (defaults !== 1) errors.push(`objects/${object}: ${defaults} default variants (want 1)`);
}
const META = new Set(['bird.json', 'clip.json', 'object.json']);
const walk = (dir) =>
  fs
    .readdirSync(dir, { withFileTypes: true })
    .flatMap((d) => (d.isDirectory() ? walk(path.join(dir, d.name)) : [path.join(dir, d.name)]));
for (const abs of walk(root)) {
  const rel = path.relative(root, abs).split(path.sep).join('/');
  if (['approved.json', 'README.md', path.basename(REGEN_QUEUE)].includes(rel)) continue;
  if (rel.startsWith('scenes/') && !listed.has(rel)) continue;
  if (META.has(path.basename(rel))) continue;
  if (!listed.has(rel)) errors.push(`not in manifest: ${rel}`);
}
const queue = fs.existsSync(REGEN_QUEUE) ? JSON.parse(fs.readFileSync(REGEN_QUEUE, 'utf8')).items : [];
if (errors.length) {
  console.error(errors.join('\n'));
  process.exit(1);
}
console.log(`ok: ${manifest.entries.length} entries, ${listed.size} files, ${queue.length} in regen queue`);
