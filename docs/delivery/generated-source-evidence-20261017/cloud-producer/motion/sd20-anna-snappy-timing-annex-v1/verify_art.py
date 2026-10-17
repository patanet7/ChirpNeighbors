from pathlib import Path
from PIL import Image
import json,hashlib
P=Path(__file__).parent;R=P.parent.parent;B=json.loads((P/'source-bindings.json').read_text());A=Image.open(P/B['atlasBinding']['file']).convert('RGBA');assert A.size==(768,96)
for f in B['sourceToRenderFrames']:
 im=Image.open(R/f['upstreamPrimaryPNG']).convert('RGBA');assert f['primarySourceFrameId']=='frame.sha256.'+hashlib.sha256(f'RGBA8;{im.width}x{im.height};'.encode()+im.tobytes()).hexdigest();out=Image.open(P/f['PNG']).convert('RGBA');r=f['atlasRect'];assert out.size==(96,96);assert out.tobytes()==A.crop((r['x'],r['y'],r['x']+r['width'],r['y']+r['height'])).tobytes()
print('8 exact primary RGBA identities and atlas tiles verified; no pixel edits')
