"""Split delivery only. Preserve parent source files; do not generate or repaint art."""
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
import json,hashlib,zipfile,copy
ROOT=Path(__file__).resolve().parent.parent
OUT=Path(__file__).resolve().parent
LIMIT=8_000_000

def digest(b):return hashlib.sha256(b).hexdigest()
def js(d):return (json.dumps(d,indent=2)+'\n').encode()
def read(rel):return (ROOT/rel).read_bytes()
def crop_preview(rel,sheet):
 import io
 im=Image.open(ROOT/rel)
 row=im.crop((0,(sheet-1)*460,1600,sheet*460))
 buf=io.BytesIO();row.save(buf,format='PNG');return buf.getvalue()

def archive(name,members,extra):
 records=[{'path':k,'sha256':digest(v),'bytes':len(v)} for k,v in sorted(members.items())]
 members['package-members.sha256.json']=js({'schema_version':'1.0.0','members':records,'scope':'All payload files except hash manifest and SHA256SUMS, which mutually cannot hash themselves'})
 members['SHA256SUMS']=''.join(f"{digest(v)}  {k}\n" for k,v in sorted(members.items())).encode()
 dst=OUT/name
 with zipfile.ZipFile(dst,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
  for path,data in sorted(members.items()):
   zi=zipfile.ZipInfo(path,date_time=(2026,10,17,16,0,0));zi.compress_type=zipfile.ZIP_DEFLATED;zi.external_attr=0o100644<<16
   z.writestr(zi,data,compresslevel=9)
 assert dst.stat().st_size<=LIMIT,(name,dst.stat().st_size)
 with zipfile.ZipFile(dst) as z:
  assert z.testzip() is None
  assert sorted(z.namelist())==sorted(members)
  for path,data in members.items():assert digest(z.read(path))==digest(data),(name,path)
  checks=z.read('SHA256SUMS').decode().splitlines()
  for line in checks:
   wanted,path=line.split('  ',1);assert digest(z.read(path))==wanted
 receipt={'archive':name,'sha256':digest(dst.read_bytes()),'bytes':dst.stat().st_size,'limit_bytes':LIMIT,'members_verified':len(members),'zip_crc_passed':True,'all_member_hashes_verified':True,**extra,'members':[{'path':k,'sha256':digest(v),'bytes':len(v)} for k,v in sorted(members.items())]}
 (OUT/(name+'.receipt.json')).write_bytes(js(receipt))
 return receipt

baseline={str(p.relative_to(ROOT)):digest(p.read_bytes()) for p in ROOT.rglob('*') if p.is_file() and OUT not in p.parents}
manifest=json.loads(read('manifest.json'))
extraction=json.loads(read('extraction-report.json'))
review=json.loads(read('review-receipt.json'))
receipts=[]
for sheet in range(1,4):
 m=copy.deepcopy(manifest);m['assets']=[a for a in m['assets'] if a['target_sheet']==sheet]
 ids=[a['asset_id'] for a in m['assets']];assert len(ids)==4
 m['original_generator_paths']=[m['original_generator_paths'][sheet-1]]
 m['scope']=f'Four-object sheet-{sheet} independently usable intake subset of CN-SD-OBJECTS-20261017-01; merge by preserved asset/variant IDs, not a replacement tracker'
 m['delivery_subset']={'sheet':sheet,'asset_count':4,'parent_asset_count':12,'transport_only':True,'main_batch_source_unchanged':True,'preview_note':'Contact sheets in this package are exact rectangular row crops of main contact-sheet composites; art is unchanged.'}
 # Main paths remain valid because package preserves original relative file names.
 members={'manifest.json':js(m),f'originals/sheet-{sheet}.png':read(f'originals/sheet-{sheet}.png'),f'prompts/sheet-{sheet}.txt':read(f'prompts/sheet-{sheet}.txt')}
 for a in m['assets']:
  for deriv in a['derivatives']:
   p=deriv['file'];members[p]=read(p);assert digest(members[p])==deriv['sha256']
  assert digest(members[f'originals/sheet-{sheet}.png'])==a['generation']['original_hashes'][0]
  assert members[f'prompts/sheet-{sheet}.txt'].decode().removesuffix('\n')==a['generation']['prompt_exact']
 for p in ['canonical-intake.json','intake-policy.json']:
  if (ROOT/p).exists():members[p]=read(p)
 er=[r for r in extraction if r['asset_id'] in ids]
 members['extraction-report.json']=js(er)
 rev=copy.deepcopy(review);rev['assets']=[r for r in rev['assets'] if r['asset_id'] in ids];rev['delivery_subset_sheet']=sheet;members['review-receipt.json']=js(rev)
 for name in ['sheet','light','dark']:
  p=f'previews/object-contact-{name}.png';members[p]=crop_preview(p,sheet)
 members['README.md']=(f'''# ChirpNeighbors objects — sheet {sheet} of 3\n\nFour complete static candidate objects, with exact original source-sheet PNG bytes, four native-alpha sprite PNGs, exact generation prompt, filtered final intake manifest, provenance/rights and placement/interaction/state metadata, technical/visual review receipts, and three four-object contact previews.\n\nAsset IDs: {', '.join(ids)}.\n\nThis is an independently usable transport subset of the established batch. Asset and variant IDs are preserved. `manifest.json` is the subset intake delta for the existing canonical ledger. Original PNG, prompt and sprite bytes are unchanged; preview PNGs are rectangular crops of existing review contact sheets. No new art generation, alpha removal, repainting or color keying occurred.\n\nGenerated and scoped-reviewed static candidates only. Strict pixel-grid/style acceptance, nectar appearance realism where applicable, reference-pixel comparison, runtime alignment and owner acceptance remain pending. Layers, state slots, wind and functional contacts are metadata; no animation, physics or independent production-layer implementation is claimed. Earlier reference ZIP pixel inspection was blocked by HTTP 403. License fields remain explicit unknowns where not established.\n\nCanonical intake remains `pending_mac_verification`; no Git or Mac application edits. `SHA256SUMS` verifies every payload file plus the machine-readable package-member hash manifest. Archive receipts separately verify all ZIP members, CRC, byte-exact source retention and size.\n''').encode()
 extra={'sheet':sheet,'asset_ids':ids,'assets':4,'source_png_byte_preserved':True,'exact_prompt_byte_preserved':True,'sprite_png_bytes_preserved':True,'canonical_intake':'pending_mac_verification','commit':None,'remote_sha':None,'original_source_sha256':digest(members[f'originals/sheet-{sheet}.png'])}
 receipts.append(archive(f'chirp-functional-objects-sheet-{sheet}-20261017.zip',members,extra))

metadata={}
for rel in ['README.md','INVENTORY.md','inventory.json','manifest.json','extraction-report.json','review-receipt.json','validation-receipt.json','process_sheets.py','finalize_manifest.py','WORKSTREAM.md','canonical-intake.json','intake-policy.json','hashes.json','SHA256SUMS']:
 if (ROOT/rel).exists():metadata['main-batch-reference/'+rel]=read(rel)
metadata['split-delivery/build_small_delivery.py']=Path(__file__).read_bytes()
metadata['README.md']=b'# ChirpNeighbors object metadata and source scripts\n\nReference copies of complete main-batch metadata and extraction/finalization scripts. Art bytes live in the three independently usable sheet packages. Main-batch-reference hashes describe the unmodified main batch and do not describe this metadata-only archive. No Git or application change is included. Canonical intake remains pending_mac_verification.\n'
receipts.append(archive('chirp-functional-objects-metadata-scripts-20261017.zip',metadata,{'package_kind':'metadata_and_source_scripts','canonical_intake':'pending_mac_verification','commit':None,'remote_sha':None}))
for rel,wanted in baseline.items():assert digest(read(rel))==wanted,('main_batch_modified',rel)
summary={'created_at':datetime.now(timezone.utc).isoformat(),'status':'passed','main_batch_files_unchanged':True,'main_batch_files_checked':len(baseline),'all_archives_under_8_decimal_MB':True,'all_archive_member_hashes_verified':True,'actual_art_generation_performed':False,'canonical_intake':'pending_mac_verification','commit':None,'remote_sha':None,'packages':[{k:v for k,v in r.items() if k!='members'} for r in receipts],'lightweight_preview_direct_paths':[str(ROOT/'previews'/f'object-contact-{n}.png') for n in ['sheet','light','dark']]}
(OUT/'delivery-receipts.json').write_bytes(js(summary))
print(json.dumps(summary,indent=2))
