# Optional local ONNX provider

Added a separate `app.audio_onnx` adapter and pinned optional dependencies. It loads
only an operator-selected local manifest/model bundle, verifies digest/profile and
license-review metadata, rejects external/custom/control-flow/random graph features,
and performs actual bounded CPU inference. No bird model, trained weights, recording
or cloud provider was downloaded or used. Core service imports remain independent
of numerical/native packages.

The Pydantic model manifest exports a deterministic validation schema and a
technical golden example. Generated arithmetic ONNX graphs provide the only actual
runtime execution evidence. Tests cover scores, zero padding with actual evidence
bounds, checksum/corruption/license/path/shape failures and native run termination.

During fixture validation the current ONNX Runtime attempted to create a telemetry
session sidecar before its normal telemetry-disable API ran. The adapter now sets
the runtime's initialization disable flag before importing it, and also disables
events through the native API. A fresh-process rerun produced neither warning nor
sidecar. The test-generated sidecar was moved to /tmp; no existing application data
or credentials were changed.

Also moved provider pin/license gates ahead of private audio download: an owner
permit is checked, but unconfigured or mismatched providers never retrieve bytes.
HTTP permit checks remain snapshots, not an atomic derived-output commit.
