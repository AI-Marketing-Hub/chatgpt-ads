#!/usr/bin/env python3
"""Build a deterministic ZIP from an already prepared public source tree."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import zipfile
from pathlib import Path, PurePosixPath

try:
    from safe_io import read_regular, reject_symlinks
except ImportError:  # imported as a module from the source root
    from scripts.safe_io import read_regular, reject_symlinks

ROOT = Path(__file__).resolve().parents[1]
try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - requires Python 3.11 by contract
    import tomli as tomllib
VERSION = tomllib.loads(read_regular(ROOT / "pyproject.toml").decode())["project"]["version"]
PREFIX = f"chatgpt-ads-brain-{VERSION}"
PATTERNS = (
    re.compile(rb"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    re.compile(rb"(?:sk-ant-|sk-|ghp_|github_pat_)[A-Za-z0-9_-]{20,}"),
    re.compile(rb"(?i:authorization:\s*bearer\s+)[A-Za-z0-9._-]{12,}"),
    re.compile(rb"/var/home/[A-Za-z0-9_-]+/"),
)
FORBIDDEN_PARTS = frozenset({".git", ".raw", "__pycache__", "dist", "legacy-v0.1", "private-workspaces", "reviews"})


def selected(source: Path):
    source = reject_symlinks(source)
    marker = source / "PUBLIC_PROJECTION.json"
    if not marker.is_file() or marker.is_symlink():
        raise ValueError("source is not a prepared public projection")
    manifest = json.loads(read_regular(marker).decode())
    if manifest.get("schema_version") != 1 or manifest.get("version") != VERSION:
        raise ValueError("public projection has an unsupported version")
    files = manifest.get("files")
    if not isinstance(files, dict) or not files:
        raise ValueError("public projection is missing its file manifest")
    for relative_text, expected in sorted(files.items()):
        if not isinstance(relative_text, str) or not isinstance(expected, str):
            raise ValueError("public projection has an invalid file manifest entry")
        # The manifest is a cross-platform archive contract. Native Path on a
        # POSIX runner would treat backslashes and drive letters as ordinary
        # characters, so validate the portable POSIX spelling explicitly.
        if (
            not relative_text
            or "\\" in relative_text
            or ":" in relative_text
            or relative_text.startswith("/")
        ):
            raise ValueError(f"unsafe manifest path: {relative_text}")
        relative = PurePosixPath(relative_text)
        if (
            relative.is_absolute()
            or "." in relative.parts
            or ".." in relative.parts
            or FORBIDDEN_PARTS.intersection(relative.parts)
            or relative.as_posix() != relative_text
        ):
            raise ValueError(f"unsafe manifest path: {relative_text}")
        if not re.fullmatch(r"[0-9a-f]{64}", expected):
            raise ValueError(f"invalid manifest hash: {relative_text}")
        path = reject_symlinks(source / relative)
        if not path.is_file():
            raise ValueError(f"manifest entry missing: {relative_text}")
        data = read_regular(path)
        if hashlib.sha256(data).hexdigest() != expected:
            raise ValueError(f"public projection changed after preparation: {relative_text}")
        if any(pattern.search(data) for pattern in PATTERNS):
            raise ValueError(f"sensitive-pattern match: {relative_text}")
        yield relative, data
    # Preserve the hash-listed source inventory so an extracted archive is
    # still a prepared projection and can be independently checked or repacked.
    yield Path("PUBLIC_PROJECTION.json"), read_regular(marker)


def build(source: Path, out: Path) -> dict:
    entries = list(selected(source))
    out = Path(out).absolute()
    reject_symlinks(out.parent)
    if out.exists():
        raise ValueError("output exists; choose a new path")
    out.parent.mkdir(parents=True, exist_ok=True)
    try:
        source_hashes = {relative.as_posix(): hashlib.sha256(data).hexdigest() for relative, data in entries}
        package_manifest = json.dumps(
            {"version": VERSION, "files": source_hashes, "source": "prepared public projection"},
            indent=2,
            sort_keys=True,
        ).encode() + b"\n"
        expected = {f"{PREFIX}/{relative.as_posix()}": data for relative, data in entries}
        expected[f"{PREFIX}/PACKAGE_MANIFEST.json"] = package_manifest
        with zipfile.ZipFile(out, "x", compression=zipfile.ZIP_DEFLATED) as archive:
            for relative, data in entries:
                info = zipfile.ZipInfo(f"{PREFIX}/{relative.as_posix()}", date_time=(2026, 9, 11, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = 0o100644 << 16
                archive.writestr(info, data)
            info = zipfile.ZipInfo(f"{PREFIX}/PACKAGE_MANIFEST.json", date_time=(2026, 9, 11, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, package_manifest)
        with zipfile.ZipFile(out) as archive:
            names = archive.namelist()
            if len(names) != len(set(names)) or set(names) != set(expected):
                raise ValueError("archive inventory verification failed")
            for name, source_data in expected.items():
                if hashlib.sha256(archive.read(name)).digest() != hashlib.sha256(source_data).digest():
                    raise ValueError(f"archive byte verification failed: {name}")
    except Exception:
        out.unlink(missing_ok=True)
        raise
    return {"artifact": str(out), "sha256": hashlib.sha256(out.read_bytes()).hexdigest(), "files": len(entries), "version": VERSION}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path, help="prepared public source directory")
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        print(json.dumps(build(args.source, args.out), indent=2))
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(str(error), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
