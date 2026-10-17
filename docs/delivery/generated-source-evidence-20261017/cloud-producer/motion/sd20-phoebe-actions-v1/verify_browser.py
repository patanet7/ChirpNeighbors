from pathlib import Path
import json,time,threading,hashlib,io,http.server,functools
from PIL import Image
import numpy as np
from playwright.sync_api import sync_playwright
P=Path(__file__).parent
class QuietHandler(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(QuietHandler,directory=str(P)))
thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
try:
 with sync_playwright() as pw:
  browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
  page=browser.new_page(viewport={'width':1200,'height':1100},device_scale_factor=1);errors=[];page.on('pageerror',lambda err:errors.append(str(err)));page.goto(f'http://127.0.0.1:{server.server_port}/review.html');page.wait_for_load_state('load');element=page.locator('#action');element.evaluate("async e=>{Object.assign(e.style,{position:'fixed',left:'0px',top:'0px',margin:'0px',zIndex:100,background:'#d9d4bd'});e.src='/normal-speed.apng?sample='+Date.now();await e.decode()}");start=time.monotonic();samples=[]
  expected={}
  for name in ['neutral','tail-up','tail-down','closed']:
   bg=Image.new('RGBA',(96,96),'#d9d4bd');bg.alpha_composite(Image.open(P/'frames96'/(name+'.png')).convert('RGBA'));expected[name]=np.array(bg.convert('RGB')).astype(float)
  for target in [150,2990,3050,3110,3170,5190,5250,5310,5550]:
   while (time.monotonic()-start)*1000<target:time.sleep(.005)
   t0=(time.monotonic()-start)*1000;png=element.screenshot(animations='allow');t1=(time.monotonic()-start)*1000;a=np.array(Image.open(io.BytesIO(png)).convert('RGB')).astype(float);dist={n:float(np.abs(a-v).mean()) for n,v in expected.items()};closest=min(dist,key=dist.get);samples.append({'requestedMs':target,'captureStartMs':round(t0,1),'captureEndMs':round(t1,1),'renderedRegionSize':list(a.shape[:2]),'closestPhase':closest,'meanAbsoluteRGBError':dist[closest],'sha256':hashlib.sha256(png).hexdigest()})
  browser.close()
 receipt={'browser':'Chromium actual APNG page playback via loopback HTTP','pageErrors':errors,'samples':samples,'observedDistinctPhases':sorted(set(s['closestPhase'] for s in samples)),'scope':'Timestamped playback samples, not continuous human visual assessment or actual yard renderer. No screenshots retained or uploaded.','passed':not errors and len(set(s['sha256'] for s in samples))>=3}
 (P/'browser-verification.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2));assert receipt['passed']
finally:server.shutdown();server.server_close()
