// `assets import`: brings the old pile (assets/generated, docs/delivery at origin/main) into the
// index. Every distinct content gets one row: art (status candidate when a curated source knows
// its slot, otherwise new) or evidence (previews, contact sheets, GIFs, opaque renders, with why).
// Curated sources, strongest first: the plant batch (plants/candidates.json), approved.json
// sources, the app catalog, the review catalog (slots.json) and the live review data. The audit
// manifest (D-assets.tsv) adds its status/reason, owner rejections and the subject it recorded.
import fs from 'node:fs';
import path from 'node:path';
import {
  readManifest, candidateVersion, plantSlot, sceneSlot, reviewToSlot, CORRECTED_REVIEW_SLOTS, parseId,
  parseStateSuffix, dateFromPath, ACTS, isSlotRow, snake, YARD_ALIASES,
} from './layout.mjs';
import { readIndex } from './index-io.mjs';
import { approvedArtId, plantFormHabit, plantVariantSlot, settleStatuses, regenBySlot, mergeRows } from './build-index.mjs';
import { scanTree, OLD_ROOTS } from './scan.mjs';
import { REGEN_QUEUE } from './approved-layout.mjs';

const REF = 'origin/main';

/** Pack a path belongs to: packs/<p>, regional-yard-packs/<p>, cloud-producer/<a>/<b>, … */
export function packOf(p) {
  const parts = p.split('/');
  let i = parts.indexOf('packs');
  if (i >= 0 && parts[i + 1]) return parts[i + 1];
  i = parts.indexOf('regional-yard-packs');
  if (i >= 0) {
    const next = parts[i + 1];
    if (next === 'files') {
      const j = parts.indexOf('expansion');
      return `regional-yard-packs/${j >= 0 ? parts.slice(j + 1, j + 3).filter((x) => !/\./.test(x)).join('/') : 'files'}`;
    }
    return `regional-yard-packs/${next}`;
  }
  i = parts.indexOf('cloud-producer');
  if (i >= 0) return parts.slice(i, i + 3).join('/');
  return parts.slice(0, -1).slice(-2).join('/');
}

/** Numbered frame files in one folder: `hopping-00-stand.png`, `rig-frame-01.png`, `03.png`. */
export function frameKey(p) {
  const dir = path.posix.dirname(p);
  const base = path.posix.basename(p).replace(/\.[a-z0-9]+$/i, '');
  const m = base.match(/^(.*?)(?:^|[-_])(\d{1,3})(?=[-_]|$)/);
  if (!m) return null;
  return { key: `${dir}/${m[1]}`, n: Number(m[2]) };
}

export function readTsv(file) {
  const lines = fs.readFileSync(file, 'utf8').split('\n').filter(Boolean);
  const head = lines.shift().split('\t');
  return lines.map((l) => Object.fromEntries(l.split('\t').map((v, i) => [head[i], v])));
}

const norm = (s) => String(s ?? '').toLowerCase().replace(/[’']/g, '').replace(/[^a-z0-9]+/g, '_').replace(/^_|_$/g, '');
const short = (s, n = 200) => (s && s.length > n ? `${s.slice(0, n - 1)}…` : s || undefined);

export async function runImport({ tsv, catalog, plants, review, ref = REF, log = console.log }) {
  const manifest = readManifest();
  let rows = readIndex().filter((r) => r.id !== '#');
  const imported = (r) => r.row === 'evidence' || (r.row === 'art' && r.status !== 'approved' && OLD_ROOTS.some((root) => String(r.made?.from ?? '').startsWith(root)));
  rows = rows.filter((r) => !imported(r));
  const byId = new Map(rows.map((r) => [r.id, r]));

  log(`scanning ${OLD_ROOTS.join(', ')} at ${ref}…`);
  const { files, bySha } = await scanTree(ref, OLD_ROOTS, { log });
  const bySha8 = new Map();
  for (const rec of bySha.values()) {
    const k = rec.sha256.slice(0, 8);
    if (!bySha8.has(k)) bySha8.set(k, []);
    bySha8.get(k).push(rec);
  }
  const byPath = new Map();
  for (const rec of bySha.values()) for (const p of rec.paths) byPath.set(p, rec);
  const one = (sha8) => (bySha8.get(sha8)?.length === 1 ? bySha8.get(sha8)[0] : null);

  // plant forms already in the index
  const forms = new Map();
  for (const r of rows) if (r.row === 'slot' && r.id.startsWith('plants/')) forms.set(parseId(r.id).name, parseId(r.id).form);
  const plantDoc = plants ? JSON.parse(fs.readFileSync(plants, 'utf8')) : { species: [] };
  for (const sp of plantDoc.species) forms.set(sp.slot.replace(/^plant\./, ''), plantFormHabit(sp.form, sp.origin).form);
  const plantForm = (name) => forms.get(name) ?? 'mature';

  // ---------------------------------------------------------------- curated claims
  /** sha256 -> { slot, by, part?, label?, became?, rejected?, frames? } (first claim wins) */
  const claims = new Map();
  const claim = (sha, c) => {
    if (sha && !claims.has(sha)) claims.set(sha, c);
  };
  const groups = []; // frame sequences: { slot, by, shas: [sha256 …] }

  // 1. the plant batch (corrects plant.healthy / plant.corrected to the oak)
  for (const sp of plantDoc.species) {
    const name = sp.slot.replace(/^plant\./, '');
    for (const v of sp.variants ?? []) {
      const { season, state, part } = plantVariantSlot(v);
      const slot = plantSlot(name, plantForm(name), season, state);
      if (bySha.has(v.sha256)) {
        claim(v.sha256, { slot, by: 'plants/candidates.json', part, label: v.label });
        continue;
      }
      // layered (base + overlay) and frame sets are several files; the batch's sha is its own composite
      const recs = (v.sourcePaths ?? []).map((sp) => byPath.get(sp.replace(/^ChirpNeighbors:/, '').replace(/@[^@]*$/, '')));
      if (recs.length && recs.every(Boolean))
        groups.push({ slot, by: 'plants/candidates.json', shas: recs.map((r) => r.sha256), layered: v.kind === 'layered', label: v.label, part });
    }
  }
  // 2. approved.json: the candidate each approved entry was made from
  for (const e of manifest.entries) {
    const rec = e.source?.candidate && one(e.source.candidate);
    const artId = approvedArtId(e);
    if (rec) claim(rec.sha256, { slot: artId.replace(/\/v\d+$/, ''), by: 'approved.json', became: artId.split('/').pop() });
  }
  // 3. the app catalog (recorded on subjects by `assets index --app`)
  for (const r of rows)
    for (const a of Object.values(r.app ?? {}))
      if (a.sha256 && a.uses == null)
        claim(a.sha256, { slot: r.kind === 'plants' ? plantSlot(r.name, plantForm(r.name)) : r.id, by: 'app catalog' });
  // 4. the review catalog (slots.json) and 5. the live review data
  const reviewDocs = [catalog && { by: 'review catalog', doc: JSON.parse(fs.readFileSync(catalog, 'utf8')) }, review && { by: 'review page', doc: JSON.parse(fs.readFileSync(review, 'utf8')) }].filter(Boolean);
  for (const { by, doc } of reviewDocs)
    for (const s of doc.slots) {
      const fix = CORRECTED_REVIEW_SLOTS[s.id];
      const slot = fix ? fix.slot : reviewToSlot(s.id, plantForm);
      if (!slot) continue;
      for (const c of s.candidates ?? []) {
        const rejected = !!(c.owner?.rejected || c.ownerRejected);
        if (c.frame_ids?.length > 1 && !c.frame_ids.every((id) => id === c.frame_ids[0])) {
          const recs = c.frame_ids.map((id) => one(id));
          if (recs.every(Boolean)) groups.push({ slot, by, shas: recs.map((r) => r.sha256), rejected, fps: c.fps ?? null });
          continue;
        }
        const rec = one(c.id);
        if (rec) claim(rec.sha256, { slot, by, part: fix?.part, rejected, review: s.id });
      }
    }

  // ---------------------------------------------------------------- audit manifest
  const audit = new Map();
  let tsvRows = 0;
  let tsvInScan = 0;
  for (const t of tsv ? readTsv(tsv) : []) {
    tsvRows++;
    if (bySha.has(t.sha256)) tsvInScan++;
    audit.set(t.sha256, t);
  }

  // ---------------------------------------------------------------- subjects for unclaimed art
  const subjects = rows.filter((r) => r.row === 'subject');
  const birdByName = new Map();
  for (const r of subjects.filter((x) => x.kind === 'birds')) {
    birdByName.set(r.name, r.id);
    if (r.label) birdByName.set(norm(r.label), r.id);
  }
  birdByName.set('robin', 'birds/american_robin');
  const plantNames = subjects.filter((x) => x.kind === 'plants').map((x) => x.name).sort((a, b) => b.length - a.length);
  const objectNames = new Map();
  for (const r of subjects.filter((x) => x.kind === 'objects')) {
    objectNames.set(r.name, r.id);
    for (const a of Object.values(r.app ?? {})) if (a.assetId) objectNames.set(norm(String(a.assetId).replace(/^(object|approved-object)[.:]/, '')), r.id);
  }
  const YARDS = new Set(['coastal', 'oak', 'courtyard', 'inland', 'patio', 'mediterranean', ...Object.keys(YARD_ALIASES)]);
  const SCENE_SUBJECTS = new Set(['ground/background', 'season', 'weather']);

  /** { subject, guess, by } for art nobody curated, from the audit subject and the path's words. */
  function placeUnclaimed(rec, p) {
    const t = audit.get(rec.sha256);
    const base = path.posix.basename(p).replace(/\.[a-z0-9]+$/i, '').toLowerCase();
    const segs = p.toLowerCase().split('/');
    const tokens = new Set(segs.flatMap((s) => s.split(/[-_.]+/)));
    const st = parseStateSuffix(p);
    // birds: the audit's species
    const bird = t && birdByName.get(norm(t.subject));
    if (bird) {
      const act = ACTS.find((a) => base.split(/[-_.]+/).includes(a));
      return { subject: bird, guess: act ? `${bird}/clips/${act}` : undefined, by: 'audit subject' };
    }
    // plants: a plant name in the file or folder name
    const flat = `/${segs.slice(-3).join('/')}/`.replace(/-/g, '_');
    const plant = plantNames.find((n) => new RegExp(`[/_.]${n}[/_.]`).test(flat));
    if (plant) {
      const form = plantForm(plant);
      return { subject: `plants/${plant}`, guess: plantSlot(plant, form, st.season ?? 'all', st.state && st.state !== 'base' ? st.state : null), by: 'name in path' };
    }
    // objects: object.<name>.… files, or an object subject's name
    const om = base.match(/^object\.([a-z0-9_]+)/);
    const obj = om && (objectNames.get(om[1]) ?? null);
    if (obj) return { subject: obj, by: 'object.<name> file name' };
    // scenes: a yard folder, for art the audit or the classifier calls a background
    const sceneLike = (t && SCENE_SUBJECTS.has(t.subject)) || rec.why.startsWith('opaque background');
    const yard = segs.find((s) => YARDS.has(s)) ?? segs.map((s) => s.replace(/-\d+$/, '')).find((s) => YARDS.has(s));
    if (sceneLike && yard) {
      const y = YARD_ALIASES[yard] ?? yard;
      const season = st.season ?? ['spring', 'summer', 'autumn', 'winter'].find((s) => tokens.has(s));
      const layer = ['background', 'ground', 'foreground', 'composite'].find((l) => tokens.has(l));
      return { subject: `scenes/${y}`, guess: season || layer ? sceneSlot(y, season ?? 'all', st.state && st.state !== 'base' ? st.state : null, layer ?? 'composite') : undefined, by: 'yard folder' };
    }
    return { subject: null, by: null };
  }

  // ---------------------------------------------------------------- rows
  const made = (rec, p) => ({ from: p, pack: packOf(p), on: dateFromPath(p) });
  const fileOf = (rec, p) => ({ path: p, sha256: rec.sha256, ...(rec.width ? { width: rec.width, height: rec.height } : {}) });
  const auditOf = (rec) => {
    const t = audit.get(rec.sha256);
    return t ? { status: t.status, reason: short(t.reason), kind: t.kind, subject: t.subject || undefined, rejectedBy: t.rejected_by || undefined } : undefined;
  };
  const ownerRejected = (rec) => /^owner$/i.test(audit.get(rec.sha256)?.rejected_by ?? '') && audit.get(rec.sha256)?.status === 'rejected';
  const out = [];
  const outIds = new Set();
  const used = new Set(); // contents placed in some art row (a frame can also be a still candidate)
  const addArt = (row) => {
    if (outIds.has(row.id)) return false; // the same content claimed twice for one slot
    if (byId.has(row.id)) throw Error(`art id ${row.id} already in the index`);
    outIds.add(row.id);
    out.push(row);
    return true;
  };

  // frame sequences the review catalog knows
  for (const g of groups) {
    const recs = g.shas.map((s) => bySha.get(s));
    const first = recs[0];
    const p = first.artPath ?? first.paths[0];
    addArt({
      id: `${g.slot}/${candidateVersion(first.sha256)}`,
      row: 'art',
      status: g.rejected ? 'rejected' : 'candidate',
      slot: g.slot,
      frames: g.layered ? undefined : recs.length,
      layers: g.layered ? recs.length : undefined,
      label: g.label,
      part: g.part,
      fps: g.fps ?? undefined,
      files: recs.map((r) => fileOf(r, r.artPath ?? r.paths[0])),
      made: made(first, p),
      by: g.by,
      audit: auditOf(first),
    });
    g.shas.forEach((s) => used.add(s));
  }
  // single files a curated source knows
  for (const [sha, c] of claims) {
    const rec = bySha.get(sha);
    if (!rec) continue;
    const p = rec.artPath ?? rec.paths[0];
    addArt({
      id: `${c.slot}/${candidateVersion(sha)}`,
      row: 'art',
      status: c.rejected || ownerRejected(rec) ? 'rejected' : 'candidate',
      slot: c.slot,
      part: c.part,
      label: c.label,
      became: c.became,
      files: [fileOf(rec, p)],
      made: made(rec, p),
      copies: rec.paths.length > 1 ? rec.paths.filter((x) => x !== p) : undefined,
      by: c.by,
      looks: rec.class === 'evidence' ? `evidence by itself (${rec.why}); kept as art because ${c.by} uses it` : undefined,
      audit: auditOf(rec),
    });
    used.add(sha);
  }
  // everything else: frame groups by folder, then single files
  const loose = [...bySha.values()].filter((r) => r.class === 'art' && !used.has(r.sha256));
  const seqs = new Map();
  for (const rec of loose) {
    const k = frameKey(rec.artPath);
    if (!k) continue;
    if (!seqs.has(k.key)) seqs.set(k.key, []);
    seqs.get(k.key).push({ rec, n: k.n });
  }
  const placeNew = (recs, frames) => {
    const first = recs[0];
    const p = first.artPath;
    const pl = placeUnclaimed(first, p);
    const v = candidateVersion(first.sha256);
    const st = parseStateSuffix(p);
    addArt({
      id: pl.subject ? `${pl.subject}/${v}` : `inbox/${v}`,
      row: 'art',
      status: ownerRejected(first) ? 'rejected' : 'new',
      frames: frames ? recs.length : undefined,
      files: recs.map((r) => fileOf(r, r.artPath)),
      made: made(first, p),
      copies: !frames && first.paths.length > 1 ? first.paths.filter((x) => x !== p) : undefined,
      guess: pl.guess,
      placedBy: pl.by ?? undefined,
      state: st.state && st.state !== 'base' ? st.state : undefined,
      season: st.season ?? undefined,
      why: first.why,
      audit: auditOf(first),
    });
    recs.forEach((r) => used.add(r.sha256));
  };
  for (const members of seqs.values()) {
    if (members.length < 2 || new Set(members.map((m) => m.n)).size < 2) continue;
    members.sort((a, b) => a.n - b.n || (a.rec.artPath < b.rec.artPath ? -1 : 1));
    placeNew(members.map((m) => m.rec), true);
  }
  for (const rec of loose) if (!used.has(rec.sha256)) placeNew([rec], false);
  // evidence
  for (const rec of bySha.values()) {
    if (used.has(rec.sha256) || rec.class !== 'evidence') continue;
    out.push({
      id: `evidence/${candidateVersion(rec.sha256)}`,
      row: 'evidence',
      why: rec.why,
      files: [{ path: rec.paths[0], sha256: rec.sha256 }],
      copies: rec.paths.length > 1 ? rec.paths.slice(1) : undefined,
      audit: auditOf(rec),
    });
  }

  // approved art records which candidate it came from; that candidate records what it became
  rows = mergeRows(rows, out);
  const queue = fs.existsSync(REGEN_QUEUE) ? JSON.parse(fs.readFileSync(REGEN_QUEUE, 'utf8')) : { items: [] };
  settleStatuses(rows, regenBySlot(queue, plantForm));

  const tsvNotInScan = [...audit.values()].filter((t) => !bySha.has(t.sha256));
  const why = {};
  for (const t of tsvNotInScan) {
    const locs = `${t.locations};${t.repo_paths}`;
    const k = /ChirpNeighbors:assets\/approved/.test(locs) ? 'in assets/approved (already indexed)' : /ChirpNeighbors:[^;]*origin\/main/.test(locs) ? 'ChirpNeighbors origin/main outside the old roots' : /ChirpNeighbors:/.test(locs) ? 'ChirpNeighbors, other refs only (not on origin/main)' : /^disk:|;disk:/.test(locs) ? 'disk only (Codex runtime copies)' : 'other repo or Downloads';
    why[k] = (why[k] ?? 0) + 1;
  }
  return {
    rows,
    report: {
      files: files.length,
      contents: bySha.size,
      art: out.filter((r) => r.row === 'art').length,
      evidence: out.filter((r) => r.row === 'evidence').length,
      byStatus: Object.fromEntries(['candidate', 'new', 'rejected'].map((s) => [s, out.filter((r) => r.row === 'art' && r.status === s).length])),
      inbox: out.filter((r) => r.id.startsWith('inbox/')).length,
      tsv: { rows: tsvRows, inScan: tsvInScan, notInScan: why },
      claimsBy: [...out.reduce((m, r) => m.set(r.by ?? r.placedBy ?? 'unplaced', (m.get(r.by ?? r.placedBy ?? 'unplaced') ?? 0) + (r.row === 'art' ? 1 : 0)), new Map())],
    },
  };
}

export { isSlotRow, snake };
