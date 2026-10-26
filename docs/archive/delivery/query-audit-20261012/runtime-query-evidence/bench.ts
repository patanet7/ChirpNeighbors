import { YardRepository } from '../birdsong-yard-sprites/src/lib/server/storage/repository';
import { ArrivalRepository } from '../birdsong-yard-sprites/src/lib/server/arrivals/repository';
import { emptyYard, yardDataSchema, yardSnapshotSchema, snapshotOf } from '../birdsong-yard-sprites/src/lib/domain/yard';
import { yardPageDataSchema } from '../birdsong-yard-sprites/src/lib/client/yard-page';
import { DatabaseSync } from 'node:sqlite';
import { mkdtempSync, writeFileSync, statSync } from 'node:fs';
import { join } from 'node:path';
import { tmpdir } from 'node:os';
import { randomUUID } from 'node:crypto';
import { Worker } from 'node:worker_threads';

const out = process.argv[2];
if (!out) throw new Error('Evidence output directory required');
const storage = mkdtempSync(join(tmpdir(), 'chirp-query-audit-'));
const now = '2026-10-12T12:00:00.000Z';
const results: any = { node: process.version, storage, scope: 'Exact repository/domain code; no server, auth, assets, jobs, providers, or real data.', warmups: 1, repeats: 7, cases: [], batches: [], contention: [], probes: [] };
const flush = () => writeFileSync(join(out, 'measurements.json'), JSON.stringify(results, null, 2) + '\n');
const species = { id: 'cn-species-erithacus-rubecula', commonName: 'European Robin', scientificName: 'Erithacus rubecula' };
function dataFor(count: number) {
  const data = emptyYard();
  data.species = [species];
  data.events = Array.from({ length: count }, (_, index) => ({ schemaVersion: 2 as const, id: `audit-event:${index}`, species, observedAt: '2026-10-01T12:00:00.000Z', ingestedAt: now, source: { kind: 'external' as const, label: 'Synthetic audit evidence', sourceEventId: `audit-source:${index}` }, metadata: { note: 'Synthetic observation for local query measurement.' } }));
  data.birds = [{ id: 'audit-bird', speciesId: species.id, name: 'Synthetic resident', lifecycle: 'permanent', createdAt: now, promotedAt: now, expiresAt: null, artworkId: null, originEventId: count ? `audit-event:${count - 1}` : null }];
  return yardDataSchema.parse(data);
}
function instrument(db: DatabaseSync) {
  const capture: any = { enabled: false, statements: [], returnedRows: 0, returnedTextBytes: 0 };
  const prepare = db.prepare.bind(db), exec = db.exec.bind(db);
  db.prepare = ((sql: string) => {
    const statement = prepare(sql);
    for (const method of ['get', 'all', 'run'] as const) {
      const original = statement[method].bind(statement);
      (statement as any)[method] = (...args: any[]) => {
        if (capture.enabled) capture.statements.push({ method, sql });
        const value = original(...args);
        if (capture.enabled && method !== 'run') {
          const rows = method === 'all' ? value : value ? [value] : [];
          capture.returnedRows += rows.length;
          for (const row of rows) for (const item of Object.values(row)) if (typeof item === 'string') capture.returnedTextBytes += Buffer.byteLength(item);
        }
        return value;
      };
    }
    return statement;
  }) as typeof db.prepare;
  db.exec = ((sql: string) => { if (capture.enabled) capture.statements.push({ method: 'exec', sql }); return exec(sql); }) as typeof db.exec;
  return {
    begin() { capture.statements = []; capture.returnedRows = 0; capture.returnedTextBytes = 0; capture.enabled = true; },
    end() { capture.enabled = false; return { statements: capture.statements, returnedRows: capture.returnedRows, returnedTextBytes: capture.returnedTextBytes }; },
  };
}
function timed(action: () => unknown, repeats = 7) {
  action();
  const samples = [];
  for (let index = 0; index < repeats; index++) { const start = performance.now(); action(); samples.push(performance.now() - start); }
  const ordered = [...samples].sort((a, b) => a - b);
  return { medianMs: ordered[Math.floor(ordered.length / 2)], minMs: ordered[0], maxMs: ordered.at(-1), samplesMs: samples };
}
function traced(trace: ReturnType<typeof instrument>, action: () => unknown) { trace.begin(); const start = performance.now(); const result = action(); const elapsedMs = performance.now() - start; return { result, elapsedMs, ...trace.end() }; }
for (const count of [100, 1000, 10000, 30000]) {
  const path = join(storage, `owner-${count}.sqlite`), yard = new YardRepository(path);
  const arrivals = new ArrivalRepository(yard.database, (owner, clock) => yard.snapshot(owner, clock));
  const trace = instrument(yard.database), seed = dataFor(count), serialized = JSON.stringify(seed);
  if (Buffer.byteLength(serialized) > 16 * 1024 * 1024) throw new Error('Synthetic case exceeds actual write budget');
  const insert = yard.database.prepare('INSERT OR REPLACE INTO yard_owners VALUES(?,2,?)');
  const reset = () => insert.run('audit-owner', serialized);
  reset();
  const snapshot = yard.snapshot('audit-owner', now), snapshotJson = JSON.stringify({ snapshot, assets: [] });
  const page = { identity: { mode: 'development', ownerId: 'audit-owner', label: 'Synthetic audit owner' }, authMode: 'development', snapshot, assets: [], jobs: [], arrivals: { schemaVersion: 1, kind: 'yard.arrivals', arrivals: [] } };
  const readTrace = traced(trace, () => yard.snapshot('audit-owner', now));
  const arrivalTrace = traced(trace, () => arrivals.list('audit-owner', now));
  const record: any = { events: count, residents: 1, objects: seed.environment.objects.length, storedBytes: Buffer.byteLength(serialized), snapshotResponseBytes: Buffer.byteLength(snapshotJson), sqlLookup: timed(() => yard.database.prepare('SELECT schema_version,data FROM yard_owners WHERE owner_id=?').get('audit-owner')), jsonParse: timed(() => JSON.parse(serialized)), storedValidation: timed(() => yardDataSchema.parse(seed)), snapshotDerivation: timed(() => snapshotOf(seed, now)), repositorySnapshot: timed(() => yard.snapshot('audit-owner', now)), snapshotJsonSerialization: timed(() => JSON.stringify({ snapshot, assets: [] })), snapshotBoundaryValidation: timed(() => yardSnapshotSchema.parse(snapshot), 3), pageBoundaryValidation: timed(() => yardPageDataSchema.parse(page), 3), emptyArrivalList: timed(() => arrivals.list('audit-owner', now)), snapshotSql: { ...readTrace, result: undefined }, arrivalSql: { ...arrivalTrace, result: undefined } };
  const renameTrace = traced(trace, () => yard.rename('audit-owner', 'audit-bird', 'Renamed synthetic resident', now));
  record.rename = { ...renameTrace, result: undefined };
  record.renameLatency = timed(() => yard.rename('audit-owner', 'audit-bird', 'Renamed synthetic resident', now));
  record.preferenceLatency = timed(() => yard.updatePreferences('audit-owner', { reducedMotion: true }, now));
  reset();
  const object = seed.environment.objects[0];
  const command = { action: 'object-inventory', requestId: randomUUID(), expected: { scene: seed.preferences.scene, scenePin: seed.preferences.scenePin, objects: seed.environment.objects }, payload: { operation: 'move', objectId: object.id, x: object.x, y: object.y } };
  yard.objectInventory('audit-owner', command, now);
  const changesBefore = yard.database.prepare('SELECT total_changes() AS n').get()!.n;
  const retry = traced(trace, () => yard.objectInventory('audit-owner', command, now));
  record.exactInventoryRetry = { ...retry, result: undefined, rowChanges: Number(yard.database.prepare('SELECT total_changes() AS n').get()!.n) - Number(changesBefore) };
  record.exactInventoryRetryLatency = timed(() => yard.objectInventory('audit-owner', command, now));
  record.explainOwner = yard.database.prepare('EXPLAIN QUERY PLAN SELECT schema_version,data FROM yard_owners WHERE owner_id=?').all('audit-owner');
  record.explainArrivals = yard.database.prepare("EXPLAIN QUERY PLAN SELECT arrival_id FROM yard_arrivals WHERE owner_id=? AND state='pending' AND json_extract(payload_json,'$.eligibleUntil')>? ORDER BY json_extract(payload_json,'$.admittedAt'),arrival_id LIMIT ?").all('audit-owner', now, 20);
  record.schema = yard.database.prepare("SELECT type,name,sql FROM sqlite_schema WHERE name NOT LIKE 'sqlite_%' ORDER BY name").all();
  record.pragmas = { journal: yard.database.prepare('PRAGMA journal_mode').get(), busy: yard.database.prepare('PRAGMA busy_timeout').get(), sqlite: yard.database.prepare('SELECT sqlite_version() AS version').get() };
  results.cases.push(record); flush();
  console.log(JSON.stringify({ events: count, storedBytes: record.storedBytes, snapshotMs: record.repositorySnapshot.medianMs, pageValidationMs: record.pageBoundaryValidation.medianMs, renameMs: record.renameLatency.medianMs, inventoryRetryMs: record.exactInventoryRetryLatency.medianMs }), flush);
  if (count === 100 || count === 10000) {
    for (const size of [1, 100, 1000]) {
      reset();
      const incoming = seed.events.slice(-size).map(({ ingestedAt, ...event }) => event);
      const started = performance.now(); trace.begin();
      const duplicate = yard.importEvents('audit-owner', incoming, now);
      results.batches.push({ events: count, requestedBatch: size, actualBatch: incoming.length, operation: 'exact-duplicate-import', elapsedMs: performance.now() - started, inserted: duplicate.inserted, duplicates: duplicate.duplicates, ...trace.end() }); flush();
    }
    for (const size of [1, 100]) {
      reset();
      const corrections = seed.events.slice(-size).map(event => ({ schemaVersion: 1, id: randomUUID(), eventId: event.id, expected: { correctionId: null, speciesId: species.id, observedAt: event.observedAt }, replacement: { speciesId: species.id, observedAt: null }, reason: 'Synthetic audit correction' }));
      const start = performance.now(); trace.begin();
      const corrected = yard.correctEvents('audit-owner', corrections, now);
      results.batches.push({ events: count, actualBatch: corrections.length, operation: 'append-correction', elapsedMs: performance.now() - start, inserted: corrected.inserted, ...trace.end() }); flush();
    }
  }
  yard.close();
}

// Same process scheduler: independent SQLite worker owns the writer lock while the
// exact YardRepository operation waits synchronously. A timer models unrelated work.
const lockPath = join(storage, 'contention.sqlite'), yard = new YardRepository(lockPath);
const seed = dataFor(100), json = JSON.stringify(seed);
for (const owner of ['audit-owner-a', 'audit-owner-b']) yard.database.prepare('INSERT INTO yard_owners VALUES(?,2,?)').run(owner, json);
for (const holdMs of [250, 5500]) {
  const worker = new Worker(`const {parentPort,workerData}=require('node:worker_threads'); const {DatabaseSync}=require('node:sqlite'); const db=new DatabaseSync(workerData.path); db.exec('BEGIN IMMEDIATE'); db.prepare('UPDATE yard_owners SET data=data WHERE owner_id=?').run('audit-owner-a'); parentPort.postMessage('locked'); setTimeout(()=>{db.exec('COMMIT');db.close();parentPort.postMessage('released')},workerData.holdMs);`, { eval: true, workerData: { path: lockPath, holdMs } });
  const released = new Promise<void>((resolve, reject) => { worker.on('message', m => { if(m === 'released') resolve(); }); worker.on('error', reject); });
  await new Promise<void>((resolve, reject) => { worker.on('message', m => { if(m === 'locked') resolve(); }); worker.on('error', reject); });
  const readStart = performance.now();
  const read = yard.snapshot('audit-owner-b', now);
  const readDuringWriterMs = performance.now() - readStart;
  const started = performance.now();
  const timer = new Promise<number>(resolve => setTimeout(() => resolve(performance.now() - started), 10));
  let failure: any = null;
  try { yard.rename('audit-owner-b', 'audit-bird', 'Contention renamed', now); } catch (error: any) { failure = { name: error.name, message: error.message, code: error.code, errcode: error.errcode, errstr: error.errstr }; }
  const writeElapsedMs = performance.now() - started;
  const timerElapsedMs = await timer;
  await released;
  const entry = { heldOwner: 'audit-owner-a', attemptedOwner: 'audit-owner-b', holdMs, readDuringWriterMs, readEvents: read.events.length, writeElapsedMs, tenMsTimerActualMs: timerElapsedMs, failure, transactionOpenAfter: yard.database.isTransaction };
  results.contention.push(entry); flush(); console.log(JSON.stringify(entry));
}
yard.close();
results.finished = true; flush();
