#!/usr/bin/env python3
"""Bounded, local operating core for versioned ChatGPT Ads operation records.

This module deliberately has no browser, credential, HTTP, or real-account adapter.
``SimulatedAdsUI`` is a controlled test double.  The approval hash and its
provenance fields make a human decision reviewable; they are not authentication,
authorization, identity verification, or a security guarantee outside an
operation performed through this helper.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import re
import secrets
import sys
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Iterable

try:
    from safe_io import SafeIOError, append_regular, atomic_write, read_regular, reject_symlinks, unlink_regular, write_new
except ImportError:  # pragma: no cover - package-style imports
    from scripts.safe_io import SafeIOError, append_regular, atomic_write, read_regular, reject_symlinks, unlink_regular, write_new


SCHEMA_VERSION = "v0.2"
RECORD_TYPES = {
    "client_profile",
    "campaign_plan",
    "action_plan",
    "action_receipt",
    "learning_candidate",
}
ACTION_PROVENANCE_NOTICE = (
    "Human decision provenance only. This hash binding is not authentication, "
    "authorization, identity verification, or a security guarantee."
)
IDENTIFIER = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9._-]{0,127}$")


class OperatingCoreError(ValueError):
    """A record, preflight, lock, or reconciliation failure."""


class UncertainOutcome(OperatingCoreError):
    """The helper cannot determine whether a side effect occurred."""


def utc_now() -> datetime:
    return datetime.now(UTC)


def utc_text(value: datetime | None = None) -> str:
    value = value or utc_now()
    if value.tzinfo is None:
        raise OperatingCoreError("timestamp must include a UTC offset")
    return value.astimezone(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def parse_utc(value: Any, field_name: str) -> datetime:
    if not isinstance(value, str) or not value.endswith("Z"):
        raise OperatingCoreError(f"{field_name} must be an ISO-8601 UTC timestamp ending in Z")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise OperatingCoreError(f"{field_name} is not a valid UTC timestamp") from exc
    if parsed.tzinfo is None or parsed.utcoffset() != UTC.utcoffset(parsed):
        raise OperatingCoreError(f"{field_name} must be UTC")
    return parsed.astimezone(UTC)


def canonical_json(value: Any) -> str:
    """Return the exact deterministic JSON serialization used for hash bindings."""
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def sha256_canonical(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(read_regular(path).decode("utf-8"))
    except (OSError, SafeIOError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise OperatingCoreError(f"cannot read JSON record {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise OperatingCoreError(f"record {path} must be a JSON object")
    return value


def save_json(path: Path, value: dict[str, Any]) -> None:
    try:
        atomic_write(path, (canonical_json(value) + "\n").encode("utf-8"))
    except (OSError, SafeIOError) as exc:
        raise OperatingCoreError(f"cannot safely write JSON record {path}: {exc}") from exc


def _require_text(record: dict[str, Any], key: str) -> str:
    value = record.get(key)
    if not isinstance(value, str) or not value.strip():
        raise OperatingCoreError(f"{key} must be a non-empty string")
    return value


def _require_id(record: dict[str, Any], key: str) -> str:
    value = _require_text(record, key)
    if not IDENTIFIER.fullmatch(value):
        raise OperatingCoreError(f"{key} must contain only letters, numbers, dot, underscore, or hyphen")
    return value


def _require_object(record: dict[str, Any], key: str) -> dict[str, Any]:
    value = record.get(key)
    if not isinstance(value, dict):
        raise OperatingCoreError(f"{key} must be an object")
    return value


def _require_nonnegative_int(record: dict[str, Any], key: str) -> int:
    value = record.get(key)
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise OperatingCoreError(f"{key} must be a non-negative integer")
    return value


def validate_record(record: dict[str, Any]) -> None:
    """Validate record semantics in addition to the shipped JSON Schemas."""
    if not isinstance(record, dict):
        raise OperatingCoreError("record must be an object")
    if record.get("schema_version") != SCHEMA_VERSION:
        raise OperatingCoreError(f"schema_version must be {SCHEMA_VERSION}")
    record_type = record.get("record_type")
    if record_type not in RECORD_TYPES:
        raise OperatingCoreError(f"record_type must be one of {sorted(RECORD_TYPES)}")
    _require_id(record, "id")
    parse_utc(record.get("created_at"), "created_at")
    validators = {
        "client_profile": _validate_client_profile,
        "campaign_plan": _validate_campaign_plan,
        "action_plan": _validate_action_plan,
        "action_receipt": _validate_action_receipt,
        "learning_candidate": _validate_learning_candidate,
    }
    validators[record_type](record)


def _validate_client_profile(record: dict[str, Any]) -> None:
    _require_id(record, "client_id")
    _require_id(record, "account_id")
    _require_text(record, "owner")
    policy = _require_object(record, "owner_decision_policy")
    if policy.get("owner_required") is not True:
        raise OperatingCoreError("owner_decision_policy.owner_required must be true")
    if policy.get("allow_policy_change") is not False:
        raise OperatingCoreError("owner_decision_policy.allow_policy_change must be false")
    _require_text(policy, "change_process")


def _validate_budget(budget: dict[str, Any], prefix: str = "budget") -> None:
    if not isinstance(budget.get("currency"), str) or not re.fullmatch(r"[A-Z]{3}", budget["currency"]):
        raise OperatingCoreError(f"{prefix}.currency must be an ISO-like three-letter uppercase code")
    value = budget.get("daily_budget_micros")
    if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
        raise OperatingCoreError(f"{prefix}.daily_budget_micros must be a positive integer")
    maximum_effect = _require_object(budget, "maximum_effect")
    if maximum_effect.get("kind") != "maximum_total_spend_micros":
        raise OperatingCoreError(f"{prefix}.maximum_effect.kind must be maximum_total_spend_micros")
    ceiling = maximum_effect.get("amount_micros")
    if not isinstance(ceiling, int) or isinstance(ceiling, bool) or ceiling < value:
        raise OperatingCoreError(f"{prefix}.maximum_effect.amount_micros must be an integer at least daily_budget_micros")


def _validate_campaign_plan(record: dict[str, Any]) -> None:
    _require_id(record, "client_id")
    _require_id(record, "account_id")
    _require_id(record, "campaign_id")
    _require_text(record, "objective")
    _validate_budget(_require_object(record, "budget"))
    _require_text(record, "expected_ui_revision")
    _require_text(record, "evidence_reference")


def _action_body(record: dict[str, Any]) -> dict[str, Any]:
    action = _require_object(record, "action")
    _require_id(action, "account_id")
    if action.get("kind") not in {"create_campaign", "edit_campaign", "status_change", "roles_change", "audience_change", "catalog_change", "bulk_change", "configure"}:
        raise OperatingCoreError("action.kind is not represented by the v0.2 interface")
    target = _require_object(action, "target")
    _require_text(target, "resource_type")
    _require_id(target, "resource_id")
    _require_object(action, "before")
    _require_object(action, "after")
    cost = _require_object(action, "cost")
    _require_text(cost, "currency")
    maximum_effect = _require_object(cost, "maximum_effect")
    if maximum_effect.get("kind") != "maximum_total_spend_micros":
        raise OperatingCoreError("action.cost.maximum_effect.kind must be maximum_total_spend_micros")
    _require_nonnegative_int(maximum_effect, "amount_micros")
    _require_text(action, "rollback")
    _require_text(action, "expected_ui_revision")
    verification = _require_object(action, "verification")
    _require_text(verification, "method")
    _require_text(verification, "expected")
    supplied_plan_hash = _require_text(action, "campaign_plan_sha256")
    if not re.fullmatch(r"[a-f0-9]{64}", supplied_plan_hash):
        raise OperatingCoreError("action.campaign_plan_sha256 must be a SHA-256 hex digest")
    if action["kind"] == "create_campaign":
        _require_id(action, "campaign_id")
        _validate_budget(_require_object(action, "budget"), "action.budget")
        if action["target"] != {"resource_type": "campaign", "resource_id": action["campaign_id"]}:
            raise OperatingCoreError("create_campaign target must identify its campaign_id")
        if action["cost"]["maximum_effect"] != action["budget"]["maximum_effect"]:
            raise OperatingCoreError("create_campaign cost must match budget maximum_effect")
        if action["cost"]["currency"] != action["budget"]["currency"]:
            raise OperatingCoreError("create_campaign cost.currency must match budget.currency")
    return action


def _validate_action_plan(record: dict[str, Any]) -> None:
    _require_id(record, "campaign_plan_id")
    action = _action_body(record)
    approval = _require_object(record, "approval")
    _require_id(approval, "decision_id")
    _require_text(approval, "approved_by")
    parse_utc(approval.get("approved_at"), "approval.approved_at")
    expiry = parse_utc(approval.get("expires_at"), "approval.expires_at")
    if expiry <= parse_utc(approval.get("approved_at"), "approval.approved_at"):
        raise OperatingCoreError("approval.expires_at must be after approval.approved_at")
    supplied = _require_text(approval, "approved_action_sha256")
    actual = sha256_canonical(action)
    if supplied != actual:
        raise OperatingCoreError("approval.approved_action_sha256 does not bind the exact canonical action JSON")
    if approval.get("provenance_notice") != ACTION_PROVENANCE_NOTICE:
        raise OperatingCoreError("approval.provenance_notice must state the non-authentication limitation")
    if _require_text(approval, "decision_sha256") != sha256_canonical({key: value for key, value in approval.items() if key != "decision_sha256"}):
        raise OperatingCoreError("approval.decision_sha256 does not bind the exact approval metadata and action hash")


def _validate_action_receipt(record: dict[str, Any]) -> None:
    _require_id(record, "operation_id")
    _require_id(record, "action_plan_id")
    if not re.fullmatch(r"[a-f0-9]{64}", _require_text(record, "action_sha256")):
        raise OperatingCoreError("action_receipt.action_sha256 must be a SHA-256 hex digest")
    _require_id(record, "observed_account_id")
    target = _require_object(record, "target")
    _require_text(target, "resource_type")
    _require_id(target, "resource_id")
    observed = _require_object(record, "observed_settings")
    _require_text(observed, "ui_revision")
    if record.get("outcome") not in {"succeeded", "rejected", "uncertain", "reconciled"}:
        raise OperatingCoreError("action_receipt.outcome is invalid")
    _require_text(record, "detail")
    _require_text(record, "observed_at")
    parse_utc(record["observed_at"], "observed_at")
    if not isinstance(record.get("simulated"), bool):
        raise OperatingCoreError("action_receipt.simulated must be boolean")
    if record.get("evidence_scope") not in {"simulated", "live_observed", "mixed"}:
        raise OperatingCoreError("action_receipt.evidence_scope is invalid")
    if record["simulated"] is True and record["evidence_scope"] != "simulated":
        raise OperatingCoreError("simulated receipt must use simulated evidence_scope")
    if record["simulated"] is False and record["evidence_scope"] == "simulated":
        raise OperatingCoreError("non-simulated receipt cannot use simulated evidence_scope")
    refs = record.get("evidence_refs")
    if not isinstance(refs, list) or not refs or not all(isinstance(item, dict) and re.fullmatch(r"[a-f0-9]{64}", str(item.get("sha256", ""))) for item in refs):
        raise OperatingCoreError("action_receipt.evidence_refs must contain hash-backed evidence")


def _validate_learning_candidate(record: dict[str, Any]) -> None:
    _require_id(record, "client_id")
    _require_text(record, "hypothesis")
    _require_text(record, "scope")
    evidence = record.get("evidence")
    if not isinstance(evidence, list) or not evidence or not all(isinstance(item, dict) for item in evidence):
        raise OperatingCoreError("learning_candidate.evidence must be a non-empty list")
    stage = record.get("stage", "pending_review")
    if stage == "pending_review":
        if record.get("generalization", "client_specific") != "client_specific":
            raise OperatingCoreError("pending private learning cannot be generalized")
        return
    if stage != "reviewed":
        raise OperatingCoreError("learning_candidate.stage must be pending_review or reviewed")
    if not all(isinstance(item.get("receipt_path"), str) and re.fullmatch(r"[a-f0-9]{64}", str(item.get("receipt_sha256", ""))) for item in evidence):
        raise OperatingCoreError("reviewed learning requires receipt_path and receipt_sha256 for every evidence item")
    reviewer = _require_object(record, "reviewer")
    _require_text(reviewer, "name")
    if reviewer.get("decision") not in {"accept", "reject", "needs_more_evidence"}:
        raise OperatingCoreError("learning_candidate.reviewer.decision is invalid")
    if record.get("anonymized") is not True:
        raise OperatingCoreError("learning_candidate.anonymized must be true")
    generalization = record.get("generalization")
    if generalization == "client_specific":
        return
    if generalization != "reviewed_general":
        raise OperatingCoreError("unsupported generalizations are rejected")
    promotion = _require_object(record, "promotion")
    _require_text(promotion, "reviewed_general_text")
    if not re.fullmatch(r"[a-f0-9]{64}", str(reviewer.get("review_binding_sha256", ""))):
        raise OperatingCoreError("reviewed general learning requires reviewer.review_binding_sha256")


def _learning_review_hash(candidate: dict[str, Any], evidence_hashes: list[str]) -> str:
    bound = copy.deepcopy(candidate)
    bound["reviewer"].pop("review_binding_sha256", None)
    return sha256_canonical({"candidate": bound, "resolved_receipt_sha256": sorted(evidence_hashes)})


def change_owner_decision_policy(previous: dict[str, Any], replacement: dict[str, Any], owner_decision: dict[str, Any]) -> None:
    """Allow a policy change only when the current owner records a specific decision.

    This is provenance validation, not identity authentication.  Persisting the
    replacement profile remains the caller's responsibility.
    """
    validate_record(previous)
    validate_record(replacement)
    if previous.get("record_type") != "client_profile" or replacement.get("record_type") != "client_profile":
        raise OperatingCoreError("owner policy changes require two client profiles")
    if previous["client_id"] != replacement["client_id"] or previous["account_id"] != replacement["account_id"]:
        raise OperatingCoreError("owner policy changes cannot move a client or account")
    if previous["owner"] != replacement["owner"]:
        raise OperatingCoreError("owner changes are not supported by this policy helper")
    if previous["owner_decision_policy"] == replacement["owner_decision_policy"]:
        raise OperatingCoreError("owner policy change has no policy difference")
    if not isinstance(owner_decision, dict):
        raise OperatingCoreError("owner policy change requires an owner decision record")
    if owner_decision.get("approved_by") != previous["owner"]:
        raise OperatingCoreError("owner policy change must name the current owner as approver")
    _require_id(owner_decision, "decision_id")
    _require_text(owner_decision, "rationale")
    parse_utc(owner_decision.get("approved_at"), "owner_decision.approved_at")
    supplied = _require_text(owner_decision, "decision_sha256")
    payload = {key: value for key, value in owner_decision.items() if key != "decision_sha256"}
    if owner_decision.get("previous_profile_sha256") != sha256_canonical(previous) or owner_decision.get("replacement_profile_sha256") != sha256_canonical(replacement):
        raise OperatingCoreError("owner policy decision must bind the exact previous and replacement profiles")
    if supplied != sha256_canonical(payload):
        raise OperatingCoreError("owner policy change decision_sha256 must bind the exact decision record")


def promote_learning_candidate(
    candidate: dict[str, Any], client_profile: dict[str, Any], private_workspace: Path, shared_workspace: Path, relative_output: str | Path
) -> Path:
    """Write only a reviewed general-text projection with bounded provenance.

    Evidence, receipt IDs, client IDs, reviewer identity, and the full candidate
    are intentionally excluded from the shared projection.  A client-specific
    learning is valid local evidence but cannot be promoted to a shared target.
    """
    validate_record(candidate)
    validate_record(client_profile)
    if client_profile.get("record_type") != "client_profile" or candidate["client_id"] != client_profile["client_id"]:
        raise OperatingCoreError("learning promotion requires the matching client profile")
    if candidate.get("stage") != "reviewed" or candidate["reviewer"]["decision"] != "accept":
        raise OperatingCoreError("learning promotion requires reviewer.accept")
    if candidate.get("generalization") != "reviewed_general":
        raise OperatingCoreError("client-specific learning cannot be promoted to shared output")
    private_root = Path(private_workspace).absolute()
    shared_root = Path(shared_workspace).absolute()
    try:
        reject_symlinks(private_root)
        reject_symlinks(shared_root)
    except SafeIOError as exc:
        raise OperatingCoreError("private and shared workspaces must not be symlinks or reparse points") from exc
    if not private_root.is_dir() or not shared_root.is_dir():
        raise OperatingCoreError("private and shared workspaces must be directories")
    if private_root == shared_root:
        raise OperatingCoreError("shared learning target must be separate from the private workspace")
    try:
        private_root.relative_to(shared_root)
        raise OperatingCoreError("private and shared workspaces must not be nested")
    except ValueError:
        pass
    try:
        shared_root.relative_to(private_root)
        raise OperatingCoreError("private and shared workspaces must not be nested")
    except ValueError:
        pass
    promotion = candidate["promotion"]
    public_text = promotion["reviewed_general_text"]
    forbidden = [candidate["client_id"], client_profile["account_id"], client_profile["owner"], "@", "token", "secret", "password", "sk-proj-", "sk-", "ghp_", "bearer", "private key", "usd", "eur", "gbp", "amount_micros", "daily_budget"]
    if any(token and token.lower() in public_text.lower() for token in forbidden):
        raise OperatingCoreError("reviewed general text contains an obvious private identifier or secret marker")
    receipt_hashes: list[str] = []
    resolved_receipts: list[dict[str, Any]] = []
    for item in candidate["evidence"]:
        receipt = load_json(safe_workspace_path(private_root, item["receipt_path"]))
        validate_record(receipt)
        if receipt.get("record_type") != "action_receipt":
            raise OperatingCoreError("learning evidence must resolve to an action_receipt")
        actual = sha256_canonical(receipt)
        if actual != item["receipt_sha256"]:
            raise OperatingCoreError("learning evidence receipt hash does not match the resolved private receipt")
        if receipt.get("observed_account_id") != client_profile["account_id"]:
            raise OperatingCoreError("learning evidence receipt account does not match the client profile")
        receipt_hashes.append(actual)
        resolved_receipts.append(receipt)
    # This is a bounded screen for identifiers resolved from the private
    # receipts. It is not an anonymization guarantee for arbitrary prose.
    resolved_private_identifiers: set[str] = set()
    for receipt in resolved_receipts:
        for key in ("id", "operation_id", "action_plan_id", "campaign_id"):
            value = receipt.get(key)
            if isinstance(value, str) and value:
                resolved_private_identifiers.add(value)
        target = receipt.get("target")
        if isinstance(target, dict):
            value = target.get("resource_id")
            if isinstance(value, str) and value:
                resolved_private_identifiers.add(value)
    lowered_public_text = public_text.casefold()
    if any(identifier.casefold() in lowered_public_text for identifier in resolved_private_identifiers):
        raise OperatingCoreError("reviewed general text contains a resolved private receipt identifier")
    if candidate["reviewer"]["review_binding_sha256"] != _learning_review_hash(candidate, receipt_hashes):
        raise OperatingCoreError("reviewer binding does not match the exact reviewed text and receipt hashes")
    if candidate.get("lesson_type") in {"policy", "authority"}:
        owner_decision = _require_object(candidate, "owner_decision")
        if owner_decision.get("approved_by") != client_profile["owner"]:
            raise OperatingCoreError("policy or authority learning requires the client owner decision")
        _require_id(owner_decision, "decision_id")
        if owner_decision.get("reviewed_text_sha256") != sha256_canonical(public_text) or owner_decision.get("receipt_sha256") != sorted(receipt_hashes):
            raise OperatingCoreError("policy or authority owner decision must bind exact reviewed text and receipt hashes")
        supplied_decision_hash = _require_text(owner_decision, "decision_sha256")
        if supplied_decision_hash != sha256_canonical({key: value for key, value in owner_decision.items() if key != "decision_sha256"}):
            raise OperatingCoreError("policy or authority owner decision hash is invalid")
    output = safe_workspace_path(shared_root, relative_output)
    supersedes = promotion.get("supersedes_reviewed_text_sha256", [])
    if (
        not isinstance(supersedes, list)
        or not all(isinstance(value, str) and re.fullmatch(r"[a-f0-9]{64}", value) for value in supersedes)
        or len(set(supersedes)) != len(supersedes)
    ):
        raise OperatingCoreError("promotion.supersedes_reviewed_text_sha256 must be unique lowercase SHA-256 digests")
    projection = {
        "schema_version": SCHEMA_VERSION,
        "record_type": "promoted_learning",
        "reviewed_general_text": public_text,
        "reviewed_text_sha256": sha256_canonical(public_text),
        "receipt_sha256": sorted(receipt_hashes),
        "evidence_scope": sorted({receipt["evidence_scope"] for receipt in resolved_receipts}),
        "supersedes_reviewed_text_sha256": supersedes,
        "promoted_at": utc_text(),
    }
    # Write exactly the reviewed public projection, never the private candidate.
    try:
        write_new(output, (canonical_json(projection) + "\n").encode("utf-8"))
    except FileExistsError as exc:
        raise OperatingCoreError("refusing to overwrite an existing shared learning projection") from exc
    except (OSError, SafeIOError) as exc:
        raise OperatingCoreError(f"cannot safely write shared learning projection: {exc}") from exc
    return output


def make_action_binding(action: dict[str, Any], *, decision_id: str, approved_by: str, approved_at: str, expires_at: str) -> dict[str, Any]:
    """Create review provenance for an already-defined action body, without signing it."""
    candidate = {
        "schema_version": SCHEMA_VERSION,
        "record_type": "action_plan",
        "id": "binding-check",
        "created_at": approved_at,
        "campaign_plan_id": "plan",
        "action": action,
        "approval": {
            "decision_id": decision_id,
            "approved_by": approved_by,
            "approved_at": approved_at,
            "expires_at": expires_at,
            "approved_action_sha256": sha256_canonical(action),
            "provenance_notice": ACTION_PROVENANCE_NOTICE,
        },
    }
    candidate["approval"]["decision_sha256"] = sha256_canonical(candidate["approval"])
    _validate_action_plan(candidate)
    return candidate["approval"]


def safe_workspace_path(workspace: Path, relative: str | Path) -> Path:
    """Contain private operation data and reject links at every path component."""
    workspace = Path(workspace).absolute()
    try:
        reject_symlinks(workspace)
    except SafeIOError as exc:
        raise OperatingCoreError("workspace must not be a symlink or reparse point") from exc
    if not workspace.is_dir():
        raise OperatingCoreError("workspace must be an existing non-symlink directory")
    target = workspace / relative
    try:
        target.relative_to(workspace)
    except ValueError as exc:
        raise OperatingCoreError("operation path escapes the private workspace") from exc
    current = workspace
    for part in Path(relative).parts:
        if part in {"", ".", ".."}:
            raise OperatingCoreError("operation path has an unsafe component")
        current = current / part
        try:
            reject_symlinks(current)
        except SafeIOError as exc:
            raise OperatingCoreError("symlinks or reparse points are not allowed in private operation paths") from exc
    return target


@dataclass
class AccountLock:
    workspace: Path
    account_id: str
    token: str = field(default_factory=lambda: secrets.token_hex(16))
    path: Path | None = None

    def acquire(self) -> None:
        if not IDENTIFIER.fullmatch(self.account_id):
            raise OperatingCoreError("account_id is invalid")
        lock_path = safe_workspace_path(self.workspace, Path("locks") / f"{self.account_id}.lock")
        try:
            write_new(lock_path, (canonical_json({"account_id": self.account_id, "created_at": utc_text(), "token": self.token}) + "\n").encode("utf-8"))
        except FileExistsError as exc:
            raise OperatingCoreError("account lock already exists; stale lock takeover is intentionally disabled") from exc
        except (OSError, SafeIOError) as exc:
            raise OperatingCoreError(f"cannot safely create account lock: {exc}") from exc
        self.path = lock_path

    def release(self) -> None:
        if self.path is None:
            return
        try:
            payload = load_json(self.path)
            if payload.get("token") != self.token:
                raise OperatingCoreError("refusing to release a lock not owned by this helper instance")
            try:
                unlink_regular(self.path)
            except (OSError, SafeIOError) as exc:
                raise OperatingCoreError(f"cannot safely remove account lock: {exc}") from exc
        finally:
            self.path = None

    def __enter__(self) -> "AccountLock":
        self.acquire()
        return self

    def __exit__(self, *_: Any) -> None:
        self.release()


@dataclass
class CheckpointStore:
    workspace: Path
    operation_id: str

    @property
    def path(self) -> Path:
        return safe_workspace_path(self.workspace, Path("operations") / f"{self.operation_id}.jsonl")

    def append(self, event: str, **fields: Any) -> dict[str, Any]:
        entry = {"event": event, "at": utc_text(), **fields}
        path = self.path
        try:
            append_regular(path, (canonical_json(entry) + "\n").encode("utf-8"))
        except (OSError, SafeIOError) as exc:
            raise OperatingCoreError(f"cannot safely append checkpoint: {exc}") from exc
        return entry

    def events(self) -> list[dict[str, Any]]:
        path = self.path
        if not path.exists():
            return []
        try:
            entries = [json.loads(line) for line in read_regular(path).decode("utf-8").splitlines() if line.strip()]
        except (OSError, SafeIOError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise OperatingCoreError(f"checkpoint log is corrupt: {path}") from exc
        allowed = {"started", "preflight_passed", "saved", "uncertain", "reconciled", "rejected", "receipt"}
        for entry in entries:
            if not isinstance(entry, dict) or entry.get("event") not in allowed:
                raise OperatingCoreError("checkpoint log contains an invalid event")
            parse_utc(entry.get("at"), "checkpoint.at")
        if entries and (entries[0].get("event") != "started" or sum(entry.get("event") == "started" for entry in entries) != 1):
            raise OperatingCoreError("checkpoint log must begin with exactly one started event")
        return entries

    def has_terminal_receipt(self, action_plan: dict[str, Any], ui: "SimulatedAdsUI") -> dict[str, Any] | None:
        action = action_plan["action"]
        for entry in reversed(self.events()):
            if entry.get("event") == "receipt" and isinstance(entry.get("receipt"), dict):
                receipt = entry["receipt"]
                validate_record(receipt)
                if receipt.get("outcome") == "uncertain":
                    continue
                if receipt.get("operation_id") != self.operation_id or receipt.get("action_plan_id") != action_plan["id"] or receipt.get("action_sha256") != sha256_canonical(action) or receipt.get("observed_account_id") != action["account_id"] or receipt.get("target") != action["target"]:
                    raise OperatingCoreError("checkpoint terminal receipt does not bind the current operation and action")
                if receipt["outcome"] in {"succeeded", "reconciled"} and not ui.reconcile(action, sha256_canonical(action)):
                    raise OperatingCoreError("checkpoint success cannot be reconciled against the current simulated UI")
                return receipt
        return None


@dataclass
class SimulatedAdsUI:
    """Explicit in-memory model used only by tests and the simulate CLI command."""

    account_id: str
    ui_revision: str
    daily_budget_micros: int
    maximum_effect: dict[str, Any]
    session_active: bool = True
    save_mode: str = "success"  # success, lost_session, uncertain_after_create
    campaigns: dict[str, dict[str, Any]] = field(default_factory=dict)

    @classmethod
    def from_record(cls, data: dict[str, Any]) -> "SimulatedAdsUI":
        return cls(
            account_id=_require_id(data, "account_id"),
            ui_revision=_require_text(data, "ui_revision"),
            daily_budget_micros=_require_nonnegative_int(data, "daily_budget_micros"),
            maximum_effect=_require_object(data, "maximum_effect"),
            session_active=bool(data.get("session_active", True)),
            save_mode=data.get("save_mode", "success"),
            campaigns=dict(data.get("campaigns", {})),
        )

    def as_record(self) -> dict[str, Any]:
        return {
            "account_id": self.account_id,
            "ui_revision": self.ui_revision,
            "daily_budget_micros": self.daily_budget_micros,
            "maximum_effect": self.maximum_effect,
            "session_active": self.session_active,
            "save_mode": self.save_mode,
            "campaigns": self.campaigns,
        }

    def reconcile(self, action: dict[str, Any], action_hash: str) -> dict[str, Any] | None:
        existing = self.campaigns.get(action["campaign_id"])
        if existing and existing.get("action_sha256") == action_hash:
            return existing
        return None

    def create_campaign(self, action: dict[str, Any], action_hash: str) -> dict[str, Any]:
        if not self.session_active or self.save_mode == "lost_session":
            raise OperatingCoreError("simulated session is not active; no save was attempted")
        if action["campaign_id"] in self.campaigns:
            raise OperatingCoreError("campaign identifier already exists with a different action binding")
        created = {
            "campaign_id": action["campaign_id"], "account_id": self.account_id, "action_sha256": action_hash,
            "observed_ui_revision": self.ui_revision, "observed_budget": action["budget"], "created_at": utc_text(),
        }
        if self.save_mode == "uncertain_after_create":
            self.campaigns[action["campaign_id"]] = created
            raise UncertainOutcome("simulated save acknowledgement was lost; reconcile before retry")
        self.campaigns[action["campaign_id"]] = created
        return created


def _receipt(operation_id: str, action_plan: dict[str, Any], ui: SimulatedAdsUI, outcome: str, detail: str, *, reconciled: bool = False) -> dict[str, Any]:
    action = action_plan["action"]
    observed_settings: dict[str, Any] = {"ui_revision": ui.ui_revision}
    if action["kind"] == "create_campaign":
        observed_settings["budget"] = {"currency": action["budget"]["currency"], "daily_budget_micros": ui.daily_budget_micros, "maximum_effect": ui.maximum_effect}
    receipt = {
        "schema_version": SCHEMA_VERSION,
        "record_type": "action_receipt",
        "id": f"receipt-{operation_id}",
        "created_at": utc_text(),
        "operation_id": operation_id,
        "action_plan_id": action_plan["id"],
        "action_sha256": sha256_canonical(action),
        "observed_account_id": ui.account_id,
        "target": action["target"],
        "observed_settings": observed_settings,
        "outcome": "reconciled" if reconciled else outcome,
        "detail": detail,
        "observed_at": utc_text(),
        "simulated": True,
        "evidence_scope": "simulated",
        "evidence_refs": [{"type": "simulated_ui_state", "sha256": sha256_canonical(ui.as_record())}],
    }
    if action["kind"] == "create_campaign":
        receipt["campaign_id"] = action["campaign_id"]
    return receipt


def preflight(action_plan: dict[str, Any], campaign_plan: dict[str, Any], ui: SimulatedAdsUI, *, now: datetime | None = None, allow_expired: bool = False) -> bool:
    validate_record(action_plan)
    validate_record(campaign_plan)
    if action_plan["record_type"] != "action_plan" or campaign_plan["record_type"] != "campaign_plan":
        raise OperatingCoreError("preflight requires an action plan and campaign plan")
    action = action_plan["action"]
    if action_plan["campaign_plan_id"] != campaign_plan["id"]:
        raise OperatingCoreError("action plan does not reference this campaign plan")
    if action["account_id"] != campaign_plan["account_id"] or action["account_id"] != ui.account_id:
        raise OperatingCoreError("wrong account: action, campaign plan, and observed UI must match")
    if action["campaign_id"] != campaign_plan["campaign_id"]:
        raise OperatingCoreError("campaign identifier drift between plan and action")
    if action["expected_ui_revision"] != campaign_plan["expected_ui_revision"] or action["expected_ui_revision"] != ui.ui_revision:
        raise OperatingCoreError("UI revision drift detected")
    if action["budget"] != campaign_plan["budget"]:
        raise OperatingCoreError("budget drift between campaign plan and approved action")
    if action["campaign_plan_sha256"] != sha256_canonical(campaign_plan):
        raise OperatingCoreError("campaign plan binding drift detected")
    if action["budget"]["daily_budget_micros"] != ui.daily_budget_micros or action["budget"]["maximum_effect"] != ui.maximum_effect:
        raise OperatingCoreError("cost drift detected: observed budget or maximum effect differs from approved action")
    if not ui.session_active:
        raise OperatingCoreError("simulated session is not active")
    current_time = now or utc_now()
    approved_at = parse_utc(action_plan["approval"]["approved_at"], "approval.approved_at")
    if current_time < approved_at:
        raise OperatingCoreError("approved action is not active yet")
    expired = current_time >= parse_utc(action_plan["approval"]["expires_at"], "approval.expires_at")
    if expired and not allow_expired:
        raise OperatingCoreError("approved action has expired")
    return expired


def _assert_operation_binding(store: CheckpointStore, action_hash: str, account_id: str, campaign_plan_hash: str) -> None:
    for event in store.events():
        if event.get("event") != "started":
            continue
        actual = (event.get("action_sha256"), event.get("account_id"), event.get("campaign_plan_sha256"))
        expected = (action_hash, account_id, campaign_plan_hash)
        if actual != expected:
            raise OperatingCoreError("operation_id is already bound to a different action, account, or campaign plan")
        return


def execute_simulated(
    action_plan: dict[str, Any], campaign_plan: dict[str, Any], ui: SimulatedAdsUI, workspace: Path, operation_id: str, *, now: datetime | None = None
) -> dict[str, Any]:
    """Execute against only ``SimulatedAdsUI`` with durable checkpoints and reconciliation."""
    _require_id({"operation_id": operation_id}, "operation_id")
    validate_record(action_plan)
    validate_record(campaign_plan)
    action = action_plan["action"]
    action_hash = sha256_canonical(action)
    campaign_plan_hash = sha256_canonical(campaign_plan)
    account_id = action["account_id"]
    store = CheckpointStore(workspace, operation_id)
    with AccountLock(workspace, f"operation-{operation_id}"), AccountLock(workspace, account_id):
        _assert_operation_binding(store, action_hash, account_id, campaign_plan_hash)
        if not store.events():
            store.append("started", action_plan_id=action_plan["id"], action_sha256=action_hash, account_id=account_id, campaign_plan_sha256=campaign_plan_hash)
        if action["kind"] != "create_campaign":
            receipt = _receipt(operation_id, action_plan, ui, "rejected", "simulate executor supports only create_campaign")
            store.append("rejected", reason=receipt["detail"])
            store.append("receipt", receipt=receipt)
            return receipt
        # Identity, UI, budget, session, and hash bindings must pass before a
        # reconciliation lookup can declare an existing campaign successful.
        try:
            expired = preflight(action_plan, campaign_plan, ui, now=now, allow_expired=True)
        except OperatingCoreError as exc:
            receipt = _receipt(operation_id, action_plan, ui, "rejected", str(exc))
            store.append("rejected", reason=str(exc))
            store.append("receipt", receipt=receipt)
            return receipt
        prior = store.has_terminal_receipt(action_plan, ui)
        if prior:
            return prior
        found = ui.reconcile(action, action_hash)
        if found:
            detail = "existing matching simulated campaign found during reconciliation"
            if expired:
                detail += "; approval was expired, so reconciliation was read-only and no save was attempted"
            receipt = _receipt(operation_id, action_plan, ui, "succeeded", detail, reconciled=True)
            store.append("reconciled", campaign=found)
            store.append("receipt", receipt=receipt)
            return receipt
        if expired:
            receipt = _receipt(operation_id, action_plan, ui, "rejected", "approved action has expired")
            store.append("rejected", reason="approved action has expired")
            store.append("receipt", receipt=receipt)
            return receipt
        store.append("preflight_passed", action_sha256=action_hash)
        try:
            created = ui.create_campaign(action, action_hash)
        except UncertainOutcome as exc:
            store.append("uncertain", reason=str(exc))
            found = ui.reconcile(action, action_hash)
            if found:
                receipt = _receipt(operation_id, action_plan, ui, "succeeded", "simulated campaign found after uncertain save", reconciled=True)
                store.append("reconciled", campaign=found)
                store.append("receipt", receipt=receipt)
                return receipt
            receipt = _receipt(operation_id, action_plan, ui, "uncertain", str(exc))
            store.append("receipt", receipt=receipt)
            return receipt
        except OperatingCoreError as exc:
            receipt = _receipt(operation_id, action_plan, ui, "rejected", str(exc))
            store.append("rejected", reason=str(exc))
            store.append("receipt", receipt=receipt)
            return receipt
        receipt = _receipt(operation_id, action_plan, ui, "succeeded", "simulated campaign created")
        store.append("saved", campaign=created)
        store.append("receipt", receipt=receipt)
        return receipt


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="operating_core.py",
        description="Validate v0.2 operation records and run only the controlled simulated Ads UI.",
    )
    sub = parser.add_subparsers(dest="command", required=True)
    validate = sub.add_parser("validate", help="validate one versioned JSON record")
    validate.add_argument("record", type=Path)
    hash_action = sub.add_parser("hash-action", help="print the canonical SHA-256 for an action object")
    hash_action.add_argument("action_json", type=Path)
    check = sub.add_parser("check", help="preflight the supported create_campaign simulation against observed local state")
    check.add_argument("--action-plan", required=True, type=Path)
    check.add_argument("--campaign-plan", required=True, type=Path)
    check.add_argument("--state", required=True, type=Path)
    simulate = sub.add_parser("simulate-execute", help="run a locally controlled simulation, never a live account")
    simulate.add_argument("--action-plan", required=True, type=Path)
    simulate.add_argument("--campaign-plan", required=True, type=Path)
    simulate.add_argument("--state", required=True, type=Path)
    simulate.add_argument("--workspace", required=True, type=Path)
    simulate.add_argument("--operation-id", required=True)
    simulate.add_argument("--receipt-out", type=Path)
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    args = _parser().parse_args(list(argv) if argv is not None else None)
    try:
        if args.command == "validate":
            record = load_json(args.record)
            validate_record(record)
            print(json.dumps({"valid": True, "record_type": record["record_type"], "id": record["id"]}, sort_keys=True))
            return 0
        if args.command == "hash-action":
            action = load_json(args.action_json)
            print(sha256_canonical(action))
            return 0
        if args.command == "check":
            action_plan = load_json(args.action_plan)
            campaign_plan = load_json(args.campaign_plan)
            if action_plan.get("action", {}).get("kind") != "create_campaign":
                raise OperatingCoreError("check currently supports only the create_campaign simulated fixture")
            expired = preflight(action_plan, campaign_plan, SimulatedAdsUI.from_record(load_json(args.state)), allow_expired=True)
            print(canonical_json({"ok": True, "expired": expired, "executor": "simulated create_campaign only"}))
            return 0 if not expired else 2
        action_plan = load_json(args.action_plan)
        campaign_plan = load_json(args.campaign_plan)
        state = load_json(args.state)
        ui = SimulatedAdsUI.from_record(state)
        receipt = execute_simulated(action_plan, campaign_plan, ui, args.workspace, args.operation_id)
        save_json(args.state, ui.as_record())
        if args.receipt_out:
            save_json(args.receipt_out, receipt)
        print(canonical_json(receipt))
        return 0 if receipt.get("outcome") in {"succeeded", "reconciled"} else 2
    except OperatingCoreError as exc:
        print(f"operating core error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
