from pathlib import Path
from playwright.sync_api import sync_playwright
from PIL import Image
from fractions import Fraction
import json,hashlib,http.server,threading,functools,time,struct,zlib
P=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
h=json.loads((P/'source-handoff.json').read_text()); started=time.perf_counter(); errors=[]
class Handler(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(P)))
threading.Thread(target=server.serve_forever,daemon=True).start()
try:
 with sync_playwright() as pw:
  browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
  page=browser.new_page(viewport={'width':1200,'height':1100},device_scale_factor=1);page.on('pageerror',lambda e:errors.append(str(e)))
  page.goto(f'http://127.0.0.1:{server.server_port}/review.html');page.wait_for_function('window.ATTENTION_REPAIR_REVIEW?.ready')
  dims=page.evaluate('Array.from(document.querySelectorAll("canvas")).map(c=>({id:c.id,backing:[c.width,c.height],CSS:[c.getBoundingClientRect().width,c.getBoundingClientRect().height]}))')
  assert all(d['backing']==d['CSS']==[124,124] for d in dims)
  page.evaluate("ATTENTION_REPAIR_REVIEW.select('look')");samples=[]
  def sample(label):
   d=page.evaluate('({state:ATTENTION_REPAIR_REVIEW.getState(),pixels:Array.from(document.getElementById("codec-light").getContext("2d").getImageData(0,0,124,124).data)})')
   return {'label':label,'state':d['state'],'codecLightRGBAsha256':hashlib.sha256(bytes(d['pixels'])).hexdigest()}
  for tick in [0,59,60,77,78,89,90]:
   page.evaluate('(t)=>ATTENTION_REPAIR_REVIEW.seek(t)',tick);samples.append(sample('seek:'+str(tick)))
  assert [s['state']['frameId'] for s in samples]==['neutral','neutral','look','look','neutral','neutral','neutral']
  assert samples[0]['codecLightRGBAsha256']==samples[-1]['codecLightRGBAsha256']!=samples[2]['codecLightRGBAsha256']
  page.evaluate('ATTENTION_REPAIR_REVIEW.play()');live=[sample('play')]
  page.wait_for_function("ATTENTION_REPAIR_REVIEW.getState().running&&ATTENTION_REPAIR_REVIEW.getState().frameId==='look'")
  live.append(sample('live-look'));page.wait_for_function('!ATTENTION_REPAIR_REVIEW.getState().running');live.append(sample('deadline'))
  assert live[-1]['state']['tick']==89 and live[-1]['state']['frameId']=='neutral' and live[-1]['state']['elapsedMs']>=3000
  browser.close()
 assert not errors
 apng=P/'look.apng';b=apng.read_bytes();o=8;fc=[]
 while o<len(b):
  n=int.from_bytes(b[o:o+4],'big');typ=b[o+4:o+8];data=b[o+8:o+8+n]
  assert zlib.crc32(typ+data)&0xffffffff==int.from_bytes(b[o+8+n:o+12+n],'big')
  if typ==b'fcTL':
   v=struct.unpack('>IIIIIHHBB',data);fc.append({'width':v[1],'height':v[2],'delayNumerator':v[5],'delayDenominator':v[6] or 100,'seconds':float(Fraction(v[5],v[6] or 100))})
  o+=n+12
 assert [Fraction(f['delayNumerator'],f['delayDenominator']) for f in fc]==[Fraction(60,30),Fraction(18,30),Fraction(12,30)]
 im=Image.open(apng);frameproof=[]
 for i,role in enumerate(['neutral','look','neutral']):
  im.seek(i);expected=Image.open(P/f'frames/{role}.png').convert('RGBA');assert im.convert('RGBA').tobytes()==expected.tobytes()
  frameproof.append({'index':i,'role':role,'exactPNGsha256':sha(P/f'frames/{role}.png'),'decodedRGBAsha256':hashlib.sha256(expected.tobytes()).hexdigest()})
 receipt={'passed':True,'scope':'Copied baseline playback and exact APNG identity/timing only; no new export, codec run, independent art verdict or runtime admission','normalWorld':h['fullWorldCanvas'],'transparentCeilStage':[124,124],'dimensions':dims,'seekSamples':samples,'liveSamples':live,'pageErrors':errors,'APNG':{'file':'look.apng','SHA256':sha(apng),'fcTL':fc,'authoredTicks':[60,18,12],'tickRate':30,'totalSeconds':3,'exactFrameProof':frameproof},'observedVerificationWallSeconds':time.perf_counter()-started,'capturesSaved':0,'runtimeAdmission':False}
 (P/'arm-a-browser-apng-proof.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({'PASS':True,'seconds':receipt['observedVerificationWallSeconds'],'liveSamples':len(live),'seekSamples':len(samples),'captures':0}))
finally:server.shutdown();server.server_close()
