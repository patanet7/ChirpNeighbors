// `assets queue-review`: the review page's data (same shape as _chirp-work/chirp-review/
// review-data.json, built by prep.mjs) generated from the index. Existing review slot ids are kept,
// with their candidates, so the owner's decisions still line up; the index adds plant, scene and
// weather slots, new candidates, and an Unsorted group for art with no slot yet.
import fs from 'node:fs';
import path from 'node:path';
import { isSlotRow, parseId, reviewToSlot, CORRECTED_REVIEW_SLOTS } from './layout.mjs';
import { decodePng, encodePng } from './png.mjs';
import { listTree, readBlobs } from './git-blobs.mjs';

export const GROUPS = [
  { id: 'birds', label: 'Birds', note: 'bird slots keep their species as `group` (the bird grid); `section` is birds' },
  { id: 'objects', label: 'Objects' },
  { id: 'plants', label: 'Plants and trees' },
  { id: 'scenes', label: 'Backgrounds and weather' },
  { id: 'unsorted', label: 'Unsorted' },
];
const THUMB = 320;

/** Box-filter downscale (premultiplied alpha) so the longest side is at most `max`. */
export function thumbnail(img, max = THUMB) {
  const k = Math.max(1, Math.ceil(Math.max(img.width, img.height) / max));
  if (k === 1) return img;
  const w = Math.max(1, Math.floor(img.width / k));
  const h = Math.max(1, Math.floor(img.height / k));
  const out = new Uint8Array(w * h * 4);
  for (let y = 0; y < h; y++)
    for (let x = 0; x < w; x++) {
      let r = 0, g = 0, b = 0, a = 0;
      for (let dy = 0; dy < k; dy++)
        for (let dx = 0; dx < k; dx++) {
          const i = ((y * k + dy) * img.width + (x * k + dx)) * 4;
          const al = img.data[i + 3];
          r += img.data[i] * al;
          g += img.data[i + 1] * al;
          b += img.data[i + 2] * al;
          a += al;
        }
      const o = (y * w + x) * 4;
      if (a) {
        out[o] = Math.round(r / a);
        out[o + 1] = Math.round(g / a);
        out[o + 2] = Math.round(b / a);
      }
      out[o + 3] = Math.round(a / (k * k));
    }
  return { width: w, height: h, data: out };
}

const sectionOf = (kind) => (kind === 'birds' ? 'birds' : kind === 'objects' ? 'objects' : kind === 'plants' ? 'plants' : kind === 'scenes' ? 'scenes' : 'unsorted');
const safe = (s) => s.replace(/[^a-z0-9_.-]+/gi, '_');
const titleCase = (s) => String(s).replace(/_/g, ' ').replace(/^./, (c) => c.toUpperCase());

function slotLabel(r, subject) {
  const p = parseId(r.id);
  const name = subject?.label ?? titleCase(p.name);
  if (p.kind === 'plants') return `${name} · ${p.form}${p.season !== 'all' ? `, ${p.season}` : ''}${p.state ? `, ${p.state}` : ''}`;
  if (p.kind === 'scenes') return `${name} · ${p.season === 'all' ? 'any season' : p.season}${p.state ? `, ${p.state}` : ''} · ${p.layer}`;
  if (p.kind === 'birds') return `${name} ${p.act}`;
  return name;
}

export async function queueReview({ rows, live, decisions, imgDir, ref = 'origin/main', log = console.log }) {
  const byId = new Map(rows.map((r) => [r.id, r]));
  const subjectOf = (id) => byId.get(parseId(id).subject);
  const liveById = new Map(live.slots.map((s) => [s.id, s]));
  const decided = decisions ? Object.keys(decisions) : [];

  // review slots: every live slot (except the corrected wrong names, when undecided), then new ones
  const slots = [];
  const reviewSlot = new Map(); // index slot id -> the review slot its new candidates join
  const moved = [];
  for (const s of live.slots) {
    if (CORRECTED_REVIEW_SLOTS[s.id] && !decided.includes(s.id)) {
      moved.push(s);
      continue;
    }
    const target = reviewToSlot(s.id, (name) => {
      const base = rows.find((r) => r.row === 'slot' && r.id.startsWith(`plants/${name}/`));
      return base ? parseId(base.id).form : 'mature';
    });
    const kind = target ? parseId(target).kind : null;
    const out = { ...s, section: s.species ? 'birds' : sectionOf(kind), indexSlot: target ?? null };
    if (!s.species) out.group = out.section;
    slots.push(out);
    if (target && !reviewSlot.has(target)) reviewSlot.set(target, out);
  }
  for (const r of rows) {
    if (!isSlotRow(r) || reviewSlot.has(r.id)) continue;
    const p = parseId(r.id);
    if (p.kind === 'birds') continue; // the 15-act grid already has every bird slot
    const subject = subjectOf(r.id);
    const out = {
      id: r.id,
      group: sectionOf(p.kind),
      section: sectionOf(p.kind),
      species: null,
      name: null,
      action: null,
      label: slotLabel(r, subject),
      needed: true,
      status: 'empty',
      flags: [],
      note: r.note ?? r.regen?.note ?? undefined,
      indexSlot: r.id,
      candidates: [],
    };
    slots.push(out);
    reviewSlot.set(r.id, out);
  }
  // the corrected slots' candidates join the real slot
  for (const s of moved) {
    const target = reviewSlot.get(CORRECTED_REVIEW_SLOTS[s.id].slot);
    for (const c of s.candidates) if (!target.candidates.some((x) => x.id === c.id)) target.candidates.push({ ...c, rank: target.candidates.length + 1, movedFrom: s.id });
  }

  // new candidates from the index
  const thumbs = []; // { file, path }
  const addCandidate = (slot, art) => {
    const sha8 = art.id.split('/').pop().replace(/^c/, '');
    if (slot.candidates.some((c) => c.id === sha8)) return;
    const f = art.files[0];
    const preview = `${safe(slot.id)}__${slot.candidates.length + 1}__${sha8}.png`;
    thumbs.push({ file: preview, path: f.path });
    slot.candidates.push({
      rank: slot.candidates.length + 1,
      id: sha8,
      kind: art.frames ? 'frames' : art.layers ? 'layered' : 'still',
      preview,
      dims: f.width ? `${f.width}x${f.height}` : null,
      pack: art.made?.pack ?? null,
      codexStatus: art.audit?.status ?? null,
      codexReason: art.audit?.reason ?? null,
      ownerApproved: art.status === 'approved',
      ownerRejected: art.status === 'rejected',
      ...(art.frames ? { frames: art.frames } : {}),
      ...(art.layers ? { layers: art.layers } : {}),
      source: art.made?.from ?? f.path,
      ...(art.label ? { label: art.label } : {}),
      ...(art.part ? { part: art.part } : {}),
      ...(art.guess ? { guess: art.guess } : {}),
    });
    if (slot.status === 'empty') slot.status = 'needs_review';
  };
  for (const r of rows) {
    if (r.row !== 'art' || r.status === 'approved' || r.status === 'new' || !r.slot) continue;
    const slot = reviewSlot.get(r.slot);
    if (slot) addCandidate(slot, r);
  }
  // unsorted: one card per subject (or per pack for art with no subject)
  const unsorted = new Map();
  for (const r of rows) {
    if (r.row !== 'art' || r.status !== 'new') continue;
    const p = parseId(r.id);
    const key = p.subject ? `unsorted/${p.subject}` : `unsorted/inbox/${safe(r.made?.pack ?? 'other')}`;
    if (!unsorted.has(key)) {
      const subject = p.subject ? byId.get(p.subject) : null;
      unsorted.set(key, {
        id: key,
        group: 'unsorted',
        section: 'unsorted',
        species: null,
        name: null,
        action: null,
        label: p.subject ? `Unsorted · ${subject?.label ?? titleCase(p.name)}` : `Unsorted · ${r.made?.pack ?? 'other'}`,
        needed: false,
        status: 'empty',
        flags: [],
        subject: p.subject ?? null,
        candidates: [],
      });
    }
    addCandidate(unsorted.get(key), r);
  }
  for (const s of [...unsorted.values()].sort((a, b) => (a.id < b.id ? -1 : 1))) {
    s.label += ` (${s.candidates.length})`;
    slots.push(s);
  }

  // previews: thumbnails straight from git (only files not already in imgDir)
  fs.mkdirSync(imgDir, { recursive: true });
  const todo = thumbs.filter((t) => !fs.existsSync(path.join(imgDir, t.file)));
  const tree = new Map(listTree(ref, [...new Set(todo.map((t) => t.path.split('/').slice(0, 2).join('/')))]).map((f) => [f.path, f.blob]));
  const byBlob = new Map();
  for (const t of todo) {
    const blob = tree.get(t.path);
    if (!blob) continue;
    if (!byBlob.has(blob)) byBlob.set(blob, []);
    byBlob.get(blob).push(t.file);
  }
  const failed = new Set();
  let written = 0;
  await readBlobs([...byBlob.keys()], (blob, bytes) => {
    let png;
    try {
      png = encodePng(thumbnail(decodePng(bytes)));
    } catch {
      byBlob.get(blob).forEach((f) => failed.add(f));
      return;
    }
    for (const f of byBlob.get(blob)) {
      fs.writeFileSync(path.join(imgDir, f), png);
      written++;
    }
    if (written % 250 === 0) log(`  ${written} previews`);
  });
  for (const t of todo) if (!tree.get(t.path)) failed.add(t.file);
  for (const s of slots) s.candidates = s.candidates.filter((c) => !c.preview || !failed.has(c.preview));

  const ids = new Set(slots.map((s) => s.id));
  const missing = decided.filter((id) => !ids.has(id));
  const data = {
    generated: new Date().toISOString().slice(0, 10),
    groups: GROUPS.map((g) => ({ ...g, slots: slots.filter((s) => s.section === g.id).length })),
    slots,
    packs: live.packs,
    owner: live.owner,
    ...(live.sanDiego ? { sanDiego: live.sanDiego } : {}),
  };
  return { data, report: { slots: slots.length, newPreviews: written, failedPreviews: failed.size, moved: moved.map((s) => s.id), missing, decided: decided.length, images: [...new Set(slots.flatMap((s) => s.candidates.map((c) => c.preview)).filter((p) => p && !/^(sd:|\/|https?:)/.test(p)))].sort() } };
}
