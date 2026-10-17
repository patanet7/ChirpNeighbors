from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib,base64
P=Path(__file__).parent;(P/'derivatives').mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rid(im):return 'frame.sha256.'+hashlib.sha256(f'RGBA8;{im.width}x{im.height};'.encode()+im.tobytes()).hexdigest()
def write(n,o):(P/n).write_text(json.dumps(o,indent=2)+'\n')
s=Image.open(P/'frames/closed-source1254.png').convert('RGBA');a=np.array(s)
reg=Image.new('RGBA',s.size);reg.paste(s,(-1,-4));r=np.array(reg)
assert np.count_nonzero(a[:,:,3])==np.count_nonzero(r[:,:,3]) and a[:,:,3].sum()==r[:,:,3].sum()
assert np.array_equal(a[4:,1:],r[:-4,:-1])
reg.save(P/'derivatives/closed-registered-source1254.png');out=reg.resize((192,192),Image.Resampling.NEAREST);out.save(P/'derivatives/closed-registered192.png')
old=Image.open(P/'reused/awake192.png').convert('RGBA');native=Image.open(P/'frames/closed192.png').convert('RGBA')
def feet(im):
 z=np.array(im);sub=z[138:155,98:132,3]>=128;y,x=np.where(sub);return {'roi':[98,138,132,155],'centroid':[float(x.mean()+98),float(y.mean()+138)],'bottom':int(y.max()+138),'pixelCount':int(len(x)),'qualification':'coarse lower-foot ROI; no anatomical correspondence proof'}
oldfoot=feet(old);nf=feet(native);rf=feet(out)
info={'schema':'chirp-whole-pose-registration-study-v1','newDrawings':0,'primaryNativeSourcePNG':'frames/closed-source1254.png','primaryNativeSHA256':sha(P/'frames/closed-source1254.png'),'nativeIntegerTranslation':[-1,-4],'nativeOriginalContactProxy':[754,982],'oldReferenceContactProxy':[615,799],'oldReferenceContactProxyConvertedToNative':[615/1024*1254,799/1024*1254],'registeredContactProxy':[753,978],'registeredProxyResidualWorld':[float((753-615/1024*1254)*192/1254/1.1),float((978-799/1024*1254)*192/1254/1.1)],'contactQualification':'Same presumed lowest foot-tip area by location; anatomical identity is unverified. One whole-pose origin adjustment only, not individual toe fitting.','allNonzeroAlphaPixelsPreserved':True,'allAlphaSumPreserved':True,'nativeAlphaCount':int(np.count_nonzero(a[:,:,3])),'nativeAlphaSum':int(a[:,:,3].sum()),'sourceDerivativePNG':'derivatives/closed-registered-source1254.png','sourceDerivativeSHA256':sha(P/'derivatives/closed-registered-source1254.png'),'sourceDerivativeRGBAId':rid(reg),'outputPNG':'derivatives/closed-registered192.png','outputPNGsha256':sha(P/'derivatives/closed-registered192.png'),'outputRGBAId':rid(out),'sourceToOutputScale':192/1254,'sourcePixelsPerWorldUnit':1.1,'bodyScaleFit':False,'pixelPainting':False,'feetBefore':nf,'feetAfter':rf,'feetReference':oldfoot,'beforeBottomDeltaWorld':(nf['bottom']-oldfoot['bottom'])/1.1,'afterBottomDeltaWorld':(rf['bottom']-oldfoot['bottom'])/1.1,'packetBindingReady':False,'scope':'Optional explicitly registered source study; no admission or blink completion. Native original and primary ID unchanged.'}
write('registration-alternative.json',info)
atlas=Image.new('RGBA',(384,192));atlas.paste(old,(0,0));atlas.paste(out,(192,0));atlas.save(P/'blink-registered-study-atlas192.png')
old.save(P/'previews/blink-registered-study.apng',save_all=True,append_images=[out,old],duration=[2000,100,900],loop=0,disposal=0,blend=0)
ims=[]
for im in [old,out,old]:
 b=Image.new('RGBA',im.size,'#d5dcc3');b.alpha_composite(im);ims.append(b.convert('RGB'))
ims[0].save(P/'previews/blink-registered-study.gif',save_all=True,append_images=ims[1:],duration=[2000,100,900],loop=0,disposal=2)
sheet=Image.new('RGB',(1200,760),'#eee9dc');d=ImageDraw.Draw(sheet)
for col,(name,im) in enumerate([('Exact awake',old),('Native closure',native),('Closure integer[-1,-4]',out)]):
 d.text((col*400+10,10),name,fill='black')
 for row,bg in enumerate(['#e4e6d6','#25302e']):
  b=Image.new('RGBA',(175,175),bg);b.alpha_composite(im.resize((175,175),Image.Resampling.NEAREST));sheet.paste(b.convert('RGB'),(10+400*col,35+row*370))
  c=im.crop((98,138,132,153));v=Image.new('RGBA',c.size,bg);v.alpha_composite(c);sheet.paste(v.resize((340,150),Image.Resampling.NEAREST).convert('RGB'),(10+400*col,220+row*370))
sheet.save(P/'previews/registration-comparison-light-dark.png')
blink=json.load(open(P/'blink-manifest.json'));blink['registrationAlternative']={'file':'registration-alternative.json','renderId':'western-bluebird-closed-registered-study','sourceFrameId':blink['frames'][0]['sourceFrameId'],'sourceDerivativePNG':info['sourceDerivativePNG'],'outputPNG':info['outputPNG'],'outputPNGsha256':info['outputPNGsha256'],'newDrawing':False,'nativeIntegerTranslation':[-1,-4],'packetBindingReady':False};write('blink-manifest.json',blink)
primary=json.load(open(P/'PRIMARY-SOURCE-MANIFEST.json'));primary['outputMetadata']+=['registration-alternative.json','blink-registered-study-atlas192.png','previews/blink-registered-study.apng','previews/blink-registered-study.gif','previews/registration-comparison-light-dark.png','frame-to-action-map.json'];primary['notes'].append('Optional single native integer[-1,-4]pose-registration derivative preserves all alpha; not a new drawing, body fit or source-original edit.');write('PRIMARY-SOURCE-MANIFEST.json',primary)
intake=json.load(open(P/'intake-manifest.json'));intake['registrationAlternative']='registration-alternative.json';intake['nativeUnregisteredPrimaryRetained']=True;write('intake-manifest.json',intake)
# Viewer has an explicit variant selector. Never silently replace native/default.
f=P/'review.html';html=f.read_text();aidx=html.index('const urls=')+len('const urls=');bidx=html.index(';const imgs=',aidx);urls=json.loads(html[aidx:bidx]);urls['closedRegistered']='data:image/png;base64,'+base64.b64encode((P/info['outputPNG']).read_bytes()).decode();html=html[:aidx]+json.dumps(urls)+html[bidx:]
html=html.replace('<span id="state">','<label>Closed source variant <select id="variant"><option value="native">Native unchanged</option><option value="registered">Integer[-1,-4] native registration study</option></select></label> <span id="state">')
html=html.replace("const pose=tick>=60&&tick<63?'closed':'awake';for", "const pose=tick>=60&&tick<63?'closed':'awake';const variant=document.querySelector('#variant').value;const drawPose=pose==='closed'&&variant==='registered'?'closedRegistered':pose;for")
html=html.replace('x.drawImage(imgs[pose]','x.drawImage(imgs[drawPose]').replace('tick${tick}/89 / ${pose} / root stationary','tick${tick}/89 / ${pose} / ${variant} / root stationary').replace('window.reviewState={tick,pose,root:','window.reviewState={tick,pose,variant,root:').replace('if(++ready===2)','if(++ready===3)')
html=html.replace('<h2>Nearest enlarged eye', '<p>Optional native integer[-1,-4] whole-pose registration preserves all source alpha, no new drawing; lower support residual remains~0.909world. Both variants held for independent actual-size review.</p><h2>Nearest enlarged eye');f.write_text(html)
# Explicit primary-source -> render -> atlas wrapper for both source studies.
awake=primary['reusedFrames'][0];closed=primary['frames'][0];mapping=[]
for variant,at,cp in [('native','blink-study-atlas192.png','frames/closed192.png'),('registered','blink-registered-study-atlas192.png','derivatives/closed-registered192.png')]:
 mapping.append({'variant':variant,'atlasFile':at,'atlasSHA256':sha(P/at),'atlasDimensions':[384,192],'manifestFile':'blink-manifest.json','manifestSHA256':sha(P/'blink-manifest.json'),'frames':[{'sourceFrameId':awake['sourceFrameId'],'sourceStatus':'exact-reuse-not-new','renderId':'western-bluebird-awake-reused','individualPNG':awake['outputPNG'],'individualPNGsha256':awake['outputPNGsha256'],'sourceRect':{'x':0,'y':0,'width':192,'height':192}},{'sourceFrameId':closed['sourceFrameId'],'sourceStatus':'one-new-native-drawing' if variant=='native' else 'registered-derivative-of-same-new-native-drawing-not-additional-art','renderId':'western-bluebird-closed-'+variant+'-study','individualPNG':cp,'individualPNGsha256':sha(P/cp),'sourceRect':{'x':192,'y':0,'width':192,'height':192},'nativeIntegerTranslation':[0,0] if variant=='native' else [-1,-4]}],'tickRate':30,'clips':[{'id':'blink-'+variant+'-study','loop':True,'steps':[{'renderId':'western-bluebird-awake-reused','durationTicks':60},{'renderId':'western-bluebird-closed-'+variant+'-study','durationTicks':3},{'renderId':'western-bluebird-awake-reused','durationTicks':27}]}],'packetBindingReady':False})
write('frame-to-action-map.json',{'schema':'chirp-source-frame-action-map-v1','batchId':P.name,'newPrimaryDrawings':1,'reusedPrimaryDrawings':1,'derivativeRegistrationDrawings':0,'scope':'Source studies only; exact atlas filenames and hashes, no canonical Sharp/runtime admission.','variants':mapping})
print(json.dumps({'nativeID':closed['sourceFrameId'],'htmlSHA256':sha(P/'review.html'),'registrationResidualBottomWorld':info['afterBottomDeltaWorld'],'allAlphaPreserved':True,'manifestSHA256':sha(P/'blink-manifest.json')},indent=2))
