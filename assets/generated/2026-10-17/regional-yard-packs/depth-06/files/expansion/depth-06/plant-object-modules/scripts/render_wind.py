"""Portable offline source-part transform preview. Pillow+numpy only; no services/app/runtime worker.
No new plant art is painted. Existing actual RGBA parts rotate rigidly about recorded attachment pivots.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageSequence
import numpy as np,json,hashlib,math
P=Path(__file__).resolve().parents[1];R=json.load(open(P/'metadata/rig.json'));SZ=tuple(R['canvas_px']);N=48;D=8.0
sha=lambda b:hashlib.sha256(b).hexdigest()
base=Image.open(P/R['base_part']).convert('RGBA');assert sha((P/R['base_part']).read_bytes())==R['base_sha256']
basecan=Image.new('RGBA',SZ);basecan.alpha_composite(base,tuple(R['base_paste_xy_px']));basealpha=np.asarray(basecan)[:,:,3]
modules=[]
for m in R['modules']:
 src=Image.open(P/m['source_module']).convert('RGBA');assert sha((P/m['source_module']).read_bytes())==m['source_module_sha256'];canvas=Image.new('RGBA',SZ);canvas.alpha_composite(src,tuple(m['rest_paste_xy_px']));yy,xx=np.where(np.asarray(canvas)[:,:,3]>8);pivot=np.array(m['attachment_scene_px']);radius=float(np.sqrt((xx-pivot[0])**2+(yy-pivot[1])**2).max());modules.append((m,canvas,radius))
protected=tuple(R['protected_contact_rect_scene_px']);expected_base_region=None

def render(t,cap):
 global expected_base_region
 frame=Image.new('RGBA',SZ);checks=[]
 for i,(m,can,radius)in enumerate(modules):
  phase=0 if i==0 else .4;wave=(math.sin(2*math.pi*t/D+phase)+.2*math.sin(4*math.pi*t/D+phase))/1.2;angle=round(cap*wave,6);pivot=tuple(m['attachment_scene_px']);trans=can.rotate(angle,resample=Image.Resampling.NEAREST,expand=False,center=pivot,fillcolor=(0,0,0,0));ar=np.asarray(trans)[:,:,3];x,y=pivot;patch=ar[y-24:y+25,x-24:x+25];bpatch=basealpha[y-24:y+25,x-24:x+25];overlap=int(((patch>=128)&(bpatch>=128)).sum());assert overlap>0
  assert ar[y,x]>=128
  clipping=[int((ar[0]>8).sum()),int((ar[-1]>8).sum()),int((ar[:,0]>8).sum()),int((ar[:,-1]>8).sum())];assert not any(clipping)
  # Tip displacement bound at farthest alpha>8 source sample; geometry diagnostic, not physical wind speed.
  tip=2*radius*abs(math.sin(math.radians(angle)/2));assert tip<=m['heavy_tip_cap_px'] if cap>1 else tip<=m['mild_tip_cap_px']
  checks.append({'module':m['part_key'],'angle_deg':angle,'attachment_scene_px':list(pivot),'mapped_pivot_xy_px':list(pivot),'pivot_geometry_drift_px':0,'rendered_attachment_alpha':int(ar[y,x]),'local_overlap_alpha128_pixels':overlap,'max_rigid_rotation_tip_displacement_bound_px':round(tip,4),'clipped_edge_visible_pixels':clipping})
  frame.alpha_composite(trans)
 frame.alpha_composite(basecan)
 band=np.asarray(frame.crop(protected)).copy()
 if expected_base_region is None:expected_base_region=band
 assert np.array_equal(band,expected_base_region)
 return frame,checks

def review_rgb(im,col=(239,240,232,255)):
 bg=Image.new('RGBA',SZ,col);bg.alpha_composite(im);return bg.convert('RGB')
frames=[];ledger=[]
for k in range(N+1):
 t=k*D/N;small=[];sample={'index':k,'time_s':round(t,7),'base_root_scene_px':R['base_root_scene_px'],'base_source_sha256':R['base_sha256'],'base_paste_xy_px':R['base_paste_xy_px'],'base_unchanged':True,'regimes':{}}
 for label,cap in [('mild',.8),('heavy',2.2)]:
  im,checks=render(t,cap);sample['regimes'][label]={'modules':checks,'RGBA_sha256':sha(np.asarray(im).tobytes()),'protected_contact_RGBA_sha256':sha(np.asarray(im.crop(protected)).tobytes())};small.append(review_rgb(im).resize((256,205),Image.Resampling.NEAREST))
  if k in [0,8,16,24,32,40]:im2=review_rgb(im);im2.resize((480,384),Image.Resampling.NEAREST).save(P/'previews'/f'wind-{label}-sample{k:02}.png')
 board=Image.new('RGB',(512,237),(239,240,232));draw=ImageDraw.Draw(board);draw.text((8,8),'MILD - offline module rotations',fill=(25,30,30));draw.text((264,8),'HEAVY - artist cap2.2deg',fill=(25,30,30));board.paste(small[0],(0,30));board.paste(small[1],(256,30));frames.append(board);ledger.append(sample)
# One shared palette across every frame prevents static base/ground color pumping from adaptive per-frame palettes.
strip=Image.new('RGB',(512,237*6))
for i,k in enumerate([0,8,16,24,32,40]):strip.paste(frames[k],(0,237*i))
palette=strip.quantize(colors=256,method=Image.Quantize.MEDIANCUT);pf=[f.quantize(palette=palette,dither=Image.Dither.NONE)for f in frames]
out=P/'previews/cleveland-sage-mild-heavy.gif';pf[0].save(out,save_all=True,append_images=pf[1:],duration=160,loop=0,disposal=1,optimize=False)
gif=Image.open(out);decoded=[fr.convert('RGB').copy()for fr in ImageSequence.Iterator(gif)];durations=[];gif.seek(0)
for i in range(gif.n_frames):gif.seek(i);durations.append(gif.info.get('duration',0))
assert np.array_equal(np.asarray(decoded[0]),np.asarray(decoded[-1]))
# Source contact y650..735 maps to source downscaled pane rows203..226 after30px title.
protected_small=[(80,204,174,226),(336,204,430,226)]
for rect in protected_small:
 baseline=np.asarray(decoded[0].crop(rect))
 assert all(np.array_equal(np.asarray(f.crop(rect)),baseline)for f in decoded)
# Decode six actual GIF frames for inspectable contact, independent of higher quality source PNG rendering.
contact=Image.new('RGB',(1024,237*3+60),(239,240,232));draw=ImageDraw.Draw(contact)
indices=[round(i*(len(decoded)-1)/5)for i in range(6)]
for i,k in enumerate(indices):x=(i%2)*512;y=(i//2)*257;draw.text((x+8,y+3),f'DECODED GIF frame{k}',fill=(25,30,30));contact.paste(decoded[k],(x,y+20))
contact.save(P/'previews/decoded-six-frame-contact.png')
calm,_=render(0,0);review_rgb(calm).save(P/'previews/sage-assembly-calm-full.png');review_rgb(calm,(24,30,36,255)).save(P/'previews/sage-assembly-calm-dark.png')
# True alpha still assembly derivative is a composite, not a newly generated whole-plant original.
calm.save(P/'previews/sage-assembly-calm-alpha.png')
# Joint detail uses source crop/scaling only, no invented occlusion masks or repair painting.
joint=review_rgb(calm).crop((320,490,640,620)).resize((960,390),Image.Resampling.NEAREST);joint.save(P/'previews/sage-joint-detail.png')
(P/'metadata/frame-ledger.json').write_text(json.dumps({'rig':'metadata/rig.json','duration_model_seconds':D,'source_samples':N+1,'sample_duration_ms':160,'loop_closure_extra_frame':True,'frames':ledger},indent=2)+'\n')
validation={'source_transform_frames':N+1,'regimes':2,'base_input_geometry_and_root_fixed_all_samples':True,'protected_source_contact_rect':list(protected),'source_contact_pixels_identical_all98_regime_samples':True,'all_attachment_rendered_alpha128_present':True,'all_joints_have_local_base_module_alpha128_overlap':True,'minimum_joint_overlap_pixels':min(m['local_overlap_alpha128_pixels']for f in ledger for r in f['regimes'].values()for m in r['modules']),'max_pivot_geometry_drift_px':0,'clipping_visible_alpha_gt8_edge_pixels':0,'first_and_last_source_frame_equal':all(ledger[0]['regimes'][r]['RGBA_sha256']==ledger[-1]['regimes'][r]['RGBA_sha256']for r in ['mild','heavy']),'gif_path':'previews/cleveland-sage-mild-heavy.gif','gif_sha256':sha(out.read_bytes()),'gif_bytes':out.stat().st_size,'gif_dimensions_px':list(decoded[0].size),'gif_decoded_frames':len(decoded),'gif_unique_decoded_RGB_hashes':len({sha(np.asarray(f).tobytes())for f in decoded}),'gif_total_duration_ms':sum(durations),'gif_loop':gif.info.get('loop'),'gif_first_last_decoded_pixels_equal':True,'gif_static_contact_rects_px':[list(r)for r in protected_small],'gif_static_contact_pixels_identical_all_decoded_frames':True,'fixed_shared_palette':True,'decoded_frame_RGB_hashes':[sha(np.asarray(f).tobytes())for f in decoded],'duration_per_decoded_frame_ms':durations,'actual_drawn_animation_frames_authored':0,'physics_or_app_animation_runtime_implemented':False,'deergrass_base_botanical_hold':True,'visual_review':'pending actual decoded-contact/GIF/joint inspection','limitations':['A compound module contains baked stems/leaves/flowers; individual leaf articulation absent.','Nearest rotation may shimmer at tiny tips; sourcebase has slight native translucence, upper overlap can vary subtly even though protected lowercontact pixels fixed.','Local overlap/pivot checks do not certify botanical joints or perceptual style.']}
(P/'metadata/wind-validation.json').write_text(json.dumps(validation,indent=2)+'\n');print(json.dumps({k:v for k,v in validation.items()if k not in ['decoded_frame_RGB_hashes','duration_per_decoded_frame_ms']},indent=2))
