"""Standard JSON Schema against exact published export; not runtime source validation."""
import json,pathlib,hashlib,re,importlib.metadata
import jsonschema
O=pathlib.Path(__file__).resolve().parent; R=O.parent
schema_path=O/'public-contracts/asset-packaging-input-v4.schema.json'; schema=json.loads(schema_path.read_text()); V=jsonschema.validators.validator_for(schema);V.check_schema(schema);validator=V(schema)
def ptr(parts):return ''.join('/'+str(x).replace('~','~0').replace('/','~1') for x in parts) or '/'
inputs=[R/'species/mourning_dove/source-handoff.json',R/'species/yellow_rumped_warbler/source-handoff.json']+sorted((O/'proposals').glob('*.INCOMPLETE.input-v4.json'))
reports=[]
for p in inputs:
 data=json.loads(p.read_text());errors=[]
 for e in sorted(validator.iter_errors(data),key=lambda e: (str(list(e.absolute_path)),str(e.validator),e.message)):
  d={'instancePath':ptr(e.absolute_path),'schemaPath':ptr(e.absolute_schema_path),'keyword':e.validator,'message':e.message}
  if e.validator=='required':
   m=re.fullmatch("'([^']+)' is a required property",e.message)
   if m:d['missingPath']=ptr(list(e.absolute_path)+[m[1]])
  errors.append(d)
 reports.append({'input':str(p.relative_to(R)),'inputSHA256':hashlib.sha256(p.read_bytes()).hexdigest(),'status':'PASS static exported JSON Schema only' if not errors else 'FAIL static exported JSON Schema','errorCount':len(errors),'errors':errors,'runtimeSourceRefinementsExecuted':False,'actualRuntimeCLIExecuted':False,'sourceAdmitted':False})
result={'authority':'Exact official exported asset-packaging-input-v4 JSON Schema; secondary static fallback, not an alternate implementation of runtime refinements','schemaSHA256':hashlib.sha256(schema_path.read_bytes()).hexdigest(),'publicSourceCommit':'130f04517127036d6787d7741b8b55beb2fb04c8','schemaMatchesRuntimeCommit':'8cd59c21abb990e5be95424587b3952d7fa3f1c4','library':'jsonschema','libraryVersion':importlib.metadata.version('jsonschema'),'dialect':schema['$schema'],'customRuntimeRefinementsIncluded':False,'actualCheckerBlockedBy':'ERR_MODULE_NOT_FOUND zod','reports':reports,'sourceAdmitted':False}
(O/'static-public-schema-results.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps([{'input':r['input'],'errors':r['errorCount'],'missingPaths':[e['missingPath'] for e in r['errors'] if 'missingPath' in e]} for r in reports]))
