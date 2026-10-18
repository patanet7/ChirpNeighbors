from pathlib import Path
from PIL import Image,__version__ as pillow_version
import numpy as np,json,hashlib
P=Path(__file__).parent;R=P.parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def fid(im):return 'frame.sha256.'+hashlib.sha256(f'RGBA8;{im.width}x{im.height};'.encode()+im.tobytes()).hexdigest()
source=Image.open(R/'source-reference/neutral192.png').convert('RGBA');nn=source.resize((186,186),Image.Resampling.NEAREST);a=np.array(nn);mask=a[:,:,3]>=128
reference=np.array(Image.open(R/'ground-idle186.png'));assert np.array_equal(reference[:,:,3],mask.astype(np.uint8)*255)
rows=[]
for n in [56,48,40,32,24,16]+list(range(15,1,-1)):
 q=Image.fromarray(a[:,:,:3][mask].reshape(1,-1,3),'RGB').quantize(colors=n-1,method=Image.Quantize.MEDIANCUT,dither=Image.Dither.NONE).convert('RGB');b=np.zeros((186,186,4),np.uint8);b[:,:,:3][mask]=np.array(q).reshape(-1,3);b[:,:,3][mask]=255;im=Image.fromarray(b,'RGBA');name=f'crow-ground-idle186-total{n}.png';im.save(P/name)
 assert np.array_equal(reference[:,:,3],b[:,:,3]) and np.all(b[:,:,:3][~mask]==0)
 rows.append({'requestedTotalColorLimit':n,'actualRGBAColors':len(np.unique(b.reshape(-1,4),axis=0)),'opaqueRGBColorLimit':n-1,'file':name,'PNGsha256':sha(P/name),'derivativeDecodedRGBAId':fid(im),'alphaMaskSHA256':hashlib.sha256(b[:,:,3].tobytes()).hexdigest(),'alphaMaskByteIdenticalToReviewed64Color':True,'newDrawings':0,'nativeCalls':0})
receipt={'kind':'additive-palette-variant-study','newDrawings':0,'nativeCalls':0,'sourceFrameId':'frame.sha256.54329ae7d715c698c9be4e025d0841adc4bff478fa10b080a88d8d141db3ffd5','inputSource192PNGsha256':sha(R/'source-reference/neutral192.png'),'reviewed64ColorPNGsha256':sha(R/'ground-idle186.png'),'wholeCanvasNearest':[192,186],'alphaThreshold':128,'opaqueAlpha':255,'transparentRGBA':[0,0,0,0],'paletteAlgorithm':'Pillow MEDIANCUT on row-major opaque-surviving RGB only','dither':'NONE','PillowVersion':pillow_version,'bodyFit':False,'perFootTranslation':False,'painting':False,'variants':rows}
(P/'variant-generation-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(rows))
