"""Capture the existing renderers' actual RGBA frames, then review at yard scale.
No wind math is duplicated. Frozen producer files run only in temporary copies.
"""
from pathlib import Path
import argparse,contextlib,hashlib,io,json,runpy,sys,tempfile
from PIL import Image,ImageDraw
from review_io import resolve,stage_scope,save_loop,write_json,sha
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--repo',type=Path,required=True);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args();out=args.output;out.mkdir(parents=True,exist_ok=True);results=[]
    for scope in ['oak','deergrass']:
        per_size={960:[],384:[]};source_hashes=[]
        plate=Image.open(resolve(args.repo,'expansion/repair-07/'+scope+('/references/existing-yard-review-plate.png'if scope=='oak'else'/references/depth06-coastal-review-source.png'))).convert('RGBA')
        source_ledger=json.loads(resolve(args.repo,'expansion/repair-07/'+scope+('/reports/frame-ledger.json'if scope=='oak'else'/metadata/frame-ledger.json')).read_text());source_ledger=source_ledger if isinstance(source_ledger,list)else source_ledger['frames']
        def capture(im,k):
            digest=hashlib.sha256(im.tobytes()).hexdigest();expected=source_ledger[k]['rgba_tree_sha256'if scope=='oak'else'frame_RGBA_sha256'];assert digest==expected,(scope,k)
            source_hashes.append(digest)
            # Every original frame is checked; every other phase is delivered at the same cycle speed.
            if k%2:return
            yard=plate.copy();size=(768,768)if scope=='oak'else(384,307);xy=(23,231)if scope=='oak'else(578,544)
            yard.alpha_composite(im.resize(size,Image.Resampling.NEAREST),xy);view=yard.crop((0,160,1536,1024))
            for width in per_size:per_size[width].append(view.resize((width,round(width*9/16)),Image.Resampling.NEAREST).convert('RGB'))
        with tempfile.TemporaryDirectory(prefix='chirp-yard-wind-review-')as temporary:
            stage=Path(temporary);stage_scope(args.repo,scope,stage)
            script=stage/('render_gentle.py'if scope=='oak'else'scripts/render_gentle.py')
            with contextlib.redirect_stdout(io.StringIO()):
                if scope=='oak':
                    source=script.read_text();line=next(i for i,s in enumerate(source.splitlines(),1)if "bg=Image.new('RGBA',(n,n),(214,219,207,255))"in s);seen=set()
                    def tracer(frame,event,arg):
                        if frame.f_code.co_filename!=str(script):return None
                        if event=='line'and frame.f_lineno==line:
                            k=frame.f_locals['i']
                            if k not in seen:seen.add(k);capture(frame.f_locals['tree'],k)
                        return tracer
                    sys.settrace(tracer)
                    try:runpy.run_path(str(script),run_name='__main__')
                    finally:sys.settrace(None)
                else:
                    module=runpy.run_path(str(script))
                    for k in range(49):capture(module['frame'](k,module['R']['gentle_rotation_cap_deg'])[0],k)
        assert len(source_hashes)==(33 if scope=='oak' else 49)
        files=[]
        for width,frames in per_size.items():
            path=out/f'{scope}-gentle-yard-{width}.gif';duration=160 if scope=='oak' else 320;durations=[duration]*len(frames);durations[-1]=duration//2
            receipt=save_loop(frames,path,durations);decoded=receipt.pop('frames');receipt.update(file=path.name,source_samples_checked=len(source_hashes),sampling='Every second source phase; original cycle speed, closing frame half hold',physical_camera_fit_verified=False)
            # A fixed bark/root rectangle and unchanged far-yard patch must survive GIF encoding.
            # Interior of the published protected core/root after assembly->yard->viewport mapping.
            root_rect=((238,448,285,465)if scope=='oak'else(465,411,496,416))
            factor=width/960;rect=tuple(round(v*factor)for v in root_rect);a=decoded[0].crop(rect).tobytes();assert all(f.crop(rect).tobytes()==a for f in decoded)
            far=(round(800*factor),round(25*factor),round(900*factor),round(75*factor));a=decoded[0].crop(far).tobytes();assert all(f.crop(far).tobytes()==a for f in decoded)
            receipt.update(decoded_fixed_root_rect=rect,decoded_root_unchanged=True,decoded_far_background_unchanged=True)
            files.append(receipt)
            if width==960:
                contact=Image.new('RGB',(960,3*560),(237,238,228));draw=ImageDraw.Draw(contact)
                for j,k in enumerate([0,len(decoded)//3,2*len(decoded)//3]):contact.paste(decoded[k],(0,j*560+20));draw.text((8,j*560+4),f'{scope} actual yard scale / decoded frame {k}',fill=(25,35,25))
                contact.save(out/f'{scope}-yard-decoded-contact.jpg',quality=90)
        results.append({'scope':scope,'all_source_RGBA_frames_match_frozen_ledger':True,'source_frames':len(source_hashes),'yard_review_scale':.5 if scope=='oak'else.4,'normal_and_mobile':files,'state':'actual wind source proof, no runtime implementation','visual_review':'pending inspection'})
    write_json(out/'yard-wind-qa.json',{'source_checkpoint':'repair-07','new_art_originals':0,'new_scene_identities':0,'proofs':results})
    print(json.dumps({'status':'passed','proofs':[{**r,'normal_and_mobile':[{k:v for k,v in x.items()if k!='frames'}for x in r['normal_and_mobile']]}for r in results]}))
if __name__=='__main__':main()
