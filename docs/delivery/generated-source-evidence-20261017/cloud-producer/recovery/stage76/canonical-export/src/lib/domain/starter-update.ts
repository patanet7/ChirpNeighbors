import { z } from 'zod';
import {
  candidateChannelSchema,
  candidateCompatibilitySchema,
} from '../assets/candidate-registry.ts';
import type { Artwork } from './yard';
import { idSchema, timestampSchema } from './primitives.ts';

export const STARTER_UPDATE_LIMITS = Object.freeze({ birds: 32, receipts: 128 });
const revision = z.number().int().min(0).max(Number.MAX_SAFE_INTEGER);
export const starterArtBindingSchema = z
  .object({
    schemaVersion: z.literal(1),
    revision,
    mode: z.enum(['fixed', 'follow-compatible']),
    channel: candidateChannelSchema.refine(
      (value) => value.kind === 'bird',
      'Starter binding requires a bird channel.',
    ),
    compatibility: candidateCompatibilitySchema,
    previousArtworkId: idSchema.nullable(),
  })
  .strict();
export type StarterArtBinding = z.infer<typeof starterArtBindingSchema>;
const expected = z
  .object({
    requestId: z.string().uuid(),
    birdId: idSchema,
    expectedArtworkId: idSchema.nullable(),
    expectedRevision: revision,
  })
  .strict();
export const starterUpdateCommandSchema = z.discriminatedUnion('action', [
  expected
    .extend({
      action: z.literal('starter-art-policy'),
      mode: z.enum(['fixed', 'follow-compatible']),
    })
    .strict(),
  expected.extend({ action: z.literal('revert-starter-art') }).strict(),
  z.object({ action: z.literal('refresh-starter-art'), requestId: z.string().uuid() }).strict(),
]);
export type StarterUpdateCommand = z.infer<typeof starterUpdateCommandSchema>;
export const starterUpdateReceiptSchema = z
  .object({
    requestId: z.string().uuid(),
    commandDigest: z.string().regex(/^[a-f0-9]{64}$/),
    action: z.enum(['starter-art-policy', 'revert-starter-art', 'refresh-starter-art']),
    changedBirdIds: z.array(idSchema).max(STARTER_UPDATE_LIMITS.birds),
    createdAt: timestampSchema,
  })
  .strict()
  .superRefine((value, ctx) => {
    if (new Set(value.changedBirdIds).size !== value.changedBirdIds.length)
      ctx.addIssue({ code: 'custom', message: 'Duplicate changed bird identity.' });
  });
export type StarterUpdateReceipt = z.infer<typeof starterUpdateReceiptSchema>;
export const starterUpdateReceiptsSchema = z
  .array(starterUpdateReceiptSchema)
  .max(STARTER_UPDATE_LIMITS.receipts)
  .superRefine((rows, ctx) => {
    if (new Set(rows.map((row) => row.requestId)).size !== rows.length)
      ctx.addIssue({ code: 'custom', message: 'Duplicate starter update request identity.' });
  });
export interface StarterUpdateBird {
  id: string;
  speciesId: string;
  artworkId: string | null;
  lifecycle?: 'temporary' | 'permanent' | 'expired';
  starterArt?: StarterArtBinding | undefined;
}
export interface StarterUpdateSnapshot {
  birds: readonly StarterUpdateBird[];
  artworks: readonly Artwork[];
  preferences: { developmentCandidateArt?: boolean | undefined };
}
export type StagedStarterChange = {
  birdId: string;
  speciesId: string;
  expectedArtworkId: string | null;
  expectedBindingRevision: number;
  expectedMode: 'fixed' | 'follow-compatible';
  target:
    | { kind: 'keep' }
    | { kind: 'reviewed-animation'; artwork: Omit<Artwork, 'id' | 'version'> }
    | { kind: 'retained-artwork'; artworkId: string };
  binding: StarterArtBinding;
};
export type StagedStarterBatch = {
  schemaVersion: 1;
  command: StarterUpdateCommand;
  requestId: string;
  commandDigest: string;
  expectedFollowSetSha256: string | null;
  changes: StagedStarterChange[];
};
/** Stable CAS over only followed residents; legacy/default fixed state never writes on read. */
export function starterFollowSetValue(snapshot: Pick<StarterUpdateSnapshot, 'birds'>) {
  return snapshot.birds
    .filter((bird) => bird.lifecycle !== 'expired' && bird.starterArt?.mode === 'follow-compatible')
    .sort((a, b) => a.id.localeCompare(b.id))
    .map((bird) => [bird.id, bird.speciesId, bird.artworkId, bird.starterArt?.revision ?? 0]);
}
