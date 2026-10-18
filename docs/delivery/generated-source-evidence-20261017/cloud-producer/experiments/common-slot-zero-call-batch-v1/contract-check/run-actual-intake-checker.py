"""Run unmodified real CLI; retain failure/success reports without supplied private pins."""
import pathlib,json,subprocess,hashlib
O=pathlib.Path(__file__).resolve().parent;R=O.parent;UI=pathlib.Path('/workspace/runtime-common-v6-intake-inspect');out=O/'actual-cli';out.mkdir(exist_ok=True)
inputs=[R/'species/mourning_dove/source-handoff.json',R/'species/yellow_rumped_warbler/source-handoff.json']+sorted((O/'proposals').glob('*.INCOMPLETE.input-v4.json'))
receipts=[]
for p in inputs:
 key=(p.parent.parent.name+'-'+p.parent.name if p.name=='source-handoff.json' else p.stem)
 cmd=['node',str(UI/'scripts/check-common-intake.ts'),str(p)];r=subprocess.run(cmd,cwd=UI,capture_output=True,text=True)
 (out/(key+'.stdout.json')).write_text(r.stdout);(out/(key+'.stderr.txt')).write_text(r.stderr)
 d={'input':str(p.relative_to(R)),'inputSHA256':hashlib.sha256(p.read_bytes()).hexdigest(),'command':cmd,'workingDirectory':str(UI),'exitCode':r.returncode,'stdout':str((out/(key+'.stdout.json')).relative_to(O)),'stderr':str((out/(key+'.stderr.txt')).relative_to(O)),'runtimeSourceChanged':False}
 try:
  report=json.loads(r.stdout);d.update({'actualCheckerExecuted':True,'metadataComplete':report['metadataComplete'],'sourceAdmitted':report['sourceAdmitted'],'issueCount':len(report['issues']),'issues':report['issues']});assert report['sourceAdmitted'] is False
 except json.JSONDecodeError:d.update({'actualCheckerExecuted':False,'sourceAdmitted':False,'blocker':r.stderr})
 receipts.append(d)
result={'scope':'Actual unchanged runtime check-common-intake.ts at8cd; metadata preflight only, no submission or runtime admission','runtimeCommit':'8cd59c21abb990e5be95424587b3952d7fa3f1c4','previousFailureRetained':'actual-checker-blocker.json','dependencyResolution':{'method':'Parent installed exact dependencies in isolated directory; untracked node_modules symlink only, no runtime source/package edits','zod':'3.25.76','zod-to-json-schema':'3.25.2','directory':'/workspace/asset-production/recovery/common-intake-deps/node_modules'},'reports':receipts,'sourceAdmitted':False,'newCalls':0,'newDrawings':0}
(O/'actual-cli-results.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps([{'input':x['input'],'exitCode':x['exitCode'],'issues':x.get('issueCount'),'actual':x['actualCheckerExecuted']} for x in receipts]))
