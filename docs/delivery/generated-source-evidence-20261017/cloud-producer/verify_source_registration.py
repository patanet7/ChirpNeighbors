"""Verify zero-native registry continuation without rewriting source history.

API: verify(Path(root)) -> the exact stage63 result plus registryContinuation facts.
CLI: python verify_source_registration_continuation.py --root DELIVERY_DIRECTORY

Root supplies source-registration-continuation-v1.json, schemaVersion 1:
{
  "kind": "zero-native-registry-continuation",
  "baselineDirectory": "registration-continuation-v1",
  "baselineRegistrySHA256": "<pinned exact 20-entry public registry>",
  "baselineExperimentCount": 20,
  "priorVerifierSHA256": "<pinned exact stage63 verifier>",
  "sourceBankSHA256": "<pinned unchanged source bank>",
  "activeInventorySHA256": "<pinned unchanged runtime slot inventory>",
  "newNativeCalls": 0, "newNativeDrawings": 0,
  "acceptedUsesAdded": 0, "runtimeAdmission": false,
  "experiments": [{
    "id": "<extra registry entry id>",
    "source": "experiments/.../PREREGISTRATION.json", "sourceSHA256": "...",
    "outcome": "experiments/.../ROOT-ADJUDICATION.json", "outcomeSHA256": "...",
    "countsEvidence": {
      "file": "experiments/.../ROOT-ADJUDICATION.json", "sha256": "...",
      "nativeCallsPointer": "/actualImageCalls",
      "nativeDrawingsPointer": "/newNativeDrawings"
    }
  }]
}

Receipt rows exactly cover current registry entries after the immutable prefix,
in order. Each countsEvidence file must be that entry's final outcome. Pointers
are RFC6901 JSON pointers to explicit integer zero counts, not generation budgets.
Future zero-native experiments extend the receipt and registry; no verifier edit.
Root retains exact old lessons/verifier in baselineDirectory before installation.

Only temporary hardlink trees are written. Before either metadata copy, unlink
its temporary hardlink. Execute the cryptographically pinned old verifier there;
its own stage61/57 callbacks remain unchanged. No source file is opened to write.
No installs, network, image calls, registry edits or admission claims.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import tempfile
from typing import Any


BASELINE_DIRECTORY = "registration-continuation-v1"
RECEIPT = "source-registration-continuation-v1.json"
REGISTRY = "lessons-and-experiments.json"
VERIFIER = "verify_source_registration.py"
ACTIVE_INVENTORY = "release/animation-checkpoint-1-20261017/CURRENT-SLOT-INVENTORY.json"
BASELINE_REGISTRY_SHA256 = "eff09af3378f0a5b8f3272bb94cdfba73e17c5d752ff50aee81ee22d2654a276"
PRIOR_VERIFIER_SHA256 = "ae0bbae0c7ffcf04d938bff15812df4c59e9e19947329af0e5661713241bae97"
SOURCE_BANK_SHA256 = "88ab37b86c732a1b634b65a28b727466785ef2a32eca2dc2fa3e9e05d4ecae17"
ACTIVE_INVENTORY_SHA256 = "164507fddf904e892ec95868841271effc5a4e7da4232c4d1f6c18cc6385351a"
# These artifacts do not change for a zero-native/zero-admission continuation.
# The exact old verifier independently checks decoded sources, receipts and cells.
UNCHANGED_SOURCE_METADATA = {
    "frame-bank.json": SOURCE_BANK_SHA256,
    "original-source-inventory.json": "022fa2e0bcb9f0a21af22acfeb8c3c63774117366a2c72d6809659007dc0f7e6",
    "source-frame-map.json": "1e576262368bb2b8675a6ec3d9096a851e380fa0f8b773f5c6f6b9e07806192a",
    "source-registration-stage61.json": "216333d7d31e4511d46bafe9b2b295c793f909d6c0ab7d05710553ddc66dbdd5",
    "source-registration-stage63.json": "81c4809e5c3aeb2190130970ffe7c796470d4a436d995f383334ee2dd87537d5",
    "release/animation-checkpoint-1-20261017/intake-overlay.json": "d71c41569c3cde25c8da80554474cda462a5a2af02bcd8467d20a0082c96e210",
    ACTIVE_INVENTORY: ACTIVE_INVENTORY_SHA256,
}
OVERRIDES = (REGISTRY, VERIFIER)


class VerificationError(RuntimeError):
    pass


def require(condition: Any, message: str) -> None:
    if not condition:
        raise VerificationError(message)


def sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def inside(root: Path, relative: str) -> Path:
    require(isinstance(relative, str) and bool(relative), "Missing relative artifact path")
    rel = Path(relative)
    require(not rel.is_absolute() and ".." not in rel.parts,
            f"Non-local artifact path: {relative}")
    current = root
    for part in rel.parts:
        current /= part
        require(not current.is_symlink(), f"Symlink artifact path: {relative}")
    resolved = current.resolve(strict=True)
    require(resolved.is_relative_to(root), f"Artifact path escapes root: {relative}")
    return resolved


def checked_file(root: Path, relative: str, expected: str | None = None) -> Path:
    path = inside(root, relative)
    require(path.is_file(), f"Artifact is not a file: {relative}")
    if expected is not None:
        require(sha(path) == expected, f"SHA256 mismatch: {relative}")
    return path


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def json_pointer(document: Any, pointer: str) -> Any:
    """Resolve a strict RFC6901 pointer; do not use Python evaluation."""
    require(isinstance(pointer, str) and pointer.startswith("/"),
            "Count evidence requires a nonempty JSON pointer")
    current = document
    for encoded in pointer[1:].split("/"):
        # Invalid tilde escapes would otherwise resolve a different literal key.
        offset = 0
        while offset < len(encoded):
            if encoded[offset] == "~":
                require(offset + 1 < len(encoded) and encoded[offset+1] in "01",
                        f"Invalid JSON pointer escape: {pointer}")
                offset += 2
            else:
                offset += 1
        token = encoded.replace("~1", "/").replace("~0", "~")
        if isinstance(current, dict):
            require(token in current, f"Count evidence pointer missing: {pointer}")
            current = current[token]
        elif isinstance(current, list):
            require(token.isascii() and token.isdecimal()
                    and (token == "0" or not token.startswith("0")),
                    f"Invalid JSON pointer array index: {pointer}")
            require(int(token) < len(current), f"Count evidence index exceeds array: {pointer}")
            current = current[int(token)]
        else:
            raise VerificationError(f"Count evidence traverses a scalar: {pointer}")
    return current


def verify_registry(root: Path, receipt: dict[str, Any], baseline: Path) -> dict[str, Any]:
    old_path = checked_file(baseline, REGISTRY, BASELINE_REGISTRY_SHA256)
    current_path = checked_file(root, REGISTRY)
    old, current = load(old_path), load(current_path)
    require(type(receipt["baselineExperimentCount"]) is int
            and receipt["baselineExperimentCount"] == len(old["experiments"]) == 20,
            "Wrong historical registry entry count")
    require(current["experiments"][:len(old["experiments"])] == old["experiments"],
            "Historical public registry prefix changed")
    require({k:v for k,v in current.items() if k != "experiments"}
            == {k:v for k,v in old.items() if k != "experiments"},
            "Historical registry top-level metadata changed")
    ids = [entry["id"] for entry in current["experiments"]]
    require(all(isinstance(ident, str) and ident for ident in ids)
            and len(ids) == len(set(ids)), "Experiment IDs missing or duplicated")
    extra = current["experiments"][len(old["experiments"]):]
    rows = receipt["experiments"]
    require(isinstance(rows, list) and [row["id"] for row in rows]
            == [entry["id"] for entry in extra],
            "Continuation receipt does not exactly cover extra registry entries in order")
    verified = []
    for entry, row in zip(extra, rows):
        require(entry["source"] == row["source"] and entry["outcome"] == row["outcome"],
                f"Registry source/outcome binding differs: {row['id']}")
        checked_file(root, row["source"], row["sourceSHA256"])
        outcome = checked_file(root, row["outcome"], row["outcomeSHA256"])
        counts = row["countsEvidence"]
        require(counts["file"] == row["outcome"] and counts["sha256"] == row["outcomeSHA256"],
                "Actual zero-count evidence must be the hash-bound final outcome")
        require(counts["nativeCallsPointer"] != counts["nativeDrawingsPointer"],
                "Call and drawing evidence cannot share one count field")
        outcome_json = load(outcome)
        actual_calls = json_pointer(outcome_json, counts["nativeCallsPointer"])
        actual_drawings = json_pointer(outcome_json, counts["nativeDrawingsPointer"])
        require(type(actual_calls) is int and actual_calls == 0
                and type(actual_drawings) is int and actual_drawings == 0,
                f"Continuation has nonzero/missing actual native counts: {row['id']}")
        # Never replace an explicit positive registry claim with receipt zeros.
        for key in ("actualImageCalls","newNativeCalls","actualNativeCalls",
                    "newNativeDrawings","newGeneratedDrawings","generatedDrawings"):
            if key in entry:
                require(type(entry[key]) is int and entry[key] == 0,
                        f"Registry native count conflicts with zero-native continuation: {row['id']}:{key}")
        for key in ("runtimeAdmission","runtimeAccepted","liveIntegration","liveAcceptance"):
            if key in entry:
                require(entry[key] is False or entry[key] in ("NOT_TESTED","NOT_SUBMITTED_NOT_TESTED"),
                        f"Registry entry claims runtime/live acceptance: {row['id']}:{key}")
        verified.append({"id":row["id"],"source":row["source"],"sourceSHA256":row["sourceSHA256"],
                         "outcome":row["outcome"],"outcomeSHA256":row["outcomeSHA256"],
                         "actualNewNativeCalls":0,"actualNewNativeDrawings":0})
    return {"baselineExperimentCount":len(old["experiments"]),
            "currentExperimentCount":len(current["experiments"]),
            "baselinePublicRegistrySHA256":sha(old_path),"currentPublicRegistrySHA256":sha(current_path),
            "oldExperimentPrefixExact":True,"registryTopMetadataUnchanged":True,
            "extraExperimentIDsUnique":True,"extraExperiments":verified}


def historical_regression(root: Path, baseline: Path) -> dict[str, Any]:
    checked_file(baseline, VERIFIER, PRIOR_VERIFIER_SHA256)
    checked_file(baseline, REGISTRY, BASELINE_REGISTRY_SHA256)
    protected_names = set(UNCHANGED_SOURCE_METADATA) | {REGISTRY, VERIFIER, RECEIPT}
    before = {name:sha(checked_file(root,name)) for name in protected_names}
    temp_path = None
    report: dict[str, Any]
    with tempfile.TemporaryDirectory(prefix=".stage65-source-continuation-", dir=root.parent) as dirname:
        temp_path = Path(dirname)
        count = 0
        for directory, dirs, files in os.walk(root, followlinks=False):
            source_dir = Path(directory)
            target_dir = temp_path/source_dir.relative_to(root)
            target_dir.mkdir(parents=True,exist_ok=True)
            for name in dirs:
                require(not (source_dir/name).is_symlink(), f"Symlink directory: {source_dir/name}")
            for name in files:
                source = source_dir/name
                require(not source.is_symlink() and stat.S_ISREG(source.stat().st_mode),
                        f"Non-regular source artifact: {source}")
                os.link(source,target_dir/name,follow_symlinks=False)
                count += 1
        # The ONLY overrides. Never copy onto a still-hardlinked file.
        for name in OVERRIDES:
            target = temp_path/name
            target.unlink()
            shutil.copyfile(checked_file(baseline,name),target)
        require(sha(temp_path/VERIFIER) == PRIOR_VERIFIER_SHA256
                and sha(temp_path/REGISTRY) == BASELINE_REGISTRY_SHA256,
                "Temporary historical callback identity differs")
        environment = os.environ.copy()
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        completed = subprocess.run([sys.executable,str(temp_path/VERIFIER),"--root",str(temp_path)],
                                   cwd=temp_path,env=environment,text=True,capture_output=True,timeout=900)
        require(completed.returncode == 0,
                "Exact stage63 regression failed:\n"+completed.stdout+completed.stderr)
        result = json.loads(completed.stdout.strip())
        require(result.get("passed") is True and result.get("stage") == 63,
                "Historical stage63 result did not pass")
        require(result["registrationOnlyNativeDrawings"] == 33
                and result["registrationOnlyNativeOriginals"] == 19
                and result["totalBankDrawingIDs"] == 183
                and result["totalOriginalPromptPairs"] == 69,
                "Historical registration checkpoint counters differ")
        report = {"result":result,"verifierSHA256":PRIOR_VERIFIER_SHA256,
                  "hardlinkedFiles":count,"temporaryOverrides":list(OVERRIDES),
                  "nestedHistoricalStage61And57Unchanged":True}
    require(temp_path is not None and not temp_path.exists(), "Temporary tree was not removed")
    require(all(sha(checked_file(root,name)) == digest for name,digest in before.items()),
            "Historical callback mutated real source metadata")
    report.update(temporaryTreeRemoved=True,actualSourceMetadataUnchanged=True)
    return report


def verify(root: Path) -> dict[str, Any]:
    require(not root.is_symlink(), "Source root cannot be a symlink")
    root = root.resolve(strict=True)
    require(root.is_dir(), "Source root is not a directory")
    receipt_path = checked_file(root, RECEIPT)
    receipt = load(receipt_path)
    require(receipt["schemaVersion"] == 1 and receipt["kind"] == "zero-native-registry-continuation",
            "Unsupported continuation receipt")
    require(receipt["baselineDirectory"] == BASELINE_DIRECTORY,
            "Unexpected registry baseline directory")
    require(receipt["baselineRegistrySHA256"] == BASELINE_REGISTRY_SHA256
            and receipt["priorVerifierSHA256"] == PRIOR_VERIFIER_SHA256
            and receipt["sourceBankSHA256"] == SOURCE_BANK_SHA256
            and receipt["activeInventorySHA256"] == ACTIVE_INVENTORY_SHA256,
            "Continuation receipt disagrees with historical immutable pins")
    for key in ("newNativeCalls","newNativeDrawings","acceptedUsesAdded"):
        require(type(receipt[key]) is int and receipt[key] == 0,
                f"Continuation cannot change {key}")
    require(receipt["runtimeAdmission"] is False, "Continuation cannot admit runtime art")
    for name,digest in UNCHANGED_SOURCE_METADATA.items():
        checked_file(root,name,digest)
    bank = load(checked_file(root,"frame-bank.json"))
    require(len(bank["frames"]) == 183 and bank["frameCount"] == 183
            and all(frame.get("acceptedUses") == [] for frame in bank["frames"]),
            "Source bank changed counts or accepted uses")
    baseline = inside(root,BASELINE_DIRECTORY)
    registry_facts = verify_registry(root,receipt,baseline)
    historical = historical_regression(root,baseline)
    # Preserve every legacy field/value for the unchanged checkpoint caller.
    result = dict(historical["result"])
    result["registryContinuation"] = {
        "wrapperStage":65,"receipt":RECEIPT,"receiptSHA256":sha(receipt_path),
        **registry_facts,"newNativeCalls":0,"newNativeDrawings":0,"acceptedUsesAdded":0,
        "sourceBankSHA256":SOURCE_BANK_SHA256,"activeInventorySHA256":ACTIVE_INVENTORY_SHA256,
        "unchangedMetadataHashes":UNCHANGED_SOURCE_METADATA,
        "historicalVerifierSHA256":historical["verifierSHA256"],
        "temporaryOverrides":historical["temporaryOverrides"],
        "temporaryHardlinkedFiles":historical["hardlinkedFiles"],
        "temporaryTreeRemoved":historical["temporaryTreeRemoved"],
        "actualSourceMetadataUnchanged":historical["actualSourceMetadataUnchanged"],
        "runtimeAdmission":False,"sourceAppearanceOrSupportApproved":False,
    }
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root",type=Path,default=Path(__file__).parent)
    args = parser.parse_args()
    try:
        print(json.dumps(verify(args.root),sort_keys=True))
    except (VerificationError,OSError,ValueError,KeyError,TypeError,subprocess.SubprocessError) as error:
        print(json.dumps({"passed":False,"error":str(error),"runtimeAdmission":False}),file=sys.stderr)
        raise SystemExit(1)
