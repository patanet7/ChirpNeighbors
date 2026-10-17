from pathlib import Path
import hashlib,json,datetime,zipfile
P=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
expected={'independent-review.json':'38ac6f707dd828c6760e8babee9a0650ec77b5c238ce30e7ee7a0e2d73311b53','independent-review.md':'8da04786ced323ecc26c9e035288b50cad7fafde4088f1e0b5600b7c2fef60c7','annex/independent-technical-review.json':'1e8b8691bfd3fca957c050f9932a59d2b54205206263ac6572e27c1c2331def5','annex/registered-texture-review-manifest.json':'5266e6101c4173e899919fa46f1be4f93ac6181e2e5df978531a2cea9209959c'}
for name,h in expected.items():
 f=P/name;assert sha(f)==h,(name,'stable hash mismatch')
 if name.endswith(('review.json','review.md')):
  text=f.read_text();assert 'data:image/' not in text and 'iVBORw0KGgo' not in text,'Capture payload forbidden'
stable=json.load(open(P/'annex/ANNEX-STABLE-REVIEW-INPUTS.json'))
for name,r in stable['files'].items():assert sha(P/'annex'/name)==r['sha256']
primary=json.load(open(P/'PRIMARY-SOURCE-MANIFEST.json'));args=json.load(open(P/'receipts/native-args.json'))
assert primary['nativeCalls']==1 and len(primary['frames'])==1 and len(primary['reusedFrames'])==1
assert args['prompt'].encode()==(P/primary['prompt']).read_bytes()
assert sha(P/primary['prompt'])==primary['promptSHA256'] and sha(P/primary['original'])==primary['originalSHA256']
for f in primary['frames']+primary['reusedFrames']:assert sha(P/f['sourcePNG'])==f['sourcePNGsha256'] and sha(P/f['outputPNG'])==f['outputPNGsha256']
before={str(x.relative_to(P)):sha(x) for x in P.rglob('*') if x.is_file() and x.suffix!='.zip' and x.name not in ['bundle-seal.json','source-files.sha256.json','library-receipt.json']}
seal={'batchId':P.name,'sealedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'nativeCalls':1,'newPrimaryDrawings':1,'newNeutralDrawings':0,'reusedPrimaryDrawings':1,'registeredDerivativeNewDrawings':0,'sourceStatus':'registered variant independently recommended provisionally; native control retained','artReview':{'json':'independent-review.json','jsonSHA256':expected['independent-review.json'],'markdown':'independent-review.md','markdownSHA256':expected['independent-review.md'],'recommendation':'registered provisional source candidate; small toe/belly/feather redraw retained'},'technicalAnnex':{'bindingIndex':'annex/technical-contract-annex.json','independentReceipt':'annex/independent-technical-review.json','independentReceiptSHA256':expected['annex/independent-technical-review.json'],'selectedManifest':'annex/registered-texture-review-manifest.json','selectedManifestSHA256':expected['annex/registered-texture-review-manifest.json'],'result':'local explicit shape/hash/pixel mapping checks pass','canonicalSharpExecuted':False,'MacAdmission':False,'registeredSecondContactAlpha':74,'qualification':'Second contact is semitransparent. Positive alpha is not opaque toe/anatomical support or physical contact approval. Pivot clarification retained in annex; no source geometry changed.'},'historicalPendingLabels':'Frozen original PRIMARY/frame-to-action-map/intake flags retain their pre-review labels; final art recommendation and separate technical shape result are recorded here without changing those reviewed inputs.','frozenFilesUnchangedAtSeal':True,'preSealFrozenFileCount':len(before),'runtimeBound':False,'ownerApproved':False,'generationRunning':False,'nextQueued':{'state':'queued','task':'Wren independent review/seal, then Anna contract preparation only; no image call authorized'},'browserCaptureImagesIncluded':False}
(P/'bundle-seal.json').write_text(json.dumps(seal,indent=2)+'\n')
files=[x for x in sorted(P.rglob('*')) if x.is_file() and 'internal-browser' not in x.parts and '__pycache__' not in x.parts and x.suffix!='.zip' and x.name not in ['source-files.sha256.json','library-receipt.json']]
index={'batchId':P.name,'fileCount':len(files),'files':[{'path':str(x.relative_to(P)),'bytes':x.stat().st_size,'sha256':sha(x)} for x in files]};(P/'source-files.sha256.json').write_text(json.dumps(index,indent=2)+'\n')
z=P/'ChirpNeighbors-Western-Bluebird-Blink-Source-Study.zip'
with zipfile.ZipFile(z,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as out:
 for f in files+[P/'source-files.sha256.json']:out.write(f,f.relative_to(P))
assert all(sha(P/n)==h for n,h in before.items()),'Frozen file changed during seal'
print(json.dumps({'path':str(z),'bytes':z.stat().st_size,'sha256':sha(z),'indexedSourceFiles':len(files),'zipEntries':len(files)+1,'indexBytes':(P/'source-files.sha256.json').stat().st_size,'indexSHA256':sha(P/'source-files.sha256.json'),'allPreSealFilesUnchanged':True},indent=2))
