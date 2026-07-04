"""
test_pipeline.py — Unit tests for OSINT pipeline.
Run: pytest tests/test_pipeline.py -v
"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from attorney_nodes import (
    extract_attorney_from_agent,
    generate_attorney_id,
    process_attorney_batch,
)
from entity_match import (
    clear_cache,
    get_cache_stats,
    match_entity,
    match_exact,
    normalize_name,
)
from neo4j_export import (
    export_entities,
    export_relationships,
    export_attorneys,
    get_export_stats,
)
from people_handler import (
    build_control_clusters,
    extract_person_from_entity,
    generate_person_id,
    merge_person_records,
)


# ── entity_match tests ─────────────────────────────────────────

class TestNormalizeName:
    def test_removes_llc(self):
        assert normalize_name("ACME LLC") == "ACME"

    def test_removes_inc(self):
        assert normalize_name("ACME INC.") == "ACME"

    def test_removes_punctuation(self):
        assert normalize_name("ACME & SONS, LLC") == "ACME SONS"

    def test_uppercase(self):
        assert normalize_name("acme llc") == "ACME"

    def test_strips_whitespace(self):
        assert normalize_name("  ACME LLC  ") == "ACME"


class TestMatchExact:
    def setup_method(self):
        clear_cache()

    def test_exact_match(self):
        candidates = [
            {"entity_id": "1", "entity_name": "ACME LLC"},
            {"entity_id": "2", "entity_name": "BOB INC"},
        ]
        result = match_exact("ACME LLC", candidates)
        assert result is not None
        assert result["entity_id"] == "1"
        assert result["match_score"] == 100.0

    def test_no_match(self):
        candidates = [{"entity_id": "1", "entity_name": "ACME LLC"}]
        result = match_exact("XYZ CORP", candidates)
        assert result is None


class TestMatchEntity:
    def setup_method(self):
        clear_cache()

    def test_fuzzy_match(self):
        candidates = [
            {"entity_id": "1", "entity_name": "ACME INVESTMENTS LLC"},
            {"entity_id": "2", "entity_name": "BOB CORP"},
        ]
        result = match_entity("ACME INVESTMENTS", candidates, threshold=70)
        assert result is not None
        assert result["entity_id"] == "1"
        assert result["match_score"] > 70

    def test_below_threshold(self):
        candidates = [{"entity_id": "1", "entity_name": "ACME LLC"}]
        result = match_entity("XYZ CORPORATION", candidates, threshold=90)
        assert result is None


class TestCache:
    def test_cache_stats(self):
        clear_cache()
        stats = get_cache_stats()
        assert stats["size"] == 0
        assert stats["ttl_seconds"] == 300

    def test_clear_cache(self):
        clear_cache()
        candidates = [{"entity_id": "1", "entity_name": "ACME LLC"}]
        match_exact("ACME LLC", candidates)
        assert get_cache_stats()["size"] == 1
        clear_cache()
        assert get_cache_stats()["size"] == 0


# ── attorney_nodes tests ───────────────────────────────────────

class TestAttorneyExtraction:
    def test_valid_attorney(self):
        result = extract_attorney_from_agent("JOHN SMITH, Bar #12345")
        assert result is not None
        assert result["name"] == "JOHN SMITH"
        assert result["bar_number"] == "12345"

    def test_corporate_agent(self):
        result = extract_attorney_from_agent("C T CORPORATION SYSTEM")
        assert result is None

    def test_llc_agent(self):
        result = extract_attorney_from_agent("ACME LLC")
        assert result is None

    def test_empty_agent(self):
        assert extract_attorney_from_agent("") is None
        assert extract_attorney_from_agent("NONE") is None

    def test_attorney_id_generation(self):
        id1 = generate_attorney_id("JOHN SMITH", "12345")
        id2 = generate_attorney_id("JOHN SMITH", "12345")
        assert id1 == id2

    def test_different_names_different_ids(self):
        id1 = generate_attorney_id("JOHN SMITH")
        id2 = generate_attorney_id("JANE DOE")
        assert id1 != id2


class TestAttorneyBatch:
    def test_deduplication(self):
        attorneys = [
            {"attorney_id": "a1", "name": "JOHN SMITH", "linked_entities": ["E1"], "entity_count": 1},
            {"attorney_id": "a1", "name": "JOHN SMITH", "linked_entities": ["E2"], "entity_count": 1},
            {"attorney_id": "a2", "name": "JANE DOE", "linked_entities": ["E3"], "entity_count": 1},
        ]
        result = process_attorney_batch(attorneys)
        assert result["total"] == 2


# ── people_handler tests ───────────────────────────────────────

class TestPersonExtraction:
    def test_valid_person(self):
        entity = {
            "entity_id": "E1",
            "registered_agent": "JOHN SMITH",
            "agent_address": "123 Main St, LA, CA",
        }
        result = extract_person_from_entity(entity)
        assert result is not None
        assert result["full_name"] == "JOHN SMITH"
        assert "123 Main St, LA, CA" in result["addresses"]

    def test_corporate_agent(self):
        entity = {
            "entity_id": "E1",
            "registered_agent": "C T CORPORATION SYSTEM",
        }
        result = extract_person_from_entity(entity)
        assert result is None

    def test_person_id_deterministic(self):
        id1 = generate_person_id("JOHN SMITH", ["123 Main St"])
        id2 = generate_person_id("JOHN SMITH", ["123 Main St"])
        assert id1 == id2


class TestPersonMerge:
    def test_merge_same_person(self):
        records = [
            {
                "person_id": "p1",
                "full_name": "JOHN SMITH",
                "linked_entities": ["E1"],
                "addresses": ["123 Main St"],
                "phone_numbers": [],
                "emails": [],
                "total_ppp_amount": 100000,
                "confidence_score": 0.8,
            },
            {
                "person_id": "p1",
                "full_name": "JOHN SMITH",
                "linked_entities": ["E2"],
                "addresses": ["456 Oak Ave"],
                "phone_numbers": ["555-1234"],
                "emails": [],
                "total_ppp_amount": 200000,
                "confidence_score": 0.9,
            },
        ]
        result = merge_person_records(records)
        assert result["total"] == 1
        person = result["people"][0]
        assert len(person["linked_entities"]) == 2
        assert len(person["addresses"]) == 2
        assert person["total_ppp_amount"] == 300000
        assert person["confidence_score"] == 0.9


class TestControlClusters:
    def test_cluster_detection(self):
        people = [
            {"person_id": "p1", "linked_entities": ["E1", "E2"]},
            {"person_id": "p2", "linked_entities": ["E2", "E3"]},
        ]
        entities = [
            {"entity_id": "E1", "state": "CA", "loan_amount": 100000},
            {"entity_id": "E2", "state": "CA", "loan_amount": 200000},
            {"entity_id": "E3", "state": "NV", "loan_amount": 300000},
        ]
        clusters = build_control_clusters(people, entities)
        assert len(clusters) >= 1
        cluster = clusters[0]
        assert cluster["total_entities"] >= 2
        assert cluster["total_loan_amount"] > 0


# ── neo4j_export tests ─────────────────────────────────────────

class TestNeo4jExport:
    def setup_method(self):
        clear_cache()

    def test_export_entities(self):
        entities = [
            {"entity_id": "E1", "entity_name": "ACME LLC", "entity_type": "LLC"},
        ]
        path = export_entities(entities, batch_id="test_entities")
        assert path.exists()
        assert path.suffix == ".jsonl"

    def test_export_empty(self):
        path = export_entities([])
        assert path.name == "empty"

    def test_export_relationships(self):
        rels = [
            {
                "source_entity_id": "E1",
                "target_entity_id": "E2",
                "relationship_type": "same_agent",
                "weight": 1.0,
            }
        ]
        path = export_relationships(rels, batch_id="test_rels")
        assert path.exists()

    def test_export_stats(self):
        stats = get_export_stats()
        assert "batch_files" in stats
        assert "total_records" in stats


# ── Integration smoke test ─────────────────────────────────────

class TestPipelineIntegration:
    def test_full_entity_flow(self):
        """Test: normalize -> match -> extract attorney -> export."""
        clear_cache()

        # Normalize
        name = normalize_name("ACME INVESTMENTS LLC")
        assert name == "ACME INVESTMENTS"

        # Match
        candidates = [{"entity_id": "E1", "entity_name": "ACME INVESTMENTS LLC"}]
        match = match_exact("ACME INVESTMENTS LLC", candidates)
        assert match is not None

        # Extract attorney
        att = extract_attorney_from_agent("JOHN SMITH, Bar #12345", "E1")
        assert att is not None

        # Export
        path = export_entities([{"entity_id": "E1", "entity_name": "ACME INVESTMENTS LLC"}])
        assert path.exists()
