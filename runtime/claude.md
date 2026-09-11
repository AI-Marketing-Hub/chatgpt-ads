# Claude browser adapter

Status: native Claude Chrome keyboard execution verified on the localhost fixture for seven scenarios and uncertain-save retry. Pointer clicks were unreliable. Native Ads account operations remain unverified. Fresh no-tool advisory probes include residual errors and require review; see the acceptance assessment.

Inspect the host's installed browser capabilities and their documentation. Browser tools, Chrome integrations and computer-use bindings are not interchangeable. If no supported browser tool is available, return `capability_unavailable` with a manual procedure; do not claim execution.

Resolve the exact tab, advertiser and account from observed UI. Use the shared operate workflow and local guard CLI through the host's authorized shell capability. If shell execution is unavailable, record the guard as unavailable and do not perform a guarded mutation through this adapter.

Use current observable controls rather than stored coordinates or guessed selectors. Recheck account and plan applicability before each consequential step. Pause for owner authentication challenges and any unapproved effect. Reconcile an uncertain save before retrying. Record a private receipt with observed object IDs and effective values.

Claude-specific acceptance requires a fresh Claude process using these files and its actual tool binding. A Codex agent reading this document is a contract review only, not a Claude runtime test. No host configuration, permissions or credentials are changed by this file.

Manual fallback instructions retain the same authorization boundary as tool execution. If an unintended campaign is found, propose pausing it and obtain applicable approval; do not silently expand authority during recovery.

## Read-only browser guard

Before a consequential action, capture current visible state into the private `browser-observation.schema.json` shape. Run the companion `scripts/check_browser_action.py --action-plan A.json --reviewed-plan P.json --observation O.json --max-age-seconds 300`. It checks exact account, target, before/after settings, cost, UI revision, plan hash, active session and approval/observation timing. A tighter freshness window may be used. The historical campaign_plan_sha256 field binds the complete reviewed plan artifact even for account setup or catalog plans.

A passing report is a consistency check, not proof the observation is truthful or permission to act. Acquire the account lock through operating_core.AccountLock, re-observe immediately before the external step, and follow host-specific approval/handoff requirements. A host may require confirmation at action time for terms, access or financial steps even when a local approval record exists.

The only bundled executor is the create-campaign simulation. Real browser actions use the observed host tools and must produce separate action receipts with actual evidence; no native account behavior has been verified by this build.

If pointer activation has no observed effect, reconcile the resulting state before trying another input method. Keyboard activation may be used only after observing the focused control; localhost success does not establish reliability in Ads Manager. The acceptance run timed out during final logging and left one local test tab in its original native session group.

Before entering a create flow, determine whether navigation itself may create a draft and whether that effect is authorized. Preserve unknown persistence and reconcile existing objects after interruption. Keyboard fallback requires an observed focused control and state reconciliation before retry; success in a localhost fixture does not establish reliability in a live account.
