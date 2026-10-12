"""Reproducible pipeline metrics, not accuracy metrics for real bird recognition."""

from __future__ import annotations

from typing import TypedDict

from .contracts import AudioCompletedEvent
from .fixtures import FIXTURE_OWNER, FixtureStorage, fixture_command, synthetic_wav
from .providers import FIXTURE_TAXONOMY, SyntheticFixtureProvider
from .service import AudioService


class EvaluationCase(TypedDict):
    name: str
    expectedReview: bool
    actualReview: bool
    rawCount: int
    reviewCount: int


class EvaluationReport(TypedDict):
    schemaVersion: int
    scope: str
    modelVersion: str
    taxonomyVersion: str
    samplesAreSynthetic: bool
    cases: list[EvaluationCase]
    precision: float
    recall: float
    truePositive: int
    falsePositive: int
    trueNegative: int
    falseNegative: int


def evaluate() -> EvaluationReport:
    cases: list[EvaluationCase] = []
    for name, tone, rate, channels in (
        ("silence-mono-16k", False, 16000, 1),
        ("tone-mono-16k", True, 16000, 1),
        ("tone-stereo-48k", True, 48000, 2),
        ("silence-mono-8k", False, 8000, 1),
    ):
        data = synthetic_wav(tone=tone, rate=rate, channels=channels)
        result = AudioService(
            FixtureStorage(data), SyntheticFixtureProvider(), FIXTURE_TAXONOMY
        ).analyze(FIXTURE_OWNER, fixture_command(data))
        if not isinstance(result, AudioCompletedEvent):
            raise TypeError("Synthetic pipeline evaluation failed")
        cases.append(
            EvaluationCase(
                name=name,
                expectedReview=tone,
                actualReview=bool(result.reviewCandidates),
                rawCount=len(result.rawCandidates),
                reviewCount=len(result.reviewCandidates),
            )
        )
    tp = sum(case["expectedReview"] and case["actualReview"] for case in cases)
    fp = sum(not case["expectedReview"] and case["actualReview"] for case in cases)
    tn = sum(not case["expectedReview"] and not case["actualReview"] for case in cases)
    fn = sum(case["expectedReview"] and not case["actualReview"] for case in cases)
    return EvaluationReport(
        schemaVersion=1,
        scope="technical synthetic pipeline regression; not real-bird accuracy",
        modelVersion="energy-fixture-1",
        taxonomyVersion=FIXTURE_TAXONOMY.version,
        samplesAreSynthetic=True,
        cases=cases,
        precision=tp / (tp + fp) if tp + fp else 0.0,
        recall=tp / (tp + fn) if tp + fn else 0.0,
        truePositive=tp,
        falsePositive=fp,
        trueNegative=tn,
        falseNegative=fn,
    )
