from pathlib import Path
from PIL import Image
import json,hashlib
P=Path(__file__).parent;m=json.loads((P/'family-source-manifest.json').read_text());ratio=112/96
for r in m['frames']:
 old=Image.open(P/r['legacy96PNG']).convert('RGBA');source=Image.open(P/r['sourcePNG']).convert('RGBA');runtime=Image.open(P/r['runtimePNG']).convert('RGBA');legacy=[('bill-region',[68,32]),('eye-region',[60,30])]if r['phase']=='look'else[('bill-region',[72,33]),('eye-region',[63,30])];rows=[]
 for label,p in legacy:
  q=[int(v*ratio+.5)for v in p];rows.append({'label':label,'legacy96Point':p,'source112Point':q,'legacyRGBA':list(old.getpixel(tuple(p))),'source112RGBA':list(source.getpixel(tuple(q))),'runtime112RGBA':list(runtime.getpixel(tuple(q))),'uncertaintyOutputPixelsAtLeast':1,'anatomicalEndpointCertified':False,'physicalContactApproved':False,'meaning':'manually inspected image region only; use technical overlay, not beak/eye target physics'})
 r['imageAnchorProxies']=rows;r['declaredRoot']={'point':[67,88],'source112RGBA':list(source.getpixel((67,88))),'meaning':'rounded abstract shared origin; may be transparent, not certified anatomical anchor/support'}
(P/'family-source-manifest.json').write_text(json.dumps(m,indent=2)+'\n')
