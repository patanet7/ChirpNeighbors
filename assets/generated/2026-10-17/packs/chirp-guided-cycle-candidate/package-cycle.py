from PIL import Image,ImageDraw
from pathlib import Path
import json,hashlib,zipfile
p=Path(__file__).parent;c=p/'cycle-candidate';c.mkdir(exist_ok=True)
sources=[p.parent/'originals/crow-contact-source.png',p/'near-support-passing-output.png',p/'opposite-contact-output.png',p/'far-support-passing-output.png']
labels=['near forward contact','near support / far swing','far forward contact','far support / near swing']
frames=[];stats={}
for i,src in enumerate(sources):
 im=Image.open(src).convert('RGBA');h=im.getchannel('A').histogram();stats[src.name]={'size':list(im.size),'alpha_zero':h[0],'alpha_max':max(k for k,n in enumerate(h) if n),'alpha_1_to_249':sum(h[1:250])}
 im=im.resize((384,256),Image.Resampling.NEAREST);f=Image.new('RGBA',(384,384));f.alpha_composite(im,(0,64));f.save(c/f'frame-{i}.png');frames.append(f)
atlas=Image.new('RGBA',(768,768))
for i,f in enumerate(frames):atlas.alpha_composite(f,((i%2)*384,(i//2)*384))
atlas.save(c/'crow-guided-four-pose-atlas.png')
frames[0].save(c/'crow-guided-four-pose.apng',save_all=True,append_images=frames[1:],duration=180,loop=0,disposal=0,blend=0)
preview=[]
for i,f in enumerate(frames):
 b=Image.new('RGBA',(384,384),(231,228,216,255));b.alpha_composite(f);d=ImageDraw.Draw(b);d.text((8,12),'CANDIDATE: '+labels[i],fill='black');d.line((0,302,384,302),fill=(150,140,125,255));preview.append(b)
preview[0].save(c/'crow-guided-four-pose.gif',save_all=True,append_images=preview[1:],duration=180,loop=0)
strip=Image.new('RGBA',(1536,384),(231,228,216,255))
for i,f in enumerate(preview):strip.alpha_composite(f,(i*384,0))
strip.save(c/'four-pose-review.png')
translated=[]
for i in range(8):
 b=Image.new('RGBA',(800,384),(231,228,216,255));d=ImageDraw.Draw(b)
 for x in range(0,800,50):d.line((x,302,x,324),fill=(170,160,145,255));d.text((x+2,330),str(x),fill=(90,80,70,255))
 d.line((0,302,800,302),fill=(100,90,70,255));b.alpha_composite(frames[i%4],(20+50*i,0));d.text((8,12),'QA ONLY: fixed advance 50 px/frame; watch planted feet slide',fill='black');translated.append(b)
translated[0].save(c/'fixed-speed-contact-test.gif',save_all=True,append_images=translated[1:],duration=360,loop=0)
review={'status':'candidate_rework_not_approved_walk','new_calls_extension':2,'guided_calls_total':3,'known_project_calls_total':14,'fallback':'v2 unchanged','ordered_phases':labels,'timing_ms':[180]*4,'runtime_frame_size':[384,384],'scale':'All source art normalized by fixed canvas ratio to 384x256 and placed at y=64. No per-frame fit, body warping, morphing or synthesized in-betweens.','gates':{'opposite_contact_geometry':'PASS: foreground near shin crosses backward over forward far shin.','near_support_far_swing':'PASS: near foot planted, far foot visibly above it. Guide exact angles not copied.','far_support_near_swing':'PASS: far foot planted, near foot lifted forward. Guide exact angles not copied.','leg_occlusion':'PASS at coarse visible near/far-role level. Toe topology still needs detailed production cleanup.','identity':'CONDITIONAL: recognizable crow, neutral palette and head/bill retained; feather patterns and lower chest/leg attachment vary.','body_root_scale':'CONDITIONAL: same overall framing and scale after fixed normalization; lower-body silhouette shifts. No production pelvis registration claimed.','world_foot_contact':'FAIL at fixed speed: representative manually estimated toe tracks drift about 20 to 26 runtime pixels over stance.','ground_height':'FAIL tight one-pixel target: representative toe y varies up to about 5 runtime pixels.','alpha':'CONDITIONAL: true transparent background; max alpha 254; anti-aliased edges remain.','loop_continuity':'FAIL production gate: only four sparse phases, unequal stride spacing and abrupt changes. Genuine alternating roles, not a smooth approved walk.','native_pixel_finish':'FAIL final gate: high-resolution feather detail resampled to runtime; temporal texture cleanup unperformed.'},'contact_estimates':{'method':'Manual corresponding forward-toe estimates from source images at normalized 768x512 coordinates; approximate +/-5 pixels. Not automatic tracking or subpixel measurements.','fixed_root_advance_at_768_scale':[0,100,200,300,400],'near_stance_frame_indices':[0,1,2],'near_local_toe_xy':[[695,466],[610,470],[470,467]],'near_world_x':[695,710,670],'near_world_x_range_runtime_pixels':20,'far_stance_frame_indices':[2,3,4],'far_local_toe_xy':[[600,463],[485,470],[436,473]],'far_world_x':[800,785,836],'far_world_x_range_runtime_pixels':25.5},'alpha_stats':stats,'next':'Keep this as a useful guide-compliance and phase-coverage proof. To approach production, author target contact trajectories/stance timing and use tightly controlled keyframe cleanup; no blind sheet regeneration. More in-betweens alone will not repair foot sliding.'}
(c/'cycle-review.json').write_text(json.dumps(review,indent=2))
files=[f for f in p.rglob('*') if f.is_file() and f.name!='cycle-hashes.json']
(c/'cycle-hashes.json').write_text(json.dumps({str(f.relative_to(p)):hashlib.sha256(f.read_bytes()).hexdigest() for f in files},indent=2))
with zipfile.ZipFile('/workspace/shared/chirp-guided-cycle-candidate.zip','w',zipfile.ZIP_DEFLATED) as z:
 for f in p.rglob('*'):
  if f.is_file():z.write(f,f.relative_to(p))
 z.write(sources[0],'input-crow-contact-source.png')
print('Packaged candidate; full production gate fails.')
