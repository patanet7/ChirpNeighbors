"""Check source aliases, shared labels, exact normal/mobile replay and repaired annotation."""
from pathlib import Path
import json,hashlib,argparse,sys,subprocess,tempfile
sys.dont_write_bytecode=True
from materialize_source import materialize,PREFIX
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--repo',type=Path,required=True);a=p.parse_args();m=json.loads((a.repo/PREFIX/'manifest.json').read_text())
 for e in m['files']:assert sha(a.repo/e['canonical_path'])==e['sha256']==e['source_sha256']
 for n,h in json.loads((a.repo/PREFIX/'SHA256SUMS.json').read_text())['files'].items():assert sha(a.repo/n)==h
 with tempfile.TemporaryDirectory(prefix='asset-qualification-consumer-')as tmp:
  out=Path(tmp);n=materialize(a.repo,out)
  for name,h in json.loads((out/'file-index.json').read_text())['files'].items():assert sha(out/name)==h
  result=json.loads(subprocess.check_output([sys.executable,str(out/'tools/verify_qualification.py'),'--root',str(out)],text=True));assert result['result']=='pass';print(json.dumps({'result':'pass','restored_source_files':n,'consumer':result,'runtime_admitted':False,'physical_geometry_reviewed':False},indent=2))
