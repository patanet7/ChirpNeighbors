from pathlib import Path
import json,hashlib,zipfile,argparse
P=Path(__file__).parent;arg=argparse.ArgumentParser();arg.add_argument('--expected-review-sha256',required=True);arg.add_argument('--expected-review-md-sha256',required=True);args=arg.parse_args();sha=lambda b:hashlib.sha256(b).hexdigest();r=P/'independent-review.json';md=P/'independent-review.md';assert r.exists() and md.exists(),'Final independent source review files required';assert sha(r.read_bytes())==args.expected_review_sha256;assert sha(md.read_bytes())==args.expected_review_md_sha256;primarysha=sha((P/'PRIMARY-SOURCE-MANIFEST.json').read_bytes())
def safe(o,path='review'):
 if isinstance(o,dict):
  for k,v in o.items():
   assert not(isinstance(v,str) and ('base64' in k.lower() or v.startswith('data:image/'))),'Image payload forbidden: '+path+'.'+k
   safe(v,path+'.'+k)
 elif isinstance(o,list):
  for i,v in enumerate(o):safe(v,path+f'[{i}]')
safe(json.loads(r.read_text()))
seal={'independentReview':'independent-review.json','independentReviewSHA256':args.expected_review_sha256,'independentReviewMD':'independent-review.md','independentReviewMDSHA256':args.expected_review_md_sha256,'reviewedPrimaryManifestSHA256':primarysha,'scope':'American Crow relaxed supported neutral/blink source candidate; same inherited charcoal individual intent; no locomotion/newcanon/appbinding or physics approval','reviewedArtManifestAndPromptRewritten':False,'sourceDocumentationStatus':'Final independent review and this additive seal supersede pre-review pending text in frozen producer documentation.','browserCapturesIncluded':False,'anotherNativeCall':False};(P/'review-seal.json').write_text(json.dumps(seal,indent=2)+'\n')
s=json.loads((P/'status.json').read_text());s.update(state='independent source review recorded; staged portable source artifact',independentReviewSHA256=args.expected_review_sha256,independentReviewMDSHA256=args.expected_review_md_sha256,running=False,nextQueued='Hold; coordinator decides admission/next common-first action. No automaticretry.');(P/'status.json').write_text(json.dumps(s,indent=2)+'\n')
zipname='ChirpNeighbors-Crow-Supported-Neutral-Blink.zip';excluded={zipname,'source-files.sha256.json','delivery.json'};files=sorted(f for f in P.rglob('*') if f.is_file() and f.name not in excluded and not f.name.startswith('library-') and 'internal-browser' not in f.parts and '__pycache__' not in f.parts)
for f in files:
 if f.suffix=='.json':safe(json.loads(f.read_text()),str(f.relative_to(P)))
index={'independentReviewSHA256':args.expected_review_sha256,'independentReviewMDSHA256':args.expected_review_md_sha256,'files':[{'path':str(f.relative_to(P)),'bytes':f.stat().st_size,'sha256':sha(f.read_bytes())} for f in files]};(P/'source-files.sha256.json').write_text(json.dumps(index,indent=2)+'\n');z=P/zipname
with zipfile.ZipFile(z,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as archive:
 for f in files+[P/'source-files.sha256.json']:archive.write(f,str(f.relative_to(P)))
assert sha(r.read_bytes())==args.expected_review_sha256 and sha(md.read_bytes())==args.expected_review_md_sha256 and sha((P/'PRIMARY-SOURCE-MANIFEST.json').read_bytes())==primarysha
out={'zip':str(z),'bytes':z.stat().st_size,'sha256':sha(z.read_bytes()),'indexedFiles':len(files),'zipFiles':len(files)+1,'finalIndependentReviewSHA256':args.expected_review_sha256,'finalIndependentReviewMDSHA256':args.expected_review_md_sha256,'reviewedPrimaryManifestSHA256Unchanged':primarysha,'nativeCalls':1,'newDrawings':2,'noBrowserCapturesOrEmbeddedBase64':True,'appBound':False};(P/'delivery.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
