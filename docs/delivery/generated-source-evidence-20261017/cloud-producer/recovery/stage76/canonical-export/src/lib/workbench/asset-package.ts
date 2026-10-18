import { z } from 'zod';
import { speciesManifestV2Schema, type PixelRectangle } from '../assets/manifest-v2.ts';
import {
  OBJECT_CATALOG,
  objectKindSchema,
  type ObjectKind,
  type YardObject,
} from '../domain/scene.ts';

/** Local review resource envelope; this is not a production scene or animation contract. */
export const REVIEW_PACKAGE_LIMITS = Object.freeze({
  files: 12,
  manifestBytes: 32_768,
  compressedBytes: 4_194_304,
  decodedPixels: 262_144,
  rectangles: 16_384,
  palette: 64,
});
export const reviewSeasonSchema = z.enum(['base', 'spring', 'summer', 'autumn', 'winter']);
export type ReviewSeason = z.infer<typeof reviewSeasonSchema>;
/** Family declarations classify review capabilities; they never authorize another render path. */
export const reviewAssetFamilySchema = z.enum([
  'scene-layer',
  'catalog-object',
  'bird',
  'foliage',
  'decoration',
  'weather-layer',
]);
export type ReviewAssetFamily = z.infer<typeof reviewAssetFamilySchema>;
export const REVIEW_ASSET_FAMILY_SUPPORT = Object.freeze([
  {
    family: 'scene-layer',
    supported: true,
    reason: 'Existing side-view background, ground and foreground paint at scale four.',
  },
  {
    family: 'catalog-object',
    supported: true,
    reason: 'Existing catalog object skins with unchanged dimensions, pivots and contact anchors.',
  },
  {
    family: 'bird',
    supported: false,
    reason:
      'Use the existing native bird animation intake; this PNG review intake cannot create bird animation or contact geometry.',
  },
  {
    family: 'foliage',
    supported: true,
    reason:
      'V3 decorative foliage only, with fixed placement and no collision, support, shelter or wind authority.',
  },
  {
    family: 'decoration',
    supported: false,
    reason: 'Dedicated decoration placement and depth contracts are unsupported.',
  },
  {
    family: 'weather-layer',
    supported: false,
    reason: 'Dedicated weather layer blending, state and physical mask contracts are unsupported.',
  },
] as const);
export const REVIEW_COVERAGE_MASK_NOTE = 'Coverage alpha only, no physical mask.';
const manifestContractError =
  'The review manifest does not match the bounded review-only package contract.';
const familyIssuePrefix = 'Review asset family ';
const stateIssue =
  "Review asset state is unsupported; only 'default' is accepted, with no physical-state mask authority.";
const coverageIssue =
  "V2 review assets require coverageMask 'png-alpha': coverage alpha only, no physical mask.";
const familyRoleIssue =
  'Review asset family must match its scene-layer role or catalog-object role exactly.';
const contactIssue = 'Catalog-object review assets require unchanged catalog contact anchors.';

const id = z
  .string()
  .min(1)
  .max(80)
  .regex(/^[a-zA-Z0-9][a-zA-Z0-9._-]*$/);
const hash = z.string().regex(/^[a-f0-9]{64}$/);
const point = z
  .object({ x: z.number().int().min(0).max(256), y: z.number().int().min(0).max(256) })
  .strict();
const anchor = z
  .object({
    id,
    affordance: z.enum(['perch', 'feed', 'bath', 'nest']),
    dx: z.number().int(),
    dy: z.number().int(),
    capability: z.enum(['play', 'nest-building']).optional(),
  })
  .strict();
const rectangle = speciesManifestV2Schema.innerType().shape.frames.element.element;
export const reviewLayerRoleSchema = z.enum(['background', 'ground', 'foreground']);
const common = z
  .object({
    id,
    fileName: z
      .string()
      .min(5)
      .max(100)
      .regex(/^[A-Za-z0-9][A-Za-z0-9._-]*\.png$/),
    sha256: hash,
    season: reviewSeasonSchema,
    alpha: z.enum(['opaque', 'binary']),
    derivation: z
      .object({
        sourceSha256: hash,
        operations: z
          .array(
            z
              .object({
                operation: z.enum([
                  'crop',
                  'nearest-neighbor-downsample',
                  'palette-quantize',
                  'binary-alpha',
                ]),
                tool: z.string().min(1).max(120),
                version: z.string().min(1).max(80),
                details: z.string().min(1).max(1000),
              })
              .strict(),
          )
          .max(8),
      })
      .strict(),
  })
  .strict();
const layerFile = common
  .extend({
    role: reviewLayerRoleSchema,
    width: z.literal(240),
    height: z.literal(135),
    pivot: z.object({ x: z.literal(0), y: z.literal(0) }).strict(),
  })
  .strict();
const objectFile = common
  .extend({
    role: z.literal('object'),
    kind: objectKindSchema,
    width: z.number().int().min(1).max(256),
    height: z.number().int().min(1).max(256),
    pivot: point,
    anchors: z.array(anchor).min(1).max(4),
  })
  .strict();

const v2LayerFile = layerFile
  .extend({
    family: z.literal('scene-layer'),
    state: z.literal('default'),
    coverageMask: z.literal('png-alpha'),
  })
  .strict();
const v2ObjectFile = objectFile
  .extend({
    family: z.literal('catalog-object'),
    state: z.literal('default'),
    coverageMask: z.literal('png-alpha'),
  })
  .strict();

const foliagePhysicsSchema = z
  .object({
    collision: z.literal(false),
    supports: z.literal(false),
    shelter: z.literal(false),
    wind: z.literal(false),
  })
  .strict();
const foliageGeometryShape = {
  foliageId: id,
  themeId: id,
  width: z.number().int().min(1).max(256),
  height: z.number().int().min(1).max(256),
  pivot: point,
  placement: z
    .object({ x: z.number().int().min(0).max(960), y: z.number().int().min(0).max(540) })
    .strict(),
  scale: z.union([z.literal(1), z.literal(2), z.literal(4)]),
  depth: z.enum(['background', 'foreground']),
  physics: foliagePhysicsSchema,
  family: z.literal('foliage'),
  state: z.literal('default'),
  coverageMask: z.literal('png-alpha'),
};
const v3FoliageFile = common
  .extend({
    ...foliageGeometryShape,
    role: z.literal('foliage'),
    alpha: z.literal('binary'),
  })
  .strict();
type FoliageGeometry = z.infer<typeof v3FoliageFile>;
function foliageCanvasValid(
  file: Pick<FoliageGeometry, 'width' | 'height' | 'pivot' | 'placement' | 'scale'>,
) {
  return (
    file.pivot.x <= file.width &&
    file.pivot.y <= file.height &&
    file.placement.x - file.pivot.x * file.scale >= 0 &&
    file.placement.y - file.pivot.y * file.scale >= 0 &&
    file.placement.x + (file.width - file.pivot.x) * file.scale <= 960 &&
    file.placement.y + (file.height - file.pivot.y) * file.scale <= 540
  );
}
const foliageIssue =
  'V3 foliage must retain decorative-only geometry, a canvas inside the world, and unchanged base identity/theme/placement across seasons.';
const foliageCoverageIssue =
  "V3 review assets require coverageMask 'png-alpha': coverage alpha only, no physical mask.";

export function reviewObjectGeometry(kind: ObjectKind) {
  const definition = OBJECT_CATALOG[kind];
  return {
    width: definition.width,
    height: definition.height,
    pivot: { x: definition.width / 2, y: definition.height },
    anchors: definition.slots.map((slot) => ({ ...slot })),
  };
}
const legacyReviewPackageManifestSchema = z
  .object({
    schemaVersion: z.literal(1),
    kind: z.literal('workbench-review-package'),
    id,
    version: z.number().int().min(1).max(1_000_000),
    scope: z.literal('local-review-only'),
    approval: z.literal('unreviewed'),
    productionApproved: z.literal(false),
    projection: z.literal('side-view-orthographic'),
    world: z.object({ width: z.literal(960), height: z.literal(540) }).strict(),
    provenance: z
      .object({
        creator: z.string().min(1).max(200),
        tool: z.string().min(1).max(200),
        toolVersion: z.string().min(1).max(100),
        originality: z.literal('claimed-original-unreviewed'),
        rightsReview: z.literal('unreviewed'),
        licenseId: z.string().min(1).max(200),
        licenseEvidence: z.string().min(1).max(2000),
        sourceDigests: z.array(hash).min(1).max(32),
      })
      .strict(),
    files: z
      .array(z.union([layerFile, objectFile]))
      .min(1)
      .max(REVIEW_PACKAGE_LIMITS.files),
  })
  .strict();
const explicitReviewPackageManifestSchema = legacyReviewPackageManifestSchema
  .extend({
    schemaVersion: z.literal(2),
    files: z
      .array(z.union([v2LayerFile, v2ObjectFile]))
      .min(1)
      .max(REVIEW_PACKAGE_LIMITS.files),
  })
  .strict();

const foliageReviewPackageManifestSchema = legacyReviewPackageManifestSchema
  .extend({
    schemaVersion: z.literal(3),
    files: z
      .array(z.union([v2LayerFile, v2ObjectFile, v3FoliageFile]))
      .min(1)
      .max(REVIEW_PACKAGE_LIMITS.files),
  })
  .strict();

export const reviewPackageManifestSchema = z
  .preprocess(
    (input, context) => {
      if (!input || typeof input !== 'object') return input;
      const value = input as Record<string, unknown>;
      if (
        (value.schemaVersion !== 2 && value.schemaVersion !== 3) ||
        !Array.isArray(value.files) ||
        value.files.length > REVIEW_PACKAGE_LIMITS.files
      )
        return input;
      for (let index = 0; index < value.files.length; index++) {
        const raw: unknown = value.files[index];
        if (!raw || typeof raw !== 'object') continue;
        const file = raw as Record<string, unknown>;
        const issue = (message: string, field: string) =>
          context.addIssue({ code: 'custom', message, path: ['files', index, field] });
        const family = reviewAssetFamilySchema.safeParse(file.family);
        if (!family.success)
          issue(
            value.schemaVersion === 3
              ? 'Review asset family is unknown; choose scene-layer, catalog-object or foliage.'
              : 'Review asset family is unknown; choose scene-layer or catalog-object.',
            'family',
          );
        else if (
          family.data !== 'scene-layer' &&
          family.data !== 'catalog-object' &&
          !(value.schemaVersion === 3 && family.data === 'foliage')
        )
          issue(
            value.schemaVersion === 3
              ? `${familyIssuePrefix}'${family.data}' is unsupported by this intake; only scene-layer, catalog-object and decorative foliage are supported.`
              : `${familyIssuePrefix}'${family.data}' is unsupported by this intake; only scene-layer and catalog-object are supported.`,
            'family',
          );
        else if (
          family.data === 'foliage'
            ? file.role !== 'foliage'
            : (family.data === 'catalog-object') !== (file.role === 'object') ||
              file.role === 'foliage'
        )
          issue(family.data === 'foliage' ? foliageIssue : familyRoleIssue, 'family');
        if (file.state !== 'default') issue(stateIssue, 'state');
        if (file.coverageMask !== 'png-alpha')
          issue(value.schemaVersion === 3 ? foliageCoverageIssue : coverageIssue, 'coverageMask');
        if (
          family.success &&
          family.data === 'catalog-object' &&
          (!Array.isArray(file.anchors) || file.anchors.length === 0)
        )
          issue(contactIssue, 'anchors');
      }
      return input;
    },
    z.union([
      legacyReviewPackageManifestSchema,
      explicitReviewPackageManifestSchema,
      foliageReviewPackageManifestSchema,
    ]),
  )
  .superRefine((value, context) => {
    const fail = (message: string) => context.addIssue({ code: 'custom', message });
    for (const field of ['id', 'fileName'] as const)
      if (new Set(value.files.map((file) => file[field])).size !== value.files.length)
        fail('Asset IDs and filenames must be unique.');
    const keys = value.files.map(
      (file) =>
        `${file.season}/${file.role === 'object' ? `object/${file.kind}` : file.role === 'foliage' ? `foliage/${file.foliageId}` : file.role}`,
    );
    if (new Set(keys).size !== keys.length)
      fail('A season can supply only one asset per layer or object kind.');
    for (const file of value.files)
      if (
        file.season !== 'base' &&
        !value.files.some(
          (base) =>
            base.season === 'base' &&
            (file.role === 'object'
              ? base.role === 'object' && base.kind === file.kind
              : file.role === 'foliage'
                ? base.role === 'foliage' && base.foliageId === file.foliageId
                : base.role === file.role),
        )
      )
        fail('Every seasonal asset needs an unchanged-geometry base fallback.');
    if (
      value.files.reduce((sum, file) => sum + file.width * file.height, 0) >
      REVIEW_PACKAGE_LIMITS.decodedPixels
    )
      fail('Review package decoded pixel budget exceeded.');
    for (const file of value.files)
      if (file.role === 'foliage') {
        const base = value.files.find(
          (candidate) =>
            candidate.role === 'foliage' &&
            candidate.foliageId === file.foliageId &&
            candidate.season === 'base',
        );
        if (
          !foliageCanvasValid(file) ||
          !base ||
          base.role !== 'foliage' ||
          JSON.stringify([
            file.themeId,
            file.width,
            file.height,
            file.pivot,
            file.placement,
            file.scale,
            file.depth,
            file.physics,
          ]) !==
            JSON.stringify([
              base.themeId,
              base.width,
              base.height,
              base.pivot,
              base.placement,
              base.scale,
              base.depth,
              base.physics,
            ])
        )
          fail(foliageIssue);
      }
    if (new Set(value.provenance.sourceDigests).size !== value.provenance.sourceDigests.length)
      fail('Source digests must be distinct.');
    for (const file of value.files) {
      if (!value.provenance.sourceDigests.includes(file.derivation.sourceSha256))
        fail('Every file must retain a declared source digest.');
      if (!file.derivation.operations.length && file.derivation.sourceSha256 !== file.sha256)
        fail('Changed source bytes require declared derivation operations.');
      if (file.role === 'background' && file.alpha !== 'opaque')
        fail('The background must be opaque.');
      if (file.role !== 'background' && file.alpha !== 'binary')
        fail('Overlays and object skins require binary transparency.');
      if (file.role === 'object') {
        const geometry = reviewObjectGeometry(file.kind);
        if (
          file.width !== geometry.width ||
          file.height !== geometry.height ||
          JSON.stringify(file.pivot) !== JSON.stringify(geometry.pivot) ||
          JSON.stringify(file.anchors) !== JSON.stringify(geometry.anchors)
        )
          fail(
            'Object dimensions, pivot and anchors must exactly match the existing runtime catalog.',
          );
      }
    }
  });
export type ReviewPackageManifest = z.infer<typeof reviewPackageManifestSchema>;
export type ReviewPackageFile = ReviewPackageManifest['files'][number];

/** Parsed v1 remains unchanged; its supported family is inferred only for display. */
export function classifyReviewAssetPackage(metadata: ReviewPackageManifest) {
  const checked = reviewPackageManifestSchema.parse(metadata);
  return checked.files.map((file) => ({
    fileId: file.id,
    family:
      file.role === 'object'
        ? ('catalog-object' as const)
        : file.role === 'foliage'
          ? ('foliage' as const)
          : ('scene-layer' as const),
    declaration:
      checked.schemaVersion === 3
        ? ('explicit-v3' as const)
        : 'family' in file
          ? ('explicit-v2' as const)
          : ('inferred-v1' as const),
    ...(file.role === 'foliage' ? { foliageId: file.foliageId, themeId: file.themeId } : {}),
    role: file.role,
    season: file.season,
    state: 'default' as const,
    coverageMask: 'png-alpha' as const,
    coverageMaskDeclared: 'coverageMask' in file,
    maskNote: REVIEW_COVERAGE_MASK_NOTE,
    physicalMask: false as const,
  }));
}

/** Curated contract errors are safe for the upload UI; arbitrary exception details stay private. */
export function reviewPackageContractError(cause: unknown): string {
  if (!(cause instanceof z.ZodError)) return manifestContractError;
  return (
    cause.issues.find(
      (issue) =>
        issue.code === 'custom' &&
        (issue.message.startsWith(familyIssuePrefix) ||
          [
            stateIssue,
            coverageIssue,
            familyRoleIssue,
            contactIssue,
            foliageIssue,
            foliageCoverageIssue,
          ].includes(issue.message)),
    )?.message ?? manifestContractError
  );
}

const decodedAsset = z
  .object({
    fileId: id,
    canonicalSha256: hash,
    rgbaSha256: hash,
    decoder: z
      .object({
        id: z.literal('sharp'),
        version: z.string().min(1).max(40),
        libvips: z.string().min(1).max(40),
      })
      .strict(),
    normalization: z.literal('chirp-png-straight-srgb8-hidden-rgb-zero-v1'),
    rectangles: z.array(rectangle).min(1).max(4096),
  })
  .strict();
export const reviewAssetPackageSchema = z
  .object({
    metadata: reviewPackageManifestSchema,
    assets: z.array(decodedAsset).min(1).max(REVIEW_PACKAGE_LIMITS.files),
  })
  .strict()
  .superRefine((value, context) => {
    const fail = (message: string) => context.addIssue({ code: 'custom', message });
    if (
      value.assets.length !== value.metadata.files.length ||
      new Set(value.assets.map((asset) => asset.fileId)).size !== value.assets.length
    )
      fail('Decoded assets must correspond exactly to the package files.');
    const palette = new Set<number>();
    let count = 0;
    for (const asset of value.assets) {
      const file = value.metadata.files.find((entry) => entry.id === asset.fileId);
      if (!file) {
        fail('Decoded asset file identity is missing.');
        continue;
      }
      for (const rect of asset.rectangles) {
        palette.add(rect.color);
        count++;
        if (rect.x + rect.width > file.width || rect.y + rect.height > file.height)
          fail('Review pixels exceed their source canvas.');
      }
    }
    if (count > REVIEW_PACKAGE_LIMITS.rectangles || palette.size > REVIEW_PACKAGE_LIMITS.palette)
      fail('Review package rectangle or palette budget exceeded.');
  });
export type ReviewAssetPackage = z.infer<typeof reviewAssetPackageSchema>;

const reviewLayer = z
  .object({
    id,
    role: reviewLayerRoleSchema,
    width: z.literal(240),
    height: z.literal(135),
    scale: z.literal(4),
    rectangles: z.array(rectangle).min(1).max(4096),
  })
  .strict();
const reviewSkin = z
  .object({
    id,
    kind: objectKindSchema,
    width: z.number().int().min(1).max(256),
    height: z.number().int().min(1).max(256),
    pivot: point,
    rectangles: z.array(rectangle).min(1).max(4096),
  })
  .strict();
const legacyReviewArtSelectionSchema = z
  .object({
    schemaVersion: z.literal(1),
    scope: z.literal('local-review-only'),
    productionApproved: z.literal(false),
    packageId: id,
    packageVersion: z.number().int().min(1).max(1_000_000),
    season: reviewSeasonSchema,
    primitiveCount: z.number().int().min(1).max(REVIEW_PACKAGE_LIMITS.rectangles),
    layers: z.array(reviewLayer).max(3),
    objectSkins: z.array(reviewSkin).max(4),
  })
  .strict();
const reviewFoliageSchema = z
  .object({ id, ...foliageGeometryShape, rectangles: z.array(rectangle).min(1).max(4096) })
  .strict();
export type ReviewFoliage = z.infer<typeof reviewFoliageSchema>;
const foliageReviewArtSelectionSchema = legacyReviewArtSelectionSchema
  .extend({
    schemaVersion: z.literal(2),
    foliage: z.array(reviewFoliageSchema).max(REVIEW_PACKAGE_LIMITS.files),
  })
  .strict();
export const reviewArtSelectionSchema = z
  .union([legacyReviewArtSelectionSchema, foliageReviewArtSelectionSchema])
  .superRefine((value, context) => {
    const fail = (message: string) => context.addIssue({ code: 'custom', message });
    if (
      new Set(value.layers.map((layer) => layer.role)).size !== value.layers.length ||
      new Set(value.objectSkins.map((skin) => skin.kind)).size !== value.objectSkins.length
    )
      fail('Selected layer roles and object kinds must be unique.');
    const foliage = value.schemaVersion === 2 ? value.foliage : [];
    if (
      new Set(foliage.map((entry) => entry.foliageId)).size !== foliage.length ||
      foliage.some((entry) => !foliageCanvasValid(entry))
    )
      fail(foliageIssue);
    const entries = [...value.layers, ...value.objectSkins, ...foliage];
    if (value.schemaVersion === 2 && entries.length > REVIEW_PACKAGE_LIMITS.files)
      fail('Selection exceeds the review package file budget.');
    if (new Set(entries.map((entry) => entry.id)).size !== entries.length)
      fail('Selected review asset IDs must be unique.');
    const palette = new Set<number>();
    let count = 0;
    for (const entry of entries)
      for (const rect of entry.rectangles) {
        palette.add(rect.color);
        count++;
        if (rect.x + rect.width > entry.width || rect.y + rect.height > entry.height)
          fail('Selected pixels exceed source bounds.');
      }
    if (
      count !== value.primitiveCount ||
      count > REVIEW_PACKAGE_LIMITS.rectangles ||
      palette.size > REVIEW_PACKAGE_LIMITS.palette
    )
      fail('Selection must declare its exact bounded resource cost.');
    for (const skin of value.objectSkins) {
      const geometry = reviewObjectGeometry(skin.kind);
      if (
        skin.width !== geometry.width ||
        skin.height !== geometry.height ||
        skin.pivot.x !== geometry.pivot.x ||
        skin.pivot.y !== geometry.pivot.y
      )
        fail('Review skin geometry cannot change the runtime catalog.');
    }
  });
export type ValidatedReviewArt = z.infer<typeof reviewArtSelectionSchema>;
export type ReviewLayer = ValidatedReviewArt['layers'][number];
export type ReviewObjectSkin = ValidatedReviewArt['objectSkins'][number];

export function selectReviewArt(
  input: ReviewAssetPackage,
  season: ReviewSeason,
): ValidatedReviewArt {
  const checked = reviewAssetPackageSchema.parse(input);
  const chosen = new Map<string, ReviewPackageFile>();
  for (const desired of ['base', season])
    for (const file of checked.metadata.files) {
      if (file.season === desired)
        chosen.set(
          file.role === 'object'
            ? `object/${file.kind}`
            : file.role === 'foliage'
              ? `foliage/${file.foliageId}`
              : file.role,
          file,
        );
    }
  const layers: ReviewLayer[] = [],
    objectSkins: ReviewObjectSkin[] = [],
    foliage: ReviewFoliage[] = [];
  for (const file of chosen.values()) {
    const rectangles = checked.assets.find((asset) => asset.fileId === file.id)!.rectangles;
    if (file.role === 'object')
      objectSkins.push({
        id: file.id,
        kind: file.kind,
        width: file.width,
        height: file.height,
        pivot: file.pivot,
        rectangles,
      });
    else if (file.role === 'foliage')
      foliage.push({
        id: file.id,
        foliageId: file.foliageId,
        themeId: file.themeId,
        width: file.width,
        height: file.height,
        pivot: file.pivot,
        placement: file.placement,
        scale: file.scale,
        depth: file.depth,
        physics: file.physics,
        family: file.family,
        state: file.state,
        coverageMask: file.coverageMask,
        rectangles,
      });
    else
      layers.push({
        id: file.id,
        role: file.role,
        width: file.width,
        height: file.height,
        scale: 4,
        rectangles,
      });
  }
  return reviewArtSelectionSchema.parse({
    schemaVersion: checked.metadata.schemaVersion === 3 ? 2 : 1,
    ...(checked.metadata.schemaVersion === 3 ? { foliage } : {}),
    scope: 'local-review-only',
    productionApproved: false,
    packageId: checked.metadata.id,
    packageVersion: checked.metadata.version,
    season,
    primitiveCount: [...layers, ...objectSkins, ...foliage].reduce(
      (sum, entry) => sum + entry.rectangles.length,
      0,
    ),
    layers,
    objectSkins,
  });
}

/** Review paint follows existing placed object depth/anchors; it never supplies simulation geometry. */
export function reviewObjectPlacement(skin: ReviewObjectSkin, object: YardObject) {
  if (skin.kind !== object.kind)
    throw new Error('The review skin does not match the placed object.');
  return {
    x: object.x - skin.pivot.x,
    y: object.y - skin.pivot.y,
    depth: object.y,
    anchors: OBJECT_CATALOG[object.kind].slots.map((slot) => ({
      ...slot,
      x: object.x + slot.dx,
      y: object.y + slot.dy,
    })),
  };
}
export function reviewArtPrimitiveCost(art: ValidatedReviewArt, objects: readonly YardObject[]) {
  return (
    art.layers.reduce((sum, layer) => sum + layer.rectangles.length, 0) +
    (art.schemaVersion === 2
      ? art.foliage.reduce((sum, entry) => sum + entry.rectangles.length, 0)
      : 0) +
    objects.reduce(
      (sum, object) =>
        sum + (art.objectSkins.find((skin) => skin.kind === object.kind)?.rectangles.length ?? 0),
      0,
    )
  );
}
/** Raw cost, including every placed instance. Caller rejects the whole overlay before scene admission. */
export function reviewArtPrimitiveReserve(
  art: ValidatedReviewArt | null | undefined,
  objects: readonly YardObject[] = [],
) {
  return art ? reviewArtPrimitiveCost(art, objects) : 0;
}
export function parseReviewPackageManifest(text: string): ReviewPackageManifest {
  if (new TextEncoder().encode(text).byteLength > REVIEW_PACKAGE_LIMITS.manifestBytes)
    throw new Error('Review manifests are limited to 32 KiB.');
  const input: unknown = JSON.parse(text);
  return reviewPackageManifestSchema.parse(input);
}
export type ReviewPixelRectangle = PixelRectangle;
