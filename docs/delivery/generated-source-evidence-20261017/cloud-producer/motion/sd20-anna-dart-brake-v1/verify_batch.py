from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
P=Path(__file__).parent;checks=[]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def check(n,v):
 checks.append({'name':n,'passed':bool(v)})
 if not v:raise AssertionError(n)
m=json.load(open(P/'PRIMARY-SOURCE-MANIFEST.json'));mapp=json.load(open(P/'frame-to-action-map.json'));manifest=json.load(open(P/'airborne-source-manifest.json'));trajectory=json.load(open(P/'body-trajectory.json'));cal=json.load(open(P/'whole-call-calibration.json'));args=json.load(open(P/'receipts/native-args.json'))
check('exactly one native call',m['nativeCalls']==1)
check('four new body wing drawings',len(m['frames'])==4)
check('four reused hover sources',len(m['reusedFrames'])==4)
check('exact submitted prompt bytes',args['prompt'].encode()==(P/m['prompt']).read_bytes())
check('original byte hash',sha(P/m['original'])==m['originalSHA256'])
check('prompt byte hash',sha(P/m['prompt'])==m['promptSHA256'])
atlas=Image.open(P/mapp['atlas']['file'])
check('atlas exact hash',sha(P/mapp['atlas']['file'])==mapp['atlas']['sha256'])
check('manifest exact hash',sha(P/mapp['manifest']['file'])==mapp['manifest']['sha256'])
check('trajectory exact hash',sha(P/mapp['trajectory']['file'])==mapp['trajectory']['sha256'])
ids=set();outputs={};allframes=m['frames']+m['reusedFrames']
for f,mapf in zip(allframes,mapp['sourceToRenderFrames']):
 src=Image.open(P/f['sourcePNG']).convert('RGBA');out=Image.open(P/f['outputPNG']).convert('RGBA');label=f['pose'];identity='frame.sha256.'+hashlib.sha256(f'RGBA8;{src.width}x{src.height};'.encode()+src.tobytes()).hexdigest();check(label+' primary decoded ID',identity==f['sourceFrameId']);check(label+' source byte hash',sha(P/f['sourcePNG'])==f['sourcePNGsha256']);check(label+' output byte hash',sha(P/f['outputPNG'])==f['outputPNGsha256']);check(label+' output96RGBA',out.size==(96,96));r=f['atlasRect'];check(label+' atlas pixel equality',atlas.crop((r['x'],r['y'],r['x']+96,r['y']+96)).tobytes()==out.tobytes());check(label+' wrapper matches source and render',mapf['primarySourceFrameId']==f['sourceFrameId'] and mapf['renderFrameId']==f['renderFrameId']);ids.add(identity);outputs[f['renderFrameId']]=out
 if f['newDrawing']:
  check(label+' primary1536canvas',src.size==(1536,1536));check(label+' positivealpha primary all retained',np.count_nonzero(np.array(src)[:,:,3])==f['registration']['sourceAlphaPixels']);check(label+' no opaque clipping in render window',f['renderWindowDiagnostic']['alpha128PixelsOutsideRenderWindow']==0);check(label+' only alpha1 fringe outside render',f['renderWindowDiagnostic']['maximumExcludedSourceAlpha']<=1);check(label+' no perpose scale',f['registration']['perPoseScale']==False)
check('all new and reuse IDs distinct',len(ids)==8)
original=np.array(Image.open(P/'original.png'));reconstructed=np.zeros_like(original)
for f in m['frames']:
 src=Image.open(P/f['sourcePNG']);tx,ty=f['registration']['integerSourceTranslation'];back=Image.new('RGBA',(original.shape[1],original.shape[0]));back.paste(src,(-tx,-ty));ba=np.array(back);hit=ba[:,:,3]>0
 check(f['pose']+' registered derivative exact hash',sha(P/f['registeredPNG'])==f['registeredPNGsha256'])
 check(f['pose']+' full source disjoint ownership',not np.any((reconstructed[:,:,3]>0)&hit));reconstructed[hit]=ba[hit]
check('all original positive alpha RGBA reconstructed exactly',np.array_equal(original[original[:,:,3]>0],reconstructed[original[:,:,3]>0]))
check('no original alpha omitted',np.array_equal(original[:,:,3],reconstructed[:,:,3]))
check('actual old up/down generator lineage disclosed',all(f['sourceOrigin']['originalSHA256']=='edf72eb0aa91432249c6acdd4351913163c6497c655268e9a4eed7eb38927c5e' for f in m['reusedFrames'] if f['pose'] in ['existing-hover-up','existing-hover-down']))
for f in manifest['frames']:
 check(f['id']+' density',f['sourcePixelsPerWorldUnit']==1.5 and f['world']=={'width':64,'height':64});check(f['id']+' airborne without ground contacts',f['supportState']=='airborne' and f['contacts']==[]);check(f['id']+' positivealpha body origin',outputs[f['id']].getpixel((f['pivot']['x'],f['pivot']['y']))[3]>0)
check('90 root samples at30Hz',trajectory['tickRate']==30 and len(trajectory['samples'])==90)
check('root final displacement36',trajectory['samples'][-1]['root']==[36.0,0])
check('root vertical bob absent',all(s['root'][1]==0 for s in trajectory['samples']))
check('root x monotonic short dart',all(a['root'][0]<=b['root'][0] for a,b in zip(trajectory['samples'],trajectory['samples'][1:])))
check('root initial and final holds',all(s['root']==[0.0,0] for s in trajectory['samples'][:15]) and all(s['root']==[36.0,0] for s in trajectory['samples'][51:]))
check('no silent root loop',trajectory['loop']==False and trajectory['oneShot']==True)
check('all source frame selections defined',all(z['frameId'] in outputs for c in manifest['clips'] for z in c['frames']))
check('explicit clips match root segments',all(s['poseClipId'] in {c['id'] for c in manifest['clips']} for s in trajectory['samples']))
check('no fake idle runtime profile',mapp['idleProfileClaimed']==False and mapp['canonicalSharpReceipt'] is None and mapp['runtimeBound']==False)
result={'status':'passed','checkCount':len(checks),'checks':checks,'scope':'Source byte/decoded IDs, mapping/pixel/clock/support declaration checks only; not biological flight/force or actual Mac/runtime admission.'};(P/'verification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'status':'passed','checks':len(checks)}))
