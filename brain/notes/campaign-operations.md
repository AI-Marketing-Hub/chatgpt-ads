# Campaign operations

## Interpretation

A saved object, an approved ad and a delivering campaign are distinct states. An uncertain save is an unresolved external effect, not a failed operation safe to repeat. Reconciliation uses object identity and current state. Pausing limits future delivery but cannot undo incurred charges.

This interpretation is methodological guidance, not an additional assertion about current platform availability.

## Current evidence

Resolve these claim IDs through `scripts/query_brain.py` and inspect their linked source and conflict records. Canonical claim wording lives in `references/claims.json`; do not maintain a second editable copy here.

- `platform-finding-017`
- `platform-finding-018`
- `platform-finding-008`

- [Overview - Ads](https://developers.openai.com/ads/api-overview) (`platform-advertiser-api-overview`)
- [Ad Groups - Ads](https://developers.openai.com/ads/api-reference/ad-groups) (`platform-api-ad-groups`)
- [Ads - OpenAI Developers](https://developers.openai.com/ads/api-reference/ads) (`platform-api-ads`)
- [Campaigns - Ads](https://developers.openai.com/ads/api-reference/campaigns) (`platform-api-campaigns`)
- [Insights - Ads](https://developers.openai.com/ads/api-reference/insights) (`platform-api-insights`)
- [Budget Pacing](https://help.openai.com/en/articles/20001515-budget-pacing) (`platform-budget-pacing`)
- [Create Campaigns for ChatGPT Ads](https://help.openai.com/en/articles/20001210-create-campaigns-for-chatgpt-ads) (`platform-campaigns`)
- [Daily Budgets](https://help.openai.com/en/articles/20001413-daily-budgets) (`platform-daily-budgets`)
- [Edit Campaigns](https://help.openai.com/en/articles/20001215-edit-campaigns) (`platform-edit`)
- [Launch Campaigns](https://help.openai.com/en/articles/20001209-launch-campaigns) (`platform-launch`)
- [Ads Manager Beta Overview](https://help.openai.com/en/articles/20001206-ads-manager-beta-overview) (`platform-manager-overview`)

- `refresh-ai-creative-controls-20260911`
- `refresh-account-spend-controls-20260911`

## Procedure

[chatgpt-ads-operate](../../skills/chatgpt-ads-operate/SKILL.md). [Coverage and limits](../../references/coverage.json).
