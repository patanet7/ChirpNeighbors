from PIL import Image,ImageDraw
from pathlib import Path
import numpy as np,json,hashlib
P=Path(__file__).parent
imgs={p.stem:Image.open(p).convert('RGBA') for p in (P/'source').glob('*.png')}
assets=[]
for k,im in imgs.items():
 a=np.array(im)[:,:,3]; y,x=np.where(a>=128)
 assets.append(dict(id=k,path=f'source/{k}.png',sha256=hashlib.sha256((P/'source'/f'{k}.png').read_bytes()).hexdigest(),size=list(im.size),alpha128_bbox=[int(x.min()),int(y.min()),int(x.max()+1),int(y.max()+1)],transparent_fraction=float((a==0).mean()),partial_alpha_fraction=float(((a>0)&(a<255)).mean())))
 if k!='maple-leaf-poses':
  im.resize((512,512),Image.Resampling.NEAREST).save(P/'runtime'/f'{k}.png')
leaf=imgs['maple-leaf-poses']; frames=[]
for i in range(3):
 f=leaf.crop((i*724,0,(i+1)*724,724));f.save(P/'runtime'/f'maple-leaf-pose-{i+1}-full.png');f.resize((128,128),Image.Resampling.NEAREST).save(P/'runtime'/f'maple-leaf-pose-{i+1}.png');frames.append(f)
A=np.array(imgs['maple-summer-foliage']);B=np.array(imgs['maple-autumn-foliage']);am=A[:,:,3]>=128;bm=B[:,:,3]>=128
H=np.array(imgs['arrowwood-healthy']);D=np.array(imgs['arrowwood-dry']);mask=(H[:,:,3]>128)&(D[:,:,3]>128);mask[:1120]=False
metrics={'season_alpha128_iou':float((am&bm).sum()/(am|bm).sum()),'season_identical_alpha_fraction':float((A[:,:,3]==B[:,:,3]).mean()),'shrub_root_opaque_rgb_mean_absolute_difference':float(np.abs(H[:,:,:3].astype(float)-D[:,:,:3])[mask].mean()),'shrub_root_pixels_equal_fraction':float((H[1120:]==D[1120:]).all(axis=2).mean()),'registration':'common full canvas; generated contours not pixel-invariant; shrub root approx 2px drift and bark changes; runtime admission blocked pending authored correction'}
(P/'provenance'/'registration.json').write_text(json.dumps(metrics,indent=2))
wood=imgs['maple-wood'];summer=Image.alpha_composite(wood,imgs['maple-summer-foliage']);autumn=Image.alpha_composite(wood,imgs['maple-autumn-foliage']);
items=[('Maple summer composite',summer),('Maple autumn composite',autumn),('Maple winter / wood only',wood),('Arrowwood flowering',imgs['arrowwood-healthy']),('Arrowwood dry stress',imgs['arrowwood-dry']),('Generated leaf poses',leaf)]
board=Image.new('RGB',(1500,1080),'#e5e2d8');d=ImageDraw.Draw(board)
for i,(label,im) in enumerate(items):
 x=(i%3)*500;y=(i//3)*540;d.text((x+12,y+10),label,fill='#243135'); bg=Image.new('RGBA',(480,490),'#35464b'); cp=im.copy();cp.thumbnail((470,470));bg.alpha_composite(cp,((480-cp.width)//2,(490-cp.height)//2));board.paste(bg.convert('RGB'),(x+10,y+35))
board.save(P/'review'/'contact-sheet.png')
for label,im in items[:3]:
 im.save(P/'review'/(label.split()[1]+'-composite.png'))
manifest={'version':1,'region':'Eastern North America reference candidates; NOT San Diego local pack','status':'unapproved candidates; not runtime integrated','species':[{'id':'acer_rubrum','name':'Red maple','source':'https://plants.ces.ncsu.edu/plants/acer-rubrum/','states':['bare wood/winter','summer foliage layer','autumn foliage layer','3 detached leaf poses']},{'id':'viburnum_dentatum','name':'Southern arrowwood','source':'https://plants.ces.ncsu.edu/plants/viburnum-dentatum/','states':['healthy spring flowering complete shrub','drought-stressed complete shrub']}],'assets':assets,'world_assumptions':{'viewport':[960,540],'tree_box':[256,320],'tree_canvas_world':[256,256],'shrub_canvas_world':[100,100],'leaf_world':[8,8]},'anchors':{'status':'proposed from visual inspection, not authored engine validation','maple_root_source':[650,1230],'maple_branch_split':[650,860],'maple_foliage_pivot':[650,780],'arrowwood_root_source':[634,1207],'leaf_cell_pivot':[362,362]},'wind':{'implemented':False,'proposal':'Keep wood/root stationary. Canopy mask upper y0..950 with deformation weight rising above y780. Shrub pin y1120..1254 and bend upper stems lightly. Seam test required. No independent branch cluster masks delivered.'},'animation':{'leaf':'3 generated distinct poses, ping-pong preview at 6 fps; changing shape is generated, playback only is scripted','plant':'static states only; no runtime animation'},'runtime_derivatives':{'plant_canvas':[512,512],'method':'uniform nearest neighbor entire canvas; no auto crop','leaf':'724-square exact cell extraction then uniform 128-square nearest neighbor','admitted':False},'registration':metrics,'rights':'OpenAI built-in generated originals; model revision and seed not exposed. Biological sources are text references only, no third-party artwork copied. Rights/exclusivity not legally certified.','missing':['San Diego local plants (next pack)','spring maple','arrowwood fruit/autumn/winter','wet and snow overlays','authored wind masks','pixel exact root correction','engine admission and QA']}
(P/'manifest.json').write_text(json.dumps(manifest,indent=2))
print(json.dumps(metrics,indent=2))
