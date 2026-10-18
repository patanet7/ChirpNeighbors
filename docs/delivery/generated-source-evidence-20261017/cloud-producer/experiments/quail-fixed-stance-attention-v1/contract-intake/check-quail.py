"""One unchanged runtime subset after exact source construction proof. No source export or repair."""
import pathlib,json,hashlib,subprocess,math,collections,time
from PIL import Image
O=pathlib.Path(__file__).resolve().parent;R=O.parent;BANK=pathlib.Path('/workspace/asset-production');U=pathlib.Path('/workspace/runtime-resting-intake-v5-inspect');RUN=pathlib.Path('/workspace/asset-production/validation/shared-structural-check.mjs');SHARP='/opt/codex/runtimes/codex-primary-runtime/dependencies/node/node_modules/sharp/dist/index.cjs';sha=lambda b:hashlib.sha256(b).hexdigest()
def load(p):return json.loads(p.read_text())
def dump(p,d):p.write_text(json.dumps(d,indent=2)+'\n')
def im(p):return Image.open(p).convert('RGBA')
def rid(i):return 'frame.sha256.'+sha(f'RGBA8;{i.width}x{i.height};'.encode()+i.tobytes())
def member(r,n):
 p=(r/n).resolve();assert p.is_relative_to(r.resolve());return p
def inside(x,y,p):
 yes=False;j=len(p)-1
 for k in range(len(p)):
  xi,yi=p[k];xj,yj=p[j]
  if (yi>y)!=(yj>y) and x<(xj-xi)*(y-yi)/(yj-yi)+xi:yes=not yes
  j=k
 return yes
def holes(i):
 free={(x,y) for y in range(i.height) for x in range(i.width) if not i.getpixel((x,y))[3]};seen={p for p in free if p[0] in [0,i.width-1] or p[1] in [0,i.height-1]};q=collections.deque(seen)
 while q:
  x,y=q.popleft()
  for p in [(x-1,y),(x+1,y),(x,y-1),(x,y+1)]:
   if p in free and p not in seen:seen.add(p);q.append(p)
 return free-seen
def run(cmd,n):
 t=time.monotonic();p=subprocess.run(cmd,cwd=U,capture_output=True,text=True);(O/(n+'.stdout.txt')).write_text(p.stdout);(O/(n+'.stderr.txt')).write_text(p.stderr);return {'command':cmd,'exitCode':p.returncode,'stdout':n+'.stdout.txt','stderr':n+'.stderr.txt','observedWallSeconds':time.monotonic()-t}
assert not (O/'pixel-receipt.json').exists() and not (O/'CONSTRUCTION-RECEIPT.json').exists(),'Retain prior attempt; no automatic repeat'
a=load(O/'authority-receipt.json');c=load(O/'frozen-config.json');assert subprocess.check_output(['git','-C',str(U),'rev-parse','HEAD'],text=True).strip()==a['runtimeCommit'];assert sha(RUN.read_bytes())==a['sharedRunner']['sha256']
for f in a['authorityFiles']:assert sha((U/f['file']).read_bytes())==f['sha256']
for k in ['ledger','stableGO','handoff','enumClarification']:assert sha(member(R,c[k]['file']).read_bytes())==c[k]['sha256'],k
ld=load(member(R,c['ledger']['file']));en=ld.get('files',ld) if isinstance(ld,dict) else ld;pairs=[(x.get('file',x.get('path')),x.get('sha256',x.get('SHA256'))) for x in en] if isinstance(en,list) else list(en.items())
for n,d in pairs:
 if isinstance(d,dict):d=d.get('sha256',d.get('SHA256'))
 assert sha(member(R,n).read_bytes())==d,n
h=load(R/'source-handoff.json');pr=load(R/'PREREGISTRATION.json');recipe=load(R/'construction-recipe.json');proof=load(R/'protection-seam-proof.json');anc=load(R/'ancestry.json');paletteProof=load(R/'palette-proof.json');assert recipe['headReplacementPolygonCellEdges']==pr['headPlumeUpperNeckOwnershipContourCellEdges'];assert h['newNativeCalls']==h['newDrawings']==0;assert h['density']==1 and h['fullWorldCanvas']==[236.30769230769232]*2 and h['displayStage']==[237,237];assert h['candidateCanvas']==[95,100] and h['candidatePivot']==[50,93] and h['commonCropOrigin']==[90,92];assert h['roundedFullPivot']==[140,185] and h['contacts']==[] and h['supportWorld'] is None and h['physicalSupportReviewed'] is False;assert recipe['joint']['rotation']==0 and recipe['joint']['translation']==[0,0] and recipe['joint']['scale']==[1,1];clips={x['id']:x for x in h['clips']};assert clips['idle']['frames']==[{'frameId':'neutral','durationTicks':90}] and clips['idle']['tickRate']==30 and clips['idle']['loop'];assert clips['look']['frames']==[{'frameId':'neutral','durationTicks':60},{'frameId':'look','durationTicks':18},{'frameId':'neutral','durationTicks':12}] and clips['look']['tickRate']==30 and not clips['look']['loop'];assert set(clips)=={'idle','look'}
ancestry=[];native={};raws={};codecs={}
for f in anc['sources']:
 file=member(R,f['file']);up=member(BANK,f['upstreamFile']);assert sha(file.read_bytes())==f['PNGsha256']==sha(up.read_bytes());i=im(file);ancestry.append({'file':f['file'],'SHA256':f['PNGsha256'],'upstream':f['upstreamFile'],'exact':True})
 if f['kind']=='native':assert rid(i)==f['nativeSourceFrameId'];native[f['role']]=i
 elif f['kind']=='raw237':raws[f['role']]=i
 elif f['kind']=='codec':codecs[f['role']]=i
for name,key in [('historicalNativeOriginal','historicalNativeOriginalSHA256'),('exactHistoricalPrompt','exactHistoricalPromptSHA256')]:assert sha(member(R,anc[name]).read_bytes())==anc[key]
for role,src in native.items():
 expected=bytearray();world=h['fullWorldCanvas'][0]
 for y in range(237):
  sy=math.floor((y+.5)*src.height/world)
  for x in range(237):
   sx=math.floor((x+.5)*src.width/world);expected.extend(src.getpixel((sx,sy)) if sx<src.width and sy<src.height else (0,0,0,0))
 assert raws[role].size==(237,237) and raws[role].tobytes()==expected
N=Image.new('RGBA',(237,237));N.paste(codecs['neutral'],(90,92));L=Image.new('RGBA',(237,237));L.paste(codecs['look-v1'],(90,92));mask=Image.open(R/'masks/head-plume-upperneck-ownership.png').convert('L');fullN=im(R/'full-stage/neutral.png');fullL=im(R/'full-stage/look.png');assert fullN.tobytes()==N.tobytes();maskXY=set();changed=cleared=outsideChanges=0;allXY=[(x,y) for y in range(237) for x in range(237)]
for xy in allXY:
 x,y=xy;m=mask.getpixel(xy);assert m in [0,255] and bool(m)==inside(x+.5,y+.5,recipe['headReplacementPolygonCellEdges']);n=N.getpixel(xy);l=L.getpixel(xy);v=fullL.getpixel(xy);assert v==(l if m else n)
 if m:
  maskXY.add(xy);changed+=n!=l;cleared+=bool(n[3] and not l[3])
 else:outsideChanges+=n!=v
assert outsideChanges==0 and changed==proof['actualHeadPixelChanges'] and cleared==proof['oldOpaqueHeadPixelsClearedByDonorTransparent'] and len(maskXY)==proof['ownershipMaskPixels']
mp=load(R/'source-pixel-maps.json');seen=set()
for r in mp['runs']:
 y,x,w=r['y'],r['x'],r['width'];assert 0<=y<237 and 0<=x<x+w<=237
 for xx in range(x,x+w):
  xy=(xx,y);assert xy not in seen;seen.add(xy);assert r['source']==('look-v1' if xy in maskXY else 'neutral')
assert len(seen)==237*237;foot=proof['footProtectionROI'];fx0,fy0,fx1,fy1=foot;footChanges=sum(fullL.getpixel((x,y))!=N.getpixel((x,y)) for y in range(fy0,fy1) for x in range(fx0,fx1));bodyChanges=sum(fullL.getpixel(xy)!=N.getpixel(xy) for xy in allXY if xy[1]>=131);assert footChanges==bodyChanges==0;newHoles=holes(fullL)-holes(N);assert len(newHoles)==proof['newEnclosedTransparentPixelsCount'] and sorted(newHoles)==sorted(map(tuple,proof['newEnclosedTransparentCoordinates']))
expectedColors={tuple(x)+(255,) for x in paletteProof['sharedOpaqueColors']}|{(0,0,0,0)};frames=[];pixels=[];metrics=[]
for f,full in zip(h['frames'],[fullN,fullL]):
 file=member(R,f['png']);assert sha(file.read_bytes())==f['PNGsha256'];i=im(file);assert i.size==(95,100) and rid(i)==f['decodedRGBAId'];assert i.tobytes()==full.crop((90,92,185,192)).tobytes();assert sha(member(R,f['fullStagePNG']).read_bytes())==f['fullStagePNGsha256'];assert all(not full.getpixel((x,y))[3] for x,y in allXY if not(90<=x<185 and 92<=y<192));colors=set(i.getdata());assert colors<=expectedColors and all(p[3] in [0,255] and (p[3] or p==(0,0,0,0)) for p in colors);assert f['pivot']==[50,93] and f['density']==1 and f['contacts']==[];frames.append({'id':f['id'],'png':str(file),'PNGsha256':f['PNGsha256'],'decodedRGBAId':f['decodedRGBAId']});pixels.append({'rgba':list(i.tobytes())});metrics.append({'frame':f['id'],'RGBAColorsIncludingTransparent':len(colors),'opaquePixels':sum(q[3]>0 for q in i.getdata()),'enclosedTransparentPixels':len(holes(i)),'bbox':i.getbbox()})
assert (R/'frames/neutral.png').read_bytes()==(R/'sources/neutral-codec.png').read_bytes()
(O/'producer-index.snapshot.json').write_bytes(member(R,c['ledger']['file']).read_bytes());(O/'producer-STABLE-GO.snapshot.json').write_bytes(member(R,c['stableGO']['file']).read_bytes());dump(O/'CONSTRUCTION-RECEIPT.json',{'state':'PASS exact donor/mask/palette/registration facts; no art/physical approval','frozenProducerInputsExact':len(pairs),'nativeSourceIDsVerified':anc['originalSourceIDs'],'ancestryExact':ancestry,'historicalOriginalSHA256':anc['historicalNativeOriginalSHA256'],'historicalPromptSHA256':anc['exactHistoricalPromptSHA256'],'nativeToRawWholeWorldScalarSampleExact':True,'newNativeCalls':0,'newDrawings':0,'primarySourceIDsAdded':0,'maskPixels':len(maskXY),'sameXYDonorRuns':len(mp['runs']),'mapCoversAllFullStagePixelsExactlyOnce':True,'changedInsideOwnershipMaskPixels':changed,'vacatedOriginalOpaqueHeadPlumeFootprintPixelsByActualDonorTransparency':cleared,'vacatedFootprintIsNotAnatomicalGapCount':True,'outsideOwnershipMaskChangedPixels':outsideChanges,'bodyAtAndBelowY131ChangedPixels':bodyChanges,'footROI':foot,'footROIChangedPixels':footChanges,'footROISemanticallyCertifiedSoles':False,'newEnclosedTransparentPixels':len(newHoles),'hiddenUnderpaintUsed':False,'perPoseFitTransform':False,'noNewColorsOrRequantization':True,'frameColorHoleMetrics':metrics,'cropDiscardedNonzeroRGBA':0,'oldFractionalRoot':h['oldPivotWorld'],'roundedFullRoot':[140,185],'roundingDeltaWorld':[140-h['oldPivotWorld'][0],185-h['oldPivotWorld'][1]],'canvas':[95,100],'cropOrigin':[90,92],'pivot':[50,93],'density':1,'contacts':[],'supportWorld':None,'physicalSupportReviewed':False,'alphaOriginFacts':{'frozenCustomHandoffValue':h['alphaOrigin'],'officialEnumMapping':'upstream-cleanup','mappingEvidence':c['enumClarification'],'originalCustomStringIsNotOfficialSchemaPass':True},'sourceAdmitted':False,'runtimeAdmission':False})
pc={'expectedPackageSHA256':sha((U/'src/lib/server/asset-pipeline/package.ts').read_bytes()),'expectedCanonicalSHA256':sha((U/'src/lib/server/pipeline/canonical.ts').read_bytes()),'canvas':{'width':95,'height':100},'frames':frames,'logicalPixelSize':1,'paletteLimit':64,'contacts':[],'geometryReviewed':False,'supportWorld':None};dump(O/'canonical-pixel-input.json',pc);(O/'raw-candidate-input.json').write_text(json.dumps({'canvas':pc['canvas'],'frames':pixels,'logicalPixelSize':1,'paletteLimit':64},separators=(',',':'))+'\n');commands=[run(['node',str(RUN),'--repo',str(U),'--input',str(O/'canonical-pixel-input.json'),'--receipt',str(O/'pixel-receipt.json'),'--sharp',SHARP],'actual-pixel')];jc={'inputs':[{'label':'raw candidate input','path':str(O/'raw-candidate-input.json')},{'label':'frozen source handoff','path':str(R/'source-handoff.json')},{'label':'construction recipe','path':str(R/'construction-recipe.json')}],'output':str(O/'json-budget-receipt.json')};dump(O/'json-budget-config.json',jc);commands.append(run(['node',str(O/'actual-json-budget.mjs'),str(O/'json-budget-config.json')],'actual-json'));dump(O/'commands.json',commands)
for n,d in pairs:
 if isinstance(d,dict):d=d.get('sha256',d.get('SHA256'))
 assert sha(member(R,n).read_bytes())==d,n
assert sha(member(R,c['enumClarification']['file']).read_bytes())==c['enumClarification']['sha256'];dump(O/'FINAL-SOURCE-GUARD.json',{'status':'PASS all44 producer inputs and additive enum clarification exact after check','producerInputCount':len(pairs),'enumClarification':c['enumClarification'],'sourceFilesModified':0});print(json.dumps({'actualRuns':1,'JSONRuns':1,'commandsExitCodes':[x['exitCode'] for x in commands],'producerInputsExact':len(pairs),'sourceAdmitted':False}))
