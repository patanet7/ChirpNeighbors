from pathlib import Path
from datetime import datetime, timezone
from PIL import Image
import json,hashlib

ROOT=Path(__file__).resolve().parent
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 d=json.loads((ROOT/'inventory.json').read_text())
 contract=json.loads((ROOT.parent/'references'/'chirp-asset-requirements-and-coverage.json').read_text())['recommended_inventory_contract']
 extracts={r['asset_id']:r for r in json.loads((ROOT/'extraction-report.json').read_text())}
 refs=['[private-source-reference-retained-locally]','[private-source-reference-retained-locally]','[private-source-reference-retained-locally]','[private-source-reference-retained-locally]']
 # Authored points are approximate image observations, not tested physics.
 specs={
 'object.pedestal_birdbath': {'root':[385,471],'feet':[[293,467],[485,467]],'footprint':[[275,447],[385,429],[501,454],[485,480],[310,485]],'points':[('rim_front_perch',380,206),('rim_left_perch',148,131),('drink_water',378,130),('bathe_center',400,145)],'surface':'stone; shallow blue-green water'},
 'object.ground_birdbath': {'root':[1136,447],'feet':[[995,448],[1288,448]],'footprint':[[935,407],[1120,389],[1361,420],[1278,459],[1010,461]],'points':[('rim_front_perch',1134,370),('landing_stone',1350,307),('drink_water',1170,311),('bathe_center',1140,307)],'surface':'terracotta; shallow blue-green water'},
 'object.solar_bubbler_fountain': {'root':[391,966],'feet':[[257,962],[523,962]],'footprint':[[241,934],[385,909],[548,943],[502,978],[287,979]],'points':[('rim_front_perch',392,811),('drink_water',300,731),('bathe_edge',255,739),('water_emitter',387,616),('water_return',395,749)],'surface':'glazed ceramic; stones; water'},
 'object.seed_tube_feeder': {'root':[1151,494],'feet':[],'footprint':[],'points':[('suspension',1151,494),('perch_left',1061,863),('perch_right',1237,863),('mesh_feed_left',1099,832),('mesh_feed_right',1206,832)],'surface':'metal mesh; dry seed; green metal'},
 'object.cedar_feeder': {'root':[395,486],'feet':[[335,475],[457,476]],'footprint':[[324,461],[397,445],[473,469],[455,493],[377,502]],'points':[('tray_front_perch',374,276),('tray_side_perch',547,256),('seed_peck_front',385,252),('seed_peck_side',510,241),('roof_perch',425,27)],'surface':'cedar; glass hopper; dry seed'},
 'object.platform_feeder': {'root':[1157,404],'feet':[[881,329],[1183,413],[1407,310]],'footprint':[[858,319],[1083,286],[1428,320],[1189,426]],'points':[('front_lip_perch',1166,349),('left_lip_perch',892,253),('seed_peck',1136,258)],'surface':'cedar slats; dry seed'},
 'object.nectar_feeder': {'root':[371,519],'feet':[],'footprint':[],'points':[('suspension',371,519),('perch_left',277,905),('perch_right',507,905),('nectar_port_left',349,892),('nectar_port_right',447,892)],'surface':'ruby glass; red metal or plastic; yellow ports'},
 'object.bench': {'root':[1105,936],'feet':[[795,888],[899,841],[1347,974],[1435,901]],'footprint':[[785,880],[913,837],[1440,901],[1360,985]],'points':[('back_perch',1123,552),('armrest_left_perch',827,658),('seat_surface',1123,758)],'surface':'weathered cedar'},
 'object.terracotta_pot': {'root':[323,461],'feet':[[227,459],[400,459]],'footprint':[[196,440],[313,425],[440,446],[395,477],[245,477]],'points':[('rim_perch',308,140),('plant_attachment',317,124)],'surface':'weathered terracotta; empty hollow'},
 'object.raised_cedar_planter': {'root':[966,477],'feet':[[641,386],[1106,494],[1292,353]],'footprint':[[627,379],[849,336],[1302,356],[1123,506]],'points':[('front_edge_perch',948,295),('soil_plant_slot_left',867,209),('soil_plant_slot_right',1090,216)],'surface':'cedar boards; bare dry soil'},
 'object.rain_barrel': {'root':[337,1062],'feet':[[156,1051],[429,1088]],'footprint':[[122,1031],[339,983],[551,1041],[437,1101],[187,1064]],'points':[('spigot_outlet',228,989),('lid_surface',337,536)],'surface':'olive plastic; brass spigot; timber base'},
 'object.hose_reel': {'root':[970,1054],'feet':[[738,1029],[1019,1074],[1168,1013]],'footprint':[[712,1015],[883,970],[1201,1019],[1040,1092]],'points':[('nozzle_outlet',1248,719),('crank',1259,921),('reel_axis',1091,820)],'surface':'dark metal; green hose; brass nozzle'}
 }
 now=datetime.now(timezone.utc).isoformat()
 receipts=[]
 for a in d['assets']:
  r=extracts[a['asset_id']];s=specs[a['asset_id']]
  x0,y0,_,_=r['source_crop_rect_px'];w,h=r['dimensions_px']
  def point(xy):
   p=[round(xy[0]-x0+8,2),round(xy[1]-y0+8,2)]
   assert 0<=p[0]<w and 0<=p[1]<h,(a['asset_id'],xy,p)
   return p
  root=point(s['root']);feet=[point(v) for v in s['feet']];foot=[point(v) for v in s['footprint']]
  contacts=[{'id':n,'position_px':point([x,y]),'coordinate_status':'approximate_manual_image_observation_requires_runtime_alignment','implemented':False} for n,x,y in s['points']]
  prompt=(ROOT/'prompts'/f"sheet-{a['target_sheet']}.txt").read_text().removesuffix('\n')
  source=ROOT/r['source'];variant=a['canonical_lineage']['variant_id']
  a.update({'family_id':a['asset_id'],'variant_id':variant,'species_or_plant_taxon':None,'semantic_role':a['category'],'schema_version':'1.0.0','content_version':'0.1.0','parent_asset_ids':[a['asset_id']] if a['canonical_lineage']['existing_asset_id'] else [],'supersedes':[]})
  groups={group:{key:None for key in keys} for group,keys in contract.items() if group!='asset_identity'}
  groups['source_and_rights'].update({'reference_id':refs,'reference_url':None,'retrieved_at':None,'creator':'OpenAI image generation service','license_id':None,'license_url':None,'attribution_text':'Generated for ChirpNeighbors. No third-party reference pixels were supplied.','modification_notice':'Derivative is crop and transparent padding only.','share_alike_obligations':'unknown_not_asserted','commercial_use_status':'not_independently_reviewed','original_file_hash':r['source_sha256']})
  groups['generation'].update({'job_id':f"CN-SD-OBJECTS-20261017-01-sheet-{a['target_sheet']}",'visible_task_url':None,'prompt_exact':prompt,'negative_prompt_if_supported':None,'reference_asset_ids':refs,'tool':'image_gen.imagegen','settings_if_exposed':{'transparent_background':True},'generation_timestamp':datetime.fromtimestamp(source.stat().st_mtime,timezone.utc).isoformat(),'original_output_paths':[r['source']],'original_hashes':[r['source_sha256']],'edit_history':[{'operation':r['operation'],'source_crop_rect_px':r['source_crop_rect_px'],'derivative':r['file'],'derivative_sha256':r['sha256']}],'failed_attempts':[{'stage':'initial_extraction','reason':'strict quadrant crop included neighboring fragments or clipped silhouettes; replaced with reviewed object rectangles; no rejected art generation'}]})
  groups['geometry'].update({'source_dimensions_px':r['source_dimensions_px'],'frame_canvas_dimensions_px':r['dimensions_px'],'alpha_bounds':list(Image.open(ROOT/r['file']).getchannel('A').getbbox()),'trim_offset':[x0,y0],'world_units':'meter_proposed','physical_measurement_basis':'art direction approximate; no measured product','species_size_range':None,'chosen_instance_size':a['intended_scale'],'pixels_per_world_unit':round(h/a['physical_dimensions']['height_m'],2),'root_pivot':root,'feet_contact_points':feet,'beak_anchor':None,'perches':[c for c in contacts if 'perch' in c['id']],'collision_shapes':[],'occluders':[],'layer_depth':'placeable_yard_prop; instance depth supplied by future scene','material_surface':s['surface']})
  groups['clips']={k:None for k in contract['clips']};groups['clips'].update({'frames':[r['file']],'frame_durations_ms':None,'loop_mode':None,'visual_review_receipt':'previews/object-contact-sheet.png; previews/object-contact-light.png; previews/object-contact-dark.png'})
  groups['interaction'].update({'affordances':[c['id'] for c in contacts],'diet_compatibility':{'seed':['object.seed_tube_feeder','object.cedar_feeder','object.platform_feeder'],'nectar':['object.nectar_feeder']}.get('seed') if a['asset_id'] in ['object.seed_tube_feeder','object.cedar_feeder','object.platform_feeder'] else (['nectar'] if a['asset_id']=='object.nectar_feeder' else []),'plant_habitat':None,'perch_capacity':None,'water_capacity':None,'inflow_outflow':{'points':[c for c in contacts if any(n in c['id'] for n in ['outlet','emitter','return'])],'capacity_and_flow_unimplemented':True},'wetness':{'state_slots':a['state_slots'],'implemented':False},'snow_attachment_surfaces':[],'wind_response':{'status':'metadata_only_not_implemented','type':'suspended_pendulum' if a['wind_rig']['type']=='suspended_pendulum' else 'rigid','attachment_point_px':root if a['wind_rig']['type']=='suspended_pendulum' else None,'separate_rigged_parts':[]},'leaf_emitters':[],'holiday_theme':None,'season_applicability':{'region':'San Diego/Southern California','no_default_snow_ice_or_autumn_orange':True,'weathering_or_water_state_needs_only':True}})
  if a['asset_id'] in ['object.seed_tube_feeder','object.cedar_feeder','object.platform_feeder']:groups['interaction']['diet_compatibility']=['seed'];
  groups['runtime'].update({'package_manifest':'manifest.json','loader_profile':'intake_only_not_a_validated_runtime_loader_contract','scene_preset_ids':['scene.san_diego_coastal_urban','scene.san_diego_inland_canyon','scene.san_diego_managed_patio'],'fallback':None})
  defects=['Dense shaded textures and antialiased edges are not proven to meet a strict logical pixel grid; final style acceptance pending.','Existing reference-pack image bytes could not be inspected (download proxy HTTP 403); Library IDs are provenance only.','Flattened body, contact shadow, and fill/water are not independently authored production layers.','No state variants, animation clips, physics, or runtime interaction alignment implemented.']
  if a['asset_id']=='object.nectar_feeder':defects.append('Ruby-red glass/liquid appearance does not clearly distinguish colored glass from red liquid; revise realism before final canon acceptance.')
  if a['asset_id']=='object.solar_bubbler_fountain':defects.append('Solar power is an intended semantic capability only; no visible solar panel or implemented pump control.')
  groups['evidence'].update({'requirement_ids':['ART-005','ART-006','ART-020','ART-052','ART-053','ART-055','ART-056','ART-058','ART-062','ART-063'],'source_message_ids':[],'state':'reviewed_static_candidate','owner':'ChirpNeighbors asset-production objects workstream','last_verified_at':now,'test_command':'python process_sheets.py; final manifest and source/derivative hash validation','test_result':'12 native-alpha source crops decode; each reviewed against originals and three contact backgrounds; no acceptance or runtime claim','screenshot_or_playback_receipt':['previews/object-contact-sheet.png','previews/object-contact-light.png','previews/object-contact-dark.png'],'reviewer':'objects agent; parent visual completeness/crop/alpha presentation check','known_defects':defects,'next_action':'Mac owner verify complete archive bytes, import canonical tracker delta, review strict pixel style/interaction anchors, then perform canon Git checkpoint'})
  a.update(groups)
  a['states'].update({'generated':True,'static':True,'reviewed':True,'tested':True})
  a['review_status']='reviewed_candidate_owner_acceptance_pending'
  a['rejection_reason']=None
  a['pivot']=root;a['anchors']=contacts;a['ground_contact_footprint']={'coordinate_system':'sprite_canvas_px','polygon_px':foot,'status':'proposed_contact_geometry_not_physics','suspended_no_ground_contact':not bool(foot)}
  a['functional_interactions']={'status':'metadata_only_not_runtime_implemented','coordinate_system':'sprite_canvas_px','points':contacts}
  a['wind_rig']=groups['interaction']['wind_response']
  a['derivatives']=[r]
  a['references']=[{'library_file_id':v,'pixels_inspected':False,'supplied_to_generator':False,'status':'provenance_only_download_proxy_http_403'} for v in refs]
  a['layers']={'actual':[{'id':'flattened_static_sprite','path':r['file'],'includes':['body','contact_shadow']+(['water','water_fx'] if a['category']=='water' else [])}],'requested_unproduced':a['layer_slots'],'separable_production_layers':False}
  for state in a['state_slots']:state['status']='missing'
  actual={'water':'full_with_static_water','feeder':'filled_static','furniture':'dry_static','container':'empty_or_bare_soil_static','utility':'dry_static'}[a['category']]
  a['generated_state']=actual
  a['canonical_intake']={'status':'pending_mac_verification','commit':None,'remote_sha':None,'canonical_tracker_library_id':'[private-source-reference-retained-locally]'}
  receipts.append({'asset_id':a['asset_id'],'candidate_id':a['asset_id']+'.'+variant,'original_sha256':r['source_sha256'],'sprite_sha256':r['sha256'],'review':'technical_pass_style_and_owner_acceptance_pending'})
 d['canonical_intake']={'status':'pending_mac_verification','commit':None,'remote_sha':None}
 d['status']='generated_and_reviewed_static_candidates_not_staged_integrated_or_accepted'
 d['recommended_inventory_contract_source']='[private-source-reference-retained-locally]'
 d['original_generator_paths']=['/workspace/generated_images/exec-3dc255f6-061a-4c39-877e-449ffe153066.png','/workspace/generated_images/exec-ff096338-2334-4af9-9fa5-74aa1a346bd7.png','/workspace/generated_images/exec-d5f99c33-bdc6-4c36-94d7-de504b19348c.png']
 d['review_receipt']={'at':now,'reviewer':'objects agent + parent scoped visual review','passed':['12 distinct silhouettes','corrected crops exclude neighboring fragments','native alpha transparency','light/dark/checker presentation'],'pending':['strict pixel grid conformity','nectar feeder appearance realism','canon style/reference comparison','runtime anchors/scale','Mac bytes and canonical Git checkpoint'],'no_implementation_claim':['state variants','animation','physics','staging','integration','acceptance']}
 (ROOT/'manifest.json').write_text(json.dumps(d,indent=2)+'\n')
 (ROOT/'review-receipt.json').write_text(json.dumps({'created_at':now,'assets':receipts,'review':d['review_receipt']},indent=2)+'\n')
 print(json.dumps({'assets':len(d['assets']),'manifest':'manifest.json','status':d['status']}))

if __name__=='__main__':main()
