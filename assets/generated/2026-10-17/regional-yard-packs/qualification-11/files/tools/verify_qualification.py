"""Consumer verification for the non-bird source qualification packet."""
from pathlib import Path
import argparse,hashlib,json,io
from PIL import Image
import jsonschema
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def verify(root):
 read=lambda p:json.loads((root/p).read_text());packet=read('admission/admission-packet.json');summary=read('root/qualification-summary.json');assert summary['fresh_subject_grade_counts']=={'pass':12,'repair':1,'blocked':0,'reject':1};assert not summary['physical_geometry_reviewed']and not summary['runtime_admitted'];assert summary['inventory']['availability']=={'AVAILABLE':185,'PLANNED':2}
 schema=read('root/shared/asset-qualification-report-v1.schema.json');labels={e['id']for e in read('root/shared/asset-defect-labels-v1.json')['labels']};findings=read('root/qualification-findings.json')['records']
 for e in findings:jsonschema.validate(e,schema);assert e['canonical_label']in labels
 assert len(findings)==99;bg=Image.open(root/'admission/references/empty-yard-960.png').convert('RGBA');assert sha(root/'admission/references/empty-yard-960.png')==packet['background_reference']['sha256'];composite=bg.copy()
 for e in packet['instances']:
  src=root/'admission'/e['original']['file'];p=root/'admission'/e['display_sprite']['file'];assert sha(src)==e['original']['sha256'];assert sha(p)==e['display_sprite']['sha256'];im=Image.open(p).convert('RGBA');cat=e['catalog_record_exact'];assert im.size==(cat['width'],cat['height']);assert im.tobytes()==Image.open(src).convert('RGBA').resize(im.size,Image.Resampling.NEAREST).tobytes();m=read('admission/'+e['manifest']);assert m['frames'][0]['pivot']==cat['pivot'];assert m['frames'][0]['sourcePixelsPerWorldUnit']==1;assert m['source']['sha256']==sha(p);c=m['frames'][0]['contacts'][0];assert im.getpixel((c['x'],c['y']))[3]>0;assert not e['catalog_geometry_changed'];assert not e['runtime_admitted'];assert not e['physical_geometry_reviewed'];a=im.getchannel('A')
  for k,mask in e['masks'].items():
   got=Image.open(root/'admission'/mask['file']).convert('L');expected=a if k=='soft_alpha'else a.point(lambda x:255 if x>=128 else 0);assert got.tobytes()==expected.tobytes();assert sha(root/'admission'/mask['file'])==mask['sha256']
 for e in sorted(packet['instances'],key=lambda e:(e['diagnostic_root_world'][1],e['catalog_id'])):
  im=Image.open(root/'admission'/e['display_sprite']['file']).convert('RGBA');cat=e['catalog_record_exact'];xy=tuple(e['diagnostic_root_world'][i]-cat['pivot'][['x','y'][i]]for i in[0,1]);composite.alpha_composite(im,xy)
 expected=root/'root/previews/coherent-catalog-set-960.png';assert composite.tobytes()==Image.open(expected).convert('RGBA').tobytes();buf=io.BytesIO();composite.save(buf,format='PNG');assert hashlib.sha256(buf.getvalue()).hexdigest()==sha(expected)
 mobile=composite.resize((384,216),Image.Resampling.NEAREST);assert mobile.tobytes()==Image.open(root/'root/previews/coherent-catalog-set-384.png').convert('RGBA').tobytes()
 repair=read('trees/repairs/q11_layered_torrey_anchor_review_v1/candidate.json');where=root/'trees/repairs/q11_layered_torrey_anchor_review_v1';assert repair['new_art']is False;change=repair['changes'][0];assert change['old_native_xy']==[1033,600]and change['proposed_native_xy']==[1044,546]
 for f in repair['source_files']:
  p=where/f['file'];assert sha(p)==f['sha256'];im=Image.open(p).convert('RGBA');role='wood'if f['variant_id']=='wood_scaffold'else'canopy';assert list(im.getpixel(tuple(change['old_native_xy'])))==change['old_rgba'][role];assert list(im.getpixel(tuple(change['proposed_native_xy'])))==change['new_rgba'][role]
 assert repair['unresolved'][0]['status']=='BLOCKED';assert read('admission/media-preflight.json')['actual_current_parser_inputs']==7
 return {'result':'pass','inventory_pairs':187,'available':185,'planned':2,'fresh_review_subjects':14,'subject_grades':summary['fresh_subject_grade_counts'],'selected_catalog_assets':7,'normalized_records_schema_valid':99,'coherent_960_replay_byte_and_pixel_exact':True,'mobile384_pixel_exact':True,'media_masks_exact':True,'metadata_right_bough_annotation_verified':True,'upper_crown_blocked':True,'generation_calls':0,'physical_geometry_reviewed':False,'runtime_admitted':False}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);a=p.parse_args();print(json.dumps(verify(a.root),indent=2))
