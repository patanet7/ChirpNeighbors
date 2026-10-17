from pathlib import Path
import hashlib,json,zipfile,sys,datetime
P=Path(__file__).parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
if len(sys.argv)!=3:raise SystemExit('Supply coordinator-confirmed final JSON and Markdown review SHA256 values.')
for name,h in zip(['independent-review.json','independent-review.md'],sys.argv[1:]):
 assert (P/name).exists() and sha(P/name)==h,(name,'final independent hash mismatch')
 text=(P/name).read_text();assert 'data:image/' not in text and 'iVBORw0KGgo' not in text,'Browser capture image payload forbidden'
m=json.load(open(P/'PRIMARY-SOURCE-MANIFEST.json'));assert m['nativeCalls']==1 and len(m['frames'])==1 and len(m['reusedFrames'])==1
args=json.load(open(P/'receipts/native-args.json'));assert args['prompt'].encode()==(P/m['prompt']).read_bytes()
assert sha(P/m['prompt'])==m['promptSHA256'] and sha(P/m['original'])==m['originalSHA256']
for f in m['frames']+m['reusedFrames']:assert sha(P/f['sourcePNG'])==f['sourcePNGsha256'] and sha(P/f['outputPNG'])==f['outputPNGsha256']
mapping=json.load(open(P/'frame-to-action-map.json'))
for v in mapping['variants']:assert sha(P/v['atlasFile'])==v['atlasSHA256'] and sha(P/v['manifestFile'])==v['manifestSHA256']
assert json.load(open(P/'receipts/verification.json'))['status']=='passed'
seal={'batchId':P.name,'sealedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'sourceStatus':'independently reviewed source; exact verdict/restrictions in review files, not app admission','newPrimaryDrawings':1,'reusedPrimaryDrawings':1,'registeredDerivativeNewDrawings':0,'nativeCalls':1,'generationRunning':False,'nextQueued':{'state':'queued','task':'Coordinator integration/animation-gap review; no automatic native retry'},'reviewHashes':dict(zip(['independent-review.json','independent-review.md'],sys.argv[1:])),'inputStatusNote':'Immutable intake/source flags record pre-review pending-study state. Final reviewer verdict accompanies this seal without altering reviewed input hashes.','runtimeBound':False,'ownerApproved':False,'browserCaptureImagesIncluded':False,'originalAndNativePrimaryUnchanged':True}
(P/'bundle-seal.json').write_text(json.dumps(seal,indent=2)+'\n')
files=[x for x in sorted(P.rglob('*')) if x.is_file() and 'internal-browser' not in x.parts and '__pycache__' not in x.parts and x.suffix!='.zip' and x.name not in ['source-files.sha256.json','library-receipt.json']]
index={'batchId':P.name,'fileCount':len(files),'files':[{'path':str(x.relative_to(P)),'bytes':x.stat().st_size,'sha256':sha(x)} for x in files]};(P/'source-files.sha256.json').write_text(json.dumps(index,indent=2)+'\n')
z=P/'ChirpNeighbors-Western-Bluebird-Blink-Source-Study.zip'
with zipfile.ZipFile(z,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as out:
 for f in files+[P/'source-files.sha256.json']:out.write(f,f.relative_to(P))
print(json.dumps({'path':str(z),'bytes':z.stat().st_size,'sha256':sha(z),'indexedSourceFiles':len(files),'zipEntries':len(files)+1,'indexBytes':(P/'source-files.sha256.json').stat().st_size,'indexSHA256':sha(P/'source-files.sha256.json')},indent=2))
