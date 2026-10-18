"""Restore exact selected source aliases from the canonical publication map."""
from pathlib import Path
import argparse,hashlib,json,shutil
PREFIX=Path('assets/generated/2026-10-17/regional-yard-packs/integration-10')
def materialize(repo,dest,previews=False):
 manifest=json.loads((repo/PREFIX/'manifest.json').read_text());count=0
 for e in manifest['files']:
  alias=e['source_key'].removeprefix('expansion/integration-10/')
  if alias.startswith('bundle/'):alias=alias.removeprefix('bundle/')
  elif previews and alias.startswith('previews/'):alias='reference-previews/'+alias.removeprefix('previews/')
  else:continue
  source=(repo/e['canonical_path']).resolve();assert source.is_relative_to(repo.resolve());data=source.read_bytes();assert hashlib.sha256(data).hexdigest()==e['sha256'];target=(dest/alias).resolve();assert target.is_relative_to(dest.resolve());target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data);count+=1
 return count
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--repo',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--with-previews',action='store_true');a=p.parse_args();print(json.dumps({'restored_files':materialize(a.repo,a.output,a.with_previews),'exact_bundle_metadata_bytes_preserved':True,'runtime_admitted':False}))
