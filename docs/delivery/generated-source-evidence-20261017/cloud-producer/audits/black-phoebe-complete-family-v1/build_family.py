from pathlib import Path
from PIL import Image,ImageDraw,__version__ as pillow_version
import numpy as np,json,hashlib,shutil,struct,zlib
P=Path(__file__).parent;A=P.parents[1]/'motion/sd20-phoebe-actions-v1';L=P.parents[1]/'motion/sd20-black-phoebe-look-v1';N=91
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def fid(im):return 'frame.sha256.'+hashlib.sha256(f'RGBA8;{im.width}x{im.height};'.encode()+im.tobytes()).hexdigest()
def J(n,v):p=P/n;p.parent.mkdir(exist_ok=True,parents=True);p.write_text(json.dumps(v,indent=2)+'\n')
for d in ['originals','source91','runtime91']: (P/d).mkdir(exist_ok=True)
blinkprofile=json.loads((A/'blink-manifest.json').read_text());lookprofile=json.loads((L/'texture-review-manifest.json').read_text());old=blinkprofile['frames'][0];oldworld=old['world']['width'];ratio=91/96
canonical=[('neutral',A/'neutral-source1024.png',A/'frames96/neutral.png','frame.sha256.afdb316304688a04c8ea5130d42685c0a6bb74e922a8d0c5ac34637dd720850f'),('blink',A/'frames1024/closed.png',A/'frames96/closed.png','frame.sha256.9b499790521d1fa4a00fae9a466ce7ad235cae606d48659c4d9078658229aca3'),('look',L/'look-native.png',L/'look96.png','frame.sha256.7a9195b40f85229be462769920e8726be7f97fe33c7ddeb66b293144957e985b')]
rows=[];sourceframes=[];protection=[]
for name,source,png,sid in canonical:
 im=Image.open(source).convert('RGBA');assert fid(im)==sid;shutil.copyfile(source,P/'originals'/(name+'-bank-source.png'));shutil.copyfile(png,P/'originals'/(name+'96.png'));legacy=Image.open(png);assert legacy.mode=='RGBA' and legacy.size==(96,96)
 a=np.array(legacy);indices=((2*np.arange(91)+1)*96)//182;b=a[indices[:,None],indices[None,:]].copy();out=Image.fromarray(b,'RGBA');out.save(P/'source91'/(name+'.png'));sourceframes.append(out)
 contacts=[]
 for c,pt in zip(old['contacts'],[(50,70),(55,70)]):contacts.append({'legacyContactId':c['id'],'legacyPixel':[c['x'],c['y']],'proposed91Pixel':list(pt),'exactNNInputPixel':[int(indices[pt[0]]),int(indices[pt[1]])],'source91RGBA':list(out.getpixel(pt)),'admittedContact':False,'uncertaintyPixelsAtLeast':1})
 row={'phase':name,'sourceFrameId':sid,'canonicalBankSourcePNG':'originals/'+name+'-bank-source.png','canonicalBankSourcePNGsha256':sha(source),'legacy96PNG':'originals/'+name+'96.png','legacy96PNGsha256':sha(png),'source91PNG':'source91/'+name+'.png','source91PNGsha256':sha(P/'source91'/(name+'.png')),'source91DerivativeRGBAId':fid(out),'newDrawing':False,'generationCalls':0,'footRegionProxies':contacts}
 if name=='blink':
  raw=A/'native-cells/closed.png';shutil.copyfile(raw,P/'originals/blink-native724.png');cell=Image.open(raw).convert('RGBA');assert fid(cell)=='frame.sha256.10446a4ce450e999b4f0551d7017e30b0540f0b17424e99ecb3117dc1a14f6e0';registered=Image.new('RGBA',(1024,1024));registered.paste(cell,(100,161));assert registered.tobytes()==im.tobytes();row['nativeAliasSameExistingDrawing']={'sourceFrameId':fid(cell),'PNG':'originals/blink-native724.png','PNGsha256':sha(raw),'historicalRegistrationTranslation':[100,161],'registeredBankSourceId':sid,'aliasIsAdditionalDrawing':False,'historicalDerivationByteExactVerified':True};protection.append({'file':str(raw.relative_to(P.parents[1])),'sha256':sha(raw)})
 row['bankResolution']={'entryFrameId':row['nativeAliasSameExistingDrawing']['sourceFrameId'],'referenceField':'derivation.registeredDerivativeFrameId','familyReferenceIsRegisteredAliasOfSameDrawing':True} if name=='blink' else {'entryFrameId':sid,'referenceField':'frameId','familyReferenceIsRegisteredAliasOfSameDrawing':False}
 rows.append(row)
 for f in [source,png]:protection.append({'file':str(f.relative_to(P.parents[1])),'sha256':sha(f)})
# One common opaque63RGB palette learned over all three surviving images, no dither.
arrays=[np.array(im) for im in sourceframes];masks=[a[:,:,3]>=128 for a in arrays];opaque=np.concatenate([a[:,:,:3][mask] for a,mask in zip(arrays,masks)],axis=0);colors=Image.fromarray(opaque.reshape(1,-1,3),'RGB').quantize(colors=63,method=Image.Quantize.MEDIANCUT,dither=Image.Dither.NONE).convert('RGB');quant=np.array(colors).reshape(-1,3);cursor=0;runtime=[]
for r,a,mask in zip(rows,arrays,masks):
 n=int(mask.sum());b=np.zeros((91,91,4),np.uint8);b[:,:,:3][mask]=quant[cursor:cursor+n];cursor+=n;b[:,:,3][mask]=255;im=Image.fromarray(b,'RGBA');name=r['phase'];im.save(P/'runtime91'/(name+'.png'));runtime.append(im);r['runtime91PNG']='runtime91/'+name+'.png';r['runtime91PNGsha256']=sha(P/'runtime91'/(name+'.png'));r['runtime91DerivativeRGBAId']=fid(im);r['runtimeThresholdFringePixelsRemoved']=int(((a[:,:,3]>0)&~mask).sum());r['runtimeFootProxies']=[{'point':x['proposed91Pixel'],'RGBA':list(im.getpixel(tuple(x['proposed91Pixel']))),'physicalSupportApproved':False} for x in r['footRegionProxies']]
clips=[{'id':'idle','tickRate':30,'loop':True,'frames':[{'phase':'neutral','durationTicks':90}]},{'id':'blink','tickRate':30,'loop':True,'frames':[{'phase':'neutral','durationTicks':90},{'phase':'blink','durationTicks':3},{'phase':'neutral','durationTicks':90}]},{'id':'look','tickRate':30,'loop':False,'frames':[{'phase':'neutral','durationTicks':30},{'phase':'look','durationTicks':12},{'phase':'neutral','durationTicks':30}]}]
proof={'kind':'zero-call existing three-drawing source family density1 proposal','nativeCalls':0,'newDrawings':0,'existingDistinctDrawingsReused':3,'canonicalBankSourceIDs':[r['sourceFrameId']for r in rows],'frames':rows,'legacyDeclaredWorld':oldworld,'legacyObservedBrowserCSS':90.9375,'legacyCSSIsRoundingNotContractWorld':True,'legacyDensity':old['sourcePixelsPerWorldUnit'],'newCanvas':[91,91],'newWorld':[91,91],'newDensity':1,'worldRoundingPercent':(91/oldworld-1)*100,'sampler':'full96→91 explicitfloor-center nearest straightRGBA channel copy; no perpose fit/translate/paint/alpha cleanup','continuousScaledPivot':{'x':57*ratio,'y':75*ratio},'integerPivot':{'x':54,'y':71},'pivotRoundingDeltaWorld':{'x':54-57*ratio,'y':71-75*ratio},'contacts':[],'geometryReviewed':False,'supportWorld':None,'candidateSourceArea':3*91*91,'runtimeArea':3*91*91,'runtimeDerivative':{'alphaThreshold':128,'alphaValues':[0,255],'transparentRGBA':[0,0,0,0],'commonOpaqueColorLimit':63,'dither':'NONE','paletteBasis':'all three source91opaque-surviving samples in neutral/blink/look row-major order','PillowVersion':pillow_version,'newDrawings':0},'clips':clips,'legacyTimingBindings':{'idle':'lookprofile.clips.idle90ticks; unchanged awake only','blink':'originalblink-manifest idle90/3/90 looping re-expressed as separate authored blink proposal; no legacy binding edit','look':'original look30/12/30one-shot'},'legacyWarmBrownPlumageLimitRetained':True,'sourceFamilyVisualAcceptance':'PENDING independent91normalreview','runtimeFullSchema':'NOT_RUN','MacAdmission':False,'productionPins':'UNSUPPLIED','activation':'none','packetBindingReady':False}
J('family-source-manifest.json',proof)
for f,name in [(A/'source-lineage.json','legacy-source-lineage.json'),(A/'blink-manifest.json','legacy-blink-manifest.json'),(L/'texture-review-manifest.json','legacy-look-manifest.json'),(L/'PRIMARY-SOURCE-MANIFEST.json','legacy-look-primary.json'),(L/'independent-review.json','legacy-look-independent-review.json'),(L/'independent-review.md','legacy-look-independent-review.md'),(L/'SEALED-STATUS.json','legacy-look-sealed-status.json')]:shutil.copyfile(f,P/'originals'/name);protection.append({'file':str(f.relative_to(P.parents[1])),'sha256':sha(f)})
assert sha(L/'independent-review.json')=='b8a73f5abcc3720bf84bf15c2d8b2813aa42fc336882255050de864d93872b41'
J('legacy-protection.json',{'allLegacyBindingsUntouched':True,'files':protection})
J('preflight.json',{'state':'sourcefamily assembled;91normalindependentreview and exactcodec pending','nativeCalls':0,'newDrawings':0,'existingDrawingCount':3,'folder':str(P),'manifest':'family-source-manifest.json','sourceCanvas':[91,91],'density':1,'plannedRuntimeArea':24843,'frames':[{'phase':r['phase'],'sourceFrameId':r['sourceFrameId'],'nativeAlias':r.get('nativeAliasSameExistingDrawing')}for r in rows],'worldCorrection':'declared90.94736842105263 vs browser90.9375CSS; new91world explicit','clipSchedules':[{'id':c['id'],'ticks':[x['durationTicks']for x in c['frames']]}for c in clips],'legacySourceBodyRegistrationUnchanged':True,'geometryReviewed':False,'supportWorld':None,'MacAdmission':False})
# Actual91px source and runtime comparison, light/dark; no screenshots.
sheet=Image.new('RGB',(273,113*4),'#d9d4bd');dr=ImageDraw.Draw(sheet)
for row,(images,bg,label) in enumerate([(sourceframes,'#d9d4bd','SOURCE'),(runtime,'#d9d4bd','BINARY'),(sourceframes,'#17221f','SOURCE'),(runtime,'#17221f','BINARY')]):
 for i,(name,im)in enumerate(zip(['neutral','blink','look'],images)):
  tile=Image.new('RGBA',(91,91),bg);tile.alpha_composite(im);x=i*91;y=row*113;sheet.paste(tile.convert('RGB'),(x,y+22));dr.text((x+2,y+4),name+' '+label,fill='white' if row>=2 else '#24342b')
sheet.save(P/'normal91-light-dark-source-runtime.png')
for label,rect in [('eye',(53,23,76,44)),('feet',(44,63,62,73))]:
 w=(rect[2]-rect[0])*10;h=(rect[3]-rect[1])*10;out=Image.new('RGB',(w*3,(h+23)*2),'#d9d4bd');dr=ImageDraw.Draw(out)
 for row,images in enumerate([sourceframes,runtime]):
  for i,(r,im) in enumerate(zip(rows,images)):
   bg=Image.new('RGBA',(91,91),'#d9d4bd');bg.alpha_composite(im);out.paste(bg.crop(rect).resize((w,h),Image.Resampling.NEAREST).convert('RGB'),(i*w,row*(h+23)+23));dr.text((i*w+3,row*(h+23)+4),r['phase']+(' source' if row==0 else ' binary'),fill='#24342b')
 out.save(P/(label+'-inspection.png'))
# RGBA APNG one-shot proofs; clip loop declarations remain in source manifest.
def chunk(k,d):return struct.pack('>I',len(d))+k+d+struct.pack('>I',zlib.crc32(k+d)&0xffffffff)
for name,inds,ticks in [('blink',[0,1,0],[90,3,90]),('look',[0,2,0],[30,12,30])]:
 for variant,ims in [('source',sourceframes),('runtime',runtime)]:
  png=b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',91,91,8,6,0,0,0))+chunk(b'acTL',struct.pack('>II',3,1));seq=0
  for i,(idx,t) in enumerate(zip(inds,ticks)):
   png+=chunk(b'fcTL',struct.pack('>IIIIIHHBB',seq,91,91,0,0,t,30,0,0));seq+=1;a=np.array(ims[idx]);data=zlib.compress(b''.join(b'\0'+a[y].tobytes()for y in range(91)),9)
   if i==0:png+=chunk(b'IDAT',data)
   else:png+=chunk(b'fdAT',struct.pack('>I',seq)+data);seq+=1
  (P/(name+'-'+variant+'.apng')).write_bytes(png+chunk(b'IEND',b''))
print(json.dumps({'sourceIDs':proof['canonicalBankSourceIDs'],'worldRoundingPercent':proof['worldRoundingPercent'],'pivot':proof['integerPivot'],'area':24843,'nativeCalls':0,'newDrawings':0}))
