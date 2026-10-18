from pathlib import Path
from datetime import datetime, timezone
from PIL import Image, ImageDraw
import json,hashlib,shutil,time,collections,struct,zlib,binascii
P=Path(__file__).resolve().parent;A=P.parent/'arm-a-baseline'
assert not (P/'export-receipt.json').exists(),'One bounded export only'
start=time.perf_counter();utc=datetime.now(timezone.utc).isoformat()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rid(im):return 'frame.sha256.'+hashlib.sha256(('RGBA8;%dx%d;'%im.size).encode()+im.tobytes()).hexdigest()
def save(n,d):q=P/n;q.parent.mkdir(parents=True,exist_ok=True);q.write_text(json.dumps(d,indent=2)+'\n')
def png(n,im):q=P/n;q.parent.mkdir(parents=True,exist_ok=True);im.save(q)
S=(124,124);crop=(30,54,91,99);poly=[(64,54),(92,54),(92,68),(74,68),(70,66),(66,66),(64,64)]
# Polygon coordinates are cell edges. Test pixel centers, not inclusive ImageDraw fill.
def inside(x,y):
 x+=.5;y+=.5;c=False;j=len(poly)-1
 for i in range(len(poly)):
  ax,ay=poly[i];bx,by=poly[j]
  if (ay>y)!=(by>y) and x<(bx-ax)*(y-ay)/(by-ay)+ax:c=not c
  j=i
 return c
mask=Image.new('L',S);mask.putdata([255 if inside(x,y) else 0 for y in range(124) for x in range(124)])
inv=mask.point(lambda a:255-a);png('masks/head-upper-neck-replacement.png',mask);png('masks/canonical-body-protected.png',inv)
full={};provenance=[]
for role in ['neutral','look']:
 im=Image.new('RGBA',S);im.paste(Image.open(A/f'frames/{role}.png').convert('RGBA'),crop[:2]);full[role]=im;png(f'sources/stage-{role}.png',im)
 for rel in [f'frames/{role}.png',f'raw-full/{role}.png']:
  dest=P/'sources'/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(A/rel,dest);provenance.append({'file':str(dest.relative_to(P)),'upstream':'arm-a-baseline/'+rel,'SHA256':sha(dest)})
for rel in ['reference-awake-source1024.png','original.png','prompt.txt','native-call-arguments.json','call-dispatch-receipt.json','native-return-receipt.json','native-tool-return-metadata.json','source-lineage.json','historical-reference/original.png','historical-reference/prompt.txt','historical-reference/registered-frame-record.json']:
 dest=P/'source-provenance'/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(A/rel,dest);provenance.append({'file':str(dest.relative_to(P)),'upstream':'arm-a-baseline/'+rel,'SHA256':sha(dest)})
body=Image.new('RGBA',S);body.paste(full['neutral'],(0,0),inv);png('layers/canonical-body-wing-tail-legs-feet.png',body)
heads={};comps={}
for role in ['neutral','look']:
 head=Image.new('RGBA',S);head.paste(full[role],(0,0),mask);heads[role]=head;png(f'layers/{role}-head-upper-neck.png',head)
 # Disjoint binary replacement, no alpha compositing/edge blends/new colors.
 comp=body.copy();comp.paste(full[role],(0,0),mask);comps[role]=comp;png(f'full-stage/{role}.png',comp);png(f'frames/{role}.png',comp.crop(crop))
assert comps['neutral'].tobytes()==full['neutral'].tobytes()
protected=[(x,y) for y in range(124) for x in range(124) if not mask.getpixel((x,y))]
assert all(comps['neutral'].getpixel(q)==comps['look'].getpixel(q)==full['neutral'].getpixel(q) for q in protected)
alpha=[comps[r].getchannel('A') for r in ['neutral','look']]
def holes(im):
 a=im.getchannel('A');seen=set();q=collections.deque()
 for x in range(124):
  for y in [0,123]:
   if a.getpixel((x,y))==0:q.append((x,y));seen.add((x,y))
 for y in range(124):
  for x in [0,123]:
   if a.getpixel((x,y))==0:q.append((x,y));seen.add((x,y))
 while q:
  x,y=q.popleft()
  for dx,dy in [(1,0),(-1,0),(0,1),(0,-1)]:
   v=(x+dx,y+dy)
   if 0<=v[0]<124 and 0<=v[1]<124 and v not in seen and a.getpixel(v)==0:seen.add(v);q.append(v)
 return sorted([list((x,y)) for y in range(124) for x in range(124) if a.getpixel((x,y))==0 and (x,y) not in seen])
changed=[];removed=[];added=[];mapping=[]
for y in range(124):
 for x in range(124):
  q=(x,y);n=full['neutral'].getpixel(q);l=full['look'].getpixel(q);h=comps['look'].getpixel(q)
  if mask.getpixel(q):mapping.append({'outputXY':[x,y],'sourceRole':'authored-look','sourceStageXY':[x,y],'RGBA':list(l)})
  if h!=n:changed.append([x,y])
  if mask.getpixel(q) and n[3] and not h[3]:removed.append([x,y])
  if mask.getpixel(q) and h[3] and not n[3]:added.append([x,y])
assert all(mask.getpixel(tuple(q)) for q in changed)
# Technical seam boundary: adjacent mask sides only; color deltas are diagnostics, not appearance gates.
boundary=[]
for y in range(123):
 for x in range(123):
  for dx,dy in [(1,0),(0,1)]:
   a=(x,y);b=(x+dx,y+dy)
   if bool(mask.getpixel(a))!=bool(mask.getpixel(b)) and comps['look'].getpixel(a)[3] and comps['look'].getpixel(b)[3]:
    v=comps['look'].getpixel(a);w=comps['look'].getpixel(b)
    boundary.append({'a':list(a),'b':list(b),'maxRGBJump':max(abs(v[i]-w[i]) for i in range(3))})
wholelookdiff=sum(comps['look'].getpixel(q)!=full['look'].getpixel(q) for q in protected)
for r in comps:
 im=comps[r];outside=im.copy();ImageDraw.Draw(outside).rectangle((30,54,90,98),fill=(0,0,0,0));assert not any(outside.tobytes())
frames=[];hA=json.loads((A/'source-handoff.json').read_text())
for role in ['neutral','look']:
 im=Image.open(P/f'frames/{role}.png').convert('RGBA');ref=next(f for f in hA['frames'] if f['role']==role)
 frames.append({'id':role,'role':role,'png':f'frames/{role}.png','PNGsha256':sha(P/f'frames/{role}.png'),'decodedRGBAId':rid(im),'sourceFrameID':ref['sourceFrameId'],'constructionDerivative':True,'newDrawing':False,'canvas':[61,45],'density':1,'pivot':[43,42],'contacts':[],'fullStageOrigin':[30,54],'fullStagePNG':f'full-stage/{role}.png','fullStagePNGsha256':sha(P/f'full-stage/{role}.png'),'nativeSourceIDsContributing':([hA['frames'][0]['sourceFrameId']] if role=='neutral' else [hA['frames'][0]['sourceFrameId'],ref['sourceFrameId']])})
# Explicit APNG chunks preserve exact rational holds and full RGBA source replacement.
def chunk(t,b):return struct.pack('>I',len(b))+t+b+struct.pack('>I',binascii.crc32(t+b)&0xffffffff)
ims=[Image.open(P/f'frames/{r}.png').convert('RGBA') for r in ['neutral','look','neutral']];w,hh=ims[0].size
out=b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',w,hh,8,6,0,0,0))+chunk(b'acTL',struct.pack('>II',3,1));seq=0
for i,(im,t) in enumerate(zip(ims,[60,18,12])):
 out+=chunk(b'fcTL',struct.pack('>IIIIIHHBB',seq,w,hh,0,0,t,30,0,0));seq+=1
 raw=im.tobytes();data=zlib.compress(b''.join(b'\0'+raw[y*w*4:(y+1)*w*4] for y in range(hh)),9)
 if i==0:out+=chunk(b'IDAT',data)
 else:out+=chunk(b'fdAT',struct.pack('>I',seq)+data);seq+=1
out+=chunk(b'IEND',b'');(P/'look.apng').write_bytes(out)
recipe={'method':'binary source-pixel layer replacement; no rig rotation or inferred hidden anatomy','worldCanvas':hA['fullWorldCanvas'],'stage':[124,124],'density':1,'headReplacementPolygonCellEdges':poly,'maskMeaning':'Manually selected visible head/upper-neck/very small shoulder overlap; not a semantic segmentation or recovered hidden layer','pixelCenterInPolygon':True,'compositionOrder':['fixed canonical neutral body/wing/tail/legs/feet outside replacement mask','neutral or authored-look pixels inside mask, INCLUDING donor transparent pixels to clear old bill/head'],'sourceStageOriginByKey':{'neutral':[0,0],'look':[0,0]},'joint':{'neckBoundaryDiagnosticXY':[74,68],'uncertaintyWorldPixels':2,'rotation':0,'translation':[0,0],'scale':[1,1],'meaning':'Documentary cut boundary, not a calibrated joint/rig or physical neck axis'},'commonCrop':[30,54,91,99],'pivot':[43,42],'supportWorld':None,'contacts':[],'physicalSupportReviewed':False,'geometryScope':'image-registration-only','rights':'Existing project-generated source facts retained; rights/clearance UNKNOWN, no CC0 or permission invented','nativeCalls':0,'newDrawings':0,'sourcePosePainting':False,'canonicalBodyPerPoseFit':False,'sourcePixelMaps':'source-pixel-map.json'}
save('construction-recipe.json',recipe);save('source-pixel-map.json',{'mapScope':'Every pixel in replacement mask, including transparent erasure of old head; unchanged outside pixels map to canonical neutral sameXY','pixels':mapping})
proof={'protectedPixelCount':len(protected),'protectedVisibleCanonicalPixels':sum(full['neutral'].getpixel(q)[3]>0 for q in protected),'protectedBodyFeetRGBAChangedPixels':0,'neutralReconstructionByteExact':True,'headChangedPixels':len(changed),'oldHeadOrBillPixelsClearedByRealDonorTransparency':removed,'newVisibleHeadPixelsFromDonorOnly':added,'bodyDiffVersusWholeAuthoredLookOutsideMask':wholelookdiff,'enclosedTransparentHolePixels':{r:holes(im) for r,im in comps.items()},'canonicalEnclosedHolePixels':holes(full['neutral']),'sourceLookEnclosedHolePixels':holes(full['look']),'opaqueBoundaryPixelPairs':boundary,'seamAcceptance':'PENDING independent normal-scale cluster/silhouette/light/volume review; equality/holes do not certify artistic quality','noPixelsMovedResizedPainted':True,'rawOriginalSourcesPreserved':True,'maskNoBodyFeatherReconstruction':True}
save('protected-body-and-seam-proof.json',proof)
save('ancestry.json',{'inputFiles':provenance,'sourceFrameIDs':[f['sourceFrameId'] for f in hA['frames'] if f['role'] in ['neutral','look']],'noArmCSourceUsed':True,'model':None,'seed':None,'existingAttentionMethod':'One historical native authored edit; no new edit in D','rightsGranted':False,'referenceRightsAssessed':False,'historicalUnknownsRetained':True})
palette=set()
for im in comps.values():palette.update(im.getdata())
save('palette-alpha-proof.json',{'method':'Exact existing A final palette reused by source-pixel copy; zero re-quantization','colors':sorted([list(c) for c in palette]),'totalColors':len(palette),'alphaValues':sorted({c[3] for c in palette}),'transparentRGBZero':all(c[:3]==(0,0,0) for c in palette if not c[3]),'alphaOrigin':'upstream-cleanup','upstreamAlphaThreshold':128,'noDither':True})
save('source-handoff.json',{'kind':'Attention-only source construction prototype; no common-family envelope or admission','speciesId':'white_crowned_sparrow','arm':'D','newNativeCalls':0,'newDrawings':0,'existingAuthoredSourceDrawings':2,'frames':frames,'fullWorldCanvas':hA['fullWorldCanvas'],'displayStage':[124,124],'candidateCanvas':[61,45],'density':1,'crop':list(crop),'commonCropOrigin':[30,54],'candidatePivot':[43,42],'roundedFullPivot':[73,96],'oldPivotWorld':hA['oldPivotWorld'],'alphaOrigin':'upstream-cleanup','contacts':[],'supportWorld':None,'geometryScope':'image-registration-only','physicalSupportReviewed':False,'clips':[{'id':'look','tickRate':30,'frames':[{'frameId':'neutral','durationTicks':60},{'frameId':'look','durationTicks':18},{'frameId':'neutral','durationTicks':12}],'loop':False}],'blinkAvailability':'NOT INCLUDED; no new closure or full common family claimed','sourceUsefulness':'PENDING independent appearance/geometry','runtimeAdmission':False,'sourceAdmitted':False,'rightsGranted':False,'constructionRecipe':'construction-recipe.json','ancestry':'ancestry.json'})
# Actual-scale source comparison with enlarged boundary views only for inspection.
sheet=Image.new('RGB',(3*154,2*160),'#e5e0cd');d=ImageDraw.Draw(sheet)
for j,bg in enumerate(['#e5e0cd','#182a32']):
 d.rectangle((0,j*160,462,(j+1)*160),fill=bg)
 for i,(label,im) in enumerate([('canonical neutral',full['neutral']),('authored whole look',full['look']),('hybrid fixed body',comps['look'])]):
  sheet.paste(im,(i*154+10,j*160+24),im);d.text((i*154+4,j*160+4),label,fill='black' if not j else 'white')
png('normal-light-dark.png',sheet)
zoom=Image.new('RGB',(720,280),'#e5e0cd')
for i,(label,im) in enumerate([('neutral',full['neutral']),('wholelook',full['look']),('hybrid',comps['look'])]):
 z=im.crop((60,54,92,76)).resize((224,154),Image.Resampling.NEAREST);zoom.paste(z,(i*240,25),z);ImageDraw.Draw(zoom).text((i*240,4),label,fill='black')
png('enlarged-neck-inspection.png',zoom)
save('export-receipt.json',{'arm':'D','exportStartedUTC':utc,'exportCompletedUTC':datetime.now(timezone.utc).isoformat(),'observedOneExportWallSeconds':time.perf_counter()-start,'nativeCalls':0,'newDrawings':0,'deterministicExportPasses':1,'variants':1,'maskDesign':'One manually chosen polygon after source inspection; no subsequent blind retries','humanCleanupMinutes':None,'cleanupScope':'No painting/hidden underfill/pixel editing; manual inspection/design wall time not timed as human labor','sourceScaleUnchanged':True,'protectedBodyUnchanged':True,'APNGTicks':[60,18,12],'tickRate':30,'commonCropNonzeroDiscarded':0,'sourceOnly':True,'runtimeAdmission':False})
print(json.dumps({'PASS_producer_bytefacts':True,'newCalls':0,'newDrawings':0,'protectedChanged':0,'headChangedPixels':len(changed),'clearedOldHeadPixels':len(removed),'newDonorSilhouettePixels':len(added),'enclosedHoles':{r:len(holes(im)) for r,im in comps.items()},'exportSeconds':time.perf_counter()-start}))
