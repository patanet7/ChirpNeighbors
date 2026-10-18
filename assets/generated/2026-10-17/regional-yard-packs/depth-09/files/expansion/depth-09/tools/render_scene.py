"""Compose exact reusable layers and invoke the one shared tree/leaf animator."""
from pathlib import Path
import argparse,hashlib,importlib.util,json,math,sys
import numpy as np
from PIL import Image,ImageDraw,ImageSequence
ROOT=Path(__file__).resolve().parents[1]
def file(value):
    p=Path(value);return p if p.is_absolute()else ROOT/p
def load(value):return Image.open(file(value)).convert('RGBA')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def view(im,width=960):return im.crop((0,160,1536,1024)).resize((width,round(width*9/16)),Image.Resampling.NEAREST)
def save_season_contact(out):
    contact=Image.new('RGB',(1440,2*435),(237,238,229));draw=ImageDraw.Draw(contact)
    for i,s in enumerate(['spring','summer','autumn','winter-summit-snow']):
        label='winter / OPTIONAL summit snow after storm'if s=='winter-summit-snow'else s
        contact.paste(Image.open(out/f'{s}-960.png').resize((720,405),Image.Resampling.NEAREST),((i%2)*720,(i//2)*435+25));draw.text(((i%2)*720+8,(i//2)*435+5),label+' / source candidate',fill=(25,40,30))
    contact.save(out/'ChirpNeighbors-Depth09-Seasons.png');contact.resize((1080,652),Image.Resampling.NEAREST).save(out/'ChirpNeighbors-Depth09-Index.jpg',quality=85)
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path);parser.add_argument('--contacts-only',action='store_true');args=parser.parse_args();global ROOT
    if args.root:ROOT=args.root.resolve()
    if args.contacts_only:save_season_contact(ROOT/'root/previews');return
    c=json.loads((ROOT/'root/render-config.json').read_text());out=ROOT/'root/previews';out.mkdir(parents=True,exist_ok=True)
    spec=importlib.util.spec_from_file_location('depth09_tree',file(c['tree_module']));tree=importlib.util.module_from_spec(spec);spec.loader.exec_module(tree)
    static={k:load(c[k])for k in['sky','mountains_base','mountains_snow','fence']};grounds={s:load(p)for s,p in c['grounds'].items()};props=[dict(x,image=load(x['file']))for x in c['object_instances']]
    def frame(season,phase=0,snow=False):
        im=static['sky'].copy();im.alpha_composite(static['mountains_snow'if snow else 'mountains_base']);im.alpha_composite(grounds[season]);im.alpha_composite(static['fence']);im.alpha_composite(tree.make_litter_frame(season))
        items=[(x['root_scene_px'][1],x['image'])for x in props]+[(c['tree_root_scene_px'][1],tree.make_tree_frame(phase,season))]
        for _,sprite in sorted(items,key=lambda x:x[0]):im.alpha_composite(sprite)
        im.alpha_composite(tree.make_leaf_particles(phase,season));return im
    records=[]
    for season in['spring','summer','autumn','winter']:
        for snow in([False,True]if season=='winter'else[False]):
            name=season+('-summit-snow'if snow else'');im=frame(season,snow=snow);assert im.getchannel('A').getextrema()==(255,255);im.save(out/(name+'-source.png'))
            for width in[960,384]:view(im,width).save(out/f'{name}-{width}.png')
            records.append({'season':season,'summit_snow':snow,'source':str(out/(name+'-source.png')),'normal':str(out/(name+'-960.png')),'mobile':str(out/(name+'-384.png')),'new_primary_scene_identity':False})
    save_season_contact(out)
    autumn=frame('autumn');layers=tree.make_tree_layers(0,'autumn');tiles=[('sky',static['sky']),('mountains / optional snow',static['mountains_snow']),('independent fence',static['fence']),('whole ground / summer dry',grounds['summer']),('objects / independent instances',Image.alpha_composite(props[0]['image'],props[1]['image'])),('rigid tree wood',layers['wood']),('flexible autumn canopy',layers['canopy']),('litter and blowing leaves',Image.alpha_composite(tree.make_litter_frame('autumn'),tree.make_leaf_particles(0,'autumn')))]
    board=Image.new('RGB',(1536,2*282),(225,228,218));dr=ImageDraw.Draw(board)
    for i,(label,im)in enumerate(tiles):
        tile=Image.new('RGBA',(384,256),(237,239,232,255));tile.alpha_composite(im.resize((384,256),Image.Resampling.NEAREST));board.paste(tile.convert('RGB'),((i%4)*384,(i//4)*282+24));dr.text(((i%4)*384+6,(i//4)*282+5),label,fill=(25,40,30))
    board.save(out/'depth-layer-contact.jpg',quality=91)
    # Same original tree/leaf functions for every phase; no duplicated animation implementation.
    frames=[];source_frames=[]
    for k in range(33):
        im=frame('autumn',2*math.pi*k/32);source_frames.append(hashlib.sha256(im.tobytes()).hexdigest());frames.append(view(im).convert('RGB'))
    strip=Image.new('RGB',(960,540*3))
    for j,k in enumerate([0,8,24]):strip.paste(frames[k],(0,j*540))
    pal=strip.quantize(colors=256,method=Image.Quantize.MEDIANCUT);indexed=[f.quantize(palette=pal,dither=Image.Dither.NONE)for f in frames];gif=out/'autumn-yard-tree-sway-blowing-leaves.gif';indexed[0].save(gif,save_all=True,append_images=indexed[1:],duration=100,loop=0,optimize=False,disposal=1)
    decoded=[x.convert('RGB').copy()for x in ImageSequence.Iterator(Image.open(gif))];assert decoded[0].tobytes()==decoded[-1].tobytes();rect=(145,433,207,452);first=decoded[0].crop(rect).tobytes();root_changes=[np.any(np.array(x.crop(rect))!=np.array(decoded[0].crop(rect)),axis=2).sum().item()for x in decoded];assert max(root_changes)==0
    far=(650,20,800,45);a=decoded[0].crop(far).tobytes();assert all(x.crop(far).tobytes()==a for x in decoded)
    receipt={'source_frames':33,'source_first_last_equal':source_frames[0]==source_frames[-1],'decoded_frames':len(decoded),'decoded_unique_frames':len({x.tobytes()for x in decoded}),'decoded_first_last_equal':True,'fixed_root_rect_viewport_px':list(rect),'decoded_root_max_changed_pixels':max(root_changes),'decoded_far_background_unchanged':True,'sha256':sha(gif),'bytes':gif.stat().st_size,'dimensions_px':[960,540],'motion_implementation':'Reused tree_motion.py functions, compound canopy and authored dry-leaf paths','runtime_physics_or_adoption':False}
    sample=Image.new('RGB',(960,3*560),(237,238,229));dr=ImageDraw.Draw(sample)
    for j,k in enumerate([0,8,24]):sample.paste(decoded[k],(0,j*560+20));dr.text((8,j*560+4),f'Decoded autumn yard frame{k}',fill=(25,40,30))
    sample.save(out/'yard-wind-decoded-contact.jpg',quality=90)
    (ROOT/'root/scene-render-receipt.json').write_text(json.dumps({'scene_recipes':records,'wind':receipt,'source_config':str(ROOT/'root/render-config.json'),'source_config_sha256':sha(ROOT/'root/render-config.json')},indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
