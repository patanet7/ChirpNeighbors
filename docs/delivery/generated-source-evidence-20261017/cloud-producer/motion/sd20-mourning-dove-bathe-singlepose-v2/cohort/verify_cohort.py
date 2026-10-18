"""Uniform sampler, identities, exact source copies, crop/clock/preview checks only."""
from pathlib import Path
from PIL import Image
import hashlib,json,subprocess,numpy as np
P=Path(__file__).parent;B=P.parent;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();J=lambda n:json.loads((P/n).read_text())
def fid(im):return 'frame.sha256.'+hashlib.sha256(f'RGBA8;{im.width}x{im.height};'.encode()+im.tobytes()).hexdigest()
m=J('COHORT-SOURCE-MANIFEST.json');proposal=J('cohort-behavior-proposal.json');expected=['approach','settle','dip','wingflutter','shake','exit-preen'];assert m['nativeCalls']==m['newDrawings']==0 and len(m['frames'])==6 and m['allSourcesFrozen']
assert [r['phase'] for r in m['frames']]==expected and len({r['sourceFrameId'] for r in m['frames']})==6
images=[]
for row in m['frames']:
 src=Image.open(P/row['sourcePNG']);assert src.mode=='RGBA' and src.size==(1536,1024) and fid(src)==row['sourceFrameId'] and sha(P/row['sourcePNG'])==row['sourcePNGsha256']
 native=src.load();out=Image.new('RGBA',(144,96));px=out.load()
 # Scalar mathematical floor-center reference independent from NumPy gather exporter.
 for y in range(96):
  for x in range(144):px[x,y]=native[((2*x+1)*1536)//288,((2*y+1)*1024)//192]
 whole=Image.open(P/row['wholeCanvasPNG']);frame=Image.open(P/row['outputPNG']);assert whole.mode==frame.mode=='RGBA'
 assert out.tobytes()==whole.tobytes() and out.crop((4,8,140,88)).tobytes()==frame.tobytes()
 assert fid(frame)==row['derivativeDecodedRGBAId'] and sha(P/row['outputPNG'])==row['outputPNGsha256']
 assert row['pivot']==[77,76] and row['density']==1 and row['contacts']==[] and not row['newDrawing']
 for c in row['copiedSourceReceipts']:assert sha(P/c['file'])==c['sha256']
 for c in row['producerExportComparison']:assert sha(B/c['siblingProducerExport'])==c['sha256']
 images.append(frame)
for r in J('source-input-protection.json')['files']:assert sha(B/r['originalSiblingPath'])==r['sha256']
assert len(proposal['frames'])==6 and proposal['candidateDecodedAnimationArea']==6*136*80==65280<=65536
assert proposal['comparisonOutro']['outsideCandidateAsset'] and not proposal['comparisonOutro']['countedInCandidateArea']
assert proposal['bodyRootTrajectory']['translation']==[0,0] and proposal['contacts']==[] and not proposal['geometryReviewed'] and proposal['supportWorld'] is None
assert not proposal['batheSlotAccepted'] and not proposal['currentMacAdmission'] and not proposal['packetBindingReady']
assert [r['durationTicks'] for r in proposal['clips'][0]['frames']]==[18,18,12,18,12,24]
ap=Image.open(P/'six-phase-candidate.apng');assert ap.n_frames==6 and ap.size==(136,80) and ap.info['loop']==1
for i,im in enumerate(images):ap.seek(i);assert ap.convert('RGBA').tobytes()==im.tobytes() and ap.info['duration']==[600,600,400,600,400,800][i]
gif=Image.open(P/'Six-Phase-Candidate.gif');assert gif.n_frames==6 and gif.size==(136,80) and 'loop' not in gif.info
durations=[]
for i in range(6):gif.seek(i);durations.append(gif.info['duration'])
assert durations==[600,600,400,600,400,800]
js="""const assert=require('node:assert/strict'),{chooseAt}=require('./player.js'),p=require('./cohort-behavior-proposal.json');for(const [t,phase]of[[0,'approach'],[599,'approach'],[600,'settle'],[1200,'dip'],[1600,'wingflutter'],[2200,'shake'],[2600,'exit-preen'],[3399,'exit-preen'],[3400,'exact-awake-outro'],[4400,'exact-awake-outro']])assert.equal(chooseAt(p,t).phase,phase);assert.equal(chooseAt(p,4400).terminal,true);assert.equal(chooseAt(p,3400).outro,true);for(const t of[-1,NaN,Infinity])assert.throws(()=>chooseAt(p,t));console.log('phase boundaries, outside-asset awake outro and terminal hold PASS');"""
node=subprocess.run(['node','-e',js],cwd=P,capture_output=True,text=True,check=True)
r={'status':'PASS source/export integrity only','nativeCallsByCohort':0,'newDrawingsByCohort':0,'nativeOriginalsReferenced':6,'allSixSourceIDsVerifiedFromExactNativeRGBA':True,'independentScalarFloorCenterSampler':'PASS','uniformWholeCanvas144AndFixedCrop136RGBA':'PASS','producerExportsAndOriginalsUnchanged':True,'candidateDecodedAnimationArea':65280,'comparisonAwakeExcluded':True,'APNGSixFramesExactRGBA':True,'GIFSixFramesDurationsMs':durations,'authoredTicks':[18,18,12,18,12,24],'staticRoot':[77,76],'nodeBoundaryChecks':node.stdout.strip(),'geometryReviewed':False,'supportWorld':None,'fullBatheSlotAccepted':False,'MacAdmission':False,'canonicalRuntimeZod':'NOT_RUN','annotation':'Physical toe/wing/bill/water contact remains unbound; crop-fringe losses/source scale changes retained for independent review'}
(P/'verification.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
