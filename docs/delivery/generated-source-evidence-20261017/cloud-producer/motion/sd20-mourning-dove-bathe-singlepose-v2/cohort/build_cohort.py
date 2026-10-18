"""Uniform cohort derivative exporter; never calls imagegen or edits sibling packets."""
from pathlib import Path
from PIL import Image,ImageDraw,__version__ as pillow_version
import numpy as np,json,hashlib,shutil,struct,zlib,datetime,re
P=Path(__file__).parent;B=P.parent;SH=B/'shared';PHASES=['approach','settle','dip','wingflutter','shake','exit-preen'];TICKS=[18,18,12,18,12,24]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def J(n,v):p=P/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2)+'\n')
def fid(im):return 'frame.sha256.'+hashlib.sha256(f'RGBA8;{im.width}x{im.height};'.encode()+im.tobytes()).hexdigest()
def safe(p):
 try:t=p.read_text()
 except UnicodeDecodeError:return True
 return not re.search(r'libfile_[a-f0-9]{32}|data:image/[^;]+;base64,|https?://[^\s\"<>]*(?:X-Amz-|sig=|token=)',t,re.I)
def bbox(a,k):
 y,x=np.where(a[:,:,3]>=k);return None if len(x)==0 else [int(x.min()),int(y.min()),int(x.max()+1),int(y.max()+1)]
contract=json.loads((SH/'reference-contract.json').read_text());assert contract['runtimeCrop144']==[4,8,140,88] and contract['runtimePivot']==[77,76]
(P/'reference').mkdir(exist_ok=True)
for n in ['reference-contract.json','exact-awake144x96.png','exact-awake136x80.png','conditioning-awake576x384.png']:
 assert safe(SH/n);shutil.copyfile(SH/n,P/'reference'/n)
rows=[];status=[];frozen=[];inputs=[];images=[]
for phase,ticks in zip(PHASES,TICKS):
 S=B/phase;original=S/'original.png';receipt=S/'native-return-receipt.json'
 if not original.exists() or not receipt.exists():
  status.append({'phase':phase,'state':'WAITING_NATIVE_SOURCE','sourceOriginalAvailable':original.exists(),'nativeReturnReceiptAvailable':receipt.exists(),'cohortExported':False});continue
 r=json.loads(receipt.read_text());assert sha(original)==r['originalSHA256'],phase
 im=Image.open(original);assert im.mode=='RGBA' and im.size==(1536,1024),(phase,im.mode,im.size)
 canonical=fid(im);reported_ids=[];reported_rgba_sha=None
 if (S/'source-manifest.json').exists():reported_rgba_sha=json.loads((S/'source-manifest.json').read_text()).get('original',{}).get('RGBAsha256')
 if (S/'PRIMARY-SOURCE-MANIFEST.json').exists():
  primary=json.loads((S/'PRIMARY-SOURCE-MANIFEST.json').read_text());reported_ids=[x.get('sourceFrameId') for x in primary.get('frames',[]) if x.get('sourceFrameId')]
 # Floor-center nearest using exact integer arithmetic equivalent to floor((d+.5)*src/dst).
 a=np.array(im);xs=((2*np.arange(144)+1)*1536)//(2*144);ys=((2*np.arange(96)+1)*1024)//(2*96);small=a[ys[:,None],xs[None,:]].copy();cropped=small[8:88,4:140].copy();whole=Image.fromarray(small,'RGBA');frame=Image.fromarray(cropped,'RGBA')
 fp=P/'frames';fp.mkdir(exist_ok=True);wn=f'frames/{phase}144x96.png';cn=f'frames/{phase}136x80.png';whole.save(P/wn);frame.save(P/cn)
 # Producer derivatives are retained untouched and compared; they are never inputs to this cohort.
 comparisons=[]
 for suffix,generated in [('144x96',small),('136x80',cropped)]:
  old=S/f'{phase}{suffix}.png'
  if old.exists():
   oldim=Image.open(old).convert('RGBA');ob=np.array(oldim);comparisons.append({'siblingProducerExport':str(old.relative_to(B)),'sha256':sha(old),'sameSize':ob.shape==generated.shape,'differentRGBAPixels':int(np.any(ob!=generated,axis=2).sum()) if ob.shape==generated.shape else None,'producerBytesPreserved':True})
 sp=P/'sources'/phase;sp.mkdir(parents=True,exist_ok=True);retained=[];excluded=[]
 for n in ['original.png','prompt.txt','native-call-arguments.json','native-return-receipt.json','call-dispatch-receipt.json','export-attempt-failure-receipt.json','export-verification.json','reference-contract.json','PRIMARY-SOURCE-MANIFEST.json','review-target-hashes.json','STABLE-GO.json','source-files.sha256.json','FROZEN-SOURCE-INPUTS.json','source-manifest.json','README.md','approach-framing-gate.json','producer-verdict.json','measurement-proof.json',phase+'-key.json']:
  f=S/n
  if not f.exists():continue
  if not safe(f):excluded.append({'file':n,'sha256':sha(f),'reason':'unsafe private handle/signedURL/embedded image payload; source retained in sibling only'});continue
  shutil.copyfile(f,sp/n);retained.append({'file':str((sp/n).relative_to(P)),'sha256':sha(sp/n)});inputs.append({'originalSiblingPath':str(f.relative_to(B)),'sha256':sha(f)})
 args=S/'native-call-arguments.json'
 if args.exists() and (S/'prompt.txt').exists():
  native=json.loads(args.read_text());prompt=native.get('arguments',{}).get('prompt',native.get('prompt'))
  if prompt is not None:assert prompt.encode()==(S/'prompt.txt').read_bytes(),phase+' prompt mismatch'
 freeze_paths=[]
 if (S/'STABLE-GO.json').exists():
  for n in ['review-target-hashes.json','source-files.sha256.json']:
   if (S/n).exists():freeze_paths.append(S/n)
 if (S/'FROZEN-SOURCE-INPUTS.json').exists():freeze_paths.append(S/'FROZEN-SOURCE-INPUTS.json')
 stable=bool(freeze_paths)
 for ledger in freeze_paths:
  l=json.loads(ledger.read_text());l=l.get('files',l) if isinstance(l,dict) else l
  pairs=[(x['file'],x['sha256']) for x in l] if isinstance(l,list) else list(l.items())
  for n,h in pairs:assert sha(S/n)==h,phase+'/'+n
 if stable:frozen.append(phase)
 removed=small.copy();removed[8:88,4:140]=0
 row={'phase':phase,'sourceFrameId':canonical,'reportedProducerSourceFrameIds':reported_ids,'reportedIdsMatchRawNative':canonical in reported_ids,'producerReportedRawRGBAsha256':reported_rgba_sha,'actualRawRGBAbytesSHA256':hashlib.sha256(im.tobytes()).hexdigest(),'producerRawRGBAhashMatches':None if reported_rgba_sha is None else reported_rgba_sha==hashlib.sha256(im.tobytes()).hexdigest(),'identityReconciliation':'Canonical drawing identity is independently decoded raw native RGBA8;WxH;+bytes. Producer reported IDs retained separately; cohort derivatives never new drawings.','sourcePNG':f'sources/{phase}/original.png','sourcePNGsha256':sha(original),'nativeCanvas':[1536,1024],'newDrawing':False,'nativeCallsByExporter':0,'canonicalSourceFromNativeOriginal':True,'wholeCanvasPNG':wn,'wholeCanvasPNGsha256':sha(P/wn),'outputPNG':cn,'outputPNGsha256':sha(P/cn),'derivativeDecodedRGBAId':fid(frame),'derivativeIsNewSourceDrawing':False,'renderFrameId':'dove-bath-'+phase+'-136x80','durationTicks':ticks,'canvas':[136,80],'pivot':[77,76],'density':1,'contacts':[],'sourceStableGO':stable,'copiedSourceReceipts':retained,'excludedMetadata':excluded,'sourcePositiveAlphaRemovedByFixedCrop':int((removed[:,:,3]>0).sum()),'sourceAlpha128RemovedByFixedCrop':int((removed[:,:,3]>=128).sum()),'whole144BBoxAlpha128':bbox(small,128),'cohort136BBoxAlpha128':bbox(cropped,128),'lowestAlpha128Row':None if bbox(cropped,128) is None else bbox(cropped,128)[3]-1,'producerExportComparison':comparisons,'PillowNearestDifferentRGBAPixels144':int(np.any(np.array(im.resize((144,96),Image.Resampling.NEAREST))!=small,axis=2).sum())}
 rows.append(row);images.append(frame);status.append({'phase':phase,'state':'EXPORTED_SOURCE_FROZEN' if stable else 'EXPORTED_AWAITING_PRODUCER_FREEZE','sourceOriginalAvailable':True,'nativeReturnReceiptAvailable':True,'cohortExported':True,'sourceFrameId':canonical,'sourceStableGO':stable})
complete=len(rows)==6;frozenall=complete and len(frozen)==6
J('source-intake-status.json',{'updatedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'nativeCallsByCohort':0,'newDrawingsByCohort':0,'expectedPhases':6,'actualNativeOriginalsAvailable':len(rows),'actualCohortExports':len(rows),'sourcePhasesFrozen':frozen,'allSixPresent':complete,'allSixSourceFrozen':frozenall,'states':status,'status':'COMPLETE_SOURCES_AWAITING_COHORT_REVIEW' if frozenall else 'INCOMPLETE_OR_WAITING_PRODUCER_FREEZE'})
J('COHORT-SOURCE-MANIFEST.json',{'batchId':B.name+'-cohort','nativeCalls':0,'newDrawings':0,'sourceCount':len(rows),'sourceNativeCallReceipts':len(rows),'expectedSourceCount':6,'canonicalOriginalIDsRetained':True,'frames':rows,'reusedAwakeComparison':{'sourceFrameId':'frame.sha256.168bf85942235e125601c6e245b5f2060f4a254ef2427d1f2d9adeb88ef90b81','file':'reference/exact-awake136x80.png','sha256':sha(P/'reference/exact-awake136x80.png'),'outsideCandidateAnimation':True},'normalization':{'nativeSize':[1536,1024],'wholeCanvasTarget':[144,96],'indices':'floor((dstIndex+.5)*sourceDimension/destinationDimension), computed as ((2*dstIndex+1)*sourceDimension)//(2*destinationDimension)','channelCopy':'straight RGBA source bytes; no premultiply','commonCrop':[4,8,140,88],'outputCanvas':[136,80],'density':1,'pivot':[77,76],'perPoseFit':False,'warp':False,'paint':False,'snap':False,'alphaCleanup':False},'candidateAnimationArea':6*136*80,'awakeExcludedFromCandidateArea':True,'allSixPresent':complete,'allSourcesFrozen':frozenall,'batheSlotAccepted':False,'supportReviewed':False,'geometryReviewed':False,'supportWorld':None,'currentMacAdmission':False})
frames=[{'id':r['renderFrameId'],'PNG':r['outputPNG'],'PNGsha256':r['outputPNGsha256'],'sourceFrameId':r['sourceFrameId'],'derivativeDecodedRGBAId':r['derivativeDecodedRGBAId'],'canvas':{'width':136,'height':80},'pivot':{'x':77,'y':76},'sourcePixelsPerWorldUnit':1,'contacts':[]} for r in rows]
schedule=[{'phase':phase,'frameId':'dove-bath-'+phase+'-136x80','durationTicks':t,'available':any(r['phase']==phase for r in rows)} for phase,t in zip(PHASES,TICKS)]
J('cohort-behavior-proposal.json',{'kind':'source-only bath six-phase cohort proposal','complete':complete,'allSourceFrozen':frozenall,'frames':frames,'candidateBitmapFiles':[r['outputPNG'] for r in rows],'candidateCanvas':[136,80],'candidateFrameCountExpected':6,'candidateDecodedAnimationArea':65280,'clips':[{'id':'bathe','tickRate':30,'loop':False,'frames':schedule}] if complete else [],'plannedSchedule':schedule,'bodyRootTrajectory':{'type':'static','root':[77,76],'translation':[0,0],'wholeSpriteBobbing':False},'comparisonOutro':{'outsideCandidateAsset':True,'file':'reference/exact-awake136x80.png','holdTicks':30,'countedInCandidateArea':False},'illustrativeEvents':{'waterlineY':70,'floorY':76,'proposalOnly':True,'actualWaterContactMeasured':False},'contacts':[],'geometryReviewed':False,'supportWorld':None,'batheSlotAccepted':False,'runtimeFullSchema':'NOT_RUN','currentMacAdmission':False,'activation':'none','packetBindingReady':False,'timing':'authored one-shot, not verified biology','sourceArtIsRealPhaseKeys':True})
# Preview sheet shows missing slots explicitly; no fabricated poses fill absent phases.
sheet=Image.new('RGB',(136*3,104*4),'#d9d4bd');dr=ImageDraw.Draw(sheet)
for bgrow,bg in enumerate(['#d9d4bd','#17221f']):
 for i,phase in enumerate(PHASES):
  x=(i%3)*136;y=(bgrow*2+i//3)*104;dr.rectangle((x,y,x+135,y+103),fill=bg);dr.text((x+3,y+3),phase,fill='white' if bgrow else '#24342b');row=next((r for r in rows if r['phase']==phase),None)
  if row:
   tile=Image.new('RGBA',(136,80),bg);tile.alpha_composite(Image.open(P/row['outputPNG']).convert('RGBA'));sheet.paste(tile.convert('RGB'),(x,y+22))
  else:dr.text((x+5,y+50),'SOURCE NOT RETURNED',fill='white' if bgrow else '#24342b')
sheet.save(P/'normal-light-dark-phase-sheet.png')
J('source-input-protection.json',{'siblingsReadOnly':True,'files':inputs,'sharedReferenceContractSHA256':sha(SH/'reference-contract.json')})
# Candidate animation previews are only emitted when all SIX actual native sources exist.
if complete:
 def chunk(k,data):return struct.pack('>I',len(data))+k+data+struct.pack('>I',zlib.crc32(k+data)&0xffffffff)
 png=b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',136,80,8,6,0,0,0))+chunk(b'acTL',struct.pack('>II',6,1));seq=0
 for i,(im,ticks) in enumerate(zip(images,TICKS)):
  png+=chunk(b'fcTL',struct.pack('>IIIIIHHBB',seq,136,80,0,0,ticks,30,0,0));seq+=1;a=np.array(im);data=zlib.compress(b''.join(b'\0'+a[row].tobytes() for row in range(80)),9)
  if i==0:png+=chunk(b'IDAT',data)
  else:png+=chunk(b'fdAT',struct.pack('>I',seq)+data);seq+=1
 (P/'six-phase-candidate.apng').write_bytes(png+chunk(b'IEND',b''));g=[]
 for im in images:
  bg=Image.new('RGBA',im.size,'#d9d4bd');bg.alpha_composite(im);g.append(bg.convert('RGB'))
 g[0].save(P/'Six-Phase-Candidate.gif',save_all=True,append_images=g[1:],duration=[t*1000//30 for t in TICKS],optimize=False)
print(json.dumps({'sources':len(rows),'frozenPhases':frozen,'allSixPresent':complete,'newDrawingsByExporter':0,'nativeCallsByExporter':0,'missing':[x['phase'] for x in status if not x['cohortExported']]}))
