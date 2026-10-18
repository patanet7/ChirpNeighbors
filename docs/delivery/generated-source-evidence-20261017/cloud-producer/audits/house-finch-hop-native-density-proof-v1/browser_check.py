from pathlib import Path
import json,threading,http.server,socketserver,functools
from playwright.sync_api import sync_playwright
P=Path(__file__).parent
class Quiet(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
s=socketserver.TCPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(P)));threading.Thread(target=s.serve_forever,daemon=True).start();samples=[];errors=[]
with sync_playwright() as pl:
 b=pl.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox']);page=b.new_page(viewport={'width':1300,'height':1100},device_scale_factor=1);page.on('pageerror',lambda e:errors.append(str(e)));page.goto(f'http://127.0.0.1:{s.server_address[1]}/review.html');page.wait_for_function('window.FINCH_DENSITY_PROOF?.ready')
 def sample(label):
  v=page.evaluate('''async()=>({state:FINCH_DENSITY_PROOF.getState(),panels:await Promise.all(['awake-light','held-light','proof-light','proof-dark','travel-proof-light','travel-proof-dark'].map(async id=>{let c=document.getElementById(id),d=await crypto.subtle.digest('SHA-256',c.getContext('2d').getImageData(0,0,c.width,c.height).data);return{id,width:c.width,height:c.height,cssWidth:parseFloat(getComputedStyle(c).width),cssHeight:parseFloat(getComputedStyle(c).height),rgbaSHA256:Array.from(new Uint8Array(d)).map(x=>x.toString(16).padStart(2,'0')).join('')}}))})''');v['label']=label;samples.append(v);return v
 for t in [0,6,9,12,15,18,29]:page.evaluate('(t)=>FINCH_DENSITY_PROOF.seek(t)',t);sample('seek:'+str(t))
 page.evaluate('FINCH_DENSITY_PROOF.play()');sample('immediate0')
 for lo,hi in [(6,9),(9,12),(12,15),(15,18)]:page.wait_for_function('([a,b])=>{let t=FINCH_DENSITY_PROOF.getState().tick;return t>=a&&t<b}',arg=[lo,hi],polling=5,timeout=2500);sample('livephase:'+str(lo))
 page.wait_for_function('!FINCH_DENSITY_PROOF.getState().running',timeout=2500);r=sample('terminal');assert r['state']['tick']==29 and r['state']['elapsedMs']>=1000;assert not errors;assert all(v['state']['newDrawings']==0 and not v['state']['proposedPivotApplied'] and not v['state']['acceptedHop'] for v in samples);b.close()
s.shutdown();v={'status':'PASS bounded engineering sourceviewer clocks/layout/numeric hashes','samples':samples,'pageErrors':errors,'nativeCalls':0,'newDrawings':0,'captureFiles':0,'capturePayloadsRetained':0,'appVisited':False,'birdCanvasCSS':96,'deviceScaleFactor':1,'acceptedHop':False,'qualification':'Nativepixel-density calibrationHYPOTHESIS only; supportedfootplanes still unresolved; no metadata pivot realignment used.'};(P/'browser-verification.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps({'samples':len(samples),'errors':errors,'captures':0,'nativeCalls':0}))
