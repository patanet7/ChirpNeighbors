from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from functools import partial
from threading import Thread
from playwright.sync_api import sync_playwright
import json,hashlib,time
P=Path(__file__).parent;server=ThreadingHTTPServer(('127.0.0.1',0),partial(SimpleHTTPRequestHandler,directory=str(P)));Thread(target=server.serve_forever,daemon=True).start();errors=[]
try:
 with sync_playwright() as pw:
  browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox']);page=browser.new_page(viewport={'width':1180,'height':1500});page.on('pageerror',lambda e:errors.append(str(e)));page.goto(f'http://127.0.0.1:{server.server_port}/review.html');page.wait_for_function('Array.from(document.images).every(i=>i.complete&&i.naturalWidth>0)&&window.currentHoverState');images=page.locator('img');sizes=images.evaluate_all('(a)=>a.map(i=>({cssWidth:i.clientWidth,cssHeight:i.clientHeight,naturalWidth:i.naturalWidth,naturalHeight:i.naturalHeight}))');assert [s['cssWidth'] for s in sizes[:3]]==[64,96,384]
  live=page.evaluate('''()=>new Promise(resolve=>{const rows=[];let start;function sample(t){if(start===undefined)start=t;rows.push({elapsedMs:t-start,...window.currentHoverState});if(t-start<650)requestAnimationFrame(sample);else resolve(rows)}requestAnimationFrame(sample)})''');assert len({r['frameId'] for r in live})==4
  samples=[];start=time.monotonic()
  for k in range(10):
   page.wait_for_timeout(21+7*(k%3));samples.append({'elapsedMs':round((time.monotonic()-start)*1000),'sha256':hashlib.sha256(images.nth(0).screenshot()).hexdigest()})
  assert len({r['sha256'] for r in samples})>=2
  page.get_by_role('button',name='Pause body demo').click();times=[0,100/3,200/3,100,1000,1499,1500,1550,1600,1700,2500,2999,3000,3050,3100,3200,3999,4000];controls=page.evaluate('ts=>ts.map(t=>({t,...window.sampleHoverAt(t)}))',times);assert len({r['frameId'] for r in controls[:4]})==4;assert all(r['root']==[48,44] for r in controls[:5]);assert controls[-1]['root']==[48,44];assert controls[9]['root']==[49.5,43.5]
  canvasDigests=page.evaluate('''async()=>{const out=[];for(const t of[0,100/3,200/3,100,1550,3050]){const state=window.sampleHoverAt(t);const c=document.querySelector('#yard'),d=c.getContext('2d').getImageData(0,0,c.width,c.height).data;const hash=await crypto.subtle.digest('SHA-256',d);out.push({t,state,pixelSHA256:Array.from(new Uint8Array(hash),v=>v.toString(16).padStart(2,'0')).join('')})}return out}''');assert len({r['pixelSHA256'] for r in canvasDigests[:4]})==4
  page.get_by_role('button',name='Dark ground').click();dark=images.nth(0).evaluate('(i)=>getComputedStyle(i).backgroundColor');assert dark=='rgb(23, 34, 31)';page.get_by_role('button',name='Light ground').click();light=images.nth(0).evaluate('(i)=>getComputedStyle(i).backgroundColor');assert light=='rgb(217, 212, 189)';assert not errors;browser.close()
 r={'passed':True,'method':'Actual Chromium native APNG64CSSpx sampled10times; actual rAF canvas4poses; deterministic frozen/moving root controls with pixel hashes only, bytes discarded','sizes':sizes,'nativeAPNGSamples':samples,'distinctNativeAPNGSampleStates':len({s['sha256'] for s in samples}),'liveCanvasRecords':live,'distinctActualCanvasFrameIds':len({s['frameId'] for s in live}),'frozenAndMovingRootControls':controls,'canvasPixelHashControls':canvasDigests,'backgroundControlsVerified':{'dark':dark,'light':light},'pageErrors':errors,'actualYardIntegration':False,'browserCapturesSavedOrBundled':False,'continuousHumanMotionPerceptionVerified':False};(P/'browser-verification.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:r[k] for k in ['passed','distinctNativeAPNGSampleStates','distinctActualCanvasFrameIds','backgroundControlsVerified','pageErrors']}))
finally:server.shutdown();server.server_close()
