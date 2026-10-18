import { z } from 'zod';
import { idSchema } from './primitives.ts';

const unitSchema = z.number().finite().min(0).max(1);
/** Fictional display traits, not recognition or inference from sightings/names. */
export const fictionalPersonalitySchema = z
  .object({
    schemaVersion: z.literal(1),
    provenance: z
      .object({
        kind: z.literal('fictional-individual'),
        version: z.literal(1),
        observationDerived: z.literal(false),
        seedBasis: z.literal('decorative-resident-id'),
      })
      .strict(),
    seed: z.number().int().min(0).max(0xffffffff),
    curiosity: unitSchema,
    sociability: unitSchema,
    boldness: unitSchema,
  })
  .strict();
export type FictionalPersonality = z.infer<typeof fictionalPersonalitySchema>;
export const personalityAxesSchema = fictionalPersonalitySchema.pick({
  curiosity: true,
  sociability: true,
  boldness: true,
});
export type PersonalityAxes = z.infer<typeof personalityAxesSchema>;
export const savedBirdBehaviorSchema = z
  .object({
    schemaVersion: z.literal(1),
    revision: z
      .number()
      .int()
      .min(1)
      .max(Number.MAX_SAFE_INTEGER - 1),
    source: z.enum(['owner-authored', 'decorative-default']),
    traits: fictionalPersonalitySchema,
  })
  .strict();
export type SavedBirdBehavior = z.infer<typeof savedBirdBehaviorSchema>;
export const personalityCommandSchema = z
  .object({
    action: z.literal('personality'),
    birdId: idSchema,
    expectedRevision: z
      .number()
      .int()
      .min(0)
      .max(Number.MAX_SAFE_INTEGER - 2),
    /** Null resets axes; a new revision is retained so stale commands cannot pass after reset. */
    traits: personalityAxesSchema.nullable(),
  })
  .strict();
export type PersonalityCommand = z.infer<typeof personalityCommandSchema>;
function decorativeHash(value: string) {
  let seed = 2166136261;
  for (let i = 0; i < value.length; i++) seed = Math.imul(seed ^ value.charCodeAt(i), 16777619);
  return seed >>> 0;
}
/** Exact legacy default algorithm. One authority shared by storage, client and simulation. */
export function defaultFictionalPersonality(decorativeId: string): FictionalPersonality {
  const seed = decorativeHash(`fictional-personality-v1:${decorativeId}`);
  const trait = (name: string) => decorativeHash(`${seed}:${name}`) / 0xffffffff;
  return fictionalPersonalitySchema.parse({
    schemaVersion: 1,
    provenance: {
      kind: 'fictional-individual',
      version: 1,
      seedBasis: 'decorative-resident-id',
      observationDerived: false,
    },
    seed,
    curiosity: trait('curiosity'),
    sociability: trait('sociability'),
    boldness: trait('boldness'),
  });
}
export function effectiveBirdBehavior(id: string, saved?: SavedBirdBehavior) {
  if (saved) {
    const checked = savedBirdBehaviorSchema.parse(saved);
    return { revision: checked.revision, traits: checked.traits };
  }
  return { revision: 0, traits: defaultFictionalPersonality(id) };
}
