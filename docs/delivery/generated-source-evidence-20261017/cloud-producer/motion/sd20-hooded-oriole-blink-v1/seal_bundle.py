"""Seal only after coordinator supplies exact final independent-review hashes."""
from pathlib import Path
import argparse,json,hashlib,zipfile,datetime,re
P=Path(__file__).parent;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
a=argparse.ArgumentParser()
for name in ['visual-json','visual-md','technical-json','technical-md']:a.add_argument('--'+name,required=True)
args=a.parse_args();reviews=dict(zip(['independent-review.json','independent-review.md','source-technical-review.json','source-technical-review.md'],[args.visual_json,args.visual_md,args.technical_json,args.technical_md]))
assert all(re.fullmatch('[a-f0-9]{64}',h) and sha(P/n)==h for n,h in reviews.items())
frozen=json.loads((P/'review-target-hashes.json').read_text())['files'];assert all(sha(P/n)==h for n,h in frozen.items())
v=json.loads((P/'independent-review.json').read_text());t=json.loads((P/'source-technical-review.json').read_text())
verdict={k:v[k] for k in ['disposition','recommendation','verdict','sourceDisposition','overallDisposition'] if k in v}
receipt={'batchId':P.name,'sealedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'finalReviewHashes':reviews,'originalFrozenTargetsUnchanged':len(frozen),'visualVerdictFields':verdict,'finalSourceDisposition':'HELD native eyelid-closure study; zero normal-yard blink coverage gain','normalYardBlinkAccepted':False,'usefulBlinkGain':0,'newClosureStudyDrawings':1,'individualLibraryUpload':'NOT_REQUESTED; coordinator combined handoff only','producerPendingHeldLabelsHistorical':'Frozen source metadata is retained as original review input; final independent review files are authoritative for source usefulness only.','canonicalMacAdmission':'NOT_RUN','geometryReviewed':False,'supportWorld':None,'appBound':False,'newNativeCalls':1,'newDrawings':1,'newNeutral':0,'newLook':0,'reusedAwake':1,'renderClipId':'blink','idleFirstNeutralHoldTicks':60,'blinkTicks':[60,3,27],'sourceOriginalAndPromptUnchanged':True,'browserCapturesIncluded':False}
(P/'FINAL-SEAL-RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n')
exclude={'source-files.sha256.json','ChirpNeighbors-Hooded-Oriole-Blink-Source.zip'}
files=[p for p in sorted(P.iterdir()) if p.is_file() and p.name not in exclude and not p.name.startswith('library-')]
index=[{'file':p.name,'bytes':p.stat().st_size,'sha256':sha(p)} for p in files];(P/'source-files.sha256.json').write_text(json.dumps(index,indent=2)+'\n');files.append(P/'source-files.sha256.json')
archive=P/'ChirpNeighbors-Hooded-Oriole-Blink-Source.zip'
with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
 for p in files:
  info=zipfile.ZipInfo(p.name,date_time=(1980,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o100644<<16;z.writestr(info,p.read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
with zipfile.ZipFile(archive) as z:
 assert z.testzip() is None and len(z.infolist())==len(files)
 assert all(hashlib.sha256(z.read(p.name)).hexdigest()==sha(p) for p in files)
assert all(sha(P/n)==h for n,h in frozen.items())
print(json.dumps({'archive':str(archive),'bytes':archive.stat().st_size,'sha256':sha(archive),'indexedPayloadFiles':len(index),'ZIPMembers':len(files),'indexSHA256':sha(P/'source-files.sha256.json'),'finalSealSHA256':sha(P/'FINAL-SEAL-RECEIPT.json'),'frozen40Unchanged':True}))
