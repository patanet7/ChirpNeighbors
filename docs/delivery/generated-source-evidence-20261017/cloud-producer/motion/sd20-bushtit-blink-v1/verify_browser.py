from pathlib import Path
import json,threading,functools,http.server,hashlib,time
from playwright.sync_api import sync_playwright
P=Path(__file__).parent
class Handler(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(P)));threading.Thread(target=server.serve_forever,daemon=True).start()
try:
 with sync_playwright() as pw:
  browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox']);page=browser.new_page(viewport={'width':1180,'height':1000});errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.goto(f'http://127.0.0.1:{server.server_port}/review.html');page.wait_for_function('window.BUSHTIT_REVIEW?.ready===true');dimensions=page.evaluate("['light','dark'].map(id=>{const c=document.getElementById(id),r=c.getBoundingClientRect();return{id,source:[c.width,c.height],displayCSS:[r.width,r.height]}})");seek=[]
  for tick in [0,59,60,62,63,89,90]:
   state=page.evaluate('(t)=>window.BUSHTIT_REVIEW.seek(t)',tick);hashes={}
   for canvas in ['light','dark']:
    pixels=page.evaluate('(id)=>Array.from(document.getElementById(id).getContext("2d").getImageData(0,0,96,96).data)',canvas);hashes[canvas]=hashlib.sha256(bytes(pixels)).hexdigest()
   seek.append({'requestedTick':tick,'state':state,'renderedCanvasRGBAsha256':hashes})
  page.evaluate('window.BUSHTIT_REVIEW.play()');start=time.monotonic();playback=[]
  for target in [100,1950,2020,2070,2150,2950,3100]:
   while (time.monotonic()-start)*1000<target:time.sleep(.003)
   state=page.evaluate('window.BUSHTIT_REVIEW.getState()');playback.append({'wallElapsedMs':round((time.monotonic()-start)*1000,1),'state':state})
  page.evaluate('window.BUSHTIT_REVIEW.pause()');browser.close()
 passed=not errors and all(abs(d['displayCSS'][0]-96/1.5)<.02 for d in dimensions) and set(s['state']['phase'] for s in playback)=={'open','closed'} and len(set(s['renderedCanvasRGBAsha256']['light'] for s in seek))==2 and all(s['state']['rootOutputXY']==[57,75] for s in seek+playback)
 receipt={'browser':'Chromium','transport':'loopbackHTTP','pageErrors':errors,'declaredWorldSizeCanvasDimensions':dimensions,'seekSamples':seek,'actualPlaybackSamples':playback,'observedPlaybackPhases':sorted(set(s['state']['phase'] for s in playback)),'rootTransformAlwaysUnchanged':True,'scope':'Actual sourceviewer clock/canvas samples atdeclaredCSSworldsize/lightdark. Numericalstate+rawRGBAhashes only;no browsercaptures stored,embeddedoruploaded. Not actualappyard or continuoushumanvisual review.','passed':passed};(P/'browser-verification.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({'passed':passed,'pageErrors':errors,'dimensions':dimensions,'seekCount':len(seek),'playbackSamples':[(s['wallElapsedMs'],s['state']['phase'],s['state']['tick']) for s in playback]},indent=2));assert passed
finally:server.shutdown();server.server_close()
