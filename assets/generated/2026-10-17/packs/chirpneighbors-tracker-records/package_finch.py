"""Technical frame isolation; originals retained. No synthesized anatomy or per-frame fitting."""
from pathlib import Path
from PIL import Image,ImageDraw
from scipy import ndimage
import numpy as np,json,hashlib
R=Path(__file__).parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def fid(im):return 'frame.sha256.'+hashlib.sha256(f'RGBA8;{im.width}x{im.height};'.encode()+im.tobytes()).hexdigest()
bank=[];clips=[]
for sex in ['male','female']:
 for action in ['idle','feed']:
  name=f'house-finch-{sex}-{action}-v1';p=R/'batches'/name;im=Image.open(p/'original.png').convert('RGBA');a=np.array(im);alpha=a[:,:,3]
  # Main bird components preserve silhouette assignment when the model overruns nominal cells.
  labels,n=ndimage.label(alpha>=32,np.ones((3,3)));sizes=np.bincount(labels.ravel());main_ids=np.argsort(sizes[1:])[-6:]+1;objects=ndimage.find_objects(labels)
  ordered=sorted(main_ids,key=lambda i:(int((objects[i-1][0].start+objects[i-1][0].stop)/2)//512,objects[i-1][1].start))
  principal=np.zeros_like(labels)
  for k,i in enumerate(ordered):principal[labels==i]=k+1
  _,nearest=ndimage.distance_transform_edt(principal==0,return_indices=True);owners=principal[nearest[0],nearest[1]]
  # Alpha=1 residue is excluded from derivative frames only; original remains byte-identical.
  substantive=alpha>=2;assigned=np.zeros_like(substantive);frames=[];previews=[];entries=[]
  durations=[1700,180,90,350,180,120] if action=='idle' else [300,200,180,260,280,280]
  phases=['neutral','upward-attention','closed-blink','viewer-glance','profile-return','half-blink'] if action=='idle' else ['ready','bow-to-seed','pickup','seed-held','kernel-bite','swallow-recovery']
  for k,label_id in enumerate(ordered):
   core=labels==label_id;yy,xx=np.nonzero(core);ground=int(yy.max());low=core&(np.indices(core.shape)[0]>=ground-28);fy,fx=np.nonzero(low);rootx=int(np.median(fx));dx=512-rootx;dy=800-ground
   mask=(owners==k+1)&substantive;ys,xs=np.nonzero(mask);tx=xs+dx;ty=ys+dy
   assert tx.min()>=0 and ty.min()>=0 and tx.max()<1024 and ty.max()<1024
   out=np.zeros((1024,1024,4),dtype=np.uint8);out[ty,tx]=a[ys,xs];assert np.array_equal(out[ty,tx],a[ys,xs]);assigned|=mask
   frame=Image.fromarray(out,'RGBA');frame_id=fid(frame);dest=R/'frames'/frame_id.replace('frame.sha256.','');dest=dest.with_suffix('.png');dest.parent.mkdir(exist_ok=True)
   if not dest.exists():frame.save(dest)
   rev=frame.resize((384,384),Image.Resampling.NEAREST);preview_dir=p/'frames-review384';preview_dir.mkdir(exist_ok=True);rev.save(preview_dir/f'{k:02d}.png')
   bg=Image.new('RGBA',(384,384),(239,235,213,255));bg.alpha_composite(rev);previews.append(bg.convert('RGB'));frames.append(frame)
   split=float(np.median(fx));contacts=[]
   for condition in [fx<=split,fx>split]:
    if condition.any():contacts.append([int(np.median(fx[condition]))+dx,int(fy[condition].max())+dy])
   box=objects[label_id-1];edge_contacts=int(np.count_nonzero(core[:,0])+np.count_nonzero(core[:,-1])+np.count_nonzero(core[0,:])+np.count_nonzero(core[-1,:]))
   record={'frameId':frame_id,'file':str(dest.relative_to(R)),'fileSha256':sha(dest),'pixelIdentity':'SHA256 of RGBA8;WxH; plus decoded bytes','dimensions':[1024,1024],'species':'house_finch','variant':'adult-'+sex,'appearanceVersion':'house-finch-canon-v1','poseTags':[phases[k],action,'right-facing'],'sourceAtlas':str((p/'original.png').relative_to(R)),'sourceAtlasSha256':sha(p/'original.png'),'sourceComponentId':int(label_id),'sourceCoreBBox':[box[1].start,box[0].start,box[1].stop,box[0].stop],'derivation':{'method':'6 principal alpha>=32 components; nearest-component assignment of all alpha>=2 pixels; integer translation only','alphaOneResidueDiscardedInDerivative':True,'originalRetainedUnchanged':True,'translation':[dx,dy],'sourceScale':1,'perFrameRescale':False},'supportRoot':[512,800],'feetContactsApprox':contacts,'contactAnnotationMethod':'manual-review-needed pixel heuristic: lower28px median foot groups; not anatomical tracking','beakAnchorApprox':None,'scaleCalibrationRef':'scale.house_finch','anatomyScaleAccepted':False,'rootContactAccepted':False,'originalCoreEdgeContacts':edge_contacts,'technicalSourcePixelCopyExact':True,'acceptedUses':[],'rejectedUses':[],'candidateUses':['idle','perching'] if action=='idle' else ['feeding','idle-entry-or-exit-pose'],'reuseStatus':'suggestion only; appearance/anchor/transition validation required','sourcePrompt':str((p/'prompt.txt').relative_to(R)),'generator':'OpenAI image_gen.imagegen','model':None,'seed':None}
   bank.append(record);entries.append({'frameId':frame_id,'durationMs':durations[k],'phase':phases[k],'feetContactState':'both-planted-candidate','seedContactState':'beak-seed-candidate' if action=='feed' and k in [2,3,4] else None,'contactVerified':False})
  assert np.array_equal(assigned,substantive)
  frames[0].save(p/'preview.apng',save_all=True,append_images=frames[1:],duration=durations,loop=0,disposal=0,blend=0);previews[0].save(p/'preview.gif',save_all=True,append_images=previews[1:],duration=durations,loop=0,disposal=2)
  atlas=Image.new('RGBA',(3072,2048));sheet=Image.new('RGB',(1152,820),(239,235,213));d=ImageDraw.Draw(sheet)
  for i,f in enumerate(frames):atlas.paste(f,(i%3*1024,i//3*1024));sheet.paste(previews[i],(i%3*384,i//3*410));d.text((i%3*384+10,i//3*410+389),f'{i+1} {phases[i]} | {durations[i]}ms',fill=(30,40,35))
  atlas.save(p/'atlas.png');sheet.save(p/'contact-sheet.png')
  issues=['Species canon is sourced-text-grounded with own style reference; licensed photo bytes were inaccessible, not used as image conditioning.','Eye rendering and smooth fine feather texture may be too photographic for target pixel-art style.','Source body size, feather identity and foot layout drift between poses; no per-frame normalization conceals it.','Root/feet points are pixel heuristics pending anatomical/contact review; beak landmark and seed contact need explicit annotation.','Published species length13–14cm/wingspan20–25cm are evidence only; measurement endpoints undefined and cross-species sprite calibration remains unaccepted.','Original atlas overruns nominal cells; component isolation preserves all alpha>=2 source pixels exactly; alpha=1 residue omitted only in derivatives.']
  if action=='feed':issues+=['Seed/kernel is oversized and pickup/crushing contact timing is illustrative; no resolved shell-splitting acceptance.','Feeding posture is a head/neck bow; ordinary ground walking/hopping amplitude is a separate requested behavior.']
  else:issues+=['Six idle key poses are stepped; viewer turn and return have residual contour drift; loop seam unaccepted.']
  clip={'schemaVersion':1,'kind':'production-clip-proposal-not-app-wire-format','clipId':name,'species':'house_finch','variant':'adult-'+sex,'canonicalSpeciesId':None,'appearanceVersion':'house-finch-canon-v1','action':'idle' if action=='idle' else 'seed-feeding','direction':'right-facing','loop':True,'frames':entries,'frameBank':'../../frame-bank.json','sourceCanvas':[1024,1024],'supportRoot':[512,800],'reviewDerivative':{'canvas':[384,384],'uniformScale':0.375,'resampling':'nearest neighbor','purpose':'review/Mac intake candidate; old runtime profile not claimed'},'worldSize':None,'scaleCalibrationRef':'scale.house_finch','reducedMotion':{'frameId':entries[0]['frameId'],'verified':False},'transitionsVerified':False,'review':{'state':'reviewed-with-issues','accepted':False,'issues':issues},'validation':{'uniqueFrames':len(set(e['frameId'] for e in entries)),'APNGframes':Image.open(p/'preview.apng').n_frames,'GIFframes':Image.open(p/'preview.gif').n_frames,'alphaGE2WholeAtlasAssignedExactlyOnce':True,'allCopiedPixelsExact':True,'sourceCoreEdgeContacts':sum(b['originalCoreEdgeContacts'] for b in bank if b['sourceAtlas']==str((p/'original.png').relative_to(R)))},'sourceOriginal':{'file':'original.png','sha256':sha(p/'original.png')},'promptFile':'prompt.txt','staged':False,'integrated':False}
  (p/'manifest.json').write_text(json.dumps(clip,indent=2)+'\n');(p/'review.md').write_text('# '+name+' — reviewed candidate\n\n'+'\n'.join('- '+x for x in issues)+'\n');clips.append(clip)
  print(name,json.dumps(clip['validation']))
# Canon references stay reference-only, at their native crop scale; never substituted as runtime frames.
for sex in ['male','female']:
 p=R/'batches/house-finch-canon-v1'/f'{sex}-source.png';im=Image.open(p).convert('RGBA');bank.append({'frameId':fid(im),'file':str(p.relative_to(R)),'fileSha256':sha(p),'dimensions':list(im.size),'species':'house_finch','variant':'adult-'+sex,'appearanceVersion':'house-finch-canon-v1','poseTags':['neutral','canonical-reference-only'],'acceptedUses':[],'candidateUses':['style/species-identity reference'],'reuseStatus':'not approved as runtime pose; scale differs from animation source canvases','scaleCalibrationRef':'scale.house_finch','rootContactAccepted':False,'sourceAtlas':'batches/house-finch-canon-v1/original.png'})
(R/'frame-bank.json').write_text(json.dumps({'schemaVersion':1,'authority':'local immutable production-frame evidence; pending Mac canonical frame contract','frames':bank,'clips':clips,'frameImageCopiesPerClip':False,'reuseProposals':[{'frameId':b['frameId'],'proposedUse':'perching' if 'idle' in b['poseTags'] else 'feeding transition','state':'candidate suggestion','requires':['same species/variant/appearance version','shared scale and anchors','pose/contact/transition review'],'verified':False} for b in bank if 'neutral' in b['poseTags'] and 'idle' in b['poseTags']]},indent=2)+'\n')
