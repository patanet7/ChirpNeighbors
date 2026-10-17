"""Portable offline review: native-alpha generated crown + byte-identical reused fan sprites.
Pillow/numpy only. No network/services, new painted art, weather simulation or application access.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageSequence
import numpy as np,json,hashlib,math
P=Path(__file__).resolve().parents[1];R=json.load(open(P/'metadata/rig.json'));SZ=tuple(R['canvas_px']);N=48
H=lambda b:hashlib.sha256(b).hexdigest()
basep=P/R['base']['file'];assert H(basep.read_bytes())==R['base']['sha256'];base=Image.open(basep).convert('RGBA').resize(R['base']['resize_dimensions_px'],Image.Resampling.NEAREST);basecan=Image.new('RGBA',SZ);basecan.alpha_composite(base,tuple(R['base']['paste_xy_px']));basealpha=np.asarray(basecan)[:,:,3];fans=[]
for f in R['fans']:
 p=P/f['file'];assert H(p.read_bytes())==f['sha256'];im=Image.open(p).convert('RGBA');can=Image.new('RGBA',SZ);can.alpha_composite(im,tuple(f['rest_paste_xy_px']));yy,xx=np.where(np.array(can)[:,:,3]>8);pi=np.array(f['attachment_scene_px']);radius=float(np.sqrt((xx-pi[0])**2+(yy-pi[1])**2).max());fans.append((f,can,radius))
rect=tuple(R['core_root_qa_rect_scene_px']);reference_band=None

def frame(k,cap):
 global reference_band
 t=k*8/N;out=Image.new('RGBA',SZ);checks=[]
 for i,(f,can,radius)in enumerate(fans):
  ph=0 if i==0 else .3;v=(math.sin(2*math.pi*t/8+ph)+.15*math.sin(4*math.pi*t/8+ph))/1.15;angle=round(cap*v,6);pivot=tuple(f['attachment_scene_px']);rot=can.rotate(angle,resample=Image.Resampling.NEAREST,expand=False,center=pivot,fillcolor=(0,0,0,0));a=np.array(rot)[:,:,3];x,y=pivot;overlap=int(((a[y-25:y+26,x-25:x+26]>=128)&(basealpha[y-25:y+26,x-25:x+26]>=128)).sum());assert overlap>0 and a[y,x]>=128
  edges=[int((a[0]>8).sum()),int((a[-1]>8).sum()),int((a[:,0]>8).sum()),int((a[:,-1]>8).sum())];assert not any(edges);tip=2*radius*abs(math.sin(math.radians(angle)/2));assert tip<=R['gentle_tip_displacement_cap_px']
  checks.append({'fan':f['id'],'angle_deg':angle,'attachment_scene_px':list(pivot),'mapped_pivot_scene_px':list(pivot),'pivot_geometry_drift_px':0,'attachment_alpha':int(a[y,x]),'local_base_fan_overlap_alpha128_pixels':overlap,'tip_displacement_upper_bound_px':round(tip,5),'clipping_edges_alpha_gt8':edges});out.alpha_composite(rot)
 out.alpha_composite(basecan);band=np.array(out.crop(rect))
 if reference_band is None:reference_band=band.copy()
 assert np.array_equal(band,reference_band)
 return out,checks

def onbg(im,dark=False):
 bg=Image.new('RGBA',SZ,(24,30,36,255)if dark else(239,240,232,255));bg.alpha_composite(im);return bg.convert('RGB')
calm,_=frame(0,0);calm.save(P/'previews/healthy-assembly-alpha.png');onbg(calm).save(P/'previews/healthy-assembly-light.png');onbg(calm,True).save(P/'previews/healthy-assembly-dark.png');onbg(calm).crop((320,550,640,720)).resize((960,510),Image.Resampling.NEAREST).save(P/'previews/root-joint-detail.png')
frames=[];ledger=[]
for k in range(N+1):
 im,checks=frame(k,R['gentle_rotation_cap_deg']);rgb=onbg(im).resize((512,410),Image.Resampling.NEAREST);board=Image.new('RGB',(512,440),(239,240,232));ImageDraw.Draw(board).text((8,8),'DEERGRASS - gentle offline fan rotations, fixed crown',fill=(25,30,30));board.paste(rgb,(0,30));frames.append(board);ledger.append({'index':k,'source_phase_time_s':round(k*8/N,7),'base_root_scene_px':R['base']['root_scene_px'],'base_source_sha256':R['base']['sha256'],'base_paste_xy_px':R['base']['paste_xy_px'],'base_geometry_fixed':True,'fans':checks,'frame_RGBA_sha256':H(np.array(im).tobytes()),'core_root_RGBA_sha256':H(np.array(im.crop(rect)).tobytes())})
 if k in [0,8,16,24,32,40]:board.save(P/'previews'/f'gentle-sample{k:02}.png')
strip=Image.new('RGB',(512,440*6))
for i,k in enumerate([0,8,16,24,32,40]):strip.paste(frames[k],(0,i*440))
pal=strip.quantize(colors=256,method=Image.Quantize.MEDIANCUT);pp=[im.quantize(palette=pal,dither=Image.Dither.NONE)for im in frames];gifp=P/'previews/deergrass-gentle-offline.gif';pp[0].save(gifp,save_all=True,append_images=pp[1:],duration=160,loop=0,disposal=1,optimize=False)
gif=Image.open(gifp);decoded=[im.convert('RGB').copy()for im in ImageSequence.Iterator(gif)];duration=[]
for k in range(gif.n_frames):gif.seek(k);duration.append(gif.info.get('duration',0))
assert np.array_equal(np.array(decoded[0]),np.array(decoded[-1]));smallrect=(199,390,314,412);ref=np.array(decoded[0].crop(smallrect));assert all(np.array_equal(np.array(im.crop(smallrect)),ref)for im in decoded)
board=Image.new('RGB',(1024,1380),(239,240,232));draw=ImageDraw.Draw(board)
for i,k in enumerate([round(n*(len(decoded)-1)/5)for n in range(6)]):x=(i%2)*512;y=(i//2)*460;draw.text((x+8,y+3),f'DECODED GIF frame{k}',fill=(25,30,30));board.paste(decoded[k],(x,y+20))
board.save(P/'previews/decoded-six-frame-contact.png')
# Review overlay on byte-identical existing depth06 coastal scene, preserving the scene identity.
yard=P/R['yard_review']['source']
if yard.exists():
 yard=P/R['yard_review']['source'];assert H(yard.read_bytes())==R['yard_review']['source_sha256'];bg=Image.open(yard).convert('RGBA');comp=bg.copy();comp.alpha_composite(calm.resize(R['yard_review']['plant_assembly_resize_px'],Image.Resampling.NEAREST),tuple(R['yard_review']['plant_paste_xy_px']));comp.save(P/'previews/coastal-yard-review-full.png')
 for size in [(960,540),(384,216)]:comp.crop(tuple(R['yard_review']['crop_xyxy'])).resize(size,Image.Resampling.NEAREST).save(P/'previews'/f'coastal-yard-review-{size[0]}.png')
(P/'metadata/frame-ledger.json').write_text(json.dumps({'source_cycle_seconds':8,'sample_hold_ms':160,'frames':ledger},indent=2)+'\n')
qa={'source_frame_samples':N+1,'base_root_fixed_all_samples':True,'base_input_RGBA_geometry_fixed':True,'protected_core_root_rect_scene_px':list(rect),'core_root_RGBA_identical_all49sourceframes':True,'minimum_joint_overlap_alpha128_pixels':min(c['local_base_fan_overlap_alpha128_pixels']for f in ledger for c in f['fans']),'actual_attachment_alpha128_present_all_frames':True,'max_pivot_geometry_drift_px':0,'visible_alpha_gt8_edge_clipping_pixels':0,'GIF':{'path':'previews/deergrass-gentle-offline.gif','sha256':H(gifp.read_bytes()),'bytes':gifp.stat().st_size,'dimensions_px':list(decoded[0].size),'decoded_frames':len(decoded),'unique_decoded_RGB_hashes':len({H(np.array(f).tobytes())for f in decoded}),'decoded_frame_hashes':[H(np.array(f).tobytes())for f in decoded],'durations_ms':duration,'total_duration_ms':sum(duration),'fixed_shared_palette':True,'first_last_decoded_RGB_equal':True,'protected_core_root_rect_px':list(smallrect),'core_root_RGB_identical_all_decoded_frames':True,'loop_forever':True},'first_last_source_RGBA_equal':ledger[0]['frame_RGBA_sha256']==ledger[-1]['frame_RGBA_sha256'],'reused_fan_bytes_not_new_art':True,'new_generated_crowns':1,'physics_or_app_runtime_implementation':False,'visual_review':'pending actual light/dark/joint/GIF contact/yard960+384 inspection','limits':['Rigid fan transforms, not per-blade deformation or physics.','Fine native leaves may shimmer under nearest rotation at small scale.','Base has native alpha; upper collar occlusion can vary subtly; protected core/root pixels proved invariant.','Yard overlay is review only, not new scene asset or app integration.']}
(P/'metadata/wind-qa.json').write_text(json.dumps(qa,indent=2)+'\n');print(json.dumps({k:v for k,v in qa.items()if k!='GIF'},indent=2));print('GIF',len(decoded),sum(duration),gifp.stat().st_size)
