from pathlib import Path
from PIL import Image
import json,hashlib,re
P=Path(__file__).resolve().parent;O=P.parent/'american_crow';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();load=lambda n:json.loads((P/n).read_text());h=load('source-handoff.json');old=json.loads((O/'source-handoff.json').read_text());primary=load('PRIMARY-SOURCE-MANIFEST.json');checks=[]
def check(n,v):checks.append({'check':n,'pass':bool(v)});assert v,n
def fid(im):return 'frame.sha256.'+hashlib.sha256(f'RGBA8;{im.width}x{im.height};'.encode()+im.tobytes()).hexdigest()
check('zero native calls/new drawings and no new primary source entries',primary['nativeCalls']==primary['newDrawings']==h['newNativeCalls']==h['newDrawings']==0 and primary['frames']==[] and len(primary['reusedFrames'])==3)
check('same original source IDs and clocks',[f['sourceFrameId'] for f in h['frames']]==[f['sourceFrameId'] for f in old['frames']] and h['clips']==old['clips'])
check('same exact global geometry/root/crop/density',all(h[k]==old[k] for k in ['fullWorldCanvas','displayStage','candidateCanvas','density','oldPivotWorld','roundedFullPivot','commonCropOrigin','candidatePivot','crop']))
check('source ancestry references original generation once',h['originalPrimaryManifest']['sha256']==sha(O/'PRIMARY-SOURCE-MANIFEST.json') and h['ancestrySHA256']==sha(O/'source-lineage.json'))
for i,f in enumerate(h['frames']):
 before=old['frames'][i];raw=P/f['rawPNG'];src=P/f['sourcePNG'];out=P/f['png'];im=Image.open(out).convert('RGBA');original=Image.open(O/before['png']).convert('RGBA');check(f['id']+' raw-full PNG exact',sha(raw)==sha(O/before['rawPNG']));check(f['id']+' native source PNG/ID exact',sha(src)==sha(O/before['sourcePNG'])==f['sourcePNGsha256'] and fid(Image.open(src).convert('RGBA'))==f['sourceFrameId']);check(f['id']+' output PNG/RGBA identities',sha(out)==f['PNGsha256'] and fid(im)==f['decodedRGBAId']);check(f['id']+' alpha mask and canvas exact',im.size==original.size and im.getchannel('A').tobytes()==original.getchannel('A').tobytes());check(f['id']+' reused/registration/contact scope',not f['newDrawing'] and f['registration']==before['registration'] and f['pivot']==before['pivot'] and f['contacts']==[])
 rect=f['atlasRect'];atlas=Image.open(P/'atlas.png').convert('RGBA');check(f['id']+' atlas exact',atlas.crop((rect['x'],rect['y'],rect['x']+rect['width'],rect['y']+rect['height'])).tobytes()==im.tobytes())
colors={v[:3] for f in h['frames'] for v in Image.open(P/f['png']).convert('RGBA').getdata() if v[3]};check('one31opaque+transparent common palette',len(colors)==31 and len(colors)<=31 and load('fixed-palette.json')['actualOpaqueColors']==31)
check('binary alpha/transparent RGBA0',all(v[3] in [0,255] and (v[3]!=0 or v==(0,0,0,0)) for f in h['frames'] for v in Image.open(P/f['png']).convert('RGBA').getdata()))
for clip in h['clips'][1:]:
 ap=Image.open(P/f"{clip['id']}.apng");check(clip['id']+' APNG3 one-shot',ap.n_frames==3 and ap.info['loop']==1)
 for i,step in enumerate(clip['frames']):
  ap.seek(i);check(clip['id']+' APNG exact RGBA/delay '+str(i),ap.convert('RGBA').tobytes()==Image.open(P/'frames'/f"{step['frameId']}.png").convert('RGBA').tobytes() and abs(ap.info['duration']-step['durationTicks']*1000/30)<.001)
check('prior actual original63 failure retained','Normalized rectangle budget exceeded' in (P/'prior-failure/actual-pixel-subset.stderr.txt').read_text())
check('source geometry only/support unapproved',h['contacts']==[] and h['supportWorld'] is None and not h['physicalSupportReviewed'] and h['geometryScope']=='image-registration-only' and not h['runtimeAdmission'])
guards={}
for name,base in [('originalCrow',O),('originalAggregate',P.parent)]:
 ledger=json.loads((base/'review-target-hashes.json').read_text());g={'count':len(ledger['files']),'allMatch':all(sha(base/r['path'])==r['SHA256'] and (base/r['path']).stat().st_size==r['bytes'] for r in ledger['files']),'ledgerSHA256':sha(base/'review-target-hashes.json'),'GOsha256':sha(base/'STABLE-GO.json')};guards[name]=g;check(name+' frozen inputs unchanged',g==load('preregistered-original-freeze-guard.json')[name] and g['allMatch'])
findings=[]
for f in P.rglob('*'):
 if f.is_file() and f.suffix in ['.json','.txt','.md','.py','.js','.html']:
  if re.search('libfile_'+r'[0-9a-f]{32}|data:image/[^;]+;base64,|https?://[^\s\"<>]*(?:X-Amz-Signature|X-Goog-Signature|[?&]sig=)',f.read_text(),re.I):findings.append(str(f.relative_to(P)))
check('public metadata no private handles/signed URLs/embedded captures',not findings)
(P/'original-freeze-guard-after.json').write_text(json.dumps(guards,indent=2)+'\n');(P/'verification.json').write_text(json.dumps({'status':'PASS technical derivative byte/alpha/geometry/clock/privacy proof only','checks':checks,'checkCount':len(checks),'nativeCalls':0,'newDrawings':0,'reusedDrawings':3,'original45CrowAnd102AggregateUnchanged':True,'findings':findings,'actualCurrentPixelAndInput5Checks':'Corvid-owned; NOT_RUN by producer','sourceUsefulness':'UNKNOWN pending independent palette review','runtimeAdmission':False},indent=2)+'\n');print(json.dumps({'checks':len(checks),'status':'PASS','nativeCalls':0,'newDrawings':0,'original45And102Unchanged':True}))
