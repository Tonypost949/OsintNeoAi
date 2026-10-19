# IP Intake — IP Forensic Sweep Pipeline

Provenance-first IP extraction for the OsintNeoAi evidence program (Law 15:
every data point carries source, hash, and line-level provenance).

## What it does

Scans a directory tree for IPv4/IPv6 addresses in text sources and PDFs,
classifies each address (public / private / loopback / link-local / multicast /
CGNAT / reserved / unspecified), dedupes per file, and emits:

| Output | Contents |
|--------|----------|
| `ip_occurrences.jsonl` | one row per (file, IP): IP, class, file path, file SHA-256, line number, context snippet, UTC stamp |
| `ip_rollup.csv` | one row per unique IP: occurrences, file count, first source, first context |
| `source_manifest.csv` | every scanned file: SHA-256, size, mtime, type, IPs found |
| `summary.json` | machine-readable totals, class counts, top public IPs |
| `PUBLIC_IPS_FORENSIC_SWEEP_DOSSIER.md` | human-readable dossier (public IPs ranked, source files, methodology) |

## Usage

```bash
python3 ip_ingest.py --root /path/to/tree --out /path/to/output [--label NAME]
```

Options: `--max-filesize-mb` (default 6), `--max-pdf-mb` (default 20), `--no-pdf`.

PDF text extraction requires `pdftotext` (apt: `poppler-utils`); scanned/image-only
PDFs are skipped automatically. Text extraction is deterministic: same tree + same
tool version produces identical outputs.

## Automation

`ip_watch.sh` polls the OsintNeoAi GitHub repo (cron: every 6 hours). When the
remote HEAD changes (new files pushed from the Windows workstation), it pulls,
re-runs the sweep, and pushes the new dossier set to GCS automatically. State
lives in `.last_remote_head`.

## Deployment

- VM: `/home/osintneoai/tools/ip_intake/`
- Outputs: `/home/osintneoai/evidence/ip_intake/<UTC-stamp>_<label>/`
- Cloud mirror: `gcs:backup-project-743aab84-f9a5-4ec7-954/osintneoai_azure_vm/vm-osintneoai-01/<UTC-stamp>/<label>`
  via `tools/cloud_backup/cloud_backup.sh push-path`
