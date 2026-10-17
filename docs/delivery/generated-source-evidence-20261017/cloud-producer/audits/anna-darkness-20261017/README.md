# Anna source/export darkness audit

No export darkening transform was found. All five retained1024→96 outputs exactly match the selected source RGBA pixels. Visible registered pixels also map exactly back to the original generated atlases. Source images were not edited.

Mean visible sRGB code-value luma (not physical luminance):

| Pose | Source | Output96 | Change |
|---|---:|---:|---:|
| Original canon |98.15|96.31|−1.84|
| Blink |96.59|97.90|+1.32|
| Look |97.59|98.54|+0.96|
| Hover up |98.26|97.33|−0.92|
| Hover down |95.38|95.88|+0.50|

These small mean changes come from which pixels nearest sampling selects; selected pixels are unchanged. Pale breast feather specks already exist in the generated sources. Threshold/component diagnostics in `audit.json` describe this texture and sampling, not art acceptance or screenshot causality.

Scale is a separate variable: the original canon declares density1.2941 and34world-unit visible width; actions declare density1.5 and32.67world-unit perched width. `comparison.png` shows both published sizes and a common1.5density control. The common control is64×64canvas, not a per-body34unit fit.

The owner screenshot was not retrieved/retried or seen. This audit cannot identify its brown feeder bird, diagnose overlap, or rule out Mac tint/opacity/blend/color-space/scale behavior. Mac owns that investigation.

Next proposed control: compare one unchanged PNG/frame in direct and actual-yard renders with matching size/background/DPR, recording render parameters and removing overlap ambiguity. Only afterwards, if requested, test a same-identity lower-frequency feather-texture alternative. No art calls, model changes or runtime changes were performed.

Reproduce local diagnostics with `python3 build_audit.py`. It reads existing sources and writes only this audit directory.
