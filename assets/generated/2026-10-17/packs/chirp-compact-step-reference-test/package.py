from pathlib import Path
from PIL import Image,ImageDraw
import hashlib,json,zipfile
p=Path(__file__).parent
f=[]
for src,label in [(p.parent/'originals/crow-contact-source.png','Earlier exaggerated stride (rejected)'),(p/'compact-step-output.png','Compact test: improved reach; still misses guide')]:
 im=Image.open(src).convert('RGBA').resize((768,512),Image.Resampling.NEAREST);b=Image.new('RGBA',(768,548),(231,228,216,255));b.alpha_composite(im,(0,36));ImageDraw.Draw(b).text((12,10),label,fill='black');f.append(b)
side=Image.new('RGBA',(1536,548));side.alpha_composite(f[0]);side.alpha_composite(f[1],(768,0));side.save(p/'compact-before-after.png')
f[0].save(p/'compact-before-after.gif',save_all=True,append_images=f[1:],duration=1000,loop=0)
(p/'hashes.json').write_text(json.dumps({x.name:hashlib.sha256(x.read_bytes()).hexdigest() for x in p.iterdir() if x.is_file() and x.name!='hashes.json'},indent=2))
with zipfile.ZipFile('/workspace/shared/chirp-compact-step-reference-test.zip','w',zipfile.ZIP_DEFLATED) as z:
 for x in p.iterdir():
  if x.is_file():z.write(x,x.name)
