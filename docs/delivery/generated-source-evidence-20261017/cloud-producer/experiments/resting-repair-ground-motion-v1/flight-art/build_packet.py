import json,hashlib,shutil,math
from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np
P=Path(__file__).parent; R=Path('/workspace/asset-production'); (P/'frames96').mkdir(exist_ok=True);(P/'lineage').mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rgbaid(p):
 im=Image.open(p).convert('RGBA');return 'frame.sha256.'+hashlib.sha256(f'RGBA8;{im.width}x{im.height};'.encode()+im.tobytes()).hexdigest()
def save(name,d): (P/name).write_text(json.dumps(d,indent=2)+'\n')
frames=[]; originals=[]; targetrefs={}
for pack,man in [('sd20-anna-hover-cycle-v2','airborne-source-manifest.json'),('sd20-anna-dart-brake-v1','airborne-source-manifest.json'),('sd20-anna-transitions-v1','action-source-manifest.json')]:
 q=R/'motion'/pack; m=json.loads((q/man).read_text()); mp=json.loads((q/'frame-to-action-map.json').read_text()); pm=json.loads((q/'PRIMARY-SOURCE-MANIFEST.json').read_text()); sd={x.get('primarySourceFrameId',x.get('sourceFrameId')):x for x in mp['sourceToRenderFrames']}
 for fname in ['PRIMARY-SOURCE-MANIFEST.json','whole-call-calibration.json','frame-to-action-map.json',man,'independent-review.json']:
  f=q/fname
  if f.exists():
   local=f'lineage/{pack}--{fname}';shutil.copyfile(f,P/local);targetrefs[str(f.relative_to(R))]=sha(f)
 originals.append({'package':str(q.relative_to(R)), 'primaryManifest':f'lineage/{pack}--PRIMARY-SOURCE-MANIFEST.json','original':str((q/pm['original']).relative_to(R)),'originalSHA256':sha(q/pm['original']),'prompt':str((q/pm['prompt']).relative_to(R)),'promptSHA256':sha(q/pm['prompt']),'model':'UNKNOWN','seed':'UNKNOWN','note':'Historical generation. This packet makes zero requests. Older reused keys retain origin lineage inside copied primary manifest; package original is not necessarily their origin.'})
 for f in m['frames']:
  sid=f['primarySourceFrameId']
  if any(x['primarySourceFrameId']==sid for x in frames):continue
  x=sd[sid]; out=q/x['outputPNG']; src=q/x.get('primarySourcePNG',x.get('sourcePNG',''))
  assert out.is_file() and src.is_file(); assert sha(out)==x['outputPNGsha256'];assert rgbaid(src)==sid,(sid,rgbaid(src))
  local='frames96/'+f['id']+'.png';shutil.copyfile(out,P/local)
  frames.append({'id':f['id'],'primarySourceFrameId':sid,'newDrawing':False,'outputPNG':local,'outputPNGsha256':sha(out),'outputDecodedRGBAId':rgbaid(out),'primarySourcePNG':str(src.relative_to(R)),'primarySourcePNGsha256':sha(src),'primarySourceCanvas':list(Image.open(src).size),'referencePackage':str(q.relative_to(R)),'sourceRect':{'x':0,'y':0,'width':96,'height':96},'canvas':[96,96],'world':[64,64],'sourcePixelsPerWorldUnit':1.5,'pivot':[f['pivot']['x'],f['pivot']['y']],'anchors':f.get('anchors',{}),'contacts':[],'sourceContactProbes':f.get('contacts',[]),'supportState':'proposal-only-unbound' if f.get('contacts') else 'airborne','geometryReviewed':False,'supportWorld':None})
D={f['id']:f for f in frames}
# Exact source rows, plus common body-origin diagnostics; source pixels are never changed.
W=920; sheet=Image.new('RGB',(W,420),'#eee9da');d=ImageDraw.Draw(sheet)
for i,f in enumerate(frames):
 x=10+(i%7)*130;y=12+(i//7)*200
 d.text((x,y),f['id'].replace('anna-','').replace('-96',''),fill='black')
 im=Image.open(P/f['outputPNG']).convert('RGBA');idx=np.floor((np.arange(64)+.5)*96/64).astype(int);small=Image.fromarray(np.array(im)[idx[:,None],idx[None,:]])
 for j,bg in enumerate(['#f1eddf','#24313c']):
  tile=Image.new('RGBA',(120,77),bg);tile.alpha_composite(small,(20,0)); sheet.paste(tile.convert('RGB'),(x,y+18+j*80))
 d.text((x,y+174),'pivot '+str(f['pivot']),fill='black')
sheet.save(P/'normal64-light-dark-sheet.png')
# Source clocks are independent of authored trajectory. Existing poses only; no new wing drawings.
up='anna-hover-up-96';mid='anna-hover-mid-downstroke-96';down='anna-hover-down-96';rec='anna-hover-mid-recovery-96';per='anna-c-perched-reference-96';release='anna-c-takeoff-release-96';reach='anna-c-landing-reach-96';arrival='anna-c-arrival-supported-96'
cycle=[up,mid,down,rec]
def seg(a,b,fr,root0,root1,state):return {'ticks':[a,b],'frameId':fr,'rootFrom':root0,'rootTo':root1,'supportState':state,'contacts':[]}
clips=[]
clips.append({'id':'hover-existing-four-poses','status':'PROVISIONAL_SOURCE_SUBSET_REVIEW_PENDING','segments':[seg(i,i+1,cycle[i%4],[80,96],[80,96],'airborne') for i in range(24)]})
launch=[seg(0,15,per,[80,126],[80,126],'proposed-supported-unbound'),seg(15,18,release,[80,118],[80,114],'airborne')]
for i in range(18,42):launch.append(seg(i,i+1,cycle[(i-18)%4],[80,114-(i-18)*.75],[80,114-(i-17)*.75],'airborne'))
clips.append({'id':'takeoff-held-join','status':'HELD_SUPPORTED_PRELOAD_MISSING','segments':launch,'limitation':'Perch to curled-foot release has no visibly weighted wing-engaged preload. 8world body-origin step retained as historical counterexample, not toe-gap claim.'})
landing=[seg(i,i+1,cycle[i%4],[78,102+i*.55],[78,102+(i+1)*.55],'airborne') for i in range(12)]
landing += [seg(12,18,reach,[77.3333333333,112],[77.3333333333,117.3333333333],'airborne'),seg(18,21,reach,[77.3333333333,117.3333333333],[77.3333333333,117.3333333333],'proposed-first-near-contact-unbound'),seg(21,42,arrival,[80,122.6666666667],[80,122.6666666667],'proposed-supported-unbound')]
clips.append({'id':'landing-stepped-contact-study','status':'HELD_ABRUPT_FOLD_COMPRESSION_JOIN','segments':landing,'limitation':'Near proxy retained at82,130 across reach-to-arrival, but bill shifts3.77world and head4.06world; instant wing fold remains. Other claw is not flattened to plane.'})
bids=['anna-forward-drive-a-96','anna-forward-drive-b-96','anna-upright-brake-a-96','anna-upright-brake-b-96']
clips.append({'id':'drive-brake-common-body-origin','status':'CROSS_PACK_DIAGNOSTIC_NOT_JOIN_ACCEPTANCE','segments':[seg(i*6,(i+1)*6,x,[80,96],[80,96],'airborne') for i,x in enumerate([up]+bids+[up])],'limitation':'B pivot48,60 versusA54,68 retained; body pitch/head motion intentional but cross-pack identity/size handoff requires independent actual-size review. No pose fit.'})
for c in clips:c.update(tickRate=30,loop=False,durationTicks=c['segments'][-1]['ticks'][1],segmentTickConvention='half-open',sampleTickConvention='frame-starts',terminal='hold last sample, manual replay only',rootPathGeneratesNewDrawings=False)
save('flight-source-proposal.json',{'batchId':'anna-existing-flight-reuse-v1','scope':'source-only flight proposal; separate from common idle/blink/look input5','nativeCalls':0,'newDrawings':0,'reusedDrawings':len(frames),'speciesId':'anna_s_hummingbird','sourceStatus':'PARTIAL_USEFUL_KEYS_WITH_HELD_TERMINAL_JOINS','rights':'unreviewed; generated-source lineage retained; no licensed footage pixels used','sourceCanvas':[96,96],'sourcePixelsPerWorldUnit':1.5,'worldCanvas':[64,64],'perPoseFit':False,'pixelEdits':False,'frames':frames,'clips':clips,'geometryReviewed':False,'supportWorld':None,'currentMacAdmission':'NOT_TESTED','canonicalPixelJSONAdmission':'NOT_RUN_FOR_THIS_PROPOSAL','physicalFlightSimulation':False,'timing':'authored stylization, not measured wingbeat or behavior rates'})
save('reference-lineage.json',{'rootRelativeTo':'asset-production','priorNativePackages':originals,'verifiedInputFiles':targetrefs,'history':'A and C already use one shared calibration per historical native call; B has its own historical shared calibration. This packet byte-copies existing96 outputs, performs no recalibration/fit. Primary source IDs differ from registered derivative IDs.'})
save('join-findings.json',{'nativeCalls':0,'chosenSpecies':'anna_s_hummingbird','perPhase':{'hover':'four genuine distinct wing drawings, useful provisional subset; anatomical smoothness not granted','driveBrake':'distinct pitch/tail/wing poses; common-origin comparison only, not biological kinematics','takeoff':'HELD missing wing-engaged yet visibly weighted supported preload; existing curled claw is not weighted support','landing':'HELD abrupt wingfold/compression join; proposed one-near-contact math is not bilateral physical approval'},'worldFormula':'W=R+(q-p)/1.5','landingNearProxy':{'reachPixel':[61,87],'reachRoot':[77.3333333333,117.3333333333],'arrivalPixel':[57,79],'arrivalRoot':[80,122.6666666667],'worldBoth':[82,130],'headStepWorld':4.057,'billStepWorld':3.771,'caveat':'pixel probes with uncertain anatomy; other claw remains4world higher'},'takeoff':{'oldBodyRoot':[80,126],'releaseBodyRoot':[80,118],'releaseCurledClawWorld':[77.3333333333,123.3333333333],'plane':130,'gapWorld':6.6666666667,'caveat':'8world body-origin gap is not toe gap; toe-pinning curled claw would not prove support'},'generationDecision':'HOLD optional sixth request: existing airborne wing subset sufficient to hand off now; terminal missing purposes explicit, no wholeflight regeneration.'})
# APNG previews are actual generated-art derivatives, not browser screenshots. Sampling identical for every96 frame.
for c in clips:
 seq=[]
 for t in range(c['durationTicks']):
  s=next(s for s in c['segments'] if s['ticks'][0]<=t<s['ticks'][1]);f=D[s['frameId']];a,b=s['ticks'];u=(t-a)/(b-a);root=[s['rootFrom'][j]+u*(s['rootTo'][j]-s['rootFrom'][j]) for j in range(2)]
  arr=np.array(Image.open(P/f['outputPNG']).convert('RGBA'));idx=np.floor((np.arange(64)+.5)*1.5).astype(int);im=Image.fromarray(arr[idx[:,None],idx[None,:]])
  stage=Image.new('RGBA',(360,170),(238,233,221,255));dr=ImageDraw.Draw(stage);dr.line((0,130,360,130),fill='#a69d8b');dr.text((5,5),c['id'],fill='black')
  for off,bg in [(0,None),(180,'#24313c')]:
   if bg:dr.rectangle((180,20,359,169),fill=bg);dr.line((180,130,359,130),fill='#858e91')
   xy=(round(root[0]-f['pivot'][0]/1.5)+off,round(root[1]-f['pivot'][1]/1.5));stage.alpha_composite(im,xy)
  seq.append(stage)
 seq[0].save(P/(c['id']+'.apng'),save_all=True,append_images=seq[1:],duration=1000/30,loop=1,disposal=0,blend=0)
save('active-status.json',{'status':'SOURCE_PREVIEW_PREPARED_REVIEW_PENDING','species':'anna_s_hummingbird','nativeCallStarted':False,'nativeCalls':0,'newDrawings':0,'reusedDrawings':len(frames),'actualWork':'13 exact existing96 PNG copies, primaryIDs checked against decoded sourceRGBA, normal64world source sheet and separate authored one-shot clocks','next':'independent actual-size review then frozen handoff; optional newmissingpurpose call not started','stopConditions':['No existing key relabeled as new','No generated flight claimed from trajectory','Takeoff/landing held until independent review; no automatic retry']})
print(len(frames),'existing drawings copied; no native call')
