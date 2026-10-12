# ChirpNeighbors

Bird identification from an ESP32 microphone, with a personal illustrated yard in [birdsong-yard-sprites](https://github.com/patanet7/birdsong-yard-sprites).

## Current local implementation · 2026-10-11

The companion UI runs SvelteKit, Pixi and owner-scoped SQLite. It includes reviewed versioned asset manifests, pose validation/fallbacks, provenance, private PNG intake/review/pins/archive, Findings and residents, configurable authentication, private recordings and analysis, revocable safe sharing, and deterministic illustrative yard/weather behavior. Artwork, biology and model scores remain technical fixtures.

This repository owns the [audio request service](docs/architecture/audio-pipeline.md), generated wire contracts and optional operator-supplied local ONNX adapter. The original ESP32 stream history is now [locally integrated](docs/delivery/esp32-integrated-20261009.md); its development receiver is separate from authenticated private recording admission. The original autonomous worker remains unavailable.

Start with the [authoritative 36-entry task index](docs/delivery/product-behavior-and-ideas.md), [current animation/content/reference-discovery checkpoint](docs/delivery/animation-planning-20261011.md), [consolidated audit findings](docs/delivery/audit-findings-20261009.json), and [complete verification command](docs/delivery/quality.md). The current checkpoint records 94/94 frozen gates at its exact tested source revisions, separate from later documentation/evidence commits reported in the final delivery response. It adds versioned recipes, bounded overrides and private Commons metadata discovery; the default nine clips/60 frames remain proposals with zero generated pixels. Actual live discovery returned blocked/network-unavailable. The [transport/static checkpoint](docs/delivery/external-transport-20261009.md) and [75-gate product/connection audit](docs/delivery/product-audit-20261009.md) remain historical proof, not current-source results.

## Check the integration boundary

Python 3.12:

```sh
python3 -m venv /tmp/chirp-contract
/tmp/chirp-contract/bin/pip install -r backend-inference/requirements-contract.txt
cd backend-inference
/tmp/chirp-contract/bin/python -m unittest discover -s tests -p 'test_identification_contract.py' -v
```

This narrow command checks the original adapter only. The current CI and aggregate gate also cover the new request API, schema drift, strict typing and isolated optional-model tests without downloading trained weights. The [original foundation log](docs/agents/20261007_061000_hierarchical-foundation.md) remains historical evidence.

## Next useful work

The [current bounded tasks and dependencies](docs/delivery/animation-planning-20261011.md#next-bounded-tasks-and-dependencies) and [product task index](docs/delivery/product-behavior-and-ideas.md) give observable acceptance; earlier transport/product audit lists retain their historical scope. Remaining work includes live provider validation, the original worker, private device admission, approved model/art inputs, a real authorized import adapter, scene sound, whole-scene performance budgets and production operating policy. Dedicated Svelte MCP is not exposed in this session. Normal PlatformIO registry access is blocked at proxy CONNECT; QEMU starts after a local dependency repair, but board/simulator/hardware acceptance is still open. The Commons metadata adapter is configured; image-generation providers remain unconfigured. Publication and deployment were not performed.
