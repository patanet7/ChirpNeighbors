from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from functools import partial
from threading import Thread
from playwright.sync_api import sync_playwright
from PIL import Image
from io import BytesIO
import json,hashlib,time,numpy as np
P=Path(__file__).parent;server=ThreadingHTTPServer(('127.0.0.1',0),partial(SimpleHTTPRequestHandler,directory=str(P)));Thread(target=server.serve_forever,daemon=True).start();errors=[]
try:
 with sync_playwright() as pw:
  browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox']);page=browser.new_page(viewport={'width':1100,'height':900});page.on('pageerror',lambda e:errors.append(str(e)));page.goto(f'http://127.0.0.1:{server.server_port}/review.html');page.wait_for_function('Array.from(document.images).every(i=>i.complete&&i.naturalWidth>0)');loc=page.locator('#normal');size=loc.evaluate('(i)=>({cssWidth:i.clientWidth,cssHeight:i.clientHeight,naturalWidth:i.naturalWidth})');assert size['cssWidth']==186 and size['naturalWidth']==192
  # Dense timestamped real native playback samples around a100ms blink. Captures stay in memory.
  samples=[];start=time.monotonic()
  for target in [0,2.20,2.30,2.40,2.46,2.50,2.54,2.58,2.62,2.70,2.85,3.2]:
   page.wait_for_timeout(max(0,(target-(time.monotonic()-start))*1000));before=(time.monotonic()-start)*1000;raw=loc.screenshot();after=(time.monotonic()-start)*1000;samples.append({'captureStartElapsedMs':round(before,2),'captureEndElapsedMs':round(after,2),'screenshotPNGsha256':hashlib.sha256(raw).hexdigest(),'dimensions':list(Image.open(BytesIO(raw)).size)})
  browser.close()
 assert not errors;distinct=len({s['screenshotPNGsha256'] for s in samples});assert distinct>=2,'Closed state not captured in native playback samples'
 (P/'browser-playback.json').write_text(json.dumps({'method':'native Chromium APNG playback on retained standalone HTML at normal proposed CSS/world size, dense samples around blink; no manual phase stepping','normalImage':size,'samples':samples,'distinctNativeBrowserStates':distinct,'pageErrors':errors,'captureRetention':'Only numeric timing/dimensions and SHA256 hashes retained; no browser capture bytes/base64 or screenshot files saved.','exactPhaseOriginUncertain':'Image decode/compositor load origin and capture duration limit exact frame-boundary timing inference. Source APNG decoded timings are verified separately.','continuousHumanVideoReview':False,'actualMacYardPlayback':False,'appBound':False},indent=2)+'\n')
finally:server.shutdown();server.server_close()
