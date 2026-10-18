"""Portable source compositor. Pillow only; no application or physical authority."""
from pathlib import Path
import argparse,copy,json
from PIL import Image,ImageDraw
SIZE=(1536,1024);CROP=(0,160,1536,1024)
def image(root,manifest,key):return Image.open(root/manifest['images'][key]['file']).convert('RGBA')
def actor_image(root,m,a,season):
 out=Image.new('RGBA',SIZE)
 if a['asset_id']=='plant.california_sycamore':
  keys=[a['modules']['wood'],a['modules']['canopy_autumn' if season=='autumn' else 'canopy_healthy']]
  if season=='winter':keys=keys[:1]
  for key in keys:
   src=image(root,m,key);src.putalpha(src.getchannel('A').point(lambda x:0 if x<=1 else x));size=tuple(a['resize_px']);xy=tuple(round(a['root_source_px'][i]-a['pivot_native_px'][i]*size[i]/src.size[i]) for i in [0,1]);out.alpha_composite(src.resize(size,Image.Resampling.NEAREST),xy)
 elif a['method']=='resize_then_place':
  src=image(root,m,a['sprite']);size=tuple(a['resize_px']);xy=tuple(round(a['root_source_px'][i]-a['pivot_native_px'][i]*size[i]/src.size[i])for i in[0,1]);out.alpha_composite(src.resize(size,Image.Resampling.NEAREST),xy)
 else:
  src=image(root,m,a['sprite']);s=a['scale_native_to_source'];t=[a['root_source_px'][i]-a['pivot_native_px'][i]*s for i in[0,1]];out=src.transform(SIZE,Image.Transform.AFFINE,(1/s,0,-t[0]/s,0,1/s,-t[1]/s),Image.Resampling.NEAREST)
 return out

def render(root,m,season,summit_snow=False,hidden=(),moved=None):
 m=copy.deepcopy(m);moved=moved or{}
 for a in m['instances']:
  if a['instance_id']in moved:a['root_source_px']=moved[a['instance_id']]
 out=Image.new('RGBA',SIZE)
 for key in [m['background']['sky'],m['background']['mountains_snow' if summit_snow else 'mountains'],m['background']['grounds'][season],m['background']['fence']]:out.alpha_composite(image(root,m,key))
 if season in ['autumn','winter'] and'tree'in {a['instance_id']for a in m['instances']if a['instance_id']not in hidden}:out.alpha_composite(image(root,m,m['background']['litter'][season]))
 for a in sorted(m['instances'],key=lambda a:(a['root_source_px'][1],a['instance_id'])):
  if a['instance_id']not in hidden:out.alpha_composite(actor_image(root,m,a,season))
 return out.crop(CROP).resize((960,540),Image.Resampling.NEAREST)
def main():
 p=argparse.ArgumentParser();p.add_argument('--bundle',type=Path,required=True);p.add_argument('--output',type=Path,required=True);args=p.parse_args();m=json.loads((args.bundle/'yard-source.json').read_text());o=args.output;o.mkdir(parents=True,exist_ok=True)
 views=[]
 for season in ['spring','summer','autumn','winter']:
  im=render(args.bundle,m,season);im.save(o/(season+'-960.png'));im.resize((384,216),Image.Resampling.NEAREST).save(o/(season+'-384.png'));views.append((season,im))
 render(args.bundle,m,'winter',True).save(o/'winter-optional-summit-snow-960.png')
 render(args.bundle,m,'spring',hidden=[a['instance_id']for a in m['instances']]).save(o/'all-instances-removed-960.png')
 render(args.bundle,m,'spring',moved={'tree':[650,880],'bladderpod':[1200,950],'cedar_feeder':[950,820],'bench':[800,975]}).save(o/'editable-instances-moved-960.png')
 board=Image.new('RGB',(1200,710),'#f1efe7');d=ImageDraw.Draw(board)
 for i,(label,im)in enumerate(views):x=(i%2)*600;y=(i//2)*355;d.text((x+8,y+5),label+' / source review; same bladderpod artwork',fill='#233d30');board.paste(im.resize((600,337),Image.Resampling.NEAREST),(x,y+18))
 board.save(o/'ChirpNeighbors-Integration10-Seasons.png')
 print(json.dumps({'rendered_seasons':4,'static_previews':12,'runtime_admitted':False}))
if __name__=='__main__':main()
