// Scan the old art tree at a git ref: one record per distinct content (sha256) with every path it
// sits at, what png.mjs could read, and the art/evidence verdict with its reason.
import { listTree, readBlobs } from './git-blobs.mjs';
import { sha256, imageInfo, classifyImage } from './layout.mjs';

export const IMAGE_EXT = /\.(png|apng|gif|jpe?g|webp|svg)$/i;
export const OLD_ROOTS = ['assets/generated', 'docs/delivery'];

/** Prefer a path under assets/generated, then the shortest, then alphabetical. */
export const preferPath = (a, b) =>
  Number(b.startsWith('assets/generated')) - Number(a.startsWith('assets/generated')) || a.length - b.length || (a < b ? -1 : 1);

export async function scanTree(ref = 'origin/main', roots = OLD_ROOTS, { log = () => {} } = {}) {
  const files = listTree(ref, roots).filter((f) => IMAGE_EXT.test(f.path));
  const byBlob = new Map();
  for (const f of files) {
    if (!byBlob.has(f.blob)) byBlob.set(f.blob, []);
    byBlob.get(f.blob).push(f.path);
  }
  const bySha = new Map();
  let n = 0;
  await readBlobs([...byBlob.keys()], (blob, bytes) => {
    const paths = byBlob.get(blob).sort(preferPath);
    const sha = sha256(bytes);
    const isPngish = /\.a?png$/i.test(paths[0]);
    const info = isPngish ? imageInfo(bytes) : {};
    const verdicts = paths.map((p) => classifyImage(p, info));
    // one content, one verdict: art if any of its paths reads as art (a sprite copied into a
    // previews folder is still the sprite)
    const art = verdicts.findIndex((v) => v.class === 'art');
    const verdict = art >= 0 ? verdicts[art] : verdicts[0];
    const rec = bySha.get(sha) ?? { sha256: sha, paths: [], bytes: bytes.length, width: info.width, height: info.height, info };
    rec.paths.push(...paths);
    rec.paths.sort(preferPath);
    if (!rec.class || verdict.class === 'art') Object.assign(rec, { class: verdict.class, why: verdict.why, artPath: art >= 0 ? paths[art] : null });
    bySha.set(sha, rec);
    if (++n % 500 === 0) log(`  read ${n}/${byBlob.size} blobs`);
  });
  for (const rec of bySha.values()) {
    if (rec.width === undefined && /\.a?png$/i.test(rec.paths[0])) {
      // opaque PNGs skip the decode; read the size from IHDR
    }
    delete rec.info.width;
    delete rec.info.height;
  }
  return { files, bySha };
}
