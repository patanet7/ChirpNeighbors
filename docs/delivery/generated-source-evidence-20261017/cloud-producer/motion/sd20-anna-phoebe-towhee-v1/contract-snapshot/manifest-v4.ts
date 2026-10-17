import { z } from 'zod';
import { speciesManifestV3Schema } from './manifest-v3.ts';

/** Explicit source resolution; coordinates and retained pixels remain in source units. */
export const assetPresentationSchema = z
  .object({
    schemaVersion: z.literal(1),
    sourcePixelsPerWorldUnit: z.union([z.literal(1), z.literal(2), z.literal(4)]),
  })
  .strict();
export const speciesManifestV4Schema = speciesManifestV3Schema
  .innerType()
  .extend({
    schemaVersion: z.literal(4),
    presentation: assetPresentationSchema,
  })
  .strict()
  .superRefine((value, context) => {
    const legacy = { ...value };
    Reflect.deleteProperty(legacy, 'presentation');
    const result = speciesManifestV3Schema.safeParse({ ...legacy, schemaVersion: 3 });
    if (!result.success) for (const issue of result.error.issues) context.addIssue(issue);
  });
export type SpeciesManifestV4 = z.infer<typeof speciesManifestV4Schema>;
