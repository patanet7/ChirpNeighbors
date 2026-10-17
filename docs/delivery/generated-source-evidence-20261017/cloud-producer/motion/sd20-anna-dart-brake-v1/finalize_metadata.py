from pathlib import Path
from PIL import Image
import json,hashlib,shutil
P=Path(__file__).parent;ROOT=Path('/workspace/asset-production');A=ROOT/'motion/sd20-anna-hover-cycle-v2';OLD=ROOT/'motion/sd20-anna-actions-v1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rid(im):return 'frame.sha256.'+hashlib.sha256(f'RGBA8;{im.width}x{im.height};'.encode()+im.tobytes()).hexdigest()
def write(n,o):(P/n).write_text(json.dumps(o,indent=2)+'\n')
m=json.load(open(P/'PRIMARY-SOURCE-MANIFEST.json'));originalHashes={f['sourcePNG']:sha(P/f['sourcePNG']) for f in m['frames']+m['reusedFrames']};originalHashes.update({f['outputPNG']:sha(P/f['outputPNG']) for f in m['frames']+m['reusedFrames']})
package=json.load(open(P/'reused/a-primary-source-manifest.json'));lookup={f['sourceFrameId']:f for f in package['frames']+package['reusedFrames']}
for f in m['reusedFrames']:
 old=f['sourceFrameId'] in {x['sourceFrameId'] for x in package['reusedFrames']};origin=OLD if old else A
 f.pop('originPrimaryManifest',None);f.pop('originOriginalSHA256',None);f.pop('originPromptSHA256',None)
 f['referencePackagePrimaryManifest']='motion/sd20-anna-hover-cycle-v2/PRIMARY-SOURCE-MANIFEST.json';f['referencePackageOriginalSHA256']=package['originalSHA256'];f['originPrimaryManifestLocal']='reused/a-primary-source-manifest.json';f['originPrimaryManifestLocalSHA256']=sha(P/'reused/a-primary-source-manifest.json')
 f['sourceOrigin']={'original':str((origin/'original.png').relative_to(ROOT)),'originalSHA256':sha(origin/'original.png'),'prompt':str((origin/'prompt.txt').relative_to(ROOT)),'promptSHA256':sha(origin/'prompt.txt'),'sourceGenerationBatch':origin.name,'referencePackageIsNotNecessarilyGenerator':True}
 reg=dict(lookup[f['sourceFrameId']]['registration']);reg['sharedCalibrationFile']=None if old else 'reused/a-whole-call-calibration.json';reg['sharedCalibrationSHA256']=None if old else sha(P/'reused/a-whole-call-calibration.json');reg['perPoseFit']=False;reg['paintOrWarp']=False;f['registration']=reg
write('PRIMARY-SOURCE-MANIFEST.json',m)
rights=json.load(open(P/'reference-rights-provenance.json'));(P/'references').mkdir(exist_ok=True)
for i,r in enumerate(rights['references']):
 source=Path(r['path']);source=source if source.is_absolute() else ROOT/source;assert sha(source)==r['sha256'],'Conditioned reference changed since actual call'
 local=f'references/conditioning-{i:02d}.png';shutil.copyfile(source,P/local);r['retainedLocalPNG']=local;r['actualInputDecodedRGBAId']=rid(Image.open(source).convert('RGBA'));r['primaryLineageSourceFrameId']=rights['generatedReferenceSourceIDs'][i];r['inputIsDerivativeOfPrimary']=r['actualInputDecodedRGBAId']!=r['primaryLineageSourceFrameId'];r['path']=str(source.relative_to(ROOT))
 if i==2:r['derivativeLineage']={'nativePrimaryPNG':'motion/sd20-anna-hover-cycle-v2/mid-downstroke-native.png','nativePrimaryCanvas':[887,887],'conditionedDerivativeCanvas':[1024,1024],'calibrationLocal':'reused/a-whole-call-calibration.json','calibrationSHA256':sha(P/'reused/a-whole-call-calibration.json'),'note':'Conditioned bytes are registered1024derivative, not identical to887native primary.'}
write('reference-rights-provenance.json',rights)
t=json.load(open(P/'body-trajectory.json'));t['segments'][-1]['ticks'][1]=90;t.update(durationTicks=90,totalTicks=90,lastSampleTick=89,frameCount=90,sampleTickConvention='frame-starts',segmentTickConvention='half-open',supports=[],rootPathGeneratesNewDrawings=False,segmentIntervalConvention='half-open[start,end); samples at frame starts0..89; endTick89 is last sample, not duration');write('body-trajectory.json',t)
mapping=json.load(open(P/'frame-to-action-map.json'));mapping['trajectory']['sha256']=sha(P/'body-trajectory.json');write('frame-to-action-map.json',mapping)
assert all(sha(P/n)==h for n,h in originalHashes.items())
write('receipts/pre-freeze-metadata-fix.json',{'sourceAndOutputPixelsUnchanged':True,'hashes':originalHashes,'corrections':['Distinguished A reference-package metadata from actual old hover generator original/prompt provenance.','Copied local A primary/calibration lineage; actual registered1024conditioning bytes get their own decodedID separate from887native primary.','Added explicit90tick duration/end89, airborne supports[] and rootPathGeneratesNewDrawings=false; all pose/path sample values unchanged.'],'newNativeCalls':0,'newDrawings':0})
print(json.dumps({'primarySHA256':sha(P/'PRIMARY-SOURCE-MANIFEST.json'),'mapSHA256':sha(P/'frame-to-action-map.json'),'trajectorySHA256':sha(P/'body-trajectory.json'),'allPixelsUnchanged':True,'conditionedDerivativeRGBAId':rights['references'][2]['actualInputDecodedRGBAId']},indent=2))
