from pathlib import Path
import functools,http.server,threading,json,hashlib,time
from playwright.sync_api import sync_playwright
P=Path('/workspace/asset-production/experiments/bushtit-blink-readability-preflight-v1')
class Handler(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(P)));threading.Thread(target=server.serve_forever,daemon=True).start()
try:
 with sync_playwright() as pw:
  browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox']);page=browser.new_page(viewport={'width':1000,'height':850},device_scale_factor=1);errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.goto(f'http://127.0.0.1:{server.server_port}/review.html');page.wait_for_function('window.BUSHTIT_PREFLIGHT?.ready')
  dims=page.evaluate('Array.from(document.querySelectorAll("canvas")).map(c=>({id:c.id,backing:[c.width,c.height],CSS:[c.getBoundingClientRect().width,c.getBoundingClientRect().height]}))');samples=[]
  for tick in [0,59,60,61,62,63,89,90]:
   state=page.evaluate('(t)=>BUSHTIT_PREFLIGHT.seek(t)',tick);hashes=page.evaluate('Object.fromEntries(Array.from(document.querySelectorAll("canvas")).map(c=>[c.id,Array.from(c.getContext("2d").getImageData(0,0,64,64).data)]))');samples.append({'requested':tick,'state':state,'canvasRGBAsha256':{k:hashlib.sha256(bytes(v)).hexdigest() for k,v in hashes.items()}})
  page.evaluate('BUSHTIT_PREFLIGHT.play()');start=time.monotonic();live=[]
  for target in [50,1960,2010,2045,2075,2140,3010]:
   while (time.monotonic()-start)*1000<target:time.sleep(.001)
   live.append({'wallElapsedMs':(time.monotonic()-start)*1000,'state':page.evaluate('BUSHTIT_PREFLIGHT.getState()')})
  browser.close()
 assert not errors and all(d['CSS']==[64,64] and d['backing']==[64,64] for d in dims)
 assert [s['state']['phase'] for s in samples]==['awake','awake','closed','closed','closed','awake','awake','awake']
 assert any(s['state']['phase']=='closed' for s in live) and live[-1]['state']['tick']==89 and not live[-1]['state']['running']
 for cid in samples[0]['canvasRGBAsha256']:
  assert samples[0]['canvasRGBAsha256'][cid]==samples[5]['canvasRGBAsha256'][cid]!=samples[2]['canvasRGBAsha256'][cid]
 receipt={'passed':True,'browser':'Chromium','DPR':1,'dimensions':dims,'seekSamples':samples,'liveSamples':live,'pageErrors':errors,'sourceRasterClockVerified':True,'semanticBlinkReadabilityPassed':None,'capturesSaved':False,'actualRuntimeAdmission':False,'scope':'Numerical live source-viewer/decoded canvas verification only, not semantic review or app execution.'};(P/'browser-playback-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({'passed':True,'dimensions':dims,'closedLiveTicks':[s['state']['tick'] for s in live if s['state']['phase']=='closed'],'terminal':live[-1]['state']}))
finally:server.shutdown();server.server_close()
