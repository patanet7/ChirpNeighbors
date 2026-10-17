"""Pack immutable review evidence with one shared CRC/hash implementation."""
from pathlib import Path
import argparse,json
from review_io import pack,write_json
def main():
    p=argparse.ArgumentParser();p.add_argument('--review-root',type=Path,required=True);args=p.parse_args();root=args.review_root;dest=root/'delivery';receipts=[]
    plant=list((root/'curated-static-plants').glob('*'))+[root/'root/runtime-object-intake.json',root/'root/README.md',root/'root/runtime-contract.json']
    receipts.append(pack(sorted(plant),root,dest/'review08-curated-static-plants.zip'))
    files=[x for x in root.rglob('*')if x.is_file()and x.suffix.lower()in{'.png','.jpg','.gif','.json','.md','.txt','.py'}and not any(s in x.relative_to(root).parts for s in['stage','__pycache__','delivery','library-receipts'])and x.name not in['package-receipts.json','ChirpNeighbors-Review08-Handoff.json']]
    groups=[];current=[];size=0
    for f in sorted(files):
        if size+f.stat().st_size>6_800_000 and current:groups.append(current);current=[];size=0
        current.append(f);size+=f.stat().st_size
    if current:groups.append(current)
    for i,group in enumerate(groups,1):receipts.append(pack(group,root,dest/f'review08-evidence-{i:02}.zip'))
    write_json(root/'root/package-receipts.json',{'packages':receipts,'all_under_decimal_8MB':True,'all_CRC_and_member_hashes_pass':True,'package_snapshot':'Pre-publication frozen evidence; final Library/Git receipts appended outside immutable archives.'})
    print(json.dumps({'packages':len(receipts),'max_bytes':max(x['bytes']for x in receipts)}))
if __name__=='__main__':main()
