# Native account acceptance handoff

Two distinct observations must be kept separate. The maintainer's earlier session reached an availability gate. A community first-pass report, updated September 11, 2026, subsequently describes native Chrome-enabled Claude access to a working Ads Manager, with campaign, reporting and tracking controls inspected read-only. The later report supersedes any blanket claim that no usable account has been observed. It does not establish current access in another session or native acceptance of this release's helpers.

The community report says billing setup and an account logo were still pending, with no campaigns, exports, API keys or conversion resources. No campaign was published and no tracking data was transmitted. Account identity and raw evidence remain outside this public package. These are attributed external observations, not independently reproduced maintainer results.

Reported controls include campaign objectives and budgets, location inclusion and exclusion, platforms, bidding, automatic text personalization, report segmentation and attribution columns, and distinct reporting versus bulk-edit export modes. Control visibility does not prove saved-state behavior. In particular, the report's statement that an automatically generated draft does not persist before publication remains unverified; reconcile possible drafts before any create/retry action.

## Inputs required in the private workspace

- Legal advertiser name, actual billing country, approved destination and product category.
- Exact account identity and which reporting objects/windows belong to this acceptance run.
- Existing API key reference if API testing is desired, never the secret in chat or this package.
- A genuine native CSV export with original bytes preserved privately, selected columns, table level, date range, timezone and attribution definitions.
- Existing Pixel/CAPI resources, event definitions and controlled destination if measurement testing is desired.

Use current official availability documentation and truthful business details. Do not change country, create a replacement identity or bypass a restriction to obtain acceptance.

## Read-only phase

The current task authorizes read-only inspection. Once an eligible account is supplied, verify its identity first. Inspect available controls; record account, currency, timezone and feature observations privately. If an existing configured key is available, use the documented account-read endpoint, then a narrowly scoped reporting read. Classify an endpoint by its documented effects, not simply its HTTP verb.

Obtain a minimal genuine report export. Hash the raw bytes, preserve original metadata and inspect actual headers and row grain. Only then implement and test a versioned mapping. Retain missing values, keep event-specific conversion definitions explicit, separate VTA, and reconcile totals against the selected native reporting view. Do not enable a native adapter from a fictional fixture or a bulk-upload template.

## Measurement phase

Prepare the exact staging URL, event payload and data flow for review before sending test data or changing a destination. Prefer validation-only checks where documented and available. Never transmit customer identifiers for a synthetic test. Record consent behavior, event IDs, browser/server deduplication, payload validation and receipt as separate outcomes. Attribution acceptance additionally needs eligible traffic, configured event settings and reporting lag.

A successful HTTP response or event receipt does not establish attribution. A validation-only response does not establish persistence. The offline measurement fixture validates only its declared business preparation rules.

## Live action phase

Prepare a campaign plan and action plan using the companion schemas. Bind account, exact before/after settings, assets, destination, maximum spend effect, schedule, recovery limits and verification to the reviewed artifact. No budget is assumed by this handoff. Obtain applicable owner approval for the concrete batch. Re-observe immediately before acting and reconcile uncertain saves before retrying.

A draft or review-pending object is not a delivering campaign. Record object IDs, actual saved values and later delivery state separately. Measuring performance requires real eligible traffic, a meaningful observation period, measurement quality and actual economics. Do not promise results or universal benchmarks from local tests.

## Acceptance evidence to retain

| Area | Evidence that closes the gate |
| --- | --- |
| Account access | Verified advertiser/account profile and observed usable controls |
| Native reporting | Real export, versioned mapping, data-quality checks and reconciled native totals |
| API | Actual authenticated response, identity match, field contract, scoped adapter tests |
| Pixel/CAPI | Reviewed test data, browser/network observations, native validation and receipt results |
| Live changes | Exact authorization, executed steps, saved-state receipt and reconciliation |
| Performance | Compatible measurement window, spend/outcomes, uncertainty and business decision |
| Claude browser | Actual native binding invocation and observed control of the local fixture before account use |

Scheduling remains disabled. No global installation, credential creation, permission change or publication is part of this handoff.
