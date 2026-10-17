/** Read-only cross-repository release check; only synthetic in-memory yards. */
import { createRequire } from "node:module";
import {
  mkdtempSync,
  readFileSync,
  readdirSync,
  rmSync,
  writeFileSync,
} from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { spawnSync } from "node:child_process";
import assert from "node:assert/strict";

const canonical = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const ui = resolve(process.argv[2] ?? "../birdsong-yard-sprites");
const python = process.argv[3] ?? "python3";
const requireUI = createRequire(join(ui, "package.json"));
const schemas = (root) =>
  readdirSync(join(root, "contracts")).filter((name) =>
    name.endsWith(".schema.json"),
  );
const missing = schemas(ui).filter(
  (name) => !schemas(canonical).includes(name),
);
assert.deepEqual(missing, [], "Canonical mirror is missing runtime schemas");
const shared = schemas(ui).filter((name) => schemas(canonical).includes(name));
assert(shared.length > 100, "Expected the complete shared schema set");
for (const name of shared)
  assert(
    readFileSync(join(ui, "contracts", name), "utf8") ===
      readFileSync(join(canonical, "contracts", name), "utf8"),
    `Schema drift: ${name}`,
  );
const dir = mkdtempSync(join(tmpdir(), "chirp-contract-sync-"));
try {
  requireUI("esbuild").buildSync({
    entryPoints: [join(canonical, "scripts/runtime_contract_sync_probe.ts")],
    alias: { "@chirp-runtime": join(ui, "src") },
    bundle: true,
    platform: "node",
    format: "cjs",
    outfile: join(dir, "probe.cjs"),
    logLevel: "silent",
  });
  const run = spawnSync(
    process.execPath,
    [join(dir, "probe.cjs"), ui, canonical],
    { encoding: "utf8" },
  );
  assert.equal(run.status, 0, run.stderr || run.stdout);
  const corpus = JSON.parse(run.stdout);
  writeFileSync(join(dir, "corpus.json"), JSON.stringify(corpus));
  const validation = spawnSync(
    python,
    [
      join(canonical, "scripts/check_runtime_sync_corpus.py"),
      join(dir, "corpus.json"),
    ],
    { encoding: "utf8", env: { ...process.env, PYTHONDONTWRITEBYTECODE: "1" } },
  );
  assert.equal(validation.status, 0, validation.stderr || validation.stdout);
  console.log(
    JSON.stringify(
      {
        sharedSchemas: shared.length,
        ...JSON.parse(validation.stdout),
        migration: corpus.migration,
        roundtrip: corpus.roundtrip,
      },
      null,
      2,
    ),
  );
} finally {
  rmSync(dir, { recursive: true, force: true });
}
