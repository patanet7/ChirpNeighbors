import { performance } from 'node:perf_hooks';
import { writeFileSync } from 'node:fs';
import { YardRepository } from '/workspace/archive-history/birdsong-yard-sprites/src/lib/server/storage/repository';
import { JobRepository } from '/workspace/archive-history/birdsong-yard-sprites/src/lib/server/pipeline/repository';
import { PipelineRunner } from '/workspace/archive-history/birdsong-yard-sprites/src/lib/server/pipeline/runner';
import { developmentPipelines } from '/workspace/archive-history/birdsong-yard-sprites/src/lib/server/pipeline/definitions';
import { assetPackagingV2Definition } from '/workspace/archive-history/birdsong-yard-sprites/src/lib/server/asset-pipeline/definitions-v2';
import { technicalFixtureInputV2 } from '/workspace/archive-history/birdsong-yard-sprites/src/lib/server/asset-pipeline/fixture-v2';
import { reviewedManifest, pinReviewedAnimation, yardAssets } from '/workspace/archive-history/birdsong-yard-sprites/src/lib/server/assets/resolve';
import { AssetLifecycleService } from '/workspace/archive-history/birdsong-yard-sprites/src/lib/server/assets/lifecycle';
import { AnimationRegistry } from '/workspace/archive-history/birdsong-yard-sprites/src/lib/assets/registry';
import { fixtureEvents } from '/workspace/archive-history/birdsong-yard-sprites/src/lib/fixtures';
const owner='audit-owner',speciesId='cn-species-erithacus-rubecula';
const evidence:any={timestamp:new Date().toISOString(),node:process.version,method:'Actual repositories and pipeline, disposable SQLite :memory:, existing fixture pixels only, 1 warm-up then 3 samples; synchronous SQL statement executions counted via get/all/run wrapping; synthetic presentation snapshots assembled from actual pinned artwork rows',runs:[]};
async function setup(){
 const yard=new YardRepository(':memory:');
 const jobs=new JobRepository(yard.database);
 const lifecycle=new AssetLifecycleService(yard,jobs);
 const runner=new PipelineRunner(jobs,[...developmentPipelines,assetPackagingV2Definition(jobs),assetPackagingV2Definition(jobs,3)]);
 yard.importEvents(owner,fixtureEvents(yard.snapshot(owner),new Date().toISOString()));
 const referenceJob=jobs.queue(owner,{definitionId:'fixture-artwork',definitionVersion:2,input:{speciesId,label:'Existing technical fixture for audit'},idempotencyKey:crypto.randomUUID()});
 await runner.advance(owner,referenceJob.id);await runner.advance(owner,referenceJob.id);
 const a=jobs.artifacts(owner,referenceJob.id)[0]!;jobs.review(owner,a.id,'approved');
 const reference=reviewedManifest(jobs,owner,referenceJob.id,a.id);
 const input=technicalFixtureInputV2(reference.manifest as any,reference.pin);
 const bird=yard.snapshot(owner).birds.find(b=>b.speciesId===speciesId)!;
 let queryCount=0,artifactCalls=0, getCalls=0;
 const originalPrepare=yard.database.prepare.bind(yard.database);
 (yard.database as any).prepare=(...args:any[])=>{const st=(originalPrepare as any)(...args);for(const m of ['get','all','run']){const old=st[m].bind(st);st[m]=(...xs:any[])=>{queryCount++;return old(...xs)}}return st};
 const originalArtifacts=jobs.artifacts.bind(jobs),originalGet=jobs.get.bind(jobs);
 jobs.artifacts=(...a)=>{artifactCalls++;return originalArtifacts(...a)};
 jobs.get=(...a)=>{getCalls++;return originalGet(...a)};
 function measure(label:string,action:()=>unknown){action();const samples=[];let returned:any;for(let i=0;i<3;i++){queryCount=artifactCalls=getCalls=0;const start=performance.now();returned=action();samples.push({ms:performance.now()-start,queries:queryCount,artifactCalls,getCalls})}const result={label,samples,returnBytes:Buffer.byteLength(JSON.stringify(returned)),statuses:Array.isArray(returned)?returned.map(v=>v.status):undefined};evidence.runs.push(result);console.log(JSON.stringify(result));return returned}
 return{yard,jobs,lifecycle,runner,input,bird,reference,measure};
}
async function packageNext(c:Awaited<ReturnType<typeof setup>>,basedOn:any){
 const input:any=structuredClone(c.input);input.schemaVersion=3;input.presentation={schemaVersion:1,sourcePixelsPerWorldUnit:2};
 input.conditioning.references[0].pin=basedOn.pin;input.source.references[0].contentDigest=basedOn.pin.contentDigest;
 const j=c.jobs.queue(owner,{definitionId:'asset-packaging',definitionVersion:3,input,idempotencyKey:crypto.randomUUID()});
 await c.runner.advance(owner,j.id);await c.runner.advance(owner,j.id);const s=c.jobs.artifacts(owner,j.id).find(a=>a.kind==='rgba-source-manifest')!;
 if(!s)throw new Error(JSON.stringify(c.jobs.get(owner,j.id)));c.jobs.review(owner,s.id,'approved');await c.runner.advance(owner,j.id);
 const a=c.jobs.artifacts(owner,j.id).find(a=>a.kind==='animation-manifest')!;if(!a)throw new Error(JSON.stringify(c.jobs.get(owner,j.id)));c.jobs.review(owner,a.id,'approved');
 const resolved=reviewedManifest(c.jobs,owner,j.id,a.id);pinReviewedAnimation(c.yard,c.jobs,owner,c.bird.id,j.id,a.id);
 const snapshot=c.yard.snapshot(owner),art=snapshot.artworks.find(a=>a.id===snapshot.birds.find(b=>b.id===c.bird.id)!.artworkId)!;
 return{...resolved,art};
}
async function main(){
 const flat=await setup();const arts:any[]=[];
 for(let n=1;n<=24;n++){
  const p=await packageNext(flat,flat.reference);arts.push(p.art);
  if(![1,8,24].includes(n))continue;
  const snap=flat.yard.snapshot(owner);snap.artworks=arts;snap.birds=arts.map((art,i)=>({...flat.bird,id:`audit-bird-${i}`,artworkId:art.id}));
  const entries=flat.measure(`flat ${n} selected V4 packages sharing one V2 ancestor: yardAssets`,()=>yardAssets(flat.jobs,owner,snap));
  flat.measure(`flat ${n+1} retained jobs: lifecycle.overview`,()=>flat.lifecycle.overview(owner));
  const reg=new AnimationRegistry();reg.replace(entries);const birds=snap.birds;
  flat.measure(`flat ${n} client registry warm resolve`,()=>birds.map(b=>reg.resolve(b)));
  const before=reg.resolve(birds[0]!).key;reg.replace(structuredClone(entries));const after=reg.resolve(birds[0]!).key;
  evidence.runs.push({label:`flat ${n} equal-byte assets replacement changes key`,changed:before!==after});
  flat.measure(`flat ${n} client registry equal-byte replacement + resolve`,()=>{reg.replace(structuredClone(entries));return birds.map(b=>reg.resolve(b))});
 }
 flat.yard.close();
 const chain=await setup();let previous:any=chain.reference;
 for(let n=1;n<=12;n++){
  previous=await packageNext(chain,previous);
  if(![1,4,8,12].includes(n))continue;
  const snap=chain.yard.snapshot(owner);
  chain.measure(`chain ${n} V4 + V2 ancestor, one selected: yardAssets`,()=>yardAssets(chain.jobs,owner,snap));
  chain.measure(`chain ${n+1} retained jobs: lifecycle.overview`,()=>chain.lifecycle.overview(owner));
 }
 chain.yard.close();writeFileSync('/tmp/chirp-audit-engine-results.json',JSON.stringify(evidence,null,2)+'\n');
}
main().catch(e=>{console.error(e);process.exitCode=1});
