"""Source-only Anna flight-study validation. Never an idle/runtime admission adapter."""
from pathlib import Path
import copy, hashlib, json, math
from PIL import Image

def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def rgba_id(im):
    im=im.convert('RGBA')
    return 'frame.sha256.'+hashlib.sha256(f'RGBA8;{im.width}x{im.height};'.encode()+im.tobytes()).hexdigest()
def require(ok, message):
    if not ok: raise ValueError(message)

def validate_flight_motion_batch(root, batch):
    """Validate exact retained sources; return additive proposal, not accepted coverage.

    All overlay paths are root-relative. Manifest-local paths resolve ONLY beside
    their owning manifest. Optional <field>SHA256 guards bind retained bytes.
    Mixed support actions require per-frame and per-segment supportState. Unknown
    shapes fail closed; producers/coordinator must supply explicit mappings.
    """
    root=Path(root).resolve(); files={}; checks=[]
    def path(value, parent=None):
        p=(root/value if parent is None else parent/value).resolve()
        require(p.is_relative_to(root) and p.is_file(),f'missing/outside-root path: {value}')
        files[str(p.relative_to(root))]=sha(p);return p
    def load(field, required=True):
        value=batch.get(field)
        if not value:
            require(not required,f'missing overlay field {field}');return None,None
        p=path(value); guard=batch.get(field+'SHA256')
        require(not guard or guard==sha(p),f'{field} hash mismatch')
        return p,json.loads(p.read_text())
    require(batch.get('flightMotionProposal') is True,'flightMotionProposal must be true')
    require(batch.get('runtimeAdmission') is False,'runtimeAdmission must explicitly be false')
    require(batch.get('speciesIds')==['anna_s_hummingbird'],'adapter is Anna-only')
    slots=batch.get('sourceActionSlots',['locomotion'])
    require(slots and all(s in ['locomotion','feeding','takeoff_flight_landing'] for s in slots),'unsupported flight-study slot; neutral/blink must remain unchanged')
    pp,primary=load('primaryManifest');mp,mapping=load('frameToActionMap')
    field='airborneSourceManifest' if batch.get('airborneSourceManifest') else 'actionSourceManifest'
    sp,source=load(field)
    tp,trajectory=load('motionTrajectory',required=False)
    motion_path,motion=load('motionProposalManifest',required=False)
    review_path,review=load('review',required=False)
    if review_path:require(bool(batch.get('reviewSHA256')),'review receipt needs exact reviewSHA256 guard')
    require(trajectory is not None or motion is not None,'separate trajectory/motion proposal required')
    require(source.get('scope')=='source-only' and source.get('activation')=='none','source-only/no-activation contract required')
    require(source.get('profile')!='chirp-texture-review-v1','airborne contract cannot claim idle profile')
    require(source.get('kind') in ['airborne-source-review','action-source-review'],'unknown source-only manifest kind')
    require(source.get('approval') in ['unreviewed','provisional','held','source-study'],'no runtime/source acceptance inferred')
    require(mapping.get('appBound',False) is False and mapping.get('SharpCanonicalAdmission',False) is False and mapping.get('runtimeBound',False) is False and mapping.get('idleProfileClaimed',False) is False,'mapping claims runtime admission')
    # Original and prompt retained; exact hashes are mandatory, not generation claims.
    for name,hashname in [('original','originalSHA256'),('prompt','promptSHA256')]:
        require(primary.get(name) and primary.get(hashname),f'missing retained {name}/hash')
        require(sha(path(primary[name],pp.parent))==primary[hashname],f'{name} hash mismatch')
    entries={}; new_ids=[]; reuse_ids=[]
    for field_name,target in [('frames',new_ids),('reusedFrames',reuse_ids)]:
        for f in primary.get(field_name,[]):
            require(f.get('speciesId')=='anna_s_hummingbird','source species mismatch')
            sid=f['sourceFrameId']; p=path(f['sourcePNG'],pp.parent);im=Image.open(p).convert('RGBA')
            require(sha(p)==f['sourcePNGsha256'] and rgba_id(im)==sid,'primary PNG hash/decoded source ID mismatch')
            if f.get('sourceCanvas'):require(f['sourceCanvas']==list(im.size),'primary declared source canvas differs from actual PNG')
            require(sid not in entries,'duplicate source ID across new/reused records')
            entries[sid]=(f,im);target.append(sid)
    require(new_ids,'retained batch has no actual new drawings')
    binding=mapping['manifest']
    require(path(binding['file'],mp.parent)==sp and binding['sha256']==sha(sp),'action map/source manifest binding mismatch')
    atlas=source['atlas'];ap=path(atlas['file'],sp.parent);ai=Image.open(ap).convert('RGBA')
    require(sha(ap)==atlas['sha256'] and ai.size==(atlas['width'],atlas['height']),'atlas bytes/dimensions mismatch')
    mapatlas=mapping.get('atlasBinding',mapping.get('atlas'))
    require(mapatlas and path(mapatlas['file'],mp.parent)==ap and mapatlas['sha256']==sha(ap),'action map atlas binding mismatch')
    mapped=mapping.get('sourceToRenderFrames')
    require(isinstance(mapped,list) and mapped,'explicit sourceToRenderFrames required')
    render={}; frame_checks=[]; shared_calibrations=set()
    for m in mapped:
        require(m['renderFrameId'] not in render,'duplicate render ID')
        render[m['renderFrameId']]=m
    frames={}
    for f in source['frames']:
        fid=f['id'];sid=f['primarySourceFrameId'];require(fid not in frames and sid in entries,'unknown/duplicate source frame')
        m=render.get(fid);require(m and m.get('primarySourceFrameId',m.get('sourceFrameId'))==sid,'source/render ID lineage mismatch')
        p,si=entries[sid]; rect=f['sourceRect'];require(rect==m['atlasRect'],'atlas rectangles disagree')
        x,y,w,h=[rect[k] for k in ['x','y','width','height']]
        require(all(isinstance(v,int) for v in [x,y,w,h]) and x>=0 and y>=0 and w>0 and h>0 and x+w<=ai.width and y+h<=ai.height,'atlas rectangle out of bounds')
        require((w,h)==(f['canvas']['width'],f['canvas']['height']),'rect/canvas mismatch')
        d=f['sourcePixelsPerWorldUnit'];require(math.isfinite(d) and d>0,'invalid density')
        require(all(abs(f['world'][axis]*d-f['canvas'][axis])<1e-6 for axis in ['width','height']),'whole-canvas world*density mismatch')
        require(d==1.5 and (w,h)==(96,96),'Anna family density/canvas mismatch')
        op=path(m['outputPNG'],mp.parent);oi=Image.open(op).convert('RGBA');tile=ai.crop((x,y,x+w,y+h))
        require(sha(op)==m['outputPNGsha256'] and oi.size==(w,h) and tile.tobytes()==oi.tobytes(),'atlas crop/output PNG mismatch')
        if m.get('primarySourcePNG',m.get('sourcePNG')):require(path(m.get('primarySourcePNG',m.get('sourcePNG')),mp.parent)==path(p['sourcePNG'],pp.parent),'map source file mismatch')
        if m.get('primarySourcePNGsha256',m.get('sourcePNGsha256')):require(m.get('primarySourcePNGsha256',m.get('sourcePNGsha256'))==p['sourcePNGsha256'],'map source hash mismatch')
        require(m.get('newDrawing',sid in new_ids)==(sid in new_ids),'new/reused mapping disagrees')
        # Recompute common registration if A calibration is declared; no shape inference.
        reg=p.get('registration',{});calfile=reg.get('sharedCalibrationFile',reg.get('wholeCallScaleFile'));transform='exact full-canvas nearest resize'
        if calfile:
            cp=path(calfile,pp.parent);c=json.loads(cp.read_text());shared_calibrations.add(str(cp.relative_to(root)))
            if reg.get('sharedCalibrationSHA256'):require(reg['sharedCalibrationSHA256']==sha(cp),'shared calibration hash mismatch')
            require(c.get('perPoseScale',reg.get('perPoseScale')) is False and c.get('perPoseTranslation',False) is False and c.get('wingEnvelopeFit',False) is False,'per-pose fit is not family registration')
            if 'sharedNativeTo1024Scale' in c:
                s=c['sharedNativeTo1024Scale'];tx,ty=c['sharedOriginTranslation'];tw,th=c['targetCanvas']
                predicted=Image.new('RGBA',(w,h));dst=predicted.load();src=si.load()
                for yy in range(h):
                    iy=math.floor((((yy+.5)*th/h)-ty)/s)
                    if iy<0 or iy>=si.height:continue
                    for xx in range(w):
                        ix=math.floor((((xx+.5)*tw/w)-tx)/s)
                        if 0<=ix<si.width:dst[xx,yy]=src[ix,iy]
                transform='recomputed shared analytic nearest calibration'
            elif 'sharedNativeCellTo1024Scale' in c:
                scale=c['sharedNativeCellTo1024Scale'];tx,ty=c['sharedOriginInteger'];tw,th=c['targetCanvas']
                registered=si.transform((tw,th),Image.Transform.AFFINE,(1/scale,0,-tx/scale,0,1/scale,-ty/scale),Image.Resampling.NEAREST)
                predicted=registered.resize((w,h),Image.Resampling.NEAREST)
                if p.get('registeredPNG'):
                    rp=path(p['registeredPNG'],pp.parent);require(Image.open(rp).convert('RGBA').tobytes()==registered.tobytes(),'C registered intermediate does not match shared affine')
                    if p.get('registeredPNGsha256'):require(sha(rp)==p['registeredPNGsha256'],'registered PNG hash mismatch')
                transform='recomputed shared cell-to1024 affine then nearest output resize'
            elif 'sharedNativeToFamilyScale' in c:
                scale=c['sharedNativeToFamilyScale'];sx,sy=c['primaryRoot'];rx,ry=c['registeredRoot'];rw,rh=c['registeredCanvas']
                offset=(sx-rx/scale,sy-ry/scale)
                registered=si.transform((rw,rh),Image.Transform.AFFINE,(1/scale,0,offset[0],0,1/scale,offset[1]),Image.Resampling.NEAREST)
                predicted=registered.resize((w,h),Image.Resampling.NEAREST)
                if p.get('registeredPNG'):
                    registered_path=path(p['registeredPNG'],pp.parent)
                    require(Image.open(registered_path).convert('RGBA').tobytes()==registered.tobytes(),'registered intermediate does not match declared affine transform')
                transform='recomputed shared affine registration then nearest output resize'
            else:raise ValueError('unsupported explicit calibration schema; coordinator adaptation required')
        else:predicted=si.resize((w,h),Image.Resampling.NEAREST)
        require(predicted.tobytes()==oi.tobytes(),'source-to-output transformation not proven by declared supported transform')
        state=f.get('supportState','airborne' if source['kind']=='airborne-source-review' else None)
        require(state in ['airborne','supported','first-contact','grounded','perched'],'explicit supported/airborne state required')
        contacts=f.get('contacts');require(isinstance(contacts,list),'contacts array required')
        if state=='airborne':require(contacts==[],'airborne contacts must be []')
        else:require(contacts,'supported/arrival frame needs technical contact marker')
        samples=[]
        for contact in contacts:
            require(set(contact)=={'id','x','y'},'contact shape must be {id,x,y}')
            cx,cy=contact['x'],contact['y'];require(isinstance(cx,int) and isinstance(cy,int) and 0<=cx<w and 0<=cy<h,'contact outside canvas')
            alpha=tile.getpixel((cx,cy))[3];require(alpha>0,'contact samples transparent pixel');samples.append({**contact,'sampledAlpha':alpha,'anatomicallyApproved':False})
        pivot=f['pivot'];require(0<=pivot['x']<=w and 0<=pivot['y']<=h,'pivot outside canvas')
        frames[fid]=f;frame_checks.append({'renderFrameId':fid,'sourceFrameId':sid,'newDrawing':sid in new_ids,'sourcePNGsha256':p['sourcePNGsha256'],'outputPNGsha256':sha(op),'outputRGBAId':rgba_id(oi),'atlasRect':rect,'canvas':f['canvas'],'world':f['world'],'density':d,'pivot':pivot,'supportState':state,'contacts':samples,'transformProof':transform,'occupiedAlphaBBox':list(tile.getchannel('A').getbbox()) if tile.getchannel('A').getbbox() else None,'renderWindowDiagnostic':p.get('renderWindowDiagnostic')})
    require(set(render)==set(frames),'map/manifest render frame sets differ')
    require(mapping.get('clips')==source['clips'],'map and manifest clip schedules differ')
    clips=[]
    for c in source['clips']:
        require(c['tickRate']==30 and isinstance(c.get('loop'),bool),'clip tick rate/loop missing or unsupported')
        seq=[]
        for step in c['frames']:
            fid=step['frameId'];require(fid in frames and isinstance(step['durationTicks'],int) and step['durationTicks']>0,'invalid clip frame/duration')
            f=frames[fid];seq.append({**step,'sourceFrameId':f['primarySourceFrameId'],'pose':entries[f['primarySourceFrameId']][0]['pose']})
        require(seq,'empty source clip')
        if c.get('durationTicks') is not None:require(c['durationTicks']==sum(s['durationTicks'] for s in seq),'declared clip duration mismatch')
        clips.append({**c,'orderedSourceFrameSequence':seq,'durationTicks':sum(s['durationTicks'] for s in seq),'uniqueSourceDrawingCount':len(set(s['sourceFrameId'] for s in seq))})
    require(len({c['id'] for c in clips})==len(clips),'duplicate clip ID')
    # Body trajectory has a separate clock. A longer episode never creates more source drawings.
    trajectories=[]
    trajectory_docs=[('motionTrajectory',tp,trajectory),('motionProposalManifest',motion_path,motion)]
    if mapping.get('motionProposalManifest'):
        bound=mapping['motionProposalManifest'];require(motion_path and path(bound['file'],mp.parent)==motion_path and bound['sha256']==sha(motion_path),'map/main motion proposal binding mismatch')
    for ref in mapping.get('motionProposalFiles',[]):
        dp=path(ref['file'],mp.parent);require(sha(dp)==ref['sha256'],'additional study hash mismatch')
        trajectory_docs.append(('independentStudy:'+ref['file'],dp,json.loads(dp.read_text())))
    for trajectory_name,document_path,t in trajectory_docs:
        if t is None:continue
        if 'segments' not in t:
            raise ValueError(f'{trajectory_name} unsupported trajectory shape; explicit segments required')
        require(t.get('tickRate')==30,'body trajectory tick rate mismatch')
        require(t.get('runtimeBound',False) is False and t.get('newDrawingsFromTrajectory',0)==0,'trajectory cannot claim runtime admission/new drawings')
        if t.get('poseClock'):require(t['poseClock'].get('tickRate')==30,'pose clock tick rate mismatch')
        if t.get('sourceManifest'):require(path(t['sourceManifest'],document_path.parent)==sp,'motion document source manifest mismatch')
        duration=t.get('durationTicks',t.get('totalTicks',t.get('endTick')));require(isinstance(duration,int) and duration>0,'body duration required')
        prev_tick=0;prev_root=None
        for segment in t['segments']:
            start,end=segment['ticks'];a,b=segment['rootFrom'],segment['rootTo']
            require(isinstance(start,int) and isinstance(end,int) and start==prev_tick and end>start,'body segments must be contiguous half-open ticks')
            require(len(a)==len(b)==2 and all(math.isfinite(v) for v in a+b),'invalid root coordinates')
            require(prev_root is None or a==prev_root,'body root discontinuity')
            state=segment.get('supportState','airborne' if source['kind']=='airborne-source-review' else None)
            require(state in ['airborne','supported','first-contact','grounded','perched'],'trajectory support state required')
            if segment.get('poseClipId'):require(segment['poseClipId'] in [c['id'] for c in clips],'trajectory references unknown pose clip')
            if state in ['supported','grounded','perched'] or segment.get('motion',segment.get('interpolation'))=='hold':require(a==b,'supported/hold root must be stationary')
            prev_tick=end;prev_root=b
        require(prev_tick==duration,'body duration/segment endpoint mismatch')
        if mapping.get('trajectory') and trajectory_name=='motionTrajectory':
            tb=mapping['trajectory'];require(path(tb['file'],mp.parent)==tp and tb['sha256']==sha(tp),'map/body trajectory path/hash mismatch')
        if t.get('samples'):
            samples=t['samples'];expected_ticks=list(range(duration)) if t.get('sampleTickConvention')=='frame-starts' else list(range(duration+1))
            require([s['tick'] for s in samples]==expected_ticks,'trajectory samples must match declared frame-start or inclusive-endpoint convention')
            for sample in samples:
                tick=sample['tick'];seg=next((s for s in t['segments'] if s['ticks'][0]<=tick<s['ticks'][1]),t['segments'][-1])
                require(sample.get('supportState')==seg.get('supportState','airborne' if source['kind']=='airborne-source-review' else None),'sample/segment support state mismatch')
                if sample.get('poseClipId'):require(sample['poseClipId']==seg.get('poseClipId'),'sample/segment pose clip mismatch')
                require(abs(sample.get('timeSeconds',tick/30)-tick/30)<1e-8,'sample time/tick mismatch')
                rule=seg.get('interpolation',t.get('rootInterpolation','linear'))
                require(rule in ['hold','linear','uSquared','2uMinusUSquared','smoothstep-segment-frame-endpoints'],'unknown trajectory interpolation')
                denominator=seg['ticks'][1]-seg['ticks'][0]-(1 if rule=='smoothstep-segment-frame-endpoints' else 0)
                u=(tick-seg['ticks'][0])/denominator if denominator else 0
                u={'hold':0,'linear':u,'uSquared':u*u,'2uMinusUSquared':2*u-u*u,'smoothstep-segment-frame-endpoints':u*u*(3-2*u)}[rule]
                expected=[a+(b-a)*u for a,b in zip(seg['rootFrom'],seg['rootTo'])]
                actual_root=sample.get('root',sample.get('rootWorldXY'))
                require(actual_root is not None and len(actual_root)==2 and all(abs(a-b)<1e-7 for a,b in zip(actual_root,expected)),'sample roots disagree with exact authored segment interpolation')
                if sample.get('renderFrameId'):
                    fid=sample['renderFrameId'];require(fid in frames,'sample references unknown render frame')
                    rf=frames[fid];require(not sample.get('primarySourceFrameId') or sample['primarySourceFrameId']==rf['primarySourceFrameId'],'sample source/render lineage mismatch')
                    cf=next(c for c in clips if c['id']==sample['poseClipId']);require(fid in [x['frameId'] for x in cf['frames']],'sample frame not in selected pose clip')
                    state=rf.get('supportState','airborne' if source['kind']=='airborne-source-review' else None)
                    require(sample['supportState']==state,'sample/selected source support state mismatch')
                    if sample.get('wingClockTick') is not None:
                        require(sample['wingClockTick']==tick,'wing clock is not declared global tick')
                        phase=tick%cf['durationTicks'] if cf['loop'] else min(tick,cf['durationTicks']-1)
                        cursor=0;expected_frame=None
                        for step in cf['frames']:
                            cursor+=step['durationTicks']
                            if phase<cursor:expected_frame=step['frameId'];break
                        require(fid==expected_frame,'actual wing/pose sample does not follow declared source clip clock')
                    technical=rf['contacts'];sample_contacts=sample.get('contacts',[])
                    if state=='airborne':require(sample_contacts==[] and sample.get('grounded',False) is False,'airborne sample claims grounded support')
                    else:
                        require(bool(sample_contacts) and sample.get('grounded') is True,'supported sample requires explicit grounded contact projections')
                        require(len(sample_contacts)==len(technical),'support sample/contact count mismatch')
                        for marker in technical:
                            sc=next((c for c in sample_contacts if c['id']==marker['id']),None);require(sc is not None and sc['sourcePositiveAlphaPixel']==[marker['x'],marker['y']],'support sample marker not bound to exact source pixel')
                            projected=[actual_root[0]+(marker['x']-rf['pivot']['x'])/rf['sourcePixelsPerWorldUnit'],actual_root[1]+(marker['y']-rf['pivot']['y'])/rf['sourcePixelsPerWorldUnit']]
                            require(all(abs(a-b)<1e-7 for a,b in zip(sc['worldXY'],projected)),'support contact projection mismatch')
                            if t.get('flatPerchPlaneWorldY') is not None:require(abs(sc['worldXY'][1]-t['flatPerchPlaneWorldY'])<1e-6,'declared technical toe is not on support plane')
        if t.get('wingCycleTicks') is not None:require(t['wingCycleTicks'] in [c['durationTicks'] for c in clips],'declared wing cycle does not match exact clip')
        require(t.get('rootPathGeneratesNewDrawings',False) is False,'trajectory cannot add source drawings')
        if source['kind']=='airborne-source-review':require(t.get('supports',[])==[],'airborne trajectory cannot claim support')
        trajectories.append({'field':trajectory_name,'document':str(document_path.relative_to(root)),'documentSHA256':sha(document_path),'tickRate':30,'durationTicks':duration,'segments':t['segments'],'separateFromPoseClock':True,'sourceDrawingsAdded':0})
    held=any(batch.get(k) is True or primary.get(k) is True for k in ['sourceHeld','newSourceHeld'])
    return {'batchId':primary['batchId'],'kind':'validated-source-only-flight-motion-proposal','technicalValidationPassed':True,'sourceReviewState':'held' if held else 'reviewed-source-study-with-qualifications' if review_path else 'pending-independent-source-review','reviewReceipt':({'path':str(review_path.relative_to(root)),'sha256':sha(review_path),**{k:review[k] for k in ['decision','verdict','recommendation','sourceAccepted','disposition','heldClaims','selectedSourceUsefulSlots','artAccepted'] if k in review}} if review_path else None),'runtimeAdmission':False,'productionAccepted':False,'fullLocomotionAccepted':False,'packetBindingReady':False,'appBinding':'UNKNOWN','actualYardVerification':'UNKNOWN','sourceActionSlots':slots,'newSourceFrameIds':new_ids,'reusedSourceFrameIds':reuse_ids,'newDrawingCount':len(new_ids),'reusedDrawingCount':len(reuse_ids),'renderDerivativeCount':len(frames),'renderDerivativesAreNewDrawings':False,'primaryManifest':str(pp.relative_to(root)),'sourceManifest':str(sp.relative_to(root)),'frameToActionMap':str(mp.relative_to(root)),'retainedFileSHA256':files,'frameChecks':frame_checks,'clips':clips,'trajectories':trajectories,'sharedCalibrations':sorted(shared_calibrations),'sourceHeld':held,'qualifications':['Technical identity, alpha and schedule checks do not establish art quality or physical support.','Perched primary, neutral and blink selections remain unchanged.','Wing/pose and body clocks are independent; root translation adds zero drawings.']}

def attach_flight_motion_proposal(bird, batch, report):
    """Add only study evidence; leave accepted/provisional semantic source coverage intact."""
    before=copy.deepcopy({k:bird.get(k) for k in ['primaryManifest','primaryAtlas','primaryIntakeStatus']})
    idle=copy.deepcopy([r for r in bird['slots'] if r['slot'] in ['neutral','look','blink']])
    proposals=bird.setdefault('sourceMotionProposals',[])
    require(not any(p['batchId']==report['batchId'] for p in proposals),'duplicate flight batch attachment')
    proposals.append(report)
    rows={r['slot']:r for r in bird['slots']}
    for slot in report['sourceActionSlots']:
        require(slot in rows,f'unknown semantic inventory slot {slot}')
        row=rows[slot];row.setdefault('motionStudyProposals',[]).append({'batchId':report['batchId'],'sourceManifest':report['sourceManifest'],'newSourceFrameIds':report['newSourceFrameIds'],'reusedSourceFrameIds':report['reusedSourceFrameIds'],'clipIds':[c['id'] for c in report['clips']],'sourceReviewState':report['sourceReviewState'],'held':report['sourceHeld'],'runtimeAdmission':False,'fullLocomotionAccepted':False,'packetBindingReady':False})
        # Preserve row.state and provisionalUsefulSourceForThisSemanticSlot exactly;
        # an additive source study cannot erase existing evidence or complete a gap.
    require(before=={k:bird.get(k) for k in before},'flight proposal mutated perched selection')
    require(idle==[r for r in bird['slots'] if r['slot'] in ['neutral','look','blink']],'flight proposal mutated idle source slots')

def current_bounded_queue(species, root, overlays):
    """Only unfinished source checkpoints and actual gaps; no Git publication inference."""
    root=Path(root);queue=[]
    batches=[('sd20-anna-hover-cycle-v2','hover phase compatibility'),('sd20-anna-dart-brake-v1','dart/brake source and root checks'),('sd20-anna-transitions-v1','reverse/nectar/perch support-state checks')]
    registered={b['batchId']:b for b in overlays if b.get('flightMotionProposal')}
    for batch_id,task in batches:
        record=registered.get(batch_id)
        if record and record.get('review') and record.get('reviewSHA256'):
            reviewed=(root/record['review']).resolve()
            if reviewed.is_relative_to(root.resolve()) and reviewed.is_file() and sha(reviewed)==record['reviewSHA256']:
                # Retained sourceMotionProposals preserve this completed checkpoint.
                # Git/publication status is owned by the coordinator's queue.
                continue
        candidates=[root/'motion'/batch_id,Path('/workspace/asset-production/motion')/batch_id]
        p=next((x for x in candidates if (x/'PRIMARY-SOURCE-MANIFEST.json').is_file()),None)
        original_folder=next((x for x in candidates if (x/'original.png').is_file()),None)
        retained=bool(p)
        queue.append({'priority':1,'speciesId':'anna_s_hummingbird','batchId':batch_id,'task':task,'checkpoint':'source review/registration checkpoint' if retained else 'producer frozen-export checkpoint; original retained' if original_folder else 'producer receipt checkpoint; actual completion UNKNOWN','retainedPrimaryManifest':str(p/'PRIMARY-SOURCE-MANIFEST.json') if p else None,'retainedPathScope':('canonical source root' if p and p.is_relative_to(root) else 'producer source only; not canonical intake' if p else None),'actualSourceRetained':retained,'nativeOriginalRetained':bool(original_folder),'registeredOverlay':bool(record),'newCallQueued':False,'workerRunning':'UNKNOWN','sourceAccepted':False,'GitPublicationStatus':'not inferred; coordinator owns publication queue'})
    next_priority=2 if queue else 1
    gap_candidates=[root/'motion/sd20-anna-transitions-v1/transition-gap-receipt.json',Path('/workspace/asset-production/motion/sd20-anna-transitions-v1/transition-gap-receipt.json')]
    gap=next((p for p in gap_candidates if p.is_file()),None)
    queue.append({'priority':next_priority,'speciesId':'anna_s_hummingbird','task':'Review existing contact/transition endpoint gaps and authored root-motion proof before choosing any new Anna art','checkpoint':'existing-source joint/contact/root proof; complete flight remains unaccepted','newCallQueued':False,'sourceAcceptedFullFlight':False,'gapEvidence':({'file':str(gap),'sha256':sha(gap),'pathScope':'canonical source' if gap.is_relative_to(root) else 'producer source only'} if gap else None)})
    missing=[]
    for bird in species:
        row=next(r for r in bird['slots'] if r['slot']=='look')
        if not row['provisionalUsefulSourceForThisSemanticSlot']:
            missing.append({'speciesId':bird['id'],'actualSlotState':row['state'],'sourceFrameIds':row.get('sourceFrameIds',[]),'existingStudyBeforeNewCall':bool(row.get('sourceFrameIds'))})
    missing.sort(key=lambda candidate: candidate['speciesId']!='black_phoebe')
    queue.append({'priority':next_priority+1,'task':'Select bounded missing look source work, Phoebe first when its look slot remains missing, then actual study-only/missing roster slots','candidates':missing,'newCallQueued':False,'orderingMeaning':'common-first product priority; not biological frequency'})
    queue.append({'priority':next_priority+2,'speciesId':'mourning_dove','task':'Repair existing gait/drink reuse contact and authored root/water target mappings before any new generation','newCallQueued':False,'checkpoint':'existing-source contact repair'})
    queue.append({'priority':next_priority+3,'speciesId':'house_finch','task':'Select bounded short ground hop or seed/beak-contact source work from actual gaps','newCallQueued':False,'checkpoint':'unassigned product-priority proposal'})
    return queue
