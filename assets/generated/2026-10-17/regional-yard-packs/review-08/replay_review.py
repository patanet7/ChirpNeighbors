"""Reproduce four yard-scale GIFs using existing producer renderers in isolation."""
from pathlib import Path
import hashlib,json,subprocess,sys,tempfile
HERE=Path(__file__).resolve().parent
ROOT=next(p for p in HERE.parents if(p/'.git').exists())
m=json.loads((HERE/'manifest.json').read_text());by={x['source_key']:x for x in m['files']}
script=ROOT/by['expansion/review-08/tools/review_wind.py']['canonical_path']
results=[]
with tempfile.TemporaryDirectory(prefix='chirp-review08-replay-')as tmp:
    run=subprocess.run([sys.executable,str(script),'--repo',str(ROOT),'--output',tmp],capture_output=True,text=True)
    assert run.returncode==0,run.stderr[-4000:]
    for scope in['oak','deergrass']:
        for width in[960,384]:
            name=f'{scope}-gentle-yard-{width}.gif';e=by['expansion/review-08/wind/'+name];h=hashlib.sha256((Path(tmp)/name).read_bytes()).hexdigest();assert h==e['sha256']
            results.append({'file':name,'sha256':h,'exact_replay':True})
print(json.dumps({'status':'passed','application_modified':False,'source_wind_math_duplicated':False,'results':results},indent=2))
