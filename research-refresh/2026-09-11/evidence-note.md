# ChatGPT Ads official-source refresh, 2026-09-11

This refresh answers the v0.3.0 research questions with current public OpenAI sources. The external first-pass report was used only as an untrusted lead list. This note contains no contributor identity, private account identifier, or account-specific value. No Ads Manager account, campaign, Pixel, CAPI event, API key, report, export, feed, audience, or spending-limit configuration was observed or changed.

## Proposed additions

1. [Measure Results](https://help.openai.com/en/articles/20001214-launch-your-campaign-and-monitor-performance) lists `{campaign_id}`, `{ad_group_id}`, `{ad_id}`, and `{ad_account_id}` as configurable URL macros and gives the precedence order Ad URL, Ad, Ad Group, Campaign. [Conversion Measurement](https://help.openai.com/en/articles/20001409-conversion-measurement) separately describes `oppref` as the click reference OpenAI appends and the advertiser should preserve. The public pages reviewed do not list `oppref` as a configurable macro. A report that an account UI displayed `{oppref}` therefore remains an uncorroborated account observation.

2. [Product-feed setup](https://help.openai.com/en/articles/20001268-create-campaigns-from-product-feeds) and [Measure Results](https://help.openai.com/en/articles/20001214-launch-your-campaign-and-monitor-performance) define the Products tab as reporting backed by delivered activity, not a complete feed inventory. The ad-group product count is the readiness check, and reporting can lag delivery by up to seven hours.

3. [Account Setup](https://help.openai.com/en/articles/20001213) documents eligible business-account setup through ChatGPT Ads Manager. It also states that advertiser access follows the business or ad-account country selected during setup, not the ChatGPT login country, and that actions and workspace access can vary. This is documentation, not proof of access or setup state for any account.

4. [Measure Results](https://help.openai.com/en/articles/20001214-launch-your-campaign-and-monitor-performance) explicitly supports Google Tag Manager for the Pixel when the manager preserves correct loading and call order. The source recommends direct installation or appropriate server-side measurement if reliable loading cannot be maintained.

5. [Create Campaigns](https://help.openai.com/en/articles/20001210-create-campaigns-for-chatgpt-ads) documents U.S. state, DMA, and ZIP targeting plus broader cities and postal codes where available. It adds an explicit product-feed exception: new product-feed campaigns allow country-level geographic targeting and exclusions only, while existing campaigns can retain saved subnational settings but cannot add new ones. The [Location Targeting API guide](https://developers.openai.com/ads/location-targeting) documents country, region, and Market IDs, `geo_lookup`, and a downloadable catalog CSV. The reviewed API guide does not document postal-code IDs, so campaign type, Help surface, and API capability must stay separate.

6. The [Ad Account API](https://developers.openai.com/ads/api-reference/ad-account) documents shared date-range and daily limits only for postpaid invoice accounts and only with billing-management permission. These limits apply to billable ad spend, do not replace campaign budgets, and may not stop delivery immediately. Missing or null spend counters are unavailable, not zero.

7. [Ad Tools Terms](https://openai.com/policies/ad-tools-terms/) define optional AI Creative Tools and say campaign settings can allow review or automatic application. They also preserve advertiser responsibility and the ability to manage or disable applicable controls. The terms do not establish that text personalization defaults on in a particular account.

8. Reporting range, API bucket/window, click attribution setting, and conversion-time basis must remain separate. [Insights](https://developers.openai.com/ads/api-reference/insights) defines `time_ranges` as the report window and `time_granularity` as bucket size. [Conversion Setup](https://developers.openai.com/ads/api-reference/conversion-setup) separately defines `attribution_window_days` on an event setting. Public documentation retrieved on 2026-09-11 did not define reported 7/14/30-day UI column labels or a conversion-time column, so those semantics need raw account evidence or a native export before canonical promotion.

## Verified duplicate and nomenclature boundary

The current canonical `platform-finding-007` already covers manual max bids, Maximize results, and 0.1x to 10x custom-audience bid multipliers. [Maximize Results](https://help.openai.com/en/articles/20001425-maximize-results-bid-strategy) names the alternative `Manual: Max bid`; the [Ad Groups API](https://developers.openai.com/ads/api-reference/ad-groups) says an oCPC `max_bid_micros` value is a CPA bid even though the billing event is a click. The [Conversion-optimized Campaigns guide](https://help.openai.com/en/articles/20001412-conversion-optimized-campaigns), section 5 and its Bid Cap FAQ, explicitly documents `Bid Cap` for conversion campaigns. It is a conversion-oriented bid, not a conversion charge or guaranteed achieved CPA. The integration review corrected the initial two-page research gap; account-visible controls remain unverified. Minimum daily budgets are already `platform-finding-009`; this refresh does not duplicate them. Existing product-feed intake and audience-region claims also remain valid.

## Unresolved account-only observations

No public claim is proposed for geographic exclusions in the account UI, bulk-edit export, conversion-time columns, 7/14/30-day attribution comparison columns, default-on text personalization, EQS, identifier-coverage labels, AI-generated draft persistence, or the exact set of platform labels in a particular locale. These remain reported observations until sanitized raw screenshots, a native export, or an official definition is available. Labels such as EQS or coverage do not establish a metric definition.

The hash-bound proposal is generated from `integration-update.json`. It is review material only and does not modify canonical registries.
