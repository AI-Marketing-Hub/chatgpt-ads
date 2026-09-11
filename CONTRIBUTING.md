# Contributing

Keep changes small, sourced and testable. Read `README.md`,
`docs/PRODUCT_BOUNDARIES.md`, and the relevant skill before changing a workflow.

- Do not commit credentials, client data, raw browser captures, raw exports,
  local paths, copied third-party material with unclear rights, or generated
  release archives.
- Keep documented facts, account observations and inferences distinct. Changes
  to canonical sources need locator, scope, freshness and an affected-guidance
  review.
- Add focused tests for changed behavior and run the checks in
  `docs/OPERATOR_KIT.md`.
- Test public-release changes with `scripts/prepare_public.py` in a new
  temporary directory. Never add a broad directory to its allowlist merely to
  make a missing file available.
- Issues and pull requests must not contain secrets or client information.

Contributions do not grant account authority. Browser, API, billing and
campaign actions remain subject to the operator's separate approval.
