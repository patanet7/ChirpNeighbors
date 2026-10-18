// Executes actual exported PR40 schemas; contains no replacement report schema.
import fs from 'node:fs';import path from 'node:path';import crypto from 'node:crypto';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {registerCanonicalLoader} from './canonical-loader.mjs';
const P=path.dirname(fileURLToPath(import.meta.url));
const sha=data=>crypto.createHash('sha256').update(data).digest('hex');
const requireFact=(ok,message)=>{if(!ok)throw Error(message);};
const args=process.argv.slice(2),get=key=>args[args.indexOf(key)+1];
requireFact(args.includes('--config')&&args.includes('--out'),'Required --config path --out NEWPATH');
const configPath=path.resolve(get('--config')),out=path.resolve(get('--out'));
requireFact(!fs.existsSync(out),'Refusing to overwrite output');
const configBytes=fs.readFileSync(configPath),config=JSON.parse(configBytes);
const observed=new Map();
observed.set(configPath,sha(configBytes));
function read(file,expected){const b=fs.readFileSync(file);if(expected)requireFact(sha(b)===expected,'SHA changed: '+file);observed.set(file,sha(b));return b;}
const provenancePath=path.join(P,'canonical-export-provenance.json');
requireFact(/^[a-f0-9]{64}$/.test(config.canonicalExportProvenanceSHA256),'Exact source-export provenance pin required');
const provenance=JSON.parse(read(provenancePath,config.canonicalExportProvenanceSHA256));
requireFact(provenance.commit==='ba87917fc93c547dae07e78c3148542390c2456c','Wrong source commit');
for(const f of provenance.files)read(path.join(P,'canonical-export',f.file),f.sha256);
requireFact(/^[a-f0-9]{64}$/.test(config.dependencyProvenanceSHA256),'Exact dependency provenance pin required');
const dependency=JSON.parse(read(path.join(P,'dependency-provenance.json'),config.dependencyProvenanceSHA256));
const dependencyDirectory=path.resolve(args.includes('--zod-directory')?get('--zod-directory'):
 process.env.ASSET_QUALITY_ZOD_DIR||dependency.directory);
for(const f of dependency.files)read(path.join(dependencyDirectory,f.file),f.sha256);
requireFact(JSON.parse(fs.readFileSync(path.join(dependencyDirectory,'package.json'))).version===dependency.version,'Dependency version differs');
registerCanonicalLoader(dependencyDirectory);
const api=await import(pathToFileURL(path.join(P,'canonical-export',provenance.sourceModule)).href);
const root=path.resolve(config.evidenceRoot||path.join(P,'../..'));
function referenced(ref){
 requireFact(ref&&typeof ref.file==='string'&&!path.isAbsolute(ref.file)&&!ref.file.split('/').includes('..'),'Unsafe input reference');
 const full=path.join(root,ref.file);requireFact(fs.realpathSync(full)===full,'Symlink input not allowed');
 requireFact(/^[a-f0-9]{64}$/.test(ref.sha256),'Exact input SHA256 required');return read(full,ref.sha256);
}
// A tiny JSON span reader for the explicitly known producer {records:[]} file.
// It returns exact record substrings, never reserializes retained source data.
function recordTexts(text){
 let i=0;const ws=()=>{while(/\s/.test(text[i]||'')&&i<text.length)i++;};
 function string(){const start=i++;while(i<text.length){if(text[i]==='\\'){i+=2;continue;}if(text[i++]==='"')return JSON.parse(text.slice(start,i));}throw Error('Unclosed JSON string');}
 function value(){ws();const start=i;if(text[i]==='"')string();else if(text[i]==='{'||text[i]==='['){const close=text[i++]==='{'?'}':']';ws();if(text[i]!==close){while(true){if(close==='}'){string();ws();requireFact(text[i++]===':','Invalid JSON member');}value();ws();if(text[i]!==',')break;i++;ws();}}requireFact(text[i++]===close,'Invalid JSON container');}else{while(i<text.length&&!/[\s,\]}]/.test(text[i]))i++;requireFact(i>start,'Invalid JSON value');}return text.slice(start,i);}
 JSON.parse(text);ws();requireFact(text[i++]==='{','Known producer envelope must be an object');let result=null;ws();
 while(text[i]!=='}'){const key=string();ws();requireFact(text[i++]===':','Invalid envelope');ws();if(key==='records'){
   requireFact(result===null&&text[i++]==='[','Duplicate/nonarray records');result=[];ws();if(text[i]!==']')while(true){result.push(value());ws();if(text[i]!==',')break;i++;ws();}requireFact(text[i++]===']','Invalid records array');
  }else value();ws();if(text[i]!==',')break;i++;ws();}
 requireFact(Array.isArray(result),'No known records[] envelope');return result;
}
const results={sourceCommit:provenance.commit,sourceModuleSHA256:provenance.files.find(f=>f.file===provenance.sourceModule).sha256,
 canonicalExportProvenanceSHA256:sha(fs.readFileSync(provenancePath)),configSHA256:sha(configBytes),harnessSHA256:sha(fs.readFileSync(fileURLToPath(import.meta.url))),
 actualExports:Object.keys(api).sort(),retainedSources:[],reports:[],selfTests:[],runtimeAdmission:false,artworkOrSourceMutations:0,modelCalls:0,
 limits:api.ASSET_QUALITY_LIMITS,classificationReference:api.ASSET_QUALITY_SOURCE_LABEL_CLASSIFICATIONS_V1,
 dependencyDirectoryUsed:dependencyDirectory,dependencyVersion:dependency.version,
 dependencyProvenanceSHA256:config.dependencyProvenanceSHA256,loaderSHA256:sha(read(path.join(P,'canonical-loader.mjs'))),
 producerReportEnvelopesSubmitted:(config.reports||[]).length,
 reportConstructionBlockedReasons:config.reportConstructionBlockedReasons||[],
 validationScope:'Actual source-retention API plus any explicitly submitted report envelopes; no envelope synthesized from producer source findings',
 actualSchemaFieldNames:{report:Object.keys(api.assetQualityEvaluationSchema.innerType().shape),
 finding:Object.keys(api.assetQualityFindingSchema.innerType().shape),
 subject:Object.keys(api.assetQualityEvaluationSchema.innerType().shape.subject.shape),
 requirement:Object.keys(api.assetQualityEvaluationSchema.innerType().shape.requirement.shape)}};
if(config.lineageSelection){referenced(config.lineageSelection);results.lineageSelection=config.lineageSelection;}
for(const unit of config.retainedSources||[]){
 try{
  const bytes=referenced(unit),texts=recordTexts(bytes.toString('utf8'));
  requireFact(Number.isInteger(unit.recordIndex)&&unit.recordIndex>=0&&unit.recordIndex<texts.length,'Record index missing');
  const original=texts[unit.recordIndex],originalHash=sha(Buffer.from(original));
  requireFact(unit.applicability==='unverified'||unit.applicability==='subject-source','Explicit retention applicability required');
  const source=api.retainCanonicalAssetDefectSourceLabel(original,originalHash,unit.applicability);
  const label=api.resolveAssetQualitySourceLabel(source,unit.mappings||[]);
  requireFact(source.originalRecord.json===original,'Source text changed');
  results.retainedSources.push({id:unit.id,status:'PASS_ACTUAL_CANONICAL_RETENTION',inputFile:unit.file,inputSHA256:unit.sha256,recordIndex:unit.recordIndex,
   exactOriginalRecordSHA256:originalHash,label,classificationStatus:label.status,
   classificationPermittedByCanonicalReference:api.ASSET_QUALITY_SOURCE_LABEL_CLASSIFICATIONS_V1[source.rawLabel],
   fullReportValidation:'NOT_RUN_NO_REPORT_SUBMITTED',sourceBinding:'BLOCKED_MISSING_INDEPENDENT_CURRENT_CONSUMER_CONTEXT',
   noSourceGradeKnowledgeVerdictConversion:true});
 }catch(error){results.retainedSources.push({id:unit.id,status:'FAIL_ACTUAL_CANONICAL_RETENTION',error:String(error)});}
}
for(const unit of config.reports||[]){
 try{
  const bytes=referenced(unit),report=api.parseAssetQualityEvaluationJson(bytes.toString('utf8'));
  const canonical=api.serializeAssetQualityEvaluation(report);let bindingStatus='BLOCKED_MISSING_INDEPENDENT_CURRENT_CONSUMER_CONTEXT';
  if(unit.binding){const binding=JSON.parse(referenced(unit.binding));api.validateAssetQualityEvaluation(report,binding);bindingStatus='PASS_PROVIDED_CONTEXT_SEMANTICS_ONLY_NOT_AUTHENTICATED_BY_HARNESS';}
  results.reports.push({id:unit.id,status:'PASS_ACTUAL_REPORT_SCHEMA_AND_SEMANTICS',canonicalSHA256:sha(Buffer.from(canonical)),canonicalUTF8Bytes:Buffer.byteLength(canonical),bindingStatus,
   sourceKnowledge:report.findings.map(f=>({id:f.id,knowledge:f.knowledge,verdict:f.verdict,severity:f.severity,confidence:f.confidence})),grantsAdmission:report.grantsAdmission});
 }catch(error){results.reports.push({id:unit.id,status:'FAIL_ACTUAL_REPORT_VALIDATION',error:String(error)});}
}
if(config.syntheticSelfTests){
 const fixture=JSON.parse(fs.readFileSync(path.join(P,'canonical-export/contracts/fixtures/asset-quality-evaluation-v1.synthetic.json')));
 for(const name of ['crow','bath']){const input=fixture[name];
  const report=api.parseAssetQualityEvaluationJson(JSON.stringify(input));requireFact(api.serializeAssetQualityEvaluation(api.parseAssetQualityEvaluationJson(api.serializeAssetQualityEvaluation(report)))===api.serializeAssetQualityEvaluation(report),'Canonical roundtrip changed');
  results.selfTests.push({name:'synthetic-positive-'+name,passed:true,basis:report.basis,consumerBinding:'NOT_RUN'});
 }
 for(const [name,mutate]of [['forged-admission',r=>r.grantsAdmission=true],['unknown-rule',r=>r.findings[0].label={...r.findings[0].label,ruleId:'invented-rule'}],['unknown-measurement-pass',r=>{r.findings[0].knowledge='unknown';r.findings[0].verdict='pass';}],['unscoped-contact-proof',r=>{r.findings[0].contactBasis='reviewed-reference';r.findings[0].target.contactKind='left-foot';}]]){
  const report=structuredClone(fixture.crow);mutate(report);let rejected=false;try{api.serializeAssetQualityEvaluation(report);}catch{rejected=true;}requireFact(rejected,'Negative control unexpectedly accepted: '+name);results.selfTests.push({name,passed:true,rejected:true,basis:'SYNTHETIC_VALIDATOR_CONTROL_ONLY'});
 }
 const unknown=structuredClone(fixture.crow);unknown.findings[0].label.source={catalogId:'shared-source-art-defect-label-contract',catalogVersion:'1',rawLabel:'invented.source-label'};
 requireFact(!api.assetQualityEvaluationSchema.safeParse(unknown).success,'Unknown source label accepted');results.selfTests.push({name:'unknown-canonical-source-label',passed:true,rejected:true});
}
for(const [file,hash]of observed)requireFact(sha(fs.readFileSync(file))===hash,'Input changed during validation');
results.inputFilesUnchanged=true;results.rows=results.retainedSources.length;results.uniqueCanonicalSourceLabels=[...new Set(results.retainedSources.filter(r=>r.label).map(r=>r.label.source.rawLabel))];
results.classificationCounts=Object.fromEntries(['mapped','unclassified'].map(s=>[s,results.retainedSources.filter(r=>r.classificationStatus===s).length]));
results.passed=results.retainedSources.every(r=>r.status.startsWith('PASS'))&&results.reports.every(r=>r.status.startsWith('PASS'));
fs.mkdirSync(path.dirname(out),{recursive:true});fs.writeFileSync(out,JSON.stringify(results,null,2)+'\n',{flag:'wx'});console.log(JSON.stringify({passed:results.passed,rows:results.rows,reports:results.reports.length,selfTests:results.selfTests.length,out}));
if(!results.passed)process.exitCode=1;
