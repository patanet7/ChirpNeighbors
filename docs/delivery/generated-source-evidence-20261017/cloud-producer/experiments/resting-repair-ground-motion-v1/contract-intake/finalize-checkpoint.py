"""Finalize bounded evidence only. Never invokes codec, writes producer files, or admits source."""
import pathlib,json,hashlib,re,datetime
from PIL import Image
O=pathlib.Path(__file__).resolve().parent;B=O.parent;R=B/'flight-tech-repair'
sha=lambda b:hashlib.sha256(b).hexdigest()
def dump(p,d):p.write_text(json.dumps(d,indent=2)+'\n')
def rgba(p):return Image.open(p).convert('RGBA')
h=json.loads((R/'airborne-source-handoff.json').read_text());proof=[];union=set()
for f in h['frames']:
 old=rgba(R/f['original96PNG']);raw=rgba(R/f['raw64PNG']);final=rgba(R/f['png']);assert old.size==(96,96) and raw.size==final.size==(64,64)
 expected=bytes(v for y in range(64) for x in range(64) for v in old.getpixel(((2*x+1)*96//128,(2*y+1)*96//128)))
 assert raw.tobytes()==expected
 rp=list(raw.getdata());fp=list(final.getdata());assert all(q[3]==(255 if p[3]>=128 else 0) for p,q in zip(rp,fp));assert all(q==(0,0,0,0) for q in fp if q[3]==0)
 union.update(fp);assert f['pivot']==[36,45] and f['density']==1 and f['contacts']==[]
 baseline=B/'flight-art/frames96'/pathlib.Path(f['original96PNG']).name;assert baseline.read_bytes()==(R/f['original96PNG']).read_bytes()
 proof.append({'sourceFrameID':f['sourceFrameID'],'raw96PNGsha256':sha((R/f['original96PNG']).read_bytes()),'raw64PNGsha256':sha((R/f['raw64PNG']).read_bytes()),'finalPNGsha256':sha((R/f['png']).read_bytes()),'exactScalarWholeCanvasNearestSample':True,'exactThresholdMask':True,'transparentRGBZero':True,'oldBaseline96BytesExact':True,'newDrawings':0})
assert len(union)<=64
ledgerChecks=[];seen=set()
for p in sorted((O/'configs').glob('*.json')):
 c=json.loads(p.read_text());e=c.get('freezeLedger',{});root=pathlib.Path(c['candidateRoot']);key=(str(root),e.get('file'),e.get('sha256'))
 if not e.get('sha256') or key in seen:continue
 seen.add(key);lp=root/e['file'];assert sha(lp.read_bytes())==e['sha256'];d=json.loads(lp.read_text());entries=d.get('files',d) if isinstance(d,dict) else d
 pairs=[(f.get('file',f.get('path')),f.get('sha256',f.get('SHA256'))) for f in entries] if isinstance(entries,list) else list(entries.items())
 for n,s in pairs:
  if isinstance(s,dict):s=s.get('sha256',s.get('SHA256'))
  pp=(root/n).resolve();assert pp.is_relative_to(root.resolve());assert sha(pp.read_bytes())==s,(root,n)
 ledgerChecks.append({'candidateRoot':str(root.relative_to(B)),'ledger':e['file'],'ledgerSHA256':e['sha256'],'filesVerified':len(pairs),'allExact':True})
dump(O/'flight-tech-independent-receipt.json',{'scope':'Independent fixed-transform/pixel/JSON subset only; no source art or runtime admission','frames':proof,'finalRGBAColorUnionIncludingTransparent':len(union),'sameWholeCanvas96to64SampleAllFour':True,'alphaThreshold':128,'perPoseFittingOrShift':False,'sourcePivotWorld':[36,68/1.5],'proposedIntegerPivot':[36,45],'roundingDeltaWorld':[0,45-68/1.5],'originMeaning':'Image registration only; airborne torso origin is not foot support','contacts':[],'geometryReviewed':False,'supportWorld':None,'sourceAdmitted':False,'runtimeAdmission':False,'newCalls':0,'newDrawings':0,'actualPixelReceipt':'receipts/anna-flight-tech-four64-v1/pixel-receipt.json','actualJSONReceipt':'receipts/anna-flight-tech-four64-v1/official-checks.json','commonInput5':'NOT APPLICABLE to airborne source subset; no idle/blink/look family fabricated','full13FlightAdmission':False,'oldFailureReceiptsRetained':True})
dump(O/'FINAL-FROZEN-GUARDS.json',{'state':'PASS all reviewed producer ledger bytes remain exact','ledgers':ledgerChecks,'uniqueFrozenLedgers':len(ledgerChecks),'totalLedgerEntriesVerified':sum(x['filesVerified'] for x in ledgerChecks),'extraMetadataAliasesOutsideOriginalLedgers':4,'sourcePixelsModifiedByThisWorkstream':False,'codecRerunsDuringFinalization':0})
rows=[]
for p in sorted((O/'receipts').iterdir()):
 if not p.is_dir():continue
 r={'candidateId':p.name,'sourceAdmitted':False,'runtimeAdmission':False}
 j=p/'official-checks.json'
 if j.exists():
  d=json.loads(j.read_text());r.update(JSON=d.get('rawCandidateBudget'),producerProposalShapePass=d.get('proposal',{}).get('shapePass'),input5ClassificationCounts=d.get('input5Diagnostic',{}).get('classificationCounts'),fullGraphRefinementsValidated=False)
 else:r['JSON']=json.loads((p/'actual-json-receipt.json').read_text())
 if (p/'pixel-receipt.json').exists():
  d=json.loads((p/'pixel-receipt.json').read_text());r.update(pixelStatus=d['status'],rectangles=d['totalRectangles'],decodedArea=d['decodedArea'],producerPixelReceiptReused=(p/'producer-pixel-receipt-verification.json').exists())
 elif (p/'actual-pixel-subset.stderr.txt').exists():
  t=(p/'actual-pixel-subset.stderr.txt').read_text();m=re.search(r'PermanentStageError: ([^\r\n]+)',t);r.update(pixelStatus='FAIL actual normalizer',pixelFailure=m.group(1) if m else 'See exact retained failure log')
 else:r['pixelStatus']='NOT APPLICABLE source facts only'
 rows.append(r)
assert len(rows)==16
dump(O/'CHECKPOINT-RESULTS.json',{'scope':'Bounded source pixel/JSON and metadata checks; no art usefulness or admission promotion','completed':rows,'sourceAdmitted':False,'runtimeAdmission':False})
status=json.loads((O/'STATUS.json').read_text());status.update(state='FINAL GO for parent source-only sealing; all assigned bounded checks completed',checksRunning=0,completedCandidateChecks=len(rows),completed=rows,pending=[],remainingBlockers=['Importer-owned output-use declarations, real runtime reference bindings and approved projectGeneratedEvidence pin are unavailable here; official input5 remains incomplete.','Full graph refinements and actual runtime admission have not executed.','Historical Crow awake generation receipt and Anna A-wing image input enumeration remain unresolved in actual collector facts.','Native bridge composite conditioning guide has exact component proof but no supported collector composition adapter; held source study only.','Original Crow63 and authorized Crow32 rectangle failures, Quail gait/full13 area+JSON failures, and legacy flight/bridge alpha failures remain retained; no further retries authorized.'],sourceAdmitted=False,runtimeAdmission=False)
dump(O/'STATUS.json',status)
print(json.dumps({'completedCandidateChecks':len(rows),'uniqueFrozenLedgers':len(ledgerChecks),'producerLedgerEntriesExact':sum(x['filesVerified'] for x in ledgerChecks),'flightTechColors':len(union),'pixelPasses':sum(x['pixelStatus'].startswith('PASS') for x in rows),'pixelFailures':sum(x['pixelStatus'].startswith('FAIL') for x in rows),'factsOnly':sum(x['pixelStatus'].startswith('NOT') for x in rows),'checksRunning':0}))
