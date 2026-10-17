"""Replay actual source-part proofs in an isolated temporary tree (Pillow + NumPy).
Source files and the application are never modified. Canonical paths are resolved
through manifest.json, restoring aliases only inside the temporary replay folder.
"""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / '.git').exists())
manifest = json.loads((HERE / 'manifest.json').read_text())
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--kind', choices=['tree', 'sage', 'both'], default='both')
args = parser.parse_args()
configs = [
    ('tree', 'tree-wind', 'render_motion.py', ['previews/mild-anchored-wind.gif', 'previews/heavy-anchored-wind.gif']),
    ('sage', 'plant-object-modules', 'scripts/render_wind.py', ['previews/cleveland-sage-mild-heavy.gif']),
]
results = []
for name, scope, script, outputs in configs:
    if args.kind not in ('both', name):
        continue
    prefix = 'expansion/depth-06/' + scope + '/'
    entries = {e['source_key'][len(prefix):]: e for e in manifest['files'] if e['source_key'].startswith(prefix)}
    assert script in entries
    with tempfile.TemporaryDirectory(prefix='chirp-depth-wind-') as temporary:
        stage = Path(temporary)
        for relative, entry in entries.items():
            destination = stage / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / entry['canonical_path'], destination)
        result = subprocess.run([sys.executable, str(stage / script)], cwd=stage, capture_output=True, text=True)
        assert result.returncode == 0, result.stderr[-4000:]
        for relative in outputs:
            actual = hashlib.sha256((stage / relative).read_bytes()).hexdigest()
            expected = entries[relative]['sha256']
            assert actual == expected, (scope, relative, actual, expected)
            results.append({'proof': name, 'file': relative, 'sha256': actual, 'exact_replay': True})
print(json.dumps({'status': 'passed', 'application_modified': False, 'results': results}, indent=2))
