"""Verify exact direct pins are present in the frozen local quality environment."""

from __future__ import annotations

import argparse
import re
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend-inference"
PIN = re.compile(r"([A-Za-z0-9_.-]+)==([A-Za-z0-9_.+!-]+)")


def normalized(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def pins(path: Path, visited: frozenset[Path] = frozenset()) -> dict[str, str]:
    path = path.resolve()
    if path in visited:
        raise ValueError("Cyclic requirements include")
    result: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("-r "):
            additions = pins(path.parent / line[3:].strip(), visited | {path})
        else:
            match = PIN.fullmatch(line)
            if match is None:
                raise ValueError(f"Require exact local dependency pins in {path.name}")
            name, expected = match.groups()
            additions = {normalized(name): expected}
        for name, expected in additions.items():
            if name in result and result[name] != expected:
                raise ValueError(f"Conflicting dependency pin: {name}")
            result[name] = expected
    return result


def verify(*, declarations: Path, lock: Path, environment: bool = True) -> int:
    direct = pins(declarations)
    frozen = pins(lock)
    for name, expected in direct.items():
        if frozen.get(name) != expected:
            raise ValueError(f"Quality lock must include the declared pin for {name}")
    if environment:
        for name, expected in frozen.items():
            try:
                installed = version(name)
            except PackageNotFoundError:
                raise ValueError(f"Missing locked dependency: {name}") from None
            if installed != expected:
                raise ValueError(
                    f"Installed dependency differs from quality lock: {name}"
                )
    return len(frozen)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--declarations", type=Path, default=BACKEND / "requirements-quality.txt"
    )
    parser.add_argument(
        "--lock", type=Path, default=BACKEND / "requirements-quality.lock"
    )
    parser.add_argument("--skip-environment", action="store_true")
    args = parser.parse_args()
    count = verify(
        declarations=args.declarations,
        lock=args.lock,
        environment=not args.skip_environment,
    )
    print(f"{count} frozen dependencies and direct declaration pins verified")


if __name__ == "__main__":
    main()
