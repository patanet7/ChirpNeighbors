"""Deterministic source-raster inspection. No drawing edits or art/admission approval.

CLI: --config CONFIG --out NEW_DIRECTORY [--config-sha256 EXTERNAL_PIN].
Paths are relative to config directory. Config bytes, thresholds, tool and every
input hash are retained. Translation estimation is measurement, never fitting.
Status scope is explicit: PASS means a configured raster check, not anatomy.
"""
from pathlib import Path
import argparse, hashlib, json, math, sys, platform, importlib.metadata
import numpy as np
from PIL import Image, ImageDraw, __version__ as pillow_version

DEFAULTS = dict(alphaCutoff=128, maxOffsetWorld=1, widthRelativeWarn=.20,
                searchRadiusPixels=8, brightMin=240, brightChromaMax=15)
RANK = {'NOT_EVALUATED':0, 'NOT_RUN':0, 'PASS':1, 'WARN':2, 'FAIL':3}
def digest(data): return hashlib.sha256(data).hexdigest()
def put(p, value): p.write_text(json.dumps(value, indent=2, allow_nan=False)+'\n')
def status(values): return max(values, key=lambda x:RANK[x], default='NOT_EVALUATED')
def pointer(value, path):
    for key in path.strip('/').split('/') if path else []:
        key=key.replace('~1','/').replace('~0','~'); value=value[int(key)] if isinstance(value,list) else value[key]
    return value
def bbox(mask):
    y,x=np.nonzero(mask)
    return [int(x.min()),int(y.min()),int(x.max()+1),int(y.max()+1)] if len(x) else None
def centroid(mask):
    y,x=np.nonzero(mask); return [float(x.mean()),float(y.mean())] if len(x) else None
def rgba(path):
    with Image.open(path) as image:
        if image.format!='PNG': raise ValueError('Frame is not PNG: '+str(path))
        return np.array(image.convert('RGBA'))
def components(mask):
    try:
        from scipy.ndimage import label
        labels,n=label(mask); sizes=np.bincount(labels.ravel())[1:]
        return int(n),int(np.sum(sizes<=2)),int(sizes[sizes<=2].sum()),'scipy.ndimage.label four-neighbor'
    except ImportError:
        seen=mask.copy(); sizes=[]; h,w=mask.shape
        for y,x in zip(*np.nonzero(mask)):
            if not seen[y,x]: continue
            stack=[(y,x)]; seen[y,x]=False; count=0
            while stack:
                yy,xx=stack.pop(); count+=1
                for ny,nx in ((yy-1,xx),(yy+1,xx),(yy,xx-1),(yy,xx+1)):
                    if 0<=ny<h and 0<=nx<w and seen[ny,nx]: seen[ny,nx]=False; stack.append((ny,nx))
            sizes.append(count)
        return len(sizes),sum(n<=2 for n in sizes),sum(n for n in sizes if n<=2),'numpy/python four-neighbor'
def region(shape, roi):
    x,y,w,h=roi
    if not all(type(v) is int for v in roi) or min(x,y)<0 or min(w,h)<=0 or x+w>shape[1] or y+h>shape[0]: raise ValueError('ROI outside source canvas')
    mask=np.zeros(shape,bool); mask[y:y+h,x:x+w]=True; return mask
def difference(ref, cur, mask, shift):
    y,x=np.nonzero(mask); xx=x+shift[0]; yy=y+shift[1]
    valid=(xx>=0)&(xx<cur.shape[1])&(yy>=0)&(yy<cur.shape[0]); err=ref[y,x].astype(float)
    err[valid]=np.abs(ref[y[valid],x[valid]].astype(float)-cur[yy[valid],xx[valid]].astype(float))
    return float(err.mean()) if len(err) else None, int(np.count_nonzero(np.any(err!=0,axis=1)))
def inspect(config_path, output, expected_hash=None):
    raw=config_path.read_bytes(); config_hash=digest(raw)
    if expected_hash and config_hash!=expected_hash: raise ValueError('Config SHA256 mismatch')
    cfg=json.loads(raw,parse_constant=lambda v:(_ for _ in ()).throw(ValueError('Nonfinite JSON '+v)))
    if cfg['schemaVersion']!=1 or not cfg.get('candidates'): raise ValueError('Expected schemaVersion1/candidates')
    thresholds=DEFAULTS|cfg.get('thresholds',{})
    if set(thresholds)!=set(DEFAULTS) or not all(isinstance(v,(float,int)) and math.isfinite(v) for v in thresholds.values()): raise ValueError('Invalid threshold keys/values')
    if not 1<=thresholds['alphaCutoff']<=255 or min(thresholds['maxOffsetWorld'],thresholds['widthRelativeWarn'],thresholds['searchRadiusPixels'])<0: raise ValueError('Invalid threshold range')
    if type(thresholds['searchRadiusPixels']) is not int or type(thresholds['alphaCutoff']) is not int: raise ValueError('Integer cutoff/search radius required')
    cache={}; inputs=[]
    def bound(spec):
        path=(config_path.parent/spec.get('file',spec.get('png',''))).resolve(strict=True)
        actual=digest(path.read_bytes())
        if not spec.get('sha256') or actual!=spec['sha256']: raise ValueError(f'Input hash mismatch: {path}; expected={spec.get("sha256")}; actual={actual}')
        cache[str(path)]=spec['sha256']; inputs.append({'file':str(path),'sha256':spec['sha256']}); return path
    canonical=cfg.get('canonicalEvaluationContract'); canonical_pin=None
    if canonical:
        contract_path=bound(canonical); catalog=None
        if canonical.get('labelMapPointer'):
            catalog=pointer(json.loads(contract_path.read_text()),canonical['labelMapPointer'])
            label_ids=list(catalog) if isinstance(catalog,dict) else [x if isinstance(x,str) else x['id'] for x in catalog]
            if not all(isinstance(x,str) and x for x in label_ids) or len(set(label_ids))!=len(label_ids): raise ValueError('Canonical existing label map is not valid')
        canonical_pin={'file':str(contract_path),'sha256':canonical['sha256'],'existingIDCount':len(label_ids) if catalog is not None else None,'labelsAssignedByInspector':False}
    ids=set(); prepared=[]
    # Verify ALL declared artifacts before decoding/measuring any image.
    for candidate in cfg['candidates']:
        cid=candidate['id']
        if not isinstance(cid,str) or not cid or cid in ids: raise ValueError('Missing/duplicate candidate id')
        ids.add(cid)
        if not isinstance(candidate['motionIntent'],dict) or not candidate['motionIntent'].get('kind'): raise ValueError('Explicit motionIntent.kind required')
        frames=candidate['frames']
        if not frames or len({f['id'] for f in frames})!=len(frames): raise ValueError('Missing/duplicate frames')
        for f in frames:
            for key in ('action','pose','pivot','density'): f[key]
            if len(f['pivot'])!=2 or not all(math.isfinite(v) for v in f['pivot']) or not math.isfinite(f['density']) or f['density']<=0 or f.get('cssScale',1)<=0: raise ValueError('Invalid pivot/density/CSS scale')
            shift=f.get('expectedPixelTranslation',[0,0])
            if len(shift)!=2 or not all(type(v) is int for v in shift): raise ValueError('Expected translation is an integer source-pixel pair')
        paths=[bound(f) for f in frames]; mask=bound(candidate['stableMaskPNG']) if candidate.get('stableMaskPNG') else None
        manifest=bound(candidate['actionManifest']) if candidate.get('actionManifest') else None
        codec=candidate.get('codecReceipt'); receipts=None
        if codec: receipts=(bound(codec),bound(codec['canonicalSource']))
        for link in candidate.get('reevaluationLinks',[]):
            if link.get('existingReport'):
                previous=bound(link['existingReport'])
                if link.get('existingReportSHA256')!=digest(previous.read_bytes()): raise ValueError('Reevaluation report link hash differs')
        trajectory=candidate.get('expectedTrajectory')
        if trajectory is not None and (len(trajectory)!=len(frames) or any(len(p)!=2 or not all(math.isfinite(v) for v in p) for p in trajectory)): raise ValueError('Expected trajectory must contain one finite world-root pair per frame')
        prepared.append((candidate,paths,mask,manifest,receipts))
    output.mkdir(parents=True,exist_ok=False); (output/'config.json').write_bytes(raw)
    report={'schemaVersion':1,'scope':'source-raster diagnostics only; no anatomy, physical support, subjective art or runtime approval',
            'configSHA256':config_hash,'externalConfigPinVerified':bool(expected_hash),'toolSHA256':digest(Path(__file__).read_bytes()),
            'toolVersions':{'python':platform.python_version(),'Pillow':pillow_version,'NumPy':np.__version__,'OpenCV':'NOT_USED'},
            'canonicalDefectId':None,'evaluationContractPin':canonical_pin,'canonicalLabelsStatus':'PENDING_SHARED_CONTRACT' if canonical_pin is None else 'PIN_VERIFIED_MEASUREMENTS_UNLABELED','severity':None,'confidence':None,
            'thresholds':thresholds,'thresholdCalibration':'Static predeclared values; no fitting/learning/calibration in this run',
            'inputs':inputs,'candidates':[],'runtimeAdmission':False,'sourceImagesModified':False,'modelCalls':0}
    try: report['toolVersions']['SciPy']=importlib.metadata.version('scipy')
    except importlib.metadata.PackageNotFoundError: report['toolVersions']['SciPy']=None
    for number,(c,paths,mask_path,manifest,receipts) in enumerate(prepared):
        folder=output/f'{number:03d}'; folder.mkdir(); arrays=[rgba(p) for p in paths]
        ref=arrays[0]; cutoff=thresholds['alphaCutoff']; stable=None
        if c.get('stableBodyROI') is not None: stable=region(ref.shape[:2],c['stableBodyROI'])
        if mask_path:
            mask_image=Image.open(mask_path)
            if mask_image.mode not in ('L','1'): raise ValueError('Stable mask must be explicit L/1, not implicit RGBA ownership')
            mask=np.array(mask_image.convert('L'))>0
            if mask.shape!=ref.shape[:2]: raise ValueError('Stable mask/reference dimensions differ')
            stable=mask if stable is None else stable&mask
        cr={'id':c['id'],'speciesId':c.get('speciesId'),'assetId':c.get('assetId'),'clipId':c.get('clipId'),'context':c.get('context'),'supportRequirement':c.get('supportRequirement'),
            'repairDecision':c.get('repairDecision'),'repairDecisionAuthority':'Caller-supplied metadata, not an automatic art decision','reevaluationLinks':c.get('reevaluationLinks',[]),'reevaluationRefs':c.get('reevaluationRefs',[]),
            'canonicalDefectId':None,'severity':None,'confidence':None,'motionIntent':c['motionIntent'],'frames':[],'expectedTrajectory':c.get('expectedTrajectory'),
            'anatomyAndPhysicalSupport':'NOT_EVALUATED','subjectiveArt':'NOT_EVALUATED'}
        colors=[]; visible_colors=[]; panels=[]; first_width=None; previous=None
        for i,(f,a) in enumerate(zip(c['frames'],arrays)):
            h,w=a.shape[:2]; alpha=a[:,:,3]; mask=alpha>=cutoff; nonzero=alpha>0; box=bbox(mask); center=centroid(mask); den=f['density']; pivot=f['pivot']
            edge=np.pad(mask,1); interior=edge[1:-1,:-2]&edge[1:-1,2:]&edge[:-2,1:-1]&edge[2:,1:-1]; boundary=mask&~interior
            partial=(alpha>0)&(alpha<255); bright=(a[:,:,:3].min(2)>thresholds['brightMin'])&(np.ptp(a[:,:,:3],axis=2)<=thresholds['brightChromaMax'])
            palette={tuple(x) for x in a[alpha==255,:3].tolist()}; visible_palette={tuple(x) for x in a[mask,:3].tolist()}; colors.append(palette); visible_colors.append(visible_palette); n,tiny,pixels,backend=components(mask)
            px,py=map(lambda v:int(math.floor(v)),pivot); in_bounds=0<=pivot[0]<w and 0<=pivot[1]<h
            entry={'id':f['id'],'clipId':f.get('clipId',c.get('clipId')),'action':f['action'],'pose':f['pose'],'PNGsha256':digest(paths[i].read_bytes()),'canvasPixels':[w,h],'contacts':f.get('contacts',c.get('contacts',[])),
                'evidenceType':'MEASURED_SOURCE_RASTER','inferredAnatomy':None,'canonicalDefectId':None,'severity':None,'confidence':None,
                'stableBodyROI':c.get('stableBodyROI'),'stableMaskPNG':c.get('stableMaskPNG'),'expectedROIChanges':c['motionIntent'].get('expectedROIChanges',[]),
                'decodedRGBAId':'frame.sha256.'+digest(f'RGBA8;{w}x{h};'.encode()+a.tobytes()),'density':den,'worldCanvas':[w/den,h/den],
                'cssCanvas':[w/den*f.get('cssScale',1),h/den*f.get('cssScale',1)],'pivot':pivot,'pivotInBounds':in_bounds,'pivotAlpha':int(alpha[py,px]) if in_bounds else None,
                'alphaBBox':bbox(nonzero),'thresholdBBox':box,'thresholdCentroid':center,'alphaNonzeroPixels':int(nonzero.sum()),'partialAlphaPixels':int(partial.sum()),
                'edgeTouchPixels':int(nonzero[0].sum()+nonzero[-1].sum()+nonzero[1:-1,0].sum()+nonzero[1:-1,-1].sum()),
                'componentCount':n,'tinyComponentsLE2':tiny,'tinyComponentPixels':pixels,'componentBackend':backend,'opaqueRGBCount':len(palette),'visibleRGBCountAtAlphaCutoff':len(visible_palette),
                'brightLowChromaBoundaryPixelsProxy':int((bright&(boundary|partial)&nonzero).sum()),'fringePixelsProxy':int(partial.sum()),
                'anchorRelativeCentroidWorld':[(center[j]-pivot[j])/den for j in (0,1)] if center else None,'contactROIProxies':[],
                'expectedPixelTranslation':f.get('expectedPixelTranslation',[0,0]),'checks':{}}
            root=c.get('expectedTrajectory',[[0,0]]*len(arrays))[i]
            entry['expectedRootWorld']=root if c.get('expectedTrajectory') is not None else None
            entry['projectedCentroidAtDeclaredRootWorld']=[root[j]+entry['anchorRelativeCentroidWorld'][j] for j in (0,1)] if center and c.get('expectedTrajectory') is not None else None
            entry['checks']['raster']={'status':'FAIL' if not nonzero.any() or not in_bounds else 'WARN' if entry['edgeTouchPixels'] else 'PASS','scope':'empty raster/pivot bounds; edge touch is a clipping proxy, not anatomy'}
            entry['checks']['binaryAlpha']={'status':('FAIL' if partial.any() else 'PASS') if c.get('requireBinaryAlpha',False) else 'NOT_EVALUATED','scope':'configured binary-alpha prerequisite only; not canonical codec execution'}
            entry['checks']['whiteNoiseProxies']={'status':'WARN' if entry['brightLowChromaBoundaryPixelsProxy'] or tiny else 'PASS','scope':'proxy counts only; no automatic white-edge/noise/art rejection'}
            width=(box[2]-box[0])/den if box else None
            if first_width is None: first_width=width
            entry['visibleBBoxWidthWorld']=width; entry['relativeWidthChangeFromFirst']=width/first_width-1 if width is not None and first_width else None
            entry['checks']['width']={'status':'WARN' if entry['relativeWidthChangeFromFirst'] is not None and abs(entry['relativeWidthChangeFromFirst'])>thresholds['widthRelativeWarn'] else 'PASS','scope':'silhouette width proxy; intentional wings/directional asymmetry may change width'}
            for probe in c.get('contactProbeROIs',[]):
                roi=region((h,w),probe['rect']); ys,xs=np.nonzero(roi&mask); x,y,rw,rh=probe['rect']
                entry['contactROIProxies'].append({'id':probe['id'],'rect':probe['rect'],'maxAlpha':int(alpha[roi].max()),'thresholdPixelCount':len(ys),
                    'lowestThresholdRow':int(ys.max()) if len(ys) else None,'baselineFromPivotWorld':float((ys.max()-pivot[1])/den) if len(ys) else None,'physicalContact':'NOT_EVALUATED'})
            if i:
                for probe,first_probe in zip(entry['contactROIProxies'],cr['frames'][0]['contactROIProxies']):
                    values=(probe['baselineFromPivotWorld'],first_probe['baselineFromPivotWorld'])
                    probe['baselineDeltaWorldFromFirst']=values[0]-values[1] if None not in values else None
            if previous:
                entry['previousFrameDelta']={'anchorRelativeCentroidWorld':[entry['anchorRelativeCentroidWorld'][j]-previous['anchorRelativeCentroidWorld'][j] for j in (0,1)] if center and previous['anchorRelativeCentroidWorld'] else None,
                    'bboxWorld':[box[j]/den-previous['thresholdBBox'][j]/previous['density'] for j in range(4)] if box and previous['thresholdBBox'] else None}
            entry['stableRegion']={'status':'NOT_EVALUATED','reason':'No stable mask/ROI supplied; global centroid changes are report-only.'}
            if stable is not None:
                if a.shape!=ref.shape: raise ValueError('Stable-region comparison requires equal source canvas')
                support=stable&(ref[:,:,3]>=cutoff); expected=np.array(entry['expectedPixelTranslation'])-np.array(c['frames'][0].get('expectedPixelTranslation',[0,0]))
                if support.any():
                    radius=thresholds['searchRadiusPixels']; scored=[]
                    for dy in range(int(expected[1])-radius,int(expected[1])+radius+1):
                        for dx in range(int(expected[0])-radius,int(expected[0])+radius+1):
                            error,changed=difference(ref,a,support,(dx,dy)); scored.append((error,(dx-expected[0])**2+(dy-expected[1])**2,dy,dx))
                    error,_,dy,dx=min(scored); ties=sum(s[0]==error for s in scored); residual=[float((dx-expected[0])/den),float((dy-expected[1])/den)]; _,changed=difference(ref,a,stable,expected)
                    failed=max(map(abs,residual))>thresholds['maxOffsetWorld']
                    entry['stableRegion']={'status':('WARN' if ties>1 else 'FAIL' if failed else 'WARN' if changed else 'PASS') if c['motionIntent'].get('registrationExpectedStable',False) else 'NOT_EVALUATED',
                        'observedPixelTranslation':[dx,dy],'residualWorld':residual,'meanAbsoluteRGBAErrorAtBestOffset':error,'changedPixelsAtDeclaredTranslation':changed,
                        'equallyBestOffsetCount':ties,
                        'scope':'configured stable raster region, integer translation estimate only; no bitmap/pivot changes or anatomical inference'}
            entry['paletteDriftFromFirst']={'scope':'RGB tuples only where alpha==255','addedOpaqueRGBCount':len(palette-colors[0]),'jaccardDistance':1-len(palette&colors[0])/len(palette|colors[0]) if palette|colors[0] else 0}
            entry['visiblePaletteDriftFromFirst']={'scope':f'RGB tuples where alpha>={cutoff}, not a canonical codec palette verdict','addedRGBCount':len(visible_palette-visible_colors[0]),'jaccardDistance':1-len(visible_palette&visible_colors[0])/len(visible_palette|visible_colors[0]) if visible_palette|visible_colors[0] else 0}
            entry['centeringSuggestion']={'status':'NOT_EVALUATED','reason':'Directional asymmetry and off-center framing are not failures.'}
            if c.get('centerSuggestions',False) and box:
                delta=[round((w-box[0]-box[2])/2),round((h-box[1]-box[3])/2)]
                yy,xx=np.nonzero(nonzero); risk=int(np.count_nonzero((xx+delta[0]<0)|(xx+delta[0]>=w)|(yy+delta[1]<0)|(yy+delta[1]>=h)))
                contacts=[({**p,'x':p['x']+delta[0],'y':p['y']+delta[1]} if 'x' in p and 'y' in p else {**p,'point':[p['point'][j]+delta[j] for j in (0,1)]} if 'point' in p else {'original':p,'translatedMetadata':'NOT_EVALUATED_UNKNOWN_FORMAT'}) for p in entry['contacts']]
                entry['centeringSuggestion']={'status':'NOT_EVALUATED','hypotheticalPixelTranslation':delta,'pivotIfTranslated':[pivot[j]+delta[j] for j in (0,1)],'contactsIfTranslated':contacts,'stableMasksRequireSameTranslation':mask_path is not None,'nonzeroPixelsDiscardedIfApplied':risk,'allProbeROIsIfTranslated':[{'id':p['id'],'rect':[p['rect'][0]+delta[0],p['rect'][1]+delta[1],*p['rect'][2:]]} for p in c.get('contactProbeROIs',[])],'applied':False,'warning':'Texture repack only: translating pixels AND every pivot/contact/mask consistently preserves the rendered world pose and DOES NOT repair visible jitter. No suggestion is approval; no translation applied.'}
            entry['status']=status([x['status'] for x in entry['checks'].values()]+[entry['stableRegion']['status']]); cr['frames'].append(entry); previous=entry
            # Derivative previews only: straight nearest source sampling, light/dark normal CSS scale.
            size=tuple(max(1,math.ceil(v)) for v in entry['cssCanvas'])
            if size[0]*size[1]>16000000: raise ValueError('Diagnostic preview exceeds16M pixels')
            im=Image.fromarray(a).resize(size,Image.Resampling.NEAREST); panel=Image.new('RGB',(size[0]*2,size[1]+22)); draw=ImageDraw.Draw(panel)
            for side,color in enumerate(((228,224,204),(24,42,49))):
                bg=Image.new('RGBA',size,color+(255,)); bg.alpha_composite(im); panel.paste(bg.convert('RGB'),(side*size[0],22))
            draw.text((2,2),f['id']+' / '+f['pose'],fill='white'); panels.append(panel)
            overlay=Image.fromarray(a).copy(); draw=ImageDraw.Draw(overlay)
            if box: draw.rectangle((box[0],box[1],box[2]-1,box[3]-1),outline='cyan')
            draw.line((pivot[0]-3,pivot[1],pivot[0]+3,pivot[1]),fill='red'); draw.line((pivot[0],pivot[1]-3,pivot[0],pivot[1]+3),fill='red')
            for probe in c.get('contactProbeROIs',[]):
                x,y,rw,rh=probe['rect']; draw.rectangle((x,y,x+rw-1,y+rh-1),outline='magenta')
            overlay.save(folder/f'frame-{i:03d}-overlay.png'); put(folder/f'frame-{i:03d}.json',entry)
        coverage={'status':'NOT_EVALUATED','reason':'No hash-bound declared action manifest; never infer action completeness from filenames.'}
        if manifest:
            declared=pointer(json.loads(manifest.read_text()),c['actionManifest']['actionsPointer']); actions=list(declared) if isinstance(declared,dict) else [x if isinstance(x,str) else x['id'] for x in declared]
            missing=sorted(set(c.get('requiredActions',[]))-set(actions)); coverage={'status':'FAIL' if missing else 'PASS','declared':actions,'required':c.get('requiredActions',[]),'missing':missing,'scope':'declared action keys only, not genuine motion/anatomy completeness'}
        cr['actionCoverage']=coverage; cr['codec']={'status':'NOT_RUN','reason':'No nominated current-code, exact-input, hash-bound codec receipt.'}
        residuals=[max(map(abs,f['stableRegion']['residualWorld'])) for f in cr['frames'] if 'residualWorld' in f['stableRegion']]
        cr['stableRegistrationMaxResidualWorld']=max(residuals) if residuals else None
        cr['temporalOrBiologicalActionCompleteness']='NOT_EVALUATED; declared keys and raster changes do not prove action semantics'
        if receipts:
            spec=c['codecReceipt']; receipt=json.loads(receipts[0].read_text()); source=spec['canonicalSource']
            bound_hashes=pointer(receipt,spec['frameHashesPointer']); bound_hashes=[bound_hashes] if isinstance(bound_hashes,str) else bound_hashes
            if spec.get('frameHashField'): bound_hashes=[x[spec['frameHashField']] for x in bound_hashes]
            if sorted(bound_hashes)!=sorted(f['sha256'] for f in c['frames']) or pointer(receipt,source['receiptHashPointer'])!=source['sha256']: raise ValueError('Codec receipt not bound to exact frames/current nominated code')
            value=pointer(receipt,spec['statusPointer']); value=('PASS' if value else 'FAIL') if type(value) is bool else value
            cr['codec']={'status':value,'scope':'reused exact receipt, not rerun; nominated current module hash verified','receiptSHA256':spec['sha256'],'canonicalSourceSHA256':source['sha256']}
            if cr['codec']['status'] not in ('PASS','WARN','FAIL','NOT_EVALUATED'): raise ValueError('Codec receipt status must be an explicit inspection status')
            if spec.get('rectanglesPointer'):
                count=pointer(receipt,spec['rectanglesPointer'])
                if type(count) is not int or count<0: raise ValueError('Rectangle receipt value is not a measured count')
                cr['codec']['reportedRectangles']=count
        sheet=Image.new('RGB',(max(p.width for p in panels),sum(p.height for p in panels)),(70,70,70)); y=0
        for panel in panels: sheet.paste(panel,(0,y)); y+=panel.height
        sheet.save(folder/'light-dark-contact-sheet.png'); cr['status']=status([f['status'] for f in cr['frames']]+[coverage['status'],cr['codec']['status']]); put(folder/'candidate.json',cr); report['candidates'].append(cr)
    if digest(config_path.read_bytes())!=config_hash or any(digest(Path(p).read_bytes())!=h for p,h in cache.items()): raise ValueError('Config/input changed during inspection')
    report['status']=status(c['status'] for c in report['candidates']); report['allInputHashesUnchanged']=True; put(output/'inspection.json',report)
    return report

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__); parser.add_argument('--config',required=True,type=Path); parser.add_argument('--out',required=True,type=Path); parser.add_argument('--config-sha256'); args=parser.parse_args()
    already_existed=args.out.exists()
    try:
        result=inspect(args.config.resolve(),args.out,args.config_sha256); print(json.dumps({'status':result['status'],'report':str(args.out/'inspection.json'),'runtimeAdmission':False}))
    except (OSError,ValueError,KeyError,TypeError,IndexError) as error:
        failure={'status':'FAIL','scope':'configuration/input/inspection execution','error':str(error),'configSHA256':digest(args.config.read_bytes()) if args.config.is_file() else None,'toolSHA256':digest(Path(__file__).read_bytes()),'runtimeAdmission':False,'canonicalDefectId':None,'evaluationContractPin':None,'canonicalLabelsStatus':'PENDING_SHARED_CONTRACT','severity':None,'confidence':None,'modelCalls':0}
        if not already_existed:
            try: args.out.mkdir(parents=True,exist_ok=True); put(args.out/'inspection-error.json',failure)
            except OSError: pass
        print(json.dumps(failure),file=sys.stderr); sys.exit(2)
