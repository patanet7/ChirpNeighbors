# Approved art

This folder is the only approved art. Nothing else in the repo counts as approved.
Layout, file rules and the manifest are specified in [`docs/ASSETS.md`](../../docs/ASSETS.md).

- `birds/<species>/` — `bird.json`, `canon.png`, `clips/<action>/<variant>/NN.png` + `clip.json`
- `objects/<object>/` — `object.json`, `<variant>.png`
- `scenes/<yard>/<season>/<layer>.png` — painted yards (kind `scene`), owned by the scenes track; geometry lives in the app (`REGIONAL_YARD_SCENES`)
- `approved.json` — every approved file (sha256, source, dates, review slot)
- `regen-queue.json` — slots the owner sent back, and approvals that could not become clean frames

Nothing is copied here without an owner decision: `node scripts/art-sync.mjs --decisions <export.json>`
copies approved picks in; `node scripts/approved-art-check.mjs` verifies the folder.
