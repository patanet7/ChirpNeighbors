from pathlib import Path
from PIL import Image
import json,hashlib,math
P=Path(__file__).parent
m=json.load(open(P/'PRIMARY-SOURCE-MANIFEST.json'));motion=json.load(open(P/'motion-manifest.json'));checks=[]
def check(name,condition):
 checks.append({'name':name,'passed':bool(condition)})
 if not condition:raise AssertionError(name)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
check('one native call',m['nativeCalls']==1)
check('four new primary drawings',len(m['frames'])==4)
check('four unique IDs',len({f['sourceFrameId'] for f in m['frames']})==4)
check('original hash',sha(P/m['original'])==m['originalSHA256'])
check('prompt hash',sha(P/m['prompt'])==m['promptSHA256'])
original=Image.open(P/'original.png');check('original full RGBA',original.mode=='RGBA');check('original alpha background',original.getextrema()[3][0]==0)
for f in m['frames']:
 im=Image.open(P/f['sourcePNG']);out=Image.open(P/f['outputPNG']);name=f['pose']
 expected='frame.sha256.'+hashlib.sha256(f'RGBA8;{im.width}x{im.height};'.encode()+im.tobytes()).hexdigest()
 check(name+' decoded identity',f['sourceFrameId']==expected)
 check(name+' source byte hash',sha(P/f['sourcePNG'])==f['sourcePNGsha256'])
 check(name+' output byte hash',sha(P/f['outputPNG'])==f['outputPNGsha256'])
 check(name+' source RGBA canvas',im.mode=='RGBA' and im.size==(1024,1024))
 check(name+' output RGBA canvas',out.mode=='RGBA' and out.size==(192,192))
 check(name+' common density',f['sourcePixelsPerWorldUnit']==1.4)
 check(name+' no per-pose rescale',f['registration']['perPoseScaleFit']==False)
 for c in f['supportContacts']:check(name+' positive alpha contact '+c['id'],out.getpixel((c['x'],c['y']))[3]>=128)
 if f['supportContacts']:check(name+' support plane anchored',f['lowestAlpha128WorldOffsetFromRoot']==0)
 else:check(name+' airborne feet above local plane',f['lowestAlpha128WorldOffsetFromRoot']<0)
check('61 distinct30Hz times',len(motion['ticks'])==61 and all(abs(t['timeSeconds']-t['tick']/30)<1e-9 for t in motion['ticks']))
check('grounded root no horizontal or vertical drift',all(t['rootWorld']==([0,0] if t['tick']<19 else [20,0]) for t in motion['ticks'] if t['grounded']))
check('only airborne root travels',all(not a['grounded'] or a['rootWorld']==b['rootWorld'] or not b['grounded'] for a,b in zip(motion['ticks'],motion['ticks'][1:])))
check('landing at exact20,0',motion['ticks'][27]['rootWorld']==[20,0] and motion['ticks'][27]['grounded'])
check('one-shot no silent loop',motion['loop'] is False)
check('no old neutral in action',all(t['pose']!='neutral' for t in motion['ticks']))
check('no actor binding claim',motion['runtimeBound']==False and motion['packetBindingReady']==False)
check('no canonicalSharp receipt invented',motion['canonicalSharpReceipt'] is None)
r=m['reusedFrames'][0];check('reused neutral immutable',sha(P/r['sourcePNG'])==r['sourcePNGsha256']);check('reused neutral not counted',r['newDrawing']==False)
with Image.open(P/'previews/pose-sequence.apng') as ap:check('APNG one-play and5heldposes',ap.n_frames==5 and ap.info.get('loop')==1)
with Image.open(P/'previews/pose-sequence.gif') as gif:check('GIF single play',gif.info.get('loop') is None)
receipt={'batchId':P.name,'status':'passed','checkCount':len(checks),'checks':checks,'limitations':'Source/export and declared-trajectory checks only. No semantic anatomical foot-lock proof, calibrated biomechanics, Mac app runtime or independent visual verdict.'}
(P/'receipts/verification.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({'status':'passed','checks':len(checks)}))
