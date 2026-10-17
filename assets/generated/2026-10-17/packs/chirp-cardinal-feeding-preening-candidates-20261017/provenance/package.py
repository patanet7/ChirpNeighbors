from PIL import Image,ImageDraw
from scipy.ndimage import label,distance_transform_edt
import numpy as np,json,hashlib,pathlib,zipfile
root=pathlib.Path(__file__).resolve().parents[1]
configs={
'feeding':{'ids':[1,4,10,14,18,15],'feet':[(397,459),(852,459),(1350,459),(399,941),(872,941),(1382,941)],'beaks':[(521,161),(977,266),(1460,441),(525,641),(954,557),(1500,635)],'poses':['upright','look_down','lean_peck','seed_held_crack','swallow','upright_recovery'],'times':[420,180,180,340,240,420]},
'preening':{'ids':[1,2,3,11,9,10],'feet':[(404,461),(919,461),(1414,461),(413,967),(920,967),(1411,966)],'beaks':[(531,131),(834,189),(1350,201),(362,703),(1028,615),(1520,633)],'poses':['upright','turn_back','beak_wing_contact','groom_wing','ruffle','recover'],'times':[400,220,300,320,240,440]}}
manifest={'status':'review_candidate_not_production_approved','species':'northern cardinal male','method':'Native image_gen edits; scripts only split sprite sheets, translate planted-foot anchor, package, validate and preview. No resizing or body deformation.','canvas':[600,540],'root_anchor':[360,350],'foot_anchor':[420,490],'anchor_accuracy':'Manually estimated visible right ankle contact; residual toe drift remains. Root is nominal runtime pivot, not tracked anatomical landmark.','clips':{}}
previews=[]
for name,c in configs.items():
 im=Image.open(root/'originals'/f'{name}-native.png').convert('RGBA');a=np.array(im);labs,n=label(a[:,:,3]>20)
 # Partition sheet alpha among its six connected sprites. Preserve native pixels and their alpha.
 strong=np.isin(labs,c['ids']); _,inds=distance_transform_edt(~strong,return_indices=True);owners=labs[inds[0],inds[1]]
 frames=[]; infos=[]
 for i,(ident,foot,beak,pose,dur) in enumerate(zip(c['ids'],c['feet'],c['beaks'],c['poses'],c['times'])):
  pix=a.copy();pix[owners!=ident]=0
  dx,dy=420-foot[0],490-foot[1]
  frame=Image.new('RGBA',(600,540));frame.paste(Image.fromarray(pix),(dx,dy))
  out=root/'frames'/f'{name}-{i:02}-{pose}.png';frame.save(out);frames.append(frame)
  infos.append({'file':str(out.relative_to(root)),'duration_ms':dur,'foot_anchor':[420,490],'root_anchor':[360,350],'beak_tip':[beak[0]+dx,beak[1]+dy],'sheet_foot':foot,'translation':[dx,dy],'alpha_bbox':frame.getchannel('A').getbbox(),'sha256':hashlib.sha256(out.read_bytes()).hexdigest()})
 frames[0].save(root/f'{name}.apng',format='PNG',save_all=True,append_images=frames[1:],duration=c['times'],loop=0,disposal=0,blend=0)
 # GIF is an opaque preview because GIF cannot preserve smooth RGBA alpha.
 gf=[]
 for fr in frames:
  bg=Image.new('RGBA',fr.size,'#cad6bc');bg.alpha_composite(fr);gf.append(bg.convert('RGB'))
 gf[0].save(root/'preview'/f'{name}.gif',save_all=True,append_images=gf[1:],duration=c['times'],loop=0,disposal=2)
 atlas=Image.new('RGBA',(1800,1080))
 sheet=Image.new('RGB',(1800,1140),'#cad6bc');dr=ImageDraw.Draw(sheet)
 for i,fr in enumerate(frames):
  atlas.paste(fr,((i%3)*600,(i//3)*540));sheet.paste(gf[i],((i%3)*600,(i//3)*570));dr.text(((i%3)*600+15,(i//3)*570+540),f'{i}: {c["poses"][i]} ({c["times"][i]} ms)',fill='black')
 atlas.save(root/f'{name}-atlas.png');sheet.save(root/'preview'/f'{name}-contact-sheet.jpg',quality=92)
 manifest['clips'][name]={'frames':infos,'duration_ms':sum(c['times']),'unique_pixel_frames':len({hashlib.sha256(fr.tobytes()).hexdigest() for fr in frames})}
 for suffix in [f'{name}.apng']:
  check=Image.open(root/suffix);assert check.n_frames==6
(root/'timing-anchors.json').write_text(json.dumps(manifest,indent=2))
(root/'REVIEW.md').write_text('''# Cardinal animation review candidate\n\n12 genuine native-generated poses, six per clip. Feeding shows looking down, body/neck flexion to ground, seed held in open beak, swallowing and recovery. Preening shows turned head, beak-wing contact, grooming and substantial feather ruffle. Source feather detail and male cardinal identity remain recognizable.\n\nNOT production approved. Generated sheets ignored precise grid/foot positions. Packaging extracts each sprite and translates it to one manually estimated planted ankle anchor, with no per-frame scaling. Foot/toe geometry and body silhouette still drift. Feeding frame 3 has one ground seed near the beak; frame 4 shows seed held, but a distinct shell-splitting event is not resolved. Preening frame 4 has similar neck pose to frame 3 but a meaningfully lifted/separated wing. Frame 5 ruffle is exaggerated. The detailed rendered style is pixel-edged, with soft alpha at edges rather than a strict low-resolution limited-color pixel grid.\n\nOriginals and exact prompts are retained. APNG and individual PNGs retain native RGBA alpha. GIFs and contact sheets are previews composited over pale green. No artificial body warps, in-betweens, autoscaling or movement simulations were used. Six poses are discrete; no interpolated frames. Beak coordinates and root pivots are estimates intended for staging, not final collision/contact precision.\n''')
files=sorted(p for p in root.rglob('*') if p.is_file() and p.name!='SHA256SUMS.txt')
(root/'SHA256SUMS.txt').write_text('\n'.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+str(p.relative_to(root)) for p in files)+'\n')
zipout=root.parent/'chirp-cardinal-feeding-preening-candidates-20261017.zip'
with zipfile.ZipFile(zipout,'w',zipfile.ZIP_DEFLATED) as z:
 for p in sorted(root.rglob('*')):
  if p.is_file():z.write(p,p.relative_to(root))
print(zipout,zipout.stat().st_size,hashlib.sha256(zipout.read_bytes()).hexdigest())
