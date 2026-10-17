"""Explicit, source-pixel layer edit. No diffusion, new drawings or runtime engine."""
from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib,shutil
P=Path(__file__).parent;V1=P.with_name('finch-fixed-body-rig-proof-v1');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for name in ['source-neutral.png','head-mask.png']:
 if (V1/name).exists():shutil.copy2(V1/name,P/name)
assert sha(P/'source-neutral.png')=='ed79704dca763d6ef32beb6ff6a7a9e0d7cf26e3069619e25f2c7539d14fb605'
a=np.array(Image.open(P/'source-neutral.png').convert('RGBA'));hm=np.array(Image.open(P/'head-mask.png').convert('L'))>0;H,W=a.shape[:2];yy,xx=np.indices((H,W));roi=(xx>=445)&(xx<635)&(yy>=475)&(yy<575)
# Editable underpaint mask is explicit; its pixels clone the original same XY.
ump=P/'neck-underpaint-mask.png'
if not ump.exists():Image.fromarray(np.uint8(hm&roi)*255).save(ump)
um=np.array(Image.open(ump).convert('L'))>0
assert not um[600:].any();assert np.all(~um|(hm&roi))
base=a.copy();base[hm]=0;under=np.zeros_like(a);under[um]=a[um];body=base.copy();body[um]=under[um];head=a.copy();head[~hm]=0
for n,b in [('body-base-layer.png',base),('neck-underpaint-layer.png',under),('body-underpaint-layer.png',body),('head-layer.png',head)]:Image.fromarray(b).save(P/n)
(P/'before').mkdir(exist_ok=True);(P/'frames-native1024').mkdir(exist_ok=True);frames=[];entries=[];measure=[];angles=[0,-.12,0,.12,0];cx,cy=560,516
for i,t in enumerate(angles):
 old=V1/f'rig-frame-{i:02}.png';before=P/'before'/old.name
 if old.exists():shutil.copy2(old,before)
 assert before.exists()
 c,s=np.cos(t),np.sin(t);sx=np.floor(c*(xx-cx)+s*(yy-cy)+cx+.5).astype(int);sy=np.floor(-s*(xx-cx)+c*(yy-cy)+cy+.5).astype(int);valid=(sx>=0)&(sx<W)&(sy>=0)&(sy<H);sx=np.clip(sx,0,W-1);sy=np.clip(sy,0,H-1);sa=a[sy,sx,3]
 # Hard layer ownership keeps actual original RGBA tuples; no color repaint/blend.
 hit=valid&hm[sy,sx]&(sa>0)&((sa>=128)|(body[:,:,3]<128));out=body.copy();out[hit]=a[sy[hit],sx[hit]];out[600:]=a[600:]
 if t==0:out=a.copy()
 path=P/'frames-native1024'/f'{i:02}.png';Image.fromarray(out).save(path);frames.append(Image.fromarray(out));b=np.array(Image.open(before).convert('RGBA'));beforeMissing=(a[:,:,3]>=128)&(b[:,:,3]<128)&hm;afterMissing=(a[:,:,3]>=128)&(out[:,:,3]<128)&hm
 measure.append({'phase':i,'angleRadians':t,'beforeWholeRestMaskUncoveredPixels':int(beforeMissing.sum()),'afterWholeRestMaskUncoveredPixels':int(afterMissing.sum()),'beforeNeckRegionUncoveredPixels':int((beforeMissing&roi).sum()),'afterNeckRegionUncoveredPixels':int((afterMissing&roi).sum()),'protectedRGBAChangedPixels':int(np.any(out[600:]!=a[600:],axis=2).sum()),'underpaintVisiblePixelCount':int((um&~hit&(out[:,:,3]>0)).sum()) if t else 0,'occlusion':'neutral source exact' if not t else 'moving head over retained neck overlap; no behind-head reconstruction or depth switch','artReview':'owner-review-required'})
 entries.append({'file':str(path.relative_to(P)),'sha256':sha(path),'angleRadians':t,'durationMs':160,'riggedAssembly':True,'newDrawing':False})
frames[0].save(P/'preview.apng',save_all=True,append_images=frames[1:],duration=[160]*5,loop=0,disposal=0,blend=0)
g=[]
for f in frames:
 bg=Image.new('RGBA',f.size,'#e1dbc8');bg.alpha_composite(f);g.append(bg.resize((384,384),Image.Resampling.NEAREST).convert('RGB'))
g[0].save(P/'preview.gif',save_all=True,append_images=g[1:],duration=[160]*5,loop=0,optimize=False)
plan={'workflow':'explicit editable binary masks + source-clone underpaint + rigid source head cutout','sourceUnchanged':True,'sourceSha256':sha(P/'source-neutral.png'),'headMask':'head-mask.png','underpaintMask':'neck-underpaint-mask.png','sourceCloneMapping':'same sourceXY; no generated or painted colors','underpaintAllowedRectangle':[445,475,635,575],'protectedRectangle':[0,600,1024,1024],'hardOwnership':'prefer head alpha>=128 or uncovered background; retain originalRGBA tuples, no feather blend','layerOrder':['body-base-layer.png','neck-underpaint-layer.png','rigid head-layer.png'],'anglesRadians':angles,'pivot':[560,516],'fixedFootPoints':[[483,792],[535,800]],'root':[512,800],'leftRightAnatomyAssigned':False,'newGenerationCalls':0,'newDrawings':0,'forbidden':['protectedpixel changes','perphase body rescale/translation','newgeneratorcalls','loosen contact tolerances'],'ownerReviewRegion':[445,465,650,580],'limits':['fixed side view and small +/-0.12rad head pivot only','neck overlap clone may retain stale contour/doubled feather edge','no wing/body/depth occlusion switch','not actual preening/walking or full species clip']}
(P/'layer-edit-plan.json').write_text(json.dumps(plan,indent=2)+'\n');manifest={'experimentId':P.name,'classification':'rigged-layer-cleanup-not-new-drawings','sourceFrameId':'frame.sha256.7c12c45d8a8a6e64824669c595f4f58630aaa7a2eb6854ca76f5cd2311d2e6fe','sourceOriginal':{'file':'source-neutral.png','sha256':sha(P/'source-neutral.png')},'canvas':[1024,1024],'root':[512,800],'protectedRectangle':[0,600,1024,1024],'frames':entries,'newGenerationCalls':0,'newDrawings':0,'artAccepted':False,'sourceReuseProductionVerified':False,'integrated':False,'layerPlan':'layer-edit-plan.json','fixedContacts':[{'id':'foot-A','source':[483,792]},{'id':'foot-B','source':[535,800]}],'rendererBinding':{'repository':'patanet7/birdsong-yard-sprites','commit':'2e2f724f7b952179495e91f06f0d2d4575569595','files':[{'file':'src/lib/assets/pose-geometry.ts','sha256':sha(P/'contract-snapshot/pose-geometry.ts')}],'actualMacWorkingTreeVerified':False},'priorProofUnchanged':True,'ownerReviewRegion':[445,465,650,580]};(P/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');(P/'occlusion-review.json').write_text(json.dumps({'allFivePhases':measure,'neckGapCountsUseSameAlpha128HeuristicAsV1':True,'wholeRestMaskMetricRetained':True,'remainingOwnerReview':{'phase':1,'uncoveredSourcePixels':144,'sourceRectangle':[607,475,633,492],'visualFinding':'small stepped jaw/neck edge after original bill removal; do not restore old bill to eliminate numerical holes','ownerNeedsToJudge':['continuous lowerjaw/neck contour','no duplicatedbill or staleneck edge','feather overlap/lighting phases1and3'],'accepted':False},'allArtJudgmentPendingOwner':True,'ownerReviewRectangle':[445,465,650,580]},indent=2)+'\n')
print(json.dumps({'beforeNeckGaps':[x['beforeNeckRegionUncoveredPixels'] for x in measure],'afterNeckGaps':[x['afterNeckRegionUncoveredPixels'] for x in measure],'wholeRestMaskAfter':[x['afterWholeRestMaskUncoveredPixels'] for x in measure],'protectedChanges':[x['protectedRGBAChangedPixels'] for x in measure]}))
