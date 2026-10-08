"""Optional CPU ONNX adapter for a reviewed, checksum-pinned local waveform model.

No model downloads, custom ops, external tensor files, client paths or trained
weights ship here. The narrowly supported profile is deliberately explicit.
"""

from __future__ import annotations

import hashlib
import importlib
import math
import os
import stat
import threading
from collections.abc import Sequence
from pathlib import Path
from typing import Protocol, runtime_checkable

import numpy as np
import numpy.typing as npt
import onnx

from app.audio_pipeline.contracts import ProviderProvenance
from app.audio_pipeline.model_contracts import AudioModelManifest
from app.audio_pipeline.pcm import CHUNK_FRAMES, Chunk
from app.audio_pipeline.providers import (
    Prediction,
    ProviderConfigurationError,
    ProviderExecutionError,
    Taxon,
    Taxonomy,
)

MAX_MODEL_BYTES = 32 * 1024 * 1024


@runtime_checkable
class NodeMetadata(Protocol):
    @property
    def name(self) -> str: ...
    @property
    def type(self) -> str: ...
    @property
    def shape(self) -> Sequence[object]: ...


@runtime_checkable
class Session(Protocol):
    def get_inputs(self) -> Sequence[NodeMetadata]: ...
    def get_outputs(self) -> Sequence[NodeMetadata]: ...
    def run(
        self,
        output_names: list[str],
        input_feed: dict[str, npt.NDArray[np.float32]],
        run_options: object,
    ) -> Sequence[object]: ...


@runtime_checkable
class SessionOptions(Protocol):
    intra_op_num_threads: int
    inter_op_num_threads: int
    log_severity_level: int


@runtime_checkable
class RunOptions(Protocol):
    terminate: bool
    log_severity_level: int


def _bounded_regular_file(path: Path, maximum: int) -> bytes:
    descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(descriptor, "rb") as source:
        metadata = os.fstat(source.fileno())
        if not stat.S_ISREG(metadata.st_mode) or not 0 < metadata.st_size <= maximum:
            raise ProviderConfigurationError("Model bundle file is outside limits")
        data = source.read(maximum + 1)
        if len(data) > maximum:
            raise ProviderConfigurationError("Model bundle file is outside limits")
        return data


class ONNXProvider:
    def __init__(self, manifest_path: Path, *, timeout_seconds: float = 5.0) -> None:
        if not 0.1 <= timeout_seconds <= 10:
            raise ValueError("Invalid model execution timeout")
        self.timeout_seconds = timeout_seconds
        try:
            manifest = AudioModelManifest.model_validate_json(
                _bounded_regular_file(manifest_path, 65536)
            )
            if manifest.license.status == "unreviewed" or (
                manifest.license.status == "approved"
                and (
                    manifest.license.reviewId is None
                    or manifest.license.reviewedAt is None
                )
            ):
                raise ProviderConfigurationError("A model license review is required")
            if len({taxon.label for taxon in manifest.labels}) != len(manifest.labels):
                raise ProviderConfigurationError("Model taxonomy labels must be unique")
            data = _bounded_regular_file(
                manifest_path.parent / manifest.modelFilename, MAX_MODEL_BYTES
            )
            if hashlib.sha256(data).hexdigest() != manifest.modelSha256:
                raise ProviderConfigurationError("Model digest mismatch")
            model = onnx.load_model_from_string(data)
            # This adapter deliberately excludes control-flow/subgraphs, custom
            # operators and external data so loading a manifest cannot fetch files.
            if (
                model.functions
                or model.training_info
                or model.graph.sparse_initializer
                or not 1 <= len(model.graph.node) <= 256
                or any(tensor.external_data for tensor in model.graph.initializer)
                or any(
                    node.domain not in ("", "ai.onnx")
                    or node.op_type
                    in (
                        "Loop",
                        "If",
                        "Scan",
                        "RandomNormal",
                        "RandomNormalLike",
                        "RandomUniform",
                        "RandomUniformLike",
                        "Multinomial",
                        "Bernoulli",
                        "Dropout",
                    )
                    or any(
                        attribute.type
                        in (
                            onnx.AttributeProto.GRAPH,
                            onnx.AttributeProto.GRAPHS,
                            onnx.AttributeProto.SPARSE_TENSOR,
                            onnx.AttributeProto.SPARSE_TENSORS,
                        )
                        or attribute.t.external_data
                        or any(tensor.external_data for tensor in attribute.tensors)
                        for attribute in node.attribute
                    )
                    for node in model.graph.node
                )
            ):
                raise ProviderConfigurationError("Unsupported model graph profile")
            onnx.checker.check_model(model, full_check=True)
            # ONNX Runtime lacks py.typed. Keep the untyped import at this checked
            # structural facade; public arrays, outputs and metadata are validated.
            # Disable native initialization telemetry before importing the runtime;
            # disable_telemetry_events alone is too late for initialization.
            os.environ["ORT_DISABLE_TELEMETRY"] = "1"
            runtime = importlib.import_module("onnxruntime")
            runtime.disable_telemetry_events()
            runtime.set_default_logger_severity(4)
            options: object = runtime.SessionOptions()
            if not isinstance(options, SessionOptions):
                raise ProviderConfigurationError("Unsupported runtime options API")
            options.intra_op_num_threads = 1
            options.inter_op_num_threads = 1
            options.log_severity_level = 4
            session: object = runtime.InferenceSession(
                data, sess_options=options, providers=["CPUExecutionProvider"]
            )
            if not isinstance(session, Session):
                raise ProviderConfigurationError("Unsupported runtime session API")
            inputs, outputs = session.get_inputs(), session.get_outputs()
            if (
                len(inputs) != 1
                or len(outputs) != 1
                or inputs[0].name != manifest.inputName
                or inputs[0].type != "tensor(float)"
                or list(inputs[0].shape) != [1, CHUNK_FRAMES]
                or outputs[0].name != manifest.outputName
                or outputs[0].type != "tensor(float)"
                or list(outputs[0].shape) != [1, len(manifest.labels)]
            ):
                raise ProviderConfigurationError(
                    "Model input/output does not match its profile"
                )
            self.manifest = manifest
            self.session = session
        except ProviderConfigurationError:
            raise
        except Exception:  # noqa: BLE001 - sanitize model/parser/native-runtime failures.
            raise ProviderConfigurationError(
                "Cannot load reviewed model bundle"
            ) from None

    @property
    def taxonomy(self) -> Taxonomy:
        return Taxonomy(
            self.manifest.taxonomyVersion,
            tuple(
                Taxon(t.label, t.speciesId, t.commonName, t.scientificName)
                for t in self.manifest.labels
            ),
        )

    @property
    def provenance(self) -> ProviderProvenance:
        fixture = self.manifest.license.status == "technical-fixture"
        return ProviderProvenance(
            providerId="onnx-local",
            modelVersion=self.manifest.modelVersion,
            modelSha256=self.manifest.modelSha256,
            taxonomyVersion=self.manifest.taxonomyVersion,
            inputKind="synthetic-fixture" if fixture else "recording",
            licenseStatus="technical-fixture" if fixture else "approved",
            licenseIdentifier=self.manifest.license.identifier,
            preprocessingVersion="pcm16-mono-sinc16k-v1",
        )

    def infer(self, chunk: Chunk, *, idempotency_key: str) -> tuple[Prediction, ...]:
        if not 0 < len(chunk.samples) <= CHUNK_FRAMES:
            raise ProviderExecutionError("Invalid model window")
        values = np.zeros((1, CHUNK_FRAMES), dtype=np.float32)
        values[0, : len(chunk.samples)] = chunk.samples
        runtime = importlib.import_module("onnxruntime")
        options: object = runtime.RunOptions()
        if not isinstance(options, RunOptions):
            raise ProviderExecutionError("Unsupported runtime run options API")
        options.log_severity_level = 4

        def terminate() -> None:
            options.terminate = True

        deadline = threading.Timer(self.timeout_seconds, terminate)
        deadline.daemon = True
        deadline.start()
        try:
            outputs = self.session.run(
                [self.manifest.outputName], {self.manifest.inputName: values}, options
            )
        except Exception:  # noqa: BLE001 - native execution errors contain model details.
            raise ProviderExecutionError(
                "Model execution failed or timed out"
            ) from None
        finally:
            deadline.cancel()
        if len(outputs) != 1 or not isinstance(outputs[0], np.ndarray):
            raise ProviderExecutionError("Unsupported model output")
        scores = outputs[0]
        if scores.shape != (1, len(self.manifest.labels)) or scores.dtype != np.float32:
            raise ProviderExecutionError("Unsupported model output")
        predictions: list[Prediction] = []
        for index, taxon in enumerate(self.manifest.labels):
            confidence = float(scores[0, index])
            if not math.isfinite(confidence) or not 0 <= confidence <= 1:
                raise ProviderExecutionError("Model output is not a probability")
            predictions.append(Prediction(taxon.label, confidence))
        return tuple(predictions)
