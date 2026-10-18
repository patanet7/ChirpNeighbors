/** Frozen Integration10 planar placement review. Source pixels, authored ground and
 * persisted world roots are separate coordinates. No metres, support heights or
 * upright sprite scale are derived from this registration. */
export const INTEGRATION10_GROUND_RELEASE = Object.freeze({
  id: 'sd-inland-ground-v2',
  version: 2,
  sourceReleaseDigest: '3de66c0b4d5278196a493cd7637f11fd2000ec928198ef82d62f9f3cab139e57',
  geometryDigest: 'bea532e535f7620973ee9d8a9d3aa858533f682db8e3398031f956328fdccd5e',
  calibrationDigest: 'f0681bf8ed840b6748472fed18cea73504af346d9aa2cf92d80f265ca3453fe1',
});
export const INTEGRATION10_GROUND_REVIEW = Object.freeze({
  scope: 'planar-lawn-placement-only',
  sourceCanvas: Object.freeze({ width: 1536, height: 1024 }),
  sourceCrop: Object.freeze({ left: 0, top: 160, right: 1536, bottom: 1024 }),
  sourceFloor: Object.freeze({ left: 0, top: 494, right: 1536, bottom: 1024 }),
  worldFloor: Object.freeze({ left: 0, top: 208.75, right: 960, bottom: 540 }),
  fenceCoverageAtAlpha128: Object.freeze({ sourceBottom: 488, worldBottom: 205 }),
  floorMaskSha256: 'b47043e31197424aaf5a66df800930f432861f922807dfa12c509d1e3e98bb89',
  floorMaskCoveredPixels: 814080,
  permanentHoles: Object.freeze([]),
  uprightScale: 'retain-canonical-object-geometry',
  supports: 'not-approved',
  metricCalibration: false,
  inspection: 'actual-spring-empty-yard-layer-sheet-and-source-mask-coverage',
});
export interface GroundPoint {
  x: number;
  y: number;
}
export interface GroundBounds {
  left: number;
  top: number;
  right: number;
  bottom: number;
}
const finite = (point: GroundPoint) => Number.isFinite(point.x) && Number.isFinite(point.y);
const WORLD_SCALE = 0.625;
/** Origin is source[0,494], rather than the source canvas or the camera crop. */
export function integration10GroundToWorld(point: GroundPoint): GroundPoint | null {
  if (!finite(point) || point.x < 0 || point.x > 1536 || point.y < 0 || point.y > 530) return null;
  return { x: point.x * WORLD_SCALE, y: 208.75 + point.y * WORLD_SCALE };
}
export function integration10WorldToGround(point: GroundPoint): GroundPoint | null {
  if (!finite(point) || point.x < 0 || point.x > 960 || point.y < 208.75 || point.y > 540)
    return null;
  return { x: point.x / WORLD_SCALE, y: (point.y - 208.75) / WORLD_SCALE };
}
/** Full source-bound footprint, not sprite alpha. Edge tangency rejects, matching
 * the registered-ground candidate's conservative footprint policy. */
export function integration10ContainsFootprint(bounds: GroundBounds): boolean {
  const { left, right, top, bottom } = bounds;
  return (
    [left, right, top, bottom].every(Number.isFinite) &&
    left < right &&
    top < bottom &&
    left > 0 &&
    right < 960 &&
    top > 208.75 &&
    bottom < 540
  );
}
/** Move the known ground root by the screen grab delta, THEN invert that root.
 * Inverting the grabbed elevated sprite pixel would discard its upright offset. */
export function integration10DragRoot(
  origin: GroundPoint,
  start: GroundPoint,
  pointer: GroundPoint,
) {
  if (![origin, start, pointer].every(finite)) return null;
  const world = {
    x: Math.round(origin.x + pointer.x - start.x),
    y: Math.round(origin.y + pointer.y - start.y),
  };
  const ground = integration10WorldToGround(world);
  return ground ? { world, ground } : null;
}
