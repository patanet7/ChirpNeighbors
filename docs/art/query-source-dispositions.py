#!/usr/bin/env python3
"""Read-only query of the existing, hash-pinned 133-packet public projection."""
import argparse,collections,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/"docs/delivery/generated-source-evidence-20261017/cloud-producer/reports/qualification-continuation-20261018/133-packet-actionable-summary.json"
EXPECTED_BLOB="2d20609bec20c69e142a46bfad82c947b7d709e3"
def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--partition',choices=['all','blocked','reject','repair','reuse'],default='all')
    ap.add_argument('--packet',help='Exact packet path, not a fuzzy search')
    ap.add_argument('--rows',action='store_true')
    a=ap.parse_args()
    raw=SOURCE.read_bytes()
    actual=hashlib.sha1(('blob '+str(len(raw))+'\0').encode()+raw).hexdigest()
    if actual!=EXPECTED_BLOB:
        raise ValueError('Projection changed; use the source pinned in the ledger, not a guessed replacement')
    d=json.loads(raw)
    if len(d['rows'])!=133:
        raise ValueError('Expected exactly 133 original projection rows')
    lookup={'blocked':'BLOCKED','reject':'REJECT','repair':'REPAIR_OR_ADJUDICATE','reuse':'REUSE'}
    rows=[x for x in d['rows'] if (a.partition=='all' or x['primaryHandling']==lookup[a.partition]) and (not a.packet or x['packet']==a.packet)]
    if a.packet and not rows:
        raise ValueError('No exact matching packet in this partition')
    out={'source':str(SOURCE.relative_to(ROOT)),'sourceGitBlobSHA':actual,'count':len(rows),'partitions':dict(collections.Counter(x['primaryHandling'] for x in rows))}
    if a.rows:
        out['rows']=rows
    print(json.dumps(out,indent=2,ensure_ascii=False))
if __name__=='__main__':
    main()
