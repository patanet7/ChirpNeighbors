"""Finalize existing checks without rerunning any normalizer or editing source arms."""
import pathlib,json,hashlib,re
from PIL import Image
O=pathlib.Path(__file__).resolve().parent;E=O.parent
sha=lambda b:hashlib.sha256(b).hexdigest()
def load(p):return json.loads(p.read_text())
def dump(p,d):p.write_text(json.dumps(d,indent=2)+'\n')
def rid(im):return 'frame.sha256.'+sha(f'RGBA8;{im.width}x{im.height};'.encode()+im.tobytes())
summary={};protocolDifferences=[];prov=[]
for arm in ['a','c']:
 r=O/('arm-'+arm);cfg=load(O/('arm-'+arm+'-config.json'));root=pathlib.Path(cfg['root']);metrics=load(r/'METRICS.json');h=load(root/cfg['handoff']['file']);ld=load(root/cfg['ledger']['file']);pairs=ld.get('files',ld) if isinstance(ld,dict) else ld
 pairs=[(p.get('file',p.get('path')),p.get('sha256',p.get('SHA256'))) for p in pairs] if isinstance(pairs,list) else list(pairs.items())
 for n,d in pairs:
  if isinstance(d,dict):d=d.get('sha256',d.get('SHA256'))
  assert sha((root/n).read_bytes())==d,n
 (r/'producer-index.snapshot.json').write_bytes((root/cfg['ledger']['file']).read_bytes());(r/'producer-STABLE-GO.snapshot.json').write_bytes((root/cfg['stableGO']['file']).read_bytes())
 args=load(root/'native-call-arguments.json');a=args.get('arguments',args);prompt=(root/'prompt.txt').read_bytes();assert a['prompt'].encode()==prompt;assert args.get('tool')=='image_gen.imagegen';assert a['transparent_background'] is True
 ret=load(root/'native-return-receipt.json');original=root/ret.get('original','original.png');assert sha(original.read_bytes())==ret['originalSHA256'];im=Image.open(original).convert('RGBA');id=rid(im);assert id==ret.get('primarySourceFrameId',ret.get('sourceFrameId'));assert ret['nativeCalls']==1
 refs=[]
 for name in a['referenced_image_paths']:
  p=pathlib.Path(name);assert p.exists();imref=Image.open(p).convert('RGBA');refs.append({'literalSubmittedPath':name,'PNGsha256':sha(p.read_bytes()),'decodedRGBAId':rid(imref),'dimensions':list(imref.size),'factualReferenceVerified':True})
 prov.append({'arm':arm.upper(),'tool':'image_gen.imagegen','nativeArgumentsSHA256':sha((root/'native-call-arguments.json').read_bytes()),'promptSHA256':sha(prompt),'promptUTF8Bytes':len(prompt),'literalPromptBytesExact':True,'returnReceiptSHA256':sha((root/'native-return-receipt.json').read_bytes()),'originalPNGsha256':ret['originalSHA256'],'originalDecodedRGBAId':id,'literalInputs':refs,'historicalReturnedNativeCalls':1,'callsForThisExperiment':0 if arm=='a' else 1,'sourceRegistrationPerformedHere':False,'fullPrivateAncestryPolicyOrRightsRecovery':False,'model':None,'seed':None,'unknownModelSeedMeaning':'Not supplied; null is not an inferred provider identifier.'})
 p=r/'pixel-receipt.json';pixel=load(p) if p.exists() else None
 error=None
 if not pixel:
  t=(r/'actual-pixel.stderr.txt').read_text();m=re.search(r'PermanentStageError: ([^\r\n]+)',t);error=m.group(1) if m else 'See exact actual pixel stderr'
 summary[arm.upper()]={'method':'Existing authored-native baseline copied exactly' if arm=='a' else 'One reference-conditioned native whole-pose edit','callsForThisExperiment':0 if arm=='a' else 1,'newDrawingsForThisExperiment':0 if arm=='a' else 1,'sourceFrameIDs':[f['sourceFrameID'] for f in metrics['frames']],'canvas':metrics['canvas'],'cropOrigin':metrics['cropOrigin'],'pivot':metrics['pivot'],'density':metrics['density'],'RGBAColorUnionIncludingTransparent':metrics['RGBAColorUnionIncludingTransparent'],'pixelStatus':pixel['status'] if pixel else 'FAIL actual unchanged normalizer','perFrameRectangles':pixel['perFrameRectangles'] if pixel else None,'rectangles':pixel['totalRectangles'] if pixel else None,'decodedArea':metrics['uniqueDecodedArea'],'actualPixelFailure':error,'JSON':load(r/'json-budget-receipt.json')['results'],'lookVsNeutralFullWorld':metrics['lookVsNeutralFullWorld'],'frameFacts':metrics['frames'],'contacts':[],'physicalSupportReviewed':False,'sourceAdmitted':False,'runtimeAdmission':False}
A=load(O/'arm-a/METRICS.json');C=load(O/'arm-c/METRICS.json');sameFields=['density','fullWorldCanvas','fullRoot','contacts','geometryScope','physicalSupportReviewed','supportWorld']
for n in sameFields:
 if A[n]!=C[n]:protocolDifferences.append({'field':n,'A':A[n],'C':C[n]})
def clock_semantics(m):return sorted([{'id':c['id'],'tickRate':c['tickRate'],'frames':c['frames'],'loop':c['loop']} for c in m['clocks']],key=lambda c:c['id'])
if clock_semantics(A)!=clock_semantics(C):protocolDifferences.append({'field':'clock semantics','A':clock_semantics(A),'C':clock_semantics(C)})
# Geometry protocol is shared; common crop and palette may differ and remain explicit.
rawChecks=[]
for role in ['neutral','blink']:
 a=next(f for f in A['frames'] if f['role']==role);c=next(f for f in C['frames'] if f['role']==role);assert a['sourceFrameID']==c['sourceFrameID'];assert a['sourcePNGsha256']==c['sourcePNGsha256'];assert a['rawPNGsha256']==c['rawPNGsha256'];rawChecks.append({'role':role,'sourceFrameID':a['sourceFrameID'],'nativeSourceBytesExactAcrossArms':True,'fullStageRawBytesExactAcrossArms':True,'finalPNGBytesExactAcrossArms':a['finalPNGsha256']==c['finalPNGsha256']})
assert not protocolDifferences,protocolDifferences
paletteA={tuple(p) for p in A['paletteRGB']};paletteC={tuple(p) for p in C['paletteRGB']}
dump(O/'native-provenance-receipt.json',{'scope':'Actual submitted prompt/input/output facts only; no provider attestation or private importer recovery','records':prov,'sourceEdits':0,'newCallsByTechnicalCheck':0,'sourceAdmitted':False})
dump(O/'COMPARISON.json',{'experiment':'ANIM-AUTHORING-COMPARE-1','runtimeCommit':'c4ae7529786e28cf55e2008b7f7b64215fc6542c','arms':summary,'B':{'state':'UNTESTED pending or unsupported compatible parts/rig implementation','pixelCheckRun':False,'qualityScore':None,'generationCalls':0},'sharedProtocolFieldsEqual':sameFields,'protocolDifferences':protocolDifferences,'sameReusedNativeSources':rawChecks,'paletteComparison':{'sharedOpaqueRGBColors':len(paletteA&paletteC),'AOnlyRGBColors':len(paletteA-paletteC),'COnlyRGBColors':len(paletteC-paletteA),'exactPaletteEqual':paletteA==paletteC},'cropComparison':{'sameCanvas':A['canvas']==C['canvas'],'sameOrigin':A['cropOrigin']==C['cropOrigin'],'sameLocalPivot':A['pivot']==C['pivot'],'commonFullRootPreserved':A['fullRoot']==C['fullRoot']},'interpretation':['Pixel normalization and JSON budgets are bounded engine-compatible source checks, not actual intake or admission.','A and C are both native-generated pose methods; A is an existing baseline, not evidence of a successful parts rig.','Fixed foot-region changes do not prove sole correspondence, grounding, contact or quality.','No source-quality or authoring-efficiency winner is inferred from these technical metrics.'],'sourceAdmitted':False,'runtimeAdmission':False})
print(json.dumps({'armsCompleted':['A','C'],'frozenSourcesUnchanged':True,'rawReusedNeutralAndBlinkExact':True,'sharedProtocolDifferences':len(protocolDifferences)}))
