"""Read local evidence; write only this arm. Never run old experiment builders."""
from pathlib import Path
import datetime as dt
import hashlib
import importlib.metadata as md
import json
import re
import shutil
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
from PIL import Image

P = Path(__file__).resolve().parent
R = Path('/workspace/asset-production')
UI = Path('/workspace/runtime-resting-intake-v5-inspect')
BASE = R/'experiments/resting-repair-ground-motion-v1/attention-repairs/white_crowned_sparrow'
START = time.monotonic()
utc = lambda: dt.datetime.now(dt.timezone.utc).isoformat()
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
def put(name, value):
    (P/name).write_text(json.dumps(value, indent=2) + '\n')
def fact(p):
    return {'file':str(p), 'sha256':sha(p), 'bytes':p.stat().st_size}
commands=[]
def run(argv):
    try:
        p=subprocess.run(argv,capture_output=True,text=True,timeout=20)
        item={'argv':argv,'exitCode':p.returncode,'stdout':p.stdout,'stderr':p.stderr}
    except Exception as e:
        item={'argv':argv,'error':type(e).__name__+': '+str(e)}
    commands.append(item)
    return item

packages=[]
for name in ['Pillow','numpy','jsonschema','torch','torchvision','diffusers','controlnet_aux','mediapipe','opencv-python','open3d','trimesh','pygltflib','bpy','pybullet']:
    try:
        m=md.metadata(name)
        license_text=m.get('License-Expression') or m.get('License') or ''
        packages.append({'name':name,'version':m['Version'],'licenseMetadataBeginning':license_text[:900],
                         'licenseMetadataSHA256':hashlib.sha256(license_text.encode()).hexdigest(),
                         'licenseClassifiers':[x for x in m.get_all('Classifier',[]) if x.startswith('License')]})
    except md.PackageNotFoundError:
        packages.append({'name':name,'status':'NOT_INSTALLED according to distribution metadata'})
for argv in [['ffmpeg','-version'],['ffmpeg','-L'],['magick','-version'],['inkscape','--version'],['gimp','--version'],['node','--version']]:
    run(argv)
licenses=[]
for name in ['ffmpeg','imagemagick','gimp','inkscape','blender']:
    p=Path('/usr/share/doc')/name/'copyright'
    if p.exists():
        licenses.append({**fact(p),'declaredLicenseLabels':list(dict.fromkeys(re.findall(r'^License: (.+)$',p.read_text(errors='replace'),re.M)))})
tools={n:shutil.which(n) for n in ['ffmpeg','magick','inkscape','gimp','blender','krita','aseprite','synfig','spine','dragonbones']}

# Exhaustive rg listing within these two bounded roots, excluding vendored/build/duplicate/private trees.
search_argv=['rg','--files',str(R),str(UI),'-g','!**/node_modules/**','-g','!**/.git/**','-g','!**/research-private/**','-g','!**/internal-review-retention/**','-g','!**/receipts/**','-g','!**/delivery/**','-g','!**/recovery/**','-g','!**/stream.raw']
listing=run(search_argv)
allfiles=listing.get('stdout','').splitlines()
# Retain only matched paths, not the large general listing.
listing['stdout']={'fileCount':len(allfiles),'matchedPathsRetainedBelow':True}
editable_suffixes={'.blend','.fbx','.gltf','.glb','.obj','.psd','.ora','.kra','.scml','.scon','.spine'}
editable=[x for x in allfiles if Path(x).suffix.lower() in editable_suffixes]
masks=[x for x in allfiles if Path(x).suffix.lower()=='.png' and re.search(r'(head|neck|body).*(layer|mask)|(layer|mask).*(head|neck|body)',Path(x).name)]
sparrow_parts=[x for x in allfiles if ('sparrow' in x.lower()) and (Path(x).suffix.lower() in editable_suffixes or re.search(r'(head|neck|body).*(layer|mask)',Path(x).name))]
fixture=UI/'public/fixtures/sparrow.svg'
svg=ET.parse(fixture).getroot()
fixture_fact={**fact(fixture),'viewBox':svg.attrib.get('viewBox'),'ariaLabel':svg.attrib.get('aria-label'),
              'metadata':''.join(svg.find('{http://www.w3.org/2000/svg}metadata').itertext()),
              'groupElements':len(svg.findall('.//{http://www.w3.org/2000/svg}g')),
              'interpretation':'Editable rect fixture exists; self-labels not reviewed species art, no articulated head/neck groups. Not the canonical detailed Sparrow.'}
put('inspection-evidence.json',{'createdUTC':utc(),'pythonVersion':sys.version,'packages':packages,'binaries':tools,
    'binaryVersionCommands':commands,'licenseEvidence':licenses,
    'blender':'Installed executable observed; NOT invoked or used because this experiment forbids Blender.',
    'toolCatalogObservation':'Image-generation edit capability present but not a bird rig; no dedicated bird-rig/3D-pose tool observed in available tool metadata. No connector calls made.',
    'assetSearch':{'roots':[str(R),str(UI)],'editableFormatsFound':editable,'headBodyMaskLayerPaths':masks,'sparrowEditablePartsFound':sparrow_parts,'scope':'Bounded checked-in/local asset trees; no claim of exhaustive host or online-model search.'},'svgFixture':fixture_fact})

registry=json.loads((R/'lessons-and-experiments.json').read_text())
ids=['HF-fixed-body-rig-proof-1','HF-rig-neck-overlap-2']
experiments=[]
for rec in registry['experiments']:
    if rec.get('id') not in ids: continue
    folder=(R/rec['source']).parent
    files=['manifest.json','build_proof.py','build_cleanup.py','layer-edit-plan.json','head-mask.png','head-layer.png','body-feet-layer.png','body-base-layer.png','neck-underpaint-mask.png','neck-underpaint-layer.png','occlusion-review.json','contract-binding.json','app-validator-receipt.json','pixel-measurements.json','SHA256SUMS.json']
    artifacts=[]
    for name in files:
        f=folder/name
        if not f.exists():continue
        a=fact(f)
        if f.suffix=='.png':
            with Image.open(f) as im:a.update(mode=im.mode,canvas=list(im.size))
        artifacts.append(a)
    validator=folder/'app-validator-receipt.json'
    experiments.append({'registryRecord':rec,'recipeId':None,'recipeIdReason':'Existing selected registry records have no recipeId field; experiment id retained without inventing a recipe.',
        'retainedAppValidatorResult':json.loads(validator.read_text()) if validator.exists() else None,
        'artifactEvidence':artifacts,'rerunPerformed':False,'scope':'Read-only source/mask/manifest inspection; no old builder or validator executed.'})
put('existing-experiment-evidence.json',{'registry':fact(R/'lessons-and-experiments.json'),'registrySchemaVersion':registry['schemaVersion'],'registryAuthority':registry['authority'],'experiments':experiments})

h=json.loads((BASE/'source-handoff.json').read_text())
source_facts=[]
for frame in h['frames']:
    if frame['id'] not in ['neutral','look']:continue
    files=[fact(BASE/frame[k]) for k in ['sourcePNG','rawPNG','png']]
    source_facts.append({'role':frame['id'],'sourceFrameId':frame['sourceFrameId'],'nativeCanvas':frame['nativeCanvas'],'files':files})
put('FEASIBILITY.json',{
    'experimentId':'ANIM-AUTHORING-COMPARE-1','arm':'B','speciesId':'white_crowned_sparrow','action':'toward-viewer attention with stationary stance',
    'status':'UNTESTED','statusScope':'Actual part/rig-authored Sparrow toward-viewer yaw; no compatible Sparrow rig/parts implementation executed in this arm.',
    'mechanical2DCompositorAvailable':True,'compatibleSparrowPartsFound':False,'compatible3DBirdRigFound':False,
    'threeDStatus':'UNTESTED; no compatible mesh/weights/camera/source-art views located in bounded asset search; Blender excluded by instruction.',
    'newNativeCalls':0,'newGeneratedDrawings':0,'derivedAssemblies':0,'sourceFamiliesExported':0,
    'authoringTimeSeconds':None,'exportTimeSeconds':None,'cleanupMinutes':None,
    'timingExplanation':'No authoring/export test in B; inspection elapsed is not a comparable authoring benchmark. Earlier HF durations not inferred from file timestamps.',
    'priorExperiments':['HF-fixed-body-rig-proof-1','HF-rig-neck-overlap-2'],
    'whatActuallyExists':'Python/Pillow/NumPy compositor, explicit editable binary head/neck masks and source-clone overlap layers for a different House Finch individual; protected body/feet copy. Same side-view head is rigidly rotated +/-0.12 radians in image plane.',
    'whyNotCompatibleYaw':['HF source is another taxon/individual and masks/pivots cannot be transferred as anatomy.','In-plane rotation supplies no genuinely foreshortened bill/crown/far-eye drawing or depth/occlusion reconstruction.','HF V2 phase1 retains 144 uncovered neck pixels in [607,475,633,492], art acceptance false.','Whole Sparrow neutral/look RGBA drawings are real source art but no preexisting Sparrow head ownership/neck-overlap masks or 3D mesh/rig were located.'],
    'sourceBaseline':str(BASE),'sourceHandoff':fact(BASE/'source-handoff.json'),'sources':source_facts,
    'visualInspection':{'method':'Local view_image inspection of retained source PNGs; no browser capture or new image created.',
       'files':[fact(BASE/'head-feet-diagnostics.png'),fact(BASE/'normal-light-dark.png'),fact(R/'experiments/finch-fixed-body-rig-cleanup-v2/head-mask.png'),fact(R/'experiments/finch-fixed-body-rig-cleanup-v2/owner-review-jaw-phase01.png')],
       'observations':['Sparrow donor look genuinely shortens/turns bill and changes crown/head view; body/shoulder pixels also differ.','HF head mask is a coarse explicit polygon, not semantic bird segmentation or a rigged mesh.','Retained HF jaw crop exposes a stepped contour requiring art judgment.'],
       'newNormalScaleAcceptance':False},
    'proposedHybridInterface':{
      'implementationOwner':'/root/anna_actions; separate arm-d-hybrid-construction, not implemented or counted here',
      'feasibility':'A real bounded 2D layered prototype is feasible using the existing genuinely authored neutral and attention head variants, not synthetic rotation. Exact seams and body protection require actual construction/review.',
      'inputStage':h['displayStage'],'worldCanvas':h['fullWorldCanvas'],'existingCommonCrop':h['crop'],'existingPivot':h['candidatePivot'],
      'sourceInputs':['raw-full/neutral.png','raw-full/look.png'],'canonicalBody':'Exact neutral body/tail/legs/feet pixels; static root. No donor body rescale or painted cleanup.',
      'editableConstructionFilesRequired':['Explicit neutral-head removal mask','Explicit donor head ownership mask','Fixed body layer','Genuine authored neutral/look head layers','Joint/root parameters and layer-order recipe','Source-coordinate lineage, mask hashes, uncovered-head and seam audit'],
      'jointPolicy':'Yaw is authored head variant selection, not an image-plane rotation claiming 3D yaw. No hidden neck underpaint invented; use known source pixels only and disclose old-bill leakage/holes.',
      'clock':{'tickRate':30,'neutralTicks':60,'attentionTicks':18,'neutralReturnTicks':12,'provenance':'authored timing, not biological measurement'},
      'reviewGates':['Protected body/feet RGBA exact','Canonical neutral return exact','No stale bill/head outline, transparent seam or doubled crown at normal124-stage display','Part provenance/rights unresolved authority fields stay null','Source quality separate from codec/schema/runtime admission'],
      'ifSeamFails':'Hold exact construction; human-authored neckline/occlusion art or additional genuine head views needed. Do not fill holes with fabricated anatomy.'},
    'rights':{'toolLicenses':'Actual installed metadata/copyright evidence in inspection-evidence.json; tool licenses do not license bird artwork.','sourceArtAuthority':'Retained owned/generated project source lineage; no new rights certification/private pin invented.','externalModelOrAssetLicense':None},
    'validation':{'inspectionOnly':True,'nativeModelSeed':None,'sourceQualityAccepted':False,'runtimeAdmission':False,'liveMacAcceptance':'UNKNOWN','physicalSupportReviewed':False,'supportWorld':None},
    'failureReasons':['Compatible Sparrow layered yaw rig absent at inspection time','Existing mechanical mask proof has unresolved jaw/occlusion art','No construction in B; actual hybrid prototype delegated separately'],
    'nextQueuedWork':'Independent review of separately constructed hybrid D; no new B call or automatic asset setup.',
    'evidenceFiles':['inspection-evidence.json','existing-experiment-evidence.json','BATH-CONTRACT-FINDINGS.json']})

bath_files=['src/lib/domain/scene.ts','src/lib/engine/surface-interactions.ts','src/lib/engine/surface-runtime.ts','src/lib/engine/physical-surface-contracts.ts','src/lib/assets/manifest-v3.ts','src/lib/assets/manifest-v6.ts','src/lib/assets/manifest.ts','src/lib/assets/pose-geometry.ts','src/lib/assets/animation-specification.ts','src/lib/assets/shape.ts']
snippets={
 'src/lib/domain/scene.ts':[(1,35),(88,100)],
 'src/lib/engine/surface-interactions.ts':[(10,76),(277,337),(360,372)],
 'src/lib/engine/surface-runtime.ts':[(138,145),(635,657),(674,707)],
 'src/lib/assets/manifest-v3.ts':[(14,51)],
 'src/lib/assets/manifest-v6.ts':[(1,39)],
 'src/lib/assets/pose-geometry.ts':[(40,71)],
 'src/lib/assets/animation-specification.ts':[(198,223)],
 'src/lib/assets/manifest.ts':[(64,87)],
 'src/lib/assets/shape.ts':[(32,49)]}
evidence=[]
for name in bath_files:
    f=UI/name
    if not f.exists():continue
    lines=f.read_text().splitlines()
    evidence.append({**fact(f),'excerpts':[{'startLine':a,'endLine':min(b,len(lines)),'text':'\n'.join(lines[a-1:b])} for a,b in snippets.get(name,[])]})
commit=run(['git','-C',str(UI),'rev-parse','HEAD']).get('stdout','').strip()
put('BATH-CONTRACT-FINDINGS.json',{
 'auditId':'BATH-SUPPORT-CONTRACT-AUDIT-1','status':'READ_ONLY_SOURCE_FINDINGS','repository':str(UI),'commit':commit,
 'freshMacState':'UNKNOWN','cloudLag':'Checked-in cloud snapshot only; current Mac geometry, source adoption and renderer may differ.',
 'authoredSceneGeometry':{'objectKind':'bath','width':100,'depth':54,'height':80,'slots':[{'id':'left','affordance':'bath','dx':-18,'dy':-68},{'id':'right','affordance':'bath','dx':18,'dy':-68}],'meaning':'World object slots; not source-image foot/water rows.'},
 'waterGeometry':{'basinAreaM2':0.12,'basinCapacityM3':0.006,'waterlineExpression':'topY + 3 - level * 6','topY':'first authored bath slot y, fallback authored.y - 68','level':'min(1, volumeM3 / 0.006)','waterRectangleWidth':88,'fixedSourceImageWaterPlane':False,'anatomicalBasinFloorRow':'NOT_EXPOSED in inspected source sprite contract'},
 'actionEvents':{'requestActionEnum':['drink','bath'],'runtimeStatusAnimationClip':['idle-fallback','bathing'],'bathDurationSeconds':3,'timingAuthority':'synthetic product tuning, explicitly not measured bird physiology','contactPayload':['actorId','slotId','kind','objectId','generation','revision','x','y'],'contactCoordinates':'Engine issues slot.x/slot.y after proximity/occupancy/wet/environment/generation validation; WeakMap-issued identity retained. Not an arbitrary source bill joint.','waterWithdrawal':'Drink emits mass withdrawal requests; bath contacts are cosmetic, not claimed ingestion.','sourcePoseSemanticBathEventField':'No per-pose splash/dip/feather event field found in inspected strict animationPoseSchema.'},
 'spriteContractBoundary':{'legacyActions':'V3 clips include optional bathing; named action alone is not scene adoption.','poseFields':['frame','durationTicks','pivot','contacts','poseId','rotation'],'contactKinds':['left-foot','right-foot','perch','ground'],'waterOrBillContactKindSupported':False,'shapeLandmarks':'Separate shape schema can name beak/head/body/tail/feet; a named landmark is not an authorized water contact or action event.','commonFamilyV6':'Requires neutral-only static idle and no contacts/activity clips. commonMotion blink/look cannot silently carry bathing.','worldAnchor':'poseTransform uses reviewed shape support if present, otherwise pivot; world position is support anchor, not sprite top-left.','missingClip':'Sampler may fall back to idle; does not prove bathing art or correct live binding.'},
 'producerHandoffRequirements':['Keep bird RGBA separate from pool/water/splash effect layer.','Retain source body/bill/feet landmark proposals, original canvas/density/pivot, source IDs and explicit authored pose clocks in source facts.','Importer must map actual reviewed support onto authored bath slot and dynamic waterline; source alpha positivity alone proves no support.','If phase-specific bill-water, basin-floor depth or splash event coupling is required, importer must select/extend an appropriate action contract; no unknown fields in current strict common-family manifest.','Use checked-in scene defaults for engineering proposals; do not ask Thomas to supply technical geometry.'],
 'unresolved':['Current live Mac bath/sprite mapping and geometry','Admitted bath-source action profile and actual source art quality','Per-phase toe/floor/waterline/bill event mapping and depth/occlusion review'],
 'writesToApplication':False,'runtimeAdmission':False,'physicalSupportReviewed':False,'supportWorld':None,'evidence':evidence})
put('inspection-time-receipt.json',{'recordedUTC':utc(),'observedEvidenceCollectionSeconds':round(time.monotonic()-START,3),'meaning':'Only this reproducible evidence collection script elapsed; excludes earlier reasoning/source reads and is NOT rig authoring/export/cleanup benchmark.','authoringSeconds':None,'exportSeconds':None,'cleanupMinutes':None,'actualNewNativeCalls':0,'actualNewDrawings':0,'actualNewSourceFamilies':0})
print(json.dumps({'status':'UNTESTED','mechanicalCompositorAvailable':True,'compatibleSparrowRigFound':False,'bathCommit':commit,'arm':str(P)}))
