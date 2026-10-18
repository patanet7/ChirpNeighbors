import { animationStates, type SpeciesManifestV2 } from './manifest-v2.ts';
import type { AnimationClipsV3 } from './manifest-v3.ts';

/** Mechanical edge differences only. Zero differences do not prove a natural loop. */
export function measureLoopEdges(
  canvas: Pick<SpeciesManifestV2['canvas'], 'width' | 'height'>,
  frames: SpeciesManifestV2['frames'],
  clips: AnimationClipsV3,
) {
  const cache = new Map<number, Uint32Array>();
  function pixels(index: number) {
    const cached = cache.get(index);
    if (cached) return cached;
    const frame = frames[index];
    if (!frame) throw new Error('Loop metric references an absent frame.');
    const output = new Uint32Array(canvas.width * canvas.height);
    for (const rect of frame)
      for (let y = rect.y; y < Math.min(canvas.height, rect.y + rect.height); y++)
        for (let x = rect.x; x < Math.min(canvas.width, rect.x + rect.width); x++)
          output[y * canvas.width + x] = rect.color + 1;
    cache.set(index, output);
    return output;
  }
  return animationStates.flatMap((action) => {
    const clip = clips[action];
    if (!clip?.loop) return [];
    const first = clip.poses[0],
      last = clip.poses.at(-1);
    if (!first || !last) throw new Error('Loop metric requires a pose.');
    const left = pixels(first.frame),
      right = pixels(last.frame);
    let changedPixels = 0;
    for (let index = 0; index < left.length; index++)
      if (left[index] !== right[index]) changedPixels++;
    const contacts = (pose: typeof first) =>
      JSON.stringify(
        [...pose.contacts].sort((a, b) => (a.kind < b.kind ? -1 : a.kind > b.kind ? 1 : 0)),
      );
    return [
      {
        action,
        comparedPixels: left.length,
        changedPixels,
        pivotDistance: Math.hypot(first.pivot.x - last.pivot.x, first.pivot.y - last.pivot.y),
        contactLayoutChanged: contacts(first) !== contacts(last),
      },
    ];
  });
}
