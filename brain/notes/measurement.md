# Measurement and attribution

## Interpretation

Business events, received events, attributed conversions and incremental conversions are different sets. Browser/server deduplication requires an identity for the same business event, not merely similar timestamps. Consent and event minimization must be evaluated before sending data. Supplemental view-through reporting must not be silently added to a click-attributed optimization metric.

This interpretation is methodological guidance, not an additional assertion about current platform availability.

## Current evidence

Resolve these claim IDs through `scripts/query_brain.py` and inspect their linked source and conflict records. Canonical claim wording lives in `references/claims.json`; do not maintain a second editable copy here.

- `measurement-pixel-capi`
- `measurement-attribution-and-matching`
- `measurement-vta-definition`
- `measurement-events-and-values`
- `measurement-partner-coverage`
- `measurement-optimization-objectives`

- [Conversions API](https://developers.openai.com/ads/conversions-api) (`measurement-openai-capi-20260910`)
- [Conversion Measurement](https://help.openai.com/en/articles/20001409-conversion-measurement) (`measurement-openai-conversion-20260910`)
- [Conversion Setup](https://developers.openai.com/ads/api-reference/conversion-setup) (`measurement-openai-conversion-setup-api-20260910`)
- [Supported Events](https://developers.openai.com/ads/supported-events) (`measurement-openai-events-20260910`)
- [Insights API](https://developers.openai.com/ads/api-reference/insights) (`measurement-openai-insights-api-20260910`)
- [Measure Results](https://help.openai.com/en/articles/20001214-measure-results) (`measurement-openai-measure-results-20260910`)
- [Set up Mobile Measurement Partner Integrations](https://help.openai.com/en/articles/20001372-set-up-mobile-measurement-partner-integrations) (`measurement-openai-mobile-partners-20260910`)
- [Conversion-optimized Campaigns](https://help.openai.com/en/articles/20001412-conversion-optimized-campaigns) (`measurement-openai-ocpm-20260910`)
- [Set up Measurement Partner Integrations](https://help.openai.com/en/articles/20001416-set-up-measurement-partner-integrations) (`measurement-openai-partners-20260910`)
- [Measurement Pixel](https://developers.openai.com/ads/measurement-pixel) (`measurement-openai-pixel-20260910`)

Additional reviewed claim: `refresh-vta-scope-20260910`.

- `refresh-pixel-gtm-boundary-20260911`
- `refresh-report-window-semantics-20260911`

## Procedure

[chatgpt-ads-measurement](../../skills/chatgpt-ads-measurement/SKILL.md). [Coverage and limits](../../references/coverage.json).
