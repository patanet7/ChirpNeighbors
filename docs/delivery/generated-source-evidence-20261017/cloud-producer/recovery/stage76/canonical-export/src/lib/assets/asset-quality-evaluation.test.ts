import { schemaRecord } from '../../../scripts/contract-tools/schema-tools.ts';
import Ajv from 'ajv';
import { zodToJsonSchema } from 'zod-to-json-schema';
import { readFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
import canonicalCatalog from '../../../contracts/fixtures/asset-defect-labels-v1.canonical.json';
import { describe, expect, it } from 'vitest';
import examples from '../../../contracts/fixtures/asset-quality-evaluation-v1.synthetic.json';
import {
  ASSET_QUALITY_CATALOG_V1,
  CANONICAL_SOURCE_ART_LABEL_REFERENCE_V1,
  ASSET_QUALITY_SOURCE_LABEL_CLASSIFICATIONS_V1,
  retainCanonicalAssetDefectSourceLabel,
  assetQualityEvaluationSchema,
  parseAssetQualityEvaluationJson,
  resolveAssetQualitySourceLabel,
  serializeAssetQualityEvaluation,
  validateAssetQualityEvaluation,
  type AssetQualityEvaluation,
  type AssetQualityReviewedContactProof,
} from './asset-quality-evaluation';
import { fixtureManifest } from './fixtures';
import { speciesManifestSchema, sampleClip } from './manifest';

const crow = () => assetQualityEvaluationSchema.parse(examples.crow);
const bath = () => assetQualityEvaluationSchema.parse(examples.bath);
const change = (mutate: (report: AssetQualityEvaluation) => void) => {
  const report = crow();
  mutate(report);
  return report;
};
function binding(report = crow()) {
  return {
    subject: report.subject,
    requirement: report.requirement,
    manifest: fixtureManifest(report.subject.speciesId, true),
    reviewedContactProofs: [],
    sourceRecords: [],
  };
}

function reviewedReport() {
  const report = bath(),
    f = report.findings[0]!;
  report.subject.geometrySha256 = '6'.repeat(64);
  f.knowledge = 'measured';
  f.verdict = 'pass';
  f.contactBasis = 'reviewed-reference';
  f.target.contactKind = 'left-foot';
  f.measurements = [
    { metricId: 'external-contact-error', value: 0, unit: 'world-unit', tolerance: 1 },
  ];
  f.evidenceIds = ['contact-reference'];
  report.evidence.push({
    id: 'contact-reference',
    kind: 'reviewed-contact',
    sha256: '9'.repeat(64),
  });
  return report;
}
// Synthetic trusted-context fixture. Production consumers must load these independently.
function proofFor(report: AssetQualityEvaluation): AssetQualityReviewedContactProof {
  return {
    sha256: '9'.repeat(64),
    subject: structuredClone(report.subject),
    requirement: structuredClone(report.requirement),
    coverage: [
      { clip: 'idle', frames: [0], poseIds: [null], contactKinds: ['left-foot'], region: null },
    ],
  };
}
function contactBinding(report: AssetQualityEvaluation, proof = proofFor(report)) {
  return { ...binding(report), reviewedContactProofs: [proof] };
}
function originalSourceRecord(label = 'visual.alpha-matte') {
  return (
    JSON.stringify(
      {
        asset_id: crow().subject.assetId,
        variant_id: 'synthetic-right',
        candidate_revision: 1,
        source_sha256: crow().subject.sourcePngSha256,
        scope: 'static_visual',
        grade: 'blocked',
        canonical_label: label,
        finding_state: 'unknown',
        reason: 'SYNTHETIC retained source-only review',
        evidence: [{ source: 'SYNTHETIC', region: null }],
        original_extra: { unchanged: true },
      },
      null,
      2,
    ) + '\n'
  );
}
describe('versioned advisory asset quality evaluation', () => {
  it('keeps synthetic Crow inference distinct from unknown bath contact and admission', () => {
    expect(crow().findings[0]?.knowledge).toBe('inferred');
    expect(bath().findings[0]).toMatchObject({
      knowledge: 'unknown',
      verdict: 'unmeasured',
      severity: null,
      confidence: null,
    });
    expect(crow()).toMatchObject({ basis: 'synthetic-illustrative', grantsAdmission: false });
    expect(ASSET_QUALITY_CATALOG_V1.categories).toHaveLength(10);
    expect(Object.isFrozen(ASSET_QUALITY_CATALOG_V1.rules)).toBe(true);
  });
  it('serializes canonical lossless JSON and never silently accepts undefined or cyclic input', () => {
    const encoded = serializeAssetQualityEvaluation(crow());
    expect(serializeAssetQualityEvaluation(parseAssetQualityEvaluationJson(encoded))).toBe(encoded);
    expect(parseAssetQualityEvaluationJson(encoded)).toEqual(crow());
    expect(() =>
      serializeAssetQualityEvaluation({ ...examples.crow, unexpected: undefined }),
    ).toThrow();
    const cyclic: { cycle?: unknown } = {};
    cyclic.cycle = cyclic;
    expect(() => serializeAssetQualityEvaluation(cyclic)).toThrow();
  });
  it.each([
    { ...examples.crow, schemaVersion: 2 },
    { ...examples.crow, authority: 'another-authority' },
    { ...examples.crow, grantsAdmission: true },
    { ...examples.crow, approved: true },
    { ...examples.crow, advisoryOnly: false },
  ])('rejects changed authority/versions/approval fields', (input) => {
    expect(assetQualityEvaluationSchema.safeParse(input).success).toBe(false);
  });
  it('rejects oversized JSON before decoding and enforces serialized byte bounds', () => {
    expect(() => parseAssetQualityEvaluationJson(' '.repeat(65537))).toThrow(/bound|large/i);
    expect(() => parseAssetQualityEvaluationJson('{')).toThrow();
    const report = crow();
    report.findings = Array.from({ length: 257 }, () => report.findings[0]!);
    expect(() => serializeAssetQualityEvaluation(report)).toThrow();
  });
  it('rejects unknown rules, category mismatches and unknown contact vocabulary', () => {
    const report = crow(),
      first = report.findings[0]!;
    expect(
      assetQualityEvaluationSchema.safeParse({
        ...report,
        findings: [{ ...first, label: { ...first.label, ruleId: 'ANIM-AUTHORING-COMPARE-1' } }],
      }).success,
    ).toBe(false);
    expect(
      assetQualityEvaluationSchema.safeParse(
        change((r) => {
          r.findings[0]!.category = 'palette-style';
        }),
      ).success,
    ).toBe(false);
    expect(
      assetQualityEvaluationSchema.safeParse({
        ...report,
        findings: [{ ...first, target: { ...first.target, contactKind: 'beak' } }],
      }).success,
    ).toBe(false);
  });
  it('preserves unclassified source labels and maps only exact explicit source identities', () => {
    const source = { catalogId: 'producer', catalogVersion: '1', rawLabel: 'Ground REST ?' };
    expect(resolveAssetQualitySourceLabel(source)).toEqual({ status: 'unclassified', source });
    const mapping = {
      source,
      ruleId: 'pose-action-mismatch' as const,
      status: 'proposed' as const,
      evidenceSha256: '7'.repeat(64),
    };
    expect(resolveAssetQualitySourceLabel(source, [mapping])).toMatchObject({
      status: 'mapped',
      ruleId: 'pose-action-mismatch',
      mappingStatus: 'proposed',
    });
    expect(
      resolveAssetQualitySourceLabel({ ...source, rawLabel: 'ground rest ?' }, [mapping]).status,
    ).toBe('unclassified');
    expect(() => resolveAssetQualitySourceLabel(source, [mapping, mapping])).toThrow(
      /collision|duplicate/i,
    );
    expect(() =>
      resolveAssetQualitySourceLabel(source, [{ ...mapping, ruleId: 'unregistered' }]),
    ).toThrow();
  });
  it('rejects unknown canonical source codes instead of admitting a second defect namespace', () => {
    expect(() =>
      resolveAssetQualitySourceLabel({
        catalogId: 'shared-source-art-defect-label-contract',
        catalogVersion: '1',
        rawLabel: 'invented.source-defect',
      }),
    ).toThrow(/canonical|source.*label/i);
  });
  it('requires losslessly retained original records for canonical source labels', () => {
    const report = crow();
    report.findings[0]!.label = {
      status: 'unclassified',
      source: {
        catalogId: 'shared-source-art-defect-label-contract',
        catalogVersion: '1',
        rawLabel: 'visual.alpha-matte',
      },
    };
    expect(assetQualityEvaluationSchema.safeParse(report).success).toBe(false);
  });
  it('pins the sole canonical source catalog bytes and all 17 classifications', () => {
    const bytes = readFileSync(
      new URL('../../../contracts/fixtures/asset-defect-labels-v1.canonical.json', import.meta.url),
    );
    expect(createHash('sha256').update(bytes).digest('hex')).toBe(
      CANONICAL_SOURCE_ART_LABEL_REFERENCE_V1.sha256,
    );
    expect(canonicalCatalog.document_kind).toBe(CANONICAL_SOURCE_ART_LABEL_REFERENCE_V1.catalogId);
    expect(canonicalCatalog.version).toBe(1);
    expect(canonicalCatalog.labels.map((label) => label.id)).toEqual(
      CANONICAL_SOURCE_ART_LABEL_REFERENCE_V1.labels,
    );
    expect(Object.keys(ASSET_QUALITY_SOURCE_LABEL_CLASSIFICATIONS_V1)).toEqual(
      CANONICAL_SOURCE_ART_LABEL_REFERENCE_V1.labels,
    );
    for (const label of canonicalCatalog.labels) {
      const source = retainCanonicalAssetDefectSourceLabel(
        originalSourceRecord(label.id),
        'a'.repeat(64),
        'unverified',
      );
      expect(resolveAssetQualitySourceLabel(source)).toEqual({ status: 'unclassified', source });
    }
  });
  it('retains exact source scope/grade/state/reason/evidence and extra fields through report serialization', () => {
    const json = originalSourceRecord(),
      report = crow();
    const source = retainCanonicalAssetDefectSourceLabel(json, 'a'.repeat(64), 'subject-source');
    report.findings[0]!.label = resolveAssetQualitySourceLabel(source);
    const encoded = serializeAssetQualityEvaluation(report),
      decoded = parseAssetQualityEvaluationJson(encoded);
    expect(decoded.findings[0]!.label.source.originalRecord!.json).toBe(json);
    expect(decoded.findings[0]!.knowledge).toBe('inferred');
    expect(decoded.findings[0]!.verdict).toBe('fail'); // Not copied from source blocked/unknown.
    expect(decoded.grantsAdmission).toBe(false);
    expect(() => validateAssetQualityEvaluation(report, binding(report))).toThrow(
      /source record.*binding/i,
    );
    const trusted = { ...binding(report), sourceRecords: [{ json, sha256: 'a'.repeat(64) }] };
    expect(validateAssetQualityEvaluation(report, trusted)).toEqual(report);
    report.findings[0]!.label.source.originalRecord!.json += ' ';
    expect(() => validateAssetQualityEvaluation(report, trusted)).toThrow(
      /source record.*binding/i,
    );
    report.findings[0]!.label.source.originalRecord!.json = json;
    report.findings[0]!.label.source.originalRecord!.sha256 = 'b'.repeat(64);
    expect(() => validateAssetQualityEvaluation(report, trusted)).toThrow(
      /source record.*binding/i,
    );
  });
  it('requires claimed source records to match exact asset/source while retaining unverified history', () => {
    for (const field of ['asset_id', 'source_sha256']) {
      const json = originalSourceRecord().replace(
        field === 'asset_id' ? crow().subject.assetId : crow().subject.sourcePngSha256,
        field === 'asset_id' ? 'other-asset' : '0'.repeat(64),
      );
      const report = crow(),
        source = retainCanonicalAssetDefectSourceLabel(json, 'a'.repeat(64), 'subject-source');
      report.findings[0]!.label = resolveAssetQualitySourceLabel(source);
      expect(assetQualityEvaluationSchema.safeParse(report).success).toBe(false);
      report.findings[0]!.label.source.originalRecord!.applicability = 'unverified';
      expect(assetQualityEvaluationSchema.safeParse(report).success).toBe(true);
      expect(validateAssetQualityEvaluation(report, binding(report))).toEqual(report);
    }
  });
  it('maps only conservative classifications explicitly and keeps physical absence unclassified', () => {
    const source = retainCanonicalAssetDefectSourceLabel(
      originalSourceRecord(),
      'a'.repeat(64),
      'subject-source',
    );
    const mapping = {
      source,
      ruleId: 'transparency-noise' as const,
      status: 'proposed' as const,
      evidenceSha256: '7'.repeat(64),
    };
    const report = crow();
    report.findings[0]!.label = resolveAssetQualitySourceLabel(source, [mapping]);
    report.findings[0]!.category = 'transparency-noise';
    expect(assetQualityEvaluationSchema.safeParse(report).success).toBe(true);
    expect(() =>
      resolveAssetQualitySourceLabel(source, [{ ...mapping, ruleId: 'support-contact-mismatch' }]),
    ).toThrow(/classification/i);
    const historical = structuredClone(source);
    historical.originalRecord!.applicability = 'unverified';
    expect(() => resolveAssetQualitySourceLabel(historical, [mapping])).toThrow(/unverified/i);
    const unknownPhysical = retainCanonicalAssetDefectSourceLabel(
      originalSourceRecord('physics.unreviewed'),
      'a'.repeat(64),
      'subject-source',
    );
    expect(resolveAssetQualitySourceLabel(unknownPhysical).status).toBe('unclassified');
    expect(() =>
      resolveAssetQualitySourceLabel(unknownPhysical, [
        { ...mapping, source: unknownPhysical, ruleId: 'support-contact-mismatch' },
      ]),
    ).toThrow(/classification/i);
    const sameIdentityOtherRecord = structuredClone(source);
    sameIdentityOtherRecord.originalRecord!.json += ' ';
    expect(() =>
      resolveAssetQualitySourceLabel(source, [
        mapping,
        { ...mapping, source: sameIdentityOtherRecord },
      ]),
    ).toThrow(/collision/i);
  });
  it('rejects malformed/nonfinite/deep/missing and conflicting retained records without throwing from safeParse', () => {
    const json = originalSourceRecord();
    for (const invalid of [
      '{',
      '[]',
      json.replace('"unknown"', '"invented-state"'),
      json.replace('"candidate_revision": 1', '"candidate_revision": 1e999'),
      json.replace('"scope": "static_visual",', ''),
      '{"nested":' + '['.repeat(66) + '0' + ']'.repeat(66) + '}',
    ]) {
      const report = crow();
      report.findings[0]!.label = {
        status: 'unclassified',
        source: {
          catalogId: CANONICAL_SOURCE_ART_LABEL_REFERENCE_V1.catalogId,
          catalogVersion: '1',
          rawLabel: 'visual.alpha-matte',
          originalRecord: {
            json: invalid,
            sha256: 'a'.repeat(64),
            applicability: 'subject-source',
          },
        },
      };
      expect(assetQualityEvaluationSchema.safeParse(report).success).toBe(false);
    }
    const source = retainCanonicalAssetDefectSourceLabel(json, 'a'.repeat(64), 'unverified');
    expect(() =>
      resolveAssetQualitySourceLabel({ ...source, rawLabel: 'registration.scale' }),
    ).toThrow(/record identity/i);
    expect(() => resolveAssetQualitySourceLabel({ ...source, catalogVersion: '2' })).toThrow(
      /version/i,
    );
  });
  it('rejects whitespace-padded mutable model aliases while retaining exact pinned version text', () => {
    const report = crow();
    report.tools[0]!.model = {
      id: 'synthetic-model',
      version: ' latest ',
      promptSha256: '1'.repeat(64),
      configurationSha256: '2'.repeat(64),
    };
    expect(assetQualityEvaluationSchema.safeParse(report).success).toBe(false);
    report.tools[0]!.model.version = ' ';
    expect(assetQualityEvaluationSchema.safeParse(report).success).toBe(false);
    report.tools[0]!.model.version = ' snapshot-2026-10-18 ';
    expect(
      parseAssetQualityEvaluationJson(serializeAssetQualityEvaluation(report)).tools[0]!.model!
        .version,
    ).toBe(' snapshot-2026-10-18 ');
  });
  it('rejects within-report mapping collisions rather than inferring producer issue namespaces', () => {
    const report = crow(),
      other = structuredClone(report.findings[0]!);
    other.id = 'other';
    other.category = 'palette-style';
    other.label = {
      status: 'mapped',
      source: report.findings[0]!.label.source,
      ruleId: 'palette-style-mismatch',
      mappingStatus: 'proposed',
      mappingEvidenceSha256: '7'.repeat(64),
    };
    report.findings.push(other);
    expect(assetQualityEvaluationSchema.safeParse(report).success).toBe(false);
  });
  it.each(['findings', 'evidence', 'tools'] as const)(
    'rejects duplicate %s identities',
    (field) => {
      const report = crow();
      if (field === 'findings') report.findings.push(structuredClone(report.findings[0]!));
      if (field === 'evidence') report.evidence.push(structuredClone(report.evidence[0]!));
      if (field === 'tools') report.tools.push(structuredClone(report.tools[0]!));
      expect(assetQualityEvaluationSchema.safeParse(report).success).toBe(false);
    },
  );
  it('rejects missing evidence/tool/calibration/rubric references', () => {
    for (const mutate of [
      (r: AssetQualityEvaluation) => {
        r.findings[0]!.evidenceIds = ['absent'];
      },
      (r: AssetQualityEvaluation) => {
        r.findings[0]!.toolId = 'absent';
      },
      (r: AssetQualityEvaluation) => {
        r.findings[0]!.confidence = {
          kind: 'calibrated',
          value: 0.9,
          calibrationSha256: '0'.repeat(64),
        };
      },
      (r: AssetQualityEvaluation) => {
        r.findings[0]!.confidence = {
          kind: 'ordinal',
          level: 'high',
          rubricSha256: '0'.repeat(64),
        };
      },
    ])
      expect(assetQualityEvaluationSchema.safeParse(change(mutate)).success).toBe(false);
  });
  it('never turns missing evidence into failure, confidence or successful contact', () => {
    for (const mutate of [
      (r: AssetQualityEvaluation) => {
        r.findings[0]!.verdict = 'pass';
      },
      (r: AssetQualityEvaluation) => {
        r.findings[0]!.verdict = 'fail';
      },
      (r: AssetQualityEvaluation) => {
        r.findings[0]!.severity = 'critical';
      },
      (r: AssetQualityEvaluation) => {
        r.findings[0]!.confidence = {
          kind: 'ordinal',
          level: 'high',
          rubricSha256: '8'.repeat(64),
        };
      },
    ]) {
      const report = bath();
      mutate(report);
      expect(assetQualityEvaluationSchema.safeParse(report).success).toBe(false);
    }
  });
  it('requires measured values to be finite, typed and separate from confidence', () => {
    const measured = change((r) => {
      const f = r.findings[0]!;
      f.knowledge = 'measured';
      f.confidence = null;
      f.measurements = [
        { metricId: 'anchor-displacement', value: 5, unit: 'source-px', tolerance: 1 },
      ];
      r.tools[0]!.kind = 'deterministic';
    });
    expect(assetQualityEvaluationSchema.safeParse(measured).success).toBe(true);
    for (const value of [NaN, Infinity, -Infinity]) {
      const input = structuredClone(measured);
      input.findings[0]!.measurements[0]!.value = value;
      expect(assetQualityEvaluationSchema.safeParse(input).success).toBe(false);
    }
    measured.findings[0]!.measurements = [];
    expect(assetQualityEvaluationSchema.safeParse(measured).success).toBe(false);
  });
  it('requires model/prompt/version/config for VL and keeps its judgment inferred', () => {
    const report = crow();
    report.tools[0]!.kind = 'vl';
    expect(assetQualityEvaluationSchema.safeParse(report).success).toBe(false);
    report.tools[0]!.model = {
      id: 'synthetic-vl',
      version: 'snapshot-1',
      promptSha256: '1'.repeat(64),
      configurationSha256: '2'.repeat(64),
    };
    expect(assetQualityEvaluationSchema.safeParse(report).success).toBe(true);
    report.findings[0]!.knowledge = 'observed';
    expect(assetQualityEvaluationSchema.safeParse(report).success).toBe(false);
  });
  it('rejects destructive or unbound repair/review outcomes', () => {
    expect(
      assetQualityEvaluationSchema.safeParse(
        change((r) => {
          r.findings[0]!.repair.proposalSha256 = null;
        }),
      ).success,
    ).toBe(false);
    expect(
      assetQualityEvaluationSchema.safeParse(
        change((r) => {
          r.findings[0]!.review.status = 'accepted';
        }),
      ).success,
    ).toBe(false);
    expect(
      assetQualityEvaluationSchema.safeParse(
        change((r) => {
          r.findings[0]!.repair.resultSha256 = '1'.repeat(64);
        }),
      ).success,
    ).toBe(false);
  });
  it('rejects local supersession cycles and keeps external digest links immutable', () => {
    const report = crow(),
      f = report.findings[0]!;
    f.supersedes = [f.id];
    expect(assetQualityEvaluationSchema.safeParse(report).success).toBe(false);
    const second = structuredClone(f);
    second.id = 'second';
    second.supersedes = [f.id];
    f.supersedes = [second.id];
    report.findings.push(second);
    expect(assetQualityEvaluationSchema.safeParse(report).success).toBe(false);
  });
  it('binds exact source/requirement/manifest and actual clip/frame/pose/ROI', () => {
    const report = crow(),
      expected = binding(report);
    expect(validateAssetQualityEvaluation(report, expected)).toEqual(report);
    expect(() =>
      validateAssetQualityEvaluation(
        change((r) => {
          r.subject.rgbaSha256 = '0'.repeat(64);
        }),
        expected,
      ),
    ).toThrow(/binding|subject/i);
    expect(() =>
      validateAssetQualityEvaluation(
        change((r) => {
          r.requirement.sha256 = '0'.repeat(64);
        }),
        expected,
      ),
    ).toThrow(/binding|requirement/i);
    expect(() =>
      validateAssetQualityEvaluation(
        change((r) => {
          r.findings[0]!.target.frame = 255;
        }),
        expected,
      ),
    ).toThrow(/frame/i);
    expect(() =>
      validateAssetQualityEvaluation(
        change((r) => {
          r.findings[0]!.target.poseId = 'invented';
        }),
        expected,
      ),
    ).toThrow(/pose/i);
    expect(() =>
      validateAssetQualityEvaluation(
        change((r) => {
          r.findings[0]!.target.region = { x: 74, y: 0, width: 2, height: 1 };
        }),
        expected,
      ),
    ).toThrow(/region|canvas/i);
    expect(() =>
      validateAssetQualityEvaluation(
        change((r) => {
          r.basis = 'source-bound';
        }),
        expected,
      ),
    ).toThrow(/fixture|synthetic/i);
  });
  it('binds current V6 attention frames without inventing locomotion or contact', () => {
    const manifest = speciesManifestSchema.parse(
      JSON.parse(
        readFileSync(
          new URL('../../../contracts/fixtures/common-family-manifest-v6.json', import.meta.url),
          'utf8',
        ),
      ),
    );
    const report = crow();
    report.subject.speciesId = manifest.speciesId;
    report.subject.canvas = { width: manifest.canvas.width, height: manifest.canvas.height };
    report.requirement.speciesId = manifest.speciesId;
    report.findings[0]!.target = {
      clip: 'blink',
      frame: sampleClip(manifest, 'blink', 0, false).frame,
      poseId: null,
      region: null,
      contactKind: null,
    };
    expect(validateAssetQualityEvaluation(report, { ...binding(report), manifest })).toEqual(
      report,
    );
    report.findings[0]!.target.clip = 'moving';
    expect(() => validateAssetQualityEvaluation(report, { ...binding(report), manifest })).toThrow(
      /clip/i,
    );
  });
  it('binds reviewed contact to an actual frame and current independent reference', () => {
    const report = reviewedReport(),
      f = report.findings[0]!;
    expect(assetQualityEvaluationSchema.safeParse(report).success).toBe(true);
    expect(() => validateAssetQualityEvaluation(report, binding(report))).toThrow(
      /contact.*binding/i,
    );
    expect(validateAssetQualityEvaluation(report, contactBinding(report))).toEqual(report);
    f.target = { clip: null, frame: null, poseId: null, region: null, contactKind: null };
    expect(assetQualityEvaluationSchema.safeParse(report).success).toBe(false);
  });
  it('rejects reuse of a trusted left-foot/frame-0 hash for right-foot/frame-1', () => {
    const report = reviewedReport(),
      trusted = contactBinding(report);
    expect(validateAssetQualityEvaluation(report, trusted)).toEqual(report);
    report.findings[0]!.target.contactKind = 'right-foot';
    report.findings[0]!.target.frame = 1;
    expect(() => validateAssetQualityEvaluation(report, trusted)).toThrow(
      /contact.*(scope|binding)/i,
    );
  });
  it('rejects proof reuse for each changed frame, clip, contact, pose, region and trusted identity', () => {
    for (const mutate of [
      (r: AssetQualityEvaluation) => {
        r.subject.sourcePngSha256 = 'a'.repeat(64);
        r.evidence.find((e) => e.kind === 'source')!.sha256 = 'a'.repeat(64);
      },
      (r: AssetQualityEvaluation) => {
        r.requirement.sha256 = 'a'.repeat(64);
      },
      (r: AssetQualityEvaluation) => {
        r.requirement.support!.slotId = 'synthetic-bath:other';
      },
      (r: AssetQualityEvaluation) => {
        r.requirement.support!.geometrySha256 = 'a'.repeat(64);
      },
      (r: AssetQualityEvaluation) => {
        r.subject.geometrySha256 = 'a'.repeat(64);
      },
      (r: AssetQualityEvaluation) => {
        r.findings[0]!.target.clip = 'bathing';
      },
      (r: AssetQualityEvaluation) => {
        r.findings[0]!.target.frame = 1;
      },
      (r: AssetQualityEvaluation) => {
        r.findings[0]!.target.contactKind = 'right-foot';
      },
      (r: AssetQualityEvaluation) => {
        r.findings[0]!.target.poseId = 'other-pose';
      },
      (r: AssetQualityEvaluation) => {
        r.findings[0]!.target.region = null;
      },
    ]) {
      const report = reviewedReport(),
        proof = proofFor(report);
      proof.coverage[0]!.region = { x: 0, y: 0, width: 10, height: 10 };
      report.findings[0]!.target.region = { x: 1, y: 1, width: 2, height: 2 };
      expect(validateAssetQualityEvaluation(report, contactBinding(report, proof))).toEqual(report);
      mutate(report);
      // Current source/requirement move together; the independent proof deliberately does not.
      expect(() => validateAssetQualityEvaluation(report, contactBinding(report, proof))).toThrow(
        /contact.*(scope|binding)/i,
      );
    }
  });
  it('accepts explicitly wider trusted coverage and source-region subsets without wildcard poses', () => {
    const report = reviewedReport(),
      proof = proofFor(report);
    proof.coverage[0] = {
      clip: 'idle',
      frames: [0, 1],
      poseIds: [null],
      contactKinds: ['left-foot', 'right-foot'],
      region: { x: 0, y: 0, width: 20, height: 20 },
    };
    report.findings[0]!.target = {
      clip: 'idle',
      frame: 1,
      poseId: null,
      contactKind: 'right-foot',
      region: { x: 5, y: 5, width: 10, height: 10 },
    };
    expect(validateAssetQualityEvaluation(report, contactBinding(report, proof))).toEqual(report);
    report.findings[0]!.target.region!.width = 16;
    expect(() => validateAssetQualityEvaluation(report, contactBinding(report, proof))).toThrow(
      /contact.*scope/i,
    );
    report.findings[0]!.target.region = null;
    proof.coverage[0].region = null;
    expect(validateAssetQualityEvaluation(report, contactBinding(report, proof))).toEqual(report);
    proof.coverage[0].poseIds = ['a-specific-pose'];
    expect(() => validateAssetQualityEvaluation(report, contactBinding(report, proof))).toThrow(
      /contact.*scope/i,
    );
  });
  it('binds reviewed contact scopes to actual V6 pose identity', () => {
    const manifest = speciesManifestSchema.parse(
      JSON.parse(
        readFileSync(
          new URL('../../../contracts/fixtures/common-family-manifest-v6.json', import.meta.url),
          'utf8',
        ),
      ),
    );
    if (manifest.schemaVersion !== 6) throw Error('Expected V6 fixture');
    const pose = manifest.commonMotion.clips.blink.poses[0]!;
    const report = reviewedReport();
    report.subject.speciesId = manifest.speciesId;
    report.subject.canvas = { width: manifest.canvas.width, height: manifest.canvas.height };
    report.requirement.speciesId = manifest.speciesId;
    report.findings[0]!.target = {
      clip: 'blink',
      frame: pose.frame,
      poseId: pose.poseId,
      contactKind: 'left-foot',
      region: null,
    };
    const proof = proofFor(report);
    proof.coverage[0] = {
      clip: 'blink',
      frames: [pose.frame],
      poseIds: [pose.poseId],
      contactKinds: ['left-foot'],
      region: null,
    };
    expect(
      validateAssetQualityEvaluation(report, { ...contactBinding(report, proof), manifest }),
    ).toEqual(report);
    report.findings[0]!.target.poseId = null;
    expect(() =>
      validateAssetQualityEvaluation(report, { ...contactBinding(report, proof), manifest }),
    ).toThrow(/contact.*scope/i);
    proof.coverage[0].poseIds.push(null);
    expect(
      validateAssetQualityEvaluation(report, { ...contactBinding(report, proof), manifest }),
    ).toEqual(report);
  });
  it('rejects bare hash lists, duplicate/empty/out-of-bounds proof scopes and report-declared trust', () => {
    const report = reviewedReport(),
      proof = proofFor(report);
    expect(() =>
      validateAssetQualityEvaluation(report, {
        ...binding(report),
        reviewedContactEvidenceSha256s: [proof.sha256],
      }),
    ).toThrow();
    expect(() =>
      validateAssetQualityEvaluation(
        { ...report, reviewedContactProofs: [proof] },
        binding(report),
      ),
    ).toThrow();
    for (const badProof of [
      { ...proof, coverage: [] },
      { ...proof, coverage: [{ ...proof.coverage[0], frames: [] }] },
      { ...proof, coverage: [{ ...proof.coverage[0], frames: [0, 0] }] },
      {
        ...proof,
        coverage: [{ ...proof.coverage[0], region: { x: 74, y: 0, width: 2, height: 1 } }],
      },
      { ...proof, subject: { ...proof.subject, geometrySha256: null } },
    ])
      expect(() =>
        validateAssetQualityEvaluation(report, {
          ...binding(report),
          reviewedContactProofs: [badProof],
        }),
      ).toThrow();
  });
  it('rejects missing clip, illegal source catalog pair and expired configuration identity', () => {
    const report = crow(),
      f = report.findings[0]!;
    f.label.source.catalogId = 'unversioned-source';
    expect(assetQualityEvaluationSchema.safeParse(report).success).toBe(false);
    f.label.source.catalogVersion = '1';
    report.tools[0]!.configurationSha256 = '0'.repeat(64);
    expect(assetQualityEvaluationSchema.safeParse(report).success).toBe(false);
  });
  it('does not claim model-backed CV landmarks are directly measured anatomy', () => {
    const report = crow();
    report.tools[0]!.kind = 'cv';
    report.tools[0]!.model = {
      id: 'synthetic-cv',
      version: 'snapshot-1',
      promptSha256: '1'.repeat(64),
      configurationSha256: '2'.repeat(64),
    };
    expect(assetQualityEvaluationSchema.safeParse(report).success).toBe(true);
    report.findings[0]!.knowledge = 'observed';
    expect(assetQualityEvaluationSchema.safeParse(report).success).toBe(false);
  });
  it('retains exact prior report digests without fabricating external graph validation', () => {
    const report = crow();
    report.findings[0]!.supersedesExternal = [
      { reportId: 'prior-report', reportSha256: '1'.repeat(64), findingId: 'prior-finding' },
    ];
    expect(parseAssetQualityEvaluationJson(serializeAssetQualityEvaluation(report))).toEqual(
      report,
    );
    report.findings[0]!.supersedesExternal[0]!.reportId = report.reportId;
    expect(assetQualityEvaluationSchema.safeParse(report).success).toBe(false);
  });
  it('exports the existing portable structural dialect while retaining source semantics', () => {
    const exported = zodToJsonSchema(assetQualityEvaluationSchema, {
      name: 'AssetQualityEvaluationV1',
      $refStrategy: 'root',
      target: 'jsonSchema7',
    });
    const structural = new Ajv({ strict: true }).compile(schemaRecord(exported));
    expect(structural(examples.crow)).toBe(true);
    expect(structural(examples.bath)).toBe(true);
    expect(structural({ ...examples.crow, grantsAdmission: true })).toBe(false);
    const semanticNegative = bath();
    semanticNegative.findings[0]!.verdict = 'pass';
    expect(structural(semanticNegative)).toBe(true);
    expect(assetQualityEvaluationSchema.safeParse(semanticNegative).success).toBe(false);
  });
  it('rejects byte-heavy reports within array limits without throwing from safeParse', () => {
    const report = crow();
    report.findings = Array.from({ length: 100 }, (_, index) => ({
      ...structuredClone(report.findings[0]!),
      id: 'finding-' + index,
    }));
    expect(assetQualityEvaluationSchema.safeParse(report).success).toBe(false);
  });
  it('rejects conflicting mapping evidence even when the diagnostic rule is identical', () => {
    const report = crow(),
      second = structuredClone(report.findings[0]!);
    second.id = 'same-rule-new-mapping';
    second.label = {
      status: 'mapped',
      source: second.label.source,
      ruleId: 'pose-action-mismatch',
      mappingStatus: 'reviewed',
      mappingEvidenceSha256: '0'.repeat(64),
    };
    report.evidence.push({
      id: 'different-mapping-review',
      kind: 'mapping-review',
      sha256: '0'.repeat(64),
    });
    report.findings.push(second);
    expect(assetQualityEvaluationSchema.safeParse(report).success).toBe(false);
  });
});
