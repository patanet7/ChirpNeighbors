"""Numeric browser evidence only; no screenshots/captures are saved."""
from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from functools import partial
from threading import Thread
from playwright.sync_api import sync_playwright
import json,hashlib,datetime
P=Path(__file__).parent
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(P)))
Thread(target=server.serve_forever,daemon=True).start()
samples=[];errors=[]
with sync_playwright() as pw:
 browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
 page=browser.new_page(viewport={'width':1200,'height':1100},device_scale_factor=1)
 page.on('pageerror',lambda e:errors.append(str(e)))
 page.goto(f'http://127.0.0.1:{server.server_port}/review.html')
 page.wait_for_function('window.annaReady===true')
 def sample(label):
  r=page.evaluate("""async label=>{let c=document.querySelector('#normal'),rect=c.getBoundingClientRect(),bytes=c.getContext('2d').getImageData(0,0,96,96).data,hash=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes)),x=>x.toString(16).padStart(2,'0')).join('');return {label,...window.annaState,canvasPixelSHA256:hash,cssWidth:rect.width,cssHeight:rect.height,backingWidth:c.width,background:getComputedStyle(c).backgroundColor}}""",label)
  samples.append(r);return r
 page.evaluate("annaPreview.replay('look')");page.wait_for_timeout(1100)
 liveTurn=sample('actual live turned window');assert liveTurn['renderFrameId']=='anna-look-viewer-96'
 page.wait_for_timeout(1500);liveReturn=sample('actual live final awake hold');assert liveReturn['renderFrameId']=='anna-look-96' and liveReturn['terminal']
 page.evaluate('annaPreview.pause()')
 for t in [0,999,1000,1399,1400,2400,5000]:
  page.evaluate('t=>annaPreview.sampleAt(t)',t);r=sample('paused exact ms '+str(t));assert r['renderFrameId']==('anna-look-viewer-96' if 1000<=t<1400 else 'anna-look-96')
 page.click('#dark');sample('dark turned context before explicit sample');page.evaluate('annaPreview.sampleAt(1100)');dark=sample('dark turned exact1100');assert dark['background']=='rgb(23, 34, 31)'
 page.click('#light');light=sample('light turned exact1100');assert light['background']=='rgb(217, 212, 189)'
 page.click('#idle');page.wait_for_timeout(120);page.evaluate('annaPreview.pause()');page.evaluate('annaPreview.sampleAt(20000)');idle=sample('idle awake only at20000');assert idle['renderFrameId']=='anna-look-96'
 # A replay invalidates the prior animation loop; pause must remain stable thereafter.
 page.click('#look');page.click('#idle');page.click('#pause');page.evaluate('annaPreview.sampleAt(1001)');before=sample('paused after replay replacement');page.wait_for_timeout(140);after=sample('paused stable after RAF opportunity');assert before['renderFrameId']==after['renderFrameId'] and before['elapsedMs']==after['elapsedMs'] and after['clipId']=='idle'
 assert not errors and page.evaluate('window.annaError||null') is None
 assert len({r['canvasPixelSHA256'] for r in samples})==2
 assert all(abs(r['cssWidth']-64)<.02 for r in samples)
 result={'status':'PASS','testedAtUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'browser':browser.version,'normalDeclaredWorldCanvas':64,'normalActualCSSWidth':samples[0]['cssWidth'],'deviceScaleFactor':1,'samples':samples,'pageErrors':errors,'liveLookAndFinalAwakeObserved':True,'twoExactCanvasPixelHashes':sorted({r['canvasPixelSHA256'] for r in samples}),'idleOnlyAwake':True,'replayReplacementAndPausedStabilityChecked':True,'savedScreenshots':0,'savedBrowserCaptureBytes':0,'canonicalZodSharpValidation':'NOT_RUN','actualMacContract':'UNKNOWN','scope':'local source-only player numeric evidence, no app admission'}
 browser.close()
server.shutdown()
(P/'browser-verification.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k!='samples'}))
