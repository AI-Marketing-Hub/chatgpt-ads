#!/usr/bin/env python3
from __future__ import annotations

import copy
import sys
import unittest
from datetime import UTC, datetime, timedelta
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from scripts.check_browser_action import check_browser_action
from scripts.operating_core import ACTION_PROVENANCE_NOTICE, OperatingCoreError, sha256_canonical


NOW = datetime(2026, 9, 10, 12, 0, tzinfo=UTC)
MAX_EFFECT = {"kind": "maximum_total_spend_micros", "amount_micros": 250_000_000}


def records(kind: str = "configure") -> tuple[dict, dict, dict]:
    reviewed = {"id": "reviewed-plan", "status": "reviewed", "configuration": {"objective": "bounded"}}
    action = {
        "kind": kind, "account_id": "acct-demo", "target": {"resource_type": "campaign", "resource_id": "campaign-demo"},
        "before": {"status": "paused", "daily_budget_micros": 25_000_000}, "after": {"status": "active", "daily_budget_micros": 25_000_000},
        "cost": {"currency": "USD", "maximum_effect": MAX_EFFECT}, "rollback": "pause the target after a new review", "verification": {"method": "operator inspection", "expected": "active"},
        "expected_ui_revision": "ui-7", "campaign_plan_sha256": sha256_canonical(reviewed),
    }
    if kind == "create_campaign":
        action.update({"campaign_id": "campaign-demo", "budget": {"currency": "USD", "daily_budget_micros": 25_000_000, "maximum_effect": MAX_EFFECT}})
    approval = {"decision_id": "decision-1", "approved_by": "human", "approved_at": "2026-09-01T00:00:00Z", "expires_at": "2026-10-01T00:00:00Z", "approved_action_sha256": sha256_canonical(action), "provenance_notice": ACTION_PROVENANCE_NOTICE}
    approval["decision_sha256"] = sha256_canonical(approval)
    plan = {"schema_version": "v0.2", "record_type": "action_plan", "id": f"action-{kind}", "created_at": "2026-09-01T00:00:00Z", "campaign_plan_id": "reviewed-plan", "action": action, "approval": approval}
    observation = {"schema_version": "v0.2", "record_type": "browser_observation", "id": "obs-1", "observed_at": "2026-09-10T11:58:00Z", "account_id": "acct-demo", "session_active": True, "ambiguous": False, "ui_revision": "ui-7", "target": copy.deepcopy(action["target"]), "observed_settings": copy.deepcopy(action["before"]), "proposed_settings": copy.deepcopy(action["after"]), "cost": copy.deepcopy(action["cost"])}
    return plan, reviewed, observation


class BrowserGuardTests(unittest.TestCase):
    def test_all_supported_kinds_have_a_read_only_guard_path(self) -> None:
        for kind in ("create_campaign", "edit_campaign", "status_change", "roles_change", "audience_change", "catalog_change", "bulk_change", "configure"):
            plan, reviewed, observation = records(kind)
            report = check_browser_action(plan, reviewed, observation, now=NOW)
            self.assertTrue(report["eligible"])
            self.assertIn("not authentication", report["limitations"])

    def test_account_field_cost_session_and_time_drift_are_refused(self) -> None:
        mutations = [
            ("account_id", "acct-other", "wrong account"),
            ("ui_revision", "ui-8", "UI revision drift"),
            ("session_active", False, "session is not active"),
            ("ambiguous", True, "ambiguous"),
        ]
        for field, value, message in mutations:
            plan, reviewed, observation = records()
            observation[field] = value
            with self.assertRaisesRegex(OperatingCoreError, message):
                check_browser_action(plan, reviewed, observation, now=NOW)
        plan, reviewed, observation = records()
        observation["observed_settings"] = {"status": "active"}
        with self.assertRaisesRegex(OperatingCoreError, "observed settings"):
            check_browser_action(plan, reviewed, observation, now=NOW)
        plan, reviewed, observation = records()
        observation["cost"]["maximum_effect"]["amount_micros"] += 1
        with self.assertRaisesRegex(OperatingCoreError, "cost"):
            check_browser_action(plan, reviewed, observation, now=NOW)
        plan, reviewed, observation = records()
        observation["observed_at"] = "2026-09-10T11:54:59Z"
        with self.assertRaisesRegex(OperatingCoreError, "stale"):
            check_browser_action(plan, reviewed, observation, now=NOW)
        plan, reviewed, observation = records()
        observation["observed_at"] = "2026-09-10T12:00:01Z"
        with self.assertRaisesRegex(OperatingCoreError, "future"):
            check_browser_action(plan, reviewed, observation, now=NOW)

    def test_guard_age_and_json_types_are_exact(self) -> None:
        plan, reviewed, observation = records()
        with self.assertRaises(OperatingCoreError):
            check_browser_action(plan, reviewed, observation, now=NOW, max_age_seconds=301)
        plan["action"]["before"]["enabled"] = 1
        observation["observed_settings"]["enabled"] = True
        plan["approval"]["approved_action_sha256"] = sha256_canonical(plan["action"])
        del plan["approval"]["decision_sha256"]
        plan["approval"]["decision_sha256"] = sha256_canonical(plan["approval"])
        with self.assertRaisesRegex(OperatingCoreError, "observed settings"):
            check_browser_action(plan, reviewed, observation, now=NOW)

    def test_plan_hash_target_and_approval_window_are_refused_when_drifted(self) -> None:
        plan, reviewed, observation = records()
        reviewed["status"] = "changed"
        with self.assertRaisesRegex(OperatingCoreError, "hash"):
            check_browser_action(plan, reviewed, observation, now=NOW)
        plan, reviewed, observation = records()
        observation["target"]["resource_id"] = "other"
        with self.assertRaisesRegex(OperatingCoreError, "target"):
            check_browser_action(plan, reviewed, observation, now=NOW)
        plan, reviewed, observation = records()
        with self.assertRaisesRegex(OperatingCoreError, "not active yet"):
            check_browser_action(plan, reviewed, observation, now=datetime(2026, 8, 31, tzinfo=UTC))
        plan, reviewed, observation = records()
        with self.assertRaisesRegex(OperatingCoreError, "expired"):
            check_browser_action(plan, reviewed, observation, now=datetime(2026, 10, 1, tzinfo=UTC))


if __name__ == "__main__":
    raise SystemExit(unittest.main())
