from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from functools import partial
from threading import Thread
from playwright.sync_api import sync_playwright
import json,hashlib,datetime
P=Path(__file__).parent
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(P)));Thread(target=server.serve_forever,daemon=True).start();samples=[];errors=[]
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox']);p=b.new_page(viewport={'width':1250,'height':1000},device_scale_factor=1);p.on('pageerror',lambda e:errors.append(str(e)));p.goto(f'http://127.0.0.1:{server.server_port}/review.html');p.wait_for_function('window.phoebeFamilyReady===true')
 def sample(label):
  s=p.evaluate("""async label=>{let canvases={};for(const id of ['legacy','source','runtime']){const c=document.getElementById(id),r=c.getBoundingClientRect(),a=c.getContext('2d').getImageData(0,0,c.width,c.height).data;canvases[id]={CSS:[r.width,r.height],backing:[c.width,c.height],background:getComputedStyle(c).backgroundColor,rawSHA256:Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',a)),x=>x.toString(16).padStart(2,'0')).join('')}}return {label,...window.phoebeFamilyState,canvases}}""",label);samples.append(s);return s
 sample('initial live awake idle');p.click('#blink');p.wait_for_function("window.phoebeFamilyState.phase==='blink'",timeout=4500);sample('actual live100ms closure');p.wait_for_function("window.phoebeFamilyState.phase==='neutral'",timeout=2000);sample('actual live awake return')
 p.click('#look');p.wait_for_function("window.phoebeFamilyState.phase==='look'",timeout=2000);sample('actual live turned look');p.wait_for_function('window.phoebeFamilyState.terminal===true',timeout=2500);sample('actual live look terminal awake')
 for clip,times in [('idle',[0,90000]),('blink',[2999,3000,3099,3100,6100]),('look',[999,1000,1399,1400,2400])]:
  p.evaluate('id=>phoebeFamilyPreview.replay(id)',clip)
  for t in times:p.evaluate('ms=>phoebeFamilyPreview.sampleAt(ms)',t);sample(clip+' paused '+str(t))
 p.click('#dark');p.evaluate('phoebeFamilyPreview.sampleAt(1100)');s=sample('actual dark turned');assert s['phase']=='look' and s['canvases']['runtime']['background']=='rgb(23, 34, 31)';p.click('#light');sample('actual light turned')
 p.click('#look');p.click('#blink');p.click('#pause');p.evaluate('phoebeFamilyPreview.sampleAt(3001)');a=sample('paused after replay replacement');p.wait_for_timeout(100);z=sample('paused stable RAF');assert a['elapsedMs']==z['elapsedMs'] and z['phase']=='blink'
 assert not errors and p.evaluate('window.phoebeFamilyError||null') is None
 assert all(s['canvases']['source']['CSS']==[91,91] and s['canvases']['runtime']['CSS']==[91,91] and abs(s['canvases']['legacy']['CSS'][0]-90.94736842105263)<.02 and s['root']==[54,71]for s in samples)
 r={'status':'PASS local existing-family playback only','testedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'browser':b.version,'samples':samples,'actual91CSS':True,'legacyActualCSS':samples[0]['canvases']['legacy']['CSS'],'actualLiveClosureAndReturn':True,'actualLiveLookAndFinalAwake':True,'separateIdleBlinkLookClocks':True,'replayReplacementPause':True,'savedScreenshots':0,'savedCaptureBytes':0,'pageErrors':errors,'familyManifestSHA256':hashlib.sha256((P/'family-source-manifest.json').read_bytes()).hexdigest(),'sourceVisualDisposition':'PENDING independentreview','MacAdmission':False};b.close()
server.shutdown();(P/'browser-verification.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:v for k,v in r.items()if k!='samples'}))
