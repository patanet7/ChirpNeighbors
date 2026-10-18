import { placementSnapshotReaderSchema, placementSnapshotV2Schema } from './layout-authority.ts';
import { z } from 'zod';
import { canonicalObjectIdSchema } from './canonical-yard.ts';
import { idSchema } from './primitives.ts';
import {
  MAX_OBJECTS,
  objectKindSchema,
  placementSnapshotSchema,
  yardObjectsSchema,
  type ObjectKind,
  type YardObject,
} from './scene.ts';

export const FREE_FIXTURES_PER_KIND = 3;
export const MAX_OBJECT_OPERATION_RECEIPTS = 4096;
export const objectInventorySchema = z
  .object({
    version: z.literal(1),
    owned: z
      .object({
        perch: z.number().int().min(0).max(MAX_OBJECTS),
        feeder: z.number().int().min(0).max(MAX_OBJECTS),
        bath: z.number().int().min(0).max(MAX_OBJECTS),
        nest: z.number().int().min(0).max(MAX_OBJECTS),
        plant: z.number().int().min(0).max(MAX_OBJECTS).default(FREE_FIXTURES_PER_KIND),
      })
      .strict(),
  })
  .strict();
export type ObjectInventory = z.infer<typeof objectInventorySchema>;

/** Compact durable retry identity. The command's expected layout belongs in its
 * digest, never duplicated into every receipt. Receipts are private owner data. */
export const objectOperationReceiptSchema = z
  .object({
    requestId: z.string().uuid(),
    commandDigest: z.string().regex(/^[a-f0-9]{64}$/),
    resultObjectId: idSchema,
  })
  .strict();
export type ObjectOperationReceipt = z.infer<typeof objectOperationReceiptSchema>;
export const objectOperationReceiptsSchema = z
  .array(objectOperationReceiptSchema)
  .max(MAX_OBJECT_OPERATION_RECEIPTS)
  .superRefine((receipts, context) => {
    if (new Set(receipts.map((receipt) => receipt.requestId)).size !== receipts.length)
      context.addIssue({ code: 'custom', message: 'Object operation request IDs must be unique.' });
  });

export const objectInventoryCommandSchema = z
  .object({
    action: z.literal('object-inventory'),
    requestId: z.string().uuid(),
    expected: placementSnapshotSchema,
    payload: z.discriminatedUnion('operation', [
      z
        .object({
          operation: z.literal('place'),
          kind: objectKindSchema,
          catalogId: canonicalObjectIdSchema.optional(),
        })
        .strict(),
      z
        .object({
          operation: z.literal('restyle'),
          objectId: idSchema,
          catalogId: canonicalObjectIdSchema,
        })
        .strict(),
      z.object({ operation: z.literal('regional-defaults') }).strict(),
      z.object({ operation: z.literal('return'), objectId: idSchema }).strict(),
      z
        .object({
          operation: z.literal('undo-return'),
          objectId: idSchema,
          returnRequestId: z.string().uuid(),
          returnedFrom: placementSnapshotSchema,
        })
        .strict(),
      z
        .object({
          operation: z.literal('move'),
          objectId: idSchema,
          x: z.number().finite(),
          y: z.number().finite(),
        })
        .strict(),
    ]),
  })
  .strict();
export const objectInventoryCommandV2Schema = objectInventoryCommandSchema
  .extend({
    schemaVersion: z.literal(2),
    expected: placementSnapshotV2Schema,
    payload: z.union([
      objectInventoryCommandSchema.shape.payload,
      z
        .object({
          operation: z.literal('undo-return'),
          objectId: idSchema,
          returnRequestId: z.string().uuid(),
          returnedFrom: placementSnapshotReaderSchema,
        })
        .strict(),
    ]),
  })
  .strict();
export const objectInventoryCommandReaderSchema = z.union([
  objectInventoryCommandSchema,
  objectInventoryCommandV2Schema,
]);
export type ObjectInventoryCommand = z.infer<typeof objectInventoryCommandReaderSchema>;
export type ObjectInventoryPayload = ObjectInventoryCommand['payload'];

/** Only missing legacy inventory receives a starter allocation. Callers must
 * validate any supplied inventory instead of replacing it, including zero stock. */
export function starterInventory(objects: readonly YardObject[]): ObjectInventory {
  const placed = yardObjectsSchema.parse(objects);
  const owned = { perch: 3, feeder: 3, bath: 3, nest: 3, plant: 3 };
  for (const kind of objectKindSchema.options)
    owned[kind] = Math.max(
      FREE_FIXTURES_PER_KIND,
      placed.filter((item) => item.kind === kind).length,
    );
  return { version: 1, owned };
}

/** Cross-record checks supplement the structural inventory schema. Existing
 * placement geometry/ID validation remains the yard object's authority. */
export function inventoryIssues(
  inventory: ObjectInventory,
  objects: readonly YardObject[],
): string[] {
  return objectKindSchema.options
    .filter((kind) => availableStock(inventory, objects, kind) < 0)
    .map((kind) => `Placed ${kind} objects exceed owned stock.`);
}

/** Derived from validated owner inventory and placements; never persisted or
 * incremented on return. A negative result identifies an invalid aggregate. */
export function availableStock(
  inventory: ObjectInventory,
  objects: readonly YardObject[],
  kind: ObjectKind,
): number {
  return inventory.owned[kind] - objects.filter((object) => object.kind === kind).length;
}
