import { z } from 'zod';
import { animationPoseSchema } from './manifest-v3.ts';
const id = z
  .string()
  .min(1)
  .max(160)
  .regex(/^[a-zA-Z0-9][a-zA-Z0-9._:@-]*$/);
export const commonClipNames = ['blink', 'look'] as const;
const clipName = z.enum(commonClipNames);
const pose = animationPoseSchema
  .extend({ contacts: z.array(z.never()).length(0), rotation: z.literal(0) })
  .strict();
const clip = z
  .object({ name: clipName, loop: z.boolean(), poses: z.array(pose).min(1).max(32) })
  .strict();
/** Named idle presentation is separate from behavioral activities and physical contacts. */
export const commonMotionSchema = z
  .object({
    schemaVersion: z.literal(1),
    geometryScope: z.literal('image-registration-only'),
    physicalSupportReviewed: z.literal(false),
    idleSequence: z
      .array(z.enum(['idle', 'blink', 'look']))
      .min(3)
      .max(8),
    clips: z.object({ blink: clip, look: clip }).strict(),
    poseGraph: z
      .object({
        nodes: z
          .array(
            z
              .object({
                id,
                frame: z.number().int().min(0).max(63),
                clip: clipName,
                referenceId: id,
              })
              .strict(),
          )
          .min(2)
          .max(64),
        edges: z
          .array(z.object({ from: id, to: id }).strict())
          .min(1)
          .max(128),
      })
      .strict(),
  })
  .strict();
export type CommonMotion = z.infer<typeof commonMotionSchema>;
export function commonMotionIssues(
  value: CommonMotion,
  frameCount: number,
  width: number,
  height: number,
  references: readonly { id: string; roles: readonly string[] }[],
  pivot: { x: number; y: number },
  neutralFrame: number,
): string[] {
  const issues: string[] = [];
  if (
    !['idle', 'blink', 'look'].every((name) =>
      value.idleSequence.includes(name as 'idle' | 'blink' | 'look'),
    )
  )
    issues.push('Common idle sequence must explicitly include neutral, blink and look.');
  const nodes = new Map(value.poseGraph.nodes.map((n) => [n.id, n]));
  if (nodes.size !== value.poseGraph.nodes.length) issues.push('Common pose IDs must be unique.');
  const edgeKey = (a: string, b: string) => JSON.stringify([a, b]);
  const declared = new Set(value.poseGraph.edges.map((e) => edgeKey(e.from, e.to))),
    used = new Set<string>(),
    edges = new Set<string>();
  if (
    declared.size !== value.poseGraph.edges.length ||
    value.poseGraph.edges.some((e) => !nodes.has(e.from) || !nodes.has(e.to))
  )
    issues.push('Common edges must be unique and refer to existing nodes.');
  for (const name of commonClipNames) {
    const clip = value.clips[name];
    if (clip.name !== name) issues.push('Common clip name must match its registered key.');
    const first = clip.poses[0]!,
      last = clip.poses.at(-1)!;
    if (first.frame !== neutralFrame || last.frame !== neutralFrame)
      issues.push('Common clips must start and finish on the exact neutral frame.');
    if (
      clip.loop &&
      (first.frame !== last.frame ||
        first.pivot.x !== last.pivot.x ||
        first.pivot.y !== last.pivot.y)
    )
      issues.push('A common loop must return to its exact neutral image registration.');
    for (const [i, p] of clip.poses.entries()) {
      const node = nodes.get(p.poseId);
      used.add(p.poseId);
      if (
        !node ||
        node.clip !== name ||
        node.frame !== p.frame ||
        !references.some((r) => r.id === node.referenceId && r.roles.includes('pose'))
      )
        issues.push('Common pose frame, named clip and reviewed reference must match its graph.');
      if (
        p.frame >= frameCount ||
        p.pivot.x > width ||
        p.pivot.y > height ||
        p.pivot.x !== pivot.x ||
        p.pivot.y !== pivot.y
      )
        issues.push('Common pose must retain the neutral in-bounds image registration.');
      const next = clip.poses[i + 1] ?? (clip.loop ? first : undefined);
      if (next) edges.add(edgeKey(p.poseId, next.poseId));
    }
  }
  if (
    used.size !== nodes.size ||
    edges.size !== declared.size ||
    [...edges].some((e) => !declared.has(e))
  )
    issues.push('Common graph must exactly describe all named clip transitions.');
  return issues;
}
