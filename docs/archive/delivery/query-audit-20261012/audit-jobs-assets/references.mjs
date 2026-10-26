// audit-jobs-assets/references.ts
import { DatabaseSync as DatabaseSync2 } from "node:sqlite";
import { mkdirSync as mkdirSync3, writeFileSync as writeFileSync2 } from "node:fs";
import { join as join4 } from "node:path";
import { randomUUID as randomUUID4 } from "node:crypto";
import { performance } from "node:perf_hooks";
import sharp2 from "sharp";

// birdsong-yard-sprites/src/lib/scenes/fixture-geometry.ts
var shape = (x, y, width, height, color, alpha) => ({ x, y, width, height, color, ...alpha === void 0 ? {} : { alpha } });
function backgroundPrimitives(setting) {
  const result2 = [shape(0, 0, 960, 540, "sky"), shape(0, 145, 960, 145, "skyLow")];
  result2.push(
    shape(40, 204, 196, 96, "wall"),
    shape(30, 195, 216, 11, "trunk"),
    shape(42, 184, 192, 11, "trunk"),
    shape(60, 173, 156, 11, "wood"),
    shape(73, 218, 44, 38, "sky"),
    shape(93, 218, 4, 38, "wood")
  );
  for (let i = 0; i < 13; i++) {
    const y = 247 - i * 17 % 30;
    result2.push(
      shape(i * 80, y, 85, 310 - y, "leaf"),
      shape(i * 80 + 9, y - 8, 61, 10, "leafLight")
    );
  }
  const fenceY = setting === "courtyard" ? 283 : 281;
  result2.push(shape(0, fenceY + 21, 960, 9, "wood"), shape(0, fenceY + 58, 960, 8, "wood"));
  for (let x = 0; x < 960; x += 28)
    result2.push(shape(x, fenceY, 22, 74, "wood"), shape(x + 3, fenceY + 3, 3, 68, "glow", 0.14));
  return result2;
}
function groundPrimitives(setting) {
  const result2 = [shape(0, 354, 960, 186, "grassLight"), shape(0, 354, 960, 14, "grass")];
  if (setting === "courtyard") {
    result2.push(shape(44, 366, 72, 174, "stone"), shape(844, 366, 72, 174, "stone"));
    for (let y = 380; y < 540; y += 28)
      result2.push(shape(44, y, 72, 2, "trunk", 0.16), shape(844, y, 72, 2, "trunk", 0.16));
  }
  for (let i = 0; i < 52; i++) {
    const x = 30 + i * 107 % 900, y = 379 + i * 47 % 150;
    result2.push(shape(x, y, 3, 5, "grass", 0.65), shape(x + 5, y - 2, 2, 7, "grass", 0.65));
  }
  return result2;
}
function foregroundPrimitives() {
  const result2 = [];
  for (const x of [0, 25, 920, 943])
    result2.push(shape(x, 510, 25, 30, "leaf"), shape(x + 5, 501, 17, 12, "leafLight"));
  for (const x of [13, 39, 927, 950])
    result2.push(shape(x, 500, 3, 18, "leaf"), shape(x - 4, 497, 11, 7, "flower"));
  return result2;
}

// birdsong-yard-sprites/src/lib/scenes/manifest.ts
import { z as z2 } from "zod";

// birdsong-yard-sprites/src/lib/domain/primitives.ts
import { z } from "zod";
var timestampSchema = z.string().datetime();
var idSchema = z.string().min(1).max(160).regex(/^[a-zA-Z0-9][a-zA-Z0-9._:-]*$/).refine((value) => !["__proto__", "prototype", "constructor"].includes(value));

// birdsong-yard-sprites/src/lib/scenes/manifest.ts
var WORLD_WIDTH = 960;
var WORLD_HEIGHT = 540;
var sceneSettingSchema = z2.enum(["garden", "courtyard"]);
var scenePinSchema = z2.object({ id: idSchema, version: z2.number().int().min(1).max(1e6) }).strict();
var regionPreferenceSchema = z2.enum([
  "unspecified",
  "europe",
  "north-america",
  "south-america",
  "africa",
  "asia",
  "oceania"
]);
var paletteColorSchema = z2.enum([
  "sky",
  "skyLow",
  "grass",
  "grassLight",
  "leaf",
  "leafLight",
  "trunk",
  "wood",
  "wall",
  "stone",
  "water",
  "flower",
  "glow"
]);
var pixelRectSchema = z2.object({
  x: z2.number().finite().int().min(0),
  y: z2.number().finite().int().min(0),
  width: z2.number().finite().int().min(1),
  height: z2.number().finite().int().min(1),
  color: paletteColorSchema,
  alpha: z2.number().finite().min(0).max(1).optional()
}).strict();
var boundsSchema = z2.object({
  left: z2.number().finite().min(0),
  right: z2.number().finite().max(WORLD_WIDTH),
  top: z2.number().finite().min(0),
  bottom: z2.number().finite().max(WORLD_HEIGHT)
}).strict().refine((b) => b.left < b.right && b.top < b.bottom, "Zones must have positive area.");
var containsPoint = (b, x, y) => x >= b.left && x <= b.right && y >= b.top && y <= b.bottom;
var containsBounds = (outer, inner) => containsPoint(outer, inner.left, inner.top) && containsPoint(outer, inner.right, inner.bottom);
var point = z2.object({ id: idSchema, x: z2.number().finite(), y: z2.number().finite() }).strict();
var layer = (order) => z2.object({ order: z2.literal(order), assetId: idSchema }).strict();
var sceneManifestSchema = z2.object({
  schemaVersion: z2.literal(1),
  id: idSchema,
  version: scenePinSchema.shape.version,
  publicSceneId: sceneSettingSchema,
  label: z2.string().min(1).max(80),
  representation: z2.literal("technical-fixture"),
  provenance: z2.object({
    kind: z2.literal("existing-authored-geometry"),
    approvedRegionalArt: z2.literal(false)
  }).strict(),
  world: z2.object({ width: z2.literal(WORLD_WIDTH), height: z2.literal(WORLD_HEIGHT) }).strict(),
  assets: z2.array(
    z2.object({
      id: idSchema,
      kind: z2.literal("inline-palette-rectangles"),
      rectangles: z2.array(pixelRectSchema).min(1).max(512)
    }).strict()
  ).min(3).max(3),
  layers: z2.object({ background: layer(0), ground: layer(1), foreground: layer(3) }).strict(),
  depth: z2.object({
    order: z2.literal(2),
    sort: z2.literal("ground-y"),
    actorOffset: z2.literal(0.25),
    weatherOrder: z2.literal(4)
  }).strict(),
  zones: z2.object({
    placement: z2.array(boundsSchema).min(1).max(8),
    walkable: z2.array(boundsSchema).min(1).max(8)
  }).strict(),
  navigation: z2.object({
    mode: z2.literal("flight-corridors"),
    groundSlots: z2.array(point).min(1).max(128),
    roaming: boundsSchema,
    overflow: z2.object({ left: z2.number().finite(), right: z2.number().finite(), y: z2.number().finite() }).strict()
  }).strict()
}).strict().superRefine((manifest, ctx) => {
  const fail = (message) => ctx.addIssue({ code: "custom", message });
  const assets = new Map(manifest.assets.map((asset) => [asset.id, asset]));
  if (assets.size !== manifest.assets.length) fail("Scene asset IDs must be unique.");
  const references = Object.values(manifest.layers).map((value) => value.assetId);
  if (new Set(references).size !== 3 || references.some((id8) => !assets.has(id8)))
    fail("Each required scene layer needs its own valid asset.");
  for (const asset of manifest.assets)
    for (const rect of asset.rectangles)
      if (rect.x + rect.width > manifest.world.width || rect.y + rect.height > manifest.world.height)
        fail("Scene asset pixels must fit the world bounds.");
  const { groundSlots, roaming, overflow } = manifest.navigation;
  if (new Set(groundSlots.map((slot) => slot.id)).size !== groundSlots.length)
    fail("Ground slot IDs must be unique.");
  if (groundSlots.some(
    (slot) => !slot.id.startsWith("ground:") || !manifest.zones.walkable.some((zone) => containsPoint(zone, slot.x, slot.y))
  ))
    fail("Ground slots must be named ground:* and lie in walkable zones.");
  if (!manifest.zones.walkable.some((zone) => containsBounds(zone, roaming)))
    fail("Roaming bounds must fit a walkable zone.");
  if (overflow.left >= overflow.right || !manifest.zones.walkable.some(
    (zone) => containsPoint(zone, overflow.left, overflow.y) && containsPoint(zone, overflow.right, overflow.y)
  ))
    fail("Overflow anchors must fit a walkable zone.");
  if (manifest.zones.placement.some(
    (zone) => overflow.y >= zone.top - 12 && overflow.y <= zone.bottom + 12 && overflow.right >= zone.left - 20 && overflow.left <= zone.right + 20
  ))
    fail("Overflow anchors must remain clear of placeable footprints.");
});

// birdsong-yard-sprites/src/lib/scenes/catalog.ts
function clip(rectangles) {
  return rectangles.map((rect) => ({
    ...rect,
    width: Math.min(rect.width, 960 - rect.x),
    height: Math.min(rect.height, 540 - rect.y)
  })).filter((rect) => rect.width > 0 && rect.height > 0);
}
function fixture(setting) {
  return sceneManifestSchema.parse({
    schemaVersion: 1,
    id: `fixture-${setting}`,
    version: 1,
    publicSceneId: setting,
    label: `${setting === "garden" ? "Garden" : "Courtyard"} technical fixture`,
    representation: "technical-fixture",
    provenance: { kind: "existing-authored-geometry", approvedRegionalArt: false },
    world: { width: 960, height: 540 },
    assets: [
      {
        id: "background",
        kind: "inline-palette-rectangles",
        rectangles: clip(backgroundPrimitives(setting))
      },
      {
        id: "ground",
        kind: "inline-palette-rectangles",
        rectangles: clip(groundPrimitives(setting))
      },
      {
        id: "foreground",
        kind: "inline-palette-rectangles",
        rectangles: clip(foregroundPrimitives())
      }
    ],
    layers: {
      background: { order: 0, assetId: "background" },
      ground: { order: 1, assetId: "ground" },
      foreground: { order: 3, assetId: "foreground" }
    },
    depth: { order: 2, sort: "ground-y", actorOffset: 0.25, weatherOrder: 4 },
    zones: {
      placement: [
        setting === "garden" ? { left: 40, right: 920, top: 340, bottom: 510 } : { left: 90, right: 870, top: 355, bottom: 495 }
      ],
      walkable: [
        { left: 70, right: 890, top: 360, bottom: 510 },
        { left: 70, right: 890, top: 520, bottom: 532 }
      ]
    },
    navigation: {
      mode: "flight-corridors",
      groundSlots: Array.from({ length: 24 }, (_, i) => ({
        id: `ground:${Math.floor(i / 8)}:${i % 8}`,
        x: 100 + i % 8 * 108,
        y: 370 + Math.floor(i / 8) * 64
      })),
      roaming: { left: 70, right: 890, top: 375, bottom: 507 },
      overflow: { left: 90, right: 870, y: 525 }
    }
  });
}
function freeze(value) {
  if (value && typeof value === "object") {
    for (const child of Object.values(value)) freeze(child);
    Object.freeze(value);
  }
  return value;
}
var fixtures = freeze({ garden: fixture("garden"), courtyard: fixture("courtyard") });
var SCENE_CATALOG = Object.freeze(Object.values(fixtures));
var fixtureScene = (setting) => fixtures[setting];
var legacyScenePin = (setting) => ({
  id: fixtures[setting].id,
  version: 1
});
function resolveScene(setting, pin, catalog = SCENE_CATALOG) {
  const requested = pin ?? legacyScenePin(setting);
  const candidates = catalog.filter(
    (entry) => !!entry && typeof entry === "object" && "id" in entry && "version" in entry && entry.id === requested.id && entry.version === requested.version
  );
  const parsed = candidates.length === 1 ? sceneManifestSchema.safeParse(candidates[0]) : void 0;
  const ready = scenePinSchema.safeParse(requested).success && parsed?.success && parsed.data.publicSceneId === setting;
  const manifest = ready && parsed?.success ? parsed.data : fixtureScene(setting);
  const status = ready ? "ready" : "unavailable";
  return {
    requested: { ...requested },
    manifest,
    status,
    message: ready ? `${manifest.label}. Regional artwork is not reviewed.` : "Selected scene manifest is unavailable or invalid. Showing the existing technical fixture; your saved scene selection is retained.",
    key: JSON.stringify([requested, status, manifest])
  };
}

// birdsong-yard-sprites/src/lib/server/storage/repository.ts
import { z as z11 } from "zod";
import { DatabaseSync } from "node:sqlite";
import { randomUUID, createHash } from "node:crypto";
import { mkdirSync } from "node:fs";
import { dirname } from "node:path";

// birdsong-yard-sprites/src/lib/domain/yard.ts
import { z as z9 } from "zod";

// birdsong-yard-sprites/src/lib/assets/manifest-v2.ts
import { z as z3 } from "zod";
var animationStates = [
  "idle",
  "moving",
  "perching",
  "singing",
  "feeding",
  "bathing",
  "sleeping",
  "playing",
  "nesting"
];
var identifier = z3.string().min(1).max(160);
var integer = z3.number().int().nonnegative();
var animationPinSchema = z3.object({
  jobId: identifier,
  artifactId: identifier,
  version: z3.number().int().positive().max(Number.MAX_SAFE_INTEGER),
  contentDigest: z3.string().regex(/^[a-f0-9]{64}$/)
}).strict();
var rectangle = z3.object({
  x: integer,
  y: integer,
  width: z3.number().int().min(1).max(256),
  height: z3.number().int().min(1).max(256),
  color: z3.number().int().min(0).max(16777215)
}).strict();
var clip2 = z3.object({
  frames: z3.array(integer).min(1).max(256),
  ticksPerFrame: z3.number().int().min(1).max(300),
  loop: z3.boolean(),
  /** Optional authored pose transform, also frozen to the first pose in quiet mode. */
  rotations: z3.array(z3.number().min(-0.5).max(0.5)).max(256).optional()
}).strict();
var speciesManifestV2Schema = z3.object({
  schemaVersion: z3.literal(2),
  speciesId: identifier,
  representation: z3.string().min(1).max(200),
  fixture: z3.boolean(),
  taxonFidelityReviewed: z3.boolean(),
  format: z3.literal("pixel-rects"),
  canvas: z3.object({
    width: z3.number().int().min(1).max(256),
    height: z3.number().int().min(1).max(256),
    anchorX: integer,
    anchorY: integer
  }).strict(),
  frames: z3.array(z3.array(rectangle).min(1).max(4096)).min(1).max(64),
  clips: z3.object(
    Object.fromEntries(
      animationStates.map((state) => [state, state === "idle" ? clip2 : clip2.optional()])
    )
  ).strict(),
  provenance: z3.object({
    source: z3.enum(["deterministic_fixture", "provider", "user_upload"]),
    creator: identifier,
    sourceVersion: identifier,
    references: z3.array(identifier).max(32),
    license: z3.string().min(1).max(200),
    usage: z3.enum(["development-only", "cleared"]),
    attribution: z3.string().min(1).max(300)
  }).strict()
}).strict().superRefine((value, context2) => {
  const fail = (message) => context2.addIssue({ code: "custom", message });
  if (value.canvas.anchorX > value.canvas.width || value.canvas.anchorY > value.canvas.height)
    fail("Anchor exceeds canvas bounds");
  if (value.frames.reduce((sum, frame) => sum + frame.length, 0) > 16384)
    fail("Manifest exceeds total rectangle budget");
  if (value.frames.some(
    (frame) => frame.some(
      (rect) => rect.x + rect.width > value.canvas.width || rect.y + rect.height > value.canvas.height
    )
  ))
    fail("Frame exceeds canvas bounds");
  for (const entry of Object.values(value.clips)) {
    if (!entry) continue;
    if (entry.frames.some((index) => index >= value.frames.length))
      fail("Clip frame index exceeds frame count");
    if (entry.rotations && entry.rotations.length !== entry.frames.length)
      fail("Clip pose count must match frames");
  }
  if (value.fixture && (value.taxonFidelityReviewed || value.provenance.source !== "deterministic_fixture" || value.provenance.usage !== "development-only"))
    fail("Fixture cannot claim fidelity review or cleared production usage");
  if (!value.fixture && (!value.taxonFidelityReviewed || value.provenance.source === "deterministic_fixture" || value.provenance.usage !== "cleared"))
    fail("Non-fixture art requires fidelity review and cleared usage");
});

// birdsong-yard-sprites/src/lib/assets/catalog-pin.ts
import { z as z4 } from "zod";
var catalogPinSchema = z4.object({
  catalogKey: z4.string().regex(/^[a-f0-9]{64}$/),
  releaseVersion: z4.number().int().min(1).max(Number.MAX_SAFE_INTEGER),
  renderSha256: z4.string().regex(/^[a-f0-9]{64}$/)
}).strict();

// birdsong-yard-sprites/src/lib/domain/evidence.ts
import { z as z5 } from "zod";
var evidenceValueSchema = z5.object({
  speciesId: idSchema,
  observedAt: timestampSchema.nullable()
}).strict();
var evidenceRevisionSchema = evidenceValueSchema.extend({
  correctionId: z5.string().uuid().nullable()
}).strict();
var manualFindingSchema = z5.object({
  schemaVersion: z5.literal(1),
  id: z5.string().uuid(),
  speciesId: idSchema,
  observedAt: timestampSchema.nullable(),
  note: z5.string().max(1e3)
}).strict();
var correctionInputSchema = z5.object({
  schemaVersion: z5.literal(1),
  id: z5.string().uuid(),
  eventId: idSchema,
  expected: evidenceRevisionSchema,
  replacement: evidenceValueSchema,
  reason: z5.string().min(1).max(500).regex(/\S/, "Explain the correction.")
}).strict();
var correctionRecordSchema = correctionInputSchema.extend({
  recordedAt: timestampSchema
}).strict();
var findingCommandSchema = z5.discriminatedUnion("action", [
  z5.object({ action: z5.literal("manual-finding"), finding: manualFindingSchema }).strict(),
  z5.object({
    action: z5.literal("correct-events"),
    corrections: z5.array(correctionInputSchema).min(1).max(100)
  }).strict()
]);
var effectiveEvidenceSchema = evidenceRevisionSchema.extend({ eventId: idSchema }).strict();
var sameValue = (a, b) => a.speciesId === b.speciesId && (a.observedAt === b.observedAt || a.observedAt !== null && b.observedAt !== null && Date.parse(a.observedAt) === Date.parse(b.observedAt));
var sameRevision = (a, b) => a.correctionId === b.correctionId && sameValue(a, b);

// birdsong-yard-sprites/src/lib/domain/scene.ts
import { z as z6 } from "zod";

// birdsong-yard-sprites/src/lib/domain/validation-error.ts
var messages = {
  objectPlacement: "Objects must fit inside the yard ground area without overlapping other objects.",
  sceneCapacity: "This yard has no collision-free placement for all objects.",
  legacySpeciesIdentity: "Legacy species key mismatch",
  legacyArtworkIdentity: "Legacy artwork identity mismatch"
};
var YardValidationError = class extends Error {
  code = "INVALID";
  constructor(reason) {
    super(messages[reason]);
    this.name = "YardValidationError";
  }
};

// birdsong-yard-sprites/src/lib/domain/scene.ts
var sceneManifestOf = (input) => typeof input === "string" ? fixtureScene(input) : input;
var MAX_OBJECTS = 12;
var OBJECT_CLEARANCE = 8;
var objectKindSchema = z6.enum(["perch", "feeder", "bath", "nest"]);
var OBJECT_CATALOG = {
  perch: {
    label: "Perch",
    width: 96,
    depth: 30,
    height: 130,
    slots: [
      { id: "left", affordance: "perch", dx: -25, dy: -115 },
      { id: "right", affordance: "perch", dx: 25, dy: -115, capability: "play" }
    ]
  },
  feeder: {
    label: "Feeder",
    width: 84,
    depth: 46,
    height: 74,
    slots: [
      { id: "left", affordance: "feed", dx: -18, dy: -24 },
      { id: "right", affordance: "feed", dx: 18, dy: -24 }
    ]
  },
  bath: {
    label: "Birdbath",
    width: 100,
    depth: 54,
    height: 80,
    slots: [
      { id: "left", affordance: "bath", dx: -18, dy: -68 },
      { id: "right", affordance: "bath", dx: 18, dy: -68 }
    ]
  },
  nest: {
    label: "Nest",
    width: 72,
    depth: 36,
    height: 50,
    slots: [{ id: "center", affordance: "nest", dx: 0, dy: -30, capability: "nest-building" }]
  }
};
var yardObjectSchema = z6.object({
  id: idSchema,
  kind: objectKindSchema,
  x: z6.number().finite().min(0).max(WORLD_WIDTH),
  y: z6.number().finite().min(0).max(WORLD_HEIGHT)
}).strict();
var yardObjectsSchema = z6.array(yardObjectSchema).max(MAX_OBJECTS).superRefine((objects, ctx) => {
  if (new Set(objects.map((object) => object.id)).size !== objects.length)
    ctx.addIssue({ code: "custom", message: "Yard object IDs must be unique." });
});
var placementSnapshotSchema = z6.object({
  scene: sceneSettingSchema,
  scenePin: scenePinSchema.nullable().optional(),
  objects: yardObjectsSchema
}).strict();
function placementKey(scene, objects, pin) {
  return JSON.stringify([
    scene,
    pin ?? legacyScenePin(scene),
    [...objects].sort((a, b) => a.id.localeCompare(b.id)).map(({ id: id8, kind, x, y }) => [id8, kind, x, y])
  ]);
}
var PLACEMENT_BOUNDS = {
  garden: placementBounds("garden"),
  courtyard: placementBounds("courtyard")
};
function placementBounds(setting) {
  const first = fixtureScene(setting).zones.placement[0];
  if (!first) throw new Error("Fixture scene requires a placement zone");
  return first;
}
function objectFootprint(object) {
  const definition = OBJECT_CATALOG[object.kind];
  return {
    left: object.x - definition.width / 2,
    right: object.x + definition.width / 2,
    top: object.y - definition.depth / 2,
    bottom: object.y + definition.depth / 2
  };
}
function objectsOverlap(first, second) {
  const a = objectFootprint(first), b = objectFootprint(second);
  return a.left < b.right + OBJECT_CLEARANCE && a.right + OBJECT_CLEARANCE > b.left && a.top < b.bottom + OBJECT_CLEARANCE && a.bottom + OBJECT_CLEARANCE > b.top;
}
function isPlacementValid(object, objects, setting) {
  const manifest = sceneManifestOf(setting), bounds = objectFootprint(object);
  return manifest.zones.placement.some((area) => containsBounds(area, bounds)) && object.y - OBJECT_CATALOG[object.kind].height >= 24 && !objects.some((other) => other.id !== object.id && objectsOverlap(object, other));
}
function validateObjects(input, setting) {
  const objects = yardObjectsSchema.parse(input);
  for (const object of objects)
    if (!isPlacementValid(object, objects, setting))
      throw new YardValidationError("objectPlacement");
  return objects;
}
function defaultObjects(setting = "garden") {
  const objects = [
    { id: "fixture-perch", kind: "perch", x: 180, y: 420 },
    { id: "fixture-feeder", kind: "feeder", x: 400, y: 465 },
    { id: "fixture-bath", kind: "bath", x: 700, y: 445 },
    { id: "fixture-nest", kind: "nest", x: 820, y: 475 }
  ];
  return validateObjects(objects, setting);
}
function placementCandidates(kind, setting, desired) {
  const definition = OBJECT_CATALOG[kind];
  const candidates = [];
  const clamp = (value, min, max) => Math.min(max, Math.max(min, value));
  for (const area of sceneManifestOf(setting).zones.placement) {
    const minX = area.left + definition.width / 2, maxX = area.right - definition.width / 2;
    const minY = area.top + definition.depth / 2, maxY = area.bottom - definition.depth / 2;
    if (minX > maxX || minY > maxY) continue;
    candidates.push({ x: clamp(desired.x, minX, maxX), y: clamp(desired.y, minY, maxY) });
    for (let y = minY; y <= maxY; y += 8)
      for (let x = minX; x <= maxX; x += 8) candidates.push({ x, y });
  }
  return candidates.sort(
    (a, b) => (a.x - desired.x) ** 2 + (a.y - desired.y) ** 2 - ((b.x - desired.x) ** 2 + (b.y - desired.y) ** 2) || a.y - b.y || a.x - b.x
  );
}
function findObjectPlacement(kind, objects, setting, desired = { x: WORLD_WIDTH / 2, y: 430 }) {
  objectKindSchema.parse(kind);
  for (const point3 of placementCandidates(kind, setting, desired)) {
    const candidate = { id: "placement-candidate", kind, ...point3 };
    if (isPlacementValid(
      candidate,
      objects.filter((object) => object.id !== "placement-candidate"),
      setting
    ) && !objects.some((other) => objectsOverlap(candidate, other)))
      return point3;
  }
  return null;
}
function reanchorObjects(input, setting) {
  const objects = yardObjectsSchema.parse(input);
  let placed = objects.filter((object) => isPlacementValid(object, objects, setting));
  const retained = new Set(placed.map((object) => object.id));
  const ordered = [...objects].sort(
    (a, b) => OBJECT_CATALOG[b.kind].width * OBJECT_CATALOG[b.kind].depth - OBJECT_CATALOG[a.kind].width * OBJECT_CATALOG[a.kind].depth || a.id.localeCompare(b.id)
  );
  for (const object of ordered) {
    if (retained.has(object.id)) continue;
    const position = findObjectPlacement(object.kind, placed, setting, object);
    if (!position) {
      placed = [];
      break;
    }
    placed.push({ ...object, ...position });
  }
  if (placed.length !== objects.length) {
    const areas = sceneManifestOf(setting).zones.placement;
    const width = Math.max(...Object.values(OBJECT_CATALOG).map((definition) => definition.width));
    const depth = Math.max(...Object.values(OBJECT_CATALOG).map((definition) => definition.depth));
    const cells = [];
    for (const bounds of areas)
      for (let y = bounds.top + depth / 2; y <= bounds.bottom - depth / 2; y += depth + OBJECT_CLEARANCE)
        for (let x = bounds.left + width / 2; x <= bounds.right - width / 2; x += width + OBJECT_CLEARANCE)
          cells.push({ x, y });
    for (const object of ordered) {
      cells.sort(
        (a, b) => (a.x - object.x) ** 2 + (a.y - object.y) ** 2 - ((b.x - object.x) ** 2 + (b.y - object.y) ** 2) || a.y - b.y || a.x - b.x
      );
      const position = cells.find(
        (point3) => isPlacementValid({ ...object, ...point3 }, placed, setting)
      );
      if (!position) throw new YardValidationError("sceneCapacity");
      placed.push({ ...object, ...position });
    }
  }
  const byId = new Map(placed.map((object) => [object.id, object]));
  return validateObjects(
    objects.map((object) => byId.get(object.id)),
    setting
  );
}

// birdsong-yard-sprites/src/lib/domain/object-inventory.ts
import { z as z7 } from "zod";
var FREE_FIXTURES_PER_KIND = 3;
var MAX_OBJECT_OPERATION_RECEIPTS = 4096;
var objectInventorySchema = z7.object({
  version: z7.literal(1),
  owned: z7.object({
    perch: z7.number().int().min(0).max(MAX_OBJECTS),
    feeder: z7.number().int().min(0).max(MAX_OBJECTS),
    bath: z7.number().int().min(0).max(MAX_OBJECTS),
    nest: z7.number().int().min(0).max(MAX_OBJECTS)
  }).strict()
}).strict();
var objectOperationReceiptSchema = z7.object({
  requestId: z7.string().uuid(),
  commandDigest: z7.string().regex(/^[a-f0-9]{64}$/),
  resultObjectId: idSchema
}).strict();
var objectOperationReceiptsSchema = z7.array(objectOperationReceiptSchema).max(MAX_OBJECT_OPERATION_RECEIPTS).superRefine((receipts, context2) => {
  if (new Set(receipts.map((receipt) => receipt.requestId)).size !== receipts.length)
    context2.addIssue({ code: "custom", message: "Object operation request IDs must be unique." });
});
var objectInventoryCommandSchema = z7.object({
  action: z7.literal("object-inventory"),
  requestId: z7.string().uuid(),
  expected: placementSnapshotSchema,
  payload: z7.discriminatedUnion("operation", [
    z7.object({ operation: z7.literal("place"), kind: objectKindSchema }).strict(),
    z7.object({ operation: z7.literal("return"), objectId: idSchema }).strict(),
    z7.object({
      operation: z7.literal("move"),
      objectId: idSchema,
      x: z7.number().finite(),
      y: z7.number().finite()
    }).strict()
  ])
}).strict();
function starterInventory(objects) {
  const placed = yardObjectsSchema.parse(objects);
  const owned = { perch: 3, feeder: 3, bath: 3, nest: 3 };
  for (const kind of objectKindSchema.options)
    owned[kind] = Math.max(
      FREE_FIXTURES_PER_KIND,
      placed.filter((item) => item.kind === kind).length
    );
  return { version: 1, owned };
}
function inventoryIssues(inventory, objects) {
  return objectKindSchema.options.filter((kind) => availableStock(inventory, objects, kind) < 0).map((kind) => `Placed ${kind} objects exceed owned stock.`);
}
function availableStock(inventory, objects, kind) {
  return inventory.owned[kind] - objects.filter((object) => object.kind === kind).length;
}

// birdsong-yard-sprites/src/lib/weather/contracts.ts
import { z as z8 } from "zod";
var weatherConditionSchema = z8.enum(["clear", "cloudy", "rain", "snow"]);
var weatherSettingsSchema = z8.object({
  mode: z8.enum(["simulated", "manual", "real"]),
  manual: z8.object({
    condition: weatherConditionSchema,
    hour: z8.number().int().min(0).max(23)
  }).strict(),
  simulation: z8.object({
    seed: z8.number().int().safe(),
    dayLengthSeconds: z8.number().int().min(120).max(86400),
    epoch: z8.string().datetime()
  }).strict()
}).strict();
function defaultWeatherSettings() {
  return {
    mode: "simulated",
    manual: { condition: "clear", hour: 12 },
    simulation: {
      seed: 17,
      dayLengthSeconds: 600,
      epoch: "2026-01-01T00:00:00Z"
    }
  };
}

// birdsong-yard-sprites/src/lib/domain/yard.ts
var jsonValueSchema = z9.lazy(
  () => z9.union([
    z9.string(),
    z9.number().finite(),
    z9.boolean(),
    z9.null(),
    z9.array(jsonValueSchema),
    z9.record(jsonValueSchema)
  ])
);
var speciesSchema = z9.object({
  id: idSchema,
  commonName: z9.string().min(1).max(120),
  scientificName: z9.string().min(3).max(160),
  description: z9.string().max(1e3).optional(),
  referencePhoto: z9.record(jsonValueSchema).optional()
}).strict();
var sourceSchema = z9.object({
  kind: z9.enum(["fixture", "manual", "model", "external"]),
  label: z9.string().min(1).max(120),
  sourceEventId: idSchema,
  provider: z9.string().min(1).max(100).optional(),
  modelVersion: z9.string().max(100).optional()
}).strict();
var identificationSchema = z9.object({
  schemaVersion: z9.literal(2),
  id: idSchema,
  species: speciesSchema,
  observedAt: timestampSchema.nullable(),
  ingestedAt: timestampSchema,
  source: sourceSchema,
  confidence: z9.number().min(0).max(1).optional(),
  recordingId: idSchema.optional(),
  /** Private evidence only. Never copy this object into a public projection. */
  metadata: z9.record(jsonValueSchema).optional()
}).strict();
var importEventSchema = identificationSchema.omit({ ingestedAt: true }).extend({ ingestedAt: timestampSchema.optional() });
var hasControlCharacters = (value) => Array.from(value).some(
  (character) => character.charCodeAt(0) < 32 || character.charCodeAt(0) === 127
);
var localImageSchema = z9.string().max(15e5).refine(
  (value) => value.startsWith("/") && !value.startsWith("//") && !/[\\\s]/.test(value) && !hasControlCharacters(value) || /^data:image\/(png|jpeg|webp);base64,[a-zA-Z0-9+/=]+$/.test(value),
  "Use a bundled image path or embedded PNG, JPEG or WebP image; remote image requests are disabled."
);
var artworkObjectSchema = z9.object({
  id: idSchema,
  speciesId: idSchema,
  version: z9.number().int().positive(),
  status: z9.enum(["fixture", "reviewed"]),
  /** Optional exact pipeline artifact; old backups and image-only art remain valid. */
  animationPin: animationPinSchema.optional(),
  /** Exact generic shared release; never a private job or an individual bird identity. */
  catalogPin: catalogPinSchema.optional(),
  imageUrl: localImageSchema,
  sha256: z9.string().regex(/^[a-f0-9]{64}$/).optional(),
  representation: z9.string().min(1).max(200),
  provenance: z9.record(jsonValueSchema),
  /** Only explicit catalog keys can cross the public boundary; URLs cannot. */
  catalogKey: z9.enum(["fixture-robin", "fixture-sparrow", "fixture-bluejay"]).optional()
}).strict();
var artworkSchema = artworkObjectSchema.superRefine((artwork, context2) => {
  if (artwork.catalogPin && (artwork.animationPin || artwork.catalogKey))
    context2.addIssue({
      code: "custom",
      message: "Shared, private and bundled asset pins cannot be mixed."
    });
});
var birdInstanceSchema = z9.object({
  id: idSchema,
  speciesId: idSchema,
  name: z9.string().trim().min(1).max(60).nullable(),
  lifecycle: z9.enum(["temporary", "permanent", "expired"]),
  createdAt: timestampSchema,
  expiresAt: timestampSchema.nullable(),
  promotedAt: timestampSchema.nullable(),
  artworkId: idSchema.nullable(),
  originEventId: idSchema.nullable()
}).strict();
var collectionEntrySchema = z9.object({ id: idSchema, speciesId: idSchema, collectedAt: timestampSchema }).strict();
var preferencesSchema = z9.object({
  palette: z9.enum(["twilight", "fieldnotes", "moonlit"]),
  scene: sceneSettingSchema,
  scenePin: scenePinSchema.nullable().default(null),
  regionPreference: regionPreferenceSchema.default("unspecified"),
  reducedMotion: z9.boolean(),
  /** Provisional development default; changing it affects future imports only. */
  visitorTtlHours: z9.number().int().min(1).max(24 * 90)
}).strict();
var preferencesPatchSchema = preferencesSchema.partial();
var defaultPreferences = () => ({
  palette: "twilight",
  scene: "garden",
  scenePin: null,
  regionPreference: "unspecified",
  reducedMotion: false,
  visitorTtlHours: 24
});
var environmentSchema = z9.object({
  version: z9.literal(1),
  objects: yardObjectsSchema,
  weather: weatherSettingsSchema,
  inventory: objectInventorySchema,
  objectReceipts: objectOperationReceiptsSchema
}).strict();
var persistedEnvironmentSchema = environmentSchema.extend({
  inventory: objectInventorySchema.optional(),
  objectReceipts: objectOperationReceiptsSchema.optional()
}).transform((environment) => ({
  ...environment,
  inventory: environment.inventory ?? starterInventory(environment.objects),
  objectReceipts: environment.objectReceipts ?? []
}));
var defaultEnvironment = () => ({
  version: 1,
  objects: defaultObjects(),
  weather: defaultWeatherSettings(),
  inventory: starterInventory(defaultObjects()),
  objectReceipts: []
});
var yardDataSchema = z9.object({
  version: z9.literal(2),
  species: z9.array(speciesSchema),
  events: z9.array(identificationSchema),
  /** Additive v2 extension; raw events never change when corrections are appended. */
  corrections: z9.array(correctionRecordSchema).max(1e4).default([]),
  collection: z9.array(collectionEntrySchema),
  birds: z9.array(birdInstanceSchema),
  artworks: z9.array(artworkSchema),
  preferences: preferencesSchema,
  /** Additive v2 extension: older persisted yards/backups receive fresh, stable defaults. */
  environment: persistedEnvironmentSchema.default(defaultEnvironment)
}).strict().superRefine((state, ctx) => {
  const fail = (message) => ctx.addIssue({ code: "custom", message });
  for (const issue of inventoryIssues(state.environment.inventory, state.environment.objects))
    fail(issue);
  try {
    validateObjects(
      state.environment.objects,
      resolveScene(state.preferences.scene, state.preferences.scenePin).manifest
    );
  } catch {
    fail("Invalid yard object placement for this scene.");
  }
  for (const [label2, values] of Object.entries({
    species: state.species,
    events: state.events,
    corrections: state.corrections,
    collection: state.collection,
    birds: state.birds,
    artworks: state.artworks
  })) {
    if (new Set(values.map((value) => value.id)).size !== values.length)
      fail(`Duplicate ${label2} ID`);
  }
  const species = new Map(state.species.map((s) => [s.id, s]));
  const art = new Map(state.artworks.map((a) => [a.id, a]));
  if (new Set(state.species.map((s) => s.scientificName.toLowerCase())).size !== state.species.length)
    fail("Duplicate taxon identity");
  if (new Set(state.events.map(sourceEventKey)).size !== state.events.length)
    fail("Duplicate source event identity");
  if (new Set(state.collection.map((entry) => entry.speciesId)).size !== state.collection.length)
    fail("Duplicate collection species");
  if (new Set(state.artworks.map((a) => `${a.speciesId}:${a.version}`)).size !== state.artworks.length)
    fail("Duplicate artwork version");
  for (const event of state.events)
    if (species.get(event.species.id)?.scientificName !== event.species.scientificName)
      fail("Evidence taxon mismatch");
  const revisions = new Map(
    state.events.map((event) => [
      event.id,
      {
        eventId: event.id,
        correctionId: null,
        speciesId: event.species.id,
        observedAt: event.observedAt
      }
    ])
  );
  for (const correction of state.corrections) {
    const previous = revisions.get(correction.eventId);
    if (!previous || !sameRevision(previous, correction.expected))
      fail("Correction history must be an unbroken append-only chain.");
    if (!species.has(correction.replacement.speciesId)) fail("Corrected species missing");
    revisions.set(correction.eventId, {
      eventId: correction.eventId,
      correctionId: correction.id,
      ...correction.replacement
    });
  }
  for (const entry of [...state.collection, ...state.birds, ...state.artworks])
    if (!species.has(entry.speciesId)) fail("Referenced species missing");
  for (const bird of state.birds) {
    if (bird.artworkId && art.get(bird.artworkId)?.speciesId !== bird.speciesId)
      fail("Pinned artwork taxon mismatch");
    if (bird.originEventId && !state.events.some((event) => event.id === bird.originEventId))
      fail("Origin event missing");
    if (bird.lifecycle === "permanent" && bird.expiresAt !== null)
      fail("Permanent birds cannot expire");
    if (bird.lifecycle !== "permanent" && bird.expiresAt === null)
      fail("Temporary birds require expiry");
  }
});
var findingSchema = z9.object({
  id: z9.string().min(1).max(168),
  speciesId: idSchema,
  eventIds: z9.array(idSchema).min(1),
  evidenceCount: z9.number().int().positive().max(Number.MAX_SAFE_INTEGER),
  firstObservedAt: timestampSchema.nullable(),
  lastObservedAt: timestampSchema.nullable(),
  sourceKinds: z9.array(sourceSchema.shape.kind).min(1),
  hasUnknownTime: z9.boolean()
}).strict();
var snapshotProjectionSchema = z9.object({
  findings: z9.array(findingSchema),
  effectiveEvidence: z9.array(effectiveEvidenceSchema)
}).strict();
var emptyYard = () => ({
  version: 2,
  species: [],
  events: [],
  corrections: [],
  collection: [],
  birds: [],
  artworks: [],
  preferences: defaultPreferences(),
  environment: defaultEnvironment()
});
function sourceEventKey(event) {
  return JSON.stringify([
    event.source.kind,
    event.source.provider ?? "",
    event.source.sourceEventId
  ]);
}
function canonicalJson(value) {
  if (Array.isArray(value)) return `[${value.map(canonicalJson).join(",")}]`;
  if (value && typeof value === "object")
    return `{${Object.keys(value).filter((key) => value[key] !== void 0).sort().map(
      (key) => `${JSON.stringify(key)}:${canonicalJson(value[key])}`
    ).join(",")}}`;
  return JSON.stringify(value) ?? "null";
}
function evidenceFingerprint(event) {
  const evidence = Object.fromEntries(
    Object.entries(event).filter(([key]) => key !== "ingestedAt")
  );
  return canonicalJson(evidence);
}
function effectiveEvidenceOf(data) {
  const latest = new Map(data.corrections.map((correction) => [correction.eventId, correction]));
  return data.events.map((event) => {
    const correction = latest.get(event.id);
    return {
      eventId: event.id,
      correctionId: correction?.id ?? null,
      ...correction?.replacement ?? { speciesId: event.species.id, observedAt: event.observedAt }
    };
  });
}
function snapshotOf(data, now) {
  const groups = /* @__PURE__ */ new Map();
  const effectiveEvidence = effectiveEvidenceOf(data);
  const effective = new Map(effectiveEvidence.map((entry) => [entry.eventId, entry]));
  for (const event of data.events) {
    const value = effective.get(event.id);
    const finding = groups.get(value.speciesId) ?? {
      id: `finding:${value.speciesId}`,
      speciesId: value.speciesId,
      eventIds: [],
      evidenceCount: 0,
      firstObservedAt: null,
      lastObservedAt: null,
      sourceKinds: [],
      hasUnknownTime: false
    };
    finding.eventIds.push(event.id);
    finding.evidenceCount++;
    if (!finding.sourceKinds.includes(event.source.kind))
      finding.sourceKinds.push(event.source.kind);
    if (value.observedAt === null) finding.hasUnknownTime = true;
    else {
      if (!finding.firstObservedAt || Date.parse(value.observedAt) < Date.parse(finding.firstObservedAt))
        finding.firstObservedAt = value.observedAt;
      if (!finding.lastObservedAt || Date.parse(value.observedAt) > Date.parse(finding.lastObservedAt))
        finding.lastObservedAt = value.observedAt;
    }
    groups.set(value.speciesId, finding);
  }
  return {
    ...data,
    effectiveEvidence,
    birds: data.birds.map(
      (bird) => bird.lifecycle === "temporary" && Date.parse(bird.expiresAt) <= Date.parse(now) ? { ...bird, lifecycle: "expired" } : bird
    ),
    findings: [...groups.values()]
  };
}
var yardSnapshotSchema = yardDataSchema.innerType().extend({
  ...snapshotProjectionSchema.shape,
  environment: environmentSchema,
  corrections: yardDataSchema.innerType().shape.corrections.removeDefault(),
  preferences: preferencesSchema.extend({
    scenePin: preferencesSchema.shape.scenePin.removeDefault(),
    regionPreference: preferencesSchema.shape.regionPreference.removeDefault()
  }).strict()
}).strict().superRefine((snapshot, context2) => {
  const { findings, effectiveEvidence, ...raw } = snapshot;
  const parsed = yardDataSchema.safeParse(raw);
  if (!parsed.success) {
    for (const issue of parsed.error.issues) context2.addIssue(issue);
    return;
  }
  const expected = snapshotOf(parsed.data, "1970-01-01T00:00:00.000Z");
  if (canonicalJson(findings) !== canonicalJson(expected.findings))
    context2.addIssue({
      code: "custom",
      path: ["findings"],
      message: "Findings do not match saved evidence."
    });
  if (canonicalJson(effectiveEvidence) !== canonicalJson(expected.effectiveEvidence))
    context2.addIssue({
      code: "custom",
      path: ["effectiveEvidence"],
      message: "Effective evidence does not match correction history."
    });
});
var backupSchema = z9.object({
  format: z9.literal("chirpneighbors-yard"),
  version: z9.literal(2),
  exportedAt: timestampSchema,
  data: yardDataSchema
}).strict();
var displayCatalog = {
  "cn-species-erithacus-rubecula": {
    commonName: "European Robin",
    scientificName: "Erithacus rubecula",
    catalogKey: "fixture-robin"
  },
  "cn-species-passer-domesticus": {
    commonName: "House Sparrow",
    scientificName: "Passer domesticus",
    catalogKey: "fixture-sparrow"
  },
  "cn-species-cyanocitta-cristata": {
    commonName: "Blue Jay",
    scientificName: "Cyanocitta cristata",
    catalogKey: "fixture-bluejay"
  }
};
function catalogEntry(speciesId) {
  return Object.hasOwn(displayCatalog, speciesId) ? displayCatalog[speciesId] : void 0;
}
function availableSpecies(data) {
  const choices = data.species.map(({ id: id8, commonName, scientificName: scientificName2 }) => ({
    id: id8,
    commonName,
    scientificName: scientificName2
  }));
  for (const [id8, species] of Object.entries(displayCatalog)) {
    if (!choices.some(
      (entry) => entry.id === id8 || entry.scientificName.toLowerCase() === species.scientificName.toLowerCase()
    ))
      choices.push({ id: id8, commonName: species.commonName, scientificName: species.scientificName });
  }
  return choices;
}
var publicYardProjectionSchema = z9.object({
  version: z9.literal(1),
  viewOnly: z9.literal(true),
  scene: sceneSettingSchema,
  palette: preferencesSchema.shape.palette,
  birds: z9.array(
    z9.object({
      displayKey: z9.string().regex(/^bird-[1-9][0-9]*$/),
      commonName: speciesSchema.shape.commonName,
      scientificName: speciesSchema.shape.scientificName.nullable(),
      catalogKey: artworkObjectSchema.shape.catalogKey.unwrap().nullable()
    }).strict()
  )
}).strict();

// birdsong-yard-sprites/src/lib/domain/migration.ts
import { z as z10 } from "zod";
var legacyPhoto = z10.object({
  id: idSchema,
  speciesId: idSchema,
  creator: z10.string().min(1),
  sourceUrl: z10.string().url(),
  license: z10.enum(["CC0-1.0", "CC-BY-4.0", "CC-BY-SA-4.0", "user-owned"]),
  licenseUrl: z10.string().url(),
  verifiedAt: timestampSchema,
  representation: z10.string().min(1),
  imageUrl: z10.string().optional(),
  sha256: z10.string().optional()
}).strict();
var legacySpecies = z10.object({
  id: idSchema,
  commonName: z10.string().min(1).max(120),
  scientificName: z10.string().min(3).max(160),
  description: z10.string().max(1e3).optional(),
  referencePhoto: legacyPhoto.optional()
}).strict();
var legacySchema = z10.object({
  version: z10.literal(1),
  species: z10.record(legacySpecies),
  identifications: z10.array(
    z10.object({
      schemaVersion: z10.literal(1),
      id: idSchema,
      species: legacySpecies,
      observedAt: timestampSchema,
      source: z10.object({
        kind: z10.enum(["audio", "manual", "import", "demo"]),
        label: z10.string().min(1).max(120)
      }).strict(),
      confidence: z10.number().min(0).max(1).optional(),
      recordingUrl: z10.string().optional()
    }).strict()
  ),
  residents: z10.array(
    z10.object({
      id: idSchema,
      speciesId: idSchema,
      savedAt: timestampSchema,
      artworkId: idSchema.nullable()
    }).strict()
  ),
  artworks: z10.record(
    z10.object({
      id: idSchema,
      speciesId: idSchema,
      version: z10.number().int().positive(),
      referencePhoto: legacyPhoto,
      representation: z10.string().min(1).max(200),
      imageUrl: z10.string(),
      sha256: z10.string().regex(/^[a-f0-9]{64}$/),
      reviewedAt: timestampSchema,
      method: z10.literal("reviewed-upload")
    }).strict()
  ),
  preferences: z10.object({
    palette: z10.enum(["twilight", "fieldnotes", "moonlit"]),
    reducedMotion: z10.boolean()
  }).strict()
}).strict();
function migrateV1(input, now = (/* @__PURE__ */ new Date()).toISOString()) {
  timestampSchema.parse(now);
  const legacy2 = legacySchema.parse(input);
  for (const [key, species] of Object.entries(legacy2.species))
    if (key !== species.id) throw new YardValidationError("legacySpeciesIdentity");
  for (const [key, art] of Object.entries(legacy2.artworks))
    if (key !== art.id || art.referencePhoto.speciesId !== art.speciesId)
      throw new YardValidationError("legacyArtworkIdentity");
  const stripSpecies = (species) => species;
  return yardDataSchema.parse({
    version: 2,
    species: Object.values(legacy2.species).map(stripSpecies),
    events: legacy2.identifications.map((event) => ({
      schemaVersion: 2,
      id: event.id,
      species: stripSpecies(event.species),
      observedAt: event.observedAt,
      ingestedAt: now,
      source: {
        kind: event.source.kind === "demo" ? "fixture" : event.source.kind === "manual" ? "manual" : "external",
        label: event.source.label,
        provider: "legacy-v1",
        sourceEventId: event.id
      },
      ...event.confidence === void 0 ? {} : { confidence: event.confidence },
      metadata: {
        legacySourceKind: event.source.kind,
        ...event.recordingUrl ? { legacyRecordingUrl: event.recordingUrl } : {},
        ...event.species.referencePhoto ? { referencePhoto: event.species.referencePhoto } : {}
      }
    })),
    collection: legacy2.residents.map((bird) => ({
      id: bird.id,
      speciesId: bird.speciesId,
      collectedAt: bird.savedAt
    })),
    birds: legacy2.residents.map((bird) => ({
      id: bird.id,
      speciesId: bird.speciesId,
      name: null,
      lifecycle: "permanent",
      createdAt: bird.savedAt,
      promotedAt: bird.savedAt,
      expiresAt: null,
      artworkId: bird.artworkId,
      originEventId: null
    })),
    artworks: Object.values(legacy2.artworks).map(
      (art) => artworkSchema.parse({
        id: art.id,
        speciesId: art.speciesId,
        version: art.version,
        status: "reviewed",
        imageUrl: art.imageUrl,
        sha256: art.sha256,
        representation: art.representation,
        provenance: {
          referencePhoto: art.referencePhoto,
          reviewedAt: art.reviewedAt,
          method: art.method,
          migratedFrom: 1
        }
      })
    ),
    preferences: { ...defaultPreferences(), ...legacy2.preferences }
  });
}

// birdsong-yard-sprites/src/lib/server/storage/repository.ts
var YardError = class extends Error {
  constructor(code, message) {
    super(message);
    this.code = code;
    this.name = "YardError";
  }
  code;
};
var nowIso = () => (/* @__PURE__ */ new Date()).toISOString();
var normalizeNow = (now) => new Date(timestampSchema.parse(now)).toISOString();
var checkOwner = (ownerId) => idSchema.parse(ownerId);
var clone = (value) => structuredClone(value);
var storedYardRowSchema = z11.object({
  schema_version: z11.number().int().positive().safe(),
  data: z11.string()
});
var YardRepository = class {
  constructor(pathOrDatabase, hooks = {}) {
    this.hooks = hooks;
    this.ownsDatabase = typeof pathOrDatabase === "string";
    if (typeof pathOrDatabase === "string") {
      if (pathOrDatabase !== ":memory:") mkdirSync(dirname(pathOrDatabase), { recursive: true });
      this.database = new DatabaseSync(pathOrDatabase);
      this.database.exec("PRAGMA journal_mode = WAL; PRAGMA busy_timeout = 5000;");
    } else this.database = pathOrDatabase;
    this.database.exec(
      "CREATE TABLE IF NOT EXISTS yard_migrations (version INTEGER PRIMARY KEY, applied_at TEXT NOT NULL)"
    );
    const version2 = z11.object({ version: z11.number().int().positive().safe().nullable() }).parse(this.database.prepare("SELECT MAX(version) AS version FROM yard_migrations").get()).version ?? 0;
    if (version2 > 1)
      throw new YardError(
        "SCHEMA_VERSION",
        "Database is newer than this application; downgrade refused."
      );
    if (version2 < 1)
      this.transaction(() => {
        this.database.exec(
          "CREATE TABLE IF NOT EXISTS yard_owners (owner_id TEXT PRIMARY KEY NOT NULL, schema_version INTEGER NOT NULL, data TEXT NOT NULL CHECK(json_valid(data)))"
        );
        this.database.prepare("INSERT OR IGNORE INTO yard_migrations (version, applied_at) VALUES (1, ?)").run(nowIso());
      });
  }
  hooks;
  database;
  ownsDatabase;
  savepointSequence = 0;
  close() {
    if (this.ownsDatabase) this.database.close();
  }
  transaction(action) {
    if (this.database.isTransaction) {
      const name = `yard_operation_${++this.savepointSequence}`;
      this.database.exec(`SAVEPOINT ${name}`);
      try {
        const result2 = action();
        this.database.exec(`RELEASE SAVEPOINT ${name}`);
        return result2;
      } catch (error) {
        this.database.exec(`ROLLBACK TO SAVEPOINT ${name}`);
        this.database.exec(`RELEASE SAVEPOINT ${name}`);
        throw error;
      }
    }
    this.database.exec("BEGIN IMMEDIATE");
    try {
      const result2 = action();
      this.database.exec("COMMIT");
      return result2;
    } catch (error) {
      this.database.exec("ROLLBACK");
      throw error;
    }
  }
  read(ownerId) {
    checkOwner(ownerId);
    const value = this.database.prepare("SELECT schema_version, data FROM yard_owners WHERE owner_id = ?").get(ownerId);
    if (!value) return emptyYard();
    const row = storedYardRowSchema.safeParse(value);
    if (!row.success) throw new Error("Stored yard row is invalid.");
    if (row.data.schema_version !== 2)
      throw new YardError(
        "SCHEMA_VERSION",
        "Unsupported stored yard version; explicit migration required."
      );
    try {
      const data = JSON.parse(row.data.data);
      return yardDataSchema.parse(data);
    } catch {
      throw new Error("Stored yard data is invalid.");
    }
  }
  write(ownerId, state) {
    const validated = yardDataSchema.parse(state);
    const serialized = JSON.stringify(validated);
    if (Buffer.byteLength(serialized) > 16 * 1024 * 1024)
      throw new YardError(
        "INVALID",
        "Development yard limit reached; export before importing more."
      );
    this.database.prepare(
      "INSERT INTO yard_owners (owner_id, schema_version, data) VALUES (?, 2, ?) ON CONFLICT(owner_id) DO UPDATE SET schema_version = 2, data = excluded.data"
    ).run(checkOwner(ownerId), serialized);
  }
  mutate(ownerId, action, afterWrite) {
    checkOwner(ownerId);
    return this.transaction(() => {
      const state = this.read(ownerId);
      const result2 = action(state);
      this.write(ownerId, state);
      this.hooks.changed?.(ownerId, state);
      afterWrite?.(result2);
      return result2;
    });
  }
  snapshot(ownerId, now = nowIso()) {
    return snapshotOf(this.read(ownerId), normalizeNow(now));
  }
  importEvents(ownerId, input, now = nowIso()) {
    const serverNow = normalizeNow(now);
    const batch = Array.isArray(input) ? input : [input];
    if (batch.length > 1e3)
      throw new YardError("INVALID", "Import at most 1000 events per batch.");
    const incoming = batch.map((item) => importEventSchema.parse(item));
    return this.mutate(ownerId, (state) => this.insertEvents(ownerId, state, incoming, serverNow));
  }
  insertEvents(ownerId, state, incoming, serverNow) {
    let inserted = 0;
    let duplicates = 0;
    for (const raw of incoming) {
      const event = { ...raw, ingestedAt: serverNow };
      const existing = state.events.find(
        (item) => item.id === event.id || sourceEventKey(item) === sourceEventKey(event)
      );
      if (existing) {
        if (evidenceFingerprint(existing) !== evidenceFingerprint(event))
          throw new YardError(
            "CONFLICT",
            "An event identity already has different evidence. The whole batch was kept unchanged."
          );
        duplicates++;
        continue;
      }
      const species = state.species.find((item) => item.id === event.species.id);
      if (species && species.scientificName !== event.species.scientificName)
        throw new YardError("CONFLICT", "Species identity conflicts with the existing taxon.");
      if (state.species.some(
        (item) => item.id !== event.species.id && item.scientificName.toLowerCase() === event.species.scientificName.toLowerCase()
      ))
        throw new YardError(
          "CONFLICT",
          "This taxon already has a different ID; resolve taxonomy before importing."
        );
      if (!species) state.species.push(clone(event.species));
      state.events.push(clone(event));
      inserted++;
      this.visit(ownerId, state, event, serverNow);
    }
    return { inserted, duplicates, snapshot: snapshotOf(state, serverNow) };
  }
  knownSpecies(state, speciesId) {
    const species = availableSpecies(state).find((entry) => entry.id === speciesId);
    if (!species) throw new YardError("INVALID", "Select a species from the available catalog.");
    return species;
  }
  addManualFinding(ownerId, input, now = nowIso()) {
    now = normalizeNow(now);
    const finding = manualFindingSchema.parse(input);
    return this.mutate(
      ownerId,
      (state) => {
        const id8 = `manual:${finding.id}`;
        return this.insertEvents(
          ownerId,
          state,
          [
            {
              schemaVersion: 2,
              id: id8,
              species: this.knownSpecies(state, finding.speciesId),
              observedAt: finding.observedAt === null ? null : new Date(finding.observedAt).toISOString(),
              source: { kind: "manual", label: "Manual entry", sourceEventId: id8 },
              metadata: { manualEntryVersion: 1, note: finding.note }
            }
          ],
          now
        );
      },
      (result2) => {
        if (result2.inserted === 1)
          this.hooks.manualInserted?.(ownerId, `manual:${finding.id}`, now);
      }
    );
  }
  /** Appends only; a retry checks its immutable receipt before checking the current revision. */
  correctEvents(ownerId, input, now = nowIso()) {
    now = normalizeNow(now);
    const incoming = correctionInputSchema.array().min(1).max(100).parse(input);
    return this.mutate(ownerId, (state) => {
      let inserted = 0, duplicates = 0;
      for (const correction of incoming) {
        const existing = state.corrections.find((entry) => entry.id === correction.id);
        if (existing) {
          if (canonicalJson({ ...existing, recordedAt: void 0 }) !== canonicalJson(correction))
            throw new YardError(
              "EVIDENCE_CONFLICT",
              "This correction submission already contains different changes. Review the latest history."
            );
          duplicates++;
          continue;
        }
        const current = effectiveEvidenceOf(state).find(
          (entry) => entry.eventId === correction.eventId
        );
        if (!current) throw new YardError("NOT_FOUND", "Observation not found in this yard.");
        if (!sameRevision(current, correction.expected))
          throw new YardError(
            "EVIDENCE_CONFLICT",
            "This observation changed since your draft. Review the latest correction before saving."
          );
        if (sameValue(current, correction.replacement))
          throw new YardError(
            "INVALID",
            "Change the species or observation time before saving a correction."
          );
        const species = this.knownSpecies(state, correction.replacement.speciesId);
        if (!state.species.some((entry) => entry.id === species.id)) state.species.push(species);
        state.corrections.push({ ...correction, recordedAt: now });
        inserted++;
      }
      return { inserted, duplicates, snapshot: snapshotOf(state, now) };
    });
  }
  selectableArtwork(ownerId, artwork, state) {
    return this.hooks.artworkSelectable?.(
      ownerId,
      artwork,
      state.species.find((species) => species.id === artwork.speciesId)
    ) ?? true;
  }
  visit(ownerId, state, event, now) {
    if (!event.observedAt) return;
    const observed = Date.parse(event.observedAt);
    const current = Date.parse(now);
    const expires = observed + state.preferences.visitorTtlHours * 36e5;
    if (observed > current || expires <= current) return;
    const active2 = state.birds.find(
      (bird) => bird.speciesId === event.species.id && (bird.lifecycle === "permanent" || bird.lifecycle === "temporary" && Date.parse(bird.expiresAt) > current)
    );
    if (active2) {
      if (active2.lifecycle === "temporary" && Date.parse(active2.expiresAt) < expires)
        active2.expiresAt = new Date(expires).toISOString();
      return;
    }
    const artwork = state.artworks.filter(
      (art) => art.speciesId === event.species.id && this.selectableArtwork(ownerId, art, state)
    ).sort((a, b) => b.version - a.version)[0];
    state.birds.push({
      id: randomUUID(),
      speciesId: event.species.id,
      name: null,
      lifecycle: "temporary",
      createdAt: now,
      expiresAt: new Date(expires).toISOString(),
      promotedAt: null,
      artworkId: artwork?.id ?? null,
      originEventId: event.id
    });
  }
  bird(state, birdId) {
    idSchema.parse(birdId);
    const bird = state.birds.find((item) => item.id === birdId);
    if (!bird) throw new YardError("NOT_FOUND", "Bird not found in this yard.");
    return bird;
  }
  collect(state, speciesId, now) {
    idSchema.parse(speciesId);
    if (!state.species.some((s) => s.id === speciesId))
      throw new YardError("NOT_FOUND", "Species not found in this collection.");
    if (!state.collection.some((entry) => entry.speciesId === speciesId))
      state.collection.push({ id: randomUUID(), speciesId, collectedAt: now });
  }
  promote(ownerId, birdId, name, now = nowIso()) {
    now = normalizeNow(now);
    return this.mutate(ownerId, (state) => {
      const bird = this.bird(state, birdId);
      if (name !== void 0) bird.name = this.validName(name);
      bird.lifecycle = "permanent";
      bird.expiresAt = null;
      bird.promotedAt ??= now;
      this.collect(state, bird.speciesId, now);
      return snapshotOf(state, now);
    });
  }
  validName(name) {
    const trimmed = name.trim();
    if (trimmed.length > 60 || hasControlCharacters(trimmed))
      throw new YardError(
        "INVALID",
        "Choose a name of at most 60 characters without control characters."
      );
    return trimmed || null;
  }
  rename(ownerId, birdId, name, now = nowIso()) {
    now = normalizeNow(now);
    return this.mutate(ownerId, (state) => {
      this.bird(state, birdId).name = this.validName(name);
      return snapshotOf(state, now);
    });
  }
  /** Remove only this display instance; evidence, species collection and immutable assets survive. */
  removeBird(ownerId, birdId, now = nowIso()) {
    now = normalizeNow(now);
    return this.mutate(ownerId, (state) => {
      this.bird(state, birdId);
      state.birds = state.birds.filter((bird) => bird.id !== birdId);
      return snapshotOf(state, now);
    });
  }
  addInstance(ownerId, speciesId, name, now = nowIso()) {
    now = normalizeNow(now);
    return this.mutate(ownerId, (state) => {
      this.collect(state, speciesId, now);
      const artwork = state.artworks.filter((art) => art.speciesId === speciesId && this.selectableArtwork(ownerId, art, state)).sort((a, b) => b.version - a.version)[0];
      state.birds.push({
        id: randomUUID(),
        speciesId,
        name: name === void 0 ? null : this.validName(name),
        lifecycle: "permanent",
        createdAt: now,
        promotedAt: now,
        expiresAt: null,
        artworkId: artwork?.id ?? null,
        originEventId: null
      });
      return snapshotOf(state, now);
    });
  }
  collectSpecies(ownerId, speciesId, now = nowIso()) {
    now = normalizeNow(now);
    return this.mutate(ownerId, (state) => {
      this.collect(state, speciesId, now);
      return snapshotOf(state, now);
    });
  }
  updatePreferences(ownerId, patch, now = nowIso()) {
    now = normalizeNow(now);
    const parsed = preferencesPatchSchema.parse(patch);
    return this.mutate(ownerId, (state) => {
      const next = preferencesSchema.parse({
        ...state.preferences,
        ...Object.fromEntries(Object.entries(parsed).filter(([, value]) => value !== void 0))
      });
      if (parsed.scene !== void 0 && parsed.scenePin === void 0)
        next.scenePin = legacyScenePin(next.scene);
      if (parsed.scene !== void 0 || parsed.scenePin !== void 0) {
        const resolved = resolveScene(next.scene, next.scenePin);
        if (resolved.status !== "ready")
          throw new YardError(
            "INVALID",
            "Select an available scene manifest. The saved yard was kept unchanged."
          );
        state.environment.objects = reanchorObjects(state.environment.objects, resolved.manifest);
      }
      state.preferences = next;
      return snapshotOf(state, now);
    });
  }
  addObject(ownerId, kind, now = nowIso()) {
    now = normalizeNow(now);
    objectKindSchema.parse(kind);
    return this.mutate(ownerId, (state) => {
      if (state.environment.objects.length >= MAX_OBJECTS)
        throw new YardError("INVALID", "A yard supports at most 12 objects.");
      if (availableStock(state.environment.inventory, state.environment.objects, kind) <= 0)
        throw new YardError(
          "INVALID",
          "No owned fixtures of this kind are available. Return one to inventory first."
        );
      const position = findObjectPlacement(
        kind,
        state.environment.objects,
        resolveScene(state.preferences.scene, state.preferences.scenePin).manifest
      );
      if (!position)
        throw new YardError(
          "INVALID",
          "There is no free space for this object. Move or remove another object first."
        );
      state.environment.objects.push({ id: randomUUID(), kind, ...position });
      return snapshotOf(state, now);
    });
  }
  moveObject(ownerId, objectId, x, y, now = nowIso(), expected) {
    now = normalizeNow(now);
    idSchema.parse(objectId);
    const baseline = expected ? placementSnapshotSchema.parse(expected) : void 0;
    return this.mutate(ownerId, (state) => {
      if (baseline && placementKey(baseline.scene, baseline.objects, baseline.scenePin) !== placementKey(
        state.preferences.scene,
        state.environment.objects,
        state.preferences.scenePin
      ))
        throw new YardError(
          "STALE_PLACEMENT",
          "The yard changed while you were arranging. Start the move again."
        );
      const object = state.environment.objects.find((item) => item.id === objectId);
      if (!object) throw new YardError("NOT_FOUND", "Object not found in this yard.");
      const moved = yardObjectSchema.parse({ ...object, x, y });
      const objects = state.environment.objects.map(
        (item) => item.id === objectId ? moved : item
      );
      state.environment.objects = validateObjects(
        objects,
        resolveScene(state.preferences.scene, state.preferences.scenePin).manifest
      );
      return snapshotOf(state, now);
    });
  }
  removeObject(ownerId, objectId, now = nowIso()) {
    now = normalizeNow(now);
    idSchema.parse(objectId);
    return this.mutate(ownerId, (state) => {
      if (!state.environment.objects.some((item) => item.id === objectId))
        throw new YardError("NOT_FOUND", "Object not found in this yard.");
      state.environment.objects = state.environment.objects.filter((item) => item.id !== objectId);
      return snapshotOf(state, now);
    });
  }
  /** Exact retries retain their receipt even after later moves, returns or restores. */
  objectInventory(ownerId, input, now = nowIso()) {
    now = normalizeNow(now);
    const command = objectInventoryCommandSchema.parse(input);
    const commandDigest = createHash("sha256").update(canonicalJson(command)).digest("hex");
    return this.mutate(ownerId, (state) => {
      const existing = state.environment.objectReceipts.find(
        (receipt) => receipt.requestId === command.requestId
      );
      if (existing) {
        if (existing.commandDigest !== commandDigest)
          throw new YardError(
            "CONFLICT",
            "This object request ID already belongs to a different operation."
          );
        return snapshotOf(state, now);
      }
      if (state.environment.objectReceipts.length >= MAX_OBJECT_OPERATION_RECEIPTS)
        throw new YardError(
          "INVALID",
          "The saved object-operation history is full. Existing retries still work; new operations require a future history upgrade."
        );
      const expected = command.expected;
      if (placementKey(expected.scene, expected.objects, expected.scenePin) !== placementKey(state.preferences.scene, state.environment.objects, state.preferences.scenePin))
        throw new YardError(
          "STALE_PLACEMENT",
          "The yard changed while you were arranging. Review the latest layout and start again."
        );
      const payload = command.payload;
      let resultObjectId;
      if (payload.operation === "place") {
        if (state.environment.objects.length >= MAX_OBJECTS)
          throw new YardError("INVALID", "A yard supports at most 12 objects.");
        if (availableStock(state.environment.inventory, state.environment.objects, payload.kind) <= 0)
          throw new YardError(
            "INVALID",
            "No owned fixtures of this kind are available. Return one to inventory first."
          );
        const position = findObjectPlacement(
          payload.kind,
          state.environment.objects,
          resolveScene(state.preferences.scene, state.preferences.scenePin).manifest
        );
        if (!position)
          throw new YardError(
            "INVALID",
            "There is no free space for this object. Move or return another object first."
          );
        resultObjectId = randomUUID();
        state.environment.objects.push({ id: resultObjectId, kind: payload.kind, ...position });
      } else {
        const object = state.environment.objects.find((item) => item.id === payload.objectId);
        if (!object) throw new YardError("NOT_FOUND", "Object not found in this yard.");
        resultObjectId = object.id;
        if (payload.operation === "return")
          state.environment.objects = state.environment.objects.filter(
            (item) => item.id !== object.id
          );
        else {
          const moved = yardObjectSchema.parse({ ...object, x: payload.x, y: payload.y });
          state.environment.objects = validateObjects(
            state.environment.objects.map((item) => item.id === object.id ? moved : item),
            resolveScene(state.preferences.scene, state.preferences.scenePin).manifest
          );
        }
      }
      state.environment.objectReceipts.push({
        requestId: command.requestId,
        commandDigest,
        resultObjectId
      });
      return snapshotOf(state, now);
    });
  }
  updateWeather(ownerId, settings, now = nowIso()) {
    now = normalizeNow(now);
    const parsed = weatherSettingsSchema.parse(settings);
    return this.mutate(ownerId, (state) => {
      state.environment.weather = parsed;
      return snapshotOf(state, now);
    });
  }
  registerArtwork(ownerId, input, now = nowIso()) {
    now = normalizeNow(now);
    const art = artworkSchema.parse(input);
    return this.mutate(ownerId, (state) => {
      if (!state.species.some((s) => s.id === art.speciesId))
        throw new YardError("NOT_FOUND", "Artwork requires a known species.");
      if (state.artworks.some(
        (a) => a.id === art.id || a.speciesId === art.speciesId && a.version === art.version
      ))
        throw new YardError("CONFLICT", "Artwork is immutable; create a new ID and version.");
      state.artworks.push(art);
      for (const bird of state.birds)
        if (bird.speciesId === art.speciesId && !bird.artworkId && this.selectableArtwork(ownerId, art, state))
          bird.artworkId = art.id;
      return snapshotOf(state, now);
    });
  }
  /** Explicit per-resident selection; never auto-pins siblings or mutates previous art. */
  pinAnimation(ownerId, birdId, input, now = nowIso()) {
    now = normalizeNow(now);
    return this.mutate(ownerId, (state) => {
      const bird = this.bird(state, birdId);
      if (bird.speciesId !== input.speciesId)
        throw new YardError("INVALID", "Animation species does not match this bird.");
      const art = artworkSchema.parse({
        ...input,
        id: randomUUID(),
        version: 1 + Math.max(
          0,
          ...state.artworks.filter((a) => a.speciesId === bird.speciesId).map((a) => a.version)
        )
      });
      if (!art.animationPin) throw new YardError("INVALID", "An exact animation pin is required.");
      if (!this.selectableArtwork(ownerId, art, state))
        throw new YardError(
          "CONFLICT",
          "Restore this archived or unavailable asset dependency before selecting it."
        );
      const existing = state.artworks.find(
        (a) => a.speciesId === art.speciesId && JSON.stringify(a.animationPin) === JSON.stringify(art.animationPin)
      );
      if (!existing) state.artworks.push(art);
      bird.artworkId = existing?.id ?? art.id;
      return snapshotOf(state, now);
    });
  }
  /** Lifecycle CAS; immutable artwork and evidence remain available for explicit undo. */
  pinCatalog(ownerId, birdId, expectedArtworkId, input, now = nowIso()) {
    now = normalizeNow(now);
    return this.mutate(ownerId, (state) => {
      const bird = this.bird(state, birdId);
      if (bird.artworkId !== expectedArtworkId)
        throw new YardError(
          "CONFLICT",
          "This bird\u2019s artwork changed. Refresh before selecting a catalog version."
        );
      if (bird.speciesId !== input.speciesId)
        throw new YardError("INVALID", "Catalog species does not match this bird.");
      const art = artworkSchema.parse({
        ...input,
        id: randomUUID(),
        version: 1 + Math.max(
          0,
          ...state.artworks.filter((a) => a.speciesId === bird.speciesId).map((a) => a.version)
        )
      });
      if (!art.catalogPin || !this.selectableArtwork(ownerId, art, state))
        throw new YardError(
          "CONFLICT",
          "This shared catalog release is unavailable for selection."
        );
      const existing = state.artworks.find(
        (a) => a.speciesId === art.speciesId && a.catalogPin && canonicalJson(a.catalogPin) === canonicalJson(art.catalogPin) && this.selectableArtwork(ownerId, a, state)
      );
      if (!existing) state.artworks.push(art);
      bird.artworkId = existing?.id ?? art.id;
      return snapshotOf(state, now);
    });
  }
  /** Lifecycle CAS; immutable artwork and evidence remain available for explicit undo. */
  replaceArtworkSelection(ownerId, birdId, expected, next, now = nowIso()) {
    return this.mutate(ownerId, (state) => {
      const bird = this.bird(state, birdId);
      if (bird.artworkId !== expected)
        throw new YardError(
          "CONFLICT",
          "This bird\u2019s artwork changed. Refresh before trying again."
        );
      if (next !== null) {
        const art = state.artworks.find(
          (item) => item.id === next && item.speciesId === bird.speciesId
        );
        if (!art || !this.selectableArtwork(ownerId, art, state))
          throw new YardError(
            "CONFLICT",
            "Restore the archived or unavailable asset dependency before restoring this pin."
          );
      }
      bird.artworkId = next;
      return snapshotOf(state, normalizeNow(now));
    });
  }
  exportBackup(ownerId, now = nowIso()) {
    return backupSchema.parse({
      format: "chirpneighbors-yard",
      version: 2,
      exportedAt: normalizeNow(now),
      data: this.read(ownerId)
    });
  }
  /** Explicit replacement of this owner's yard; supplied owner IDs are never accepted. */
  restoreBackup(ownerId, input, now = nowIso()) {
    now = normalizeNow(now);
    checkOwner(ownerId);
    const data = z11.object({ version: z11.literal(1) }).safeParse(input).success ? migrateV1(input, now) : backupSchema.parse(input).data;
    return this.transaction(() => {
      const current = this.read(ownerId);
      for (const bird of data.birds) {
        if (bird.artworkId === null) continue;
        const art = data.artworks.find((item) => item.id === bird.artworkId);
        const priorBird = current.birds.find((item) => item.id === bird.id);
        const priorArt = current.artworks.find((item) => item.id === priorBird?.artworkId);
        if (art && (priorBird?.artworkId !== bird.artworkId || canonicalJson(priorArt ?? null) !== canonicalJson(art)) && !this.selectableArtwork(ownerId, art, data))
          throw new YardError(
            "CONFLICT",
            "This backup would newly select an archived or unavailable asset. Restore the asset first."
          );
      }
      const receipts = new Map(
        this.read(ownerId).environment.objectReceipts.map((receipt) => [
          receipt.requestId,
          receipt
        ])
      );
      for (const receipt of data.environment.objectReceipts) {
        const existing = receipts.get(receipt.requestId);
        if (existing && canonicalJson(existing) !== canonicalJson(receipt))
          throw new YardError(
            "CONFLICT",
            "The backup conflicts with a saved object-operation receipt."
          );
        receipts.set(receipt.requestId, receipt);
      }
      if (receipts.size > MAX_OBJECT_OPERATION_RECEIPTS)
        throw new YardError(
          "INVALID",
          "The combined object-operation history exceeds this version\u2019s capacity."
        );
      data.environment.objectReceipts = [...receipts.values()];
      this.write(ownerId, data);
      this.hooks.changed?.(ownerId, data);
      this.hooks.restored?.(ownerId, now);
      return snapshotOf(data, now);
    });
  }
  migrateV1(ownerId, input, now = nowIso()) {
    return this.restoreBackup(ownerId, input, now);
  }
};

// birdsong-yard-sprites/src/lib/server/reference-admission/service.ts
import { createHash as createHash6, randomUUID as randomUUID3 } from "node:crypto";
import { existsSync as existsSync2, lstatSync as lstatSync3, readdirSync } from "node:fs";
import { join as join2, resolve as resolve2 } from "node:path";
import { z as z24 } from "zod";

// birdsong-yard-sprites/src/lib/assets/reference-admission.ts
import { z as z20 } from "zod";

// birdsong-yard-sprites/src/lib/assets/animation-specification.ts
import { z as z15 } from "zod";

// birdsong-yard-sprites/src/lib/assets/image-stage-contracts.ts
import { z as z14 } from "zod";

// birdsong-yard-sprites/src/lib/assets/manifest-v3.ts
import { z as z13 } from "zod";

// birdsong-yard-sprites/src/lib/assets/metrics-v3.ts
function measureLoopEdges(canvas, frames, clips) {
  const cache = /* @__PURE__ */ new Map();
  function pixels(index) {
    const cached = cache.get(index);
    if (cached) return cached;
    const frame = frames[index];
    if (!frame) throw new Error("Loop metric references an absent frame.");
    const output = new Uint32Array(canvas.width * canvas.height);
    for (const rect of frame)
      for (let y = rect.y; y < Math.min(canvas.height, rect.y + rect.height); y++)
        for (let x = rect.x; x < Math.min(canvas.width, rect.x + rect.width); x++)
          output[y * canvas.width + x] = rect.color + 1;
    cache.set(index, output);
    return output;
  }
  return animationStates.flatMap((action) => {
    const clip3 = clips[action];
    if (!clip3?.loop) return [];
    const first = clip3.poses[0], last = clip3.poses.at(-1);
    if (!first || !last) throw new Error("Loop metric requires a pose.");
    const left = pixels(first.frame), right = pixels(last.frame);
    let changedPixels = 0;
    for (let index = 0; index < left.length; index++)
      if (left[index] !== right[index]) changedPixels++;
    const contacts = (pose) => JSON.stringify(
      [...pose.contacts].sort((a, b) => a.kind < b.kind ? -1 : a.kind > b.kind ? 1 : 0)
    );
    return [
      {
        action,
        comparedPixels: left.length,
        changedPixels,
        pivotDistance: Math.hypot(first.pivot.x - last.pivot.x, first.pivot.y - last.pivot.y),
        contactLayoutChanged: contacts(first) !== contacts(last)
      }
    ];
  });
}

// birdsong-yard-sprites/src/lib/assets/shape.ts
import { z as z12 } from "zod";
var coordinate = z12.number().int().min(0).max(256);
var point2 = z12.object({ x: coordinate, y: coordinate }).strict();
var id = z12.string().min(1).max(160).regex(/^[a-zA-Z0-9][a-zA-Z0-9._:@-]*$/);
var physicalFootprintSchema = z12.object({
  left: z12.number().int().min(0).max(128),
  right: z12.number().int().min(0).max(128),
  back: z12.number().int().min(0).max(64),
  front: z12.number().int().min(0).max(64)
}).strict().refine(
  (value) => value.left + value.right > 0 && value.back + value.front > 0,
  "Physical footprint must have positive width and depth."
);
var visualBoundsSchema = z12.object({
  x: coordinate,
  y: coordinate,
  width: z12.number().int().min(1).max(256),
  height: z12.number().int().min(1).max(256)
}).strict();
var shapePoseSchema = z12.object({
  poseId: id,
  frame: z12.number().int().min(0).max(63),
  visualBounds: visualBoundsSchema,
  support: point2,
  footprint: physicalFootprintSchema,
  landmarks: z12.array(
    point2.extend({ kind: z12.enum(["head", "body", "beak", "tail", "left-foot", "right-foot"]) }).strict()
  ).max(6)
}).strict();
var shapeReviewSchema = z12.object({
  schemaVersion: z12.literal(1),
  basedOn: animationPinSchema,
  speciesId: id,
  masterPoseId: id,
  poses: z12.array(shapePoseSchema).min(1).max(576)
}).strict().superRefine((value, context2) => {
  if (new Set(value.poses.map((pose) => pose.poseId)).size !== value.poses.length)
    context2.addIssue({ code: "custom", message: "Shape pose IDs must be unique." });
  if (!value.poses.some((pose) => pose.poseId === value.masterPoseId))
    context2.addIssue({ code: "custom", message: "Master pose must identify an annotated pose." });
  if (value.poses.some(
    (pose) => new Set(pose.landmarks.map((point3) => point3.kind)).size !== pose.landmarks.length
  ))
    context2.addIssue({ code: "custom", message: "Landmark kinds must be distinct per pose." });
});
function opaqueBounds(rectangles) {
  if (!rectangles.length) return null;
  const x = Math.min(...rectangles.map((rect) => rect.x));
  const y = Math.min(...rectangles.map((rect) => rect.y));
  return {
    x,
    y,
    width: Math.max(...rectangles.map((rect) => rect.x + rect.width)) - x,
    height: Math.max(...rectangles.map((rect) => rect.y + rect.height)) - y
  };
}
function shapeReviewIssues(manifest, shape2) {
  const issues = [];
  const poses = [
    ...new Map(
      Object.values(manifest.clips).flatMap((clip3) => clip3?.poses ?? []).map((pose) => [pose.poseId, pose])
    ).values()
  ];
  const occurrences = Object.values(manifest.clips).flatMap((clip3) => clip3?.poses ?? []);
  if (occurrences.some(
    (pose) => poses.some((unique) => unique.poseId === pose.poseId && unique.frame !== pose.frame)
  ))
    issues.push("Repeated pose identities must retain the same frame.");
  if (shape2.speciesId !== manifest.speciesId) issues.push("Shape species differs from its pixels.");
  if (poses.length !== shape2.poses.length || poses.some(
    (pose) => !shape2.poses.some((entry) => entry.poseId === pose.poseId && entry.frame === pose.frame)
  ))
    issues.push("Shape annotations must bind every exact authored pose and frame.");
  for (const pose of shape2.poses) {
    const bounds = opaqueBounds(manifest.frames[pose.frame] ?? []);
    if (!bounds || ["x", "y", "width", "height"].some((key) => bounds[key] !== pose.visualBounds[key]))
      issues.push(`Shape visual bounds do not match opaque frame: ${pose.poseId}.`);
    const points = [pose.support, ...pose.landmarks];
    if (points.some((point3) => point3.x > manifest.canvas.width || point3.y > manifest.canvas.height))
      issues.push(`Shape point exceeds canvas: ${pose.poseId}.`);
    if (bounds && (pose.support.x < bounds.x || pose.support.x > bounds.x + bounds.width || pose.support.y < bounds.y || pose.support.y > bounds.y + bounds.height))
      issues.push(`Support must lie within the opaque extent: ${pose.poseId}.`);
  }
  return issues;
}

// birdsong-yard-sprites/src/lib/assets/manifest-v3.ts
var legacy = speciesManifestV2Schema.innerType().shape;
var id2 = z13.string().min(1).max(160).regex(/^[a-zA-Z0-9][a-zA-Z0-9._:@-]*$/);
var integer2 = z13.number().int().min(0).max(Number.MAX_SAFE_INTEGER);
var pointSchema = z13.object({ x: integer2.max(256), y: integer2.max(256) }).strict();
var contactSchema = pointSchema.extend({
  kind: z13.enum(["left-foot", "right-foot", "perch", "ground"])
}).strict();
var animationPoseSchema = z13.object({
  frame: integer2.max(63),
  durationTicks: z13.number().int().min(1).max(300),
  pivot: pointSchema,
  contacts: z13.array(contactSchema).max(4),
  poseId: id2,
  rotation: z13.number().min(-0.5).max(0.5)
}).strict();
var animationClipV3Schema = z13.object({
  action: z13.enum(animationStates),
  direction: z13.literal("right-facing-mirrorable"),
  loop: z13.boolean(),
  poses: z13.array(animationPoseSchema).min(1).max(256)
}).strict();
var animationClipsV3Schema = z13.object({
  idle: animationClipV3Schema,
  moving: animationClipV3Schema.optional(),
  perching: animationClipV3Schema.optional(),
  singing: animationClipV3Schema.optional(),
  feeding: animationClipV3Schema.optional(),
  bathing: animationClipV3Schema.optional(),
  sleeping: animationClipV3Schema.optional(),
  playing: animationClipV3Schema.optional(),
  nesting: animationClipV3Schema.optional()
}).strict();
var taxonomyIdentitySchema = z13.object({
  catalog: z13.literal("chirp-display-catalog"),
  version: z13.literal(1),
  speciesId: id2
}).strict().superRefine((value, context2) => {
  if (!catalogEntry(value.speciesId))
    context2.addIssue({
      code: "custom",
      message: "Species is absent from the pinned application catalog."
    });
});
var reviewedReferenceSchema = z13.object({
  id: id2,
  roles: z13.array(z13.enum(["species", "style", "pose"])).min(1).max(3),
  pin: animationPinSchema
}).strict().superRefine((value, context2) => {
  if (new Set(value.roles).size !== value.roles.length)
    context2.addIssue({ code: "custom", message: "Reference roles must be distinct." });
});
var poseGraphSchema = z13.object({
  nodes: z13.array(
    z13.object({
      id: id2,
      frame: integer2.max(63),
      action: z13.enum(animationStates),
      referenceId: id2
    }).strict()
  ).min(1).max(576),
  edges: z13.array(z13.object({ from: id2, to: id2 }).strict()).max(2304)
}).strict();
var animationConditioningSchema = z13.object({
  taxonomy: taxonomyIdentitySchema,
  references: z13.array(reviewedReferenceSchema).min(1).max(16),
  poseGraph: poseGraphSchema
}).strict();
var normalizationReportSchema = z13.object({
  algorithm: z13.literal("lossless-rgba-rects-v2"),
  alpha: z13.literal("binary"),
  logicalPixelSize: z13.number().int().min(1).max(16),
  palette: z13.array(z13.number().int().min(0).max(16777215)).min(1).max(64),
  loopEdges: z13.array(
    z13.object({
      action: z13.enum(animationStates),
      comparedPixels: integer2.min(1).max(65536),
      changedPixels: integer2.max(65536),
      pivotDistance: z13.number().min(0).max(512),
      contactLayoutChanged: z13.boolean()
    }).strict()
  ).max(9)
}).strict();
var metricGeometrySchema = z13.object({
  canvas: legacy.canvas.omit({ anchorX: true, anchorY: true }),
  frames: legacy.frames,
  clips: animationClipsV3Schema
}).strip();
var speciesManifestV3Schema = z13.object({
  schemaVersion: z13.literal(3),
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
  shape: shapeReviewSchema.optional()
}).strict().superRefine((value, context2) => {
  const fail = (message) => context2.addIssue({ code: "custom", message });
  const { width, height } = value.canvas;
  if (width * height * value.frames.length > 65536) {
    fail("Decoded animation exceeds pixel budget.");
    return;
  }
  if (value.frames.reduce((sum, frame) => sum + frame.length, 0) > 16384)
    fail("Manifest exceeds rectangle budget.");
  if (value.conditioning.taxonomy.speciesId !== value.speciesId)
    fail("Taxonomy and manifest species differ.");
  if (value.fixture ? value.taxonFidelityReviewed || value.provenance.source !== "deterministic_fixture" || value.provenance.usage !== "development-only" : !value.taxonFidelityReviewed || value.provenance.source === "deterministic_fixture" || value.provenance.usage !== "cleared")
    fail("Fixture/fidelity provenance is inconsistent.");
  const grid = value.normalization.logicalPixelSize;
  if (width % grid || height % grid) fail("Canvas does not align to logical grid.");
  const colors = /* @__PURE__ */ new Set();
  for (const frame of value.frames)
    for (const rect of frame) {
      if (rect.x + rect.width > width || rect.y + rect.height > height)
        fail("Frame exceeds canvas bounds.");
      if (rect.x % grid || rect.y % grid || rect.width % grid || rect.height % grid)
        fail("Rectangle does not align to logical grid.");
      colors.add(rect.color);
    }
  if (new Set(value.normalization.palette).size !== value.normalization.palette.length || value.normalization.palette.length !== colors.size || value.normalization.palette.some((color) => !colors.has(color)))
    fail("Palette does not match authored pixels.");
  const refs = value.conditioning.references;
  if (new Set(refs.map((ref) => ref.id)).size !== refs.length || refs.filter((ref) => ref.roles.includes("style")).length !== 1)
    fail("Conditioning requires unique references and exactly one reviewed style reference.");
  const graph = value.conditioning.poseGraph;
  const nodes = new Map(graph.nodes.map((node) => [node.id, node]));
  if (nodes.size !== graph.nodes.length) fail("Pose node IDs must be unique.");
  for (const node of graph.nodes)
    if (node.frame >= value.frames.length || !refs.some((ref) => ref.id === node.referenceId && ref.roles.includes("pose")))
      fail("Pose reference/frame is unavailable.");
  const edgeKey = (from, to) => JSON.stringify([from, to]);
  const declaredEdges = new Set(graph.edges.map((edge) => edgeKey(edge.from, edge.to)));
  if (declaredEdges.size !== graph.edges.length || graph.edges.some((edge) => !nodes.has(edge.from) || !nodes.has(edge.to)))
    fail("Pose edges must be unique and reference available nodes.");
  const usedNodes = /* @__PURE__ */ new Set(), usedEdges = /* @__PURE__ */ new Set();
  const loops = /* @__PURE__ */ new Set();
  for (const [action, clip3] of Object.entries(value.clips)) {
    if (!clip3) continue;
    if (clip3.action !== action) fail("Clip action must match its registered state.");
    for (const [index, pose] of clip3.poses.entries()) {
      const node = nodes.get(pose.poseId);
      if (!node || node.frame !== pose.frame || node.action !== action)
        fail("Clip pose does not match its graph node.");
      usedNodes.add(pose.poseId);
      if (pose.frame >= value.frames.length || pose.pivot.x > width || pose.pivot.y > height || pose.contacts.some((contact2) => contact2.x > width || contact2.y > height))
        fail("Clip frame/pivot/contact exceeds bounds.");
      if (new Set(pose.contacts.map((contact2) => contact2.kind)).size !== pose.contacts.length)
        fail("Contact kinds must be unique per pose.");
      const next = clip3.poses[index + 1] ?? (clip3.loop ? clip3.poses[0] : void 0);
      if (next) usedEdges.add(edgeKey(pose.poseId, next.poseId));
    }
    if (clip3.loop) loops.add(action);
  }
  if (usedNodes.size !== nodes.size || usedEdges.size !== declaredEdges.size || [...usedEdges].some((edge) => !declaredEdges.has(edge)))
    fail("Pose graph must describe exactly the authored clip transitions.");
  const metrics = value.normalization.loopEdges;
  if (new Set(metrics.map((entry) => entry.action)).size !== metrics.length || metrics.length !== loops.size || metrics.some(
    (entry) => !loops.has(entry.action) || entry.comparedPixels !== width * height || entry.changedPixels > entry.comparedPixels
  ))
    fail("Loop metrics do not match authored looping clips.");
  const validIndices = Object.values(value.clips).every(
    (clip3) => !clip3 || clip3.poses.every((pose) => pose.frame < value.frames.length)
  );
  if (validIndices && metricGeometrySchema.safeParse(value).success) {
    if (value.shape) for (const issue of shapeReviewIssues(value, value.shape)) fail(issue);
    const measured = measureLoopEdges(value.canvas, value.frames, value.clips);
    if (measured.some((entry) => {
      const declared = metrics.find((metric) => metric.action === entry.action);
      return !declared || declared.changedPixels !== entry.changedPixels || declared.pivotDistance !== entry.pivotDistance || declared.contactLayoutChanged !== entry.contactLayoutChanged;
    }))
      fail("Loop metrics do not match decoded frame edges.");
  }
});

// birdsong-yard-sprites/src/lib/assets/image-stage-contracts.ts
var id3 = z14.string().min(1).max(160).regex(/^[a-zA-Z0-9][a-zA-Z0-9._:@-]*$/);
var sha256 = z14.string().regex(/^[a-f0-9]{64}$/);
var text = z14.string().min(1).max(2e3).refine((value) => value === value.trim(), "Reference metadata must already be normalized").refine(
  (value) => [...value].every(
    (character) => character >= " " && character !== "\x7F" && character !== "<" && character !== ">"
  ),
  "Reference metadata must be plain text"
);
var https = z14.string().max(2048).regex(/^https:\/\/[!-~]+(?![\s\S])/).refine((value) => {
  try {
    const url = new URL(value);
    return url.protocol === "https:" && !url.username && !url.password;
  } catch {
    return false;
  }
}, "Only credential-free HTTPS source identifiers are allowed");
var pointInTime = z14.string().datetime();
var review = z14.object({ reviewerId: id3, evidenceId: id3, reviewedAt: pointInTime }).strict();
var localReferenceSchema = z14.object({
  schemaVersion: z14.literal(1),
  id: id3,
  fixture: z14.boolean(),
  source: z14.object({
    kind: z14.enum(["local-file", "archive-file", "technical-fixture"]),
    fileIdentity: text,
    originalUrl: https.nullable(),
    descriptionPageUrl: https.nullable(),
    author: text,
    uploader: text.nullable(),
    attribution: text,
    description: text.nullable(),
    sourceTimestamp: pointInTime.nullable(),
    remoteHash: z14.object({
      algorithm: z14.enum(["sha1", "sha256"]),
      value: z14.string().regex(/^[a-f0-9]{40}([a-f0-9]{24})?$/)
    }).strict().nullable()
  }).strict(),
  original: z14.object({
    bytes: z14.number().int().min(1).max(16777216),
    sha256,
    mime: z14.enum(["image/png", "image/jpeg", "application/x-chirp-rgba8"])
  }).strict(),
  decoded: z14.object({
    format: z14.literal("rgba8-straight"),
    width: z14.number().int().min(1).max(256),
    height: z14.number().int().min(1).max(256),
    sha256,
    decoder: z14.object({ id: id3, version: id3 }).strict(),
    derivation: z14.enum(["raw-identity", "declared-unverified"])
  }).strict(),
  rights: z14.object({
    licenseId: id3,
    licenseVersion: id3,
    licenseUrl: https.nullable(),
    status: z14.enum(["pending", "approved", "denied", "conflicting"]),
    restrictions: z14.array(text).max(16),
    referenceUseAllowed: z14.boolean(),
    derivativesAllowed: z14.boolean(),
    redistributionAllowed: z14.boolean(),
    generationPermission: z14.enum(["not-reviewed", "allowed", "denied"]),
    review: review.nullable()
  }).strict(),
  taxonomy: z14.object({
    application: taxonomyIdentitySchema,
    declaredScientificName: text,
    aliases: z14.array(
      z14.object({ authority: id3, version: id3, taxonId: id3, scientificName: text }).strict()
    ).max(16),
    externalEvidence: z14.array(
      z14.object({
        authority: id3,
        version: id3,
        entityId: id3,
        statement: z14.enum(["scientific-name", "rank", "parent-taxon", "image", "depicts"]),
        value: text,
        status: z14.literal("candidate-evidence")
      }).strict()
    ).max(32),
    review: review.nullable()
  }).strict(),
  annotations: z14.object({
    sex: z14.enum(["female", "male", "unknown"]),
    age: z14.enum(["juvenile", "adult", "unknown"]),
    plumage: text.nullable(),
    viewpoint: z14.enum([
      "left",
      "right",
      "front",
      "back",
      "above",
      "below",
      "oblique",
      "unknown"
    ])
  }).strict()
}).strict().superRefine((value, context2) => {
  const fail = (message) => context2.addIssue({ code: "custom", message });
  if (value.source.kind === "technical-fixture" !== value.fixture)
    fail("Technical fixture status must match source kind.");
  if (value.source.kind === "archive-file" && (!value.source.originalUrl || !value.source.descriptionPageUrl))
    fail("Archive files require original and description-page identifiers.");
  const remote = value.source.remoteHash;
  if (remote && remote.value.length !== (remote.algorithm === "sha1" ? 40 : 64))
    fail("Remote hash length does not match its algorithm.");
  const aliases = value.taxonomy.aliases.map(
    (alias) => `${alias.authority}/${alias.version}/${alias.taxonId}`
  );
  if (new Set(aliases).size !== aliases.length) fail("Taxonomy alias pins must be unique.");
  if (value.fixture && value.taxonomy.review !== null)
    fail("A technical fixture cannot claim reviewed species fidelity.");
  if (value.original.mime === "application/x-chirp-rgba8" !== (value.decoded.derivation === "raw-identity"))
    fail(
      "Encoded photo decoding remains an unverified declaration until an adapter is implemented."
    );
});
var referencePolicySchema = z14.object({
  schemaVersion: z14.literal(1),
  id: id3,
  version: id3,
  use: z14.enum(["reference-only", "derived-sprite"]),
  allowedLicenses: z14.array(z14.object({ id: id3, version: id3, url: https.nullable() }).strict()).max(32),
  allowTechnicalFixtures: z14.boolean()
}).strict();
var byte = z14.number().int().min(0).max(255);
var channel = z14.array(byte).min(1).max(65536);
var coordinates = z14.object({ x: z14.number().int().min(0).max(256), y: z14.number().int().min(0).max(256) }).strict();
var contact = coordinates.extend({ kind: z14.enum(["left-foot", "right-foot", "ground", "perch"]) }).strict();
var stageIdentity = z14.object({ id: id3, version: id3 }).strict();
var segmentationStageSchema = z14.discriminatedUnion("encoding", [
  z14.object({
    encoding: z14.literal("binary-mask-u8"),
    values: z14.array(z14.union([z14.literal(0), z14.literal(255)])).min(1).max(65536),
    sha256,
    adapter: stageIdentity
  }).strict(),
  z14.object({
    encoding: z14.literal("logits-f32-le"),
    values: z14.array(z14.number().finite().min(-1e6).max(1e6)).min(1).max(65536),
    sha256,
    adapter: stageIdentity
  }).strict()
]);
var matteStageSchema = z14.object({
  encoding: z14.literal("alpha-u8"),
  alpha: channel,
  sha256,
  origin: z14.enum(["supplied-matte", "technical-fixture"]),
  adapter: stageIdentity
}).strict();
var foregroundStageSchema = z14.object({
  encoding: z14.literal("rgb8"),
  rgb: z14.array(byte).min(3).max(65536 * 3),
  sha256,
  alphaMode: z14.enum(["straight", "premultiplied"]),
  recovery: z14.enum(["supplied-recovered", "technical-fixture"]),
  adapter: stageIdentity
}).strict();
var imageFrameSchema = z14.object({
  id: id3,
  timestampUs: z14.number().int().min(0).max(Number.MAX_SAFE_INTEGER),
  durationUs: z14.number().int().min(1).max(6e7),
  sourceRgba: z14.array(byte).min(4).max(65536 * 4),
  sourceSha256: sha256,
  anchor: coordinates,
  contacts: z14.array(contact).max(4),
  segmentation: segmentationStageSchema.nullable(),
  matte: matteStageSchema,
  foreground: foregroundStageSchema
}).strict();
var imageStageSequenceSchema = z14.object({
  schemaVersion: z14.literal(1),
  fixture: z14.boolean(),
  canvas: z14.object({ width: z14.number().int().min(1).max(256), height: z14.number().int().min(1).max(256) }).strict(),
  frames: z14.array(imageFrameSchema).min(1).max(64),
  loop: z14.boolean(),
  // These are audit identities, not URLs, invocation settings, or an execution capability.
  referenceIds: z14.array(id3).min(1).max(16),
  modelSlot: z14.literal("unconfigured")
}).strict().superRefine((sequence, context2) => {
  const fail = (message) => context2.addIssue({ code: "custom", message });
  const { width, height } = sequence.canvas, pixels = width * height;
  if (pixels * sequence.frames.length > 65536)
    fail("Image sequence exceeds decoded pixel budget.");
  if (new Set(sequence.referenceIds).size !== sequence.referenceIds.length)
    fail("Reference IDs must be unique.");
  if (new Set(sequence.frames.map((frame) => frame.id)).size !== sequence.frames.length)
    fail("Frame IDs must be unique.");
  for (const [index, frame] of sequence.frames.entries()) {
    if (frame.sourceRgba.length !== pixels * 4 || frame.matte.alpha.length !== pixels || frame.foreground.rgb.length !== pixels * 3 || frame.segmentation && frame.segmentation.values.length !== pixels)
      fail("Every image stage must exactly match canvas dimensions.");
    if (frame.anchor.x > width || frame.anchor.y > height || frame.contacts.some((point3) => point3.x > width || point3.y > height))
      fail("Frame anchor/contact is outside its canvas.");
    if (new Set(frame.contacts.map((point3) => point3.kind)).size !== frame.contacts.length)
      fail("Contact kinds must be unique.");
    if (!Number.isSafeInteger(frame.timestampUs + frame.durationUs))
      fail("Frame end timestamp exceeds safe integer range.");
    const previous = sequence.frames[index - 1];
    if (previous && frame.timestampUs !== previous.timestampUs + previous.durationUs)
      fail("Frame timestamps must preserve contiguous original durations/order.");
    if (sequence.fixture !== (frame.matte.origin === "technical-fixture") || sequence.fixture !== (frame.foreground.recovery === "technical-fixture"))
      fail("Fixture stages cannot claim recovered photographic foreground.");
  }
});
var imageQaPolicySchema = z14.object({
  schemaVersion: z14.literal(1),
  id: id3,
  version: id3,
  edgeAlphaThreshold: byte.min(1),
  maxChangedEdgeFraction: z14.number().min(0).max(1),
  maxContactDriftPixels: z14.number().min(0).max(512),
  allowContactSetChange: z14.boolean()
}).strict();
var losslessPixelPolicySchema = z14.object({
  schemaVersion: z14.literal(1),
  id: id3,
  version: id3,
  alpha: z14.literal("binary-required"),
  palette: z14.literal("preserve"),
  logicalPixelSize: z14.number().int().min(1).max(16),
  paletteLimit: z14.number().int().min(1).max(64),
  crop: z14.literal("stable-union-including-anchors")
}).strict();

// birdsong-yard-sprites/src/lib/assets/animation-specification.ts
var hash = z15.string().regex(/^[a-f0-9]{64}$/);
var id4 = z15.string().regex(/^[a-zA-Z0-9][a-zA-Z0-9._:@-]{0,159}$/);
var text2 = z15.string().min(1).max(4e3);
var animationPlanningInputSchema = z15.object({
  schemaVersion: z15.literal(1),
  taxonomy: taxonomyIdentitySchema,
  scientificName: z15.string().min(3).max(160),
  references: z15.array(localReferenceSchema).max(16)
}).strict().superRefine((value, context2) => {
  const fail = (message) => context2.addIssue({ code: "custom", message });
  if (catalogEntry(value.taxonomy.speciesId)?.scientificName !== value.scientificName)
    fail("Scientific name must exactly match the pinned application catalog identity.");
  if (new Set(value.references.map((reference) => reference.id)).size !== value.references.length)
    fail("Planning reference IDs must be unique.");
  for (const reference of value.references)
    if (reference.taxonomy.application.speciesId !== value.taxonomy.speciesId || reference.taxonomy.declaredScientificName !== value.scientificName)
      fail("Reference identity must match the planned species and its scientific name.");
});
var frameSchema = z15.object({
  frame: animationPoseSchema.shape.frame,
  phase: z15.string().min(1).max(160),
  durationTicks: animationPoseSchema.shape.durationTicks,
  proposedPivot: pointSchema,
  contactRequirements: z15.array(contactSchema.shape.kind).max(4)
}).strict();
var clipSchema = z15.object({
  action: z15.enum(animationStates),
  direction: animationClipV3Schema.shape.direction,
  loop: z15.boolean(),
  completion: z15.enum(["repeat", "hold-final-pose"]),
  purpose: z15.string().min(1).max(300),
  frames: z15.array(frameSchema).min(1).max(64),
  entry: z15.literal("review-against-idle-support-and-silhouette"),
  exit: z15.literal("review-against-idle-support-and-silhouette"),
  loopReview: z15.enum(["last-to-first-pixels-pivot-contacts", "not-looping-review-terminal-hold"])
}).strict();
var animationSpecificationSchema = z15.object({
  schemaVersion: z15.literal(1),
  templateVersion: z15.literal("chirp-animation-prompts@1"),
  status: z15.literal("proposed"),
  canvas: z15.object({ width: z15.literal(32), height: z15.literal(32) }).strict(),
  logicalPixelSize: z15.literal(1),
  paletteLimit: z15.literal(32),
  alpha: z15.literal("binary-transparent-background"),
  ticksPerSecond: z15.literal(30),
  totalFrames: z15.number().int().min(1).max(64),
  decodedPixels: z15.number().int().min(1).max(65536),
  clips: z15.array(clipSchema).length(animationStates.length)
}).strict().superRefine((value, context2) => {
  const fail = (message) => context2.addIssue({ code: "custom", message });
  if (value.clips.some((clip3, index) => clip3.action !== animationStates[index]) || new Set(value.clips.map((clip3) => clip3.action)).size !== animationStates.length)
    fail("A production plan requires each canonical action once in canonical order.");
  const frames = value.clips.flatMap((clip3) => clip3.frames);
  if (frames.length !== value.totalFrames || frames.some((frame, index) => frame.frame !== index) || value.decodedPixels !== value.canvas.width * value.canvas.height * frames.length)
    fail("Frame inventory must be contiguous and match the exact decoded allocation.");
  for (const clip3 of value.clips) {
    if (clip3.loop && (clip3.completion !== "repeat" || clip3.loopReview !== "last-to-first-pixels-pivot-contacts") || !clip3.loop && (clip3.completion !== "hold-final-pose" || clip3.loopReview !== "not-looping-review-terminal-hold"))
      fail("Loop, completion and seam review requirements disagree.");
    for (const frame of clip3.frames)
      if (frame.proposedPivot.x > value.canvas.width || frame.proposedPivot.y > value.canvas.height || new Set(frame.contactRequirements).size !== frame.contactRequirements.length)
        fail("Proposed pivots must fit the canvas and contact requirements must be distinct.");
  }
});
var animationRecipeSchema = z15.object({
  schemaVersion: z15.literal(1),
  id: id4,
  version: z15.number().int().min(1).max(1e6),
  specification: animationSpecificationSchema
}).strict();
var frameOverrideSchema = z15.object({
  index: z15.number().int().min(0).max(63),
  phase: z15.string().regex(/^[a-z][a-z0-9-]{0,159}$/).optional(),
  durationTicks: animationPoseSchema.shape.durationTicks.optional(),
  proposedPivot: z15.object({ x: pointSchema.shape.x.max(32), y: pointSchema.shape.y.max(32) }).strict().optional(),
  contactRequirements: z15.array(contactSchema.shape.kind).max(4).optional()
}).strict().superRefine((value, context2) => {
  if (Object.keys(value).length === 1)
    context2.addIssue({
      code: "custom",
      message: "A frame override must explicitly change a field."
    });
  if (value.contactRequirements && new Set(value.contactRequirements).size !== value.contactRequirements.length)
    context2.addIssue({
      code: "custom",
      message: "Override contact requirements must be distinct."
    });
});
var clipOverrideSchema = z15.object({
  action: z15.enum(animationStates),
  durationTicks: animationPoseSchema.shape.durationTicks.optional(),
  loop: z15.boolean().optional(),
  frames: z15.array(frameOverrideSchema).min(1).max(64).optional()
}).strict().superRefine((value, context2) => {
  if (Object.keys(value).length === 1)
    context2.addIssue({
      code: "custom",
      message: "A clip override must explicitly change a field."
    });
  if (value.frames && new Set(value.frames.map((frame) => frame.index)).size !== value.frames.length)
    context2.addIssue({
      code: "custom",
      message: "Frame override indices must be unique within a clip."
    });
});
var animationPlanningInputV2Schema = z15.object({
  schemaVersion: z15.literal(2),
  taxonomy: taxonomyIdentitySchema,
  scientificName: z15.string().min(3).max(160),
  references: z15.array(localReferenceSchema).max(16),
  recipe: z15.object({ id: id4, version: animationRecipeSchema.shape.version }).strict(),
  overrides: z15.object({ clips: z15.array(clipOverrideSchema).max(animationStates.length) }).strict()
}).strict().superRefine((value, context2) => {
  const identity = animationPlanningInputSchema.safeParse({
    schemaVersion: 1,
    taxonomy: value.taxonomy,
    scientificName: value.scientificName,
    references: value.references
  });
  if (!identity.success) for (const issue of identity.error.issues) context2.addIssue(issue);
  if (new Set(value.overrides.clips.map((clip3) => clip3.action)).size !== value.overrides.clips.length)
    context2.addIssue({ code: "custom", message: "Each clip can have only one override." });
});
var animationProductionPlanSchema = z15.object({
  schemaVersion: z15.literal(1),
  format: z15.literal("animation-production-plan"),
  execution: z15.literal("planning-only"),
  model: z15.literal("unconfigured"),
  generatedFrames: z15.literal(0),
  taxonFidelityReviewed: z15.literal(false),
  taxonomy: taxonomyIdentitySchema,
  scientificName: z15.string().min(3).max(160),
  inputSha256: hash,
  specificationSha256: hash,
  specification: animationSpecificationSchema,
  references: z15.array(
    z15.object({
      id: id4,
      originalSha256: hash,
      decodedSha256: hash,
      status: z15.literal("declared-not-byte-verified")
    }).strict()
  ).max(16),
  blockers: z15.array(
    z15.enum([
      "references-missing",
      "reference-bytes-unverified",
      "reference-is-fixture",
      "reference-rights-unreviewed",
      "generation-permission-unreviewed",
      "species-fidelity-unreviewed",
      "model-unconfigured",
      "art-direction-unapproved",
      "output-review-required"
    ])
  ).min(3).max(9),
  prompts: z15.array(
    z15.object({
      action: z15.enum(animationStates),
      templateVersion: z15.literal("chirp-animation-prompts@1"),
      prompt: text2,
      negativePrompt: text2,
      frames: z15.array(z15.object({ frame: animationPoseSchema.shape.frame, prompt: text2 }).strict()).min(1).max(64)
    }).strict()
  ).length(animationStates.length),
  limitations: z15.array(text2).min(1).max(16)
}).strict().superRefine((value, context2) => {
  const fail = (message) => context2.addIssue({ code: "custom", message });
  if (catalogEntry(value.taxonomy.speciesId)?.scientificName !== value.scientificName)
    fail("Plan scientific name must match its pinned catalog identity.");
  if (new Set(value.references.map((reference) => reference.id)).size !== value.references.length || new Set(value.blockers).size !== value.blockers.length)
    fail("Reference identities and blockers must be unique.");
  const required = [
    "reference-bytes-unverified",
    "species-fidelity-unreviewed",
    "model-unconfigured",
    "art-direction-unapproved",
    "output-review-required"
  ];
  if (required.some((blocker) => !value.blockers.includes(blocker)))
    fail("A technical plan cannot remove mandatory unverified production gates.");
  if (!value.references.length !== value.blockers.includes("references-missing"))
    fail("Missing references must be disclosed exactly.");
  for (const [index, prompt] of value.prompts.entries()) {
    const clip3 = value.specification.clips[index];
    if (!clip3 || prompt.action !== clip3.action || prompt.frames.length !== clip3.frames.length || prompt.frames.some((frame, frameIndex) => frame.frame !== clip3.frames[frameIndex]?.frame))
      fail("Every proposed action and frame must have its matching ordered prompt.");
  }
});

// birdsong-yard-sprites/src/lib/assets/intake-v2.ts
import { z as z18 } from "zod";

// birdsong-yard-sprites/src/lib/assets/intake.ts
import { z as z16 } from "zod";
var identifier2 = z16.string().min(1).max(160).regex(/^[a-zA-Z0-9][a-zA-Z0-9._:@-]*$/);
var hash2 = z16.string().regex(/^[a-f0-9]{64}$/);
var label = z16.string().trim().min(1).max(200);
var manifestShape = speciesManifestV2Schema.innerType().shape;
var assetSourceSchema = z16.object({
  schemaVersion: z16.literal(1),
  speciesId: identifier2,
  representation: label,
  source: z16.enum(["deterministic_fixture", "user_upload", "provider"]),
  creator: identifier2,
  sourceVersion: identifier2,
  license: z16.object({
    id: label,
    status: z16.enum(["development-only", "cleared", "pending", "denied"]),
    derivativesAllowed: z16.boolean(),
    redistributionAllowed: z16.boolean(),
    evidenceId: identifier2.nullable(),
    attribution: z16.string().trim().min(1).max(300)
  }).strict(),
  references: z16.array(
    z16.object({
      id: identifier2,
      speciesId: identifier2,
      contentDigest: hash2,
      role: z16.enum(["technical-fixture", "species-reference"])
    }).strict()
  ).min(1).max(16),
  fidelityReview: z16.object({
    reviewerId: identifier2,
    reviewedAt: z16.string().datetime(),
    evidenceId: identifier2
  }).strict().nullable()
}).strict();
var pixelAnimationSourceSchema = z16.object({
  schemaVersion: z16.literal(1),
  format: z16.literal("rgba8-frames"),
  canvas: manifestShape.canvas,
  logicalPixelSize: z16.number().int().min(1).max(16),
  paletteLimit: z16.number().int().min(1).max(64),
  frames: z16.array(
    z16.object({
      rgba: z16.array(z16.number().int().min(0).max(255)).min(4).max(256 * 256 * 4)
    }).strict()
  ).min(1).max(64),
  clips: manifestShape.clips
}).strict();
var assetPackagingInputSchema = z16.object({
  schemaVersion: z16.literal(1),
  source: assetSourceSchema,
  pixels: pixelAnimationSourceSchema
}).strict();
var assetGenerationInputSchema = z16.object({
  schemaVersion: z16.literal(1),
  source: assetSourceSchema,
  requestedStates: z16.array(z16.enum(animationStates)).min(1).max(9)
}).strict();

// birdsong-yard-sprites/src/lib/assets/png-origin.ts
import { z as z17 } from "zod";
var PNG_MAX_BYTES = 524288;
var PNG_MAX_PIXELS = 65536;
var PNG_MAX_DIMENSION = 1024;
var hash3 = z17.string().regex(/^[a-f0-9]{64}$/);
var bytes = z17.number().int().min(1).max(PNG_MAX_BYTES);
var pngFileIdentitySchema = z17.object({
  schemaVersion: z17.literal(1),
  id: z17.string().uuid(),
  original: z17.object({ sha256: hash3, bytes }).strict(),
  canonical: z17.object({
    sha256: hash3,
    bytes,
    rgbaSha256: hash3,
    width: z17.number().int().min(1).max(PNG_MAX_DIMENSION),
    height: z17.number().int().min(1).max(PNG_MAX_DIMENSION)
  }).strict(),
  decoder: z17.object({
    id: z17.literal("sharp"),
    version: z17.string().min(1).max(40),
    libvips: z17.string().min(1).max(40)
  }).strict(),
  normalization: z17.literal("chirp-png-straight-srgb8-hidden-rgb-zero-v1")
}).strict().superRefine((value, context2) => {
  if (value.canonical.width * value.canonical.height > PNG_MAX_PIXELS)
    context2.addIssue({ code: "custom", message: "PNG pixel budget exceeded." });
});
var pngFrameLayoutSchema = z17.object({
  width: z17.number().int().min(1).max(256),
  height: z17.number().int().min(1).max(256),
  columns: z17.number().int().min(1).max(64),
  rows: z17.number().int().min(1).max(64)
}).strict().superRefine((value, context2) => {
  if (value.columns * value.rows > 64 || value.width * value.height * value.columns * value.rows > PNG_MAX_PIXELS)
    context2.addIssue({ code: "custom", message: "PNG frame budget exceeded." });
});
var pngFileOriginSchema = z17.object({
  file: pngFileIdentitySchema,
  reviewDigest: hash3,
  layout: pngFrameLayoutSchema
}).strict();

// birdsong-yard-sprites/src/lib/assets/intake-v2.ts
var id5 = z18.string().min(1).max(160).regex(/^[a-zA-Z0-9][a-zA-Z0-9._:@-]*$/);
var hash4 = z18.string().regex(/^[a-f0-9]{64}$/);
var localModelManifestSchema = z18.object({
  id: id5,
  revision: id5,
  weightsSha256: hash4,
  license: z18.object({ id: id5, contentSha256: hash4 }).strict(),
  adapters: z18.array(
    z18.object({
      id: id5,
      revision: id5,
      weightsSha256: hash4,
      parentWeightsSha256: hash4,
      license: z18.object({ id: id5, contentSha256: hash4 }).strict()
    }).strict()
  ).max(8)
}).strict().superRefine((value, context2) => {
  if (new Set(value.adapters.map((adapter) => adapter.id)).size !== value.adapters.length || value.adapters.some((adapter) => adapter.parentWeightsSha256 !== value.weightsSha256))
    context2.addIssue({
      code: "custom",
      message: "Adapter IDs must be unique and pin the declared parent model weights."
    });
});
var unsupportedStrategy = z18.object({
  version: z18.literal(1),
  execution: z18.literal("unconfigured-local"),
  model: localModelManifestSchema,
  alphaPlan: z18.enum(["native-binary", "native-continuous", "layered", "matting-required"])
}).strict();
var generationStrategySchema = z18.discriminatedUnion("kind", [
  z18.object({
    kind: z18.literal("decoded-rgba"),
    version: z18.literal(1),
    alphaOrigin: z18.enum(["technical-fixture", "native", "upstream-cleanup", "unknown"]),
    output: z18.literal("rgba8-binary")
  }).strict(),
  unsupportedStrategy.extend({ kind: z18.literal("direct-spritesheet") }).strict(),
  unsupportedStrategy.extend({ kind: z18.literal("conditioned-frame-edit") }).strict(),
  unsupportedStrategy.extend({ kind: z18.literal("video-extract") }).strict(),
  unsupportedStrategy.extend({ kind: z18.literal("rigged-deterministic") }).strict()
]);
var pixelAnimationSourceV2Schema = pixelAnimationSourceSchema.omit({ clips: true }).extend({
  schemaVersion: z18.literal(2),
  canvas: speciesManifestV2Schema.innerType().shape.canvas.omit({ anchorX: true, anchorY: true })
}).strict();
var assetPackagingInputV2Schema = z18.object({
  schemaVersion: z18.literal(2),
  source: assetSourceSchema,
  pixels: pixelAnimationSourceV2Schema,
  clips: animationClipsV3Schema,
  conditioning: animationConditioningSchema,
  strategy: generationStrategySchema,
  shape: shapeReviewSchema.optional(),
  fileOrigin: pngFileOriginSchema.optional()
}).strict().superRefine((value, context2) => {
  if (value.conditioning.taxonomy.speciesId !== value.source.speciesId)
    context2.addIssue({ code: "custom", message: "Source and pinned taxonomy species differ." });
  if (value.strategy.kind === "decoded-rgba" && value.source.source === "deterministic_fixture" !== (value.strategy.alphaOrigin === "technical-fixture"))
    context2.addIssue({
      code: "custom",
      message: "Technical fixture alpha declarations cannot claim native generation."
    });
  const refs = value.conditioning.references;
  if (new Set(refs.map((reference) => reference.id)).size !== refs.length || value.source.references.length !== refs.length || refs.some(
    (reference) => !value.source.references.some(
      (source) => source.id === reference.id && source.contentDigest === reference.pin.contentDigest
    )
  ))
    context2.addIssue({
      code: "custom",
      message: "Conditioning pins must match every declared source reference and hash."
    });
});
var rgbaSourceArtifactSchema = z18.object({
  schemaVersion: z18.literal(1),
  format: z18.literal("private-rgba-source"),
  lifecycle: z18.literal("retained-until-owner-deletion"),
  inputDigest: hash4,
  input: assetPackagingInputV2Schema,
  blobs: z18.array(
    z18.object({
      frame: z18.number().int().min(0).max(63),
      encoding: z18.literal("rgba8"),
      bytes: z18.number().int().min(4).max(256 * 256 * 4),
      sha256: hash4
    }).strict()
  ).min(1).max(64)
}).strict().superRefine((value, context2) => {
  if (value.blobs.length !== value.input.pixels.frames.length || value.blobs.some(
    (blob, index) => blob.frame !== index || blob.bytes !== value.input.pixels.canvas.width * value.input.pixels.canvas.height * 4 || blob.bytes !== value.input.pixels.frames[index]?.rgba.length
  ))
    context2.addIssue({
      code: "custom",
      message: "Source blob descriptors must match every decoded frame."
    });
});

// birdsong-yard-sprites/src/lib/assets/reference-discovery.ts
import { z as z19 } from "zod";
var id6 = z19.string().regex(/^[a-zA-Z0-9][a-zA-Z0-9._:@-]{0,159}$/);
var text3 = z19.string().trim().min(1).max(2e3);
var sha2562 = z19.string().regex(/^[a-f0-9]{64}$/);
var scientificName = z19.string().regex(/^[A-Z][a-z]{1,39} [a-z]{2,40}(?: [a-z]{2,40})?$/);
var publicHttps = z19.string().max(2048).refine((value) => {
  try {
    const url = new URL(value);
    return url.protocol === "https:" && !url.username && !url.password && !url.port && !url.hash;
  } catch {
    return false;
  }
}, "A credential-free HTTPS source identifier is required.");
var referenceSourcePinSchema = z19.object({ id: id6, version: z19.number().int().min(1).max(100) }).strict();
var referenceSourceDescriptorSchema = referenceSourcePinSchema.extend({
  schemaVersion: z19.literal(1),
  name: text3,
  homepage: publicHttps,
  capabilities: z19.object({ search: z19.literal(true), originalFetch: z19.boolean() }).strict()
}).strict();
var referenceDiscoveryPolicySchema = z19.object({
  schemaVersion: z19.literal(1),
  purpose: z19.enum(["reference-only", "derived-sprite"]),
  commercial: z19.boolean(),
  allowShareAlike: z19.boolean()
}).strict();
var referenceDiscoveryRequestSchema = z19.object({
  schemaVersion: z19.literal(1),
  taxonomy: taxonomyIdentitySchema,
  scientificName,
  aliases: z19.array(scientificName).max(4),
  sources: z19.array(referenceSourcePinSchema).min(1).max(3),
  suppliedReferences: z19.array(localReferenceSchema).max(16),
  policy: referenceDiscoveryPolicySchema
}).strict().superRefine((value, context2) => {
  const fail = (message) => context2.addIssue({ code: "custom", message });
  if (catalogEntry(value.taxonomy.speciesId)?.scientificName !== value.scientificName)
    fail("Scientific name must match the pinned application catalog.");
  if ((/* @__PURE__ */ new Set([value.scientificName, ...value.aliases])).size !== value.aliases.length + 1)
    fail("Scientific name and aliases must be distinct.");
  if (new Set(value.sources.map((source) => `${source.id}@${source.version}`)).size !== value.sources.length)
    fail("Source pins must be distinct.");
  if (new Set(value.suppliedReferences.map((reference) => reference.id)).size !== value.suppliedReferences.length)
    fail("Supplied references must have distinct identities.");
  for (const reference of value.suppliedReferences)
    if (reference.taxonomy.application.speciesId !== value.taxonomy.speciesId || reference.taxonomy.declaredScientificName !== value.scientificName)
      fail("Supplied reference identity differs from the requested species.");
});
function canonicalReferenceDiscoveryRequest(value) {
  const request = referenceDiscoveryRequestSchema.parse(value);
  const compare = (left, right) => left < right ? -1 : left > right ? 1 : 0;
  request.aliases.sort(compare);
  request.sources.sort(
    (left, right) => compare(`${left.id}@${left.version}`, `${right.id}@${right.version}`)
  );
  request.suppliedReferences.sort((left, right) => compare(left.id, right.id));
  return request;
}
var referenceLicenseSchema = z19.object({
  id: z19.enum([
    "CC0",
    "CC-BY",
    "CC-BY-SA",
    "CC-BY-NC",
    "CC-BY-ND",
    "CC-BY-NC-SA",
    "CC-BY-NC-ND",
    "PDM",
    "unknown"
  ]),
  version: z19.string().regex(/^[1-4]\.[05]$/).nullable(),
  url: publicHttps.nullable(),
  declaredName: text3.nullable(),
  attribution: text3.nullable(),
  status: z19.enum(["recognized", "unknown", "conflicting"]),
  restrictions: z19.array(text3).max(8)
}).strict();
var referenceRightsDecisionSchema = z19.object({
  status: z19.enum(["eligible-for-review", "review-required", "denied"]),
  reasons: z19.array(
    z19.enum([
      "unknown-license",
      "conflicting-license",
      "missing-creator",
      "missing-attribution",
      "restrictions-present",
      "commercial-use-excluded",
      "derivative-use-excluded",
      "share-alike-not-accepted",
      "per-file-review-required"
    ])
  ).min(1).max(9),
  generationApproved: z19.literal(false)
}).strict();
var discoveredReferenceSchema = z19.object({
  schemaVersion: z19.literal(1),
  id: id6,
  source: referenceSourcePinSchema,
  sourceFileId: id6,
  title: text3,
  pageUrl: publicHttps,
  originalUrl: publicHttps,
  accessedAt: z19.string().datetime(),
  sourceUpdatedAt: z19.string().datetime().nullable(),
  creator: text3.nullable(),
  uploader: text3.nullable(),
  license: referenceLicenseSchema,
  sourceSha1: z19.string().regex(/^[a-f0-9]{40}$/).nullable(),
  declaredBytes: z19.number().int().min(1).max(Number.MAX_SAFE_INTEGER),
  width: z19.number().int().min(1).max(1e5),
  height: z19.number().int().min(1).max(1e5),
  mime: z19.enum(["image/jpeg", "image/png"]),
  identification: z19.object({
    confidence: z19.enum(["text-match", "unresolved"]),
    matchedName: scientificName.nullable(),
    review: z19.literal("required")
  }).strict(),
  poseSuitability: z19.literal("unreviewed"),
  rightsDecision: referenceRightsDecisionSchema
}).strict().superRefine((value, context2) => {
  if (value.identification.confidence === "text-match" !== (value.identification.matchedName !== null))
    context2.addIssue({
      code: "custom",
      message: "Text-match confidence requires an explicit matched name."
    });
});
var referenceDiscoveryResultSchema = z19.object({
  schemaVersion: z19.literal(1),
  format: z19.literal("reference-discovery-result"),
  taxonomy: taxonomyIdentitySchema,
  scientificName,
  requestSha256: sha2562,
  policy: referenceDiscoveryPolicySchema,
  status: z19.enum(["supplied", "candidates", "no-results", "blocked", "partial"]),
  suppliedReferenceIds: z19.array(id6).max(16),
  candidates: z19.array(discoveredReferenceSchema).max(12),
  sources: z19.array(
    z19.object({
      id: id6,
      version: z19.number().int().min(1).max(100),
      status: z19.enum(["complete", "partial", "blocked", "skipped"]),
      code: z19.enum([
        "ok",
        "supplied-references",
        "request-budget",
        "byte-budget",
        "rate-limited",
        "denied",
        "network-unavailable",
        "invalid-response",
        "unsafe-url",
        "cancelled",
        "timeout"
      ])
    }).strict()
  ).max(3),
  requestCount: z19.number().int().min(0).max(8),
  downloadCount: z19.literal(0),
  /** Body bytes admitted into bounded buffers, excluding any rejected overflow chunk.
   * This is not a wire-transfer/compressed-byte count. byte-budget records such rejection. */
  totalBytes: z19.number().int().min(0).max(2e6),
  truncated: z19.boolean(),
  generatedFrames: z19.literal(0)
}).strict().superRefine((value, context2) => {
  const fail = (message) => context2.addIssue({ code: "custom", message });
  if (catalogEntry(value.taxonomy.speciesId)?.scientificName !== value.scientificName)
    fail("Discovery identity must match the canonical application catalog.");
  if (new Set(
    value.candidates.map(
      (candidate) => `${candidate.source.id}@${candidate.source.version}/${candidate.sourceFileId}`
    )
  ).size !== value.candidates.length)
    fail("Discovery candidate identities must be unique.");
  if (new Set(value.suppliedReferenceIds).size !== value.suppliedReferenceIds.length || new Set(value.sources.map((source) => `${source.id}@${source.version}`)).size !== value.sources.length)
    fail("Supplied references and source result pins must be unique.");
  if (value.candidates.some(
    (candidate) => !value.sources.some(
      (source) => source.id === candidate.source.id && source.version === candidate.source.version
    )
  ))
    fail("Every candidate must bind an included source result pin.");
  if (value.status === "supplied" && (value.requestCount || value.totalBytes || value.candidates.length || !value.suppliedReferenceIds.length))
    fail("Supplied references bypass all external discovery.");
  if (value.status !== "supplied" && value.suppliedReferenceIds.length)
    fail("Supplied references cannot be mixed into external discovery results.");
  if (value.status === "no-results" && value.candidates.length)
    fail("No-results cannot contain candidates.");
  if (value.status === "candidates" && !value.candidates.length)
    fail("Candidate status requires candidates.");
});
var referenceFetchReceiptSchema = z19.object({
  schemaVersion: z19.literal(1),
  candidateId: id6,
  source: referenceSourcePinSchema,
  originalUrl: publicHttps,
  pageUrl: publicHttps,
  fetchedAt: z19.string().datetime(),
  sha256: sha2562,
  sha1: z19.string().regex(/^[a-f0-9]{40}$/),
  bytes: z19.number().int().min(1).max(8388608),
  mime: z19.enum(["image/jpeg", "image/png"]),
  license: referenceLicenseSchema,
  creator: text3,
  rightsReview: z19.literal("required"),
  speciesReview: z19.literal("required"),
  poseReview: z19.literal("required"),
  generationApproved: z19.literal(false)
}).strict();

// birdsong-yard-sprites/src/lib/assets/reference-admission.ts
var id7 = z20.string().regex(/^[a-zA-Z0-9][a-zA-Z0-9._:@-]{0,159}$/);
var sha2563 = z20.string().regex(/^[a-f0-9]{64}$/);
var text4 = z20.string().trim().min(1).max(2e3);
var time = z20.string().datetime();
var licenseUrl = z20.string().max(2048).refine((value) => {
  try {
    const url = new URL(value);
    return url.protocol === "https:" && !url.username && !url.password && !url.port && !url.hash;
  } catch {
    return false;
  }
}, "License metadata requires a credential-free HTTPS identifier.");
var REFERENCE_IMAGE_LIMITS = {
  originalBytes: 2097152,
  canonicalBytes: 5242880,
  pixels: 1048576,
  side: 2048
};
var referenceImageIdentitySchema = z20.object({
  schemaVersion: z20.literal(1),
  id: z20.string().uuid(),
  original: z20.object({
    sha256: sha2563,
    bytes: z20.number().int().min(1).max(REFERENCE_IMAGE_LIMITS.originalBytes),
    mime: z20.enum(["image/png", "image/jpeg"])
  }).strict(),
  canonical: z20.object({
    sha256: sha2563,
    bytes: z20.number().int().min(1).max(REFERENCE_IMAGE_LIMITS.canonicalBytes),
    width: z20.number().int().min(1).max(REFERENCE_IMAGE_LIMITS.side),
    height: z20.number().int().min(1).max(REFERENCE_IMAGE_LIMITS.side),
    rgbaSha256: sha2563
  }).strict(),
  decoder: z20.object({ id: z20.literal("sharp"), version: id7, libvips: id7 }).strict(),
  normalization: z20.literal("chirp-reference-straight-srgb8-oriented-hidden-rgb-zero-v1")
}).strict().superRefine((value, context2) => {
  if (value.canonical.width * value.canonical.height > REFERENCE_IMAGE_LIMITS.pixels)
    context2.addIssue({
      code: "custom",
      message: "Decoded reference allocation exceeds its limit."
    });
});
var referenceAdmissionSourceSchema = z20.discriminatedUnion("kind", [
  z20.object({ kind: z20.literal("owner-upload") }).strict(),
  z20.object({
    kind: z20.literal("retained-discovery"),
    discoveryPin: animationPinSchema,
    candidateId: id7,
    candidate: discoveredReferenceSchema,
    receipt: referenceFetchReceiptSchema
  }).strict()
]);
var referenceAdmissionPinSchema = z20.object({ referenceId: z20.string().uuid(), contentDigest: sha2563, reviewDigest: sha2563 }).strict();
var reviewBase = {
  requestId: z20.string().uuid(),
  decision: z20.enum(["approved", "rejected"]),
  evidenceId: id7
};
var rightsCommand = z20.object({
  ...reviewBase,
  kind: z20.literal("rights"),
  generationAllowed: z20.boolean(),
  derivativesAllowed: z20.boolean(),
  redistributionAllowed: z20.boolean(),
  licenseId: id7,
  licenseVersion: id7.nullable(),
  licenseUrl: licenseUrl.nullable(),
  creator: text4,
  attribution: text4
}).strict();
var speciesCommand = z20.object({ ...reviewBase, kind: z20.literal("species"), speciesId: id7 }).strict();
var referenceViewpoints = [
  "left",
  "right",
  "front",
  "back",
  "three-quarter",
  "other"
];
var poseCommand = z20.object({
  ...reviewBase,
  kind: z20.literal("pose"),
  poseLabel: z20.string().trim().min(1).max(160),
  permittedActions: z20.array(z20.enum(animationStates)).min(1).max(animationStates.length),
  viewpoints: z20.array(z20.enum(referenceViewpoints)).min(1).max(referenceViewpoints.length)
}).strict();
var reviewCommand = z20.discriminatedUnion("kind", [rightsCommand, speciesCommand, poseCommand]);
function validateReview(value, context2) {
  const fail = (message) => context2.addIssue({ code: "custom", message });
  if (value.kind === "rights" && value.decision === "approved" && (!value.generationAllowed || !value.derivativesAllowed || !value.redistributionAllowed || ["unknown", "pending", "unreviewed", "denied"].includes(value.licenseId.toLowerCase())))
    fail("Approved rights require an identified license and all intended-use permissions.");
  if (value.kind === "species" && !catalogEntry(value.speciesId))
    fail("Species review requires a supported catalog identity.");
  if (value.kind === "pose" && (new Set(value.permittedActions).size !== value.permittedActions.length || new Set(value.viewpoints).size !== value.viewpoints.length))
    fail("Pose review action and viewpoint scopes must be distinct.");
}
var referenceReviewCommandSchema = reviewCommand.superRefine(validateReview);
var reviewEvent = { reviewerId: id7, reviewedAt: time };
var rightsEvent = rightsCommand.extend(reviewEvent).strict();
var speciesEvent = speciesCommand.extend(reviewEvent).strict();
var poseEvent = poseCommand.extend(reviewEvent).strict();
var referenceReviewSchema = z20.discriminatedUnion("kind", [rightsEvent, speciesEvent, poseEvent]).superRefine(validateReview);
var referenceRevokeCommandSchema = z20.object({ requestId: z20.string().uuid(), reason: text4 }).strict();
var referenceRevocationSchema = referenceRevokeCommandSchema.extend({ reviewerId: id7, revokedAt: time }).strict();
var referenceAdmissionRecordSchema = z20.object({
  identity: referenceImageIdentitySchema,
  contentDigest: sha2563,
  reviewDigest: sha2563,
  source: referenceAdmissionSourceSchema,
  createdAt: time,
  reviews: z20.object({
    rights: rightsEvent.superRefine(validateReview).nullable(),
    species: speciesEvent.superRefine(validateReview).nullable(),
    pose: poseEvent.superRefine(validateReview).nullable()
  }).strict(),
  revocation: referenceRevocationSchema.nullable()
}).strict().superRefine((value, context2) => {
  const fail = (message) => context2.addIssue({ code: "custom", message });
  if (value.source.kind === "retained-discovery") {
    const receipt = value.source.receipt;
    const candidate = value.source.candidate;
    if (receipt.candidateId !== value.source.candidateId || receipt.sha256 !== value.identity.original.sha256 || receipt.bytes !== value.identity.original.bytes || receipt.mime !== value.identity.original.mime)
      fail("Retained source receipt must identify the exact original image bytes.");
    if (candidate.id !== value.source.candidateId || candidate.source.id !== receipt.source.id || candidate.source.version !== receipt.source.version || candidate.originalUrl !== receipt.originalUrl || candidate.pageUrl !== receipt.pageUrl || candidate.mime !== receipt.mime || candidate.declaredBytes !== receipt.bytes || candidate.sourceSha1 !== null && candidate.sourceSha1 !== receipt.sha1 || candidate.creator !== receipt.creator || JSON.stringify(candidate.license) !== JSON.stringify(receipt.license))
      fail(
        "Retained discovery metadata and original-fetch receipt must identify the same source."
      );
    const rights = value.reviews.rights;
    if (rights?.decision === "approved" && (candidate.license.status !== "recognized" || candidate.license.id === "unknown" || candidate.rightsDecision.status === "denied" || candidate.license.restrictions.length > 0 || rights.licenseId !== candidate.license.id || rights.licenseVersion !== candidate.license.version || rights.licenseUrl !== candidate.license.url || rights.creator !== candidate.creator || rights.attribution !== candidate.license.attribution))
      fail(
        "Approved rights cannot replace retained source license, creator, attribution or unresolved restrictions."
      );
  }
  const createdAt = Date.parse(value.createdAt);
  const reviews = Object.values(value.reviews).filter((review2) => review2 !== null);
  if (reviews.some((review2) => Date.parse(review2.reviewedAt) < createdAt) || value.revocation && (Date.parse(value.revocation.revokedAt) < createdAt || reviews.some(
    (review2) => Date.parse(review2.reviewedAt) > Date.parse(value.revocation.revokedAt)
  )))
    fail("Review and terminal revocation chronology must follow admission.");
});
var referenceAdmissionListSchema = z20.object({ files: z20.array(referenceAdmissionRecordSchema).max(16) }).strict();
var referenceAdmissionResponseSchema = z20.object({ file: referenceAdmissionRecordSchema }).strict();
var referenceGenerationProviderPinSchema = z20.object({ id: id7, version: z20.number().int().min(1).max(100) }).strict();
var referenceGenerationInputSchema = z20.object({
  schemaVersion: z20.literal(1),
  referencePin: referenceAdmissionPinSchema,
  planningInput: animationPlanningInputV2Schema,
  provider: referenceGenerationProviderPinSchema
}).strict().superRefine((value, context2) => {
  if (value.planningInput.references.length)
    context2.addIssue({
      code: "custom",
      message: "Only the admitted reference pin can supply reference bytes."
    });
});
var referenceGenerationCommandSchema = z20.discriminatedUnion("action", [
  z20.object({
    action: z20.literal("queue"),
    requestId: z20.string().uuid(),
    input: referenceGenerationInputSchema
  }).strict(),
  z20.object({ action: z20.literal("advance"), jobId: id7 }).strict(),
  z20.object({ action: z20.literal("cancel"), jobId: id7 }).strict()
]);
var referenceAcquisitionCommandSchema = z20.object({
  requestId: z20.string().uuid(),
  jobId: id7,
  artifactId: id7,
  candidateId: id7
}).strict();
var diagnosticPixels = pixelAnimationSourceV2Schema.extend({
  canvas: pixelAnimationSourceV2Schema.shape.canvas.extend({
    width: z20.number().int().min(1).max(8),
    height: z20.number().int().min(1).max(8)
  }).strict(),
  logicalPixelSize: z20.literal(1),
  frames: z20.array(
    pixelAnimationSourceV2Schema.shape.frames.element.extend({
      rgba: pixelAnimationSourceV2Schema.shape.frames.element.shape.rgba.max(8 * 8 * 4)
    }).strict()
  ).length(1)
}).strict().superRefine((value, context2) => {
  const rgba = value.frames[0]?.rgba;
  if (!rgba || rgba.length !== value.canvas.width * value.canvas.height * 4)
    context2.addIssue({
      code: "custom",
      message: "Diagnostic RGBA allocation must exactly match its canvas."
    });
  if (rgba?.some((channel2, index) => index % 4 === 3 && channel2 !== 0 && channel2 !== 255))
    context2.addIssue({ code: "custom", message: "Diagnostic fixtures require binary alpha." });
  if (rgba?.some(
    (channel2, index) => index % 4 !== 3 && rgba[index - index % 4 + 3] === 0 && channel2 !== 0
  ))
    context2.addIssue({
      code: "custom",
      message: "Transparent diagnostic pixels require zero RGB."
    });
});
var referenceGenerationCandidateSchema = z20.object({
  schemaVersion: z20.literal(1),
  format: z20.literal("reference-generation-candidate"),
  renderable: z20.literal(false),
  fixture: z20.literal(true),
  generated: z20.literal(false),
  purpose: z20.literal("local-diagnostic-not-species-art"),
  provider: referenceGenerationProviderPinSchema,
  inputSha256: sha2563,
  planSha256: sha2563,
  referencePin: referenceAdmissionPinSchema,
  reference: z20.object({ originalSha256: sha2563, canonicalSha256: sha2563, rgbaSha256: sha2563 }).strict(),
  pixels: diagnosticPixels,
  outputSha256: sha2563,
  execution: z20.object({
    kind: z20.literal("local-fake"),
    externalCalls: z20.literal(0),
    modelCalls: z20.literal(0),
    scientificFidelityApproved: z20.literal(false)
  }).strict(),
  limitations: z20.array(text4).min(1).max(16)
}).strict();

// birdsong-yard-sprites/src/lib/server/pipeline/canonical.ts
import { createHash as createHash2 } from "node:crypto";
function canonicalJson2(value) {
  const seen = /* @__PURE__ */ new Set();
  const visit = (current, depth) => {
    if (depth > 64) throw new PermanentStageError("Pipeline JSON is too deeply nested");
    if (current === null || typeof current === "boolean" || typeof current === "string") {
      return JSON.stringify(current);
    }
    if (typeof current === "number" && Number.isFinite(current)) return JSON.stringify(current);
    if (!current || typeof current !== "object")
      throw new PermanentStageError("Expected finite JSON data");
    if (seen.has(current)) throw new PermanentStageError("Cyclic pipeline JSON");
    seen.add(current);
    let encoded;
    if (Array.isArray(current)) {
      encoded = "[" + Array.from(current, (item) => visit(item, depth + 1)).join(",") + "]";
    } else {
      if (Object.getPrototypeOf(current) !== Object.prototype && Object.getPrototypeOf(current) !== null) {
        throw new PermanentStageError("Pipeline data must contain plain JSON objects");
      }
      const entries = Object.entries(current);
      encoded = "{" + entries.sort(([left], [right]) => left < right ? -1 : left > right ? 1 : 0).map(([key, item]) => JSON.stringify(key) + ":" + visit(item, depth + 1)).join(",") + "}";
    }
    seen.delete(current);
    return encoded;
  };
  const result2 = visit(value, 0);
  if (Buffer.byteLength(result2) > 1e6)
    throw new PermanentStageError("Pipeline JSON exceeds 1 MB");
  return result2;
}
var digest = (value) => createHash2("sha256").update(canonicalJson2(value)).digest("hex");
var PermanentStageError = class extends Error {
};

// birdsong-yard-sprites/src/lib/server/reference-discovery/service.ts
import { createHash as createHash3 } from "node:crypto";
import { z as z22 } from "zod";

// birdsong-yard-sprites/src/lib/server/asset-pipeline/reference-stage.ts
function sanitizeReferenceText(value) {
  if (value.length > 16384) throw new PermanentStageError("Source metadata exceeds text budget");
  const decoded = value.replace(
    /&#(?:x([a-f0-9]+)|([0-9]+));|&(lt|gt|amp|quot|apos|nbsp);/gi,
    (_match, hex, decimal, name) => {
      if (hex || decimal) {
        const code = Number.parseInt(hex ?? decimal ?? "", hex ? 16 : 10);
        return code > 0 && code <= 1114111 && !(code >= 55296 && code <= 57343) ? String.fromCodePoint(code) : " ";
      }
      return { lt: "<", gt: ">", amp: "&", quot: '"', apos: "'", nbsp: " " }[name?.toLowerCase() ?? ""] ?? " ";
    }
  );
  const stripped = decoded.replace(/<(script|style)\b[^>]*>[\s\S]*?<\/\1\s*>/gi, " ").replace(/<[^>]*>/g, " ");
  return [...stripped].map(
    (character) => character < " " || character === "\x7F" || character === "<" || character === ">" ? " " : character
  ).join("").replace(/\s+/g, " ").trim().slice(0, 2e3);
}

// birdsong-yard-sprites/src/lib/server/reference-discovery/policy.ts
function plainMetadata(value) {
  if (typeof value !== "string" || value.length > 16384) return null;
  const text5 = sanitizeReferenceText(value);
  return text5 || null;
}
function identifyReferenceLicense(input) {
  const declaredName = plainMetadata(input.name), attribution = plainMetadata(input.attribution);
  const restrictions = plainMetadata(input.restrictions);
  let url = null;
  if (typeof input.url === "string") {
    try {
      url = new URL(input.url);
    } catch {
    }
  }
  const safe = url && ["http:", "https:"].includes(url.protocol) && url.hostname === "creativecommons.org" && !url.username && !url.password && !url.port && !url.search && !url.hash;
  const canonicalUrl = safe && url ? `https://creativecommons.org${url.pathname.endsWith("/") ? url.pathname : `${url.pathname}/`}` : null;
  const match = canonicalUrl?.match(
    /^https:\/\/creativecommons\.org\/licenses\/(by(?:-nc)?(?:-nd|-sa)?)\/(1\.0|2\.0|2\.5|3\.0|4\.0)\/$/
  );
  let id8 = "unknown", version2 = null;
  if (match?.[1] && match[2]) {
    id8 = `CC-${match[1].toUpperCase()}`;
    version2 = match[2];
  }
  if (canonicalUrl === "https://creativecommons.org/publicdomain/zero/1.0/") {
    id8 = "CC0";
    version2 = "1.0";
  }
  if (canonicalUrl === "https://creativecommons.org/publicdomain/mark/1.0/") {
    id8 = "PDM";
    version2 = "1.0";
  }
  const normalizedName = declaredName?.toUpperCase().replaceAll("-", " ").replace(/\s+/g, " ");
  const expected = id8 === "CC0" ? ["CC0", "CC0 1.0", "CC0 1.0 UNIVERSAL"] : id8 === "PDM" ? ["PUBLIC DOMAIN", "PUBLIC DOMAIN MARK", "PUBLIC DOMAIN MARK 1.0", "PDM 1.0"] : [`${id8.replaceAll("-", " ")} ${version2}`];
  const status = id8 === "unknown" ? "unknown" : normalizedName && expected.includes(normalizedName) ? "recognized" : "conflicting";
  return referenceLicenseSchema.parse({
    id: id8,
    version: version2,
    url: canonicalUrl,
    declaredName,
    attribution,
    status,
    restrictions: restrictions ? [restrictions] : []
  });
}
function evaluateReferenceRights(licenseValue, creator, policyValue) {
  const declared = referenceLicenseSchema.parse(licenseValue), policy = referenceDiscoveryPolicySchema.parse(policyValue);
  const license = identifyReferenceLicense({
    name: declared.declaredName,
    url: declared.url,
    attribution: declared.attribution,
    restrictions: declared.restrictions.join("; ")
  });
  if (license.id !== declared.id || license.version !== declared.version || license.status !== declared.status)
    license.status = "conflicting";
  const reasons = [];
  if (license.status === "unknown" || license.id === "unknown" || !license.url || !license.version)
    reasons.push("unknown-license");
  if (license.status === "conflicting") reasons.push("conflicting-license");
  if (!creator) reasons.push("missing-creator");
  if (!license.attribution) reasons.push("missing-attribution");
  if (license.restrictions.length) reasons.push("restrictions-present");
  let denied = false;
  if (policy.commercial && license.id.includes("-NC")) {
    reasons.push("commercial-use-excluded");
    denied = true;
  }
  if (policy.purpose === "derived-sprite" && license.id.includes("-ND")) {
    reasons.push("derivative-use-excluded");
    denied = true;
  }
  if (policy.purpose === "derived-sprite" && license.id.includes("-SA") && !policy.allowShareAlike) {
    reasons.push("share-alike-not-accepted");
    denied = true;
  }
  const status = denied ? "denied" : reasons.length ? "review-required" : "eligible-for-review";
  reasons.push("per-file-review-required");
  return referenceRightsDecisionSchema.parse({ status, reasons, generationApproved: false });
}

// birdsong-yard-sprites/src/lib/server/reference-discovery/registry.ts
import { z as z21 } from "zod";
var DISCOVERY_LIMITS = Object.freeze({
  requests: 8,
  pages: 3,
  candidates: 12,
  pageSize: 5,
  responseBytes: 512e3,
  totalBytes: 2e6,
  originalBytes: 8388608,
  requestTimeoutMs: 5e3,
  operationTimeoutMs: 15e3,
  retryDelayMs: 2e3
});
var ReferenceDiscoveryError = class extends Error {
  constructor(code, retryAfterMs = null) {
    super(`Reference discovery ${code}`);
    this.code = code;
    this.retryAfterMs = retryAfterMs;
  }
  code;
  retryAfterMs;
};
var trustedTaxonomyAliasesSchema = z21.array(
  z21.object({
    speciesId: z21.string().min(1),
    scientificName: z21.string().min(1),
    aliases: z21.array(z21.string().regex(/^[A-Z][a-z]{1,39} [a-z]{2,40}(?: [a-z]{2,40})?$/)).max(4)
  }).strict()
).max(128);

// birdsong-yard-sprites/src/lib/server/reference-discovery/service.ts
var pageSchema = z22.object({
  candidates: z22.array(discoveredReferenceSchema).max(DISCOVERY_LIMITS.pageSize),
  nextCursor: z22.string().min(1).max(2048).nullable()
}).strict();
function context(signal, byteLimit = DISCOVERY_LIMITS.totalBytes, isCancelled) {
  const timeout = AbortSignal.timeout(DISCOVERY_LIMITS.operationTimeoutMs);
  return {
    signal: signal ? AbortSignal.any([signal, timeout]) : timeout,
    ...isCancelled ? { isCancelled } : {},
    usage: { requests: 0, bytes: 0 },
    byteLimit
  };
}
async function fetchDiscoveredOriginal(candidateValue, requestValue, registry, options = {}) {
  const candidate = discoveredReferenceSchema.parse(candidateValue), request = canonicalReferenceDiscoveryRequest(requestValue);
  registry.assertRequest(request);
  if (!request.sources.some(
    (pin) => pin.id === candidate.source.id && pin.version === candidate.source.version
  ) || !candidate.identification.matchedName || ![request.scientificName, ...request.aliases].includes(candidate.identification.matchedName) || evaluateReferenceRights(candidate.license, candidate.creator, request.policy).status !== "eligible-for-review")
    throw new ReferenceDiscoveryError("denied");
  const adapter = registry.resolve(candidate.source);
  if (!adapter.fetchOriginal) throw new ReferenceDiscoveryError("denied");
  const result2 = await adapter.fetchOriginal(
    candidate,
    request,
    context(options.signal, DISCOVERY_LIMITS.originalBytes + DISCOVERY_LIMITS.responseBytes)
  );
  const receipt = referenceFetchReceiptSchema.parse(result2.receipt);
  if (!(result2.bytes instanceof Uint8Array) || result2.bytes.byteLength !== receipt.bytes || createHash3("sha256").update(result2.bytes).digest("hex") !== receipt.sha256 || receipt.candidateId !== candidate.id || receipt.source.id !== candidate.source.id || receipt.source.version !== candidate.source.version || receipt.originalUrl !== candidate.originalUrl || receipt.pageUrl !== candidate.pageUrl)
    throw new ReferenceDiscoveryError("invalid-response");
  if (options.persist) await options.persist(result2.bytes.slice(), structuredClone(receipt));
  return { bytes: result2.bytes, receipt, persisted: !!options.persist };
}

// birdsong-yard-sprites/src/lib/server/storage/private-files.ts
import {
  chmodSync,
  closeSync,
  constants,
  fchmodSync,
  fstatSync,
  lstatSync,
  mkdirSync as mkdirSync2,
  openSync,
  realpathSync
} from "node:fs";
var unavailable = () => new Error("Private application storage is unavailable.");
function ensurePrivateDirectory(directory) {
  try {
    mkdirSync2(directory, { recursive: true, mode: 448 });
    const stat = lstatSync(directory);
    if (!stat.isDirectory() || stat.isSymbolicLink()) throw unavailable();
    chmodSync(directory, 448);
    return realpathSync(directory);
  } catch {
    throw unavailable();
  }
}

// birdsong-yard-sprites/src/lib/server/reference-admission/decode.ts
import { createHash as createHash4 } from "node:crypto";
import { crc32, inflateSync } from "node:zlib";
import sharp from "sharp";
var referenceHash = (bytes3) => createHash4("sha256").update(bytes3).digest("hex");
function invalid(message) {
  throw new YardError("INVALID", message);
}
function dimensions(width, height) {
  if (!width || !height || width > REFERENCE_IMAGE_LIMITS.side || height > REFERENCE_IMAGE_LIMITS.side || width * height > REFERENCE_IMAGE_LIMITS.pixels)
    invalid("Reference image dimensions exceed the supported budget.");
}
var signature = Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]);
var chromaticity = [31270, 32900, 64e3, 33e3, 3e4, 6e4, 15e3, 6e3];
function png(input) {
  if (!input.subarray(0, 8).equals(signature)) invalid("Reference bytes do not match PNG.");
  let offset = 8, count = 0, width = 0, height = 0, channels = 0, metadata = 0;
  let image = false, afterImage = false, ended = false;
  const clean = [signature], compressed = [], seen = /* @__PURE__ */ new Set();
  while (offset < input.length) {
    if (++count > 256 || offset + 12 > input.length) invalid("Invalid PNG structure.");
    const length = input.readUInt32BE(offset), end = offset + length + 12;
    if (end > input.length) invalid("Truncated PNG.");
    const type = input.toString("ascii", offset + 4, offset + 8), payload = input.subarray(offset + 8, end - 4);
    if (!/^[A-Za-z]{4}$/.test(type) || type[2] !== type[2]?.toUpperCase() || crc32(input.subarray(offset + 4, end - 4)) !== input.readUInt32BE(end - 4))
      invalid("Invalid PNG chunk or checksum.");
    if (count === 1 && type !== "IHDR") invalid("PNG header is missing.");
    if (seen.has(type) && !["IDAT", "tEXt"].includes(type)) invalid("Duplicate PNG chunk.");
    if (image && type !== "IDAT") afterImage = true;
    if (type === "IHDR") {
      if (length !== 13) invalid("Invalid PNG header.");
      width = payload.readUInt32BE(0);
      height = payload.readUInt32BE(4);
      dimensions(width, height);
      channels = payload[9] === 2 ? 3 : payload[9] === 6 ? 4 : 0;
      if (payload[8] !== 8 || !channels || payload[10] !== 0 || payload[11] !== 0 || payload[12] !== 0)
        invalid("Use non-interlaced RGB or RGBA8 PNG references.");
      clean.push(input.subarray(offset, end));
    } else if (type === "IDAT") {
      if (afterImage || !length) invalid("Invalid PNG image data.");
      image = true;
      compressed.push(payload);
      clean.push(input.subarray(offset, end));
    } else if (type === "IEND") {
      if (!image || length !== 0 || end !== input.length)
        invalid("Invalid PNG end or trailing bytes.");
      ended = true;
      clean.push(input.subarray(offset, end));
    } else if (["sRGB", "gAMA", "cHRM"].includes(type)) {
      if (image || type === "sRGB" && (length !== 1 || payload[0] > 3) || type === "gAMA" && (length !== 4 || payload.readUInt32BE(0) !== 45455) || type === "cHRM" && (length !== 32 || chromaticity.some((n, i) => payload.readUInt32BE(i * 4) !== n)))
        invalid("Only standard sRGB PNG references are supported.");
    } else if (["tEXt", "pHYs", "tIME"].includes(type)) {
      metadata += length;
      if (metadata > 16384) invalid("PNG metadata exceeds its budget.");
    } else
      invalid("Animated PNG, compressed profiles and unsupported PNG metadata are not accepted.");
    seen.add(type);
    offset = end;
  }
  if (!ended) invalid("PNG end is missing.");
  const bytes3 = Buffer.concat(compressed), expected = height * (1 + width * channels);
  try {
    const result2 = inflateSync(bytes3, { maxOutputLength: expected + 1, info: true });
    if (!result2 || typeof result2 !== "object" || !("buffer" in result2) || !Buffer.isBuffer(result2.buffer) || !("engine" in result2) || !result2.engine || typeof result2.engine !== "object" || !("bytesWritten" in result2.engine) || result2.engine.bytesWritten !== bytes3.length || result2.buffer.length !== expected)
      invalid("Invalid PNG decompression.");
    for (let y = 0; y < height; y++)
      if (result2.buffer[y * (1 + width * channels)] > 4) invalid("Invalid PNG scanline.");
  } catch {
    invalid("PNG compressed pixels are invalid or exceed their budget.");
  }
  return { input: Buffer.concat(clean), width, height };
}
function jpeg(input) {
  if (input[0] !== 255 || input[1] !== 216) invalid("Reference bytes do not match JPEG.");
  let offset = 2, markers = 0, metadata = 0, width = 0, height = 0, scans = 0, ended = false;
  while (offset < input.length) {
    if (++markers > 4096 || input[offset++] !== 255) invalid("Invalid JPEG marker structure.");
    while (input[offset] === 255) offset++;
    const marker = input[offset++];
    if (marker === 217) {
      if (!scans || offset !== input.length)
        invalid("JPEG contains missing pixels or trailing images.");
      ended = true;
      break;
    }
    if (marker === void 0 || marker === 0 || marker === 216 || marker >= 208 && marker <= 215)
      invalid("Invalid JPEG marker.");
    if (offset + 2 > input.length) invalid("Truncated JPEG segment.");
    const length = input.readUInt16BE(offset), end = offset + length;
    if (length < 2 || end > input.length) invalid("Truncated JPEG segment.");
    const payload = input.subarray(offset + 2, end);
    if (marker >= 224 && marker <= 239 || marker === 254) {
      metadata += payload.length;
      if (metadata > 131072 || payload.subarray(0, 4).toString("ascii") === "MPF\0")
        invalid("JPEG metadata or image count exceeds its budget.");
    } else if (marker === 192 || marker === 194) {
      if (width || payload.length < 6 || payload[0] !== 8 || ![1, 3].includes(payload[5]))
        invalid("Use one 8-bit grayscale or RGB JPEG.");
      height = payload.readUInt16BE(1);
      width = payload.readUInt16BE(3);
      dimensions(width, height);
      if (payload.length !== 6 + 3 * payload[5]) invalid("Invalid JPEG frame header.");
    } else if (marker === 218) {
      if (!width || ++scans > 128) invalid("Invalid JPEG scan budget.");
      offset = end;
      while (offset < input.length) {
        if (input[offset] !== 255) {
          offset++;
          continue;
        }
        let next = offset + 1;
        while (input[next] === 255) next++;
        const code = input[next];
        if (code === 0 || code !== void 0 && code >= 208 && code <= 215) {
          offset = next + 1;
          continue;
        }
        break;
      }
      continue;
    } else if (![196, 219, 221].includes(marker)) invalid("Unsupported JPEG coding format.");
    offset = end;
  }
  if (!ended || !width) invalid("JPEG end or image header is missing.");
  return { input, width, height };
}
var active = 0;
async function decodeReferenceImage(value, mime) {
  if (value.byteLength < 16 || value.byteLength > REFERENCE_IMAGE_LIMITS.originalBytes)
    invalid("Reference upload must be nonempty and at most 2 MiB.");
  if (active >= 2) invalid("Reference decoder is busy. Retry later.");
  const original = Buffer.from(value);
  const checked = mime === "image/png" ? png(original) : jpeg(original);
  active++;
  try {
    const decoder = sharp(checked.input, {
      failOn: "warning",
      limitInputPixels: REFERENCE_IMAGE_LIMITS.pixels,
      limitInputChannels: 4,
      unlimited: false
    });
    const metadata = await decoder.timeout({ seconds: 3 }).metadata();
    if ((metadata.pages ?? 1) !== 1 || metadata.width !== checked.width || metadata.height !== checked.height)
      invalid("Reference image pages or dimensions do not match.");
    const { data, info } = await decoder.timeout({ seconds: 3 }).autoOrient().toColourspace("srgb").ensureAlpha().raw({ depth: "uchar" }).toBuffer({ resolveWithObject: true });
    dimensions(info.width, info.height);
    if (info.channels !== 4 || data.length !== info.width * info.height * 4)
      invalid("Invalid decoded reference pixels.");
    for (let i = 0; i < data.length; i += 4) if (data[i + 3] === 0) data.fill(0, i, i + 3);
    const canonical = await sharp(data, {
      raw: { width: info.width, height: info.height, channels: 4, premultiplied: false }
    }).timeout({ seconds: 3 }).png({ palette: false, progressive: false, compressionLevel: 6 }).toBuffer();
    if (canonical.length > REFERENCE_IMAGE_LIMITS.canonicalBytes)
      invalid("Canonical reference exceeds its byte limit.");
    return {
      original,
      canonical,
      rgba: data,
      width: info.width,
      height: info.height,
      decoder: {
        id: "sharp",
        version: sharp.versions.sharp,
        libvips: sharp.versions.vips
      }
    };
  } catch (cause) {
    if (cause instanceof YardError) throw cause;
    return invalid("Reference image decoding failed.");
  } finally {
    active--;
  }
}

// birdsong-yard-sprites/src/lib/server/reference-admission/files.ts
import { createHash as createHash5, randomUUID as randomUUID2 } from "node:crypto";
import {
  closeSync as closeSync2,
  constants as constants2,
  existsSync,
  fstatSync as fstatSync2,
  fsyncSync,
  linkSync,
  lstatSync as lstatSync2,
  openSync as openSync2,
  readSync,
  realpathSync as realpathSync2,
  unlinkSync,
  writeFileSync
} from "node:fs";
import { dirname as dirname2, join, relative, resolve, sep } from "node:path";
import { z as z23 } from "zod";
var referenceHash2 = (bytes3) => createHash5("sha256").update(bytes3).digest("hex");
var tables = [
  [
    "reference_admission_migrations",
    "CREATE TABLE reference_admission_migrations(version INTEGER PRIMARY KEY)"
  ],
  [
    "reference_admission_identity",
    "CREATE TABLE reference_admission_identity(singleton INTEGER PRIMARY KEY CHECK(singleton=1), database_id TEXT NOT NULL UNIQUE)"
  ],
  [
    "reference_files",
    `CREATE TABLE reference_files(id TEXT PRIMARY KEY, owner_id TEXT NOT NULL, request_id TEXT NOT NULL, request_digest TEXT NOT NULL, record_json TEXT NOT NULL, UNIQUE(owner_id,request_id))`
  ],
  [
    "reference_reviews",
    `CREATE TABLE reference_reviews(reference_id TEXT NOT NULL, owner_id TEXT NOT NULL, kind TEXT NOT NULL, request_id TEXT NOT NULL, review_json TEXT NOT NULL, PRIMARY KEY(reference_id,kind), UNIQUE(owner_id,request_id))`
  ],
  [
    "reference_revocations",
    `CREATE TABLE reference_revocations(reference_id TEXT PRIMARY KEY, owner_id TEXT NOT NULL, request_id TEXT NOT NULL, revocation_json TEXT NOT NULL, UNIQUE(owner_id,request_id))`
  ]
];
var REFERENCE_SCHEMA = [
  ...tables.map(([name, sql]) => [name, "table", sql]),
  ...tables.flatMap(
    ([name]) => ["UPDATE", "DELETE"].map(
      (operation) => [
        `${name}_${operation.toLowerCase()}_denied`,
        "trigger",
        `CREATE TRIGGER ${name}_${operation.toLowerCase()}_denied BEFORE ${operation} ON ${name} BEGIN SELECT RAISE(ABORT, 'Reference admission history is immutable'); END`
      ]
    )
  )
];
var normalize = (sql) => sql.replace(/\s+/g, " ").replace(/\s*([(),;])\s*/g, "$1").trim().replace(/;$/, "").toLowerCase();
function referenceAdmissionInitialized(database) {
  const actual = database.prepare(
    "SELECT name,type,sql FROM sqlite_master WHERE sql IS NOT NULL AND (name LIKE 'reference_admission_%' OR name LIKE 'reference_files%' OR name LIKE 'reference_reviews%' OR name LIKE 'reference_revocations%' OR tbl_name IN ('reference_admission_migrations','reference_admission_identity','reference_files','reference_reviews','reference_revocations'))"
  ).all();
  if (!actual.length) return false;
  if (actual.length !== REFERENCE_SCHEMA.length)
    throw new Error("Incomplete reference admission schema.");
  for (const [name, type, sql] of REFERENCE_SCHEMA) {
    const row = actual.find((entry) => entry.name === name && entry.type === type);
    if (typeof row?.sql !== "string" || normalize(row.sql) !== normalize(sql))
      throw new Error("Unsupported reference admission schema.");
  }
  const migrations = database.prepare("SELECT version FROM reference_admission_migrations").all();
  if (migrations.length !== 1 || migrations[0]?.version !== 1)
    throw new Error("Unsupported reference admission version.");
  return true;
}
function prospectiveRealPath(path) {
  if (existsSync(path)) return realpathSync2(path);
  const parent = dirname2(path);
  if (parent === path) throw new Error("Private reference directory is unavailable.");
  return join(prospectiveRealPath(parent), relative(parent, path));
}
function referenceDirectory(root2, publicRoots, create) {
  const path = resolve(root2), real = prospectiveRealPath(path);
  for (const item of publicRoots) {
    const publicPath = prospectiveRealPath(resolve(item)), rel = relative(publicPath, real);
    if (!rel || !rel.startsWith(`..${sep}`) && rel !== ".." && !rel.startsWith(sep))
      throw new Error("References require private storage outside public roots.");
  }
  if (create) ensurePrivateDirectory(path);
  const stat = lstatSync2(path);
  if (!stat.isDirectory() || stat.isSymbolicLink() || (stat.mode & 63) !== 0)
    throw new Error("Invalid private reference directory.");
  return realpathSync2(path);
}
function readPrivate(path, maximum, exact, hash5) {
  const directory = lstatSync2(dirname2(path));
  if (!directory.isDirectory() || directory.isSymbolicLink() || (directory.mode & 63) !== 0)
    throw new Error("Invalid private reference directory.");
  const fd = openSync2(path, constants2.O_RDONLY | constants2.O_NOFOLLOW | constants2.O_NONBLOCK);
  try {
    const stat = fstatSync2(fd);
    if (!stat.isFile() || (stat.mode & 63) !== 0 || stat.nlink !== 1 || stat.size < 1 || stat.size > maximum || exact !== void 0 && stat.size !== exact)
      throw new Error("Invalid private reference file.");
    const value = Buffer.alloc(stat.size);
    let offset = 0;
    while (offset < value.length) {
      const n = readSync(fd, value, offset, value.length - offset, offset);
      if (!n) throw new Error("Incomplete private reference file.");
      offset += n;
    }
    if (hash5 !== void 0 && referenceHash2(value) !== hash5)
      throw new Error("Private reference integrity failed.");
    return value;
  } finally {
    closeSync2(fd);
  }
}
function syncDirectory(path) {
  const fd = openSync2(path, constants2.O_RDONLY | constants2.O_DIRECTORY | constants2.O_NOFOLLOW);
  try {
    fsyncSync(fd);
  } finally {
    closeSync2(fd);
  }
}
function publishPrivate(path, bytes3) {
  const part = join(dirname2(path), `${randomUUID2()}.part`);
  const fd = openSync2(
    part,
    constants2.O_CREAT | constants2.O_EXCL | constants2.O_WRONLY | constants2.O_NOFOLLOW,
    384
  );
  try {
    writeFileSync(fd, bytes3);
    fsyncSync(fd);
  } finally {
    closeSync2(fd);
  }
  try {
    linkSync(part, path);
  } finally {
    unlinkSync(part);
  }
  syncDirectory(dirname2(path));
}
var storeIdentitySchema = z23.object({ schemaVersion: z23.literal(1), databaseId: z23.string().uuid() }).strict();
function readStoreIdentity(root2) {
  return storeIdentitySchema.parse(
    JSON.parse(readPrivate(join(root2, "identity.json"), 4096).toString("utf8"))
  );
}
var tombstoneSchema = z23.object({
  schemaVersion: z23.literal(1),
  databaseId: z23.string().uuid(),
  ownerId: idSchema,
  referenceId: z23.string().uuid(),
  contentDigest: z23.string().regex(/^[a-f0-9]{64}$/),
  revocation: referenceRevocationSchema
}).strict();
function readReferenceBytes(root2, record) {
  const id8 = record.identity.id;
  return {
    original: readPrivate(
      join(root2, `${id8}.original`),
      REFERENCE_IMAGE_LIMITS.originalBytes,
      record.identity.original.bytes,
      record.identity.original.sha256
    ),
    canonical: readPrivate(
      join(root2, `${id8}.canonical.png`),
      REFERENCE_IMAGE_LIMITS.canonicalBytes,
      record.identity.canonical.bytes,
      record.identity.canonical.sha256
    ),
    rgba: readPrivate(
      join(root2, `${id8}.rgba`),
      REFERENCE_IMAGE_LIMITS.pixels * 4,
      record.identity.canonical.width * record.identity.canonical.height * 4,
      record.identity.canonical.rgbaSha256
    )
  };
}

// birdsong-yard-sprites/src/lib/server/reference-admission/rights.ts
var conflict = (message) => {
  throw new YardError("CONFLICT", message);
};
function assertDiscoveredRights(file, review2) {
  if (file.source.kind !== "retained-discovery" || review2.kind !== "rights" || review2.decision !== "approved")
    return;
  const candidate = file.source.candidate;
  if (evaluateReferenceRights(candidate.license, candidate.creator, {
    schemaVersion: 1,
    purpose: "derived-sprite",
    commercial: true,
    allowShareAlike: false
  }).status !== "eligible-for-review" || review2.licenseId !== candidate.license.id || review2.licenseVersion !== candidate.license.version || review2.licenseUrl !== candidate.license.url || review2.creator !== candidate.creator || review2.attribution !== candidate.license.attribution)
    conflict(
      "Reference rights cannot override retained source declarations or unsupported restrictions."
    );
}

// birdsong-yard-sprites/src/lib/server/reference-admission/service.ts
var uuid = z24.string().uuid();
var unavailable2 = () => {
  throw new YardError("CONFLICT", "Private reference integrity is unavailable.");
};
var conflict2 = (message) => {
  throw new YardError("CONFLICT", message);
};
var missing = () => {
  throw new YardError("NOT_FOUND", "Reference was not found.");
};
var parseJson = (value) => {
  if (typeof value !== "string" || Buffer.byteLength(value, "utf8") > 65536) return unavailable2();
  return JSON.parse(value);
};
function persistedJson(value) {
  const result2 = canonicalJson2(value);
  if (Buffer.byteLength(result2, "utf8") > 65536)
    throw new YardError("INVALID", "Reference metadata exceeds its storage budget.");
  return result2;
}
var ReferenceAdmissionService = class {
  constructor(database, root2, options = {}) {
    this.database = database;
    this.options = options;
    this.now = options.now ?? (() => (/* @__PURE__ */ new Date()).toISOString());
    const initialized = referenceAdmissionInitialized(database);
    if (database.isTransaction && !initialized)
      conflict2("Reference admission must be initialized before this transaction.");
    this.root = referenceDirectory(
      root2,
      options.publicRoots ?? [
        resolve2("static"),
        resolve2("public"),
        resolve2("build/client"),
        resolve2(".svelte-kit/output/client")
      ],
      !database.isTransaction
    );
    if (!initialized) {
      if (readdirSync(this.root).some((name) => name !== "identity.json" && name !== "revocations"))
        unavailable2();
      const revoked = join2(this.root, "revocations");
      if (existsSync2(revoked) && readdirSync(revoked).length) unavailable2();
      const identity = existsSync2(join2(this.root, "identity.json")) ? readStoreIdentity(this.root) : { schemaVersion: 1, databaseId: randomUUID3() };
      this.transaction(() => {
        for (const [, , sql] of REFERENCE_SCHEMA) database.exec(sql);
        database.prepare("INSERT INTO reference_admission_migrations(version) VALUES(1)").run();
        database.prepare("INSERT INTO reference_admission_identity(singleton,database_id) VALUES(1,?)").run(identity.databaseId);
        ensurePrivateDirectory(revoked);
        if (!existsSync2(join2(this.root, "identity.json")))
          publishPrivate(join2(this.root, "identity.json"), Buffer.from(canonicalJson2(identity)));
      });
    }
    const row = database.prepare("SELECT database_id FROM reference_admission_identity WHERE singleton=1").get();
    this.databaseId = uuid.parse(row?.database_id);
    this.assertStore();
  }
  database;
  options;
  root;
  databaseId;
  now;
  timestamp() {
    return z24.string().datetime().parse(this.now());
  }
  transaction(action) {
    if (this.database.isTransaction) conflict2("Reference mutation requires its own transaction.");
    this.database.exec("BEGIN IMMEDIATE");
    try {
      const value = action();
      this.database.exec("COMMIT");
      return value;
    } catch (error) {
      this.database.exec("ROLLBACK");
      throw error;
    }
  }
  assertStore() {
    try {
      if (readStoreIdentity(this.root).databaseId !== this.databaseId) unavailable2();
      referenceDirectory(join2(this.root, "revocations"), [], false);
      if (readdirSync(this.root).length > 512) unavailable2();
    } catch {
      unavailable2();
    }
  }
  tombstone(id8) {
    uuid.parse(id8);
    this.assertStore();
    const path = join2(this.root, "revocations", `${id8}.json`);
    try {
      lstatSync3(path);
    } catch (error) {
      if (error && typeof error === "object" && "code" in error && error.code === "ENOENT")
        return null;
      return unavailable2();
    }
    try {
      const value = tombstoneSchema.parse(JSON.parse(readPrivate(path, 16384).toString("utf8")));
      if (value.databaseId !== this.databaseId || value.referenceId !== id8) unavailable2();
      return value;
    } catch {
      return unavailable2();
    }
  }
  base(owner, id8) {
    idSchema.parse(owner);
    uuid.parse(id8);
    this.assertStore();
    const row = this.database.prepare("SELECT record_json FROM reference_files WHERE owner_id=? AND id=?").get(owner, id8);
    if (!row) return missing();
    try {
      const file = referenceAdmissionRecordSchema.parse(parseJson(row.record_json));
      if (file.identity.id !== id8 || digest({ identity: file.identity, source: file.source }) !== file.contentDigest || Object.values(file.reviews).some(Boolean) || file.revocation || digest({ contentDigest: file.contentDigest, reviews: file.reviews }) !== file.reviewDigest)
        unavailable2();
      return file;
    } catch {
      return unavailable2();
    }
  }
  get(owner, id8) {
    const file = this.base(owner, id8);
    try {
      const rows = this.database.prepare(
        "SELECT kind,review_json FROM reference_reviews WHERE owner_id=? AND reference_id=?"
      ).all(owner, id8);
      for (const row of rows) {
        const event = referenceReviewSchema.parse(parseJson(row.review_json));
        if (event.kind !== row.kind || event.reviewerId !== owner) unavailable2();
        if (event.kind === "rights") file.reviews.rights = event;
        else if (event.kind === "species") file.reviews.species = event;
        else file.reviews.pose = event;
      }
      const external = this.tombstone(id8), stored = this.database.prepare(
        "SELECT revocation_json FROM reference_revocations WHERE owner_id=? AND reference_id=?"
      ).get(owner, id8);
      if (external && (external.ownerId !== owner || external.contentDigest !== file.contentDigest))
        unavailable2();
      if (stored && (!external || digest(parseJson(stored.revocation_json)) !== digest(external.revocation)))
        unavailable2();
      file.revocation = external?.revocation ?? null;
      file.reviewDigest = digest({ contentDigest: file.contentDigest, reviews: file.reviews });
      return referenceAdmissionRecordSchema.parse(file);
    } catch {
      return unavailable2();
    }
  }
  list(owner) {
    idSchema.parse(owner);
    this.assertStore();
    const rows = this.database.prepare("SELECT id FROM reference_files WHERE owner_id=? ORDER BY rowid LIMIT 17").all(owner);
    if (rows.length > 16) unavailable2();
    return rows.map((row) => this.get(owner, uuid.parse(row.id)));
  }
  prior(owner, requestId) {
    return this.database.prepare("SELECT id,request_digest FROM reference_files WHERE owner_id=? AND request_id=?").get(owner, requestId);
  }
  assertUnusedRequest(owner, requestId) {
    for (const table of ["reference_files", "reference_reviews", "reference_revocations"]) {
      if (this.database.prepare(`SELECT 1 FROM ${table} WHERE owner_id=? AND request_id=?`).get(owner, requestId))
        conflict2("Reference request ID is already used.");
    }
    const names = readdirSync(join2(this.root, "revocations"));
    if (names.length > 64) unavailable2();
    for (const name of names) {
      if (!/^[a-f0-9-]{36}\.json$/.test(name)) unavailable2();
      const event = this.tombstone(name.slice(0, -5));
      if (event?.ownerId === owner && event.revocation.requestId === requestId)
        conflict2("Reference request ID is already used.");
    }
  }
  async upload(owner, requestId, bytes3, mime) {
    return this.admit(owner, requestId, bytes3, mime, { kind: "owner-upload" });
  }
  async admit(owner, requestId, bytes3, mime, sourceValue) {
    idSchema.parse(owner);
    uuid.parse(requestId);
    z24.enum(["image/png", "image/jpeg"]).parse(mime);
    this.assertStore();
    if (!(bytes3 instanceof Uint8Array) || bytes3.byteLength > REFERENCE_IMAGE_LIMITS.originalBytes)
      throw new YardError("INVALID", "Reference upload exceeds its byte limit.");
    const original = Buffer.from(bytes3);
    const source = referenceAdmissionSourceSchema.parse(sourceValue), requestDigest = digest({ sha256: referenceHash(original), mime, source });
    const retry = this.prior(owner, requestId);
    if (retry) {
      if (retry.request_digest !== requestDigest)
        conflict2("Reference request ID has different content.");
      return this.get(owner, uuid.parse(retry.id));
    }
    const decoded = await decodeReferenceImage(original, mime);
    return this.transaction(() => {
      this.assertStore();
      const raced = this.prior(owner, requestId);
      if (raced) {
        if (raced.request_digest !== requestDigest)
          conflict2("Reference request ID has different content.");
        return this.get(owner, uuid.parse(raced.id));
      }
      this.assertUnusedRequest(owner, requestId);
      const owned = this.database.prepare("SELECT COUNT(*) AS n FROM reference_files WHERE owner_id=?").get(owner), total = this.database.prepare("SELECT COUNT(*) AS n FROM reference_files").get();
      if (Number(owned?.n) >= 16 || Number(total?.n) >= 64)
        conflict2("Private reference capacity reached.");
      const id8 = randomUUID3(), identity = {
        schemaVersion: 1,
        id: id8,
        original: {
          sha256: referenceHash(decoded.original),
          bytes: decoded.original.length,
          mime
        },
        canonical: {
          sha256: referenceHash(decoded.canonical),
          bytes: decoded.canonical.length,
          width: decoded.width,
          height: decoded.height,
          rgbaSha256: referenceHash(decoded.rgba)
        },
        decoder: decoded.decoder,
        normalization: "chirp-reference-straight-srgb8-oriented-hidden-rgb-zero-v1"
      };
      const contentDigest = digest({ identity, source }), reviews = { rights: null, species: null, pose: null };
      const file = referenceAdmissionRecordSchema.parse({
        identity,
        contentDigest,
        reviewDigest: digest({ contentDigest, reviews }),
        source,
        createdAt: this.timestamp(),
        reviews,
        revocation: null
      });
      const json2 = persistedJson(file);
      publishPrivate(join2(this.root, `${id8}.original`), decoded.original);
      publishPrivate(join2(this.root, `${id8}.canonical.png`), decoded.canonical);
      publishPrivate(join2(this.root, `${id8}.rgba`), decoded.rgba);
      this.options.failpoint?.("files-published");
      this.database.prepare(
        "INSERT INTO reference_files(id,owner_id,request_id,request_digest,record_json) VALUES(?,?,?,?,?)"
      ).run(id8, owner, requestId, requestDigest, json2);
      return file;
    });
  }
  review(owner, id8, value) {
    const command = referenceReviewCommandSchema.parse(value);
    return this.transaction(() => {
      const file = this.get(owner, id8), prior = file.reviews[command.kind];
      if (prior) {
        const original = Object.fromEntries(
          Object.entries(prior).filter(([key]) => key !== "reviewerId" && key !== "reviewedAt")
        );
        if (digest(original) !== digest(command)) conflict2("Reference review is immutable.");
        return file;
      }
      if (file.revocation) conflict2("Reference is terminally revoked.");
      if (command.decision === "approved") this.verifiedBytes(file);
      this.assertUnusedRequest(owner, command.requestId);
      const event = referenceReviewSchema.parse({
        ...command,
        reviewerId: owner,
        reviewedAt: this.timestamp()
      });
      assertDiscoveredRights(file, event);
      this.database.prepare(
        "INSERT INTO reference_reviews(reference_id,owner_id,kind,request_id,review_json) VALUES(?,?,?,?,?)"
      ).run(id8, owner, event.kind, event.requestId, persistedJson(event));
      return this.get(owner, id8);
    });
  }
  revoke(owner, id8, value) {
    const command = referenceRevokeCommandSchema.parse(value);
    return this.transaction(() => {
      const file = this.get(owner, id8);
      let event = file.revocation;
      if (event) {
        if (event.requestId !== command.requestId || event.reason !== command.reason)
          conflict2("Reference revocation is terminal.");
      } else {
        this.assertUnusedRequest(owner, command.requestId);
        event = referenceRevocationSchema.parse({
          ...command,
          reviewerId: owner,
          revokedAt: this.timestamp()
        });
        referenceAdmissionRecordSchema.parse({ ...file, revocation: event });
        publishPrivate(
          join2(this.root, "revocations", `${id8}.json`),
          Buffer.from(
            canonicalJson2(
              tombstoneSchema.parse({
                schemaVersion: 1,
                databaseId: this.databaseId,
                ownerId: owner,
                referenceId: id8,
                contentDigest: file.contentDigest,
                revocation: event
              })
            )
          )
        );
        this.options.failpoint?.("revocation-published");
      }
      this.database.prepare(
        "INSERT OR IGNORE INTO reference_revocations(reference_id,owner_id,request_id,revocation_json) VALUES(?,?,?,?)"
      ).run(id8, owner, event.requestId, persistedJson(event));
      return this.get(owner, id8);
    });
  }
  readCanonical(owner, id8) {
    const file = this.get(owner, id8);
    try {
      return readPrivate(
        join2(this.root, `${id8}.canonical.png`),
        REFERENCE_IMAGE_LIMITS.canonicalBytes,
        file.identity.canonical.bytes,
        file.identity.canonical.sha256
      );
    } catch {
      return unavailable2();
    }
  }
  resolve(owner, value, speciesId) {
    const pin = referenceAdmissionPinSchema.parse(value), record = this.get(owner, pin.referenceId);
    if (pin.contentDigest !== record.contentDigest || pin.reviewDigest !== record.reviewDigest || record.revocation || record.reviews.rights?.decision !== "approved" || record.reviews.species?.decision !== "approved" || record.reviews.pose?.decision !== "approved" || record.reviews.species.speciesId !== speciesId)
      conflict2("Reference pin is not currently approved for this species.");
    assertDiscoveredRights(record, record.reviews.rights);
    return { record, ...this.verifiedBytes(record) };
  }
  verifiedBytes(record) {
    try {
      return readReferenceBytes(this.root, record);
    } catch {
      return unavailable2();
    }
  }
  assertPinsCurrent(owner, pins, speciesId) {
    if (pins.length < 1 || pins.length > 16) conflict2("Reference pin count exceeds its budget.");
    for (const pin of pins) this.resolve(owner, pin, speciesId);
  }
  async admitDiscovered(owner, requestId, pinValue, candidateValue, requestValue, registry, signal) {
    idSchema.parse(owner);
    uuid.parse(requestId);
    this.assertStore();
    const discoveryPin = animationPinSchema.parse(pinValue), candidate = discoveredReferenceSchema.parse(candidateValue);
    if (candidate.declaredBytes > REFERENCE_IMAGE_LIMITS.originalBytes)
      throw new YardError("INVALID", "Reference original exceeds the admission byte limit.");
    if (candidate.width > REFERENCE_IMAGE_LIMITS.side || candidate.height > REFERENCE_IMAGE_LIMITS.side || candidate.width * candidate.height > REFERENCE_IMAGE_LIMITS.pixels)
      throw new YardError("INVALID", "Reference dimensions exceed the admission limit.");
    const prior = this.prior(owner, requestId);
    if (prior) {
      const file = this.get(owner, uuid.parse(prior.id));
      if (file.source.kind !== "retained-discovery" || digest(file.source.discoveryPin) !== digest(discoveryPin) || digest(file.source.candidate) !== digest(candidate))
        conflict2("Reference request ID has different discovery content.");
      return file;
    }
    this.assertUnusedRequest(owner, requestId);
    if (candidate.mime !== "image/png" && candidate.mime !== "image/jpeg")
      throw new YardError("INVALID", "Only PNG or JPEG reference originals are supported.");
    const result2 = await fetchDiscoveredOriginal(
      candidate,
      requestValue,
      registry,
      signal ? { signal } : {}
    );
    if (createHash6("sha1").update(result2.bytes).digest("hex") !== result2.receipt.sha1)
      throw new YardError("INVALID", "Reference fetch identity does not match its bytes.");
    return this.admit(owner, requestId, result2.bytes, result2.receipt.mime, {
      kind: "retained-discovery",
      discoveryPin,
      candidateId: candidate.id,
      candidate,
      receipt: result2.receipt
    });
  }
};

// birdsong-yard-sprites/src/lib/server/reference-admission/recovery.ts
import { readdirSync as readdirSync2 } from "node:fs";
import { join as join3 } from "node:path";
import { z as z26 } from "zod";

// birdsong-yard-sprites/src/lib/assets/reference-recovery.ts
import { z as z25 } from "zod";
var REFERENCE_AUTHORITY_MAX_BYTES = 8 * 1024 * 1024;
var entrySchema = z25.object({
  ownerId: idSchema,
  requestId: z25.string().uuid(),
  requestDigest: z25.string().regex(/^[a-f0-9]{64}$/),
  record: referenceAdmissionRecordSchema
}).strict();
var referenceAuthoritySchema = z25.object({
  schemaVersion: z25.literal(1),
  kind: z25.literal("reference-authority"),
  databaseId: z25.string().uuid(),
  entries: z25.array(entrySchema).max(64)
}).strict().superRefine((value, context2) => {
  const owners = /* @__PURE__ */ new Map();
  let previous;
  for (const [index, entry] of value.entries.entries()) {
    const fail = (message) => context2.addIssue({ code: "custom", path: ["entries", index], message });
    const identity = entry.record.identity.id;
    if (previous !== void 0 && previous >= identity)
      fail("Reference identities must be unique and strictly ASCII sorted.");
    previous = identity;
    const owner = owners.get(entry.ownerId) ?? { count: 0, requests: /* @__PURE__ */ new Set() };
    owners.set(entry.ownerId, owner);
    if (++owner.count > 16) fail("A reference authority permits at most 16 records per owner.");
    const request = (requestId) => {
      if (owner.requests.has(requestId))
        fail("Admission, review and revocation request IDs must be unique per owner.");
      owner.requests.add(requestId);
    };
    request(entry.requestId);
    const events = [...Object.values(entry.record.reviews), entry.record.revocation];
    for (const event of events) {
      if (event === null) continue;
      if (event.reviewerId !== entry.ownerId)
        fail("Every review and revocation must belong to the admitted reference owner.");
      request(event.requestId);
    }
    if (new TextEncoder().encode(JSON.stringify(entry.record)).byteLength > 65536)
      fail("Canonical reference metadata exceeds 65536 bytes.");
  }
});

// birdsong-yard-sprites/src/lib/server/reference-admission/recovery.ts
var uuid2 = z26.string().uuid();
var sha2564 = z26.string().regex(/^[a-f0-9]{64}$/);
var fileRow = z26.object({
  id: uuid2,
  owner_id: idSchema,
  request_id: uuid2,
  request_digest: sha2564,
  record_json: z26.string().max(65536)
}).strict();
var reviewRow = z26.object({
  reference_id: uuid2,
  owner_id: idSchema,
  kind: z26.enum(["rights", "species", "pose"]),
  request_id: uuid2,
  review_json: z26.string().max(65536)
}).strict();
var revokeRow = z26.object({
  reference_id: uuid2,
  owner_id: idSchema,
  request_id: uuid2,
  revocation_json: z26.string().max(65536)
}).strict();
function invalid2() {
  throw new Error("reference_authority_invalid");
}
function json(value) {
  if (Buffer.byteLength(value) > 65536) invalid2();
  const parsed = JSON.parse(value);
  if (canonicalJson2(parsed) !== value) invalid2();
  return parsed;
}
function base(record) {
  const reviews = { rights: null, species: null, pose: null };
  return {
    ...record,
    reviews,
    revocation: null,
    reviewDigest: digest({ contentDigest: record.contentDigest, reviews })
  };
}
function encodeAuthority(authority) {
  return "{" + Object.entries(authority).sort(([a], [b]) => a < b ? -1 : a > b ? 1 : 0).map(
    ([key, value]) => JSON.stringify(key) + ":" + (key === "entries" ? "[" + authority.entries.map((entry) => canonicalJson2(entry)).join(",") + "]" : canonicalJson2(value))
  ).join(",") + "}\n";
}
function validateReferenceAuthority(value) {
  const authority = referenceAuthoritySchema.parse(value);
  for (const entry of authority.entries) {
    const record = entry.record;
    if (digest({ identity: record.identity, source: record.source }) !== record.contentDigest || digest({ contentDigest: record.contentDigest, reviews: record.reviews }) !== record.reviewDigest || digest({
      sha256: record.identity.original.sha256,
      mime: record.identity.original.mime,
      source: record.source
    }) !== entry.requestDigest)
      invalid2();
    if (record.reviews.rights) assertDiscoveredRights(record, record.reviews.rights);
  }
  if (Buffer.byteLength(encodeAuthority(authority)) > REFERENCE_AUTHORITY_MAX_BYTES) invalid2();
  return authority;
}
function exportReferenceAuthority(database, root2) {
  database.exec("SAVEPOINT reference_authority_snapshot");
  try {
    if (!referenceAdmissionInitialized(database)) invalid2();
    referenceDirectory(root2, [], false);
    referenceDirectory(join3(root2, "revocations"), [], false);
    const identityRows = database.prepare("SELECT singleton,database_id FROM reference_admission_identity").all();
    if (identityRows.length !== 1) invalid2();
    const identity = z26.object({ singleton: z26.literal(1), database_id: uuid2 }).strict().parse(identityRows[0]);
    if (readStoreIdentity(root2).databaseId !== identity.database_id) invalid2();
    const rows = database.prepare("SELECT * FROM reference_files ORDER BY id LIMIT 65").all().map((row) => fileRow.parse(row));
    if (rows.length > 64) invalid2();
    const entries = rows.map((row) => {
      const record = referenceAdmissionRecordSchema.parse(json(row.record_json));
      if (record.identity.id !== row.id || canonicalJson2(record) !== canonicalJson2(base(record)))
        invalid2();
      readReferenceBytes(root2, record);
      return {
        ownerId: row.owner_id,
        requestId: row.request_id,
        requestDigest: row.request_digest,
        record
      };
    });
    const byId = new Map(entries.map((entry) => [entry.record.identity.id, entry]));
    const reviews = database.prepare("SELECT * FROM reference_reviews LIMIT 193").all().map((row) => reviewRow.parse(row));
    if (reviews.length > 192) invalid2();
    for (const row of reviews) {
      const entry = byId.get(row.reference_id);
      const event = referenceReviewSchema.parse(json(row.review_json));
      if (!entry || row.owner_id !== entry.ownerId || event.reviewerId !== entry.ownerId || event.kind !== row.kind || event.requestId !== row.request_id || entry.record.reviews[row.kind])
        invalid2();
      if (event.kind === "rights") entry.record.reviews.rights = event;
      else if (event.kind === "species") entry.record.reviews.species = event;
      else entry.record.reviews.pose = event;
    }
    const names = readdirSync2(join3(root2, "revocations"));
    if (names.length > 64) invalid2();
    for (const name of names) {
      if (!/^[a-f0-9-]{36}\.json$/.test(name)) invalid2();
      const bytes3 = readPrivate(join3(root2, "revocations", name), 16384);
      const tombstone = tombstoneSchema.parse(json(bytes3.toString("utf8")));
      const entry = byId.get(tombstone.referenceId);
      if (!entry || name !== `${tombstone.referenceId}.json` || tombstone.databaseId !== identity.database_id || tombstone.ownerId !== entry.ownerId || tombstone.contentDigest !== entry.record.contentDigest || tombstone.revocation.reviewerId !== entry.ownerId)
        invalid2();
      entry.record.revocation = tombstone.revocation;
    }
    const revocations = database.prepare("SELECT * FROM reference_revocations LIMIT 65").all().map((row) => revokeRow.parse(row));
    if (revocations.length > 64) invalid2();
    for (const row of revocations) {
      const entry = byId.get(row.reference_id);
      const event = referenceRevocationSchema.parse(json(row.revocation_json));
      if (!entry || entry.ownerId !== row.owner_id || event.requestId !== row.request_id || canonicalJson2(entry.record.revocation) !== canonicalJson2(event))
        invalid2();
    }
    const expectedNames = /* @__PURE__ */ new Set([
      "identity.json",
      "revocations",
      ...entries.flatMap(
        ({ record }) => ["original", "canonical.png", "rgba"].map((suffix) => `${record.identity.id}.${suffix}`)
      )
    ]);
    const actualNames = readdirSync2(root2);
    if (actualNames.length !== expectedNames.size || actualNames.some((name) => !expectedNames.has(name)))
      invalid2();
    for (const { record } of entries)
      record.reviewDigest = digest({
        contentDigest: record.contentDigest,
        reviews: record.reviews
      });
    const authority = validateReferenceAuthority({
      schemaVersion: 1,
      kind: "reference-authority",
      databaseId: identity.database_id,
      entries
    });
    database.exec("RELEASE reference_authority_snapshot");
    return authority;
  } catch (error) {
    database.exec("ROLLBACK TO reference_authority_snapshot; RELEASE reference_authority_snapshot");
    throw error;
  }
}

// birdsong-yard-sprites/src/lib/assets/lifecycle-contracts.ts
import { z as z28 } from "zod";

// birdsong-yard-sprites/src/lib/workbench/pagination.ts
import { z as z27 } from "zod";
var WORKBENCH_PAGE_SIZE = 5;
var WORKBENCH_PAGE_MAX = 10;
var WORKBENCH_RESPONSE_BYTES = 8 * 1024 * 1024;
var pageCursorSchema = z27.string().min(1).max(512).regex(/^[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+$/);
var pageRequestSchema = z27.object({
  cursor: pageCursorSchema.optional(),
  limit: z27.number().int().min(1).max(WORKBENCH_PAGE_MAX).default(WORKBENCH_PAGE_SIZE)
}).strict();
var pageInfoSchema = z27.object({
  cursor: pageCursorSchema,
  nextCursor: pageCursorSchema.nullable(),
  limit: z27.number().int().min(1).max(WORKBENCH_PAGE_MAX)
}).strict();

// birdsong-yard-sprites/src/lib/assets/lifecycle-contracts.ts
var uuid3 = z28.string().uuid();
var revision = z28.number().int().min(0).max(1e6);
var time2 = z28.string().datetime().max(40);
var assetLifecycleTargetSchema = z28.object({
  kind: z28.enum(["private-file", "private-package"]),
  id: uuid3
}).strict();
var assetArchiveStateSchema = z28.object({
  target: assetLifecycleTargetSchema,
  revision,
  archived: z28.boolean(),
  changedAt: time2.nullable()
}).strict().superRefine((value, context2) => {
  if (value.revision === 0 !== (value.changedAt === null) || value.revision === 0 && value.archived)
    context2.addIssue({
      code: "custom",
      message: "Initial archive state must be active without a change timestamp."
    });
});
var assetLifecycleCommandSchema = z28.discriminatedUnion("action", [
  z28.object({
    action: z28.literal("set-archive"),
    requestId: uuid3,
    target: assetLifecycleTargetSchema,
    expectedRevision: revision,
    archived: z28.boolean()
  }).strict(),
  z28.object({
    action: z28.literal("unpin"),
    requestId: uuid3,
    birdId: idSchema,
    expectedArtworkId: idSchema
  }).strict(),
  z28.object({ action: z28.literal("restore-pin"), requestId: uuid3, unpinRequestId: uuid3 }).strict()
]);
var assetLifecycleReceiptSchema = z28.object({
  schemaVersion: z28.literal(1),
  command: assetLifecycleCommandSchema,
  commandDigest: z28.string().regex(/^[a-f0-9]{64}$/),
  previousArtworkId: idSchema.nullable(),
  savedAt: time2
}).strict().superRefine((value, context2) => {
  if (value.command.action === "unpin" !== (value.previousArtworkId !== null) || value.command.action === "unpin" && value.previousArtworkId !== value.command.expectedArtworkId)
    context2.addIssue({
      code: "custom",
      message: "Only unpin receipts retain the exact previous artwork."
    });
});
var assetRetentionReasonSchema = z28.enum([
  "active",
  "pinned-bird",
  "retained-artwork",
  "referenced-by-package",
  "file-review-evidence",
  "pipeline-history",
  "incomplete-reference-scan"
]);
var assetLifecycleEntrySchema = z28.object({
  state: assetArchiveStateSchema,
  label: z28.string().min(1).max(200),
  retainedBytes: z28.number().int().min(0).max(Number.MAX_SAFE_INTEGER),
  selectable: z28.boolean(),
  selectionBlock: z28.enum(["none", "archived", "archived-dependency", "unavailable"]),
  cleanupEligible: z28.boolean(),
  retainedBecause: z28.array(assetRetentionReasonSchema).max(7)
}).strict().superRefine((value, context2) => {
  if (value.selectable !== (value.selectionBlock === "none") || value.state.archived !== (value.selectionBlock === "archived") || value.cleanupEligible && (value.state.target.kind !== "private-file" || !value.state.archived || value.retainedBecause.length !== 0) || new Set(value.retainedBecause).size !== value.retainedBecause.length)
    context2.addIssue({
      code: "custom",
      message: "Lifecycle selection and retention state are inconsistent."
    });
});
var assetLifecycleOverviewSchema = z28.object({
  schemaVersion: z28.literal(1),
  purgeEnabled: z28.literal(false),
  sharedCatalog: z28.literal("read-only-not-owned"),
  referenceScan: z28.enum(["complete", "incomplete"]),
  entries: z28.array(assetLifecycleEntrySchema).max(576),
  pins: z28.array(
    z28.object({ birdId: idSchema, artworkId: idSchema, label: z28.string().min(1).max(200) }).strict()
  ).max(2048),
  undoPins: z28.array(
    z28.object({
      requestId: uuid3,
      birdId: idSchema,
      artworkId: idSchema,
      label: z28.string().min(1).max(200)
    }).strict()
  ).max(32)
}).strict().superRefine((value, context2) => {
  if (new Set(value.entries.map((entry) => `${entry.state.target.kind}/${entry.state.target.id}`)).size !== value.entries.length || new Set(value.pins.map((pin) => pin.birdId)).size !== value.pins.length || new Set(value.undoPins.map((pin) => pin.requestId)).size !== value.undoPins.length || value.referenceScan === "incomplete" && value.entries.some((entry) => entry.cleanupEligible))
    context2.addIssue({
      code: "custom",
      message: "Lifecycle overview identities or eligibility are inconsistent."
    });
});
var assetLifecycleResponseSchema = z28.object({
  overview: assetLifecycleOverviewSchema,
  receipt: z28.object({ requestId: uuid3, replayed: z28.boolean() }).strict()
}).strict();
var assetPackageHistorySchema = z28.object({
  schemaVersion: z28.literal(1),
  purgeEnabled: z28.literal(false),
  referenceScan: z28.literal("not-run"),
  entries: z28.array(assetLifecycleEntrySchema).max(WORKBENCH_PAGE_MAX),
  page: pageInfoSchema
}).strict().superRefine((value, context2) => {
  if (value.entries.length > value.page.limit || new Set(value.entries.map((entry) => entry.state.target.id)).size !== value.entries.length || value.entries.some(
    (entry) => entry.state.target.kind !== "private-package" || entry.cleanupEligible || !entry.retainedBecause.includes("pipeline-history") || !entry.retainedBecause.includes("incomplete-reference-scan")
  ))
    context2.addIssue({ code: "custom", message: "Package history cannot authorize cleanup." });
});

// birdsong-yard-sprites/src/lib/pipeline/contracts.ts
import { z as z29 } from "zod";
var pipelineIdentifierSchema = z29.string().min(1).max(200).regex(/\S/);
var identifier3 = pipelineIdentifierSchema;
var integer3 = z29.number().int().nonnegative().max(Number.MAX_SAFE_INTEGER);
var pipelineVersionSchema = integer3.positive();
var version = pipelineVersionSchema;
var pipelineTimeSchema = integer3.max(864e13);
var time3 = pipelineTimeSchema;
var errorCode = z29.string().regex(/^[a-z0-9_-]{1,80}$/).nullable();
var jobStatusSchema = z29.enum([
  "queued",
  "running",
  "retry_wait",
  "blocked_provider",
  "awaiting_review",
  "completed",
  "failed",
  "cancelled"
]);
var stageStatusSchema = z29.enum([
  "pending",
  "running",
  "retry_wait",
  "blocked_provider",
  "succeeded",
  "failed",
  "cancelled"
]);
var artifactProvenanceSchema = z29.object({
  source: z29.enum(["deterministic_fixture", "provider", "user_upload"]),
  providerId: identifier3,
  providerVersion: identifier3,
  references: z29.array(z29.string()),
  fixture: z29.boolean(),
  license: z29.string().optional()
}).strict().superRefine((value, context2) => {
  if (value.fixture !== (value.source === "deterministic_fixture"))
    context2.addIssue({
      code: "custom",
      message: "Fixture provenance must identify a deterministic fixture."
    });
});
var reviewCommandSchema = z29.object({
  artifactId: identifier3,
  decision: z29.enum(["approved", "rejected"]),
  note: z29.string().max(1e3)
}).strict();
function pipelineSchemas(payload) {
  const queueJobSchema2 = z29.object({
    definitionId: identifier3,
    definitionVersion: version,
    input: payload,
    idempotencyKey: identifier3,
    parentJobId: identifier3.optional()
  }).strict();
  const jobFields = queueJobSchema2.extend({
    id: identifier3,
    ownerId: identifier3,
    rootJobId: identifier3,
    inputDigest: z29.string().regex(/^[a-f0-9]{64}$/),
    status: jobStatusSchema,
    createdAt: time3,
    updatedAt: time3,
    error: errorCode
  }).strict();
  const checkJob = (value, context2) => {
    if (value.updatedAt < value.createdAt)
      context2.addIssue({ code: "custom", message: "Job update predates creation." });
    if (value.parentJobId === value.id || !value.parentJobId && value.rootJobId !== value.id)
      context2.addIssue({ code: "custom", message: "Invalid job ancestry." });
  };
  const pipelineJobSchema2 = jobFields.superRefine(checkJob);
  const stageRecordSchema2 = z29.object({
    jobId: identifier3,
    path: identifier3,
    version,
    ordinal: integer3.max(99),
    status: stageStatusSchema,
    attempts: integer3.max(10),
    maxAttempts: integer3.min(1).max(10),
    nextRunAt: time3.nullable(),
    leaseUntil: time3.nullable(),
    output: payload,
    error: errorCode
  }).strict().superRefine((value, context2) => {
    if (value.attempts > value.maxAttempts)
      context2.addIssue({ code: "custom", message: "Stage attempts exceed the retry policy." });
    if (value.status === "running" !== (value.leaseUntil !== null))
      context2.addIssue({ code: "custom", message: "Stage lease does not match its state." });
    if (value.status === "running" && (value.attempts === 0 || value.nextRunAt !== null))
      context2.addIssue({ code: "custom", message: "Running stage requires a claimed attempt." });
    if (value.status === "retry_wait" && value.nextRunAt === null)
      context2.addIssue({ code: "custom", message: "Retry stage requires its next run time." });
  });
  const stageRunSchema2 = z29.object({
    id: identifier3,
    jobId: identifier3,
    stagePath: identifier3,
    attempt: integer3.min(1).max(10),
    status: z29.enum([
      "running",
      "succeeded",
      "failed",
      "expired",
      "cancelled",
      "blocked_provider"
    ]),
    startedAt: time3,
    finishedAt: time3.nullable(),
    error: errorCode
  }).strict().superRefine((value, context2) => {
    if (value.status === "running" !== (value.finishedAt === null) || value.finishedAt !== null && value.finishedAt < value.startedAt)
      context2.addIssue({
        code: "custom",
        message: "Run completion time does not match its state."
      });
  });
  const artifactDraftSchema2 = z29.object({
    family: identifier3,
    kind: identifier3,
    payload,
    provenance: artifactProvenanceSchema
  }).strict();
  const pipelineArtifactSchema2 = artifactDraftSchema2.extend({
    id: identifier3,
    ownerId: identifier3,
    jobId: identifier3,
    stagePath: identifier3,
    stageVersion: version,
    definitionId: identifier3,
    definitionVersion: version,
    inputDigest: z29.string().regex(/^[a-f0-9]{64}$/),
    contentDigest: z29.string().regex(/^[a-f0-9]{64}$/),
    version,
    createdAt: time3,
    reviewStatus: z29.enum(["pending", "approved", "rejected"]),
    reviewedAt: time3.nullable(),
    reviewNote: z29.string().max(1e3).nullable()
  }).strict().superRefine((value, context2) => {
    if (value.reviewStatus === "pending" !== (value.reviewedAt === null) || value.reviewStatus === "pending" && value.reviewNote !== null || value.reviewedAt !== null && value.reviewedAt < value.createdAt)
      context2.addIssue({
        code: "custom",
        message: "Artifact review evidence does not match its decision."
      });
  });
  const stageResultSchema2 = z29.object({ output: payload, artifacts: z29.array(artifactDraftSchema2).max(32).optional() }).strict();
  const workbenchJobSchema2 = jobFields.extend({
    stages: z29.array(stageRecordSchema2).max(100),
    artifacts: z29.array(pipelineArtifactSchema2).max(3200),
    artifactError: z29.string().max(2e3).nullable()
  }).strict().superRefine((value, context2) => {
    checkJob(value, context2);
    const paths = /* @__PURE__ */ new Set();
    for (const [ordinal, stage] of value.stages.entries()) {
      if (stage.jobId !== value.id || stage.ordinal !== ordinal || paths.has(stage.path))
        context2.addIssue({
          code: "custom",
          message: "Stage identity or order does not match its job."
        });
      paths.add(stage.path);
    }
    const ids = /* @__PURE__ */ new Set();
    for (const artifact of value.artifacts) {
      const stage = value.stages.find((entry) => entry.path === artifact.stagePath);
      if (ids.has(artifact.id) || artifact.ownerId !== value.ownerId || artifact.jobId !== value.id || artifact.definitionId !== value.definitionId || artifact.definitionVersion !== value.definitionVersion || artifact.inputDigest !== value.inputDigest || !stage || stage.version !== artifact.stageVersion)
        context2.addIssue({
          code: "custom",
          message: "Artifact identity does not match its job and stage."
        });
      ids.add(artifact.id);
    }
    if (value.artifactError !== null && value.artifacts.length)
      context2.addIssue({
        code: "custom",
        message: "Corrupt artifact responses cannot include renderable artifacts."
      });
  });
  const jobsReadResponseSchema2 = z29.object({
    jobs: z29.array(workbenchJobSchema2).max(WORKBENCH_PAGE_MAX),
    page: pageInfoSchema.optional(),
    refreshError: z29.string().min(1).max(500).optional()
  }).strict();
  const jobsCommandResponseSchema2 = jobsReadResponseSchema2.extend({ message: z29.string().min(1).max(2e3) }).strict();
  return {
    jobsReadResponseSchema: jobsReadResponseSchema2,
    jobsCommandResponseSchema: jobsCommandResponseSchema2,
    queueJobSchema: queueJobSchema2,
    pipelineJobSchema: pipelineJobSchema2,
    stageRecordSchema: stageRecordSchema2,
    stageRunSchema: stageRunSchema2,
    artifactDraftSchema: artifactDraftSchema2,
    pipelineArtifactSchema: pipelineArtifactSchema2,
    stageResultSchema: stageResultSchema2,
    workbenchJobSchema: workbenchJobSchema2
  };
}
var {
  jobsReadResponseSchema,
  jobsCommandResponseSchema,
  queueJobSchema,
  pipelineJobSchema,
  stageRecordSchema,
  stageRunSchema,
  artifactDraftSchema,
  pipelineArtifactSchema,
  stageResultSchema,
  workbenchJobSchema
} = pipelineSchemas(jsonValueSchema);

// birdsong-yard-sprites/src/lib/server/assets/lifecycle-storage.ts
var ASSET_LIFECYCLE_SCHEMA = [
  [
    "asset_lifecycle_migrations",
    "table",
    "CREATE TABLE asset_lifecycle_migrations(version INTEGER PRIMARY KEY)"
  ],
  [
    "asset_archives",
    "table",
    `CREATE TABLE asset_archives(
    owner_id TEXT NOT NULL, kind TEXT NOT NULL, target_id TEXT NOT NULL,
    revision INTEGER NOT NULL, archived INTEGER NOT NULL, changed_at TEXT NOT NULL,
    PRIMARY KEY(owner_id,kind,target_id))`
  ],
  [
    "asset_lifecycle_receipts",
    "table",
    `CREATE TABLE asset_lifecycle_receipts(
    owner_id TEXT NOT NULL, request_id TEXT NOT NULL, receipt_json TEXT NOT NULL,
    PRIMARY KEY(owner_id,request_id))`
  ],
  [
    "asset_lifecycle_receipts_immutable",
    "trigger",
    `CREATE TRIGGER asset_lifecycle_receipts_immutable
    BEFORE UPDATE ON asset_lifecycle_receipts BEGIN SELECT RAISE(ABORT, 'Lifecycle receipts are immutable'); END`
  ]
];
var normalize2 = (sql) => sql.replace(/\s+/g, " ").replace(/\s*([(),;])\s*/g, "$1").trim().replace(/;$/, "").toLowerCase();
function assertAssetLifecycleCompatibility(db) {
  let found = 0;
  for (const [name, type, sql] of ASSET_LIFECYCLE_SCHEMA) {
    const row = db.prepare("SELECT sql FROM sqlite_master WHERE name=? AND type=?").get(name, type);
    if (!row) continue;
    found++;
    if (typeof row.sql !== "string" || normalize2(row.sql) !== normalize2(sql))
      throw new Error("Unsupported asset lifecycle schema.");
  }
  if (!found) return false;
  if (found !== ASSET_LIFECYCLE_SCHEMA.length)
    throw new Error("Incomplete asset lifecycle schema.");
  const versions = db.prepare("SELECT version FROM asset_lifecycle_migrations LIMIT 2").all();
  if (versions.length !== 1 || versions[0]?.version !== 1)
    throw new Error("Unsupported asset lifecycle version.");
  const triggers = db.prepare(
    "SELECT name FROM sqlite_master WHERE type='trigger' AND tbl_name IN ('asset_archives','asset_lifecycle_receipts','asset_lifecycle_migrations')"
  ).all();
  if (triggers.length !== 1) throw new Error("Unsupported asset lifecycle trigger.");
  return true;
}
function archiveState(db, owner, target) {
  pipelineIdentifierSchema.parse(owner);
  assetLifecycleTargetSchema.parse(target);
  const row = db.prepare("SELECT * FROM asset_archives WHERE owner_id=? AND kind=? AND target_id=?").get(owner, target.kind, target.id);
  if (!row)
    return assetArchiveStateSchema.parse({ target, revision: 0, archived: false, changedAt: null });
  if (row.archived !== 0 && row.archived !== 1) throw new Error("Invalid archive state.");
  return assetArchiveStateSchema.parse({
    target,
    revision: row.revision,
    archived: row.archived === 1,
    changedAt: row.changed_at
  });
}
function readLifecycleReceipt(value) {
  if (typeof value !== "string" || value.length > 4096)
    throw new Error("Invalid lifecycle receipt.");
  const json2 = JSON.parse(value);
  const receipt = assetLifecycleReceiptSchema.parse(json2);
  if (digest(receipt.command) !== receipt.commandDigest || receipt.command.action === "unpin" !== (receipt.previousArtworkId !== null) || receipt.command.action === "unpin" && receipt.previousArtworkId !== receipt.command.expectedArtworkId)
    throw new Error("Invalid lifecycle receipt identity.");
  return receipt;
}
function verifyAssetLifecycleStore(db) {
  if (!assertAssetLifecycleCompatibility(db)) return;
  const states = db.prepare("SELECT * FROM asset_archives LIMIT 16385").all();
  const receipts = db.prepare("SELECT * FROM asset_lifecycle_receipts LIMIT 32769").all();
  if (states.length > 16384 || receipts.length > 32768)
    throw new Error("Asset lifecycle verification budget exceeded.");
  for (const row of states) {
    const owner = pipelineIdentifierSchema.parse(row.owner_id);
    const target = assetLifecycleTargetSchema.parse({ kind: row.kind, id: row.target_id });
    archiveState(db, owner, target);
    const table = target.kind === "private-file" ? "image_files" : "pip_jobs";
    if (!db.prepare(`SELECT 1 FROM ${table} WHERE owner_id=? AND id=?`).get(owner, target.id))
      throw new Error("Orphaned asset archive state.");
  }
  for (const row of receipts) {
    pipelineIdentifierSchema.parse(row.owner_id);
    const receipt = readLifecycleReceipt(row.receipt_json);
    if (receipt.command.requestId !== row.request_id)
      throw new Error("Lifecycle receipt identity mismatch.");
  }
}

// audit-jobs-assets/references.ts
var root = "/workspace/archive-history/audit-jobs-assets";
function trace(db) {
  const original = db.prepare.bind(db);
  let count = 0, rows = 0;
  const queries = /* @__PURE__ */ new Map();
  db.prepare = ((sql) => {
    const s = original(sql);
    return new Proxy(s, { get(t, k) {
      const value = Reflect.get(t, k);
      if (["get", "all", "run"].includes(String(k))) return (...args) => {
        count++;
        queries.set(sql, (queries.get(sql) ?? 0) + 1);
        const v = value.apply(t, args);
        rows += Array.isArray(v) ? v.length : v ? 1 : 0;
        return v;
      };
      return typeof value === "function" ? value.bind(t) : value;
    } });
  });
  return { clear() {
    count = 0;
    rows = 0;
    queries.clear();
  }, get() {
    return { count, rows, queries: [...queries].map(([sql, n]) => ({ sql, n })) };
  } };
}
function measure(name, run, meter) {
  run();
  const times = [];
  let output;
  for (let i = 0; i < 9; i++) {
    meter.clear();
    const start = performance.now();
    const value = run();
    times.push(performance.now() - start);
    output = { ...meter.get(), entries: value?.entries?.length ?? value?.length ?? null };
  }
  times.sort((a, b) => a - b);
  return { name, medianMs: times[4], p95Ms: times[8], ...output };
}
var result = [];
var bytes2 = await sharp2(Buffer.from([20, 40, 60, 255]), { raw: { width: 1, height: 1, channels: 4 } }).png().toBuffer();
for (const n of [1, 16, 64]) {
  const dir = join4(root, `references-${n}`);
  mkdirSync3(dir, { recursive: true, mode: 448 });
  const yard = new YardRepository(join4(dir, "synthetic.sqlite")), db = yard.database;
  const refs = new ReferenceAdmissionService(db, join4(dir, "private-reference-files"));
  let first;
  for (let i = 0; i < n; i++) {
    const owner = i < 16 ? "alice" : `owner-${Math.floor(i / 16)}`;
    const r = await refs.upload(owner, randomUUID4(), bytes2, "image/png");
    first ??= r;
  }
  const meter = trace(db);
  const list = measure("reference-list-alice", () => refs.list("alice"), meter);
  const exportAll = measure("reference-authority-export-all", () => exportReferenceAuthority(db, refs.root), meter);
  const plans = [
    ["list", "SELECT id FROM reference_files WHERE owner_id=? ORDER BY rowid LIMIT 17", ["alice"]],
    ["get", "SELECT record_json FROM reference_files WHERE owner_id=? AND id=?", ["alice", first.identity.id]],
    ["reviews", "SELECT kind,review_json FROM reference_reviews WHERE owner_id=? AND reference_id=?", ["alice", first.identity.id]],
    ["revocations", "SELECT revocation_json FROM reference_revocations WHERE owner_id=? AND reference_id=?", ["alice", first.identity.id]],
    ["export-files", "SELECT * FROM reference_files ORDER BY id LIMIT 65", []],
    ["export-reviews", "SELECT * FROM reference_reviews LIMIT 193", []]
  ].map(([name, sql, args]) => ({ name, sql, plan: db.prepare("EXPLAIN QUERY PLAN " + sql).all(...args) }));
  result.push({ globalReferences: n, ownerReferences: Math.min(16, n), list, exportAll, plans });
  console.log(JSON.stringify(result.at(-1)));
  yard.close();
}
writeFileSync2(join4(root, "references-results.json"), JSON.stringify(result, null, 2));
var recovery = [];
for (const count of [32, 256, 2048, 8192]) {
  const db = new DatabaseSync2(join4(root, `data-${count}`, "synthetic.sqlite"));
  db.exec("PRAGMA journal_mode=WAL;PRAGMA busy_timeout=5000;BEGIN");
  db.prepare("INSERT INTO asset_archives(owner_id,kind,target_id,revision,archived,changed_at) SELECT owner_id,'private-package',id,1,1,'2026-10-12T00:00:00.000Z' FROM pip_jobs").run();
  db.exec("COMMIT");
  const meter = trace(db);
  const m = measure("asset-lifecycle-preflight-archives", () => verifyAssetLifecycleStore(db), meter);
  recovery.push({ archives: count, ...m });
  db.close();
}
writeFileSync2(join4(root, "recovery-results.json"), JSON.stringify(recovery, null, 2));
