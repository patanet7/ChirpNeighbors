#!/usr/bin/env node
// The asset index: one command for building, finding and checking art (docs/ASSETS.md).
//   node scripts/assets.mjs index [--app <app checkout>] [--plants <candidates.json>] [--review <review-data.json>]
//   node scripts/assets.mjs find [--wanted|--unsorted|--candidates] [--kind <kind>]
//   node scripts/assets.mjs check
//   node scripts/assets.mjs import --tsv <D-assets.tsv> --catalog <slots.json> [--plants <candidates.json>] [--review <review-data.json>]
//   node scripts/assets.mjs queue-review --live <review-data.json> --out <review-data.next.json> [--img <dir>] [--decisions <export.json>]
// Plain Node, no dependencies.
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { isSlotRow, KINDS, parseId } from './lib/layout.mjs';
import { readIndex, writeIndex } from './lib/index-io.mjs';
import { buildIndex } from './lib/build-index.mjs';
import { checkApproved, checkIndex, strayImages } from './lib/check.mjs';
import { runImport } from './lib/import.mjs';
import { queueReview } from './lib/review.mjs';
import fs from 'node:fs';

function args(argv) {
  const out = { _: [] };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a.startsWith('--')) {
      const key = a.slice(2);
      const next = argv[i + 1];
      if (next === undefined || next.startsWith('--')) out[key] = true;
      else out[key] = argv[++i];
    } else out._.push(a);
  }
  return out;
}

/** Per kind: slots approved / with candidates / wanted, and art with no slot yet (unsorted). */
export function coverage(rows) {
  const table = Object.fromEntries([...KINDS, 'inbox'].map((k) => [k, { approved: 0, candidates: 0, unsorted: 0, wanted: 0 }]));
  for (const r of rows) {
    if (r.id === '#') continue;
    const kind = r.id.split('/')[0];
    if (!table[kind]) continue;
    if (isSlotRow(r)) {
      if (r.status === 'approved') table[kind].approved++;
      else if (r.status === 'candidate') table[kind].candidates++;
      else if (r.status === 'wanted') table[kind].wanted++;
    } else if (r.row === 'art' && r.status === 'new') table[kind].unsorted++;
  }
  if (!Object.values(table.packs).some(Boolean)) delete table.packs;
  return table;
}

export const coverageLines = (table) =>
  Object.entries(table).map(
    ([k, c]) => `${k.padEnd(8)} ${c.approved} approved · ${c.candidates} candidates · ${c.unsorted} unsorted · ${c.wanted} wanted`,
  );

function cmdIndex(opts) {
  const { rows, report } = buildIndex({ app: opts.app, plants: opts.plants, review: opts.review });
  const changed = writeIndex(rows);
  for (const s of report.seeds) console.log(`seed ${s}`);
  if (report.unmapped.length) console.log(`review slots with no mapping: ${report.unmapped.join(', ')}`);
  if (report.stray.length) console.log(`files in approved/ not in approved.json (status new): ${report.stray.length}`);
  console.log(`${changed ? 'wrote' : 'unchanged'} assets/index.jsonl: ${rows.length} rows`);
  console.log(coverageLines(coverage(rows)).join('\n'));
}

function cmdFind(opts) {
  const rows = readIndex();
  const pick = opts.wanted ? 'wanted' : opts.unsorted ? 'new' : opts.candidates ? 'candidate' : null;
  if (!pick) return console.log(coverageLines(coverage(rows)).join('\n'));
  for (const r of rows) {
    if (r.id === '#' || (opts.kind && !r.id.startsWith(`${opts.kind}/`))) continue;
    const hit = pick === 'new' ? r.row === 'art' && r.status === 'new' : isSlotRow(r) && r.status === pick;
    if (hit) console.log(`${r.id}${r.note ? `  (${r.note})` : r.regen?.note ? `  (make new: ${r.regen.note.slice(0, 80)})` : ''}${r.made?.from ? `  ${r.made.from}` : ''}`);
  }
}

async function cmdImport(opts) {
  if (!opts.tsv || !opts.catalog) {
    console.error('usage: node scripts/assets.mjs import --tsv <D-assets.tsv> --catalog <slots.json> [--plants <candidates.json>] [--review <review-data.json>]');
    process.exit(2);
  }
  const before = coverage(readIndex());
  const { rows, report } = await runImport({ tsv: opts.tsv, catalog: opts.catalog, plants: opts.plants, review: opts.review });
  writeIndex(rows);
  const r = report;
  console.log(`scanned ${r.files} image files (${r.contents} distinct contents): ${r.art} art rows, ${r.evidence} evidence rows`);
  console.log(`art by status: ${Object.entries(r.byStatus).map(([k, v]) => `${v} ${k}`).join(', ')}; ${r.inbox} in inbox (no subject)`);
  console.log(`placed by: ${r.claimsBy.map(([k, v]) => `${k} ${v}`).join(', ')}`);
  console.log(`audit TSV: ${r.tsv.rows} rows, ${r.tsv.inScan} found in the scan; not in the scan: ${Object.entries(r.tsv.notInScan).map(([k, v]) => `${v} ${k}`).join(', ')}`);
  console.log('coverage before:');
  console.log(coverageLines(before).join('\n'));
  console.log('coverage after:');
  console.log(coverageLines(coverage(rows)).join('\n'));
}

async function cmdQueueReview(opts) {
  if (!opts.live || !opts.out) {
    console.error('usage: node scripts/assets.mjs queue-review --live <review-data.json> --out <review-data.next.json> [--img <dir>] [--decisions <export.json>]');
    process.exit(2);
  }
  if (path.resolve(opts.out) === path.resolve(opts.live)) {
    console.error('queue-review never overwrites the live review data; pick another --out');
    process.exit(2);
  }
  const live = JSON.parse(fs.readFileSync(opts.live, 'utf8'));
  const decisions = opts.decisions ? JSON.parse(fs.readFileSync(opts.decisions, 'utf8')) : null;
  const imgDir = opts.img ?? path.join(path.dirname(opts.out), 'img');
  const { data, report } = await queueReview({ rows: readIndex(), live, decisions, imgDir });
  fs.writeFileSync(opts.out, JSON.stringify(data));
  fs.writeFileSync(path.join(path.dirname(opts.out), 'images.next.txt'), report.images.join('\n') + '\n');
  console.log(`wrote ${opts.out}: ${report.slots} slots (${data.groups.map((g) => `${g.label} ${g.slots}`).join(', ')})`);
  console.log(`previews: ${report.newPreviews} new in ${imgDir}, ${report.failedPreviews} could not be made; ${report.images.length} images listed in images.next.txt`);
  if (report.moved.length) console.log(`retired wrong slot names (candidates moved to the real slot): ${report.moved.join(', ')}`);
  if (decisions) console.log(report.missing.length ? `DECIDED SLOT IDS MISSING: ${report.missing.join(', ')}` : `all ${report.decided} decided slot ids are present`);
}

function cmdCheck() {
  const a = checkApproved();
  const ix = checkIndex(a.manifest);
  const errors = [...a.errors, ...ix.errors];
  const stray = strayImages();
  for (const [dir, n] of stray) console.warn(`warning: ${n} images in ${dir} (outside ${['approved', 'candidates', 'inbox', 'references'].join('/')}; moved by assets migrate)`);
  if (errors.length) {
    console.error(errors.join('\n'));
    process.exit(1);
  }
  console.log(`ok: ${a.summary}; index ${ix.rows.length - 1} rows`);
}

export async function main(argv = process.argv.slice(2)) {
  const opts = args(argv);
  const cmd = opts._[0];
  if (cmd === 'index') return cmdIndex(opts);
  if (cmd === 'find') return cmdFind(opts);
  if (cmd === 'check') return cmdCheck(opts);
  if (cmd === 'import') return cmdImport(opts);
  if (cmd === 'queue-review') return cmdQueueReview(opts);
  console.error('usage: node scripts/assets.mjs <index|find|check> [options] (see the header of scripts/assets.mjs)');
  process.exit(2);
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) await main();
export { parseId };
