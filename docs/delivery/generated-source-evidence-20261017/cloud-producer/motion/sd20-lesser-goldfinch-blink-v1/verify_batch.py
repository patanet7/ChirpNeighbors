from pathlib import Path
from PIL import Image
import json,hashlib,numpy as np
P=Path(__file__).parent;sha=lambda b:hashlib.sha256(b).hexdigest();m=json.loads((P/'PRIMARY-SOURCE-MANIFEST.json').read_text());assert len(m['frames'])==1 and len(m['reusedFrames'])==1;assert sha((P/m['original']).read_bytes())==m['originalSHA256'];assert sha((P/m['prompt']).read_bytes())==m['promptSHA256'];assert (P/'original.png').read_bytes()==(P/'closed-native.png').read_bytes();checks=['one new native closure and byte-identical original retention']
for f in m['frames']+m['reusedFrames']:
 im=Image.open(P/f['sourcePNG']).convert('RGBA');assert f['sourceFrameId']=='frame.sha256.'+sha(f'RGBA8;{im.width}x{im.height};'.encode()+im.tobytes());assert sha((P/f['sourcePNG']).read_bytes())==f['sourcePNGsha256'];out=Image.open(P/f['outputPNG']).convert('RGBA');assert out.tobytes()==im.resize((96,96),Image.Resampling.NEAREST).tobytes();assert sha((P/f['outputPNG']).read_bytes())==f['outputPNGsha256']
checks+=['primary/reused IDs and source hashes','whole-native-canvas nearest exports, no perpose fit']
ref=Path('/workspace/asset-production/new-species/sd20-next-three-canon-v1/lesser_goldfinch');assert (ref/'neutral-source1024.png').read_bytes()==(P/'reused-awake-source1024.png').read_bytes();assert (ref/'neutral96.png').read_bytes()==(P/'reused-awake96.png').read_bytes();checks+=['existing awake source and output PNG reused byte-identical']
T=json.loads((P/'texture-review-manifest.json').read_text());R=json.loads((P/'reference-intake-manifest.json').read_text());atlas=Image.open(P/'idle-blink-atlas96.png').convert('RGBA');assert T['source']['sha256']==sha((P/'idle-blink-atlas96.png').read_bytes());assert T['frames'][0]==R['frames'][0]
for i,f in enumerate(T['frames']):
 tile=atlas.crop((i*96,0,(i+1)*96,96));assert tile.tobytes()==Image.open(P/['reused-awake96.png','closed96.png'][i]).convert('RGBA').tobytes();assert f['contacts']==R['frames'][0]['contacts'];assert f['pivot']==R['frames'][0]['pivot'];assert f['world']==R['frames'][0]['world'];assert f['sourcePixelsPerWorldUnit']==R['frames'][0]['sourcePixelsPerWorldUnit']
 for c in f['contacts']:assert tile.getpixel((c['x'],c['y']))[3]>0
checks+=['unchanged scale, world, pivot and technical contacts across atlas']
mapping=json.loads((P/'frame-to-action-map.json').read_text());binding=mapping['atlasBinding'];assert binding['sha256']==sha((P/binding['file']).read_bytes())==T['source']['sha256'];assert atlas.size==(binding['width'],binding['height']);assert mapping['manifest']['sha256']==sha((P/mapping['manifest']['file']).read_bytes());assert mapping['clipSchedule']==T['clips']
for item,frame,src in zip(mapping['sourceToRenderFrames'],T['frames'],[m['reusedFrames'][0],m['frames'][0]]):
 assert item['primarySourceFrameId']==src['sourceFrameId'];assert item['renderFrameId']==frame['id'];assert item['atlasRect']==frame['sourceRect'];assert item['outputPNGsha256']==sha((P/item['outputPNG']).read_bytes())
for name in ['idle-blink.apng','yard-scale-blink.apng','Lesser-Goldfinch-Blink-Yard-Scale.gif']:
 im=Image.open(P/name);assert im.n_frames==3;dur=[];rgba=[]
 for k in range(3):im.seek(k);dur.append(im.info['duration']);rgba.append(im.convert('RGBA').tobytes())
 assert dur==[2000,100,900];assert rgba[0]==rgba[2] and rgba[0]!=rgba[1]
checks+=['exact30Hz 100ms closure and identical reused-open endpoint']
r={'passed':True,'checks':checks,'frameToActionMapBindingVerified':True,'newDrawings':1,'reusedDrawings':1,'newNeutralDrawings':0,'appBound':False,'SharpCanonicalAdmission':False,'scope':'integrity, immutable reuse, declared canvas conversion and technical contact/timing; normal-size semantic compatibility requires independent review'};(P/'verification.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
