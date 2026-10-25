#!/usr/bin/env node
// Reproduce using existing installed dependencies. No installs or source changes.
import { createRequire } from 'node:module';
import { fileURLToPath } from 'node:url';
import { dirname, resolve, join } from 'node:path';
import { mkdirSync, writeFileSync, readFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { execFileSync } from 'node:child_process';
const here = dirname(fileURLToPath(import.meta.url));
const root = resolve(here, '../birdsong-yard-sprites');
const output = process.argv[2];
if (!output || !output.startsWith('/tmp/')) throw new Error('Supply a new absolute /tmp output directory.');
mkdirSync(output, { recursive: false });
const { build } = createRequire(join(root, 'package.json'))('esbuild');
for (const name of ['bench', 'probes']) {
  const result = await build({ absWorkingDir: root, entryPoints: [join(here, `${name}.ts`)], bundle: true, platform: 'node', format: 'esm', target: 'node24', alias: { $lib: join(root, 'src/lib') }, outfile: join(output, `${name}.mjs`), metafile: true });
  const hashes = {};
  for (const path of Object.keys(result.metafile.inputs)) if (!path.includes('node_modules/')) hashes[path] = createHash('sha256').update(readFileSync(resolve(root, path))).digest('hex');
  writeFileSync(join(output, `${name}-source-hashes.json`), JSON.stringify(hashes, null, 2) + '\n');
  execFileSync(process.execPath, [join(output, `${name}.mjs`), output], { stdio: 'inherit' });
}
