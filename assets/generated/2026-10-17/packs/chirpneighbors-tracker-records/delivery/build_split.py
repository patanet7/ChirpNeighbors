from pathlib import Path
import gzip,base64,json,re,zipfile,hashlib
R=Path('/workspace/asset-production');D=R/'delivery';q=json.loads((R/'queue.json').read_text())
for b in q['batches']:
 if b.get('manifestFile') and (R/b['manifestFile']).exists():b['manifestData']=json.loads((R/b['manifestFile']).read_text())
 if b.get('previewFile') and (R/b['previewFile']).exists():b['previewEmbeddedData']='data:image/gif;base64,'+base64.b64encode((R/b['previewFile']).read_bytes()).decode()
s=(R/'tracker.html').read_text();encoded=base64.b64encode(gzip.compress(json.dumps(q,separators=(',',':')).encode(),compresslevel=9)).decode();s=re.sub(r'<script id="queue-data" type="application/json">.*?</script>','<script id="queue-data" type="application/octet-stream">'+encoded+'</script>',s,flags=re.S);s=s.replace("const q=JSON.parse(document.getElementById('queue-data').textContent)","(async()=>{const bytes=Uint8Array.from(atob(document.getElementById('queue-data').textContent),c=>c.charCodeAt(0));const stream=new Blob([bytes]).stream().pipeThrough(new DecompressionStream('gzip'));const q=JSON.parse(await new Response(stream).text())")
s=s.replace('src="${esc(b.previewFile)}"','src="${esc(b.previewEmbeddedData||b.previewFile)}"');s=s.replace('draw();\n</script>','draw();})();\n</script>');(D/'ChirpNeighbors-Production-Tracker.html').write_text(s)
meta=[]
def pack(out,files):
 with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
  for f in files:z.write(f,f.relative_to(R))
 meta.append({'file':str(out),'bytes':out.stat().st_size,'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'files':len(files)})
for name in ['dove-walk-v1','dove-drink-v1','understory-wind-v1','rain-layer-v1','rain-continuity-v2']:
 out=D/('ChirpNeighbors-'+name+'.zip')
 if not out.exists():pack(out,[p for p in sorted((R/'batches'/name).rglob('*')) if p.is_file()])
 else:meta.append({'file':str(out),'bytes':out.stat().st_size,'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'preservedPriorSourcePack':True})
# Checkpoint all current source/docs/receipts and current manifests. Existing
# binary packs stay immutable; include the two previously unpackaged inspections.
files=sorted({p for p in R.iterdir() if p.is_file() and p.suffix in {'.json','.py','.md','.txt'}} | {p for folder in ['receipts','audit-contract-review'] for p in (R/folder).rglob('*') if p.is_file()} | {p for p in (R/'batches').rglob('*') if p.is_file() and p.suffix in {'.json','.txt','.md','.svg'}} | {p for p in D.iterdir() if p.is_file() and p.suffix in {'.py','.json'}} | {R/'batches/house-finch-canon-v1/female-inspection.png',R/'batches/house-finch-canon-v1/male-inspection.png'})
pack(D/'ChirpNeighbors-Tracker-Records.zip',files)
meta.insert(0,{'file':str(D/'ChirpNeighbors-Production-Tracker.html'),'bytes':(D/'ChirpNeighbors-Production-Tracker.html').stat().st_size,'sha256':hashlib.sha256((D/'ChirpNeighbors-Production-Tracker.html').read_bytes()).hexdigest()})
(D/'split-delivery-index.json').write_text(json.dumps({'combinedArchivePreserved':str(R/'chirp-visible-production-and-tracker-20261017.zip'),'combinedSha256':'dd7d9ffdbb47c53513dc66ef6991ffd8ce390f1ecac9fedbb24f2fc28172845d','items':meta},indent=2)+'\n');print(json.dumps(meta))
