from PIL import Image
from pathlib import Path
import json,hashlib
p=Path(__file__).parent
im=Image.open(p/'originals/crow-walk-v2.png').convert('RGBA')
anchors=[(530,345),(502,345),(530,313),(502,313)]
target=(254,240);scale=.44;frames=[];records=[]
for i,(ax,ay) in enumerate(anchors):
 x=i%2*768;y=i//2*512
 c=im.crop((x,y,x+768,y+512)).resize((338,225),Image.Resampling.NEAREST)
 pos=(round(target[0]-ax*scale),round(target[1]-ay*scale))
 f=Image.new('RGBA',(384,384));f.paste(c,pos);f.save(p/'frames'/f'crow-walk-v2-{i}.png');frames.append(f)
 records.append({'frame':i,'source_cell':[x,y,768,512],'estimated_torso_root_local':[ax,ay],'runtime_root':list(target),'translation':list(pos),'duration_ms':180})
frames[0].save(p/'previews/crow-walk-v2.apng',save_all=True,append_images=frames[1:],duration=180,loop=0,disposal=0,blend=0)
g=[]
for f in frames:
 b=Image.new('RGBA',(384,384),(225,220,199,255));b.alpha_composite(f);g.append(b.convert('RGB'))
g[0].save(p/'previews/crow-walk-v2.gif',save_all=True,append_images=g[1:],duration=180,loop=0)
a=Image.new('RGBA',(768,768))
for i,f in enumerate(frames):a.paste(f,((i%2)*384,(i//2)*384))
a.save(p/'crow-walk-v2-atlas.png')
# Playback comparison, before and after, equivalent fixed canvas. No art recoloring.
old=Image.open(p/'previews/crow-walk.gif');compare=[]
for i,f in enumerate(g):
 old.seek(i);b=Image.new('RGB',(768,384),(225,220,199));b.paste(old.convert('RGB'),(0,0));b.paste(f,(384,0));compare.append(b)
compare[0].save(p/'previews/crow-walk-before-after.gif',save_all=True,append_images=compare[1:],duration=180,loop=0)
# Alpha-qualified plumage metric excludes black hidden transparent RGB.
metrics={}
for v in ['crow-walk','crow-walk-v2']:
 image=Image.open(p/'originals'/f'{v}.png').convert('RGBA')
 pix=[(r,g,b) for r,g,b,a in image.getdata() if a>200 and 15<(r+g+b)/3<180]
 metrics[v]={'sample_pixels':len(pix),'mean_blue_minus_red':sum(b-r for r,g,b in pix)/len(pix)}
report={'imagegen_calls_total':8,'additional_calls_since_v1':2,'lineage':'v1 crow walk rejected by user for blue palette and alignment; v2 edit and translation-only registration','uniform_scale':scale,'frames':records,'registration_note':'Visually estimated body/upper-thigh landmark, not bounding box. Constant torso root, zero intended root travel. Foot contact is not pinned to avoid switching support-foot snap. No per-frame scale changes. Residual feather/anatomical drift and weak near/far leg alternation remain.','palette_metrics':metrics,'review_status':'candidate_requires_user_review','new_queued_original':'crow-hop generated but remains blue and not promoted','raven_walk':'not generated; paused for user correction'}
(p/'crow-walk-v2-review.json').write_text(json.dumps(report,indent=2))
(p/'hashes.json').write_text(json.dumps({str(f.relative_to(p)):hashlib.sha256(f.read_bytes()).hexdigest() for f in p.rglob('*') if f.is_file() and f.name!='hashes.json'},indent=2))
print(json.dumps(report,indent=2))
