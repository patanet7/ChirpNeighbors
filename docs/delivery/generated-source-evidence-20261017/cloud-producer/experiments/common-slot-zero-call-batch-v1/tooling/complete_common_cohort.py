from pathlib import Path
import sys,json,subprocess,functools,http.server,threading,time,hashlib
from PIL import Image
from playwright.sync_api import sync_playwright
P=Path(sys.argv[1]).resolve();assert P.is_relative_to(Path('/workspace/asset-production/experiments/common-slot-zero-call-batch-v1/species'));assert not (P/'browser-playback-receipt.json').exists(),'One technical playback run per exported cohort.'
R=Path('/workspace/runtime-contract-checkpoint8');SHARP='/opt/codex/runtimes/codex-primary-runtime/dependencies/node/node_modules/sharp/dist/index.cjs';h=json.loads((P/'source-handoff.json').read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
# Call the defining canonicalJSON function, never a copied byte/depth guard.
code="""import fs from'node:fs';import path from'node:path';import crypto from'node:crypto';import {canonicalJson,PermanentStageError} from'/workspace/runtime-contract-checkpoint8/src/lib/server/pipeline/canonical.ts';import {canonicalJson as defining,PermanentStageError as DefiningError} from'/workspace/runtime-contract-checkpoint8/src/lib/pipeline/canonical-json.ts';import sharp from'/opt/codex/runtimes/codex-primary-runtime/dependencies/node/node_modules/sharp/dist/index.cjs';if(canonicalJson!==defining||PermanentStageError!==DefiningError)throw Error('Canonical identity changed');const P=process.argv[1],sha=b=>crypto.createHash('sha256').update(b).digest('hex'),h=JSON.parse(fs.readFileSync(path.join(P,'source-handoff.json'))),receipts=[];for(const clip of h.clips){const cfg=JSON.parse(fs.readFileSync(path.join(P,'checks',clip.id,'canonical-input.json'))),frames=[];for(const f of cfg.frames){const{data}=await sharp(path.resolve(P,'checks',clip.id,f.png)).ensureAlpha().raw().toBuffer({resolveWithObject:true});frames.push({rgba:Array.from(data)})}try{let encoded=canonicalJson({canvas:cfg.canvas,frames,logicalPixelSize:cfg.logicalPixelSize,paletteLimit:cfg.paletteLimit});receipts.push({clip:clip.id,status:'PASS',actualCanonicalJSONBytes:Buffer.byteLength(encoded),canonicalSHA256:sha(encoded)})}catch(e){receipts.push({clip:clip.id,status:'FAIL',actualError:e.message,actualErrorClass:e.constructor.name})}}let compact=canonicalJson(h);fs.writeFileSync(path.join(P,'canonical-json-budget-receipt.json'),JSON.stringify({currentModuleFacadeSHA256:sha(fs.readFileSync('/workspace/runtime-contract-checkpoint8/src/lib/server/pipeline/canonical.ts')),definingModuleSHA256:sha(fs.readFileSync('/workspace/runtime-contract-checkpoint8/src/lib/pipeline/canonical-json.ts')),actualFunctionAndErrorIdentity:true,rawInputs:receipts,compactHandoff:{bytes:Buffer.byteLength(compact),SHA256:sha(compact)},scope:'Source JSON module acceptance only, not full schema, pins or runtime admission.'},null,2)+'\\n');console.log(JSON.stringify({rawInputs:receipts,compactBytes:Buffer.byteLength(compact)}));"""
run=subprocess.run(['node','--input-type=module','-e',code,str(P)],text=True,capture_output=True);assert run.returncode==0,run.stderr
# Exact APNG tuples and clock.
for clip in h['clips']:
 ap=Image.open(P/(clip['id']+'.apng'));assert ap.n_frames==3
 for i,role in enumerate(['neutral',clip['id'],'neutral']):
  ap.seek(i);im=Image.open(P/'codec-cropped'/f'{role}.png').convert('RGBA');assert ap.convert('RGBA').tobytes()==im.tobytes();assert ap.info['duration']==[2000,600,400][i]
class Handler(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(P)));threading.Thread(target=server.serve_forever,daemon=True).start();samples=[]
try:
 with sync_playwright() as pw:
  browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox']);page=browser.new_page(viewport={'width':1200,'height':1000},device_scale_factor=1);errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.goto(f'http://127.0.0.1:{server.server_port}/review.html');page.wait_for_function('window.COMMON_SLOT_PREFLIGHT?.ready');dims=page.evaluate('Array.from(document.querySelectorAll("canvas")).map(c=>({id:c.id,backing:[c.width,c.height],CSS:[c.getBoundingClientRect().width,c.getBoundingClientRect().height]}))')
  for clip in h['clips']:
   page.evaluate('(id)=>COMMON_SLOT_PREFLIGHT.select(id)',clip['id']);seeks=[]
   for tick in [0,59,60,77,78,89,90]:
    s=page.evaluate('(t)=>COMMON_SLOT_PREFLIGHT.seek(t)',tick);rgba=page.evaluate('Array.from(document.getElementById("codec-light").getContext("2d").getImageData(0,0,...COMMON_SLOT_PREFLIGHT.getState().displayStage).data)');seeks.append({'requested':tick,'state':s,'codecLightRGBAsha256':hashlib.sha256(bytes(rgba)).hexdigest()})
   page.evaluate('COMMON_SLOT_PREFLIGHT.play()');start=time.monotonic();live=[]
   for target in [100,2010,2250,2550,2650,3020]:
    while(time.monotonic()-start)*1000<target:time.sleep(.001)
    live.append({'wallElapsedMs':(time.monotonic()-start)*1000,'state':page.evaluate('COMMON_SLOT_PREFLIGHT.getState()')})
   assert [s['state']['role'] for s in seeks]==['neutral','neutral',clip['id'],clip['id'],'neutral','neutral','neutral'];assert any(s['state']['role']==clip['id'] for s in live);assert live[-1]['state']['tick']==89 and not live[-1]['state']['running'];assert seeks[0]['codecLightRGBAsha256']==seeks[4]['codecLightRGBAsha256']!=seeks[2]['codecLightRGBAsha256'];samples.append({'candidate':clip['id'],'seekSamples':seeks,'liveSamples':live})
  browser.close()
 assert not errors and all(d['backing']==h['displayStage'] and d['CSS']==h['displayStage'] for d in dims)
 receipt={'passed':True,'DPR':1,'dimensions':dims,'clips':samples,'pageErrors':errors,'APNGRGBAAndTimingExact':True,'capturesSaved':False,'sourceReadabilityVerified':None,'runtimeAdmission':False,'scope':'Live source-player numerical geometry/clock integrity, not semantic or app acceptance.'};(P/'browser-playback-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({'cohort':str(P),'browserPASS':True,'candidates':len(samples),'dimensions':dims,'JSON':json.loads((P/'canonical-json-budget-receipt.json').read_text())['rawInputs']}))
finally:server.shutdown();server.server_close()
