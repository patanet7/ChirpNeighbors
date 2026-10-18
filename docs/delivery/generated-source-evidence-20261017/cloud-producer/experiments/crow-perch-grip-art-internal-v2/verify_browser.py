from pathlib import Path
from playwright.sync_api import sync_playwright
from PIL import Image
import json,hashlib,http.server,threading,functools,time,struct,zlib
P=Path(__file__).resolve().parent;start=time.perf_counter();errors=[]
class Handler(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
s=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(P)));threading.Thread(target=s.serve_forever,daemon=True).start()
try:
 with sync_playwright() as pw:
  b=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox']);page=b.new_page(viewport={'width':1200,'height':1100},device_scale_factor=1);page.on('pageerror',lambda e:errors.append(str(e)));page.goto(f'http://127.0.0.1:{s.server_port}/review.html');page.wait_for_function('window.CROW_GRIP_REVIEW?.ready')
  dims=page.evaluate('Array.from(document.querySelectorAll("canvas")).map(c=>({id:c.id,backing:[c.width,c.height],CSS:[c.getBoundingClientRect().width,c.getBoundingClientRect().height]}))');assert all(d['backing']==[192,192] and abs(d['CSS'][0]-185.88535031847132)<.02 and abs(d['CSS'][1]-185.88535031847132)<.02 for d in dims)
  def sample(label):
   d=page.evaluate('({state:CROW_GRIP_REVIEW.getState(),pixels:Array.from(document.getElementById("new-light").getContext("2d").getImageData(0,0,192,192).data)})');return {'label':label,'state':d['state'],'RGBAsha256':hashlib.sha256(bytes(d['pixels'])).hexdigest()}
  samples=[]
  for t in [0,45,89,90]:page.evaluate('(t)=>CROW_GRIP_REVIEW.seek(t)',t);samples.append(sample('seek:'+str(t)))
  assert len({x['RGBAsha256'] for x in samples})==1
  page.evaluate('CROW_GRIP_REVIEW.play()');live=[sample('play')];page.wait_for_timeout(100);live.append(sample('live-hold'));page.wait_for_function('!CROW_GRIP_REVIEW.getState().running');live.append(sample('deadline'));assert live[-1]['state']['tick']==89 and live[-1]['state']['elapsedMs']>=3000
  page.evaluate('CROW_GRIP_REVIEW.play();CROW_GRIP_REVIEW.seek(45)');page.wait_for_timeout(80);assert page.evaluate('CROW_GRIP_REVIEW.getState().tick')==45;b.close()
 assert not errors
 data=(P/'STATIC-grip-study.apng').read_bytes();o=8;fc=[]
 while o<len(data):
  n=int.from_bytes(data[o:o+4],'big');typ=data[o+4:o+8];v=data[o+8:o+8+n];assert zlib.crc32(typ+v)&0xffffffff==int.from_bytes(data[o+8+n:o+12+n],'big')
  if typ==b'fcTL':fc.append(struct.unpack('>IIIIIHHBB',v))
  o+=n+12
 assert len(fc)==1 and fc[0][5:7]==(90,30)
 im=Image.open(P/'STATIC-grip-study.apng');raw=Image.open(P/'grip-study192.png').convert('RGBA');assert im.convert('RGBA').tobytes()==raw.tobytes()
 gif=Image.open(P/'STATIC-grip-study.gif');assert gif.n_frames==1
 proof={'PASS':True,'scope':'Static sourceclock/layout/APNGRGBA proof only; not art/anatomical/support/currentMacapproval','DPR':1,'dimensions':dims,'seekSamples':samples,'liveSamples':live,'uniqueRGBAStates':1,'authoredTicks':90,'tickRate':30,'APNG':{'fcTLCount':1,'delayNumerator':90,'delayDenominator':30,'exactRGBAFrame':True,'SHA256':hashlib.sha256(data).hexdigest()},'GIF':{'frames':1,'qualification':'Palette/alpha-lossy preview only, not primaryRGBAidentity'},'pageErrors':errors,'staleRAFCancelled':True,'capturesSaved':0,'wallSeconds':time.perf_counter()-start,'perchingAnimationGain':0,'landingGain':0,'runtimeAdmission':False};(P/'browser-static-proof.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps({'PASS':True,'actualCSS':dims[0]['CSS'],'staticStates':1,'captures':0,'seconds':proof['wallSeconds']}))
finally:s.shutdown();s.server_close()
