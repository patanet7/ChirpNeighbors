#!/usr/bin/env python3
"""Read-only PNG inspection. No image write, quantization, resizing or cleanup."""
import json, hashlib, time
from datetime import datetime, timezone
from pathlib import Path
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parent
started=datetime.now(timezone.utc).isoformat()
t0=time.monotonic()
manifest=json.loads((ROOT/'candidate-manifest.json').read_text())
result={'startedAt':started,'command':'python inspect_pack.py','images':[]}
for asset in manifest['assets']:
    p=ROOT/asset['file']; im=Image.open(p).convert('RGBA'); a=np.asarray(im)[:,:,3]
    pixels=np.asarray(im); visible=pixels[a>0,:3]
    colors=int(len(np.unique(visible,axis=0)))
    result['images'].append({'id':asset['id'],'sha256Matches':hashlib.sha256(p.read_bytes()).hexdigest()==asset['sha256'],'size':list(im.size),'strictBinaryAlpha':bool(np.all((a==0)|(a==255))),'partialAlphaPixels':int(np.sum((a>0)&(a<255))),'uniqueRGBColorsWhereAlphaNonzero':colors,'palette64Passed':colors<=64,'sourceUnchanged':True})

sa=np.asarray(Image.open(ROOT/'sources/tree-summer-v1.png'))
au=np.asarray(Image.open(ROOT/'sources/tree-autumn-v1.png'))
def roi_test(box):
    x0,y0,x1,y1=box
    a=sa[y0:y1,x0:x1,3]>=128;b=au[y0:y1,x0:x1,3]>=128
    coords=[]
    for v in (a,b):
        yy,xx=np.where(v); coords.append([int(xx.min()+x0),int(yy.min()+y0),int(xx.max()+x0+1),int(yy.max()+y0+1)])
    scores=[]
    for dy in range(-8,9):
      for dx in range(-8,9):
        shifted=np.zeros_like(b)
        ys=slice(max(0,dy),min(b.shape[0],b.shape[0]+dy));xs=slice(max(0,dx),min(b.shape[1],b.shape[1]+dx))
        sy=slice(max(0,-dy),min(b.shape[0],b.shape[0]-dy));sx=slice(max(0,-dx),min(b.shape[1],b.shape[1]-dx))
        shifted[ys,xs]=b[sy,sx]
        scores.append((float(np.logical_and(a,shifted).sum()/np.logical_or(a,shifted).sum()),dx,dy))
    best=max(scores)
    return {'sourcePixelROI':box,'threshold':128,'summerBBox':coords[0],'autumnBBox':coords[1],'unshiftedIoU':float(np.logical_and(a,b).sum()/np.logical_or(a,b).sum()),'bestMaskTranslationWithin8px':{'dx':best[1],'dy':best[2],'IoU':best[0]},'interpretation':'Diagnostic silhouette comparison only; not landmark or contact approval.'}
result['treeRegistration']={
 'sameCanvas':sa.shape==au.shape,
 'rescaleApplied':False,
 'trunkAndRootROI':roi_test([300,990,900,1330]),
 'rootContactROI':roi_test([300,1180,900,1330]),
 'majorBranches':'Visual review: topology and principal forks remain similar. Exact branch landmarks have not been traced or approved; leaf-color changes prevent whole-image RGB matching from proving geometry.',
 'occupiedPerchAnchors':[],
 'occupiedPerchAnchorsStatus':'None defined in these generic foliage candidates. No existing runtime tree perch contacts supplied; do not invent them.',
 'pivotStatus':'Shared source pivot proposal [620,1295], pending local root/ground review.',
 'acceptance':'Unapproved pending pivot, trunk/branch, alpha and display-size checks. Foliage silhouette differences alone are not a rejection criterion.'}
result['elapsedSeconds']=round(time.monotonic()-t0,3)
result['exitStatus']=0
(ROOT/'reports/pack-inspection.json').write_text(json.dumps(result,indent=2)+'\n')
with (ROOT/'execution-ledger.jsonl').open('a') as f:f.write(json.dumps({'timestamp':started,'command':'python inspect_pack.py','inputs':[a['file'] for a in manifest['assets']],'outputs':['reports/pack-inspection.json'],'elapsedSeconds':result['elapsedSeconds'],'exitStatus':0,'state':'source-byte-and-alpha-validation-complete; runtime-approval-pending'})+'\n')
print(json.dumps(result,indent=2))
