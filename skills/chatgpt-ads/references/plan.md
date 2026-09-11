# Design campaign strategy and economics

## Inputs

Approved brief, primary outcome, explicit budget or request for budget scenarios, currency, timezone and evidence window.

## Procedure

1. Define the business hypothesis, funnel stage and primary success metric. Calculate break-even economics from supplied margin or lead value; show assumptions and sensitivity instead of substituting platform benchmarks.

2. Select only source-backed, account-available objectives, bid modes and targeting. Resolve daily versus total budgets, effective pacing behavior and schedule from current evidence. Never treat a payment threshold as a spend ceiling.

3. Specify campaign, ad-group and ad structure, locations/platforms, audience exclusions where available, approved creative variants and destinations. Inspect defaults and omission behavior before recommending API or bulk fields.

4. Define measurement, experiment window, reporting cadence and failure/stop conditions. Return a versioned campaign plan. Recommendations do not execute changes; use launch for a reviewable change batch.

## Output

Campaign plan with economics, configuration, evidence, constraints and success/stop criteria.

## Evidence and failure behavior

Use current source IDs from `sources.json` and check `capabilities.md` and conflicts before making platform claims. Missing decisions return `needs_input`; missing evidence returns `no_data`; unavailable tools return `capability_unavailable`; external effects lacking approval return `needs_approval`. Keep partial work and observed failures explicit.

Use the plan section of [workflow output templates](workflow-outputs.md) to structure the deliverable.

Separate owner-approved thresholds and cadence from calculated economics and proposed review rules. A calculated break-even CPA does not establish an approved weekly review window or automatic stop. Label any new timing, threshold or response as a proposal pending the relevant owner decision; conditional budget/CPA arithmetic is not a performance forecast.

Record campaign budget, account spend controls and the owner-authorized maximum effect separately. A platform-created large default limit does not authorize that spend. Observe the relevant controls and daily/total semantics before translating a scenario into an executable plan.
