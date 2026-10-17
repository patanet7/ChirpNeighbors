"""Check source review truthfulness and exact pixels without accessing the app."""
from pathlib import Path
from collections import Counter
import hashlib,json
from PIL import Image,ImageSequence
HERE=Path(__file__).resolve().parent
ROOT=next(p for p in HERE.parents if(p/'.git').exists())
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
m=json.loads((HERE/'manifest.json').read_text());c=json.loads((HERE/'review-catalog.json').read_text());d=json.loads((ROOT/c['reviewed_intake']).read_text())
assert H(ROOT/c['reviewed_intake'])==c['sha256']
for e in m['files']:
    p=Path(e['canonical_path']);assert not p.is_absolute()and'..'not in p.parts
    assert H(ROOT/p)==e['sha256'],p
    if e['transformation']in('exact_bytes','exact_non_sensitive_prompt_bytes'):assert e['source_sha256']==e['sha256']
assert sum(e['transformation']=='exact_non_sensitive_prompt_bytes'for e in m['files'])==1
assert len(d['entries'])==len({(x['asset_id'],x['variant_id'])for x in d['entries']})==8
assert Counter(x['source_review_status']for x in d['entries'])=={'accepted-for-scoped-source-review':4,'provisional':3,'held':1}
assert len(d['curated_static_plant_source_selection'])==3 and not d['runtime_integrated']and not d['owner_accepted']
for a in d['entries']:
    p=ROOT/a['sprite']['file'];im=Image.open(p);assert H(p)==a['sprite']['sha256']and im.mode=='RGBA'and im.getchannel('A').getextrema()[0]==0
    assert not a['interaction_slots']and not a['runtime_integrated']and not a['owner_accepted']
    assert set(a['season_variants'])=={'spring','summer','autumn','winter'}
    assert all(not s['separate_art_available']for s in a['season_variants'].values())
    if a['asset_id']=='object.wall_tool_rail':assert not any(x['id'].startswith('hook_seat_')for x in a['observed_functional_markers'])
attempt=d['held_controlled_attempt'];assert attempt['source_review_status']=='held'and not attempt['selected_for_intake']
held=json.loads((ROOT/attempt['intake']).read_text())['assets'][0];assert not any(held['states'][k]for k in['staged','integrated','accepted'])
qa_entry=next(x for x in m['files']if x['source_key']=='expansion/review-08/wind/yard-wind-qa.json');qa=json.loads((ROOT/qa_entry['canonical_path']).read_text())
for proof in qa['proofs']:
    assert proof['all_source_RGBA_frames_match_frozen_ledger']and proof['source_frames']in[33,49]
    for gif in proof['normal_and_mobile']:
        e=next(x for x in m['files']if x['source_key']=='expansion/review-08/wind/'+Path(gif['file']).name);im=Image.open(ROOT/e['canonical_path']);frames=[x.convert('RGB')for x in ImageSequence.Iterator(im)]
        assert len(frames)==gif['decoded_frames']and frames[0].tobytes()==frames[-1].tobytes()
        rect=tuple(gif['decoded_fixed_root_rect']);assert all(x.crop(rect).tobytes()==frames[0].crop(rect).tobytes()for x in frames)
for p,h in json.loads((HERE/'SHA256SUMS.json').read_text())['files'].items():assert H(ROOT/p)==h
print(json.dumps({'status':'passed','reviewed_originals':8,'curated_static_plants':3,'held_oak_attempts':2,'yardscale_wind_GIFs':4,'runtime_or_owner_acceptance':False}))
