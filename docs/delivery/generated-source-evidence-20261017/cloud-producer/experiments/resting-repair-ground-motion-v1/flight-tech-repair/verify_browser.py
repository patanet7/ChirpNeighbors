from pathlib import Path
from PIL import Image
from playwright.sync_api import sync_playwright
import json,hashlib,http.server,functools,threading
P=Path(__file__).resolve().parent;assert not (P/'browser-proof.json').exists(),'One bounded player proof.'
h=json.loads((P/'airborne-source-handoff.json').read_text());ap=Image.open(P/'airborne-four-pose-cycle.apng');assert ap.n_frames==24
for t in range(24):
    ap.seek(t);im=Image.open(P/h['frames'][t%4]['png']).convert('RGBA');assert ap.convert('RGBA').tobytes()==im.tobytes();assert abs(ap.info['duration']-1000/30)<.001
class Handler(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(P)));threading.Thread(target=server.serve_forever,daemon=True).start()
try:
 with sync_playwright() as pw:
    br=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox']);page=br.new_page(device_scale_factor=1,viewport={'width':1200,'height':1000});errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.goto(f'http://127.0.0.1:{server.server_port}/review.html');page.wait_for_function('window.FLIGHT_TECH_REVIEW?.ready');dims=page.evaluate('Array.from(document.querySelectorAll("canvas")).map(c=>({id:c.id,backing:[c.width,c.height],CSS:[c.getBoundingClientRect().width,c.getBoundingClientRect().height]}))');assert all(d['CSS']==[64,64] for d in dims);assert all(d['backing']==([96,96] if d['id'].startswith('raw') else [64,64]) for d in dims)
    controls=[]
    for t in [0,1,2,3,4,22,23,24]:
        s=page.evaluate('(t)=>FLIGHT_TECH_REVIEW.seek(t)',t);rgba=page.evaluate('Array.from(document.getElementById("codec64-light").getContext("2d").getImageData(0,0,64,64).data)');assert s['frameId']==h['frames'][min(t,23)%4]['id'];controls.append({'requestedTick':t,'state':s,'codecLightRGBAsha256':hashlib.sha256(bytes(rgba)).hexdigest()})
    assert controls[0]['codecLightRGBAsha256']==controls[4]['codecLightRGBAsha256'];assert len({x['codecLightRGBAsha256'] for x in controls[:4]})==4
    page.evaluate('FLIGHT_TECH_REVIEW.play()');page.wait_for_function('FLIGHT_TECH_REVIEW.getState().tick>=4');live=page.evaluate('FLIGHT_TECH_REVIEW.getState()');page.wait_for_function('!FLIGHT_TECH_REVIEW.getState().running',timeout=2500);terminal=page.evaluate('FLIGHT_TECH_REVIEW.getState()');assert terminal['tick']==23 and terminal['rootTravel']==[0,0]
    page.evaluate('FLIGHT_TECH_REVIEW.play();FLIGHT_TECH_REVIEW.seek(2)');page.wait_for_timeout(100);stale=page.evaluate('FLIGHT_TECH_REVIEW.getState()');assert stale['tick']==2 and not stale['running'];br.close();assert not errors
 (P/'browser-proof.json').write_text(json.dumps({'passed':True,'DPR':1,'dimensions':dims,'sourceAPNG24FramesRGBAAndDelaysExact':True,'controls':controls,'actualLiveSample':live,'terminal':terminal,'staleRAFGuard':stale,'pageErrors':errors,'capturePayloadsSaved':False,'sourceAppearanceAccepted':False,'runtimeAdmission':False},indent=2)+'\n');print(json.dumps({'passed':True,'actualWorldCSS':[64,64],'rawBacking':[96,96],'newBacking':[64,64],'APNGFrames':24,'capturesSaved':False}))
finally:server.shutdown();server.server_close()
