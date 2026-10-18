"""Bounded source consumption. No repacking, runtime adoption, registry writes or new validator."""
import pathlib,json,hashlib,subprocess,sys,copy
from PIL import Image
O=pathlib.Path(__file__).resolve().parent;B=O.parent;UI=pathlib.Path('/workspace/runtime-resting-intake-v5-inspect');SHARED=pathlib.Path('/workspace/asset-production/validation/shared-structural-check.mjs');SHARP='/opt/codex/runtimes/codex-primary-runtime/dependencies/node/node_modules/sharp/dist/index.cjs'
sha=lambda b:hashlib.sha256(b).hexdigest()
def dump(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2)+'\n')
def run(cmd,label,out):
 r=subprocess.run(cmd,cwd=UI,capture_output=True,text=True);(out/(label+'.stdout.txt')).write_text(r.stdout);(out/(label+'.stderr.txt')).write_text(r.stderr);return {'command':cmd,'exitCode':r.returncode,'stdout':label+'.stdout.txt','stderr':label+'.stderr.txt'}
def member(root,name):
 p=(root/name).resolve();assert p.is_relative_to(root.resolve()),'Source path escapes assigned candidate folder';return p
cfgpath=pathlib.Path(sys.argv[1]).resolve();assert cfgpath.is_relative_to(O);cfg=json.loads(cfgpath.read_text());cid=cfg['candidateId'];assert cid and all(c.isalnum() or c in '-_' for c in cid)
root=pathlib.Path(cfg['candidateRoot']).resolve();assert any(root.is_relative_to(B/p) for p in ['blink-repairs','attention-repairs','movement-support','flight-art','flight-tech-repair'])
out=O/'receipts'/cid;assert not out.exists(),'Existing receipt retained; use an explicitly versioned config/output for a justified correction';out.mkdir(parents=True)
try:
 authority=json.loads((O/'authority-receipt.json').read_text());assert sha(SHARED.read_bytes())==authority['sharedRunner']['sha256'];assert subprocess.check_output(['git','-C',str(UI),'rev-parse','HEAD'],text=True).strip()==authority['runtimeCommit']
 for f in authority['authorityFiles']:assert sha((UI/f['file']).read_bytes())==f['sha256'],f['file']
 handoff=member(root,cfg['handoff']['file']);assert sha(handoff.read_bytes())==cfg['handoff']['sha256'];h=json.loads(handoff.read_text());ledger=member(root,cfg['freezeLedger']['file']);assert sha(ledger.read_bytes())==cfg['freezeLedger']['sha256'];ld=json.loads(ledger.read_text());entries=ld.get('files',ld) if isinstance(ld,dict) else ld
 if isinstance(entries,list):pairs=[(f.get('file',f.get('path')),f.get('sha256',f.get('SHA256'))) for f in entries]
 else:pairs=list(entries.items())
 for n,d in pairs:
  if isinstance(d,dict):d=d.get('sha256',d.get('SHA256'))
  assert sha(member(root,n).read_bytes())==d,n
 width,height=cfg['canvas']['width'],cfg['canvas']['height'];frames=[];pixel_frames=[];identities=[]
 for f in cfg['frames']:
  p=member(root,f['png']);b=p.read_bytes();assert sha(b)==f['PNGsha256'];im=Image.open(p).convert('RGBA');assert im.size==(width,height);rgba=im.tobytes();rid='frame.sha256.'+sha(f'RGBA8;{width}x{height};'.encode()+rgba);assert rid==f['decodedRGBAId'];frames.append({'role':f['role'],'png':str(p),'PNGsha256':f['PNGsha256'],'decodedRGBAId':rid});pixel_frames.append({'rgba':list(rgba)});identities.append({**f,'verifiedPNG':True,'verifiedDecodedIdentity':True})
 native_facts=[]
 for f in cfg.get('sourceFacts',[]):
  p=member(root,f['sourcePNG']);b=p.read_bytes();assert sha(b)==f['sourcePNGsha256'];im=Image.open(p).convert('RGBA');rid='frame.sha256.'+sha(f'RGBA8;{im.width}x{im.height};'.encode()+im.tobytes());expected=f.get('sourceFrameID',f.get('sourceFrameId'));assert rid==expected,'Native/registered source identity mismatch: '+str(p);native_facts.append({'sourceFrameID':expected,'sourcePNG':f['sourcePNG'],'PNGsha256':f['sourcePNGsha256'],'decodedIdentityVerified':True,'newDrawingAsDeclared':f.get('newDrawing'),'globallyRegisteredAsDeclared':f.get('globallyRegistered',not f.get('newDrawing',False))})
 dump(out/'source-identity-receipt.json',{'sourceFacts':native_facts,'sourceFilesUnchanged':True,'parentBankModified':False,'registrationNotPerformed':True,'fullRecursiveAncestryNotAssessed':True})
 for e in cfg.get('ancestryFiles',[]):assert sha(member(root,e['file']).read_bytes())==e['sha256'],e['file']
 dump(out/'frozen-input-receipt.json',{'candidateRoot':str(root),'handoff':cfg['handoff'],'freezeLedger':cfg['freezeLedger'],'producerFrozenFilesExact':len(pairs),'candidateFrames':identities,'sourceBytesModified':False,'registrationState':cfg.get('registrationState','not verified; root owns registration'),'retainedAncestryFilesChecked':cfg.get('ancestryFiles',[]),'ancestryBlockers':cfg.get('ancestryBlockers',['Importer collectProjectLineage and registry reconciliation have not executed here.']),'completeGeneratedAncestryReviewed':False,'sourceAdmitted':False})
 raw={'canvas':cfg['canvas'],'frames':pixel_frames,'logicalPixelSize':1,'paletteLimit':64};dump(out/'raw-candidate-input.json',raw)
 pixel_cfg={'expectedPackageSHA256':sha((UI/'src/lib/server/asset-pipeline/package.ts').read_bytes()),'expectedCanonicalSHA256':sha((UI/'src/lib/server/pipeline/canonical.ts').read_bytes()),'canvas':cfg['canvas'],'frames':frames,'logicalPixelSize':1,'paletteLimit':64,'contacts':[],'geometryReviewed':False,'supportWorld':None};dump(out/'canonical-pixel-input.json',pixel_cfg)
 commands=[]
 if cfg.get('producerPixelReceipt'):
  e=cfg['producerPixelReceipt'];p=member(root,e['file']);b=p.read_bytes();assert sha(b)==e['sha256'];prior=json.loads(b);assert prior['status']=='PASS exact canonical pixel normalization subset';pc=member(root,e['inputFile']);assert sha(pc.read_bytes())==e['inputSHA256']==prior['inputSHA256'];pd=json.loads(pc.read_text());assert prior['sharedRunnerSHA256']==sha(SHARED.read_bytes());assert prior['canonicalRepositoryHead']==authority['runtimeCommit'];assert prior['packageFileSHA256']==pixel_cfg['expectedPackageSHA256'];assert prior['canonicalErrorModuleSHA256']==pixel_cfg['expectedCanonicalSHA256'];assert prior['canvas']==cfg['canvas'];assert prior['RGBAReconstructionExact'] and prior['actualCanonicalPermanentStageErrorUsed'] and prior['partialAlphaNegativeControlRejected'];assert len(prior['candidateImages'])==len(frames)==len(pd['frames'])
  for before,declared,actual in zip(prior['candidateImages'],pd['frames'],frames):
   assert before['PNGsha256']==declared['PNGsha256']==actual['PNGsha256'];assert before['decodedRGBAId']==declared['decodedRGBAId']==actual['decodedRGBAId'];assert pathlib.Path(pc.parent/declared['png']).resolve()==pathlib.Path(actual['png'])
  (out/'pixel-receipt.json').write_bytes(b);dump(out/'producer-pixel-receipt-verification.json',{'status':'PASS exact actual producer-executed receipt verified; codec not rerun','producerReceipt':e,'authorityHashesExact':True,'candidatePNGsAndDecodedIdentitiesExact':True,'sourceAdmitted':False});commands.append({'operation':'Verified and retained exact producer-executed shared pixel subset','exitCode':0,'receipt':'pixel-receipt.json','codecRerun':False})
 else:commands.append(run(['node',str(SHARED),'--repo',str(UI),'--input',str(out/'canonical-pixel-input.json'),'--receipt',str(out/'pixel-receipt.json'),'--sharp',SHARP],'actual-pixel-subset',out))
 if cfg['candidateKind']=='common-family':
  role={f['role']:i for i,f in enumerate(cfg['frames'])};missing=set(['neutral','blink','look'])-set(role)
  if missing:
   dump(out/'metadata-blocker.json',{'status':'BLOCKED missing genuine common family frames','missingRoles':sorted(missing),'fakeReplacementMade':False,'sourceAdmitted':False})
  else:
   pivot=cfg['pivot'];clips={c['id']:c for c in cfg['clips']};assert set(clips)=={'idle','blink','look'};assert cfg['density'] in [1,2,4]
   def pose(r,t,id):return {'frame':role[r],'durationTicks':t,'pivot':pivot,'contacts':[],'poseId':id,'rotation':0}
   idle=clips['idle'];assert idle['roles']==['neutral'] and idle['loop'] and idle['tickRate']==30
   nodes=[];edges=[];named={}
   for name in ['blink','look']:
    c=clips[name];assert c['roles']==['neutral',name,'neutral'] and c['tickRate']==30 and len(c['durationTicks'])==3
    ids=[name+'-neutral',name+'-expression',name+'-neutral'];pp=[pose(r,t,i) for r,t,i in zip(c['roles'],c['durationTicks'],ids)];named[name]={'name':name,'loop':c['loop'],'poses':pp};nodes.extend([{'id':ids[0],'frame':role['neutral'],'clip':name,'referenceId':None},{'id':ids[1],'frame':role[name],'clip':name,'referenceId':None}]);edges.extend([{'from':ids[0],'to':ids[1]},{'from':ids[1],'to':ids[2]}])
    if c['loop']:edges.append({'from':ids[2],'to':ids[0]})
   input4={'schemaVersion':4,'source':{'schemaVersion':1,'speciesId':cfg['catalogSpeciesId'],'representation':'Existing generated bird sources and bounded new repair; detailed naturalistic pixel art','source':'provider','reviewScope':'development-candidate','creator':'OpenAI','sourceVersion':cid,'license':{'id':None,'status':'development-only','derivativesAllowed':None,'redistributionAllowed':None,'evidenceId':None,'attribution':None},'references':[],'fidelityReview':None},'pixels':{'schemaVersion':2,'format':'rgba8-frames',**raw},'clips':{'idle':{'action':'idle','direction':'right-facing-mirrorable','loop':True,'poses':[pose('neutral',idle['durationTicks'][0],'idle-neutral')]}},'conditioning':{'taxonomy':{'catalog':'chirp-display-catalog','version':1,'speciesId':cfg['catalogSpeciesId']},'references':[],'poseGraph':{'nodes':[{'id':'idle-neutral','frame':role['neutral'],'action':'idle','referenceId':None}],'edges':[{'from':'idle-neutral','to':'idle-neutral'}]}},'strategy':{'kind':'decoded-rgba','version':1,'alphaOrigin':cfg['alphaOrigin'],'output':'rgba8-binary'},'presentation':{'schemaVersion':1,'sourcePixelsPerWorldUnit':cfg['density']},'commonMotion':{'schemaVersion':1,'geometryScope':'image-registration-only','physicalSupportReviewed':False,'idleSequence':['idle','blink','look'],'clips':named,'poseGraph':{'nodes':nodes,'edges':edges}}}
   dump(out/'producer-proposal.json',{'schemaVersion':1,'kind':'project-generated-common-proposal','input':input4});input5=copy.deepcopy(input4);input5['schemaVersion']=5;dump(out/'incomplete-input5.json',input5)
   commands.append(run(['node',str(UI/'scripts/check-common-intake.ts'),str(out/'incomplete-input5.json')],'actual-intake-cli',out))
 else:dump(out/'metadata-blocker.json',{'status':'NOT APPLICABLE to common-only input5/proposal','candidateKind':cfg['candidateKind'],'reason':'Existing gait/support source study is not neutral/blink/look idle presentation. No activity was renamed to pass common-family authority.','sourceAdmitted':False})
 commands.append(run(['node',str(O/'check-official.mjs'),str(out)],'official-proposal-json',out));dump(out/'commands.json',commands)
 official=json.loads((out/'official-checks.json').read_text()) if (out/'official-checks.json').exists() else None
 if official:dump(out/'CHECK-SUMMARY.json',{'actualPixelCheckStatus':json.loads((out/'pixel-receipt.json').read_text())['status'] if (out/'pixel-receipt.json').exists() else 'FAIL actual pixel normalization; see preserved stderr','canonicalJSON':official.get('rawCandidateBudget'),'officialProducerProposalShapePass':official.get('proposal',{}).get('shapePass'),'actualInput5Diagnostic':official.get('input5Diagnostic'),'actualSourceDeclaration':official.get('sourceDeclaration'),'sourceAdmitted':False,'runtimeAdmission':False})
 dump(out/'RESULT.json',{'status':'COMPLETED bounded source checks; inspect actual failure receipts and incomplete authority','candidateId':cid,'kind':cfg['candidateKind'],'commands':commands,'sourceAdmitted':False,'runtimeAdmission':False,'sourceArtGenerationCalls':0,'noSourcePixelsOrFilesModified':True,'fullGeneratedAncestryOrPrivateBindingRecoveryExecuted':False,'fullGraphCustomRefinementsValidated':False})
 print(json.dumps({'candidateId':cid,'output':str(out),'exitCodes':[x['exitCode'] for x in commands],'sourceAdmitted':False}))
except Exception as e:
 dump(out/'consumption-failure.json',{'type':type(e).__name__,'message':str(e),'sourceModified':False,'sourceAdmitted':False});raise
