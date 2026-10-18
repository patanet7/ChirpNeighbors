"""Check shared structural goldens and emit independently decoded roundtrips."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from jsonschema import Draft7Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
NAMES = frozenset(
    {
        "dev-workbench-playback-v2",
        "dev-workbench-scenario-v2",
        "dev-workbench-request-v2",
        "asset-quality-evaluation-v1",
        "registered-scene-manifest-v2",
        "integration10-source-request-v2",
        "integration10-source-response-v2",
        "registered-yard-texture-pack-v2",
        "behavior-decision-trace-v2",
        "placement-snapshot-v2",
        "placement-command-v2",
        "object-inventory-command-v2",
        "dev-workbench-command-request-v2",
        "project-generated-evidence-v1",
        "project-generated-common-proposal-v1",
        "asset-packaging-input-v5",
        "rgba-source-artifact-v4",
        "png-file-package-command-v4",
        "png-workshop-plan-v4",
        "job-command-v5",
        "common-intake-report-v2",
        "common-intake-receipt-v2",
        "common-motion-v1",
        "species-manifest-v6",
        "asset-packaging-input-v4",
        "rgba-source-artifact-v3",
        "png-file-package-command-v3",
        "png-workshop-plan-v3",
        "job-command-v4",
        "yard-layout-read-v1",
        "yard-layout-command-response-v1",
        "runtime-control-v1",
        "physical-surface-options-v1",
        "yard-runtime-selection-v1",
        "yard-runtime-advance-v1",
        "dev-workbench-request-v1",
        "dev-workbench-scenario-v1",
        "dev-workbench-playback-v1",
        "animation-planning-input-v1",
        "animation-specification-v1",
        "animation-production-plan-v1",
        "job-command-v1",
        "animation-recipe-v1",
        "animation-planning-input-v2",
        "job-command-v2",
        "reference-source-descriptor-v1",
        "reference-discovery-policy-v1",
        "reference-discovery-request-v1",
        "discovered-reference-v1",
        "reference-discovery-result-v1",
        "reference-fetch-receipt-v1",
        "reference-image-identity-v1",
        "reference-admission-source-v1",
        "reference-admission-pin-v1",
        "reference-review-command-v1",
        "reference-review-v1",
        "reference-revoke-command-v1",
        "reference-revocation-v1",
        "reference-admission-record-v1",
        "reference-admission-list-v1",
        "reference-admission-response-v1",
        "reference-generation-provider-pin-v1",
        "reference-generation-input-v1",
        "reference-generation-command-v1",
        "reference-acquisition-command-v1",
        "reference-generation-candidate-v1",
        "reference-authority-v1",
        "catalog-pin-v1",
        "public-catalog-render-v1",
        "catalog-entry-v1",
        "catalog-promotion-command-v1",
        "catalog-revocation-command-v1",
        "catalog-publication-receipt-v1",
        "catalog-pin-command-v1",
        "catalog-selection-receipt-v1",
        "catalog-overview-v1",
        "catalog-command-response-v1",
        "asset-lifecycle-target-v1",
        "asset-archive-state-v1",
        "asset-lifecycle-command-v1",
        "asset-lifecycle-receipt-v1",
        "asset-lifecycle-entry-v1",
        "asset-lifecycle-overview-v1",
        "asset-lifecycle-response-v1",
        "asset-package-history-v1",
        "png-file-origin-v1",
        "png-frame-layout-v1",
        "png-file-record-v1",
        "png-file-list-v1",
        "png-file-receipt-v1",
        "png-file-review-command-v1",
        "png-file-package-command-v1",
        "png-workshop-plan-v1",
        "arrival-adapter-capability-v1",
        "object-inventory-v1",
        "object-inventory-command-v1",
        "object-operation-receipts-v1",
        "arrival-v1",
        "arrival-list-v1",
        "arrival-consume-command-v1",
        "arrival-consume-result-v1",
        "arrival-cue-v1",
        "session-context-v1",
        "session-changed-v1",
        "illustrative-species-profile-v1",
        "simulation-options-v1",
        "species-behavior-traits-v1",
        "fictional-personality-v1",
        "behavior-decision-trace-v1",
        "behavior-experiment-v1",
        "environment-controls-v1",
        "environment-frame-v1",
        "product-event-v1",
        "analytics-batch-v1",
        "analytics-preference-command-v1",
        "analytics-status-v1",
        "analytics-receipt-v1",
        "analytics-failure-v1",
        "security-audit-event-v1",
        "catalog-request-v1",
        "pending-catalog-request-v1",
        "catalog-release-v1",
        "generation-recipe-v1",
        "shared-generation-plan-v1",
        "private-generation-plan-v1",
        "generation-cost-v1",
        "generation-usage-v1",
        "generation-usage-summary-v1",
        "shape-review-v1",
        "local-reference-v1",
        "reference-policy-v1",
        "segmentation-stage-v1",
        "matte-stage-v1",
        "foreground-stage-v1",
        "image-stage-sequence-v1",
        "image-qa-policy-v1",
        "lossless-pixel-policy-v1",
        "recording-lifecycle-v1",
        "recording-lifecycle-page-v1",
        "recording-deletion-ledger-v1",
        "confirmation-command-v1",
        "confirmation-receipt-v1",
        "confirmation-error-v1",
        "share-create-command-v1",
        "share-revoke-command-v1",
        "share-status-v1",
        "share-created-v1",
        "public-share-v1",
        "share-error-v1",
        "public-share-unavailable-v1",
        "request-budget-error-v1",
        "command-error-v1",
        "species-manifest-v2",
        "species-manifest-v3",
        "species-manifest-v4",
        "asset-packaging-input-v2",
        "asset-packaging-input-v3",
        "rgba-source-artifact-v1",
        "rgba-source-artifact-v2",
        "job-command-v3",
        "png-file-package-command-v2",
        "png-workshop-plan-v2",
        "identification-v2",
        "finding-command-v1",
        "recording-metadata-v1",
        "scene-manifest-v1",
        "yard-backup-v2",
    }
)


def check_corpus(path: Path) -> list[dict[str, object]]:
    corpus: object = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(corpus, dict) or corpus.get("schemaVersion") != 1:
        raise ValueError("Unsupported corpus")
    cases = corpus.get("cases")
    if not isinstance(cases, list) or not cases:
        raise ValueError("Missing corpus cases")
    if "date-time" not in FormatChecker.checkers:
        raise RuntimeError("Install requirements-contract.txt")
    validators: dict[str, Draft7Validator] = {}
    results: list[dict[str, object]] = []
    names: set[str] = set()
    for case in cases:
        if not isinstance(case, dict):
            raise TypeError("Malformed corpus case")
        name, contract = case.get("name"), case.get("schema")
        if not isinstance(name, str) or name in names or contract not in NAMES:
            raise ValueError("Duplicate case or unknown contract")
        names.add(name)
        if not isinstance(contract, str):
            raise TypeError("Malformed contract name")
        if contract not in validators:
            schema = json.loads(
                (ROOT / "contracts" / f"{contract}.schema.json").read_text(
                    encoding="utf-8"
                )
            )
            Draft7Validator.check_schema(schema)
            validators[contract] = Draft7Validator(
                schema, format_checker=FormatChecker()
            )
        validator = validators[contract]
        accepted = validator.is_valid(case.get("value"))
        if accepted is not case.get("valid"):
            raise AssertionError(f"Python structural validation disagrees: {name}")
        result: dict[str, object] = {"name": name, "accepted": accepted}
        if accepted:
            result["value"] = case["value"]
        results.append(result)
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--corpus",
        type=Path,
        default=ROOT / "contracts/fixtures/boundary-cases-v1.json",
    )
    parser.add_argument("--roundtrip", action="store_true")
    args = parser.parse_args()
    results = check_corpus(args.corpus)
    if args.roundtrip:
        print(json.dumps(results, allow_nan=False))
    else:
        print(f"{len(results)} Python contract corpus cases verified")


if __name__ == "__main__":
    main()
