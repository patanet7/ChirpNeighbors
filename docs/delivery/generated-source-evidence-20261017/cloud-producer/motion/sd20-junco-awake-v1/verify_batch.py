from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
P=Path(__file__).parent;sha=lambda b:hashlib.sha256(b).hexdigest();M=json.loads((P/'PRIMARY-SOURCE-MANIFEST.json').read_text());A=Image.open(P/M['original']).convert('RGBA');assert sha((P/M['original']).read_bytes())==M['originalSHA256'];assert sha((P/M['prompt']).read_bytes())==M['promptSHA256'];checks=['original and prompt hashes'];ids=[]
for f in M['frames']:
 src=Image.open(P/f['sourcePNG']).convert('RGBA');r=f['registration'];expected=Image.new('RGBA',(1024,1024));crop=A.crop(r['sourceAtlasRect']);expected.paste(crop,tuple(r['integerTranslation']));assert src.tobytes()==expected.tobytes()
 dx,dy=r['integerTranslation']
 ca=np.array(crop);assert dx>=0 and dy>=0 and dx+crop.width<=1024 and dy+crop.height<=1024;assert sha((P/f['sourcePNG']).read_bytes())==f['sourcePNGsha256'];assert f['sourceFrameId']=='frame.sha256.'+sha(b'RGBA8;1024x1024;'+src.tobytes());out=Image.open(P/f['outputPNG']).convert('RGBA');assert out.tobytes()==src.resize((192,192),Image.Resampling.NEAREST).tobytes();assert sha((P/f['outputPNG']).read_bytes())==f['outputPNGsha256'];ids.append(f['sourceFrameId'])
assert len(set(ids))==2;checks+=['two exact registered source IDs','integer source registration with no positive-alpha clipping','whole-canvas nearest outputs and PNG hashes']
T=json.loads((P/'texture-review-manifest.json').read_text());atlas=Image.open(P/'idle-blink-atlas192.png').convert('RGBA');assert T['source']['sha256']==sha((P/'idle-blink-atlas192.png').read_bytes())
for i,f in enumerate(T['frames']):
 tile=atlas.crop((i*192,0,(i+1)*192,192));assert tile.tobytes()==Image.open(P/M['frames'][i]['outputPNG']).convert('RGBA').tobytes();assert abs(f['world']['width']*f['sourcePixelsPerWorldUnit']-192)<1e-9
 for c in f['contacts']:assert tile.getpixel((c['x'],c['y']))[3]>0
assert T['frames'][0]['contacts']==T['frames'][1]['contacts'];assert T['frames'][0]['pivot']==T['frames'][1]['pivot'];checks+=['atlas, constant technical contacts, pivot and shared scale']
for fn in ['idle-blink.apng','yard-scale-blink.apng','Junco-Awake-Blink-Yard-Scale.gif']:
 im=Image.open(P/fn);assert im.n_frames==3;dur=[];raw=[]
 for i in range(3):im.seek(i);dur.append(im.info['duration']);raw.append(im.convert('RGBA').tobytes())
 assert dur==[2000,100,900];assert raw[0]==raw[2];assert raw[0]!=raw[1]
checks+=['30Hz timing, actual changed blink pixels and identical loop endpoints']
# Eye diagnostics distinguish actual pixels; semantic judgment stays with reviewers.
eye=[]
for f in M['frames']:
 a=np.array(Image.open(P/f['sourcePNG']).convert('RGBA'));roi=a[355:388,742:775];bright=(roi[:,:,:3].min(axis=2)>170)&(roi[:,:,3]>=128);dark=(roi[:,:,:3].max(axis=2)<40)&(roi[:,:,3]>=128);eye.append({'pose':f['pose'],'brightCatchlightPixels':int(bright.sum()),'darkEyeRegionPixels':int(dark.sum())})
measure=json.loads((P/'scale-contact-measurements.json').read_text());foot=[]
for name in ['awake','closed']:
 a=np.array(Image.open(P/(name+'192.png')));y,x=np.indices(a.shape[:2]);parts=[]
 for side in [x<122,x>=122]:
  yy,xx=np.where((a[:,:,3]>=128)&side&(x>=90)&(x<=153)&(y>=138)&(y<=150));parts.append({'bbox':[int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)],'lowestVisibleRow':int(yy.max()),'centroid':[float(xx.mean()),float(yy.mean())],'alpha128Pixels':len(xx)})
 foot.append({'pose':name,'feetHeuristic':parts})
measure['outputFootCoreHeuristic']=foot;measure['outputFootCoreHeuristicNote']='Fixed output ROI threshold128 and X split; not anatomical tracking or proof of contact. Base row/bounds and visible artifacts require review.';measure['maxPairwiseFootCentroidDisplacementOutputPixels']=max(float(np.linalg.norm(np.array(a['centroid'])-b['centroid'])) for a,b in zip(foot[0]['feetHeuristic'],foot[1]['feetHeuristic']));measure['maxPairwiseFootCentroidDisplacementWorld']=measure['maxPairwiseFootCentroidDisplacementOutputPixels']/measure['density'];measure['maxPairwiseFootBaselineRowChangeOutputPixels']=max(abs(a['lowestVisibleRow']-b['lowestVisibleRow']) for a,b in zip(foot[0]['feetHeuristic'],foot[1]['feetHeuristic']));(P/'scale-contact-measurements.json').write_text(json.dumps(measure,indent=2)+'\n')
result={'passed':True,'checks':checks,'newDrawings':2,'newCanons':0,'eyeRegionDiagnostics':eye,'interpretation':'Source eye crop visibly round-open with catchlight versus thin closed lid; numeric counts alone are not an artistic acceptance gate.','appBound':False,'SharpCanonicalAdmission':False};(P/'verification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
