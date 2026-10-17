import { arrivalCueSchema, type ArrivalCue, type ArrivalSettlement } from '../arrivals/contracts';
import { simulationOptionsSchema, type SimulationOptions } from './behavior-contracts';
import { illustrativeProfile, speciesTraits, fictionalPersonality } from './behavior-profiles';
import {
  activitySupports,
  applyBehaviorExperiment,
  behaviorPriority,
  effectiveCaution,
  socialClearance,
  supportPriority,
} from './behavior-policy';
import type { BehaviorDecisionTrace } from './ontology-contracts';
import type { WeatherFrame } from '../weather/contracts';
import type { EnvironmentFrame } from '../weather/environment-contracts';
import {
  compatibleShelter,
  describeEnvironmentDecision,
  environmentPriority,
  environmentSupports as baseEnvironmentSupports,
  resolveEnvironmentPolicy,
} from './environment-policy';
import { boundsOverlap, footprintBounds } from '../assets/shape';
import { containsBounds, containsPoint, type SceneManifest } from '../scenes/manifest';
import { findRoute, sceneDefinition } from './scenes';
import type {
  Actor,
  Affordance,
  Behavior,
  SceneBird,
  ScenePhase,
  SceneSlot,
  RoutineBehavior,
  Simulation,
  YardSetting,
} from './types';
import { objectFootprint, type ObjectCapability, type YardObject } from '../domain/scene';

export type { Actor, Behavior, SceneBird, Simulation, YardPalette, YardSetting } from './types';
export const FIXED_STEP_SECONDS = 1 / 30;
const MOVE_SPEED = 112;
/** Local physical-preview admission; deliberately outside saved/wire SimulationOptions. */
export interface PreviewSurfaceAdmission {
  actorId: string;
  objectId: string;
  generation: number;
  revision: number;
  wet: boolean;
}
const previewSurfaces = new WeakMap<Simulation, PreviewSurfaceAdmission>();
export function setPreviewSurfaceAdmission(sim: Simulation, input: PreviewSurfaceAdmission | null) {
  if (input) previewSurfaces.set(sim, { ...input });
  else previewSurfaces.delete(sim);
}
function environmentSupports(sim: Simulation, actor: Actor, slot: SceneSlot, behavior: Behavior) {
  const surface = previewSurfaces.get(sim);
  if (surface?.actorId === actor.id && slot.affordance === 'bath' && behavior === 'bathing') {
    if (!surface.wet || slot.objectId !== surface.objectId) return false;
  }
  return baseEnvironmentSupports(sim, actor, slot, behavior);
}

/** Uses normal clearance, route construction and the shared in-flight reservation map. */
export function requestPreviewSurfaceActivity(
  sim: Simulation,
  identity: Omit<PreviewSurfaceAdmission, 'wet'>,
  slotId: string,
): 'started' | 'blocked-dry' | 'blocked-environment' | 'occupied' | 'stale-object' | 'unavailable' {
  const surface = previewSurfaces.get(sim);
  if (
    !surface ||
    Object.entries(identity).some(
      ([key, value]) => surface[key as keyof PreviewSurfaceAdmission] !== value,
    )
  )
    return 'stale-object';
  if (!surface.wet) return 'blocked-dry';
  if (sim.phase === 'night' || sim.environment?.seekShelter) return 'blocked-environment';
  const actor = sim.actors.get(identity.actorId);
  const slot = sim.scene.slots.find(
    (value) =>
      value.id === slotId && value.objectId === identity.objectId && value.affordance === 'bath',
  );
  if (!actor || !slot || !environmentSupports(sim, actor, slot, 'bathing')) return 'unavailable';
  if (!slotAvailable(sim, actor, slot)) return 'occupied';
  if (!findRoute(sim.scene, actor.slotId, slot.id).length) return 'unavailable';
  // An explicit request supersedes only this actor's old in-flight destination.
  if (actor.targetSlotId && sim.occupancy.get(actor.targetSlotId) === actor.id)
    sim.occupancy.delete(actor.targetSlotId);
  actor.targetSlotId = null;
  return beginActivity(sim, actor, slot, 'bathing') ? 'started' : 'unavailable';
}

/** A local semantic drinking action uses the existing idle clip, without extending Behavior. */
export function holdPreviewSurfaceActivity(
  sim: Simulation,
  actorId: string,
  action: 'drink' | 'bath',
) {
  const surface = previewSurfaces.get(sim);
  const actor = sim.actors.get(actorId);
  const slot = sim.scene.slots.find((value) => value.id === actor?.slotId);
  if (
    !actor ||
    surface?.actorId !== actorId ||
    !slot ||
    sim.occupancy.get(slot.id) !== actor.id ||
    actor.targetSlotId !== null ||
    Math.hypot(actor.x - slot.x, actor.y - slot.y) > 1 ||
    !environmentSupports(sim, actor, slot, 'bathing') ||
    sim.phase === 'night' ||
    sim.environment?.seekShelter
  )
    return false;
  actor.behavior = action === 'bath' ? 'bathing' : 'idle';
  actor.nextBehavior = actor.behavior;
  actor.remainingTicks = Math.max(actor.remainingTicks, 6);
  return true;
}

/** Release only the selected actor and fly away from its current point; never teleport it. */
export function cancelPreviewSurfaceActivity(sim: Simulation, actorId: string) {
  const actor = sim.actors.get(actorId);
  if (!actor || previewSurfaces.get(sim)?.actorId !== actorId) return;
  releaseReservations(sim, actor);
  actor.nextBehavior = 'idle';
  const target = sim.scene.slots
    .filter((slot) => slot.affordance === 'ground' && slotAvailable(sim, actor, slot))
    .sort(
      (a, b) => Math.hypot(a.x - actor.x, a.y - actor.y) - Math.hypot(b.x - actor.x, b.y - actor.y),
    )[0];
  if (target && beginActivity(sim, actor, target, 'idle')) return;
  transition(actor, 'idle', 1);
}
/** Explicit local preview intent only; normal simulation callers never enter this seam.
 * Hops require a settled, owned ground start and a short fully clear ground route. An idle
 * request from elevated/in-flight support follows the existing route back to ground. */
export function requestPreviewGroundActivity(
  sim: Simulation,
  actorId: string,
  action: 'hop' | 'idle',
): 'started' | 'unavailable' | 'blocked-environment' {
  const actor = sim.actors.get(actorId);
  if (
    !actor ||
    previewSurfaces.get(sim)?.actorId !== actorId ||
    (action !== 'hop' && action !== 'idle') ||
    actor.placement !== 'placed'
  )
    return 'unavailable';
  if (sim.phase === 'night' || sim.environment?.seekShelter) return 'blocked-environment';
  const current = sim.scene.slots.find((slot) => slot.id === actor.slotId);
  if (
    (actor.slotId && sim.occupancy.get(actor.slotId) !== actor.id) ||
    (actor.targetSlotId && sim.occupancy.get(actor.targetSlotId) !== actor.id)
  )
    return 'unavailable';
  if (
    action === 'hop' &&
    (!current ||
      current.affordance !== 'ground' ||
      actor.targetSlotId ||
      actor.route.length ||
      Math.hypot(actor.x - current.x, actor.y - current.y) > 1)
  )
    return 'unavailable';
  if (
    action === 'idle' &&
    current?.affordance === 'ground' &&
    !actor.targetSlotId &&
    !actor.route.length &&
    Math.hypot(actor.x - current.x, actor.y - current.y) <= 1
  )
    return beginActivity(sim, actor, current, 'idle') ? 'started' : 'unavailable';
  const candidates = sim.scene.slots
    .filter(
      (slot) =>
        slot.affordance === 'ground' &&
        slot.id !== actor.slotId &&
        slotAvailable(sim, actor, slot) &&
        environmentSupports(sim, actor, slot, 'idle'),
    )
    .sort(
      (a, b) =>
        Math.hypot(a.x - actor.x, a.y - actor.y) - Math.hypot(b.x - actor.x, b.y - actor.y) ||
        a.id.localeCompare(b.id),
    );
  const target = candidates.find((slot) => {
    const route = findRoute(sim.scene, actor.slotId, slot.id);
    if (!route.length) return false;
    if (action === 'idle') return true;
    if (Math.hypot(slot.x - actor.x, slot.y - actor.y) > 120) return false;
    let previous = { x: actor.x, y: actor.y },
      distance = 0;
    for (const point of route) {
      distance += Math.hypot(point.x - previous.x, point.y - previous.y);
      if (point.affordance !== 'ground' || distance > 120) return false;
      const start = clearanceBounds(actor, previous),
        end = clearanceBounds(actor, point);
      const corridor = {
        left: Math.min(start.left, end.left),
        right: Math.max(start.right, end.right),
        top: Math.min(start.top, end.top),
        bottom: Math.max(start.bottom, end.bottom),
      };
      if (
        !sim.scene.manifest.zones.walkable.some((zone) => containsBounds(zone, corridor)) ||
        sim.scene.objects.some((object) => boundsOverlap(corridor, objectFootprint(object))) ||
        !Array.from({ length: 9 }, (_, i) => i / 8).every((f) =>
          clearanceAvailable(sim, actor, {
            x: previous.x + (point.x - previous.x) * f,
            y: previous.y + (point.y - previous.y) * f,
          }),
        )
      )
        return false;
      previous = point;
    }
    return true;
  });
  if (!target) return 'unavailable';
  if (actor.targetSlotId && sim.occupancy.get(actor.targetSlotId) === actor.id)
    sim.occupancy.delete(actor.targetSlotId);
  actor.targetSlotId = null;
  if (!beginActivity(sim, actor, target, 'idle')) return 'unavailable';
  if (action === 'hop') {
    actor.locomotion = 'hop';
    if (actor.decision)
      actor.decision.locomotion = { mode: 'hop', reason: 'explicit-preview-clear-ground-hop' };
  }
  return 'started';
}

/** Decorative activity budgets, in fixed 30 Hz ticks; no evidence or breeding semantics. */
export const ROUTINE_TRAVEL_LIMIT = 300;
export const ROUTINES: Readonly<
  Record<
    RoutineBehavior,
    {
      capability: ObjectCapability;
      minTicks: number;
      maxTicks: number;
    }
  >
> = {
  playing: { capability: 'play', minTicks: 60, maxTicks: 119 },
  nesting: { capability: 'nest-building', minTicks: 120, maxTicks: 179 },
};
const ROUTINE_ORDER: readonly RoutineBehavior[] = ['playing', 'nesting'];
function isRoutine(behavior: Behavior): behavior is RoutineBehavior {
  return behavior === 'playing' || behavior === 'nesting';
}
function duration(actor: Actor, behavior: Behavior) {
  const limits = isRoutine(behavior) ? ROUTINES[behavior] : { minTicks: 80, maxTicks: 179 };
  return limits.minTicks + Math.floor(random(actor) * (limits.maxTicks - limits.minTicks + 1));
}

export function seedFromId(id: string): number {
  let seed = 2166136261;
  for (let i = 0; i < id.length; i++) seed = Math.imul(seed ^ id.charCodeAt(i), 16777619);
  return seed >>> 0 || 1;
}

function random(actor: Actor): number {
  let x = actor.randomState;
  x ^= x << 13;
  x ^= x >>> 17;
  x ^= x << 5;
  actor.randomState = x >>> 0 || 1;
  return actor.randomState / 0x100000000;
}

function clearGround(sim: Simulation, x: number, y: number, actor?: Actor): boolean {
  if (actor && (actor.footprint || actor.profile)) {
    const bounds = clearanceBounds(actor, { x, y });
    return (
      sim.scene.manifest.zones.walkable.some((zone) => containsBounds(zone, bounds)) &&
      !sim.scene.objects.some((object) => boundsOverlap(bounds, objectFootprint(object))) &&
      clearanceAvailable(sim, actor, { x, y })
    );
  }
  return (
    sim.scene.manifest.zones.walkable.some((zone) => containsPoint(zone, x, y)) &&
    !sim.scene.objects.some((object) => {
      const box = objectFootprint(object);
      return x >= box.left - 20 && x <= box.right + 20 && y >= box.top - 12 && y <= box.bottom + 12;
    })
  );
}

const LEGACY_CLEARANCE = { left: 20, right: 20, back: 12, front: 12 };
/** Reserve enough ground space to face either way. Travel can change facing after a
 * destination is claimed; an asymmetric reviewed body must not expand into a
 * neighbor or obstacle when it turns. Actual pose geometry remains unchanged. */
function clearanceBounds(actor: Actor, point: { x: number; y: number }) {
  const footprint = actor.footprint ?? LEGACY_CLEARANCE;
  const radius = Math.max(footprint.left, footprint.right);
  return footprintBounds({ ...footprint, left: radius, right: radius }, point);
}
/** Ground-plane footprints never use sprite height/rotation; reservations include in-flight targets. */
export function clearanceAvailable(
  sim: Simulation,
  actor: Actor,
  point: { x: number; y: number },
  slotId?: string,
) {
  if (slotId && sim.occupancy.has(slotId) && sim.occupancy.get(slotId) !== actor.id) return false;
  for (const other of sim.actors.values()) {
    if (
      other.id === actor.id ||
      other.placement === 'waiting-for-space' ||
      (!actor.footprint && !other.footprint && !actor.profile && !other.profile)
    )
      continue;
    const otherSlot = other.targetSlotId ?? other.slotId;
    const slot = otherSlot ? sim.scene.slots.find((item) => item.id === otherSlot) : undefined;
    const otherPoint =
      slot ?? (other.behavior === 'moving' ? other.route.at(-1) : undefined) ?? other;
    const spacing = Math.max(socialClearance(actor), socialClearance(other));
    const first = clearanceBounds(actor, point);
    if (
      boundsOverlap(
        {
          left: first.left - spacing,
          right: first.right + spacing,
          top: first.top - spacing,
          bottom: first.bottom + spacing,
        },
        clearanceBounds(other, otherPoint),
      )
    )
      return false;
  }
  return true;
}
/** Structural fit is separate from temporary occupancy, so impossible bodies cannot hold FIFO turns. */
function slotFitsWorld(sim: Simulation, actor: Actor, slot: SceneSlot) {
  return (
    !(actor.footprint || actor.profile) ||
    containsBounds(
      { left: 0, right: sim.scene.width, top: 0, bottom: sim.scene.height },
      clearanceBounds(actor, slot),
    )
  );
}
function slotAvailable(sim: Simulation, actor: Actor, slot: SceneSlot) {
  return (
    slotFitsWorld(sim, actor, slot) &&
    clearanceAvailable(sim, actor, slot, slot.id) &&
    (slot.affordance !== 'ground' ||
      (!actor.footprint && !actor.profile) ||
      clearGround(sim, slot.x, slot.y, actor))
  );
}
function routineFitsScene(sim: Simulation, actor: Actor, behavior: RoutineBehavior) {
  if (actor.placement !== 'placed' || behaviorPriority(actor, behavior) <= 0) return false;
  // Original point-only callers keep their existing queues even when an object is absent.
  if (!actor.footprint && !actor.profile && !actor.traits) return true;
  return sim.scene.slots.some(
    (slot) => activitySupports(actor, slot, behavior) && slotFitsWorld(sim, actor, slot),
  );
}

function overflowPoint(sim: Simulation, actor: Actor) {
  const area = sim.scene.manifest.navigation.overflow;
  return { x: area.left + (actor.randomState % (area.right - area.left)), y: area.y };
}

function roamingPoint(sim: Simulation, actor: Actor) {
  for (let attempt = 0; attempt < 24; attempt++) {
    const area = sim.scene.manifest.navigation.roaming;
    const point = {
      x: area.left + random(actor) * (area.right - area.left),
      y: area.top + random(actor) * (area.bottom - area.top),
    };
    if (clearGround(sim, point.x, point.y, actor)) return point;
  }
  if (actor.footprint || actor.profile) {
    const area = sim.scene.manifest.navigation.roaming;
    for (let y = area.top; y <= area.bottom; y += 16)
      for (let x = area.left; x <= area.right; x += 16)
        if (clearGround(sim, x, y, actor)) return { x, y };
    return null;
  }
  // Point-only legacy callers retain their original overflow placement.
  return overflowPoint(sim, actor);
}

function transition(
  actor: Actor,
  behavior: Behavior,
  ticks: number,
  reason = 'activity-transition',
) {
  if (actor.decision) actor.decision.transition = { from: actor.behavior, to: behavior, reason };
  actor.behavior = behavior;
  actor.behaviorTicks = 0;
  actor.remainingTicks = ticks;
  actor.frame = 0;
  actor.transitionCount++;
}

function restAtSlot(sim: Simulation, actor: Actor) {
  const slot = sim.scene.slots.find((item) => item.id === actor.slotId);
  const behavior: Behavior = slot?.affordance === 'perch' ? 'perching' : 'idle';
  transition(actor, behavior, 55 + Math.floor(random(actor) * 85));
}

function traceDecision(
  sim: Simulation,
  actor: Actor,
  trigger: BehaviorDecisionTrace['trigger'],
  behavior: Behavior,
  slot: SceneSlot | undefined,
  reasons: string[],
  candidates: BehaviorDecisionTrace['candidates'] = [],
) {
  actor.decision = {
    schemaVersion: 1,
    provenance: 'decorative-simulation',
    tick: sim.ticks,
    phase: sim.phase,
    trigger,
    selected: {
      behavior,
      slotId: slot?.id ?? null,
      affordance: slot?.affordance ?? null,
      capability: slot?.capability ?? null,
      priority:
        candidates.find((candidate) => candidate.behavior === behavior)?.priority ??
        behaviorPriority(actor, behavior),
      reasons: [...reasons, ...(actor.behaviorExperiment ? ['developer-experiment'] : [])],
    },
    candidates,
    locomotion: { mode: actor.locomotion, reason: 'stationary-support' },
    transition: { from: actor.behavior, to: actor.behavior, reason: reasons[0]! },
  };
}
function waitForSpace(sim: Simulation, actor: Actor, trigger: BehaviorDecisionTrace['trigger']) {
  releaseReservations(sim, actor);
  const environmentDecision = describeEnvironmentDecision(sim, actor);
  if (environmentDecision) actor.environmentDecision = environmentDecision;
  else delete actor.environmentDecision;
  actor.placement = 'waiting-for-space';
  actor.nextBehavior = 'idle';
  traceDecision(sim, actor, trigger, 'idle', undefined, ['no-clearance-waiting']);
  transition(actor, 'idle', 30, 'no-clearance-waiting');
}
function placeActor(
  sim: Simulation,
  actor: Actor,
  preferredIndex = 0,
  trigger: BehaviorDecisionTrace['trigger'] = 'initial-placement',
) {
  const slots = sim.scene.slots;
  const ordered = slots
    .map((_, offset) => slots[(offset + preferredIndex) % slots.length]!)
    .filter(
      (slot) =>
        slot.affordance !== 'nest' &&
        (!actor.traits || supportPriority(actor, slot, sim.phase === 'night') > 0),
    );
  if (actor.traits)
    ordered.sort(
      (a, b) =>
        supportPriority(actor, b, sim.phase === 'night') -
        supportPriority(actor, a, sim.phase === 'night'),
    );
  for (const slot of ordered) {
    if (slotAvailable(sim, actor, slot)) {
      actor.placement = 'placed';
      actor.x = slot.x;
      actor.y = slot.y;
      actor.slotId = slot.id;
      sim.occupancy.set(slot.id, actor.id);
      traceDecision(sim, actor, trigger, slot.affordance === 'perch' ? 'perching' : 'idle', slot, [
        actor.traits ? 'highest-available-affinity' : 'legacy-slot-order',
        'clearance-verified',
      ]);
      restAtSlot(sim, actor);
      return;
    }
  }
  const point = roamingPoint(sim, actor);
  if (!point) {
    waitForSpace(sim, actor, trigger);
    return;
  }
  actor.placement = 'placed';
  actor.x = point.x;
  actor.y = point.y;
  actor.slotId = null;
  traceDecision(sim, actor, trigger, 'idle', undefined, ['safe-ground-fallback']);
  restAtSlot(sim, actor);
}

export function createSimulation(
  birds: readonly SceneBird[],
  setting: YardSetting = 'garden',
  objects?: readonly YardObject[],
  phase: ScenePhase = 'day',
  manifest?: SceneManifest,
  options: SimulationOptions = {},
): Simulation {
  const simulation: Simulation = {
    environment: null,
    options: simulationOptionsSchema.parse(options),
    decorativeVisit: {
      phase: 'idle',
      ticks: 0,
      pending: false,
      sequence: 0,
      participants: new Map(),
    },
    arrival: null,
    arrivalSettlements: [],
    settledArrivalTokens: [],
    phase,
    scene: sceneDefinition(setting, objects, manifest),
    actors: new Map(),
    occupancy: new Map(),
    routineTurns: { playing: [], nesting: [] },
    ticks: 0,
    accumulator: 0,
  };
  reconcileBirds(simulation, birds);
  return simulation;
}

/** Existing actor references, schedules and positions survive promotion, naming and list refreshes. */
export function reconcileBirds(sim: Simulation, birds: readonly SceneBird[]) {
  const incoming = new Map(birds.map((bird) => [bird.id, bird]));
  const resized: Actor[] = [];
  for (const [id] of sim.actors) {
    if (!incoming.has(id)) {
      if (sim.arrival?.birdId === id) finishArrival(sim, 'cancelled');
      sim.decorativeVisit.participants.delete(id);
      sim.actors.delete(id);
      for (const [slot, owner] of sim.occupancy) if (owner === id) sim.occupancy.delete(slot);
    }
  }
  for (const bird of [...incoming.values()].sort((a, b) => a.id.localeCompare(b.id))) {
    const existing = sim.actors.get(bird.id);
    if (existing) {
      if (bird.name === undefined) delete existing.name;
      else existing.name = bird.name;
      const traits = sim.options.illustrativeProfiles
        ? applyBehaviorExperiment(speciesTraits(bird.speciesId), bird.behaviorExperiment)
        : null;
      if (JSON.stringify(existing.traits) !== JSON.stringify(traits)) resized.push(existing);
      existing.traits = traits;
      if (bird.behaviorExperiment) existing.behaviorExperiment = bird.behaviorExperiment;
      else delete existing.behaviorExperiment;
      existing.personality = sim.options.illustrativeProfiles
        ? fictionalPersonality(bird.id)
        : null;
      existing.speciesId = bird.speciesId;
      existing.profile = sim.options.illustrativeProfiles
        ? illustrativeProfile(bird.speciesId)
        : null;
      if (JSON.stringify(existing.footprint) !== JSON.stringify(bird.footprint))
        resized.push(existing);
      if (bird.footprint) existing.footprint = bird.footprint;
      else delete existing.footprint;
      if (bird.artworkId === undefined) delete existing.artworkId;
      else existing.artworkId = bird.artworkId;
      continue;
    }
    const actor: Actor = {
      ...bird,
      traits: sim.options.illustrativeProfiles
        ? applyBehaviorExperiment(speciesTraits(bird.speciesId), bird.behaviorExperiment)
        : null,
      personality: sim.options.illustrativeProfiles ? fictionalPersonality(bird.id) : null,
      decision: null,
      placement: 'placed',
      x: 0,
      y: 0,
      profile: sim.options.illustrativeProfiles ? illustrativeProfile(bird.speciesId) : null,
      locomotion: 'flight',
      behavior: 'idle',
      behaviorTicks: 0,
      remainingTicks: 0,
      direction: 1,
      frame: 0,
      slotId: null,
      targetSlotId: null,
      route: [],
      nextBehavior: 'idle',
      lastActivity: 'idle',
      lastRoutine: null,
      randomState: seedFromId(
        sim.options.sessionSeed === undefined ? bird.id : `${sim.options.sessionSeed}:${bird.id}`,
      ),
      transitionCount: 0,
    };
    sim.actors.set(actor.id, actor);
    placeActor(sim, actor, actor.randomState % sim.scene.slots.length);
  }
  for (const actor of new Set(resized)) {
    if (sim.environment) delete actor.environmentKey;
    const claimedId = actor.targetSlotId ?? actor.slotId;
    const slot = claimedId ? sim.scene.slots.find((entry) => entry.id === claimedId) : undefined;
    if (
      slot
        ? !slotAvailable(sim, actor, slot) ||
          (actor.traits &&
            (actor.behavior === 'moving'
              ? !environmentSupports(sim, actor, slot, actor.nextBehavior)
              : isRoutine(actor.behavior) ||
                  ['feeding', 'bathing', 'singing', 'sleeping'].includes(actor.behavior)
                ? !environmentSupports(sim, actor, slot, actor.behavior)
                : supportPriority(actor, slot) <= 0))
        : !clearGround(sim, actor.x, actor.y, actor)
    ) {
      for (const [id, owner] of sim.occupancy) if (owner === actor.id) sim.occupancy.delete(id);
      actor.slotId = null;
      actor.targetSlotId = null;
      actor.route = [];
      actor.nextBehavior = 'idle';
      placeActor(sim, actor, actor.randomState % sim.scene.slots.length);
    }
  }
  for (const routine of ROUTINE_ORDER) {
    const turns = sim.routineTurns[routine].filter(
      (id) => incoming.has(id) && routineFitsScene(sim, sim.actors.get(id)!, routine),
    );
    for (const id of [...incoming.keys()].sort())
      if (!turns.includes(id) && routineFitsScene(sim, sim.actors.get(id)!, routine))
        turns.push(id);
    sim.routineTurns[routine] = turns;
  }
}

/** Object edits repair transient positions and reservations, retaining safe schedules and RNG state. */
export function switchScene(
  sim: Simulation,
  setting: YardSetting,
  objects?: readonly YardObject[],
  manifest?: SceneManifest,
) {
  const next = sceneDefinition(setting, objects, manifest);
  const signature = (scene: typeof next) =>
    JSON.stringify([scene.id, scene.manifest, scene.objects]);
  if (signature(sim.scene) === signature(next)) return;
  cancelDecorativeVisit(sim);
  if (sim.arrival) finishArrival(sim, 'placed');
  const previous = sim.scene;
  sim.scene = next;
  sim.occupancy.clear();
  const slots = new Map(next.slots.map((slot) => [slot.id, slot]));
  const oldSlots = new Map(previous.slots.map((slot) => [slot.id, slot]));
  const displaced: Actor[] = [];
  for (const actor of sim.actors.values()) {
    if (sim.environment) delete actor.environmentKey;
    const claimedId = actor.targetSlotId ?? actor.slotId;
    const landing = actor.route.at(-1);
    const unreservedLandingBlocked =
      !claimedId &&
      (actor.behavior === 'moving' && landing
        ? !clearGround(sim, landing.x, landing.y, actor)
        : !clearGround(sim, actor.x, actor.y, actor));
    const slot = claimedId ? slots.get(claimedId) : undefined;
    const oldSlot = claimedId ? oldSlots.get(claimedId) : undefined;
    if (
      slot &&
      slot.affordance === oldSlot?.affordance &&
      slot.capability === oldSlot?.capability &&
      slotAvailable(sim, actor, slot) &&
      (!actor.traits ||
        (actor.behavior === 'moving'
          ? environmentSupports(sim, actor, slot, actor.nextBehavior)
          : ['sleeping', 'feeding', 'bathing', 'singing', 'playing', 'nesting'].includes(
                actor.behavior,
              )
            ? environmentSupports(sim, actor, slot, actor.behavior)
            : supportPriority(actor, slot) > 0))
    ) {
      sim.occupancy.set(slot.id, actor.id);
      if (actor.targetSlotId) actor.route = [{ x: slot.x, y: slot.y }];
      else {
        actor.x = slot.x;
        actor.y = slot.y;
      }
    } else if (claimedId || unreservedLandingBlocked) {
      actor.slotId = null;
      actor.targetSlotId = null;
      actor.route = [];
      actor.nextBehavior = 'idle';
      actor.lastActivity = 'idle';
      transition(actor, 'idle', Math.max(30, actor.remainingTicks));
      displaced.push(actor);
    }
  }
  // Only displaced actors need a safe ground anchor; unaffected birds do not restart routines.
  for (const actor of displaced) {
    const free = next.slots
      .filter((slot) => slot.affordance === 'ground' && slotAvailable(sim, actor, slot))
      .sort(
        (a, b) =>
          Math.hypot(a.x - actor.x, a.y - actor.y) - Math.hypot(b.x - actor.x, b.y - actor.y),
      )[0];
    if (free) {
      actor.placement = 'placed';
      actor.x = free.x;
      actor.y = free.y;
      actor.slotId = free.id;
      sim.occupancy.set(free.id, actor.id);
    } else {
      const point = roamingPoint(sim, actor);
      if (!point) {
        waitForSpace(sim, actor, 'scene-edit');
        continue;
      }
      actor.placement = 'placed';
      actor.x = point.x;
      actor.y = point.y;
    }
    traceDecision(sim, actor, 'scene-edit', 'idle', free, [
      'edited-support-repaired',
      'safe-ground-fallback',
    ]);
  }
}

const ACTIVITIES: readonly { behavior: Behavior; affordance: Affordance }[] = [
  { behavior: 'feeding', affordance: 'feed' },
  { behavior: 'bathing', affordance: 'bath' },
  { behavior: 'singing', affordance: 'perch' },
  { behavior: 'perching', affordance: 'perch' },
  { behavior: 'idle', affordance: 'ground' },
];

function configureTravel(
  sim: Simulation,
  actor: Actor,
  point: { x: number; y: number },
  destinationGround: boolean,
) {
  actor.locomotion = 'flight';
  const movement = actor.traits?.locomotion ?? actor.profile?.movement;
  const current = sim.scene.slots.find((slot) => slot.id === actor.slotId);
  let reason = 'flight-corridor-required';
  if (
    movement &&
    destinationGround &&
    (!current || current.affordance === 'ground') &&
    Math.hypot(point.x - actor.x, point.y - actor.y) <= 120
  ) {
    const start = clearanceBounds(actor, actor);
    const end = clearanceBounds(actor, point);
    const corridor = {
      left: Math.min(start.left, end.left),
      right: Math.max(start.right, end.right),
      top: Math.min(start.top, end.top),
      bottom: Math.max(start.bottom, end.bottom),
    };
    if (
      sim.scene.manifest.zones.walkable.some((zone) => containsBounds(zone, corridor)) &&
      !sim.scene.objects.some((object) => boundsOverlap(corridor, objectFootprint(object))) &&
      Array.from({ length: 9 }, (_, index) => index / 8).every((fraction) =>
        clearanceAvailable(sim, actor, {
          x: actor.x + (point.x - actor.x) * fraction,
          y: actor.y + (point.y - actor.y) * fraction,
        }),
      )
    ) {
      if (random(actor) < movement.hopBias) {
        actor.locomotion = 'hop';
        reason = 'clear-ground-hop-bias';
      } else reason = 'flight-selected-by-hop-bias';
    } else reason = 'ground-corridor-blocked';
  }
  if (actor.decision) actor.decision.locomotion = { mode: actor.locomotion, reason };
}

function beginActivity(sim: Simulation, actor: Actor, target: SceneSlot, behavior: Behavior) {
  if (!environmentSupports(sim, actor, target, behavior) || !slotAvailable(sim, actor, target))
    return false;
  const route = findRoute(sim.scene, actor.slotId, target.id);
  if (!route.length) return false;
  actor.placement = 'placed';
  if (actor.slotId === target.id) {
    actor.lastActivity = behavior;
    actor.nextBehavior = behavior;
    transition(actor, behavior, duration(actor, behavior), 'activity-on-current-support');
    return true;
  }
  configureTravel(sim, actor, target, target.affordance === 'ground');
  if (actor.slotId) sim.occupancy.delete(actor.slotId);
  actor.slotId = null;
  actor.targetSlotId = target.id;
  sim.occupancy.set(target.id, actor.id);
  actor.route = route.map(({ x, y }) => ({ x, y }));
  actor.nextBehavior = behavior;
  transition(actor, 'moving', 0, 'travel-to-selected-support');
  return true;
}

type Candidate = { detail: BehaviorDecisionTrace['candidates'][number]; slots: SceneSlot[] };
function activityCandidates(sim: Simulation, actor: Actor): Candidate[] {
  for (const behavior of ROUTINE_ORDER) {
    const turns = sim.routineTurns[behavior].filter((id) => {
      const resident = sim.actors.get(id);
      return resident && routineFitsScene(sim, resident, behavior);
    });
    for (const resident of sim.actors.values())
      if (routineFitsScene(sim, resident, behavior) && !turns.includes(resident.id))
        turns.push(resident.id);
    sim.routineTurns[behavior] = turns;
  }
  return [...ROUTINE_ORDER, ...ACTIVITIES.map((activity) => activity.behavior)].map((behavior) => {
    const priority = environmentPriority(sim, actor, behavior);
    const rejected = { occupiedOrClearance: 0, unsupported: 0, unreachable: 0 };
    const slots = sim.scene.slots.filter((slot) => {
      if (!environmentSupports(sim, actor, slot, behavior)) {
        rejected.unsupported++;
        return false;
      }
      if (!slotAvailable(sim, actor, slot)) {
        rejected.occupiedOrClearance++;
        return false;
      }
      if (!findRoute(sim.scene, actor.slotId, slot.id).length) {
        rejected.unreachable++;
        return false;
      }
      return true;
    });
    const reasons = [actor.traits ? 'illustrative-trait-priority' : 'legacy-behavior-policy'];
    if (
      actor.personality &&
      actor.traits &&
      ['playing', 'nesting', 'bathing', 'singing'].includes(behavior)
    )
      reasons.push('fictional-personality-modifier');
    let eligible = priority > 0;
    if (behaviorPriority(actor, behavior) <= 0) reasons.push('trait-ineligible');
    if (isRoutine(behavior)) {
      if (!routineFitsScene(sim, actor, behavior)) {
        eligible = false;
        reasons.push('no-compatible-routine-support');
      }
      if (isRoutine(actor.lastActivity)) {
        eligible = false;
        reasons.push('ordinary-activity-interleave');
      }
      if (sim.routineTurns[behavior][0] !== actor.id) {
        eligible = false;
        reasons.push('fifo-waiting-turn');
      }
    } else if (behavior === actor.lastActivity) {
      eligible = false;
      reasons.push('avoid-immediate-repeat');
    }
    if (!slots.length) {
      eligible = false;
      reasons.push('no-available-support');
    }
    return {
      detail: { behavior, eligible, priority, reasons, availableSlots: slots.length, rejected },
      slots,
    };
  });
}
function chooseRoutine(sim: Simulation, actor: Actor, candidates: Candidate[]): boolean {
  const order = [...ROUTINE_ORDER].sort(
    (a, b) =>
      (a === actor.lastRoutine ? 1 : 0) - (b === actor.lastRoutine ? 1 : 0) ||
      behaviorPriority(actor, b) - behaviorPriority(actor, a),
  );
  for (const behavior of order) {
    const candidate = candidates.find((value) => value.detail.behavior === behavior)!;
    if (!candidate.detail.eligible) continue;
    const slots = [...candidate.slots].sort(
      (a, b) =>
        Math.hypot(a.x - actor.x, a.y - actor.y) - Math.hypot(b.x - actor.x, b.y - actor.y) ||
        a.id.localeCompare(b.id),
    );
    for (const target of slots) {
      traceDecision(
        sim,
        actor,
        'activity',
        behavior,
        target,
        [
          'eligible-capability',
          'fifo-finite-turn',
          'nearest-available-support',
          'clearance-verified',
        ],
        candidates.map((value) => value.detail),
      );
      if (beginActivity(sim, actor, target, behavior)) {
        actor.lastRoutine = behavior;
        const turns = sim.routineTurns[behavior];
        turns.push(turns.shift()!);
        return true;
      }
    }
  }
  return false;
}
function chooseActivity(sim: Simulation, actor: Actor) {
  const candidates = activityCandidates(sim, actor);
  const shelter = sim.environment?.seekShelter
    ? candidates
        .find((value) => value.detail.behavior === 'idle')!
        .slots.filter((slot) => compatibleShelter(sim, actor, slot))
        .sort(
          (a, b) =>
            Math.hypot(a.x - actor.x, a.y - actor.y) - Math.hypot(b.x - actor.x, b.y - actor.y) ||
            a.id.localeCompare(b.id),
        )[0]
    : undefined;
  const environmentDecision = describeEnvironmentDecision(sim, actor, shelter);
  if (environmentDecision) actor.environmentDecision = environmentDecision;
  else delete actor.environmentDecision;
  if (shelter) {
    const candidate = candidates.find((value) => value.detail.behavior === 'idle')!;
    candidate.detail.eligible = true;
    candidate.detail.priority = Math.max(1, candidate.detail.priority);
    candidate.detail.reasons = ['eligible-affordance', 'clearance-verified'];
    traceDecision(
      sim,
      actor,
      'activity',
      'idle',
      shelter,
      ['eligible-affordance', 'clearance-verified'],
      candidates.map((value) => value.detail),
    );
    if (beginActivity(sim, actor, shelter, 'idle')) return;
  }
  // FIFO turns remain finite and interleaved; weighted species policy never starves an eligible turn.
  if (chooseRoutine(sim, actor, candidates)) return;
  let ordered: Candidate[];
  if (actor.traits || actor.profile) {
    const remaining = candidates.filter(
      (value) => !isRoutine(value.detail.behavior) && value.detail.eligible,
    );
    ordered = [];
    while (remaining.length) {
      let choice = random(actor) * remaining.reduce((sum, value) => sum + value.detail.priority, 0);
      let index = 0;
      while (index < remaining.length - 1 && choice >= remaining[index]!.detail.priority) {
        choice -= remaining[index]!.detail.priority;
        index++;
      }
      ordered.push(remaining.splice(index, 1)[0]!);
    }
  } else {
    const start = Math.floor(random(actor) * ACTIVITIES.length);
    ordered = ACTIVITIES.map((_, index) =>
      candidates.find(
        (value) =>
          value.detail.behavior === ACTIVITIES[(start + index) % ACTIVITIES.length]!.behavior,
      )!,
    );
  }
  for (const candidate of ordered) {
    if (!candidate.detail.eligible) continue;
    const target = candidate.slots[Math.floor(random(actor) * candidate.slots.length)]!;
    traceDecision(
      sim,
      actor,
      'activity',
      candidate.detail.behavior,
      target,
      [
        actor.traits ? 'weighted-eligible-activity' : 'legacy-activity-order',
        'eligible-affordance',
        'clearance-verified',
      ],
      candidates.map((value) => value.detail),
    );
    if (beginActivity(sim, actor, target, candidate.detail.behavior)) return;
  }
  const destination = roamingPoint(sim, actor);
  if (!destination) {
    waitForSpace(sim, actor, 'activity');
    return;
  }
  const fallback = candidates.find((value) => value.detail.behavior === 'idle')!;
  fallback.detail.eligible = true;
  fallback.detail.priority = Math.max(1, fallback.detail.priority);
  fallback.detail.reasons = ['safe-ground-fallback', 'resource-yield'];
  traceDecision(
    sim,
    actor,
    'activity',
    'idle',
    undefined,
    ['safe-ground-fallback', 'resource-yield'],
    candidates.map((value) => value.detail),
  );
  actor.placement = 'placed';
  configureTravel(sim, actor, destination, true);
  if (actor.slotId) sim.occupancy.delete(actor.slotId);
  actor.slotId = null;
  actor.targetSlotId = null;
  actor.route = [destination];
  actor.nextBehavior = 'idle';
  transition(actor, 'moving', 0, 'yield-resource-to-safe-ground');
}

/** Phase is presentation input, never an observed behavior or owner-data mutation.
 * Intent is applied on fixed ticks; quiet/hidden renderers do not advance motion. */
export function setScenePhase(sim: Simulation, phase: ScenePhase = 'day') {
  if (phase === 'night' && sim.phase !== 'night') {
    cancelDecorativeVisit(sim);
    if (sim.arrival) finishArrival(sim, 'placed');
  }
  sim.phase = phase;
}

/** Same resolved scene clock as rendering. Updating input alone never moves an actor or consumes RNG. */
export function setSceneEnvironment(sim: Simulation, frame?: WeatherFrame | EnvironmentFrame) {
  sim.environment = resolveEnvironmentPolicy(frame, sim.environment);
  if (frame) sim.phase = frame.status === 'ready' ? frame.phase : 'day';
}

function releaseReservations(sim: Simulation, actor: Actor) {
  for (const [slot, owner] of sim.occupancy) if (owner === actor.id) sim.occupancy.delete(slot);
  actor.slotId = null;
  actor.targetSlotId = null;
  actor.route = [];
}

function chooseSleep(sim: Simulation, actor: Actor) {
  // Reuse the same arbitration map as daytime activity, including in-flight claims.
  const free = sim.scene.slots.filter(
    (slot) =>
      slotAvailable(sim, actor, slot) &&
      findRoute(sim.scene, actor.slotId, slot.id).length > 0 &&
      (!actor.traits || environmentSupports(sim, actor, slot, 'sleeping')),
  );
  const rank = (affordance: Affordance) =>
    affordance === 'roost' ? 0 : affordance === 'perch' ? 1 : 2;
  const target = free
    .filter(
      (slot) =>
        ['roost', 'perch', 'ground'].includes(slot.affordance) ||
        compatibleShelter(sim, actor, slot),
    )
    .sort(
      (a, b) =>
        Number(compatibleShelter(sim, actor, b)) - Number(compatibleShelter(sim, actor, a)) ||
        (actor.traits
          ? supportPriority(actor, b, true) - supportPriority(actor, a, true)
          : rank(a.affordance) - rank(b.affordance)) ||
        Math.hypot(a.x - actor.x, a.y - actor.y) - Math.hypot(b.x - actor.x, b.y - actor.y) ||
        a.id.localeCompare(b.id),
    )[0];
  // Crowded yards use clear ground; never spin forever waiting for a perch or occupy a bath/nest.
  const point =
    target ??
    (actor.behavior !== 'moving' && clearGround(sim, actor.x, actor.y, actor)
      ? { x: actor.x, y: actor.y }
      : roamingPoint(sim, actor));
  if (!point) {
    waitForSpace(sim, actor, 'night');
    return;
  }
  const environmentDecision = describeEnvironmentDecision(
    sim,
    actor,
    target && compatibleShelter(sim, actor, target) ? target : undefined,
  );
  if (environmentDecision) actor.environmentDecision = environmentDecision;
  else delete actor.environmentDecision;
  traceDecision(sim, actor, 'night', 'sleeping', target, [
    target ? 'night-roost-affinity' : 'night-safe-ground-fallback',
    'clearance-verified',
  ]);
  actor.placement = 'placed';
  const route = target ? findRoute(sim.scene, actor.slotId, target.id) : [point];
  releaseReservations(sim, actor);
  actor.nextBehavior = 'sleeping';
  actor.locomotion = 'flight';
  if (actor.decision)
    actor.decision.locomotion = { mode: 'flight', reason: 'night-support-flight' };
  if (target) sim.occupancy.set(target.id, actor.id);
  if (Math.hypot(point.x - actor.x, point.y - actor.y) < 0.01) {
    actor.slotId = target?.id ?? null;
    actor.lastActivity = 'sleeping';
    transition(actor, 'sleeping', 0);
  } else {
    actor.targetSlotId = target?.id ?? null;
    actor.route = route.map(({ x, y }) => ({ x, y }));
    transition(actor, 'moving', 0);
  }
}

function wake(sim: Simulation, actor: Actor) {
  traceDecision(
    sim,
    actor,
    'wake',
    'idle',
    sim.scene.slots.find((slot) => slot.id === actor.slotId),
    ['phase-wake'],
  );
  if (actor.behavior === 'moving') {
    // Dawn interrupts a sleep-bound flight without teleporting or leaking its destination.
    releaseReservations(sim, actor);
    actor.nextBehavior = 'idle';
    actor.lastActivity = 'sleeping';
    chooseActivity(sim, actor);
  } else {
    actor.nextBehavior = 'idle';
    actor.lastActivity = 'sleeping';
    restAtSlot(sim, actor);
  }
}

export const DECORATIVE_VISIT_LIMITS = {
  approach: 45,
  scatter: 150,
  return: 300,
  cooldown: 300,
} as const;

function safePresentationTarget(
  sim: Simulation,
  actor: Actor,
  preferredId?: string | null,
  far = false,
) {
  const preferred = preferredId
    ? sim.scene.slots.find((slot) => slot.id === preferredId)
    : undefined;
  if (
    preferred &&
    ['ground', 'perch', 'roost'].includes(preferred.affordance) &&
    !preferred.capability &&
    (!actor.traits || supportPriority(actor, preferred) > 0) &&
    slotAvailable(sim, actor, preferred)
  )
    return preferred;
  return sim.scene.slots
    .filter(
      (slot) =>
        ['ground', 'perch', 'roost'].includes(slot.affordance) &&
        !slot.capability &&
        (!actor.traits || supportPriority(actor, slot) > 0) &&
        slotAvailable(sim, actor, slot),
    )
    .sort(
      (a, b) =>
        (far ? -1 : 1) *
          (Math.hypot(a.x - actor.x, a.y - actor.y) - Math.hypot(b.x - actor.x, b.y - actor.y)) ||
        a.id.localeCompare(b.id),
    )[0];
}
function presentationFlight(sim: Simulation, actor: Actor, target?: SceneSlot) {
  releaseReservations(sim, actor);
  const point = target ?? roamingPoint(sim, actor);
  if (!point) {
    waitForSpace(sim, actor, 'decorative-visit');
    return;
  }
  actor.placement = 'placed';
  traceDecision(sim, actor, 'decorative-visit', 'idle', target, [
    'decorative-visit-response',
    'clearance-verified',
  ]);
  if (actor.decision)
    actor.decision.locomotion = { mode: 'flight', reason: 'decorative-visit-flight' };
  if (target) {
    actor.targetSlotId = target.id;
    sim.occupancy.set(target.id, actor.id);
  }
  actor.route = [{ x: point.x, y: point.y }];
  actor.locomotion = 'flight';
  actor.nextBehavior = 'idle';
  transition(actor, 'moving', 0);
}
function settlePresentationActor(sim: Simulation, actor: Actor) {
  const reserved = actor.targetSlotId
    ? sim.scene.slots.find((slot) => slot.id === actor.targetSlotId)
    : undefined;
  if (reserved && slotAvailable(sim, actor, reserved)) {
    actor.x = reserved.x;
    actor.y = reserved.y;
    actor.slotId = reserved.id;
    actor.targetSlotId = null;
    actor.route = [];
    restAtSlot(sim, actor);
  } else {
    releaseReservations(sim, actor);
    placeActor(sim, actor, actor.randomState % sim.scene.slots.length);
  }
}
/** A clearly labeled demonstration; never represents a sighting or changes owner data. */
export function triggerDecorativeVisit(sim: Simulation): 'started' | 'queued' | 'unavailable' {
  if (sim.phase === 'night' || sim.environment?.seekShelter || sim.arrival || !sim.actors.size)
    return 'unavailable';
  const visit = sim.decorativeVisit;
  if (visit.phase !== 'idle') {
    visit.pending = true;
    return 'queued';
  }
  visit.phase = 'approach';
  visit.ticks = 0;
  visit.sequence++;
  return 'started';
}
export function cancelDecorativeVisit(sim: Simulation) {
  const visit = sim.decorativeVisit;
  if (visit.phase === 'scatter' || visit.phase === 'return') {
    for (const id of visit.participants.keys()) {
      const actor = sim.actors.get(id);
      if (actor) releaseReservations(sim, actor);
    }
    for (const [id, home] of visit.participants) {
      const actor = sim.actors.get(id);
      if (!actor) continue;
      presentationFlight(sim, actor, safePresentationTarget(sim, actor, home.slotId));
      settlePresentationActor(sim, actor);
    }
  }
  visit.phase = 'idle';
  visit.ticks = 0;
  visit.pending = false;
  visit.participants.clear();
}
function advanceDecorativeVisit(sim: Simulation) {
  const visit = sim.decorativeVisit;
  if (visit.phase === 'idle') return;
  visit.ticks++;
  if (visit.phase === 'approach' && visit.ticks >= DECORATIVE_VISIT_LIMITS.approach) {
    visit.phase = 'scatter';
    visit.ticks = 0;
    for (const actor of sim.actors.values()) {
      if (actor.placement === 'waiting-for-space') continue;
      const slotId = actor.targetSlotId ?? actor.slotId;
      const slot = sim.scene.slots.find((value) => value.id === slotId);
      visit.participants.set(actor.id, {
        slotId,
        point: { x: slot?.x ?? actor.x, y: slot?.y ?? actor.y },
        delay: Math.round((1 - effectiveCaution(actor)) * 30),
      });
      releaseReservations(sim, actor);
    }
    for (const id of visit.participants.keys()) {
      const actor = sim.actors.get(id)!;
      presentationFlight(sim, actor, safePresentationTarget(sim, actor, undefined, true));
    }
  } else if (visit.phase === 'scatter' && visit.ticks >= DECORATIVE_VISIT_LIMITS.scatter) {
    visit.phase = 'return';
    visit.ticks = 0;
    for (const id of visit.participants.keys()) {
      const actor = sim.actors.get(id);
      if (actor) releaseReservations(sim, actor);
    }
    for (const [id, home] of visit.participants) {
      const actor = sim.actors.get(id);
      if (actor) presentationFlight(sim, actor, safePresentationTarget(sim, actor, home.slotId));
    }
  } else if (
    visit.phase === 'return' &&
    (visit.ticks >= DECORATIVE_VISIT_LIMITS.return ||
      [...visit.participants.keys()].every((id) => sim.actors.get(id)?.behavior !== 'moving'))
  ) {
    for (const id of visit.participants.keys()) {
      const actor = sim.actors.get(id);
      if (actor?.behavior === 'moving') settlePresentationActor(sim, actor);
    }
    visit.participants.clear();
    visit.phase = 'cooldown';
    visit.ticks = 0;
  } else if (visit.phase === 'cooldown' && visit.ticks >= DECORATIVE_VISIT_LIMITS.cooldown) {
    const pending = visit.pending;
    visit.pending = false;
    visit.phase = 'idle';
    visit.ticks = 0;
    if (pending) triggerDecorativeVisit(sim);
  }
}
function recordSettlement(sim: Simulation, value: ArrivalSettlement) {
  if (sim.settledArrivalTokens.includes(value.token)) return;
  sim.settledArrivalTokens.push(value.token);
  if (sim.settledArrivalTokens.length > 64) sim.settledArrivalTokens.shift();
  sim.arrivalSettlements.push(value);
}
function finishArrival(sim: Simulation, outcome: ArrivalSettlement['outcome']) {
  const arrival = sim.arrival;
  if (!arrival) return;
  const actor = sim.actors.get(arrival.birdId);
  if (actor?.behavior === 'moving') settlePresentationActor(sim, actor);
  sim.arrival = null;
  recordSettlement(sim, { token: arrival.token, outcome });
}
/** Only an absent authoritative actor may fly in; already-visible residents are never rewound. */
export function admitArrival(sim: Simulation, cue: ArrivalCue, bird: SceneBird, quiet = false) {
  cue = arrivalCueSchema.parse(cue);
  if (
    cue.birdId !== bird.id ||
    sim.settledArrivalTokens.includes(cue.token) ||
    sim.arrival?.token === cue.token
  )
    return;
  if (sim.arrival) finishArrival(sim, 'cancelled');
  cancelDecorativeVisit(sim);
  if (sim.actors.has(bird.id)) {
    recordSettlement(sim, { token: cue.token, outcome: 'placed' });
    return;
  }
  reconcileBirds(sim, [...sim.actors.values(), bird]);
  const actor = sim.actors.get(bird.id)!;
  if (
    quiet ||
    sim.phase === 'night' ||
    sim.environment?.seekShelter ||
    actor.placement === 'waiting-for-space'
  ) {
    recordSettlement(sim, { token: cue.token, outcome: 'placed' });
    return;
  }
  traceDecision(
    sim,
    actor,
    'arrival',
    'idle',
    sim.scene.slots.find((slot) => slot.id === actor.slotId),
    ['decorative-arrival'],
  );
  if (actor.decision)
    actor.decision.locomotion = { mode: 'flight', reason: 'decorative-arrival-flight' };
  const destination = { x: actor.x, y: actor.y },
    slotId = actor.slotId;
  actor.x = actor.randomState % 2 ? 0 : sim.scene.width;
  actor.y = Math.max(70, Math.min(150, destination.y - 140));
  actor.slotId = null;
  actor.targetSlotId = slotId;
  actor.route = [destination];
  actor.locomotion = 'flight';
  actor.nextBehavior = 'idle';
  transition(actor, 'moving', 0);
  sim.arrival = { token: cue.token, birdId: bird.id, ticks: 0 };
}
export function rejectArrivalCue(sim: Simulation, cue: ArrivalCue) {
  cue = arrivalCueSchema.parse(cue);
  recordSettlement(sim, { token: cue.token, outcome: 'cancelled' });
}
export function cancelArrival(sim: Simulation) {
  finishArrival(sim, 'cancelled');
}
export function takeArrivalSettlements(sim: Simulation) {
  return sim.arrivalSettlements.splice(0);
}

function step(sim: Simulation) {
  sim.ticks++;
  if (sim.environment?.seekShelter || sim.phase === 'night') {
    if (sim.decorativeVisit.phase !== 'idle') cancelDecorativeVisit(sim);
    if (sim.arrival) finishArrival(sim, 'placed');
  }
  advanceDecorativeVisit(sim);
  if (sim.arrival) {
    sim.arrival.ticks++;
    if (sim.arrival.ticks >= 360) finishArrival(sim, 'placed');
    else if (sim.actors.get(sim.arrival.birdId)?.behavior !== 'moving')
      finishArrival(sim, 'completed');
  }
  const environmentKey = sim.environment
    ? JSON.stringify([
        sim.phase,
        sim.environment.rain,
        sim.environment.snow,
        sim.environment.strongWind,
        sim.environment.fog,
      ])
    : '';
  for (const actor of sim.actors.values()) {
    if (actor.placement === 'waiting-for-space') {
      if (--actor.remainingTicks <= 0) placeActor(sim, actor, 0, 'activity');
      if (actor.placement === 'waiting-for-space') continue;
    }
    if ((actor.environmentKey ?? '') !== environmentKey) {
      actor.environmentKey = environmentKey;
      const decision = describeEnvironmentDecision(sim, actor);
      if (decision) actor.environmentDecision = decision;
      else delete actor.environmentDecision;
      if (sim.phase === 'night') chooseSleep(sim, actor);
      else {
        const support = sim.scene.slots.find(
          (slot) => slot.id === (actor.targetSlotId ?? actor.slotId),
        );
        const intended = actor.behavior === 'moving' ? actor.nextBehavior : actor.behavior;
        if (
          sim.environment?.seekShelter ||
          environmentPriority(sim, actor, intended) <= 0 ||
          (support?.shelter && !environmentSupports(sim, actor, support, intended))
        ) {
          // Weather redirects flight from its current point; it never teleports or creates capacity.
          releaseReservations(sim, actor);
          chooseActivity(sim, actor);
        }
      }
    }
    if (sim.phase === 'night') {
      if (
        actor.behavior !== 'sleeping' &&
        !(actor.behavior === 'moving' && actor.nextBehavior === 'sleeping')
      )
        chooseSleep(sim, actor);
    } else if (
      actor.behavior === 'sleeping' ||
      (actor.behavior === 'moving' && actor.nextBehavior === 'sleeping')
    ) {
      wake(sim, actor);
    }
    const visit = sim.decorativeVisit;
    const participant = visit.participants.get(actor.id);
    if (participant && (visit.phase === 'scatter' || visit.phase === 'return')) {
      if (
        actor.behavior !== 'moving' ||
        (visit.phase === 'scatter' && visit.ticks < participant.delay)
      )
        continue;
    }
    actor.behaviorTicks++;
    actor.frame = Math.floor(actor.behaviorTicks / (actor.behavior === 'moving' ? 4 : 9)) % 2;
    if (actor.behavior === 'moving') {
      if (isRoutine(actor.nextBehavior) && actor.behaviorTicks >= ROUTINE_TRAVEL_LIMIT) {
        // Repeated object moves cannot hold a routine reservation indefinitely.
        releaseReservations(sim, actor);
        actor.nextBehavior = 'idle';
        transition(actor, 'idle', 30);
        continue;
      }
      const next = actor.route[0];
      if (!next) {
        const destination = sim.scene.slots.find((slot) => slot.id === actor.targetSlotId);
        if (
          (destination &&
            (!slotAvailable(sim, actor, destination) ||
              (actor.traits &&
                !environmentSupports(sim, actor, destination, actor.nextBehavior) &&
                !['decorative-visit', 'arrival'].includes(actor.decision?.trigger ?? '')))) ||
          (!destination &&
            (actor.footprint || actor.profile) &&
            !clearGround(sim, actor.x, actor.y, actor))
        ) {
          releaseReservations(sim, actor);
          placeActor(sim, actor, 0, 'cancelled');
          continue;
        }
        if (
          isRoutine(actor.nextBehavior) &&
          !sim.scene.slots.some(
            (slot) =>
              slot.id === actor.targetSlotId &&
              slot.capability === ROUTINES[actor.nextBehavior as RoutineBehavior].capability,
          )
        ) {
          releaseReservations(sim, actor);
          actor.nextBehavior = 'idle';
          transition(actor, 'idle', 30);
          continue;
        }
        actor.slotId = actor.targetSlotId;
        actor.targetSlotId = null;
        actor.lastActivity = actor.nextBehavior;
        transition(
          actor,
          actor.nextBehavior,
          duration(actor, actor.nextBehavior),
          'arrived-at-selected-support',
        );
        continue;
      }
      const dx = next.x - actor.x,
        dy = next.y - actor.y;
      const distance = Math.hypot(dx, dy);
      const travel =
        (actor.traits?.locomotion.speed ?? actor.profile?.movement.speed ?? MOVE_SPEED) *
        (actor.locomotion === 'hop' ? 0.65 : 1) *
        FIXED_STEP_SECONDS;
      if (Math.abs(dx) > 0.01) actor.direction = dx < 0 ? -1 : 1;
      if (distance <= travel) {
        actor.x = next.x;
        actor.y = next.y;
        actor.route.shift();
      } else {
        actor.x += (dx / distance) * travel;
        actor.y += (dy / distance) * travel;
      }
    } else if (actor.behavior !== 'sleeping' && --actor.remainingTicks <= 0) {
      if (isRoutine(actor.behavior)) {
        releaseReservations(sim, actor);
        actor.nextBehavior = 'idle';
      }
      chooseActivity(sim, actor);
    }
  }
}

/** Fixed steps make behavior independent of display refresh rate. Hidden-tab backlog is discarded. */
export function advanceSimulation(sim: Simulation, elapsedSeconds: number) {
  if (!Number.isFinite(elapsedSeconds) || elapsedSeconds <= 0) return;
  sim.accumulator += Math.min(elapsedSeconds, 2);
  while (sim.accumulator + 1e-10 >= FIXED_STEP_SECONDS) {
    step(sim);
    sim.accumulator = Math.max(0, sim.accumulator - FIXED_STEP_SECONDS);
  }
}

/** Stable, serializable diagnostics; transient simulation state is never evidence of observed behavior. */
export function simulationSnapshot(sim: Simulation) {
  return {
    scene: sim.scene.id,
    options: { ...sim.options },
    decorativeVisit: {
      ...sim.decorativeVisit,
      participants: [...sim.decorativeVisit.participants],
    },
    arrival: sim.arrival ? { ...sim.arrival } : null,
    phase: sim.phase,
    ticks: sim.ticks,
    occupancy: [...sim.occupancy.entries()].sort(([a], [b]) => a.localeCompare(b)),
    routineTurns: {
      playing: [...sim.routineTurns.playing],
      nesting: [...sim.routineTurns.nesting],
    },
    actors: [...sim.actors.values()].map((actor) => ({
      ...actor,
      route: actor.route.map((p) => ({ ...p })),
    })),
  };
}
