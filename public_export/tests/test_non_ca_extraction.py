"""
test_non_ca_extraction.py
=========================
Comprehensive Test Suite for Milestone M2: Non-California Entity Extraction & Data Isolation
Author: Worker M2 (Non-California Entity Extraction & Data Isolation Specialist)
Verification Authority: Teamwork Preview Auditor / Forensic Integrity Standards

Tests:
1. Deliverable existence and JSON validity
2. 100% Non-California purity (Zero California entities)
3. Valid US state/territory postal codes
4. Interface contract compliance (schema fields and types)
5. Canonical ID formatting (NONCA-ENT-XXXX)
6. Valid entity type classifications
7. Core target entity presence across primary hubs (NJ, NV, PA, AZ, TX, FL, MI, MA, DC, CT, NY, GA, DE, MS, TN, NC)
8. Multi-state coverage (>30 states)
9. Uniqueness and deduplication (zero ID collisions)
10. End-to-end execution of scripts/extract_non_ca_records.py
"""

import os
import re
import json
import unittest

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DELIVERABLE_PATH = os.path.join(REPO_ROOT, "data", "non_ca_raw_entities.json")
SCRIPT_PATH = os.path.join(REPO_ROOT, "scripts", "extract_non_ca_records.py")

VALID_NON_CA_STATES = {
    "AL", "AK", "AZ", "AR", "CO", "CT", "DE", "FL", "GA", "HI", "ID", "IL",
    "IN", "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO",
    "MT", "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "OH", "OK", "OR",
    "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI",
    "WY", "DC", "PR", "VI", "GU"
}

ALLOWED_ENTITY_TYPES = {
    "CORPORATION", "CONTRACTOR", "INDIVIDUAL", "PROPERTY",
    "JUDICIAL_DOCKET", "POLICE_RECORD", "TRANSACTION"
}


class TestNonCAEntityExtraction(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        if not os.path.exists(DELIVERABLE_PATH):
            import sys
            sys.path.insert(0, os.path.join(REPO_ROOT, "scripts"))
            from extract_non_ca_records import NonCAEntityExtractor
            extractor = NonCAEntityExtractor(repo_root=REPO_ROOT)
            extractor.execute()
            extractor.save_deliverable("data/non_ca_raw_entities.json")

        with open(DELIVERABLE_PATH, "r", encoding="utf-8") as f:
            cls.deliverable_data = json.load(f)

    def test_01_deliverable_structure(self):
        """Test top-level metadata and entities array structure."""
        self.assertIn("metadata", self.deliverable_data, "Missing 'metadata' root key")
        self.assertIn("entities", self.deliverable_data, "Missing 'entities' root key")
        entities = self.deliverable_data["entities"]
        self.assertIsInstance(entities, list)
        self.assertGreaterEqual(len(entities), 100, f"Expected >= 100 entities, got {len(entities)}")

        metadata = self.deliverable_data["metadata"]
        self.assertEqual(metadata["total_entities"], len(entities))
        self.assertTrue(metadata["non_ca_purity_verified"])
        self.assertIn("sha256_checksum", metadata)
        self.assertEqual(len(metadata["sha256_checksum"]), 64)

    def test_02_strict_non_california_purity(self):
        """CRITICAL: Test that 100% of extracted entities are strictly OUTSIDE California (State != 'CA')."""
        entities = self.deliverable_data["entities"]
        ca_violations = []
        for ent in entities:
            if ent.get("state") == "CA":
                ca_violations.append(ent)

        self.assertEqual(len(ca_violations), 0, f"Found {len(ca_violations)} California violations: {ca_violations}")

    def test_03_valid_jurisdictions(self):
        """Test that all entities map to valid US non-CA state/territory codes."""
        entities = self.deliverable_data["entities"]
        for ent in entities:
            state = ent.get("state")
            self.assertIn(state, VALID_NON_CA_STATES, f"Invalid state code '{state}' in entity: {ent.get('name')}")
            self.assertTrue(ent.get("jurisdiction"), f"Missing jurisdiction in entity: {ent.get('name')}")

    def test_04_interface_contract_schema(self):
        """Test that every entity complies with the plan.md interface contract schema."""
        required_keys = {
            "entity_id", "name", "state", "jurisdiction",
            "source_dataset", "entity_type", "nexus_details",
            "raw_attributes", "first_discovered"
        }
        entities = self.deliverable_data["entities"]
        for ent in entities:
            missing = required_keys - set(ent.keys())
            self.assertFalse(missing, f"Entity {ent.get('entity_id')} missing required keys: {missing}")
            self.assertIsInstance(ent["nexus_details"], dict, f"nexus_details must be dict in {ent.get('entity_id')}")
            self.assertIsInstance(ent["raw_attributes"], dict, f"raw_attributes must be dict in {ent.get('entity_id')}")

    def test_05_canonical_entity_id_format(self):
        """Test that entity IDs follow the canonical sequential format NONCA-ENT-XXXX."""
        entities = self.deliverable_data["entities"]
        id_pattern = re.compile(r"^NONCA-ENT-\d{4,}$")
        seen_ids = set()
        for ent in entities:
            ent_id = ent.get("entity_id")
            self.assertTrue(id_pattern.match(ent_id), f"Invalid entity_id format: {ent_id}")
            self.assertNotIn(ent_id, seen_ids, f"Duplicate entity_id detected: {ent_id}")
            seen_ids.add(ent_id)

    def test_06_valid_entity_types(self):
        """Test that all entity types conform to the allowed enumerations."""
        entities = self.deliverable_data["entities"]
        for ent in entities:
            ent_type = ent.get("entity_type")
            self.assertIn(ent_type, ALLOWED_ENTITY_TYPES, f"Invalid entity_type '{ent_type}' in {ent.get('name')}")

    def test_07_core_target_entities_present(self):
        """Verify presence of core mandatory entities from DISPATCH.md and Explorer surveys."""
        entities = self.deliverable_data["entities"]
        entity_names = {ent["name"].upper(): ent for ent in entities}

        # 1. Nevada Shell
        self.assertTrue(any("BROWN HUBERT" in k for k in entity_names), "Missing BROWN HUBERT LLC")

        # 2. Florida Front
        self.assertTrue(any("DOG'S DAY PRODUCTIONS" in k for k in entity_names), "Missing Dog's Day Productions")

        # 3. New Jersey Criminal & Police
        self.assertTrue(any("CHRISTOPHER RYAN" in k for k in entity_names), "Missing USA v. Christopher Ryan docket")
        self.assertTrue(any("DEAN ANTHONY INNOCENZI" in k for k in entity_names), "Missing Dean Anthony Innocenzi")
        self.assertTrue(any("ZARTMAN" in k for k in entity_names), "Missing SA Bradley Zartman")
        self.assertTrue(any("2019-00053723" in k for k in entity_names), "Missing Hamilton PD Incident 2019-00053723")
        self.assertTrue(any("I-2019-001222" in k for k in entity_names), "Missing Ewing PD Ledger Case I-2019-001222")
        self.assertTrue(any("QUANTUM AUTO" in k for k in entity_names), "Missing Quantum Auto Dismantler shipment")

        # 4. Pennsylvania Split Billing
        self.assertTrue(any("STERLING-RIVERS" in k for k in entity_names), "Missing Sterling-Rivers Nominee LLC")
        self.assertTrue(any("ENDO PHARMACEUTICALS" in k for k in entity_names), "Missing Endo Pharmaceuticals")

        # 5. Arizona Shells & Grants
        self.assertTrue(any("ONNI HUNTINGTON BEACH" in k for k in entity_names), "Missing ONNI HUNTINGTON BEACH LLC")
        self.assertTrue(any("DOLORES RE HOLDINGS" in k for k in entity_names), "Missing DOLORES RE HOLDINGS LLC")
        self.assertTrue(any("220141-RFP" in k for k in entity_names), "Missing Maricopa County Grant #220141-RFP")
        self.assertTrue(any("WILLIE MITCHELL" in k for k in entity_names), "Missing USA v. Willie Mitchell docket")

        # 6. Texas 50-Shell Ring
        self.assertTrue(any("AMIR AQEEL" in k for k in entity_names), "Missing USA v. Amir Aqeel docket")

        # 7. Florida Luxury PPP Ring
        self.assertTrue(any("DAVID T. HINES" in k for k in entity_names), "Missing USA v. David T. Hines docket")

        # 8. Michigan PPP Diversion
        self.assertTrue(any("STEWART INDUSTRIES" in k for k in entity_names), "Missing Stewart Industries LLC")

        # 9. Federal Node in DC
        self.assertTrue(any("TITLE IV-E" in k for k in entity_names), "Missing Title IV-E Federal Billing Node")

        # 10. Connecticut Academic
        self.assertTrue(any("POST UNIVERSITY" in k for k in entity_names), "Missing Post University")

        # 11. New York Trading Firm
        self.assertTrue(any("T3 TRADING GROUP" in k for k in entity_names), "Missing T3 Trading Group, LLC")

    def test_08_geographic_distribution(self):
        """Test that data spans multiple out-of-state jurisdictions (at least 30 states)."""
        entities = self.deliverable_data["entities"]
        distinct_states = set(ent["state"] for ent in entities)
        self.assertGreaterEqual(len(distinct_states), 30, f"Expected >= 30 states, got {len(distinct_states)}: {distinct_states}")
        # Key states must be present
        mandatory_states = {"NV", "NJ", "PA", "AZ", "TX", "FL", "MI", "MA", "DC", "CT", "NY", "GA", "DE"}
        missing_mandatory = mandatory_states - distinct_states
        self.assertFalse(missing_mandatory, f"Missing mandatory states: {missing_mandatory}")

    def test_09_end_to_end_extractor_execution(self):
        """Verify that scripts/extract_non_ca_records.py can be imported and executed programmatically."""
        import sys
        sys.path.insert(0, os.path.join(REPO_ROOT, "scripts"))
        from extract_non_ca_records import NonCAEntityExtractor

        extractor = NonCAEntityExtractor(repo_root=REPO_ROOT)
        extracted = extractor.execute()
        self.assertGreaterEqual(len(extracted), 100)
        self.assertTrue(all(e["state"] != "CA" for e in extracted))


if __name__ == "__main__":
    unittest.main()
