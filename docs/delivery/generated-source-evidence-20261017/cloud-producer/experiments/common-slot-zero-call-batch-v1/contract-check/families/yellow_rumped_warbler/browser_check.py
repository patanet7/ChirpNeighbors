from pathlib import Path
from playwright.sync_api import sync_playwright
from PIL import Image
import json,hashlib,http.server,threading,functools,time
P=Path(__file__).resolve().parent;assert not (P/'browser-playback-receipt.json').exists(),'One bounded family playback proof only.'
class Handler(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(P)));threading.Thread(target=server.serve_forever,daemon=True).start();clips=[];errors=[]
try:
 with sync_playwright() as pw:
  browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox']);page=browser.new_page(viewport={'width':1000,'height':1000},device_scale_factor=1);page.on('pageerror',lambda e:errors.append(str(e)));page.goto(f'http://127.0.0.1:{server.server_port}/review.html');page.wait_for_function('window.FAMILY_REVIEW?.ready')
  dims=page.evaluate('Array.from(document.querySelectorAll("canvas")).map(c=>({id:c.id,backing:[c.width,c.height],CSS:[c.getBoundingClientRect().width,c.getBoundingClientRect().height]}))');assert all(d['backing']==d['CSS']==[120,120] for d in dims)
  def sample(label):
   state=page.evaluate('FAMILY_REVIEW.getState()');a=page.evaluate('Array.from(document.getElementById("light").getContext("2d").getImageData(0,0,120,120).data)');b=page.evaluate('Array.from(document.getElementById("dark").getContext("2d").getImageData(0,0,120,120).data)');return {'label':label,'state':state,'lightRGBAsha256':hashlib.sha256(bytes(a)).hexdigest(),'darkRGBAsha256':hashlib.sha256(bytes(b)).hexdigest()}
  for name,ticks in [('blink',[0,59,60,62,63,89,90]),('look',[0,59,60,77,78,89,90])]:
   page.evaluate('(name)=>FAMILY_REVIEW.select(name)',name);seek=[]
   for tick in ticks:page.evaluate('(tick)=>FAMILY_REVIEW.seek(tick)',tick);seek.append(sample('seek:'+str(tick)))
   assert [s['state']['frameId'] for s in seek]==['neutral','neutral',name,name,'neutral','neutral','neutral'];assert seek[0]['lightRGBAsha256']==seek[-1]['lightRGBAsha256']!=seek[2]['lightRGBAsha256']
   page.evaluate('FAMILY_REVIEW.play()');live=[sample('immediate-play')];assert live[0]['state']['tick']==0 and live[0]['state']['frameId']=='neutral';page.wait_for_function('(name)=>FAMILY_REVIEW.getState().running&&FAMILY_REVIEW.getState().frameId===name',arg=name,timeout=3500);live.append(sample('live-pose'));assert live[-1]['state']['frameId']==name;page.wait_for_function('!FAMILY_REVIEW.getState().running',timeout=2000);live.append(sample('deadline-stop'));assert live[-1]['state']['tick']==89 and live[-1]['state']['elapsedMs']>=3000 and live[-1]['state']['frameId']=='neutral';clips.append({'clip':name,'seekSamples':seek,'liveSamples':live})
  browser.close()
 assert not errors
 receipt={'passed':True,'DPR':1,'dimensions':dims,'clips':clips,'pageErrors':errors,'capturesSaved':False,'browserCaptureFiles':0,'APNGRGBAAndTimingExact':'See verification.json independent decoded frame assertions','sourceReadabilityVerified':None,'runtimeAdmission':False,'scope':'Actual source viewer geometry, frame identities, exact neutral return and full3000ms clock only. No Mac or semantic acceptance.'};(P/'browser-playback-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({'passed':True,'clips':len(clips),'seekSamples':sum(len(c['seekSamples']) for c in clips),'liveSamples':sum(len(c['liveSamples']) for c in clips),'captureFiles':0}))
finally:server.shutdown();server.server_close()
