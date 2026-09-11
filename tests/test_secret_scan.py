"""Integration checks use synthetic canaries, never valid credentials."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts' / 'scan_secrets.py'


@unittest.skipUnless(importlib.util.find_spec('detect_secrets'), 'security dependencies installed in dedicated CI job')
class SecretScanTests(unittest.TestCase):
    def test_current_tree_candidate_fails_without_printing_value(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / '.secrets.baseline').write_text('{"schema_version":1,"results":{}}')
            value = 'audit-only-' + 'canary-value-please-ignore'
            (root / 'sample.json').write_text(json.dumps({'password': value}))
            result = subprocess.run([sys.executable, str(SCRIPT), '--root', str(root)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 1, result.stderr)
            self.assertNotIn(value, result.stdout + result.stderr)
            self.assertTrue(json.loads(result.stdout)['findings'])

    def test_deleted_historical_candidate_still_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            def git(*args):
                return subprocess.run(['git', '-c', 'core.hooksPath=/dev/null', '-c', 'commit.gpgsign=false', *args], cwd=root, check=True, capture_output=True)
            git('init')
            git('config', 'user.name', 'Synthetic Test')
            git('config', 'user.email', 'test@example.invalid')
            (root / '.secrets.baseline').write_text('{"schema_version":1,"results":{}}')
            value = 'audit-only-' + 'historical-canary-value'
            (root / 'sample.json').write_text(json.dumps({'password': value}))
            git('add', '.')
            git('commit', '-m', 'synthetic fixture')
            (root / 'sample.json').unlink()
            git('add', '-u')
            git('commit', '-m', 'remove fixture')
            result = subprocess.run([sys.executable, str(SCRIPT), '--root', str(root), '--history'], capture_output=True, text=True)
            self.assertEqual(result.returncode, 1, result.stderr)
            self.assertNotIn(value, result.stdout + result.stderr)
            self.assertTrue(any(row['surface'] == 'history' for row in json.loads(result.stdout)['findings']))


if __name__ == '__main__':
    unittest.main()
