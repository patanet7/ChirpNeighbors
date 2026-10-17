"""Verify retained identities, real nearest exports, exact APNG timing and handoff facts."""
from pathlib import Path
from PIL import Image
import json, hashlib, struct, numpy as np
P=Path(__file__).parent;R=P.parent.parent
sha=lambda b:hashlib.sha256(b).hexdigest()
line=json.loads((P/'source-lineage.json').read_text());m=json.loads((P/'texture-review-manifest.json').read_text());v=json.loads((P/'runtime-measurements.json').read_text())
assert line['newDrawings']==0 and line['outputUniqueFrames']==3 and line['clipSteps']==5
assert m['profile']=='chirp-texture-review-v1' and m['approval']=='unreviewed' and m['activation']=='none'
assert m['source']['sha256']==sha((P/'blink-atlas96.png').read_bytes())
assert len((P/'texture-review-manifest.json').read_bytes())<=65536 and (P/'blink-atlas96.png').stat().st_size<=4194304
atlas=Image.open(P/'blink-atlas96.png').convert('RGBA');assert atlas.size==(288,96)
for i,(f,entry) in enumerate(zip(m['frames'],line['frames'])):
 src=Image.open(R/entry['sourcePNG']).convert('RGBA');out=Image.open(P/entry['outputPNG']).convert('RGBA')
 assert sha((R/entry['sourcePNG']).read_bytes())==entry['sourcePNGsha256']
 assert 'frame.sha256.'+sha(f'RGBA8;{src.width}x{src.height};'.encode()+src.tobytes())==entry['sourceFrameId']
 assert out.tobytes()==src.resize((96,96),Image.Resampling.NEAREST).tobytes()
 assert out.tobytes()==atlas.crop((96*i,0,96*(i+1),96)).tobytes()
 assert sha(out.tobytes())==entry['outputRGBAsha256'] and sha((P/entry['outputPNG']).read_bytes())==entry['outputPNGsha256']
 assert f['canvas']=={'width':96,'height':96} and f['pivot']=={'x':48,'y':75} and f['trim']=={'x':0,'y':0}
 assert f['sourcePixelsPerWorldUnit']==1 and f['world']=={'width':96,'height':96}
 for c in f['contacts']: assert out.getpixel((c['x'],c['y']))[3]>0
assert all(f['contacts']==m['frames'][0]['contacts'] for f in m['frames'])
clip=m['clips'][0];assert clip['tickRate']==30 and clip['loop'] and [s['durationTicks'] for s in clip['frames']]==[42,2,3,2,20]
assert clip['frames'][0]['frameId']==clip['frames'][-1]['frameId']
data=(P/'normal-speed.apng').read_bytes();p=8;delays=[]
while p<len(data):
 n=struct.unpack('>I',data[p:p+4])[0];kind=data[p+4:p+8];payload=data[p+8:p+8+n];p+=12+n
 if kind==b'fcTL': delays.append(struct.unpack('>IIIIIHHBB',payload)[5:7])
assert delays==[(42,30),(2,30),(3,30),(2,30),(20,30)]
with Image.open(P/'normal-speed.apng') as im:
 assert im.n_frames==5
 for k,idx in enumerate([0,1,2,1,0]):
  im.seek(k);assert im.convert('RGBA').tobytes()==atlas.crop((96*idx,0,96*(idx+1),96)).tobytes()
assert v['actualRasterAlpha128FootCore']['maxPerFootGroundBoundaryChangeOutputPx']==0
assert abs(v['projectedSourceFootHeuristic']['maxPairwiseOutputPx']-.29646353064078557)<1e-12
bank=json.loads((R/'frame-bank.json').read_text());assert len(bank['frames'])==64 and bank['verifiedReuseCount']==0
result={'passed':True,'checks':['3exact sourceRGBA/file identities','3whole-canvas nearest96 exports and atlas tiles','same canvas/pivot/world/density and positivealpha commoncontacts','strict30Hz5step timeline','5APNG decoded frames and exact rational tick delays','outputscaled contact metrics retained','64drawing bank and zero verifiedproductionreuse unchanged'],'fullZodSharpAdmission':'not executed here; canonical Mac validator required','qualityAcceptance':False,'normalYardIntegration':False,'newGenerationCalls':0}
(P/'verification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
