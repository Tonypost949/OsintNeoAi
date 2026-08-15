#!/usr/bin/env python3
"""Create a validation-only manifest for the fixed 11770 Warner PPP CSV.

This tool reads repository data and writes a new JSON artifact. It never writes
to the source CSV, schema, repository database, or upstream services.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
INPUT_CSV = ROOT / "ppp_data" / "ppp_11770_warner.csv"
SCHEMA_JSON = ROOT / "ppp_data" / "ppp_bq_schema.json"
REQUIRED_FIELDS = ("LoanNumber", "BorrowerName", "BorrowerAddress", "CurrentApprovalAmount", "DateApproved")


def digest(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(65_536), b""):
            hasher.update(block)
    return hasher.hexdigest()


def normalized(value: str | None) -> str:
    return re.sub(r"[^a-z0-9]", "", (value or "").lower())


def money(value: str | None) -> Decimal | None:
    raw = (value or "").strip()
    if not raw:
        return None
    try:
        return Decimal(raw.replace("$", "").replace(",", ""))
    except InvalidOperation:
        return None


def date_value(value: str | None) -> datetime | None:
    raw = (value or "").strip()
    for pattern in ("%Y-%m-%d", "%m/%d/%Y", "%Y/%m/%d"):
        try:
            return datetime.strptime(raw, pattern)
        except ValueError:
            continue
    return None


def add_flag(flags: list[dict[str, Any]], rule_id: str, status: str, interpretation: str, row_number: int | None = None, fields: dict[str, Any] | None = None) -> None:
    flags.append({
        "rule_id": rule_id,
        "status": status,
        "row_number": row_number,
        "fields": fields or {},
        "interpretation": interpretation,
    })


def validate(headers: list[str], rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    flags: list[dict[str, Any]] = []
    for field in REQUIRED_FIELDS:
        if field not in headers:
            add_flag(flags, "dataset_missing_column", "data_quality", "The fixed validation task cannot evaluate this required source field because the CSV does not contain the column.", fields={"field": field})

    identifiers: defaultdict[str, list[int]] = defaultdict(list)
    for row_number, row in enumerate(rows, start=2):
        for field in REQUIRED_FIELDS:
            if field in headers and not (row.get(field) or "").strip():
                add_flag(flags, "required_value_missing", "data_quality", "The source value is absent for this validation task; this is a completeness condition, not an investigative conclusion.", row_number, {"field": field, "raw_value": row.get(field, "")})
        if "CurrentApprovalAmount" in headers and (row.get("CurrentApprovalAmount") or "").strip():
            amount = money(row.get("CurrentApprovalAmount"))
            if amount is None:
                add_flag(flags, "amount_parse_failure", "data_quality", "The amount text could not be parsed. Preserve the raw source value for review.", row_number, {"raw_value": row.get("CurrentApprovalAmount", "")})
            elif amount < 0:
                add_flag(flags, "negative_amount", "data_quality", "A negative amount is a source-data condition, not an investigative conclusion.", row_number, {"raw_value": row.get("CurrentApprovalAmount", "")})
            elif amount == 0:
                add_flag(flags, "zero_amount", "needs_human_review", "A zero amount requires source review; it does not establish an irregularity, eligibility result, or misconduct.", row_number, {"raw_value": row.get("CurrentApprovalAmount", "")})
        if "DateApproved" in headers and (row.get("DateApproved") or "").strip() and date_value(row.get("DateApproved")) is None:
            add_flag(flags, "date_parse_failure", "data_quality", "The approval-date text could not be parsed with supported formats. Preserve the raw source value for review.", row_number, {"raw_value": row.get("DateApproved", "")})
        if "LoanNumber" in headers and normalized(row.get("LoanNumber")):
            identifiers[normalized(row.get("LoanNumber"))].append(row_number)
    for identifier, row_numbers in identifiers.items():
        if len(row_numbers) > 1:
            for row_number in row_numbers:
                add_flag(flags, "duplicate_loan_identifier", "possible_duplicate", "Rows share an exact normalized loan identifier. Preserve all rows and reconcile with the source release before any interpretation.", row_number, {"normalized_loan_identifier": identifier, "candidate_rows": row_numbers})
    return flags


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the fixed PPP 11770 Warner CSV without modifying source data.")
    parser.add_argument("--output", type=Path, required=True, help="New JSON artifact path; source files are never overwritten.")
    args = parser.parse_args()
    if args.output.resolve() in {INPUT_CSV.resolve(), SCHEMA_JSON.resolve()}:
        raise ValueError("The validation output must not overwrite a repository source file.")
    with INPUT_CSV.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        if not reader.fieldnames:
            raise ValueError("The fixed PPP input has no CSV header row.")
        headers = reader.fieldnames
        rows = list(reader)
    flags = validate(headers, rows)
    result = {
        "tool": "validate_ppp_11770_warner",
        "status": "validation_only",
        "disclaimer": "This artifact records data-quality and review conditions only. It does not establish fraud, identity, ownership, eligibility, misconduct, or any investigative conclusion.",
        "input": {
            "path": str(INPUT_CSV.relative_to(ROOT)),
            "sha256": digest(INPUT_CSV),
            "schema_path": str(SCHEMA_JSON.relative_to(ROOT)),
            "schema_sha256": digest(SCHEMA_JSON),
            "raw_headers": headers,
            "row_count": len(rows),
            "repository_revision": __import__("os").environ.get("GITHUB_SHA", "local-uncommitted"),
        },
        "flags": flags,
        "summary": dict(Counter(flag["status"] for flag in flags)),
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
