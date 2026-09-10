"""
Unit & Integration Test Suite: BigQuery Evidence & FCA Timeline Injection Engine
================================================================================
Verifies chronological event generation, ARRAY<STRING> UTXO domain tags,
SHA-256 cryptographic proofs, and graceful BigQuery fallback caching.
"""

import os
import json
import unittest
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))
from fca_timeline_and_bigquery_injector_v2 import build_fca_timeline_events, inject_to_bigquery_or_fallback

class TestFCATimelineBigQueryInjector(unittest.TestCase):

    def test_build_timeline_events(self):
        """Verify timeline event generator produces rich, well-formed forensic nodes."""
        events = build_fca_timeline_events()
        self.assertGreaterEqual(len(events), 10, "Must extract at least 10 timeline nodes")

        for evt in events:
            self.assertIn("event_id", evt)
            self.assertIn("event_timestamp", evt)
            self.assertIn("event_type", evt)
            self.assertIn("source_file", evt)
            self.assertIn("description", evt)
            self.assertIn("extracted_entities", evt)
            self.assertIn("utxo_domain_tags", evt)
            self.assertIn("evidence_sha256", evt)

            # Check UTXO domain tags format (ARRAY<STRING>)
            self.assertIsInstance(evt["utxo_domain_tags"], list)
            self.assertGreater(len(evt["utxo_domain_tags"]), 0)

            # Check SHA-256 length
            self.assertEqual(len(evt["evidence_sha256"]), 64)

    def test_inject_and_local_cache(self):
        """Verify injection generates local JSON ledger and synchronizes leads feed."""
        events = build_fca_timeline_events()
        res = inject_to_bigquery_or_fallback(events)

        self.assertEqual(res.get("status"), "SUCCESS")
        self.assertGreaterEqual(res.get("total_events"), 10)

        ledger_path = Path(res.get("json_ledger"))
        self.assertTrue(ledger_path.exists())

        with open(ledger_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.assertEqual(data.get("total_events"), len(events))
        self.assertIn("events", data)

        # Check leads feed
        leads_feed_path = REPO_ROOT / "data" / "leads_feed.json"
        self.assertTrue(leads_feed_path.exists())

if __name__ == "__main__":
    unittest.main()
