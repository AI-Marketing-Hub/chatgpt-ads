#!/usr/bin/env python3
"""Build a deterministic ZIP from an already prepared public source tree."""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import re
import sys
import zipfile
from pathlib import Path, PurePosixPath

try:
    from safe_io import read_regular, reject_symlinks, write_new
except ImportError:  # imported as a module from the source root
    from scripts.safe_io import read_regular, reject_symlinks, write_new

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
    re.compile(rb"AKIA[0-9A-Z]{16}"),
    re.compile(rb"AIza[0-9A-Za-z_-]{35}"),
    re.compile(rb"glpat-[A-Za-z0-9_-]{20,}"),
    re.compile(rb"xox[baprs]-[A-Za-z0-9-]{20,}"),
    re.compile(rb"sk_(?:live|test)_[A-Za-z0-9]{16,}"),
    re.compile(rb"(?i:authorization:\s*bearer\s+)[A-Za-z0-9._-]{12,}"),
    re.compile(rb"/var/home/[A-Za-z0-9_-]+/"),
)
FORBIDDEN_PARTS = frozenset({".git", ".raw", "__pycache__", "dist", "legacy-v0.1", "private-workspaces", "reviews"})
PROJECTION_SCOPE = "allowlisted public source projection; canonical evidence and local workspaces are excluded"
MARKER_KEYS = frozenset({"schema_version", "version", "scope", "files"})
RESERVED_MANIFEST_PATHS = frozenset({"PUBLIC_PROJECTION.json", "PACKAGE_MANIFEST.json"})


def selected(source: Path):
    source = reject_symlinks(source)
    marker = reject_symlinks(source / "PUBLIC_PROJECTION.json")
    if not marker.is_file():
        raise ValueError("source is not a prepared public projection")
    marker_data = read_regular(marker)
    if any(pattern.search(marker_data) for pattern in PATTERNS):
        raise ValueError("sensitive-pattern match: PUBLIC_PROJECTION.json")
    manifest = json.loads(marker_data.decode())
    if not isinstance(manifest, dict) or set(manifest) != MARKER_KEYS:
        raise ValueError("public projection marker has unknown or missing fields")
    if (
        manifest.get("schema_version") != 1
        or manifest.get("version") != VERSION
        or manifest.get("scope") != PROJECTION_SCOPE
    ):
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
        if relative_text in RESERVED_MANIFEST_PATHS:
            raise ValueError(f"reserved manifest path: {relative_text}")
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
    yield Path("PUBLIC_PROJECTION.json"), marker_data


def build(source: Path, out: Path) -> dict:
    entries = list(selected(source))
    source_hashes = {relative.as_posix(): hashlib.sha256(data).hexdigest() for relative, data in entries}
    package_manifest = json.dumps(
        {"version": VERSION, "files": source_hashes, "source": "prepared public projection"},
        indent=2,
        sort_keys=True,
    ).encode() + b"\n"
    expected = {f"{PREFIX}/{relative.as_posix()}": data for relative, data in entries}
    expected[f"{PREFIX}/PACKAGE_MANIFEST.json"] = package_manifest
    archive_bytes = io.BytesIO()
    with zipfile.ZipFile(archive_bytes, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for relative, data in entries:
            info = zipfile.ZipInfo(f"{PREFIX}/{relative.as_posix()}", date_time=(2026, 9, 11, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, data)
        info = zipfile.ZipInfo(f"{PREFIX}/PACKAGE_MANIFEST.json", date_time=(2026, 9, 11, 0, 0, 0))
        info.compress_type = zipfile.ZIP_DEFLATED
        info.external_attr = 0o100644 << 16
        archive.writestr(info, package_manifest)
    payload = archive_bytes.getvalue()
    with zipfile.ZipFile(io.BytesIO(payload)) as archive:
        names = archive.namelist()
        if len(names) != len(set(names)) or set(names) != set(expected):
            raise ValueError("archive inventory verification failed")
        for name, source_data in expected.items():
            if hashlib.sha256(archive.read(name)).digest() != hashlib.sha256(source_data).digest():
                raise ValueError(f"archive byte verification failed: {name}")
    out = Path(out).absolute()
    try:
        write_new(out, payload)
    except FileExistsError as exc:
        raise ValueError("output exists; choose a new path") from exc
    return {"artifact": str(out), "sha256": hashlib.sha256(payload).hexdigest(), "files": len(entries), "version": VERSION}


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
