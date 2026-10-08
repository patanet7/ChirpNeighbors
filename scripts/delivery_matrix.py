#!/usr/bin/env python3
"""Validate the delivery graph and execute its declared local verification gates."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATUSES = {
    "partial_local",
    "in_progress",
    "implemented_local",
    "external_gate",
    "unintegrated",
}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--run", metavar="GATE", help="Run one gate ID or baseline")
    parser.add_argument(
        "--ui-repo", type=Path, default=ROOT.parent / "birdsong-yard-sprites"
    )
    parser.add_argument("--python", default=sys.executable)
    parser.add_argument("--onnx-python", default=sys.executable)
    parser.add_argument(
        "--output-dir", type=Path, default=Path("/tmp/chirp-system-verification")
    )
    args = parser.parse_args()
    matrix = json.loads((ROOT / "docs/delivery/matrix.json").read_text())
    assert matrix["version"] == 1
    items = matrix["workstreams"]
    ids = {item["id"] for item in items}
    assert len(ids) == len(items)
    for item in items:
        assert item["owner"] and item["status"] in STATUSES and item["acceptance"]
        assert all(dependency in ids for dependency in item["dependencies"])
        assert item["id"] not in item["dependencies"]

    def visit(identifier: str, path: frozenset[str]) -> None:
        assert identifier not in path, f"Circular dependency: {identifier}"
        item = next(entry for entry in items if entry["id"] == identifier)
        for dependency in item["dependencies"]:
            visit(dependency, path | {identifier})

    for identifier in ids:
        visit(identifier, frozenset())
    gates = matrix["gates"]
    assert len({gate["id"] for gate in gates}) == len(gates)
    for gate in gates:
        assert gate["repo"] in {"ui", "main", "backend"}
        assert gate["command"] and all(isinstance(arg, str) for arg in gate["command"])
    if args.run:
        selected = [
            gate
            for gate in gates
            if gate["id"] == args.run
            or (args.run == "baseline" and gate.get("baseline"))
        ]
        if not selected:
            parser.error("Unknown gate ID")
        roots = {
            "ui": args.ui_repo.resolve(),
            "main": ROOT,
            "backend": ROOT / "backend-inference",
        }
        values = {
            "python": args.python,
            "onnx_python": args.onnx_python,
            "ui_repo": str(args.ui_repo.resolve()),
            "main_repo": str(ROOT),
            "output_dir": str(args.output_dir.resolve()),
        }
        for gate in selected:
            command = [argument.format_map(values) for argument in gate["command"]]
            print(f"Running {gate['id']}: {' '.join(command)}", flush=True)
            subprocess.run(command, cwd=roots[gate["repo"]], check=True)
    print(
        f"Delivery matrix valid: {len(items)} workstreams, "
        f"{len(gates)} executable gates"
    )


if __name__ == "__main__":
    main()
