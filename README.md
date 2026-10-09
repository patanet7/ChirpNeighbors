# ChirpNeighbors

Bird identification from an ESP32 microphone, with a personal illustrated yard in [birdsong-yard-sprites](https://github.com/patanet7/birdsong-yard-sprites).

## Current local implementation · 2026-10-09

The companion UI runs SvelteKit, Pixi and owner-scoped SQLite. It includes reviewed versioned asset manifests, pose validation/fallbacks, provenance, private PNG intake/review/pins/archive, Findings and residents, configurable authentication, private recordings and analysis, revocable safe sharing, and deterministic illustrative yard/weather behavior. Artwork, biology and model scores remain technical fixtures.

This repository owns the [audio request service](docs/architecture/audio-pipeline.md), generated wire contracts and optional operator-supplied local ONNX adapter. The original ESP32 stream history is now [locally integrated](docs/delivery/esp32-integrated-20261009.md); its development receiver is separate from authenticated private recording admission. The original autonomous worker remains unavailable.

Start with the [authoritative 36-entry task index](docs/delivery/product-behavior-and-ideas.md), [current product/connection audit](docs/delivery/product-audit-20261009.md), and [complete verification command](docs/delivery/quality.md). The historical [environment checkpoint](docs/delivery/environment-verified-20261009.md) retains its complete 75-gate proof; the current audit records its own exact revisions and verification state. Historical checkpoint counts are not current-source results.

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

The [audit task breakdown](docs/delivery/product-audit-20261009.md#concrete-next-tasks) gives dependencies and observable acceptance. Remaining work includes transport deadlines, the original worker, private device admission, approved model/art inputs, a real authorized import adapter, scene sound, whole-scene performance budgets and production operating policy. Normal PlatformIO registry access is blocked at proxy CONNECT; QEMU starts after a local dependency repair, but board/simulator/hardware acceptance is still open. Provider setup, publication and deployment were not performed.
