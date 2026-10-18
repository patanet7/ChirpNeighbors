"""Rasterize explicitly authored source ground, without inferring physical geometry."""
from pathlib import Path
import argparse,hashlib,json
from PIL import Image,ImageDraw
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,required=True);args=parser.parse_args();root=args.root;d=json.loads((root/'root/scene-basis.json').read_text());dest=root/'ground';dest.mkdir(exist_ok=True);poly=d['ground_polygon_source_px'];size=d['source_canvas_px']
    # Boundary is half-open [0,1536)x[494,1024), authored after actual image inspection.
    mask=Image.new('L',size,0);ImageDraw.Draw(mask).rectangle((0,494,size[0]-1,size[1]-1),fill=255);p=dest/'full-visible-ground-mask.png';mask.save(p)
    viewport=mask.crop(tuple(d['viewport_crop_xyxy'])).resize(tuple(d['viewport_px']),Image.Resampling.NEAREST);viewport.save(dest/'full-visible-ground-mask-960.png')
    assert mask.getbbox()==(0,494,1536,1024)
    for y in[494,512,768,1023]:assert mask.getpixel((0,y))==mask.getpixel((1535,y))==255
    count=mask.histogram()[255];assert count==1536*(1024-494)
    result={'role':'Authored placement eligibility mask, not automatically recovered physical support','mask_file':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'mode':'L','value_meanings':{'0':'outside authored visible floor','255':'authored eligible floor before instance checks'},'source_polygon_px':poly,'coordinate_system':'source_canvas_px','source_dimensions_px':size,'eligible_pixels':count,'full_width_each_floor_row':True,'instance_exclusions_baked':False,'physical_collision_or_support_implemented':False,'review_status':'authored_source_boundary_review_pending_composite','evidence':'Cedar source alpha strong base ends488; faint exterior reaches493. Empty floor from494 extends across every horizontal row.','viewport_mask':str(dest/'full-visible-ground-mask-960.png')}
    (dest/'ground-mask.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'eligible_pixels':count,'bounds':mask.getbbox(),'full_width':True}))
if __name__=='__main__':main()
