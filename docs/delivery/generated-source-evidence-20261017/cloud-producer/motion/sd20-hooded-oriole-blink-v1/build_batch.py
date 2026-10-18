from pathlib import Path
from PIL import Image,ImageDraw
import hashlib,json,copy,numpy as np
P=Path(__file__).parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
J=lambda n:json.loads((P/n).read_text())
def put(n,o):(P/n).write_text(json.dumps(o,indent=2)+'\n')
def fid(im):return 'frame.sha256.'+hashlib.sha256(f'RGBA8;{im.width}x{im.height};'.encode()+im.tobytes()).hexdigest()
oldSource=Image.open(P/'reused-awake-source1024.png');native=Image.open(P/'closed-native.png');awake=Image.open(P/'reused-awake192.png');closed=native.resize((192,192),Image.Resampling.NEAREST);closed.save(P/'closed192.png');ims=[awake,closed];d=15/11
assert awake.tobytes()==oldSource.resize((192,192),Image.Resampling.NEAREST).tobytes()
at=Image.new('RGBA',(384,192));at.paste(awake,(0,0));at.paste(closed,(192,0));at.save(P/'blink-atlas192.png')
base=J('existing-idle-look-manifest-reference.json');frames=[copy.deepcopy(base['frames'][0]),copy.deepcopy(base['frames'][0])];frames[1]['id']='hooded_oriole-closed-blink-study-192';frames[1]['sourceRect']['x']=192
# Existing coordinate samples are provisional source review points, not physical or bilateral support acceptance.
contactAlpha=[[im.getpixel((c['x'],c['y']))[3] for c in frames[0]['contacts']] for im in ims]
if not all(contactAlpha[1]):frames[1]['contacts']=[]
clips=[{'id':'idle','tickRate':30,'loop':True,'frames':[{'frameId':frames[0]['id'],'durationTicks':60}]},{'id':'blink','tickRate':30,'loop':True,'frames':[{'frameId':frames[0]['id'],'durationTicks':60},{'frameId':frames[1]['id'],'durationTicks':3},{'frameId':frames[0]['id'],'durationTicks':27}]}]
profile={'schemaVersion':1,'profile':'chirp-texture-review-v1','scope':'review-only','approval':'unreviewed','activation':'none','source':{'sha256':sha(P/'blink-atlas192.png'),'creator':'Chirp bounded eyelid-only native edit exporter','tool':'Native image_gen;wholecanvas RGBA nearest output','toolVersion':'Native model not exposed;Pillow'+Image.__version__,'rights':'unreviewed','fidelity':'unreviewed'},'atlas':{'width':384,'height':192,'alpha':'straight-rgba8','colorSpace':'srgb'},'frames':frames,'clips':clips};put('texture-review-manifest.json',profile)
rows=[{'sourceFrameId':fid(native),'sourcePNG':'closed-native.png','sourcePNGsha256':sha(P/'closed-native.png'),'speciesId':'hooded_oriole','pose':'closed-eyelid-blink-study','outputPNG':'closed192.png','outputPNGsha256':sha(P/'closed192.png'),'newDrawing':True,'registration':{'nativeCanvas':list(native.size),'referenceCanvas':[1024,1024],'outputCanvas':[192,192],'wholeNativeToReferenceScale':1024/native.width,'directNativeToOutputScale':192/native.width,'integerOriginTranslation':[0,0],'perPoseFit':False,'snap':False,'paint':False,'warp':False,'alphaCleanup':False}},{'sourceFrameId':fid(oldSource),'sourcePNG':'reused-awake-source1024.png','sourcePNGsha256':sha(P/'reused-awake-source1024.png'),'speciesId':'hooded_oriole','pose':'exact-existing-awake','outputPNG':'reused-awake192.png','outputPNGsha256':sha(P/'reused-awake192.png'),'newDrawing':False,'registration':{'sourceCanvas':[1024,1024],'outputCanvas':[192,192],'method':'Exact existing primary and export reuse; fullcanvas192NN','originIntake':'conditioning-provenance.json#/originIntake','sourceLineageQualification':'Existing alpha>=2 component ownership and integer translation derivative; not oldnative originalRGBA. Exact reusedsource unchanged.'}}]
primary={'batchId':P.name,'nativeCalls':1,'original':'original.png','originalSHA256':sha(P/'original.png'),'prompt':'prompt.txt','promptSHA256':sha(P/'prompt.txt'),'frames':[rows[0]],'reusedFrames':[rows[1]],'newNeutralDrawings':0,'newLookDrawings':0,'newClosureDrawings':1,'outputMetadata':['texture-review-manifest.json','frame-to-action-map.json','body-contact-measurements.json','producer-review.json','verification.json'],'sourceStatus':'HELD producer precaution pending independent yard-scale blink/body/feet review; stance redraw retained','notes':['One real eyelidclosure;exact existing awake unchanged;no newneutral/look.','Native1024request returned1254;one declared wholecanvas192NN conversion,not perposefit.','Ownidle60ticks preserves existing firstneutralhold;blink separate60/3/27 authoredticks.','Nativeoriginal/allnativeRGBAalpha retained;export no cleanup/recolor/painting.','No retries,worldsupport or appbinding.']};put('PRIMARY-SOURCE-MANIFEST.json',primary)
ordered=[rows[1],rows[0]];mapping={'batchId':P.name,'speciesId':'hooded_oriole','renderClipId':'blink','newNeutralDrawings':0,'newLookDrawings':0,'newSourceHeld':True,'manifest':{'file':'texture-review-manifest.json','sha256':sha(P/'texture-review-manifest.json'),'profile':'chirp-texture-review-v1'},'atlasBinding':{'file':'blink-atlas192.png','sha256':sha(P/'blink-atlas192.png'),'width':384,'height':192,'alpha':'straight-rgba8'},'sourceToRenderFrames':[{'primarySourceFrameId':s['sourceFrameId'],'primarySourcePNG':s['sourcePNG'],'primarySourcePNGsha256':s['sourcePNGsha256'],'newDrawing':s['newDrawing'],'renderFrameId':f['id'],'outputPNG':s['outputPNG'],'outputPNGsha256':s['outputPNGsha256'],'atlasRect':f['sourceRect']} for s,f in zip(ordered,frames)],'clips':clips,'baselineNeutralFirstHoldTicks':60,'originalNeutralLookProfileUntouched':True,'canonicalZodValidation':'NOT_RUN','canonicalSharpAdmission':'NOT_RUN','currentMacNamedBlinkContract':'UNKNOWN','packetBindingReady':False,'appBound':False};put('frame-to-action-map.json',mapping)
arrays=[np.array(im) for im in ims];boxes=[];feet=[]
for a in arrays:
 y,x=np.where(a[:,:,3]>=128);boxes.append([int(x.min()),int(y.min()),int(x.max()+1),int(y.max()+1)]);parts=[]
 for roi in [(100,136,118,157),(118,136,138,157)]:
  x0,y0,x1,y1=roi;y,x=np.where(a[y0:y1,x0:x1,3]>=128);parts.append({'roi':list(roi),'lowestRow':int(y.max()+y0),'centroid':[float(x.mean()+x0),float(y.mean()+y0)]})
 feet.append(parts)
cent=max(float(np.linalg.norm(np.array(x['centroid'])-y['centroid'])) for x,y in zip(feet[0],feet[1]));base=max(abs(x['lowestRow']-y['lowestRow']) for x,y in zip(feet[0],feet[1]));regions={}
for name,roi in [('eye',[122,90,135,100]),('head',[121,85,148,105]),('body-wing',[80,103,133,138]),('tail',[53,123,105,153]),('feet',[100,136,138,157])]:
 x0,y0,x1,y1=roi;a,b=[im[y0:y1,x0:x1] for im in arrays];aa=a[:,:,3]>=128;bb=b[:,:,3]>=128;regions[name]={'roi':roi,'changedRGBApixels':int(np.any(a!=b,axis=2).sum()),'alpha128SilhouetteIoU':float((aa&bb).sum()/max(1,(aa|bb).sum()))}
put('body-contact-measurements.json',{'sourceCanvases':[[1024,1024],list(native.size)],'outputCanvas':[192,192],'density':d,'worldCanvas':[140.8,140.8],'pivot':[114,150],'contacts':frames[0]['contacts'],'contactAlphaByFrame':contactAlpha,'newFrameContacts':frames[1]['contacts'],'contactMeaning':'Inherited positive toe/foot-region comparison probes only;not certified bilateral soles or supportWorld.','bboxAlpha128':boxes,'footProxies':feet,'maxFootLowestRowChangeOutputPx':base,'maxFootLowestRowChangeWorld':base/d,'maxFootCentroidChangeOutputPx':cent,'maxFootCentroidChangeWorld':cent/d,'regionalRedraw':regions,'metricsLimits':'FixedROIs not anatomical segmentation;outside-eye redraw retained,not an automatic equality approvalgate.','producerDisposition':'HELD pending independent actual140.8CSS playback due toe/claw redraw;no automatic retry'})
# Preserve exact RGBA previews at output and rounded yard canvas; all are generated-art derivatives, not browser screenshots.
seq=[awake,closed,awake];dur=[2000,100,900];seq[0].save(P/'blink-preview.apng',save_all=True,append_images=seq[1:],duration=dur,loop=0,disposal=0,blend=0)
yardSeq=[x.resize((141,141),Image.Resampling.NEAREST) for x in seq];yardSeq[0].save(P/'blink-yard141.apng',save_all=True,append_images=yardSeq[1:],duration=dur,loop=0,disposal=0,blend=0)
gif=[]
for im in yardSeq:
 pane=Image.new('RGBA',(282,141))
 for i,color in enumerate(['#dfdac7','#172823']):
  bg=Image.new('RGBA',(141,141),color);bg.alpha_composite(im);pane.paste(bg,(141*i,0))
 gif.append(pane.convert('RGB'))
gif[0].save(P/'Oriole-Blink-Yard-Light-Dark.gif',save_all=True,append_images=gif[1:],duration=dur,loop=0,disposal=2)
sheet=Image.new('RGB',(650,410),'#e9e4d3');dr=ImageDraw.Draw(sheet)
for i,im in enumerate(ims):
 x=i*325;dr.text((x+5,5),['EXACT oldawake','NEW closed study;redraw retained'][i],fill='#233b31')
 for j,bgcol in enumerate(['#dfdac7','#172823']):
  bg=Image.new('RGBA',(141,141),bgcol);bg.alpha_composite(im.resize((141,141),Image.Resampling.NEAREST));sheet.paste(bg.convert('RGB'),(x+5+j*155,25))
 eye=im.crop((121,88,137,102)).resize((160,140),Image.Resampling.NEAREST);bg=Image.new('RGBA',eye.size,'#dfdac7');bg.alpha_composite(eye);sheet.paste(bg.convert('RGB'),(x+5,190));dr.text((x+5,338),'192eye crop10x;not a new drawing',fill='#233b31')
dr.text((5,380),'PNG yardcanvas rounded141px;exactHTML140.8CSS. Nativeallalpha retained;no recolor/threshold.',fill='#233b31');sheet.save(P/'light-dark-normal-size.png')
for name,roi,scale in [('eye-feather-closeup',(121,88,137,102),16),('feet-closeup',(98,133,139,155),10)]:
 crops=[im.crop(roi).resize(((roi[2]-roi[0])*scale,(roi[3]-roi[1])*scale),Image.Resampling.NEAREST) for im in ims];sheet=Image.new('RGBA',(crops[0].width*2+20,crops[0].height+40),'#dfdac7');dr=ImageDraw.Draw(sheet)
 for i,crop in enumerate(crops):sheet.alpha_composite(crop,(i*(crop.width+20),30));dr.text((i*(crop.width+20)+4,5),['EXACT oldawake','NEWclosure;unwarped'][i],fill='#243d31')
 sheet.save(P/(name+'.png'))
# Source-level eye crops use the same wholecanvas coordinate ratio only; no perpose anatomical fit.
roi=[650,470,720,545];crops=[]
for im in [oldSource,native]:
 r=[round(v*im.width/1024) for v in roi];crops.append(im.crop(r).resize((280,300),Image.Resampling.NEAREST))
sheet=Image.new('RGBA',(580,340),'#dfdac7');dr=ImageDraw.Draw(sheet)
for i,im in enumerate(crops):sheet.alpha_composite(im,(i*300,30));dr.text((i*300+5,5),['Awake source eye','Closed source eye'][i],fill='#243d31')
sheet.save(P/'source-eye-comparison.png')
alpha=[]
for name in ['reused-awake-source1024.png','original.png','reused-awake192.png','closed192.png']:
 a=np.array(Image.open(P/name));aa=a[:,:,3];red=(a[:,:,0]>200)&(a[:,:,1]<70)&(a[:,:,2]<70)&(aa>0);u,c=np.unique(aa[red],return_counts=True);alpha.append({'file':name,'alpha0':int((aa==0).sum()),'alpha1':int((aa==1).sum()),'alpha2to127':int(((aa>=2)&(aa<128)).sum()),'alpha128to254':int(((aa>=128)&(aa<255)).sum()),'alpha255':int((aa==255).sum()),'brightRedPositiveAlphaPixels':int(red.sum()),'brightRedAlphaHistogram':{str(int(k)):int(v) for k,v in zip(u,c)}})
put('alpha-edge-diagnostics.json',{'predicate':'decodedRGBA R>200 G<70 B<70 A>0','images':alpha,'alphaProcessing':'None;directwholecanvasRGBA nearest only. Lowalpha red pixels retained,not thresholded or recolored.','interpretation':'Rawviewer RGB may exaggerate lowalpha fringe;actual lightdark runtime-size assessment separate.'})
put('producer-review.json',{'status':'HELD pending independent normal-worldsize playback','nativeClosedEyelidObserved':True,'runtimeBlinkReadability':'PENDING independent140.8CSSsamples','sourceCanvas1254RatherThanRequested1024':True,'exactReferenceAwakeReused':True,'wholeEnvelopeAlpha128Same':boxes[0]==boxes[1],'bodyOutsideEyeRedraw':True,'footLowestRowChangeOutputPx':base,'footLowestRowChangeWorld':base/d,'allFeetStanceAccepted':False,'outsideEyePixelEqualityIsApprovalGate':False,'newDrawings':1,'newNeutral':0,'newLook':0,'automaticRetry':False,'physicalGeometryApproved':False,'appBound':False})
put('behavior-handoff.json',{'speciesId':'hooded_oriole','newAction':'blink','newClosureDrawings':1,'newNeutral':0,'newLook':0,'reusedAwake':1,'renderClipId':'blink','idleFirstNeutralHoldTicks':60,'idleScope':'own exactawake only;existingneutral/lookprimaryuntouched','blinkSchedule':{'tickRate':30,'durationTicks':[60,3,27],'loop':True,'timing':'authored;not measured biology'},'sourceStatus':'HELD pending independent source-usefulness review','packetBindingReady':False,'runtimeAdoption':False,'supportWorld':None,'geometryReviewed':False,'currentMacNamedBlinkContract':'UNKNOWN','canonicalZodSharp':'NOT_RUN'})
print(json.dumps({'newPrimaryID':rows[0]['sourceFrameId'],'newOutputPNGsha256':sha(P/'closed192.png'),'contactAlpha':contactAlpha,'bboxes':boxes,'footBaselineWorld':base/d,'footCentroidWorld':cent/d,'profileSHA256':sha(P/'texture-review-manifest.json')}))
