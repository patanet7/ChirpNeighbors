from pathlib import Path
from datetime import datetime, timezone
from PIL import Image
import json, hashlib, shutil, time, re

P=Path(__file__).resolve().parent
R=Path('/workspace/asset-production')
S=R/'experiments/resting-repair-ground-motion-v1/attention-repairs/white_crowned_sparrow'
started=datetime.now(timezone.utc).isoformat(); clock=time.perf_counter()
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,d): (P/n).write_text(json.dumps(d,indent=2)+'\n')
ledger=json.loads((S/'review-target-hashes.json').read_text())
for row in ledger['files']: assert sha(S/row['path'])==row['SHA256'],row['path']
assert len(ledger['files'])==45
copied=[]
for f in sorted(S.rglob('*')):
 if not f.is_file() or '__pycache__' in f.parts: continue
 rel=f.relative_to(S); output_rel=Path('historical-baseline-'+rel.name) if str(rel) in ['STABLE-GO.json','review-target-hashes.json'] else rel; dest=P/output_rel
 assert not dest.exists(),str(dest)
 dest.parent.mkdir(parents=True,exist_ok=True); shutil.copyfile(f,dest)
 assert sha(dest)==sha(f)
 copied.append({'path':str(output_rel),'upstreamPath':str(rel),'SHA256':sha(f),'bytes':f.stat().st_size})
reviews=R/'experiments/resting-repair-ground-motion-v1/reviews'
historical=[]
for rel in ['geometry/white_crowned_sparrow-attention-repair.json','geometry/white_crowned_sparrow-attention-repair.md','appearance/attention-white_crowned_sparrow.json','appearance/attention-white_crowned_sparrow.md']:
 src=reviews/rel; dst=P/'historical-reviews'/rel; dst.parent.mkdir(parents=True,exist_ok=True); shutil.copyfile(src,dst)
 historical.append({'path':str(dst.relative_to(P)),'upstream':str(src.relative_to(R)),'SHA256':sha(dst)})
h=json.loads((P/'source-handoff.json').read_text()); frame_metrics=[]; union=set()
for f in h['frames']:
 final=Image.open(P/f['png']).convert('RGBA'); raw=Image.open(P/f['rawPNG']).convert('RGBA'); native=Image.open(P/f['sourcePNG']).convert('RGBA')
 final_id='frame.sha256.'+hashlib.sha256(('RGBA8;%dx%d;'%final.size).encode()+final.tobytes()).hexdigest()
 native_id='frame.sha256.'+hashlib.sha256(('RGBA8;%dx%d;'%native.size).encode()+native.tobytes()).hexdigest()
 assert final_id==f['decodedRGBAId'] and native_id==f['sourceFrameId']
 assert sha(P/f['png'])==f['PNGsha256']
 pixels=list(final.getdata()); colors=set(pixels); union.update(colors)
 assert all(v[3] in (0,255) and (v[3] or v[:3]==(0,0,0)) for v in pixels)
 frame_metrics.append({'role':f['role'],'sourceFrameID':native_id,'sourcePNG':f['sourcePNG'],'sourcePNGsha256':sha(P/f['sourcePNG']),'sourceCanvas':list(native.size),'PNG':f['png'],'PNGsha256':sha(P/f['png']),'decodedRGBAId':final_id,'canvas':list(final.size),'rawFullPNG':f['rawPNG'],'rawFullPNGsha256':sha(P/f['rawPNG']),'rawAlphaValues':sorted(set(raw.getchannel('A').getdata())),'finalAlphaValues':sorted(set(final.getchannel('A').getdata())),'finalColorsIncludingTransparent':len(colors),'finalOpaquePixels':sum(v[3]>0 for v in pixels),'pivot':f['pivot'],'contacts':[]})
assert len(union)<=64
prompt=(P/'prompt.txt').read_bytes(); args=json.loads((P/'native-call-arguments.json').read_text())
assert args['arguments']['prompt'].encode()==prompt
dispatch=json.loads((P/'call-dispatch-receipt.json').read_text()); returned=json.loads((P/'native-return-receipt.json').read_text())
assert sha(P/'prompt.txt')==dispatch['promptSHA256']
interval=(datetime.fromisoformat(returned['completedUTC'])-datetime.fromisoformat(dispatch['dispatchedUTC'])).total_seconds()
look=next(x for x in h['clips'] if x['id']=='look'); assert [x['durationTicks'] for x in look['frames']]==[60,18,12]
palette=sorted([list(x) for x in union]); save('baseline-palette.json',{'source':'Exact union of existing final PNG RGBA values; no palette regenerated','colors':palette,'colorsIncludingTransparent':len(palette)})
save('baseline-copy-proof.json',{'copiedFileCount':len(copied),'files':copied,'frozenOriginalInputs':45,'originalLedgerSHA256':sha(S/'review-target-hashes.json'),'allOriginalFrozenInputsUnchanged':True,'copyByteIdentity':True,'exportRerun':False,'historicalReviews':historical})
save('arm-a-metrics.json',{'arm':'A','method':'existing authored native attention sprite baseline','newNativeCalls':0,'newDrawings':0,'sourcePoseEdits':0,'reexportPasses':0,'historicalAttentionNativeCalls':1,'historicalAttentionNewDrawings':1,'historicalAttentionMethod':'native reference-conditioned edit; not a rig','historicalNativeAwaitSeconds':None,'historicalHumanAuthoringMinutes':None,'historicalCleanupMinutes':None,'historicalExportWallSeconds':None,'historicalDispatchPreparedUTC':dispatch['dispatchedUTC'],'historicalReturnRecordedUTC':returned['completedUTC'],'historicalReceiptTimestampIntervalSeconds':interval,'intervalMeaning':'Receipt timestamp span only; not proven native tool latency or human effort.','historicalExportReceiptUTC':json.loads((P/'export-receipt.json').read_text())['exportedUTC'],'historicalFreezeUTC':json.loads((S/'STABLE-GO.json').read_text())['frozenUTC'],'currentPackagingStartedUTC':started,'currentPackagingWallSecondsThroughIdentityAndPaletteAudit':time.perf_counter()-clock,'currentWallMetricScope':'Measured byte-copy, hashes, source/render identity and palette audit in this script; excludes browser check and prior planning. No export performed.','frames':frame_metrics,'sharedFinalColorsIncludingTransparent':len(union),'fixedFullWorldCanvas':h['fullWorldCanvas'],'displayStage':h['displayStage'],'worldDensity':1,'commonCrop':h['crop'],'candidatePivot':h['candidatePivot'],'fullRoundedPivot':h['roundedFullPivot'],'oldPivotWorld':h['oldPivotWorld'],'rootRoundingDeltaWorld':[-.2857142857142776,-.4285714285714306],'lookClip':look,'contacts':[],'geometryScope':'image-registration-only','physicalSupportReviewed':False,'supportWorld':None,'runtimeAdmission':False,'currentAppearanceVerdict':'PENDING independent experiment review','currentGeometryVerdict':'PENDING independent experiment review'})
save('artifact-manifest.json',{'experiment':'ANIM-AUTHORING-COMPARE-1','arm':'A','method':'existing authored native attention sprite baseline','newNativeCalls':0,'newDrawings':0,'sourceBaseline':str(S.relative_to(R)),'baselineSourceManifest':'source-handoff.json','sourceHandoffSHA256':sha(P/'source-handoff.json'),'baselinePlayer':'review.html','baselinePlayerSHA256':sha(P/'review.html'),'baselinePlayerAPI':'ATTENTION_REPAIR_REVIEW alias FAMILY_REVIEW: ready/select/play/seek/getState','baselinePreview':'look.apng','baselinePreviewSHA256':sha(P/'look.apng'),'sourceFrameIDs':[x['sourceFrameId'] for x in h['frames']],'timingTicks30':[60,18,12],'sourceFullWorld':h['fullWorldCanvas'],'normalDisplayCSS':h['displayStage'],'exactPrompt':'prompt.txt','exactPromptSHA256':sha(P/'prompt.txt'),'promptBytes':len(prompt),'exactNativeArguments':'native-call-arguments.json','exactNativeArgumentsSHA256':sha(P/'native-call-arguments.json'),'referencePNG':'reference-awake-source1024.png','referencePNGsha256':sha(P/'reference-awake-source1024.png'),'copyProof':'baseline-copy-proof.json','metrics':'arm-a-metrics.json','sourceCompatibilityIsNotAdmission':True,'runtimeAdmission':False,'historicalMetadataScope':'Copied source-handoff/producer review statuses, counts and pending registration describe the original historical batch; current arm counts are only those in this additive artifact manifest.','currentIndependentReviewsPending':True,'priorReviews':'historical-reviews/; prior source decisions, not independent comparison-arm verdicts'})
for row in ledger['files']: assert sha(S/row['path'])==row['SHA256']
print(json.dumps({'copied':len(copied),'originalFrozen':45,'newCalls':0,'newDrawings':0,'sourceHandoffSHA256':sha(P/'source-handoff.json'),'PNGsha256':{f['role']:f['PNGsha256'] for f in h['frames']},'measuredPackagingSeconds':time.perf_counter()-clock}))
