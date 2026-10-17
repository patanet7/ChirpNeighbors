from PIL import Image,ImageDraw
import hashlib,json,pathlib
root=pathlib.Path('/workspace/scratch/4bfe0669552a/bird_candidates/output')
files=[('Northern cardinal (male)','northern-cardinal-male-standing.png',62,[1035,978],[[902,950],[1100,978]]),('Mourning dove','mourning-dove-standing.png',78,[1070,930],[[956,916],[1175,930]])]
canvas=Image.new('RGB',(1100,790),'#eee9db');d=ImageDraw.Draw(canvas)
d.text((24,18),'CHIRPNEIGHBORS | BACKYARD BIRD SOURCE CANDIDATES | UNAPPROVED',fill='#242c2c')
d.text((24,40),'Static open-eye poses. Proposed game widths: cardinal 62 px / dove 78 px / blue jay reference 72 px.',fill='#242c2c')
assets=[]
for row,(name,f,w,anchor,contacts) in enumerate(files):
 im=Image.open(root/'source'/f).convert('RGBA');a=im.getchannel('A');bbox=a.point(lambda v:255 if v>127 else 0).getbbox();crop=im.crop(bbox)
 height=round(crop.height*w/crop.width);game=crop.resize((w,height),Image.Resampling.NEAREST)
 y=75+row*350
 d.text((24,y),name,fill='#242c2c')
 for col,bg in enumerate(['#ebe7d8','#182a30']):
  x=24+col*535; panel=Image.new('RGBA',(510,310),bg)
  source=crop.copy();source.thumbnail((295,260),Image.Resampling.NEAREST);panel.alpha_composite(source,(10,10))
  panel.alpha_composite(game,(330,30));panel.alpha_composite(game.resize((w*2,height*2),Image.Resampling.NEAREST),(330,130))
  pd=ImageDraw.Draw(panel);fg='#17272a' if col==0 else '#f0eadc';pd.text((330,12),'1x game scale',fill=fg);pd.text((330,110),'2x nearest',fill=fg)
  canvas.paste(panel.convert('RGB'),(x,y+22))
 hist=a.histogram();assets.append({'name':name,'file':'source/'+f,'sha256':hashlib.sha256((root/'source'/f).read_bytes()).hexdigest(),'canvas_px':im.size,'alpha_range':a.getextrema(),'alpha_zero_pixels':hist[0],'alpha_partial_pixels':sum(hist[1:255]),'alpha_opaque_pixels':hist[255],'alpha_gt_127_bbox':bbox,'proposed_silhouette_world_width_px':w,'proposed_height_px':height,'scale_basis':'Art-direction estimate relative to existing blue-jay width 72 px; not measured biology. Pose changes silhouette extent.','source_foot_anchor_estimate':anchor,'source_contact_estimates':contacts,'coordinate_system':'Uncropped source pixels, top-left origin; manually estimated contacts, validate before adapter.','animation':'static open-eye only; no blink or animation coherence validated','runtime_approved':False})
canvas.save(root/'chirp-backyard-birds-review.png')
(root/'manifest.json').write_text(json.dumps({'status':'unapproved source candidates only','generation':'built-in imagegen; originals preserved unchanged','reference':{'library_file_id':'[private-source-reference-retained-locally]','member':'source/blue-jay-standing-v2.png','sha256':'407a5c6b30f3190cf877d212b5ccc518c545b4f81aa8f6ec2214337a2f8aea72'},'assets':assets,'qa':'Preview uses actual RGBA compositing on light and dark, nearest-neighbor game scaling. Alpha is nonbinary, maximum 254. Transparent RGB is not evaluated as visible glow. No alpha repair or production resampling applied. No runtime files changed.'},indent=2))
