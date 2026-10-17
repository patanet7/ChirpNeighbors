from pathlib import Path
from PIL import Image,ImageDraw,__version__ as pillow_version
from scipy import ndimage
import numpy as np,json,hashlib,base64,html
P=Path(__file__).resolve().parent
def sha(b):return hashlib.sha256(b).hexdigest()
def fid(im):return 'frame.sha256.'+sha(f'RGBA8;{im.width}x{im.height};'.encode()+im.tobytes())
def js(p,j):p.write_text(json.dumps(j,indent=2)+'\n')
im=Image.open(P/'original.png').convert('RGBA');a=np.array(im);l,n=ndimage.label(a[:,:,3]>=32);counts=np.bincount(l.ravel());big=np.argsort(counts[1:])[-6:]+1
# Native grid identified by component centroids, not inferred species from color.
comps=sorted(big,key=lambda q:(int(np.where(l==q)[0].mean()//512),np.where(l==q)[1].mean()))
seed=np.zeros(l.shape,np.uint8)
for i,q in enumerate(comps,1):seed[l==q]=i
_,near=ndimage.distance_transform_edt(seed==0,return_indices=True);owner=seed[tuple(near)]
birds=[{'id':'bushtit','name':'Bushtit','latin':'Psaltriparus minimus','targetLength':28,'lengthCm':[7,8],'morphology':'Pacific/local male: tiny plump gray-brown bird, dark eye, soft brown crown, very long narrow tail and short bill.','url':'https://www.allaboutbirds.org/guide/Bushtit/id','footROIs':[[295,410,462,470],[295,853,462,920]],'beakTips':[[497,225],[483,621]],'movement':'twig-to-twig hop','interaction':'foliage insect glean','seasonTag':'resident','alternatePose':'look'},
{'id':'bewick_s_wren','name':"Bewick's Wren",'latin':'Thryomanes bewickii','targetLength':44,'lengthCm':[13,13],'morphology':'Local darker brown wren, white eyebrow, fine slightly downcurved bill, long cocked tail with restrained barring/tip marks, gray-white underside.','url':'https://www.allaboutbirds.org/guide/Bewicks_Wren/id','footROIs':[[724,411,908,470],[724,856,908,918]],'beakTips':[[987,210],[986,754]],'movement':'shrub hop','interaction':'crevice insect probe','seasonTag':'resident','alternatePose':'look'},
{'id':'white_crowned_sparrow','name':'White-crowned Sparrow','latin':'Zonotrichia leucophrys','targetLength':54,'lengthCm':[15,16],'morphology':'Adult black-white crown stripes, pink/pale-orange bill, pale lores, plain gray breast, brown back streaks and restrained wingbars; Gambels-type proposal, not confirmed subspecies.','url':'https://www.allaboutbirds.org/guide/White-crowned_Sparrow/id','footROIs':[[1260,410,1455,470],[1260,858,1455,917]],'beakTips':[[1483,189],[1483,635]],'movement':'short ground hop','interaction':'seed/leaf-litter peck','seasonTag':'seasonal-cool-season-lowland','alternatePose':'blink'}]
allframes=[];outbirds=[]
for col,b in enumerate(birds):
 d=P/b['id'];d.mkdir(exist_ok=True);frames=[];outs=[];edge=96;unit=1
 for row,pose in enumerate(['neutral',b['alternatePose']]):
  k=row*3+col+1;mask=(owner==k)&(a[:,:,3]>=2);ys,xs=np.where(mask);bbox=[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)]
  x0,y0,x1,y1=b['footROIs'][row];foot=(a[y0:y1,x0:x1,3]>=128)&(owner[y0:y1,x0:x1]==k);fy,fx=np.where(foot);root=[int(round(np.median(fx+x0))),int(fy.max()+y0+1)]
  dx,dy=608-root[0],800-root[1]
  assert min(bbox[0]+dx,bbox[1]+dy)>=0 and bbox[2]+dx<=1024 and bbox[3]+dy<=1024,'no clipping'
  owned=np.zeros_like(a);owned[mask]=a[mask];src=Image.new('RGBA',(1024,1024));src.paste(Image.fromarray(owned).crop(tuple(bbox)),(bbox[0]+dx,bbox[1]+dy));src.save(d/(pose+'-source1024.png'))
  out=src.resize((edge,edge),Image.Resampling.NEAREST);out.save(d/(pose+str(edge)+'.png'));outs.append(out);oa=np.array(out);y,x=np.where(oa[:,:,3]>=128);vb=[int(x.min()),int(y.min()),int(x.max()+1),int(y.max()+1)]
  f={'speciesId':b['id'],'pose':pose,'sourceFrameId':fid(src),'sourcePNG':f'{b["id"]}/{pose}-source1024.png','sourcePNGsha256':sha((d/(pose+'-source1024.png')).read_bytes()),'sourceCanvas':[1024,1024],'originalOwnedBBox':bbox,'sourceRegistration':{'method':'nearest principal alpha>=32 component assignment of original alpha>=2; alpha1 excluded only from derivative; integer translation','translation':[dx,dy],'originalFootRoot':root,'footHeuristicROI':b['footROIs'][row],'registeredRoot':[608,800],'perPoseRescale':False,'noSourcePainting':True},'outputFrameId':b['id']+'-'+pose+'-'+str(edge),'outputPNG':f'{b["id"]}/{pose}{edge}.png','outputPNGsha256':sha((d/(pose+str(edge)+'.png')).read_bytes()),'outputRGBAId':fid(out),'outputCanvas':[edge,edge],'sourceToOutputScale':edge/1024,'visibleBBoxAlpha128':vb,'visibleOutputPx':[vb[2]-vb[0],vb[3]-vb[1]],'beakTipApproxSourceRegistered':[b['beakTips'][row][0]+dx,b['beakTips'][row][1]+dy],'beakTipApproxOutput':[(b['beakTips'][row][0]+dx)*edge/1024,(b['beakTips'][row][1]+dy)*edge/1024],'beakAnchorQualification':'Producer-estimated silhouette tip, not a verified target-contact anchor.'}
  frames.append(f);allframes.append(f)
 density=frames[0]['visibleOutputPx'][0]/b['targetLength']
 common=(np.array(outs[0])[:,:,3]>=128)&(np.array(outs[1])[:,:,3]>=128)
 # Common toe-core review anchors. These satisfy the technical contact rule only.
 contacts=[]
 for i,(xmin,xmax) in enumerate([(38,57),(57,77)]):
  yy,xx=np.where(common[70*unit:76*unit,xmin*unit:xmax*unit]);assert len(xx)>0,(b['id'],'foot contact intersection missing')
  y=int(yy.max()+70*unit);rowxs=np.where(common[y,xmin*unit:xmax*unit])[0]+xmin*unit;x=int(rowxs[len(rowxs)//2]);contacts.append({'id':f'foot-{i+1}','x':x,'y':y})
 atlas=Image.new('RGBA',(edge*2,edge));atlas.paste(outs[0],(0,0));atlas.paste(outs[1],(edge,0));atlas.save(d/f'idle-look-atlas{edge}.png')
 mf=[]
 for idx,f in enumerate(frames):
  mf.append({'id':f['outputFrameId'],'sourceRect':{'x':idx*edge,'y':0,'width':edge,'height':edge},'canvas':{'width':edge,'height':edge},'trim':{'x':0,'y':0},'pivot':{'x':57*unit,'y':75*unit},'contacts':contacts,'world':{'width':edge/density,'height':edge/density},'sourcePixelsPerWorldUnit':density})
 altTicks=3 if b['alternatePose']=='blink' else 6
 clip=[{'frameId':frames[0]['outputFrameId'],'durationTicks':60},{'frameId':frames[1]['outputFrameId'],'durationTicks':altTicks},{'frameId':frames[0]['outputFrameId'],'durationTicks':30-altTicks}]
 manifest={'schemaVersion':1,'profile':'chirp-texture-review-v1','scope':'review-only','approval':'unreviewed','activation':'none','source':{'sha256':sha((d/f'idle-look-atlas{edge}.png').read_bytes()),'creator':'Chirp cloud source-preserving exporter','tool':'Pillow nearest canvas export','toolVersion':pillow_version,'rights':'unreviewed','fidelity':'unreviewed'},'atlas':{'width':edge*2,'height':edge,'alpha':'straight-rgba8','colorSpace':'srgb'},'frames':mf,'clips':[{'id':'idle','tickRate':30,'loop':True,'frames':clip}]}
 js(d/'texture-review-manifest.json',manifest)
 # A separate still manifest is a genuine fallback for incomplete motion review.
 still=json.loads(json.dumps(manifest));still['source']['sha256']=frames[0]['outputPNGsha256'];still['atlas']['width']=edge;still['frames']=still['frames'][:1];still['clips'][0]['frames']=[{'frameId':frames[0]['outputFrameId'],'durationTicks':90}];js(d/'static-review-manifest.json',still)
 seq=[outs[0],outs[1],outs[0]];seq[0].save(d/'idle-look.apng',save_all=True,append_images=seq[1:],duration=[2000,altTicks*1000/30,(30-altTicks)*1000/30],loop=0,disposal=0,blend=0)
 gif=[]
 for q in seq:
  bg=Image.new('RGBA',(edge,edge),(232,232,213,255));bg.alpha_composite(q);gif.append(bg.convert('RGB'))
 gif[0].save(d/'idle-look.gif',save_all=True,append_images=gif[1:],duration=[2000,altTicks*1000/30,(30-altTicks)*1000/30],loop=0,disposal=2,optimize=False)
 # Displacement measures evaluate actual output pixels, not source-pixel identity.
 feet=[]
 for q in outs:
  aa=np.array(q)[:,:,3]>=128;yy,xx=np.where(aa[70*unit:76*unit,38*unit:77*unit]);feet.append({'centroid':[float(xx.mean()+38*unit),float(yy.mean()+70*unit)],'groundBoundary':int(yy.max()+70*unit+1),'pixels':len(xx)})
 slip=float(np.linalg.norm(np.array(feet[1]['centroid'])-feet[0]['centroid']))
 union=np.logical_or(np.array(outs[0])[:,:,3]>0,np.array(outs[1])[:,:,3]>0);changed=np.any(np.array(outs[0])!=np.array(outs[1]),axis=2)&union
 rec={**{k:v for k,v in b.items() if k not in ['footROIs','beakTips']},'sourceRefs':[{'url':b['url'],'accessed':'2026-10-17','use':'Factual morphology/length descriptions only; no reference photo pixels downloaded.'}],'frames':frames,'proposedDensity':density,'worldCanvas':[edge/density,edge/density],'outputCanvas':[edge,edge],'atlasPNG':f'{b["id"]}/idle-look-atlas{edge}.png','visibleWorldUnits':[[f['visibleOutputPx'][0]/density,f['visibleOutputPx'][1]/density] for f in frames],'scaleQualification':'Bounding-box width of neutral pose is practical scale proxy, not calibrated bill-to-tail biological measurement. Same density for both poses; no per-pose scale fit.','contacts':contacts,'outputFootHeuristic':{'poses':feet,'centroidDeltaOutputPx':slip,'centroidDeltaWorldUnits':slip/density,'temporalGroundBoundaryDeltaOutputPx':abs(feet[0]['groundBoundary']-feet[1]['groundBoundary']),'measurementLimit':'Coarse alpha mask in presumed feet region, not tracked anatomical toe correspondences; posture/pixel texture changes can shift centroid.'},'outputChangedPixels':int(changed.sum()),'changedPixelInterpretation':'Not semantic quality gate; two real drawn poses differ in body texture as well as head.','timing':{'tickRate':30,'ticks':[60,altTicks,30-altTicks],'totalTicks':90,'totalMs':3000,'alternateHoldMs':altTicks*1000/30},'newDrawings':2,'proposedIdleLookClips':1,'behaviorCoverage':{'idleLook':{'planned':True,'sourceDrawingsAvailable':True,'runtimeBound':False,'normalYardVisuallyVerified':False},'movement':{'planned':True,'sourceDrawingsAvailable':False,'runtimeBound':False,'normalYardVisuallyVerified':False},'interaction':{'planned':True,'sourceDrawingsAvailable':False,'runtimeBound':False,'normalYardVisuallyVerified':False}},'runtimeAdmission':False,'ownerApproval':False}
 outbirds.append(rec)
js(P/'intake-manifest.json',{'schemaVersion':1,'batchId':'sd20-bushtit-wren-sparrow-v1','kind':'source-candidate-intake-not-runtime-admission','styleAttempt':'Quieter coherent feather grouping by native prompt; no causal claim about the owner screenshot or a demonstrated pipeline fix','nativeGenerationCalls':1,'originalDrawings':6,'uniqueSourceFrames':6,'proposedIdleLookClips':3,'original':'original.png','originalSHA256':sha((P/'original.png').read_bytes()),'exactPrompt':'prompt.txt','species':outbirds,'nextBatch':{'state':'queued-not-running','task':'Parent coordinates next missing roster source species; actor movement/interaction remains a separate binding task.'},'macIntake':'Use each species idle-look-atlas96.png + texture-review-manifest.json; fallback neutral96.png + static-review-manifest.json. Mac existing Sharp intake must create canonical receipt; none fabricated here.'})
preview=Image.new('RGB',(1040,520),(232,232,213));dr=ImageDraw.Draw(preview);dr.text((20,12),'Bushtit / wren / sparrow: two real poses each. Normal world size above; enlarged diagnostic crops below.',fill='#20342a')
for k,b in enumerate(outbirds):
 x=24+k*340;dr.text((x,40),b['name'],fill='#20342a')
 for i,f in enumerate(b['frames']):
  q=Image.open(P/f['outputPNG']).convert('RGBA');ws=round(b['outputCanvas'][0]/b['proposedDensity']);n=q.resize((ws,ws),Image.Resampling.NEAREST);preview.paste(n,(x+i*150,65),n)
  c=q.crop(tuple(f['visibleBBoxAlpha128']));zoom=2 if b['outputCanvas'][0]==96 else 1;c=c.resize((c.width*zoom,c.height*zoom),Image.Resampling.NEAREST);preview.paste(c,(x+i*155,350),c)
 dr.text((x,315),f"Neutral {b['targetLength']} world px / look pair",fill='#20342a')
preview.save(P/'normal-size-preview.png')
cards=[]
for b in outbirds:
 data=base64.b64encode((P/b['id']/'idle-look.apng').read_bytes()).decode();ws=b['outputCanvas'][0]/b['proposedDensity'];still=base64.b64encode((P/b['frames'][0]['outputPNG']).read_bytes()).decode()
 cards.append(f'<article><h2>{html.escape(b["name"])}</h2><div class="stage"><img src="data:image/png;base64,{data}" style="width:{ws}px;height:{ws}px"></div><p>Normal speed: 2s neutral, {b["timing"]["alternateHoldMs"]:.0f}ms {b["alternatePose"]}, remainder neutral to 3s. {b["targetLength"]} world pixels neutral visible width. Alternate: {b["alternatePose"]}.</p><details><summary>4x output pixels</summary><img width="{b['outputCanvas'][0]*4}" height="{b['outputCanvas'][0]*4}" src="data:image/png;base64,{data}"></details><p>Output foot-mask centroid change {b["outputFootHeuristic"]["centroidDeltaOutputPx"]:.3f}px; coarse heuristic, not anatomical approval.</p><p>{html.escape(b["morphology"])}</p></article>')
(P/'review.html').write_text('<!doctype html><meta charset="utf-8"><title>Bushtit / wren / sparrow canons</title><style>body{font:16px system-ui;background:#e8e8d5;color:#20342a;margin:24px}main{display:flex;gap:20px;flex-wrap:wrap}article{width:390px;padding:16px;background:#f7f5e9;border:1px solid #a4ac91}img{image-rendering:pixelated}.stage{height:185px;border-bottom:1px solid #7a895c;display:flex;align-items:flex-end}p{line-height:1.4}</style><h1>Six real source drawings, three species</h1><p>Actual APNG playback at proposed world scale. One world unit equals one CSS pixel here, as in a 960px yard at 1:1. Source-only: canonical Mac intake, owner approval, actor motion and interactions remain pending. Neutral still fallback is included for every species.</p><main>'+''.join(cards)+'</main>')
js(P/'status.json',{'state':'generated','sourceReviewed':True,'normalSizePlaybackReviewed':False,'nativeCalls':1,'newDrawings':6,'proposedIdleLookClips':3,'runtimeBound':False,'running':False,'next':'normal-size paired-pose review then staged source handoff; movement/interaction remains queued'})
print(json.dumps([{'species':b['name'],'sourceIds':[f['sourceFrameId'] for f in b['frames']],'visible':b['visibleWorldUnits'],'foot':b['outputFootHeuristic']} for b in outbirds],indent=2))
