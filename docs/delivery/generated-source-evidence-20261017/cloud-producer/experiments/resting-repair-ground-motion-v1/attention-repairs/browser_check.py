from pathlib import Path
from playwright.sync_api import sync_playwright
import json,hashlib,http.server,threading,functools,sys
P=Path(__file__).resolve().parent/sys.argv[1];assert not (P/'browser-playback-receipt.json').exists(),'One bounded technical proof only.';h=json.loads((P/'source-handoff.json').read_text())
class Handler(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(P)));threading.Thread(target=server.serve_forever,daemon=True).start();samples=[];errors=[]
try:
 with sync_playwright() as pw:
  browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox']);page=browser.new_page(viewport={'width':1200,'height':1100},device_scale_factor=1);page.on('pageerror',lambda e:errors.append(str(e)));page.goto(f'http://127.0.0.1:{server.server_port}/review.html');page.wait_for_function('window.ATTENTION_REPAIR_REVIEW?.ready');dims=page.evaluate('Array.from(document.querySelectorAll("canvas")).map(c=>({id:c.id,backing:[c.width,c.height],CSS:[c.getBoundingClientRect().width,c.getBoundingClientRect().height]}))');assert all(d['backing']==d['CSS']==h['displayStage'] for d in dims)
  def sample(label):
   state=page.evaluate('ATTENTION_REPAIR_REVIEW.getState()');values=page.evaluate('Array.from(document.getElementById("codec-light").getContext("2d").getImageData(0,0,...ATTENTION_REPAIR_REVIEW.getState().displayStage).data)');return {'label':label,'state':state,'codecLightRGBAsha256':hashlib.sha256(bytes(values)).hexdigest()}
  for clip in [c for c in h['clips'] if c['id'] in ['blink','look']]:
   name=clip['id'];dur=[f['durationTicks'] for f in clip['frames']];total=sum(dur);ticks=[0,dur[0]-1,dur[0],dur[0]+dur[1]-1,dur[0]+dur[1],total-1,total];page.evaluate('(name)=>ATTENTION_REPAIR_REVIEW.select(name)',name);seek=[]
   for tick in ticks:page.evaluate('(tick)=>ATTENTION_REPAIR_REVIEW.seek(tick)',tick);seek.append(sample('seek:'+str(tick)))
   assert [s['state']['frameId'] for s in seek]==['neutral','neutral',name,name,'neutral','neutral','neutral'];assert seek[0]['codecLightRGBAsha256']==seek[-1]['codecLightRGBAsha256']!=seek[2]['codecLightRGBAsha256'];page.evaluate('ATTENTION_REPAIR_REVIEW.play()');live=[sample('immediate-play')];assert live[0]['state']['tick']==0;page.wait_for_function('(name)=>ATTENTION_REPAIR_REVIEW.getState().running&&ATTENTION_REPAIR_REVIEW.getState().frameId===name',arg=name,timeout=5000);live.append(sample('live-pose'));page.wait_for_function('!ATTENTION_REPAIR_REVIEW.getState().running',timeout=3000);live.append(sample('deadline-stop'));assert live[-1]['state']['tick']==total-1 and live[-1]['state']['elapsedMs']>=total*1000/30 and live[-1]['state']['frameId']=='neutral';samples.append({'clip':name,'durationTicks':dur,'seekSamples':seek,'liveSamples':live})
  browser.close()
 assert not errors
 receipt={'passed':True,'DPR':1,'dimensions':dims,'clips':samples,'pageErrors':errors,'capturesSaved':False,'browserCaptureFiles':0,'sourceReadabilityVerified':None,'runtimeAdmission':False,'scope':'Actual normal-scale source viewer numerical image identity, layout and authored clock proof only; independent appearance, geometry and current live engine remain separate.'};(P/'browser-playback-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({'species':sys.argv[1],'passed':True,'clips':len(samples),'seekSamples':sum(len(c['seekSamples']) for c in samples),'liveSamples':sum(len(c['liveSamples']) for c in samples),'captures':0}))
finally:server.shutdown();server.server_close()
