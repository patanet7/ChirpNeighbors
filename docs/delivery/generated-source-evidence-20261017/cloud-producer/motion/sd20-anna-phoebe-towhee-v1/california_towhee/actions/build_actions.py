from pathlib import Path
from PIL import Image,ImageDraw
import hashlib,json,struct,zlib,base64,numpy as np
P=Path(__file__).parent;S=Path('/workspace/asset-production/new-species/sd20-three-canon-v1');sha=lambda b:hashlib.sha256(b).hexdigest();fid=lambda im:'frame.sha256.'+sha(('RGBA8;%dx%d;'%im.size).encode()+im.tobytes())
original=Image.open(P/'original.png').convert('RGBA');assert original.size==(1774,887)
source=Image.open(S/'california_towhee/source1024.png').convert('RGBA');frames=[Image.open(S/'california_towhee/idle96.png').convert('RGBA')];sources=[source];lineage=[]
for i,name in enumerate(['blink','look']):
 raw=original.crop((i*887,0,(i+1)*887,887));raw.save(P/f'{name}-raw-cell.png')
 # Single call-wide scale from height/body reference; no per-frame bbox fitting.
 scaled=raw.resize((816,816),Image.Resampling.NEAREST);registered=Image.new('RGBA',(1024,1024));registered.paste(scaled,(34,84));registered.save(P/f'{name}-source1024.png');out=registered.resize((96,96),Image.Resampling.NEAREST);out.save(P/f'{name}-96.png');sources.append(registered);frames.append(out)
 lineage.append({'pose':name,'nativeOriginalSHA256':sha((P/'original.png').read_bytes()),'nativeCellRect':[i*887,0,887,887],'nativeCellRgbaId':fid(raw),'registeredSourceFrameId':fid(registered),'registeredSourcePNG':f'{name}-source1024.png','registeredSourcePNGsha256':sha((P/f'{name}-source1024.png').read_bytes()),'registration':{'sourceCell887To816Scale':816/887,'sameScaleBothPoses':True,'translation':[34,84],'method':'one fixed call-wide nearest resize plus same integer placement; manually calibrated source body/ground span; no per-frame fit, source paint, local body warping or foot snapping'},'outputPNG':f'{name}-96.png','outputPNGsha256':sha((P/f'{name}-96.png').read_bytes()),'outputRgbaId':fid(out),'registeredToOutputScale':3/32})
source.save(P/'open-source1024.png');frames[0].save(P/'open-96.png');arrays=[np.array(f) for f in frames];y,x=np.indices((96,96));common=np.all(np.stack([a[:,:,3]>0 for a in arrays]),axis=0);contacts=[]
for label,side,target in [('foot-a',x<57,(54,75)),('foot-b',x>=57,(60,74))]:
 yy,xx=np.where(common&side&(x>=47)&(x<=68)&(y>=73)&(y<=77));assert len(xx);idx=np.argmin((xx-target[0])**2+(yy-target[1])**2);contacts.append({'id':label,'x':int(xx[idx]),'y':int(yy[idx])})
atlas=Image.new('RGBA',(288,96))
for i,f in enumerate(frames):atlas.paste(f,(i*96,0))
atlas.save(P/'idle-atlas96.png');ids=['towhee-open-96','towhee-blink-96','towhee-look-96'];steps=[(0,42),(1,3),(0,24),(2,18),(0,27)];m=json.loads((S/'california_towhee/texture-review-manifest.json').read_text());prototype=m['frames'][0];m['source']['sha256']=sha((P/'idle-atlas96.png').read_bytes());m['source']['tool']='native image_gen reference edit; fixed call-wide registration; nearest full-canvas output';m['atlas']['width']=288;m['frames']=[]
for i in range(3):
 f=json.loads(json.dumps(prototype));f['id']=ids[i];f['sourceRect']['x']=96*i;f['contacts']=contacts;m['frames'].append(f)
m['clips']=[{'id':'idle','tickRate':30,'loop':True,'frames':[{'frameId':ids[i],'durationTicks':t} for i,t in steps]}];(P/'texture-review-manifest.json').write_text(json.dumps(m,indent=2)+'\n')
def chunk(k,d):return struct.pack('>I',len(d))+k+d+struct.pack('>I',zlib.crc32(k+d)&0xffffffff)
png=b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',96,96,8,6,0,0,0))+chunk(b'acTL',struct.pack('>II',len(steps),0));number=0
for k,(i,t) in enumerate(steps):
 png+=chunk(b'fcTL',struct.pack('>IIIIIHHBB',number,96,96,0,0,t,30,0,0));number+=1;data=zlib.compress(b''.join(b'\0'+arrays[i][row].tobytes() for row in range(96)),9)
 if k==0:png+=chunk(b'IDAT',data)
 else:png+=chunk(b'fdAT',struct.pack('>I',number)+data);number+=1
png+=chunk(b'IEND',b'');(P/'idle.apng').write_bytes(png)
g=[]
for i,t in steps:
 b=Image.new('RGBA',(96,96),(231,229,211,255));b.alpha_composite(frames[i]);g.append(b.convert('RGB'))
g[0].save(P/'idle.gif',save_all=True,append_images=g[1:],duration=[1400,100,800,600,900],loop=0,optimize=False)
proof=[];density=prototype['sourcePixelsPerWorldUnit'];size=round(96/density)
for i,t in steps:
 b=Image.new('RGBA',(480,200),(231,229,211,255));b.alpha_composite(frames[i].resize((size,size),Image.Resampling.NEAREST),(20,30));b.alpha_composite(frames[i].resize((192,192),Image.Resampling.NEAREST),(240,5));d=ImageDraw.Draw(b);d.text((12,8),'Towhee: proposed78worldpx body length',fill=(30,34,26));d.text((12,180),'Actual drawn blink/look, app intake pending',fill=(30,34,26));proof.append(b.convert('RGB'))
proof[0].save(P/'normal-size-and-2x-preview.gif',save_all=True,append_images=proof[1:],duration=[1400,100,800,600,900],loop=0,optimize=False)
measure=[]
for name,a in zip(['open','blink','look'],arrays):
 mask=a[:,:,3]>=128;yy,xx=np.where(mask);feet=[]
 for side in [x<57,x>=57]:
  fy,fx=np.where(mask&side&(x>=47)&(x<=68)&(y>=72)&(y<=78));feet.append({'bottomBoundary':int(fy.max()+1),'centroid':[float(fx.mean()),float(fy.mean())]})
 measure.append({'pose':name,'visibleBBoxAlpha128':[int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)],'feet':feet})
baseline=max(abs(a['bottomBoundary']-b['bottomBoundary']) for af in measure for bf in measure for a,b in zip(af['feet'],bf['feet']));centroid=max(float(np.linalg.norm(np.array(a['centroid'])-np.array(b['centroid']))) for af in measure for bf in measure for a,b in zip(af['feet'],bf['feet']))
doc={'oneActualNewCall':True,'newDrawings':2,'existingOpenSourceFrameId':fid(source),'existingOpenPNGsha256':sha((S/'california_towhee/source1024.png').read_bytes()),'newFrames':lineage,'sequence':steps,'durationTicks':sum(t for i,t in steps),'tickRate':30,'durationSeconds':sum(t for i,t in steps)/30,'commonPositiveAlphaContacts':contacts,'outputMeasurements':measure,'maxPerFootGroundBoundaryChangeOutputPx':baseline,'maxFootPixelCentroidChangeOutputPx':centroid,'atProposedDensity':density,'maxGroundBoundaryChangeWorldUnits':baseline/density,'contactCaveat':'bounded output alpha-mask proxies, not toe tracking or world-actor contact','actualRuntimeAdmission':False,'canonicalSharpReceipt':None,'ownerAcceptance':False,'newProductionAnimationAccepted':False};(P/'source-lineage.json').write_text(json.dumps(doc,indent=2)+'\n')
apng=base64.b64encode(png).decode();(P/'review.html').write_text('<!doctype html><meta charset="utf-8"><title>Towhee blink and look</title><style>body{font:16px system-ui;background:#e7e5d3;padding:24px}img{image-rendering:pixelated}</style><h1>Towhee blink/look source candidate</h1><p>Two newly drawn poses from one reference edit; existing open pose reused. Left proposed normal world size, right2× output pixels. Actual yard/Sharp intake pending.</p><img width="'+str(size)+'" src="data:image/png;base64,'+apng+'"><img width="192" src="data:image/png;base64,'+apng+'"><p>Contacts and scale are provisional; exact source pixel equality is not an animation quality gate. See source-lineage.json for measured output foot drift and retained generation prompt/original.</p>')
print(json.dumps(doc,indent=2))
