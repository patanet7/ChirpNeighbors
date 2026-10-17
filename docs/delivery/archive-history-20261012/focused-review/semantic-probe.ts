import assert from 'node:assert/strict';
import { mkdtempSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { randomUUID } from 'node:crypto';
import { YardRepository } from '/workspace/archive-history/birdsong-yard-sprites/src/lib/server/storage/repository';
import { JobRepository } from '/workspace/archive-history/birdsong-yard-sprites/src/lib/server/pipeline/repository';
import { AssetLifecycleService } from '/workspace/archive-history/birdsong-yard-sprites/src/lib/server/assets/lifecycle';
import { readOwnerPage } from '/workspace/archive-history/birdsong-yard-sprites/src/lib/server/workbench/pagination';
import { assetPackageHistorySchema } from '/workspace/archive-history/birdsong-yard-sprites/src/lib/assets/lifecycle-contracts';
import { createPageNavigation } from '/workspace/archive-history/birdsong-yard-sprites/src/lib/client/page-navigation';

async function main() {
  const root = mkdtempSync(join(tmpdir(), 'chirp-independent-history-semantics-'));
  const yard = new YardRepository(join(root, 'chirp.sqlite'));
  const jobs = new JobRepository(yard.database);
  const service = new AssetLifecycleService(yard, jobs);
  const controls: string[] = [];
  const check = (name: string, run: () => void) => { run(); controls.push(name); };
  function queue(owner = 'alice') { return jobs.queue(owner, {
    definitionId: 'fixture-artwork', definitionVersion: 2,
    input: { speciesId: 'cn-species-erithacus-rubecula', label: 'Synthetic local metadata' },
    idempotencyKey: randomUUID(),
  }); }
  try {
    const ids = Array.from({length: 13}, () => queue().id);
    const bob = queue('bob');
    const first = service.packageHistory('alice', {limit: 5});
    const inserted = queue();
    yard.database.prepare('UPDATE pip_jobs SET created_at=0 WHERE id=?').run(inserted.id);
    const pages = [first];
    while(pages.at(-1)!.page.nextCursor) pages.push(service.packageHistory('alice', {limit: 5, cursor: pages.at(-1)!.page.nextCursor!}));
    check('Watermark excludes a backdated insert across all three pages', () => assert.deepEqual(pages.flatMap(p => p.entries.map(e => e.state.target.id)), ids.toReversed()));
    check('Every response is bounded to requested five entries', () => assert.ok(pages.every(p => p.entries.length <= 5 && Buffer.byteLength(JSON.stringify(p)) < 32768)));
    check('Restart includes the new insertion', () => assert.equal(service.packageHistory('alice').entries[0].state.target.id, inserted.id));
    check('Other owner sees only its own membership', () => assert.deepEqual(service.packageHistory('bob').entries.map(e => e.state.target.id), [bob.id]));
    check('Other-owner cursor rejected', () => assert.throws(() => service.packageHistory('bob', {limit: 5,cursor:first.page.cursor})));
    check('Changed page limit rejected', () => assert.throws(() => service.packageHistory('alice', {limit: 4,cursor:first.page.cursor})));
    check('Changed signature rejected', () => assert.throws(() => service.packageHistory('alice', {limit: 5,cursor:first.page.cursor+'x'})));
    const foreign=readOwnerPage(yard.database,'alice','jobs',{limit:5},id=>id);
    check('Jobs-list cursor rejected by package list', () => assert.throws(() => service.packageHistory('alice',{limit:5,cursor:foreign.page.cursor})));
    const oldest=pages.at(-1)!;
    const target={kind:'private-package' as const,id:ids[0]};
    const cmd={action:'set-archive' as const,requestId:randomUUID(),target,expectedRevision:0,archived:true};
    const before=JSON.stringify(yard.snapshot('alice'));
    const response=service.command('alice',cmd);
    check('Archive changes live state inside retained traversal', () => assert.deepEqual(service.packageHistory('alice',{limit:5,cursor:oldest.page.cursor}).entries.at(-1)!.state.archived,true));
    check('Confirmed command retry is idempotent', () => assert.equal(service.command('alice',cmd).receipt.replayed,true));
    check('Cross-owner mutation refused', () => assert.throws(()=>service.command('bob',{...cmd,requestId:randomUUID()})));
    check('Stale archive revision refused', () => assert.throws(()=>service.command('alice',{...cmd,requestId:randomUUID(),archived:false})));
    check('Archive leaves yard snapshot unchanged', () => assert.equal(JSON.stringify(yard.snapshot('alice')),before));
    check('Legacy command response has no page metadata', () => assert.deepEqual(Object.keys(response).sort(),['overview','receipt']));
    check('Every history entry prohibits cleanup and retains conservative reasons', () => assert.ok(pages.every(p=>p.referenceScan==='not-run' && !p.purgeEnabled && p.entries.every(e=>!e.cleanupEligible&&e.retainedBecause.includes('pipeline-history')&&e.retainedBecause.includes('incomplete-reference-scan')))));
    check('Contract rejects forged complete-scan authority', () => assert.equal(assetPackageHistorySchema.safeParse({...first,referenceScan:'complete'}).success,false));
    check('Contract rejects removal of mandatory retention reasons', () => {const v=structuredClone(first);v.entries[0].retainedBecause=['active'];assert.equal(assetPackageHistorySchema.safeParse(v).success,false);});
    check('Contract rejects owner injection', () => assert.equal(assetPackageHistorySchema.safeParse({...first,owner:'bob'}).success,false));

    const pending: {request: unknown; resolve: (value: typeof first)=>void; reject: (error: Error)=>void}[]=[];
    const states: unknown[]=[];
    const nav=createPageNavigation(first,(request)=>new Promise((resolve,reject)=>pending.push({request,resolve,reject})),s=>states.push(s));
    const next=nav.next(); const restarted=nav.refresh();
    pending[1].resolve(first); await restarted; const count=states.length;
    pending[0].resolve(oldest); await next;
    check('Delayed previous response cannot replace newer restart',()=>assert.equal(states.length,count));
    const current=nav.current(); pending[2].reject(new Error('Synthetic failed read'));await current;
    const last=states.at(-1) as {value:typeof first,error:string};
    check('Failed current-page refresh retains confirmed rows',()=>assert.equal(last.value,first));
    const retry=nav.retry();
    check('Failed current-page retry keeps exact request',()=>assert.deepEqual(pending[3].request,pending[2].request));
    pending[3].resolve(first);await retry;
    const late=nav.next();nav.destroy();const destroyedCount=states.length;pending[4].resolve(oldest);await late;
    check('Unmount discards late response',()=>assert.equal(states.length,destroyedCount));
    console.log(JSON.stringify({passed:controls.length,controls,scope:'Disposable local SQLite and transport promises; no server, browser, external request or repository write'},null,2));
  } finally {yard.close();rmSync(root,{recursive:true,force:true});}
}
main().catch(error=>{console.error(error);process.exitCode=1;});
