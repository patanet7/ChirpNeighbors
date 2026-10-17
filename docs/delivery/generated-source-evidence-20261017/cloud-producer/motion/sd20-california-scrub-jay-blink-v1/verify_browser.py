from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from functools import partial
from threading import Thread
from playwright.sync_api import sync_playwright
import json,hashlib,time
P=Path(__file__).parent;server=ThreadingHTTPServer(('127.0.0.1',0),partial(SimpleHTTPRequestHandler,directory=str(P)));Thread(target=server.serve_forever,daemon=True).start();errors=[]
try:
 with sync_playwright() as pw:
  browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox']);page=browser.new_page(viewport={'width':1150,'height':1400});page.on('pageerror',lambda e:errors.append(str(e)));page.goto(f'http://127.0.0.1:{server.server_port}/review.html');page.wait_for_function('Array.from(document.images).every(i=>i.complete&&i.naturalWidth>0)');images=page.locator('img');sizes=images.evaluate_all('(a)=>a.map(i=>({cssWidth:i.clientWidth,cssHeight:i.clientHeight,naturalWidth:i.naturalWidth,naturalHeight:i.naturalHeight}))');assert [s['cssWidth'] for s in sizes[:4]]==[200,384,200,200];samples=[];start=time.monotonic()
  for target in [0,.5,1.5,1.94,1.99,2.03,2.08,2.14,2.5,3.1]:
   page.wait_for_timeout(max(0,(target-(time.monotonic()-start))*1000));samples.append({'elapsedMs':round((time.monotonic()-start)*1000),'sha256':hashlib.sha256(images.nth(0).screenshot()).hexdigest()})
  page.get_by_role('button',name='Dark ground').click();dark=images.nth(0).evaluate('(i)=>getComputedStyle(i).backgroundColor');assert dark=='rgb(23, 34, 31)';page.get_by_role('button',name='Light ground').click();light=images.nth(0).evaluate('(i)=>getComputedStyle(i).backgroundColor');assert light=='rgb(217, 212, 189)';assert not errors;assert len({s['sha256'] for s in samples})==2;browser.close()
 result={'passed':True,'method':'Chromium native APNG at200CSSpx world canvas; ten timestamped actual playback raster samples, not continuous human review','sizes':sizes,'samples':samples,'distinctNormalSizeStates':len({s['sha256'] for s in samples}),'backgroundControlsVerified':{'dark':dark,'light':light},'pageErrors':errors,'actualYardIntegration':False,'screenshotsSavedOrPublished':False};(P/'browser-verification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k not in ['samples','sizes']}))
finally:server.shutdown();server.server_close()
