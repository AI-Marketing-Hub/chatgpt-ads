#!/usr/bin/env python3
"""Offline secret scan with reviewed, value-hashed exceptions; never print values."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
EXCLUDE = r'(^|/)(\.git/|\.venv/|__pycache__/|\.secrets\.baseline$|PUBLIC_PROJECTION\.json$|PACKAGE_MANIFEST\.json$)'


def scan(root: Path):
    result = subprocess.run([sys.executable, '-m', 'detect_secrets', 'scan', '--all-files', '--no-verify', '--exclude-files', EXCLUDE, '.'], cwd=root, capture_output=True, text=True, check=True)
    return json.loads(result.stdout)['results']


def inspect_marker(path: Path):
    # Manifests are omitted from entropy exceptions to avoid a manifest/baseline
    # hash cycle. Their complete bytes still pass the package's pattern gate.
    from package_release import PATTERNS, PROJECTION_SCOPE, parse_marker
    raw = path.read_bytes()
    if any(pattern.search(raw) for pattern in PATTERNS):
        raise ValueError('sensitive marker content')
    data = parse_marker(raw)
    allowed = {'schema_version', 'version', 'scope', 'files'} if path.name == 'PUBLIC_PROJECTION.json' else {'version', 'source', 'files'}
    if not isinstance(data, dict) or set(data) - allowed or not isinstance(data.get('files'), dict):
        raise ValueError('unexpected marker metadata')
    if not re.fullmatch(r'[0-9]+\.[0-9]+\.[0-9]+', str(data.get('version', ''))):
        raise ValueError('invalid marker version')
    if path.name == 'PUBLIC_PROJECTION.json' and (data.get('schema_version') != 1 or data.get('scope') != PROJECTION_SCOPE):
        raise ValueError('unexpected projection scope')
    if path.name == 'PACKAGE_MANIFEST.json' and data.get('source') != 'prepared public projection':
        raise ValueError('unexpected package scope')
    for name, digest in data['files'].items():
        if not isinstance(name, str) or not isinstance(digest, str) or not re.fullmatch(r'[0-9a-f]{64}', digest):
            raise ValueError('invalid marker entry')


def inspect_baseline(raw):
    from package_release import PATTERNS, parse_marker
    if any(pattern.search(raw) for pattern in PATTERNS):
        raise ValueError('sensitive baseline content')
    data = parse_marker(raw)
    if set(data) != {'schema_version', 'results'} or data['schema_version'] != 1 or not isinstance(data['results'], dict):
        raise ValueError('unexpected baseline metadata')
    for name, rows in data['results'].items():
        if not re.fullmatch(r'[A-Za-z0-9._/-]+', name) or not isinstance(rows, list):
            raise ValueError('invalid baseline entry')
        for row in rows:
            if set(row) != {'type', 'hashed_secret'} or row['type'] not in {'Hex High Entropy String', 'Secret Keyword'} or not re.fullmatch(r'[0-9a-f]{40}', row['hashed_secret']):
                raise ValueError('unreviewed baseline schema')
    return data


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--history', action='store_true', help='also scan every reachable historical blob and commit')
    args = parser.parse_args()
    root = args.root.resolve()
    baseline = inspect_baseline((root / '.secrets.baseline').read_bytes())
    approved = {(name, row['type'], row['hashed_secret']) for name, rows in baseline['results'].items() for row in rows}
    findings = []
    counts = {'tree_candidates': 0, 'history_candidates': 0, 'history_objects': 0}

    def assess(directory, mapping=None, label='tree'):
        for file, rows in scan(directory).items():
            path = (directory / file).resolve()
            relative = mapping[path.name] if mapping is not None else path.relative_to(directory).as_posix()
            for row in rows:
                counts[label + '_candidates'] += 1
                if (relative, row['type'], row['hashed_secret']) not in approved:
                    findings.append({'surface': label, 'file': relative, 'line': row['line_number'], 'type': row['type']})
        for name in ('PUBLIC_PROJECTION.json', 'PACKAGE_MANIFEST.json'):
            for path in directory.rglob(name):
                if '.git' in path.parts or '.venv' in path.parts:
                    continue
                try:
                    inspect_marker(path)
                except (ValueError, TypeError):
                    findings.append({'surface': label, 'file': name, 'type': 'manifest validation'})

    assess(root)
    if args.history:
        objects = subprocess.check_output(['git', 'rev-list', '--objects', '--all'], cwd=root, text=True).splitlines()
        with tempfile.TemporaryDirectory() as temp:
            directory = Path(temp)
            mapping = {}
            for row in objects:
                oid, _, name = row.partition(' ')
                kind = subprocess.check_output(['git', 'cat-file', '-t', oid], cwd=root, text=True).strip()
                if kind not in {'blob', 'commit', 'tag'}:
                    continue
                counts['history_objects'] += 1
                raw = subprocess.check_output(['git', 'cat-file', kind, oid], cwd=root)
                if Path(name).name in {'PUBLIC_PROJECTION.json', 'PACKAGE_MANIFEST.json'}:
                    marker_dir = directory / oid
                    marker_dir.mkdir()
                    (marker_dir / Path(name).name).write_bytes(raw)
                    continue
                if name == '.secrets.baseline':
                    inspect_baseline(raw)
                    continue  # reviewed detector hashes, not original secret values
                (directory / oid).write_bytes(raw)
                mapping[oid] = name or '__git_metadata__'
            assess(directory, mapping, 'history')
    print(json.dumps({'status': 'fail' if findings else 'pass', 'findings': findings, 'counts': counts, 'scope': 'offline detectors and reviewed exceptions; not proof of absence'}, indent=2))
    return bool(findings)


if __name__ == '__main__':
    raise SystemExit(main())
