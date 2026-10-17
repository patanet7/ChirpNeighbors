from pathlib import Path
from PIL import Image
import json,hashlib,numpy as np
P=Path(__file__).parent;sha=lambda b:hashlib.sha256(b).hexdigest();m=json.loads((P/'PRIMARY-SOURCE-MANIFEST.json').read_text());texture=json.loads((P/'texture-review-manifest.json').read_text());atlas=Image.open(P/'idle-look-atlas192.png').convert('RGBA');original=Image.open(P/'original.png').convert('RGBA');assert sha((P/'original.png').read_bytes())==m['originalSHA256'];assert sha((P/'prompt.txt').read_bytes())==m['promptSHA256'];assert m['nativeCalls']==1 and len(m['frames'])==2
checks=[]
for i,f in enumerate(m['frames']):
 im=Image.open(P/f['sourcePNG']).convert('RGBA');assert sha((P/f['sourcePNG']).read_bytes())==f['sourcePNGsha256'];assert 'frame.sha256.'+sha(f'RGBA8;{im.width}x{im.height};'.encode()+im.tobytes())==f['sourceFrameId']
 reg=f['registration'];x,y,w,h=reg['nativeCellRect'];raw=original.crop((x,y,x+w,y+h));expected=Image.new('RGBA',(1024,1024));expected.paste(raw,tuple(reg['translation']));assert expected.tobytes()==im.tobytes();assert reg['callWideSourceScale']==1
 out=Image.open(P/(f['pose']+'192.png')).convert('RGBA');assert im.resize((192,192),Image.Resampling.NEAREST).tobytes()==out.tobytes();assert out.tobytes()==atlas.crop((192*i,0,192*i+192,192)).tobytes();assert all(out.getpixel((c['x'],c['y']))[3]>0 for c in texture['frames'][i]['contacts']);checks.append({'pose':f['pose'],'sourceId':f['sourceFrameId'],'exactNativeCellsAndTranslationVerified':True,'exactNearestOutputAndAtlasVerified':True,'allDeclaredStudyContactsPositiveAlpha':True})
assert texture['source']['sha256']==sha((P/'idle-look-atlas192.png').read_bytes());assert atlas.width<=1024 and atlas.height<=1024 and atlas.width*atlas.height<=1048576;assert len((P/'texture-review-manifest.json').read_bytes())<65536;assert all(f['world']['width']*f['sourcePixelsPerWorldUnit']==192 for f in texture['frames'])
im=Image.open(P/'idle-look.apng');dur=[]
for i in range(im.n_frames):im.seek(i);dur.append(im.info.get('duration'))
assert im.n_frames==3 and dur==[2000.0,200.0,800.0]
fit=json.loads((P/'inclined-support-fit.json').read_text());support=json.loads((P/'support-measurements.json').read_text());points=np.array([item['source1024'][name]['pixelPoint'] for item in support['measurements'] for name in ['toe-upper','toe-lower','tail-tip']]);b,a=np.polyfit(points[:,1],points[:,0],1);assert abs(a-fit['jointFixedPlaneBothPoses']['a'])<1e-9 and abs(b-fit['jointFixedPlaneBothPoses']['b'])<1e-9
receipt={'sourceChecks':checks,'originalAndPromptHashesVerified':True,'decodedAPNGDurationsMs':dur,'manifestEnvelopeChecks':True,'actualZodSharpIntakeExecuted':False,'sharedInclinedFitRecomputedFromAllSixPoints':True,'requestedVerticalCorrectionPass':False,'inclinedAnatomyContactApproval':False,'actualMacContactVerified':False,'newNativeCalls':1,'newDrawings':2,'noBrowserCapturesIncluded':True};(P/'verification.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
