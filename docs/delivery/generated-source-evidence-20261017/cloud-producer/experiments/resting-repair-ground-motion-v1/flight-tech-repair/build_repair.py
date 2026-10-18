from pathlib import Path
from PIL import Image,ImageDraw
from fractions import Fraction
import json,hashlib,shutil,struct,zlib,math,time
R=Path('/workspace/asset-production');P=Path(__file__).resolve().parent;B=P.parent/'flight-art'
assert not (P/'export-receipt.json').exists(),'One deterministic export only.'
start=time.perf_counter()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def put(n,v):p=P/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2)+'\n')
def fid(im):return 'frame.sha256.'+hashlib.sha256(f'RGBA8;{im.width}x{im.height};'.encode()+im.tobytes()).hexdigest()
def copy(src,rel):
    dst=P/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst);assert sha(src)==sha(dst);return {'file':rel,'SHA256':sha(dst),'upstream':str(src.relative_to(R))}
def guard():
    g=json.loads((B/'STABLE-GO.json').read_text());l=json.loads((B/'review-target-hashes.json').read_text());assert len(l)==52 and sha(B/'review-target-hashes.json')==g['ledgerSHA256']
    for n,h in l.items():assert sha(B/n)==h
    return {'frozenInputs':52,'ledgerSHA256':g['ledgerSHA256'],'allExact':True}
put('baseline-guard-before.json',guard())
proposal=json.loads((B/'flight-source-proposal.json').read_text());frames={f['id']:f for f in proposal['frames']}
copies=[copy(B/'flight-source-proposal.json','baseline-flight-source-proposal.json'),copy(B/'PRIMARY-SOURCE-MANIFEST.json','baseline-PRIMARY-SOURCE-MANIFEST.json'),copy(P.parent/'FLIGHT-TECHNICAL-ADDENDUM.json','FLIGHT-TECHNICAL-ADDENDUM.json')]
for f in frames.values():
    assert sha(B/f['outputPNG'])==f['outputPNGsha256'];assert fid(Image.open(B/f['outputPNG']).convert('RGBA'))==f['outputDecodedRGBAId'];copy(B/f['outputPNG'],'baseline96/'+Path(f['outputPNG']).name)
ids=['anna-hover-up-96','anna-hover-mid-downstroke-96','anna-hover-down-96','anna-hover-mid-recovery-96']
raw={};mapping=[]
for id in ids:
    f=frames[id];im=Image.open(B/f['outputPNG']).convert('RGBA');assert im.size==(96,96)
    copy(B/f['outputPNG'],'raw96/'+id+'.png');native=R/f['primarySourcePNG'];assert sha(native)==f['primarySourcePNGsha256'] and fid(Image.open(native).convert('RGBA'))==f['primarySourceFrameId'];nativeCopy=copy(native,'native-sources/'+id+'.png')
    out=Image.new('RGBA',(64,64));out.putdata([im.getpixel((((2*x+1)*96)//128,((2*y+1)*96)//128)) for y in range(64) for x in range(64)]);(P/'raw64').mkdir(exist_ok=True);out.save(P/'raw64'/f'{id}.png');raw[id]=out
    mapping.append({'id':id.replace('-96','-64'),'sourceFrameID':f['primarySourceFrameId'],'newDrawing':False,'original96PNG':'raw96/'+id+'.png','original96PNGsha256':f['outputPNGsha256'],'nativeSource':nativeCopy,'raw64PNG':'raw64/'+id+'.png','raw64PNGsha256':sha(P/'raw64'/f'{id}.png'),'raw64RGBAId':fid(out),'originalPivot96':f['pivot'],'continuousWorldPivot':[p/1.5 for p in f['pivot']],'proposedIntegerPivot64':[36,45]})
sample=Image.new('RGB',(sum(sum(p[3]>=128 for p in im.getdata()) for im in raw.values()),1));sample.putdata([p[:3] for im in raw.values() for p in im.getdata() if p[3]>=128]);palette=sample.quantize(colors=63,method=Image.Quantize.MEDIANCUT,dither=Image.Dither.NONE);codec={};colors=set()
for id,im in raw.items():
    rgb=im.convert('RGB').quantize(palette=palette,dither=Image.Dither.NONE).convert('RGB');o=Image.new('RGBA',(64,64));o.putdata([(*rgb.getpixel((x,y)),255) if im.getpixel((x,y))[3]>=128 else (0,0,0,0) for y in range(64) for x in range(64)]);(P/'frames64').mkdir(exist_ok=True);o.save(P/'frames64'/f'{id.replace("-96","-64")}.png');codec[id]=o;colors.update(p[:3] for p in o.getdata() if p[3]);m=next(x for x in mapping if x['id']==id.replace('-96','-64'));m.update({'png':'frames64/'+id.replace('-96','-64')+'.png','PNGsha256':sha(P/'frames64'/f'{id.replace("-96","-64")}.png'),'decodedRGBAId':fid(o),'canvas':[64,64],'pivot':[36,45],'density':1,'contacts':[],'opaqueBBox':o.getchannel('A').getbbox(),'pivotRGBA':list(o.getpixel((36,45)))})
put('fixed-palette.json',{'opaqueRGB':sorted(colors),'opaqueColors':len(colors),'transparentRGBA':[0,0,0,0],'alphaThreshold':128,'quantization':'One pooled63opaque MEDIANCUT palette, no dithering, only the4 A-wing source frames.','paletteTrials':1})

# Explicit APNG writer retains every authored hold, including identical consecutive frames.
def chunk(kind,data):return struct.pack('>I',len(data))+kind+data+struct.pack('>I',zlib.crc32(kind+data)&0xffffffff)
def encode_apng(path,seq):
    w,h=seq[0].size;buf=b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',w,h,8,6,0,0,0))+chunk(b'acTL',struct.pack('>II',len(seq),1));number=0
    for i,im in enumerate(seq):
        assert im.mode=='RGBA' and im.size==(w,h);buf+=chunk(b'fcTL',struct.pack('>IIIIIHHBB',number,w,h,0,0,1,30,0,0));number+=1;rgba=im.tobytes();scan=b''.join(b'\0'+rgba[y*w*4:(y+1)*w*4] for y in range(h));compressed=zlib.compress(scan,9)
        if i==0:buf+=chunk(b'IDAT',compressed)
        else:buf+=chunk(b'fdAT',struct.pack('>I',number)+compressed);number+=1
    buf+=chunk(b'IEND',b'');path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(buf)
def controls(path):
    data=path.read_bytes();pos=8;out=[]
    while pos<len(data):
        n=struct.unpack('>I',data[pos:pos+4])[0];kind=data[pos+4:pos+8];v=data[pos+8:pos+8+n];assert zlib.crc32(kind+v)&0xffffffff==struct.unpack('>I',data[pos+8+n:pos+12+n])[0];pos+=n+12
        if kind==b'fcTL':
            x=struct.unpack('>IIIIIHHBB',v);out.append({'sequence':x[0],'width':x[1],'height':x[2],'offset':[x[3],x[4]],'delayNumerator':x[5],'delayDenominator':x[6] or 100,'dispose':x[7],'blend':x[8]})
    return out
hover=proposal['clips'][0];wingseq=[codec[ids[t%4]] for t in range(hover['durationTicks'])];encode_apng(P/'airborne-four-pose-cycle.apng',wingseq)
timings=[]
for clip in proposal['clips']:
    old=B/(clip['id']+'.apng');copy(old,'original-previews/'+old.name);seq=[];timeline=[]
    for t in range(clip['durationTicks']):
        s=next(s for s in clip['segments'] if s['ticks'][0]<=t<s['ticks'][1]);f=frames[s['frameId']];a,b=s['ticks'];u=(t-a)/(b-a);root=[s['rootFrom'][j]+u*(s['rootTo'][j]-s['rootFrom'][j]) for j in range(2)];im96=Image.open(B/f['outputPNG']).convert('RGBA');im=Image.new('RGBA',(64,64));im.putdata([im96.getpixel((((2*x+1)*96)//128,((2*y+1)*96)//128)) for y in range(64) for x in range(64)])
        stage=Image.new('RGBA',(360,170),(238,233,221,255));dr=ImageDraw.Draw(stage);dr.line((0,130,360,130),fill='#a69d8b');dr.text((5,5),clip['id'],fill='black')
        for off,bg in [(0,None),(180,'#24313c')]:
            if bg:dr.rectangle((180,20,359,169),fill=bg);dr.line((180,130,359,130),fill='#858e91')
            xy=(round(root[0]-f['pivot'][0]/1.5)+off,round(root[1]-f['pivot'][1]/1.5));stage.alpha_composite(im,xy)
        seq.append(stage);timeline.append({'tick':t,'sourceFrameId':f['id'],'primarySourceFrameId':f['primarySourceFrameId'],'authoredRoot':root,'stageRGBAsha256':hashlib.sha256(stage.tobytes()).hexdigest()})
    runs=[]
    for q in timeline:
        if runs and runs[-1]['RGBAsha256']==q['stageRGBAsha256']:runs[-1]['ticks']+=1
        else:runs.append({'RGBAsha256':q['stageRGBAsha256'],'ticks':1})
    oldim=Image.open(old);oldDecoded=[]
    for i in range(oldim.n_frames):oldim.seek(i);oldDecoded.append(hashlib.sha256(oldim.convert('RGBA').tobytes()).hexdigest())
    assert oldDecoded==[x['RGBAsha256'] for x in runs],(clip['id'],'Baseline actual pixels differ from unchanged source composition')
    out=P/'corrected-previews'/(clip['id']+'.apng');encode_apng(out,seq);ctl=controls(out);newim=Image.open(out);assert len(ctl)==len(seq)==newim.n_frames
    for i,im in enumerate(seq):newim.seek(i);assert newim.convert('RGBA').tobytes()==im.tobytes();assert ctl[i]['delayNumerator']==1 and ctl[i]['delayDenominator']==30
    oldctl=controls(old);oldsum=sum((Fraction(x['delayNumerator'],x['delayDenominator']) for x in oldctl),Fraction());newsum=sum((Fraction(x['delayNumerator'],x['delayDenominator']) for x in ctl),Fraction());assert newsum==Fraction(clip['durationTicks'],30)
    timings.append({'clip':clip['id'],'sourceStatusUnchanged':clip['status'],'originalAPNG':'original-previews/'+old.name,'originalPNGsha256':sha(old),'originalfcTLFrames':len(oldctl),'originalDurationFraction':str(oldsum),'originalSeconds':float(oldsum),'authoredTicks':clip['durationTicks'],'authoredSecondsFraction':str(Fraction(clip['durationTicks'],30)),'expectedUniqueConsecutiveSourceRuns':runs,'originalDecodedFramesMatchUnchangedAuthoredRunPixels':True,'oldAggregateTimingCorrect':oldsum==Fraction(clip['durationTicks'],30),'correctedAPNG':str(out.relative_to(P)),'correctedPNGsha256':sha(out),'correctedfcTLFrames':len(ctl),'correctedDurationFraction':str(newsum),'everyEncodedFrameDelay':[1,30],'exactAuthoredRGBAEveryTick':True,'authoredTimeline':timeline,'pixelsOrSourceClocksChanged':False,'qualification':'Corrected preview timing only; terminal joins and cross-pack/source limits remain held.'})
put('apng-timing-proof.json',{'encoder':'Explicit fullRGBA PNG/APNG chunks, one fcTL per authored tick, no frame coalescing; SOURCE blend and no disposal. CRCs parsed and verified; decoded PillowRGBA checked.','sourceFramesAndClocksUnchanged':True,'correctedPreviews':timings,'oldFailureCause':'Consecutive identical rendered poses were coalesced while scalar frame duration was not accumulated; preserved original holds were lost. Old hover total already0.8s, per-frame delays had millisecond rounding.','nativeCalls':0,'newDrawings':0})
handoff={'kind':'Existing4-key airborne derivative only; not full flight or common idle/blink/look input5','speciesId':'anna_s_hummingbird','nativeCalls':0,'newDrawings':0,'reusedNativeSourceIDs':4,'frames':mapping,'canvas':[64,64],'world':[64,64],'density':1,'source96Density':1.5,'commonCrop':[0,0,64,64],'originShift':[0,0],'continuousSourcePivotWorld':[36,68/1.5],'proposedIntegerPivot':[36,45],'pivotRoundingDeltaWorld':[0,45-68/1.5],'pivotMeaning':'Common airborne torso image-registration origin, not foot support. No body pixel moved to round pivot.','contacts':[],'supportState':'airborne source artwork','geometryReviewed':False,'supportWorld':None,'alphaOrigin':'upstream-cleanup','alphaRule':'alpha>=128→255; otherwiseRGBA0; common63opaque+transparent, no dither','sampler':'floor((x+.5)*96/64), same fullcanvas transform for all4; no crop/fit/paint/warp/offset','clip':{'id':'existing-airborne-four-pose-study','tickRate':30,'durationTicks':24,'poseOrder':[x['id'] for x in mapping],'frames':[mapping[t%4]['id'] for t in range(24)],'durationTicksPerFrame':1,'loop':False,'rootTravel':[0,0],'wingClockSeparateFromBodyPath':True,'physicalWingbeatClaim':False},'playableAPNG':'airborne-four-pose-cycle.apng','correctedBaselinePreviews':'apng-timing-proof.json','full13FrameFlightAdmission':False,'takeoffLandingJoinStatus':'HELD, unchanged; new bridge drawings are outside this packet','rightsGranted':False,'sourceAdmitted':False,'currentPixelJSONValidation':'Corvid-owned after freeze','runtimeAdmission':False}
put('airborne-source-handoff.json',handoff);put('PRIMARY-SOURCE-MANIFEST.json',{'batchId':'anna-four-airborne64-technical-derivative','nativeCalls':0,'newDrawings':0,'frames':[],'reusedFrames':mapping,'sourceStatus':'Derivative source appearance/geometry and current technical review pending. Existing useful4key study does not certify biological smooth hover or full flight.','corrected13SourcePreviewsAreNewDrawings':False})
put('baseline-guard-after.json',guard())
put('export-receipt.json',{'state':'ONE_EXPORT_COMPLETE_PENDING_BROWSER_AND_FREEZE','wallSeconds':time.perf_counter()-start,'nativeCalls':0,'newDrawings':0,'fourFrameArea':4*64*64,'paletteTrials':1,'wholeCanvasTransform':[96,96,64,64],'baseline52Unchanged':True,'pixelSource96Exact':True,'nativeIDsAndSourcesPreserved':True,'noPerPoseFitCropShift':True,'correctedAPNGCount':4,'copies':copies,'readOnlyPreflightHarnessError':'Initial timing parser snippet had a Python or100 spacing SyntaxError before execution; corrected read-only parse, no image call/export/output existed from failed snippet.'})
print(json.dumps({'nativeCalls':0,'newDrawings':0,'frames':4,'area':16384,'pivot':[36,45],'correctedClips':[{'id':x['clip'],'old':x['originalDurationFraction'],'new':x['correctedDurationFraction']} for x in timings],'baseline52Unchanged':True,'handoffSHA256':sha(P/'airborne-source-handoff.json')}))
