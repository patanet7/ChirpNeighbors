"""Verify exact publication bytes and replay one complete source assembly."""
from pathlib import Path
import argparse,hashlib,json,subprocess,sys,tempfile
sys.dont_write_bytecode = True
from materialize_bundle import materialize,PREFIX
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--repo',type=Path,required=True);a=p.parse_args();manifest=json.loads((a.repo/PREFIX/'manifest.json').read_text())
 for e in manifest['files']:assert sha(a.repo/e['canonical_path'])==e['sha256']==e['source_sha256']
 for name,h in json.loads((a.repo/PREFIX/'SHA256SUMS.json').read_text())['files'].items():assert sha(a.repo/name)==h
 with tempfile.TemporaryDirectory(prefix='selected-yard-source-')as tmp:
  d=Path(tmp);restored=materialize(a.repo,d,True)
  for name,h in json.loads((d/'SHA256SUMS.json').read_text())['files'].items():assert sha(d/name)==h
  result=json.loads(subprocess.check_output([sys.executable,str(d/'verify_bundle.py'),'--bundle',str(d)],text=True))
  out=d/'replayed';subprocess.run([sys.executable,str(d/'render_bundle.py'),'--bundle',str(d),'--output',str(out)],check=True,stdout=subprocess.DEVNULL)
  outputs=[]
  for f in sorted(out.iterdir()):assert sha(f)==sha(d/'reference-previews'/f.name);outputs.append({'file':f.name,'sha256':sha(f)})
  assert len(outputs)==12
  print(json.dumps({'result':'pass','publication_records':len(manifest['files']),'restored_aliases':restored,'source_checks':result,'exact_replay_outputs':outputs,'runtime_admitted':False,'physical_geometry_reviewed':False},indent=2))
