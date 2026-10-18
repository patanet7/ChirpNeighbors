"""Strict registration-only provenance verification; no action/runtime admission."""
from pathlib import Path
import hashlib,json,argparse
from PIL import Image

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text())
def inside(root,rel):
 p=(root/rel).resolve();assert p.is_relative_to(root.resolve()) and not Path(rel).is_absolute(),rel;return p

def verify(root):
 j=load(root/'source-registration-stage53.json');assert j['nativeOriginals']==11 and j['newNativeDrawings']==19 and j['registeredDrawings']==169 and j['registeredOriginals']==61
 for rel,h in j['frozenSourceGuards'].items():assert sha(inside(root,rel))==h,rel
 for freeze in j['frozenPackages']:
  p=inside(root,freeze['sourcePath']);ix=load(p/freeze['index']);items=ix if isinstance(ix,list) else ix.get('files',ix)
  if isinstance(items,dict):items=[{'file':k,**(v if isinstance(v,dict) else {'sha256':v})} for k,v in items.items()]
  for f in items:
   q=inside(p,f.get('file',f.get('path')));assert sha(q)==f['sha256'],str(q)
   if 'bytes' in f:assert q.stat().st_size==f['bytes'],str(q)
 ids=set();originals=set();count=0
 for b in j['registrationOnlyBatches']:
  assert b['registrationOnly'] is True and b['runtimeAdmission'] is False and b['acceptedUses']==[]
  op=inside(root,b['original']);assert sha(op)==b['originalSHA256'];originals.add(b['original'])
  prompt=inside(root,b['prompt']).read_bytes();assert hashlib.sha256(prompt).hexdigest()==b['promptSHA256'] and len(prompt)==b['promptBytes']
  args=load(inside(root,b['nativeArguments']));assert args['arguments']['prompt'].encode()==prompt
  dispatch=load(inside(root,b['dispatchReceipt']));ret=load(inside(root,b['returnReceipt']))
  if b['sourcePath']=='motion/sd20-mourning-dove-airborne-singlepose-v1/upstroke':
   # PREPARED proves authorization only. Affirmative return evidence is separate.
   assert dispatch.get('status')=='DISPATCH_PREPARED_ONE_AUTHORIZED_NATIVE_CALL' and dispatch.get('nativeCallsAuthorized')==1 and dispatch.get('newDrawingTarget')==1
   assert ret.get('state')=='RETURNED_ONE_NATIVE_CALL' and ret.get('nativeCalls')==1 and ret.get('actualNewDrawings')==1 and ret.get('nativeRunning') is False
   assert len(b['frames'])==1 and ret.get('sourceFrameId')==b['frames'][0]['sourceFrameId'] and ret.get('originalSHA256')==b['originalSHA256']
  else:
   assert any(dispatch.get(k)==1 for k in ['callsDispatched','nativeCalls','nativeCallsDispatched'])
  assert dispatch['promptSHA256']==b['promptSHA256']
  if 'promptBytes' in dispatch:assert dispatch['promptBytes']==len(prompt)
  for key in ['nativeArgsSHA256','nativeArgumentsSHA256','preparedArgsSHA256']:
   if key in dispatch:assert dispatch[key]==sha(inside(root,b['dispatchArguments'])),b['original']
  assert ret['nativeCalls']==1 and ret['originalSHA256']==b['originalSHA256']
  if 'nativeRunning' in ret:assert ret['nativeRunning'] in [0,False]
  assert len(b['frames'])==b['newDrawings']
  with Image.open(op) as oi:
   orig=oi.convert('RGBA');assert list(orig.size)==b['originalDimensions']
   for f in b['frames']:
    p=inside(root,f['sourcePNG']);assert sha(p)==f['sourcePNGsha256']
    with Image.open(p) as si:im=si.convert('RGBA');assert si.mode=='RGBA'
    fid='frame.sha256.'+hashlib.sha256(f'RGBA8;{im.width}x{im.height};'.encode()+im.tobytes()).hexdigest()
    assert fid==f['sourceFrameId'] and fid not in ids;ids.add(fid);count+=1
    r=f['nativeSourceRect'];assert orig.crop((r[0],r[1],r[0]+r[2],r[1]+r[3])).tobytes()==im.tobytes()
    assert list(im.size)==r[2:] and f['derivativeIsNewDrawing'] is False
 assert len(originals)==11 and count==19
 bank=load(root/'frame-bank.json');assert len(bank['frames'])==169 and len({f['frameId'] for f in bank['frames']})==169
 assert {f['frameId'] for f in bank['frames'][150:]}==ids and all(f['acceptedUses']==[] for f in bank['frames'])
 assert bank['frames'][150:]==j['appendedBankRecords']
 inv=load(root/'original-source-inventory.json');assert len(inv['originals'])==61 and len({r['file'] for r in inv['originals']})==61
 assert {r['file'] for r in inv['originals'][-11:]}==originals
 fmap=load(root/'source-frame-map.json');assert len(fmap['frames'])==169 and {r['sourceFrameId'] for r in fmap['frames']}=={f['frameId'] for f in bank['frames']}
 for f,m in zip(bank['frames'],fmap['frames']):
  assert m['sourceFrameId']==f['frameId'] and m['sourcePNG']==f['file'] and m['sourcePNGsha256']==f['fileSha256']
 for p,h in j['bindingSnapshotHashes'].items():assert sha(inside(root,p))==h,p
 overlay=load(root/'release/animation-checkpoint-1-20261017/intake-overlay.json')
 assert overlay['registrationOnlyBatches']==j['registrationOnlyBatches'] and overlay['registeredDrawings']==169 and overlay['registeredOriginals']==61
 return {'passed':True,'registrationOnlyNativeOriginals':11,'registrationOnlyNativeDrawings':19,'totalBankDrawingIDs':169,'totalOriginalPromptPairs':61,'bindingFilesByteIdentical':len(j['bindingSnapshotHashes']),'runtimeAdmission':False,'acceptedHopSlotsAdded':0,'acceptedBathingSlotsAdded':0}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=Path(__file__).parent);a=p.parse_args();print(json.dumps(verify(a.root)))
