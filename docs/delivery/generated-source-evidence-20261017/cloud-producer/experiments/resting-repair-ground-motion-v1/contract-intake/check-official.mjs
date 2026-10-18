// Uses exact current runtime exports only. No replacement schema, codec, rights or private pins.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {projectCommonProposalSchema} from '/workspace/runtime-resting-intake-v5-inspect/src/lib/assets/project-common-proposal.ts';
import {commonIntakeReportV2} from '/workspace/runtime-resting-intake-v5-inspect/src/lib/assets/common-intake-report-v2.ts';
import {assetPackagingInputV5Schema,rgbaSourceArtifactV4Schema} from '/workspace/runtime-resting-intake-v5-inspect/src/lib/assets/intake-v3.ts';
import {speciesManifestV6Schema} from '/workspace/runtime-resting-intake-v5-inspect/src/lib/assets/manifest-v6.ts';
import {assetSourceSchema} from '/workspace/runtime-resting-intake-v5-inspect/src/lib/assets/intake.ts';
import {assetSourceIssues} from '/workspace/runtime-resting-intake-v5-inspect/src/lib/assets/source-review.ts';
import {canonicalJson,PermanentStageError} from '/workspace/runtime-resting-intake-v5-inspect/src/lib/pipeline/canonical-json.ts';
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
if(process.argv.includes('--readiness')){
 console.log(JSON.stringify({status:'PASS actual official module imports; no candidate supplied or validated',exports:['projectCommonProposalSchema','commonIntakeReportV2','assetSourceSchema','assetSourceIssues','canonicalJson','PermanentStageError'],runtimeCommit:'c4ae7529786e28cf55e2008b7f7b64215fc6542c',actualSchemaVersions:{input:assetPackagingInputV5Schema.innerType().shape.schemaVersion.value,sourceArtifact:rgbaSourceArtifactV4Schema.innerType().shape.schemaVersion.value,renderManifest:speciesManifestV6Schema.innerType().shape.schemaVersion.value,producerProposal:projectCommonProposalSchema.shape.schemaVersion.value,proposalNestedInput:projectCommonProposalSchema.shape.input.shape.schemaVersion.value},sourceAdmitted:false}));
}else{
 const dir=path.resolve(process.argv[2]),r={scope:'Actual official proposal shape/source declaration/report2 and canonical JSON only; no admission or private binding recovery',sourceAdmitted:false,rightsGranted:false};
 const budget=f=>{const p=path.join(dir,f),b=fs.readFileSync(p);try{const c=canonicalJson(JSON.parse(b));return{file:f,inputSHA256:sha(b),status:'PASS actual canonicalJson',canonicalUTF8Bytes:Buffer.byteLength(c),canonicalSHA256:sha(c)}}catch(e){if(!(e instanceof PermanentStageError))throw e;return{file:f,inputSHA256:sha(b),status:'FAIL actual canonicalJson',message:e.message,actualPermanentStageError:true}}};
 r.rawCandidateBudget=budget('raw-candidate-input.json');
 if(fs.existsSync(path.join(dir,'producer-proposal.json'))){
  const bytes=fs.readFileSync(path.join(dir,'producer-proposal.json')),p=JSON.parse(bytes),checked=projectCommonProposalSchema.safeParse(p);r.proposal={inputSHA256:sha(bytes),schema:'project-generated-common-proposal-v1',shapePass:checked.success,issues:checked.success?[]:checked.error.issues.map(i=>({path:i.path.join('.')||'$',code:i.code,message:i.message})),fullCommonGraphRefinementsValidated:false};r.proposalBudget=budget('producer-proposal.json');
  const s=assetSourceSchema.safeParse(p.input.source);r.sourceDeclaration={shapeParseable:s.success,state:s.success?'actual assetSourceIssues executed':'unparseable importer-owned declarations remain null',issues:s.success?assetSourceIssues(s.data):s.error.issues.map(i=>({path:i.path.join('.'),code:i.code,message:i.message})),rightsGranted:false};
  r.input4Diagnostic=commonIntakeReportV2(p.input);r.input5Diagnostic=commonIntakeReportV2(JSON.parse(fs.readFileSync(path.join(dir,'incomplete-input5.json'))));
  r.refinementQualification='Producer proposal shape intentionally allows null private declarations and references. It does not run the full recovered common graph/source-reference checks; required importer authority must exist before full package validation.';
 }else r.metadataBoundary={applicable:false,reason:'Movement/support study is not a complete neutral/blink/look family; common input5/proposal not fabricated.'};
 fs.writeFileSync(path.join(dir,'official-checks.json'),JSON.stringify(r,null,2)+'\n');console.log(JSON.stringify({budget:r.rawCandidateBudget.status,proposalShape:r.proposal?.shapePass??null,sourceAdmitted:false}));
}
