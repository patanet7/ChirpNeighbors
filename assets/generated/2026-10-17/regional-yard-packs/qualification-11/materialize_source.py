"""Restore exact review-source aliases, including shared labels, from this checkout."""
from pathlib import Path
import argparse,json,hashlib
PREFIX=Path('assets/generated/2026-10-17/regional-yard-packs/qualification-11')
def materialize(repo,destination):
 m=json.loads((repo/PREFIX/'manifest.json').read_text());n=0
 for e in m['files']:
  rel=e['source_key'].removeprefix('expansion/qualification-11/');p=(repo/e['canonical_path']).resolve();assert p.is_relative_to(repo.resolve());b=p.read_bytes();assert hashlib.sha256(b).hexdigest()==e['sha256'];q=(destination/rel).resolve();assert q.is_relative_to(destination.resolve());q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(b);n+=1
 return n
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--repo',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();print(json.dumps({'restored_exact_files':materialize(a.repo,a.output)}))
