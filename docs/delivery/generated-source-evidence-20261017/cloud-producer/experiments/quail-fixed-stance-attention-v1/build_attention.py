from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib,shutil,datetime,time
P=Path(__file__).parent;R=Path('/workspace/asset-production');Q=R/'experiments/common-slot-zero-call-batch-v1/species/california_quail';pr=json.load(open(P/'PREREGISTRATION.json'));assert not (P/'export-receipt.json').exists() and not (P/'ART-WRITTEN-NO-REEXPORT.json').exists(),'ONE export only';start=datetime.datetime.now(datetime.timezone.utc).isoformat();clock=time.perf_counter();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def fid(im):return 'frame.sha256.'+hashlib.sha256(f'RGBA8;{im.width}x{im.height};'.encode()+im.convert('RGBA').tobytes()).hexdigest()
def put(n,d):(P/n).write_text(json.dumps(d,indent=2,default=lambda value:int(value))+'\n')
for n in ['sources','source-provenance','frames','full-stage','layers','masks']: (P/n).mkdir(exist_ok=True)
orig=[90,92];crop=pr['commonCrop'];stage=237;arrays={};inputs=[]
for f in pr['sourceInputs']:
 role=f['role'];src=R/f['codecPNG'];assert sha(src)==f['codecPNGsha256'];im=Image.open(src).convert('RGBA');full=Image.new('RGBA',(stage,stage));full.paste(im,tuple(orig));arrays[role]=np.array(full)
 for kind,path in [('native',f['nativeSourcePNG']),('raw237',f['rawFullPNG']),('codec',f['codecPNG'])]:
  infile=R/path;out=f'sources/{role}-{kind}.png';shutil.copyfile(infile,P/out)
  inputs.append({'role':role,'kind':kind,'file':out,'PNGsha256':sha(P/out),'upstreamFile':path,'nativeSourceFrameId':f['nativeSourceFrameID'],'noPixelChanges':True})
for n in ['original.png','prompt.txt','PRIMARY-SOURCE-MANIFEST.json','intake-manifest.json']:
 s=R/'new-species/sd20-final-four-v1'/n
 if s.exists():shutil.copyfile(s,P/'source-provenance'/('final-four--'+n))
for n in ['source-handoff.json','source-provenance.json','historical-review-findings.json','review-target-hashes.json']:
 shutil.copyfile(Q/n,P/'source-provenance'/('common-quail--'+n))
poly=pr['headPlumeUpperNeckOwnershipContourCellEdges']
def inside(x,y):
 result=False;j=len(poly)-1
 for i in range(len(poly)):
  xi,yi=poly[i];xj,yj=poly[j]
  if (yi>y)!=(yj>y) and x<(xj-xi)*(y-yi)/(yj-yi)+xi:result=not result
  j=i
 return result
mask=np.array([[inside(x+.5,y+.5) for x in range(stage)] for y in range(stage)],dtype=bool);base=arrays['neutral'];donor=arrays['look-v1'];out=base.copy();out[mask]=donor[mask];assert np.array_equal(out[~mask],base[~mask]);body=base.copy();body[mask]=0;head=np.zeros_like(donor);head[mask]=donor[mask];neutralhead=np.zeros_like(base);neutralhead[mask]=base[mask];Image.fromarray(mask.astype(np.uint8)*255).save(P/'masks/head-plume-upperneck-ownership.png');Image.fromarray(body).save(P/'layers/fixed-neutral-body.png');Image.fromarray(head).save(P/'layers/upward-attention-head.png');Image.fromarray(neutralhead).save(P/'layers/neutral-head.png')
colors=lambda a:{tuple(v[:3]) for v in a.reshape(-1,4) if v[3]};palette=colors(base)|colors(donor);assert len(palette)==63;assert colors(out)<=palette;assert set(np.unique(out[:,:,3]))=={0,255}
frameRecords=[];fulls={'neutral':base,'look':out}
for role,arr in fulls.items():
 im=Image.fromarray(arr);im.save(P/'full-stage'/f'{role}.png');cut=im.crop(crop);recon=Image.new('RGBA',(stage,stage));recon.paste(cut,tuple(orig));assert recon.tobytes()==im.tobytes()
 if role=='neutral':shutil.copyfile(Q/'codec-cropped/neutral.png',P/'frames/neutral.png')
 else:cut.save(P/'frames/look.png')
 contrib=[f['nativeSourceFrameID'] for f in pr['sourceInputs'][:1 if role=='neutral' else 2]]
 frameRecords.append({'id':role,'role':role,'png':f'frames/{role}.png','PNGsha256':sha(P/'frames'/f'{role}.png'),'decodedRGBAId':fid(cut),'sourceFrameID':pr['sourceInputs'][0 if role=='neutral' else 1]['nativeSourceFrameID'],'constructionDerivative':True,'newDrawing':False,'canvas':[95,100],'density':1,'pivot':[50,93],'contacts':[],'fullStageOrigin':orig,'fullStagePNG':f'full-stage/{role}.png','fullStagePNGsha256':sha(P/'full-stage'/f'{role}.png'),'nativeSourceIDsContributing':contrib})
assert sha(P/'frames/neutral.png')==pr['sourceInputs'][0]['codecPNGsha256']
# RLE exact source-pixel ownership, same global coordinates; no fitted part offsets.
runs=[]
for y in range(stage):
 x=0
 while x<stage:
  startx=x;selected=bool(mask[y,x]);x+=1
  while x<stage and bool(mask[y,x])==selected:x+=1
  runs.append({'y':y,'x':startx,'width':x-startx,'source':'look-v1' if selected else 'neutral'})
put('source-pixel-maps.json',{'coordinates':'fullstage237 worldpixelcenters; sourcecodec xy=(fullX-90,fullY-92),outsidecodec=exacttransparent zero padding','mapMeaning':'Each output pixel bytecopies one existing codecfullstage source atsameXY; inside contour includes donortransparent, outside exactneutral','runs':runs,'nativeSourceIDs':[f['nativeSourceFrameID'] for f in pr['sourceInputs']],'hiddenUnderpaint':False,'rotation':0,'translation':[0,0],'scale':[1,1]})
# Detect newly enclosed transparent pixels via exterior flood fill, an image diagnostic, not anatomy.
def holes(a):
 transparent=a[:,:,3]==0;seen=np.zeros((stage,stage),bool);stack=[(x,y) for x in range(stage) for y in [0,stage-1]]+[(x,y) for y in range(stage) for x in [0,stage-1]]
 while stack:
  x,y=stack.pop()
  if x<0 or x>=stage or y<0 or y>=stage or seen[y,x] or not transparent[y,x]:continue
  seen[y,x]=True;stack.extend([(x-1,y),(x+1,y),(x,y-1),(x,y+1)])
 return transparent&~seen
newholes=holes(out)&~holes(base);yy,xx=np.where(newholes);outsideDiff=int(np.any(out!=base,axis=2)[~mask].sum());footRegion=[105,165,180,190];x0,y0,x1,y1=footRegion;assert np.array_equal(out[y0:y1,x0:x1],base[y0:y1,x0:x1]);put('protection-seam-proof.json',{'outsideOwnershipContourChangedPixels':outsideDiff,'bodyAtAndBelowRow131ByteExact':bool(np.array_equal(out[131:],base[131:])),'footProtectionROI':footRegion,'footROIByteExact':True,'neutralPNGByteExact':True,'paletteUnchanged':True,'noNewRGBAValuesBeyondTwoSources':True,'oldOpaqueHeadPixelsClearedByDonorTransparent':int((mask&(base[:,:,3]>0)&(donor[:,:,3]==0)).sum()),'actualHeadPixelChanges':int(np.any(out!=base,axis=2)[mask].sum()),'ownershipMaskPixels':int(mask.sum()),'newEnclosedTransparentPixelsCount':len(xx),'newEnclosedTransparentCoordinates':[[int(x),int(y)] for x,y in zip(xx,yy)],'holesMeaning':'4-neighbor exterior floodfill image diagnostic; notproof of anatomicalneck quality. No missing pixels were filled.','hardContourAndPaletteTrials':1,'noHiddenUnderpaint':True,'contacts':[],'supportWorld':None,'physicalSupportApproved':False,'seamRisk':'One hard upperneck contour may show tone/pattern step; actualnormal237playback independent review required.'})
put('construction-recipe.json',{'recipeId':pr['recipeId'],'method':'binary same-coordinate authored head/plume/upperneck sourcepixel replacement','sourceWorldHistorical':[236.30769230769232]*2,'worldPixelStage':[237,237],'density':1,'headReplacementPolygonCellEdges':poly,'maskMeaning':'one manually inspected contour, notsemanticsegmentation or recovered hidden anatomy','pixelCenterInPolygon':True,'compositionOrder':['exactfixedneutralbody/wing/tail/legs/feet outsidecontour','realupwardlookV1 pixels insidecontour INCLUDING transparent to clear oldhead/plume'],'joint':{'rotation':0,'translation':[0,0],'scale':[1,1],'uncertaintyWorldPixels':2,'meaning':'documentaryownershipseam, notcalibratedjoint/rig/physicalneckaxis'},'commonCrop':crop,'candidatePivot':[50,93],'fullRoot':[140,185],'sourcePixelMaps':'source-pixel-maps.json','supportWorld':None,'contacts':[],'nativeCalls':0,'newDrawings':0,'sourcePosePainting':False,'hiddenUnderpaint':False,'recolorRequantization':False,'rights':'UNKNOWN existinggeneratedsources; no CC/clearance asserted'})
clips=[{'id':'idle','tickRate':30,'frames':[{'frameId':'neutral','durationTicks':90}],'loop':True,'authoredStaticHold':True},{'id':'look','tickRate':30,'frames':[{'frameId':'neutral','durationTicks':60},{'frameId':'look','durationTicks':18},{'frameId':'neutral','durationTicks':12}],'loop':False}];ims=[Image.open(P/'frames'/f'{r}.png').convert('RGBA') for r in ['neutral','look','neutral']];ims[0].save(P/'attention.apng',save_all=True,append_images=ims[1:],duration=[2000,600,400],loop=1,disposal=0,blend=0)
atlas=Image.new('RGBA',(190,100));atlas.paste(ims[0],(0,0));atlas.paste(ims[1],(95,0));atlas.save(P/'atlas.png')
for i,f in enumerate(frameRecords):f['atlasRect']={'x':95*i,'y':0,'width':95,'height':100}
sheet=Image.new('RGB',(237*3,237*2+62),'#eee9da');dr=ImageDraw.Draw(sheet)
for i,(role,a) in enumerate([('neutral',base),('old whole-lookV1',donor),('fixed-bodyattention',out)]):
 dr.text((i*237+4,5),role+'237stage',fill='black')
 for j,bg in enumerate(['#e5e0cd','#182a32']):
  tile=Image.new('RGBA',(237,237),bg);tile.alpha_composite(Image.fromarray(a));sheet.paste(tile.convert('RGB'),(i*237,25+j*250))
sheet.save(P/'normal-light-dark.png')
large=Image.new('RGB',(600,330),'#eee9da');dr=ImageDraw.Draw(large)
for i,(role,a) in enumerate([('neutral',base),('fixedattention',out)]):
 bg=Image.new('RGBA',(237,237),'#24313c');bg.alpha_composite(Image.fromarray(a));cropim=bg.crop((136,88,189,137)).resize((265,245),Image.Resampling.NEAREST);large.paste(cropim.convert('RGB'),(i*300,30));dr.text((i*300+4,5),role+' head+seam5x',fill='black')
large.save(P/'enlarged-head-neck.png')
h={'kind':'Attention-only authoredhead sourceconstruction; no completecommonfamily or runtimeadmission','speciesId':'california_quail','batchId':pr['id'],'recipeId':pr['recipeId'],'newNativeCalls':0,'newDrawings':0,'existingAuthoredSourceDrawings':2,'frames':frameRecords,'fullWorldCanvas':[236.30769230769232]*2,'displayStage':[237,237],'pixelDerivativeWorldStage':[237,237],'candidateCanvas':[95,100],'density':1,'crop':crop,'commonCropOrigin':orig,'candidatePivot':[50,93],'roundedFullPivot':[140,185],'oldPivotWorld':pr['oldFractionalRoot'],'alphaOrigin':'upstream-cleanup existingcodec exact','contacts':[],'supportWorld':None,'geometryScope':'image-registration-only','geometryReviewed':False,'physicalSupportReviewed':False,'clips':clips,'blinkAvailability':'Existing nativeblink retainedupstream, notconstructed orclaimed as part ofthis2frame attentionpacket','sourceUsefulness':'PENDING_INDEPENDENT_REVIEW','runtimeAdmission':False,'sourceAdmitted':False,'rightsGranted':False,'constructionRecipe':'construction-recipe.json','ancestry':'ancestry.json','atlas':{'file':'atlas.png','sha256':sha(P/'atlas.png'),'width':190,'height':100}};put('source-handoff.json',h)
put('PRIMARY-SOURCE-MANIFEST.json',{'batchId':pr['id'],'nativeCalls':0,'newDrawings':0,'frames':[],'reusedFrames':[{'sourceFrameId':f['nativeSourceFrameID'],'role':f['role'],'sourcePNG':f'sources/{f["role"]}-native.png','sourcePNGsha256':f['nativePNGsha256']} for f in pr['sourceInputs']],'derivativeRenderFrames':frameRecords,'sourceStatus':'PENDING_INDEPENDENT_REVIEW','notes':['Notnewnativeart. Newpixelconstructionderivative references2existing genuineauthoredkeys.','No rigroll, inbetween generation, bodybob, hiddenunderpaint, warp, perposefit, recolor or requantization.'],'sourceAdmitted':False,'runtimeAdmission':False})
put('frame-to-action-map.json',{'manifest':{'file':'source-handoff.json','sha256':sha(P/'source-handoff.json')},'atlas':h['atlas'],'renderFrames':frameRecords,'clips':clips,'rootStationary':True,'nativeCalls':0,'newDrawings':0,'runtimeAdmission':False})
put('palette-proof.json',{'sharedOpaqueColors':sorted([list(c) for c in palette]),'opaqueColorCount':63,'newFrameColorCount':len(colors(out)),'newColorsAdded':0,'recolor':False,'requantization':False,'neutralCodecPNGByteExact':True})
put('ancestry.json',{'sources':inputs,'historicalNativeOriginal':'source-provenance/final-four--original.png','historicalNativeOriginalSHA256':sha(P/'source-provenance/final-four--original.png'),'exactHistoricalPrompt':'source-provenance/final-four--prompt.txt','exactHistoricalPromptSHA256':sha(P/'source-provenance/final-four--prompt.txt'),'originalSourceIDs':[f['nativeSourceFrameID'] for f in pr['sourceInputs']],'nativeOriginalOrPromptModified':False,'factualReferenceRights':'UNKNOWN inheritedgeneratedsource; no photo clearance/CC invented','oldSourceCountsAdded':0})
put('export-receipt.json',{'state':'ONE_FIXED_CONTOUR_EXPORT_COMPLETE','exportStartUTC':start,'exportEndUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'observedExportSeconds':time.perf_counter()-clock,'nativeCalls':0,'newNativeDrawings':0,'existingSourceIDs':2,'contourVariants':1,'exportPasses':1,'retries':0,'samplerPasses':0,'sourceCodecPixelsCopied':True,'crop':crop,'canvas':[95,100],'pivot':[50,93],'nonzeroDiscardedRGBA':0,'paletteVariants':0,'noRecolorRequantization':True,'hiddenUnderpaint':False,'newEnclosedHoles':len(xx),'sourceUseful':'PENDING_REVIEW','runtimeAdmission':False})
print(json.dumps({'exportPasses':1,'newNativeCalls':0,'newEnclosedTransparentPixels':len(xx),'headChanges':int(np.any(out!=base,axis=2)[mask].sum()),'outsideContourDifferences':outsideDiff,'clearedOldHeadPixels':int((mask&(base[:,:,3]>0)&(donor[:,:,3]==0)).sum()),'newCodecHash':sha(P/'frames/look.png')}))
