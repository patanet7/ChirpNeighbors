import { z } from 'zod';
import { animationPinSchema, type AnimationPin } from './manifest-v2.ts';

const coordinate = z.number().int().min(0).max(256);
const point = z.object({ x: coordinate, y: coordinate }).strict();
const id = z
  .string()
  .min(1)
  .max(160)
  .regex(/^[a-zA-Z0-9][a-zA-Z0-9._:@-]*$/);
export const physicalFootprintSchema = z
  .object({
    left: z.number().int().min(0).max(128),
    right: z.number().int().min(0).max(128),
    back: z.number().int().min(0).max(64),
    front: z.number().int().min(0).max(64),
  })
  .strict()
  .refine(
    (value) => value.left + value.right > 0 && value.back + value.front > 0,
    'Physical footprint must have positive width and depth.',
  );
export const visualBoundsSchema = z
  .object({
    x: coordinate,
    y: coordinate,
    width: z.number().int().min(1).max(256),
    height: z.number().int().min(1).max(256),
  })
  .strict();
export const shapePoseSchema = z
  .object({
    poseId: id,
    frame: z.number().int().min(0).max(63),
    visualBounds: visualBoundsSchema,
    support: point,
    footprint: physicalFootprintSchema,
    landmarks: z
      .array(
        point
          .extend({ kind: z.enum(['head', 'body', 'beak', 'tail', 'left-foot', 'right-foot']) })
          .strict(),
      )
      .max(6),
  })
  .strict();
/** Reviewed geometry only: pixel silhouette is always measured from the actual frame rectangles.
 * Model/reference provenance remains on the enclosing immutable source/manifest, never inferred here. */
export const shapeReviewSchema = z
  .object({
    schemaVersion: z.literal(1),
    basedOn: animationPinSchema,
    speciesId: id,
    masterPoseId: id,
    poses: z.array(shapePoseSchema).min(1).max(576),
  })
  .strict()
  .superRefine((value, context) => {
    if (new Set(value.poses.map((pose) => pose.poseId)).size !== value.poses.length)
      context.addIssue({ code: 'custom', message: 'Shape pose IDs must be unique.' });
    if (!value.poses.some((pose) => pose.poseId === value.masterPoseId))
      context.addIssue({ code: 'custom', message: 'Master pose must identify an annotated pose.' });
    if (
      value.poses.some(
        (pose) => new Set(pose.landmarks.map((point) => point.kind)).size !== pose.landmarks.length,
      )
    )
      context.addIssue({ code: 'custom', message: 'Landmark kinds must be distinct per pose.' });
  });
export type ShapeReview = z.infer<typeof shapeReviewSchema>;
export type ShapePose = z.infer<typeof shapePoseSchema>;
export type PhysicalFootprint = z.infer<typeof physicalFootprintSchema>;
export interface Point {
  x: number;
  y: number;
}
export interface PixelRectangle extends Point {
  width: number;
  height: number;
  color: number;
}
export interface ShapeManifest {
  speciesId: string;
  canvas: { width: number; height: number };
  frames: PixelRectangle[][];
  clips: Record<string, { poses: { poseId: string; frame: number; pivot: Point }[] } | undefined>;
}
export function opaqueBounds(rectangles: readonly PixelRectangle[]) {
  if (!rectangles.length) return null;
  const x = Math.min(...rectangles.map((rect) => rect.x));
  const y = Math.min(...rectangles.map((rect) => rect.y));
  return {
    x,
    y,
    width: Math.max(...rectangles.map((rect) => rect.x + rect.width)) - x,
    height: Math.max(...rectangles.map((rect) => rect.y + rect.height)) - y,
  };
}
/** Called at both source admission and manifest load, after their bounded pixel validation. */
export function shapeReviewIssues(manifest: ShapeManifest, shape: ShapeReview): string[] {
  const issues: string[] = [];
  const poses = [
    ...new Map(
      Object.values(manifest.clips)
        .flatMap((clip) => clip?.poses ?? [])
        .map((pose) => [pose.poseId, pose]),
    ).values(),
  ];
  const occurrences = Object.values(manifest.clips).flatMap((clip) => clip?.poses ?? []);
  if (
    occurrences.some((pose) =>
      poses.some((unique) => unique.poseId === pose.poseId && unique.frame !== pose.frame),
    )
  )
    issues.push('Repeated pose identities must retain the same frame.');
  if (shape.speciesId !== manifest.speciesId) issues.push('Shape species differs from its pixels.');
  if (
    poses.length !== shape.poses.length ||
    poses.some(
      (pose) =>
        !shape.poses.some((entry) => entry.poseId === pose.poseId && entry.frame === pose.frame),
    )
  )
    issues.push('Shape annotations must bind every exact authored pose and frame.');
  for (const pose of shape.poses) {
    const bounds = opaqueBounds(manifest.frames[pose.frame] ?? []);
    if (
      !bounds ||
      (['x', 'y', 'width', 'height'] as const).some((key) => bounds[key] !== pose.visualBounds[key])
    )
      issues.push(`Shape visual bounds do not match opaque frame: ${pose.poseId}.`);
    const points = [pose.support, ...pose.landmarks];
    if (points.some((point) => point.x > manifest.canvas.width || point.y > manifest.canvas.height))
      issues.push(`Shape point exceeds canvas: ${pose.poseId}.`);
    if (
      bounds &&
      (pose.support.x < bounds.x ||
        pose.support.x > bounds.x + bounds.width ||
        pose.support.y < bounds.y ||
        pose.support.y > bounds.y + bounds.height)
    )
      issues.push(`Support must lie within the opaque extent: ${pose.poseId}.`);
  }
  return issues;
}
export function initialShapeReview(manifest: ShapeManifest, basedOn: AnimationPin): ShapeReview {
  return shapeReviewSchema.parse({
    schemaVersion: 1,
    basedOn,
    speciesId: manifest.speciesId,
    masterPoseId: manifest.clips.idle!.poses[0]!.poseId,
    poses: [
      ...new Map(
        Object.values(manifest.clips)
          .flatMap((clip) => clip?.poses ?? [])
          .map((pose) => [pose.poseId, pose]),
      ).values(),
    ].map((pose) => {
      const bounds = opaqueBounds(manifest.frames[pose.frame]!)!;
      return {
        poseId: pose.poseId,
        frame: pose.frame,
        visualBounds: bounds,
        support: { x: Math.round(bounds.x + bounds.width / 2), y: bounds.y + bounds.height },
        footprint: { left: 12, right: 12, back: 6, front: 6 },
        landmarks: [],
      };
    }),
  });
}
export function footprintBounds(
  footprint: PhysicalFootprint,
  origin: Point,
  direction: -1 | 1 = 1,
) {
  return {
    left: origin.x - (direction === 1 ? footprint.left : footprint.right),
    right: origin.x + (direction === 1 ? footprint.right : footprint.left),
    top: origin.y - footprint.back,
    bottom: origin.y + footprint.front,
  };
}
export function boundsOverlap(
  a: ReturnType<typeof footprintBounds>,
  b: ReturnType<typeof footprintBounds>,
) {
  return a.left < b.right && a.right > b.left && a.top < b.bottom && a.bottom > b.top;
}
