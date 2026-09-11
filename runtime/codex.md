# Codex browser adapter

Status: procedural adapter with local record guards; no standalone account connector.

1. Discover installed browser tools. In a host exposing `mcp__cua_repl`, follow its current entrypoint documentation: select the specified browser/tab, otherwise inventory available surfaces. Do not invent APIs or selectors. A different host may expose another supported browser tool; inspect its actual contract.
2. Read the browser state and confirm signed-in advertiser/account identity against the client profile. Login, MFA and payment authorization may require the user.
3. Read the operate workflow, prepare an action plan and obtain applicable approval before external writes. Validate the plan with the local operating helper, acquire its account lock and retain the guard result.
4. Interact through fresh observed controls, re-observing after navigation and any material UI change. The helper does not prevent direct tool calls; this step is an agent obligation.
5. Check the saved object, effective configuration and delivery/review state. Record the action receipt and release the lock. Uncertain saves enter reconciliation; never retry creation blindly.

Account data and screenshots go only to the authorized private workspace. Redact evidence before sharing. Read-only native acceptance needs a real signed-in account and consent for that scope; simulated evidence does not supply it.

## Read-only browser guard

Before a consequential action, capture current visible state into the private `browser-observation.schema.json` shape. Run the companion `scripts/check_browser_action.py --action-plan A.json --reviewed-plan P.json --observation O.json --max-age-seconds 300`. It checks exact account, target, before/after settings, cost, UI revision, plan hash, active session and approval/observation timing. A tighter freshness window may be used. The historical campaign_plan_sha256 field binds the complete reviewed plan artifact even for account setup or catalog plans.

A passing report is a consistency check, not proof the observation is truthful or permission to act. Acquire the account lock through operating_core.AccountLock, re-observe immediately before the external step, and follow host-specific approval/handoff requirements. A host may require confirmation at action time for terms, access or financial steps even when a local approval record exists.

The only bundled executor is the create-campaign simulation. Real browser actions use the observed host tools and must produce separate action receipts with actual evidence; no native account behavior has been verified by this build.

Before entering a create flow, determine whether navigation itself may create a draft and whether that effect is authorized. Preserve unknown persistence and reconcile existing objects after interruption. Keyboard fallback requires an observed focused control and state reconciliation before retry; success in a localhost fixture does not establish reliability in a live account.
