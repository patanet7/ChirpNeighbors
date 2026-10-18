from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib,copy,shutil,struct,zlib
P=Path(__file__).parent;N=384;D=1.625;W=N/D
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();fid=lambda im:'frame.sha256.'+hashlib.sha256(f'RGBA8;{im.width}x{im.height};'.encode()+im.tobytes()).hexdigest();read=lambda n:json.loads((P/n).read_text())
def js(n,v):(P/n).write_text(json.dumps(v,indent=2)+'\n')
native=Image.open(P/'original.png').convert('RGBA');old=Image.open(P/'reference-awake-source1024.png').convert('RGBA');awake=Image.open(P/'reused-awake384.png').convert('RGBA');new=native.resize((N,N),Image.Resampling.NEAREST);new.save(P/'closed384.png');shutil.copy2(P/'original.png',P/'closed-native.png');assert old.resize((N,N),Image.Resampling.NEAREST).tobytes()==awake.tobytes();ims=[awake,new];aa=[np.array(i) for i in ims]
atlas=Image.new('RGBA',(2*N,N));atlas.paste(awake,(0,0));atlas.paste(new,(N,0));atlas.save(P/'blink-atlas384.png');base=read('existing-standing-manifest-reference.json');frames=[copy.deepcopy(base['frames'][0]),copy.deepcopy(base['frames'][0])];frames[1].update(id='california-quail-blink-closed-384',sourceRect={'x':N,'y':0,'width':N,'height':N},contacts=copy.deepcopy(base['frames'][0]['contacts']))
clips=[copy.deepcopy(base['clips'][0]),{'id':'blink','tickRate':30,'loop':False,'frames':[{'frameId':frames[0]['id'],'durationTicks':42},{'frameId':frames[1]['id'],'durationTicks':3},{'frameId':frames[0]['id'],'durationTicks':45}]}]
m=copy.deepcopy(base);m.update(source={'sha256':sha(P/'blink-atlas384.png'),'creator':'Chirp Quail blink exporter','tool':'Pillow full-canvas nearest resize','toolVersion':Image.__version__,'rights':'unreviewed','fidelity':'unreviewed'},atlas={'width':2*N,'height':N,'alpha':'straight-rgba8','colorSpace':'srgb'},frames=frames,clips=clips);js('texture-review-manifest.json',m)
newrec={'sourceFrameId':fid(native),'sourcePNG':'closed-native.png','sourcePNGsha256':sha(P/'closed-native.png'),'speciesId':'california_quail','pose':'fully-closed-eye-standing','registration':{'method':'whole native canvas nearest only','sourceCanvas':list(native.size),'outputCanvas':[N,N],'wholeCanvasScaleXY':[N/native.width,N/native.height],'nativeToReferenceWholeCanvasScaleXY':[1024/native.width,1024/native.height],'perPoseFit':False,'perPoseTranslation':False,'snap':False,'pixelPaint':False},'outputPNG':'closed384.png','outputPNGsha256':sha(P/'closed384.png'),'sourceHeld':False}
reuse={'sourceFrameId':fid(old),'sourcePNG':'reference-awake-source1024.png','sourcePNGsha256':sha(P/'reference-awake-source1024.png'),'speciesId':'california_quail','pose':'exact-existing-awake','registration':{'method':'exact existing source/export reused unchanged','sourceCanvas':[1024,1024],'outputCanvas':[N,N],'wholeCanvasScaleXY':[.375,.375],'perPoseFit':False,'perPoseTranslation':False},'outputPNG':'reused-awake384.png','outputPNGsha256':sha(P/'reused-awake384.png')}
primary={'batchId':P.name,'nativeCalls':1,'original':'original.png','originalSHA256':sha(P/'original.png'),'prompt':'prompt.txt','promptSHA256':sha(P/'prompt.txt'),'frames':[newrec],'reusedFrames':[reuse],'outputMetadata':['texture-review-manifest.json','frame-to-action-map.json','body-contact-diagnostics.json','alpha-edge-diagnostics.json','behavior-handoff.json'],'sourceStatus':'one actual closure; independent normal-size review pending','newSourceHeld':False,'notes':['One new actual eyelid closure, zero new neutral/look.','Exact awake source/render/geometry and idle90 unchanged.','Whole native1254→384 nearest only; no fit,snap,translation,bodyresize,paint,cleanup.','Inherited toe coordinates remain visible toe-region markers; not physical support acceptance.','Blink42/3/45 authored ticks, not biological timing.']};js('PRIMARY-SOURCE-MANIFEST.json',primary)
rows=[]
for i,rec in enumerate([reuse,newrec]):rows.append({'primarySourceFrameId':rec['sourceFrameId'],'primarySourcePNG':rec['sourcePNG'],'primarySourcePNGsha256':rec['sourcePNGsha256'],'newDrawing':i==1,'renderFrameId':frames[i]['id'],'atlasRect':frames[i]['sourceRect'],'outputPNG':rec['outputPNG'],'outputPNGsha256':rec['outputPNGsha256']})
js('frame-to-action-map.json',{'batchId':P.name,'speciesId':'california_quail','renderClipId':'blink','newSourceHeld':False,'manifest':{'file':'texture-review-manifest.json','sha256':sha(P/'texture-review-manifest.json'),'profile':'chirp-texture-review-v1','canonicalSchemaValidation':'NOT_RUN'},'atlasBinding':{'file':'blink-atlas384.png','sha256':sha(P/'blink-atlas384.png'),'width':2*N,'height':N,'alpha':'straight-rgba8'},'sourceToRenderFrames':rows,'clips':clips,'projectionScope':'source-only blink review; old neutral unchanged; no active app binding','appBound':False,'SharpCanonicalAdmission':False})
bbox=[]
for a in aa:
 y,x=np.where(a[:,:,3]>=128);bbox.append([int(x.min()),int(y.min()),int(x.max()+1),int(y.max()+1)])
regions={'headBill':[240,155,299,209],'bodyWing':[177,214,281,272],'tail':[145,260,200,290],'feet':[195,275,274,310]};reg={}
for name,(x0,y0,x1,y1) in regions.items():
 a,b=[ar[y0:y1,x0:x1] for ar in aa];sa=a[:,:,3]>=128;sb=b[:,:,3]>=128;reg[name]={'roi':[x0,y0,x1,y1],'changedRGBApixels':int(np.any(a!=b,axis=2).sum()),'alpha128SilhouetteIoU':float((sa&sb).sum()/max(1,(sa|sb).sum()))}
probes=[]
for c in frames[0]['contacts']:
 x,y=c['x'],c['y'];probes.append({'id':c['id'],'xy':[x,y],'awakeRGBA':aa[0][y,x].tolist(),'newRGBA':aa[1][y,x].tolist(),'status':'visible toe-region pixel in both registered outputs; not physical support acceptance'})
js('body-contact-diagnostics.json',{'canvas':[N,N],'world':[W,W],'density':D,'pivot':[228,300],'bboxAlpha128':bbox,'visibleWidthWorld':[(b[2]-b[0])/D for b in bbox],'lowestRowWorld':[(b[3]-1)/D for b in bbox],'inheritedComparisonProbes':probes,'newContacts':frames[1]['contacts'],'regions':reg,'pixelEqualityAcceptanceGate':False,'physicsApproved':False,'producerDisposition':'Actual closed-eye/body/toe continuity pending normal236.307692CSS independent review; no repair/retry'})
al=[]
for name in ['reference-awake-source1024.png','original.png','reused-awake384.png','closed384.png']:
 ar=np.array(Image.open(P/name).convert('RGBA'));a=ar[:,:,3];red=(ar[:,:,0]>200)&(ar[:,:,1]<70)&(ar[:,:,2]<70)&(a>0)&(a<255);al.append({'file':name,'alpha1':int((a==1).sum()),'alpha2to127':int(((a>=2)&(a<=127)).sum()),'alpha128to254':int(((a>=128)&(a<=254)).sum()),'alpha255':int((a==255).sum()),'extremeRedPartialAlphaPixels':int(red.sum())})
js('alpha-edge-diagnostics.json',{'images':al,'predicate':'uint8 RGBA R>200,G<70,B<70,0<A<255','processing':'All native RGBA retained, nearest resize only; no threshold/recolor/cleanup.'})
js('behavior-handoff.json',{'speciesId':'california_quail','newDrawings':1,'newNeutral':0,'newLook':0,'reusedAwake':1,'idleClip':clips[0],'blinkClip':clips[1],'timingAuthored':True,'world':[W,W],'density':D,'pivot':[228,300],'rootMotion':'none; fixed registration','newSourceHeld':False,'newContacts':frames[1]['contacts'],'canonicalSchemaValidation':'NOT_RUN','MacBinding':'UNKNOWN','appBound':False,'activation':'none'})
args=read('native-call-arguments.json')['arguments'];assert args['prompt'].encode()==(P/'prompt.txt').read_bytes();js('prompt-byte-audit.json',{'exactPreparedAndSubmittedUTF8Match':True,'bytes':len((P/'prompt.txt').read_bytes()),'promptSHA256':sha(P/'prompt.txt'),'nativeArgumentsFileSHA256':sha(P/'native-call-arguments.json'),'referenceSHA256':sha(P/'reference-awake-source1024.png'),'calls':1,'retries':0})
def chunk(t,d):return struct.pack('>I',len(d))+t+d+struct.pack('>I',zlib.crc32(t+d)&0xffffffff)
out=b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',N,N,8,6,0,0,0))+chunk(b'acTL',struct.pack('>II',3,1));seq=0
for i,(im,ticks) in enumerate([(awake,42),(new,3),(awake,45)]):
 out+=chunk(b'fcTL',struct.pack('>IIIIIHHBB',seq,N,N,0,0,ticks,30,0,0));seq+=1;data=zlib.compress(b''.join(b'\0'+im.tobytes()[y*N*4:(y+1)*N*4] for y in range(N)))
 if i==0:out+=chunk(b'IDAT',data)
 else:out+=chunk(b'fdAT',struct.pack('>I',seq)+data);seq+=1
out+=chunk(b'IEND',b'');(P/'blink-preview.apng').write_bytes(out)
g=[]
for im in [awake,new,awake]:
 bg=Image.new('RGBA',(N,N),'#e5e0cd');bg.alpha_composite(im);g.append(bg.convert('RGB').resize((round(W),round(W)),Image.Resampling.NEAREST))
g[0].save(P/'blink-preview.gif',save_all=True,append_images=g[1:],duration=[1400,100,1500],disposal=2)
sheet=Image.new('RGBA',(1040,620),'#e9e2d0');dr=ImageDraw.Draw(sheet)
for j,(im,label) in enumerate([(awake,'exact old awake'),(new,'new closed candidate')]):
 for k,(bg,color) in enumerate([('light','#e5e0cd'),('dark','#182a32')]):
  pane=Image.new('RGBA',(N,N),color);pane.alpha_composite(im);sheet.alpha_composite(pane.resize((round(W),round(W)),Image.Resampling.NEAREST),(10+j*520+k*250,28));dr.text((10+j*520+k*250,8),label+' '+bg,fill='#293c2e')
 for k,(roi,title) in enumerate([((240,150,300,210),'head x3'),((195,274,278,311),'feet x3')]):
  crop=im.crop(roi);bg=Image.new('RGBA',crop.size,'#e5e0cd');bg.alpha_composite(crop);sheet.alpha_composite(bg.resize((bg.width*3,bg.height*3),Image.Resampling.NEAREST),(10+j*520,290+k*200));dr.text((270+j*520,290+k*200),title,fill='#293c2e')
sheet.save(P/'normal-light-dark-and-crops.png')
(P/'README.md').write_text('# California Quail blink source review\n\nOne native edit/one actual new fully closed eye; exact old awake source and384 export retained. Independent normal body/toe continuity review pending. No new neutral/look. Toe markers remain visible-art probes, not physical contact acceptance.\n\nFull native1254→384 nearest only; no fit,snap,translation,bodyresize,paint or alpha cleanup. Output384, density1.625, world236.307692 CSS square; exact old pivot228,300. Old awake-only idle90 unchanged. Separate authored blink42/3/45 at30Hz,90ticks/3000ms, final sample89 held until deadline. APNG/PNG preserve RGBA, GIF is a light-composited palette preview.\n\nNo Mac binding, actual app runtime or physical contact approval; Zod/Sharp not run.\n')
print(json.dumps({'newSource':newrec['sourceFrameId'],'outputSHA256':newrec['outputPNGsha256'],'bbox':bbox,'visibleWorld':[(b[2]-b[0])/D for b in bbox],'probes':probes},indent=2))
