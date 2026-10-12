# Illustrative environment contracts

`environment-controls-v1` and `environment-frame-v1` are additive structural
boundaries for temporary owner preview controls and decorative scene samples.
The existing stored weather settings, `WeatherFrame`, legacy `resolveWeather`,
yard backup v2 and previous portable contracts remain unchanged. No migration is
required. Preview controls are not saved to the yard, backup, account or public
share; the UI must label their temporary scope and reset them on navigation.

`resolveEnvironment(settings, atMillis, controls)` uses the existing weather
epoch, simulated day length and seed plus the caller's existing scene clock.
It never reads ambient time or randomness, requests location, fetches a provider,
or changes observations, residents, saved object coordinates or their timestamps.
The `real` mode stays explicitly unconfigured and neutral even when preview
overrides are present. Preview overrides produce a `manual` source label.

The default controls follow saved weather. Overrides allow clear, cloudy, rain,
snow or fog, a fractional illustrative hour and independently normalized cloud,
rain, snow, fog and wind strengths. Null means follow the corresponding preset.
Effects are dimensionless; they are not physical rainfall, visibility or wind
measurements. The transition interval is bounded to 0–30 seconds. Zero requests
an exact deterministic target sample. Saved simulation seed drives stable
particle anchors across days, so a day rollover does not reshuffle every effect.

The illustrative solar cycle uses the existing dawn 05:00–08:00, day
08:00–17:00, dusk 17:00–20:00 and night phase boundaries. Continuous daylight and
warmth curves cross those labels without lighting jumps. The sun's x coordinate
spans the sky width and y spans sky top (0) to horizon (1); both are normalized.
This is neither astronomical sunrise nor a regional calendar model.

Simulated weather blends the preceding day's preset into the current day's
preset during the beginning of the shared cycle. `blendEnvironmentFrames`
supports manual changes and interruption: supply the current sampled frame and
the new target, then advance raw progress with the renderer's existing active
animation time. Its smoothstep is internal. Paused or hidden animation must hold
that progress; it must not accumulate catch-up motion. Hour interpolation uses
the shortest 24-hour arc; exactly opposite hours choose the negative arc.

Frame condition/source labels can describe a destination while effects are
blended. Rendering and behavioral eligibility must consume the sampled rain,
snow, fog and wind strengths rather than treating a destination enum as an
instant effect change. `environmentLighting(hour, effects)` recomputes coherent
lighting if the renderer combines separately interpolated clock/effect channels.
There is no lightning, flash or strobe channel. Reduced-motion policy belongs to
the renderer and must keep an honest static sample rather than animate a hidden
second clock.

Schemas reject unknown fields, location/private evidence, unsupported provenance,
nonfinite/out-of-range values and effect overflow. They prove shape only: the
resolver tests cover temporal continuity, exact replay, pre-epoch cycles,
midnight transitions, opposite-hour ties, real-mode neutrality, explicit
progress, interruption, bounds and immutability. Renderer, behavior and browser
tests remain necessary for actual layer ordering, paused/background behavior,
pixel readability, accessibility and environmental eligibility.
