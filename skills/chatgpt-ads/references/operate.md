# Operate an authorized account through observed controls

## Inputs

Exact client/account profile, reviewed action plan, actual human authorization and supported runtime tools.

## Procedure

1. Read the relevant runtime adapter and inspect actual tool availability. Verify account identity and current UI, then validate action applicability through `scripts/check_browser_action.py` in the companion root. Acquire one account lock for the operation.

2. Use observed controls to perform the approved sequence. Recheck after navigation and material changes. Never guess hidden APIs, bulk headers, object IDs or stale coordinates. Account setup, audiences and feeds use the specialized operation recipes.

3. After each consequential save, observe object identity and effective settings. If the outcome is uncertain, record uncertainty and reconcile by current state before retrying. A successful click is not a successful save.

4. Write an action receipt with observations, object IDs, actual settings, partial effects and verification. Release the lock on known completion; unresolved operations retain explicit recovery state. Pausing or correcting an unintended campaign is another external effect and requires applicable authorization, even in manual fallback instructions. Propose that action rather than instructing an unapproved pause. Pause cannot refund spent money.

5. If reconciliation restores the exact originally approved account, settings and scope and the approval is still valid, reuse it; do not request duplicate confirmation. A changed action or a corrective pause outside that scope needs a new decision. If authentication, payment, access or new approval is required, preserve the checkpoint and hand the exact missing decision to the owner. Do not bypass host restrictions.

## Output

Private action receipt and checkpoint, with verified effects or explicit failure/uncertainty.

## Evidence and failure behavior

Use current source IDs from `sources.json` and check `capabilities.md` and conflicts before making platform claims. Missing decisions return `needs_input`; missing evidence returns `no_data`; unavailable tools return `capability_unavailable`; external effects lacking approval return `needs_approval`. Keep partial work and observed failures explicit.

Read [operation recipes](operation-recipes.md) and the applicable [Codex](../../../runtime/codex.md) or [Claude](../../../runtime/claude.md) adapter. The full companion package is required for guarded operation.

Use the operate section of [workflow output templates](workflow-outputs.md) to structure the deliverable.

Opening a create flow may generate or persist a draft. In a strictly read-only task, inspect existing objects and passive controls first; do not enter a potentially stateful flow unless its effects are understood and authorized. A discard dialog does not prove server-side non-persistence. After uncertain draft creation, reconcile actual objects before retrying; preserve unknown state when evidence is absent.
