from pathlib import Path
import json,hashlib,zipfile,argparse
P=Path(__file__).parent;arg=argparse.ArgumentParser();arg.add_argument('--expected-review-sha256',required=True);arg.add_argument('--expected-review-md-sha256',required=True);args=arg.parse_args();sha=lambda b:hashlib.sha256(b).hexdigest();review=P/'independent-review.json';review_md=P/'independent-review.md';assert review.is_file(),'Independent source review required before sealing';assert sha(review.read_bytes())==args.expected_review_sha256,'Review changed after coordinator-supplied final hash';assert sha(review_md.read_bytes())==args.expected_review_md_sha256,'Review MD changed after coordinator-supplied final hash';j=json.loads(review.read_text());primary_before=sha((P/'PRIMARY-SOURCE-MANIFEST.json').read_bytes())
def inspect(o,path='review'):
 if isinstance(o,dict):
  for k,v in o.items():
   assert not (isinstance(v,str) and ('base64' in k.lower() or v.startswith('data:image/'))),'Embedded image payload forbidden: '+path+'.'+k
   inspect(v,path+'.'+k)
 elif isinstance(o,list):
  for i,v in enumerate(o):inspect(v,path+f'[{i}]')
inspect(j)
seal={'independentReview':'independent-review.json','independentReviewSHA256':args.expected_review_sha256,'independentReviewMD':'independent-review.md','independentReviewMDSHA256':args.expected_review_md_sha256,'reviewedPrimaryManifestSHA256':primary_before,'sourceScope':'inclined-trunk-source-candidate; vertical unresolved; actual Mac contact not verified','noNewGenerationAfterReview':True,'browserCapturesIncluded':False,'reviewedArtManifestPromptAndDocumentationRewritten':False,'statusAuthority':'Final review files and this additive seal supersede pre-review pending status text in frozen source documentation.'};(P/'review-seal.json').write_text(json.dumps(seal,indent=2)+'\n')
status=json.loads((P/'status.json').read_text());status.update(state='independently source-reviewed; staged portable source artifact; no generation running',independentReviewSHA256=args.expected_review_sha256,running=False,nextQueued='Hold; coordinator decides support binding or a separately authorized next repair. No automatic retry.');(P/'status.json').write_text(json.dumps(status,indent=2)+'\n')
zipname='ChirpNeighbors-Nuttall-Inclined-Support-Study.zip';excluded={'source-files.sha256.json',zipname,'library-receipt.json','delivery.json'}
files=sorted(f for f in P.rglob('*') if f.is_file() and f.name not in excluded and not f.name.startswith('library-') and 'internal-browser' not in f.parts and '__pycache__' not in f.parts)
for f in files:
 if f.suffix=='.json':inspect(json.loads(f.read_text()),str(f.relative_to(P)))
index={'independentReviewSHA256':args.expected_review_sha256,'independentReviewMDSHA256':args.expected_review_md_sha256,'files':[{'path':str(f.relative_to(P)),'bytes':f.stat().st_size,'sha256':sha(f.read_bytes())} for f in files]};(P/'source-files.sha256.json').write_text(json.dumps(index,indent=2)+'\n')
z=P/zipname
with zipfile.ZipFile(z,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as archive:
 for f in files+[P/'source-files.sha256.json']:archive.write(f,str(f.relative_to(P)))
assert sha(review.read_bytes())==args.expected_review_sha256 and sha(review_md.read_bytes())==args.expected_review_md_sha256 and sha((P/'PRIMARY-SOURCE-MANIFEST.json').read_bytes())==primary_before
receipt={'zip':str(z),'bytes':z.stat().st_size,'sha256':sha(z.read_bytes()),'indexedFiles':len(files),'zipFiles':len(files)+1,'finalIndependentReviewSHA256':args.expected_review_sha256,'finalIndependentReviewMDSHA256':args.expected_review_md_sha256,'reviewedPrimaryManifestSHA256Unchanged':primary_before,'nativeCalls':1,'newDrawings':2,'noBrowserCapturesOrEmbeddedBase64':True,'appBound':False};(P/'delivery.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
