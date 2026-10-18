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
assert len(originals['originals']) == 42
for item in originals['originals']:
    for path_key, hash_key in [('file', 'sha256'), ('promptFile', 'promptSha256')]:
        assert hashlib.sha256((root / item[path_key]).read_bytes()).hexdigest() == item[hash_key]
pixel_count = None
animation_pairs = None
if args.pixel_checks:
    from PIL import Image
    bank = json.loads((root / 'frame-bank.json').read_text())
    assert len(bank['frames']) == 142
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
        manifest = json.loads((gif.parent / 'manifest.json').read_text())
        expected = manifest['validation'].get('previewGIFFrames', manifest['validation'].get('GIFframes', 6))
        with Image.open(gif) as image:
            assert image.n_frames == expected, str(gif)
            for position in range(image.n_frames):
                image.seek(position)
                image.load()
        with Image.open(gif.with_suffix('.apng')) as image:
            assert image.n_frames == expected, str(gif)
            for position in range(image.n_frames):
                image.seek(position)
                image.load()
        animation_pairs += 1
    assert animation_pairs == 10
    control = root / 'batches/house-finch-female-preen-contact-v2'
    for name in ['comparison.gif', 'comparison.apng']:
        with Image.open(control / name) as image:
            assert image.n_frames == 3
            for i in range(3):
                image.seek(i)
                image.load()
                assert image.info['duration'] == 800
    assert not json.loads((control / 'manifest.json').read_text())['comparison']['isFinishedAnimation']
    pixel_count = 142
print(json.dumps({
    'passed': True,
    'byteHashedFiles': len(index['files']),
    'originalPromptPairs': 42,
    'decodedFrameIdentities': pixel_count,
    'decodedReviewApngGifPairs': animation_pairs,
    'runtimeIntegrationChecked': False,
    'artScaleContactAcceptance': False,
}))
