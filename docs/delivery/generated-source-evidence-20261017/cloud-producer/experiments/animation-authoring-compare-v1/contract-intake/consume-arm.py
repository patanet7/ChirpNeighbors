"""One immutable source-family check per arm. No export, palette, source or global writes."""
import pathlib,json,hashlib,sys,subprocess,datetime,math,collections,time
from PIL import Image
O=pathlib.Path(__file__).resolve().parent;E=O.parent;U=pathlib.Path('/workspace/runtime-resting-intake-v5-inspect');RUN=pathlib.Path('/workspace/asset-production/validation/shared-structural-check.mjs');SHARP='/opt/codex/runtimes/codex-primary-runtime/dependencies/node/node_modules/sharp/dist/index.cjs'
sha=lambda b:hashlib.sha256(b).hexdigest()
def dump(p,d):p.write_text(json.dumps(d,indent=2)+'\n')
def load(p):return json.loads(p.read_text())
def member(r,n):
 p=(r/n).resolve();assert p.is_relative_to(r.resolve()),'Path escapes frozen arm';return p
def identity(im):return 'frame.sha256.'+sha(f'RGBA8;{im.width}x{im.height};'.encode()+im.tobytes())
def run(c,n,r):
 t=time.monotonic();s=subprocess.run(c,cwd=U,capture_output=True,text=True);(r/(n+'.stdout.txt')).write_text(s.stdout);(r/(n+'.stderr.txt')).write_text(s.stderr);return {'command':c,'exitCode':s.returncode,'stdout':n+'.stdout.txt','stderr':n+'.stderr.txt','observedWallSeconds':time.monotonic()-t}
p=pathlib.Path(sys.argv[1]).resolve();assert p.is_relative_to(O);c=load(p);assert c['arm'] in ['A','C'];root=pathlib.Path(c['root']).resolve();assert root.is_relative_to(E) and not root.is_relative_to(O)
r=O/('arm-'+c['arm'].lower());assert not r.exists(),'Existing results retained; no automatic repeat';r.mkdir()
try:
 a=load(O/'authority-receipt.json');assert subprocess.check_output(['git','-C',str(U),'rev-parse','HEAD'],text=True).strip()==a['runtimeCommit'];assert sha(RUN.read_bytes())==a['sharedRunner']['sha256']
 for f in a['authorityFiles']:assert sha((U/f['file']).read_bytes())==f['sha256']
 for k in ['handoff','ledger','stableGO']:
  assert sha(member(root,c[k]['file']).read_bytes())==c[k]['sha256'],k
 h=load(member(root,c['handoff']['file']));ld=load(member(root,c['ledger']['file']));items=ld.get('files',ld) if isinstance(ld,dict) else ld
 pairs=[(x.get('file',x.get('path')),x.get('sha256',x.get('SHA256'))) for x in items] if isinstance(items,list) else list(items.items())
 for n,d in pairs:
  if isinstance(d,dict):d=d.get('sha256',d.get('SHA256'))
  assert sha(member(root,n).read_bytes())==d,n
 frames=h['frames'];assert [f['role'] for f in frames]==['neutral','blink','look'];assert h['density']==1 and h['contacts']==[];assert h['fullWorldCanvas']==[123.42857142857143]*2;assert h['displayStage']==[124,124];assert h['alphaThreshold']==128 and not h['perPoseFitPaintWarpSnap'];assert h['geometryScope']=='image-registration-only' and h['physicalSupportReviewed'] is False and h['supportWorld'] is None
 W,H=h['candidateCanvas'];ox,oy=h['commonCropOrigin'];rootxy=h['candidatePivot'];assert [ox+rootxy[0],oy+rootxy[1]]==[73,96]
 expectedTicks={'idle':[90],'blink':[60,3,27],'look':[60,18,12]};expectedRoles={'idle':['neutral'],'blink':['neutral','blink','neutral'],'look':['neutral','look','neutral']}
 for x in h['clips']:
  assert x['tickRate']==30;assert [q['durationTicks'] for q in x['frames']]==expectedTicks[x['id']];assert [q['frameId'] for q in x['frames']]==expectedRoles[x['id']]
 assert {x['id'] for x in h['clips']}==set(expectedTicks)
 actualFrames=[];pixels=[];facts=[];allColors=set();raws={};fulls={};images={}
 for f in frames:
  source=member(root,f['sourcePNG']);assert sha(source.read_bytes())==f['sourcePNGsha256'];src=Image.open(source).convert('RGBA');sid=f.get('sourceFrameID',f.get('sourceFrameId'));assert identity(src)==sid
  rawpath=member(root,f['rawPNG']);assert sha(rawpath.read_bytes())==f['rawPNGsha256'];raw=Image.open(rawpath).convert('RGBA');assert raw.size==(124,124)
  world=h['fullWorldCanvas'][0];expected=bytearray()
  for y in range(124):
   sy=math.floor((y+.5)*src.height/world)
   for x in range(124):
    sx=math.floor((x+.5)*src.width/world);expected.extend(src.getpixel((sx,sy)) if sx<src.width and sy<src.height else (0,0,0,0))
  assert raw.tobytes()==bytes(expected),'Whole-canvas scalar sample mismatch: '+f['role']
  fp=member(root,f['png']);assert sha(fp.read_bytes())==f['PNGsha256'];im=Image.open(fp).convert('RGBA');assert im.size==(W,H);assert identity(im)==f['decodedRGBAId'];assert f['pivot']==rootxy and f['density']==1 and f['contacts']==[]
  full=Image.new('RGBA',(124,124));full.paste(im,(ox,oy));thresholdLoss=0;discard=0;partial=0
  for y in range(124):
   for x in range(124):
    p0=raw.getpixel((x,y));p1=full.getpixel((x,y));assert p1[3]==(255 if p0[3]>=128 else 0),'Threshold/crop alpha mismatch';assert p1[3] or p1==(0,0,0,0)
    if 0<p0[3]<128:thresholdLoss+=1
    if 0<p0[3]<255:partial+=1
    if not (ox<=x<ox+W and oy<=y<oy+H) and p0[3]>=128:discard+=1
  assert discard==0
  colors=set(im.getdata());allColors.update(colors);assert all(p[3] in [0,255] for p in colors)
  raws[f['role']]=raw;fulls[f['role']]=full;images[f['role']]=im
  feet=[]
  for y in range(86,103):
   for x in range(59,88):
    if full.getpixel((x,y))[3]:feet.append((x,y))
  centroid=[sum(p[i] for p in feet)/len(feet) for i in [0,1]] if feet else None
  facts.append({'role':f['role'],'sourceFrameID':sid,'sourcePNGsha256':f['sourcePNGsha256'],'nativeDimensions':list(src.size),'rawPNGsha256':f['rawPNGsha256'],'finalPNGsha256':f['PNGsha256'],'decodedRGBAId':identity(im),'opaqueBBoxLocal':im.getbbox(),'RGBAColorsIncludingTransparent':len(colors),'opaquePixels':sum(p[3]>0 for p in im.getdata()),'partialAlphaBeforeCleanupPixels':partial,'belowThresholdNonzeroAlphaPixelsRemoved':thresholdLoss,'discardedThresholdOpaquePixels':discard,'scalarWholeNativeWorldSamplerExact':True,'footRegionDiagnostic':{'fullWorldROI_XYXY':[59,86,88,103],'opaquePixels':len(feet),'centroid':centroid,'scope':'Fixed image ROI only; may include leg/body fringe, not semantic toe soles or physical support'}})
  actualFrames.append({'role':f['role'],'png':str(fp),'PNGsha256':f['PNGsha256'],'decodedRGBAId':identity(im)});pixels.append({'rgba':list(im.tobytes())})
 assert len(allColors)<=64
 neutral=fulls['neutral'];look=fulls['look'];alphaDiff=sum(a[3]!=b[3] for a,b in zip(neutral.getdata(),look.getdata()));rgbDiff=sum(a!=b for a,b in zip(neutral.getdata(),look.getdata()));fixedFootDiff=sum(neutral.getpixel((x,y))!=look.getpixel((x,y)) for y in range(86,103) for x in range(59,88))
 rawinput={'canvas':{'width':W,'height':H},'frames':pixels,'logicalPixelSize':1,'paletteLimit':64};(r/'raw-candidate-input.json').write_text(json.dumps(rawinput,separators=(',',':'))+'\n')
 pc={'expectedPackageSHA256':sha((U/'src/lib/server/asset-pipeline/package.ts').read_bytes()),'expectedCanonicalSHA256':sha((U/'src/lib/server/pipeline/canonical.ts').read_bytes()),'canvas':rawinput['canvas'],'frames':actualFrames,'logicalPixelSize':1,'paletteLimit':64,'contacts':[],'geometryReviewed':False,'supportWorld':None};dump(r/'canonical-pixel-input.json',pc)
 commands=[run(['node',str(RUN),'--repo',str(U),'--input',str(r/'canonical-pixel-input.json'),'--receipt',str(r/'pixel-receipt.json'),'--sharp',SHARP],'actual-pixel',r)]
 jc={'inputs':[{'label':'raw candidate input','path':str(r/'raw-candidate-input.json')},{'label':'frozen source handoff','path':str(member(root,c['handoff']['file']))}],'output':str(r/'json-budget-receipt.json')};dump(r/'json-budget-config.json',jc);commands.append(run(['node',str(O/'actual-json-budget.mjs'),str(r/'json-budget-config.json')],'actual-json',r))
 dump(r/'commands.json',commands)
 after=[]
 for n,d in pairs:
  if isinstance(d,dict):d=d.get('sha256',d.get('SHA256'))
  assert sha(member(root,n).read_bytes())==d,n
 dump(r/'METRICS.json',{'arm':c['arm'],'frozenRoot':str(root),'handoff':c['handoff'],'frozenLedger':c['ledger'],'frozenFilesExactBeforeAndAfter':len(pairs),'canvas':[W,H],'uniqueDecodedArea':W*H*3,'density':1,'fullWorldCanvas':h['fullWorldCanvas'],'cropOrigin':[ox,oy],'pivot':rootxy,'fullRoot':[73,96],'RGBAColorUnionIncludingTransparent':len(allColors),'paletteRGB':sorted([list(p[:3]) for p in allColors if p[3]]),'alphaValues':[0,255],'frames':facts,'lookVsNeutralFullWorld':{'RGBAChangedPixels':rgbDiff,'alphaChangedPixels':alphaDiff,'fixedFootROIChangedPixels':fixedFootDiff,'scope':'Pixel differences, not anatomy quality or semantic foot contact verdict'},'clocks':h['clips'],'contacts':[],'geometryScope':'image-registration-only','physicalSupportReviewed':False,'supportWorld':None,'sourcePixelsModified':False,'nativeCallsByThisCheck':0,'newDrawingsByThisCheck':0,'registrationPendingAsDeclared':c.get('registrationPending'),'sourceAdmitted':False,'runtimeAdmission':False})
 dump(r/'RESULT.json',{'state':'COMPLETED exact frozen source comparison checks; consult actual failures if present','arm':c['arm'],'commands':commands,'sourceAdmitted':False,'runtimeAdmission':False,'fullPrivateLineageOrPolicyRecoveryExecuted':False,'notes':'Raw/final/source pixels and named clocks verified; empty contacts are no physical support claim. Normal-size art/temporal quality is independent review scope.'})
 print(json.dumps({'arm':c['arm'],'output':str(r),'exitCodes':[x['exitCode'] for x in commands],'frozenFiles':len(pairs)}))
except Exception as e:
 dump(r/'FAILURE.json',{'type':type(e).__name__,'message':str(e),'sourceModified':False,'nativeCallAttempted':False,'sourceAdmitted':False});raise
