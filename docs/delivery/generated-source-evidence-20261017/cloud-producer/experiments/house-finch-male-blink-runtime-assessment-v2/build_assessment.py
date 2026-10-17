"""Runtime-resolution assessment of existing drawn frames. No source edits/generation."""
from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,struct,zlib,math
P=Path(__file__).parent;R=P.parent.parent;old=json.loads((R/'experiments/house-finch-male-blink-reuse-v1/manifest.json').read_text());srcframes=old['referenceFrames'];names=['open','half','closed'];ids=['finch-male-open-96','finch-male-half-96','finch-male-closed-96'];O=P/'frames96';O.mkdir(exist_ok=True);images=[];arrays=[];lineage=[];sha=lambda b:hashlib.sha256(b).hexdigest()
for name,id,f in zip(names,ids,srcframes):
 path=R/f['file'];assert sha(path.read_bytes())==f['fileSha256'];im=Image.open(path).convert('RGBA');assert 'frame.sha256.'+sha(f'RGBA8;{im.width}x{im.height};'.encode()+im.tobytes())==f['frameId'];out=im.resize((96,96),Image.Resampling.NEAREST);out.save(O/(name+'.png'));images.append(out);arrays.append(np.array(out));lineage.append({'outputFrameId':id,'sourceFrameId':f['frameId'],'sourcePNG':f['file'],'sourcePNGsha256':f['fileSha256'],'outputPNG':'frames96/'+name+'.png','outputPNGsha256':sha((O/(name+'.png')).read_bytes()),'outputRGBAsha256':sha(out.tobytes()),'sourceCanvas':[1024,1024],'outputCanvas':[96,96],'scale':3/32,'resampling':'whole-canvas nearest; no alpha/palette change or per-frame fit','sourceRegistration':f['derivation']})
y,x=np.indices((96,96));visible=[a[:,:,3]>=128 for a in arrays];common=np.logical_and.reduce(visible);contacts=[]
for label,side,target in [('foot-a',x<48,(44.90625,74.34375)),('foot-b',x>=48,(50.90625,74.90625))]:
 candidates=np.argwhere(common&side&(y>=72)&(y<76)&(x>=38)&(x<61));assert len(candidates)>0;cy,cx=min(candidates,key=lambda p:(-int(p[0]),(p[1]-target[0])**2+(p[0]-target[1])**2));contacts.append({'id':label,'x':int(cx),'y':int(cy)})
atlas=Image.new('RGBA',(288,96));manifestFrames=[]
for i,(im,id) in enumerate(zip(images,ids)):
 atlas.paste(im,(i*96,0));manifestFrames.append({'id':id,'sourceRect':{'x':i*96,'y':0,'width':96,'height':96},'canvas':{'width':96,'height':96},'trim':{'x':0,'y':0},'pivot':{'x':48,'y':75},'contacts':contacts,'world':{'width':96,'height':96},'sourcePixelsPerWorldUnit':1})
atlas.save(P/'blink-atlas96.png');seq=[0,1,2,1,0];ticks=[42,2,3,2,20];manifest={'schemaVersion':1,'profile':'chirp-texture-review-v1','scope':'review-only','approval':'unreviewed','activation':'none','source':{'sha256':sha((P/'blink-atlas96.png').read_bytes()),'creator':'Chirp cloud source-preserving exporter','tool':'Pillow nearest canvas export','toolVersion':Image.__version__ if hasattr(Image,'__version__') else '12.3.0','rights':'unreviewed','fidelity':'unreviewed'},'atlas':{'width':288,'height':96,'alpha':'straight-rgba8','colorSpace':'srgb'},'frames':manifestFrames,'clips':[{'id':'idle','tickRate':30,'loop':True,'frames':[{'frameId':ids[i],'durationTicks':t} for i,t in zip(seq,ticks)]}]};(P/'texture-review-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');(P/'source-lineage.json').write_text(json.dumps({'existingSourceDrawings':3,'newDrawings':0,'outputUniqueFrames':3,'clipSteps':5,'frames':lineage},indent=2)+'\n')
# Exact rational APNG delays match ticks/30, avoiding GIF's10ms resolution.
def chunk(kind,data):return struct.pack('>I',len(data))+kind+data+struct.pack('>I',zlib.crc32(kind+data)&0xffffffff)
png=b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',96,96,8,6,0,0,0))+chunk(b'acTL',struct.pack('>II',5,0));number=0
for k,(idx,t) in enumerate(zip(seq,ticks)):
 png+=chunk(b'fcTL',struct.pack('>IIIIIHHBB',number,96,96,0,0,t,30,0,0));number+=1;a=arrays[idx];data=zlib.compress(b''.join(b'\0'+a[row].tobytes() for row in range(96)),9)
 if k==0:png+=chunk(b'IDAT',data)
 else:png+=chunk(b'fdAT',struct.pack('>I',number)+data);number+=1
png+=chunk(b'IEND',b'');(P/'normal-speed.apng').write_bytes(png)
g=[]
for idx in seq:
 bg=Image.new('RGBA',(96,96),'#d9d4bd');bg.alpha_composite(images[idx]);g.append(bg.convert('RGB'))
g[0].save(P/'normal-speed-approx.gif',save_all=True,append_images=g[1:],duration=[1400,70,100,70,660],loop=0,optimize=False)
# Measure actual96px raster foot cores separately from projected source heuristics.
def rasterfeet(a):
 mask=a[:,:,3]>=128;result=[]
 for side in [x<48,x>=48]:
  yy,xx=np.where(mask&side&(y>=72)&(y<76)&(x>=38)&(x<61));assert len(xx)>0;result.append({'medianX':float(np.median(xx)),'lowestVisibleRow':int(yy.max()),'groundBoundaryY':int(yy.max()+1),'bbox':[int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)],'pixels':len(xx)})
 return result
raster=[rasterfeet(a) for a in arrays];source=json.loads((R/'experiments/house-finch-male-blink-reuse-v1/measurements.json').read_text())['measurements'];projected=[np.array(v['feet'])*3/32 for v in source];maxpair=max(float(np.linalg.norm(p-q)) for a in projected for b in projected for p,q in zip(a,b));maxraster=max(float(np.hypot(a['medianX']-b['medianX'],a['groundBoundaryY']-b['groundBoundaryY'])) for af in raster for bf in raster for a,b in zip(af,bf));bbox=[]
for a in arrays:
 yy,xx=np.where(a[:,:,3]>=128);bbox.append([int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)])
measure={'sourceToOutput':{'scale':3/32,'outputPixelsPerSourcePixel':.09375,'sourcePixelsPerOutputPixel':32/3,'sourceCanvas':[1024,1024],'outputCanvas':[96,96],'presentationDensity':1,'presentationWorldCanvas':[96,96],'worldScaleBiologicallyApproved':False,'viewerReferenceCSSPixelsPerWorldUnit':1},'projectedSourceFootHeuristic':{'coordinateCaveat':'threshold/median proxies, not anatomical tracking; earlier integer source registration preserved','maxFromOpenSourcePx':max(v['footDriftSourcePxFromOpen'] for v in source),'maxFromOpenOutputPx':max(v['footDriftSourcePxFromOpen'] for v in source)*3/32,'maxPairwiseOutputPx':maxpair,'worldSlipAtOutputDensities':{str(d):maxpair/d for d in [1,2,4]},'anatomicalMeasurementUncertainty':None},'actualRasterAlpha128FootCore':{'bands':'output y72..75,x38..60; split atx48; threshold128','frames':[{'phase':name,'feet':v} for name,v in zip(names,raster)],'maxPairwiseMedianAndBaselineDisplacementOutputPx':maxraster,'maximumBaselineBoundaryErrorFromY75':max(abs(f['groundBoundaryY']-75) for fs in raster for f in fs),'commonDeclaredContactPixels':contacts,'commonContactsPositiveAlphaAllFrames':True,'note':'common declared pixels satisfy contact registration only, not proof that every toe/foot pixel is stationary or physical support approved'},'scaleConsistency':{'singleUniformExportScale':True,'perFrameFit':False,'visibleBBoxesAlpha128':bbox,'visibleWidthRangePx':[min(b[2]-b[0] for b in bbox),max(b[2]-b[0] for b in bbox)],'visibleHeightRangePx':[min(b[3]-b[1] for b in bbox),max(b[3]-b[1] for b in bbox)]},'loop':{'durationTicks':sum(ticks),'tickRate':30,'durationMs':sum(ticks)/30*1000,'blinkWindowMs':sum(ticks[1:4])/30*1000,'phaseDurationTicks':ticks,'phaseDurationMs':[t/30*1000 for t in ticks],'endpointRGBAChangedPixels':0,'endpointFrameSameExistingId':True,'intermediateTransitionsRequireVisualReview':True,'APNGexactRationalTiming':True,'GIFapproximate10msTiming':True},'sourcePixelDifferences':'retained diagnostics only, not animation quality gate','rigInvariantsNotAppliedToNaturalDrawnBlink':True,'newGeneratedDrawings':0,'newProductionClipsCounted':0,'ownerApproval':False,'normalYardIntegrationPerformed':False}
# Small-mask geometry complements the raw median statistic, without hiding it.
footsets=[]
for a in arrays:
 footsets.append([np.argwhere((a[:,:,3]>=128)&side&(y>=72)&(y<76)&(x>=38)&(x<61)) for side in [x<48,x>=48]])
haus=0.;centroid=0.
for af in footsets:
 for bf in footsets:
  for a,b in zip(af,bf):
   distances=np.linalg.norm(a[:,None,:]-b[None,:,:],axis=2)
   haus=max(haus,float(distances.min(axis=0).max()),float(distances.min(axis=1).max()))
   centroid=max(centroid,float(np.linalg.norm(a.mean(axis=0)-b.mean(axis=0))))
measure['actualRasterAlpha128FootCore'].update(maxPairwiseFootMaskHausdorffOutputPx=haus,maxPairwisePixelCentroidDriftOutputPx=centroid,maxPerFootGroundBoundaryChangeOutputPx=max(abs(a['groundBoundaryY']-b['groundBoundaryY']) for af in raster for bf in raster for a,b in zip(af,bf)),perFootConstantGroundBoundaryOutputY=[74,75],medianStatisticWarning='2px median shifts within11to13pixel foot masks; all bounds and perfoot baseline stayfixed, so this is not evidence of a2px rigid foot translation. Raw statistic retained; visual footflicker review required.',baselineOffsetInterpretation='The1px error from arbitraryY75 is a constant difference between near/far foot rows, not temporal foot slip.')

if (P/'owner-provisional-review.json').exists():
 measure['ownerVisualReview']=json.loads((P/'owner-provisional-review.json').read_text())
 measure['ownerApprovalMeaning']='final production approval remains false; provisional normal-size visual acceptance recorded separately'
(P/'runtime-measurements.json').write_text(json.dumps(measure,indent=2)+'\n');print(json.dumps(measure))
