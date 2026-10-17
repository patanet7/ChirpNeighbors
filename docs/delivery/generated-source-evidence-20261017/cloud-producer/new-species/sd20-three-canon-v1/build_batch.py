from pathlib import Path
import hashlib,json,base64,html,zipfile
from PIL import Image, ImageDraw, ImageFont, __version__ as pillow_version
import numpy as np
from scipy import ndimage

P=Path(__file__).resolve().parent
def sha(b): return hashlib.sha256(b).hexdigest()
def savej(p,j): p.write_text(json.dumps(j,indent=2)+'\n')
def frame_id(im): return 'frame.sha256.'+sha(f'RGBA8;{im.width}x{im.height};'.encode()+im.tobytes())
original=Image.open(P/'original.png').convert('RGBA'); a=np.array(original)
labels,n=ndimage.label(a[:,:,3]>=32)
counts=np.bincount(labels.ravel()); principal=sorted(np.argsort(counts[1:])[-3:]+1,key=lambda i:np.where(labels==i)[1].mean())
seed=np.zeros(labels.shape,dtype=np.uint8)
for k,i in enumerate(principal,1): seed[labels==i]=k
_,nearest=ndimage.distance_transform_edt(seed==0,return_indices=True)
owner=seed[tuple(nearest)]
birds=[
 dict(id='anna_s_hummingbird',name="Anna's Hummingbird",latin='Calypte anna',root=[357,645],targetLength=34,lengthCm=[10,10],beak=[594,349],footRegions=[[300,613,351,649],[352,613,420,649]],issues=['Hummingbird sheet-relative scale was too large; presentation density explicitly corrects it.','Adult male rose crown/throat and green upperparts visible; tiny toes become a few pixels at normal size.'],movement='hover/dart with real wing motion or explicitly labelled wing rig',interaction='flower nectar probe with beak/flower contact'),
 dict(id='black_phoebe',name='Black Phoebe',latin='Sayornis nigricans',root=[1008,650],targetLength=54,lengthCm=[16,16],beak=[1203,241],footRegions=[[895,617,983,655],[1000,618,1100,656]],issues=['Source has warm/brown feather shading and stronger pale wing edges than ideal sooty adult; identity silhouette and white belly remain clear.','Foot anatomy needs owner normal-size approval before interaction/actor use.'],movement='short insect sally and return; tail-pump rig can supplement idle',interaction='airborne insect catch; no seed-feeder peck'),
 dict(id='california_towhee',name='California Towhee',latin='Melozone crissalis',root=[1749,669],targetLength=78,lengthCm=[21,25],beak=[1937,218],footRegions=[[1618,631,1736,679],[1760,622,1870,680]],issues=['Detailed feather texture is stronger than uniformly matte wild plumage; rusty crissum and face plus thick bill remain visible.','Toe detail is stylized and needs actual yard contact review.'],movement='ground hop with airborne interval; no planted-foot slide',interaction='ground peck or leaf-litter scratch')
]
records=[];atlas=Image.new('RGBA',(288,96))
for k,b in enumerate(birds,1):
 d=P/b['id'];d.mkdir(exist_ok=True)
 mask=(owner==k)&(a[:,:,3]>=2)
 ys,xs=np.where(mask); bbox=[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)]
 # Ownership assignment separates only transparent inter-bird space. No synthesized/painted pixels.
 owned=np.zeros_like(a);owned[mask]=a[mask]
 src=Image.new('RGBA',(1024,1024));dx,dy=608-b['root'][0],800-b['root'][1]
 assert 0<=bbox[0]+dx<bbox[2]+dx<=1024 and 0<=bbox[1]+dy<bbox[3]+dy<=1024, 'Source clipping prohibited'
 piece=Image.fromarray(owned).crop(tuple(bbox));src.paste(piece,(bbox[0]+dx,bbox[1]+dy))
 sid=frame_id(src);src.save(d/'source1024.png')
 out=src.resize((96,96),Image.Resampling.NEAREST);out.save(d/'idle96.png');atlas.paste(out,((k-1)*96,0))
 oa=np.array(out); yy,xx=np.where(oa[:,:,3]>=128);vb=[int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)]
 density=(vb[2]-vb[0])/b['targetLength']
 contacts=[]
 for i,region in enumerate(b['footRegions']):
  x0,y0,x1,y1=region
  cand=[]
  for y in range(96):
   for x in range(96):
    sx=(x+.5)*1024/96-dx;sy=(y+.5)*1024/96-dy
    if x0<=sx<x1 and y0<=sy<y1 and oa[y,x,3]>=128:cand.append((y,x))
  assert cand,(b['id'],region)
  bottom=max(y for y,x in cand);row=[x for y,x in cand if y==bottom];cx=row[len(row)//2]
  contacts.append(dict(id=f'foot-{i+1}',x=cx,y=bottom))
 manifest={'schemaVersion':1,'profile':'chirp-texture-review-v1','scope':'review-only','approval':'unreviewed','activation':'none','source':{'sha256':sha((d/'idle96.png').read_bytes()),'creator':'Chirp cloud source-preserving exporter','tool':'Pillow nearest canvas export','toolVersion':pillow_version,'rights':'unreviewed','fidelity':'unreviewed'},'atlas':{'width':96,'height':96,'alpha':'straight-rgba8','colorSpace':'srgb'},'frames':[{'id':b['id']+'-idle-96','sourceRect':{'x':0,'y':0,'width':96,'height':96},'canvas':{'width':96,'height':96},'trim':{'x':0,'y':0},'pivot':{'x':57,'y':75},'contacts':contacts,'world':{'width':96/density,'height':96/density},'sourcePixelsPerWorldUnit':density}],'clips':[{'id':'idle','tickRate':30,'loop':True,'frames':[{'frameId':b['id']+'-idle-96','durationTicks':90}]}]}
 savej(d/'texture-review-manifest.json',manifest)
 rec={**b,'sourceFrameId':sid,'sourcePNG':b['id']+'/source1024.png','sourcePNGsha256':sha((d/'source1024.png').read_bytes()),'outputFrameId':manifest['frames'][0]['id'],'outputPNG':b['id']+'/idle96.png','outputPNGsha256':sha((d/'idle96.png').read_bytes()),'outputFrameRGBAId':frame_id(out),'sourceCanvas':[1024,1024],'originalOwnedBBox':bbox,'sourceRegistration':{'method':'nearest principal alpha>=32 component assignment of original alpha>=2; alpha1 excluded in derivative; integer translation only','translation':[dx,dy],'sourcePixelScale':1,'registeredRoot':[608,800],'originalRetainedUnchanged':True},'outputCanvas':[96,96],'sourceToOutputScale':3/32,'resampling':'whole-canvas nearest; straight RGBA, no palette quantization or alpha threshold in output','visibleBBoxAlpha128':vb,'visibleOutputPx':[vb[2]-vb[0],vb[3]-vb[1]],'presentationDensityPxPerWorldUnit':density,'visibleWorldUnits':[(vb[2]-vb[0])/density,(vb[3]-vb[1])/density],'worldCanvas':[96/density,96/density],'contacts':contacts,'sourceBeakTipRegistered':[b['beak'][0]+dx,b['beak'][1]+dy],'outputBeakTipApprox':[(b['beak'][0]+dx)*3/32,(b['beak'][1]+dy)*3/32],'scaleQualification':'Biological length is external species reference, not anatomical endpoint calibration. Visible bounding-box width is a practical presentation proxy; final world scale remains provisional.','behaviorCoverage':{'idle':{'planned':True,'sourceAvailable':True,'bound':False,'visuallyVerified':'source and normal-size contact sheet only; no actual app yard'},'movement':{'planned':True,'bound':False,'visuallyVerified':False},'interaction':{'planned':True,'bound':False,'visuallyVerified':False}},'newDrawings':1,'newAnimationClips':0,'staticHoldSeconds':3,'artApproval':'provisional source candidate, owner review pending','runtimeAdmission':False}
 records.append(rec)
atlas.save(P/'three-canon-atlas96.png')
savej(P/'intake-manifest.json',{'schemaVersion':1,'kind':'source-starter-batch-not-runtime-admission','batchId':'sd20-three-canon-v1','nativeGenerationCalls':1,'originalDrawings':3,'uniqueSourceFrames':3,'newAnimationClips':0,'original':'original.png','originalSHA256':sha((P/'original.png').read_bytes()),'prompt':'prompt.txt','frames':records,'nextBatch':{'state':'queued-not-running','task':'Add species-appropriate motion/interaction after normal-yard idle intake; preserve these individual IDs.'},'macIntake':'For each bird upload idle96.png plus its texture-review-manifest.json using existing candidate-yard RGBA intake. Existing Sharp builder must produce canonical receipt/client package. No such receipt fabricated here.'})
# Static art preview, not browser screenshot. 1 world unit = 1 preview pixel.
preview=Image.new('RGB',(740,300),(232,232,213));dr=ImageDraw.Draw(preview)
dr.text((20,12),'Three new starter canons | normal world size (top) and 2x output pixels (bottom)',fill=(30,45,35))
for k,b in enumerate(records):
 im=Image.open(P/b['outputPNG']).convert('RGBA');dens=b['presentationDensityPxPerWorldUnit'];ws=round(96/dens);normal=im.resize((ws,ws),Image.Resampling.NEAREST)
 x=30+k*240;y=36;preview.paste(normal,(x,y),normal)
 dr.text((x,142),b['name'],fill=(30,45,35));dr.text((x,158),f"{b['visibleWorldUnits'][0]:.0f} world px long | idle still",fill=(30,45,35))
 crop=im.crop(tuple(b['visibleBBoxAlpha128']));crop=crop.resize((crop.width*2,crop.height*2),Image.Resampling.NEAREST);preview.paste(crop,(x,184),crop)
dr.rectangle((0,296,740,300),fill=(76,94,61));preview.save(P/'normal-size-preview.png')
# HTML displays source96 at exact fractional CSS world size and adjustable enlarged diagnostics.
cards=[]
for b in records:
 data=base64.b64encode((P/b['outputPNG']).read_bytes()).decode();ws=96/b['presentationDensityPxPerWorldUnit']
 cards.append(f'<article><h2>{html.escape(b["name"])}</h2><div class="normal"><img src="data:image/png;base64,{data}" style="width:{ws}px;height:{ws}px"></div><p>{b["visibleWorldUnits"][0]:.0f} × {b["visibleWorldUnits"][1]:.1f} visible world px. Static idle only.</p><details><summary>Enlarge output pixels</summary><img width="384" height="384" src="data:image/png;base64,{data}"></details><p>{html.escape(" ".join(b["issues"]))}</p><code>{b["sourceFrameId"]}</code></article>')
(P/'review.html').write_text('<!doctype html><meta charset="utf-8"><title>Three San Diego starter canons</title><style>body{font:16px system-ui;background:#e8e8d5;color:#20342a;margin:24px}main{display:flex;flex-wrap:wrap;gap:20px}article{width:380px;padding:16px;background:#f7f5e9;border:1px solid #a4ac91}h2{font-size:19px}img{image-rendering:pixelated}.normal{height:150px;display:flex;align-items:flex-end;border-bottom:1px solid #7a895c}code{font-size:11px;overflow-wrap:anywhere}p{line-height:1.45}</style><h1>Three new yard starter canons</h1><p>One native generation, three original drawings. At 960px-wide yard, one world unit is one CSS pixel here. These are stills, with no invented body animation. Source art review only; actual Mac yard intake and owner approval pending.</p><main>'+''.join(cards)+'</main><p>Source morphology/length references: Cornell All About Birds. Full citations, prompts, hashes and planned vs bound behavior are in the bundle.</p>')
savej(P/'status.json',{'state':'staged','newGenerationCalls':1,'newDrawings':3,'newAnimationClips':0,'sourceReviewed':True,'normalSizePreviewReviewed':False,'integrated':False,'running':False,'next':'queued motion and interaction after source idle intake'})
print(json.dumps([{'species':b['name'],'sourceFrameId':b['sourceFrameId'],'outputVisible':b['visibleOutputPx'],'worldVisible':b['visibleWorldUnits'],'density':b['presentationDensityPxPerWorldUnit'],'contacts':b['contacts']} for b in records],indent=2))
