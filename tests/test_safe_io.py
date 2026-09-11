#!/usr/bin/env python3
"""Platform-boundary tests for guarded filesystem helpers."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "scripts"))

from scripts import safe_io
from scripts import knowledge_core
from scripts import operating_core
import safe_io as runtime_safe_io


class SafeIOTests(unittest.TestCase):
    @unittest.skipUnless(os.name == "posix", "requires the POSIX descriptor backend")
    def test_posix_guarded_reads_writes_append_and_link_refusal(self) -> None:
        with tempfile.TemporaryDirectory(prefix="safe io unicode ") as temporary:
            root = Path(temporary) / "space Ω"
            target = root / "nested" / "record.json"
            safe_io.write_new(target, b"first")
            self.assertEqual(safe_io.read_regular(target), b"first")
            safe_io.append_regular(target, b"-second")
            self.assertEqual(safe_io.read_regular(target), b"first-second")
            safe_io.atomic_write(target, b"replacement")
            self.assertEqual(safe_io.read_regular(target), b"replacement")
            linked = root / "linked.json"
            linked.symlink_to(target)
            with self.assertRaisesRegex(safe_io.SafeIOError, "symlink"):
                safe_io.read_regular(linked)

    @unittest.skipUnless(os.name == "posix" and hasattr(os, "mkfifo"), "requires POSIX FIFO support")
    def test_bounded_read_rejects_fifo_without_waiting_for_a_writer(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fifo = Path(temporary) / "untrusted.fifo"
            os.mkfifo(fifo)
            child = (
                "import sys; from scripts.safe_io import SafeIOError, read_regular; "
                "\ntry:\n read_regular(sys.argv[1])\nexcept SafeIOError:\n raise SystemExit(0)\n"
                "raise SystemExit(1)"
            )
            result = subprocess.run(
                [sys.executable, "-c", child, str(fifo)],
                cwd=REPO,
                text=True,
                capture_output=True,
                check=False,
                timeout=3,
            )
            self.assertEqual(result.returncode, 0, result.stderr)

    @unittest.skipUnless(os.name == "posix" and hasattr(os, "mkfifo"), "requires POSIX FIFO support")
    def test_append_rejects_fifo_before_a_checkpoint_write(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fifo = Path(temporary) / "checkpoint.fifo"
            os.mkfifo(fifo)
            # Keep one read end open so the child reaches fstat after its
            # non-blocking write open instead of receiving ENXIO.
            reader = os.open(fifo, os.O_RDONLY | os.O_NONBLOCK)
            try:
                child = (
                    "import sys; from scripts.safe_io import SafeIOError, append_regular; "
                    "\ntry:\n append_regular(sys.argv[1], b'x')\nexcept SafeIOError:\n raise SystemExit(0)\n"
                    "raise SystemExit(1)"
                )
                result = subprocess.run(
                    [sys.executable, "-c", child, str(fifo)],
                    cwd=REPO,
                    text=True,
                    capture_output=True,
                    check=False,
                    timeout=3,
                )
                self.assertEqual(result.returncode, 0, result.stderr)
            finally:
                os.close(reader)

    @unittest.skipUnless(os.path.isdir("/proc/self/fd"), "requires Linux /proc file-descriptor inventory")
    def test_replace_regular_closes_source_parent_when_destination_open_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "staged.json"
            source.write_bytes(b"staged")
            blocker = root / "not-a-directory"
            blocker.write_bytes(b"blocker")
            destination = blocker / "target.json"
            before = len(list(Path("/proc/self/fd").iterdir()))
            for _ in range(200):
                with self.assertRaises(NotADirectoryError):
                    safe_io.replace_regular(source, destination)
            after = len(list(Path("/proc/self/fd").iterdir()))
            self.assertLessEqual(after, before + 1)

    @unittest.skipUnless(os.name == "posix", "requires POSIX descriptor backend")
    def test_exclusive_write_fsyncs_file_and_parent_directory(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "lock-record.json"
            real_fsync = safe_io.os.fsync
            calls: list[int] = []

            def recording_fsync(fd: int) -> None:
                calls.append(fd)
                real_fsync(fd)

            with mock.patch.object(safe_io.os, "fsync", side_effect=recording_fsync):
                safe_io.write_new(target, b"lock")
            self.assertGreaterEqual(len(calls), 2)
            self.assertNotEqual(calls[-2], calls[-1])

    def test_windows_guarded_workflows_fail_closed_in_capability_simulation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "record.json"
            target.write_text("{}", encoding="utf-8")
            original_nonblock = safe_io.os.O_NONBLOCK
            delattr(safe_io.os, "O_NONBLOCK")
            try:
                with mock.patch.object(safe_io, "_platform_name", return_value="nt"), mock.patch.object(runtime_safe_io, "_platform_name", return_value="nt"):
                    capabilities = safe_io.filesystem_capabilities()
                    self.assertEqual(capabilities["backend"], "windows_restricted")
                    self.assertFalse(capabilities["bounded_reads"])
                    self.assertFalse(capabilities["exclusive_writes"])
                    self.assertFalse(capabilities["recovery"])
                    with self.assertRaisesRegex(safe_io.SafeIOError, "unavailable on Windows"):
                        safe_io.read_regular(target)
                    with self.assertRaisesRegex(safe_io.SafeIOError, "unavailable on Windows"):
                        safe_io.append_regular(target, b"blocked")
                    with self.assertRaisesRegex(safe_io.SafeIOError, "unavailable on Windows"):
                        safe_io.write_new(target, b"blocked")
                    with self.assertRaisesRegex(knowledge_core.KnowledgeCoreError, "unavailable on Windows"):
                        knowledge_core.file_hash(target)
                    with self.assertRaisesRegex(operating_core.OperatingCoreError, "unavailable on Windows"):
                        operating_core.load_json(target)
            finally:
                setattr(safe_io.os, "O_NONBLOCK", original_nonblock)

    def test_doctor_reports_no_secrets_and_current_filesystem_boundary(self) -> None:
        result = subprocess.run(
            [sys.executable, "scripts/doctor.py", "--json"],
            cwd=REPO,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertIn(report["filesystem"]["backend"], {"posix_descriptor", "windows_restricted"})
        self.assertEqual(report["secrets"], "not inspected")
        self.assertIn("native Windows", report["native_validation"])


if __name__ == "__main__":
    raise SystemExit(unittest.main())
