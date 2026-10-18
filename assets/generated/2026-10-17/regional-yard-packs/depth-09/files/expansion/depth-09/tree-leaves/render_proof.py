"""Offline proof generation; motion math is only in tree_motion.py."""
from pathlib import Path
import math,sys,hashlib,json
import numpy as np
from PIL import Image,ImageDraw,ImageSequence,ImageFilter
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parents[1]/'review-08'/'tools'))
from review_io import save_loop,write_json,sha
import tree_motion as t

def h(im):return hashlib.sha256(im.tobytes()).hexdigest()
def run():
    frames=[];ledger=[];rest=t.make_tree_frame(0,'autumn');rigid=t._rigid_scene();woodhash=h(rigid);_,_,_,cores=t._field();native0=np.array(t._canopy_native(0,'autumn'))
    rootroi=(slice(867,901),slice(210,355));restarr=np.array(rest);particle_coverage_union=np.zeros((1024,1536),bool)
    for i in range(33):
        phase=2*math.pi*(i%32)/32
        tree=t.make_tree_frame(phase,'autumn');particle=t.make_leaf_particles(phase,'autumn');litter=t.make_litter_frame('autumn');native=np.array(t._canopy_native(phase,'autumn'));a=np.array(tree)
        layer=Image.alpha_composite(litter,tree);layer.alpha_composite(particle)
        bg=Image.new('RGBA',t.CANVAS,(202,215,194,255));bg.alpha_composite(layer);frames.append(bg.convert('RGB').resize((576,384),Image.Resampling.NEAREST))
        pa=np.array(particle)[:,:,3];particle_coverage_union|=pa>8
        y,x=np.where(np.array(layer)[:,:,3]>8)
        ledger.append({'frame':i,'phase_radians':phase,'tree_rgba_sha256':h(tree),'wood_rgba_sha256':h(t._rigid_scene()),'particle_rgba_sha256':h(particle),'root_changed_rgba_pixels':int(np.any(a[rootroi]!=restarr[rootroi],axis=2).sum()),'core_changed_native_rgba_pixels':int(np.any(native[cores]!=native0[cores],axis=1).sum()),'pins_native':[list(p) for p in t.PINS],'particles':t.particle_states(phase,'autumn'),'scene_visible_coverage_bounds_gt8':[int(x.min()),int(y.min()),int(x.max()+1),int(y.max()+1)]})
    loop=save_loop(frames,ROOT/'previews/tree-and-leaves-autumn.gif',[80]*33);decoded=loop.pop('frames')
    board=Image.new('RGB',(3*384,2*280),(218,223,210));d=ImageDraw.Draw(board)
    for k,i in enumerate([0,4,8,16,24,32]):
        board.paste(decoded[i].resize((384,256),Image.Resampling.NEAREST),((k%3)*384,(k//3)*280));d.text(((k%3)*384+5,(k//3)*280+259),f'decoded autumn frame{i}',fill=(20,20,20))
    board.save(ROOT/'previews/decoded-motion-contact.jpg',quality=93)
    # The GIF is only one proof; check healthy alternative at extremes without recapturing a second loop.
    healthy=[]
    for phase in [0,math.pi/2,math.pi,3*math.pi/2,2*math.pi]:
        a=np.array(t._canopy_native(phase,'summer'));b=np.array(t._canopy_native(0,'summer'))
        healthy.append({'phase':phase,'core_changed_rgba_pixels':int(np.any(a[cores]!=b[cores],axis=1).sum())})
    raw0=np.array(decoded[0]);rr=(slice(round(867*.375),round(901*.375)),slice(round(210*.375),round(355*.375)));decodedroot=[int(np.any(np.array(f)[rr]!=raw0[rr],axis=2).sum()) for f in decoded]
    white=t._rigid_scene().getchannel('A').point(lambda a:255 if a>8 else 0)
    # Visual wood coverage, separately exclude the entire canopy swept region from stable-wood assertion.
    flex_union=np.zeros((1024,1536),np.uint8)
    for phase in [0,math.pi/2,3*math.pi/2]:flex_union=np.maximum(flex_union,np.array(t.make_tree_layers(phase,'autumn')['canopy'])[:,:,3])
    dil=np.array(Image.fromarray(flex_union).filter(ImageFilter.MaxFilter(15)))
    safe=(np.array(white)>0)&(dil==0)&~particle_coverage_union
    sm=np.array(Image.fromarray((safe*255).astype('uint8')).resize((576,384),Image.Resampling.NEAREST))>0
    stablechanges=[int(np.any(np.array(f)[sm]!=raw0[sm],axis=1).sum()) for f in decoded]
    qa={'loop':loop,'wind_implementation':'Actual offline bounded compound canopy deformation; not runtime physics','fixed_native_cores_radius_px':36,'all_root_changed_counts':[r['root_changed_rgba_pixels'] for r in ledger],'all_core_changed_counts':[r['core_changed_native_rgba_pixels'] for r in ledger],'decoded_root_max_changed_pixels':max(decodedroot),'rigid_wood_hash_count':len({r['wood_rgba_sha256'] for r in ledger}),'tree_unique_hashes':len({r['tree_rgba_sha256'] for r in ledger}),'particle_unique_hashes':len({r['particle_rgba_sha256'] for r in ledger}),'stable_wood_display_pixels_tested':int(sm.sum()),'stable_wood_max_changed_display_pixels':max(stablechanges),'healthy_extreme_checks':healthy,'intentional_clipping':'Only outer left-edge tree twigs/leaves crop at scene x0; original master sprites remain complete. No bottom/root or particle clipping.','biological_attachment_verified':False,'season_scope':'Irrigated/riparian-context illustrative California sycamore, not universal San Diego phenology','sky_fence_ground_included':False}
    assert max(qa['all_root_changed_counts'])==0 and max(qa['all_core_changed_counts'])==0
    assert loop['first_last_decoded_equal'] and loop['unique_decoded_frames']>2
    write_json(ROOT/'reports/frame-ledger.json',ledger);write_json(ROOT/'reports/motion-qa.json',qa)
    print(json.dumps(qa,indent=2))
if __name__=='__main__':run()
