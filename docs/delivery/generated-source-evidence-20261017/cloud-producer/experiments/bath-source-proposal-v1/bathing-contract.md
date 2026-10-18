# BATH-SOURCE-PROPOSAL-1 — producer-safe bathing reference

Source-only extraction from `patanet7/birdsong-yard-sprites` commit `806ef7e7522a5a4ea3d8a9cd38bac6968fcbbfe9`. The JSON binds each referenced source file with SHA-256/Git blob and line ranges. This is authored engine registration, **not physical contact, generated-art or rights approval**. No saved-yard data, private path, owner identifier, asset pin or image is included.

## Spaces and anchors

World is 960×540, top-left origin, +x right/+y down. Object anchor **A=(X,Y)** is ground/depth, not image top-left. The canonical pedestal is nearest-resized **612×487 → 122×97**, then rendered at one resized pixel/world unit with pivot **(58,90)**. Canvas point `(u,v)` maps to `(X+u−58,Y+v−90)`. The pivot belongs to the resized canvas, not the original image. The original source digest is catalog-declared; this extraction does not read or independently reverify image bytes. Ground footprint is **100×54**, centered on A; canonical definition height is90, legacy bath definition height80.

| Support | Object-local | Resized canvas | Public default example A=(700,445) |
|---|---|---|---|
| Left | (−18,−68) | (40,22) | (682,377) |
| Right | (18,−68) | (76,22) | (718,377) |

Both slots have ground depth Y and independently exclusive occupancy. These points are actor-root/support registrations, **not measured toe, belly or water-intersection coordinates**. Bird poses keep their own source pivot/scale; a reviewed pose support anchor, otherwise the pose pivot, maps to the actual actor root after mirroring/rotation. That root is admitted within1world unit of the slot; no exact root snapping is implied. The exact transform is in the JSON; no bird-specific pivot is invented.

## Interactive bowl and waterline

Normal physical mode hides the generated canonical bath image. It uses the authored bowl: rim strip `(-48,-68,96,12)`, lower bowl `(-36,-56,72,8)`, pedestal `(-10,-57,20,55)` and base `(-28,-7,56,9)`, all object-local rectangles. The generated image's inner rim/feet/body contact mapping remains unreviewed; these rectangles do not establish an image-derived bowl mask.

For liquid volume V in m³, **depth=V/0.12**, **level=min(1,V/0.006)** and **waterlineY=slotY+3−6×level**, with slotY=Y−68. The water glyph is88units wide, centered on X; it is drawn only with positive liquid. World coordinates/dimensions are rounded on emission. This is authored display tuning, not a physical metre-to-pixel calibration.

| Liquid | Model depth | Local waterline y | World y at public default |
|---|---|---|---|
| 0L | 0mm | −65 | 380; no glyph |
| 0.06L | 0.5mm | −65.06 | 379.94 before rounding |
| 0.12L | 1mm | −65.12 | 379.88 before rounding |
| 3L default | 25mm | −68 | 377 |
| 6L capacity | 50mm | −71 | 374 |

The actor slot stays at−68 as the waterline changes. **Visible blue pixels do not authorize wet contacts.** Do not move the actor root to the fluid line or infer immersion from these scalar values.

## Contact, action and cosmetics

Enter wet admission at≥1mm (0.12L); an already-wet basin stays wet only above0.5mm (0.06L). Valid contact requires the current same-object generation/revision, actual placed actor, owned bath slot, no remaining flight target/route, finite coordinates and root within1world unit of the slot. Night/shelter/scatter/return block activity. These are live slot/root rules, not body/feet geometry verification.

Semantic bathing lasts3SI seconds; hydrology steps0.05s, actor simulation1/30s. Authored clip durations are separate. A missing bathing clip still yields an honestly labeled idle fallback while semantic contacts can complete; legacy unspecified capabilities remain explicitly unverified.

Engine ripples/splashes are separate, bounded, **zero-mass cosmetics** emitted on committed physical ticks (maximum24, lifetime1.2s). Drinking is a different confirmed-withdrawal action. Object depth isY, water/effectsY+0.1, actorY+0.25. No front-rim/body interleave or immersion mask is implemented; current actor paint sits above the bowl/water layer.

## Producer review still required

Generated bathing frames, avian anatomy, feet/support/body immersion, species scale/facing, original-image rim calibration and front/back rim occlusion remain unreviewed. No animation frames, contact declarations, license, fidelity approval or source admission are supplied or implied. This packet describes the existing baseline for a proposal; tasks313/205 remain partial.

Source entry points: `src/lib/domain/canonical-yard-data.json` / `canonical-yard.ts`; `src/lib/server/canonical-yard.ts`; `src/lib/engine/scenes.ts`; `visuals.ts`; `surface-runtime.ts`; `surface-interactions.ts`; `shared-surface-contacts.ts`; `src/lib/assets/pose-geometry.ts`. Full source hashes/lines are in `bathing-contract.json`.
