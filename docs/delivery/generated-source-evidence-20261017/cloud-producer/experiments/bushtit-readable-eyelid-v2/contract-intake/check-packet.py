from pathlib import Path
import json,hashlib,subprocess,shutil,sys,struct,zlib
from PIL import Image
import numpy as np
P=Path(sys.argv[1]);O=P/'contract-intake';O.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
load=lambda f:json.loads((P/f).read_text())
put=lambda f,d:(O/f).write_text(json.dumps(d,indent=2)+'\n')
a=lambda f:np.array(Image.open(P/f).convert('RGBA'))
fid=lambda ar:'frame.sha256.'+hashlib.sha256(f'RGBA8;{ar.shape[1]}x{ar.shape[0]};'.encode()+ar.tobytes()).hexdigest()
checks=[]
def check(n,b,**e):
 checks.append(dict(check=n,status='PASS' if b else 'FAIL',**e))
 if not b:raise AssertionError(n)
ledger=load('review-target-hashes.json');check('frozen producer hashes before',all(sha(P/f)==h for f,h in ledger.items()),entries=len(ledger))
h=load('source-handoff.json');m=load('PRIMARY-SOURCE-MANIFEST.json');args=load('native-arguments.json');ret=load('native-return-receipt.json');native=a(m['original'])
check('native original SHA',sha(P/m['original'])==m['originalSHA256'])
check('whole native primary identity',fid(native)==m['frames'][0]['sourceFrameId'],sourceID=fid(native))
check('one native original one drawing',m['nativeCalls']==1 and len(m['frames'])==1)
check('literal prompt bytes',args['prompt'].encode()==(P/m['prompt']).read_bytes() and sha(P/m['prompt'])==m['promptSHA256'])
refs=args['referenced_image_paths'];check('sole actual conditioning image',len(refs)==1)
reference=Path(refs[0]);reuse=m['reusedFrames'][0];check('exact reference bytes and native identity',sha(reference)==reuse['sourcePNGsha256'] and fid(np.array(Image.open(reference).convert('RGBA')))==reuse['sourceFrameId'])
check('actual returned call',ret.get('nativeCallsReturned',ret.get('nativeCalls'))==1 and ret['originalSHA256']==m['originalSHA256'] and ret['sourceFrameId']==m['frames'][0]['sourceFrameId'])
frames=[];metrics=[]
for f in h['frames']:
 ar=a(f['png']);check('render bytes '+f['id'],sha(P/f['png'])==f['PNGsha256'] and fid(ar)==f['decodedRGBAId'])
 frames.append(dict(id=f['id'],png=str(P/f['png']),PNGsha256=f['PNGsha256'],decodedRGBAId=f['decodedRGBAId']))
 metrics.append(dict(id=f['id'],canvas=[ar.shape[1],ar.shape[0]],RGBAColors=len(np.unique(ar.reshape(-1,4),axis=0)),partialAlphaPixels=int(((ar[:,:,3]>0)&(ar[:,:,3]<255)).sum()),alphaPositivePixels=int((ar[:,:,3]>0).sum()),density=h['density'],pivot=h['candidatePivot']))
check('source contact and support remain unapproved',h['contacts']==[] and h['supportWorld'] is None and h['geometryReviewed'] is False and h['runtimeAdmission'] is False)
if h['speciesId']=='bushtit':
 check('submitted wrapper exact',load('native-call-arguments.json')['arguments']==args)
 xx=((np.arange(64)*2+1)*native.shape[1]//128);yy=((np.arange(64)*2+1)*native.shape[0]//128);donor=native[yy[:,None],xx[None,:]]
 check('whole donor pixel center nearest sample',np.array_equal(donor,a('raw/new-native-closed64.png')))
 pal=np.array(load('fixed-palette.json')['opaqueRGB'],dtype=np.int32);check('fixed palette sorted 59',len(pal)==59 and pal.tolist()==sorted(pal.tolist()))
 ix=((donor[:,:,:3].astype(np.int32)[:,:,None]-pal)**2).sum(3).argmin(2);proj=np.zeros_like(donor);opaque=donor[:,:,3]>=128;proj[:,:,:3]=pal[ix];proj[:,:,3]=np.where(opaque,255,0);proj[~opaque]=0
 check('one fixed palette threshold projection',np.array_equal(proj,a('codec/new-native-closed64.png')))
 mask=np.zeros((64,64),bool);mask[33:37,39:44]=True;check('predeclared twenty pixel mask',np.array_equal(np.array(Image.open(P/'masks/eye-context-ownership.png'))>0,mask))
 awake=a('inputs/canonical-awake64.png');closed=a('frames/closed.png');expected=awake.copy();expected[mask]=proj[mask]
 check('construction exact same XY donor inside canonical outside',np.array_equal(expected,closed),insideChanges=int(np.any(closed!=awake,axis=2)[mask].sum()),outsideChanges=int(np.any(closed!=awake,axis=2)[~mask].sum()))
 raw=a('inputs/raw-awake64.png');raw[mask]=donor[mask];check('raw construction exact',np.array_equal(raw,a('raw/constructed-closed64.png')))
 body=awake.copy();body[mask]=0;eye=np.zeros_like(awake);eye[mask]=proj[mask]
 check('actual body and eye layers',np.array_equal(body,a('layers/fixed-awake-outside-eye.png')) and np.array_equal(eye,a('layers/new-closed-eye-context.png')))
 maps=load('source-pixel-maps.json')['insideEyePatch'];check('all twenty donor maps exact',len(maps)==20 and all(r['nativeDonorXY']==[int(xx[r['outputXY'][0]]),int(yy[r['outputXY'][1]])] and r['fixedPaletteProjectedRGBA']==proj[r['outputXY'][1],r['outputXY'][0]].tolist() and r['rawNativeRGBA']==donor[r['outputXY'][1],r['outputXY'][0]].tolist() for r in maps))
 check('awake PNG byte identical',sha(P/'frames/awake.png')==sha(P/'inputs/canonical-awake64.png'))
 apng='blink.apng';sequence=['awake','closed','awake'];dur=[2000,100,900]
else:
 n=192;xx=((np.arange(n)*2+1)*native.shape[1]//(n*2));yy=((np.arange(n)*2+1)*native.shape[0]//(n*2));check('full straight RGBA nearest sample',np.array_equal(native[yy[:,None],xx[None,:]],a('grip-study192.png')))
 check('exact cached audit binding',sha(P/'cached-contract-audit.json')=='27711fba6de1a8b2c1fac81674c8d990ae8dd9913223ae8a9c4d929a338cdaed')
 regions=load('occlusion-proposal.json')['regions'];ar=a('grip-study192.png');masks={}
 for r in regions:
  mask=np.array(Image.open(P/r['mask']))>0;masks[r['id']]=mask;layer=np.zeros_like(ar);layer[mask]=ar[mask]
  check('region exact source pixels '+r['id'],sha(P/r['mask'])==r['maskSHA256'] and sha(P/r['layer'])==r['layerSHA256'] and np.array_equal(layer,a(r['layer'])) and int((mask&(ar[:,:,3]>0)).sum())==r['visibleAlphaPositivePixels'])
 overlaps=[dict(a=x,b=y,sourceAlphaPositiveIntersection=int((masks[x]&masks[y]&(ar[:,:,3]>0)).sum())) for i,x in enumerate(masks) for y in list(masks)[i+1:] if (masks[x]&masks[y]).any()]
 put('overlapping-region-evidence.json',{'regionsAreHypothesesNotDepthMasks':True,'overlaps':overlaps,'supportFit':'UNVERIFIED'})
 apng='STATIC-grip-study.apng';sequence=['crow-grip-static'];dur=[3000]
# Decode actual APNG images/delays; validate every PNG chunk CRC.
b=(P/apng).read_bytes();pos=8;chunks=0
while pos<len(b):
 size=struct.unpack('>I',b[pos:pos+4])[0];tag=b[pos+4:pos+8];data=b[pos+8:pos+8+size];crc=struct.unpack('>I',b[pos+8+size:pos+12+size])[0];check('APNG CRC '+str(chunks),zlib.crc32(tag+data)&0xffffffff==crc);chunks+=1;pos+=12+size
im=Image.open(P/apng);check('APNG frame count',getattr(im,'n_frames',1)==len(sequence));frameby={f['id']:a(f['png']) for f in h['frames']}
for i,id in enumerate(sequence):
 im.seek(i);check('APNG pixels and timing '+str(i),np.array_equal(np.array(im.convert('RGBA')),frameby[id]) and abs(im.info.get('duration',3000)-dur[i])<.01)
check('frozen producer hashes after proof',all(sha(P/f)==v for f,v in ledger.items()),entries=len(ledger))
put('source-proof.json',{'scope':'Native provenance, exact source pixels, construction and authored timing; not readability or physical support approval','frozenLedgerSHA256':sha(P/'review-target-hashes.json'),'checks':checks,'frameMetrics':metrics,'input5':'NOT_APPLICABLE_INCOMPLETE_COMMON_FAMILY','currentMacAdmission':'UNKNOWN','runtimeAdmission':False})
cfg={'expectedPackageSHA256':'b936301983382339392ffdb5cba9f36af1018f9a55513c44bbbee81c36080088','expectedCanonicalSHA256':'28c4c5f7bd522ac9709ce66df07c674e9f9a5ec53d35255c4a0ebfdef4637320','canvas':{'width':metrics[0]['canvas'][0],'height':metrics[0]['canvas'][1]},'frames':frames,'logicalPixelSize':1,'paletteLimit':64,'contacts':[],'geometryReviewed':False,'supportWorld':None}
put('canonical-pixel-input.json',cfg)
print(json.dumps({'packet':P.name,'proofChecks':len(checks),'metrics':metrics}))
