from pathlib import Path
import json,hashlib,zipfile
P=Path(__file__).resolve().parent
review=P/'independent-review.json'
assert review.exists(),'Independent review must be present before sealing'
reviewtext=review.read_text()
json.loads(reviewtext)
assert 'data:image/' not in reviewtext and 'iVBORw0KGgo' not in reviewtext, 'Reviewer must not embed browser captures'
md=P/'independent-review.md'
if md.exists():
 assert 'data:image/' not in md.read_text() and 'iVBORw0KGgo' not in md.read_text(), 'Reviewer Markdown must not embed captures'
status=json.loads((P/'status.json').read_text())
status.update(state='staged',sourceReviewed=True,normalSizePlaybackReviewed=True,independentReview='complete-see-independent-review.json',running=False,next='Parent source registration/publication and Mac canonical intake; finalfour queued-not-started, no new generation here')
(P/'status.json').write_text(json.dumps(status,indent=2)+'\n')
zipname='ChirpNeighbors-Woodpecker-Warbler-Oriole-Canons.zip'
files=sorted(x for x in P.rglob('*') if x.is_file() and 'internal-browser' not in x.parts and x.name not in ['source-files.sha256.json',zipname,'library-receipt.json'])
index={'files':[{'path':str(x.relative_to(P)),'bytes':x.stat().st_size,'sha256':hashlib.sha256(x.read_bytes()).hexdigest()} for x in files]}
(P/'source-files.sha256.json').write_text(json.dumps(index,indent=2)+'\n')
z=P/zipname
with zipfile.ZipFile(z,'w',zipfile.ZIP_DEFLATED) as a:
 for x in files+[P/'source-files.sha256.json']:a.write(x,str(x.relative_to(P)))
print(json.dumps({'zip':str(z),'bytes':z.stat().st_size,'sha256':hashlib.sha256(z.read_bytes()).hexdigest(),'indexedSourceFiles':len(files),'zipFiles':len(files)+1}))
