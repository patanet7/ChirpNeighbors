"""Bounded deterministic/local live source-family evidence, no browser capture bytes."""
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
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox']);page=b.new_page(viewport={'width':1250,'height':1000},device_scale_factor=1);page.on('pageerror',lambda e:errors.append(str(e)));page.goto(f'http://127.0.0.1:{server.server_port}/review.html');page.wait_for_function('window.goldfinchFamilyReady===true')
 def sample(label):
  x=page.evaluate("""async label=>{let canvases={};for(const id of ['legacy','source','runtime']){const c=document.getElementById(id),r=c.getBoundingClientRect(),a=c.getContext('2d').getImageData(0,0,c.width,c.height).data;canvases[id]={CSS:[r.width,r.height],backing:[c.width,c.height],background:getComputedStyle(c).backgroundColor,canvasRGBAsha256:Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',a)),x=>x.toString(16).padStart(2,'0')).join('')}}return{label,...familyPreview.getState(),canvases}}""",label);samples.append(x);return x
 sample('live neutral-only idle');page.click('#blink');page.wait_for_function("familyPreview.getState().phase==='blink'",timeout=4000);sample('live inherited100ms blink');page.wait_for_function("familyPreview.getState().phase==='neutral'",timeout=2000);sample('live inherited blink return');page.click('#look');page.wait_for_function("familyPreview.getState().phase==='look'",timeout=4000);sample('live inherited200ms look');page.wait_for_function("familyPreview.getState().phase==='neutral'",timeout=2000);sample('live inherited look return')
 for clip,times in [('idle',[0,4000]),('blink',[1999,2000,2099,2100,3000]),('look',[1999,2000,2199,2200,3000])]:
  page.evaluate('c=>familyPreview.setClip(c)',clip)
  for t in times:page.evaluate('t=>familyPreview.sampleAt(t)',t);sample(clip+' exact paused '+str(t))
 page.evaluate("familyPreview.setClip('look');familyPreview.sampleAt(2001)");a=page.evaluate('JSON.stringify(familyPreview.getState())');page.wait_for_timeout(80);assert a==page.evaluate('JSON.stringify(familyPreview.getState())')
 page.click('#dark');dark=sample('dark paused look without overlay');assert dark['canvases']['runtime']['background']=='rgb(23, 34, 31)'
 page.click('#overlay');overlay=sample('dark technical image proxies enabled');assert overlay['technicalOverlays'] and overlay['contacts']==[] and not overlay['geometryReviewed']
 page.click('#light');sample('light technical image proxies enabled');page.click('#overlay');sample('light overlays disabled')
 page.click('#blink');page.click('#look');page.click('#pause');page.evaluate('familyPreview.sampleAt(2001)');x=sample('replay replaced and paused');page.wait_for_timeout(100);y=sample('paused stable after RAF');assert x['elapsedMs']==y['elapsedMs'] and y['phase']=='look'
 assert not errors and page.evaluate('window.goldfinchFamilyError||null') is None and all(s['canvases']['source']['CSS']==[102,102] and s['canvases']['runtime']['CSS']==[102,102] and s['root']==[61,80] for s in samples)
 r={'status':'PASS local zero-call source-family playback only','testedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'browser':b.version,'samples':samples,'trueSourceAndRuntimeCSS':[102,102],'legacyActualCSS':samples[0]['canvases']['legacy']['CSS'],'liveBlinkLookAndReturns':True,'deterministicGetStateAtPausedTimestamp':True,'technicalContactAnchorOverlaysTested':True,'replayReplacementPausedRAF':True,'savedScreenshots':0,'savedCaptureBytes':0,'pageErrors':errors,'familyManifestSHA256':hashlib.sha256((P/'family-source-manifest.json').read_bytes()).hexdigest(),'canonicalInputSHA256':hashlib.sha256((P/'canonical-input.json').read_bytes()).hexdigest(),'structuralReceiptSHA256':hashlib.sha256((P/'structural-receipt.json').read_bytes()).hexdigest(),'independentReview':'PENDING','geometryReviewed':False,'supportWorld':None,'currentMacAdmission':False};b.close()
server.shutdown();(P/'browser-verification.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:v for k,v in r.items()if k!='samples'}))
