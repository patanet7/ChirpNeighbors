# Blue jay directional attention candidates

Four independent imagegen head edits plus unchanged neutral PNG. Staging experiments only.

Contact sheet: neutral, up, down, viewer three-quarter, back. Top rows are light/dark at inspection size. Bottom rows use a common approximately 72px baseline silhouette width, nearest-neighbor scaling.

All five original PNG bytes are preserved. Composites and contact sheet are previews only. No video, image cleanup, runtime integration, production approval or complete direction coverage is claimed.

The head poses read at target scale and feet retain near-identical geometry, but the generator redraws nearly all visible pixels. Foot centroid drift is below 1 source pixel per axis (under 0.06 target pixels); bounding-box drift reaches 1 source pixel. Body centroid drift reaches 1.40 source pixels (0.077 target pixels) and its right bbox edge shifts as much as 6 source pixels (0.33 target pixels). Measurements are mask summaries, not actual contact correspondence. Backward pose needs neck/anatomy review.

See manifest.json for coordinate conventions, proposed event hold timings, measurement limits and warnings; prompts.json for exact prompts and generation provenance. The provenance directory preserves inspected blink-pack metadata, not blink frames.
