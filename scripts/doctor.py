#!/usr/bin/env python3
"""Report runtime and guarded-filesystem capabilities without reading secrets."""
from __future__ import annotations

import argparse
import importlib.util
import json
import platform
import sys
from typing import Iterable

try:
    from safe_io import filesystem_capabilities
except ImportError:  # pragma: no cover - package-style imports
    from scripts.safe_io import filesystem_capabilities


def report() -> dict[str, object]:
    filesystem = filesystem_capabilities()
    restricted = filesystem["backend"] == "windows_restricted"
    return {
        "status": "limited" if restricted else "ready_for_local_posix_checks",
        "runtime": {
            "os_name": __import__("os").name,
            "system": platform.system(),
            "release": platform.release(),
            "python": platform.python_version(),
            "implementation": platform.python_implementation(),
        },
        "dependencies": {
            "jsonschema": importlib.util.find_spec("jsonschema") is not None,
            "external_dependencies": "none required for guarded filesystem helpers",
        },
        "filesystem": filesystem,
        "permitted_workflows": (
            [
                "read package Markdown with a normal text viewer",
                "run standalone analysis tools with user-controlled input paths, pending native Windows evidence",
            ]
            if restricted
            else [
                "bounded package retrieval and validation",
                "hash-bound knowledge transactions with explicit recovery",
                "local simulated-operation checkpoints and account locks",
            ]
        ),
        "blocked_workflows": (
            [
                "knowledge-core guarded retrieval, validation, updates, locking, and recovery",
                "operating-core guarded record reads/writes, locks, checkpoints, and promoted-learning output",
            ]
            if restricted
            else []
        ),
        "native_validation": "This command observes the current host only. It does not prove native Windows support.",
        "secrets": "not inspected",
    }


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="reserved for stable machine-readable output")
    parser.parse_args(list(argv) if argv is not None else None)
    print(json.dumps(report(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
