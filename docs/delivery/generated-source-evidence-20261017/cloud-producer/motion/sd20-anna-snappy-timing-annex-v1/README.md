# Anna fast-dart timing annex: zero new art

This isolated source-only runtime proposal reuses B’s unchanged eight actual source/render identities, copied atlas and per-frame pivots. It does not mutate `sd20-anna-dart-brake-v1`, generate an image, repaint/warp a sprite, fit alpha bounds, or turn root movement into drawing coverage. Existing B smooth-flight, sparse-wing and category-transition limitations remain.

## Timing comparison

The default authored one-shot is45ticks/1.5seconds at30Hz: initialhover12ticks; accelerate6ticks0→18world units usingu²; brake6ticks18→36using2u−u²; finalhover21ticks. Actual travel lasts12ticks/0.4seconds. Peak180world units/second is authored game timing, not a biological measurement. Root remains36,0 after completion with no automatic replay. The original B mode preserves its exact copied90tick path and1.2second travel for comparison.

The pose tick is global `floor(elapsedMs*30/1000)`, used modulo the selected original B clip duration. It never resets at a root segment or terminal hold; only manual replay/mode change resets the preview epoch. Final root is stationary indefinitely while the existing four hover wing frames continue. Zero support contacts and no feeding/perch claims.

## Actual pixel scale and bindings

`review.html` uses relative exact-source art. The main144×96CSS world scene renders each96px source tile as the declared64×64world/CSS canvas at density1.5. The large view is4×inspection. Draw placement subtracts the actual selected B frame pivot; no pivot/bounding-box normalization is applied. Forward/brake pivots48,60 and hover pivots54,68 remain unchanged.

`source-bindings.json` pins the unchanged upstream PRIMARY/profile/map/slow-path hashes, copied atlas hash/dimensions, eight primary IDs and primary PNG hashes, eight copied output PNG hashes, rectangles, pivots, world size and empty contacts. Primary PNG paths continue to point to canonical B sources; copied96PNG assets remain byte-identical. `references/` retains exact metadata snapshots.

`snappy-trajectory.json` is the new authored timing proposal. `PRIMARY-SOURCE-MANIFEST.json` declares nativeCalls0, frames[]empty and reusedFrames8. `upstream-qualification.json` preserves B’s provisional source limitations. This annex supplies no canonical runtime admission or actual Mac yard binding.

## Checks and review limits

Node checks verify source hashes, zero-art accounting,45tick schedule, monotonic root/endpoints, continuous180world-unit/s peak, zero endpoint velocity, continued terminal/global pose phase and invalid inputs. Pillow checks all eight primary decodedRGBA IDs and exact atlas tiles.

Actual Chromium checks observe stationary terminal root with four continuing wing states after the1.5second one-shot, all eight source frames in numeric canvas controls, light/dark and original-mode controls, and the actual animation callback rejecting stale generations while accepting a current generation. After pause, stale callbacks do not repaint. Only numeric/time/hash evidence is retained; no browser screenshots/capture bytes or encoded media receipts are saved.

The timing’s visual merits require a separate bounded annex review. No Library, Git, global queue or frame-bank writes occur here; no image call is started. Phoebe remains conditioning-prep only.
