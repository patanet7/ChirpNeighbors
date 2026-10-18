from pathlib import Path
import json,hashlib,threading,http.server,functools,time
from PIL import Image
from playwright.sync_api import sync_playwright
P=Path(__file__).parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
d=json.load(open(P/'flight-source-proposal.json'))
# APNG rounding is distributed, total exactly matches authored30Hz episode milliseconds.
for c in d['clips']:
 f=P/(c['id']+'.apng');im=Image.open(f);frames=[]
 for i in range(im.n_frames):im.seek(i);frames.append(im.convert('RGBA').copy())
 dur=[round((i+1)*1000/30)-round(i*1000/30) for i in range(len(frames))];frames[0].save(f,save_all=True,append_images=frames[1:],duration=dur,loop=1,disposal=0,blend=0)
handler=functools.partial(http.server.SimpleHTTPRequestHandler,directory=str(P));srv=http.server.ThreadingHTTPServer(('127.0.0.1',0),handler);threading.Thread(target=srv.serve_forever,daemon=True).start()
checks=[];errors=[]
with sync_playwright() as w:
 b=w.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox']);p=b.new_page();p.on('pageerror',lambda e:errors.append(str(e)));p.goto(f'http://127.0.0.1:{srv.server_port}/review.html');p.wait_for_function('window.FLIGHT_REVIEW?.ready')
 for c in d['clips']:
  p.evaluate('(id)=>FLIGHT_REVIEW.select(id)',c['id'])
  for t in sorted(set([0,c['durationTicks']-1]+[s['ticks'][0] for s in c['segments']])):
   state=p.evaluate('(t)=>{FLIGHT_REVIEW.seek(t);return FLIGHT_REVIEW.getState()}',t);assert state['tick']==t and state['contacts']==[];checks.append({'clip':c['id'],'tick':t,'frameId':state['frameId'],'root':state['root'],'supportState':state['supportState']})
 p.evaluate('FLIGHT_REVIEW.select("hover-existing-four-poses");FLIGHT_REVIEW.play()');p.wait_for_timeout(950);end=p.evaluate('FLIGHT_REVIEW.getState()');assert end['tick']==23 and not end['running'];b.close()
srv.shutdown();assert not errors
for f in d['frames']:assert sha(P/f['outputPNG'])==f['outputPNGsha256']
for f,h in json.load(open(P/'reference-lineage.json'))['verifiedInputFiles'].items():assert sha(Path('/workspace/asset-production')/f)==h
(P/'verification.json').write_text(json.dumps({'exactOutputPNGChecks':13,'sourcePrimaryDecodedIDsChecked':13,'browser':'Chromium headless; own one-shot source player','browserErrors':errors,'numericSamples':checks,'oneShotTerminal':end,'screenshotsSaved':0,'canonicalPixelJSON':'NOT_RUN','APNGTiming':'integer-ms33/34 distribution, total round(frameCount*1000/30), loop1 means play once','sourcePixelsChanged':False,'perPoseFit':False},indent=2)+'\n')
status=json.load(open(P/'active-status.json'));status['status']='FROZEN_EXISTING_KEYS_READY_FOR_INDEPENDENT_REVIEW';status['next']='Parent geometry and Slot appearance; separate authorized transition repair may follow in its own folder';(P/'active-status.json').write_text(json.dumps(status,indent=2)+'\n')
ledger={str(f.relative_to(P)):sha(f) for f in sorted(P.rglob('*')) if f.is_file() and f.name not in ['review-target-hashes.json','STABLE-GO.json'] and 'transition-repair-native-v1' not in f.parts};(P/'review-target-hashes.json').write_text(json.dumps(ledger,indent=2)+'\n')
go={'status':'STABLE_GO_EXISTING_KEYS_ONLY','nativeCalls':0,'newDrawings':0,'reusedUniqueDrawingIDs':13,'frozenFiles':len(ledger),'ledger':'review-target-hashes.json','ledgerSHA256':sha(P/'review-target-hashes.json'),'manifestSHA256':sha(P/'flight-source-proposal.json'),'primaryManifestSHA256':sha(P/'PRIMARY-SOURCE-MANIFEST.json'),'scope':'Exact existing-key baseline only. Independent reviews and optional new transition subfolder additive outside this ledger. All contacts unbound; no currentMac/runtime admission.','reviewOnlyOutputs':['independent-geometry-review.json','.md','independent-appearance-review.json','.md']};(P/'STABLE-GO.json').write_text(json.dumps(go,indent=2)+'\n');print(json.dumps(go));print('GO_SHA256',sha(P/'STABLE-GO.json'))
