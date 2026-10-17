import { DatabaseSync } from 'node:sqlite';
import { mkdirSync, writeFileSync, statSync, readFileSync } from 'node:fs';
import { join } from 'node:path';
import { performance } from 'node:perf_hooks';
import { randomUUID } from 'node:crypto';
import { YardRepository } from '/workspace/archive-history/birdsong-yard-sprites/src/lib/server/storage/repository.ts';
import { JobRepository } from '/workspace/archive-history/birdsong-yard-sprites/src/lib/server/pipeline/repository.ts';
import { PipelineRunner } from '/workspace/archive-history/birdsong-yard-sprites/src/lib/server/pipeline/runner.ts';
import { fixtureAnimationDefinition } from '/workspace/archive-history/birdsong-yard-sprites/src/lib/server/pipeline/definitions.ts';
import { jobPage } from '/workspace/archive-history/birdsong-yard-sprites/src/lib/server/workbench/jobs.ts';
import { AssetLifecycleService } from '/workspace/archive-history/birdsong-yard-sprites/src/lib/server/assets/lifecycle.ts';
import { verifyAssetLifecycleStore } from '/workspace/archive-history/birdsong-yard-sprites/src/lib/server/assets/lifecycle-storage.ts';

const root = '/workspace/archive-history/audit-jobs-assets';
const results: any[] = [];
function trace(db: DatabaseSync) {
  const original = db.prepare.bind(db), exec = db.exec.bind(db);
  let entries: { sql: string; ms: number; rows: number }[] = [];
  db.prepare = ((sql: string) => {
    const statement = original(sql);
    return new Proxy(statement, { get(target, key) {
      const value = Reflect.get(target, key);
      if (['get','all','run'].includes(String(key))) return (...args: any[]) => {
        const start = performance.now();
        try {
          const result = value.apply(target, args);
          entries.push({sql, ms: performance.now()-start, rows: Array.isArray(result)?result.length:result?1:0});
          return result;
        } catch (error) { entries.push({sql,ms:performance.now()-start,rows:0}); throw error; }
      };
      return typeof value === 'function' ? value.bind(target) : value;
    }});
  }) as typeof db.prepare;
  db.exec = ((sql: string) => { const start=performance.now();try {return exec(sql)} finally {entries.push({sql,ms:performance.now()-start,rows:0})} }) as typeof db.exec;
  return { clear() {entries=[];}, collect() {return entries;} };
}
function measure(name: string, run: ()=>any, meter: ReturnType<typeof trace>, repetitions=9) {
  run(); run(); // Explicit warmup; this is not a cold filesystem benchmark.
  const times: number[] = [];
  let sample: any;
  for (let i=0;i<repetitions;i++) {
    meter.clear(); const start=performance.now(); const value=run(); times.push(performance.now()-start);
    if(i===repetitions-1) {
      const sql = meter.collect();
      const grouped = new Map<string, {calls:number,ms:number,rows:number}>();
      for (const entry of sql) { const v=grouped.get(entry.sql)??{calls:0,ms:0,rows:0};v.calls++;v.ms+=entry.ms;v.rows+=entry.rows;grouped.set(entry.sql,v); }
      sample={queries:sql.length,sqlMs:sql.reduce((n,x)=>n+x.ms,0),rowsReturned:sql.reduce((n,x)=>n+x.rows,0),returnedItems:value?.jobs?.length??value?.entries?.length??null,sql:[...grouped].map(([sql,v])=>({sql,...v}))};
    }
  }
  times.sort((a,b)=>a-b);
  return {name,repetitions,medianMs:times[Math.floor(times.length/2)],p95Ms:times[Math.ceil(times.length*.95)-1],minMs:times[0],maxMs:times.at(-1),...sample};
}
function plans(db: DatabaseSync, job: string, watermark: number) {
  const queries = [
    ['artifacts', 'SELECT a.*,r.decision,r.reviewed_at,r.note FROM pip_artifacts a LEFT JOIN pip_reviews r ON r.artifact_id=a.id AND r.owner_id=a.owner_id WHERE a.owner_id=? AND a.job_id=? ORDER BY a.created_at,a.version',['alice',job]],
    ['artifact_budget','SELECT COUNT(*) AS n,COALESCE(SUM(length(CAST(payload_json AS BLOB))+length(CAST(provenance_json AS BLOB))),0) AS bytes FROM pip_artifacts WHERE owner_id=? AND job_id=?',['alice',job]],
    ['runs','SELECT * FROM pip_runs WHERE job_id=? ORDER BY started_at,attempt',[job]],
    ['stage_claim',"SELECT * FROM pip_stages WHERE job_id=? AND status!='succeeded' ORDER BY ordinal LIMIT 1",[job]],
    ['page_first','SELECT id,rowid AS ordinal FROM pip_jobs WHERE owner_id=? AND rowid<=? AND (? IS NULL OR rowid<?) ORDER BY rowid DESC LIMIT ?',['alice',watermark,null,null,11]],
    ['page_deep','SELECT id,rowid AS ordinal FROM pip_jobs WHERE owner_id=? AND rowid<=? AND (? IS NULL OR rowid<?) ORDER BY rowid DESC LIMIT ?',['alice',watermark,Math.floor(watermark/5),Math.floor(watermark/5),11]],
    ['page_deep_bounded_candidate','SELECT id,rowid AS ordinal FROM pip_jobs WHERE owner_id=? AND rowid<? ORDER BY rowid DESC LIMIT ?',['alice',Math.floor(watermark/5),11]],
    ['references_page','SELECT id,rowid AS ordinal FROM pip_jobs WHERE owner_id=? AND definition_id=\'reference-generation\' AND rowid<=? AND (? IS NULL OR rowid<?) ORDER BY rowid DESC LIMIT ?',['alice',watermark,null,null,11]],
    ['cancel_children','SELECT j.id FROM pip_jobs j WHERE j.parent_job_id=? AND j.owner_id=?',[job,'alice']],
  ] as const;
  return queries.map(([name,sql,args])=>({name,sql,plan:db.prepare('EXPLAIN QUERY PLAN '+sql).all(...args)}));
}
for(const count of [32,256,2048,8192]) {
  const dir=join(root,`data-${count}`);mkdirSync(dir,{recursive:true,mode:0o700});
  const path=join(dir,'synthetic.sqlite');
  const yard=new YardRepository(path), db=yard.database;
  const jobs=new JobRepository(db), life=new AssetLifecycleService(yard,jobs);
  const job=jobs.queue('alice',{definitionId:'fixture-artwork',definitionVersion:2,input:{speciesId:'cn-species-erithacus-rubecula',label:'Synthetic performance fixture'},idempotencyKey:'seed-template'});
  const runner=new PipelineRunner(jobs,[fixtureAnimationDefinition]);
  await runner.advance('alice',job.id); await runner.advance('alice',job.id);
  jobs.review('alice',jobs.artifacts('alice',job.id)[0]!.id,'approved');
  const tables=['pip_jobs','pip_stages','pip_runs','pip_artifacts','pip_reviews'];
  const templates=Object.fromEntries(tables.map(table=>[table,db.prepare(`SELECT * FROM ${table}`).all()]));
  db.exec('BEGIN');
  for(let i=1;i<count;i++) {
    const id=randomUUID(), artifactId=randomUUID();
    for(const table of tables) for(const original of templates[table]!) {
      const row={...original};
      if(table==='pip_jobs') Object.assign(row,{id,root_job_id:id,idempotency_key:`seed-${i}`,created_at:Number(row.created_at)+i,updated_at:Number(row.updated_at)+i});
      if('job_id' in row) row.job_id=id;
      if(table==='pip_runs') row.id=randomUUID();
      if(table==='pip_artifacts') Object.assign(row,{id:artifactId,version:i+1,created_at:Number(row.created_at)+i});
      if(table==='pip_reviews') Object.assign(row,{artifact_id:artifactId,reviewed_at:Number(row.reviewed_at)+i});
      db.prepare(`INSERT INTO ${table}(${Object.keys(row).join(',')}) VALUES(${Object.keys(row).map(()=>'?').join(',')})`).run(...Object.values(row));
    }
  }
  db.exec('COMMIT');
  yard.snapshot('alice');
  const meter=trace(db);
  const baselinePlans=plans(db,job.id,count);
  const plain=()=>jobPage(jobs,'alice',{limit:10});
  const packageRead=()=>life.packageHistory('alice',{limit:10});
  const overview=()=>life.overview('alice');
  const baseline=[measure('jobs-page-10',plain,meter),measure('package-history-10',packageRead,meter),measure('lifecycle-overview',overview,meter,3)];
  const inputBytes=db.prepare('SELECT SUM(length(CAST(input_json AS BLOB))) n FROM pip_jobs').get()!.n;
  const artifactBytes=db.prepare('SELECT SUM(length(CAST(payload_json AS BLOB))+length(CAST(provenance_json AS BLOB))) n FROM pip_artifacts').get()!.n;
  db.exec('CREATE INDEX audit_artifacts_owner_job ON pip_artifacts(owner_id,job_id,created_at,version)');
  const indexedPlans=plans(db,job.id,count);
  const indexed=[measure('jobs-page-10',plain,meter),measure('package-history-10',packageRead,meter),measure('lifecycle-overview',overview,meter,3)];
  const query=db.prepare('SELECT id,rowid FROM pip_jobs WHERE owner_id=? AND rowid<=? AND (? IS NULL OR rowid<?) ORDER BY rowid DESC LIMIT ?');
  const bounded=db.prepare('SELECT id,rowid FROM pip_jobs WHERE owner_id=? AND rowid<? ORDER BY rowid DESC LIMIT ?');
  const deepBefore=Math.floor(count/5);
  const deepBaseline=measure('deep-page-raw',()=>query.all('alice',count,deepBefore,deepBefore,11),meter,101);
  const deepCandidate=measure('deep-page-bounded-candidate',()=>bounded.all('alice',deepBefore,11),meter,101);
  const lockDb=new DatabaseSync(path);lockDb.exec('PRAGMA journal_mode=WAL; PRAGMA busy_timeout=75;');db.exec('PRAGMA busy_timeout=75;');
  lockDb.exec('BEGIN IMMEDIATE');
  const lockResult:any={configuredRuntimeBusyTimeoutMs:5000,probeBusyTimeoutMs:75};
  for(const [name,fn] of [['jobsPage',plain],['packageHistory',packageRead],['overview',overview]] as const) {const start=performance.now();try {fn();lockResult[name]={ok:true,ms:performance.now()-start};}catch(error:any){lockResult[name]={ok:false,ms:performance.now()-start,message:error.message,code:error.code,errcode:error.errcode};}}
  lockDb.exec('ROLLBACK');lockDb.close();
  const recovery=measure('asset-lifecycle-recovery-preflight',()=>verifyAssetLifecycleStore(db),meter,5);
  db.exec('PRAGMA wal_checkpoint(TRUNCATE)');
  results.push({count,rows:Object.fromEntries(tables.map(t=>[t,db.prepare(`SELECT COUNT(*) n FROM ${t}`).get()!.n])),inputBytes,artifactBytes,databaseBytes:statSync(path).size,baselinePlans,indexedPlans,baseline,indexed,deepBaseline,deepCandidate,lockResult,recovery});
  writeFileSync(join(root,'results.json'),JSON.stringify(results,null,2));
  console.log(JSON.stringify({count,baseline:baseline.map(x=>({name:x.name,ms:x.medianMs,queries:x.queries})),indexed:indexed.map(x=>({name:x.name,ms:x.medianMs,queries:x.queries})),lockResult}));
  yard.close();
}
