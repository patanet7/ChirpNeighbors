# ChirpNeighbors

Bird identification from an ESP32 microphone, with a personal illustrated yard in [birdsong-yard-sprites](https://github.com/patanet7/birdsong-yard-sprites).

## Current local foundation · 2026-10-07

The UI repository now runs SvelteKit with owner-scoped SQLite persistence, a deterministic yard simulation, Pixi rendering, and persisted pipeline jobs. Its working loop is imported/test identification → grouped Finding → temporary visitor → named permanent resident, surviving a server restart. Development identities and all artwork/generation outputs are explicitly labeled. Production sign-in, live device ingestion, real inference, and external generation providers are not connected by this checkpoint.

This repository contains the matching [generated identification contract](contracts/README.md) and a standalone [Python adapter](backend-inference/app/models/identification.py). The adapter validates source-neutral version-2 events and preserves unknown observation times/confidence; it does not run an inference model or add an endpoint. Existing hardware, cloud, and inference code is unchanged.

## Check the integration boundary

Python 3.12:

```sh
python3 -m venv /tmp/chirp-contract
/tmp/chirp-contract/bin/pip install -r backend-inference/requirements-contract.txt
cd backend-inference
/tmp/chirp-contract/bin/python -m unittest discover -s tests -p 'test_identification_contract.py' -v
```

The lightweight contract CI uses these checks without downloading model weights or installing the full inference stack. See [the implementation log](docs/agents/20261007_061000_hierarchical-foundation.md) for the local checkpoint, verification, and remaining integration boundaries.

## Next useful work

Connect one real identification source to the shared event contract, including stable taxonomy mapping and correction handling. Keep deployment and device work separate from the independently runnable UI foundation. The UI README contains its exact run instructions and the remaining authentication/provider work.
