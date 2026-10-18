#!/usr/bin/env python3
"""Validate and replay the published Depth09 source pack, without repository edits.

Requires Python 3, Pillow and numpy. Example:
  python verify_depth09.py --repo /path/to/checkout
Checks published hashes; optional --source-root compares private original hashes too.
Replay uses only manifest-mapped canonical bytes restored into temporary aliases.
This is source validation, not runtime admission, physical or owner acceptance.
"""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess
import sys
import tempfile

import numpy as np
from PIL import Image, ImageSequence


PREFIX = Path('assets/generated/2026-10-17/regional-yard-packs/depth-09')
SOURCE_PREFIX = 'expansion/depth-09/'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(value, message):
    if not value:
        raise AssertionError(message)


def inside(root, relative):
    p = (root / relative).resolve()
    require(p.is_relative_to(root.resolve()), 'Path escapes root: ' + str(relative))
    return p


def read(path):
    return json.loads(path.read_text())


def pixels(path, mode='RGBA'):
    with Image.open(path) as im:
        return np.asarray(im.convert(mode))


def run(args):
    repo = args.repo.resolve()
    manifest_path = args.manifest.resolve() if args.manifest else repo / PREFIX / 'manifest.json'
    manifest = read(manifest_path)
    require(manifest.get('path_base') == 'repository_root', 'Unsupported manifest path base')
    records = manifest['files']
    aliases = {}
    canonical_to_alias = {}
    source_checked = 0
    image_checked = 0
    for record in records:
        key = record['source_key']
        require(key.startswith(SOURCE_PREFIX), 'Unexpected source namespace: ' + key)
        alias = key[len(SOURCE_PREFIX):]
        require(alias and alias not in aliases, 'Duplicate or empty source alias: ' + alias)
        canonical = inside(repo, record['canonical_path'])
        require(canonical.is_file(), 'Missing canonical file: ' + str(canonical))
        require(digest(canonical) == record['sha256'], 'Published SHA mismatch: ' + key)
        require(canonical.stat().st_size == record['bytes'], 'Published size mismatch: ' + key)
        if record['transformation'] in ('exact_bytes', 'exact_non_sensitive_prompt_bytes'):
            require(record['source_sha256'] == record['sha256'], 'Exact transformation changed bytes: ' + key)
        if args.source_root:
            original = inside(args.source_root, key)
            require(original.is_file(), 'Missing optional original: ' + key)
            require(digest(original) == record['source_sha256'], 'Original SHA mismatch: ' + key)
            source_checked += 1
        if 'dimensions_px' in record:
            with Image.open(canonical) as im:
                require(list(im.size) == record['dimensions_px'], 'Dimensions mismatch: ' + key)
                require(im.mode == record['mode'], 'Mode mismatch: ' + key)
                if 'alpha_extrema' in record:
                    require(list(im.getchannel('A').getextrema()) == record['alpha_extrema'], 'Alpha extrema mismatch: ' + key)
            image_checked += 1
        aliases[alias] = (canonical, record)
        canonical_to_alias.setdefault(record['canonical_path'], alias)
    for canonical_key, record in manifest.get('embedded_image_extractions', {}).items():
        canonical = inside(repo, canonical_key)
        require(digest(canonical) == record['sha256'], 'Embedded SHA mismatch: ' + canonical_key)
    require(not manifest.get('next_art_queue', {}).get('generation_active', False), 'Manifest claims active generation')

    with tempfile.TemporaryDirectory(prefix='depth09-public-replay-') as temporary:
        stage = Path(temporary)
        # Canonical paths in JSON become absolute temporary alias paths. Identical
        # bytes may have multiple source aliases; any restored alias is equivalent.
        def rewrite(value):
            if isinstance(value, str):
                alias = canonical_to_alias.get(value)
                return str(inside(stage, alias)) if alias else value
            if isinstance(value, list):
                return [rewrite(v) for v in value]
            if isinstance(value, dict):
                return {rewrite(k): rewrite(v) for k, v in value.items()}
            return value

        for alias, (canonical, record) in aliases.items():
            target = inside(stage, alias)
            target.parent.mkdir(parents=True, exist_ok=True)
            if target.suffix == '.json':
                target.write_text(json.dumps(rewrite(read(canonical)), indent=2) + '\n')
            else:
                target.write_bytes(canonical.read_bytes())

        intake = read(stage / 'root/backgrounds-intake.json')
        assets = intake['assets']
        require(len(assets) == 4, 'Expected four primary season variants')
        require({a['season'] for a in assets} == {'spring', 'summer', 'autumn', 'winter'}, 'Season coverage mismatch')
        for asset in assets:
            require(asset['asset_id'] == 'scene.san_diego_inland_canyon', 'Asset ID drift')
            require(len(asset['layers']) == 9, 'Expected nine layer slots per season')
            require(len({layer['slot'] for layer in asset['layers']}) == 9, 'Duplicate layer slots')
            require(not asset.get('default_distant_summit_snow'), 'Default summit snow must be false')
            require(asset['states'].get('integrated') is False and asset['states'].get('accepted') is False, 'Source intake claims integration/acceptance')
            require(asset['placement'].get('physical_support_or_collision') is False, 'Physical geometry asserted')
            require(asset['wind'].get('runtime_implemented') is False, 'Runtime implementation asserted')
            for layer in asset['layers']:
                f = Path(layer['file'])
                require(f.is_relative_to(stage) and f.is_file(), 'Unrestored layer reference: ' + layer['file'])
                require(digest(f) == layer['sha256'], 'Intake layer SHA mismatch: ' + layer['slot'])
                require(list(Image.open(f).size) == [1536, 1024], 'Layer canvas mismatch')

        floor = pixels(stage / 'ground/full-visible-ground-mask.png', 'L')
        expected_floor = np.zeros((1024, 1536), dtype=np.uint8)
        expected_floor[494:] = 255
        require(np.array_equal(floor, expected_floor), 'Full floor not exact all-width y494..1024')
        available = pixels(stage / 'ground/available-with-PROPOSED-instance-envelopes.png', 'L')
        require(np.all(available <= floor), 'Available mask escapes floor')
        require(int((floor > 0).sum()) == 814080, 'Floor pixel count mismatch')
        require(int((available > 0).sum()) == 803998, 'Available pixel count mismatch')
        mask_checks = []
        for name in ['fence', 'cedar_feeder', 'bench', 'objects']:
            alpha = pixels(stage / 'fence-objects/layers' / (name + '.png'))[:, :, 3]
            soft = pixels(stage / 'fence-objects/masks' / (name + '-soft-alpha.png'), 'L')
            binary = pixels(stage / 'fence-objects/masks' / (name + '-visual-alpha128.png'), 'L')
            require(np.array_equal(alpha, soft), name + ': soft alpha mismatch')
            require(np.array_equal((alpha >= 128).astype(np.uint8) * 255, binary), name + ': binary alpha mismatch')
            mask_checks.append({'name': name, 'exact_soft_alpha': True, 'exact_binary_threshold': '>=128'})
        for season in ['spring', 'summer', 'autumn', 'winter']:
            for role in ['wood', 'canopy']:
                name = season + '-' + role
                alpha = pixels(stage / 'tree-leaves/layers' / (name + '.png'))[:, :, 3]
                coverage = pixels(stage / 'tree-leaves/masks' / (name + '-visual-coverage.png'), 'L')
                require(np.array_equal((alpha > 8).astype(np.uint8) * 255, coverage), name + ': visual coverage mismatch')
                mask_checks.append({'name': name, 'exact_binary_threshold': '>8'})
        for record in read(stage / 'mountain-masks/mask-index.json'):
            require(record.get('physical_geometry') is False, 'Mountain mask claims physical geometry')
            alpha = pixels(Path(record['source_layer']))[:, :, 3]
            require(np.array_equal(alpha, pixels(Path(record['file']), 'L')), 'Mountain soft alpha mismatch')
            mask_checks.append({'name': record['role'], 'exact_soft_alpha': True})

        schema = read(stage / 'root/runtime-schema-proposal.json')
        require(schema.get('live_engine_adoption') is False, 'Schema proposal claims live engine adoption')
        require(schema.get('integrator_agreement_recorded') is False, 'Schema proposal claims integrator agreement')
        require(schema.get('runtime_schema_files_changed') == [], 'Source publication declares runtime schema edits')
        # Assert actual negative admission fields, rather than interpreting every
        # descriptive word containing "accept" or "geometry" as a status flag.
        flags = []
        def collect_flags(value):
            if isinstance(value, dict):
                for key, child in value.items():
                    if key in {'runtime_adopted', 'runtime_implemented', 'owner_accepted', 'physical_geometry', 'coordination_agreement'}:
                        flags.append((key, child))
                        require(child is not True, 'Unpermitted positive claim: ' + key)
                    collect_flags(child)
            elif isinstance(value, list):
                for child in value:
                    collect_flags(child)
        collect_flags(schema)

        original_count = sum(alias.startswith('far-ground/originals/') and Path(alias).suffix == '.png' for alias in aliases)
        require(original_count == 2, 'Expected exactly two new mountain originals')
        expected_outputs = [name + suffix for name in ['spring', 'summer', 'autumn', 'winter', 'winter-summit-snow'] for suffix in ['-source.png', '-960.png', '-384.png']]
        expected_outputs += ['ChirpNeighbors-Depth09-Seasons.png', 'depth-layer-contact.jpg', 'autumn-yard-tree-sway-blowing-leaves.gif', 'yard-wind-decoded-contact.jpg']
        require(len(expected_outputs) == 19, 'Replay output contract changed')
        # Remove only staged expected outputs, proving replay does not pass by
        # comparing previously copied published previews to themselves.
        for name in expected_outputs:
            (stage / 'root/previews' / name).unlink()
        completed = subprocess.run([sys.executable, str(stage / 'tools/render_scene.py'), '--root', str(stage)], cwd=stage, capture_output=True, text=True, check=False)
        require(completed.returncode == 0, 'Portable replay failed: ' + completed.stderr[-4000:])
        comparisons = []
        for name in expected_outputs:
            alias = 'root/previews/' + name
            expected = aliases[alias][0]
            actual = stage / alias
            require(actual.is_file(), 'Replay omitted ' + name)
            byte_equal = digest(actual) == digest(expected)
            pixel_equal = np.array_equal(pixels(actual), pixels(expected))
            require(byte_equal and pixel_equal, 'Replay byte/pixel mismatch: ' + name)
            comparisons.append({'file': alias, 'sha256': digest(actual), 'byte_equal': True, 'pixel_equal': True})
        gif = Image.open(stage / 'root/previews/autumn-yard-tree-sway-blowing-leaves.gif')
        frames = [np.asarray(f.convert('RGB')).copy() for f in ImageSequence.Iterator(gif)]
        require(len(frames) == 33, 'Decoded frame count mismatch')
        require(np.array_equal(frames[0], frames[-1]), 'GIF loop does not close')
        require(all(np.array_equal(f[433:452, 145:207], frames[0][433:452, 145:207]) for f in frames), 'Root changed in decoded GIF')
        caption = (stage / 'tools/render_scene.py').read_text()
        require('winter / OPTIONAL summit snow after storm' in caption, 'Corrected conditional winter caption absent')
        return {'result': 'pass', 'manifest_sha256': digest(manifest_path), 'source_records_verified': len(records), 'unique_canonical_files_verified': len({r['canonical_path'] for r in records}), 'image_records_verified': image_checked, 'optional_original_source_hashes_verified': source_checked, 'season_variants': 4, 'layers_per_season': 9, 'new_mountain_originals': original_count, 'full_floor_pixels': 814080, 'available_proposed_instance_pixels': 803998, 'visual_mask_checks': mask_checks, 'replayed_outputs': comparisons, 'decoded_GIF_frames': len(frames), 'decoded_GIF_unique_frames': len({f.tobytes() for f in frames}), 'decoded_first_last_equal': True, 'decoded_root_unchanged': True, 'conditional_winter_caption_verified': True, 'runtime_admitted': False, 'physical_geometry_validated': False, 'owner_accepted': False, 'temporary_alias_stage_removed': True, 'assumptions': ['Pillow/numpy versions may affect exact GIF/JPEG encoding; this verifier requires both byte and decoded-pixel equality in the current environment.', 'Published metadata has transformed hashes. source_sha256 is checked only against optional private originals, never against sanitized canonical metadata.', 'Visual masks are raster coverage; proposed footprints and strict-V1 schema admission remain unimplemented.']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, required=True)
    parser.add_argument('--manifest', type=Path)
    parser.add_argument('--source-root', type=Path, help='Optional original yard-production root for private original-hash audit')
    args = parser.parse_args()
    try:
        result = run(args)
    except Exception as exc:
        print(json.dumps({'result': 'fail', 'error_type': type(exc).__name__, 'error': str(exc)}, indent=2))
        return 1
    print(json.dumps(result, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
