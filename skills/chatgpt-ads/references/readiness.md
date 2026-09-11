# Establish client and account readiness

## Inputs

Business objective, client identity, supplied offer/claims, market and any account evidence.

## Procedure

1. Extract known inputs first. Record business model, approved offer and claims, destinations, geography, category, primary outcome, conversion value basis and economics. Missing decisions are needs_input; missing evidence is no_data.

2. Create a client/account profile only in the authorized private workspace. Resolve exact account identity, currency, timezone and access route; credentials are reference names only. Record unavailable tooling.

3. Check current market/category eligibility, verification, role and billing requirements from source evidence and account UI. Record each as documented, observed or missing. Opening a page is not proof setup is complete.

4. Agree data purpose, access audience, retention/deletion responsibility and private evidence destination before ingesting client exports. Produce an ordered blocker list. Route account setup changes through operate.

## Output

Client/account profile, readiness findings, missing decisions and prioritized next actions.

## Evidence and failure behavior

Use current source IDs from `sources.json` and check `capabilities.md` and conflicts before making platform claims. Missing decisions return `needs_input`; missing evidence returns `no_data`; unavailable tools return `capability_unavailable`; external effects lacking approval return `needs_approval`. Keep partial work and observed failures explicit.

Use the readiness section of [workflow output templates](workflow-outputs.md) to structure the deliverable.

Keep account access, verification, billing/profile completeness, ad review and delivery readiness as separate fields. A banner establishes the blockers it displays, not an exhaustive guarantee. Preserve the observed timezone label and obtain an IANA timezone identity when needed; a date-specific UTC offset does not establish daylight-saving behavior. Do not infer the cause of a different account's access gate from one working account.

Read-only readiness checks must not enter a create flow whose draft persistence is unknown. Establish its effects through passive documentation or existing-state evidence first; any potentially stateful inspection needs applicable authorization. Use the operate and launch procedures when prescribing next operational steps.
