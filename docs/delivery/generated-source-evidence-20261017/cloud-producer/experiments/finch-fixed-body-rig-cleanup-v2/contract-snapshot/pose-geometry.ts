import type { SpeciesManifest, sampleClip } from './manifest';
import { opaqueBounds, type Point, type ShapeReview } from './shape';
export type PoseSample = ReturnType<typeof sampleClip>;
/** Optional reviewed annotation seam; absent legacy data keeps the authored pivot behavior. */
export function reviewedShape(manifest: SpeciesManifest): ShapeReview | undefined {
  return manifest.schemaVersion !== 2 ? manifest.shape : undefined;
}
/** V2/V3 coordinates retain their historical one-source-unit-to-world-unit mapping. */
export function sourceWorldScale(manifest: SpeciesManifest) {
  return manifest.schemaVersion === 4 ? 1 / manifest.presentation.sourcePixelsPerWorldUnit : 1;
}
/** One conservative ground footprint across poses and facings, shared by Pixi and SVG admission. */
export function physicalClearance(manifest: SpeciesManifest) {
  const shape = reviewedShape(manifest);
  if (!shape) return undefined;
  const scale = sourceWorldScale(manifest);
  const side =
    scale * Math.max(...shape.poses.flatMap((pose) => [pose.footprint.left, pose.footprint.right]));
  return {
    left: side,
    right: side,
    back: scale * Math.max(...shape.poses.map((pose) => pose.footprint.back)),
    front: scale * Math.max(...shape.poses.map((pose) => pose.footprint.front)),
  };
}
export function poseShape(manifest: SpeciesManifest, sample: PoseSample) {
  return reviewedShape(manifest)?.poses.find(
    (pose) => pose.poseId === sample.poseId && pose.frame === sample.frame,
  );
}
export interface PoseTransform {
  origin: Point;
  pivot: Point;
  direction: -1 | 1;
  rotation: number;
  scale?: number;
}
/** World position is the support anchor, not a sprite top-left. Rotation follows mirroring. */
export function poseTransform(
  manifest: SpeciesManifest,
  sample: PoseSample,
  position: Point,
  direction: -1 | 1,
  flightOffset = 0,
  scale = sourceWorldScale(manifest),
): PoseTransform {
  const rotation = direction * sample.rotation;
  const annotation = poseShape(manifest, sample);
  const pivot = sample.pivot;
  const anchor = annotation ? annotation.support : pivot;
  const dx = direction * (anchor.x - pivot.x) * scale,
    dy = (anchor.y - pivot.y) * scale;
  return {
    pivot,
    direction,
    rotation,
    ...(scale === 1 ? {} : { scale }),
    origin: {
      x: position.x - (Math.cos(rotation) * dx - Math.sin(rotation) * dy),
      y: position.y + flightOffset - (Math.sin(rotation) * dx + Math.cos(rotation) * dy),
    },
  };
}
export function frameToWorld(point: Point, transform: PoseTransform): Point {
  const x = (point.x - transform.pivot.x) * transform.direction * (transform.scale ?? 1),
    y = (point.y - transform.pivot.y) * (transform.scale ?? 1);
  return {
    x: transform.origin.x + Math.cos(transform.rotation) * x - Math.sin(transform.rotation) * y,
    y: transform.origin.y + Math.sin(transform.rotation) * x + Math.cos(transform.rotation) * y,
  };
}
export function worldToFrame(point: Point, transform: PoseTransform): Point {
  const x = (point.x - transform.origin.x) / (transform.scale ?? 1),
    y = (point.y - transform.origin.y) / (transform.scale ?? 1);
  return {
    x:
      (Math.cos(transform.rotation) * x + Math.sin(transform.rotation) * y) * transform.direction +
      transform.pivot.x,
    y: -Math.sin(transform.rotation) * x + Math.cos(transform.rotation) * y + transform.pivot.y,
  };
}
export function opaqueHit(sample: PoseSample, transform: PoseTransform, point: Point) {
  const local = worldToFrame(point, transform);
  return sample.rectangles.some(
    (rect) =>
      local.x >= rect.x &&
      local.x < rect.x + rect.width &&
      local.y >= rect.y &&
      local.y < rect.y + rect.height,
  );
}
export function transformedVisualBounds(sample: PoseSample, transform: PoseTransform) {
  const bounds = opaqueBounds(sample.rectangles);
  if (!bounds) return null;
  const corners = [
    { x: bounds.x, y: bounds.y },
    { x: bounds.x + bounds.width, y: bounds.y },
    { x: bounds.x, y: bounds.y + bounds.height },
    { x: bounds.x + bounds.width, y: bounds.y + bounds.height },
  ].map((point) => frameToWorld(point, transform));
  return {
    left: Math.min(...corners.map((point) => point.x)),
    right: Math.max(...corners.map((point) => point.x)),
    top: Math.min(...corners.map((point) => point.y)),
    bottom: Math.max(...corners.map((point) => point.y)),
  };
}
export function svgPoseTransform(transform: PoseTransform) {
  return `translate(${transform.origin.x},${transform.origin.y}) rotate(${(transform.rotation * 180) / Math.PI}) scale(${transform.direction * (transform.scale ?? 1)},${transform.scale ?? 1})`;
}
