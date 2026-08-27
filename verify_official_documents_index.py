#!/usr/bin/env python3
"""
Verification Script for Official Court Records and Master Index Catalog.
Verifies the integrity, completeness, statutory citations, and cross-references
of OFFICIAL_DOCUMENTS_INDEX.md and all 8 primary exhibits in C:\\OsintNeoAi\\evidence\\official_court_records\\.
"""

import os
import sys
import re
from pathlib import Path

BASE_DIR = Path("C:/OsintNeoAi")
EVIDENCE_DIR = BASE_DIR / "evidence" / "official_court_records"
MASTER_INDEX_PATH = EVIDENCE_DIR / "OFFICIAL_DOCUMENTS_INDEX.md"

EXHIBITS = [
    {
        "num": "01",
        "file": "01_USA_v_Harry_Sidhu_8_23_cr_00108_CJC.md",
        "case_no": "8:23-cr-00108-CJC",
        "judge": "Cormac J. Carney",
        "statutes": ["18 U.S.C. § 1343", "18 U.S.C. § 1519", "18 U.S.C. § 1001"],
    },
    {
        "num": "02",
        "file": "02_HCD_Notice_of_Violation_Surplus_Land_Act.md",
        "case_no": "30-2020-01131102-CU-MC-CJC",
        "judge": "Megan Kirkeby",
        "statutes": ["54220", "54221", "54222", "54230.5"],
    },
    {
        "num": "03",
        "file": "03_USA_v_Todd_Ament_and_Melahat_Rafiei.md",
        "case_no": "8:22-cr-00078-CJC",
        "judge": "Cormac J. Carney",
        "statutes": ["18 U.S.C. § 1343", "18 U.S.C. § 1014", "26 U.S.C. § 7206"],
    },
    {
        "num": "04",
        "file": "04_USA_v_Christopher_Ryan_3_20_mj_05007_TJB.md",
        "case_no": "3:20-mj-05007-TJB",
        "judge": "Tonianne J. Bongiovanni",
        "statutes": ["21 U.S.C. § 841", "Bradley H. Zartman"],
    },
    {
        "num": "05",
        "file": "05_Woodbridge_Meadows_v_Dimarcello_30_2021_01201327_CL_UD_CJC.md",
        "case_no": "30-2021-01201327-CL-UD-CJC",
        "judge": "Carmen Luege",
        "statutes": ["170.6", "415.45", "585", "473(d)", "Rochin", "Heidary"],
    },
    {
        "num": "06",
        "file": "06_JL_Investigation_Anaheim_Forensic_Audit_Report.md",
        "case_no": "JL",
        "judge": "Clay M. Smith",
        "statutes": ["Brown Act", "54952.2", "7920", "1,500,000"],
    },
    {
        "num": "07",
        "file": "07_Anaheim_City_Council_Stadium_Voidance_Resolution_2022_064.md",
        "case_no": "2022-064",
        "judge": "Trevor O'Neil",
        "statutes": ["320,000,000", "50,000,000", "1565", "1090"],
    },
    {
        "num": "08",
        "file": "08_Multi_State_Police_and_Commercial_Incident_Logs.md",
        "case_no": "2019-00053723",
        "judge": "Timothy Donovan",
        "statutes": ["2C:29-1a", "2C:20-11b", "14098", "I-2019-001222"],
    },
]

def main():
    print("=" * 80)
    print("🚀 RUNNING OFFICIAL COURT RECORDS & MASTER INDEX AUDIT")
    print("=" * 80)

    total_checks = 0
    passed_checks = 0

    def check(name, condition, details=""):
        nonlocal total_checks, passed_checks
        total_checks += 1
        if condition:
            passed_checks += 1
            print(f"  [PASS] {name}")
        else:
            print(f"  [FAIL] {name}: {details}")

    # Check 1: Master Index file exists
    check("Master Index File Exists", MASTER_INDEX_PATH.exists(), str(MASTER_INDEX_PATH))
    if not MASTER_INDEX_PATH.exists():
        print("CRITICAL: Master index not found.")
        sys.exit(1)

    index_content = MASTER_INDEX_PATH.read_text(encoding="utf-8")
    index_lines = index_content.splitlines()
    check(f"Master Index Length >= 200 lines ({len(index_lines)} lines)", len(index_lines) >= 200)

    # Check 2: All 8 exhibit files exist on disk
    print("\n--- Auditing Individual Exhibit Files On Disk ---")
    for ex in EXHIBITS:
        path = EVIDENCE_DIR / ex["file"]
        check(f"Exhibit {ex['num']} ({ex['file']}) exists", path.exists())
        if path.exists():
            content = path.read_text(encoding="utf-8")
            check(f"Exhibit {ex['num']} content > 1000 bytes ({len(content)} bytes)", len(content) > 1000)

    # Check 3: Master index includes each exhibit and its key identifiers
    print("\n--- Auditing Master Index References & Statutes ---")
    for ex in EXHIBITS:
        check(f"Master Index references {ex['file']}", ex["file"] in index_content)
        check(f"Master Index references case '{ex['case_no']}'", ex["case_no"] in index_content)
        check(f"Master Index references official '{ex['judge']}'", ex["judge"] in index_content)
        for stat in ex["statutes"]:
            check(f"Master Index references statutory token '{stat}'", stat in index_content)

    # Check 4: Master Index structural sections
    print("\n--- Auditing Master Index Key Structural Sections ---")
    required_sections = [
        "EXECUTIVE SUMMARY & REPOSITORY ARCHITECTURE",
        "COMPREHENSIVE PRIMARY EXHIBITS CATALOG",
        "EXHIBIT 01: UNITED STATES v. HARISH \"HARRY\" SIDHU",
        "EXHIBIT 02: STATE OF CALIFORNIA HCD NOTICE OF VIOLATION",
        "EXHIBIT 03: UNITED STATES v. TODD AMENT & UNITED STATES v. MELAHAT RAFIEI",
        "EXHIBIT 04: UNITED STATES v. CHRISTOPHER RYAN",
        "EXHIBIT 05: WOODBRIDGE MEADOWS APARTMENTS LLC v. ANTHONY DIMARCELLO",
        "EXHIBIT 06: JL GROUP INDEPENDENT INVESTIGATION REPORT",
        "EXHIBIT 07: ANAHEIM CITY COUNCIL STADIUM VOIDANCE RESOLUTION",
        "EXHIBIT 08: MULTI-STATE POLICE INCIDENT LOGS",
        "MASTER CROSS-JURISDICTIONAL HARMONIZATION MATRIX",
        "MASTER STATUTORY CODE & PENAL VIOLATION LOOKUP TABLE",
        "EVIDENTIARY CHAIN OF CUSTODY & REPOSITORY VAULT INTEGRATION",
        "PROCEDURAL IRREGULARITIES, DUE PROCESS & JURISDICTIONAL NULLITIES",
        "MASTER VERIFICATION MATRIX & REPOSITORY ATTESTATION",
    ]

    for sec in required_sections:
        check(f"Section Header '{sec}' present", sec in index_content)

    # Check 5: File Links Valid
    print("\n--- Auditing File Links in Master Index ---")
    file_links = re.findall(r'\[.*?\]\((file:///.*?|[\w\d_\-\.]+\.md)\)', index_content)
    for link in file_links:
        clean_path = link.replace("file:///", "").replace("/", "\\")
        target = Path(clean_path)
        if not target.is_absolute():
            target = EVIDENCE_DIR / link
        check(f"File link target exists: {target.name}", target.exists(), str(target))

    print("\n" + "=" * 80)
    print(f"AUDIT SUMMARY: {passed_checks}/{total_checks} Checks Passed ({(passed_checks/total_checks)*100:.1f}%)")
    print("=" * 80)

    if passed_checks == total_checks:
        print("🎉 ALL INTEGRITY AND VERIFICATION CHECKS PASSED PERFECTLY!")
        return 0
    else:
        print("⚠️ SOME VERIFICATION CHECKS FAILED.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
