# Analytics and reporting

## Interpretation

Column names do not establish meaning. Entity grain, event versus report date, currency units, timezone, conversion definition and attribution window determine comparability. Aggregate totals and child rows overlap. Sum compatible numerators and denominators before calculating rates; do not average row-level ratios. Missing is not zero, and attributed revenue is not incremental revenue.

This interpretation is methodological guidance, not an additional assertion about current platform availability.

## Current evidence

Resolve these claim IDs through `scripts/query_brain.py` and inspect their linked source and conflict records. Canonical claim wording lives in `references/claims.json`; do not maintain a second editable copy here.

- `platform-finding-020`
- `measurement-reporting-metrics`
- `measurement-exports-api`

- [Insights API](https://developers.openai.com/ads/api-reference/insights) (`measurement-openai-insights-api-20260910`)
- [Measure Results](https://help.openai.com/en/articles/20001214-measure-results) (`measurement-openai-measure-results-20260910`)
- [Insights - Ads](https://developers.openai.com/ads/api-reference/insights) (`platform-api-insights`)
- [Measure Results](https://help.openai.com/en/articles/20001214-measure-results) (`platform-results`)

Additional reviewed claim: `refresh-native-export-gap-20260910`.

- `refresh-report-window-semantics-20260911`
- `refresh-products-reporting-semantics-20260911`

## Procedure

[chatgpt-ads-analyze](../../skills/chatgpt-ads-analyze/SKILL.md). [Coverage and limits](../../references/coverage.json).
