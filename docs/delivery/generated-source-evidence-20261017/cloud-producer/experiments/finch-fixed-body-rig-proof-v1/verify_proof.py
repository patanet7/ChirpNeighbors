from pathlib import Path
from PIL import Image
import hashlib,json,numpy as np,importlib.util,os
P=Path(__file__).parent;m=json.loads((P/'manifest.json').read_text());src=Image.open(P/'source-neutral.png').convert('RGBA');a=np.array(src);assert hashlib.sha256((P/'source-neutral.png').read_bytes()).hexdigest()==m['sourcePNGsha256'];checks=['retained neutral source identity fixed'];unique=set();maxchanged=0;sourceColors=set(map(bytes,a[a[:,:,3]>0]))
for e in m['frames']:
 p=P/e['file'];assert hashlib.sha256(p.read_bytes()).hexdigest()==e['sha256'];im=Image.open(p).convert('RGBA');b=np.array(im);assert set(map(bytes,b[b[:,:,3]>0]))<=sourceColors;assert im.size==(1024,1024);unique.add(hashlib.sha256(im.tobytes()).hexdigest());changed=np.any(a[600:]!=b[600:],axis=2).sum();assert changed==0;maxchanged=max(maxchanged,int(changed))
 for c in m['fixedContacts']:
  x,y=c['source'];assert np.array_equal(a[y-8:y+2,x-8:x+8],b[y-8:y+2,x-8:x+8])
 if e['angleRadians']==0:assert im.tobytes()==src.tobytes()
assert len(unique)==3;checks+=['all5 derived canvases fixed1024;3 unique cutout states;every visibleRGBA tuple from retained source','all protectedRGBA and both source foot neighborhoods exactly retained','neutral entry/exit byte-identical; no sequence art approval']
bad=a.copy();bad[790:800,480:490,0]^=1;assert np.any(a[600:]!=bad[600:],axis=2).sum()==100;checks+=['negative control detects100 changed protectedpixels']
for n in ['rig-preview.apng','rig-preview.gif']:
 with Image.open(P/n) as im:
  assert im.n_frames==5
  for i in range(5):im.seek(i);im.load();assert im.info['duration']==160
for i in range(5):
 im=Image.open(P/f'outline-{i:02}.png');assert im.size==(512,512);assert set(np.unique(np.array(im.convert('L'))))<={0,255}
checks+=['five160ms diagnosticAPNG/GIF phases decode','five512px contour-only guides have binary black-on-white values; no semantic/depth claim']
assert m['newGeneratedDrawings']==m['newGenerationCalls']==0 and not m['artAccepted'] and not m['runtimeIntegrated'];checks+=['zero new generation, no acceptance/integration promotion']
receipt={'passed':True,'checksPassed':len(checks),'checks':checks,'uniqueDerivedStates':3,'sourceBodyScale':1,'maxProtectedChangedPixels':maxchanged,'visibleProtectedRGBAExactFraction':1.0,'neutralSourceReusedForEngineeringOnly':True,'biologicalIdentityApproved':False,'anatomySeamMotionApproved':False,'newGeneratedDrawings':0,'productionReuseVerified':False};(P/'verification.json').write_text(json.dumps(receipt,indent=2)+'\n')
hardware={'torchInstalled':bool(importlib.util.find_spec('torch')),'diffusersInstalled':bool(importlib.util.find_spec('diffusers')),'transformersInstalled':bool(importlib.util.find_spec('transformers')),'nvidiaDevicesVisible':[str(p) for p in Path('/dev').glob('nvidia*')],'gpuMemoryMeasured':False,'modelWeightsInspected':False,'newInstallPerformed':False,'nativeImageInterfaceHardMaskAvailable':False,'nativeImageInterfaceControlNetAvailable':False,'cpuProofExecutable':True,'inferenceFeasibility':'blocked: no installed compatible model pipeline/weights or verified accelerator; no generation authorized at this step'};(P/'capability-check.json').write_text(json.dumps(hardware,indent=2)+'\n');print(json.dumps(receipt));print(json.dumps(hardware))
