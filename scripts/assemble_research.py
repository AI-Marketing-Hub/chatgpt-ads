#!/usr/bin/env python3
"""Compatibility entrypoint for the incremental knowledge-core CLI."""

from knowledge_core import main


if __name__ == "__main__":
    raise SystemExit(main())
