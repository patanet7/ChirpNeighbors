import { z } from 'zod';
import { catalogEntry } from '../domain/yard.ts';
import { idSchema } from '../domain/primitives.ts';

/** Presentation seed only. It does not identify an owner, recording or persistent bird. */
export const sessionSeedSchema = z.number().int().min(0).max(0xffffffff);
/** Deliberately illustrative tuning, not scientific measurements or individual-bird recognition. */
export const illustrativeSpeciesProfileSchema = z
  .object({
    schemaVersion: z.literal(1),
    speciesId: idSchema,
    tuning: z.literal('illustrative'),
    sizeScale: z.number().finite().min(0.75).max(1.25),
    movement: z
      .object({
        speed: z.number().finite().min(24).max(224),
        hopBias: z.number().finite().min(0).max(1),
      })
      .strict(),
    preferences: z
      .object({
        ground: z.number().int().min(0).max(10),
        perch: z.number().int().min(0).max(10),
        feed: z.number().int().min(0).max(10),
      })
      .strict(),
    /** Additional ground spacing is an illustrative sociability setting, not physical anatomy. */
    socialSpacing: z.number().finite().min(0).max(40),
    caution: z.number().finite().min(0).max(1),
  })
  .strict()
  .superRefine((value, context) => {
    if (!catalogEntry(value.speciesId))
      context.addIssue({
        code: 'custom',
        message: 'Behavior profile species must exist in the application catalog.',
      });
    if (Object.values(value.preferences).every((weight) => weight === 0))
      context.addIssue({
        code: 'custom',
        message: 'Behavior profile requires at least one preferred activity.',
      });
  });
export type IllustrativeSpeciesProfile = z.infer<typeof illustrativeSpeciesProfileSchema>;
export const simulationOptionsSchema = z
  .object({
    sessionSeed: sessionSeedSchema.optional(),
    illustrativeProfiles: z.boolean().optional(),
  })
  .strict();
export type SimulationOptions = z.infer<typeof simulationOptionsSchema>;
