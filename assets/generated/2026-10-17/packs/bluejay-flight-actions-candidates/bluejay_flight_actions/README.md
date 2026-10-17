# Blue jay takeoff, flight and landing candidates

Three genuine built-in image_gen calls produced 18 distinct drawings from the canonical blue-jay reference. Pose imagery is generated; assembly scripts only extract alpha-connected sprites, translate into padded frames, uniformly downscale for runtime and encode previews. No generated pose is repainted, warped or synthesized by scripts.

## Deliverables
- Original generation sheets and canonical reference, exact prompts.
- 18 source-pixel 768x768 RGBA master frames.
- 18 runtime 512x512 RGBA frames, one shared nearest-neighbor scale of 2/3 in both axes.
- Three master APNGs, three runtime APNGs, three runtime atlases, three GIF previews and labelled contact sheets.
- JSON manifest with durations, exact source-to-master translations, shared runtime scale, estimated hip anchors, contact estimates, suggested external root trajectories and transition intent.
- Assembly script and SHA256 hashes.

## Motion and placement
Hip/body root is held constant at master (430,420); root travel is explicitly separate metadata and NOT baked into GIF or APNG. Takeoff and landing previews repeat solely for review; use as one-shots in the app. Flight is cyclic. Apply scene-specific world movement externally. Ground contact anchors are estimates, not verified garden-placement coordinates.

## Review findings
Takeoff visibly crouches, pushes off, alternates wings and tucks legs. Flight includes real high-wing, descending, low-wing and recovery drawings with a level body. Landing extends feet, brakes with wings, contacts and folds wings. These are candidates: anatomy/face/feather drift persists, broad white-tipped flight feathers simplify canonical markings, landing has layered feathers requiring anatomy review, and clips have nonidentical transition endpoints. The six-pose cadence is stepped. Flight phases 3 and 4 are similar downstroke variants. No per-frame scaling was used to hide body drift. No opaque source pixels or alpha-connected silhouette pixels were cropped in assembly. Some source-sheet low-alpha fringe touches image edges.

Validation confirmed all six-frame GIF/APNG structures, 18 unique master payloads, all source component pixels retained, and runtime frames <=512px. Contact sheets inspected after assembly. Actual in-app playback and garden placement remain unverified. No Mac integration performed.
