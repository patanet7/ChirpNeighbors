from pathlib import Path
from PIL import Image
import json,zipfile,hashlib
R=Path('/workspace/asset-production');D=R/'delivery';bank=json.loads((R/'frame-bank.json').read_text());all_records={f['frameId']:f for f in bank['frames']};deliveries=[]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def package(name,files,projection):
 out=D/('ChirpNeighbors-'+name+'.zip')
 with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
  for f in files:z.write(f,f.relative_to(R))
  z.writestr('frame-bank.json',json.dumps(projection,indent=2)+'\n')
  z.writestr('PACK-SHA256SUMS.txt','\n'.join(sha(f)+'  '+str(f.relative_to(R)) for f in files)+'\n')
 with zipfile.ZipFile(out) as z:assert z.testzip() is None
 deliveries.append({'batch':name,'file':str(out),'bytes':out.stat().st_size,'sha256':sha(out),'sourceFrameIds':[f['frameId'] for f in projection['frames']],'sourceRegistryFile':'frame-bank.json','sourceRegistrySha256':sha(R/'frame-bank.json')})
for sex in ['male','female']:
 for action in ['idle','feed']:
  name=f'house-finch-{sex}-{action}-v1';p=R/'batches'/name;m=json.loads((p/'manifest.json').read_text());records=[all_records[e['frameId']] for e in m['frames']];files=[f for f in sorted(p.rglob('*')) if f.is_file()]+[R/f['file'] for f in records]
  projection={'schemaVersion':1,'projectionOf':'local-production-frame-evidence@1','projectionOnly':True,'sourceRegistrySha256':sha(R/'frame-bank.json'),'frames':records,'verifiedReuseCount':0,'canonicalMacIds':'pending agreement; source frame pixel IDs are immutable'};package(name,files,projection)
p=R/'batches/house-finch-canon-v1';im=Image.open(p/'original.png').convert('RGBA');bg=Image.new('RGBA',im.size,(239,235,213,255));bg.alpha_composite(im);bg.resize((768,512),Image.Resampling.NEAREST).convert('RGB').save(p/'contact-sheet.png')
files=[p/x for x in ['original.png','male-source.png','female-source.png','contact-sheet.png','prompt.txt','manifest.json','reference-and-scale.json','generation-receipt.json']];records=[f for f in bank['frames'] if f.get('species')=='house_finch' and 'canonical-reference-only' in f.get('poseTags',[])];package('house-finch-canon-v1',files,{'schemaVersion':1,'projectionOf':'local-production-frame-evidence@1','sourceRegistrySha256':sha(R/'frame-bank.json'),'projectionOnly':True,'frames':records})
(D/'house-finch-delivery-index.json').write_text(json.dumps({'newGeneratedDrawings':26,'animatedDrawings':24,'referenceStills':2,'actualImageCalls':5,'acceptedClips':0,'staged':0,'integrated':0,'photoConditioned':False,'deliveries':deliveries},indent=2)+'\n');print(json.dumps(deliveries))
