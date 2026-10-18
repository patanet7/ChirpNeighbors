from pathlib import Path
from datetime import datetime,timezone
from PIL import Image, ImageDraw
import json,hashlib,shutil,time,math,collections,struct,zlib,binascii
P=Path(__file__).resolve().parent;D=P.parent/'animation-authoring-compare-v1/arm-d-hybrid-construction';A=D.parent/'arm-a-baseline'
assert not(P/'export-receipt.json').exists(),'One selected export, no retries or parameter search'
started=time.perf_counter();utc=datetime.now(timezone.utc).isoformat()
def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()
def save(n,d):f=P/n;f.parent.mkdir(parents=True,exist_ok=True);f.write_text(json.dumps(d,indent=2)+'\n')
def png(n,im):f=P/n;f.parent.mkdir(parents=True,exist_ok=True);im.save(f)
def rid(im):return 'frame.sha256.'+hashlib.sha256(('RGBA8;%dx%d;'%im.size).encode()+im.tobytes()).hexdigest()
def guard(folder):
 l=json.loads((folder/'review-target-hashes.json').read_text())
 for row in l['files']:assert sha(folder/row['path'])==row['SHA256']
 return {'frozenInputs':len(l['files']),'ledgerSHA256':sha(folder/'review-target-hashes.json'),'unchanged':True}
guards={'A':guard(A),'D':guard(D)};S=(124,124);poly=[(64,54),(92,54),(92,66),(86,66),(86,68),(82,68),(82,70),(78,70),(78,69),(74,69),(74,68),(70,66),(66,66),(64,64)]
def inside(x,y):
 x+=.5;y+=.5;c=False;j=len(poly)-1
 for i,(ax,ay) in enumerate(poly):
  bx,by=poly[j]
  if(ay>y)!=(by>y) and x<(bx-ax)*(y-ay)/(by-ay)+ax:c=not c
  j=i
 return c
mask=Image.new('L',S);mask.putdata([255 if inside(x,y) else 0 for y in range(124) for x in range(124)]);inv=mask.point(lambda a:255-a)
png('masks/revised-head-upper-neck.png',mask);png('masks/canonical-body-layer-ownership.png',inv)
N=Image.open(D/'sources/stage-neutral.png').convert('RGBA');L=Image.open(D/'sources/stage-look.png').convert('RGBA');oldD=Image.open(D/'full-stage/look.png').convert('RGBA')
for role,im in [('neutral',N),('authored-look',L),('prior-D-look',oldD)]:png(f'sources/{role}-stage.png',im)
ancestry=[]
for src in sorted((D/'source-provenance').rglob('*')):
 if src.is_file():
  rel=src.relative_to(D);dst=P/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst);ancestry.append({'file':str(rel),'upstream':'animation-authoring-compare-v1/arm-d-hybrid-construction/'+str(rel),'SHA256':sha(dst)})
for src in [D/'construction-recipe.json',D/'artifact-manifest.json',D/'source-handoff.json',A/'baseline-palette.json']:
 dst=P/'historical-facts'/('prior-D-'+src.name if src.parent==D else src.name);dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst)
body=Image.new('RGBA',S);body.paste(N,(0,0),inv);png('layers/canonical-body-wing-tail-legs-feet.png',body)
headN=Image.new('RGBA',S);headN.paste(N,(0,0),mask);headL=Image.new('RGBA',S);headL.paste(L,(0,0),mask)
png('layers/neutral-head-upper-neck.png',headN);png('layers/authored-look-head-upper-neck.png',headL)
frames={};maps={};comp=body.copy();comp.paste(N,(0,0),mask);assert comp.tobytes()==N.tobytes();frames['neutral']=comp
comp=body.copy();comp.paste(L,(0,0),mask);frames['look']=comp
maps['look']=[{'outputXY':[x,y],'donor':'authored-look','sourceXY':[x,y],'RGBA':list(L.getpixel((x,y)))} for y in range(124) for x in range(124) if mask.getpixel((x,y))]
pivot=(74.,68.);rotation_masks={};rotation_details=[]
for angle in [-6,0,6]:
 a=math.radians(angle);c=math.cos(a);s=math.sin(a);key='roll-minus6' if angle<0 else 'roll-plus6' if angle>0 else 'roll-zero';rot=Image.new('RGBA',S);rm=Image.new('L',S);mapping=[]
 for y in range(124):
  for x in range(124):
   dx=x+.5-pivot[0];dy=y+.5-pivot[1]
   sx=pivot[0]+c*dx+s*dy;sy=pivot[1]-s*dx+c*dy;ix=math.floor(sx);iy=math.floor(sy)
   if 0<=ix<124 and 0<=iy<124 and mask.getpixel((ix,iy)):
    rm.putpixel((x,y),255);rgba=headN.getpixel((ix,iy));rot.putpixel((x,y),rgba);mapping.append({'outputXY':[x,y],'donor':'neutral-head-upper-neck','sourceXY':[ix,iy],'sourceContinuousXY':[sx,sy],'RGBA':list(rgba)})
 # Fixed canonical body has no recovered pixels under the original cut.
 # Opaque rotated head occludes actual existing body pixels; transparent head does not fabricate fill.
 render=body.copy()
 for y in range(124):
  for x in range(124):
   rgba=rot.getpixel((x,y))
   if rgba[3]:render.putpixel((x,y),rgba)
 if angle==0:assert render.tobytes()==N.tobytes()
 else:frames[key]=render
 png(f'control-layers/{key}-head.png',rot);png(f'masks/{key}-rotated-ownership.png',rm);rotation_masks[key]=rm;maps[key]=mapping
 gaps=[[x,y] for y in range(124) for x in range(124) if mask.getpixel((x,y)) and N.getpixel((x,y))[3] and not render.getpixel((x,y))[3]]
 overlap=[[x,y] for y in range(124) for x in range(124) if not mask.getpixel((x,y)) and body.getpixel((x,y))[3] and rot.getpixel((x,y))[3]]
 escaped=[]
 # Forward image-coordinate bound diagnostic for all visible source head centers.
 for y in range(124):
  for x in range(124):
   if headN.getpixel((x,y))[3]:
    dx=x+.5-pivot[0];dy=y+.5-pivot[1];tx=pivot[0]+c*dx-s*dy;ty=pivot[1]+s*dx+c*dy
    if not(0<=tx<124 and 0<=ty<124):escaped.append([x,y])
 assert not escaped
 rotation_details.append({'key':key,'angleDegreesClockwise':angle,'pivotWorld':list(pivot),'forwardMatrix':[c,-s,s,c],'inverseMatrix':[c,s,-s,c],'sample':'Destination pixel centers → inverse matrix → floor(source continuous coordinate), straightRGBA copy, no interpolation','translation':[0,0],'scale':[1,1],'uncoveredOriginalVisibleCutoutPixels':gaps,'opaqueHeadOccludesBodyOutsideOriginalCutMask':overlap,'sourceVisibleCentersOutsideStage':escaped,'mechanicalDisposition':'HOLD_MISSING_VISIBLE_NECK_ARTWORK' if gaps else 'SOURCE_CONTROL_ONLY_PENDING_NORMAL_REVIEW','uncertaintyWorldPixels':2,'physicalJointCalibration':False})
# One common envelope across finite explicit rotations protects rendered pixels beyond moving head ownership.
protected=Image.new('L',S,255)
for y in range(124):
 for x in range(124):
  if mask.getpixel((x,y)) or any(m.getpixel((x,y)) for m in rotation_masks.values()):protected.putpixel((x,y),0)
png('masks/strict-protected-render-region.png',protected)
core=Image.new('L',S);ImageDraw.Draw(core).rectangle((0,74,123,123),fill=255);png('masks/core-body-feet-y74plus.png',core)
for key,im in frames.items():
 for y in range(124):
  for x in range(124):
   if protected.getpixel((x,y)) or core.getpixel((x,y)):assert im.getpixel((x,y))==N.getpixel((x,y)),(key,x,y)
# One zero-only common crop; never fit or separately shift any pose.
bbox=None
for im in frames.values():
 b=im.getchannel('A').getbbox()
 if b:bbox=b if bbox is None else(min(b[0],bbox[0]),min(b[1],bbox[1]),max(b[2],bbox[2]),max(b[3],bbox[3]))
crop=(min(30,bbox[0]),min(54,bbox[1]),max(91,bbox[2]),max(99,bbox[3]));framefacts=[]
hA=json.loads((A/'source-handoff.json').read_text());nativeIDs=[f['sourceFrameId'] for f in hA['frames'] if f['role'] in ['neutral','look']]
for key,im in frames.items():
 png(f'full-stage/{key}.png',im);cr=im.crop(crop);png(f'frames/{key}.png',cr);outside=im.copy();ImageDraw.Draw(outside).rectangle((crop[0],crop[1],crop[2]-1,crop[3]-1),fill=(0,0,0,0));assert not any(outside.tobytes())
 framefacts.append({'id':key,'role':key,'png':f'frames/{key}.png','PNGsha256':sha(P/f'frames/{key}.png'),'decodedRGBAId':rid(cr),'fullStagePNG':f'full-stage/{key}.png','fullStagePNGsha256':sha(P/f'full-stage/{key}.png'),'canvas':list(cr.size),'density':1,'pivot':[73-crop[0],96-crop[1]],'fullStageOrigin':list(crop[:2]),'contacts':[],'sourceFrameIDsContributing':nativeIDs if key=='look' else [nativeIDs[0]],'constructionDerivative':True,'newDrawing':False})
# APNG uses explicit rational per-key holds, binary alpha, no optimizer/coalescing.
def chunk(t,b):return struct.pack('>I',len(b))+t+b+struct.pack('>I',binascii.crc32(t+b)&0xffffffff)
def apng(name,schedule):
 ims=[frames[k].crop(crop) for k,t in schedule];w,hh=ims[0].size;out=b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',w,hh,8,6,0,0,0))+chunk(b'acTL',struct.pack('>II',len(ims),1));seq=0
 for i,(im,(key,ticks)) in enumerate(zip(ims,schedule)):
  out+=chunk(b'fcTL',struct.pack('>IIIIIHHBB',seq,w,hh,0,0,ticks,30,0,0));seq+=1;raw=im.tobytes();data=zlib.compress(b''.join(b'\0'+raw[y*w*4:(y+1)*w*4] for y in range(hh)),9)
  if i==0:out+=chunk(b'IDAT',data)
  else:out+=chunk(b'fdAT',struct.pack('>I',seq)+data);seq+=1
 out+=chunk(b'IEND',b'');(P/name).write_bytes(out)
main=[('neutral',60),('look',18),('neutral',12)];control=[('neutral',45),('roll-minus6',12),('neutral',6),('roll-plus6',12),('neutral',15)]
apng('attention.apng',main);apng('head-roll-study.apng',control)
def clip(id,sch):return {'id':id,'tickRate':30,'frames':[{'frameId':k,'durationTicks':t} for k,t in sch],'loop':False}
base={'kind':'Layered2D visible-source construction study, no runtime admission','speciesId':'white_crowned_sparrow','nativeCalls':0,'newDrawings':0,'primarySourceIDsAdded':0,'fullWorldCanvas':[123.42857142857143]*2,'displayStage':[124,124],'candidateCanvas':[crop[2]-crop[0],crop[3]-crop[1]],'density':1,'commonCropOrigin':list(crop[:2]),'crop':list(crop),'candidatePivot':[73-crop[0],96-crop[1]],'fullRoundedPivot':[73,96],'oldPivotWorld':[73.28571428571428,96.42857142857143],'alphaOrigin':'upstream-cleanup','contacts':[],'supportWorld':None,'geometryScope':'image-registration-only','physicalSupportReviewed':False,'rightsGranted':False,'sourceAdmitted':False,'runtimeAdmission':False,'frames':framefacts}
save('source-handoff.json',{**base,'frames':[f for f in framefacts if f['id'] in ['neutral','look']],'clips':[clip('attention',main)],'scope':'Main authored-head key selection with one revised neckline ownership contour; no source transforms'})
save('control-handoff.json',{**base,'frames':[f for f in framefacts if f['id']!='look'],'clips':[clip('head-roll',control)],'scope':'Actual2D neutral-head in-plane roll. Not3Dyaw, biologicaljoint, full articulated bird or hidden anatomy repair','angles':rotation_details,'controlsAccepted':False})
save('construction-recipe.json',{'priorDRecipe':'historical-facts/prior-D-construction-recipe.json','priorDImmutable':guards['D'],'chosenContourCellEdges':poly,'maskRaster':'Raycast atworldpixelcenter; binary ownership; polygon used once','layers':['layers/canonical-body-wing-tail-legs-feet.png','layers/neutral-head-upper-neck.png','layers/authored-look-head-upper-neck.png'],'mainComposition':'Static canonicalbody outsidechosenmask plus exactneutral/look sourcepixels inside, including donortransparency','controlComposition':'Same staticbody cutout plus opaque samples of rotated neutralhead; no underfill. Transparent head contributes nothing outside mask; visible original cutout gaps remain unpainted.','pivotWorld':[74,68],'pivotMeaning':'Documentary2D control point, not calibrated biologicaljoint','jointUncertaintyWorldPixels':2,'anglesDegreesClockwise':[-6,0,6],'rotationTransforms':rotation_details,'sourceScale':[1,1],'rootTravel':[0,0],'wholeCanvasFit':False,'commonCrop':list(crop),'strictProtectedMask':'masks/strict-protected-render-region.png','coreFeetBodyMask':'masks/core-body-feet-y74plus.png','canonicalBodyLayerByteStable':True,'bodyLayerMotion':False,'actualVisibleDonorOnly':True,'noPaintSoftenRecolor':True,'noNewNativeCalls':True})
save('source-pixel-maps.json',{'main':'Authoredlook sameXY inside revisedpolygon; canonicalneutral outside','controls':'InverseNN transformedneutralhead sourceXY includes transparentvalues; controlcomposition only overlays opaque samples','maps':maps})
# Explicit alpha topology diagnostics, not a sole/support or quality certificate.
def holes(im):
 a=im.getchannel('A');seen=set();q=collections.deque()
 for y in range(124):
  for x in range(124):
   if(x in [0,123] or y in [0,123]) and not a.getpixel((x,y)):seen.add((x,y));q.append((x,y))
 while q:
  x,y=q.popleft()
  for dx,dy in [(1,0),(-1,0),(0,1),(0,-1)]:
   v=(x+dx,y+dy)
   if 0<=v[0]<124 and 0<=v[1]<124 and v not in seen and not a.getpixel(v):seen.add(v);q.append(v)
 return [[x,y] for y in range(124) for x in range(124) if not a.getpixel((x,y)) and (x,y) not in seen]
seams={}
for key,im in frames.items():
 boundary=[]
 for y in range(123):
  for x in range(123):
   for dx,dy in [(1,0),(0,1)]:
    a=(x,y);b=(x+dx,y+dy)
    if bool(mask.getpixel(a))!=bool(mask.getpixel(b)) and im.getpixel(a)[3] and im.getpixel(b)[3]:boundary.append({'a':list(a),'b':list(b),'maxRGBJump':max(abs(im.getpixel(a)[i]-im.getpixel(b)[i]) for i in range(3))})
 seams[key]={'enclosedTransparentPixels':holes(im),'opaqueCutBoundaryPairs':boundary,'newTransparentCanonicalCutoutPixels':[[x,y] for y in range(124) for x in range(124) if mask.getpixel((x,y)) and N.getpixel((x,y))[3] and not im.getpixel((x,y))[3]]}
oldMask=Image.open(D/'masks/head-upper-neck-replacement.png');ownership_changes=[[x,y] for y in range(124) for x in range(124) if mask.getpixel((x,y))!=oldMask.getpixel((x,y))]
mainchanges=[[x,y] for y in range(124) for x in range(124) if frames['look'].getpixel((x,y))!=oldD.getpixel((x,y))]
save('protection-seam-occlusion-proof.json',{'priorDGuard':guards['D'],'priorAGuard':guards['A'],'ownershipContourChangedPixels':ownership_changes,'renderedLookChangedVersusPriorD':mainchanges,'strictProtectedRenderedChangesByFrame':{k:0 for k in frames},'coreBodyFeetY74PlusChangesByFrame':{k:0 for k in frames},'bodyLayerIsCanonicalOutsideChosenCutout':True,'protectedRegionMeaning':'Complement ofunion ofchosenmask andall3finite rotatedownership masks; not handwaving over changes. Core bodyfeet y>=74 also exact.','perFrameDiagnostics':seams,'angleDisposition':rotation_details,'commonCropDiscardedRGBA':0,'qualityGate':'Independentnormal/enlarged neckline/cluster/light/volume review still required; unchangedbody and topology are not artapproval','physicalSupportReviewed':False})
colors=set();Acolors=set(tuple(c) for c in json.loads((A/'baseline-palette.json').read_text())['colors'])
for im in frames.values():colors.update(im.getdata())
assert colors<=Acolors and all(c[3] in[0,255] and(c[3] or c[:3]==(0,0,0)) for c in colors)
save('palette-proof.json',{'retainedA63PaletteSHA256':sha(A/'baseline-palette.json'),'exactAColorSubset':True,'colors':sorted([list(c) for c in colors]),'countIncludingTransparent':len(colors),'alphaValues':[0,255],'alphaOrigin':'upstream-cleanup','newQuantization':False,'dither':False,'transparentRGBZero':True})
save('ancestry.json',{'sourceFrameIDs':nativeIDs,'retainedSourceFiles':ancestry,'newNativeCalls':0,'newDrawings':0,'newPrimaryIDs':[],'model':None,'seed':None,'rightsFacts':'Existing project-generated references retained with originalprompts/args; rights/referenceclearance unresolved; no CC0 or hiddenart inferred','CImageUsed':False})
save('PRIMARY-SOURCE-MANIFEST.json',{'nativeCalls':0,'newDrawings':0,'frames':[],'reusedSourceIDs':nativeIDs,'renderDerivatives':framefacts,'sourceStatus':'New neckline and finitecontrol prototype pending independentreview; rotations with cutoutgap are held','runtimeAdmission':False})
# True-scale comparison and enlarged cropped ownership diagnostics, no visual resampling of outputs.
sheet=Image.new('RGB',(5*150,320),'#e5e0cd');draw=ImageDraw.Draw(sheet)
items=[('prior D',oldD),('refined look',frames['look']),('neutral / 0deg',N),('-6deg control',frames['roll-minus6']),('+6deg control',frames['roll-plus6'])]
for j,bg in enumerate(['#e5e0cd','#182a32']):
 draw.rectangle((0,j*160,750,(j+1)*160),fill=bg)
 for i,(label,im) in enumerate(items):sheet.paste(im,(i*150+8,j*160+26),im);draw.text((i*150+3,j*160+4),label,fill='black' if not j else 'white')
png('normal-light-dark.png',sheet)
zoom=Image.new('RGB',(5*224,230),'#e5e0cd');zd=ImageDraw.Draw(zoom)
for i,(label,im) in enumerate(items):
 zz=im.crop((60,53,92,77)).resize((224,168),Image.Resampling.NEAREST);zoom.paste(zz,(i*224,25),zz);zd.text((i*224+2,4),label,fill='black')
png('enlarged-neckline-controls.png',zoom)
guards_after={'A':guard(A),'D':guard(D)};assert guards==guards_after
save('export-receipt.json',{'startedUTC':utc,'completedUTC':datetime.now(timezone.utc).isoformat(),'observedExportWallSeconds':time.perf_counter()-started,'oneInspectedContour':1,'chosenExportPasses':1,'angleTrials':[-6,0,6],'angleTrialCount':3,'parameterSearch':False,'retries':0,'nativeCalls':0,'newDrawings':0,'newPrimarySourceIDs':0,'manualCleanupMinutes':None,'manualCleanupMeaning':'No hiddenpaint/recolor/softening performed; inspection/design not estimated as human labor','mainClock':[60,18,12],'studyClock':[45,12,6,12,15],'tickRate':30,'crop':list(crop),'pivot':[73-crop[0],96-crop[1]],'commonDiscardedRGBA':0,'paletteUnchanged':True,'originalGuards':guards_after,'runtimeAdmission':False})
print(json.dumps({'exportedOnce':True,'crop':crop,'pivot':[73-crop[0],96-crop[1]],'revisedLookChangedVsD':len(mainchanges),'ownershipChanges':len(ownership_changes),'angleGaps':{d['key']:len(d['uncoveredOriginalVisibleCutoutPixels']) for d in rotation_details},'angleOverlaps':{d['key']:len(d['opaqueHeadOccludesBodyOutsideOriginalCutMask']) for d in rotation_details},'protectedChanges':0,'seconds':time.perf_counter()-started}))
