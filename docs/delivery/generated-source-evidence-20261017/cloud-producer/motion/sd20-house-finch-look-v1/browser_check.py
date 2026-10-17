from pathlib import Path
import threading,http.server,socketserver,functools,json
from playwright.sync_api import sync_playwright
P=Path(__file__).parent
class Quiet(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
s=socketserver.TCPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(P)));threading.Thread(target=s.serve_forever,daemon=True).start();samples=[];errors=[]
with sync_playwright() as pl:
 b=pl.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox']);page=b.new_page(viewport={'width':1200,'height':1000},device_scale_factor=1);page.on('pageerror',lambda e:errors.append(str(e)));page.goto(f'http://127.0.0.1:{s.server_address[1]}/review.html');page.wait_for_function('window.FINCH_LOOK_REVIEW?.ready')
 def snap(label):
  v=page.evaluate('''async()=>({state:FINCH_LOOK_REVIEW.getState(),panels:await Promise.all(['light','dark'].map(async id=>{let c=document.getElementById(id),bytes=c.getContext('2d').getImageData(0,0,c.width,c.height).data;let digest=await crypto.subtle.digest('SHA-256',bytes);return{id,width:c.width,height:c.height,cssContentWidth:parseFloat(getComputedStyle(c).width),cssContentHeight:parseFloat(getComputedStyle(c).height),rgbaSHA256:Array.from(new Uint8Array(digest)).map(v=>v.toString(16).padStart(2,'0')).join('')}}))})''');v['label']=label;samples.append(v)
 for tick in [0,29,30,35,41,42,71]:page.evaluate('(t)=>FINCH_LOOK_REVIEW.seek(t)',tick);snap('seek:'+str(tick))
 page.evaluate('FINCH_LOOK_REVIEW.play()')
 for ms in [150,950,350,1100]:page.wait_for_timeout(ms);snap('live-playback')
 page.wait_for_function('FINCH_LOOK_REVIEW.getState().tick===71&&!FINCH_LOOK_REVIEW.getState().running',timeout=6000);snap('stopped');assert not errors;assert all(p['cssContentWidth']==192 and p['cssContentHeight']==128 for r in samples for p in r['panels']);b.close()
s.shutdown();receipt={'status':'PASS bounded numeric source-viewer check','deviceScaleFactor':1,'worldToCSS':1,'sourceCanvasCSS':96,'samples':samples,'pageErrors':errors,'browserCaptureFiles':0,'appVisited':False,'nativeCalls':1,'qualification':'Numeric clocks/hash/dimensions only;source images inspected separately,not actualMacyard/continuous-motionapproval.'};(P/'browser-verification.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({'samples':len(samples),'pageErrors':errors,'nativeCalls':1,'captures':0}))
