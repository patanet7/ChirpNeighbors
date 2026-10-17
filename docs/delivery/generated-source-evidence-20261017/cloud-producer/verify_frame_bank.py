from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,datetime,sys
import PIL,scipy
R=Path(__file__).parent;bank=json.loads((R/'frame-bank.json').read_text());index={f['frameId']:f for f in bank['frames']};checks=[]
checks.append({'name':f'{len(bank["frames"])} distinct immutable frame IDs','passed':len(index)==len(bank['frames']) and bank.get('frameCount',len(index))==len(index)})
for frame in bank['frames']:
 im=Image.open(R/frame['file']).convert('RGBA');identity='frame.sha256.'+hashlib.sha256(f'RGBA8;{im.width}x{im.height};'.encode()+im.tobytes()).hexdigest();assert identity==frame['frameId'];assert hashlib.sha256((R/frame['file']).read_bytes()).hexdigest()==frame['fileSha256']
checks.append({'name':f'all{len(index)} file and decoded-pixel identities recompute','passed':True})
for sex in ['male','female']:
 for action in ['idle','feed']:
  p=R/'batches'/f'house-finch-{sex}-{action}-v1';m=json.loads((p/'manifest.json').read_text());source=np.array(Image.open(p/'original.png').convert('RGBA'));coverage=np.zeros(source.shape[:2],dtype=np.uint8)
  for e in m['frames']:
   f=index[e['frameId']];assert f['variant']=='adult-'+sex;pixels=np.array(Image.open(R/f['file']).convert('RGBA'));y,x=np.nonzero(pixels[:,:,3]>=2);dx,dy=f['derivation']['translation'];sx=x-dx;sy=y-dy;assert sx.min()>=0 and sy.min()>=0 and sx.max()<source.shape[1] and sy.max()<source.shape[0];assert np.array_equal(pixels[y,x],source[sy,sx]);coverage[sy,sx]+=1
   rev=Image.open(p/e['reviewPNG']).convert('RGBA');expected=Image.fromarray(pixels).resize((384,384),Image.Resampling.NEAREST);assert rev.tobytes()==expected.tobytes();assert f['originalCoreEdgeContacts']==0
  assert np.array_equal(coverage==1,source[:,:,3]>=2);assert coverage.max()==1;assert Image.open(p/'preview.apng').n_frames==6 and Image.open(p/'preview.gif').n_frames==6
  checks.append({'name':f'{sex}-{action}: inverse-translation restores every source alpha>=2 pixel exactly once; uniform384px derivation and six-frame previews verified','passed':True})
checks.append({'name':'no frame reuse or art acceptance falsely asserted','passed':bank['verifiedReuseCount']==0 and all(not f.get('acceptedUses') for f in bank['frames'])})
receipt={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'checks':checks,'passed':all(c['passed'] for c in checks),'versions':{'Python':sys.version.split()[0],'Pillow':PIL.__version__,'SciPy':scipy.__version__},'processingScriptSha256':hashlib.sha256((R/'package_finch.py').read_bytes()).hexdigest(),'artisticScaleContactAcceptance':False};(R/'receipts/house-finch-frame-bank-check.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2));assert receipt['passed']
