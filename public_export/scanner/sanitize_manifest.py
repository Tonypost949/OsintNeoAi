#!/usr/bin/env python3
"""Create a publish-safe manifest from a scanner run.

The raw manifest includes paths for quarantined and review-held files. Those
paths can themselves be sensitive, so the public manifest only lists
published files and aggregate counts.
"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="src", required=True)
    ap.add_argument("--out", dest="dst", required=True)
    a = ap.parse_args()
    m = json.loads(Path(a.src).read_text(encoding="utf-8"))
    published = []
    for r in m.get("records", []):
        if r.get("status") != "published":
            continue
        published.append({
            "path": r.get("path"),
            "sha256": r.get("sha256"),
            "bytes": r.get("bytes"),
            "rules": r.get("rules", {}),
            "citation": r.get("citation", {}),
        })
    out = {
        "generated_at": m.get("generated_at"),
        "source": "private archive (redacted; not published)",
        "strict_citations": m.get("strict_citations"),
        "files_total": m.get("files_total"),
        "status_counts": m.get("status_counts", {}),
        "published_records": published,
    }
    Path(a.dst).write_text(json.dumps(out, indent=2, sort_keys=True) + "\n",
                           encoding="utf-8")
    print(json.dumps({"published": len(published),
                      "status_counts": out["status_counts"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
