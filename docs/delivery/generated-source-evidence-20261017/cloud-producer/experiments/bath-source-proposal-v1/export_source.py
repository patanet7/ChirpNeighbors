from pathlib import Path
from datetime import datetime,timezone
from PIL import Image,ImageDraw
import hashlib,json,math,struct,zlib,binascii,time,collections
P=Path(__file__).resolve().parent;assert not(P/'export-receipt.json').exists(),'One export only'
start=time.perf_counter();original=Image.open(P/'original.png').convert('RGBA');assert original.size==(1254,1254)
def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()
def rid(im):return 'frame.sha256.'+hashlib.sha256(('RGBA8;%dx%d;'%im.size).encode()+im.tobytes()).hexdigest()
def save(n,d):q=P/n;q.parent.mkdir(parents=True,exist_ok=True);q.write_text(json.dumps(d,indent=2)+'\n')
def png(n,im):q=P/n;q.parent.mkdir(parents=True,exist_ok=True);im.save(q)
args=json.loads((P/'native-arguments.json').read_text());assert args['prompt'].encode()==(P/'prompt.txt').read_bytes()
roles=['lowered-ready','wing-ruffle','shake-wing-state','folded-settle'];frames={};nativefacts=[]
ref=Image.open(P/'reference-neutral768.png').convert('RGBA');assert rid(ref)=='frame.sha256.168bf85942235e125601c6e245b5f2060f4a254ef2427d1f2d9adeb88ef90b81'
neutral=Image.open(P/'ancestry/selected-neutral-raw192.png').convert('RGBA');frames['neutral']=neutral;png('raw192/neutral.png',neutral)
for i,role in enumerate(roles):
 x=(i%2)*627;y=(i//2)*627;rect=(x,y,x+627,y+627);cell=original.crop(rect);png(f'cells-native/{role}.png',cell)
 # Exact common scalar center sampler, straightRGBA channelcopy.
 src=cell.tobytes();indices=[((2*j+1)*627)//384 for j in range(192)];out=bytearray(192*192*4)
 for dy,sy in enumerate(indices):
  for dx,sx in enumerate(indices):out[(dy*192+dx)*4:(dy*192+dx+1)*4]=src[(sy*627+sx)*4:(sy*627+sx+1)*4]
 im=Image.frombytes('RGBA',(192,192),bytes(out));frames[role]=im;png(f'raw192/{role}.png',im)
 assert cell.tobytes()==original.crop(rect).tobytes()
 nativefacts.append({'sourceFrameId':rid(cell),'sourcePNG':f'cells-native/{role}.png','sourcePNGsha256':sha(P/f'cells-native/{role}.png'),'speciesId':'mourning_dove','pose':role,'nativeCanvas':[627,627],'atlasSourceRect':list(rect),'drawingClass':'One actualnewnativebody/wingdrawing; cropPNG is exactwholecell primary','registration':{'method':'Literal2x2equalquadrant extraction then common wholecellcenterNN→192, nofit/crop/snap/painting','sourceCellOrigin':[x,y],'sourcePixelsPerWorldUnit':627/192,'nativeToWorldScale':192/627,'rootWorld':[105,150],'contacts':[],'physicalSupportReviewed':False},'rawWorldPNG':f'raw192/{role}.png','rawWorldPNGsha256':sha(P/f'raw192/{role}.png'),'rawWorldRGBAId':rid(im)})
assert len({x['sourceFrameId'] for x in nativefacts})==4
# Preserve exact selected neutral palette/PNG; new candidate mapping uses that existing palette, never changes body scale.
palette=sorted({tuple(x) for x in json.loads((P/'ancestry/selected-palette.json').read_text())['colors']});assert len(palette)<=63
cache={}
def mapped(c):
 rgb=c[:3]
 if rgb not in cache:cache[rgb]=min(palette,key=lambda p:(sum((p[j]-rgb[j])**2 for j in range(3)),p))
 return cache[rgb]+(255,)
codec={}
for key,im in frames.items():
 if key=='neutral':
  clean=Image.new('RGBA',(192,192));clean.paste(Image.open(P/'ancestry/selected-neutral-codec136x89.png').convert('RGBA'),(22,73))
 else:
  clean=Image.new('RGBA',(192,192));clean.putdata([(0,0,0,0) if c[3]<128 else mapped(c) for c in im.getdata()])
 codec[key]=clean;png(f'codec192/{key}.png',clean)
# Single zero-only crop across five cleaned frames. Raw source stays fullstage unchanged.
bbox=None
for im in codec.values():
 b=im.getchannel('A').getbbox();bbox=b if bbox is None else(min(b[0],bbox[0]),min(b[1],bbox[1]),max(b[2],bbox[2]),max(b[3],bbox[3]))
crop=(min(22,bbox[0]),min(73,bbox[1]),max(158,bbox[2]),max(162,bbox[3]));facts=[];metrics={}
for key,im in codec.items():
 cr=im.crop(crop);png(f'frames/{key}.png',cr);outside=im.copy();ImageDraw.Draw(outside).rectangle((crop[0],crop[1],crop[2]-1,crop[3]-1),fill=(0,0,0,0));assert not any(outside.tobytes())
 raw=frames[key];opaque=raw.getchannel('A').point(lambda a:255 if a>=128 else 0);bb=opaque.getbbox();refs={str(q):list(raw.getpixel(q)) for q in [(97,149),(116,149),(105,150)]}
 metrics[key]={'rawAlpha128BBoxWorld':list(bb),'visibleImageWidth':bb[2]-bb[0],'visibleImageHeight':bb[3]-bb[1],'lowestAlpha128RowWorld':bb[3]-1,'lowestRowDeltaVsNeutral149':bb[3]-1-149,'widthRatioVsNeutral118':(bb[2]-bb[0])/118,'interpretation':'Image extent includes different wingposes; not a biologicalbodyfit metric or sole physicalanchor. Actualnormal comparison decides matchedscale/stance.','oldFootAndRootProbeRGBA':refs,'probeQualification':'Inheritedpixels may hit body/background aftergenerateddrift; no candidatefootcontacts approved','partialRawAlphaPreserved':True}
 sourceID='frame.sha256.168bf85942235e125601c6e245b5f2060f4a254ef2427d1f2d9adeb88ef90b81' if key=='neutral' else next(n['sourceFrameId'] for n in nativefacts if n['pose']==key)
 facts.append({'id':key,'role':key,'png':f'frames/{key}.png','PNGsha256':sha(P/f'frames/{key}.png'),'decodedRGBAId':rid(cr),'rawPNG':f'raw192/{key}.png','rawPNGsha256':sha(P/f'raw192/{key}.png'),'codecFullPNG':f'codec192/{key}.png','codecFullPNGsha256':sha(P/f'codec192/{key}.png'),'sourceFrameID':sourceID,'canvas':list(cr.size),'fullStageOrigin':list(crop[:2]),'density':1,'pivot':[105-crop[0],150-crop[1]],'contacts':[],'newDrawing':key!='neutral','sourceStatus':'HELD_PENDING_INDEPENDENT_SCALE_STANCE_BODY_REVIEW' if key!='neutral' else 'Exactexistingneutralreuse'})
schedule=[('neutral',12),(roles[0],18),(roles[1],12),(roles[2],12),(roles[3],24),('neutral',12)]
def chunk(t,b):return struct.pack('>I',len(b))+t+b+struct.pack('>I',binascii.crc32(t+b)&0xffffffff)
def apng(name,ims,sch):
 w,hh=ims[0].size;out=b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',w,hh,8,6,0,0,0))+chunk(b'acTL',struct.pack('>II',len(ims),1));seq=0
 for i,(im,(key,t)) in enumerate(zip(ims,sch)):
  out+=chunk(b'fcTL',struct.pack('>IIIIIHHBB',seq,w,hh,0,0,t,30,0,0));seq+=1;raw=im.tobytes();data=zlib.compress(b''.join(b'\0'+raw[y*w*4:(y+1)*w*4] for y in range(hh)),9)
  if i==0:out+=chunk(b'IDAT',data)
  else:out+=chunk(b'fdAT',struct.pack('>I',seq)+data);seq+=1
 out+=chunk(b'IEND',b'');(P/name).write_bytes(out)
apng('raw-source-proposal.apng',[frames[k] for k,t in schedule],schedule);apng('codec-source-proposal.apng',[codec[k].crop(crop) for k,t in schedule],schedule)
# Every nativecell, raw and cleaned body key visible at original worldscale, both backgrounds.
sheet=Image.new('RGB',(5*204,2*224),'#e5e0cd');d=ImageDraw.Draw(sheet)
for j,bg in enumerate(['#e5e0cd','#182a32']):
 d.rectangle((0,j*224,1020,(j+1)*224),fill=bg)
 for i,(key,im) in enumerate(frames.items()):sheet.paste(im,(i*204+5,j*224+23),im);d.text((i*204+3,j*224+4),key,fill='black' if not j else 'white')
png('normal-raw-light-dark.png',sheet)
sheet2=sheet.copy();d=ImageDraw.Draw(sheet2)
for j,bg in enumerate(['#e5e0cd','#182a32']):
 d.rectangle((0,j*224,1020,(j+1)*224),fill=bg)
 for i,(key,im) in enumerate(codec.items()):sheet2.paste(im,(i*204+5,j*224+23),im);d.text((i*204+3,j*224+4),key,fill='black' if not j else 'white')
png('normal-codec-light-dark.png',sheet2)
save('source-measurements.json',{'referenceBodyBBoxWorld':[32,82,150,150],'referenceLowestRow':149,'perFrame':metrics,'sourceCellNormalization':'No fit applied despite returnednormalizedbody larger/lower thanrequested','renderRootConstant':[105,150],'candidateContacts':[],'bodyFeetImmersionRimOcclusion':'UNREVIEWED','rendererCaveat':'Actorpaintsabovefullbowl/water; nofrontmask. Sourcepixels do notresolveimmersion or basinfloor.','requestedVsActualAtlas':{'requested':[1536,1536],'actual':[1254,1254],'actualEqualCell':[627,627],'squareCellAspectPreserved':True}})
save('PRIMARY-SOURCE-MANIFEST.json',{'batchId':'bath-source-proposal-v1','nativeCalls':1,'original':'original.png','originalSHA256':sha(P/'original.png'),'originalRGBAId':rid(original),'prompt':'prompt.txt','promptSHA256':sha(P/'prompt.txt'),'promptBytes':len((P/'prompt.txt').read_bytes()),'nativeArguments':'native-arguments.json','argumentsSHA256':sha(P/'native-arguments.json'),'frames':nativefacts,'reusedFrames':[{'sourceFrameId':rid(ref),'sourcePNG':'reference-neutral768.png','sourcePNGsha256':sha(P/'reference-neutral768.png'),'pose':'neutral-entry-and-exit','newDrawing':False}],'sourceStatus':'HELD_MATCHED_BATH_CANDIDATE_PENDING_INDEPENDENT_REVIEW','notes':['4genuinebody/wingdrawings oneactualnativecall,0retries','No generatedneutral or newcanon','Literalnativecells/sourcepixels retained; nofit/snap/painting or root correction','Sourceclocks illustrative; bathsupport/immersion/rimrights/unreviewed','4cellPNG/RGBAIDs are primary drawingidentities; raw/codec resamples are derivatives, notadditionaldrawings'],'outputMetadata':['native-return-receipt.json','native-tool-return-metadata.json','export-receipt.json','source-handoff.json','source-measurements.json'],'sourceAdmitted':False,'runtimeAdmission':False})
save('source-handoff.json',{'kind':'Explicitbathing source-art proposal ONLY; notcommoninput5/familyadmission or live bathcapability','speciesId':'mourning_dove','nativeCalls':1,'newDrawings':4,'reusedDrawings':1,'frames':facts,'fullWorldCanvas':[192,192],'displayStage':[192,192],'density':1,'candidateCanvas':[crop[2]-crop[0],crop[3]-crop[1]],'commonCrop':list(crop),'commonCropOrigin':list(crop[:2]),'candidatePivot':[105-crop[0],150-crop[1]],'fullPivot':[105,150],'pivotMeaning':'Existing image-registration origin only; candidateanatomy/footcorrespondenceunreviewed','contacts':[],'supportWorld':None,'physicalSupportReviewed':False,'geometryScope':'image-registration-only','alphaOrigin':'upstream-cleanup forcodec only, rawRGBAretained','palette':'Exactexisting63opaque palette nearestRGB/no dither; neutralcodec byteidentical reused beforecommoncrop','clips':[{'id':'bathing-source-proposal','tickRate':30,'frames':[{'frameId':k,'durationTicks':t} for k,t in schedule],'loop':False,'qualification':'Authored3second sourceproposal, notmeasuredbiology or actualwetcontact timeline'}],'events':[{'tick':t,'event':'phase_enter','frame':k,'meaning':'Authoredsourcephasemarker only'} for t,k in zip([0,12,30,42,54,78],[k for k,t in schedule])]+[{'tick':90,'event':'complete','meaning':'Sourceclockcomplete only; notenginewetcontact'}],'waterContactEvents':[],'actorRootToSlotBinding':'NOT_APPLIED; consumerusesactualroot and reviewedsupport/pivot, neverfluidline','bodyFeetImmersionRimOcclusion':'UNREVIEWED','frontRimMask':None,'currentPaintOrder':'Actorabovefullbowl/water fromverifiedcontract; no immersionmask invented','zeroMassEffects':'Engineownedseparate; nonebaked','sourceStatus':'HELD_MATCHED_COHORT_PENDING_INDEPENDENT_NORMAL_REVIEW','runtimeAdmission':False,'sourceAdmitted':False,'rightsGranted':False,'referenceRightsAssessed':False,'newCanonicalSpecies':0})
save('native-ancestry.json',{'soleImageInput':{'file':'reference-neutral768.png','PNGsha256':sha(P/'reference-neutral768.png'),'sourceFrameID':rid(ref),'sourceCanvas':[768,768]},'literalArguments':'native-arguments.json','prompt':'prompt.txt','fullOriginalAncestor':'ancestry/drink-original.png','ancestorSHA256':sha(P/'ancestry/drink-original.png'),'historicalAncestorPrompt':'ancestry/drink-prompt.txt','historicalAncestorPromptSHA256':sha(P/'ancestry/drink-prompt.txt'),'historicalExtraction':'Existinglosslesscrop[0,0,515,512] then integertranslation106,175→768², no newsourceextractionforreference','contractReferencesAreNotGenerationImageInputs':True,'model':None,'seed':None,'noCompositeGuide':True,'rightsFacts':'Existingprojectgeneratedsourceprovenance retained, rights/clearance notnewlyverified; noCC0'} )
save('export-receipt.json',{'exportedUTC':datetime.now(timezone.utc).isoformat(),'exportPasses':1,'observedWallSeconds':time.perf_counter()-start,'nativeCalls':1,'nativeRetries':0,'newPrimaryDrawings':4,'primaryCellSize':[627,627],'wholeCellSourceRects':[x['atlasSourceRect'] for x in nativefacts],'nativeCellsExactRoundTrip':True,'wholeCanvasSampler':'floor((dst+.5)*627/192), same192square/density1 acrossall4, straightRGBAchannelcopy','sampleIndices':indices,'perPoseFitTranslationWarpPaint':False,'neutralRawExact':sha(P/'raw192/neutral.png')==sha(P/'ancestry/selected-neutral-raw192.png'),'existingNeutralCodecPreservedFullStage':True,'paletteVariants':1,'alpha128Explicit':True,'commonCrop':list(crop),'commonCropDiscardedRGBA':0,'candidateCanvas':[crop[2]-crop[0],crop[3]-crop[1]],'candidateUniqueArea':len(codec)*(crop[2]-crop[0])*(crop[3]-crop[1]),'rawUniqueArea':5*192*192,'areaIsDiagnosticActualRuntimeCheckSeparate':True,'fullRuntimeAdmission':False,'matchedScaleFeetSourceStatus':'HELD_PENDING_INDEPENDENTREVIEW','humanCleanupMinutes':None,'cleanup':'None; no painting/fit/snap; allreturnedscale/rowdriftretained'})
(P/'active-status.json').write_text(json.dumps({'state':'generated-exported-review-preparation','nativeRunning':False,'actualNativeCallsStarted':1,'actualNativeCallsReturned':1,'actualNewSourceDrawings':4,'reusedNeutral':1,'retries':0,'next':'Browser/APNGnumericproof thenfreeze independentreviews; no furthernativecall'},indent=2)+'\n')
print(json.dumps({'newNativeCalls':1,'newPrimaryDrawings':4,'actualCells':[627,627],'crop':crop,'candidateArea':len(codec)*(crop[2]-crop[0])*(crop[3]-crop[1]),'metrics':metrics,'nativeIDs':[x['sourceFrameId'] for x in nativefacts]},indent=2))
