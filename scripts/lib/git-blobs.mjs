// Read files straight from git (no checkout, no LFS): list a tree, stream blobs through one
// `git cat-file --batch` process.
import { execFileSync, spawn } from 'node:child_process';
import { REPO } from './approved-layout.mjs';

/** [{ blob, path, size }] for every file under `roots` at `ref`. */
export function listTree(ref, roots, repo = REPO) {
  const out = execFileSync('git', ['-C', repo, 'ls-tree', '-r', '-l', '-z', ref, '--', ...roots], { maxBuffer: 1 << 30 });
  return out
    .toString('utf8')
    .split('\0')
    .filter(Boolean)
    .map((line) => {
      const tab = line.indexOf('\t');
      const [, type, blob, size] = line.slice(0, tab).trim().split(/\s+/);
      return type === 'blob' ? { blob, path: line.slice(tab + 1), size: Number(size) } : null;
    })
    .filter(Boolean);
}

/** Calls onBlob(blobSha, bytes) for each sha, in order; resolves when all are read. */
export function readBlobs(shas, onBlob, repo = REPO) {
  return new Promise((resolve, reject) => {
    const git = spawn('git', ['-C', repo, 'cat-file', '--batch'], { stdio: ['pipe', 'pipe', 'inherit'] });
    let buf = Buffer.alloc(0);
    let want = null; // { sha, size }
    let done = 0;
    git.stdout.on('data', (chunk) => {
      buf = buf.length ? Buffer.concat([buf, chunk]) : chunk;
      for (;;) {
        if (!want) {
          const nl = buf.indexOf(10);
          if (nl < 0) break;
          const head = buf.subarray(0, nl).toString('utf8').split(' ');
          buf = buf.subarray(nl + 1);
          if (head[1] === 'missing') {
            done++;
            continue;
          }
          want = { sha: head[0], size: Number(head[2]) };
        }
        if (buf.length < want.size + 1) break;
        const bytes = Buffer.from(buf.subarray(0, want.size));
        buf = buf.subarray(want.size + 1);
        try {
          onBlob(want.sha, bytes);
        } catch (err) {
          git.kill();
          return reject(err);
        }
        want = null;
        done++;
      }
    });
    git.on('error', reject);
    git.on('close', (code) => (code === 0 || done === shas.length ? resolve(done) : reject(Error(`git cat-file exited ${code}`))));
    git.stdin.end(shas.join('\n') + '\n');
  });
}

/** One blob's bytes by path. */
export const showFile = (ref, file, repo = REPO) => execFileSync('git', ['-C', repo, 'show', `${ref}:${file}`], { maxBuffer: 1 << 30 });
