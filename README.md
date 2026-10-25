# ChirpNeighbors (backend, firmware and contracts)

The backend, firmware and contracts side of the ChirpNeighbors bird-finding project: the local audio service (`backend-inference/`), ESP32 capture firmware (`esp32-client/`), a mirror of the shared JSON-Schema contracts (`contracts/`) and committed art. The application itself (SvelteKit, Pixi, owner-scoped SQLite) lives in [birdsong-yard-sprites](https://github.com/patanet7/birdsong-yard-sprites/tree/main), the source of truth for contracts; `contracts/` here is generated from it with `npm run contracts:export -- --main-repo <path>`. Current bird art and diagnostic models are technical fixtures, not approved species artwork or a validated bird classifier.

Start with the [documentation index](docs/README.md) and [product/engineering task index](docs/delivery/product-behavior-and-ideas.md).

## Run and verify

- [UI setup, startup and shutdown](https://github.com/patanet7/birdsong-yard-sprites/blob/main/docs/setup.md): the companion application's canonical guide owns the mise tasks, tool requirements, private data directory and actual loopback URL. Development identities and bird art are fixtures; production authentication fails closed without configuration. A cloud-machine localhost address is accessible there, not automatically from your own computer.
- [Run the backend](backend-inference/README.md): isolated Python environments, headless intake and the authenticated local audio boundary.
- [Build/check firmware](esp32-client/README.md): pinned PlatformIO profiles and explicit simulator/hardware limits.
- [Run the complete local verification](docs/delivery/quality.md): pinned two-repository tooling and sequential browser checks.

Verification results live in one place, the [verification ledger](docs/delivery/verification-ledger.md); the [task index](docs/delivery/product-behavior-and-ideas.md) owns current status, including newly reproduced defects such as the [2026-10-12 architecture follow-up](docs/delivery/product-behavior-and-ideas.md#architecture-follow-up).

## Remaining product dependencies

Approved detailed species art, real models and provider adapters, the original autonomous worker, physical hardware and worst-case performance acceptance remain open. Owner evidence and location stay private; sharing uses an explicit safe projection. The [task index](docs/delivery/product-behavior-and-ideas.md) owns acceptance and dependencies; add updates there instead of another parallel roadmap.
