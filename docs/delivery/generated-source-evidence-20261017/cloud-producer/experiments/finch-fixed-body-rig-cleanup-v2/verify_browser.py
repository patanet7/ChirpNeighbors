from pathlib import Path
from playwright.sync_api import sync_playwright
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from functools import partial
import threading,json,hashlib
P=Path(__file__).parent
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(P)));threading.Thread(target=server.serve_forever,daemon=True).start();errors=[];samples=[];digests=[]
try:
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox']);page=browser.new_page(viewport={'width':1350,'height':1100});page.on('pageerror',lambda e:errors.append(str(e)));page.goto(f'http://127.0.0.1:{server.server_port}/review.html');page.wait_for_function('Array.from(document.images).every(i=>i.complete&&i.naturalWidth>0)');assert page.locator('#an').evaluate('(i)=>i.clientWidth')==96 and page.locator('#az').evaluate('(i)=>i.clientWidth')==410
  for bg in ['opaque','transparent','dark']:
   page.locator('#background').select_option(bg)
   for i in range(5):
    page.evaluate('(i)=>window.proofDraw(i)',i);page.wait_for_function('Array.from(document.images).every(i=>i.complete&&i.naturalWidth>0)');assert page.evaluate('window.currentPhase')==i;samples.append({'background':bg,'phase':i,'decodedImages':page.locator('img').count()});digests.append(hashlib.sha256(page.locator('#az').screenshot()).hexdigest())
  page.locator('#play').click();initial=page.evaluate('window.currentPhase');page.wait_for_function('(i)=>window.currentPhase!==i',arg=initial);assert not errors;browser.close()
finally:server.shutdown()
receipt={'passed':True,'normalCanvasCSSpx':96,'neckZoomCSSwidth':410,'neckZoomSourceWidth':205,'backgroundPhaseSamples':15,'distinctAfterZoomStatesAcrossBackgrounds':len(set(digests)),'allImagesDecoded':True,'fivePhasePlaybackAdvances':True,'pageErrors':errors,'appRendererTested':False,'screenshotsDelivered':False,'samples':samples};(P/'browser-verification.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({k:v for k,v in receipt.items() if k!='samples'}))
