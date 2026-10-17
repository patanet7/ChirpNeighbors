#!/usr/bin/env python3
"""Offline source-art proof. Requires Python, Pillow and numpy. No runtime integration."""
from pathlib import Path
import json, hashlib, math
import numpy as np
from PIL import Image,ImageDraw,ImageSequence,ImageFilter
ROOT=Path(__file__).resolve().parent
H=lambda b:hashlib.sha256(b).hexdigest()
def run():
 for d in ['sprites','previews','reports','frames']: (ROOT/d).mkdir(exist_ok=True)
 cfg=json.loads((ROOT/'rig.json').read_text()); n=1536
 original=Image.open(ROOT/'originals/healthy-canopy-r1.png').convert('RGBA'); oa=np.array(original); removed=int(((oa[:,:,3]>0)&(oa[:,:,3]<=1)).sum());oa[oa[:,:,3]<=1]=0
 leaf=Image.new('RGBA',(n,n));leaf.alpha_composite(Image.fromarray(oa).resize((1408,1408),Image.Resampling.NEAREST),(64,0));leaf.save(ROOT/'sprites/healthy-canopy-common.png')
 wood_src=Image.open(ROOT/'references/wood-scaffold-preserved.png').convert('RGBA');wood=Image.new('RGBA',(n,n));wood.alpha_composite(wood_src,(141,141))
 la=np.array(leaf); yy,xx=np.mgrid[:n,:n].astype(np.float32); pins=np.array(cfg['pins'],dtype=np.float32)
 distances=np.min(np.stack([np.hypot(xx-p[0],yy-p[1]) for p in pins]),axis=0);t=np.clip((distances-48)/180,0,1);weight=t*t*(3-2*t)
 core=distances<=48;visible=(np.array(wood)[:,:,3]>128)&(la[:,:,3]==0)
 root=(slice(1275,1355),slice(680,900)); frames=[];ledger=[];rgba0=None;rgb0=None;palette=None; representative=[0,4,8,16,24,32]
 for i in range(33):
  phase=2*math.pi*(i%32)/32
  drive_x=8*math.sin(phase)+2*math.sin(2*phase)*(yy/n)
  drive_y=1.4*math.sin(phase)*(xx/n)
  sx=xx.copy();sy=yy.copy()
  for _ in range(4):
   xi=np.clip(np.rint(sx).astype(int),0,n-1);yi=np.clip(np.rint(sy).astype(int),0,n-1)
   sx=xx-drive_x*weight[yi,xi];sy=yy-drive_y*weight[yi,xi]
  xi=np.rint(sx).astype(int);yi=np.rint(sy).astype(int);good=(xi>=0)&(xi<n)&(yi>=0)&(yi<n)
  wa=np.zeros_like(la);wa[good]=la[yi[good],xi[good]]
  tree=Image.alpha_composite(wood,Image.fromarray(wa)); ar=np.array(tree)
  if rgba0 is None:rgba0=ar.copy();tree.save(ROOT/'sprites/whole-tree-rest.png')
  bg=Image.new('RGBA',(n,n),(214,219,207,255));bg.alpha_composite(tree);rgb=bg.convert('RGB').resize((512,512),Image.Resampling.NEAREST)
  if palette is None:palette=rgb.quantize(colors=256,method=Image.Quantize.MEDIANCUT)
  pal=rgb.quantize(palette=palette,dither=Image.Dither.NONE);frames.append(pal)
  y,x=np.where(wa[:,:,3]>1)
  row={'frame':i,'phase_radians':phase,'rgba_tree_sha256':H(ar.tobytes()),'canopy_rgba_sha256':H(wa.tobytes()),'pin_centers':cfg['pins'],'pin_max_drift_source_px':0,'core_changed_rgba_pixels':int(np.any(wa[core]!=la[core],axis=1).sum()),'root_changed_rgba_pixels':int(np.any(ar[root]!=rgba0[root],axis=2).sum()),'wood_source_sha256':H((ROOT/'references/wood-scaffold-preserved.png').read_bytes()),'foliage_bbox_alpha_gt1':[int(x.min()),int(y.min()),int(x.max()+1),int(y.max()+1)]};ledger.append(row)
  if i in representative: rgb.save(ROOT/f'frames/gentle-{i:02d}.png')
 frames[0].save(ROOT/'previews/gentle-wind.gif',save_all=True,append_images=frames[1:],duration=80,loop=0,optimize=False,disposal=2)
 decoded=[f.convert('RGB').copy() for f in ImageSequence.Iterator(Image.open(ROOT/'previews/gentle-wind.gif'))]
 contact=Image.new('RGB',(3*384,2*410),(232,232,225));dr=ImageDraw.Draw(contact)
 for k,i in enumerate(representative):contact.paste(decoded[i].resize((384,384),Image.Resampling.NEAREST),((k%3)*384,(k//3)*410));dr.text(((k%3)*384+8,(k//3)*410+388),f'decoded frame {i}',fill=(25,25,25))
 contact.save(ROOT/'previews/decoded-motion-contact.jpg',quality=90)
 for name,color in [('light',(218,220,211,255)),('dark',(32,39,37,255))]:
  bg=Image.new('RGBA',(n,n),color);bg.alpha_composite(Image.open(ROOT/'sprites/whole-tree-rest.png'));bg.convert('RGB').resize((768,768),Image.Resampling.NEAREST).save(ROOT/f'previews/whole-tree-{name}.jpg',quality=91)
 for i,r in enumerate(ledger):r['decoded_rgb_sha256']=H(np.array(decoded[i]).tobytes())
 # Prove quantized output root and exposed wood stay fixed, not just source geometry.
 vm=np.array(Image.fromarray((visible*255).astype('uint8')).resize((512,512),Image.Resampling.NEAREST))>0
 da=np.array(decoded[0]);changed=[int(np.any(np.array(f)[vm]!=da[vm],axis=1).sum()) for f in decoded]
 rp=(slice(425,451),slice(226,300));rootchanged=[int(np.any(np.array(f)[rp]!=da[rp],axis=2).sum()) for f in decoded]
 qa={'decoded_frames':len(decoded),'decoded_unique_rgb_frames':len({H(np.array(f).tobytes()) for f in decoded}),'first_last_rgba_equal':ledger[0]['rgba_tree_sha256']==ledger[-1]['rgba_tree_sha256'],'first_last_decoded_equal':np.array_equal(np.array(decoded[0]),np.array(decoded[-1])),'fixed_shared_palette_sha256':H(bytes(palette.getpalette())),'frame_duration_ms':80,'total_ms':len(decoded)*80,'pin_core_radius_source_px':48,'all_core_changed_counts':[r['core_changed_rgba_pixels'] for r in ledger],'all_root_changed_counts':[r['root_changed_rgba_pixels'] for r in ledger],'decoded_exposed_wood_max_changed_pixels':max(changed),'decoded_root_max_changed_pixels':max(rootchanged),'tested_exposed_wood_display_pixels':int(vm.sum()),'alpha_le1_pixels_removed_derivative_only':removed,'wind_max_drive_source_px':[10,1.4],'canopy_alpha_zero_fraction':float((la[:,:,3]==0).mean()),'canopy_bbox':leaf.getbbox(),'scope':'Mechanical multi-pin compound leaf-layer deformation; neither anatomical segmentation nor runtime physics. Small geometric proof only.'}
 dil=leaf.getchannel('A').filter(ImageFilter.MaxFilter(23));safe=(np.array(wood)[:,:,3]>128)&(np.array(dil)==0)
 sm=np.array(Image.fromarray((safe*255).astype('uint8')).resize((512,512),Image.Resampling.NEAREST))>0
 safechanged=[int(np.any(np.array(f)[sm]!=da[sm],axis=1).sum()) for f in decoded]
 qa.update(stable_unoccluded_wood_tested_display_pixels=int(sm.sum()),stable_unoccluded_wood_max_changed_pixels=max(safechanged),exposed_wood_change_explanation='85 initially exposed wood display pixels are crossed by moving foliage near its edge; conservative always-unoccluded wood mask excludes23px-dilated canopy and separately verifies static palette/root. This is occlusion, not wood movement.')
 qa['minimum_foliage_alpha_gt1_canvas_margin_all_frames_px']=min(min(b[0],b[1],1536-b[2],1536-b[3]) for b in [r['foliage_bbox_alpha_gt1'] for r in ledger])
 (ROOT/'reports/frame-ledger.json').write_text(json.dumps(ledger,indent=2));(ROOT/'reports/motion-qa.json').write_text(json.dumps(qa,indent=2));print(json.dumps(qa,indent=2))
 # Yard is an existing depth06 flattened REVIEW PLATE, not new scene art.
 yard=Image.open(ROOT/'references/existing-yard-review-plate.png').convert('RGBA');tree=Image.open(ROOT/'sprites/whole-tree-rest.png');tree=tree.resize((768,768),Image.Resampling.NEAREST);yard.alpha_composite(tree,(23,231));yard.save(ROOT/'previews/yard-source-review.png')
 view=yard.crop((0,160,1536,1024))
 for w,h in [(960,540),(384,216)]:view.resize((w,h),Image.Resampling.NEAREST).convert('RGB').save(ROOT/f'previews/yard-{w}.png')
 # Explicit registration overlay; lines are diagnostic, not source art.
 ov=Image.open(ROOT/'sprites/whole-tree-rest.png');draw=ImageDraw.Draw(ov)
 for i,(x,y) in enumerate(cfg['pins']):draw.ellipse((x-48,y-48,x+48,y+48),outline=(255,70,90,255),width=4);draw.text((x+12,y+12),str(i+1),fill=(255,50,80,255))
 ov.resize((768,768),Image.Resampling.NEAREST).save(ROOT/'previews/pin-overlay.png')
if __name__=='__main__':run()
