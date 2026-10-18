import { z } from 'zod';
import { catalogEntry } from '../domain/yard.ts';
import { idSchema } from '../domain/primitives.ts';

const weightSchema = z.number().int().min(0).max(10);
const unitSchema = z.number().finite().min(0).max(1);

/** Application tuning only: never a biological claim or an inference from owner observations. */
export const speciesBehaviorTraitsSchema = z
  .object({
    schemaVersion: z.literal(1),
    speciesId: idSchema,
    provenance: z
      .object({
        kind: z.literal('product-authored-illustrative'),
        version: z.literal(1),
        biologicalValidation: z.literal('unvalidated'),
        observationDerived: z.literal(false),
      })
      .strict(),
    sizeScale: z.number().finite().min(0.75).max(1.25),
    locomotion: z
      .object({ speed: z.number().finite().min(24).max(224), hopBias: unitSchema })
      .strict(),
    affinities: z
      .object({ ground: weightSchema, perch: weightSchema, roost: weightSchema })
      .strict(),
    /** Zero disables the decorative activity; positive values are relative priorities. */
    activities: z
      .object({
        feed: weightSchema,
        bath: weightSchema,
        nest: weightSchema,
        play: weightSchema,
        sing: weightSchema,
      })
      .strict(),
    socialSpacing: z.number().finite().min(0).max(40),
    caution: unitSchema,
  })
  .strict()
  .superRefine((value, context) => {
    if (!catalogEntry(value.speciesId))
      context.addIssue({
        code: 'custom',
        message: 'Illustrative traits require a catalog species.',
      });
    if (Object.values(value.affinities).every((weight) => weight === 0))
      context.addIssue({ code: 'custom', message: 'At least one location affinity is required.' });
  });
export type SpeciesBehaviorTraits = z.infer<typeof speciesBehaviorTraitsSchema>;

export { fictionalPersonalitySchema, type FictionalPersonality } from '../domain/bird-behavior.ts';

/** Transient developer comparison only; never a persisted individual or species assertion. */
export const behaviorExperimentSchema = z
  .object({
    schemaVersion: z.literal(1),
    preset: z.enum([
      'ground-only',
      'perch-only',
      'no-bathing',
      'no-routines',
      'cautious',
      'sociable',
    ]),
  })
  .strict();
export type BehaviorExperiment = z.infer<typeof behaviorExperimentSchema>;

const behaviorSchema = z.enum([
  'idle',
  'moving',
  'perching',
  'singing',
  'feeding',
  'bathing',
  'sleeping',
  'playing',
  'nesting',
]);
const affordanceSchema = z.enum(['ground', 'perch', 'feed', 'bath', 'roost', 'nest']);
/** Rule identifiers are safe diagnostics, not free-form owner notes or source evidence. */
const ruleCodeSchema = z
  .string()
  .min(1)
  .max(80)
  .regex(/^[a-z][a-z0-9-]*$/);
const reasonsSchema = z.array(ruleCodeSchema).min(1).max(12);
const prioritySchema = z.number().finite().min(0).max(1000);
const slotCountSchema = z.number().int().min(0).max(512);
// Object IDs can be 160 characters; the derived suffix ':center' adds seven.
const decisionSlotIdSchema = z
  .string()
  .min(1)
  .max(167)
  .regex(/^[a-zA-Z0-9][a-zA-Z0-9._:-]*$/)
  .refine((value) => !['__proto__', 'prototype', 'constructor'].includes(value));

/** Bounded transient explanation of the existing simulator; it grants no input authority. */
export const behaviorDecisionTraceSchema = z
  .object({
    schemaVersion: z.literal(1),
    provenance: z.literal('decorative-simulation'),
    tick: z.number().int().min(0).max(Number.MAX_SAFE_INTEGER),
    phase: z.enum(['dawn', 'day', 'dusk', 'night']),
    trigger: z.enum([
      'initial-placement',
      'activity',
      'night',
      'wake',
      'scene-edit',
      'arrival',
      'decorative-visit',
      'cancelled',
    ]),
    selected: z
      .object({
        behavior: behaviorSchema,
        slotId: decisionSlotIdSchema.nullable(),
        affordance: affordanceSchema.nullable(),
        capability: z.enum(['play', 'nest-building']).nullable(),
        priority: prioritySchema,
        reasons: reasonsSchema,
      })
      .strict(),
    candidates: z
      .array(
        z
          .object({
            behavior: behaviorSchema,
            eligible: z.boolean(),
            priority: prioritySchema,
            reasons: reasonsSchema,
            availableSlots: slotCountSchema,
            rejected: z
              .object({
                occupiedOrClearance: slotCountSchema,
                unsupported: slotCountSchema,
                unreachable: slotCountSchema,
              })
              .strict(),
          })
          .strict(),
      )
      .max(9),
    locomotion: z.object({ mode: z.enum(['flight', 'hop']), reason: ruleCodeSchema }).strict(),
    transition: z
      .object({ from: behaviorSchema, to: behaviorSchema, reason: ruleCodeSchema })
      .strict(),
  })
  .strict()
  .superRefine((value, context) => {
    if (
      new Set(value.candidates.map((candidate) => candidate.behavior)).size !==
      value.candidates.length
    )
      context.addIssue({ code: 'custom', message: 'Candidate behaviors must be unique.' });
    if (value.candidates.length) {
      const selected = value.candidates.find(
        (candidate) => candidate.behavior === value.selected.behavior,
      );
      if (!selected?.eligible || selected.priority !== value.selected.priority)
        context.addIssue({
          code: 'custom',
          message: 'Selection must match an eligible candidate priority.',
        });
    }
  });
export type BehaviorDecisionTrace = z.infer<typeof behaviorDecisionTraceSchema>;
