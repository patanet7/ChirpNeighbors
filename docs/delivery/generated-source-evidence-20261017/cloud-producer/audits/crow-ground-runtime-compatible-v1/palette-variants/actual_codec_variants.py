from pathlib import Path
import json,hashlib,subprocess
P=Path(__file__).parent;A=P.parent/'runtime-v3-adapter';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r=json.loads((P/'codec-evaluation.json').read_text());results=[]
for row in r['rows']:
 out=subprocess.run(['node','--experimental-strip-types',str(A/'codec-check.mjs'),str((P/row['file']).resolve())],capture_output=True,text=True)
 x=json.loads(out.stdout);assert x['passed']==row['actualStrictLocalCodecPass'] and out.returncode==(0 if x['passed'] else 1)
 if x['passed']:assert x['rectangles']==row['rectangleCount']
 results.append({'file':row['file'],'totalColors':row['actualRGBAColors'],'diagnosticRectangleCount':row['rectangleCount'],'actualCodecReceipt':x})
chosen=next(x for x in results if x['actualCodecReceipt']['passed'])
assert chosen['file']=='crow-ground-idle186-total12.png'
out=subprocess.run(['node','--experimental-strip-types',str(A/'codec-check.mjs'),str(P/chosen['file']),'--descriptor',str(P/'chosen-pixel-rect-fields.partial.json')],capture_output=True,text=True,check=True);descriptor=json.loads(out.stdout)
receipt={'status':'PASS chosen exact actual-dependency codec','harness':'../runtime-v3-adapter/codec-check.mjs','harnessSHA256':sha(A/'codec-check.mjs'),'exactExtractedCodecSHA256':sha(A/'exact-runtime-codec.ts'),'sourceFunctionBodyHashes':'../runtime-v3-adapter/codec-extraction-receipt.json','allEvaluated':results,'chosen':chosen['file'],'chosenTotalColors':12,'chosenRectangleCount':4021,'selection':'Highest actual passing total-color count among authorized evaluated56,48,40,32,24,16 and all15..2;13 is4141FAIL,12 is4021PASS','descriptorReceipt':descriptor,'fullManifestValidation':False,'currentMacAdmission':False,'productionPinsAndFidelityLabels':'UNSUPPLIED'}
(P/'actual-codec-evaluation.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({'chosen':chosen['file'],'count':4021,'partialDescriptorSHA256':sha(P/'chosen-pixel-rect-fields.partial.json')}))
