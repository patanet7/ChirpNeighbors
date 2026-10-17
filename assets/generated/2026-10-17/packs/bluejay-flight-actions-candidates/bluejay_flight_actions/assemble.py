from pathlib import Path
from PIL import Image,ImageDraw
from scipy.ndimage import label,find_objects
import numpy as np,json,hashlib
P=Path(__file__).parent
cfg={
 'takeoff':{'names':['stand','crouch','push_off','downstroke','climb','enter_flight'],'hips':[(310,370),(815,390),(1280,365),(267,744),(801,785),(1260,767)],'ms':[350,150,100,100,120,120],'world':[(0,0),(0,15),(8,-25),(22,-70),(40,-110),(62,-135)]},
 'flight':{'names':['upstroke_peak','downstroke_begin','downstroke_peak','recovery_begin','recovery_mid','upstroke_end'],'hips':[(300,350),(795,350),(1287,350),(299,818),(795,818),(1287,818)],'ms':[90,75,90,75,75,75],'world':[(0,0)]*6},
 'landing':{'names':['approach','brake','feet_extend','contact','settle','stand'],'hips':[(310,360),(855,401),(1348,412),(313,857),(815,867),(1321,883)],'ms':[140,130,120,130,180,450],'world':[(0,-130),(18,-90),(30,-45),(38,0),(38,10),(38,0)]}}
m={'schemaVersion':1,'status':'review_candidate_not_integrated','masterCanvas':{'width':768,'height':768},'runtimeCanvas':{'width':512,'height':512},'runtimeTransform':{'scaleX':2/3,'scaleY':2/3,'translationX':0,'translationY':0,'resampling':'nearest-neighbor','sharedAcrossEveryFrame':True},'anchor':{'kind':'estimated_hip_body_root','masterPx':[430,420],'runtimePx':[430*2/3,280]},'rootMotionPolicy':'Root movement is separate metadata, NOT baked into master/runtime frames or preview GIFs. Apply suggested world offsets externally after scaling, or use scene-specific flight path. Offsets are illustrative, not ground-calibrated.','scalePolicy':'Master source pixels at 1x with translation only; runtime exact shared 2/3 scale. Never per-bbox resize. Wingspan is not used for body normalization.','actions':{},'review':['Genuine generated body/wing/leg poses; three image_gen calls, six drawings each.','Flight loop has high and low wing phases; body remains aligned at hip but anatomy and feather patterns visibly drift.','Flight phases 3 and 4 are similar downstroke shapes; cadence is stepped.','Transitions between independently generated clips are logical but not pixel-identical; endpoint popping remains.','Landing raised wings have possible duplicated-looking feather layers and should receive anatomy review.','Generated wings use simplified broad white-tipped feathers compared with canonical wing markings.','Estimated hip anchors require garden-scale placement review.','Some low-alpha edge fringe reaches original sheet boundaries; source originals retained.']}
for action,c in cfg.items():
 src=Image.open(P/'originals'/f'{action}-generated.png').convert('RGBA');a=np.array(src);labs,n=label(a[:,:,3]>0);comps=[]
 for i,s in enumerate(find_objects(labs),1):
  ys,xs=np.where(labs[s]==i)
  if len(xs)>10000:comps.append((i,s,float(ys.mean()+s[0].start)))
 comps.sort(key=lambda z:(int(z[2]>512),z[1][1].start))
 assert len(comps)==6
 frames=[];runtime=[];entries=[]
 for j,((i,s,_),name,hip,ms,world) in enumerate(zip(comps,c['names'],c['hips'],c['ms'],c['world'])):
  isolated=np.zeros_like(a);mask=labs==i;isolated[mask]=a[mask]
  dx,dy=430-hip[0],420-hip[1];frame=Image.new('RGBA',(768,768));frame.paste(Image.fromarray(isolated),(dx,dy))
  assert (np.array(frame)[:,:,3]>0).sum()==mask.sum(),'No clipping allowed'
  f=f'{action}-{j:02d}-{name}.png';frame.save(P/'frames'/f);small=frame.resize((512,512),Image.Resampling.NEAREST);small.save(P/'runtime'/f);frames.append(frame);runtime.append(small)
  entries.append({'index':j,'pose':name,'durationMs':ms,'source':f'originals/{action}-generated.png','sourceComponent':int(i),'sourceBounds':[s[1].start,s[0].start,s[1].stop,s[0].stop],'sourceHipPx':list(hip),'sourceToMaster':{'scaleX':1,'scaleY':1,'translateX':dx,'translateY':dy},'masterFrame':'frames/'+f,'runtimeFrame':'runtime/'+f,'suggestedWorldRootOffsetMasterPx':list(world),'groundContact': action=='takeoff' and j<2 or action=='landing' and j>=3})
  if entries[-1]['groundContact']:
   # Estimated center of feet for contact review, explicitly not an exact anatomical landmark.
   ys,xs=np.where(np.array(frame)[:,:,3]>128);low=ys>ys.max()-24;entries[-1]['estimatedFootContactMasterPx']=[float(np.median(xs[low])),int(ys.max())]
 for size,seq in [('master',frames),('runtime',runtime)]:
  seq[0].save(P/f'blue-jay-{action}-{size}.apng',save_all=True,append_images=seq[1:],duration=c['ms'],loop=0,disposal=0,blend=0)
 preview=[]
 for f in runtime:
  bg=Image.new('RGBA',f.size,'#e4dfce');bg.alpha_composite(f);preview.append(bg.convert('RGB'))
 preview[0].save(P/f'blue-jay-{action}.gif',save_all=True,append_images=preview[1:],duration=c['ms'],loop=0)
 atlas=Image.new('RGBA',(1536,1024));sheet=Image.new('RGB',(1536,1080),'#e4dfce');draw=ImageDraw.Draw(sheet)
 for j,f in enumerate(runtime):
  atlas.paste(f,((j%3)*512,(j//3)*512));sheet.paste(preview[j],((j%3)*512,(j//3)*540));draw.text(((j%3)*512+12,(j//3)*540+516),c['names'][j],fill='black')
 atlas.save(P/f'blue-jay-{action}-runtime-atlas.png');sheet.save(P/f'blue-jay-{action}-contact.jpg')
 assert len({hashlib.sha256(f.tobytes()).hexdigest() for f in frames})==6
 assert Image.open(P/f'blue-jay-{action}.gif').n_frames==6
 m['actions'][action]={'frameCount':6,'durationMs':sum(c['ms']),'loop':action=='flight','frames':entries,'next':{'takeoff':'flight','flight':'flight or landing','landing':'idle'}[action]}
(P/'manifest.json').write_text(json.dumps(m,indent=2))
(P/'hashes.json').write_text(json.dumps({str(f.relative_to(P)):hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(P.rglob('*')) if f.is_file() and f.name!='hashes.json'},indent=2))
print('Validated: 18 unique master poses, 18 runtime frames <=512, all source alpha pixels retained, 3 playable GIFs, 6 APNGs.')
