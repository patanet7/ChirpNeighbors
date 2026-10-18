import { z } from 'zod';
import { idSchema, timestampSchema } from './primitives.ts';

export const evidenceValueSchema = z
  .object({
    speciesId: idSchema,
    observedAt: timestampSchema.nullable(),
  })
  .strict();
export const evidenceRevisionSchema = evidenceValueSchema
  .extend({
    correctionId: z.string().uuid().nullable(),
  })
  .strict();
export const manualFindingSchema = z
  .object({
    schemaVersion: z.literal(1),
    id: z.string().uuid(),
    speciesId: idSchema,
    observedAt: timestampSchema.nullable(),
    note: z.string().max(1000),
  })
  .strict();
export const correctionInputSchema = z
  .object({
    schemaVersion: z.literal(1),
    id: z.string().uuid(),
    eventId: idSchema,
    expected: evidenceRevisionSchema,
    replacement: evidenceValueSchema,
    reason: z.string().min(1).max(500).regex(/\S/, 'Explain the correction.'),
  })
  .strict();
export const correctionRecordSchema = correctionInputSchema
  .extend({
    recordedAt: timestampSchema,
  })
  .strict();
export const findingCommandSchema = z.discriminatedUnion('action', [
  z.object({ action: z.literal('manual-finding'), finding: manualFindingSchema }).strict(),
  z
    .object({
      action: z.literal('correct-events'),
      corrections: z.array(correctionInputSchema).min(1).max(100),
    })
    .strict(),
]);
export type EvidenceValue = z.infer<typeof evidenceValueSchema>;
export type EvidenceRevision = z.infer<typeof evidenceRevisionSchema>;
export type ManualFinding = z.infer<typeof manualFindingSchema>;
export type CorrectionInput = z.infer<typeof correctionInputSchema>;
export type EvidenceCorrection = z.infer<typeof correctionRecordSchema>;
export type FindingCommand = z.infer<typeof findingCommandSchema>;
export const effectiveEvidenceSchema = evidenceRevisionSchema
  .extend({ eventId: idSchema })
  .strict();
export type EffectiveEvidence = z.infer<typeof effectiveEvidenceSchema>;
export const sameValue = (a: EvidenceValue, b: EvidenceValue) =>
  a.speciesId === b.speciesId &&
  (a.observedAt === b.observedAt ||
    (a.observedAt !== null &&
      b.observedAt !== null &&
      Date.parse(a.observedAt) === Date.parse(b.observedAt)));
export const sameRevision = (a: EvidenceRevision, b: EvidenceRevision) =>
  a.correctionId === b.correctionId && sameValue(a, b);
