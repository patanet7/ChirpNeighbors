"""Build one selected source bundle from canonical repository bytes. No art generation."""
from pathlib import Path
import argparse,hashlib,io,json,shutil,sys
from PIL import Image,ImageDraw
BASE=Path('assets/generated/2026-10-17/regional-yard-packs');D9=BASE/'depth-09';R8=BASE/'review-08'
def sha(data):return hashlib.sha256(data).hexdigest()
def read(p):return json.loads(p.read_text())
def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2)+'\n')
def build(repo,out,selection):
 out.mkdir(parents=True,exist_ok=True);images={};records={e['source_key'].removeprefix('expansion/depth-09/'):e for e in read(repo/D9/'manifest.json')['files']};sources={}
 def d9(alias):return records[alias]['canonical_path']
 def add(key,path,im=None,operation='Exact canonical bytes'):
  p=repo/path;raw=p.read_bytes();sources[path]={'canonical_path':str(path),'sha256':sha(raw),'bytes':len(raw)}
  if im is None:b=raw
  else:buf=io.BytesIO();im.save(buf,format='PNG');b=buf.getvalue()
  h=sha(b);f='art/'+h+'.png';dest=out/f;dest.parent.mkdir(exist_ok=True);dest.write_bytes(b);im2=Image.open(io.BytesIO(b));a=im2.getchannel('A')if'A'in im2.getbands()else None
  images[key]={'file':f,'sha256':h,'bytes':len(b),'dimensions_px':list(im2.size),'mode':im2.mode,'alpha_extrema':list(a.getextrema())if a else None,'source_canonical_path':str(path),'source_sha256':sha(raw),'operation':operation,'source_rights':'Reused project-generated source; project/service terms; no independent rights or fidelity approval.'};return key
 def load(path):return Image.open(repo/path).convert('RGBA')
 bg={};sky_path=d9('far-ground/references/sky-exact-depth06.png');sky=load(sky_path);a=Image.new('L',sky.size,0);a.paste(255,(0,0,1536,494));sky.putalpha(a);bg['sky']=add('sky',sky_path,sky,'RGB preserved; convert to RGBA; authored sky alpha255 for y<494, alpha0 below. Clouds remain flattened with blue sky.')
 for name,alias in [('mountains','far-ground/layers/far-inland-base-alpha8-offset-minus120.png'),('mountains_snow','far-ground/layers/far-inland-summit-snow-alpha8-offset-minus120.png'),('fence','fence-objects/layers/fence.png')]:bg[name]=add(name,d9(alias))
 bg['grounds']={};bg['litter']={}
 for season in ['spring','summer','autumn','winter']:
  path=d9('far-ground/references/ground-'+season+'-exact-depth06.png');im=load(path);alpha=im.getchannel('A');alpha.paste(255,(0,494,1536,1024));im.putalpha(alpha);bg['grounds'][season]=add('ground_'+season,path,im,'Source RGBA/RGB retained except alpha normalized255 across authored filled-floor y>=494; no color repaint or physical inference.')
  if season in ['autumn','winter']:bg['litter'][season]=add('litter_'+season,d9('tree-leaves/layers/'+season+'-litter.png'))
 modules={}
 for name in ['wood_bare','canopy_healthy','canopy_sparse_senescent','leaf_healthy','leaf_dry','litter_cluster_a','litter_cluster_b']:modules[name]=add('sycamore_'+name,d9('tree-leaves/sources/'+name+'.png'))
 plant=read(selection);plantkey=add('bladderpod_native',plant['selected']['source']['canonical_path']);pc=plant['proposed_placement'];instances=[]
 tp=read(repo/d9('tree-leaves/placement.json'))
 instances.append({'instance_id':'tree','asset_id':'plant.california_sycamore','variant_id':'depth09_reused_sycamore_assembly','modules':{'wood':modules['wood_bare'],'canopy_healthy':modules['canopy_healthy'],'canopy_autumn':modules['canopy_sparse_senescent']},'root_source_px':tp['actual_root_scene'],'pivot_native_px':[668,1180],'resize_px':[585,585],'method':'resize_then_place','physical_calibration':False,'depth':'Actual root source y; wood and canopy are separate visual parts of one sorted actor','season_policy':'Healthy spring/summer; sparse autumn; bare winter. Conditional deciduous tree, not universal regional behavior.'})
 contract=read(repo/d9('fence-objects/scene-contract.json'))
 for e in contract['object_instances']:
  path=e['source_sprite']['path'];key=add(e['asset_id']+'_native',path);instances.append({'instance_id':e['canonical_runtime_id'],'asset_id':e['asset_id'],'variant_id':e['variant_id'],'sprite':key,'pivot_native_px':e['source_native_anchor_px'],'root_source_px':e['scene_root_px'],'scale_native_to_source':e['source_to_scene_affine']['scale'],'method':'affine_nearest','physical_calibration':False,'canonical_runtime_id':e['canonical_runtime_id'],'geometry_match_to_existing_runtime':False,'interaction_points':'Existing catalog slots must not be reused against these proposed scales without reviewed geometry mapping.'})
 instances.append({'instance_id':'bladderpod','asset_id':plant['selected']['asset_id'],'variant_id':plant['selected']['variant_id'],'sprite':plantkey,'pivot_native_px':plant['selected']['geometry']['native_contact_anchor_px'],'root_source_px':pc['actual_transformed_root_px'],'resize_px':pc['resize_px'],'method':'resize_then_place','physical_calibration':False,'season_policy':'Same healthy flowering/pods sprite across four yard seasons, manual conditional review only; no four plant states or year-round bloom claim.','runtime_catalog_registered':False,'wind':'Static whole shrub; no independent flexible parts.'})
 # Include usable raster coverage and authored masks as distinct data.
 masks=[]
 master=read(repo/d9('root/ChirpNeighbors-Depth09-Intake.json'))
 for i,e in enumerate(master['mask_inventory']):
  path=e['file'];key='mask_'+str(i);add(key,path);masks.append({'image':key,'source_semantics':e,'physical_geometry_reviewed':False})
 floor_key=add('full_ground_authored',d9('ground/full-visible-ground-mask.png'))
 # Strong/soft plant mask is measured pixel coverage only.
 src=load(plant['selected']['source']['canonical_path']);pa=src.getchannel('A')
 add('bladderpod_soft_alpha',plant['selected']['source']['canonical_path'],pa,'Exact source alpha byte L mask, visual only')
 add('bladderpod_coverage128',plant['selected']['source']['canonical_path'],pa.point(lambda a:255 if a>=128 else 0),'Binary alpha>=128 L visual mask; no physical geometry')
 m={'document_kind':'integration10-selected-source-assembly','source_inventory_authority':'Existing canonical intake; this is a derived assembly, not a competing inventory.','asset_id':'scene.san_diego_inland_canyon','season_variant_ids':[a['variant_id']for a in master['assets']],'source_scene_commit':'f955c7b97829cb647db6078cf1b7880438fdd886','native_canvas_px':[1536,1024],'viewport_crop_xyxy':[0,160,1536,1024],'world_canvas_px':[960,540],'source_to_world_matrix':[.625,0,0,0,.625,-100,0,0,1],'world_units':'Authored screen units; 130nativepx/metre is illustrative only, never calibrated support or elevation.','background':bg,'instances':instances,'masks':masks,'full_ground_mask':floor_key,'images':images,'default_summit_snow':False,'sky_clouds_separately_extracted':False,'visual_masks_are_physical_geometry':False,'physical_geometry_reviewed':False,'runtime_admitted':False,'owner_accepted':False,'new_image_generation_calls':0,'source_review_limits':master['review_limits'],'edit_controls':'Change root_source_px; hide/remove any actor. Native tree sources preserve the canopy outside the initial scene crop. Source renderer groups tree wood/canopy by root y.','source_lineage':['depth09-catalog.json in existing depth09 publication','plant-selection.json','source-contact-checklist.json','field-requirements.json'],'states':{'generated':'Existing art reused; explicit alpha/nearest derivatives produced','reviewed':'Scoped visual/registration review','staged':'Selected source bundle only','integrated':False,'accepted':False}}
 m['source_review_limits_scope']='Inherited depth09 source-review snapshot. SceneV1 and runtime admission still exclude this layered assembly. Current strict texture manifest and registered-ground candidate validation are recorded separately in current-contract-validation.json; neither creates admission or physical approval.'
 # Native-to-world details are continuous; integer preview sampling is not physical calibration.
 for a in instances:
  a['root_world_px']=[a['root_source_px'][0]*.625,(a['root_source_px'][1]-160)*.625]
  if 'scale_native_to_source'in a:a['native_to_world_scale_xy']=[a['scale_native_to_source']*.625]*2
  else:a['native_to_world_scale_xy']=[a['resize_px'][i]/images[a['modules']['wood']if'modules'in a else a['sprite']]['dimensions_px'][i]*.625 for i in[0,1]]
 # Independent frame-sized review exports fit current profile; no receipt/admission forged.
 export_keys=list(bg['grounds'].values())+[bg[k]for k in ['sky','mountains','mountains_snow','fence']]+list(bg['litter'].values());exports=[]
 for season in ['spring','summer','autumn','winter']:
  for part in ['wood','canopy']:
   key='registered_tree_'+part+'_'+season;add(key,d9('tree-leaves/layers/'+season+'-'+part+'.png'));export_keys.append(key)
 from render_bundle import actor_image
 for season in ['spring','summer','autumn','winter']:
  for actor in instances:
   im=actor_image(out,m,actor,season);path=images[actor['modules']['wood']if'modules'in actor else actor['sprite']]['source_canonical_path'];key='registered_'+actor['instance_id']+'_'+season;add(key,path,im,'Nearest native-source scene registration; root/pivot/resize or affine in assembly; no new art.');export_keys.append(key)
 for key in export_keys:
  origin=images[key];im=Image.open(out/origin['file']).convert('RGBA').crop((0,160,1536,1024)).resize((480,270),Image.Resampling.NEAREST);export='review480_'+key;add(export,origin['source_canonical_path'],im,'Crop native scene[0,160,1536,1024], nearest resize480x270 of named registered/native layer '+key+'; world960x540 density0.5.');a=im.getchannel('A');bbox=a.getbbox()
  if not bbox:exports.append({'image':export,'empty_state':True,'texture_manifest':None});continue
  maxa=a.getextrema()[1];x,y=next((x,y)for y in range(270)for x in range(480)if a.getpixel((x,y))==maxa);manifest={'schemaVersion':1,'profile':'chirp-texture-review-v1','scope':'review-only','approval':'unreviewed','activation':'none','source':{'sha256':images[export]['sha256'],'creator':'ChirpNeighbors source production','tool':'Existing project art and Pillow source export','toolVersion':'integration10','rights':'unreviewed','fidelity':'unreviewed'},'atlas':{'width':480,'height':270,'alpha':'straight-rgba8','colorSpace':'srgb'},'frames':[{'id':'rest','sourceRect':{'x':0,'y':0,'width':480,'height':270},'canvas':{'width':480,'height':270},'trim':{'x':0,'y':0},'pivot':{'x':0,'y':0},'contacts':[{'id':'visual-alpha-sample','x':x,'y':y}],'world':{'width':960,'height':540},'sourcePixelsPerWorldUnit':.5}],'clips':[{'id':'idle','tickRate':30,'loop':True,'frames':[{'frameId':'rest','durationTicks':30}]}]};mp='texture-review/'+export+'.json';write(out/mp,manifest);exports.append({'image':export,'empty_state':False,'texture_manifest':mp,'contact_meaning':'Visual alpha sample only; no foot/beak/support/perch approval; NOT native actor placement pivot.','upstream_registered_image':key})
 m['texture_review_exports']=exports;m['images']=images
 write(out/'yard-source.json',m)
 # Explicit envelopes are authored diagnostics, not a physical-ground approval.
 envelopes=master['assets'][0]['placement']['instance_envelopes_proposed_only']+[{'asset_id':plant['selected']['asset_id'],'instance_id':'bladderpod','shape':'polygon','source_polygon_px':pc['transformed_footprint_polygon_proposed'],'status':'proposed_not_physical_collision','active_only_while_instance_present':True}]
 union=Image.new('L',(1536,1024),0);draw=ImageDraw.Draw(union)
 for e in envelopes:
  if e['shape']=='ellipse':
   x,y=e['center_source_px'];rx,ry=e['radii_source_px'];draw.ellipse((x-rx,y-ry,x+rx,y+ry),fill=255)
  else:draw.polygon([tuple(p)for p in e['source_polygon_px']],fill=255)
 full=Image.open(out/images[floor_key]['file']).convert('L');available=Image.frombytes('L',full.size,bytes(255 if a and not b else 0 for a,b in zip(full.tobytes(),union.tobytes())))
 add('available_with_four_PROPOSED_envelopes',d9('ground/full-visible-ground-mask.png'),available,'Authored full floor minus explicitly listed four proposed instance envelopes. Removing all instances restores full mask; physical support unreviewed.')
 m['images']=images;write(out/'yard-source.json',m)
 write(out/'proposed-support-and-instance-geometry.json',{'role':'Authored support/placement proposal; no reviewed physical geometry','native_floor_polygon':[[0,494],[1536,494],[1536,1024],[0,1024]],'ground_authoring_origin_in_source_px':[0,494],'permanent_holes':[],'base_ground_elevation_authored':0,'metric_calibration':False,'physical_geometry_reviewed':False,'mask_semantics':'Base mask is authored raster coverage. Four instance envelopes are diagnostics only; not roots, collision bodies or automatic support.','envelopes':envelopes,'full_mask_image':floor_key,'available_example_mask_image':'available_with_four_PROPOSED_envelopes','full_floor_pixels':full.histogram()[255],'available_example_pixels':available.histogram()[255],'removing_all_instances_restores_full_floor':True,'support_heights_and_bird_anatomy':'Unreviewed and unimplemented; no perches become valid from alpha or projection tests.'})
 # Native image index is the frozen source-release binding; no circular digest.
 index={'role':'Frozen selected image bytes; keys may reuse one canonical file/hash','images':images};write(out/'source-image-index.json',index);release=sha((out/'source-image-index.json').read_bytes())
 candidate={'kind':'registered-ground-candidate-v1','reviewScope':'unadmitted','units':'authored-ground-units','sourceReleaseDigest':release,'viewport':{'width':960,'height':540},'matrix':[.625,0,0,0,.625,208.75,0,0,1],'outer':[{'x':0,'y':0},{'x':1536,'y':0},{'x':1536,'y':530},{'x':0,'y':530}],'holes':[]}
 compact=lambda d:json.dumps(d,separators=(',',':')).encode();candidate['geometryDigest']=sha(compact({'outer':candidate['outer'],'holes':candidate['holes']}));candidate['calibrationDigest']=sha(compact({k:candidate[k]for k in ['units','viewport','matrix']}));write(out/'registered-ground-candidate.json',candidate);write(out/'expected-ground-release.json',{k:candidate[k]for k in ['sourceReleaseDigest','geometryDigest','calibrationDigest']})
 write(out/'provenance-index.json',{'upstream_files':list(sources.values()),'rights':'Project-generated sources reused; no independent rights or owner approval claimed. Exact upstream originals/prompts/references/rejected studies remain at the pinned canonical source releases and existing Library handoffs.','new_image_generation_calls':0,'source_only':True})
 print(json.dumps({'image_records':len(images),'unique_image_files':len({e['file']for e in images.values()}),'texture_review_exports':len(exports),'empty_exports':sum(e['empty_state']for e in exports),'sourceReleaseDigest':release,'native_sky_alpha':images['sky']['alpha_extrema']}))
def main():
 p=argparse.ArgumentParser();p.add_argument('--repo',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--selection',type=Path,required=True);a=p.parse_args();build(a.repo,a.output,a.selection)
if __name__=='__main__':main()
