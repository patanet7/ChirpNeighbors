import assert from 'node:assert/strict';
import {DatabaseSync} from 'node:sqlite';
import {performance} from 'node:perf_hooks';
import {writeFileSync} from 'node:fs';
import {randomUUID} from 'node:crypto';
import {YardRepository} from '/workspace/archive-history/birdsong-yard-sprites/src/lib/server/storage/repository.ts';
import {JobRepository} from '/workspace/archive-history/birdsong-yard-sprites/src/lib/server/pipeline/repository.ts';
import {AssetLifecycleService} from '/workspace/archive-history/birdsong-yard-sprites/src/lib/server/assets/lifecycle.ts';
import {jobPage} from '/workspace/archive-history/birdsong-yard-sprites/src/lib/server/workbench/jobs.ts';
const path='/workspace/archive-history/audit-jobs-assets/data-32/synthetic.sqlite';
const yard=new YardRepository(path), db=yard.database,jobs=new JobRepository(db),life=new AssetLifecycleService(yard,jobs);
const target=db.prepare('SELECT id FROM pip_jobs WHERE owner_id=? ORDER BY rowid DESC LIMIT 1').get('alice')!.id as string;
db.exec('PRAGMA busy_timeout=75;');
const writer=new DatabaseSync(path);writer.exec('PRAGMA journal_mode=WAL;PRAGMA busy_timeout=75;BEGIN IMMEDIATE');
writer.prepare('UPDATE asset_archives SET archived=0,revision=2 WHERE owner_id=? AND target_id=?').run('alice',target);
const result:any={probeBusyTimeoutMs:75,writerUncommittedArchive:false,expectedReaderCommittedArchive:true};
for(const [name,run] of [
 ['jobsPage',()=>jobPage(jobs,'alice',{limit:10})],
 ['packageHistory',()=>life.packageHistory('alice',{limit:10})],
 ['overview',()=>life.overview('alice')],
] as const){const start=performance.now();const value=run();const state='entries' in value?value.entries.find(x=>x.state.target.id===target)?.state:null;result[name]={ok:true,ms:performance.now()-start,seenArchive:state?.archived??null,seenRevision:state?.revision??null};if(state){assert.equal(state.archived,true);assert.equal(state.revision,1);}}
let denied=false;const start=performance.now();try{life.command('alice',{action:'set-archive',requestId:randomUUID(),target:{kind:'private-package',id:target},expectedRevision:1,archived:false});}catch(error:any){denied=true;result.command={blocked:true,ms:performance.now()-start,message:error.message,errcode:error.errcode};assert.equal(error.errcode,5)}
assert(denied);writer.exec('ROLLBACK');writer.close();yard.close();
writeFileSync('/workspace/archive-history/audit-jobs-assets/lockfix-results.json',JSON.stringify(result,null,2));console.log(JSON.stringify(result));
