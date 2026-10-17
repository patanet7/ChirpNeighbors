from pathlib import Path
from PIL import Image
from scipy.ndimage import label,distance_transform_edt
import numpy as np,json,hashlib,struct
P=Path(__file__).parent;sha=lambda b:hashlib.sha256(b).hexdigest();fid=lambda im:'frame.sha256.'+sha(f'RGBA8;{im.width}x{im.height};'.encode()+im.tobytes());j=lambda n:json.loads((P/n).read_text());checks=[]
m=j('PRIMARY-SOURCE-MANIFEST.json');assert m['nativeCalls']==1 and len(m['frames'])==4 and len(m['reusedFrames'])==1;assert sha((P/m['original']).read_bytes())==m['originalSHA256'];assert sha((P/m['prompt']).read_bytes())==m['promptSHA256'];checks.append('One native call,4new source drawings,1neutral reuse;original/prompt SHA verified')
raw=np.array(Image.open(P/m['original']).convert('RGBA'));combined=np.zeros_like(raw);overlap=np.zeros(raw.shape[:2],int)
for f in m['frames']:
 im=Image.open(P/f['sourcePNG']).convert('RGBA');a=np.array(im);assert fid(im)==f['sourceFrameId'];assert sha((P/f['sourcePNG']).read_bytes())==f['sourcePNGsha256'];mask=a[:,:,3]>0;assert np.array_equal(a[mask],raw[mask]);combined[mask]=a[mask];overlap+=mask
 reg=f['registration'];assert abs(reg['callWideScale']-736/627)<1e-12 and not reg['perPoseScale'];scaled=im.resize((1472,1472),Image.Resampling.NEAREST);expected=Image.new('RGBA',(1024,1024));expected.paste(scaled,tuple(reg['placementFromScaledFullAtlas']));registered=Image.open(P/f['registeredPNG']).convert('RGBA');assert np.array_equal(np.array(expected),np.array(registered));assert reg['alpha128PixelsLostToCanvas']==0
 out=Image.open(P/f['outputPNG']).convert('RGBA');assert fid(out)==f['outputFrameId'];assert np.array_equal(np.array(out),np.array(expected.resize((96,96),Image.Resampling.NEAREST)));assert sha((P/f['outputPNG']).read_bytes())==f['outputPNGsha256']
assert np.array_equal(combined[raw[:,:,3]>0],raw[raw[:,:,3]>0]);assert overlap.max()==1;assert np.array_equal(overlap>0,raw[:,:,3]>0);checks.append('NativeRGBA extraction partitions every positive-alpha original pixel exactly once;cross-cell beak retained;all4sourceIDs valid')
r=m['reusedFrames'][0];im=Image.open(P/r['sourcePNG']).convert('RGBA');assert fid(im)==r['sourceFrameId'];assert sha((P/r['sourcePNG']).read_bytes())==r['sourcePNGsha256'];assert np.array_equal(np.array(im.resize((96,96),Image.Resampling.NEAREST)),np.array(Image.open(P/r['outputPNG']).convert('RGBA')));checks.append('One common new-pose scale1472/1254;integer placement only;all5whole-canvas96px exports exact')
motion=j('motion-manifest.json');samples=motion['trajectory']['samples'];assert len(samples)==29 and motion['tickRate']==30 and not motion['loop'];assert samples[0]['rootWorldXY']==[190,130] and samples[-1]['rootWorldXY']==[166,130]
for prev,cur in zip(samples,samples[1:]):
 if not(prev['planted']==False and cur['planted']==False):assert prev['rootWorldXY']==cur['rootWorldXY']
for s in samples:
 if s['planted']:assert s['supportBoundaryErrorWorldUnits']==0 and s['lowestToeBoundaryWorldY']==130
 else:assert s['toeClearanceWorldUnits']>0
for f in motion['frames']:
 a=np.array(Image.open(P/f['outputPNG']).convert('RGBA'))
 if f['footContactsState']=='planted':assert a[75,55,3]>=128 and np.where(a[:,:,3]>=128)[0].max()==75 and f['toeBoundarySupportAnchorOutputXY']==[55.5,76]
 else:assert f['toeBoundarySupportAnchorOutputXY'] is None
checks.append('29tick one-shot trajectory moves root onlybetween unplanted ticks;allgrounded root/contact boundaries stationary;landing plane error0inmodel;airborne toe clearancepositive')
for fname,n,expectedDelays in [('source-poses.apng',6,[6,3,4,4,3,9]),('traveled-once.apng',29,[1]*29)]:
 b=(P/fname).read_bytes();pos=8;ds=[];plays=None
 while pos<len(b):
  length=struct.unpack('>I',b[pos:pos+4])[0];kind=b[pos+4:pos+8];data=b[pos+8:pos+8+length]
  if kind==b'acTL':count,plays=struct.unpack('>II',data);assert count==n
  if kind==b'fcTL':ds.append(struct.unpack('>HH',data[20:24]))
  pos+=length+12
 assert ds==[(d,30) for d in expectedDelays] and plays==1
 with Image.open(P/fname) as im:assert im.n_frames==n
checks.append('BothAPNG previews exact rational30Hz and num_plays1;no seamless-reset loop or GIFtiming claim')
idle=j('neutral-idle-review-manifest.json');assert idle['profile']=='chirp-texture-review-v1' and idle['activation']=='none';assert sha((P/'neutral-idle96.png').read_bytes())==idle['source']['sha256'];assert len(idle['frames'])==1 and idle['clips'][0]['id']=='idle';checks.append('Staticneutral canonical-shapedreview packet retained;hopmotion customreview metadataisnotfakecanonicalclip/admission')
report={'passed':True,'checks':checks,'scope':'Source bytes/export geometry/contact-boundary model/timing checks. Not anatomical proof,continuous human review,canonical Sharp validation or actual app/yard binding.'};(P/'verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
