from pathlib import Path
from PIL import Image
import json,hashlib,numpy as np,datetime
p=Path(__file__).parent;s=p.parent/'shared';h=lambda f:hashlib.sha256(Path(f).read_bytes()).hexdigest();j=lambda f:json.loads((p/f).read_text())
def save(f,d):(p/f).write_text(json.dumps(d,indent=2)+'\n')
c=[]
def check(n,a):c.append({'check':n,'pass':bool(a)});assert a,n
m=j('PRIMARY-SOURCE-MANIFEST.json');proof=j('measurement-proof.json');a=Image.open(p/'original.png').convert('RGBA');b=Image.open(p/'settle144x96.png').convert('RGBA');crop=Image.open(p/'settle136x80.png').convert('RGBA');prompt=(p/'prompt.txt').read_bytes();args=j('native-call-arguments.json');dispatch=j('call-dispatch-receipt.json');contract=json.loads((s/'reference-contract.json').read_text())
check('Native actualRGBA3:2',a.size==(1536,1024) and Image.open(p/'original.png').mode=='RGBA')
check('Original PNG exact receipt hash',h(p/'original.png')==j('native-return-receipt.json')['originalSHA256']==m['originalSHA256'])
check('Primary decoded nativeRGBA identity',m['frames'][0]['sourceFrameId']=='frame.sha256.'+hashlib.sha256(b'RGBA8;1536x1024;'+a.tobytes()).hexdigest())
check('Prompt2531bytes exact submitted equality',len(prompt)==2531 and prompt==args['arguments']['prompt'].encode())
check('Prompt hash exact dispatch',h(p/'prompt.txt')==dispatch['promptSHA256']==m['promptSHA256'])
check('Native args exact dispatch hash',h(p/'native-call-arguments.json')==dispatch['nativeArgumentsSHA256'])
check('Shared conditioning exact reference hash',h(s/'conditioning-awake576x384.png')==contract['files']['conditioning-awake576x384.png']==dispatch['referenceSHA256'])
check('Shared conditioning exact4x byte copies',Image.open(s/'exact-awake144x96.png').convert('RGBA').resize((576,384),Image.Resampling.NEAREST).tobytes()==Image.open(s/'conditioning-awake576x384.png').convert('RGBA').tobytes())
check('Reused exact current awake144 bytes',(p/'reused-awake144x96.png').read_bytes()==(s/'exact-awake144x96.png').read_bytes())
check('Reused exact current awake136 bytes',(p/'reused-awake136x80.png').read_bytes()==(s/'exact-awake136x80.png').read_bytes())
x=np.floor((np.arange(144)+.5)*1536/144).astype(int);y=np.floor((np.arange(96)+.5)*1024/96).astype(int);expected=np.array(a)[y[:,None],x[None,:]]
check('Wholecanvas nearest explicitRGBA byte-copy',np.array_equal(expected,np.array(b)))
check('Fixed identical crop byte exact',b.crop((4,8,140,88)).tobytes()==crop.tobytes())
check('Runtime-size136x80 density1 fixed pivot77,76',crop.size==(136,80) and m['frames'][0]['registration']['outputPivot']==[77,76] and m['frames'][0]['registration']['density']==1)
check('Exact fixedcrop alpha loss retained and disclosed',proof['positiveAlphaOutsideCommonCropByThreshold']=={'1':1,'16':0,'128':0,'240':0})
check('No new contacts or support approval',proof['newContacts']==[] and proof['supportWorld'] is None and proof['geometryReviewed'] is False)
check('Single new source only zero new neutral',len(m['frames'])==1 and m['newActualDrawings']==1 and m['newNeutralDrawings']==0 and m['nativeCalls']==1)
check('No perpose body fit snap paint cleanup',all(m['frames'][0]['registration'][k] is False for k in ['perPoseFit','snap','paint','warp','alphaCleanup']))
proofa=Image.open(p/'awake-settle-proof.apng');dur=[]
for i in range(proofa.n_frames):proofa.seek(i);dur.append(proofa.info['duration'])
check('One-shot APNG exact3references2800ms',proofa.n_frames==3 and sum(dur)==2800 and proofa.size==(144,96))
check('Exact crop output filehash',m['frames'][0]['outputPNGsha256']==h(p/'settle136x80.png'))
# Original native support retained too: no native-positive alpha outside the mapped common crop.
arr=np.array(a);nativeOutside=np.ones(arr.shape[:2],bool);nativeOutside[86:938,43:1493]=False
nativeOut=int(((arr[:,:,3]>0)&nativeOutside).sum())
# Report bounds separately; deterministic output-crop proof is authoritative for144 renderer.
save('verification.json',{'status':'PASS','criticalChecks':len(c),'checks':c,'nativePositiveAlphaOutsideConservativeMappedCrop':nativeOut,'cropProofScope':'Exact144 output commoncrop;native original retained unchanged','PillowNearestSelectionNote':'Initial comparator found2595pixels differ from floor-center tie-index convention. Explicit integer-index straightRGBA export is used, preserving sampled bytes; no premultiply/painting.','noBrowserCaptureBytes':True,'sourceOnly':True,'geometryReviewed':False,'supportWorld':None,'canonicalAdmission':'NOT_RUN'})
save('producer-verdict.json',{'status':'HELD_FOR_PARENT_PILOT_REVIEW','newDrawings':1,'acceptedFullBathingSlots':0,'correctAspect':True,'newOutputCropLoss':1,'oldVisibleWidth':118,'newVisibleWidth':120,'poseEnvelopeInterpretation':'Real low settle changes height68→58; width change alone is not a biological scale approval','footSupport':'New lower-foot samples y82/81 vs proposedfloor84;oldmarkers73,83/92,83 nowalpha0. No source translation/snap;held/unbound.','billWater':'Settle is head-raised and has no beak-water contact intent;bill diagnostic not an admitted contact','newContacts':[],'geometryReviewed':False,'supportWorld':None,'allocationCompleteNoAdditionalCalls':True,'runningNativeCalls':0,'noAutomaticRetry':True,'nextStep':'Parent review; this worker two-phase allocation is complete, no additional generation'})
(p/'README.md').write_text('''# Mourning Dove single-pose SETTLE pilot

One native edit call produced one new1536×1024RGBA drawing. Original PNG/prompt/arguments/dispatch/return receipts are retained. Exact existing awake supplied in the shared576×384 conditioning reference is reused; no new neutral or full bath animation is claimed.

The whole native3:2 canvas is reduced to144×96 by explicit nearest sample indices floor((index+0.5)*nativeEdge/outputEdge), copying straight RGBA bytes. Pillow's own nearest tie selections differed at2595pixels during the comparator check; the explicit index convention is authoritative and retained in export.py. No Sharp premultiplication, body fitting, painting, toe snapping, rescaling by pose bounds or alpha cleanup occurred. The identical crop[4,8,140,88] gives136×80, density1, pivot[77,76]. One faint positive-alpha output pixel is outside this fixed crop (belowalpha16). Full144/native retain it; crop loss is disclosed and held, never cleaned/painted.

The new pose is a real low body/neck settle. Old alpha128 envelope118×68 versus new120×58 shows much better framing than the failed six-cell V1, but is not anatomical scale acceptance. New foot-region pixels sit at y82/81 against proposedfloor84, while inherited toe markers now have zero alpha. This settle has no beak-water contact intent. Contact regions/markers are diagnostic; contacts=[], geometryReviewed=false and supportWorld=null. No calibrated bath geometry or accepted event schema was supplied.

Open review.html for exact-size light/dark comparison, enlarged feet/head and a one-shot old/settle/old APNG. The2800ms proof timing is authored comparison only. Current producer status is HELD for parent pilot review; no support/full bathing/runtime admission, automatic retry or settle generation is authorized by this packet. Existing V1 files were untouched. This folder has no Git/global queue/bank/Library writes. Only an existing generated image was conditioned; generated-reference rights remain unreviewed, no third-party photo pixels used. Root owns any next action.
''')
files={str(f.relative_to(p)):h(f) for f in sorted(p.rglob('*')) if f.is_file() and f.name not in ['review-target-hashes.json','STABLE-GO.json']}
save('review-target-hashes.json',files)
go={'batchId':'sd20-mourning-dove-bathe-singlepose-v2-settle','state':'STABLE_HELD_PILOT_FOR_PARENT_REVIEW','nativeCalls':1,'newActualDrawings':1,'reusedExactAwake':1,'runningCalls':0,'payloadFiles':len(files),'payloadBytes':sum((p/f).stat().st_size for f in files),'ledgerSHA256':h(p/'review-target-hashes.json'),'primarySHA256':h(p/'PRIMARY-SOURCE-MANIFEST.json'),'originalSHA256':h(p/'original.png'),'primarySourceID':m['frames'][0]['sourceFrameId'],'output144SHA256':h(p/'settle144x96.png'),'output136SHA256':h(p/'settle136x80.png'),'criticalChecks':len(c),'geometryReviewed':False,'supportWorld':None,'acceptedBathingGain':0,'nextStep':'Parent review; allocation complete, no additional call or retry','frozenUTC':datetime.datetime.now(datetime.timezone.utc).isoformat()};save('STABLE-GO.json',go)
print(json.dumps({'GO':h(p/'STABLE-GO.json'),**go},indent=2))
