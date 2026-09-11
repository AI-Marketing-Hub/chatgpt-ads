#!/usr/bin/env python3
"""Reproduce the bounded synthetic workflow acceptance checks."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from datetime import date, timedelta
from decimal import Decimal, getcontext
from pathlib import Path

from jsonschema import Draft202012Validator


getcontext().prec = 40
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
AS_OF = "2026-09-10"


def load(relative: str) -> dict:
    return json.loads((HERE / relative).read_text(encoding="utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def decimal_equal(actual: str, expected: Decimal, label: str) -> None:
    actual_decimal = Decimal(actual)
    rounded_expected = expected.quantize(Decimal(1).scaleb(actual_decimal.as_tuple().exponent))
    require(actual_decimal == rounded_expected, f"{label}: {actual} != {rounded_expected}")


def run_json(command: list[str]) -> dict:
    completed = subprocess.run(
        command,
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    require(completed.returncode == 0, f"command failed: {' '.join(command)}\n{completed.stderr}\n{completed.stdout}")
    return json.loads(completed.stdout)


def sha256(relative: str) -> str:
    return hashlib.sha256((HERE / relative).read_bytes()).hexdigest()


def strings(value: object):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for item in value.values():
            yield from strings(item)
    elif isinstance(value, list):
        for item in value:
            yield from strings(item)


def main() -> int:
    fixture = load("fixture.json")
    query_ledger = load("source-query-ledger.json")
    rubric = load("rubric.json")
    case_ledger = load("case-ledger.json")
    result_schema = json.loads((ROOT / "skills/chatgpt-ads/references/result.schema.json").read_text(encoding="utf-8"))
    canonical_claims = json.loads((ROOT / "references/claims.json").read_text(encoding="utf-8"))["claims"]
    claim_index = {item["id"]: item for item in canonical_claims}
    query_by_workflow = {item["workflow"]: item for item in query_ledger["queries"]}

    require(fixture["fixture_status"] == "deliberately_invented", "fixture must be explicitly invented")
    require(case_ledger["evidence_scope"] == "synthetic_advisory_only", "ledger scope drift")
    require(case_ledger["live_account_access"] is False, "live account access cannot be claimed")
    require(case_ledger["live_execution"] == "not_performed", "live execution cannot be claimed")
    require(case_ledger["suite_outcome"] == "pass", "case ledger is not finalized")
    require(all(item["acceptance_outcome"] == "pass" for item in case_ledger["cases"]), "case ledger contains a non-passing outcome")
    require(set(query_by_workflow) == set(rubric["workflow_criteria"]), "workflow coverage mismatch")

    cases: dict[str, dict] = {}
    result_validator = Draft202012Validator(result_schema)
    for entry in case_ledger["cases"]:
        case = load(entry["path"])
        workflow = entry["workflow"]
        require(case["case_id"] == entry["case_id"], f"case ID mismatch for {workflow}")
        require(case["workflow"] == workflow, f"workflow mismatch for {workflow}")
        require(case["evidence_class"] == "synthetic_advisory", f"evidence class mismatch for {workflow}")
        errors = sorted(result_validator.iter_errors(case["advisory_result"]), key=lambda error: list(error.path))
        require(not errors, f"{workflow} advisory result schema errors: {[error.message for error in errors]}")
        require(case["advisory_result"]["status"] == entry["expected_advisory_status"], f"unexpected advisory status for {workflow}")
        require(case["advisory_result"]["live_execution"] == "not_performed", f"live effect claimed by {workflow}")
        cases[workflow] = case

    used_source_ids: set[str] = set()
    for workflow, query_record in query_by_workflow.items():
        query_result = run_json([
            sys.executable,
            "scripts/query_brain.py",
            query_record["query"],
            "--limit",
            str(query_record["limit"]),
            "--as-of",
            query_ledger["as_of"],
        ])
        require(query_result["status"] == "ok", f"guarded query blocked for {workflow}")
        require(query_result["retrieval"] == query_ledger["retrieval_contract"], f"retrieval contract drift for {workflow}")
        require(query_result["live_verification"] is False, f"query improperly claims live verification for {workflow}")
        returned = {item["id"] for item in query_result["results"]}
        withheld = {item["id"] for item in query_result["withheld_claims"]}
        require(set(query_record["expected_claim_ids"]) <= returned, f"expected claim missing for {workflow}")
        require(set(query_record["expected_withheld_claim_ids"]) <= withheld, f"guarded withheld claim missing for {workflow}")
        expected_sources: set[str] = set()
        for claim_id in query_record["used_claim_ids"]:
            require(claim_id in returned, f"used claim was not returned for {workflow}: {claim_id}")
            expected_sources.update(claim_index[claim_id]["source_ids"])
        require(expected_sources == set(query_record["used_source_ids"]), f"source binding drift for {workflow}")
        used_source_ids.update(expected_sources)

        allowed_claim_refs = {f"claim:{claim_id}" for claim_id in query_record["used_claim_ids"]}
        case_claim_refs = {value for value in strings(cases[workflow]) if value.startswith("claim:")}
        require(case_claim_refs <= allowed_claim_refs, f"uncited or cross-workflow platform claim in {workflow}: {sorted(case_claim_refs - allowed_claim_refs)}")

    freshness = run_json([
        sys.executable,
        "skills/chatgpt-ads/scripts/check_sources.py",
        "--as-of",
        AS_OF,
        "--source-ids",
        *sorted(used_source_ids),
    ])
    require(freshness["status"] == "pass", "frozen-date source freshness failed")
    require(freshness["live_verified"] is False, "freshness check cannot claim live verification")

    readiness = cases["readiness"]
    readiness_codes = {item["code"] for item in readiness["advisory_result"]["blockers"]}
    require(
        readiness_codes == {"eligible_account_unobserved", "identity_role_billing_unobserved", "destination_unobserved", "measurement_not_deployed"},
        "readiness compound blockers changed",
    )
    require(all(value is None for value in fixture["account_evidence"].values()), "fixture account evidence must remain absent")

    economics = fixture["economics"]
    revenue = Decimal(economics["unit_revenue"])
    contribution = (
        revenue
        - Decimal(economics["cost_of_goods"])
        - Decimal(economics["fulfillment_per_order"])
        - revenue * Decimal(economics["payment_fee_rate"])
        - revenue * Decimal(economics["returns_allowance_rate"])
    )
    plan = cases["plan"]["produced_output"]
    decimal_equal(plan["economics"]["contribution_before_advertising"], contribution, "contribution")
    decimal_equal(plan["economics"]["break_even_cpa"], contribution, "break-even CPA")
    decimal_equal(plan["economics"]["break_even_revenue_roas"], revenue / contribution, "break-even ROAS")
    decimal_equal(plan["economics"]["target_cpa_revenue_roas"], revenue / Decimal(economics["owner_selected_target_cpa"]), "target CPA ROAS")
    require(Decimal(plan["budget_scenario"]["maximum_spend"]) <= Decimal(economics["planning_spend_ceiling"]), "budget exceeds fixture ceiling")
    require(all(plan["proposed_structure"][key] is None for key in ["platform_objective", "bid_mode", "targeting", "locations", "platforms"]), "unobserved platform field was invented")
    for row in plan["returns_rate_sensitivity"]:
        rate = Decimal(row["returns_allowance_rate"])
        value = revenue - Decimal(economics["cost_of_goods"]) - Decimal(economics["fulfillment_per_order"]) - revenue * Decimal(economics["payment_fee_rate"]) - revenue * rate
        decimal_equal(row["contribution_before_advertising"], value, f"sensitivity contribution {rate}")
        decimal_equal(row["break_even_revenue_roas"], revenue / value, f"sensitivity ROAS {rate}")

    approved_claims = {item["id"] for item in fixture["approved_claims"]}
    creative = cases["creative"]["produced_output"]
    require(len(creative["copy_variants"]) == 2, "creative case must contain two bounded variants")
    require(len({item["hypothesis"] for item in creative["copy_variants"]}) == 2, "creative hypotheses are not distinct")
    for variant in creative["copy_variants"]:
        require(set(variant["claim_ids"]) <= approved_claims, f"unsupported creative claim in {variant['variant_id']}")
        require(variant["destination"].endswith(".invalid/products/desk-mat"), "fixture destination safety drift")
        require(variant["asset"]["rights"] is None, "asset rights were invented")
    require(creative["platform_and_destination_review"]["enforced_text_or_asset_maxima"] is None, "format maximum was invented")
    require(creative["review_disposition"] == "blocked_from_export_or_publication", "creative should remain blocked")

    experiment = cases["experiment"]["produced_output"]
    require(experiment["design_type"] == "pre_registered_feasibility_pilot_not_powered_efficacy_test", "experiment design drift")
    require(experiment["assignment"]["method"] is None and experiment["assignment"]["unit"] is None, "assignment capability was invented")
    require(experiment["sample_and_power"]["power_analysis_performed"] is False, "spurious power analysis")
    require(experiment["sample_and_power"]["required_sample"] is None, "spurious sample requirement")
    require(experiment["fixed_feasibility_window"]["efficacy_stopping_rule"].startswith("none"), "pilot can improperly make efficacy decision")

    monitor_input = fixture["synthetic_monitor_input"]
    monitor = cases["monitor"]["produced_output"]
    closed = [row for row in monitor_input["rows"] if row["state"] == "closed"]
    missing = [row for row in monitor_input["rows"] if row["state"] == "missing"]
    stale_incomplete = [row for row in monitor_input["rows"] if row["state"].startswith("stale_incomplete_")]
    require(len(missing) == 1 and missing[0]["spend"] is None, "missing day must stay null")
    require(len(stale_incomplete) == 1, "expected one stale incomplete day")
    observed_closed = sum(Decimal(row["spend"]) for row in closed)
    planned_closed = Decimal(monitor_input["planned_daily_spend"]) * len(closed)
    decimal_equal(monitor["pacing"]["observed_spend_comparable_days"], observed_closed, "closed-day observed spend")
    decimal_equal(monitor["pacing"]["planned_spend_comparable_days"], planned_closed, "closed-day planned spend")
    decimal_equal(monitor["pacing"]["comparable_pacing_ratio"], observed_closed / planned_closed, "closed-day pacing ratio")
    completeness = monitor["data_freshness_and_completeness"]
    expected_mature = completeness["expected_mature_days"]
    decimal_equal(completeness["complete_day_ratio"], Decimal(len(closed)) / Decimal(expected_mature), "complete-day coverage")
    lag_hours = fixture["owner_monitor_rules"]["report_lag_hours_before_pacing_decision"]
    maturity_days = 1 + (lag_hours + 23) // 24
    incomplete_date = date.fromisoformat(stale_incomplete[0]["date"])
    lag_maturity_date = incomplete_date + timedelta(days=maturity_days)
    case_as_of = date.fromisoformat(fixture["as_of"])
    require(case_as_of >= lag_maturity_date, "incomplete row has not passed its lag maturity date")
    assessment = completeness["stale_incomplete_assessment"]
    require(assessment["lag_maturity_date"] == lag_maturity_date.isoformat(), "monitor lag maturity date mismatch")
    require(assessment["case_as_of"] == case_as_of.isoformat(), "monitor case date mismatch")
    require(assessment["classification"] == "stale_incomplete_closed_period", "stale incomplete classification missing")
    require(assessment["excluded_from_pacing"] is True, "stale incomplete day must be excluded")
    require("partial_day_ratio" not in monitor["pacing"], "stale incomplete row must not receive a pacing ratio")
    require(monitor["pacing"]["whole_window_signal"] is None, "whole-window conclusion must stay null")
    require(monitor["scheduling"] == "disabled", "monitor scheduling was enabled")

    owned_files = [
        "README.md", "fixture.json", "source-query-ledger.json", "rubric.json", "case-ledger.json",
        "cases/readiness.json", "cases/plan.json", "cases/creative.json", "cases/experiment.json", "cases/monitor.json", "verify.py",
    ]
    require(all("\u2014" not in (HERE / path).read_text(encoding="utf-8") for path in owned_files), "em dash found in acceptance files")
    require(fixture["business"]["offer"]["destination"].startswith("https://mossline.example.invalid/"), "fixture URL is not reserved")

    output = {
        "suite_id": case_ledger["suite_id"],
        "status": "pass",
        "as_of": AS_OF,
        "evidence_scope": "synthetic_advisory_only",
        "case_outcomes": {workflow: "pass" for workflow in sorted(cases)},
        "advisory_statuses": {workflow: cases[workflow]["advisory_result"]["status"] for workflow in sorted(cases)},
        "checks": {
            "schema_and_case_contracts": "pass",
            "guarded_retrieval_and_withholding": "pass",
            "frozen_date_source_freshness": "pass",
            "readiness_failure_behavior": "pass",
            "planning_economics_and_null_controls": "pass",
            "creative_claim_id_allowlist": "pass",
            "experiment_feasibility_boundary": "pass",
            "monitor_temporal_completeness_and_arithmetic": "pass",
            "scope_and_external_effect_safety": "pass"
        },
        "input_sha256": {path: sha256(path) for path in owned_files if path != "case-ledger.json"},
        "live_account_access": False,
        "live_execution": "not_performed",
        "network_writes": "not_performed",
        "paid_generation": "not_performed",
        "limitations": [
            "Historical source freshness is checked only for the frozen 2026-09-10 case date.",
            "No native account, destination, tracking, delivery, experiment, or scheduled monitor was tested.",
            "A passing suite validates synthetic workflow behavior, not advertiser or platform readiness."
        ]
    }
    print(json.dumps(output, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AssertionError, json.JSONDecodeError) as error:
        print(json.dumps({"status": "fail", "error": str(error)}, indent=2))
        raise SystemExit(1)
