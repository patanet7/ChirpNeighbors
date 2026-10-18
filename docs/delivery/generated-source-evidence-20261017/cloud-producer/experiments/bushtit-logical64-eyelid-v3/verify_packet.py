from pathlib import Path
from PIL import Image
from playwright.sync_api import sync_playwright
import json,hashlib,numpy as np,struct,zlib,datetime,http.server,threading,functools,time
P=Path(__file__).parent;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
awake=np.asarray(Image.open(P/'frames/awake.png').convert('RGBA'));closed=np.asarray(Image.open(P/'frames/closed.png').convert('RGBA'));mask=np.asarray(Image.open(P/'masks/eye-context-ownership.png'))>0
assert np.array_equal(awake[~mask],closed[~mask]);assert sha(P/'frames/awake.png')==sha(P/'inputs/canonical-awake64.png');assert np.count_nonzero(mask)==20
args=json.loads((P/'native-arguments.json').read_text());wrapped=json.loads((P/'native-call-arguments.json').read_text());assert args==wrapped['arguments'] and args['prompt']==(P/'prompt.txt').read_text();assert wrapped['tool']=='image_gen.imagegen'
conditioning=np.asarray(Image.open(P/'inputs/conditioning-awake-logical64-up16.png').convert('RGBA'));assert np.array_equal(conditioning,np.repeat(np.repeat(awake,16,axis=0),16,axis=1))
animations=[]
for filename,expected in [('blink.apng',[awake,closed,awake]),('raw-blink.apng',[np.asarray(Image.open(P/'raw/awake64.png')),np.asarray(Image.open(P/'raw/constructed-closed64.png')),np.asarray(Image.open(P/'raw/awake64.png'))])]:
 raw=(P/filename).read_bytes();off=8;fc=[]
 while off<len(raw):
  n=int.from_bytes(raw[off:off+4],'big');typ=raw[off+4:off+8];v=raw[off+8:off+8+n];assert zlib.crc32(typ+v)&0xffffffff==int.from_bytes(raw[off+8+n:off+12+n],'big')
  if typ==b'fcTL':fc.append(struct.unpack('>IIIIIHHBB',v))
  off+=12+n
 durations=[x[5]/x[6] for x in fc];assert durations==[2,.1,.9];im=Image.open(P/filename);assert im.n_frames==3
 for i,z in enumerate(expected):im.seek(i);assert np.array_equal(np.asarray(im.convert('RGBA')),z)
 animations.append({'file':filename,'sha256':sha(P/filename),'frames':3,'seconds':durations,'CRCValid':True,'composedRGBAExact':True})
errors=[]
class H(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(H,directory=str(P)));threading.Thread(target=server.serve_forever,daemon=True).start()
try:
 with sync_playwright() as pw:
  browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox']);page=browser.new_page(device_scale_factor=1);page.on('pageerror',lambda e:errors.append(str(e)));page.goto(f'http://127.0.0.1:{server.server_port}/review.html');page.wait_for_function('FAMILY_REVIEW.ready');dims=page.evaluate('Array.from(document.querySelectorAll("canvas")).map(c=>({id:c.id,backing:[c.width,c.height],CSS:[c.getBoundingClientRect().width,c.getBoundingClientRect().height]}))');assert len(dims)==8 and all(d['backing']==[64,64] and d['CSS']==[64,64] for d in dims)
  states=[]
  for tick,phase in [(0,'awake'),(59,'awake'),(60,'closed'),(61,'closed'),(62,'closed'),(63,'awake'),(89,'awake'),(90,'awake')]:
   st=page.evaluate('(t)=>FAMILY_REVIEW.seek(t)',tick);assert st['phase']==phase and st['tick']==min(89,tick);states.append(st)
  page.locator('#tick').evaluate('(e)=>{e.value="61";e.dispatchEvent(new Event("input",{bubbles:true}))}');assert page.evaluate('FAMILY_REVIEW.getState().tick')==61
  live=page.evaluate('''()=>new Promise(resolve=>{let values=[],last=-1;FAMILY_REVIEW.select('blink');FAMILY_REVIEW.play();function step(){const s=FAMILY_REVIEW.getState();if(s.tick!==last){values.push({tick:s.tick,phase:s.phase,elapsedMs:s.elapsedMs,running:s.running});last=s.tick}if(!s.running){resolve({samples:values,terminal:s});return}requestAnimationFrame(step)}requestAnimationFrame(step)})''');assert live['terminal']['tick']==89 and live['terminal']['elapsedMs']>=3000;assert all(any(s['tick']==t and s['phase']=='closed' for s in live['samples']) for t in [60,61,62]);assert any(s['tick']==63 and s['phase']=='awake' for s in live['samples'])
  page.evaluate('FAMILY_REVIEW.select("idle");FAMILY_REVIEW.seek(90)');assert page.evaluate('FAMILY_REVIEW.getState().tick')==59;page.evaluate('FAMILY_REVIEW.select("blink");FAMILY_REVIEW.play();FAMILY_REVIEW.seek(61)');page.wait_for_timeout(80);assert page.evaluate('FAMILY_REVIEW.getState().tick')==61;browser.close()
finally:server.shutdown();server.server_close()
assert not errors
newclear=np.argwhere(mask&(awake[:,:,3]>0)&(closed[:,:,3]==0));proof={'state':'PASS_DETERMINISTIC_REGISTRATION_CLOCK_APNG_CHECKS_ONLY','verifiedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'actualSubmittedPromptBytesMatch':True,'conditioningExact64up16RGBA':True,'maskPixels':20,'insideChangedPixels':int(np.any(awake!=closed,axis=2)[mask].sum()),'outsideChangedPixels':0,'newTransparentCellsXY':[list(map(int,p[::-1])) for p in newclear],'newTransparentCellsMeaning':'Actual retained donor transparency, no manual filling. Independent normal-size seam/eye review required.','APNG':animations,'browser':{'DPR':1,'dimensions':dims,'seekStates':states,'rangeSeek61':True,'liveObservedStates':live['samples'],'terminal':live['terminal'],'staleRAFCancelled':True,'pageErrors':errors,'capturesSaved':0},'sourceUsefulness':'PENDING_TWO_INDEPENDENT_NORMAL64_100MS_REVIEWS','physicalSupportReviewed':False,'sourceAdmitted':False,'runtimeAdmission':False,'canonicalPixelJSONCheck':'NOT_RUN_BY_PRODUCER','canonicalEvaluationDefectId':None,'normalSemanticScore':None};(P/'verification.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps({'clockAPNGRGBA':'PASS','CSS64Canvases':8,'newTransparentCellsXY':proof['newTransparentCellsXY'],'closedTicksActuallyObserved':[s for s in live['samples'] if 60<=s['tick']<=63],'errors':errors}))
