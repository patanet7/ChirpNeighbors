# Approved art

This folder is the only approved art. Nothing else in the repo counts as approved.

- Layout: `<species>/<action>/` with `<action>-NN.png` frames, or `canon.png` for canons.
- Objects: `objects/<slot>/<rank>-<candidate>.png`, the exact picked image for every variant the
  owner kept (kind `"object"`, `variants` = file count). The app crops and scales them at intake.
- `approved.json` lists every approved slot (files + sha256, size, frames, fps, source pack/path,
  decision time, review URL) and a `pending` list of slots the owner sent back for regeneration.
- How entries get added: the owner decides on the review page; the pick is copied here and
  recorded in `approved.json`. Nothing is copied here without an owner decision.
- Generated packs under `assets/generated/` and `docs/delivery/` are archive, not approved art.
- Check: `node scripts/approved-art-check.mjs` (files exist, sha256 matches, no unlisted files).
