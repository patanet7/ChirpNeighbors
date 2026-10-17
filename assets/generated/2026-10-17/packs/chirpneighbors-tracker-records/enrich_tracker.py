"""Regional proposal + scale/card/feedback tasks extend the single operational queue."""
from copy import deepcopy
from pathlib import Path
import json,re
def slug(s):return re.sub(r'[^a-z0-9]+','_',s.lower()).strip('_')
def enrich(q,R):
 plan=json.loads((R/'regional-source.json').read_text())
 for bird in plan['birds']:
  bird.setdefault('id',slug(bird['name']));bird.setdefault('taxon',None)
 q['regionalResearch']={'libraryFileId':'libfile_ee60f0733b488191b21792105a61b43b','version':plan['version'],'sourceSnapshot':'regional-source.json','scope':plan['scope'],'hierarchy':plan['hierarchy'],'contexts':plan['contexts'],'birdRoster':plan['birds'],'plantRoster':plan['plants'],'weatherAndPlantStates':plan['weather_and_plant_states'],'sources':plan['sources'],'status':plan['status'],'completionClaim':False}
 q['regionalPriority']['rosterStatus']='Sourced proposal imported in full:42 birds and63 plants; first-release proposal18 birds,27 regional/native plants and10 cultivated/indoor plants. Proposed scope, not completed assets.'
 q['regionalPriority']['firstReleaseComplete']=False
 existing={s['id'] for s in q['speciesRoster']}
 for bird in plan['birds']:
  if bird['id'] not in existing:
   q['speciesRoster'].append({'id':bird['id'],'scientificName':bird['taxon'],'scope':'San Diego regional proposal; '+bird['tier'],'variants':[{'id':'adult-default','status':'working assumption; sex/age variants not yet scoped'}],'physicalSize':None,'worldScale':None,'calibrationStatus':'unmeasured; source-backed biological calibration required'})
 base=next(deepcopy(r) for r in q['birdSlots'] if r['species']=='american_robin' and r['actualFrames']==0)
 common_actions=sorted({r['action'] for r in q['birdSlots']})
 directions=q['directionScope']['directions'];known_species={r['species'] for r in q['birdSlots']}
 for bird in plan['birds']:
  if bird['id'] in known_species:continue
  for action in common_actions:
   example=next(r for r in q['birdSlots'] if r['species']=='american_robin' and r['action']==action)
   for direction in directions:
    row=deepcopy(example);row.update(id=f"bird.{bird['id']}.{action}.{direction}.default",species=bird['id'],scientificName=bird['taxon'],direction=direction,variant='adult-default',state='queued',artCoverage='missing-authored-art',actualFrames=0,sourceFiles=[],batch=None,evidenceScope='regional research proposal; no generated source',assignedWorker='unassigned regional production')
    row['generation'].update(state='queued',actualCallCount=0,actualElapsedSeconds=None,estimateSeconds=q['estimateModel']['generationSeconds'] if direction=='right' else None);row['review'].update(state='pending',speciesFidelityAccepted=False,anchorsAccepted=False);row['cleanup']['state']='pending';row['sourceCanvas']=None;row['rootPivot']=None
    if direction not in ['right','left-mirrored'] and 'unsupported body direction in inspected contract' not in row['runtimeBlockers']:row['runtimeBlockers'].append('unsupported body direction in inspected contract')
    q['birdSlots'].append(row)
 aliases={'perch':'perching','branch perch':'perching','low perch':'perching','walk':'walk_or_ground_locomotion','ground walk':'walk_or_ground_locomotion','short flight':'flight','flapping flight':'flight','flight':'flight','hop':'hop','perch sing':'singing','ground peck':'ground_peck','burst takeoff':'takeoff','return':'return_arrival'}
 index={(r['species'],r['action'],r['direction']) for r in q['birdSlots']}
 for bird in plan['birds']:
  for sourceaction in bird['animation_slots']:
   action=aliases.get(sourceaction,slug(sourceaction))
   for direction in directions:
    if (bird['id'],action,direction) in index:continue
    row=deepcopy(base);row.update(id=f"bird.{bird['id']}.{action}.{direction}.default",species=bird['id'],scientificName=bird['taxon'],action=action,direction=direction,variant='adult-default',state='queued',artCoverage='missing-authored-art',actualFrames=0,sourceFiles=[],batch=None,evidenceScope='regional research action proposal',assignedWorker='unassigned regional production',runtimeSlot=None,runtimeSupport='species-specific-action-no-confirmed-runtime-slot',runtimeBlockers=['species-specific action mapping needs Mac contract confirmation'],requirementIds=['ART-014','ART-024'])
    row['generation'].update(state='queued',actualCallCount=0,actualElapsedSeconds=None,estimateSeconds=q['estimateModel']['generationSeconds'] if direction=='right' else None);row['review'].update(state='pending');row['cleanup']['state']='pending';row['sourceCanvas']=None;row['rootPivot']=None
    q['birdSlots'].append(row);index.add((bird['id'],action,direction))
 birdmap={b['id']:b for b in plan['birds']}
 for row in q['birdSlots']:
  bird=birdmap.get(row['species']);row['scaleCalibrationRef']='scale.'+row['species'];row['speciesCardRef']='card.'+row['species'];row['anatomyDriftReview']='open: fixed canvas/root registration is not biological scale or stable anatomy'
  if bird:
   row.update(regionalPack='san-diego-proposed-first-release' if bird['tier']=='first_complete_release' else 'regional-expansion-proposal',releaseTier=bird['tier'],habitatContext=bird['habitat'],regionalSeason=bird['regional_status'],plannedDiet=bird['feeding'],sourceReferences=bird['sources'])
   if row['action']=='seed_feeding' and 'seed' not in bird['feeding']:row['biologicalApplicability']='outside current regional diet proposal; species review before authoring'
   if row['action']=='insect_feeding' and bird['id']=='anna_s_hummingbird':row['biologicalApplicability']='tiny arthropod feeding needs appropriate choreography, not generic bug peck'
  if row['species'] in ['american_crow','common_raven'] and row['actualFrames']:
   row['review'].update(state='needs-revision',speciesFidelityAccepted=False);row['artCoverage']='candidate-needs-revision-owner-feedback';row['dependencies'].append('corvid correction preview and owner review; neutral palette/root fix not yet accepted')
 def citations(ids):return [dict(id=i,**plan['sources'][i]) for i in ids if i in plan['sources']]
 q['scaleCalibrations']=[];q['speciesCards']=[]
 for species in q['speciesRoster']:
  sid=species['id'];bird=birdmap.get(sid);refs=citations(bird['sources']) if bird else []
  q['scaleCalibrations'].append({'id':'scale.'+sid,'species':sid,'scientificName':species['scientificName'],'biologicalLengthCmRange':None,'wingspanCmRange':None,'bodyLengthMeasurementDefinition':'source-defined bill tip to tail; do not substitute pose-dependent opaque bbox width','sourceEvidence':[],'candidateMeasurementSources':refs,'lengthEvidenceStatus':'measurement source/numeric range pending species fact/scale research worker','chosenIndividualLengthCm':None,'commonWorldUnitsPerCm':None,'worldLengthUnits':None,'referencePosture':None,'pixelLandmarks':None,'sourcePixelsPerWorldUnit':None,'calibrationStatus':'unmeasured / not calibrated','allClipsMustReferenceThisCalibration':True,'anatomyDriftAccepted':False,'runtimeScaleOwner':'Mac implementation task','tests':[]})
  def field(value):return {'value':value,'citations':refs if value else [],'status':'imported sourced regional proposal; card-specific review pending' if value else 'not yet collected'}
  q['speciesCards'].append({'id':'card.'+sid,'species':sid,'scientificName':species['scientificName'],'displayName':bird['name'] if bird else sid.replace('_',' ').title(),'identification':field(None),'habitat':field(bird['habitat'] if bird else None),'regionSeason':field(bird['regional_status'] if bird else None),'diet':field(bird['feeding'] if bird else None),'behaviorTendencies':field(None),'calls':{'description':None,'recordings':[],'licenseEvidence':[],'status':'uncollected; no audio reuse permission inferred from bird facts'},'funFacts':[],'factResearchOwner':'parent species-card research worker','sourceDate':plan['prepared_date'],'evidenceScope':'source-linked regional plan imported; not independently reread source pages here','individualPersonality':{'status':'fictional product traits separate from species facts','factsInferredFromPersonality':False},'uiAffordance':{'proposal':'Info button on a resident or species-gallery card opens optional Learn panel','identificationHabitatDietBehaviorCallsFactsSections':True,'audioPlayOnlyWithReviewedLicense':True,'notConfirmedAtUserHome':True,'staged':False,'integrated':False,'MacTask':'01a14730-019a-7062-a294-ba507c06f004'}})
 q['plantSlots']=[r for r in q['plantSlots'] if r['species'] not in ['flowering_shrub_taxon_pending']]
 for plant in plan['plants']:
  pid=slug(plant.get('taxon') or plant['name']);indoor='indoor' in plant['category'] or 'indoor' in plant['context'];special=plant['art_states']
  # State labels preserve the sourced text; do not invent universal winter orange/snow states.
  states=[x.strip() for x in special.split(';') if x.strip()]
  for state in states:
   layers=['structure','foliage']+(['flower-fruit-seed'] if any(x in state for x in ['flower','fruit','seed','acorn','cone']) else [])
   for layer in layers:
    interactions=['calm'] if indoor else ['calm','wind-sway','wet-rain']
    for interaction in interactions:
     q['plantSlots'].append({'id':f'plant.{pid}.{slug(state)}.{layer}.{interaction}','family':'plant','species':pid,'scientificName':plant['taxon'],'displayName':plant['name'],'season':state,'health':'species-specific sourced-state proposal','structuralLayer':layer,'action':interaction,'direction':'n/a','variant':state+'/'+layer,'state':'queued','actualFrames':0,'requiredFrameCount':None,'plannedFrameCount':6 if interaction=='wind-sway' else 1,'plannedLoop':interaction=='wind-sway','sourceFiles':[],'runtimeSupport':'Mac layer/state mapping pending','assignedWorker':'parent botanical worker' if plant['name'] in ['Coast live oak','Toyon','California buckwheat'] else 'unassigned botanical production','requirementIds':['ART-029','ART-031','ART-032','ART-033','ART-034'],'releaseTier':plant['tier'],'regionalPack':'san-diego-proposed-first-release' if plant['tier']=='first_complete_release' else 'regional-expansion-proposal','origin':plant['origin'],'habitatContext':plant['context'],'sourceReferences':plant['sources'],'citations':citations(plant['sources']),'applicability':'managed indoor/container; no automatic outdoor weather/season' if indoor else 'species/context-specific state; no universal orange or lowland snow','dependencies':['source image and declared rights','stable root/structural registration','species-specific state review','Mac stage receipt'],'generationEstimateSeconds':q['estimateModel']['generationSeconds'] if interaction=='wind-sway' else None,'artisticCorrectionEstimate':None,'integration':{'staged':False,'integrated':False,'tests':[]}})
 q['plantSlotSourceNote']='Full63-plant research proposal decomposed using its explicit art-state strings and category/context. Row expansion is a production plan, not verified applicability of every layer/interaction. No outdoor wind/rain rows auto-assigned to indoor contexts.'
 q['ongoingFeedback']=[{'asset':'corvid-v1','before':'Owner rejected blue-looking wing color and offcenter walking; throat shaggy, weak gait and eye stylization remain','requestedCorrection':'neutral charcoal/gray palette and fixed torso/root registration','afterReported':'Worker reports neutral palette edit: blue-minus-red opaque-feather metric+22.11→-0.57; fixedscale0.44 torso-anchor translations; gait remains weak','afterEvidence':'parent relay of v2 bundle libfile_63a01559f3888191a0d19c146bbcdded; corrected GIF libfile_db7b4c52f8d08191a4efb4212f10fa18; not byte-inspected here','actualImprovementAccepted':False,'artState':'needs-revision','next':'inspect corrected preview before any art acceptance'},{'asset':'rain-continuity-v2','before':'v1 six unmeasured temporal patterns','requestedCorrection':'same streak field shifted(+4,+32) each phase with wrap','afterMeasured':'mean native-alpha streak-mask overlap0.0509977; loop edge0.0','receipt':'batches/rain-continuity-v2/continuity-review.json','actualImprovementAccepted':False,'artState':'needs-revision; temporal requirement failed','next':'stop repeated sheet edits; choose deterministic advected weather compositor or another measured generation approach with Mac'}]
 q['newOwnerRequirements']=[{'id':'owner-relay-scale-all-birds','requirement':'Per-species sourced physical size and calibration across every clip; fixed canvas is insufficient','status':'calibration records created; numeric evidence pending research'}, {'id':'owner-relay-optional-learning','requirement':'Optional sourced species facts with identification, habitat/region/season, diet, behavior, calls and fun facts; distinguish fictional personalities','status':'partial card records and local UI preview; complete research and app integration pending'}, {'id':'owner-relay-feedback-evaluation','requirement':'Track before/after feedback, rejections and measured improvement','status':'corvid rejection and failed rain continuity retained; no unsupported improvement claim'}]

 q['contractCoordination']={'status':'proposed production interchange; not agreed with Mac yet','authority':'Mac main implementation task owns shared typed catalog/contracts. This queue is a derived operational view; requirements and regional facts remain source-owned. Local generation receipts are primary evidence for local output only.','canonicalIdMappingStatus':'pending Mac species/family/variant/layer/clip/pack IDs; local semantic IDs are provisional','macTask':'01a14730-019a-7062-a294-ba507c06f004','interchangeFile':'production-handoff.json','interchangeVersion':'chirp-production-receipt-proposal@1','runtimeSlotDefinitionRef':q['runtimeContracts']['slotSourceSha256'],'requestedAgreement':['canonical species and asset-family IDs','supported action/direction slots and behavior mapping','runtime source density/frame/alpha budgets','scene layer and pack IDs','review/staging/import receipt schema'],'doNotImportBlindly':True,'perUserRecordsWritten':False,'domainSeparation':['sourced species facts and physical size','sourced regional/seasonal occurrence proposals','shared asset families/variants/layers/clips','per-user inventory/residents/layout and actual observations (not present here)']}
 q['regionalOccurrenceProposals']=[{'species':b['id'],'geographicHierarchy':plan['hierarchy'],'ecologicalContext':b['habitat'],'seasonalStatusText':b['regional_status'],'dateWindows':[],'monthLikelihood':None,'preciseDateWindowStatus':'not supplied; no numerical probability invented','provenance':citations(b['sources']),'confirmedAtUserHome':False,'actualObservationRef':None,'authority':'regional research proposal; pending shared catalog mapping'} for b in plan['birds']]
 q['queryInterface']={'script':'query_gaps.py','packs':['san-diego','expansion','all'],'missing':['clips','facts','license','scale','review','runtime','integration'],'semantics':'Queries use the same queue snapshot; missing art and unsupported runtime are separate. Candidate output never implies licensed/approved/integrated. Proposal slot count is not a completion denominator.'}
 q['scaleResearchPending']='Parent species-card/measurement worker researching18 core plus existing general birds. Numeric biological lengths, chosen individual sizes and world calibration remain null until sourced.'
 q['botanicalDeliveries'].append({'id':'san-diego-native-botanical-batch01','libraryFileId':'libfile_0f4f2a8543e481919091ff362fd57dce','previewLibraryId':'libfile_e58e4201456c8191af82459cb702ec87','sourceOriginals':6,'logicalRoles':['coast-live-oak-wood','coast-live-oak-evergreen-canopy','toyon-green-base','toyon-red-fruit-layer','california-buckwheat-flower','california-buckwheat-rust-seedheads'],'uniformDerivativeCanvas':[512,512],'state':'parent-reported packaged candidates; source bytes not inspected locally','reportedRootRegistration':'oak/toyon reused bases; buckwheat about3 sourcepx drift','reportedBuckwheatAlphaIoU':0.868,'accepted':False,'staged':False,'integrated':False,'scope':'first six sources; not complete regional roster'})
 q['estimateModel']['correctionObservations']=[{'batch':'rain-continuity-v2','imageCallSeconds':37.9,'result':'failed requested temporal continuity; no improvement accepted','correctionCycleEstimate':None}]
 q['gapQuerySummary']={}
 from query_gaps import query
 for pack in ['san-diego','expansion']:
  q['gapQuerySummary'][pack]={gap:len(query(q,pack,gap)) for gap in ['clips','facts','license','scale','review','runtime','integration']}

 facts=json.loads((R/'facts-source.json').read_text())
 q['factSourceAuthority']={'libraryFileId':'libfile_ad8beb182a508191836d65aa110aff31','version':facts['version'],'sourceSnapshot':'facts-source.json','scope':facts['scope'],'status':'source-owned fact catalog; imported view pending Mac canonical-ID contract','measurementPolicy':facts['measurement_policy']}
 card_index={c['species']:c for c in q['speciesCards']};scale_index={c['species']:c for c in q['scaleCalibrations']}
 for source in facts['facts']:
  sid=source['id'];card=card_index.get(sid);scale=scale_index.get(sid)
  if card:
   source_index={x['id']:x for x in source['sources']}
   for target,key in [('identification','identification'),('habitat','habitat'),('regionSeason','season'),('diet','diet'),('behaviorTendencies','behavior')]:
    ids=source['field_sources'].get(key,[]);card[target]={'value':source[key],'citations':[source_index[i] for i in ids if i in source_index],'status':'imported source-cited fact; canonical app integration pending'}
   card['funFacts']=source['fun_facts'];card['measurements']=source['measurements'];card['measurementCaveats']=source['measurement_caveats'];card['sourceConflicts']=source['source_conflicts'];card['sourceDate']=facts['prepared_date'];card['confidence']=source['confidence'];card['sources']=source['sources'];card['evidenceScope']='full20-card source catalog read; independent source-page recheck not performed in this task';card['individualPersonality']={'value':source['fictional_personality'],'status':'unset; fictional traits separate from sourced species tendencies'}
  if scale:
   length=source['measurements'].get('length');scale['publishedMeasurementEvidence']=source['measurements'];scale['sourceEvidence']=source['sources'];scale['sourceEndpointDefinition']=length.get('source_endpoint_definition') if length else None;scale['sourceConflicts']=source['source_conflicts'];scale['measurementCaveats']=source['measurement_caveats'];scale['lengthEvidenceStatus']='published values imported; anatomical endpoint undefined, matching asset landmarks missing';scale['calibrationStatus']='blocked: source endpoint definition and matched anatomical landmarks not established';scale['bodyLengthMeasurementDefinition']=None;scale['biologicalLengthCmRange']=[length['min'],length['max']] if length and length['kind']=='published_range' else None;scale['publishedLengthPointCm']=length['value'] if length and length['kind']=='published_point' else None;scale['measurementSexScope']=length.get('sex_scope') if length else None
 q['speciesCardResearchStatus']='20 source-cited cards fully read/imported into derived tracker preview; call recordings/licenses still absent; Mac canonical import and Learn panel integration pending'
 for pack in ['san-diego','expansion']:
  q['gapQuerySummary'][pack]={gap:len(query(q,pack,gap)) for gap in ['clips','facts','license','scale','review','runtime','integration']}

 if q.get('externalDemoIntegration'):
  observed={('blue_jay',a) for a in ['hop','drinking','takeoff','flight','landing']}|{('northern_cardinal',a) for a in ['seed_feeding','preening','hop','sleeping']}
  for row in q['birdSlots']:
   if (row['species'],row['action']) in observed and row['direction']=='right':
    row['state']='integrated';row['integration'].update(state='observed-demo-via-parent',staged=True,integrated=True,evidence=q['externalDemoIntegration'],productionArtApproval=False,exactReceiptPending=True);row['review']['speciesFidelityAccepted']=False
 q['localCounts']['externalDemoClipsObserved']=q.get('externalDemoIntegration',{}).get('observedClips',0)

 hf=[r for r in q['birdSlots'] if r['species']=='house_finch'];q['birdSlots']=[r for r in q['birdSlots'] if r['species']!='house_finch']
 for template in hf:
  for sex in ['male','female']:
   row=deepcopy(template);row['variant']='adult-'+sex;row['id']=row['id'].replace('.default','.'+row['variant']);row['appearanceVersion']='house-finch-canon-v1';row['scaleCalibrationRef']='scale.house_finch';row['variantSizeInference']='Both-sex published range only; no empirical sex-size difference inferred'
   if row['direction']=='right' and row['action'] in ['idle','seed_feeding']:
    action='idle' if row['action']=='idle' else 'feed';batch='house-finch-'+sex+'-'+action+'-v1';row.update(state='reviewed',actualFrames=6,sourceFiles=['batches/'+batch+'/manifest.json'],batch=batch,artCoverage='candidate-with-issues',evidenceScope='local generated/isolated/visually reviewed',assignedWorker='this visible cloud task',sourceCanvas=[1024,1024],rootPivot=[512,800]);row['generation'].update(state='generated',actualCallCount=1,actualElapsedSeconds=json.loads((R/'batches'/batch/'generation-receipt.json').read_text()).get('measuredCallLatencySeconds'));row['review'].update(state='candidate-with-issues',speciesFidelityAccepted=False,anchorsAccepted=False);row['cleanup']['state']='technical-isolation-complete';row['integration'].update(state='pending',staged=False,integrated=False);row['frameBank']='frame-bank.json';row['contactValidation']='heuristic annotations only; actual scene contact and scale review pending'
   q['birdSlots'].append(row)
 for r in q['speciesRoster']:
  if r['id']=='house_finch':r['variants']=[{'id':'adult-male','appearance':'house-finch-canon-v1','status':'generated candidate'},{'id':'adult-female','appearance':'house-finch-canon-v1','status':'generated candidate'}]
 q['frameBankSummary']={'file':'frame-bank.json','frames':56,'verifiedReuseCount':0,'clipReferencesImmutableFrameIds':True,'rejectedSequenceNotAutomaticFrameRejection':True}
 q['lessonsAndExperiments']={'file':'lessons-and-experiments.json','experiments':7,'status':'working/failure hypotheses linked to prompts, refs, outputs and tests; no unsupported acceptance'}
 for pack in ['san-diego','expansion']:
  q['gapQuerySummary'][pack]={gap:len(query(q,pack,gap)) for gap in ['clips','facts','license','scale','review','runtime','integration']}

 q['frameEvidence']=json.loads((R/'frame-bank.json').read_text())
 q['experimentEvidence']=json.loads((R/'lessons-and-experiments.json').read_text())

 q['frameBankSummary']['frames']=len(q['frameEvidence']['frames'])
 q['lessonsAndExperiments']['experiments']=len(q['experimentEvidence']['experiments'])
 q['perchReuseEvidence']=json.loads((R/'batches/house-finch-perching-review-v1/reuse-review.json').read_text())
 q['perchCandidateEvidence']=json.loads((R/'batches/house-finch-perching-candidate-v1/candidate-review.json').read_text())
