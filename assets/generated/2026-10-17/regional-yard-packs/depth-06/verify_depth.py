"""Verify the independent depth source catalog without importing the app."""
from pathlib import Path
from collections import defaultdict
import hashlib
import json
import struct

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / '.git').exists())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
manifest = json.loads((HERE / 'manifest.json').read_text())
catalog = json.loads((HERE / 'depth-catalog.json').read_text())
for e in manifest['files']:
    relative = Path(e['canonical_path'])
    assert not relative.is_absolute() and '..' not in relative.parts
    assert sha(ROOT / relative) == e['sha256'], relative
    if e['transformation'] in ('exact_bytes', 'exact_non_sensitive_prompt_bytes'):
        assert e['source_sha256'] == e['sha256'], relative
for relative, e in manifest['embedded_image_extractions'].items():
    assert sha(ROOT / relative) == e['sha256'], relative
seasons = defaultdict(set)
assert len(catalog['scenes']) == 20 and len(catalog['component_assets']) == 7
all_assets = catalog['scenes'] + catalog['component_assets']
assert len({(a['asset_id'], a['variant_id']) for a in all_assets}) == 27
for scene in catalog['scenes']:
    seasons[scene['collection']].add(scene['season'])
    assert len(scene['layers']) == 5
    assert {l['slot'] for l in scene['layers']} == {'sky', 'far', 'midground', 'ground', 'foreground'}
    assert sha(ROOT / scene['source_manifest']) == scene['source_manifest_sha256']
    for layer in scene['layers']:
        path = ROOT / layer['file']
        assert sha(path) == layer['sha256']
        header = path.read_bytes()[:26]
        assert header[:8] == b'\x89PNG\r\n\x1a\n'
        assert struct.unpack('>II', header[16:24]) == (1536, 1024)
        assert layer['slot'] == 'sky' or header[25] == 6
    assert not scene['states']['integrated'] and not scene['states']['accepted']
assert len(seasons) == 5 and all(s == {'spring', 'summer', 'autumn', 'winter'} for s in seasons.values())
for asset in catalog['component_assets']:
    assert asset['source_files']
    for source in asset['source_files']:
        assert sha(ROOT / source['canonical_path']) == source['sha256']
        assert source['alpha_extrema'][0] == 0
    assert not asset['states']['integrated'] and not asset['states']['accepted']
assert len(catalog['wind_proofs']) == 7
for proof in catalog['wind_proofs']:
    assert sha(ROOT / proof['file']) == proof['sha256']
    assert proof['decoded_frames'] >= 24 and proof['unique_RGBA_frames'] > 2
for relative, digest in json.loads((HERE / 'SHA256SUMS.json').read_text())['files'].items():
    assert sha(ROOT / relative) == digest, relative
print(json.dumps({'status': 'passed', 'seasonal_scenes': 20, 'depth_slots_each': 5, 'tree_plant_prop_entries': 7, 'actual_wind_GIFs': 7, 'source_records': len(manifest['files']), 'runtime_integrated': False}))
