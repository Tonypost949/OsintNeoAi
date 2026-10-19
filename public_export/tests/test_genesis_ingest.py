"""
tests/test_genesis_ingest.py
============================
Comprehensive test suite for OsintNeoAi Genesis Ingestion API,
SHA-256 point-of-upload integrity hashing, Entity vs Bio classification,
Statutory tag injection, Toxic Plume Intercept, and Workspace HUD routes.
"""

import sys
import os
import json
import time
import hashlib
import unittest
from pathlib import Path

os.environ["TESTING"] = "1"

# Base Paths
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
if str(REPO_ROOT / "api") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "api"))

from api.main import app, determine_genesis_type, llm_digest_testimony


class TestGenesisIngestionAPI(unittest.TestCase):
    """Test suite for /api/genesis/ingest and related endpoints."""

    def setUp(self):
        self.app = app
        self.app.config["TESTING"] = True
        self.client = self.app.test_client()

    def test_determine_genesis_type_bio(self):
        """Test BIO classification on self-referential introductory statements."""
        self.assertEqual(determine_genesis_type("My name is John Doe and I was displaced"), "BIO")
        self.assertEqual(determine_genesis_type("I am a tenant at Woodbridge"), "BIO")
        self.assertEqual(determine_genesis_type("I'm reporting an incident"), "BIO")
        self.assertEqual(determine_genesis_type("Me, John Doe, submitting testimony"), "BIO")

    def test_determine_genesis_type_entity(self):
        """Test ENTITY classification on organization or property statements."""
        self.assertEqual(determine_genesis_type("Woodbridge Apartments failed to disclose environmental plume"), "ENTITY")
        self.assertEqual(determine_genesis_type("Anaheim Stadium lease transfer records"), "ENTITY")
        self.assertEqual(determine_genesis_type("Pacific Gas & Electric pipeline corruption"), "ENTITY")

    def test_options_preflight_cors(self):
        """Test CORS OPTIONS pre-flight on /api/genesis/ingest."""
        response = self.client.options("/api/genesis/ingest")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers.get("Access-Control-Allow-Origin"), "*")
        self.assertIn("POST", response.headers.get("Access-Control-Allow-Methods", ""))

    def test_genesis_ingest_empty_text_error(self):
        """Test 400 rejection on empty testimony."""
        response = self.client.post(
            "/api/genesis/ingest",
            data=json.dumps({"text": ""}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn("error", data)

    def test_genesis_ingest_victim_attribution_and_hashing(self):
        """Test SHA-256 integrity hash, VICTIM status, and statutory tag injection."""
        statement = "I was evicted and attacked by Woodbridge Apartments security after reporting fraud."
        wallet = "0xTEST_VICTIM_WALLET_1234"
        response = self.client.post(
            "/api/genesis/ingest",
            data=json.dumps({"text": statement, "wallet": wallet}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)

        # 1. Ledger Verification
        ledger = data.get("ledger", {})
        self.assertEqual(ledger.get("status"), "VICTIM")
        self.assertEqual(ledger.get("chain_of_custody"), "INITIALIZED_APPEND_ONLY")
        self.assertEqual(ledger.get("wallet"), wallet)
        self.assertEqual(ledger.get("genesis_page_type"), "BIO")
        self.assertIn("sha256_hash", ledger)
        self.assertEqual(len(ledger["sha256_hash"]), 64)

        # Verify hash formulation
        expected_hash = hashlib.sha256(f"{statement}:{ledger['timestamp']}:{wallet}".encode()).hexdigest()
        self.assertEqual(ledger["sha256_hash"], expected_hash)

        # 2. Wiki Page & Statutory Compliance Rules
        wiki = data.get("wiki_page", {})
        self.assertIn("compliance_rules", wiki)
        rules = wiki["compliance_rules"]
        self.assertIn("CA_CIVIL_CODE_1946_2", rules)
        self.assertIn("AB_1482", rules)
        self.assertIn("CERCLA_SUPERFUND", rules)
        self.assertIn("MALTEGO_STRIPPED_NODES", rules)

        # 3. Environmental Plume Intercept
        plume = data.get("environmental_plume_intercept", {})
        self.assertEqual(plume.get("status"), "FLAGGED")
        self.assertEqual(plume.get("jurisdiction"), "DTSC_ENVIROSTOR_GEOTRACKER")
        self.assertEqual(plume.get("valuation_discount"), "-85% FMV")
        self.assertIn("473(d)", plume.get("statutory_remedy", ""))

        # 4. Newspaper Draft & Maltego Graph
        news = data.get("newspaper_draft", {})
        self.assertEqual(news.get("publication_status"), "PRIVATE")
        self.assertIn("Woodbridge Apartments", news.get("headline", "") + news.get("body", ""))

        graph = data.get("maltego_graph", {})
        self.assertIn("nodes", graph)
        self.assertIn("edges", graph)

    def test_genesis_ingest_investigator_status(self):
        """Test INVESTIGATOR classification when no harm keywords are present."""
        statement = "Analyzing municipal public records and GIS property ownership chains."
        response = self.client.post(
            "/api/genesis/ingest",
            data=json.dumps({"text": statement}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data.get("ledger", {}).get("status"), "INVESTIGATOR")
        self.assertEqual(data.get("ledger", {}).get("genesis_page_type"), "ENTITY")

    def test_workspace_hud_view_routes(self):
        """Test /workspace and /workspace_v2 serve the workspace HUD."""
        for endpoint in ["/workspace", "/workspace_v2"]:
            res = self.client.get(endpoint)
            self.assertEqual(res.status_code, 200)
            self.assertIn(b"OSINT NEO AI", res.data)

    def test_status_endpoint(self):
        """Test /api/status endpoint."""
        res = self.client.get("/api/status")
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertEqual(data.get("status"), "ok")
        self.assertEqual(data.get("service"), "OsintNeoAi")

    def test_lockbox_deposit_and_verify(self):
        """Test offline encrypted lockbox deposit and cryptographic seal verification."""
        test_payload = "AFFIDAVIT OF PROBABLE CAUSE: EVIDENCE CHAIN 2026"
        dep_res = self.client.post(
            "/api/lockbox/deposit",
            data=json.dumps({"payload": test_payload, "pin": "4377", "classification": "TOP_SECRET"}),
            content_type="application/json"
        )
        self.assertEqual(dep_res.status_code, 200)
        dep_data = json.loads(dep_res.data)
        seal_id = dep_data["seal_id"]
        self.assertTrue(seal_id.startswith("VAULT-"))

        # Verify seal public proof
        ver_res = self.client.get(f"/api/lockbox/verify/{seal_id}")
        self.assertEqual(ver_res.status_code, 200)
        ver_data = json.loads(ver_res.data)
        self.assertEqual(ver_data["seal_id"], seal_id)
        self.assertEqual(ver_data["status"], "SEALED_IMMUTABLE")
        self.assertEqual(ver_data["chain_of_custody"], "FEDERAL_EVIDENCE_GRADE")

    def test_stealth_deposit_and_relay(self):
        """Test dark vault stealth deposit with header & IP stripping."""
        stealth_res = self.client.post(
            "/api/vault/stealth-deposit",
            data=json.dumps({"payload": "STEALTH_LEAD_ENCRYPTED_BLOB"}),
            content_type="application/json"
        )
        self.assertEqual(stealth_res.status_code, 200)
        stealth_data = json.loads(stealth_res.data)
        self.assertEqual(stealth_data["status"], "ok")
        self.assertEqual(stealth_data["ack"], "ROUTED_200")
        self.assertIn("X-Stealth-Routing", stealth_res.headers)


if __name__ == "__main__":
    unittest.main()
