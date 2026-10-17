"""Meaningful exact-source/derivation/timing checks; never anatomy acceptance."""
from pathlib import Path
from PIL import Image
import json,hashlib,numpy as np
R=Path(__file__).parent;P=R/'batches/house-finch-female-preen-v1';m=json.loads((P/'manifest.json').read_text());bank=json.loads((R/'frame-bank.json').read_text());idx={x['frameId']:x for x in bank['frames']};original=Image.open(P/'original.png').convert('RGBA');checks=[]
assert hashlib.sha256((P/'original.png').read_bytes()).hexdigest()==m['sourceOriginal']['sha256'];checks.append('original and prompt retained')
frames=[]
for i,e in enumerate(m['rawSourceFrames']):
 f=idx[e['frameId']];raw=Image.open(R/f['file']).convert('RGBA');x,y,w,h=f['sourceRect'];assert raw.tobytes()==original.crop((x,y,x+w,y+h)).tobytes();assert hashlib.sha256((R/f['file']).read_bytes()).hexdigest()==f['fileSha256'];assert 'frame.sha256.'+hashlib.sha256(f'RGBA8;{raw.width}x{raw.height};'.encode()+raw.tobytes()).hexdigest()==f['frameId']
 t=e['sourceToDiagnostic'];out=Image.new('RGBA',(1024,1024));out.paste(raw.resize((572,572),Image.Resampling.NEAREST),tuple(t['integerTranslation']));saved=Image.open(P/t['file']).convert('RGBA');assert saved.tobytes()==out.tobytes();review=Image.open(P/e['reviewPNG']).convert('RGBA');assert review.tobytes()==out.resize((384,384),Image.Resampling.NEAREST).tobytes();frames.append(f['frameId'])
assert len(set(frames))==6;checks.extend(['six unique immutable source frames exactly reconstruct original cells','all six use the same scale with explicit integer registration, no part warp','all384px review derivatives reproduce exactly'])
assert m['frames'][0]['frameId']==m['frames'][-1]['frameId'];assert not m['transitionsVerified'];assert not m['review']['accepted'];assert not m['integrated'];assert len(m['events'])==0;checks.append('existing neutral use and unaccepted transition/contact status explicit')
for name,n in [('preview.gif',8),('preview.apng',8),('raw-cell-preview.gif',6),('raw-cell-preview.apng',6)]:
 with Image.open(P/name) as im:
  assert im.n_frames==n
  for i in range(n):im.seek(i);im.load()
checks.append('raw6 and registered8 APNG/GIF frames decode')
qa=json.loads((P/'quality-review.json').read_text());assert not any(qa['localTargetResults'].values());checks.append('failed geometric/transition targets retained instead of acceptance')
receipt={'checksPassed':len(checks),'checks':checks,'sourceDrawings':6,'registeredPreviewFrames':8,'rawPreviewFrames':6,'artScaleContactAcceptance':False,'appPlaybackTested':False,'passed':True}
(P/'verification.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
