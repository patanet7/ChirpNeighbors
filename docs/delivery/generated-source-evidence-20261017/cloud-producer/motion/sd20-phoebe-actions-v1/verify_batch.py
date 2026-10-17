from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,struct
P=Path(__file__).parent;sha=lambda b:hashlib.sha256(b).hexdigest();fid=lambda im:'frame.sha256.'+sha(f'RGBA8;{im.width}x{im.height};'.encode()+im.tobytes());checks=[]
line=json.loads((P/'source-lineage.json').read_text());raw=Image.open(P/'original.png').convert('RGBA');assert sha((P/'original.png').read_bytes())==line['nativeOriginalSha256'];assert raw.size==(2172,724);checks.append('Retained native original exact hash and dimensions')
for k,f in enumerate(line['frames']):
 native=Image.open(P/f['sourcePNG']).convert('RGBA');assert fid(native)==f['immutableSourceFrameId'];assert sha((P/f['sourcePNG']).read_bytes())==f['sourcePNGsha256']
 if k:assert np.array_equal(np.array(native),np.array(raw.crop(((k-1)*724,0,k*724,724))))
 reg=Image.open(P/f['registeredPNG']).convert('RGBA');out=Image.open(P/f['outputPNG']).convert('RGBA');assert np.array_equal(np.array(out),np.array(reg.resize((96,96),Image.Resampling.NEAREST)));assert sha((P/f['outputPNG']).read_bytes())==f['outputPNGsha256']
checks.append('All4 immutable source IDs verified;3native cells exact crops;4whole-canvas nearest exports exact')
for atlaspath,manifestpath in [('idle-atlas96.png','texture-review-manifest.json'),('blink-atlas96.png','blink-manifest.json')]:
 m=json.loads((P/manifestpath).read_text());assert m['profile']=='chirp-texture-review-v1';assert m['scope']=='review-only' and m['activation']=='none' and m['approval']=='unreviewed';atlas=Image.open(P/atlaspath).convert('RGBA');assert sha((P/atlaspath).read_bytes())==m['source']['sha256'];assert atlas.width<=1024 and atlas.height<=1024 and (P/atlaspath).stat().st_size<4194304;assert len((P/manifestpath).read_bytes())<=65536
 frames={f['id']:f for f in m['frames']};assert len(frames)==len(m['frames']);reference=m['frames'][0]
 for f in m['frames']:
  for prop in ['canvas','pivot','contacts','world','sourcePixelsPerWorldUnit']:assert f[prop]==reference[prop]
  assert abs(f['world']['width']*f['sourcePixelsPerWorldUnit']-96)<1e-8
  r=f['sourceRect'];tile=atlas.crop((r['x'],r['y'],r['x']+96,r['y']+96));a=np.array(tile)
  for c in f['contacts']:assert a[c['y'],c['x'],3]>0
  phase=f['id'][13:-3];assert np.array_equal(a,np.array(Image.open(P/'frames96'/(phase+'.png')).convert('RGBA')))
 for clip in m['clips']:
  assert clip['id']=='idle' and clip['tickRate']==30
  for step in clip['frames']:assert step['frameId'] in frames and 1<=step['durationTicks']<=300
checks.append('Two review-only intake manifests satisfy checked structural/scale/positive-contact/budget subset;fullZod/Sharp admission remains pending')
for name,expected in [('normal-speed.apng',[90,3,3,60,3,30]),('blink-normal-speed.apng',[90,3,90])]:
 p=(P/name).read_bytes();pos=8;delays=[]
 while pos<len(p):
  n=struct.unpack('>I',p[pos:pos+4])[0];kind=p[pos+4:pos+8];data=p[pos+8:pos+8+n]
  if kind==b'fcTL':delaynum,delayden=struct.unpack('>HH',data[20:24]);delays.append((delaynum,delayden))
  pos+=12+n
 assert delays==[(t,30) for t in expected];im=Image.open(P/name);assert im.n_frames==len(expected)
checks.append('APNG rational timing exact30Hz;6full-idle frames/3blink frames;noGIF timing substitution')
assert line['newDrawings']==3 and line['reusedDrawings']==1 and line['generationCalls']==1
checks.append('Counts remain3new drawings +1reused,1image call,0rigged frames;no full action set or app binding claim')
receipt={'passed':True,'checks':checks,'checkCount':len(checks),'verificationScope':'Local source/export/manifest-subset verification, not actual Mac validator,Sharp receipt or yard admission.'};(P/'verification.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
