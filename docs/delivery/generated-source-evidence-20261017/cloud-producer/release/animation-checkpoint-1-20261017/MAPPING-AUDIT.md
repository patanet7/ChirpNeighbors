# Current intake projection audit

Confirmed **3 atlas byte mismatches**. Source art and manifests were not edited. The proposed projection keeps reusable source IDs separate from render exports and current Mac binding unknown.

| Species | Wrong atlas | Correct atlas |
|---|---|---|
| american_crow | `reuse/sd20-corvid-reuse-v1/american_crow/atlas.png` | `motion/sd20-crow-neutral-blink-v1/neutral-blink-atlas192.png` |
| spotted_towhee | `new-species/sd20-final-four-v1/spotted_towhee/idle-look-atlas192.png` | `motion/sd20-spotted-towhee-blink-v1/idle-blink-atlas192.png` |
| dark_eyed_junco | `new-species/sd20-final-four-v1/dark_eyed_junco/idle-look-atlas192.png` | `motion/sd20-junco-awake-v1/idle-blink-atlas192.png` |

Three awake-pair neutral slots and one Nuttall neutral-study slot incorrectly contained multiple source states; proposed neutral uses the open source only. Blink retains its exact ordered open→closed→open source/tick sequence. Look bindings retain their actual manifest/clip rather than being silently spliced into a new neutral pair.

Towhee hop uses **five unique playback sources: four new poses plus its reused old neutral**, six sequence steps,29ticks at30Hz. Bluebird hop uses four new sources and excludes its old neutral comparison from playback. These are reviewed one-shot studies, not admitted full locomotion.

Verified 29 exact packages, 70 atlas frames and 139 alpha-positive contact samples. Shape/alpha checks do not establish anatomical support or runtime acceptance.

The proposed Python updater rebuilds from frozen baseline plus current reviewed overlay. It handles incoming closure-only batches by changing blink coverage only. It writes into its own directory by default; the coordinator must explicitly set `--output-dir` for publication. The audit did not run it against any global output target.

`mapping-audit.json` contains exact mismatches and checks. `CURRENT-SLOT-INVENTORY.proposed.json` is the corrected projection. Actual source art hashes, density, world canvas, timing, contact shapes and output→source mappings are retained in its prepared packages.
