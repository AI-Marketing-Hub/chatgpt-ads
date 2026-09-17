# Security

Do not put credentials, cookies, API keys, client exports, account identifiers,
browser captures or private paths in a public issue, pull request, discussion,
log or release asset.

Report security issues privately through [GitHub private vulnerability reporting](https://github.com/AI-Marketing-Hub/chatgpt-ads/security/advisories/new). Provide a minimal, sanitized reproduction. Do not post sensitive details in public issues.

Release preparation scans for common API keys, private keys, bearer tokens,
local home paths and forbidden archive entries. Pattern scanning is a guard,
not proof that a tree is safe to publish. Manual review of the exact public
projection is required.

## Maintainer checks

CI runs an offline detect-secrets scan over the current tree and all reachable Git history. `.secrets.baseline` contains reviewed detector hashes, not secret values. New candidates fail CI and require human inspection; never regenerate the baseline simply to make a failure pass. Manifests are checked separately to avoid circular baseline hashes. Package checks and scanners are complementary, and neither guarantees the absence of all private information.

Validation and scanner dependencies are version-pinned with release hashes under `requirements/`. Update them deliberately and rerun all supported environments. No credential-validity probe is made by the local scanner.

Repository protections require signed commits and passing checks even for administrators. Review routing is configured, but a second person's approval is not enforced while there is one maintainer. Version tags cannot be updated or deleted through the ruleset. Release immutability applies to new releases; v0.3.0 remains a historical mutable release.

CodeQL covers Python and Actions, and Dependabot security updates are enabled. GitHub currently leaves generic-pattern scanning and validity checks unavailable on this personal repository; enabled provider scanning and push protection are complemented by the offline scanner.

## Local path selection and CodeQL triage

CodeQL alerts 1 and 2 on v0.3.0 trace the operator's `--csv` argument to the filesystem anchor and leaf opens in `safe_io.py`. Independent review classified these as expected same-user local file access, not a privilege or confinement bypass. The helper bounds reads, checks regular files and traverses with no-follow directory descriptors; it does not confine the caller to an application directory. Report bytes are also matched against their declared SHA-256 before analysis. Context reads use the same bounded helper in v0.3.1.

Do not expose these CLI paths to remote callers or run them as a privileged service without a new authorization and filesystem-confinement design. These classifications must be reconsidered if the threat boundary changes. The alerts are reviewed false positives in the shipped local-CLI scope, not vulnerabilities claimed fixed by this release.
