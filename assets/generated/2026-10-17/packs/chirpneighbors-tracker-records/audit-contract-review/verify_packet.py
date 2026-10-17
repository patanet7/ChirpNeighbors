"""Packet/reference integrity only. No renderer, physics, or canonical acceptance validator."""
from pathlib import Path
import argparse,json,hashlib
ap=argparse.ArgumentParser();ap.add_argument('--asset-root',type=Path);ap.add_argument('--structural-only',action='store_true');args=ap.parse_args();A=Path(__file__).parent;R=args.asset_root or A.parent
read=lambda n:json.loads((A/n).read_text())
p=read('interface-proposal.json');f=read('acceptance-fixtures.json');r=read('frame-reference-projection.json');lessons=read('generation-lessons.json');evidence=read('source-evidence-index.json');checks=[]
def check(name,condition):
 checks.append({'name':name,'passed':bool(condition)})
 if not condition:raise AssertionError(name)
check('proposal explicitly unagreed/non-runtime and frozen',p['status']=='UNAGREED_PROPOSAL_NOT_RUNTIME_INPUT' and p['implementationFrozen'] and not p['runtimeChangesAuthorizedByThisPacket'])
groups={x['group'] for x in p['requiredFieldGroups']};check('seven unique field groups/questions',len(groups)==7 and len({x['id'] for x in p['minimalQuestions']})==7)
cases={x['id']:x for x in f['fixtures']};check('eleven unique static acceptance fixtures',len(cases)==11 and f['notRuntimeConfig'])
check('question evidence/group references resolve',all(all(i in cases for i in q['evidence']) and all(g in groups for g in q['groups']) for q in p['minimalQuestions']))
refs=r['references'];check('all fixture frame references resolve',len(refs)==5 and all(k in refs for c in cases.values() for k in c['frameRefs']))
check('no canonical frame identity invented',all(x['canonicalFrameId'] is None for x in refs.values()))
check('external crow evidence remains explicitly unbound/manual',not cases['F08']['frameRefs'] and cases['F08']['externalEvidence']['canonicalFrameBindings'] is None and cases['F08']['expected']['localAutomatedWorldContactConformance'].startswith('blocked_'))
check('qualitative perch grip not promoted',not cases['F04']['expected']['acceptedPerchedClip'] and cases['F04']['expected']['registeredPerchReuse']=='withhold')
check('declared diagnostic affine values internally consistent',cases['F05']['expected']['reviewSupportRoot']==[v*cases['F05']['given']['declaredUniformReviewScale'] for v in cases['F05']['given']['sourceSupportRoot']])
check('mirror convention intentionally unresolved',cases['F06']['expected']['admission']=='withhold' and cases['F06']['given']['pixelCenterOrEdgeConvention'] is None)
check('no implicit semantic event transfer',cases['F11']['expected']['implicitConsumptionFromFrameIdentity'] is False)
check('twelve failure classes retain evidence scope',len(lessons['failureClasses'])==12 and all(c['scope'] and c['next'] for c in lessons['failureClasses']))
if not args.structural_only:
 from PIL import Image
 bank=json.loads((R/'frame-bank.json').read_text());index={x['frameId']:x for x in bank['frames']}
 check('source frame register digest matches projection',hashlib.sha256((R/'frame-bank.json').read_bytes()).hexdigest()==r['sourceFrameBankSha256'])
 for name,x in refs.items():
  source=R/x['file'];check(name+' file digest resolves',source.exists() and hashlib.sha256(source.read_bytes()).hexdigest()==x['fileSha256']);im=Image.open(source).convert('RGBA');identity='frame.sha256.'+hashlib.sha256(f'RGBA8;{im.width}x{im.height};'.encode()+im.tobytes()).hexdigest();check(name+' pixel identity/dimensions resolve',identity==x['productionFrameId'] and list(im.size)==x['nativeCanvas'] and identity in index)
 check('nine cited local evidence digests match',all((R/path).is_file() and hashlib.sha256((R/path).read_bytes()).hexdigest()==meta['sha256'] for path,meta in evidence['sourceFiles'].items()))
receipt={'passed':all(c['passed'] for c in checks),'checks':checks,'sourcePixelResolution':'not_run' if args.structural_only else 'verified_local_files','canonicalRuntimeConformanceRun':False,'biomechanicalOrArtAcceptance':False,'rendererOrPhysicsImplemented':False};(A/'packet-integrity-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
