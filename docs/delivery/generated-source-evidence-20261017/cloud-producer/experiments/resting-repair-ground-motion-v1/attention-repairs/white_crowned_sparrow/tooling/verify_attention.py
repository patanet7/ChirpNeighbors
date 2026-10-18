from pathlib import Path
from PIL import Image
import json,hashlib,math,re,sys
P=Path(__file__).resolve().parent;p=P/sys.argv[1];sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();load=lambda n:json.loads((p/n).read_text());h=load('source-handoff.json');checks=[]
def check(label,passed):checks.append({'check':label,'pass':bool(passed)});assert passed,label
def fid(im):return 'frame.sha256.'+hashlib.sha256(f'RGBA8;{im.width}x{im.height};'.encode()+im.tobytes()).hexdigest()
a=load('native-call-arguments.json');d=load('call-dispatch-receipt.json');r=load('native-return-receipt.json');primary=load('PRIMARY-SOURCE-MANIFEST.json');mapping=load('frame-to-action-map.json');original=Image.open(p/'original.png').convert('RGBA')
check('one bounded native call/new drawing, no retries',r['nativeCalls']==r['actualNewDrawings']==h['newNativeCalls']==h['newDrawings']==1 and r['retries']==0 and not r['nativeRunning'])
check('one new source and two old exact source reuses',len(primary['frames'])==1 and len(primary['reusedFrames'])==2 and primary['newNeutral']==primary['newBlink']==0)
check('exact submitted prompt bytes/hash',a['arguments']['prompt'].encode()==(p/'prompt.txt').read_bytes() and len((p/'prompt.txt').read_bytes())==a['promptUTF8Bytes'] and sha(p/'prompt.txt')==d['promptSHA256']==a['promptSHA256']==primary['promptSHA256'])
check('arguments bound before dispatch',sha(p/'native-call-arguments.json')==d['argumentsSHA256'] and d['dispatchedUTC']<r['completedUTC'])
check('exact reference image and source identity',sha(p/'reference-awake-source1024.png')==a['referenceSHA256']==d['referenceSHA256'] and fid(Image.open(p/'reference-awake-source1024.png').convert('RGBA'))==a['referenceSourceId']==d['referenceSourceId'])
check('original retained PNG/RGBA identity',sha(p/'original.png')==r['originalSHA256']==primary['originalSHA256'] and fid(original)==r['sourceFrameId'])
check('model/seed unavailable and unguessed',a['model'] is None and a['seed'] is None and r['model'] is None and r['seed'] is None)
check('mapping manifest and atlas bindings',sha(p/'source-handoff.json')==mapping['manifest']['sha256'] and sha(p/'atlas.png')==mapping['atlas']['sha256']==h['atlas']['sha256'])
for frame in h['frames']:
 native=Image.open(p/frame['sourcePNG']).convert('RGBA');raw=Image.open(p/frame['rawPNG']).convert('RGBA');out=Image.open(p/frame['png']).convert('RGBA');check(frame['id']+' source identity/hash',fid(native)==frame['sourceFrameId'] and sha(p/frame['sourcePNG'])==frame['sourcePNGsha256']);check(frame['id']+' output identity/hash',fid(out)==frame['decodedRGBAId'] and sha(p/frame['png'])==frame['PNGsha256']);expected=[]
 for y in range(h['displayStage'][1]):
  for x in range(h['displayStage'][0]):
   sx=math.floor((x+.5)*native.width/h['fullWorldCanvas'][0]);sy=math.floor((y+.5)*native.height/h['fullWorldCanvas'][1]);expected.append(native.getpixel((sx,sy)) if sx<native.width and sy<native.height else (0,0,0,0))
 check(frame['id']+' exact whole-native sampler',list(raw.getdata())==expected)
 restored=Image.new('RGBA',tuple(h['displayStage']));restored.paste(out,tuple(h['commonCropOrigin']));check(frame['id']+' exact crop reconstruction/no nonzero discard',all((restored.getpixel((x,y))[3]==255)==(raw.getpixel((x,y))[3]>=128) for y in range(raw.height) for x in range(raw.width)))
 rect=frame['atlasRect'];atlas=Image.open(p/'atlas.png').convert('RGBA');check(frame['id']+' atlas exact RGBA',atlas.crop((rect['x'],rect['y'],rect['x']+rect['width'],rect['y']+rect['height'])).tobytes()==out.tobytes());check(frame['id']+' common canvas/root/contact scope',list(out.size)==h['candidateCanvas'] and frame['pivot']==h['candidatePivot'] and frame['contacts']==[] and frame['density']==1)
colors={v[:3] for f in h['frames'] for v in Image.open(p/f['png']).convert('RGBA').getdata() if v[3]};check('at most63 shared opaque colors',len(colors)<=63)
check('RGBA binary alpha/zero transparent RGB',all(v[3] in [0,255] and (v[3]!=0 or v==(0,0,0,0)) for f in h['frames'] for v in Image.open(p/f['png']).convert('RGBA').getdata()))
check('image-registration-only physical support unapproved',h['contacts']==[] and h['geometryScope']=='image-registration-only' and not h['physicalSupportReviewed'] and h['supportWorld'] is None and not h['runtimeAdmission'])
check('exact inherited blink timing',[s['durationTicks'] for s in h['clips'][1]['frames']]==[s['durationTicks'] for s in load('current-primary-manifest-reference.json')['clips'][0]['frames']])
for clip in h['clips'][1:]:
 ap=Image.open(p/f"{clip['id']}.apng");check(clip['id']+' APNG3 one-shot',ap.n_frames==3 and ap.info['loop']==1)
 for i,step in enumerate(clip['frames']):
  ap.seek(i);expected=Image.open(p/'frames'/f"{step['frameId']}.png").convert('RGBA');check(clip['id']+' exact APNG RGBA/delay '+str(i),ap.convert('RGBA').tobytes()==expected.tobytes() and abs(ap.info['duration']-step['durationTicks']*1000/30)<.001)
 check(clip['id']+' exact neutral entry/return',clip['frames'][0]['frameId']==clip['frames'][-1]['frameId']=='neutral')
findings=[]
for f in p.rglob('*'):
 if f.is_file() and f.suffix in ['.json','.md','.txt','.html','.js','.py']:
  text=f.read_text()
  if re.search('libfile_'+r'[0-9a-f]{32}|data:image/[^;]+;base64,|https?://[^\s\"<>]*(?:X-Amz-Signature|X-Goog-Signature|[?&]sig=)',text,re.I):findings.append(str(f.relative_to(p)))
check('publishable metadata no private handles/signed URLs/embedded captures',not findings)
(p/'verification.json').write_text(json.dumps({'status':'PASS source bytes, sampling, scope, APNG, clock and privacy only','checkCount':len(checks),'checks':checks,'findings':findings,'nativeCalls':1,'newDrawings':1,'sourceUsefulness':'UNKNOWN pending independent review','actualContractChecksOwner':'Corvid; NOT_RUN by this source verifier','runtimeAdmission':False},indent=2)+'\n');print(json.dumps({'species':sys.argv[1],'checks':len(checks),'status':'PASS'}))
