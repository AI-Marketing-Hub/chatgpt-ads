# Create substantiated ads and destination briefs

## Inputs

Approved offer, audience, claims/evidence, destination and available creative assets/rights.

## Procedure

1. Load current format specifications and account-supported creative types. Distinguish recommendations from enforced maxima; verify images and URL requirements before export.

2. Draft variants around distinct hypotheses. Keep price, availability, benefit and call to action consistent with the destination. Mark every unsupported claim as a question, not finished copy.

3. Review mobile rendering, legibility, accessibility, crawlability, redirect behavior and relevant policy. Observe the actual destination when available; record unavailable visual checks.

4. Provide a creative manifest tying each variant to its claim evidence, asset provenance, destination and experiment. For catalogs, check product identity, pricing and inventory consistency. Asset generation or publication requires its own available tooling and authorization.

## Output

Copy/asset brief, variant manifest, destination findings and unresolved rights or claim decisions.

## Evidence and failure behavior

Use current source IDs from `sources.json` and check `capabilities.md` and conflicts before making platform claims. Missing decisions return `needs_input`; missing evidence returns `no_data`; unavailable tools return `capability_unavailable`; external effects lacking approval return `needs_approval`. Keep partial work and observed failures explicit.

Use the creative section of [workflow output templates](workflow-outputs.md) to structure the deliverable.

Preserve the exact meaning of approved offer terms. A 30-day return window does not establish a trial, satisfaction guarantee, free returns, or acceptance of used goods. Use the approved return wording and its policy qualifier unless additional evidence supports broader language.

When the account exposes automatic text personalization, translation or asset variations, record the observed setting and the owner-approved extent of those changes. Approved source copy does not establish approval of every generated variation. This is a conditional review requirement, not a claim that every account supports the feature.

Before returning the creative deliverable, remove language you have identified as unsupported or misleading. Keep rejected alternatives in review findings, not in the variants offered for use.
