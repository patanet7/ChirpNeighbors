from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,subprocess,time
import numpy as np
from PIL import Image
R=Path('/workspace/asset-production');P=R/'experiments/crow-perch-grip-art-internal-v2';C=P/'codec-study';C.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def put(p,j):p.write_text(json.dumps(j,indent=2,ensure_ascii=False)+'\n')
assert not (C/'PREREGISTRATION.json').exists(),'One bounded export only'
source=P/'grip-study192.png';master=R/'audits/crow-ground-runtime-compatible-v1/palette-variants/crow-ground-idle186-total12.png'
assert sha(source)=='37881c2571d09a419349d341aeaf6524fcb3a6ae6918caa27b6041c3ac871d29'
assert sha(master)=='6832bffeb9a2a2dd871be0ca1315e29b184459ff535a4539001a9d73bda81a91'
a=np.asarray(Image.open(source).convert('RGBA'));m=np.asarray(Image.open(master).convert('RGBA'));palette=np.unique(m[m[:,:,3]>0,:3],axis=0).astype(np.int32);assert palette.shape==(11,3)
recipe={'id':'crow-perch-fixed-master-palette-v1','createdUTC':datetime.now(timezone.utc).isoformat(),'scope':'One zero-native codec repair; original raw failure remains immutable','nativeCalls':0,'newPrimaryDrawings':0,'exportCeiling':1,'automaticRetries':0,'input':{'file':'../grip-study192.png','sha256':sha(source)},'masterPalette':{'sourcePNGsha256':sha(master),'source':'audits/crow-ground-runtime-compatible-v1/palette-variants/crow-ground-idle186-total12.png','opaqueRGB':palette.tolist(),'selection':'All exact eleven opaque colors, lexicographically sorted; no palette search/requantization'},'algorithm':{'alpha':'source alpha>=128 becomes255, otherwise transparent black','RGB':'Nearest squared Euclidean RGB distance to fixed master palette; equal-distance ties choose lexicographically first','dithering':False,'resize':False,'translation':False,'painting':False,'perPoseFit':False},'canvas':[192,192],'sourcePixelsPerWorldUnit':1.0328947368421053,'pivot':[111,150],'contacts':[],'supportWorld':None,'geometryReviewed':False,'reviewPlan':'One actual pinned pixel diagnostic and independent normal-size palette/toe comparison; fail retained without further palette/size variants','runtimeAdmission':False}
put(C/'PREREGISTRATION.json',recipe)
flat=a[:,:,:3].reshape(-1,3).astype(np.int32);delta=flat[:,None,:]-palette[None,:,:];indices=(delta*delta).sum(axis=2).argmin(axis=1)
out=np.zeros_like(a);keep=a[:,:,3]>=128;out[:,:,:3]=palette[indices].astype(np.uint8).reshape(a.shape[:2]+(3,));out[:,:,3]=np.where(keep,255,0);out[~keep]=0
dest=C/'crow-grip-fixed12-192.png';Image.fromarray(out,'RGBA').save(dest)
fid='frame.sha256.'+hashlib.sha256(b'RGBA8;192x192;'+out.tobytes()).hexdigest()
source_opaque=a[:,:,3]>0;removed=source_opaque&~keep
facts={'sourcePNGsha256':sha(source),'outputPNG':dest.name,'outputPNGsha256':sha(dest),'decodedRGBAId':fid,'canvas':[192,192],'opaqueColors':len(np.unique(out[keep,:3],axis=0)),'alphaValues':np.unique(out[:,:,3]).tolist(),'nonzeroAlphaSourcePixels':int(source_opaque.sum()),'retainedOpaquePixels':int(keep.sum()),'removedNonzeroFringePixels':int(removed.sum()),'maskExactlySourceAlphaGE128':True,'outputGridOrPivotMoved':False,'newNativeDrawings':0,'rawFailureRetained':'../contract-intake/ACTUAL-FAILURE-RECEIPT.json','sourceFootprintQualification':'Alpha threshold may remove faint claw fringe; no physical toe/support acceptance'}
put(C/'DERIVATION.json',facts)
cfg=json.loads((P/'contract-intake/canonical-pixel-input.json').read_text());cfg['frames']=[{'id':'crow-grip-fixed12','png':dest.name,'PNGsha256':sha(dest),'decodedRGBAId':fid}];cfg['paletteLimit']=64;put(C/'canonical-pixel-input.json',cfg)
args=['node',str(R/'validation/shared-structural-check.mjs'),'--repo','/workspace/runtime-resting-intake-v5-inspect','--input',str(C/'canonical-pixel-input.json'),'--receipt',str(C/'pixel-receipt.json'),'--sharp','/opt/codex/runtimes/codex-primary-runtime/dependencies/node/node_modules/sharp/dist/index.cjs']
start=time.monotonic();p=subprocess.run(args,capture_output=True,text=True);(C/'actual-pixel.stdout.txt').write_text(p.stdout);(C/'actual-pixel.stderr.txt').write_text(p.stderr)
put(C/'INVOCATION.json',{'command':args,'exitCode':p.returncode,'observedWallSeconds':time.monotonic()-start,'stdout':'actual-pixel.stdout.txt','stderr':'actual-pixel.stderr.txt','nativeCalls':0,'actualPixelRuns':1,'exportPasses':1,'automaticRetries':0})
put(C/'source-handoff.json',{'kind':'Static source-only codec derivative, not full render manifest','speciesId':'american_crow','sourcePrimaryID':'frame.sha256.54e8b2cf0e5e69a0b274ec9b477eab6dc5be249de9fda64fd5d918be8d7b561d','frame':{'id':'crow-grip-fixed12','png':dest.name,'PNGsha256':sha(dest),'decodedRGBAId':fid,'canvas':[192,192],'sourcePixelsPerWorldUnit':1.0328947368421053,'pivot':[111,150],'contacts':[]},'clips':[{'id':'perching-art-study','tickRate':30,'loop':False,'frames':[{'frameId':'crow-grip-fixed12','durationTicks':90}],'staticHoldOnly':True}],'geometryReviewed':False,'supportWorld':None,'runtimeAdmission':False,'artUsefulness':'PENDING independent derivative review','actualCodecExitCode':p.returncode})
print(json.dumps({'exportedOnce':True,'newNativeCalls':0,'PNGsha256':sha(dest),'pixelExitCode':p.returncode,'retainedOpaquePixels':int(keep.sum()),'removedFringe':int(removed.sum()),'stdout':p.stdout[-700:],'stderr':p.stderr[-700:]}))
