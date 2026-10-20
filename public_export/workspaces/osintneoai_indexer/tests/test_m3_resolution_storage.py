"""
OsintNeoAi Indexer: Comprehensive Milestone 3 Test Suite
Path: C:\\OsintNeoAi\\workspaces\\osintneoai_indexer\\tests\\test_m3_resolution_storage.py
Milestone: M3 (Entity Resolution, SQLite Relational Vault & Master JSON Catalog, and End-to-End Pipeline)

Covers:
1. Entity Taxonomy, Enums, Dataclasses & Confidence Scoring
2. Disjoint-Set Union (DSU) Data Structure
3. Phonetic Blocking (Soundex & Double Metaphone) & String Distances (Jaro-Winkler)
4. 4-Stage Entity Resolution, Mention Clustering & Relational Graph Synthesis
5. SQLite Vault 3NF Database, WAL, PRAGMAs, Cascades, Indexes & Batch Transactions
6. RFC 8785 Master JSON Catalog Generator & Pairwise Hierarchical Merkle Root Tree
7. End-to-End Indexer Pipeline Execution & Invariant Verification
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
import tempfile
from pathlib import Path
from typing import Any, Dict, List

import pytest

from extractors.document_extractor import ExtractedRecord
from pipeline import OsintNeoAiIndexerPipeline, PipelineResult
from resolution.entity_resolver import (
    DisjointSetUnion,
    EntityResolver,
    jaro_winkler_similarity,
    levenshtein_ratio,
)
from resolution.taxonomy import (
    CANONICAL_TARGETS,
    CanonicalEntity,
    EntityCategory,
    EntityMention,
    EventType,
    FinancialTransaction,
    PaymentMethod,
    Relationship,
    RelationshipType,
    TimelineEvent,
    calculate_confidence,
    get_category_prefix,
)
from storage.catalog_exporter import (
    CatalogExporter,
    canonical_json_dumps,
    canonical_json_sha256,
    compute_merkle_root,
)
from storage.vault_db import VaultDB


# ============================================================================
# 1. TAXONOMY, DATACLASSES & CONFIDENCE SCORING TESTS
# ============================================================================

def test_entity_categories_enumeration():
    """Validates that all 6 domain entity categories + OTHER are defined."""
    expected_categories = {
        "INDIVIDUAL",
        "MUNICIPAL_BODY",
        "FINANCIAL_INSTITUTION",
        "PROPERTY_MANAGEMENT",
        "LEGAL_AGENCY",
        "COMMERCIAL_ENTITY",
        "OTHER",
    }
    actual_categories = {c.value for c in EntityCategory}
    assert actual_categories == expected_categories


def test_category_prefix_generation():
    """Validates deterministic ID prefix mapping per category."""
    assert get_category_prefix(EntityCategory.INDIVIDUAL) == "ENT-IND"
    assert get_category_prefix(EntityCategory.MUNICIPAL_BODY) == "ENT-MUN"
    assert get_category_prefix(EntityCategory.FINANCIAL_INSTITUTION) == "ENT-FIN"
    assert get_category_prefix(EntityCategory.PROPERTY_MANAGEMENT) == "ENT-PRP"
    assert get_category_prefix(EntityCategory.LEGAL_AGENCY) == "ENT-LEG"
    assert get_category_prefix(EntityCategory.COMMERCIAL_ENTITY) == "ENT-COM"
    assert get_category_prefix(EntityCategory.OTHER) == "ENT-OTH"


def test_confidence_scoring_formula():
    """Validates contextual co-occurrence confidence formula."""
    # Exact match gives 1.0
    assert calculate_confidence(1.0, exact_match=True) == 1.0

    # 0.50 * 0.90 + 0.20 * 1 + 0.15 * 0 + 0.15 * 0 = 0.45 + 0.20 = 0.65
    score = calculate_confidence(0.90, shared_docket=True, shared_address=False, shared_agency=False)
    assert score == pytest.approx(0.65, abs=0.01)

    # Full context boost: 0.50 * 0.80 + 0.20 + 0.15 + 0.15 = 0.40 + 0.50 = 0.90
    score_full = calculate_confidence(0.80, shared_docket=True, shared_address=True, shared_agency=True)
    assert score_full == pytest.approx(0.90, abs=0.01)


def test_canonical_targets_seed_integrity():
    """Validates that seed targets contain expected investigation figures."""
    target_names = {t["canonical_name"] for t in CANONICAL_TARGETS}
    assert "Harry Sidhu" in target_names
    assert "Todd Ament" in target_names
    assert "Melahat Rafiei" in target_names
    assert "City of Anaheim" in target_names
    assert "Woodbridge Meadows Apartments LLC" in target_names
    assert "USDC CDCA" in target_names
    assert "Wallace, Richardson, Sontag & Le LLP" in target_names


# ============================================================================
# 2. DISJOINT-SET UNION (DSU) TESTS
# ============================================================================

def test_dsu_basic_operations():
    """Validates DSU initialization, union, find, and connectivity."""
    dsu = DisjointSetUnion(["A", "B", "C", "D", "E"])
    assert dsu.count_clusters() == 5
    assert not dsu.is_connected("A", "B")

    # Union A and B
    assert dsu.union("A", "B") is True
    assert dsu.is_connected("A", "B")
    assert dsu.count_clusters() == 4

    # Redundant union returns False
    assert dsu.union("A", "B") is False

    # Union B and C -> A, B, C are in same cluster
    dsu.union("B", "C")
    assert dsu.is_connected("A", "C")
    assert dsu.count_clusters() == 3

    # Check clusters map
    clusters = dsu.get_clusters()
    root_abc = dsu.find("A")
    assert clusters[root_abc] == {"A", "B", "C"}


def test_dsu_path_compression_stress():
    """Validates DSU path compression under linear chaining."""
    dsu = DisjointSetUnion()
    n = 100
    for i in range(n):
        dsu.add(str(i))
    for i in range(n - 1):
        dsu.union(str(i), str(i + 1))

    assert dsu.count_clusters() == 1
    assert dsu.is_connected("0", str(n - 1))


# ============================================================================
# 3. STRING DISTANCE & PHONETIC BLOCKING TESTS
# ============================================================================

def test_jaro_winkler_similarity():
    """Validates Jaro-Winkler metric behavior."""
    # Identical strings
    assert jaro_winkler_similarity("SIDHU", "SIDHU") == 1.0
    assert jaro_winkler_similarity("", "") == 1.0
    assert jaro_winkler_similarity("HARRY", "") == 0.0

    # Near matches with OCR noise
    sim1 = jaro_winkler_similarity("HARRY SIDHU", "HARRY SLDHU")
    assert sim1 > 0.90

    # Transposition
    sim2 = jaro_winkler_similarity("MARTHA", "MARHTA")
    assert sim2 > 0.90

    # Unrelated strings
    sim3 = jaro_winkler_similarity("ANAHEIM", "NEW JERSEY")
    assert sim3 < 0.50


def test_levenshtein_ratio():
    """Validates normalized Levenshtein ratio."""
    assert levenshtein_ratio("test", "test") == 1.0
    assert levenshtein_ratio("", "") == 1.0
    assert levenshtein_ratio("test", "tent") == 0.75
    assert levenshtein_ratio("kitten", "sitting") == pytest.approx(0.571428, abs=0.01)


def test_entity_resolver_normalization_and_suffixes():
    """Validates normalization and corporate suffix stripping."""
    res = EntityResolver()
    assert res.normalize_name("Mayor Harry Sidhu") == "HARRY SIDHU"
    assert res.normalize_name("TA Group LLC") == "TA GROUP"
    assert res.normalize_name("Wallace, Richardson, Sontag & Le LLP") == "WALLACE, RICHARDSON, SONTAG & LE"
    assert res.normalize_name("Woodbridge Meadows Apartments LLC") == "WOODBRIDGE MEADOWS APARTMENTS"
    assert res.normalize_name("Hon. Carmen Luege") == "CARMEN LUEGE"


def test_phonetic_blocking_keys():
    """Validates Soundex and Double Metaphone key generation."""
    keys_smith = EntityResolver.get_blocking_keys("Smith")
    keys_smyth = EntityResolver.get_blocking_keys("Smyth")
    # Both should share Soundex S530 or Metaphone SM0
    assert len(keys_smith & keys_smyth) > 0


# ============================================================================
# 4. 4-STAGE ENTITY RESOLUTION & CLUSTERING TESTS
# ============================================================================

def test_resolve_single_name_against_seed():
    """Validates resolving variants to seed canonical entities."""
    resolver = EntityResolver()

    # Exact canonical name
    ent1 = resolver.resolve_single_name("Harry Sidhu")
    assert ent1 is not None
    assert ent1.canonical_name == "Harry Sidhu"
    assert ent1.entity_category == EntityCategory.INDIVIDUAL

    # Name with honorific and alias
    ent2 = resolver.resolve_single_name("Mayor Harry Sidhu")
    assert ent2 is not None
    assert ent2.canonical_name == "Harry Sidhu"

    # OCR noise variant
    ent3 = resolver.resolve_single_name("Harry Sldhu")
    assert ent3 is not None
    assert ent3.canonical_name == "Harry Sidhu"

    # Corporate variant
    ent4 = resolver.resolve_single_name("TA Group L.L.C.")
    assert ent4 is not None
    assert ent4.canonical_name == "TA Group LLC"
    assert ent4.entity_category == EntityCategory.FINANCIAL_INSTITUTION


def test_cluster_mentions_across_documents():
    """Validates clustering multiple raw mentions into canonical entity clusters."""
    resolver = EntityResolver()

    mentions = [
        EntityMention(mention_id="M1", document_id="DOC1", raw_text="Todd Ament", entity_category=EntityCategory.INDIVIDUAL),
        EntityMention(mention_id="M2", document_id="DOC2", raw_text="Todd Stephen Ament", entity_category=EntityCategory.INDIVIDUAL),
        EntityMention(mention_id="M3", document_id="DOC3", raw_text="T. Ament", entity_category=EntityCategory.INDIVIDUAL),
        EntityMention(mention_id="M4", document_id="DOC1", raw_text="City of Anaheim", entity_category=EntityCategory.MUNICIPAL_BODY),
        EntityMention(mention_id="M5", document_id="DOC2", raw_text="Anaheim City Council", entity_category=EntityCategory.MUNICIPAL_BODY),
    ]

    entities, updated_mentions = resolver.cluster_mentions(mentions)

    # Should form 2 canonical clusters
    assert len(entities) == 2
    ent_names = {e.canonical_name for e in entities}
    assert "Todd Ament" in ent_names
    assert "City of Anaheim" in ent_names

    # Check that updated mentions have assigned entity_ids
    assert all(m.entity_id is not None for m in updated_mentions)


def test_extract_and_resolve_records():
    """Validates end-to-end extraction and resolution from ExtractedRecord objects."""
    resolver = EntityResolver()

    sample_record = ExtractedRecord(
        record_id="DOC-001",
        artifact_sha256="abc123sha256",
        source_path="C:/OsintNeoAi/evidence/plea_agreement.pdf",
        source_type="local_file",
        mime_type="application/pdf",
        normalized_date="2022-05-24T00:00:00Z",
        raw_date_string="May 24, 2022",
        extracted_text="United States v. Harry Sidhu. The defendant Mayor Harry Sidhu agreed to a plea agreement involving $320M stadium land sale and TA Group LLC wire transfers.",
        ocr_engine_used="pymupdf_native",
        financial_amounts=[{"raw": "$320M", "amount_float": 320000000.0, "amount_cents": 32000000000, "currency": "USD"}],
        case_numbers=["8:23-cr-00108-CJC"],
        sender="Special Agent Brian Adkins",
        recipients=["USDC CDCA"],
        metadata={"file_size_bytes": 1024},
    )

    entities, mentions, events, transactions, relationships = resolver.extract_and_resolve([sample_record])

    assert len(entities) >= 3
    assert len(mentions) >= 3
    assert len(events) >= 1
    assert len(transactions) == 1
    assert len(relationships) >= 1

    # Check transaction properties
    trx = transactions[0]
    assert trx.amount == 320000000.0
    assert trx.transaction_date_iso == "2022-05-24T00:00:00Z"

    # Check event properties
    evt = events[0]
    assert evt.event_date_iso == "2022-05-24T00:00:00Z"
    assert evt.chronological_rank == 1


# ============================================================================
# 5. SQLITE RELATIONAL VAULT DB TESTS
# ============================================================================

def test_vault_db_initialization_and_pragmas(tmp_path: Path):
    """Validates WAL mode, foreign keys, and 3NF schema tables in SQLite."""
    db_file = tmp_path / "test_vault.db"
    vault = VaultDB(db_path=db_file)

    with vault.get_connection() as conn:
        # Check foreign keys enabled
        fk_enabled = conn.execute("PRAGMA foreign_keys;").fetchone()[0]
        assert fk_enabled == 1

        # Check WAL mode
        journal_mode = conn.execute("PRAGMA journal_mode;").fetchone()[0]
        assert journal_mode.upper() == "WAL"

        # Check tables exist
        tables_cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = {r[0] for r in tables_cur.fetchall()}
        expected_tables = {
            "documents",
            "entities",
            "entity_mentions",
            "timeline_events",
            "financial_transactions",
            "relationships",
            "schema_invariants_log",
        }
        assert expected_tables.issubset(tables)


def test_vault_db_crud_and_foreign_key_enforcement(tmp_path: Path):
    """Validates inserts, queries, cascades, and strict foreign key integrity."""
    db_file = tmp_path / "test_vault.db"
    vault = VaultDB(db_path=db_file)

    # 1. Insert Document
    doc_id = vault.insert_document({
        "document_id": "DOC-100",
        "source_uri": "C:/evidence/doc1.pdf",
        "file_name": "doc1.pdf",
        "file_path": "C:/evidence/doc1.pdf",
        "file_size_bytes": 5000,
        "mime_type": "application/pdf",
        "file_sha256": "1111222233334444555566667777888899990000aaaabbbbccccddddeeeeffff",
        "content_sha256": "1111222233334444555566667777888899990000aaaabbbbccccddddeeeeffff",
        "ingestion_timestamp": "2026-08-29T18:00:00Z",
        "document_date": "2022-01-15",
        "extracted_text": "Sample document content.",
    })
    assert doc_id == "DOC-100"

    # 2. Insert Entity
    ent_id = vault.insert_entity({
        "entity_id": "ENT-IND-001",
        "canonical_name": "Todd Ament",
        "entity_category": EntityCategory.INDIVIDUAL,
        "role_or_title": "CEO",
        "aliases": ["Todd Stephen Ament"],
    })
    assert ent_id == "ENT-IND-001"

    # 3. Insert Mention linking DOC-100 and ENT-IND-001
    mention_id = vault.insert_mention({
        "mention_id": "MEN-100",
        "document_id": "DOC-100",
        "entity_id": "ENT-IND-001",
        "raw_mention_text": "Todd Ament",
        "char_offset_start": 0,
        "char_offset_end": 10,
        "context_snippet": "Todd Ament was present.",
    })
    assert mention_id == "MEN-100"

    # 4. Verify Foreign Key Rejection on Invalid entity_id
    with pytest.raises(sqlite3.IntegrityError):
        vault.insert_mention({
            "mention_id": "MEN-INVALID",
            "document_id": "DOC-100",
            "entity_id": "ENT-NONEXISTENT",
            "raw_mention_text": "Nobody",
        })

    # 5. Check Summary Counts
    counts = vault.get_summary_counts()
    assert counts["total_documents"] == 1
    assert counts["total_entities"] == 1
    assert counts["total_mentions"] == 1

    # 6. Verify Invariants Check passes
    audit = vault.verify_invariants(tier_level="TIER_1")
    assert audit["verification_status"] == "PASSED"
    assert audit["foreign_key_violations"] == 0
    assert audit["all_invariants_passed"] is True


def test_vault_db_self_relationship_check_constraint(tmp_path: Path):
    """Validates that relationships table rejects source_entity_id == target_entity_id."""
    db_file = tmp_path / "test_vault.db"
    vault = VaultDB(db_path=db_file)

    vault.insert_entity({
        "entity_id": "ENT-IND-1",
        "canonical_name": "Harry Sidhu",
        "entity_category": EntityCategory.INDIVIDUAL,
    })

    # Insertion should be ignored or raise check constraint violation
    vault.insert_relationship({
        "relationship_id": "REL-INVALID",
        "source_entity_id": "ENT-IND-1",
        "target_entity_id": "ENT-IND-1",
        "relationship_type": RelationshipType.CONNECTED_TO,
    })

    # Verify no self-loop relationship was inserted
    rels = vault.get_relationships()
    assert len(rels) == 0


# ============================================================================
# 6. MASTER JSON CATALOG & MERKLE ROOT TESTS
# ============================================================================

def test_canonical_json_formatting_and_hashing():
    """Validates RFC 8785 canonical JSON sorting and deterministic hashing."""
    obj1 = {"b": 2, "a": 1, "nested": {"y": "val", "x": "val"}}
    obj2 = {"nested": {"x": "val", "y": "val"}, "a": 1, "b": 2}

    # Canonical dumps should be identical byte-for-byte
    json1 = canonical_json_dumps(obj1)
    json2 = canonical_json_dumps(obj2)
    assert json1 == json2
    assert json1 == '{"a":1,"b":2,"nested":{"x":"val","y":"val"}}'

    # Hash must match
    assert canonical_json_sha256(obj1) == canonical_json_sha256(obj2)


def test_merkle_root_pairwise_tree_calculation():
    """Validates binary Merkle tree root reduction."""
    # Empty list
    empty_root = compute_merkle_root([])
    assert empty_root == "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"

    # Single leaf
    h1 = hashlib.sha256(b"leaf1").hexdigest().lower()
    assert compute_merkle_root([h1]) == h1

    # Two leaves
    h2 = hashlib.sha256(b"leaf2").hexdigest().lower()
    expected_pair = hashlib.sha256((h1 + h2).encode("utf-8")).hexdigest().lower()
    assert compute_merkle_root([h1, h2]) == expected_pair

    # Odd leaves (3 leaves -> 3rd paired with itself)
    h3 = hashlib.sha256(b"leaf3").hexdigest().lower()
    p1 = hashlib.sha256((h1 + h2).encode("utf-8")).hexdigest().lower()
    p2 = hashlib.sha256((h3 + h3).encode("utf-8")).hexdigest().lower()
    expected_odd = hashlib.sha256((p1 + p2).encode("utf-8")).hexdigest().lower()
    assert compute_merkle_root([h1, h2, h3]) == expected_odd


def test_catalog_exporter_end_to_end(tmp_path: Path):
    """Validates Master JSON Catalog generation, schema conformance, and disk export."""
    db_file = tmp_path / "test_vault.db"
    catalog_file = tmp_path / "master_timeline_catalog.json"
    vault = VaultDB(db_path=db_file)

    # Populate sample vault
    vault.insert_document({
        "document_id": "DOC-A",
        "source_uri": "C:/docs/plea.pdf",
        "file_name": "plea.pdf",
        "file_path": "C:/docs/plea.pdf",
        "file_size_bytes": 1234,
        "mime_type": "application/pdf",
        "file_sha256": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        "content_sha256": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        "ingestion_timestamp": "2026-08-29T18:00:00Z",
        "document_date": "2022-05-24",
        "extracted_text": "Plea agreement text.",
    })

    vault.insert_entity({
        "entity_id": "ENT-IND-A",
        "canonical_name": "Harry Sidhu",
        "entity_category": EntityCategory.INDIVIDUAL,
        "aliases": ["Mayor Sidhu"],
    })

    vault.insert_event({
        "event_id": "EVT-20220524-001",
        "document_id": "DOC-A",
        "event_date_iso": "2022-05-24",
        "event_year": 2022,
        "event_month": 5,
        "event_day": 24,
        "event_type": EventType.JUDICIAL_FILING,
        "title": "Harry Sidhu Plea Agreement",
        "description": "Defendant entered guilty plea.",
        "primary_entity_id": "ENT-IND-A",
        "chronological_rank": 1,
    })

    exporter = CatalogExporter(vault_db=vault, output_path=catalog_file)
    exported_path = exporter.export_to_file()

    assert exported_path.exists()
    catalog_json = json.loads(exported_path.read_text(encoding="utf-8"))

    # Validate Schema Properties
    assert "catalog_metadata" in catalog_json
    assert "documents" in catalog_json
    assert "entities" in catalog_json
    assert "timeline_events" in catalog_json
    assert "financial_transactions" in catalog_json
    assert "relationships" in catalog_json
    assert "audit_invariants" in catalog_json

    meta = catalog_json["catalog_metadata"]
    assert meta["total_documents"] == 1
    assert meta["total_entities"] == 1
    assert meta["total_events"] == 1
    assert len(meta["root_merkle_sha256"]) == 64

    invariants = catalog_json["audit_invariants"]
    assert invariants["foreign_key_violations"] == 0
    assert invariants["chronological_inversions"] == 0
    assert invariants["all_invariants_passed"] is True


# ============================================================================
# 7. END-TO-END PIPELINE EXECUTION TESTS
# ============================================================================

def test_pipeline_process_records(tmp_path: Path):
    """Validates pipeline execution over in-memory extracted records."""
    vault_file = tmp_path / "pipeline_vault.db"
    catalog_file = tmp_path / "pipeline_catalog.json"

    pipeline = OsintNeoAiIndexerPipeline(
        vault_db_path=vault_file,
        master_catalog_path=catalog_file,
        similarity_threshold=0.88,
        integrity_mode="development",
    )

    records = [
        ExtractedRecord(
            record_id="REC-1",
            artifact_sha256="1111111111111111111111111111111111111111111111111111111111111111",
            source_path="C:/OsintNeoAi/evidence/doc1.pdf",
            source_type="local_file",
            mime_type="application/pdf",
            normalized_date="2021-12-08T00:00:00Z",
            raw_date_string="December 8, 2021",
            extracted_text="California HCD issued a Notice of Violation to City of Anaheim regarding Angel Stadium 150-Acre Parcel with $96M penalty.",
            ocr_engine_used="pymupdf_native",
            financial_amounts=[{"raw": "$96M", "amount_float": 96000000.0, "amount_cents": 9600000000, "currency": "USD"}],
            case_numbers=[],
            sender="California HCD",
            recipients=["City of Anaheim"],
            metadata={"page_count": 5},
        ),
        ExtractedRecord(
            record_id="REC-2",
            artifact_sha256="2222222222222222222222222222222222222222222222222222222222222222",
            source_path="C:/OsintNeoAi/evidence/doc2.pdf",
            source_type="local_file",
            mime_type="application/pdf",
            normalized_date="2022-05-24T00:00:00Z",
            raw_date_string="May 24, 2022",
            extracted_text="Anaheim City Council Resolution No. 2022-064 voiding $320M land sale to SRB Management Escrow.",
            ocr_engine_used="pymupdf_native",
            financial_amounts=[{"raw": "$320M", "amount_float": 320000000.0, "amount_cents": 32000000000, "currency": "USD"}],
            case_numbers=[],
            sender="Anaheim City Council",
            recipients=["SRB Management Escrow"],
            metadata={"page_count": 3},
        ),
    ]

    result: PipelineResult = pipeline.process_records(records)

    assert result.total_extracted_records == 2
    assert result.total_entities >= 3
    assert result.total_events == 2
    assert result.total_transactions == 2
    assert result.all_invariants_passed is True
    assert len(result.root_merkle_sha256) == 64
    assert result.vault_db_path.exists()
    assert result.master_catalog_path.exists()


def test_pipeline_local_crawler_file_ingestion(tmp_path: Path):
    """Validates full pipeline execution on simulated files in a local directory."""
    source_dir = tmp_path / "evidence_files"
    source_dir.mkdir(parents=True, exist_ok=True)

    # Create dummy text files with investigation keywords
    file1 = source_dir / "affidavit.txt"
    file1.write_text(
        "FBI Special Agent Brian Adkins search warrant affidavit regarding Mayor Harry Sidhu and Todd Ament in USDC CDCA Case No. 8:23-cr-00108-CJC. Wire transfer $350,000 to TA Group LLC on 2022-04-10.",
        encoding="utf-8"
    )

    file2 = source_dir / "eviction_docket.txt"
    file2.write_text(
        "California Superior Court CJC Case No. 30-2021-01201327-CL-UD-CJC Woodbridge Meadows Apartments LLC v. Anthony DiMarcello. Attorney Richard S. Sontag filed default on 2021-06-29.",
        encoding="utf-8"
    )

    vault_file = tmp_path / "test_pipeline_vault.db"
    catalog_file = tmp_path / "test_pipeline_catalog.json"

    pipeline = OsintNeoAiIndexerPipeline(
        vault_db_path=vault_file,
        master_catalog_path=catalog_file,
        similarity_threshold=0.88,
    )

    result = pipeline.run(source_dirs=[source_dir])

    assert result.total_ingested_files == 2
    assert result.total_extracted_records == 2
    assert result.total_entities >= 4
    assert result.total_events >= 2
    assert result.all_invariants_passed is True
    assert vault_file.exists()
    assert catalog_file.exists()
