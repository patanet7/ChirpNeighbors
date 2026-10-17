from pathlib import Path
from PIL import Image,ImageDraw
from scipy import ndimage
import numpy as np,json,hashlib,shutil,base64,datetime
P=Path(__file__).parent
OLD=Path('/workspace/asset-production/new-species/sd20-final-four-v1')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rid(im):return 'frame.sha256.'+hashlib.sha256(f'RGBA8;{im.width}x{im.height};'.encode()+im.tobytes()).hexdigest()
def write(n,x):(P/n).write_text(json.dumps(x,indent=2)+'\n')
im=Image.open(P/'original.png').convert('RGBA');a=np.array(im);labels,n=ndimage.label(a[:,:,3]>=32)
components=[]
for k,s in enumerate(ndimage.find_objects(labels),1):
 if s and (labels[s]==k).sum()>500:components.append((k,s))
components.sort(key=lambda z:z[1][1].start)
assert len(components)==4
seed=np.zeros(labels.shape,dtype=np.uint8)
for i,(k,s) in enumerate(components,1):seed[labels==k]=i
_,nearest=ndimage.distance_transform_edt(seed==0,return_indices=True);owners=seed[tuple(nearest)]
names=['crouch','airborne-tuck','descending-extension','supported-settle']
# Roots are producer-declared technical registration, not observed center of mass.
# One original support plane y631 for the entire sheet preserves drawn elevation.
roots=[(345,631),(890,631),(1420,631),(1975,631)]
frames=[];outs=[];density=None
for i,(name,(rx,ry)) in enumerate(zip(names,roots),1):
 mask=(owners==i)&(a[:,:,3]>=2);piece=np.zeros_like(a);piece[mask]=a[mask]
 ys,xs=np.where(mask);bbox=[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)]
 src=Image.new('RGBA',(1024,1024));dx,dy=608-rx,800-ry
 src.alpha_composite(Image.fromarray(piece).crop(tuple(bbox)),(bbox[0]+dx,bbox[1]+dy))
 sp=f'frames/{i:02d}-{name}-source1024.png';src.save(P/sp)
 out=src.resize((192,192),Image.Resampling.NEAREST);op=f'frames/{i:02d}-{name}192.png';out.save(P/op);outs.append(out)
 aa=np.array(out)[:,:,3];yy,xx=np.where(aa>=128);bb=[int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)]
 # Bottom contour contacts only for grounded frames, not anatomical identities.
 contacts=[]
 if i in (1,4):
  near=(aa>=128);near[:bb[3]-3]=False
  yx=np.argwhere(near);order=yx[np.argsort(yx[:,1])]
  for j,q in enumerate(np.array_split(order,2),1):
   z=q[np.argmax(q[:,0])];contacts.append({'id':f'silhouette-support-{j}','x':int(z[1]),'y':int(z[0]),'alpha':int(aa[z[0],z[1]]),'qualification':'positive-alpha lower-contour proxy; not tracked toe identity'})
 beak=(int(xx.max()),int(np.median(yy[xx==xx.max()])))
 frames.append({'sourceFrameId':rid(src),'sourcePNG':sp,'sourcePNGsha256':sha(P/sp),'speciesId':'western_bluebird','pose':name,'registration':{'sourceCanvas':[1024,1024],'originalOwnedBBox':bbox,'integerTranslation':[dx,dy],'sourceRoot':[608,800],'originalProjectedSupportRoot':[rx,ry],'method':'nearest of four principal alpha>=32 components assigns alpha>=2; alpha1 omitted only in derivative; integer translation only','perPoseScaleFit':False,'sourcePixelsPainted':False,'supportPlaneOriginalY':631,'rootQualification':'technical projected support registration; artist-authored, not measured bird COM'},'outputPNG':op,'outputPNGsha256':sha(P/op),'outputRGBAId':rid(out),'outputCanvas':[192,192],'sourceToOutputScale':0.1875,'outputPivot':[114,150],'visibleBBoxAlpha128':bb,'outputBeakApprox':list(beak),'beakQualification':'silhouette tip estimate; not interaction target anchor','supportContacts':contacts,'supportStatus':'grounded silhouette study' if contacts else 'airborne; no planted contacts'})
# One call-wide density, calibrated ONCE using settle's neutral-like width.
density=(frames[-1]['visibleBBoxAlpha128'][2]-frames[-1]['visibleBBoxAlpha128'][0])/60
for f in frames:
 f['sourcePixelsPerWorldUnit']=density;f['worldCanvas']=[192/density]*2;f['visibleWorldSize']=[(f['visibleBBoxAlpha128'][2]-f['visibleBBoxAlpha128'][0])/density,(f['visibleBBoxAlpha128'][3]-f['visibleBBoxAlpha128'][1])/density]
 f['lowestAlpha128WorldOffsetFromRoot']=(f['visibleBBoxAlpha128'][3]-1-150)/density
# Exact old neutral bytes and ID, independently calibrated historical density1.1.
old=json.load(open(OLD/'intake-manifest.json'))['species'][0];neutral=old['frames'][0]
for src,dst in [('western_bluebird/neutral-source1024.png','reused/neutral-source1024.png'),('western_bluebird/neutral192.png','reused/neutral192.png')]:shutil.copyfile(OLD/src,P/dst)
reuse={'playbackRole':'immutable comparison only; excluded from hop due cross-original proportion discontinuity','sourceFrameId':neutral['sourceFrameId'],'sourcePNG':'reused/neutral-source1024.png','sourcePNGsha256':sha(P/'reused/neutral-source1024.png'),'outputPNG':'reused/neutral192.png','outputPNGsha256':sha(P/'reused/neutral192.png'),'originBatch':'sd20-final-four-v1','originOriginalSHA256':sha(OLD/'original.png'),'originPromptSHA256':sha(OLD/'prompt.txt'),'newDrawing':False,'sourcePixelsPerWorldUnit':1.1,'outputPivot':[114,148],'visibleNeutralWorldWidth':60,'qualification':'Exact immutable reused bytes. Historical density differs from this independently generated batch; one global new-batch density, no per-pose fitting. Head/body proportion continuity remains provisional.'}
# Put new supported lowest contour exactly on floor via one common draw offset.
# The original plane maps to150; nearest sampling puts settle's bottom at149.
groundPixel=frames[-1]['visibleBBoxAlpha128'][3]-1
for f in frames:
 if f['supportContacts']:
  f['outputPivot']=[sum(c['x'] for c in f['supportContacts'])/2,max(c['y'] for c in f['supportContacts'])]
 else:f['outputPivot']=[114,groundPixel]
 f['lowestAlpha128WorldOffsetFromRoot']=(f['visibleBBoxAlpha128'][3]-1-f['outputPivot'][1])/density
 f['contactOffsetsWorld']=[[(c['x']-f['outputPivot'][0])/density,(c['y']-f['outputPivot'][1])/density] for c in f['supportContacts']]

atlas=Image.new('RGBA',(768,192))
for i,o in enumerate(outs):atlas.paste(o,(192*i,0))
atlas.save(P/'hop-atlas192.png')
neutralim=Image.open(P/'reused/neutral192.png').convert('RGBA')
poseims=[]
for i in [3,0,1,2,3]:
 canvas=Image.new('RGBA',(192,192));pivot=frames[i]['outputPivot'];canvas.alpha_composite(outs[i],(round(114-pivot[0]),round(150-pivot[1])));poseims.append(canvas)

poseims[0].save(P/'previews/pose-sequence.apng',save_all=True,append_images=poseims[1:],duration=[500,133,133,133,1133],loop=1,disposal=0,blend=0)
rgb=[]
for o in poseims:
 b=Image.new('RGBA',(192,192),'#d5dcc3');b.alpha_composite(o);rgb.append(b.convert('RGB'))
rgb[0].save(P/'previews/pose-sequence.gif',save_all=True,append_images=rgb[1:],duration=[500,130,130,130,1130],disposal=2)
contactsheet=Image.new('RGB',(1050,300),'#d5dcc3');d=ImageDraw.Draw(contactsheet);d.text((10,8),'Western Bluebird / four new drawn poses / one batch scale / 60-world settle width',fill='black')
for i,f in enumerate(frames):
 o=outs[i];world=o.resize((round(192/density),)*2,Image.Resampling.NEAREST);contactsheet.paste(world,(20+i*255,50),world);d.text((20+i*255,230),f['pose'],fill='black');d.text((20+i*255,247),'source candidate; no app binding',fill='black')
contactsheet.save(P/'previews/normal-size-contact-sheet.png')
feet=Image.new('RGB',(1000,300),'#d5dcc3');fd=ImageDraw.Draw(feet)
for i,o in enumerate(outs):
 c=o.crop((85,112,140,155)).resize((220,172),Image.Resampling.NEAREST);feet.paste(c,(i*250,45),c);fd.text((i*250+5,12),names[i],fill='black')
feet.save(P/'previews/enlarged-feet.png')
ticks=[]
for t in range(61):
 if t<15:pose='supported-settle';x=y=0;ground=True
 elif t<19:pose='crouch';x=y=0;ground=True
 elif t<23:
  pose='airborne-tuck';u=(t-18)/8;x=20*u;y=-8*4*u*(1-u);ground=False
 elif t<27:
  pose='descending-extension';u=(t-18)/8;x=20*u;y=-8*4*u*(1-u);ground=False
 elif t<33:pose='supported-settle';x=20;y=0;ground=True
 else:pose='supported-settle';x=20;y=0;ground=True
 ticks.append({'tick':t,'timeSeconds':t/30,'pose':pose,'rootWorld':[x,y],'grounded':ground,'drawnPose':pose,'trajectoryComponent':'artist-authored 20-world travel and8-world root arc, only airborne ticks19..26; not new art'})
motion={'schema':'chirp-source-motion-study-v1','batchId':P.name,'speciesId':'western_bluebird','action':'ground-hop','tickRate':30,'loop':False,'playback':'one-shot; manual Replay visibly resets to start; final supported-settle holds; old neutral excluded due proportion discontinuity','totalTicks':61,'newDrawings':4,'reusedReferenceDrawings':1,'reusedDrawingsInPlayback':0,'trajectoryIsNewDrawing':False,'trajectory':{'travelWorld':20,'arcHeightWorld':8,'groundY':0,'departureRoot':[0,0],'landingRoot':[20,0],'groundedRootStationary':True,'airborneTicks':[19,26],'authoredNotMeasured':True},'frames':frames,'reusedFrames':[reuse],'ticks':ticks,'packetBindingReady':False,'canonicalSharpReceipt':None,'runtimeBound':False,'ownerApproved':False,'normalAppYardVerified':False,'supportCaveats':['Grounded actor root stays fixed. Toe silhouettes were independently redrawn and are not anatomically tracked; changing contact offsets can create visible toe redraw/stance discontinuity. Do not claim both feet are physically locked.','Exact old neutral excluded from hop playback due proportion discontinuity; available for immutable comparison only. New batch uses one density calibrated on supported-settle width. Exact reused neutral keeps its existing density; cross-original head/torso continuity must be reviewed.','Original alpha1 fringe excluded only from derivatives, original unchanged.','Airborne pose silhouette already lifts legs/body; trajectory adds a separately declared arc. Exact hop kinematics are artist-authored.']}
write('motion-manifest.json',motion)
write('PRIMARY-SOURCE-MANIFEST.json',{'batchId':P.name,'nativeCalls':1,'original':'original.png','originalSHA256':sha(P/'original.png'),'prompt':'prompt.txt','promptSHA256':sha(P/'prompt.txt'),'frames':frames,'reusedFrames':[reuse],'outputMetadata':['motion-manifest.json','intake-manifest.json','hop-atlas192.png','previews/pose-sequence.apng','previews/pose-sequence.gif','previews/normal-size-contact-sheet.png','previews/enlarged-feet.png','review.html'],'sourceStatus':'generated-source-review-pending','notes':['Only four new native drawings; reused neutral is not new art. One native call, no retry. No app admission or Sharp receipt.','Grounded support-art discontinuity remains unapproved; trajectory root has no grounded travel.']})
write('intake-manifest.json',{'schema':'chirp-source-action-intake-v1','batchId':P.name,'speciesId':'western_bluebird','newDrawings':4,'nativeCalls':1,'primaryManifest':'PRIMARY-SOURCE-MANIFEST.json','actionManifest':'motion-manifest.json','proposedNewBatchDensity':density,'sourceCanvas':[1024,1024],'outputCanvas':[192,192],'targetWorldPixels':60,'targetMeasure':'supported-settle-visible-width','scaleAxis':'width','sameDensityAllNewPoses':True,'scaleQualification':'Practical neutral-like settle width proxy, not biological calibration; cross-original proportions provisional. Reused neutral exact bytes at historical1.1 density.','coverage':{'groundHop':{'planned':True,'drawnBodyPoseCount':4,'authoredTrajectoryAvailable':True,'runtimeBound':False,'normalAppYardVisuallyVerified':False,'physicalFootLockApproved':False},'feeding':{'drawn':False,'bound':False}},'packetBindingReady':False,'approval':'unreviewed','activation':'none','rights':'unreviewed; factual references only; generated style references with exact lineage','nextQueued':{'task':'coordinator integration/animation-gap review','state':'queued','newNativeCallAuthorizedHere':False}})
# Standalone actual-world-size source preview: generated art data only, no browser capture bytes.
encoded={f['pose']:'data:image/png;base64,'+base64.b64encode((P/f['outputPNG']).read_bytes()).decode() for f in frames};encoded['neutral']='data:image/png;base64,'+base64.b64encode((P/reuse['outputPNG']).read_bytes()).decode()
html='''<!doctype html><meta charset="utf-8"><title>Western Bluebird hop source review</title><style>body{font:15px system-ui;background:#f5f2e8;color:#243220;margin:24px;max-width:1100px}canvas{image-rendering:pixelated;border:1px solid #aab79a;background:#d5dcc3}button{padding:8px 18px;margin:8px}p{max-width:900px}.warning{color:#7d321d}</style><h1>Western Bluebird: one-shot hop source study</h1><p>Four new body drawings. Exact old neutral retained as comparison only, excluded from hop playback due proportion discontinuity. Yard-scale visible neutral-like width60worldpx; travel20worldpx. Authored trajectory is separate from drawings. Manual replay visibly resets; playback holds at landing.</p><button id="replay">Replay from start</button><label><input id="overlay" type="checkbox" checked>contact/root overlay</label><span id="state"></span><br><canvas id="yard" width="640" height="280"></canvas><p class="warning">Unapproved source study. Grounded root never slides; independently redrawn toe footprints may visibly change. Old neutral excluded from playback due cross-original proportion discontinuity. No anatomical foot lock, Sharp intake or Mac yard verification claimed.</p><h2>Nearest-neighbor enlarged feet</h2><img style="max-width:100%" src="FEET"><p>APNG/GIF are pose sequence previews, not traveled clips. Source JSON supplies the full30Hz one-shot trajectory. Normal bird detail and support discontinuity require independent review.</p><script>const manifest=MOTION;const urls=URLS;const imgs={};let ready=0;let start=0,tick=0,playing=false;const canvas=document.querySelector('#yard'),ctx=canvas.getContext('2d');ctx.imageSmoothingEnabled=false;function draw(){const s=manifest.ticks[tick];ctx.fillStyle='#d5dcc3';ctx.fillRect(0,0,640,280);ctx.strokeStyle='#79866a';ctx.beginPath();ctx.moveTo(0,218);ctx.lineTo(640,218);ctx.stroke();const f=s.pose==='neutral'?manifest.reusedFrames[0]:manifest.frames.find(x=>x.pose===s.pose);const den=f.sourcePixelsPerWorldUnit;const w=192/den;const x=270+s.rootWorld[0]-f.outputPivot[0]/den;const y=218+s.rootWorld[1]-f.outputPivot[1]/den;ctx.drawImage(imgs[s.pose],Math.round(x),Math.round(y),Math.round(w),Math.round(w));if(document.querySelector('#overlay').checked){ctx.strokeStyle=s.grounded?'#9e291e':'#136bad';ctx.beginPath();ctx.moveTo(265+s.rootWorld[0],218+s.rootWorld[1]);ctx.lineTo(275+s.rootWorld[0],218+s.rootWorld[1]);ctx.moveTo(270+s.rootWorld[0],213+s.rootWorld[1]);ctx.lineTo(270+s.rootWorld[0],223+s.rootWorld[1]);ctx.stroke();for(const c of f.supportContacts||[]){ctx.fillStyle='#a02118';ctx.fillRect(Math.round(x+c.x/den)-1,Math.round(y+c.y/den)-1,3,3)}}document.querySelector('#state').textContent=`tick ${tick}/60 / ${s.pose} / root ${s.rootWorld.map(x=>x.toFixed(1)).join(',')} / ${s.grounded?'supported study':'airborne'}`;window.reviewState={tick,pose:s.pose,root:s.rootWorld,grounded:s.grounded,playing};}function loop(now){if(playing){tick=Math.min(60,Math.floor((now-start)*30/1000));if(tick===60)playing=false;draw()}requestAnimationFrame(loop)}for(const [n,u]of Object.entries(urls)){imgs[n]=new Image;imgs[n].onload=()=>{if(++ready===5){start=performance.now();playing=true;draw();requestAnimationFrame(loop)}};imgs[n].src=u}document.querySelector('#replay').onclick=()=>{tick=0;start=performance.now();playing=true;draw()};document.querySelector('#overlay').onchange=draw;</script>'''
html=html.replace('MOTION',json.dumps(motion)).replace('URLS',json.dumps(encoded)).replace('FEET','data:image/png;base64,'+base64.b64encode((P/'previews/enlarged-feet.png').read_bytes()).decode());(P/'review.html').write_text(html)
print(json.dumps({'newFrameIDs':[f['sourceFrameId'] for f in frames],'newDensity':density,'groundPixel':groundPixel,'visibleWorldSizes':[f['visibleWorldSize'] for f in frames],'sourceSHA256':sha(P/'original.png'),'promptSHA256':sha(P/'prompt.txt')},indent=2))
