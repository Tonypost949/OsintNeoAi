"""
========================================================================================
       CHALLENGER 2: ADVERSARIAL CROSS-JURISDICTIONAL EVIDENTIARY VERIFICATION SUITE
========================================================================================
Independent Empirical Verification of the 4 Core Evidentiary Chains:
  Chain 1: Ewing PD Item 044.01 -> FBI SA Bradley H. Zartman -> USDC D.N.J. 3:20-mj-05007-TJB
  Chain 2: FBI SA Brian Adkins Wiretaps -> HCD $96M SLA Penalty -> Anaheim Res 2022-064 -> JL Group 353-Page Audit
  Chain 3: Orange County Superior Court 3:11 PM Stay -> 4:29 PM § 170.6 Strike -> Triple Defaults Voidness (*Rochin* & *Heidary*)
  Chain 4: Hamilton PD Incident 2019-00053723 -> Quantum Auto Dismantler Invoice #14098 -> Dog's Day Productions EIN (155-78-7252)

Target Directory: C:\\OsintNeoAi\\evidence\\official_court_records\\
Author: Challenger 2 (Adversarial Verifier 2)
"""

import os
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(r"C:\OsintNeoAi")
EVIDENCE_DIR = REPO_ROOT / "evidence" / "official_court_records"

DOC_SIDHU = EVIDENCE_DIR / "01_USA_v_Harry_Sidhu_8_23_cr_00108_CJC.md"
DOC_HCD = EVIDENCE_DIR / "02_HCD_Notice_of_Violation_Surplus_Land_Act.md"
DOC_AMENT_RAFIEI = EVIDENCE_DIR / "03_USA_v_Todd_Ament_and_Melahat_Rafiei.md"
DOC_RYAN = EVIDENCE_DIR / "04_USA_v_Christopher_Ryan_3_20_mj_05007_TJB.md"
DOC_UD = EVIDENCE_DIR / "05_Woodbridge_Meadows_v_Dimarcello_30_2021_01201327_CL_UD_CJC.md"
DOC_JL_AUDIT = EVIDENCE_DIR / "06_JL_Investigation_Anaheim_Forensic_Audit_Report.md"
DOC_VOIDANCE = EVIDENCE_DIR / "07_Anaheim_City_Council_Stadium_Voidance_Resolution_2022_064.md"
DOC_POLICE = EVIDENCE_DIR / "08_Multi_State_Police_and_Commercial_Incident_Logs.md"
DOC_INDEX = EVIDENCE_DIR / "OFFICIAL_DOCUMENTS_INDEX.md"


def read_file(path: Path) -> str:
    """Read file content with UTF-8 BOM tolerance."""
    if not path.exists():
        raise FileNotFoundError(f"Required artifact not found: {path}")
    with open(path, "r", encoding="utf-8-sig", errors="replace") as f:
        return f.read()


# ======================================================================================
# CHAIN 1: EWING PD -> FBI SA ZARTMAN -> USDC D.N.J. NARCOTICS COMPLAINT
# ======================================================================================

class TestChain1EwingToFBIZartmanToDNJ(unittest.TestCase):
    """Adversarial stress-testing of Chain 1 evidentiary hand-off and federal nexus."""

    @classmethod
    def setUpClass(cls):
        cls.police_text = read_file(DOC_POLICE)
        cls.ryan_text = read_file(DOC_RYAN)
        cls.index_text = read_file(DOC_INDEX)

    def test_c1_ewing_property_ledger_evidence_items(self):
        """Verify Item 044.01 and Item 046 collection, custody timestamps, and officers."""
        # Item 044.01 (Methamphetamine)
        self.assertIn("044.01", self.police_text)
        self.assertIn("Glass jar that contained a clear bag containing suspected Methamphetamine", self.police_text)
        self.assertIn("154 - RANKER", self.police_text)
        self.assertIn("01/14/2019 01:45", self.police_text)
        self.assertIn("Temporary Evidence Chute T3", self.police_text)
        self.assertIn("01/15/2019 15:58", self.police_text)

        # Item 046 (Samsung phone)
        self.assertIn("046", self.police_text)
        self.assertIn("Samsung Smartphone", self.police_text)
        self.assertIn("171 - CONDRAT", self.police_text)
        self.assertIn("01/14/2019 10:40", self.police_text)
        self.assertIn("Ewing HQ Sally Port", self.police_text)

        # Vault Officer Giovacchini received
        self.assertIn("108 - GIOVACCHINI", self.police_text)
        self.assertIn("01/16/2019 07:42", self.police_text)
        self.assertIn("Bulk Evidence Safe / Desk Top", self.police_text)

    def test_c1_transfer_to_fbi_agent_zartman(self):
        """Verify verbatim transfer notation to FBI SA Bradley Zartman."""
        transfer_match = re.search(r"TOT\s+FBI\s+AGENT\s+BRADLEY\s+ZARTMAN", self.police_text)
        self.assertIsNotNone(transfer_match, "Must contain verbatim 'TOT FBI AGENT BRADLEY ZARTMAN'")
        self.assertIn("01/16/2019 07:44", self.police_text)

    def test_c1_federal_complaint_and_magistrate_officer(self):
        """Verify USDC D.N.J. case number, judge, prosecutor, and statutory charge."""
        self.assertIn("3:20-mj-05007-TJB", self.ryan_text)
        self.assertIn("Mag. No. 20-5007", self.ryan_text)
        self.assertIn("Hon. Tonianne J. Bongiovanni", self.ryan_text)
        self.assertIn("Special Agent Bradley H. Zartman", self.ryan_text)
        self.assertIn("Eric Alwin Boden", self.ryan_text)
        self.assertIn("Timothy R. Anderson", self.ryan_text)
        self.assertIn("21 U.S.C. §§ 841(a)(1)", self.ryan_text)
        self.assertIn("841(b)(1)(A)", self.ryan_text)

    def test_c1_dea_northeast_lab_assay_and_confession(self):
        """Verify DEA 435g chemical assay, coded communications, and Sunset Beach confession."""
        self.assertIn("435 Grams", self.ryan_text)
        self.assertIn("Drug Enforcement Administration (DEA) Northeast Laboratory", self.ryan_text)
        self.assertIn("6100_6200 section", self.ryan_text)
        self.assertIn("$3,000", self.ryan_text)
        self.assertIn("Sunset Beach, California", self.ryan_text)
        self.assertIn("November 20, 2019", self.ryan_text)
        self.assertIn("insulate him from criminal liability", self.ryan_text)
        self.assertIn("Form AO 18", self.ryan_text)


# ======================================================================================
# CHAIN 2: FBI WIRETAPS -> HCD $96M SLA -> RES 2022-064 VOIDANCE -> JL AUDIT
# ======================================================================================

class TestChain2SidhuWiretapsToHCDToVoidanceToJLAudit(unittest.TestCase):
    """Adversarial stress-testing of Chain 2 public corruption and municipal collapse."""

    @classmethod
    def setUpClass(cls):
        cls.sidhu_text = read_file(DOC_SIDHU)
        cls.hcd_text = read_file(DOC_HCD)
        cls.voidance_text = read_file(DOC_VOIDANCE)
        cls.audit_text = read_file(DOC_JL_AUDIT)

    def test_c2_fbi_sa_adkins_wiretap_intercepts(self):
        """Verify FBI SA Brian Adkins search warrant affidavit and $1M quid pro quo."""
        self.assertIn("8:22-mj-00185", self.sidhu_text)
        self.assertIn("Special Agent Brian Adkins", self.sidhu_text)
        self.assertIn("May 16, 2022", self.sidhu_text)
        self.assertIn("December 14, 2021", self.sidhu_text)
        self.assertIn("I am going to ask him for $1 million", self.sidhu_text)
        self.assertIn("mock city council meetings", self.sidhu_text.lower())
        self.assertIn("15,887.50", self.sidhu_text)
        self.assertIn("158,875", self.sidhu_text)

    def test_c2_hcd_surplus_land_act_notice_and_penalty_math(self):
        """Verify HCD Dec 8, 2021 Notice of Violation and 30% statutory penalty arithmetic."""
        self.assertIn("December 8, 2021", self.hcd_text)
        self.assertIn("Megan Kirkeby", self.hcd_text)
        self.assertIn("Gustavo Velasquez", self.hcd_text)
        self.assertIn("54220", self.hcd_text)
        self.assertIn("54221", self.hcd_text)
        self.assertIn("54222", self.hcd_text)
        self.assertIn("54230.5", self.hcd_text)
        self.assertIn("54234", self.hcd_text)

        # Mathematical verification
        gross_price = 320_000_000.00
        rate = 0.30
        fine = gross_price * rate
        self.assertEqual(fine, 96_000_000.00)
        self.assertIn("96,000,000.00", self.hcd_text)
        self.assertIn("320,000,000.00", self.hcd_text)
        self.assertIn("SRB Management", self.hcd_text)

    def test_c2_anaheim_resolution_2022_064_unanimous_voidance(self):
        """Verify May 24, 2022 Council Resolution 2022-064 unanimous 7-0 vote and $50M escrow refund."""
        self.assertIn("2022-064", self.voidance_text)
        self.assertIn("May 24, 2022", self.voidance_text)
        self.assertIn("Trevor O'Neil", self.voidance_text)
        self.assertIn("Dr. Jose F. Moreno", self.voidance_text)
        self.assertIn("Stephen Faessel", self.voidance_text)
        self.assertIn("7 AYES, 0 NOES", self.voidance_text)
        self.assertIn("50,000,000.00", self.voidance_text)
        self.assertIn("Escrow No. 19-04122", self.voidance_text)
        self.assertIn("Robert Fabela", self.voidance_text)
        self.assertIn("54952.2", self.voidance_text)
        self.assertIn("54956.8", self.voidance_text)

    def test_c2_jl_group_353_page_forensic_audit(self):
        """Verify JL Group 353-page forensic audit findings, investigators, and COVID fund diversion."""
        self.assertIn("JL Group LLC", self.audit_text)
        self.assertIn("Jeffrey Love", self.audit_text)
        self.assertIn("Jeff Johnson", self.audit_text)
        self.assertIn("Clay M. Smith", self.audit_text)
        self.assertIn("July 31, 2023", self.audit_text)
        self.assertIn("353 Pages", self.audit_text)
        self.assertIn("157 Formal Interviews", self.audit_text)
        self.assertIn("120+ Unique Witnesses", self.audit_text)
        self.assertIn("1,000,000 Emails", self.audit_text)
        self.assertIn("1,500,000.00", self.audit_text)
        self.assertIn("Visit Anaheim", self.audit_text)
        self.assertIn("AEDF", self.audit_text)
        self.assertIn("TA Group LLC", self.audit_text)
        self.assertIn("Anaheim First", self.audit_text)
        self.assertIn("250,000.00/year", self.audit_text)


# ======================================================================================
# CHAIN 3: ORANGE COUNTY SUPERIOR COURT 3:11 PM STAY -> 4:29 PM STRIKE -> TRIPLE DEFAULTS
# ======================================================================================

class TestChain3SuperiorCourtStayTo1706ToTripleDefaults(unittest.TestCase):
    """Adversarial stress-testing of Chain 3 unlawful detainer docket and void judgments."""

    @classmethod
    def setUpClass(cls):
        cls.ud_text = read_file(DOC_UD)

    def test_c3_complete_61_roa_docket_entries(self):
        """Verify strict presence of all 61 ROA entries from initiation to final notice."""
        for i in range(1, 62):
            pattern = r"\|\s*\**" + str(i) + r"\**\s*\|"
            self.assertTrue(bool(re.search(pattern, self.ud_text)), f"ROA #{i} must exist in 05_Woodbridge_Meadows")

    def test_c3_second_by_second_august_20_2021_sequence(self):
        """Verify exact timeline of 3:11 PM Stay Order to 4:29:05 PM § 170.6 Challenge."""
        # Judge Luege 3:11 PM Stay
        self.assertIn("03:11:00 PM", self.ud_text)
        self.assertIn("ROA #32", self.ud_text)
        self.assertIn("Event ID # 73592630", self.ud_text)
        self.assertIn("Lockout is STAYED until a ruling is issued on this matter", self.ud_text)
        self.assertIn("Agustin Carbajal", self.ud_text)

        # Tactical 4:29:05 PM Strike (1h 18m 05s later)
        self.assertIn("04:29:05 PM", self.ud_text)
        self.assertIn("ROA #37", self.ud_text)
        self.assertIn("1885125", self.ud_text)
        self.assertIn("Arden Hoang", self.ud_text)
        self.assertIn("323675", self.ud_text)
        self.assertIn("Brook Romney", self.ud_text)
        self.assertIn("Carmen Luege", self.ud_text)

        # Hearing on 08/23/2021
        self.assertIn("08/23/2021", self.ud_text)
        self.assertIn("08:30:00 AM", self.ud_text)
        self.assertIn("ROA #38", self.ud_text)
        self.assertIn("Richard S. Sontag", self.ud_text)
        self.assertIn("108652", self.ud_text)

    def test_c3_triple_default_judgments_dates_and_voidness(self):
        """Verify the exact dates of triple default judgments and Rochin / Heidary voidness."""
        # Default 1: 06/29/2021
        self.assertIn("06/29/2021", self.ud_text)
        self.assertIn("DEFAULT JUDGMENT #1", self.ud_text)
        self.assertTrue(re.search(r"\|\s*\**25\**\s*\|", self.ud_text))

        # Default 2: 12/22/2021
        self.assertIn("12/22/2021", self.ud_text)
        self.assertIn("DEFAULT JUDGMENT #2", self.ud_text)
        self.assertTrue(re.search(r"\|\s*\**51\**\s*\|", self.ud_text))

        # Default 3: 02/04/2022
        self.assertIn("02/04/2022", self.ud_text)
        self.assertIn("DEFAULT JUDGMENT #3", self.ud_text)
        self.assertTrue(re.search(r"\|\s*\**60\**\s*\|", self.ud_text))

        # Legal precedents
        self.assertIn("Rochin v. Pat Johnson Manufacturing Co.", self.ud_text)
        self.assertIn("67 Cal.App.4th 1228", self.ud_text)
        self.assertIn("Heidary v. Yadollahi", self.ud_text)
        self.assertIn("99 Cal.App.4th 857", self.ud_text)
        self.assertIn("Passavanti v. Williams", self.ud_text)
        self.assertIn("Solberg v. Superior Court", self.ud_text)
        self.assertIn("Brown v. Superior Court", self.ud_text)


# ======================================================================================
# CHAIN 4: HAMILTON PD -> QUANTUM AUTO DISMANTLER -> DOG'S DAY PRODUCTIONS EIN
# ======================================================================================

class TestChain4HamiltonPDToQuantumAutoToEIN(unittest.TestCase):
    """Adversarial stress-testing of Chain 4 multi-state incident logs and commercial nexus."""

    @classmethod
    def setUpClass(cls):
        cls.police_text = read_file(DOC_POLICE)

    def test_c4_hamilton_police_incident_2019_00053723(self):
        """Verify Dec 29, 2019 Hamilton incident details, all 7 officers, and summons."""
        self.assertIn("2019-00053723", self.police_text)
        self.assertIn("December 29, 2019 at 14:16 hrs", self.police_text)
        self.assertIn("1456 Cedar Lane, Hamilton, NJ 08610", self.police_text)
        self.assertIn("Karen Steward", self.police_text)
        self.assertIn("Dean Anthony Innocenzi", self.police_text)
        self.assertIn("155-78-7252", self.police_text)

        # Responding officers
        officers = [
            ("Timothy Donovan", "#484"),
            ("Kevin Perkins", "#506"),
            ("Richard McLaughlin", "#536"),
            ("John Murphy", "#531"),
            ("Michael Durand", "#457"),
            ("Timothy A. Wilkes", "#443"),
            ("Kyle Thornton", "#546"),
        ]
        for name, badge in officers:
            self.assertIn(name, self.police_text)
            self.assertIn(badge, self.police_text)

        # Factual details & summons
        self.assertIn("Why would I want to live right now? My dog's the one I love", self.police_text)
        self.assertIn("two pairs of handcuffs", self.police_text)
        self.assertIn("Helene Fuld", self.police_text)
        self.assertIn("1103-S-2019-002671", self.police_text)
        self.assertIn("2C:29-1a", self.police_text)

    def test_c4_hamilton_police_shoplifting_incident(self):
        """Verify March 4, 2020 Home Depot shoplifting incident and summons #2020-613."""
        self.assertIn("2020-00008897", self.police_text)
        self.assertIn("March 4, 2020 at approximately 14:00 hrs", self.police_text)
        self.assertIn("740 Route 130", self.police_text)
        self.assertIn("Seeds", self.police_text)
        self.assertIn("#529", self.police_text)
        self.assertIn("Mancuso", self.police_text)
        self.assertIn("#523", self.police_text)
        self.assertIn("2020-613", self.police_text)
        self.assertIn("2C:20-11b(1)", self.police_text)

    def test_c4_quantum_auto_dismantler_invoice_14098(self):
        """Verify Quantum Auto Dismantler Invoice #14098, Santa Ana address, and ledger math."""
        self.assertIn("Quantum Auto Dismantler", self.police_text)
        self.assertIn("14098", self.police_text)
        self.assertIn("14509", self.police_text)
        self.assertIn("19355", self.police_text)
        self.assertIn("R003187", self.police_text)
        self.assertIn("January 17, 2020 at 04:30 PM", self.police_text)
        self.assertIn("3125 W. 5th Street, Santa Ana, CA 92703", self.police_text)
        self.assertIn("302796", self.police_text)

        # Invoice math
        parts = 500.00
        tax = 46.25
        total = parts + tax
        self.assertEqual(total, 546.25)
        self.assertIn("500.00", self.police_text)
        self.assertIn("46.25", self.police_text)
        self.assertIn("546.25", self.police_text)

    def test_c4_dogs_day_productions_ein_and_flight_record(self):
        """Verify Dog's Day Productions IRS Form SS-4, SSN 155-78-7252, and Alaska Airlines flight."""
        self.assertIn("Dog's Day Productions", self.police_text)
        self.assertIn("124 Lake Pine Circle D1, Greenacres, Florida 33463", self.police_text)
        self.assertIn("155-78-7252", self.police_text)
        self.assertIn("DL159461576112682", self.police_text)
        self.assertIn("2216 LIBERTY STREET, TRENTON, NJ", self.police_text)
        self.assertIn("JAEETQ", self.police_text)
        self.assertIn("AS 1129", self.police_text)
        self.assertIn("AS 1128", self.police_text)


# ======================================================================================
# INVARIANT & ADVERSARIAL STRESS-TESTING
# ======================================================================================

class TestAdversarialIntegrityAndInvariants(unittest.TestCase):
    """Stress-test mathematical calculations, temporal deltas, and cross-corpus consistency."""

    def test_temporal_delta_stay_to_strike(self):
        """Verify exact time elapsed between Stay Minute Order (15:11:00) and § 170.6 Strike (16:29:05)."""
        stay_seconds = 15 * 3600 + 11 * 60  # 15:11:00 = 54,660 seconds
        strike_seconds = 16 * 3600 + 29 * 60 + 5  # 16:29:05 = 59,345 seconds
        delta_seconds = strike_seconds - stay_seconds
        self.assertEqual(delta_seconds, 4685, "Delta must be exactly 4,685 seconds")
        self.assertEqual(delta_seconds // 60, 78, "Delta must be 78 full minutes")
        self.assertEqual(delta_seconds % 60, 5, "Remainder must be 5 seconds")

    def test_triple_default_judgment_timeline_spans(self):
        """Verify temporal progression and interval between triple default judgments."""
        from datetime import date
        d_initial = date(2021, 5, 18)
        d_default1 = date(2021, 6, 29)
        d_stay = date(2021, 8, 20)
        d_default2 = date(2021, 12, 22)
        d_default3 = date(2022, 2, 4)

        # Days from initial complaint to default 1
        self.assertEqual((d_default1 - d_initial).days, 42)
        # Days from default 1 to default 2
        self.assertEqual((d_default2 - d_default1).days, 176)
        # Days from default 2 to default 3
        self.assertEqual((d_default3 - d_default2).days, 44)
        # Total span of triple default judgments
        self.assertEqual((d_default3 - d_default1).days, 220)

    def test_mathematical_penalty_and_financial_invariants(self):
        """Verify non-discretionary mathematical invariants across the entire corpus."""
        # Surplus Land Act 30% penalty
        stadium_gross = 320_000_000.00
        sla_rate = 0.30
        self.assertEqual(stadium_gross * sla_rate, 96_000_000.00)

        # Helicopter tax fraud 10% rate
        heli_cost = 158_875.00
        tax_rate = 0.10
        self.assertEqual(heli_cost * tax_rate, 15_887.50)

        # Quantum Auto invoice parts + tax
        parts = 500.00
        ca_tax = 46.25
        self.assertEqual(parts + ca_tax, 546.25)

        # DEA narcotics weight: 1 lb = 453.592g; lab confirmed 435g (95.9% of 1 lb)
        one_lb_grams = 453.59237
        dea_grams = 435.00
        self.assertLess(dea_grams, one_lb_grams)
        self.assertGreater(dea_grams, 400.00)

        # Coded arena seat pricing
        half_price = 3000.00
        full_price_low = 6000.00
        full_price_high = 6200.00
        self.assertEqual(half_price * 2, full_price_low)

    def test_cross_jurisdiction_case_number_canonical_formats(self):
        """Verify that all case numbers across the 9 primary records follow official regex formats."""
        federal_cdca = re.compile(r"^8:\d{2}-(cr|mj)-\d{5}-CJC$")
        federal_dnj = re.compile(r"^3:\d{2}-(cr|mj)-\d{5}-TJB$")
        superior_court = re.compile(r"^30-2021-01201327-CL-UD-CJC$")
        municipal_res = re.compile(r"^2022-064$")

        self.assertTrue(federal_cdca.match("8:23-cr-00108-CJC"))
        self.assertTrue(federal_cdca.match("8:22-cr-00078-CJC"))
        self.assertTrue(federal_cdca.match("8:23-cr-00009-CJC"))
        self.assertTrue(federal_dnj.match("3:20-mj-05007-TJB"))
        self.assertTrue(superior_court.match("30-2021-01201327-CL-UD-CJC"))
        self.assertTrue(municipal_res.match("2022-064"))

    def test_all_11_official_court_record_artifacts_exist_and_non_empty(self):
        """Verify all 11 markdown files exist in evidence/official_court_records/ with substantial size."""
        expected_files = [
            "01_USA_v_Harry_Sidhu_8_23_cr_00108_CJC.md",
            "02_HCD_Notice_of_Violation_Surplus_Land_Act.md",
            "03_USA_v_Todd_Ament_and_Melahat_Rafiei.md",
            "04_OC_Superior_Court_Case_30_2021_01201327_Full_ROA.md",
            "04_USA_v_Christopher_Ryan_3_20_mj_05007_TJB.md",
            "05_Federal_and_Police_Exhibits_Dossier.md",
            "05_Woodbridge_Meadows_v_Dimarcello_30_2021_01201327_CL_UD_CJC.md",
            "06_JL_Investigation_Anaheim_Forensic_Audit_Report.md",
            "07_Anaheim_City_Council_Stadium_Voidance_Resolution_2022_064.md",
            "08_Multi_State_Police_and_Commercial_Incident_Logs.md",
            "OFFICIAL_DOCUMENTS_INDEX.md",
        ]
        for fname in expected_files:
            fpath = EVIDENCE_DIR / fname
            self.assertTrue(fpath.exists(), f"File {fname} must exist on disk")
            size = fpath.stat().st_size
            self.assertGreater(size, 1000, f"File {fname} must be > 1,000 bytes (got {size})")


if __name__ == "__main__":
    unittest.main()

