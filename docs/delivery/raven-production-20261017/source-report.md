# Raven sprite generation and reuse in ChirpNeighbors

> Public redacted copy: private Library file identifiers and the pet identifier
> have been removed. This is not a verbatim copy of the original report. The full
> original is retained in a private preservation archive; its SHA-256 is
> `abe31d2da56d1932a0cd044664cc4a116a7d30d3b33c250b1b9f5e615ac21525`.
> The accompanying manifest records this redacted copy's separate byte count/hash.
> Generic artwork prompts, production techniques and reported results are retained;
> the report's atlas-validation and lifecycle statements remain attributed source
> claims, not independent verification by this project.

## Purpose and current result

This report documents how the charcoal raven artwork was developed into a set of animation sprites, the failures encountered during production, and a practical way to reuse the approach in ChirpNeighbors.

The central lesson is to separate character design, pose generation, image extraction, animation registration, and runtime packaging. A good-looking generated strip is not automatically a usable animation. The most important repairs in this run addressed cropping, bird anatomy, and body-size consistency rather than image resolution.

Status as of the completed asset validation on 17 October 2026:

- The user-approved canonical raven and all eleven animation rows are complete: 57 ordinary animation frames plus sixteen directional gaze frames, for 73 populated frames.
- The final RGBA PNG is 1536 × 2288 pixels and 3,483,774 bytes. Its SHA-256 checksum is `417b05c1d6ec3c71755c5d2f3ffea79c1bbc3dac12242de9c539588b556f3e8c`.
- Structural validation, final quality checks, and the Pets service validator passed; the service returned `valid: true`.
- Motion previews are available as a GIF and MP4. After the motion preview was sent, the custom pet was created as `<PRIVATE_PET_ID>` and selected as dot’s avatar. The separate Work-mode pet selection was not changed.
- One directional nuance remains recorded: the 292.5-degree gaze has an ambiguous vertical cue in blind review. Labeled review accepted the shallow upward beak and chin angle, with the warning retained.

This document distinguishes observed results from recommendations. Implementation examples below are newly written, generic examples; they are not the exact software used by the generation environment.

## Character identity and visual language

The approved reference is a compact, full-body raven with layered warm charcoal feathers, cream highlights, restrained copper glints, expressive dark eyes, a stout dark beak, visible feet, and an alert, slightly mischievous bearing. The identity is carried by the silhouette, head-to-body ratio, feather layering, beak shape, and warm highlight distribution.

The artwork is pixel-art-adjacent illustrated sprite art: stepped contours and a strong silhouette coexist with comparatively detailed feather shading. It should not be described as a rigorously hand-pixeled, fixed-palette asset. A ChirpNeighbors renderer that expects strict pixel grids or a very small palette may need an additional deliberate art conversion step.

The visual exclusions mattered: no accessories, badges, text, handheld props, or blue-purple science-fiction coloring. These restrictions kept the character recognizable across behavior changes. A waiting animation, for example, needed to remain a bird waiting, rather than become a humanoid character acting out impatience.

The approved preview is recorded in Library as `<PRIVATE_LIBRARY_FILE_ID>`. This is an asset identifier, not a public download URL. The measured canonical reference is 1206 × 1305 pixels in RGB; its preview is the same size in RGBA. These source dimensions are distinct from the much smaller runtime frame dimensions.

## Generation method and reproducibility limits

Artwork was produced using the built-in image generation tool, with reference images grounding subsequent generations. The underlying model identifier and random seed were not exposed for this run. There is therefore no honest model-and-seed command that can reproduce the exact images byte for byte.

The portable part is the method and the saved assets. Keep the approved reference image, the generated source strips, accepted frame images, rejected examples, and a record of what changed between attempts. For production reuse, add hashes and revision identifiers to those assets. Regenerating from a descriptive prompt alone is a weaker guarantee of continuity than preserving the approved source image.

The dependency structure was:

1. Establish and approve the single canonical raven.
2. Generate state-specific pose sequences grounded in that raven.
3. Extract, register, and review the nine ordinary state rows together.
4. Establish cardinal gaze anchors against the same identity and established animation scale.
5. Generate the intermediate gaze directions using those anchors and continuity references.
6. Assemble the full atlas only after frame and animation review.

Reference images served different purposes. The canonical raven defined identity. Layout references suggested separation and frame arrangement. The ordinary-row contact sheet helped compare scale and anatomy across states. Cardinal anchors constrained directional meaning. Keeping these roles separate reduces the risk that spacing guides become visible artwork or that a changed pose becomes a new character design.

The built-in generation interface and the packaging tools used in this environment should not be assumed to exist in ChirpNeighbors. A portable implementation needs its own image-generation integration, extraction code, asset manifest, validation, and runtime animation controller.

## Animation inventory

The nine ordinary states use 57 populated cells:

| Row | State | Frames | Behavior represented |
| --- | --- | ---: | --- |
| 0 | idle | 6 | Quiet breathing and blinking |
| 1 | running-right | 8 | Rightward travel |
| 2 | running-left | 8 | Leftward travel |
| 3 | waving | 4 | Greeting with a wing |
| 4 | jumping | 5 | Small folded-wing hop |
| 5 | failed | 8 | Downcast or blocked reaction and recovery |
| 6 | waiting | 6 | Attentive waiting with natural folded wings |
| 7 | running | 6 | Active work or processing, distinct from locomotion |
| 8 | review | 6 | Attentive review or ready-to-present behavior |

State names here describe this atlas contract. ChirpNeighbors should map them to its own gameplay or interaction concepts rather than treating every name as a universal animation standard. In particular, `running` is a work state, while `running-right` and `running-left` are travel states.

The contact sheet visibly shows a consistent warm-feathered character and recognizable differences between most actions. It is useful for anatomy and silhouette comparisons; it cannot establish motion smoothness or timing by itself. The final motion previews allow playback review in addition to the contact sheet. User acceptance of the preview remains separate from structural validation.

## Sixteen direction gaze design

The completed gaze set consists of sixteen targets at 22.5-degree increments. The convention is screen-oriented: 0 degrees is up, 90 is right, 180 is down, and 270 is left. Directions increase clockwise.

The first gaze row contains 0, 22.5, 45, 67.5, 90, 112.5, 135, and 157.5 degrees. The second contains 180, 202.5, 225, 247.5, 270, 292.5, 315, and 337.5 degrees.

The intended mechanics are neck and head movement on a stable body. Feet, torso, folded wings, and tail remain planted. The beak gives the strongest directional cue; eye placement follows naturally, including partial occlusion of the far eye in sideward views. Upward gaze raises the beak, while downward gaze tucks it toward the chest. This is a gaze set, not a whole-body turntable.

Four cardinal anchors were checked before intermediate directions. Their registered source is 768 × 208 pixels, corresponding to four 192 × 208 cells. The anchor review reports nonempty poses with zero occupied outer-edge pixels for each anchor. Final blind-majority review passed all four cardinal directions. The 292.5-degree intermediate direction remained ambiguous in its vertical cue during blind review; labeled review accepted the shallow upward beak and chin orientation, retaining that warning. This is a limitation to inspect at ChirpNeighbors display size rather than a claim that every direction is equally clear.

For ChirpNeighbors, test direction selection with the actual pointer, target, or neighbor location. At small display sizes, adjacent directions can become visually indistinguishable. If sixteen poses add little perceptual value, eight directions with hysteresis may be more stable. That is a product recommendation, not a change already made to this raven.

## Chroma extraction and frame registration

Source artwork used explicit magenta, RGB 255, 0, 255, as the removable background. Magenta is well separated from the raven's charcoal, cream, and copper palette. Final frame images use transparency.

The accepted ordinary-row review identifies connected-component extraction for all nine rows. This is important because generated poses did not necessarily honor exact equal-width source slots. Dividing an image into equal rectangles before locating the actual birds can cut a tail or assign part of one bird to its neighbor.

A reusable extraction system should locate foreground poses first, then register each complete pose into its destination cell. Small detached components such as toes or feather tips may belong to a nearby bird, so blindly taking only the largest component can also damage the artwork. Group components spatially and review their combined bounding boxes.

Registration has several separate responsibilities:

- Preserve the complete silhouette, including tail and extended toes.
- Maintain a consistent body scale across related frames.
- Stabilize the foot baseline for grounded behavior.
- Preserve intentional airborne displacement during a hop.
- Leave enough transparent padding for the largest motion extent.
- Place each registered frame in the correct sequence.

Do not independently stretch every bounding box to fill its cell. A wing extension changes the bounding box without implying that the torso should become smaller. Where possible, estimate scale from stable anatomy or use a common scale for a sequence. Maintain explicit pivot metadata so the runtime can place grounded and airborne frames consistently.

Chroma removal also needs edge review. Antialiasing can blend magenta into feather-edge pixels. The ordinary-frame report contains a `chroma_adjacent_pixels` diagnostic despite reporting no warnings. That number is not proof of visible spill, nor proof that the edge is clean. Inspect the sprites on light, dark, and saturated backgrounds before calling transparency finished. Aggressive deletion based only on color distance can remove legitimate warm highlights or thin anatomy.

## Failures and repairs from this run

### Clipped tails in ordinary states

Early idle, review, and active-work attempts included clipped tails. A cropped source cannot be repaired just by centering its remaining pixels. The affected source rows were revised so the full bird fit before accepted extraction. This is why a no-edge-pixels test on the final cell should be combined with review of the original silhouette: padding around a previously amputated tail can pass a cell-edge test.

### Handlike waiting gestures

An early waiting attempt produced a handlike gesture. It was rejected because the anatomy broke the raven identity. The repair used natural folded wings and attentive head movement. For animal characters, describe the action through species-appropriate body mechanics rather than relying on an abstract emotion word alone.

### Body shrinkage during a spread-wing hop

A spread-wing jumping attempt made the body appear smaller relative to other states. Large wings consumed the frame envelope, and whole-pose fitting reduced the torso. The accepted direction became a folded-wing hop, preserving a compact silhouette and more consistent body proportions. This was an animation-design repair as well as a fitting repair.

### Mirroring before proper extraction

A careless fixed-slot mirroring approach cut poses because the source birds were not perfectly aligned to those assumed slots. The corrected sequence extracted the complete poses, registered them, and then mirrored individual frames. Mirroring a registered frame preserves its entire silhouette and provides a reliable opposite-direction counterpart.

Mirroring is appropriate only when asymmetric details are allowed to swap sides. This raven has no text, badge, or side-specific accessory. A ChirpNeighbors character with those details may need separately generated or manually corrected opposite-facing frames.

### Cardinal extraction with equal source slots

The cardinal source also exposed the equal-slot assumption: source layout did not align safely with naïve cuts. The repair used connected pose extraction with explicit magenta handling, followed by registration into four stable cells. Equal-cell slicing became valid after registration, not before it.

### Body reversal in the second gaze row

The first attempt at the second gaze row flipped the body and tail, undermining the fixed-body gaze design. It was regenerated with a more explicit body-lock constraint and tail-down-left orientation. This preserved the canonical body while allowing the head and neck to supply the directional variation. The general lesson is to specify stable anatomy separately from moving anatomy; a directional prompt can otherwise be interpreted as turning the whole character.

## Packaging contract and portability

The ChatGPT-specific target in this run is an eight-column, eleven-row atlas with 192 × 208 pixel cells. The validated final texture dimensions are 1536 × 2288 pixels. Nine rows contain ordinary animation, and two rows contain the sixteen gaze poses. Of the 88 available cells, 73 contain frames; 15 are unused because some ordinary sequences are shorter than eight frames.

These dimensions are a target-format requirement, not an inherent property of generated bird animation. ChirpNeighbors can use separate frame PNGs, a differently packed atlas, larger source frames, or engine-specific sprite resources. Preserve semantic frame data outside the texture so repacking does not change behavior.

A useful manifest would record character revision, source-image hash, atlas dimensions, cell dimensions, state-to-frame mapping, frame durations, looping behavior, pivot, collision bounds if needed, and directional angle convention. The per-state preview durations are recorded below. These are preview timings, not proof of how the Dot avatar runtime schedules state changes.

For a regular grid, the source rectangle is straightforward: x equals column multiplied by cell width; y equals row multiplied by cell height. Use each state's actual frame count so empty trailing cells are never played as animation frames.

## Recommended ChirpNeighbors implementation

Build a small, versioned asset pipeline with explicit checkpoints:

1. Approve a character reference and freeze that revision before broad animation work.
2. Generate one behavior at a time against the same identity, recording accepted and rejected candidates.
3. Extract complete poses into transparent images, keeping segmentation evidence available for debugging.
4. Register sequences using stable anatomical scale and a defined pivot, then apply any safe mirroring.
5. Validate frame count, alpha occupancy, bounds, ordering, and intended direction.
6. Preview loops and transitions at actual game size on several backgrounds.
7. Pack an atlas and write a manifest from the same accepted frame list.
8. Load that package in ChirpNeighbors and test its runtime selection logic before release.

Recommended runtime behavior includes an idle fallback, explicit one-shot versus looping states, and clear priority when a greeting, work reaction, or movement animation competes for control. Keep a gaze direction stable near angle boundaries with a small hysteresis region. For transitions back to idle, compare head and torso placement to avoid a visible pop. These are proposed implementation choices; no ChirpNeighbors integration has been demonstrated in this run.

A minimal independent frame check can be written with Pillow:

```python
from pathlib import Path
from PIL import Image

for path in sorted(Path("accepted_frames").glob("*/*.png")):
    frame = Image.open(path).convert("RGBA")
    assert frame.size == (192, 208), (path, frame.size)
    alpha = frame.getchannel("A")
    box = alpha.getbbox()
    assert box is not None, f"Empty frame: {path}"
    left, top, right, bottom = box
    assert left > 0 and top > 0, f"Top or left edge contact: {path}"
    assert right < frame.width and bottom < frame.height, \
        f"Bottom or right edge contact: {path}"
```

Run this in your own project with Pillow installed. It checks dimensions and alpha bounds only. It does not verify anatomy, hidden source clipping, temporal stability, correct direction, or magenta contamination. Add tests for those requirements rather than treating a successful script run as full art approval.

## Final validation and creation

The completed package contains both eight-frame gaze rows and all nine ordinary rows. The final RGBA atlas matches the 1536 × 2288 target and contains all 73 populated frames. Structural validation, final quality checks, and the Pets service validator passed. After showing the motion preview, creation succeeded and the owned custom pet was verified in the pet list. The parent selected it as dot’s avatar.

Measured motion and registration results include:

- Jump peak lift: 28 pixels.
- Landing displacement relative to the baseline: 0 pixels.
- Maximum horizontal center drift in the gaze set: 1.5 pixels.
- Gaze silhouette width ratio: 1.109, representing the recorded relative width variation across that set.
- Cardinal directions: all passed blind-majority review.
- Intermediate direction 292.5 degrees: vertical cue ambiguous in blind review; shallow upward beak and chin accepted in labeled review, with warning retained.

An automated holes diagnostic also flagged transparent gaps around the feet. Visual verification identified these as natural spaces between legs and toes below the torso, rather than missing body pixels. This illustrates why image diagnostics need anatomical interpretation: filling every detected gap would damage a valid bird silhouette.

The completed motion preview is recorded in Library as GIF `<PRIVATE_LIBRARY_FILE_ID>` and MP4 `<PRIVATE_LIBRARY_FILE_ID>`. These are asset identifiers rather than public links. They show the completed animation set for user review.

For reuse in ChirpNeighbors, the remaining acceptance work is integration-specific: render at actual game size, compare transparent edges against the game's backgrounds, verify animation timing and transitions, and test gaze selection near angle boundaries. No ChirpNeighbors integration has been demonstrated by this asset-generation run. Pet creation and dot-avatar selection were confirmed separately from validation.

The strongest reusable outcome is the disciplined separation of generated art from validated runtime assets. The raven's repairs show why that separation matters: identity grounding produces a recognizable character, while extraction, registration, and animation review make that character usable.


## Prompt record and observable generation parameters

The canonical visual request used this actual character specification: “Beautiful detailed pixel-art raven. Warm charcoal feather layers with cream highlights and subtle copper glints, bright dark expressive eyes, stout black beak, playful curious personality. No accessories, badges, text, props, sci-fi blue or purple. Clean silhouette. Three-quarter frontal resting stance, both feet visible.”

The generation call also asked for one centered, complete, compact sprite on flat pure magenta #FF00FF, readable at 192 × 208, without scenery, text, borders, shadows, glows, or detached effects. `transparent_background` was false for the source generation calls; transparency was introduced during extraction. The canonical image was a prompt-only generation. Subsequent calls passed local reference images through `referenced_image_paths`: at minimum the canonical raven and a state layout reference; gaze calls also used established pose/context references. No explicit resolution, seed, sampling setting, or underlying model name was available in the interface used.

State prompts changed the action and frame count while retaining this character definition. A representative repair instruction actually used for review was: “render each bird 20% smaller within slot. Add substantial magenta clearance to LEFT of first tail; all six complete tails must be fully visible, NONE touching slot or canvas edges.” A second gaze-row repair explicitly said: “tail points down-left and visible folded wing is on screen-left side in ALL EIGHT frames” and “ONLY HEAD/NECK TURN over shoulder while torso stays unchanged.” These task-specific directives describe the artwork; they do not require the same generation service to be useful in another project.

Exact pixel reproduction is not guaranteed. The canonical source, accepted strips, extracted frames, atlas, and preview files are retained in the asset archive so reuse does not depend on regenerating matching images.

## Preview timing and activity binding

Per-state GIF durations, in milliseconds:

- idle: 280, 110, 110, 140, 140, 320
- running-right and running-left: 120 for the first seven frames, then 220
- waving: 140, 140, 140, 280
- jumping: 140, 140, 140, 140, 280
- failed: 140 for the first seven frames, then 240
- waiting: 150 for the first five frames, then 260
- running (active work): 120 for the first five frames, then 220
- review: 150 for the first five frames, then 280

The labeled all-state demonstration uses a slower presentation rhythm: 180 ms per frame and 350 ms for the final frame of each sequence. Its MP4 is encoded from that GIF. The gaze demonstration uses 180 ms per pose; the dedicated idle–hop–idle preview uses 170 ms per frame. These are demonstrations, not a verified specification of avatar-runtime event handling.

Our six-frame active-work animation is a thinking bird: wing near beak, squint, head tilt, and nod, with feet planted. It does not contain a computer, keyboard, or literal typing gesture. No verified event-binding documentation was available for which Dot tool or computer-use events automatically play this row. The asset supports the state; automatic activation must be checked in the live product. Arbitrary extra rows are not supported by this pet atlas contract. ChirpNeighbors can independently define additional actions and longer sequences in its own renderer.
