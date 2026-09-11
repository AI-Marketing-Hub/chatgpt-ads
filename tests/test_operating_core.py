#!/usr/bin/env python3
"""Meaningful state-machine checks for the bounded simulated operating core."""
from __future__ import annotations

import json
import copy
import subprocess
import sys
import tempfile
import threading
import unittest
from datetime import UTC, datetime
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from scripts.operating_core import (
    ACTION_PROVENANCE_NOTICE,
    AccountLock,
    CheckpointStore,
    OperatingCoreError,
    SimulatedAdsUI,
    execute_simulated,
    make_action_binding,
    promote_learning_candidate,
    safe_workspace_path,
    validate_record,
    sha256_canonical,
)


CREATED = "2026-09-10T00:00:00Z"
FUTURE = "2099-01-01T00:00:00Z"


def campaign_plan(*, account_id: str = "acct-demo", revision: str = "ui-7", budget: int = 25_000_000) -> dict:
    return {
        "schema_version": "v0.2", "record_type": "campaign_plan", "id": "plan-demo", "created_at": CREATED,
        "client_id": "client-demo", "account_id": account_id, "campaign_id": "campaign-demo", "objective": "test a bounded creative", 
        "budget": {"currency": "USD", "daily_budget_micros": budget, "maximum_effect": {"kind": "maximum_total_spend_micros", "amount_micros": 250_000_000}}, "expected_ui_revision": revision, "evidence_reference": "local-test-evidence",
    }


def action_plan(plan: dict, *, expires_at: str = FUTURE) -> dict:
    action = {"kind": "create_campaign", "campaign_id": plan["campaign_id"], "account_id": plan["account_id"], "target": {"resource_type": "campaign", "resource_id": plan["campaign_id"]}, "before": {}, "after": {"campaign_id": plan["campaign_id"]}, "cost": {"currency": "USD", "maximum_effect": dict(plan["budget"]["maximum_effect"])}, "rollback": "Disable the simulated campaign after owner review.", "verification": {"method": "simulated campaign lookup", "expected": "matching campaign id and action hash"}, "expected_ui_revision": plan["expected_ui_revision"], "budget": dict(plan["budget"]), "campaign_plan_sha256": sha256_canonical(plan)}
    return {
        "schema_version": "v0.2", "record_type": "action_plan", "id": "action-demo", "created_at": CREATED,
        "campaign_plan_id": plan["id"], "action": action,
        "approval": make_action_binding(action, decision_id="decision-42", approved_by="human reviewer", approved_at=CREATED, expires_at=expires_at),
    }


def reviewed_learning_fixture() -> tuple[dict, dict, dict]:
    candidate = {
        "schema_version": "v0.2", "record_type": "learning_candidate", "id": "learning-private", "created_at": CREATED,
        "client_id": "client-demo", "hypothesis": "Private hypothesis", "scope": "private scope", "stage": "reviewed",
        "evidence": [], "reviewer": {"name": "Private reviewer", "decision": "accept", "review_binding_sha256": ""}, "anonymized": True, "generalization": "reviewed_general",
        "promotion": {"reviewed_general_text": "Review outcomes with the owner before reuse."},
    }
    profile = {"schema_version": "v0.2", "record_type": "client_profile", "id": "profile-demo", "created_at": CREATED, "client_id": "client-demo", "account_id": "acct-demo", "owner": "Example owner", "owner_decision_policy": {"owner_required": True, "allow_policy_change": False, "change_process": "record a reviewed owner decision"}}
    receipt = {"schema_version": "v0.2", "record_type": "action_receipt", "id": "receipt-zeta-48291", "created_at": CREATED, "operation_id": "operation-zeta-48291", "action_plan_id": "action-zeta-48291", "action_sha256": "a" * 64, "observed_account_id": "acct-demo", "target": {"resource_type": "campaign", "resource_id": "cmp-zeta-48291"}, "campaign_id": "cmp-zeta-48291", "observed_settings": {"ui_revision": "ui-7", "budget": {"currency": "USD", "daily_budget_micros": 25000000, "maximum_effect": {"kind": "maximum_total_spend_micros", "amount_micros": 250000000}}}, "outcome": "succeeded", "detail": "private", "observed_at": CREATED, "simulated": True, "evidence_scope": "simulated", "evidence_refs": [{"sha256": "b" * 64}]}
    return candidate, profile, receipt


def bind_learning_candidate(candidate: dict, receipt_hash: str) -> None:
    bound = copy.deepcopy(candidate)
    bound["reviewer"].pop("review_binding_sha256")
    candidate["reviewer"]["review_binding_sha256"] = sha256_canonical({"candidate": bound, "resolved_receipt_sha256": [receipt_hash]})


class OperatingCoreTests(unittest.TestCase):
    def run_action(self, plan: dict, action: dict, ui: SimulatedAdsUI, *, operation: str = "operation-1", now: datetime | None = None) -> tuple[dict, Path]:
        temp = tempfile.TemporaryDirectory(prefix="operating-core-")
        self.addCleanup(temp.cleanup)
        return execute_simulated(action, plan, ui, Path(temp.name), operation, now=now), Path(temp.name)

    def test_hash_binding_refuses_even_one_field_change(self) -> None:
        plan = campaign_plan()
        action = action_plan(plan)
        validate_record(action)
        action["action"]["budget"]["daily_budget_micros"] += 1
        with self.assertRaisesRegex(OperatingCoreError, "exact canonical action JSON"):
            validate_record(action)

    def test_decision_hash_binds_approval_expiry(self) -> None:
        plan = campaign_plan()
        action = action_plan(plan)
        action["approval"]["expires_at"] = "2098-01-01T00:00:00Z"
        with self.assertRaisesRegex(OperatingCoreError, "decision_sha256"):
            validate_record(action)

    def test_receipt_scope_and_checkpoint_shape_fail_closed(self) -> None:
        plan = campaign_plan()
        action = action_plan(plan)
        ui = SimulatedAdsUI("acct-demo", "ui-7", 25_000_000, {"kind": "maximum_total_spend_micros", "amount_micros": 250_000_000})
        receipt, workspace = self.run_action(plan, action, ui, operation="operation-shape")
        receipt["evidence_scope"] = "live_observed"
        with self.assertRaisesRegex(OperatingCoreError, "simulated receipt"):
            validate_record(receipt)
        checkpoint = workspace / "operations" / "operation-shape.jsonl"
        checkpoint.write_text(checkpoint.read_text() + json.dumps({"event": "started", "at": CREATED}) + "\n")
        with self.assertRaisesRegex(OperatingCoreError, "exactly one started"):
            CheckpointStore(workspace, "operation-shape").events()

    def test_wrong_account_changed_ui_changed_budget_and_expiry_are_rejected_before_save(self) -> None:
        cases = [
            (campaign_plan(), SimulatedAdsUI("acct-other", "ui-7", 25_000_000, {"kind": "maximum_total_spend_micros", "amount_micros": 250_000_000}), "wrong account"),
            (campaign_plan(), SimulatedAdsUI("acct-demo", "ui-8", 25_000_000, {"kind": "maximum_total_spend_micros", "amount_micros": 250_000_000}), "UI revision drift"),
            (campaign_plan(), SimulatedAdsUI("acct-demo", "ui-7", 25_000_001, {"kind": "maximum_total_spend_micros", "amount_micros": 250_000_000}), "cost drift"),
            (campaign_plan(), SimulatedAdsUI("acct-demo", "ui-7", 25_000_000, {"kind": "maximum_total_spend_micros", "amount_micros": 250_000_000}), "expired"),
        ]
        for index, (plan, ui, phrase) in enumerate(cases):
            expiry = "2027-01-01T00:00:00Z" if phrase == "expired" else FUTURE
            now = datetime(2028, 1, 1, tzinfo=UTC) if phrase == "expired" else None
            receipt, _ = self.run_action(plan, action_plan(plan, expires_at=expiry), ui, operation=f"operation-{index}", now=now)
            self.assertEqual("rejected", receipt["outcome"])
            self.assertIn(phrase, receipt["detail"])
            self.assertEqual({}, ui.campaigns)

    def test_lost_session_does_not_create_campaign(self) -> None:
        plan = campaign_plan()
        ui = SimulatedAdsUI("acct-demo", "ui-7", 25_000_000, {"kind": "maximum_total_spend_micros", "amount_micros": 250_000_000}, session_active=False)
        receipt, _ = self.run_action(plan, action_plan(plan), ui)
        self.assertEqual("rejected", receipt["outcome"])
        self.assertIn("session", receipt["detail"])
        self.assertEqual({}, ui.campaigns)

    def test_approval_is_rejected_before_its_utc_start(self) -> None:
        plan = campaign_plan()
        action = action_plan(plan)
        action["approval"]["approved_at"] = "2098-01-01T00:00:00Z"
        action["approval"]["expires_at"] = "2099-01-01T00:00:00Z"
        action["approval"]["decision_sha256"] = sha256_canonical({key: value for key, value in action["approval"].items() if key != "decision_sha256"})
        ui = SimulatedAdsUI("acct-demo", "ui-7", 25_000_000, {"kind": "maximum_total_spend_micros", "amount_micros": 250_000_000})
        receipt, _ = self.run_action(plan, action, ui, now=datetime(2097, 1, 1, tzinfo=UTC))
        self.assertEqual("rejected", receipt["outcome"])
        self.assertIn("not active yet", receipt["detail"])

    def test_uncertain_save_reconciles_and_resume_never_creates_duplicate(self) -> None:
        plan = campaign_plan()
        action = action_plan(plan)
        ui = SimulatedAdsUI("acct-demo", "ui-7", 25_000_000, {"kind": "maximum_total_spend_micros", "amount_micros": 250_000_000}, save_mode="uncertain_after_create")
        receipt, workspace = self.run_action(plan, action, ui, operation="operation-uncertain")
        self.assertEqual("reconciled", receipt["outcome"])
        self.assertEqual(["campaign-demo"], list(ui.campaigns))
        again = execute_simulated(action, plan, ui, workspace, "operation-uncertain")
        self.assertEqual(receipt, again)
        self.assertEqual(1, len(ui.campaigns))
        events = [json.loads(line)["event"] for line in (workspace / "operations" / "operation-uncertain.jsonl").read_text().splitlines()]
        self.assertEqual(["started", "preflight_passed", "uncertain", "reconciled", "receipt"], events)
        changed_plan = campaign_plan(budget=26_000_000)
        with self.assertRaisesRegex(OperatingCoreError, "already bound"):
            execute_simulated(action, changed_plan, ui, workspace, "operation-uncertain")

    def test_checkpoint_success_without_current_reconciliation_fails_closed(self) -> None:
        plan = campaign_plan()
        action = action_plan(plan)
        ui = SimulatedAdsUI("acct-demo", "ui-7", 25_000_000, {"kind": "maximum_total_spend_micros", "amount_micros": 250_000_000})
        _, workspace = self.run_action(plan, action, ui, operation="operation-checkpoint")
        ui.campaigns.clear()
        with self.assertRaisesRegex(OperatingCoreError, "cannot be reconciled"):
            execute_simulated(action, plan, ui, workspace, "operation-checkpoint")

    def test_same_operation_id_across_two_accounts_allows_only_one_execution(self) -> None:
        with tempfile.TemporaryDirectory(prefix="operation-race-") as temp:
            workspace = Path(temp)
            plan_a, plan_b = campaign_plan(account_id="acct-a"), campaign_plan(account_id="acct-b")
            action_a, action_b = action_plan(plan_a), action_plan(plan_b)
            ui_a = SimulatedAdsUI("acct-a", "ui-7", 25_000_000, {"kind": "maximum_total_spend_micros", "amount_micros": 250_000_000})
            ui_b = SimulatedAdsUI("acct-b", "ui-7", 25_000_000, {"kind": "maximum_total_spend_micros", "amount_micros": 250_000_000})
            barrier = threading.Barrier(2)
            results: list[object] = []

            def run(plan: dict, action: dict, ui: SimulatedAdsUI) -> None:
                barrier.wait()
                try:
                    results.append(execute_simulated(action, plan, ui, workspace, "one-operation"))
                except OperatingCoreError as exc:
                    results.append(exc)

            threads = [threading.Thread(target=run, args=(plan_a, action_a, ui_a)), threading.Thread(target=run, args=(plan_b, action_b, ui_b))]
            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join()
            self.assertEqual(2, len(results))
            self.assertEqual(1, sum(isinstance(result, dict) and result.get("outcome") == "succeeded" for result in results))
            self.assertTrue(any(isinstance(result, OperatingCoreError) and ("already bound" in str(result) or "account lock already exists" in str(result)) for result in results), results)
            self.assertEqual(1, len(ui_a.campaigns) + len(ui_b.campaigns))

    def test_existing_account_lock_is_not_stolen_and_symlink_paths_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory(prefix="operating-core-") as temp:
            workspace = Path(temp)
            first = AccountLock(workspace, "acct-demo")
            first.acquire()
            try:
                with self.assertRaisesRegex(OperatingCoreError, "stale lock takeover"):
                    AccountLock(workspace, "acct-demo").acquire()
                target = workspace / "target"
                target.mkdir()
                (workspace / "linked").symlink_to(target, target_is_directory=True)
                with self.assertRaisesRegex(OperatingCoreError, "symlinks"):
                    safe_workspace_path(workspace, "linked/operation.jsonl")
            finally:
                first.release()

    def test_learning_candidate_requires_receipt_reviewer_anonymization_and_client_scope(self) -> None:
        candidate = {
            "schema_version": "v0.2", "record_type": "learning_candidate", "id": "learning-1", "created_at": CREATED,
            "client_id": "client-demo", "hypothesis": "Only this client saw the observed response.", "scope": "one completed simulated operation",
            "evidence": [{"receipt_id": "receipt-operation-1"}], "reviewer": {"name": "reviewer", "decision": "needs_more_evidence"},
            "anonymized": True, "generalization": "cross_client",
        }
        with self.assertRaisesRegex(OperatingCoreError, "pending private"):
            validate_record(candidate)
        candidate["generalization"] = "client_specific"
        validate_record(candidate)

    def test_learning_promotion_exports_only_reviewed_general_text(self) -> None:
        candidate, profile, receipt = reviewed_learning_fixture()
        with tempfile.TemporaryDirectory(prefix="private-") as private, tempfile.TemporaryDirectory(prefix="shared-") as shared:
            receipt_path = Path(private) / "receipts" / "private.json"
            receipt_path.parent.mkdir()
            receipt_path.write_text(json.dumps(receipt))
            receipt_hash = sha256_canonical(receipt)
            candidate["evidence"] = [{"receipt_path": "receipts/private.json", "receipt_sha256": receipt_hash}]
            bind_learning_candidate(candidate, receipt_hash)
            output = promote_learning_candidate(candidate, profile, Path(private), Path(shared), "promoted/learning.json")
            projection = json.loads(output.read_text())
            self.assertEqual("Review outcomes with the owner before reuse.", projection["reviewed_general_text"])
            self.assertNotIn("evidence", projection)
            self.assertNotIn("client_id", projection)
            self.assertNotIn("reviewer", projection)
            self.assertNotIn("receipt-zeta-48291", output.read_text())
            with self.assertRaisesRegex(OperatingCoreError, "overwrite"):
                promote_learning_candidate(candidate, profile, Path(private), Path(shared), "promoted/learning.json")

    def test_learning_promotion_rejects_resolved_receipt_identifiers(self) -> None:
        candidate, profile, receipt = reviewed_learning_fixture()
        candidate["promotion"]["reviewed_general_text"] = "cmp-zeta-48291 should not leave the private receipt."
        with tempfile.TemporaryDirectory(prefix="private-") as private, tempfile.TemporaryDirectory(prefix="shared-") as shared:
            receipt_path = Path(private) / "receipts" / "private.json"
            receipt_path.parent.mkdir()
            receipt_path.write_text(json.dumps(receipt))
            receipt_hash = sha256_canonical(receipt)
            candidate["evidence"] = [{"receipt_path": "receipts/private.json", "receipt_sha256": receipt_hash}]
            bind_learning_candidate(candidate, receipt_hash)
            with self.assertRaisesRegex(OperatingCoreError, "resolved private receipt identifier"):
                promote_learning_candidate(candidate, profile, Path(private), Path(shared), "promoted/leak.json")

    def test_learning_promotion_rejects_invalid_or_duplicate_supersession_hashes(self) -> None:
        candidate, profile, receipt = reviewed_learning_fixture()
        candidate["promotion"]["supersedes_reviewed_text_sha256"] = ["not-a-sha256"]
        with tempfile.TemporaryDirectory(prefix="private-") as private, tempfile.TemporaryDirectory(prefix="shared-") as shared:
            receipt_path = Path(private) / "receipts" / "private.json"
            receipt_path.parent.mkdir()
            receipt_path.write_text(json.dumps(receipt))
            receipt_hash = sha256_canonical(receipt)
            candidate["evidence"] = [{"receipt_path": "receipts/private.json", "receipt_sha256": receipt_hash}]
            bind_learning_candidate(candidate, receipt_hash)
            with self.assertRaisesRegex(OperatingCoreError, "supersedes_reviewed_text_sha256"):
                promote_learning_candidate(candidate, profile, Path(private), Path(shared), "promoted/invalid-hash.json")
            candidate["promotion"]["supersedes_reviewed_text_sha256"] = ["a" * 64, "a" * 64]
            bind_learning_candidate(candidate, receipt_hash)
            with self.assertRaisesRegex(OperatingCoreError, "supersedes_reviewed_text_sha256"):
                promote_learning_candidate(candidate, profile, Path(private), Path(shared), "promoted/duplicate-hash.json")

    def test_cli_help_is_available(self) -> None:
        result = subprocess.run([sys.executable, "scripts/operating_core.py", "--help"], cwd=REPO, text=True, capture_output=True, check=False)
        self.assertEqual(0, result.returncode)
        self.assertIn("simulate-execute", result.stdout)
        self.assertIn("controlled simulated Ads UI", result.stdout)


if __name__ == "__main__":
    raise SystemExit(unittest.main())
