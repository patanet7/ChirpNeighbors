"""Verify seasonal source assets without importing the application."""
from pathlib import Path
from collections import defaultdict
import hashlib
import json

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / '.git').exists())
manifest = json.loads((HERE / 'manifest.json').read_text())
catalog = json.loads((HERE / 'seasonal-catalog.json').read_text())
sha = lambda b: hashlib.sha256(b).hexdigest()
for e in manifest['files']:
    path = Path(e['canonical_path'])
    assert not path.is_absolute() and '..' not in path.parts
    assert sha((ROOT / path).read_bytes()) == e['sha256'], path
    if e['transformation'] in ('exact_bytes', 'exact_non_sensitive_prompt_bytes'):
        assert e['source_sha256'] == e['sha256'], path
families = defaultdict(set)
for a in catalog['assets']:
    families[a['asset_id']].add(a['season'])
    assert sha((ROOT / a['source_original']).read_bytes()) == a['source_sha256']
    assert sha((ROOT / a['source_manifest']).read_bytes()) == a['source_manifest_sha256']
    assert a['source_dimensions_px'] == [1536, 1024] and a['source_opaque']
assert len(catalog['assets']) == 20 and len(families) == 5
assert all(s == {'spring', 'summer', 'autumn', 'winter'} for s in families.values())
for path, digest in json.loads((HERE / 'SHA256SUMS.json').read_text())['files'].items():
    assert sha((ROOT / path).read_bytes()) == digest, path
print(json.dumps({'status': 'passed', 'yard_families': 5, 'actual_season_variants': 20, 'source_records': len(manifest['files']), 'runtime_integration': False}))
