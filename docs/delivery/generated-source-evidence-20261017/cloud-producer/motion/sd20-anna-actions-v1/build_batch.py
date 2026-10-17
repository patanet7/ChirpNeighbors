"""Reproducible source extraction and presentation export, not art repainting."""
from pathlib import Path
from PIL import Image
import numpy as np, json, hashlib, struct, zlib, base64
P=Path(__file__).parent
sha=lambda b:hashlib.sha256(b).hexdigest()
def savejson(name,obj):(P/name).write_text(json.dumps(obj,indent=2)+'\n')
original=Image.open(P/'original.png').convert('RGBA')
specs=[('blink',(0,0,627,600),(218,235)),('look',(627,0,1254,600),(274,233)),('hover-up',(0,600,627,1254),(193,400)),('hover-down',(627,600,1254,1254),(238,400))]
# Hover offsets are local-to-crop: global bill tips approximately(617,750),(1199,750)
# become common local body/beak region. Registration is integer translation only.
lineage=[]; images=[];arrays=[];sources=[]
for name,rect,offset in specs:
 c=original.crop(rect); im=Image.new('RGBA',(1024,1024));im.paste(c,offset);(P/'frames1024').mkdir(exist_ok=True);(P/'frames96').mkdir(exist_ok=True);im.save(P/'frames1024'/f'{name}.png');out=im.resize((96,96),Image.Resampling.NEAREST);out.save(P/'frames96'/f'{name}.png');images.append(out);arrays.append(np.array(out));sources.append(im)
 a=np.array(out);y,x=np.where(a[:,:,3]>=128);bbox=[int(x.min()),int(y.min()),int(x.max()+1),int(y.max()+1)]
 lineage.append({'name':name,'frameId':'frame.sha256.'+sha(b'RGBA8;1024x1024;'+im.tobytes()),'file':f'frames1024/{name}.png','fileSha256':sha((P/'frames1024'/f'{name}.png').read_bytes()),'sourceAtlas':'original.png','sourceAtlasSha256':sha((P/'original.png').read_bytes()),'sourceRect':list(rect),'registrationTranslation':list(offset),'sourceCanvas':[1024,1024],'noPerFrameResizing':True,'export':f'frames96/{name}.png','exportSha256':sha((P/'frames96'/f'{name}.png').read_bytes()),'exportRGBAsha256':sha(out.tobytes()),'exportScale':3/32,'visibleBBoxAlpha128':bbox,'visibleLengthWorld':(bbox[2]-bbox[0])/1.5})
atlas=Image.new('RGBA',(384,96));idleatlas=Image.new('RGBA',(192,96))
for i,im in enumerate(images):atlas.paste(im,(96*i,0))
for i,im in enumerate(images[:2]):idleatlas.paste(im,(96*i,0))
atlas.save(P/'all-actions-atlas96.png');idleatlas.save(P/'idle-atlas96.png')
# Contract anchor pixels must actually exist in both perched output frames.
common=np.minimum(arrays[0][:,:,3],arrays[1][:,:,3]);yy,xx=np.indices((96,96));contacts=[]
for side,target in [(xx<55,(53,75)),(xx>=55,(59,75))]:
 candidates=np.argwhere((common>=128)&side&(yy>=72)&(yy<=76)&(xx>=45)&(xx<=65));assert len(candidates)
 y,x=min(candidates,key=lambda p:(p[0]-target[1])**2+(p[1]-target[0])**2);contacts.append({'id':'foot-'+str(len(contacts)+1),'x':int(x),'y':int(y)})
frames=[]
for i,name in enumerate(['blink','look']):
 frames.append({'id':'anna-'+name+'-96','sourceRect':{'x':i*96,'y':0,'width':96,'height':96},'canvas':{'width':96,'height':96},'trim':{'x':0,'y':0},'pivot':{'x':55,'y':75},'contacts':contacts,'world':{'width':64,'height':64},'sourcePixelsPerWorldUnit':1.5})
idleSteps=[('look',66),('blink',3),('look',24)]
manifest={'schemaVersion':1,'profile':'chirp-texture-review-v1','scope':'review-only','approval':'unreviewed','activation':'none','source':{'sha256':sha((P/'idle-atlas96.png').read_bytes()),'creator':'Chirp cloud source-preserving exporter','tool':'Pillow whole-canvas nearest export','toolVersion':'12.3.0','rights':'unreviewed','fidelity':'unreviewed'},'atlas':{'width':192,'height':96,'alpha':'straight-rgba8','colorSpace':'srgb'},'frames':frames,'clips':[{'id':'idle','tickRate':30,'loop':True,'frames':[{'frameId':'anna-'+n+'-96','durationTicks':t} for n,t in idleSteps]}]}
savejson('texture-review-manifest.json',manifest)
def apng(path,sequence,ticks):
 def chunk(k,d):return struct.pack('>I',len(d))+k+d+struct.pack('>I',zlib.crc32(k+d)&0xffffffff)
 p=b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',96,96,8,6,0,0,0))+chunk(b'acTL',struct.pack('>II',len(sequence),0));num=0
 for j,(idx,t) in enumerate(zip(sequence,ticks)):
  p+=chunk(b'fcTL',struct.pack('>IIIIIHHBB',num,96,96,0,0,t,30,0,0));num+=1;a=arrays[idx];data=zlib.compress(b''.join(b'\0'+a[y].tobytes() for y in range(96)),9)
  if j==0:p+=chunk(b'IDAT',data)
  else:p+=chunk(b'fdAT',struct.pack('>I',num)+data);num+=1
 (P/path).write_bytes(p+chunk(b'IEND',b''))
apng('perched-idle.apng',[1,0,1],[66,3,24]);apng('hover-study.apng',[2,3],[1,1])
# A legible normal-world-size GIF. One CSS pixel per world unit;64canvas,~34bird.
gif=[]
for i in [1,0,1]:
 bg=Image.new('RGBA',(64,64),'#d9d4bd');bg.alpha_composite(images[i].resize((64,64),Image.Resampling.NEAREST));gif.append(bg.convert('RGB'))
gif[0].save(P/'Anna-Perched-Normal-World-Size.gif',save_all=True,append_images=gif[1:],duration=[2200,100,800],loop=0,optimize=False)
savejson('source-lineage.json',{'referenceCanonFrameId':'frame.sha256.6ec8bdb38dc55eaa023523e449a54bbaeb37a342679af7871231d3c57184423d','newCanonSpecies':0,'newDrawings':4,'generatedSourceSize':list(original.size),'frames':lineage})
handoff={'schemaVersion':1,'speciesId':'anna_s_hummingbird','status':'staged-provisional-source-candidate','newDrawings':4,'newCanonSpecies':0,'relativeScale':{'presentationDensity':1.5,'worldCanvas':[64,64],'perchedTargetVisibleLengthWorld':34,'measuredPerchedVisibleLengthsWorld':[v['visibleLengthWorld'] for v in lineage[:2]],'sourceCanvas':[1024,1024],'outputCanvas':[96,96],'sourceToOutputScale':3/32,'noPerFrameFit':True,'scaleBiologicallyApproved':False,'note':'One shared density for all4frames; retains native differences in drawn silhouette. Canon reference is34world units; this batch approximates that size.'},'minimumCoverage':[{'action':'perched idle/look/blink','priority':1,'basis':'product screen-time priority, not measured natural-history frequency','generated':True,'drawings':2,'rigged':False,'packetBound':True,'appBound':False,'visuallyVerified':'source image and static normal-size sheets only; temporal browser/human review pending','intake':['idle-atlas96.png','texture-review-manifest.json'],'timingTicks':[66,3,24],'tickRate':30,'notes':'100ms closed hold; look pose is the repeated open hold. Allbody changes are drawn, not bobbing.'},{'action':'hover','priority':1,'basis':'species-specific product override; no universal behavioral frequency claim','generated':True,'drawings':2,'rigged':False,'packetBound':False,'appBound':False,'visuallyVerified':'source wing poses inspected; fastcycle temporal quality pending','isolationPreview':'hover-study.apng','timingTicks':[1,1],'tickRate':30,'notes':'Two actual wing drawings;15visual cycles/s is a stylized sample, not a biological wingbeat claim. Keep fixed airbornebody, no feet-ground contract. RequiresMac actor/flight binding; not admitted asidle.'},{'action':'short airborne reposition','priority':2,'generated':False,'rigged':False,'packetBound':False,'appBound':False,'visuallyVerified':False,'proposedRuntimeBinding':'reuse hover sprites, interpolate actorflight path; never label translation new wing drawing'},{'action':'nectar feeding','priority':3,'generated':False,'rigged':False,'packetBound':False,'appBound':False,'visuallyVerified':False,'proposedRuntimeBinding':'hold stable hover at authored flower target; reference beak-tip aboutoutput(76,52), measureexact perframe before binding','missing':'flower anchor collision/offset and neck/tongue feeding drawing'},{'action':'preen/takeoff/landing/rest','priority':4,'generated':False,'rigged':False,'packetBound':False,'appBound':False,'visuallyVerified':False,'missing':'no dedicated generated action poses'}],'contacts':{'perched':contacts,'perchAnchorOutput':[55,75],'hoverGroundContact':None,'hoverBeakTipOutputApproximate':[76,52],'physicalSupportApproved':False,'note':'Declared commonpositivealpha foot pixels satisfy data registration; anatomicalfeet/root contact still normal-size review. Hover has no ground contacts; do not reuse perchedfeet contract.'},'macIntake':{'path':'existingcandidate-yard reviewTexture intake','serverCanonicalReceipt':'pending actualSharp build; never fabricated','yardPlayback':'pending','profile':'chirp-texture-review-v1'},'issues':['Nativeatlas1254² differed fromrequested1536²; documented extraction split atglobaly600 avoids upperhoverwing spill.','Perched redrawsilhouette4percent width variation; retain atnormal-size provisionalreview, noexactRGBAequality gate.','Fast2posehover may strobe; isolateuntilnormal-size temporalreview.','Noactor/physicsbinding or canonicalSharpadmission performed here.']}
savejson('behavior-handoff.json',handoff)
enc=lambda path:base64.b64encode((P/path).read_bytes()).decode()
html='''<!doctype html><meta charset="utf-8"><title>Anna: bounded action candidate</title><style>body{font:16px system-ui;background:#e7e3d1;color:#24342b;max-width:1000px;margin:30px auto}img{image-rendering:pixelated;background:#d9d4bd;margin:10px}pre{white-space:pre-wrap}section{display:inline-block;vertical-align:top}</style><h1>Anna’s Hummingbird: four drawn poses</h1><p>Existing individual reused. 0new species canons;4actual new drawings. No rigged bobbing. Small normal-world view is64px canvas, approximately34px perched bird. Larger views are inspection only.</p>'''
for name,file in [('Normal-world perched blink/look','perched-idle.apng'),('Isolated hover study;unbound','hover-study.apng')]:
 html+=f'<section><h2>{name}</h2><img width="64" height="64" src="data:image/png;base64,{enc(file)}"><img width="288" height="288" src="data:image/png;base64,{enc(file)}"></section>'
html+='<p>Hover is two real wing poses played at30Hz,15visualcycles/s, a stylized pose study. Biology/contact/pathbinding and continuous playback review remain pending. Idle packet supplies unchanged sharedcontacts/pivot/worlddensity;Mac mustcreate actualSharpcanonicalreceipt.</p><pre>'+json.dumps(handoff,indent=2)+'</pre>'
(P/'review.html').write_text(html)
print(json.dumps({'newDrawingIds':[v['frameId'] for v in lineage],'contacts':contacts,'lengths':[v['visibleLengthWorld'] for v in lineage],'originalSHA':sha((P/'original.png').read_bytes())}))
