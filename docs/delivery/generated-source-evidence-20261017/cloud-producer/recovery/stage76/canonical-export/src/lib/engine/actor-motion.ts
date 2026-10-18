import { sampleClip, type SpeciesManifest } from '../assets/manifest';
import type { Actor } from './types';

/** Transient, product-authored timing on the shared 30 Hz clock. No physical/art review implied. */
export interface ActorMotion {
  phase: 'grounded' | 'walk' | 'hop' | 'takeoff' | 'flight' | 'landing';
  ticks: number;
  /** Retargeted airborne episodes preserve current height before resuming cruise. */
  entryLift?: number;
}
export const FLIGHT_PHASE_TICKS = 6;
export const HOP_CYCLE_TICKS = 18;
export const HOP_PLANTED_TICKS = 6;
/** The first six ticks are planted; the complete airborne interval includes its landing sample. */
export function hopCycle(ticks: number) {
  const tick = Math.max(0, Math.floor(ticks) - 1) % HOP_CYCLE_TICKS;
  return tick < HOP_PLANTED_TICKS
    ? { planted: true, fraction: 0, speed: 0 }
    : { planted: false, fraction: (tick - HOP_PLANTED_TICKS + 1) / 12, speed: 1.5 };
}
/** Walk pauses are restrained authored stepping, never a claim of annotated foot contacts. */
export function walkCycle(ticks: number) {
  const tick = Math.max(0, Math.floor(ticks) - 1) % 24;
  return { planted: tick % 12 < 5, speed: tick % 12 < 5 ? 0 : 12 / 7 };
}
export function actorIsAirborne(actor: Actor) {
  if (actor.behavior !== 'moving') return false;
  const motion = actor.motion;
  if (!motion) return actor.locomotion === 'flight';
  if (motion.phase === 'flight' || motion.phase === 'takeoff') return true;
  if (motion.phase === 'landing') return motion.ticks < FLIGHT_PHASE_TICKS;
  if (motion.phase === 'hop') {
    const cycle = hopCycle(motion.ticks);
    return !cycle.planted && cycle.fraction < 1;
  }
  return false;
}
export function beginActorMotion(actor: Actor, moving: boolean) {
  const previous = actor.motion;
  if (!moving) {
    actor.motion = { phase: 'grounded', ticks: 0 };
    return;
  }
  if (actor.locomotion !== 'flight') {
    actor.motion = {
      phase: actor.locomotion,
      ticks: previous?.phase === actor.locomotion ? previous.ticks : 0,
    };
    return;
  }
  if (actorIsAirborne(actor)) {
    if (previous?.phase === 'takeoff' || previous?.phase === 'flight')
      actor.motion = { ...previous };
    else actor.motion = { phase: 'flight', ticks: 0, entryLift: -actorMotionLift(actor) };
  } else actor.motion = { phase: 'takeoff', ticks: 0 };
}
/** Attention is a pure sampled clock, separate from the choice RNG, route, occupancy and feet. */
export function sampleActorAttention(actor: Actor) {
  if (!actor.traits || !['idle', 'perching'].includes(actor.behavior))
    return { kind: 'neutral' as const, ticks: 0 };
  const seed = actor.attentionSeed ?? actor.personality?.seed ?? 0;
  const curiosity = actor.personality?.curiosity ?? 0.5;
  const blink = actor.attentionClips?.blink ?? 6,
    look = actor.attentionClips?.look ?? 36;
  const period = Math.max(
    blink + look + 90,
    Math.round(180 + (seed % 121) + actor.traits.caution * 60 - curiosity * 60),
  );
  const tick = (actor.behaviorTicks + (seed % period)) % period;
  if (tick >= period - look) return { kind: 'look' as const, ticks: tick - (period - look) };
  if (tick >= 60 && tick < 60 + blink) return { kind: 'blink' as const, ticks: tick - 60 };
  return { kind: 'neutral' as const, ticks: tick };
}

/** Generic moving clips have no gait/transition identity in the current manifest authority.
 * Ground motion and takeoff/landing hold neutral artwork explicitly; no wing clip as walking. */
export function actorClipRequest(actor: Actor) {
  if (!actor.traits) return { clip: actor.behavior, ticks: actor.behaviorTicks, fallback: null };
  if (actor.behavior === 'moving') {
    const phase = actor.motion?.phase ?? actor.locomotion;
    if (phase !== 'flight') return { clip: 'idle', ticks: 0, fallback: `missing-${phase}-clip` };
    return {
      clip: 'moving',
      ticks: actor.motion?.ticks ?? actor.behaviorTicks,
      fallback:
        actor.animationActions && !actor.animationActions.includes('moving')
          ? 'missing-flight-clip'
          : null,
    };
  }
  const attention = sampleActorAttention(actor);
  if (actor.attentionClips && attention.kind !== 'neutral')
    return { clip: attention.kind, ticks: attention.ticks, fallback: null };
  // Explicit neutral prevents a second manifest idleSequence from rescheduling expressions.
  return {
    clip: actor.behavior,
    ticks:
      actor.attentionClips && ['idle', 'perching'].includes(actor.behavior)
        ? 0
        : actor.behaviorTicks,
    fallback: null,
  };
}
export function sampleActorClip(manifest: SpeciesManifest, actor: Actor, reducedMotion = false) {
  const request = actorClipRequest(actor);
  const expressive = request.clip === 'look' || request.clip === 'blink';
  const available = !expressive || manifest.schemaVersion === 6;
  const sample = sampleClip(
    manifest,
    available ? request.clip : 'idle',
    available ? request.ticks : 0,
    reducedMotion,
  );
  return { ...sample, fallback: sample.fallback || request.fallback !== null || !available };
}
export function actorMotionLift(actor: Actor) {
  const motion = actor.motion;
  const phase = motion?.phase;
  if (phase === 'walk' || phase === 'grounded') return 0;
  if (phase === 'hop') return -7 * Math.sin(Math.PI * hopCycle(motion!.ticks).fraction);
  if (phase === 'takeoff') return -8 * Math.min(1, motion!.ticks / FLIGHT_PHASE_TICKS);
  if (phase === 'landing')
    return -(motion?.entryLift ?? 8) * Math.max(0, 1 - motion!.ticks / FLIGHT_PHASE_TICKS);
  const start = motion?.entryLift ?? 8;
  return -(
    start +
    (8 - start) * Math.min(1, (motion?.ticks ?? FLIGHT_PHASE_TICKS) / FLIGHT_PHASE_TICKS)
  );
}
