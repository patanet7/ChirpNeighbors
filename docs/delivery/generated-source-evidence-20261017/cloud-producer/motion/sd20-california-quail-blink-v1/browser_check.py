from pathlib import Path
import threading,http.server,socketserver,functools,json
from playwright.sync_api import sync_playwright
P=Path(__file__).parent
class Quiet(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
s=socketserver.TCPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(P)));threading.Thread(target=s.serve_forever,daemon=True).start();samples=[];errors=[]
with sync_playwright() as pl:
 b=pl.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox']);page=b.new_page(viewport={'width':1200,'height':1000},device_scale_factor=1);page.on('pageerror',lambda e:errors.append(str(e)));page.goto(f'http://127.0.0.1:{s.server_address[1]}/review.html');page.wait_for_function('window.QUAIL_BLINK_REVIEW?.ready')
 def snap(label):
  r=page.evaluate('''async()=>({state:QUAIL_BLINK_REVIEW.getState(),panels:await Promise.all(['light','dark'].map(async id=>{let c=document.getElementById(id),bytes=c.getContext('2d').getImageData(0,0,c.width,c.height).data,digest=await crypto.subtle.digest('SHA-256',bytes);return{id,width:c.width,height:c.height,cssWidth:parseFloat(getComputedStyle(c).width),cssHeight:parseFloat(getComputedStyle(c).height),rgbaSHA256:Array.from(new Uint8Array(digest)).map(v=>v.toString(16).padStart(2,'0')).join('')}}))})''');r['label']=label;samples.append(r);return r
 for tick in [0,41,42,44,45,89]:
  page.evaluate('(t)=>QUAIL_BLINK_REVIEW.seek(t)',tick);r=snap('seek:'+str(tick));assert ('blink-closed' in r['state']['renderFrameId'])==(42<=tick<45)
 page.evaluate('QUAIL_BLINK_REVIEW.play()');snap('immediate-play');page.wait_for_function('QUAIL_BLINK_REVIEW.getState().tick>=42&&QUAIL_BLINK_REVIEW.getState().tick<45',timeout=4000,polling=5);r=snap('live100ms-closed');assert 'blink-closed' in r['state']['renderFrameId'];page.wait_for_function('!QUAIL_BLINK_REVIEW.getState().running',timeout=5000);r=snap('deadline-stop');assert r['state']['elapsedMs']>=3000 and r['state']['tick']==89;assert not errors;assert all(p['cssWidth']==300 and p['cssHeight']==270 for r in samples for p in r['panels']);b.close()
s.shutdown();receipt={'status':'PASS bounded source viewer numeric check','samples':samples,'pageErrors':errors,'browserCaptureFiles':0,'appVisited':False,'birdCanvasCSS':384/1.625,'deviceScaleFactor':1,'nominalDurationTicks':90,'terminalSampleTick':89,'stopPolicy':'final sample89 held until elapsed>=3000ms','qualification':'Only source viewer clocks/layout/hashes; independent visual review and actual Mac admission remain separate.'};(P/'browser-verification.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({'samples':len(samples),'errors':errors,'captures':0,'liveClosureObserved':True}))
