from pathlib import Path
from PIL import Image
import json,hashlib,numpy as np,subprocess
P=Path(__file__).parent;R=P.parents[1];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();J=lambda n:json.loads((P/n).read_text())
def fid(im):return 'frame.sha256.'+hashlib.sha256(f'RGBA8;{im.width}x{im.height};'.encode()+im.tobytes()).hexdigest()
m=J('family-source-manifest.json');assert m['nativeCalls']==m['newDrawings']==0 and m['existingDistinctDrawingsReused']==3 and m['candidateSourceArea']==24843
runtime=[];source=[]
for r in m['frames']:
 im=Image.open(P/r['canonicalBankSourcePNG']).convert('RGBA');assert fid(im)==r['sourceFrameId'] and sha(P/r['canonicalBankSourcePNG'])==r['canonicalBankSourcePNGsha256'];old=Image.open(P/r['legacy96PNG']);s=Image.open(P/r['source91PNG']);run=Image.open(P/r['runtime91PNG']);assert old.mode==s.mode==run.mode=='RGBA'
 for y in range(91):
  for x in range(91):assert s.getpixel((x,y))==old.getpixel((((2*x+1)*96)//182,((2*y+1)*96)//182))
 assert fid(s)==r['source91DerivativeRGBAId'] and fid(run)==r['runtime91DerivativeRGBAId'];a=np.array(run);assert set(np.unique(a[:,:,3]))<={0,255} and np.all(a[:,:,:3][a[:,:,3]==0]==0);assert np.array_equal(a[:,:,3],(np.array(s)[:,:,3]>=128).astype(np.uint8)*255)
 runtime.append(run);source.append(s)
 assert all(p['RGBA'][3]==255 for p in r['runtimeFootProxies'])
for row in J('legacy-protection.json')['files']:assert sha(R/row['file'])==row['sha256']
colors=set().union(*[set(map(tuple,np.array(im).reshape(-1,4)))for im in runtime]);assert len(colors)==64
opaque=np.concatenate([np.array(im)[:,:,:3][np.array(im)[:,:,3]>=128]for im in source]);q=np.array(Image.fromarray(opaque.reshape(1,-1,3),'RGB').quantize(colors=63,method=Image.Quantize.MEDIANCUT,dither=Image.Dither.NONE).convert('RGB')).reshape(-1,3);cur=0
for s,run in zip(source,runtime):
 a=np.array(s);mask=a[:,:,3]>=128;n=int(mask.sum());b=np.zeros((91,91,4),np.uint8);b[:,:,:3][mask]=q[cur:cur+n];b[:,:,3][mask]=255;cur+=n;assert b.tobytes()==run.tobytes()
for name,indices,ms in [('blink',[0,1,0],[3000,100,3000]),('look',[0,2,0],[1000,400,1000])]:
 for variant,ims in [('source',source),('runtime',runtime)]:
  ap=Image.open(P/(name+'-'+variant+'.apng'));assert ap.n_frames==3 and ap.info['loop']==1
  for i,idx in enumerate(indices):ap.seek(i);assert ap.convert('RGBA').tobytes()==ims[idx].tobytes() and ap.info['duration']==ms[i]
js="""const assert=require('node:assert/strict'),{frameAt}=require('./player.js'),m=require('./family-source-manifest.json');for(const[t,ph]of[[0,'neutral'],[2999,'neutral'],[3000,'blink'],[3099,'blink'],[3100,'neutral'],[6100,'neutral']])assert.equal(frameAt(m,'blink',t).phase,ph);for(const[t,ph]of[[0,'neutral'],[999,'neutral'],[1000,'look'],[1399,'look'],[1400,'neutral'],[2400,'neutral']])assert.equal(frameAt(m,'look',t).phase,ph);assert.equal(frameAt(m,'look',2400).terminal,true);for(const t of[0,50000])assert.equal(frameAt(m,'idle',t).phase,'neutral');console.log('idle/blink/look boundaries PASS');"""
z=subprocess.run(['node','-e',js],cwd=P,capture_output=True,text=True,check=True)
# Read-only bank membership proof; no canonicalbank mutation.
bank=json.loads((R/'frame-bank.json').read_text());ids=set()
def visit(x):
 if isinstance(x,dict):
  for k,v in x.items():
   if k in ['frameId','sourceFrameId','registeredDerivativeFrameId'] and isinstance(v,str):ids.add(v)
   visit(v)
 elif isinstance(x,list):
  for v in x:visit(v)
visit(bank);assert all(r['sourceFrameId']in ids for r in m['frames'])
r={'status':'PASS deterministic source/codec derivative integrity only','nativeCalls':0,'newDrawings':0,'canonicalBankIDsResolve':True,'existingDrawings':3,'rawBlinkAliasIsSameDrawing':True,'uniform96to91ScalarRGBAProof':True,'commonBinaryPaletteReproduction':True,'commonColorsIncludingTransparent':64,'candidateArea':24843,'legacyProtectedUnchanged':True,'allProposedFootPixelsSurviveThreshold':True,'contactsAdmitted':False,'APNGsExactRGBAAndTiming':True,'nodeClocks':z.stdout.strip(),'actualCodecReceipt':'codec-verification.json','sourceFamilyVisualAcceptance':'PENDING independent91CSSreview','geometryReviewed':False,'supportWorld':None,'canonicalRuntimeZod':'NOT_RUN','MacAdmission':False};(P/'verification.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
