"""Seal only after the coordinator's independent review is present; source bytes stay fixed."""
from pathlib import Path
import json,hashlib,zipfile
P=Path(__file__).parent;sha=lambda b:hashlib.sha256(b).hexdigest()
assert (P/'independent-review.json').exists(),'Independent review pending; do not seal.'
review=json.loads((P/'independent-review.json').read_text());assert review,'Empty review'
assert sha((P/'independent-review.json').read_bytes())=='daa41578d80871a610f3e738365912e6ab4477d681ff99ef313ed1846ef1cdf9'
assert sha((P/'independent-review.md').read_bytes())=='18b267fec3e37ffea3460580eee3d62bc20832a73f605c1fc633f9118386a562'
for file,hash in review['inputFileHashes'].items():assert sha((P/file).read_bytes())==hash,'Reviewed input changed: '+file
ledger=json.loads((P/'review-target-hashes.json').read_text())
for f in ledger['files']:assert sha((P/f['file']).read_bytes())==f['sha256'],'Frozen review target changed: '+f['file']
# Keep every reviewed metadata file unchanged; review status is in the review itself.
files=[f for f in P.rglob('*') if f.is_file() and f.name!='source-files.sha256.json' and f.suffix!='.zip'];index=[{'file':str(f.relative_to(P)),'bytes':f.stat().st_size,'sha256':sha(f.read_bytes())} for f in sorted(files)];(P/'source-files.sha256.json').write_text(json.dumps(index,indent=2)+'\n')
with zipfile.ZipFile(P/'ChirpNeighbors-Junco-Awake-v1.zip','w',zipfile.ZIP_DEFLATED) as z:
 for f in sorted(P.rglob('*')):
  if f.is_file() and f.suffix!='.zip':z.write(f,f.relative_to(P))
print(json.dumps({'file':str(P/'ChirpNeighbors-Junco-Awake-v1.zip'),'bytes':(P/'ChirpNeighbors-Junco-Awake-v1.zip').stat().st_size,'sha256':sha((P/'ChirpNeighbors-Junco-Awake-v1.zip').read_bytes()),'indexedFiles':len(index)}))
