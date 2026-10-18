"""Candidate-only export, followed by the one external shared structural checker."""
from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,shutil,subprocess
P=Path(__file__).parent;R=P.parents[1];S=R/'motion/sd20-anna-phoebe-towhee-v1/california_towhee/actions';repo=Path('/workspace/runtime-contract-checkpoint8');N=112
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def fid(im):return 'frame.sha256.'+hashlib.sha256(f'RGBA8;{im.width}x{im.height};'.encode()+im.tobytes()).hexdigest()
assert subprocess.check_output(['git','-C',str(repo),'rev-parse','HEAD'],text=True).strip()=='3b20073eb96dc9e1d7385746dcfd8316eed85641'
assert sha(repo/'src/lib/server/asset-pipeline/package.ts')=='b936301983382339392ffdb5cba9f36af1018f9a55513c44bbbee81c36080088'
assert sha(repo/'src/lib/server/pipeline/canonical.ts')=='28c4c5f7bd522ac9709ce66df07c674e9f9a5ec53d35255c4a0ebfdef4637320'
assert sha(repo/'src/lib/pipeline/canonical-json.ts')=='68090d71be5ae2b04432c98fc57f93571b44ea8a54495a08bf39109bb9b37ebf'
for d in ['originals','source112','runtime112']:(P/d).mkdir(exist_ok=True)
images=[];spec=[('neutral','open'),('blink','blink'),('look','look')];idx=((2*np.arange(N)+1)*96)//(2*N)
for name,oldname in spec:
 old=Image.open(S/(oldname+'-96.png'));assert old.mode=='RGBA';shutil.copyfile(S/(oldname+'-96.png'),P/'originals'/(name+'96.png'));a=np.array(old);im=Image.fromarray(a[idx[:,None],idx[None,:]].copy(),'RGBA');im.save(P/'source112'/(name+'.png'));images.append(np.array(im))
masks=[a[:,:,3]>=128 for a in images];rgb=np.concatenate([a[:,:,:3][m]for a,m in zip(images,masks)]);quant=np.array(Image.fromarray(rgb.reshape(1,-1,3),'RGB').quantize(colors=63,method=Image.Quantize.MEDIANCUT,dither=Image.Dither.NONE).convert('RGB')).reshape(-1,3);cursor=0;rows=[]
for (name,_),a,mask in zip(spec,images,masks):
 n=int(mask.sum());out=np.zeros((N,N,4),np.uint8);out[:,:,:3][mask]=quant[cursor:cursor+n];cursor+=n;out[:,:,3][mask]=255;im=Image.fromarray(out,'RGBA');f='runtime112/'+name+'.png';im.save(P/f);rows.append({'phase':name,'png':f,'PNGsha256':sha(P/f),'decodedRGBAId':fid(im)})
cfg={'expectedPackageSHA256':sha(repo/'src/lib/server/asset-pipeline/package.ts'),'expectedCanonicalSHA256':sha(repo/'src/lib/server/pipeline/canonical.ts'),'canvas':{'width':N,'height':N},'logicalPixelSize':1,'paletteLimit':64,'frames':rows};(P/'canonical-input.json').write_text(json.dumps(cfg,indent=2)+'\n');print(json.dumps({'candidatePNGs':rows,'area':37632,'nativeCalls':0,'newDrawings':0,'repository':str(repo)}))
