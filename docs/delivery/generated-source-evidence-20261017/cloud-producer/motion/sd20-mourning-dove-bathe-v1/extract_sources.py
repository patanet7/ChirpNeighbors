from pathlib import Path
from PIL import Image,ImageDraw
import hashlib,json,numpy as np
P=Path(__file__).parent;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();original=Image.open(P/'original.png');assert original.mode=='RGBA' and original.size==(1536,1024);(P/'cells512').mkdir(exist_ok=True);(P/'frames192').mkdir(exist_ok=True);phases=['approach','settle','dip','wingflutter','shake','exit-preen'];rows=[];reconstruct=Image.new('RGBA',original.size)
for i,phase in enumerate(phases):
 x=(i%3)*512;y=(i//3)*512;cell=original.crop((x,y,x+512,y+512));cell.save(P/'cells512'/(phase+'.png'));render=cell.resize((192,192),Image.Resampling.NEAREST);render.save(P/'frames192'/(phase+'.png'));reconstruct.paste(cell,(x,y));a=np.array(render);yy,xx=np.where(a[:,:,3]>=128);bbox=[int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)];fid='frame.sha256.'+hashlib.sha256(b'RGBA8;512x512;'+cell.tobytes()).hexdigest();rows.append({'sourceFrameId':fid,'speciesId':'mourning_dove','pose':phase,'sourcePNG':'cells512/'+phase+'.png','sourcePNGsha256':sha(P/'cells512'/(phase+'.png')),'sourceCanvas':[512,512],'sourceOriginalRect':[x,y,512,512],'renderPNG':'frames192/'+phase+'.png','renderPNGsha256':sha(P/'frames192'/(phase+'.png')),'renderCanvas':[192,192],'renderScaleWholeCell':192/512,'bboxAlpha128':bbox,'bodyTouchesRenderBoundary':{'left':bool((a[:,0,3]>=128).any()),'right':bool((a[:,-1,3]>=128).any()),'top':bool((a[0,:,3]>=128).any()),'bottom':bool((a[-1,:,3]>=128).any())},'perPoseFit':False,'snap':False,'paint':False,'translation':False,'geometryReviewed':False,'supportWorld':None})
assert reconstruct.tobytes()==original.tobytes();assert len({r['sourceFrameId'] for r in rows})==6
(P/'cell-extraction-receipt.json').write_text(json.dumps({'original':'original.png','originalSHA256':sha(P/'original.png'),'nativeCanvas':list(original.size),'grid':[3,2],'equalSquareCellEdge':512,'cells':rows,'allNativeDecodedRGBAPreservedAcrossCells':True,'wholeCellDirectRenderOnly':True,'newActualDrawings':6,'conditioningCopiesCountedAsDrawings':0,'cropClippingQualification':'Exact equal native cells retained. Any model cross-cell bird content remains visible/clipped by cell ownership; no component-mask reassignment, footsnap, translation or repair.'},indent=2)+'\n')
# Real192-world output with same192cell for all poses; baseline visible118world preserved exactly.
ims=[('EXACT OLD AWAKE',Image.open(P/'reused-awake192.png'))]+[(r['pose'],Image.open(P/r['renderPNG'])) for r in rows]
sheet=Image.new('RGBA',(4*212,2*230),'#e6dfcc');dr=ImageDraw.Draw(sheet)
for i,(name,im) in enumerate(ims):x=(i%4)*212;y=(i//4)*230;dr.text((x+4,y+3),name,fill='#263c30');bg=Image.new('RGBA',(192,192),'#ded8c3');bg.alpha_composite(im);sheet.paste(bg,(x+4,y+25))
sheet.save(P/'source-normal192-contact-sheet.png')
# Grid overlay is a separate diagnostic; original unchanged.
grid=original.copy();dr=ImageDraw.Draw(grid)
for x in [512,1024]:dr.line((x,0,x,1024),fill='#e84973',width=2)
dr.line((0,512,1536,512),fill='#e84973',width=2);grid.save(P/'original-grid-diagnostic.png')
print(json.dumps({'originalSHA256':sha(P/'original.png'),'newActualDrawings':6,'frames':[{'pose':r['pose'],'sourceFrameId':r['sourceFrameId'],'bboxAlpha128':r['bboxAlpha128'],'boundary':r['bodyTouchesRenderBoundary']} for r in rows],'allNativeRGBAReconstructsExactly':True}))
