"""Map review candidates through the existing generated identification validator."""

from __future__ import annotations

from pathlib import Path

from app.models.identification import IdentificationEvent, validate_identification

from .contracts import AudioCompletedEvent


def identification_candidates(
    result: AudioCompletedEvent, *, schema_path: Path
) -> list[IdentificationEvent]:
    """PRIVATE review inputs only. No owner, admission or confirmation is invented."""
    output: list[IdentificationEvent] = []
    for review in result.reviewCandidates:
        raw = result.rawCandidates[review.rawCandidateIndex]
        event_id = f"audio:{result.requestId}:{review.rawCandidateIndex}"
        output.append(
            validate_identification(
                {
                    "schemaVersion": 2,
                    "id": event_id,
                    "species": {
                        "id": review.speciesId,
                        "commonName": review.commonName,
                        "scientificName": review.scientificName,
                    },
                    "observedAt": result.observedAt,
                    "source": {
                        "kind": "fixture"
                        if result.provenance.inputKind == "synthetic-fixture"
                        else "model",
                        "label": "Synthetic technical fixture candidate"
                        if result.provenance.inputKind == "synthetic-fixture"
                        else "Audio model candidate for review",
                        "sourceEventId": event_id,
                        "provider": result.provenance.providerId,
                        "modelVersion": result.provenance.modelVersion,
                    },
                    "confidence": raw.confidence,
                    "recordingId": result.recording.id,
                    "metadata": {
                        "audioContractVersion": 1,
                        "modelSha256": result.provenance.modelSha256,
                        "taxonomyVersion": result.provenance.taxonomyVersion,
                        "startFrame": raw.startFrame,
                        "endFrame": raw.endFrame,
                        "analyzedSampleRate": result.summary.analyzedSampleRate,
                    },
                },
                schema_path=schema_path,
            )
        )
    return output
