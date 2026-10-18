"""Bounded live and boundary source-player checks, no capture bytes."""
from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from functools import partial
from threading import Thread
from playwright.sync_api import sync_playwright
import json,datetime,hashlib
P=Path(__file__).parent
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(P)));Thread(target=server.serve_forever,daemon=True).start();samples=[];errors=[]
with sync_playwright() as pw:
 browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox']);page=browser.new_page(viewport={'width':1250,'height':1000},device_scale_factor=1);page.on('pageerror',lambda e:errors.append(str(e)));page.goto(f'http://127.0.0.1:{server.server_port}/review.html');page.wait_for_function('window.doveCohortReady===true');assert page.evaluate('!document.querySelector("#replay").disabled')
 def sample(label):
  s=page.evaluate("""async label=>{const c=document.querySelector('#normal'),r=c.getBoundingClientRect(),a=c.getContext('2d').getImageData(0,0,136,80).data;return {label,...window.doveCohortState,CSS:[r.width,r.height],backing:[c.width,c.height],background:getComputedStyle(c).backgroundColor,canvasRGBAsha256:Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',a)),x=>x.toString(16).padStart(2,'0')).join('')}}""",label);samples.append(s);return s
 page.click('#replay')
 for phase in ['approach','settle','dip','wingflutter','shake','exit-preen','exact-awake-outro']:
  page.wait_for_function('p=>window.doveCohortState.phase===p',arg=phase,timeout=6000);s=sample('actual live '+phase);assert s['available'] and s['root']==[77,76] and s['rootTranslation']==[0,0] and s['contacts']==[]
 page.wait_for_function('window.doveCohortState.terminal===true',timeout=3000);last=sample('actual live terminal awake outside asset');assert last['awakeOutsideCandidateAsset']
 for ms,phase in [(0,'approach'),(600,'settle'),(1200,'dip'),(1600,'wingflutter'),(2200,'shake'),(2600,'exit-preen'),(3400,'exact-awake-outro'),(4400,'exact-awake-outro')]:
  page.evaluate('ms=>doveCohortPreview.sampleAt(ms)',ms);s=sample('paused boundary '+str(ms));assert s['phase']==phase
 page.evaluate("doveCohortPreview.select('dip')");page.click('#dark');s=sample('dark selected dip');assert s['background']=='rgb(23, 34, 31)' and s['phase']=='dip'
 page.click('#water');sample('water overlay disabled on same manual dip');assert page.evaluate('doveCohortState.phase')=='dip';page.click('#floor');sample('floor overlay disabled on same manual dip');page.click('#light');sample('light without diagnostic overlays')
 page.click('#replay');page.click('#pause');page.evaluate('doveCohortPreview.sampleAt(2601)');a=sample('paused after replay replacement');page.wait_for_timeout(100);b=sample('paused stable after RAF');assert a['elapsedMs']==b['elapsedMs'] and b['phase']=='exit-preen'
 assert not errors and page.evaluate('window.doveCohortError||null') is None and all(s['CSS']==[136,80] and s['backing']==[136,80] for s in samples)
 result={'status':'PASS local six-source proposal playback only','testedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'browser':browser.version,'samples':samples,'actualLiveSixPhasesAndSeparateAwakeOutro':True,'staticRootVerified':True,'oneShotTerminalAwakeOutsideAsset':True,'authoredEventMarkers':[0,18,36,48,66,78,102],'markersAcceptedByMac':False,'normalCSS':[136,80],'savedScreenshots':0,'savedCaptureBytes':0,'pageErrors':errors,'manifestSHA256':hashlib.sha256((P/'COHORT-SOURCE-MANIFEST.json').read_bytes()).hexdigest(),'behaviorProposalSHA256':hashlib.sha256((P/'cohort-behavior-proposal.json').read_bytes()).hexdigest(),'fullBatheAdmission':False,'geometryReviewed':False,'supportWorld':None,'MacAdmission':False}
 browser.close()
server.shutdown();(P/'browser-verification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='samples'}))
