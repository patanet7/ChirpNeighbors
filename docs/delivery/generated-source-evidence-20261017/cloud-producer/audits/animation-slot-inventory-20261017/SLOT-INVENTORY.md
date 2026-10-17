# ChirpNeighbors saved animation source inventory

Snapshot: 2026-10-17T21:48:13.463938+00:00. Audit scope is the saved 20-species source collection. New output from assigned workers must be reconciled separately.

**Baseline: 102 registered drawings = 84 bird + 18 scene/weather drawings, from 21 retained native originals and exact prompts.** All 20 species have source candidates: 18 provisional intakes and two study-only species. Selected inherited corvid sources are separate from the native bank.

**Useful provisional source slots:** 17 neutral presentations (including Dove/Quail still fallbacks), 10 look transitions and seven blink sequences. These 34 semantic uses overlap drawings; they are not 34 distinct animations or art approvals. Crow’s held stride, Nuttall’s support study and Junco’s resting eyes do not fill the useful neutral slot.

The inventory asks ten semantic questions per species (200 rows) so neutral, look, blink, feeding and drinking stay distinct. This is not a requirement to create 200 animations. No equal frame count, uniform duration or biological frequency ranking is imposed.

## Per-species source coverage

| Species | Saved coverage | Next gap or restriction |
|---|---|---|
| Anna's Hummingbird | Perched open/closed blink; one open look pose | Two wing drawings are a hover study only; stable continuous hover and flower contact missing. |
| House Finch | Male open/half/closed blink | Older look/feed drawings retained; feeding contact and kernel size unresolved; preen attempts failed. Rig tilt is not preen. |
| Lesser Goldfinch | Neutral + upward look | Blink and seedhead/perch locomotion missing. |
| Black Phoebe | Neutral + blink; separate tail-up/down poses | Tail pump provisional; dedicated look and drawn sally/landing missing. Existing sally recipe translates a static bird. |
| California Towhee | Neutral + blink + look | Four drawn hop poses assigned, not counted here. Old hop proof is rigid reuse. Upright bill cannot reach ground seed within inspected rotation bounds. |
| Mourning Dove | Held neutral; six-pose gait and five selected drink drawings | Weak gait alternation/root travel and water/beak contact remain unresolved. No neutral look/blink loop. |
| Northern Mockingbird | Neutral + upward look | Blink and short run/stop phases missing. |
| California Scrub-Jay | Neutral + upward look | Blink, hop and acorn/seed interaction missing. |
| Bushtit | Neutral + upward look | Blink and twig hop missing; feet/eyes occupy very few display pixels. |
| American Crow | One corrected stride held still | Useful neutral/blink/look missing. Four leg drawings remain a weak walking draft with unverified support/root travel. |
| Common Raven | Four inherited idle/blink/look drawings | Four-pose hop is an exploratory inherited source, without admitted movement/contact mapping. |
| Nuttall's Woodpecker | Two vertical-cling identity/look studies | Tail is13.83–14.14 world units from inferred toe support plane. Correct contact pair assigned, not counted. |
| White-crowned Sparrow | Neutral + genuine blink | Dedicated look and hop missing; slight raster/contact twitch needs yard review. |
| Yellow-rumped Warbler | Neutral + genuine blink | Look, branch hop/sally and foliage glean missing. |
| Hooded Oriole | Neutral + upward look | Blink, perch movement and flower-probe contact missing. |
| Western Bluebird | Neutral + downward look | Four drawn hop poses assigned, not counted. Blink and insect interaction missing. |
| Bewick's Wren | Neutral + downward inspection look | Blink, shrub hop and crevice-probe contact missing. |
| Spotted Towhee | Neutral + upward look | Blink, hop and double-scratch/ground-peck phases missing. |
| Dark-eyed Junco | Two resting/eyelid studies only | Both eyes narrow/closed: no useful awake neutral or completed blink. Awake pair assigned, not counted. |
| California Quail | Neutral still first; paired look retained as stance study | Visible stance/leg redraw and3.813 world-unit mask-centroid change; planted look loop unapproved. Blink and walk missing. |

The seven useful blink sources are Anna’s Hummingbird, House Finch, Black Phoebe, California Towhee, Common Raven, White-crowned Sparrow and Yellow-rumped Warbler. Junco’s file names do not override the actual closed/narrow-eye finding.

## Exact intakes and reusable mappings

`inventory.json` contains each source ID, source PNG/original/prompt path and hash, per-slot classification and missing phases. For 25 prepared manifest packages it records 62 atlas-frame mappings verified against the decoded RGBA of retained export files, full clip/tick timing, density, canvas, pivot and declared contacts. The selected intakes are listed below; alternate action packages remain explicit in the JSON.

| Species | Selected manifest | Selected atlas |
|---|---|---|
| Anna's Hummingbird | `motion/sd20-anna-actions-v1/texture-review-manifest.json` | `motion/sd20-anna-actions-v1/idle-atlas96.png` |
| House Finch | `experiments/house-finch-male-blink-runtime-assessment-v2/texture-review-manifest.json` | `experiments/house-finch-male-blink-runtime-assessment-v2/blink-atlas96.png` |
| Lesser Goldfinch | `new-species/sd20-next-three-canon-v1/lesser_goldfinch/texture-review-manifest.json` | `new-species/sd20-next-three-canon-v1/lesser_goldfinch/idle-look-atlas96.png` |
| Black Phoebe | `motion/sd20-phoebe-actions-v1/blink-manifest.json` | `motion/sd20-phoebe-actions-v1/blink-atlas96.png` |
| California Towhee | `motion/sd20-anna-phoebe-towhee-v1/california_towhee/actions/texture-review-manifest.json` | `motion/sd20-anna-phoebe-towhee-v1/california_towhee/actions/idle-atlas96.png` |
| Mourning Dove | `reuse/sd20-dove-reuse-v1/standing-manifest.json` | `reuse/sd20-dove-reuse-v1/standing-atlas.png` |
| Northern Mockingbird | `new-species/sd20-next-three-canon-v1/northern_mockingbird/texture-review-manifest.json` | `new-species/sd20-next-three-canon-v1/northern_mockingbird/idle-look-atlas192.png` |
| California Scrub-Jay | `new-species/sd20-next-three-canon-v1/california_scrub_jay/texture-review-manifest.json` | `new-species/sd20-next-three-canon-v1/california_scrub_jay/idle-look-atlas192.png` |
| Bushtit | `new-species/sd20-bushtit-wren-sparrow-v1/bushtit/texture-review-manifest.json` | `new-species/sd20-bushtit-wren-sparrow-v1/bushtit/idle-look-atlas96.png` |
| American Crow | `reuse/sd20-corvid-reuse-v1/american_crow/texture-review-manifest.json` | `reuse/sd20-corvid-reuse-v1/american_crow/atlas.png` |
| Common Raven | `reuse/sd20-corvid-reuse-v1/common_raven/texture-review-manifest.json` | `reuse/sd20-corvid-reuse-v1/common_raven/atlas.png` |
| Nuttall's Woodpecker | `new-species/sd20-woodpecker-warbler-oriole-v1/nuttall_s_woodpecker/texture-review-manifest.json` | `new-species/sd20-woodpecker-warbler-oriole-v1/nuttall_s_woodpecker/idle-look-atlas192.png` |
| White-crowned Sparrow | `new-species/sd20-bushtit-wren-sparrow-v1/white_crowned_sparrow/texture-review-manifest.json` | `new-species/sd20-bushtit-wren-sparrow-v1/white_crowned_sparrow/idle-look-atlas96.png` |
| Yellow-rumped Warbler | `new-species/sd20-woodpecker-warbler-oriole-v1/yellow_rumped_warbler/texture-review-manifest.json` | `new-species/sd20-woodpecker-warbler-oriole-v1/yellow_rumped_warbler/idle-look-atlas96.png` |
| Hooded Oriole | `new-species/sd20-woodpecker-warbler-oriole-v1/hooded_oriole/texture-review-manifest.json` | `new-species/sd20-woodpecker-warbler-oriole-v1/hooded_oriole/idle-look-atlas192.png` |
| Western Bluebird | `new-species/sd20-final-four-v1/western_bluebird/texture-review-manifest.json` | `new-species/sd20-final-four-v1/western_bluebird/idle-look-atlas192.png` |
| Bewick's Wren | `new-species/sd20-bushtit-wren-sparrow-v1/bewick_s_wren/texture-review-manifest.json` | `new-species/sd20-bushtit-wren-sparrow-v1/bewick_s_wren/idle-look-atlas96.png` |
| Spotted Towhee | `new-species/sd20-final-four-v1/spotted_towhee/texture-review-manifest.json` | `new-species/sd20-final-four-v1/spotted_towhee/idle-look-atlas192.png` |
| Dark-eyed Junco | `new-species/sd20-final-four-v1/dark_eyed_junco/texture-review-manifest.json` | `new-species/sd20-final-four-v1/dark_eyed_junco/idle-look-atlas192.png` |
| California Quail | `new-species/sd20-final-four-v1/california_quail/static-review-manifest.json` | `new-species/sd20-final-four-v1/california_quail/neutral384.png` |

All paths above are relative to `/workspace/asset-production/`. The canonical source prefix is `docs/delivery/generated-source-evidence-20261017/cloud-producer/`.

## Existing attempts worth reusing

- **Dove:** six actual gait drawings and five selected drinking drawings are packaged; the sixth recovery drawing remains retained. Gait is stepped, with weak alternation. Drinking foot proxies drift up to 3.25 world units; the low bill spans x147.5–149.25, y151.25–151.75 in the proposed density 1 export. Match support and water targets before claiming an interaction.
- **House Finch:** 12 male/female feeding drawings and older attention poses remain available. Oversized kernels, pickup/crushing timing and source contour/feet drift are unresolved. Six new female preen drawings plus reused neutral failed contact/body/return review. The single-canvas repair also failed.
- **Finch rig proof:** fixed-body head rotation and neck cleanup add zero drawings and establish only controlled attention tilts. Jaw/neck seam and overlap judgment remain open. Do not relabel the result preening.
- **Phoebe/Towhee transform proof:** each uses one static drawing, stationary planted phases, 11 airborne ticks and exact root landing in an offline geometry proof. It supplies no new crouch, push-off, wing or landing drawing and establishes no live movement binding.
- **Crow/Raven:** four Crow leg poses are a weak optional walking draft. Four Raven hop poses have real posture changes but large wing/body variation and remain exploratory. The inherited IDs are distinct from newly generated art.
- **Anna:** the two real wing poses have a stylized one-tick-each hover study. This may strobe and does not complete hovering, takeoff, landing or nectar contact.

## Review and verification limits

All 102 registered PNG hashes and decoded RGBA IDs recomputed successfully. All 62 prepared atlas crops match their retained mapped exports. All 121 declared contact samples have positive alpha. These checks prove data lineage and technical registration; they do not certify toe anatomy, planted support, branch grip, physical scale or target interaction.

Prior independent review receipts cover actual proposed display sizes and enlarged crops. This audit reads those receipts; it does not claim a fresh continuous human playback review. Natural drawings may change body pixels and feathers. Exact whole-body equality is not a universal art gate.

**Current app binding and actual yard verification are unknown here.** Parent/Mac is integrating concurrently. Historical source flags saying false are not evidence that nothing has since been bound. No source slot is promoted to production art acceptance by this audit.

## Yard pack and concrete next production

Pinned canonical source metadata declares 41 object variant records across 38 primary IDs, 30 whole-plant variants, 22 tree/leaves variants and 20 background originals including held/history. Three clean starter foundations and nine reused whole sprites are available. These are source counts, not completed wind rigs, universally editable scenery or verified Mac composites.

The exact metadata pin and files are in `yard-metadata-read-receipts.json` and `canonical-yard-metadata/`. The local 18 scene/weather drawings comprise six mixed understory poses, six rain patterns and six failed continuity revisions. The mixed clump has drifting roots/geometry. Requested rain advection failed (mean mask IoU 0.051, loop 0); exact extraction did not fix temporal continuity.

**Recommended bounded yard batch:** three real wind poses of the revised Purple Needlegrass clump, using `yard-reference/purple_needlegrass__healthy_seed_morphology_r01.png`. The source is a morphology-improved provisional candidate, not the held fluffy-plume version. Root [540,1252] on a 1080×1293 RGBA canvas; footprint ellipse radii [151,22]. PNG SHA256: `ad9634f39e911fbe70389b91c6f867d16bb7cd5e3fc9be60bb73331c81e5ed73`.

Its actual gap is `foliage_wind_groups: needed_not_separated`; it is currently one flattened still with no rooted wind cycle. Preserve root/base and awn attachments at one full-canvas scale; inspect calm/right/left/recovery playback at a declared yard presentation size. Whole-clump pose drawings would add a bounded wind candidate, not an independently editable foliage hierarchy. The earlier source metres are illustrative and must not be treated as bird world pixels.

The same folder retains source intake geometry, exact prompt and provenance. References are factual Jepson/USDA text; no botanical photo pixels were used. Generated-source rights remain under applicable service terms, without a CC/public-domain assertion. Hidden red RGB residues are below alpha 8 and not visible art; preserve RGBA and inspect explicit composites.

Other bounded yard tasks in `yard-pack-inventory.json`: one coastal flex group separated from wood; deterministic advection of an existing rain field; held oak canopy attachment; one bath ripple/disturbance layer with a known water plane. This audit starts none of these tasks and makes no claim that another worker is running them.

## Checkpoint queue

Assigned but uncounted: Junco awake/blink pair; Nuttall corrected trunk-contact pair; California Towhee four-pose hop; Western Bluebird four-pose hop. After those results, prioritize a true Crow neutral/blink, common missing blinks and species locomotion. Reuse Dove/Finch contact candidates deliberately before repeating failed generation requests. Preen and transit follow useful core activity.

The coordinator owns the single queue and publication. This audit changed only its own output folder; no global bank/matrix/queue, Git publication, Library write or image generation occurred.
