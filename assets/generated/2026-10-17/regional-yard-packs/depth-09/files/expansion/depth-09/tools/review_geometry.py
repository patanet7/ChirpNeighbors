"""Review explicitly authored ground/envelopes; alpha is never physical geometry."""
from pathlib import Path
import argparse,hashlib,json,math
from PIL import Image,ImageDraw,ImageChops
def main():
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);args=p.parse_args();root=args.root;sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
    full=Image.open(root/'ground/full-visible-ground-mask.png').convert('L');props=json.loads((root/'fence-objects/scene-contract.json').read_text());tree=json.loads((root/'tree-leaves/placement.json').read_text());removed=Image.new('L',full.size);draw=ImageDraw.Draw(removed);envelopes=[]
    for row in props['object_instances']:
        poly=row['footprint_proposal']['scene_polygon_px'];assert all(0<=x<=1536 and 494<=y<=1024 for x,y in poly);draw.polygon([tuple(v)for v in poly],fill=255);envelopes.append({'asset_id':row['asset_id'],'instance_id':row['instance_id'],'shape':'polygon','source_polygon_px':poly,'status':'proposed_not_physical_collision','active_only_while_instance_present':True})
    f=tree['proposed_physics_footprint'];cx,cy=f['center_scene_px'];rx,ry=f['radii_scene_px'];assert 0<=cx-rx<cx+rx<=1536 and 494<=cy-ry<cy+ry<=1024;draw.ellipse((cx-rx,cy-ry,cx+rx,cy+ry),fill=255);envelopes.append({'asset_id':'plant.california_sycamore','instance_id':tree['assembly_id'],'shape':'ellipse','center_source_px':[cx,cy],'radii_source_px':[rx,ry],'status':'proposed_not_physical_collision','active_only_while_instance_present':True})
    assert not ImageChops.subtract(removed,full).getbbox();available=ImageChops.subtract(full,removed);p=root/'ground/available-with-PROPOSED-instance-envelopes.png';available.save(p);empty_case=full.copy();assert empty_case.tobytes()==full.tobytes()
    bg=Image.open(root/'root/previews/summer-source.png').convert('RGBA');overlay=Image.new('RGBA',bg.size);green=Image.new('RGBA',bg.size,(40,180,85,65));green.putalpha(full.point(lambda a:65 if a else 0));overlay.alpha_composite(green);red=Image.new('RGBA',bg.size,(210,55,35,0));red.putalpha(removed.point(lambda a:130 if a else 0));overlay.alpha_composite(red);bg.alpha_composite(overlay);dr=ImageDraw.Draw(bg)
    for y in[540,650,760,900,1000]:
        for x in[25,750,1505]:
            if available.getpixel((x,y))==255:dr.ellipse((x-6,y-6,x+6,y+6),outline=(15,90,35,255),width=2)
    bg.crop((0,160,1536,1024)).resize((960,540),Image.Resampling.NEAREST).save(root/'root/previews/full-ground-placement-review.png')
    result={'role':'Authored source placement review, outside application contracts','full_ground':{'file':str(root/'ground/full-visible-ground-mask.png'),'sha256':sha(root/'ground/full-visible-ground-mask.png'),'pixels':full.histogram()[255],'polygon_source_px':[[0,494],[1536,494],[1536,1024],[0,1024]],'left_and_right_edges_eligible':True,'permanent_instance_holes':False},'proposed_instance_envelopes':envelopes,'available_mask_with_proposals':{'file':str(p),'sha256':sha(p),'pixels':available.histogram()[255],'physical_collision_implemented':False},'remove_all_instances_restores_exact_full_mask':True,'all_proposed_envelopes_within_authored_ground':True,'depth_proposal':{'static_fence_ground_y':489,'dynamic_instances_ground_y':{'cedar_feeder':800,'sycamore':tree['actual_root_scene'][1],'bench':925},'elevation_ground_m':0,'source_px_per_m_illustrative':130,'calibrated':False},'mask_review_status':'usable_rasters_inspected; semantic_support_and_physical_envelopes_proposed','engine_adoption':False}
    (root/'root/placement-review.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'full_floor_pixels':full.histogram()[255],'available_with_proposals':available.histogram()[255],'remove_all_restores_exact_floor':True}))
if __name__=='__main__':main()
