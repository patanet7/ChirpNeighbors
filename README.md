# ChirpNeighbors

Bird identification from an ESP32 microphone, with a personal illustrated yard in [birdsong-yard-sprites](https://github.com/patanet7/birdsong-yard-sprites).

## Current local implementation · 2026-10-08

The companion UI runs SvelteKit, Pixi and owner-scoped SQLite. It preserves the Finding → visitor → resident loop and now includes reviewed versioned asset manifests, private recording upload/playback/deletion, configurable durable authentication and an authenticated audio-analysis bridge. Artwork remains explicitly labeled technical fixtures.

This repository owns the modular [audio request service](docs/architecture/audio-pipeline.md), Pydantic wire contracts, generated counterparts, synthetic evaluation and optional operator-supplied local ONNX adapter. Existing prototype hardware/streaming code is separate. No trained bird model, species-accurate art, live provider or device integration is claimed.

Start with the [concrete task checklist](docs/delivery/README.md), [verified checkpoint](docs/delivery/checkpoint-20261008.md) and [complete local verification command](docs/delivery/quality.md). The final run passed 50 gates, including 469 UI tests, 127 Python tests and 410 browser assertions.

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

Review real model/art inputs and production provider configuration, then integrate the separately completed worker/device artifacts only after authorized transfer. Durable derived-output deletion and historical backup retention remain explicit gaps. Docker image execution is unverified after a registry DNS failure; no publication or deployment occurred. See the checklist for dependencies and acceptance tests.
