#!/usr/bin/env python3
"""Read-only browser-observation guard for v0.2 action plans.

It validates an operator-observed browser snapshot. It cannot authenticate a
user, establish that an observation is truthful, click a UI control, or change
an account.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Iterable

try:  # Supports both ``python scripts/...`` and package-style test imports.
    from scripts.operating_core import OperatingCoreError, canonical_json, load_json, parse_utc, sha256_canonical, utc_now, validate_record
except ModuleNotFoundError:
    from operating_core import OperatingCoreError, canonical_json, load_json, parse_utc, sha256_canonical, utc_now, validate_record


def _object(value: Any, name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise OperatingCoreError(f"browser observation {name} must be an object")
    return value


def _text(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise OperatingCoreError(f"browser observation {name} must be a non-empty string")
    return value


def validate_observation(observation: dict[str, Any]) -> None:
    if not isinstance(observation, dict):
        raise OperatingCoreError("browser observation must be an object")
    if observation.get("schema_version") != "v0.2" or observation.get("record_type") != "browser_observation":
        raise OperatingCoreError("browser observation must be a v0.2 browser_observation")
    for field in ("id", "account_id", "ui_revision"):
        _text(observation.get(field), field)
    parse_utc(observation.get("observed_at"), "observed_at")
    if observation.get("session_active") is not True:
        raise OperatingCoreError("browser observation session is not active")
    if observation.get("ambiguous") is not False:
        raise OperatingCoreError("browser observation is ambiguous or omits ambiguity state")
    target = _object(observation.get("target"), "target")
    _text(target.get("resource_type"), "target.resource_type")
    _text(target.get("resource_id"), "target.resource_id")
    for field in ("observed_settings", "proposed_settings", "cost"):
        _object(observation.get(field), field)
    cost = observation["cost"]
    _text(cost.get("currency"), "cost.currency")
    _object(cost.get("maximum_effect"), "cost.maximum_effect")


def check_browser_action(
    action_plan: dict[str, Any], reviewed_plan: dict[str, Any], observation: dict[str, Any], *, now: datetime | None = None, max_age_seconds: int = 300
) -> dict[str, Any]:
    """Return a preflight report or raise ``OperatingCoreError`` on a mismatch."""
    if not isinstance(max_age_seconds, int) or isinstance(max_age_seconds, bool) or not 0 <= max_age_seconds <= 300:
        raise OperatingCoreError("max_age_seconds must be an integer from 0 to 300")
    validate_record(action_plan)
    if action_plan.get("record_type") != "action_plan":
        raise OperatingCoreError("browser guard requires an action_plan")
    if not isinstance(reviewed_plan, dict):
        raise OperatingCoreError("reviewed plan must be a JSON object")
    validate_observation(observation)
    action = action_plan["action"]
    expected_revision = _text(action.get("expected_ui_revision"), "action.expected_ui_revision")
    if reviewed_plan.get("id") != action_plan.get("campaign_plan_id"):
        raise OperatingCoreError("reviewed plan ID does not match action campaign_plan_id")
    if action.get("campaign_plan_sha256") != sha256_canonical(reviewed_plan):
        raise OperatingCoreError("reviewed plan hash does not match action.campaign_plan_sha256")
    if observation["account_id"] != action["account_id"]:
        raise OperatingCoreError("wrong account in browser observation")
    if observation["ui_revision"] != expected_revision:
        raise OperatingCoreError("UI revision drift in browser observation")
    if canonical_json(observation["target"]) != canonical_json(action["target"]):
        raise OperatingCoreError("browser observation target differs from action target")
    if canonical_json(observation["observed_settings"]) != canonical_json(action["before"]):
        raise OperatingCoreError("browser observed settings differ from action.before")
    if canonical_json(observation["proposed_settings"]) != canonical_json(action["after"]):
        raise OperatingCoreError("browser proposed settings differ from action.after")
    if canonical_json(observation["cost"]) != canonical_json(action["cost"]):
        raise OperatingCoreError("browser observed cost differs from action.cost")
    current = now or utc_now()
    approved_at = parse_utc(action_plan["approval"]["approved_at"], "approval.approved_at")
    expires_at = parse_utc(action_plan["approval"]["expires_at"], "approval.expires_at")
    if current < approved_at:
        raise OperatingCoreError("approved action is not active yet")
    if current >= expires_at:
        raise OperatingCoreError("approved action has expired")
    observed_at = parse_utc(observation["observed_at"], "observed_at")
    age_seconds = (current - observed_at).total_seconds()
    if age_seconds < 0:
        raise OperatingCoreError("browser observation time is in the future")
    if age_seconds > max_age_seconds:
        raise OperatingCoreError("browser observation is stale")
    return {
        "schema_version": "v0.2",
        "record_type": "browser_guard_report",
        "eligible": True,
        "action_plan_id": action_plan["id"],
        "action_sha256": sha256_canonical(action),
        "reviewed_plan_sha256": sha256_canonical(reviewed_plan),
        "observation_id": observation["id"],
        "observed_at": observation["observed_at"],
        "checked_at": current.astimezone(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "max_age_seconds": max_age_seconds,
        "limitations": "Read-only consistency check. It is not authentication, truth verification, or a click executor.",
    }


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Read-only v0.2 browser observation guard. It never controls a browser or account.")
    parser.add_argument("--action-plan", required=True, type=Path)
    parser.add_argument("--reviewed-plan", required=True, type=Path)
    parser.add_argument("--observation", required=True, type=Path)
    parser.add_argument("--max-age-seconds", type=int, default=300)
    args = parser.parse_args(list(argv) if argv is not None else None)
    try:
        report = check_browser_action(load_json(args.action_plan), load_json(args.reviewed_plan), load_json(args.observation), max_age_seconds=args.max_age_seconds)
        print(canonical_json(report))
        return 0
    except OperatingCoreError as exc:
        print(canonical_json({"schema_version": "v0.2", "record_type": "browser_guard_report", "eligible": False, "error": str(exc), "limitations": "Read-only consistency check. It is not authentication, truth verification, or a click executor."}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
