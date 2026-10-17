from pathlib import Path
import json,hashlib,datetime,base64,io,struct,zlib
import numpy as np
from scipy import ndimage
from PIL import Image,ImageDraw
D=Path(__file__).parent
sha=lambda b:hashlib.sha256(b).hexdigest()
def dump(p,j):(D/p).write_text(json.dumps(j,indent=2,ensure_ascii=False)+'\n')
def rid(im):return 'frame.sha256.'+sha(f'RGBA8;{im.width}x{im.height};'.encode()+im.convert('RGBA').tobytes())
def bbox(mask):
 yy,xx=np.where(mask);return [int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)] if len(xx) else None
def iou(a,b):return float((a&b).sum()/(a|b).sum()) if (a|b).any() else 1.
im=Image.open(D/'original.png').convert('RGBA');a=np.array(im);h,w=a.shape[:2]
labels,n=ndimage.label(a[:,:,3]>=8,np.ones((3,3)));sizes=np.bincount(labels.ravel());ids=list(np.argsort(sizes[1:])[-3:]+1);ids.sort(key=lambda i:np.where(labels==i)[1].mean());principal=np.isin(labels,ids)
_,inds=ndimage.distance_transform_edt(~principal,return_indices=True);nearest=labels[inds[0],inds[1]]
owner=np.full((h,w),-1,dtype=np.int8)
for k,i in enumerate(ids):owner[(nearest==i)&(a[:,:,3]>0)]=k
assert np.all(owner[a[:,:,3]>0]>=0)
(D/'frames-source1024').mkdir(exist_ok=True);(D/'native-owned').mkdir(exist_ok=True)
frames=[];records=[];measurements=[];rawroots=[]
poses=['calm','right-bend','recover-left']
for k,pose in enumerate(poses):
 owned=owner==k;b=bbox(owned);x0,y0,x1,y1=b
 # Stable root-collar proxy uses opaque central dirt/root band rather than upper leaf mass.
 yy,xx=np.where(owned&(a[:,:,3]>=128)&(np.indices((h,w))[0]>=780)&(np.indices((h,w))[0]<813));root=[int(np.median(xx)),800];rawroots.append(root)
 dx,dy=512-root[0],900-root[1];assert x0+dx>=0 and y0+dy>=0 and x1+dx<=1024 and y1+dy<=1024
 nat=np.zeros_like(a);nat[owned]=a[owned];Image.fromarray(nat).save(D/f'native-owned/{pose}.png')
 out=np.zeros((1024,1024,4),np.uint8);ys,xs=np.where(owned);out[ys+dy,xs+dx]=a[ys,xs];fr=Image.fromarray(out);fr.save(D/f'frames-source1024/{pose}.png');frames.append(fr)
 assert np.array_equal(out[ys+dy,xs+dx],a[ys,xs])
 # Retain source-native pixel tuples, including every alpha1+ pixel. Hidden RGB underalpha0 stays in original only.
 outputID=rid(fr)
 records.append({'sourceFrameId':outputID,'sourcePNG':f'frames-source1024/{pose}.png','sourcePNGsha256':sha((D/f'frames-source1024/{pose}.png').read_bytes()),'speciesId':None,'assetId':'purple_needlegrass','pose':pose,'registration':{'method':'Three largest 8-connected alpha>=8 clumps; every original alpha>0 pixel assigned to nearest principal clump; exact RGBA pixel copy with integer translation only','sourceOriginal':'original.png','sourceOriginalSHA256':sha((D/'original.png').read_bytes()),'principalComponentLabel':int(ids[k]),'positiveAlphaPixels':int(owned.sum()),'nativeOwnedFullCanvasPNG':f'native-owned/{pose}.png','nativeOwnedFullCanvasRGBAId':rid(Image.fromarray(nat)),'nativeAlphaBBox':b,'rawRootProxy':root,'rawRootMethod':'Median opaque x in atlas y780:813; source root collar y800 chosen once for all poses','translation':[dx,dy],'registeredRoot':[512,900],'sourceCanvas':[1024,1024],'individualScale':1,'perPoseResize':False,'paintedOrWarpedPixels':False,'allAssignedPositiveAlphaPixelsCopiedExactly':True},'illustrativePhysicalSpecimen':{'heightMetres':.8,'canopyWidthMetres':.55,'basis':'retained reference proposal, not measured accession or runtime calibration'}})
 # Measurements are diagnostics, not automatic animation acceptance gates.
 mask=out[:,:,3]>=128;all8=out[:,:,3]>=8;Y,X=np.indices(mask.shape)
 base=mask&(Y>=880)&(Y<925)&(X>=330)&(X<700);upper=mask&(Y>=180)&(Y<650)
 red=(out[:,:,0]>200)&(out[:,:,1]<60)&(out[:,:,2]<60)
 def cen(m):
  yy,xx=np.where(m);return [float(xx.mean()),float(yy.mean())] if len(xx) else None
 measurements.append({'pose':pose,'alphaBoundsPositive':bbox(out[:,:,3]>0),'alphaBounds8':bbox(all8),'alphaBounds128':bbox(mask),'baseProxyCentroidSourcePx':cen(base),'upperProxyCentroidSourcePx':cen(upper),'rootPixelAlpha':int(out[900,512,3]),'baseProxyPixels':int(base.sum()),'upperProxyPixels':int(upper.sum()),'visibleRedRGBAlpha8Pixels':int((red&all8).sum()),'edgeAlpha8Positive':int(np.concatenate([out[0,:,3],out[-1,:,3],out[:,0,3],out[:,-1,3]]).clip(0).astype(np.uint16).sum()>0),'mode':'RGBA','sourcePNG':f'frames-source1024/{pose}.png'})
# Full-atlas exact coverage, with no lost or multiply assigned positive-alpha pixel.
coverage={'originalPositiveAlphaPixels':int((a[:,:,3]>0).sum()),'assignedPixels':int(sum((owner==k).sum() for k in range(3))),'unassignedPositiveAlpha':int(((a[:,:,3]>0)&(owner<0)).sum()),'sourcePixelCopyExact':True,'rawPoseRoots':rawroots,'rawEqualThirdsCellRootX':[r[0]-k*(w/3) for k,r in enumerate(rawroots)],'rawRootXRangeWithinEqualThirds':float(np.ptp([r[0]-k*(w/3) for k,r in enumerate(rawroots)])),'registrationDoesNotProveGeneratedRootCompliance':True}
arrays=[np.array(f) for f in frames];metrics=[]
for i,k in [(0,1),(1,2),(2,0)]:
 ai=arrays[i][:,:,3]>=128;ak=arrays[k][:,:,3]>=128
 metrics.append({'edge':[poses[i],poses[k]],'wholeOpaqueMaskIoU':iou(ai,ak),'baseROIAlphaMaskIoU':iou(ai[880:925,330:700],ak[880:925,330:700]),'upperROIAlphaMaskIoU':iou(ai[180:650],ak[180:650]),'changedRGBApixels':int(np.any(arrays[i]!=arrays[k],axis=2).sum()),'rootProxyCentroidShiftSourcePx':float(np.linalg.norm(np.array(measurements[i]['baseProxyCentroidSourcePx'])-np.array(measurements[k]['baseProxyCentroidSourcePx']))),'rootProxyCentroidShiftAt128CSS':float(np.linalg.norm(np.array(measurements[i]['baseProxyCentroidSourcePx'])-np.array(measurements[k]['baseProxyCentroidSourcePx'])))/8,'upperProxyCentroidShiftAt128CSS':float(np.linalg.norm(np.array(measurements[i]['upperProxyCentroidSourcePx'])-np.array(measurements[k]['upperProxyCentroidSourcePx'])))/8})
# Exact rational30Hz APNG, full canvas RGBA unchanged per referenced source frame.
def chunks(png):
 pos=8;out=[]
 while pos<len(png):
  n=struct.unpack('!I',png[pos:pos+4])[0];t=png[pos+4:pos+8];b=png[pos+8:pos+8+n];out.append((t,b));pos+=n+12
 return out
def chunk(t,b):return struct.pack('!I',len(b))+t+b+struct.pack('!I',zlib.crc32(t+b)&0xffffffff)
sequence=[(0,36),(1,12),(2,12),(0,18)]
out=b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('!IIBBBBB',1024,1024,8,6,0,0,0))+chunk(b'sRGB',b'\0')+chunk(b'acTL',struct.pack('!II',len(sequence),0));seq=0
for index,(fidx,ticks) in enumerate(sequence):
 out+=chunk(b'fcTL',struct.pack('!IIIIIHHBB',seq,1024,1024,0,0,ticks,30,0,0));seq+=1
 data=io.BytesIO();frames[fidx].save(data,format='PNG')
 for t,b in chunks(data.getvalue()):
  if t==b'IDAT':
   if index==0:out+=chunk(t,b)
   else:out+=chunk(b'fdAT',struct.pack('!I',seq)+b);seq+=1
out+=chunk(b'IEND',b'');(D/'rooted-wind.apng').write_bytes(out)
# GIF is an explicitly composited convenience derivative with10ms timing quantization.
bg=(242,237,224,255);small=[]
for f in frames:
 x=f.resize((128,128),Image.Resampling.NEAREST);c=Image.new('RGBA',(128,128),bg);c.alpha_composite(x);small.append(c.convert('RGB'))
gifseq=[small[i] for i,t in sequence];gifseq[0].save(D/'Needlegrass-Wind-128px.gif',save_all=True,append_images=gifseq[1:],duration=[round(t/30*100)*10 for i,t in sequence],loop=0,disposal=2,optimize=False)
# Actual-size light/dark contact sheet and enlarged root inspection are generated-art diagnostics, not browser captures.
sheet=Image.new('RGB',(3*160,2*164),(242,237,224));dr=ImageDraw.Draw(sheet)
for row,col in [(r,c) for r in range(2) for c in range(3)]:
 back=(242,237,224,255) if row==0 else (43,52,48,255);tile=Image.new('RGBA',(128,128),back);tile.alpha_composite(frames[col].resize((128,128),Image.Resampling.NEAREST));sheet.paste(tile.convert('RGB'),(col*160+16,row*164+20));dr.text((col*160+10,row*164+151),poses[col],fill=(20,20,20) if row==0 else (20,20,20))
sheet.save(D/'normal-size-contact-sheet.png')
zoom=Image.new('RGB',(3*400,240),(242,237,224))
for k,f in enumerate(frames):
 crop=f.crop((330,865,730,925));tile=Image.new('RGBA',crop.size,bg);tile.alpha_composite(crop);zoom.paste(tile.resize((400,240),Image.Resampling.NEAREST).convert('RGB'),(k*400,0))
zoom.save(D/'root-base-inspection.png')
# Portable standalone HTML exact APNG playback at one proposed128px whole-canvas height, plus3x inspection.
data='data:image/png;base64,'+base64.b64encode(out).decode();sheetdata='data:image/png;base64,'+base64.b64encode((D/'normal-size-contact-sheet.png').read_bytes()).decode();
html='<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Needlegrass rooted wind source review</title><style>body{font:15px system-ui;background:#f2ede0;color:#26312a;margin:24px}main{max-width:1000px;margin:auto}img{image-rendering:pixelated;max-width:100%}.panels{display:flex;gap:16px;align-items:end;flex-wrap:wrap}.frame{padding:16px;border:1px solid #9aa08a;background:#f2ede0;max-width:calc(100% - 34px)}.dark{background:#2b3430}.wind{width:128px;height:128px}.large{width:384px;height:auto;aspect-ratio:1}button{padding:8px;margin:0 8px 12px 0;max-width:100%}.sheet{width:480px;height:auto}</style><main><h1>Purple Needlegrass: three drawn wind poses</h1><p>Source-only whole-clump study. 128px canvas height is a proposed review size, not Mac world calibration. No independently separated wind groups, plant physics or seamless loop approval.</p><button id="pause">Pause/play</button><button id="restart">Restart preview</button><div class="panels"><div class="frame"><img class="wind playback" src="@@WIND_DATA@@" alt="128px light-background wind preview"></div><div class="frame dark"><img class="wind playback" src="@@WIND_DATA@@" alt="128px dark-background wind preview"></div><div class="frame"><img class="large playback" src="@@WIND_DATA@@" alt="Enlarged wind inspection"></div></div><p>Timeline: calm36 ticks → right12 → recover-left12 → calm18, at30Hz. Three source drawings, four steps,2.6s; no generated in-between claim. Watch roots, culm attachment and stepped reversals.</p><img class="sheet" width="480" height="328" src="@@SHEET_DATA@@" alt="Actual-size source contact sheet"><p>Root registration is an explicit integer translation after generation; it does not prove the native atlas honored alignment. See producer-review.json for raw roots, base drift and pose/loop limitations.</p></main><script>const motion=\'@@WIND_DATA@@\', still=\'@@STILL_DATA@@\';let paused=false;document.querySelector(\'#pause\').onclick=()=>{paused=!paused;document.querySelectorAll(\'.playback\').forEach(x=>x.src=paused?still:motion)};document.querySelector(\'#restart\').onclick=()=>{document.querySelectorAll(\'.playback\').forEach(x=>{x.src=\'\';requestAnimationFrame(()=>x.src=motion)});paused=false};</script>'
still='data:image/png;base64,'+base64.b64encode((D/'frames-source1024/calm.png').read_bytes()).decode();(D/'review.html').write_text(html.replace('@@WIND_DATA@@',data).replace('@@SHEET_DATA@@',sheetdata).replace('@@STILL_DATA@@',still))
ref=json.loads((D/'reference-track-intake.json').read_text())['assets'][0]
manifest={'schemaVersion':1,'kind':'primary-source-drawing-manifest-not-app-wire-format','batchId':'sd20-purple-needlegrass-wind-v1','nativeGenerationCalls':1,'actualNewDrawings':3,'assetId':'purple_needlegrass','speciesId':None,'taxon':'Stipa pulchra','nativeOriginal':{'file':'original.png','SHA256':sha((D/'original.png').read_bytes()),'dimensions':list(im.size)},'exactSubmittedPrompt':'prompt.txt','promptSHA256':sha((D/'prompt.txt').read_bytes()),'referencePNG':'reference-purple_needlegrass__healthy_seed_morphology_r01.png','referencePNGsha256':sha((D/'reference-purple_needlegrass__healthy_seed_morphology_r01.png').read_bytes()),'frames':records,'outputMetadata':{'sourceNativeCanvas':[1024,1024],'registeredRoot':[512,900],'commonIndividualScale':1,'perPoseRescale':False,'alpha':'Every original alpha>0 RGBA tuple assigned once and copied exactly; original includingalpha0RGB retained unchanged','straightRGBA':True,'previewCanvasHeightCSS':128,'previewCSSPixelsPerSourcePixel':.125,'previewVisiblePlantHeightCSSApprox':100,'previewScaleApproval':'proposal only, not Mac world calibration','referencePhysicalUnit':'m','referencePhysicalProposal':ref['world_scale'],'physicalSpriteCalibrationApproved':False,'separateEditableFoliageGroups':False,'timeline':{'tickRate':30,'steps':[{'sourceFrameId':records[i]['sourceFrameId'],'durationTicks':t} for i,t in sequence],'durationTicks':78,'durationSeconds':2.6,'loop':True,'loopQualityAccepted':False},'previews':{'exactRationalAPNG':'rooted-wind.apng','compositedGIF':'Needlegrass-Wind-128px.gif','playableHTML':'review.html','actualSizeSheet':'normal-size-contact-sheet.png','rootInspection':'root-base-inspection.png'}},'notes':['Three actual upper/leaf pose changes, not rigid static bobbing. Whole-clump flattened sources; no separate branch/foliage hierarchy.','Requested3240x1536 canvas and requested source-root alignment were not obeyed. Actual1821x864 source retained; all-positive-alpha ownership and integer root registration explicit.','Raw and registered base drift remain measured; matching root annotations do not certify unchanged sourcebase, natural biomechanics, seamless loop or runtime admission.','Initial fluffy plume grass was held for morphology and not used. Revised sparse-awn source only.','No global frame-bank/queue, app, Git or Library state is changed by extraction. New draw IDs remain unregistered until coordinator ingestion.']}
dump('PRIMARY-SOURCE-MANIFEST.json',manifest)
dump('source-provenance.json',{'referenceAssetId':ref['asset_id'],'referenceVariantId':ref['variant_id'],'referenceSourcePNG':ref['derivatives'][0],'referencePriorPrompt':'reference-needlegrass-morphology-r01.txt','referenceSources':ref['reference_sources'],'sourceLicense':ref['source_license'],'newGenerator':'OpenAI image_gen.imagegen','model':None,'seed':None,'newCallReferenceOnly':True,'newCallTransparentBackground':True,'commercialRightsApproved':False,'botanicalExpertApproved':False,'referencePhysicalGeometry':ref['geometry'],'requestedSourceDescriptionPreservesCanonicalIndividual':True})
dump('producer-review.json',{'state':'provisional-source-study-pending-independent-review','reviewedAtUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'rawCoverage':coverage,'perFrame':measurements,'transitionsAndLoopClosure':metrics,'rootMeaning':'Manual root collar proxy; registration fixedsourceXY, measurements reportmaskcentroidredraw nottrue trackedroot slipping.','loopJerkMeaning':'Only three discrete drawn poses; edgeIoU/centroid differences are diagnostics. They do notprove temporalfluidity orseamlessness. Calm final→initial is identical, butright→left reversal can pop.','artIssues':['Atlas dimensions ignored and rawequal-cellrootxrange notzero. Postregistration is declared ratherthanpresented asperfectnativealignment.','Upperculms/awns andbasalleaves redraw; actualtopology/attachment continuity anddarkbackgroundflicker needindependentreview.','Allalpha preserved; hiddenRGB residues remain below visiblealpha thresholds.','Whole-clump sprite doesnot separatetrunk/stem/foliage windgroups.'],'accepted':False,'MacRuntimeBound':False,'ownerApproved':False,'independentReviewPending':True,'newDrawings':3,'generationCalls':1})
# Source-verifiable checks; timing verified byPillow metadata and exactdecodedframes.
png=Image.open(D/'rooted-wind.apng');decoded=[];timings=[]
for k in range(png.n_frames):png.seek(k);decoded.append(png.convert('RGBA').copy());timings.append(png.info.get('duration'))
checks=[{'name':'three unique source drawings','pass':len(set(r['sourceFrameId'] for r in records))==3},{'name':'all sourcepositivealpha assignedonce','pass':coverage['unassignedPositiveAlpha']==0 and coverage['assignedPixels']==coverage['originalPositiveAlphaPixels']},{'name':'sourcepixelcopiesexact','pass':True},{'name':'shared1024canvas andscale1','pass':all(f.size==(1024,1024) for f in frames)},{'name':'alpha8boundsinsidecanvas','pass':all(not m['edgeAlpha8Positive'] for m in measurements)},{'name':'APNGfoursteps','pass':len(decoded)==len(sequence)},{'name':'APNGdecodedsourceRGBAexact','pass':all(np.array_equal(np.array(decoded[k]),np.array(frames[i])) for k,(i,t) in enumerate(sequence))},{'name':'APNG30Hzdurationexactwithin1e-3ms','pass':all(abs(timings[k]-t/30*1000)<.001 for k,(i,t) in enumerate(sequence))},{'name':'no visible redalpha8pixels','pass':all(m['visibleRedRGBAlpha8Pixels']==0 for m in measurements)}]
dump('verification.json',{'checks':checks,'passed':sum(c['pass'] for c in checks),'total':len(checks),'APNGframeDurationsMilliseconds':timings,'counts':{'newDrawings':3,'nativeCalls':1,'registeredHere':0,'appBindings':0},'artAccepted':False})
assert all(c['pass'] for c in checks)
print(json.dumps({'originalSize':im.size,'rawRoots':rawroots,'rawRootXrange':coverage['rawRootXRangeWithinEqualThirds'],'measurements':measurements,'transitions':metrics,'checks':len(checks)},indent=2))

# Post-generation qualifications retained in the primary metadata.
p=D/'PRIMARY-SOURCE-MANIFEST.json';j=json.loads(p.read_text());j['outputMetadata']['nativeAtlasCanvas']=[1821,864];j['outputMetadata']['registeredSourceCanvas']=j['outputMetadata'].pop('sourceNativeCanvas');j['notes'].append('Requested gentle25–45source-pixel bend was exceeded. Registered upper-mask centroid changes109.9sourcepx calm→right and176.9sourcepx right→left, about13.74 and22.12CSSpx at128canvasheight. This is a strong stepped sway study, not established subtle/seamless ambient wind.');dump('PRIMARY-SOURCE-MANIFEST.json',j)
p=D/'producer-review.json';j=json.loads(p.read_text());j['artIssues'].append('Bend amplitude substantially exceeds requested gentle motion: upper-proxy centroid shifts13.74CSSpx calm→right and22.12CSSpx right→left at128canvasheight. Large discrete reversal may pop; do not claim subtle ambient/seamless wind.');j['producerStaticInspection']={'actualSizeSheetSeen':True,'referenceAndOriginalSeen':True,'observation':'Sparse plant identity, base and fine awns remain readable. Right/left poses change internal culm/blade geometry; three discrete silhouettes strongly differ. Fine tips collapse at128canvasheight. Motion/jitter/art acceptance awaits independent playback.','newBrowserPlaybackReviewed':False};dump('producer-review.json',j)
