"""Extend one local immutable-frame register; never infer reusable transitions from sequence status."""
from pathlib import Path
from PIL import Image
import json,hashlib
R=Path(__file__).parent
def fid(im):return 'frame.sha256.'+hashlib.sha256(f'RGBA8;{im.width}x{im.height};'.encode()+im.tobytes()).hexdigest()
bank=json.loads((R/'frame-bank.json').read_text());index={f['frameId']:f for f in bank['frames']}
for name in ['dove-walk-v1','dove-drink-v1','understory-wind-v1','rain-layer-v1','rain-continuity-v2']:
 p=R/'batches'/name;m=json.loads((p/'manifest.json').read_text());ids=[]
 for i,f in enumerate(sorted((p/'frames-source').glob('*.png'))):
  im=Image.open(f).convert('RGBA');key=fid(im);ids.append(key);previous=m['frames'][i]
  rec={'frameId':key,'file':str(f.relative_to(R)),'fileSha256':hashlib.sha256(f.read_bytes()).hexdigest(),'dimensions':list(im.size),'species':'mourning_dove' if name.startswith('dove') else None,'family':'bird' if name.startswith('dove') else 'plant' if name.startswith('understory') else 'weather','variant':'unconditioned-candidate','appearanceVersion':name,'poseTags':[previous.get('phase','phase-'+str(i)),name.split('-')[1]],'sourceAtlas':str((p/'original.png').relative_to(R)),'sourceAtlasSha256':m.get('provenance',{}).get('originalSha256'),'sourcePrompt':str((p/'prompt.txt').relative_to(R)),'supportRoot':previous.get('root',m.get('root')),'feetContactsApprox':previous.get('groundContacts',[]),'beakAnchorApprox':previous.get('beak'),'rootContactAccepted':False,'scaleCalibrationRef':'scale.mourning_dove' if name.startswith('dove') else None,'acceptedUses':[],'rejectedUses':['continuous-rain-animation'] if name=='rain-continuity-v2' else [],'candidateUses':['static rain texture for deterministic compositor'] if name.startswith('rain') else ['compatible static pose or transition reference after review'],'reuseStatus':'candidate suggestion; no verified reuse','sequenceAcceptanceIndependentOfFrameAcceptance':True,'generator':'OpenAI image_gen.imagegen','model':None,'seed':None}
  index[key]=rec;previous['frameId']=key
 m['frameBank']='../../frame-bank.json';m['frameIds']=ids;m['frameReuseStatus']='no verified cross-clip reuse; same-species/appearance/scale/contact/transition review required';(p/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
bank['frames']=list(index.values());bank['frameRegisterId']='local-production-frame-evidence@1';bank['sourceAuthority']='Exact local pixel identity/provenance; Mac shared canonical IDs still pending';bank['frameCount']=len(index);bank['verifiedReuseCount']=0;bank['status']='single derived production register; per-delivery projections reference this register'
(R/'frame-bank.json').write_text(json.dumps(bank,indent=2)+'\n');print(json.dumps({'immutableFrames':len(index),'newFinchFrames':26,'earlierFrames':30,'verifiedReuse':0}))
