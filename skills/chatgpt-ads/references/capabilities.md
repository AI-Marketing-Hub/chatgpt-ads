# Capability map

Generated navigation. Canonical capability states are in the companion root `references/capabilities.json`. No account has been verified by this package.

- [Platform findings](platform-findings.md)
- [Measurement findings](measurement-findings.md)
- [Policy findings](policy-findings.md)
- [Terms findings](terms-findings.md)

## Conflicts

### platform-contradiction-001

The September 10 Help article documents oCPC and oCPM, with oCPM in beta and expanding. The campaign overview still lists only CPM, CPC, and oCPC. The public API documents impressions, clicks, and conversions, where conversions maps to oCPC, and gives no oCPM representation.

Treat oCPM as account-dependent Ads Manager beta. Treat oCPM via API as unsupported until the API contract is updated.

### platform-contradiction-002

Create Campaigns says campaign-total can be changed to daily but not changed back. Billing & Payment says budget type cannot be changed after creation.

Do not automate a budget-type change. Create a new campaign unless the current account UI and support-confirmed behavior establish otherwise.

### platform-contradiction-003

The task seed named ads.chatgpt.com, but all current official operating docs use ads.openai.com. ads.chatgpt.com was not retrievable in this environment.

Use ads.openai.com as the documented route and retain ads.chatgpt.com as unverified.

### measurement-contradiction-vta-optimization

Measure Results and Measurement Pixel say VTA is supplemental and does not affect bidding or conversion optimization.

Resolved as distinct concepts in the 2026-09-10 refresh: displayed VTA is supplemental only; broader oCPM eligible signals do not establish displayed VTA as an optimization input. Native/account behavior remains untested.

### policy-contradiction-regulated-contexts

The Help Center FAQ says ads are not eligible near sensitive or regulated topics, including personal health, mental health, or politics. The Ad Policies changelog says medical, legal, and financial advice contexts are no longer categorically blocked by default as of April 2026, while sensitive conversations remain ineligible. The primary policy is more specific and later amended, so use its precise placement list; do not promise delivery in regulated advice contexts.

Unresolved; inspect canonical conflict record.

## Local capabilities

Normalized aggregate analysis and local operating guards are implemented. Browser procedures require available host tools and exact-action authorization. Native API integration and native CSV mapping remain unavailable. Read `sources.json`, `claims.json` and `contradictions.json` for provenance.
