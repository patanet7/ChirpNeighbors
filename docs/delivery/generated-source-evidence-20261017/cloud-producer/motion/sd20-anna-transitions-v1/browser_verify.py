from pathlib import Path
import threading,http.server,socketserver,functools,json,hashlib,time
from playwright.sync_api import sync_playwright
P=Path(__file__).parent;handler=functools.partial(http.server.SimpleHTTPRequestHandler,directory=str(P))
class Quiet(handler.func):
 def log_message(self,*a):pass
server=socketserver.TCPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(P)));threading.Thread(target=server.serve_forever,daemon=True).start();records=[];errors=[]
with sync_playwright() as pl:
 b=pl.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox']);page=b.new_page(viewport={'width':1200,'height':1000},device_scale_factor=1);page.on('pageerror',lambda e:errors.append(str(e)));page.goto(f'http://127.0.0.1:{server.server_address[1]}/review.html');page.wait_for_function('window.ANNA_C_REVIEW?.ready')
 def snapshot(label):
  v=page.evaluate('''()=>({state:ANNA_C_REVIEW.getState(),canvases:['light','dark'].map(id=>{let c=document.getElementById(id);return{id,width:c.width,height:c.height,cssWidth:c.getBoundingClientRect().width,cssHeight:c.getBoundingClientRect().height,rgba:Array.from(c.getContext('2d').getImageData(0,0,c.width,c.height).data)}})})''')
  for c in v['canvases']:c['rawRGBAsha256']=hashlib.sha256(bytes(c.pop('rgba'))).hexdigest()
  v['label']=label;records.append(v)
 for n,ts in [('motion-manifest.json',[0,1,2,3,18,30,31,32,33,53,54,59,60,68]),('landing-reach-study.json',[0,11]),('arrival-support-proof.json',[0,23]),('takeoff-release-study.json',[0,11]),('perched-reference-proof.json',[0,23])]:
  page.evaluate('(n)=>ANNA_C_REVIEW.selectStudy(n)',n)
  for t in ts:page.evaluate('(t)=>ANNA_C_REVIEW.seek(t)',t);snapshot(n+':'+str(t))
 page.evaluate("ANNA_C_REVIEW.selectStudy('motion-manifest.json');ANNA_C_REVIEW.play()")
 for delay in [130,370,540,650,700]:page.wait_for_timeout(delay);snapshot('timer-play')
 page.wait_for_function('ANNA_C_REVIEW.getState().tick===68 && !ANNA_C_REVIEW.getState().running',timeout=10000);snapshot('timer-final-conditional');final=page.evaluate('ANNA_C_REVIEW.getState()');assert final['tick']==68 and not final['running'];assert not errors
 assert all(c['cssWidth']==242 and c['cssHeight']==182 for r in records for c in r['canvases']) # CSS border 1px each side, content240x180
 b.close()
server.shutdown();receipt={'status':'PASS loopback source viewer numeric samples','browser':'Chromium via Python Playwright','deviceScaleFactor':1,'CSSContentPanel':[240,180],'worldUnitCSSPixels':1,'sourceCanvasCSSPixels':64,'samples':records,'pageErrors':errors,'capturedImages':0,'embeddedBrowserCaptures':False,'actualAppVisited':False,'qualification':'Bounded numeric source-viewer observations;not continuous human visual or app/physics approval.'};(P/'browser-numeric-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({'status':receipt['status'],'samples':len(records),'finalTick':final['tick'],'errors':errors,'captures':0}))
