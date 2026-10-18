from pathlib import Path
from PIL import Image
import hashlib,json,math,re
P=Path(__file__).resolve().parent;R=Path('/workspace/asset-production');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();h=json.loads((P/'family-handoff.json').read_text());palette=json.loads((P/'existing-palette.json').read_text());checks=[]
def check(n,v):checks.append({'check':n,'pass':bool(v)});assert v,n
def fid(im):return 'frame.sha256.'+hashlib.sha256(f'RGBA8;{im.width}x{im.height};'.encode()+im.tobytes()).hexdigest()
check('zero new calls/drawings',h['newNativeCalls']==h['newDrawings']==0)
check('three distinct registered sources',len(h['frames'])==len({f['registeredSourceID'] for f in h['frames']})==3)
check('unchanged crop/root/fullstage',h['candidateCanvas']==[51,39] and h['commonCropOrigin']==[38,60] and h['candidatePivot']==[33,33] and h['roundedFullPivot']==[71,93] and h['displayStage']==[120,120] and not h['cropChanged'])
check('registration-only support unapproved',h['geometryScope']=='image-registration-only' and not h['physicalSupportReviewed'] and h['contacts']==[] and h['supportWorld'] is None and not h['runtimeAdmission'])
for f in h['frames']:
 im=Image.open(P/f['png']).convert('RGBA');src=Image.open(P/f['sourcePNG']['file']).convert('RGBA');check(f['id']+' PNG/RGBA source identities',sha(P/f['png'])==f['PNGsha256'] and fid(im)==f['decodedRGBAId'] and fid(src)==f['registeredSourceID'] and sha(P/f['sourcePNG']['file'])==f['sourcePNG']['sha256']);check(f['id']+' binary alpha/no new palette colors',all(v[3] in [0,255] and (v[:3] in [tuple(rgb) for rgb in palette['RGB']] if v[3] else v==(0,0,0,0)) for v in im.getdata()));check(f['id']+' canvas/density/root',list(im.size)==f['canvas']==[51,39] and f['density']==1 and f['pivot']==[33,33] and f['contacts']==[])
 if f['id'] in ['neutral','look']:
  check(f['id']+' exact old selected PNG bytes',sha(P/f['png'])==sha(R/f['exactPreviousSelectedPNG']['upstream']))
  old='neutral' if f['id']=='neutral' else 'look-v1';check(f['id']+' exact old fullstage bytes',sha(P/f['rawFull']['file'])==sha(R/'experiments/common-slot-zero-call-batch-v1/species/yellow_rumped_warbler/raw-full'/f'{old}.png'))
# Independently reproduce closed sampler and fixed-palette mapping; never re-export files.
native=Image.open(P/'sources/blink-registered1024.png').convert('RGBA');raw=Image.open(P/'raw-full/blink.png').convert('RGBA');sampled=[]
for y in range(120):
 for x in range(120):
  sx=math.floor((x+.5)*native.width/h['fullWorldCanvas'][0]);sy=math.floor((y+.5)*native.height/h['fullWorldCanvas'][1]);sampled.append(native.getpixel((sx,sy)) if sx<native.width and sy<native.height else (0,0,0,0))
check('exact closed direct pixel-center sampler',sampled==list(raw.getdata()))
fixed=Image.new('P',(1,1));colors=palette['RGB']+[palette['RGB'][-1]]*(256-63);fixed.putpalette([v for rgb in colors for v in rgb]);q=raw.convert('RGB').quantize(palette=fixed,dither=Image.Dither.NONE).convert('RGB');full=Image.new('RGBA',(120,120));full.putdata([(*q.getpixel((x,y)),255) if raw.getpixel((x,y))[3]>=128 else (0,0,0,0) for y in range(120) for x in range(120)]);blink=Image.open(P/'blink.png').convert('RGBA');reconstructed=Image.new('RGBA',(120,120));reconstructed.paste(blink,(38,60));check('closed fixed palette and crop exact zero discard',reconstructed.tobytes()==full.tobytes());check('closed binary footprint bbox unchanged by palette',list(full.getbbox())==[41,62,87,93])
current=json.loads((P/'sources/current-primary-manifest.json').read_text());closedTicks=[f['durationTicks'] for f in current['clips'][0]['frames']]
for clip in h['clips']:
 if clip['id']=='idle':check('neutral-only idle90',clip['durationTicks']==[90] and clip['frameIds']==['neutral']);continue
 check(clip['id']+' source clip schedule',clip['durationTicks']==(closedTicks if clip['id']=='blink' else [60,18,12]) and clip['frameIds']==['neutral',clip['id'],'neutral'] and clip['tickRate']==30 and not clip['loop'])
 ap=Image.open(P/f"{clip['id']}.apng");check(clip['id']+' APNG3frames one-shot',ap.n_frames==3 and ap.info['loop']==1)
 for i,role in enumerate(clip['frameIds']):
  ap.seek(i);im=Image.open(P/f'{role}.png').convert('RGBA');check(clip['id']+' APNG exact RGBA/delay '+str(i),ap.convert('RGBA').tobytes()==im.tobytes() and abs(ap.info['duration']-clip['durationTicks'][i]*1000/30)<.001)
for row in json.loads((P/'source-provenance.json').read_text())['retainedHistoricalFiles']:check('exact retained '+row['file'],sha(P/row['file'])==row['sha256'])
findings=[]
for f in P.rglob('*'):
 if f.is_file() and f.suffix in ['.json','.md','.txt','.html','.js','.py']:
  text=f.read_text()
  if re.search('libfile_'+r'[0-9a-f]{32}|data:image/[^;]+;base64,|https?://[^\s\"<>]*(?:X-Amz-Signature|X-Goog-Signature|[?&]sig=)',text,re.I):findings.append(str(f.relative_to(P)))
check('public metadata no private handles/signed URLs/embedded captures',not findings)
(P/'verification.json').write_text(json.dumps({'status':'PASS exact image-registration/byte/provenance/clock/privacy checks only','checks':checks,'checkCount':len(checks),'findings':findings,'newNativeCalls':0,'newDrawings':0,'sourceFamilyUsefulness':'UNKNOWN pending independent review','runtimeAdmission':False},indent=2)+'\n');print(json.dumps({'checks':len(checks),'status':'PASS'}))
