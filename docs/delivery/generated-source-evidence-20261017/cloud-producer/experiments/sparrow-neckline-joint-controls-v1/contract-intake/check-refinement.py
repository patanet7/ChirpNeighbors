"""Read-only construction proof and at most one actual pixel/JSON run for each of two frozen sets."""
import pathlib,json,hashlib,math,collections,subprocess,time,sys
from PIL import Image
O=pathlib.Path(__file__).resolve().parent;R=O.parent;EX=R.parent;UI=pathlib.Path('/workspace/runtime-resting-intake-v5-inspect');RUN=pathlib.Path('/workspace/asset-production/validation/shared-structural-check.mjs');SHARP='/opt/codex/runtimes/codex-primary-runtime/dependencies/node/node_modules/sharp/dist/index.cjs';sha=lambda b:hashlib.sha256(b).hexdigest()
def load(p):return json.loads(p.read_text())
def dump(p,d):p.write_text(json.dumps(d,indent=2)+'\n')
def im(p):return Image.open(p).convert('RGBA')
def rid(i):return 'frame.sha256.'+sha(f'RGBA8;{i.width}x{i.height};'.encode()+i.tobytes())
def member(r,n):
 p=(r/n).resolve();assert p.is_relative_to(r.resolve());return p
def inside(x,y,p):
 yes=False;j=len(p)-1
 for i in range(len(p)):
  xi,yi=p[i];xj,yj=p[j]
  if (yi>y)!=(yj>y) and x<(xj-xi)*(y-yi)/(yj-yi)+xi:yes=not yes
  j=i
 return yes
def holes(i):
 free={(x,y) for y in range(i.height) for x in range(i.width) if not i.getpixel((x,y))[3]};border={p for p in free if p[0] in [0,i.width-1] or p[1] in [0,i.height-1]};seen=set(border);q=collections.deque(border)
 while q:
  x,y=q.popleft()
  for p in [(x-1,y),(x+1,y),(x,y-1),(x,y+1)]:
   if p in free and p not in seen:seen.add(p);q.append(p)
 return sorted(free-seen)
def run(cmd,label,out):
 t=time.monotonic();r=subprocess.run(cmd,cwd=UI,capture_output=True,text=True);(out/(label+'.stdout.txt')).write_text(r.stdout);(out/(label+'.stderr.txt')).write_text(r.stderr);return {'command':cmd,'exitCode':r.returncode,'stdout':label+'.stdout.txt','stderr':label+'.stderr.txt','observedWallSeconds':time.monotonic()-t}
c=load(pathlib.Path(sys.argv[1]));assert not (O/'CONSTRUCTION-RECEIPT.json').exists(),'Retain previous result, no automatic retry';a=load(O/'authority-receipt.json');assert subprocess.check_output(['git','-C',str(UI),'rev-parse','HEAD'],text=True).strip()==a['runtimeCommit'];assert sha(RUN.read_bytes())==a['sharedRunner']['sha256']
for f in a['authorityFiles']:assert sha((UI/f['file']).read_bytes())==f['sha256']
for k in ['ledger','stableGO','mainHandoff','controlHandoff']:assert sha(member(R,c[k]['file']).read_bytes())==c[k]['sha256'],k
ld=load(member(R,c['ledger']['file']));entries=ld.get('files',ld) if isinstance(ld,dict) else ld;pairs=[(x.get('file',x.get('path')),x.get('sha256',x.get('SHA256'))) for x in entries] if isinstance(entries,list) else list(entries.items())
for n,h in pairs:
 if isinstance(h,dict):h=h.get('sha256',h.get('SHA256'))
 assert sha(member(R,n).read_bytes())==h,n
pr=load(R/'PREREGISTRATION.json');recipe=load(R/'construction-recipe.json');p=load(R/'protection-seam-occlusion-proof.json');maps=load(R/'source-pixel-maps.json')['maps'];assert recipe['chosenContourCellEdges']==pr['newContourProposedBeforeExport'];assert recipe['anglesDegreesClockwise']==[-6,0,6]
ancestry=[]
for f in load(R/'ancestry.json')['retainedSourceFiles']:
 pp=member(R,f['file']);up=member(EX,f['upstream']);assert sha(pp.read_bytes())==f['SHA256']==sha(up.read_bytes());ancestry.append({'file':f['file'],'upstream':f['upstream'],'SHA256':f['SHA256'],'exact':True})
ns=im(R/'source-provenance/reference-awake-source1024.png');ls=im(R/'source-provenance/original.png');ids=load(R/'ancestry.json')['sourceFrameIDs'];assert [rid(ns),rid(ls)]==ids
N=im(R/'sources/neutral-stage.png');L=im(R/'sources/authored-look-stage.png');body=im(R/'layers/canonical-body-wing-tail-legs-feet.png');NH=im(R/'layers/neutral-head-upper-neck.png');LH=im(R/'layers/authored-look-head-upper-neck.png');mask=Image.open(R/'masks/revised-head-upper-neck.png').convert('L');strict=Image.open(R/'masks/strict-protected-render-region.png').convert('L');core=Image.open(R/'masks/core-body-feet-y74plus.png').convert('L');bodyOwn=Image.open(R/'masks/canonical-body-layer-ownership.png').convert('L');allXY=[(x,y) for y in range(124) for x in range(124)];maskXY=set();fulls={k:im(R/('full-stage/'+k+'.png')) for k in ['neutral','look','roll-minus6','roll-plus6']}
for x,y in allXY:
 m=mask.getpixel((x,y));assert m in [0,255] and bool(m)==inside(x+.5,y+.5,recipe['chosenContourCellEdges']);assert bodyOwn.getpixel((x,y))==255-m
 if m:maskXY.add((x,y))
 n=N.getpixel((x,y));l=L.getpixel((x,y));assert body.getpixel((x,y))==(n if not m else (0,0,0,0));assert NH.getpixel((x,y))==(n if m else (0,0,0,0));assert LH.getpixel((x,y))==(l if m else (0,0,0,0));assert fulls['neutral'].getpixel((x,y))==n;assert fulls['look'].getpixel((x,y))==(l if m else n);assert core.getpixel((x,y))==(255 if y>=74 else 0)
assert len(maps['look'])==len(maskXY)
for q in maps['look']:
 xy=tuple(q['outputXY']);assert xy in maskXY and q['sourceXY']==q['outputXY'] and tuple(q['RGBA'])==L.getpixel(xy)
angleProof=[];allOwners=set(maskXY)
for t in recipe['rotationTransforms']:
 key=t['key'];angle=t['angleDegreesClockwise'];rad=math.radians(angle);co,si=math.cos(rad),math.sin(rad);forward=[co,-si,si,co];inverse=[co,si,-si,co];assert all(abs(x-y)<1e-12 for x,y in zip(t['forwardMatrix'],forward));assert all(abs(x-y)<1e-12 for x,y in zip(t['inverseMatrix'],inverse));assert t['pivotWorld']==[74.,68.] and t['translation']==[0,0] and t['scale']==[1,1]
 head=im(R/('control-layers/'+key+'-head.png'));own=Image.open(R/('masks/'+key+'-rotated-ownership.png')).convert('L');owned=set();expectedMaps={};uncovered=[];occlusions=[]
 target=fulls['neutral'] if key=='roll-zero' else fulls[key]
 for x,y in allXY:
  dx,dy=x+.5-74,y+.5-68;sx=math.floor(74+co*dx+si*dy);sy=math.floor(68-si*dx+co*dy);inbounds=0<=sx<124 and 0<=sy<124;ownedHere=inbounds and bool(mask.getpixel((sx,sy)));expected=NH.getpixel((sx,sy)) if inbounds else (0,0,0,0);assert head.getpixel((x,y))==expected;assert own.getpixel((x,y))==(255 if ownedHere else 0)
  if ownedHere:owned.add((x,y));expectedMaps[(x,y)]=((sx,sy),expected)
  expectedFull=expected if expected[3] else body.getpixel((x,y));assert target.getpixel((x,y))==expectedFull
  if (x,y) in maskXY and N.getpixel((x,y))[3] and not expectedFull[3]:uncovered.append((x,y))
  if (x,y) not in maskXY and expected[3] and body.getpixel((x,y))[3]:occlusions.append((x,y))
 assert sorted(uncovered)==sorted(map(tuple,t['uncoveredOriginalVisibleCutoutPixels']));assert sorted(occlusions)==sorted(map(tuple,t['opaqueHeadOccludesBodyOutsideOriginalCutMask']));mapped={}
 for q in maps[key]:
  xy=tuple(q['outputXY']);assert xy in expectedMaps and xy not in mapped;assert tuple(q['sourceXY'])==expectedMaps[xy][0] and tuple(q['RGBA'])==expectedMaps[xy][1];mapped[xy]=True
 assert set(mapped)==owned;allOwners.update(owned);angleProof.append({'key':key,'degreesClockwise':angle,'forwardInverseMatrixTrigonometryExact':True,'inverseNNAndDonorRGBAExact':True,'sameScaleAndNoTranslation':True,'pivotWorld':[74,68],'mappedOwnershipPixels':len(owned),'uncoveredVisibleCutoutPixels':len(uncovered),'headOccludesBodyOutsideOriginalMaskPixels':len(occlusions),'producerDisposition':t['mechanicalDisposition'],'actualPhysicalJointCalibrated':False})
for xy in allXY:assert strict.getpixel(xy)==(0 if xy in allOwners else 255)
per=[]
for name,i in fulls.items():
 strictChanges=sum(i.getpixel(xy)!=N.getpixel(xy) for xy in allXY if strict.getpixel(xy));coreChanges=sum(i.getpixel(xy)!=N.getpixel(xy) for xy in allXY if core.getpixel(xy));assert strictChanges==coreChanges==0;holeXY=holes(i);assert holeXY==sorted(map(tuple,p['perFrameDiagnostics'][name]['enclosedTransparentPixels']));per.append({'frame':name,'strictProtectedChangedPixels':strictChanges,'coreBodyFeetY74PlusChangedPixels':coreChanges,'enclosedTransparentHolePixels':len(holeXY),'RGBAColorsIncludingTransparent':len(set(i.getdata())),'opaquePixels':sum(i.getpixel(xy)[3]>0 for xy in allXY),'semanticallyCertifiedSoles':False})
palette=set(N.getdata())|set(L.getdata());assert len(palette)<=64
(O/'producer-index.snapshot.json').write_bytes(member(R,c['ledger']['file']).read_bytes());(O/'producer-STABLE-GO.snapshot.json').write_bytes(member(R,c['stableGO']['file']).read_bytes())
dump(O/'CONSTRUCTION-RECEIPT.json',{'state':'PASS exact construction/sampling/protection facts; artistic and mechanical holds remain separate','pinnedRuntimeCommit':a['runtimeCommit'],'runtimeVersionClaim':'Pinned observed snapshot, not latest','producerLedger':c['ledger'],'producerFrozenFilesExact':len(pairs),'nativeSourceIDs':ids,'nativeIDsVerified':True,'ancestryBytesExact':ancestry,'newNativeCalls':0,'newDrawings':0,'newPrimaryIDs':0,'chosenMaskPixelCount':len(maskXY),'sameXYMainDonorMapExact':True,'layersExact':True,'finiteRotationChecks':angleProof,'strictProtectedRegion':'Complement of chosen mask plus all finite rotated ownership masks; not the entire original body silhouette','perFrame':per,'paletteIsExactCanonicalAColorSubset':all(set(i.getdata())<=palette for i in fulls.values()),'interpolatedNewColors':False,'sourcePixelEditingPerformedByTechnicalWorkstream':False,'controlsInventedMissingNeckPixels':False,'controlMechanicalAcceptance':False,'physicalSupportReviewed':False,'contacts':[],'supportWorld':None,'sourceAdmitted':False,'runtimeAdmission':False})
for label,hkey,expectedIDs,expectedTicks in [('main','mainHandoff',['neutral','look'],[60,18,12]),('controls','controlHandoff',['neutral','roll-minus6','roll-plus6'],[45,12,6,12,15])]:
 out=O/label;assert not out.exists(),'Do not retry an existing actual check';out.mkdir();h=load(member(R,c[hkey]['file']));assert [f['id'] for f in h['frames']]==expectedIDs;assert h['nativeCalls']==h['newDrawings']==h['primarySourceIDsAdded']==0;assert h['fullWorldCanvas']==[123.42857142857143]*2 and h['displayStage']==[124,124] and h['density']==1;assert h['contacts']==[] and h['supportWorld'] is None and h['physicalSupportReviewed'] is False;assert [h['commonCropOrigin'][i]+h['candidatePivot'][i] for i in [0,1]]==[73,96];clip=h['clips'][0];assert clip['tickRate']==30 and [q['durationTicks'] for q in clip['frames']]==expectedTicks and sum(expectedTicks)==90 and clip['loop'] is False
 W,H=h['candidateCanvas'];ox,oy=h['commonCropOrigin'];pixelFrames=[];raw=[]
 for f in h['frames']:
  file=member(R,f['png']);assert sha(file.read_bytes())==f['PNGsha256'];i=im(file);assert i.size==(W,H) and rid(i)==f['decodedRGBAId'];full=fulls[f['id']];assert i.tobytes()==full.crop((ox,oy,ox+W,oy+H)).tobytes();assert sha(member(R,f['fullStagePNG']).read_bytes())==f['fullStagePNGsha256'];assert im(member(R,f['fullStagePNG'])).tobytes()==full.tobytes();assert all(not full.getpixel((x,y))[3] for x,y in allXY if not (ox<=x<ox+W and oy<=y<oy+H));assert f['pivot']==h['candidatePivot'] and f['density']==1 and f['contacts']==[];assert all(p[3] in [0,255] and (p[3] or p==(0,0,0,0)) for p in set(i.getdata()));pixelFrames.append({'id':f['id'],'png':str(file),'PNGsha256':f['PNGsha256'],'decodedRGBAId':f['decodedRGBAId']});raw.append({'rgba':list(i.tobytes())})
 pc={'expectedPackageSHA256':sha((UI/'src/lib/server/asset-pipeline/package.ts').read_bytes()),'expectedCanonicalSHA256':sha((UI/'src/lib/server/pipeline/canonical.ts').read_bytes()),'canvas':{'width':W,'height':H},'frames':pixelFrames,'logicalPixelSize':1,'paletteLimit':64,'contacts':[],'geometryReviewed':False,'supportWorld':None};dump(out/'canonical-pixel-input.json',pc);(out/'raw-candidate-input.json').write_text(json.dumps({'canvas':pc['canvas'],'frames':raw,'logicalPixelSize':1,'paletteLimit':64},separators=(',',':'))+'\n');commands=[run(['node',str(RUN),'--repo',str(UI),'--input',str(out/'canonical-pixel-input.json'),'--receipt',str(out/'pixel-receipt.json'),'--sharp',SHARP],'actual-pixel',out)];jc={'inputs':[{'label':'raw candidate input','path':str(out/'raw-candidate-input.json')},{'label':'frozen '+label+' handoff','path':str(member(R,c[hkey]['file']))},{'label':'construction recipe','path':str(R/'construction-recipe.json')}],'output':str(out/'json-budget-receipt.json')};dump(out/'json-budget-config.json',jc);commands.append(run(['node',str(O/'actual-json-budget.mjs'),str(out/'json-budget-config.json')],'actual-json',out));dump(out/'commands.json',commands);dump(out/'RESULT.json',{'state':'COMPLETED actual pinned pixel and JSON subset; preserve any actual errors','set':label,'uniqueDecodedFrames':len(raw),'decodedArea':W*H*len(raw),'authoredDurationTicks30':90,'contacts':[],'supportWorld':None,'sourceAdmitted':False,'runtimeAdmission':False,'commonInput5':'NOT APPLICABLE; no complete neutral/blink/look family created','commands':commands})
for n,h in pairs:
 if isinstance(h,dict):h=h.get('sha256',h.get('SHA256'))
 assert sha(member(R,n).read_bytes())==h,n
dump(O/'FINAL-SOURCE-GUARD.json',{'status':'PASS all producer frozen files exact after both actual checks','filesExact':len(pairs),'ledger':c['ledger'],'nativeCallsByTechnicalWorkstream':0,'producerFilesChanged':0});print(json.dumps({'completedSets':['main','controls'],'pixelRuns':2,'JSONRuns':2,'producerFilesExact':len(pairs),'sourceAdmitted':False}))
