from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from functools import partial
from threading import Thread
from playwright.sync_api import sync_playwright
import json,hashlib,time
P=Path(__file__).parent
server=ThreadingHTTPServer(('127.0.0.1',0),partial(SimpleHTTPRequestHandler,directory=str(P)));Thread(target=server.serve_forever,daemon=True).start();errors=[]
try:
 with sync_playwright() as pw:
  browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox']);page=browser.new_page(viewport={'width':1100,'height':1200});page.on('pageerror',lambda e:errors.append(str(e)));page.goto(f'http://127.0.0.1:{server.server_port}/review.html');page.wait_for_function('Array.from(document.images).every(i=>i.complete&&i.naturalWidth>0)');images=page.locator('img');sizes=images.evaluate_all('(a)=>a.map(i=>({cssWidth:i.clientWidth,cssHeight:i.clientHeight,naturalWidth:i.naturalWidth,naturalHeight:i.naturalHeight}))');assert [s['cssWidth'] for s in sizes]==[64,288,64,288]
  perched=[];hover=[];start=time.monotonic()
  for target in [0,.17,.38,.59,1.1,2.16,2.21,2.25,2.3,2.5,3.2]:
   page.wait_for_timeout(max(0,(target-(time.monotonic()-start))*1000));perched.append({'elapsedMs':round((time.monotonic()-start)*1000),'sha256':hashlib.sha256(images.nth(0).screenshot()).hexdigest()});hover.append({'elapsedMs':round((time.monotonic()-start)*1000),'sha256':hashlib.sha256(images.nth(2).screenshot()).hexdigest()})
  assert not errors;browser.close()
 result={'method':'actualChromium nativeAPNG timestampedraster samples at64CSSworldcanvas; no continuoushumanvideo review','sizes':sizes,'perchedSamples':perched,'hoverSamples':hover,'distinctPerchedStates':len({s['sha256'] for s in perched}),'distinctHoverStates':len({s['sha256'] for s in hover}),'pageErrors':errors,'actualYardIntegration':False,'screenshotsSavedOrPublished':False};(P/'browser-verification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k not in ['perchedSamples','hoverSamples']}))
finally:server.shutdown();server.server_close()
