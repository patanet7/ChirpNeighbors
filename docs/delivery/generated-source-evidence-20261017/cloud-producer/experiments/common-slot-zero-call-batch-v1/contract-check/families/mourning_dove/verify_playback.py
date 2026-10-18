from pathlib import Path
from PIL import Image
from playwright.sync_api import sync_playwright
import json,hashlib,http.server,functools,threading,time
P=Path(__file__).resolve().parent
assert not (P/'browser-apng-proof.json').exists(),'One bounded playback proof only.'
h=json.loads((P/'family-handoff.json').read_text());proof=[]
for c in [x for x in h['clips'] if x['id']!='idle']:
    ap=Image.open(P/(c['id']+'.apng'));assert ap.n_frames==3
    for i,role in enumerate(c['roles']):
        ap.seek(i);im=Image.open(P/'frames'/f'{role}.png').convert('RGBA');assert ap.convert('RGBA').tobytes()==im.tobytes();assert abs(ap.info['duration']-c['durationTicks'][i]*1000/30)<.001
class Handler(http.server.SimpleHTTPRequestHandler):
    def log_message(self,*a):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(P)));threading.Thread(target=server.serve_forever,daemon=True).start()
try:
 with sync_playwright() as pw:
    browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox']);page=browser.new_page(device_scale_factor=1,viewport={'width':1200,'height':1000});errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.goto(f'http://127.0.0.1:{server.server_port}/review.html');page.wait_for_function('window.FAMILY_REVIEW?.ready');dims=page.evaluate('Array.from(document.querySelectorAll("canvas")).map(c=>({id:c.id,CSS:[c.getBoundingClientRect().width,c.getBoundingClientRect().height],backing:[c.width,c.height]}))');assert all(x['CSS']==[192,192] and x['backing']==[192,192] for x in dims)
    for c in [x for x in h['clips'] if x['id']!='idle']:
        page.evaluate('(id)=>FAMILY_REVIEW.select(id)',c['id']);boundary=[0,c['durationTicks'][0]-1,c['durationTicks'][0],sum(c['durationTicks'][:2])-1,sum(c['durationTicks'][:2]),89];samples=[]
        for t in boundary:
            state=page.evaluate('(t)=>FAMILY_REVIEW.seek(t)',t);data=page.evaluate('Array.from(document.getElementById("codec-light").getContext("2d").getImageData(0,0,192,192).data)');samples.append({'state':state,'codecLightRGBAsha256':hashlib.sha256(bytes(data)).hexdigest()})
        assert [s['state']['role'] for s in samples]==['neutral','neutral',c['id'],c['id'],'neutral','neutral'];assert samples[0]['codecLightRGBAsha256']==samples[4]['codecLightRGBAsha256']!=samples[2]['codecLightRGBAsha256']
        page.evaluate('FAMILY_REVIEW.play()');page.wait_for_function('(role)=>FAMILY_REVIEW.getState().role===role',arg=c['id'],timeout=4000);livePose=page.evaluate('FAMILY_REVIEW.getState()');page.wait_for_function('!FAMILY_REVIEW.getState().running',timeout=4000);terminal=page.evaluate('FAMILY_REVIEW.getState()');assert terminal['tick']==89 and terminal['role']=='neutral';proof.append({'clip':c['id'],'boundarySamples':samples,'actualLivePose':livePose,'actualLiveTerminal':terminal})
    # Old RAF callbacks must not advance a newly selected paused state.
    page.evaluate('FAMILY_REVIEW.play();FAMILY_REVIEW.select("look");FAMILY_REVIEW.seek(60)');page.wait_for_timeout(100);stale=page.evaluate('FAMILY_REVIEW.getState()');assert stale['tick']==60 and not stale['running'] and stale['role']=='look'
    page.evaluate('FAMILY_REVIEW.select("idle")');idle=page.evaluate('FAMILY_REVIEW.getState()');assert idle['role']=='neutral' and idle['durationTicks']==[90]
    browser.close();assert not errors
 report={'passed':True,'APNGThreeFramesRGBAAndTimingExact':True,'DPR':1,'canvasDimensions':dims,'clips':proof,'staleRAFGuard':stale,'idleState':idle,'pageErrors':errors,'capturesSaved':False,'scope':'Numerical source-player selection/timing/geometry integrity only; independent readability/support/runtime admission pending.'};(P/'browser-apng-proof.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':True,'clips':len(proof),'capturesSaved':False,'CSS':[192,192]}))
finally:server.shutdown();server.server_close()
