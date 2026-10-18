from pathlib import Path
from PIL import Image
import json,hashlib,re,math
P=Path(__file__).resolve().parent; R=P.parent.parent
checks=[]
def load(n):return json.loads((P/n).read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def check(label,passed):
 checks.append({'check':label,'pass':bool(passed)})
 assert passed,label
def rgba(n):return Image.open(P/n).convert('RGBA')
def fid(im):return 'frame.sha256.'+hashlib.sha256(f'RGBA8;{im.width}x{im.height};'.encode()+im.tobytes()).hexdigest()
a=load('native-call-arguments.json');d=load('call-dispatch-receipt.json');r=load('native-return-receipt.json');p=load('PRIMARY-SOURCE-MANIFEST.json');m=load('texture-review-manifest.json');mp=load('frame-to-action-map.json');rounding=load('density-pivot-rounding.json')['candidate']
check('one actual call, one new drawing, no retries/running',p['nativeCalls']==r['nativeCalls']==r['actualNewDrawings']==1 and not r['nativeRunning'] and r['retries']==0)
check('one new primary and one exact reused source',len(p['frames'])==len(p['reusedFrames'])==1 and p['frames'][0]['newDrawing'] and not p['reusedFrames'][0]['newDrawing'])
check('no new neutral or blink',r['newNeutral']==r['newBlink']==d['newNeutral']==d['newBlink']==0)
check('dispatch timestamp precedes return',d['startedUTC']<r['completedUTC'])
check('submitted prompt exact retained bytes',a['arguments']['prompt'].encode()==(P/'prompt.txt').read_bytes())
check('prompt bytes and hashes bound',len((P/'prompt.txt').read_bytes())==a['promptUTF8Bytes']==d['promptBytes']==2909 and sha(P/'prompt.txt')==p['promptSHA256']==d['promptSHA256']==a['promptSHA256'])
check('dispatch args hash exact',sha(P/'native-call-arguments.json')==d['nativeArgsSHA256'])
check('exact inspected awake sole reference',a['arguments']['referenced_image_paths']==[str(P/'reference-awake-source1024.png')] and a['arguments']['transparent_background'] is True)
check('raw original source size and bytes',rgba('original.png').size==(1254,1254) and sha(P/'original.png')==r['originalSHA256']==p['originalSHA256'])
for rec in p['frames']+p['reusedFrames']:
 im=rgba(rec['sourcePNG']);out=rgba(rec['outputPNG'])
 check(rec['pose']+' source bytes',sha(P/rec['sourcePNG'])==rec['sourcePNGsha256'])
 check(rec['pose']+' standard decoded RGBA ID',fid(im)==rec['sourceFrameId'])
 check(rec['pose']+' output hash',sha(P/rec['outputPNG'])==rec['outputPNGsha256'])
 check(rec['pose']+' exact full-canvas NN',im.resize((119,119),Image.Resampling.NEAREST).tobytes()==out.tobytes())
 check(rec['pose']+' no fit/translation/snap/paint/alpha cleanup',all(rec['registration'][k] is False for k in ['perPoseFit','perPoseTranslation','snap','pixelPaint','alphaCleanup']))
for row in load('protected-upstream.json')['files']:check('protected upstream '+row['file'],sha(R/row['file'])==row['sha256'])
check('copied old96 exact',sha(P/'exact-current-awake96.png')==sha(R/load('protected-upstream.json')['files'][1]['file']))
check('copied old profile exact',sha(P/'current-awake-blink-profile-reference.json')==sha(R/load('protected-upstream.json')['files'][4]['file']))
old=load('current-awake-blink-profile-reference.json')
check('existing blink 60/3/27 unchanged',[f['durationTicks'] for f in old['clips'][0]['frames']]==[60,3,27])
check('candidate review only no activation',m['scope']=='review-only' and m['activation']=='none' and mp['current96ProfileChanged'] is False and mp['appBound'] is False)
for frame in m['frames']:check(frame['id']+' density1/integerpivot/contactsunbound',frame['canvas']==frame['world']=={'width':119,'height':119} and frame['sourcePixelsPerWorldUnit']==1 and frame['pivot']=={'x':71,'y':93} and frame['contacts']==[])
check('rounding support null/geometry false',rounding['contacts']==[] and rounding['supportWorld'] is None and not rounding['geometryReviewed'])
check('world and fractional-density rounding explicit',math.isclose(rounding['previousWorldCanvas'],96/(37/46)) and math.isclose(rounding['worldCanvasDelta'],119-96/(37/46)))
check('old world pivot delta explicit',all(math.isclose(rounding['pivotDeltaFromOldWorld'][i],[71,93][i]-[57,75][i]/(37/46),abs_tol=1e-12) for i in range(2)))
check('resized old grid pivot delta explicit',all(math.isclose(rounding['pivotDeltaFromResizedGrid'][i],[71,93][i]-[57,75][i]*119/96,abs_tol=1e-12) for i in range(2)))
check('named atlas and manifest hashes',sha(P/mp['atlasBinding']['file'])==mp['atlasBinding']['sha256']==m['source']['sha256'] and sha(P/mp['manifest']['file'])==mp['manifest']['sha256'])
atlas=rgba(mp['atlasBinding']['file']);check('atlas dimensions',atlas.size==(238,119))
for i,row in enumerate(mp['sourceToRenderFrames']):
 rect=row['atlasRect'];rec=(p['reusedFrames']+p['frames'])[i]
 check(row['renderFrameId']+' source binding',row['primarySourceFrameId']==rec['sourceFrameId'] and sha(P/row['primarySourcePNG'])==row['primarySourcePNGsha256'])
 check(row['renderFrameId']+' atlas RGBA exact',atlas.crop((rect['x'],rect['y'],rect['x']+rect['width'],rect['y']+rect['height'])).tobytes()==rgba(row['outputPNG']).tobytes() and sha(P/row['outputPNG'])==row['outputPNGsha256'])
check('map exact clip schedule',mp['clips']==m['clips'])
check('awake-only idle60',[f['durationTicks'] for f in m['clips'][0]['frames']]==[60] and m['clips'][0]['frames'][0]['frameId']==m['frames'][0]['id'])
check('look30/12/30 authored 30Hz one-shot',[f['durationTicks'] for f in m['clips'][1]['frames']]==[30,12,30] and m['clips'][1]['tickRate']==30 and not m['clips'][1]['loop'])
apng=Image.open(P/'look-study.apng');check('APNG3 frames one-shot',apng.n_frames==3 and apng.info['loop']==1)
for i,n in enumerate(['reused-awake119.png','look119.png','reused-awake119.png']):
 apng.seek(i);check('APNG frame '+str(i)+' exact RGBA and delay',apng.convert('RGBA').tobytes()==rgba(n).tobytes() and math.isclose(apng.info['duration'],[1000,400,1000][i]))
gif=Image.open(P/'look-study.gif');dur=[]
for i in range(gif.n_frames):gif.seek(i);dur.append(gif.info['duration'])
check('GIF3 palette frames 2400ms',dur==[1000,400,1000])
b=load('browser-verification.json');check('browser9numeric no page errors/captures',len(b['samples'])==9 and b['pageErrors']==[] and b['browserCaptureFiles']==0 and b['birdCanvasCSS']==119 and not b['appVisited'])
check('live deadline full2400ms terminal71',b['samples'][-1]['state']['tick']==71 and not b['samples'][-1]['state']['running'] and b['samples'][-1]['state']['elapsedMs']>=2400)
check('actual live look seen',b['samples'][-2]['state']['running'] and b['samples'][-2]['state']['renderFrameId']==m['frames'][1]['id'])
diag=load('body-contact-diagnostics.json');check('diagnosed stance change retained',diag['metrics'][1]['lowestRow']-diag['metrics'][0]['lowestRow']==4 and diag['contacts']==[] and diag['supportWorld'] is None and not diag['geometryReviewed'])
# Scan publishable text, not PNG binary/source hashes. Pattern construction avoids matching this checker itself.
patterns={'privateLibraryHandle':'libfile_'+r'[0-9a-f]{32}','signedURL':r'https?://[^\s\"<>]*(?:X-Amz-Signature|X-Goog-Signature|[?&]sig=)','embeddedImagePayload':'data:image/'+r'[^;]+;base64,','capturePayloadKey':r'\"(?:screenshotBase64|captureBase64|screenshotBytes)\"\s*:'}
findings=[]
for file in sorted(P.iterdir()):
 if file.suffix not in ['.json','.txt','.js','.html','.md','.py']:continue
 text=file.read_text()
 for name,pat in patterns.items():
  if re.search(pat,text,re.I):findings.append({'file':file.name,'type':name})
check('public metadata no private handles/signed URLs/embedded captures',not findings)
result={'status':'PASS source/export/clock/privacy checks; art HELD pending independent review','checks':checks,'checkCount':len(checks),'publicMetadataFindings':findings,'nativeCalls':1,'nativeRunning':False,'newDrawings':1,'reusedSources':1,'newNeutral':0,'newBlink':0,'sourceHeld':True,'current96ProfileChanged':False,'canonicalZodSharp':'NOT_RUN','MacAdoption':'UNKNOWN'}
(P/'verification.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'checks':len(checks),'status':result['status']}))
