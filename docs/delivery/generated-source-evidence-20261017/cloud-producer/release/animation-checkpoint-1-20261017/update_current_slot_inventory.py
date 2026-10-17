"""Project reviewed source overlays onto the frozen baseline; never infer Mac binding."""
from pathlib import Path
from collections import Counter
import argparse,json
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,default=(Path(__file__).resolve().parent/'../..').resolve());root=p.parse_args().root
release=root/'release/animation-checkpoint-1-20261017';baseline=json.loads((root/'audits/animation-slot-inventory-20261017/inventory.json').read_text());overlay=json.loads((release/'intake-overlay.json').read_text());bank=json.loads((root/'frame-bank.json').read_text());byid={b['id']:b for b in baseline['species']}
for batch in overlay['batches']:
 for sid in batch['speciesIds']:
  bird=byid[sid];fs=[f for f in bank['frames'] if f['frameId'] in batch['sourceFrameIds'] and f['species']==sid]
  bird['nativeSourceRecords'].extend(fs);bird['nativeBankDrawings']+=len(fs);bird['sourceIssues'].append(batch['scope']);bird['nextAssignedTask']=None
  affected=['locomotion'] if batch['slot']=='ordinary_locomotion' else ['neutral','look'] if sid=='nuttall_s_woodpecker' else ['neutral','blink']
  for slot in bird['slots']:
   if slot['slot'] not in affected:continue
   slot['baselineState']=slot['state'];slot['sourceFrameIds']=[f['frameId'] for f in fs];slot['uniqueKnownSourceIDs']=len(fs);slot['evidencePaths']=[batch['primaryManifest'],batch['review']];slot['preparedPackagePaths']=[batch['sourcePath']];slot['remainingPhasesOrReview']=[batch['scope'],'Canonical Mac admission, actor binding and actual-yard verification unknown here.'];slot['newAssignment']=None;slot['productionAccepted']=False;slot['appBinding']='UNKNOWN';slot['actualYardVerification']='UNKNOWN'
   if sid=='nuttall_s_woodpecker':slot.update(state='inclined-support-endpoint-hypothesis-vertical-unresolved',provisionalUsefulSourceForThisSemanticSlot=False)
   elif slot['slot']=='locomotion':slot.update(state='provisional-drawn-one-shot-hop-study-contact-unbound',provisionalUsefulSourceForThisSemanticSlot=True)
   else:slot.update(state='provisional-drawn-'+slot['slot'],provisionalUsefulSourceForThisSemanticSlot=True)
  if sid in ['dark_eyed_junco','american_crow','spotted_towhee']:
   bird['primaryIntakeStatus']='provisional-source-review-candidate';bird['primaryManifest']=batch['sourcePath']+'/texture-review-manifest.json';bird['selectedIdleSourceIDs']=batch['sourceFrameIds']
slots=[s for bird in baseline['species'] for s in bird['slots']];idle=Counter(s['slot'] for s in slots if s['provisionalUsefulSourceForThisSemanticSlot'] and s['slot'] in ['neutral','look','blink'])
baseline['kind']='Current source-only slot overlay; baseline provenance and prior issues preserved';baseline['currentOverlay']=str((release/'intake-overlay.json').relative_to(root));baseline['currentCounts']={'registeredPrimaryDrawingIDs':overlay['registeredDrawings'],'registeredNativeOriginals':overlay['registeredOriginals'],'newNativeCalls':overlay['newNativeCalls'],'newDrawings':overlay['newDrawings'],'semanticQuestions':len(slots),'usefulProvisionalIdleSemanticUses':sum(idle.values()),'usefulIdleUsesByAction':dict(idle),'reviewedOneShotHopStudies':sum(s['state']=='provisional-drawn-one-shot-hop-study-contact-unbound' for s in slots),'sourceAcceptedFullLocomotionSlots':0,'appBindingsVerifiedHere':0,'states':dict(Counter(s['state'] for s in slots))}
(release/'CURRENT-SLOT-INVENTORY.json').write_text(json.dumps(baseline,indent=2)+'\n')
lines=['# Current per-species source slots','',f"{overlay['newDrawings']} new drawings /{overlay['newNativeCalls']} calls since PR33; {overlay['registeredDrawings']} registered primary IDs total. Useful provisional idle uses: "+', '.join(f'{v} {k}' for k,v in idle.items())+'. These uses overlap individual source drawings. No full locomotion or app binding is accepted by this source audit.','','| Species | Neutral | Look | Blink | Locomotion | Feed / drink / preen | Flight |','|---|---|---|---|---|---|---|']
def short(s):
 if s['state']=='missing':return 'missing'
 if s['state']=='provisional-drawn-one-shot-hop-study-contact-unbound':return 'reviewed one-shot hop study'
 if s['provisionalUsefulSourceForThisSemanticSlot']:return 'provisional drawn'
 return s['state']
for bird in baseline['species']:
 a={s['slot']:s for s in bird['slots']};lines.append('| '+bird['name']+' | '+' | '.join(short(a[k]) for k in ['neutral','look','blink','locomotion'])+' | '+' / '.join(short(a[k]) for k in ['feeding','drinking','preen'])+' | '+short(a['takeoff_flight_landing'])+' |')
lines+=['','Nuttall remains an inclined-trunk endpoint hypothesis; vertical contact is unresolved. Earlier failed studies and source issues remain in JSON. Root trajectories and repeated preview frames add no drawings. The Mac task owns current app admission and yard playback; their live status is unknown here.','']
(release/'CURRENT-SLOT-INVENTORY.md').write_text('\n'.join(lines));print(json.dumps(baseline['currentCounts']))
