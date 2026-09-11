# Operator kit

Run these commands from a complete source checkout or extracted public archive. Use Python 3.11 or newer. The tools read bundled files by relative path, so do not copy one script into a different directory or install it globally. For schema checks, create a local virtual environment and install the declared optional dependency: `python3 -m venv .venv && . .venv/bin/activate && python -m pip install "jsonschema>=4,<5"`.

## Deterministic checks

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
python3 -m unittest discover -s skills/chatgpt-ads/tests -p 'test_*.py'
python3 scripts/knowledge_core.py validate
python3 scripts/knowledge_core.py sync-projection --check
python3 scripts/validate_pack.py
python3 acceptance/workflows/verify.py
python3 acceptance/measurement/run_offline_cases.py
python3 scripts/doctor.py
```

These establish local structure and helper behavior. They do not prove that a source remains current, that an account is eligible, that a browser can reach Ads Manager, or that a campaign will deliver.

## Pack a reviewed public source

Build into new paths. Existing archives are intentionally immutable.

```bash
python3 scripts/prepare_public.py --out /tmp/chatgpt-ads-brain-public
python3 /tmp/chatgpt-ads-brain-public/scripts/package_release.py --source /tmp/chatgpt-ads-brain-public --out /tmp/chatgpt-ads-brain-v0.3.0.zip
```

The first command copies only its explicit allowlist and writes `PUBLIC_PROJECTION.json` with per-file hashes. The second verifies those hashes and refuses raw, private, review, legacy, symlink, local-home-path and common secret-pattern entries. Hashes check file integrity, they are not a signature. Review the projected file list manually before any publication. Packaging is still a local action, not a release.

## Research and account work

Start with `brain/index.md`, then run `python3 scripts/query_brain.py "your question"`. Follow [knowledge maintenance](KNOWLEDGE.md) for sourced updates. Source refreshes must preserve conflicts and mark affected guidance for review.

For account work, establish the private client/account profile using the readiness skill, review the matching runtime adapter, prepare an exact action plan, and obtain applicable authorization before any external effect. The operation helpers and fixtures are local checks and simulations.

`import_report.py` validates explicit manual-mapping provenance and account context. It is not a native Ads Manager export auto-detector. Keep raw and normalized client records outside the project.
