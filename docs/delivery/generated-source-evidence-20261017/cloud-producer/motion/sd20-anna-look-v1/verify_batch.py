"""Source, atlas, schedule and upstream checks; no canonical runtime admission."""
from pathlib import Path
from PIL import Image
import json, hashlib, struct, subprocess
P=Path(__file__).parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
J=lambda n:json.loads((P/n).read_text())
def rgba(n):
 im=Image.open(P/n);assert im.mode=='RGBA';return im
def fid(im):return 'frame.sha256.'+hashlib.sha256(f'RGBA8;{im.width}x{im.height};'.encode()+im.tobytes()).hexdigest()
m=J('PRIMARY-SOURCE-MANIFEST.json');r=J('call-receipt.json');a=J('frame-to-action-map.json');v=J('texture-review-manifest.json');h=J('behavior-handoff.json')
assert m['nativeCalls']==r['nativeCalls']==1 and len(m['frames'])==len(m['reusedFrames'])==1
assert m['lookOnlyNewDrawing'] and m['newNeutralDrawings']==m['newBlinkDrawings']==0
assert (P/'original.png').read_bytes()==(P/'look-native.png').read_bytes()
assert sha(P/'original.png')==m['originalSHA256']==r['originalSHA256']
assert sha(P/'prompt.txt')==m['promptSHA256']==r['promptSHA256']==J('prompt-byte-audit.json')['promptSHA256']
assert len((P/'prompt.txt').read_bytes())==2085 and not (P/'prompt.txt').read_bytes().endswith(b'\n')
assert J('prompt-byte-audit.json')['exactSubmittedStringCompared']
images=[]
for s in m['reusedFrames']+m['frames']:
 source=rgba(s['sourcePNG']);out=rgba(s['outputPNG']);images.append(out)
 assert fid(source)==s['sourceFrameId'] and sha(P/s['sourcePNG'])==s['sourcePNGsha256']
 assert sha(P/s['outputPNG'])==s['outputPNGsha256'] and out.size==(96,96)
 assert source.resize((96,96),Image.Resampling.NEAREST).tobytes()==out.tobytes()
assert rgba('look-native.png').size==(1254,1254) and rgba('reused-awake-source1024.png').size==(1024,1024)
assert m['reusedFrames'][0]['sourceFrameId']=='frame.sha256.96b2cbe379067cb25d7d33963ae49cd4ce3fc615de22999472b8476e6408ea28'
assert m['frames'][0]['sourceFrameId']=='frame.sha256.01966c2e6c4208a8f0c69c0bc36a4550fc1eef7884dd32535d8a9c1b39deb2e9'
atlas=rgba('look-atlas96.png');assert atlas.size==(192,96)
assert sha(P/a['atlasBinding']['file'])==a['atlasBinding']['sha256']==v['source']['sha256']
assert sha(P/a['manifest']['file'])==a['manifest']['sha256']
old=J('existing-awake-blink-manifest-reference.json')['frames'][1];assert old['id']=='anna-look-96'
retiled=json.loads(json.dumps(old));retiled['sourceRect']['x']=0;assert v['frames'][0]==retiled
assert len(v['frames'])==2 and len(a['sourceToRenderFrames'])==2
for i,(im,f,s,row) in enumerate(zip(images,v['frames'],m['reusedFrames']+m['frames'],a['sourceToRenderFrames'])):
 assert atlas.crop((96*i,0,96*i+96,96)).tobytes()==im.tobytes()
 for k in ['canvas','trim','pivot','world','sourcePixelsPerWorldUnit']:assert f[k]==old[k]
 assert row['primarySourceFrameId']==s['sourceFrameId'] and row['primarySourcePNG']==s['sourcePNG']
 assert row['primarySourcePNGsha256']==s['sourcePNGsha256'] and row['outputPNGsha256']==s['outputPNGsha256']
 assert row['renderFrameId']==f['id'] and row['atlasRect']==f['sourceRect'] and row['newDrawing']==bool(i)
 assert row['lookOnlyNewDrawing']==bool(i)
 for c in f['contacts']:assert im.getpixel((c['x'],c['y']))[3]>0
assert v['frames'][0]['contacts']==old['contacts'] and v['frames'][1]['contacts']==[]
assert [images[1].getpixel((c['x'],c['y']))[3] for c in old['contacts']]==[252,248]
assert v['approval']=='unreviewed' and v['activation']=='none' and v['profile']=='chirp-texture-review-v1'
idle,look=v['clips'];assert idle['id']=='idle' and idle['loop'] and len(idle['frames'])==1 and idle['frames'][0]['frameId']==old['id']
assert look['id']=='look' and not look['loop'] and look['tickRate']==30
assert [f['frameId'] for f in look['frames']]==[old['id'],v['frames'][1]['id'],old['id']]
assert [f['durationTicks'] for f in look['frames']]==[30,12,30] and a['clips']==v['clips']
assert a['renderClipId']=='look' and a['lookOnlyNewDrawing'] and a['canonicalSchemaValidation']=='NOT_RUN'
assert not h['packetBindingReady'] and not h['runtimePacketBindingReady'] and h['sourcePacketByteMappingVerified'] and h['activation']=='none'
for f in J('upstream-protection.json')['files']:assert sha(P.parents[1]/f['file'])==f['sha256']
q=P.parents[1]/'audits/phoebe-look-only-intake-extension-v1'
for ext in ['json','md']:assert (P/('canonical-admission-gap.'+ext)).read_bytes()==(q/('ADMISSION-GAP.'+ext)).read_bytes()
ap=Image.open(P/'look-preview.apng');assert ap.n_frames==3 and ap.info['loop']==1
durations=[]
for i,target in enumerate([images[0],images[1],images[0]]):
 ap.seek(i);assert ap.convert('RGBA').tobytes()==target.tobytes();durations.append(ap.info['duration'])
assert durations==[1000,400,1000]
gif=Image.open(P/'Anna-Look-Yard-Size.gif');assert gif.n_frames==3 and 'loop' not in gif.info
gd=[]
for i in range(3):gif.seek(i);gd.append(gif.info['duration'])
assert gd==[1000,400,1000]
js="""const assert=require('node:assert/strict'),{frameAt}=require('./player.js'),p=require('./texture-review-manifest.json');const [a,b]=p.frames;for(const [t,id]of [[0,a.id],[999,a.id],[1000,b.id],[1399,b.id],[1400,a.id],[2399,a.id],[2400,a.id],[50000,a.id]])assert.equal(frameAt(p,'look',t).frame.id,id);for(const t of [0,1000,40000])assert.equal(frameAt(p,'idle',t).frame.id,a.id);assert.equal(frameAt(p,'look',2400).terminal,true);for(const t of [-1,NaN,Infinity])assert.throws(()=>frameAt(p,'look',t));console.log('boundary, finalhold, idle, invalid-time checks passed');"""
node=subprocess.run(['node','-e',js],cwd=P,text=True,capture_output=True,check=True)
yard=Image.open(P/'look-yard64.apng');assert yard.size==(64,64) and yard.n_frames==3 and yard.info['loop']==1
for i,target in enumerate([images[0],images[1],images[0]]):
 yard.seek(i);assert yard.convert('RGBA').tobytes()==target.resize((64,64),Image.Resampling.NEAREST).tobytes();assert yard.info['duration']==[1000,400,1000][i]
result={'status':'PASS','newDrawings':1,'reusedDrawings':1,'newNeutralDrawings':0,'newBlinkDrawings':0,'sourceIDsVerified':True,'exactOldAwakeReuse':True,'wholeNativeCanvasNearestExportVerified':True,'alphaRGBAAtlasCropMappingVerified':True,'oldFootAlphaPositive':True,'newInheritedFootAlpha':[252,248],'newFrameContacts':[],'sharedContactCompatibility':'HELD','upstreamAnnaStandingFilesUnchanged':True,'exactSubmittedPromptBytesVerified':2085,'oneShotLookTicks':[30,12,30],'APNGDurationsMs':durations,'GIFDurationsMs':gd,'nodeTimingChecks':node.stdout.strip(),'canonicalZodValidation':'NOT_RUN','canonicalSharpValidation':'NOT_RUN','actualCurrentMacContract':'UNKNOWN','appBound':False,'packetBindingReady':False,'sourceArtAcceptance':'independent visual review pending; byte checks do not certify biology or smooth head turn'}
(P/'verification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
