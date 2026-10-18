from pathlib import Path
from PIL import Image,ImageDraw,__version__ as pillow_version
import numpy as np,json,hashlib,shutil,struct,zlib
P=Path(__file__).parent;R=P.parents[1];A=R/'new-species/sd20-three-canon-v1';S=R/'motion/sd20-anna-phoebe-towhee-v1/california_towhee/actions';B=S;N=112
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def fid(im):return 'frame.sha256.'+hashlib.sha256(f'RGBA8;{im.width}x{im.height};'.encode()+im.tobytes()).hexdigest()
def J(n,v):p=P/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2)+'\n')
def safe(f):
 try:t=f.read_text()
 except UnicodeDecodeError:return True
 import re
 return not re.search(r'libfile_[a-f0-9]{32}|data:image/[^;]+;base64,|https?://[^\s\"<>]*(?:X-Amz-|sig=|token=)',t,re.I)
for d in ['originals','source112','runtime112']:(P/d).mkdir(exist_ok=True)
old=json.loads((S/'texture-review-manifest.json').read_text());blink=json.loads((B/'texture-review-manifest.json').read_text());f=old['frames'][0];world=f['world']['width'];ratio=N/96
spec=[('neutral',S/'open-source1024.png',S/'open-96.png','frame.sha256.8d2819dc208be7c398b643e4ae53e1f0d3f0345896b868f11b1ccc9107761d0a'),('blink',S/'blink-source1024.png',S/'blink-96.png','frame.sha256.2ee2fdc45c9218342bb554f41f80eecd0e2215a12e4102d7df3c13cda1e8fd7f'),('look',S/'look-source1024.png',S/'look-96.png','frame.sha256.5013c42de1a67b177e9c483ab892a7d2fb5b4c2a3ac9bb2acade8b6ed2f91c8f')]
bank=json.loads((R/'frame-bank.json').read_text());entries=[]
def visit(x):
 if isinstance(x,dict):
  if x.get('species')=='california_towhee' and x.get('frameId')in [s[3]for s in spec]:entries.append(x)
  for v in x.values():visit(v)
 elif isinstance(x,list):
  for v in x:visit(v)
visit(bank);assert len(entries)==3
rows=[];images=[];protection=[];indices=((2*np.arange(N)+1)*96)//(2*N)
for name,source,png,sid in spec:
 im=Image.open(source).convert('RGBA');assert fid(im)==sid;entry=next(e for e in entries if e['frameId']==sid);assert entry['fileSha256']==sha(source)
 for src,dest in [(source,f'originals/{name}-source.png'),(png,f'originals/{name}96.png')]:shutil.copyfile(src,P/dest);protection.append({'file':str(src.relative_to(R)),'sha256':sha(src)})
 legacy=Image.open(png);assert legacy.mode=='RGBA' and legacy.size==(96,96);a=np.array(legacy);out=Image.fromarray(a[indices[:,None],indices[None,:]].copy(),'RGBA');out.save(P/'source112'/(name+'.png'));images.append(out)
 proxies=[]
 for c,pt in zip(f['contacts'],[(63,86),(69,86)]):
  oldpoint=[c['x'],c['y']];scaled=[x*ratio for x in oldpoint];oldworldpoint=[x/f['sourcePixelsPerWorldUnit'] for x in oldpoint]
  proxies.append({'id':c['id'],'legacy96Point':oldpoint,'oldDeclaredWorldPoint':oldworldpoint,'continuous112Point':scaled,'proposedInteger112Point':list(pt),'integerRoundingDelta':[pt[i]-scaled[i]for i in range(2)],'newMinusOldWorld':[pt[i]-oldworldpoint[i]for i in range(2)],'exactNNInput96Point':[int(indices[pt[0]]),int(indices[pt[1]])],'source112RGBA':list(out.getpixel(pt)),'uncertaintyOutputPixelsAtLeast':1,'physicalContactAdmitted':False})
 rows.append({'phase':name,'sourceFrameId':sid,'bankEntry':entry,'canonicalSourcePNG':f'originals/{name}-source.png','canonicalSourcePNGsha256':sha(source),'legacy96PNG':f'originals/{name}96.png','legacy96PNGsha256':sha(png),'sourcePNG':f'source112/{name}.png','sourcePNGsha256':sha(P/'source112'/(name+'.png')),'sourceDerivativeRGBAId':fid(out),'newDrawing':False,'footImageProxies':proxies})
# Exact historical raw originals/prompts/receipts retained as provenance; never runtime bitmap frames.
for source,dest in [(A/'original.png','canon-native-original.png'),(A/'prompt.txt','canon-prompt.txt'),(A/'intake-manifest.json','canon-intake-manifest.json'),(A/'visual-review.json','canon-visual-review.json'),(S/'texture-review-manifest.json','legacy-combined-manifest.json'),(S/'source-lineage.json','legacy-source-lineage.json'),(S/'original.png','action-native-original.png'),(S/'prompt.txt','action-prompt.txt'),(S/'call-status.json','action-call-status.json'),(S/'visual-review.json','action-visual-review.json'),(S/'blink-raw-cell.png','blink-native887.png'),(S/'look-raw-cell.png','look-native887.png')]:
 assert safe(source),str(source);shutil.copyfile(source,P/'originals'/dest);protection.append({'file':str(source.relative_to(R)),'sha256':sha(source)})
arrays=[np.array(i)for i in images];masks=[a[:,:,3]>=128 for a in arrays];allopaque=np.concatenate([a[:,:,:3][m]for a,m in zip(arrays,masks)]);q=np.array(Image.fromarray(allopaque.reshape(1,-1,3),'RGB').quantize(colors=63,method=Image.Quantize.MEDIANCUT,dither=Image.Dither.NONE).convert('RGB')).reshape(-1,3);cursor=0;runtimes=[]
for r,a,mask in zip(rows,arrays,masks):
 n=int(mask.sum());b=np.zeros((N,N,4),np.uint8);b[:,:,:3][mask]=q[cursor:cursor+n];cursor+=n;b[:,:,3][mask]=255;im=Image.fromarray(b,'RGBA');name=r['phase'];im.save(P/'runtime112'/(name+'.png'));runtimes.append(im);r['runtimePNG']=f'runtime112/{name}.png';r['runtimePNGsha256']=sha(P/r['runtimePNG']);r['runtimeDerivativeRGBAId']=fid(im);r['thresholdFringePixelsRemoved']=int(((a[:,:,3]>0)&~mask).sum());r['runtimeFootProxies']=[{'point':c['proposedInteger112Point'],'RGBA':list(im.getpixel(tuple(c['proposedInteger112Point']))),'admittedContact':False}for c in r['footImageProxies']]
# Explicit neutral-only idle is an authored projection; preserve original blink/look timings and looping.
clips=[{'id':'idle','tickRate':30,'loop':True,'frames':[{'phase':'neutral','durationTicks':42}],'timingOrigin':'explicit authored neutral-only42tickhold projected from first inherited entry; not biology or unchanged combined legacy clip'},{'id':'blink','tickRate':30,'loop':True,'frames':[{'phase':'neutral','durationTicks':42},{'phase':'blink','durationTicks':3},{'phase':'neutral','durationTicks':24}],'timingOrigin':'legacy combined positions0..2 preserve42/3/24 at30Hz; separate named proposal, old binding unchanged'},{'id':'look','tickRate':30,'loop':True,'frames':[{'phase':'neutral','durationTicks':24},{'phase':'look','durationTicks':18},{'phase':'neutral','durationTicks':27}],'timingOrigin':'legacy combined positions2..4 preserve24/18/27 at30Hz; separate named proposal, old binding unchanged'}]
manifest={'kind':'checkpoint8 existing California Towhee complete common family proposal','nativeCalls':0,'newDrawings':0,'newSourceSlots':0,'existingDrawingsReused':3,'frames':rows,'oldWorld':[world,world],'oldDensity':f['sourcePixelsPerWorldUnit'],'newWorld':[N,N],'newDensity':1,'newCanvas':[N,N],'worldCanvasRoundingDelta':N-world,'worldCanvasRoundingPercent':(N/world-1)*100,'oldPivot96':f['pivot'],'oldPivotWorld':[57/f['sourcePixelsPerWorldUnit'],75/f['sourcePixelsPerWorldUnit']],'continuousScaledPivot112':[57*ratio,75*ratio],'integerPivot':[67,88],'pivotIntegerRoundingDelta':[67-57*ratio,88-75*ratio],'pivotNewMinusOldWorld':[67-57/f['sourcePixelsPerWorldUnit'],88-75/f['sourcePixelsPerWorldUnit']],'sampler':'whole96canvas→112 using floor((output+.5)*96/112) exactintegerRGBAchannelcopy, no crop/fit/snap/paint/alpha cleanup','runtimeDerivative':{'alphaThreshold':128,'alphaValues':[0,255],'transparentRGBA':[0,0,0,0],'commonOpaquePaletteLimit':63,'paletteAlgorithm':'MEDIANCUT on all3 surviving sourceRGB samples, neutral/blink/look row-major order','dither':'NONE','PillowVersion':pillow_version},'candidateArea':3*N*N,'clips':clips,'contacts':[],'geometryReviewed':False,'supportWorld':None,'existingHistoricalRegistration':'Existing neutral source is registered1024 from original canon pack. Blink/look source887cells historically share call-wide887→816 nearest scale and placement34,84 onto1024. Native cells, original, source-lineage and registeredsources retained; no newregistration or fit.','sourceVisualAcceptance':'PENDING independent112worldreview','structuralAcceptance':'PENDING same shared structural runner','runtimeFullManifestValidation':False,'productionPinsAndFidelityLabels':'UNSUPPLIED','MacAdmission':False,'packetBindingReady':False,'activation':'none'}
J('family-source-manifest.json',manifest);J('legacy-protection.json',{'files':protection,'noLegacyBindingsModified':True});J('preflight.json',{'status':'assembled zero-call3existing-drawing source family; structural check/independent review pending','speciesId':'california_towhee','sourceIDs':[r['sourceFrameId']for r in rows],'source96PNGs':[r['legacy96PNGsha256']for r in rows],'bodyScaleCommonCanvasOnly':True,'oldWorld':world,'newCanvas':[N,N],'density':1,'pivot':[67,88],'area':37632,'nativeCalls':0,'newDrawings':0,'newSlots':0,'canonicalInput':'canonical-input.json','sharedRunner':str(R/'validation/shared-structural-check.mjs'),'repository':'/workspace/runtime-contract-checkpoint8','contacts':[],'geometryReviewed':False,'supportWorld':None,'MacAdmission':False})
repo=Path('/workspace/runtime-contract-checkpoint8');J('canonical-input.json',{'expectedPackageSHA256':sha(repo/'src/lib/server/asset-pipeline/package.ts'),'expectedCanonicalSHA256':sha(repo/'src/lib/server/pipeline/canonical.ts'),'canvas':{'width':N,'height':N},'logicalPixelSize':1,'paletteLimit':64,'frames':[{'phase':r['phase'],'png':r['runtimePNG'],'PNGsha256':r['runtimePNGsha256'],'decodedRGBAId':r['runtimeDerivativeRGBAId']}for r in rows]})
# Source-art comparisons and previews, not browser captures.
sheet=Image.new('RGB',(N*3,(N+22)*4),'#d9d4bd');draw=ImageDraw.Draw(sheet)
for row,(ims,bg,typ)in enumerate([(images,'#d9d4bd','RGBA'),(runtimes,'#d9d4bd','BINARY'),(images,'#17221f','RGBA'),(runtimes,'#17221f','BINARY')]):
 for i,(r,im)in enumerate(zip(rows,ims)):
  tile=Image.new('RGBA',(N,N),bg);tile.alpha_composite(im);sheet.paste(tile.convert('RGB'),(i*N,row*(N+22)+22));draw.text((i*N+3,row*(N+22)+4),r['phase']+' '+typ,fill='white'if row>=2 else '#24342b')
sheet.save(P/'normal112-light-dark-source-runtime.png')
for name,rect in [('head',(67,25,92,49)),('feet',(55,77,77,91))]:
 w=(rect[2]-rect[0])*12;h=(rect[3]-rect[1])*12;out=Image.new('RGB',(w*3,(h+23)*2),'#d9d4bd');d=ImageDraw.Draw(out)
 for row,ims in enumerate([images,runtimes]):
  for i,(r,im)in enumerate(zip(rows,ims)):
   tile=Image.new('RGBA',(N,N),'#d9d4bd');tile.alpha_composite(im);out.paste(tile.crop(rect).resize((w,h),Image.Resampling.NEAREST).convert('RGB'),(i*w,row*(h+23)+23));d.text((i*w+3,row*(h+23)+4),r['phase']+(' source'if row==0 else ' binary'),fill='#24342b')
 out.save(P/(name+'-inspection.png'))
def chunk(k,d):return struct.pack('>I',len(d))+k+d+struct.pack('>I',zlib.crc32(k+d)&0xffffffff)
for name,idx,ticks in [('blink',[0,1,0],[42,3,24]),('look',[0,2,0],[24,18,27])]:
 for typ,ims in [('source',images),('runtime',runtimes)]:
  png=b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',N,N,8,6,0,0,0))+chunk(b'acTL',struct.pack('>II',3,1));seq=0
  for i,(index,t)in enumerate(zip(idx,ticks)):
   png+=chunk(b'fcTL',struct.pack('>IIIIIHHBB',seq,N,N,0,0,t,30,0,0));seq+=1;a=np.array(ims[index]);data=zlib.compress(b''.join(b'\0'+a[y].tobytes()for y in range(N)),9)
   if i==0:png+=chunk(b'IDAT',data)
   else:png+=chunk(b'fdAT',struct.pack('>I',seq)+data);seq+=1
  (P/(name+'-'+typ+'.apng')).write_bytes(png+chunk(b'IEND',b''))
print(json.dumps({'sourceIDs':[r['sourceFrameId']for r in rows],'worldDelta':manifest['worldCanvasRoundingDelta'],'worldPercent':manifest['worldCanvasRoundingPercent'],'pivot':[67,88],'nativeCalls':0,'newDrawings':0,'canonicalInput':str(P/'canonical-input.json')}))
