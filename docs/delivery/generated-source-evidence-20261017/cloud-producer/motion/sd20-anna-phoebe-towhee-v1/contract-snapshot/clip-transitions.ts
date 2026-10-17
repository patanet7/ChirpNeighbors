import { animationStates, sampleClip, type AnimationState, type SpeciesManifest } from './manifest';

export interface ClipTransitionEndpoint {
  behavior: string;
  /** Caller-owned behavior clock, in 30 Hz simulation ticks; pass 0 on action entry. */
  ticks: number;
  /** Caller-known support identity only. null means known unsupported/in-air; omitted means unknown. */
  supportId?: string | null;
}
export interface ClipTransitionRequest {
  from: ClipTransitionEndpoint;
  to: ClipTransitionEndpoint;
  reducedMotion?: boolean;
  /** An interrupted routine does not imply an authored recovery or exit clip. */
  interrupted?: boolean;
}
export type ClipActionCoverage =
  'action-clip' | 'missing-action-idle-fallback' | 'unsupported-action-idle-fallback';
export interface ClipEndpointCoverage {
  requestedBehavior: string;
  coverage: ClipActionCoverage;
  sample: ReturnType<typeof sampleClip>;
}
export type ClipTransitionReason =
  | 'cross-clip-transition-not-authored'
  | 'support-change-transition-not-authored'
  | 'support-identity-unknown'
  | 'interrupted-transition-not-authored'
  | 'source-action-clip-missing'
  | 'destination-action-clip-missing'
  | 'source-action-unsupported'
  | 'destination-action-unsupported'
  | 'reduced-motion-first-pose'
  | 'source-clock-invalid-first-pose'
  | 'destination-clock-invalid-first-pose';
export interface ClipTransitionResolution {
  from: ClipEndpointCoverage;
  to: ClipEndpointCoverage;
  mode: 'continue-clip' | 'cut-to-action' | 'cut-to-idle-fallback';
  actionChanged: boolean;
  support: 'unknown-support-id' | 'same-support-id' | 'changed-support-id';
  interrupted: boolean;
  /** V2/V3/V4 have no authored cross-clip transition contract. */
  authoredTransition: false;
  blending: false;
  durationTicks: 0;
  reasons: ClipTransitionReason[];
}

function endpointCoverage(
  manifest: SpeciesManifest,
  endpoint: ClipTransitionEndpoint,
  reducedMotion: boolean,
): ClipEndpointCoverage {
  const known = animationStates.includes(endpoint.behavior as AnimationState);
  return {
    requestedBehavior: endpoint.behavior,
    coverage: !known
      ? 'unsupported-action-idle-fallback'
      : manifest.clips[endpoint.behavior as AnimationState]
        ? 'action-clip'
        : 'missing-action-idle-fallback',
    sample: sampleClip(manifest, endpoint.behavior, endpoint.ticks, reducedMotion),
  };
}

/**
 * Describe the existing immediate cut between two samples from an already validated manifest.
 * This neither advances/resets clocks nor validates world contact, reserves a support, invents
 * transition frames, or blends poses. V3 intra-clip graph edges are not cross-clip evidence.
 * Presence of an action clip makes no species-fidelity or artwork-approval claim.
 */
export function resolveClipTransition(
  manifest: SpeciesManifest,
  request: ClipTransitionRequest,
): ClipTransitionResolution {
  const from = endpointCoverage(manifest, request.from, request.reducedMotion ?? false);
  const to = endpointCoverage(manifest, request.to, request.reducedMotion ?? false);
  const actionChanged = request.from.behavior !== request.to.behavior;
  const support =
    request.from.supportId === undefined || request.to.supportId === undefined
      ? 'unknown-support-id'
      : request.from.supportId === request.to.supportId
        ? 'same-support-id'
        : 'changed-support-id';
  const interrupted = request.interrupted ?? false;
  const reasons: ClipTransitionReason[] = [];
  if (actionChanged) reasons.push('cross-clip-transition-not-authored');
  if (support === 'changed-support-id') reasons.push('support-change-transition-not-authored');
  if (support === 'unknown-support-id') reasons.push('support-identity-unknown');
  if (interrupted) reasons.push('interrupted-transition-not-authored');
  if (from.coverage === 'missing-action-idle-fallback') reasons.push('source-action-clip-missing');
  if (to.coverage === 'missing-action-idle-fallback')
    reasons.push('destination-action-clip-missing');
  if (from.coverage === 'unsupported-action-idle-fallback')
    reasons.push('source-action-unsupported');
  if (to.coverage === 'unsupported-action-idle-fallback')
    reasons.push('destination-action-unsupported');
  if (request.reducedMotion) reasons.push('reduced-motion-first-pose');
  if (!Number.isFinite(request.from.ticks)) reasons.push('source-clock-invalid-first-pose');
  if (!Number.isFinite(request.to.ticks)) reasons.push('destination-clock-invalid-first-pose');
  return {
    from,
    to,
    mode:
      to.coverage !== 'action-clip'
        ? 'cut-to-idle-fallback'
        : actionChanged || support === 'changed-support-id' || interrupted
          ? 'cut-to-action'
          : 'continue-clip',
    actionChanged,
    support,
    interrupted,
    authoredTransition: false,
    blending: false,
    durationTicks: 0,
    reasons,
  };
}
