#!/usr/bin/env python3
"""Analyze a sanitized, normalized ChatGPT Ads CSV export.

This tool intentionally accepts only the local normalized schema. It is not a
native-export adapter and does not make network or account calls.
"""
from __future__ import annotations

import argparse
import csv
import html
import json
import math
import os
import tempfile
import re
import sys
from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


FIELDS = (
    "currency",
    "timezone",
    "date_start",
    "date_end",
    "attribution_window",
    "conversion_definition",
    "revenue_basis",
    "granularity",
    "ad_id",
    "impressions",
    "clicks",
    "spend",
    "conversions",
    "revenue",
)
METADATA_FIELDS = FIELDS[:8]
COUNT_FIELDS = frozenset(("impressions", "clicks", "conversions"))
MEASUREMENT_FIELDS = FIELDS[9:]
CURRENCY_PATTERN = re.compile(r"^[A-Z]{3}$")
SENSITIVE_METADATA_PATTERN = re.compile(r"(?:api[_-]?key|secret|password|token|sk-[a-z0-9]|bearer\s|gh[pousr]_|github_pat_)", re.IGNORECASE)
PATH_METADATA_PATTERN = re.compile(r"(?:^~[\\/]|^/[A-Za-z0-9._-]|(?:^|[\\/])\.\.(?:[\\/]|$)|^[A-Za-z]:[\\/])")


class InputError(ValueError):
    """A safe validation error that deliberately excludes local file paths."""


@dataclass(frozen=True)
class ParsedRow:
    metadata: dict[str, str]
    ad_id: str
    measurements: dict[str, Decimal | None]


def _nonblank(value: str | None, field: str, row_number: int) -> str:
    if value is None or not value.strip():
        raise InputError(f"row {row_number}: {field} is required")
    return value.strip()


def _parse_measurement(value: str | None, field: str, row_number: int) -> Decimal | None:
    if value is None or not value.strip():
        return None
    try:
        parsed = Decimal(value.strip())
    except InvalidOperation as exc:
        raise InputError(f"row {row_number}: {field} must be numeric or blank") from exc
    if not parsed.is_finite() or parsed < 0:
        raise InputError(f"row {row_number}: {field} must be finite and non-negative")
    try:
        json_number = float(parsed)
    except (OverflowError, ValueError) as exc:
        raise InputError(f"row {row_number}: {field} must be representable as a finite JSON number") from exc
    if not math.isfinite(json_number) or (parsed != 0 and json_number == 0):
        raise InputError(f"row {row_number}: {field} must be representable as a finite JSON number")
    if field in COUNT_FIELDS and parsed != parsed.to_integral_value():
        raise InputError(f"row {row_number}: {field} must be a whole-number count")
    return parsed


def _validate_metadata(metadata: dict[str, str], row_number: int) -> None:
    if metadata["granularity"] != "ad":
        raise InputError(f"row {row_number}: granularity must be ad")
    if not CURRENCY_PATTERN.fullmatch(metadata["currency"]):
        raise InputError(f"row {row_number}: currency must be a three-letter uppercase code")
    for field, value in metadata.items():
        if (len(value) > 128 or any(ord(c) < 32 or ord(c) == 127 for c in value)
                or value.startswith(("./", ".\\", "file:"))
                or SENSITIVE_METADATA_PATTERN.search(value) or PATH_METADATA_PATTERN.search(value)):
            raise InputError(f"row {row_number}: {field} contains unsupported sensitive or path-like metadata")
    try:
        ZoneInfo(metadata["timezone"])
    except (ZoneInfoNotFoundError, ValueError) as exc:
        raise InputError(f"row {row_number}: timezone must be a recognized IANA timezone") from exc
    try:
        start = date.fromisoformat(metadata["date_start"])
        end = date.fromisoformat(metadata["date_end"])
    except ValueError as exc:
        raise InputError(f"row {row_number}: date_start and date_end must use YYYY-MM-DD") from exc
    if start > end:
        raise InputError(f"row {row_number}: date_start must not be after date_end")
    if start.isoformat() != metadata["date_start"] or end.isoformat() != metadata["date_end"]:
        raise InputError(f"row {row_number}: dates must use canonical YYYY-MM-DD")
    for field in ("attribution_window", "conversion_definition", "revenue_basis"):
        if "viewthrough" in re.sub(r"[^a-z0-9]", "", metadata[field].casefold()) or re.search(r"\bvta\b", metadata[field], re.I):
            raise InputError(f"row {row_number}: {field} may not include view-through outcomes")


def read_normalized_csv(input_file: Path) -> list[ParsedRow]:
    try:
        with input_file.open("r", encoding="utf-8-sig", newline="") as handle:
            return _read_normalized_stream(handle)
    except OSError as exc:
        raise InputError("input CSV could not be opened") from exc


def read_normalized_bytes(data: bytes) -> list[ParsedRow]:
    """Parse the exact immutable byte snapshot already hashed by an importer."""
    import io
    try:
        text = data.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise InputError("CSV must be UTF-8") from exc
    with io.StringIO(text, newline="") as handle:
        return _read_normalized_stream(handle)


def _read_normalized_stream(handle) -> list[ParsedRow]:
    reader = csv.DictReader(handle)
    headers = reader.fieldnames
    if headers is None:
        raise InputError("CSV must include a header row")
    if len(headers) != len(set(headers)):
        raise InputError("CSV header contains duplicate fields")
    actual = tuple(headers)
    missing = [field for field in FIELDS if field not in actual]
    unexpected = [field for field in actual if field not in FIELDS]
    if missing or unexpected or actual != FIELDS:
        parts = []
        if missing:
            parts.append("missing required headers: " + ", ".join(missing))
        if unexpected:
            parts.append(f"CSV contains {len(unexpected)} unexpected header field(s)")
        if not missing and not unexpected:
            parts.append("headers must use the documented order")
        raise InputError("; ".join(parts))

    rows: list[ParsedRow] = []
    seen_ad_ids: set[str] = set()
    reference_metadata: dict[str, str] | None = None
    for row_number, raw in enumerate(reader, start=2):
        if None in raw:
            raise InputError(f"row {row_number}: contains extra CSV values")
        metadata = {field: _nonblank(raw[field], field, row_number) for field in METADATA_FIELDS}
        _validate_metadata(metadata, row_number)
        if reference_metadata is None:
            reference_metadata = metadata
        elif metadata != reference_metadata:
            changed = [field for field in METADATA_FIELDS if metadata[field] != reference_metadata[field]]
            raise InputError(f"row {row_number}: metadata differs from the CSV window ({', '.join(changed)})")
        ad_id = _nonblank(raw["ad_id"], "ad_id", row_number)
        if ad_id in seen_ad_ids:
            raise InputError(f"row {row_number}: duplicate ad_id")
        seen_ad_ids.add(ad_id)
        rows.append(ParsedRow(metadata, ad_id, {
            field: _parse_measurement(raw[field], field, row_number)
            for field in MEASUREMENT_FIELDS
        }))
    if not rows:
        raise InputError("CSV must include at least one ad row")
    return rows


def _number(value: Decimal) -> int | float:
    try:
        as_float = float(value)
    except (OverflowError, ValueError) as exc:
        raise InputError("aggregate measurement must be representable as a finite JSON number") from exc
    if not math.isfinite(as_float) or (value != 0 and as_float == 0):
        raise InputError("aggregate measurement must be representable as a finite JSON number")
    if value == value.to_integral_value():
        return int(value)
    return as_float


def _aggregate_measurement(rows: list[ParsedRow], field: str) -> dict[str, Any]:
    missing_count = sum(row.measurements[field] is None for row in rows)
    if missing_count:
        return {
            "value": None,
            "reason": f"{field} is blank for {missing_count} ad row(s); aggregate is not measurable",
        }
    return {"value": _number(sum((row.measurements[field] for row in rows), Decimal("0"))), "reason": None}


def _ratio(numerator: dict[str, Any], denominator: dict[str, Any], name: str, *, multiplier: float = 1.0) -> dict[str, Any]:
    if numerator["value"] is None:
        return {"value": None, "reason": f"{name} is not measurable because {numerator['reason']}"}
    if denominator["value"] is None:
        return {"value": None, "reason": f"{name} is not measurable because {denominator['reason']}"}
    if denominator["value"] == 0:
        return {"value": None, "reason": f"{name} is not measurable because its denominator is zero"}
    try:
        value = (numerator["value"] / denominator["value"]) * multiplier
    except OverflowError:
        return {"value": None, "reason": f"{name} exceeds the finite JSON number range"}
    if not math.isfinite(value) or (numerator["value"] != 0 and value == 0):
        return {"value": None, "reason": f"{name} exceeds the finite JSON number range"}
    return {"value": value, "reason": None}


def analyze(rows: list[ParsedRow]) -> dict[str, Any]:
    metadata = rows[0].metadata
    totals = {field: _aggregate_measurement(rows, field) for field in MEASUREMENT_FIELDS}
    metrics = {
        "click_through_rate": _ratio(totals["clicks"], totals["impressions"], "click_through_rate"),
        "conversion_rate": _ratio(totals["conversions"], totals["clicks"], "conversion_rate"),
        "cost_per_click": _ratio(totals["spend"], totals["clicks"], "cost_per_click"),
        "cost_per_conversion": _ratio(totals["spend"], totals["conversions"], "cost_per_conversion"),
        "average_cpm": _ratio(totals["spend"], totals["impressions"], "average_cpm", multiplier=1000.0),
        "revenue_roas": {
            **_ratio(totals["revenue"], totals["spend"], "revenue_roas"),
            "basis": metadata["revenue_basis"],
        },
    }
    return {
        "status": "provisional" if any(item["value"] is None for item in [*totals.values(), *metrics.values()]) else "ok",
        "workflow": "normalized_csv_aggregate_analysis",
        "source_type": "local_normalized_schema_not_native_export",
        "metadata": metadata,
        "ad_count": len(rows),
        "totals": totals,
        "metrics": metrics,
        "limits": [
            "Blank measurements propagate as not measurable; they are not treated as zero.",
            "Rates are aggregate weighted calculations, not averages of ad-level rates.",
            "No view-through outcomes, incompatible attribution windows, or incompatible revenue bases are summed.",
            "Revenue ROAS is labeled with the supplied revenue_basis and is not assumed to be order-created revenue.",
            "The analyzer cannot detect overlapping native aggregate totals disguised as ad rows; map only non-overlapping ad rows before input.",
        ],
        "metric_units": {
            "click_through_rate": "ratio; multiply by 100 to display percent",
            "conversion_rate": "ratio; multiply by 100 to display percent",
            "cost_per_click": f"{metadata['currency']} per click",
            "cost_per_conversion": f"{metadata['currency']} per conversion",
            "average_cpm": f"{metadata['currency']} per 1,000 impressions",
            "revenue_roas": f"revenue / spend, basis: {metadata['revenue_basis']}",
        },
    }


def render_html(result: dict[str, Any]) -> str:
    """Render an escaped presentation of the same result returned as JSON."""
    def safe(value: Any) -> str:
        if value is None:
            return "not measurable"
        return html.escape(str(value), quote=True)

    def metric_row(name: str, metric: dict[str, Any]) -> str:
        reason = metric.get("reason")
        basis = metric.get("basis")
        detail = "" if reason is None else f" <small>{safe(reason)}</small>"
        unit = result.get("metric_units", {}).get(name)
        if unit: detail += f" <small>{safe(unit)}</small>"
        if basis is not None:
            detail += f" <small>basis: {safe(basis)}</small>"
        return f"<tr><th>{safe(name)}</th><td>{safe(metric['value'])}{detail}</td></tr>"

    metadata_rows = "".join(
        f"<tr><th>{safe(key)}</th><td>{safe(value)}</td></tr>"
        for key, value in result["metadata"].items()
    )
    total_rows = "".join(metric_row(name, total) for name, total in result["totals"].items())
    metric_rows = "".join(metric_row(name, metric) for name, metric in result["metrics"].items())
    limits = "".join(f"<li>{safe(limit)}</li>" for limit in result["limits"])
    return "<!doctype html><html><head><meta charset=\"utf-8\"><title>Normalized CSV analysis</title></head><body>" + (
        f"<h1>Normalized CSV aggregate analysis</h1><p>Status: {safe(result['status'])}</p>"
        f"<p>Ad count: {safe(result['ad_count'])}</p><h2>Metadata</h2><table>{metadata_rows}</table>"
        f"<h2>Totals</h2><table>{total_rows}</table><h2>Weighted metrics</h2><table>{metric_rows}</table>"
        f"<h2>Limits</h2><ul>{limits}</ul></body></html>"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Analyze a local normalized CSV aggregate export.")
    parser.add_argument("input", type=Path, help="normalized CSV input")
    parser.add_argument("--out", type=Path, required=True, help="JSON output path")
    parser.add_argument("--html", type=Path, help="optional escaped HTML output path")
    args = parser.parse_args(argv)
    staged = []
    created = []
    try:
        outputs = [args.out] + ([args.html] if args.html else [])
        if len({p.resolve() for p in [args.input, *outputs]}) != 1 + len(outputs):
            raise InputError("input and output destinations must be distinct")
        if any(p.exists() or p.is_symlink() for p in outputs):
            raise InputError("output destinations must be new files")
        result = analyze(read_normalized_csv(args.input))
        contents = [json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n"]
        if args.html:
            contents.append(render_html(result))
        for target, content in zip(outputs, contents):
            with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=target.parent, delete=False) as handle:
                staged.append(Path(handle.name))
                handle.write(content)
        # Atomic create without overwriting even if a destination appears after preflight.
        for temp, target in zip(staged, outputs):
            os.link(temp, target)
            created.append(target)
    except InputError as exc:
        print(f"analysis failed: {exc}", file=sys.stderr)
        return 2
    except (UnicodeError, csv.Error, ValueError):
        print("analysis failed: malformed CSV or invalid value", file=sys.stderr)
        return 2
    except OSError:
        for target in created:
            target.unlink(missing_ok=True)
        print("analysis failed: input or output could not be processed", file=sys.stderr)
        return 2
    finally:
        for temp in staged:
            temp.unlink(missing_ok=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
