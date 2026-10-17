from pathlib import Path
from PIL import Image
import json,hashlib
P=Path(__file__).resolve().parent
def sha(b): return hashlib.sha256(b).hexdigest()
def fid(im):return 'frame.sha256.'+sha(f'RGBA8;{im.width}x{im.height};'.encode()+im.tobytes())
j=json.loads((P/'intake-manifest.json').read_text());bankPath=P.parent.parent/'frame-bank.json';bank=json.loads(bankPath.read_text())['frames'] if bankPath.exists() else [];checks=[]
def check(label,truth):
 assert truth,label
 checks.append(label)
check('Original source PNG hash matches retained generation',sha((P/'original.png').read_bytes())==j['originalSHA256'])
check('Exactly one call and three drawings; no animation overcount',j['nativeGenerationCalls']==1 and j['originalDrawings']==3 and j['newAnimationClips']==0)
ids=[]
for b in j['frames']:
 s=Image.open(P/b['sourcePNG']).convert('RGBA');o=Image.open(P/b['outputPNG']).convert('RGBA');ids.append(b['sourceFrameId'])
 check(b['id']+' source identity and bytes',fid(s)==b['sourceFrameId'] and sha((P/b['sourcePNG']).read_bytes())==b['sourcePNGsha256'])
 check(b['id']+' output exact nearest whole-canvas',s.resize((96,96),Image.Resampling.NEAREST).tobytes()==o.tobytes() and fid(o)==b['outputFrameRGBAId'])
 matches=[f for f in bank if f['frameId']==b['sourceFrameId']]
 check(b['id']+' no collision or exact own-batch registration',not matches or (len(matches)==1 and matches[0]['appearanceVersion']==j['batchId'] and matches[0]['fileSha256']==b['sourcePNGsha256']))
 m=json.loads((P/b['id']/'texture-review-manifest.json').read_text());f=m['frames'][0];d=f['sourcePixelsPerWorldUnit']
 check(b['id']+' contract scale and basic limits',.25<=d<=8 and abs(f['world']['width']*d-96)<1e-8 and abs(f['world']['height']*d-96)<1e-8 and len((P/b['outputPNG']).read_bytes())<4194304)
 check(b['id']+' contacts on positive-alpha toe pixels',all(o.getpixel((c['x'],c['y']))[3]>=128 for c in f['contacts']))
 check(b['id']+' transparent margin and source no clipping',s.getbbox()[0]>0 and s.getbbox()[1]>0 and s.getbbox()[2]<1024 and s.getbbox()[3]<1024)
 check(b['id']+' static hold and runtime authority honest',len(m['clips'][0]['frames'])==1 and m['clips'][0]['frames'][0]['durationTicks']==90 and not b['runtimeAdmission'] and not b['behaviorCoverage']['movement']['bound'] and not b['behaviorCoverage']['interaction']['bound'])
check('Three unique new source IDs',len(set(ids))==3)
result={'passed':True,'checksPassed':len(checks),'checks':checks,'fullCanonicalSharpValidatorExecuted':False,'limitations':['Local semantic/byte checks only; Mac existing intake must run its canonical Sharp builder and validator.','Contacts are manually selected positive-alpha toe-core pixels, not anatomical or physics approval.','No actual normal-yard actor playback or behavior binding performed.']}
(P/'verification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'passed':True,'checksPassed':len(checks)}))
