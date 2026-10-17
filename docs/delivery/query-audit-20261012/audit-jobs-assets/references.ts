import {DatabaseSync} from 'node:sqlite';
import {mkdirSync,writeFileSync} from 'node:fs';
import {join} from 'node:path';
import {randomUUID} from 'node:crypto';
import {performance} from 'node:perf_hooks';
import sharp from 'sharp';
import {YardRepository} from '/workspace/archive-history/birdsong-yard-sprites/src/lib/server/storage/repository.ts';
import {ReferenceAdmissionService} from '/workspace/archive-history/birdsong-yard-sprites/src/lib/server/reference-admission/service.ts';
import {exportReferenceAuthority} from '/workspace/archive-history/birdsong-yard-sprites/src/lib/server/reference-admission/recovery.ts';
import {verifyAssetLifecycleStore} from '/workspace/archive-history/birdsong-yard-sprites/src/lib/server/assets/lifecycle-storage.ts';
const root='/workspace/archive-history/audit-jobs-assets';
function trace(db:DatabaseSync){
 const original=db.prepare.bind(db);let count=0,rows=0;const queries=new Map<string,number>();
 db.prepare=((sql:string)=>{const s=original(sql);return new Proxy(s,{get(t,k){const value=Reflect.get(t,k);if(['get','all','run'].includes(String(k)))return (...args:any[])=>{count++;queries.set(sql,(queries.get(sql)??0)+1);const v=value.apply(t,args);rows+=Array.isArray(v)?v.length:v?1:0;return v};return typeof value==='function'?value.bind(t):value}})}) as typeof db.prepare;
 return {clear(){count=0;rows=0;queries.clear()},get(){return {count,rows,queries:[...queries].map(([sql,n])=>({sql,n}))}}};
}
function measure(name:string,run:()=>any,meter:ReturnType<typeof trace>){run();const times=[];let output:any;for(let i=0;i<9;i++){meter.clear();const start=performance.now();const value=run();times.push(performance.now()-start);output={...meter.get(),entries:value?.entries?.length??value?.length??null};}times.sort((a,b)=>a-b);return {name,medianMs:times[4],p95Ms:times[8],...output};}
const result:any[]=[];
const bytes=await sharp(Buffer.from([20,40,60,255]),{raw:{width:1,height:1,channels:4}}).png().toBuffer();
for(const n of [1,16,64]){
 const dir=join(root,`references-${n}`);mkdirSync(dir,{recursive:true,mode:0o700});
 const yard=new YardRepository(join(dir,'synthetic.sqlite')),db=yard.database;
 const refs=new ReferenceAdmissionService(db,join(dir,'private-reference-files'));
 let first:any;
 for(let i=0;i<n;i++){const owner=i<16?'alice':`owner-${Math.floor(i/16)}`;const r=await refs.upload(owner,randomUUID(),bytes,'image/png');first??=r;}
 const meter=trace(db);
 const list=measure('reference-list-alice',()=>refs.list('alice'),meter);
 const exportAll=measure('reference-authority-export-all',()=>exportReferenceAuthority(db,refs.root),meter);
 const plans=[
  ['list','SELECT id FROM reference_files WHERE owner_id=? ORDER BY rowid LIMIT 17',['alice']],
  ['get','SELECT record_json FROM reference_files WHERE owner_id=? AND id=?',['alice',first.identity.id]],
  ['reviews','SELECT kind,review_json FROM reference_reviews WHERE owner_id=? AND reference_id=?',['alice',first.identity.id]],
  ['revocations','SELECT revocation_json FROM reference_revocations WHERE owner_id=? AND reference_id=?',['alice',first.identity.id]],
  ['export-files','SELECT * FROM reference_files ORDER BY id LIMIT 65',[]],
  ['export-reviews','SELECT * FROM reference_reviews LIMIT 193',[]],
 ].map(([name,sql,args]:any)=>({name,sql,plan:db.prepare('EXPLAIN QUERY PLAN '+sql).all(...args)}));
 result.push({globalReferences:n,ownerReferences:Math.min(16,n),list,exportAll,plans});
 console.log(JSON.stringify(result.at(-1)));yard.close();
}
writeFileSync(join(root,'references-results.json'),JSON.stringify(result,null,2));
const recovery:any[]=[];
for(const count of [32,256,2048,8192]){
 const db=new DatabaseSync(join(root,`data-${count}`,'synthetic.sqlite'));
 db.exec('PRAGMA journal_mode=WAL;PRAGMA busy_timeout=5000;BEGIN');
 db.prepare("INSERT INTO asset_archives(owner_id,kind,target_id,revision,archived,changed_at) SELECT owner_id,'private-package',id,1,1,'2026-10-12T00:00:00.000Z' FROM pip_jobs").run();
 db.exec('COMMIT');
 const meter=trace(db);const m=measure('asset-lifecycle-preflight-archives',()=>verifyAssetLifecycleStore(db),meter);
 recovery.push({archives:count,...m});db.close();
}
writeFileSync(join(root,'recovery-results.json'),JSON.stringify(recovery,null,2));
