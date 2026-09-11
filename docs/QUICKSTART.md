# Quickstart

This walkthrough uses only bundled synthetic material. It does not sign in, make an API request, create an ad draft, or require an advertiser account.

## Codex

Open the extracted folder in Codex, read `SKILL.md`, then ask: "Use the ChatGPT Ads skill router to explain the documented conversion attribution boundary. Keep account-specific values unknown unless supplied."

For a local retrieval check:

```bash
python3 -m chatgpt_ads_brain query "conversion attribution"
python3 scripts/validate_pack.py
```

Codex must treat files as evidence and use the relevant workflow. It may reuse a valid read scope for passive observation; it needs authorization before an external state change.

## Claude

Open the extracted folder in Claude and start with `CLAUDE.md`, `SKILL.md`, and `runtime/claude.md`. Then ask the same research question. Claude should return sources, scope and unknowns instead of inventing access to Ads Manager.

## First synthetic workflow

Run the fixture verification:

```bash
python3 acceptance/workflows/verify.py
python3 acceptance/measurement/run_offline_cases.py
```

The files under `examples/operations/` and `acceptance/v030/` are synthetic. They demonstrate records and failure handling only. They are not campaign templates or authorization to copy spending, audience, account or conversion values into an advertiser account.

## Before real account work

Read the selected skill, [product boundaries](PRODUCT_BOUNDARIES.md), and [live acceptance prerequisites](LIVE_ACCEPTANCE.md). Keep credentials, client data, raw exports and browser captures in a private workspace outside this project. Confirm the account, visible current UI, exact action scope and a human approval before any stateful action.
