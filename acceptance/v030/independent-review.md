# v0.3.0 independent integrated review

Date: 2026-09-11

Verdict: **PASS for a limited local public-source release candidate.** I found no
open release-blocking defect in the frozen scope after the corrections below.
This verdict does not establish publication, native Windows support, native Ads
account behavior, live action safety, remote CI success, or general model
reliability.

## Scope reviewed

- `scripts/safe_io.py`, `scripts/knowledge_core.py`, and
  `scripts/operating_core.py`, with their filesystem, transaction, lock,
  checkpoint, recovery, and learning-projection tests.
- `scripts/prepare_public.py` and `scripts/package_release.py`, their tests, the
  explicit public allowlist, projection manifest, archive manifest, privacy
  exclusions, deterministic ZIP behavior, and MIT license inclusion.
- `README.md`, `BUILD_STATUS.md`, `docs/WINDOWS.md`,
  `docs/LIVE_ACCEPTANCE.md`, `docs/RELEASE_DRAFT.md`, runtime guides, v0.3.0
  status and probe assessment, refreshed registries, and generated projections.
- Historical v0.2.1 review evidence was not regraded or rewritten.

Initial core hashes inspected before fixes:

- `safe_io.py`: `ce3634c51bfa135fef6d56370bdf52430a60428632479227f41abe6f21b3b8eb`
- `knowledge_core.py`: `8d2af7b3585607563f1f0257b70d2c2cd88e2cacf5bddf4ca4cd28e55cce3c26`
- `operating_core.py`: `304b3537d2449a902a0581b28716aff8978a2ae3374cef3e9f786a2d68975275`

Frozen core hashes rechecked after fixes:

- `safe_io.py`: `85a9c46b373c3e3774fd3e65e2767d68b2a48b99acde4c140baa7617c61352e8`
- `knowledge_core.py`: `8d2af7b3585607563f1f0257b70d2c2cd88e2cacf5bddf4ca4cd28e55cce3c26`
- `operating_core.py`: `8d45f2fca0a16f276b67523798e02e14305c03db902b319c0e5fddea11838057`

## Findings closed during review

1. Bounded reads opened a FIFO before checking its type and could hang. The
   final helper uses nonblocking open before `fstat`, with a subprocess test.
2. Checkpoint append had the corresponding FIFO-open hang. It now fails before
   waiting for a peer, with focused coverage.
3. Exclusive creation called `fsync` only on file contents despite claiming a
   durable new name. It now syncs the file and parent directories.
4. A failed destination-parent open in `replace_regular` leaked the already-open
   source descriptor. The final exception path closes it, with an fd regression.
5. Cross-directory staged replacement synced only the destination directory.
   The final helper syncs both source and destination directory entries.
6. Learning promotion copied an unvalidated supersession field into public
   output. It now accepts only unique lowercase SHA-256 values.
7. Reviewed general text could repeat identifiers resolved from private receipt
   fields. The promotion path now screens those known identifiers while stating
   correctly that this bounded check is not an anonymization guarantee.
8. The package boundary omitted the bearer-header detector used by the public
   projection boundary. Both pattern sets now match, and a parity test prevents
   silent drift. No actual credential was used in the test.

## Verification

- Core tests: 63 passed.
- Analyzer and skill tests: 12 passed.
- Synthetic workflow verifier: five cases passed all listed checks.
- Offline measurement fixture: ten cases passed; it reports zero native events
  sent and does not claim platform behavior.
- Knowledge validation: 68 sources, 60 claims, and 5 contradictions; generated
  JSON projections were in sync.
- `validate_pack.py`: passed with 167 pre-report allowlisted files.
- Local doctor: POSIX descriptor backend ready for local checks; secrets were
  explicitly not inspected by that command.
- A temporary clean public projection and deterministic archive were built:
  167 manifest-listed source files, MIT `LICENSE` included, no forbidden private
  path part, one archive root, and matching projection/package inventories.

## Evidence limits and remaining gates

Windows evidence is a simulated fail-closed capability test only. Guarded native
Windows workflows remain unavailable, and native Windows and macOS runs remain
unverified. The Linux Python 3.11/3.14 CI matrix is configured; remote CI has not
run. Filesystem `fsync` behavior was inspected and locally exercised, not tested
through a real power-loss event.

The v0.3.0 advisory probes remain partial and retain their recorded output
errors and corrections. Synthetic workflow success does not prove reliable
agent behavior on other inputs. Native Ads account controls, genuine CSV/API
mapping, measurement transmission, delivery, and live actions remain unverified.
No repository, release, or community post was published by this review.

This review preceded inclusion of this file in the public projection. The
release owner must rebuild and verify the final projection and extracted ZIP so
their manifests include this report. Hashes provide integrity, not identity,
authentication, authorization, or protection from an equal-privilege writer.
