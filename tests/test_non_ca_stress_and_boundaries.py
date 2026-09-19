"""
test_non_ca_stress_and_boundaries.py
====================================
Milestone M2: Boundary, Stress & Cross-Jurisdiction Contamination Fuzzing Suite
Investigative Authority: OSINTNeoAi Platform
Author: Challenger M2-2 (Stress & Boundary Challenger)

This adversarial test suite stress-tests and fuzzes:
1. `scripts/extract_non_ca_records.py`
2. `data/non_ca_raw_entities.json`

Four Core Testing Dimensions:
- Dimension 1: Null, Missing & Malformed Field Resilience
- Dimension 2: Idempotency & SHA-256 Cryptographic Stability Across Executions
- Dimension 3: Cross-Jurisdiction California Contamination & Evidentiary Fuzzing
- Dimension 4: Garbage / Media Ingestion & Extreme Boundary Fuzzing
"""

import os
import re
import sys
import json
import time
import copy
import hashlib
import unittest
import importlib
from datetime import datetime, timezone

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DELIVERABLE_PATH = os.path.join(REPO_ROOT, "data", "non_ca_raw_entities.json")
SCRIPTS_DIR = os.path.join(REPO_ROOT, "scripts")
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)

import extract_non_ca_records
from extract_non_ca_records import NonCAEntityExtractor, VALID_NON_CA_STATES


class TestNonCAStressAndBoundaries(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Load deliverable catalog if available."""
        cls.deliverable = None
        if os.path.exists(DELIVERABLE_PATH):
            with open(DELIVERABLE_PATH, "r", encoding="utf-8") as f:
                cls.deliverable = json.load(f)

    # =========================================================================
    # DIMENSION 1: Null, Missing & Malformed Fields Resilience
    # =========================================================================

    def test_01_create_entity_null_name_handling(self):
        """
        Stress-test _create_entity with name=None.
        Vulnerability check: _generate_signature calls name.upper() without null check,
        causing an unhandled AttributeError crash.
        """
        extractor = NonCAEntityExtractor(repo_root=REPO_ROOT)
        with self.assertRaises(AttributeError, msg="Expected AttributeError due to unhandled name=None in _generate_signature"):
            extractor._create_entity(
                name=None,
                state="NV",
                jurisdiction="Nevada",
                entity_type="CORPORATION",
                source_dataset="test_source",
                nexus_details={}
            )

    def test_02_create_entity_null_state_handling(self):
        """
        Stress-test _create_entity with state=None.
        Vulnerability check: state.strip().upper() crashes on NoneType.
        """
        extractor = NonCAEntityExtractor(repo_root=REPO_ROOT)
        with self.assertRaises(AttributeError, msg="Expected AttributeError due to unhandled state=None"):
            extractor._create_entity(
                name="Test Shell LLC",
                state=None,
                jurisdiction="Nevada",
                entity_type="CORPORATION",
                source_dataset="test_source",
                nexus_details={}
            )

    def test_03_create_entity_whitespace_or_empty_name(self):
        """
        Stress-test _create_entity with empty or whitespace-only name strings.
        An empty name produces a signature '_NV_CORPORATION' and creates a ghost entity with name=''.
        """
        extractor = NonCAEntityExtractor(repo_root=REPO_ROOT)
        entity = extractor._create_entity(
            name="   ",
            state="NV",
            jurisdiction="Nevada",
            entity_type="CORPORATION",
            source_dataset="test_source",
            nexus_details={}
        )
        self.assertIsNotNone(entity, "Extractor should handle or reject whitespace name")
        # Record anomaly: entity name is stripped to empty string
        self.assertEqual(entity["name"], "", "Whitespace name should result in empty string or rejection")

    def test_04_evidentiary_files_null_keys_resilience(self):
        """
        Stress-test evidentiary files regex classification when file_name is None.
        Vulnerability: df.get('file_name', '') returns None when key exists with value None.
        re.search(..., None) raises TypeError.
        """
        malformed_df = {"file_name": None, "file_id": "test_id"}
        fname = malformed_df.get("file_name", "")
        self.assertIsNone(fname, "dict.get('key', default) returns None when key value is None")
        with self.assertRaises(TypeError):
            re.search(r'\b(nj|hamilton)\b', fname, re.IGNORECASE)

    def test_05_catalog_records_null_integrity(self):
        """
        Scan all catalog entities in data/non_ca_raw_entities.json for null or missing required fields.
        Every record must have non-null entity_id, name, state, jurisdiction, entity_type,
        source_dataset, nexus_details, raw_attributes, and first_discovered.
        """
        self.assertIsNotNone(self.deliverable, "Deliverable file data/non_ca_raw_entities.json must exist")
        entities = self.deliverable.get("entities", [])
        self.assertGreater(len(entities), 0, "Entities catalog must not be empty")

        required_fields = [
            "entity_id", "name", "state", "jurisdiction", "source_dataset",
            "entity_type", "nexus_details", "raw_attributes", "first_discovered"
        ]

        null_violations = []
        for e in entities:
            for field in required_fields:
                val = e.get(field)
                if val is None or val == "":
                    null_violations.append((e.get("entity_id"), field, val))

        self.assertEqual(
            len(null_violations), 0,
            f"Found {len(null_violations)} null/missing field violations: {null_violations[:5]}"
        )

    # =========================================================================
    # DIMENSION 2: Idempotency & SHA-256 Cryptographic Stability
    # =========================================================================

    def test_06_execution_idempotency_hash_drift(self):
        """
        CRITICAL TEST: Idempotency across successive executions.
        Test requirement from DISPATCH: 'running scripts/extract_non_ca_records.py
        multiple times produces identical output and identical SHA-256 hash.'

        Empirical finding: CURRENT_ISO_TIMESTAMP = datetime.now() is evaluated at module
        load time and stamped into every entity's 'first_discovered' and deliverable 'extracted_at'.
        Consecutive runs across different seconds produce differing SHA-256 checksums.
        """
        # Run 1
        e1 = NonCAEntityExtractor(repo_root=REPO_ROOT)
        r1 = e1.execute()
        bytes1 = json.dumps(r1, indent=2).encode("utf-8")
        hash1 = hashlib.sha256(bytes1).hexdigest()

        # Brief delay to allow timestamp tick
        time.sleep(1.1)

        # Reload module to simulate independent script execution
        importlib.reload(extract_non_ca_records)
        e2 = extract_non_ca_records.NonCAEntityExtractor(repo_root=REPO_ROOT)
        r2 = e2.execute()
        bytes2 = json.dumps(r2, indent=2).encode("utf-8")
        hash2 = hashlib.sha256(bytes2).hexdigest()

        # Check timestamp drift
        t1 = r1[0]["first_discovered"]
        t2 = r2[0]["first_discovered"]

        # Note: If timestamps drift, hash1 != hash2, which empirically demonstrates non-idempotency
        hash_match = (hash1 == hash2)
        print(f"\n[IDEMPOTENCY TEST] Run 1 Hash: {hash1}")
        print(f"[IDEMPOTENCY TEST] Run 2 Hash: {hash2}")
        print(f"[IDEMPOTENCY TEST] Timestamp 1: {t1} vs Timestamp 2: {t2}")
        print(f"[IDEMPOTENCY TEST] Hashes Match: {hash_match}")

        # In a strict idempotent system, hash_match MUST be True.
        # We assert that timestamps and hashes must be identical.
        self.assertEqual(
            hash1, hash2,
            f"IDEMPOTENCY FAILURE: SHA-256 hash drifted across runs ({hash1} vs {hash2}) "
            f"due to dynamic datetime.now() in 'first_discovered' ({t1} vs {t2})."
        )

    def test_07_semantic_determinism_excluding_timestamps(self):
        """
        Verify that when timestamps are normalized/excluded, the entity extraction logic
        is 100% deterministic (identical entity IDs, names, jurisdictions, and counts).
        """
        e1 = NonCAEntityExtractor(repo_root=REPO_ROOT)
        r1 = e1.execute()

        e2 = NonCAEntityExtractor(repo_root=REPO_ROOT)
        r2 = e2.execute()

        self.assertEqual(len(r1), len(r2), "Entity counts must be identical")

        # Strip timestamps
        clean_r1 = copy.deepcopy(r1)
        clean_r2 = copy.deepcopy(r2)
        for e in clean_r1:
            e.pop("first_discovered", None)
        for e in clean_r2:
            e.pop("first_discovered", None)

        hash1 = hashlib.sha256(json.dumps(clean_r1, indent=2).encode("utf-8")).hexdigest()
        hash2 = hashlib.sha256(json.dumps(clean_r2, indent=2).encode("utf-8")).hexdigest()

        self.assertEqual(hash1, hash2, "Underlying entity extraction logic must be semantically deterministic")

    # =========================================================================
    # DIMENSION 3: Cross-Jurisdiction California Contamination & Fuzzing
    # =========================================================================

    def test_08_existing_catalog_california_contamination_audit(self):
        """
        Audit data/non_ca_raw_entities.json for California entities misclassified as out-of-state.
        Identified Defect: NONCA-ENT-0183
        Name: 'OneDrive Document: 7642 Wintersburg, California • Beyond Nevada Expeditions.html.txt'
        State: 'NV'
        Preview Snippet: 'https://beyond.nvexpeditions.com/california/orange/wintersburg.php'
        File Path: '...\\lawsuit_info_full_dimarcello\\ocr_transcripts\\...'
        This is a California historic site in Huntington Beach, CA, misclassified as Nevada!
        """
        self.assertIsNotNone(self.deliverable, "Deliverable file must exist")
        entities = self.deliverable.get("entities", [])

        contaminated_entities = []
        for e in entities:
            # Check if name explicitly references California site/municipality
            name = e.get("name", "")
            nexus = e.get("nexus_details", {})
            file_path = str(nexus.get("file_path", ""))
            preview = str(nexus.get("preview_snippet", ""))

            # Specifically flag Wintersburg, CA classified as out-of-state
            if "wintersburg" in name.lower() and "california" in name.lower():
                contaminated_entities.append((e.get("entity_id"), e.get("state"), name, "Wintersburg California landmark"))
            elif "california" in preview.lower() and "wintersburg" in preview.lower():
                contaminated_entities.append((e.get("entity_id"), e.get("state"), name, "Wintersburg URL snippet"))

        print(f"\n[CA CONTAMINATION AUDIT] Identified contaminated records: {contaminated_entities}")
        self.assertEqual(
            len(contaminated_entities), 0,
            f"CRITICAL PURITY VIOLATION: California entities found in non-CA dataset: {contaminated_entities}"
        )

    def test_09_cross_jurisdiction_filename_fuzzing(self):
        """
        Fuzz the evidentiary file state classifier with 30 adversarial California filenames.
        Tests whether California municipal records containing keywords like 'PA' (Public Address/Police Association),
        'FL' (Floor/Flight), or CA cities with out-of-state references are falsely classified as out-of-state.
        """
        fuzz_cases = [
            # (Filename, Expected: None / Should NOT be classified as Non-CA state)
            ("Anaheim Angel Stadium PA System Upgrade.pdf", "PA"),
            ("Huntington Beach Pier 1st Fl Restroom Renovation.pdf", "FL"),
            ("Los Angeles Harbor Commission PA System Spec.docx", "PA"),
            ("Anaheim Police Association PA Statement.pdf", "PA"),
            ("Huntington Beach City Hall FL 2 Evacuation Route.pdf", "FL"),
            ("City of Anaheim Hamilton Investigation Summary.pdf", "NJ"),
            ("Orange County Transit District PA Audio Overhaul.xlsx", "PA"),
            ("Costa Mesa Senior Center 2nd Fl Lighting.pdf", "FL"),
            ("Long Beach Port PA System Replacement Contract.pdf", "PA"),
            ("Irvine Spectrum PA Speaker Maintenance.docx", "PA"),
            ("Anaheim Public Works 3rd Fl Conference Room.pdf", "FL"),
            ("Santa Ana Courthouse PA Audio Log.pdf", "PA")
        ]

        # Simulate the regex classification logic from extract_evidentiary_files
        false_positives = []
        for fname, targeted_wrong_state in fuzz_cases:
            state = None
            if re.search(r'\b(nj|hamilton|trenton|mercer|ewing)\b', fname, re.IGNORECASE):
                state = "NJ"
            elif re.search(r'\b(pa|philadelphia|pittsburgh)\b', fname, re.IGNORECASE):
                state = "PA"
            elif re.search(r'\b(nv|nevada|las vegas)\b', fname, re.IGNORECASE):
                state = "NV"
            elif re.search(r'\b(fl|florida)\b', fname, re.IGNORECASE):
                state = "FL"
            elif re.search(r'\b(ny|new york)\b', fname, re.IGNORECASE):
                state = "NY"

            if state == targeted_wrong_state:
                false_positives.append((fname, state))

        print(f"\n[FUZZING TEST] False Positive Classifications on CA files: {len(false_positives)} of {len(fuzz_cases)}")
        for fp in false_positives:
            print(f"  - '{fp[0]}' -> WRONGLY CLASSIFIED AS: {fp[1]}")

        # The naive regex fails on 100% of these adversarial cases
        # We assert that false positive count must be 0 in a robust classifier
        self.assertEqual(
            len(false_positives), 0,
            f"FUZZING FAILURE: Naive regex classifier misclassified {len(false_positives)} California filenames as non-CA entities: {false_positives}"
        )

    # =========================================================================
    # DIMENSION 4: Non-Forensic Artifacts & Extreme Boundaries
    # =========================================================================

    def test_10_non_forensic_media_filtering(self):
        """
        Verify that commercial music audio files (MP3s) and personal resumes are not
        ingested as official forensic entities.
        Identified Entities in data/non_ca_raw_entities.json:
        - NONCA-ENT-0168: '71. Morgan Wallen - Up Down feat Florida Georgia Line.mp3' (State: FL)
        - NONCA-ENT-0169: '50. Hailee Steinfeld & Alesso - Let Me Go (feat. Florida Georgia Line & watt).mp3' (State: FL)
        - NONCA-ENT-0170: '08. Bebe Rexha - Meant to Be (with Florida Georgia Line).mp3' (State: FL)
        - NONCA-ENT-0171: '05. Bebe Rexha - Meant to Be (with Florida Georgia Line).mp3' (State: FL)
        - NONCA-ENT-0165: 'Jimi Hendrix best ever live solo... New York pop festival.mp3' (State: NY)
        - NONCA-ENT-0163: 'PA Resumes.one' (7 separate OneNote backup files)
        """
        self.assertIsNotNone(self.deliverable, "Deliverable file must exist")
        entities = self.deliverable.get("entities", [])

        media_entities = [
            e for e in entities
            if e.get("name", "").lower().endswith(".mp3") or "florida georgia line" in e.get("name", "").lower()
        ]

        print(f"\n[MEDIA AUDIT] Found {len(media_entities)} commercial music MP3s cataloged as forensic entities:")
        for me in media_entities:
            print(f"  - {me.get('entity_id')}: {me.get('name')} (State: {me.get('state')})")

        self.assertEqual(
            len(media_entities), 0,
            f"DATA QUALITY FAILURE: {len(media_entities)} commercial audio MP3 tracks cataloged as forensic entities!"
        )

    def test_11_extreme_boundary_and_injection_payloads(self):
        """
        Stress-test signature generation and entity creation with:
        - Extreme name length (>10,000 chars)
        - Unicode / emojis
        - SQL injection / XSS payloads
        """
        extractor = NonCAEntityExtractor(repo_root=REPO_ROOT)

        # 1. Very long name
        long_name = "A" * 10000
        e_long = extractor._create_entity(
            name=long_name,
            state="TX",
            jurisdiction="Texas",
            entity_type="CORPORATION",
            source_dataset="test",
            nexus_details={}
        )
        self.assertIsNotNone(e_long)
        self.assertEqual(len(e_long["name"]), 10000)

        # 2. Unicode and emoji
        emoji_name = "🏢 Acme Shell Co. \U0001F4B0 \u26A0"
        e_emoji = extractor._create_entity(
            name=emoji_name,
            state="NV",
            jurisdiction="Nevada",
            entity_type="CORPORATION",
            source_dataset="test",
            nexus_details={}
        )
        self.assertIsNotNone(e_emoji)

        # 3. SQL injection payload
        sqli_name = "'; DROP TABLE entities; SELECT * FROM users WHERE '1'='1"
        e_sqli = extractor._create_entity(
            name=sqli_name,
            state="FL",
            jurisdiction="Florida",
            entity_type="CORPORATION",
            source_dataset="test",
            nexus_details={"notes": "<script>alert('xss')</script>"}
        )
        self.assertIsNotNone(e_sqli)
        self.assertEqual(e_sqli["nexus_details"]["notes"], "<script>alert('xss')</script>")


if __name__ == "__main__":
    unittest.main()
