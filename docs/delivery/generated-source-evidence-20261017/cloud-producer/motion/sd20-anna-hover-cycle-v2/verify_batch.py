from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,math
P=Path(__file__).parent;sha=lambda b:hashlib.sha256(b).hexdigest();M=json.loads((P/'PRIMARY-SOURCE-MANIFEST.json').read_text());A=json.loads((P/'airborne-source-manifest.json').read_text());C=json.loads((P/'whole-call-calibration.json').read_text());F=json.loads((P/'frame-to-action-map.json').read_text());B=json.loads((P/'body-trajectory.json').read_text());original=Image.open(P/'original.png').convert('RGBA');assert sha((P/'original.png').read_bytes())==M['originalSHA256'];assert sha((P/'prompt.txt').read_bytes())==M['promptSHA256'];assert len(M['frames'])==2 and len(M['reusedFrames'])==2;checks=['original/prompt hashes and honest2new+2reused counts']
for i,f in enumerate(M['frames']):
 im=Image.open(P/f['sourcePNG']).convert('RGBA');assert im.tobytes()==original.crop((i*887,0,(i+1)*887,887)).tobytes();assert f['sourceFrameId']=='frame.sha256.'+sha(b'RGBA8;887x887;'+im.tobytes());assert sha((P/f['sourcePNG']).read_bytes())==f['sourcePNGsha256'];q=(np.arange(96)+.5)*1024/96;ix=np.floor((q-C['sharedOriginTranslation'][0])/C['sharedNativeTo1024Scale']).astype(int);iy=np.floor((q-C['sharedOriginTranslation'][1])/C['sharedNativeTo1024Scale']).astype(int);a=np.array(im);expected=np.zeros((96,96,4),np.uint8);vx=(ix>=0)&(ix<887);vy=(iy>=0)&(iy<887);expected[np.ix_(vy,vx)]=a[np.ix_(iy[vy],ix[vx])];assert Image.open(P/f['outputPNG']).convert('RGBA').tobytes()==expected.tobytes();assert sha((P/f['outputPNG']).read_bytes())==f['outputPNGsha256']
checks+=['two exact native-cell source IDs/crops and one shared direct-nearest transform']
oldroot=P.parent/'sd20-anna-actions-v1'
for f,name in zip(M['reusedFrames'],['up','down']):
 assert (P/f['sourcePNG']).read_bytes()==(oldroot/'frames1024'/('hover-'+name+'.png')).read_bytes();assert (P/f['outputPNG']).read_bytes()==(oldroot/'frames96'/('hover-'+name+'.png')).read_bytes();im=Image.open(P/f['sourcePNG']).convert('RGBA');assert f['sourceFrameId']=='frame.sha256.'+sha(b'RGBA8;1024x1024;'+im.tobytes())
checks+=['old two source and render PNGs reused byte-identical']
o=np.array(C['oldMeanBillTail']);n=np.array(C['newMeanBillTail']);ov=o[0]-o[1];nv=n[0]-n[1];s=float(np.dot(ov,nv)/np.dot(nv,nv));t=np.rint(o.mean(0)-n.mean(0)*s).astype(int);assert abs(s-C['sharedNativeTo1024Scale'])<1e-12;assert list(t)==C['sharedOriginTranslation'];assert all(v>=0 for v in t);assert t[0]+887*s<1024 and t[1]+887*s<1024
checks+=['one global bill-tail calibration, shared integer origin and no source-envelope clipping']
atlas=Image.open(P/'hover-atlas96.png').convert('RGBA');assert atlas.size==(384,96);assert sha((P/'hover-atlas96.png').read_bytes())==A['atlas']['sha256']==F['atlasBinding']['sha256'];assert sha((P/F['manifest']['file']).read_bytes())==F['manifest']['sha256'];assert F['clips']==A['clips'];RGBA=[]
for i,(f,m) in enumerate(zip(A['frames'],F['sourceToRenderFrames'])):
 tile=atlas.crop((i*96,0,(i+1)*96,96));assert tile.tobytes()==Image.open(P/m['outputPNG']).convert('RGBA').tobytes();assert f['primarySourceFrameId']==m['primarySourceFrameId'];assert f['id']==m['renderFrameId'];assert f['sourceRect']==m['atlasRect'];assert f['contacts']==[];assert f['world']=={'width':64,'height':64};assert f['sourcePixelsPerWorldUnit']==1.5
 for point in f['anchorMeasurements'].values():
  p=point['pixel'];rgba=tile.getpixel(tuple(p));assert rgba[3]>0;assert list(rgba)==point['RGBA']
 b=f['anchorMeasurements']['billTip']['pixel'];a=np.array(tile);yy,xx=np.where((a[:,:,3]>=128)&(np.indices((96,96))[1]>=66)&(np.indices((96,96))[1]<=85)&(np.indices((96,96))[0]>=48)&(np.indices((96,96))[0]<=55));assert b[0]==int(xx.max());RGBA.append(tile.tobytes())
assert len(set(RGBA))==4;checks+=['4distinct render tiles, exact source/action/atlas binding, perpose positive-alpha anchor samples, airborne contacts[]']
for name,tick in [('wing-cycle.apng',1),('wing-cycle-slow.apng',8)]:
 im=Image.open(P/name);assert im.n_frames==4
 for i in range(4):im.seek(i);assert abs(im.info['duration']-tick/30*1000)<1e-8;assert im.convert('RGBA').tobytes()==RGBA[i]
assert B['durationTicks']==120 and B['wingCycleTicks']==4;assert len([s for s in B['segments'] if s['rootFrom']!=s['rootTo']])==2;assert B['segments'][0]['rootFrom']==B['segments'][-1]['rootTo'];assert B['maximumCorrectionWorld']<=2
checks+=['exact30Hz fourpose and slow timing;120tick body path has2bounded corrections and loop root return']
r={'passed':True,'checks':checks,'newDrawings':2,'reusedDrawings':2,'newNeutralDrawings':0,'appBound':False,'runtimeProfileAccepted':False,'physicalFrequencyClaim':False,'pixelEqualityQualityGate':False,'scope':'source/transform/anchor/clock integrity only; fourpose compatibility and recovery/hover semantics await independent review'};(P/'verification.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
