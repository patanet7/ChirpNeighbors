from pathlib import Path
from PIL import Image
import numpy as np, json, hashlib, datetime
P=Path(__file__).resolve().parent.parent
R=P.parent.parent
O=R/'experiments/resting-repair-ground-motion-v1/attention-repairs/american_crow'
S=R/'audits/crow-ground-runtime-compatible-v1/palette-variants/crow-ground-idle186-total12.png'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def put(name,v): (P/name).write_text(json.dumps(v,indent=2)+'\n')
assert not (P/'PREREGISTRATION.json').exists(), 'One preregistration only'
h=json.loads((O/'source-handoff.json').read_text())
a=np.array(Image.open(S).convert('RGBA'))
palette=np.unique(a[a[:,:,3]>0,:3],axis=0).tolist()
assert len(palette)==11 and sha(S)=='6832bffeb9a2a2dd871be0ca1315e29b184459ff535a4539001a9d73bda81a91'
sources=[]
for f in h['frames']:
 p=O/f['rawPNG']; assert sha(p)==f['rawPNGsha256']
 b=np.array(Image.open(p).convert('RGBA'));m=b[:,:,3]>=128; y,x=np.where(m)
 sources.append({'id':f['id'],'sourceFrameId':f['sourceFrameId'],'nativePNG':str((O/f['sourcePNG']).relative_to(R)), 'nativePNGsha256':sha(O/f['sourcePNG']),
  'rawPNG':str(p.relative_to(R)),'rawPNGsha256':sha(p),'rawCanvas':[b.shape[1],b.shape[0]],'binaryAlphaMaskSHA256':hashlib.sha256((m.astype(np.uint8)*255).tobytes()).hexdigest(),
  'thresholdBBox':[int(x.min()),int(y.min()),int(x.max()+1),int(y.max()+1)],'thresholdPixels':len(x)})
guards=[]
for q in [O,O.parent/'american_crow-palette32']:
 ledger=q/'review-target-hashes.json'; rows=json.loads(ledger.read_text())['files']
 assert all(sha(q/f['path'])==f['SHA256'] for f in rows)
 guards.append({'directory':str(q.relative_to(R)), 'ledger':str(ledger.relative_to(R)),'ledgerSHA256':sha(ledger),'count':len(rows)})
evidence=[str(O.relative_to(R))+'/source-handoff.json','recovery/stage70/candidate-discovery-qualification-addendum.json','recovery/stage70/common-resting-qualification.json','recovery/stage70/priority-qualification.json','recovery/stage70/priority-qualification-correction.json','experiments/resting-repair-ground-motion-v1/contract-intake/receipts/american_crow-repair-v1/CHECK-SUMMARY.json','experiments/resting-repair-ground-motion-v1/contract-intake/receipts/american-crow-palette32-v1/CHECK-SUMMARY.json','audits/crow-ground-runtime-compatible-v1/palette-variants/actual-codec-evaluation.json','validation/sprite-inspection.py']
put('PREFLIGHT.json',{'kind':'Measured backlog repair selection; no grading catalog invented','nativeCalls':0,'newDrawings':0,'reportsInspected':{'packetQualifications':133,'priorityCandidates':14,'commonQuestions':60,'derivedSourceUseful':54,'historicalRESTSourceUseful':53},
 'selected':'One deterministic Crow family projection onto existing selected-ground 11 opaque RGB palette',
 'comparison':[{'candidate':'Crow quiet ground attention','existingArt':'Independent quiet head attention useful','knownDefect':'63-color rectangles5196/5198/5178;32-color4982/4964/4917; limit4096 per frame','boundedAction':'Use one exact existing palette, not another quantizer/search; zero new source drawings','risk':'Reduced eye/feather/toe shading or still over budget'},
 {'candidate':'Hooded Oriole blink','existingArt':'Genuine eyelid variants and technical clock pass, ambiguous at141CSS/100ms','reasonNotSelected':'A same-ROI copy cannot add missing semantic cue. Another source attempt has less certain improvement and repeats the recently held Bushtit problem.'},
 {'candidate':'House Finch hop','existingArt':'Four real pose keys; matched hop held','reasonNotSelected':'Oldwidth49 vs normalized72–74; density hypothesis43–45 but settled toe row67 vs old74. A palette operation cannot repair support/phase registration; metadata anchors could disguise a jump and need separate transition/art proof.'}],
 'groundNeutralSafety':{'asset':str(S.relative_to(R)),'PNGsha256':sha(S),'mustRemainByteExact':True,'historicalStaticRectangles':4021,'repairNeutralMaskXorPixels':int(np.count_nonzero((a[:,:,3]>0)^(np.array(Image.open(O/'raw-full/neutral.png'))[:,:,3]>=128))), 'historicalPassTransfersToNewFamily':False,'reason':'Static safe source was192→186 NN; repair raw family uses direct whole-native legacy-world pixel-center sampling. Different samplers/masks; no registration repair or active profile write authorized.'},
 'canonicalDefectId':None,'evaluationContractPin':None,'canonicalLabelsStatus':'PENDING_SHARED_CONTRACT',
 'sharedContractSearch':{'localRepositories':['chirp-finch-preen-canon','chirp-cloud-source-canon','ChirpNeighbors','runtime-resting-intake-v5-inspect'],'observedImplementation':'No shared sprite grading schema/catalog located by grading/defect/evaluation/taxonomy filename scans. Audio evaluation is unrelated. Parent independently confirmed origin/main e040fc4 has no matching schema or remote grading branch. This is an observation of available snapshots, not proof no work exists elsewhere.','coordination':'Parent/spec-owner relay required; no outbound cloud-thread sender available to root.'},
 'measurementMappingRequest':[{'existingLocalKeys':keys,'canonicalDefectId':None,'requiredSharedDefinition':meaning,'automaticArtApproval':False} for keys,meaning in [
 (['alphaBBox','thresholdBBox','edgeTouchPixels'],'Region/frame clipping observation; distinguish edge-touch proxy from confirmed missing anatomy'),
 (['partialAlphaPixels','opaqueRGBCount','visibleRGBCountAtAlphaCutoff','codec'],'Representation prerequisites and exact hash-bound codec error; no rectangle count inferred from palette size'),
 (['stableRegion.residualWorld','contactROIProxies.baselineDeltaWorldFromFirst'],'Intent-conditioned image registration, mask/ROI scope, grounded versus airborne context; never sole pressure'),
 (['paletteDriftFromFirst','brightLowChromaBoundaryPixelsProxy','tinyComponentsLE2'],'Raster texture proxies with explicit cutoff/scope; subjective defect interpretation remains separate'),
 (['actionCoverage','expectedRootWorld','projectedCentroidAtDeclaredRootWorld'],'Declared action/trajectory evidence versus genuine pose semantics and runtime adoption')]],
 'sharedSeamRequired':['version+SHA256 of actual schema and defect catalog','existing IDs and exact definitions, permitted action/species/support contexts','measured/inferred/unknown evidence fields','independent nullable confidence/severity rules','repairDecision and reevaluation source/report hash links'],
 'mappingConsumerExamples':[{'candidate':'Crow attention','measurement':'actual per-frame rectangle cap exceeded','existingRuntimeError':'Normalized rectangle budget exceeded','canonicalDefectId':None,'reason':'A runtime error string is not a verified shared defect ID'}, {'candidate':'Oriole blink','measurement':'100ms clock passes, normal-size lid meaning held by reviewers','canonicalDefectId':None,'reason':'A timing pass must not become eye-readability approval'}, {'candidate':'Finch hop','measurement':'settle foot-image baseline7world above old reference under density hypothesis','canonicalDefectId':None,'reason':'Image baseline is not a physical contact verdict'}],
 'evidence':[{'file':p,'sha256':sha(R/p)} for p in evidence],'executedBeforeDecision':{'generations':0,'exports':0,'codecRuns':0},'ownerSelection':'Root subsequently authorized this single zero-native projection; no other repair selected'})
put('PREREGISTRATION.json',{'schemaVersion':1,'batchId':P.name,'createdUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'authorizer':'Parent root explicit single projection approval after measured backlog preflight',
 'nativeCalls':0,'newDrawings':0,'reusedDrawings':3,'exportPassLimit':1,'paletteVariants':1,'quantizerTrainingRuns':0,'paletteSource':{'file':str(S.relative_to(R)),'sha256':sha(S),'opaqueRGB':palette,'maximumOpaque':11,'maximumTotal':12},
 'sourceFrames':sources,'geometry':{k:h[k] for k in ['fullWorldCanvas','displayStage','candidateCanvas','density','oldPivotWorld','roundedFullPivot','commonCropOrigin','candidatePivot','crop']},'clips':h['clips'],
 'recipe':'Use exact retained raw186 RGBA. Preserve existing alpha>=128 mask; surviving alpha255, transparentRGBA0. Map surviving RGB to nearest squared-Euclidean RGB among the fixed11 values, ties lexicographic ascending. No dithering, new quantizer, resize, translation, body/head cutout, fit, warp, painting or contact snap. Same zero-discard common crop.',
 'knownLoss':'Lossy RGB-only packaging; current raw partial-alpha and high-resolution originals retained unchanged. Prior alpha cleanup is disclosed, not newly approved.',
 'stopConditions':['One source export only; no palette ladder or new native call','Retain any actual codec/JSON failure; no fallback export','Fresh independent normal186 light/dark review required even if representation passes','Hold eye/head readability loss, distracting foot/texture phase pop, anatomy/registration failure; no subjective auto pass'],
 'checkerNomination':{'repo':'/workspace/runtime-resting-intake-v5-inspect','commit':'c4ae7529786e28cf55e2008b7f7b64215fc6542c','runner':'validation/shared-structural-check.mjs','runnerSHA256':'5317b37dbd7229f7e0cf62302f70ad526890c99b56b2c0704b441cebfcb141e7','packageSHA256':'b936301983382339392ffdb5cba9f36af1018f9a55513c44bbbee81c36080088','canonicalErrorSHA256':'28c4c5f7bd522ac9709ce66df07c674e9f9a5ec53d35255c4a0ebfdef4637320','currentMacAdmission':False},
 'frozenPriorGuards':guards,'safeGroundGuard':{'file':str(S.relative_to(R)),'sha256':sha(S)},'geometryReviewed':False,'contacts':[],'supportWorld':None,'runtimeAdmission':False,'canonicalDefectId':None,'evaluationContractPin':None,'canonicalLabelsStatus':'PENDING_SHARED_CONTRACT'})
print(json.dumps({'preregistrationSHA256':sha(P/'PREREGISTRATION.json'),'preflightSHA256':sha(P/'PREFLIGHT.json'),'opaquePalette':palette,'oldFrozenCounts':[g['count'] for g in guards]}))
