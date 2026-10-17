from pathlib import Path
import hashlib,json,zipfile,sys,datetime
P=Path(__file__).parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
if len(sys.argv)!=3:raise SystemExit('Supply independently confirmed JSON and Markdown review SHA256 values, in that order.')
for name,expected in zip(['independent-review.json','independent-review.md'],sys.argv[1:]):
 p=P/name
 assert p.exists() and sha(p)==expected,(name,'stable independent hash mismatch')
 text=p.read_text();assert 'data:image/' not in text and 'iVBORw0KGgo' not in text,'Embedded browser capture data forbidden'
verification=json.load(open(P/'receipts/verification.json'));assert verification['status']=='passed'
primary=json.load(open(P/'PRIMARY-SOURCE-MANIFEST.json'));assert primary['nativeCalls']==1 and len(primary['frames'])==4
for name,key in [('original.png','originalSHA256'),('prompt.txt','promptSHA256')]:assert sha(P/name)==primary[key]
for f in primary['frames']:assert sha(P/f['sourcePNG'])==f['sourcePNGsha256'] and sha(P/f['outputPNG'])==f['outputPNGsha256']
seal={'batchId':P.name,'sealedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'sourceStatus':'generated and independently reviewed; see verdict for restrictions, not runtime admission','newDrawings':4,'reusedReferenceDrawings':1,'nativeCalls':1,'generationRunning':False,'generationStoppedAfterBoundedCall':True,'runtimeBound':False,'ownerApproved':False,'nextQueued':{'state':'queued','task':'Coordinator integration and animation-gap review; this worker holds with no next native call authorized'},'reviewHashes':dict(zip(['independent-review.json','independent-review.md'],sys.argv[1:])),'immutableInputNote':'Primary source manifest status records creation-time review-pending state. This separate seal records review completion without mutating reviewed inputs.','excluded':'Internal browser screenshots, ZIP, Library receipt and hash index itself. Generated-art diagnostics remain included.'}
(P/'bundle-seal.json').write_text(json.dumps(seal,indent=2)+'\n')
files=[p for p in sorted(P.rglob('*')) if p.is_file() and 'internal-browser' not in p.parts and '__pycache__' not in p.parts and p.suffix!='.zip' and p.name not in ['library-receipt.json','source-files.sha256.json']]
index={'batchId':P.name,'fileCount':len(files),'files':[{'path':str(p.relative_to(P)),'bytes':p.stat().st_size,'sha256':sha(p)} for p in files]}
(P/'source-files.sha256.json').write_text(json.dumps(index,indent=2)+'\n')
z=P/'ChirpNeighbors-Western-Bluebird-Hop-Source-Study.zip'
with zipfile.ZipFile(z,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as out:
 for p in files+[P/'source-files.sha256.json']:out.write(p,p.relative_to(P))
print(json.dumps({'path':str(z),'bytes':z.stat().st_size,'sha256':sha(z),'indexedSourceFiles':len(files),'zipEntries':len(files)+1},indent=2))
