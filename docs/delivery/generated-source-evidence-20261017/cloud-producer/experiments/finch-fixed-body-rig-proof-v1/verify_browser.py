from pathlib import Path
from playwright.sync_api import sync_playwright
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from functools import partial
import hashlib,json,threading
P=Path(__file__).parent
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(P)));threading.Thread(target=server.serve_forever,daemon=True).start();errors=[];samples=[];digests=[]
try:
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox']);page=browser.new_page(viewport={'width':1100,'height':1150});page.on('pageerror',lambda e:errors.append(str(e)));page.goto(f'http://127.0.0.1:{server.server_port}/review.html');page.wait_for_function('window.proofReady===true');page.locator('#play').click()
  for direction in ['1','-1']:
   page.locator('#face').select_option(direction)
   for i in range(5):
    sample=page.evaluate('(k)=>window.proofRender(k)',i);assert sample['changed']==0 and sample['bodyScale']==1;samples.append({'direction':direction,**sample});digests.append(hashlib.sha256(page.locator('#view').screenshot()).hexdigest())
  page.locator('#face').select_option('1');page.evaluate('window.proofRender(1)');page.screenshot(path='/tmp/finch-rig-proof-internal.png');assert len(set(digests))==6;assert not errors;browser.close()
finally:server.shutdown()
receipt={'passed':True,'runtimeCanvasPhaseFacingSamples':len(samples),'distinctVisibleStatesAcrossBothFacings':len(set(digests)),'allProtectedRGBAChangedPixelsZero':all(s['changed']==0 for s in samples),'errors':errors,'screenshotsDelivered':False,'appRendererRun':False,'samples':samples};(P/'browser-verification.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({k:v for k,v in receipt.items() if k!='samples'}))
