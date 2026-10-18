import { z } from 'zod';
import {
  animationStates,
  speciesManifestV2Schema,
  type AnimationState,
  type SpeciesManifestV2,
} from './manifest-v2.ts';
import { speciesManifestV3Schema, type SpeciesManifestV3 } from './manifest-v3.ts';
import { speciesManifestV4Schema, type SpeciesManifestV4 } from './manifest-v4.ts';
export { speciesManifestV4Schema, type SpeciesManifestV4 } from './manifest-v4.ts';
import { speciesManifestV5Schema, type SpeciesManifestV5 } from './manifest-v5.ts';
import { speciesManifestV6Schema, type SpeciesManifestV6 } from './manifest-v6.ts';
import { commonClipNames } from './common-motion.ts';
import type { AnimationClipsV3 } from './manifest-v3.ts';
export { speciesManifestV6Schema, type SpeciesManifestV6 } from './manifest-v6.ts';
export { speciesManifestV5Schema, type SpeciesManifestV5 } from './manifest-v5.ts';
export * from './manifest-v2.ts';
export { speciesManifestV3Schema, type SpeciesManifestV3 } from './manifest-v3.ts';
export const speciesManifestSchema = z.union([
  speciesManifestV2Schema,
  speciesManifestV3Schema,
  speciesManifestV4Schema,
  speciesManifestV5Schema,
  speciesManifestV6Schema,
]);
export type SpeciesManifest =
  SpeciesManifestV2 | SpeciesManifestV3 | SpeciesManifestV4 | SpeciesManifestV5 | SpeciesManifestV6;

function samplePose(
  manifest: SpeciesManifest,
  clip: { loop: boolean; poses: readonly AnimationClipsV3['idle']['poses'][number][] },
  elapsed: number,
  state: AnimationState,
  fallback: boolean,
) {
  const duration = clip.poses.reduce((sum, pose) => sum + pose.durationTicks, 0);
  let remaining = clip.loop ? elapsed % duration : Math.min(elapsed, duration - 1),
    selected = clip.poses.at(-1)!;
  for (const pose of clip.poses) {
    if (remaining < pose.durationTicks) {
      selected = pose;
      break;
    }
    remaining -= pose.durationTicks;
  }
  return {
    frame: selected.frame,
    rectangles: manifest.frames[selected.frame]!,
    rotation: selected.rotation,
    state,
    fallback,
    pivot: selected.pivot,
    contacts: selected.contacts,
    poseId: selected.poseId,
    durationTicks: selected.durationTicks,
  };
}

/** Geometry can reuse a frame with a different pose pivot. */
export function sampledGeometryKey(assetKey: string, sample: ReturnType<typeof sampleClip>) {
  return JSON.stringify([assetKey, sample.frame, sample.pivot.x, sample.pivot.y]);
}

/** Unknown/missing behaviors resolve directly to idle; no fallback chains or cycles. */
export function sampleClip(
  manifest: SpeciesManifest,
  behavior: string,
  ticks: number,
  reducedMotion = false,
) {
  const elapsedTicks =
    reducedMotion || !Number.isFinite(ticks) ? 0 : Math.max(0, Math.floor(ticks));
  if (
    manifest.schemaVersion === 6 &&
    (behavior === 'idle' || commonClipNames.includes(behavior as 'blink' | 'look'))
  ) {
    let name = behavior as 'idle' | 'blink' | 'look',
      local = elapsedTicks;
    if (name === 'idle') {
      const duration = (id: 'idle' | 'blink' | 'look') =>
        (id === 'idle' ? manifest.clips.idle : manifest.commonMotion.clips[id]).poses.reduce(
          (sum, p) => sum + p.durationTicks,
          0,
        );
      local %= manifest.commonMotion.idleSequence.reduce((sum, id) => sum + duration(id), 0);
      for (const id of manifest.commonMotion.idleSequence) {
        if (local < duration(id)) {
          name = id;
          break;
        }
        local -= duration(id);
      }
    }
    if (name !== 'idle')
      return {
        ...samplePose(manifest, manifest.commonMotion.clips[name], local, 'idle', false),
        commonClip: name,
      };
    return samplePose(manifest, manifest.clips.idle, local, 'idle', false);
  }
  const state = animationStates.includes(behavior as AnimationState)
    ? (behavior as AnimationState)
    : 'idle';
  const resolved = manifest.clips[state] ? state : 'idle';
  // Unsupported routines use a still pose; a generic idle loop must not imply authored activity.
  const stillFallback =
    ['sleeping', 'playing', 'nesting'].includes(behavior) && resolved === 'idle';
  const elapsed =
    reducedMotion || stillFallback || !Number.isFinite(ticks) ? 0 : Math.max(0, Math.floor(ticks));
  if (manifest.schemaVersion !== 2) {
    const clip = manifest.clips[resolved]!;
    return samplePose(manifest, clip, elapsed, resolved, state !== behavior || resolved !== state);
  }
  const clip = manifest.clips[resolved]!;
  const step = Math.floor(elapsed / clip.ticksPerFrame);
  const pose = clip.loop ? step % clip.frames.length : Math.min(step, clip.frames.length - 1);
  const frame = clip.frames[pose]!;
  return {
    frame,
    rectangles: manifest.frames[frame]!,
    rotation: clip.rotations?.[pose] ?? 0,
    state: resolved,
    fallback: state !== behavior || resolved !== state,
    pivot: { x: manifest.canvas.anchorX, y: manifest.canvas.anchorY },
    contacts: [],
    poseId: null,
    durationTicks: clip.ticksPerFrame,
  };
}
