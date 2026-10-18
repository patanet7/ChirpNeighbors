from pathlib import Path
import subprocess,json,hashlib,sys,shutil
P=Path(sys.argv[1]);O=P/'contract-intake';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert not (O/'invocations.json').exists(),'No duplicate diagnostic runs'
runner=Path('/workspace/asset-production/validation/shared-structural-check.mjs');assert sha(runner)=='5317b37dbd7229f7e0cf62302f70ad526890c99b56b2c0704b441cebfcb141e7'
repo=Path('/workspace/runtime-resting-intake-v5-inspect');head=subprocess.check_output(['git','-C',str(repo),'rev-parse','HEAD'],text=True).strip();assert head=='c4ae7529786e28cf55e2008b7f7b64215fc6542c'
rows=[]
cmd=['node',str(runner),'--repo',str(repo),'--input',str(O/'canonical-pixel-input.json'),'--receipt',str(O/'pixel-receipt.json'),'--sharp','/opt/codex/runtimes/codex-primary-runtime/dependencies/node/node_modules/sharp/dist/index.cjs']
for label,cmd in [('pixel',cmd),('json',['node',str(O/'actual-json-budget.mjs'),str(O)])]:
 r=subprocess.run(cmd,text=True,capture_output=True);(O/(label+'-stdout.txt')).write_text(r.stdout);(O/(label+'-stderr.txt')).write_text(r.stderr)
 lines=[l for l in r.stderr.splitlines() if l.startswith('PermanentStageError:') or l.startswith('Error:')]
 rows.append(dict(kind=label,command=cmd,exitCode=r.returncode,stdoutSHA256=sha(O/(label+'-stdout.txt')),stderrSHA256=sha(O/(label+'-stderr.txt')),exactError=lines[0] if lines else None))
(O/'invocations.json').write_text(json.dumps(rows,indent=2)+'\n')
authority={'runtimeCommit':head,'scope':'Pinned cloud source subset; not latest Mac or actual admission','sharedRunnerSHA256':sha(runner),'modules':[]}
for f in ['src/lib/server/asset-pipeline/package.ts','src/lib/server/pipeline/canonical.ts','src/lib/pipeline/canonical-json.ts','src/lib/server/pipeline/errors.ts']:
 if (repo/f).exists():authority['modules'].append({'file':f,'sha256':sha(repo/f)})
(O/'authority-receipt.json').write_text(json.dumps(authority,indent=2)+'\n')
print(json.dumps(rows))
