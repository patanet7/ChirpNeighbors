"""Project reviewed source overlays with exact atlas/source mappings; never infer live Mac binding.

Default output is this script's directory. Coordinator publication must explicitly supply
--output-dir <canonical release directory>. Running the audit does not alter art or app files.
"""
from pathlib import Path
from collections import Counter,defaultdict
import argparse,json,copy,hashlib,datetime
from PIL import Image
P=argparse.ArgumentParser(description=__doc__);P.add_argument('--root',type=Path,required=True);P.add_argument('--output-dir',type=Path,default=Path(__file__).resolve().parent);P.add_argument('--apply',action='store_true',help='Coordinator only: write CURRENT-SLOT-INVENTORY.json/MD instead of proposed outputs into explicitly supplied output directory');args=P.parse_args();root=args.root.resolve();out=args.output_dir.resolve();out.mkdir(parents=True,exist_ok=True)
sha=lambda b:hashlib.sha256(b).hexdigest()
def rid(im):return 'frame.sha256.'+sha(f'RGBA8;{im.width}x{im.height};'.encode()+im.convert('RGBA').tobytes())
def read(p):return json.loads((root/p).read_text())
def save(p,j):(out/p).write_text(json.dumps(j,indent=2,ensure_ascii=False)+'\n')
def safe(p):
 p=(root/p).resolve();assert p.is_relative_to(root),p;assert p.is_file(),p;return p
release='release/animation-checkpoint-1-20261017';baseline=read('audits/animation-slot-inventory-20261017/inventory.json');current=read(release+'/CURRENT-SLOT-INVENTORY.json');overlay=read(release+'/intake-overlay.json');bank=read('frame-bank.json');byid={b['id']:b for b in baseline['species']};bankids={f['frameId']:f for f in bank['frames']};images={};pngsByHash=defaultdict(list);mapping=defaultdict(list);checks=[];issues=[]
def rgba(p):
 p=Path(p)
 if p not in images:images[p]=Image.open(p).convert('RGBA')
 return images[p]
def add(export,sourceID,evidence,source=None,phase=None,method='recorded explicit export verified by pixels'):
 p=safe(export);im=rgba(p)
 if source:
  sp=safe(source);actual=rid(rgba(sp));assert actual==sourceID,(source,sourceID,actual)
 entry={'sourceFrameId':sourceID,'sourcePNG':source or(bankids[sourceID]['file'] if sourceID in bankids else None),'outputPNG':export,'outputPNGsha256':sha(p.read_bytes()),'outputRGBAId':rid(im),'evidence':evidence,'phase':phase,'mappingMethod':method}
 if entry not in mapping[rid(im)]:mapping[rid(im)].append(entry)
# Preserve the frozen baseline export mapping, but re-read actual output pixels.
for path,pkg in baseline['preparedPackages'].items():
 for frame in pkg['sourceFrameMappings']:
  for m in frame['sourceMappings']:add(m['exportPNG'],m['sourceFrameId'],m['mappingEvidence'],phase=m.get('phase'))
# Exact primary IDs are reusable source records. Registered/output derivatives are not added as new drawings.
primaries={}
for b in overlay['batches']:
 path=b['primaryManifest'];j=read(path);parent=Path(path).parent;primaries[path]=j
 for field in ['frames','reusedFrames']:
  for f in j.get(field,[]):
   sid=f['sourceFrameId'];source=str(parent/f['sourcePNG']);sp=safe(source);actual=rid(rgba(sp));expectedHash=f.get('sourcePNGsha256');checks.append({'kind':'primary-source-identity','manifest':path,'sourcePNG':source,'expectedSourceID':sid,'actualSourceID':actual,'pass':actual==sid and(not expectedHash or sha(sp.read_bytes())==expectedHash),'newDrawing':field=='frames'})
   assert actual==sid,(path,source,sid,actual)
   if f.get('outputPNG'):add(str(parent/f['outputPNG']),sid,path,source,f.get('pose'))
   # Some primary records omit export mapping. Accept only exact nearest full-canvas pixel matches,
   # never name/silhouette guesses, across declared small output images.
   else:
    for candidate in j.get('outputMetadata',[]):
     if not isinstance(candidate,str) or not candidate.endswith('.png'):continue
     cp=root/parent/candidate
     if not cp.is_file():continue
     ci=rgba(cp);si=rgba(sp)
     if ci.width!=ci.height or ci.width>512 or si.width!=si.height:continue
     resized=si.resize(ci.size,Image.Resampling.NEAREST)
     if resized.tobytes()==ci.tobytes():add(str(parent/candidate),sid,path,source,f.get('pose'),'exact full-source nearest resize matches declared export RGBA')
# Manifest source.sha256 is the exact atlas file hash. Resolve actual files by that hash.
for p in sorted(root.rglob('*.png')):pngsByHash[sha(p.read_bytes())].append(str(p.relative_to(root)))
packages={}
def package(man,preferredAtlas=None):
 if man in packages:return packages[man]
 p=safe(man);j=read(man);expected=j.get('source',{}).get('sha256');candidates=pngsByHash.get(expected,[]);local=[x for x in candidates if Path(x).parent==Path(man).parent]
 if preferredAtlas in candidates:atlas=preferredAtlas
 elif len(local)==1:atlas=local[0]
 elif len(candidates)==1:atlas=candidates[0]
 else:raise RuntimeError(f'Atlas hash resolution ambiguous/missing {man}: {candidates}')
 im=rgba(root/atlas);assert list(im.size)==[j['atlas']['width'],j['atlas']['height']],man;fm=[]
 for f in j['frames']:
  r=f['sourceRect'];tile=im.crop((r['x'],r['y'],r['x']+r['width'],r['y']+r['height']));matches=mapping.get(rid(tile),[]);sids=list(dict.fromkeys(x['sourceFrameId'] for x in matches));assert len(sids)==1,(man,f['id'],sids)
  assert abs(f['world']['width']*f['sourcePixelsPerWorldUnit']-f['canvas']['width'])<1e-6
  assert abs(f['world']['height']*f['sourcePixelsPerWorldUnit']-f['canvas']['height'])<1e-6
  contacts=[]
  for c in f.get('contacts',[]):
   assert set(c)=={'id','x','y'},(man,c);alpha=tile.getpixel((c['x'],c['y']))[3];assert alpha>0
   contacts.append({**c,'sampledAlpha':alpha,'anatomicallyApproved':False})
  fm.append({'outputFrameId':f['id'],'outputRGBAId':rid(tile),'sourceFrameId':sids[0],'exactExportMappings':matches,'sourceRect':r,'canvas':f['canvas'],'world':f['world'],'sourcePixelsPerWorldUnit':f['sourcePixelsPerWorldUnit'],'pivot':f['pivot'],'contacts':f.get('contacts',[]),'alphaContactChecks':contacts})
 byframe={f['outputFrameId']:f for f in fm};clips=[]
 for c in j['clips']:
  seq=[]
  for step in c['frames']:seq.append({**step,'sourceFrameId':byframe[step['frameId']]['sourceFrameId'],'outputRGBAId':byframe[step['frameId']]['outputRGBAId']})
  clips.append({**c,'orderedSourceFrameSequence':seq,'durationTicks':sum(s['durationTicks'] for s in seq),'durationSeconds':sum(s['durationTicks'] for s in seq)/c['tickRate'],'uniqueSourceFrameIds':list(dict.fromkeys(s['sourceFrameId'] for s in seq))})
 pkg={'manifest':man,'manifestSHA256':sha(p.read_bytes()),'atlasPNG':atlas,'atlasSHA256':sha((root/atlas).read_bytes()),'atlasDimensions':list(im.size),'scope':j.get('scope'),'profile':j.get('profile'),'approval':j.get('approval'),'activation':j.get('activation'),'frames':fm,'clips':clips,'appBinding':'UNKNOWN','actualYardVerification':'UNKNOWN','technicalShapeIsArtOrPhysicsApproval':False};packages[man]=pkg;return pkg
# Verify all retained baseline action packages as well as primaryidle selections.
for man,pkg in baseline['preparedPackages'].items():package(man,pkg['atlasPNG'])
# Rebuild baseline primary packages and source geometry projections from exact manifests.
for bird in baseline['species']:
 bird['baselineSourceIssues']=list(bird['sourceIssues']);bird['currentSourceIssues']=[];bird['sourceIssues']=list(bird['sourceIssues']);bird['nextAssignedTask']=None
 for row in bird['slots']:row['newAssignment']=None
 package(bird['primaryManifest'],bird['primaryAtlas'])
def clip(pkg,id='idle'):return next(c for c in pkg['clips'] if c['id']==id)
def binding(pkg,c,neutralHold=False):
 result={'manifest':pkg['manifest'],'atlasPNG':pkg['atlasPNG'],'clipId':c['id'],'tickRate':c['tickRate'],'loop':c['loop'],'durationTicks':c['durationTicks'],'orderedSourceFrameSequence':c['orderedSourceFrameSequence'],'contactsMeaning':'technical alpha markers, not physical support approval','appBinding':'UNKNOWN','actualYardVerification':'UNKNOWN'}
 if neutralHold:
  first=c['orderedSourceFrameSequence'][0]
  result.update(selectionMode='single-open-frame-hold-only',sourceClipId=c['id'],sourceClipScheduleUsed=False,orderedSourceFrameSequence=[{**first,'durationTicks':None}],durationTicks=None,sourceClipFirstStepDurationTicks=first['durationTicks'],loop=False,projectionOnly=True)
 return result
def render_manifest(batch,primary,parent):
 seen=set()
 def resolve(value,base=parent):
  if not isinstance(value,str) or not value.endswith('.json'):return []
  p=root/value
  if not p.is_file():p=root/base/value
  if not p.is_file():return []
  rel=str(p.relative_to(root))
  if rel in seen:return []
  seen.add(rel);j=read(rel)
  if j.get('profile')=='chirp-texture-review-v1':return [rel]
  found=[]
  def visit(x):
   if isinstance(x,dict):
    for k,v in x.items():
     if isinstance(v,str) and v.endswith('.json'):found.extend(resolve(v,Path(rel).parent))
     elif isinstance(v,(dict,list)):visit(v)
   elif isinstance(x,list):
    for v in x:visit(v)
  visit(j);return found
 for field in ['renderManifest','frameToActionMap','frameToActionMapPath','frameToActionMapManifest']:
  if batch.get(field):
   found=list(dict.fromkeys(resolve(batch[field])))
   if len(found)==1:return found[0]
   if found:raise RuntimeError('Ambiguous explicit render manifest '+str(found))
 candidates=[]
 for value in primary.get('outputMetadata',[]):candidates.extend(resolve(value))
 default=str(parent/'texture-review-manifest.json')
 if (root/default).is_file():candidates.append(default)
 candidates=list(dict.fromkeys(candidates));animated=[p for p in candidates if any(len(set(s['frameId'] for s in c['frames']))>1 for c in read(p).get('clips',[]))]
 if len(animated)==1:return animated[0]
 if len(candidates)==1:return candidates[0]
 raise RuntimeError('Missing/ambiguous render manifest; coordinator must set renderManifest: '+str(candidates))
def semantic_sequence(c,action,ids):
 seq=c['orderedSourceFrameSequence'];first=seq[0]['sourceFrameId']
 if action=='neutral':return [seq[0]]
 if action=='blink':
  closed=[i for i,x in enumerate(seq) if any(t in x['frameId'].lower() for t in ['blink','closed','half']) and x['sourceFrameId']!=first]
  if not closed:closed=[i for i,x in enumerate(seq) if x['sourceFrameId']!=first and x['sourceFrameId'] in ids]
  if not closed:return []
  end=next((i for i in range(max(closed)+1,len(seq)) if seq[i]['sourceFrameId']==first),max(closed))
  start=max([i for i in range(min(closed)) if seq[i]['sourceFrameId']==first] or[0]);return seq[start:end+1]
 if action=='look':
  targets=[i for i,x in enumerate(seq) if x['sourceFrameId'] in ids and x['sourceFrameId']!=first]
  if not targets:return [x for x in seq if x['sourceFrameId'] in ids]
  start=max([i for i in range(min(targets)) if seq[i]['sourceFrameId']==first] or[0]);end=next((i for i in range(max(targets)+1,len(seq)) if seq[i]['sourceFrameId']==first),max(targets));return seq[start:end+1]
 return seq
def assign(row,ids,sequence,paths,pkg=None,c=None):
 row['sourceFrameIds']=list(dict.fromkeys(ids));row['uniqueKnownSourceIDs']=len(row['sourceFrameIds']);row['orderedSourceFrameSequence']=sequence;row['evidencePaths']=paths;row['preparedPackagePaths']=[pkg['manifest']] if pkg else paths;row['renderBindings']=[binding(pkg,c,neutralHold=row['slot']=='neutral')] if pkg else[];row['newAssignment']=None;row['productionAccepted']=False;row['appBinding']='UNKNOWN';row['actualYardVerification']='UNKNOWN'
# Replay reviewed overlays once. A closure-only batch affects blink only; it adds no neutral coverage.
for b in overlay['batches']:
 primary=primaries[b['primaryManifest']];parent=Path(b['primaryManifest']).parent
 for sid in b.get('speciesIds',[]):
  bird=byid[sid];bird['currentSourceIssues'].append(b['scope']);bird['sourceIssues']=['Baseline PR33: '+x for x in bird['baselineSourceIssues']]+['Current checkpoint: '+x for x in bird['currentSourceIssues']];rows={r['slot']:r for r in bird['slots']};new=[f for f in primary['frames'] if f.get('speciesId')==sid];newIDs=[f['sourceFrameId'] for f in new]
  if b['slot']=='ordinary_locomotion':
   motionPath=str(parent/'motion-manifest.json');motion=read(motionPath);poses={f['pose']:f for f in primary['frames']+primary.get('reusedFrames',[]) if f.get('playbackRole','')!='immutable comparison only; excluded from hop due cross-original proportion discontinuity'}
   seq=[]
   if 'sourcePoseSequence' in motion:
    for s in motion['sourcePoseSequence']:seq.append({'sourceFrameId':poses[s['pose']]['sourceFrameId'],'outputFrameId':s['outputFrameId'],'pose':s['pose'],'durationTicks':s['durationTicks']})
   else:
    for t in motion['ticks']:
     pose=t['pose'];f=poses[pose]
     if seq and seq[-1]['sourceFrameId']==f['sourceFrameId']:seq[-1]['durationTicks']+=1
     else:seq.append({'sourceFrameId':f['sourceFrameId'],'outputFrameId':f.get('outputFrameId',f.get('outputRGBAId')),'pose':pose,'durationTicks':1})
   ids=list(dict.fromkeys(s['sourceFrameId'] for s in seq));assign(rows['locomotion'],ids,seq,[b['primaryManifest'],motionPath,b['review']]);rows['locomotion'].update(state='provisional-drawn-one-shot-hop-study-contact-unbound',provisionalUsefulSourceForThisSemanticSlot=True,batchNewDrawings=len(newIDs),newSourceFrameIds=newIDs,reusedSourceFrameIds=[i for i in ids if i not in newIDs],motionClipId=motion.get('clipId',motion.get('action')),tickRate=motion['tickRate'],durationTicks=motion['totalTicks'],loop=False,packetBindingReady=False,remainingPhasesOrReview=[b['scope'],'Canonical Mac admission, actor binding and actual-yard verification unknown here.'])
   assert sum(s['durationTicks'] for s in seq)==motion['totalTicks']
  else:
   man=render_manifest(b,primary,parent);pkg=package(man);c=clip(pkg);first=c['orderedSourceFrameSequence'][0];isStudy=sid=='nuttall_s_woodpecker';hasNewNeutral=any(any(t in f.get('pose','').lower() for t in ['neutral','awake','open-eye']) and not any(t in f.get('pose','').lower() for t in ['closed','blink']) for f in new)
   held=b.get('newSourceHeld') is True or primary.get('newSourceHeld') is True or b.get('sourceHeld') is True or primary.get('sourceHeld') is True or('usefulSourceSlotsCompleted' in b and b['usefulSourceSlotsCompleted']==[])
   affected=['blink'] if held else ['neutral','look'] if isStudy else ['neutral','blink'] if hasNewNeutral else ['blink']
   for action in affected:
    row=rows[action];row['baselineState']=row['state'];seq=[first] if action=='neutral' else c['orderedSourceFrameSequence'];assign(row,[s['sourceFrameId'] for s in seq],seq,[b['primaryManifest'],man,b['review']],pkg,c);row['remainingPhasesOrReview']=[b['scope'],'Canonical Mac admission, actor binding and actual-yard verification unknown here.'];row['newSourceFrameIds']=[i for i in row['sourceFrameIds'] if i in newIDs];row['reusedSourceFrameIds']=[i for i in row['sourceFrameIds'] if i not in newIDs]
    if held:
     row.update(state='new-drawn-blink-held-source-study',provisionalUsefulSourceForThisSemanticSlot=False,newSourceHeld=True,sourceHeld=True)
     for rb in row['renderBindings']:rb.update(held=True,useAsActiveSource=False)
    elif isStudy:row.update(state='inclined-support-endpoint-hypothesis-vertical-unresolved',provisionalUsefulSourceForThisSemanticSlot=False)
    else:row.update(state='provisional-drawn-'+action,provisionalUsefulSourceForThisSemanticSlot=True)
   if not isStudy and not held:
    if not hasNewNeutral:assert first['sourceFrameId'] in rows['neutral']['sourceFrameIds'],('Closure-only open source differs from existing neutral; do not silently replace',sid,first['sourceFrameId'],rows['neutral']['sourceFrameIds'])
    bird['primaryIntakeStatus']='provisional-source-review-candidate';bird['primaryManifest']=man;bird['primaryAtlas']=pkg['atlasPNG'];bird['selectedIdleSourceIDs']=c['uniqueSourceFrameIds']
    if not hasNewNeutral:bird.setdefault('overlayQualifications',[]).append('Closure-only source batch: existing awake source reused; neutral coverage unchanged; no new neutral drawing counted.')
# Attach exact primary packages, keeping each neutral single-open and each blink actualordered states.
for bird in baseline['species']:
 pkg=package(bird['primaryManifest'],bird['primaryAtlas']);c=clip(pkg);first=c['orderedSourceFrameSequence'][0];bird['primaryAtlas']=pkg['atlasPNG'];bird['primaryManifestSHA256']=pkg['manifestSHA256'];bird['primaryAtlasSHA256']=pkg['atlasSHA256'];bird['primaryClipId']=c['id'];bird['selectedIdleSourceIDs']=c['uniqueSourceFrameIds'];bird['primaryFrameMappings']=pkg['frames'];rows={r['slot']:r for r in bird['slots']}
 # Keep Nuttall's new alternate support hypothesis separate from its historical primary study.
 if bird['id']!='nuttall_s_woodpecker':
  row=rows['neutral'];row['sourceFrameIds']=[first['sourceFrameId']];row['uniqueKnownSourceIDs']=1;row['orderedSourceFrameSequence']=[first];row['renderBindings']=[binding(pkg,c,neutralHold=True)]
 # Preserve exact look-package references; no automatic splice into a new neutral/blinkpair.
 for row in bird['slots']:
  if row['slot']=='look' and row.get('sourceFrameIds'):
   man=next((p for p in row['evidencePaths'] if p.endswith('.json') and 'texture-review-manifest' in p),None)
   if man:
    lp=package(man);lc=clip(lp);seq=semantic_sequence(lc,'look',row['sourceFrameIds']);row['orderedSourceFrameSequence']=seq;row['renderBindings']=[binding(lp,lc)]
  if row['slot']=='blink' and row['state']=='provisional-drawn-blink' :
   seq=semantic_sequence(c,'blink',row['sourceFrameIds']);row['orderedSourceFrameSequence']=seq;row['renderBindings']=[binding(pkg,c)]
  if row['slot'] not in ['neutral','look','blink'] and not row.get('renderBindings'):
   bindings=[]
   for man in row.get('evidencePaths',[]):
    if man in packages:
     ap=packages[man];ac=max(ap['clips'],key=lambda cl:len(set(cl['uniqueSourceFrameIds'])&set(row['sourceFrameIds'])))
     bindings.append(binding(ap,ac));row['orderedSourceFrameSequence']=ac['orderedSourceFrameSequence']
    elif man.endswith('/manifest.json') and (root/man).is_file():
     source=read(man)
     if source.get('kind')=='production-clip-proposal-not-app-wire-format':bindings.append({'sourceProposalManifest':man,'clipId':source['clipId'],'action':source.get('action'),'loop':source.get('loop'),'orderedSourceFrameSequence':source['frames'],'appBinding':'UNKNOWN','actualYardVerification':'UNKNOWN','canonicalRenderPacket':False})
   if bindings:row['renderBindings']=bindings
 fs=[f for f in bank['frames'] if f.get('species')==bird['id']];bird['nativeBankDrawings']=len(fs);bird['nativeSourceRecords']=fs
 # Check every referenced source/evidence path resolves within canonical source root.
 for row in bird['slots']:
  for p in row.get('evidencePaths',[]):safe(p)
slots=[s for b in baseline['species'] for s in b['slots']];idle=Counter(s['slot'] for s in slots if s['provisionalUsefulSourceForThisSemanticSlot'] and s['slot'] in ['neutral','look','blink']);baseline['kind']='Current source-only slot overlay with verified atlas/source sequence projections';baseline['currentOverlay']=release+'/intake-overlay.json';baseline['projectionAsOfUTC']=datetime.datetime.now(datetime.timezone.utc).isoformat();baseline['preparedPackages']=packages;baseline['currentCounts']={'registeredPrimaryDrawingIDs':overlay['registeredDrawings'],'registeredNativeOriginals':overlay['registeredOriginals'],'newNativeCalls':overlay['newNativeCalls'],'newDrawings':overlay['newDrawings'],'semanticQuestions':len(slots),'usefulProvisionalIdleSemanticUses':sum(idle.values()),'usefulIdleUsesByAction':dict(idle),'reviewedOneShotHopStudies':sum(s['state']=='provisional-drawn-one-shot-hop-study-contact-unbound' for s in slots),'sourceAcceptedFullLocomotionSlots':0,'appBindingsVerifiedHere':0,'appBindingCurrentState':'UNKNOWN','states':dict(Counter(s['state'] for s in slots))}
# Report actual byte-pair problems in the existing projection, independent of proposed changes.
for old in current['species']:
 man=old['primaryManifest'];p=safe(man);j=read(man);a=safe(old['primaryAtlas']);actual=sha(a.read_bytes());expected=j['source']['sha256'];pkg=package(man)
 if actual!=expected:issues.append({'kind':'primary-atlas-byte-mismatch','speciesId':old['id'],'manifest':man,'oldAtlas':old['primaryAtlas'],'oldAtlasSHA256':actual,'manifestExpectedAtlasSHA256':expected,'correctedAtlas':pkg['atlasPNG'],'expectedDimensions':j['atlas'],'oldDimensions':list(rgba(a).size)})
 for row in old['slots']:
  if row['slot']=='neutral' and len(row.get('sourceFrameIds',[]))>1:issues.append({'kind':'neutral-projects-multiple-eye-or-look-states','speciesId':old['id'],'oldSourceIDs':row['sourceFrameIds'],'correctedSourceIDs':next(r for r in byid[old['id']]['slots'] if r['slot']=='neutral')['sourceFrameIds']})
 if man not in current['preparedPackages']:issues.append({'kind':'missing-current-prepared-package','speciesId':old['id'],'manifest':man})
ct=byid['california_towhee'];cthop=next(r for r in ct['slots'] if r['slot']=='locomotion');oldhop=next(r for b in current['species'] if b['id']=='california_towhee' for r in b['slots'] if r['slot']=='locomotion')
if set(oldhop['sourceFrameIds'])!=set(cthop['sourceFrameIds']):issues.append({'kind':'hop-omits-reused-neutral-source','speciesId':'california_towhee','oldSourceIDs':oldhop['sourceFrameIds'],'correctedSourceIDs':cthop['sourceFrameIds'],'newDrawingCountUnchanged':4,'playbackUniqueSourceCount':5})
report={'kind':'read-only-current-intake-projection-audit','createdUTC':baseline['projectionAsOfUTC'],'canonicalSourceRoot':str(root),'auditedInventory':release+'/CURRENT-SLOT-INVENTORY.json','inputInventorySHA256':sha(safe(release+'/CURRENT-SLOT-INVENTORY.json').read_bytes()),'inputOverlaySHA256':sha(safe(release+'/intake-overlay.json').read_bytes()),'currentRegisteredDrawings':len(bank['frames']),'actualAtlasMismatches':sum(i['kind']=='primary-atlas-byte-mismatch' for i in issues),'issues':issues,'primarySourceChecks':checks,'allPrimarySourceChecksPassed':all(c['pass'] for c in checks),'exactPackagesVerified':len(packages),'exactPrimaryAtlasFramesVerified':sum(len(p['frames']) for p in packages.values()),'alphaContactSamplesVerified':sum(len(f['alphaContactChecks']) for p in packages.values() for f in p['frames']),'currentCountsUnchanged':all(baseline['currentCounts'].get(k)==v for k,v in current['currentCounts'].items()),'proposedCounts':baseline['currentCounts'],'artOrManifestBytesChanged':False,'liveAppRuntimeImpact':'None from audit/projection; liveMacbinding UNKNOWN','overlayRules':['neutral is one first-open source only','blink sequence maps exact ordered output steps to reusable source IDs','look preserves its own manifest/clip, with no automaticcross-original neutral splice','Towheehop has5playbacksourceIDs:4new+1oldneutral; Bluebirdhop excludesoldneutral reference','closure-onlyincoming batches affect blink only, reuseoldawake and add no neutralcoverage; sourceHeld/newSourceHeld or explicit empty usefulSourceSlotsCompleted keep priorprimary/neutral and holdnewblink','atlas chosen byselectedmanifest source.sha256, never carriedforwardblindly','output IDs andregistered derivative IDs never become extra new drawingIDs'],'remainingGaps':'Provisional neutral/look/blink sources do notcomplete speciesanimation.2reviewed one-shot hops remain unbound studies; otherlocomotion/feed/drink/preen/flightgaps retained; Nuttallverticalsupport unresolved.'}
save('CURRENT-SLOT-INVENTORY.json' if args.apply else 'CURRENT-SLOT-INVENTORY.proposed.json',baseline);save('mapping-audit.json',report)
lines=['# Current intake projection audit','',f"Confirmed **{report['actualAtlasMismatches']} atlas byte mismatches**. Source art and manifests were not edited. The proposed projection keeps reusable source IDs separate from render exports and current Mac binding unknown.",'','| Species | Wrong atlas | Correct atlas |','|---|---|---|']
for i in issues:
 if i['kind']=='primary-atlas-byte-mismatch':lines.append(f"| {i['speciesId']} | `{i['oldAtlas']}` | `{i['correctedAtlas']}` |")
lines+=['','Three awake-pair neutral slots and one Nuttall neutral-study slot incorrectly contained multiple source states; proposed neutral uses the open source only. Blink retains its exact ordered open→closed→open source/tick sequence. Look bindings retain their actual manifest/clip rather than being silently spliced into a new neutral pair.','', 'Towhee hop uses **five unique playback sources: four new poses plus its reused old neutral**, six sequence steps,29ticks at30Hz. Bluebird hop uses four new sources and excludes its old neutral comparison from playback. These are reviewed one-shot studies, not admitted full locomotion.','',f"Verified {len(packages)} exact packages, {report['exactPrimaryAtlasFramesVerified']} atlas frames and {report['alphaContactSamplesVerified']} alpha-positive contact samples. Shape/alpha checks do not establish anatomical support or runtime acceptance.",'', 'The proposed Python updater rebuilds from frozen baseline plus current reviewed overlay. It handles incoming closure-only batches by changing blink coverage only. It writes into its own directory by default; the coordinator must explicitly set `--output-dir` for publication. The audit did not run it against any global output target.','', '`mapping-audit.json` contains exact mismatches and checks. `CURRENT-SLOT-INVENTORY.proposed.json` is the corrected projection. Actual source art hashes, density, world canvas, timing, contact shapes and output→source mappings are retained in its prepared packages.','']
(out/'MAPPING-AUDIT.md').write_text('\n'.join(lines));print(json.dumps({'atlasMismatches':report['actualAtlasMismatches'],'issueCounts':dict(Counter(i['kind'] for i in issues)),'packages':len(packages),'atlasFrames':report['exactPrimaryAtlasFramesVerified'],'contacts':report['alphaContactSamplesVerified'],'primarySourceChecksPassed':report['allPrimarySourceChecksPassed'],'counts':baseline['currentCounts']},indent=2))

# Readable current source/gap projection. Mandatory frame counts and live binding are never inferred.
lines=['# Current per-species source slots','',f"{overlay['registeredDrawings']} registered primary source IDs across {overlay['registeredOriginals']} retained originals. Useful provisional idle semantic uses: "+', '.join(f'{v} {k}' for k,v in idle.items())+'. These uses overlap drawings. Source studies do not complete species action sets.','','| Species | Neutral | Look | Blink | Locomotion | Feed / drink / preen | Flight |','|---|---|---|---|---|---|---|']
def short(row):
 if row.get('newSourceHeld'):return 'new source held'
 if row['state']=='missing':return 'missing'
 if row['state']=='provisional-drawn-one-shot-hop-study-contact-unbound':return 'reviewed one-shot study'
 if row['state']=='provisional-held-static-fallback':return 'provisional still'
 if row['provisionalUsefulSourceForThisSemanticSlot']:return 'provisional source'
 return row['state']
for bird in baseline['species']:
 r={x['slot']:x for x in bird['slots']};lines.append('| '+bird['name']+' | '+' | '.join(short(r[k]) for k in ['neutral','look','blink','locomotion'])+' | '+' / '.join(short(r[k]) for k in ['feeding','drinking','preen'])+' | '+short(r['takeoff_flight_landing'])+' |')
lines+=['','Nuttall remains an inclined-trunk endpoint hypothesis; vertical support is unresolved. Towhee hop uses four new drawings plus one reused neutral; Bluebird excludes its old-neutral comparison from playback. Canonical Mac binding and actual yard verification remain UNKNOWN here.','','Atlas paths are resolved against each selected manifest’s exact source.sha256. Primary/source IDs are reusable drawings; render IDs and registered derivatives add no drawings. Closure-only incoming batches affect blink coverage only. A batch marked newSourceHeld keeps the prior primary neutral intake and records the new blink as a held study.','']
(out/('CURRENT-SLOT-INVENTORY.md' if args.apply else 'CURRENT-SLOT-INVENTORY.proposed.md')).write_text('\n'.join(lines))
