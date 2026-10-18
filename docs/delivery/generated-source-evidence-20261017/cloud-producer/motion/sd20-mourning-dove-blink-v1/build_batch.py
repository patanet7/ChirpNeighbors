from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib,copy,shutil,struct,zlib
P=Path(__file__).parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
fid=lambda im:'frame.sha256.'+hashlib.sha256(f'RGBA8;{im.width}x{im.height};'.encode()+im.tobytes()).hexdigest()
read=lambda n:json.loads((P/n).read_text())
def js(n,v):(P/n).write_text(json.dumps(v,indent=2)+'\n')
native=Image.open(P/'original.png').convert('RGBA');old=Image.open(P/'reference-awake-source768.png').convert('RGBA');awake=Image.open(P/'reused-awake192.png').convert('RGBA');closed=native.resize((192,192),Image.Resampling.NEAREST);closed.save(P/'closed192.png');shutil.copy2(P/'original.png',P/'closed-native.png');assert old.resize((192,192),Image.Resampling.NEAREST).tobytes()==awake.tobytes();ims=[awake,closed];aa=[np.array(i) for i in ims]
atlas=Image.new('RGBA',(384,192));atlas.paste(awake,(0,0));atlas.paste(closed,(192,0));atlas.save(P/'blink-atlas192.png')
base=read('existing-standing-manifest-reference.json');frames=[copy.deepcopy(base['frames'][0]),copy.deepcopy(base['frames'][0])];frames[1].update(id='dove-blink-closed-192',sourceRect={'x':192,'y':0,'width':192,'height':192})
# Inherited coordinates land on the visible pink toe silhouettes in both strict outputs.
clips=[copy.deepcopy(base['clips'][0]),{'id':'blink','tickRate':30,'loop':False,'frames':[{'frameId':frames[0]['id'],'durationTicks':42},{'frameId':frames[1]['id'],'durationTicks':3},{'frameId':frames[0]['id'],'durationTicks':45}]}]
manifest=copy.deepcopy(base);manifest.update(source={'sha256':sha(P/'blink-atlas192.png'),'creator':'Chirp Dove blink source exporter','tool':'Pillow full-canvas nearest resize only','toolVersion':Image.__version__,'rights':'unreviewed','fidelity':'unreviewed'},atlas={'width':384,'height':192,'alpha':'straight-rgba8','colorSpace':'srgb'},frames=frames,clips=clips);js('texture-review-manifest.json',manifest)
new={'sourceFrameId':fid(native),'sourcePNG':'closed-native.png','sourcePNGsha256':sha(P/'closed-native.png'),'speciesId':'mourning_dove','pose':'fully-closed-eye-standing','registration':{'method':'full native canvas nearest resize only','sourceCanvas':list(native.size),'outputCanvas':[192,192],'wholeCanvasScaleXY':[192/native.width,192/native.height],'nativeToReferenceWholeCanvasScaleXY':[768/native.width,768/native.height],'perPoseFit':False,'perPoseTranslation':False,'snap':False,'pixelPaint':False},'outputPNG':'closed192.png','outputPNGsha256':sha(P/'closed192.png')}
reuse={'sourceFrameId':fid(old),'sourcePNG':'reference-awake-source768.png','sourcePNGsha256':sha(P/'reference-awake-source768.png'),'speciesId':'mourning_dove','pose':'exact-existing-awake-standing','registration':{'method':'exact existing source and output bytes reused unchanged','sourceCanvas':[768,768],'outputCanvas':[192,192],'wholeCanvasScaleXY':[0.25,0.25],'perPoseFit':False,'perPoseTranslation':False},'outputPNG':'reused-awake192.png','outputPNGsha256':sha(P/'reused-awake192.png')}
primary={'batchId':P.name,'nativeCalls':1,'original':'original.png','originalSHA256':sha(P/'original.png'),'prompt':'prompt.txt','promptSHA256':sha(P/'prompt.txt'),'frames':[new],'reusedFrames':[reuse],'outputMetadata':['texture-review-manifest.json','frame-to-action-map.json','body-contact-diagnostics.json','alpha-field-diagnostics.json','behavior-handoff.json'],'sourceStatus':'generated one actual closure; independent normal-size review pending','notes':['One new closed-eye drawing; zero new neutral/look/half-closure.','Exact old awake source/export and idle90 timing unchanged.','Native1254→192 whole canvas nearest only; no fit, snap, translation, paint or alpha cleanup.','Closure timing authored:42open/3closed/45open at30Hz; not a biological timing claim.','Body/toe redraw and warm alpha field continuity require normal192CSS review.']};js('PRIMARY-SOURCE-MANIFEST.json',primary)
rows=[]
for i,rec in enumerate([reuse,new]):rows.append({'primarySourceFrameId':rec['sourceFrameId'],'primarySourcePNG':rec['sourcePNG'],'primarySourcePNGsha256':rec['sourcePNGsha256'],'newDrawing':i==1,'renderFrameId':frames[i]['id'],'atlasRect':frames[i]['sourceRect'],'outputPNG':rec['outputPNG'],'outputPNGsha256':rec['outputPNGsha256']})
js('frame-to-action-map.json',{'batchId':P.name,'speciesId':'mourning_dove','renderClipId':'blink','manifest':{'file':'texture-review-manifest.json','sha256':sha(P/'texture-review-manifest.json'),'profile':'chirp-texture-review-v1','canonicalSchemaValidation':'NOT_RUN'},'atlasBinding':{'file':'blink-atlas192.png','sha256':sha(P/'blink-atlas192.png'),'width':384,'height':192,'alpha':'straight-rgba8'},'sourceToRenderFrames':rows,'clips':clips,'projectionScope':'source-only blink review; exact old neutral source/profile geometry/idle90 preserved','appBound':False,'SharpCanonicalAdmission':False})
bbox=[]
for a in aa:
 y,x=np.where(a[:,:,3]>=128);bbox.append([int(x.min()),int(y.min()),int(x.max()+1),int(y.max()+1)])
regions={'eye':[135,86,144,94],'headBill':[126,80,152,102],'bodyWing':[78,101,132,128],'tail':[29,123,81,143],'feet':[89,138,123,153]};metrics={}
for name,(x0,y0,x1,y1) in regions.items():
 a,b=[ar[y0:y1,x0:x1] for ar in aa];sa=a[:,:,3]>=128;sb=b[:,:,3]>=128;metrics[name]={'roi':[x0,y0,x1,y1],'changedRGBApixels':int(np.any(a!=b,axis=2).sum()),'alpha128SilhouetteIoU':float((sa&sb).sum()/max(1,(sa|sb).sum()))}
contacts=[]
for c in frames[0]['contacts']:
 x,y=c['x'],c['y'];contacts.append({'id':c['id'],'xy':[x,y],'awakeRGBA':aa[0][y,x].tolist(),'closedRGBA':aa[1][y,x].tolist(),'interpretation':'visible pink toe pixel in both registered outputs; alpha is not physical support approval'})
js('body-contact-diagnostics.json',{'canvas':[192,192],'world':[192,192],'density':1,'pivot':[105,150],'bboxAlpha128':bbox,'lowestOpaqueRows':[b[3]-1 for b in bbox],'toePixelProbes':contacts,'regions':metrics,'pixelEqualityAcceptanceGate':False,'physicsApproved':False,'bodyReview':'Identity/feather/toe redraw retained; no transformations added to repair differences.'})
fieldROIs={'upper-left-clear':[25,50,75,80],'tail-underfield':[30,145,75,170],'right-foot-field':[120,145,155,170]};al=[]
for name in ['reference-awake-source768.png','original.png','reused-awake192.png','closed192.png']:
 ar=np.array(Image.open(P/name).convert('RGBA'));a=ar[:,:,3];red=(ar[:,:,0]>200)&(ar[:,:,1]<70)&(ar[:,:,2]<70)&(a>0)&(a<255);al.append({'file':name,'alpha1':int((a==1).sum()),'alpha2to127':int(((a>=2)&(a<=127)).sum()),'alpha128to254':int(((a>=128)&(a<=254)).sum()),'alpha255':int((a==255).sum()),'extremeRedPartialAlphaPixels':int(red.sum())})
field=[]
for name,(x0,y0,x1,y1) in fieldROIs.items():
 field.append({'name':name,'roi':[x0,y0,x1,y1],'awake':{'positiveAlpha':int((aa[0][y0:y1,x0:x1,3]>0).sum()),'alphaSum':int(aa[0][y0:y1,x0:x1,3].sum())},'closed':{'positiveAlpha':int((aa[1][y0:y1,x0:x1,3]>0).sum()),'alphaSum':int(aa[1][y0:y1,x0:x1,3].sum())}})
js('alpha-field-diagnostics.json',{'images':al,'extremeRedPredicate':'uint8 RGBA R>200,G<70,B<70,0<A<255','fieldROIs':field,'processing':'all native RGBA retained; whole-canvas nearest only; no alpha cleanup','qualification':'Old diffuse warm partial-alpha field is part of exact reference. Generated field/edge differences retained and judged on actual normal light/dark; raw transparent-black view alone is insufficient.'})
js('behavior-handoff.json',{'speciesId':'mourning_dove','newDrawings':1,'newNeutral':0,'newLook':0,'reusedAwake':1,'idleClip':clips[0],'blinkClip':clips[1],'timingAuthored':True,'closedDurationMs':100,'world':[192,192],'density':1,'pivot':[105,150],'rootMotion':'none; fixed registration','support':'ground standing source proposal; pixel probes not physical validation','canonicalSchemaValidation':'NOT_RUN','MacBinding':'UNKNOWN','appBound':False,'activation':'none','acceptance':'independent review pending'})
args=read('native-call-arguments.json')['arguments'];assert args['prompt'].encode()==(P/'prompt.txt').read_bytes();js('prompt-byte-audit.json',{'exactPreparedAndSubmittedUTF8Match':True,'bytes':len((P/'prompt.txt').read_bytes()),'promptSHA256':sha(P/'prompt.txt'),'nativeArgumentsFileSHA256':sha(P/'native-call-arguments.json'),'referenceSHA256':sha(P/'reference-awake-source768.png'),'calls':1,'retries':0})
# PNG/APNG frames retain full RGBA; GIF is a lossy palette preview only.
def chunk(t,d):return struct.pack('>I',len(d))+t+d+struct.pack('>I',zlib.crc32(t+d)&0xffffffff)
out=b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',192,192,8,6,0,0,0))+chunk(b'acTL',struct.pack('>II',3,1));seq=0
for i,(im,ticks) in enumerate([(awake,42),(closed,3),(awake,45)]):
 out+=chunk(b'fcTL',struct.pack('>IIIIIHHBB',seq,192,192,0,0,ticks,30,0,0));seq+=1;data=zlib.compress(b''.join(b'\0'+im.tobytes()[y*768:(y+1)*768] for y in range(192)))
 if i==0:out+=chunk(b'IDAT',data)
 else:out+=chunk(b'fdAT',struct.pack('>I',seq)+data);seq+=1
out+=chunk(b'IEND',b'');(P/'blink-preview.apng').write_bytes(out)
g=[]
for im in [awake,closed,awake]:
 bg=Image.new('RGBA',(192,192),'#e5e0cd');bg.alpha_composite(im);g.append(bg.convert('RGB'))
g[0].save(P/'blink-preview.gif',save_all=True,append_images=g[1:],duration=[1400,100,1500],disposal=2)
sheet=Image.new('RGBA',(850,620),'#e9e2d0');dr=ImageDraw.Draw(sheet)
for j,(im,label) in enumerate([(awake,'exact old awake'),(closed,'new closed candidate')]):
 for k,(bg,color) in enumerate([('light','#e5e0cd'),('dark','#182a32')]):
  pane=Image.new('RGBA',(192,192),color);pane.alpha_composite(im);sheet.alpha_composite(pane,(15+j*420+k*200,28));dr.text((15+j*420+k*200,8),label+' '+bg,fill='#293c2e')
 for k,(roi,title) in enumerate([((130,81,151,99),'eye x8'),((87,138,125,155),'feet x5'),((30,145,75,170),'field x3')]):
  crop=im.crop(roi);bg=Image.new('RGBA',crop.size,'#e5e0cd');bg.alpha_composite(crop);scale=[8,5,3][k];sheet.alpha_composite(bg.resize((bg.width*scale,bg.height*scale),Image.Resampling.NEAREST),(15+j*420,250+[0,164,270][k]));dr.text((215+j*420,250+[0,164,270][k]),title,fill='#293c2e')
sheet.save(P/'normal-light-dark-and-crops.png')
(P/'README.md').write_text('# Mourning Dove blink source review\n\nOne actual closed-eye drawing from one native edit; exact existing awake source and192 export reused. No new neutral/look or body animation. Full1254→192 nearest only; no fit, snap, repair, alpha cleanup or pixel paint.\n\nNormal canvas/world192 CSS pixels, density1, fixed pivot105,150. Existing awake-only idle90 ticks unchanged. Separate authored blink:42open/3closed/45open at30Hz,100ms closure, exact old awake return. Player nominal duration90ticks/3000ms; final sample89 remains awake until deadline. GIF is a composited palette preview; APNG and PNG retain RGBA.\n\nBody/toe/partial-alpha warm-field redraw retained for independent review. Source-only, activation none, Mac binding unknown; canonical Zod/Sharp not run. No physical contact or biological timing claim.\n')
print(json.dumps({'newSource':new['sourceFrameId'],'outputSHA256':new['outputPNGsha256'],'bbox':bbox,'contacts':contacts,'field':field},indent=2))
