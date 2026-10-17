# ChirpNeighbors functional placeables — batch 20261017-01

Twelve actual image-generated static object candidates, three preserved source sheets, twelve usable individual RGBA sprites, and checker/light/dark contact sheets. The objects are pedestal bath, ground bath, bubbler fountain, hanging seed tube feeder, cedar hopper feeder, platform feeder, nectar feeder, bench, empty terracotta pot, raised cedar planter, rain barrel, and hose reel.

`manifest.json` is the final intake delta. `inventory.json` and `INVENTORY.md` are the preserved pre-generation inventory snapshot. Merge the final delta into the established canonical tracker; this directory is not a replacement source of truth. Existing `object.cedar_feeder` and `object.bench` keep their identities and gain candidate variant lineage.

Source images are imagegen originals, copied without alteration from the provider's generated-images directory. Exact prompts (with one file-terminating newline omitted in `prompt_exact`, matching the tool call) and generation provenance are retained. Earlier Library style-reference ZIPs could not be downloaded because the proxy returned HTTP 403; no reference pixels were inspected or supplied. Their IDs are provenance only. No third-party license or model revision is invented.

`process_sheets.py` performs only reviewed rectangular crops, alpha-bound trimming, transparent padding and nearest-neighbor contact-sheet compositing. Initial quadrant crops crossed objects, so corrected object rectangles replaced those failed extraction attempts. No sprites were color-keyed, repainted or resynthesized. Each original has native RGBA transparency. Light and dark composites confirm clean backgrounds; soft contact shadows remain flattened into sprites.

Technical/crop/completeness review passed. Strict logical pixel-grid style conformity and owner canon acceptance remain pending. Dense shading and antialiased contours warrant style review. The nectar feeder's ruby glass/liquid appearance does not clearly distinguish colored glass from red liquid. Solar power on the bubbler is a proposed capability only; no solar panel or pump behavior is delivered.

The manifest records approximate image-observed placement pivots, ground-contact polygons, perch/feeding/water points, scale proposals, missing state/layer slots, wind attachments and region-appropriate seasonal applicability. Those coordinates and slots are metadata, not animation, collision, physics, water simulation or runtime alignment. All sprites are flattened; no independent body/shadow/water production layers are claimed. There are no authored dry/empty/wet variants or motion clips in this batch.

Not staged, integrated or accepted. Canonical intake is `pending_mac_verification`, with commit and remote SHA null. Mac application preservation and Git branches were untouched. Parent coordinates archive packaging, Library transport, Mac byte verification, canonical tracker import and Git checkpoint.
