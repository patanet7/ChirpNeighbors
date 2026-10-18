"""Independent construction facts plus one unchanged runtime subset; does not render source outputs."""
import pathlib,json,hashlib,subprocess,collections,time,sys
from PIL import Image
O=pathlib.Path(__file__).resolve().parent;E=O.parent;U=pathlib.Path('/workspace/runtime-resting-intake-v5-inspect');RUN=pathlib.Path('/workspace/asset-production/validation/shared-structural-check.mjs');SHARP='/opt/codex/runtimes/codex-primary-runtime/dependencies/node/node_modules/sharp/dist/index.cjs';sha=lambda b:hashlib.sha256(b).hexdigest()
def load(p):return json.loads(p.read_text())
def dump(p,d):p.write_text(json.dumps(d,indent=2)+'\n')
def image(p):return Image.open(p).convert('RGBA')
def rid(im):return 'frame.sha256.'+sha(f'RGBA8;{im.width}x{im.height};'.encode()+im.tobytes())
def member(r,n):
 p=(r/n).resolve();assert p.is_relative_to(r.resolve());return p
def inside(x,y,p):
 yes=False;j=len(p)-1
 for i in range(len(p)):
  xi,yi=p[i];xj,yj=p[j]
  if (yi>y)!=(yj>y) and x<(xj-xi)*(y-yi)/(yj-yi)+xi:yes=not yes
  j=i
 return yes
def holes(im):
 free={(x,y) for y in range(im.height) for x in range(im.width) if im.getpixel((x,y))[3]==0};edge={p for p in free if p[0] in [0,im.width-1] or p[1] in [0,im.height-1]};q=collections.deque(edge);seen=set(edge)
 while q:
  x,y=q.popleft()
  for p in [(x-1,y),(x+1,y),(x,y-1),(x,y+1)]:
   if p in free and p not in seen:seen.add(p);q.append(p)
 return sorted(free-seen)
def run(cmd,n,r):
 t=time.monotonic();s=subprocess.run(cmd,cwd=U,capture_output=True,text=True);(r/(n+'.stdout.txt')).write_text(s.stdout);(r/(n+'.stderr.txt')).write_text(s.stderr);return {'command':cmd,'exitCode':s.returncode,'stdout':n+'.stdout.txt','stderr':n+'.stderr.txt','observedWallSeconds':time.monotonic()-t}
c=load(pathlib.Path(sys.argv[1]));root=pathlib.Path(c['root']);assert root==E/'arm-d-hybrid-construction';r=O/'arm-d';assert not r.exists();r.mkdir()
try:
 a=load(O/'authority-receipt.json');assert subprocess.check_output(['git','-C',str(U),'rev-parse','HEAD'],text=True).strip()==a['runtimeCommit'];assert sha(RUN.read_bytes())==a['sharedRunner']['sha256']
 for f in a['authorityFiles']:assert sha((U/f['file']).read_bytes())==f['sha256']
 for k in ['handoff','ledger','stableGO']:assert sha(member(root,c[k]['file']).read_bytes())==c[k]['sha256']
 ld=load(member(root,c['ledger']['file']));pairs=ld.get('files',ld) if isinstance(ld,dict) else ld;pairs=[(x.get('file',x.get('path')),x.get('sha256',x.get('SHA256'))) for x in pairs] if isinstance(pairs,list) else list(pairs.items())
 for n,d in pairs:
  if isinstance(d,dict):d=d.get('sha256',d.get('SHA256'))
  assert sha(member(root,n).read_bytes())==d,n
 h=load(member(root,c['handoff']['file']));recipe=load(root/'construction-recipe.json');proof=load(root/'protected-body-and-seam-proof.json');mp=load(root/'source-pixel-map.json');assert h['newNativeCalls']==h['newDrawings']==0;assert h['density']==1 and h['contacts']==[] and h['supportWorld'] is None;assert h['physicalSupportReviewed'] is False and h['geometryScope']=='image-registration-only';assert h['candidateCanvas']==[61,45] and h['candidatePivot']==[43,42] and h['commonCropOrigin']==[30,54] and h['roundedFullPivot']==[73,96]
 assert len(h['clips'])==1 and h['clips'][0]['id']=='look';clip=h['clips'][0];assert clip['tickRate']==30 and clip['loop'] is False;assert clip['frames']==[{'frameId':'neutral','durationTicks':60},{'frameId':'look','durationTicks':18},{'frameId':'neutral','durationTicks':12}]
 anc=load(root/'ancestry.json');ancestry=[]
 for f in anc['inputFiles']:
  p=member(root,f['file']);up=member(E,f['upstream']);assert sha(p.read_bytes())==f['SHA256']==sha(up.read_bytes());ancestry.append({'file':f['file'],'upstream':f['upstream'],'SHA256':f['SHA256'],'exact':True})
 native=[]
 for file,id in [('source-provenance/reference-awake-source1024.png',anc['sourceFrameIDs'][0]),('source-provenance/original.png',anc['sourceFrameIDs'][1])]:
  im=image(root/file);assert rid(im)==id;native.append({'file':file,'sourceFrameID':id,'exactNativeIdentity':True})
 n=image(root/'sources/stage-neutral.png');l=image(root/'sources/stage-look.png');assert n.size==l.size==(124,124);mask=Image.open(root/'masks/head-upper-neck-replacement.png').convert('L');protected=Image.open(root/'masks/canonical-body-protected.png').convert('L');assert mask.size==protected.size==(124,124)
 body=image(root/'layers/canonical-body-wing-tail-legs-feet.png');nl=image(root/'layers/neutral-head-upper-neck.png');ll=image(root/'layers/look-head-upper-neck.png');fullN=image(root/'full-stage/neutral.png');fullL=image(root/'full-stage/look.png');poly=recipe['headReplacementPolygonCellEdges'];maskXY=set();changed=cleared=added=protectedVisible=0
 for y in range(124):
  for x in range(124):
   m=mask.getpixel((x,y));assert m in [0,255];assert bool(m)==inside(x+.5,y+.5,poly);assert protected.getpixel((x,y))==255-m
   if m:maskXY.add((x,y))
   pn=n.getpixel((x,y));pl=l.getpixel((x,y));assert body.getpixel((x,y))==(pn if not m else (0,0,0,0));assert nl.getpixel((x,y))==(pn if m else (0,0,0,0));assert ll.getpixel((x,y))==(pl if m else (0,0,0,0));assert fullN.getpixel((x,y))==pn;assert fullL.getpixel((x,y))==(pl if m else pn)
   if not m and pn[3]:protectedVisible+=1
   if m and pn!=pl:changed+=1
   if m and pn[3] and not pl[3]:cleared+=1
   if m and not pn[3] and pl[3]:added+=1
 assert protectedVisible==proof['protectedVisibleCanonicalPixels'];assert 124*124-len(maskXY)==proof['protectedPixelCount'];assert changed==proof['headChangedPixels'];assert len(mp['pixels'])==len(maskXY)
 mapped=set()
 for p in mp['pixels']:
  xy=tuple(p['outputXY']);assert xy in maskXY and xy not in mapped;assert p['sourceRole']=='authored-look' and p['sourceStageXY']==p['outputXY'];assert tuple(p['RGBA'])==l.getpixel(xy);mapped.add(xy)
 assert mapped==maskXY
 assert holes(fullN)==sorted(map(tuple,proof['enclosedTransparentHolePixels']['neutral']));assert holes(fullL)==sorted(map(tuple,proof['enclosedTransparentHolePixels']['look']))
 finals=[];pixels=[];colors=set()
 for f,full in zip(h['frames'],[fullN,fullL]):
  p=member(root,f['png']);assert sha(p.read_bytes())==f['PNGsha256'];im=image(p);assert im.tobytes()==full.crop((30,54,91,99)).tobytes();assert rid(im)==f['decodedRGBAId'];assert f['density']==1 and f['pivot']==[43,42] and f['contacts']==[];assert sha(member(root,f['fullStagePNG']).read_bytes())==f['fullStagePNGsha256'];assert full.tobytes()==image(member(root,f['fullStagePNG'])).tobytes();colors.update(im.getdata());finals.append({'role':f['role'],'png':str(p),'PNGsha256':f['PNGsha256'],'decodedRGBAId':rid(im)});pixels.append({'rgba':list(im.tobytes())})
 assert len(colors)<=64 and all(p[3] in [0,255] for p in colors) and all(p==(0,0,0,0) for p in colors if not p[3]);assert colors<=set(n.getdata())|set(l.getdata())
 pc={'expectedPackageSHA256':sha((U/'src/lib/server/asset-pipeline/package.ts').read_bytes()),'expectedCanonicalSHA256':sha((U/'src/lib/server/pipeline/canonical.ts').read_bytes()),'canvas':{'width':61,'height':45},'frames':finals,'logicalPixelSize':1,'paletteLimit':64,'contacts':[],'geometryReviewed':False,'supportWorld':None};dump(r/'canonical-pixel-input.json',pc);(r/'raw-candidate-input.json').write_text(json.dumps({'canvas':pc['canvas'],'frames':pixels,'logicalPixelSize':1,'paletteLimit':64},separators=(',',':'))+'\n')
 commands=[run(['node',str(RUN),'--repo',str(U),'--input',str(r/'canonical-pixel-input.json'),'--receipt',str(r/'pixel-receipt.json'),'--sharp',SHARP],'actual-pixel',r)]
 jc={'inputs':[{'label':'raw candidate input','path':str(r/'raw-candidate-input.json')},{'label':'frozen source handoff','path':str(root/c['handoff']['file'])},{'label':'construction recipe','path':str(root/'construction-recipe.json')}],'output':str(r/'json-budget-receipt.json')};dump(r/'json-budget-config.json',jc);commands.append(run(['node',str(O/'actual-json-budget.mjs'),str(r/'json-budget-config.json')],'actual-json',r));dump(r/'commands.json',commands)
 for n0,d in pairs:
  if isinstance(d,dict):d=d.get('sha256',d.get('SHA256'))
  assert sha(member(root,n0).read_bytes())==d,n0
 (r/'producer-index.snapshot.json').write_bytes((root/c['ledger']['file']).read_bytes());(r/'producer-STABLE-GO.snapshot.json').write_bytes((root/c['stableGO']['file']).read_bytes())
 dump(r/'CONSTRUCTION-RECEIPT.json',{'scope':'Exact recipe and pixel preservation only; no semantic sole, physical contact or artistic seam acceptance','nativeInputs':native,'ancestryBytesExact':ancestry,'frozenFilesExactBeforeAndAfter':len(pairs),'maskPixelCount':len(maskXY),'protectedPixelCount':124*124-len(maskXY),'protectedVisibleCanonicalPixels':protectedVisible,'protectedRGBAChangedPixels':0,'maskMatchesDeclaredPixelCenterPolygon':True,'explicitLayersReconstructedExactly':True,'allDonorSourceXYEqualOutputXY':True,'neutralReconstructionExact':True,'hybridReconstructionExact':True,'headChangedPixels':changed,'oldHeadBillPixelsClearedByActualDonorTransparency':cleared,'donorSilhouettePixelsAdded':added,'enclosedTransparentHoles':{'neutral':len(holes(fullN)),'hybrid':len(holes(fullL)),'holesMatchProducerProof':True},'crop':[30,54,91,99],'pivot':[43,42],'density':1,'RGBAColorUnionIncludingTransparent':len(colors),'lookTimingTicks30':[60,18,12],'uniqueSourceRenderFrames':2,'commonFamilyComplete':False,'blinkIncluded':False,'newNativeCalls':0,'newDrawings':0,'actualDerivedConstructionFrames':2,'contacts':[],'supportWorld':None,'physicalSupportReviewed':False,'geometryScope':'image-registration-only','sourceAdmitted':False,'runtimeAdmission':False})
 dump(r/'RESULT.json',{'state':'COMPLETED exact frozen construction and current subset checks; inspect retained errors if present','commands':commands,'sourceModified':False,'sourceAdmitted':False,'runtimeAdmission':False,'commonInput5':'NOT APPLICABLE attention-only pair; no closure/common family fabricated','artSeamQualityOrSoleSupportAccepted':False})
 print(json.dumps({'arm':'D','output':str(r),'exitCodes':[x['exitCode'] for x in commands],'sourceFrozenFilesExact':len(pairs),'protectedChangedPixels':0}))
except Exception as e:dump(r/'FAILURE.json',{'type':type(e).__name__,'message':str(e),'sourceModified':False,'nativeCallAttempted':False,'sourceAdmitted':False});raise
