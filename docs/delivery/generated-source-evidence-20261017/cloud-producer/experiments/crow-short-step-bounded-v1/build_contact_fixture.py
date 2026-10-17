"""Author a diagnostic contact schedule, not bird art or a runtime animation."""
from pathlib import Path
import json,hashlib,math
R=Path(__file__).parent
# Source coordinates are proposed, NOT fitted to unavailable crow pixels.
# Near/far names are screen-depth roles, not anatomical L/R.
data=[
 (0,0,540,502,800,522,800,'scan hold','near+far'),
 (180,0,540,502,800,522,800,'first step starts','far'),
 (260,10,538,522,792,522,800,'near swings','far'),
 (340,20,540,542,800,522,800,'near lands','near+far'),
 (460,20,540,542,800,522,800,'second step starts','near'),
 (540,30,538,542,800,542,792,'far swings','near'),
 (620,40,540,542,800,562,800,'far lands','near+far'),
 (800,40,540,542,800,562,800,'scan hold','near+far'),
 (1000,40,540,542,800,562,800,'scan hold ends','near+far')]
keys=[]
for t,dx,ty,nx,ny,fx,fy,label,stance in data:
 keys.append({'timeMs':t,'rootWorldOffset':[dx,0],'torsoLocalAnchor':[512,ty],'nearFootLocal':[nx-dx,ny],'farFootLocal':[fx-dx,fy],'nearFootWorld':[nx,ny],'farFootWorld':[fx,fy],'stanceRoles':stance.split('+'),'label':label})
fixture={'format':'chirp-crow-contact-diagnostic-proposal@0.1','status':'UNBOUND_NOT_RUNTIME_INPUT_NOT_ANIMATION','canonicalFrameIds':None,'sourcePixelsInspected':False,'biologicalScaleAccepted':False,'sourceCanvasProposal':[1024,1024],'space':{'origin':'top-left','axes':['right','down'],'units':'unbound diagnostic source pixels','pivot':[512,800],'transform':'world = source-local + rootWorldOffset; exactly once; no per-frame scaling/mirroring'},'fixedSupportBaselineY':800,'torsoRestAnchor':[512,540],'torsoMaximumVerticalExcursion':2,'footSwingMaximumLift':8,'rootDisplacementTotal':40,'contactEndpointSeparation':20,'headBillAndBodyOutlineAnchors':None,'appearanceTarget':'American crow; neutral black feathers; detailed naturalistic pixel art; mostly upright; no long reaching legs/deep crouch','trajectory':keys,'stanceIntervals':[{'role':'far','startMs':0,'endMs':340,'worldPoint':[522,800]},{'role':'near','startMs':340,'endMs':620,'worldPoint':[542,800]}],'interpolation':'linear per numeric landmark interval; hold endpoints during pauses; no body deformation implied','events':[],'limitations':['All numbers are authored test constraints, not observed anatomy, accepted pixel scale or current Mac contract.','No airborne hop is specified; this fixture isolates two modest walking steps and scan holds.','Short-step amplitude must be bound to torso/body scale from actual source and reviewed footage before biological acceptance.','No near/far foot occlusion mask or part rig exists.','Torso point motion is a diagnostic trajectory, not generated body animation.']}
(R/'contact-trajectory-proposal.json').write_text(json.dumps(fixture,indent=2)+'\n')
checks=[]
for interval in fixture['stanceIntervals']:
 pts=[k[interval['role']+'FootWorld'] for k in keys if interval['startMs']<=k['timeMs']<=interval['endMs']]
 err=max(math.dist(p,interval['worldPoint']) for p in pts)
 checks.append({'check':interval['role']+' authored stance endpoints','maximumDisplacement':err,'passed':err==0})
for k in keys:
 for role in ['near','far']:
  local=k[role+'FootLocal'];world=k[role+'FootWorld'];assert world==[local[0]+k['rootWorldOffset'][0],local[1]]
checks.append({'check':'all 18 authored foot coordinates obey declared translation once','passed':True})
checks.append({'check':'source-pixel/candidate contact tracking','passed':None,'status':'NOT_RUN_SOURCE_BYTES_UNAVAILABLE'})
(R/'fixture-check.json').write_text(json.dumps({'checks':checks,'mathChecksPassed':3,'candidateMeasured':False,'artOrMotionAccepted':False},indent=2)+'\n')
parts=['<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="500" viewBox="0 0 1080 500"><rect width="1080" height="500" fill="#17262a"/><g font-family="sans-serif" fill="#e4eee9"><text x="24" y="30" font-size="19">Unbound contact trajectory — technical landmarks only</text><text x="24" y="53" font-size="13">No crow pixels available. No new candidate. No generated bird animation or runtime acceptance.</text>']
for i,k in enumerate(keys):
 col=i%5;row=i//5;x=28+col*210;y=85+row*170
 parts.append(f'<g transform="translate({x},{y})"><rect width="192" height="150" fill="#21383c"/><text x="8" y="20" font-size="12">{k["timeMs"]}ms · root +{k["rootWorldOffset"][0]}</text><path d="M8 118H184" stroke="#b8c5b6"/><text x="8" y="139" font-size="10">{k["label"]}</text>')
 # One uniform .3 display scale in every panel; original values stay in JSON.
 for role,color in [('near','#61d5ed'),('far','#f3ba68')]:
  px,py=k[role+'FootWorld'];parts.append(f'<circle cx="{90+(px-512)*.3}" cy="{118+(py-800)*.3}" r="2" fill="{color}"/>')
 tx,ty=k['torsoLocalAnchor'];tx+=k['rootWorldOffset'][0];parts.append(f'<path d="M{90+(tx-512)*.3-5} {118+(ty-800)*.3}h10m-5 -5v10" stroke="#ec7a91"/></g>')
parts.append('<text x="870" y="350" font-size="12">Pink: torso anchor</text><text x="870" y="370" font-size="12" fill="#61d5ed">Blue: near foot</text><text x="870" y="390" font-size="12" fill="#f3ba68">Gold: far foot</text><text x="24" y="470" font-size="13">Positions are authored diagnostic constraints; zero mathematical slip is not measured success on generated pixels.</text></g></svg>')
(R/'contact-guide.svg').write_text(''.join(parts))
print(json.dumps({'authoredKeyframes':len(keys),'mathChecksPassed':3,'generatedCandidates':0,'sourcePixelsInspected':False}))
