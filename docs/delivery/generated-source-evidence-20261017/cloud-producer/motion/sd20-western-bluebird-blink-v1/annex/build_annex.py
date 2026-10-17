from pathlib import Path
import json,hashlib,copy,datetime
from PIL import Image
A=Path(__file__).parent;D=A.parent;B=Path('/workspace/asset-production/new-species/sd20-final-four-v1/western_bluebird');C=Path('/workspace/chirp-finch-preen-canon/docs/delivery/generated-source-evidence-20261017/cloud-producer/new-species/sd20-final-four-v1/western_bluebird')
sha=lambda b:hashlib.sha256(b).hexdigest()
def rid(im):return 'frame.sha256.'+sha(f'RGBA8;{im.width}x{im.height};'.encode()+im.convert('RGBA').tobytes())
def dump(p,j):(A/p).write_text(json.dumps(j,indent=2,ensure_ascii=False)+'\n')
# Read-only frozen baseline. This script writes only its own annex directory.
frozen={str(p.relative_to(D)):sha(p.read_bytes()) for p in D.rglob('*') if p.is_file() and A not in p.parents}
oldPath=B/'texture-review-manifest.json';old=json.loads(oldPath.read_text());assert oldPath.read_bytes()==(C/'texture-review-manifest.json').read_bytes();oldNeutral=old['frames'][0]
frameMapPath=D/'frame-to-action-map.json';frameMap=json.loads(frameMapPath.read_text());expectedMapSHA='f5cab78c64940481725fce2147ece5efe8e0db7041f5a63e2ffbd7218134249f';assert sha(frameMapPath.read_bytes())==expectedMapSHA
assert oldNeutral['pivot']=={'x':114,'y':150};assert oldNeutral['contacts']==[{'id':'foot-1','x':112,'y':148},{'id':'foot-2','x':115,'y':148}]
primary=json.loads((D/'PRIMARY-SOURCE-MANIFEST.json').read_text());sourceIDs=[f['sourceFrameId'] for f in primary['reusedFrames']+primary['frames']]
checks=[];variants=[]
for v in frameMap['variants']:
 name=v['variant'];atlasPath=D/v['atlasFile'];atlas=Image.open(atlasPath).convert('RGBA');assert sha(atlasPath.read_bytes())==v['atlasSHA256'];assert list(atlas.size)==v['atlasDimensions']==[384,192]
 frames=[];maps=[]
 for f in v['frames']:
  pngPath=D/f['individualPNG'];im=Image.open(pngPath).convert('RGBA');r=f['sourceRect'];tile=atlas.crop((r['x'],r['y'],r['x']+r['width'],r['y']+r['height']));assert im.size==(192,192);assert tile.tobytes()==im.tobytes();assert sha(pngPath.read_bytes())==f['individualPNGsha256'];assert f['sourceFrameId'] in sourceIDs
  frame={k:copy.deepcopy(oldNeutral[k]) for k in ['canvas','trim','pivot','contacts','world','sourcePixelsPerWorldUnit']};frame.update(id=f['renderId'],sourceRect=copy.deepcopy(r));frames.append(frame)
  contacts=[]
  for p in frame['contacts']:
   alpha=im.getpixel((p['x'],p['y']))[3];contacts.append({**p,'sampledAlpha':alpha,'positiveAlpha':alpha>0,'alphaAtLeast128':alpha>=128,'anatomicalSupportApproved':False});assert alpha>0
  maps.append({'renderFrameId':f['renderId'],'renderRGBAId':rid(im),'renderPNG':'../'+f['individualPNG'],'renderPNGsha256':sha(pngPath.read_bytes()),'sourceFrameId':f['sourceFrameId'],'sourceStatus':f['sourceStatus'],'sourceRect':copy.deepcopy(r),'sourceRectRGBAExact':True,'technicalContactSamples':contacts,'registeredDerivativeIsNewDrawing':False if name=='registered' else None})
 contract={'schemaVersion':1,'profile':'chirp-texture-review-v1','scope':'review-only','approval':'unreviewed','activation':'none','source':{'sha256':sha(atlasPath.read_bytes()),'creator':'Chirp metadata-only Bluebird technical contract annex','tool':'Metadata projection of unchanged frozen render atlas and original neutral geometry','toolVersion':'1','rights':'unreviewed','fidelity':'unreviewed'},'atlas':{'width':384,'height':192,'alpha':'straight-rgba8','colorSpace':'srgb'},'frames':frames,'clips':[{'id':'idle','tickRate':30,'loop':True,'frames':[{'frameId':maps[0]['renderFrameId'],'durationTicks':60},{'frameId':maps[1]['renderFrameId'],'durationTicks':3},{'frameId':maps[0]['renderFrameId'],'durationTicks':27}]}]}
 # Strict local shape, layout and pixel checks; this is not canonical Zod/Sharp execution.
 assert set(contract)==set(old)
 assert set(contract['source'])==set(old['source'])
 assert len(json.dumps(contract).encode())<=65536 and atlasPath.stat().st_size<=4*1024*1024
 assert max(atlas.size)<=1024 and all(max(f['canvas'].values())<=512 for f in frames)
 ids={f['id'] for f in frames};assert len(ids)==2
 for f in frames:
  assert set(f)==set(oldNeutral)
  assert 1<=len(f['contacts'])<=4 and all(set(p)=={'id','x','y'} for p in f['contacts'])
  assert f['world']==oldNeutral['world'] and f['sourcePixelsPerWorldUnit']==1.1
  assert abs(f['world']['width']*1.1-192)<1e-9 and abs(f['world']['height']*1.1-192)<1e-9
  assert f['pivot']==oldNeutral['pivot'] and f['contacts']==oldNeutral['contacts'] and f['trim']=={'x':0,'y':0}
  assert 0<=f['pivot']['x']<192 and 0<=f['pivot']['y']<192
  assert all(0<=p['x']<192 and 0<=p['y']<192 for p in f['contacts'])
  r=f['sourceRect'];assert 0<=r['x'] and 0<=r['y'] and r['x']+r['width']<=384 and r['y']+r['height']<=192
 seq=contract['clips'][0];assert seq['id']=='idle' and seq['tickRate']==30 and seq['loop'] is True
 assert [s['durationTicks'] for s in seq['frames']]==[60,3,27] and all(s['frameId'] in ids for s in seq['frames']);assert sum(s['durationTicks'] for s in seq['frames'])==90
 for key in ['canvas','world','sourcePixelsPerWorldUnit','pivot','contacts']:assert frames[0][key]==frames[1][key]
 file=f'{name}-texture-review-manifest.json';dump(file,contract)
 variants.append({'variant':name,'technicalContract':file,'technicalContractSHA256':sha((A/file).read_bytes()),'atlasPNG':'../'+v['atlasFile'],'atlasSHA256':sha(atlasPath.read_bytes()),'atlasDimensions':list(atlas.size),'frozenSourceMapClipId':v['clips'][0]['id'],'annexClipId':'idle','orderedSourceFrameSequence':[{'renderFrameId':maps[0]['renderFrameId'],'sourceFrameId':maps[0]['sourceFrameId'],'durationTicks':60},{'renderFrameId':maps[1]['renderFrameId'],'sourceFrameId':maps[1]['sourceFrameId'],'durationTicks':3},{'renderFrameId':maps[0]['renderFrameId'],'sourceFrameId':maps[0]['sourceFrameId'],'durationTicks':27}],'frames':maps,'localShapeAndPixelChecksPassed':True,'sourceArtPreferred':None,'canonicalSharpReceipt':None,'canonicalMacAdmission':False,'physicalContactApproved':False})
 checks.extend([{'variant':name,'check':n,'pass':True} for n in ['exactAtlasHashAnd384x192Layout','exactFrozenRenderPNGHashesAndRectPixels','sourceIDsSeparateFromRenderDerivativeIDs','oldNeutralPivot150AndContacts148InheritedExactly','allFourTechnicalContactSamplesPositiveAlpha','192CanvasDensity1point1World174point545Contract','sameCanvasWorldDensityPivotContactsAcrossIdle','strictLocalManifestKeysAndBudgets','idle30Hz60_3_27ThreeSecondLoop']])
link={'schemaVersion':1,'kind':'additive-technical-contract-annex-not-new-source-art','batchId':frameMap['batchId'],'createdUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'frozenFrameToActionMap':'../frame-to-action-map.json','frozenFrameToActionMapSHA256':expectedMapSHA,'frozenSourceCustomManifest':'../blink-manifest.json','frozenSourceCustomManifestSHA256':sha((D/'blink-manifest.json').read_bytes()),'frozenPrimarySourceManifest':'../PRIMARY-SOURCE-MANIFEST.json','frozenPrimarySourceManifestSHA256':sha((D/'PRIMARY-SOURCE-MANIFEST.json').read_bytes()),'sourceFrameIDs':sourceIDs,'newDrawingsFromAnnex':0,'newGenerationCalls':0,'originalNeutralContract':{'sourcePath':str(oldPath),'canonicalSourcePath':'new-species/sd20-final-four-v1/western_bluebird/texture-review-manifest.json','SHA256':sha(oldPath.read_bytes()),'pivot':oldNeutral['pivot'],'contacts':oldNeutral['contacts'],'canvas':oldNeutral['canvas'],'density':oldNeutral['sourcePixelsPerWorldUnit'],'world':oldNeutral['world']},'pivotClarification':{'earlierProseReminder':[114,148],'actualOriginalManifestPivot':[114,150],'customProducerPivot':[114,150],'actualProducerVersusOriginalDiscrepancy':False,'explanation':'Earlier coordinator reminder from this worker confused foot-marker y148 with pivoty150. Saved producer-reference-contracts JSON and both local/canonical original manifests already use150. Annex inherits verified original150, not the erroneous prose148. No frozen input or geometry was changed.'},'variantBindings':variants,'preferredVariant':'pending independent source-art review; technicalshape doesnotchooseart','sourceArtAcceptance':False,'packetShapeOnly':True,'canonicalZodSharpExecuted':False,'MacIntakeAdmission':False,'actualYardBinding':'UNKNOWN','contactsQualification':'Original expected image-space foot markers, tested for positive alpha only. Registered closed foot-2 alpha74 is semitransparent; positive alpha is not opaque toe support or anatomical/physics approval.','sourceAndPixelFilesEdited':False,'frozenFilesEdited':False}
dump('technical-contract-annex.json',link)
assert all(sha((D/p).read_bytes())==h for p,h in frozen.items())
dump('verification.json',{'kind':'local-additive-contract-shape-and-alpha-checks','createdUTC':link['createdUTC'],'passed':len(checks),'total':len(checks),'checks':checks,'frozenFilesUnchangedCount':len(frozen),'allFrozenFilesUnchanged':True,'allContactSamplesPositive':True,'registeredClosedFoot2Alpha':74,'alpha128AllContactsPass':False,'alpha128IsNotInventedAsThisAnnexGate':True,'canonicalZodSharpExecution':False,'MacAdmission':False,'noNewDrawingsOrCalls':True,'captureBytesAdded':False})
readme='''# Bluebird technical review contract annex

This is additive metadata only. No source pixels, frozen atlases, PRIMARY manifest, custom blink manifest or frame-to-action map were changed. The two contracts project the existing native and registered atlas variants into the existing chirp-texture-review-v1 review-only shape, with approval unreviewed and activation none.

Use each contract with its exact linked atlas in technical-contract-annex.json. Both use192×192 frame canvases, density1.1 and world canvas174.54545454545453, an idle clip at30Hz and60/3/27ticks (3seconds). Existing render IDs and source rectangles are retained. Source drawing IDs remain distinct from render/export IDs; the registered derivative adds no drawing.

The verified original neutral pivot is[114,150], with technical foot markers[112,148] and[115,148]. An earlier prose reminder from this worker incorrectly said pivot[114,148]; it confused the foot-marker row with the pivot. Both original local/canonical manifests and the frozen producer use150. The annex therefore preserves the actual old geometry and discloses the mistaken prose rather than fabricating a producer anchor discrepancy.

Native awake foot alphas are248/231; native closed251/249; registered closed250/74. All original markers are alpha-positive in both frames of each variant. Registered foot-2 is semitransparent. These are image-space technical markers, not anatomical support, opaque toe coverage, branch grip, physics or real yard contact approval. No invented alpha128 gate is used to silently change markers.

Local checks cover exact atlas/hash/rect-to-render-PNG mapping, dimensions, strict manifest field shape, canvas/world/density equality, same idle geometry, contact bounds/alpha and timing/clip IDs. No canonical Zod/Sharp execution or Mac admission happened here. Technical packet shape is separate from provisional source-art review, body redraw, foot continuity and preferred variant. Independent review determines any source preference; no default activation follows.

The annex pins the exact frozen frame-to-action-map SHA and source IDs. No new generation, Library upload, global metadata or Git changes occurred. Browser capture bytes are not added.
'''
for old,new in [('use192','use 192'),('density1.1','density 1.1'),('canvas174','canvas 174'),('at30','at 30'),('and60','and 60'),('3seconds','3 seconds'),('pivotis[','pivot is ['),('is[114','is [114'),('markers[','markers ['),('and[115','and [115'),('are248','are 248'),('closed251','closed 251'),('closed250','closed 250'),('alpha128','alpha 128')]:readme=readme.replace(old,new)
(A/'README.md').write_text(readme)
print(json.dumps({'contracts':[{'variant':v['variant'],'file':v['technicalContract'],'sha256':v['technicalContractSHA256'],'contactAlphas':[[p['sampledAlpha'] for p in f['technicalContactSamples']] for f in v['frames']]} for v in variants],'checks':len(checks),'frozenFilesUnchanged':len(frozen),'frameMapSHA256':expectedMapSHA,'actualPivot':oldNeutral['pivot']},indent=2))

# Optional independent source preference is additive and does not change contracts/art.
review=D/'independent-review.json'
if review.exists() and sha(review.read_bytes())=='38ac6f707dd828c6760e8babee9a0650ec77b5c238ce30e7ee7a0e2d73311b53':
 j=json.loads((A/'technical-contract-annex.json').read_text());j['preferredVariant']='registered: provisional independent source-art choice; raw native control retained';j['technicalPacketShapePrepared']=True;j['independentSourceArtReview']={'JSON':'../independent-review.json','JSONsha256':'38ac6f707dd828c6760e8babee9a0650ec77b5c238ce30e7ee7a0e2d73311b53','Markdown':'../independent-review.md','Markdownsha256':'8da04786ced323ecc26c9e035288b50cad7fafde4088f1e0b5600b7c2fef60c7','preference':'registered','sourceOnly':True,'canonicalAdmission':False,'packetBindingReadyInArtReview':False,'annexTechnicalReviewStillPending':True}
 for v in j['variantBindings']:v['sourceArtPreferred']=v['variant']=='registered'
 dump('technical-contract-annex.json',j)
