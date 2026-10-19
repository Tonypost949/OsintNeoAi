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
- `scanner/verify_public.py` — post-scan verifier; blocks secrets, SSNs, and
  private IPs from being published.
- `scanner/sanitize_manifest.py` — publish-safe manifest generator.
- `scanner/run_scan.sh` — VM runner.
- `POLICY.md` — masking and public-record policy with examples.
- `index.html` — public landing page.
- `public_export/` — generated public output (redacted docs and records).
- `review_queue/` — items held for missing citations or review; not committed.
- `quarantine/` — never-publish items; contents are not committed.

## Current status

- Free always-on worker: GCP `osint-free` e2-micro in `us-central1-a`.
- Public full-tree export: **3,325 published files** (76 MB), verified with
  zero hard secrets, zero unredacted SSNs, and zero private IPs.
- Citation coverage: 1,163 source URLs, 1,126 authority lines, 1,057
  legal-section links; 364 files carry all three. Gaps are published in
  `public_export/CITATION_GAPS.csv`.
- Schedule: systemd timer `osint-public-scan.timer` runs every 6 hours; a
  source-remote guard refuses to scan anything that is not the private archive.
- Private source and its git history: not published.

