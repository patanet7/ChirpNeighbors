"""Create a minimal source intake from frozen authoritative IDs and named reviews."""
from pathlib import Path
import argparse,json
from PIL import Image
from review_io import PREFIX,sha,write_json,resolve
SEASONS=['spring','summer','autumn','winter']
def main():
    p=argparse.ArgumentParser();p.add_argument('--repo',type=Path,required=True);p.add_argument('--review-root',type=Path,required=True);args=p.parse_args();repo=args.repo;root=args.review_root
    original=json.loads((repo/PREFIX/'repair-07/repair-catalog.json').read_text())
    botany=json.loads((root/'botany/botanical-review.json').read_text());objects=json.loads((root/'objects/review.json').read_text())
    bot={a['asset_id']:a for a in botany['records']};obj={a['asset_id']:a for a in objects['assets']};rows=[]
    for rec in original['assets']:
        a=rec['intake'];aid=a['asset_id'];review=obj[aid]if aid in obj else bot[aid];is_object=aid.startswith('object.')
        sprite=rec.get('registered_assembly')or rec['source_files'][0]['file'];im=Image.open(repo/sprite);dimensions=list(im.size)
        if aid=='coast-live-oak-foliage':anchor=a['placement_anchor_px'];footprint=a['footprint'];size=[480,480];state=['healthy_leaf_on']; wind={'kind':'compound_canopy_proof','runtime_available':False,'source_rig':resolve(repo,'expansion/repair-07/oak/rig.json').relative_to(repo).as_posix(),'scope':'Four fixed attachment envelopes; anatomical leaf/branch rig unavailable.'}
        elif aid=='deergrass-vegetative':anchor=a['geometry']['assembly_root_px'];footprint=a['geometry']['ground_contact_footprint'];size=[240,192];state=['healthy_vegetative'];wind={'kind':'two_reused_fan_rotations_proof','runtime_available':False,'source_rig':resolve(repo,'expansion/repair-07/deergrass/metadata/rig.json').relative_to(repo).as_posix(),'scope':'Fixed fibrous crown/core and compound fans; per-blade anatomy unavailable.'}
        elif not is_object:
            anchor=a['geometry']['anchor_px'];footprint={'bbox_px':a['geometry']['contact_footprint_bbox_px'],'polygon_px':a['geometry']['contact_footprint_polygon_px'],'calibrated':False};size=[98,113]if aid=='plant.bladderpod'else[125,150];state=a.get('actual_states',[]);wind={'kind':'needs_art','runtime_available':False,'independent_flexible_parts':[]}
        else:
            anchor=review['placement_anchor_exact_source']['point'];footprint=review['ground_contact_footprint_exact_source'];size=review['existing_yard_scale']['normal_canvas_size_px'];state=['weathered_static'];wind={'kind':'rigid_static','response':0,'runtime_available':False,'moving_hardware_parts':'needs_art_only_if_required'}
        status=review.get('source_review_status')or review.get('classification');assert status,aid
        row={'asset_id':aid,'variant_id':a['variant_id'],'family_id':a.get('family_id',aid),'source_review_status':status,'review_scopes':review.get('scoped_results',review.get('review_scopes',{})),'sprite':{'file':sprite,'sha256':sha(repo/sprite),'dimensions_px':dimensions,'mode':im.mode,'alpha_extrema':list(im.getchannel('A').getextrema()),'kind':'registered_assembly_derivative'if rec.get('registered_assembly')else'individual_static_sprite'},'source_modules':rec['source_files'],'source_anchor_px':anchor,'ground_or_mount_footprint':footprint,'render_proposal':{'world_canvas_px':[960,540],'width':size[0],'height':size[1],'pivot':{'x':round(anchor[0]*size[0]/dimensions[0],4),'y':round(anchor[1]*size[1]/dimensions[1],4)},'physical_scale_verified':False,'basis':'Earlier recorded diagnostic yard size; no live Mac acceptance.'},'catalog_mapping':{'existing_catalog_id':None,'candidate_existing_kind':None if is_object else'plant','status':'held_missing_runtime_kind_and_catalog_id'if is_object else'pending_explicit_catalog_id_registration'},'actual_state_art':state,'season_variants':{s:{'separate_art_available':False,'fallback':'explicit_static_base_source_only','ecology':'Region-specific foliage/flower/fruit/stress response; no default snow or orange autumn.'if not is_object else'Rigid base reused; separate wet/weathering/decoration states need art.'}for s in SEASONS},'wind':wind,'interaction_slots':[],'runtime_integrated':False,'owner_accepted':False,'source_intake':rec['source_manifest'],'source_intake_sha256':rec['source_manifest_sha256'],'review_evidence':str(root/('objects'if is_object else'botany')/'review.json')}
        if is_object:
            row['observed_functional_markers']=review['functional_points_exact_source'];row['held_functional_scopes']=review['held_scope']
            if aid=='object.wall_tool_rail':
                row['observed_functional_markers']=[dict(x,id=x['id'].replace('hook_seat_','hook_outer_curve_marker_'),semantic_status='observed_source_marker_not_load_contact',implemented=False)for x in row['observed_functional_markers']]
                row['contact_metadata_correction']='Prior hook_seat names implied unvalidated hanging contacts. Exact coordinates are preserved as outer-curve markers; no hanging/load slots are admitted. Wall mount needs projection review; no ground footprint.'
        else:
            row['review_evidence']=str(root/'botany/botanical-review.json')
            row['botanical_status']=review['botanical_status']
            row['review_scopes']={'static_geometry':review.get('source_geometry_review',status),'botanical':review['botanical_status']}
            row['wind']['yard_scale_proofs']=[str(root/'wind'/f'{scope}-gentle-yard-{w}.gif')for w in [960,384]]if (scope:={'coast-live-oak-foliage':'oak','deergrass-vegetative':'deergrass'}.get(aid))else[]
        row['review_findings']=review.get('actual_defects',review.get('concrete_defects',[]))
        row['style_status']='provisional_strict_logical_pixel_grid_not_established; practical static silhouette/material review completed'
        row['next_runtime_intake']='excluded_botanical_hold'if status=='held'else('held_missing_owned_runtime_kind'if is_object else'selected_for_static_source_intake_review_only')
        rows.append(row)
    assert len(rows)==8 and len({(a['asset_id'],a['variant_id'])for a in rows})==8
    result={'schema_version':'1.0.0','role':'Minimal reviewed source projection into the existing canonical runtime object catalog; not a replacement inventory or admitted runtime package.','derived_from':str(PREFIX/'repair-07/repair-catalog.json'),'existing_runtime_contract':'runtime-contract.json','entries':rows,'review_status_definitions':{'accepted-for-scoped-source-review':'Named static-source/silhouette/botanical scopes passed; final style/owner/runtime acceptance remains separate.','provisional':'Specific readability, morphology, presentation or contact limitation remains.','held':'Named source scope is unsuitable for the target until corrected.'},'reviewed_original_candidate_count':8,'new_scene_ids':0,'runtime_integrated':False,'owner_accepted':False,'contact_metadata_corrections':1,'controlled_art_repair':'One oak foliage edit only; selected or held after actual resulting pixels are reviewed.'}
    result['curated_static_plant_source_selection']=[{'asset_id':r['asset_id'],'variant_id':r['variant_id']}for r in rows if r['next_runtime_intake']=='selected_for_static_source_intake_review_only']
    result['controlled_art_repair']='One oak foliage edit completed but botanical defect persists. Held attempt retained, no replacement selected, generation stopped.'
    write_json(root/'root/runtime-object-intake.json',result);print(json.dumps({'entries':len(rows),'statuses':{s:sum(r['source_review_status']==s for r in rows)for s in set(r['source_review_status']for r in rows)},'curated_static_plant_sources':len(result['curated_static_plant_source_selection'])}))
if __name__=='__main__':main()
