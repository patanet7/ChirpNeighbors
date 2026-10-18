from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from functools import partial
from threading import Thread
from playwright.sync_api import sync_playwright
from PIL import Image
import json,hashlib,datetime
P=Path(__file__).parent
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(P)));Thread(target=server.serve_forever,daemon=True).start();errors=[];samples=[]
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox']);p=b.new_page(viewport={'width':1250,'height':1000},device_scale_factor=1);p.on('pageerror',lambda e:errors.append(str(e)));p.goto(f'http://127.0.0.1:{server.server_port}/review.html');p.wait_for_function('window.doveAirPilotReady===true')
 for theme in ['light','dark']:
  p.click('#'+theme)
  for ident in ['old','normal']:
   x=p.evaluate("""async id=>{const c=document.getElementById(id),r=c.getBoundingClientRect(),a=c.getContext('2d').getImageData(0,0,144,144).data;return {id,CSS:[r.width,r.height],backing:[c.width,c.height],background:getComputedStyle(c).backgroundColor,canvasRGBAsha256:Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',a)),x=>x.toString(16).padStart(2,'0')).join('')}}""",ident);x['theme']=theme;samples.append(x);assert x['CSS']==x['backing']==[144,144]
 assert not errors and p.evaluate('window.doveAirPilotError||null') is None
 for ident in ['old','normal']:
  assert len({s['canvasRGBAsha256'] for s in samples if s['id']==ident})==1
 r={'status':'PASS static source-only light/dark comparison','testedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'browser':b.version,'samples':samples,'actualCandidateCSS':[144,144],'oneStaticCandidatePose':True,'animationOrRootTravelTested':False,'savedScreenshots':0,'savedCaptureBytes':0,'pageErrors':errors,'sourceFramingVerdict':'independent/root pending','takeoffLandingFullFlightAccepted':False,'MacAdmission':False};b.close()
server.shutdown();(P/'browser-verification.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:v for k,v in r.items() if k!='samples'}))
