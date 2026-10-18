from pathlib import Path
from PIL import Image,ImageDraw
from datetime import datetime,timezone
import json,hashlib,numpy as np,shutil
P=Path(__file__).parent;S=Path('/workspace/asset-production/motion/sd20-house-finch-hop-v1');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();fid=lambda im:'frame.sha256.'+hashlib.sha256(f'RGBA8;{im.width}x{im.height};'.encode()+im.tobytes()).hexdigest()
def js(n,v):(P/n).write_text(json.dumps(v,indent=2)+'\n')
primary=json.loads((S/'PRIMARY-SOURCE-MANIFEST.json').read_text());ledger=json.loads((S/'review-target-hashes.json').read_text());assert len(ledger['files'])==46
tracked={r['file']:r['sha256'] for r in ledger['files']}
for n in ['review-target-hashes.json','STABLE-GO.json','source-files.sha256.json','independent-review.json','independent-review.md','source-technical-review.json','source-technical-review.md']:
 if (S/n).exists():tracked[n]=sha(S/n)
assert all(sha(S/n)==h for n,h in tracked.items());js('held-source-before-hashes.json',{'sourceFolder':str(S),'frozenPayloadTargets':46,'trackedInputs':tracked,'nativeCallsThisAudit':0})
for d in ['raw-cells627','padded1024','proof96','held96']:(P/d).mkdir(exist_ok=True)
shutil.copy2(S/'reference-awake-source1024.png',P/'exact-awake-source1024.png');shutil.copy2(S/'exact-awake96.png',P/'exact-awake96.png');shutil.copy2(S/'motion-manifest.json',P/'original-authored-motion-reference.json');old=Image.open(P/'exact-awake96.png').convert('RGBA');records=[]
lookupIndices=[];samplePosition=(1024/96)*.5
for _ in range(96):lookupIndices.append(int(samplePosition));samplePosition+=1024/96
for r in primary['frames']:
 n=r['pose'];raw=Image.open(S/r['sourcePNG']).convert('RGBA');assert raw.size==(627,627) and fid(raw)==r['sourceFrameId'];shutil.copy2(S/r['sourcePNG'],P/'raw-cells627'/(n+'.png'));shutil.copy2(S/r['outputPNG'],P/'held96'/(n+'.png'));padded=Image.new('RGBA',(1024,1024),(0,0,0,0));padded.paste(raw,(198,198));padded.save(P/'padded1024'/(n+'.png'));assert padded.crop((198,198,825,825)).tobytes()==raw.tobytes();out=padded.resize((96,96),Image.Resampling.NEAREST);out.save(P/'proof96'/(n+'.png'));metrics=[]
 for file in [P/'exact-awake96.png',P/'held96'/(n+'.png'),P/'proof96'/(n+'.png')]:
  a=np.array(Image.open(file).convert('RGBA'));y,x=np.where(a[:,:,3]>=128);bbox=[int(x.min()),int(y.min()),int(x.max()+1),int(y.max()+1)];metrics.append({'file':str(file.relative_to(P)),'PNGsha256':sha(file),'decodedRGBAId':fid(Image.fromarray(a)),'bboxAlpha128':bbox,'visibleWidthWorld':bbox[2]-bbox[0],'lowestRow':bbox[3]-1,'positiveAlphaPixels':int((a[:,:,3]>0).sum())})
 records.append({'pose':n,'primarySourceFrameId':r['sourceFrameId'],'primaryPNG':'raw-cells627/'+n+'.png','primaryPNGsha256':sha(P/'raw-cells627'/(n+'.png')),'originalPrimaryPNG':r['sourcePNG'],'paddedPNG':'padded1024/'+n+'.png','paddedPNGsha256':sha(P/'padded1024'/(n+'.png')),'proofPNG':'proof96/'+n+'.png','proofPNGsha256':sha(P/'proof96'/(n+'.png')),'metricsOrder':['exactoldawake','held627to96','densityhypothesisPad1024to96'],'metrics':metrics,'sourcePixelsUnchanged':True,'opaqueImageFitUsed':False})
js('density-proof-manifest.json',{'kind':'zero-call-native-pixel-density-calibration-HYPOTHESIS','batchId':P.name,'createdUTC':datetime.now(timezone.utc).isoformat(),'nativeCalls':0,'newDrawings':0,'reusedNewSourceDrawings':4,'reusedAwake':1,'sourceOriginalHopStatus':'HELD; unchanged','hypothesis':'Treat each actual native627cell pixel as same sourcepixel density as selected1024awake (1024/96px perworld), instead of treating each cell as whole1024canvas. Generator did not fulfill matched sourcecanvas composition; this is an alternate engineering hypothesis only.','inputCellCanvas':[627,627],'constantCanvasPadding':{'left':198,'top':198,'right':199,'bottom':199,'RGBA':[0,0,0,0],'sameEveryPose':True},'paddedCanvas':[1024,1024],'outputCanvas':[96,96],'outputWorld':[96,96],'outputDensity':1,'referenceNativePixelsPerWorldUnit':1024/96,'nativeCellPixelDensityActuallyKnown':False,'cellToPaddedEdgeMatrix':[[1,0,198],[0,1,198],[0,0,1]],'paddedToOutputEdgeMatrix':[[3/32,0,0],[0,3/32,0],[0,0,1]],'composedCellToOutputEdgeMatrix':[[3/32,0,18.5625],[0,3/32,18.5625],[0,0,1]],'sampling':'Pillow12.3nearest doubleaccumulation: step=1024/96;position=step*.5; select int(position);position+=step, identicalx/y. Exacttable retained in sampling-formula-failure-receipt.json; no blending.','nearestOutputToPaddedIndex1D':lookupIndices,'samplingFailureReceipt':'sampling-formula-failure-receipt.json','previousHeldCellTo96Scale':96/627,'hypothesisRelativeScaleToHeld':627/1024,'bboxFit':False,'perPoseScale':False,'perPosePixelTranslation':False,'footSnap':False,'paint':False,'alphaCleanup':False,'qualification':'Constant198padding is declared canvasembedding shared by allposes. It is not a claim that native627cell dimensions established the requested scale. Derivatives are not new drawings or replacements of frozen artwork.','records':records,'acceptedHop':False,'usableGain':0,'geometryReviewed':False,'supportWorld':None,'MacBinding':'UNKNOWN','appBound':False})
# Triptych normal96 CSS projection and enlarged feet; all composites from ownedsourcePNGs.
sheet=Image.new('RGBA',(690,640),'#e8e1d0');d=ImageDraw.Draw(sheet)
for i,r in enumerate(records):
 y=30+i*150;d.text((8,y-18),r['pose'],fill='#283e2e')
 for j,(lab,file) in enumerate([('exactawake',P/'exact-awake96.png'),('heldwholecell',P/'held96'/(r['pose']+'.png')),('densityHYPOTHESIS',P/'proof96'/(r['pose']+'.png'))]):
  im=Image.open(file).convert('RGBA')
  for k,color in enumerate(['#e5e0cd','#182a32']):
   pane=Image.new('RGBA',(96,96),color);pane.alpha_composite(im);sheet.alpha_composite(pane,(j*230+k*105+5,y))
  d.text((j*230+5,y+100),lab+' width'+str(r['metrics'][j]['visibleWidthWorld']),fill='#283e2e')
sheet.save(P/'normal96-side-by-side-light-dark.png');feet=Image.new('RGBA',(1060,460),'#e8e1d0');dd=ImageDraw.Draw(feet)
for i,r in enumerate(records):
 im=Image.open(P/r['proofPNG']).convert('RGBA');pane=Image.new('RGBA',im.size,'#e5e0cd');pane.alpha_composite(im);feet.alpha_composite(pane.resize((192,192),Image.Resampling.NEAREST),(i*265+5,20));feet.alpha_composite(pane.crop((38,50,77,80)).resize((234,180),Image.Resampling.NEAREST),(i*265+5,240));dd.text((i*265+5,4),r['pose'],fill='#283e2e')
feet.save(P/'density-hypothesis-enlarged-feet.png');assert all(sha(S/n)==h for n,h in tracked.items());js('held-source-after-hashes.json',{'sourceFolder':str(S),'frozenPayloadTargets':46,'allTrackedHashesUnchanged':True,'trackedInputs':tracked});print(json.dumps([{'pose':r['pose'],'widths':[m['visibleWidthWorld'] for m in r['metrics']],'lowrows':[m['lowestRow'] for m in r['metrics']]} for r in records],indent=2))
