# v030 synthetic preflight workflow result

## Scope and evidence

This is an advisory result produced from the synthetic fixture in `acceptance/v030/fixture.json` as of 2026-09-11. The fixture SHA-256 is `74e77cc5e6d3823a1e43bf20314da217a1be6ab80f2c541893c5c1218ee77e59`. No real account, network source, browser control, account mutation, campaign execution, or monitoring schedule was used. The fixture's account reference is intentionally not reproduced.

The decision uses the local workflow contracts in `skills/chatgpt-ads/references/readiness.md`, `plan.md`, `creative.md`, `analyze.md`, and `monitor.md`. All account observations below are **synthetic observations**, not native account verification.

## Decision

| Workstream | Disposition | Decision |
| --- | --- | --- |
| Readiness | **Blocked for execution** | Billing is incomplete, the logo is missing, account changes are not authorized, and the proposed EUR 200 campaign budget is not approved. Required business, destination, measurement, and timezone decisions are also missing. |
| Campaign plan | **Needs input and approval** | A bounded draft plan can be prepared, but objective, conversion definition, economics, audience, target geography, destination, budget semantics, and measurement route are unresolved. |
| Creative | **Conditional review draft** | The copy below uses only the supplied price and approved claims. It still requires destination, format, asset-rights, and personalization review before use. |
| Analysis | **No data / unsupported mapping** | The supplied artifact is an empty bulk-edit template, not a performance report. The separate fractional metric sample cannot be represented faithfully by the current normalized whole-number conversion contract. |
| Monitoring | **Read-only repull now, no schedule** | Treat the lag case as a stale completeness incident, repull within the authorized read scope, and exclude the incomplete row from pacing. The approved EUR 65.60 zero-purchase rule is not currently evaluable. |

## Readiness finding

### Synthetic account and business profile

- Product: Cork desk mat.
- Price: EUR 80.
- Approved claims: `Cork surface`; `30-day return window under the published policy`.
- Account country: Spain.
- Currency: EUR.
- Observed timezone label: `Madrid UTC+02:00`.
- IANA timezone identity: **unknown**. The supplied label does not establish daylight-saving behavior.
- Read-only account inspection: authorized in the fixture.
- Account changes: not authorized.
- Campaign inventory: empty in the fixture. This does not prove a real account has no campaigns.
- Synthetic blockers displayed: `Billing profile incomplete`; `Logo missing`.
- Synthetic text-personalization setting: enabled. The approved claims do not approve generated variations.
- Synthetic account default limit: EUR 1,000,000,000. This is an observed platform value, not an owner-authorized spend ceiling.
- Proposed campaign budget: EUR 200. Execution approval: **absent**.
- Create flow: not opened. Persistence behavior and defaults: **unknown**.

### Missing decisions and evidence

| Item | State | Why it matters | Resolution |
| --- | --- | --- | --- |
| Business objective and funnel stage | `needs_input` | No primary outcome can be selected. | Owner defines the campaign objective in business terms. |
| Conversion definition and value basis | `needs_input` | Success, break-even economics, and measurement cannot be defined. | Owner defines the conversion event and contribution value or margin. |
| Target geography and audience | `needs_input` | Account country is not evidence of campaign targeting intent. | Owner supplies target market, audience, and exclusions. |
| Destination URL and landing-page state | `needs_input` | Copy continuity, price, return wording, crawlability, and conversion path cannot be checked. | Supply the exact destination and approve inspection. |
| Creative assets and rights | `no_data` | No logo or ad asset provenance was supplied. | Supply the approved logo/assets and rights record. |
| Billing and logo completion | `blocked` | The synthetic UI identifies both as blockers. | Inspect details read-only, then obtain authorization for the exact account changes. |
| IANA timezone | `needs_input` | Scheduling and daily reporting boundaries remain ambiguous. | Confirm the account's IANA timezone in the account UI. |
| Budget semantics and create-flow defaults | `no_data` | Daily versus total budget and persistence behavior were not observed. | Inspect the current create flow without saving or entering values that may persist. |
| Budget and external action approval | `needs_approval` | EUR 200 is proposed only, and campaign creation would change the account. | Approve the exact reviewed action batch and maximum spend effect separately. |

**Readiness verdict: blocked for campaign execution.** Read-only inspection may continue within the fixture's authorized scope. Account setup changes, campaign creation, spend, and automatic edits remain outside that scope.

## Draft campaign plan

- Plan ID: `v030-cork-mat-draft-v1`.
- Currency: EUR.
- Timezone: preserve `Madrid UTC+02:00` as the observed label; scheduling remains unset until an IANA timezone is confirmed.
- Business hypothesis: **unknown pending owner input**. No demand or performance claim is inferred from the fixture.
- Primary outcome and conversion definition: **unknown**.
- Unit economics: price is EUR 80; contribution margin, variable cost, refund cost, and customer value are absent. Break-even CPA and ROAS are therefore not calculable.
- Proposed maximum campaign effect: EUR 200, pending explicit approval. The synthetic EUR 1,000,000,000 account limit is excluded from the authorization boundary.
- Budget mode and pacing: **unknown** until the current create-flow controls are observed.
- Proposed structure after inputs are resolved: one campaign hypothesis, one approved audience cell, and the three copy variants below. Objective, bid mode, placement, targeting, and exclusions remain unset rather than being borrowed from another platform.
- Measurement: define one primary conversion, its business meaning, attribution semantics, validation method, and reporting window before launch.
- Review rule: the owner-approved EUR 65.60 spend with zero purchases triggers a review only. It does not authorize an automatic pause, bid change, budget change, or campaign edit.
- Experiment window and routine cadence: **unknown**. No schedule is created.

## Usable draft copy

These variants are ready for owner and destination review. They are not launch-approved assets.

| Variant | Intended context | Headline | Primary text | CTA draft | Substantiation | Test hypothesis |
| --- | --- | --- | --- | --- | --- | --- |
| `cork-material-v1` | Material-led message; audience unknown | Cork surface for your desk | Cork desk mat. EUR 80. 30-day return window under the published policy. | View details | Product, price, and both approved claims from the fixture | Leading with the material earns more qualified destination visits than leading with price or return terms. |
| `cork-price-v1` | Price-led message; audience unknown | Cork desk mat. EUR 80. | Cork surface. 30-day return window under the published policy. | View details | Product, price, and both approved claims from the fixture | Clear price disclosure earns more qualified destination visits than the other approved messages. |
| `cork-returns-v1` | Return-policy-led message; audience unknown | 30-day return window | EUR 80 cork desk mat with a cork surface. 30-day return window under the published policy. | See details | Product, price, and both approved claims from the fixture | Leading with the exact return-window wording earns more qualified destination visits than material or price first. |

Creative restrictions for review:

- Keep the return wording tied to the published policy. Do not rewrite it as a trial, guarantee, free returns, risk-free purchase, or acceptance of used goods.
- Do not add comfort, durability, sustainability, protection, quality, shipping, inventory, or performance claims without evidence.
- Destination URL, format limits, rendering, accessibility, crawlability, redirect behavior, logo/assets, and asset rights are unknown and untested.
- Because synthetic text personalization is enabled, either bind allowed transformations to the approved claims and review generated variants, or change that account setting only after exact authorization. The copy above does not approve every generated variation.

## Analysis disposition

### Export artifact

- Label: `Export for editing`.
- Fixture kind: `bulk_edit_template`.
- Rows: none.
- Classification: **not a performance report**.
- Disposition: do not pass it to `skills/chatgpt-ads/scripts/analyze.py`; do not infer zero impressions, clicks, spend, purchases, or revenue from the empty rows.
- Result status: `no_data` for performance analysis.

### Separate unmapped metric sample

| Source field | Preserved value | Disposition |
| --- | --- | --- |
| Conversion value text | `2,5` | Under the supplied `es-ES` locale this is a decimal-comma value with a candidate numeric interpretation of 2.5. Its business and metric definition are unknown. If it is a conversion count, the current normalized contract requires a whole number, so it must not be rounded or ingested. |
| Attribution label | `Click attribution 7 days` | A bare label does not establish whether this is a comparison column, a reporting definition, or an event-setting control. Preserve it as unmapped source text. |
| Event-setting window | `null` | The configured attribution window is unknown. Do not infer it from the label. |

Disposition: **unsupported mapping**. The sample is separate from the empty template and cannot be joined to it. Obtain a sanitized performance export with exact native headers, row grain, report window, currency, IANA timezone, conversion definition, attribution meaning, account boundary, and completeness status. Then record a manual mapping and provenance. Use the normalized analyzer only if every value can be represented without rounding or semantic substitution.

No performance totals, rates, CPA, ROAS, or diagnosis are produced.

## Monitoring decision

### Lag and completeness case

The synthetic case supplies a 2026-09-07 report date with only 12 hours covered, a 24-hour lag, and an as-of date of 2026-09-10. For a daily row using the supplied Madrid UTC+02:00 label, the reporting day ends at the start of 2026-09-08 local time and the 24-hour lag window ends at the start of 2026-09-09. By the supplied as-of date, the 12-hour row is stale and incomplete. The date-only as-of value prevents an exact timestamp calculation, but it does not change this disposition.

- Classify this as a **stale completeness incident**, not a healthy partial day or a zero-performance day.
- Repull the 2026-09-07 report and verify currency, timezone, row grain, and completeness. This read-only action is already within the fixture's authorized inspection scope.
- Exclude the incomplete row from pacing and threshold evaluation until it is reconciled.
- If the repull remains incomplete, escalate it as a reporting-data incident and retain the missing values as null.

### Approved zero-purchase rule

- Rule on record: review when spend reaches EUR 65.60 with zero purchases.
- Approval scope: review trigger only.
- Current evaluation: **not measurable**. The fixture supplies no compatible spend or purchase report, and the rule's aggregation window is not defined.
- Required resolution: owner defines the evaluation window; the operator applies the rule only to complete, compatible data.
- If triggered, produce a diagnostic review covering delivery, tracking, destination, and creative evidence. Do not automatically pause or edit the campaign because account changes are not authorized.

### Scheduling

No cadence was requested, so scheduling remains disabled. The next action is a one-time read-only repull and reconciliation, followed by an owner decision on monitoring window and cadence.

## Ordered operational steps

1. Repull and reconcile the stale 2026-09-07 report within the authorized read-only scope. Keep incomplete measurements null.
2. Privately verify the exact account identity, IANA timezone, billing blocker detail, logo requirement, text-personalization control, and create-flow persistence/defaults. Do not save account or campaign changes during inspection.
3. Obtain the business objective, target geography, audience, destination, conversion definition, contribution margin or conversion value, approved assets/rights, measurement route, experiment window, and monitoring aggregation window.
4. Inspect the exact destination and current account-supported format/configuration before finalizing copy, assets, objective, bidding, targeting, budget mode, or measurement fields.
5. Produce a versioned action proposal capped at EUR 200, with exact before/after state, campaign objects, personalization scope, budget effects, recovery limits, and post-save verification.
6. Obtain separate authorization for billing/logo account changes, the campaign action batch, and the EUR 200 maximum spend effect. Approval of one does not imply approval of the others.
7. After blockers are cleared, re-observe the account, revalidate the exact batch, execute only through an available verified controller, and record actual effects separately from this advisory result.

