from pathlib import Path
import json,threading,http.server,socketserver,functools
from playwright.sync_api import sync_playwright
P=Path(__file__).parent
class Quiet(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
s=socketserver.TCPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(P)));threading.Thread(target=s.serve_forever,daemon=True).start();samples=[];errors=[]
with sync_playwright() as pl:
 b=pl.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox']);page=b.new_page(viewport={'width':1200,'height':1100},device_scale_factor=1);page.on('pageerror',lambda e:errors.append(str(e)));page.goto(f'http://127.0.0.1:{s.server_address[1]}/review.html');page.wait_for_function('window.SPARROW_LOOK_REVIEW?.ready')
 def snap(label):
  page.wait_for_function("Array.from(document.querySelectorAll('img.bird')).every(x=>x.complete&&x.naturalWidth===96)");v=page.evaluate('''async()=>({state:SPARROW_LOOK_REVIEW.getState(),panels:await Promise.all(['light','dark'].map(async id=>{let p=document.getElementById(id),im=p.querySelector('img.bird'),r=im.getBoundingClientRect(),q=p.getBoundingClientRect();let c=document.createElement('canvas');c.width=96;c.height=96;c.getContext('2d').drawImage(im,0,0);let raw=c.getContext('2d').getImageData(0,0,96,96).data,d=await crypto.subtle.digest('SHA-256',raw);return{id,outputPNG:im.getAttribute('src'),natural:[im.naturalWidth,im.naturalHeight],CSSCanvas:[r.width,r.height],CSSPositionInPanel:[r.x-q.x-1,r.y-q.y-1],sourceOutputCanvasRGBAsha256:Array.from(new Uint8Array(d)).map(v=>v.toString(16).padStart(2,'0')).join('')}}))})''');v['label']=label;samples.append(v)
 for tick in [0,29,30,35,41,42,71]:page.evaluate('(t)=>SPARROW_LOOK_REVIEW.seek(t)',tick);snap('seek:'+str(tick))
 page.evaluate('SPARROW_LOOK_REVIEW.play()')
 for ms in [150,950,350,1100]:page.wait_for_timeout(ms);snap('live-playback')
 page.wait_for_function('SPARROW_LOOK_REVIEW.getState().tick===71&&!SPARROW_LOOK_REVIEW.getState().running',timeout=6000);snap('stopped');assert not errors;assert all(p['CSSCanvas']==[123.421875,123.421875] for r in samples for p in r['panels']);b.close()
s.shutdown();r={'status':'PASS bounded source-viewer clock/dimension checks;art held assessment unchanged','deviceScaleFactor':1,'normalNominalCSS':123.42857142857143,'normalActualCSS':123.421875,'samples':samples,'pageErrors':errors,'browserCaptureFiles':0,'appVisited':False,'nativeCalls':1,'qualification':'Source-image pixels sampled via offscreen96canvas only for hashes;no browser captures retained. JSterminalfirsttick71vs72nominal sourceclip,notMaccompletionproof.'};(P/'browser-verification.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'samples':len(samples),'actualCSS':123.421875,'errors':errors,'captures':0}))
