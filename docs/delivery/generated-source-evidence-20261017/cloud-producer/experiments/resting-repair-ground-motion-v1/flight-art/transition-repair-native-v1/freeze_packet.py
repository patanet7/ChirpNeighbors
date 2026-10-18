from pathlib import Path
import json,hashlib,threading,http.server,functools
from PIL import Image
from playwright.sync_api import sync_playwright
P=Path(__file__).parent;B=P.parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,d):(P/n).write_text(json.dumps(d,indent=2)+'\n')
D=json.load(open(P/'flight-source-proposal.json'));probeDefs={'weighted-preload':[[58,89],[66,89]],'push-off-release':[[44,89],[50,85]],'near-contact-fold':[[63,78],[68,71]],'supported-settle':[[50,75],[60,75]]};probes=[]
for f in D['frames'][-4:]:
 im=Image.open(P/f['outputPNG']).convert('RGBA');ps=[]
 for x,y in probeDefs[f['pose']]:
  rgba=list(im.getpixel((x,y)));assert rgba[3]>0;ps.append({'pixel':[x,y],'RGBA':rgba,'worldAtIllustrativeBodyRoot80_122_6667':[80+(x-54)/1.5,122.6666666667+(y-68)/1.5],'meaning':'manual visible claw/toe-region pixel diagnostic, NOT accepted sole/contact/weight;1–2outputpx and ownership uncertainty'})
 probes.append({'pose':f['pose'],'proposedPixels':ps,'contacts':[],'supportWorld':None,'geometryReviewed':False})
save('contact-proposals.json',{'formula':'W=R+(q-p)/density','sourceDensity':1.5,'fixedCanvasPivot':[54,68],'intendedSharedToePlaneOutputY':79,'actualSourceProposals':probes,'warning':'Do not pin these pixels to a plane to assert physical support. No perpose compensation was applied. Source placement mismatch remains visible.'})
# Direct source equality, IDs, prompt and unchanged baseline.
for f in D['frames'][-4:]:
 im=Image.open(P/f['sourcePNG']).convert('RGBA');rid='frame.sha256.'+hashlib.sha256(f'RGBA8;{im.width}x{im.height};'.encode()+im.tobytes()).hexdigest();assert rid==f['primarySourceFrameId'];assert sha(P/f['outputPNG'])==f['outputPNGsha256']
args=json.load(open(P/'native-call-arguments.json'));assert args['tool']=='image_gen.imagegen';assert args['arguments']['prompt'].encode()==(P/'prompt.txt').read_bytes()
for n,h in json.load(open(B/'review-target-hashes.json')).items():assert sha(B/n)==h,n
class Quiet(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
handler=functools.partial(Quiet,directory=str(B));srv=http.server.ThreadingHTTPServer(('127.0.0.1',0),handler);threading.Thread(target=srv.serve_forever,daemon=True).start();errors=[];samples=[]
with sync_playwright() as w:
 b=w.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox']);p=b.new_page();p.on('pageerror',lambda e:errors.append(str(e)));p.goto(f'http://127.0.0.1:{srv.server_port}/transition-repair-native-v1/review.html');p.wait_for_function('window.FLIGHT_REVIEW?.ready')
 for c in D['clips']:
  p.evaluate('(id)=>FLIGHT_REVIEW.select(id)',c['id'])
  for t in sorted(set([0,c['durationTicks']-1]+[s['ticks'][0] for s in c['segments']])):
   s=p.evaluate('(t)=>{FLIGHT_REVIEW.seek(t);return FLIGHT_REVIEW.getState()}',t);assert s['tick']==t;samples.append(s)
 p.evaluate('FLIGHT_REVIEW.select("new-four-common-origin-held");FLIGHT_REVIEW.play()');p.wait_for_timeout(950);end=p.evaluate('FLIGHT_REVIEW.getState()');assert end['tick']==23 and not end['running'];b.close()
srv.shutdown();assert not errors
save('verification.json',{'requestCount':1,'actualReturnedDrawings':4,'newPrimaryDecodedIDsVerified':4,'literalNativePromptBytesVerified':True,'baseline52TargetsUnchanged':True,'browserErrors':errors,'browserNumericSamples':samples,'oneShotTerminal':end,'screenshotsSaved':0,'sourceAdmission':'UNREVIEWED_SOURCE','runtimePixelJSON':'NOT_RUN','physicalSupport':'NOT_APPROVED','currentMac':'NOT_TESTED','APNGTiming':'rounded cumulative ms33/34, totalround(N*1000/30), one-shot'})
(P/'README.md').write_text('''# Anna native transition bridge attempt\n\nExactly one native edit returned four actual new drawings in a1254square RGBA atlas. The original is unchanged. Four exact627square cells partition every original pixel; primary IDs use decodedRGBA8+dimensions. Every cell receives the same direct whole-canvas floor-center627→96 byteRGBA nearest export. No perpose fitting, translation, body rescale, warp, alpha cleanup, repaint, toe snapping or retry occurred.\n\nNew poses retain the male green/rose identity and real body/wing/leg changes, but source framing/body scale and foot placement differ from the existing family. Preload’s visible toes are aroundrow89 versus intended79; supported settle’s around75. Reach remains high-wing; settle is nearly fully folded, so the requested intermediate fold is weak. These are source failures with the outputs retained, not four useful accepted transitions. The two terminal joins remain HELD pending independent actual64world review.\n\n`review.html` draws exact96outputs at64CSS/world using density1.5, fixed pivot54,68. Existing output PNGs are referenced unchanged from the frozen parent baseline. Clocks are30Hz half-open tick segments, one-shot with terminal hold. Actual new poses are separate from authored root trajectories. APNG previews are generated-art presentation derivatives with one shared96→64 sample, not browser captures.\n\n`contact-proposals.json` records manually selected positive visible toe/claw pixels and their uncertain meaning. Contacts remain[], geometryReviewed=false, supportWorld=null; no weighted support or physical flight is approved. Neither current Mac nor common-input5 nor canonical pixel/JSON admission is claimed.\n\nExact prompt/native arguments, guide, all source originals and prior lineage references are retained. Native model/seed are UNKNOWN. Research factual/access limits are retained: unavailable licensed footage was not seen or used as conditioning. Generated reference rights are unreviewed. All13 old drawing IDs are reuse; the four new primaryIDs are new raw-source drawings only. No further calls are authorized.\n''')
st=json.load(open(P/'active-status.json'));st.update(status='STABLE_HELD_SOURCE_READY_FOR_INDEPENDENT_REVIEW',actualReturnedDrawings=4,newUsefulTransitions='PENDING_INDEPENDENT_REVIEW',nativeCalls=1,automaticRetry=False,next='Root geometry and Slot appearance; no further generation');save('active-status.json',st)
ledger={str(f.relative_to(P)):sha(f) for f in sorted(P.rglob('*')) if f.is_file() and f.name not in ['review-target-hashes.json','STABLE-GO.json']};save('review-target-hashes.json',ledger)
go={'status':'STABLE_GO_HELD_TRANSITION_ATTEMPT','frozenFiles':len(ledger),'ledgerSHA256':sha(P/'review-target-hashes.json'),'nativeCalls':1,'newRawDrawings':4,'usefulTransitionCount':'PENDING_REVIEW','originalSHA256':sha(P/'original.png'),'primaryManifestSHA256':sha(P/'PRIMARY-SOURCE-MANIFEST.json'),'manifestSHA256':sha(P/'flight-source-proposal.json'),'mapSHA256':sha(P/'frame-to-action-map.json'),'noRetry':True,'scope':'source-only, held until independent review. Baseline52 unchanged. Reviews additively outside ledger.'};save('STABLE-GO.json',go);print(json.dumps(go));print('GO_SHA256',sha(P/'STABLE-GO.json'))
