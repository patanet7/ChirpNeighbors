import { YardRepository } from '../birdsong-yard-sprites/src/lib/server/storage/repository';
import { parseResponse, SERVICE_RESPONSE_MAX_BYTES } from '../birdsong-yard-sprites/src/lib/client/service';
import { yardReadResponseSchema, yardCommandResponseSchema } from '../birdsong-yard-sprites/src/lib/client/contracts';
import { yardDataSchema } from '../birdsong-yard-sprites/src/lib/domain/yard';
import { readFileSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';
const out=process.argv[2];
const measurements=JSON.parse(readFileSync(join(out,'measurements.json'),'utf8'));
const evidence:any={ transport:[], originValidation:[], limit:SERVICE_RESPONSE_MAX_BYTES, source:'Exact repository + client parseResponse; in-process Response only, no HTTP server/browser.' };
for(const count of [100,30000]) {
  const yard=new YardRepository(join(measurements.storage,`owner-${count}.sqlite`));
  const snapshot=yard.rename('audit-owner','audit-bird','Committed audit rename', '2026-10-12T12:00:00.000Z');
  const stored=yard.database.prepare('SELECT data FROM yard_owners WHERE owner_id=?').get('audit-owner')!.data as string;
  for(const command of [false,true]) {
    const payload=JSON.stringify({snapshot,assets:[],...(command?{message:'Saved to your yard.'}:{})});
    for(const declared of [false,true]) {
      const headers:Record<string,string>={'content-type':'application/json'};
      if(declared)headers['content-length']=String(Buffer.byteLength(payload));
      let failure=null,accepted=false;
      const start=performance.now();
      try { await parseResponse(new Response(payload,{status:200,headers}),command?yardCommandResponseSchema:yardReadResponseSchema); accepted=true; }
      catch(error) { failure={name:(error as Error).constructor.name,message:(error as Error).message}; }
      evidence.transport.push({events:count,command,declaredLength:declared,status:200,storedBytes:Buffer.byteLength(stored),responseBytes:Buffer.byteLength(payload),accepted,failure,elapsedMs:performance.now()-start,committedName:JSON.parse(stored).birds[0].name});
    }
  }
  yard.close();
}
const yard=new YardRepository(join(measurements.storage,'owner-10000.sqlite'));
const raw=JSON.parse(yard.database.prepare('SELECT data FROM yard_owners WHERE owner_id=?').get('audit-owner')!.data as string);
for(const count of [1,100,1000]) {
  for(const linked of [false,true]) {
    const data={...raw,birds:Array.from({length:count},(_,index)=>({...raw.birds[0],id:`origin-audit:${index}`,originEventId:linked?raw.events[raw.events.length-1-index].id:null}))};
    yardDataSchema.parse(data);
    const samples=[];
    for(let i=0;i<3;i++){const start=performance.now();yardDataSchema.parse(data);samples.push(performance.now()-start);}
    evidence.originValidation.push({events:data.events.length,residents:count,linkedLateOrigins:linked,samplesMs:samples,medianMs:[...samples].sort((a,b)=>a-b)[1]});
  }
}
yard.close();
writeFileSync(join(out,'probes.json'),JSON.stringify(evidence,null,2)+'\n');
console.log(JSON.stringify(evidence,null,2));
