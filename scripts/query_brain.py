#!/usr/bin/env python3
"""Bounded deterministic claim retrieval with evidence safety gates."""

from __future__ import annotations

import argparse
import json
import re
from datetime import date
from pathlib import Path
from typing import Any
try:
    from scripts.knowledge_core import maintenance_state
except ModuleNotFoundError:
    from knowledge_core import maintenance_state

from knowledge_core import KnowledgeCoreError, validate_registries


ROOT = Path(__file__).resolve().parents[1]
MAX_QUERY_CHARS = 2_000
MAX_TERMS = 200
RESOLVED_CONTRADICTION_STATUSES = {"resolved", "closed", "superseded"}
SAFE_SOURCE_TYPES = {
    "official", "primary", "regulator", "academic", "independent",
    "vendor", "practitioner", "supporting", "market", "news", "fixture",
}
UNSAFE_CLAIM_STATES = {"needs_review", "contested", "refuted", "superseded"}


def _terms(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9_]+", text.lower())[:MAX_TERMS])


def _freshness(source: dict[str, Any], as_of: str) -> tuple[str, list[dict[str, Any]]]:
    issues: list[dict[str, Any]] = []
    as_of_date = date.fromisoformat(as_of)
    source_type = source.get("source_type")
    if source_type not in SAFE_SOURCE_TYPES:
        issues.append({
            "code": "source_type_unknown" if source_type == "unknown" else "source_type_invalid",
            "detail": f"source type is {source_type!r}",
        })
    retrieved = source.get("retrieved")
    if retrieved in (None, "", "unknown"):
        issues.append({"code": "source_retrieval_unknown", "detail": "source retrieval date is unknown"})
    else:
        try:
            retrieved_date = date.fromisoformat(str(retrieved))
        except ValueError:
            issues.append({"code": "source_retrieval_invalid", "detail": "source retrieval date is invalid"})
        else:
            if retrieved_date > as_of_date:
                issues.append({"code": "source_retrieved_after_as_of", "detail": f"source was retrieved {retrieved}"})
    due = source.get("refresh_due")
    if due in (None, "", "unknown"):
        issues.append({"code": "source_refresh_unknown", "detail": "source refresh date is unknown"})
    else:
        try:
            due_date = date.fromisoformat(str(due))
        except ValueError:
            issues.append({"code": "source_refresh_invalid", "detail": "source refresh date is invalid"})
        else:
            if due_date < as_of_date:
                issues.append({"code": "source_stale", "detail": f"source refresh was due {due}"})
    if not issues:
        return "within_maintenance_window", []
    if all(issue["code"] == "source_stale" for issue in issues):
        return "stale", issues
    return "unsafe", issues


def _load_registry(path: Path, list_key: str, registry: str) -> tuple[dict[str, Any], dict[str, Any] | None]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {}, {"code": "registry_missing", "registry": registry}
    except (OSError, json.JSONDecodeError):
        return {}, {"code": "registry_invalid", "registry": registry}
    if not isinstance(value, dict) or not isinstance(value.get(list_key), list):
        return {}, {"code": "registry_invalid", "registry": registry}
    return value, None


def _active_conflicts(contradictions: list[Any]) -> tuple[set[str], set[str], dict[str, list[str]]]:
    source_ids: set[str] = set()
    claim_ids: set[str] = set()
    reasons: dict[str, list[str]] = {}
    for item in contradictions:
        if not isinstance(item, dict):
            continue
        status = str(item.get("status", "unresolved")).lower()
        if status in RESOLVED_CONTRADICTION_STATUSES or status.startswith("resolved_"):
            continue
        conflict_id = str(item.get("id", "unidentified-contradiction"))
        refs = item.get("evidence_refs", [])
        claims = item.get("claim_ids", [])
        if isinstance(refs, list):
            for source_id in refs:
                if isinstance(source_id, str):
                    source_ids.add(source_id)
                    reasons.setdefault(source_id, []).append(conflict_id)
        if isinstance(claims, list):
            claim_ids.update(value for value in claims if isinstance(value, str))
    return source_ids, claim_ids, reasons


def query(
    text: str,
    limit: int = 8,
    as_of: str | None = None,
    include_stale: bool = False,
    *,
    root: Path | None = None,
) -> dict[str, Any]:
    if not isinstance(text, str) or not text.strip():
        raise ValueError("query must be non-empty")
    if len(text) > MAX_QUERY_CHARS:
        raise ValueError(f"query must be at most {MAX_QUERY_CHARS} characters")
    if limit < 1 or limit > 50:
        raise ValueError("limit must be between 1 and 50")
    as_of = as_of or date.today().isoformat()
    date.fromisoformat(as_of)
    brain_root = root or ROOT
    maintenance = maintenance_state(brain_root)
    if maintenance['status'] != 'clean':
        return {'status': 'blocked', 'as_of': as_of, 'retrieval': 'bounded_lexical_not_semantic',
                'results': [], 'withheld_claims': [], 'withheld_stale_claims': [],
                'live_verification': False, 'reason': 'knowledge_maintenance_incomplete',
                'maintenance': maintenance}
    registry_paths = {
        "sources": brain_root / "references/source-ledger.json",
        "claims": brain_root / "references/claims.json",
        "contradictions": brain_root / "references/contradictions.json",
    }
    source_data, source_issue = _load_registry(registry_paths["sources"], "sources", "sources")
    claim_data, claim_issue = _load_registry(registry_paths["claims"], "claims", "claims")
    contradiction_data, contradiction_issue = _load_registry(
        registry_paths["contradictions"], "contradictions", "contradictions"
    )
    registry_issues = [issue for issue in (source_issue, claim_issue, contradiction_issue) if issue]
    if not registry_issues:
        try:
            validate_registries({
                "sources": source_data,
                "claims": claim_data,
                "contradictions": contradiction_data,
            })
        except (KnowledgeCoreError, KeyError, TypeError) as exc:
            registry_issues.append({
                "code": "registry_validation_failed",
                "registry": "knowledge_core",
                "detail": str(exc),
            })
    sources = {
        item["id"]: item
        for item in source_data.get("sources", [])
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }
    contradictions = contradiction_data.get("contradictions", [])
    contradiction_sources, contradiction_claims, conflict_reasons = _active_conflicts(
        contradictions if isinstance(contradictions, list) else []
    )
    words = _terms(text)
    candidates: list[dict[str, Any]] = []
    withheld: list[dict[str, Any]] = []
    claims = claim_data.get("claims", [])
    for claim in claims if isinstance(claims, list) else []:
        if not isinstance(claim, dict) or not isinstance(claim.get("id"), str):
            continue
        haystack = " ".join(str(claim.get(field, "")) for field in ("id", "claim", "recommendation", "lane"))
        score = len(words & _terms(haystack))
        if not score:
            continue
        reasons: list[dict[str, Any]] = []
        source_refs: list[dict[str, Any]] = []
        freshness_values: list[str] = []
        claim_source_ids = claim.get("source_ids", []) if isinstance(claim.get("source_ids"), list) else []
        for source_id in claim_source_ids:
            source = sources.get(source_id)
            if source is None:
                reasons.append({"code": "missing_source", "source_id": source_id})
                continue
            freshness, source_issues = _freshness(source, as_of)
            freshness_values.append(freshness)
            source_refs.append({
                "id": source_id,
                "url": source.get("url"),
                "retrieved": source.get("retrieved", "unknown"),
                "refresh_due": source.get("refresh_due", "unknown"),
                "source_type": source.get("source_type", "unknown"),
            })
            for issue in source_issues:
                reasons.append({**issue, "source_id": source_id})
            if source_id in contradiction_sources:
                reasons.append({
                    "code": "unresolved_contradiction",
                    "source_id": source_id,
                    "contradiction_ids": conflict_reasons.get(source_id, []),
                })
        if not claim_source_ids:
            reasons.append({"code": "missing_source_refs"})
        if claim["id"] in contradiction_claims:
            reasons.append({"code": "unresolved_contradiction", "claim_id": claim["id"]})
        claim_status = str(claim.get("status", "active")).lower()
        claim_support = str(claim.get("support", "")).lower()
        unsafe_state = next(
            (
                state for state in UNSAFE_CLAIM_STATES
                if claim_status == state or claim_status.startswith(state + "_")
                or claim_support == state or claim_support.startswith(state + "_")
            ),
            None,
        )
        if unsafe_state:
            reasons.append({
                "code": "claim_state_unsafe",
                "status": claim.get("status"),
                "support": claim.get("support"),
                "warnings": claim.get("warnings", []),
            })
        reasons.extend(registry_issues)
        only_stale = bool(reasons) and all(
            reason["code"] == "source_stale" for reason in reasons
        )
        result = {
            "score": score,
            **claim,
            "freshness": (
                "unsafe" if "unsafe" in freshness_values
                else "stale" if "stale" in freshness_values
                else "within_maintenance_window"
            ),
            "source_refs": source_refs,
            "sources": source_refs,
            "live_verification": False,
        }
        if reasons and not (include_stale and only_stale):
            withheld.append({"id": claim["id"], "score": score, "reasons": reasons})
        else:
            if reasons:
                result["warnings"] = list(claim.get("warnings", [])) + reasons
                result["historical_only"] = True
            candidates.append(result)
    candidates.sort(key=lambda item: (-item["score"], item["id"]))
    withheld.sort(key=lambda item: (-item["score"], item["id"]))
    results = candidates[:limit]
    stale_ids = [
        item["id"] for item in withheld
        if any(reason["code"] == "source_stale" for reason in item["reasons"])
    ]
    if results:
        status = "historical" if include_stale and any(item.get("historical_only") for item in results) else "ok"
    elif registry_issues:
        status = "blocked"
    elif withheld:
        status = "needs_refresh" if len(stale_ids) == len(withheld) else "blocked"
    else:
        status = "no_data"
    return {
        "status": status,
        "as_of": as_of,
        "retrieval": "bounded_lexical_not_semantic",
        "results": results,
        "withheld_claims": withheld,
        "withheld_stale_claims": stale_ids,
        "registry_issues": registry_issues,
        "live_verification": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("query")
    parser.add_argument("--limit", type=int, default=8)
    parser.add_argument("--as-of")
    parser.add_argument("--include-stale", action="store_true", help="include stale evidence as historical")
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    try:
        result = query(args.query, args.limit, args.as_of, args.include_stale, root=args.root.resolve())
    except ValueError as exc:
        parser.error(str(exc))
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
