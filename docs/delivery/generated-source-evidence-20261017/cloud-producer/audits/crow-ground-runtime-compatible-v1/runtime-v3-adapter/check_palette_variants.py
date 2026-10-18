from pathlib import Path
from PIL import Image
import json,hashlib,subprocess
A=Path(__file__).resolve().parent;P=A.parent;V=P/'palette-variants';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();original=Image.open(P/'ground-idle186.png');alpha=original.getchannel('A').tobytes();old=Image.open(P/'source-reference/neutral192.png').resize((186,186),Image.Resampling.NEAREST);opaque=[p[:3]for p in old.get_flattened_data()if p[3]>=128];rgb=Image.new('RGB',(len(opaque),1));rgb.putdata(opaque);rows=[]
def count_rects(im):
 rects=[];prior={}
 for y in range(im.height):
  cur={};x=0
  while x<im.width:
   p=im.getpixel((x,y));start=x;x+=1
   if not p[3]:continue
   while x<im.width and im.getpixel((x,y))==p:x+=1
   k=(start,x-start,p[:3]);i=prior.get(k)
   if i is None:cur[k]=len(rects);rects.append([start,y,x-start,1,p[:3]])
   else:rects[i][3]+=1;cur[k]=i
  prior=cur
 return len(rects)
for n in [56,48,40,32,24,16]:
 f=V/f'crow-ground-idle186-total{n}.png';before=sha(f);im=Image.open(f);im.load();assert im.mode=='RGBA'and im.size==(186,186)and im.getchannel('A').tobytes()==alpha
 colors=set(im.get_flattened_data());assert len(colors)<=n and all(p[3]in[0,255]and(p[3]or p==(0,0,0,0))for p in colors)
 q=iter(rgb.quantize(colors=n-1,method=Image.Quantize.MEDIANCUT,dither=Image.Dither.NONE).convert('RGB').get_flattened_data());repro=[tuple(next(q))+(255,)if p[3]>=128 else(0,0,0,0)for p in old.get_flattened_data()];assert repro==list(im.get_flattened_data())
 result=subprocess.run(['node','--experimental-strip-types',str(A/'codec-check.mjs'),str(f)],capture_output=True,text=True);actual=json.loads(result.stdout);assert result.returncode==1 and actual['passed']is False and actual['errorClass']=='PermanentStageError'and actual['error']=='Normalized rectangle budget exceeded';count=count_rects(im);assert sha(f)==before
 rows.append({'totalColorLimit':n,'PNG':f.name,'PNGsha256':before,'actualRGBAColors':len(colors),'pixelMaskExact':True,'deterministicPixelReproductionExact':True,'diagnosticUncappedRectangles':count,'actualStrictCodec':actual})
assert [r['diagnosticUncappedRectangles']for r in rows]==[5290,5230,5102,5037,4806,4362]
r={'status':'All six authorized total-color variants fail actual strict codec; no selected variant','baseline64Rectangles':5332,'rows':rows,'actualCodecExtractionReceiptSHA256':sha(A/'codec-extraction-receipt.json'),'unchangedStrictBudgets':{'perFrame':4096,'total':16384,'area':65536},'allAlphaMasksByteIdenticalToReviewed64PNG':True,'sourcePixelOutputsWritten':False,'fullManifestValidation':False,'canonicalRuntimeAdmission':False,'newDrawings':0,'nativeCalls':0};f=A/'independent-palette-variants-check.json';f.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'sha256':sha(f),'allActualStrictFail':True,'counts':[r['diagnosticUncappedRectangles']for r in rows]}))
