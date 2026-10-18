from pathlib import Path
from PIL import Image
import hashlib,json,subprocess,datetime,threading,http.server,functools,time
p=Path(__file__).parent
j=lambda f:json.loads((p/f).read_text())
h=lambda f:hashlib.sha256((p/f).read_bytes()).hexdigest()
rgba=lambda f:Image.open(p/f).convert('RGBA')
idof=lambda a:'frame.sha256.'+hashlib.sha256(f'RGBA8;{a.width}x{a.height};'.encode()+a.tobytes()).hexdigest()
checks=[]
def check(name,actual,expected=True):
 checks.append({'check':name,'pass':actual==expected}); assert actual==expected,(name,actual,expected)
primary=j('PRIMARY-SOURCE-MANIFEST.json');mapping=j('frame-to-action-map.json');profile=j('texture-review-manifest.json');motion=j('bathing-motion-manifest.json');traj=j('body-root-trajectory.json');dispatch=j('call-dispatch-receipt.json')
prompt=(p/'prompt.txt').read_bytes()
check('Exact prompt4096UTF8 bytes',len(prompt),4096)
check('Submitted and prepared prompt byte equality',j('native-call-arguments.json')['arguments']['prompt'].encode()==prompt==j('prepared-native-arguments.json')['arguments']['prompt'].encode())
check('Dispatch saved prompt SHA',dispatch['promptSHA256'],h('prompt.txt'))
check('Prepared args dispatch SHA',dispatch['preparedArgsSHA256'],h('prepared-native-arguments.json'))
check('Original hash',primary['originalSHA256'],h('original.png'))
original=rgba('original.png');check('Actual native3:2 dimensions',original.size,(1536,1024))
cond=rgba('conditioning-atlas3x2.png');old=rgba('reused-awake-source768.png');rebuild=Image.new('RGBA',original.size)
for i,f in enumerate(primary['frames']):
 a=rgba(f['sourcePNG']);check(f['pose']+' decodedRGBA primaryID',idof(a),f['sourceFrameId']);check(f['pose']+' source PNG hash',h(f['sourcePNG']),f['sourcePNGsha256'])
 r=f['registration']['originalRect'];check(f['pose']+' exact nativecell',original.crop((r[0],r[1],r[0]+r[2],r[1]+r[3])).tobytes(),a.tobytes());rebuild.paste(a,(r[0],r[1]))
 b=rgba(f['outputPNG']);check(f['pose']+' fullcell directNN output',a.resize((192,192),Image.Resampling.NEAREST).tobytes(),b.tobytes());check(f['pose']+' output PNG hash',h(f['outputPNG']),f['outputPNGsha256'])
 x=(i%3)*768;y=(i//3)*768;check(f['pose']+' exact whole conditioning copy',cond.crop((x,y,x+768,y+768)).tobytes(),old.tobytes())
check('All original decodedRGBA survives sixcells',rebuild.tobytes(),original.tobytes())
check('Exact awake source identity',idof(old),primary['reusedFrames'][0]['sourceFrameId'])
root=p.parents[1]
check('Reused source unchanged from immutable oldfile',(p/'reused-awake-source768.png').read_bytes(),(root/'batches/dove-drink-v1/frames-source/00.png').read_bytes())
check('Reused192 unchanged from immutable export',(p/'reused-awake192.png').read_bytes(),(root/'reuse/sd20-dove-reuse-v1/frames192/standing-0.png').read_bytes())
check('Atlas exact hash',h('bathing-atlas192.png'),mapping['atlasBinding']['sha256']);check('Profile map exact hash',h('texture-review-manifest.json'),mapping['manifest']['sha256'])
atlas=rgba('bathing-atlas192.png')
for f in mapping['sourceToRenderFrames']:
 r=f['atlasRect'];check('Atlas exact unmodified cell '+f['renderFrameId'],atlas.crop((r['x'],r['y'],r['x']+r['width'],r['y']+r['height'])).tobytes(),rgba(f['outputPNG']).tobytes())
check('Only6new uniqueIDs',len({f['sourceFrameId'] for f in primary['frames']}),6)
check('Six new contacts empty',all(not f['contacts'] for f in profile['frames'][1:]))
check('All image pivots density world constant',all(f['pivot']=={'x':105,'y':150} and f['sourcePixelsPerWorldUnit']==1 and f['world']=={'width':192,'height':192} for f in profile['frames']))
check('Motion unbound no physicalevents',motion['supportWorld'] is None and not motion['geometryReviewed'] and all(not e['physicalEventEmitted'] for e in motion['eventMarkers']))
check('Beak water proposal explicitly unsatisfied',next(e for e in motion['eventMarkers'] if e['label']=='beak-water')['status'],'UNSATISFIED_AT_PROPOSED_WATERPLANE')
check('Halfopen contiguous135tick clock',motion['steps'][0]['ticks'][0]==0 and motion['steps'][-1]['ticks'][1]==135 and all(a['ticks'][1]==b['ticks'][0] for a,b in zip(motion['steps'],motion['steps'][1:])))
check('Root separated stationary135samples',traj['sampleTickConvention']=='frame-starts' and traj['segmentTickConvention']=='half-open' and len(traj['samples'])==135 and all(s['tick']==i and s['root']==[0,0] for i,s in enumerate(traj['samples'])))
check('Motion exact map hash',motion['frameMap']['sha256'],h('frame-to-action-map.json'));check('Motion exact root hash',motion['rootTrajectory']['sha256'],h('body-root-trajectory.json'))
for file,size in [('bathing-source-proof.apng',(192,192)),('Dove-Bathe-Held-Source-Light-Dark.gif',(384,192))]:
 a=Image.open(p/file);dur=[]
 for i in range(a.n_frames):a.seek(i);dur.append(a.info.get('duration'))
 check(file+' dimensions',a.size,size);check(file+' eight timed references',a.n_frames,8);check(file+' duration4500ms',sum(dur),4500)
check('No compact-runtime compatibility claimed',j('compact-runtime-status.json')['runtimeAdmissionClaimed'],False)
node='const fs=require("fs"),c=require("./player.js"),m=JSON.parse(fs.readFileSync("bathing-motion-manifest.json")); console.log(JSON.stringify([-99,0,23,24,38,39,56,57,68,69,77,78,86,87,110,111,134,135,999].map(t=>({requested:t,...c.stateAt(m,t)}))))'
r=subprocess.run(['node','-e',node],cwd=p,check=True,capture_output=True,text=True);node_states=json.loads(r.stdout)
check('Player negativeRAFclamp and terminalhold',node_states[0]['tick']==0 and node_states[-1]['tick']==134 and node_states[-1]['phase']=='awake-return' and node_states[-1]['ended'])
(p/'verification.json').write_text(json.dumps({'status':'PASS','checks':checks,'total':len(checks),'nodeActualClockSamples':node_states,'sourceArtAccepted':False,'canonicalZodSharpAdmission':'NOT_RUN','currentMacBinding':'UNKNOWN','testedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat()},indent=2)+'\n')
class Handler(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(p)));threading.Thread(target=server.serve_forever,daemon=True).start()
from playwright.sync_api import sync_playwright
with sync_playwright() as pw:
 browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox']);page=browser.new_page(viewport={'width':1100,'height':900});errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.goto(f'http://127.0.0.1:{server.server_port}/review.html');page.wait_for_function('window.DOVE_BATH_REVIEW?.ready');samples=[]
 for tick in [0,24,39,57,69,78,87,111,135]:
  page.evaluate('(t)=>DOVE_BATH_REVIEW.seek(t)',tick);samples.append({'requestedTick':tick,'state':page.evaluate('DOVE_BATH_REVIEW.getState()'),'canvasCSS':page.locator('canvas').first.evaluate('(e)=>({width:e.getBoundingClientRect().width,height:e.getBoundingClientRect().height,backing:[e.width,e.height],contentCSS:[getComputedStyle(e).width,getComputedStyle(e).height]})')})
 page.evaluate('DOVE_BATH_REVIEW.seek(69)');shot=page.locator('canvas').first.screenshot();Path('/tmp/dove-bathe-flutter-view.png').write_bytes(shot)
 shot_receipt={'sha256':hashlib.sha256(shot).hexdigest(),'dimensions':list(Image.open(__import__('io').BytesIO(shot)).size),'capturedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'imageBytesExcluded':True,'sourcePixelFit':False}
 page.evaluate('DOVE_BATH_REVIEW.replay()');page.wait_for_function('DOVE_BATH_REVIEW.getState().ended && !DOVE_BATH_REVIEW.getState().playing',timeout=8000);terminal=page.evaluate('DOVE_BATH_REVIEW.getState()');browser.close()
server.shutdown()
assert not errors,errors
assert terminal['tick']==134 and terminal['phase']=='awake-return'
assert all(s['canvasCSS']['contentCSS']==['192px','192px'] for s in samples)
(p/'browser-verification.json').write_text(json.dumps({'status':'PASS','browser':'Chromium via Playwright','samples':samples,'liveOneShotTerminal':terminal,'pageErrors':errors,'internalCaptureEvidence':shot_receipt,'captureImageBytesInBundle':False,'noIndependentArtVerdict':True,'geometryReviewed':False,'supportWorld':None},indent=2)+'\n')
print(json.dumps({'checks':len(checks),'allPASS':True,'browserPhaseSamples':len(samples),'liveEnd':terminal,'captureBytesExcluded':True}))
