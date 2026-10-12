import { mkdtempSync, rmSync, readFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { randomUUID, createHash } from 'node:crypto';
import { YardRepository } from '/workspace/archive-history/birdsong-yard-sprites/src/lib/server/storage/repository';
import { JobRepository } from '/workspace/archive-history/birdsong-yard-sprites/src/lib/server/pipeline/repository';
import { AssetLifecycleService } from '/workspace/archive-history/birdsong-yard-sprites/src/lib/server/assets/lifecycle';
import { requestBudgetFor } from '/workspace/archive-history/birdsong-yard-sprites/src/lib/server/operations/request-budget';

const root = mkdtempSync(join(tmpdir(), 'chirp-independent-history-'));
const yard = new YardRepository(join(root, 'chirp.sqlite'));
const jobs = new JobRepository(yard.database);
const lifecycle = new AssetLifecycleService(yard, jobs);
const inputs = [
  ['ascii-over-limit', ' '.repeat(1_000_001)],
  ['nul-over-limit', '\0' + 'x'.repeat(1_000_001)],
  ['utf8-over-limit', '水'.repeat(333_335)],
] as const;
const calls: string[] = [];
const get = jobs.get.bind(jobs);
try {
  const rows = inputs.map(([label, text]) => {
    const job = jobs.queue('alice', {
      definitionId: 'fixture-artwork', definitionVersion: 2,
      input: { speciesId: 'cn-species-erithacus-rubecula', label: 'Synthetic private metadata' },
      idempotencyKey: randomUUID(),
    });
    yard.database.prepare('UPDATE pip_jobs SET input_json=? WHERE id=?').run(text, job.id);
    const counts = yard.database.prepare('SELECT length(input_json) AS textLength, length(CAST(input_json AS BLOB)) AS byteLength FROM pip_jobs WHERE id=?').get(job.id);
    return { label, id: job.id, ...counts };
  });
  jobs.get = (owner, id) => { calls.push(id); return get(owner, id); };
  const result = lifecycle.packageHistory('alice', { limit: 10 });
  console.log(JSON.stringify({
    sourceSha256: createHash('sha256').update(readFileSync('/workspace/archive-history/birdsong-yard-sprites/src/lib/server/assets/lifecycle.ts')).digest('hex'),
    routeBudgets: ['GET', 'HEAD'].map(method => ({method, value: requestBudgetFor('/api/asset-lifecycle/packages', method)})),
    rows: rows.map(row => ({...row, hydratedThroughGet: calls.includes(row.id), selectionBlock: result.entries.find(e => e.state.target.id === row.id)?.selectionBlock})),
    assertion: 'Oversized corrupt input must be rejected before JobRepository.get performs SELECT * hydration.',
  }, null, 2));
} finally { yard.close(); rmSync(root, {recursive: true, force: true}); }
