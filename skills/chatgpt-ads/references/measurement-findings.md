# Measurement evidence

Generated from canonical registries. Do not edit this projection. Dated documentation is not account verification. Run guarded retrieval before using a current claim.

## measurement-reporting-metrics

Ads Manager reports impressions, clicks, spend, CTR, average CPC, average CPM, and attributed conversions at campaign, ad-group, and ad level. `order_created` events alone feed Order Created Sales and Order Created ROAS. CSV supports cumulative and daily exports; charts are limited to impressions, clicks, and spend. The aggregate Conversions column combines configured events. Add event-specific columns before exporting to avoid treating unlike actions as one business outcome. Ads Manager may take 24 to 48 hours to reflect attributed conversions.

Evidence state: evidence_based. Availability: documented_not_account_verified.

Interpretation: Set a primary business event, export daily and cumulative data at a fixed time zone, and preserve event-level columns and spend for reconciliation. Compute CPA as spend divided by click-through conversions, and ROAS as Order Created Sales divided by spend only when `order_created` value data is complete.

- [Measure Results](https://help.openai.com/en/articles/20001214-measure-results) (`measurement-openai-measure-results-20260910`; retrieved 2026-09-10)

## measurement-pixel-capi

OpenAI supports a browser Measurement Pixel, a server-to-server Conversions API, or both. The API documentation calls CAPI more reliable than pixel-only tracking. Pixel plus CAPI require the same event ID for one conversion so OpenAI can deduplicate. The browser Pixel measures website events; CAPI receives server-originated events only. CAPI has a validation-only mode and accepts batches of up to 1,000 events, but one invalid event fails the full batch. The conversion-setup API documents a recent browser-event stream for enabled accounts. It is a receipt diagnostic, not attributed-conversion reporting.

Evidence state: evidence_based. Availability: documented_not_account_verified.

Interpretation: Use browser Pixel for user-side journey events and CAPI for authoritative server-side outcomes. Create a durable unique event ID at conversion creation, send that ID in both paths, use validation-only before production transmission, and monitor accepted events before interpreting performance.

- [Conversion Measurement](https://help.openai.com/en/articles/20001409-conversion-measurement) (`measurement-openai-conversion-20260910`; retrieved 2026-09-10)

- [Measurement Pixel](https://developers.openai.com/ads/measurement-pixel) (`measurement-openai-pixel-20260910`; retrieved 2026-09-10)

- [Conversions API](https://developers.openai.com/ads/conversions-api) (`measurement-openai-capi-20260910`; retrieved 2026-09-10)

- [Conversion Setup](https://developers.openai.com/ads/api-reference/conversion-setup) (`measurement-openai-conversion-setup-api-20260910`; retrieved 2026-09-10)

## measurement-attribution-and-matching

A reported conversion requires a connected data-source event, a configured matching standard or custom event, occurrence inside the applicable click window, and connection to an eligible click using available signals. `oppref` is appended to landing-page URLs, retained by the Pixel in a first-party cookie, and may be passed unchanged in CAPI. OpenAI may include modeled measurement where available. Advanced matching can use eligible normalized SHA-256 hashed first-party identifiers. Automatic advanced matching is documented for web pixels. The current conversion-setup API documents `attribution_window_days` as required and says to use 30 when defining an event setting. Modeled attribution means an Ads Manager total need not equal a directly observed click-ID match.

Evidence state: evidence_based. Availability: documented_not_account_verified.

Interpretation: Preserve `oppref` through redirects and client navigation, pass it to server events when available, and document whether reporting includes modeled conversions. Reconcile against internal event logs by event ID and timestamp, rather than expecting equality with web-analytics sessions.

- [Conversion Measurement](https://help.openai.com/en/articles/20001409-conversion-measurement) (`measurement-openai-conversion-20260910`; retrieved 2026-09-10)

- [Measurement Pixel](https://developers.openai.com/ads/measurement-pixel) (`measurement-openai-pixel-20260910`; retrieved 2026-09-10)

- [Conversions API](https://developers.openai.com/ads/conversions-api) (`measurement-openai-capi-20260910`; retrieved 2026-09-10)

- [Conversion Setup](https://developers.openai.com/ads/api-reference/conversion-setup) (`measurement-openai-conversion-setup-api-20260910`; retrieved 2026-09-10)

## measurement-vta-definition

View-through conversions are supplemental and separate from the main Conversions total. An eligible conversion within one day of an impression qualifies only when no qualifying click receives credit. Clicks take precedence. The fixed one-day view window cannot be configured. VTA (1d) can be added as a column and included in CSV exports. The report/API documentation says VTA must not be added to Conversions or used for core CPA, post-click CVR, bidding, billing, or optimization calculations.

Evidence state: evidence_based. Availability: documented_not_account_verified.

Interpretation: Report click-through CPA/ROAS as the decision metric and show VTA (1d) in a separate diagnostic column. Never combine the two into a blended CPA without an explicitly stated alternative model.

- [Measure Results](https://help.openai.com/en/articles/20001214-measure-results) (`measurement-openai-measure-results-20260910`; retrieved 2026-09-10)

- [Measurement Pixel](https://developers.openai.com/ads/measurement-pixel) (`measurement-openai-pixel-20260910`; retrieved 2026-09-10)

- [Insights API](https://developers.openai.com/ads/api-reference/insights) (`measurement-openai-insights-api-20260910`; retrieved 2026-09-10)

## measurement-events-and-values

Supported standard events include page/content views, cart and checkout activity, lead, registration, appointment, order, subscription, and trial events. App installs and app opens are CAPI-only with `mobile_app` action source. CAPI documents action sources including web, offline, physical store, phone call, email, and other. Use a standard event when it accurately describes the action. A custom event requires an exact custom name match in campaign configuration. For CAPI, event timestamp must be no older than seven days and no more than ten minutes ahead at submission.

Evidence state: evidence_based. Availability: documented_not_account_verified.

Interpretation: Make `order_created` the purchase event if sales/ROAS columns are required. Map lead stages and offline outcomes distinctly, retain transaction IDs in internal systems, and configure only exact event names used by the implementation.

- [Supported Events](https://developers.openai.com/ads/supported-events) (`measurement-openai-events-20260910`; retrieved 2026-09-10)

- [Conversions API](https://developers.openai.com/ads/conversions-api) (`measurement-openai-capi-20260910`; retrieved 2026-09-10)

- [Measure Results](https://help.openai.com/en/articles/20001214-measure-results) (`measurement-openai-measure-results-20260910`; retrieved 2026-09-10)

## measurement-exports-api

Ads Manager exports daily or cumulative CSVs. The Ads API provides aggregate delivery-insights endpoints at account, campaign, ad-group, and ad scope, plus `POST /conversions/insights` for attributed conversion totals. Documented insights segments include product, country, device, and platform, subject to enabled account capability. API `conversions` equals `click_through_conversions`; VTA is separately returned when available. No claim is made here that all accounts have API access or every segment enabled.

Evidence state: evidence_based. Availability: documented_not_account_verified.

Interpretation: Start with versioned CSV exports if API access is absent. If API access is enabled, retrieve delivery and conversion insights separately, record requested window, time granularity, segment, and query timestamp, then retain immutable raw responses.

- [Measure Results](https://help.openai.com/en/articles/20001214-measure-results) (`measurement-openai-measure-results-20260910`; retrieved 2026-09-10)

- [Insights API](https://developers.openai.com/ads/api-reference/insights) (`measurement-openai-insights-api-20260910`; retrieved 2026-09-10)

## measurement-partner-coverage

OpenAI documents integrations with Fospha, Hightouch, LiveRamp, Triple Whale and WorkMagic, with capabilities varying by partner. AppsFlyer and Adjust have separate mobile setup documentation. Do not infer that every listed partner supports web, app and offline activity. Partner functionality varies and must be confirmed in the partner documentation. No partner is evidence by itself of causal incrementality.

Evidence state: evidence_based. Availability: documented_not_account_verified.

Interpretation: Choose a partner only where its existing identity, event, or offline-conversion data closes a defined measurement gap. Keep a parallel first-party event ledger and test a new eligible click after mapping, then allow the documented 24 to 48 hours before judging reporting.

- [Set up Measurement Partner Integrations](https://help.openai.com/en/articles/20001416-set-up-measurement-partner-integrations) (`measurement-openai-partners-20260910`; retrieved 2026-09-10)

- [Set up Mobile Measurement Partner Integrations](https://help.openai.com/en/articles/20001372-set-up-mobile-measurement-partner-integrations) (`measurement-openai-mobile-partners-20260910`; retrieved 2026-09-10)

## measurement-optimization-objectives

Conversion optimization requires tracking and one supported standard event. Each campaign selects one event. oCPC bills valid clicks and is described as optimizing click-following conversions. oCPM bills impressions and is described as optimizing toward conversions using a broader eligible signal set, including actions after clicks and views. Custom events are not currently supported for these campaigns. Objective, billing model, and selected conversion event cannot be changed after creation, so a changed measurement definition requires a new campaign. OpenAI gives no recommended bid amount for conversion-optimized campaigns.

Evidence state: evidence_based. Availability: documented_not_account_verified.

Interpretation: Pre-register the optimization event, economic target, primary click-through KPI, and decision window before launch. Treat oCPM view-based optimization behavior as an account-specific feature to validate with support or an observed test because it is not fully reconciled with the general VTA reporting language.

- [Conversion-optimized Campaigns](https://help.openai.com/en/articles/20001412-conversion-optimized-campaigns) (`measurement-openai-ocpm-20260910`; retrieved 2026-09-10)

## measurement-benchmarks-evidence-quality

No independent controlled causal study of ChatGPT Ads performance was found in this research pass. OpenAI reports an unnamed ecommerce advertiser at 3x ROAS over 28 days and a technology-partner report that more than 80% of ad-driven traffic was new customers, without sample, baseline, attribution rule, spend, or experimental method. Flowboost, a vendor, reports relative results across three client accounts after two months and explicitly says its apparent incremental conversions are not statistically proven without a controlled test. These are publisher or vendor claims, not transferable benchmarks. OpenAI's reported 3x ROAS is an attributed outcome claim, not proof of incremental revenue.

Evidence state: practitioner. Availability: documented_not_account_verified.

Interpretation: Do not use published ROAS, CPC, CPA, conversion-rate, or new-customer figures for planning assumptions. Run a pre-specified holdout, matched-market, or randomized audience experiment and use first-party orders, qualified pipeline, or retained revenue as the causal outcome.

- [A milestone in expanding access to AI](https://openai.com/index/expanding-access-to-ai-with-chatgpt-ads/) (`measurement-openai-platform-claim-20260910`; retrieved 2026-09-10)

- [Claiming the first-movers advantage in ChatGPT ads](https://flowboost.com/client-stories/chatgpt-ads) (`measurement-flowboost-case-20260910`; retrieved 2026-09-10)

## refresh-vta-scope-20260910

Displayed VTA (1d) is supplemental reporting, separate from main click-through Conversions, and must not be used to change native CPA, post-click CVR, bidding, billing or conversion optimization. oCPM documentation separately describes broader eligible click and view signals; this does not establish the displayed VTA metric as an optimization input.

Evidence state: evidence_based. Availability: documented_not_account_verified.

Interpretation: Keep VTA reporting separate; do not calculate a blended native CPA.

- [Conversion-optimized Campaigns](https://help.openai.com/en/articles/20001412-conversion-optimized-campaigns) (`measurement-openai-ocpm-20260910`; retrieved 2026-09-10)

- [Measure Results](https://help.openai.com/en/articles/20001214-measure-results) (`measurement-openai-measure-results-20260910`; retrieved 2026-09-10)

- [Insights API](https://developers.openai.com/ads/api-reference/insights) (`measurement-openai-insights-api-20260910`; retrieved 2026-09-10)

## refresh-native-export-gap-20260910

Official documentation establishes daily and cumulative Ads Manager CSV exports and separately reports VTA where available. No native CSV sample was inspected in this refresh.

Evidence state: evidence_based. Availability: documented_not_account_verified.

Interpretation: Keep native mapping disabled until a real sanitized fixture and exact source-field interpretation are reviewed.

- [Measure Results](https://help.openai.com/en/articles/20001214-measure-results) (`measurement-openai-measure-results-20260910`; retrieved 2026-09-10)

- [Insights API](https://developers.openai.com/ads/api-reference/insights) (`measurement-openai-insights-api-20260910`; retrieved 2026-09-10)

## refresh-url-parameters-precedence-20260911

Current Ads Manager Help lists four configurable URL macros: campaign_id, ad_group_id, ad_id, and ad_account_id. It documents precedence from the most specific setting to the broadest: an existing parameter in the Ad URL wins, followed by Ad, Ad Group, and Campaign settings. Separately, OpenAI describes oppref as a click reference appended to landing-page URLs and preserved for Pixel or CAPI attribution. The public documentation reviewed does not list oppref as a user-configurable URL macro.

Evidence state: evidence_based. Availability: documented_not_account_verified.

Interpretation: Preserve existing landing-page parameters, apply the documented precedence order, and preserve oppref through redirects and navigation without assuming that a visible oppref token is a configurable macro in every account.

- [Measure Results](https://help.openai.com/en/articles/20001214-launch-your-campaign-and-monitor-performance) (`refresh-measure-results-20260911`; retrieved 2026-09-11)

- [Conversion Measurement](https://help.openai.com/en/articles/20001409-conversion-measurement) (`refresh-conversion-measurement-20260911`; retrieved 2026-09-11)

## refresh-products-reporting-semantics-20260911

For product-feed campaigns, the Products tab is an insights-backed reporting view rather than a complete uploaded-feed inventory. A product appears after an active campaign has delivered and reporting data is available. The product count shown during ad-group setup is the documented check for products that pass the selected filters and are ready to serve. Product reporting can take up to seven hours after delivery to appear.

Evidence state: evidence_based. Availability: documented_not_account_verified.

Interpretation: Do not diagnose feed ingestion from an empty Products tab alone. Check upload history and the ad-group product count first, then allow for reporting lag after delivery.

- [Create Campaigns from Product Feeds](https://help.openai.com/en/articles/20001268-create-campaigns-from-product-feeds) (`refresh-product-feeds-help-20260911`; retrieved 2026-09-11)

- [Measure Results](https://help.openai.com/en/articles/20001214-launch-your-campaign-and-monitor-performance) (`refresh-measure-results-20260911`; retrieved 2026-09-11)

## refresh-pixel-gtm-boundary-20260911

OpenAI documents deployment of the browser Pixel through Google Tag Manager when the tag manager loads the Pixel on the correct pages and does not block or reorder initialization and event calls. The same guidance recommends direct installation or appropriate server-side measurement if the tag manager prevents reliable loading.

Evidence state: evidence_based. Availability: documented_not_implementation_verified.

Interpretation: Treat GTM support as conditional on observed load order and event delivery. Validate the Pixel ID and debug behavior before relying on conversions.

- [Measure Results](https://help.openai.com/en/articles/20001214-launch-your-campaign-and-monitor-performance) (`refresh-measure-results-20260911`; retrieved 2026-09-11)

## refresh-report-window-semantics-20260911

Official documentation distinguishes three separate concepts: the reporting date range that selects the period being aggregated, the API time_ranges and time_granularity that bound and bucket insights, and the configured click attribution window used to determine conversion credit. The conversion-setup API currently requires attribution_window_days and instructs callers to use 30. The reviewed public documentation does not define account-visible 7-day, 14-day, or 30-day report-column labels as mutations of the conversion event setting, and it does not document a conversion-time column basis.

Evidence state: evidence_based_with_explicit_gap. Availability: documented_boundary_native_semantics_unverified.

Interpretation: Preserve report date range, row grain, timezone, configured attribution window, and conversion-time basis as separate fields. Treat unfamiliar UI column labels as account observations until a native export or current official definition establishes their semantics.

- [Measure Results](https://help.openai.com/en/articles/20001214-launch-your-campaign-and-monitor-performance) (`refresh-measure-results-20260911`; retrieved 2026-09-11)

- [Insights - Ads](https://developers.openai.com/ads/api-reference/insights) (`refresh-insights-api-20260911`; retrieved 2026-09-11)

- [Conversion Setup - Ads](https://developers.openai.com/ads/api-reference/conversion-setup) (`refresh-conversion-setup-api-20260911`; retrieved 2026-09-11)

- [Conversion Measurement](https://help.openai.com/en/articles/20001409-conversion-measurement) (`refresh-conversion-measurement-20260911`; retrieved 2026-09-11)
