import {
  cancelPreviewSurfaceActivity,
  holdPreviewSurfaceActivity,
  requestPreviewSurfaceActivity,
  setPreviewSurfaceAdmission,
} from './simulation';
import type { Simulation, SceneSlot, Actor } from './types';

/** Synthetic product tuning, not a measurement of bird physiology. All quantities are SI. */
export const SURFACE_INTERACTION_TUNING = Object.freeze({
  wetEnterDepthM: 0.001,
  wetLeaveDepthM: 0.0005,
  drinkingVolumeM3: 0.0000005,
  drinkingRateM3PerSecond: 0.00000025,
  bathingSeconds: 3,
});
export type LocalSurfaceAction = 'drink' | 'bath';
export type SurfaceInteractionState =
  | 'idle'
  | 'seeking'
  | 'drinking'
  | 'bathing'
  | 'complete'
  | 'cancelled'
  | 'blocked-dry'
  | 'blocked-environment'
  | 'occupied'
  | 'stale-object'
  | 'unavailable';
export interface SurfaceInteractionInput {
  objectId: string | null;
  generation: number;
  revision: number;
  waterVolumeM3: number;
  waterDepthM: number;
}
export interface SurfaceWithdrawal {
  id: string;
  sequence: number;
  storeId: 'bath';
  volumeM3: number;
  reason: 'drinking';
  actorId: string;
  objectId: string;
  generation: number;
  revision: number;
}
export interface SurfaceContact {
  actorId: string;
  slotId: string;
  kind: LocalSurfaceAction;
  objectId: string;
  generation: number;
  revision: number;
  x: number;
  y: number;
}
export interface SurfaceInteractionStatus {
  state: SurfaceInteractionState;
  action: LocalSurfaceAction | null;
  actorId: string | null;
  objectId: string | null;
  generation: number;
  revision: number;
  slotId: string | null;
  wet: boolean;
  elapsedSeconds: number;
  drinkingVolumeM3: number;
  animationClip: 'idle-fallback' | 'bathing';
  clipNote: string;
}
export interface SurfaceInteractionController {
  readonly sim: Simulation;
  status: SurfaceInteractionStatus;
  surface: SurfaceInteractionInput | null;
  geometry: string;
  sequence: number;
  pending: SurfaceWithdrawal | null;
  active: boolean;
}
export interface SurfaceInteractionStep {
  status: SurfaceInteractionStatus;
  withdrawals: SurfaceWithdrawal[];
  contacts: SurfaceContact[];
}

const selectedActors = new WeakMap<SurfaceInteractionController, string | null>();
const episodes = new WeakMap<SurfaceInteractionController, object>();
const issuedWithdrawals = new WeakMap<
  SurfaceWithdrawal,
  {
    controller: SurfaceInteractionController;
    episode: object;
    contact: SurfaceContact;
  }
>();
const issuedContacts = new WeakMap<
  SurfaceContact,
  {
    controller: SurfaceInteractionController;
    episode: object;
    actor: Actor;
    slot: SceneSlot;
    object: Simulation['scene']['objects'][number];
    geometry: string;
  }
>();

/** Explicit actor selection is local and opt-in. Omitting it preserves the first-Robin policy. */
export function createSurfaceInteractions(
  sim: Simulation,
  options: { actorId?: string } = {},
): SurfaceInteractionController {
  if (
    options.actorId !== undefined &&
    (typeof options.actorId !== 'string' || !options.actorId.length || options.actorId.length > 128)
  )
    throw new RangeError('An explicit surface actor ID must be a nonempty bounded string.');
  const controller: SurfaceInteractionController = {
    sim,
    surface: null,
    geometry: '',
    sequence: 0,
    pending: null,
    active: false,
    status: {
      state: 'unavailable',
      action: null,
      actorId: null,
      objectId: null,
      generation: 0,
      revision: 0,
      slotId: null,
      wet: false,
      elapsedSeconds: 0,
      drinkingVolumeM3: 0,
      animationClip: 'idle-fallback',
      clipNote: 'Dedicated drinking clip is unavailable; the existing idle clip is used.',
    },
  };
  selectedActors.set(controller, options.actorId ?? null);
  episodes.set(controller, Object.freeze({}));
  return controller;
}
function slots(controller: SurfaceInteractionController): SceneSlot[] {
  return controller.sim.scene.slots.filter(
    (slot) => slot.affordance === 'bath' && slot.objectId === controller.status.objectId,
  );
}
function stop(controller: SurfaceInteractionController, state: SurfaceInteractionState) {
  if (controller.active && controller.status.actorId)
    cancelPreviewSurfaceActivity(controller.sim, controller.status.actorId);
  controller.active = false;
  episodes.set(controller, Object.freeze({}));
  controller.pending = null;
  controller.status.state = state;
  controller.status.slotId = null;
}
export function cancelSurfaceInteraction(controller: SurfaceInteractionController) {
  stop(controller, 'cancelled');
  return { ...controller.status };
}
function environmentBlocked(controller: SurfaceInteractionController) {
  return controller.sim.phase === 'night' || !!controller.sim.environment?.seekShelter;
}

export function requestSurfaceInteraction(
  controller: SurfaceInteractionController,
  action: LocalSurfaceAction,
): SurfaceInteractionStatus {
  if (controller.active) stop(controller, 'cancelled');
  const status = controller.status;
  status.action = action;
  status.elapsedSeconds = 0;
  status.drinkingVolumeM3 = 0;
  status.animationClip = action === 'drink' ? 'idle-fallback' : 'bathing';
  status.clipNote =
    action === 'drink'
      ? 'Dedicated drinking clip is unavailable; the existing idle clip is used.'
      : 'Existing bathing clip; contact ripples are cosmetic and withdraw no water.';
  if (!status.actorId || !status.objectId || !controller.surface) status.state = 'unavailable';
  else if (!status.wet) status.state = 'blocked-dry';
  else if (environmentBlocked(controller)) status.state = 'blocked-environment';
  else {
    const actor = controller.sim.actors.get(status.actorId);
    const ordered = slots(controller).sort(
      (a, b) =>
        Math.hypot(a.x - (actor?.x ?? 0), a.y - (actor?.y ?? 0)) -
          Math.hypot(b.x - (actor?.x ?? 0), b.y - (actor?.y ?? 0)) || a.id.localeCompare(b.id),
    );
    status.state = 'occupied';
    for (const slot of ordered) {
      const result = requestPreviewSurfaceActivity(
        controller.sim,
        {
          actorId: status.actorId,
          objectId: status.objectId,
          generation: status.generation,
          revision: status.revision,
        },
        slot.id,
      );
      if (result === 'started') {
        status.state = 'seeking';
        status.slotId = slot.id;
        controller.active = true;
        break;
      }
      if (result !== 'occupied') status.state = result;
    }
  }
  return { ...status };
}

/** Run on the shared physical clock; dt=0 validates contact without advancing action time. */
export function updateSurfaceInteractions(
  controller: SurfaceInteractionController,
  input: SurfaceInteractionInput,
  dtSeconds: number,
): SurfaceInteractionStep {
  const status = controller.status;
  const selected = selectedActors.get(controller);
  const actor = selected
    ? controller.sim.actors.get(selected)
    : [...controller.sim.actors.values()].find(
        (value) => value.speciesId === 'cn-species-erithacus-rubecula',
      );
  const object = controller.sim.scene.objects.find(
    (value) => value.id === input.objectId && value.kind === 'bath',
  );
  const geometry = object ? `${object.id}:${object.x}:${object.y}` : '';
  const changed =
    controller.surface !== null &&
    (status.actorId !== (actor?.id ?? null) ||
      status.objectId !== (object?.id ?? null) ||
      status.generation !== input.generation ||
      status.revision !== input.revision ||
      controller.geometry !== geometry);
  if (changed) stop(controller, 'stale-object');
  if (changed) status.wet = false;
  status.actorId = actor?.id ?? null;
  status.objectId = object?.id ?? null;
  status.generation = input.generation;
  status.revision = input.revision;
  controller.surface = { ...input };
  controller.geometry = geometry;
  const valid =
    [input.waterVolumeM3, input.waterDepthM, input.generation, input.revision].every(
      Number.isFinite,
    ) &&
    input.waterVolumeM3 >= 0 &&
    input.waterDepthM >= 0 &&
    Number.isSafeInteger(input.generation) &&
    input.generation >= 0 &&
    Number.isSafeInteger(input.revision) &&
    input.revision >= 0;
  status.wet =
    valid &&
    !!object &&
    input.waterVolumeM3 > 0 &&
    (status.wet
      ? input.waterDepthM > SURFACE_INTERACTION_TUNING.wetLeaveDepthM
      : input.waterDepthM >= SURFACE_INTERACTION_TUNING.wetEnterDepthM);
  if (actor)
    setPreviewSurfaceAdmission(controller.sim, {
      actorId: actor.id,
      objectId: object?.id ?? '',
      generation: input.generation,
      revision: input.revision,
      wet: status.wet,
    });
  else setPreviewSurfaceAdmission(controller.sim, null);
  const support = slots(controller).find(
    (slot) => slot.id === (actor?.targetSlotId ?? actor?.slotId),
  );
  if (!actor || !object || !valid) stop(controller, 'unavailable');
  else if (!status.wet) {
    if (!controller.active && support) cancelPreviewSurfaceActivity(controller.sim, actor.id);
    stop(controller, 'blocked-dry');
  } else if (environmentBlocked(controller)) stop(controller, 'blocked-environment');
  else if (
    !controller.active &&
    !changed &&
    ['unavailable', 'blocked-dry', 'blocked-environment'].includes(status.state)
  )
    status.state = 'idle';
  else if (!controller.active && !changed && actor.behavior === 'bathing' && support) {
    // Wet-only autonomous bathing still uses the actor's existing claim, never a fake actor.
    status.action = 'bath';
    status.state = 'seeking';
    status.slotId = support.id;
    status.elapsedSeconds = 0;
    status.drinkingVolumeM3 = 0;
    status.animationClip = 'bathing';
    status.clipNote = 'Existing bathing clip; cosmetic contact withdraws no water.';
    controller.active = true;
  }
  const withdrawals: SurfaceWithdrawal[] = [];
  const contacts: SurfaceContact[] = [];
  if (controller.active && actor && object && status.action && status.slotId) {
    const slot = slots(controller).find((value) => value.id === status.slotId);
    const claimed = controller.sim.occupancy.get(status.slotId) === actor.id;
    if (!slot || !claimed || (actor.slotId !== slot.id && actor.targetSlotId !== slot.id))
      stop(controller, 'occupied');
    else if (
      actor.slotId === slot.id &&
      !actor.targetSlotId &&
      Math.hypot(actor.x - slot.x, actor.y - slot.y) <= 1
    ) {
      if (!holdPreviewSurfaceActivity(controller.sim, actor.id, status.action))
        stop(controller, 'blocked-environment');
      else {
        status.state = status.action === 'drink' ? 'drinking' : 'bathing';
        const dt = Number.isFinite(dtSeconds) ? Math.max(0, Math.min(0.05, dtSeconds)) : 0;
        status.elapsedSeconds += dt;
        const contact: SurfaceContact = Object.freeze({
          actorId: actor.id,
          slotId: slot.id,
          kind: status.action,
          objectId: object.id,
          generation: status.generation,
          revision: status.revision,
          x: slot.x,
          y: slot.y,
        });
        issuedContacts.set(contact, {
          controller,
          episode: episodes.get(controller)!,
          actor,
          slot,
          object,
          geometry: controller.geometry,
        });
        contacts.push(contact);
        if (status.action === 'drink' && !controller.pending && dt > 0) {
          const volumeM3 = Math.min(
            input.waterVolumeM3,
            SURFACE_INTERACTION_TUNING.drinkingVolumeM3 - status.drinkingVolumeM3,
            SURFACE_INTERACTION_TUNING.drinkingRateM3PerSecond * dt,
          );
          if (volumeM3 > 1e-15 && Number.isSafeInteger(controller.sequence + 1)) {
            controller.pending = {
              id: `surface-drink-${++controller.sequence}`,
              sequence: controller.sequence,
              storeId: 'bath',
              volumeM3,
              reason: 'drinking',
              actorId: actor.id,
              objectId: object.id,
              generation: status.generation,
              revision: status.revision,
            };
            const request = Object.freeze({ ...controller.pending });
            issuedWithdrawals.set(request, {
              controller,
              episode: episodes.get(controller)!,
              contact,
            });
            withdrawals.push(request);
          }
        }
        if (
          status.action === 'bath' &&
          status.elapsedSeconds >= SURFACE_INTERACTION_TUNING.bathingSeconds
        )
          stop(controller, 'complete');
      }
    } else status.state = 'seeking';
  }
  return { status: { ...status }, withdrawals, contacts: controller.active ? contacts : [] };
}

/** A matching finite core receipt is the only authority for consumed water. Never debit locally. */
export function applySurfaceWithdrawal(
  controller: SurfaceInteractionController,
  receipt: { id: string; actualVolumeM3: number },
): boolean {
  const pending = controller.pending;
  if (
    !controller.active ||
    controller.status.action !== 'drink' ||
    !pending ||
    pending.objectId !== controller.status.objectId ||
    pending.generation !== controller.status.generation ||
    pending.revision !== controller.status.revision ||
    pending.id !== receipt.id ||
    !Number.isFinite(receipt.actualVolumeM3) ||
    receipt.actualVolumeM3 < 0 ||
    receipt.actualVolumeM3 > pending.volumeM3
  )
    return false;
  controller.pending = null;
  controller.status.drinkingVolumeM3 += receipt.actualVolumeM3;
  if (controller.status.drinkingVolumeM3 >= SURFACE_INTERACTION_TUNING.drinkingVolumeM3 - 1e-15)
    stop(controller, 'complete');
  else if (receipt.actualVolumeM3 === 0) stop(controller, 'blocked-dry');
  return true;
}
export function disposeSurfaceInteractions(controller: SurfaceInteractionController) {
  stop(controller, 'cancelled');
  setPreviewSurfaceAdmission(controller.sim, null);
}

/** Opaque local episode identity, available only for an issued, still-current occupied contact.
 * A structurally identical clone is not an issued contact. No saved/wire authority is introduced. */
export function currentSurfaceContactEpisode(
  sim: Simulation,
  contact: SurfaceContact,
): object | null {
  const issued = issuedContacts.get(contact);
  if (!issued || !issued.episode || issued.controller.sim !== sim) return null;
  const { controller, actor, slot, object, episode } = issued;
  const status = controller.status;
  if (
    !controller.active ||
    episodes.get(controller) !== episode ||
    sim.actors.get(contact.actorId) !== actor ||
    !sim.scene.objects.includes(object) ||
    !sim.scene.slots.includes(slot) ||
    object.kind !== 'bath' ||
    object.id !== contact.objectId ||
    issued.geometry !== `${object.id}:${object.x}:${object.y}` ||
    status.actorId !== contact.actorId ||
    status.objectId !== contact.objectId ||
    status.generation !== contact.generation ||
    status.revision !== contact.revision ||
    !status.wet ||
    status.action !== contact.kind ||
    status.slotId !== contact.slotId ||
    slot.objectId !== object.id ||
    slot.affordance !== 'bath' ||
    sim.occupancy.get(slot.id) !== actor.id ||
    actor.slotId !== slot.id ||
    actor.targetSlotId !== null ||
    actor.route.length !== 0 ||
    actor.placement !== 'placed' ||
    actor.behavior !== (contact.kind === 'bath' ? 'bathing' : 'idle') ||
    ![actor.x, actor.y, slot.x, slot.y, contact.x, contact.y].every(Number.isFinite) ||
    contact.x !== slot.x ||
    contact.y !== slot.y ||
    Math.hypot(actor.x - slot.x, actor.y - slot.y) > 1 ||
    sim.phase === 'night' ||
    sim.environment?.seekShelter
  )
    return null;
  return episode;
}
export function isCurrentSurfaceContact(sim: Simulation, contact: SurfaceContact): boolean {
  return currentSurfaceContactEpisode(sim, contact) !== null;
}

/** A pending original request from this live controller only; copies and acknowledged requests fail. */
export function isCurrentSurfaceWithdrawal(sim: Simulation, request: SurfaceWithdrawal): boolean {
  const issued = issuedWithdrawals.get(request);
  if (!issued || !issued.episode || issued.controller.sim !== sim) return false;
  const c = issued.controller,
    p = c.pending,
    s = c.status;
  return (
    c.active &&
    currentSurfaceContactEpisode(sim, issued.contact) === issued.episode &&
    episodes.get(c) === issued.episode &&
    s.action === 'drink' &&
    s.state === 'drinking' &&
    !!p &&
    p.id === request.id &&
    p.sequence === request.sequence &&
    p.volumeM3 === request.volumeM3 &&
    p.actorId === request.actorId &&
    p.objectId === request.objectId &&
    p.generation === request.generation &&
    p.revision === request.revision &&
    s.actorId === request.actorId &&
    s.objectId === request.objectId &&
    s.generation === request.generation &&
    s.revision === request.revision
  );
}
