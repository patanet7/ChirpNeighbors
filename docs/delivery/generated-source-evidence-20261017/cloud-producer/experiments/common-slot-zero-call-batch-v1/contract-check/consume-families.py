"""Consume stable producer handoffs read-only into intentionally incomplete V4 inputs."""
import pathlib,json,hashlib,copy,sys
from PIL import Image
O=pathlib.Path(__file__).resolve().parent;UI=pathlib.Path('/workspace/runtime-common-v6-intake-inspect')
sha=lambda b:hashlib.sha256(b).hexdigest()
def write(name,d):
 p=O/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2)+'\n');return {'file':name,'bytes':p.stat().st_size,'sha256':sha(p.read_bytes())}
receipts=[]
for sp in (sys.argv[1:] or ['mourning_dove','yellow_rumped_warbler']):
 family=O/'families'/sp
 # Caller runs only after producer freeze GO. A stable ledger must be present.
 candidates=list(family.glob('*STABLE*GO*.json'))+list(family.glob('STABLE-GO.json'))
 assert candidates,'Producer stable GO missing: '+sp
 handoff=family/'family-handoff.json';h=json.loads(handoff.read_text());assert h['speciesId']==sp;assert h['newNativeCalls']==h['newDrawings']==0
 width,height=h['candidateCanvas'];pivot=dict(zip(['x','y'],h['candidatePivot']));assert h['density']==1
 roles={};pixels=[];cfg=[];lineage=[]
 for i,f in enumerate(h['frames']):
  p=family/f['png'];b=p.read_bytes();assert sha(b)==f['PNGsha256'];im=Image.open(p).convert('RGBA');assert im.size==(width,height);rgba=im.tobytes();assert 'frame.sha256.'+sha(f'RGBA8;{width}x{height};'.encode()+rgba)==f['decodedRGBAId'];roles[f['role']]=i;pixels.append({'rgba':list(rgba)});cfg.append({'role':f['role'],'png':str(p),'PNGsha256':f['PNGsha256'],'decodedRGBAId':f['decodedRGBAId']});lineage.append(copy.deepcopy(f))
 assert set(roles)=={'neutral','blink','look'}
 base=json.loads((O/f'proposals/{sp}.INCOMPLETE.input-v4.json').read_text());base['pixels']['canvas']={'width':width,'height':height};base['pixels']['frames']=pixels
 clips={c['id']:c for c in h['clips']};assert set(clips)=={'idle','blink','look'}
 def pose(role,ticks,id):return {'frame':roles[role],'durationTicks':ticks,'pivot':pivot,'contacts':[],'poseId':id,'rotation':0}
 idle=clips['idle'];assert idle.get('roles',idle.get('frameIds'))==['neutral'];assert idle['loop'] is True;assert idle['tickRate']==30
 base['clips']['idle']['poses']=[pose('neutral',idle['durationTicks'][0],'idle-neutral')]
 base['conditioning']['poseGraph']['nodes'][0]['frame']=roles['neutral']
 nodes=[];edges=[];named={}
 for name in ['blink','look']:
  c=clips[name];rr=c.get('roles',c.get('frameIds'));assert rr==['neutral',name,'neutral'];assert len(c['durationTicks'])==3 and c['loop'] is False and c['tickRate']==30
  ids=[name+'-neutral',name+'-expression',name+'-neutral'];poses=[pose(role,ticks,id) for role,ticks,id in zip(rr,c['durationTicks'],ids)]
  named[name]={'name':name,'loop':False,'poses':poses};nodes.extend([{'id':ids[0],'frame':roles['neutral'],'clip':name,'referenceId':None},{'id':ids[1],'frame':roles[name],'clip':name,'referenceId':None}]);edges.extend([{'from':ids[0],'to':ids[1]},{'from':ids[1],'to':ids[2]}])
 base['commonMotion']={'schemaVersion':1,'geometryScope':'image-registration-only','physicalSupportReviewed':False,'idleSequence':['idle','blink','look'],'clips':named,'poseGraph':{'nodes':nodes,'edges':edges}}
 output=write(f'proposals/{sp}.family.INCOMPLETE.input-v4.json',base)
 recheck=write(f'rechecks/{sp}-family/canonical-input.json',{'expectedPackageSHA256':sha((UI/'src/lib/server/asset-pipeline/package.ts').read_bytes()),'expectedCanonicalSHA256':sha((UI/'src/lib/server/pipeline/canonical.ts').read_bytes()),'canvas':{'width':width,'height':height},'frames':cfg,'logicalPixelSize':1,'paletteLimit':64,'contacts':[],'geometryReviewed':False,'supportWorld':None})
 receipts.append({'speciesId':sp,'familyHandoff':str(handoff.relative_to(O)),'familyHandoffSHA256':sha(handoff.read_bytes()),'producerGOs':[{'file':str(p.relative_to(O)),'sha256':sha(p.read_bytes())} for p in sorted(set(candidates))],'template':output,'candidatePixelConfig':recheck,'frameOrder':[f['role'] for f in h['frames']],'frames':lineage,'clips':h['clips'],'candidateCanvas':h['candidateCanvas'],'pivot':h['candidatePivot'],'density':1,'commonCropOrigin':h['commonCropOrigin'],'alphaOrigin':'upstream-cleanup','sourceAdmitted':False,'metadataComplete':False,'missingPrivateAuthority':{'source.references':[],'conditioning.references':[],'requiredPinFields':['jobId','artifactId','version','contentDigest'],'matchingSourceFields':['id','speciesId','contentDigest','role'],'requiredRoles':'Exactly one reviewed style reference, and actual pose references for idle, blink and look; all identity/digest bindings must match actual owner-reviewed artifacts.'},'unknownRightsFields':['source.license.id','source.license.derivativesAllowed','source.license.redistributionAllowed','source.license.evidenceId','source.license.attribution'],'sourceFidelityReview':None,'geometryScope':'image-registration-only','physicalSupportReviewed':False,'contacts':[],'supportWorld':None,'newCalls':0,'newDrawings':0,'runtimeAdmission':False,'usefulness':'Assembled family remains subject to its actual independent source review; existing selected-pair agreement is not a full-family acceptance.'})
prior=O/'family-proposal-lineage.json'
if prior.exists():
 old=json.loads(prior.read_text())['families'];updated={r['speciesId']:r for r in old};updated.update({r['speciesId']:r for r in receipts});receipts=[updated[k] for k in sorted(updated)]
write('family-proposal-lineage.json',{'scope':'Read-only handoff consumption, decoded pixels and concrete producer-owned V4 fields; intentionally incomplete private authority fields','families':receipts,'staticSchemaCheckSeparate':True,'actualRuntimeCheckerBlocked':True,'sourceAdmitted':False})
print(json.dumps([{'species':r['speciesId'],'template':r['template'],'canvas':r['candidateCanvas']} for r in receipts]))
