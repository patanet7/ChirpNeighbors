from pathlib import Path
from PIL import Image,ImageDraw
import hashlib,json
R=Path(__file__).parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
for name in ['understory-wind-v1','rain-layer-v1','rain-continuity-v2']:
 p=R/'batches'/name;im=Image.open(p/'original.png').convert('RGBA');plant=name.startswith('understory');size=768 if plant else 512
 roots=[[245,474],[246,474],[255,474],[255,475],[258,475],[249,476]]
 times=[220,180,240,180,220,240] if plant else [90]*6
 phases=['neutral','right-lean','right-bow','return','left-lag','settle'] if plant else ['rain-phase-'+str(i+1) for i in range(6)]
 frames=[];comps=[];entries=[];(p/'frames-source').mkdir(exist_ok=True);(p/'frames-review384').mkdir(exist_ok=True)
 for i in range(6):
  rect=[i%3*512,i//3*512,i%3*512+512,i//3*512+512];cut=im.crop(rect);f=Image.new('RGBA',(size,size));dx=384-roots[i][0] if plant else 0;dy=640-roots[i][1] if plant else 0;f.paste(cut,(dx,dy));file=p/'frames-source'/f'{i:02d}.png';f.save(file);frames.append(f)
  exact=f.crop((dx,dy,dx+512,dy+512)).tobytes()==cut.tobytes();assert exact
  rev=f.resize((384,384),Image.Resampling.NEAREST);rev.save(p/'frames-review384'/f'{i:02d}.png');bg=Image.new('RGBA',(384,384),(239,235,213,255) if plant else (40,67,51,255));bg.alpha_composite(rev);comps.append(bg.convert('RGB'))
  entries.append({'index':i,'phase':phases[i],'durationMs':times[i],'file':str(file.relative_to(p)),'sha256':sha(file),'rawPixelSha256':hashlib.sha256(f.tobytes()).hexdigest(),'sourceRectangle':rect,'translation':[dx,dy],'sourceScale':1,'root':[384,640] if plant else None,'rootAccepted':False,'alphaBBox':f.getchannel('A').getbbox(),'exactCropRoundTrip':exact})
 frames[0].save(p/'preview.apng',save_all=True,append_images=frames[1:],duration=times,loop=0,disposal=0,blend=0);comps[0].save(p/'preview.gif',save_all=True,append_images=comps[1:],duration=times,loop=0,disposal=2)
 atlas=Image.new('RGBA',(size*3,size*2));sheet=Image.new('RGB',(1152,820),(239,235,213) if plant else (40,67,51));draw=ImageDraw.Draw(sheet)
 for i,f in enumerate(frames):atlas.paste(f,(i%3*size,i//3*size))
 for i,f in enumerate(comps):x=i%3*384;y=i//3*410;sheet.paste(f,(x,y));draw.text((x+10,y+389),f'{i+1} {phases[i]} | {times[i]}ms',fill=(30,40,35) if plant else (220,235,225))
 atlas.save(p/'atlas.png');sheet.save(p/'contact-sheet.png')
 issues=['New unconditioned style candidate; existing canonical plant source inaccessible.','Frond geometry, root cluster and flower spacing drift; translated root annotation does not guarantee rooted motion.','Illustrative mixed clump with no verified botanical taxon or regional/native claim.','Six poses have stepped motion and unreviewed loop seam.','Combined foreground clump; stems, leaves and flowers are not separately editable structural layers.'] if plant else ['Sparse pixel streaks are generated; six patterns show temporal change but coherent fall tracking and loop seam are unverified.','Not a mathematically seamless tile; edge discontinuities and flicker may need revision.','Native translucent RGBA is preserved; not compatible with old binary-alpha bird manifest.','This is a separate rain overlay; it provides no container filling, pooling, snow accumulation, water physics or live-weather connection.']
 m={'schemaVersion':1,'kind':'private-layer-animation-candidate','batch':name,'semanticRole':'foreground-foliage' if plant else 'weather-rain-overlay','state':'reviewed','accepted':False,'staged':False,'integrated':False,'canvas':[size,size],'root':[384,640] if plant else None,'worldScale':None,'frames':entries,'clips':[{'name':'wind-sway' if plant else 'rain','loop':True,'frameIndices':list(range(6)),'durationMs':times}],'reviewIssues':issues+(['Requested fixed-displacement continuity failed: mean alpha-mask IoU0.051; loop edge0.0. Needs revision; no temporal improvement accepted.'] if name=='rain-continuity-v2' else []),'provenance':{'tool':'OpenAI image_gen.imagegen','model':None,'seed':None,'promptFile':'prompt.txt','original':'original.png','originalSha256':sha(p/'original.png'),'references':[]},'processing':{'alpha':'unchanged','source':'exact rectangular extraction plus integer translation only','reviewScale':384/size,'reviewResampling':'nearest neighbor identical scale for every frame','proceduralNewBodyFrames':0},'validation':{'uniqueFrames':len(set(e['rawPixelSha256'] for e in entries)),'exactCropRoundTrips':all(e['exactCropRoundTrip'] for e in entries),'APNGframes':Image.open(p/'preview.apng').n_frames,'GIFframes':Image.open(p/'preview.gif').n_frames,'RGBA':all(f.mode=='RGBA' for f in frames)},'runtimeCompatibility':'Scene-layer handoff only; Mac loader and staged route not verified. Not an importable October12 bird manifest.'}
 assert m['validation']['uniqueFrames']==6 and m['validation']['APNGframes']==6 and m['validation']['GIFframes']==6
 (p/'manifest.json').write_text(json.dumps(m,indent=2)+'\n');(p/'review.md').write_text('# '+name+' — reviewed with issues\n\n'+'\n'.join('- '+x for x in issues)+'\n')
 print(name,json.dumps(m['validation']))
