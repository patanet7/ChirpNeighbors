from pathlib import Path
from PIL import Image,ImageDraw,__version__
import numpy as np,json,hashlib,shutil,subprocess,datetime
A=Path(__file__).resolve().parent;P=Path('/workspace/asset-production/motion/sd20-mourning-dove-bathe-singlepose-v2/cohort');C=Path('/workspace/asset-production/audits/crow-ground-runtime-compatible-v1/runtime-v3-adapter');sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();J=lambda n,v:(A/n).write_text(json.dumps(v,indent=2)+'\n');load=lambda p:json.loads(Path(p).read_text());fid=lambda im:'frame.sha256.'+hashlib.sha256(f'RGBA8;{im.width}x{im.height};'.encode()+im.tobytes()).hexdigest()
LH='226822763873280f61b8a9f673517c9507fbd7e19194e20a9657e2583bc881d0';assert sha(P/'review-target-hashes.json')==LH;L=load(P/'review-target-hashes.json');assert len(L)==96 and all(sha(P/n)==h for n,h in L.items());protect={n:sha(P/n)for n in ['source-technical-review.json','source-technical-review.md']};m=load(P/'COHORT-SOURCE-MANIFEST.json');proposal=load(P/'cohort-behavior-proposal.json');landmarks=load(P/'phase-landmark-proxies.json')['phaseLandmarks'];assert len(m['frames'])==6 and proposal['complete'];rows=m['frames'];images=[Image.open(P/r['outputPNG']).convert('RGBA')for r in rows];arrays=[np.array(i)for i in images];masks=[a[:,:,3]>=128 for a in arrays];samples=np.concatenate([a[:,:,:3][mask]for a,mask in zip(arrays,masks)],axis=0);rgb=Image.fromarray(samples.reshape(1,-1,3),'RGB')
# Copy exact authorized codec and actual error class, not a weakened or rewritten validator.
for n in ['exact-runtime-codec.ts','codec-extraction-receipt.json','contract-snapshot/src/lib/server/pipeline/canonical.ts','contract-snapshot/src/lib/server/asset-pipeline/package.ts']:
 q=A/n;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(C/n,q);assert sha(q)==sha(C/n)
loss=[]
for r,a,mask,l in zip(rows,arrays,masks,landmarks):
 assert r['phase']==l['phase'];lost=(a[:,:,3]>0)&~mask;windows=[];zone=np.zeros(mask.shape,dtype=bool)
 for p in l['footRegionProxies']:
  x,y=p['cohortPoint'];rect=[max(0,x-3),max(0,y-3),min(136,x+4),min(80,y+4)];zone[rect[1]:rect[3],rect[0]:rect[2]]=True;windows.append(rect)
 bbox=lambda k:list(Image.fromarray(np.where(a[:,:,3]>=k,255,0).astype('uint8')).getbbox())
 loss.append({'phase':r['phase'],'sourceFrameId':r['sourceFrameId'],'sourceCohortPNGsha256':r['outputPNGsha256'],'upstreamCropPositiveAlphaExcluded':r['sourcePositiveAlphaRemovedByFixedCrop'],'rawPositiveAlphaPixels':int((a[:,:,3]>0).sum()),'binaryOpaquePixels':int(mask.sum()),'thresholdPositiveAlphaRemoved':int(lost.sum()),'partialAlphaPromotedTo255':int(((a[:,:,3]>=128)&(a[:,:,3]<255)).sum()),'rawPositiveAlphaBBox':bbox(1),'binaryAlphaBBox':bbox(128),'footDiagnosticWindows':windows,'footWindowPositiveAlphaRemoved':int((lost&zone).sum()),'footImageProxyFloorResidualsUnchanged':[p['floorResidualPixels']for p in l['footRegionProxies']],'footImageProxyAlphaBefore':[p['actualCohortRGBA'][3]for p in l['footRegionProxies']],'footImageProxyAlphaAfter':[255 if p['actualCohortRGBA'][3]>=128 else 0 for p in l['footRegionProxies']],'billImageProxyWaterResidualUnchanged':l['billRegionProxy']['waterResidualPixels'],'meaning':'Fixed image-region diagnostics include neighboring pixels; no tracked sole, geometric repair, grip, water or physical contact claim.'})
J('threshold-and-contact-diagnostics.json',{'alphaThreshold':128,'transparentRGBA':[0,0,0,0],'binaryAlpha':[0,255],'geometricTransform':'NONE; cohort136x80 coordinates unchanged','frames':loss,'contacts':[],'geometryReviewed':False,'supportWorld':None})
def count_rects(im):
 rectangles=[];prior={}
 for y in range(im.height):
  current={};x=0
  while x<im.width:
   p=im.getpixel((x,y));start=x;x+=1
   if not p[3]:continue
   while x<im.width and im.getpixel((x,y))==p:x+=1
   key=(start,x-start,p[:3]);above=prior.get(key)
   if above is None:current[key]=len(rectangles);rectangles.append([start,y,x-start,1,p[:3]])
   else:rectangles[above][3]+=1;current[key]=above
  prior=current
 return len(rectangles)
tests=[];selected=None
for total in [64,48,32,24,16]:
 V=A/f'total{total}';assert not V.exists(),'Run once only; preserve prior attempts';V.mkdir();quant=np.array(rgb.quantize(colors=total-1,method=Image.Quantize.MEDIANCUT,dither=Image.Dither.NONE).convert('RGB')).reshape(-1,3);offset=0;entries=[];globalColors=set();rendered=[]
 for r,a,mask in zip(rows,arrays,masks):
  out=np.zeros_like(a);n=int(mask.sum());out[:,:,:3][mask]=quant[offset:offset+n];out[:,:,3][mask]=255;offset+=n;im=Image.fromarray(out,'RGBA');name=r['phase']+'136x80.png';im.save(V/name);assert np.array_equal(out[:,:,3],np.where(mask,255,0))and np.all(out[:,:,:3][~mask]==0);globalColors.update(im.get_flattened_data());rendered.append(im)
  entries.append({'phase':r['phase'],'PNG':name,'PNGsha256':sha(V/name),'derivativeDecodedRGBAId':fid(im),'sourceFrameId':r['sourceFrameId'],'sourceCohortPNGsha256':r['outputPNGsha256'],'alpha128MaskExact':True,'canvas':[136,80],'pivot':[77,76],'density':1,'diagnosticRectangles':count_rects(im),'contacts':[]})
 assert offset==len(samples)and len(globalColors)<=total;cfg={'totalColors':total,'frames':entries,'ticks':[18,18,12,18,12,24],'candidateArea':65280,'oldAwakeExcluded':True};(V/'candidate-input.json').write_text(json.dumps(cfg,indent=2)+'\n')
 cmd=['node','--experimental-strip-types',str(A/'run_exact_codec.mjs'),str(V/'candidate-input.json')];result=subprocess.run(cmd,capture_output=True,text=True);(V/'actual-codec.stdout.txt').write_text(result.stdout);(V/'actual-codec.stderr.txt').write_text(result.stderr);actual=json.loads(result.stdout);assert result.returncode==(0 if actual['passed']else 1)
 counts=[r['diagnosticRectangles']for r in entries];test={'totalColorLimit':total,'actualRGBAColorsAcrossSix':len(globalColors),'opaqueCommonPaletteColors':len(globalColors)-1,'perFrameRectangles':counts,'summedRectangles':sum(counts),'perFrameUnder4096':all(c<=4096 for c in counts),'sumUnder16384':sum(counts)<=16384,'actualExactCodec':actual,'strictPass':actual['passed'],'maskAndCanvasPreserved':True,'directory':V.name};tests.append(test)
 if actual['passed']:
  assert actual['perFrameRectangles']==counts and actual['sumRectangles']==sum(counts)and actual['pixelReconstructionExact']is True;selected=total
  # Source-art comparison sheet at exact136world pixels, no browser captures.
  sheet=Image.new('RGB',(136*6,98*4),'#d9d4bd');d=ImageDraw.Draw(sheet)
  for bgrow,bg in enumerate(['#d9d4bd','#17221f']):
   for i,(original,derivative,r)in enumerate(zip(images,rendered,rows)):
    for pair,im in enumerate([original,derivative]):
     y=(bgrow*2+pair)*98;tile=Image.new('RGBA',(136,80),bg);tile.alpha_composite(im);sheet.paste(tile.convert('RGB'),(i*136,y+18));d.rectangle((i*136,y,(i+1)*136-1,y+17),fill=bg);d.text((i*136+2,y+2),r['phase']+(' RAW'if pair==0 else f' C{total}'),fill='white'if bgrow else'#24342b')
  sheet.save(A/'selected-normal-source-derivative-light-dark.png');break
J('codec-evaluation.json',{'status':'STRICT SIX-FRAME CODEC PASS; physical/source action acceptance separate'if selected else'HELD no authorized palette passes strict six-frame codec','tested':tests,'selectedTotalColors':selected,'stopRule':'64,48,32,24,16 descending; stop FIRST strict6framePASS, no unrequested lower tests','codecSource':'exact unchanged normalizeDecodedPixels with actual PermanentStageError from retained6f23d988 code','sourceFunctionSHA256':sha(A/'exact-runtime-codec.ts'),'decoder':'actual installed Sharp0.35.4 RGBA decode','globalDecodedArea':65280,'sourceNativeCallsAdded':0,'newPrimaryDrawings':0,'fullRuntimeManifestValidation':False,'canonicalMacAdmission':False})
if selected:
 V=A/f'total{selected}';actual=tests[-1]['actualExactCodec'];J('selected-field-mapping.json',{'kind':'partial v3 pixel/clip-field mapping; NOT complete runtime manifest','selectedTotalColors':selected,'frames':load(V/'candidate-input.json')['frames'],'pixelDescriptor':{'file':str((V/'pixel-clip-fields.partial.json').relative_to(A)),'sha256':sha(V/'pixel-clip-fields.partial.json')},'actualCodecReceipt':{'file':str((V/'actual-codec.stdout.txt').relative_to(A)),'sha256':sha(V/'actual-codec.stdout.txt')},'canvas':[136,80],'densityIntent':1,'pivot':[77,76],'candidateArea':65280,'oldAwakeAssetOutsideCandidate':True,'authoredScheduleTicks':[18,18,12,18,12,24],'candidateDurationTicks':102,'oneShot':True,'sourceClipId':'bathe','availableCloudV3ActionProposal':'bathing','currentMacActionContract':'UNKNOWN; no alias/admission inferred','rootTranslation':[0,0],'illustrativeWaterY':70,'nominalFloorY':76,'contacts':[],'geometryReviewed':False,'supportWorld':None,'fullManifestMissing':'Real species/catalog/provenance/fidelity/reference/sourceArtifact pins and authoritative action resolver/idle-asset composition; actual current runtime full validator required. No fake idle added to bathing keys.','paletteVisualReview':'PENDING coordinator comparison','acceptedBathingSlots':0,'runtimeAdmitted':False,'bodyFit':False,'perPhaseTranslation':False,'paint':False,'maskInterpretation':'Binaryalpha128 loses source fringes; positive foot/image proxies do not establish support, soles, pressure or water contact.'})
J('source-preservation-receipt.json',{'sourceCohort':str(P),'frozenLedgerSHA256':LH,'all96SourceFrozenFilesUnchanged':all(sha(P/n)==h for n,h in L.items()),'sourceTechnicalReviewPairUnchanged':{n:sha(P/n)for n in protect},'expectedTechnicalReviewHashes':protect,'sourceIDs':[r['sourceFrameId']for r in rows],'cohortPNGsha256':[r['outputPNGsha256']for r in rows],'newNativeCalls':0,'newSourceDrawings':0,'onlyWrites':str(A),'sourcePixelsUnchanged':True});assert all(sha(P/n)==h for n,h in L.items())and all(sha(P/n)==h for n,h in protect.items())
(A/'README.md').write_text('''Dove bathing runtime codec derivative — source proposal only

This separate zero-call audit thresholds the frozen six136×80 cohort frames at alpha128, RGB0 for transparent pixels, then applies one common opaque RGB median-cut palette/no dither across the entire family. No fit, translation, body/foot movement or painting. Source96 frozen files and source technical reviews remain exact. Only palettes64/48/32/24/16 are authorized, descending, STOP first strict six-frame pass.

Actual unchanged normalizeDecodedPixels with its actual PermanentStageError validates sixframes together: area65,280, per-frame4,096 and sum16,384 rectangles, binary alpha and common palette. Decoder reconstruction proof is pixel-exact. See codec-evaluation.json for actual pass/fail and every count; no successful cohort is invented when none passes.

Threshold loss and foot-region/proxy gaps are disclosed per phase. Nominal77,76/floor76/water70 remain authored source coordinates; contacts[]/supportnull/geometryfalse. Palette/threshold fidelity requires separate visual review. No accepted full bathing slot, pressure/plant/water physics/resource consumption or runtime admission. Existing awake is a separate comparison asset, not a seventh decoded candidate frame.

Any selected descriptor contains only pixel/clip/normalization fields; available cloud actionbathing is a proposal mapping from sourcebathe. Actual Mac action/schema/pins/production metadata and proper separate idle-asset composition remain unverified. No fake idle pose, provenance pins or full-schema pass. Source pipeline adds0nativecalls/0primarydrawings. All variants/failures retained; no browser captures or app/global/Git/Library changes.
''')
files=[p for p in sorted(A.rglob('*'))if p.is_file()and p.name!='source-files.sha256.json'];J('source-files.sha256.json',{'files':[{'file':str(p.relative_to(A)),'sha256':sha(p),'bytes':p.stat().st_size}for p in files],'state':'selected pixel-codec derivative only; no accepted bathing/runtime claim'})
print(json.dumps({'selectedTotalColors':selected,'testedCounts':[{'total':r['totalColorLimit'],'rectangles':r['perFrameRectangles'],'sum':r['summedRectangles'],'strictPass':r['strictPass']}for r in tests],'evaluationSHA256':sha(A/'codec-evaluation.json'),'indexSHA256':sha(A/'source-files.sha256.json'),'source96Unchanged':True},indent=2))
