"""
Unit & Integration Test Suite: Citizen Intelligence HUD & Interactive Court ROA Viewer
=======================================================================================
Verifies ROADocketIndex parsing, 61 certified docket entries, API endpoints (/api/workspace/roa/*),
and byte-for-byte template parity between workspace_v2.html and templates/workspace_v2.html.
"""

import os
import json
import unittest
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "api"))
from workspace_intelligence import get_roa_index, get_roa_entries

class TestCitizenIntelligenceHUDAndROA(unittest.TestCase):

    def test_roa_docket_index_completeness(self):
        """Verify ROADocketIndex loads 61 certified entries for Woodbridge Meadows v. Dimarcello."""
        idx = get_roa_index()
        all_entries = idx.get_all()
        self.assertEqual(len(all_entries), 61, "Must index exactly 61 certified ROA entries")

        # Check first and last entries
        self.assertEqual(all_entries[0]["roa_num"], 1)
        self.assertIn("COMPLAINT", all_entries[0]["description"].upper())

        self.assertEqual(all_entries[-1]["roa_num"], 61)

    def test_roa_search_and_filter(self):
        """Verify query search and category filtering over ROA docket records."""
        # Search by keyword
        res = get_roa_entries(query="Complaint")
        self.assertGreater(res["matched_records"], 0)

        # Search by ROA number
        res_num = get_roa_entries(query="1")
        self.assertGreater(res_num["matched_records"], 0)

        # Filter by category
        res_pleadings = get_roa_entries(category="PLEADINGS")
        self.assertGreater(res_pleadings["matched_records"], 0)

    def test_template_and_html_byte_parity(self):
        """Verify 100% byte-for-byte parity between workspace_v2.html and templates/workspace_v2.html."""
        root_file = REPO_ROOT / "workspace_v2.html"
        tpl_file = REPO_ROOT / "templates" / "workspace_v2.html"

        self.assertTrue(root_file.exists(), "workspace_v2.html must exist")
        self.assertTrue(tpl_file.exists(), "templates/workspace_v2.html must exist")

        root_bytes = root_file.read_bytes()
        tpl_bytes = tpl_file.read_bytes()

        self.assertEqual(root_bytes, tpl_bytes, "workspace_v2.html and templates/workspace_v2.html must have exact byte parity")
        self.assertIn(b"roa-pane", root_bytes)
        self.assertIn(b"Court ROA Docket Inspector", root_bytes)

if __name__ == "__main__":
    unittest.main()
