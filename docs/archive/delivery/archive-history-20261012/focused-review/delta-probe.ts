import assert from 'node:assert/strict';
import { mkdtempSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { randomUUID } from 'node:crypto';
import { DatabaseSync } from 'node:sqlite';
import { YardRepository } from '/workspace/archive-history/birdsong-yard-sprites/src/lib/server/storage/repository';
import { JobRepository } from '/workspace/archive-history/birdsong-yard-sprites/src/lib/server/pipeline/repository';
import { AssetLifecycleService } from '/workspace/archive-history/birdsong-yard-sprites/src/lib/server/assets/lifecycle';
import { initialJobPage, jobPage } from '/workspace/archive-history/birdsong-yard-sprites/src/lib/server/workbench/jobs';
import { fixtureEvents } from '/workspace/archive-history/birdsong-yard-sprites/src/lib/fixtures';
import { fixtureManifest } from '/workspace/archive-history/birdsong-yard-sprites/src/lib/assets/fixtures';
import { yardReadResponseSchema, yardCommandResponseSchema } from '/workspace/archive-history/birdsong-yard-sprites/src/lib/client/contracts';
import { createPageNavigation } from '/workspace/archive-history/birdsong-yard-sprites/src/lib/client/page-navigation';

async function main() {
  const root=mkdtempSync(join(tmpdir(),'chirp-history-delta-review-'));
  const yard=new YardRepository(join(root,'chirp.sqlite'));
  const jobs=new JobRepository(yard.database);
  const service=new AssetLifecycleService(yard,jobs);
  const writer=new DatabaseSync(join(root,'chirp.sqlite'));
  yard.database.exec('PRAGMA busy_timeout=25');writer.exec('PRAGMA busy_timeout=25');
  const results:string[]=[];
  const check=(name:string,fn:()=>void)=>{fn();results.push(name);};
  function queue(owner='alice') {return jobs.queue(owner,{definitionId:'fixture-artwork',definitionVersion:2,input:{speciesId:'cn-species-erithacus-rubecula',label:'Synthetic metadata'},idempotencyKey:randomUUID()});}
  try {
    const job=queue();
    const target={kind:'private-package' as const,id:job.id};
    service.command('alice',{action:'set-archive',requestId:randomUUID(),target,expectedRevision:0,archived:true});
    writer.exec('BEGIN IMMEDIATE');
    writer.prepare('UPDATE asset_archives SET archived=0,revision=2 WHERE target_id=?').run(job.id);
    check('Standalone history reads committed state while another connection holds writer lock',()=>assert.equal(service.packageHistory('alice').entries[0].state.revision,1));
    check('Standalone overview also reads committed state under writer lock',()=>assert.equal(service.overview('alice').entries[0].state.archived,true));
    check('Lifecycle write still requires exclusive writer admission',()=>assert.throws(()=>service.command('alice',{action:'set-archive',requestId:randomUUID(),target,expectedRevision:1,archived:false}),/locked/));
    writer.exec('ROLLBACK');
    const snapshot=yard.snapshot.bind(yard);
    yard.snapshot=(owner,...args)=>{
      const value=snapshot(owner,...args);
      writer.exec('BEGIN IMMEDIATE');
      writer.prepare('UPDATE asset_archives SET archived=0,revision=2 WHERE target_id=?').run(job.id);
      writer.exec('COMMIT');return value;
    };
    const frozen=service.packageHistory('alice');
    yard.snapshot=snapshot;
    check('History keeps one snapshot if concurrent archive commits between yard and membership reads',()=>assert.equal(frozen.entries[0].state.revision,1));
    check('Following history transaction observes newly committed revision',()=>assert.equal(service.packageHistory('alice').entries[0].state.revision,2));
    const write=service.command('alice',{action:'set-archive',requestId:randomUUID(),target,expectedRevision:2,archived:true});
    check('Nested command overview sees its own write and caller commits once',()=>{assert.equal(write.overview.entries[0].state.revision,3);assert.equal(yard.database.isTransaction,false);});

    const tables=['pip_jobs','pip_artifacts','pip_reviews','pip_migrations'];
    const rows=()=>tables.map(t=>yard.database.prepare(`SELECT * FROM ${t} ORDER BY rowid`).all());
    const before=rows();yard.database.exec('DROP INDEX pip_artifacts_owner_job');
    new JobRepository(yard.database);
    check('Adding artifact index preserves retained rows and migration version',()=>assert.deepEqual(rows(),before));
    check('New artifact index is nonunique with exact owner/job/order columns',()=>{
      assert.deepEqual(yard.database.prepare("PRAGMA index_info('pip_artifacts_owner_job')").all().map(r=>r.name),['owner_id','job_id','created_at','version']);
      assert.equal(yard.database.prepare("PRAGMA index_list('pip_artifacts')").all().find(r=>r.name==='pip_artifacts_owner_job')?.unique,0);
    });
    const plan=yard.database.prepare('EXPLAIN QUERY PLAN SELECT * FROM pip_artifacts WHERE owner_id=? AND job_id=? ORDER BY created_at,version').all('alice',job.id).map(r=>String(r.detail)).join('\n');
    check('Owner/job artifact lookup uses new index without a sorting scan',()=>{assert.match(plan,/pip_artifacts_owner_job \(owner_id=\? AND job_id=\?\)/);assert.doesNotMatch(plan,/SCAN |TEMP B-TREE/);});
    new JobRepository(yard.database);
    check('Repeated startup keeps index and data unchanged',()=>assert.deepEqual(rows(),before));

    jobs.db.prepare('UPDATE pip_jobs SET input_digest=? WHERE id=?').run('corrupt',job.id);
    check('Strict API job page still rejects corrupt job',()=>assert.throws(()=>jobPage(jobs,'alice')));
    check('Initial fallback omits cursor and does not admit corrupt row',()=>assert.deepEqual(initialJobPage(jobs,'alice'),{jobs:[]}));
    check('Other owner has a normal empty page with real metadata',()=>{const p=initialJobPage(jobs,'bob');assert.deepEqual(p.jobs,[]);assert.ok(p.page);});
    check('Invalid owner cannot be hidden by initial fallback',()=>assert.throws(()=>initialJobPage(jobs,'')));
    check('Fallback does not alter corrupt row',()=>assert.equal(jobs.db.prepare('SELECT input_digest FROM pip_jobs WHERE id=?').get(job.id)?.input_digest,'corrupt'));
    jobs.db.prepare('UPDATE pip_jobs SET input_digest=? WHERE id=?').run(job.inputDigest,job.id);
    check('Explicit new read recovers after unrelated metadata is repaired',()=>assert.equal(initialJobPage(jobs,'alice').jobs[0].id,job.id));

    const now='2026-10-12T12:00:00.000Z';
    yard.importEvents('alice',fixtureEvents(yard.snapshot('alice',now),now),now);
    const value=yard.snapshot('alice',now),speciesId=value.species[0].id;
    const catalogPin={catalogKey:'a'.repeat(64),releaseVersion:1,renderSha256:'b'.repeat(64)};
    value.artworks.push({id:'art:shared-review',speciesId,version:1,status:'fixture',imageUrl:'/placeholder.svg',representation:'Synthetic retained fixture',provenance:{},catalogPin});
    value.birds.push({id:'bird:shared-review',speciesId,name:null,lifecycle:'permanent',createdAt:now,expiresAt:null,promotedAt:now,artworkId:'art:shared-review',originEventId:null});
    const entry={artworkId:'art:shared-review',status:'ready',catalogStatus:'available',catalogPin,manifest:fixtureManifest(speciesId)};
    const response={snapshot:value,assets:[entry]};
    check('Exact shared catalog identity remains accepted',()=>{assert.equal(yardReadResponseSchema.safeParse(response).success,true);assert.equal(yardCommandResponseSchema.safeParse({...response,message:'Saved.'}).success,true);});
    for(const field of ['catalogKey','releaseVersion','renderSha256'])check(`Mismatched ${field} rejected for read and command responses`,()=>{
      const rejected={...response,assets:[{...entry,catalogPin:{...catalogPin,[field]:field==='releaseVersion'?2:'c'.repeat(64)}}]};
      assert.equal(yardReadResponseSchema.safeParse(rejected).success,false);assert.equal(yardCommandResponseSchema.safeParse({...rejected,message:'Saved.'}).success,false);
    });
    check('Exact revoked shared identity still permits explicit unavailable fallback',()=>assert.equal(yardReadResponseSchema.safeParse({...response,assets:[{artworkId:entry.artworkId,status:'unavailable',catalogStatus:'revoked',catalogPin}]}).success,true));

    let state:{error:string}={error:''},loads=0;
    const nav=createPageNavigation({jobs:[]},async()=>{loads++;throw new Error('Synthetic read failure');},s=>state=s);
    const retry=()=>state.error?nav.retry():nav.refresh();
    await retry();
    check('Initial missing-page retry selection starts fresh request',()=>assert.equal(loads,1));
    await retry();
    check('Subsequent failed-request retry selection repeats request',()=>assert.equal(loads,2));
    nav.destroy();
    console.log(JSON.stringify({passed:results.length,controls:results,queryPlan:plan,scope:'Disposable SQLite and controlled functions only; UI retry dispatch checked against actual source, no rendered DOM assertion'},null,2));
  } finally {if(writer.isTransaction)writer.exec('ROLLBACK');writer.close();yard.close();rmSync(root,{recursive:true,force:true});}
}
main().catch(error=>{console.error(error);process.exitCode=1;});
