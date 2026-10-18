"""Strict registration-only provenance verification; no action/runtime admission."""
from pathlib import Path
import hashlib,json,argparse
from PIL import Image

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text())
def inside(root,rel):
 p=(root/rel).resolve();assert p.is_relative_to(root.resolve()) and not Path(rel).is_absolute(),rel;return p

def verify(root):
 j=load(root/'source-registration-stage57.json');assert j['nativeOriginals']==12 and j['newNativeDrawings']==20 and j['registeredDrawings']==170 and j['registeredOriginals']==62
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
  args=load(inside(root,b['nativeArguments']));assert (args['prompt'] if b.get('receiptVariant')=='oriole-reference-edit-flat-v1' else args['arguments']['prompt']).encode()==prompt
  dispatch=load(inside(root,b['dispatchReceipt']));ret=load(inside(root,b['returnReceipt']))
  experimental=b.get('receiptVariant')=='oriole-reference-edit-flat-v1'
  if experimental:
   assert b['original']=='experiments/oriole-blink-method-comparison-v1/native-edit/original.png' and b['originalSHA256']=='1a48eb61dd59447cb41b9c399af2e581ceb836279f9e430cb5f4af461e35c95c'
   assert len(b['frames'])==1 and b['frames'][0]['sourceFrameId']=='frame.sha256.1a33a90a427d053b31bf2528bd025f2e20cdbcee13799e312a84e7347a8b1f0c'
   assert b['promptBytes']==2313 and b['promptSHA256']=='eec04f32f21e47e8abeb3056742814f79197916898899cfc51caa5c3d3ea5b93' and not prompt.endswith(b'\n')
   assert sha(inside(root,b['nativeArguments']))=='51a1252749f7cc4c134b89917742aa859235123d40efc77675d435618bc798cc'
   assert args.get('transparent_background') is True and args.get('referenced_image_paths')==[b['savedReferenceArgument']]
   # Prepared metadata is not dispatch proof; the exact completed-call receipt below is authoritative.
   assert dispatch.get('nativeCallOrdinal')==1 and dispatch.get('nativeCallLimit')==1 and dispatch.get('automaticRetries')==0
   assert sha(inside(root,b['returnReceipt']))=='3ef3d6e73023b160efe76e67ed7c3ea15e8656ba6f1282275de7709f2ab0c1ef'
   assert ret.get('nativeCallsStarted')==1 and ret.get('nativeCallsReturned')==1 and ret.get('automaticRetries')==0
   assert ret.get('state')=='one-native-call-completed-source-candidate-unreviewed' and ret.get('originalPNGsha256')==b['originalSHA256'] and ret.get('sourceFrameId')==b['frames'][0]['sourceFrameId']
   assert ret.get('originalByteEqualToolSavedFile') is True and ret.get('originalAltered') is False and ret.get('postprocessingPerformed') is False and ret.get('sourceCanvas')==[1254,1254]
   from datetime import datetime
   dt=lambda x:datetime.fromisoformat(x.replace('Z','+00:00'))
   started=dt(ret['actualToolInvokedUTC']);returned=dt(ret['actualToolReturnUTC']);assert started>dt(ret['dispatchPreparedUTC']) and returned>started and round((returned-started).total_seconds()*1000)==ret['measuredToolAwaitMilliseconds']
   assert ret['promptSHA256']==b['promptSHA256'] and ret['promptBytes']==len(prompt) and ret['promptExactToNativeArguments'] is True
   assert ret['nativeArgumentsSHA256']==sha(inside(root,b['nativeArguments'])) and dispatch['nativeArgumentsSHA256']==ret['nativeArgumentsSHA256']
   assert b['referenceSourceFrameId']=='frame.sha256.b7741c8ea9988ac8cb6f8faf36563af4a4fb67a94a5c5ebc2fa50567517e781f'
   assert b['referencePNGsha256']=='ae4323d2f7bc9434df6c469867b728a2be5b901381e0798d833c5442db768749'
   assert ret['referenceSourceFrameId']==dispatch['referenceSourceId']==b['referenceSourceFrameId'] and ret['referencePNGsha256']==dispatch['referencePNGsha256']==b['referencePNGsha256']
   assert sha(inside(root,b['referenceCopy']))==b['referencePNGsha256']
   bankNow=load(root/'frame-bank.json');reference=next(f for f in bankNow['frames'] if f['frameId']==b['referenceSourceFrameId']);assert sha(inside(root,reference['file']))==reference['fileSha256']==b['referencePNGsha256']
   failure=load(inside(root,b['preCallError']));assert failure['nativeImageCallsInFailedExec']==0 and failure['nativeToolInvokedByFailedExec'] is False
  elif b['sourcePath']=='motion/sd20-mourning-dove-airborne-singlepose-v1/upstroke':
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
  if not experimental:assert ret['nativeCalls']==1 and ret['originalSHA256']==b['originalSHA256']
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
 assert len(originals)==12 and count==20
 bank=load(root/'frame-bank.json');assert len(bank['frames'])==170 and len({f['frameId'] for f in bank['frames']})==170
 assert {f['frameId'] for f in bank['frames'][150:]}==ids and all(f['acceptedUses']==[] for f in bank['frames'])
 assert bank['frames'][150:]==j['appendedBankRecords']
 inv=load(root/'original-source-inventory.json');assert len(inv['originals'])==62 and len({r['file'] for r in inv['originals']})==62
 assert {r['file'] for r in inv['originals'][-12:]}==originals
 fmap=load(root/'source-frame-map.json');assert len(fmap['frames'])==170 and {r['sourceFrameId'] for r in fmap['frames']}=={f['frameId'] for f in bank['frames']}
 for f,m in zip(bank['frames'],fmap['frames']):
  assert m['sourceFrameId']==f['frameId'] and m['sourcePNG']==f['file'] and m['sourcePNGsha256']==f['fileSha256']
 for p,h in j['bindingSnapshotHashes'].items():assert sha(inside(root,p))==h,p
 overlay=load(root/'release/animation-checkpoint-1-20261017/intake-overlay.json')
 assert overlay['registrationOnlyBatches']==j['registrationOnlyBatches'] and overlay['registeredDrawings']==170 and overlay['registeredOriginals']==62
 return {'passed':True,'registrationOnlyNativeOriginals':12,'registrationOnlyNativeDrawings':20,'totalBankDrawingIDs':170,'totalOriginalPromptPairs':62,'bindingFilesByteIdentical':len(j['bindingSnapshotHashes']),'runtimeAdmission':False,'acceptedHopSlotsAdded':0,'acceptedBathingSlotsAdded':0}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=Path(__file__).parent);a=p.parse_args();print(json.dumps(verify(a.root)))
