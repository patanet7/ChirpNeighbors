"""Deterministic whole-canvas runtime derivative. Zero native calls/new drawings."""
from pathlib import Path
from PIL import Image,ImageDraw,__version__ as pillow_version
import numpy as np,json,hashlib,shutil,datetime,zlib,struct
P=Path(__file__).parent;S=P.parents[1]/'motion/sd20-crow-neutral-blink-v1';R=P/'source-reference';R.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def J(n,o):(P/n).write_text(json.dumps(o,indent=2)+'\n')
def fid(im):return 'frame.sha256.'+hashlib.sha256(f'RGBA8;{im.width}x{im.height};'.encode()+im.tobytes()).hexdigest()
expected={'neutral192.png':'52b7e13d4621706c983a027b60d36340b9068800247b25ef6c84390e41c54f05','neutral-source1024.png':'64a3199e6509cccf3e578c46e796246b5fca35b25e94d5d54bf88fab31c3bcec','original.png':'4bbfadfd874fdac874ee11b8408336b17117a7c161b4a6e375366ad71292fbf8'}
source_id='frame.sha256.54329ae7d715c698c9be4e025d0841adc4bff478fa10b080a88d8d141db3ffd5'
for n,h in expected.items():assert sha(S/n)==h;shutil.copyfile(S/n,R/n)
for n in ['texture-review-manifest.json','PRIMARY-SOURCE-MANIFEST.json','prompt.txt']:shutil.copyfile(S/n,R/n)
assert fid(Image.open(R/'neutral-source1024.png').convert('RGBA'))==source_id
old=Image.open(R/'neutral192.png');assert old.mode=='RGBA' and old.size==(192,192)
oldprofile=json.loads((R/'texture-review-manifest.json').read_text());base=oldprofile['frames'][0]
N=186;resized=old.resize((N,N),Image.Resampling.NEAREST);a=np.array(resized);mask=a[:,:,3]>=128
# Quantize only opaque-surviving RGB samples; transparent pixels do not influence palette.
pixels=Image.fromarray(a[:,:,:3][mask].reshape(1,-1,3),'RGB');quant=pixels.quantize(colors=63,method=Image.Quantize.MEDIANCUT,dither=Image.Dither.NONE).convert('RGB')
b=np.zeros((N,N,4),dtype=np.uint8);b[:,:,:3][mask]=np.array(quant).reshape(-1,3);b[:,:,3][mask]=255
out=Image.fromarray(b,'RGBA');out.save(P/'ground-idle186.png');outid=fid(out)
assert len(set(map(tuple,b.reshape(-1,4))))<=64 and set(np.unique(b[:,:,3]))=={0,255}
assert np.all(b[:,:,:3][~mask]==0)
ratio=N/192;oldworld=base['world']['width'];world=N;pivot={k:v*ratio for k,v in base['pivot'].items()}
# Derive exact inverse NN sample lookup with the same Pillow operation, no guessed rounding.
lookup=np.array(Image.fromarray(np.arange(192,dtype=np.int32)[None,:],'I').resize((N,1),Image.Resampling.NEAREST))[0]
points=[]
for label,(x,y) in [('old-foot-a',(99,146)),('old-foot-b',(124,144)),('near-claw',(109,149))]:
 nx=int(np.argmin(abs(lookup-x)));ny=int(np.argmin(abs(lookup-y)));sx=int(lookup[nx]);sy=int(lookup[ny]);rgba=a[ny,nx].tolist();after=b[ny,nx].tolist()
 points.append({'label':label,'oldReferencePixel':[x,y],'oldRGBA':list(old.getpixel((x,y))),'continuousCanvasScaledPoint':[x*ratio,y*ratio],'proposedDerivativePixel':[nx,ny],'exactNNInputPixel':[sx,sy],'beforeThresholdRGBA':rgba,'afterThresholdRGBA':after,'survivesAlpha128':after[3]==255,'uncertainty':'at least1pixel raster/anatomical; proxy correspondence requires visual review, not pressure/sole support'})
roi=np.zeros(mask.shape,dtype=bool);roi[132:151,86:130]=True
lost=(a[:,:,3]>0)&~mask;toelost=lost&roi
bbox=lambda arr:([int(np.where(arr)[1].min()),int(np.where(arr)[0].min()),int(np.where(arr)[1].max()+1),int(np.where(arr)[0].max()+1)] if arr.any() else None)
receipt={'kind':'deterministic-runtime-derivative','builtAtUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'nativeCalls':0,'newDrawings':0,'sourceFrameIdRetained':source_id,'derivativeDecodedRGBAId':outid,'derivativeIsNewPrimarySource':False,'sourceFiles':{str(p.relative_to(P)):sha(p) for p in sorted(R.iterdir())},'output':{'file':'ground-idle186.png','PNGsha256':sha(P/'ground-idle186.png'),'decodedRGBAId':outid,'size':[186,186]},'steps':[{'operation':'wholecanvas-nearest-resize','from':[192,192],'to':[186,186],'ratio':ratio,'bodyBBoxFit':False,'translation':[0,0]},{'operation':'alpha-threshold','opaqueWhenAlphaAtLeast':128,'opaqueAlpha':255,'transparentAlpha':0,'transparentRGB':[0,0,0]},{'operation':'opaque-only-RGB-median-cut','maximumOpaqueColors':63,'dither':'NONE','PillowVersion':pillow_version,'transparentColors':1,'deterministicPixelOrder':'row-major surviving opaque samples'}],'oldWorld':oldworld,'newWorld':186,'worldCanvasRoundingPercent':(186/oldworld-1)*100,'oldDensity':base['sourcePixelsPerWorldUnit'],'newDensity':1,'oldPivot':base['pivot'],'newContinuousPivot':pivot,'pivotRoundingPerformed':False,'oldFootReferences':base['contacts'],'pointMappings':points,'geometryReviewed':False,'supportWorld':None,'plantarSoleOrPressureClaim':False,'canonicalRuntimeZod':'NOT_RUN','currentExpectedFullSchema':'PENDING','appBound':False}
J('transformation-receipt.json',receipt)
f={'id':'crow-ground-idle-runtime186','sourceRect':{'x':0,'y':0,'width':N,'height':N},'canvas':{'width':N,'height':N},'trim':{'x':0,'y':0},'pivot':pivot,'contacts':[],'world':{'width':N,'height':N},'sourcePixelsPerWorldUnit':1}
v={'schemaVersion':1,'profile':'chirp-texture-review-v1','scope':'review-only','approval':'unreviewed','activation':'none','source':{'sha256':sha(P/'ground-idle186.png'),'creator':'deterministic derivative of existing Crow ground neutral','tool':'Pillow wholecanvas nearest, alpha128, opaque63RGB median-cut/no-dither','toolVersion':pillow_version,'rights':'unreviewed','fidelity':'unreviewed'},'atlas':{'width':N,'height':N,'alpha':'straight-rgba8','colorSpace':'srgb'},'frames':[f],'clips':[{'id':'idle','tickRate':30,'loop':True,'frames':[{'frameId':f['id'],'durationTicks':120}]}]}
J('runtime-idle-proposal.json',v)
J('runtime-binding-proposal.json',{'kind':'source-only runtime compatibility proposal','sourceFrameId':source_id,'derivativeDecodedRGBAId':outid,'newDrawings':0,'nativeCalls':0,'manifest':{'file':'runtime-idle-proposal.json','sha256':sha(P/'runtime-idle-proposal.json')},'bitmap':{'file':'ground-idle186.png','sha256':sha(P/'ground-idle186.png'),'width':N,'height':N},'runtimeBitmapFiles':['ground-idle186.png'],'frameCount':1,'decodedAnimationArea':N*N,'oneGroundIdleOnly':True,'unusedBlinkAtlasIncluded':False,'geometryReviewed':False,'supportWorld':None,'contactProxies':'diagnostic only, transformation-receipt.json pointMappings; not admitted foot contacts','canonicalRuntimeZod':'NOT_RUN','currentExpectedFullSchema':'PENDING','packetBindingReady':False,'appBound':False,'activation':'none'})
# Source-art composites only; no browser capture bytes.
W=186;comp=Image.new('RGB',(W*2,2*(W+22)),'#d9d4bd');dr=ImageDraw.Draw(comp)
for row,bg in enumerate(['#d9d4bd','#17221f']):
 for col,(im,label) in enumerate([(resized,'SOURCE NN, PARTIAL ALPHA'),(out,'BINARY ALPHA / <=64 COLORS')]):
  tile=Image.new('RGBA',(W,W),bg);tile.alpha_composite(im);comp.paste(tile.convert('RGB'),(col*W,row*(W+22)+22));dr.text((col*W+2,row*(W+22)+4),label,fill='white' if row else '#24342b')
comp.save(P/'normal-light-dark-source-comparison.png')
cr=(86,132,132,153);size=(552,252);sheet=Image.new('RGB',(size[0]*3,size[1]+28),'#d9d4bd');d=ImageDraw.Draw(sheet)
for i,(im,label) in enumerate([(resized,'DIRECT NN BEFORE THRESHOLD'),(out,'BINARY/PALETTE DERIVATIVE'),(out,'DERIVATIVE + DIAGNOSTIC PROXIES')]):
 tile=Image.new('RGBA',im.size,'#d9d4bd');tile.alpha_composite(im);tile=tile.crop(cr).resize(size,Image.Resampling.NEAREST);sheet.paste(tile.convert('RGB'),(i*size[0],28));d.text((i*size[0]+4,6),label,fill='#24342b')
 if i==2:
  for j,p in enumerate(points):
   x,y=p['proposedDerivativePixel'];cx=i*size[0]+(x-cr[0]+.5)*12;cy=28+(y-cr[1]+.5)*12;d.ellipse((cx-5,cy-5,cx+5,cy+5),outline='#ff4444',width=2);d.text((cx+6,cy-10),str(j+1),fill='#b00000')
sheet.save(P/'contact-threshold-inspection.png')
J('threshold-loss-diagnostics.json',{'alpha128OpaquePixels':int(mask.sum()),'nonzeroAlphaBefore':int((a[:,:,3]>0).sum()),'nonzeroFringeRemoved':int(lost.sum()),'removedFringeBBox':bbox(lost),'fixedFootROIPixels':[86,132,130,151],'footROINonzeroFringeRemoved':int(toelost.sum()),'footROIAlphaAtLeast128Unchanged':True,'footROIThresholdLostPixelList':[[int(x),int(y),int(a[y,x,3])] for y,x in zip(*np.where(toelost))],'pointMappings':points,'limits':'Threshold removes native antialias fringes, including toes. Wholecanvas NN can omit original samples. No toe reconstruction, painting, per-foot translation or morphology. Surviving positive proxies do not establish entire claw continuity/support.'})
# A single rendered frame held120ticks; APNG is unnecessary for a static sprite.
print(json.dumps({'outputPNGsha256':sha(P/'ground-idle186.png'),'derivativeRGBAId':outid,'colors':len(set(map(tuple,b.reshape(-1,4)))),'decodedArea':N*N,'worldRoundingPercent':receipt['worldCanvasRoundingPercent'],'pointMappings':points,'footFringeRemoved':int(toelost.sum())}))
