from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib,math,shutil
P=Path(__file__).parent;S=Path('/workspace/asset-production/new-species/sd20-three-canon-v1');M=json.loads((S/'intake-manifest.json').read_text());COMMIT='a8d3666e293047efaf7f162a1e2b069f346fc18d'
sha=lambda b:hashlib.sha256(b).hexdigest()
def dump(path,v):path.write_text(json.dumps(v,indent=2)+'\n')
rows=[]
for f in M['frames']:
 species=f['id'];out=P/species;out.mkdir(exist_ok=True);im=Image.open(S/f['outputPNG']).convert('RGBA');assert sha((S/f['outputPNG']).read_bytes())==f['outputPNGsha256'];density=f['presentationDensityPxPerWorldUnit'];pivot=[57,75]
 # Nearest visible output pixel to supplied approximate bill proxy; preserve both.
 proxy=f['outputBeakTipApprox'];candidates=[(x,y) for y in range(max(0,int(proxy[1])-7),min(96,int(proxy[1])+8)) for x in range(max(0,int(proxy[0])-7),min(96,int(proxy[0])+8)) if im.getpixel((x,y))[3]>=128];tip=min(candidates,key=lambda p:(p[0]-proxy[0])**2+(p[1]-proxy[1])**2)
 beakoffset=[(tip[i]-pivot[i])/density for i in [0,1]];root=[200,330];target=[root[i]+beakoffset[i] for i in [0,1]]
 shutil.copyfile(S/f['outputPNG'],out/'source-idle96.png');shutil.copyfile(S/species/'texture-review-manifest.json',out/'texture-review-manifest.json')
 if species=='anna_s_hummingbird':
  movement={'kind':'not available from folded-wing canon','planned':True,'packetBound':False,'appBound':False,'videoViewed':False,'recipe':'Remain on owned perch; no dart, hover, flight displacement or flap claim. Await species wing source.'}
  interaction={'kind':'perched flower-tip visual alignment proof only','targetType':'flower opening proxy at existing upright bill height','targetWorld':target,'resourceEvent':False,'ingestionPhysics':False,'sourcePoseSuitableForRealNectarProbe':False,'planned':True,'packetBound':True,'appBound':False,'videoViewed':False}
 else:
  distance,height=(18,6) if species=='black_phoebe' else (24,8);airTicks=12
  keys=[]
  for tick in range(31):
   if tick<=9:u=0;support='start-ground'
   elif tick<21:u=(tick-9)/airTicks;support=None
   else:u=1;support='end-ground'
   keys.append({'tick':tick,'rootWorld':[root[0]+distance*u,root[1]-4*height*u*(1-u)],'groundPlaneWorld':[root[0]+distance*u,root[1]],'presentationLiftWorld':-4*height*u*(1-u),'supportId':support,'sourceFrameId':f['sourceFrameId'],'rotationRadians':0,'scaleWorldPerOutputPx':1/density})
  movement={'kind':'bounded rigid-source ground-hop transform proof','planned':True,'packetBound':True,'appBound':False,'videoViewed':False,'tickRate':30,'startGroundTicks':[0,9],'airborneTicks':[10,20],'landedTicks':[21,30],'airborneEndpointTicks':[9,21],'distanceWorld':distance,'heightWorld':height,'sourceFrameReuse':'one identical standing drawing; no crouch/toe-flex/landing drawings, tail-pump or wing animation','supportPolicy':'root stationary throughout both grounded intervals; null support while airborne; reserve landing before release; cancellation must retain/reacquire a valid owned support','keyframes':keys,'quietMode':'hold current valid support; do not translate a planted still pose'}
  if species=='black_phoebe':interaction={'kind':'perched insect-marker inspection only','targetType':'decorative insect proxy at bill height; not airborne capture','targetWorld':target,'resourceEvent':False,'ingestionPhysics':False,'planned':True,'packetBound':True,'appBound':False,'videoViewed':False}
  else:interaction={'kind':'look at ground seed; ground peck missing','targetType':'decorative ground seed proxy','targetWorld':[root[0]+28,root[1]],'beakWorldAtRest':target,'beakGroundVerticalGapWorld':-beakoffset[1],'minimumRigidPivotRotationToGroundRadians':math.atan2(-beakoffset[1],beakoffset[0]),'currentV3V4V5PoseRotationLimitRadians':.5,'resourceEvent':False,'ingestionPhysics':False,'planned':True,'packetBound':True,'appBound':False,'videoViewed':False,'missing':'head-down/beak-contact source; upright still cannot honestly count as peck or leaf-litter scratch'}
 row={'species':species,'sourceFrameId':f['sourceFrameId'],'outputRgbaFrameId':f['outputFrameRGBAId'],'outputPNGsha256':f['outputPNGsha256'],'sourcePNGsha256':f['sourcePNGsha256'],'sourceOriginalSHA256':M['originalSHA256'],'sourceOriginalCanonicalRef':'assets/generated/2026-10-17/packs/NOT_ASSUMED; use parent-source original bytes and intake manifest','sourcePacketLocal':str(S),'outputPixelPivot':pivot,'densityPxPerWorldUnit':density,'canvasWorld':f['worldCanvas'],'rootWorldExample':root,'bill':{'suppliedApproxOutputPx':proxy,'snappedVisibleAlpha128OutputPx':list(tip),'outputSnapDistancePx':math.dist(proxy,tip),'worldOffsetFromPivot':beakoffset,'anatomicalEndpointApproved':False,'approximateWorldPositionAtExampleRoot':target},'footContactsOutputPx':f['contacts'],'idle':{'kind':'static source hold','packetBound':True,'appBound':False,'videoViewed':False},'movement':movement,'interaction':interaction,'newDrawings':0}
 dump(out/'binding-recipe.json',row);rows.append(row)

contracts={'repository':'patanet7/birdsong-yard-sprites','commit':COMMIT,'fixedStepSeconds':1/30,'currentSeams':[
 {'path':'src/lib/engine/simulation.ts','symbols':['requestPreviewGroundActivity','setPreviewSurfaceAdmission'],'constraint':'preview actor must be placed and own settled ground; no pending route/destination; shortest clear ground path and target within120worldunits; daylight/no shelter environment; actual clearance/occupancy must be checked by app'},
 {'path':'src/lib/engine/renderer.ts','symbol':'flightLift','constraint':'current hop uses -5*abs(sin(behaviorTicks*pi/8))*min(1,remaining/12); actor route root advances continuously, so source packet alone cannot establish stationary feet at sine zeros'},
 {'path':'src/lib/engine/review-texture.ts','symbol':'YardReviewTexture','constraint':'clipId idle only; optional paint has no actor/support/physics/catalog authority; normal source manifests retained with no forged movement clip'},
 {'path':'src/lib/assets/manifest.ts','symbols':['sampleClip'],'constraint':'V3/V4/V5 sample pose may reuse frame with pivot/contacts/rotation; clip does not own root trajectory'},
 {'path':'src/lib/assets/clip-transitions.ts','symbol':'resolveClipTransition','constraint':'immediate cuts; authoredTransition false; blending false; durationTicks0; caller supplies known support identity'},
 {'path':'src/lib/assets/manifest-v3.ts','symbol':'animationPoseSchema','constraint':'rotation -0.5..0.5rad; contact kinds left-foot/right-foot/perch/ground; no beak/flower/insect contact semantics'},
 {'path':'src/lib/assets/pose-geometry.ts','symbols':['poseTransform','sourceWorldScale'],'constraint':'world origin is support anchor, not sprite top-left; apply mirroring thenrotation; V4/V5 world scale=1/presentation.sourcePixelsPerWorldUnit'}],
 'macBindingRecipe':['Admit unchanged source atlas/idle manifest through actual Sharp canonical intake first.','Bind only a transient explicit preview actor with real placement and clearance; do not equate review paint with actor admission.','For Phoebe/Towhee hop, reserve a clear owned landing ground support18/24worldunits away. Start exactly on owned ground.','Use provided 30Hz sample table as a bounded acceptance recipe: hold root on ground, unsupported parabolic displacement only, then snap neither scale nor source to fit landing; settle endpoint exactly. Current app may need this explicit trajectory seam; packet does not implement it.','Switch idle→moving→idle at behavior-clock0 with explicit support IDs. Existing transition helper reports immediate cuts and no authored recovery. A missing moving drawing can be an honestly labelled static-source rigged hop.','Reduced-motion holds a valid settled support and source pose, never a visibly sliding planted still.','Place example decorative targets at exact proxy world coordinates; flower/insect target lies at upright bill height. Towhee groundseed remains a look target with about50worldunit bill gap; do not emit feeding/ingestion events.','Verify actual yard playback, contacts, scale and interruption/reduced-motion behavior on Mac before labeling appBound or videoViewed.'],
 'scope':'recipe and isolated transform proof; not runtime schema, alternate renderer, bound action package or new engine',
 'newGenerationCalls':0,'newDrawings':0,'canonicalSharpReceipt':None}
dump(P/'contract-handoff.json',contracts);dump(P/'intake.json',{'contractCommit':COMMIT,'sourceBatchId':M['batchId'],'candidates':rows,'status':'packet-bound geometry and source reuse only; all app-bound and video-viewed flags false','newGenerationCalls':0,'newDrawings':0})

# A pre-rendered GIF is an explicitly labelled motion proof, never an alternate yard engine.
proof=[]
for tick in range(31):
 panel=Image.new('RGBA',(900,250),(231,229,211,255));d=ImageDraw.Draw(panel);d.text((12,8),'STATIC-SOURCE TRANSFORM PROOF — not the app yard; no new drawings',fill=(32,35,27))
 for k,row in enumerate(rows):
  spec=row['species'];density=row['densityPxPerWorldUnit'];im=Image.open(P/spec/'source-idle96.png').convert('RGBA');size=round(96/density);display=im.resize((size,size),Image.Resampling.NEAREST);base=[150+k*300,174];movement=row['movement'];delta=[0,0]
  if 'keyframes' in movement:
   key=movement['keyframes'][tick];delta=[key['rootWorld'][i]-row['rootWorldExample'][i] for i in [0,1]]
  px=round(base[0]+delta[0]-57/density);py=round(base[1]+delta[1]-75/density);panel.alpha_composite(display,(px,py));d.line((k*300+20,174,k*300+280,174),fill=(113,124,83),width=1)
  d.text((k*300+20,30),spec.replace('_',' '),fill=(32,35,27));d.text((k*300+20,204),'perched static / flower-tip proxy' if k==0 else ('rigged hop / insect inspection' if k==1 else 'rigged hop / ground-seed look'),fill=(32,35,27));d.text((k*300+20,224),'wing motion missing' if k==0 else 'single still reused; app binding pending',fill=(32,35,27))
  target=row['interaction']['targetWorld'];tx=base[0]+target[0]-200;ty=base[1]+target[1]-330;d.ellipse((tx-2,ty-2,tx+2,ty+2),fill=(188,92,51))
 proof.append(panel.convert('RGB'))
proof[0].save(P/'normal-size-transform-proof.gif',save_all=True,append_images=proof[1:],duration=[100 if i%3 else 130 for i in range(31)],loop=0,optimize=False)
dump(P/'proof-qualification.json',{'kind':'pre-rendered source-transform proof; not actual yard','tickRateSourceRecipe':30,'gifPlayback':'slowed approx3.5seconds for inspection; GIF10ms quantization, not realtime30Hz','newDrawings':0,'sourceCanons':3,'wholeBirdRigidTranslationOnly':True,'anatomicalAnimation':False,'appBound':False,'videoViewed':False})
print(json.dumps({'species':[r['species'] for r in rows],'contractCommit':COMMIT,'newDrawings':0,'proof':'normal-size-transform-proof.gif'}))
