"""Portable Pillow+NumPy offline source-art motion demonstration.
Run beside reports/module-transforms.json and source sprites. No runtime/app use.
Original color/alpha pixels are only sampled; no art is painted or inpainted.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageSequence
import numpy as np, math,json,hashlib
P=Path(__file__).resolve().parent
for directory in ['previews','frames','reports']:(P/directory).mkdir(exist_ok=True)
CONFIG=json.loads((P/'reports/module-transforms.json').read_text())
SIZE=tuple(CONFIG['assembly_canvas_px']);WOOD_OFFSET=tuple(CONFIG['wood_translation_px']);DISPLAY=(512,512)
N=32;DURATION=80;KEYS=[0,5,10,16,23,31]
BG=(229,226,212,255)
def digest(im):return hashlib.sha256(im.tobytes()).hexdigest()
def flatten(im,bg=BG):
 b=Image.new('RGBA',im.size,bg);b.alpha_composite(im);return b.convert('RGB')
def smooth(t):return t*t*(3-2*t)
wood=Image.open(P/'sprites/wood-scaffold-v1.png').convert('RGBA')
wood_bytes_digest=digest(wood)
wood_layer=Image.new('RGBA',SIZE,(0,0,0,0));wood_layer.alpha_composite(wood,WOOD_OFFSET)
prepared=[]
for m in CONFIG['modules']:
 source=Image.open(P/m['path']).convert('RGBA');src=np.asarray(source);ay,ax=m['crop_anchor_xy'][1],m['crop_anchor_xy'][0]
 ys,xs=np.nonzero(src[:,:,3]>0);radius=max(np.hypot(xs-ax,ys-ay))*m['uniform_scale'];half=math.ceil(radius+24)
 patchsize=(half*2+1,half*2+1);theta=math.radians(m['rest_rotation_deg']);s=m['uniform_scale'];c=math.cos(theta)/s;sn=math.sin(theta)/s
 affine=[c,sn,ax+.5-(c+sn)*(half+.5),-sn,c,ay+.5-(-sn+c)*(half+.5)]
 rest=source.transform(patchsize,Image.Transform.AFFINE,affine,Image.Resampling.NEAREST,fillcolor=(0,0,0,0))
 ra=np.asarray(rest);yy,xx=np.indices(ra.shape[:2],dtype=np.float32);dx=xx-half;dy=yy-half;r=np.hypot(dx,dy)
 # Artist radial envelope, not anatomical leaf/branch segmentation or physics.
 w=np.where(r<=48,0,np.where(r<100,.35*smooth(np.clip((r-48)/52,0,1)),.35+.65*smooth(np.clip((r-100)/160,0,1)))).astype(np.float32)
 prepared.append({'m':m,'rest':rest,'array':ra,'half':half,'dx':dx,'dy':dy,'weight':w,'core_mask':r<=48,'affine':affine,'offset':[m['target_canvas_xy'][0]-half,m['target_canvas_xy'][1]-half]})
def warp(p,angle_deg):
 if abs(angle_deg)<1e-12:return p['rest'].copy()
 phi=np.deg2rad(angle_deg)*p['weight'];c=np.cos(phi);s=np.sin(phi)
 x=np.floor(p['half']+c*p['dx']+s*p['dy']+.5).astype(np.int32)
 y=np.floor(p['half']-s*p['dx']+c*p['dy']+.5).astype(np.int32)
 h,w=p['array'].shape[:2];valid=(x>=0)&(x<w)&(y>=0)&(y<h)
 out=np.zeros_like(p['array']);out[valid]=p['array'][y[valid],x[valid]]
 return Image.fromarray(out,'RGBA')
def assemble(modules):
 result=Image.new('RGBA',SIZE,(0,0,0,0))
 for p,im in zip(prepared,modules):result.alpha_composite(im,p['offset'])
 result.alpha_composite(wood_layer) # fixed visible wood hides generated cut faces
 return result
rest=assemble([p['rest'] for p in prepared]);rest.save(P/'previews/assembled-rest-rgba.png')
for theme,bg in [('light',BG),('dark',(34,42,43,255))]:flatten(rest,bg).resize(DISPLAY,Image.Resampling.NEAREST).save(P/f'previews/assembled-rest-{theme}.png')
# Actual local wood/module/rest composition triptychs, same source-space crop.
for p in prepared:
 x,y=p['m']['target_canvas_xy'];box=(x-72,y-72,x+72,y+72)
 modulelayer=Image.new('RGBA',SIZE,(0,0,0,0));modulelayer.alpha_composite(p['rest'],p['offset'])
 contact=Image.new('RGB',(864,320),BG[:3]);d=ImageDraw.Draw(contact)
 for i,(name,img) in enumerate([('Fixed wood',wood_layer),('Leaf module',modulelayer),('Assembly (wood above)',rest)]):
  contact.paste(flatten(img.crop(box)).resize((288,288),Image.Resampling.NEAREST),(i*288,32));d.text((i*288+8,8),name,fill=(30,30,30));d.ellipse((i*288+138,170,i*288+150,182),outline=(220,20,150),width=1)
 contact.save(P/f'previews/{p["m"]["slot"]}-joint-triptych.jpg',quality=95)

# One shared palette for both complete GIF sequences, trained on unchanged rest
# colors. Transform sampling introduces no new source color; fixed wood retains
# exactly the same palette entries in every frame.
palette=flatten(rest).resize(DISPLAY,Image.Resampling.NEAREST).quantize(colors=256,method=Image.Quantize.MEDIANCUT,dither=Image.Dither.NONE)
palette_bytes=bytes(palette.getpalette());palette_hash=hashlib.sha256(palette_bytes).hexdigest()
all_reports=[]
for mode,amplitude in [('mild',2.0),('heavy',6.0)]:
 frames=[];ledger=[];module_alpha_union=np.zeros(SIZE[::-1],dtype=bool);first_assembled=None
 for frame in range(N+1):
  t=(frame%N)/N;leaf_images=[];pieces=[]
  for i,p in enumerate(prepared):
   # All drives close exactly at t=0; smaller second harmonic differentiates pieces.
   angle=amplitude*(1-.08*i)*(math.sin(2*math.pi*t)+(.15 if i%2==0 else -.12)*math.sin(4*math.pi*t))
   image=warp(p,angle);arr=np.asarray(image);h=p['half'];anchor=list(p['m']['target_canvas_xy']);offset=p['offset'];bb=image.getchannel('A').getbbox()
   core_equal=bool(np.array_equal(arr[p['core_mask']],p['array'][p['core_mask']]))
   assert core_equal
   assert tuple(arr[h,h])==tuple(p['array'][h,h])
   clipped=bb is not None and (offset[0]+bb[0]<0 or offset[1]+bb[1]<0 or offset[0]+bb[2]>SIZE[0] or offset[1]+bb[3]>SIZE[1])
   assert not clipped,(mode,frame,p['m']['slot'])
   # The patch is a radius-preserving twist, so source may not reach its border.
   edge_nonzero=int(np.count_nonzero(arr[[0,-1],:,3]))+int(np.count_nonzero(arr[:,[0,-1],3]));assert edge_nonzero==0
   leaf_images.append(image)
   layer=Image.new('RGBA',SIZE,(0,0,0,0));layer.alpha_composite(image,offset);module_alpha_union|=np.asarray(layer)[:,:,3]>0
   pieces.append({'slot':p['m']['slot'],'drive_angle_deg':angle,'attachment_canvas_xy':anchor,'attachment_drift_px':0,'base_sample_rgba':arr[h,h].tolist(),'fixed_core_radius_px':48,'fixed_core_pixel_equal':core_equal,'rgba_hash':digest(image),'clipped':clipped,'patch_edge_alpha_nonzero':edge_nonzero})
  composed=assemble(leaf_images)
  if frame==0:first_assembled=composed.copy()
  if frame==N:assert composed.tobytes()==first_assembled.tobytes()
  display=flatten(composed).resize(DISPLAY,Image.Resampling.NEAREST)
  indexed=display.quantize(palette=palette,dither=Image.Dither.NONE)
  assert bytes(indexed.getpalette())==palette_bytes
  frames.append(indexed)
  ledger.append({'frame':frame,'time_seconds':frame*DURATION/1000,'wood_source_rgba_hash':wood_bytes_digest,'root_canvas_xy':[1053,1578],'root_drift_px':0,'modules':pieces,'source_composite_rgba_hash':digest(composed),'display_rgb_hash_before_gif':digest(indexed.convert('RGB'))})
  if frame in KEYS:display.save(P/f'frames/{mode}-frame-{frame:02d}.png')
 frames[0].save(P/f'previews/{mode}-anchored-wind.gif',save_all=True,append_images=frames[1:],duration=DURATION,loop=0,optimize=False,disposal=1)
 with Image.open(P/f'previews/{mode}-anchored-wind.gif') as gif:
  decoded=[f.convert('RGB').copy() for f in ImageSequence.Iterator(gif)]
 with Image.open(P/f'previews/{mode}-anchored-wind.gif') as gif:
  encoded_duration_ms=sum(f.info.get('duration',0) for f in ImageSequence.Iterator(gif))
 assert len(decoded)==N+1,(mode,len(decoded))
 assert decoded[0].tobytes()==decoded[-1].tobytes()
 assert all(digest(d)==r['display_rgb_hash_before_gif'] for d,r in zip(decoded,ledger))
 # Visible rigid wood outside the union of ANY moving module may not flicker.
 fixed_visible=(np.asarray(wood_layer)[:,:,3]>128)&(~module_alpha_union)
 fixedmask=Image.fromarray((fixed_visible*255).astype(np.uint8)).resize(DISPLAY,Image.Resampling.NEAREST)
 mask=np.asarray(fixedmask)>0;first=np.asarray(decoded[0]);stable=all(np.array_equal(np.asarray(d)[mask],first[mask]) for d in decoded)
 assert stable
 rootbox=(244,374,284,402);root_hashes=[digest(d.crop(rootbox)) for d in decoded];assert len(set(root_hashes))==1
 # Contact is derived from ACTUALLY DECODED GIF keyframes, not the inputs.
 contact=Image.new('RGB',(1536,1080),BG[:3]);dr=ImageDraw.Draw(contact)
 for j,f in enumerate(KEYS):
  x=(j%3)*512;y=(j//3)*540;dr.text((x+10,y+10),f'{mode.upper()} decoded GIF frame {f}',fill=(30,30,30));contact.paste(decoded[f],(x,y+28))
 contact.save(P/f'previews/{mode}-decoded-keyframe-contact.jpg',quality=94)
 report={'mode':mode,'amplitude_drive_deg':amplitude,'frame_count':len(decoded),'unique_decoded_rgb_hashes':len(set(digest(d) for d in decoded)),'gif_dimensions_px':list(DISPLAY),'frame_duration_ms':DURATION,'nominal_drive_period_ms':N*DURATION,'encoded_gif_duration_ms':encoded_duration_ms,'appended_closure_frame':True,'closure_duplicate_hold_ms':DURATION,'first_last_decoded_rgb_equal':True,'first_last_source_rgba_equal':True,'shared_palette_sha256':palette_hash,'decoded_frames_equal_encoded_rgb':True,'fixed_visible_wood_pixels_tested':int(mask.sum()),'fixed_visible_wood_pixels_stable':stable,'root_roi_decoded_rgb_hashes_unique':len(set(root_hashes)),'root_roi_px':rootbox,'root_roi_hash':root_hashes[0],'frame_ledger':ledger,'semantic_branch_leaf_masks':False,'per_pixel_motion_weights':'radial artist envelope:0 inside48px, smooth0..0.35 at48..100px, smooth0.35..1 at100..260px; all wood/root0','runtime_physics_or_wind_implemented':False,'offline_preview_implementation':True}
 (P/f'reports/{mode}-frame-ledger.json').write_text(json.dumps(report,indent=2)+'\n');all_reports.append({k:v for k,v in report.items() if k!='frame_ledger'})
(P/'reports/motion-validation.json').write_text(json.dumps({'status':'all numerical offline checks pass; visual/anatomical join review separate','wood_source_rgba_hash':wood_bytes_digest,'wood_source_file_sha256':hashlib.sha256((P/'sprites/wood-scaffold-v1.png').read_bytes()).hexdigest(),'assembly_canvas_px':list(SIZE),'display_px':list(DISPLAY),'modes':all_reports},indent=2)+'\n')
print(json.dumps(all_reports,indent=2))
