# ChatGPT Ads

![ChatGPT Ads: Research. Plan. Create. Measure.](assets/chatgpt-ads-cover.webp)

An independent, MIT-licensed knowledge and operating-skill pack for research, planning, creative, measurement, analysis and guarded ChatGPT Ads workflows. It is not an OpenAI product, integration, endorsement, account connector or production certification. Account access, billing, approval, ad review and delivery must be established separately for each advertiser.

Version 0.3.1 is the audit-hardening update to the published v0.3.0 release. It includes documented source knowledge, synthetic fixtures and deterministic helpers. It does not include private workspaces, browser captures, credentials, raw research, customer data or an account capable of running ads.

[![CI](https://github.com/agricidaniel/chatgpt-ads/actions/workflows/ci.yml/badge.svg)](https://github.com/agricidaniel/chatgpt-ads/actions/workflows/ci.yml)

![Illustration of campaign planning, creative review and performance analysis](assets/chatgpt-ads-workflow.webp)

*Conceptual workflow illustration, not a product dashboard or evidence of live campaign results.*

## Start here

- [Beginner quickstart](docs/QUICKSTART.md), including a synthetic first run.
- [Knowledge index](brain/index.md) and the [12-skill router](skills/chatgpt-ads/SKILL.md).
- [Operator kit](docs/OPERATOR_KIT.md), for verification and local packaging.
- [Support policy](SUPPORT.md), [contributing guide](CONTRIBUTING.md), and [security guidance](SECURITY.md).
- [Product boundaries](docs/PRODUCT_BOUNDARIES.md) and [live-account prerequisites](docs/LIVE_ACCEPTANCE.md).

## Use from the folder

Use Python 3.11 or later. No account credentials or global installation is needed for the synthetic walkthrough. Clone or extract the full repository, keep its sibling folders together, create a local virtual environment, then run:

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --require-hashes -r requirements/validation.txt
python3 -m chatgpt_ads_brain query "conversion attribution"
python3 scripts/knowledge_core.py validate
python3 scripts/validate_pack.py
```

The package deliberately does not advertise a global command: its helpers load the bundled source registries, skills and fixtures by relative path. The install above adds local schema validation and the timezone database required by the analyzer on Windows. Run tools from the complete source folder.

## Supported environments

| Environment | Status | Scope |
| --- | --- | --- |
| Linux, Python 3.11 and 3.14 | Hosted CI passed on v0.3.0; the live badge tracks the current revision | Retrieval, validation, synthetic workflows and packaging |
| Windows, Python 3.11 and 3.14 | Hosted restriction checks passed on v0.3.0; guarded operations unavailable | Read [Windows boundary](docs/WINDOWS.md) and use `python scripts/doctor.py`; guarded filesystem and browser workflows fail closed because no native backend is implemented |
| macOS | Not yet verified | Do not treat it as a supported runtime |

The tools never authenticate an advertiser, perform browser actions on their own, or establish campaign performance. Read the selected skill and runtime guide before account work. Private account records belong outside this tree.

## Public-release boundary

`scripts/prepare_public.py` makes a separate source tree from an explicit allowlist. `scripts/package_release.py` accepts only that prepared tree and creates a deterministic archive. Neither command publishes, installs globally, contacts a third party or certifies a live account. Existing v0.2.1 archives are historical artifacts and are never overwritten.

Repository: [agricidaniel/chatgpt-ads](https://github.com/agricidaniel/chatgpt-ads). Download versioned ZIPs and checksums from [Releases](https://github.com/agricidaniel/chatgpt-ads/releases). See [CHANGELOG.md](CHANGELOG.md) for upgrade notes and [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) for license provenance.
