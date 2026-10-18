from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib,numpy as np
P=Path(__file__).parent;im=Image.open(P/'original.png').convert('RGBA');assert im.size==(1254,1254);N=627;names=['compression','tucked-air','landing-reach-air','supported-settle'];records=[]
(P/'cells627').mkdir(exist_ok=True);(P/'frames96').mkdir(exist_ok=True);reconstruction=Image.new('RGBA',im.size)
for i,name in enumerate(names):
 x=(i%2)*N;y=(i//2)*N;cell=im.crop((x,y,x+N,y+N));cell.save(P/'cells627'/(name+'.png'));out=cell.resize((96,96),Image.Resampling.NEAREST);out.save(P/'frames96'/(name+'.png'));reconstruction.paste(cell,(x,y));a=np.array(out);yy,xx=np.where(a[:,:,3]>=128);bbox=[int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)];records.append({'pose':name,'cellRect':[x,y,N,N],'bboxAlpha128':bbox,'visibleWidthWorld':bbox[2]-bbox[0],'sourceCellPixelsPerWorldUnit':N/96,'edgePositiveAlpha':int((np.array(cell)[[0,-1],:,3]>0).sum()+(np.array(cell)[:,[0,-1],3]>0).sum())})
assert reconstruction.tobytes()==im.tobytes();
for r in records:
 a=np.array(Image.open(P/'cells627'/(r['pose']+'.png')).convert('RGBA'));edges=np.concatenate([a[0,:,3],a[-1,:,3],a[:,0,3],a[:,-1,3]]);r['edgeMaxAlpha']=int(edges.max());r['edgeAlpha128Count']=int((edges>=128).sum())
(P/'cell-extraction-receipt.json').write_text(json.dumps({'method':'exactfourquadrants,nocroppingalphatransform/translation/paint','originalCanvas':[1254,1254],'cellCanvas':[627,627],'completeRGBAReconstructionExact':True,'allNativePixelsAssignedOnce':True,'referenceCanvas':[1024,1024],'outputCanvas':[96,96],'referenceWholeCanvasScale':96/1024,'generatedCellWholeCanvasScale':96/627,'sharedCellTransform':True,'perPoseFit':False,'records':records},indent=2)+'\n')
sheet=Image.new('RGBA',(1000,600),'#e5e0cd');d=ImageDraw.Draw(sheet)
for i,name in enumerate(names):
 out=Image.open(P/'frames96'/(name+'.png')).convert('RGBA');pane=Image.new('RGBA',(96,96),'#e5e0cd');pane.alpha_composite(out);sheet.alpha_composite(pane,(i*250+10,25));d.text((i*250+5,5),name,fill='#273d2e');sheet.alpha_composite(pane.resize((192,192),Image.Resampling.NEAREST),(i*250+5,150));crop=pane.crop((35,60,90,96));sheet.alpha_composite(crop.resize((220,144),Image.Resampling.NEAREST),(i*250+5,375));d.text((i*250+5,535),str(records[i]['bboxAlpha128']),fill='#273d2e')
sheet.save(P/'pose-feet-diagnostic.png');print(json.dumps(records,indent=2))
