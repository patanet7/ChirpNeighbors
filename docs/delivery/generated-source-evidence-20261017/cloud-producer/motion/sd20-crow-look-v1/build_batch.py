"""One native look; exact old awake; whole-canvas nearest exports only."""
from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib,numpy as np,struct,zlib,shutil
P=Path(__file__).parent;N=192
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def J(n,v):(P/n).write_text(json.dumps(v,indent=2)+'\n')
def fid(im):return 'frame.sha256.'+hashlib.sha256(f'RGBA8;{im.width}x{im.height};'.encode()+im.tobytes()).hexdigest()
old=Image.open(P/'reused-awake-source1024.png').convert('RGBA');new=Image.open(P/'look-native.png').convert('RGBA')
awake=Image.open(P/'reused-awake192.png').convert('RGBA');turned=new.resize((N,N),Image.Resampling.NEAREST);turned.save(P/'look192.png');images=[awake,turned]
assert awake.tobytes()==old.resize((N,N),Image.Resampling.NEAREST).tobytes()
atlas=Image.new('RGBA',(N*2,N));atlas.paste(awake,(0,0));atlas.paste(turned,(N,0));atlas.save(P/'look-atlas192.png')
v=json.loads((P/'existing-neutral-blink-manifest-reference.json').read_text());f=json.loads(json.dumps(v['frames'][0]));g=json.loads(json.dumps(f));g['id']='crow-look-viewer-192';g['sourceRect']['x']=N
v['frames']=[f,g];v['source'].update(sha256=sha(P/'look-atlas192.png'),creator='Chirp bounded native Crow look exporter',tool='native image_gen; direct nearest wholecanvas output',toolVersion='native model not exposed; Pillow12.3.0');v['clips']=[{'id':'idle','tickRate':30,'loop':True,'frames':[{'frameId':f['id'],'durationTicks':90}]},{'id':'look','tickRate':30,'loop':False,'frames':[{'frameId':f['id'],'durationTicks':30},{'frameId':g['id'],'durationTicks':12},{'frameId':f['id'],'durationTicks':30}]}];J('texture-review-manifest.json',v)
rows=[]
for source,png,output,pose,isnew in [(old,'reused-awake-source1024.png','reused-awake192.png','existing supported awake neutral unchanged',False),(new,'look-native.png','look192.png','toward-viewer skull/bill turn open eyes; compatibility pending',True)]:
 row={'sourceFrameId':fid(source),'sourcePNG':png,'sourcePNGsha256':sha(P/png),'speciesId':'american_crow','pose':pose,'newDrawing':isnew,'outputPNG':output,'outputPNGsha256':sha(P/output)}
 if isnew:row['registration']={'nativeCanvas':list(new.size),'referenceCanvas':[1024,1024],'wholeCallDensityNormalization':1024/new.width,'directNativeToOutputRatio':N/new.width,'integerOriginTranslation':[0,0],'perPoseBodyFit':False,'paint':False,'warp':False,'alphaErasure':False}
 rows.append(row)
J('PRIMARY-SOURCE-MANIFEST.json',{'batchId':P.name,'nativeCalls':1,'original':'original.png','originalSHA256':sha(P/'original.png'),'prompt':'prompt.txt','promptSHA256':sha(P/'prompt.txt'),'frames':[rows[1]],'reusedFrames':[rows[0]],'lookOnlyNewDrawing':True,'newNeutralDrawings':0,'newBlinkDrawings':0,'outputMetadata':['texture-review-manifest.json','frame-to-action-map.json','anchor-measurements.json','body-contact-measurements.json','behavior-handoff.json','verification.json','browser-verification.json','independent-review.json'],'sourceStatus':'one new look candidate; body/contact compatibility pending independent normal-size review; no provisional usefulness claimed yet','notes':['Whole native1254canvas to192 nearest; no body-envelope fit/paint/warp/contact snap.','Exact old awake reused; no neutral/blink generation.','Native model changed body/tail/feet; retain drift for independent provisional-versus-held decision.','Two actual distinct poses; no generated turn intermediates or smooth-motion claim.']})
mapping={'batchId':P.name,'speciesId':'american_crow','lookOnlyNewDrawing':True,'renderClipId':'look','manifest':{'file':'texture-review-manifest.json','sha256':sha(P/'texture-review-manifest.json'),'profile':'chirp-texture-review-v1'},'atlasBinding':{'file':'look-atlas192.png','sha256':sha(P/'look-atlas192.png'),'width':N*2,'height':N,'alpha':'straight-rgba8','bindRule':'wrapper PNG filename/sha/dimensions explicitly bound; strict profile has no atlas filename field'},'sourceToRenderFrames':[{'primarySourceFrameId':s['sourceFrameId'],'primarySourcePNG':s['sourcePNG'],'primarySourcePNGsha256':s['sourcePNGsha256'],'newDrawing':s['newDrawing'],'lookOnlyNewDrawing':s['newDrawing'],'renderFrameId':frame['id'],'atlasRect':frame['sourceRect'],'outputPNG':s['outputPNG'],'outputPNGsha256':s['outputPNGsha256']} for s,frame in zip(rows,[f,g])],'clips':v['clips'],'projectionScope':'look-only overlay candidate; exact awake idle fallback; existing neutral/blink intake untouched','canonicalSchemaValidation':'NOT_RUN','currentMacContract':'UNKNOWN','packetBindingReady':False,'appBound':False};J('frame-to-action-map.json',mapping)
arrays=[np.array(i) for i in images];y,x=np.indices((N,N));anchors=[];bboxes=[];feet=[]
for i,a in enumerate(arrays):
 yy,xx=np.where(a[:,:,3]>=128);bboxes.append([int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)])
 yy,xx=np.where((a[:,:,3]>=128)&(x>=143)&(x<170)&(y>=49)&(y<66));bx=int(xx.max());ys=yy[xx==bx];bill=[bx,int(ys[len(ys)//2])]
 eye=[[140,50],[139,52]][i];torso=[116,110];sample=lambda q:a[q[1],q[0]].tolist()
 anchors.append({'renderFrameId':[f['id'],g['id']][i],'billTip':{'pixel':bill,'RGBA':sample(bill),'method':'perpose alpha128 maxX in ROI[143,49,170,66], middle occupiedY','caveat':'raster terminal proxy not subpixel anatomical tracking'},'headEyeReference':{'pixel':eye,'RGBA':sample(eye),'method':'visually selected eye-area positive-alpha pixel','uncertaintyOutputPxAtLeast':1,'caveat':'approximate eye region not certified pupil centre'},'torsoReference':{'pixel':torso,'RGBA':sample(torso),'meaning':'actual body sample not support'},'declaredPivot':f['pivot'],'technicalFootContacts':[{'id':c['id'],'pixel':[c['x'],c['y']],'RGBA':sample([c['x'],c['y']])} for c in f['contacts']]})
 parts=[]
 for side in [x<112,x>=112]:
  yy,xx=np.where((a[:,:,3]>=128)&side&(x>=82)&(x<145)&(y>=132)&(y<161));parts.append({'bbox':[int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)],'lowestRow':int(yy.max()),'centroid':[float(xx.mean()),float(yy.mean())]})
 feet.append(parts)
J('anchor-measurements.json',{'scope':'actual raster samples; declared pivot and technical alpha markers do not certify physical sole support','frames':anchors})
d=f['sourcePixelsPerWorldUnit'];drift=max(float(np.linalg.norm(np.array(a['centroid'])-b['centroid'])) for a,b in zip(feet[0],feet[1]));baseline=max(abs(a['lowestRow']-b['lowestRow']) for a,b in zip(feet[0],feet[1]))
J('body-contact-measurements.json',{'sourceCanvases':[[1024,1024],list(new.size)],'outputCanvas':[N,N],'wholeNativeCanvasNormalization':1024/new.width,'normalizationBasis':'fullcanvas dimensions only, not body/head/bbox fit','densityPreserved':d,'worldPreserved':f['world'],'pivotPreserved':f['pivot'],'contactsPreserved':f['contacts'],'outputBBoxAlpha128':bboxes,'visibleProjectedWidthWorld':[(b[2]-b[0])/d for b in bboxes],'widthInterpretation':'head projection and native redraw shorten envelope; no bbox refit','footProxies':feet,'maxFootCentroidChangeOutputPx':drift,'maxFootCentroidChangeWorld':drift/d,'maxFootBaselineRowChangeOutputPx':baseline,'maxFootBaselineRowChangeWorld':baseline/d,'bodyRGBADifferentPixels':int(np.any(arrays[0]!=arrays[1],axis=2).sum()),'bodyPixelEqualityAcceptanceGate':False,'requestedHeadTurnDegrees':[25,35],'actualHeadAngleMeasured':False,'sourceReviewDisposition':'pending; body jump may require held-look-candidate decision'})
up=P.parent/'sd20-crow-neutral-blink-v1';names=['neutral-source1024.png','neutral192.png','blink-source1024.png','blink192.png','texture-review-manifest.json','neutral-blink-atlas192.png'];J('upstream-protection.json',{'files':[{'file':'motion/sd20-crow-neutral-blink-v1/'+n,'sha256':sha(up/n)} for n in names],'existingNeutralBlinkNeverReplaced':True})
J('behavior-handoff.json',{'speciesId':'american_crow','newAction':'look','newDrawings':1,'reusedAwake':1,'newNeutralDrawings':0,'newBlinkDrawings':0,'lookOnlyNewDrawing':True,'renderClipId':'look','idleScope':'own exact-awake fallback only; existing neutral/blink authoritative','lookSchedule':{'tickRate':30,'ticks':[30,12,30],'oneShot':True,'totalMs':2400},'headTurnIntermediatesGenerated':0,'smoothHeadTurnClaimed':False,'actualAngleMeasured':False,'sourcePacketByteMappingVerified':True,'runtimePacketBindingReady':False,'packetBindingReady':False,'appBound':False,'canonicalSchemaValidation':'NOT_RUN','currentMacContract':'UNKNOWN','activation':'none','sourceAdmission':'pending independent provisional versus held decision; body/tail/feet redraw explicitly retained'})
J('reference-rights-provenance.json',{'speciesId':'american_crow','sourceFrameId':rows[0]['sourceFrameId'],'modelReference':rows[0]['sourcePNG'],'sourcePNGsha256':rows[0]['sourcePNGsha256'],'sourceRole':'exact existing generated supported awake','rights':'unreviewed','externalPhotoPixelsSupplied':False,'oldOriginalFamily':'sd20-crow-neutral-blink-v1','oldFamilyOriginalSHA256':'4bbfadfd874fdac874ee11b8408336b17117a7c161b4a6e375366ad71292fbf8','noNewCanonClaim':True})
def chunk(k,data):return struct.pack('>I',len(data))+k+data+struct.pack('>I',zlib.crc32(k+data)&0xffffffff)
png=b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',N,N,8,6,0,0,0))+chunk(b'acTL',struct.pack('>II',3,1));seq=0
for i,(idx,ticks) in enumerate(zip([0,1,0],[30,12,30])):
 png+=chunk(b'fcTL',struct.pack('>IIIIIHHBB',seq,N,N,0,0,ticks,30,0,0));seq+=1;data=zlib.compress(b''.join(b'\0'+arrays[idx][row].tobytes() for row in range(N)),9)
 if i==0:png+=chunk(b'IDAT',data)
 else:png+=chunk(b'fdAT',struct.pack('>I',seq)+data);seq+=1
(P/'look-preview.apng').write_bytes(png+chunk(b'IEND',b''));gif=[];yard=round(f['world']['width'])
for i in [0,1,0]:
 im=images[i].resize((yard,yard),Image.Resampling.NEAREST);bg=Image.new('RGBA',im.size,'#d9d4bd');bg.alpha_composite(im);gif.append(bg.convert('RGB'))
gif[0].save(P/'Crow-Look-Yard-Size.gif',save_all=True,append_images=gif[1:],duration=[1000,400,1000],optimize=False)
for name,rect,size in [('head',(655,190,905,395),(500,410)),('contact',(420,700,780,825),(600,210))]:
 sheet=Image.new('RGBA',(size[0]*2,size[1]+25),'#d9d4bd');draw=ImageDraw.Draw(sheet)
 for i,(im,label) in enumerate(zip([old,new],['EXACT OLD AWAKE','ONE NEW LOOK CANDIDATE'])):
  r=rect if i==0 else tuple(round(v*new.width/1024) for v in rect);draw.text((i*size[0]+6,5),label,fill='#24342b');sheet.alpha_composite(im.crop(r).resize(size,Image.Resampling.NEAREST),(i*size[0],25))
 sheet.convert('RGB').save(P/(name+'-inspection.png'))
sheet=Image.new('RGB',(yard*2,yard*2+40),'#d9d4bd');draw=ImageDraw.Draw(sheet)
for row,color in enumerate(['#d9d4bd','#17221f']):
 for i,im in enumerate(images):
  tile=Image.new('RGBA',(yard,yard),color);tile.alpha_composite(im.resize((yard,yard),Image.Resampling.NEAREST));sheet.paste(tile.convert('RGB'),(i*yard,row*(yard+20)+20));draw.text((i*yard+4,row*(yard+20)+3),['OLD AWAKE','NEW LOOK'][i],fill='#24342b')
sheet.save(P/'light-dark-normal-size.png')
J('preview-data.json',{'profile':v,'atlas':'look-atlas192.png','frameToPrimary':{frame['id']:s['sourceFrameId'] for frame,s in zip([f,g],rows)},'actualWorldCanvas':f['world'],'normalCSSCanvas':[f['world']['width']]*2,'canonicalSchemaValidation':'NOT_RUN'})
print(json.dumps({'newPrimary':rows[1]['sourceFrameId'],'billPoints':[a['billTip']['pixel'] for a in anchors],'footBaselineOutputChange':baseline,'footCentroidWorld':drift/d,'density':d,'world':f['world']}))
