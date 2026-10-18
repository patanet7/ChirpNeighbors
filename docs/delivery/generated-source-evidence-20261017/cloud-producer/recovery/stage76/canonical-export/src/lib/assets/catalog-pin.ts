import { z } from 'zod';

/** Generic species release identity only; never a private pipeline or individual bird pin. */
export const catalogPinSchema = z
  .object({
    catalogKey: z.string().regex(/^[a-f0-9]{64}$/),
    releaseVersion: z.number().int().min(1).max(Number.MAX_SAFE_INTEGER),
    renderSha256: z.string().regex(/^[a-f0-9]{64}$/),
  })
  .strict();
export type CatalogPin = z.infer<typeof catalogPinSchema>;
