# Native acceptance research, 2026-09-10

## Decision

The next acceptance pass is **blocked for native-account evidence**, not for
local analysis. The documented Advertiser API provides a narrow read-only
account verification and delivery-insights path. It cannot be exercised here:
no configured account-key reference, native CSV, or account-visible
campaign/report controls was available. The observed browser gate is evidence
of unavailable controls in this session, not evidence of country availability
or account ineligibility.

No source-registry update proposal accompanies this report. The live sources
confirmed the documented facts already represented by the current claims. The
availability page still lists 52 available self-service countries and the
existing registry already treats it as volatile. The report records newly
precise locators and an acceptance sequence without changing canonical facts.

## Evidence classes

| Class | Result |
| --- | --- |
| Local deterministic | Implemented normalized-CSV analyzer and local guards. Its contract explicitly excludes native ChatGPT Ads CSV ingestion. |
| Official documentation, live rechecked | Authentication, ad-account metadata, insights, Pixel, CAPI, conversion setup, measurement CSV workflow, and availability. |
| Native read-only | Not performed. The browser session exposed a country-availability gate and no campaign/report controls. No API request was made. |
| Account mutation or event delivery | Not performed. No key, Pixel, CAPI event, account creation, conversion resource, or campaign action was made. |

## Current documented read-only API path

1. Ads API requests use `https://api.ads.openai.com/v1` with
   `Authorization: Bearer $OPENAI_ADS_API_KEY`. A key is scoped to one ad
   account. The quickstart says the account holder issues it in Ads Manager
   Settings.
2. The documented safe authentication and account-identity probe is
   `GET /ad_account`, with no body or query parameters. It returns the
   account ID, name, URL, status where available, timezone, currency and brand
   review state. It requires a configured account key reference, confirmed
   account identity, exact read scope, and private response handling.
3. Documented delivery-insights reads are `GET /ad_account/insights`,
   `GET /campaigns/{campaign_id}/insights`,
   `GET /ad_groups/{ad_group_id}/insights`, and
   `GET /ads/{ad_id}/insights`. Attributed conversion totals use
   `POST /conversions/insights`. It is a documented retrieval endpoint despite
   its HTTP verb. The authorized acceptance read scope can cover it after the
   exact account, IDs, time range, and private handling are confirmed.
4. API capability is still account-dependent. The conversion-setup reference
   says Pixel management, CAPI-key creation, and the recent-event stream must
   be enabled per account, and directs a caller to its OpenAI partner
   representative after a `404 Not found`.

## Native CSV: documented boundary versus local adapter

The official Help article documents an **export workflow**, not a fixed CSV
file schema. It says cumulative export is available for the current table or
selected rows, daily export is separate, VTA may be included when available,
and event-specific columns must be added before export. Example event headers
may be `attributed_event_account_created` or
`attributed_event_registration_completed`. It does not publish required column
order, complete header enumeration, types, row granularity, encoding, or a
versioned CSV contract.

Therefore the package's `manual-normalized-v1` CSV is a local transformation
contract only. Its exact 14-column ad-level schema is not an OpenAI native
export schema. The disabled `chatgpt-ads-native-csv` adapter remains correctly
disabled until one sanitized native export is inspected and a reviewed mapping
is tested. Do not infer a native API-to-CSV parity contract from the published
insights endpoints.

## Safe measurement validation procedures

| Procedure | What it proves | Preconditions | What it does not prove |
| --- | --- | --- | --- |
| Pixel debug mode in a staging page | SDK initialization and browser-side debug activity | Existing Pixel ID, site deployment authority, consent design | That OpenAI received an event, attribution, delivery, or production readiness |
| `GET /conversions/events?pid=...` | Up to 50 Pixel-SDK events received in the last 15 minutes | Ads API key, Pixel ID, endpoint enabled for account, approval for account read | Attribution or reporting totals |
| CAPI batch with `validate_only: true` | Event payload validity without saving the events | Existing Pixel ID and CAPI key, server-side secret handling, separately approved test-event transmission | Persistence, receipt in the account, attribution, or performance |
| Delivery insights GET | Account/campaign/ad-group/ad delivery response shape and fields actually returned | Configured key reference, confirmed account identity, exact IDs/window, private output handling | Native CSV compatibility or conversion attribution |
| `POST /conversions/insights` | Attributed click-through totals and separately reported VTA, when returned | Configured key reference, confirmed account identity, exact IDs/window, private output handling | That source events were accepted, or that VTA should enter CPA/ROAS |

Pixel consent matters: if consent is false, the Pixel does not send event
pings, and events blocked during that state are not replayed. The CAPI
reference requires server-originated delivery. If Pixel and CAPI are both used
for the same conversion, the conversion-setup reference requires a shared
event ID for deduplication. CAPI batch validation accepts at most 1,000 events;
one invalid event fails the whole batch.

## Minimal private account intake

Keep these records outside the distributable package and never paste keys,
cookies, raw exported rows, customer identifiers, or account IDs into this
report.

1. Legal entity's billing country, advertiser name, primary URL, and declared
   category. Confirm the legal entity's country against the current official
   availability list. Country availability is necessary for self-service, not
   proof of account eligibility or feature enablement.
2. Observed Ads Manager route and timestamp. Record whether the session reaches
   account controls or an availability gate. Treat historical UI dates/text as
   stale presentation data until rechecked against the official availability
   page.
3. Account metadata, collected only after approval, via the documented
   `GET /ad_account` probe: redacted account reference, status, timezone,
   currency, and brand-review status.
4. Read-only acceptance scope: which of account metadata, delivery insights,
   conversion insights, event settings, and recent Pixel events may be read;
   window, object IDs or a private ID-reference manifest, recipient, and
   retention path for responses.
5. Measurement setup evidence: existing Pixel ID reference, CAPI key reference
   held only by the server secret manager, consent state/design, conversion
   event definition, value/currency basis, and test/staging URL. State whether
   each conversion-setup resource already exists. Resource creation is outside
   this acceptance pass.
6. A sanitized, minimum native CSV export: selected reporting scope, export
   mode (daily or cumulative), date window, account timezone, headers, and one
   non-sensitive representative data row. Preserve the original privately with
   a hash. Do not use a made-up CSV as proof.

## Minimal safe acceptance sequence

1. Recheck the official availability page immediately before account work and
   record the legal entity's country result. The page currently says the legal
   entity that is advertised and billed must be based in a listed country.
2. In the private workspace, have the account owner identify the exact account
   and provide an existing configured key reference without disclosing the
   secret. Do not create an account, API key, Pixel, CAPI key, event setting,
   campaign, or budget in this pass.
3. Use the authorized read-only acceptance scope to issue only
   `GET /ad_account`. Compare returned timezone/currency/status/review with
   the private intake. Store a redacted receipt and response hash.
4. If the account exposes objects within the agreed read scope, call one
   delivery-insights GET for a tightly stated time range and
   scope. Save raw output privately, its hash, request parameters, and
   retrieval time. If conversion totals are in that read scope, use
   `POST /conversions/insights` with the same exact-scope and privacy checks.
5. Export one native CSV through the visible Ads Manager reporting workflow,
   once it is actually accessible. Capture daily and cumulative exports as two
   separate artifacts if both are needed. Record table level, selected rows,
   columns, VTA availability, timezone, and date range. Inspect headers and
   row grain before any mapping.
6. Map only non-overlapping ad-level native rows into `manual-normalized-v1`.
   Preserve the mapping and reconciliation. If native rows cannot satisfy the
   local schema, leave the adapter disabled and report the mismatch.
7. For measurement, first exercise Pixel debug on a controlled staging route
   after consent is satisfied. If the account supports it, use the recent
   event stream to confirm receipt. Use a one-event CAPI validation-only batch
   before any production submission. These checks require separate access and
   deployment authorization.
8. Do not call successful receipt, validation, or an insight response
   attribution acceptance. Attribution requires configured conversion settings,
   eligible traffic, and reporting lag. The Help page says attributed
   conversions can take 24-48 hours to appear.

## Account blockers observed or unresolved

| Blocker | Evidence | Acceptance effect |
| --- | --- | --- |
| Browser did not show campaign or reporting controls | Parent's logged-in browser observation, 2026-09-10 | Cannot collect a native export, create/view API key, or observe account capabilities. |
| Current country eligibility of the actual legal entity is unknown | No private intake supplied | Do not interpret the gate as country ineligibility. Recheck the legal entity's country against the official page. |
| No configured key reference or resolved account identity | Read-only inspection is authorized, but no secret or target identity was supplied to this lane | No native `GET /ad_account`, insights, Pixel event stream, or CAPI validation was performed. |
| No native CSV sample | Adapter manifest explicitly says native CSV is disabled | No source-field mapping or parser acceptance can be claimed. |
| No measurement resource evidence | No existing Pixel/CAPI/key/event-setting evidence supplied | Pixel/CAPI test procedures are documented only. |

## Incorrect or unsafe guidance to retire

- **Do not say that the package's 14-column normalized CSV is the documented
  OpenAI CSV schema.** Official material documents export modes and examples of
  optional event-specific columns, not a complete file schema.
- **Do not call `POST /conversions/insights` a GET.** It is a documented
  retrieval endpoint using POST. Apply the acceptance task's authorized read
  scope after confirming exact target IDs, time range, and private handling.
- **Do not claim CAPI validation-only mode proves receipt or attribution.** It
  validates without saving events.
- **Do not read a country-availability gate's dated UI message as the current
  rollout state.** The official availability page is the volatile controlling
  source. Its current legal-entity condition still applies.
- **Do not treat a missing `GET /conversions/events` result as proof the Pixel
  is broken.** The endpoint itself is enabled-account-only and its documented
  `404` remediation is partner contact.

## Scope limits

No live account endpoint was issued, no secret was read, no browser control
was executed by this lane, no account was created, and no external state was
changed. This report does not establish self-service access, advertiser API
availability, a native report schema, Pixel/CAPI enablement, or delivery.
