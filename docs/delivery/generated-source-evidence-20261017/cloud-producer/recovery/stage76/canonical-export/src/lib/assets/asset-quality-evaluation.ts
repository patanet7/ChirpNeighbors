import { z } from 'zod';
import { idSchema } from '../domain/primitives.ts';
import { canonicalJson } from '../pipeline/canonical-json.ts';
import type { ActorMotion } from '../engine/actor-motion.ts';
import { behaviorDecisionTraceSchema } from '../engine/ontology-contracts.ts';
import { animationStates, speciesManifestSchema } from './manifest.ts';
import { commonClipNames } from './common-motion.ts';
import { contactSchema } from './manifest-v3.ts';

export const ASSET_QUALITY_LIMITS = Object.freeze({
  bytes: 65_536,
  findings: 256,
  evidence: 64,
  tools: 16,
  mappings: 128,
});
const categories = [
  'species-identity-anatomy',
  'pose-action-phase',
  'support-contact',
  'registration-centering',
  'relative-scale',
  'palette-style',
  'transparency-noise',
  'temporal-stability',
  'technical-budgets',
  'runtime-adoption',
] as const;
const ruleIds = [
  'identity-anatomy-mismatch',
  'pose-action-mismatch',
  'support-contact-mismatch',
  'anchor-registration-drift',
  'relative-scale-mismatch',
  'palette-style-mismatch',
  'transparency-noise',
  'temporal-instability',
  'technical-budget-exceeded',
  'runtime-adoption-unverified',
] as const;
const rules: Record<(typeof ruleIds)[number], (typeof categories)[number]> = {
  'identity-anatomy-mismatch': 'species-identity-anatomy',
  'pose-action-mismatch': 'pose-action-phase',
  'support-contact-mismatch': 'support-contact',
  'anchor-registration-drift': 'registration-centering',
  'relative-scale-mismatch': 'relative-scale',
  'palette-style-mismatch': 'palette-style',
  'transparency-noise': 'transparency-noise',
  'temporal-instability': 'temporal-stability',
  'technical-budget-exceeded': 'technical-budgets',
  'runtime-adoption-unverified': 'runtime-adoption',
};
/** Provisional evaluation-rule IDs only; canonical source labels retain their own meaning. */
export const ASSET_QUALITY_CATALOG_V1 = Object.freeze({
  authority: 'asset-quality-evaluation-v1' as const,
  version: 1 as const,
  status: 'provisional-advisory' as const,
  categories: Object.freeze(categories),
  rules: Object.freeze(rules),
});
const sha = z.string().regex(/^[a-f0-9]{64}$/);
const text = z.string().min(1).max(160);
const counter = z.number().int().safe().nonnegative();
const clipId = z.enum([...animationStates, ...commonClipNames]);
const motionPhases = [
  'grounded',
  'walk',
  'hop',
  'takeoff',
  'flight',
  'landing',
] as const satisfies readonly ActorMotion['phase'][];
const slotId = behaviorDecisionTraceSchema.innerType().shape.selected.shape.slotId.unwrap();
// Reference to the sole canonical source-defect namespace, not a second catalog.
const canonicalSourceLabelIds = [
  'visual.alpha-matte',
  'visual.crop-truncation',
  'visual.display-density',
  'fidelity.subject-structure',
  'registration.pivot',
  'registration.scale',
  'registration.anchor-empty',
  'registration.contact-appearance',
  'layer.seam',
  'layer.ownership',
  'state.art-missing',
  'motion.parts-unqualified',
  'media.constraint',
  'provenance.incomplete',
  'physics.unreviewed',
  'interaction.unreviewed',
  'runtime.unadmitted',
] as const;
export const CANONICAL_SOURCE_ART_LABEL_REFERENCE_V1 = Object.freeze({
  catalogId: 'shared-source-art-defect-label-contract' as const,
  version: '1' as const,
  canonicalRevision: 'd104afbaf6949d71d24768a577f4eb9d8ef709c3',
  sha256: 'b78e048b84bff2a99da153c6b3636bb5683b4d0ab015d8b68fa3745b39a56996',
  path: 'docs/art/asset-defect-labels-v1.json',
  labels: Object.freeze(canonicalSourceLabelIds),
});
/** Conservative bird-evaluation classification only; never changes a source label's meaning.
 * Null means no faithful existing evaluation rule: retain the source as unclassified.
 */
export const ASSET_QUALITY_SOURCE_LABEL_CLASSIFICATIONS_V1 = Object.freeze({
  'visual.alpha-matte': 'transparency-noise',
  'visual.crop-truncation': null,
  'visual.display-density': null,
  'fidelity.subject-structure': 'identity-anatomy-mismatch',
  'registration.pivot': 'anchor-registration-drift',
  'registration.scale': 'relative-scale-mismatch',
  'registration.anchor-empty': null,
  'registration.contact-appearance': null,
  'layer.seam': null,
  'layer.ownership': null,
  'state.art-missing': null,
  'motion.parts-unqualified': null,
  'media.constraint': null,
  'provenance.incomplete': null,
  'physics.unreviewed': null,
  'interaction.unreviewed': null,
  'runtime.unadmitted': 'runtime-adoption-unverified',
} as const satisfies Record<
  (typeof canonicalSourceLabelIds)[number],
  (typeof ruleIds)[number] | null
>);
const retainedRecordSchema = z
  .object({
    json: z.string().min(1).max(16_384),
    sha256: sha,
    applicability: z.enum(['unverified', 'subject-source']),
  })
  .strict();
const canonicalRecordRequirements = [
  'asset_id',
  'variant_id',
  'candidate_revision',
  'source_sha256',
  'scope',
  'grade',
  'canonical_label',
  'finding_state',
  'reason',
  'evidence',
] as const;
function readCanonicalSourceRecord(json: string) {
  const value: unknown = JSON.parse(json);
  // Validate finite, depth-bounded JSON without spreading or rewriting the original record.
  canonicalJson(value);
  const record = z.record(z.unknown()).parse(value);
  for (const key of canonicalRecordRequirements)
    if (!Object.hasOwn(record, key))
      throw Error('Canonical source record requirement is missing: ' + key);
  z.enum(canonicalSourceLabelIds).parse(record.canonical_label);
  z.enum([
    'static_visual',
    'registration',
    'media_preflight',
    'state_coverage',
    'wind_parts',
    'physical_geometry',
    'functional_fit',
    'runtime_admission',
    'rights_review',
  ]).parse(record.scope);
  z.enum(['pass', 'repair', 'blocked', 'reject']).parse(record.grade);
  z.enum([
    'observed',
    'not_detected_in_scope',
    'unknown',
    'not_applicable',
    'corrected_in_candidate',
  ]).parse(record.finding_state);
  sha.parse(record.source_sha256);
  return record;
}
const sourceLabelSchema = z
  .object({
    catalogId: idSchema.nullable(),
    catalogVersion: text.nullable(),
    rawLabel: z.string().min(1).max(256),
    originalRecord: retainedRecordSchema.optional(),
  })
  .strict()
  .superRefine((source, ctx) => {
    const fail = (message: string) => ctx.addIssue({ code: 'custom', message });
    if (source.catalogId === CANONICAL_SOURCE_ART_LABEL_REFERENCE_V1.catalogId) {
      if (
        source.catalogVersion !== '1' ||
        !canonicalSourceLabelIds.some((id) => id === source.rawLabel)
      )
        fail('Unknown canonical source label/version');
      if (!source.originalRecord) fail('Canonical source label requires retained original record');
      else {
        try {
          const record = readCanonicalSourceRecord(source.originalRecord.json);
          if (record.canonical_label !== source.rawLabel)
            fail('Canonical source label/record identity differs');
        } catch {
          fail('Invalid canonical source record JSON/requirements');
        }
      }
    } else if (source.originalRecord)
      fail('Retained canonical record requires its exact catalog identity');
  });
function sourceLabelIdentity(source: z.infer<typeof sourceLabelSchema>) {
  return canonicalJson({
    catalogId: source.catalogId,
    catalogVersion: source.catalogVersion,
    rawLabel: source.rawLabel,
  });
}
function allowedSourceRule(
  source: z.infer<typeof sourceLabelSchema>,
  rule: (typeof ruleIds)[number],
) {
  if (source.catalogId !== CANONICAL_SOURCE_ART_LABEL_REFERENCE_V1.catalogId) return true;
  const label = z.enum(canonicalSourceLabelIds).safeParse(source.rawLabel);
  return (
    label.success &&
    source.originalRecord?.applicability === 'subject-source' &&
    ASSET_QUALITY_SOURCE_LABEL_CLASSIFICATIONS_V1[label.data] === rule
  );
}
const mappingSchema = z
  .object({
    source: sourceLabelSchema,
    ruleId: z.enum(ruleIds),
    status: z.enum(['proposed', 'reviewed']),
    evidenceSha256: sha,
  })
  .strict();
const labelSchema = z.discriminatedUnion('status', [
  z.object({ status: z.literal('unclassified'), source: sourceLabelSchema }).strict(),
  z
    .object({
      status: z.literal('mapped'),
      source: sourceLabelSchema,
      ruleId: z.enum(ruleIds),
      mappingStatus: z.enum(['proposed', 'reviewed']),
      mappingEvidenceSha256: sha,
    })
    .strict(),
]);
const subjectSchema = z
  .object({
    assetId: idSchema,
    speciesId: idSchema,
    contentDigest: sha,
    sourcePngSha256: sha,
    rgbaSha256: sha,
    manifestSha256: sha,
    geometrySha256: sha.nullable(),
    canvas: z
      .object({
        width: z.number().int().min(1).max(4096),
        height: z.number().int().min(1).max(4096),
      })
      .strict(),
  })
  .strict();
const requirementSchema = z
  .object({
    sha256: sha,
    speciesId: idSchema,
    activity: z.enum(animationStates),
    motionPhase: z.enum(motionPhases),
    requestedClip: clipId,
    facing: z.enum(['right', 'mirrored-left']),
    recipe: z
      .object({ id: idSchema, version: counter.min(1), sha256: sha })
      .strict()
      .nullable(),
    support: z
      .object({
        sceneId: idSchema,
        sceneVersion: counter.min(1),
        objectId: idSchema,
        slotId,
        geometrySha256: sha,
      })
      .strict()
      .nullable(),
  })
  .strict();
const modelSchema = z
  .object({
    id: text,
    version: text,
    promptSha256: sha,
    configurationSha256: sha,
  })
  .strict();
const toolSchema = z
  .object({
    id: idSchema,
    kind: z.enum(['deterministic', 'cv', 'vl', 'human']),
    name: text,
    version: text,
    codeSha256: sha,
    configurationSha256: sha,
    model: modelSchema.nullable(),
  })
  .strict();
const evidenceSchema = z
  .object({
    id: idSchema,
    sha256: sha,
    kind: z.enum([
      'source',
      'configuration',
      'measurement',
      'diagnostic-overlay',
      'calibration',
      'rubric',
      'review',
      'mapping-review',
      'reviewed-contact',
    ]),
  })
  .strict();
const confidenceSchema = z
  .discriminatedUnion('kind', [
    z
      .object({
        kind: z.literal('calibrated'),
        value: z.number().finite().min(0).max(1),
        calibrationSha256: sha,
      })
      .strict(),
    z
      .object({
        kind: z.literal('ordinal'),
        level: z.enum(['low', 'medium', 'high']),
        rubricSha256: sha,
      })
      .strict(),
  ])
  .nullable();
const regionSchema = z
  .object({
    x: z.number().finite().min(0).max(4096),
    y: z.number().finite().min(0).max(4096),
    width: z.number().finite().positive().max(4096),
    height: z.number().finite().positive().max(4096),
  })
  .strict();
const findingStructure = z
  .object({
    id: idSchema,
    category: z.enum(categories),
    label: labelSchema,
    target: z
      .object({
        clip: clipId.nullable(),
        frame: z.number().int().min(0).max(255).nullable(),
        poseId: idSchema.nullable(),
        region: regionSchema.nullable(),
        contactKind: contactSchema.shape.kind.nullable(),
      })
      .strict(),
    knowledge: z.enum(['observed', 'measured', 'inferred', 'unknown']),
    verdict: z.enum(['pass', 'fail', 'held', 'unmeasured']),
    severity: z.enum(['critical', 'major', 'minor', 'note']).nullable(),
    confidence: confidenceSchema,
    toolId: idSchema,
    evidenceIds: z.array(idSchema).max(32),
    measurements: z
      .array(
        z
          .object({
            metricId: idSchema,
            value: z.number().finite().min(-1e12).max(1e12),
            unit: z.enum([
              'source-px',
              'world-unit',
              'css-px',
              'ms',
              'ticks',
              'bytes',
              'count',
              'ratio',
              'degrees',
            ]),
            tolerance: z.number().finite().min(0).max(1e12).nullable(),
          })
          .strict(),
      )
      .max(16),
    contactBasis: z.enum([
      'unavailable',
      'declared-only',
      'reviewed-reference',
      'synthetic-reference',
    ]),
    supersedes: z.array(idSchema).max(32),
    supersedesExternal: z
      .array(z.object({ reportId: idSchema, reportSha256: sha, findingId: idSchema }).strict())
      .max(32),
    repair: z
      .object({
        status: z.enum(['none', 'proposed', 'applied', 'rejected']),
        proposalSha256: sha.nullable(),
        resultSha256: sha.nullable(),
      })
      .strict(),
    review: z
      .object({
        status: z.enum(['unreviewed', 'accepted', 'rejected', 'needs-repair', 'blocked']),
        evidenceSha256: sha.nullable(),
      })
      .strict(),
  })
  .strict();
export const assetQualityFindingSchema = findingStructure.superRefine(intrinsicFinding);
const evaluationStructure = z
  .object({
    schemaVersion: z.literal(1),
    authority: z.literal('asset-quality-evaluation-v1'),
    advisoryOnly: z.literal(true),
    grantsAdmission: z.literal(false),
    reportId: idSchema,
    basis: z.enum(['synthetic-illustrative', 'source-bound']),
    subject: subjectSchema,
    requirement: requirementSchema,
    tools: z.array(toolSchema).min(1).max(ASSET_QUALITY_LIMITS.tools),
    evidence: z.array(evidenceSchema).min(1).max(ASSET_QUALITY_LIMITS.evidence),
    findings: z
      .array(findingStructure.superRefine(intrinsicFinding))
      .min(1)
      .max(ASSET_QUALITY_LIMITS.findings),
  })
  .strict();
function intrinsicFinding(f: z.infer<typeof findingStructure>, c: z.RefinementCtx) {
  const fail = (message: string) => c.addIssue({ code: 'custom', message });
  if ((f.label.source.catalogId === null) !== (f.label.source.catalogVersion === null))
    fail('Source catalog identity and version must be present together');
  if (
    f.knowledge === 'unknown' &&
    (!['held', 'unmeasured'].includes(f.verdict) ||
      f.severity !== null ||
      f.confidence !== null ||
      f.measurements.length)
  )
    fail('Unknown evidence cannot claim failure, success, severity, confidence or measurement');
  if (f.knowledge !== 'unknown' && !f.evidenceIds.length) fail('Known findings require evidence');
  if (f.knowledge === 'measured' && !f.measurements.length)
    fail('Measured findings require finite measurements');
  if (f.knowledge === 'observed' && f.measurements.length)
    fail('Numeric observations must use measured knowledge');
  if (f.verdict === 'fail' && f.severity === null) fail('Failure requires an independent severity');
  if (f.verdict === 'pass' && f.severity !== null && f.severity !== 'note')
    fail('Passing evidence cannot claim defect severity');
  if (
    f.target.clip === null &&
    (f.target.frame !== null ||
      f.target.poseId !== null ||
      f.target.region !== null ||
      f.target.contactKind !== null)
  )
    fail('Frame/pose/region/contact references require an actual clip');
  if (
    f.target.frame === null &&
    (f.target.poseId !== null || f.target.region !== null || f.target.contactKind !== null)
  )
    fail('Pose/region/contact references require an actual frame');
  if (
    new Set(f.evidenceIds).size !== f.evidenceIds.length ||
    new Set(f.supersedes).size !== f.supersedes.length ||
    new Set(f.measurements.map((m) => m.metricId)).size !== f.measurements.length
  )
    fail('Finding references and measurement IDs must be unique');
  if (f.supersedes.includes(f.id)) fail('A finding cannot supersede itself');
  if (
    f.repair.status === 'none'
      ? f.repair.proposalSha256 !== null || f.repair.resultSha256 !== null
      : f.repair.proposalSha256 === null ||
        (f.repair.status === 'applied'
          ? f.repair.resultSha256 === null
          : f.repair.resultSha256 !== null)
  )
    fail('Repair outcome must bind its immutable proposal and applicable result');
  if ((f.review.status === 'unreviewed') !== (f.review.evidenceSha256 === null))
    fail('Review outcome must bind its evidence without claiming admission');
}

function evaluationIssues(v: z.infer<typeof evaluationStructure>, c: z.RefinementCtx) {
  const fail = (message: string) => c.addIssue({ code: 'custom', message });
  try {
    if (new TextEncoder().encode(canonicalJson(v)).byteLength > ASSET_QUALITY_LIMITS.bytes)
      fail('Asset quality report exceeds byte bound');
  } catch {
    fail('Asset quality report exceeds finite JSON bounds');
  }
  const evidence = new Map(v.evidence.map((e) => [e.id, e]));
  const tools = new Map(v.tools.map((t) => [t.id, t]));
  const findings = new Map(v.findings.map((f) => [f.id, f]));
  if (
    evidence.size !== v.evidence.length ||
    tools.size !== v.tools.length ||
    findings.size !== v.findings.length
  )
    fail('Evidence, tool and finding identities must be unique');
  if (v.subject.speciesId !== v.requirement.speciesId)
    fail('Subject and requirement taxon binding differs');
  const has = (hash: string, kinds: readonly string[]) =>
    v.evidence.some((e) => e.sha256 === hash && kinds.includes(e.kind));
  if (!has(v.subject.sourcePngSha256, ['source']))
    fail('Subject source must be bound to source evidence');
  for (const t of v.tools) {
    if (!has(t.configurationSha256, ['configuration']))
      fail('Tool configuration evidence is missing');
    if (t.kind === 'vl' && t.model === null)
      fail('VL reports require exact model/prompt/config identity');
    if (
      t.model &&
      (!t.model.version.trim() ||
        /^(latest|auto|unknown|default|unversioned)$/i.test(t.model.version.trim()))
    )
      fail('Mutable or unknown model aliases are not version provenance');
  }
  const mapped = new Map<string, string>();
  for (const f of v.findings) {
    const t = tools.get(f.toolId);
    if (!t) fail('Finding tool reference is missing');
    if (
      (t?.kind === 'vl' || (t?.kind === 'cv' && t.model !== null)) &&
      !['unknown', 'inferred'].includes(f.knowledge)
    )
      fail('Model judgments are inferred, not observed measurements');
    if (f.evidenceIds.some((id) => !evidence.has(id)))
      fail('Finding evidence reference is missing');
    if (
      f.confidence?.kind === 'calibrated' &&
      !has(f.confidence.calibrationSha256, ['calibration'])
    )
      fail('Confidence calibration evidence is missing');
    if (f.confidence?.kind === 'ordinal' && !has(f.confidence.rubricSha256, ['rubric']))
      fail('Ordinal confidence rubric is missing');
    if (f.review.evidenceSha256 !== null && !has(f.review.evidenceSha256, ['review']))
      fail('Review evidence is missing');
    const original = f.label.source.originalRecord;
    if (original?.applicability === 'subject-source') {
      try {
        const record = readCanonicalSourceRecord(original.json);
        if (
          record.asset_id !== v.subject.assetId ||
          record.source_sha256 !== v.subject.sourcePngSha256
        )
          fail('Retained source record subject/source identity differs');
      } catch {
        fail('Invalid retained source record');
      }
    }
    if (f.label.status === 'mapped') {
      if (!allowedSourceRule(f.label.source, f.label.ruleId))
        fail('Canonical source classification is unverified or incompatible');
      if (rules[f.label.ruleId] !== f.category) fail('Rule/category binding differs');
      if (
        !has(
          f.label.mappingEvidenceSha256,
          f.label.mappingStatus === 'reviewed'
            ? ['mapping-review']
            : ['configuration', 'mapping-review'],
        )
      )
        fail('Explicit label mapping evidence is missing');
      const key = sourceLabelIdentity(f.label.source),
        signature = canonicalJson({
          ruleId: f.label.ruleId,
          status: f.label.mappingStatus,
          evidence: f.label.mappingEvidenceSha256,
        }),
        old = mapped.get(key);
      if (old && old !== signature) fail('Source label mapping collision');
      mapped.set(key, signature);
    }
    const region = f.target.region;
    if (
      region &&
      (region.x + region.width > v.subject.canvas.width ||
        region.y + region.height > v.subject.canvas.height)
    )
      fail('Source region exceeds exact canvas');
    if (f.contactBasis === 'synthetic-reference' && v.basis !== 'synthetic-illustrative')
      fail('Synthetic contact reference must remain synthetic');
    if (
      f.category === 'support-contact' &&
      ['pass', 'fail'].includes(f.verdict) &&
      (v.subject.geometrySha256 === null ||
        v.requirement.support === null ||
        f.target.clip === null ||
        f.target.frame === null ||
        f.target.contactKind === null ||
        (f.contactBasis !== 'reviewed-reference' &&
          !(f.contactBasis === 'synthetic-reference' && v.basis === 'synthetic-illustrative')))
    )
      fail(
        'Contact verdict requires exact geometry/support and reviewed or explicitly synthetic reference',
      );
    if (
      f.contactBasis === 'reviewed-reference' &&
      !f.evidenceIds.some((id) => evidence.get(id)?.kind === 'reviewed-contact')
    )
      fail('Reviewed contact reference evidence is missing');
    if (f.supersedes.some((id) => !findings.has(id)))
      fail('Local supersession reference is missing; external links require exact report digest');
    if (
      f.supersedesExternal.some((ref) => ref.reportId === v.reportId) ||
      new Set(f.supersedesExternal.map((ref) => canonicalJson(ref))).size !==
        f.supersedesExternal.length
    )
      fail('External supersession must have unique prior-report bindings');
  }
  const visited = new Set<string>(),
    active = new Set<string>();
  const visit = (id: string): boolean => {
    if (active.has(id)) return false;
    if (visited.has(id)) return true;
    active.add(id);
    for (const prior of findings.get(id)?.supersedes ?? []) if (!visit(prior)) return false;
    active.delete(id);
    visited.add(id);
    return true;
  };
  if (v.findings.some((f) => !visit(f.id))) fail('Supersession graph is cyclic');
}
export const assetQualityEvaluationSchema = evaluationStructure.superRefine(evaluationIssues);

export type AssetQualityEvaluation = z.infer<typeof assetQualityEvaluationSchema>;
export type AssetQualityFinding = z.infer<typeof assetQualityFindingSchema>;
export type AssetQualityLabelMapping = z.infer<typeof mappingSchema>;
export type AssetQualitySourceLabel = z.infer<typeof sourceLabelSchema>;

export function resolveAssetQualitySourceLabel(source: unknown, mappings: unknown = []) {
  const label = sourceLabelSchema.parse(source);
  const entries = z.array(mappingSchema).max(ASSET_QUALITY_LIMITS.mappings).parse(mappings);
  const keys = entries.map((entry) => sourceLabelIdentity(entry.source));
  if (new Set(keys).size !== keys.length) throw Error('Duplicate source label mapping collision');
  for (const entry of entries) {
    if ((entry.source.catalogId === null) !== (entry.source.catalogVersion === null))
      throw Error('Source catalog identity/version binding differs');
    if (!allowedSourceRule(entry.source, entry.ruleId))
      throw Error('Canonical source classification is unverified or incompatible');
  }
  if ((label.catalogId === null) !== (label.catalogVersion === null))
    throw Error('Source catalog identity/version binding differs');
  const selected = entries.find(
    (entry) => sourceLabelIdentity(entry.source) === sourceLabelIdentity(label),
  );
  if (selected && !allowedSourceRule(label, selected.ruleId))
    throw Error('Canonical source classification is unverified or incompatible');
  return labelSchema.parse(
    selected
      ? {
          status: 'mapped',
          source: label,
          ruleId: selected.ruleId,
          mappingStatus: selected.status,
          mappingEvidenceSha256: selected.evidenceSha256,
        }
      : { status: 'unclassified', source: label },
  );
}
/** Normalized migration seam only: the producer serializer is not asserted by this helper. */
export function retainCanonicalAssetDefectSourceLabel(
  originalJson: string,
  declaredSha256: string,
  applicability: 'unverified' | 'subject-source',
): AssetQualitySourceLabel {
  const record = readCanonicalSourceRecord(originalJson);
  return sourceLabelSchema.parse({
    catalogId: CANONICAL_SOURCE_ART_LABEL_REFERENCE_V1.catalogId,
    catalogVersion: CANONICAL_SOURCE_ART_LABEL_REFERENCE_V1.version,
    rawLabel: record.canonical_label,
    originalRecord: { json: originalJson, sha256: declaredSha256, applicability },
  });
}
export function serializeAssetQualityEvaluation(input: unknown): string {
  const bytes = canonicalJson(input);
  if (new TextEncoder().encode(bytes).byteLength > ASSET_QUALITY_LIMITS.bytes)
    throw Error('Asset quality report exceeds byte bound');
  return canonicalJson(assetQualityEvaluationSchema.parse(input));
}
export function parseAssetQualityEvaluationJson(input: string): AssetQualityEvaluation {
  if (new TextEncoder().encode(input).byteLength > ASSET_QUALITY_LIMITS.bytes)
    throw Error('Asset quality report exceeds byte bound');
  return assetQualityEvaluationSchema.parse(JSON.parse(input));
}
/** Trusted consumer context, never authority supplied by the submitted report.
 * Each coverage entry explicitly covers the Cartesian product of its lists.
 * A null pose matches only an unspecified pose; it is not a wildcard.
 * A null region covers the whole source canvas; otherwise findings must be contained.
 */
export const assetQualityReviewedContactProofSchema = z
  .object({
    sha256: sha,
    subject: subjectSchema,
    requirement: requirementSchema,
    coverage: z
      .array(
        z
          .object({
            clip: clipId,
            frames: z.array(z.number().int().min(0).max(255)).min(1).max(256),
            poseIds: z.array(idSchema.nullable()).min(1).max(256),
            contactKinds: z.array(contactSchema.shape.kind).min(1).max(4),
            region: regionSchema.nullable(),
          })
          .strict(),
      )
      .min(1)
      .max(32),
  })
  .strict()
  .superRefine((proof, ctx) => {
    const fail = (message: string) => ctx.addIssue({ code: 'custom', message });
    if (proof.subject.geometrySha256 === null || proof.requirement.support === null)
      fail('Reviewed contact scope requires exact subject and support geometry');
    for (const scope of proof.coverage) {
      for (const values of [scope.frames, scope.poseIds, scope.contactKinds])
        if (new Set<string | number | null>(values).size !== values.length)
          fail('Contact scope coverage contains duplicates');
      const region = scope.region;
      if (
        region &&
        (region.x + region.width > proof.subject.canvas.width ||
          region.y + region.height > proof.subject.canvas.height)
      )
        fail('Contact scope region exceeds source canvas');
    }
  });
export type AssetQualityReviewedContactProof = z.infer<
  typeof assetQualityReviewedContactProofSchema
>;

function contactProofCovers(
  proof: AssetQualityReviewedContactProof,
  report: AssetQualityEvaluation,
  target: AssetQualityFinding['target'],
): boolean {
  if (
    canonicalJson(proof.subject) !== canonicalJson(report.subject) ||
    canonicalJson(proof.requirement) !== canonicalJson(report.requirement)
  )
    return false;
  return proof.coverage.some((scope) => {
    if (
      target.clip !== scope.clip ||
      target.frame === null ||
      !scope.frames.includes(target.frame) ||
      !scope.poseIds.includes(target.poseId) ||
      target.contactKind === null ||
      !scope.contactKinds.includes(target.contactKind)
    )
      return false;
    if (scope.region === null) return true;
    const region = target.region;
    return (
      region !== null &&
      region.x >= scope.region.x &&
      region.y >= scope.region.y &&
      region.x + region.width <= scope.region.x + scope.region.width &&
      region.y + region.height <= scope.region.y + scope.region.height
    );
  });
}
const bindingSchema = z
  .object({
    subject: subjectSchema,
    requirement: requirementSchema,
    manifest: speciesManifestSchema,
    reviewedContactProofs: z.array(assetQualityReviewedContactProofSchema).max(64),
    sourceRecords: z.array(retainedRecordSchema.pick({ sha256: true, json: true })).max(64),
  })
  .strict();
export type AssetQualityEvaluationBinding = z.infer<typeof bindingSchema>;
export function validateAssetQualityEvaluation(
  input: unknown,
  binding: unknown,
): AssetQualityEvaluation {
  const report = parseAssetQualityEvaluationJson(serializeAssetQualityEvaluation(input));
  const expected = bindingSchema.parse(binding);
  if (canonicalJson(expected.subject) !== canonicalJson(report.subject))
    throw Error('Subject source binding differs');
  if (canonicalJson(expected.requirement) !== canonicalJson(report.requirement))
    throw Error('Requirement binding differs');
  const manifest = expected.manifest;
  if (
    manifest.speciesId !== report.subject.speciesId ||
    manifest.canvas.width !== report.subject.canvas.width ||
    manifest.canvas.height !== report.subject.canvas.height
  )
    throw Error('Manifest subject/canvas binding differs');
  if (report.basis === 'source-bound' && manifest.fixture)
    throw Error('Fixture sources must remain synthetic illustrative evidence');
  for (const f of report.findings) {
    const target = f.target;
    const original = f.label.source.originalRecord;
    if (
      original?.applicability === 'subject-source' &&
      !expected.sourceRecords.some(
        (record) => record.sha256 === original.sha256 && record.json === original.json,
      )
    )
      throw Error('Retained source record hash/text binding differs');

    if (
      f.contactBasis === 'reviewed-reference' &&
      !f.evidenceIds.some((id) => {
        const evidence = report.evidence.find((e) => e.id === id);
        return (
          evidence?.kind === 'reviewed-contact' &&
          expected.reviewedContactProofs.some(
            (proof) =>
              proof.sha256 === evidence.sha256 && contactProofCovers(proof, report, target),
          )
        );
      })
    )
      throw Error('Reviewed contact proof scope/source binding differs');
    if (target.clip === null) continue;
    const action = animationStates.find((name) => name === target.clip);
    const common = commonClipNames.find((name) => name === target.clip);
    if (action && manifest.schemaVersion === 2) {
      const clip = manifest.clips[action];
      if (!clip) throw Error('Actual clip is missing; fallback is not coverage');
      if (target.frame !== null && !clip.frames.includes(target.frame))
        throw Error('Actual clip/frame binding differs');
      if (target.poseId !== null) throw Error('Legacy source has no pose identity');
      if (target.contactKind !== null && f.contactBasis === 'declared-only')
        throw Error('Legacy source has no declared contact');
    } else {
      const clip =
        common && manifest.schemaVersion === 6
          ? manifest.commonMotion.clips[common]
          : action && manifest.schemaVersion !== 2
            ? manifest.clips[action]
            : undefined;
      if (!clip) throw Error('Actual clip is missing; fallback is not coverage');
      const poses = clip.poses.filter(
        (p) =>
          (target.frame === null || p.frame === target.frame) &&
          (target.poseId === null || p.poseId === target.poseId),
      );
      if (!poses.length) throw Error('Actual frame/pose binding differs');
      if (
        target.contactKind !== null &&
        f.contactBasis === 'declared-only' &&
        (poses.length !== 1 ||
          !poses[0]!.contacts.some((contact) => contact.kind === target.contactKind))
      )
        throw Error('Exact declared contact/pose binding differs');
    }
  }
  return report;
}
