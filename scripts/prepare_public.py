#!/usr/bin/env python3
"""Create a reviewed public-source projection from this canonical checkout.

This command is deliberately a copier, not a sanitizer. Only files named by
the allowlist below can cross the canonical-to-public boundary. It never
deletes or modifies the canonical checkout and refuses an existing output.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

try:
    from safe_io import ensure_directory, read_regular, reject_symlinks, write_new
except ImportError:  # imported as a module from the source root
    from scripts.safe_io import ensure_directory, read_regular, reject_symlinks, write_new

ROOT = Path(__file__).resolve().parents[1]
try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - requires Python 3.11 by contract
    import tomli as tomllib
VERSION = tomllib.loads(read_regular(ROOT / "pyproject.toml").decode())["project"]["version"]

DIRECTORIES = (
    ".github", "brain", "chatgpt_ads_brain", "examples", "interfaces",
    "runtime", "scripts", "skills", "tests",
    "acceptance/measurement", "acceptance/native-research",
    "acceptance/policy", "acceptance/v030", "acceptance/workflows",
    "references/third-party-licenses",
)
FILES = (
    ".gitignore", ".secrets.baseline", "AGENTS.md", "BUILD_STATUS.md", "CHANGELOG.md", "CLAUDE.md", "CODEX.md",
    "CONTRIBUTING.md", "LICENSE", "README.md", "SECURITY.md", "SKILL.md",
    "SUPPORT.md", "THIRD_PARTY_NOTICES.md", "pyproject.toml",
    "assets/chatgpt-ads-cover.webp", "assets/chatgpt-ads-workflow.webp",
    "acceptance/README.md", "acceptance/matrix.json",
    "docs/KNOWLEDGE.md", "docs/LIVE_ACCEPTANCE.md", "docs/MIGRATION.md",
    "docs/OPERATOR_KIT.md", "docs/PRODUCT_BOUNDARIES.md", "docs/QUICKSTART.md",
    "docs/RELEASE_DRAFT.md", "docs/WINDOWS.md",
    "requirements/security.txt", "requirements/validation.txt",
    "research-refresh/2026-09-11/evidence-note.md",
    "references/adapter-manifest.json", "references/capabilities.json",
    "references/claims.json", "references/contradictions.json", "references/coverage.json",
    "references/migration.json",
    "references/readiness.json", "references/reuse.json", "references/source-ledger.json",
)
FORBIDDEN_PARTS = frozenset({".git", ".raw", "__pycache__", "dist", "legacy-v0.1", "private-workspaces", "reviews"})
PROJECTION_SCOPE = "allowlisted public source projection; canonical evidence and local workspaces are excluded"
SECRET_PATTERNS = (
    re.compile(rb"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    re.compile(rb"(?:sk-ant-|sk-|ghp_|github_pat_)[A-Za-z0-9_-]{20,}"),
    re.compile(rb"AKIA[0-9A-Z]{16}"),
    re.compile(rb"AIza[0-9A-Za-z_-]{35}"),
    re.compile(rb"glpat-[A-Za-z0-9_-]{20,}"),
    re.compile(rb"xox[baprs]-[A-Za-z0-9-]{20,}"),
    re.compile(rb"sk_(?:live|test)_[A-Za-z0-9]{16,}"),
    re.compile(rb"(?i:authorization:\s*bearer\s+)[A-Za-z0-9._-]{12,}"),
    re.compile(rb"/var/home/[A-Za-z0-9_-]+/"),
)


def _read(path: Path) -> bytes:
    path = reject_symlinks(path)
    if not path.is_file():
        raise ValueError(f"required regular file missing: {path}")
    data = read_regular(path, 10 * 1024 * 1024)
    if any(pattern.search(data) for pattern in SECRET_PATTERNS):
        raise ValueError(f"sensitive-pattern match: {path}")
    return data


def selected(root: Path):
    """Yield sorted (relative path, bytes) entries from the explicit allowlist."""
    root = reject_symlinks(root)
    entries: set[Path] = set()
    for relative in DIRECTORIES:
        directory = root / relative
        if directory.is_symlink() or not directory.is_dir():
            raise ValueError(f"required public directory missing or unsafe: {relative}")
        entries.update(path for path in directory.rglob("*") if path.is_file() or path.is_symlink())
    for relative in FILES:
        entries.add(root / relative)
    for path in sorted(entries):
        relative = path.relative_to(root)
        if "__pycache__" in relative.parts or path.suffix in {".pyc", ".pyo"}:
            continue
        if FORBIDDEN_PARTS.intersection(relative.parts):
            raise ValueError(f"forbidden path selected: {relative}")
        yield relative, _read(path)


def materialize(root: Path, destination: Path) -> dict:
    root = reject_symlinks(root)
    destination = Path(destination).absolute()
    reject_symlinks(destination.parent)
    if destination.exists():
        raise ValueError(f"destination already exists: {destination}")
    entries = list(selected(root))
    for relative, data in entries:
        target = destination / relative
        ensure_directory(target.parent)
        write_new(target, data)
    hashes = {relative.as_posix(): hashlib.sha256(data).hexdigest() for relative, data in entries}
    manifest = {"schema_version": 1, "version": VERSION,
                "scope": PROJECTION_SCOPE,
                "files": hashes}
    write_new(destination / "PUBLIC_PROJECTION.json", json.dumps(manifest, indent=2, sort_keys=True).encode() + b"\n")
    return {"destination": str(destination), "files": len(entries), "version": VERSION}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True, type=Path, help="new public-source directory")
    args = parser.parse_args(argv)
    try:
        print(json.dumps(materialize(ROOT, args.out), indent=2))
    except (OSError, ValueError) as error:
        print(str(error), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
