import importlib.util
import json
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


prepare = load("prepare_public", ROOT / "scripts" / "prepare_public.py")
package = load("package_release", ROOT / "scripts" / "package_release.py")


class PackageTests(unittest.TestCase):
    def test_privacy_patterns_match_at_both_release_boundaries(self):
        self.assertEqual(
            [(p.pattern, p.flags) for p in prepare.SECRET_PATTERNS],
            [(p.pattern, p.flags) for p in package.PATTERNS],
        )
        self.assertEqual(prepare.PROJECTION_SCOPE, package.PROJECTION_SCOPE)

    # Kept for the adjacent boundary-regression test, which needs a minimal
    # hash-listed prepared projection before it replaces the top-level brain directory.
    def fixture(self, root):
        target = root / "brain" / "index.md"
        target.parent.mkdir(parents=True)
        target.write_text("synthetic\n")
        digest = __import__("hashlib").sha256(target.read_bytes()).hexdigest()
        (root / "PUBLIC_PROJECTION.json").write_text(json.dumps({
            "schema_version": 1, "version": package.VERSION, "scope": package.PROJECTION_SCOPE,
            "files": {"brain/index.md": digest},
        }))

    def test_projection_is_complete_and_excludes_private_boundaries(self):
        with tempfile.TemporaryDirectory() as directory:
            public = Path(directory) / "public"
            result = prepare.materialize(ROOT, public)
            manifest = json.loads((public / "PUBLIC_PROJECTION.json").read_text())
            names = set(manifest["files"])
            self.assertEqual(result["version"], package.VERSION)
            self.assertIn("pyproject.toml", names)
            self.assertIn("chatgpt_ads_brain/cli.py", names)
            self.assertIn("tests/test_packaging.py", names)
            self.assertIn("scripts/prepare_public.py", names)
            self.assertIn("acceptance/v030/fixture.json", names)
            self.assertIn("assets/chatgpt-ads-cover.webp", prepare.FILES)
            self.assertIn("assets/chatgpt-ads-workflow.webp", prepare.FILES)
            self.assertIn("requirements/validation.txt", prepare.FILES)
            self.assertIn("requirements/security.txt", prepare.FILES)
            self.assertIn(".secrets.baseline", prepare.FILES)
            self.assertNotIn("references/reviews/pack-validation.json", names)
            self.assertFalse(any(part in {".raw", "private-workspaces", "reviews", "legacy-v0.1"} for name in names for part in Path(name).parts))

    def test_archive_is_reproducible_from_unchanged_projection(self):
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            public = directory / "public"
            prepare.materialize(ROOT, public)
            first, second = directory / "one.zip", directory / "two.zip"
            package.build(public, first)
            package.build(public, second)
            self.assertEqual(first.read_bytes(), second.read_bytes())
            with zipfile.ZipFile(first) as archive:
                self.assertIn(f"{package.PREFIX}/README.md", archive.namelist())
                self.assertIn(f"{package.PREFIX}/PUBLIC_PROJECTION.json", archive.namelist())
                self.assertNotIn(f"{package.PREFIX}/.raw/research-captures/manifest.json", archive.namelist())

    def test_archive_refuses_changed_or_unprepared_source(self):
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            with self.assertRaisesRegex(ValueError, "prepared public projection"):
                package.build(directory, directory / "no.zip")
            partial = directory / "partial"
            partial.mkdir()
            (partial / "README.md").write_text("copied before interruption\n")
            with self.assertRaisesRegex(ValueError, "prepared public projection"):
                package.build(partial, directory / "partial.zip")
            public = directory / "public"
            prepare.materialize(ROOT, public)
            (public / "README.md").write_text("changed\n")
            with self.assertRaisesRegex(ValueError, "changed after preparation"):
                package.build(public, directory / "changed.zip")

    def test_manifest_rejects_portability_escape_paths_and_bad_hashes(self):
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            public = directory / "public"
            prepare.materialize(ROOT, public)
            marker = public / "PUBLIC_PROJECTION.json"
            manifest = json.loads(marker.read_text())
            cases = {
                "../outside.md": "unsafe manifest path",
                "C:\\outside.md": "unsafe manifest path",
                "folder\\entry.md": "unsafe manifest path",
                "/absolute.md": "unsafe manifest path",
                "folder/./entry.md": "unsafe manifest path",
            }
            for path, expected in cases.items():
                altered = dict(manifest)
                altered["files"] = {path: "0" * 64}
                marker.write_text(json.dumps(altered))
                with self.assertRaisesRegex(ValueError, expected):
                    list(package.selected(public))
            altered = dict(manifest)
            altered["files"] = {"README.md": "not-a-sha256"}
            marker.write_text(json.dumps(altered))
            with self.assertRaisesRegex(ValueError, "invalid manifest hash"):
                list(package.selected(public))

    def test_marker_is_scanned_strict_and_cannot_list_reserved_files(self):
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            public = directory / "public"
            prepare.materialize(ROOT, public)
            marker = public / "PUBLIC_PROJECTION.json"
            manifest = json.loads(marker.read_text())
            with_extra = dict(manifest)
            with_extra["unexpected"] = "synthetic"
            marker.write_text(json.dumps(with_extra))
            with self.assertRaisesRegex(ValueError, "unknown or missing fields"):
                list(package.selected(public))
            marker.write_text(json.dumps(manifest))
            sensitive_extra = dict(manifest)
            sensitive_extra["note"] = "AKIA" + "A" * 16
            marker.write_text(json.dumps(sensitive_extra))
            with self.assertRaisesRegex(ValueError, "sensitive-pattern match: PUBLIC_PROJECTION.json"):
                list(package.selected(public))
            reserved = dict(manifest)
            reserved["files"] = {"PUBLIC_PROJECTION.json": "0" * 64}
            marker.write_text(json.dumps(reserved))
            with self.assertRaisesRegex(ValueError, "reserved manifest path"):
                list(package.selected(public))

    def test_marker_rejects_duplicate_json_keys_including_nested_objects(self):
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            public = directory / "public"
            prepare.materialize(ROOT, public)
            marker = public / "PUBLIC_PROJECTION.json"
            manifest = json.loads(marker.read_text())
            digest = manifest["files"]["README.md"]
            nested_duplicate = (
                '{"schema_version":1,"version":' + json.dumps(package.VERSION)
                + ',"scope":' + json.dumps(package.PROJECTION_SCOPE)
                + ',"files":{"README.md":' + json.dumps(digest)
                + ',"README.md":' + json.dumps(digest) + "}}"
            )
            marker.write_text(nested_duplicate)
            with self.assertRaisesRegex(ValueError, "duplicate JSON key"):
                list(package.selected(public))
            top_level_duplicate = (
                '{"schema_version":1,"schema_version":1,"version":' + json.dumps(package.VERSION)
                + ',"scope":' + json.dumps(package.PROJECTION_SCOPE)
                + ',"files":' + json.dumps(manifest["files"], sort_keys=True) + "}"
            )
            marker.write_text(top_level_duplicate)
            with self.assertRaisesRegex(ValueError, "duplicate JSON key"):
                list(package.selected(public))

    def test_expanded_patterns_cover_synthetic_access_key_shape(self):
        synthetic = b"AKIA" + b"A" * 16
        self.assertTrue(any(pattern.search(synthetic) for pattern in prepare.SECRET_PATTERNS))


if __name__ == "__main__":
    unittest.main()
