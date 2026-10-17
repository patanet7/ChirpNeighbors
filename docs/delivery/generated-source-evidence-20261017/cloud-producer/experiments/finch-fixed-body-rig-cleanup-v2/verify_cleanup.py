from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,jsonschema
P=Path(__file__).parent;sha=lambda b:hashlib.sha256(b).hexdigest();m=json.loads((P/'manifest.json').read_text());a=np.array(Image.open(P/'source-neutral.png').convert('RGBA'));assert sha((P/'source-neutral.png').read_bytes())==m['sourceOriginal']['sha256'];sourceColors=set(map(bytes,a[a[:,:,3]>0]));checks=['original neutralPNG preserved'];exports=[]
for i,e in enumerate(m['frames']):
 b=np.array(Image.open(P/e['file']).convert('RGBA'));assert b.shape==a.shape and sha((P/e['file']).read_bytes())==e['sha256'];assert np.array_equal(a[600:],b[600:]);assert set(map(bytes,b[b[:,:,3]>0]))<=sourceColors
 for x,y in [(483,792),(535,800)]:assert np.array_equal(a[y-8:y+2,x-8:x+8],b[y-8:y+2,x-8:x+8])
 if e['angleRadians']==0:assert np.array_equal(a,b)
 exports.append(np.array(Image.open(P/f'export96/{i:02}.png').convert('RGBA')))
checks+=['all5 fixed body/feet RGBA regions and foot neighborhoods exact, same strict gate','native visibleRGBA tuples all from original source; neutral phases0/2/4 exact']
under=np.array(Image.open(P/'neck-underpaint-layer.png').convert('RGBA'));mask=np.array(Image.open(P/'neck-underpaint-mask.png').convert('L'))>0;assert not mask[600:].any();assert np.array_equal(under[mask],a[mask]);assert np.all(under[~mask]==0);checks+=['explicit underpaint mask clones same sourceXY only and never touches protected region']
bad=a.copy();bad[790:800,480:490,0]^=1;assert np.any(a[600:]!=bad[600:],axis=2).sum()==100;checks+=['unchanged negative control catches100 modified protectedpixels']
stage=json.loads((P/'export96/image-stage-sequence.json').read_text());schema=json.loads((P/'contract-snapshot/image-stage-sequence-v1.schema.json').read_text());jsonschema.validate(stage,schema);assert len(stage['frames'])*96*96==46080 and stage['modelSlot']=='unconfigured' and not stage['fixture']
# Additional cross-field refinements from retained Zod, beyond exported JSON schema.
for i,f in enumerate(stage['frames']):
 b=exports[i];assert f['timestampUs']==i*160000 and f['durationUs']==160000;rb=bytes(f['sourceRgba']);ab=bytes(f['matte']['alpha']);rgb=bytes(f['foreground']['rgb']);assert len(rb)==96*96*4 and rb==b.tobytes();assert len(ab)==96*96 and ab==b[:,:,3].tobytes();assert len(rgb)==96*96*3 and rgb==b[:,:,:3].tobytes();assert sha(rb)==f['sourceSha256'] and sha(ab)==f['matte']['sha256'] and sha(rgb)==f['foreground']['sha256'];assert all(0<=p['x']<=96 and 0<=p['y']<=96 for p in f['contacts']+[f['anchor']]);assert len({p['kind'] for p in f['contacts']})==len(f['contacts']);assert f['matte']['origin']=='supplied-matte' and f['foreground']['recovery']=='supplied-recovered';assert set(np.unique(b[:,:,3]))<={0,255};assert len(np.unique(b[b[:,:,3]>0,:3],axis=0))<=63
checks+=['canonical UI-main JSONschema plus cross-field hashes/dimensions/timing/origin refinements pass','96px fivephase review export has binaryalpha shared<=63visiblecolors and46080decodedpixels']
sourceY=np.floor((np.arange(96)+.5)*1024/96).astype(int);protected=sourceY>=600
assert protected[56] and all(np.array_equal(b[protected],exports[0][protected]) for b in exports);checks+=['uniform lossily derived protected region is also identical across all5 export phases']
review=json.loads((P/'occlusion-review.json').read_text());assert [x['afterNeckRegionUncoveredPixels'] for x in review['allFivePhases']]==[0,144,0,0,0];assert review['remainingOwnerReview']['accepted'] is False;checks+=['remaining phase1 jaw defect144pixels retained without changing test region or claiming approval']
for n in ['preview.gif','preview.apng']:
 with Image.open(P/n) as im:
  assert im.n_frames==5
  for i in range(5):im.seek(i);im.load();assert im.info['duration']==160
checks+=['five160ms APNG/GIF diagnostic phases decode']
meta=json.loads((P/'export-metadata.json').read_text());assert meta['runtimeManifest'] is None and not meta['artAccepted'] and not meta['integrated'] and not meta['originalPalettePreserved'];checks+=['lossy review export kept separate from production rights/art/scale/timing admission']
out={'passed':True,'checksPassed':len(checks),'checks':checks,'sourceOriginalUnchanged':True,'protectedChangedPixels':0,'newGeneratedDrawings':0,'riggedDerivedPhases':5,'ownerArtReviewPending':True,'remainingJawGapPixelsPhase1':144,'runtimeAdmitted':False,'jsonSchemaChecked':'canonical UI2e2f724f image-stage-sequence-v1','fullMacZodAndPlaybackRun':False};(P/'verification.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
