import { starterArtBindingSchema, starterUpdateReceiptsSchema } from './starter-update.ts';
import { regionalBackgroundSchema } from './regional-yard.ts';
import { savedBirdBehaviorSchema } from './bird-behavior.ts';
import { starterSpeciesCatalog } from './starter-birds.ts';
import { scenePinSchema, sceneSettingSchema, regionPreferenceSchema } from '../scenes/manifest.ts';
import { resolveScene } from '../scenes/catalog.ts';
import { z } from 'zod';
import { reviewAssetPackageSchema } from '../workbench/asset-package.ts';
import { animationPinSchema } from '../assets/manifest-v2.ts';
import { catalogPinSchema } from '../assets/catalog-pin.ts';
import { idSchema, timestampSchema } from './primitives.ts';
import {
  correctionRecordSchema,
  effectiveEvidenceSchema,
  sameRevision,
  type EffectiveEvidence,
} from './evidence.ts';
import { defaultObjects, validateObjects, yardObjectsSchema } from './scene.ts';
import {
  objectInventorySchema,
  objectOperationReceiptsSchema,
  starterInventory,
  inventoryIssues,
} from './object-inventory.ts';
import { defaultWeatherSettings, weatherSettingsSchema } from '../weather/contracts.ts';

export { idSchema, timestampSchema } from './primitives.ts';
export type JsonValue =
  string | number | boolean | null | JsonValue[] | { [key: string]: JsonValue };
export const jsonValueSchema: z.ZodType<JsonValue> = z.lazy(() =>
  z.union([
    z.string(),
    z.number().finite(),
    z.boolean(),
    z.null(),
    z.array(jsonValueSchema),
    z.record(jsonValueSchema),
  ]),
);
export const speciesSchema = z
  .object({
    id: idSchema,
    commonName: z.string().min(1).max(120),
    scientificName: z.string().min(3).max(160),
    description: z.string().max(1000).optional(),
    referencePhoto: z.record(jsonValueSchema).optional(),
  })
  .strict();
export const sourceSchema = z
  .object({
    kind: z.enum(['fixture', 'manual', 'model', 'external']),
    label: z.string().min(1).max(120),
    sourceEventId: idSchema,
    provider: z.string().min(1).max(100).optional(),
    modelVersion: z.string().max(100).optional(),
  })
  .strict();
export const identificationSchema = z
  .object({
    schemaVersion: z.literal(2),
    id: idSchema,
    species: speciesSchema,
    observedAt: timestampSchema.nullable(),
    ingestedAt: timestampSchema,
    source: sourceSchema,
    confidence: z.number().min(0).max(1).optional(),
    recordingId: idSchema.optional(),
    /** Private evidence only. Never copy this object into a public projection. */
    metadata: z.record(jsonValueSchema).optional(),
  })
  .strict();
export const importEventSchema = identificationSchema
  .omit({ ingestedAt: true })
  .extend({ ingestedAt: timestampSchema.optional() });
export const hasControlCharacters = (value: string): boolean =>
  Array.from(value).some(
    (character) => character.charCodeAt(0) < 32 || character.charCodeAt(0) === 127,
  );
const localImageSchema = z
  .string()
  .max(1_500_000)
  .refine(
    (value) =>
      (value.startsWith('/') &&
        !value.startsWith('//') &&
        !/[\\\s]/.test(value) &&
        !hasControlCharacters(value)) ||
      /^data:image\/(png|jpeg|webp);base64,[a-zA-Z0-9+/=]+$/.test(value),
    'Use a bundled image path or embedded PNG, JPEG or WebP image; remote image requests are disabled.',
  );
const artworkObjectSchema = z
  .object({
    id: idSchema,
    speciesId: idSchema,
    version: z.number().int().positive(),
    status: z.enum(['fixture', 'reviewed', 'candidate']),
    /** Optional exact pipeline artifact; old backups and image-only art remain valid. */
    animationPin: animationPinSchema.optional(),
    /** Exact generic shared release; never a private job or an individual bird identity. */
    catalogPin: catalogPinSchema.optional(),
    imageUrl: localImageSchema,
    sha256: z
      .string()
      .regex(/^[a-f0-9]{64}$/)
      .optional(),
    representation: z.string().min(1).max(200),
    provenance: z.record(jsonValueSchema),
    /** Only explicit catalog keys can cross the public boundary; URLs cannot. */
    catalogKey: z.enum(['fixture-robin', 'fixture-sparrow', 'fixture-bluejay']).optional(),
  })
  .strict();
export const artworkSchema = artworkObjectSchema.superRefine((artwork, context) => {
  if (artwork.catalogPin && (artwork.animationPin || artwork.catalogKey))
    context.addIssue({
      code: 'custom',
      message: 'Shared, private and bundled asset pins cannot be mixed.',
    });
});
export const birdInstanceSchema = z
  .object({
    id: idSchema,
    speciesId: idSchema,
    name: z.string().trim().min(1).max(60).nullable(),
    lifecycle: z.enum(['temporary', 'permanent', 'expired']),
    createdAt: timestampSchema,
    expiresAt: timestampSchema.nullable(),
    promotedAt: timestampSchema.nullable(),
    artworkId: idSchema.nullable(),
    originEventId: idSchema.nullable(),
    /** Private authored display traits; absent legacy values retain deterministic defaults. */
    behavior: savedBirdBehaviorSchema.optional(),
    starterArt: starterArtBindingSchema.optional(),
  })
  .strict();
export const collectionEntrySchema = z
  .object({ id: idSchema, speciesId: idSchema, collectedAt: timestampSchema })
  .strict();
export const preferencesSchema = z
  .object({
    palette: z.enum(['twilight', 'fieldnotes', 'moonlit']),
    scene: sceneSettingSchema,
    scenePin: scenePinSchema.nullable().default(null),
    regionPreference: regionPreferenceSchema.default('unspecified'),
    reducedMotion: z.boolean(),
    /** Private opt-in technical candidates, never included by public projection. */
    developmentCandidateArt: z.boolean().optional(),
    hideLegacyShowcaseSamples: z.boolean().optional(),
    candidateRegionalBackground: regionalBackgroundSchema.nullable().optional(),
    candidateObjectArt: z
      .object({ objectId: idSchema, package: reviewAssetPackageSchema })
      .strict()
      .optional(),
    /** Provisional development default; changing it affects future imports only. */
    visitorTtlHours: z
      .number()
      .int()
      .min(1)
      .max(24 * 90),
  })
  .strict();
export const preferencesPatchSchema = preferencesSchema
  .omit({ candidateObjectArt: true })
  .partial();
export type PreferencesPatch = z.input<typeof preferencesPatchSchema>;
export const defaultPreferences = (): Preferences => ({
  palette: 'twilight',
  scene: 'garden',
  scenePin: null,
  regionPreference: 'unspecified',
  reducedMotion: false,
  visitorTtlHours: 24,
});
export const environmentSchema = z
  .object({
    version: z.literal(1),
    objects: yardObjectsSchema,
    weather: weatherSettingsSchema,
    inventory: objectInventorySchema,
    objectReceipts: objectOperationReceiptsSchema,
  })
  .strict();
export type YardEnvironment = z.infer<typeof environmentSchema>;
/** Hydration belongs only to stored data and backup admission, never current responses. */
const persistedEnvironmentSchema = environmentSchema
  .extend({
    inventory: objectInventorySchema.optional(),
    objectReceipts: objectOperationReceiptsSchema.optional(),
  })
  .transform((environment) => ({
    ...environment,
    inventory: environment.inventory ?? starterInventory(environment.objects),
    objectReceipts: environment.objectReceipts ?? [],
  }));
export const defaultEnvironment = (): YardEnvironment => ({
  version: 1,
  objects: defaultObjects(),
  weather: defaultWeatherSettings(),
  inventory: starterInventory(defaultObjects()),
  objectReceipts: [],
});
export const yardDataSchema = z
  .object({
    version: z.literal(2),
    species: z.array(speciesSchema),
    events: z.array(identificationSchema),
    /** Additive v2 extension; raw events never change when corrections are appended. */
    corrections: z.array(correctionRecordSchema).max(10000).default([]),
    collection: z.array(collectionEntrySchema),
    birds: z.array(birdInstanceSchema),
    artworks: z.array(artworkSchema),
    starterUpdateReceipts: starterUpdateReceiptsSchema.optional(),
    preferences: preferencesSchema,
    /** Additive v2 extension: older persisted yards/backups receive fresh, stable defaults. */
    environment: persistedEnvironmentSchema.default(defaultEnvironment),
  })
  .strict()
  .superRefine((state, ctx) => {
    const fail = (message: string) => ctx.addIssue({ code: 'custom', message });
    for (const issue of inventoryIssues(state.environment.inventory, state.environment.objects))
      fail(issue);
    try {
      validateObjects(
        state.environment.objects,
        resolveScene(state.preferences.scene, state.preferences.scenePin).manifest,
      );
    } catch {
      fail('Invalid yard object placement for this scene.');
    }
    for (const [label, values] of Object.entries({
      species: state.species,
      events: state.events,
      corrections: state.corrections,
      collection: state.collection,
      birds: state.birds,
      artworks: state.artworks,
    })) {
      if (new Set(values.map((value) => value.id)).size !== values.length)
        fail(`Duplicate ${label} ID`);
    }
    const species = new Map(state.species.map((s) => [s.id, s]));
    const art = new Map(state.artworks.map((a) => [a.id, a]));
    if (
      new Set(state.species.map((s) => s.scientificName.toLowerCase())).size !==
      state.species.length
    )
      fail('Duplicate taxon identity');
    if (new Set(state.events.map(sourceEventKey)).size !== state.events.length)
      fail('Duplicate source event identity');
    if (new Set(state.collection.map((entry) => entry.speciesId)).size !== state.collection.length)
      fail('Duplicate collection species');
    if (
      new Set(state.artworks.map((a) => `${a.speciesId}:${a.version}`)).size !==
      state.artworks.length
    )
      fail('Duplicate artwork version');
    for (const event of state.events)
      if (species.get(event.species.id)?.scientificName !== event.species.scientificName)
        fail('Evidence taxon mismatch');
    const revisions = new Map(
      state.events.map((event) => [
        event.id,
        {
          eventId: event.id,
          correctionId: null as string | null,
          speciesId: event.species.id,
          observedAt: event.observedAt,
        },
      ]),
    );
    for (const correction of state.corrections) {
      const previous = revisions.get(correction.eventId);
      if (!previous || !sameRevision(previous, correction.expected))
        fail('Correction history must be an unbroken append-only chain.');
      if (!species.has(correction.replacement.speciesId)) fail('Corrected species missing');
      revisions.set(correction.eventId, {
        eventId: correction.eventId,
        correctionId: correction.id,
        ...correction.replacement,
      });
    }
    for (const entry of [...state.collection, ...state.birds, ...state.artworks])
      if (!species.has(entry.speciesId)) fail('Referenced species missing');
    for (const bird of state.birds) {
      if (bird.artworkId && art.get(bird.artworkId)?.speciesId !== bird.speciesId)
        fail('Pinned artwork taxon mismatch');
      if (bird.originEventId && !state.events.some((event) => event.id === bird.originEventId))
        fail('Origin event missing');
      if (bird.lifecycle === 'permanent' && bird.expiresAt !== null)
        fail('Permanent birds cannot expire');
      if (bird.lifecycle !== 'permanent' && bird.expiresAt === null)
        fail('Temporary birds require expiry');
    }
  });
export type Species = z.infer<typeof speciesSchema>;
export type IdentificationEvent = z.infer<typeof identificationSchema>;
export type ImportEvent = z.infer<typeof importEventSchema>;
export type Artwork = z.infer<typeof artworkSchema>;
export type BirdInstance = z.infer<typeof birdInstanceSchema>;
export type CollectionEntry = z.infer<typeof collectionEntrySchema>;
export type Preferences = z.infer<typeof preferencesSchema>;
export type YardData = z.infer<typeof yardDataSchema>;
export const findingSchema = z
  .object({
    id: z.string().min(1).max(168),
    speciesId: idSchema,
    eventIds: z.array(idSchema).min(1),
    evidenceCount: z.number().int().positive().max(Number.MAX_SAFE_INTEGER),
    firstObservedAt: timestampSchema.nullable(),
    lastObservedAt: timestampSchema.nullable(),
    sourceKinds: z.array(sourceSchema.shape.kind).min(1),
    hasUnknownTime: z.boolean(),
  })
  .strict();
export type Finding = z.infer<typeof findingSchema>;
const snapshotProjectionSchema = z
  .object({
    findings: z.array(findingSchema),
    effectiveEvidence: z.array(effectiveEvidenceSchema),
  })
  .strict();
export type YardSnapshot = YardData & z.infer<typeof snapshotProjectionSchema>;
export const emptyYard = (): YardData => ({
  version: 2,
  species: [],
  events: [],
  corrections: [],
  collection: [],
  birds: [],
  artworks: [],
  preferences: defaultPreferences(),
  environment: defaultEnvironment(),
});

export function sourceEventKey(event: Pick<IdentificationEvent, 'source'>): string {
  return JSON.stringify([
    event.source.kind,
    event.source.provider ?? '',
    event.source.sourceEventId,
  ]);
}

/** Object key order does not change evidence identity. Array order remains significant. */
export function canonicalJson(value: unknown): string {
  if (Array.isArray(value)) return `[${value.map(canonicalJson).join(',')}]`;
  if (value && typeof value === 'object')
    return `{${Object.keys(value)
      .filter((key) => (value as Record<string, unknown>)[key] !== undefined)
      .sort()
      .map(
        (key) => `${JSON.stringify(key)}:${canonicalJson((value as Record<string, unknown>)[key])}`,
      )
      .join(',')}}`;
  return JSON.stringify(value) ?? 'null';
}

/** Ingestion time belongs to this server, not the submitted evidence payload. */
export function evidenceFingerprint(event: IdentificationEvent | ImportEvent): string {
  const evidence = Object.fromEntries(
    Object.entries(event).filter(([key]) => key !== 'ingestedAt'),
  );
  return canonicalJson(evidence);
}

export function effectiveEvidenceOf(
  data: Pick<YardData, 'events' | 'corrections'>,
): EffectiveEvidence[] {
  const latest = new Map(data.corrections.map((correction) => [correction.eventId, correction]));
  return data.events.map((event) => {
    const correction = latest.get(event.id);
    return {
      eventId: event.id,
      correctionId: correction?.id ?? null,
      ...(correction?.replacement ?? { speciesId: event.species.id, observedAt: event.observedAt }),
    };
  });
}

export function snapshotOf(data: YardData, now: string): YardSnapshot {
  const groups = new Map<string, Finding>();
  const effectiveEvidence = effectiveEvidenceOf(data);
  const effective = new Map(effectiveEvidence.map((entry) => [entry.eventId, entry]));
  for (const event of data.events) {
    const value = effective.get(event.id)!;
    const finding = groups.get(value.speciesId) ?? {
      id: `finding:${value.speciesId}`,
      speciesId: value.speciesId,
      eventIds: [],
      evidenceCount: 0,
      firstObservedAt: null,
      lastObservedAt: null,
      sourceKinds: [],
      hasUnknownTime: false,
    };
    finding.eventIds.push(event.id);
    finding.evidenceCount++;
    if (!finding.sourceKinds.includes(event.source.kind))
      finding.sourceKinds.push(event.source.kind);
    if (value.observedAt === null) finding.hasUnknownTime = true;
    else {
      if (
        !finding.firstObservedAt ||
        Date.parse(value.observedAt) < Date.parse(finding.firstObservedAt)
      )
        finding.firstObservedAt = value.observedAt;
      if (
        !finding.lastObservedAt ||
        Date.parse(value.observedAt) > Date.parse(finding.lastObservedAt)
      )
        finding.lastObservedAt = value.observedAt;
    }
    groups.set(value.speciesId, finding);
  }
  return {
    ...data,
    effectiveEvidence,
    birds: data.birds.map((bird) =>
      bird.lifecycle === 'temporary' && Date.parse(bird.expiresAt!) <= Date.parse(now)
        ? { ...bird, lifecycle: 'expired' as const }
        : bird,
    ),
    findings: [...groups.values()],
  };
}

/** Read boundary also checks derived history so malformed counts cannot replace confirmed UI state. */
export const yardSnapshotSchema = yardDataSchema
  .innerType()
  .extend({
    ...snapshotProjectionSchema.shape,
    environment: environmentSchema,
    corrections: yardDataSchema.innerType().shape.corrections.removeDefault(),
    preferences: preferencesSchema
      .extend({
        scenePin: preferencesSchema.shape.scenePin.removeDefault(),
        regionPreference: preferencesSchema.shape.regionPreference.removeDefault(),
      })
      .strict(),
  })
  .strict()
  .superRefine((snapshot, context) => {
    const { findings, effectiveEvidence, ...raw } = snapshot;
    const parsed = yardDataSchema.safeParse(raw);
    if (!parsed.success) {
      for (const issue of parsed.error.issues) context.addIssue(issue);
      return;
    }
    const expected = snapshotOf(parsed.data, '1970-01-01T00:00:00.000Z');
    if (canonicalJson(findings) !== canonicalJson(expected.findings))
      context.addIssue({
        code: 'custom',
        path: ['findings'],
        message: 'Findings do not match saved evidence.',
      });
    if (canonicalJson(effectiveEvidence) !== canonicalJson(expected.effectiveEvidence))
      context.addIssue({
        code: 'custom',
        path: ['effectiveEvidence'],
        message: 'Effective evidence does not match correction history.',
      });
  });

export const backupSchema = z
  .object({
    format: z.literal('chirpneighbors-yard'),
    version: z.literal(2),
    exportedAt: timestampSchema,
    data: yardDataSchema,
  })
  .strict();
export type YardBackup = z.infer<typeof backupSchema>;

export const displayCatalog = {
  ...starterSpeciesCatalog,
  'cn-species-erithacus-rubecula': {
    commonName: 'European Robin',
    scientificName: 'Erithacus rubecula',
    catalogKey: 'fixture-robin',
  },
  'cn-species-passer-domesticus': {
    commonName: 'House Sparrow',
    scientificName: 'Passer domesticus',
    catalogKey: 'fixture-sparrow',
  },
  'cn-species-cyanocitta-cristata': {
    commonName: 'Blue Jay',
    scientificName: 'Cyanocitta cristata',
    catalogKey: 'fixture-bluejay',
  },
} as const;

/** Imported taxon IDs may name Object.prototype properties; only own catalog entries are trusted. */
export function catalogEntry(speciesId: string) {
  return Object.hasOwn(displayCatalog, speciesId)
    ? displayCatalog[speciesId as keyof typeof displayCatalog]
    : undefined;
}
export function catalogThumbnail(speciesId: string): string {
  const entry = catalogEntry(speciesId);
  return entry?.catalogKey
    ? `/fixtures/${entry.catalogKey.slice('fixture-'.length)}.svg`
    : '/placeholder.svg';
}

/** Only already known owner taxa and application catalog IDs; no provider taxonomy inference. */
export function availableSpecies(data: Pick<YardData, 'species'>): Species[] {
  const choices = data.species.map(({ id, commonName, scientificName }) => ({
    id,
    commonName,
    scientificName,
  }));
  for (const [id, species] of Object.entries(displayCatalog)) {
    if (
      !choices.some(
        (entry) =>
          entry.id === id ||
          entry.scientificName.toLowerCase() === species.scientificName.toLowerCase(),
      )
    )
      choices.push({ id, commonName: species.commonName, scientificName: species.scientificName });
  }
  return choices;
}

export const publicYardProjectionSchema = z
  .object({
    version: z.literal(1),
    viewOnly: z.literal(true),
    scene: sceneSettingSchema,
    palette: preferencesSchema.shape.palette,
    birds: z.array(
      z
        .object({
          displayKey: z.string().regex(/^bird-[1-9][0-9]*$/),
          commonName: speciesSchema.shape.commonName,
          scientificName: speciesSchema.shape.scientificName.nullable(),
          catalogKey: artworkObjectSchema.shape.catalogKey.unwrap().nullable(),
        })
        .strict(),
    ),
  })
  .strict();

/** Public responses use trusted labels. User-entered species names can themselves contain private text. */
export function publicYardProjection(
  snapshot: YardSnapshot,
): z.infer<typeof publicYardProjectionSchema> {
  return {
    version: 1 as const,
    viewOnly: true as const,
    scene: resolveScene(snapshot.preferences.scene, snapshot.preferences.scenePin).manifest
      .publicSceneId,
    palette: snapshot.preferences.palette,
    birds: snapshot.birds
      .filter((bird) => bird.lifecycle !== 'expired')
      .map((bird, index) => {
        const species = snapshot.species.find((s) => s.id === bird.speciesId)!;
        const asset = snapshot.artworks.find(
          (art) => art.id === bird.artworkId && art.speciesId === bird.speciesId,
        );
        const entry = catalogEntry(species.id);
        const trusted =
          entry && entry.scientificName.toLowerCase() === species.scientificName.toLowerCase()
            ? entry
            : null;
        return {
          displayKey: `bird-${index + 1}`,
          commonName: trusted?.commonName ?? 'Bird',
          scientificName: trusted?.scientificName ?? null,
          catalogKey:
            trusted?.catalogKey && asset?.catalogKey === trusted.catalogKey
              ? trusted.catalogKey
              : null,
        };
      }),
  };
}
