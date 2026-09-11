# Design and validate measurement

## Inputs

Business conversion definition, event sources, value basis, currency, consent requirements and account setup evidence.

## Procedure

1. Map business events to currently documented platform events. Separate received events, attributed conversions, view-through outcomes and optimization signals. Do not infer an event is supported from a familiar cross-platform name.

2. Design event IDs, browser/server deduplication, matching inputs, timestamps, value/currency handling and consent suppression. If repeated event IDs carry conflicting values, hold the conflicting group for reconciliation. Do not choose the server value, first arrival, or a native deduplication algorithm without documented business authority and platform evidence. Keep business-order counts distinct from received and attributed conversions. Unknown consent suppresses transmission; retention of identifiers also needs a defined lawful purpose and approved retention policy, not an assumed default. Document redirects and click-identifier handling without putting real identifiers in the brain.

3. Prepare test events and expected outcomes, including duplicate, late, invalid-value and no-consent cases. Deployment and sending events are external effects routed through exact approved plans.

4. Reconcile platform counts against eligible backend events using compatible windows and lag. Explain discrepancies and missing visibility rather than forcing totals to match. Record partner capabilities separately.

## Output

Event mapping, implementation proposal, test protocol, reconciliation and production evidence requirements.

## Evidence and failure behavior

Use current source IDs from `sources.json` and check `capabilities.md` and conflicts before making platform claims. Missing decisions return `needs_input`; missing evidence returns `no_data`; unavailable tools return `capability_unavailable`; external effects lacking approval return `needs_approval`. Keep partial work and observed failures explicit.

Use the measurement section of [workflow output templates](workflow-outputs.md) to structure the deliverable.

## Evidence table required in the deliverable

Keep these stages separate: `local_eligible_events`, `outbound_attempts`, `native_validation_response`, `native_received_events`, `attributed_conversions`. Unknown native values are null, including received events when no account receipt was inspected. A held event is ineligible locally; it does not establish a native count of zero. Business-order counts are not native conversion counts.

For a local stub, expected results say locally eligible or held, never platform received. For CAPI validate-only, a successful result establishes only `native_validation_response_verified`, not storage, receipt or attribution. Sending a validation request transmits data and is not an account read-only inspection. A stored staging event is also an external action. Use `native_event_receipt_verified` only after actual receipt evidence. These are narrow evidence details, not permission to mark the entire workflow verified. Account read-only evidence comes from actual account reads. Any action receipt must retain whether the request validated only or saved events.

Never invent late-event acceptance, native matching fields, or deduplication rules. Where the current source/account contract is unavailable, leave native expected behavior unresolved and provide only the declared business-side rule.

Use consistent local dispositions: invalid values or currencies under the declared business contract are rejected before sending; repeated IDs with conflicting otherwise valid fields are held for reconciliation. Both are ineligible for transmission. These are local preparation outcomes, not claims about native API acceptance.
