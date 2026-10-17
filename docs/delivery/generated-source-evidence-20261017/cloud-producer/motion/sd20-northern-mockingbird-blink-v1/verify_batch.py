from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,struct
P=Path(__file__).parent;sha=lambda b:hashlib.sha256(b).hexdigest();fid=lambda im:'frame.sha256.'+sha(f'RGBA8;{im.width}x{im.height};'.encode()+im.tobytes());read=lambda n:json.loads((P/n).read_text());checks=[]
p=read('PRIMARY-SOURCE-MANIFEST.json');args=read('native-call-arguments.json')['arguments'];assert args['prompt'].encode()==(P/'prompt.txt').read_bytes();assert sha((P/'prompt.txt').read_bytes())==p['promptSHA256'];assert len(p['frames'])==1 and len(p['reusedFrames'])==1 and p['nativeCalls']==1;checks.append('Exact native prompt bytes/hash retained;1native call/1newclosure/1existingawake')
f=p['frames'][0];orig=Image.open(P/f['sourcePNG']).convert('RGBA');assert fid(orig)==f['sourceFrameId'];assert sha((P/f['sourcePNG']).read_bytes())==f['sourcePNGsha256']==p['originalSHA256'];reg=orig.resize((1024,1024),Image.Resampling.NEAREST);out=reg.resize((192,192),Image.Resampling.NEAREST);assert np.array_equal(np.array(reg),np.array(Image.open(P/f['registeredPNG']).convert('RGBA')));assert fid(out)==f['outputFrameId'];assert np.array_equal(np.array(out),np.array(Image.open(P/f['outputPNG']).convert('RGBA')));checks.append('Newnative1254²→1024²→192² exact whole-canvas nearest;zero translation,no per-posefit/sourcepaint')
r=p['reusedFrames'][0];ref=Path('/workspace/asset-production')/r['canonicalBankPath'];assert (P/r['sourcePNG']).read_bytes()==ref.read_bytes();op=Image.open(P/r['sourcePNG']).convert('RGBA');assert fid(op)==r['sourceFrameId'];assert (P/'open192.png').read_bytes()==(ref.parent/'neutral192.png').read_bytes();assert np.array_equal(np.array(op.resize((192,192),Image.Resampling.NEAREST)),np.array(Image.open(P/'open192.png').convert('RGBA')));checks.append('Existingawake1024source and192PNG reused byte-for-byte;no newneutral/look source')
m=read('texture-review-manifest.json');assert (P/'texture-review-manifest.json').stat().st_size<=65536 and (P/'blink-atlas192.png').stat().st_size<=4194304;atlas=Image.open(P/'blink-atlas192.png').convert('RGBA');assert atlas.size==(384,192);assert sha((P/'blink-atlas192.png').read_bytes())==m['source']['sha256'];assert m['profile']=='chirp-texture-review-v1' and m['activation']=='none' and m['scope']=='review-only' and m['approval']=='unreviewed'
for i,frame in enumerate(m['frames']):
 tile=atlas.crop((i*192,0,(i+1)*192,192));a=np.array(tile);assert np.array_equal(a,np.array(Image.open(P/(['open192.png','closed192.png'][i])).convert('RGBA')))
 for c in frame['contacts']:assert a[c['y'],c['x'],3]>0
 assert frame['sourcePixelsPerWorldUnit']==1.225;assert abs(frame['world']['width']*1.225-192)<1e-9
 for key in ['contacts','canvas','world','pivot','sourcePixelsPerWorldUnit']:assert frame[key]==m['frames'][0][key]
assert m['clips'][0]['tickRate']==30 and [x['durationTicks'] for x in m['clips'][0]['frames']]==[60,3,27];checks.append('Two-frame atlas exact;checked profile/budgets/density/samepositivecontacts subset;fullZod/Sharp admission pending')
w=read('frame-to-action-map.json');assert sha((P/w['atlas']['file']).read_bytes())==w['atlas']['sha256'];assert sha((P/w['manifest']['file']).read_bytes())==w['manifest']['sha256']
for record,source,render in zip(w['frames'],[r,f],m['frames']):
 assert record['sourceFrameId']==source['sourceFrameId'] and record['renderFrameId']==render['id'] and record['atlasRect']==render['sourceRect'];assert sha((P/record['outputPNG']).read_bytes())==record['outputPNGsha256']==source['outputPNGsha256']
assert [x['sourceFrameId'] for x in w['clip']['schedule']]==[r['sourceFrameId'],f['sourceFrameId'],r['sourceFrameId']];checks.append('Explicit filename/hash wrapper maps oldawake/newclosure primaryIDs→renderIDs/rects/PNGhashes and30Hzschedule')
b=(P/'blink.apng').read_bytes();pos=8;delays=[]
while pos<len(b):
 n=struct.unpack('>I',b[pos:pos+4])[0];kind=b[pos+4:pos+8];data=b[pos+8:pos+8+n]
 if kind==b'fcTL':delays.append(struct.unpack('>HH',data[20:24]))
 pos+=n+12
assert delays==[(60,30),(3,30),(27,30)];assert read('runtime-measurements.json')['footDiagnostics']['maximumGroundBoundaryChangeOutputPx']==0;checks.append('APNG exact30Hz phase timing;100ms closure;ground-boundary proxy unchanged,wholefoot approval explicitly absent')
report={'passed':True,'checks':checks,'scope':'Source/export/hash/contactgeometry/profile-subset checks,not semanticart acceptance,canonicalSharp admission or actual appyard binding.'};(P/'verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
