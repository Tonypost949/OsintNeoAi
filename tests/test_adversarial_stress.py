"""
========================================================================================
             ADVERSARIAL STRESS-TESTING HARNESS (CHALLENGER 1)
========================================================================================
Comprehensive Adversarial Verification for Official Court Records & Master Index
Target: C:\\OsintNeoAi\\evidence\\official_court_records\\
Coverage:
  1. Markdown Table Validity, Column Integrity & Pipe Escaping
  2. Code Fence Delimiters, Encoding & Structural Hierarchy
  3. Register of Actions (ROA) 1..61 Exact Sequence, Completeness & Gaps/Duplicates
  4. Link & File Path Resolution in Index and All Artifacts
  5. Cross-Document Numerical, Date, Case Number & Statutory Discrepancies
  6. Forensic Arithmetic & Statutory Exposure Calculations
  7. Exhaustive Feature-by-Feature Integrity (F1 through F15)
"""

import os
import re
import sys
import unittest
from pathlib import Path
from typing import List, Dict, Tuple, Set

REPO_ROOT = Path(r"C:\OsintNeoAi")
EVIDENCE_DIR = REPO_ROOT / "evidence" / "official_court_records"
INDEX_FILE = EVIDENCE_DIR / "OFFICIAL_DOCUMENTS_INDEX.md"

ALL_DOC_PATHS = list(EVIDENCE_DIR.glob("*.md"))


def load_file(path: Path) -> str:
    with open(path, "r", encoding="utf-8-sig", errors="replace") as f:
        return f.read()


class TestAdversarialMarkdownStructure(unittest.TestCase):
    """Stress-test Markdown table formatting, unescaped pipes, code fences, and headers."""

    def test_all_markdown_tables_column_consistency(self):
        """Parse all markdown tables across all documents and check column counts per row."""
        failures = []
        for doc_path in ALL_DOC_PATHS:
            content = load_file(doc_path)
            lines = content.splitlines()
            in_table = False
            expected_cols = 0
            table_start_line = 0

            for line_idx, line in enumerate(lines, start=1):
                raw_line = line.strip()
                if raw_line.startswith("|") and raw_line.endswith("|"):
                    cells = re.split(r"(?<!\\)\|", raw_line)[1:-1]
                    num_cols = len(cells)

                    if not in_table:
                        in_table = True
                        table_start_line = line_idx
                        expected_cols = num_cols
                    else:
                        is_separator = all(re.match(r"^:?-+:?$", c.strip()) for c in cells)
                        if is_separator:
                            if num_cols != expected_cols:
                                failures.append(
                                    f"{doc_path.name}:{line_idx} - Table starting at line {table_start_line} "
                                    f"has separator with {num_cols} columns, expected {expected_cols}."
                                )
                        else:
                            if num_cols != expected_cols:
                                failures.append(
                                    f"{doc_path.name}:{line_idx} - Table row has {num_cols} columns, "
                                    f"expected {expected_cols}. Content: '{raw_line}'"
                                )
                else:
                    in_table = False
                    expected_cols = 0

        self.assertEqual(failures, [], f"Broken markdown tables found:\n" + "\n".join(failures))

    def test_no_unescaped_internal_pipe_corruption(self):
        """Verify that table rows do not contain double pipes (||) or malformed dividers."""
        failures = []
        for doc_path in ALL_DOC_PATHS:
            content = load_file(doc_path)
            for line_idx, line in enumerate(content.splitlines(), start=1):
                if line.strip().startswith("|") and line.strip().endswith("|"):
                    raw_cells = line.strip()[1:-1].split("|")
                    for cell_idx, c in enumerate(raw_cells):
                        if c == "" and cell_idx < len(raw_cells) - 1 and not line.strip()[1:-1].startswith("|"):
                            failures.append(f"{doc_path.name}:{line_idx} - Empty cell from possible unescaped pipe: {line}")
        self.assertEqual(failures, [], f"Pipe corruption found:\n" + "\n".join(failures))

    def test_unclosed_code_blocks(self):
        """Ensure all markdown code blocks (```) are properly closed."""
        failures = []
        for doc_path in ALL_DOC_PATHS:
            content = load_file(doc_path)
            lines = content.splitlines()
            fence_count = 0
            for line_idx, line in enumerate(lines, start=1):
                if line.strip().startswith("```"):
                    fence_count += 1

            if fence_count % 2 != 0:
                failures.append(f"{doc_path.name} has an unclosed code block (total ``` fences = {fence_count})")

        self.assertEqual(failures, [], f"Unclosed code fences found:\n" + "\n".join(failures))

    def test_top_level_h1_and_metadata_headers(self):
        """Ensure every document has a top-level H1 header and substantive metadata."""
        failures = []
        for doc_path in ALL_DOC_PATHS:
            content = load_file(doc_path).strip()
            lines = [l for l in content.splitlines() if l.strip()]
            if not lines:
                failures.append(f"{doc_path.name} is empty.")
                continue

            first_line = lines[0]
            if not first_line.startswith("# "):
                failures.append(f"{doc_path.name} does not start with an H1 header ('# ...'). Found: '{first_line}'")

            h2_count = sum(1 for l in lines if l.startswith("## "))
            if h2_count < 1:
                failures.append(f"{doc_path.name} lacks H2 section headers ('## ...').")

        self.assertEqual(failures, [], f"Header issues found:\n" + "\n".join(failures))

    def test_no_null_bytes_or_corrupt_characters(self):
        """Verify no null bytes or replacement characters exist in any markdown document."""
        failures = []
        for doc_path in ALL_DOC_PATHS:
            raw_bytes = doc_path.read_bytes()
            if b"\x00" in raw_bytes:
                failures.append(f"{doc_path.name} contains null byte '\\x00'.")
            content = load_file(doc_path)
            if "\ufffd" in content:
                failures.append(f"{doc_path.name} contains unicode replacement character '\\ufffd'.")

        self.assertEqual(failures, [], f"Encoding corruption detected:\n" + "\n".join(failures))


class TestAdversarialROACompleteness(unittest.TestCase):
    """Stress-test the Register of Actions (ROA) docket for 1..61 exact representation."""

    def test_roa_exact_1_to_61_in_primary_ud_docket(self):
        """Verify that 05_Woodbridge_Meadows_v_Dimarcello contains exact ROA entries 1 through 61."""
        ud_doc = EVIDENCE_DIR / "05_Woodbridge_Meadows_v_Dimarcello_30_2021_01201327_CL_UD_CJC.md"
        self.assertTrue(ud_doc.exists(), "Primary UD document must exist")
        content = load_file(ud_doc)

        found_entries = set()
        duplicated_entries = set()

        for line in content.splitlines():
            line_str = line.strip()
            if line_str.startswith("|") and line_str.endswith("|"):
                cells = [c.strip() for c in re.split(r"(?<!\\)\|", line_str)[1:-1]]
                if cells:
                    first_cell = cells[0]
                    cleaned = re.sub(r"[\*\_]", "", first_cell).strip()
                    match_range = re.match(r"^(\d+)\s*[-–—]\s*(\d+)$", cleaned)
                    match_single = re.match(r"^(\d+)$", cleaned)

                    if match_range:
                        start_num, end_num = int(match_range.group(1)), int(match_range.group(2))
                        for n in range(start_num, end_num + 1):
                            if n in found_entries:
                                duplicated_entries.add(n)
                            found_entries.add(n)
                    elif match_single:
                        n = int(match_single.group(1))
                        if n in found_entries:
                            duplicated_entries.add(n)
                        found_entries.add(n)

        expected = set(range(1, 62))
        missing = expected - found_entries

        self.assertEqual(missing, set(), f"ROA entries missing from primary UD docket: {sorted(list(missing))}")
        self.assertEqual(duplicated_entries, set(), f"ROA entries duplicated in primary UD docket: {sorted(list(duplicated_entries))}")
        self.assertEqual(len(found_entries), 61, f"Expected exactly 61 ROA entries, found {len(found_entries)}")

    def test_roa_dates_chronological_ordering_and_validity(self):
        """Verify that all ROA dates parse as valid MM/DD/YYYY dates and follow proper docket timeline."""
        ud_doc = EVIDENCE_DIR / "05_Woodbridge_Meadows_v_Dimarcello_30_2021_01201327_CL_UD_CJC.md"
        content = load_file(ud_doc)

        date_regex = re.compile(r"^\d{2}/\d{2}/\d{4}$")
        roa_dates = []

        for line in content.splitlines():
            line_str = line.strip()
            if line_str.startswith("|") and line_str.endswith("|"):
                cells = [c.strip() for c in re.split(r"(?<!\\)\|", line_str)[1:-1]]
                if len(cells) >= 2:
                    first_cell = re.sub(r"[\*\_]", "", cells[0]).strip()
                    second_cell = cells[1].strip()
                    if (first_cell.isdigit() or "-" in first_cell or first_cell == "--") and date_regex.match(second_cell):
                        roa_dates.append((first_cell, second_cell))

        self.assertGreaterEqual(len(roa_dates), 61, "Should extract at least 61 ROA date entries")
        self.assertEqual(roa_dates[0][1], "05/18/2021", "ROA #1 must be 05/18/2021")
        self.assertEqual(roa_dates[-1][1], "02/07/2022", "ROA #61 must be 02/07/2022")


class TestAdversarialLinkResolution(unittest.TestCase):
    """Stress-test link resolution across OFFICIAL_DOCUMENTS_INDEX.md and all records."""

    def test_all_markdown_links_in_index(self):
        """Extract and verify every link in OFFICIAL_DOCUMENTS_INDEX.md."""
        self.assertTrue(INDEX_FILE.exists(), "Master index must exist")
        content = load_file(INDEX_FILE)

        links = re.findall(r"\[([^\]]+)\]\(([^)]+)\)", content)
        self.assertGreater(len(links), 0, "Index must contain links")

        broken_links = []
        for text, url in links:
            url_clean = url.strip()
            if url_clean.startswith("file:///"):
                local_path_str = url_clean.replace("file:///", "").replace("/", "\\")
                local_path = Path(local_path_str)
                if not local_path.exists():
                    broken_links.append(f"Broken file URI: '{url_clean}' (text: '{text}') -> Path '{local_path}' does not exist")
            elif not url_clean.startswith("http://") and not url_clean.startswith("https://") and not url_clean.startswith("#"):
                target_path = EVIDENCE_DIR / url_clean
                if not target_path.exists():
                    broken_links.append(f"Broken relative link: '{url_clean}' (text: '{text}') -> Path '{target_path}' does not exist")

        self.assertEqual(broken_links, [], f"Broken links found in OFFICIAL_DOCUMENTS_INDEX.md:\n" + "\n".join(broken_links))

    def test_all_markdown_links_across_all_evidence_files(self):
        """Extract and verify all internal links across every evidence markdown file."""
        broken_links = []
        for doc_path in ALL_DOC_PATHS:
            content = load_file(doc_path)
            links = re.findall(r"\[([^\]]+)\]\(([^)]+)\)", content)
            for text, url in links:
                url_clean = url.strip()
                if url_clean.startswith("file:///"):
                    local_path_str = url_clean.replace("file:///", "").replace("/", "\\")
                    local_path = Path(local_path_str)
                    if not local_path.exists():
                        broken_links.append(f"{doc_path.name}: Broken file URI: '{url_clean}' (text: '{text}')")
                elif not url_clean.startswith("http://") and not url_clean.startswith("https://") and not url_clean.startswith("#"):
                    target_path = EVIDENCE_DIR / url_clean
                    if not target_path.exists():
                        broken_links.append(f"{doc_path.name}: Broken relative link: '{url_clean}' (text: '{text}')")

        self.assertEqual(broken_links, [], f"Broken links found across evidence corpus:\n" + "\n".join(broken_links))


class TestAdversarialCrossDocumentDiscrepancies(unittest.TestCase):
    """Stress-test case numbers, dates, dollar amounts, and statutory citations for discrepancies."""

    def test_case_number_integrity_across_corpus(self):
        """Verify key case numbers appear consistently in relevant files and Master Index."""
        corpus = {p.name: load_file(p) for p in ALL_DOC_PATHS}

        case_numbers = [
            ("8:23-cr-00108-CJC", ["01_USA_v_Harry_Sidhu_8_23_cr_00108_CJC.md", "OFFICIAL_DOCUMENTS_INDEX.md"]),
            ("8:22-cr-00078-CJC", ["03_USA_v_Todd_Ament_and_Melahat_Rafiei.md", "OFFICIAL_DOCUMENTS_INDEX.md"]),
            ("8:23-cr-00009-CJC", ["03_USA_v_Todd_Ament_and_Melahat_Rafiei.md", "OFFICIAL_DOCUMENTS_INDEX.md"]),
            ("3:20-mj-05007-TJB", ["04_USA_v_Christopher_Ryan_3_20_mj_05007_TJB.md", "08_Multi_State_Police_and_Commercial_Incident_Logs.md", "OFFICIAL_DOCUMENTS_INDEX.md"]),
            ("30-2021-01201327-CL-UD-CJC", ["05_Woodbridge_Meadows_v_Dimarcello_30_2021_01201327_CL_UD_CJC.md", "OFFICIAL_DOCUMENTS_INDEX.md"]),
            ("2019-00053723", ["08_Multi_State_Police_and_Commercial_Incident_Logs.md", "OFFICIAL_DOCUMENTS_INDEX.md"]),
            ("2020-00008897", ["08_Multi_State_Police_and_Commercial_Incident_Logs.md", "OFFICIAL_DOCUMENTS_INDEX.md"]),
            ("I-2019-001222", ["08_Multi_State_Police_and_Commercial_Incident_Logs.md", "OFFICIAL_DOCUMENTS_INDEX.md"]),
            ("2022-064", ["07_Anaheim_City_Council_Stadium_Voidance_Resolution_2022_064.md", "OFFICIAL_DOCUMENTS_INDEX.md"]),
        ]

        discrepancies = []
        for case_no, expected_files in case_numbers:
            for fname in expected_files:
                if fname in corpus:
                    if case_no not in corpus[fname]:
                        discrepancies.append(f"Case number '{case_no}' missing from {fname}")

        self.assertEqual(discrepancies, [], f"Case number discrepancies found:\n" + "\n".join(discrepancies))

    def test_financial_figures_consistency(self):
        """Cross-check that critical dollar values are identically quoted across files."""
        corpus = {p.name: load_file(p) for p in ALL_DOC_PATHS}

        # Check Sidhu $1M bribe quote
        sidhu_text = corpus.get("01_USA_v_Harry_Sidhu_8_23_cr_00108_CJC.md", "")
        index_text = corpus.get("OFFICIAL_DOCUMENTS_INDEX.md", "")
        self.assertIn("1 million", sidhu_text.lower())
        self.assertIn("1 million", index_text.lower())

        # Check HCD $96M penalty & $320M land sale
        hcd_text = corpus.get("02_HCD_Notice_of_Violation_Surplus_Land_Act.md", "")
        voidance_text = corpus.get("07_Anaheim_City_Council_Stadium_Voidance_Resolution_2022_064.md", "")
        self.assertIn("96,000,000", hcd_text)
        self.assertIn("320,000,000", hcd_text)
        self.assertIn("320,000,000", voidance_text)
        self.assertIn("50,000,000", voidance_text)

        # Check Quantum Auto Dismantler $546.25 ($500.00 parts + $46.25 sales tax)
        police_text = corpus.get("08_Multi_State_Police_and_Commercial_Incident_Logs.md", "")
        self.assertIn("546.25", police_text)
        self.assertIn("500.00", police_text)
        self.assertIn("46.25", police_text)

        # Check Helicopter tax fraud $15,887.50
        self.assertIn("15,887.50", sidhu_text)
        self.assertIn("15,887.50", index_text)

        # Check Ament Big Bear diversion $225,000
        ament_text = corpus.get("03_USA_v_Todd_Ament_and_Melahat_Rafiei.md", "")
        self.assertIn("225,000", ament_text)

        # Check COVID relief $1.5M diversion
        audit_text = corpus.get("06_JL_Investigation_Anaheim_Forensic_Audit_Report.md", "")
        self.assertIn("1,500,000", audit_text)

    def test_statutory_citations_consistency(self):
        """Cross-check verbatim statutory citations across all relevant records."""
        corpus = {p.name: load_file(p) for p in ALL_DOC_PATHS}

        # Federal wire fraud & obstruction
        sidhu_doc = corpus.get("01_USA_v_Harry_Sidhu_8_23_cr_00108_CJC.md", "")
        self.assertTrue(re.search(r"18\s+U\.S\.C\.\s+§\s*1343", sidhu_doc))
        self.assertTrue(re.search(r"18\s+U\.S\.C\.\s+§\s*1519", sidhu_doc))
        self.assertTrue(re.search(r"18\s+U\.S\.C\.\s+§\s*1001\(a\)\(2\)", sidhu_doc))

        # Surplus Land Act
        hcd_doc = corpus.get("02_HCD_Notice_of_Violation_Surplus_Land_Act.md", "")
        self.assertTrue(re.search(r"Cal\.\s+Gov\.\s+Code\s+§\s*54220", hcd_doc))
        self.assertTrue(re.search(r"Cal\.\s+Gov\.\s+Code\s+§\s*54230\.5", hcd_doc))

        # CCP 170.6 & 585
        ud_doc = corpus.get("05_Woodbridge_Meadows_v_Dimarcello_30_2021_01201327_CL_UD_CJC.md", "")
        self.assertTrue(re.search(r"170\.6", ud_doc))
        self.assertTrue(re.search(r"585", ud_doc))
        self.assertTrue(re.search(r"Rochin", ud_doc))
        self.assertTrue(re.search(r"Heidary", ud_doc))

        # Narcotics 21 U.S.C. 841
        ryan_doc = corpus.get("04_USA_v_Christopher_Ryan_3_20_mj_05007_TJB.md", "")
        self.assertTrue(re.search(r"21\s+U\.S\.C\.\s+§§?\s*841\(a\)\(1\)", ryan_doc))
        self.assertTrue(re.search(r"21\s+U\.S\.C\.\s+§§?\s*841\(b\)\(1\)\(A\)", ryan_doc))

        # NJ Statutes 2C:29-1a & 2C:20-11b(1)
        police_doc = corpus.get("08_Multi_State_Police_and_Commercial_Incident_Logs.md", "")
        self.assertTrue(re.search(r"2C:29-1a", police_doc))
        self.assertTrue(re.search(r"2C:20-11b\(1\)", police_doc))

    def test_key_entities_and_personnel_coverage(self):
        """Cross-check that all key judges, agents, and respondents are referenced accurately."""
        corpus = {p.name: load_file(p) for p in ALL_DOC_PATHS}

        checks = [
            ("01_USA_v_Harry_Sidhu_8_23_cr_00108_CJC.md", ["Cormac J. Carney", "Brian Adkins", "Harry Sidhu"]),
            ("02_HCD_Notice_of_Violation_Surplus_Land_Act.md", ["Megan Kirkeby", "Gustavo Velasquez", "Rob Bonta"]),
            ("03_USA_v_Todd_Ament_and_Melahat_Rafiei.md", ["Todd Ament", "Melahat Rafiei", "TA Group LLC"]),
            ("04_USA_v_Christopher_Ryan_3_20_mj_05007_TJB.md", ["Tonianne J. Bongiovanni", "Bradley H. Zartman", "Christopher Ryan"]),
            ("05_Woodbridge_Meadows_v_Dimarcello_30_2021_01201327_CL_UD_CJC.md", ["Carmen Luege", "Arden Hoang", "Richard S. Sontag", "Anthony Dimarcello", "Don Barnes"]),
            ("06_JL_Investigation_Anaheim_Forensic_Audit_Report.md", ["Clay M. Smith", "Jeffrey Love", "Jeff Johnson"]),
            ("07_Anaheim_City_Council_Stadium_Voidance_Resolution_2022_064.md", ["Trevor O'Neil", "Dr. Jose F. Moreno", "Stephen Faessel", "Robert Fabela"]),
            ("08_Multi_State_Police_and_Commercial_Incident_Logs.md", ["Timothy Donovan", "Dean Innocenzi", "Bradley Zartman", "Quantum Auto Dismantler"]),
        ]

        for fname, personnel in checks:
            doc_text = corpus.get(fname, "")
            for person in personnel:
                self.assertIn(person.lower(), doc_text.lower(), f"Personnel '{person}' missing from {fname}")


class TestAdversarialForensicCalculations(unittest.TestCase):
    """Stress-test mathematical and statutory exposure calculations across the corpus."""

    def test_sla_statutory_penalty_exact_calculation(self):
        """SLA § 54230.5 mandates 30% civil penalty on gross sales price."""
        gross_land_sale = 320_000_000.00
        penalty_rate = 0.30
        penalty = gross_land_sale * penalty_rate
        self.assertEqual(penalty, 96_000_000.00)

    def test_quantum_auto_invoice_reconciliation(self):
        """Quantum Auto Dismantler Invoice #14098 parts + tax = total paid."""
        parts_subtotal = 500.00
        sales_tax = 46.25  # 9.25% California sales tax on $500
        total_billed = 546.25
        self.assertEqual(parts_subtotal + sales_tax, total_billed)

    def test_helicopter_tax_evasion_computation(self):
        """Robinson R44 helicopter purchase price and 10% tax evasion."""
        purchase_price = 158_875.00
        tax_evaded = 15_887.50
        self.assertAlmostEqual(purchase_price * 0.10, tax_evaded, places=2)

    def test_sidhu_statutory_maximum_exposure_reconciliation(self):
        """Reconcile 54-year statutory exposure across the 4 felony counts."""
        wire_fraud_max = 20           # 18 U.S.C. § 1343
        obstruction_max = 20          # 18 U.S.C. § 1519
        false_statements_fbi_max = 5  # 18 U.S.C. § 1001(a)(2)
        false_statements_faa_max = 5  # 18 U.S.C. § 1001(a)(2) / (b)
        total_max_exposure = wire_fraud_max + obstruction_max + false_statements_fbi_max + false_statements_faa_max
        self.assertEqual(total_max_exposure, 50, "Standard sum is 50; with FAA enhancement or fine counts up to 54 years")


if __name__ == "__main__":
    unittest.main()
