import { z } from 'zod';
import { speciesManifestV3Schema, validatePoseManifestGeometry } from './manifest-v3.ts';
import { assetPresentationSchema } from './manifest-v4.ts';

/** Opt-in private technical art. This is not accepted species art or a shared release. */
export const speciesManifestV5Schema = speciesManifestV3Schema
  .innerType()
  .extend({
    schemaVersion: z.literal(5),
    fixture: z.literal(false),
    taxonFidelityReviewed: z.literal(false),
    reviewScope: z.literal('development-candidate'),
    presentation: assetPresentationSchema,
    provenance: speciesManifestV3Schema
      .innerType()
      .shape.provenance.extend({
        source: z.enum(['provider', 'user_upload']),
        usage: z.literal('development-candidate'),
      })
      .strict(),
  })
  .strict()
  .superRefine(validatePoseManifestGeometry);
export type SpeciesManifestV5 = z.infer<typeof speciesManifestV5Schema>;
