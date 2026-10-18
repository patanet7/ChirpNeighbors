# Asset evaluation portable integration

The single additive portable authority is `asset-quality-evaluation-v1`, generated from `assetQualityEvaluationSchema` with title `AssetQualityEvaluationV1`. It carries advisory diagnostics and cannot grant source approval, rights, renderer admission or a pin. The implementation was reviewed at UI source commit `ba87917fc93c547dae07e78c3148542390c2456c`. No prior same-version schema is widened.

The canonical 17-label catalog remains the sole source-defect namespace at canonical commit `d104afbaf6949d71d24768a577f4eb9d8ef709c3`, `docs/art/asset-defect-labels-v1.json`, SHA256 `b78e048b84bff2a99da153c6b3636bb5683b4d0ab015d8b68fa3745b39a56996`. Ten evaluation rules classify diagnostics; five conservative mappings exist, and the other twelve source codes remain unclassified. The catalog and trusted proof context are not additional portable authorities.

## Consumer boundary

Generated TypeScript declarations and the standalone Ajv guard validate structural JSON only. The canonical Python TypedDict is a wire declaration, not a validator; `check_contract_corpus.py` validates the same schema offline. Callers must additionally invoke source serialization/parsing for finite JSON and the 65,536-byte UTF-8 limit, then `validateAssetQualityEvaluation` with independently verified current subject, requirement, bird manifest V2–V6, scoped reviewed contact proofs and original source-record text/hash. Structural success cannot establish current source identity, reviewed contact applicability or original-record custody.

`retainCanonicalAssetDefectSourceLabel(originalJson, verifiedSha256, 'unverified')` preserves descriptive raw source data without claiming applicability. Only an independently verified producer adapter may establish `subject-source`, pass its exact text/hash through trusted `sourceRecords`, and supply an explicit conservative classification mapping. The canonical `record_requirements` are descriptive; this integration contains no verified producer serializer, genuine producer-record ingestion, automatic migration or status/admission conversion. Synthetic Crow/bath marker hashes never become approval evidence. No provider, runtime, API or persisted-yard change is supplied.

## Compatibility and tests

Both repositories append only the one new schema and two equal digest entries. All old schema bytes, prior 341 digest entries, 854 corpus cases and 494 semantic exception entries retain their values/order. Two synthetic positive reports and 18 public-safe structural/source cases append to the shared corpus. Six property exceptions carry explicit existing source refinements into the new report only: four subject/requirement taxon mismatches and two regions exceeding a reduced canvas. They do not weaken validation.

Run the established generators and gates from the UI checkout, selecting the canonical path and pinned contract Python explicitly:

```sh
node scripts/export-contract.ts --check --main-repo ../ChirpNeighbors
node --test scripts/contract-tools/*.test.ts
node scripts/check-contract-roundtrips.ts --main-repo ../ChirpNeighbors --python /path/to/contract-python
node scripts/check-contract-properties.ts --main-repo ../ChirpNeighbors --python /path/to/contract-python
node scripts/check-contract-compatibility.ts --main-repo ../ChirpNeighbors
node scripts/check-declarations.ts
```

From the canonical checkout, run `python scripts/generate_python_contracts.py --check` and the focused `tests.test_asset_quality_evaluation_contract` suite under `backend-inference`. No hardware, model download, browser, credentials or public service is required. Older readers without this new authority must reject it until their schema/allowlist is synchronized; this is no change to acceptance of existing formats.
