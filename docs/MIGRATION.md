# Upgrade to v0.3.0

Extract v0.3.0 into a new folder and follow the quickstart there. Keep the complete source tree together. Preserve the older ZIP and any private client workspace; do not copy private records into the public source folder. No global installation or automatic data migration is performed.

The new release adds guarded filesystem helpers, an explicit OS capability check, updated campaign-control research and preflight instructions, and a separately prepared public-source package. Source-folder commands require Python 3.11 or later. Linux is validated; Windows guarded workflows are unavailable and macOS remains unverified.

Existing versioned account and action records still require identity, schema and authorization checks before reuse. A prior approval does not authorize new settings, additional spending or a different account. Reconcile any unfinished external operation before retrying it. Knowledge updates continue through hash-bound proposals, preserving curated notes and registry history.

For rollback, open the retained v0.2.1 artifact in a separate folder. Retain newer private records and review compatibility before reuse. A local rollback cannot undo external campaign changes. The canonical pre-v0.3.0 backup is retained separately and excluded from the public package.

## Earlier v0.1 to v0.2 migration


Before implementation, the complete v0.1 tree was saved in a timestamped `pre-v0.2` archive in the parent workspace's `backups/` directory. Restore that archive into a new directory to inspect or run the prior candidate. Never extract over the current workspace.

[Migration map](../references/migration.json) records historical paths moved to `legacy-v0.1/`. The old Obsidian template, generated sample, site, installer, scaffold commands and maturity score scripts are historical and excluded from active packaging. Their internal paths are preserved for traceability, not promised runnable in their archived location.

The new `brain/index.md` routes 13 topic notes to stable canonical claim IDs. Source registries and raw research summaries retain their original identity. Historical capture-path and vault links describe the old capture layout; factual retrieval uses canonical source IDs and URLs.

The old all-at-once assembler is replaced by reviewed incremental proposals. The package entrypoint now dispatches query, knowledge, operate and validate. Old scaffold commands are available only by restoring the prior snapshot. No global installation, Git change, AIMH edit or account action was performed by this migration.

Rollback new local work by comparing against the saved snapshot and restoring only selected files into a separate candidate. Preserve any newer private records and user changes; do not roll back external effects from a filesystem archive.
