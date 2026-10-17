"""Verify source-only checkpoint bytes and identities. Does not admit app assets."""
from pathlib import Path
import argparse,hashlib,json
from PIL import Image
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--root',type=Path,default=(Path(__file__).resolve().parent / '../..').resolve())
a=parser.parse_args();root=a.root
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
overlay=json.loads((root/'release/animation-checkpoint-1-20261017/intake-overlay.json').read_text())
files=0;frames=0;previews=0;ids=set()
for batch in overlay['batches']:
 p=root/batch['sourcePath']
 for filekey,hashkey in [('primaryManifest','primaryManifestSha256'),('original','originalSHA256'),('exactNativePrompt','exactNativePromptSHA256'),('review','reviewSHA256'),('sourceFileIndex','sourceFileIndexSHA256')]:
  assert sha(root/batch[filekey])==batch[hashkey],batch[filekey]
 index=json.loads((root/batch['sourceFileIndex']).read_text());items=index if isinstance(index,list) else index['files']
 if isinstance(items,dict):items=[dict(v,file=k) for k,v in items.items()]
 for f in items:
  path=p/f.get('file',f.get('path'));assert path.is_file() and path.stat().st_size==f['bytes'] and sha(path)==f['sha256'],str(path);files+=1
 j=json.loads((root/batch['primaryManifest']).read_text())
 assert j.get('nativeCalls',j.get('nativeGenerationCalls'))==1
 assert len(j['frames'])==batch['newDrawings']
 for f in j['frames']:
  path=p/f['sourcePNG'];assert sha(path)==f['sourcePNGsha256'];im=Image.open(path);assert im.mode=='RGBA';im.load()
  fid='frame.sha256.'+hashlib.sha256(f'RGBA8;{im.width}x{im.height};'.encode()+im.tobytes()).hexdigest()
  assert fid==f['sourceFrameId'] and fid not in ids;ids.add(fid);frames+=1
 for path in p.rglob('*'):
  if path.suffix.lower() not in ['.gif','.apng']:continue
  with Image.open(path) as im:
   assert im.n_frames>=2,str(path)
   for i in range(im.n_frames):im.seek(i);im.load();assert im.info.get('duration',0)>0,str(path)
  previews+=1
 assert set(batch['sourceFrameIds'])=={f['sourceFrameId'] for f in j['frames']}
assert frames==overlay['newDrawings'] and len(overlay['batches'])==overlay['newNativeCalls']
print(json.dumps({'passed':True,'nativeOriginals':len(overlay['batches']),'newPrimaryDrawingIDs':frames,'indexedBatchFiles':files,'decodedMultiFramePreviews':previews,'appAdmissionChecked':False,'artAnatomicalAcceptance':False}))
