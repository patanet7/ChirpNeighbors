"""Lossless extraction/translation and explicitly labelled uniform review derivatives.

No body interpolation, pose generation, per-frame fitting, or artistic cleanup.
"""
from pathlib import Path
from PIL import Image, ImageDraw
import hashlib,json,datetime

ROOT=Path(__file__).parent
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
SPECS={
 'dove-walk-v1':{
  'rects':[[0,0,512,512],[512,0,1024,512],[1024,0,1536,512],[0,512,512,1024],[512,512,1024,1024],[1024,512,1536,1024]],
  'baseline':[411,410,410,410,409,412],
  'rootx':[302,298,304,302,300,304],
  'beak':[[491,207],[465,205],[489,207],[489,205],[481,206],[489,207]],
  'contacts':[[[365,409]],[[293,409]],[[294,409],[381,409]],[[365,409]],[[371,408]],[[365,411]]],
  'duration':[130,110,130,130,110,130], 'loop':True,
  'phases':['left-foot-forward','right-foot-pass','right-foot-reach','right-foot-forward','left-foot-pass','left-foot-reach'],
  'issues':['Unconditioned source: identity comparison with canonical standing dove is blocked by source download failure.','Uneven gait, some foot anatomy ambiguity and residual feather/body volume drift.','Six key poses are visibly stepped; no intermediate frames were generated.','Grounded contacts and root are manual approximate annotations, pending owner review.','Native output has fractional alpha, no fully opaque pixels; source preserved unchanged.']},
 'dove-drink-v1':{
  'rects':[[0,0,515,512],[515,0,1019,512],[1019,0,1536,512],[0,512,515,1024],[515,512,1019,1024],[1019,512,1536,1024]],
  'baseline':[425,425,425,372,372,373],
  'rootx':[314,304,293,302,298,298],
  'beak':[[493,209],[503,295],[467,430],[479,379],[468,379],[479,178]],
  'contacts':[[[279,423],[359,424]],[[256,423],[349,424]],[[246,423],[331,424]],[[260,370],[349,371]],[[257,370],[344,371]],[[254,371],[342,372]]],
  'duration':[300,160,200,260,260,220], 'loop':False,
  'phases':['upright-ready','neck-bend','beak-contact-entry','low-sip','low-sip-blink','recovery-upright'],
  'issues':['Conditioned on the new unconditioned walk candidate; canonical identity matching remains blocked.','Generated sheet ignored exact 512-cell boundaries: third bird tail crossed x1024; extraction uses explicit split x1019 to preserve complete tail.','Upper/lower row registration drift corrected by translation only; no per-frame scaling.','Beak contact varies across low poses; basin placement requires review or revised generation.','Sixth pose returns directly upright; intermediate recovery poses remain missing.','Native output has fractional alpha; no binary-alpha cleanup silently applied.','Illustrative motion, not footage-derived biological validation.']}
}

def package(name,s):
 p=ROOT/'batches'/name;im=Image.open(p/'original.png').convert('RGBA');(p/'frames-source').mkdir(exist_ok=True);(p/'frames-review384').mkdir(exist_ok=True)
 manifest={'schemaVersion':1,'kind':'private-generated-animation-candidate','species':'Zenaida macroura','batch':name,'reviewStatus':'reviewed-with-issues; staging permitted for private demo only','canonicalIdentityAccepted':False,'integrated':False,'canvas':[768,768],'root':[420,540],'groundY':600,'frames':[],'clips':[{'name':'walking' if 'walk' in name else 'drinking','frameIndices':list(range(6)),'durationMs':s['duration'],'loop':s['loop']}], 'reviewIssues':s['issues'],'processing':{'source':'lossless rectangular crops and integer translations only','reviewDerivative':'all frames nearest-neighbor 768→384 using identical 1/2 scale; alpha unchanged','generatedBodyPoses':6,'procedurallyGeneratedBodyPoses':0},'compatibility':{'oct12Snapshot':False,'reason':'768x768 source and six 384x384 review frames exceed snapshot edge/total decoded pixels/color/binary-alpha budgets; this is a handoff manifest, not an importable runtime contract. Mac implementation task owns current profile and clip mapping.'},'provenance':{'generator':'OpenAI image_gen.imagegen','promptFile':'prompt.txt','original':'original.png','originalSha256':sha(p/'original.png'),'copyrightLicense':'Not newly verified in this task; no canonical species/source approval asserted.','sourceConditioning':'none' if 'walk' in name else '../dove-walk-v1/original.png'}}
 source_frames=[];review_frames=[];composites=[]
 for i,rect in enumerate(s['rects']):
  # rect.x may differ from nominal grid; all annotations remain in nominal cell coordinates.
  nominalx=(i%3)*512;nominaly=(i//3)*512
  dx=420-s['rootx'][i];dy=600-s['baseline'][i]
  cut=im.crop(rect);frame=Image.new('RGBA',(768,768),(0,0,0,0)); paste=(rect[0]-nominalx+dx,rect[1]-nominaly+dy)
  frame.paste(cut,paste)
  assert frame.getchannel('A').getbbox() is not None
  file=p/'frames-source'/f'{i:02d}.png';frame.save(file);source_frames.append(frame)
  review=frame.resize((384,384),Image.Resampling.NEAREST);review.save(p/'frames-review384'/f'{i:02d}.png');review_frames.append(review)
  bbox=frame.getchannel('A').getbbox();beak=[s['beak'][i][0]+dx,s['beak'][i][1]+dy];contacts=[[x+dx,y+dy] for x,y in s['contacts'][i]]
  manifest['frames'].append({'index':i,'phase':s['phases'][i],'file':str(file.relative_to(p)),'sha256':sha(file),'durationMs':s['duration'][i],'sourceRectangle':rect,'translationFromNominalCell':[dx,dy],'sourceScale':1,'root':[420,540],'groundContacts':contacts,'beak':beak,'beakWaterContact':('drink' in name and i in [2,3,4]),'anchorsReviewed':False,'alphaBBox':bbox,'boundsContained':all([bbox[0]>0,bbox[1]>0,bbox[2]<768,bbox[3]<768])})
  comp=Image.new('RGBA',review.size,(239,235,213,255));comp.alpha_composite(review);composites.append(comp.convert('RGB'))
 source_frames[0].save(p/'preview.apng',save_all=True,append_images=source_frames[1:],duration=s['duration'],loop=0 if s['loop'] else 1,disposal=0,blend=0)
 composites[0].save(p/'preview.gif',save_all=True,append_images=composites[1:],duration=s['duration'],loop=0 if s['loop'] else 1,disposal=2)
 atlas=Image.new('RGBA',(2304,1536));sheet=Image.new('RGB',(1152,820),(239,235,213));draw=ImageDraw.Draw(sheet)
 for i,f in enumerate(source_frames): atlas.paste(f,((i%3)*768,(i//3)*768))
 for i,f in enumerate(composites):
  x=(i%3)*384;y=(i//3)*410;sheet.paste(f,(x,y));draw.text((x+12,y+388),f'{i+1}: {s["phases"][i]} | {s["duration"][i]} ms',fill=(35,40,35))
 atlas.save(p/'atlas.png');sheet.save(p/'contact-sheet.png')
 # Exact pixels, distinct frames and decodable animation verification.
 checks=[]
 for i,frame in enumerate(source_frames):
  rect=s['rects'][i];nominalx=(i%3)*512;nominaly=(i//3)*512;dx,dy=manifest['frames'][i]['translationFromNominalCell'];cut=im.crop(rect)
  recovered=frame.crop((rect[0]-nominalx+dx,rect[1]-nominaly+dy,rect[2]-nominalx+dx,rect[3]-nominaly+dy))
  checks.append({'frame':i,'losslessCropRoundTrip':cut.tobytes()==recovered.tobytes(),'uniquePixelSha256':hashlib.sha256(frame.tobytes()).hexdigest(),'visiblePixels':sum(v>0 for v in frame.getchannel('A').getdata())})
 apng=Image.open(p/'preview.apng');gif=Image.open(p/'preview.gif');manifest['validation']={'perFrame':checks,'uniqueSourceFrames':len(set(c['uniquePixelSha256'] for c in checks)),'apngDecodedFrames':apng.n_frames,'gifDecodedFrames':gif.n_frames,'noPerFrameRescale':True,'exactCropRoundTrips':all(c['losslessCropRoundTrip'] for c in checks),'allBoundsContained':all(f['boundsContained'] for f in manifest['frames'])}
 (p/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 (p/'review.md').write_text('# '+name+' — reviewed candidate, not accepted app art\n\n'+'\n'.join('- '+i for i in s['issues'])+'\n\nOriginal output is retained byte-for-byte. Frame preparation changes position only; the 384px review set uses one uniform nearest-neighbor scale for all frames. Root/contact/beak annotations are provisional source-pixel evidence. No publication or app integration.\n')
 print(name,json.dumps(manifest['validation']))

if __name__=='__main__':
 for name,s in SPECS.items():package(name,s)
