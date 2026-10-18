from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib
P=Path(__file__).parent;m=json.loads((P/'COHORT-SOURCE-MANIFEST.json').read_text());rows=[];frames=[('old-awake-comparison','reference/exact-awake136x80.png')]+[(r['phase'],r['outputPNG']) for r in m['frames']]
rect=(55,58,120,80);scale=5;w=(rect[2]-rect[0])*scale;h=(rect[3]-rect[1])*scale+25;sheet=Image.new('RGB',(w*3,h*3),'#d9d4bd');d=ImageDraw.Draw(sheet)
for i,(name,f) in enumerate(frames):
 im=Image.open(P/f).convert('RGBA');bg=Image.new('RGBA',im.size,'#d9d4bd');bg.alpha_composite(im);crop=bg.crop(rect).resize((w,h-25),Image.Resampling.NEAREST).convert('RGB');x=i%3*w;y=i//3*h;sheet.paste(crop,(x,y+25));d.text((x+3,y+5),name,fill='#24342b');floor=y+25+(76-rect[1])*scale;d.line((x,floor,x+w-1,floor),fill='#6298b6',width=1)
 pts=[{'point':pt,'RGBA':list(im.getpixel(tuple(pt))),'meaning':'old fixed raster reference only; not phase toe tracking/admitted contact'} for pt in [[69,75],[88,75]]]
 rows.append({'phase':name,'file':f,'PNGsha256':hashlib.sha256((P/f).read_bytes()).hexdigest(),'fixedOldToeReferenceSamples':pts,'admittedContacts':[],'diagnosticFloorY':76,'supportWorld':None,'geometryReviewed':False})
sheet.save(P/'enlarged-phase-foot-regions.png');(P/'phase-contact-diagnostics.json').write_text(json.dumps({'inspectionWindow':list(rect),'windowNotAnatomicalSegmentation':True,'floorOverlayOnly':True,'footCorrespondenceNotApproved':True,'rows':rows},indent=2)+'\n')
