// Exact current canonical JSON routine for bounded source facts, no runtime schema claim.
import fs from 'node:fs';
import crypto from 'node:crypto';
import {canonicalJson,PermanentStageError} from '/workspace/runtime-resting-intake-v5-inspect/src/lib/pipeline/canonical-json.ts';
const [input,output]=process.argv.slice(2),b=fs.readFileSync(input),sha=x=>crypto.createHash('sha256').update(x).digest('hex');let r;
try{const c=canonicalJson(JSON.parse(b));r={status:'PASS actual canonicalJson source-facts budget',inputSHA256:sha(b),canonicalUTF8Bytes:Buffer.byteLength(c),canonicalSHA256:sha(c)}}catch(e){if(!(e instanceof PermanentStageError))throw e;r={status:'FAIL actual canonicalJson',inputSHA256:sha(b),message:e.message,actualClass:true}}
fs.writeFileSync(output,JSON.stringify({...r,scope:'Factual source JSON only; no pixel normalization/full common-family/admission check',runtimeCommit:'c4ae7529786e28cf55e2008b7f7b64215fc6542c',sourceAdmitted:false},null,2)+'\n');
