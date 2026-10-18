# Private common-family intake

A blink or look is named idle presentation, not another behavioral activity. The existing nine action names and older schemas remain unchanged. A V6 private development candidate has one neutral idle pose plus a `commonMotion` V1 record containing explicit blink/look clips and their ordered idle sequence. The production Pixi/SVG paths use the same deterministic `sampleClip` function. Missing bath/perch/flight/sleeping actions continue to resolve to the neutral fallback. Reduced motion holds neutral; a non-looping look ends on its supplied neutral frame.

| Boundary | Version / canonical file |
| --- | --- |
| Named presentation and graph | `contracts/common-motion-v1.schema.json` |
| Full decoded source input | `contracts/asset-packaging-input-v4.schema.json` |
| Immutable retained source | `contracts/rgba-source-artifact-v3.schema.json` |
| Render manifest | `contracts/species-manifest-v6.schema.json` |
| PNG atlas package command / workshop plan | `contracts/png-file-package-command-v3.schema.json`, `contracts/png-workshop-plan-v3.schema.json` |
| Job command | `contracts/job-command-v4.schema.json` |

All seven schemas are generated from the companion UI's Zod authorities and mirrored in ChirpNeighbors. Tiny `contracts/fixtures/common-family-*.json` files contain synthetic pixels and fabricated test pins only. They never authorize real source references. Existing contract digests, including job-command V3, remain unchanged. Old strict readers reject these new versions; upgrade the receiving UI/contracts together. Portable structural schemas cannot enforce every graph, frame, reference and provenance relationship; production authorities must still validate them.

## Producer field checklist

| Field group | Required evidence |
| --- | --- |
| `source` | Versioned species identity, creator/source version, honest representation, `reviewScope: development-candidate`, development-only derivative rights/evidence, technical reference descriptors and `fidelityReview: null`. Keep source IDs and private rights evidence private. |
| `pixels` | Exact decoded RGBA frames, canvas, logical grid and palette bounds. Record original PNG and decoded frame hashes separately; do not invent either. Preserve whole-frame registration. |
| `strategy`, `presentation` | Explicit decoded-RGBA alpha origin and source pixels per world unit. PNG command V3 requires explicit `alphaOrigin`; it does not silently call cleaned pixels native. |
| `clips.idle` | One supplied neutral frame, explicit ticks and loop flag, proposed image pivot, zero rotation and empty contacts. |
| `conditioning` | Taxonomy, exact already-reviewed owner-local technical reference pins, neutral pose graph. References do not grant species/anatomy approval. |
| `commonMotion` | Version1, `geometryScope: image-registration-only`, `physicalSupportReviewed: false`, explicit idle sequence, named blink/look frames/ticks/loop flags, matching reference-bound graph with exact edges. Each clip starts and ends on the same neutral frame; every pose retains its proposed pivot and has empty contacts. |
| Actual admission | Immutable file/rights review, source review, manifest review, explicit opted-in private pin. These are separate repository decisions; uploaded JSON cannot assert them. |

From the UI repository, run:

```sh
node scripts/check-common-intake.ts /path/to/private-input.json
```

The reusable report binds input bytes, exported structural schema and named source-authority file hashes, names invalid/missing paths and exits1 on incomplete metadata. Passing this metadata preflight still reports `sourceAdmitted: false`; it cannot prove actual bytes, rights, owner pins or review decisions. A PNG atlas uses command V3 and real file validation; a decoded bundle uses input V4. Neither path bypasses source and manifest review.

## Completed source slice and acceptance limits

The supplied four-frame House Finch family was packaged without drawing, resampling, per-pose fitting or changed source timings. Actual PNG SHA and decoded-frame identities match; all four normalized render frames reconstruct the retained RGBA exactly. Neutral42 ticks; blink42/2/3/2/20 loop; look30/12/30 non-loop. Proposed pivot48,75 and empty contacts are preserved. Existing authored illustrative Finch width30 is constant across poses; it is not an anatomical or physical scale measurement.

An isolated copy of the saved showcase passes the actual immutable file→source→manifest review and explicit private opt-in pin path, exact retry, owner/opt-out/corruption checks, reopening and retained-source repack. The other20 bird pins stay unchanged. Source bytes, private pins and copied saved data are not included in either code repository. No live saved-yard pin was changed. The normal renderer display-object test assigns synthetic named frames through the real Pixi code; it does not establish GPU or browser appearance.

Phoebe and Goldfinch still need their complete canonical envelope and immutable authority bindings assembled; partial source handoffs are not runtime packages. Junco also retains its transparent far-foot/support exclusion. Crow and bath candidates remain separate held physical/geometry work. An ambiguous-eye Bushtit blink stays held regardless of a structural pass. No new generation or artwork acceptance follows from this integration.

Actual source PNG inspection is complete for Finch. Anatomy, grounded/perch support, contacts, bilateral appearance and live desktop/mobile blink/look clarity remain unreviewed. Browser verification is explicitly stopped. Before any live pin adoption, resume visual QA in an authorized isolated profile and review appearance, facing, stable registration/scale, timing/terminal holds, reduced motion, selection changes and held-action fallback. No support/fidelity/production approval is claimed by this source-only slice. Canonical task611 remains partial; downstream622 is not closed.
