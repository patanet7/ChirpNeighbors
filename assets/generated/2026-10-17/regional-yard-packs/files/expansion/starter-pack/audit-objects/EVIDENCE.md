# Baked scenery and editable object audit

The latest coastal yard has a usable local-foreground-free foundation now. Draw the unchanged distance source at (0,0), draw it again at (0,-140), then draw ground-boundary at (0,0). Omit both rigid_edges and flexible_foliage. The saved native preview is `coastal-foundation-no-local-foreground.png`; source hashes and exact passes are in `drawpass-contracts.json`.

| Scene variant | Fixed content | Optional compound content | Plant/prop-free local stage now? |
| --- | --- | --- | --- |
| Initial coastal urban | Left tree, border planting, stones, wall and ground in opaque base | Generated corner accents and extracted corner crops | No; regenerate base to remove baked local vegetation |
| Initial inland canyon | Both side trees, shrubs/flowers/rocks, fence and ground in opaque base | Generated corner accents and extracted corner crops | No; regenerate base to remove baked local vegetation |
| Initial managed patio | Pergola, vines, containers/potted plants, walls and pavers in opaque base | Generated corner accents and extracted corner crops | No; regenerate base to remove baked local props/vegetation |
| Compact marine courtyard proof01 | Shrubs/flowers/planted border fused into wall+ground file | Branch, pot+shrub and stones+foliage fused in foreground file | Foreground-free preview exists, but planted border remains baked; regenerate ground for an empty border |
| Coastal wave04 | Wall/gate, bare soil/stone bed, turf texture; distant vegetation fused into distance | Pot+trunk in rigid file; foliage and rear planting in flexible file | Yes for local foreground; omit both optional files. Turf/distant canopy stay baked |

The original scenes contain no independent canonical plant/object instances. Compound render-layer paths and spatial foliage crops do not acquire canonical species or object IDs from visual resemblance. The coastal six foliage-group crops are provisional spatial groups, not anatomical rigs or implemented wind motion. The existing `pre-foliage-registered.png` still contains the rigid pot and trunk.

`object-placement-catalog.json` copies nine independent object variants from the authoritative source manifests, including sprite files/hashes, roots, contact polygons, proposed sizes, perch/drink/feed/water points and missing states. The common starter recommendation is `object.cedar_feeder` default plus `object.ground_birdbath` / `rectangular_concrete`. The fountain is an optional static art candidate: its emitter/return points do not implement flow. All functional points remain provisional sprite-pixel metadata.

The 960x540 coastal preview uses a proposed centered 16:9 viewport: crop [0,80,1536,944], uniformly resize by0.625. `viewport-contract.json` records this derivative. This is an explicit review choice, not accepted runtime camera mapping. Full native source pixels remain unchanged.

Verification: reconstruction of both existing full composites from their full listed source passes is RGBA-pixel-identical. Both omitted-foreground previews are fully opaque. `baked-versus-optional-contact.png` was visually inspected and supports the contents above. Current output changes only this audit directory; no app/Git/root inventory changes.

The inspected cloud app is stale and only has saved object kinds perch/feeder/bath/nest with id/kind/x/y. It does not establish direct import of these art manifests, arbitrary plant placement, asset skin selection or alignment of generic runtime perch slots to sprite anchors. Native art is3:2; world dimensions are960x540. Camera, canonical asset mapping, physical scale, bird contact/depth and current Mac intake receipt remain pending. No saved layout or runtime integration was created here.
