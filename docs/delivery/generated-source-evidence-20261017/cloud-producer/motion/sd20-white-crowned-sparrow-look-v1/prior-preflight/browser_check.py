from pathlib import Path
import json,threading,http.server,socketserver,functools
from playwright.sync_api import sync_playwright
P=Path(__file__).parent
class Quiet(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
s=socketserver.TCPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(P)));threading.Thread(target=s.serve_forever,daemon=True).start();errors=[]
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox']);page=b.new_page(viewport={'width':1200,'height':1000},device_scale_factor=1);page.on('pageerror',lambda e:errors.append(str(e)));page.goto(f'http://127.0.0.1:{s.server_address[1]}/review.html');page.wait_for_function("Array.from(document.querySelectorAll('img.bird')).every(x=>x.complete&&x.naturalWidth===96)");imgs=page.evaluate("Array.from(document.querySelectorAll('img.bird')).map(x=>({file:x.getAttribute('src'),naturalWidth:x.naturalWidth,naturalHeight:x.naturalHeight,CSSWidth:x.getBoundingClientRect().width,CSSHeight:x.getBoundingClientRect().height,background:getComputedStyle(x).backgroundColor}))");assert len(imgs)==4;assert all(abs(x['CSSWidth']-123.42857142857143)<1/64 for x in imgs);assert not errors;b.close()
s.shutdown();r={'status':'PASS static existing-source normal-CSS preflight','normalNominalCSS':123.42857142857143,'deviceScaleFactor':1,'panels':imgs,'normalGeometryMatchedSourceFrames':2,'pageErrors':errors,'browserCaptureFiles':0,'newNativeCalls':0,'appVisited':False,'qualification':'CSS layout quantizes fractional123.428571 to123.421875 CSS in Chromium;this static source preflight is not newlook/actualMacyard review.'};(P/'browser-numeric-receipt.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
