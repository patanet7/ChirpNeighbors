"""Read-only source/export diagnostics; writes only this audit directory."""
from pathlib import Path
from PIL import Image, ImageDraw
import numpy as np
from scipy import ndimage
import hashlib, json

OUT=Path(__file__).resolve().parent
ROOT=Path('/workspace/asset-production')
CANON=ROOT/'new-species/sd20-three-canon-v1'
ACTION=ROOT/'motion/sd20-anna-actions-v1'
cm=json.loads((CANON/'intake-manifest.json').read_text())
cf=next(f for f in cm['frames'] if f['id']=='anna_s_hummingbird')
line=json.loads((ACTION/'source-lineage.json').read_text())
records=[{'name':'canon-idle','source':CANON/cf['sourcePNG'],'output':CANON/cf['outputPNG'],'frameId':cf['sourceFrameId'],'declaredDensity':cf['presentationDensityPxPerWorldUnit'],'native':CANON/'original.png','translation':cf['sourceRegistration']['translation'],'cropOrigin':[0,0]}]
records += [{'name':f['name'],'source':ACTION/f['file'],'output':ACTION/f['export'],'frameId':f['frameId'],'declaredDensity':1.5,'native':ACTION/'original.png','translation':f['registrationTranslation'],'cropOrigin':f['sourceRect'][:2]} for f in line['frames']]

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def fid(im):return 'frame.sha256.'+hashlib.sha256(f'RGBA8;{im.width}x{im.height};'.encode()+im.tobytes()).hexdigest()
def stats(im):
    a=np.array(im.convert('RGBA')); rgb=a[:,:,:3].astype(float); alpha=a[:,:,3]; m=alpha>=128
    yp=rgb@np.array([.2126,.7152,.0722]); v=yp[m]
    # sRGB code-value luma, explicitly not physical/linear luminance.
    pale=m&(yp>=170)&(rgb.min(axis=2)>=140)&(np.ptp(rgb,axis=2)<=60)
    labels,count=ndimage.label(pale,np.ones((3,3),dtype=bool)); areas=np.bincount(labels.ravel())[1:]
    interior=ndimage.binary_erosion(m,structure=np.ones((3,3),dtype=bool),border_value=0)
    il,ic=ndimage.label(pale&interior,np.ones((3,3),dtype=bool)); ia=np.bincount(il.ravel())[1:]
    y,x=np.where(m)
    return {'canvas':list(im.size),'alpha128Pixels':int(m.sum()),'bboxAlpha128':[int(x.min()),int(y.min()),int(x.max()+1),int(y.max()+1)],'meanCodeValueLuma':float(v.mean()),'medianCodeValueLuma':float(np.median(v)),'lumaQuantiles10_25_75_90':np.quantile(v,[.1,.25,.75,.9]).tolist(),'alphaWeightedMeanCodeValueLuma':float((yp*(alpha/255)).sum()/(alpha/255).sum()),'meanVisibleRGB':rgb[m].mean(axis=0).tolist(),'darkLumaBelow64Fraction':float((v<64).mean()),'paleThresholdPixels':int(pale.sum()),'paleThresholdFractionOfVisible':float(pale.sum()/m.sum()),'pale8ConnectedComponents':int(count),'paleComponentAreasSorted':sorted(int(x) for x in areas),'paleTinyComponentsArea1or2':int((areas<=2).sum()),'interiorPalePixels':int((pale&interior).sum()),'interiorPaleComponents':int(ic),'interiorPaleTinyComponentsArea1or2':int((ia<=2).sum()),'interiorPaleComponentAreasSorted':sorted(int(x) for x in ia),'uniqueRGBAmongAlpha128':len(np.unique(a[:,:,:3][m],axis=0))}

results=[]
for r in records:
    source=Image.open(r['source']).convert('RGBA'); output=Image.open(r['output']).convert('RGBA')
    expected=source.resize(output.size,Image.Resampling.NEAREST)
    # Recover the exact Pillow nearest selected source coordinates rather than assuming a resampling convention.
    iy,ix=np.indices((source.height,source.width)); coords=Image.fromarray((iy*source.width+ix).astype('int32'))
    selected=np.array(coords.resize(output.size,Image.Resampling.NEAREST)); sy=selected//source.width;sx=selected%source.width
    sampled=np.array(source)[sy,sx]; actual=np.array(output)
    sa=np.array(source);na=np.array(Image.open(r['native']).convert('RGBA'));vy,vx=np.where(sa[:,:,3]>=128)
    nx=vx-r['translation'][0]+r['cropOrigin'][0];ny=vy-r['translation'][1]+r['cropOrigin'][1]
    valid=(nx>=0)&(nx<na.shape[1])&(ny>=0)&(ny<na.shape[0]);assert valid.all()
    origin_equal=np.array_equal(sa[vy,vx],na[ny,nx])
    world_common=output.resize((64,64),Image.Resampling.NEAREST)
    ss=stats(source);os=stats(output)
    results.append({'name':r['name'],'nativeGeneratedAtlasPath':str(r['native']),'nativeGeneratedAtlasSHA256':sha(r['native']),'visibleRegisteredPixelsExactlyMapToNativeAtlasRGBA':origin_equal,'maximumNativeToRegisteredVisibleRGBAByteDifference':int(np.abs(sa[vy,vx].astype(int)-na[ny,nx].astype(int)).max()),'mapping':{'translation':r['translation'],'cropOrigin':r['cropOrigin'],'visibilityThreshold':128},'sourcePath':str(r['source']),'sourceFrameId':r['frameId'],'sourceFrameIdMatchesDecodedRGBA':fid(source)==r['frameId'],'sourcePNGsha256':sha(r['source']),'outputPath':str(r['output']),'outputPNGsha256':sha(r['output']),'outputRGBAId':fid(output),'exportScale':output.width/source.width,'nearestWholeCanvasRGBAExactlyMatches':np.array_equal(np.array(expected),actual),'selectedNativeRGBAExactlyMatchesOutput':np.array_equal(sampled,actual),'maximumRGBAByteDifferenceAtSelectedCoordinates':int(np.abs(sampled.astype(int)-actual.astype(int)).max()),'source':ss,'output96':os,'wholeVisibleMeanLumaDifferenceOutputMinusSource':os['meanCodeValueLuma']-ss['meanCodeValueLuma'],'declaredDensity':r['declaredDensity'],'declaredWorldCanvas':[96/r['declaredDensity']]*2,'declaredVisibleWorldWidth':(os['bboxAlpha128'][2]-os['bboxAlpha128'][0])/r['declaredDensity'],'commonDensity1p5World64Diagnostic':stats(world_common)})

# Diagnostic composites only; source art files are never overwritten.
sheet=Image.new('RGB',(1100,640),(232,232,218));draw=ImageDraw.Draw(sheet)
draw.text((10,8),'Anna source/export audit: columns canon, blink, look, hover-up, hover-down',fill=(20,35,25))
draw.text((10,30),'Top: each published density (canon1.294 / actions1.5); middle: common density1.5; bottom: fixed output crop at3x inspection',fill=(20,35,25))
for i,r in enumerate(records):
    im=Image.open(r['output']).convert('RGBA');x=i*220
    draw.text((x+10,53),r['name'],fill=(20,35,25))
    def comp(v,at):
        bg=Image.new('RGBA',v.size,(217,212,189,255));bg.alpha_composite(v);sheet.paste(bg.convert('RGB'),at)
    edge=round(96/r['declaredDensity']);comp(im.resize((edge,edge),Image.Resampling.NEAREST),(x+10,75))
    draw.text((x+10,154),'common1.5:64canvas',fill=(20,35,25));comp(im.resize((64,64),Image.Resampling.NEAREST),(x+10,175))
    draw.text((x+10,251),'output pixels,3x crop',fill=(20,35,25))
    # Same fixed output ROI for all poses, not a body-fit scale;3x inspection.
    crop=im.crop((20,34,82,90)).resize((186,168),Image.Resampling.NEAREST)
    comp(crop,(x+10,276));draw.text((x+10,450),'fixedROI20,34..82,90 at3x',fill=(20,35,25))
    draw.text((x+10,478),'96luma '+str(round(results[i]['output96']['meanCodeValueLuma'],2)),fill=(20,35,25))
draw.text((10,520),'Composites are diagnostic views, not edited/replacement bird assets. No tint, opacity reduction, smoothing or body-fit used.',fill=(20,35,25))
draw.text((10,541),'Owner screenshot unavailable/not retrieved. Runtime rendering/contact overlap causality is outside this source-only audit.',fill=(20,35,25))
sheet.save(OUT/'comparison.png')

data={'format':'chirp-anna-source-darkness-audit@0.1','scope':'source-only; owner screenshot not seen, no screenshot retrieval attempted; Mac owns runtime RCA','metrics':results,'sourceNativeFiles':[{'path':str(CANON/'original.png'),'sha256':sha(CANON/'original.png'),'canvas':list(Image.open(CANON/'original.png').size)},{'path':str(ACTION/'original.png'),'sha256':sha(ACTION/'original.png'),'canvas':list(Image.open(ACTION/'original.png').size)}],'inputMetadataHashes':{str(p):sha(p) for p in [CANON/'intake-manifest.json',ACTION/'source-lineage.json',ACTION/'behavior-handoff.json']},'diagnosticDefinitions':{'visibility':'alpha>=128 unless alpha-weighted metric explicitly named','luma':'Yprime=.2126R+.7152G+.0722B on sRGB8 code values, not linear-light physical luminance','pale':'visible && Yprime>=170 && minRGB>=140 && (maxRGB-minRGB)<=60; heuristic neutral/pale-feather pixel selection, not semantic whiteness or an art gate','connectivity':'8-connected components; tiny means1or2pixels at the reported resolution','interior':'visible mask eroded by one3x3pixel step at that resolution; pixel-size dependent, not a matched anatomical region','commonWorldSize':'96→64 nearest-only at density1.5; no per-bird fit. Canon published density differs and is also shown separately.','componentInterpretation':'Native/output/world component counts are not directly scale invariant. Tiny-component statistics diagnose sampling/texture, not defects or screenshot causality.'},'comparisonPNG':{'file':'comparison.png','sha256':sha(OUT/'comparison.png'),'canvas':list(sheet.size)},'sourceImagesEdited':False,'imageGenerationCalls':0,'modelInstalls':0,'MacRuntimeOrScreenshotPixelsInspected':False,'globalMetadataOrLibraryOrGitWrites':False}
data['finding']='No color-darkening transform found in these retained Anna source/export paths. All five exported RGBA arrays exactly equal the selected native1024 source pixels; small global visible-luma mean changes are nearest-sampling population changes. This does not diagnose the unavailable owner screenshot or current Mac rendering.'
data['nativeLineageCheck']='At alpha>=128, every registered visible pixel in all five frames also exactly maps back to its original generated atlas at the documented crop/translation. No visible RGB/alpha change was detected in native-atlas→registered-source or registered-source→96 export.'
data['manualVisualFindings']=[
    'The generated native canon and action sources already contain high-frequency pale gray/white breast feather flecks, olive/green highlights and brown/dark folded-wing feather lines. These details were not invented by the96 export.',
    'Rose crown/throat, green upperparts and long thin dark bill remain recognizable in the source family. New perched poses remain about32.67world units wide under their declared density, compared with34 for the first canon under its different density.',
    'At a common density1.5, the old canon becomes29.33world units wide while new perched poses remain32.67. Forcing every body to34 would be a different fit and was deliberately not performed.',
    'At common64canvas nearest presentation the bird is tiny and high-frequency plumage is represented by a small set of contrasting pixels. Pale speck components are present, but component counts are not a semantic defect criterion.',
    'No owner screenshot pixels, brown feeder bird, corvid comparison, real feeder overlap, runtime tint or current Mac rendering was inspected in this audit. Parent descriptions are context, not source-pixel evidence.'
]
data['causalAssessment']={
    'establishedLocally':['Native source feather texture includes pale/interior color variation.','All visible atlas→registered pixel mappings tested are byte-exact.','All five1024→96 nearest outputs are byte-exact at the selected coordinates.','Per-frame whole-visible luma means change by sampling only; the new perched exports are slightly brighter by this metric, not darker.','Published old and new Anna presentation densities differ.'],
    'possibleButUnproven':['Fine source texture may appear noisy at tiny presentation sizes.','Different presentation density/device scaling and background contrast may alter perceived detail/brightness.','Mac opacity, tint, filter, blending, color-space or premultiplied-alpha handling could change actual rendering; these were not tested.','Overlapping birds/feeder geometry or mismatched contact placement could create a visual mixture.','Fast alternating wing area could create temporal contrast/strobing distinct from a per-pixel color transform.'],
    'notEstablished':['That the unavailable screenshot depicts Anna.','That these source textures caused the owner\'s reported brown-bird mottling/darkness.','That the current Mac renderer darkens these assets.','That exporting a different palette or regenerating art would fix the reported issue.'],
    'ownerScreenshotAccess':'Not retrieved or retried; earlier cloud download failure remains outside this audit. No screenshot pixels claimed seen.',
    'MacRCAOwner':'Mac implementation owner; source-only audit does not replace its renderer/contact investigation.'
}
data['futureControlledExperiment']={
    'status':'proposal only; no art call, runtime change, model install or rendering change performed',
    'firstRuntimeIsolation':'Mac owner freezes one exact PNG/frame/hash, pose, background, world placement and size, then compares a direct unmodified PNG render with the actual yard render at the same effective density/DPR. Capture frame/tint/opacity/filter/blend/alpha/color-space parameters and isolate overlaps. Compare equivalent composited crops; transparent RGB alone is not a display result.',
    'scaleControl':'Compare each published density separately and a common1.5density control. Do not confuse a34world-length fit with the old/new actual density values.',
    'laterArtControlIfStillNeeded':'After runtime/overlap causes are separated and if owner requests it, compare one geometry-registered same-identity source with reduced high-frequency pale feather contrast against the unchanged source at the same world size/background. Preserve mean body brightness/palette/identity as practical controls and retain exact source/prompts. This is a prospective comparison, not a current image-generation request or promised fix.',
    'acceptance':'Owner normal-size visual judgment plus actual renderer/contact evidence. No automatic body-RGBA-equality, luma threshold or component-count art gate.'
}
readme='''# Anna source/export darkness audit

No export darkening transform was found. All five retained1024→96 outputs exactly match the selected source RGBA pixels. Visible registered pixels also map exactly back to the original generated atlases. Source images were not edited.

Mean visible sRGB code-value luma (not physical luminance):

| Pose | Source | Output96 | Change |
|---|---:|---:|---:|
| Original canon |98.15|96.31|−1.84|
| Blink |96.59|97.90|+1.32|
| Look |97.59|98.54|+0.96|
| Hover up |98.26|97.33|−0.92|
| Hover down |95.38|95.88|+0.50|

These small mean changes come from which pixels nearest sampling selects; selected pixels are unchanged. Pale breast feather specks already exist in the generated sources. Threshold/component diagnostics in `audit.json` describe this texture and sampling, not art acceptance or screenshot causality.

Scale is a separate variable: the original canon declares density1.2941 and34world-unit visible width; actions declare density1.5 and32.67world-unit perched width. `comparison.png` shows both published sizes and a common1.5density control. The common control is64×64canvas, not a per-body34unit fit.

The owner screenshot was not retrieved/retried or seen. This audit cannot identify its brown feeder bird, diagnose overlap, or rule out Mac tint/opacity/blend/color-space/scale behavior. Mac owns that investigation.

Next proposed control: compare one unchanged PNG/frame in direct and actual-yard renders with matching size/background/DPR, recording render parameters and removing overlap ambiguity. Only afterwards, if requested, test a same-identity lower-frequency feather-texture alternative. No art calls, model changes or runtime changes were performed.

Reproduce local diagnostics with `python3 build_audit.py`. It reads existing sources and writes only this audit directory.
'''
(OUT/'README.md').write_text(readme)
data['deliverables']={'audit':'audit.json','readme':'README.md','readmeSHA256':sha(OUT/'README.md'),'comparison':'comparison.png','reproducer':'build_audit.py','reproducerSHA256':sha(Path(__file__))}
(OUT/'audit.json').write_text(json.dumps(data,indent=2)+'\n')
print(json.dumps({'file':str(OUT/'audit.json'),'nearestAllExact':all(x['nearestWholeCanvasRGBAExactlyMatches'] for x in results),'rows':[{'name':x['name'],'sourceLuma':x['source']['meanCodeValueLuma'],'outputLuma':x['output96']['meanCodeValueLuma'],'delta':x['wholeVisibleMeanLumaDifferenceOutputMinusSource'],'paleOutputPixels':x['output96']['paleThresholdPixels'],'tinyInteriorPaleOutputComponents':x['output96']['interiorPaleTinyComponentsArea1or2'],'declaredVisibleWorldWidth':x['declaredVisibleWorldWidth']} for x in results]}))
