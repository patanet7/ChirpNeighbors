import { YardRepository } from './birdsong-yard-sprites/src/lib/server/storage/repository.ts';
import { emptyYard, snapshotOf } from './birdsong-yard-sprites/src/lib/domain/yard.ts';
import { parseResponse, SERVICE_RESPONSE_MAX_BYTES } from './birdsong-yard-sprites/src/lib/client/service.ts';
import { yardReadResponseSchema } from './birdsong-yard-sprites/src/lib/client/contracts.ts';
import { ArrivalRepository } from './birdsong-yard-sprites/src/lib/server/arrivals/repository.ts';
import { writeFileSync } from 'node:fs';
import { performance } from 'node:perf_hooks';

const now = '2026-10-12T12:00:00.000Z';
const species = {id:'cn-species-erithacus-rubecula', commonName:'European Robin', scientificName:'Erithacus rubecula'};
function event(index:number) {
  const id = `synthetic-${String(index).padStart(6, '0')}`;
  return {schemaVersion:2 as const,id,species, observedAt:null, ingestedAt:now, source:{kind:'fixture' as const,label:'Synthetic audit fixture',sourceEventId:id}};
}
const yard = new YardRepository(':memory:');
new ArrivalRepository(yard.database, (owner, clock) => yard.snapshot(owner, clock));
const report:any = { syntheticOnly:true, realOwnerData:false, clientLimitBytes:SERVICE_RESPONSE_MAX_BYTES, measurements:[] };
for(const count of [1000,10000,45000]) {
  const data=emptyYard();data.species=[species];data.events=Array.from({length:count},(_,i)=>event(i));
  const serialized=JSON.stringify(data);
  const start=performance.now();
  const snapshot=yard.restoreBackup('synthetic:alice',{format:'chirpneighbors-yard',version:2,exportedAt:now,data},now);
  const restoreMs=performance.now()-start;
  const snapStart=performance.now();yard.snapshot('synthetic:alice',now);const snapshotMs=performance.now()-snapStart;
  const response=JSON.stringify({snapshot,assets:[]});
  let clientAccepted=true,clientError:string|null=null;
  const clientStart=performance.now();
  try {await parseResponse(new Response(response,{headers:{'Content-Type':'application/json'}}),yardReadResponseSchema)}
  catch(error) {clientAccepted=false;clientError=error instanceof Error ? error.message : String(error)}
  report.measurements.push({events:count,storedBytes:Buffer.byteLength(serialized),responseBytes:Buffer.byteLength(response),restoreMs,snapshotMs,clientMs:performance.now()-clientStart,clientAccepted,clientError});
}
const mutationStart=performance.now();
const mutated=yard.updatePreferences('synthetic:alice',{reducedMotion:true},now);
const mutationBody=JSON.stringify({snapshot:mutated,assets:[],message:'Saved to your yard.'});
report.acceptedMutation={reducedMotion:yard.snapshot('synthetic:alice',now).preferences.reducedMotion,responseBytes:Buffer.byteLength(mutationBody),exceedsClientLimit:Buffer.byteLength(mutationBody)>SERVICE_RESPONSE_MAX_BYTES,durationMs:performance.now()-mutationStart};
report.otherOwnerEvents=yard.snapshot('synthetic:bob',now).events.length;
report.queryPlans={
 ownerRead:yard.database.prepare('EXPLAIN QUERY PLAN SELECT schema_version,data FROM yard_owners WHERE owner_id=?').all('synthetic:alice'),
 arrivalRead:yard.database.prepare("EXPLAIN QUERY PLAN SELECT arrival_id FROM yard_arrivals WHERE owner_id=? AND state='pending' AND json_extract(payload_json,'$.eligibleUntil')>? ORDER BY json_extract(payload_json,'$.admittedAt'),arrival_id LIMIT ?").all('synthetic:alice',now,20),
 arrivalDedupe:yard.database.prepare('EXPLAIN QUERY PLAN SELECT 1 FROM yard_arrivals WHERE owner_id=? AND event_id=?').all('synthetic:alice','synthetic-000001'),
};
yard.close();
writeFileSync('/workspace/archive-history/audit-storage-probe-results.json',JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify(report,null,2));
