// Uses actual pinned canonical JSON implementation; no replacement caps or validator.
import fs from 'node:fs';import crypto from 'node:crypto';
import {canonicalJson,PermanentStageError} from '/workspace/runtime-resting-intake-v5-inspect/src/lib/pipeline/canonical-json.ts';
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
const cfg=JSON.parse(fs.readFileSync(process.argv[2]));const rows=[];
for(const f of cfg.inputs){const bytes=fs.readFileSync(f.path);try{const text=canonicalJson(JSON.parse(bytes));rows.push({label:f.label,path:f.path,inputSHA256:sha(bytes),status:'PASS actual canonicalJson',canonicalUTF8Bytes:Buffer.byteLength(text),canonicalSHA256:sha(text)});}catch(e){if(!(e instanceof PermanentStageError))throw e;rows.push({label:f.label,path:f.path,inputSHA256:sha(bytes),status:'FAIL actual canonicalJson',message:e.message,actualPermanentStageError:true});}}
const r={runtimeCommit:'c4ae7529786e28cf55e2008b7f7b64215fc6542c',scope:'Actual raw candidate input and source metadata budget; not generated production manifest or full admission',results:rows,sourceAdmitted:false,runtimeAdmission:false};fs.writeFileSync(cfg.output,JSON.stringify(r,null,2)+'\n');console.log(JSON.stringify(rows.map(({label,status,canonicalUTF8Bytes,message})=>({label,status,canonicalUTF8Bytes,message}))));
