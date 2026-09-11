# Windows runtime boundary

The v0.3.0 work introduces an explicit Windows filesystem capability boundary. It does **not** establish native Windows support for the guarded package workflows.

On POSIX, the package opens each path component through directory descriptors with `O_NOFOLLOW`. That lets it bind a bounded read, exclusive file creation, atomic replacement, lock file, checkpoint, and transaction recovery operation to the directories it inspected. CPython's public Windows API has no equivalent handle-relative, no-reparse-point primitive in this package. Implementing an untested `ctypes` approximation would make the security claim less credible, so the Windows backend fails closed instead.

Use the diagnostic before relying on a workflow:

```powershell
py -3 scripts/doctor.py
```

On a native Windows host it reports `backend: windows_restricted` and names each blocked workflow. It does not inspect credentials, account data, or private records.

| Activity | Native Windows position in this release |
| --- | --- |
| Read the bundled Markdown and JSON as ordinary files | Usable with normal tools. This is outside the guarded workflow boundary. |
| Run a standalone analyzer with user-controlled input | Documented as a limited path, native Windows execution is still unverified. Validate its output independently. |
| `knowledge_core.py` retrieval, validation, proposal output, update, locking, replacement, recovery | Capability unavailable. It refuses before a junction, symlink, or weakened no-follow fallback can be used. |
| `operating_core.py` guarded records, account locks, checkpoints, simulation state, promoted-learning output | Capability unavailable for the same reason. |
| Native Windows security and concurrency acceptance | Not tested, not supported, and not implied by this document. |

`reject_symlinks()` still treats a discovered Windows reparse point, including a junction, as unsafe during preflight. That check is defence in depth. It is not advertised as sufficient to make an operation safe, because a path component can change between checks without a handle-relative traversal primitive.

WSL runs the POSIX backend when the process itself is Linux. That is not native Windows validation, and this project has not recorded WSL acceptance evidence. Do not use a WSL result to mark the native Windows rows as passed.

Before enabling guarded Windows workflows, a controlled native Windows runner must test Python 3.11 and 3.14 with paths containing spaces and Unicode, case differences, reserved names, long paths where enabled, locked files, concurrent writers, crash recovery, symlinks, and junctions. Symlink creation may require Developer Mode or elevation. If that prerequisite prevents a reparse-point security test, record it as missing evidence rather than a passing skip. The implementation also needs a reviewed native handle-relative, no-reparse-point backend for bounded reads, exclusive writes, replacement, locks, and recovery.
