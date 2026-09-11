# Prepare and verify an exact campaign change

## Inputs

Campaign plan, approved assets, account profile, current settings and measurement/policy findings.

## Procedure

1. Confirm readiness for the exact account and intended objects. Inspect current effective settings and available controls. Complete creative, destination and measurement checks that are possible before requesting execution approval.

2. Produce an action plan containing before/after settings, object identities, budget effects, explicit ceiling, time window, preconditions, recovery limits and verification steps. Freeze and hash the reviewed artifact.

3. Use applicable human approval for the exact action batch. Changed scope, cost, target or material state requires a new decision. Approval records do not authenticate the person or supply an absent browser capability.

4. Hand the approved batch to operate. Evaluate the resulting receipt: saved, under review, delivering and failed are different outcomes. Record native evidence and unresolved delayed states.

## Output

Reviewable action plan, preflight evidence and, after authorized execution, launch acceptance or unresolved status.

## Evidence and failure behavior

Use current source IDs from `sources.json` and check `capabilities.md` and conflicts before making platform claims. Missing decisions return `needs_input`; missing evidence returns `no_data`; unavailable tools return `capability_unavailable`; external effects lacking approval return `needs_approval`. Keep partial work and observed failures explicit.

Read [operation recipes](operation-recipes.md) and the applicable [Codex](../../../runtime/codex.md) or [Claude](../../../runtime/claude.md) adapter. The full companion package is required for guarded operation.

Use the launch section of [workflow output templates](workflow-outputs.md) to structure the deliverable.

Use [release preflight](release-preflight.md) for automated creative controls, effective spending limits and draft state. Include observed defaults and intended automation settings in the reviewed plan and exact action before/after fields so a changed toggle invalidates the original batch. Unknown material settings remain unresolved; do not substitute a platform default for the client's authorized spending ceiling.
