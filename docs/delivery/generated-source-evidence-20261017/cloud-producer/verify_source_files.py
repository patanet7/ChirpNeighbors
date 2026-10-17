"""Verify retained source bytes; optional Pillow decode checks, no rewrites."""
from pathlib import Path
import argparse
import hashlib
import json

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--pixel-checks', action='store_true')
args = parser.parse_args()
root = Path(__file__).parent
index = json.loads((root / 'source-files.sha256.json').read_text())
for item in index['files']:
    path = root / item['file']
    assert path.is_file(), item['file']
    payload = path.read_bytes()
    assert len(payload) == item['bytes'], item['file']
    assert hashlib.sha256(payload).hexdigest() == item['sha256'], item['file']
originals = json.loads((root / 'original-source-inventory.json').read_text())
assert len(originals['originals']) == 11
for item in originals['originals']:
    for path_key, hash_key in [('file', 'sha256'), ('promptFile', 'promptSha256')]:
        assert hashlib.sha256((root / item[path_key]).read_bytes()).hexdigest() == item[hash_key]
pixel_count = None
animation_pairs = None
if args.pixel_checks:
    from PIL import Image
    bank = json.loads((root / 'frame-bank.json').read_text())
    assert len(bank['frames']) == 57
    for frame in bank['frames']:
        with Image.open(root / frame['file']) as source:
            rgba = source.convert('RGBA')
            digest = hashlib.sha256(
                f'RGBA8;{rgba.width}x{rgba.height};'.encode() + rgba.tobytes()
            ).hexdigest()
            assert frame['frameId'] == 'frame.sha256.' + digest
            assert list(rgba.size) == frame['dimensions']
    assert bank['verifiedReuseCount'] == 0
    assert all(not frame.get('acceptedUses') for frame in bank['frames'])
    animation_pairs = 0
    for gif in sorted((root / 'batches').glob('*/preview.gif')):
        with Image.open(gif) as image:
            assert image.n_frames == 6, str(gif)
            for position in range(image.n_frames):
                image.seek(position)
                image.load()
        with Image.open(gif.with_suffix('.apng')) as image:
            assert image.n_frames == 6, str(gif)
            for position in range(image.n_frames):
                image.seek(position)
                image.load()
        animation_pairs += 1
    assert animation_pairs == 9
    pixel_count = 57
print(json.dumps({
    'passed': True,
    'byteHashedFiles': len(index['files']),
    'originalPromptPairs': 11,
    'decodedFrameIdentities': pixel_count,
    'decodedSixFrameApngGifPairs': animation_pairs,
    'runtimeIntegrationChecked': False,
    'artScaleContactAcceptance': False,
}))
