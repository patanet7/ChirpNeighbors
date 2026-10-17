"""Shared derived review feeds and compact source/artifact preparation."""
from pathlib import Path
import argparse,json,shutil
from PIL import Image,ImageDraw
from review_io import sha,write_json
def main():
    p=argparse.ArgumentParser();p.add_argument('--repo',type=Path,required=True);p.add_argument('--review-root',type=Path,required=True);args=p.parse_args();R=args.review_root;O=R/'root';d=json.loads((O/'runtime-object-intake.json').read_text());fix=json.loads((R/'oakfix/intake.json').read_text());a=fix['assets'][0]
    # Local source paths are made explicit before public reconciliation; frozen producer intake stays unchanged.
    def localize(v):
        if isinstance(v,str)and len(v)<200 and not any(x.isspace()for x in v):
            p=R/'oakfix'/v
            if p.is_file():return str(p)
        if isinstance(v,list):return[localize(x)for x in v]
        if isinstance(v,dict):return{k:localize(x)for k,x in v.items()}
        return v
    a=localize(a);a['track']='trees_leaves';a['intake_source_manifest']=str(R/'oakfix/intake.json');a['intake_source_manifest_sha256']=sha(R/'oakfix/intake.json')
    assert a['states']=={'generated':True,'reviewed':True,'staged':False,'integrated':False,'accepted':False}
    d['held_controlled_attempt']={'asset_id':a['asset_id'],'variant_id':a['variant_id'],'source_review_status':'held','intake':str(R/'oakfix/intake.json'),'intake_sha256':sha(R/'oakfix/intake.json'),'reason':a['rejection_reason'],'selected_for_intake':False,'original':a['original']}
    d['counts']={'original_candidates_reviewed':8,'accepted_for_scoped_source_review':4,'provisional':3,'held_originals':1,'held_controlled_edits':1,'curated_static_plant_sources':3,'actual_yardscale_wind_GIFs':4,'new_generation_calls':1,'new_accepted_art':0,'new_scene_ids':0,'active_calls':0}
    write_json(O/'runtime-object-intake.json',d)
    for track in ['trees_leaves','plants','objects']:
        review_rows=[]
        for row in d['entries']:
            t='trees_leaves'if row['asset_id']=='coast-live-oak-foliage'else'objects'if row['asset_id'].startswith('object.')else'plants'
            if t==track:review_rows.append({'asset_id':row['asset_id'],'variant_id':row['variant_id'],'source_review_status':row['source_review_status'],'review_findings':row['review_findings'],'scope':row['review_scopes'],'owner_accepted':False,'runtime_integrated':False,'review_source':row['review_evidence']})
        write_json(O/(track+'-intake.json'),{'schema_version':'1.0.0','role':'Derived review delta; old asset records are not duplicated or overwritten.','assets':[a]if track=='trees_leaves'else[],'existing_variant_reviews':review_rows})
    board=Image.new('RGB',(1440,820),(236,238,228));draw=ImageDraw.Draw(board);provenance=[]
    for i,row in enumerate(d['entries']):
        source=args.repo/row['sprite']['file'];im=Image.open(source).convert('RGBA');bbox=im.getchannel('A').point(lambda x:255 if x>8 else 0).getbbox();view=im.crop(bbox);view.thumbnail((336,300),Image.Resampling.NEAREST);x=(i%4)*360+(360-view.width)//2;y=(i//4)*400+48;board.paste(view,(x,y),view.getchannel('A'));label=row['asset_id'].replace('object.','').replace('plant.','');draw.text(((i%4)*360+10,(i//4)*400+10),label,fill=(25,40,30));draw.text(((i%4)*360+10,(i//4)*400+350),row['source_review_status'].replace('accepted-for-scoped-source-review','SCOPED SOURCE PASS').upper(),fill=(125,40,25)if row['source_review_status']=='held'else(35,65,40));provenance.append({'asset_id':row['asset_id'],'variant_id':row['variant_id'],'source':str(source),'sha256':sha(source),'review_fit_only_not_world_scale':True})
    draw.text((10,800),'Eight reviewed original candidates. One further oak edit remains held. No owner/runtime acceptance.',fill=(25,40,30));board.save(O/'ChirpNeighbors-Reviewed-Intake.png');board.resize((1080,615),Image.Resampling.NEAREST).save(O/'ChirpNeighbors-Reviewed-Index.jpg',quality=85);write_json(O/'review-contact-provenance.json',provenance)
    bundle=R/'curated-static-plants';bundle.mkdir(exist_ok=True);members=[]
    for row in d['entries']:
        if row['next_runtime_intake']!='selected_for_static_source_intake_review_only':continue
        source=args.repo/row['sprite']['file'];name=row['asset_id']+'.'+row['variant_id']+'.png';dest=bundle/name;shutil.copyfile(source,dest);assert sha(source)==sha(dest);members.append({'asset_id':row['asset_id'],'variant_id':row['variant_id'],'bundled_file':name,**row['sprite'],'source_anchor_px':row['source_anchor_px'],'ground_or_mount_footprint':row['ground_or_mount_footprint'],'render_proposal':row['render_proposal'],'source_review_status':row['source_review_status'],'botanical_status':row['botanical_status'],'runtime_integrated':False,'owner_accepted':False})
    write_json(bundle/'bundle-inventory.json',{'role':'Three exact static source sprites selected for next intake review; no runtime admission','members':members})
    print(json.dumps(d['counts']))
if __name__=='__main__':main()
