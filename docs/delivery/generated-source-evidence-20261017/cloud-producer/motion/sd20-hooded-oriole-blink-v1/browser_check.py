from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from functools import partial
from threading import Thread
from playwright.sync_api import sync_playwright
import json,datetime
P=Path(__file__).parent
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(P)));Thread(target=server.serve_forever,daemon=True).start();samples=[];errors=[]
with sync_playwright() as pw:
 browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox']);page=browser.new_page(viewport={'width':1000,'height':1200},device_scale_factor=1);page.on('pageerror',lambda e:errors.append(str(e)))
 page.goto(f'http://127.0.0.1:{server.server_port}/review.html');page.wait_for_function('window.ORIOLE_BLINK_REVIEW?.ready===true')
 def sample(label):
  row=page.evaluate("""async label=>{const state={...window.orioleState};const canvases=[...document.querySelectorAll('canvas')];const bytes=canvases[0].getContext('2d').getImageData(0,0,192,192).data;const rects=canvases.map(c=>{let r=c.getBoundingClientRect();return {width:r.width,height:r.height,backingWidth:c.width,backingHeight:c.height,background:getComputedStyle(c.parentElement).backgroundColor}});const hash=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes)),x=>x.toString(16).padStart(2,'0')).join('');return{label,...state,canvases:rects,canvasPixelSHA256:hash}}""",label);samples.append(row);return row
 page.evaluate("ORIOLE_BLINK_REVIEW.replay('blink')");page.wait_for_function("window.orioleState?.renderFrameId==='hooded_oriole-closed-blink-study-192'",timeout=5000);live=sample('actual live closed-window');assert live['renderFrameId']=='hooded_oriole-closed-blink-study-192'
 page.wait_for_function('window.orioleState?.terminal===true',timeout=5000);held=sample('actual onecycle finalawakehold');assert held['renderFrameId']=='hooded_oriole-neutral-192'
 for t in [0,1999,2000,2099,2100,3000,9000]:
  page.evaluate('t=>ORIOLE_BLINK_REVIEW.sampleAt(t)',t);r=sample('manual exactms '+str(t));assert r['renderFrameId']==('hooded_oriole-closed-blink-study-192' if 2000<=t<2100 else 'hooded_oriole-neutral-192')
 page.click('#idle');r=sample('awake-only idle firsthold');assert r['clipId']=='idle' and r['renderFrameId']=='hooded_oriole-neutral-192'
 page.evaluate("ORIOLE_BLINK_REVIEW.replay('blink');ORIOLE_BLINK_REVIEW.replay('blink');ORIOLE_BLINK_REVIEW.sampleAt(2050)");before=sample('paused after repeatedreplay');page.wait_for_timeout(80);after=sample('pausedstableafterRAF');assert before['elapsedMs']==after['elapsedMs']==2050 and before['renderFrameId']==after['renderFrameId']
 assert not errors and page.evaluate('window.orioleError||null') is None
 assert len({x['canvasPixelSHA256'] for x in samples})==2
 assert all(abs(c['width']-140.8)<.02 for row in samples for c in row['canvases'])
 receipt={'status':'PASS localsourceplayer numericchecks only','testedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'browser':browser.version,'deviceScaleFactor':1,'normalDeclaredCSS':140.8,'normalActualCSS':samples[0]['canvases'][0]['width'],'actualLiveClosedWindowObserved':True,'actualFinalAwakeHoldObserved':True,'samples':samples,'pageErrors':errors,'twoDisplayedRGBAHashes':sorted({x['canvasPixelSHA256'] for x in samples}),'screenshotsSaved':0,'embeddedCaptureBytes':0,'appVisited':False,'sourceArtUsefulness':'Independent visual review pending;numeric browsercheck not artapproval','canonicalZodSharpAdmission':'NOT_RUN'};browser.close()
server.shutdown();(P/'browser-verification.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({k:v for k,v in receipt.items() if k not in ['samples','twoDisplayedRGBAHashes']}))
