from __future__ import annotations

import csv
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[3]
SCRIPT = REPO / "skills" / "chatgpt-ads" / "scripts" / "analyze.py"
SPEC = importlib.util.spec_from_file_location("chatgpt_ads_analyze", SCRIPT)
assert SPEC and SPEC.loader
analyze = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = analyze
SPEC.loader.exec_module(analyze)

HEADERS = list(analyze.FIELDS)
BASE = {
    "currency": "USD", "timezone": "America/New_York", "date_start": "2026-09-01",
    "date_end": "2026-09-07", "attribution_window": "7-day click",
    "conversion_definition": "Purchase", "revenue_basis": "Order created",
    "granularity": "ad",
}


def row(ad_id: str, **values: str) -> dict[str, str]:
    return {
        **BASE, "ad_id": ad_id, "impressions": "100", "clicks": "10",
        "spend": "20.5", "conversions": "2", "revenue": "80", **values,
    }


def write_csv(path: Path, rows: list[dict[str, str]], headers: list[str] = HEADERS) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


class AnalyzeTests(unittest.TestCase):
    def expect_error(self, rows: list[dict[str, str]], phrase: str, headers: list[str] = HEADERS) -> str:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "input.csv"
            write_csv(path, rows, headers)
            with self.assertRaises(analyze.InputError) as raised:
                analyze.read_normalized_csv(path)
            self.assertIn(phrase, str(raised.exception))
            return str(raised.exception)

    def test_cli_valid_aggregate_and_html(self) -> None:
        rows = [
            row("a", impressions="100", clicks="10", spend="20", conversions="2", revenue="100"),
            row("b", impressions="300", clicks="30", spend="90", conversions="3", revenue="180"),
        ]
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "analysis space Ω"
            root.mkdir()
            source, output, page = root / "input.csv", root / "output.json", root / "output.html"
            write_csv(source, rows)
            process = subprocess.run(
                [sys.executable, str(SCRIPT), str(source), "--out", str(output), "--html", str(page)],
                text=True, capture_output=True, check=False,
            )
            self.assertEqual(process.returncode, 0, process.stderr)
            result = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(result["status"], "ok")
            self.assertEqual(result["totals"]["impressions"]["value"], 400)
            self.assertEqual(result["totals"]["spend"]["value"], 110)
            self.assertEqual(result["metrics"]["click_through_rate"]["value"], 0.1)
            self.assertEqual(result["metrics"]["conversion_rate"]["value"], 0.125)
            self.assertEqual(result["metrics"]["average_cpm"]["value"], 275)
            self.assertEqual(result["metrics"]["revenue_roas"]["value"], 280 / 110)
            self.assertEqual(result["metrics"]["revenue_roas"]["basis"], "Order created")
            self.assertEqual(result["metric_units"]["conversion_rate"], "ratio; multiply by 100 to display percent")
            self.assertNotIn("<script>", page.read_text(encoding="utf-8"))

    def test_missing_values_propagate_and_zero_denominator_is_null(self) -> None:
        missing = analyze.analyze([analyze.ParsedRow(BASE, "a", {
            "impressions": None, "clicks": analyze.Decimal("0"), "spend": analyze.Decimal("0"),
            "conversions": analyze.Decimal("0"), "revenue": analyze.Decimal("0"),
        })])
        self.assertEqual(missing["status"], "provisional")
        self.assertIsNone(missing["totals"]["impressions"]["value"])
        self.assertIsNone(missing["metrics"]["click_through_rate"]["value"])
        zero = analyze.analyze([analyze.ParsedRow(BASE, "a", {
            field: analyze.Decimal("0") for field in analyze.MEASUREMENT_FIELDS
        })])
        self.assertIsNone(zero["metrics"]["click_through_rate"]["value"])
        self.assertIn("denominator is zero", zero["metrics"]["click_through_rate"]["reason"])

    def test_rejects_schema_and_measurement_violations(self) -> None:
        self.expect_error([row("a"), row("a")], "duplicate ad_id")
        self.expect_error([row("a"), row("b", date_end="2026-09-08")], "metadata differs")
        self.expect_error([row("a"), row("b", currency="EUR")], "metadata differs")
        self.expect_error([row("a", clicks="1.5")], "whole-number count")
        self.expect_error([row("a", spend="-1")], "finite and non-negative")
        self.expect_error([row("a", revenue="NaN")], "finite and non-negative")
        self.expect_error([row("a", revenue="1e999999")], "representable as a finite JSON number")
        self.expect_error([row("a", attribution_window="1-day click and view-through")], "may not include view-through")
        error = self.expect_error([row("a")], "unexpected header", HEADERS + ["api_key=not-a-real-key"])
        self.assertNotIn("api_key=not-a-real-key", error)
        duplicate_headers = HEADERS.copy()
        duplicate_headers[-1] = "clicks"
        self.expect_error([row("a")], "duplicate fields", duplicate_headers)

    def test_escapes_markup_and_blocks_sensitive_or_path_metadata(self) -> None:
        unsafe = analyze.analyze([analyze.ParsedRow(
            {**BASE, "conversion_definition": "<script>alert(1)</script>"}, "a",
            {field: analyze.Decimal("1") for field in analyze.MEASUREMENT_FIELDS},
        )])
        rendered = analyze.render_html(unsafe)
        self.assertNotIn("<script>", rendered)
        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", rendered)
        error = self.expect_error([row("a", timezone=("/" + "/".join(["var", "home", "fixture-user", "Desktop", "Keys"])))], "sensitive or path-like")
        self.assertNotIn(("/" + "/".join(["var", "home", "fixture-user", "Desktop", "Keys"])), error)
        error = self.expect_error([row("a", conversion_definition="api_key=not-a-real-key")], "sensitive or path-like")
        self.assertNotIn("not-a-real-key", error)

    def test_revenue_basis_and_native_total_limit(self) -> None:
        error = self.expect_error([row("a", revenue_basis="View-through revenue")], "may not include view-through")
        self.assertIn("revenue_basis", error)
        result = analyze.analyze([analyze.ParsedRow(BASE, "campaign-total", {
            field: analyze.Decimal("1") for field in analyze.MEASUREMENT_FIELDS
        })])
        self.assertIn("cannot detect overlapping native aggregate totals", " ".join(result["limits"]))

    def test_ratio_overflow_becomes_null_with_reason(self) -> None:
        result = analyze.analyze([analyze.ParsedRow(BASE, "a", {
            "impressions": analyze.Decimal("1e-308"), "clicks": analyze.Decimal("1e308"),
            "spend": analyze.Decimal("1e308"), "conversions": analyze.Decimal("1"),
            "revenue": analyze.Decimal("1"),
        })])
        self.assertIsNone(result["metrics"]["click_through_rate"]["value"])
        self.assertIn("finite JSON number range", result["metrics"]["click_through_rate"]["reason"])

    def test_underflow_view_aliases_and_zero_status(self):
        self.expect_error([row("a", spend="1e-999")], "finite JSON number")
        for label in ["7-day view through", "viewthrough", "VTA (1d)"]:
            self.expect_error([row("a", attribution_window=label)], "view-through")
        zero = analyze.analyze([analyze.ParsedRow(BASE, "a", {
            field: analyze.Decimal(0) for field in analyze.MEASUREMENT_FIELDS
        })])
        self.assertEqual(zero["status"], "provisional")

    def test_cli_output_collisions_preserve_input(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); source = root / "input.csv"
            write_csv(source, [row("a")]); original = source.read_bytes()
            for args in [["--out", str(source)],
                         ["--out", str(root/"same"), "--html", str(root/"same")]]:
                proc = subprocess.run([sys.executable,str(SCRIPT),str(source),*args],capture_output=True,text=True)
                self.assertEqual(proc.returncode,2)
                self.assertEqual(source.read_bytes(),original)
            alias = root / "alias"
            if os.name == "nt":
                # NTFS hard links exercise alias preservation without requiring
                # Developer Mode. This is not a reparse-point safety test.
                os.link(source, alias)
            else:
                alias.symlink_to(source)
            proc = subprocess.run([sys.executable,str(SCRIPT),str(source),"--out",str(alias)],capture_output=True,text=True)
            self.assertEqual(proc.returncode,2);self.assertEqual(source.read_bytes(),original)
            existing = root/"old.json";existing.write_text("keep")
            proc = subprocess.run([sys.executable,str(SCRIPT),str(source),"--out",str(existing)],capture_output=True,text=True)
            self.assertEqual(proc.returncode,2);self.assertEqual(existing.read_text(),"keep")

    def test_cli_malformed_bytes_cells_and_timezone_are_safe(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);source=root/"input.csv";output=root/"output.json"
            cases=[b"\xff", (",".join(HEADERS)+"\n"+"x"*140000).encode()]
            for content in cases:
                source.write_bytes(content)
                proc=subprocess.run([sys.executable,str(SCRIPT),str(source),"--out",str(output)],capture_output=True,text=True)
                self.assertEqual(proc.returncode,2);self.assertNotIn("Traceback",proc.stderr)
                self.assertNotIn(str(root),proc.stderr);self.assertFalse(output.exists())
            write_csv(source,[row("a",timezone="UTC\x00")])
            proc=subprocess.run([sys.executable,str(SCRIPT),str(source),"--out",str(output)],capture_output=True,text=True)
            self.assertEqual(proc.returncode,2);self.assertNotIn("Traceback",proc.stderr)

    def test_normalized_json_schema_validates_real_rows(self):
        from jsonschema import Draft202012Validator, FormatChecker
        schema=json.loads((REPO/"skills/chatgpt-ads/references/normalized-input.schema.json").read_text())
        data=row("a")
        for field in analyze.MEASUREMENT_FIELDS:data[field]=float(data[field])
        validator=Draft202012Validator(schema,format_checker=FormatChecker())
        self.assertEqual(list(validator.iter_errors([data])),[])
        data["spend"]=-1
        self.assertTrue(list(validator.iter_errors([data])))

    def test_common_sensitive_metadata_forms(self):
        for value in ["Bearer " + "sample", "ghp_" + "sample", "./Desktop/Keys/sample", "file:" + "///example", "name\x00value"]:
            self.expect_error([row("a",conversion_definition=value)],"sensitive or path-like")


if __name__ == "__main__":
    unittest.main(verbosity=2)
