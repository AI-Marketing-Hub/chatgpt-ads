#!/usr/bin/env python3
"""Incremental maintenance for the ChatGPT Ads evidence registries.

Update payloads are treated as data. This module does not fetch URLs, execute
captured text, or rewrite curated Markdown. Proposals bind the hashes of all
canonical registries. Apply rejects stale bases and keeps the prior files in a
transaction directory with a manifest.
"""

from __future__ import annotations

import argparse
import copy
import errno
import hashlib
import json
import os
import re
import sys
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping
from urllib.parse import urlparse

try:
    from safe_io import (
        SafeIOError,
        atomic_write,
        ensure_directory,
        read_regular,
        reject_symlinks,
        replace_regular,
        unlink_regular,
        write_new,
    )
except ImportError:  # pragma: no cover - package-style imports
    from scripts.safe_io import (
        SafeIOError,
        atomic_write,
        ensure_directory,
        read_regular,
        reject_symlinks,
        replace_regular,
        unlink_regular,
        write_new,
    )


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_SPECS = {
    "sources": ("references/source-ledger.json", "sources"),
    "claims": ("references/claims.json", "claims"),
    "contradictions": ("references/contradictions.json", "contradictions"),
}
PROJECTION_SPECS = {
    "references/source-ledger.json": "skills/chatgpt-ads/references/sources.json",
    "references/claims.json": "skills/chatgpt-ads/references/claims.json",
    "references/contradictions.json": "skills/chatgpt-ads/references/contradictions.json",
}
CANONICAL_PATHS = frozenset(PROJECTION_SPECS)
PROJECTION_PATHS = frozenset(PROJECTION_SPECS.values())
RENDER_VIEW_PATHS = frozenset({
    "skills/chatgpt-ads/references/platform-findings.md",
    "skills/chatgpt-ads/references/measurement-findings.md",
    "skills/chatgpt-ads/references/policy-findings.md",
    "skills/chatgpt-ads/references/terms-findings.md",
    "skills/chatgpt-ads/references/capabilities.md",
})
ID_RE = re.compile(r"^[a-z0-9][a-z0-9._:-]{0,127}$")
SOURCE_TYPES = {
    "official", "primary", "regulator", "academic", "independent",
    "vendor", "practitioner", "supporting", "market", "news", "fixture",
    "unknown",
}
DATE_KINDS = {"publication", "retrieval", "updated", "unknown"}


class KnowledgeCoreError(ValueError):
    """A bounded validation or transaction failure."""


TERMINAL_TRANSACTION_STATUSES = {"committed", "rolled_back", "recovered"}
LOCK_SCHEMA_VERSION = 1


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def pretty_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def file_hash(path: Path) -> str | None:
    try:
        reject_symlinks(path)
        if not path.exists():
            return None
        return sha256_bytes(read_regular(path))
    except (OSError, ValueError) as exc:
        raise KnowledgeCoreError(f"unsafe or unreadable file: {path}: {exc}") from exc


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(read_regular(path).decode("utf-8"))
    except FileNotFoundError as exc:
        raise KnowledgeCoreError(f"missing required JSON: {path}") from exc
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise KnowledgeCoreError(f"invalid JSON in {path}: {exc}") from exc
    except (OSError, ValueError) as exc:
        raise KnowledgeCoreError(f"unsafe or unreadable JSON: {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise KnowledgeCoreError(f"JSON root must be an object: {path}")
    return value


def _atomic_write(path: Path, data: bytes) -> None:
    try:
        atomic_write(path, data)
    except (OSError, SafeIOError) as exc:
        raise KnowledgeCoreError(f"guarded atomic write failed: {path}: {exc}") from exc


def _write_new_file(path: Path, data: bytes) -> None:
    """Create one immutable transaction artifact without following links."""
    try:
        write_new(path, data)
    except (OSError, SafeIOError) as exc:
        raise KnowledgeCoreError(f"guarded exclusive write failed: {path}: {exc}") from exc


def _valid_id(value: Any, label: str) -> str:
    if not isinstance(value, str) or not ID_RE.fullmatch(value):
        raise KnowledgeCoreError(f"{label} must match {ID_RE.pattern}")
    return value


def _valid_url(value: Any, label: str) -> str:
    if not isinstance(value, str):
        raise KnowledgeCoreError(f"{label} must be an HTTPS URL")
    parsed = urlparse(value)
    if parsed.scheme != "https" or not parsed.netloc or parsed.username or parsed.password:
        raise KnowledgeCoreError(f"{label} must be an HTTPS URL without embedded credentials")
    return value


def _valid_date(value: Any, label: str) -> None:
    if value is None or value == "unknown":
        return
    if not isinstance(value, str):
        raise KnowledgeCoreError(f"{label} must be an ISO date or explicit unknown")
    try:
        date.fromisoformat(value)
    except ValueError as exc:
        raise KnowledgeCoreError(f"{label} must be an ISO date or explicit unknown") from exc


def validate_source(source: Mapping[str, Any], *, require_explicit_dates: bool = False) -> None:
    sid = _valid_id(source.get("id"), "source id")
    _valid_url(source.get("url"), f"source {sid} url")
    if not isinstance(source.get("title"), str) or not source["title"].strip():
        raise KnowledgeCoreError(f"source {sid} requires a non-empty title")
    source_type = source.get("source_type")
    if source_type not in SOURCE_TYPES:
        raise KnowledgeCoreError(f"source {sid} has invalid source_type {source_type!r}")
    if require_explicit_dates:
        for field in ("publication_date", "retrieved", "refresh_due", "date_kind"):
            if field not in source:
                raise KnowledgeCoreError(
                    f"new source {sid} must explicitly set {field}; use null or 'unknown' for an unknown date"
                )
    if "date_kind" in source and source["date_kind"] not in DATE_KINDS:
        raise KnowledgeCoreError(f"source {sid} has invalid date_kind {source['date_kind']!r}")
    for field in ("publication_date", "retrieved", "refresh_due", "last_verified", "date"):
        if field in source:
            _valid_date(source[field], f"source {sid} {field}")
    for field in ("supports_claims", "claims"):
        if field in source:
            if not isinstance(source[field], list):
                raise KnowledgeCoreError(f"source {sid} {field} must be a list")
            for claim_id in source[field]:
                _valid_id(claim_id, f"source {sid} {field} item")


def _locator_source_ids(claim: Mapping[str, Any]) -> set[str]:
    source_ids = claim.get("source_ids", [])
    locators = claim.get("evidence_locators")
    if isinstance(locators, dict):
        found = {key for key, value in locators.items() if isinstance(value, str) and value.strip()}
    elif isinstance(locators, list):
        found = {
            item.get("source_id")
            for item in locators
            if isinstance(item, dict) and isinstance(item.get("locator"), str) and item["locator"].strip()
        }
    else:
        found = set()
    single = claim.get("evidence_locator")
    if len(source_ids) == 1 and isinstance(single, str) and single.strip():
        found.add(source_ids[0])
    return {value for value in found if isinstance(value, str)}


def validate_claim(claim: Mapping[str, Any], *, require_evidence_locators: bool = False) -> None:
    cid = _valid_id(claim.get("id"), "claim id")
    if not isinstance(claim.get("claim"), str) or not claim["claim"].strip():
        raise KnowledgeCoreError(f"claim {cid} requires non-empty claim text")
    source_ids = claim.get("source_ids")
    if not isinstance(source_ids, list) or not source_ids:
        raise KnowledgeCoreError(f"claim {cid} requires at least one source_id")
    for sid in source_ids:
        _valid_id(sid, f"claim {cid} source_id")
    if len(set(source_ids)) != len(source_ids):
        raise KnowledgeCoreError(f"claim {cid} has duplicate source_ids")
    if "as_of" in claim:
        _valid_date(claim["as_of"], f"claim {cid} as_of")
    if require_evidence_locators:
        missing = set(source_ids) - _locator_source_ids(claim)
        if missing:
            raise KnowledgeCoreError(
                f"new claim {cid} requires an evidence locator for source(s): {', '.join(sorted(missing))}"
            )


def validate_contradiction(contradiction: Mapping[str, Any]) -> None:
    cid = _valid_id(contradiction.get("id"), "contradiction id")
    for field in ("evidence_refs", "claim_ids"):
        values = contradiction.get(field, [])
        if not isinstance(values, list):
            raise KnowledgeCoreError(f"contradiction {cid} {field} must be a list")
        for value in values:
            _valid_id(value, f"contradiction {cid} {field} item")


def _unique_records(records: Any, label: str) -> dict[str, dict[str, Any]]:
    if not isinstance(records, list):
        raise KnowledgeCoreError(f"{label} registry list is missing")
    result: dict[str, dict[str, Any]] = {}
    for record in records:
        if not isinstance(record, dict):
            raise KnowledgeCoreError(f"{label} records must be objects")
        rid = _valid_id(record.get("id"), f"{label} id")
        if rid in result:
            raise KnowledgeCoreError(f"duplicate {label} id: {rid}")
        result[rid] = record
    return result


def validate_registries(registries: Mapping[str, Mapping[str, Any]], *, allow_review_gaps: bool = True) -> None:
    sources = _unique_records(registries["sources"].get("sources"), "source")
    claims = _unique_records(registries["claims"].get("claims"), "claim")
    contradictions = _unique_records(registries["contradictions"].get("contradictions"), "contradiction")
    for source in sources.values():
        validate_source(source)
    for claim in claims.values():
        validate_claim(claim)
        missing = set(claim["source_ids"]) - set(sources)
        if missing and not (allow_review_gaps and claim.get("status") == "needs_review"):
            raise KnowledgeCoreError(f"claim {claim['id']} has unknown source_ids: {', '.join(sorted(missing))}")
    for contradiction in contradictions.values():
        validate_contradiction(contradiction)
        unknown_sources = set(contradiction.get("evidence_refs", [])) - set(sources)
        unknown_claims = set(contradiction.get("claim_ids", [])) - set(claims)
        if unknown_sources:
            raise KnowledgeCoreError(
                f"contradiction {contradiction['id']} has unknown evidence_refs: {', '.join(sorted(unknown_sources))}"
            )
        if unknown_claims:
            raise KnowledgeCoreError(
                f"contradiction {contradiction['id']} has unknown claim_ids: {', '.join(sorted(unknown_claims))}"
            )


def load_registries(root: Path = ROOT) -> dict[str, dict[str, Any]]:
    return {name: _read_json(root / relative) for name, (relative, _key) in REGISTRY_SPECS.items()}


def _normalise_operations(updates: Mapping[str, Any], name: str) -> tuple[list[dict[str, Any]], list[str]]:
    section = updates.get(name, {})
    if isinstance(section, list):
        upserts, removals = section, []
    elif isinstance(section, dict):
        upserts = section.get("upsert", section.get("upserts", []))
        removals = section.get("remove_ids", section.get("remove", []))
    else:
        raise KnowledgeCoreError(f"updates.{name} must be an object or list")
    if not isinstance(upserts, list) or not all(isinstance(item, dict) for item in upserts):
        raise KnowledgeCoreError(f"updates.{name}.upsert must be a list of objects")
    upsert_ids = [_valid_id(item.get("id"), f"updates.{name} id") for item in upserts]
    if len(set(upsert_ids)) != len(upsert_ids):
        raise KnowledgeCoreError(f"updates.{name}.upsert contains duplicate ids")
    if not isinstance(removals, list):
        raise KnowledgeCoreError(f"updates.{name}.remove_ids must be a list")
    for rid in removals:
        _valid_id(rid, f"updates.{name}.remove_ids item")
    if len(set(removals)) != len(removals):
        raise KnowledgeCoreError(f"updates.{name}.remove_ids contains duplicates")
    return copy.deepcopy(upserts), list(removals)


def _append_warning(claim: dict[str, Any], warning: str) -> None:
    warnings = claim.get("warnings", [])
    if not isinstance(warnings, list):
        warnings = [str(warnings)]
    if warning not in warnings:
        warnings.append(warning)
    claim["warnings"] = warnings
    claim["status"] = "needs_review"


def _proposal_payload(proposal: Mapping[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in proposal.items() if key not in {"proposal_id", "proposal_sha256"}}


def build_proposal(root: Path, updates: Mapping[str, Any], *, created_at: str | None = None) -> dict[str, Any]:
    """Build a proposal without mutating the root."""
    if not isinstance(updates, dict):
        raise KnowledgeCoreError("update payload must be a JSON object")
    allowed_update_keys = set(REGISTRY_SPECS) | {"metadata"}
    unknown_keys = set(updates) - allowed_update_keys
    if unknown_keys:
        raise KnowledgeCoreError(f"unknown update section(s): {', '.join(sorted(unknown_keys))}")
    metadata = updates.get("metadata", {})
    if not isinstance(metadata, dict):
        raise KnowledgeCoreError("updates.metadata must be an object")
    initial_hashes = {
        relative: file_hash(root / relative)
        for relative, _key in REGISTRY_SPECS.values()
    }
    current = load_registries(root)
    for relative, expected in initial_hashes.items():
        if file_hash(root / relative) != expected:
            raise KnowledgeCoreError(f"concurrent change detected while reading {relative}")
    validate_registries(current)
    projected = copy.deepcopy(current)
    changed_sources: set[str] = set()
    removed_claims: set[str] = set()
    operations: dict[str, dict[str, Any]] = {}

    for name, (_relative, list_key) in REGISTRY_SPECS.items():
        upserts, removals = _normalise_operations(updates, name)
        operations[name] = {"upsert": upserts, "remove_ids": removals}
        existing = _unique_records(projected[name][list_key], name.rstrip("s"))
        for record in upserts:
            rid = _valid_id(record.get("id"), f"updates.{name} id")
            if name == "sources":
                validate_source(record, require_explicit_dates=True)
            elif name == "claims":
                validate_claim(record, require_evidence_locators=rid not in existing)
            else:
                validate_contradiction(record)
            if name == "sources" and rid in existing and canonical_json(existing[rid]) != canonical_json(record):
                changed_sources.add(rid)
            existing[rid] = record
        for rid in removals:
            if rid not in existing:
                raise KnowledgeCoreError(f"cannot remove unknown {name} id: {rid}")
            del existing[rid]
            if name == "sources":
                changed_sources.add(rid)
            elif name == "claims":
                removed_claims.add(rid)
        projected[name][list_key] = list(existing.values())

    if not any(section["upsert"] or section["remove_ids"] for section in operations.values()):
        raise KnowledgeCoreError("update payload contains no registry changes")

    projected_claims = _unique_records(projected["claims"]["claims"], "claim")
    proposal_warnings: list[dict[str, Any]] = []
    for claim in projected_claims.values():
        affected = sorted(set(claim.get("source_ids", [])) & changed_sources)
        if affected:
            _append_warning(claim, "dependent source changed or was removed: " + ", ".join(affected))
            proposal_warnings.append(
                {"claim_id": claim["id"], "code": "source_dependency_changed", "source_ids": affected}
            )

    # Maintain JSON backlinks while leaving human-authored notes untouched.
    for source in projected["sources"]["sources"]:
        linked = [
            cid for cid, claim in projected_claims.items()
            if source["id"] in claim.get("source_ids", [])
        ]
        if "supports_claims" in source or linked:
            source["supports_claims"] = linked
        if "claims" in source or linked:
            source["claims"] = linked
    if removed_claims:
        proposal_warnings.append({"code": "claims_removed", "claim_ids": sorted(removed_claims)})
    validate_registries(projected, allow_review_gaps=True)
    base: dict[str, dict[str, str | None]] = {}
    after: dict[str, dict[str, str]] = {}
    projected_by_path: dict[str, Any] = {}
    for name, (relative, _key) in REGISTRY_SPECS.items():
        base[relative] = {"sha256": initial_hashes[relative]}
        projected_by_path[relative] = projected[name]
        after[relative] = {"sha256": sha256_bytes(pretty_json(projected[name]))}
    proposal: dict[str, Any] = {
        "schema_version": 1,
        "kind": "knowledge-core-proposal",
        "created_at": created_at or datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "base": base,
        "after": after,
        "operations": operations,
        "metadata": copy.deepcopy(metadata),
        "projected": projected_by_path,
        "warnings": proposal_warnings,
    }
    proposal_id = sha256_bytes(canonical_json(_proposal_payload(proposal)))
    proposal["proposal_id"] = proposal_id
    proposal["proposal_sha256"] = proposal_id
    return proposal


def validate_proposal(proposal: Mapping[str, Any]) -> None:
    if proposal.get("kind") != "knowledge-core-proposal" or proposal.get("schema_version") != 1:
        raise KnowledgeCoreError("unsupported proposal kind or schema_version")
    if not isinstance(proposal.get("operations"), dict) or set(proposal["operations"]) != set(REGISTRY_SPECS):
        raise KnowledgeCoreError("proposal operations must contain exactly sources, claims, and contradictions")
    if not isinstance(proposal.get("metadata", {}), dict):
        raise KnowledgeCoreError("proposal metadata must be an object")
    expected = sha256_bytes(canonical_json(_proposal_payload(proposal)))
    if proposal.get("proposal_id") != expected or proposal.get("proposal_sha256") != expected:
        raise KnowledgeCoreError("proposal digest mismatch")
    expected_paths = {relative for relative, _key in REGISTRY_SPECS.values()}
    for field in ("base", "after", "projected"):
        value = proposal.get(field)
        if not isinstance(value, dict) or set(value) != expected_paths:
            raise KnowledgeCoreError(f"proposal {field} must bind exactly the canonical registries")
    for relative, _key in REGISTRY_SPECS.values():
        if relative not in proposal.get("base", {}) or relative not in proposal.get("projected", {}):
            raise KnowledgeCoreError(f"proposal missing bound registry: {relative}")
        expected_after = proposal.get("after", {}).get(relative, {}).get("sha256")
        actual_after = sha256_bytes(pretty_json(proposal["projected"][relative]))
        if expected_after != actual_after:
            raise KnowledgeCoreError(f"proposal projected hash mismatch: {relative}")
    projected = {
        name: proposal["projected"][relative]
        for name, (relative, _key) in REGISTRY_SPECS.items()
    }
    validate_registries(projected, allow_review_gaps=True)


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _safe_relative_path(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value or "\\" in value:
        raise KnowledgeCoreError(f"{label} must be a non-empty POSIX relative path")
    path = Path(value)
    if path.is_absolute() or value != path.as_posix() or any(part in {"", ".", ".."} for part in path.parts):
        raise KnowledgeCoreError(f"{label} must be a normalized relative path")
    return value


def _valid_sha256(value: Any, label: str, *, allow_none: bool = False) -> str | None:
    if allow_none and value is None:
        return None
    if not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{64}", value):
        raise KnowledgeCoreError(f"{label} must be a lowercase SHA-256 digest")
    return value


def _pid_alive(pid: Any) -> bool | None:
    if not isinstance(pid, int) or isinstance(pid, bool) or pid <= 0:
        return None
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    except OSError as exc:
        if exc.errno == errno.ESRCH:
            return False
        if exc.errno == errno.EPERM:
            return True
        return None
    return True


def _read_lock(lock_path: Path) -> dict[str, Any]:
    try:
        reject_symlinks(lock_path)
        raw = read_regular(lock_path)
    except FileNotFoundError:
        return {"present": False}
    except (OSError, ValueError) as exc:
        return {"present": True, "valid": False, "error": f"unsafe or unreadable lock: {exc}"}
    digest = sha256_bytes(raw)
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return {
            "present": True,
            "valid": False,
            "sha256": digest,
            "error": "legacy or malformed lock has no verifiable owner; manual inspection required",
        }
    required = {"schema_version", "pid", "started_at", "transaction_id", "purpose", "owner_token"}
    if not isinstance(value, dict) or not required.issubset(value) or value.get("schema_version") != LOCK_SCHEMA_VERSION:
        return {"present": True, "valid": False, "sha256": digest, "error": "unsupported lock record"}
    if (
        value.get("purpose") not in {"write", "recover"}
        or not isinstance(value.get("pid"), int)
        or isinstance(value.get("pid"), bool)
        or value["pid"] <= 0
        or not isinstance(value.get("owner_token"), str)
        or not re.fullmatch(r"[0-9a-f]{32}", value["owner_token"])
    ):
        return {"present": True, "valid": False, "sha256": digest, "error": "invalid lock owner record"}
    try:
        started = datetime.fromisoformat(value.get("started_at"))
        if started.tzinfo is None:
            raise ValueError
    except (TypeError, ValueError):
        return {"present": True, "valid": False, "sha256": digest, "error": "invalid lock start time"}
    try:
        _valid_id(value.get("transaction_id"), "lock transaction_id")
    except KnowledgeCoreError as exc:
        return {"present": True, "valid": False, "sha256": digest, "error": str(exc)}
    alive = _pid_alive(value.get("pid"))
    return {
        "present": True,
        "valid": True,
        "sha256": digest,
        "pid": value["pid"],
        "started_at": value["started_at"],
        "transaction_id": value["transaction_id"],
        "purpose": value["purpose"],
        "owner_token": value["owner_token"],
        "owner_alive": alive,
        "raw": raw,
    }


def _public_lock_status(lock: Mapping[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in lock.items() if key not in {"raw", "owner_token"}}


def _validate_action_scope(
    *,
    action: Any,
    transaction_id: str,
    base_hashes: Mapping[str, str | None],
    target_hashes: Mapping[str, str],
    guard_hashes: Mapping[str, str | None],
    proposal: Mapping[str, Any] | None,
) -> None:
    """Bind recovery to the small file sets each known writer owns."""
    targets = set(target_hashes)
    guards = set(guard_hashes)
    if set(base_hashes) != targets:
        raise KnowledgeCoreError("transaction base and target bindings do not match")
    if action == "apply_proposal":
        if targets != CANONICAL_PATHS or guards:
            raise KnowledgeCoreError("apply_proposal transaction scope is invalid")
        if proposal is None:
            raise KnowledgeCoreError("apply_proposal recovery requires its retained proposal")
        validate_proposal(proposal)
        if proposal.get("proposal_id") != transaction_id:
            raise KnowledgeCoreError("transaction ID does not match the retained proposal")
        proposal_base = {path: binding.get("sha256") for path, binding in proposal["base"].items()}
        proposal_after = {path: binding.get("sha256") for path, binding in proposal["after"].items()}
        if dict(base_hashes) != proposal_base or dict(target_hashes) != proposal_after:
            raise KnowledgeCoreError("transaction manifest hashes do not match the retained proposal")
    elif action == "sync_projection":
        if targets != PROJECTION_PATHS or guards != CANONICAL_PATHS:
            raise KnowledgeCoreError("sync_projection transaction scope is invalid")
        if proposal is not None or not re.fullmatch(r"projection-[0-9a-f]{64}", transaction_id):
            raise KnowledgeCoreError("sync_projection transaction identity is invalid")
        for canonical, projection in PROJECTION_SPECS.items():
            if guard_hashes[canonical] is None or target_hashes[projection] != guard_hashes[canonical]:
                raise KnowledgeCoreError("sync_projection target hashes do not match canonical guards")
    elif action == "render_views":
        if targets != RENDER_VIEW_PATHS or guards != CANONICAL_PATHS:
            raise KnowledgeCoreError("render_views transaction scope is invalid")
        if proposal is not None or not re.fullmatch(r"render-[0-9a-f]{32}", transaction_id):
            raise KnowledgeCoreError("render_views transaction identity is invalid")
        if any(value is None for value in guard_hashes.values()):
            raise KnowledgeCoreError("render_views requires all canonical guard hashes")
    else:
        raise KnowledgeCoreError(f"unknown transaction action: {action!r}")


def _create_lock(control: Path, transaction_id: str, purpose: str) -> dict[str, Any]:
    _valid_id(transaction_id, "transaction_id")
    try:
        reject_symlinks(control)
    except ValueError as exc:
        raise KnowledgeCoreError(f"symlink control path refused: {control}") from exc
    try:
        ensure_directory(control)
        reject_symlinks(control)
    except (OSError, SafeIOError) as exc:
        raise KnowledgeCoreError(f"guarded lock directory unavailable: {control}: {exc}") from exc
    lock_path = control / "apply.lock"
    reject_symlinks(lock_path)
    record = {
        "schema_version": LOCK_SCHEMA_VERSION,
        "pid": os.getpid(),
        "started_at": _utc_now(),
        "transaction_id": transaction_id,
        "purpose": purpose,
        "owner_token": os.urandom(16).hex(),
    }
    raw = pretty_json(record)
    try:
        write_new(lock_path, raw, create_parent=False)
    except FileExistsError as exc:
        raise KnowledgeCoreError(f"another knowledge-core write is in progress: {lock_path}") from exc
    except (OSError, SafeIOError) as exc:
        raise KnowledgeCoreError(f"guarded lock creation failed: {lock_path}: {exc}") from exc
    return {**record, "raw": raw, "sha256": sha256_bytes(raw), "present": True, "valid": True}


def _release_owned_lock(lock_path: Path, owner: Mapping[str, Any]) -> None:
    current = _read_lock(lock_path)
    if not current.get("valid") or current.get("owner_token") != owner.get("owner_token"):
        raise KnowledgeCoreError(f"lock ownership changed; refusing to remove {lock_path}")
    try:
        unlink_regular(lock_path)
    except (OSError, SafeIOError) as exc:
        raise KnowledgeCoreError(f"guarded lock cleanup failed: {lock_path}: {exc}") from exc


def _manifest_file_states(root: Path, transaction: Path, manifest: Mapping[str, Any]) -> list[dict[str, Any]]:
    files = manifest.get("files")
    base_hashes = manifest.get("base_hashes")
    target_hashes = manifest.get("target_hashes")
    if not isinstance(files, list) or not isinstance(base_hashes, dict) or not isinstance(target_hashes, dict):
        raise KnowledgeCoreError("transaction manifest is missing files, base_hashes, or target_hashes")
    if len(files) != len(set(files)) or set(files) != set(base_hashes) or set(files) != set(target_hashes):
        raise KnowledgeCoreError("transaction manifest file and hash bindings do not match")
    states: list[dict[str, Any]] = []
    for index, raw_relative in enumerate(files):
        relative = _safe_relative_path(raw_relative, f"manifest files[{index}]")
        base_hash = _valid_sha256(base_hashes[relative], f"base hash for {relative}", allow_none=True)
        target_hash = _valid_sha256(target_hashes[relative], f"target hash for {relative}")
        live = root / relative
        before = transaction / "before" / relative
        staged = transaction / "staged" / relative
        for checked in (live, before, staged):
            try:
                reject_symlinks(checked)
            except ValueError as exc:
                raise KnowledgeCoreError(f"symlink transaction path refused: {checked}") from exc
        actual_hash = file_hash(live)
        before_hash = file_hash(before)
        staged_hash = file_hash(staged)
        if actual_hash == base_hash:
            actual_state = "before"
        elif actual_hash == target_hash:
            actual_state = "target"
        else:
            actual_state = "unknown"
        states.append({
            "path": relative,
            "base_sha256": base_hash,
            "target_sha256": target_hash,
            "actual_sha256": actual_hash,
            "actual_state": actual_state,
            "before_image_sha256": before_hash,
            "before_image_valid": before_hash == base_hash,
            "staged_sha256": staged_hash,
            "staged_valid": staged_hash in {None, target_hash},
        })
    return states


def _inspect_transaction(root: Path, transaction: Path) -> dict[str, Any]:
    try:
        reject_symlinks(transaction)
    except ValueError as exc:
        raise KnowledgeCoreError(f"symlink transaction path refused: {transaction}") from exc
    transaction_id = _valid_id(transaction.name, "transaction directory name")
    manifest_path = transaction / "manifest.json"
    manifest = _read_json(manifest_path)
    if manifest.get("schema_version") != 1 or manifest.get("transaction_id") != transaction_id:
        raise KnowledgeCoreError(f"invalid manifest identity for transaction {transaction_id}")
    status = manifest.get("status")
    if not isinstance(status, str):
        raise KnowledgeCoreError(f"transaction {transaction_id} has no valid status")
    base_hashes = manifest.get("base_hashes")
    target_hashes = manifest.get("target_hashes")
    guard_hashes = manifest.get("guard_hashes", {})
    if not isinstance(base_hashes, dict) or not isinstance(target_hashes, dict) or not isinstance(guard_hashes, dict):
        raise KnowledgeCoreError(f"transaction {transaction_id} has invalid hash bindings")
    if status not in TERMINAL_TRANSACTION_STATUSES:
        proposal = None
        if manifest.get("action") == "apply_proposal":
            proposal = _read_json(transaction / "proposal.json")
        _validate_action_scope(
            action=manifest.get("action"),
            transaction_id=transaction_id,
            base_hashes=base_hashes,
            target_hashes=target_hashes,
            guard_hashes=guard_hashes,
            proposal=proposal,
        )
    return {
        "transaction_id": transaction_id,
        "action": manifest.get("action"),
        "status": status,
        "manifest_path": str(manifest_path),
        "files": _manifest_file_states(root, transaction, manifest),
        "manifest": manifest,
    }


def maintenance_state(root: Path = ROOT) -> dict[str, Any]:
    """Report locks and unfinished transactions without changing package state."""
    root = Path(root).absolute()
    control = root / ".knowledge-core"
    lock = _read_lock(control / "apply.lock")
    unfinished: list[dict[str, Any]] = []
    issues: list[dict[str, Any]] = []
    transactions = control / "transactions"
    try:
        reject_symlinks(control)
        reject_symlinks(transactions)
        if transactions.exists():
            if not transactions.is_dir():
                raise KnowledgeCoreError(f"transaction path is not a directory: {transactions}")
            for transaction in sorted(transactions.iterdir(), key=lambda item: item.name):
                try:
                    reject_symlinks(transaction)
                except SafeIOError:
                    issues.append({"transaction_id": transaction.name, "error": "unexpected symlink or reparse-point transaction entry"})
                    continue
                if not transaction.is_dir():
                    issues.append({"transaction_id": transaction.name, "error": "unexpected non-directory transaction entry"})
                    continue
                try:
                    inspected = _inspect_transaction(root, transaction)
                except (KnowledgeCoreError, OSError) as exc:
                    issues.append({"transaction_id": transaction.name, "error": str(exc)})
                    continue
                if inspected["status"] not in TERMINAL_TRANSACTION_STATUSES:
                    inspected.pop("manifest", None)
                    unfinished.append(inspected)
    except (KnowledgeCoreError, OSError, ValueError) as exc:
        issues.append({"error": str(exc)})
    blocked = bool(lock.get("present") or unfinished or issues)
    return {
        "status": "blocked" if blocked else "clean",
        "lock": _public_lock_status(lock),
        "unfinished_transactions": unfinished,
        "issues": issues,
    }


def _require_clean_maintenance(root: Path) -> None:
    state = maintenance_state(root)
    if state["status"] != "clean":
        transaction_ids = [item["transaction_id"] for item in state["unfinished_transactions"]]
        detail = f" unfinished={','.join(transaction_ids)}" if transaction_ids else ""
        raise KnowledgeCoreError(f"knowledge-core maintenance is blocked; inspect `status` and recover explicitly.{detail}")


def _manifest_write(path: Path, manifest: dict[str, Any]) -> None:
    manifest["updated_at"] = _utc_now()
    _atomic_write(path, pretty_json(manifest))


def _transaction_commit(
    root: Path,
    *,
    action: str,
    transaction_id: str,
    base_hashes: Mapping[str, str | None],
    target_bytes: Mapping[str, bytes],
    proposal: Mapping[str, Any] | None = None,
    guard_hashes: Mapping[str, str | None] | None = None,
) -> dict[str, Any]:
    root = Path(root).absolute()
    if set(base_hashes) != set(target_bytes):
        raise KnowledgeCoreError("base_hashes must bind exactly the target files")
    for relative, expected in base_hashes.items():
        _safe_relative_path(relative, "transaction target")
        _valid_sha256(expected, f"base hash for {relative}", allow_none=True)
    for relative in target_bytes:
        if not isinstance(target_bytes[relative], bytes):
            raise KnowledgeCoreError(f"transaction target must be bytes: {relative}")
    for relative, expected in (guard_hashes or {}).items():
        _safe_relative_path(relative, "transaction guard")
        _valid_sha256(expected, f"guard hash for {relative}", allow_none=True)
    target_hashes = {key: sha256_bytes(value) for key, value in target_bytes.items()}
    _validate_action_scope(
        action=action,
        transaction_id=transaction_id,
        base_hashes=base_hashes,
        target_hashes=target_hashes,
        guard_hashes=guard_hashes or {},
        proposal=proposal,
    )
    _require_clean_maintenance(root)
    control = root / ".knowledge-core"
    lock_path = control / "apply.lock"
    owner = _create_lock(control, transaction_id, "write")
    transaction = control / "transactions" / transaction_id
    manifest_path = transaction / "manifest.json"
    applied: list[str] = []
    try:
        reject_symlinks(transaction)
        if transaction.exists():
            raise KnowledgeCoreError(f"transaction already exists: {transaction_id}")
        for relative, expected in base_hashes.items():
            actual = file_hash(root / relative)
            if actual != expected:
                raise KnowledgeCoreError(f"stale base for {relative}: expected {expected}, found {actual}")
        for relative, expected in (guard_hashes or {}).items():
            if file_hash(root / relative) != expected:
                raise KnowledgeCoreError(f"concurrent change detected for guarded {relative}")
        for relative, data in target_bytes.items():
            staged = transaction / "staged" / relative
            _write_new_file(staged, data)
            before = transaction / "before" / relative
            live = root / relative
            if file_hash(live) is not None:
                _write_new_file(before, read_regular(live))
        if proposal is not None:
            _write_new_file(transaction / "proposal.json", pretty_json(proposal))
        manifest: dict[str, Any] = {
            "schema_version": 1,
            "transaction_id": transaction_id,
            "action": action,
            "status": "prepared",
            "files": list(target_bytes),
            "base_hashes": dict(base_hashes),
            "target_hashes": target_hashes,
            "guard_hashes": dict(guard_hashes or {}),
            "applied": [],
            "rollback_conflicts": [],
        }
        _manifest_write(manifest_path, manifest)
        manifest["status"] = "applying"
        _manifest_write(manifest_path, manifest)
        try:
            for relative in target_bytes:
                for guarded, expected in (guard_hashes or {}).items():
                    if file_hash(root / guarded) != expected:
                        raise KnowledgeCoreError(f"concurrent change detected for guarded {guarded}")
                if file_hash(root / relative) != base_hashes[relative]:
                    raise KnowledgeCoreError(f"concurrent change detected for {relative}")
                destination = root / relative
                reject_symlinks(destination)
                reject_symlinks(destination.parent)
                staged = transaction / "staged" / relative
                reject_symlinks(staged)
                try:
                    replace_regular(staged, destination)
                except (OSError, SafeIOError) as exc:
                    raise KnowledgeCoreError(f"guarded transaction replacement failed: {relative}: {exc}") from exc
                applied.append(relative)
                manifest["applied"] = list(applied)
                _manifest_write(manifest_path, manifest)
            for relative, expected in manifest["target_hashes"].items():
                if file_hash(root / relative) != expected:
                    raise KnowledgeCoreError(f"post-apply hash mismatch for {relative}")
            for guarded, expected in (guard_hashes or {}).items():
                if file_hash(root / guarded) != expected:
                    raise KnowledgeCoreError(f"concurrent change detected for guarded {guarded}")
        except Exception:
            manifest["status"] = "rolling_back"
            _manifest_write(manifest_path, manifest)
            for relative in reversed(applied):
                live = root / relative
                if file_hash(live) != manifest["target_hashes"][relative]:
                    manifest["rollback_conflicts"].append(relative)
                    continue
                before = transaction / "before" / relative
                if file_hash(before) is not None:
                    _atomic_write(live, read_regular(before))
                else:
                    try:
                        unlink_regular(live, missing_ok=True)
                    except (OSError, SafeIOError) as exc:
                        raise KnowledgeCoreError(f"guarded rollback cleanup failed: {relative}: {exc}") from exc
            manifest["status"] = "rollback_conflict" if manifest["rollback_conflicts"] else "rolled_back"
            _manifest_write(manifest_path, manifest)
            raise
        manifest["status"] = "committed"
        _manifest_write(manifest_path, manifest)
        return manifest
    finally:
        _release_owned_lock(lock_path, owner)


def _remove_verified_dead_lock(lock_path: Path, lock: Mapping[str, Any], transaction_id: str) -> None:
    if not lock.get("valid"):
        raise KnowledgeCoreError("lock has no verifiable owner; refusing automatic removal")
    if lock.get("owner_alive") is not False:
        raise KnowledgeCoreError(f"active or unverifiable writer owns the lock (pid {lock.get('pid')})")
    if lock.get("transaction_id") != transaction_id:
        raise KnowledgeCoreError(
            f"lock belongs to transaction {lock.get('transaction_id')}; recover that transaction first"
        )
    reject_symlinks(lock_path)
    before_stat = lock_path.stat(follow_symlinks=False)
    current = _read_lock(lock_path)
    after_stat = lock_path.stat(follow_symlinks=False)
    if (
        not current.get("valid")
        or current.get("raw") != lock.get("raw")
        or (before_stat.st_dev, before_stat.st_ino) != (after_stat.st_dev, after_stat.st_ino)
    ):
        raise KnowledgeCoreError("lock changed during recovery inspection; refusing removal")
    try:
        unlink_regular(lock_path)
    except (OSError, SafeIOError) as exc:
        raise KnowledgeCoreError(f"guarded dead-lock cleanup failed: {lock_path}: {exc}") from exc


def _validated_recovery(root: Path, transaction_id: str) -> tuple[Path, Path, dict[str, Any], list[dict[str, Any]]]:
    _valid_id(transaction_id, "transaction_id")
    transaction = root / ".knowledge-core" / "transactions" / transaction_id
    if not transaction.exists():
        raise KnowledgeCoreError(f"unknown transaction: {transaction_id}")
    inspected = _inspect_transaction(root, transaction)
    if inspected["status"] in TERMINAL_TRANSACTION_STATUSES:
        raise KnowledgeCoreError(f"transaction {transaction_id} is already {inspected['status']}")
    manifest = inspected["manifest"]
    guard_hashes = manifest.get("guard_hashes", {})
    if not isinstance(guard_hashes, dict):
        raise KnowledgeCoreError("transaction manifest guard_hashes must be an object")
    for raw_relative, expected in guard_hashes.items():
        relative = _safe_relative_path(raw_relative, "manifest guard")
        _valid_sha256(expected, f"guard hash for {relative}", allow_none=True)
        actual = file_hash(root / relative)
        if actual != expected:
            raise KnowledgeCoreError(
                f"guarded file changed outside the transaction: {relative}: expected {expected}, found {actual}"
            )
    bad_before = [item["path"] for item in inspected["files"] if not item["before_image_valid"]]
    bad_staged = [item["path"] for item in inspected["files"] if not item["staged_valid"]]
    unknown = [item["path"] for item in inspected["files"] if item["actual_state"] == "unknown"]
    if bad_before:
        raise KnowledgeCoreError(f"before image hash mismatch: {', '.join(bad_before)}")
    if bad_staged:
        raise KnowledgeCoreError(f"staged file hash mismatch: {', '.join(bad_staged)}")
    if unknown:
        raise KnowledgeCoreError(f"unknown live edits prevent recovery: {', '.join(unknown)}")
    return transaction, transaction / "manifest.json", manifest, inspected["files"]


def recover_transaction(root: Path, transaction_id: str) -> dict[str, Any]:
    """Explicitly restore an unfinished transaction after hash and owner checks."""
    root = Path(root).absolute()
    state = maintenance_state(root)
    other = [
        item["transaction_id"]
        for item in state["unfinished_transactions"]
        if item["transaction_id"] != transaction_id
    ]
    if state["issues"] or other:
        suffix = f": {', '.join(other)}" if other else ""
        raise KnowledgeCoreError(f"other unresolved maintenance state prevents recovery{suffix}")
    transaction, manifest_path, manifest, initial_states = _validated_recovery(root, transaction_id)
    control = root / ".knowledge-core"
    lock_path = control / "apply.lock"
    existing_lock = _read_lock(lock_path)
    if existing_lock.get("present"):
        _remove_verified_dead_lock(lock_path, existing_lock, transaction_id)
    owner = _create_lock(control, transaction_id, "recover")
    restored: list[str] = []
    original_status = manifest.get("status")
    try:
        transaction, manifest_path, manifest, current_states = _validated_recovery(root, transaction_id)
        manifest["status"] = "recovering"
        manifest["recovery_started_at"] = _utc_now()
        manifest["recovery_original_status"] = original_status
        manifest["recovery_initial_hashes"] = {
            item["path"]: item["actual_sha256"] for item in initial_states
        }
        manifest["recovery_restored"] = []
        _manifest_write(manifest_path, manifest)
        try:
            for item in reversed(current_states):
                if item["actual_state"] != "target" or item["base_sha256"] == item["target_sha256"]:
                    continue
                relative = item["path"]
                live = root / relative
                if file_hash(live) != item["target_sha256"]:
                    raise KnowledgeCoreError(f"live file changed during recovery: {relative}")
                before = transaction / "before" / relative
                if item["base_sha256"] is None:
                    try:
                        unlink_regular(live, missing_ok=True)
                    except (OSError, SafeIOError) as exc:
                        raise KnowledgeCoreError(f"guarded recovery cleanup failed: {relative}: {exc}") from exc
                else:
                    before_data = read_regular(before)
                    if sha256_bytes(before_data) != item["base_sha256"]:
                        raise KnowledgeCoreError(f"before image changed during recovery: {relative}")
                    _atomic_write(live, before_data)
                restored.append(relative)
                manifest["recovery_restored"] = list(restored)
                _manifest_write(manifest_path, manifest)
            final_states = _manifest_file_states(root, transaction, manifest)
            not_restored = [item["path"] for item in final_states if item["actual_sha256"] != item["base_sha256"]]
            if not_restored:
                raise KnowledgeCoreError(f"recovery post-check failed: {', '.join(not_restored)}")
        except Exception as exc:
            manifest["status"] = "recovery_conflict"
            manifest["recovery_error"] = str(exc)
            _manifest_write(manifest_path, manifest)
            raise
        manifest["status"] = "recovered"
        manifest["recovered_at"] = _utc_now()
        manifest.pop("recovery_error", None)
        _manifest_write(manifest_path, manifest)
        return {
            "status": "recovered",
            "transaction_id": transaction_id,
            "action": manifest.get("action"),
            "restored": restored,
            "initial_files": initial_states,
            "final_hashes": {item["path"]: item["base_sha256"] for item in final_states},
            "manifest_path": str(manifest_path),
        }
    finally:
        _release_owned_lock(lock_path, owner)


def apply_proposal(root: Path, proposal: Mapping[str, Any]) -> dict[str, Any]:
    _require_clean_maintenance(root)
    validate_proposal(proposal)
    for relative, binding in proposal["base"].items():
        actual = file_hash(root / relative)
        expected = binding.get("sha256")
        if actual != expected:
            raise KnowledgeCoreError(f"stale base for {relative}: expected {expected}, found {actual}")
    replay_updates = copy.deepcopy(proposal["operations"])
    replay_updates["metadata"] = copy.deepcopy(proposal.get("metadata", {}))
    replayed = build_proposal(root, replay_updates, created_at=proposal["created_at"])
    if replayed["projected"] != proposal["projected"] or replayed["after"] != proposal["after"]:
        raise KnowledgeCoreError("proposal projection does not match its incremental operations")
    target_bytes = {relative: pretty_json(value) for relative, value in proposal["projected"].items()}
    base_hashes = {relative: binding.get("sha256") for relative, binding in proposal["base"].items()}
    return _transaction_commit(
        root,
        action="apply_proposal",
        transaction_id=proposal["proposal_id"],
        base_hashes=base_hashes,
        target_bytes=target_bytes,
        proposal=proposal,
    )


def projection_status(root: Path) -> dict[str, Any]:
    files = []
    for canonical, projection in PROJECTION_SPECS.items():
        canonical_hash = file_hash(root / canonical)
        projection_hash = file_hash(root / projection)
        files.append({
            "canonical": canonical,
            "projection": projection,
            "canonical_sha256": canonical_hash,
            "projection_sha256": projection_hash,
            "in_sync": canonical_hash == projection_hash,
        })
    return {"status": "in_sync" if all(item["in_sync"] for item in files) else "drift", "files": files}


def sync_projection(root: Path) -> dict[str, Any]:
    _require_clean_maintenance(root)
    status = projection_status(root)
    if status["status"] == "in_sync":
        return {"status": "in_sync", "action": "sync_projection", "transaction_id": None, "files": status["files"]}
    target_bytes: dict[str, bytes] = {}
    base_hashes: dict[str, str | None] = {}
    guard_hashes: dict[str, str | None] = {}
    for item in status["files"]:
        if item["canonical_sha256"] is None:
            raise KnowledgeCoreError(f"missing canonical registry: {item['canonical']}")
        try:
            data = read_regular(root / item["canonical"])
        except (OSError, SafeIOError) as exc:
            raise KnowledgeCoreError(f"guarded canonical read failed: {item['canonical']}: {exc}") from exc
        if sha256_bytes(data) != item["canonical_sha256"]:
            raise KnowledgeCoreError(f"concurrent change detected while reading {item['canonical']}")
        target_bytes[item["projection"]] = data
        base_hashes[item["projection"]] = item["projection_sha256"]
        guard_hashes[item["canonical"]] = item["canonical_sha256"]
    digest = sha256_bytes(canonical_json({"action": "sync_projection", "files": status["files"]}))
    return _transaction_commit(
        root,
        action="sync_projection",
        transaction_id=f"projection-{digest}",
        base_hashes=base_hashes,
        target_bytes=target_bytes,
        guard_hashes=guard_hashes,
    )


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="brain root (defaults to this checkout)")
    commands = parser.add_subparsers(dest="command", required=True)
    propose = commands.add_parser("propose", help="build a non-mutating incremental proposal")
    propose.add_argument("--updates", type=Path, required=True, help="JSON update operations")
    propose.add_argument("--output", type=Path, help="explicitly write the proposal; otherwise print it")
    apply = commands.add_parser("apply", help="apply a hash-bound proposal transaction")
    apply.add_argument("--proposal", type=Path, required=True)
    commands.add_parser("validate", help="validate canonical registries without writing")
    commands.add_parser("status", help="report locks and unfinished transactions without writing")
    recover = commands.add_parser("recover", help="restore one unfinished transaction after hash checks")
    recover.add_argument("--transaction", required=True, help="exact unfinished transaction ID")
    sync = commands.add_parser("sync-projection", help="sync generated JSON projections only")
    sync.add_argument("--check", action="store_true", help="report drift without writing")
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(list(argv) if argv is not None else None)
    root = args.root.absolute()
    try:
        if args.command == "propose":
            proposal = build_proposal(root, _read_json(args.updates))
            rendered = pretty_json(proposal)
            if args.output:
                output = args.output.absolute()
                _atomic_write(output, rendered)
                print(json.dumps({
                    "status": "proposed", "proposal_id": proposal["proposal_id"],
                    "output": str(output), "warnings": proposal["warnings"],
                }, indent=2))
            else:
                sys.stdout.buffer.write(rendered)
        elif args.command == "apply":
            print(json.dumps(apply_proposal(root, _read_json(args.proposal)), indent=2))
        elif args.command == "validate":
            state = maintenance_state(root)
            if state["status"] != "clean":
                raise KnowledgeCoreError(
                    "unfinished knowledge-core transaction or lock; run `knowledge_core.py status`"
                )
            registries = load_registries(root)
            validate_registries(registries)
            counts = {name: len(registries[name][key]) for name, (_path, key) in REGISTRY_SPECS.items()}
            print(json.dumps({"status": "valid", "counts": counts}, indent=2))
        elif args.command == "status":
            state = maintenance_state(root)
            print(json.dumps(state, indent=2))
            return 0 if state["status"] == "clean" else 1
        elif args.command == "recover":
            print(json.dumps(recover_transaction(root, args.transaction), indent=2))
        elif args.command == "sync-projection":
            if args.check:
                result = projection_status(root)
                print(json.dumps(result, indent=2))
                return 0 if result["status"] == "in_sync" else 1
            print(json.dumps(sync_projection(root), indent=2))
        return 0
    except (KnowledgeCoreError, OSError) as exc:
        print(f"knowledge-core error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
