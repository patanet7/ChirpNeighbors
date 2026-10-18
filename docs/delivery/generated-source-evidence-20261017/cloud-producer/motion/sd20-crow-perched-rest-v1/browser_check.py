from pathlib import Path
import threading,http.server,socketserver,functools,json
from playwright.sync_api import sync_playwright
P=Path(__file__).parent
class Quiet(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
s=socketserver.TCPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(P)));threading.Thread(target=s.serve_forever,daemon=True).start();samples=[];errors=[]
with sync_playwright() as pl:
 b=pl.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox']);page=b.new_page(viewport={'width':1300,'height':1100},device_scale_factor=1);page.on('pageerror',lambda e:errors.append(str(e)));page.goto(f'http://127.0.0.1:{s.server_address[1]}/review.html');page.wait_for_function('window.CROW_PERCH_REVIEW?.ready')
 def snap(label):
  page.wait_for_function("Array.from(document.querySelectorAll('.bird')).every(x=>x.complete&&x.naturalWidth===192)");r=page.evaluate('''async()=>({state:CROW_PERCH_REVIEW.getState(),panels:await Promise.all(['light','dark'].map(async id=>{let p=document.getElementById(id),im=p.querySelector('.bird'),r=im.getBoundingClientRect(),q=p.getBoundingClientRect();let c=document.createElement('canvas');c.width=192;c.height=192;c.getContext('2d').drawImage(im,0,0);let d=await crypto.subtle.digest('SHA-256',c.getContext('2d').getImageData(0,0,192,192).data);return{id,CSSCanvas:[r.width,r.height],natural:[im.naturalWidth,im.naturalHeight],positionInPanel:[r.x-q.x-1,r.y-q.y-1],proxyVisible:getComputedStyle(p.querySelector('.proxy')).display!=='none',sourceOutputRGBAhash:Array.from(new Uint8Array(d)).map(v=>v.toString(16).padStart(2,'0')).join('')}}))})''');r['label']=label;samples.append(r)
 for clip in ['perching','idle']:
  page.evaluate('(c)=>CROW_PERCH_REVIEW.select(c)',clip)
  for tick in [0,45,89]:page.evaluate('(t)=>CROW_PERCH_REVIEW.seek(t)',tick);snap(clip+':'+str(tick))
 page.evaluate("CROW_PERCH_REVIEW.select('perching');CROW_PERCH_REVIEW.play()")
 for ms in [120,1100,1100,850]:page.wait_for_timeout(ms);snap('live-static-clock')
 page.wait_for_function('CROW_PERCH_REVIEW.getState().tick===89&&!CROW_PERCH_REVIEW.getState().running',timeout=6000);snap('stopped');assert not errors;assert all(p['CSSCanvas']==[185.875,185.875] for r in samples for p in r['panels']);assert all(not p['proxyVisible'] for r in samples if r['state']['clip']=='idle' for p in r['panels']);b.close()
s.shutdown();receipt={'status':'PASS bounded source static-clock/CSS checks;grip/art still unreviewed','deviceScaleFactor':1,'nominalCSS':185.88535031847132,'actualCSS':185.875,'samples':samples,'pageErrors':errors,'browserCaptureFiles':0,'appVisited':False,'nativeCalls':1,'qualification':'SourceRGBA sampled onlyforhashes,no browser capturebytes;staticposeclock90nominalticks/firsttick89terminal isnotanimatedcycleorMaccompletionproof.'};(P/'browser-verification.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({'samples':len(samples),'actualCSS':185.875,'pageErrors':errors,'captures':0}))
