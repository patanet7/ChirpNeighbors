from pathlib import Path
from PIL import Image
import json,hashlib
P=Path(__file__).resolve().parent
def sha(b):return hashlib.sha256(b).hexdigest()
def fid(im):return 'frame.sha256.'+sha(f'RGBA8;{im.width}x{im.height};'.encode()+im.tobytes())
j=json.loads((P/'intake-manifest.json').read_text());bank=(P/'prebatch-source-ids.json').read_text();checks=[];ids=[]
def check(label,v):
 assert v,label
 checks.append(label)
check('Original native PNG retained byte identity',sha((P/'original.png').read_bytes())==j['originalSHA256'])
check('Exactly one native call, six drawings and three proposed source loops',j['nativeGenerationCalls']==1 and j['originalDrawings']==6 and j['proposedIdleLookClips']==3)
for b in j['species']:
 edge=b['outputCanvas'][0];d=b['proposedDensity'];outs=[]
 for f in b['frames']:
  s=Image.open(P/f['sourcePNG']).convert('RGBA');o=Image.open(P/f['outputPNG']).convert('RGBA');outs.append(o);ids.append(f['sourceFrameId'])
  check(b['id']+' '+f['pose']+' source identity',fid(s)==f['sourceFrameId'] and sha((P/f['sourcePNG']).read_bytes())==f['sourcePNGsha256'])
  check(b['id']+' '+f['pose']+' exact nearest RGBA export',s.resize((edge,edge),Image.Resampling.NEAREST).tobytes()==o.tobytes() and fid(o)==f['outputRGBAId'] and sha((P/f['outputPNG']).read_bytes())==f['outputPNGsha256'])
  check(b['id']+' '+f['pose']+' source margin/no clipping',s.getbbox()[0]>0 and s.getbbox()[1]>0 and s.getbbox()[2]<1024 and s.getbbox()[3]<1024)
  check(b['id']+' '+f['pose']+' not duplicate bank ID',f['sourceFrameId'] not in bank)
 m=json.loads((P/b['id']/'texture-review-manifest.json').read_text());atlas=Image.open(P/b['atlasPNG']).convert('RGBA')
 check(b['id']+' atlas/source SHA and slots',m['source']['sha256']==sha((P/b['atlasPNG']).read_bytes()) and atlas.size==(edge*2,edge) and all(atlas.crop((i*edge,0,(i+1)*edge,edge)).tobytes()==q.tobytes() for i,q in enumerate(outs)))
 check(b['id']+' contract limits/density',edge<=512 and edge*2<=1024 and .25<=d<=8 and all(abs(f['world']['width']*d-edge)<1e-8 and abs(f['world']['height']*d-edge)<1e-8 for f in m['frames']) and (P/b['atlasPNG']).stat().st_size<4194304)
 check(b['id']+' stable pivot/scale/contacts across poses',m['frames'][0]['pivot']==m['frames'][1]['pivot'] and m['frames'][0]['contacts']==m['frames'][1]['contacts'] and m['frames'][0]['sourcePixelsPerWorldUnit']==m['frames'][1]['sourcePixelsPerWorldUnit'])
 check(b['id']+' actual positive-alpha foot contacts',all(q.getpixel((c['x'],c['y']))[3]>=128 for q in outs for c in b['contacts']))
 apng=Image.open(P/b['id']/'idle-look.apng');dur=[]
 for k in range(apng.n_frames):apng.seek(k);dur.append(apng.info['duration'])
 check(b['id']+' actual APNG timing and endpoint',apng.n_frames==3 and dur==[2000.,b['timing']['alternateHoldMs'],1000.-b['timing']['alternateHoldMs']] and sum(x['durationTicks'] for x in m['clips'][0]['frames'])==90 and m['clips'][0]['tickRate']==30)
 apng.seek(0);first=apng.convert('RGBA').tobytes();apng.seek(2);check(b['id']+' loop endpoint exact existing neutral',first==apng.convert('RGBA').tobytes())
 check(b['id']+' no behavior binding claim',not b['runtimeAdmission'] and all(not c['runtimeBound'] and not c['normalYardVisuallyVerified'] for c in b['behaviorCoverage'].values()))
check('Six unique new source IDs',len(ids)==6 and len(set(ids))==6)
wood=j['species'][0]
check('Nuttall scale explicitly height',wood['scaleAxis']=='height' and wood['targetMeasure']=='visible-height' and abs(wood['visibleWorldUnits'][0][1]-58)<1e-9 and 'targetLength' not in wood)
check('Nuttall tail-plane support failure retained',not wood['packetBindingReady'] and not wood['supportMetrics']['physicalPlanarTailBraceApproved'] and all(p['tailToToePlaneGapWorldUnits']>13 for p in wood['supportMetrics']['poses']))
check('Other two packets review-eligible without binding claim',all(b['packetBindingReady'] and not b['runtimeAdmission'] for b in j['species'][1:]))

result={'passed':True,'checksPassed':len(checks),'checks':checks,'canonicalMacSharpValidatorRun':False,'limitations':['Local byte, semantic and contract-shape checks; no Zod/Sharp receipt fabricated.','Owner-specific approval and actual normal-yard admission remain pending.']}
(P/'verification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'passed':True,'checksPassed':len(checks)}))
