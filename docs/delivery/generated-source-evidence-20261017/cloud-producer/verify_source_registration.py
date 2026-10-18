"""DRAFT stage75: one native Bushtit original plus a zero-native Crow outcome.

Source-only, no generation/admission. Root owns mutation and publication. This
module does not mutate D. verify(root) checks an ALREADY registered190/73 corpus,
then runs the exact published stage69 verifier in a temporary hardlink view with
all eight old metadata paths unlinked and restored to189/72/25/5726 snapshots.
No byte-linked payload is opened for writing. Final producer references must be
bound by root before this draft is selected for execution.
"""
from __future__ import annotations
import argparse
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import stat
import subprocess
import sys
import tempfile
from typing import Any
from PIL import Image

STAGE = 75
BASELINE_DIRECTORY = 'registration-baseline-stage75'
LEDGER = 'source-registration-stage75.json'
PRIOR_INDEX_SHA256 = 'e153a00f7f41e9e0ebb203f69bbf12e21d3c2f8637f39544acf6390a06c896c2'
PRIOR_INDEX_ENTRIES = 5726
LEGACY_VERIFIER_SHA256 = '82086b056e6e04039b2beefac09fc0ace079c83263680c477390b59189b82bb5'
ACTIVE = 'release/animation-checkpoint-1-20261017/CURRENT-SLOT-INVENTORY.json'
ACTIVE_SHA256 = '164507fddf904e892ec95868841271effc5a4e7da4232c4d1f6c18cc6385351a'
OVERLAY = 'release/animation-checkpoint-1-20261017/intake-overlay.json'
NATIVE_EXPERIMENT = 'BUSHTIT-logical64-readable-eyelid-source-3'
NATIVE_PACKET = 'experiments/bushtit-logical64-eyelid-v3'
ZERO_PACKET = 'experiments/crow-attention-selected-ground-palette-v1'
REPORTS = 'reports/qualification-continuation-20261018'
OVERRIDES = {'frame-bank.json':'frame-bank.json',
 'original-source-inventory.json':'original-source-inventory.json',
 'source-frame-map.json':'source-frame-map.json',
 'verify_source_registration.py':'verify_source_registration.py',
 'verify_source_files.py':'verify_source_files.py',
 'lessons-and-experiments.json':'lessons-and-experiments.json',
 'source-files.sha256.json':'source-files.sha256.json',OVERLAY:'intake-overlay.json'}
BASELINE_SHA = {'frame-bank.json':'b7df3a39b2eb85da0407b8b4f89d98e6f5019db7e338685ba23ea252819b859e',
 'original-source-inventory.json':'0a0cc46e5c08be575b6a884d63c44659b722dfa480a6477087ed4af9a7259722',
 'source-frame-map.json':'6f15f0ab5771c7897090d35971861ca9e75ff38d2808dee2204de104725b217b',
 'verify_source_registration.py':LEGACY_VERIFIER_SHA256,
 'verify_source_files.py':'870995a0ec5da92c1b3b0e7e6b26e4432e2a5653ac028fde84d5a3d2cfd6d1c6',
 'lessons-and-experiments.json':'c7c20bc9d7b17481d058a51dce18a7d456371cd3f8a704216b4579859261c517',
 'source-files.sha256.json':PRIOR_INDEX_SHA256,
 OVERLAY:'1fae8a71301e1e49b134759eedfc293ff5b0266dd24cb399b2ba2aeeb122fe40'}

class VerificationError(RuntimeError): pass

def require(condition: Any, message: str) -> None:
 if not condition: raise VerificationError(message)

def sha(path: Path) -> str: return hashlib.sha256(path.read_bytes()).hexdigest()
def load(path: Path) -> Any: return json.loads(path.read_text(encoding='utf-8'))
def inside(root: Path, relative: str) -> Path:
 require(isinstance(relative,str) and relative and not Path(relative).is_absolute()
         and '..' not in Path(relative).parts,'Unsafe nonlocal source path')
 require(not root.is_symlink(),'Symlink root forbidden')
 p=root
 for part in Path(relative).parts:
  p/=part;require(not p.is_symlink(),f'Symlink source path: {relative}')
 resolved=p.resolve(strict=True)
 require(resolved.is_relative_to(root.resolve()),'Source path escapes root')
 return resolved

def checked_file(root: Path, relative: str, expected: str|None=None) -> Path:
 p=inside(root,relative);require(p.is_file(),f'Missing source file: {relative}')
 if expected is not None: require(sha(p)==expected,f'SHA mismatch: {relative}')
 return p

def rgba(path: Path) -> Image.Image:
 with Image.open(path) as im:return im.convert('RGBA')

def frame_id(im: Image.Image) -> str:
 return 'frame.sha256.'+hashlib.sha256(f'RGBA8;{im.width}x{im.height};'.encode('ascii')+im.tobytes()).hexdigest()

def legacy_definitions(baseline: Path) -> dict[str,Any]:
 p=checked_file(baseline,'verify_source_registration.py',LEGACY_VERIFIER_SHA256)
 helpers={'__name__':'stage75_exact_stage69_helpers','__file__':str(p)}
 exec(compile(p.read_text(),str(p),'exec'),helpers)
 return helpers

def verify_logical64_conditioning(packet: Path, prereg: dict, arguments: dict,
                                  old_bank: dict, old_root: Path) -> dict:
 """Exact existing canonical64 ->16x1024 reference is not a new drawing."""
 awake=prereg['awake'];cond=prereg['nativeConditioning']
 old_by_id={f['frameId']:f for f in old_bank['frames']}
 ident=awake['sourceFrameId'];require(ident in old_by_id,'Conditioning ancestry not registered')
 native=checked_file(packet,awake['nativeFile'],awake['nativePNGsha256'])
 bank_native=checked_file(old_root,old_by_id[ident]['file'],old_by_id[ident]['fileSha256'])
 require(sha(native)==sha(bank_native) and frame_id(rgba(native))==ident,
         'Retained registered native ancestry differs')
 canonical_path=checked_file(packet,awake['canonical64'],awake['canonical64SHA256'])
 canonical=rgba(canonical_path);require(canonical.size==(64,64),'Canonical grid is not64square')
 # This published source-family manifest binds the existing rendered64 to the
 # same registered native identity. No new quantization/phase/codec is run here.
 family_rel='experiments/resting-repair-ground-motion-v1/blink-repairs/bushtit/family-handoff.json'
 family=load(checked_file(old_root,family_rel))
 matches=[f for f in family['frames'] if f.get('role')=='neutral'
          and f.get('sourceFrameID')==ident and f.get('PNGsha256')==sha(canonical_path)]
 require(len(matches)==1,'Canonical64 has no exact published source/native binding')
 published64=checked_file((old_root/family_rel).parent,matches[0]['png'],sha(canonical_path))
 require(published64.read_bytes()==canonical_path.read_bytes(),'Canonical64 differs from old indexed render')
 conditioning_path=checked_file(packet,cond['soleImage'],cond['sha256'])
 conditioning=rgba(conditioning_path)
 require(conditioning.size==(1024,1024)==tuple(cond['canvas']),'Conditioning canvas differs')
 # Existing whole integer nearest upscale, byte comparison only; no PNG export.
 require(canonical.resize((1024,1024),Image.Resampling.NEAREST).tobytes()==conditioning.tobytes(),
         'Conditioning is not exact16x RGBA replication')
 refs=arguments.get('referenced_image_paths',[])
 require(len(refs)==1 and Path(refs[0]).as_posix().endswith('/'+cond['soleImage']),
         'Sole actual input differs; native ancestry must not be counted as a second input')
 provenance=load(checked_file(packet,'input-provenance.json'))
 inputs=provenance['actualSubmittedImages'];require(len(inputs)==1,'Actual submitted image enumeration differs')
 item=inputs[0]
 require(item['path']==cond['soleImage'] and item['sha256']==sha(conditioning_path)
         and item['upstream']==awake['canonical64'] and item['upstreamSHA256']==sha(canonical_path)
         and item['nativeSourceFrameId']==ident and item['newDrawing'] is False,
         'Conditioning derivative provenance differs')
 require(set(provenance['otherInputsRetainedNotSubmitted'])
         .isdisjoint({item['path']}),'Submitted image mislabeled as unsubmitted')
 return {'registeredNativeSourceID':ident,'canonical64SHA256':sha(canonical_path),
         'conditioningSHA256':sha(conditioning_path),'conditionedRGBAId':frame_id(conditioning),
         'integerUpscale':16,'newNativeDrawingsFromConditioning':0,'exactRoundtrip':True}

def verify_stage75_receipts(batch: dict, prompt: bytes, arguments: dict,
                            arguments_sha: str, dispatch: dict, returned: dict,
                            packet: Path) -> dict:
 """Validate actual v3 states directly; never rewrite them into the v2 protocol.

 observedAwaitMs is a measured tool-await scope. Dispatch-to-receipt includes
 other work and has different endpoints; neither implies a server duration.
 """
 require(dispatch.get('state')=='DISPATCHING_NATIVE_IMAGE_EDIT'
         and returned.get('state')=='NATIVE_RETURNED_ONE_CALL_NO_RETRY',
         'Unrecognized actual stage75 native receipt states')
 require(dispatch.get('tool')=='image_gen.imagegen'
         and dispatch.get('nativeCallNumber')==dispatch.get('nativeCallsStarted')==1
         and dispatch.get('nativeCallsReturned')==0 and dispatch.get('nativeCallsRunning')==1
         and dispatch.get('maxNativeCalls')==1 and dispatch.get('automaticRetries')==0,
         'Actual dispatch does not bind exactly one in-flight request')
 require(returned.get('nativeCallsStarted')==returned.get('nativeCallsReturned')==returned.get('newNativeDrawings')==1
         and returned.get('nativeCallsRunning')==returned.get('automaticRetries')==0,
         'Actual return count/retry/running state differs')
 args_path=checked_file(packet,dispatch['argumentsFile'],arguments_sha)
 record=load(args_path)
 require(record.get('tool')=='image_gen.imagegen' and record.get('arguments')==arguments
         and dispatch['argumentsSHA256']==sha(args_path),'Actual wrapped invocation arguments differ')
 require(arguments.get('transparent_background')is True and arguments['prompt'].encode('utf-8')==prompt
         and hashlib.sha256(prompt).hexdigest()==batch['promptSHA256']==dispatch['promptSHA256'],
         'Literal prompt/transparency differs')
 require(dispatch['preregistrationSHA256']==sha(checked_file(packet,'PREREGISTRATION.json')),
         'Dispatch preregistration hash differs')
 began=datetime.fromisoformat(dispatch['dispatchUTC'].replace('Z','+00:00'))
 ended=datetime.fromisoformat(returned['returnedUTC'].replace('Z','+00:00'))
 require(began.tzinfo is not None and ended.tzinfo is not None and began<=ended,
         'Invalid actual dispatch/return chronology')
 await_ms=returned.get('observedAwaitMs')
 require(isinstance(await_ms,(int,float)) and not isinstance(await_ms,bool) and await_ms>=0,
         'Missing observed await duration')
 original=checked_file(packet,returned['original'],batch['originalSHA256']);image=rgba(original)
 require(returned['originalSHA256']==sha(original) and returned['originalBytes']==original.stat().st_size
         and returned['mode']=='RGBA' and returned['nativeCanvas']==list(image.size)==[1254,1254]
         and returned['sourceFrameId']==frame_id(image)==batch['frames'][0]['sourceFrameId']
         and returned['sourceOriginalRect']==[0,0,1254,1254]
         and returned['sourceWholeCanvasOriginalUnchanged']is True,
         'Native return original/canvas/primary identity differs')
 require(returned.get('model')is None and returned.get('seed')is None,
         'Do not invent an unexposed model/seed')
 return {'protocol':'actual-v3-state-fields','nativeCallsReturned':1,'automaticRetries':0,
         'wrappedArgumentsSHA256':arguments_sha,'observedAwaitMilliseconds':await_ms,
         'dispatchToReturnReceiptSeconds':(ended-began).total_seconds(),
         'timingScopesDistinct':True,'serverGenerationDuration':'UNKNOWN'}

def verify_packet_seal(root: Path, packet_rel: str) -> dict:
 packet=inside(root,packet_rel)
 rows=load(checked_file(packet,'FINAL-source-files.sha256.json'))['files'];seen=set()
 for row in rows:
  require(row['file'] not in seen,'Duplicate final seal path');seen.add(row['file'])
  p=checked_file(packet,row['file'],row['sha256'])
  if 'bytes' in row: require(p.stat().st_size==row['bytes'],'Final seal byte length differs')
 require('ROOT-ADJUDICATION.json'in seen and 'PREREGISTRATION.json'in seen,'Root seal lacks outcome/preregistration')
 actual=set()
 for p in packet.rglob('*'):
  require(not p.is_symlink(),'Symlink in source packet')
  if p.is_file():actual.add(str(p.relative_to(packet)))
 require(actual==seen|{'FINAL-source-files.sha256.json'},'Sealed packet has unindexed additions')
 return {'packet':packet_rel,'sealedFiles':len(seen)}

def prior_bytes(root: Path, baseline: Path, ledger: dict) -> dict:
 old_index=load(checked_file(baseline,'source-files.sha256.json',PRIOR_INDEX_SHA256))
 require(len(old_index['files'])==PRIOR_INDEX_ENTRIES==ledger['priorSourceIndexEntries']
         and ledger['priorSourceIndexSHA256']==PRIOR_INDEX_SHA256,'Wrong prior5726 index')
 allowed=set(OVERRIDES)|{'README.md'};seen=set();protected=0
 for row in old_index['files']:
  require(row['file']not in seen,'Duplicate historical index path');seen.add(row['file'])
  p=checked_file(root,row['file'])
  if row['file']not in allowed:
   require(sha(p)==row['sha256'] and p.stat().st_size==row['bytes'],f'Old indexed bytes changed: {row["file"]}')
   protected+=1
 for target,snapshot in OVERRIDES.items():checked_file(baseline,snapshot,BASELINE_SHA[target])
 # No historical ledger gets a metadata exception.
 for name in ['source-registration-stage69.json','source-registration-stage67.json',
              'source-registration-stage63.json','source-registration-stage61.json',
              'source-registration-continuation-v1.json']:
  row=next(r for r in old_index['files']if r['file']==name);checked_file(root,name,row['sha256'])
 checker=checked_file(root,'verify_source_files.py').read_text();original=checker
 for before,after in [("len(originals['originals']) == 72","len(originals['originals']) == 73"),
   ("len(bank['frames']) == 189","len(bank['frames']) == 190"),
   ("len({f['frameId'] for f in bank['frames']}) == 189","len({f['frameId'] for f in bank['frames']}) == 190"),
   ('pixel_count = 189','pixel_count = 190'),("'originalPromptPairs': 72","'originalPromptPairs': 73")]:
  require(original.count(after)==1,'General checker count edit ambiguous');original=original.replace(after,before)
 require(hashlib.sha256(original.encode()).hexdigest()==BASELINE_SHA['verify_source_files.py'],
         'General checker changed beyond five source-count assertions')
 return {'oldIndexEntries':5726,'oldNonMetadataByteExact':protected,'oldLedgersByteExact':True,
         'fiveGeneralCheckerEditsOnly':True,'newReportsAllowedBelow':REPORTS}

def historical_stage69(root: Path, baseline: Path) -> dict:
 legacy=checked_file(baseline,'verify_source_registration.py',LEGACY_VERIFIER_SHA256)
 guards={k:sha(checked_file(root,k))for k in OVERRIDES}
 with tempfile.TemporaryDirectory(prefix='.stage75-stage69-',dir=root.parent)as dirname:
  temp=Path(dirname)
  for directory,dirs,files in os.walk(root,followlinks=False):
   srcdir=Path(directory);dst=temp/srcdir.relative_to(root);dst.mkdir(parents=True,exist_ok=True)
   for name in dirs:require(not(srcdir/name).is_symlink(),'Symlink source directory')
   for name in files:
    p=srcdir/name;require(not p.is_symlink()and stat.S_ISREG(p.stat().st_mode),'Nonregular payload')
    os.link(p,dst/name,follow_symlinks=False)
  for target,snapshot in OVERRIDES.items():
   (temp/target).unlink() # sever every hardlink before restoring old metadata
   shutil.copyfile(checked_file(baseline,snapshot,BASELINE_SHA[target]),temp/target)
  env=os.environ.copy();env['PYTHONDONTWRITEBYTECODE']='1'
  result=subprocess.run([sys.executable,str(temp/'verify_source_registration.py'),'--root',str(temp)],
    cwd=temp,env=env,text=True,capture_output=True,timeout=900)
  require(result.returncode==0,'Exact stage69 reconstructed regression failed:\n'+result.stdout+result.stderr)
  d=json.loads(result.stdout)
  require(d.get('passed')is True and d.get('stage')==69
          and d['totalBankDrawingIDs']==189 and d['totalOriginalPromptPairs']==72,
          'Historical stage69 result/counts differ')
 require(all(sha(checked_file(root,k))==v for k,v in guards.items()),'Historical callback mutated current metadata')
 return {'verifierSHA256':sha(legacy),'overrides':list(OVERRIDES),'result':d,'sourceMetadataUnchanged':True}

def safe_new_reports(root: Path) -> dict:
 directory=root/REPORTS;count=0
 if directory.exists():
  for p in directory.rglob('*'):
   require(not p.is_symlink(),'Symlink new report')
   if not p.is_file():continue
   count+=1
   if p.suffix.lower()not in{'.json','.md','.txt','.html','.js'}:continue
   text=p.read_text()
   require(re.search(r'libfile_[a-f0-9]{32}|data:image/[^;,]+;base64,|https?://[^\s"<>]+[?&](?:X-Amz-Signature|Signature|sig)=',text,re.I)is None,
           'Private Library/signed URL/capture payload in new report')
   if p.suffix=='.json':
    def walk(v):
     if isinstance(v,dict):
      for k,item in v.items():
       if k.lower()in{'ownerid','actorid','residentid','activemanifestid','sourceartifactid','referencepinid','supportinstanceid'}:
        require(item is None,'Concrete private runtime identifier in new report')
       walk(item)
     elif isinstance(v,list):
      for item in v:walk(item)
    walk(json.loads(text))
 return {'path':REPORTS,'files':count,'privateBindingValuesAllowed':False,'reportsAddSourceDrawings':0}

def verify(root: Path) -> dict:
 require(not root.is_symlink(),'Symlink root');root=root.resolve(strict=True)
 ledger=load(checked_file(root,LEDGER));require(ledger['stage']==75,'Wrong stage ledger')
 require(ledger['baselineDirectory']==BASELINE_DIRECTORY,'Wrong baseline directory')
 baseline=inside(root,BASELINE_DIRECTORY)
 for target,snapshot in OVERRIDES.items():checked_file(baseline,snapshot,BASELINE_SHA[target])
 require(ledger['priorVerifierSHA256']==LEGACY_VERIFIER_SHA256,'Wrong historical verifier pin')
 for key,target in [('oldBankRecordsSHA256','frame-bank.json'),('oldOriginalRecordsSHA256','original-source-inventory.json'),
                    ('oldFrameMapSHA256','source-frame-map.json'),('oldOverlaySHA256',OVERLAY),
                    ('oldLessonsSHA256','lessons-and-experiments.json')]:
  require(ledger[key]==BASELINE_SHA[target],'Ledger baseline hash binding differs: '+key)
 old_bank=load(baseline/'frame-bank.json');old_inv=load(baseline/'original-source-inventory.json');old_map=load(baseline/'source-frame-map.json')
 bank=load(checked_file(root,'frame-bank.json'));inv=load(checked_file(root,'original-source-inventory.json'));mapping=load(checked_file(root,'source-frame-map.json'))
 require(len(old_bank['frames'])==len(old_map['frames'])==189 and len(old_inv['originals'])==72,'Old189/72 baseline differs')
 require(ledger['baselineDrawings']==189 and ledger['baselineOriginals']==72,'Ledger old counts differ')
 require(bank['frames'][:189]==old_bank['frames'] and inv['originals'][:72]==old_inv['originals']
         and mapping['frames'][:189]==old_map['frames'],'Exact old189/72 prefix altered')
 require(len(bank['frames'])==len(mapping['frames'])==bank['frameCount']==190
         and len(inv['originals'])==73,'Final190/73 counts differ')
 require({k:v for k,v in bank.items()if k not in{'frames','frameCount','status'}}
         =={k:v for k,v in old_bank.items()if k not in{'frames','frameCount','status'}},'Bank authority/reuse metadata changed')
 require({k:v for k,v in inv.items()if k not in{'originals','localGeneratedDrawings','newGenerationCallsForThisHandoff'}}
         =={k:v for k,v in old_inv.items()if k not in{'originals','localGeneratedDrawings','newGenerationCallsForThisHandoff'}},'Old inventory metadata changed')
 require({k:v for k,v in mapping.items()if k!='frames'}=={k:v for k,v in old_map.items()if k!='frames'},'Old map metadata changed')
 require(inv['localGeneratedDrawings']==190 and inv['newGenerationCallsForThisHandoff']==1,'Inventory counter differs')
 require(ledger['registeredDrawings']==190 and ledger['registeredOriginals']==73
         and ledger['newNativeOriginals']==ledger['newNativeDrawings']==ledger['actualGenerationCallsInBatch']==1
         and ledger['registrationMakesNativeCalls']==ledger['acceptedUsesAdded']==0
         and ledger['runtimeAdmission']is False,'Source registration counts or admission differ')
 appended=ledger['appendedBankRecords'];batches=ledger['registrationOnlyBatches']
 require(len(appended)==len(batches)==1 and bank['frames'][189:]==appended,'Only one new native primary may append')
 old_ids={f['frameId']for f in old_bank['frames']};ids=set()
 for f,mp in zip(bank['frames'],mapping['frames']):
  im=rgba(checked_file(root,f['file'],f['fileSha256']));ident=frame_id(im)
  require(ident==f['frameId']and ident not in ids and list(im.size)==f['dimensions'],'Full bank identity/dimensions/uniqueness differs');ids.add(ident)
  require(f.get('acceptedUses')==[],'Accepted uses changed')
  require(mp['sourceFrameId']==ident and mp['sourcePNG']==f['file']and mp['sourcePNGsha256']==f['fileSha256']
          and mp['dimensions']==f['dimensions']and mp['original']==f['sourceAtlas']
          and mp.get('prompt')==f.get('sourcePrompt')and mp.get('acceptedUses')==[],'Map provenance differs')
 for item in inv['originals']:
  p=checked_file(root,item['file'],item['sha256']);q=checked_file(root,item['promptFile'],item['promptSha256'])
  require(p.stat().st_size==item['bytes']and q.stat().st_size==item['promptBytes']and list(rgba(p).size)==item['dimensions'],'Original/prompt identity differs')
 b=batches[0];f=appended[0];item=inv['originals'][72];legacy=legacy_definitions(baseline)
 require(b['nativeCalls']==1 and b['acceptedUses']==[]and b['runtimeAdmission']is False,'Native batch count/admission differs')
 require(b['originalSHA256']not in{v['sha256']for v in old_inv['originals']},'Native original already counted')
 orig=checked_file(root,b['original'],b['originalSHA256']);im=rgba(orig);require(im.size==(1254,1254)==tuple(b['originalDimensions']),'Actual nativecanvas differs')
 packet=orig.parent;require(str(packet.relative_to(root))==NATIVE_PACKET,'Wrong native packet')
 prompt=checked_file(root,b['prompt'],b['promptSHA256']);require(len(prompt.read_bytes())==b['promptBytes'],'Prompt byte count differs')
 args_path=checked_file(root,b['nativeArguments'],b['nativeArgumentsSHA256']);arg_record=load(args_path);args=arg_record.get('arguments',arg_record)
 require(args['prompt'].encode()==prompt.read_bytes(),'Literal prompt bytes differ')
 dispatch=load(checked_file(root,b['dispatchReceipt'],b['dispatchSHA256']));returned=load(checked_file(root,b['returnReceipt'],b['returnSHA256']))
 # v3 dispatch names/hashes the wrapped file. Do not substitute the older flat convention.
 require(dispatch['argumentsFile']==args_path.name and dispatch['argumentsSHA256']==sha(args_path),'Actual dispatch argument file/hash differs')
 for alias in ['native-arguments.json','native-call-arguments.json','prepared-native-arguments.json']:
  if(packet/alias).exists():
   d=load(checked_file(packet,alias));require(d.get('arguments',d)==args,'Argument alias semantics differ')
 verify_stage75_receipts(b,prompt.read_bytes(),args,sha(args_path),dispatch,returned,packet)
 prereg_path=checked_file(root,b['preregistration'],b['preregistrationSHA256']);prereg=load(prereg_path)
 require(prereg_path.parent==packet and prereg['id']==NATIVE_EXPERIMENT,'Native preregistration differs')
 conditioning=verify_logical64_conditioning(packet,prereg,args,old_bank,root)
 adjud_path=checked_file(root,b['adjudication'],b['adjudicationSHA256']);adjud=load(adjud_path)
 require(adjud_path.parent==packet and adjud['nativeCallsReturned']==adjud['newNativeDrawings']==1
         and adjud.get('runtimeAdmission',False)is False,'Own native outcome count/admission differs')
 expected_adjud=[{'file':b['adjudication'],'sha256':sha(adjud_path),'nativeCallsReturned':1,'newNativeDrawings':1}]
 require(ledger['adjudications']==expected_adjud,'Do not synthesize a native adjudication for deterministic Crow')
 manifest_path=checked_file(root,b['manifest'],b['manifestSHA256']);manifest=load(manifest_path)
 require(manifest_path.parent==packet and manifest['batchId']==b['batchId']and manifest['nativeCalls']==1
         and len(manifest['frames'])==len(b['frames'])==1,'PRIMARY native count/batch differs')
 require(manifest['frames'][0]['speciesId']=='bushtit','Wrong native species')
 require(checked_file(packet,manifest['original'],manifest['originalSHA256'])==orig
         and checked_file(packet,manifest['prompt'],manifest['promptSHA256'])==prompt,'PRIMARY input binding differs')
 src=b['frames'][0];decl=manifest['frames'][0];src_path=checked_file(root,src['sourcePNG'],src['sourcePNGsha256']);src_im=rgba(src_path)
 ident=frame_id(src_im);rect=legacy['native_rect'](src);dr=legacy['native_rect'](decl,[0,0,*im.size])
 require(ident==src['sourceFrameId']==decl['sourceFrameId']==f['frameId']and ident not in old_ids
         and checked_file(packet,decl['sourcePNG'],decl['sourcePNGsha256'])==src_path
         and src['dimensions']==[1254,1254]and src_im.size==im.size==(1254,1254)and src_im.tobytes()==im.tobytes()
         and rect==dr==[0,0,1254,1254],'Only the whole native original is a new primary, never a64 patch derivative')
 require(f['file']==src['sourcePNG']and f['fileSha256']==src['sourcePNGsha256']and f['sourceAtlas']==b['original']
         and f['sourceAtlasSha256']==b['originalSHA256']and f['sourcePrompt']==b['prompt']
         and f['sourceNativeArguments']==b['nativeArguments']and f['appearanceVersion']==b['batchId']
         and f['species']=='bushtit'and f['sourceReview']==b['adjudication']
         and f['sourceReviewSHA256']==sha(adjud_path),'New bank provenance differs')
 require(legacy['native_rect'](f['derivation'])==rect and f['derivation']['registrationOnly']is True
         and f['derivation']['perFrameRescale']is False and f['anatomyScaleAccepted']is False
         and f['rootContactAccepted']is False and f['runtimeAdmission']is False,'New record grants authority or changes source')
 require(returned['sourceFrameId']==ident,'Return primary ID differs')
 require(item['batch']==b['batchId']and item['file']==b['original']and item['sha256']==b['originalSHA256']
         and item['promptFile']==b['prompt']and item['promptSha256']==b['promptSHA256']
         and item['sourceReviewFile']==b['adjudication']and item['sourceReviewSha256']==sha(adjud_path)
         and item['acceptedProductionArt']is False and item['stagedInMac']is False
         and item['integratedInMac']is False,'New inventory record authority/provenance differs')
 seals=[verify_packet_seal(root,NATIVE_PACKET)]
 # The second outcome is explicitly zero-native, not a second original or source record.
 zero=ledger['zeroNativeExperiments'];require(len(zero)==1,'Exactly one zero-native Crow outcome expected')
 z=zero[0];require(z['packetDirectory']==ZERO_PACKET,'Wrong deterministic packet')
 zp=inside(root,ZERO_PACKET);zpr=checked_file(root,z['preregistration'],z['preregistrationSHA256']);zpre=load(zpr)
 za=checked_file(root,z['adjudication'],z['adjudicationSHA256']);zad=load(za)
 zm=checked_file(root,z['manifest'],z['manifestSHA256']);zman=load(zm)
 require(zpr.parent==za.parent==zm.parent==zp and zpre.get('batchId')=='crow-attention-selected-ground-palette-v1','Zero-native references belong to another packet')
 require(zad['nativeCallsReturned']==zad['newNativeDrawings']==0,'Zero-native Crow outcome counted native art')
 require(zman['nativeCalls']==0 and zman['frames']==[],'Deterministic PRIMARY cannot add native frames')
 reused=zman['reusedFrames'];require(len(reused)==3,'Actual Crow packet retains exactly neutral/blink/look existing native sources')
 require(set(z['reusedSourceFrameIDs'])=={v['sourceFrameId']for v in reused}and set(z['reusedSourceFrameIDs'])<=old_ids,'Crow reused sources differ from old bank')
 for r in reused:
  p=checked_file(zp,r['sourcePNG'],r['sourcePNGsha256']);require(frame_id(rgba(p))==r['sourceFrameId'],'Zero-native reused PNG identity differs')
 require(zad.get('runtimeAdmission',False)is False,'Zero-native source outcome cannot admit runtime')
 seals.append(verify_packet_seal(root,ZERO_PACKET))
 old_lessons=load(baseline/'lessons-and-experiments.json');lessons=load(checked_file(root,'lessons-and-experiments.json'))
 require(len(old_lessons['experiments'])==25 and len(lessons['experiments'])==27
         and lessons['experiments'][:25]==old_lessons['experiments']
         and {x['id']for x in lessons['experiments'][25:]}=={NATIVE_EXPERIMENT,z['experimentId']}
         and len({x['id']for x in lessons['experiments']})==27
         and {k:v for k,v in lessons.items()if k!='experiments'}=={k:v for k,v in old_lessons.items()if k!='experiments'},'Public registry prefix changed or duplicated outcomes')
 require(ledger['activeInventorySHA256']==ACTIVE_SHA256,'Active inventory ledger pin changed');checked_file(root,ACTIVE,ACTIVE_SHA256)
 overlay=load(checked_file(root,OVERLAY));old_overlay=load(baseline/'intake-overlay.json')
 changed={'registeredDrawings','registeredOriginals','newSourceRegistration','sourceRegistrationNote','newDrawings','newNativeCalls'}
 require(all(overlay.get(k)==v for k,v in old_overlay.items()if k not in changed),'Old overlay metadata changed')
 require(overlay['newDrawings']==old_overlay['newDrawings']+1 and overlay['newNativeCalls']==old_overlay['newNativeCalls']+1
         and overlay['registeredDrawings']==190 and overlay['registeredOriginals']==73
         and overlay['newSourceRegistration']==LEDGER,'Overlay counted deterministic derivative as generated art')
 prior=prior_bytes(root,baseline,ledger);reports=safe_new_reports(root);history=historical_stage69(root,baseline)
 return {'passed':True,'stage':75,'totalBankDrawingIDs':190,'totalOriginalPromptPairs':73,
         'newNativeDrawings':1,'newNativeOriginals':1,'zeroNativeExperimentCount':1,
         'registrationOnlyNativeDrawings':history['result']['registrationOnlyNativeDrawings']+1,
         'registrationOnlyNativeOriginals':history['result']['registrationOnlyNativeOriginals']+1,
         'conditioning':conditioning,'old189And72PrefixesExact':True,'old25ExperimentPrefixExact':True,
         'activeInventoryUnchanged':True,'acceptedUsesAdded':0,'registrationMakesNativeCalls':0,
         'packetSeals':seals,'priorSourceIndex':prior,'newReports':reports,'historicalStage69':history,
         'sourceAppearanceOrSupportApproved':False,'runtimeAdmission':False}

if __name__=='__main__':
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--root',type=Path,default=Path(__file__).parent);args=parser.parse_args()
 try:print(json.dumps(verify(args.root),sort_keys=True))
 except (VerificationError,OSError,ValueError,KeyError,TypeError)as e:
  print(json.dumps({'passed':False,'error':str(e),'runtimeAdmission':False}),file=sys.stderr);raise SystemExit(1)
