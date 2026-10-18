from pathlib import Path
from PIL import Image
import hashlib,json,subprocess
P=Path(__file__).parent;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();J=lambda n:json.loads((P/n).read_text());checks=[]
def ck(n,x):assert x,n;checks.append(n)
m=J('PRIMARY-SOURCE-MANIFEST.json');w=J('frame-to-action-map.json');v=J('texture-review-manifest.json');prep=J('prepared-native-arguments.json');args=J('native-call-arguments.json');dispatch=J('call-dispatch-receipt.json');ret=J('native-return-receipt.json')
ck('one native edit one closure one reuse no newneutral/look',m['nativeCalls']==1 and len(m['frames'])==len(m['reusedFrames'])==1 and m['newNeutralDrawings']==m['newLookDrawings']==0)
ck('prompt literal exact prepared submitted and dispatchguard',args['arguments']==prep['arguments'] and args['arguments']['prompt'].encode()==(P/'prompt.txt').read_bytes() and sha(P/'prompt.txt')==m['promptSHA256']==dispatch['promptSHA256'] and sha(P/'prepared-native-arguments.json')==dispatch['preparedArgumentsFileSHA256'])
ck('original native retained exact toolbytes',sha(P/'original.png')==m['originalSHA256']==ret['originalSHA256'] and (P/'original.png').read_bytes()==(P/'closed-native.png').read_bytes()==Path(ret['toolSavedPath']).read_bytes())
rows=m['reusedFrames']+m['frames'];ims=[];at=Image.open(P/'blink-atlas192.png')
for i,s in enumerate(rows):
 src=Image.open(P/s['sourcePNG']);out=Image.open(P/s['outputPNG']);ims.append(out);fid='frame.sha256.'+hashlib.sha256(f'RGBA8;{src.width}x{src.height};'.encode()+src.tobytes()).hexdigest()
 ck(s['pose']+' primaryRGBA and PNGhash',src.mode==out.mode=='RGBA' and s['sourceFrameId']==fid and sha(P/s['sourcePNG'])==s['sourcePNGsha256'])
 ck(s['pose']+' fullcanvas192NN exactatlas PNGhash',out.size==(192,192) and src.resize((192,192),Image.Resampling.NEAREST).tobytes()==out.tobytes()==at.crop((192*i,0,192*(i+1),192)).tobytes() and sha(P/s['outputPNG'])==s['outputPNGsha256'])
 srow=w['sourceToRenderFrames'][i];f=v['frames'][i]
 ck(s['pose']+' source-render map geometry contacts',srow['primarySourceFrameId']==s['sourceFrameId'] and srow['primarySourcePNGsha256']==s['sourcePNGsha256'] and srow['outputPNGsha256']==s['outputPNGsha256'] and srow['renderFrameId']==f['id'] and srow['atlasRect']==f['sourceRect'] and f['world']=={'width':140.8,'height':140.8} and f['sourcePixelsPerWorldUnit']==15/11 and f['pivot']=={'x':114,'y':150} and all(out.getpixel((c['x'],c['y']))[3]>0 for c in f['contacts']))
ck('wrapper explicit atlas and profile hashes',sha(P/w['atlasBinding']['file'])==w['atlasBinding']['sha256']==v['source']['sha256'] and sha(P/w['manifest']['file'])==w['manifest']['sha256'])
origin=P.parents[1]/'new-species/sd20-woodpecker-warbler-oriole-v1/hooded_oriole';ck('exact currentawake1024 and192 unchanged upstream',(P/'reused-awake-source1024.png').read_bytes()==(origin/'neutral-source1024.png').read_bytes() and (P/'reused-awake192.png').read_bytes()==(origin/'neutral192.png').read_bytes())
ck('ownidle oldfirstneutralhold60 separateblink60/3/27',v['clips']==w['clips'] and v['clips'][0]['frames']==[{'frameId':v['frames'][0]['id'],'durationTicks':60}] and v['clips'][1]['id']=='blink' and [x['durationTicks'] for x in v['clips'][1]['frames']]==[60,3,27] and w['renderClipId']=='blink')
for file,size in [('blink-preview.apng',192),('blink-yard141.apng',141)]:
 im=Image.open(P/file);ck(file+' threeframes loopingcanvas',im.size==(size,size) and im.n_frames==3 and im.info['loop']==0)
 for i,target in enumerate([ims[0],ims[1],ims[0]]):
  im.seek(i);assert im.convert('RGBA').tobytes()==target.resize((size,size),Image.Resampling.NEAREST).tobytes() and im.info['duration']==[2000,100,900][i]
 ck(file+' exactRGBA and authoredtiming',True)
node="const assert=require('node:assert/strict'),{frameAt}=require('./player.js'),p=require('./texture-review-manifest.json');const[a,b]=p.frames;for(const[t,id]of [[0,a.id],[1999,a.id],[2000,b.id],[2099,b.id],[2100,a.id],[2999,a.id],[3000,a.id],[9000,a.id]])assert.equal(frameAt(p,'blink',t,true).frame.id,id);assert.equal(frameAt(p,'blink',3000,true).terminal,true);for(const t of[0,2000,99999])assert.equal(frameAt(p,'idle',t).frame.id,a.id);for(const t of[-1,NaN,Infinity])assert.throws(()=>frameAt(p,'blink',t));console.log('8blinkboundaries/3idle/3invalidtime/terminalholdPASS')"
r=subprocess.run(['node','-e',node],cwd=P,text=True,capture_output=True,check=True);ck('actualplayer clockboundaries oncehold idle invalidtimes',r.stdout.startswith('8blink'))
ck('sourceheld no appadmission or supportapproval',m['sourceStatus'].startswith('HELD') and not w['packetBindingReady'] and not w['appBound'] and v['approval']=='unreviewed' and v['activation']=='none')
receipt={'status':'PASS technical source/export/player invariants; sourceusefulnessHELDpendingindependentreview','checks':checks,'sourceCheckCount':len(checks),'newDrawings':1,'newNeutral':0,'newLook':0,'reusedAwake':1,'nativeCalls':1,'nodeClockChecks':r.stdout.strip(),'canonicalZodValidation':'NOT_RUN','canonicalSharpAdmission':'NOT_RUN','currentMacNamedBlinkContract':'UNKNOWN','appBound':False,'geometryReviewed':False,'supportWorld':None,'sourcePixelsRepainted':False};(P/'verification.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({k:v for k,v in receipt.items() if k!='checks'}))
