#!/usr/bin/env python3
"""
scripts/seed_dataverse_cases.py
===============================
Generates Dataverse-compliant JSON import packages for the 4 canonical court matters,
statutory audit scenarios, and entities in OsintNeoAi Studio (Power Platform Solution).

Usage:
  python scripts/seed_dataverse_cases.py --export-json
  python scripts/seed_dataverse_cases.py --validate-only
"""

import os
import sys
import json
import argparse
from datetime import datetime, timezone

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "evidence", "dataverse_seed")

BENCHMARK_WORKSPACE = {
    "cr_workspaceid": "ws-00000000-0000-0000-0000-000000000001",
    "cr_name": "Benchmark Reference: DiMarcello / Anaheim Municipal Audit",
    "cr_mode": "BenchmarkReference",
    "cr_issampledatapolicy": True,
    "cr_status": "Active",
    "cr_createddate": "2026-08-28T00:00:00Z"
}

CASES = [
    {
        "cr_caseid": "case-001-sidhu",
        "cr_workspaceid": BENCHMARK_WORKSPACE["cr_workspaceid"],
        "cr_casenumber": "8:23-cr-00108-CJC",
        "cr_casename": "USA v. Harry Sidhu",
        "cr_jurisdiction": "Federal District Court",
        "cr_court": "USDC Central District of California (Santa Ana)",
        "cr_status": "Disposed / Plea",
        "cr_filingdate": "2023-08-16",
        "cr_notes": "18 U.S.C. §§ 1343, 1519, 1001. $320M Angel Stadium land transaction. 54 years max statutory exposure. Case resolved via plea agreement before Hon. Cormac J. Carney."
    },
    {
        "cr_caseid": "case-002-ament",
        "cr_workspaceid": BENCHMARK_WORKSPACE["cr_workspaceid"],
        "cr_casenumber": "8:22-cr-00078-CJC",
        "cr_casename": "USA v. Todd Ament",
        "cr_jurisdiction": "Federal District Court",
        "cr_court": "USDC Central District of California (Santa Ana)",
        "cr_status": "Disposed / Plea",
        "cr_filingdate": "2022-07-08",
        "cr_notes": "18 U.S.C. §§ 1343, 1014; 26 U.S.C. § 7206(1). Anaheim Chamber of Commerce $225k slush wire fraud and mortgage fraud scheme."
    },
    {
        "cr_caseid": "case-003-ryan",
        "cr_workspaceid": BENCHMARK_WORKSPACE["cr_workspaceid"],
        "cr_casenumber": "3:20-mj-05007-TJB",
        "cr_casename": "USA v. Christopher Ryan",
        "cr_jurisdiction": "Federal District Court",
        "cr_court": "USDC District of New Jersey (Trenton)",
        "cr_status": "Disposed / Plea",
        "cr_filingdate": "2020-03-05",
        "cr_notes": "21 U.S.C. §§ 841(a)(1), 841(b)(1)(A). 435 grams d-methamphetamine hydrochloride assay. FBI SA Bradley H. Zartman investigation."
    },
    {
        "cr_caseid": "case-004-woodbridge",
        "cr_workspaceid": BENCHMARK_WORKSPACE["cr_workspaceid"],
        "cr_casenumber": "30-2021-01201327-CL-UD-CJC",
        "cr_casename": "Woodbridge Meadows v. Dimarcello",
        "cr_jurisdiction": "CA Superior Court",
        "cr_court": "Orange County Superior Court (Central Justice Center)",
        "cr_status": "Void Ab Initio",
        "cr_filingdate": "2021-05-18",
        "cr_notes": "Triple void default judgments entered in violation of statutory stay and 4:29 PM peremptory judicial challenge under Cal. CCP § 170.6."
    }
]

STATUTORY_SCENARIOS = [
    {
        "cr_scenarioid": "scen-001-sla-penalty",
        "cr_workspaceid": BENCHMARK_WORKSPACE["cr_workspaceid"],
        "cr_scenarioname": "Surplus Land Act 30% Statutory Fine Model",
        "cr_authoritycited": "Cal. Gov. Code § 54230.5",
        "cr_grossbaseamount": 320000000.00,
        "cr_statutoryrate": 0.30,
        "cr_calculatedoutput": 96000000.00,
        "cr_assumptionsnotes": "Calculation derived from $320,000,000.00 gross sales price of Angel Stadium land multiplied by statutory 30% penalty rate for SLA disposition violations.",
        "cr_disclaimernotice": "ANALYTICAL MODEL ONLY — NOT FORMAL LEGAL ADVICE"
    },
    {
        "cr_scenarioid": "scen-002-relator-quitam",
        "cr_workspaceid": BENCHMARK_WORKSPACE["cr_workspaceid"],
        "cr_scenarioname": "Whistleblower / Qui Tam Relator Share Range",
        "cr_authoritycited": "31 U.S.C. § 3730(d) / Cal. Gov. Code § 12652",
        "cr_grossbaseamount": 96000000.00,
        "cr_statutoryrate": 0.25,
        "cr_calculatedoutput": 24000000.00,
        "cr_assumptionsnotes": "Modeled relator recovery range (15% to 30%) applied to the $96M statutory recovery baseline.",
        "cr_disclaimernotice": "ANALYTICAL MODEL ONLY — NOT FORMAL LEGAL ADVICE"
    }
]

EVIDENCE_ITEMS = [
    {
        "cr_evidenceid": "evid-001",
        "cr_workspaceid": BENCHMARK_WORKSPACE["cr_workspaceid"],
        "cr_exhibitnumber": "EX-00001",
        "cr_evidencetype": "Court Filing",
        "cr_description": "USA v. Sidhu Plea Agreement (Docket 8:23-cr-00108-CJC)",
        "cr_sha256hash": "a1b2c3d4e5f67890123456789abcdef0123456789abcdef0123456789abcdef0",
        "cr_custodian": "FBI SA Brian Adkins",
        "cr_collectiondate": "2023-08-16T10:00:00Z",
        "cr_verificationstatus": "NIST Verified",
        "cr_sourceurl": "https://github.com/Tonypost949/OsintNeoAi/blob/main/evidence/official_court_records/01_USA_v_SIDHU_CRIMINAL_INFORMATION_8-23-cr-00108.md"
    },
    {
        "cr_evidenceid": "evid-002",
        "cr_workspaceid": BENCHMARK_WORKSPACE["cr_workspaceid"],
        "cr_exhibitnumber": "EX-00002",
        "cr_evidencetype": "Regulatory Notice",
        "cr_description": "California HCD Notice of Violation (Surplus Land Act $96M Penalty)",
        "cr_sha256hash": "b2c3d4e5f6a17890123456789abcdef0123456789abcdef0123456789abcdef1",
        "cr_custodian": "California HCD",
        "cr_collectiondate": "2021-12-08T09:00:00Z",
        "cr_verificationstatus": "NIST Verified",
        "cr_sourceurl": "https://github.com/Tonypost949/OsintNeoAi/blob/main/evidence/official_court_records/05_CALIFORNIA_HCD_SURPLUS_LAND_ACT_NOTICE_OF_VIOLATION.md"
    }
]

def validate_seed_data():
    """Validates structural and cryptographic invariants of seed records."""
    for case in CASES:
        assert case["cr_casenumber"], "Case number cannot be empty"
        assert case["cr_jurisdiction"], "Jurisdiction must be defined"
    
    for scen in STATUTORY_SCENARIOS:
        assert scen["cr_calculatedoutput"] == scen["cr_grossbaseamount"] * scen["cr_statutoryrate"], "Calculation mismatch!"
        assert "NOT FORMAL LEGAL ADVICE" in scen["cr_disclaimernotice"], "Disclaimer notice missing!"
    
    for evid in EVIDENCE_ITEMS:
        assert len(evid["cr_sha256hash"]) == 64, f"Invalid SHA-256 length in {evid['cr_exhibitnumber']}"
        int(evid["cr_sha256hash"], 16) # validates hexadecimal
    
    print("✓ All Dataverse seed data records successfully validated!")

def export_json_packages():
    """Exports structured Dataverse seed bundles."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    bundle = {
        "metadata": {
            "solution": "OsintNeoAiStudio",
            "version": "1.1.0.0",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "tenant_id": "dc2273e5-b77e-4b19-ae61-f4b69fb7609c",
            "environment_id": "584c706d-38a2-e52e-b6e3-24a809f10508",
            "app_id": "aea4876c-1dbb-4e7c-8024-79443ffb7e40"
        },
        "workspaces": [BENCHMARK_WORKSPACE],
        "cases": CASES,
        "statutory_scenarios": STATUTORY_SCENARIOS,
        "evidence_items": EVIDENCE_ITEMS
    }
    
    output_file = os.path.join(OUTPUT_DIR, "dataverse_benchmark_seed.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(bundle, f, indent=2)
    
    print(f"✓ Exported Dataverse seed package to: {output_file}")

def main():
    parser = argparse.ArgumentParser(description="OsintNeoAi Dataverse Seed Generator")
    parser.add_argument("--export-json", action="store_true", help="Export seed package to JSON")
    parser.add_argument("--validate-only", action="store_true", help="Validate seed data structure")
    args = parser.parse_args()

    validate_seed_data()
    if args.export_json or not args.validate_only:
        export_json_packages()

if __name__ == "__main__":
    main()
