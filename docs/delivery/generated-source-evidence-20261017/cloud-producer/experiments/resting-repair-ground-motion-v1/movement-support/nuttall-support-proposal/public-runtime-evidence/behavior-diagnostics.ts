import { animationStates, sampleClip } from '../assets/manifest';
import type { ResolvedAsset } from '../assets/registry';
import { footprintBounds } from '../assets/shape';
import {
  frameToWorld,
  poseShape,
  poseTransform,
  transformedVisualBounds,
} from '../assets/pose-geometry';
import { starterMotion } from './starter-motion';
import { presentationScale } from './presentation';
import { behaviorPriority, socialClearance, effectiveCaution } from './behavior-policy';
import type { Actor, ScenePhase } from './types';
import type { EnvironmentDecision } from './environment-policy';

/** Owner-local presentation telemetry; no observations, owner IDs or location.
 * The existing opaque registry key can identify a private asset pin and is never shared. */
export function behaviorDisplayDiagnostic(
  actor: Actor,
  asset: ResolvedAsset,
  options: {
    phase: ScenePhase;
    reducedMotion: boolean;
    illustrativeProfiles: boolean;
    mode: 'pixi' | 'static';
    worldScale: number;
    pixelRatio: number;
    flightOffset: number;
    sessionSeed?: number;
  },
) {
  const staticView = options.mode === 'static';
  const requestedClip = staticView
    ? options.phase === 'night'
      ? 'sleeping'
      : 'idle'
    : options.reducedMotion && options.phase === 'night'
      ? 'sleeping'
      : actor.behavior;
  const sample = sampleClip(
    asset.manifest,
    requestedClip,
    staticView ? 0 : actor.behaviorTicks,
    options.reducedMotion || staticView,
  );
  const transform = poseTransform(
    asset.manifest,
    sample,
    actor,
    actor.direction,
    options.flightOffset,
    presentationScale(asset.manifest, options.illustrativeProfiles),
  );
  const annotation = poseShape(asset.manifest, sample);
  const environment: EnvironmentDecision | undefined = actor.environmentDecision
    ? structuredClone(actor.environmentDecision)
    : undefined;
  return {
    sessionSeed: options.sessionSeed ?? null,
    profile: actor.profile,
    speciesId: actor.speciesId,
    traits: actor.traits,
    personality: actor.personality,
    pacing: {
      elapsedTicks: actor.behaviorTicks,
      remainingTicks: actor.remainingTicks,
      ticksPerSecond: 30,
      authoredSpeciesPacing: Boolean(starterMotion(actor.speciesId)),
    },
    groundProjection: {
      y: actor.currentGroundY ?? actor.y,
      basis: actor.currentGroundY === undefined ? 'legacy-paint-depth' : 'simulation-ground',
    },
    decision: actor.decision,
    ...(environment ? { environment } : {}),
    effective: {
      socialSpacing: socialClearance(actor),
      caution: effectiveCaution(actor),
      priorities: Object.fromEntries(
        animationStates.map((state) => [state, behaviorPriority(actor, state)]),
      ),
    },
    placement: actor.placement,
    experiment: actor.behaviorExperiment ?? null,
    locomotion: actor.locomotion,
    direction: actor.direction,
    transform,
    supportWorld: annotation ? frameToWorld(annotation.support, transform) : null,
    contactsWorld: sample.contacts.map((contact) => ({
      kind: contact.kind,
      ...frameToWorld(contact, transform),
    })),
    visualBounds: transformedVisualBounds(sample, transform),
    footprint: actor.footprint ? footprintBounds(actor.footprint, actor, actor.direction) : null,
    geometryReviewed: Boolean(annotation),
    id: actor.id,
    artworkId: actor.artworkId ?? null,
    status: asset.status,
    key: asset.key,
    frame: sample.frame,
    schemaVersion: asset.manifest.schemaVersion,
    poseId: sample.poseId,
    durationTicks: sample.durationTicks,
    pivot: sample.pivot,
    contacts: sample.contacts,
    clip: sample.state,
    clipFallback: sample.fallback,
    requestedClip,
    missingClips: animationStates.filter((state) => !asset.manifest.clips[state]),
    visualOverride: staticView
      ? 'static-still'
      : options.reducedMotion && options.phase === 'night'
        ? 'quiet-night-pose'
        : options.reducedMotion
          ? 'motion-paused'
          : 'none',
    behavior: actor.behavior,
    nextBehavior: actor.nextBehavior,
    phase: options.phase,
    slotId: actor.slotId,
    targetSlotId: actor.targetSlotId,
    x: actor.x,
    y: actor.y,
    display: {
      mode: options.mode,
      worldScale: options.worldScale,
      pixelRatio: options.pixelRatio,
      sourcePixelCss: options.worldScale * (transform.scale ?? 1),
      paused: options.reducedMotion || staticView,
    },
  };
}
export type BehaviorDisplayDiagnostic = ReturnType<typeof behaviorDisplayDiagnostic>;
