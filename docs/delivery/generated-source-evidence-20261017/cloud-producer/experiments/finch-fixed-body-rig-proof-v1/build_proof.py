"""Bounded cutout scaffold. No diffusion, drawing synthesis or runtime integration."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFilter
import numpy as np,json,hashlib,shutil
P=Path(__file__).parent;R=P.parent.parent
source=R/'frames/7c12c45d8a8a6e64824669c595f4f58630aaa7a2eb6854ca76f5cd2311d2e6fe.png'
if not source.exists():source=P/'source-neutral.png'
im=Image.open(source).convert('RGBA');a=np.array(im);H,W=a.shape[:2]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(source)=='ed79704dca763d6ef32beb6ff6a7a9e0d7cf26e3069619e25f2c7539d14fb605'
if source.resolve()!=(P/'source-neutral.png').resolve():shutil.copy2(source,P/'source-neutral.png')
polygon=[[458,461],[484,409],[566,389],[618,415],[663,449],[669,481],[621,501],[621,550],[576,564],[535,529],[493,514]]
mask=Image.new('L',(W,H));ImageDraw.Draw(mask).polygon([tuple(x) for x in polygon],fill=255);mask.save(P/'head-mask.png');hm=np.array(mask)>0
head=a.copy();head[~hm]=0;body=a.copy();body[hm]=0;Image.fromarray(head).save(P/'head-layer.png');Image.fromarray(body).save(P/'body-feet-layer.png')
xx,yy=np.meshgrid(np.arange(W),np.arange(H));cx,cy=560,516
angles=[0,-.12,0,.12,0];allframes=[];entries=[];metrics=[]
for i,t in enumerate(angles):
 c,s=np.cos(t),np.sin(t);sx=np.floor(c*(xx-cx)+s*(yy-cy)+cx+.5).astype(int);sy=np.floor(-s*(xx-cx)+c*(yy-cy)+cy+.5).astype(int);valid=(sx>=0)&(sx<W)&(sy>=0)&(sy<H);sx=np.clip(sx,0,W-1);sy=np.clip(sy,0,H-1);hit=valid&hm[sy,sx]&(a[sy,sx,3]>0);out=body.copy();out[hit]=a[sy[hit],sx[hit]];out[600:]=a[600:]
 # At neutral preserve original hiddenRGBA too; no invented head drawing.
 if t==0:out=a.copy()
 path=P/f'rig-frame-{i:02}.png';Image.fromarray(out).save(path);allframes.append(Image.fromarray(out));opaque=Image.fromarray(np.uint8(out[:,:,3]>=128)*255);edge=np.array(opaque)-np.minimum(np.array(opaque),np.array(opaque.filter(ImageFilter.MinFilter(3))));line=Image.fromarray(255-edge).convert('RGB');line.resize((512,512),Image.Resampling.NEAREST).save(P/f'outline-{i:02}.png')
 metrics.append({'frame':i,'protectedRGBAChangedPixels':int(np.any(out[600:]!=a[600:],axis=2).sum()),'sourceFootPixelNeighborhoodsExact':all(np.array_equal(out[y-8:y+2,x-8:x+8],a[y-8:y+2,x-8:x+8]) for x,y in [(483,792),(535,800)]),'bodyLayerScale':1,'headTransformScale':1,'rotationRadians':t,'restSupportMaskUncoveredPixelsAlpha128':int(((a[:,:,3]>=128)&(out[:,:,3]<128)&hm).sum()),'newlyDrawnFrame':False})
 entries.append({'file':path.name,'sha256':sha(path),'angleRadians':t,'durationMs':160,'classification':'deterministic-existing-pixel-cutout-assembly','generatedDrawing':False})
allframes[0].save(P/'rig-preview.apng',save_all=True,append_images=allframes[1:],duration=[160]*5,loop=0,disposal=0,blend=0)
gifs=[f.resize((384,384),Image.Resampling.NEAREST).convert('RGB') for f in allframes];gifs[0].save(P/'rig-preview.gif',save_all=True,append_images=gifs[1:],duration=[160]*5,loop=0,optimize=False)
contract=Path('/workspace/birdsong-yard-sprites');binding=[]
for n in ['pose-geometry.ts','manifest-v2.ts','manifest-v3.ts','manifest-v4.ts','image-stage-contracts.ts']:
 p=contract/'src/lib/assets'/n
 if p.exists():shutil.copy2(p,P/'contract-snapshot'/n)
 else:p=P/'contract-snapshot'/n
 binding.append({'file':'src/lib/assets/'+n,'snapshot':'contract-snapshot/'+n,'sha256':sha(p)})
manifest={'experimentId':P.name,'classification':'executable-engineering-scaffold-not-generated-animation','sourceFrameId':'frame.sha256.7c12c45d8a8a6e64824669c595f4f58630aaa7a2eb6854ca76f5cd2311d2e6fe','sourcePNGsha256':sha(source),'sourceCanvas':[1024,1024],'sourceRoot':[512,800],'protectedRectangle':[0,600,1024,1024],'headPivot':[cx,cy],'manualHeadPolygon':polygon,'maskReviewStatus':'rough hand-authored engineering mask, anatomy/overlaps not approved','fixedContacts':[{'id':'foot-A','source':[483,792]},{'id':'foot-B','source':[535,800]}],'leftRightAnatomyAssigned':False,'worldScale':None,'diagnosticSourcePixelsPerWorldUnit':4,'diagnosticWorldOrigin':[400,300],'frames':entries,'newGenerationCalls':0,'newGeneratedDrawings':0,'newDerivedAssemblies':5,'distinctDerivedPoses':3,'verifiedProductionReuse':False,'artAccepted':False,'contactAnatomyAccepted':False,'runtimeIntegrated':False,'productionClip':False,'geometry':{'protectedPixelsGuaranteedBy':'explicit copy from retained neutral after cutout composition; not diffusion','footFixedDuringThisProof':True,'rootTranslation':[0,0],'walkOrPreenMotionValidated':False,'headPixelsResampled':'nearest inverse rigid transform; no repaint','occlusion':'head over body, rough mask; missing neck underpaint and seam review'},'rendererBinding':{'repository':'patanet7/birdsong-yard-sprites','commit':'6f23d988a788a29de509f92af7c1f24f7e63c6b4','freshMacSource':False,'files':binding,'noArticulatedRuntimeSchemaFound':True,'nativeExportAdmission':False,'knownMismatch':'source1024 edge exceeds inspected256 max;5nativeframes exceed65536 decodedpixel budget; continuousalpha/palette also require reviewed export, preening not inspected runtimekey'}}
(P/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');assert all(x['protectedRGBAChangedPixels']==0 and x['sourceFootPixelNeighborhoodsExact'] for x in metrics)
(P/'pixel-measurements.json').write_text(json.dumps({'passedTechnicalProtectedRegion':True,'nativePixelPreservationOnlyNotArtApproval':True,'frames':metrics,'visibleProtectedRGBAExactFraction':1.0,'newGeneratedDrawings':0},indent=2)+'\n')
print(json.dumps({'proofFrames':5,'distinctAssemblies':3,'newGeneratedDrawings':0,'protectedRegionChangedPixels':0,'maximumUncoveredHeadMaskPixels':max(x['restSupportMaskUncoveredPixelsAlpha128'] for x in metrics)}))
