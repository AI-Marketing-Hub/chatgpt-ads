# v0.2 simulated operation example

These records are local example data. `simulated-ui-state.json` is an in-memory
test-double snapshot, not an Ads Manager export or a browser adapter. The core
never accepts credentials and does not make real account, campaign, spend, or
browser changes.

The v0.2 action record can describe create, edit, status, role, audience,
catalog, bulk, and generic configuration work with target, before/after, cost,
rollback, and verification fields. The executable local guard and `check`
command currently support only the `create_campaign` simulated fixture.

Validate the records:

```bash
python3 scripts/operating_core.py validate examples/operations/client-profile.json
python3 scripts/operating_core.py validate examples/operations/campaign-plan.json
python3 scripts/operating_core.py validate examples/operations/action-plan.json
python3 scripts/operating_core.py validate examples/operations/learning-candidate.json
python3 scripts/operating_core.py check --action-plan examples/operations/action-plan.json --campaign-plan examples/operations/campaign-plan.json --state examples/operations/simulated-ui-state.json
```

Run the controlled local state-machine simulation in a private, newly created
workspace. Its checkpoint log is appended at `operations/operation-demo.jsonl`.

```bash
mkdir -p /tmp/chatgpt-ads-operation-demo
cp examples/operations/simulated-ui-state.json /tmp/chatgpt-ads-operation-demo/state.json
python3 scripts/operating_core.py simulate-execute \
  --action-plan examples/operations/action-plan.json \
  --campaign-plan examples/operations/campaign-plan.json \
  --state /tmp/chatgpt-ads-operation-demo/state.json \
  --workspace /tmp/chatgpt-ads-operation-demo \
  --operation-id operation-demo \
  --receipt-out /tmp/chatgpt-ads-operation-demo/receipt.json
```

The approval hash is a SHA-256 of the exact canonical JSON serialization of the
`action` object: sorted keys, compact separators, UTF-8, and no extra fields.
It records review provenance only. It is not authentication or authorization.
If a save acknowledgement is uncertain, the core reconciles using the campaign
identifier and action hash before it can make another attempt.

`promote_learning_candidate()` is a library-only helper used after reviewer
acceptance. It creates a new shared JSON file with only the reviewed general
text, public-safe evidence and review hashes, and supersession hashes. It rejects client-specific candidates and never
writes the candidate's evidence, client ID, or reviewer identity to the shared
target.
