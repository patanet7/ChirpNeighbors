"""Replay oak and deergrass source-part motion in a temporary directory.
Requires Pillow and NumPy. No network or application modules are used.
"""
from pathlib import Path
import hashlib,json,shutil,subprocess,sys,tempfile
HERE=Path(__file__).resolve().parent
ROOT=next(p for p in HERE.parents if (p/'.git').exists())
manifest=json.loads((HERE/'manifest.json').read_text())
def resolve(v):
    if isinstance(v,str) and v.startswith('assets/generated/') and (ROOT/v).is_file():return str(ROOT/v)
    if isinstance(v,list):return [resolve(x)for x in v]
    if isinstance(v,dict):return {k:resolve(x)for k,x in v.items()}
    return v
results=[]
for scope,script,outputs in [
    ('oak','render_gentle.py',['previews/gentle-wind.gif','sprites/whole-tree-rest.png','previews/yard-960.png','previews/yard-384.png']),
    ('deergrass','scripts/render_gentle.py',['previews/deergrass-gentle-offline.gif','previews/healthy-assembly-alpha.png','previews/coastal-yard-review-full.png','previews/coastal-yard-review-960.png','previews/coastal-yard-review-384.png']),
]:
    prefix='expansion/repair-07/'+scope+'/'
    entries={e['source_key'][len(prefix):]:e for e in manifest['files']if e['source_key'].startswith(prefix)}
    with tempfile.TemporaryDirectory(prefix='chirp-repair-replay-')as temporary:
        stage=Path(temporary)
        for relative,e in entries.items():
            target=stage/relative;target.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(ROOT/e['canonical_path'],target)
            # Resolve portable canonical references in the isolated replay copy only.
            if target.suffix=='.json':target.write_text(json.dumps(resolve(json.loads(target.read_text())),indent=2)+'\n')
        run=subprocess.run([sys.executable,str(stage/script)],cwd=stage,capture_output=True,text=True)
        assert run.returncode==0,run.stderr[-4000:]
        for relative in outputs:
            actual=hashlib.sha256((stage/relative).read_bytes()).hexdigest();expected=entries[relative]['sha256']
            assert actual==expected,(scope,relative,actual,expected)
            results.append({'scope':scope,'output':relative,'sha256':actual,'exact_replay':True})
print(json.dumps({'status':'passed','isolated_replay':True,'application_modified':False,'results':results},indent=2))
