# San Diego yard batch intake

Three distinct yard concepts: coastal urban, inland canyon edge, and sheltered outdoor managed patio. Six generated originals (RGB flattened bases plus independent true-alpha foreground edges), six extracted corner sprites, three composite previews, and light/dark contact sheets are included with exact prompts and source hashes.

This is an intake delta for the established canonical ledger. Canonical IDs remain `scene.san_diego_coastal_urban`, `scene.san_diego_inland_canyon`, and `scene.san_diego_managed_patio`. Content/variant versions describe these candidates. No competing Git changes or application edits were made. Mac verification, commit, remote SHA and PR evidence remain pending.

Open `index.html` or `previews/yard-contact-light.png`. The bases are flattened: sky, wall, ground and baked plants are not semantically separated. Separate foreground overlays and their left/right crops are real alpha assets, independently generated rather than segmented from bases. Each crop records its exact source offset.

Technical and visual reviews are recorded. The originals decode at 1536×1024; all three overlays have actual RGBA alpha and fully transparent center pixels. Known defects remain: painterly/high-resolution texture in bases, soft overlay halo and faint stray alpha, foreground dimensions exceeding prompt constraints, and approximate scene alignment/style. These are review candidates, not accepted art.

Every state, interaction, scale, footprint and wind-rig field is production metadata or a proposed placement. No weather, seasonal animation, physics, feeder/bath coupling, runtime staging or integration is implemented here. Bird art is handled separately.

Reference ZIP pixels were blocked by the Library download proxy (HTTP 403), so no existing visual reference pixels were inspected or supplied. Provenance IDs and readable regional plan text are recorded. No standalone image-generation skill was available; actual art was generated through the exposed `image_gen.imagegen` tool. No Blender or code-painted art.
