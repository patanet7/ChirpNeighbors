from pathlib import Path
import json,hashlib,zipfile,datetime
D=Path(__file__).parent
sha=lambda b:hashlib.sha256(b).hexdigest()
expected={'independent-review.json':'c812abd04c03c1f34326644a80a6e3783c9fa3e5eb9282094e8ee74f9f3a6a30','independent-review.md':'fa65a3d8fb5cfa5943d7d0f7487a82ce876f52649f463a68ae9dd49c99dfc86a','review.html':'2c38057c2678eb054620910c7b1c1289b05f266b0b6188cd6525d5db5e7e3560'}
for p,v in expected.items():assert sha((D/p).read_bytes())==v,(p,'review input changed')
stable=json.loads((D/'stable-review-inputs.json').read_text())
for p,v in stable['files'].items():assert sha((D/p).read_bytes())==v['sha256'],p
prompt=json.loads((D/'native-call-arguments.json').read_text())['prompt'].encode();assert prompt==(D/'prompt.txt').read_bytes()
summary={'kind':'sealed-reviewed-source-batch-not-runtime-admission','batchId':'sd20-purple-needlegrass-wind-v1','nativeGenerationCalls':1,'newDrawings':3,'globalDrawingRegistrationsHere':0,'firstIntake':'frames-source1024/calm.png','firstIntakeState':'provisional calm still; not owner approved','motionIntake':'rooted-wind.apng + PRIMARY-SOURCE-MANIFEST.json','motionState':'strong stepped-gust source study; gentle/fluid/seamless ambient-wind target failed','sourceGeometry':'Native pixels copied atscale1; full1024canvas; commonregisteredroot[512,900]; integertranslation only; rawatlasalignmentfailure preserved','frameIDs':[f['sourceFrameId'] for f in json.loads((D/'PRIMARY-SOURCE-MANIFEST.json').read_text())['frames']],'independentReviewExactHashes':expected,'sourceVerification':{'checksPassed':9,'checksTotal':9,'sourcePositiveAlphaPixels':725918,'lostPositiveAlphaPixels':0},'viewerRegression':'viewer-regression.json','playbackEvidence':'Independent16light/dark samples at8times,3poses+return; correctedviewer inspected; no browsercapture bytes','referenceRights':'Generatedsource, factualprimarytext reference constraints; no photo pixels; no CC/publicdomain or full commercialclearance claimed','actualYardBindingVerifiedHere':False,'separateEditableFoliageHierarchy':False,'generationRunning':False,'additionalGenerationAuthorized':False,'LibraryStateAtSeal':'ZIP upload follows seal; identity receipt excluded from ZIP/public copy','pending':'Coordinator source registration/publication; Mac intake and owner review; no fullwind admission','nextQueue':'Hold checkpoint. Any intermediatepose/rig continuation requires review prioritization; no autonomous furthercall.'}
(D/'bundle-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
# Exclude Librarytransport/identity receipts, archive output and selfindex. No browsercaptures exist.
excluded={'files.sha256.json','bundle-seal-receipt.json'}
ps=sorted(p for p in D.rglob('*') if p.is_file() and p.suffix!='.zip' and not any(t.startswith('.') for t in p.relative_to(D).parts) and p.name not in excluded and 'library' not in p.name.lower())
index={str(p.relative_to(D)):{'bytes':p.stat().st_size,'sha256':sha(p.read_bytes())} for p in ps}
(D/'files.sha256.json').write_text(json.dumps({'kind':'sealed-source-file-index','files':index,'selfExcluded':True,'privateLibraryReceiptsExcluded':True},indent=2)+'\n')
archive=D/'ChirpNeighbors-Purple-Needlegrass-Wind-v1.zip'
with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in ps+[D/'files.sha256.json']:z.write(p,str(p.relative_to(D)))
with zipfile.ZipFile(archive) as z:
 assert len(z.namelist())==len(ps)+1
 for p,v in index.items():assert sha(z.read(p))==v['sha256'],p
 assert all('library' not in p.lower() and not any(t.startswith('.') for t in Path(p).parts) for p in z.namelist())
receipt={'batchId':'sd20-purple-needlegrass-wind-v1','ZIP':archive.name,'ZIPbytes':archive.stat().st_size,'ZIPsha256':sha(archive.read_bytes()),'ZIPfileCount':len(ps)+1,'indexedFiles':len(index),'indexedFileHashesVerified':len(index),'exactReviewHashes':expected,'sourceCoreFrozenHashesVerified':len(stable['files']),'privateLibraryReceiptsInZIP':False,'savedBrowserCapturesInZIP':False,'newGenerationCallsAtSealing':0,'generationRunning':False}
(D/'bundle-seal-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
