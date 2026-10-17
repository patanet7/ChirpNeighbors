from pathlib import Path
import json,hashlib,sys,zipfile,datetime
P=Path(__file__).parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
# Final art JSON/MD plus independent second-review receipt, exact root-confirmed hashes.
if len(sys.argv)<7 or len(sys.argv)%2!=1:raise SystemExit('Provide at least3 relative-review-file SHA256 pairs confirmed by coordinator, including both independent reviews.')
reviews={}
for name,h in zip(sys.argv[1::2],sys.argv[2::2]):
 file=P/name;assert file.resolve().is_relative_to(P.resolve()) and file.is_file();assert sha(file)==h,(name,'final review hash mismatch');text=file.read_text();assert 'data:image/' not in text and 'iVBORw0KGgo' not in text,'No embedded browser capture bytes';reviews[name]=h
assert len(reviews)>=3
stable=json.load(open(P/'review-target-hashes.json'))
for name,r in stable['files'].items():assert sha(P/name)==r['sha256'],(name,'frozen source input changed')
m=json.load(open(P/'PRIMARY-SOURCE-MANIFEST.json'));assert m['nativeCalls']==1 and len(m['frames'])==4 and len(m['reusedFrames'])==4
assert json.load(open(P/'receipts/native-args.json'))['prompt'].encode()==(P/m['prompt']).read_bytes()
assert sha(P/m['prompt'])==m['promptSHA256'] and sha(P/m['original'])==m['originalSHA256']
for f in m['frames']+m['reusedFrames']:assert sha(P/f['sourcePNG'])==f['sourcePNGsha256'] and sha(P/f['outputPNG'])==f['outputPNGsha256']
seal={'batchId':P.name,'sealedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'nativeCalls':1,'newPrimaryDrawings':4,'reusedPrimaryDrawings':4,'newNeutralOrHoverDrawings':0,'sourceStatus':'Independently reviewed source drawings and authored trajectory; exact limitations/verdicts in final review files. No runtime admission inferred.','finalReviewHashes':reviews,'frozenInputHashesUnchanged':True,'historicalPendingFlags':'Frozen PRIMARY and source contracts retain creation-time pending labels; this separate seal records receipt completion without editing reviewed input.','originalAlphaPreservedInPrimary':True,'renderWindowAlpha1FringeExclusionDisclosed':True,'sourceScale':'one common eye-to-bill family calibration; no perpose scale/body fitting','trajectoryIsNewDrawing':False,'canonicalSharpReceipt':None,'MacRuntimeBound':False,'ownerApproved':False,'generationRunning':False,'nextQueue':'Coordinator Anna integration/source-action review; no additional native call authorized in this packet','browserCaptureImagesIncluded':False}
(P/'bundle-seal.json').write_text(json.dumps(seal,indent=2)+'\n')
files=[f for f in sorted(P.rglob('*')) if f.is_file() and 'internal-browser' not in f.parts and '__pycache__' not in f.parts and f.suffix!='.zip' and f.name not in ['source-files.sha256.json','library-receipt.json']]
index={'batchId':P.name,'fileCount':len(files),'files':[{'path':str(f.relative_to(P)),'bytes':f.stat().st_size,'sha256':sha(f)} for f in files]};(P/'source-files.sha256.json').write_text(json.dumps(index,indent=2)+'\n')
z=P/'ChirpNeighbors-Anna-Dart-Brake-Source-Study.zip'
with zipfile.ZipFile(z,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as out:
 for f in files+[P/'source-files.sha256.json']:out.write(f,f.relative_to(P))
print(json.dumps({'path':str(z),'bytes':z.stat().st_size,'sha256':sha(z),'indexedSourceFiles':len(files),'zipEntries':len(files)+1,'indexBytes':(P/'source-files.sha256.json').stat().st_size,'indexSHA256':sha(P/'source-files.sha256.json')},indent=2))
