from pathlib import Path
from PIL import Image
from playwright.sync_api import sync_playwright
import sys,json,hashlib,http.server,functools,threading
D=Path(__file__).resolve().parent/sys.argv[1];h=json.loads((D/'family-handoff.json').read_text());N=h['displayStage'][0]
assert not (D/'browser-apng-proof.json').exists(),'One bounded browser run only.'
for c in [c for c in h['clips'] if c['id']!='idle']:
 for kind in ['raw','codec']:
    ap=Image.open(D/(kind+'-'+c['id']+'.apng'));assert ap.n_frames==3
    for i,role in enumerate(c['roles']):
        f=next(f for f in h['frames'] if f['role']==role);ap.seek(i);im=Image.open(D/(f['rawPNG'] if kind=='raw' else f['png'])).convert('RGBA');assert ap.convert('RGBA').tobytes()==im.tobytes();assert abs(ap.info['duration']-c['durationTicks'][i]*1000/30)<.001
class Handler(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(D)));threading.Thread(target=server.serve_forever,daemon=True).start()
try:
 with sync_playwright() as pw:
    br=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox']);page=br.new_page(device_scale_factor=1,viewport={'width':1100,'height':900});errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.goto(f'http://127.0.0.1:{server.server_port}/review.html');page.wait_for_function('window.REPAIR_REVIEW?.ready');dims=page.evaluate('Array.from(document.querySelectorAll("canvas")).map(c=>({id:c.id,backing:[c.width,c.height],CSS:[c.getBoundingClientRect().width,c.getBoundingClientRect().height]}))');assert all(x['backing']==[N,N] and x['CSS']==[N,N] for x in dims);samples=[]
    for c in [c for c in h['clips'] if c['id']!='idle']:
        page.evaluate('(id)=>REPAIR_REVIEW.select(id)',c['id']);ticks=[0,c['durationTicks'][0]-1,c['durationTicks'][0],sum(c['durationTicks'][:2])-1,sum(c['durationTicks'][:2]),89];ss=[]
        for t in ticks:
            st=page.evaluate('(t)=>REPAIR_REVIEW.seek(t)',t);rgba=page.evaluate('Array.from(document.getElementById("codec-light").getContext("2d").getImageData(0,0,...REPAIR_REVIEW.getState().displayStage).data)');ss.append({'state':st,'codecLightRGBAsha256':hashlib.sha256(bytes(rgba)).hexdigest()})
        assert [x['state']['role'] for x in ss]==['neutral','neutral',c['id'],c['id'],'neutral','neutral'];assert ss[0]['codecLightRGBAsha256']==ss[4]['codecLightRGBAsha256']!=ss[2]['codecLightRGBAsha256']
        page.evaluate('REPAIR_REVIEW.play()');page.wait_for_function('(id)=>REPAIR_REVIEW.getState().role===id',arg=c['id'],timeout=4000);live=page.evaluate('REPAIR_REVIEW.getState()');page.wait_for_function('!REPAIR_REVIEW.getState().running',timeout=4000);terminal=page.evaluate('REPAIR_REVIEW.getState()');assert terminal['tick']==89 and terminal['role']=='neutral';samples.append({'clip':c['id'],'boundarySamples':ss,'actualLivePose':live,'actualLiveTerminal':terminal})
    page.evaluate('REPAIR_REVIEW.play();REPAIR_REVIEW.select("blink");REPAIR_REVIEW.seek(60)');page.wait_for_timeout(100);stale=page.evaluate('REPAIR_REVIEW.getState()');assert stale['tick']==60 and not stale['running']
    br.close();assert not errors
 (D/'browser-apng-proof.json').write_text(json.dumps({'passed':True,'APNGExactRGBAAndTiming':True,'dimensions':dims,'DPR':1,'clips':samples,'staleRAFGuard':stale,'pageErrors':errors,'captureBytesSaved':False,'readabilityAcceptance':None,'scope':'Numerical whole-source player geometry/clock integrity, not independent blink semantics or full runtime admission.'},indent=2)+'\n');print(json.dumps({'species':D.name,'passed':True,'actualNormalCSS':N,'liveClips':2,'captureBytesSaved':False}))
finally:server.shutdown();server.server_close()
