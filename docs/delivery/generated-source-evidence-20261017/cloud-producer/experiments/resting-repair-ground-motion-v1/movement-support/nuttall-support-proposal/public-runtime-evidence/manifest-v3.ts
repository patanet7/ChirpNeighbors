import { z } from 'zod';
import { catalogEntry } from '../domain/yard.ts';
import { measureLoopEdges } from './metrics-v3.ts';
import { animationPinSchema, animationStates, speciesManifestV2Schema } from './manifest-v2.ts';
import { shapeReviewSchema, shapeReviewIssues } from './shape.ts';

const legacy = speciesManifestV2Schema.innerType().shape;
const id = z
  .string()
  .min(1)
  .max(160)
  .regex(/^[a-zA-Z0-9][a-zA-Z0-9._:@-]*$/);
const integer = z.number().int().min(0).max(Number.MAX_SAFE_INTEGER);
export const pointSchema = z.object({ x: integer.max(256), y: integer.max(256) }).strict();
export const contactSchema = pointSchema
  .extend({
    kind: z.enum(['left-foot', 'right-foot', 'perch', 'ground']),
  })
  .strict();
export const animationPoseSchema = z
  .object({
    frame: integer.max(63),
    durationTicks: z.number().int().min(1).max(300),
    pivot: pointSchema,
    contacts: z.array(contactSchema).max(4),
    poseId: id,
    rotation: z.number().min(-0.5).max(0.5),
  })
  .strict();
export const animationClipV3Schema = z
  .object({
    action: z.enum(animationStates),
    direction: z.literal('right-facing-mirrorable'),
    loop: z.boolean(),
    poses: z.array(animationPoseSchema).min(1).max(256),
  })
  .strict();
export const animationClipsV3Schema = z
  .object({
    idle: animationClipV3Schema,
    moving: animationClipV3Schema.optional(),
    perching: animationClipV3Schema.optional(),
    singing: animationClipV3Schema.optional(),
    feeding: animationClipV3Schema.optional(),
    bathing: animationClipV3Schema.optional(),
    sleeping: animationClipV3Schema.optional(),
    playing: animationClipV3Schema.optional(),
    nesting: animationClipV3Schema.optional(),
  })
  .strict();
export const taxonomyIdentitySchema = z
  .object({
    catalog: z.literal('chirp-display-catalog'),
    version: z.literal(1),
    speciesId: id,
  })
  .strict()
  .superRefine((value, context) => {
    if (!catalogEntry(value.speciesId))
      context.addIssue({
        code: 'custom',
        message: 'Species is absent from the pinned application catalog.',
      });
  });
export const reviewedReferenceSchema = z
  .object({
    id,
    roles: z
      .array(z.enum(['species', 'style', 'pose']))
      .min(1)
      .max(3),
    pin: animationPinSchema,
  })
  .strict()
  .superRefine((value, context) => {
    if (new Set(value.roles).size !== value.roles.length)
      context.addIssue({ code: 'custom', message: 'Reference roles must be distinct.' });
  });
export const poseGraphSchema = z
  .object({
    nodes: z
      .array(
        z
          .object({
            id,
            frame: integer.max(63),
            action: z.enum(animationStates),
            referenceId: id,
          })
          .strict(),
      )
      .min(1)
      .max(576),
    edges: z.array(z.object({ from: id, to: id }).strict()).max(2304),
  })
  .strict();
export const animationConditioningSchema = z
  .object({
    taxonomy: taxonomyIdentitySchema,
    references: z.array(reviewedReferenceSchema).min(1).max(16),
    poseGraph: poseGraphSchema,
  })
  .strict();
export const normalizationReportSchema = z
  .object({
    algorithm: z.literal('lossless-rgba-rects-v2'),
    alpha: z.literal('binary'),
    logicalPixelSize: z.number().int().min(1).max(16),
    palette: z.array(z.number().int().min(0).max(0xffffff)).min(1).max(64),
    loopEdges: z
      .array(
        z
          .object({
            action: z.enum(animationStates),
            comparedPixels: integer.min(1).max(65_536),
            changedPixels: integer.max(65_536),
            pivotDistance: z.number().min(0).max(512),
            contactLayoutChanged: z.boolean(),
          })
          .strict(),
      )
      .max(9),
  })
  .strict();

const metricGeometrySchema = z
  .object({
    canvas: legacy.canvas.omit({ anchorX: true, anchorY: true }),
    frames: legacy.frames,
    clips: animationClipsV3Schema,
  })
  .strip();

/** Render v3 keeps rectangle geometry, but timing/anchors belong to each clip pose.
 * Contact coordinates are review evidence and renderer diagnostics, not an IK solver. */
const manifestV3BaseSchema = z
  .object({
    schemaVersion: z.literal(3),
    speciesId: legacy.speciesId,
    representation: legacy.representation,
    fixture: legacy.fixture,
    taxonFidelityReviewed: legacy.taxonFidelityReviewed,
    format: legacy.format,
    canvas: legacy.canvas.omit({ anchorX: true, anchorY: true }),
    frames: legacy.frames,
    clips: animationClipsV3Schema,
    provenance: legacy.provenance,
    conditioning: animationConditioningSchema,
    sourceArtifact: animationPinSchema,
    normalization: normalizationReportSchema,
    shape: shapeReviewSchema.optional(),
  })
  .strict();
/** Shared geometry validation; caller separately validates its actual provenance class. */
export function validatePoseManifestGeometry(
  value: Omit<
    z.infer<typeof manifestV3BaseSchema>,
    'schemaVersion' | 'fixture' | 'taxonFidelityReviewed' | 'provenance'
  >,
  context: z.RefinementCtx,
) {
  const fail = (message: string) => context.addIssue({ code: 'custom', message });
  const { width, height } = value.canvas;
  if (width * height * value.frames.length > 65_536) {
    fail('Decoded animation exceeds pixel budget.');
    return;
  }
  if (value.frames.reduce((sum, frame) => sum + frame.length, 0) > 16_384)
    fail('Manifest exceeds rectangle budget.');
  if (value.conditioning.taxonomy.speciesId !== value.speciesId)
    fail('Taxonomy and manifest species differ.');
  const grid = value.normalization.logicalPixelSize;
  if (width % grid || height % grid) fail('Canvas does not align to logical grid.');
  const colors = new Set<number>();
  for (const frame of value.frames)
    for (const rect of frame) {
      if (rect.x + rect.width > width || rect.y + rect.height > height)
        fail('Frame exceeds canvas bounds.');
      if (rect.x % grid || rect.y % grid || rect.width % grid || rect.height % grid)
        fail('Rectangle does not align to logical grid.');
      colors.add(rect.color);
    }
  if (
    new Set(value.normalization.palette).size !== value.normalization.palette.length ||
    value.normalization.palette.length !== colors.size ||
    value.normalization.palette.some((color) => !colors.has(color))
  )
    fail('Palette does not match authored pixels.');
  const refs = value.conditioning.references;
  if (
    new Set(refs.map((ref) => ref.id)).size !== refs.length ||
    refs.filter((ref) => ref.roles.includes('style')).length !== 1
  )
    fail('Conditioning requires unique references and exactly one reviewed style reference.');
  const graph = value.conditioning.poseGraph;
  const nodes = new Map(graph.nodes.map((node) => [node.id, node]));
  if (nodes.size !== graph.nodes.length) fail('Pose node IDs must be unique.');
  for (const node of graph.nodes)
    if (
      node.frame >= value.frames.length ||
      !refs.some((ref) => ref.id === node.referenceId && ref.roles.includes('pose'))
    )
      fail('Pose reference/frame is unavailable.');
  const edgeKey = (from: string, to: string) => JSON.stringify([from, to]);
  const declaredEdges = new Set(graph.edges.map((edge) => edgeKey(edge.from, edge.to)));
  if (
    declaredEdges.size !== graph.edges.length ||
    graph.edges.some((edge) => !nodes.has(edge.from) || !nodes.has(edge.to))
  )
    fail('Pose edges must be unique and reference available nodes.');
  const usedNodes = new Set<string>(),
    usedEdges = new Set<string>();
  const loops = new Set<string>();
  for (const [action, clip] of Object.entries(value.clips)) {
    if (!clip) continue;
    if (clip.action !== action) fail('Clip action must match its registered state.');
    for (const [index, pose] of clip.poses.entries()) {
      const node = nodes.get(pose.poseId);
      if (!node || node.frame !== pose.frame || node.action !== action)
        fail('Clip pose does not match its graph node.');
      usedNodes.add(pose.poseId);
      if (
        pose.frame >= value.frames.length ||
        pose.pivot.x > width ||
        pose.pivot.y > height ||
        pose.contacts.some((contact) => contact.x > width || contact.y > height)
      )
        fail('Clip frame/pivot/contact exceeds bounds.');
      if (new Set(pose.contacts.map((contact) => contact.kind)).size !== pose.contacts.length)
        fail('Contact kinds must be unique per pose.');
      const next = clip.poses[index + 1] ?? (clip.loop ? clip.poses[0] : undefined);
      if (next) usedEdges.add(edgeKey(pose.poseId, next.poseId));
    }
    if (clip.loop) loops.add(action);
  }
  if (
    usedNodes.size !== nodes.size ||
    usedEdges.size !== declaredEdges.size ||
    [...usedEdges].some((edge) => !declaredEdges.has(edge))
  )
    fail('Pose graph must describe exactly the authored clip transitions.');
  const metrics = value.normalization.loopEdges;
  if (
    new Set(metrics.map((entry) => entry.action)).size !== metrics.length ||
    metrics.length !== loops.size ||
    metrics.some(
      (entry) =>
        !loops.has(entry.action) ||
        entry.comparedPixels !== width * height ||
        entry.changedPixels > entry.comparedPixels,
    )
  )
    fail('Loop metrics do not match authored looping clips.');
  const validIndices = Object.values(value.clips).every(
    (clip) => !clip || clip.poses.every((pose) => pose.frame < value.frames.length),
  );
  if (validIndices && metricGeometrySchema.safeParse(value).success) {
    if (value.shape) for (const issue of shapeReviewIssues(value, value.shape)) fail(issue);
    const measured = measureLoopEdges(value.canvas, value.frames, value.clips);
    if (
      measured.some((entry) => {
        const declared = metrics.find((metric) => metric.action === entry.action);
        return (
          !declared ||
          declared.changedPixels !== entry.changedPixels ||
          declared.pivotDistance !== entry.pivotDistance ||
          declared.contactLayoutChanged !== entry.contactLayoutChanged
        );
      })
    )
      fail('Loop metrics do not match decoded frame edges.');
  }
}
export const speciesManifestV3Schema = manifestV3BaseSchema.superRefine((value, context) => {
  validatePoseManifestGeometry(value, context);
  const fail = (message: string) => context.addIssue({ code: 'custom', message });
  if (
    value.fixture
      ? value.taxonFidelityReviewed ||
        value.provenance.source !== 'deterministic_fixture' ||
        value.provenance.usage !== 'development-only'
      : !value.taxonFidelityReviewed ||
        value.provenance.source === 'deterministic_fixture' ||
        value.provenance.usage !== 'cleared'
  )
    fail('Fixture/fidelity provenance is inconsistent.');
});
export type SpeciesManifestV3 = z.infer<typeof speciesManifestV3Schema>;
export type AnimationClipsV3 = z.infer<typeof animationClipsV3Schema>;
export type AnimationConditioning = z.infer<typeof animationConditioningSchema>;
