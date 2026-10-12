# ChirpNeighbors

A private bird-finding application with a layered illustrated yard. The companion UI uses SvelteKit, Pixi and owner-scoped SQLite; this repository owns shared contracts, the local audio service and ESP32 capture firmware. Current bird art and diagnostic models are technical fixtures, not approved species artwork or a validated bird classifier.

Start with the [documentation index](docs/README.md) and [product/engineering task index](docs/delivery/product-behavior-and-ideas.md).

## Run and verify

- [UI setup, startup and shutdown](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/visual-foundations-20261012/docs/setup.md): the companion application's canonical guide owns the mise tasks, tool requirements, private data directory and actual loopback URL. Development identities and bird art are fixtures; production authentication fails closed without configuration. A cloud-machine localhost address is accessible there, not automatically from your own computer.
- [Run the backend](backend-inference/README.md): isolated Python environments, headless intake and the authenticated local audio boundary.
- [Build/check firmware](esp32-client/README.md): pinned PlatformIO profiles and explicit simulator/hardware limits.
- [Run the complete local verification](docs/delivery/quality.md): pinned two-repository tooling and sequential browser checks.

The complete frozen checkpoint passed **97/97 gates**, including build, type checks, lint and renderer/browser execution. The [publication checkpoints](docs/publication/20261012/README.md) contains exact tested revisions, source mapping, hosted-CI results and current PR/merge status. Counts from older checkpoints apply only to those historical revisions. The [2026-10-12 architecture follow-up](docs/delivery/product-behavior-and-ideas.md#architecture-follow-up) tracks newly reproduced defects and their concrete acceptance; the earlier pass does not close them.

The subsequent runtime-safety slice passed its [frozen UI quality and selected integration checks](docs/architecture/architecture-review-20261012.md#local-implementation-follow-up). **Visual acceptance failed:** the user rejected the fixture-art screenshot. The [implemented visual foundation](docs/product/yard-and-behavior.md#pb-011-c--separate-artwork-detail-from-world-size-and-restrain-the-ui) separates artwork detail from world size and simplifies the controls. Approved concept pixels remain blocked in Library materialization and have not been inspected; no 32px design approval or species-fidelity acceptance is claimed. The versioned source-density and layout code passed its own bounded checks; its fixture captures remain unapproved art.

## Remaining product dependencies

Approved detailed species art, real models and provider adapters, the original autonomous worker, physical hardware and worst-case performance acceptance remain open. Owner evidence and location stay private; sharing uses an explicit safe projection. The [task index](docs/delivery/product-behavior-and-ideas.md) owns acceptance and dependencies; add updates there instead of another parallel roadmap.
