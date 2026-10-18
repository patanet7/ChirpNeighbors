from pathlib import Path
from playwright.sync_api import sync_playwright
from PIL import Image
from fractions import Fraction
import hashlib,json,struct,zlib,time,http.server,threading,functools
P=Path(__file__).resolve().parent;h=json.loads((P/'source-handoff.json').read_text());sch=h['clips'][0]['frames'];start=time.perf_counter();errors=[]
class Handler(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
s=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(P)));threading.Thread(target=s.serve_forever,daemon=True).start()
try:
 with sync_playwright() as pw:
  b=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox']);page=b.new_page(viewport={'width':1200,'height':1000},device_scale_factor=1);page.on('pageerror',lambda e:errors.append(str(e)));page.goto(f'http://127.0.0.1:{s.server_port}/review.html');page.wait_for_function('window.BATH_SOURCE_REVIEW?.ready')
  dims=page.evaluate('Array.from(document.querySelectorAll("canvas")).map(c=>({id:c.id,backing:[c.width,c.height],CSS:[c.getBoundingClientRect().width,c.getBoundingClientRect().height]}))');assert all(d['backing']==d['CSS']==[192,192] for d in dims)
  def sample(label):
   d=page.evaluate('({state:BATH_SOURCE_REVIEW.getState(),pixels:Array.from(document.getElementById("codec-light").getContext("2d").getImageData(0,0,192,192).data)})');return {'label':label,'state':d['state'],'codecLightRGBAsha256':hashlib.sha256(bytes(d['pixels'])).hexdigest()}
  samples=[]
  for t in [0,11,12,29,30,41,42,53,54,77,78,89,90]:
   page.evaluate('(t)=>BATH_SOURCE_REVIEW.seek(t)',t);x=sample('seek:'+str(t));samples.append(x);end=0
   for f in sch:
    end+=f['durationTicks']
    if x['state']['tick']<end:assert x['state']['frameId']==f['frameId'];break
  assert samples[0]['codecLightRGBAsha256']==samples[-1]['codecLightRGBAsha256']
  page.evaluate('BATH_SOURCE_REVIEW.play()');live=[sample('play')]
  for role in ['lowered-ready','wing-ruffle','shake-wing-state','folded-settle']:
   page.wait_for_function('(r)=>BATH_SOURCE_REVIEW.getState().running&&BATH_SOURCE_REVIEW.getState().frameId===r',arg=role);live.append(sample('live:'+role))
  page.wait_for_function('!BATH_SOURCE_REVIEW.getState().running');live.append(sample('deadline'));assert live[-1]['state']['tick']==89 and live[-1]['state']['frameId']=='neutral' and live[-1]['state']['elapsedMs']>=3000
  page.evaluate('BATH_SOURCE_REVIEW.play();BATH_SOURCE_REVIEW.seek(35)');page.wait_for_timeout(80);assert page.evaluate('BATH_SOURCE_REVIEW.getState().tick')==35;b.close()
 assert not errors
 ap=[]
 for name,folder in [('raw-source-proposal.apng','raw192'),('codec-source-proposal.apng','frames')]:
  data=(P/name).read_bytes();o=8;delays=[]
  while o<len(data):
   n=int.from_bytes(data[o:o+4],'big');typ=data[o+4:o+8];v=data[o+8:o+8+n];assert zlib.crc32(typ+v)&0xffffffff==int.from_bytes(data[o+8+n:o+12+n],'big')
   if typ==b'fcTL':x=struct.unpack('>IIIIIHHBB',v);delays.append(Fraction(x[5],x[6] or 100))
   o+=n+12
  assert delays==[Fraction(f['durationTicks'],30) for f in sch]
  im=Image.open(P/name);pf=[]
  for i,f in enumerate(sch):
   im.seek(i);ex=Image.open(P/f'{folder}/{f["frameId"]}.png').convert('RGBA');assert im.convert('RGBA').tobytes()==ex.tobytes();pf.append({'index':i,'frameId':f['frameId'],'seconds':float(delays[i]),'decodedRGBAsha256':hashlib.sha256(ex.tobytes()).hexdigest()})
  ap.append({'path':name,'SHA256':hashlib.sha256(data).hexdigest(),'frames':pf,'totalSeconds':3,'exactAuthoredTicks':[12,18,12,12,24,12],'tickRate':30})
 proof={'PASS':True,'scope':'Normal192CSS numerical pixel identity/clock/APNG proof only, no accepted bathing/physical/runtime claim','dimensions':dims,'seekSamples':samples,'liveSamples':live,'staleRAFCancelled':True,'APNGs':ap,'pageErrors':errors,'capturesSaved':0,'wallSeconds':time.perf_counter()-start,'runtimeAdmission':False};(P/'browser-apng-proof.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps({'PASS':True,'seekSamples':len(samples),'liveSamples':len(live),'APNGs':2,'captures':0,'seconds':proof['wallSeconds']}))
finally:s.shutdown();s.server_close()
