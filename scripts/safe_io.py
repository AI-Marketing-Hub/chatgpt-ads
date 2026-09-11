"""Filesystem operations with an explicit, fail-closed platform boundary.

The package handles evidence and private operation records. POSIX therefore
uses directory descriptors and ``O_NOFOLLOW`` for every component that is
opened. CPython's public Windows API does not provide an equivalent
handle-relative, no-reparse-point create/replace primitive. The Windows
backend is deliberately *restricted* until that boundary has native evidence:
it reports its limitation and refuses guarded reads and mutations instead of
silently following a junction or weakening a flag to zero.

Keep platform decisions here. Callers should not use ``Path.open`` for data
that crosses a package or private-workspace boundary.
"""
from __future__ import annotations

import os
import stat
import uuid
from pathlib import Path


class SafeIOError(ValueError):
    """A filesystem operation could not satisfy the required guard."""


def _platform_name() -> str:
    """Small seam for deterministic capability tests."""
    return os.name


def is_windows() -> bool:
    return _platform_name() == "nt"


def filesystem_capabilities() -> dict[str, object]:
    """Describe actual guarded workflows, without treating unsupported as off."""
    if is_windows():
        reason = (
            "Windows guarded I/O is disabled: this package has no native-tested "
            "handle-relative, no-reparse-point traversal for bounded reads, "
            "exclusive creates, replacement, locks, or recovery."
        )
        return {
            "backend": "windows_restricted",
            "platform": "windows",
            "bounded_reads": False,
            "exclusive_writes": False,
            "atomic_replace": False,
            "locks": False,
            "recovery": False,
            "reparse_points": "refused by capability boundary; native traversal is not implemented",
            "reason": reason,
        }
    return {
        "backend": "posix_descriptor",
        "platform": "posix",
        "bounded_reads": True,
        "exclusive_writes": True,
        "atomic_replace": True,
        "locks": True,
        "recovery": True,
        "reparse_points": "symlinks refused with O_NOFOLLOW and descriptor traversal",
        "reason": None,
    }


def require_guarded_io(operation: str) -> None:
    """Fail clearly before a Windows call could use an unsafe fallback."""
    if is_windows():
        raise SafeIOError(
            f"{operation} is unavailable on Windows: guarded filesystem workflows "
            "require native-tested handle-relative no-reparse-point support"
        )
    required = ("O_NOFOLLOW", "O_DIRECTORY", "O_NONBLOCK")
    missing = [name for name in required if not hasattr(os, name)]
    if missing:
        raise SafeIOError(f"{operation} is unavailable: missing required POSIX flag(s): {', '.join(missing)}")


def _absolute(path: str | os.PathLike[str]) -> Path:
    return Path(path).absolute()


def _is_link_or_reparse(path: Path) -> bool:
    """Use lstat so dangling links and Windows junctions remain visible."""
    try:
        info = path.lstat()
    except FileNotFoundError:
        return False
    if stat.S_ISLNK(info.st_mode):
        return True
    # Python exposes FILE_ATTRIBUTE_REPARSE_POINT in st_file_attributes on
    # Windows. Treat every reparse point, including a junction, as a link.
    attributes = getattr(info, "st_file_attributes", 0)
    reparse = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
    return bool(attributes & reparse)


def reject_symlinks(path: str | os.PathLike[str]) -> Path:
    """Return an absolute path after rejecting every existing link component.

    ``Path.is_symlink`` alone misses dangling links. ``lstat`` also lets the
    same policy reject Windows junctions and other reparse points when this
    function is used for preflight or diagnostics.
    """
    candidate = _absolute(path)
    for part in (candidate, *candidate.parents):
        if _is_link_or_reparse(part):
            raise SafeIOError(f"symlink or reparse-point path refused: {part}")
    return candidate


def _open_parent(path: Path, *, create: bool = False) -> tuple[int, str]:
    """Open ``path.parent`` through no-follow directory descriptors on POSIX."""
    require_guarded_io("secure path traversal")
    path = reject_symlinks(path)
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
    fd = os.open(path.anchor, flags)
    try:
        for component in path.parts[1:-1]:
            try:
                next_fd = os.open(component, flags, dir_fd=fd)
            except FileNotFoundError:
                if not create:
                    raise
                os.mkdir(component, 0o700, dir_fd=fd)
                # The new directory entry is part of the durability boundary.
                os.fsync(fd)
                next_fd = os.open(component, flags, dir_fd=fd)
            os.close(fd)
            fd = next_fd
    except BaseException:
        os.close(fd)
        raise
    return fd, path.name


def ensure_directory(path: str | os.PathLike[str]) -> Path:
    """Create a directory tree without following a component created by a race."""
    directory = reject_symlinks(path)
    fd, leaf = _open_parent(directory, create=True)
    try:
        if leaf:
            try:
                child = os.open(leaf, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
            except FileNotFoundError:
                os.mkdir(leaf, 0o700, dir_fd=fd)
                os.fsync(fd)
                child = os.open(leaf, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
            os.close(child)
    finally:
        os.close(fd)
    return directory


def _open_regular(path: Path, flags: int, *, create_parent: bool = False, mode: int = 0o600) -> tuple[int, int]:
    parent_fd, leaf = _open_parent(path, create=create_parent)
    try:
        fd = os.open(leaf, flags | os.O_NOFOLLOW, mode, dir_fd=parent_fd)
    except BaseException:
        os.close(parent_fd)
        raise
    return fd, parent_fd


def read_regular(path: str | os.PathLike[str], max_bytes: int = 50 * 1024 * 1024) -> bytes:
    """Read one bounded regular file without following path components."""
    if max_bytes < 0:
        raise SafeIOError("max_bytes must be non-negative")
    target = reject_symlinks(path)
    require_guarded_io("bounded regular-file read")
    # FIFOs can block at open time before the regular-file check. Non-blocking
    # open lets us reject them after fstat without waiting for a peer.
    fd, parent_fd = _open_regular(target, os.O_RDONLY | os.O_NONBLOCK)
    try:
        info = os.fstat(fd)
        if not stat.S_ISREG(info.st_mode):
            raise SafeIOError("regular file required")
        if info.st_size > max_bytes:
            raise SafeIOError("file exceeds bounded read limit")
        with os.fdopen(fd, "rb", closefd=False) as handle:
            data = handle.read(max_bytes + 1)
        if len(data) > max_bytes:
            raise SafeIOError("file exceeds bounded read limit")
        return data
    finally:
        os.close(fd)
        os.close(parent_fd)


def write_new(path: str | os.PathLike[str], data: bytes, *, create_parent: bool = True) -> None:
    """Create one regular file exclusively and durably, never through a link."""
    if not isinstance(data, bytes):
        raise TypeError("write_new data must be bytes")
    target = reject_symlinks(path)
    fd, parent_fd = _open_regular(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL, create_parent=create_parent)
    try:
        with os.fdopen(fd, "wb", closefd=False) as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        # fsync the parent after file fsync so the exclusive lock/staging name
        # survives a crash as well as its contents.
        os.fsync(parent_fd)
    finally:
        os.close(fd)
        os.close(parent_fd)


def atomic_write(path: str | os.PathLike[str], data: bytes, *, create_parent: bool = True) -> None:
    """Durably replace one file inside the already-guarded parent directory."""
    if not isinstance(data, bytes):
        raise TypeError("atomic_write data must be bytes")
    target = reject_symlinks(path)
    parent_fd, leaf = _open_parent(target, create=create_parent)
    temporary = f".{leaf}.{os.getpid()}.{uuid.uuid4().hex}.tmp"
    fd: int | None = None
    try:
        fd = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600, dir_fd=parent_fd)
        with os.fdopen(fd, "wb", closefd=False) as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.close(fd)
        fd = None
        try:
            existing = os.lstat(leaf, dir_fd=parent_fd)
            if stat.S_ISLNK(existing.st_mode):
                raise SafeIOError(f"symlink path refused: {target}")
        except FileNotFoundError:
            pass
        os.replace(temporary, leaf, src_dir_fd=parent_fd, dst_dir_fd=parent_fd)
        os.fsync(parent_fd)
    finally:
        if fd is not None:
            os.close(fd)
        try:
            os.unlink(temporary, dir_fd=parent_fd)
        except FileNotFoundError:
            pass
        finally:
            os.close(parent_fd)


def replace_regular(source: str | os.PathLike[str], destination: str | os.PathLike[str], *, create_parent: bool = True) -> None:
    """Rename a staged regular file over a guarded destination."""
    source_path = reject_symlinks(source)
    destination_path = reject_symlinks(destination)
    source_parent, source_leaf = _open_parent(source_path)
    try:
        destination_parent, destination_leaf = _open_parent(destination_path, create=create_parent)
    except BaseException:
        os.close(source_parent)
        raise
    try:
        source_info = os.lstat(source_leaf, dir_fd=source_parent)
        if not stat.S_ISREG(source_info.st_mode):
            raise SafeIOError("staged source must be a regular file")
        try:
            destination_info = os.lstat(destination_leaf, dir_fd=destination_parent)
            if stat.S_ISLNK(destination_info.st_mode):
                raise SafeIOError(f"symlink path refused: {destination_path}")
        except FileNotFoundError:
            pass
        os.replace(source_leaf, destination_leaf, src_dir_fd=source_parent, dst_dir_fd=destination_parent)
        # Cross-directory replacement removes a staged entry and creates a
        # destination entry. Both directory updates need durability.
        os.fsync(source_parent)
        os.fsync(destination_parent)
    finally:
        os.close(source_parent)
        os.close(destination_parent)


def unlink_regular(path: str | os.PathLike[str], *, missing_ok: bool = False) -> None:
    """Unlink a non-link regular file through its guarded parent descriptor."""
    target = reject_symlinks(path)
    try:
        parent_fd, leaf = _open_parent(target)
    except FileNotFoundError:
        if missing_ok:
            return
        raise
    try:
        try:
            info = os.lstat(leaf, dir_fd=parent_fd)
        except FileNotFoundError:
            if missing_ok:
                return
            raise
        if not stat.S_ISREG(info.st_mode):
            raise SafeIOError("refusing to unlink a non-regular file")
        os.unlink(leaf, dir_fd=parent_fd)
        os.fsync(parent_fd)
    finally:
        os.close(parent_fd)


def append_regular(path: str | os.PathLike[str], data: bytes, *, create_parent: bool = True) -> None:
    """Append durable bytes to a regular no-follow file."""
    if not isinstance(data, bytes):
        raise TypeError("append_regular data must be bytes")
    target = reject_symlinks(path)
    require_guarded_io("checkpoint append")
    # A FIFO opened write-only can block waiting for a reader before fstat.
    # O_NONBLOCK lets the regular-file check reject it without waiting.
    fd, parent_fd = _open_regular(target, os.O_WRONLY | os.O_APPEND | os.O_CREAT | os.O_NONBLOCK, create_parent=create_parent)
    try:
        info = os.fstat(fd)
        if not stat.S_ISREG(info.st_mode):
            raise SafeIOError("regular file required")
        with os.fdopen(fd, "ab", closefd=False) as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.fsync(parent_fd)
    finally:
        os.close(fd)
        os.close(parent_fd)
