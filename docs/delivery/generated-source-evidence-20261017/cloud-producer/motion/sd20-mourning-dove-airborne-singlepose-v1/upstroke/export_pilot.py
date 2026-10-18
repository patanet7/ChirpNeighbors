"""One native airborne pilot; zero perpose fitting or alpha cleanup."""
from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib,shutil,sys,datetime
P=Path(__file__).parent;SH=P.parent/'shared';src=Path(sys.argv[1]);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def J(n,o):(P/n).write_text(json.dumps(o,indent=2)+'\n')
def fid(im):return 'frame.sha256.'+hashlib.sha256(f'RGBA8;{im.width}x{im.height};'.encode()+im.tobytes()).hexdigest()
shutil.copyfile(src,P/'original.png');im=Image.open(P/'original.png');assert im.mode=='RGBA';w,h=im.size
r={'state':'RETURNED_ONE_NATIVE_CALL','completedReceiptUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'nativeCalls':1,'nativeRunning':False,'nativeOriginalPath':str(src),'original':'original.png','originalSHA256':sha(P/'original.png'),'nativeCanvas':[w,h],'mode':im.mode,'actualNewDrawings':1,'sourceFrameId':fid(im),'noAutomaticRetry':True,'nextCallsBlockedUntilRootFramingReview':True};J('native-return-receipt.json',r)
args=json.loads((P/'native-call-arguments.json').read_text());assert args['arguments']['prompt'].encode()==(P/'prompt.txt').read_bytes()
if w!=h:
 J('framing-gate-input.json',{'status':'HELD_NONSQUARE_NATIVE_CANVAS','nativeCanvas':[w,h],'outputExported':False,'noAspectWarpPerformed':True,'nativeCalls':1,'newDrawings':1,'nextCallsBlocked':True});print(json.dumps(r));sys.exit(0)
a=np.array(im);xs=((2*np.arange(144)+1)*w)//288;ys=((2*np.arange(144)+1)*h)//288;new=Image.fromarray(a[ys[:,None],xs[None,:]].copy(),'RGBA');new.save(P/'upstroke144x144.png');old=Image.open(SH/'exact-awake144x144.png').convert('RGBA');shutil.copyfile(SH/'exact-awake144x144.png',P/'comparison-awake144x144.png')
arr=np.array(new);oldarr=np.array(old)
def bbox(x,t):
 yy,xx=np.where(x[:,:,3]>=t);return None if not len(xx) else [int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)]
points=[[73,99],[92,99]]
measure={'oldPaddedAwakeBBoxAlpha128':bbox(oldarr,128),'newWholeWingEnvelopeBBoxAlpha128':bbox(arr,128),'oldBodyBillTailLengthReferenceWorld':118,'newBodyLengthAutomaticallyFitOrCertified':False,'wingEnvelopeIsNotBodyLength':True,'nativeCanvas':[w,h],'sourceCanvas':[144,144],'density':1,'virtualOrigin':[81,100],'virtualOriginIsGroundContact':False,'oldToeReferenceSamples':[{'point':p,'oldRGBA':oldarr[p[1],p[0]].tolist(),'newRGBA':arr[p[1],p[0]].tolist(),'meaning':'old reference pixel only, not an airborne contact'}for p in points],'newPositiveAlphaOnSourceBorder':int((arr[0,:,3]>0).sum()+(arr[-1,:,3]>0).sum()+(arr[:,0,3]>0).sum()+(arr[:,-1,3]>0).sum()),'newAlpha128OnSourceBorder':int((arr[0,:,3]>=128).sum()+(arr[-1,:,3]>=128).sum()+(arr[:,0,3]>=128).sum()+(arr[:,-1,3]>=128).sum()),'PillowTieDifferentRGBAPixels':int(np.any(np.array(im.resize((144,144),Image.Resampling.NEAREST))!=arr,axis=2).sum()),'contacts':[],'geometryReviewed':False,'supportWorld':None,'sourceFramingDecision':'PENDING_ROOT_NORMAL144_REVIEW','wholeCanvasFloorCenterByteCopy':True,'perPoseFit':False,'crop':False,'paint':False,'snap':False,'alphaCleanup':False};J('measurement-proof.json',measure)
frame={'sourceFrameId':fid(im),'sourcePNG':'original.png','sourcePNGsha256':sha(P/'original.png'),'speciesId':'mourning_dove','pose':'single airborne raised-wing/upstroke source pilot','outputPNG':'upstroke144x144.png','outputPNGsha256':sha(P/'upstroke144x144.png'),'outputDerivativeId':fid(new),'registration':{'nativeCanvas':[w,h],'outputCanvas':[144,144],'sampleIndices':'floor((dst+.5)*src/dst) exactinteger ((2*dst+1)*src)//288, straightRGBA channel copy','crop':None,'density':1,'virtualOrigin':[81,100],'contacts':[],'perPoseFit':False,'bodyTranslate':[0,0],'paint':False,'warp':False,'alphaCleanup':False}}
J('PRIMARY-SOURCE-MANIFEST.json',{'batchId':'sd20-mourning-dove-airborne-singlepose-v1-upstroke','nativeCalls':1,'newDrawings':1,'original':'original.png','originalSHA256':sha(P/'original.png'),'prompt':'prompt.txt','promptSHA256':sha(P/'prompt.txt'),'frames':[frame],'reusedFrames':[{'sourceFrameId':'frame.sha256.168bf85942235e125601c6e245b5f2060f4a254ef2427d1f2d9adeb88ef90b81','file':'comparison-awake144x144.png','PNGsha256':sha(P/'comparison-awake144x144.png'),'role':'exactoldawake padded comparison outside candidate'}],'sourceStatus':'first airborne source pilot pending root framing gate, no fullfly admission','newCanons':0,'newNeutralBlinkOrBathing':0,'plannedMaximumUniqueWingFrames':3,'plannedThreeFrameArea':62208,'currentCandidateFrames':1,'currentCandidateArea':20736,'oldAwakeOutsideCandidate':True,'contacts':[],'geometryReviewed':False,'supportWorld':None,'nextCalls':'NO second/third until root framing gate; no autoretry'})
sheet=Image.new('RGB',(288,2*166),'#d9d4bd');d=ImageDraw.Draw(sheet)
for row,bg in enumerate(['#d9d4bd','#17221f']):
 for i,(bird,label) in enumerate([(old,'EXACT AWAKE PADDED'),(new,'ONE AIRBORNE PILOT')]):
  tile=Image.new('RGBA',(144,144),bg);tile.alpha_composite(bird);sheet.paste(tile.convert('RGB'),(i*144,row*166+22));d.text((i*144+3,row*166+4),label,fill='white' if row else '#24342b')
sheet.save(P/'normal144-light-dark-comparison.png');enlarge=Image.new('RGB',(1152,602),'#d9d4bd');d=ImageDraw.Draw(enlarge)
for i,(bird,label) in enumerate([(old,'EXACT AWAKE — NO BODY RESIZE'),(new,'NATIVE AIRBORNE UPSTROKE CANDIDATE')]):
 bg=Image.new('RGBA',(144,144),'#d9d4bd');bg.alpha_composite(bird);enlarge.paste(bg.resize((576,576),Image.Resampling.NEAREST).convert('RGB'),(i*576,26));d.text((i*576+4,6),label,fill='#24342b')
enlarge.save(P/'enlarged-body-wing-comparison.png')
print(json.dumps({'nativeReturn':r,'outputPNGsha256':sha(P/'upstroke144x144.png'),'derivativeId':fid(new),'measurements':measure}))
