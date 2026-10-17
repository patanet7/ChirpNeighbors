from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib,zipfile
p=Path(__file__).parent
src=p.parent/'originals/crow-contact-source.png'; out=p/'opposite-contact-output.png'
frames=[];stats={}
for path,label in [(src,'SOURCE: near leg forward'),(out,'GUIDED TEST: near leg back, far leg forward')]:
 im=Image.open(path).convert('RGBA'); a=im.getchannel('A'); hist=a.histogram()
 stats[path.name]={'size':list(im.size),'alpha_zero':hist[0],'alpha_opaque':hist[255],'alpha_partial':sum(hist[1:255]),'alpha_max':max(i for i,n in enumerate(hist) if n),'alpha_nearly_opaque_250_to_255':sum(hist[250:]),'alpha_1_to_249':sum(hist[1:250]),'alpha_bbox':a.getbbox(),'corners':[im.getpixel(xy)[3] for xy in [(0,0),(im.width-1,0),(0,im.height-1),(im.width-1,im.height-1)]]}
 im=im.resize((768,512),Image.Resampling.NEAREST)
 f=Image.new('RGBA',(768,548),(231,228,216,255));f.alpha_composite(im,(0,36));d=ImageDraw.Draw(f);d.text((12,10),label,fill=(25,25,25,255));frames.append(f)
frames[0].save(p/'two-contact-comparison.gif',save_all=True,append_images=frames[1:],duration=900,loop=0)
frames[0].save(p/'two-contact-comparison.apng',save_all=True,append_images=frames[1:],duration=900,loop=0,disposal=0,blend=0)
review=Image.new('RGBA',(1536,548),(231,228,216,255));review.alpha_composite(frames[0]);review.alpha_composite(frames[1],(768,0));review.save(p/'side-by-side-review.png')
report={'status':'pass_opposite_leg_geometry_only','calls_this_experiment':1,'known_project_calls_total':12,'second_call':'not_needed_for_this_gate','fallback':'crow-walk-v2 unchanged','geometry':'Near leg goes down-left in foreground across far leg; far leg goes down-right behind. Genuine opposite geometry achieved. Support/load transfer and full gait remain unproved from one still.','appearance':'Neutral charcoal and recognizable head/bill/wing retained, but feather texture and lower chest/leg attachment shifted. Not pixel-identical torso preservation.','registration':'Output 1536x1024 vs source 768x512. Comparison uses uniform 0.5 scale only, no per-frame fitting/warping. No production root registration claimed.','alpha':stats,'preview':'Two held contact poses at 900 ms each. A/B comparison, NOT walk animation.','tool':'built-in image_gen','seed':'not exposed','model_version':'not exposed','cost':'not exposed','remaining':'Need anatomically credible passing/lift phases, toe contact and stance timing, body consistency, runtime pixel cleanup and loop QA.'}
(p/'review.json').write_text(json.dumps(report,indent=2))
files=[f for f in p.iterdir() if f.is_file() and f.name!='hashes.json']
(p/'hashes.json').write_text(json.dumps({f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in files},indent=2))
with zipfile.ZipFile('/workspace/shared/chirp-guided-opposite-contact-test.zip','w',zipfile.ZIP_DEFLATED) as z:
 for f in p.iterdir():
  if f.is_file():z.write(f,f.name)
 z.write(src,'input-crow-contact-source.png')
print(json.dumps(report,indent=2))
