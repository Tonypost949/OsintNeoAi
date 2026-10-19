#!/usr/bin/env python3
"""Write citation coverage and gap reports from a publish-safe manifest."""
from __future__ import annotations
import argparse
import csv
import json
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--csv", required=True)
    ap.add_argument("--json", required=True)
    a = ap.parse_args()
    m = json.loads(Path(a.manifest).read_text(encoding="utf-8"))
    records = m.get("published_records", [])
    fields = ("source_url", "authority", "legal_section")
    with Path(a.csv).open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["path", *fields, "citation_status"])
        for r in records:
            c = r.get("citation", {})
            missing = [k for k in fields if not c.get(k)]
            w.writerow([r.get("path"), *(c.get(k) for k in fields),
                        "complete" if not missing else "missing:" + ",".join(missing)])
    coverage = {k: sum(1 for r in records if r.get("citation", {}).get(k))
                for k in fields}
    coverage["published"] = len(records)
    coverage["all_three"] = sum(
        1 for r in records if all(r.get("citation", {}).get(k) for k in fields))
    Path(a.json).write_text(json.dumps(coverage, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(coverage, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
