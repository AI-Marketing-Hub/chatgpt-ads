# Account operation recipes

These recipes select what to inspect. Current UI and documented feature availability determine the actual controls. Each external change follows the operate workflow and an exact approved action plan.

## Account setup and roles

Confirm advertiser identity and selected account. Inspect verification, business details, currency/timezone, billing and current roles. Prepare the smallest change. Owner handles authentication and confirms payment or permission changes. Verify completed state; do not repeat an invitation or payment submission after an uncertain response.

## Campaign creation and edits

Inspect existing objects first. Bind a unique local operation ID to the intended campaign. Record objective, schedule, budgets, bidding, targeting, creative and measurement. Review defaults before saving. After save, record the platform object ID and read back effective settings. If an object may already exist, reconcile before retrying. A draft, review-pending ad and delivering campaign have separate receipt states.

## Audiences

Verify account feature availability, eligibility, approved data purpose and supported identifiers. Keep raw identifiers private. Capture inclusion/exclusion semantics and match status without exporting member data to the brain. Upload success is not audience readiness. Changes to recipients or purpose need owner review.

## Catalogs and feeds

Verify feed ownership, supported source route, item IDs, price/currency, inventory, destination and update schedule. Review a sanitized sample and diagnostics before proposing import. After approval, inspect accepted/rejected items and refresh status. Confirm campaign product filters separately. Reconcile uncertain imports using existing feed identity.

## Bulk changes

Obtain the current native template from official docs or observed account export. Preserve the original privately and generate a diff for only the approved objects. Reject ambiguous IDs, unsupported columns and scope expansion. After upload, inspect per-row outcomes and read back affected objects. A partially successful batch needs reconciliation, not a blind full retry.

## Pause, incident and recovery

Inspect current delivery and pending effects. Pause only with applicable approval; record observed status and any delayed billing. Restore only the approved prior configuration and only when still valid. Do not delete objects to conceal an unsuccessful run. Persist unresolved effects for the next operator.
