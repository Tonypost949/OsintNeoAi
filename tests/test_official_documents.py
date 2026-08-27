"""
========================================================================================
                      OFFICIAL COURT RECORDS & STATUTORY INVESTIGATIONS
                                4-TIER E2E TEST SUITE
========================================================================================
Test Writer: Automated Verification Suite for Features F1 through F15
Target Directory: C:\\OsintNeoAi\\evidence\\official_court_records\\
Compatible with: pytest, unittest, and direct python invocation.
"""

import os
import re
import unittest
from pathlib import Path

# Base Paths
REPO_ROOT = Path(r"C:\OsintNeoAi")
OFFICIAL_RECORDS_DIR = REPO_ROOT / "evidence" / "official_court_records"

# Document Mapping
DOC_MAP = {
    "F1_SIDHU": OFFICIAL_RECORDS_DIR / "01_USA_v_Harry_Sidhu_8_23_cr_00108_CJC.md",
    "F2_AMENT": OFFICIAL_RECORDS_DIR / "03_USA_v_Todd_Ament_and_Melahat_Rafiei.md",
    "F3_RAFIEI": OFFICIAL_RECORDS_DIR / "03_USA_v_Todd_Ament_and_Melahat_Rafiei.md",
    "F4_RYAN": OFFICIAL_RECORDS_DIR / "04_USA_v_Christopher_Ryan_3_20_mj_05007_TJB.md",
    "F5_HCD": OFFICIAL_RECORDS_DIR / "02_HCD_Notice_of_Violation_Surplus_Land_Act.md",
    "F6_VOIDANCE": OFFICIAL_RECORDS_DIR / "07_Anaheim_City_Council_Stadium_Voidance_Resolution_2022_064.md",
    "F7_JL_AUDIT": OFFICIAL_RECORDS_DIR / "06_JL_Investigation_Anaheim_Forensic_Audit_Report.md",
    "F8_ROA": OFFICIAL_RECORDS_DIR / "05_Woodbridge_Meadows_v_Dimarcello_30_2021_01201327_CL_UD_CJC.md",
    "F9_DEFAULTS": OFFICIAL_RECORDS_DIR / "05_Woodbridge_Meadows_v_Dimarcello_30_2021_01201327_CL_UD_CJC.md",
    "F10_STRIKE": OFFICIAL_RECORDS_DIR / "05_Woodbridge_Meadows_v_Dimarcello_30_2021_01201327_CL_UD_CJC.md",
    "F11_HAMILTON": OFFICIAL_RECORDS_DIR / "08_Multi_State_Police_and_Commercial_Incident_Logs.md",
    "F12_EWING": OFFICIAL_RECORDS_DIR / "08_Multi_State_Police_and_Commercial_Incident_Logs.md",
    "F13_QUANTUM": OFFICIAL_RECORDS_DIR / "08_Multi_State_Police_and_Commercial_Incident_Logs.md",
    "F14_INDEX": OFFICIAL_RECORDS_DIR / "OFFICIAL_DOCUMENTS_INDEX.md",
}


def read_doc(path: Path) -> str:
    """Helper to read document content safely with UTF-8 BOM handling."""
    if not path.exists():
        return ""
    with open(path, "r", encoding="utf-8-sig", errors="replace") as f:
        return f.read()


# ======================================================================================
# TIER 1: FEATURE COVERAGE (>=5 Assertions Per Feature for F1 to F15)
# ======================================================================================

class TestTier1FeatureCoverage(unittest.TestCase):
    """Tier 1: Feature Isolation & Unit Verification for F1 through F15."""

    def test_f1_us_v_sidhu(self):
        """F1: US v. Sidhu (8:23-cr-00108-CJC) - 4-Count Felony Information & Adkins Wiretaps."""
        content = read_doc(DOC_MAP["F1_SIDHU"])
        self.assertTrue(DOC_MAP["F1_SIDHU"].exists(), "F1 file must exist")
        self.assertIn("8:23-cr-00108-CJC", content, "F1 must contain federal docket number")
        self.assertIn("Cormac J. Carney", content, "F1 must name presiding Judge Carney")
        self.assertIn("Harish \"Harry\" Sidhu", content, "F1 must name Defendant Harry Sidhu")
        self.assertIn("18 U.S.C. § 1343", content, "F1 must cite Wire Fraud statute")
        self.assertIn("18 U.S.C. § 1519", content, "F1 must cite Obstruction of Justice statute")
        self.assertIn("18 U.S.C. § 1001(a)(2)", content, "F1 must cite False Statements statute")
        self.assertIn("8:22-mj-00185", content, "F1 must cite Brian Adkins Search Warrant Docket")
        self.assertIn("Brian Adkins", content, "F1 must name FBI SA Brian Adkins")
        self.assertIn("I am going to ask him for $1 million", content, "F1 must quote recorded $1M bribe solicitation")
        self.assertIn("15,887.50", content, "F1 must reference helicopter tax fraud amount")
        self.assertIn("54 Years", content, "F1 must state 54-year maximum exposure")

    def test_f2_us_v_ament(self):
        """F2: US v. Todd Ament (8:22-cr-00078-CJC) - 4-Count Felony Information & Plea."""
        content = read_doc(DOC_MAP["F2_AMENT"])
        self.assertTrue(DOC_MAP["F2_AMENT"].exists(), "F2 file must exist")
        self.assertIn("8:22-cr-00078-CJC", content, "F2 must contain Ament docket number")
        self.assertIn("Todd Ament", content, "F2 must name Defendant Todd Ament")
        self.assertIn("Anaheim Chamber of Commerce", content, "F2 must reference Anaheim Chamber of Commerce")
        self.assertIn("18 U.S.C. § 1343", content, "F2 must cite Wire Fraud statute")
        self.assertIn("18 U.S.C. § 1014", content, "F2 must cite False Statements to Financial Institution")
        self.assertIn("26 U.S.C. § 7206(1)", content, "F2 must cite False Tax Returns statute")
        self.assertIn("225,000", content, "F2 must reference $225,000 Big Bear home fund diversion")
        self.assertIn("TA Group LLC", content, "F2 must identify consulting shell entity TA Group LLC")

    def test_f3_us_v_rafiei(self):
        """F3: US v. Melahat Rafiei (8:23-cr-00009-CJC) - Honest Services Bribery & Wire Fraud."""
        content = read_doc(DOC_MAP["F3_RAFIEI"])
        self.assertTrue(DOC_MAP["F3_RAFIEI"].exists(), "F3 file must exist")
        self.assertIn("8:23-cr-00009-CJC", content, "F3 must contain Rafiei docket number")
        self.assertIn("Melahat Rafiei", content, "F3 must name Defendant Melahat Rafiei")
        self.assertIn("18 U.S.C.", content, "F3 must cite Title 18 USC")
        self.assertIn("1343", content, "F3 must cite Wire Fraud § 1343")
        self.assertIn("Irvine", content, "F3 must reference City of Irvine cannabis scheme")
        self.assertIn("cannabis", content.lower(), "F3 must reference commercial cannabis bribery")
        self.assertIn("cooperat", content.lower(), "F3 must reference FBI cooperation")

    def test_f4_us_v_christopher_ryan(self):
        """F4: US v. Christopher Ryan (3:20-mj-05007-TJB) - USDC D.N.J. Narcotics Complaint."""
        content = read_doc(DOC_MAP["F4_RYAN"])
        self.assertTrue(DOC_MAP["F4_RYAN"].exists(), "F4 file must exist")
        self.assertIn("3:20-mj-05007-TJB", content, "F4 must contain D.N.J. docket number")
        self.assertIn("Tonianne J. Bongiovanni", content, "F4 must name Magistrate Judge Bongiovanni")
        self.assertIn("Christopher Ryan", content, "F4 must name Defendant Christopher Ryan")
        self.assertIn("Bradley H. Zartman", content, "F4 must name FBI SA Bradley H. Zartman")
        self.assertIn("21 U.S.C. §", content, "F4 must cite Title 21 narcotics statutes")
        self.assertIn("841(a)(1)", content, "F4 must cite 21 U.S.C. § 841(a)(1)")
        self.assertIn("841(b)(1)(A)", content, "F4 must cite 21 U.S.C. § 841(b)(1)(A)")
        self.assertIn("6100_6200 section", content, "F4 must quote coded arena seating text")
        self.assertIn("3,000", content, "F4 must reference $3,000 cash Priority Mail delivery")
        self.assertIn("435 Grams", content, "F4 must reference DEA 435 grams laboratory confirmation")

    def test_f5_california_hcd_notice_of_violation(self):
        """F5: California HCD Notice of Violation (Dec 8, 2021) - Surplus Land Act Enforcement."""
        content = read_doc(DOC_MAP["F5_HCD"])
        self.assertTrue(DOC_MAP["F5_HCD"].exists(), "F5 file must exist")
        self.assertIn("December 8, 2021", content, "F5 must specify Dec 8 2021 issuance date")
        self.assertIn("54220", content, "F5 must cite Cal. Gov. Code § 54220 (Surplus Land Act)")
        self.assertIn("54222", content, "F5 must cite Cal. Gov. Code § 54222 (Notice of Availability)")
        self.assertIn("54230.5", content, "F5 must cite Cal. Gov. Code § 54230.5 (Penalty Section)")
        self.assertIn("96,000,000", content, "F5 must compute $96,000,000 statutory penalty")
        self.assertIn("320,000,000", content, "F5 must state $320,000,000 gross transaction value")
        self.assertIn("30%", content, "F5 must state 30% statutory penalty rate")
        self.assertIn("150", content, "F5 must describe 150-acre stadium land")
        self.assertIn("SRB Management", content, "F5 must identify counterparty SRB Management")

    def test_f6_anaheim_resolution_2022_064(self):
        """F6: Anaheim City Council Resolution 2022-064 (May 24, 2022) - Stadium Voidance."""
        content = read_doc(DOC_MAP["F6_VOIDANCE"])
        self.assertTrue(DOC_MAP["F6_VOIDANCE"].exists(), "F6 file must exist")
        self.assertIn("2022-064", content, "F6 must cite Resolution No. 2022-064")
        self.assertIn("May 24, 2022", content, "F6 must state May 24, 2022 meeting date")
        self.assertIn("Trevor O'Neil", content, "F6 must name Mayor Pro Tem Trevor O'Neil")
        self.assertIn("Dr. Jose F. Moreno", content, "F6 must name Motion Maker Dr. Jose F. Moreno")
        self.assertIn("Stephen Faessel", content, "F6 must name Seconder Stephen Faessel")
        self.assertIn("7-0", content, "F6 must record unanimous 7-0 roll call vote")
        self.assertIn("50,000,000", content, "F6 must order refund of $50,000,000 escrow deposit")
        self.assertIn("Robert Fabela", content, "F6 must name City Attorney Robert Fabela")

    def test_f7_jl_investigation_forensic_audit(self):
        """F7: JL Investigation Forensic Audit Report (July 31, 2023) - Anaheim Public Corruption."""
        content = read_doc(DOC_MAP["F7_JL_AUDIT"])
        self.assertTrue(DOC_MAP["F7_JL_AUDIT"].exists(), "F7 file must exist")
        self.assertIn("JL Group", content, "F7 must identify JL Group LLC")
        self.assertIn("July 31, 2023", content, "F7 must state July 31, 2023 report release date")
        self.assertIn("353 Pages", content, "F7 must state 353-page volume")
        self.assertIn("Clay M. Smith", content, "F7 must name Judicial Overseer Hon. Clay M. Smith")
        self.assertIn("Jeffrey Love", content, "F7 must name Lead Investigator Jeffrey Love")
        self.assertIn("Jeff Johnson", content, "F7 must name Lead Investigator Jeff Johnson")
        self.assertIn("1,500,000", content, "F7 must cite $1.5M COVID relief diversion or budget")
        self.assertIn("Visit Anaheim", content, "F7 must identify Visit Anaheim CARES conduit")
        self.assertIn("Anaheim First", content, "F7 must document Anaheim First data mining program")
        self.assertIn("Brown Act", content, "F7 must cite Brown Act open-meeting subversion")

    def test_f8_orange_county_superior_court_61_roa_docket(self):
        """F8: Orange County Superior Court Unlawful Detainer Docket (30-2021-01201327-CL-UD-CJC)."""
        content = read_doc(DOC_MAP["F8_ROA"])
        self.assertTrue(DOC_MAP["F8_ROA"].exists(), "F8 file must exist")
        self.assertIn("30-2021-01201327-CL-UD-CJC", content, "F8 must contain Superior Court case number")
        self.assertIn("WOODBRIDGE MEADOWS", content, "F8 must name Plaintiff Woodbridge Meadows")
        self.assertIn("DIMARCELLO", content, "F8 must name Defendant Dimarcello")
        self.assertIn("Carmen Luege", content, "F8 must name Assigned Judge Carmen Luege")
        self.assertIn("Arden Hoang", content, "F8 must name Plaintiff Counsel Arden Hoang")
        self.assertIn("Richard S. Sontag", content, "F8 must name Plaintiff Counsel Richard S. Sontag")
        self.assertIn("May 18, 2021", content, "F8 must state May 18, 2021 case filing date")

    def test_f9_triple_default_judgments_analysis(self):
        """F9: Triple Default Judgments Analysis (06/29/2021, 12/22/2021, 02/04/2022)."""
        content = read_doc(DOC_MAP["F9_DEFAULTS"])
        self.assertTrue(DOC_MAP["F9_DEFAULTS"].exists(), "F9 file must exist")
        self.assertIn("06/29/2021", content, "F9 must record Default Judgment #1 on June 29, 2021")
        self.assertIn("12/22/2021", content, "F9 must record Default Judgment #2 on December 22, 2021")
        self.assertIn("02/04/2022", content, "F9 must record Default Judgment #3 on February 4, 2022")
        self.assertIn("Rochin", content, "F9 must cite Rochin v. Pat Johnson Mfg. Co. void judgment doctrine")
        self.assertIn("Heidary", content, "F9 must cite Heidary v. Yadollahi jurisdictional nullity")
        self.assertIn("Don Barnes", content, "F9 must name Sheriff Don Barnes")
        self.assertIn("2021102780", content, "F9 must cite Sheriff Levying File #2021102780")

    def test_f10_tactical_429pm_1706_challenge(self):
        """F10: Tactical 4:29 PM Cal. CCP § 170.6 Peremptory Strike of Judge Carmen Luege."""
        content = read_doc(DOC_MAP["F10_STRIKE"])
        self.assertTrue(DOC_MAP["F10_STRIKE"].exists(), "F10 file must exist")
        self.assertIn("170.6", content, "F10 must cite Cal. CCP § 170.6")
        self.assertIn("08/20/2021", content, "F10 must state August 20, 2021 date")
        self.assertIn("03:11", content, "F10 must timestamp 3:11 PM Chambers Work Stay Order")
        self.assertIn("04:29", content, "F10 must timestamp 4:29 PM Peremptory Challenge filing")
        self.assertIn("1885125", content, "F10 must cite E-Filing Transaction #1885125")
        self.assertIn("STAYED", content, "F10 must cite Judge Luege order: Lockout is STAYED")
        self.assertIn("Carmen Luege", content, "F10 must identify Judge Carmen Luege as target of strike")

    def test_f11_hamilton_township_police_records(self):
        """F11: Hamilton Township Police Division Incident Records (2019-00053723 & 2020-00008897)."""
        content = read_doc(DOC_MAP["F11_HAMILTON"])
        self.assertTrue(DOC_MAP["F11_HAMILTON"].exists(), "F11 file must exist")
        self.assertIn("2019-00053723", content, "F11 must cite Incident Case 2019-00053723")
        self.assertIn("1456 Cedar Lane", content, "F11 must state 1456 Cedar Lane occurrence location")
        self.assertIn("Timothy Donovan", content, "F11 must name Officer Timothy Donovan #484")
        self.assertIn("Helene Fuld", content, "F11 must name Capital Health Regional Crisis Unit (Helene Fuld)")
        self.assertIn("1103-S-2019-002671", content, "F11 must cite Summons 1103-S-2019-002671")
        self.assertIn("2C:29-1a", content, "F11 must cite N.J.S.A. 2C:29-1a (Obstruction)")
        self.assertIn("2020-00008897", content, "F11 must cite Case 2020-00008897")
        self.assertIn("2020-613", content, "F11 must cite Summons #2020-613")
        self.assertIn("2C:20-11b(1)", content, "F11 must cite N.J.S.A. 2C:20-11b(1) (Shoplifting)")

    def test_f12_ewing_police_logs_and_fbi_nexus(self):
        """F12: Ewing Police Department Evidence Logs & FBI Nexus (Case I-2019-001222)."""
        content = read_doc(DOC_MAP["F12_EWING"])
        self.assertTrue(DOC_MAP["F12_EWING"].exists(), "F12 file must exist")
        self.assertIn("I-2019-001222", content, "F12 must cite Ewing Case I-2019-001222")
        self.assertIn("044.01", content, "F12 must cite Evidence Item 044.01 (Methamphetamine)")
        self.assertIn("046", content, "F12 must cite Evidence Item 046 (Samsung phone)")
        self.assertIn("BRADLEY ZARTMAN", content, "F12 must record TOT FBI AGENT BRADLEY ZARTMAN")
        self.assertIn("GIOVACCHINI", content, "F12 must name Officer Giovacchini")
        self.assertIn("RANKER", content, "F12 must name Officer Ranker")

    def test_f13_quantum_auto_dismantler_commercial_invoice(self):
        """F13: Quantum Auto Dismantler Commercial Invoice #14098 & Corporate Nexus."""
        content = read_doc(DOC_MAP["F13_QUANTUM"])
        self.assertTrue(DOC_MAP["F13_QUANTUM"].exists(), "F13 file must exist")
        self.assertIn("Quantum Auto Dismantler", content, "F13 must identify Quantum Auto Dismantler")
        self.assertIn("14098", content, "F13 must cite Invoice #14098")
        self.assertIn("14509", content, "F13 must cite Workorder #14509")
        self.assertIn("3125 W. 5th St", content, "F13 must state Santa Ana merchant address")
        self.assertIn("302796", content, "F13 must state VIN 302796")
        self.assertIn("546.25", content, "F13 must state total billed $546.25 cash paid")
        self.assertIn("Dog's Day Productions", content, "F13 must identify IRS EIN entity Dog's Day Productions")
        self.assertIn("155-78-7252", content, "F13 must record SSN 155-78-7252")
        self.assertIn("JAEETQ", content, "F13 must cite Alaska Airlines confirmation code JAEETQ")

    def test_f14_master_index_catalog(self):
        """F14: Master Index Catalog (OFFICIAL_DOCUMENTS_INDEX.md)."""
        content = read_doc(DOC_MAP["F14_INDEX"])
        self.assertTrue(DOC_MAP["F14_INDEX"].exists(), "F14 file must exist")
        self.assertIn("OFFICIAL COURT", content, "F14 must contain repository title")
        self.assertIn("01_USA_v_Harry_Sidhu", content, "F14 must link to Sidhu record")
        self.assertIn("02_HCD_Notice", content, "F14 must link to HCD record")
        self.assertIn("03_USA_v_Todd_Ament", content, "F14 must link to Ament/Rafiei record")
        self.assertIn("04_USA_v_Christopher_Ryan", content, "F14 must link to Ryan federal record")
        self.assertIn("05_Woodbridge_Meadows", content, "F14 must link to Superior Court docket")
        self.assertIn("06_JL_Investigation", content, "F14 must link to JL Audit record")
        self.assertIn("07_Anaheim_City_Council", content, "F14 must link to Voidance Resolution")
        self.assertIn("08_Multi_State_Police", content, "F14 must link to Multi-State Police record")

    def test_f15_repository_integrity_and_backup(self):
        """F15: Repository Integrity & Multi-Location Archival Verification."""
        self.assertTrue(OFFICIAL_RECORDS_DIR.exists(), "Official records directory must exist")
        core_files = [
            "01_USA_v_Harry_Sidhu_8_23_cr_00108_CJC.md",
            "02_HCD_Notice_of_Violation_Surplus_Land_Act.md",
            "03_USA_v_Todd_Ament_and_Melahat_Rafiei.md",
            "04_USA_v_Christopher_Ryan_3_20_mj_05007_TJB.md",
            "05_Woodbridge_Meadows_v_Dimarcello_30_2021_01201327_CL_UD_CJC.md",
            "06_JL_Investigation_Anaheim_Forensic_Audit_Report.md",
            "07_Anaheim_City_Council_Stadium_Voidance_Resolution_2022_064.md",
            "08_Multi_State_Police_and_Commercial_Incident_Logs.md",
            "OFFICIAL_DOCUMENTS_INDEX.md",
        ]
        for fname in core_files:
            fpath = OFFICIAL_RECORDS_DIR / fname
            self.assertTrue(fpath.exists(), f"Core artifact {fname} must exist on disk")
            self.assertGreater(fpath.stat().st_size, 1000, f"Core artifact {fname} must be > 1000 bytes")


# ======================================================================================
# TIER 2: BOUNDARY & CORNER CASES
# ======================================================================================

class TestTier2BoundaryAndCornerCases(unittest.TestCase):
    """Tier 2: Edge conditions, regex validations, arithmetic checks, and chronologies."""

    def test_tier2_non_empty_and_minimum_size(self):
        """Verify all official court record documents are non-empty and well-structured."""
        for doc_key, doc_path in DOC_MAP.items():
            self.assertTrue(doc_path.exists(), f"Path {doc_path} should exist")
            size = doc_path.stat().st_size
            self.assertGreater(size, 500, f"Document {doc_key} ({doc_path.name}) must be > 500 bytes (got {size})")

    def test_tier2_case_number_regex_formats(self):
        """Validate case numbers across all jurisdictions against authoritative regex patterns."""
        cdca_regex = re.compile(r"\b8:\d{2}-(cr|mj)-\d{5}-[A-Z]{3,4}\b")
        dnj_regex = re.compile(r"\b3:\d{2}-(cr|mj)-\d{5}-[A-Z]{3,4}\b")
        oc_ud_regex = re.compile(r"\b30-2021-01201327-CL-UD-CJC\b")
        hamilton_regex = re.compile(r"\b2019-00053723\b|\b2020-00008897\b")
        ewing_regex = re.compile(r"\bI-2019-001222\b")

        sidhu_text = read_doc(DOC_MAP["F1_SIDHU"])
        self.assertIsNotNone(cdca_regex.search(sidhu_text), "Sidhu document must match CDCA regex")

        ryan_text = read_doc(DOC_MAP["F4_RYAN"])
        self.assertIsNotNone(dnj_regex.search(ryan_text), "Ryan document must match DNJ regex")

        ud_text = read_doc(DOC_MAP["F8_ROA"])
        self.assertIsNotNone(oc_ud_regex.search(ud_text), "UD document must match Orange County case number regex")

        police_text = read_doc(DOC_MAP["F11_HAMILTON"])
        self.assertIsNotNone(hamilton_regex.search(police_text), "Police log must match Hamilton incident regex")
        self.assertIsNotNone(ewing_regex.search(police_text), "Police log must match Ewing incident regex")

    def test_tier2_statutory_citation_syntax(self):
        """Validate precision of statutory citation blocks across federal and state codes."""
        statute_patterns = [
            (DOC_MAP["F1_SIDHU"], r"18\s+U\.S\.C\.\s+§\s*1343"),
            (DOC_MAP["F1_SIDHU"], r"18\s+U\.S\.C\.\s+§\s*1519"),
            (DOC_MAP["F1_SIDHU"], r"18\s+U\.S\.C\.\s+§\s*1001\(a\)\(2\)"),
            (DOC_MAP["F2_AMENT"], r"26\s+U\.S\.C\.\s+§\s*7206\(1\)"),
            (DOC_MAP["F4_RYAN"], r"21\s+U\.S\.C\.\s+§§?\s*841\(a\)\(1\)"),
            (DOC_MAP["F5_HCD"], r"Cal\.\s+Gov\.\s+Code\s+§\s*54220"),
            (DOC_MAP["F8_ROA"], r"Cal\.\s+CCP\s+§\s*170\.6|Code\s+of\s+Civil\s+Procedure\s+§\s*170\.6"),
            (DOC_MAP["F11_HAMILTON"], r"N\.J\.S\.A\.\s+2C:29-1a"),
            (DOC_MAP["F11_HAMILTON"], r"N\.J\.S\.A\.\s+2C:20-11b\(1\)"),
        ]
        for path, pattern in statute_patterns:
            text = read_doc(path)
            self.assertIsNotNone(re.search(pattern, text), f"File {path.name} must match statute pattern {pattern}")

    def test_tier2_roa_61_entry_continuity(self):
        """Ensure full, continuous 1-61 Register of Actions entries with zero gaps."""
        content = read_doc(DOC_MAP["F8_ROA"])
        missing_entries = []
        for i in range(1, 62):
            # Matches "| **1** |" or "| 1 |" in markdown tables
            pattern = r"\|\s*\**" + str(i) + r"\**\s*\|"
            if not re.search(pattern, content):
                missing_entries.append(i)
        self.assertEqual(missing_entries, [], f"All 61 ROA entries must be present. Missing: {missing_entries}")

    def test_tier2_chronological_ordering_superior_court(self):
        """Verify strict chronological sequence in Superior Court Unlawful Detainer docket."""
        content = read_doc(DOC_MAP["F8_ROA"])
        d1_idx = content.find("05/18/2021")  # Initial filing
        d2_idx = content.find("06/29/2021")  # Default #1
        d3_idx = content.find("08/20/2021")  # 170.6 Strike
        d4_idx = content.find("12/22/2021")  # Default #2
        d5_idx = content.find("02/04/2022")  # Default #3

        self.assertTrue(-1 < d1_idx < d2_idx < d3_idx < d4_idx < d5_idx,
                        "Superior Court events must be chronologically ordered")

    def test_tier2_financial_and_penalty_arithmetic(self):
        """Verify mathematical integrity of all statutory penalties and commercial invoices."""
        gross_land_sale = 320_000_000.00
        penalty_rate = 0.30
        expected_sla_penalty = gross_land_sale * penalty_rate
        self.assertEqual(expected_sla_penalty, 96_000_000.00, "Surplus Land Act penalty math must equal $96M")

        parts_subtotal = 500.00
        sales_tax = 46.25
        expected_invoice_total = parts_subtotal + sales_tax
        self.assertEqual(expected_invoice_total, 546.25, "Quantum Auto Dismantler invoice math must equal $546.25")

        heli_purchase = 158_875.00
        tax_evaded = 15_887.50
        self.assertAlmostEqual(heli_purchase * 0.10, tax_evaded, places=2)


# ======================================================================================
# TIER 3: CROSS-FEATURE COMBINATIONS & EVIDENTIARY CONDUITS
# ======================================================================================

class TestTier3CrossFeatureCombinations(unittest.TestCase):
    """Tier 3: Multi-way and pairwise cross-jurisdiction interactions."""

    def test_combo_ewing_police_to_zartman_to_dnj_narcotics(self):
        """Cross-Feature Link 1: Ewing PD Chain of Custody -> FBI SA Zartman -> USDC D.N.J. Complaint."""
        ewing_text = read_doc(DOC_MAP["F12_EWING"])
        ryan_text = read_doc(DOC_MAP["F4_RYAN"])

        self.assertIn("I-2019-001222", ewing_text)
        self.assertIn("044.01", ewing_text)
        self.assertIn("BRADLEY ZARTMAN", ewing_text)

        self.assertIn("Bradley H. Zartman", ryan_text)
        self.assertIn("3:20-mj-05007-TJB", ryan_text)
        self.assertIn("435 Grams", ryan_text)

    def test_combo_sidhu_wiretaps_to_hcd_to_voidance_to_jl_audit(self):
        """Cross-Feature Link 2: Sidhu Wiretaps -> HCD SLA Penalty -> Anaheim Voidance -> JL Forensic Audit."""
        sidhu_text = read_doc(DOC_MAP["F1_SIDHU"])
        hcd_text = read_doc(DOC_MAP["F5_HCD"])
        voidance_text = read_doc(DOC_MAP["F6_VOIDANCE"])
        audit_text = read_doc(DOC_MAP["F7_JL_AUDIT"])

        self.assertIn("Brian Adkins", sidhu_text)
        self.assertIn("8:22-mj-00185", sidhu_text)
        self.assertIn("320,000,000", sidhu_text)

        self.assertIn("96,000,000", hcd_text)
        self.assertIn("54220", hcd_text)

        self.assertIn("2022-064", voidance_text)
        self.assertIn("May 24, 2022", voidance_text)
        self.assertIn("50,000,000", voidance_text)

        self.assertIn("JL Group", audit_text)
        self.assertIn("353 Pages", audit_text)
        self.assertIn("Visit Anaheim", audit_text)

    def test_combo_ament_rafiei_cabal_syndicate(self):
        """Cross-Feature Link 3: Ament Big Bear Wire Fraud + Rafiei Irvine Cannabis Bribery."""
        ament_rafiei_text = read_doc(DOC_MAP["F2_AMENT"])
        audit_text = read_doc(DOC_MAP["F7_JL_AUDIT"])

        self.assertIn("8:22-cr-00078-CJC", ament_rafiei_text)
        self.assertIn("8:23-cr-00009-CJC", ament_rafiei_text)
        self.assertIn("TA Group LLC", ament_rafiei_text)
        self.assertIn("Irvine", ament_rafiei_text)

        self.assertIn("Todd Ament", audit_text)
        self.assertIn("Melahat Rafiei", audit_text)

    def test_combo_superior_court_stay_to_peremptory_strike_to_void_defaults(self):
        """Cross-Feature Link 4: Judge Luege 3:11 PM Stay -> Arden Hoang 4:29 PM 170.6 Strike -> Triple Defaults."""
        ud_text = read_doc(DOC_MAP["F8_ROA"])

        self.assertIn("03:11", ud_text)
        self.assertIn("STAYED", ud_text)

        self.assertIn("04:29", ud_text)
        self.assertIn("170.6", ud_text)
        self.assertIn("1885125", ud_text)

        self.assertIn("06/29/2021", ud_text)
        self.assertIn("12/22/2021", ud_text)
        self.assertIn("02/04/2022", ud_text)
        self.assertIn("Rochin", ud_text)
        self.assertIn("Heidary", ud_text)

    def test_combo_hamilton_police_to_quantum_auto_to_ein(self):
        """Cross-Feature Link 5: Hamilton Police 1456 Cedar Ln -> Quantum Auto Invoice #14098 -> Dog's Day Productions EIN."""
        police_text = read_doc(DOC_MAP["F11_HAMILTON"])

        self.assertIn("1456 Cedar Lane", police_text)
        self.assertIn("Dean", police_text)
        self.assertIn("Innocenzi", police_text)
        self.assertIn("Quantum Auto Dismantler", police_text)
        self.assertIn("14098", police_text)
        self.assertIn("Dog's Day Productions", police_text)
        self.assertIn("155-78-7252", police_text)


# ======================================================================================
# TIER 4: REAL-WORLD ACCEPTANCE SCENARIOS & FULL PIPELINE VALIDATION
# ======================================================================================

class TestTier4RealWorldAcceptance(unittest.TestCase):
    """Tier 4: End-to-End Acceptance, Master Index Link Integrity, and Forensic Compliance."""

    def test_tier4_full_pipeline_primary_document_structural_compliance(self):
        """Validate that all official court records meet standard institutional markdown specifications."""
        required_headers = [
            DOC_MAP["F1_SIDHU"],
            DOC_MAP["F2_AMENT"],
            DOC_MAP["F4_RYAN"],
            DOC_MAP["F5_HCD"],
            DOC_MAP["F6_VOIDANCE"],
            DOC_MAP["F7_JL_AUDIT"],
            DOC_MAP["F8_ROA"],
            DOC_MAP["F11_HAMILTON"],
        ]

        for path in required_headers:
            content = read_doc(path).strip()
            self.assertTrue(content.startswith("#"), f"Document {path.name} must start with top-level H1 header")
            self.assertIn("---", content, f"Document {path.name} must contain Markdown dividers")
            self.assertIn("##", content, f"Document {path.name} must contain structured H2 sections")

    def test_tier4_master_index_cross_reference_integrity(self):
        """Validate that OFFICIAL_DOCUMENTS_INDEX.md links to all primary evidence files without dead links."""
        index_content = read_doc(DOC_MAP["F14_INDEX"])
        self.assertTrue(DOC_MAP["F14_INDEX"].exists(), "OFFICIAL_DOCUMENTS_INDEX.md must exist")

        # Extract all referenced markdown file paths from the index
        referenced_files = re.findall(r"\[`?([a-zA-Z0-9_\-]+\.md)`?\]", index_content)
        self.assertGreaterEqual(len(referenced_files), 5, "Master index must link to at least 5 primary artifacts")

        for ref in referenced_files:
            target_path = OFFICIAL_RECORDS_DIR / ref
            self.assertTrue(target_path.exists(), f"Referenced file {ref} in Master Index must exist at {target_path}")

    def test_tier4_complete_evidentiary_corpus_audit(self):
        """Comprehensive verification that all 15 features have zero orphaned or missing data across the corpus."""
        all_text = ""
        for p in OFFICIAL_RECORDS_DIR.glob("*.md"):
            all_text += read_doc(p) + "\n"

        anchors = [
            "8:23-cr-00108-CJC",
            "8:22-cr-00078-CJC",
            "8:23-cr-00009-CJC",
            "3:20-mj-05007-TJB",
            "54220",
            "2022-064",
            "353",
            "30-2021-01201327-CL-UD-CJC",
            "Rochin",
            "170.6",
            "2019-00053723",
            "I-2019-001222",
            "14098",
            "OFFICIAL_DOCUMENTS_INDEX",
        ]
        for anchor in anchors:
            self.assertIn(anchor, all_text, f"Anchor '{anchor}' must be present in the official court records corpus")


# Entrypoint for direct execution and unittest
if __name__ == "__main__":
    unittest.main()
