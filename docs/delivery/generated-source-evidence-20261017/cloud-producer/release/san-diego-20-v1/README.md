# San Diego first release:20decent recognizable birds

Exactly20species are the release target. This is a production roster, not20finished/admitted birds. Core18 are retained; Dark-eyed Junco and California Quail are promoted from existing expansion research. Habitat/season tags are qualitative source-based eligibility, not encounter probabilities.

|Species|Tag / context|Movement minimum|Interaction minimum|Existing source|
|---|---|---|---|---|
|Anna's Hummingbird|resident; resident; individual movements|hover/dart, with hovering clearly labelled rigged if used|flower nectar probe; beak/flower contact required|missing; queued|
|House Finch|resident; resident|short grounded hop with planted/airborne phases|seed inspection/peck; beak/seed point required|house-finch-male-idle-v1, house-finch-male-feed-v1, house-finch-female-idle-v1, house-finch-female-feed-v1, house-finch-male-blink-runtime-assessment-v2|
|Lesser Goldfinch|resident; resident; wandering flocks|short hop between seedhead/perch|seedhead pluck|missing; queued|
|Black Phoebe|resident; resident|short insect sally and return|airborne insect catch; no seed-feeder peck|missing; queued|
|California Towhee|resident; resident|ground hop|leaf-litter scratch/ground peck|missing; queued|
|Mourning Dove|resident; resident plus seasonal movement|alternating ground walk|water-edge drink or seed peck|dove-walk-v1, dove-drink-v1|
|Northern Mockingbird|resident; resident|short ground run with stops|berry inspection/pluck|missing; queued|
|California Scrub-Jay|resident; resident; habitat dependent|short hop|acorn/seed cache inspection|missing; queued|
|Bushtit|resident; resident; roaming flocks|twig-to-twig hop|foliage insect glean|missing; queued|
|American Crow|resident; resident|walk if alternating feet read; otherwise labelled short rigged hop|ground-item inspect; no unsupported ingestion claim|chirp-guided-cycle-candidate|
|Common Raven|resident; resident|walk or short rigged hop with contact review|ground-item inspect; preserve raven bill/throat identity|crow-raven-first-motion|
|Nuttall's Woodpecker|resident; resident; trees required|short upward trunk hitch|bark peck at trunk point|missing; queued|
|White-crowned Sparrow|seasonal; primarily cool-season visitor in target lowlands|short ground hop|seed/leaf-litter peck|missing; queued|
|Yellow-rumped Warbler|seasonal; primarily cool-season visitor in target lowlands|short branch hop/sally|foliage insect glean|missing; queued|
|Hooded Oriole|seasonal; primarily spring/summer visitor|short perch-to-perch flight/hop|flower probe; not generic seed crack|missing; queued|
|Western Bluebird|resident; resident/local seasonal movements; conditional yard visitor|short ground drop and return|ground insect inspection/catch|missing; queued|
|Bewick's Wren|resident; resident|shrub hop|crevice insect probe|missing; queued|
|Spotted Towhee|resident; resident with seasonal redistribution|ground hop|double scratch or ground peck|missing; queued|
|Dark-eyed Junco|seasonal; cool-season visitor in target lowlands; local resident breeding populations also documented|ground hop|seed peck|missing; queued|
|California Quail|resident; resident; conditional on connected native scrub/ground habitat|short ground walk|ground seed/green peck|missing; queued|

The recognizable standing/idle/look minimum and exact available source/frameIDs are in `roster.json`. Rigged motion and repeated frames may satisfy implemented movement only after observed runtime behavior; they remain labelled and add0newdrawings. A static still is an honest temporary preview, not completed locomotion. No incorrect species art substitutes for missing art.

BatchSD20-reuse-01: male House Finch blink,3existingdrawings,96px fullRGBA,30Hz. Independentnormal-speed samples coherent; owner provisionally accepts continued normal-size use. Current Mac `/candidate-yard` suppliedPNG/manifest → canonicalSharpreceipt → verified `reviewTexture` uses the existing yard renderer. No Mac integration has been performed by cloud. Standing/look andfeeding sourceIDs are retained; hop and contact-bound interaction are still missing from runtime admission.

Next batchSD20-reuse-02: MourningDove/AmericanCrow/CommonRaven source reuse. Source access is resolved for recoveredcrow, exactravenIDs needparenthandoff. New3speciesAnna/BlackPhoebe/CaliforniaTowhee remain queued, not running. No image generation call was made for this roster/batch.

Local primary source additions rechecked: [Dark-eyed Junco](https://sdplantatlas.org/birdatlas/pdf/Dark-eyed%20Junco.pdf), [California Quail](https://sdplantatlas.org/birdatlas/pdf/California%20Quail.pdf). The other18species retain their SDNHM atlas references and supporting Cornellbehavior sources from the existing regional research. No current abundance asserted.
