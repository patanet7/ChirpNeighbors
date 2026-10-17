"""Verify the source fence catalog without importing the application."""
from pathlib import Path
from collections import defaultdict
import hashlib
import json
import struct

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / '.git').exists())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
manifest = json.loads((HERE / 'manifest.json').read_text())
catalog = json.loads((HERE / 'fence-catalog.json').read_text())
for item in manifest['files']:
    p = Path(item['canonical_path'])
    assert not p.is_absolute() and '..' not in p.parts, p
    assert sha(ROOT / p) == item['sha256'], p
    if item['transformation'] in ('exact_bytes', 'exact_non_sensitive_prompt_bytes'):
        assert item['source_sha256'] == item['sha256'], p
components = catalog['component_assets']
foundations = catalog['seasonal_foundations']
yards = catalog['seasonal_yards']
assert (len(components), len(foundations), len(yards)) == (12, 4, 12)
assert len({(a['asset_id'], a['variant_id']) for a in components + foundations + yards}) == 28
for a in components:
    p = ROOT / a['source_sprite']
    assert sha(p) == a['source_sprite_sha256']
    header = p.read_bytes()[:26]
    assert header[:8] == b'\x89PNG\r\n\x1a\n' and header[25] == 6
    assert list(struct.unpack('>II', header[16:24])) == a['source_dimensions_px']
    assert a['source_alpha_extrema'][0] == 0 and a['source_alpha_extrema'][1] > 200
    assert not a['states']['integrated'] and not a['states']['accepted']
for a in foundations:
    assert sha(ROOT / a['source_original']) == a['source_original_sha256']
styles = defaultdict(set)
for a in yards:
    styles[a['style']].add(a['season'])
    assert sha(ROOT / a['scene_contract']) == a['scene_contract_sha256']
    assert len(a['layers']) == 2 and a['layers'][1]['true_alpha']
    for layer in a['layers']:
        assert sha(ROOT / layer['file']) == layer['sha256']
    for item in a['render_items']:
        assert sha(ROOT / item['source_file']) == item['source_sha256']
    assert not a['runtime_season_switching_implemented']
assert len(styles) == 3 and all(s == {'spring', 'summer', 'autumn', 'winter'} for s in styles.values())
assert {a['season'] for a in foundations} == {'spring', 'summer', 'autumn', 'winter'}
for relative, digest in json.loads((HERE / 'SHA256SUMS.json').read_text())['files'].items():
    assert sha(ROOT / relative) == digest, relative
print(json.dumps({'status': 'passed', 'placeable_sprites': 12, 'seasonal_foundations': 4, 'seasonal_yards': 12, 'styles': 3, 'source_records': len(manifest['files']), 'runtime_integration': False}))
