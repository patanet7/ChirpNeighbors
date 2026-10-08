"""Create local mechanics-test files: arithmetic ONNX, synthetic tone and manifest.

This is NOT a trained bird model. The explicit test-only license review authorizes
this generated arithmetic fixture for an isolated mechanics test, never biological
recognition, production deployment or third-party model use.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from onnx import TensorProto, helper

from app.audio_pipeline.fixtures import synthetic_wav
from app.audio_pipeline.model_contracts import (
    AudioModelManifest,
    ModelLicense,
    ModelTaxon,
)

MODEL_VERSION = "technical-mechanics-arithmetic-v1"
TAXONOMY_VERSION = "technical-mechanics-taxonomy-v1"
SPECIES_ID = "technical-mechanics-signal"


def arithmetic_model() -> bytes:
    """A deterministic energy calculation; all weights/constants are authored here."""
    graph = helper.make_graph(
        [
            helper.make_node("Mul", ["waveform", "waveform"], ["squared"]),
            helper.make_node(
                "ReduceMean", ["squared"], ["energy"], axes=[1], keepdims=1
            ),
            helper.make_node("Mul", ["energy", "gain"], ["probabilities"]),
        ],
        "technical-mechanics-only-no-bird-classifier",
        [helper.make_tensor_value_info("waveform", TensorProto.FLOAT, [1, 48000])],
        [helper.make_tensor_value_info("probabilities", TensorProto.FLOAT, [1, 1])],
        initializer=[helper.make_tensor("gain", TensorProto.FLOAT, [1, 1], [40.0])],
    )
    model = helper.make_model(
        graph, opset_imports=[helper.make_opsetid("", 13)], ir_version=10
    )
    encoded: object = model.SerializeToString()
    if not isinstance(encoded, bytes):
        raise TypeError("ONNX serialization must return bytes")
    return encoded


def manifest_for(model: bytes) -> AudioModelManifest:
    return AudioModelManifest(
        schemaVersion=1,
        kind="audio.onnx-model",
        providerId="onnx-local",
        modelVersion=MODEL_VERSION,
        modelSha256=hashlib.sha256(model).hexdigest(),
        modelFilename="model.onnx",
        profile="waveform16k-3s-probabilities-v1",
        inputName="waveform",
        outputName="probabilities",
        taxonomyVersion=TAXONOMY_VERSION,
        labels=[
            ModelTaxon(
                label="technical-energy-fixture",
                speciesId=SPECIES_ID,
                commonName="Technical mechanics fixture",
                scientificName="No biological identification",
            )
        ],
        license=ModelLicense(
            status="approved",
            identifier="LicenseRef-Generated-Arithmetic-Fixture-Test-Only",
            reviewId="65489ed3-d26a-4e58-90a0-e31276465d00",
            reviewedAt="2026-10-08T00:00:00Z",
        ),
    )


def create_bundle(directory: Path) -> dict[str, str]:
    """Write only into a new/empty explicitly selected fixture directory."""
    if directory.is_symlink() or (
        directory.exists() and (not directory.is_dir() or any(directory.iterdir()))
    ):
        raise ValueError("Choose a new or empty mechanics-test directory")
    directory.mkdir(parents=True, exist_ok=True)
    model = arithmetic_model()
    manifest = manifest_for(model)
    data = synthetic_wav(tone=True, rate=16000, milliseconds=1000)
    (directory / "model.onnx").write_bytes(model)
    (directory / "manifest.json").write_text(manifest.model_dump_json(indent=2) + "\n")
    (directory / "synthetic-tone.wav").write_bytes(data)
    declaration = (
        "ISOLATED TECHNICAL MECHANICS TEST ONLY.\n"
        "The generated model calculates waveform energy. It has no bird training,\n"
        "taxonomy evidence, species accuracy, external weights or provider.\n"
        "The fixture review/approved license declaration covers this authored\n"
        "arithmetic graph in temporary integration tests only. It is not a real-model\n"
        "approval or permission to use this bundle with real recordings.\n"
    )
    (directory / "FIXTURE-ONLY.txt").write_text(declaration)
    return {
        "modelSha256": manifest.modelSha256,
        "audioSha256": hashlib.sha256(data).hexdigest(),
        "modelVersion": MODEL_VERSION,
        "taxonomyVersion": TAXONOMY_VERSION,
        "scope": "generated arithmetic mechanics test, no biological identification",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    arguments = parser.parse_args()
    print(json.dumps(create_bundle(arguments.output), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
