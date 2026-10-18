from pathlib import Path
from PIL import Image
import sys,json,hashlib,datetime,shutil
P=Path(__file__).resolve().parent
species=sys.argv[1];meta=json.loads(sys.argv[2]);D=P/species
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def put(p,v):p.write_text(json.dumps(v,indent=2)+'\n')
assert not (D/'native-return-receipt.json').exists()
f=json.loads((D/'preflight.json').read_text());dispatch=json.loads((D/'dispatch-receipt.json').read_text())
if meta.get('error'):
    put(D/'native-error-receipt.json',{'state':'native-request-failed','error':meta['error'],'actualInvocationUTC':dispatch['actualInvocationUTC'],'returnUTC':meta['returnUTC'],'toolAwaitWallMilliseconds':meta['elapsedMs'],'nativeCallsStarted':1,'nativeCallsReturned':0,'automaticRetries':0})
    state='failed'
else:
    original=Path(meta['path']);shutil.copyfile(original,D/'original.png');im=Image.open(D/'original.png').convert('RGBA');fid='frame.sha256.'+hashlib.sha256(f'RGBA8;{im.width}x{im.height};'.encode()+im.tobytes()).hexdigest()
    rec={'state':'generated-source-candidate-not-reviewed','nativeCallsStarted':1,'nativeCallsReturned':1,'automaticRetries':0,'actualInvocationUTC':dispatch['actualInvocationUTC'],'returnUTC':meta['returnUTC'],'toolAwaitWallMilliseconds':meta['elapsedMs'],'nativeServiceMilliseconds':None,'serviceTimingQualification':'The tool exposes no separate provider-service duration; await wall time includes tool overhead.','original':'original.png','originalSHA256':sha(D/'original.png'),'sourceCanvas':[im.width,im.height],'sourceFrameID':fid,'decodedMode':'RGBA8','alphaExtrema':list(im.getchannel('A').getextrema()),'toolOriginalRetained':True,'toolOriginalByteExact':original.read_bytes()==(D/'original.png').read_bytes(),'toolOriginalPathOmittedFromPortableReceipt':True,'generatedImageDisplayed':True,'promptSHA256':sha(D/'prompt.txt'),'nativeArgumentsSHA256':sha(D/'native-arguments.json'),'referenceSHA256':sha(D/'reference-awake1024.png'),'model':None,'seed':None,'newNeutralDrawings':0,'sourceUsefulBlinkSlots':None,'sourceAdmitted':False,'rightsGranted':False,'generationInputsAssessed':False,'referenceRightsAssessed':False}
    put(D/'native-return-receipt.json',rec)
    put(D/'generation-record.json',{'generator':'OpenAI image_gen.imagegen','original':'original.png','originalSHA256':rec['originalSHA256'],'sourceFrameID':fid,'prompt':'prompt.txt','promptSHA256':rec['promptSHA256'],'nativeArguments':'native-arguments.json','nativeArgumentsSHA256':rec['nativeArgumentsSHA256'],'generationReceipt':'native-return-receipt.json','generationReceiptSHA256':sha(D/'native-return-receipt.json'),'model':None,'seed':None,'imageInputs':[{'file':'reference-awake1024.png','SHA256':rec['referenceSHA256'],'sourceFrameID':f['soleImageInput']['sourceFrameID'],'upstreamPath':f['soleImageInput']['upstream'],'kind':'retained project-generated source, not an external photograph'}],'imageInputEnumerationCompleteForThisCall':True,'factualCitationsAreNotImageInputs':True,'newNativeCalls':1,'automaticRetries':0,'conditioningAncestry':'Retained source bank record, original atlas and historical prompt; recursive importer lineage recovery required. No private declarations or rights asserted.'})
    state='generated'
put(D/'active-status.json',{'updatedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'state':state,'requestInFlight':False,'nativeCallsStarted':1,'nativeCallsReturned':0 if state=='failed' else 1,'automaticRetries':0,'nextQueued':'One source export and independent frozen review; no additional native request for this target.'})
active=json.loads((P/'active-status.json').read_text());active['targets'][species]=state;active.update({'updatedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'state':state,'requestInFlight':False,'nativeRequestsInFlight':0});put(P/'active-status.json',active)
print(json.dumps({'species':species,'state':state,**({k:rec[k] for k in ['originalSHA256','sourceFrameID','sourceCanvas','toolAwaitWallMilliseconds']} if state!='failed' else {})}))
