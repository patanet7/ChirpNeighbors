import { z } from 'zod';

/** Pure metadata only: no source bytes, private pin, filesystem, fetch or approval authority.
 * Full existing pose/PNG manifest validation remains a mandatory server admission step.
 */
export const CANDIDATE_REGISTRY_LIMITS = Object.freeze({
  releases: 128,
  receipts: 512,
});
const hash = z.string().regex(/^[a-f0-9]{64}$/);
const version = z.number().int().min(1).max(Number.MAX_SAFE_INTEGER);
const revision = z.number().int().min(0).max(Number.MAX_SAFE_INTEGER);
const id = z
  .string()
  .min(1)
  .max(160)
  .regex(/^[A-Za-z0-9][A-Za-z0-9._:-]*$/)
  .refine((value) => !['__proto__', 'prototype', 'constructor'].includes(value));
const actions = z
  .array(id)
  .max(32)
  .refine((value) => new Set(value).size === value.length);
export const candidateChannelSchema = z
  .object({
    kind: z.enum(['bird', 'background', 'object-art']),
    subjectId: id,
    styleId: id,
    variantId: id,
    compatibilityMajor: version,
  })
  .strict();
export type CandidateChannel = z.infer<typeof candidateChannelSchema>;
export const candidateCompatibilitySchema = z
  .object({
    rendererContract: z.enum(['palette-pose-v1', 'rgba-pose-v1', 'scene-rgba-v1']),
    anchorConvention: id,
    scaleConvention: id,
    geometrySha256: hash.nullable(),
  })
  .strict();
export const candidateReleaseSchema = z
  .object({
    schemaVersion: z.literal(1),
    channel: candidateChannelSchema,
    releaseVersion: version,
    sourceVersion: id,
    sourceSha256: hash,
    renderSha256: hash,
    compatibility: candidateCompatibilitySchema,
    availableActions: actions,
    heldActions: actions,
    scope: z.literal('development-candidate'),
    fixture: z.literal(false),
    taxonFidelityReviewed: z.literal(false),
    approvalReceiptSha256: hash,
  })
  .strict()
  .superRefine((value, context) => {
    if (value.availableActions.some((action) => value.heldActions.includes(action)))
      context.addIssue({
        code: 'custom',
        message: 'Held actions cannot claim available animation.',
      });
    if (value.channel.kind === 'bird' && !value.availableActions.includes('idle'))
      context.addIssue({
        code: 'custom',
        message: 'Bird candidates require an explicit idle fallback.',
      });
    if (value.channel.kind === 'background' && value.availableActions.length)
      context.addIssue({
        code: 'custom',
        message: 'Background art cannot grant bird actions.',
      });
  });
export type CandidateRelease = z.infer<typeof candidateReleaseSchema>;
export const candidateReleasePinSchema = z
  .object({
    releaseVersion: version,
    renderSha256: hash,
  })
  .strict();
export type CandidateReleasePin = z.infer<typeof candidateReleasePinSchema>;
const receiptSchema = z
  .object({
    requestId: z.string().uuid(),
    action: z.enum(['promote', 'revoke', 'rollback']),
    commandIdentity: z.string().min(1).max(20_000),
    revision: version,
    pin: candidateReleasePinSchema,
  })
  .strict();
export const candidateRegistrySchema = z
  .object({
    schemaVersion: z.literal(1),
    channel: candidateChannelSchema,
    revision,
    releases: z.array(candidateReleaseSchema).max(CANDIDATE_REGISTRY_LIMITS.releases),
    head: candidateReleasePinSchema.nullable(),
    revoked: z.array(candidateReleasePinSchema).max(CANDIDATE_REGISTRY_LIMITS.releases),
    receipts: z.array(receiptSchema).max(CANDIDATE_REGISTRY_LIMITS.receipts),
  })
  .strict()
  .superRefine((state, context) => {
    const fail = (message: string) => context.addIssue({ code: 'custom', message });
    if (state.revision !== state.receipts.length)
      fail('Registry revision must match receipt history.');
    if (new Set(state.releases.map((row) => row.releaseVersion)).size !== state.releases.length)
      fail('Release versions are immutable and unique.');
    if (state.releases.some((row) => !same(row.channel, state.channel)))
      fail('Release channel mismatch.');
    if (state.releases.some((row) => !same(row.compatibility, state.releases[0]?.compatibility)))
      fail('Registry channel contains incompatible contracts.');
    if (state.head && !findRelease(state, state.head))
      fail('Registry head must identify an exact release.');
    if (state.releases.length > 0 && !state.head)
      fail('A populated registry requires an explicit head.');
    if (
      new Set(state.revoked.map(identity)).size !== state.revoked.length ||
      state.revoked.some((pin) => !findRelease(state, pin))
    )
      fail('Invalid revocation identities.');
    if (
      new Set(state.receipts.map((row) => row.requestId)).size !== state.receipts.length ||
      state.receipts.some((row, i) => row.revision !== i + 1 || !findRelease(state, row.pin))
    )
      fail('Invalid request receipt history.');
  });
export type CandidateRegistry = z.infer<typeof candidateRegistrySchema>;
export type CandidateApproval = (release: CandidateRelease) => boolean;
const mutationBase = z
  .object({ requestId: z.string().uuid(), expectedRevision: revision })
  .strict();
const promoteSchema = mutationBase.extend({ release: candidateReleaseSchema }).strict();
const targetSchema = mutationBase.extend({ pin: candidateReleasePinSchema }).strict();
const selectionSchema = z.discriminatedUnion('mode', [
  z
    .object({
      mode: z.literal('fixed'),
      channel: candidateChannelSchema,
      pin: candidateReleasePinSchema,
    })
    .strict(),
  z
    .object({
      mode: z.literal('follow-compatible'),
      channel: candidateChannelSchema,
      compatibility: candidateCompatibilitySchema,
    })
    .strict(),
]);
export type CandidateSelection = z.infer<typeof selectionSchema>;
export type CandidateResolution = {
  status: 'ready' | 'disabled' | 'unavailable';
  release: CandidateRelease | null;
  registryRevision: number;
  key: string | null;
  availableActions: string[];
  missingActions: string[];
  reason: string;
};
function identity(value: unknown): string {
  if (Array.isArray(value)) return '[' + value.map(identity).join(',') + ']';
  if (value !== null && typeof value === 'object')
    return (
      '{' +
      Object.entries(value)
        .sort(([a], [b]) => a.localeCompare(b))
        .map(([key, entry]) => JSON.stringify(key) + ':' + identity(entry))
        .join(',') +
      '}'
    );
  return JSON.stringify(value) ?? 'null';
}
const same = (a: unknown, b: unknown) => identity(a) === identity(b);
const pinFor = (value: CandidateRelease): CandidateReleasePin => ({
  releaseVersion: value.releaseVersion,
  renderSha256: value.renderSha256,
});
function findRelease(state: Pick<CandidateRegistry, 'releases'>, pin: CandidateReleasePin) {
  return state.releases.find((row) => same(pinFor(row), pin));
}
function freeze<T>(value: T): T {
  if (value !== null && typeof value === 'object') {
    for (const child of Object.values(value)) freeze(child);
    Object.freeze(value);
  }
  return value;
}
function approved(release: CandidateRelease, authority?: CandidateApproval): boolean {
  try {
    return authority?.(freeze(structuredClone(release))) === true;
  } catch {
    return false;
  }
}
/** Content identity is independent of registry revision, frame tick and caller object identity. */
export function candidateReleaseKey(value: CandidateRelease): string {
  const parsed = candidateReleaseSchema.parse(value);
  return identity([
    parsed.channel,
    parsed.releaseVersion,
    parsed.sourceSha256,
    parsed.renderSha256,
  ]);
}
export function createCandidateRegistry(channel: CandidateChannel): CandidateRegistry {
  return freeze(
    candidateRegistrySchema.parse({
      schemaVersion: 1,
      channel,
      revision: 0,
      releases: [],
      head: null,
      revoked: [],
      receipts: [],
    }),
  );
}
function mutate(
  inputState: CandidateRegistry,
  action: 'promote' | 'revoke' | 'rollback',
  input: z.input<typeof promoteSchema> | z.input<typeof targetSchema>,
  authority?: CandidateApproval,
) {
  const state = candidateRegistrySchema.parse(inputState);
  const command = action === 'promote' ? promoteSchema.parse(input) : targetSchema.parse(input);
  const commandIdentity = identity([action, command]);
  const previous = state.receipts.find((row) => row.requestId === command.requestId);
  if (previous) {
    if (previous.commandIdentity !== commandIdentity)
      throw new Error('Candidate request identity changed.');
    return {
      registry: freeze(state),
      receipt: freeze(previous),
      replayed: true,
    };
  }
  if (state.revision !== command.expectedRevision)
    throw new Error('Candidate registry revision changed.');
  if (state.receipts.length >= CANDIDATE_REGISTRY_LIMITS.receipts)
    throw new Error('Candidate receipt budget exceeded.');
  let selected: CandidateRelease;
  if ('release' in command) {
    selected = command.release;
    if (!same(selected.channel, state.channel)) throw new Error('Candidate channel mismatch.');
    if (state.releases.some((row) => row.releaseVersion >= selected.releaseVersion))
      throw new Error('Candidate release versions must increase without overwriting history.');
    if (state.releases.length >= CANDIDATE_REGISTRY_LIMITS.releases)
      throw new Error('Candidate release budget exceeded.');
    const current = state.head ? findRelease(state, state.head) : undefined;
    if (state.releases[0] && !same(state.releases[0].compatibility, selected.compatibility))
      throw new Error('Candidate compatibility contract changed.');
    if (
      current &&
      current.availableActions.some((item) => !selected.availableActions.includes(item))
    )
      throw new Error('Candidate update removes an available action.');
  } else {
    const found = findRelease(state, command.pin);
    if (!found) throw new Error('Candidate release pin unavailable.');
    selected = found;
    if (state.revoked.some((pin) => same(pin, command.pin)))
      throw new Error('Candidate release is revoked.');
  }
  if (!approved(selected, authority)) throw new Error('Trusted candidate approval is required.');
  const pin = pinFor(selected);
  const receipt = {
    requestId: command.requestId,
    action,
    commandIdentity,
    revision: state.revision + 1,
    pin,
  };
  const next = candidateRegistrySchema.parse({
    ...state,
    revision: receipt.revision,
    releases: action === 'promote' ? [...state.releases, selected] : state.releases,
    head: action === 'revoke' ? state.head : pin,
    revoked: action === 'revoke' ? [...state.revoked, pin] : state.revoked,
    receipts: [...state.receipts, receipt],
  });
  return { registry: freeze(next), receipt: freeze(receipt), replayed: false };
}
export function promoteCandidateRelease(
  state: CandidateRegistry,
  command: z.input<typeof promoteSchema>,
  authority?: CandidateApproval,
) {
  return mutate(state, 'promote', command, authority);
}
export function revokeCandidateRelease(
  state: CandidateRegistry,
  command: z.input<typeof targetSchema>,
  authority?: CandidateApproval,
) {
  return mutate(state, 'revoke', command, authority);
}
export function rollbackCandidateRelease(
  state: CandidateRegistry,
  command: z.input<typeof targetSchema>,
  authority?: CandidateApproval,
) {
  return mutate(state, 'rollback', command, authority);
}
/** Read-time opt-in and exact authority check; no silent fallback to different or revoked art.
 * Requested slot names are supplied by the existing animation ontology, not duplicated here.
 */
export function resolveCandidateRelease(
  inputState: CandidateRegistry,
  inputSelection: CandidateSelection,
  options: {
    candidateOptIn: boolean;
    authorize?: CandidateApproval;
    requestedActions?: readonly string[];
  },
): CandidateResolution {
  const unavailable = (reason: string, registryRevision = 0): CandidateResolution => ({
    status: 'unavailable',
    release: null,
    registryRevision,
    key: null,
    availableActions: [],
    missingActions: [...new Set(options.requestedActions ?? [])],
    reason,
  });
  if (options.candidateOptIn !== true)
    return { ...unavailable('Candidate art is disabled.'), status: 'disabled' };
  try {
    const state = candidateRegistrySchema.parse(inputState);
    const selection = selectionSchema.parse(inputSelection);
    if (!same(state.channel, selection.channel))
      return unavailable('Candidate channel mismatch.', state.revision);
    const pin = selection.mode === 'fixed' ? selection.pin : state.head;
    if (!pin) return unavailable('No approved candidate release is selected.', state.revision);
    const selected = findRelease(state, pin);
    if (!selected || state.revoked.some((value) => same(value, pin)))
      return unavailable('The exact candidate release is unavailable or revoked.', state.revision);
    if (
      selection.mode === 'follow-compatible' &&
      !same(selection.compatibility, selected.compatibility)
    )
      return unavailable('Candidate compatibility requires explicit selection.', state.revision);
    if (!approved(selected, options.authorize))
      return unavailable('Trusted candidate approval is unavailable.', state.revision);
    return freeze({
      status: 'ready',
      release: selected,
      registryRevision: state.revision,
      key: candidateReleaseKey(selected),
      availableActions: [...selected.availableActions],
      missingActions: [
        ...new Set([...(options.requestedActions ?? []), ...selected.heldActions]),
      ].filter((value) => !selected.availableActions.includes(value)),
      reason:
        selection.mode === 'fixed'
          ? 'Exact approved candidate pin.'
          : 'Approved compatible candidate channel head.',
    });
  } catch {
    return unavailable('Invalid candidate registry or selection.');
  }
}
