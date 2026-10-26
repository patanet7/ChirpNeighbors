// audit-jobs-assets/lockfix.ts
import assert from "node:assert/strict";
import { DatabaseSync as DatabaseSync3 } from "node:sqlite";
import { performance } from "node:perf_hooks";
import { writeFileSync } from "node:fs";
import { randomUUID as randomUUID3 } from "node:crypto";

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
}).strict().superRefine((value, context) => {
  const fail = (message) => context.addIssue({ code: "custom", message });
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
var objectOperationReceiptsSchema = z7.array(objectOperationReceiptSchema).max(MAX_OBJECT_OPERATION_RECEIPTS).superRefine((receipts, context) => {
  if (new Set(receipts.map((receipt) => receipt.requestId)).size !== receipts.length)
    context.addIssue({ code: "custom", message: "Object operation request IDs must be unique." });
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
var artworkSchema = artworkObjectSchema.superRefine((artwork, context) => {
  if (artwork.catalogPin && (artwork.animationPin || artwork.catalogKey))
    context.addIssue({
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
    return `{${Object.keys(value).filter((key2) => value[key2] !== void 0).sort().map(
      (key2) => `${JSON.stringify(key2)}:${canonicalJson(value[key2])}`
    ).join(",")}}`;
  return JSON.stringify(value) ?? "null";
}
function evidenceFingerprint(event) {
  const evidence = Object.fromEntries(
    Object.entries(event).filter(([key2]) => key2 !== "ingestedAt")
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
}).strict().superRefine((snapshot, context) => {
  const { findings, effectiveEvidence, ...raw } = snapshot;
  const parsed = yardDataSchema.safeParse(raw);
  if (!parsed.success) {
    for (const issue of parsed.error.issues) context.addIssue(issue);
    return;
  }
  const expected = snapshotOf(parsed.data, "1970-01-01T00:00:00.000Z");
  if (canonicalJson(findings) !== canonicalJson(expected.findings))
    context.addIssue({
      code: "custom",
      path: ["findings"],
      message: "Findings do not match saved evidence."
    });
  if (canonicalJson(effectiveEvidence) !== canonicalJson(expected.effectiveEvidence))
    context.addIssue({
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
  for (const [key2, species] of Object.entries(legacy2.species))
    if (key2 !== species.id) throw new YardValidationError("legacySpeciesIdentity");
  for (const [key2, art] of Object.entries(legacy2.artworks))
    if (key2 !== art.id || art.referencePhoto.speciesId !== art.speciesId)
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
    const active = state.birds.find(
      (bird) => bird.speciesId === event.species.id && (bird.lifecycle === "permanent" || bird.lifecycle === "temporary" && Date.parse(bird.expiresAt) > current)
    );
    if (active) {
      if (active.lifecycle === "temporary" && Date.parse(active.expiresAt) < expires)
        active.expiresAt = new Date(expires).toISOString();
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

// birdsong-yard-sprites/src/lib/server/pipeline/repository.ts
import { randomUUID as randomUUID2 } from "node:crypto";
import { DatabaseSync as DatabaseSync2 } from "node:sqlite";
import { z as z16 } from "zod";

// birdsong-yard-sprites/src/lib/pipeline/contracts.ts
import { z as z13 } from "zod";

// birdsong-yard-sprites/src/lib/workbench/pagination.ts
import { z as z12 } from "zod";
var WORKBENCH_PAGE_SIZE = 5;
var WORKBENCH_PAGE_MAX = 10;
var WORKBENCH_RESPONSE_BYTES = 8 * 1024 * 1024;
var pageCursorSchema = z12.string().min(1).max(512).regex(/^[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+$/);
var pageRequestSchema = z12.object({
  cursor: pageCursorSchema.optional(),
  limit: z12.number().int().min(1).max(WORKBENCH_PAGE_MAX).default(WORKBENCH_PAGE_SIZE)
}).strict();
var pageInfoSchema = z12.object({
  cursor: pageCursorSchema,
  nextCursor: pageCursorSchema.nullable(),
  limit: z12.number().int().min(1).max(WORKBENCH_PAGE_MAX)
}).strict();

// birdsong-yard-sprites/src/lib/pipeline/contracts.ts
var pipelineIdentifierSchema = z13.string().min(1).max(200).regex(/\S/);
var identifier2 = pipelineIdentifierSchema;
var integer2 = z13.number().int().nonnegative().max(Number.MAX_SAFE_INTEGER);
var pipelineVersionSchema = integer2.positive();
var version = pipelineVersionSchema;
var pipelineTimeSchema = integer2.max(864e13);
var time = pipelineTimeSchema;
var errorCode = z13.string().regex(/^[a-z0-9_-]{1,80}$/).nullable();
var jobStatusSchema = z13.enum([
  "queued",
  "running",
  "retry_wait",
  "blocked_provider",
  "awaiting_review",
  "completed",
  "failed",
  "cancelled"
]);
var stageStatusSchema = z13.enum([
  "pending",
  "running",
  "retry_wait",
  "blocked_provider",
  "succeeded",
  "failed",
  "cancelled"
]);
var artifactProvenanceSchema = z13.object({
  source: z13.enum(["deterministic_fixture", "provider", "user_upload"]),
  providerId: identifier2,
  providerVersion: identifier2,
  references: z13.array(z13.string()),
  fixture: z13.boolean(),
  license: z13.string().optional()
}).strict().superRefine((value, context) => {
  if (value.fixture !== (value.source === "deterministic_fixture"))
    context.addIssue({
      code: "custom",
      message: "Fixture provenance must identify a deterministic fixture."
    });
});
var reviewCommandSchema = z13.object({
  artifactId: identifier2,
  decision: z13.enum(["approved", "rejected"]),
  note: z13.string().max(1e3)
}).strict();
function pipelineSchemas(payload) {
  const queueJobSchema2 = z13.object({
    definitionId: identifier2,
    definitionVersion: version,
    input: payload,
    idempotencyKey: identifier2,
    parentJobId: identifier2.optional()
  }).strict();
  const jobFields = queueJobSchema2.extend({
    id: identifier2,
    ownerId: identifier2,
    rootJobId: identifier2,
    inputDigest: z13.string().regex(/^[a-f0-9]{64}$/),
    status: jobStatusSchema,
    createdAt: time,
    updatedAt: time,
    error: errorCode
  }).strict();
  const checkJob = (value, context) => {
    if (value.updatedAt < value.createdAt)
      context.addIssue({ code: "custom", message: "Job update predates creation." });
    if (value.parentJobId === value.id || !value.parentJobId && value.rootJobId !== value.id)
      context.addIssue({ code: "custom", message: "Invalid job ancestry." });
  };
  const pipelineJobSchema2 = jobFields.superRefine(checkJob);
  const stageRecordSchema2 = z13.object({
    jobId: identifier2,
    path: identifier2,
    version,
    ordinal: integer2.max(99),
    status: stageStatusSchema,
    attempts: integer2.max(10),
    maxAttempts: integer2.min(1).max(10),
    nextRunAt: time.nullable(),
    leaseUntil: time.nullable(),
    output: payload,
    error: errorCode
  }).strict().superRefine((value, context) => {
    if (value.attempts > value.maxAttempts)
      context.addIssue({ code: "custom", message: "Stage attempts exceed the retry policy." });
    if (value.status === "running" !== (value.leaseUntil !== null))
      context.addIssue({ code: "custom", message: "Stage lease does not match its state." });
    if (value.status === "running" && (value.attempts === 0 || value.nextRunAt !== null))
      context.addIssue({ code: "custom", message: "Running stage requires a claimed attempt." });
    if (value.status === "retry_wait" && value.nextRunAt === null)
      context.addIssue({ code: "custom", message: "Retry stage requires its next run time." });
  });
  const stageRunSchema2 = z13.object({
    id: identifier2,
    jobId: identifier2,
    stagePath: identifier2,
    attempt: integer2.min(1).max(10),
    status: z13.enum([
      "running",
      "succeeded",
      "failed",
      "expired",
      "cancelled",
      "blocked_provider"
    ]),
    startedAt: time,
    finishedAt: time.nullable(),
    error: errorCode
  }).strict().superRefine((value, context) => {
    if (value.status === "running" !== (value.finishedAt === null) || value.finishedAt !== null && value.finishedAt < value.startedAt)
      context.addIssue({
        code: "custom",
        message: "Run completion time does not match its state."
      });
  });
  const artifactDraftSchema2 = z13.object({
    family: identifier2,
    kind: identifier2,
    payload,
    provenance: artifactProvenanceSchema
  }).strict();
  const pipelineArtifactSchema2 = artifactDraftSchema2.extend({
    id: identifier2,
    ownerId: identifier2,
    jobId: identifier2,
    stagePath: identifier2,
    stageVersion: version,
    definitionId: identifier2,
    definitionVersion: version,
    inputDigest: z13.string().regex(/^[a-f0-9]{64}$/),
    contentDigest: z13.string().regex(/^[a-f0-9]{64}$/),
    version,
    createdAt: time,
    reviewStatus: z13.enum(["pending", "approved", "rejected"]),
    reviewedAt: time.nullable(),
    reviewNote: z13.string().max(1e3).nullable()
  }).strict().superRefine((value, context) => {
    if (value.reviewStatus === "pending" !== (value.reviewedAt === null) || value.reviewStatus === "pending" && value.reviewNote !== null || value.reviewedAt !== null && value.reviewedAt < value.createdAt)
      context.addIssue({
        code: "custom",
        message: "Artifact review evidence does not match its decision."
      });
  });
  const stageResultSchema2 = z13.object({ output: payload, artifacts: z13.array(artifactDraftSchema2).max(32).optional() }).strict();
  const workbenchJobSchema2 = jobFields.extend({
    stages: z13.array(stageRecordSchema2).max(100),
    artifacts: z13.array(pipelineArtifactSchema2).max(3200),
    artifactError: z13.string().max(2e3).nullable()
  }).strict().superRefine((value, context) => {
    checkJob(value, context);
    const paths = /* @__PURE__ */ new Set();
    for (const [ordinal, stage2] of value.stages.entries()) {
      if (stage2.jobId !== value.id || stage2.ordinal !== ordinal || paths.has(stage2.path))
        context.addIssue({
          code: "custom",
          message: "Stage identity or order does not match its job."
        });
      paths.add(stage2.path);
    }
    const ids = /* @__PURE__ */ new Set();
    for (const artifact of value.artifacts) {
      const stage2 = value.stages.find((entry) => entry.path === artifact.stagePath);
      if (ids.has(artifact.id) || artifact.ownerId !== value.ownerId || artifact.jobId !== value.id || artifact.definitionId !== value.definitionId || artifact.definitionVersion !== value.definitionVersion || artifact.inputDigest !== value.inputDigest || !stage2 || stage2.version !== artifact.stageVersion)
        context.addIssue({
          code: "custom",
          message: "Artifact identity does not match its job and stage."
        });
      ids.add(artifact.id);
    }
    if (value.artifactError !== null && value.artifacts.length)
      context.addIssue({
        code: "custom",
        message: "Corrupt artifact responses cannot include renderable artifacts."
      });
  });
  const jobsReadResponseSchema2 = z13.object({
    jobs: z13.array(workbenchJobSchema2).max(WORKBENCH_PAGE_MAX),
    page: pageInfoSchema.optional(),
    refreshError: z13.string().min(1).max(500).optional()
  }).strict();
  const jobsCommandResponseSchema2 = jobsReadResponseSchema2.extend({ message: z13.string().min(1).max(2e3) }).strict();
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

// birdsong-yard-sprites/src/lib/pipeline/admission.ts
import { z as z14 } from "zod";

// birdsong-yard-sprites/src/lib/contracts/generated/json-value-v1.validator.js
var json_value_v1_validator_default = validate10;
var wrapper0 = { validate: validate11 };
function validate11(data, { instancePath = "", parentData, parentDataProperty, rootData = data } = {}) {
  let vErrors = null;
  let errors = 0;
  const _errs0 = errors;
  let valid0 = false;
  const _errs1 = errors;
  if (typeof data !== "string") {
    const err0 = {
      instancePath,
      schemaPath: "#/anyOf/0/type",
      keyword: "type",
      params: { type: "string" },
      message: "must be string"
    };
    if (vErrors === null) {
      vErrors = [err0];
    } else {
      vErrors.push(err0);
    }
    errors++;
  }
  var _valid0 = _errs1 === errors;
  valid0 = valid0 || _valid0;
  if (!valid0) {
    const _errs3 = errors;
    if (!(typeof data == "number" && isFinite(data))) {
      const err1 = {
        instancePath,
        schemaPath: "#/anyOf/1/type",
        keyword: "type",
        params: { type: "number" },
        message: "must be number"
      };
      if (vErrors === null) {
        vErrors = [err1];
      } else {
        vErrors.push(err1);
      }
      errors++;
    }
    var _valid0 = _errs3 === errors;
    valid0 = valid0 || _valid0;
    if (!valid0) {
      const _errs5 = errors;
      if (typeof data !== "boolean") {
        const err2 = {
          instancePath,
          schemaPath: "#/anyOf/2/type",
          keyword: "type",
          params: { type: "boolean" },
          message: "must be boolean"
        };
        if (vErrors === null) {
          vErrors = [err2];
        } else {
          vErrors.push(err2);
        }
        errors++;
      }
      var _valid0 = _errs5 === errors;
      valid0 = valid0 || _valid0;
      if (!valid0) {
        const _errs7 = errors;
        if (data !== null) {
          const err3 = {
            instancePath,
            schemaPath: "#/anyOf/3/type",
            keyword: "type",
            params: { type: "null" },
            message: "must be null"
          };
          if (vErrors === null) {
            vErrors = [err3];
          } else {
            vErrors.push(err3);
          }
          errors++;
        }
        var _valid0 = _errs7 === errors;
        valid0 = valid0 || _valid0;
        if (!valid0) {
          const _errs9 = errors;
          if (errors === _errs9) {
            if (Array.isArray(data)) {
              var valid1 = true;
              const len0 = data.length;
              for (let i0 = 0; i0 < len0; i0++) {
                const _errs11 = errors;
                if (!wrapper0.validate(data[i0], {
                  instancePath: instancePath + "/" + i0,
                  parentData: data,
                  parentDataProperty: i0,
                  rootData
                })) {
                  vErrors = vErrors === null ? wrapper0.validate.errors : vErrors.concat(wrapper0.validate.errors);
                  errors = vErrors.length;
                }
                var valid1 = _errs11 === errors;
                if (!valid1) {
                  break;
                }
              }
            } else {
              const err4 = {
                instancePath,
                schemaPath: "#/anyOf/4/type",
                keyword: "type",
                params: { type: "array" },
                message: "must be array"
              };
              if (vErrors === null) {
                vErrors = [err4];
              } else {
                vErrors.push(err4);
              }
              errors++;
            }
          }
          var _valid0 = _errs9 === errors;
          valid0 = valid0 || _valid0;
          if (!valid0) {
            const _errs12 = errors;
            if (errors === _errs12) {
              if (data && typeof data == "object" && !Array.isArray(data)) {
                for (const key0 in data) {
                  const _errs15 = errors;
                  if (!wrapper0.validate(data[key0], {
                    instancePath: instancePath + "/" + key0.replace(/~/g, "~0").replace(/\//g, "~1"),
                    parentData: data,
                    parentDataProperty: key0,
                    rootData
                  })) {
                    vErrors = vErrors === null ? wrapper0.validate.errors : vErrors.concat(wrapper0.validate.errors);
                    errors = vErrors.length;
                  }
                  var valid2 = _errs15 === errors;
                  if (!valid2) {
                    break;
                  }
                }
              } else {
                const err5 = {
                  instancePath,
                  schemaPath: "#/anyOf/5/type",
                  keyword: "type",
                  params: { type: "object" },
                  message: "must be object"
                };
                if (vErrors === null) {
                  vErrors = [err5];
                } else {
                  vErrors.push(err5);
                }
                errors++;
              }
            }
            var _valid0 = _errs12 === errors;
            valid0 = valid0 || _valid0;
          }
        }
      }
    }
  }
  if (!valid0) {
    const err6 = {
      instancePath,
      schemaPath: "#/anyOf",
      keyword: "anyOf",
      params: {},
      message: "must match a schema in anyOf"
    };
    if (vErrors === null) {
      vErrors = [err6];
    } else {
      vErrors.push(err6);
    }
    errors++;
    validate11.errors = vErrors;
    return false;
  } else {
    errors = _errs0;
    if (vErrors !== null) {
      if (_errs0) {
        vErrors.length = _errs0;
      } else {
        vErrors = null;
      }
    }
  }
  validate11.errors = vErrors;
  return errors === 0;
}
function validate10(data, { instancePath = "", parentData, parentDataProperty, rootData = data } = {}) {
  let vErrors = null;
  let errors = 0;
  if (!validate11(data, { instancePath, parentData, parentDataProperty, rootData })) {
    vErrors = vErrors === null ? validate11.errors : vErrors.concat(validate11.errors);
    errors = vErrors.length;
  }
  validate10.errors = vErrors;
  return errors === 0;
}

// birdsong-yard-sprites/src/lib/contracts/json-value.ts
function isJsonValue(value) {
  const active = /* @__PURE__ */ new WeakSet();
  const pending = [{ kind: "enter", value }];
  try {
    while (pending.length) {
      const current = pending.pop();
      if (!current) break;
      if (current.kind === "leave") {
        active.delete(current.value);
        continue;
      }
      const item = current.value;
      if (item === null || typeof item !== "object") continue;
      if (item instanceof Date || item instanceof Map || item instanceof Set) return false;
      const then = Reflect.get(item, "then");
      const catchValue = Reflect.get(item, "catch");
      if (typeof then === "function" && typeof catchValue === "function") return false;
      if (active.has(item)) return false;
      active.add(item);
      pending.push({ kind: "leave", value: item });
      for (const key2 in item) {
        const child = Reflect.get(item, key2);
        if (child !== null && typeof child === "object") {
          pending.push({ kind: "enter", value: child });
        }
      }
    }
    return json_value_v1_validator_default(value);
  } catch {
    return false;
  }
}

// birdsong-yard-sprites/src/lib/pipeline/admission.ts
var checkedJsonSchema = z14.unknown().transform((value, context) => {
  if (isJsonValue(value)) return value;
  context.addIssue({ code: "custom", message: "Expected finite JSON data." });
  return z14.NEVER;
});
var admittedPipeline = pipelineSchemas(checkedJsonSchema);

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
      encoded = "{" + entries.sort(([left], [right]) => left < right ? -1 : left > right ? 1 : 0).map(([key2, item]) => JSON.stringify(key2) + ":" + visit(item, depth + 1)).join(",") + "}";
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
var PipelineConflict = class extends Error {
  code = "pipeline_conflict";
};
var PipelineNotFound = class extends Error {
  code = "pipeline_not_found";
  constructor() {
    super("Pipeline resource not found");
  }
};
var PermanentStageError = class extends Error {
};

// birdsong-yard-sprites/src/lib/server/pipeline/configuration.ts
import { z as z15 } from "zod";
var stage = z15.object({
  path: z15.string().regex(/^[a-z0-9][a-z0-9/_-]{0,119}$/),
  version: pipelineVersionSchema,
  maxAttempts: z15.number().int().min(1).max(10).optional(),
  backoffMs: z15.number().int().min(0).max(36e5).optional(),
  providerId: pipelineIdentifierSchema.optional(),
  providerVersion: pipelineIdentifierSchema.optional(),
  execute: z15.custom((value) => typeof value === "function").optional()
}).strict().superRefine((value, context) => {
  if (value.execute !== void 0 === (value.providerId !== void 0) || value.providerId !== void 0 !== (value.providerVersion !== void 0))
    context.addIssue({
      code: "custom",
      message: "Stage requires exactly one local callback or pinned provider."
    });
});
var definitionConfigurationSchema = z15.object({
  id: pipelineIdentifierSchema,
  version: pipelineVersionSchema,
  stages: z15.array(stage).min(1).max(100)
}).strict().superRefine((value, context) => {
  if (new Set(value.stages.map((entry) => entry.path)).size !== value.stages.length)
    context.addIssue({ code: "custom", message: "Stage paths must be unique." });
});
var providerConfigurationSchema = z15.object({
  id: pipelineIdentifierSchema,
  version: pipelineIdentifierSchema,
  execute: z15.custom((value) => typeof value === "function")
}).strict();
var leaseDurationSchema = z15.number().int().min(100).max(36e5);

// birdsong-yard-sprites/src/lib/server/pipeline/repository.ts
function databaseText(value) {
  if (typeof value !== "string") throw new Error("Invalid pipeline text column");
  return value;
}
function readJson(column) {
  const text5 = databaseText(column);
  if (Buffer.byteLength(text5) > 1e6) throw new Error("Pipeline JSON exceeds 1 MB");
  const value = JSON.parse(text5);
  function visit(current, depth) {
    if (depth > 64) throw new Error("Pipeline JSON is too deeply nested");
    if (current === null || typeof current === "string" || typeof current === "boolean")
      return current;
    if (typeof current === "number" && Number.isFinite(current)) return current;
    if (Array.isArray(current)) return current.map((entry) => visit(entry, depth + 1));
    if (typeof current === "object" && current !== null) {
      const result2 = {};
      Object.setPrototypeOf(result2, null);
      const entries = Object.entries(current);
      for (const [key2, entry] of entries) result2[key2] = visit(entry, depth + 1);
      return result2;
    }
    throw new Error("Invalid finite pipeline JSON");
  }
  return visit(value, 0);
}
function identifier3(value, label2) {
  if (!pipelineIdentifierSchema.safeParse(value).success) {
    throw new Error(`Invalid ${label2}`);
  }
}
var JobRepository = class {
  db;
  ownsConnection;
  now;
  validateFileInput;
  admitQueue;
  validateCompletion;
  validateReview;
  constructor(database, options = {}) {
    this.ownsConnection = typeof database === "string";
    this.db = typeof database === "string" ? new DatabaseSync2(database) : database;
    const clock = options.now ?? Date.now;
    this.now = () => pipelineTimeSchema.parse(clock());
    this.validateFileInput = options.validateFileInput;
    this.admitQueue = options.admitQueue;
    this.validateCompletion = options.validateCompletion;
    this.validateReview = options.validateReview;
    if (this.ownsConnection) this.db.exec("PRAGMA journal_mode = WAL; PRAGMA busy_timeout = 5000;");
    this.db.exec(`
      CREATE TABLE IF NOT EXISTS pip_migrations(version INTEGER PRIMARY KEY, applied_at INTEGER NOT NULL);
      CREATE TABLE IF NOT EXISTS pip_jobs(
        id TEXT PRIMARY KEY, owner_id TEXT NOT NULL, definition_id TEXT NOT NULL,
        definition_version INTEGER NOT NULL, input_json TEXT NOT NULL, input_digest TEXT NOT NULL,
        idempotency_key TEXT NOT NULL, parent_job_id TEXT, root_job_id TEXT NOT NULL,
        status TEXT NOT NULL, definition_digest TEXT, created_at INTEGER NOT NULL,
        updated_at INTEGER NOT NULL, error TEXT, UNIQUE(owner_id, idempotency_key)
      );
      CREATE INDEX IF NOT EXISTS pip_jobs_owner ON pip_jobs(owner_id, created_at);
      CREATE INDEX IF NOT EXISTS pip_jobs_owner_insertion ON pip_jobs(owner_id);
      CREATE TABLE IF NOT EXISTS pip_stages(
        job_id TEXT NOT NULL, path TEXT NOT NULL, version INTEGER NOT NULL, ordinal INTEGER NOT NULL,
        status TEXT NOT NULL, attempts INTEGER NOT NULL DEFAULT 0, max_attempts INTEGER NOT NULL,
        backoff_ms INTEGER NOT NULL, next_run_at INTEGER, lease_token TEXT, lease_until INTEGER,
        output_json TEXT, error TEXT, PRIMARY KEY(job_id, path)
      );
      CREATE TABLE IF NOT EXISTS pip_runs(
        id TEXT PRIMARY KEY, job_id TEXT NOT NULL, stage_path TEXT NOT NULL, attempt INTEGER NOT NULL,
        status TEXT NOT NULL, started_at INTEGER NOT NULL, finished_at INTEGER, error TEXT
      );
      CREATE TABLE IF NOT EXISTS pip_artifacts(
        id TEXT PRIMARY KEY, owner_id TEXT NOT NULL, job_id TEXT NOT NULL, stage_path TEXT NOT NULL,
        stage_version INTEGER NOT NULL, definition_id TEXT NOT NULL, definition_version INTEGER NOT NULL,
        input_digest TEXT NOT NULL, family TEXT NOT NULL, kind TEXT NOT NULL, version INTEGER NOT NULL,
        payload_json TEXT NOT NULL, content_digest TEXT NOT NULL, provenance_json TEXT NOT NULL,
        created_at INTEGER NOT NULL, UNIQUE(owner_id, family, version)
      );
      CREATE TABLE IF NOT EXISTS pip_reviews(
        artifact_id TEXT PRIMARY KEY, owner_id TEXT NOT NULL, decision TEXT NOT NULL,
        reviewed_at INTEGER NOT NULL, note TEXT
      );
      CREATE TRIGGER IF NOT EXISTS pip_artifacts_immutable BEFORE UPDATE ON pip_artifacts
        BEGIN SELECT RAISE(ABORT, 'Artifacts are immutable; publish another version'); END;
      CREATE TRIGGER IF NOT EXISTS pip_reviews_immutable BEFORE UPDATE ON pip_reviews
        BEGIN SELECT RAISE(ABORT, 'Reviews are immutable; publish another artifact version'); END;
    `);
    this.db.prepare("INSERT OR IGNORE INTO pip_migrations(version, applied_at) VALUES (1, ?)").run(this.now());
  }
  close() {
    if (this.ownsConnection) this.db.close();
  }
  /** File-backed sources require a configured owner-scoped integrity authority. */
  validateSourceFile(owner, input) {
    if (!this.validateFileInput) throw new Error("Private image file validation is unavailable.");
    this.validateFileInput(owner, input);
  }
  transaction(run) {
    this.db.exec("BEGIN IMMEDIATE");
    try {
      const result2 = run();
      this.db.exec("COMMIT");
      return result2;
    } catch (error) {
      this.db.exec("ROLLBACK");
      throw error;
    }
  }
  row(ownerId, id8) {
    identifier3(ownerId, "owner");
    identifier3(id8, "job ID");
    const row = this.db.prepare("SELECT * FROM pip_jobs WHERE id = ? AND owner_id = ?").get(id8, ownerId);
    if (!row) throw new PipelineNotFound();
    return row;
  }
  job(row) {
    const job = admittedPipeline.pipelineJobSchema.parse({
      id: row.id,
      ownerId: row.owner_id,
      definitionId: row.definition_id,
      definitionVersion: row.definition_version,
      input: readJson(row.input_json),
      inputDigest: row.input_digest,
      idempotencyKey: row.idempotency_key,
      ...row.parent_job_id === null ? {} : { parentJobId: row.parent_job_id },
      rootJobId: row.root_job_id,
      status: row.status,
      createdAt: row.created_at,
      updatedAt: row.updated_at,
      error: row.error
    });
    if (digest(job.input) !== job.inputDigest) throw new Error("Pipeline input digest mismatch");
    return job;
  }
  get(ownerId, id8) {
    return this.job(this.row(ownerId, id8));
  }
  list(ownerId) {
    identifier3(ownerId, "owner");
    return this.db.prepare("SELECT * FROM pip_jobs WHERE owner_id = ? ORDER BY created_at DESC, id").all(ownerId).map((row) => this.job(row));
  }
  queue(ownerId, request) {
    identifier3(ownerId, "owner");
    request = admittedPipeline.queueJobSchema.parse(request);
    const input = canonicalJson2(request.input);
    const inputDigest = digest(request.input);
    return this.transaction(() => {
      const existing = this.db.prepare("SELECT * FROM pip_jobs WHERE owner_id = ? AND idempotency_key = ?").get(ownerId, request.idempotencyKey);
      if (existing) {
        if (existing.input_digest !== inputDigest || existing.definition_id !== request.definitionId || existing.definition_version !== request.definitionVersion || (existing.parent_job_id ?? void 0) !== request.parentJobId) {
          throw new PipelineConflict("Idempotency key already belongs to a different request");
        }
        return this.job(existing);
      }
      this.admitQueue?.(ownerId, request);
      const parent = request.parentJobId ? this.get(ownerId, request.parentJobId) : void 0;
      if (parent && ["cancelled", "failed", "completed"].includes(parent.status)) {
        throw new PipelineConflict("Cannot attach a child to a terminal job");
      }
      const id8 = randomUUID2();
      const now = this.now();
      this.db.prepare(
        `INSERT INTO pip_jobs(id, owner_id, definition_id, definition_version,
        input_json, input_digest, idempotency_key, parent_job_id, root_job_id, status, created_at, updated_at)
        VALUES(?,?,?,?,?,?,?,?,?,'queued',?,?)`
      ).run(
        id8,
        ownerId,
        request.definitionId,
        request.definitionVersion,
        input,
        inputDigest,
        request.idempotencyKey,
        request.parentJobId ?? null,
        parent?.rootJobId ?? id8,
        now,
        now
      );
      return this.get(ownerId, id8);
    });
  }
  stage(row) {
    return admittedPipeline.stageRecordSchema.parse({
      jobId: row.job_id,
      path: row.path,
      version: row.version,
      ordinal: row.ordinal,
      status: row.status,
      attempts: row.attempts,
      maxAttempts: row.max_attempts,
      nextRunAt: row.next_run_at,
      leaseUntil: row.lease_until,
      output: row.output_json === null ? null : readJson(row.output_json),
      error: row.error
    });
  }
  stages(ownerId, id8, includeOutputs = true) {
    this.row(ownerId, id8);
    return this.db.prepare(
      `SELECT ${includeOutputs ? "*" : "job_id,path,version,ordinal,status,attempts,max_attempts,next_run_at,lease_until,error,NULL AS output_json"} FROM pip_stages WHERE job_id = ? ORDER BY ordinal LIMIT 101`
    ).all(id8).map((row) => this.stage(row));
  }
  runs(ownerId, id8) {
    this.row(ownerId, id8);
    return this.db.prepare("SELECT * FROM pip_runs WHERE job_id = ? ORDER BY started_at, attempt").all(id8).map(
      (row) => admittedPipeline.stageRunSchema.parse({
        id: row.id,
        jobId: row.job_id,
        stagePath: row.stage_path,
        attempt: row.attempt,
        status: row.status,
        startedAt: row.started_at,
        finishedAt: row.finished_at,
        error: row.error
      })
    );
  }
  artifact(row) {
    const artifact = admittedPipeline.pipelineArtifactSchema.parse({
      id: row.id,
      ownerId: row.owner_id,
      jobId: row.job_id,
      stagePath: row.stage_path,
      stageVersion: row.stage_version,
      definitionId: row.definition_id,
      definitionVersion: row.definition_version,
      inputDigest: row.input_digest,
      family: row.family,
      kind: row.kind,
      version: row.version,
      payload: readJson(row.payload_json),
      contentDigest: row.content_digest,
      provenance: artifactProvenanceSchema.parse(readJson(row.provenance_json)),
      createdAt: row.created_at,
      reviewStatus: row.decision ?? "pending",
      reviewedAt: row.reviewed_at,
      reviewNote: row.note
    });
    if (digest(artifact.payload) !== artifact.contentDigest)
      throw new Error("Pipeline artifact digest mismatch");
    return artifact;
  }
  artifacts(ownerId, jobId) {
    this.row(ownerId, jobId);
    return this.db.prepare(
      `SELECT a.*, r.decision, r.reviewed_at, r.note FROM pip_artifacts a
      LEFT JOIN pip_reviews r ON r.artifact_id = a.id AND r.owner_id = a.owner_id WHERE a.owner_id = ? AND a.job_id = ?
      ORDER BY a.created_at, a.version`
    ).all(ownerId, jobId).map((row) => this.artifact(row));
  }
  /** Binds the immutable versioned stage manifest; stages form an ordered hierarchy. */
  prepare(ownerId, id8, definition) {
    definitionConfigurationSchema.parse(definition);
    const manifest = definition.stages.map((stage2) => ({
      path: stage2.path,
      version: stage2.version,
      maxAttempts: stage2.maxAttempts ?? 3,
      backoffMs: stage2.backoffMs ?? 1e3,
      providerId: stage2.providerId ?? null,
      providerVersion: stage2.providerVersion ?? null
    }));
    const fingerprint = digest(manifest);
    this.transaction(() => {
      const persistedJob = this.row(ownerId, id8);
      const job = this.job(persistedJob);
      const definitionDigest = z16.string().regex(/^[a-f0-9]{64}$/).nullable().parse(persistedJob.definition_digest);
      if (job.definitionId !== definition.id || job.definitionVersion !== definition.version) {
        throw new PipelineConflict("Job definition does not match runner");
      }
      if (definitionDigest && definitionDigest !== fingerprint) {
        throw new PipelineConflict("A persisted definition version cannot change");
      }
      if (definitionDigest || ["cancelled", "completed", "failed"].includes(job.status)) return;
      this.db.prepare("UPDATE pip_jobs SET definition_digest = ? WHERE id = ?").run(fingerprint, id8);
      for (const [ordinal, stage2] of manifest.entries()) {
        this.db.prepare(
          `INSERT INTO pip_stages(job_id,path,version,ordinal,status,max_attempts,backoff_ms)
          VALUES(?,?,?,?,'pending',?,?)`
        ).run(id8, stage2.path, stage2.version, ordinal, stage2.maxAttempts, stage2.backoffMs);
      }
    });
  }
  claim(ownerId, id8, definition, leaseMs) {
    leaseDurationSchema.parse(leaseMs);
    this.prepare(ownerId, id8, definition);
    return this.transaction(() => {
      const job = this.get(ownerId, id8);
      if (!["queued", "running", "retry_wait"].includes(job.status)) return null;
      const now = this.now();
      const stage2 = this.db.prepare(
        `SELECT * FROM pip_stages WHERE job_id = ?
        AND status != 'succeeded' ORDER BY ordinal LIMIT 1`
      ).get(id8);
      if (!stage2) return null;
      const checkedStage = this.stage(stage2);
      const leaseToken = pipelineIdentifierSchema.nullable().parse(stage2.lease_token);
      if (checkedStage.status === "running" && leaseToken === null)
        throw new Error("Running stage requires a lease token");
      if (stage2.status === "running") {
        if ((checkedStage.leaseUntil ?? 0) > now) return null;
        const exhausted = checkedStage.attempts >= checkedStage.maxAttempts;
        this.db.prepare(
          `UPDATE pip_runs SET status = 'expired', finished_at = ?, error = 'lease_expired'
          WHERE id = ? AND status = 'running'`
        ).run(now, leaseToken);
        this.db.prepare(
          `UPDATE pip_stages SET status = ?, lease_token = NULL, lease_until = NULL,
          next_run_at = ?, error = 'lease_expired' WHERE job_id = ? AND path = ?`
        ).run(
          exhausted ? "failed" : "retry_wait",
          pipelineTimeSchema.parse(now + this.backoff(stage2)),
          id8,
          checkedStage.path
        );
        this.db.prepare("UPDATE pip_jobs SET status = ?, updated_at = ?, error = ? WHERE id = ?").run(exhausted ? "failed" : "retry_wait", now, "lease_expired", id8);
        return null;
      }
      if (!["pending", "retry_wait"].includes(checkedStage.status) || (checkedStage.nextRunAt ?? 0) > now) {
        return null;
      }
      const executableStage = definition.stages[checkedStage.ordinal];
      if (!executableStage || executableStage.path !== checkedStage.path || executableStage.version !== checkedStage.version || (executableStage.maxAttempts ?? 3) !== checkedStage.maxAttempts || (executableStage.backoffMs ?? 1e3) !== stage2.backoff_ms)
        throw new Error("Persisted stage is absent from its pinned definition");
      const token = randomUUID2();
      const attempt = checkedStage.attempts + 1;
      this.db.prepare(
        `UPDATE pip_stages SET status = 'running', attempts = ?, lease_token = ?,
        lease_until = ?, next_run_at = NULL, error = NULL WHERE job_id = ? AND path = ?`
      ).run(attempt, token, pipelineTimeSchema.parse(now + leaseMs), id8, checkedStage.path);
      this.db.prepare(
        `INSERT INTO pip_runs(id,job_id,stage_path,attempt,status,started_at)
        VALUES(?,?,?,?,'running',?)`
      ).run(token, id8, checkedStage.path, attempt, now);
      this.db.prepare(
        "UPDATE pip_jobs SET status = 'running', updated_at = ?, error = NULL WHERE id = ?"
      ).run(now, id8);
      const previous = {};
      for (const item of this.stages(ownerId, id8))
        if (item.status === "succeeded") previous[item.path] = item.output;
      return {
        token,
        job: this.get(ownerId, id8),
        stage: executableStage,
        previous
      };
    });
  }
  backoff(stage2) {
    return Math.min(
      36e5,
      z16.number().int().min(0).max(36e5).parse(stage2.backoff_ms) * 2 ** Math.max(0, this.stage(stage2).attempts - 1)
    );
  }
  live(ownerId, claim) {
    this.get(ownerId, claim.job.id);
    const row = this.db.prepare(
      `SELECT s.* FROM pip_stages s JOIN pip_jobs j ON j.id = s.job_id
      WHERE s.job_id = ? AND s.path = ? AND j.owner_id = ? AND j.status = 'running'
      AND s.status = 'running' AND s.lease_token = ? AND s.lease_until > ?`
    ).get(claim.job.id, claim.stage.path, ownerId, claim.token, this.now());
    if (!row) return null;
    this.stage(row);
    return row;
  }
  /** Fences output from cancelled, timed-out or replaced workers. Artifacts commit atomically. */
  complete(ownerId, claim, result2) {
    result2 = admittedPipeline.stageResultSchema.parse(result2);
    const output = canonicalJson2(result2.output);
    const drafts = result2.artifacts ?? [];
    for (const artifact of drafts) {
      canonicalJson2(artifact.payload);
      canonicalJson2(artifact.provenance);
    }
    return this.transaction(() => {
      if (!this.live(ownerId, claim)) return false;
      this.validateCompletion?.(ownerId, this.get(ownerId, claim.job.id));
      const now = this.now();
      for (const artifact of drafts) {
        const next = z16.object({ version: pipelineVersionSchema }).parse(
          this.db.prepare(
            "SELECT COALESCE(MAX(version),0)+1 AS version FROM pip_artifacts WHERE owner_id = ? AND family = ?"
          ).get(ownerId, artifact.family)
        );
        this.db.prepare(
          `INSERT INTO pip_artifacts(id,owner_id,job_id,stage_path,stage_version,
          definition_id,definition_version,input_digest,family,kind,version,payload_json,
          content_digest,provenance_json,created_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)`
        ).run(
          randomUUID2(),
          ownerId,
          claim.job.id,
          claim.stage.path,
          claim.stage.version,
          claim.job.definitionId,
          claim.job.definitionVersion,
          claim.job.inputDigest,
          artifact.family,
          artifact.kind,
          next.version,
          canonicalJson2(artifact.payload),
          digest(artifact.payload),
          canonicalJson2(artifact.provenance),
          now
        );
      }
      this.db.prepare(
        `UPDATE pip_stages SET status = 'succeeded', output_json = ?, lease_token = NULL,
        lease_until = NULL, error = NULL WHERE job_id = ? AND path = ?`
      ).run(output, claim.job.id, claim.stage.path);
      this.db.prepare("UPDATE pip_runs SET status = 'succeeded', finished_at = ? WHERE id = ?").run(now, claim.token);
      const pending = this.stages(ownerId, claim.job.id).some(
        (stage2) => stage2.status !== "succeeded"
      );
      this.db.prepare("UPDATE pip_jobs SET status = ?, updated_at = ?, error = NULL WHERE id = ?").run(
        drafts.length ? "awaiting_review" : pending ? "queued" : "completed",
        now,
        claim.job.id
      );
      return true;
    });
  }
  fail(ownerId, claim, code, options = {}) {
    return this.transaction(() => {
      const stage2 = this.live(ownerId, claim);
      if (!stage2) return false;
      const now = this.now();
      const checkedStage = this.stage(stage2);
      const status = options.blocked ? "blocked_provider" : options.permanent || checkedStage.attempts >= checkedStage.maxAttempts ? "failed" : "retry_wait";
      const safeCode = /^[a-z0-9_-]{1,80}$/.test(code) ? code : "stage_execution_failed";
      this.db.prepare(
        `UPDATE pip_stages SET status = ?, error = ?, next_run_at = ?,
        lease_token = NULL, lease_until = NULL WHERE job_id = ? AND path = ?`
      ).run(
        status,
        safeCode,
        status === "retry_wait" ? pipelineTimeSchema.parse(now + this.backoff(stage2)) : null,
        claim.job.id,
        claim.stage.path
      );
      this.db.prepare("UPDATE pip_runs SET status = ?, error = ?, finished_at = ? WHERE id = ?").run(options.blocked ? "blocked_provider" : "failed", safeCode, now, claim.token);
      this.db.prepare("UPDATE pip_jobs SET status = ?, error = ?, updated_at = ? WHERE id = ?").run(status, safeCode, now, claim.job.id);
      return true;
    });
  }
  cancel(ownerId, id8) {
    return this.transaction(() => {
      this.get(ownerId, id8);
      const descendants = this.db.prepare(
        `WITH RECURSIVE tree(id) AS (
        SELECT id FROM pip_jobs WHERE id = ? AND owner_id = ? UNION ALL
        SELECT j.id FROM pip_jobs j JOIN tree t ON j.parent_job_id = t.id WHERE j.owner_id = ?)
        SELECT id FROM tree`
      ).all(id8, ownerId, ownerId);
      const now = this.now();
      for (const item of descendants) {
        const child = this.get(ownerId, pipelineIdentifierSchema.parse(item.id));
        if (["cancelled", "completed", "failed"].includes(child.status)) continue;
        this.db.prepare(
          "UPDATE pip_jobs SET status = 'cancelled', updated_at = ?, error = NULL WHERE id = ?"
        ).run(now, child.id);
        this.db.prepare(
          `UPDATE pip_stages SET status = 'cancelled', lease_token = NULL,
          lease_until = NULL, next_run_at = NULL WHERE job_id = ? AND status != 'succeeded'`
        ).run(child.id);
        this.db.prepare(
          "UPDATE pip_runs SET status = 'cancelled', finished_at = ? WHERE job_id = ? AND status = 'running'"
        ).run(now, child.id);
      }
      return this.get(ownerId, id8);
    });
  }
  /** Operator/user action after configuring the pinned provider; never auto-retries blocked work. */
  resumeBlocked(ownerId, id8) {
    return this.transaction(() => {
      const job = this.get(ownerId, id8);
      if (job.status !== "blocked_provider")
        throw new PipelineConflict("Job is not blocked on a provider");
      this.db.prepare(
        `UPDATE pip_stages SET status = 'pending', attempts = MAX(0, attempts - 1),
        error = NULL WHERE job_id = ? AND status = 'blocked_provider'`
      ).run(id8);
      this.db.prepare("UPDATE pip_jobs SET status = 'queued', error = NULL, updated_at = ? WHERE id = ?").run(this.now(), id8);
      return this.get(ownerId, id8);
    });
  }
  /** Removes this owner's live pipeline data. Backup/object-store policies belong to the host. */
  deleteOwner(ownerId) {
    identifier3(ownerId, "owner");
    this.transaction(() => {
      this.db.prepare("DELETE FROM pip_reviews WHERE owner_id = ?").run(ownerId);
      this.db.prepare("DELETE FROM pip_artifacts WHERE owner_id = ?").run(ownerId);
      this.db.prepare(
        "DELETE FROM pip_runs WHERE job_id IN (SELECT id FROM pip_jobs WHERE owner_id = ?)"
      ).run(ownerId);
      this.db.prepare(
        "DELETE FROM pip_stages WHERE job_id IN (SELECT id FROM pip_jobs WHERE owner_id = ?)"
      ).run(ownerId);
      this.db.prepare("DELETE FROM pip_jobs WHERE owner_id = ?").run(ownerId);
    });
  }
  review(ownerId, artifactId, decision, note = "") {
    identifier3(ownerId, "owner");
    reviewCommandSchema.parse({ artifactId, decision, note });
    return this.transaction(() => {
      const row = this.db.prepare("SELECT * FROM pip_artifacts WHERE id = ? AND owner_id = ?").get(artifactId, ownerId);
      if (!row) throw new PipelineNotFound();
      const job = this.get(ownerId, pipelineIdentifierSchema.parse(row.job_id));
      const previous = this.artifacts(ownerId, job.id).find((item) => item.id === artifactId);
      if (!previous) throw new PipelineNotFound();
      if (decision === "approved") this.validateReview?.(ownerId, job, previous);
      if (previous.reviewStatus !== "pending") {
        if (previous.reviewStatus !== decision || previous.reviewNote !== note) {
          throw new PipelineConflict("Reviews are immutable; publish a new artifact version");
        }
        return previous;
      }
      if (job.status !== "awaiting_review")
        throw new PipelineConflict("Job is not awaiting review");
      const now = this.now();
      this.db.prepare(
        "INSERT INTO pip_reviews(artifact_id,owner_id,decision,reviewed_at,note) VALUES(?,?,?,?,?)"
      ).run(artifactId, ownerId, decision, now, note);
      const artifacts = this.artifacts(ownerId, job.id);
      if (decision === "rejected") {
        this.db.prepare(
          "UPDATE pip_jobs SET status = 'failed', error = 'review_rejected', updated_at = ? WHERE id = ?"
        ).run(now, job.id);
      } else if (artifacts.every((item) => item.reviewStatus === "approved")) {
        const done = this.stages(ownerId, job.id).every((stage2) => stage2.status === "succeeded");
        this.db.prepare("UPDATE pip_jobs SET status = ?, updated_at = ? WHERE id = ?").run(done ? "completed" : "queued", now, job.id);
      }
      const reviewed = artifacts.find((item) => item.id === artifactId);
      if (!reviewed) throw new PipelineNotFound();
      return reviewed;
    });
  }
};

// birdsong-yard-sprites/src/lib/server/assets/lifecycle.ts
import { z as z38 } from "zod";

// birdsong-yard-sprites/src/lib/assets/lifecycle-contracts.ts
import { z as z17 } from "zod";
var uuid = z17.string().uuid();
var revision = z17.number().int().min(0).max(1e6);
var time2 = z17.string().datetime().max(40);
var assetLifecycleTargetSchema = z17.object({
  kind: z17.enum(["private-file", "private-package"]),
  id: uuid
}).strict();
var assetArchiveStateSchema = z17.object({
  target: assetLifecycleTargetSchema,
  revision,
  archived: z17.boolean(),
  changedAt: time2.nullable()
}).strict().superRefine((value, context) => {
  if (value.revision === 0 !== (value.changedAt === null) || value.revision === 0 && value.archived)
    context.addIssue({
      code: "custom",
      message: "Initial archive state must be active without a change timestamp."
    });
});
var assetLifecycleCommandSchema = z17.discriminatedUnion("action", [
  z17.object({
    action: z17.literal("set-archive"),
    requestId: uuid,
    target: assetLifecycleTargetSchema,
    expectedRevision: revision,
    archived: z17.boolean()
  }).strict(),
  z17.object({
    action: z17.literal("unpin"),
    requestId: uuid,
    birdId: idSchema,
    expectedArtworkId: idSchema
  }).strict(),
  z17.object({ action: z17.literal("restore-pin"), requestId: uuid, unpinRequestId: uuid }).strict()
]);
var assetLifecycleReceiptSchema = z17.object({
  schemaVersion: z17.literal(1),
  command: assetLifecycleCommandSchema,
  commandDigest: z17.string().regex(/^[a-f0-9]{64}$/),
  previousArtworkId: idSchema.nullable(),
  savedAt: time2
}).strict().superRefine((value, context) => {
  if (value.command.action === "unpin" !== (value.previousArtworkId !== null) || value.command.action === "unpin" && value.previousArtworkId !== value.command.expectedArtworkId)
    context.addIssue({
      code: "custom",
      message: "Only unpin receipts retain the exact previous artwork."
    });
});
var assetRetentionReasonSchema = z17.enum([
  "active",
  "pinned-bird",
  "retained-artwork",
  "referenced-by-package",
  "file-review-evidence",
  "pipeline-history",
  "incomplete-reference-scan"
]);
var assetLifecycleEntrySchema = z17.object({
  state: assetArchiveStateSchema,
  label: z17.string().min(1).max(200),
  retainedBytes: z17.number().int().min(0).max(Number.MAX_SAFE_INTEGER),
  selectable: z17.boolean(),
  selectionBlock: z17.enum(["none", "archived", "archived-dependency", "unavailable"]),
  cleanupEligible: z17.boolean(),
  retainedBecause: z17.array(assetRetentionReasonSchema).max(7)
}).strict().superRefine((value, context) => {
  if (value.selectable !== (value.selectionBlock === "none") || value.state.archived !== (value.selectionBlock === "archived") || value.cleanupEligible && (value.state.target.kind !== "private-file" || !value.state.archived || value.retainedBecause.length !== 0) || new Set(value.retainedBecause).size !== value.retainedBecause.length)
    context.addIssue({
      code: "custom",
      message: "Lifecycle selection and retention state are inconsistent."
    });
});
var assetLifecycleOverviewSchema = z17.object({
  schemaVersion: z17.literal(1),
  purgeEnabled: z17.literal(false),
  sharedCatalog: z17.literal("read-only-not-owned"),
  referenceScan: z17.enum(["complete", "incomplete"]),
  entries: z17.array(assetLifecycleEntrySchema).max(576),
  pins: z17.array(
    z17.object({ birdId: idSchema, artworkId: idSchema, label: z17.string().min(1).max(200) }).strict()
  ).max(2048),
  undoPins: z17.array(
    z17.object({
      requestId: uuid,
      birdId: idSchema,
      artworkId: idSchema,
      label: z17.string().min(1).max(200)
    }).strict()
  ).max(32)
}).strict().superRefine((value, context) => {
  if (new Set(value.entries.map((entry) => `${entry.state.target.kind}/${entry.state.target.id}`)).size !== value.entries.length || new Set(value.pins.map((pin) => pin.birdId)).size !== value.pins.length || new Set(value.undoPins.map((pin) => pin.requestId)).size !== value.undoPins.length || value.referenceScan === "incomplete" && value.entries.some((entry) => entry.cleanupEligible))
    context.addIssue({
      code: "custom",
      message: "Lifecycle overview identities or eligibility are inconsistent."
    });
});
var assetLifecycleResponseSchema = z17.object({
  overview: assetLifecycleOverviewSchema,
  receipt: z17.object({ requestId: uuid, replayed: z17.boolean() }).strict()
}).strict();
var assetPackageHistorySchema = z17.object({
  schemaVersion: z17.literal(1),
  purgeEnabled: z17.literal(false),
  referenceScan: z17.literal("not-run"),
  entries: z17.array(assetLifecycleEntrySchema).max(WORKBENCH_PAGE_MAX),
  page: pageInfoSchema
}).strict().superRefine((value, context) => {
  if (value.entries.length > value.page.limit || new Set(value.entries.map((entry) => entry.state.target.id)).size !== value.entries.length || value.entries.some(
    (entry) => entry.state.target.kind !== "private-package" || entry.cleanupEligible || !entry.retainedBecause.includes("pipeline-history") || !entry.retainedBecause.includes("incomplete-reference-scan")
  ))
    context.addIssue({ code: "custom", message: "Package history cannot authorize cleanup." });
});

// birdsong-yard-sprites/src/lib/assets/intake-v3.ts
import { z as z24 } from "zod";

// birdsong-yard-sprites/src/lib/assets/intake-v2.ts
import { z as z22 } from "zod";

// birdsong-yard-sprites/src/lib/assets/intake.ts
import { z as z18 } from "zod";
var identifier4 = z18.string().min(1).max(160).regex(/^[a-zA-Z0-9][a-zA-Z0-9._:@-]*$/);
var hash = z18.string().regex(/^[a-f0-9]{64}$/);
var label = z18.string().trim().min(1).max(200);
var manifestShape = speciesManifestV2Schema.innerType().shape;
var assetSourceSchema = z18.object({
  schemaVersion: z18.literal(1),
  speciesId: identifier4,
  representation: label,
  source: z18.enum(["deterministic_fixture", "user_upload", "provider"]),
  creator: identifier4,
  sourceVersion: identifier4,
  license: z18.object({
    id: label,
    status: z18.enum(["development-only", "cleared", "pending", "denied"]),
    derivativesAllowed: z18.boolean(),
    redistributionAllowed: z18.boolean(),
    evidenceId: identifier4.nullable(),
    attribution: z18.string().trim().min(1).max(300)
  }).strict(),
  references: z18.array(
    z18.object({
      id: identifier4,
      speciesId: identifier4,
      contentDigest: hash,
      role: z18.enum(["technical-fixture", "species-reference"])
    }).strict()
  ).min(1).max(16),
  fidelityReview: z18.object({
    reviewerId: identifier4,
    reviewedAt: z18.string().datetime(),
    evidenceId: identifier4
  }).strict().nullable()
}).strict();
var pixelAnimationSourceSchema = z18.object({
  schemaVersion: z18.literal(1),
  format: z18.literal("rgba8-frames"),
  canvas: manifestShape.canvas,
  logicalPixelSize: z18.number().int().min(1).max(16),
  paletteLimit: z18.number().int().min(1).max(64),
  frames: z18.array(
    z18.object({
      rgba: z18.array(z18.number().int().min(0).max(255)).min(4).max(256 * 256 * 4)
    }).strict()
  ).min(1).max(64),
  clips: manifestShape.clips
}).strict();
var assetPackagingInputSchema = z18.object({
  schemaVersion: z18.literal(1),
  source: assetSourceSchema,
  pixels: pixelAnimationSourceSchema
}).strict();
var assetGenerationInputSchema = z18.object({
  schemaVersion: z18.literal(1),
  source: assetSourceSchema,
  requestedStates: z18.array(z18.enum(animationStates)).min(1).max(9)
}).strict();

// birdsong-yard-sprites/src/lib/assets/manifest-v3.ts
import { z as z20 } from "zod";

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
import { z as z19 } from "zod";
var coordinate = z19.number().int().min(0).max(256);
var point2 = z19.object({ x: coordinate, y: coordinate }).strict();
var id = z19.string().min(1).max(160).regex(/^[a-zA-Z0-9][a-zA-Z0-9._:@-]*$/);
var physicalFootprintSchema = z19.object({
  left: z19.number().int().min(0).max(128),
  right: z19.number().int().min(0).max(128),
  back: z19.number().int().min(0).max(64),
  front: z19.number().int().min(0).max(64)
}).strict().refine(
  (value) => value.left + value.right > 0 && value.back + value.front > 0,
  "Physical footprint must have positive width and depth."
);
var visualBoundsSchema = z19.object({
  x: coordinate,
  y: coordinate,
  width: z19.number().int().min(1).max(256),
  height: z19.number().int().min(1).max(256)
}).strict();
var shapePoseSchema = z19.object({
  poseId: id,
  frame: z19.number().int().min(0).max(63),
  visualBounds: visualBoundsSchema,
  support: point2,
  footprint: physicalFootprintSchema,
  landmarks: z19.array(
    point2.extend({ kind: z19.enum(["head", "body", "beak", "tail", "left-foot", "right-foot"]) }).strict()
  ).max(6)
}).strict();
var shapeReviewSchema = z19.object({
  schemaVersion: z19.literal(1),
  basedOn: animationPinSchema,
  speciesId: id,
  masterPoseId: id,
  poses: z19.array(shapePoseSchema).min(1).max(576)
}).strict().superRefine((value, context) => {
  if (new Set(value.poses.map((pose) => pose.poseId)).size !== value.poses.length)
    context.addIssue({ code: "custom", message: "Shape pose IDs must be unique." });
  if (!value.poses.some((pose) => pose.poseId === value.masterPoseId))
    context.addIssue({ code: "custom", message: "Master pose must identify an annotated pose." });
  if (value.poses.some(
    (pose) => new Set(pose.landmarks.map((point3) => point3.kind)).size !== pose.landmarks.length
  ))
    context.addIssue({ code: "custom", message: "Landmark kinds must be distinct per pose." });
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
    if (!bounds || ["x", "y", "width", "height"].some((key2) => bounds[key2] !== pose.visualBounds[key2]))
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
var id2 = z20.string().min(1).max(160).regex(/^[a-zA-Z0-9][a-zA-Z0-9._:@-]*$/);
var integer3 = z20.number().int().min(0).max(Number.MAX_SAFE_INTEGER);
var pointSchema = z20.object({ x: integer3.max(256), y: integer3.max(256) }).strict();
var contactSchema = pointSchema.extend({
  kind: z20.enum(["left-foot", "right-foot", "perch", "ground"])
}).strict();
var animationPoseSchema = z20.object({
  frame: integer3.max(63),
  durationTicks: z20.number().int().min(1).max(300),
  pivot: pointSchema,
  contacts: z20.array(contactSchema).max(4),
  poseId: id2,
  rotation: z20.number().min(-0.5).max(0.5)
}).strict();
var animationClipV3Schema = z20.object({
  action: z20.enum(animationStates),
  direction: z20.literal("right-facing-mirrorable"),
  loop: z20.boolean(),
  poses: z20.array(animationPoseSchema).min(1).max(256)
}).strict();
var animationClipsV3Schema = z20.object({
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
var taxonomyIdentitySchema = z20.object({
  catalog: z20.literal("chirp-display-catalog"),
  version: z20.literal(1),
  speciesId: id2
}).strict().superRefine((value, context) => {
  if (!catalogEntry(value.speciesId))
    context.addIssue({
      code: "custom",
      message: "Species is absent from the pinned application catalog."
    });
});
var reviewedReferenceSchema = z20.object({
  id: id2,
  roles: z20.array(z20.enum(["species", "style", "pose"])).min(1).max(3),
  pin: animationPinSchema
}).strict().superRefine((value, context) => {
  if (new Set(value.roles).size !== value.roles.length)
    context.addIssue({ code: "custom", message: "Reference roles must be distinct." });
});
var poseGraphSchema = z20.object({
  nodes: z20.array(
    z20.object({
      id: id2,
      frame: integer3.max(63),
      action: z20.enum(animationStates),
      referenceId: id2
    }).strict()
  ).min(1).max(576),
  edges: z20.array(z20.object({ from: id2, to: id2 }).strict()).max(2304)
}).strict();
var animationConditioningSchema = z20.object({
  taxonomy: taxonomyIdentitySchema,
  references: z20.array(reviewedReferenceSchema).min(1).max(16),
  poseGraph: poseGraphSchema
}).strict();
var normalizationReportSchema = z20.object({
  algorithm: z20.literal("lossless-rgba-rects-v2"),
  alpha: z20.literal("binary"),
  logicalPixelSize: z20.number().int().min(1).max(16),
  palette: z20.array(z20.number().int().min(0).max(16777215)).min(1).max(64),
  loopEdges: z20.array(
    z20.object({
      action: z20.enum(animationStates),
      comparedPixels: integer3.min(1).max(65536),
      changedPixels: integer3.max(65536),
      pivotDistance: z20.number().min(0).max(512),
      contactLayoutChanged: z20.boolean()
    }).strict()
  ).max(9)
}).strict();
var metricGeometrySchema = z20.object({
  canvas: legacy.canvas.omit({ anchorX: true, anchorY: true }),
  frames: legacy.frames,
  clips: animationClipsV3Schema
}).strip();
var speciesManifestV3Schema = z20.object({
  schemaVersion: z20.literal(3),
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
}).strict().superRefine((value, context) => {
  const fail = (message) => context.addIssue({ code: "custom", message });
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

// birdsong-yard-sprites/src/lib/assets/png-origin.ts
import { z as z21 } from "zod";
var PNG_MAX_BYTES = 524288;
var PNG_MAX_PIXELS = 65536;
var PNG_MAX_DIMENSION = 1024;
var hash2 = z21.string().regex(/^[a-f0-9]{64}$/);
var bytes = z21.number().int().min(1).max(PNG_MAX_BYTES);
var pngFileIdentitySchema = z21.object({
  schemaVersion: z21.literal(1),
  id: z21.string().uuid(),
  original: z21.object({ sha256: hash2, bytes }).strict(),
  canonical: z21.object({
    sha256: hash2,
    bytes,
    rgbaSha256: hash2,
    width: z21.number().int().min(1).max(PNG_MAX_DIMENSION),
    height: z21.number().int().min(1).max(PNG_MAX_DIMENSION)
  }).strict(),
  decoder: z21.object({
    id: z21.literal("sharp"),
    version: z21.string().min(1).max(40),
    libvips: z21.string().min(1).max(40)
  }).strict(),
  normalization: z21.literal("chirp-png-straight-srgb8-hidden-rgb-zero-v1")
}).strict().superRefine((value, context) => {
  if (value.canonical.width * value.canonical.height > PNG_MAX_PIXELS)
    context.addIssue({ code: "custom", message: "PNG pixel budget exceeded." });
});
var pngFrameLayoutSchema = z21.object({
  width: z21.number().int().min(1).max(256),
  height: z21.number().int().min(1).max(256),
  columns: z21.number().int().min(1).max(64),
  rows: z21.number().int().min(1).max(64)
}).strict().superRefine((value, context) => {
  if (value.columns * value.rows > 64 || value.width * value.height * value.columns * value.rows > PNG_MAX_PIXELS)
    context.addIssue({ code: "custom", message: "PNG frame budget exceeded." });
});
var pngFileOriginSchema = z21.object({
  file: pngFileIdentitySchema,
  reviewDigest: hash2,
  layout: pngFrameLayoutSchema
}).strict();

// birdsong-yard-sprites/src/lib/assets/intake-v2.ts
var id3 = z22.string().min(1).max(160).regex(/^[a-zA-Z0-9][a-zA-Z0-9._:@-]*$/);
var hash3 = z22.string().regex(/^[a-f0-9]{64}$/);
var localModelManifestSchema = z22.object({
  id: id3,
  revision: id3,
  weightsSha256: hash3,
  license: z22.object({ id: id3, contentSha256: hash3 }).strict(),
  adapters: z22.array(
    z22.object({
      id: id3,
      revision: id3,
      weightsSha256: hash3,
      parentWeightsSha256: hash3,
      license: z22.object({ id: id3, contentSha256: hash3 }).strict()
    }).strict()
  ).max(8)
}).strict().superRefine((value, context) => {
  if (new Set(value.adapters.map((adapter) => adapter.id)).size !== value.adapters.length || value.adapters.some((adapter) => adapter.parentWeightsSha256 !== value.weightsSha256))
    context.addIssue({
      code: "custom",
      message: "Adapter IDs must be unique and pin the declared parent model weights."
    });
});
var unsupportedStrategy = z22.object({
  version: z22.literal(1),
  execution: z22.literal("unconfigured-local"),
  model: localModelManifestSchema,
  alphaPlan: z22.enum(["native-binary", "native-continuous", "layered", "matting-required"])
}).strict();
var generationStrategySchema = z22.discriminatedUnion("kind", [
  z22.object({
    kind: z22.literal("decoded-rgba"),
    version: z22.literal(1),
    alphaOrigin: z22.enum(["technical-fixture", "native", "upstream-cleanup", "unknown"]),
    output: z22.literal("rgba8-binary")
  }).strict(),
  unsupportedStrategy.extend({ kind: z22.literal("direct-spritesheet") }).strict(),
  unsupportedStrategy.extend({ kind: z22.literal("conditioned-frame-edit") }).strict(),
  unsupportedStrategy.extend({ kind: z22.literal("video-extract") }).strict(),
  unsupportedStrategy.extend({ kind: z22.literal("rigged-deterministic") }).strict()
]);
var pixelAnimationSourceV2Schema = pixelAnimationSourceSchema.omit({ clips: true }).extend({
  schemaVersion: z22.literal(2),
  canvas: speciesManifestV2Schema.innerType().shape.canvas.omit({ anchorX: true, anchorY: true })
}).strict();
var assetPackagingInputV2Schema = z22.object({
  schemaVersion: z22.literal(2),
  source: assetSourceSchema,
  pixels: pixelAnimationSourceV2Schema,
  clips: animationClipsV3Schema,
  conditioning: animationConditioningSchema,
  strategy: generationStrategySchema,
  shape: shapeReviewSchema.optional(),
  fileOrigin: pngFileOriginSchema.optional()
}).strict().superRefine((value, context) => {
  if (value.conditioning.taxonomy.speciesId !== value.source.speciesId)
    context.addIssue({ code: "custom", message: "Source and pinned taxonomy species differ." });
  if (value.strategy.kind === "decoded-rgba" && value.source.source === "deterministic_fixture" !== (value.strategy.alphaOrigin === "technical-fixture"))
    context.addIssue({
      code: "custom",
      message: "Technical fixture alpha declarations cannot claim native generation."
    });
  const refs = value.conditioning.references;
  if (new Set(refs.map((reference) => reference.id)).size !== refs.length || value.source.references.length !== refs.length || refs.some(
    (reference) => !value.source.references.some(
      (source) => source.id === reference.id && source.contentDigest === reference.pin.contentDigest
    )
  ))
    context.addIssue({
      code: "custom",
      message: "Conditioning pins must match every declared source reference and hash."
    });
});
var rgbaSourceArtifactSchema = z22.object({
  schemaVersion: z22.literal(1),
  format: z22.literal("private-rgba-source"),
  lifecycle: z22.literal("retained-until-owner-deletion"),
  inputDigest: hash3,
  input: assetPackagingInputV2Schema,
  blobs: z22.array(
    z22.object({
      frame: z22.number().int().min(0).max(63),
      encoding: z22.literal("rgba8"),
      bytes: z22.number().int().min(4).max(256 * 256 * 4),
      sha256: hash3
    }).strict()
  ).min(1).max(64)
}).strict().superRefine((value, context) => {
  if (value.blobs.length !== value.input.pixels.frames.length || value.blobs.some(
    (blob, index) => blob.frame !== index || blob.bytes !== value.input.pixels.canvas.width * value.input.pixels.canvas.height * 4 || blob.bytes !== value.input.pixels.frames[index]?.rgba.length
  ))
    context.addIssue({
      code: "custom",
      message: "Source blob descriptors must match every decoded frame."
    });
});

// birdsong-yard-sprites/src/lib/assets/manifest-v4.ts
import { z as z23 } from "zod";
var assetPresentationSchema = z23.object({
  schemaVersion: z23.literal(1),
  sourcePixelsPerWorldUnit: z23.union([z23.literal(1), z23.literal(2), z23.literal(4)])
}).strict();
var speciesManifestV4Schema = speciesManifestV3Schema.innerType().extend({
  schemaVersion: z23.literal(4),
  presentation: assetPresentationSchema
}).strict().superRefine((value, context) => {
  const legacy2 = { ...value };
  Reflect.deleteProperty(legacy2, "presentation");
  const result2 = speciesManifestV3Schema.safeParse({ ...legacy2, schemaVersion: 3 });
  if (!result2.success) for (const issue of result2.error.issues) context.addIssue(issue);
});

// birdsong-yard-sprites/src/lib/assets/intake-v3.ts
var assetPackagingInputV3Schema = assetPackagingInputV2Schema.innerType().extend({
  schemaVersion: z24.literal(3),
  presentation: assetPresentationSchema
}).strict().superRefine((value, context) => {
  const legacy2 = { ...value };
  Reflect.deleteProperty(legacy2, "presentation");
  const result2 = assetPackagingInputV2Schema.safeParse({ ...legacy2, schemaVersion: 2 });
  if (!result2.success) for (const issue of result2.error.issues) context.addIssue(issue);
});
var rgbaSourceArtifactV2Schema = rgbaSourceArtifactSchema.innerType().extend({
  schemaVersion: z24.literal(2),
  input: assetPackagingInputV3Schema
}).strict().superRefine((value, context) => {
  const legacy2 = { ...value.input };
  Reflect.deleteProperty(legacy2, "presentation");
  const result2 = rgbaSourceArtifactSchema.safeParse({
    ...value,
    schemaVersion: 1,
    input: { ...legacy2, schemaVersion: 2 }
  });
  if (!result2.success) for (const issue of result2.error.issues) context.addIssue(issue);
});
var supportedPosePackagingInputSchema = z24.union([
  assetPackagingInputV2Schema,
  assetPackagingInputV3Schema
]);
var supportedRgbaSourceArtifactSchema = z24.union([
  rgbaSourceArtifactSchema,
  rgbaSourceArtifactV2Schema
]);

// birdsong-yard-sprites/src/lib/assets/manifest.ts
import { z as z25 } from "zod";
var speciesManifestSchema = z25.union([
  speciesManifestV2Schema,
  speciesManifestV3Schema,
  speciesManifestV4Schema
]);

// birdsong-yard-sprites/src/lib/assets/animation-specification.ts
import { z as z27 } from "zod";

// birdsong-yard-sprites/src/lib/assets/image-stage-contracts.ts
import { z as z26 } from "zod";
var id4 = z26.string().min(1).max(160).regex(/^[a-zA-Z0-9][a-zA-Z0-9._:@-]*$/);
var sha256 = z26.string().regex(/^[a-f0-9]{64}$/);
var text = z26.string().min(1).max(2e3).refine((value) => value === value.trim(), "Reference metadata must already be normalized").refine(
  (value) => [...value].every(
    (character) => character >= " " && character !== "\x7F" && character !== "<" && character !== ">"
  ),
  "Reference metadata must be plain text"
);
var https = z26.string().max(2048).regex(/^https:\/\/[!-~]+(?![\s\S])/).refine((value) => {
  try {
    const url = new URL(value);
    return url.protocol === "https:" && !url.username && !url.password;
  } catch {
    return false;
  }
}, "Only credential-free HTTPS source identifiers are allowed");
var pointInTime = z26.string().datetime();
var review = z26.object({ reviewerId: id4, evidenceId: id4, reviewedAt: pointInTime }).strict();
var localReferenceSchema = z26.object({
  schemaVersion: z26.literal(1),
  id: id4,
  fixture: z26.boolean(),
  source: z26.object({
    kind: z26.enum(["local-file", "archive-file", "technical-fixture"]),
    fileIdentity: text,
    originalUrl: https.nullable(),
    descriptionPageUrl: https.nullable(),
    author: text,
    uploader: text.nullable(),
    attribution: text,
    description: text.nullable(),
    sourceTimestamp: pointInTime.nullable(),
    remoteHash: z26.object({
      algorithm: z26.enum(["sha1", "sha256"]),
      value: z26.string().regex(/^[a-f0-9]{40}([a-f0-9]{24})?$/)
    }).strict().nullable()
  }).strict(),
  original: z26.object({
    bytes: z26.number().int().min(1).max(16777216),
    sha256,
    mime: z26.enum(["image/png", "image/jpeg", "application/x-chirp-rgba8"])
  }).strict(),
  decoded: z26.object({
    format: z26.literal("rgba8-straight"),
    width: z26.number().int().min(1).max(256),
    height: z26.number().int().min(1).max(256),
    sha256,
    decoder: z26.object({ id: id4, version: id4 }).strict(),
    derivation: z26.enum(["raw-identity", "declared-unverified"])
  }).strict(),
  rights: z26.object({
    licenseId: id4,
    licenseVersion: id4,
    licenseUrl: https.nullable(),
    status: z26.enum(["pending", "approved", "denied", "conflicting"]),
    restrictions: z26.array(text).max(16),
    referenceUseAllowed: z26.boolean(),
    derivativesAllowed: z26.boolean(),
    redistributionAllowed: z26.boolean(),
    generationPermission: z26.enum(["not-reviewed", "allowed", "denied"]),
    review: review.nullable()
  }).strict(),
  taxonomy: z26.object({
    application: taxonomyIdentitySchema,
    declaredScientificName: text,
    aliases: z26.array(
      z26.object({ authority: id4, version: id4, taxonId: id4, scientificName: text }).strict()
    ).max(16),
    externalEvidence: z26.array(
      z26.object({
        authority: id4,
        version: id4,
        entityId: id4,
        statement: z26.enum(["scientific-name", "rank", "parent-taxon", "image", "depicts"]),
        value: text,
        status: z26.literal("candidate-evidence")
      }).strict()
    ).max(32),
    review: review.nullable()
  }).strict(),
  annotations: z26.object({
    sex: z26.enum(["female", "male", "unknown"]),
    age: z26.enum(["juvenile", "adult", "unknown"]),
    plumage: text.nullable(),
    viewpoint: z26.enum([
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
}).strict().superRefine((value, context) => {
  const fail = (message) => context.addIssue({ code: "custom", message });
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
var referencePolicySchema = z26.object({
  schemaVersion: z26.literal(1),
  id: id4,
  version: id4,
  use: z26.enum(["reference-only", "derived-sprite"]),
  allowedLicenses: z26.array(z26.object({ id: id4, version: id4, url: https.nullable() }).strict()).max(32),
  allowTechnicalFixtures: z26.boolean()
}).strict();
var byte = z26.number().int().min(0).max(255);
var channel = z26.array(byte).min(1).max(65536);
var coordinates = z26.object({ x: z26.number().int().min(0).max(256), y: z26.number().int().min(0).max(256) }).strict();
var contact = coordinates.extend({ kind: z26.enum(["left-foot", "right-foot", "ground", "perch"]) }).strict();
var stageIdentity = z26.object({ id: id4, version: id4 }).strict();
var segmentationStageSchema = z26.discriminatedUnion("encoding", [
  z26.object({
    encoding: z26.literal("binary-mask-u8"),
    values: z26.array(z26.union([z26.literal(0), z26.literal(255)])).min(1).max(65536),
    sha256,
    adapter: stageIdentity
  }).strict(),
  z26.object({
    encoding: z26.literal("logits-f32-le"),
    values: z26.array(z26.number().finite().min(-1e6).max(1e6)).min(1).max(65536),
    sha256,
    adapter: stageIdentity
  }).strict()
]);
var matteStageSchema = z26.object({
  encoding: z26.literal("alpha-u8"),
  alpha: channel,
  sha256,
  origin: z26.enum(["supplied-matte", "technical-fixture"]),
  adapter: stageIdentity
}).strict();
var foregroundStageSchema = z26.object({
  encoding: z26.literal("rgb8"),
  rgb: z26.array(byte).min(3).max(65536 * 3),
  sha256,
  alphaMode: z26.enum(["straight", "premultiplied"]),
  recovery: z26.enum(["supplied-recovered", "technical-fixture"]),
  adapter: stageIdentity
}).strict();
var imageFrameSchema = z26.object({
  id: id4,
  timestampUs: z26.number().int().min(0).max(Number.MAX_SAFE_INTEGER),
  durationUs: z26.number().int().min(1).max(6e7),
  sourceRgba: z26.array(byte).min(4).max(65536 * 4),
  sourceSha256: sha256,
  anchor: coordinates,
  contacts: z26.array(contact).max(4),
  segmentation: segmentationStageSchema.nullable(),
  matte: matteStageSchema,
  foreground: foregroundStageSchema
}).strict();
var imageStageSequenceSchema = z26.object({
  schemaVersion: z26.literal(1),
  fixture: z26.boolean(),
  canvas: z26.object({ width: z26.number().int().min(1).max(256), height: z26.number().int().min(1).max(256) }).strict(),
  frames: z26.array(imageFrameSchema).min(1).max(64),
  loop: z26.boolean(),
  // These are audit identities, not URLs, invocation settings, or an execution capability.
  referenceIds: z26.array(id4).min(1).max(16),
  modelSlot: z26.literal("unconfigured")
}).strict().superRefine((sequence, context) => {
  const fail = (message) => context.addIssue({ code: "custom", message });
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
var imageQaPolicySchema = z26.object({
  schemaVersion: z26.literal(1),
  id: id4,
  version: id4,
  edgeAlphaThreshold: byte.min(1),
  maxChangedEdgeFraction: z26.number().min(0).max(1),
  maxContactDriftPixels: z26.number().min(0).max(512),
  allowContactSetChange: z26.boolean()
}).strict();
var losslessPixelPolicySchema = z26.object({
  schemaVersion: z26.literal(1),
  id: id4,
  version: id4,
  alpha: z26.literal("binary-required"),
  palette: z26.literal("preserve"),
  logicalPixelSize: z26.number().int().min(1).max(16),
  paletteLimit: z26.number().int().min(1).max(64),
  crop: z26.literal("stable-union-including-anchors")
}).strict();

// birdsong-yard-sprites/src/lib/assets/animation-specification.ts
var hash4 = z27.string().regex(/^[a-f0-9]{64}$/);
var id5 = z27.string().regex(/^[a-zA-Z0-9][a-zA-Z0-9._:@-]{0,159}$/);
var text2 = z27.string().min(1).max(4e3);
var animationPlanningInputSchema = z27.object({
  schemaVersion: z27.literal(1),
  taxonomy: taxonomyIdentitySchema,
  scientificName: z27.string().min(3).max(160),
  references: z27.array(localReferenceSchema).max(16)
}).strict().superRefine((value, context) => {
  const fail = (message) => context.addIssue({ code: "custom", message });
  if (catalogEntry(value.taxonomy.speciesId)?.scientificName !== value.scientificName)
    fail("Scientific name must exactly match the pinned application catalog identity.");
  if (new Set(value.references.map((reference) => reference.id)).size !== value.references.length)
    fail("Planning reference IDs must be unique.");
  for (const reference of value.references)
    if (reference.taxonomy.application.speciesId !== value.taxonomy.speciesId || reference.taxonomy.declaredScientificName !== value.scientificName)
      fail("Reference identity must match the planned species and its scientific name.");
});
function canonicalAnimationPlanningInput(value) {
  const input = animationPlanningInputSchema.parse(value);
  input.references.sort((left, right) => left.id < right.id ? -1 : left.id > right.id ? 1 : 0);
  return input;
}
var frameSchema = z27.object({
  frame: animationPoseSchema.shape.frame,
  phase: z27.string().min(1).max(160),
  durationTicks: animationPoseSchema.shape.durationTicks,
  proposedPivot: pointSchema,
  contactRequirements: z27.array(contactSchema.shape.kind).max(4)
}).strict();
var clipSchema = z27.object({
  action: z27.enum(animationStates),
  direction: animationClipV3Schema.shape.direction,
  loop: z27.boolean(),
  completion: z27.enum(["repeat", "hold-final-pose"]),
  purpose: z27.string().min(1).max(300),
  frames: z27.array(frameSchema).min(1).max(64),
  entry: z27.literal("review-against-idle-support-and-silhouette"),
  exit: z27.literal("review-against-idle-support-and-silhouette"),
  loopReview: z27.enum(["last-to-first-pixels-pivot-contacts", "not-looping-review-terminal-hold"])
}).strict();
var animationSpecificationSchema = z27.object({
  schemaVersion: z27.literal(1),
  templateVersion: z27.literal("chirp-animation-prompts@1"),
  status: z27.literal("proposed"),
  canvas: z27.object({ width: z27.literal(32), height: z27.literal(32) }).strict(),
  logicalPixelSize: z27.literal(1),
  paletteLimit: z27.literal(32),
  alpha: z27.literal("binary-transparent-background"),
  ticksPerSecond: z27.literal(30),
  totalFrames: z27.number().int().min(1).max(64),
  decodedPixels: z27.number().int().min(1).max(65536),
  clips: z27.array(clipSchema).length(animationStates.length)
}).strict().superRefine((value, context) => {
  const fail = (message) => context.addIssue({ code: "custom", message });
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
var proposals = [
  {
    action: "idle",
    ticks: 9,
    purpose: "Quiet settled alert pose; review subtle body and head motion.",
    phases: ["settled", "breathe-in", "breathe-out", "return-settled"],
    contact: "ground",
    loop: true
  },
  {
    action: "moving",
    ticks: 3,
    purpose: "Current moving state covers hop, flight, arrival and scatter; review this shared-motion limitation.",
    phases: [
      "support",
      "lift",
      "wing-up",
      "wing-mid-down",
      "wing-down",
      "wing-mid-up",
      "approach-support",
      "settle"
    ],
    contact: "mixed",
    loop: true
  },
  {
    action: "perching",
    ticks: 12,
    purpose: "Stable perch balance with support contacts retained.",
    phases: ["perch-settled", "look", "rebalance", "return-perch"],
    contact: "perch",
    loop: true
  },
  {
    action: "singing",
    ticks: 5,
    purpose: "Visible singing posture without adding audio or claiming song accuracy.",
    phases: ["ready", "head-lift", "beak-open", "hold-song", "beak-close", "return-ready"],
    contact: "perch",
    loop: true
  },
  {
    action: "feeding",
    ticks: 5,
    purpose: "Reach, peck and recovery with stable support; beak contact is a human review requirement, not an unsupported contact type.",
    phases: [
      "ready",
      "lean",
      "reach",
      "peck",
      "recover-head",
      "hold",
      "straighten",
      "return-ready"
    ],
    contact: "ground",
    loop: true
  },
  {
    action: "bathing",
    ticks: 3,
    purpose: "Illustrative bathing body motion; water/splash belongs to a separate effect layer.",
    phases: [
      "ready",
      "lower",
      "dip",
      "shake-left",
      "shake-right",
      "lift",
      "recover",
      "return-ready"
    ],
    contact: "ground",
    loop: true
  },
  {
    action: "sleeping",
    ticks: 30,
    purpose: "Perched restful-pose proposal; existing sleep also supports roost and safe ground, requiring separate support review before reuse.",
    phases: ["rest", "breathe-in", "breathe-out", "return-rest"],
    contact: "perch",
    loop: true
  },
  {
    action: "playing",
    ticks: 5,
    purpose: "One illustrative gesture on the current perch:right play support; object physics and individual behavior are separate engine concerns.",
    phases: [
      "ready",
      "notice-object",
      "lean",
      "touch",
      "withdraw",
      "look",
      "recover",
      "terminal-settled"
    ],
    contact: "perch",
    loop: false
  },
  {
    action: "nesting",
    ticks: 6,
    purpose: "One illustrative material-placement gesture on the nest center surface; ground contact means surface support, not yard elevation. Biological technique needs review.",
    phases: [
      "ready",
      "inspect",
      "reach",
      "gather",
      "lift-material",
      "turn-to-nest",
      "place",
      "release",
      "recover",
      "terminal-settled"
    ],
    contact: "ground",
    loop: false
  }
];
function proposedAnimationSpecification() {
  let nextFrame = 0;
  const clips = proposals.map((proposal) => ({
    action: proposal.action,
    direction: "right-facing-mirrorable",
    loop: proposal.loop,
    completion: proposal.loop ? "repeat" : "hold-final-pose",
    purpose: proposal.purpose,
    frames: proposal.phases.map((phase, index) => ({
      frame: nextFrame++,
      phase,
      durationTicks: proposal.ticks,
      proposedPivot: { x: 16, y: 28 },
      contactRequirements: proposal.contact === "mixed" && index > 0 && index < proposal.phases.length - 1 ? [] : ["left-foot", "right-foot", proposal.contact === "perch" ? "perch" : "ground"]
    })),
    entry: "review-against-idle-support-and-silhouette",
    exit: "review-against-idle-support-and-silhouette",
    loopReview: proposal.loop ? "last-to-first-pixels-pivot-contacts" : "not-looping-review-terminal-hold"
  }));
  return animationSpecificationSchema.parse({
    schemaVersion: 1,
    templateVersion: "chirp-animation-prompts@1",
    status: "proposed",
    canvas: { width: 32, height: 32 },
    logicalPixelSize: 1,
    paletteLimit: 32,
    alpha: "binary-transparent-background",
    ticksPerSecond: 30,
    totalFrames: nextFrame,
    decodedPixels: 32 * 32 * nextFrame,
    clips
  });
}
var animationRecipeSchema = z27.object({
  schemaVersion: z27.literal(1),
  id: id5,
  version: z27.number().int().min(1).max(1e6),
  specification: animationSpecificationSchema
}).strict();
var frameOverrideSchema = z27.object({
  index: z27.number().int().min(0).max(63),
  phase: z27.string().regex(/^[a-z][a-z0-9-]{0,159}$/).optional(),
  durationTicks: animationPoseSchema.shape.durationTicks.optional(),
  proposedPivot: z27.object({ x: pointSchema.shape.x.max(32), y: pointSchema.shape.y.max(32) }).strict().optional(),
  contactRequirements: z27.array(contactSchema.shape.kind).max(4).optional()
}).strict().superRefine((value, context) => {
  if (Object.keys(value).length === 1)
    context.addIssue({
      code: "custom",
      message: "A frame override must explicitly change a field."
    });
  if (value.contactRequirements && new Set(value.contactRequirements).size !== value.contactRequirements.length)
    context.addIssue({
      code: "custom",
      message: "Override contact requirements must be distinct."
    });
});
var clipOverrideSchema = z27.object({
  action: z27.enum(animationStates),
  durationTicks: animationPoseSchema.shape.durationTicks.optional(),
  loop: z27.boolean().optional(),
  frames: z27.array(frameOverrideSchema).min(1).max(64).optional()
}).strict().superRefine((value, context) => {
  if (Object.keys(value).length === 1)
    context.addIssue({
      code: "custom",
      message: "A clip override must explicitly change a field."
    });
  if (value.frames && new Set(value.frames.map((frame) => frame.index)).size !== value.frames.length)
    context.addIssue({
      code: "custom",
      message: "Frame override indices must be unique within a clip."
    });
});
var animationPlanningInputV2Schema = z27.object({
  schemaVersion: z27.literal(2),
  taxonomy: taxonomyIdentitySchema,
  scientificName: z27.string().min(3).max(160),
  references: z27.array(localReferenceSchema).max(16),
  recipe: z27.object({ id: id5, version: animationRecipeSchema.shape.version }).strict(),
  overrides: z27.object({ clips: z27.array(clipOverrideSchema).max(animationStates.length) }).strict()
}).strict().superRefine((value, context) => {
  const identity = animationPlanningInputSchema.safeParse({
    schemaVersion: 1,
    taxonomy: value.taxonomy,
    scientificName: value.scientificName,
    references: value.references
  });
  if (!identity.success) for (const issue of identity.error.issues) context.addIssue(issue);
  if (new Set(value.overrides.clips.map((clip3) => clip3.action)).size !== value.overrides.clips.length)
    context.addIssue({ code: "custom", message: "Each clip can have only one override." });
});
function defaultAnimationRecipe() {
  return animationRecipeSchema.parse({
    schemaVersion: 1,
    id: "chirp-default-bird",
    version: 1,
    specification: proposedAnimationSpecification()
  });
}
function canonicalAnimationPlanningInputV2(value) {
  const input = animationPlanningInputV2Schema.parse(value);
  input.references.sort((left, right) => left.id < right.id ? -1 : left.id > right.id ? 1 : 0);
  input.overrides.clips.sort(
    (left, right) => animationStates.indexOf(left.action) - animationStates.indexOf(right.action)
  );
  for (const clip3 of input.overrides.clips) {
    clip3.frames?.sort((left, right) => left.index - right.index);
    for (const frame of clip3.frames ?? []) frame.contactRequirements?.sort();
  }
  return input;
}
function resolveAnimationSpecification(value, recipes = [defaultAnimationRecipe()]) {
  const input = canonicalAnimationPlanningInputV2(value);
  const registry = z27.array(animationRecipeSchema).min(1).max(64).parse(recipes);
  const keys = registry.map((recipe2) => `${recipe2.id}@${recipe2.version}`);
  if (new Set(keys).size !== keys.length)
    throw new Error("Duplicate animation recipe identity/version.");
  const recipe = registry.find(
    (entry) => entry.id === input.recipe.id && entry.version === input.recipe.version
  );
  if (!recipe) throw new Error("Unknown animation recipe identity/version.");
  const specification = recipe.specification;
  for (const override of input.overrides.clips) {
    const clip3 = specification.clips.find((entry) => entry.action === override.action);
    if (!clip3) throw new Error("Unknown animation clip override.");
    const presentation = () => JSON.stringify([
      clip3.loop,
      clip3.frames.map((frame) => [
        frame.phase,
        frame.durationTicks,
        frame.proposedPivot.x,
        frame.proposedPivot.y,
        [...frame.contactRequirements].sort()
      ])
    ]);
    const inheritedPresentation = presentation();
    if (override.durationTicks !== void 0)
      for (const frame of clip3.frames) frame.durationTicks = override.durationTicks;
    if (override.loop !== void 0) {
      clip3.loop = override.loop;
      clip3.completion = clip3.loop ? "repeat" : "hold-final-pose";
      clip3.loopReview = clip3.loop ? "last-to-first-pixels-pivot-contacts" : "not-looping-review-terminal-hold";
    }
    for (const frameOverride of override.frames ?? []) {
      const frame = clip3.frames[frameOverride.index];
      if (!frame) throw new Error("Frame override index is outside the selected recipe clip.");
      if (frameOverride.phase !== void 0) frame.phase = frameOverride.phase;
      if (frameOverride.durationTicks !== void 0)
        frame.durationTicks = frameOverride.durationTicks;
      if (frameOverride.proposedPivot !== void 0)
        frame.proposedPivot = frameOverride.proposedPivot;
      if (frameOverride.contactRequirements !== void 0 && (frame.contactRequirements.length !== frameOverride.contactRequirements.length || frame.contactRequirements.some(
        (kind) => !frameOverride.contactRequirements?.includes(kind)
      )))
        frame.contactRequirements = frameOverride.contactRequirements;
    }
    if (presentation() !== inheritedPresentation)
      clip3.purpose = `${clip3.action} presentation variant: follow the resolved per-frame phases, timing, pivots, contact requirements and loop policy. Re-review behavior and support assumptions before reuse; no biological fidelity is established by this override.`;
  }
  return animationSpecificationSchema.parse(specification);
}
var animationProductionPlanSchema = z27.object({
  schemaVersion: z27.literal(1),
  format: z27.literal("animation-production-plan"),
  execution: z27.literal("planning-only"),
  model: z27.literal("unconfigured"),
  generatedFrames: z27.literal(0),
  taxonFidelityReviewed: z27.literal(false),
  taxonomy: taxonomyIdentitySchema,
  scientificName: z27.string().min(3).max(160),
  inputSha256: hash4,
  specificationSha256: hash4,
  specification: animationSpecificationSchema,
  references: z27.array(
    z27.object({
      id: id5,
      originalSha256: hash4,
      decodedSha256: hash4,
      status: z27.literal("declared-not-byte-verified")
    }).strict()
  ).max(16),
  blockers: z27.array(
    z27.enum([
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
  prompts: z27.array(
    z27.object({
      action: z27.enum(animationStates),
      templateVersion: z27.literal("chirp-animation-prompts@1"),
      prompt: text2,
      negativePrompt: text2,
      frames: z27.array(z27.object({ frame: animationPoseSchema.shape.frame, prompt: text2 }).strict()).min(1).max(64)
    }).strict()
  ).length(animationStates.length),
  limitations: z27.array(text2).min(1).max(16)
}).strict().superRefine((value, context) => {
  const fail = (message) => context.addIssue({ code: "custom", message });
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

// birdsong-yard-sprites/src/lib/assets/reference-discovery.ts
import { z as z28 } from "zod";
var id6 = z28.string().regex(/^[a-zA-Z0-9][a-zA-Z0-9._:@-]{0,159}$/);
var text3 = z28.string().trim().min(1).max(2e3);
var sha2562 = z28.string().regex(/^[a-f0-9]{64}$/);
var scientificName = z28.string().regex(/^[A-Z][a-z]{1,39} [a-z]{2,40}(?: [a-z]{2,40})?$/);
var publicHttps = z28.string().max(2048).refine((value) => {
  try {
    const url = new URL(value);
    return url.protocol === "https:" && !url.username && !url.password && !url.port && !url.hash;
  } catch {
    return false;
  }
}, "A credential-free HTTPS source identifier is required.");
var referenceSourcePinSchema = z28.object({ id: id6, version: z28.number().int().min(1).max(100) }).strict();
var referenceSourceDescriptorSchema = referenceSourcePinSchema.extend({
  schemaVersion: z28.literal(1),
  name: text3,
  homepage: publicHttps,
  capabilities: z28.object({ search: z28.literal(true), originalFetch: z28.boolean() }).strict()
}).strict();
var referenceDiscoveryPolicySchema = z28.object({
  schemaVersion: z28.literal(1),
  purpose: z28.enum(["reference-only", "derived-sprite"]),
  commercial: z28.boolean(),
  allowShareAlike: z28.boolean()
}).strict();
var referenceDiscoveryRequestSchema = z28.object({
  schemaVersion: z28.literal(1),
  taxonomy: taxonomyIdentitySchema,
  scientificName,
  aliases: z28.array(scientificName).max(4),
  sources: z28.array(referenceSourcePinSchema).min(1).max(3),
  suppliedReferences: z28.array(localReferenceSchema).max(16),
  policy: referenceDiscoveryPolicySchema
}).strict().superRefine((value, context) => {
  const fail = (message) => context.addIssue({ code: "custom", message });
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
function defaultReferenceDiscoveryRequest(speciesId) {
  const entry = catalogEntry(speciesId);
  if (!entry) throw new Error("Reference discovery requires a supported catalog species.");
  return referenceDiscoveryRequestSchema.parse({
    schemaVersion: 1,
    taxonomy: { catalog: "chirp-display-catalog", version: 1, speciesId },
    scientificName: entry.scientificName,
    aliases: [],
    sources: [{ id: "wikimedia-commons", version: 1 }],
    suppliedReferences: [],
    policy: {
      schemaVersion: 1,
      purpose: "reference-only",
      commercial: false,
      allowShareAlike: false
    }
  });
}
var referenceLicenseSchema = z28.object({
  id: z28.enum([
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
  version: z28.string().regex(/^[1-4]\.[05]$/).nullable(),
  url: publicHttps.nullable(),
  declaredName: text3.nullable(),
  attribution: text3.nullable(),
  status: z28.enum(["recognized", "unknown", "conflicting"]),
  restrictions: z28.array(text3).max(8)
}).strict();
var referenceRightsDecisionSchema = z28.object({
  status: z28.enum(["eligible-for-review", "review-required", "denied"]),
  reasons: z28.array(
    z28.enum([
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
  generationApproved: z28.literal(false)
}).strict();
var discoveredReferenceSchema = z28.object({
  schemaVersion: z28.literal(1),
  id: id6,
  source: referenceSourcePinSchema,
  sourceFileId: id6,
  title: text3,
  pageUrl: publicHttps,
  originalUrl: publicHttps,
  accessedAt: z28.string().datetime(),
  sourceUpdatedAt: z28.string().datetime().nullable(),
  creator: text3.nullable(),
  uploader: text3.nullable(),
  license: referenceLicenseSchema,
  sourceSha1: z28.string().regex(/^[a-f0-9]{40}$/).nullable(),
  declaredBytes: z28.number().int().min(1).max(Number.MAX_SAFE_INTEGER),
  width: z28.number().int().min(1).max(1e5),
  height: z28.number().int().min(1).max(1e5),
  mime: z28.enum(["image/jpeg", "image/png"]),
  identification: z28.object({
    confidence: z28.enum(["text-match", "unresolved"]),
    matchedName: scientificName.nullable(),
    review: z28.literal("required")
  }).strict(),
  poseSuitability: z28.literal("unreviewed"),
  rightsDecision: referenceRightsDecisionSchema
}).strict().superRefine((value, context) => {
  if (value.identification.confidence === "text-match" !== (value.identification.matchedName !== null))
    context.addIssue({
      code: "custom",
      message: "Text-match confidence requires an explicit matched name."
    });
});
var referenceDiscoveryResultSchema = z28.object({
  schemaVersion: z28.literal(1),
  format: z28.literal("reference-discovery-result"),
  taxonomy: taxonomyIdentitySchema,
  scientificName,
  requestSha256: sha2562,
  policy: referenceDiscoveryPolicySchema,
  status: z28.enum(["supplied", "candidates", "no-results", "blocked", "partial"]),
  suppliedReferenceIds: z28.array(id6).max(16),
  candidates: z28.array(discoveredReferenceSchema).max(12),
  sources: z28.array(
    z28.object({
      id: id6,
      version: z28.number().int().min(1).max(100),
      status: z28.enum(["complete", "partial", "blocked", "skipped"]),
      code: z28.enum([
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
  requestCount: z28.number().int().min(0).max(8),
  downloadCount: z28.literal(0),
  /** Body bytes admitted into bounded buffers, excluding any rejected overflow chunk.
   * This is not a wire-transfer/compressed-byte count. byte-budget records such rejection. */
  totalBytes: z28.number().int().min(0).max(2e6),
  truncated: z28.boolean(),
  generatedFrames: z28.literal(0)
}).strict().superRefine((value, context) => {
  const fail = (message) => context.addIssue({ code: "custom", message });
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
var referenceFetchReceiptSchema = z28.object({
  schemaVersion: z28.literal(1),
  candidateId: id6,
  source: referenceSourcePinSchema,
  originalUrl: publicHttps,
  pageUrl: publicHttps,
  fetchedAt: z28.string().datetime(),
  sha256: sha2562,
  sha1: z28.string().regex(/^[a-f0-9]{40}$/),
  bytes: z28.number().int().min(1).max(8388608),
  mime: z28.enum(["image/jpeg", "image/png"]),
  license: referenceLicenseSchema,
  creator: text3,
  rightsReview: z28.literal("required"),
  speciesReview: z28.literal("required"),
  poseReview: z28.literal("required"),
  generationApproved: z28.literal(false)
}).strict();

// birdsong-yard-sprites/src/lib/server/reference-discovery/service.ts
import { z as z30 } from "zod";

// birdsong-yard-sprites/src/lib/server/reference-discovery/registry.ts
import { z as z29 } from "zod";
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
var trustedTaxonomyAliasesSchema = z29.array(
  z29.object({
    speciesId: z29.string().min(1),
    scientificName: z29.string().min(1),
    aliases: z29.array(z29.string().regex(/^[A-Z][a-z]{1,39} [a-z]{2,40}(?: [a-z]{2,40})?$/)).max(4)
  }).strict()
).max(128);

// birdsong-yard-sprites/src/lib/server/reference-discovery/service.ts
var pageSchema = z30.object({
  candidates: z30.array(discoveredReferenceSchema).max(DISCOVERY_LIMITS.pageSize),
  nextCursor: z30.string().min(1).max(2048).nullable()
}).strict();

// birdsong-yard-sprites/src/lib/server/asset-pipeline/definitions.ts
import "zod";

// birdsong-yard-sprites/src/lib/assets/source-review.ts
function assetSourceIssues(source) {
  const issues = [];
  if (new Set(source.references.map((reference) => reference.id)).size !== source.references.length)
    issues.push("Reference identifiers must be unique");
  if (source.references.some((reference) => reference.speciesId !== source.speciesId))
    issues.push("Every reference must identify the intended species");
  if (!source.license.derivativesAllowed || !source.license.redistributionAllowed)
    issues.push("Source permissions do not permit reusable animation");
  if (source.source === "deterministic_fixture") {
    if (source.license.status !== "development-only" || source.fidelityReview !== null || source.references.some((reference) => reference.role !== "technical-fixture"))
      issues.push("Technical fixtures cannot claim cleared rights or species fidelity");
  } else if (source.license.status !== "cleared" || !source.license.evidenceId || !source.fidelityReview || source.references.some((reference) => reference.role !== "species-reference")) {
    issues.push("Non-fixture intake needs rights evidence and a recorded species review");
  }
  return issues;
}

// birdsong-yard-sprites/src/lib/server/asset-pipeline/package.ts
function invalid(reason) {
  throw new PermanentStageError(reason);
}
function validateAssetSource(input) {
  const parsed = assetSourceSchema.safeParse(input);
  if (!parsed.success) return invalid("Invalid asset source contract");
  const source = parsed.data;
  const issue = assetSourceIssues(source)[0];
  if (issue) invalid(issue);
  return source;
}
function component(bytes2, offset) {
  const value = bytes2[offset];
  if (value === void 0) return invalid("Truncated RGBA frame");
  return value;
}
function pixel(bytes2, offset) {
  const alpha = component(bytes2, offset + 3);
  if (alpha === 0) return null;
  if (alpha !== 255) return invalid("Only transparent or opaque pixels are supported");
  return component(bytes2, offset) << 16 | component(bytes2, offset + 1) << 8 | component(bytes2, offset + 2);
}
function normalizeDecodedPixels(pixels) {
  const { width, height } = pixels.canvas;
  if (width * height * pixels.frames.length > 65536)
    invalid("Decoded animation exceeds pixel budget");
  if (width % pixels.logicalPixelSize || height % pixels.logicalPixelSize)
    invalid("Canvas must align to the declared logical pixel grid");
  const colors = /* @__PURE__ */ new Set();
  let rectangles = 0;
  const frames = pixels.frames.map(({ rgba }) => {
    if (rgba.length !== width * height * 4)
      invalid("RGBA length must exactly match canvas dimensions");
    for (let y = 0; y < height; y++)
      for (let x = 0; x < width; x++) {
        const color = pixel(rgba, (y * width + x) * 4);
        const gridX = x - x % pixels.logicalPixelSize, gridY = y - y % pixels.logicalPixelSize;
        if (color !== pixel(rgba, (gridY * width + gridX) * 4))
          invalid("Pixels disagree within logical grid cell");
        if (color !== null) colors.add(color);
        if (colors.size > pixels.paletteLimit) invalid("Animation exceeds palette budget");
      }
    const result2 = [];
    let previous = /* @__PURE__ */ new Map();
    for (let y = 0; y < height; y++) {
      const current = /* @__PURE__ */ new Map();
      for (let x = 0; x < width; ) {
        const color = pixel(rgba, (y * width + x) * 4), start2 = x++;
        if (color === null) continue;
        while (x < width && pixel(rgba, (y * width + x) * 4) === color) x++;
        const key2 = `${start2}/${x - start2}/${color}`, above = previous.get(key2);
        if (above) {
          above.height++;
          current.set(key2, above);
        } else {
          const rect = { x: start2, y, width: x - start2, height: 1, color };
          result2.push(rect);
          current.set(key2, rect);
          rectangles++;
          if (result2.length > 4096 || rectangles > 16384)
            invalid("Normalized rectangle budget exceeded");
        }
      }
      previous = current;
    }
    if (!result2.length) invalid("An animation frame cannot be entirely transparent");
    return result2;
  });
  return frames;
}

// birdsong-yard-sprites/src/lib/server/asset-pipeline/animation-planning.ts
function compileAnimationPlanV2(value, recipes) {
  const parsed = animationPlanningInputV2Schema.safeParse(value);
  if (!parsed.success) throw new PermanentStageError("Invalid animation planning v2 input");
  const input = canonicalAnimationPlanningInputV2(parsed.data);
  let specification;
  try {
    specification = resolveAnimationSpecification(input, recipes);
  } catch {
    throw new PermanentStageError("Invalid animation recipe, version or overrides");
  }
  return compileResolvedPlan(input, specification);
}
function compileResolvedPlan(input, specification) {
  const perchedSleep = specification.clips.find((clip3) => clip3.action === "sleeping")?.frames.every((frame) => frame.contactRequirements.includes("perch"));
  const blockers = [
    "reference-bytes-unverified",
    "species-fidelity-unreviewed",
    "model-unconfigured",
    "art-direction-unapproved",
    "output-review-required"
  ];
  if (!input.references.length) blockers.unshift("references-missing");
  if (input.references.some((reference) => reference.fixture))
    blockers.push("reference-is-fixture");
  if (input.references.some(
    ({ rights }) => rights.status !== "approved" || !rights.review || !rights.referenceUseAllowed || !rights.derivativesAllowed || !rights.redistributionAllowed || rights.restrictions.length > 0
  ))
    blockers.push("reference-rights-unreviewed");
  if (input.references.some(({ rights }) => rights.generationPermission !== "allowed"))
    blockers.push("generation-permission-unreviewed");
  const negativePrompt = "No background, baked scenery, water splashes, text, labels, watermark, gradients, antialiasing, soft alpha, invented markings, hybrid species, changing anatomy, camera motion or changing scale. Do not treat any fixture or this proposal as a reviewed species reference.";
  const prompts = specification.clips.map((clip3) => {
    const uniformTiming = clip3.frames.every(
      (frame) => frame.durationTicks === clip3.frames[0]?.durationTicks
    );
    const timing = uniformTiming ? `each ${clip3.frames[0]?.durationTicks ?? 1} ticks` : `per-frame durations [${clip3.frames.map((frame) => frame.durationTicks).join(", ")}] ticks`;
    const defaultPivots = clip3.frames.every(
      (frame) => frame.proposedPivot.x === 16 && frame.proposedPivot.y === 28
    );
    const prompt = [
      `PLANNING TEMPLATE ONLY; no image model has run. Proposed ${clip3.action} clip for ${input.scientificName} (${input.taxonomy.speciesId}, ${input.taxonomy.catalog}@${input.taxonomy.version}).`,
      "Use only separately authorized and biologically reviewed actual-species references. Match reviewed anatomy, plumage, proportions and silhouette across all frames; do not infer sex, age or seasonal plumage from a common name.",
      `Art-direction proposal awaiting approval: ${specification.canvas.width}x${specification.canvas.height} pixel canvas, logical pixel size ${specification.logicalPixelSize}, at most ${specification.paletteLimit} opaque colors, straight RGBA with alpha exactly 0 or 255, transparent background. This capacity proposal does not establish sufficient artistic detail.`,
      `Direction: ${clip3.direction}. Keep one stable canvas and scale; review left/right mirroring for asymmetric markings. Propose ${clip3.frames.length} unique frames, ${timing} at ${specification.ticksPerSecond} simulation ticks per second. Timing is authored proposal, not measured bird behavior.`,
      clip3.purpose,
      defaultPivots ? "Proposed pivot is (16,28), subject to reviewed support geometry. Foot/ground/perch contacts must be explicitly annotated per pose and remain compatible with the existing renderer. No contact or IK solver is implied." : "Proposed pivots vary by frame as specified in the frame prompts, subject to reviewed support geometry. Foot/ground/perch contacts must be explicitly annotated per pose and remain compatible with the existing renderer. No contact or IK solver is implied.",
      `Entry and exit: ${clip3.entry}; ${clip3.exit}. ${clip3.loop ? "Review the last-to-first pixel, pivot and contact seam before approving this loop." : "Do not loop; review the terminal held pose and the later return to idle. Routine scheduling does not await clip completion."}`,
      "Keep bird art separate from placeable objects, weather and foreground effects. Retain source/model/license hashes and review provenance outside this prompt. Run existing bounded pixel/manifest validation and independent human review before any selection or reusable release."
    ].join("\n");
    return {
      action: clip3.action,
      templateVersion: specification.templateVersion,
      prompt,
      negativePrompt,
      frames: clip3.frames.map((frame, index) => ({
        frame: frame.frame,
        prompt: [
          prompt,
          `Frame ${index + 1}/${clip3.frames.length}, inventory index ${frame.frame}: ${frame.phase}. Hold for ${frame.durationTicks} ticks.`,
          `Proposed pivot (${frame.proposedPivot.x},${frame.proposedPivot.y}); required review contacts: ${frame.contactRequirements.join(", ") || (input.schemaVersion === 1 ? "none during this airborne phase" : "none specified; support state requires review")}.`,
          `Previous phase: ${clip3.frames[index - 1]?.phase ?? (clip3.loop ? clip3.frames.at(-1)?.phase : "reviewed idle entry")}. Next phase: ${clip3.frames[index + 1]?.phase ?? (clip3.loop ? clip3.frames[0]?.phase : "terminal hold; reviewed idle exit")}. Preserve anatomical identity and canvas registration across neighboring frames.`
        ].join("\n")
      }))
    };
  });
  return animationProductionPlanSchema.parse({
    schemaVersion: 1,
    format: "animation-production-plan",
    execution: "planning-only",
    model: "unconfigured",
    generatedFrames: 0,
    taxonFidelityReviewed: false,
    taxonomy: input.taxonomy,
    scientificName: input.scientificName,
    inputSha256: digest(input),
    specificationSha256: digest(specification),
    specification,
    references: input.references.map((reference) => ({
      id: reference.id,
      originalSha256: reference.original.sha256,
      decodedSha256: reference.decoded.sha256,
      status: "declared-not-byte-verified"
    })),
    blockers,
    prompts,
    limitations: [
      "This immutable technical plan contains no generated frames and cannot be selected as bird artwork. Approving a plan is not approval of references, rights, biology or rendered output.",
      `The ${specification.canvas.width}x${specification.canvas.height} canvas, ${specification.totalFrames} frames, phase descriptions, pivots, contacts and timing are proposed engineering budgets. They are not approved concept pixels, demonstrated artistic detail or validated biological motion.`,
      "Scientific-name matching checks the pinned application catalog only. Reference declarations and hashes have not been checked against original bytes or authenticated external taxonomies by this planner.",
      "Only right-facing-mirrorable clips are supported by the current render contract. Front/back/oblique sets, independent takeoff/landing clips and authored cross-clip transition frames require future contracts and artwork.",
      perchedSleep ? "Contact labels describe proposed support geometry, not elevation or biological truth. Ground contact can denote an elevated feeder, bath or nest surface. Sleep supports ground, perch and roost; the single proposed perched sleep clip cannot cover every support without further review." : "Contact labels describe proposed support geometry, not elevation or biological truth. Ground contact can denote an elevated feeder, bath or nest surface. Sleep supports ground, perch and roost; resolved sleep contacts must be reviewed separately for each support before reuse.",
      "Arrival, scatter, return and hop/flight currently use moving. Weather, lighting, clouds, precipitation, fog, wind and scene objects remain separate procedural layers, not additional bird-generated clips.",
      input.schemaVersion === 1 ? "Provider adapters, approved actual-species references, scientific review, production rights, model licenses and final output review are required before real generation or release. No provider is invoked or configured here." : "Provider adapters, approved actual-species references, scientific review, production rights, model licenses and final output review are required before real generation or release. No image-generation provider is invoked or configured here. Separate reference discovery can query public metadata; candidate metadata is not an approved reference."
    ]
  });
}

// birdsong-yard-sprites/src/lib/server/asset-pipeline/animation-planning-v2.ts
function animationReferenceRequest(value) {
  const input = canonicalAnimationPlanningInputV2(value);
  return canonicalReferenceDiscoveryRequest({
    ...defaultReferenceDiscoveryRequest(input.taxonomy.speciesId),
    suppliedReferences: input.references
  });
}

// birdsong-yard-sprites/src/lib/server/asset-pipeline/reference-generation.ts
import { z as z33 } from "zod";

// birdsong-yard-sprites/src/lib/assets/reference-admission.ts
import { z as z32 } from "zod";
var id7 = z32.string().regex(/^[a-zA-Z0-9][a-zA-Z0-9._:@-]{0,159}$/);
var sha2563 = z32.string().regex(/^[a-f0-9]{64}$/);
var text4 = z32.string().trim().min(1).max(2e3);
var time3 = z32.string().datetime();
var licenseUrl = z32.string().max(2048).refine((value) => {
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
var referenceImageIdentitySchema = z32.object({
  schemaVersion: z32.literal(1),
  id: z32.string().uuid(),
  original: z32.object({
    sha256: sha2563,
    bytes: z32.number().int().min(1).max(REFERENCE_IMAGE_LIMITS.originalBytes),
    mime: z32.enum(["image/png", "image/jpeg"])
  }).strict(),
  canonical: z32.object({
    sha256: sha2563,
    bytes: z32.number().int().min(1).max(REFERENCE_IMAGE_LIMITS.canonicalBytes),
    width: z32.number().int().min(1).max(REFERENCE_IMAGE_LIMITS.side),
    height: z32.number().int().min(1).max(REFERENCE_IMAGE_LIMITS.side),
    rgbaSha256: sha2563
  }).strict(),
  decoder: z32.object({ id: z32.literal("sharp"), version: id7, libvips: id7 }).strict(),
  normalization: z32.literal("chirp-reference-straight-srgb8-oriented-hidden-rgb-zero-v1")
}).strict().superRefine((value, context) => {
  if (value.canonical.width * value.canonical.height > REFERENCE_IMAGE_LIMITS.pixels)
    context.addIssue({
      code: "custom",
      message: "Decoded reference allocation exceeds its limit."
    });
});
var referenceAdmissionSourceSchema = z32.discriminatedUnion("kind", [
  z32.object({ kind: z32.literal("owner-upload") }).strict(),
  z32.object({
    kind: z32.literal("retained-discovery"),
    discoveryPin: animationPinSchema,
    candidateId: id7,
    candidate: discoveredReferenceSchema,
    receipt: referenceFetchReceiptSchema
  }).strict()
]);
var referenceAdmissionPinSchema = z32.object({ referenceId: z32.string().uuid(), contentDigest: sha2563, reviewDigest: sha2563 }).strict();
var reviewBase = {
  requestId: z32.string().uuid(),
  decision: z32.enum(["approved", "rejected"]),
  evidenceId: id7
};
var rightsCommand = z32.object({
  ...reviewBase,
  kind: z32.literal("rights"),
  generationAllowed: z32.boolean(),
  derivativesAllowed: z32.boolean(),
  redistributionAllowed: z32.boolean(),
  licenseId: id7,
  licenseVersion: id7.nullable(),
  licenseUrl: licenseUrl.nullable(),
  creator: text4,
  attribution: text4
}).strict();
var speciesCommand = z32.object({ ...reviewBase, kind: z32.literal("species"), speciesId: id7 }).strict();
var referenceViewpoints = [
  "left",
  "right",
  "front",
  "back",
  "three-quarter",
  "other"
];
var poseCommand = z32.object({
  ...reviewBase,
  kind: z32.literal("pose"),
  poseLabel: z32.string().trim().min(1).max(160),
  permittedActions: z32.array(z32.enum(animationStates)).min(1).max(animationStates.length),
  viewpoints: z32.array(z32.enum(referenceViewpoints)).min(1).max(referenceViewpoints.length)
}).strict();
var reviewCommand = z32.discriminatedUnion("kind", [rightsCommand, speciesCommand, poseCommand]);
function validateReview(value, context) {
  const fail = (message) => context.addIssue({ code: "custom", message });
  if (value.kind === "rights" && value.decision === "approved" && (!value.generationAllowed || !value.derivativesAllowed || !value.redistributionAllowed || ["unknown", "pending", "unreviewed", "denied"].includes(value.licenseId.toLowerCase())))
    fail("Approved rights require an identified license and all intended-use permissions.");
  if (value.kind === "species" && !catalogEntry(value.speciesId))
    fail("Species review requires a supported catalog identity.");
  if (value.kind === "pose" && (new Set(value.permittedActions).size !== value.permittedActions.length || new Set(value.viewpoints).size !== value.viewpoints.length))
    fail("Pose review action and viewpoint scopes must be distinct.");
}
var referenceReviewCommandSchema = reviewCommand.superRefine(validateReview);
var reviewEvent = { reviewerId: id7, reviewedAt: time3 };
var rightsEvent = rightsCommand.extend(reviewEvent).strict();
var speciesEvent = speciesCommand.extend(reviewEvent).strict();
var poseEvent = poseCommand.extend(reviewEvent).strict();
var referenceReviewSchema = z32.discriminatedUnion("kind", [rightsEvent, speciesEvent, poseEvent]).superRefine(validateReview);
var referenceRevokeCommandSchema = z32.object({ requestId: z32.string().uuid(), reason: text4 }).strict();
var referenceRevocationSchema = referenceRevokeCommandSchema.extend({ reviewerId: id7, revokedAt: time3 }).strict();
var referenceAdmissionRecordSchema = z32.object({
  identity: referenceImageIdentitySchema,
  contentDigest: sha2563,
  reviewDigest: sha2563,
  source: referenceAdmissionSourceSchema,
  createdAt: time3,
  reviews: z32.object({
    rights: rightsEvent.superRefine(validateReview).nullable(),
    species: speciesEvent.superRefine(validateReview).nullable(),
    pose: poseEvent.superRefine(validateReview).nullable()
  }).strict(),
  revocation: referenceRevocationSchema.nullable()
}).strict().superRefine((value, context) => {
  const fail = (message) => context.addIssue({ code: "custom", message });
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
var referenceAdmissionListSchema = z32.object({ files: z32.array(referenceAdmissionRecordSchema).max(16) }).strict();
var referenceAdmissionResponseSchema = z32.object({ file: referenceAdmissionRecordSchema }).strict();
var referenceGenerationProviderPinSchema = z32.object({ id: id7, version: z32.number().int().min(1).max(100) }).strict();
var referenceGenerationInputSchema = z32.object({
  schemaVersion: z32.literal(1),
  referencePin: referenceAdmissionPinSchema,
  planningInput: animationPlanningInputV2Schema,
  provider: referenceGenerationProviderPinSchema
}).strict().superRefine((value, context) => {
  if (value.planningInput.references.length)
    context.addIssue({
      code: "custom",
      message: "Only the admitted reference pin can supply reference bytes."
    });
});
var referenceGenerationCommandSchema = z32.discriminatedUnion("action", [
  z32.object({
    action: z32.literal("queue"),
    requestId: z32.string().uuid(),
    input: referenceGenerationInputSchema
  }).strict(),
  z32.object({ action: z32.literal("advance"), jobId: id7 }).strict(),
  z32.object({ action: z32.literal("cancel"), jobId: id7 }).strict()
]);
var referenceAcquisitionCommandSchema = z32.object({
  requestId: z32.string().uuid(),
  jobId: id7,
  artifactId: id7,
  candidateId: id7
}).strict();
var diagnosticPixels = pixelAnimationSourceV2Schema.extend({
  canvas: pixelAnimationSourceV2Schema.shape.canvas.extend({
    width: z32.number().int().min(1).max(8),
    height: z32.number().int().min(1).max(8)
  }).strict(),
  logicalPixelSize: z32.literal(1),
  frames: z32.array(
    pixelAnimationSourceV2Schema.shape.frames.element.extend({
      rgba: pixelAnimationSourceV2Schema.shape.frames.element.shape.rgba.max(8 * 8 * 4)
    }).strict()
  ).length(1)
}).strict().superRefine((value, context) => {
  const rgba = value.frames[0]?.rgba;
  if (!rgba || rgba.length !== value.canvas.width * value.canvas.height * 4)
    context.addIssue({
      code: "custom",
      message: "Diagnostic RGBA allocation must exactly match its canvas."
    });
  if (rgba?.some((channel2, index) => index % 4 === 3 && channel2 !== 0 && channel2 !== 255))
    context.addIssue({ code: "custom", message: "Diagnostic fixtures require binary alpha." });
  if (rgba?.some(
    (channel2, index) => index % 4 !== 3 && rgba[index - index % 4 + 3] === 0 && channel2 !== 0
  ))
    context.addIssue({
      code: "custom",
      message: "Transparent diagnostic pixels require zero RGB."
    });
});
var referenceGenerationCandidateSchema = z32.object({
  schemaVersion: z32.literal(1),
  format: z32.literal("reference-generation-candidate"),
  renderable: z32.literal(false),
  fixture: z32.literal(true),
  generated: z32.literal(false),
  purpose: z32.literal("local-diagnostic-not-species-art"),
  provider: referenceGenerationProviderPinSchema,
  inputSha256: sha2563,
  planSha256: sha2563,
  referencePin: referenceAdmissionPinSchema,
  reference: z32.object({ originalSha256: sha2563, canonicalSha256: sha2563, rgbaSha256: sha2563 }).strict(),
  pixels: diagnosticPixels,
  outputSha256: sha2563,
  execution: z32.object({
    kind: z32.literal("local-fake"),
    externalCalls: z32.literal(0),
    modelCalls: z32.literal(0),
    scientificFidelityApproved: z32.literal(false)
  }).strict(),
  limitations: z32.array(text4).min(1).max(16)
}).strict();

// birdsong-yard-sprites/src/lib/server/asset-pipeline/reference-generation.ts
function canonicalReferenceGenerationInput(value) {
  const parsed = referenceGenerationInputSchema.safeParse(value);
  if (!parsed.success) throw new PermanentStageError("Invalid reference generation input");
  return {
    ...parsed.data,
    planningInput: canonicalAnimationPlanningInputV2(parsed.data.planningInput)
  };
}
function diagnosticPixels2(value) {
  const envelope = z33.object({ pixels: z33.unknown() }).strict().safeParse(value);
  if (!envelope.success)
    throw new PermanentStageError("Provider output may contain only diagnostic pixels");
  const budget = z33.object({
    canvas: z33.object({
      width: z33.number().int().min(1).max(8),
      height: z33.number().int().min(1).max(8)
    }),
    frames: z33.unknown()
  }).safeParse(envelope.data.pixels);
  if (!budget.success)
    throw new PermanentStageError("Diagnostic output exceeds the single-frame 8x8 budget");
  if (!Array.isArray(budget.data.frames) || budget.data.frames.length !== 1)
    throw new PermanentStageError("Diagnostic output exceeds the single-frame 8x8 budget");
  const frame = z33.object({ rgba: z33.unknown() }).safeParse(budget.data.frames[0]);
  const rgba = frame.success ? frame.data.rgba : void 0;
  if (!Array.isArray(rgba) || rgba.length !== budget.data.canvas.width * budget.data.canvas.height * 4)
    throw new PermanentStageError("Diagnostic channel length does not match its canvas");
  const parsed = pixelAnimationSourceV2Schema.safeParse(envelope.data.pixels);
  if (!parsed.success) throw new PermanentStageError("Invalid diagnostic pixel output");
  normalizeDecodedPixels(parsed.data);
  for (let index = 0; index < rgba.length; index += 4)
    if (rgba[index + 3] === 0 && (rgba[index] !== 0 || rgba[index + 1] !== 0 || rgba[index + 2] !== 0))
      throw new PermanentStageError("Diagnostic transparent pixels must have canonical zero RGB");
  return parsed.data;
}
function validateReferenceGenerationCandidate(value, inputValue) {
  const input = canonicalReferenceGenerationInput(inputValue);
  const parsed = referenceGenerationCandidateSchema.safeParse(value);
  if (!parsed.success) throw new PermanentStageError("Invalid reference generation candidate");
  const candidate = parsed.data;
  const pixels = diagnosticPixels2({ pixels: candidate.pixels });
  if (candidate.inputSha256 !== digest(input) || candidate.planSha256 !== digest(compileAnimationPlanV2(input.planningInput)) || digest(candidate.referencePin) !== digest(input.referencePin) || digest(candidate.provider) !== digest(input.provider) || candidate.outputSha256 !== digest(pixels))
    throw new PermanentStageError(
      "Diagnostic candidate differs from its immutable generation input or output"
    );
  return candidate;
}

// birdsong-yard-sprites/src/lib/assets/png-file-contracts.ts
import { z as z34 } from "zod";
var pngFileReviewCommandSchema = z34.object({
  requestId: z34.string().uuid(),
  decision: z34.enum(["approved", "rejected"]),
  source: assetSourceSchema
}).strict();
var pngFileReviewSchema = pngFileReviewCommandSchema.extend({
  reviewedAt: z34.string().datetime()
}).strict();
var pngFileRecordSchema = z34.object({
  file: pngFileIdentitySchema,
  createdAt: z34.string().datetime(),
  review: pngFileReviewSchema.nullable()
}).strict();
var pngFileListSchema = z34.object({ files: z34.array(pngFileRecordSchema).max(64), page: pageInfoSchema.optional() }).strict();
var pngFilePageSchema = pngFileListSchema.extend({ files: z34.array(pngFileRecordSchema).max(WORKBENCH_PAGE_MAX), page: pageInfoSchema }).strict().superRefine((value, context) => {
  if (value.files.length > value.page.limit || new Set(value.files.map((file) => file.file.id)).size !== value.files.length)
    context.addIssue({
      code: "custom",
      message: "File page exceeds its limit or repeats a file."
    });
});
var pngFileReceiptSchema = z34.object({ file: pngFileRecordSchema }).strict();
var pngFilePackageCommandSchema = z34.object({
  requestId: z34.string().uuid(),
  layout: pngFrameLayoutSchema,
  logicalPixelSize: z34.number().int().min(1).max(16),
  paletteLimit: z34.number().int().min(1).max(64),
  clips: animationClipsV3Schema,
  conditioning: animationConditioningSchema
}).strict();
var pngFilePackageCommandV2Schema = pngFilePackageCommandSchema.extend({
  schemaVersion: z34.literal(2),
  presentation: assetPresentationSchema
}).strict();
var supportedPngFilePackageCommandSchema = z34.union([
  pngFilePackageCommandSchema,
  pngFilePackageCommandV2Schema
]);
var pngWorkshopPlanSchema = z34.object({
  source: assetSourceSchema,
  plan: pngFilePackageCommandSchema.omit({ requestId: true })
}).strict();
var pngWorkshopPlanV2Schema = pngWorkshopPlanSchema.extend({
  schemaVersion: z34.literal(2),
  plan: pngFilePackageCommandV2Schema.omit({ requestId: true })
}).strict();
var supportedPngWorkshopPlanSchema = z34.union([
  pngWorkshopPlanSchema,
  pngWorkshopPlanV2Schema
]);

// birdsong-yard-sprites/src/lib/server/image-files/files.ts
import { z as z35 } from "zod";
var MAX_IMAGE_REVIEW_CHARS = 2e4;

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
var normalize = (sql) => sql.replace(/\s+/g, " ").replace(/\s*([(),;])\s*/g, "$1").trim().replace(/;$/, "").toLowerCase();
function assertAssetLifecycleCompatibility(db2) {
  let found = 0;
  for (const [name, type, sql] of ASSET_LIFECYCLE_SCHEMA) {
    const row = db2.prepare("SELECT sql FROM sqlite_master WHERE name=? AND type=?").get(name, type);
    if (!row) continue;
    found++;
    if (typeof row.sql !== "string" || normalize(row.sql) !== normalize(sql))
      throw new Error("Unsupported asset lifecycle schema.");
  }
  if (!found) return false;
  if (found !== ASSET_LIFECYCLE_SCHEMA.length)
    throw new Error("Incomplete asset lifecycle schema.");
  const versions = db2.prepare("SELECT version FROM asset_lifecycle_migrations LIMIT 2").all();
  if (versions.length !== 1 || versions[0]?.version !== 1)
    throw new Error("Unsupported asset lifecycle version.");
  const triggers = db2.prepare(
    "SELECT name FROM sqlite_master WHERE type='trigger' AND tbl_name IN ('asset_archives','asset_lifecycle_receipts','asset_lifecycle_migrations')"
  ).all();
  if (triggers.length !== 1) throw new Error("Unsupported asset lifecycle trigger.");
  return true;
}
function archiveState(db2, owner, target2) {
  pipelineIdentifierSchema.parse(owner);
  assetLifecycleTargetSchema.parse(target2);
  const row = db2.prepare("SELECT * FROM asset_archives WHERE owner_id=? AND kind=? AND target_id=?").get(owner, target2.kind, target2.id);
  if (!row)
    return assetArchiveStateSchema.parse({ target: target2, revision: 0, archived: false, changedAt: null });
  if (row.archived !== 0 && row.archived !== 1) throw new Error("Invalid archive state.");
  return assetArchiveStateSchema.parse({
    target: target2,
    revision: row.revision,
    archived: row.archived === 1,
    changedAt: row.changed_at
  });
}
function readLifecycleReceipt(value) {
  if (typeof value !== "string" || value.length > 4096)
    throw new Error("Invalid lifecycle receipt.");
  const json = JSON.parse(value);
  const receipt = assetLifecycleReceiptSchema.parse(json);
  if (digest(receipt.command) !== receipt.commandDigest || receipt.command.action === "unpin" !== (receipt.previousArtworkId !== null) || receipt.command.action === "unpin" && receipt.previousArtworkId !== receipt.command.expectedArtworkId)
    throw new Error("Invalid lifecycle receipt identity.");
  return receipt;
}

// birdsong-yard-sprites/src/lib/server/asset-pipeline/package-v2.ts
import { createHash as createHash3 } from "node:crypto";
import { z as z36 } from "zod";
function supportedPackagingInputV2(value) {
  const input = supportedPosePackagingInputSchema.safeParse(value);
  if (!input.success) throw new PermanentStageError("Invalid versioned pose asset packaging input");
  if (input.data.strategy.kind !== "decoded-rgba")
    throw new PermanentStageError(
      "This local generation strategy is not configured; submit decoded RGBA frames."
    );
  validateAssetSource(input.data.source);
  if (input.data.shape) {
    const frames = normalizeDecodedPixels(input.data.pixels);
    const issues = shapeReviewIssues(
      {
        speciesId: input.data.source.speciesId,
        canvas: input.data.pixels.canvas,
        frames,
        clips: input.data.clips
      },
      input.data.shape
    );
    if (issues.length)
      throw new PermanentStageError("Shape annotations do not match retained pixels and poses");
  }
  return input.data;
}
function sourceArtifactV2(value) {
  const input = supportedPackagingInputV2(value);
  normalizeDecodedPixels(input.pixels);
  return supportedRgbaSourceArtifactSchema.parse({
    schemaVersion: input.schemaVersion === 3 ? 2 : 1,
    format: "private-rgba-source",
    lifecycle: "retained-until-owner-deletion",
    inputDigest: digest(input),
    input,
    blobs: input.pixels.frames.map((frame, index) => ({
      frame: index,
      encoding: "rgba8",
      bytes: frame.rgba.length,
      sha256: createHash3("sha256").update(Uint8Array.from(frame.rgba)).digest("hex")
    }))
  });
}
function validateSourceArtifactV2(value) {
  const source = supportedRgbaSourceArtifactSchema.safeParse(value);
  if (!source.success) throw new PermanentStageError("Invalid source RGBA artifact");
  const actual = sourceArtifactV2(source.data.input);
  if (source.data.inputDigest !== actual.inputDigest || source.data.blobs.some((blob, index) => blob.sha256 !== actual.blobs[index]?.sha256))
    throw new PermanentStageError("Source RGBA content hashes do not match retained bytes");
  return source.data;
}
function packageAssetV2(value, sourceArtifact) {
  const input = supportedPackagingInputV2(value);
  const frames = normalizeDecodedPixels(input.pixels);
  if (Object.values(input.clips).some(
    (clip3) => clip3?.poses.some((pose) => pose.frame >= frames.length)
  ))
    throw new PermanentStageError("Clip references an unavailable frame");
  const source = input.source;
  const manifest = z36.union([speciesManifestV3Schema, speciesManifestV4Schema]).safeParse({
    schemaVersion: input.schemaVersion === 3 ? 4 : 3,
    ...input.schemaVersion === 3 ? { presentation: input.presentation } : {},
    speciesId: source.speciesId,
    representation: source.representation,
    fixture: source.source === "deterministic_fixture",
    taxonFidelityReviewed: source.fidelityReview !== null,
    format: "pixel-rects",
    canvas: input.pixels.canvas,
    frames,
    clips: input.clips,
    conditioning: input.conditioning,
    sourceArtifact,
    ...input.shape ? { shape: input.shape } : {},
    provenance: {
      source: source.source,
      creator: source.creator,
      sourceVersion: source.sourceVersion,
      references: source.references.map((reference) => reference.id),
      license: source.license.id,
      usage: source.source === "deterministic_fixture" ? "development-only" : "cleared",
      attribution: source.license.attribution
    },
    normalization: {
      algorithm: "lossless-rgba-rects-v2",
      alpha: "binary",
      logicalPixelSize: input.pixels.logicalPixelSize,
      palette: [...new Set(frames.flat().map((rect) => rect.color))].sort((a, b) => a - b),
      loopEdges: measureLoopEdges(input.pixels.canvas, frames, input.clips)
    }
  });
  if (!manifest.success)
    throw new PermanentStageError("Versioned manifest, graph or pose validation failed");
  return manifest.data;
}
function sourceProvenanceV2(input) {
  return {
    source: input.source.source,
    providerId: input.source.creator,
    providerVersion: input.source.sourceVersion,
    references: input.source.references.map((reference) => reference.id),
    fixture: input.source.source === "deterministic_fixture",
    license: input.source.license.id
  };
}

// birdsong-yard-sprites/src/lib/server/assets/resolve.ts
function resolutionContext(reserveCandidate = false) {
  return {
    visits: reserveCandidate ? 1 : 0,
    reservedDepth: reserveCandidate ? 1 : 0,
    ancestry: /* @__PURE__ */ new Set(),
    checked: /* @__PURE__ */ new Map()
  };
}
function reviewedManifest(jobs2, owner, jobId, artifactId) {
  return reviewedManifestInContext(jobs2, owner, jobId, artifactId, resolutionContext());
}
function reviewedManifestInContext(jobs2, owner, jobId, artifactId, context) {
  if (++context.visits > 64)
    throw new YardError("INVALID", "Reviewed source dependency traversal exceeds its budget.");
  if (context.ancestry.has(artifactId) || context.ancestry.size + context.reservedDepth >= 32)
    throw new YardError("INVALID", "Reviewed source dependency chain is invalid.");
  const key2 = `${jobId}/${artifactId}`;
  const cached = context.checked.get(key2);
  if (cached) return cached;
  context.ancestry.add(artifactId);
  const artifact = jobs2.artifacts(owner, jobId).find((entry) => entry.id === artifactId);
  if (!artifact || artifact.reviewStatus !== "approved" || artifact.kind !== "animation-manifest")
    throw new YardError(
      "INVALID",
      "Animation requires an approved artifact in this owner\u2019s workshop."
    );
  const manifest = speciesManifestSchema.parse(artifact.payload);
  if (digest(artifact.payload) !== artifact.contentDigest)
    throw new YardError("INVALID", "Animation content digest mismatch.");
  const source = manifest.provenance, recorded = artifact.provenance;
  if (manifest.fixture !== recorded.fixture || source.source !== recorded.source || source.creator !== recorded.providerId || source.sourceVersion !== recorded.providerVersion || source.license !== recorded.license || JSON.stringify(source.references) !== JSON.stringify(recorded.references))
    throw new YardError("INVALID", "Animation provenance mismatch.");
  const pin = {
    jobId,
    artifactId,
    version: artifact.version,
    contentDigest: artifact.contentDigest
  };
  if (manifest.schemaVersion !== 2) {
    const source2 = reviewedSourceArtifactV2(jobs2, owner, manifest.sourceArtifact);
    if (manifest.sourceArtifact.jobId !== jobId || source2.input.source.speciesId !== manifest.speciesId)
      throw new YardError(
        "INVALID",
        "Source artifact does not match this animation job and species."
      );
    validateReferencesInContext(jobs2, owner, source2.input, context);
    if (digest(packageAssetV2(source2.input, manifest.sourceArtifact)) !== pin.contentDigest)
      throw new YardError(
        "INVALID",
        "Reviewed animation does not match its retained source frames."
      );
  }
  context.ancestry.delete(artifactId);
  const approved = { manifest, pin };
  context.checked.set(key2, approved);
  return approved;
}
function reviewedSourceArtifactV2(jobs2, owner, pin) {
  const artifact = jobs2.artifacts(owner, pin.jobId).find((entry) => entry.id === pin.artifactId);
  if (!artifact || artifact.kind !== "rgba-source-manifest" || artifact.reviewStatus !== "approved" || artifact.version !== pin.version || artifact.contentDigest !== pin.contentDigest)
    throw new YardError(
      "INVALID",
      "Source frames require an exact approved artifact in this owner\u2019s workshop."
    );
  const source = validateSourceArtifactV2(artifact.payload);
  if (source.input.fileOrigin) jobs2.validateSourceFile(owner, source.input);
  if (digest(artifact.provenance) !== digest(sourceProvenanceV2(source.input)) || digest(artifact.payload) !== pin.contentDigest || source.inputDigest !== jobs2.get(owner, pin.jobId).inputDigest)
    throw new YardError("INVALID", "Source frames do not match their original private input.");
  return source;
}
function validateReferencesInContext(jobs2, owner, input, context) {
  if (input.fileOrigin) jobs2.validateSourceFile(owner, input);
  if (input.source.source !== "deterministic_fixture" && !input.conditioning.references.some((reference) => reference.roles.includes("species")))
    throw new YardError("INVALID", "Production source requires an approved species reference.");
  for (const reference of input.conditioning.references) {
    const approved = reviewedManifestInContext(
      jobs2,
      owner,
      reference.pin.jobId,
      reference.pin.artifactId,
      context
    );
    if (approved.pin.version !== reference.pin.version || approved.pin.contentDigest !== reference.pin.contentDigest || approved.manifest.fixture !== (input.source.source === "deterministic_fixture") || reference.roles.some((role) => role === "species" || role === "pose") && approved.manifest.speciesId !== input.source.speciesId)
      throw new YardError(
        "INVALID",
        "Reviewed reference version, rights class or species does not match the conditioning request."
      );
  }
  if (input.shape) {
    const base = reviewedManifestInContext(
      jobs2,
      owner,
      input.shape.basedOn.jobId,
      input.shape.basedOn.artifactId,
      context
    );
    if (base.manifest.schemaVersion === 2 || base.manifest.speciesId !== input.source.speciesId || digest(base.pin) !== digest(input.shape.basedOn))
      throw new YardError("INVALID", "Shape revision requires the exact approved base animation.");
    const retained = reviewedSourceArtifactV2(jobs2, owner, base.manifest.sourceArtifact).input;
    const currentSource = { ...input };
    const baseSource = { ...retained };
    delete currentSource.shape;
    delete baseSource.shape;
    if (digest(currentSource) !== digest(baseSource))
      throw new YardError(
        "INVALID",
        "Shape revision must preserve the complete reviewed source and clips."
      );
  }
}

// birdsong-yard-sprites/src/lib/server/workbench/pagination.ts
import { createHmac, randomBytes, timingSafeEqual } from "node:crypto";
import { z as z37 } from "zod";
var key = randomBytes(32);
var positionSchema = z37.object({
  version: z37.literal(1),
  watermark: z37.number().int().min(0).max(Number.MAX_SAFE_INTEGER),
  before: z37.number().int().positive().max(Number.MAX_SAFE_INTEGER).nullable(),
  limit: pageRequestSchema.shape.limit
}).strict();
function invalid2() {
  throw new YardError("INVALID", "This page is unavailable. Refresh the list to start again.");
}
function sign(owner, scope, body) {
  return createHmac("sha256", key).update(JSON.stringify([owner, scope, body])).digest();
}
function encode(owner, scope, position) {
  const body = Buffer.from(JSON.stringify(position)).toString("base64url");
  return `${body}.${sign(owner, scope, body).toString("base64url")}`;
}
function readOwnerPage(db2, owner, scope, request, read) {
  if (db2.isTransaction) return readSnapshotPage(db2, owner, scope, request, read);
  db2.exec("BEGIN");
  try {
    const result2 = readSnapshotPage(db2, owner, scope, request, read);
    db2.exec("COMMIT");
    return result2;
  } catch (cause) {
    db2.exec("ROLLBACK");
    throw cause;
  }
}
function readSnapshotPage(db2, owner, scope, request, read) {
  pipelineIdentifierSchema.parse(owner);
  const checked = pageRequestSchema.parse(request);
  const table = scope === "png-files" ? "image_files" : "pip_jobs";
  const filter = scope === "reference-jobs" ? " AND definition_id='reference-generation'" : "";
  let position;
  if (checked.cursor) {
    const [body, signature] = checked.cursor.split(".");
    if (!body || !signature) invalid2();
    const bytes2 = Buffer.from(signature, "base64url");
    if (bytes2.toString("base64url") !== signature || bytes2.length !== 32 || !timingSafeEqual(bytes2, sign(owner, scope, body)))
      invalid2();
    try {
      const value = JSON.parse(Buffer.from(body, "base64url").toString("utf8"));
      position = positionSchema.parse(value);
    } catch {
      return invalid2();
    }
    if (position.limit !== checked.limit) invalid2();
  } else {
    const value = db2.prepare(`SELECT COALESCE(MAX(rowid),0) AS watermark FROM ${table} WHERE owner_id=?${filter}`).get(owner);
    position = positionSchema.parse({
      version: 1,
      watermark: value?.watermark,
      before: null,
      limit: checked.limit
    });
  }
  const rows = db2.prepare(
    `SELECT id,rowid AS ordinal FROM ${table} WHERE owner_id=?${filter} AND rowid<=? AND (? IS NULL OR rowid<?) ORDER BY rowid DESC LIMIT ?`
  ).all(owner, position.watermark, position.before, position.before, checked.limit + 1);
  const items = [];
  let size = 4096, last = null;
  for (const row of rows.slice(0, checked.limit)) {
    const id8 = pipelineIdentifierSchema.parse(row.id);
    const item = read(id8);
    const bytes2 = Buffer.byteLength(JSON.stringify(item)) + 1;
    if (size + bytes2 > WORKBENCH_RESPONSE_BYTES) {
      if (!items.length)
        throw new YardError(
          "INVALID",
          "This item exceeds the workbench response limit. Stored data and selections are unchanged."
        );
      break;
    }
    size += bytes2;
    items.push(item);
    last = z37.number().int().positive().parse(row.ordinal);
  }
  return {
    items,
    page: pageInfoSchema.parse({
      cursor: encode(owner, scope, position),
      nextCursor: rows.length > items.length && last !== null ? encode(owner, scope, { ...position, before: last }) : null,
      limit: checked.limit
    })
  };
}

// birdsong-yard-sprites/src/lib/server/assets/lifecycle.ts
function conflict(message) {
  throw new YardError("CONFLICT", message);
}
function unavailable() {
  throw new YardError("INVALID", "This private asset or its retained references are unavailable.");
}
var AssetLifecycleService = class {
  constructor(yard2, jobs2, options = {}) {
    this.yard = yard2;
    this.jobs = jobs2;
    this.options = options;
    this.db = yard2.database;
    if (jobs2.db !== this.db)
      throw new Error("Asset lifecycle requires one transaction connection.");
    const initialized = assertAssetLifecycleCompatibility(this.db);
    this.transaction(() => {
      if (!initialized) {
        for (const [, , sql] of ASSET_LIFECYCLE_SCHEMA) this.db.exec(sql);
        this.db.exec("INSERT INTO asset_lifecycle_migrations(version) VALUES(1)");
      }
    });
  }
  yard;
  jobs;
  options;
  db;
  transaction(run, mode = "write") {
    if (this.db.isTransaction) return run();
    this.db.exec(mode === "read" ? "BEGIN" : "BEGIN IMMEDIATE");
    try {
      const value = run();
      this.db.exec("COMMIT");
      return value;
    } catch (cause) {
      this.db.exec("ROLLBACK");
      throw cause;
    }
  }
  owned(owner, target2) {
    pipelineIdentifierSchema.parse(owner);
    const table = target2.kind === "private-file" ? "image_files" : "pip_jobs";
    if (!this.db.prepare("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?").get(table) || !this.db.prepare(`SELECT 1 FROM ${table} WHERE owner_id=? AND id=?`).get(owner, target2.id))
      unavailable();
  }
  inputDependencies(input, refs) {
    if (input.fileOrigin) refs.files.add(input.fileOrigin.file.id);
    for (const reference of input.conditioning.references) refs.jobs.add(reference.pin.jobId);
    if (input.shape) refs.jobs.add(input.shape.basedOn.jobId);
  }
  packageDependencies(owner, id8) {
    const input = this.db.prepare(
      "SELECT length(CAST(input_json AS BLOB)) AS n FROM pip_jobs WHERE owner_id=? AND id=?"
    ).get(owner, id8);
    if (!input || Number(input.n) > 1e6) unavailable();
    const budget = this.db.prepare(
      "SELECT COUNT(*) AS n, COALESCE(SUM(length(CAST(payload_json AS BLOB))+length(CAST(provenance_json AS BLOB))),0) AS bytes FROM pip_artifacts WHERE owner_id=? AND job_id=?"
    ).get(owner, id8);
    if (Number(budget?.n) > 64 || Number(budget?.bytes) > 8e6) unavailable();
    const job = this.jobs.get(owner, id8), refs = { jobs: /* @__PURE__ */ new Set(), files: /* @__PURE__ */ new Set() };
    if (job.parentJobId) refs.jobs.add(job.parentJobId);
    if (["asset-packaging", "asset-generation"].includes(job.definitionId)) {
      if ([2, 3].includes(job.definitionVersion) && job.definitionId === "asset-packaging")
        this.inputDependencies(supportedPosePackagingInputSchema.parse(job.input), refs);
      else if (job.definitionVersion === 1 && job.definitionId === "asset-packaging")
        assetPackagingInputSchema.parse(job.input);
      else if (job.definitionVersion === 1 && job.definitionId === "asset-generation")
        assetGenerationInputSchema.parse(job.input);
      else unavailable();
    } else if (job.definitionId === "animation-planning" && job.definitionVersion === 1) {
      animationPlanningInputSchema.parse(job.input);
    } else if (job.definitionId === "animation-planning" && job.definitionVersion === 2) {
      resolveAnimationSpecification(canonicalAnimationPlanningInputV2(job.input));
    } else if (job.definitionId === "reference-generation" && job.definitionVersion === 1) {
      canonicalReferenceGenerationInput(job.input);
    } else if (job.definitionId === "fixture-artwork" && [1, 2].includes(job.definitionVersion) || job.definitionId === "photo-to-animation" && job.definitionVersion === 1) {
      z38.object({ speciesId: z38.string().min(1).max(100), label: z38.string().min(1).max(120) }).strict().parse(job.input);
    } else unavailable();
    for (const artifact of this.jobs.artifacts(owner, id8)) {
      if (artifact.kind === "rgba-source-manifest")
        this.inputDependencies(
          supportedRgbaSourceArtifactSchema.parse(artifact.payload).input,
          refs
        );
      else if (artifact.kind === "animation-manifest") {
        const manifest = speciesManifestSchema.parse(artifact.payload);
        if (manifest.schemaVersion !== 2) {
          if (manifest.sourceArtifact.jobId !== id8) refs.jobs.add(manifest.sourceArtifact.jobId);
          for (const reference of manifest.conditioning.references)
            refs.jobs.add(reference.pin.jobId);
          if (manifest.shape) refs.jobs.add(manifest.shape.basedOn.jobId);
        }
      } else if (artifact.kind === "animation-production-plan") {
        if (job.definitionId !== "animation-planning" || ![1, 2].includes(job.definitionVersion))
          unavailable();
        const plan = animationProductionPlanSchema.parse(artifact.payload);
        const input2 = job.definitionVersion === 1 ? canonicalAnimationPlanningInput(job.input) : canonicalAnimationPlanningInputV2(job.input);
        if (plan.taxonomy.speciesId !== input2.taxonomy.speciesId || plan.inputSha256 !== digest(input2) || plan.specificationSha256 !== digest(plan.specification))
          unavailable();
        if (job.definitionVersion === 2 && plan.specificationSha256 !== digest(resolveAnimationSpecification(input2)))
          unavailable();
      } else if (artifact.kind === "reference-discovery-result") {
        if (job.definitionId !== "animation-planning" || job.definitionVersion !== 2) unavailable();
        const result2 = referenceDiscoveryResultSchema.parse(artifact.payload);
        const request = animationReferenceRequest(job.input);
        if (result2.taxonomy.speciesId !== request.taxonomy.speciesId || result2.requestSha256 !== digest(request))
          unavailable();
      } else if (artifact.kind === "reference-generation-candidate") {
        if (job.definitionId !== "reference-generation" || job.definitionVersion !== 1)
          unavailable();
        validateReferenceGenerationCandidate(artifact.payload, job.input);
      } else unavailable();
    }
    if (refs.jobs.has(id8)) unavailable();
    return refs;
  }
  selectablePackage(owner, id8, path2 = /* @__PURE__ */ new Set(), checked = /* @__PURE__ */ new Set()) {
    if (path2.has(id8) || path2.size >= 32 || checked.size >= 64) unavailable();
    if (checked.has(id8)) return true;
    path2.add(id8);
    this.owned(owner, { kind: "private-package", id: id8 });
    if (archiveState(this.db, owner, { kind: "private-package", id: id8 }).archived) return false;
    const refs = this.packageDependencies(owner, id8);
    for (const file of refs.files) {
      this.owned(owner, { kind: "private-file", id: file });
      if (archiveState(this.db, owner, { kind: "private-file", id: file }).archived) return false;
    }
    for (const job of refs.jobs)
      if (!this.selectablePackage(owner, job, path2, checked)) return false;
    path2.delete(id8);
    checked.add(id8);
    return true;
  }
  /** Retained resolution never calls this admission-only guard. */
  canSelectArtwork(owner, artwork) {
    if (!artwork.animationPin) return true;
    try {
      const approved = reviewedManifest(
        this.jobs,
        owner,
        artwork.animationPin.jobId,
        artwork.animationPin.artifactId
      );
      return digest(approved.pin) === digest(artwork.animationPin) && approved.manifest.speciesId === artwork.speciesId && this.selectablePackage(owner, artwork.animationPin.jobId);
    } catch {
      return false;
    }
  }
  assertQueueSelectable(owner, request) {
    const refs = { jobs: /* @__PURE__ */ new Set(), files: /* @__PURE__ */ new Set() };
    if (request.parentJobId) refs.jobs.add(request.parentJobId);
    if ([2, 3].includes(request.definitionVersion) && ["asset-packaging", "asset-generation"].includes(request.definitionId))
      this.inputDependencies(supportedPosePackagingInputSchema.parse(request.input), refs);
    for (const file of refs.files) {
      this.owned(owner, { kind: "private-file", id: file });
      if (archiveState(this.db, owner, { kind: "private-file", id: file }).archived)
        conflict("Restore this archived PNG before creating a new package.");
    }
    for (const id8 of refs.jobs)
      if (!this.selectablePackage(owner, id8))
        conflict(
          "Restore the archived package or source dependency before creating a new version."
        );
  }
  graph(owner) {
    const graph = { complete: true, packages: /* @__PURE__ */ new Map(), files: [] };
    const payloadSize = this.db.prepare(
      `SELECT
      (SELECT COALESCE(SUM(length(CAST(input_json AS BLOB))),0) FROM pip_jobs WHERE owner_id=?) +
      (SELECT COALESCE(SUM(length(CAST(payload_json AS BLOB))+length(CAST(provenance_json AS BLOB))),0) FROM pip_artifacts WHERE owner_id=?) AS n`
    ).get(owner, owner);
    const oversized = Number(payloadSize?.n) > 32e6;
    const rows = oversized ? [] : this.db.prepare(
      "SELECT id FROM pip_jobs WHERE owner_id=? ORDER BY created_at DESC, id LIMIT 513"
    ).all(owner);
    if (oversized) graph.complete = false;
    if (rows.length > 512) graph.complete = false;
    for (const row of rows.slice(0, 512)) {
      try {
        const id8 = pipelineIdentifierSchema.parse(row.id);
        graph.packages.set(id8, this.packageDependencies(owner, id8));
      } catch {
        graph.complete = false;
      }
    }
    if (this.db.prepare("SELECT 1 FROM sqlite_master WHERE name='image_files' AND type='table'").get()) {
      const files = this.db.prepare("SELECT * FROM image_files WHERE owner_id=? ORDER BY created_at DESC,id LIMIT 65").all(owner);
      if (files.length > 64) graph.complete = false;
      for (const row of files.slice(0, 64)) {
        try {
          if (typeof row.identity_json !== "string" || row.identity_json.length > 4096 || row.review_json !== null && (typeof row.review_json !== "string" || row.review_json.length > MAX_IMAGE_REVIEW_CHARS))
            unavailable();
          const file = JSON.parse(row.identity_json);
          const review2 = row.review_json === null ? null : JSON.parse(row.review_json);
          const record = pngFileRecordSchema.parse({ file, review: review2, createdAt: row.created_at });
          if (record.file.id !== row.id || record.file.original.sha256 !== row.original_sha256)
            unavailable();
          graph.files.push(record);
        } catch {
          graph.complete = false;
        }
      }
    }
    const fileIds = new Set(graph.files.map((file) => file.file.id));
    for (const deps of graph.packages.values()) {
      if ([...deps.jobs].some((id8) => !graph.packages.has(id8)) || [...deps.files].some((id8) => !fileIds.has(id8)))
        graph.complete = false;
    }
    const checked = /* @__PURE__ */ new Set();
    const visit = (id8, path2) => {
      if (path2.has(id8) || path2.size >= 32) {
        graph.complete = false;
        return;
      }
      if (checked.has(id8)) return;
      path2.add(id8);
      for (const next of graph.packages.get(id8)?.jobs ?? []) visit(next, path2);
      path2.delete(id8);
      checked.add(id8);
    };
    for (const id8 of graph.packages.keys()) visit(id8, /* @__PURE__ */ new Set());
    return graph;
  }
  overview(owner) {
    pipelineIdentifierSchema.parse(owner);
    return this.transaction(() => {
      const graph = this.graph(owner), snapshot = this.yard.snapshot(owner);
      const entries = [];
      const add = (target2, label3, retainedBytes, reasons) => {
        const state = archiveState(this.db, owner, target2);
        if (!state.archived) reasons.push("active");
        if (!graph.complete) reasons.push("incomplete-reference-scan");
        let selectionBlock = state.archived ? "archived" : "none";
        if (!state.archived && target2.kind === "private-package") {
          try {
            if (!this.selectablePackage(owner, target2.id)) selectionBlock = "archived-dependency";
          } catch {
            selectionBlock = "unavailable";
          }
        }
        entries.push({
          state,
          label: label3,
          retainedBytes,
          selectable: selectionBlock === "none",
          selectionBlock,
          cleanupEligible: target2.kind === "private-file" && reasons.length === 0,
          retainedBecause: [...new Set(reasons)]
        });
      };
      for (const [id8] of graph.packages) {
        const reasons = ["pipeline-history"];
        const artworks = snapshot.artworks.filter((art) => art.animationPin?.jobId === id8);
        if (artworks.length) reasons.push("retained-artwork");
        if (snapshot.birds.some((bird) => artworks.some((art) => art.id === bird.artworkId)))
          reasons.push("pinned-bird");
        if ([...graph.packages.values()].some((deps) => deps.jobs.has(id8)))
          reasons.push("referenced-by-package");
        const size = this.db.prepare(
          `SELECT
          (SELECT length(CAST(input_json AS BLOB)) FROM pip_jobs WHERE id=? AND owner_id=?) +
          (SELECT COALESCE(SUM(length(CAST(payload_json AS BLOB))+length(CAST(provenance_json AS BLOB))),0)
            FROM pip_artifacts WHERE job_id=? AND owner_id=?) AS n`
        ).get(id8, owner, id8, owner);
        add(
          { kind: "private-package", id: id8 },
          `${this.jobs.get(owner, id8).definitionId} \xB7 ${id8.slice(0, 8)}`,
          Number(size?.n),
          reasons
        );
      }
      for (const file of graph.files) {
        const reasons = [];
        if (file.review) reasons.push("file-review-evidence");
        if ([...graph.packages.values()].some((deps) => deps.files.has(file.file.id)))
          reasons.push("referenced-by-package");
        add(
          { kind: "private-file", id: file.file.id },
          `PNG \xB7 ${file.file.id.slice(0, 8)}`,
          file.file.original.bytes + file.file.canonical.bytes + file.file.canonical.width * file.file.canonical.height * 4,
          reasons
        );
      }
      const label2 = (bird) => (bird.name || snapshot.species.find((s) => s.id === bird.speciesId)?.commonName || "Bird").slice(0, 200);
      const pins = snapshot.birds.filter((bird) => bird.artworkId !== null).map((bird) => ({ birdId: bird.id, artworkId: bird.artworkId, label: label2(bird) }));
      const undoPins = [];
      const receipts = this.db.prepare(
        "SELECT receipt_json FROM asset_lifecycle_receipts WHERE owner_id=? ORDER BY rowid DESC LIMIT 2049"
      ).all(owner);
      if (receipts.length > 2048) throw new Error("Lifecycle receipt budget exceeded.");
      for (const row of receipts) {
        const receipt = readLifecycleReceipt(row.receipt_json);
        if (receipt.command.action !== "unpin") continue;
        const birdId = receipt.command.birdId;
        const retained = snapshot.birds.find((b) => b.id === birdId && b.artworkId === null);
        if (retained && receipt.previousArtworkId && undoPins.length < 32)
          undoPins.push({
            requestId: receipt.command.requestId,
            birdId,
            artworkId: receipt.previousArtworkId,
            label: label2(retained)
          });
      }
      return assetLifecycleOverviewSchema.parse({
        schemaVersion: 1,
        purgeEnabled: false,
        sharedCatalog: "read-only-not-owned",
        referenceScan: graph.complete ? "complete" : "incomplete",
        entries,
        pins,
        undoPins
      });
    }, "read");
  }
  /** Visible membership is independent of the conservative whole-graph scan budget.
   * Only bounded metadata and exact-target dependency checks are read; no bytes are purged. */
  packageHistory(owner, request = {}) {
    pipelineIdentifierSchema.parse(owner);
    return this.transaction(() => {
      const snapshot = this.yard.snapshot(owner);
      const result2 = readOwnerPage(this.db, owner, "asset-packages", request, (id8) => {
        const target2 = { kind: "private-package", id: id8 };
        const state = archiveState(this.db, owner, target2);
        const row = this.db.prepare(
          `SELECT substr(definition_id,1,120) AS label,
              length(CAST(input_json AS BLOB)) +
              (SELECT COALESCE(SUM(length(CAST(payload_json AS BLOB))+length(CAST(provenance_json AS BLOB))),0)
                FROM pip_artifacts WHERE job_id=? AND owner_id=?) AS bytes
              FROM pip_jobs WHERE id=? AND owner_id=?`
        ).get(id8, owner, id8, owner);
        const reasons = ["pipeline-history", "incomplete-reference-scan"];
        if (!state.archived) reasons.push("active");
        const artworks = snapshot.artworks.filter((art) => art.animationPin?.jobId === id8);
        if (artworks.length) reasons.push("retained-artwork");
        if (snapshot.birds.some((bird) => artworks.some((art) => art.id === bird.artworkId)))
          reasons.push("pinned-bird");
        let selectionBlock = state.archived ? "archived" : "none";
        if (!state.archived) {
          try {
            if (!this.selectablePackage(owner, id8)) selectionBlock = "archived-dependency";
          } catch {
            selectionBlock = "unavailable";
          }
        }
        return {
          state,
          label: `${String(row?.label || "Package")} \xB7 ${id8.slice(0, 8)}`,
          retainedBytes: Number(row?.bytes),
          selectable: selectionBlock === "none",
          selectionBlock,
          cleanupEligible: false,
          retainedBecause: reasons
        };
      });
      return assetPackageHistorySchema.parse({
        schemaVersion: 1,
        purgeEnabled: false,
        referenceScan: "not-run",
        entries: result2.items,
        page: result2.page
      });
    }, "read");
  }
  command(owner, value) {
    pipelineIdentifierSchema.parse(owner);
    const command = assetLifecycleCommandSchema.parse(value);
    return this.transaction(() => {
      const existing = this.db.prepare(
        "SELECT receipt_json FROM asset_lifecycle_receipts WHERE owner_id=? AND request_id=?"
      ).get(owner, command.requestId);
      if (existing) {
        if (readLifecycleReceipt(existing.receipt_json).commandDigest !== digest(command))
          conflict("This request ID belongs to a different lifecycle operation.");
        return assetLifecycleResponseSchema.parse({
          overview: this.overview(owner),
          receipt: { requestId: command.requestId, replayed: true }
        });
      }
      const count = this.db.prepare("SELECT COUNT(*) AS n FROM asset_lifecycle_receipts WHERE owner_id=?").get(owner);
      if (Number(count?.n) >= 2048)
        conflict("Lifecycle history capacity reached; no change was made.");
      if (Number(this.db.prepare("SELECT COUNT(*) AS n FROM asset_lifecycle_receipts").get()?.n) >= 32768)
        conflict("Lifecycle storage capacity reached; no change was made.");
      const savedAt = new Date((this.options.now ?? Date.now)()).toISOString();
      let previousArtworkId = null;
      if (command.action === "set-archive") {
        this.owned(owner, command.target);
        const current = archiveState(this.db, owner, command.target);
        if (current.revision === 0 && Number(this.db.prepare("SELECT COUNT(*) AS n FROM asset_archives").get()?.n) >= 16384)
          conflict("Archive storage capacity reached; no change was made.");
        if (current.revision !== command.expectedRevision)
          conflict("Archive state changed. Refresh before trying again.");
        if (current.revision >= 1e6) conflict("Archive revision capacity reached.");
        this.db.prepare(
          `INSERT INTO asset_archives(owner_id,kind,target_id,revision,archived,changed_at) VALUES(?,?,?,?,?,?)
          ON CONFLICT(owner_id,kind,target_id) DO UPDATE SET revision=excluded.revision,archived=excluded.archived,changed_at=excluded.changed_at`
        ).run(
          owner,
          command.target.kind,
          command.target.id,
          current.revision + 1,
          command.archived ? 1 : 0,
          savedAt
        );
      } else if (command.action === "unpin") {
        previousArtworkId = command.expectedArtworkId;
        this.yard.replaceArtworkSelection(owner, command.birdId, command.expectedArtworkId, null);
      } else this.restorePin(owner, command);
      this.options.failpoint?.("after-change");
      const receipt = {
        schemaVersion: 1,
        command,
        commandDigest: digest(command),
        previousArtworkId,
        savedAt
      };
      const serialized = JSON.stringify(receipt);
      readLifecycleReceipt(serialized);
      this.db.prepare(
        "INSERT INTO asset_lifecycle_receipts(owner_id,request_id,receipt_json) VALUES(?,?,?)"
      ).run(owner, command.requestId, serialized);
      this.options.failpoint?.("after-receipt");
      return assetLifecycleResponseSchema.parse({
        overview: this.overview(owner),
        receipt: { requestId: command.requestId, replayed: false }
      });
    });
  }
  restorePin(owner, command) {
    const row = this.db.prepare(
      "SELECT receipt_json FROM asset_lifecycle_receipts WHERE owner_id=? AND request_id=?"
    ).get(owner, command.unpinRequestId);
    if (!row) unavailable();
    const previous = readLifecycleReceipt(row.receipt_json);
    if (previous.command.action !== "unpin" || !previous.previousArtworkId) unavailable();
    this.yard.replaceArtworkSelection(
      owner,
      previous.command.birdId,
      null,
      previous.previousArtworkId
    );
  }
};

// birdsong-yard-sprites/src/lib/server/workbench/jobs.ts
var DETAIL_BYTES = 4 * 1024 * 1024;
function workbenchJob(jobs2, owner, id8) {
  const job = jobs2.get(owner, id8);
  const size = jobs2.db.prepare(
    `SELECT
    (SELECT COALESCE(SUM(length(CAST(output_json AS BLOB))),0) FROM pip_stages WHERE job_id=?) +
    (SELECT COALESCE(SUM(length(CAST(payload_json AS BLOB))+length(CAST(provenance_json AS BLOB))),0) FROM pip_artifacts WHERE owner_id=? AND job_id=?) AS bytes,
    (SELECT COUNT(*) FROM pip_artifacts WHERE owner_id=? AND job_id=?) AS artifacts`
  ).get(id8, owner, id8, owner, id8);
  const omitted = Number(size?.bytes) > DETAIL_BYTES / 2 || Number(size?.artifacts) > 3200;
  const small = () => ({
    ...job,
    stages: jobs2.stages(owner, id8, false),
    artifacts: [],
    artifactError: "Job details exceed the workbench page limit. Stored sources, reviews and selected pins are unchanged."
  });
  if (omitted) return admittedPipeline.workbenchJobSchema.parse(small());
  let value;
  try {
    value = {
      ...job,
      stages: jobs2.stages(owner, id8),
      artifacts: jobs2.artifacts(owner, id8),
      artifactError: null
    };
  } catch {
    value = {
      ...job,
      stages: jobs2.stages(owner, id8, false),
      artifacts: [],
      artifactError: "Stored artifact metadata is corrupt; selected pins are preserved."
    };
  }
  if (Buffer.byteLength(JSON.stringify(value)) > DETAIL_BYTES) value = small();
  return admittedPipeline.workbenchJobSchema.parse(value);
}
function jobPage(jobs2, owner, request = {}, references = false) {
  const result2 = readOwnerPage(
    jobs2.db,
    owner,
    references ? "reference-jobs" : "jobs",
    request,
    (id8) => workbenchJob(jobs2, owner, id8)
  );
  return admittedPipeline.jobsReadResponseSchema.parse({ jobs: result2.items, page: result2.page });
}

// audit-jobs-assets/lockfix.ts
var path = "/workspace/archive-history/audit-jobs-assets/data-32/synthetic.sqlite";
var yard = new YardRepository(path);
var db = yard.database;
var jobs = new JobRepository(db);
var life = new AssetLifecycleService(yard, jobs);
var target = db.prepare("SELECT id FROM pip_jobs WHERE owner_id=? ORDER BY rowid DESC LIMIT 1").get("alice").id;
db.exec("PRAGMA busy_timeout=75;");
var writer = new DatabaseSync3(path);
writer.exec("PRAGMA journal_mode=WAL;PRAGMA busy_timeout=75;BEGIN IMMEDIATE");
writer.prepare("UPDATE asset_archives SET archived=0,revision=2 WHERE owner_id=? AND target_id=?").run("alice", target);
var result = { probeBusyTimeoutMs: 75, writerUncommittedArchive: false, expectedReaderCommittedArchive: true };
for (const [name, run] of [
  ["jobsPage", () => jobPage(jobs, "alice", { limit: 10 })],
  ["packageHistory", () => life.packageHistory("alice", { limit: 10 })],
  ["overview", () => life.overview("alice")]
]) {
  const start2 = performance.now();
  const value = run();
  const state = "entries" in value ? value.entries.find((x) => x.state.target.id === target)?.state : null;
  result[name] = { ok: true, ms: performance.now() - start2, seenArchive: state?.archived ?? null, seenRevision: state?.revision ?? null };
  if (state) {
    assert.equal(state.archived, true);
    assert.equal(state.revision, 1);
  }
}
var denied = false;
var start = performance.now();
try {
  life.command("alice", { action: "set-archive", requestId: randomUUID3(), target: { kind: "private-package", id: target }, expectedRevision: 1, archived: false });
} catch (error) {
  denied = true;
  result.command = { blocked: true, ms: performance.now() - start, message: error.message, errcode: error.errcode };
  assert.equal(error.errcode, 5);
}
assert(denied);
writer.exec("ROLLBACK");
writer.close();
yard.close();
writeFileSync("/workspace/archive-history/audit-jobs-assets/lockfix-results.json", JSON.stringify(result, null, 2));
console.log(JSON.stringify(result));
