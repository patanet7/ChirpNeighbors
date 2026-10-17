from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib,shutil,struct,zlib
P=Path(__file__).parent;R=Path('/workspace/asset-production');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();fid=lambda im:'frame.sha256.'+hashlib.sha256(f'RGBA8;{im.width}x{im.height};'.encode()+im.tobytes()).hexdigest();js=lambda n,v:(P/n).write_text(json.dumps(v,indent=2)+'\n');native=Image.open(P/'original.png').convert('RGBA');old=Image.open(P/'reference-awake-source1024.png').convert('RGBA');awake=Image.open(P/'reused-awake96.png').convert('RGBA');look=native.resize((96,96),Image.Resampling.NEAREST);look.save(P/'look96.png');assert old.resize((96,96),Image.Resampling.NEAREST).tobytes()==awake.tobytes();shutil.copy2(P/'original.png',P/'look-native.png');imgs=[awake,look];atlas=Image.new('RGBA',(192,96));atlas.paste(awake,(0,0));atlas.paste(look,(96,0));atlas.save(P/'look-atlas96.png');ids=['finch-male-open-96','house-finch-look-viewer-96'];contacts=[{'id':'foot-a','x':45,'y':73},{'id':'foot-b','x':48,'y':74}];frames=[]
for i,im in enumerate(imgs):
 ar=np.array(im)
 for c in contacts:assert ar[c['y'],c['x'],3]>0
 frames.append({'id':ids[i],'sourceRect':{'x':96*i,'y':0,'width':96,'height':96},'canvas':{'width':96,'height':96},'trim':{'x':0,'y':0},'pivot':{'x':48,'y':75},'contacts':contacts,'world':{'width':96,'height':96},'sourcePixelsPerWorldUnit':1})
clips=[{'id':'idle','tickRate':30,'loop':True,'frames':[{'frameId':ids[0],'durationTicks':90}]},{'id':'look','tickRate':30,'loop':False,'frames':[{'frameId':ids[0],'durationTicks':30},{'frameId':ids[1],'durationTicks':12},{'frameId':ids[0],'durationTicks':30}]}]
m={'schemaVersion':1,'profile':'chirp-texture-review-v1','scope':'review-only','approval':'unreviewed','activation':'none','source':{'sha256':sha(P/'look-atlas96.png'),'creator':'Chirp cloud source-preserving exporter','tool':'Pillow whole-native-canvas nearest export','toolVersion':Image.__version__ if hasattr(Image,'__version__') else '12.3.0','rights':'unreviewed','fidelity':'unreviewed'},'atlas':{'width':192,'height':96,'alpha':'straight-rgba8','colorSpace':'srgb'},'frames':frames,'clips':clips};js('texture-review-manifest.json',m)
new={'sourceFrameId':fid(native),'sourcePNG':'look-native.png','sourcePNGsha256':sha(P/'look-native.png'),'speciesId':'house_finch','pose':'look-viewer','registration':{'method':'whole native canvas nearest resize only','sourceCanvas':list(native.size),'outputCanvas':[96,96],'wholeCanvasScaleXY':[96/native.width,96/native.height],'referenceSourceCanvas':[1024,1024],'nativeToReferenceWholeCanvasScaleXY':[1024/native.width,1024/native.height],'perPoseFit':False,'perPoseTranslation':False,'snap':False,'pixelPaint':False},'outputPNG':'look96.png','outputPNGsha256':sha(P/'look96.png')};reuse={'sourceFrameId':fid(old),'sourcePNG':'reference-awake-source1024.png','sourcePNGsha256':sha(P/'reference-awake-source1024.png'),'speciesId':'house_finch','pose':'existing-awake','registration':{'method':'exact existing source/output reused unchanged','sourceCanvas':[1024,1024],'outputCanvas':[96,96],'wholeCanvasScaleXY':[3/32,3/32],'perPoseFit':False,'perPoseTranslation':False},'outputPNG':'reused-awake96.png','outputPNGsha256':sha(P/'reused-awake96.png')};primary={'batchId':P.name,'nativeCalls':1,'original':'original.png','originalSHA256':sha(P/'original.png'),'prompt':'prompt.txt','promptSHA256':sha(P/'prompt.txt'),'frames':[new],'reusedFrames':[reuse],'outputMetadata':['texture-review-manifest.json','frame-to-action-map.json','body-contact-measurements.json','conditioning-selection.json','behavior-handoff.json'],'sourceStatus':'one actual head-turn drawing;source review pending;body/tail/feet redraw retained','notes':['0 new neutral/blink.','Whole native canvas1254to96NN only;no body bbox fit/snap/paint/translation.','25-35degree request is art direction,not actual angle measurement.','30/12/30ticks authored,not biological timing.','Portable zero-call legacy reuse audit retained in prior-reuse-audit/.']};js('PRIMARY-SOURCE-MANIFEST.json',primary)
maprows=[]
for i,f in enumerate([reuse,new]):maprows.append({'primarySourceFrameId':f['sourceFrameId'],'primarySourcePNG':f['sourcePNG'],'primarySourcePNGsha256':f['sourcePNGsha256'],'newDrawing':i==1,'lookOnlyNewDrawing':i==1,'renderFrameId':ids[i],'atlasRect':frames[i]['sourceRect'],'outputPNG':f['outputPNG'],'outputPNGsha256':f['outputPNGsha256']})
js('frame-to-action-map.json',{'batchId':P.name,'speciesId':'house_finch','lookOnlyNewDrawing':True,'renderClipId':'look','manifest':{'file':'texture-review-manifest.json','sha256':sha(P/'texture-review-manifest.json'),'profile':'chirp-texture-review-v1','canonicalSchemaValidation':'NOT_RUN;explicitlookcliprequirescurrentMacconfirmation'},'atlasBinding':{'file':'look-atlas96.png','sha256':sha(P/'look-atlas96.png'),'width':192,'height':96,'alpha':'straight-rgba8'},'sourceToRenderFrames':maprows,'clips':clips,'projectionScope':'look-only;own idle exactawake only,no change existing primary neutral/blink intake','appBound':False,'SharpCanonicalAdmission':False})
# Body/feet diagnostics, no equality acceptance gate.
arr=[np.array(i) for i in imgs];bboxes=[];foot=[];regions={'head':[43,34,68,56],'body-wing':[24,53,60,70],'tail':[12,63,39,78],'feet':[39,68,61,78]};regional={}
for ar in arr:
 y,x=np.where(ar[:,:,3]>=128);bboxes.append([int(x.min()),int(y.min()),int(x.max()+1),int(y.max()+1)]);row=[]
 for roi in [[39,68,49,78],[49,68,61,78]]:
  x0,y0,x1,y1=roi;y,x=np.where(ar[y0:y1,x0:x1,3]>=128);row.append({'roi':roi,'bbox':[int(x.min()+x0),int(y.min()+y0),int(x.max()+x0+1),int(y.max()+y0+1)],'centroid':[float(x.mean()+x0),float(y.mean()+y0)],'lowestRow':int(y.max()+y0)})
 foot.append(row)
for n,(x0,y0,x1,y1) in regions.items():
 a,b=[ar[y0:y1,x0:x1] for ar in arr];union=(a[:,:,3]>0)|(b[:,:,3]>0);sa=a[:,:,3]>=128;sb=b[:,:,3]>=128;regional[n]={'roi':[x0,y0,x1,y1],'changedRGBApixels':int(np.any(a!=b,axis=2).sum()),'positiveAlphaUnionPixels':int(union.sum()),'alpha128SilhouetteIoU':float((sa&sb).sum()/max(1,(sa|sb).sum()))}
metrics={'sourceCanvases':[[1024,1024],list(native.size)],'outputCanvas':[96,96],'worldCanvas':[96,96],'density':1,'pivot':[48,75],'contacts':contacts,'contactAlphaByFrame':[[int(ar[c['y'],c['x'],3]) for c in contacts] for ar in arr],'bboxAlpha128':bboxes,'footProxies':foot,'maxFootCentroidChangeWorld':max(float(np.linalg.norm(np.array(foot[0][i]['centroid'])-foot[1][i]['centroid'])) for i in [0,1]),'maxFootBaselineChangeWorld':max(abs(foot[0][i]['lowestRow']-foot[1][i]['lowestRow']) for i in [0,1]),'regionalComparisons':regional,'metricsLimits':'ROIs are inspection windows,not anatomical segmentation or equality acceptance gate. Alpha-positive fixed probes are not grip/physical support approval.','actualHeadAngleMeasured':False,'reviewDisposition':'pending independent normal96CSS readable head turn versus body/foot pop review'};js('body-contact-measurements.json',metrics)
js('behavior-handoff.json',{'speciesId':'house_finch','newAction':'look','newDrawings':1,'reusedAwake':1,'newNeutral':0,'newBlink':0,'lookOnlyNewDrawing':True,'renderClipId':'look','idleScope':'exactexistingawakeonly;oldprimaryneutral/blinkunchanged','lookSchedule':{'tickRate':30,'ticks':[30,12,30],'totalTicks':72,'loop':False,'timing':'authored'},'smoothHeadTurnClaimed':False,'actualAngleMeasured':False,'appBound':False,'canonicalSchemaValidation':'NOT_RUN','activation':'none','reviewStatus':'pending'})
# Exact APNG one-shot three authored key holds.
def chunk(t,b):return struct.pack('>I',len(b))+t+b+struct.pack('>I',zlib.crc32(t+b)&0xffffffff)
out=b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',96,96,8,6,0,0,0))+chunk(b'acTL',struct.pack('>II',3,1));seq=0
for i,(im,t) in enumerate(zip([awake,look,awake],[30,12,30])):
 out+=chunk(b'fcTL',struct.pack('>IIIIIHHBB',seq,96,96,0,0,t,30,0,0));seq+=1;raw=b''.join(b'\0'+row.tobytes() for row in np.array(im));data=zlib.compress(raw)
 if i==0:out+=chunk(b'IDAT',data)
 else:out+=chunk(b'fdAT',struct.pack('>I',seq)+data);seq+=1
out+=chunk(b'IEND',b'');(P/'look-preview.apng').write_bytes(out)
preview=[]
for im in [awake,look,awake]:
 pane=Image.new('RGBA',(192,96))
 for j,bg in enumerate(['#e5e0cd','#182a32']):a=Image.new('RGBA',(96,96),bg);a.alpha_composite(im);pane.alpha_composite(a,(j*96,0))
 preview.append(pane.convert('RGB'))
preview[0].save(P/'House-Finch-Look-Yard-Size.gif',save_all=True,append_images=preview[1:],duration=[1000,400,1000],disposal=2)
sheet=Image.new('RGBA',(640,460),'#eee8d9');d=ImageDraw.Draw(sheet)
for i,(name,im) in enumerate(zip(['exact existing awake','new head-turn study'],imgs)):
 x=i*320;d.text((x+8,5),name,fill='#243c31')
 for j,bg in enumerate(['#e5e0cd','#182a32']):a=Image.new('RGBA',(96,96),bg);a.alpha_composite(im);sheet.alpha_composite(a,(x+8+j*120,25))
 sheet.alpha_composite(im.resize((288,288),Image.Resampling.NEAREST),(x+8,140))
sheet.save(P/'light-dark-normal-size.png')
for name,roi,size in [('head-inspection.png',(42,32,70,57),(224,200)),('contact-inspection.png',(37,65,63,80),(260,150))]:
 sheet=Image.new('RGBA',(size[0]*2,size[1]),'#dcd8c7')
 for i,im in enumerate(imgs):sheet.alpha_composite(im.crop(roi).resize(size,Image.Resampling.NEAREST),(i*size[0],0))
 sheet.save(P/name)
shutil.copytree(R/'audits/house-finch-look-reuse-before-generation-v1',P/'prior-reuse-audit',dirs_exist_ok=True)
args=json.loads((P/'prepared-native-arguments.json').read_text())['arguments'];assert args['prompt'].encode()==(P/'prompt.txt').read_bytes();js('prompt-byte-audit.json',{'exactSubmittedUTF8Match':True,'promptBytes':2591,'promptSHA256':sha(P/'prompt.txt'),'nativeCalls':1,'newCallsAfterReturn':0})
print(json.dumps({'newSourceID':new['sourceFrameId'],'newSourceSHA256':new['sourcePNGsha256'],'newOutputSHA256':new['outputPNGsha256'],'manifestSHA256':sha(P/'texture-review-manifest.json'),'mapSHA256':sha(P/'frame-to-action-map.json'),'metrics':metrics},indent=2))
