"""Verify the source-only regional yard publication; no app modules required."""
from pathlib import Path
import argparse
import hashlib
import json
import re

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / '.git').exists())
PRIVATE = re.compile(r'lib(?:file|dir)_[A-Za-z0-9_-]+|https?://[^\s"<>]*chatgpt\.com/|/(?:workspace|tmp|home|Users)/')
sha = lambda payload: hashlib.sha256(payload).hexdigest()
manifest = json.loads((HERE / 'manifest.json').read_text())
paths = {}
for entry in manifest['files']:
    relative = Path(entry['canonical_path'])
    assert not relative.is_absolute() and '..' not in relative.parts, relative
    target = ROOT / relative
    data = target.read_bytes()
    assert sha(data) == entry['sha256'], relative
    assert len(data) == entry['bytes'], relative
    if entry['transformation'] in ('exact_bytes', 'exact_non_sensitive_prompt_bytes'):
        assert entry['source_sha256'] == entry['sha256'], relative
    paths[str(relative)] = entry['sha256']
for relative, entry in manifest['embedded_image_extractions'].items():
    target = ROOT / relative
    assert sha(target.read_bytes()) == entry['sha256'], relative
    paths[relative] = entry['sha256']
# New outputs are plain source files, with no duplicate byte copy or transport ZIP.
by_hash = {}
for target in HERE.rglob('*'):
    if not target.is_file():
        continue
    assert target.suffix.lower() != '.zip', target
    assert target.stat().st_size < 100 * 1024 * 1024, target
    digest = sha(target.read_bytes())
    assert digest not in by_hash, (target, by_hash.get(digest))
    by_hash[digest] = target
    if target.suffix.lower() in ('.json', '.txt', '.md', '.csv', '.html', '.py'):
        assert not PRIVATE.search(target.read_text()), target
sums = json.loads((HERE / 'SHA256SUMS.json').read_text())
for relative, digest in sums['files'].items():
    assert sha((ROOT / relative).read_bytes()) == digest, relative
# The starter HTML's image URLs must resolve inside the canonical checkout.
preview = HERE / 'files/expansion/starter-pack/root/ChirpNeighbors-San-Diego-Editable-Asset-Preview.html'
text = preview.read_text()
data = json.loads(text.split('const DATA=', 1)[1].split(';\nconst canvas=', 1)[0])
for item in data['backgrounds'] + data['sprites']:
    target = (preview.parent / item['image']).resolve()
    assert target.is_relative_to(ROOT) and target.is_file(), target
    assert sha(target.read_bytes()) == item['review_derivative']['sha256'], target
print(json.dumps({'status': 'passed', 'source_records': len(manifest['files']), 'canonical_files_verified': len(paths), 'new_prefix_files': len(by_hash), 'exact_prompt_records': manifest['summary']['exact_prompt_records'], 'application_integration': False}))
