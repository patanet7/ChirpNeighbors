"""Verify source bytes, actual alpha, unique identities and decoded motion proofs."""
from pathlib import Path
import hashlib,json
from PIL import Image,ImageSequence
HERE=Path(__file__).resolve().parent
ROOT=next(p for p in HERE.parents if (p/'.git').exists())
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
m=json.loads((HERE/'manifest.json').read_text());c=json.loads((HERE/'repair-catalog.json').read_text())
for e in m['files']:
    p=Path(e['canonical_path']);assert not p.is_absolute() and '..'not in p.parts
    assert H(ROOT/p)==e['sha256'],p
    if e['transformation']in('exact_bytes','exact_non_sensitive_prompt_bytes'):assert e['source_sha256']==e['sha256'],p
assert len([e for e in m['files']if '/originals/'in e['source_key']and e['source_key'].endswith('.png')])==5
assert sum(e['transformation']=='exact_non_sensitive_prompt_bytes'for e in m['files'])==5
assert len(c['assets'])==len({(a['asset_id'],a['variant_id'])for a in c['assets']})==8
assert not c['new_yard_scenes'] and c['generation_stopped_for_checkpoint']
for a in c['assets']:
    assert H(ROOT/a['source_manifest'])==a['source_manifest_sha256']
    assert a['states']['generated'] and a['states']['reviewed'] and a['states']['staged']
    assert not a['states']['integrated'] and not a['states']['accepted']
    for f in a['source_files']:
        im=Image.open(ROOT/f['file']);assert H(ROOT/f['file'])==f['sha256']
        assert im.mode=='RGBA' and list(im.size)==f['dimensions_px'] and im.getchannel('A').getextrema()[0]==0
for proof in c['wind_proofs']:
    assert H(ROOT/proof['file'])==proof['sha256']
    frames=[f.convert('RGBA').tobytes()for f in ImageSequence.Iterator(Image.open(ROOT/proof['file']))]
    assert len(frames)==proof['decoded_frames'] and len(set(frames))==proof['unique_RGBA_frames'] and frames[0]==frames[-1]
    qa=json.loads((ROOT/proof['qa']).read_text())
    if proof['scope']=='oak':
        assert max(qa['all_core_changed_counts'])==max(qa['all_root_changed_counts'])==0
        assert qa['decoded_root_max_changed_pixels']==qa['stable_unoccluded_wood_max_changed_pixels']==0
        assert qa['minimum_foliage_alpha_gt1_canvas_margin_all_frames_px']>0
    else:
        assert qa['core_root_RGBA_identical_all49sourceframes'] and qa['max_pivot_geometry_drift_px']==0
        assert qa['minimum_joint_overlap_alpha128_pixels']>0 and qa['visible_alpha_gt8_edge_clipping_pixels']==0
        assert qa['GIF']['core_root_RGB_identical_all_decoded_frames']
for p,h in json.loads((HERE/'SHA256SUMS.json').read_text())['files'].items():assert H(ROOT/p)==h,p
print(json.dumps({'status':'passed','source_records':len(m['files']),'asset_variants':8,'originals_and_prompts':5,'actual_wind_GIFs':2,'new_yards':0,'runtime_integrated':False}))
