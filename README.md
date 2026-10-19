# OsintNeoAi Public Mirror

This repository is the **public, redacted, source-cited** mirror of the private
investigation workspace. Raw evidence and unredacted local files are never
published here.

## Publishing rules

- Full names are retained.
- Partial identifiers are masked in the style used by people-search and
  identity-theft-protection sites:
  - SSN: `***-**-1234`
  - phone: `(***) ***-1234`
  - email: `j***@example.com`
  - street address: `123 M*** St`
  - date of birth: `**/**/1984`
  - account numbers: `****1234`
- Material that is already an official public record is **not masked** when it
  carries a source URL and authority citation. High-risk identifiers (SSNs,
  financial accounts, secrets) remain masked even in public records.
- Every published item must carry a source URL, a citation, an authority, and
  where applicable a link to the relevant legal section. Items without a
  source are held in the review queue, not published.
- Local/private source remains unredacted.
- The scanner fails closed: unsupported binaries, secrets, and files with
  unresolved high-risk identifiers are quarantined, not published.

## Layout

- `scanner/redact.py` — fail-closed redaction and citation auditor.
- `scanner/run_scan.sh` — VM runner.
- `POLICY.md` — masking and public-record policy with examples.
- `public_export/` — generated public output (populated by the scan).
- `review_queue/` — items held for missing citations or review.
- `quarantine/` — never-publish items; contents are not committed.

## Current status

The scanner is being armed on the free always-on VM. The public mirror is
populated only from scan output, never from the private working tree.
