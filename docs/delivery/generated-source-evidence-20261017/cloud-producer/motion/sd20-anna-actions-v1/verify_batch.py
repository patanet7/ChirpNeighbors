from pathlib import Path
from PIL import Image
import hashlib,json,numpy as np
P=Path(__file__).parent;sha=lambda b:hashlib.sha256(b).hexdigest();L=json.loads((P/'source-lineage.json').read_text());M=json.loads((P/'texture-review-manifest.json').read_text());original=Image.open(P/'original.png').convert('RGBA');checks=[]
for f in L['frames']:
 im=Image.open(P/f['file']).convert('RGBA');expected=Image.new('RGBA',(1024,1024));expected.paste(original.crop(f['sourceRect']),f['registrationTranslation']);assert im.tobytes()==expected.tobytes();assert f['frameId']=='frame.sha256.'+sha(b'RGBA8;1024x1024;'+im.tobytes());assert sha((P/f['file']).read_bytes())==f['fileSha256'];out=Image.open(P/f['export']).convert('RGBA');assert out.tobytes()==im.resize((96,96),Image.Resampling.NEAREST).tobytes();assert sha((P/f['export']).read_bytes())==f['exportSha256']
checks+=['4registeredsourceIDsandPNGhashes','documentedoriginalcropandintegertranslation','wholecanvasnearest96pixels']
assert len(set(f['frameId'] for f in L['frames']))==4;checks+=['4distinctnewdrawings0newcanons']
atlas=Image.open(P/'idle-atlas96.png').convert('RGBA');assert M['source']['sha256']==sha((P/'idle-atlas96.png').read_bytes())
for f in M['frames']:
 r=f['sourceRect'];tile=atlas.crop((r['x'],r['y'],r['x']+96,r['y']+96));assert tile.tobytes()==Image.open(P/'frames96'/(f['id'].split('-')[1]+'.png')).convert('RGBA').tobytes()
 for c in f['contacts']:assert tile.getpixel((c['x'],c['y']))[3]>0
 assert f['world']['width']*f['sourcePixelsPerWorldUnit']==96
assert M['frames'][0]['contacts']==M['frames'][1]['contacts'];assert M['frames'][0]['pivot']==M['frames'][1]['pivot'];checks+=['idleatlasmetadatahashcontactsanddensity']
for name,ms,count in [('perched-idle.apng',3100,3),('hover-study.apng',2000/30,2)]:
 im=Image.open(P/name);assert im.n_frames==count;dur=[]
 for k in range(count):im.seek(k);dur.append(im.info['duration'])
 assert abs(sum(dur)-ms)<.0001
checks+=['exactrational30Hztiming']
result={'passed':True,'checks':checks,'newDrawings':4,'newCanons':0,'idlePacketBound':True,'hoverPacketBound':False,'appBound':False,'SharpCanonicalAdmission':False,'scope':'byte-integrity, exports, positive-alpha technical contacts and exact timing; not artistic or physical approval'};(P/'verification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
