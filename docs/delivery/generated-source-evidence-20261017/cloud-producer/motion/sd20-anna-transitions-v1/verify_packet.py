from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,struct,math
P=Path(__file__).parent;sha=lambda b:hashlib.sha256(b).hexdigest();read=lambda n:json.loads((P/n).read_text());fid=lambda im:'frame.sha256.'+sha(f'RGBA8;{im.width}x{im.height};'.encode()+im.tobytes());p=read('PRIMARY-SOURCE-MANIFEST.json');m=read('frame-to-action-map.json');a=read('action-source-manifest.json');cal=read('whole-call-calibration.json');checks=[]
def ok(label,v):assert v,label;checks.append({'check':label,'pass':True})
ok('native original exact',sha((P/p['original']).read_bytes())==p['originalSHA256']);ok('prompt exact submitted bytes',(P/'prompt.txt').read_bytes()==read('native-call-arguments.json')['arguments']['prompt'].encode());ok('bounded call and drawing counts',p['nativeCalls']==1 and len(p['frames'])==4 and len(p['reusedFrames'])==5);atlas=Image.open(P/a['atlas']['file']).convert('RGBA');ok('atlas hash/dimensions',sha((P/a['atlas']['file']).read_bytes())==a['atlas']['sha256'] and atlas.size==(864,96));ok('action manifest mapping hash',sha((P/m['manifest']['file']).read_bytes())==m['manifest']['sha256']);regscales=[]
for i,f in enumerate(p['frames']+p['reusedFrames']):
 src=Image.open(P/f['sourcePNG']).convert('RGBA');out=Image.open(P/f['outputPNG']).convert('RGBA');ok(f['pose']+' nativeRGBA/sourcePNG/outputPNG',fid(src)==f['sourceFrameId'] and sha((P/f['sourcePNG']).read_bytes())==f['sourcePNGsha256'] and sha((P/f['outputPNG']).read_bytes())==f['outputPNGsha256']);ok(f['pose']+' atlas slot',np.array_equal(np.array(out),np.array(atlas.crop((i*96,0,(i+1)*96,96)))))
 if i<4:
  r=f['registration'];ok(f['pose']+' calibration bound',r['sharedCalibrationFile']=='whole-call-calibration.json' and r['sharedCalibrationSHA256']==sha((P/'whole-call-calibration.json').read_bytes()));scale=cal['sharedNativeCellTo1024Scale'];x,y=cal['sharedOriginInteger'];reg=src.transform((1024,1024),Image.Transform.AFFINE,(1/scale,0,-x/scale,0,1/scale,-y/scale),Image.Resampling.NEAREST);ok(f['pose']+' exact common transform',np.array_equal(np.array(reg),np.array(Image.open(P/f['registeredPNG']).convert('RGBA'))) and np.array_equal(np.array(reg.resize((96,96),Image.Resampling.NEAREST)),np.array(out)));ok(f['pose']+' core fits',min(r['coreProjectedBoundsRegistered'][:2])>=0 and max(r['coreProjectedBoundsRegistered'][2:])<=1024);regscales.append((r['sharedCallScale'],tuple(r['sharedIntegerOrigin'])))
 elif f['registration'].get('sharedCalibrationFile'):ok(f['pose']+' local A calibration hash',sha((P/f['registration']['sharedCalibrationFile']).read_bytes())==f['registration']['sharedCalibrationSHA256'])
 rf=a['frames'][i];ar=np.array(out);ok(f['pose']+' support alpha',all(ar[c['y'],c['x'],3]>0 for c in rf['contacts']) and (rf['supportState']!='airborne' or rf['contacts']==[]))
ok('no perpose transforms',len(set(regscales))==1)
clipids={c['id'] for c in a['clips']};maxcontact=0.;billres=[];docs=['motion-manifest.json']+[x['file'] for x in m['motionProposalFiles']]
for n in docs:
 d=read(n);ok(n+' clock exact',d['tickRate']==30 and d['sampleTickConvention']=='frame-starts' and len(d['samples'])==d['durationTicks'] and [r['tick'] for r in d['samples']]==list(range(d['durationTicks'])));prev=0
 for s in d['segments']:
  st,en=s['ticks'];ok(n+' segment coverage '+str(st),st==prev and en>st and s['poseClipId'] in clipids);prev=en
  if s['supportState']!='airborne':ok(n+' supported stationary',s['rootFrom']==s['rootTo'])
  for t in range(st,en):
   u=(t-st)/(en-st-1) if en-st>1 else 0;q=u*u*(3-2*u);expect=(np.array(s['rootFrom'])*(1-q)+np.array(s['rootTo'])*q);r=d['samples'][t];assert np.allclose(expect,r['rootWorldXY'],atol=1e-10)
 ok(n+' duration covered',prev==d['durationTicks'])
 for r in d['samples']:
  if r['supportState']=='airborne':assert r['contacts']==[] and not r['grounded']
  for c in r['contacts']:maxcontact=max(maxcontact,abs(c['worldXY'][1]-d['flatPerchPlaneWorldY']))
  if r.get('billTargetResidualWorld') is not None:billres.append(r['billTargetResidualWorld'])
ok('supported contact plane residual',maxcontact<1e-9);ok('visual bill target residual',len(billres)==24 and max(billres)<1e-9)
# APNG header rational clock evidence, no decoder timing rounding inferred.
ap=(P/'yard-travel-one-shot.apng').read_bytes();pos=8;delays=[];num=None
while pos<len(ap):
 length=struct.unpack('>I',ap[pos:pos+4])[0];typ=ap[pos+4:pos+8];data=ap[pos+8:pos+8+length];pos+=length+12
 if typ==b'acTL':num,plays=struct.unpack('>II',data)
 if typ==b'fcTL':v=struct.unpack('>IIIIIHHBB',data);delays.append([v[5],v[6]])
ok('APNG 69 exact 30Hz frames one shot',num==69 and plays==1 and delays==[[1,30]]*69)
ex=read('native-extraction-receipt.json');ok('extraction quantified residual',ex['omittedFringePixels']==43 and ex['omittedAlphaValues']==[1] and ex['overlappingAssignedPixels']==0)
receipt={'status':'PASS technical source/export invariants;semantic approval pending','checks':checks,'checkCount':len(checks),'maxSupportedPlaneResidualWorld':maxcontact,'maxVisualBillTargetResidualWorld':max(billres),'APNG':{'frames':num,'delay':[1,30],'plays':plays},'GIF':'30/40ms delay quantization;APNG authoritative','limits':['No app admission or physical grip approval.','Single C flight key each;full landing/takeoff joins held.','A reuse provisional flutter;smooth hover held.','Source phase changes and authored root travel are separate.'],'browserCaptureFiles':0};(P/'verification.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({k:v for k,v in receipt.items() if k!='checks'}))
