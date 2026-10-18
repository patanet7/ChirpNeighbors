"""Independent PNG byte decoder plus runtime constraint/reproduction checks. No app admission."""
from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,struct,zlib
P=Path(__file__).parent;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();J=lambda n:json.loads((P/n).read_text())
r=J('transformation-receipt.json');m=J('runtime-idle-proposal.json');bind=J('runtime-binding-proposal.json');im=Image.open(P/'ground-idle186.png');a=np.array(im)
assert im.mode=='RGBA' and im.size==(186,186)
assert set(np.unique(a[:,:,3]))=={0,255} and np.all(a[:,:,:3][a[:,:,3]==0]==0)
assert len(np.unique(a.reshape(-1,4),axis=0))==64
assert len(m['frames'])==1 and m['atlas']['width']*m['atlas']['height']==34596<=65536
f=m['frames'][0];assert f['sourcePixelsPerWorldUnit']==1 and f['world']=={'width':186,'height':186} and f['contacts']==[]
assert f['pivot']=={'x':107.53125,'y':145.3125}
assert m['clips']==[{'id':'idle','tickRate':30,'loop':True,'frames':[{'frameId':f['id'],'durationTicks':120}]}]
assert bind['runtimeBitmapFiles']==['ground-idle186.png'] and bind['bitmap']['sha256']==sha(P/'ground-idle186.png') and bind['manifest']['sha256']==sha(P/'runtime-idle-proposal.json')
for n,h in r['sourceFiles'].items():assert sha(P/n)==h
old=Image.open(P/'source-reference/neutral192.png').convert('RGBA');pre=np.array(old.resize((186,186),Image.Resampling.NEAREST));mask=pre[:,:,3]>=128
q=Image.fromarray(pre[:,:,:3][mask].reshape(1,-1,3),'RGB').quantize(colors=63,method=Image.Quantize.MEDIANCUT,dither=Image.Dither.NONE).convert('RGB')
rebuild=np.zeros_like(a);rebuild[:,:,:3][mask]=np.array(q).reshape(-1,3);rebuild[:,:,3][mask]=255
assert rebuild.tobytes()==a.tobytes()
# Decode PNG independently of Pillow (PNG RGBA8 color type6, filter0..4, CRC validated).
b=(P/'ground-idle186.png').read_bytes();assert b[:8]==b'\x89PNG\r\n\x1a\n';offset=8;idat=b''
while offset<len(b):
 n=struct.unpack('>I',b[offset:offset+4])[0];k=b[offset+4:offset+8];d=b[offset+8:offset+8+n];crc=struct.unpack('>I',b[offset+8+n:offset+12+n])[0];assert zlib.crc32(k+d)&0xffffffff==crc
 if k==b'IHDR':w,h,depth,ct,co,fi,inter=struct.unpack('>IIBBBBB',d);assert (w,h,depth,ct,co,fi,inter)==(186,186,8,6,0,0,0)
 if k==b'IDAT':idat+=d
 offset+=12+n
raw=zlib.decompress(idat);stride=186*4;prev=[0]*stride;decoded=bytearray();types=[]
for row in range(186):
 start=row*(stride+1);ft=raw[start];types.append(ft);scan=list(raw[start+1:start+1+stride])
 for x in range(stride):
  left=scan[x-4] if x>=4 else 0;up=prev[x];ul=prev[x-4] if x>=4 else 0
  if ft==0:predict=0
  elif ft==1:predict=left
  elif ft==2:predict=up
  elif ft==3:predict=(left+up)//2
  elif ft==4:
   p=left+up-ul;ds=[abs(p-left),abs(p-up),abs(p-ul)];predict=[left,up,ul][ds.index(min(ds))]
  else:raise AssertionError('unsupported PNG filter')
  scan[x]=(scan[x]+predict)&255
 decoded.extend(scan);prev=scan
assert bytes(decoded)==im.tobytes()
# Original source packet was read-only. All copied selected inputs equal authoritative inputs.
S=P.parents[1]/'motion/sd20-crow-neutral-blink-v1'
for p in (P/'source-reference').iterdir():assert p.read_bytes()==(S/p.name).read_bytes()
pixelid='frame.sha256.'+hashlib.sha256(b'RGBA8;186x186;'+bytes(decoded)).hexdigest();assert pixelid==r['derivativeDecodedRGBAId']
sharp=J('sharp-decode-receipt.json');assert sharp['rawSHA256']==hashlib.sha256(im.tobytes()).hexdigest() and sharp['decodedRGBAId']==pixelid and sharp['RGBAColorsTotal']==64 and sharp['alphaValues']==[0,255]
result={'status':'PASS declared pixel/area/density constraints only','nativeCalls':0,'newDrawings':0,'sourceFrameIdRetained':r['sourceFrameIdRetained'],'derivativeDecodedRGBAId':pixelid,'RGBAColorsTotal':64,'opaqueRGBColors':63,'transparentRGBA':[0,0,0,0],'alphaValues':[0,255],'decodedAnimationArea':34596,'areaLimit':65536,'density':1,'allowedDensities':[1,2,4],'runtimeFrameCount':1,'unusedBlinkAtlas':False,'deterministicQuantizationReproduction':'PASS','independentPNGCRCAndFilterDecodeVsPillow':'PASS','PNGFilterTypes':sorted(set(types)),'actualSharpDecode':'PASS Sharp0.35.4 actualRGBA decode agrees with Pillow and independent PNG decoder','canonicalRuntimeZod':'NOT_RUN','expectedFullRuntimeSchema':'PENDING','geometryReviewed':False,'supportWorld':None,'appBound':False,'sourceInputsUnchanged':True,'wholeCanvasNearestOnly':True,'perFootSnapOrPainting':False,'contactApproval':'NONE; actual toe/claw inspection required beyond positive alpha'}
(P/'validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
