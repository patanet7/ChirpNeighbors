from pathlib import Path
from playwright.sync_api import sync_playwright
from PIL import Image
from fractions import Fraction
import json,hashlib,time,struct,zlib,http.server,threading,functools
P=Path(__file__).resolve().parent;start=time.perf_counter();errors=[];results=[]
class Handler(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(P)));threading.Thread(target=server.serve_forever,daemon=True).start()
try:
 with sync_playwright() as pw:
  b=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox']);page=b.new_page(viewport={'width':1200,'height':1000},device_scale_factor=1);page.on('pageerror',lambda e:errors.append(str(e)))
  page.goto(f'http://127.0.0.1:{server.server_port}/review.html');page.wait_for_function('window.NECKLINE_REVIEW?.ready')
  dims=page.evaluate('Array.from(document.querySelectorAll("canvas")).map(c=>({id:c.id,backing:[c.width,c.height],CSS:[c.getBoundingClientRect().width,c.getBoundingClientRect().height]}))');assert all(d['backing']==d['CSS']==[124,124] for d in dims)
  def sample(label):
   d=page.evaluate('({state:NECKLINE_REVIEW.getState(),pixels:Array.from(document.getElementById("chosen-light").getContext("2d").getImageData(0,0,124,124).data)})');return {'label':label,'state':d['state'],'RGBAsha256':hashlib.sha256(bytes(d['pixels'])).hexdigest()}
  for mode,handoff,ap in [('attention','source-handoff.json','attention.apng'),('head-roll','control-handoff.json','head-roll-study.apng')]:
   h=json.loads((P/handoff).read_text());clip=h['clips'][0];sch=clip['frames'];ends=[];t=0
   for f in sch:t+=f['durationTicks'];ends.extend([t-1,t])
   ticks=sorted(set([0]+ends));page.evaluate('(m)=>NECKLINE_REVIEW.select(m)',mode);samples=[]
   for tick in ticks:page.evaluate('(t)=>NECKLINE_REVIEW.seek(t)',tick);s=sample('seek:'+str(tick));samples.append(s);t=0;expected=None
   for s in samples:
    t=0
    for f in sch:
     t+=f['durationTicks']
     if s['state']['tick']<t:expected=f['frameId'];break
    assert s['state']['frameId']==expected
   assert samples[0]['RGBAsha256']==samples[-1]['RGBAsha256']
   page.evaluate('NECKLINE_REVIEW.play()');live=[sample('play')];target='look' if mode=='attention' else 'roll-minus6';page.wait_for_function('(r)=>NECKLINE_REVIEW.getState().running&&NECKLINE_REVIEW.getState().frameId===r',arg=target);live.append(sample('live-key'));page.wait_for_function('!NECKLINE_REVIEW.getState().running');live.append(sample('deadline'));assert live[-1]['state']['tick']==89 and live[-1]['state']['elapsedMs']>=3000 and live[-1]['state']['frameId']=='neutral'
   data=(P/ap).read_bytes();o=8;delays=[]
   while o<len(data):
    n=int.from_bytes(data[o:o+4],'big');typ=data[o+4:o+8];v=data[o+8:o+8+n];assert zlib.crc32(typ+v)&0xffffffff==int.from_bytes(data[o+8+n:o+12+n],'big')
    if typ==b'fcTL':x=struct.unpack('>IIIIIHHBB',v);delays.append(Fraction(x[5],x[6] or 100))
    o+=n+12
   assert delays==[Fraction(f['durationTicks'],30) for f in sch]
   im=Image.open(P/ap);frames=[]
   for i,f in enumerate(sch):
    im.seek(i);expected=Image.open(P/f'frames/{f["frameId"]}.png').convert('RGBA');assert im.convert('RGBA').tobytes()==expected.tobytes();frames.append({'index':i,'frameId':f['frameId'],'seconds':float(delays[i]),'decodedRGBAsha256':hashlib.sha256(expected.tobytes()).hexdigest()})
   results.append({'mode':mode,'ticks':[f['durationTicks'] for f in sch],'seekSamples':samples,'liveSamples':live,'APNG':{'file':ap,'SHA256':hashlib.sha256(data).hexdigest(),'decodedFramesExact':frames,'totalSeconds':float(sum(delays))}})
  controls=[]
  for angle,expected in [(-6,'roll-minus6'),(0,'neutral'),(6,'roll-plus6')]:
   page.evaluate('(a)=>NECKLINE_REVIEW.setAngle(a)',angle);s=sample('angle:'+str(angle));assert s['state']['frameId']==expected;controls.append(s)
  # A seek must cancel pending RAF so controls do not keep moving.
  page.evaluate('NECKLINE_REVIEW.play();NECKLINE_REVIEW.seek(46)');page.wait_for_timeout(80);assert page.evaluate('NECKLINE_REVIEW.getState().tick')==46
  b.close()
 assert not errors
 receipt={'PASS':True,'scope':'Actual normal-scale numerical playback, finite control selection and APNG identity/timing; no art or runtime approval','DPR':1,'dimensions':dims,'clips':results,'finiteAngleControlSamples':controls,'staleRAFCancelled':True,'pageErrors':errors,'capturesSaved':0,'verificationWallSeconds':time.perf_counter()-start,'runtimeAdmission':False};(P/'browser-apng-proof.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({'PASS':True,'clips':2,'actualAngleSelections':3,'seconds':receipt['verificationWallSeconds'],'captures':0}))
finally:server.shutdown();server.server_close()
