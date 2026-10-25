#!/usr/bin/env node
// Verifies assets/approved matches assets/approved/approved.json (existence, sha256, no extras).
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', 'assets', 'approved');
const manifest = JSON.parse(fs.readFileSync(path.join(root, 'approved.json'), 'utf8'));
const errors = [];
const listed = new Set();
for (const e of manifest.approved) {
  for (const f of e.files) {
    listed.add(f.path);
    const abs = path.join(root, f.path);
    if (!fs.existsSync(abs)) { errors.push(`missing: ${f.path}`); continue; }
    const sha = crypto.createHash('sha256').update(fs.readFileSync(abs)).digest('hex');
    if (sha !== f.sha256) errors.push(`sha256 mismatch: ${f.path}`);
  }
  const expected = e.frames * (e.variants ?? 1);
  if (expected !== e.files.length) errors.push(`${e.slot}: frames × variants = ${expected} but ${e.files.length} files`);
}
const walk = (dir) => fs.readdirSync(dir, { withFileTypes: true }).flatMap((d) =>
  d.isDirectory() ? walk(path.join(dir, d.name)) : [path.join(dir, d.name)]);
for (const abs of walk(root)) {
  const rel = path.relative(root, abs).split(path.sep).join('/');
  if (rel === 'approved.json' || rel === 'README.md') continue;
  if (!listed.has(rel)) errors.push(`not in manifest: ${rel}`);
}
if (errors.length) { console.error(errors.join('\n')); process.exit(1); }
console.log(`ok: ${manifest.approved.length} slots, ${listed.size} files, ${manifest.pending.length} pending`);
