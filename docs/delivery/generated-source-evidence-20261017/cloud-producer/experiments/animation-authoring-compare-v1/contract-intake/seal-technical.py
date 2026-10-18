"""Seal bounded comparison evidence only. No checks rerun and no producer/global writes."""
import pathlib,json,hashlib,re,datetime
from PIL import Image
O=pathlib.Path(__file__).resolve().parent;E=O.parent;sha=lambda b:hashlib.sha256(b).hexdigest()
def load(p):return json.loads(p.read_text())
def dump(p,d):p.write_text(json.dumps(d,indent=2)+'\n')
base=load(O/'COMPARISON.json');dp=load(O/'arm-d/pixel-receipt.json');dc=load(O/'arm-d/CONSTRUCTION-RECEIPT.json');dj=load(O/'arm-d/json-budget-receipt.json');dr=E/'arm-d-hybrid-construction';dh=load(dr/'source-handoff.json');de=load(dr/'export-receipt.json')
neutral=Image.open(dr/'full-stage/neutral.png').convert('RGBA');look=Image.open(dr/'full-stage/look.png').convert('RGBA');footdiff=sum(neutral.getpixel((x,y))!=look.getpixel((x,y)) for y in range(86,103) for x in range(59,88));assert footdiff==0
Dpalette=set(neutral.getdata())|set(look.getdata());Apalette={tuple(p)+(255,) for p in load(O/'arm-a/METRICS.json')['paletteRGB']}|{(0,0,0,0)};assert Dpalette==Apalette;assert (dr/'frames/neutral.png').read_bytes()==(E/'arm-a-baseline/frames/neutral.png').read_bytes()
rows=[]
for arm in ['A','C']:
 m=base['arms'][arm];p=load(O/('arm-'+arm.lower())/'pixel-receipt.json');rows.append({'arm':arm,'method':m['method'],'currentNativeCalls':m['callsForThisExperiment'],'newNativeDrawings':m['newDrawingsForThisExperiment'],'uniqueTestedRenderFrames':3,'containsActualBlink':True,'canvas':m['canvas'],'density':m['density'],'pixelStatus':m['pixelStatus'],'rectangles':m['rectangles'],'decodedArea':m['decodedArea'],'attentionPairRectangleSumFromActualPerFrameResults':sum([p['perFrameRectangles'][0],p['perFrameRectangles'][2]]),'attentionPairAreaArithmetic':m['canvas'][0]*m['canvas'][1]*2,'attentionPairIsAdditionalCodecRun':False,'canonicalRawJSONBytes':m['JSON'][0]['canonicalUTF8Bytes'],'JSONFrameCount':3,'lookVsNeutralFullWorld':m['lookVsNeutralFullWorld'],'contacts':[],'physicalSupportReviewed':False,'runtimeAdmission':False})
rows.append({'arm':'D','method':'Explicit visible-head source-pixel replacement; neutral body protected, authored head donor','currentNativeCalls':0,'newNativeDrawings':0,'uniqueTestedRenderFrames':2,'containsActualBlink':False,'canvas':[61,45],'density':1,'pixelStatus':dp['status'],'rectangles':dp['totalRectangles'],'decodedArea':dp['decodedArea'],'attentionPairRectangleSumFromActualPerFrameResults':dp['totalRectangles'],'attentionPairAreaArithmetic':dp['decodedArea'],'attentionPairIsAdditionalCodecRun':False,'canonicalRawJSONBytes':dj['results'][0]['canonicalUTF8Bytes'],'JSONFrameCount':2,'lookVsNeutralFullWorld':{'RGBAChangedPixels':dc['headChangedPixels'],'alphaChangedPixels':dc['oldHeadBillPixelsClearedByActualDonorTransparency']+dc['donorSilhouettePixelsAdded'],'fixedFootROIChangedPixels':footdiff,'scope':'Fixed image region only; exact protected pixels do not establish physical planting'},'protectedVisibleCanonicalPixels':dc['protectedVisibleCanonicalPixels'],'protectedRGBAChangedPixels':dc['protectedRGBAChangedPixels'],'canonicalAPaletteExact':True,'canonicalANeutralPNGBytesExact':True,'contacts':[],'physicalSupportReviewed':False,'runtimeAdmission':False})
be=load(O/'BE-FEASIBILITY-CONSUMPTION.json');effort=load(O/'OBSERVED-EFFORT.json');effort['D']={'source':'../arm-d-hybrid-construction/export-receipt.json','sha256':sha((dr/'export-receipt.json').read_bytes()),'nativeCalls':0,'singleExportObservedSeconds':de['observedOneExportWallSeconds'],'manualHumanCleanupMinutes':de['humanCleanupMinutes'],'humanMaskDesignTimeSeconds':None,'paintingOrHiddenUnderfillPerformed':False,'qualification':'One mask authored after inspection; unmeasured inspection/design labor cannot be inferred from exporter walltime.'}
dump(O/'FINAL-OBSERVED-EFFORT.json',effort)
guards=[]
for arm in ['a','c','d']:
 cfg=load(O/('arm-'+arm+'-config.json'));r=pathlib.Path(cfg['root']);ld=load(r/cfg['ledger']['file']);items=ld.get('files',ld) if isinstance(ld,dict) else ld;pairs=[(x.get('file',x.get('path')),x.get('sha256',x.get('SHA256'))) for x in items] if isinstance(items,list) else list(items.items())
 for n,s in pairs:
  if isinstance(s,dict):s=s.get('sha256',s.get('SHA256'))
  assert sha((r/n).read_bytes())==s,n
 assert sha((r/cfg['handoff']['file']).read_bytes())==cfg['handoff']['sha256'];assert sha((r/cfg['stableGO']['file']).read_bytes())==cfg['stableGO']['sha256'];guards.append({'arm':arm.upper(),'ledgerSHA256':cfg['ledger']['sha256'],'producerGOsha256':cfg['stableGO']['sha256'],'filesExact':len(pairs),'sourceModified':False})
b=E/'arm-b-rig-feasibility';bi=load(b/'artifact-index.json')
for f in bi['files']:assert sha((b/f['file']).read_bytes())==f['sha256']
guards.append({'arm':'B and E evidence','ledgerSHA256':sha((b/'artifact-index.json').read_bytes()),'producerGOsha256':sha((b/'STABLE-GO.json').read_bytes()),'filesExact':len(bi['files']),'sourceModified':False})
# A/C intermediate snapshot remains exact; final summary does not overwrite it.
ac=load(O/'AC-CHECKPOINT.json')
for n,s in ac['files'].items():assert sha((O/n).read_bytes())==s,n
report={'experiment':'ANIM-AUTHORING-COMPARE-1','state':'BOUNDED TECHNICAL COMPARISON COMPLETE','runtimeCommit':'c4ae7529786e28cf55e2008b7f7b64215fc6542c','tested':rows,'untested':{'B':be['B'],'E':be['E']},'commonProtocol':load(O/'protocol.json'),'sourcePreservation':guards,'totalFrozenProducerFilesExact':sum(r['filesExact'] for r in guards),'nativeGenerationCallsByTechnicalWorkstream':0,'newNativeCallsInExperimentAsObserved':1,'newNativeDrawingsInExperimentAsObserved':1,'DRenderConstructionIsNotNewDrawing':True,'familyCompleteness':{'A':'3-frame actual neutral/blink/look','C':'3-frame actual neutral/blink/look','D':'2-frame attention-only derivative; no blink or full common family'},'comparisonQualification':['A/C full-family totals include blink, whereas D has two attention frames. Per-attention rectangle/area values are arithmetic selections from actual per-frame results, not extra runs.','A/C both use native pose art; copying A did not test a parts rig. D is an explicit head-pixel construction using genuine authored head art.','D exactly protects canonical body/feet pixels; this cannot certify a natural neck join, silhouette, lighting, or physical foot contact.','C raw reused neutral/blink bytes equal A, while its recomputed palette and larger common crop are explicit comparison differences.','No source-quality winner or authoring speed advantage can be inferred without independent normal-size appearance/geometry reviews and comparable human-effort measurements.'],'unresolved':['Independent art, seam, temporal and semantic-contact verdicts are separate from these technical metrics.','Full importer private provenance, rights/reference/fidelity recovery, input5 packaging and actual runtime admission were not executed.','New C native source remains proposed until root registration; no bank/queue/runtime or publication mutation by this workstream.'],'sourceAdmitted':False,'runtimeAdmission':False,'nextActualCheckQueued':None,'checksRunning':0}
dump(O/'FINAL-COMPARISON.json',report)
p=O/'READINESS.json';d=load(p);d.update(state='FINAL bounded technical checks complete; ready for parent enclosing source-only seal',completedArms=['A','C','D'],pending=[],actualChecksRunning=0,sourceAdmitted=False,runtimeAdmission=False);dump(p,d)
md='''The technical comparison is complete on the exact UI22 snapshot. A, C and D passed the unchanged pixel normalizer and actual canonical JSON checks, with exact source hashes and RGBA reconstruction. B and E remain untested; no compatible ready-made Sparrow rig/parts implementation or simple 3D bird model/weights/camera/render pipeline was executed. D is credited separately as a new explicit layered construction, not retroactively as a B rig success.

| Arm | Tested frames | Canvas | Rectangles | Decoded area | Raw JSON bytes |
| --- | ---: | --- | ---: | ---: | ---: |
| A: existing native baseline | 3 | 61 × 45 | 2,205 | 8,235 | 83,301 |
| C: one native edit | 3 | 64 × 52 | 2,337 | 9,984 | 98,452 |
| D: visible-head construction | 2 | 61 × 45 | 1,456 | 5,490 | 55,370 |

A and C include neutral, genuine closure and look. D contains only neutral and look, so the full totals have different frame counts. Selecting actual neutral/look rectangle results gives A 1,480 and C 1,623; D's actual pair is 1,456. These are budget facts, not quality rankings or additional codec runs.

All arms retain the same world scale, density, full root and authored attention clock of 60/18/12 ticks at 30 Hz. C expands one common transparent-only crop and recomputes the shared palette. Its reused native and raw neutral/blink source pixels stay exact, while final palette colors can differ. Its fixed image foot-region changes exceed A's; that region is not a semantic sole model.

D's canonical A palette and neutral PNG bytes are exact. Its declared 375-pixel mask, protected complement, source layers and same-coordinate donor map reconstruct exactly. The 15,001 protected full-stage pixels include 656 visible canonical body/feet pixels, with zero changes. The donor changes 168 head pixels, clears 26 old head/bill pixels using actual donor transparency and adds 9 silhouette pixels. Both neutral and hybrid retain the same 24 enclosed transparent pixels. None of these counts certifies a natural seam, anatomical neck, grounded feet or normal-size artistic acceptance.

Source effort is not directly comparable: A copies existing work whose original authoring/export labor is unknown; C records a 50.4-second tool duration and 0.118-second export; D records a 0.152-second export but unmeasured mask design/inspection labor. These measurements do not establish an authoring-efficiency winner. Exact scopes and hashes are retained in FINAL-OBSERVED-EFFORT.json.

All 151 frozen producer files across A, B, C and D remain exact. This technical workstream made zero native calls and no source, bank, queue, runtime or publication edits. The experiment observed one newly generated C drawing; D derivatives introduce no native identities. Enclosing registration and publication remain parent-owned.

Full input5 packaging, private rights/reference/fidelity recovery and actual runtime admission were not attempted. Engine-compatible pixel/JSON subsets remain separate from independent art/geometry decisions and runtime acceptance. The original A/C checkpoint remains unchanged, and all commands, outputs, source-index snapshots and actual receipts are retained here.
'''
(O/'FINAL-REPORT.md').write_text(md)
# Only bounded public checks, no matched secret/capture contents retained.
patterns={'privateLibraryHandle':re.compile(r'libfile_[A-Za-z0-9]{8,}'),'embeddedImageBase64':re.compile(r'data:image/[^\s\"\']*;base64,'),'signedURL':re.compile(r'https?://[^\s\"\']*[?&](?:X-Amz-Signature|sig|token)=',re.I)}
hits=[]
for p in O.rglob('*'):
 if not p.is_file():continue
 try:t=p.read_text()
 except UnicodeDecodeError:continue
 for name,pat in patterns.items():
  if pat.search(t):hits.append({'file':str(p.relative_to(O)),'category':name})
assert not hits,hits
dump(O/'PUBLIC-SAFETY-SCAN.json',{'status':'PASS bounded UTF8 scan','privateLibraryHandles':0,'embeddedImageBase64':0,'signedURLs':0,'privateRuntimeBindingRecoveryExecuted':False})
files={str(p.relative_to(O)):sha(p.read_bytes()) for p in sorted(O.rglob('*')) if p.is_file() and p.name not in ['FINAL-FILES.sha256.json','STABLE-GO.json']};dump(O/'FINAL-FILES.sha256.json',files)
go={'experiment':'ANIM-AUTHORING-COMPARE-1','state':'FROZEN bounded technical comparison; parent enclosing seal owns publication','index':'FINAL-FILES.sha256.json','indexSHA256':sha((O/'FINAL-FILES.sha256.json').read_bytes()),'indexedFiles':len(files),'testedArms':['A','C','D'],'untestedArms':['B','E'],'actualPixelChecks':3,'actualJSONChecks':3,'checksRunning':0,'sourceGenerationCallsByTechnicalWorkstream':0,'newNativeDrawingsByTechnicalWorkstream':0,'frozenProducerFilesExact':151,'finalComparisonSHA256':sha((O/'FINAL-COMPARISON.json').read_bytes()),'finalReportSHA256':sha((O/'FINAL-REPORT.md').read_bytes()),'sourceAdmitted':False,'runtimeAdmission':False,'noFurtherTechnicalWritesPlanned':True};dump(O/'STABLE-GO.json',go);print(json.dumps({'GOSHA256':sha((O/'STABLE-GO.json').read_bytes()),'indexSHA256':go['indexSHA256'],'indexedFiles':len(files),'finalComparisonSHA256':go['finalComparisonSHA256'],'finalReportSHA256':go['finalReportSHA256']},indent=2))
