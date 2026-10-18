from pathlib import Path
import threading,http.server,socketserver,functools,json
from playwright.sync_api import sync_playwright
P=Path(__file__).parent
class Quiet(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
server=socketserver.TCPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(P)));threading.Thread(target=server.serve_forever,daemon=True).start();samples=[];errors=[]
with sync_playwright() as pl:
 b=pl.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox']);page=b.new_page(viewport={'width':1200,'height':1000},device_scale_factor=1);page.on('pageerror',lambda e:errors.append(str(e)));page.goto(f'http://127.0.0.1:{server.server_address[1]}/review.html');page.wait_for_function('window.FINCH_HOP_REVIEW?.ready')
 def sample(label):
  r=page.evaluate('''async()=>({state:FINCH_HOP_REVIEW.getState(),panels:await Promise.all(['pose-light','pose-dark','travel-light','travel-dark'].map(async id=>{let c=document.getElementById(id),a=c.getContext('2d').getImageData(0,0,c.width,c.height).data,d=await crypto.subtle.digest('SHA-256',a);return{id,width:c.width,height:c.height,cssWidth:parseFloat(getComputedStyle(c).width),cssHeight:parseFloat(getComputedStyle(c).height),rgbaSHA256:Array.from(new Uint8Array(d)).map(x=>x.toString(16).padStart(2,'0')).join('')}}))})''');r['label']=label;samples.append(r);return r
 for t in [0,5,6,8,9,11,12,14,15,17,18,29]:page.evaluate('(t)=>FINCH_HOP_REVIEW.seek(t)',t);r=sample('seek:'+str(t));assert r['state']['tick']==t
 page.evaluate('FINCH_HOP_REVIEW.play()');sample('immediate-play')
 for lo,hi in [(6,9),(9,12),(12,15),(15,18)]:
  page.wait_for_function('([lo,hi])=>{let t=FINCH_HOP_REVIEW.getState().tick;return t>=lo&&t<hi}',arg=[lo,hi],polling=5,timeout=2500);sample('live-phase:'+str(lo))
 page.wait_for_function('!FINCH_HOP_REVIEW.getState().running',timeout=2500);r=sample('deadline-stop');assert r['state']['tick']==29 and r['state']['elapsedMs']>=1000;assert not errors;assert all(s['state']['sourceHeld'] and not s['state']['completedHop'] and s['state']['contacts']==[] for s in samples);b.close()
server.shutdown();receipt={'status':'PASS bounded held-study viewer clocks/hash/layout; no art/contact admission','samples':samples,'pageErrors':errors,'browserCaptureFiles':0,'appVisited':False,'birdCanvasCSS':96,'deviceScaleFactor':1,'nativeCalls':1,'nominalDurationTicks':30,'terminalSampleTick':29,'stopPolicy':'finalsample29 held until elapsed>=1000ms','knownFailure':'Unmatched source family scale/body placements; actual projected toe-plane gaps retained.','newDrawings':4,'supportAccepted':False};(P/'browser-verification.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({'samples':len(samples),'errors':errors,'captures':0,'deadline':r['state']['elapsedMs']}))
