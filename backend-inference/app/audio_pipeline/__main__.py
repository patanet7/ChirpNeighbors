"""Local synthetic-only CLI: python -m app.audio_pipeline evaluate|analyze-fixture."""

from __future__ import annotations

import argparse
import json

from .evaluation import evaluate
from .fixtures import FIXTURE_OWNER, FixtureStorage, fixture_command, synthetic_wav
from .providers import FIXTURE_TAXONOMY, SyntheticFixtureProvider
from .service import AudioService


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["evaluate", "analyze-fixture"])
    parser.add_argument(
        "--tone", action="store_true", help="Generate a 440Hz technical tone"
    )
    args = parser.parse_args()
    if args.command == "evaluate":
        print(json.dumps(evaluate(), indent=2, sort_keys=True))
    else:
        data = synthetic_wav(tone=args.tone)
        result = AudioService(
            FixtureStorage(data), SyntheticFixtureProvider(), FIXTURE_TAXONOMY
        ).analyze(FIXTURE_OWNER, fixture_command(data))
        print(result.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
