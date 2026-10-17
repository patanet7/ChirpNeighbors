# Cloud-produced source artwork — exact-byte preservation

This directory retains actual project source bytes for the canonical repository.
It contains 11 native generated originals and their exact prompts, 57 registered
drawings, separate PNG frames, nine APNG/GIF review clips, atlases, contact sheets,
current candidate manifests, review findings and technical processing sources.
These are source evidence: **zero local batches are admitted, integrated into the
Mac app, or accepted as production artwork.** No catalog/default/pin, renderer,
runtime contract or existing Mac integration is changed by this archive.

`original-source-inventory.json` records every original and prompt SHA-256, byte
count and source dimensions. All originals match a second native generator-output
copy in the producing workspace. `source-files.sha256.json` inventories every
retained file with its stable byte digest; it excludes itself to avoid a circular
hash. `frame-bank.json` is the retained producer pixel-evidence register, subordinate
to canonical app identities and admission. Its frame IDs hash decoded RGBA plus
dimensions; file SHA-256 is separate. None of its proposed reuses is verified.

The source folder structure is preserved so that candidate manifests and source
frame references resolve. Generated originals, prompts, manifests and frames are
copied without rewriting their bytes. Older processing scripts retain their
original workspace paths as historical source; use the portable verifier below
to verify this archive rather than running those packaging scripts in place.

```sh
python3 verify_source_files.py
# Optional decoded identities and animation frame counts; requires Pillow:
python3 verify_source_files.py --pixel-checks
```

The verified source archive is 78 MB across small individual files (largest under
2.5 MB). Rejected rain continuity and the failed perch registration are retained.
Passing hashes/decoding proves recoverable source bytes, not anatomy, contact,
scale, temporal quality or production acceptance. Original prompts do not expose
a deterministic model/seed guarantee.

## Prior crow source access

The three external compact/guided crow references are **absent**, with no invented
source hashes. Fresh supported Library materialization attempts failed with
`URLError: Tunnel connection failed: 403 Forbidden` at network tunnel setup.
No payload reached an image/ZIP decoder. This is an observed proxy transport
denial; it does not establish an application permission denial, URL expiry,
missing origin file or unsupported format. The earlier helper exposed only
`library file transfer failed: download failed` (exit 1).

`source-access-diagnosis.json` and the three `transport-*.jsonl` files retain the
safe operation/error evidence. No alternate proxy, disabled proxy, raw URL route,
escalation or credential change was attempted after the observed denial. Private
Library handles, transfer credentials and URLs are omitted from this public
projection; the exact original receipts remain with the private handoff.

The bounded crow experiment used **zero** new generation calls. Its technical
fixture passes three authored-arithmetic checks only. Its scale/contact points
remain unbound to crow pixels; no candidate before/after motion or acceptance is
claimed. The queued next action is accessible prior source bytes plus matched
scale/root/contact data, then a concrete controllable method before generation.

## Mac handoff

This additive source branch is for parent/Mac-owner review and placement into the
chosen versioned asset storage. Mac owns runtime admission and any merge with its
ongoing reconciliation. File hashes allow exact deduplication with Mac-held
sources. The private complete checkpoint inventory separately rehashed all 244
files from the earlier preservation checkpoint; this public folder deliberately
contains generated project media and technical evidence, rather than personal
research catalogs, Library identifiers, recordings, databases or credentials.
