# Platform evidence

Generated from canonical registries. Do not edit this projection. Dated documentation is not account verification. Run guarded retrieval before using a current claim.

## platform-finding-001

ChatGPT Ads is no longer announcement-only. OpenAI describes Ads Manager as beta and early-stage scaling, while its August 31 announcement describes availability in more than 40 countries. The current availability page lists 52 self-service countries. The exact per-country list is the controlling volatile source.

Evidence state: evidence_based. Availability: documented_not_account_verified.

Interpretation: Label the platform available in beta. Refresh the availability page before any market-specific plan.

- [Ads Manager Availability](https://help.openai.com/en/articles/20001245-ads-manager-availability) (`platform-availability`; retrieved 2026-09-10)

- [Ads Manager Beta Overview](https://help.openai.com/en/articles/20001206-ads-manager-beta-overview) (`platform-manager-overview`; retrieved 2026-09-10)

- [A milestone in expanding access to AI](https://openai.com/index/expanding-access-to-ai-with-chatgpt-ads/) (`platform-global-expansion`; retrieved 2026-09-10)

## platform-finding-002

Current official Help and developer pages consistently direct advertisers to https://ads.openai.com/. The requested https://ads.chatgpt.com/ returned DisabledError in this research environment and was not the URL named by current public operating docs.

Evidence state: evidence_based. Availability: documented_not_account_verified.

Interpretation: Use ads.openai.com as the documented portal route. Treat ads.chatgpt.com behavior as unverified until it can be checked in an ordinary browser without signing in.

- [Ads Manager Beta Account Setup](https://help.openai.com/en/articles/20001213-ads-manager-beta-account-setup) (`platform-account-setup`; retrieved 2026-09-10)

- [Ads Manager Beta Overview](https://help.openai.com/en/articles/20001206-ads-manager-beta-overview) (`platform-manager-overview`; retrieved 2026-09-10)

- [New ways to buy ChatGPT ads](https://openai.com/index/new-ways-to-buy-chatgpt-ads/) (`platform-new-buying-routes`; retrieved 2026-09-10)

## platform-finding-003

OpenAI documents direct support through its Ads Solutions team, agency partners, technology partners, beta self-service Ads Manager, and an account-scoped Advertiser API. Partner tools can support budgeting, bidding, and creative, while OpenAI controls delivery decisions.

Evidence state: evidence_based. Availability: documented_not_account_verified.

Interpretation: Choose route by advertiser size and eligibility. Do not assume self-service or API access from market availability alone.

- [New ways to buy ChatGPT ads](https://openai.com/index/new-ways-to-buy-chatgpt-ads/) (`platform-new-buying-routes`; retrieved 2026-09-10)

- [Ads Manager Availability](https://help.openai.com/en/articles/20001245-ads-manager-availability) (`platform-availability`; retrieved 2026-09-10)

- [Overview - Ads](https://developers.openai.com/ads/api-overview) (`platform-advertiser-api-overview`; retrieved 2026-09-10)

## platform-finding-004

Account creation requires an OpenAI login, business and account details, advertiser verification, account name and logo, billing profile, payment method, and access roles. Campaigns do not deliver until required setup and review are complete. Country, currency, and time zone can be non-editable after creation.

Evidence state: evidence_based. Availability: documented_not_account_verified.

Interpretation: Add a preflight that confirms legal entity, country, currency, time zone, advertiser identity, brand review, payment, and accountable owner before campaign creation.

- [Ads Manager Beta Account Setup](https://help.openai.com/en/articles/20001213-ads-manager-beta-account-setup) (`platform-account-setup`; retrieved 2026-09-10)

- [Managing identity and access for Ads Manager](https://help.openai.com/en/articles/20001273-managing-identity-and-access-for-ads-manager) (`platform-identity-access`; retrieved 2026-09-10)

- [Billing & Payment](https://help.openai.com/en/articles/20001216-billing-payment) (`platform-billing`; retrieved 2026-09-10)

## platform-finding-005

OpenAI documents a relevance-weighted, second-price auction. When several ads are eligible, relevance and advertiser bids are factors. Public sources do not disclose the scoring formula, reserve prices, quality thresholds, or tie-breaking rules.

Evidence state: evidence_based. Availability: documented_not_account_verified.

Interpretation: Model auction mechanics only at the documented level. Do not import Google Ads quality-score formulas or first-price assumptions.

- [Ads in ChatGPT: The Basics](https://help.openai.com/en/articles/20001207-ads-in-chatgpt-the-basics) (`platform-ads-basics`; retrieved 2026-09-10)

- [Ads in ChatGPT](https://help.openai.com/en/articles/20001047-ads-in-chatgpt) (`platform-consumer-faq`; retrieved 2026-09-10)

## platform-finding-006

Current Help documents CPM, CPC, and oCPC. A newer conversion-optimized article also documents oCPM as beta with rapidly expanding access. CPC and oCPC bill valid clicks, CPM and oCPM bill impressions. oCPC and oCPM optimize toward one standard conversion event and do not bill per conversion. The public Advertiser API documents impressions, clicks, and conversions, with conversions meaning oCPC, but does not document oCPM.

Evidence state: evidence_based. Availability: documented_not_account_verified.

Interpretation: Expose oCPM as account-dependent beta in UI guidance and block API creation until official API docs add a supported representation.

- [Create Campaigns for ChatGPT Ads](https://help.openai.com/en/articles/20001210-create-campaigns-for-chatgpt-ads) (`platform-campaigns`; retrieved 2026-09-10)

- [Conversion-optimized Campaigns](https://help.openai.com/en/articles/20001412-conversion-optimized-campaigns) (`platform-conversion-optimized`; retrieved 2026-09-10)

- [Campaigns - Ads](https://developers.openai.com/ads/api-reference/campaigns) (`platform-api-campaigns`; retrieved 2026-09-10)

## platform-finding-007

Manual maximum bids are set at ad-group level. OpenAI recommends a starting max CPC of USD 3 to 5 for CPC campaigns, but gives no universal conversion bid recommendation. Maximize results automatically adjusts bids for eligible ad groups and does not guarantee CPA, CPC, ROAS, or other efficiency targets. Custom-audience bid multipliers are documented from 0.1x to 10x for eligible audiences.

Evidence state: evidence_based. Availability: documented_not_account_verified.

Interpretation: Treat bid guidance as a starting point, not a benchmark or forecast. Preserve explicit max-bid and automated-strategy distinctions.

- [Ads in ChatGPT: The Basics](https://help.openai.com/en/articles/20001207-ads-in-chatgpt-the-basics) (`platform-ads-basics`; retrieved 2026-09-10)

- [Maximize Results Bid Strategy](https://help.openai.com/en/articles/20001425-maximize-results-bid-strategy) (`platform-maximize-results`; retrieved 2026-09-10)

- [Ad Groups - Ads](https://developers.openai.com/ads/api-reference/ad-groups) (`platform-api-ad-groups`; retrieved 2026-09-10)

## platform-finding-008

Ads Manager supports daily average and campaign-total budgets. Daily spend can reach twice the selected daily budget, while billed media spend over the applicable seven-day period cannot exceed seven times that budget, subject to proration after changes. Campaign-total pacing uses the schedule, up to 365 days with an end date and a default 60-day period without one. Pacing does not guarantee full spend or equal daily spend.

Evidence state: evidence_based. Availability: documented_not_account_verified.

Interpretation: Show the two-times daily exposure and seven-day cap in budget reviews. Use campaign-total budgets where a hard campaign cap matters most.

- [Daily Budgets](https://help.openai.com/en/articles/20001413-daily-budgets) (`platform-daily-budgets`; retrieved 2026-09-10)

- [Budget Pacing](https://help.openai.com/en/articles/20001515-budget-pacing) (`platform-budget-pacing`; retrieved 2026-09-10)

- [Create Campaigns for ChatGPT Ads](https://help.openai.com/en/articles/20001210-create-campaigns-for-chatgpt-ads) (`platform-campaigns`; retrieved 2026-09-10)

## platform-finding-009

Minimum daily campaign budget varies by billing currency. The current table includes USD 25, EUR 15, GBP 15, and other listed currency values. The API campaign reference separately shows a lifetime budget field minimum of 1,000,000 micros, which is a schema minimum and is not evidence of a generally usable one-unit campaign budget.

Evidence state: evidence_based. Availability: documented_not_account_verified.

Interpretation: Validate against the account currency and current Ads Manager minimum. Do not substitute the API field minimum for the operational minimum.

- [Create Campaigns for ChatGPT Ads](https://help.openai.com/en/articles/20001210-create-campaigns-for-chatgpt-ads) (`platform-campaigns`; retrieved 2026-09-10)

- [Campaigns - Ads](https://developers.openai.com/ads/api-reference/campaigns) (`platform-api-campaigns`; retrieved 2026-09-10)

## platform-finding-010

The public campaign targeting contract documents location, platform, custom-audience inclusion and exclusion, and ad-group audience bid adjustments. Ad-group context hints guide conversational relevance but are not exact-match keywords, audience rules, or guaranteed placements. No current public source establishes demographic, interest, device-model, schedule/daypart, negative-keyword, or placement-exclusion controls for advertisers.

Evidence state: evidence_based. Availability: documented_not_account_verified.

Interpretation: Represent only documented targeting controls. Keep all other conventional ad-platform controls explicitly unsupported.

- [Campaign Targeting - Ads](https://developers.openai.com/ads/campaign-targeting) (`platform-api-targeting`; retrieved 2026-09-10)

- [Create Ad Groups for ChatGPT Ads](https://help.openai.com/en/articles/20001211-create-ad-groups-for-chatgpt-ads) (`platform-ad-groups`; retrieved 2026-09-10)

- [Set up Custom Audiences for your Campaign](https://help.openai.com/en/articles/20001346-set-up-custom-audiences-for-your-campaign) (`platform-custom-audiences`; retrieved 2026-09-10)

## platform-finding-011

Ads Manager supports countries and available states or regions, cities, DMAs, and postal codes. Availability varies by country. The API uses location IDs from geo lookup and defaults to all available locations when location targeting is omitted. Exception: new product-feed campaign location selections are country-level only, with exclusions; saved older subnational selections may remain, but new subnational selections cannot be added.

Evidence state: evidence_based. Availability: documented_not_account_verified.

Interpretation: Resolve location IDs or use the live picker/catalog immediately before launch. Never assume all subnational types exist in every market. Verify product-feed campaign restrictions before offering subnational targets.

- [Create Campaigns for ChatGPT Ads](https://help.openai.com/en/articles/20001210-create-campaigns-for-chatgpt-ads) (`platform-campaigns`; retrieved 2026-09-10)

- [Campaign Targeting - Ads](https://developers.openai.com/ads/campaign-targeting) (`platform-api-targeting`; retrieved 2026-09-10)

- [Create Campaigns for ChatGPT Ads](https://help.openai.com/en/articles/20001210-create-campaigns-for-chatgpt-ads) (`refresh-campaigns-help-20260911`; retrieved 2026-09-11)

## platform-finding-012

Ads Manager Help documents iOS app, Android app, and Web, with Web covering desktop and mobile web. The Advertiser API changelog added desktop_web, ios_web, and android_web on 2026-09-10, alongside ios_app, android_app, and the broad web value. Omitting platform targeting leaves no platform restriction.

Evidence state: evidence_based. Availability: documented_not_account_verified.

Interpretation: Prefer current API values for automation and preserve the broad web value for compatibility. Refresh this control weekly during beta.

- [Create Campaigns for ChatGPT Ads](https://help.openai.com/en/articles/20001210-create-campaigns-for-chatgpt-ads) (`platform-campaigns`; retrieved 2026-09-10)

- [Platform Targeting - Ads](https://developers.openai.com/ads/platform-targeting) (`platform-api-platform-targeting`; retrieved 2026-09-10)

- [Overview - Ads](https://developers.openai.com/ads/api-overview) (`platform-advertiser-api-overview`; retrieved 2026-09-10)

## platform-finding-013

Custom audiences accept email, phone, hashed email or phone, and GAID identifiers. Inclusion and bid adjustments require at least 25,000 matched users, with 100,000 recommended. Smaller and empty ready audiences can be used for exclusion. Developer docs say custom audiences are not supported for campaigns targeting the EEA or Switzerland, and broker-sourced data is prohibited by the documented audience guidance.

Evidence state: evidence_based. Availability: documented_not_account_verified.

Interpretation: Require rights, notice, consent, regional, and matched-size checks before activation. Preserve exclusion-only eligibility separately.

- [Set up Custom Audiences for your Campaign](https://help.openai.com/en/articles/20001346-set-up-custom-audiences-for-your-campaign) (`platform-custom-audiences`; retrieved 2026-09-10)

- [Campaigns - Ads](https://developers.openai.com/ads/api-reference/campaigns) (`platform-api-campaigns`; retrieved 2026-09-10)

## platform-finding-014

Ads can appear below a ChatGPT response, clearly sponsored and visually separate. A response may have one or more ad units, and a unit may include one or more items or multiple advertisers. Ads do not appear in ChatGPT Atlas during the test. OpenAI controls delivery and excludes sensitive and brand-unsafe contexts. Public advertiser docs do not expose a control to choose a precise response position or exact conversation.

Evidence state: evidence_based. Availability: documented_not_account_verified.

Interpretation: Describe placement as contextual inventory controlled by OpenAI, with platform and policy controls. Do not promise exact queries or adjacencies.

- [Ads in ChatGPT](https://help.openai.com/en/articles/20001047-ads-in-chatgpt) (`platform-consumer-faq`; retrieved 2026-09-10)

- [Ad policies](https://openai.com/policies/ad-policies/) (`platform-ad-policies`; retrieved 2026-09-10)

- [New ways to buy ChatGPT ads](https://openai.com/index/new-ways-to-buy-chatgpt-ads/) (`platform-new-buying-routes`; retrieved 2026-09-10)

## platform-finding-015

The Advertiser API names two creative types: chat_card and product_ad_template. A chat card uses title, body, image file, and target URL. Product-feed ads use product data such as image, title, price or sale price, rating, brand, and destination. Current self-service documentation does not establish a general video, audio, lead-form, or advertiser-authored conversational creative format.

Evidence state: evidence_based. Availability: documented_not_account_verified.

Interpretation: Support only chat cards and product-feed templates in current-format guidance. Track future formats as announced, not available.

- [Ads in ChatGPT: The Basics](https://help.openai.com/en/articles/20001207-ads-in-chatgpt-the-basics) (`platform-ads-basics`; retrieved 2026-09-10)

- [Create Campaigns from Product Feeds](https://help.openai.com/en/articles/20001268-create-campaigns-from-product-feeds) (`platform-product-feeds`; retrieved 2026-09-10)

- [Ads - OpenAI Developers](https://developers.openai.com/ads/api-reference/ads) (`platform-api-ads`; retrieved 2026-09-10)

## platform-finding-016

Current Help recommends 16 to 24 title characters and 32 to 48 body characters, with maxima of 50 and 100. Bulk-upload guidance requires a square PNG or JPG image, no larger than 1200 by 1200, at a directly accessible public URL. API-created chat cards require an uploaded file ID. Landing pages must be reachable by OAI-AdsBot and pass review.

Evidence state: evidence_based. Availability: documented_not_account_verified.

Interpretation: Validate maximums as hard constraints and recommendations as soft checks. Verify both human reachability and OAI-AdsBot access.

- [Launch Campaigns](https://help.openai.com/en/articles/20001209-launch-campaigns) (`platform-launch`; retrieved 2026-09-10)

- [Create Ads for ChatGPT Ads](https://help.openai.com/en/articles/20001212-create-ads-for-chatgpt-ads) (`platform-create-ads`; retrieved 2026-09-10)

## platform-finding-017

Campaigns use campaign, ad group, and ad hierarchy. Ads Manager supports guided creation, bulk CSV creation and edit, inline edits, export-for-edit, pause, and reporting. The Advertiser API supports account-scoped management of campaigns, ad groups, ads, files, audiences, feeds, conversions, and insights. API keys are created in Ads Manager. API availability and some operations remain account-enabled.

Evidence state: evidence_based. Availability: documented_not_account_verified.

Interpretation: Treat UI, CSV, and API as separate adapters. Mark API controls documented but untested until exercised against an eligible account with explicit authorization.

- [Ads Manager Beta Overview](https://help.openai.com/en/articles/20001206-ads-manager-beta-overview) (`platform-manager-overview`; retrieved 2026-09-10)

- [Launch Campaigns](https://help.openai.com/en/articles/20001209-launch-campaigns) (`platform-launch`; retrieved 2026-09-10)

- [Edit Campaigns](https://help.openai.com/en/articles/20001215-edit-campaigns) (`platform-edit`; retrieved 2026-09-10)

- [Overview - Ads](https://developers.openai.com/ads/api-overview) (`platform-advertiser-api-overview`; retrieved 2026-09-10)

## platform-finding-018

The base endpoint is https://api.ads.openai.com/v1. Keys are scoped to one ad account. The documented rate limits are 600 requests per minute per endpoint and 1,200 requests per minute overall, enforced by ad account and IP; bulk job creation has a separate limit. This research made no API request and created no key, so account entitlement, schema responses, and live behavior remain unverified.

Evidence state: evidence_based. Availability: documented_not_account_verified.

Interpretation: Keep all API capabilities at documented status. Require a separate authorized sandbox or account validation before claiming live support.

- [Overview - Ads](https://developers.openai.com/ads/api-overview) (`platform-advertiser-api-overview`; retrieved 2026-09-10)

- [Campaigns - Ads](https://developers.openai.com/ads/api-reference/campaigns) (`platform-api-campaigns`; retrieved 2026-09-10)

- [Ad Groups - Ads](https://developers.openai.com/ads/api-reference/ad-groups) (`platform-api-ad-groups`; retrieved 2026-09-10)

- [Ads - OpenAI Developers](https://developers.openai.com/ads/api-reference/ads) (`platform-api-ads`; retrieved 2026-09-10)

- [Insights - Ads](https://developers.openai.com/ads/api-reference/insights) (`platform-api-insights`; retrieved 2026-09-10)

## platform-finding-019

Retailers can import a feed by CSV or TXT, hosted HTTPS URL, or SFTP, filter eligible products at ad-group level, and create one template per ad group. Feed items expire after two weeks, so hosted or automated updates are recommended. During beta, uploaded products are ads-eligible only and do not appear in organic ChatGPT conversations.

Evidence state: evidence_based. Availability: documented_not_account_verified.

Interpretation: Require feed freshness monitoring, validation history checks, and a clear boundary between paid inventory and organic commerce visibility.

- [Create Campaigns from Product Feeds](https://help.openai.com/en/articles/20001268-create-campaigns-from-product-feeds) (`platform-product-feeds`; retrieved 2026-09-10)

- [Ads - OpenAI Developers](https://developers.openai.com/ads/api-reference/ads) (`platform-api-ads`; retrieved 2026-09-10)

## platform-finding-020

Ads Manager reports impressions, clicks, spend, CTR, average CPC, average CPM, and attributed conversions. Views include tables, charts, and daily or cumulative CSV. API insights cover account, campaign, ad group, and ad scopes with hourly, daily, monthly, or total buckets and product, country, device, or platform segments. Reporting can lag, especially conversions.

Evidence state: evidence_based. Availability: documented_not_account_verified.

Interpretation: Treat missing or zero recent values as potentially delayed. Preserve reporting timezone and attribution definitions in every analysis.

- [Measure Results](https://help.openai.com/en/articles/20001214-measure-results) (`platform-results`; retrieved 2026-09-10)

- [Insights - Ads](https://developers.openai.com/ads/api-reference/insights) (`platform-api-insights`; retrieved 2026-09-10)

## platform-finding-021

ChatGPT Ads uses postpay billing. The card is charged at an assigned unpaid-spend threshold or at month end. A threshold is neither a campaign budget nor an account spend cap. Delivery updates can take time, and billable delivery may continue for up to 24 hours after a pause, while final reporting can change later without exceeding the applicable budget.

Evidence state: evidence_based. Availability: documented_not_account_verified.

Interpretation: Separate payment threshold, account spending limit, campaign budget, and reported spend in every control model. Allow for pause and reporting latency.

- [Billing & Payment](https://help.openai.com/en/articles/20001216-billing-payment) (`platform-billing`; retrieved 2026-09-10)

## platform-finding-022

OpenAI's current advertiser FAQ states that the platform does not yet have cross-advertiser, industry, or campaign-type performance benchmarks. Public case-study anecdotes do not establish planning benchmarks.

Evidence state: evidence_based. Availability: documented_not_account_verified.

Interpretation: Do not publish universal CTR, CPC, CPM, conversion-rate, or ROAS benchmarks for ChatGPT Ads. Use account data only when supplied and qualified.

- [Ads Manager Beta Overview](https://help.openai.com/en/articles/20001206-ads-manager-beta-overview) (`platform-manager-overview`; retrieved 2026-09-10)

## refresh-catalog-api-boundary-20260910

The public product-feed API documentation does not provide feed-connection creation, feed-connection listing or catalog-file upload. Ads Manager documents CSV/TXT, hosted HTTPS URL and SFTP intake.

Evidence state: evidence_based. Availability: documented_not_account_verified.

Interpretation: Use account-observed Ads Manager onboarding for feeds; do not invent API catalog upload.

- [Product Feeds](https://developers.openai.com/ads/product-feeds) (`refresh-product-feeds-20260910`; retrieved 2026-09-10)

- [Create Campaigns from Product Feeds](https://help.openai.com/en/articles/20001268-create-campaigns-from-product-feeds) (`platform-product-feeds`; retrieved 2026-09-10)

## refresh-manual-bid-label-boundary-20260911

Help names Manual: Max bid as an alternative to Maximize results. Conversion-optimized Campaigns explicitly documents Bid Cap as a maximum conversion-oriented bid. For oCPC, the API max_bid_micros is a CPA bid while billing remains per valid click. Bid Cap is not a conversion charge or guaranteed achieved CPA. Exact available controls still require account verification.

Evidence state: evidence_based. Availability: documented_not_account_verified.

Interpretation: Preserve the strategy name, economic unit, and billing event separately. Confirm the account-visible label before writing UI-specific instructions.

- [Maximize Results Bid Strategy](https://help.openai.com/en/articles/20001425-maximize-results-bid-strategy) (`refresh-maximize-results-help-20260911`; retrieved 2026-09-11)

- [Ad Groups - Ads](https://developers.openai.com/ads/api-reference/ad-groups) (`refresh-ad-groups-api-20260911`; retrieved 2026-09-11)

- [Conversion-optimized Campaigns](https://help.openai.com/en/articles/20001412-conversion-optimized-campaigns) (`refresh-conversion-controls-20260911`; retrieved 2026-09-11)

## refresh-chatgpt-account-setup-scope-20260911

Eligible business advertisers can begin self-serve Ads Manager account setup through ChatGPT Ads Manager and work with supported campaigns, ad groups, ads, and performance insights. Available actions and workspace access may vary. Eligibility and access depend on the advertiser business or ad-account country selected during setup; the country of the ChatGPT login or account registration does not override it. Remaining billing, tax, payment, and identity-verification steps may still require Ads Manager.

Evidence state: evidence_based. Availability: documented_account_dependent.

Interpretation: Verify the advertiser entity, account country, organization permission, currency, timezone, and remaining setup gates before treating ChatGPT account setup as delivery readiness.

- [Ads Manager Beta Account Setup](https://help.openai.com/en/articles/20001213) (`refresh-account-setup-help-20260911`; retrieved 2026-09-11)

## refresh-location-catalog-surface-boundary-20260911

Ads Manager Help documents campaign-level country targeting and, in the United States, supported state, DMA, and ZIP-code targeting. Its FAQ also describes states or regions, cities, DMAs, and postal codes where available, with availability varying by country. New product-feed campaigns are an explicit exception: they support country-level geographic targeting and exclusions only; existing product-feed campaigns may retain saved subnational settings but cannot add new subnational locations. The public API location guide documents country, region, and Market IDs through geo_lookup search and links a current downloadable location catalog CSV; it does not document a postal-code API type in the reviewed page.

Evidence state: evidence_based. Availability: documented_account_and_country_dependent.

Interpretation: Resolve target locations against campaign type, the current account picker or geo lookup, and the current catalog. Do not apply general subnational targeting to new product-feed campaigns or assume a Help-only location type exists in the API.

- [Create Campaigns for ChatGPT Ads](https://help.openai.com/en/articles/20001210-create-campaigns-for-chatgpt-ads) (`refresh-campaigns-help-20260911`; retrieved 2026-09-11)

- [Location Targeting - Ads](https://developers.openai.com/ads/location-targeting) (`refresh-location-targeting-api-20260911`; retrieved 2026-09-11)
