"""Retain actual native drawings and expose registration as a separate diagnostic."""
from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib
R=Path(__file__).parent;P=R/'batches/house-finch-female-preen-v1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def fid(im):return 'frame.sha256.'+hashlib.sha256(f'RGBA8;{im.width}x{im.height};'.encode()+im.tobytes()).hexdigest()
def metrics(im):
 a=np.array(im);mask=a[:,:,3]>=128;y,x=np.nonzero(mask);ground=int(y.max());low=mask&(np.indices(mask.shape)[0]>=ground-28);fy,fx=np.nonzero(low);root=int(np.median(fx));split=float(np.median(fx));feet=[]
 for test in [fx<=split,fx>split]:feet.append([float(np.median(fx[test])),int(fy[test].max())])
 return {'bboxAlpha128':[int(x.min()),int(y.min()),int(x.max()+1),ground+1],'rootHeuristic':[root,ground],'feetHeuristic':feet,'mask':mask,'alphaZeroPixels':int((a[:,:,3]==0).sum()),'alphaPartialPixels':int(((a[:,:,3]>0)&(a[:,:,3]<255)).sum()),'borderAlpha128':int(mask[0].sum()+mask[-1].sum()+mask[:,0].sum()+mask[:,-1].sum())}
def public(m):return {k:v for k,v in m.items() if k!='mask'}
original=Image.open(P/'original.png').convert('RGBA');assert original.size==(1536,1024)
plan=json.loads((P/'production-plan.json').read_text());bank=json.loads((R/'frame-bank.json').read_text());prior_ids={f['frameId'] for f in bank['frames']}
ref=Image.open(R/plan['referenceFile']).convert('RGBA');refhalf=ref.resize((512,512),Image.Resampling.NEAREST);refm=metrics(refhalf)
raw=[];registered=[];rawmetrics=[];regmetrics=[];records=[];entries=[]
for name in ['frames-native512','frames-registered1024','frames-review384']:(P/name).mkdir(exist_ok=True)
for i,phase in enumerate(plan['phases']):
 cell=original.crop(((i%3)*512,(i//3)*512,(i%3+1)*512,(i//3+1)*512));frame_id=fid(cell);assert frame_id not in prior_ids
 native=P/'frames-native512'/f'{i:02d}.png';cell.save(native);raw.append(cell);rawmetrics.append(metrics(cell))
 # ONE common factor for all poses. It is technical scale registration, not
 # newly generated geometry or evidence that the model obeyed the template.
 scaled=cell.resize((572,572),Image.Resampling.NEAREST);m=metrics(scaled);dx=512-m['rootHeuristic'][0];dy=800-m['rootHeuristic'][1];out=Image.new('RGBA',(1024,1024));out.paste(scaled,(dx,dy));registered.append(out);out.save(P/'frames-registered1024'/f'{i:02d}.png');review=out.resize((384,384),Image.Resampling.NEAREST);review.save(P/'frames-review384'/f'{i:02d}.png');regmetrics.append(metrics(out))
 rec={'frameId':frame_id,'file':str(native.relative_to(R)),'fileSha256':sha(native),'pixelIdentity':'SHA256 of RGBA8;WxH; plus decoded bytes','dimensions':[512,512],'species':'house_finch','variant':'adult-female','appearanceVersion':'house-finch-canon-v1','poseTags':[phase,'preening','right-facing-body'],'sourceAtlas':str((P/'original.png').relative_to(R)),'sourceAtlasSha256':sha(P/'original.png'),'sourceRect':[(i%3)*512,(i//3)*512,512,512],'derivation':{'method':'exact fixed native512 cell crop; no translation, alpha cleanup, repaint or resampling in immutable source frame','copiedPixelsExact':True},'supportRoot':None,'feetContactsApprox':rawmetrics[-1]['feetHeuristic'],'contactAnnotationMethod':'alpha>=128 lower28-pixel split heuristic; not anatomical tracking','beakAnchorApprox':None,'scaleCalibrationRef':'scale.house_finch','anatomyScaleAccepted':False,'rootContactAccepted':False,'technicalSourcePixelCopyExact':True,'acceptedUses':[],'rejectedUses':[],'candidateUses':['preening-source-reference'],'sourcePrompt':str((P/'prompt.txt').relative_to(R)),'generator':'OpenAI image_gen.imagegen','model':None,'seed':None}
 records.append(rec);entries.append({'frameId':frame_id,'durationMs':plan['durationMs'][i],'phase':phase,'feetContactState':'both-planted-requested-unverified','billFeatherContact':'visible-candidate' if i in [0,1,2,3] else 'release-or-neutral','contactVerified':False,'sourceToDiagnostic':{'commonUniformScale':572/512,'integerTranslation':[dx,dy],'sourceFrameCanvas':[512,512],'diagnosticCanvas':[1024,1024],'registrationMethod':'lower-alpha foot heuristic; documented per-frame placement correction; no anatomical part warp','file':f'frames-registered1024/{i:02d}.png','sha256':sha(P/'frames-registered1024'/f'{i:02d}.png')},'reviewPNG':f'frames-review384/{i:02d}.png','reviewSha256':sha(P/'frames-review384'/f'{i:02d}.png')})
def saveclip(frames,durations,stem):
 frames[0].save(P/(stem+'.apng'),save_all=True,append_images=frames[1:],duration=durations,loop=0,disposal=0,blend=0)
 gifs=[]
 for f in frames:
  rev=f.resize((384,384),Image.Resampling.NEAREST);bg=Image.new('RGBA',rev.size,(239,235,213,255));bg.alpha_composite(rev);gifs.append(bg.convert('RGB'))
 gifs[0].save(P/(stem+'.gif'),save_all=True,append_images=gifs[1:],duration=durations,loop=0,disposal=2,optimize=False)
 return gifs
rawpreviews=saveclip(raw,plan['durationMs'],'raw-cell-preview')
diagnostic_frames=[ref]+registered+[ref];durations=[800]+plan['durationMs']+[600];previews=saveclip(diagnostic_frames,durations,'preview')
sheet=Image.new('RGB',(1536,820),(239,235,213));d=ImageDraw.Draw(sheet)
labels=['existing neutral']+plan['phases']+['existing neutral']
for i,im in enumerate(previews):sheet.paste(im,((i%4)*384,(i//4)*410));d.text(((i%4)*384+8,(i//4)*410+390),f'{i} {labels[i]} {durations[i]}ms',fill=(30,40,35))
sheet.save(P/'contact-sheet.png')
def iou(a,b):return float((a&b).sum()/max(1,(a|b).sum()))
raw_widths=[m['bboxAlpha128'][2]-m['bboxAlpha128'][0] for m in rawmetrics];rw=refm['bboxAlpha128'][2]-refm['bboxAlpha128'][0]
ref_full=metrics(ref);feet=np.array([m['feetHeuristic'] for m in regmetrics]);ref_feet=np.array(ref_full['feetHeuristic']);drift=float(np.linalg.norm(feet-ref_feet,axis=2).max());newdrift=float(np.linalg.norm(feet-feet[0],axis=2).max())
rawseam=iou(rawmetrics[-1]['mask'],refm['mask']);regseam=iou(regmetrics[-1]['mask'],ref_full['mask'])
# Fixed torso/wing band in the registered source comparison; head angle is
# excluded so genuine head motion is not automatically called body-scale drift.
band=[]
for out in registered:
 mask=(np.array(out)[:,:,3]>=128)[600:720];yy,xx=np.nonzero(mask);band.append(int(xx.max()-xx.min()+1))
band_drift=float((max(band)-min(band))/band[-1])
qa={'sourceMeasurementThreshold':'alpha>=128; approximate silhouette/foot heuristics, no anatomical contact acceptance','rawCellCanvas':[512,512],'referenceHalfCanvas':[512,512],'raw':{'frames':[public(m) for m in rawmetrics],'widthVsTemplateReferenceRatio':[w/rw for w in raw_widths],'groundYRange':max(m['rootHeuristic'][1] for m in rawmetrics)-min(m['rootHeuristic'][1] for m in rawmetrics),'neutralReturnVsReferenceMaskIoU':rawseam},'registeredDiagnostic':{'commonScale':572/512,'canvas':[1024,1024],'frames':[public(m) for m in regmetrics],'referenceFeetHeuristic':ref_feet.tolist(),'maximumFootDifferenceFromExistingNeutralPx':drift,'maximumFootDifferenceWithinNewPosesPx':newdrift,'lowerBodyBandY':[600,720],'lowerBodyBandWidths':band,'lowerBodyBandRelativeWidthRange':band_drift,'neutralReturnVsExistingNeutralMaskIoU':regseam,'loopFirstLastSameExistingFrame':True,'newReturnToExistingNeutralTransitionAccepted':False},'plannedLocalTargets':plan['reviewTargets'],'localTargetResults':{'rawModelScaleAndBaselinePreserved':False,'registeredFeetWithin4pxFromExistingNeutral':drift<=4,'registeredLowerBodyWidthVariationWithin3percent':band_drift<=.03,'neutralReturnMaskIoUAtLeastPoint95':regseam>=.95},'generatedDistinctSourceDrawings':len({fid(f) for f in raw}),'sourceCropReconstructionExact':True,'actualNewHeadNeckDrawings':True,'registeredMotionIsNotNewGeneratedDrawings':True,'artAccepted':False,'MacIntegrated':False}
(P/'quality-review.json').write_text(json.dumps(qa,indent=2)+'\n')
neutral_entry={'frameId':plan['referenceFrameId'],'durationMs':800,'phase':'existing-neutral-entry','reuseVerified':False,'contactVerified':False,'sourceToDiagnostic':{'commonUniformScale':1,'integerTranslation':[0,0],'diagnosticCanvas':[1024,1024]}}
neutral_exit={**neutral_entry,'durationMs':600,'phase':'existing-neutral-exit'}
manifest={'schemaVersion':1,'kind':'production-clip-proposal-not-app-wire-format','clipId':'house-finch-female-preen-v1','species':'house_finch','variant':'adult-female','appearanceVersion':'house-finch-canon-v1','canonicalSpeciesId':None,'action':'preening','direction':'right-facing-body-with-head-turn','loop':True,'frames':[neutral_entry]+entries+[neutral_exit],'rawSourceFrames':entries,'sourceCanvas':[512,512],'diagnosticCanvas':[1024,1024],'supportRoot':[512,800],'frameBank':'../../frame-bank.json','sourceOriginal':{'file':'original.png','sha256':sha(P/'original.png')},'promptFile':'prompt.txt','events':[],'frameTimingMs':durations,'totalDurationMs':sum(durations),'worldSize':None,'reducedMotion':{'frameId':plan['referenceFrameId'],'verified':False},'review':{'state':'needs-revision','accepted':False,'issues':['Native generation ignored intended cell scale and introduced64px row-baseline offset.','One common diagnostic rescale and integer registration are explicit postprocessing, not proof of generated geometric compliance.','Feet/root and beak-feather annotations are provisional; no biological scale or physical contact acceptance.','Original neutral reuse is a proposed clip use; body/feather continuity with the new return drawing is not accepted.']},'validation':{'generatedSourceDrawings':6,'distinctSourceFrameIds':6,'previewAPNGFrames':Image.open(P/'preview.apng').n_frames,'previewGIFFrames':Image.open(P/'preview.gif').n_frames,'rawAPNGFrames':Image.open(P/'raw-cell-preview.apng').n_frames,'rawGIFFrames':Image.open(P/'raw-cell-preview.gif').n_frames,'sourceCropPixelsExact':True},'staged':False,'integrated':False,'transitionsVerified':False}
(P/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
# Extend once without rewriting or deleting any previous record/clip.
bank['frames'] += records;bank['clips'].append(manifest);bank['frameCount']=len(bank['frames']);bank['verifiedReuseCount']=0
(R/'frame-bank.json').write_text(json.dumps(bank,indent=2)+'\n')
(P/'frame-bank-projection.json').write_text(json.dumps({'authority':'subset projection of existing producer frame-bank.json; not a second registry','sourceRegistrySha256':sha(R/'frame-bank.json'),'frames':records,'existingNeutralReference':plan['referenceFrameId']},indent=2)+'\n')
print(json.dumps({'newDrawings':6,'registeredPreviewFrames':manifest['validation']['previewGIFFrames'],'rawPreviewFrames':manifest['validation']['rawGIFFrames'],'rawModelGroundRange':qa['raw']['groundYRange'],'registeredFootDifferenceFromReference':drift,'registeredFootDriftWithinNewPoses':newdrift,'registeredBodyBandWidthVariation':band_drift,'neutralSeamIoU':regseam,'localTargets':qa['localTargetResults'],'totalFramesInRegister':len(bank['frames'])}))
