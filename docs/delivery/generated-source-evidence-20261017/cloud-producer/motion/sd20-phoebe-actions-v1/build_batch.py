from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib,struct,zlib,shutil
P=Path(__file__).parent
sha=lambda b:hashlib.sha256(b).hexdigest()
frameid=lambda im:'frame.sha256.'+sha(f'RGBA8;{im.width}x{im.height};'.encode()+im.tobytes())
def writejson(name,v):(P/name).write_text(json.dumps(v,indent=2)+'\n')
canon=Path('/workspace/asset-production/new-species/sd20-three-canon-v1/black_phoebe/source1024.png')
shutil.copy2(canon,P/'neutral-source1024.png')
neutral=Image.open(canon).convert('RGBA');assert frameid(neutral)=='frame.sha256.afdb316304688a04c8ea5130d42685c0a6bb74e922a8d0c5ac34637dd720850f'
raw=Image.open(P/'original.png').convert('RGBA');assert raw.size==(2172,724)
names=['neutral','tail-up','tail-down','closed'];imgs=[neutral];lineage=[]
(P/'frames1024').mkdir(exist_ok=True);(P/'frames96').mkdir(exist_ok=True);(P/'native-cells').mkdir(exist_ok=True)
a=np.array(neutral);target=(a[:,:,3]>=128);yy,xx=np.indices((1024,1024));footarea=(yy>=770)&(yy<812)&(xx>=490)&(xx<710)
lineage.append({'phase':'neutral','drawingKind':'existing-canon','immutableSourceFrameId':frameid(neutral),'sourcePNG':'neutral-source1024.png','sourcePNGsha256':sha(canon.read_bytes()),'sourceCanvas':[1024,1024],'registration':{'scale':1,'translation':[0,0]}})
for i,name in enumerate(names[1:]):
 cell=raw.crop((i*724,0,(i+1)*724,724));cell.save(P/'native-cells'/f'{name}.png')
 # Single scale1 for every native cell; only integer foot-region alignment.
 best=None
 for dy in range(152,166):
  for dx in range(94,114):
   trial=Image.new('RGBA',(1024,1024));trial.paste(cell,(dx,dy));mask=np.array(trial)[:,:,3]>=128
   inter=(mask&target&footarea).sum();union=((mask|target)&footarea).sum();score=inter/max(1,union)
   if best is None or score>best[0]:best=(score,dx,dy)
 _,dx,dy=best;registered=Image.new('RGBA',(1024,1024));registered.paste(cell,(dx,dy));imgs.append(registered)
 lineage.append({'phase':name,'drawingKind':'new-native-drawn-pose','immutableSourceFrameId':frameid(cell),'sourcePNG':f'native-cells/{name}.png','sourcePNGsha256':sha((P/'native-cells'/f'{name}.png').read_bytes()),'originalAtlasPNG':'original.png','originalAtlasPNGsha256':sha((P/'original.png').read_bytes()),'originalSourceRect':[i*724,0,724,724],'sourceCanvas':[724,724],'registration':{'scale':1,'translation':[dx,dy],'method':'maximize alpha128 foot-mask IoU in fixed source region x490:710,y770:812; integer translation only; no per-frame scaling','footMaskIoU':best[0]},'registeredDerivativeFrameId':frameid(registered)})
images=[]
for name,im,line in zip(names,imgs,lineage):
 im.save(P/'frames1024'/f'{name}.png');out=im.resize((96,96),Image.Resampling.NEAREST);out.save(P/'frames96'/f'{name}.png');images.append(out);line.update(registeredPNG=f'frames1024/{name}.png',registeredPNGsha256=sha((P/'frames1024'/f'{name}.png').read_bytes()),outputPNG=f'frames96/{name}.png',outputPNGsha256=sha((P/'frames96'/f'{name}.png').read_bytes()),outputFrameId=frameid(out),export={'wholeCanvas':[1024,1024],'output':[96,96],'scale':3/32,'resampling':'nearest','alpha':'straight original RGBA; no quantization or alpha threshold','perFrameFit':False})
arrays=[np.array(im) for im in images];common=np.logical_and.reduce([a[:,:,3]>=128 for a in arrays]);y,x=np.indices((96,96));contacts=[]
for id,side,targetx in [('foot-1',x<57,53),('foot-2',x>=57,60)]:
 candidates=np.argwhere(common&side&(y>=71)&(y<=76)&(x>=47)&(x<=66));assert len(candidates)>0
 cy,cx=min(candidates,key=lambda p:(-int(p[0]),abs(p[1]-targetx)));contacts.append({'id':id,'x':int(cx),'y':int(cy)})
atlas=Image.new('RGBA',(384,96));frames=[];density=19/18
for i,(name,im) in enumerate(zip(names,images)):
 atlas.paste(im,(96*i,0));frames.append({'id':'black-phoebe-'+name+'-96','sourceRect':{'x':96*i,'y':0,'width':96,'height':96},'canvas':{'width':96,'height':96},'trim':{'x':0,'y':0},'pivot':{'x':57,'y':75},'contacts':contacts,'world':{'width':96/density,'height':96/density},'sourcePixelsPerWorldUnit':density})
atlas.save(P/'idle-atlas96.png')
seq=[0,1,2,0,3,0];ticks=[90,3,3,60,3,30]
base={'schemaVersion':1,'profile':'chirp-texture-review-v1','scope':'review-only','approval':'unreviewed','activation':'none','source':{'sha256':sha((P/'idle-atlas96.png').read_bytes()),'creator':'Chirp cloud source-preserving exporter','tool':'Pillow nearest canvas export','toolVersion':'12.3.0','rights':'unreviewed','fidelity':'unreviewed'},'atlas':{'width':384,'height':96,'alpha':'straight-rgba8','colorSpace':'srgb'},'frames':frames,'clips':[{'id':'idle','tickRate':30,'loop':True,'frames':[{'frameId':frames[i]['id'],'durationTicks':t} for i,t in zip(seq,ticks)]}]}
writejson('texture-review-manifest.json',base)
# A quieter practical intake choice: original neutral + new blink, excluding strong tail pump.
blink=Image.new('RGBA',(192,96));blink.paste(images[0],(0,0));blink.paste(images[3],(96,0));blink.save(P/'blink-atlas96.png')
bm=json.loads(json.dumps(base));bm['source']['sha256']=sha((P/'blink-atlas96.png').read_bytes());bm['atlas']['width']=192;bm['frames']=[bm['frames'][0],bm['frames'][3]];bm['frames'][1]['sourceRect']['x']=96;bm['clips'][0]['frames']=[{'frameId':frames[i]['id'],'durationTicks':t} for i,t in [(0,90),(3,3),(0,90)]];writejson('blink-manifest.json',bm)
def chunk(kind,data):return struct.pack('>I',len(data))+kind+data+struct.pack('>I',zlib.crc32(kind+data)&0xffffffff)
def apng(name,indices,durations):
 png=b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',96,96,8,6,0,0,0))+chunk(b'acTL',struct.pack('>II',len(indices),0));number=0
 for k,(idx,t) in enumerate(zip(indices,durations)):
  png+=chunk(b'fcTL',struct.pack('>IIIIIHHBB',number,96,96,0,0,t,30,0,0));number+=1;a=arrays[idx];data=zlib.compress(b''.join(b'\0'+a[row].tobytes() for row in range(96)),9)
  if k==0:png+=chunk(b'IDAT',data)
  else:png+=chunk(b'fdAT',struct.pack('>I',number)+data);number+=1
 png+=chunk(b'IEND',b'');(P/name).write_bytes(png)
apng('normal-speed.apng',seq,ticks);apng('blink-normal-speed.apng',[0,3,0],[90,3,90])
g=[]
for idx in seq:
 bg=Image.new('RGBA',(96,96),'#d9d4bd');bg.alpha_composite(images[idx]);g.append(bg.convert('RGB'))
g[0].save(P/'normal-speed-approx.gif',save_all=True,append_images=g[1:],duration=[3000,100,100,2000,100,1000],loop=0,optimize=False)
# A normal-size row and a4x nearest row for anatomical inspection.
sheet=Image.new('RGBA',(1024,620),'#d9d4bd');draw=ImageDraw.Draw(sheet)
for i,(name,im) in enumerate(zip(names,images)):
 draw.text((i*250+20,15),name,fill='#262622');sheet.alpha_composite(im,(i*250+70,45))
 # Separate each4x tile without overprinting neighbouring tiles.
 crop=im.crop((0,25,80,82)).resize((240,171),Image.Resampling.NEAREST);sheet.alpha_composite(crop,(i*250+5,210))
draw.text((15,420),'Top row:96px canvases. Bottom:3x pixel inspection (cropped).',fill='#262622');draw.text((15,445),'Neutral source reused. Three new drawings; integer registration only. Tail-up remains provisional.',fill='#262622');sheet.save(P/'contact-sheet.png')
bboxes=[];footstats=[]
for name,a in zip(names,arrays):
 mask=a[:,:,3]>=128;yy,xx=np.where(mask);bboxes.append({'phase':name,'bboxAlpha128':[int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)],'visibleWidthOutputPx':int(xx.max()+1-xx.min()),'visibleHeightOutputPx':int(yy.max()+1-yy.min()),'visibleWidthWorldUnits':float((xx.max()+1-xx.min())/density)})
 band=mask&(y>=72)&(y<=76)&(x>=46)&(x<=67);fy,fx=np.where(band);footstats.append({'phase':name,'footCoreBBox':[int(fx.min()),int(fy.min()),int(fx.max()+1),int(fy.max()+1)],'groundBoundaryOutputY':int(fy.max()+1),'pixels':len(fx),'centroidOutputXY':[float(fx.mean()),float(fy.mean())]})
metrics={'sourceCanvas':[1024,1024],'nativeGeneratedCell':[724,724],'outputCanvas':[96,96],'sourceToOutputScale':3/32,'outputPixelsPerWorldUnit':density,'worldCanvas':[96/density,96/density],'neutralTargetLengthWorldUnits':54,'relativeScaleBiologicallyApproved':False,'visibleBounds':bboxes,'actualRasterFootCore':footstats,'maxFootGroundBoundaryRangeOutputPx':max(f['groundBoundaryOutputY'] for f in footstats)-min(f['groundBoundaryOutputY'] for f in footstats),'contacts':contacts,'contactMeaning':'Shared positive-alpha pixels only, not anatomical toe/physical support approval. Integer registration aligns source feet but does not guarantee fixed whole-foot geometry.','singleExportScale':True,'perFrameFit':False,'durationTicks':sum(ticks),'tickRate':30,'durationMs':sum(ticks)/30*1000,'loopEndpointChangedPixels':0,'loopCaveat':'Endpoints reuse neutral; intermediate body/foot flicker needs actual normal-speed yard review.','newDrawings':3,'existingDrawingsReused':1,'imageGenerationCalls':1,'riggedFrames':0,'normalYardVerified':False,'fullAppAdmission':False}
writejson('runtime-measurements.json',metrics);writejson('source-lineage.json',{'schemaVersion':1,'newDrawings':3,'reusedDrawings':1,'generationCalls':1,'nativeOriginalSha256':sha((P/'original.png').read_bytes()),'frames':lineage})
print(json.dumps({'contacts':contacts,'bounds':bboxes,'feet':footstats,'sourceIds':[l['immutableSourceFrameId'] for l in lineage]},indent=2))
