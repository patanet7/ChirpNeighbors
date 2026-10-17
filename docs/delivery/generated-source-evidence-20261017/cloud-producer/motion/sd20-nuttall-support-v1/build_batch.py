from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib,numpy as np,struct,zlib
P=Path(__file__).parent;BATCH='sd20-nuttall-support-v1';sha=lambda b:hashlib.sha256(b).hexdigest();fid=lambda im:'frame.sha256.'+sha(('RGBA8;%dx%d;'%im.size).encode()+im.tobytes())
def dump(n,v):P.joinpath(n).write_text(json.dumps(v,indent=2)+'\n')
native=Image.open(P/'original.png').convert('RGBA');assert native.size==(1774,887);frames=[];sources=[];records=[];measure=[]
for i,(pose,dx) in enumerate([('neutral',0),('look',51)]):
 raw=native.crop((i*887,0,(i+1)*887,887));raw.save(P/f'{pose}-native-cell.png');source=Image.new('RGBA',(1024,1024));source.paste(raw,(dx,0));source.save(P/f'{pose}-source1024.png');out=source.resize((192,192),Image.Resampling.NEAREST);out.save(P/f'{pose}192.png');sources.append(source);frames.append(out)
 records.append({'sourceFrameId':fid(source),'sourcePNG':f'{pose}-source1024.png','sourcePNGsha256':sha((P/f'{pose}-source1024.png').read_bytes()),'speciesId':'nuttall_s_woodpecker','pose':pose,'registration':{'nativeOriginal':'original.png','nativeCellRect':[i*887,0,887,887],'nativeCellRgbaId':fid(raw),'sourceCanvas':[1024,1024],'translation':[dx,0],'callWideSourceScale':1,'method':'equal native887px cells padded on stable1024canvas; head-independent torso/toe layout translation estimate of+51px for right pose; no per-frame scale, fitting, rotation, repaint or contact snapping'}})

def points(im,rois):
 a=np.array(im);y,x=np.indices(a.shape[:2]);mask=a[:,:,3]>=128;data={}
 for label,roi in rois.items():
  x1,y1,x2,y2=roi;yy,xx=np.where(mask&(x>=x1)&(x<x2)&(y>=y1)&(y<y2));assert len(xx)
  if label.startswith('toe'):
   maxx=int(xx.max());point=[float(maxx),float(np.median(yy[xx==maxx]))]
  else:
   maxy=int(yy.max());point=[float(np.median(xx[yy==maxy])),float(maxy)]
  data[label]={'pixelPoint':point,'roi':roi,'method':'rightmost alpha>=128 in bounded toe ROI; medianY' if label.startswith('toe') else 'lowest alpha>=128 tail ROI row; medianX'}
 plane=(data['toe-upper']['pixelPoint'][0]+data['toe-lower']['pixelPoint'][0])/2
 data['inferredToePlaneX']=plane;data['toePlaneSpreadPx']=abs(data['toe-upper']['pixelPoint'][0]-data['toe-lower']['pixelPoint'][0]);data['tailToInferredToePlaneGapPx']=plane-data['tail-tip']['pixelPoint'][0];data['tailBelowBothFeet']=data['tail-tip']['pixelPoint'][1]>max(data['toe-upper']['pixelPoint'][1],data['toe-lower']['pixelPoint'][1]);return data

# ROIs follow visible anatomy, not a searched-for favorable contact plane.
for pose,source,out in zip(['neutral','look'],sources,frames):
 high=points(source,{'toe-upper':[590,335,690,447],'toe-lower':[530,510,650,622],'tail-tip':[500,770,620,833]})
 low=points(out,{'toe-upper':[110,62,130,84],'toe-lower':[99,95,123,117],'tail-tip':[93,144,117,158]})
 a=np.array(out);yy,xx=np.where(a[:,:,3]>=128);measure.append({'pose':pose,'source1024':high,'output192':low,'visibleBBoxAlpha128':[int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)]})
height=measure[0]['visibleBBoxAlpha128'][3]-measure[0]['visibleBBoxAlpha128'][1];density=height/58
for item in measure:
 for key,scale in [('source1024',density/(192/1024)),('output192',density)]:
  data=item[key];data['pixelsPerWorldUnit']=scale;data['toePlaneSpreadWorld']=data['toePlaneSpreadPx']/scale;data['tailToInferredToePlaneGapWorld']=data['tailToInferredToePlaneGapPx']/scale
 item['visibleWorldHeight']=(item['visibleBBoxAlpha128'][3]-item['visibleBBoxAlpha128'][1])/density
common=np.logical_and.reduce([np.array(f)[:,:,3]>0 for f in frames]);y,x=np.indices(common.shape);contacts=[]
for name,roi,target in [('toe-upper-study',[111,65,125,82],[123,69]),('toe-lower-study',[101,98,118,114],[115,103]),('tail-tip-study',[102,148,112,155],[107,153])]:
 x1,y1,x2,y2=roi;yy,xx=np.where(common&(x>=x1)&(x<x2)&(y>=y1)&(y<y2));assert len(xx);idx=np.argmin((xx-target[0])**2+(yy-target[1])**2);contacts.append({'id':name,'x':int(xx[idx]),'y':int(yy[idx])})
atlas=Image.new('RGBA',(384,192))
for i,f in enumerate(frames):atlas.paste(f,(i*192,0))
atlas.save(P/'idle-look-atlas192.png');world=192/density;pivot={'x':120,'y':128};ids=['nuttall-support-neutral-192','nuttall-support-look-192'];seq=[0,1,0];ticks=[60,6,24]
m={'schemaVersion':1,'profile':'chirp-texture-review-v1','scope':'review-only','approval':'unreviewed','activation':'none','source':{'sha256':sha((P/'idle-look-atlas192.png').read_bytes()),'creator':'Chirp native reference-edit support study','tool':'native image_gen; translation-only source registration; nearest full-canvas output','toolVersion':'native model/version not exposed; Pillow '+Image.__version__,'rights':'unreviewed','fidelity':'unreviewed'},'atlas':{'width':384,'height':192,'alpha':'straight-rgba8','colorSpace':'srgb'},'frames':[{'id':id,'sourceRect':{'x':i*192,'y':0,'width':192,'height':192},'canvas':{'width':192,'height':192},'trim':{'x':0,'y':0},'pivot':pivot,'contacts':contacts,'world':{'width':world,'height':world},'sourcePixelsPerWorldUnit':density} for i,id in enumerate(ids)],'clips':[{'id':'idle','tickRate':30,'loop':True,'frames':[{'frameId':ids[i],'durationTicks':t} for i,t in zip(seq,ticks)]}]};dump('texture-review-manifest.json',m);static=json.loads(json.dumps(m));static['clips'][0]['frames']=[{'frameId':ids[0],'durationTicks':90}];dump('static-review-manifest.json',static)
def chunk(k,d):return struct.pack('>I',len(d))+k+d+struct.pack('>I',zlib.crc32(k+d)&0xffffffff)
png=b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',192,192,8,6,0,0,0))+chunk(b'acTL',struct.pack('>II',3,0));number=0
for k,(idx,t) in enumerate(zip(seq,ticks)):
 png+=chunk(b'fcTL',struct.pack('>IIIIIHHBB',number,192,192,0,0,t,30,0,0));number+=1;a=np.array(frames[idx]);data=zlib.compress(b''.join(b'\0'+a[row].tobytes() for row in range(192)),9)
 if k==0:png+=chunk(b'IDAT',data)
 else:png+=chunk(b'fdAT',struct.pack('>I',number)+data);number+=1
png+=chunk(b'IEND',b'');(P/'idle-look.apng').write_bytes(png)
rgb=[]
for i in seq:
 b=Image.new('RGBA',(192,192),(234,231,212,255));b.alpha_composite(frames[i]);rgb.append(b.convert('RGB'))
rgb[0].save(P/'idle-look.gif',save_all=True,append_images=rgb[1:],duration=[2000,200,800],loop=0,optimize=False)

# Art-pixel derived comparison and contact guides are separate from source/atlas.
preview=Image.new('RGBA',(600,200),(234,231,212,255));overlay=preview.copy();d=ImageDraw.Draw(preview);g=ImageDraw.Draw(overlay)
old=Image.open('/workspace/asset-production/new-species/sd20-woodpecker-warbler-oriole-v1/nuttall_s_woodpecker/neutral192.png').convert('RGBA');old_density=81/58
for n,(im,den,label) in enumerate([(old,old_density,'Old neutral: study only'),(frames[0],density,'New neutral: study only'),(frames[1],density,'New look: study only')]):
 size=round(192/den);scaled=im.resize((size,size),Image.Resampling.NEAREST);pos=(200*n+20,25);preview.alpha_composite(scaled,pos);overlay.alpha_composite(scaled,pos);d.text((200*n+8,8),label,fill=(30,33,27));g.text((200*n+8,8),label,fill=(30,33,27))
 if n>0:
  item=measure[n-1]['output192'];plane=pos[0]+item['inferredToePlaneX']/den;g.line((plane,30,plane,160),fill=(195,90,45),width=1)
  for lab in ['toe-upper','toe-lower','tail-tip']:
   pt=item[lab]['pixelPoint'];cx=pos[0]+pt[0]/den;cy=pos[1]+pt[1]/den;g.ellipse((cx-1,cy-1,cx+1,cy+1),outline=(30,120,175))
 d.text((200*n+8,177),'58 world-pixel visible HEIGHT',fill=(30,33,27));g.text((200*n+8,177),'Guide overlay; not a rendered trunk',fill=(30,33,27))
preview.convert('RGB').save(P/'normal-yard-scale-preview.png');overlay.convert('RGB').save(P/'normal-yard-scale-contact-guide.png')
crop=Image.new('RGBA',(800,1100),(234,231,212,255));draw=ImageDraw.Draw(crop)
for i,(im,item) in enumerate(zip(sources,measure)):
 region=(500,330,690,835);c=im.crop(region).resize((380,1010),Image.Resampling.NEAREST);crop.alpha_composite(c,(i*400,40));draw.text((i*400+8,10),item['pose']+' source support crop2x',fill=(30,33,27));h=item['source1024'];px=i*400+(h['inferredToePlaneX']-500)*2;draw.line((px,40,px,1050),fill=(195,90,45),width=2)
 for name in ['toe-upper','toe-lower','tail-tip']:
  xx,yy=h[name]['pixelPoint'];cx=i*400+(xx-500)*2;cy=40+(yy-330)*2;draw.ellipse((cx-4,cy-4,cx+4,cy+4),outline=(20,120,180),width=2)
crop.convert('RGB').save(P/'enlarged-support-crops-with-guide.png')

dump('support-measurements.json',{'target':'upper/lower toe tips and stiff tail tip on common near-vertical trunk plane; tail below both feet','scale':{'axis':'visible-height','neutralWorldHeight':58,'outputPxPerWorldUnit':density,'outputCanvas':[192,192],'worldCanvas':[world,world],'sourceCanvas':[1024,1024],'wholeCanvasOutputScale':192/1024,'biologicalApproval':False},'measurements':measure,'sourceGeometryUncertainty':'bounded manually selected anatomical ROIs and alpha128 endpoint proxies; not expert toe tracking. About±3nativepx endpoint uncertainty is plausible but not independently calibrated. Difference remains visibly much larger than a one-pixel endpoint ambiguity.','declaredContacts':{'points':contacts,'meaning':'positive-alpha study registration only; not support plane or physics approval'},'priorTailGapWorld':[13.828703703703704,14.141975308641975],'semanticFinding':'Tail now angles down+right rather than directly under torso, but remains left of the requested vertical toe plane. A separate inclined-support-fit.json evaluates a modest inclined line; independent contact/anatomy review must judge that distinct support hypothesis. Requested vertical support correction still fails.','packetBindingReady':False,'physicsApproved':False,'appBound':False,'retryPerformed':False})
outputs=['neutral192.png','look192.png','idle-look-atlas192.png','texture-review-manifest.json','static-review-manifest.json','idle-look.apng','idle-look.gif','support-measurements.json','normal-yard-scale-preview.png','normal-yard-scale-contact-guide.png','enlarged-support-crops-with-guide.png']
dump('PRIMARY-SOURCE-MANIFEST.json',{'batchId':BATCH,'nativeCalls':1,'original':'original.png','originalSHA256':sha((P/'original.png').read_bytes()),'prompt':'prompt.txt','promptSHA256':sha((P/'prompt.txt').read_bytes()),'frames':records,'outputMetadata':outputs,'sourceStatus':'generated; study-only; requested vertical correction incomplete; inclined-support hypothesis awaiting independent review','notes':['Exactly2new drawn poses from1native reference edit. Crops/registered/output renditions are derivatives, not additional drawings.','Transparent bird-only source; generated body/tail geometry was not scripted into compliance.','Native result1774x887 rather than requested2048x1024; source registration preserves equal887cells and call-wide scale1.','Old tail-to-toe-plane failure lesson retained. Actual new toe/tail geometry still misses one flat plane; no automaticretry.','No actor/physics/catalog approval, runtime binding or canonical Sharp receipt.','All browser evidence must be numeric/hash/timing only; no browser captures or image base64 in artifacts.']})
dump('provenance.json',{'nativeTool':'OpenAI image_gen reference edit','nativeCalls':1,'nativeModelVersionAndSeed':'not exposed','referenceInputs':[{'file':n,'sha256':sha((P/n).read_bytes()),'use':'existing generated adult male identity' if n.startswith('reference-') else 'authored geometry layout guide only'} for n in ['reference-neutral-source1024.png','support-geometry-guide.png']],'originalOutputPathRetained':'/workspace/generated_images/exec-7481649c-687e-42a9-b28a-7bce9d85ff82.png','rights':'generated reference artwork provenance retained; no external photo pixels downloaded or incorporated; review-profile rights unreviewed','morphologyReference':'https://www.allaboutbirds.org/guide/Nuttalls_Woodpecker/id','newDrawingCount':2,'sourceBankWrites':False,'paidExternalServices':False})
(P/'review.html').write_text('''<!doctype html><meta charset="utf-8"><title>Nuttall support correction study</title><style>body{font:16px system-ui;background:#eae7d4;color:#25281e;padding:24px}img{image-rendering:pixelated;max-width:100%}p{max-width:950px}</style><h1>Nuttall support correction: study only</h1><p>One real reference edit; two new drawn poses. Tail angles down/right, but the requested vertical toe plane still fails. A separate approximately11degree inclined-line hypothesis fits the measured anchors closely; independent anatomy/contact review remains required. No binding or physics approval. No retry.</p><p>Source APNG, proposed visible height58worldpixels:</p><img src="idle-look.apng" width="'''+str(round(world))+'''"><img src="idle-look.apng" width="384"><p>Normal yard-scale image and a separate guide overlay derived from art pixels:</p><img src="normal-yard-scale-preview.png"><img src="normal-yard-scale-contact-guide.png"><p>Enlarged exact source support crops with inferred mean toe plane (orange) and measured endpoint proxies (blue). Guide is not trunk artwork.</p><img src="enlarged-support-crops-with-guide.png"><p>See support-measurements.json and PRIMARY-SOURCE-MANIFEST.json for endpoints, units, gaps, exact source IDs and retained prompt/original. Independent review pending.</p>''')
dump('status.json',{'state':'generated and producer-reviewed study-only; awaiting independent review','nativeCalls':1,'newDrawings':2,'running':False,'packetBindingReady':False,'physicsApproved':False,'sourceFilesStableForIndependentReview':True,'nextQueued':'Hold. Coordinator independent review, then exact review hash seal and Library ZIP; no automatic new generation.'})
print(json.dumps({'heightPx':height,'density':density,'primaryFrames':records,'support':measure},indent=2))
