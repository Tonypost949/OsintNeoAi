import unittest
import os
import json
import sqlite3

class TestEvidenceLockerAndMatchers(unittest.TestCase):

    def setUp(self):
        self.evidence_manifest = r"C:\OsintNeoAi\evidence\ocr_transcripts_photos\NEURAL_OCR_EVIDENCE_MANIFEST_20260918_141006.json"
        self.matches_json = r"C:\OsintNeoAi\reports\spatial_temporal_photos_matches.json"
        self.bq_report_json = r"C:\OsintNeoAi\reports\bigquery_evidence_crossref_report.json"
        self.opencode_digest = r"C:\OsintNeoAi\data\opencode_shares_digest.json"

    def test_evidence_manifest_exists_and_valid(self):
        self.assertTrue(os.path.exists(self.evidence_manifest), "Evidence manifest file must exist")
        with open(self.evidence_manifest, "r", encoding="utf-8") as f:
            data = json.load(f)
            self.assertEqual(data.get("status"), "COMPLETED")
            self.assertGreaterEqual(len(data.get("matches", [])), 1)

    def test_spatial_temporal_matches_report(self):
        self.assertTrue(os.path.exists(self.matches_json), "Spatial temporal matches report must exist")
        with open(self.matches_json, "r", encoding="utf-8") as f:
            data = json.load(f)
            self.assertEqual(data.get("status"), "COMPLETED")
            self.assertIn("timeline_nodes_ref", data)

    def test_bigquery_crossref_report(self):
        self.assertTrue(os.path.exists(self.bq_report_json), "BigQuery crossref report must exist")
        with open(self.bq_report_json, "r", encoding="utf-8") as f:
            data = json.load(f)
            self.assertEqual(data.get("status"), "COMPLETED")
            self.assertEqual(data.get("target_project"), "noble-beanbag-497411-m4")

    def test_opencode_shares_digest(self):
        self.assertTrue(os.path.exists(self.opencode_digest), "OpenCode shares digest must exist")
        with open(self.opencode_digest, "r", encoding="utf-8") as f:
            data = json.load(f)
            self.assertEqual(data.get("status"), "COMPLETED")
            self.assertEqual(data.get("total_shares_ingested"), 4)

if __name__ == "__main__":
    unittest.main()
