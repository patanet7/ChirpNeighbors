from pathlib import Path
import hashlib,json,threading,http.server,functools
from playwright.sync_api import sync_playwright
P=Path(__file__).parent;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();records=[]
for q in [P,P/'transition-repair-native-v1']:
 html=(q/'review.html').read_text();old="$('seek').oninput=()=>{pause();tick=Number($('seek').value);draw()}";new="$('seek').oninput=()=>{const requestedTick=Number($('seek').value);pause();tick=requestedTick;draw()}";assert old in html;(q/'review-controls-fixed.html').write_text(html.replace(old,new));records.append({'packet':str(q.relative_to(P)),'originalFrozenViewerSHA256':sha(q/'review.html'),'fixedViewer':'review-controls-fixed.html','fixedViewerSHA256':sha(q/'review-controls-fixed.html'),'change':'Capture range input value before pause() redraw overwrites DOM. No source/frame/manifest/clock/root/trajectory changes.'})
class Quiet(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
srv=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(P)));threading.Thread(target=srv.serve_forever,daemon=True).start()
with sync_playwright() as w:
 b=w.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox']);page=b.new_page()
 for rec in records:
  prefix='' if rec['packet']=='.' else rec['packet']+'/'
  page.goto(f'http://127.0.0.1:{srv.server_port}/'+prefix+'review-controls-fixed.html');page.wait_for_function('window.FLIGHT_REVIEW?.ready');s=page.evaluate("()=>{const e=document.getElementById('seek');e.value='9';e.dispatchEvent(new Event('input'));return FLIGHT_REVIEW.getState()}");assert s['tick']==9;rec['actualRangeEventTickVerified']=s['tick']
 b.close()
srv.shutdown()
for q in [P,P/'transition-repair-native-v1']:
 for f,h in json.load(open(q/'review-target-hashes.json')).items():assert sha(q/f)==h
(P/'viewer-control-annex.json').write_text(json.dumps({'reason':'Frozen viewer range control reset requested value during pause redraw; additive alternate viewer fixes only UI control race. Exact API seek/play worked in original frozen viewer.','records':records,'all52Plus33FrozenInputsUnchanged':True,'screenshots':0,'artStatusChanged':False},indent=2)+'\n');print(json.dumps(records));print('annexSHA',sha(P/'viewer-control-annex.json'))
