from PIL import Image
from pathlib import Path
import json,hashlib,zipfile
p=Path(__file__).parent
manifest={'status':'candidate_art_not_production_approved','generation_calls':6,'method':'built-in image_gen; scripts only crop, uniformly resize and package','assumptions':'North American starter species: American Crow and Common Raven','runtime_canvas':[384,384],'atlas_canvas':[768,768],'physical_scale':{'American Crow':{'length_cm':[40,53],'representative_cm':46.5},'Common Raven':{'length_cm':[56,69],'representative_cm':62.5},'raven_to_crow_representative_length':62.5/46.5,'note':'Reference midpoint ratio, not a measured individual. Pixel canvas sizes do not encode real size; apply world scale separately.'},'clips':{}}
for name in ['crow-walk','raven-hop','crow-idle','raven-idle']:
 im=Image.open(p/'originals'/f'{name}.png').convert('RGBA');w,h=im.size;frames=[];rects=[]
 for i in range(4):
  split=754 if name=='crow-idle' else w//2
  x=0 if i%2==0 else split;y=i//2*h//2;rect=(x,y,split if i%2==0 else w,y+h//2)
  cell=im.crop(rect);cell=cell.resize((round(cell.width*.48),round(cell.height*.48)),Image.Resampling.NEAREST)
  f=Image.new('RGBA',(384,384));f.paste(cell,(4,64));f.save(p/'frames'/f'{name}-{i}.png');frames.append(f);rects.append(rect)
 dur=[1000,120,500,500] if 'idle' in name else ([160,110,140,190] if 'hop' in name else [160]*4)
 frames[0].save(p/'previews'/f'{name}.apng',save_all=True,append_images=frames[1:],duration=dur,loop=0,disposal=0,blend=0)
 gifs=[]
 for f in frames:
  bg=Image.new('RGBA',f.size,(225,220,199,255));bg.alpha_composite(f);gifs.append(bg.convert('RGB'))
 gifs[0].save(p/'previews'/f'{name}.gif',save_all=True,append_images=gifs[1:],duration=dur,loop=0)
 atlas=Image.new('RGBA',(768,768))
 for i,f in enumerate(frames):atlas.paste(f,((i%2)*384,(i//2)*384))
 atlas.save(p/f'{name}-atlas.png')
 manifest['clips'][name]={'frames':4,'durations_ms':dur,'source_rectangles':rects,'source_to_runtime_scale':0.48,'placement_offset':[4,64],'nominal_ground_anchor':[256,316],'anchor_note':'Common cell-space pivot; generated feet vary slightly, no per-frame resizing or synthetic motion. Hop retains generated airborne displacement.','slots':['idle','blink','head_turn'] if 'idle' in name else [name.split('-')[1]],'status':'generated_candidate'}
for s in ['crow','raven']:
 im=Image.open(p/'originals'/f'{s}-canonical.png');im.resize((512,342),Image.Resampling.NEAREST).save(p/f'{s}-canonical-runtime.png')
manifest['remaining_slots']={'crow':['hop','feeding','drinking','preening','takeoff','flight','landing','sleep'],'raven':['walk','feeding','drinking','preening','takeoff','flight','landing','sleep']}
(p/'manifest.json').write_text(json.dumps(manifest,indent=2))
h={str(f.relative_to(p)):hashlib.sha256(f.read_bytes()).hexdigest() for f in p.rglob('*') if f.is_file() and f.name not in ['hashes.json']}
(p/'hashes.json').write_text(json.dumps(h,indent=2))
