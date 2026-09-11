# Analyze compatible reports and diagnose performance

## Inputs

Authorized sanitized aggregate export, account reference, period, currency, timezone, attribution and conversion meaning.

## Procedure

1. Use a versioned native mapping only if its exact headers and semantics are established. Otherwise map manually into the normalized contract with provenance. Familiar columns alone do not establish native support.

2. Validate source grain, duplicates, dates, units, missing values, account boundaries and compatible attribution before aggregation. Preserve original fields and transformation metadata privately. Use the bundled analyzer for its supported normalized shape.

3. Diagnose eligibility and delivery before creative or conversion performance. Separate platform credit, backend revenue and incremental effects. Calculate compatible weighted rates and economics; make uncertainty and lag explicit.

4. Never calculate or label native CPA, post-click CVR or optimized conversions by adding VTA to click conversions. Report VTA separately. A request for a combined total does not establish deduplication or justify a blended CPA; withhold it unless an independently defined, reconciled metric is explicitly supplied. Produce a decision report with observations, hypotheses and prioritized tests. Any budget, bid, audience or status change becomes an action proposal, not an automatic optimization.

## Output

Validated analysis, data-quality findings, diagnostic report and evidence-linked change proposals.

## Evidence and failure behavior

Use current source IDs from `sources.json` and check `capabilities.md` and conflicts before making platform claims. Missing decisions return `needs_input`; missing evidence returns `no_data`; unavailable tools return `capability_unavailable`; external effects lacking approval return `needs_approval`. Keep partial work and observed failures explicit.

Use [normalized analysis contract](normalized-analysis.md). Native mappings and their limitations are in [adapter manifest](../../../references/adapter-manifest.json).

Use the analyze section of [workflow output templates](workflow-outputs.md) to structure the deliverable.

First classify the file as reporting data or a bulk-edit template. A template is not a performance report. Distinguish attribution-comparison columns from event attribution configuration and conversion-time versus interaction-time reporting. Observe exact metric definitions before mapping. Preserve locale decimal conventions and modeled/fractional values in the source; never round them to satisfy the current whole-number conversion contract. Return unsupported mapping when the supplied data cannot be represented faithfully.

A bare attribution label does not establish even whether it is a comparison column or a configuration control. Record that semantic distinction as unknown until the surrounding UI or native documentation establishes its purpose.
