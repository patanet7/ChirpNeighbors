from pathlib import Path
from PIL import Image
from functools import lru_cache
import hashlib, json, shutil, time, datetime, re

R = Path('/workspace/asset-production')
P = Path(__file__).resolve().parent
C = R / 'experiments/common-slot-zero-call-batch-v1/species/mourning_dove'
S = R / 'motion/sd20-mourning-dove-blink-v1'
assert not (P/'export-receipt.json').exists(), 'One family export only; do not overwrite.'
start=time.perf_counter()
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def put(n,v): (P/n).write_text(json.dumps(v,indent=2)+'\n')
def identity(im): return 'frame.sha256.'+hashlib.sha256(f'RGBA8;{im.width}x{im.height};'.encode()+im.tobytes()).hexdigest()
def copy(src,dst):
    q=P/dst;q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,q);return {'file':dst,'SHA256':sha(q),'upstream':str(src.relative_to(R))}

bank=json.loads((R/'frame-bank.json').read_text())
rows={f['frameId']:f for f in bank['frames']}
ids={'neutral':'frame.sha256.168bf85942235e125601c6e245b5f2060f4a254ef2427d1f2d9adeb88ef90b81',
     'blink':'frame.sha256.3d8652745686a643174e42d31245822af39e47f7e5c190cf08ff8dd812edbef2',
     'look':'frame.sha256.6d37dd4147c8a7864ca401e13043145c442b8df752318d799a4b3039c8cf4a66'}
originals={}
for role,id in ids.items():
    row=rows[id];src=R/row['file'];im=Image.open(src).convert('RGBA')
    assert sha(src)==row['fileSha256'] and identity(im)==id
    originals[role]=copy(src,'sources/'+role+'-registered.png')
copies=[]
for name in ['prompt.txt','native-call-arguments.json','call-dispatch-receipt.json','prompt-byte-audit.json','PRIMARY-SOURCE-MANIFEST.json','texture-review-manifest.json']:
    data=(S/name).read_bytes()
    assert not re.search(rb'libfile_[a-f0-9]{32}|data:image/[^;]+;base64,',data)
    copies.append(copy(S/name,'provenance/closure-'+name))
for name in ['source-handoff.json','export-receipt.json','measurements.json']:
    copies.append(copy(C/name,'provenance/reviewed-look-'+name))
# Retain the exact historical native original separately, even though it equals registered closure.
copies.append(copy(S/'original.png','sources/closure-native-original.png'))
ret=json.loads((S/'native-return-receipt.json').read_text())
put('closure-origin.json',{'registeredSourceID':ids['blink'],'nativeOriginalSHA256':sha(S/'original.png'),
    'nativeReturnReceiptUpstream':'motion/sd20-mourning-dove-blink-v1/native-return-receipt.json',
    'nativeReturnReceiptSHA256':sha(S/'native-return-receipt.json'),'nativeDimensions':ret['nativeDimensions'],
    'historicalNativeCalls':1,'newCallsInThisFamily':0,'model':None,'seed':None,
    'qualification':'Historical native call, not a new drawing; portable receipt omits generated-file UUID path. Exact prompt/arguments retained.'})

oldcrop=[22,73,158,162]; oldpivot=[83,77]
palette=set()
for q in sorted((C/'codec-cropped').glob('*.png')):
    im=Image.open(q).convert('RGBA')
    assert set(im.getchannel('A').getdata()) <= {0,255}
    palette.update(v[:3] for v in im.getdata() if v[3]==255)
palette=sorted(palette);assert len(palette)==63
put('existing-palette.json',{'colors':palette,'opaqueColors':63,'origin':'Exact union of ALL four previously frozen Dove codec PNG opaque colors; no old PNG requantization.',
    'inputs':[{'path':str(q.relative_to(R)),'SHA256':sha(q)} for q in sorted((C/'codec-cropped').glob('*.png'))]})
@lru_cache(None)
def nearest(rgb):
    return min(palette,key=lambda c:(sum((c[i]-rgb[i])**2 for i in range(3)),c))

native=Image.open(S/'closed-native.png').convert('RGBA')
raw=Image.new('RGBA',(192,192))
raw.putdata([native.getpixel((((2*x+1)*native.width)//384,((2*y+1)*native.height)//384)) for y in range(192) for x in range(192)])
clean=Image.new('RGBA',(192,192));clean.putdata([(*nearest(v[:3]),255) if v[3]>=128 else (0,0,0,0) for v in raw.getdata()])
(P/'raw-full').mkdir(exist_ok=True);raw.save(P/'raw-full/blink.png')
full={'blink':clean}
for role,oldrole in [('neutral','neutral'),('look','neck-bend')]:
    cut=Image.open(C/'codec-cropped'/f'{oldrole}.png').convert('RGBA')
    full[role]=Image.new('RGBA',(192,192));full[role].paste(cut,oldcrop[:2])
    copies.append(copy(C/'codec-cropped'/f'{oldrole}.png','inputs/selected-'+role+'.png'))
    copies.append(copy(C/'raw-full'/f'{oldrole}.png','raw-full/'+role+'.png'))
bb=clean.getbbox();crop=[min(oldcrop[0],bb[0]),min(oldcrop[1],bb[1]),max(oldcrop[2],bb[2]),max(oldcrop[3],bb[3])]
pivot=[105-crop[0],150-crop[1]];canvas=[crop[2]-crop[0],crop[3]-crop[1]]
frames=[];proof={};(P/'frames').mkdir(exist_ok=True)
for role in ['neutral','blink','look']:
    im=full[role];cut=im.crop(crop);back=Image.new('RGBA',(192,192));back.paste(cut,crop[:2]);assert back.tobytes()==im.tobytes()
    dest=P/'frames'/f'{role}.png'
    if role in ['neutral','look'] and crop==oldcrop:
        shutil.copyfile(P/'inputs'/f'selected-{role}.png',dest)
    else:cut.save(dest)
    proof[role]={'nonzeroCleanedRGBADiscarded':0,'fullStageRGBAUnchanged':True,
        'byteIdenticalSelectedPNG':sha(dest)==sha(P/'inputs'/f'selected-{role}.png') if role!='blink' else None}
    frames.append({'role':role,'frameId':'dove-family-'+role,'sourceFrameID':ids[role],'png':'frames/'+role+'.png',
        'PNGsha256':sha(dest),'decodedRGBAId':identity(cut),'canvas':canvas,'pivot':pivot,'density':1,'contacts':[]})
clips=[{'id':'idle','tickRate':30,'loop':True,'roles':['neutral'],'durationTicks':[90]},
    {'id':'blink','tickRate':30,'loop':False,'roles':['neutral','blink','neutral'],'durationTicks':[42,3,45]},
    {'id':'look','tickRate':30,'loop':False,'roles':['neutral','look','neutral'],'durationTicks':[60,18,12]}]
for clip in clips[1:]:
    seq=[Image.open(P/'frames'/f'{role}.png').convert('RGBA') for role in clip['roles']]
    seq[0].save(P/(clip['id']+'.apng'),save_all=True,append_images=seq[1:],duration=[t*1000/30 for t in clip['durationTicks']],disposal=1,blend=0,loop=1,optimize=False)
handoff={'kind':'source-family producer data only; not V6 envelope or commonMotion graph authority','speciesId':'mourning_dove',
    'sourceBankSHA256':sha(R/'frame-bank.json'),'newNativeCalls':0,'newDrawings':0,'existingDrawingCount':3,
    'frameOrder':['neutral','blink','look'],'frames':frames,'clips':clips,'fullWorldCanvas':[192,192],'displayStage':[192,192],
    'candidateCanvas':canvas,'density':1,'commonCrop':crop,'commonCropOrigin':crop[:2],'fullPivot':[105,150],'candidatePivot':pivot,
    'oldSelectedCrop':oldcrop,'oldSelectedPivot':oldpivot,'oldNeutralLookFullStageRGBAExact':True,
    'oldNeutralLookPNGsByteExact':crop==oldcrop,'commonCropEnlarged':crop!=oldcrop,
    'alphaOrigin':'upstream-cleanup','alphaCleanup':'alpha>=128→255, otherwiseRGBA0','paletteOrigin':'existing frozen cohort palette, no neutral/look requantization',
    'sampling':'Whole native square→192 floor((worldPixel+0.5)*nativeDimension/192); no fit/crop/paint/snap before one shared margin crop.',
    'contacts':[],'geometryReviewed':False,'supportWorld':None,'sourceFamilyAcceptance':'pending independent closed-eye/unchanged-look review',
    'fullRuntimeAdmission':'NOT_RUN','privatePins':None,'runtimeApproval':False,'liveSceneAcceptance':False}
put('family-handoff.json',handoff)
put('export-receipt.json',{'state':'EXPORTED_PENDING_BROWSER_APNG_PROOF_AND_FREEZE','exportUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'exportWallSeconds':time.perf_counter()-start,'newNativeCalls':0,'newDrawings':0,'originals':originals,'copies':copies,
    'closureNativeCanvas':list(native.size),'closureRaw192DecodedRGBAId':identity(raw),'closureAlpha128BBoxFullWorld':bb,
    'sharedCrop':crop,'candidateCanvas':canvas,'candidatePivot':pivot,'proof':proof,'paletteMapping':'Nearest squared RGB distance among sorted existing63 colors; ties lexicographic; no dither.',
    'existingPaletteColorCount':len(palette),'closureColorsSubsetOfExisting':all(v[:3] in palette for v in clean.getdata() if v[3]),
    'registeredIDsRetained':ids,'familyHandoffSHA256':sha(P/'family-handoff.json'),'fullRuntimeAdmission':'NOT_RUN'})
print(json.dumps({'canvas':canvas,'crop':crop,'pivot':pivot,'closureBBox':bb,'proof':proof,'handoffSHA256':sha(P/'family-handoff.json')}))
