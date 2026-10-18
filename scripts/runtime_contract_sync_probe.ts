// Bundled by the paired checker against the explicitly selected UI authority.
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { createRequire } from "node:module";
import { join } from "node:path";
import { YardRepository } from "@chirp-runtime/lib/server/storage/repository.ts";
import { backupSchema } from "@chirp-runtime/lib/domain/yard.ts";
import { yardCommandSchema } from "@chirp-runtime/lib/domain/commands.ts";
import { objectInventoryCommandSchema } from "@chirp-runtime/lib/domain/object-inventory.ts";
import {
  yardLayoutReadSchema,
  yardLayoutCommandResponseSchema,
} from "@chirp-runtime/lib/domain/yard-layout.ts";
import { defaultFictionalPersonality } from "@chirp-runtime/lib/domain/bird-behavior.ts";
import { runtimeControlSchema } from "@chirp-runtime/lib/engine/runtime-control-contracts.ts";
import {
  physicalSurfaceOptionsSchema,
  defaultPhysicalSurfaceOptions,
} from "@chirp-runtime/lib/engine/physical-surface-contracts.ts";
import {
  yardRuntimeSelectionCommandSchema,
  yardRuntimeAdvanceV1CommandSchema,
} from "@chirp-runtime/lib/engine/yard-runtime-contracts.ts";
import {
  devWorkbenchRequestSchema,
  devWorkbenchDocumentSchema,
  devWorkbenchPlaybackSchema,
} from "@chirp-runtime/lib/dev-workbench/contracts.ts";
import { defaultEnvironmentControls } from "@chirp-runtime/lib/weather/environment-contracts.ts";

const [ui, canonical] = process.argv.slice(2);
const requireUI = createRequire(join(ui, "package.json"));
const Ajv = requireUI("ajv");
const addFormats = requireUI("ajv-formats");
const ajv = new Ajv({ allErrors: true, strict: false });
addFormats(ajv);
const validators = new Map();
const cases = [];
const authorities = new Map([
  ["object-inventory-command-v1", objectInventoryCommandSchema],
  ["yard-layout-read-v1", yardLayoutReadSchema],
  ["yard-layout-command-response-v1", yardLayoutCommandResponseSchema],
  ["yard-backup-v2", backupSchema],
  ["runtime-control-v1", runtimeControlSchema],
  ["physical-surface-options-v1", physicalSurfaceOptionsSchema],
  ["yard-runtime-selection-v1", yardRuntimeSelectionCommandSchema],
  ["yard-runtime-advance-v1", yardRuntimeAdvanceV1CommandSchema],
  ["dev-workbench-request-v1", devWorkbenchRequestSchema],
  ["dev-workbench-scenario-v1", devWorkbenchDocumentSchema],
  ["dev-workbench-playback-v1", devWorkbenchPlaybackSchema],
]);
function add(schema, name, value, valid, authoritativeValid = valid) {
  if (authorities.has(schema))
    assert.equal(
      authorities.get(schema).safeParse(value).success,
      authoritativeValid,
      name + " Zod authority",
    );
  if (!validators.has(schema))
    validators.set(
      schema,
      ajv.compile(
        JSON.parse(
          readFileSync(
            join(canonical, "contracts", schema + ".schema.json"),
            "utf8",
          ),
        ),
      ),
    );
  const validator = validators.get(schema);
  assert.equal(
    validator(value),
    valid,
    name + ": " + JSON.stringify(validator.errors),
  );
  cases.push({
    schema,
    name,
    value: structuredClone(value),
    valid,
    authoritativeValid,
  });
}
const now = "2026-10-17T12:00:00.000Z";
const repository = new YardRepository(":memory:");
const owner = "synthetic-contract-sync";
try {
  const fresh = repository.exportBackup(owner, now);
  add(
    "yard-backup-v2",
    "actual fresh runtime export includes plant inventory",
    fresh,
    true,
  );
  const staleAjv = new Ajv({ allErrors: true, strict: false });
  addFormats(staleAjv);
  const stale = staleAjv.compile(
    JSON.parse(
      readFileSync(
        join(
          canonical,
          "contracts/fixtures/compatibility/yard-backup-v2-before-20261017.schema.json",
        ),
        "utf8",
      ),
    ),
  );
  assert.equal(
    stale(fresh),
    false,
    "Stale V2 strict reader must visibly reject new plant inventory",
  );
  assert(
    stale.errors.some(
      (error) =>
        error.keyword === "additionalProperties" &&
        error.params.additionalProperty === "plant",
    ),
  );
  const expected = {
    scene: fresh.data.preferences.scene,
    scenePin: fresh.data.preferences.scenePin,
    objects: fresh.data.environment.objects,
  };
  const place = {
    action: "object-inventory",
    requestId: "c73bbd65-f29a-4933-8f91-dc12e258f580",
    expected,
    payload: {
      operation: "place",
      kind: "plant",
      catalogId: "blue_eyed_grass",
    },
  };
  assert(yardCommandSchema.safeParse(place).success);
  add(
    "object-inventory-command-v1",
    "plant with canonical catalog identity",
    place,
    true,
  );
  repository.objectInventory(owner, place, now);
  const plant = repository.exportBackup(owner, now);
  add(
    "yard-backup-v2",
    "actual export after canonical plant placement",
    plant,
    true,
  );
  const restored = new YardRepository(":memory:");
  try {
    restored.restoreBackup(owner, plant, now);
    assert.deepEqual(restored.exportBackup(owner, now), plant);
  } finally {
    restored.close();
  }
  const legacy = structuredClone(fresh);
  const zeroStock = structuredClone(fresh);
  zeroStock.data.environment.inventory.owned.plant = 0;
  assert.equal(
    backupSchema.parse(zeroStock).data.environment.inventory.owned.plant,
    0,
  );
  add(
    "yard-backup-v2",
    "supplied zero plant stock is not replaced by a default",
    zeroStock,
    true,
  );
  delete legacy.data.environment.inventory.owned.plant;
  add(
    "yard-backup-v2",
    "legacy V2 missing plant remains admitted",
    legacy,
    true,
  );
  const migrated = backupSchema.parse(legacy);
  assert.equal(migrated.data.environment.inventory.owned.plant, 3);
  assert.equal(
    stale(legacy),
    true,
    "Pinned old reader still accepts actual legacy shape",
  );
  const extended = structuredClone(plant);
  const speciesId = "cn-species-passer-domesticus";
  extended.data.species.push({
    id: speciesId,
    commonName: "House Sparrow",
    scientificName: "Passer domesticus",
  });
  extended.data.birds.push({
    id: "synthetic-resident",
    speciesId,
    name: "Synthetic contract resident",
    lifecycle: "permanent",
    createdAt: now,
    expiresAt: null,
    promotedAt: now,
    artworkId: null,
    originEventId: null,
    behavior: {
      schemaVersion: 1,
      revision: 1,
      source: "owner-authored",
      traits: defaultFictionalPersonality("synthetic-resident"),
    },
    starterArt: {
      schemaVersion: 1,
      revision: 0,
      mode: "fixed",
      channel: {
        kind: "bird",
        subjectId: speciesId,
        styleId: "synthetic",
        variantId: "default",
        compatibilityMajor: 1,
      },
      compatibility: {
        rendererContract: "rgba-pose-v1",
        anchorConvention: "feet",
        scaleConvention: "world",
        geometrySha256: null,
      },
      previousArtworkId: null,
    },
  });
  extended.data.starterUpdateReceipts = [
    {
      requestId: "0c04821e-2140-4dbb-89f9-5ac6b340c358",
      commandDigest: "a".repeat(64),
      action: "starter-art-policy",
      changedBirdIds: ["synthetic-resident"],
      createdAt: now,
    },
  ];
  const admitted = backupSchema.parse(extended);
  const extendedRestore = new YardRepository(":memory:");
  try {
    extendedRestore.restoreBackup(owner, admitted, now);
    assert.deepEqual(extendedRestore.exportBackup(owner, now), admitted);
    extendedRestore.restoreBackup("synthetic-legacy-migration", legacy, now);
    assert.equal(
      extendedRestore.exportBackup("synthetic-legacy-migration", now).data
        .environment.inventory.owned.plant,
      3,
    );
  } finally {
    extendedRestore.close();
  }
  add(
    "yard-backup-v2",
    "saved personality and starter binding receipts",
    admitted,
    true,
  );
  for (const [name, mutate] of [
    [
      "unknown owner field",
      (v) => {
        v.ownerId = "not-authority";
      },
    ],
    [
      "future backup version",
      (v) => {
        v.version = 99;
      },
    ],
    [
      "negative plant stock",
      (v) => {
        v.data.environment.inventory.owned.plant = -1;
      },
    ],
    [
      "unknown catalog identity",
      (v) => {
        v.data.environment.objects.at(-1).catalogId = "unknown";
      },
    ],
    [
      "personality beyond bounds",
      (v) => {
        v.data.birds[0].behavior.traits.boldness = 2;
      },
    ],
    [
      "future starter binding",
      (v) => {
        v.data.birds[0].starterArt.schemaVersion = 99;
      },
    ],
    [
      "invalid starter receipt UUID",
      (v) => {
        v.data.starterUpdateReceipts[0].requestId = "invalid";
      },
    ],
  ]) {
    const value = structuredClone(admitted);
    mutate(value);
    assert.equal(backupSchema.safeParse(value).success, false, name);
    add("yard-backup-v2", name, value, false);
  }
  add(
    "object-inventory-command-v1",
    "unknown catalog rejected",
    { ...place, payload: { ...place.payload, catalogId: "unknown" } },
    false,
  );
  add(
    "object-inventory-command-v1",
    "restyle canonical identity",
    {
      ...place,
      payload: {
        operation: "restyle",
        objectId: plant.data.environment.objects.at(-1).id,
        catalogId: "san_diego_monkeyflower",
      },
    },
    true,
  );
  add(
    "object-inventory-command-v1",
    "regional defaults canonical command",
    { ...place, payload: { operation: "regional-defaults" } },
    true,
  );
  const control = { seed: 42, paused: false, speed: 1 };
  const physical = defaultPhysicalSurfaceOptions();
  const selection = {
    runtimeId: "synthetic-runtime",
    actorId: null,
    targetObjectId: null,
  };
  const advance = {
    schemaVersion: 1,
    physical,
    delta: 0,
    interactionRequest: {
      revision: 1,
      action: "cancel",
      origin: { ...selection, selectionRevision: 0 },
    },
  };
  const state = {
    control,
    physical,
    environment: defaultEnvironmentControls(),
    selection: { actorId: null, targetObjectId: null },
  };
  const playback = {
    initial: state,
    current: state,
    timeline: [{ type: "step", ticks: 1 }],
  };
  const document = {
    format: "chirpneighbors-dev-workbench",
    version: 1,
    ownerId: owner,
    frozenAt: now,
    sessionSeed: 42,
    initialBackup: fresh,
    backup: plant,
    playback,
  };
  add(
    "dev-workbench-playback-v1",
    "seed consistency remains an authoritative semantic check",
    { ...playback, current: { ...state, control: { ...control, seed: 43 } } },
    true,
    false,
  );
  add(
    "dev-workbench-scenario-v1",
    "scenario seed binding remains an authoritative semantic check",
    { ...document, sessionSeed: 43 },
    true,
    false,
  );
  const mismatchedCatalog = structuredClone(admitted);
  mismatchedCatalog.data.environment.objects.at(-1).catalogId = "bench";
  add(
    "yard-backup-v2",
    "catalog kind matching remains authoritative beyond enum structure",
    mismatchedCatalog,
    true,
    false,
  );
  for (const [schema, value] of [
    ["runtime-control-v1", control],
    ["physical-surface-options-v1", physical],
    ["yard-runtime-selection-v1", selection],
    ["yard-runtime-advance-v1", advance],
    ["dev-workbench-playback-v1", playback],
    ["dev-workbench-scenario-v1", document],
  ]) {
    add(schema, schema + " actual authority seed", value, true);
    add(
      schema,
      schema + " rejects unknown field",
      { ...value, unknown: true },
      false,
    );
  }
  add(
    "runtime-control-v1",
    "string boolean cannot unpause clock",
    { ...control, paused: "false" },
    false,
  );
  add(
    "physical-surface-options-v1",
    "unbounded rainfall rejected",
    { ...physical, precipitationMmPerHour: 501 },
    false,
  );
  add(
    "yard-runtime-advance-v1",
    "versioned request must bind exact runtime selection",
    { ...advance, interactionRequest: { revision: 1, action: "cancel" } },
    false,
  );
  add(
    "yard-runtime-advance-v1",
    "unknown action cannot become a bath request",
    {
      ...advance,
      interactionRequest: { ...advance.interactionRequest, action: "typo" },
    },
    false,
  );
  const request = {
    schemaVersion: 1,
    op: "command",
    scenarioId: "a328182e-26e8-443b-a58b-5a00cb3614ab",
    requestId: "ae36ab79-ae03-40b4-aedc-cb1187276694",
    expectedRevision: 0,
    command: place,
  };
  add(
    "dev-workbench-request-v1",
    "canonical plant command in workbench envelope",
    request,
    true,
  );
  add(
    "dev-workbench-request-v1",
    "workbench exact saved document load",
    { schemaVersion: 1, op: "load", requestId: request.requestId, document },
    true,
  );
  for (const action of [
    "fixtures",
    "import",
    "restore",
    "pin-animation",
    "move-object",
  ])
    add(
      "dev-workbench-request-v1",
      "workbench excludes unsafe direct alias " + action,
      { ...request, command: { action } },
      false,
    );
  const pngCase = JSON.parse(
    readFileSync(join(ui, "contracts/fixtures/boundary-cases-v1.json"), "utf8"),
  ).cases.find(
    (entry) =>
      entry.schema === "png-file-review-command-v1" &&
      entry.valid &&
      entry.value.source,
  );
  assert(pngCase, "Existing PNG source review golden required");
  const candidateReview = structuredClone(pngCase.value);
  candidateReview.source.reviewScope = "development-candidate";
  add(
    "png-file-review-command-v1",
    "explicit candidate review scope survives canonical reader",
    candidateReview,
    true,
  );
  candidateReview.source.reviewScope = "production";
  add(
    "png-file-review-command-v1",
    "candidate scope cannot assert production approval",
    candidateReview,
    false,
  );
  // Object-edit continuation: all writes are isolated synthetic in-memory owners.
  const objectOwner = "synthetic-object-edit";
  const placement = (snapshot) => ({
    scene: snapshot.preferences.scene,
    scenePin: snapshot.preferences.scenePin,
    objects: snapshot.environment.objects,
  });
  const objectBefore = repository.snapshot(objectOwner, now);
  const originalBath = objectBefore.environment.objects.find(
    (object) => object.id === "fixture-bath",
  );
  assert(originalBath);
  const returned = {
    action: "object-inventory",
    requestId: "3eb58505-05b6-466b-96e7-5002cb62e232",
    expected: placement(objectBefore),
    payload: { operation: "return", objectId: originalBath.id },
  };
  const afterReturn = repository.objectInventory(objectOwner, returned, now);
  const undo = {
    action: "object-inventory",
    requestId: "68397060-d324-4aa0-8f48-34ed474202d0",
    expected: placement(afterReturn),
    payload: {
      operation: "undo-return",
      objectId: originalBath.id,
      returnRequestId: returned.requestId,
      returnedFrom: returned.expected,
    },
  };
  add(
    "object-inventory-command-v1",
    "object edit: receipt-bound undo return",
    undo,
    true,
  );
  add(
    "dev-workbench-request-v1",
    "object edit: undo through existing workbench envelope",
    { ...request, command: undo },
    true,
  );
  for (const field of ["returnRequestId", "returnedFrom"]) {
    const invalid = structuredClone(undo);
    delete invalid.payload[field];
    add(
      "object-inventory-command-v1",
      "object edit: undo requires " + field,
      invalid,
      false,
    );
  }
  add(
    "object-inventory-command-v1",
    "object edit: undo requires UUID return receipt",
    { ...undo, payload: { ...undo.payload, returnRequestId: "not-a-uuid" } },
    false,
  );
  add(
    "object-inventory-command-v1",
    "object edit: undo rejects invented owner authority",
    { ...undo, payload: { ...undo.payload, ownerId: "other-owner" } },
    false,
  );
  const forged = structuredClone(undo);
  forged.payload.returnedFrom.objects.find(
    (object) => object.id === originalBath.id,
  ).x += 10;
  add(
    "object-inventory-command-v1",
    "object edit: structurally valid history still requires owner receipt semantics",
    forged,
    true,
  );
  assert.throws(
    () => repository.objectInventory(objectOwner, forged, now),
    /cannot be undone/,
  );
  assert.deepEqual(repository.snapshot(objectOwner, now), afterReturn);
  const otherOwner = "synthetic-object-edit-other";
  const otherBefore = repository.snapshot(otherOwner, now);
  assert.throws(
    () =>
      repository.objectInventory(
        otherOwner,
        { ...undo, expected: placement(otherBefore) },
        now,
      ),
    /cannot be undone/,
  );
  assert.deepEqual(repository.snapshot(otherOwner, now), otherBefore);
  const move = {
    action: "object-inventory",
    requestId: "8f780d7c-a143-4f5b-b058-f41e22a37221",
    expected: placement(afterReturn),
    payload: { operation: "move", objectId: "fixture-perch", x: 280, y: 420 },
  };
  const afterMove = repository.objectInventory(objectOwner, move, now);
  assert.throws(
    () => repository.objectInventory(objectOwner, undo, now),
    /yard changed/,
  );
  assert.deepEqual(repository.snapshot(objectOwner, now), afterMove);
  const currentUndo = { ...undo, expected: placement(afterMove) };
  const afterUndo = repository.objectInventory(objectOwner, currentUndo, now);
  assert.deepEqual(
    afterUndo.environment.objects.find(
      (object) => object.id === originalBath.id,
    ),
    originalBath,
  );
  assert.equal(
    afterUndo.environment.objects.length,
    objectBefore.environment.objects.length,
  );
  assert.equal(
    afterUndo.environment.objectReceipts.at(-1).requestId,
    undo.requestId,
  );
  assert.deepEqual(
    repository.objectInventory(objectOwner, currentUndo, now),
    afterUndo,
  );
  const layoutRead = { snapshot: afterUndo };
  const layoutAck = { ...layoutRead, message: "Arrangement saved." };
  add(
    "yard-layout-read-v1",
    "object edit: actual owner snapshot without resolved assets",
    layoutRead,
    true,
  );
  add(
    "yard-layout-command-response-v1",
    "object edit: actual durable undo acknowledgment",
    layoutAck,
    true,
  );
  add(
    "yard-layout-read-v1",
    "object edit: layout read rejects asset bundle",
    { ...layoutRead, assets: [] },
    false,
  );
  add(
    "yard-layout-command-response-v1",
    "object edit: layout acknowledgment rejects asset bundle",
    { ...layoutAck, assets: [] },
    false,
  );
  add(
    "yard-layout-command-response-v1",
    "object edit: acknowledgment requires message",
    layoutRead,
    false,
  );
  add(
    "yard-layout-command-response-v1",
    "object edit: acknowledgment rejects empty message",
    { ...layoutAck, message: "" },
    false,
  );
  add(
    "yard-layout-command-response-v1",
    "object edit: acknowledgment cannot claim owner field",
    { ...layoutAck, ownerId: otherOwner },
    false,
  );
  console.log(
    JSON.stringify({
      schemaVersion: 1,
      cases,
      migration: {
        missingPlantDefaultsTo: 3,
        staleReaderRejectsPlant: true,
        readerAppliesDefaults:
          "Zod backup admission; JSON Schema validation does not mutate data",
      },
      roundtrip:
        "exact actual plant backup -> separate in-memory repository -> export",
    }),
  );
} finally {
  repository.close();
}
