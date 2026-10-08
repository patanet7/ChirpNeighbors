# ChirpNeighbors

Bird identification from an ESP32 microphone, with a personal illustrated yard in [birdsong-yard-sprites](https://github.com/patanet7/birdsong-yard-sprites).

## Current local implementation · 2026-10-08

The companion UI runs SvelteKit, Pixi and owner-scoped SQLite. It preserves the Finding → visitor → resident loop and now includes reviewed versioned asset manifests, private recording upload/playback/deletion, configurable durable authentication and an authenticated audio-analysis bridge. Artwork remains explicitly labeled technical fixtures.

This repository owns the modular [audio request service](docs/architecture/audio-pipeline.md), Pydantic wire contracts, generated counterparts, synthetic evaluation and optional operator-supplied local ONNX adapter. Existing prototype hardware/streaming code is separate. No trained bird model, species-accurate art, live provider or device integration is claimed.

Start with the [concrete task checklist](docs/delivery/README.md), [verified checkpoint](docs/delivery/checkpoint-20261008.md) and [complete local verification command](docs/delivery/quality.md). The [lifecycle checkpoint](docs/delivery/lifecycle-checkpoint-20261008.md) covers all 55 gates across the complete run and one selector-fix rerun: 554 UI tests, 136 Python tests and 460 renderer/browser assertions, plus actual auth/recovery/audio journeys. The [task checklist](docs/delivery/lifecycle-wave.md) records dependencies and remaining gates.

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

Review real model/art inputs and production provider configuration, then integrate the separately completed worker/device artifacts only after authorized transfer. Durable managed derived-output deletion and retained-ledger recovery are implemented. Operators must retain the newest complete deletion ledger; offline backups and pre-identity checkpoints cannot be erased or automatically reconciled without that history. Docker image execution is unverified after a registry DNS failure; no publication or deployment occurred. See the checklist for dependencies and acceptance tests.
