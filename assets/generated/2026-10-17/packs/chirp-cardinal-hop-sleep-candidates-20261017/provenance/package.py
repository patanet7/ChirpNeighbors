from PIL import Image,ImageDraw
from scipy.ndimage import label,distance_transform_edt
import numpy as np,json,hashlib,pathlib,zipfile
r=pathlib.Path(__file__).resolve().parents[1]
cfg={'hopping':{'ids':[2,8,1,13,16,14],'anchors':[(300,375),(780,400),(1280,340),(280,790),(850,870),(1290,885)],'target':[350,400],'beaks':[(495,162),(1029,260),(1505,146),(544,656),(1012,679),(1497,673)],'root_y':[0,20,-25,-65,-15,10],'poses':['stand','crouch','push_off','airborne_tuck','landing_reach','settle'],'times':[350,140,100,130,120,220]},'sleep':{'ids':[1,4,6,19,18,17],'anchors':[(402,475),(910,475),(1410,475),(405,967),(911,967),(1414,967)],'target':[450,530],'beaks':[(528,137),(1058,201),(1310,218),(360,685),(1034,649),(1515,636)],'root_y':[0]*6,'poses':['awake','drowsy','tuck','sleep','wake_ruffle','alert'],'times':[450,500,650,1400,500,450]}}
m={'status':'review_candidate_not_production_approved','source_canvas':[640,576],'runtime_canvas':[320,288],'uniform_runtime_scale':0.5,'resampler':'nearest','per_frame_scaling':False,'atlas_size':[960,576],'coordinate_note':'Native anchors manually estimated; runtime points equal native points * 0.5. Hop source poses normalized at hip/root; root-motion curve supplied separately and applied only in motion previews. Sleep poses aligned at right ankle. Fixed canvases do not guarantee identical anatomical scale.','clips':{}}
for name,c in cfg.items():
 im=Image.open(r/'originals'/f'{name}-native.png').convert('RGBA');a=np.array(im);labs,n=label(a[:,:,3]>20);strong=np.isin(labs,c['ids']);_,inds=distance_transform_edt(~strong,return_indices=True);owners=labs[inds[0],inds[1]]
 fs=[];rt=[];motion=[];info=[]
 for i,(ident,anchor,beak,pose,t) in enumerate(zip(c['ids'],c['anchors'],c['beaks'],c['poses'],c['times'])):
  p=a.copy();p[owners!=ident]=0;dx,dy=c['target'][0]-anchor[0],c['target'][1]-anchor[1];fr=Image.new('RGBA',(640,576));fr.paste(Image.fromarray(p),(dx,dy));fn=f'{name}-{i:02}-{pose}.png';fr.save(r/'frames'/fn);fs.append(fr)
  sm=fr.resize((320,288),Image.Resampling.NEAREST);sm.save(r/'runtime'/fn);rt.append(sm)
  mo=Image.new('RGBA',(320,320));mo.paste(sm,(0,32+round(c['root_y'][i]*.5)));motion.append(mo)
  info.append({'source_file':'frames/'+fn,'runtime_file':'runtime/'+fn,'pose':pose,'duration_ms':t,'native_translation':[dx,dy],'anchor':c['target'],'beak_tip_native':[beak[0]+dx,beak[1]+dy],'root_motion_runtime':[0,c['root_y'][i]*.5],'alpha_bbox_native':fr.getchannel('A').getbbox()})
 for folder,frames,fn in [('',fs,name+'.apng'),('runtime',rt,name+'-pose.apng'),('preview',motion,name+'-motion.apng')]:
  frames[0].save(r/folder/fn,format='PNG',save_all=True,append_images=frames[1:],duration=c['times'],loop=0,disposal=0,blend=0)
 preview=[]
 for fr in motion:
  bg=Image.new('RGBA',fr.size,'#cad6bc');bg.alpha_composite(fr);preview.append(bg.convert('RGB'))
 preview[0].save(r/'preview'/f'{name}.gif',save_all=True,append_images=preview[1:],duration=c['times'],loop=0,disposal=2)
 atlas=Image.new('RGBA',(960,576));contact=Image.new('RGB',(960,636),'#cad6bc');d=ImageDraw.Draw(contact)
 for i,fr in enumerate(rt):
  x,y=(i%3)*320,(i//3)*288;atlas.paste(fr,(x,y));bg=Image.new('RGBA',fr.size,'#cad6bc');bg.alpha_composite(fr);cy=(i//3)*318;contact.paste(bg.convert('RGB'),(x,cy));d.text((x+8,cy+291),f'{i} {c["poses"][i]} {c["times"][i]}ms',fill='black')
 atlas.save(r/'runtime'/f'{name}-atlas.png');contact.save(r/'preview'/f'{name}-contact.jpg',quality=95)
 m['clips'][name]={'duration_ms':sum(c['times']),'frames':info,'unique_frames':len({hashlib.sha256(x.tobytes()).hexdigest() for x in fs})}
 for file in [r/f'{name}.apng',r/'runtime'/f'{name}-pose.apng',r/'preview'/f'{name}-motion.apng',r/'preview'/f'{name}.gif']:
  test=Image.open(file);assert test.n_frames==6
(r/'manifest.json').write_text(json.dumps(m,indent=2))
(r/'REVIEW.md').write_text('''# Cardinal hop and sleep candidates\n\nTwo native image-generated six-pose sheets. Visually inspected alpha composites and extracted contact sheets. Hop has real crouch, tail counterbalance, extended launch legs, curled airborne feet and forward landing legs. Sleep has eyelid closure, beak/neck tuck into shoulder/back feathers, rounded body, waking ruffle and alert recovery.\n\nNOT production approved. Anatomical scale/silhouette drifts between generated poses despite fixed canvas and no per-frame scaling. Hip anchors are manually estimated for hop; sleep uses estimated ankle contact. Landing and settle need foot-contact refinement. Hop is an in-place loop with a separate vertical root-motion curve; no net horizontal travel is implied. The native pose APNG does not apply this curve; preview motion APNG/GIF does. This is articulated generated artwork, not deformation of a static bird. Sleep tuck and eye state are clearly distinguishable, but ruffle is exaggerated and feather layout changes.\n\nOriginal native sheets, exact prompts, canonical source and full-resolution extracted frames retained. Runtime derives every frame using exactly 0.5 nearest-neighbor scale, not bounding-box fitting. Native frame canvas 640x576; runtime frames 320x288; runtime atlases 960x576. Preview motion canvas 320x320 adds room for hop. Alpha retained for PNG/APNG, GIF composited pale green.\n''')
(r/'SHA256SUMS.txt').write_text('\n'.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+str(p.relative_to(r)) for p in sorted(r.rglob('*')) if p.is_file() and p.name!='SHA256SUMS.txt')+'\n')
z=r.parent/'chirp-cardinal-hop-sleep-candidates-20261017.zip'
with zipfile.ZipFile(z,'w',zipfile.ZIP_DEFLATED) as f:
 for p in sorted(r.rglob('*')):
  if p.is_file():f.write(p,p.relative_to(r))
print(z,z.stat().st_size,hashlib.sha256(z.read_bytes()).hexdigest())
