"""Execute tiny generated arithmetic ONNX graphs, never trained bird models."""

from __future__ import annotations

import hashlib
import json
import tempfile
import threading
import unittest
from collections.abc import Mapping, Sequence
from pathlib import Path

import numpy as np
import numpy.typing as npt
import onnx
from onnx import TensorProto, helper

from app.audio_onnx.provider import NodeMetadata, ONNXProvider, RunOptions
from app.audio_pipeline.contracts import (
    AudioAnalyzeCommand,
    AudioCompletedEvent,
    ModelPin,
)
from app.audio_pipeline.fixtures import (
    FIXTURE_OWNER,
    FixtureStorage,
    fixture_command,
    synthetic_wav,
)
from app.audio_pipeline.pcm import Chunk
from app.audio_pipeline.providers import (
    ProviderConfigurationError,
    ProviderExecutionError,
)
from app.audio_pipeline.service import AudioService


def technical_model(*, input_frames: int = 48000, nan_output: bool = False) -> bytes:
    nodes = [
        helper.make_node("Mul", ["waveform", "waveform"], ["squared"]),
        helper.make_node(
            "ReduceMean", ["squared"], ["probabilities"], axes=[1], keepdims=1
        ),
    ]
    if nan_output:
        nodes = [
            helper.make_node(
                "Constant",
                [],
                ["probabilities"],
                value=helper.make_tensor(
                    "nan", TensorProto.FLOAT, [1, 1], [float("nan")]
                ),
            )
        ]
    graph = helper.make_graph(
        nodes,
        "synthetic-energy-no-bird-model",
        [
            helper.make_tensor_value_info(
                "waveform", TensorProto.FLOAT, [1, input_frames]
            )
        ],
        [helper.make_tensor_value_info("probabilities", TensorProto.FLOAT, [1, 1])],
    )
    model = helper.make_model(
        graph, opset_imports=[helper.make_opsetid("", 13)], ir_version=10
    )
    serialized: object = model.SerializeToString()
    if not isinstance(serialized, bytes):
        raise TypeError("ONNX serialization did not return bytes")
    return serialized


def manifest_value(model: bytes) -> dict[str, object]:
    return {
        "schemaVersion": 1,
        "kind": "audio.onnx-model",
        "providerId": "onnx-local",
        "modelVersion": "technical-energy-onnx-1",
        "modelSha256": hashlib.sha256(model).hexdigest(),
        "modelFilename": "model.onnx",
        "profile": "waveform16k-3s-probabilities-v1",
        "inputName": "waveform",
        "outputName": "probabilities",
        "taxonomyVersion": "technical-taxonomy-1",
        "labels": [
            {
                "label": "technical-signal",
                "speciesId": "technical-signal-unreviewed",
                "commonName": "Technical signal fixture",
                "scientificName": "No biological identification",
            }
        ],
        "license": {
            "status": "technical-fixture",
            "identifier": "Generated arithmetic test graph without trained weights",
            "reviewId": None,
            "reviewedAt": None,
        },
    }


class ONNXAdapterTests(unittest.TestCase):
    def setUp(self) -> None:
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        self.path = self.root / "manifest.json"
        self.data = technical_model()
        self.write_bundle()

    def write_bundle(self, *, changes: Mapping[str, object] | None = None) -> None:
        (self.root / "model.onnx").write_bytes(self.data)
        self.path.write_text(
            json.dumps({**manifest_value(self.data), **(changes or {})})
        )

    def test_actual_cpu_execution_silence_tone_and_partial_window(self) -> None:
        provider = ONNXProvider(self.path)
        self.assertEqual(provider.provenance.inputKind, "synthetic-fixture")
        for tone, expected in ((False, 0.0), (True, 0.0223)):
            data = synthetic_wav(tone=tone)
            command = AudioAnalyzeCommand.model_validate(
                {
                    **fixture_command(data).model_dump(),
                    "model": ModelPin(
                        providerId="onnx-local",
                        modelVersion=provider.manifest.modelVersion,
                        taxonomyVersion=provider.taxonomy.version,
                    ).model_dump(),
                    "reviewThreshold": 0.01,
                }
            )
            result = AudioService(
                FixtureStorage(data), provider, provider.taxonomy
            ).analyze(FIXTURE_OWNER, command)
            self.assertIsInstance(result, AudioCompletedEvent)
            if isinstance(result, AudioCompletedEvent):
                self.assertAlmostEqual(
                    result.rawCandidates[0].confidence, expected, places=4
                )
                self.assertEqual(len(result.reviewCandidates), 1 if tone else 0)
                self.assertEqual(result.rawCandidates[0].endFrame, 16000)
                self.assertEqual(
                    result.provenance.modelSha256, hashlib.sha256(self.data).hexdigest()
                )

    def test_digest_mismatch_and_corrupt_model_fail_before_execution(self) -> None:
        self.write_bundle(changes={"modelSha256": "0" * 64})
        with self.assertRaises(ProviderConfigurationError):
            ONNXProvider(self.path)
        self.data = b"not an ONNX graph private diagnostic"
        self.write_bundle()
        with self.assertRaises(ProviderConfigurationError) as raised:
            ONNXProvider(self.path)
        self.assertNotIn("private", str(raised.exception))

    def test_license_requires_explicit_review_before_actual_recordings(self) -> None:
        for status in ("unreviewed", "approved"):
            self.write_bundle(
                changes={
                    "license": {
                        "status": status,
                        "identifier": "unreviewed test license",
                        "reviewId": None,
                        "reviewedAt": None,
                    }
                }
            )
            with (
                self.subTest(status=status),
                self.assertRaises(ProviderConfigurationError),
            ):
                ONNXProvider(self.path)

    def test_paths_unknown_profiles_and_duplicate_taxonomy_are_rejected(self) -> None:
        labels = [
            {
                "label": "duplicate",
                "speciesId": "technical",
                "commonName": "Technical",
                "scientificName": "Technical",
            }
        ] * 2
        for changes in (
            {"modelFilename": "../private.onnx"},
            {"profile": "guessed-birdnet-profile"},
            {"labels": labels},
            {"ownerId": "injected"},
        ):
            self.write_bundle(changes=changes)
            with (
                self.subTest(changes=changes),
                self.assertRaises(ProviderConfigurationError),
            ):
                ONNXProvider(self.path)

    def test_symbolic_link_and_oversized_manifest_are_rejected(self) -> None:
        model_path = self.root / "model.onnx"
        renamed = self.root / "other.onnx"
        model_path.rename(renamed)
        model_path.symlink_to(renamed)
        with self.assertRaises(ProviderConfigurationError):
            ONNXProvider(self.path)
        self.path.write_bytes(b"x" * 65537)
        with self.assertRaises(ProviderConfigurationError):
            ONNXProvider(self.path)

    def test_shape_mismatch_is_not_silently_adapted(self) -> None:
        self.data = technical_model(input_frames=16000)
        self.write_bundle()
        with self.assertRaises(ProviderConfigurationError):
            ONNXProvider(self.path)

    def test_external_tensor_files_never_load(self) -> None:
        model = onnx.load_model_from_string(self.data)
        tensor = model.graph.initializer.add()
        tensor.name = "external"
        tensor.data_type = TensorProto.FLOAT
        tensor.dims.append(1)
        tensor.data_location = TensorProto.EXTERNAL
        entry = tensor.external_data.add()
        entry.key = "location"
        entry.value = "../../private-file"
        self.data = model.SerializeToString()
        self.write_bundle()
        with self.assertRaises(ProviderConfigurationError):
            ONNXProvider(self.path)

    def test_nonfinite_native_outputs_are_rejected(self) -> None:
        self.data = technical_model(nan_output=True)
        self.write_bundle()
        provider = ONNXProvider(self.path)
        with self.assertRaises(ProviderExecutionError):
            provider.infer(Chunk(0, 0, 1, (0.0,)), idempotency_key="synthetic-only")

    def test_execution_timeout_configuration_is_bounded(self) -> None:
        for seconds in (0, 11):
            with self.assertRaises(ValueError):
                ONNXProvider(self.path, timeout_seconds=seconds)

    def test_deadline_terminates_a_cooperative_native_run(self) -> None:
        provider = ONNXProvider(self.path, timeout_seconds=0.1)
        terminated = threading.Event()

        class SlowSession:
            def get_inputs(self) -> Sequence[NodeMetadata]:
                return []

            def get_outputs(self) -> Sequence[NodeMetadata]:
                return []

            def run(
                self,
                output_names: list[str],
                input_feed: dict[str, npt.NDArray[np.float32]],
                run_options: object,
            ) -> Sequence[object]:
                if not isinstance(run_options, RunOptions):
                    raise TypeError("Expected checked native run options")
                for _ in range(200):
                    if run_options.terminate:
                        terminated.set()
                        raise RuntimeError("Synthetic native timeout")
                    terminated.wait(0.005)
                raise RuntimeError("Test timer did not terminate")

        provider.session = SlowSession()
        with self.assertRaises(ProviderExecutionError):
            provider.infer(Chunk(0, 0, 1, (0.0,)), idempotency_key="synthetic-timeout")
        self.assertTrue(terminated.is_set())


if __name__ == "__main__":
    unittest.main()
