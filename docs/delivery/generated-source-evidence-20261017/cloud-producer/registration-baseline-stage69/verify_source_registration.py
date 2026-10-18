"""Verify append-only stage67 native source facts and exact stage65/63/61/57 history.

CLI: python verify_source_registration.py --root SOURCE_DELIVERY_DIRECTORY
API: verify(Path(root)) -> JSON source-only report. No generation/admission.

The exact previous verifier runs in a temporary HARDLINK corpus under root.parent.
Eight historical metadata paths are unlinked before copying baseline bytes.
No payload file is opened for writing. All temporary trees clean up on exit.
Requires only existing Python/Pillow; no installs/network/private runtime data.

Stage67 ledger: source-registration-stage67.json, schemaVersion1/stage67,
baselineDirectory='registration-baseline-stage67', baselineDrawings/Originals,
registeredDrawings/Originals, oldBankRecordsSHA256, oldOriginalRecordsSHA256,
oldFrameMapSHA256, oldOverlaySHA256, oldLessonsSHA256, priorVerifierSHA256,
priorSourceIndexSHA256/Entries, appendedBankRecords, registrationOnlyBatches,
newNativeDrawings=4, newNativeOriginals=1, actualGenerationCallsInBatch=1,
registrationMakesNativeCalls=0, acceptedUsesAdded=0, runtimeAdmission=false,
activeInventorySHA256 and adjudication. Batch/native-frame fields retain the
stage63 schema; ledger frame nativeSourceRect is always integer XYWH.
Bath PRIMARY atlasSourceRect is separately declared XYXY and converted explicitly.
Baseline snapshots include the old general verify_source_files.py as well as
bank/original inventory/map/overlay/lessons/registration verifier/source index.
"""
from __future__ import annotations

import argparse
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import stat
import subprocess
import sys
import tempfile
from typing import Any

from PIL import Image

# Exact pre-stage67 stage65 verifier and index pins anchor the historical callback.
# New source/original counts remain ledger-derived.
LEGACY_VERIFIER_SHA256 = "41c817ae2458ce4e137eb2b9f785c3849e08c827219825160b3345704458516b"
PRIOR_INDEX_SHA256 = "4b1035f242bfeea476a17af56a657592681e79facb528b95905bfa914c77d954"
PRIOR_INDEX_ENTRIES = 5419
BASELINE_DIRECTORY = "registration-baseline-stage67"
OVERLAY = "release/animation-checkpoint-1-20261017/intake-overlay.json"
ACTIVE_INVENTORY = "release/animation-checkpoint-1-20261017/CURRENT-SLOT-INVENTORY.json"
OVERRIDES = {
    "frame-bank.json": "frame-bank.json",
    "original-source-inventory.json": "original-source-inventory.json",
    "source-frame-map.json": "source-frame-map.json",
    "verify_source_registration.py": "verify_source_registration.py",
    OVERLAY: "intake-overlay.json",
    "lessons-and-experiments.json": "lessons-and-experiments.json",
    "source-files.sha256.json": "source-files.sha256.json",
    "verify_source_files.py": "verify_source_files.py",
}


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


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def inside(root: Path, relative: str) -> Path:
    """Accept only existing, in-root paths without symlink components."""
    require(isinstance(relative, str) and bool(relative), "Missing relative path")
    rel = Path(relative)
    require(not rel.is_absolute() and ".." not in rel.parts,
            f"Non-local source path: {relative}")
    current = root
    for component in rel.parts:
        current /= component
        require(not current.is_symlink(), f"Symlink source path: {relative}")
    resolved = current.resolve(strict=True)
    require(resolved.is_relative_to(root), f"Source path escapes root: {relative}")
    return resolved


def checked_file(root: Path, relative: str, expected: str | None = None) -> Path:
    path = inside(root, relative)
    require(path.is_file(), f"Not a source file: {relative}")
    if expected is not None:
        require(sha(path) == expected, f"SHA256 mismatch: {relative}")
    return path


def rgba(path: Path) -> Image.Image:
    with Image.open(path) as image:
        require(image.format == "PNG", f"Source is not PNG: {path.name}")
        return image.convert("RGBA")


def frame_id(image: Image.Image) -> str:
    prefix = f"RGBA8;{image.width}x{image.height};".encode("ascii")
    return "frame.sha256." + hashlib.sha256(prefix + image.tobytes()).hexdigest()


def first(record: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        if key in record:
            return record[key]
    return None


def native_rect(record: dict[str, Any], fallback: list[int] | None = None) -> list[int]:
    rect = first(record, "nativeSourceRect", "nativeSourceRectXYWH",
                 "sourceCellRect", "nativeCellRect", "sourceOriginalRectXYWH", "sourceOriginalRect")
    if rect is None and "atlasSourceRect" in record:
        # Bath producer explicitly uses PIL.crop XYXY in the native source sheet.
        # Render sourceRect/atlasRect fields are deliberately NOT interpreted here.
        bounds = record["atlasSourceRect"]
        require(isinstance(bounds,list) and len(bounds) == 4
                and all(type(value) is int for value in bounds),
                "Invalid native atlasSourceRect XYXY")
        rect = [bounds[0],bounds[1],bounds[2]-bounds[0],bounds[3]-bounds[1]]
    if rect is None:
        require(fallback is not None, "Missing native source rectangle")
        rect = fallback
    if isinstance(rect, dict):
        rect = [rect.get("x"), rect.get("y"),
                first(rect, "width", "w"), first(rect, "height", "h")]
    require(isinstance(rect, list) and len(rect) == 4
            and all(type(value) is int for value in rect),
            f"Invalid integer XYWH rectangle: {rect}")
    require(rect[0] >= 0 and rect[1] >= 0 and rect[2] > 0 and rect[3] > 0,
            f"Invalid source rectangle extent: {rect}")
    return rect


def verify_receipts(batch: dict[str, Any], prompt: bytes, args: dict[str, Any],
                    args_sha: str, dispatch: dict[str, Any], returned: dict[str, Any],
                    arguments_root: Path) -> None:
    affirmative_dispatch = any(dispatch.get(key) == 1 for key in (
        "nativeCallsStarted", "callsDispatched", "nativeCalls",
        "nativeCallsDispatched", "nativeCallOrdinal", "actualRequestCount"))
    if not affirmative_dispatch:
        # The retained Bath preparation receipt candidly records a plan. Actual
        # invocation is bound by the separate completed return's start/return
        # counters and actual orchestration timestamps, not inferred from budget.
        require(str(dispatch.get("state","")).startswith("DISPATCH_PREPARED")
                and dispatch.get("plannedRequestNumber") == 1
                and returned.get("state") == "generated-native-original-returned"
                and returned.get("nativeCallsStarted") == 1
                and returned.get("nativeCallsReturned") == 1,
                "Prepared receipt lacks affirmative retained invocation/return evidence")
        def instant(key: str) -> datetime:
            value = returned[key]
            require(isinstance(value,str), f"Invalid native time field: {key}")
            result = datetime.fromisoformat(value.replace("Z","+00:00"))
            require(result.tzinfo is not None, f"Native time has no timezone: {key}")
            return result
        invoked = instant("actualToolInvokeNotifyUTC")
        completed = instant("returnUTC")
        require(instant("toolInvokeOrchestrationUTC") <= invoked <= completed,
                "Native orchestration/invocation/return chronology differs")
        measured = returned.get("actualInvokeNotifyToReturnMilliseconds")
        if measured is not None:
            require(type(measured) is int
                    and abs((completed-invoked).total_seconds()*1000-measured) < 1,
                    "Retained native elapsed receipt differs from timestamps")
    require(any(returned.get(key) == 1 for key in ("nativeCalls", "nativeCallsReturned", "actualRequestCount")),
            f"Return has no affirmative completed request: {batch['batchId']}")
    require(first(returned, "originalSHA256", "originalPNGsha256") == batch["originalSHA256"],
            f"Return original identity differs: {batch['batchId']}")
    if "promptSHA256" in dispatch:
        require(dispatch["promptSHA256"] == batch["promptSHA256"],
                f"Dispatch prompt hash differs: {batch['batchId']}")
    else:
        # The original flight receipt records its actual argument filename, not
        # an invented later prompt hash. Bind that retained file semantically to
        # the ledger-hashed original args, without rewriting UNKNOWN model/seed.
        require(dispatch.get("actualRequestCount") == 1
                and dispatch.get("status") == "DISPATCHING"
                and returned.get("actualRequestCount") == 1
                and returned.get("status") == "RETURNED",
                "Unrecognized dispatch receipt without prompt hash")
        dispatched_args = load(checked_file(arguments_root, dispatch["argumentsFile"]))
        require(dispatched_args.get("arguments", dispatched_args) == args,
                "Original dispatch argument-file alias differs from native arguments")
    if "actualReturnedDrawings" in returned:
        require(returned["actualReturnedDrawings"] == len(batch["frames"]),
                "Return drawing count differs from ledger")
    if "actualDrawingCount" in returned:
        require(returned["actualDrawingCount"] == len(batch["frames"]),
                "Raw return drawing count differs from ledger source cells")
    for receipt in (dispatch, returned):
        for key in ("promptSHA256", "promptSha256"):
            if key in receipt:
                require(receipt[key] == batch["promptSHA256"], f"Receipt {key} differs")
        for key in ("promptBytes", "promptUTF8Bytes"):
            if key in receipt:
                require(receipt[key] == len(prompt), f"Receipt {key} differs")
        for key in ("nativeArgsSHA256", "nativeArgumentsSHA256",
                    "preparedArgsSHA256", "argumentsSHA256", "literalArgumentsSHA256"):
            if key in receipt:
                require(receipt[key] == args_sha, f"Receipt {key} differs")
        for key in ("automaticRetries", "retries"):
            if key in receipt:
                require(receipt[key] == 0, f"Unexpected automatic retries: {batch['batchId']}")
    if "nativeRunning" in returned:
        require(returned["nativeRunning"] is False or returned["nativeRunning"] == 0,
                "Return still reports a running native request")
    for receipt in (dispatch, returned):
        require(receipt.get("status") not in {"FAILED","RUNNING"}, "Native receipt is not completed history")
    require(args.get("transparent_background") is True,
            f"Missing submitted transparency argument: {batch['batchId']}")


def prior_index_and_metadata(root: Path, baseline: Path, ledger: dict[str, Any],
                             drawings: int, originals: int, baseline_drawings: int,
                             baseline_originals: int) -> dict[str, Any]:
    """Preserve prior corpus except explicitly changed append-only metadata."""
    index_path = checked_file(baseline, "source-files.sha256.json", PRIOR_INDEX_SHA256)
    index = load(index_path)
    require(ledger["priorSourceIndexSHA256"] == sha(index_path)
            and ledger["priorSourceIndexEntries"] == len(index["files"]) == PRIOR_INDEX_ENTRIES,
            "Historical source index identity/count differs")
    allowed = set(OVERRIDES) | {"verify_source_files.py", "README.md"}
    protected = 0
    seen: set[str] = set()
    old_rows = {}
    for row in index["files"]:
        name = row["file"]
        require(name not in seen, "Duplicate path in historical source index")
        seen.add(name)
        old_rows[name] = row
        path = checked_file(root, name)
        if name not in allowed:
            require(sha(path) == row["sha256"] and path.stat().st_size == row["bytes"],
                    f"Historical payload bytes changed: {name}")
            protected += 1
    for current_name, snapshot_name in OVERRIDES.items():
        if current_name in old_rows:
            require(sha(checked_file(baseline, snapshot_name)) == old_rows[current_name]["sha256"],
                    f"Baseline metadata differs from historical index: {current_name}")
    # Preserve both native ledgers and the zero-native continuation receipt exactly.
    for historical_name in ("source-registration-stage61.json", "source-registration-stage63.json",
                            "source-registration-continuation-v1.json"):
        checked_file(root,historical_name,old_rows[historical_name]["sha256"])
    # Only count assertions in the separate byte/pixel verifier may advance.
    current_checker = checked_file(root, "verify_source_files.py").read_text()
    reconstructed_old_checker = current_checker
    replacements = [
        (f"len(originals['originals']) == {baseline_originals}", f"len(originals['originals']) == {originals}"),
        (f"len(bank['frames']) == {baseline_drawings}", f"len(bank['frames']) == {drawings}"),
        (f"len({{f['frameId'] for f in bank['frames']}}) == {baseline_drawings}",
         f"len({{f['frameId'] for f in bank['frames']}}) == {drawings}"),
        (f"pixel_count = {baseline_drawings}", f"pixel_count = {drawings}"),
        (f"'originalPromptPairs': {baseline_originals}", f"'originalPromptPairs': {originals}"),
    ]
    for before, after in replacements:
        require(reconstructed_old_checker.count(after) == 1,
                "Updated count assertion not uniquely recognized")
        reconstructed_old_checker = reconstructed_old_checker.replace(after, before)
    require(hashlib.sha256(reconstructed_old_checker.encode("utf-8")).hexdigest()
            == old_rows["verify_source_files.py"]["sha256"],
            "General source verifier changed beyond declared count assertions")
    return {"priorIndexSHA256":sha(index_path), "priorIndexEntries":len(seen),
            "historicalNonMetadataFilesExact":protected,
            "declaredMetadataExceptions":sorted(allowed),
            "stage61And63LedgersAndZeroNativeContinuationByteExact":True,
            "generalVerifierOnlyCountAssertionsAdvanced":True,
            "readmeScope":"README may update source totals/add stage67 description; original hash remains in immutable prior index."}


def historical_regression(root: Path, baseline: Path) -> dict[str, Any]:
    """Run exact stage65 wrapper, which recursively retains stage63/61/57 regression."""
    legacy = checked_file(baseline, "verify_source_registration.py", LEGACY_VERIFIER_SHA256)
    protected = {name:sha(checked_file(root, name)) for name in OVERRIDES}
    # These counters are old legacy outputs, not assumptions about appended counts.
    temp_path = None
    with tempfile.TemporaryDirectory(prefix=".stage67-legacy-", dir=root.parent) as dirname:
        temp_path = Path(dirname)
        count = 0
        for directory, dirs, files in os.walk(root, followlinks=False):
            source_dir = Path(directory)
            target_dir = temp_path / source_dir.relative_to(root)
            target_dir.mkdir(parents=True, exist_ok=True)
            for name in dirs:
                require(not (source_dir/name).is_symlink(), f"Symlink directory: {source_dir/name}")
            for name in files:
                source = source_dir/name
                require(not source.is_symlink() and stat.S_ISREG(source.stat().st_mode),
                        f"Non-regular payload: {source}")
                os.link(source, target_dir/name, follow_symlinks=False)
                count += 1
        for target_name, baseline_name in OVERRIDES.items():
            target = temp_path/target_name
            target.unlink()  # Always sever the hardlink before copying metadata.
            shutil.copyfile(checked_file(baseline, baseline_name), target)
        require(sha(temp_path/"verify_source_registration.py") == sha(legacy),
                "Prior verifier callback bytes changed")
        environment = os.environ.copy()
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        completed = subprocess.run([sys.executable,str(temp_path/"verify_source_registration.py"),
                                    "--root",str(temp_path)],
                                   cwd=temp_path,env=environment,text=True,capture_output=True,timeout=600)
        require(completed.returncode == 0,
                "Historical stage65/63/61/57 regression failed:\n"+completed.stdout+completed.stderr)
        result = json.loads(completed.stdout.strip())
        require(result.get("passed") is True and result.get("stage") == 63
                and result.get("registryContinuation",{}).get("wrapperStage") == 65,
                "Historical stage65 continuation result did not pass")
        require(result["registrationOnlyNativeDrawings"] == 33
                and result["registrationOnlyNativeOriginals"] == 19
                and result["totalBankDrawingIDs"] == 183
                and result["totalOriginalPromptPairs"] == 69,
                "Wrong prior source checkpoint counters")
        report = {"result":result,"verifierSHA256":sha(legacy),"hardlinkedFiles":count,
                  "baselineOverrides":list(OVERRIDES),"sourceSymlinksAllowed":False}
    require(temp_path is not None and not temp_path.exists(), "Temporary corpus not removed")
    require(all(sha(checked_file(root,name)) == digest for name,digest in protected.items()),
            "Legacy callback changed real metadata")
    report.update(temporaryTreeRemoved=True,actualPayloadMetadataUnchanged=True)
    return report


def verify(root: Path) -> dict[str, Any]:
    require(not root.is_symlink(), "Source root cannot be a symlink")
    root = root.resolve(strict=True)
    require(root.is_dir(), "Source root is not a directory")
    ledger = load(checked_file(root, "source-registration-stage67.json"))
    require(ledger.get("stage") == 67, "Not a stage67 registration ledger")
    require(ledger["baselineDirectory"] == BASELINE_DIRECTORY, "Baseline directory differs")
    baseline = inside(root, BASELINE_DIRECTORY)
    old_bank_path = checked_file(baseline, "frame-bank.json", ledger["oldBankRecordsSHA256"])
    old_inv_path = checked_file(baseline, "original-source-inventory.json", ledger["oldOriginalRecordsSHA256"])
    old_map_path = checked_file(baseline, "source-frame-map.json", ledger["oldFrameMapSHA256"])
    old_overlay_path = checked_file(baseline, "intake-overlay.json", ledger["oldOverlaySHA256"])
    require(ledger["priorVerifierSHA256"] == LEGACY_VERIFIER_SHA256, "Prior verifier pin differs")
    checked_file(baseline, "verify_source_registration.py", LEGACY_VERIFIER_SHA256)
    old_lessons_path = checked_file(baseline, "lessons-and-experiments.json", ledger["oldLessonsSHA256"])
    old_lessons, current_lessons = load(old_lessons_path), load(checked_file(root,"lessons-and-experiments.json"))
    require(len(old_lessons["experiments"]) == 22, "Wrong historical public registry baseline")
    require(current_lessons["experiments"][:len(old_lessons["experiments"])] == old_lessons["experiments"]
            and {k:v for k,v in current_lessons.items() if k != "experiments"}
                == {k:v for k,v in old_lessons.items() if k != "experiments"},
            "Old lessons prefix/metadata changed")
    require(len(current_lessons["experiments"]) == len(old_lessons["experiments"]) + 1
            and current_lessons["experiments"][-1]["id"] == "BATH-SOURCE-PROPOSAL-1",
            "Registry changed beyond its one declared experiment entry")
    old_bank, old_inv, old_map = load(old_bank_path), load(old_inv_path), load(old_map_path)
    bank = load(checked_file(root, "frame-bank.json"))
    inventory = load(checked_file(root, "original-source-inventory.json"))
    frame_map = load(checked_file(root, "source-frame-map.json"))
    baseline_drawings, baseline_originals = len(old_bank["frames"]), len(old_inv["originals"])
    require(ledger["baselineDrawings"] == baseline_drawings
            and ledger["baselineOriginals"] == baseline_originals,
            "Ledger baseline counts differ from retained records")
    require((baseline_drawings, baseline_originals) == (183,69), "Wrong historical stage67 baseline")
    require(len(old_map["frames"]) == baseline_drawings, "Baseline frame map count differs")
    require(bank["frames"][:baseline_drawings] == old_bank["frames"], "Old bank prefix changed")
    require(inventory["originals"][:baseline_originals] == old_inv["originals"],
            "Old original inventory prefix changed")
    require(frame_map["frames"][:baseline_drawings] == old_map["frames"], "Old frame-map prefix changed")
    require({k:v for k,v in bank.items() if k not in {"frames","frameCount","status"}}
            == {k:v for k,v in old_bank.items() if k not in {"frames","frameCount","status"}},
            "Historical bank clip/reuse/authority metadata changed")
    inv_changes = {"originals","localGeneratedDrawings","newGenerationCallsForThisHandoff"}
    require({k:v for k,v in inventory.items() if k not in inv_changes}
            == {k:v for k,v in old_inv.items() if k not in inv_changes},
            "Historical original inventory metadata changed")
    require({k:v for k,v in frame_map.items() if k != "frames"}
            == {k:v for k,v in old_map.items() if k != "frames"},
            "Historical frame-map scope metadata changed")
    appended = ledger["appendedBankRecords"]
    batches = ledger["registrationOnlyBatches"]
    require(len(appended) == 4 and len(batches) == 1,
            "Stage67 must register its four returned source cells and one native original")
    require(bank["frames"][baseline_drawings:] == appended, "Appended bank records differ from ledger")
    require(len(bank["frames"]) == ledger["registeredDrawings"]
            == baseline_drawings + len(appended), "Final drawing counts differ")
    require(len(inventory["originals"]) == ledger["registeredOriginals"]
            == baseline_originals + len(batches), "Final original counts differ")
    require(ledger["newNativeDrawings"] == len(appended)
            and ledger["newNativeOriginals"] == len(batches)
            and ledger["actualGenerationCallsInBatch"] == len(batches),
            "Native source ledger totals differ")
    require(ledger["registrationMakesNativeCalls"] == 0
            and ledger["acceptedUsesAdded"] == 0 and ledger["runtimeAdmission"] is False,
            "Registration claims generation or runtime admission")
    require(bank["frameCount"] == len(bank["frames"])
            and inventory["localGeneratedDrawings"] == len(bank["frames"])
            and inventory["newGenerationCallsForThisHandoff"] == len(batches),
            "Metadata totals differ from source records")

    ids: set[str] = set()
    by_id: dict[str, dict[str, Any]] = {}
    for frame in bank["frames"]:
        ident = frame["frameId"]
        require(re.fullmatch(r"frame\.sha256\.[0-9a-f]{64}", ident) is not None,
                f"Malformed frame ID: {ident}")
        image_path = checked_file(root, frame["file"], frame["fileSha256"])
        image = rgba(image_path)
        require(frame_id(image) == ident and list(image.size) == frame["dimensions"],
                f"Decoded frame identity/dimensions differ: {ident}")
        require(ident not in ids, f"Duplicate source ID: {ident}")
        require(frame.get("acceptedUses") == [], f"Accepted use added: {ident}")
        ids.add(ident)
        by_id[ident] = frame
    require(len(frame_map["frames"]) == len(bank["frames"]), "Full frame-map count differs")
    map_ids: set[str] = set()
    for frame, mapping in zip(bank["frames"], frame_map["frames"]):
        require(mapping["sourceFrameId"] == frame["frameId"]
                and mapping["sourcePNG"] == frame["file"]
                and mapping["sourcePNGsha256"] == frame["fileSha256"]
                and mapping["dimensions"] == frame["dimensions"]
                and mapping["original"] == frame["sourceAtlas"]
                and mapping.get("prompt") == frame.get("sourcePrompt")
                and mapping.get("acceptedUses") == [], "Full source-frame-map record differs")
        require(mapping["sourceFrameId"] not in map_ids, "Duplicate mapped source ID")
        map_ids.add(mapping["sourceFrameId"])
    require(map_ids == ids, "Mapped IDs differ from full source bank")

    original_paths: set[str] = set()
    for item in inventory["originals"]:
        path = checked_file(root, item["file"], item["sha256"])
        prompt = checked_file(root, item["promptFile"], item["promptSha256"])
        require(path.stat().st_size == item["bytes"] and prompt.stat().st_size == item["promptBytes"],
                "Original/prompt byte counts differ")
        require(item["file"] not in original_paths, "Duplicate original inventory path")
        require(list(rgba(path).size) == item["dimensions"], "Original dimensions differ")
        original_paths.add(item["file"])

    appended_ids = {frame["frameId"] for frame in appended}
    old_ids = {frame["frameId"] for frame in old_bank["frames"]}
    require(not appended_ids.intersection(old_ids), "A historical drawing was registered again")
    seen_new_ids: set[str] = set()
    seen_original_hashes: set[str] = set()
    old_original_hashes = {item["sha256"] for item in old_inv["originals"]}
    for batch, item in zip(batches, inventory["originals"][baseline_originals:]):
        require(batch["nativeCalls"] == 1 and batch["runtimeAdmission"] is False
                and batch["acceptedUses"] == [], "Non-native or admitted registration batch")
        require(batch["originalSHA256"] not in seen_original_hashes | old_original_hashes,
                "Original was counted twice")
        seen_original_hashes.add(batch["originalSHA256"])
        original_path = checked_file(root, batch["original"], batch["originalSHA256"])
        original = rgba(original_path)
        require(list(original.size) == batch["originalDimensions"], "Native canvas differs")
        prompt_path = checked_file(root, batch["prompt"], batch["promptSHA256"])
        prompt = prompt_path.read_bytes()
        require(len(prompt) == batch["promptBytes"], "Native prompt byte count differs")
        args_path = checked_file(root, batch["nativeArguments"], batch["nativeArgumentsSHA256"])
        args_record = load(args_path)
        arguments = args_record.get("arguments", args_record)
        require(isinstance(arguments, dict) and arguments["prompt"].encode("utf-8") == prompt,
                "Submitted prompt bytes differ from retained prompt")
        dispatch = load(checked_file(root, batch["dispatchReceipt"], batch["dispatchSHA256"]))
        returned = load(checked_file(root, batch["returnReceipt"], batch["returnSHA256"]))
        # Both original flat arguments and later compatibility wrappers may be
        # present. Their actual tool arguments must agree; metadata can differ.
        for alias_name in ("native-arguments.json", "native-call-arguments.json",
                           "prepared-native-arguments.json"):
            alias_path = args_path.parent / alias_name
            if alias_path.exists():
                alias = load(checked_file(args_path.parent, alias_name))
                require(alias.get("arguments", alias) == arguments,
                        f"Native argument compatibility alias differs: {alias_name}")
        verify_receipts(batch, prompt, arguments, sha(args_path), dispatch, returned,
                        args_path.parent)
        provenance_path = args_path.parent / "input-provenance.json"
        if provenance_path.exists():
            provenance = load(checked_file(args_path.parent,"input-provenance.json"))
            references = provenance["exactReferences"]
            submitted = arguments.get("referenced_image_paths", [])
            require(len(submitted) == len(references) > 0, "Submitted reference count differs")
            for submitted_path, reference in zip(submitted,references):
                retained = checked_file(args_path.parent, reference["retainedPath"], reference["PNGsha256"])
                require(Path(submitted_path).as_posix().endswith("/"+reference["retainedPath"]),
                        "Submitted path does not bind the retained input image")
                require(frame_id(rgba(retained)) == reference["decodedRGBAId"],
                        "Retained reference decoded identity differs")
        ancestry_path = args_path.parent / "native-ancestry.json"
        require(ancestry_path.exists(), "Missing actual Bath reference ancestry")
        ancestry = load(checked_file(args_path.parent,"native-ancestry.json"))
        reference = ancestry["soleImageInput"]
        retained = checked_file(args_path.parent,reference["file"],reference["PNGsha256"])
        reference_image = rgba(retained)
        require(frame_id(reference_image) == reference["sourceFrameID"]
                and reference["sourceFrameID"] in old_ids
                and list(reference_image.size) == reference["sourceCanvas"],
                "Sole input is not the exact registered canonical source")
        submitted = arguments.get("referenced_image_paths",[])
        require(len(submitted) == 1
                and Path(submitted[0]).as_posix().endswith("/"+reference["file"]),
                "Literal submitted reference differs from retained sole image input")
        require(ancestry["literalArguments"] == args_path.name
                and ancestry["prompt"] == prompt_path.name,
                "Ancestry literal argument/prompt binding differs")
        checked_file(args_path.parent,ancestry["fullOriginalAncestor"],ancestry["ancestorSHA256"])
        checked_file(args_path.parent,ancestry["historicalAncestorPrompt"],
                     ancestry["historicalAncestorPromptSHA256"])
        require(dispatch.get("referenceSHA256") == sha(retained),
                "Prepared reference hash differs from submitted retained source")
        require(returned.get("literalArguments") == args_path.name,
                "Return literal argument filename differs")
        manifest_path = checked_file(root, batch["manifest"], batch["manifestSHA256"])
        manifest = load(manifest_path)
        require(manifest["nativeCalls"] == 1 and manifest["batchId"] == batch["batchId"],
                "Primary manifest native call/batch identity differs")
        require(checked_file(manifest_path.parent, manifest["original"], manifest["originalSHA256"])
                == original_path, "Manifest native original binding differs")
        require(checked_file(manifest_path.parent, manifest["prompt"], manifest["promptSHA256"])
                == prompt_path, "Manifest prompt binding differs")
        require(manifest["nativeArguments"] == args_path.name
                and manifest["argumentsSHA256"] == sha(args_path)
                and manifest["originalRGBAId"] == frame_id(original)
                and returned["originalRGBAId"] == frame_id(original)
                and returned["actualCanvas"] == list(original.size),
                "Native manifest/return original/argument identities differ")
        require(len(manifest["frames"]) == len(batch["frames"]) > 0, "New source frame counts differ")
        rectangles: list[list[int]] = []
        for source, declared in zip(batch["frames"], manifest["frames"]):
            ident = source["sourceFrameId"]
            require(ident in appended_ids and ident not in seen_new_ids,
                    f"Missing or duplicate newly generated frame: {ident}")
            require(first(declared, "sourceFrameId", "sourceFrameID", "primarySourceFrameId") == ident
                    and declared.get("newDrawing", True) is not False,
                    "Manifest frames do not identify new native drawings")
            image_path = checked_file(root, source["sourcePNG"], source["sourcePNGsha256"])
            require(checked_file(manifest_path.parent, declared["sourcePNG"],
                                 declared["sourcePNGsha256"]) == image_path,
                    "Manifest source PNG binding differs")
            image = rgba(image_path)
            require(list(image.size) == source["dimensions"] and frame_id(image) == ident,
                    "Registered source cell ID/dimensions differ")
            rect = native_rect(source)
            manifest_rect = native_rect(declared, [0, 0, original.width, original.height])
            require(rect == manifest_rect and rect[2:] == list(image.size)
                    and rect[0] + rect[2] <= original.width
                    and rect[1] + rect[3] <= original.height,
                    "Native source rectangle differs or exceeds original")
            require(rect[2:] == [627,627], "Bath source is not a whole equal 627-square cell")
            require(original.crop((rect[0], rect[1], rect[0]+rect[2], rect[1]+rect[3])).tobytes()
                    == image.tobytes(), "Native source-cell roundtrip changes pixels")
            for previous in rectangles:
                overlap_w = min(rect[0]+rect[2], previous[0]+previous[2]) - max(rect[0], previous[0])
                overlap_h = min(rect[1]+rect[3], previous[1]+previous[3]) - max(rect[1], previous[1])
                require(overlap_w <= 0 or overlap_h <= 0, "Native source cells overlap")
            rectangles.append(rect)
            frame = by_id[ident]
            require(frame["file"] == source["sourcePNG"]
                    and frame["fileSha256"] == source["sourcePNGsha256"]
                    and frame["sourceAtlas"] == batch["original"]
                    and frame["sourceAtlasSha256"] == batch["originalSHA256"]
                    and frame["sourcePrompt"] == batch["prompt"]
                    and frame["sourceNativeArguments"] == batch["nativeArguments"]
                    and frame["appearanceVersion"] == batch["batchId"],
                    "New bank provenance differs from native ledger")
            require(native_rect(frame["derivation"]) == rect
                    and frame["derivation"]["registrationOnly"] is True
                    and frame["derivation"]["perFrameRescale"] is False
                    and frame["acceptedUses"] == [] and frame["runtimeAdmission"] is False
                    and frame["anatomyScaleAccepted"] is False
                    and frame["rootContactAccepted"] is False,
                    "New registration claims geometry/admission or rescale")
            require(frame["sourceReview"] == ledger["adjudication"],
                    "New drawing review path differs from source adjudication")
            checked_file(root, frame["sourceReview"], frame["sourceReviewSHA256"])
            seen_new_ids.add(ident)
        if len(rectangles) > 1:
            require(len({tuple(rect[2:]) for rect in rectangles}) == 1,
                    "Native multi-pose source canvases have different sizes")
        require(original.size == (1254,1254)
                and {tuple(rect) for rect in rectangles}
                == {(0,0,627,627),(627,0,627,627),(0,627,627,627),(627,627,627,627)},
                "Bath primary cells do not cover the exact four native quadrants")
        if len(batch["frames"]) == 1:
            supplied_id = first(returned, "sourceFrameId", "sourceFrameID", "primarySourceFrameId")
            if supplied_id is not None:
                require(supplied_id == batch["frames"][0]["sourceFrameId"], "Return source ID differs")
        if "decodedNativeID" in returned:
            require(returned["decodedNativeID"] == frame_id(original), "Return native sheet ID differs")
        require(item["batch"] == batch["batchId"] and item["file"] == batch["original"]
                and item["sha256"] == batch["originalSHA256"]
                and item["promptFile"] == batch["prompt"]
                and item["promptSha256"] == batch["promptSHA256"]
                and item["acceptedProductionArt"] is False
                and item["stagedInMac"] is False and item["integratedInMac"] is False,
                "New original inventory record differs or claims app/art acceptance")
    require(seen_new_ids == appended_ids, "Ledger native cells do not cover appended bank exactly")

    adjudication = load(checked_file(root, ledger["adjudication"]))
    require(adjudication["nativeCallsReturned"] == len(batches)
            and adjudication["newNativeDrawings"] == len(appended),
            "Actual source adjudication counts differ from ledger")
    checked_file(root, ACTIVE_INVENTORY, ledger["activeInventorySHA256"])
    overlay, old_overlay = load(checked_file(root, OVERLAY)), load(old_overlay_path)
    require(overlay["registeredDrawings"] == len(bank["frames"])
            and overlay["registeredOriginals"] == len(inventory["originals"])
            and overlay["newSourceRegistration"] == "source-registration-stage67.json",
            "Overlay registration totals differ")
    changed_fields = {"registeredDrawings", "registeredOriginals",
                      "newSourceRegistration", "sourceRegistrationNote", "newDrawings", "newNativeCalls"}
    require(all(overlay.get(key) == value for key, value in old_overlay.items()
                if key not in changed_fields), "Historical overlay metadata changed")
    require(overlay["newDrawings"] == old_overlay["newDrawings"] + len(appended)
            and overlay["newNativeCalls"] == old_overlay["newNativeCalls"] + len(batches),
            "Cumulative checkpoint generation counts differ from immutable baseline plus new records")
    prior_index = prior_index_and_metadata(root, baseline, ledger, len(bank["frames"]),
                                           len(inventory["originals"]), baseline_drawings, baseline_originals)
    legacy = historical_regression(root, baseline)
    return {"passed": True, "stage": 67,
            "registrationOnlyNativeDrawings": legacy["result"]["registrationOnlyNativeDrawings"] + len(appended),
            "registrationOnlyNativeOriginals": legacy["result"]["registrationOnlyNativeOriginals"] + len(batches), "baselineDrawings": baseline_drawings,
            "baselineOriginals": baseline_originals, "newNativeDrawings": len(appended),
            "newNativeOriginals": len(batches), "totalBankDrawingIDs": len(bank["frames"]),
            "totalOriginalPromptPairs": len(inventory["originals"]),
            "oldBankInventoryAndMapPrefixesExact": True, "activeInventoryUnchanged": True,
            "newSourceCellRoundtripsExact": True, "legacyStage65ContinuationRegression": legacy, "priorSourceIndexVerification":prior_index,
            "oldLessonsPrefixExact":True,
            "registrationMakesNativeCalls": 0, "acceptedUsesAdded": 0,
            "runtimeAdmission": False, "sourceAppearanceOrSupportApproved": False}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).parent)
    arguments = parser.parse_args()
    try:
        print(json.dumps(verify(arguments.root), sort_keys=True))
    except (VerificationError, OSError, ValueError, KeyError, TypeError) as error:
        print(json.dumps({"passed": False, "error": str(error), "runtimeAdmission": False}),
              file=sys.stderr)
        raise SystemExit(1)
