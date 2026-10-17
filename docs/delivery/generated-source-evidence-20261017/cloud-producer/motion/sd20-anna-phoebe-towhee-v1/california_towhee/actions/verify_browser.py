from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from functools import partial
from threading import Thread
from playwright.sync_api import sync_playwright
import json,hashlib,time
P=Path(__file__).parent;server=ThreadingHTTPServer(('127.0.0.1',0),partial(SimpleHTTPRequestHandler,directory=str(P)));Thread(target=server.serve_forever,daemon=True).start();errors=[]
try:
 with sync_playwright() as pw:
  browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox']);page=browser.new_page(viewport={'width':1050,'height':650});page.on('pageerror',lambda e:errors.append(str(e)));page.goto(f'http://127.0.0.1:{server.server_port}/review.html');page.wait_for_function('Array.from(document.images).every(i=>i.complete&&i.naturalWidth>0)');sizes=page.locator('img').evaluate_all('(a)=>a.map(i=>({cssWidth:i.clientWidth,naturalWidth:i.naturalWidth}))');assert [s['cssWidth'] for s in sizes]==[112,192];start=time.monotonic();samples=[]
  for target in [0,1.41,1.47,2.4,2.7,3.3]:
   page.wait_for_timeout(max(0,(target-(time.monotonic()-start))*1000));samples.append({'elapsedMs':round((time.monotonic()-start)*1000),'rasterSha256':hashlib.sha256(page.locator('img').first.screenshot()).hexdigest()})
  browser.close()
 assert not errors;distinct=len({s['rasterSha256'] for s in samples});assert distinct>=2
 (P/'browser-verification.json').write_text(json.dumps({'method':'native Chromium APNG at proposed112CSSpx world canvas; six timestamped in-memory raster samples, no screenshots saved','sizes':sizes,'samples':samples,'distinctBrowserStates':distinct,'pageErrors':errors,'continuousHumanVideoReview':False,'actualAppYardReview':False,'appBound':False},indent=2)+'\n')
finally:server.shutdown();server.server_close()
