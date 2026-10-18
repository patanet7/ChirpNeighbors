// Executes the actual nominated canonicalJson only; this is not intake or schema validation.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { canonicalJson, PermanentStageError } from '/workspace/runtime-common-v6-intake-inspect/src/lib/pipeline/canonical-json.ts';
const root=path.dirname(new URL(import.meta.url).pathname),sha=x=>crypto.createHash('sha256').update(x).digest('hex');
const results=[];
for(const f of fs.readdirSync(path.join(root,'proposals')).filter(x=>x.endsWith('.json')).sort()){
 const p=path.join(root,'proposals',f), bytes=fs.readFileSync(p);let result;
 try{const canonical=canonicalJson(JSON.parse(bytes));result={status:'PASS actual canonicalJson budget only',canonicalUTF8Bytes:Buffer.byteLength(canonical),canonicalSHA256:sha(canonical)};}
 catch(e){if(!(e instanceof PermanentStageError))throw e;result={status:'FAIL actual canonicalJson budget',actualClass:true,message:e.message};}
 results.push({input:'proposals/'+f,inputSHA256:sha(bytes),...result,metadataComplete:false,sourceAdmitted:false});
}
const module='/workspace/runtime-common-v6-intake-inspect/src/lib/pipeline/canonical-json.ts';fs.writeFileSync(path.join(root,'candidate-json-budget.json'),JSON.stringify({scope:'Actual candidate input JSON budget; not generated runtime manifest or full metadata validation',canonicalModuleSHA256:sha(fs.readFileSync(module)),runtimeCommit:'8cd59c21abb990e5be95424587b3952d7fa3f1c4',results,sourceAdmitted:false},null,2)+'\n');
console.log(JSON.stringify(results.map(x=>({input:x.input,status:x.status,bytes:x.canonicalUTF8Bytes}))));
