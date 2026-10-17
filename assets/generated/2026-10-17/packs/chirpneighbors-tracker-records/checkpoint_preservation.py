"""Index existing delivery ZIP bytes and current source coverage; no generation."""
from pathlib import Path
import json,hashlib,zipfile,datetime,platform,sys
R=Path(__file__).parent;D=R/'delivery'
sha=lambda b:hashlib.sha256(b).hexdigest()
receipt=json.loads((R/'receipts/preservation-library-metadata.json').read_text())
metadata={x['name']:x for x in receipt['existing']}
a=receipt['auditCreate'];metadata[a['file_name']]={'library_file_id':a['library_file_id'],'size_bytes':a['file_size_bytes'],'version_id':str(a['current_version_number'])}
covered={};deliveries=[]
for p in sorted(D.iterdir()):
 if p.name not in metadata:continue
 m=metadata[p.name];item={'file':str(p.relative_to(R)),'libraryFileId':m['library_file_id'],'libraryVersionAtRead':m.get('version_id'),'bytes':p.stat().st_size,'sha256':sha(p.read_bytes()),'libraryMetadataSizeMatchesLocal':m['size_bytes']==p.stat().st_size,'remoteBytesReDownloaded':False}
 if p.name in {'ChirpNeighbors-Tracker-Records.zip','ChirpNeighbors-Production-Tracker.html'}:
  item={'file':str(p.relative_to(R)),'libraryFileId':m['library_file_id'],'priorVersionAtRead':m.get('version_id'),'checkpointReplacement':'pending final Library write/read receipt outside this self-referential records archive','remoteBytesReDownloaded':False}
 if p.suffix=='.zip':
  with zipfile.ZipFile(p) as z:
   assert z.testzip() is None,p
   if 'checkpointReplacement' not in item:item['zipMembers']=len(z.namelist())
   for n in z.namelist():covered.setdefault(n,[]).append({'archive':p.name,'sha256':sha(z.read(n))})
 deliveries.append(item)
files=[]
for folder in ['batches','frames','receipts','audit-contract-review']:
 for p in sorted((R/folder).rglob('*')):
  if not p.is_file():continue
  rel=str(p.relative_to(R));h=sha(p.read_bytes());matches=[x['archive'] for x in covered.get(rel,[]) if x['sha256']==h]
  files.append({'file':rel,'bytes':p.stat().st_size,'sha256':h,'coveredByArchives':matches})
inventory={'scope':'current asset/prompt/manifest/derived/review files; producer source/docs are in Tracker Records','files':files,'uncovered':[x['file'] for x in files if not x['coveredByArchives']]}
(R/'preservation-file-inventory.json').write_text(json.dumps(inventory,indent=2)+'\n')
q=json.loads((R/'queue.json').read_text())
summary={'createdAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'executionEnvironment':{'platform':platform.platform(),'python':sys.version.split()[0],'cwd':'/workspace','assetRoot':str(R),'Mac':False},'operationalQueue':'queue.json','stateSummary':q['preservationCheckpoint'],'auditPacket':q['auditCoordination']['packet'],'deliveries':deliveries,'coverage':{'indexedFiles':len(files),'uncovered':inventory['uncovered'],'remoteByteHashVerification':False,'localZipCRCAndMemberHashesVerified':True},'verificationBoundary':'Library existence/size read plus successful uploads; local files and ZIP members hashed. No claim of remote byte re-download, Mac staging, runtime conformance, art or biological acceptance.','nextSteps':q['preservationCheckpoint']['nextSteps']}
(R/'preservation-checkpoint.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps({'deliveries':len(deliveries),'indexedFiles':len(files),'uncovered':inventory['uncovered'],'sizeMismatches':[x['file'] for x in deliveries if x.get('libraryMetadataSizeMatchesLocal') is False]}))
