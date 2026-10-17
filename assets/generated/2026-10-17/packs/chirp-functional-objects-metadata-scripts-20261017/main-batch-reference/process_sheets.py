"""Crop authored objects without repainting art; make review contact sheets.

Invocation: python process_sheets.py, after original sheet-N.png copies exist.
No image color, alpha, style or geometry edits are performed beyond alpha-bound
crop and transparent padding. Contact-sheet resampling is nearest-neighbor only.
"""
from pathlib import Path
import hashlib, json
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parent
OBJECT_RECTS={
 'object.pedestal_birdbath':[90,20,700,500],
 'object.ground_birdbath':[825,175,1480,480],
 'object.solar_bubbler_fountain':[120,585,665,1010],
 'object.seed_tube_feeder':[995,482,1305,1000],
 'object.cedar_feeder':[200,0,640,512],
 'object.platform_feeder':[820,125,1470,455],
 'object.nectar_feeder':[240,510,555,975],
 'object.bench':[735,515,1480,1010],
 'object.terracotta_pot':[60,20,580,490],
 'object.raised_cedar_planter':[600,80,1340,525],
 'object.rain_barrel':[95,495,590,1120],
 'object.hose_reel':[680,535,1320,1115]
}
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
    manifest=json.loads((ROOT/'inventory.json').read_text())
    report=[]
    for asset in manifest['assets']:
        sheet=ROOT/'originals'/f"sheet-{asset['target_sheet']}.png"
        if not sheet.exists(): continue
        im=Image.open(sheet)
        if im.mode!='RGBA':
            raise ValueError(f'{sheet}: expected native RGBA, got {im.mode}')
        if im.getchannel('A').getextrema()[0]!=0:
            raise ValueError(f'{sheet}: requested transparency absent')
        w,h=im.size
        idx=['top_left','top_right','bottom_left','bottom_right'].index(asset['target_cell'])
        rect=OBJECT_RECTS[asset['asset_id']]
        x,y=rect[:2]
        tile=im.crop(rect)
        bbox=tile.getchannel('A').getbbox()
        if bbox is None: raise ValueError(f'{asset["asset_id"]}: empty crop')
        cut=tile.crop(bbox)
        padded=Image.new('RGBA',(cut.width+16,cut.height+16),(0,0,0,0))
        padded.alpha_composite(cut,(8,8))
        path=ROOT/'sprites'/f"{asset['asset_id']}.san_diego_20261017_candidate_v1.png"
        padded.save(path)
        record={'asset_id':asset['asset_id'],'source':str(sheet.relative_to(ROOT)),'source_sha256':sha(sheet),'source_dimensions_px':[w,h],'quadrant':asset['target_cell'],'manually_reviewed_source_rect_px':rect,'alpha_crop_rect_in_source_rect_px':list(bbox),'source_crop_rect_px':[x+bbox[0],y+bbox[1],x+bbox[2],y+bbox[3]],'transparent_padding_px':8,'file':str(path.relative_to(ROOT)),'sha256':sha(path),'dimensions_px':list(padded.size),'alpha_extrema':list(padded.getchannel('A').getextrema()),'alpha_zero_pixels':sum(v==0 for v in padded.getchannel('A').get_flattened_data()),'alpha_partial_pixels':sum(0<v<255 for v in padded.getchannel('A').get_flattened_data()),'operation':'lossless manually reviewed object-rectangle crop, alpha-bound trim and 8px transparent padding; no repainting'}
        report.append(record)
    (ROOT/'extraction-report.json').write_text(json.dumps(report,indent=2)+'\n')
    cellw,cellh=400,460
    contact=Image.new('RGB',(cellw*4,cellh*3),(232,226,214))
    draw=ImageDraw.Draw(contact)
    for idx,r in enumerate(report):
        x=(idx%4)*cellw;y=(idx//4)*cellh
        for cy in range(y+36,y+cellh-42,16):
            for cx in range(x+8,x+cellw-8,16):
                color=(210,206,197) if ((cx-x)//16+(cy-y)//16)%2 else (226,222,213)
                draw.rectangle((cx,cy,min(cx+15,x+cellw-8),min(cy+15,y+cellh-42)),fill=color)
        sprite=Image.open(ROOT/r['file'])
        scale=min((cellw-35)/sprite.width,(cellh-100)/sprite.height,1)
        display=sprite.resize((round(sprite.width*scale),round(sprite.height*scale)),Image.Resampling.NEAREST)
        px=x+(cellw-display.width)//2;py=y+40+(cellh-95-display.height)//2
        contact.paste(display,(px,py),display)
        draw.text((x+10,y+12),r['asset_id'],fill=(38,48,40))
        draw.text((x+10,y+cellh-31),f"{r['dimensions_px'][0]}x{r['dimensions_px'][1]} RGBA | static candidate",fill=(38,48,40))
    contact.save(ROOT/'previews'/'object-contact-sheet.png')
    print(json.dumps({'extracted':len(report),'sheet_count':len(set(r['source'] for r in report)),'contact_sheet':'previews/object-contact-sheet.png'}))

if __name__=='__main__':main()
