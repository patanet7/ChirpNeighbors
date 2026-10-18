"""Artifact identity/transformation/timing guards; runtime policy belongs to shared structural runner."""
from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,subprocess
P=Path(__file__).parent;R=P.parents[1];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();J=lambda n:json.loads((P/n).read_text())
def fid(im):return 'frame.sha256.'+hashlib.sha256(f'RGBA8;{im.width}x{im.height};'.encode()+im.tobytes()).hexdigest()
m=J('family-source-manifest.json');cfg=J('canonical-input.json');receipt=J('structural-receipt.json');assert m['nativeCalls']==m['newDrawings']==m['newSourceSlots']==0 and len(m['frames'])==3
assert receipt['inputSHA256']==sha(P/'canonical-input.json') and receipt['status']=='PASS exact canonical pixel normalization subset'
assert receipt['sharedRunnerSHA256']==sha(R/'validation/shared-structural-check.mjs') and receipt['actualCanonicalPermanentStageErrorUsed'] and receipt['partialAlphaNegativeControlRejected']
assert receipt['inputSchemaAndFullProductionManifestValidation'] is False and receipt['currentMacAdmission'] is False
assert receipt['packageFileSHA256']==cfg['expectedPackageSHA256'] and receipt['canonicalErrorModuleSHA256']==cfg['expectedCanonicalSHA256']
source=[];run=[]
for row,candidate in zip(m['frames'],cfg['frames']):
 original=Image.open(P/row['canonicalSourcePNG']).convert('RGBA');old=Image.open(P/row['legacy96PNG']);s=Image.open(P/row['sourcePNG']);rt=Image.open(P/row['runtimePNG']);assert old.mode==s.mode==rt.mode=='RGBA' and fid(original)==row['sourceFrameId']
 assert sha(P/row['canonicalSourcePNG'])==row['canonicalSourcePNGsha256'] and sha(P/row['legacy96PNG'])==row['legacy96PNGsha256']
 for y in range(102):
  for x in range(102):assert s.getpixel((x,y))==old.getpixel((((2*x+1)*96)//204,((2*y+1)*96)//204))
 assert fid(s)==row['sourceDerivativeRGBAId'] and fid(rt)==candidate['decodedRGBAId']==row['runtimeDerivativeRGBAId'];assert sha(P/row['runtimePNG'])==candidate['PNGsha256']==row['runtimePNGsha256']
 a=np.array(s);b=np.array(rt);assert np.array_equal(b[:,:,3],(a[:,:,3]>=128).astype(np.uint8)*255) and np.all(b[:,:,:3][b[:,:,3]==0]==0)
 for proxy in row['footImageProxies']:assert list(s.getpixel(tuple(proxy['proposedInteger102Point'])))==proxy['source102RGBA']
 for proxy in row['imageAnchorProxies']:assert list(s.getpixel(tuple(proxy['source102Point'])))==proxy['source102RGBA']
 source.append(s);run.append(rt)
for row in J('legacy-protection.json')['files']:assert sha(R/row['file'])==row['sha256']
opaque=np.concatenate([np.array(im)[:,:,:3][np.array(im)[:,:,3]>=128]for im in source]);q=np.array(Image.fromarray(opaque.reshape(1,-1,3),'RGB').quantize(colors=63,method=Image.Quantize.MEDIANCUT,dither=Image.Dither.NONE).convert('RGB')).reshape(-1,3);cursor=0
for s,rt in zip(source,run):
 a=np.array(s);mask=a[:,:,3]>=128;n=int(mask.sum());b=np.zeros((102,102,4),np.uint8);b[:,:,:3][mask]=q[cursor:cursor+n];b[:,:,3][mask]=255;cursor+=n;assert b.tobytes()==rt.tobytes()
assert m['integerPivot']==[61,80] and m['pivotIntegerRoundingDelta']==[.4375,.3125] and m['contacts']==[] and not m['geometryReviewed'] and m['supportWorld'] is None
assert [[f['durationTicks']for f in c['frames']]for c in m['clips']]==[[60],[60,3,27],[60,6,24]] and all(c['loop']for c in m['clips'])
for name,ids,ms in [('blink',[0,1,0],[2000,100,900]),('look',[0,2,0],[2000,200,800])]:
 for typ,ims in [('source',source),('runtime',run)]:
  ap=Image.open(P/(name+'-'+typ+'.apng'));assert ap.n_frames==3 and ap.size==(102,102) and ap.info['loop']==1
  for i,idx in enumerate(ids):ap.seek(i);assert ap.convert('RGBA').tobytes()==ims[idx].tobytes() and ap.info['duration']==ms[i]
js="""const assert=require('node:assert/strict'),{frameAt}=require('./player.js'),m=require('./family-source-manifest.json');for(const[t,p]of[[0,'neutral'],[1999,'neutral'],[2000,'blink'],[2099,'blink'],[2100,'neutral'],[3000,'neutral']])assert.equal(frameAt(m,'blink',t).phase,p);for(const[t,p]of[[0,'neutral'],[1999,'neutral'],[2000,'look'],[2199,'look'],[2200,'neutral'],[3000,'neutral']])assert.equal(frameAt(m,'look',t).phase,p);for(const t of[0,50000])assert.equal(frameAt(m,'idle',t).phase,'neutral');for(const t of[-1,NaN,Infinity])assert.throws(()=>frameAt(m,'blink',t));console.log('inherited blink/look loops, authored neutral hold and invalid-time checks PASS');"""
z=subprocess.run(['node','-e',js],cwd=P,capture_output=True,text=True,check=True)
result={'status':'PASS artifact identity/transformation/timing only','nativeCalls':0,'newDrawings':0,'newSlots':0,'existingDrawingIDs':3,'legacyBytesPreserved':True,'scalarFloorCenterRGBAProof':True,'globalPaletteReproduction':True,'sourceFramesAndRuntimeFrames':3,'uniformCanvas':[102,102],'density':1,'authoredIdleTicks':60,'inheritedBlinkTicks':[60,3,27],'inheritedLookTicks':[60,6,24],'APNGsRGBAAndTimingExact':True,'nodeTimingEvidence':z.stdout.strip(),'sharedStructuralReceipt':'structural-receipt.json','sharedStructuralInputSHA256':sha(P/'canonical-input.json'),'runtimePolicyThresholdsCopiedIntoProducerValidator':False,'sourceVisualReview':'PENDING','geometryReviewed':False,'supportWorld':None,'MacAdmission':False}
(P/'verification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
