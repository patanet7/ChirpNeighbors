"""Numeric source-player checks only; no capture files."""
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
 browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox']);page=browser.new_page(viewport={'width':1300,'height':1000},device_scale_factor=1);page.on('pageerror',lambda e:errors.append(str(e)));page.goto(f'http://127.0.0.1:{server.server_port}/review.html');page.wait_for_function('window.crowRuntimeReady===true')
 def sample(label):
  s=page.evaluate("""async label=>{const c=document.querySelector('#normal'),s=document.querySelector('#source'),r=c.getBoundingClientRect(),raw=c.getContext('2d').getImageData(0,0,186,186).data;return {label,...window.crowRuntimeState,normalCSS:r.width,sourceCSS:s.getBoundingClientRect().width,backing:[c.width,c.height],background:getComputedStyle(c).backgroundColor,pixelSHA256:Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',raw)),x=>x.toString(16).padStart(2,'0')).join('')}}""",label);samples.append(s);return s
 a=sample('first actual RAF static idle');page.wait_for_timeout(180);b=sample('live authored clock advancing');assert b['globalTick']>a['globalTick']
 for t in [0,3999,4000,8000]:
  page.evaluate('t=>crowRuntimePreview.sampleAt(t)',t);s=sample('paused boundary '+str(t));assert s['loopTick']==int(t*30/1000)%120 and s['frameIndex']==0
 page.click('#dark');dark=sample('actual dark context');assert dark['background']=='rgb(23, 34, 31)'
 page.click('#light');sample('actual light context')
 page.click('#reset');page.click('#reset');page.click('#pause');page.evaluate('crowRuntimePreview.sampleAt(4010)');a=sample('after replay replacement pause');page.wait_for_timeout(150);b=sample('paused stable after RAF');assert a['elapsedMs']==b['elapsedMs']
 assert len({s['pixelSHA256'] for s in samples})==1 and all(s['normalCSS']==186 for s in samples) and not errors
 assert abs(samples[0]['sourceCSS']-185.88535031847132)<.02
 receipt={'status':'PASS source-only local player','testedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'browser':browser.version,'samples':samples,'oneStaticFrame':True,'authoredIdleTicks':120,'tickRate':30,'firstRAFAndLiveClock':True,'loopBoundariesAndReplayPause':True,'savedScreenshots':0,'savedCaptureBytes':0,'pageErrors':errors,'canonicalRuntimeZod':'NOT_RUN','MacAppBinding':False}
 browser.close()
server.shutdown();(P/'browser-verification.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({k:v for k,v in receipt.items() if k!='samples'}))
