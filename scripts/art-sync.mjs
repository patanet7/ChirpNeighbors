#!/usr/bin/env node
/**
 * art:sync — make assets/approved match the owner's decisions (docs/ASSETS.md).
 *
 *   node scripts/art-sync.mjs --decisions <owner-decisions-export.json> [--work <_chirp-work>] [--dry-run]
 *
 * For every `approve`: resolve the picked candidate(s) to source files, turn them into RGBA PNG
 * frames at their native pixel grid (sheets are cut into cells, block-upscaled copies are brought
 * back down, GIF previews are replaced by their PNG frames), write them at the canonical path and
 * record them in approved.json. For every `regenerate` (and every approval that cannot become clean
 * frames) write an item to regen-queue.json; a slot sent back loses its approved files (their
 * source paths stay in the queue item). Idempotent: a slot whose approved candidates already match
 * the decision is left alone, files are only written when their bytes change.
 *
 * Inputs (defaults under --work, ~/GitHub/personal/_chirp-work):
 *   --review   chirp-review/review-data.json   the review page's slots and candidates
 *   --catalog  chirp-work/catalog/slots.json   each candidate's original location and frame ids
 *   --index    chirp-audit/D-assets.tsv        sha256 -> every known copy of a file
 *   --rig      chirp-work/rig                  rig outputs (picks named rig-…)
 *   --codex-root  where `disk:` locations live (the Codex task directory)
 */
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { execFileSync } from 'node:child_process';
import { decodePng, encodePng, crop, blockFactor, downsample, columnClear, opaqueFraction, isPng, feetPoint } from './lib/png.mjs';
import * as L from './lib/approved-layout.mjs';

// --- arguments --------------------------------------------------------------------------------
const argv = process.argv.slice(2);
const opt = (name, fallback) => {
  const i = argv.indexOf(name);
  return i >= 0 ? argv[i + 1] : fallback;
};
const DRY = argv.includes('--dry-run');
const decisionsFile = opt('--decisions');
if (!decisionsFile) {
  console.error('usage: node scripts/art-sync.mjs --decisions <export.json> [--work <dir>] [--dry-run]');
  process.exit(2);
}
const WORK = opt('--work', path.join(os.homedir(), 'GitHub/personal/_chirp-work'));
const reviewFile = opt('--review', path.join(WORK, 'chirp-review/review-data.json'));
const catalogFile = opt('--catalog', path.join(WORK, 'chirp-work/catalog/slots.json'));
const indexFile = opt('--index', path.join(WORK, 'chirp-audit/D-assets.tsv'));
const rigDir = opt('--rig', path.join(WORK, 'chirp-work/rig'));
const codexRoot = opt('--codex-root', path.join(os.homedir(), 'Documents/Codex/2026-10-16/task'));
const REVIEW_URL = opt('--review-url', 'https://claude.ai/artifact/MeKrKt4tdpFEjniGgpBsU6');

const readJson = (f) => JSON.parse(fs.readFileSync(f, 'utf8'));
const rawDecisions = readJson(decisionsFile);
/** Accepts the live export ({slotId: {verdict, pick, picks?, note, at}}) or {decisions: [...]}. */
const decisions = Array.isArray(rawDecisions.decisions)
  ? rawDecisions.decisions.map((d) => ({ slot: d.slot, verdict: d.verdict, pick: d.pick?.id ?? d.pick, picks: d.picks, note: d.note, at: d.decidedAt }))
  : Object.entries(rawDecisions).map(([slot, d]) => ({ slot, ...d }));
const review = readJson(reviewFile);
const reviewSlots = new Map(review.slots.map((s) => [s.id, s]));
const catalog = fs.existsSync(catalogFile) ? new Map(readJson(catalogFile).slots.map((s) => [s.id, s])) : new Map();
const rig = ['candidates.json', 'candidates-corvid.json'].flatMap((f) =>
  fs.existsSync(path.join(rigDir, f)) ? readJson(path.join(rigDir, f)) : [],
);
/** sha8 -> [{sha256, locations[]}] from the asset index. */
const index = new Map();
if (fs.existsSync(indexFile))
  for (const line of fs.readFileSync(indexFile, 'utf8').split('\n').slice(1)) {
    const c = line.split('\t');
    if (!c[0]) continue;
    const list = index.get(c[0].slice(0, 8)) ?? [];
    list.push({ sha256: c[0], locations: (c[5] ?? '').split(';').filter(Boolean) });
    index.set(c[0].slice(0, 8), list);
  }

// --- reading sources --------------------------------------------------------------------------
/** Bytes for one location string (`ChirpNeighbors:<path>@<ref>` or `disk:<path>`), or null. */
function readLocation(loc) {
  const repo = loc.match(/^ChirpNeighbors:(.+?)(?:@(.+))?$/);
  if (repo) {
    for (const ref of [...new Set([repo[2]?.split(',')[0], 'HEAD', 'origin/main'].filter(Boolean))])
      try {
        return execFileSync('git', ['-C', L.REPO, 'show', `${ref}:${repo[1]}`], { maxBuffer: 1 << 28, stdio: ['ignore', 'pipe', 'ignore'] });
      } catch {
        /* try the next ref */
      }
    return null;
  }
  const disk = loc.match(/^disk:(.+)$/);
  if (disk) {
    const abs = disk[1].startsWith('/') ? disk[1] : path.join(codexRoot, disk[1]);
    return fs.existsSync(abs) ? fs.readFileSync(abs) : null;
  }
  return fs.existsSync(loc) ? fs.readFileSync(loc) : null;
}
const repoPath = (loc) => loc.replace(/@[^@]*$/, '');
/** A file by sha8 (verified against the full sha256 when the index knows it). */
function readBySha8(sha8, hint) {
  const rows = index.get(sha8) ?? [];
  const tries = [...(hint ? [hint] : []), ...rows.flatMap((r) => r.locations)];
  for (const loc of tries) {
    const bytes = readLocation(loc);
    if (bytes && L.sha256(bytes).startsWith(sha8)) return { bytes, location: repoPath(loc) };
  }
  return null;
}
/** Where the producer kept prompts for a ChirpNeighbors source (pack root `prompts/` or prompt file). */
function promptFor(location, action) {
  const m = location.match(/^ChirpNeighbors:((?:assets\/generated\/[^/]+\/packs\/[^/]+)|(?:docs\/delivery\/[^/]+\/cloud-producer\/[^/]+\/[^/]+))\//);
  if (!m) return null;
  try {
    const files = execFileSync('git', ['-C', L.REPO, 'ls-tree', '-r', '--name-only', 'HEAD', m[1]], { encoding: 'utf8', maxBuffer: 1 << 26 })
      .split('\n')
      .filter((f) => /(^|\/)prompts?(\/|[-_.][^/]*$)/i.test(f.slice(m[1].length)));
    const named = files.find((f) => action && path.basename(f).toLowerCase().includes(action));
    if (named) return `ChirpNeighbors:${named}`;
    if (files.length === 1) return `ChirpNeighbors:${files[0]}`;
    const dir = files.length ? files[0].match(/^(.*\/prompts?)\//i)?.[1] : null;
    return dir ? `ChirpNeighbors:${dir}/` : null;
  } catch {
    return null;
  }
}

/** Equal cells of a horizontal sheet: the catalog's count when its gutters are clear, else the largest clean count. */
function sheetCells(img, hinted) {
  const clean = (n) => {
    if (img.width % n) return false;
    const w = img.width / n;
    for (let i = 1; i < n; i++) if (!columnClear(img, i * w - 1) || !columnClear(img, i * w)) return false;
    for (let i = 0; i < n; i++) if (!hasInk(crop(img, i * w, 0, w, img.height))) return false;
    return true;
  };
  if (hinted && hinted > 1 && clean(hinted)) return hinted;
  for (let n = Math.min(16, Math.floor(img.width / 8)); n >= 2; n--) if (clean(n)) return n;
  return 0;
}
const hasInk = (img) => {
  for (let i = 3; i < img.data.length; i += 4) if (img.data[i] >= 128) return true;
  return false;
};

/**
 * Resolve one pick to frames. Returns { frames: [{img, bytes?, from}], fps|frameMs, pack, source,
 * derivation[], candidate } or { problem }.
 */
function resolvePick(slotId, pick) {
  const action = slotId.split('.').slice(1).join('.');
  if (pick.startsWith('rig-')) {
    const c = rig.find((r) => r.slot === slotId);
    if (!c) return { problem: `rig pick ${pick} has no rig output for ${slotId}` };
    const canon8 = pick.match(/^rig-([0-9a-f]{8})-/)?.[1];
    if (canon8 && !c.canonSha256.startsWith(canon8)) return { problem: `rig output for ${slotId} was made from another canon` };
    const frameMs = c.ticks.map((t) => Math.round((t * 1000) / 30));
    if (c.framesDir) {
      const frames = Array.from({ length: c.frames }, (_, i) => {
        const file = path.join(rigDir, c.framesDir, `${action}-${L.pad(i)}.png`);
        const bytes = fs.readFileSync(file);
        return { img: decodePng(bytes), bytes, from: `rig:${path.relative(rigDir, file)}` };
      });
      return { frames, frameMs, pack: 'bodyplan-rig', source: `rig:${c.framesDir}/${action}-NN.png`, derivation: [], candidate: pick };
    }
    const strip = decodePng(fs.readFileSync(path.join(rigDir, c.strip)));
    const w = Number(c.size.split('x')[0]);
    const frames = Array.from({ length: c.frames }, (_, i) => ({ img: crop(strip, i * w, 0, w, strip.height), from: `rig:${c.strip}#${i}` }));
    return { frames, frameMs, pack: 'bodyplan-rig', source: `rig:${c.strip}`, derivation: [`cut ${c.frames} cells of ${c.size} from the rig strip`], candidate: pick };
  }
  const cand = catalog.get(slotId)?.candidates?.find((c) => c.id === pick);
  if (!cand) return { problem: `pick ${pick} is not in the catalog (no source location)` };
  const primary = cand.original_location?.primary;
  const derivation = [];
  let frames;
  if (cand.kind === 'frames' && cand.frame_ids?.length) {
    frames = [];
    for (const [i, id] of cand.frame_ids.entries()) {
      const got = readBySha8(id, i === 0 ? primary : undefined);
      if (!got) return { problem: `frame ${i + 1} (${id}) of ${pick} not found` };
      if (!isPng(got.bytes)) return { problem: `frame ${i + 1} of ${pick} is not a PNG` };
      frames.push({ img: decodePng(got.bytes), bytes: got.bytes, from: got.location });
    }
  } else if (cand.kind === 'frames' && /\.gif(@|$)/i.test(primary ?? '')) {
    // A GIF is a preview; its PNG frames sit in the pack's frames/ folder as <name>-<n>.png.
    const m = primary.match(/^(ChirpNeighbors:.*\/)previews\/([^/]+)\.gif(@.*)?$/i);
    frames = [];
    for (let i = 0; m && i < 64; i++) {
      const loc = `${m[1]}frames/${m[2]}-${i}.png${m[3] ?? ''}`;
      const bytes = readLocation(loc);
      if (!bytes) break;
      frames.push({ img: decodePng(bytes), bytes, from: repoPath(loc) });
    }
    if (!frames.length) return { problem: `${pick} exists only as a GIF preview; no PNG frames found` };
    derivation.push('GIF preview replaced by its PNG frames');
  } else {
    const got = readBySha8(pick, primary);
    if (!got) return { problem: `${pick} not found at ${primary}` };
    if (!isPng(got.bytes)) return { problem: `${pick} is not a PNG` };
    const img = decodePng(got.bytes);
    if (cand.kind === 'sheet') {
      const n = sheetCells(img, cand.frames);
      if (!n) return { problem: `${pick} is a sheet whose cells cannot be found (no clear gutters)` };
      const w = img.width / n;
      frames = Array.from({ length: n }, (_, i) => ({ img: crop(img, i * w, 0, w, img.height), from: `${got.location}#cell${i}` }));
      derivation.push(`cut ${n} cells of ${w}x${img.height} from the sheet`);
    } else frames = [{ img, bytes: got.bytes, from: got.location }];
  }
  return {
    frames,
    fps: cand.fps ?? null,
    pack: cand.pack ?? null,
    source: repoPath(derivation.some((x) => x.startsWith("GIF")) ? frames[0].from : (primary ?? frames[0].from)),
    prompt: primary ? promptFor(primary, action) : null,
    derivation,
    candidate: pick,
  };
}

/** Bring frames to their native grid; flag art that is not a transparent sprite. */
function normalize(resolved, { kind, action }) {
  if (resolved.problem) return resolved;
  const isBird = kind !== 'object';
  // Rig output is always clip frames; a one-frame rig idle is a hold pose, not a board.
  if (isBird && action !== 'canon' && resolved.pack !== 'bodyplan-rig' && resolved.frames.length < 2)
    return { problem: `${resolved.candidate} is one drawing (a board or still), not clip frames; needs cutting or regeneration` };
  const k = Math.min(...resolved.frames.map((f) => blockFactor(f.img)));
  const sizes = new Set(resolved.frames.map((f) => `${f.img.width}x${f.img.height}`));
  if (sizes.size > 1) return { problem: `${resolved.candidate}: frames differ in size (${[...sizes].join(', ')})` };
  for (const f of resolved.frames) {
    if (opaqueFraction(f.img) > 0.9) return { problem: `${resolved.candidate}: background baked in (not a transparent sprite)` };
    if (k > 1) {
      f.img = downsample(f.img, k);
      delete f.bytes;
    }
  }
  if (k > 1) resolved.derivation.push(`brought down ${k}x to the native pixel grid`);
  return resolved;
}
const pngBytes = (f) => f.bytes ?? encodePng(f.img);

// --- plan ---------------------------------------------------------------------------------------
const manifest = L.readManifest();
let entries = [...manifest.entries];
const queue = [];
// Items keep what an earlier run removed from approved, so re-runs write the same queue.
const priorQueue = new Map(
  (fs.existsSync(L.REGEN_QUEUE) ? readJson(L.REGEN_QUEUE).items : []).map((q) => [q.slot, q]),
);
const removedNote = (slot, removed) => {
  const list = removed.length ? removed : (priorQueue.get(slot)?.removedFromApproved ?? []);
  return list.length ? { removedFromApproved: list } : {};
};
const log = [];
const parseSlot = (slot) => {
  if (slot.startsWith('object.')) return { kind: 'object', object: L.snake(slot.slice(7)) };
  const [species, ...rest] = slot.split('.');
  const action = rest.join('.');
  return { kind: action === 'canon' ? 'bird-canon' : 'bird-clip', species, action };
};
const bestCandidate = (slotId, exclude) => {
  const s = reviewSlots.get(slotId);
  const c = (s?.candidates ?? []).filter((x) => !x.ownerRejected && x.id !== exclude).sort((a, b) => a.rank - b.rank)[0];
  if (!c) return null;
  const loc = catalog.get(slotId)?.candidates?.find((x) => x.id === c.id)?.original_location?.primary;
  const rigOut = c.id.startsWith("rig-") ? rig.find((r) => r.slot === slotId) : null;
  return { id: c.id, kind: c.kind, preview: c.preview, pack: c.pack, source: loc ? repoPath(loc) : rigOut ? `rig:${rigOut.framesDir ?? rigOut.strip}` : null };
};

const decided = new Set();
for (const d of decisions.sort((a, b) => a.slot.localeCompare(b.slot))) {
  const where = parseSlot(d.slot);
  decided.add(d.slot);
  const current = entries.filter((e) => e.reviewSlot === d.slot);
  const drop = (reason) => {
    if (!current.length) return [];
    entries = entries.filter((e) => e.reviewSlot !== d.slot);
    log.push(`${d.slot}: removed from approved (${reason})`);
    return current.map((e) => ({ id: e.id, candidate: e.source?.candidate ?? null, source: e.source?.path ?? null }));
  };
  if (d.verdict !== 'approve') {
    const removed = drop(`owner: ${d.verdict}`);
    queue.push({
      slot: d.slot,
      ...where,
      verdict: d.verdict,
      note: d.note ?? '',
      decidedAt: d.at ?? null,
      reason: 'owner asked to regenerate',
      bestCandidate: bestCandidate(d.slot),
      ...removedNote(d.slot, removed),
    });
    continue;
  }
  const picks = (d.picks?.length ? d.picks : [d.pick]).filter(Boolean);
  if (!picks.length) continue;
  const have = current.map((e) => e.source?.candidate).sort().join(',');
  const intact = (e) =>
    e.files.every((f) => fs.existsSync(path.join(L.APPROVED, f.path))) && (e.kind !== 'bird-clip' || e.files.length >= 2);
  if (have === [...picks].sort().join(',') && current.every(intact)) continue; // already in the library
  const resolved = picks.map((p) => normalize(resolvePick(d.slot, p), where));
  const bad = resolved.find((r) => r.problem);
  if (bad) {
    const removed = drop(bad.problem);
    queue.push({
      slot: d.slot,
      ...where,
      verdict: 'approve',
      note: d.note ?? '',
      decidedAt: d.at ?? null,
      reason: bad.problem,
      bestCandidate: bestCandidate(d.slot) && { ...bestCandidate(d.slot), id: picks[0] },
      ...removedNote(d.slot, removed),
    });
    log.push(`${d.slot}: queued (${bad.problem})`);
    continue;
  }
  entries = entries.filter((e) => e.reviewSlot !== d.slot);
  resolved.forEach((r, i) => {
    const variant = `v${i + 1}`;
    const base = {
      source: { candidate: r.candidate, pack: r.pack, path: r.source, ...(r.derivation.length ? { derivation: r.derivation } : {}) },
      prompt: r.prompt ?? null,
      generated: L.dateFromPath(r.source),
      approved: d.at ?? null,
      reviewSlot: d.slot,
      reviewUrl: REVIEW_URL,
    };
    if (where.kind === 'object') {
      const rel = L.objectPath(where.object, variant);
      const bytes = pngBytes(r.frames[0]);
      entries.push({ id: `${L.objectDir(where.object)}/${variant}`, kind: 'object', object: where.object, variant, default: r.candidate === d.pick, files: [L.fileRecord(rel, bytes)], ...base, _write: [[rel, bytes]] });
    } else if (where.kind === 'bird-canon') {
      const rel = L.canonPath(where.species);
      const bytes = pngBytes(r.frames[0]);
      entries.push({ id: `${L.birdDir(where.species)}/canon`, kind: 'bird-canon', species: where.species, files: [L.fileRecord(rel, bytes)], ...base, _write: [[rel, bytes]] });
    } else {
      const writes = r.frames.map((f, j) => [L.framePath(where.species, where.action, variant, j), pngBytes(f)]);
      const clip = L.clipJson({ action: where.action, frames: r.frames.map((f) => f.img), fps: r.fps, frameMs: r.frameMs });
      writes.push([`${L.clipDir(where.species, where.action, variant)}/clip.json`, Buffer.from(L.json(clip))]);
      entries.push({
        id: L.clipDir(where.species, where.action, variant),
        kind: 'bird-clip',
        species: where.species,
        action: where.action,
        variant,
        default: i === 0,
        files: writes.filter(([p]) => p.endsWith('.png')).map(([p, b]) => L.fileRecord(p, b)),
        ...(clip.frameMs ? { frameMs: clip.frameMs } : { fps: clip.fps }),
        loop: clip.loop,
        ...base,
        _write: writes,
      });
    }
  });
  log.push(`${d.slot}: approved ${picks.join(', ')}${resolved.some((r) => r.derivation.length) ? ' (' + resolved.flatMap((r) => r.derivation).join('; ') + ')' : ''}`);
}

// --- write --------------------------------------------------------------------------------------
const keep = new Set();
for (const e of entries) for (const f of e.files) keep.add(f.path);
const birds = new Set(entries.filter((e) => e.kind === 'bird-canon').map((e) => e.species));
const clipDirs = new Set(entries.filter((e) => e.kind === 'bird-clip').map((e) => e.id));
const objects = new Set(entries.filter((e) => e.kind === 'object').map((e) => e.object));
let written = 0;
let removed = 0;
const write = (rel, bytes) => {
  if (!DRY && L.writeIfChanged(path.join(L.APPROVED, rel), bytes)) written++;
};
for (const e of entries) for (const [rel, bytes] of e._write ?? []) write(rel, bytes);
// bird.json: keep the species facts already there, refresh the canon canvas and anchor.
for (const species of birds) {
  const rel = `${L.birdDir(species)}/bird.json`;
  const abs = path.join(L.APPROVED, rel);
  const prior = fs.existsSync(abs) ? readJson(abs) : { id: species, appSpeciesId: null, lengthCm: null, facing: 'right' };
  const canon = entries.find((e) => e.kind === 'bird-canon' && e.species === species);
  const img = decodePng(canon._write ? canon._write[0][1] : fs.readFileSync(path.join(L.APPROVED, canon.files[0].path)));
  write(rel, Buffer.from(L.json({ ...prior, canvas: { width: img.width, height: img.height }, anchor: feetPoint(img), palette: prior.palette ?? null })));
}
// Remove files no entry owns (slots sent back, replaced picks), outside scenes/.
const walk = (dir) =>
  fs.existsSync(dir) ? fs.readdirSync(dir, { withFileTypes: true }).flatMap((d) => (d.isDirectory() ? walk(path.join(dir, d.name)) : [path.join(dir, d.name)])) : [];
for (const abs of [...walk(path.join(L.APPROVED, 'birds')), ...walk(path.join(L.APPROVED, 'objects'))]) {
  const rel = path.relative(L.APPROVED, abs).split(path.sep).join('/');
  const parts = rel.split('/');
  const owned =
    keep.has(rel) ||
    (parts[0] === 'birds' && parts.length === 3 && parts[2] === 'bird.json' && birds.has(parts[1])) ||
    (parts[0] === 'birds' && parts[parts.length - 1] === 'clip.json' && clipDirs.has(parts.slice(0, -1).join('/'))) ||
    (parts[0] === 'objects' && parts[2] === 'object.json' && objects.has(parts[1]));
  if (!owned) {
    removed++;
    if (!DRY) fs.rmSync(abs);
  }
}
if (!DRY) execFileSync('find', [L.APPROVED, '-type', 'd', '-empty', '-delete']);
// Objects approved for the first time get an object.json shell (geometry is filled by hand / the app).
for (const object of objects) {
  const abs = path.join(L.APPROVED, L.objectDir(object), 'object.json');
  if (fs.existsSync(abs)) continue;
  const variants = Object.fromEntries(entries.filter((e) => e.object === object).map((e) => [e.variant, { appCatalogId: null }]));
  write(`${L.objectDir(object)}/object.json`, Buffer.from(L.json({ id: object, reviewSlot: entries.find((e) => e.object === object).reviewSlot, kind: null, variants })));
}
// Entries no decision mentions stay as they are (the export may be partial); say so.
for (const e of entries) if (!decided.has(e.reviewSlot)) log.push(`${e.reviewSlot}: no decision in this export; kept`);
const clean = L.sortEntries(entries.map(({ _write, ...e }) => e));
const outManifest = { schema: L.SCHEMA, layout: 'docs/ASSETS.md', entries: clean };
const outQueue = { schema: 'chirp-regen-queue/1', items: queue.sort((a, b) => a.slot.localeCompare(b.slot)) };
if (!DRY) {
  if (L.writeIfChanged(L.MANIFEST, L.json(outManifest))) written++;
  if (L.writeIfChanged(L.REGEN_QUEUE, L.json(outQueue))) written++;
}
console.log([...new Set(log)].join('\n') || 'no changes');
console.log(
  `${DRY ? '[dry run] ' : ''}${clean.length} entries, ${clean.reduce((n, e) => n + e.files.length, 0)} files; ${queue.length} in regen queue; ${written} written, ${removed} removed`,
);
