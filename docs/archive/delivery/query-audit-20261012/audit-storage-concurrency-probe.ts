import { YardRepository } from './birdsong-yard-sprites/src/lib/server/storage/repository.ts';
import { mkdtempSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { Worker } from 'node:worker_threads';
import { randomUUID } from 'node:crypto';
import { once } from 'node:events';
const root=mkdtempSync(join(tmpdir(),'chirp-storage-audit-'));
const path=join(root,'synthetic.sqlite');
const a=new YardRepository(path),b=new YardRepository(path);
const now='2026-10-12T12:00:00.000Z';
const report:any={syntheticOnly:true,realOwnerData:false};
try {
 a.updatePreferences('synthetic:alice',{palette:'twilight'},now);
 const worker=new Worker(`const {parentPort,workerData}=require('node:worker_threads');const {DatabaseSync}=require('node:sqlite');const db=new DatabaseSync(workerData);db.exec('PRAGMA busy_timeout=5000; BEGIN IMMEDIATE');db.prepare("UPDATE yard_owners SET data=json_set(data,'$.preferences.palette','moonlit') WHERE owner_id=?").run('synthetic:alice');parentPort.postMessage('locked');setTimeout(()=>{db.exec('COMMIT');db.close();parentPort.close()},300);`,{eval:true,workerData:path});
 await once(worker,'message');
 const readStart=performance.now();
 const whileLocked=b.snapshot('synthetic:alice',now);
 const readMs=performance.now()-readStart;
 const writeStart=performance.now();
 const after=a.updatePreferences('synthetic:alice',{reducedMotion:true},now);
 const writeMs=performance.now()-writeStart;
 await once(worker,'exit');
 report.wal={readMs,writeWaitMs:writeMs,readerSawCommittedPalette:whileLocked.preferences.palette,finalPalette:after.preferences.palette,finalReducedMotion:after.preferences.reducedMotion,preservedOtherWriter:after.preferences.palette==='moonlit'&&after.preferences.reducedMotion};
 const before=a.snapshot('synthetic:alice',now);
 const expected={scene:before.preferences.scene,scenePin:before.preferences.scenePin,objects:before.environment.objects};
 const request={action:'object-inventory',requestId:randomUUID(),expected,payload:{operation:'return',objectId:before.environment.objects[0]!.id}};
 const committed=b.objectInventory('synthetic:alice',request,now);
 let staleCode=null;
 try{a.objectInventory('synthetic:alice',{...request,requestId:randomUUID()},now)}catch(error){staleCode=(error as any).code}
 const retried=a.objectInventory('synthetic:alice',request,now);
 let changedRetryCode=null;
 try{a.objectInventory('synthetic:alice',{...request,payload:{operation:'return',objectId:before.environment.objects[1]!.id}},now)}catch(error){changedRetryCode=(error as any).code}
 report.cas={staleCode,changedRetryCode,exactRetryPreserved:JSON.stringify(retried)===JSON.stringify(committed),receiptCount:retried.environment.objectReceipts.length,otherOwnerReceiptCount:b.snapshot('synthetic:bob',now).environment.objectReceipts.length};
 report.journalMode=a.database.prepare('PRAGMA journal_mode').get();
 report.busyTimeout=a.database.prepare('PRAGMA busy_timeout').get();
}finally{a.close();b.close();rmSync(root,{recursive:true,force:true})}
writeFileSync('/workspace/archive-history/audit-storage-concurrency-results.json',JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report,null,2));
