"""Seal reviewed source bytes; run only with coordinator-supplied exact review hashes."""
from pathlib import Path
import json,hashlib,zipfile,argparse
args=argparse.ArgumentParser();args.add_argument('--review-json-sha',required=True);args.add_argument('--review-md-sha',required=True);args=args.parse_args();P=Path(__file__).parent;sha=lambda b:hashlib.sha256(b).hexdigest()
assert sha((P/'independent-review.json').read_bytes())==args.review_json_sha
assert sha((P/'independent-review.md').read_bytes())==args.review_md_sha
review=json.loads((P/'independent-review.json').read_text());assert review
reviewedHashes=review.get('inputFileHashes') or review.get('evidence',{}).get('inputHashes')
assert reviewedHashes,'Review must contain explicit input hashes'
for name,hash in reviewedHashes.items():assert sha((P/name).read_bytes())==hash,'Reviewed input changed: '+name
ledger=json.loads((P/'review-target-hashes.json').read_text())
for f in ledger['files']:assert sha((P/f['file']).read_bytes())==f['sha256'],'Frozen target changed: '+f['file']
files=[f for f in P.rglob('*') if f.is_file() and '.private' not in f.parts and f.name!='source-files.sha256.json' and f.suffix!='.zip'];index=[{'file':str(f.relative_to(P)),'bytes':f.stat().st_size,'sha256':sha(f.read_bytes())} for f in sorted(files)];(P/'source-files.sha256.json').write_text(json.dumps(index,indent=2)+'\n')
path=P/'ChirpNeighbors-California-Scrub-Jay-Blink-v1.zip'
with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED) as z:
 for f in sorted(files+[P/'source-files.sha256.json']):z.write(f,f.relative_to(P))
with zipfile.ZipFile(path) as z:
 for f in index:assert sha(z.read(f['file']))==f['sha256']
print(json.dumps({'file':str(path),'bytes':path.stat().st_size,'sha256':sha(path.read_bytes()),'indexedFiles':len(index),'ZIPFiles':len(index)+1}))
