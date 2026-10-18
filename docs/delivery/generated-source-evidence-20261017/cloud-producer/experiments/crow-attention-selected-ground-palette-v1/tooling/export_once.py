from pathlib import Path
from PIL import Image,ImageDraw,__version__ as pillow_version
import numpy as np,json,hashlib,shutil,copy,datetime
P=Path(__file__).resolve().parent.parent;R=P.parent.parent
O=R/'experiments/resting-repair-ground-motion-v1/attention-repairs/american_crow'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def put(n,v):(P/n).write_text(json.dumps(v,indent=2)+'\n')
def fid(im):return 'frame.sha256.'+hashlib.sha256(f'RGBA8;{im.width}x{im.height};'.encode()+im.tobytes()).hexdigest()
assert not (P/'export-start.json').exists(),'No automatic export retry'
pre=json.loads((P/'PREREGISTRATION.json').read_text());h=json.loads((O/'source-handoff.json').read_text());old=copy.deepcopy(h)
def guards():
 for g in pre['frozenPriorGuards']:
  q=R/g['directory']; assert sha(R/g['ledger'])==g['ledgerSHA256']
  assert all(sha(q/f['path'])==f['SHA256'] for f in json.loads((R/g['ledger']).read_text())['files'])
 assert sha(R/pre['safeGroundGuard']['file'])==pre['safeGroundGuard']['sha256']
guards();put('export-start.json',{'atUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'preregistrationSHA256':sha(P/'PREREGISTRATION.json'),'nativeCalls':0,'newDrawings':0,'exportAttempt':1})
for d in ['frames','raw-full','full-projected','source-images','provenance','contract-intake']:(P/d).mkdir()
palette=np.array(pre['paletteSource']['opaqueRGB'],dtype=np.int32);records=[];proof=[];fulls={};atlas=Image.new('RGBA',(h['candidateCanvas'][0]*3,h['candidateCanvas'][1]))
for i,(f,source) in enumerate(zip(h['frames'],pre['sourceFrames'])):
 assert sha(R/source['rawPNG'])==source['rawPNGsha256'];raw=Image.open(R/source['rawPNG']).convert('RGBA');a=np.array(raw);mask=a[:,:,3]>=128
 assert hashlib.sha256((mask.astype(np.uint8)*255).tobytes()).hexdigest()==source['binaryAlphaMaskSHA256']
 rgb=a[:,:,:3][mask].astype(np.int32);indices=((rgb[:,None,:]-palette[None,:,:])**2).sum(2).argmin(1)
 b=np.zeros_like(a);b[mask,:3]=palette[indices].astype(np.uint8);b[mask,3]=255;full=Image.fromarray(b);cut=full.crop(h['crop']);prior=Image.open(O/f['png']).convert('RGBA')
 assert cut.getchannel('A').tobytes()==prior.getchannel('A').tobytes()
 back=Image.new('RGBA',full.size);back.paste(cut,tuple(h['commonCropOrigin']));assert back.tobytes()==full.tobytes()
 role=f['id'];shutil.copyfile(R/source['rawPNG'],P/'raw-full'/f'{role}.png');shutil.copyfile(R/source['nativePNG'],P/'source-images'/f'{role}-native.png')
 full.save(P/'full-projected'/f'{role}.png');cut.save(P/'frames'/f'{role}.png');fulls[role]=full;atlas.paste(cut,(i*cut.width,0))
 r=copy.deepcopy(f);r.update({'sourcePNG':f'source-images/{role}-native.png','sourcePNGsha256':sha(P/'source-images'/f'{role}-native.png'),'rawPNG':f'raw-full/{role}.png','rawPNGsha256':sha(P/'raw-full'/f'{role}.png'),'png':f'frames/{role}.png','PNGsha256':sha(P/'frames'/f'{role}.png'),'decodedRGBAId':fid(cut),'newDrawing':False,'sourceWasNewOnlyInEarlierNativeBatch':f['newDrawing'],'registrationUnchangedFromEarlierFamily':True})
 r.pop('globallyRegistered',None);records.append(r)
 proof.append({'id':role,'sameRawPNGBytes':sha(P/r['rawPNG'])==source['rawPNGsha256'],'sameNativePNGBytes':sha(P/r['sourcePNG'])==source['nativePNGsha256'],'sameAlphaAsPrior63':True,'nonzeroDiscardedRGBA':0,'opaquePixels':int(mask.sum()),'opaqueRGBColorsUsed':len(np.unique(b[mask,:3],axis=0)),'RGBChangedAtOpaquePixels':int(np.any(b[mask,:3]!=a[mask,:3],axis=1).sum()),'sourcePNGsha256':source['nativePNGsha256'],'outputPNGsha256':r['PNGsha256'],'fullProjectedPNGsha256':sha(P/'full-projected'/f'{role}.png')})
atlas.save(P/'atlas.png')
for clip in h['clips'][1:]:
 ims=[Image.open(P/'frames'/f"{f['frameId']}.png").convert('RGBA') for f in clip['frames']]
 ims[0].save(P/f"{clip['id']}.apng",save_all=True,append_images=ims[1:],duration=[f['durationTicks']*1000/30 for f in clip['frames']],loop=1,disposal=1,blend=0,optimize=False)
for filename in ['PRIMARY-SOURCE-MANIFEST.json','source-handoff.json','prompt.txt','native-call-arguments.json','native-return-receipt.json','call-dispatch-receipt.json','source-lineage.json','blink-source-provenance.json','current-primary-manifest-reference.json']:
 shutil.copyfile(O/filename,P/'provenance'/('earlier-attention-'+filename))
shutil.copytree(O/'historical-reference',P/'provenance'/'historical-reference')
shutil.copyfile(R/pre['paletteSource']['file'],P/'provenance'/'unchanged-safe-ground12.png')
for name,up in [('prior63','american_crow-repair-v1'),('prior32','american-crow-palette32-v1')]:
 q=R/'experiments/resting-repair-ground-motion-v1/contract-intake/receipts'/up
 for filename in ['CHECK-SUMMARY.json','commands.json','actual-pixel-subset.stderr.txt']:
  if (q/filename).exists():shutil.copyfile(q/filename,P/'provenance'/f'{name}-{filename}')
h.update({'kind':'Zero-native source-only fixed-existing-palette family derivative','batchId':P.name,'newNativeCalls':0,'newDrawings':0,'reusedDrawings':3,'frames':records,'opaquePaletteColors':11,'palette':'One exact existing11opaque RGB palette from safe ground12; nearest squared Euclidean RGB, ascending lexicographic tie-break, no dithering/training/variants. Lossy RGB-only operation.','atlas':{'file':'atlas.png','sha256':sha(P/'atlas.png'),'width':atlas.width,'height':atlas.height},'sourceUsefulness':'UNKNOWN pending fresh independent normal-size palette/eye/head/stance review','runtimeAdmission':False,'liveVisualAcceptance':False,'ancestry':'provenance/earlier-attention-source-lineage.json','previousSourceHandoff':{'file':'provenance/earlier-attention-source-handoff.json','sha256':sha(P/'provenance/earlier-attention-source-handoff.json')},'nativeGenerationCountedOnlyInEarlierPacket':True,'safeGroundAssetModified':False,'canonicalDefectId':None,'evaluationContractPin':None,'canonicalLabelsStatus':'PENDING_SHARED_CONTRACT'})
put('source-handoff.json',h)
put('PRIMARY-SOURCE-MANIFEST.json',{'batchId':P.name,'speciesId':'american_crow','nativeCalls':0,'newDrawings':0,'frames':[],'reusedFrames':records,'originalGenerationManifest':{'file':'provenance/earlier-attention-PRIMARY-SOURCE-MANIFEST.json','sha256':sha(P/'provenance/earlier-attention-PRIMARY-SOURCE-MANIFEST.json')},'operation':'Single authorized lossy RGB projection to already selected ground palette. Original native drawings unchanged; no new prompt/model call.','sourceStatus':'Await actual nominated checks and fresh independent derivative reviews','geometryReviewed':False,'supportWorld':None,'runtimeAdmission':False,'model':None,'seed':None})
put('frame-to-action-map.json',{'speciesId':'american_crow','manifest':{'file':'source-handoff.json','sha256':sha(P/'source-handoff.json')},'atlas':h['atlas'],'sourceToRenderFrames':[{'sourceFrameId':f['sourceFrameId'],'newDrawing':False,'sourcePNG':f['sourcePNG'],'sourcePNGsha256':f['sourcePNGsha256'],'renderFrameId':f['id'],'outputPNG':f['png'],'outputPNGsha256':f['PNGsha256'],'atlasRect':f['atlasRect']} for f in records],'clips':h['clips'],'runtimeAdmission':False})
put('geometry-preservation-proof.json',{'frames':proof,'sameGeometryFields':all(h[k]==old[k] for k in pre['geometry']),'sameClocks':h['clips']==old['clips'],'crop':h['crop'],'pivot':h['candidatePivot'],'safeGroundUnchanged':True,'frozenPriorGuardsVerified':pre['frozenPriorGuards'],'contacts':[],'geometryScope':'image-registration-only','physicalSupportReviewed':False,'supportWorld':None})
put('fixed-palette.json',pre['paletteSource']|{'rule':'Nearest squared Euclidean RGB; lexicographic ascending tie-break','dither':'NONE','trainingRuns':0,'nativeCalls':0,'newDrawings':0})
shutil.copyfile(O/'player.js',P/'player.js')
js=(P/'player.js').read_text().replace('window.ATTENTION_REPAIR_REVIEW=window.FAMILY_REVIEW={ready:true,select,play,seek,getState:state}',"window.REPAIR_REVIEW=window.ATTENTION_REPAIR_REVIEW=window.FAMILY_REVIEW={ready:true,select,play,seek,pause:()=>{epoch++;running=false;draw();return state()},getState:state}")
(P/'player.js').write_text(js)
html=(O/'review.html').read_text().replace('targeted attention source repair','single fixed-ground-palette attention derivative').replace('One new native head-attention drawing; exact existing neutral and closed sources reused. Whole-canvas legacy-world sampler, one shared palette/crop, no pose fitting or foot snap.','Zero new native calls or drawings. Three exact existing drawings, one fixed11opaque RGB projection. Safe ground12 source is unchanged. Raw family mask/canvas/crop/root/clocks stay fixed; no head cutout, fitting, repainting, foot snap or palette variants.').replace('Shared codec / common crop','Fixed ground11opaque palette / common crop')
(P/'review.html').write_text(html)
sheet=Image.new('RGB',(186*3,186*2+62),'#eee9da');dr=ImageDraw.Draw(sheet)
for i,f in enumerate(records):
 dr.text((i*186+5,5),f['id']+' (fixed ground palette)',fill='#182a32')
 for j,bg in enumerate(['#e5e0cd','#182a32']):
  base=Image.new('RGBA',(186,186),bg);base.alpha_composite(fulls[f['id']]);sheet.paste(base.convert('RGB'),(i*186,25+j*198))
sheet.save(P/'normal-light-dark.png')
# Source-derived head and feet comparisons; exact same crop for each phase and representation.
regions=[('head',(105,35,164,78)),('feet',(78,119,132,149))];panels=Image.new('RGB',(3*236,4*184),'#eee9da');dr=ImageDraw.Draw(panels)
for j,(label,rect) in enumerate(regions):
 for i,f in enumerate(records):
  for kind,src in enumerate([Image.open(P/f['rawPNG']).convert('RGBA'),fulls[f['id']]]):
   crop=src.crop(rect).resize(((rect[2]-rect[0])*4,(rect[3]-rect[1])*4),Image.Resampling.NEAREST);x=i*236;y=(j*2+kind)*184;dr.text((x+2,y+2),f"{f['id']} {label} {'raw' if kind==0 else 'fixed11'}",fill='#182a32');panels.paste(crop,(x,y+16),crop)
panels.save(P/'head-feet-diagnostics.png')
guards();put('export-receipt.json',{'atUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'exportPasses':1,'nativeCalls':0,'newDrawings':0,'reusedDrawings':3,'paletteVariants':1,'quantizerTrainingRuns':0,'fullStage':[186,186],'crop':h['crop'],'pivot':h['candidatePivot'],'canvas':h['candidateCanvas'],'unchangedRawNativeMaskGeometryClocks':True,'safeGroundAndOldFrozenTargetsUnchanged':True,'preregistrationSHA256':sha(P/'PREREGISTRATION.json'),'exporterSHA256':sha(Path(__file__)),'Pillow':pillow_version,'NumPy':np.__version__,'actualChecks':'Pending single nominated test set','sourceUsefulness':'UNKNOWN','runtimeAdmission':False})
print(json.dumps({'exportPasses':1,'nativeCalls':0,'newDrawings':0,'frames':proof,'sourceHandoffSHA256':sha(P/'source-handoff.json')}))
