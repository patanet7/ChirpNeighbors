"""Direct owner card assembled from retained cleanup renders; never edits source art."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import hashlib,json
D=Path(__file__).parent;R=D.parent.parent;P=R/'experiments/finch-fixed-body-rig-cleanup-v2';font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',15);small=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',13);frames=[]
for phase in [0,1,3,0]:
 card=Image.new('RGB',(960,400),'#142a27');d=ImageDraw.Draw(card);d.text((14,10),f'Finch seam review — phase {phase} / angle {[0,-.12,0,.12,0][phase]:+.2f} rad',font=font,fill='#f1ead7');d.text((14,35),'Rigged existing pixels. Owner judgment pending. No new drawings or generation.',font=small,fill='#ffbd99')
 for label,fname,x in [('Before',P/f'before/rig-frame-{phase:02}.png',12),('After',P/f'frames-native1024/{phase:02}.png',116)]:
  im=Image.open(fname).convert('RGBA');tile=Image.new('RGBA',(1024,1024),'#e1dbc8');tile.alpha_composite(im);card.paste(tile.resize((96,96),Image.Resampling.NEAREST).convert('RGB'),(x,91));d.text((x,68),label+'96px',font=small,fill='#f1ead7')
 im=Image.open(P/f'frames-native1024/{phase:02}.png').convert('RGBA');comp=Image.new('RGBA',im.size,'#e1dbc8');comp.alpha_composite(im)
 jaw=comp.crop((590,455,650,510)).resize((240,220),Image.Resampling.NEAREST).convert('RGB');j=ImageDraw.Draw(jaw);j.rectangle(((607-590)*4,(475-455)*4,(633-590)*4-1,(492-455)*4-1),outline='#e83358',width=2);card.paste(jaw,(245,91));d.text((245,68),'Jaw 4x — phase1 flagged',font=small,fill='#f1ead7')
 overlap=comp.crop((445,465,650,580)).resize((410,230),Image.Resampling.NEAREST).convert('RGB');card.paste(overlap,(530,91));d.text((530,68),'Neck/shoulder 2x — phase3 flagged',font=small,fill='#f1ead7')
 d.text((12,338),'Phase1 jaw: [607,475,633,492], 144 uncovered source pixels remain.',font=small,fill='#ffbd99');d.text((12,359),'Phase3 overlap: [445,465,650,580]. Check feather seam, jaw and lighting.',font=small,fill='#ffbd99');d.text((12,380),'96px is a proposed review size. Feet/body unchanged; no art or yard admission.',font=small,fill='#f1ead7');frames.append(card)
out=D/'ChirpNeighbors-Jaw-and-Overlap-Direct-Review.gif';frames[0].save(out,save_all=True,append_images=frames[1:],duration=[800,1400,1400,800],loop=0,optimize=False)
receipt=json.loads((D/'review-receipt.json').read_text());assert hashlib.sha256(out.read_bytes()).hexdigest()==receipt['sha256'];print('Direct GIF reproduces exact retained digest; no source writes')
