from pathlib import Path
from PIL import Image,ImageDraw
from datetime import datetime,timezone
import json,hashlib,time,struct,zlib,binascii
P=Path(__file__).resolve().parent;assert not(P/'export-receipt.json').exists(),'Onechosenexport,no retry'
start=time.perf_counter()
def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()
def rid(im):return 'frame.sha256.'+hashlib.sha256(('RGBA8;%dx%d;'%im.size).encode()+im.tobytes()).hexdigest()
def save(n,d):(P/n).write_text(json.dumps(d,indent=2)+'\n')
def nn(im):
 assert im.size==(1254,1254);src=im.tobytes();out=bytearray(192*192*4);ix=[((2*x+1)*1254)//384 for x in range(192)]
 for y,sy in enumerate(ix):
  for x,sx in enumerate(ix):out[(y*192+x)*4:(y*192+x+1)*4]=src[(sy*1254+sx)*4:(sy*1254+sx+1)*4]
 return Image.frombytes('RGBA',(192,192),bytes(out)),ix
orig=Image.open(P/'original.png').convert('RGBA');ref=Image.open(P/'reference-held-perch-native1254.png').convert('RGBA');new,ix=nn(orig);old,_=nn(ref);new.save(P/'grip-study192.png');old.save(P/'reference-commonNN192.png')
assert sha(P/'reference-held-perch-native1254.png')=='505dcd1f738740110b24b27e7f54e5a799a0d921f2903b6d1e4f0374e1463d5a'
metrics={}
for name,im in [('held-reference-commonNN',old),('new-grip-study',new)]:
 alpha=im.getchannel('A');b=alpha.point(lambda a:255 if a>=128 else 0).getbbox()
 metrics[name]={'alpha128BBoxOutput':list(b),'alpha128WidthWorld':(b[2]-b[0])/(157/152),'lowestOpaqueRowWorld':(b[3]-1)/(157/152),'partialAlphaPixels':sum(0<a<255 for a in alpha.getdata()),'alphaValues':sorted(set(alpha.getdata())),'oldAnkleFootProbeSamples':{str(q):list(im.getpixel(q)) for q in [(108,147),(100,151),(113,154),(112,158),(126,147),(119,151),(131,154),(128,157)]},'probeMeaning':'Inheritedimagepixels only, not anatomicalhallux/contact/supportcertification'}
bodyroi=(0,0,192,138);footroi=(93,138,141,164);bodychange=sum(old.getpixel((x,y))!=new.getpixel((x,y)) for y in range(138) for x in range(192));footalpha=sum(old.getpixel((x,y))[3]>=128 !=(new.getpixel((x,y))[3]>=128) for y in range(138,164) for x in range(93,141))
save('source-measurements.json',{'comparisonSampler':'Samewhole1254floorcenterNN→192bothreference/new. OldhistoricalPIL192exportalso retainedbyteexact inancestry; notrewritten','perFrame':metrics,'upperBodyRGBAChangedPixelsROI0_0_192_138':bodychange,'bodyEqualityMeaning':'No automaticbodypixel-equalityacceptancegate; shapes/identity reviewednormal. No pixelrepairs applied.','footRegion':list(footroi),'footAlphaDiagnosticExpression':'Masks/landmarksdiagnosticonly; no pressureplane inferred','fullWorld':[185.88535031847132]*2,'density':157/152,'pivot':[111,150],'contacts':[],'supportWorld':None,'geometryReviewed':False,'currentMacSupportGeometry':'UNKNOWN','supportFit':'UNVERIFIED'})
# Actual source-native feet and direct192samples, with coordinates for later semantic inspection.
feet=Image.new('RGB',(960,640),'#e5e0cd');d=ImageDraw.Draw(feet)
for i,(label,im) in enumerate([('Held native feet',ref),('New native feet',orig)]):
 crop=im.crop((610,885,930,1065));feet.paste(crop,(i*480+20,30),crop);d.text((i*480+20,6),label+' — source x610..929,y885..1064',fill='black')
 for j,(lab,out) in enumerate([(label+' output',old if i==0 else new)]):
  cr=out.crop(footroi).resize((384,208),Image.Resampling.NEAREST);feet.paste(cr,(i*480+20,280),cr);d.text((i*480+20,250),lab+' —192grid x93..140,y138..163 x8',fill='black')
feet.save(P/'feet-source-and-output-enlarged.png')
# Sourceactualfootcoordinate inspection grid, no pixel repainting in bird.
grid=Image.new('RGB',(2*530,420),'#e5e0cd');d=ImageDraw.Draw(grid)
for i,(label,im) in enumerate([('Held commonNN192',old),('New grip192',new)]):
 cr=im.crop((94,138,142,166)).resize((480,280),Image.Resampling.NEAREST);grid.paste(cr,(i*530+40,40),cr);d.text((i*530+40,8),label,fill='black')
 for y in range(138,167,2):yy=40+(y-138)*10;d.text((i*530+8,yy),str(y),fill='black');d.line((i*530+40,yy,i*530+520,yy),fill='#a08070')
 for x in range(94,143,4):d.text((i*530+40+(x-94)*10,337),str(x),fill='black')
grid.save(P/'toe-coordinate-inspection.png')
sheet=Image.new('RGB',(2*212,2*222),'#e5e0cd');d=ImageDraw.Draw(sheet)
for y,bg in enumerate(['#e5e0cd','#182a32']):
 d.rectangle((0,y*222,424,(y+1)*222),fill=bg)
 for x,(label,im) in enumerate([('HELDreference',old),('Newstaticgripstudy',new)]):sheet.paste(im,(x*212+10,y*222+25),im);d.text((x*212+5,y*222+5),label,fill='black' if not y else 'white')
sheet.save(P/'normal-old-new-light-dark192.png')
# One static192RGBA frame with exact3second authoredhold, not a perchinganimation.
def chunk(t,b):return struct.pack('>I',len(b))+t+b+struct.pack('>I',binascii.crc32(t+b)&0xffffffff)
raw=new.tobytes();packed=zlib.compress(b''.join(b'\0'+raw[y*192*4:(y+1)*192*4] for y in range(192)),9)
data=b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',192,192,8,6,0,0,0))+chunk(b'acTL',struct.pack('>II',1,1))+chunk(b'fcTL',struct.pack('>IIIIIHHBB',0,192,192,0,0,90,30,0,0))+chunk(b'IDAT',packed)+chunk(b'IEND',b'');(P/'STATIC-grip-study.apng').write_bytes(data)
new.save(P/'STATIC-grip-study.gif',save_all=True,duration=3000,loop=0,disposal=2)
sourceid=rid(orig);referenceid=rid(ref)
save('PRIMARY-SOURCE-MANIFEST.json',{'batchId':'crow-perch-grip-art-internal-v2','nativeCalls':1,'original':'original.png','originalSHA256':sha(P/'original.png'),'prompt':'prompt.txt','promptSHA256':sha(P/'prompt.txt'),'frames':[{'sourceFrameId':sourceid,'sourcePNG':'original.png','sourcePNGsha256':sha(P/'original.png'),'speciesId':'american_crow','pose':'static-perch-grip-art-internal-candidate','registration':{'method':'Whole1254→192floorcenterNNstraightRGBA, nofit/crop/paint/snap/translation','sourceCanvas':[1254,1254],'outputCanvas':[192,192],'wholeCanvasScale':192/1254,'density':157/152,'pivot':[111,150],'contacts':[],'geometryReviewed':False,'supportWorld':None},'outputPNG':'grip-study192.png','outputPNGsha256':sha(P/'grip-study192.png'),'outputRGBAId':rid(new)}],'reusedFrames':[{'sourceFrameId':referenceid,'sourcePNG':'reference-held-perch-native1254.png','sourcePNGsha256':sha(P/'reference-held-perch-native1254.png'),'pose':'historicalHELDperchconditioningonly','newDrawing':False}],'outputMetadata':['source-handoff.json','source-measurements.json','support-unknown-snapshot.json','occlusion-proposal.json'],'sourceStatus':'PENDING_INDEPENDENT_ART_INTERNAL_TOE_REVIEW;supportfitunverified','perchingAnimationGain':0,'landingGain':0,'sourceAdmitted':False,'runtimeAdmission':False})
save('source-handoff.json',{'kind':'Artinternal Crowdigitopposition staticpose sourceproposal only','speciesId':'american_crow','nativeCalls':1,'newDrawings':1,'newStaticPoses':1,'perchingAnimationGain':0,'landingGain':0,'groundRestRework':False,'frames':[{'id':'crow-grip-static','role':'static-grip-study','png':'grip-study192.png','PNGsha256':sha(P/'grip-study192.png'),'decodedRGBAId':rid(new),'sourceFrameID':sourceid,'sourcePNG':'original.png','sourcePNGsha256':sha(P/'original.png'),'nativeCanvas':[1254,1254],'canvas':[192,192],'density':157/152,'pivot':[111,150],'contacts':[]}],'fullWorldCanvas':[185.88535031847132]*2,'displayStage':[185.88535031847132]*2,'outputCanvas':[192,192],'candidateCanvas':[192,192],'density':157/152,'candidatePivot':[111,150],'commonCrop':[0,0,192,192],'originShift':[0,0],'contacts':[],'supportWorld':None,'geometryScope':'image-registration-only','geometryReviewed':False,'physicalGripReviewed':False,'currentMacSupportGeometry':'UNKNOWN','sourceAlpha':'ExactpartialRGBAretained; no binary cleanup/palettequantization imposed','clips':[{'id':'static-perch-grip-study','tickRate':30,'frames':[{'frameId':'crow-grip-static','durationTicks':90}],'loop':False,'uniqueDrawings':1,'qualification':'Static3secondhold only, not perchingcycle/takeoff/landing'}],'sourceUsefulness':'PENDING_INDEPENDENT_TOE_ANATOMY_NORMAL_REVIEW','supportFit':'UNVERIFIED','sourceAdmitted':False,'rightsGranted':False,'runtimeAdmission':False,'activation':'none'})
save('export-receipt.json',{'exportedUTC':datetime.now(timezone.utc).isoformat(),'observedExportWallSeconds':time.perf_counter()-start,'exportPasses':1,'nativeCalls':1,'retries':0,'sourceCanvas':[1254,1254],'outputCanvas':[192,192],'wholeCanvasSampler':'floor((dst+.5)*1254/192),sameindicesbothaxes,straightRGBA','sampleIndices':ix,'sourceIndividualScalePreservedByTransform':True,'perPoseFit':False,'translation':False,'crop':False,'toePixelPainting':False,'bodyManualCorrection':False,'sourceOriginalRGBAId':sourceid,'originalSHA256':sha(P/'original.png'),'referenceOriginalSHA256':sha(P/'reference-held-perch-native1254.png'),'staticClockTicks':90,'tickRate':30,'uniqueFrames':1,'perchingAnimationGain':0,'landingGain':0,'supportFit':'UNVERIFIED','humanCleanupMinutes':None,'runtimeAdmission':False})
print(json.dumps({'sourceFrameID':sourceid,'renderPNGsha256':sha(P/'grip-study192.png'),'metrics':metrics,'bodyRGBADiff':bodychange,'singleStatic':True},indent=2))
