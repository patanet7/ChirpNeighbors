from pathlib import Path
from PIL import Image,ImageDraw
from scipy.ndimage import label,distance_transform_edt
import numpy as np,json,hashlib,struct,zlib,shutil,math
P=Path(__file__).parent
sha=lambda b:hashlib.sha256(b).hexdigest()
fid=lambda im:'frame.sha256.'+sha(f'RGBA8;{im.width}x{im.height};'.encode()+im.tobytes())
def js(name,obj):(P/name).write_text(json.dumps(obj,indent=2)+'\n')
raw=Image.open(P/'original.png').convert('RGBA');a=np.array(raw);assert raw.size==(1254,1254)
# Extract4 disjoint birds, retaining every positive-alpha native pixel exactly once.
# Equal-cell rectangular cropping would cut the descending bird's beak atx627.
labels,n=label(a[:,:,3]>0,np.ones((3,3)));counts=np.bincount(labels.ravel());large=np.argsort(counts[1:])[::-1][:4]+1
seeds=np.zeros(labels.shape,np.uint8)
for lab in large:
 y,x=np.where(labels==lab);quadrant=int(y.mean()>=627)*2+int(x.mean()>=627);seeds[labels==lab]=quadrant+1
_,nearest=distance_transform_edt(seeds==0,return_indices=True);assignment=seeds[nearest[0],nearest[1]];assert set(np.unique(assignment))=={1,2,3,4}
names=['crouch','airborne-tuck','descending-reach','supported-settle'];(P/'native-frames').mkdir(exist_ok=True);(P/'frames1024').mkdir(exist_ok=True);(P/'frames96').mkdir(exist_ok=True)
# One fixed call-wide scale chosen against the existing neutral's ~714px length.
scale=736/627;scaledEdge=1472;assert scaledEdge/raw.width==scale
# x registration aligns body/foot region; y registration grounded for planted poses.
# Both air poses retain a virtual ground root while toes are deliberately unplanted.
translations=[(74,0),(109,150),(55,210),(100,0)]
frames=[];native_images=[];registered=[]
for i,(name,(dx,dy)) in enumerate(zip(names,translations)):
 native=np.zeros_like(a);chosen=(assignment==i+1)&(a[:,:,3]>0);native[chosen]=a[chosen];im=Image.fromarray(native);im.save(P/'native-frames'/f'{name}.png');native_images.append(im)
 # Resize the full common atlas canvas once with common scale, then account for cell origin.
 scaled=im.resize((scaledEdge,scaledEdge),Image.Resampling.NEAREST);sx=(i%2)*736;sy=(i//2)*736
 if i in [0,3]:
  mask=np.array(scaled)[:,:,3]>=128;yy,xx=np.where(mask);# lowest core toe on output-source ground boundary810
  dy=810-int(yy.max()+1-sy)
 offset=(dx-sx,dy-sy);canvas=Image.new('RGBA',(1024,1024));canvas.paste(scaled,offset)
 registrationAdjustment=[0,0]
 if i in [0,3]:
  # Align one common output toe support pixel with unchanged neutral:pixel55,75.
  # Translation only; do not warp feet or manufacture RGBA equality.
  options=[]
  for ay in range(-4,17):
   for ax in range(-24,25):
    trial=Image.new('RGBA',(1024,1024));trial.paste(scaled,(offset[0]+ax,offset[1]+ay));outa=np.array(trial.resize((96,96),Image.Resampling.NEAREST));core=outa[:,:,3]>=128
    if core[75,55] and np.where(core)[0].max()==75:options.append((abs(ax)+abs(ay),abs(ax),ax,ay,trial))
  assert options;_,_,ax,ay,canvas=min(options,key=lambda v:v[:2]);dx+=ax;dy+=ay;offset=(dx-sx,dy-sy);registrationAdjustment=[ax,ay]
 # Negative placement only removes transparent/very-low-alpha outer residue, never bird core.
 before=int((np.array(scaled)[:,:,3]>=128).sum());after=int((np.array(canvas)[:,:,3]>=128).sum());assert before==after
 canvas.save(P/'frames1024'/f'{name}.png');out=canvas.resize((96,96),Image.Resampling.NEAREST);out.save(P/'frames96'/f'{name}.png');registered.append(canvas)
 frames.append({'sourceFrameId':fid(im),'sourcePNG':f'native-frames/{name}.png','sourcePNGsha256':sha((P/'native-frames'/f'{name}.png').read_bytes()),'speciesId':'california_towhee','pose':name,'registration':{'nativeSourceCanvas':[1254,1254],'nativeAtlasQuadrant':i,'extraction':'Four largest alpha-positive connected components identify bird seeds; every positive-alpha atlas pixel assigned to nearest seed component. Original RGBA at assigned pixels retained verbatim on full atlas canvas; other pixels transparent zero. No connected bird core cut at equal-cell boundary.','callWideScale':scale,'scaledFullCanvas':[1472,1472],'placementFromScaledFullAtlas':list(offset),'localCellTranslation':[dx,dy],'outputToeAnchorTranslationAdjustment':registrationAdjustment,'perPoseScale':False,'poseCanvas':[1024,1024],'alpha128PixelsLostToCanvas':before-after,'plantedYRegistration':'integer translation aligns lowest alpha128 toe boundary to sourceY810' if i in [0,3] else 'virtual ground reference; no planted contact; deliberate foot clearance'},'registeredPNG':f'frames1024/{name}.png','registeredFrameId':fid(canvas),'registeredPNGsha256':sha((P/'frames1024'/f'{name}.png').read_bytes()),'outputPNG':f'frames96/{name}.png','outputFrameId':fid(out),'outputPNGsha256':sha((P/'frames96'/f'{name}.png').read_bytes()),'outputScaleFromRegistered':3/32})
reused=Image.open(P/'reused-neutral-source1024.png').convert('RGBA');assert fid(reused)=='frame.sha256.8d2819dc208be7c398b643e4ae53e1f0d3f0345896b868f11b1ccc9107761d0a'
reused.save(P/'frames1024'/'neutral.png');neutral=reused.resize((96,96),Image.Resampling.NEAREST);neutral.save(P/'frames96'/'neutral.png')
reuse={'sourceFrameId':fid(reused),'sourcePNG':'reused-neutral-source1024.png','sourcePNGsha256':sha((P/'reused-neutral-source1024.png').read_bytes()),'speciesId':'california_towhee','pose':'neutral','registration':{'scale':1,'translation':[0,0],'sourceCanvas':[1024,1024]},'outputPNG':'frames96/neutral.png','outputFrameId':fid(neutral),'outputPNGsha256':sha((P/'frames96'/'neutral.png').read_bytes())}
imgs=[neutral]+[Image.open(P/f['outputPNG']).convert('RGBA') for f in frames];allnames=['neutral']+names;ids=[reuse['outputFrameId']]+[f['outputFrameId'] for f in frames];density=67/78;pivot=[57,76];arrays=[np.array(im) for im in imgs]
metrics=[]
for j,(name,ar) in enumerate(zip(allnames,arrays)):
 y,x=np.where(ar[:,:,3]>=128);bbox=[int(x.min()),int(y.min()),int(x.max()+1),int(y.max()+1)];footROI=(ar[:,:,3]>=128)&(np.indices(ar.shape[:2])[0]>=58)&(np.indices(ar.shape[:2])[1]>=38)&(np.indices(ar.shape[:2])[1]<=77);fy,fx=np.where(footROI)
 # toes/legs ROI excludes tail for this right-facing anatomy; proxies remain labelled.
 supportBoundary=int(fy.max()+1);bottomx=fx[fy==fy.max()];grounded=j in [0,1,4]
 head=(ar[:,:,3]>=128)&(np.indices(ar.shape[:2])[0]<58)&(np.indices(ar.shape[:2])[1]>60);hy,hx=np.where(head);beakx=int(hx.max());beaky=float(np.median(hy[hx==beakx]));contact=[55.5,76.0] if grounded else None
 metrics.append({'pose':name,'sourceFrameId':reuse['sourceFrameId'] if j==0 else frames[j-1]['sourceFrameId'],'outputFrameId':ids[j],'outputPNG':'frames96/'+name+'.png','visibleBBoxAlpha128':bbox,'visibleWidthWorldUnits':(bbox[2]-bbox[0])/density,'visibleHeightWorldUnits':(bbox[3]-bbox[1])/density,'footLegProxyBBoxAlpha128':[int(fx.min()),int(fy.min()),int(fx.max()+1),supportBoundary],'lowestFootPixelBoundaryOutputY':supportBoundary,'toeBoundarySupportAnchorOutputXY':contact if grounded else None,'footContactsState':'planted' if grounded else 'unplanted','toeClearanceAtZeroRootHeightOutputPx':76-supportBoundary,'beakTipOutputXY':[beakx,beaky],'measurementCaveat':'bounded alpha128 geometry proxies, not anatomical toe tracking; lowest pixel-boundary support aligns plane but individual toes may change silhouette'})
# Retain diagnostic grounded-foot silhouette changes; a fixed support pixel is not fullfoot equality.
footsets=[];footrows=[]
for idx in [0,1,4]:
 ar=arrays[idx];yy,xx=np.indices((96,96));pts=np.argwhere((ar[:,:,3]>=128)&(yy>=72)&(yy<77)&(xx>=43)&(xx<73));footsets.append(pts);footrows.append({'pose':allnames[idx],'pixelCount':len(pts),'centroidOutputXY':[float(pts[:,1].mean()),float(pts[:,0].mean())],'bboxOutput':[int(pts[:,1].min()),int(pts[:,0].min()),int(pts[:,1].max()+1),int(pts[:,0].max()+1)]})
haus=0.;cent=0.
for aa in footsets:
 for bb in footsets:
  dd=np.linalg.norm(aa[:,None,:]-bb[None,:,:],axis=2);haus=max(haus,float(dd.min(axis=0).max()),float(dd.min(axis=1).max()));cent=max(cent,float(np.linalg.norm(aa.mean(axis=0)-bb.mean(axis=0))))
footdiag={'ROI':'alpha128,y72:77,x43:73;bothfeet combined,notanatomicaltracking','groundedFrames':footrows,'maxPairwiseCentroidChangeOutputPx':cent,'maxPairwiseMaskHausdorffOutputPx':haus,'maxPairwiseCentroidChangeWorldUnits':cent/density,'caveat':'Toes change silhouette despite one fixed support boundary pixel; visual footflicker review is still required. These shape statistics do not establish a rigid foot translation.'}
# Every output pixel remains original RGBA resampled only by the declared whole-canvas nearest rule.
atlas=Image.new('RGBA',(480,96))
for j,im in enumerate(imgs):atlas.paste(im,(j*96,0))
atlas.save(P/'hop-atlas96.png')
shutil.copy2('/workspace/asset-production/new-species/sd20-three-canon-v1/california_towhee/texture-review-manifest.json',P/'neutral-idle-review-manifest.json')
shutil.copy2('/workspace/asset-production/new-species/sd20-three-canon-v1/california_towhee/idle96.png',P/'neutral-idle96.png')
seq=[0,1,2,3,4,0];durations=[6,3,4,4,3,9];trajectory=[];t=0
for phase,(idx,hold) in enumerate(zip(seq,durations)):
 for k in range(hold):
  tick=t+k;air=idx in [2,3]
  if tick<9:root=[190.,130.]
  elif tick<=16:
   u=(tick-9)/7;root=[190-24*u,130-8*4*u*(1-u)]
  else:root=[166.,130.]
  m=metrics[idx];boundary=m['lowestFootPixelBoundaryOutputY'];lowworld=root[1]+(boundary-pivot[1])/density
  trajectory.append({'tick':tick,'pose':allnames[idx],'outputFrameId':ids[idx],'sourceFrameId':m['sourceFrameId'],'rootWorldXY':root,'rootTravelKind':'airborne-translation' if air else 'stationary-planted','planted':not air,'supportPlaneWorldY':130.,'lowestToeBoundaryWorldY':lowworld,'supportBoundaryErrorWorldUnits':lowworld-130 if not air else None,'toeClearanceWorldUnits':130-lowworld if air else 0})
 t+=hold
motion={'schemaVersion':1,'profile':'chirp-source-hop-motion-v1','speciesId':'california_towhee','clipId':'ground-hop-backward','canonicalRuntimeContract':False,'scope':'source-review-only','appBound':False,'canonicalSharpReceipt':None,'tickRate':30,'loop':False,'totalTicks':29,'durationMs':29/30*1000,'sourcePoseSequence':[{'pose':allnames[i],'outputFrameId':ids[i],'durationTicks':d} for i,d in zip(seq,durations)],'frameAtlas':{'PNG':'hop-atlas96.png','width':480,'height':96,'alpha':'straight-rgba8','colorSpace':'srgb','frames':[{'pose':n,'sourceRect':[i*96,0,96,96],'outputFrameId':ids[i]} for i,n in enumerate(allnames)]},'presentation':{'canvas':[96,96],'pivotOutputXY':pivot,'outputPixelsPerWorldUnit':density,'worldCanvas':[96/density,96/density],'existingNeutralVisibleWidthWorldUnits':78,'relativeBiologicalScaleApproved':False,'oneScaleForAllNewPoses':True},'trajectory':{'distanceWorldUnits':-24,'maxDesignedRootRiseWorldUnits':8,'groundPlaneWorldY':130,'startRootWorldXY':[190,130],'landingRootWorldXY':[166,130],'horizontalRule':'Linear root travel over ticks9..16 inclusive. Root position fixed while grounded, including lift-off and landing boundaries.','verticalRule':'Parabolic root rise8*4*u*(1-u) over airborne ticks; source drawn tuck additionally clears toes.','interpolation':'30Hz tick samples authoritative; display may hold per tick. Never move root during planted frames.','oneShotEnd':'Hold final neutral at landed root. Replay is explicit reset; no seamless loop claim.','samples':trajectory},'frames':metrics,'groundedFootDiagnostics':footdiag,'actionCoverage':{'generatedDrawings':4,'reusedDrawings':1,'riggedDrawings':0,'trajectoryTransformsCountAsDrawings':False,'packetBound':True,'appBound':False,'visuallyVerifiedInActualYard':False,'behavior':'Single backward ground hop; not complete double-scratch or feeding.'}}
js('motion-manifest.json',motion);js('frame-metadata.json',{'outputCanvas':[96,96],'density':density,'sourceToOutputScale':3/32,'frames':metrics,'groundedFootDiagnostics':footdiag,'rootAnchorMeaning':'Ground-plane virtual root at output[57,76]. Pixel-boundary contact points may be continuous and are custom source-review metadata, not canonical positive-alpha texture contacts.'})
# Source pose and traveled preview images are source composites, never browser captures.
def chunk(kind,data):return struct.pack('>I',len(data))+kind+data+struct.pack('>I',zlib.crc32(kind+data)&0xffffffff)
def apng(path,ims,ticks,plays):
 W,H=ims[0].size;data=b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',W,H,8,6,0,0,0))+chunk(b'acTL',struct.pack('>II',len(ims),plays));num=0
 for k,(im,d) in enumerate(zip(ims,ticks)):
  data+=chunk(b'fcTL',struct.pack('>IIIIIHHBB',num,W,H,0,0,d,30,0,0));num+=1;ar=np.array(im.convert('RGBA'));packed=zlib.compress(b''.join(b'\0'+ar[row].tobytes() for row in range(H)),9)
  if not k:data+=chunk(b'IDAT',packed)
  else:data+=chunk(b'fdAT',struct.pack('>I',num)+packed);num+=1
 (P/path).write_bytes(data+chunk(b'IEND',b''))
apng('source-poses.apng',[imgs[i] for i in seq],durations,1)
g=[]
for idx in seq:
 bg=Image.new('RGBA',(96,96),'#d9d4bd');bg.alpha_composite(imgs[idx]);g.append(bg.convert('RGB'))
g[0].save(P/'source-poses-once.gif',save_all=True,append_images=g[1:],duration=[200,100,130,130,100,300],optimize=False)
# World-scale composite: one output composite pixel per world unit; source pixels retain metadata density.
worldims=[];normalworld=round(96/density)
for sample in trajectory:
 idx=allnames.index(sample['pose']);root=sample['rootWorldXY'];bg=Image.new('RGBA',(360,180),'#e5e0cd');d=ImageDraw.Draw(bg);d.line((0,130,359,130),fill='#777a62');d.line((190,133,190,140),fill='#789b63');d.line((166,133,166,140),fill='#789b63');worldimg=imgs[idx].resize((normalworld,normalworld),Image.Resampling.NEAREST);xy=(round(root[0]-pivot[0]/density),round(root[1]-pivot[1]/density));bg.alpha_composite(worldimg,xy);d.text((8,7),'One-shot backward hop; end stays at landing. Replay resets.',fill='#28362d');d.text((8,156),f"tick {sample['tick']:02d} / {sample['pose']} / {'planted' if sample['planted'] else 'airborne'}",fill='#28362d');worldims.append(bg)
apng('traveled-once.apng',worldims,[1]*len(worldims),1)
worldims[0].convert('RGB').save(P/'traveled-once.gif',save_all=True,append_images=[im.convert('RGB') for im in worldims[1:]],duration=[30 if k%3 else 40 for k in range(len(worldims))],optimize=False)
# Normal output row, body thumbnails, and enlarged feet/leg crops for review.
sheet=Image.new('RGBA',(1000,520),'#e5e0cd');d=ImageDraw.Draw(sheet)
for j,(name,im,m) in enumerate(zip(allnames,imgs,metrics)):
 dx=j*198;d.text((dx+10,10),name,fill='#24312b');sheet.alpha_composite(im,(dx+45,35));crop=im.crop((38,53,79,80)).resize((164,108),Image.Resampling.NEAREST);sheet.alpha_composite(crop,(dx+10,175));d.text((dx+10,295),m['footContactsState'],fill='#24312b');d.text((dx+10,315),f"toe boundary y{m['lowestFootPixelBoundaryOutputY']}",fill='#24312b');d.text((dx+10,335),f"visible {m['visibleBBoxAlpha128'][2]-m['visibleBBoxAlpha128'][0]}px wide",fill='#24312b')
d.text((10,390),'Top:96px untrimmed source canvases. Bottom:4x feet/leg crops. Canon density67/78 retained.',fill='#24312b');d.text((10,415),'Airborne frames have no ground contacts. Planted toe-boundary support is explicit; toe shapes are not pixel-locked.',fill='#24312b');sheet.save(P/'normal-size-and-feet-contact-sheet.png')
js('source-lineage.json',{'original':'original.png','originalSHA256':sha((P/'original.png').read_bytes()),'frames':frames,'reusedFrames':[reuse],'newDrawings':4,'nativeCalls':1,'extractionPreservesAssignedRGBA':True,'allPositiveAlphaOriginalPixelsAssignedExactlyOnce':True,'sameCallWideRegistrationScale':scale})
primary={'batchId':'sd20-california-towhee-hop-v1','nativeCalls':1,'original':'original.png','originalSHA256':sha((P/'original.png').read_bytes()),'prompt':'prompt.txt','promptSHA256':sha((P/'prompt.txt').read_bytes()),'frames':frames,'reusedFrames':[reuse],'outputMetadata':['motion-manifest.json','frame-metadata.json','behavior-reference.json','source-lineage.json','neutral-idle-review-manifest.json'],'sourceStatus':'generated; registered and source motion packet prepared; coordinator independent review pending','notes':['Only4new native drawings;neutral reuse and trajectory transforms do not count as drawings.','Native2x2 grid was not strictly padded;full-atlas component extraction preserves crossing beak.','No per-pose fit/scale,source paint,warping,forced pixel equality or rigged standing-sprite locomotion.','Source status/rights/fidelity unreviewed;no canonicalSharp receipt or app binding claimed.']}
js('PRIMARY-SOURCE-MANIFEST.json',primary)
print(json.dumps({'newSourceIDs':[f['sourceFrameId'] for f in frames],'newPoseFrames':4,'registeredScale':scale,'support':metrics,'rootStart':trajectory[0]['rootWorldXY'],'rootEnd':trajectory[-1]['rootWorldXY']},indent=2))
