# Cardinal hop and sleep candidates

Two native image-generated six-pose sheets. Visually inspected alpha composites and extracted contact sheets. Hop has real crouch, tail counterbalance, extended launch legs, curled airborne feet and forward landing legs. Sleep has eyelid closure, beak/neck tuck into shoulder/back feathers, rounded body, waking ruffle and alert recovery.

NOT production approved. Anatomical scale/silhouette drifts between generated poses despite fixed canvas and no per-frame scaling. Hip anchors are manually estimated for hop; sleep uses estimated ankle contact. Landing and settle need foot-contact refinement. Hop is an in-place loop with a separate vertical root-motion curve; no net horizontal travel is implied. The native pose APNG does not apply this curve; preview motion APNG/GIF does. This is articulated generated artwork, not deformation of a static bird. Sleep tuck and eye state are clearly distinguishable, but ruffle is exaggerated and feather layout changes.

Original native sheets, exact prompts, canonical source and full-resolution extracted frames retained. Runtime derives every frame using exactly 0.5 nearest-neighbor scale, not bounding-box fitting. Native frame canvas 640x576; runtime frames 320x288; runtime atlases 960x576. Preview motion canvas 320x320 adds room for hop. Alpha retained for PNG/APNG, GIF composited pale green.
