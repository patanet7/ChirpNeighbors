"""Queries over a derived production snapshot, never over actual observations.
Usage: python3 query_gaps.py --pack san-diego --missing scale --limit 10
"""
from pathlib import Path
import json,argparse
def query(q,pack,missing):
 birds=q['regionalResearch']['birdRoster'];selected={b['id'] for b in birds if pack=='all' or (b['tier']=='first_complete_release' if pack=='san-diego' else b['tier']!='first_complete_release')}
 rows=[r for r in q['birdSlots'] if pack=='all' or r['species'] in selected]
 cards={c['species']:c for c in q['speciesCards']};scales={s['species']:s for s in q['scaleCalibrations']}
 if missing=='facts':return [{'species':s,'missingFields':[k for k in ['identification','habitat','regionSeason','diet','behaviorTendencies'] if not cards[s][k]['value']]+(['calls'] if not cards[s]['calls']['description'] else [])+(['funFacts'] if not cards[s]['funFacts'] else []),'cardRef':cards[s]['id']} for s in sorted(selected if pack!='all' else cards) if s in cards]
 if missing=='scale':return [{'species':s,'calibrationRef':scales[s]['id'],'status':scales[s]['calibrationStatus']} for s in sorted(selected if pack!='all' else scales) if s in scales and scales[s]['calibrationStatus']!='calibrated']
 tests={
  'clips':lambda r:not r.get('sourceFiles') or not r.get('actualFrames') or r.get('review',{}).get('state')=='needs-revision',
  'runtime':lambda r:bool(r.get('runtimeBlockers')) or r.get('runtimeSlot') is None,
  'license':lambda r:bool(r.get('sourceFiles')) and not r.get('verifiedLicenseEvidence'),
  'review':lambda r:not r.get('review',{}).get('speciesFidelityAccepted',False) or not r.get('review',{}).get('anchorsAccepted',False),
  'integration':lambda r:not r.get('integration',{}).get('integrated',False)}
 return [{'slot':r['id'],'species':r['species'],'action':r['action'],'direction':r['direction'],'state':r['state'],'reason':r.get('runtimeBlockers') if missing=='runtime' else r['artCoverage'],'provisionalCanonicalMapping':True} for r in rows if tests[missing](r)]
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--pack',choices=['san-diego','expansion','all'],default='san-diego');ap.add_argument('--missing',choices=['clips','facts','license','scale','review','runtime','integration'],required=True);ap.add_argument('--limit',type=int,default=10);args=ap.parse_args();q=json.loads((Path(__file__).parent/'queue.json').read_text());rows=query(q,args.pack,args.missing);print(json.dumps({'snapshot':q['updatedAt'],'pack':args.pack,'gap':args.missing,'matches':len(rows),'sample':rows[:args.limit],'scope':'derived proposal/production snapshot; no assertion of actual bird observations or current Mac contracts'},indent=2))
