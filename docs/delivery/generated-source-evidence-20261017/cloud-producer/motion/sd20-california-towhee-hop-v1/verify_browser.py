from pathlib import Path
import json,threading,functools,http.server,hashlib,time
from playwright.sync_api import sync_playwright
P=Path(__file__).parent
class Handler(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(P)));threading.Thread(target=server.serve_forever,daemon=True).start()
try:
 with sync_playwright() as pw:
  browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox']);page=browser.new_page(viewport={'width':1200,'height':1000});errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.goto(f'http://127.0.0.1:{server.server_port}/review.html');page.wait_for_function('window.TOWHEE_REVIEW?.ready===true');seek=[]
  for tick in [0,6,9,12,13,16,17,20,28]:
   state=page.evaluate('(t)=>window.TOWHEE_REVIEW.seek(t)',tick);pixels=page.evaluate('Array.from(document.getElementById("yard").getContext("2d").getImageData(0,0,360,180).data)');seek.append({'tick':tick,'pose':state['pose'],'rootWorldXY':state['rootWorldXY'],'planted':state['planted'],'supportErrorWorldUnits':state['supportBoundaryErrorWorldUnits'],'renderedCanvasRGBAsha256':hashlib.sha256(bytes(pixels)).hexdigest()})
  page.evaluate('window.TOWHEE_REVIEW.play()');start=time.monotonic();playback=[]
  for target in [100,220,330,470,590,750,1050]:
   while (time.monotonic()-start)*1000<target:time.sleep(.003)
   s=page.evaluate('window.TOWHEE_REVIEW.getState()');playback.append({'wallElapsedMs':round((time.monotonic()-start)*1000,1),'tick':s['tick'],'pose':s['pose'],'rootWorldXY':s['rootWorldXY'],'planted':s['planted']})
  done=page.evaluate('({state:window.TOWHEE_REVIEW.getState(),playing:window.TOWHEE_REVIEW.getPlaying()})');page.wait_for_timeout(150);hold=page.evaluate('window.TOWHEE_REVIEW.getState()');browser.close()
 receipt={'browser':'Chromium','transport':'loopbackHTTP','pageErrors':errors,'seekSamples':seek,'actualPlaybackSamples':playback,'finalHoldAtLandedRoot':done['state']['rootWorldXY']==[166,130] and hold['rootWorldXY']==[166,130] and not done['playing'],'observedPlaybackPoses':sorted(set(s['pose'] for s in playback)),'scope':'Actual customsourceviewer canvas render/clock samples;numericstate+rawRGBAhashes only,no browser screenshots stored/embedded/uploaded. Not actual yardrenderer or continuoushuman review.','passed':not errors and len(set(s['renderedCanvasRGBAsha256'] for s in seek))>=5 and done['state']['tick']==28 and not done['playing']}
 (P/'browser-verification.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2));assert receipt['passed']
finally:server.shutdown();server.server_close()
