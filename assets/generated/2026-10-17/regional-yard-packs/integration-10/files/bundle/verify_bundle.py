"""Verify the selected source bundle, image/mask semantics and actual edit renders."""
from pathlib import Path
import argparse,hashlib,json,sys,tempfile
from PIL import Image,ImageChops
from render_bundle import render
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def verify(root):
 m=json.loads((root/'yard-source.json').read_text());assert not m['runtime_admitted']and not m['physical_geometry_reviewed']and not m['owner_accepted'];assert len(m['instances'])==4;assert len(set(m['season_variant_ids']))==4
 for e in m['images'].values():
  p=(root/e['file']).resolve();assert p.is_relative_to(root.resolve());assert sha(p)==e['sha256'];im=Image.open(p);assert list(im.size)==e['dimensions_px']and im.mode==e['mode'];assert p.stat().st_size==e['bytes']
 sky=Image.open(root/m['images']['sky']['file']);assert sky.mode=='RGBA';assert sky.getchannel('A').crop((0,494,1536,1024)).getextrema()==(0,0);assert sky.getchannel('A').crop((0,0,1536,494)).getextrema()==(255,255)
 for key in m['background']['grounds'].values():assert Image.open(root/m['images'][key]['file']).getchannel('A').crop((0,494,1536,1024)).getextrema()==(255,255)
 full=Image.open(root/m['images'][m['full_ground_mask']]['file']).convert('L');assert full.histogram()[255]==814080;assert full.crop((0,494,1536,1024)).getextrema()==(255,255)
 exported=0;empty=0
 for e in m['texture_review_exports']:
  im=Image.open(root/m['images'][e['image']]['file']);assert im.size==(480,270)and im.mode=='RGBA'
  if e['empty_state']:assert im.getchannel('A').getextrema()==(0,0);assert e['texture_manifest']is None;empty+=1;continue
  d=json.loads((root/e['texture_manifest']).read_text());assert d['source']['sha256']==sha(root/m['images'][e['image']]['file']);f=d['frames'][0];assert f['canvas']=={'width':480,'height':270};assert d['activation']=='none'and d['approval']=='unreviewed';c=f['contacts'][0];assert im.getpixel((c['x'],c['y']))[3]>0;assert m['images'][e['image']]['bytes']<=4194304;exported+=1
 candidate=json.loads((root/'registered-ground-candidate.json').read_text());assert candidate['sourceReleaseDigest']==sha(root/'source-image-index.json');assert candidate['reviewScope']=='unadmitted'and candidate['holes']==[]
 seasons=['spring','summer','autumn','winter'];hashes=[]
 for s in seasons:
  im=render(root,m,s);assert im.size==(960,540);assert im.getchannel('A').getextrema()==(255,255);hashes.append(hashlib.sha256(im.tobytes()).hexdigest())
 assert len(set(hashes))==4
 removed=render(root,m,'spring',hidden=[a['instance_id']for a in m['instances']]);moved=render(root,m,'spring',moved={'tree':[650,880],'bladderpod':[1200,950],'cedar_feeder':[950,820],'bench':[800,975]});assert ImageChops.difference(removed,render(root,m,'spring')).convert('RGB').getbbox();assert ImageChops.difference(moved,render(root,m,'spring')).convert('RGB').getbbox()
 # Both prop and plant can be independently removed while background source bytes remain fixed.
 for a in m['instances']:assert ImageChops.difference(render(root,m,'summer',hidden=[a['instance_id']]),render(root,m,'summer')).convert('RGB').getbbox()
 return {'result':'pass','image_records':len(m['images']),'unique_image_files':len({e['file']for e in m['images'].values()}),'strict_manifest_candidates_pixel_checked':exported,'explicit_empty_states':empty,'seasonal_renders':4,'all_season_views_opaque':True,'native_sky_has_real_transparency':True,'full_floor_pixels':814080,'four_instances_move_and_remove':True,'sourceReleaseDigest':candidate['sourceReleaseDigest'],'physical_geometry_reviewed':False,'runtime_admitted':False}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--bundle',type=Path,required=True);a=p.parse_args();print(json.dumps(verify(a.bundle),indent=2))
