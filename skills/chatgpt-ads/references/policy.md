# Review policy and privacy requirements

## Inputs

Creative/destination or proposed data flow, advertiser category, geography and intended operation.

## Procedure

1. Retrieve the relevant current official policies and terms. Keep platform requirements, legal obligations and account enforcement separate. For legal interpretation, identify jurisdiction and instrument; unresolved legal conclusions go to qualified review.

2. Check claim substantiation, destination integrity, restricted categories, placement context, audience eligibility, data sourcing and consent. A broad label such as household goods does not establish every product is eligible. If product details are absent, keep category clearance unresolved rather than assuming there is no restricted-category issue. Record exact evidence and disputed wording.

3. For data flows, record purpose, fields, recipients, access, storage, retention, deletion owner and verification method. Do not call hashes anonymous or collect sensitive examples into the shared pack.

4. Return clear blockers, conditional findings and approved content boundaries. Any safer copy draft must use only facts supplied in the approved brief. Do not invent product ranges, delivery, discounts, scarcity, guarantees or other replacement claims. Use explicit placeholders where needed, and distinguish a conditional draft from an approved ad. Previous ad approval does not validate a changed offer. Remediation is drafted; account appeals or third-party contact need explicit authorization.

## Output

Evidence-cited findings with severity, remediation and remaining owner/legal decisions.

## Evidence and failure behavior

Use current source IDs from `sources.json` and check `capabilities.md` and conflicts before making platform claims. Missing decisions return `needs_input`; missing evidence returns `no_data`; unavailable tools return `capability_unavailable`; external effects lacking approval return `needs_approval`. Keep partial work and observed failures explicit.

Use the policy section of [workflow output templates](workflow-outputs.md) to structure the deliverable.
