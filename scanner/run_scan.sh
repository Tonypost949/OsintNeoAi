#!/usr/bin/env bash
set -euo pipefail
# Usage: run_scan.sh <private-source-dir> <public-output-dir>
SOURCE="${1:?source dir required}"
OUT="${2:?output dir required}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
python3 "$ROOT/scanner/redact.py" \
  --source "$SOURCE" \
  --out "$OUT" \
  --strict-citations \
  --clean
python3 "$ROOT/scanner/verify_public.py" \
  --root "$OUT/public_export" \
  --out "$OUT/VERIFY_REPORT.json"
python3 "$ROOT/scanner/sanitize_manifest.py" \
  --in "$OUT/PUBLIC_MANIFEST.json" \
  --out "$OUT/PUBLIC_MANIFEST_PUBLIC.json"
python3 "$ROOT/scanner/citation_report.py" \
  --manifest "$OUT/PUBLIC_MANIFEST_PUBLIC.json" \
  --csv "$OUT/CITATION_GAPS.csv" \
  --json "$OUT/CITATION_COVERAGE.json"
