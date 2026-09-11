# Analyze sanitized aggregate data

## Procedure

Use the normalized CSV contract below. Require explicit mapping from any native export and inspect granularity, selected dates and totals before analysis. Never add campaign totals to ad rows or cumulative exports to daily values. Explain conversion lag and small samples before diagnosing a trend. Report null metrics as not measurable, never zero. Investigate tracking, policy and landing-page failures before attributing poor results to creative or bids. No fixed pause or scale thresholds are built into this pack.

## Deliverable

Canonical JSON and optional escaped HTML from the same result; prioritized hypotheses with evidence needed to refute each. Account performance cannot be inferred from synthetic fixtures.

Read the matching current findings in `capabilities.md` and the source registry `sources.json`. Policy, product and measurement facts belong to that registry; this workflow is operator guidance.
# Normalized CSV contract

`scripts/analyze.py` accepts a local normalized aggregate CSV only. It does
not detect or ingest native ChatGPT Ads exports. Map an authorized export into
this schema outside the distributable pack, and retain the mapping and source
window for review.

The header row must be exactly, in this order:

```text
currency,timezone,date_start,date_end,attribution_window,conversion_definition,revenue_basis,granularity,ad_id,impressions,clicks,spend,conversions,revenue
```

- Every row is one ad (`granularity=ad`) and `ad_id` must be unique.
- `currency`, `timezone`, `date_start`, `date_end`, `attribution_window`,
  `conversion_definition`, `revenue_basis`, and `granularity` are mandatory
  and must be identical across the file. Dates are ISO dates and currency is a
  three-letter uppercase code.
- `impressions`, `clicks`, and `conversions` are non-negative whole-number
  counts. `spend` and `revenue` are non-negative finite numbers. A blank
  measurement means missing, not zero.
- Totals become null when any contributing measurement is blank. Derived
  rates use aggregate numerators and denominators, so they are weighted rather
  than averages of ad-level percentages. `click_through_rate` and
  `conversion_rate` are ratios, not percentage-formatted values, so multiply
  them by 100 only when displaying a percent. A zero denominator or a result
  beyond the finite JSON numeric range produces null and an explanatory reason.
- Revenue is aggregated only within the one required `revenue_basis` and
  revenue ROAS is emitted with that basis. It must not be called Order Created
  ROAS unless the supplied basis is actually `Order created`.
- The analyzer rejects view-through-labelled attribution, conversion, or
  revenue fields. It also rejects mixed attribution windows, conversion
  definitions, currencies, or revenue bases in a single file.
- It cannot identify a native campaign or account total that has been relabelled
  as an ad row. Map only one non-overlapping ad-level row per `ad_id`; do not
  mix native totals, cumulative rows, or rollups into this local input.
- Input metadata is treated as local, potentially sensitive account data. The
  analyzer rejects obvious credential-like and path-like metadata and does not
  echo unexpected headers or unsafe metadata in validation errors, but this is
  error-output hygiene, not a guarantee that a supplied file contains no secret.

Usage:

```bash
python skills/chatgpt-ads/scripts/analyze.py skills/chatgpt-ads/examples/normalized-demo.csv --out analysis.json --html analysis.html
```

## Validation and output safety

Output paths must be distinct from input and from one another, and must not exist. Use fresh destinations for each run. Outputs are staged and created atomically per file without overwriting. A failure creating the second output removes the first output created by that run.

`normalized-input.schema.json` validates the JSON array form of normalized rows after numbers and blanks become numeric values and null. Python additionally enforces duplicate IDs and same-window metadata. Labels cannot prove attribution semantics: the operator must verify their mapping. Common view-through spellings and VTA labels are rejected; relabeling such outcomes does not make them valid input.

`analysis-result.schema.json` validates the analyzer result, separately from the advisory workflow schema. Missing or undefined derived metrics produce provisional status. Extremely small nonzero input values that would silently become zero are rejected.
