from pathlib import Path
from PIL import Image
import json,hashlib,shutil,time,subprocess,sys
R=Path('/workspace/asset-production');P=Path(__file__).resolve().parent;D=P/sys.argv[1]
assert not (D/'export-receipt.json').exists(),'One export per repair; no automatic alternate fit or palette.'
start=time.perf_counter();species=D.name;pre=json.loads((D/'preflight.json').read_text());ret=json.loads((D/'native-return-receipt.json').read_text());N=pre['outputWorldCanvas'][0];pivot=pre['proposedRoot']
bankbytes=(R/'frame-bank.json').read_bytes();bank={f['frameId']:f for f in json.loads(bankbytes)['frames']}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def put(p,v):p.write_text(json.dumps(v,indent=2)+'\n')
def fid(im):return 'frame.sha256.'+hashlib.sha256(f'RGBA8;{im.width}x{im.height};'.encode()+im.tobytes()).hexdigest()
def retain(path):
    path=Path(path);h=sha(path);dest=D/'lineage'/path.relative_to(R);dest.parent.mkdir(parents=True,exist_ok=True)
    if not dest.exists():shutil.copyfile(path,dest)
    assert sha(dest)==h
    return {'file':str(dest.relative_to(D)),'upstream':str(path.relative_to(R)),'SHA256':h}
lookid='frame.sha256.70314a70a0d69da644906b8375bd033bac0b2d48ac3d6192c9b39342497c0bc7' if species=='bushtit' else 'frame.sha256.a80c7fa0cefe3ebcc414b9b42e99612ed7c2a79034332c8899931895e22865b8'
records=[];seen=set();ancestorCopies=[]
def lineage(id):
    if id in seen:return
    seen.add(id);row=bank[id];source=retain(R/row['file']);orig=retain(R/row['sourceAtlas']);prompt=retain(R/row['sourcePrompt']);base=(R/row['sourceAtlas']).parent;g=base/'receipts/generation.json';reference=row.get('sourceReferenceFrameId')
    rec={'sourceFrameID':id,'registeredSource':source,'original':orig,'prompt':prompt,'bankRecord':row,'historicalRegistrationUnchanged':True}
    if g.exists():
        rec['generationReceipt']=retain(g);jg=json.loads(g.read_text());reference=jg.get('styleReferenceFrameId') or reference;rec['declaredGeneratedConditioningFrameID']=reference
    if (base/'intake-manifest.json').exists():rec['registrationManifest']=retain(base/'intake-manifest.json')
    records.append(rec)
    if reference:
        if reference in bank:lineage(reference)
        else:rec['unresolvedReferenceFrameID']=reference
lineage(pre['soleImageInput']['sourceFrameID']);lineage(lookid)
prior=[]
for old in pre['existingPoolFirst']['priorClosedStudies']:
    row=next(f for f in bank.values() if f['fileSha256']==old['PNGsha256']);entry={'sourceFrameID':row['frameId'],'nativeOriginal':retain(R/row['file']),'exactPrompt':retain(R/row['sourcePrompt']),'purpose':'Rejected prior study retained for comparison only; NOT a native input for this repair.'}
    base=(R/row['file']).parent
    for name in ['native-call-arguments.json','native-arguments.json','native-prompt-audit.json','prompt-byte-audit.json','call-status.json','native-return-receipt.json']:
        if (base/name).exists():entry[name]=retain(base/name)
    prior.append(entry)
put(D/'lineage-input-enumeration.json',{'nativeCallImageInputs':[pre['soleImageInput']],'imageInputEnumerationCompleteForThisCall':True,'historicalGeneratedSourceRecords':records,'priorRejectedAttemptsNotInputs':prior,'newCallImageInputCount':1,'noExternalImageInputsDeclaredForThisCall':True,'historicalRightsAssessment':'Importer-owned recursive history/evidence assessment remains unapproved; factual citations are not image inputs.','model':None,'seed':None,'sourceAdmitted':False,'rightsGranted':False,'generationInputsAssessed':False,'referenceRightsAssessed':False})
sourceFiles={'awake':D/'reference-awake1024.png','closed':D/'original.png','look':R/bank[lookid]['file']}
sourceIds={'awake':pre['soleImageInput']['sourceFrameID'],'closed':ret['sourceFrameID'],'look':lookid}
raw={};sourceRows=[]
(D/'raw').mkdir(exist_ok=True);(D/'codec').mkdir(exist_ok=True)
for role,path in sourceFiles.items():
    im=Image.open(path).convert('RGBA');assert fid(im)==sourceIds[role]
    out=Image.new('RGBA',(N,N));out.putdata([im.getpixel((((2*x+1)*im.width)//(2*N),((2*y+1)*im.height)//(2*N))) for y in range(N) for x in range(N)]);out.save(D/'raw'/f'{role}.png');raw[role]=out
    sourceRows.append({'role':role,'sourceFrameID':sourceIds[role],'sourcePNG':str(path.relative_to(D)) if path.is_relative_to(D) else retain(path)['file'],'sourcePNGsha256':sha(path),'nativeCanvas':list(im.size),'newDrawing':role=='closed','rawPNG':'raw/'+role+'.png','rawPNGsha256':sha(D/'raw'/f'{role}.png'),'rawDecodedRGBAId':fid(out)})
rgb=[v[:3] for im in raw.values() for v in im.getdata() if v[3]>=128];sample=Image.new('RGB',(len(rgb),1));sample.putdata(rgb);palette=sample.quantize(colors=63,method=Image.Quantize.MEDIANCUT,dither=Image.Dither.NONE);render=[];codec={}
for role,im in raw.items():
    q=im.convert('RGB').quantize(palette=palette,dither=Image.Dither.NONE).convert('RGB');out=Image.new('RGBA',(N,N));out.putdata([(*q.getpixel((x,y)),255) if im.getpixel((x,y))[3]>=128 else (0,0,0,0) for y in range(N) for x in range(N)]);out.save(D/'codec'/f'{role}.png');codec[role]=out
    render.append({'role':role,'frameId':species+'-'+role,'sourceFrameID':sourceIds[role],'png':'codec/'+role+'.png','PNGsha256':sha(D/'codec'/f'{role}.png'),'decodedRGBAId':fid(out),'canvas':[N,N],'pivot':pivot,'density':1,'contacts':[]})
clips=[{'id':'idle','tickRate':30,'loop':True,'roles':['awake'],'durationTicks':[60],'qualification':'Authored static projection from the existing idle/look schedule.'},{'id':'blink','tickRate':30,'loop':False,'roles':['awake','closed','awake'],'durationTicks':[60,3,27]},{'id':'look','tickRate':30,'loop':False,'roles':['awake','look','awake'],'durationTicks':[60,6,24],'qualification':'Existing generated look and inherited old idle/look clocks, no new look drawing.'}]
for kind,images in [('raw',raw),('codec',codec)]:
    for clip in clips[1:]:
        seq=[images[x] for x in clip['roles']];seq[0].save(D/(kind+'-'+clip['id']+'.apng'),save_all=True,append_images=seq[1:],duration=[x*1000/30 for x in clip['durationTicks']],disposal=1,blend=0,loop=1,optimize=False)
h={'kind':'project-generated source producer facts; not admitted input5 or private evidence/pin authority','speciesId':species,'newNativeCalls':1,'newDrawings':1,'newNeutralDrawings':0,'newLookDrawings':0,'sourceBankUnchangedSHA256':hashlib.sha256(bankbytes).hexdigest(),'sourceFrames':sourceRows,'frames':render,'clips':clips,'fullWorldCanvas':[N,N],'displayStage':[N,N],'candidateCanvas':[N,N],'commonCrop':[0,0,N,N],'commonCropOrigin':[0,0],'density':1,'fullPivot':pivot,'candidatePivot':pivot,'contacts':[],'geometryScope':'image-registration-only','geometryReviewed':False,'physicalSupportReviewed':False,'supportWorld':None,'alphaOrigin':'upstream-cleanup','alphaCleanup':'Binary alpha128, transparentRGBA0, one common63opaqueRGB palette across awake/closed/existinglook; no dithering. Raw RGBA separately retained.','registration':'One whole-native-canvas floor-center NN mapping per dimension to the fixed target canvas; identical full crop/root, no per-pose fit, translation, paint or snap.','legacyWorldQualification':'Bushtit64 is exact legacy world. Oriole141 is the existing readability-study canvas, versus legacy140.8 (+0.14204545%); fixed globally, never fitted to a bird envelope.','sourceAcceptance':'pending frozen independent normal-size blink review','sourceAdmitted':False,'rightsGranted':False,'generationInputsAssessed':False,'referenceRightsAssessed':False,'runtimeAdmission':False,'privateBindings':None}
put(D/'family-handoff.json',h)
put(D/'PRIMARY-SOURCE-MANIFEST.json',{'batchId':'resting-repair-'+species+'-blink','nativeCalls':1,'original':'original.png','originalSHA256':ret['originalSHA256'],'prompt':'prompt.txt','promptSHA256':sha(D/'prompt.txt'),'frames':[sourceRows[1]],'reusedFrames':[sourceRows[0],sourceRows[2]],'generationRecord':'generation-record.json','inputEnumeration':'lineage-input-enumeration.json','sourceStatus':'generated candidate; useful blink not assumed','outputMetadata':['family-handoff.json','export-receipt.json']})
put(D/'export-receipt.json',{'state':'one export complete, independent review pending','exportWallSeconds':time.perf_counter()-start,'newNativeCalls':0,'generationCallsElsewhereInThisTarget':1,'newDrawingsFromExport':0,'canvas':[N,N],'commonCrop':[0,0,N,N],'pivot':pivot,'zeroCropDiscard':True,'visibleScaleFit':False,'nativeFrameCanvas':ret['sourceCanvas'],'sampler':'sx=floor((2*x+1)*nativeWidth/(2*targetWidth)); sy analogous; direct straightRGBA channel copy','partialAlphaSourcePreserved':True,'commonPaletteAcross3Frames':True,'sourceFrameIDs':sourceIds,'normalSizeReadability':'unreviewed','legacyWorld':64 if species=='bushtit' else 140.8,'studyWorld':N})
print(json.dumps({'species':species,'canvas':[N,N],'sources':3,'newDrawings':1,'handoffSHA256':sha(D/'family-handoff.json'),'nativeOriginal':ret['originalSHA256']}))
