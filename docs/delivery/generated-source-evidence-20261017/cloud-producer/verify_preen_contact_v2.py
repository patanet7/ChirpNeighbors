"""Reproduce failed preservation control; checks prove evidence, never art approval."""
from pathlib import Path
from PIL import Image
import hashlib,json,numpy as np
R=Path(__file__).parent; B=R/'batches/house-finch-female-preen-contact-v2'
m=json.loads((B/'manifest.json').read_text()); q=json.loads((B/'quality-review.json').read_text());checks=[]
o=Image.open(B/'original.png').convert('RGBA'); ref=Image.open(B/'reference-neutral.png').convert('RGBA'); d=Image.open(B/'whole-canvas-diagnostic1024.png').convert('RGBA')
assert hashlib.sha256((B/'original.png').read_bytes()).hexdigest()==m['sourceOriginal']['sha256'];assert o.size==(1254,1254);checks.append('native original hash and failed1254 canvas retained')
assert ref.tobytes()==Image.open(R/'frames/7c12c45d8a8a6e64824669c595f4f58630aaa7a2eb6854ca76f5cd2311d2e6fe.png').convert('RGBA').tobytes();assert d.tobytes()==o.resize((1024,1024),Image.Resampling.NEAREST).tobytes();checks.append('neutral unchanged; diagnostic is exact whole-canvas resize without placement correction')
a=np.array(ref);b=np.array(d);ma=a[600:,:,3]>=128;mb=b[600:,:,3]>=128;inter=ma&mb;union=ma|mb
assert abs((inter.sum()/union.sum())-q['diagnosticOnly']['protectedLowerBodyMaskIoU'])<1e-12
mad=np.abs(a[600:,:,:3].astype(float)-b[600:,:,:3].astype(float))[inter].mean();assert abs(mad-q['diagnosticOnly']['visibleProtectedRGBMeanAbsoluteDifferenceByteValues'])<1e-12
exact=(a[600:]==b[600:]).all(axis=2);assert exact[inter].mean()==0 and exact[union].mean()==0;checks.append('protected maskIoU, visibleRGBMAD and zero exactvisibleRGBA recompute')
assert not any(q['proposedLocalTargetResults'].values());assert not m['review']['accepted'] and not m['integrated'] and not m['comparison']['isFinishedAnimation'];checks.append('all five failed targets and no full-animation acceptance explicit')
for name in ['comparison.gif','comparison.apng']:
 with Image.open(B/name) as im:
  assert im.n_frames==3
  for i in range(3):im.seek(i);im.load();assert im.info['duration']==800
checks.append('comparison-only GIF/APNG decode three800ms phases')
id='frame.sha256.'+hashlib.sha256(f'RGBA8;{o.width}x{o.height};'.encode()+o.tobytes()).hexdigest();assert id==m['frames'][0]['frameId'];bank=json.loads((R/'frame-bank.json').read_text());assert len(bank['frames'])==64 and sum(f['frameId']==id for f in bank['frames'])==1;checks.append('one native drawing has one immutable RGBA identity among64')
review=json.loads((B/'independent-review.json').read_text())
for name,h in review['inputFileHashes'].items():assert hashlib.sha256((B/name).read_bytes()).hexdigest()==h,name
checks.append('independent review inputs match current bytes')
out={'passed':True,'checksPassed':len(checks),'checks':checks,'nativeNewDrawings':1,'comparisonOnly':True,'allPreservationTargetsFail':True,'artAccepted':False,'runtimeIntegrationChecked':False};(B/'verification.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
