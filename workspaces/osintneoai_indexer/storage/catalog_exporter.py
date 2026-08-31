"""
OsintNeoAi Indexer: Master JSON Catalog Exporter & Cryptographic Merkle Root Engine
Path: C:\\OsintNeoAi\\workspaces\\osintneoai_indexer\\storage\\catalog_exporter.py
Milestone: M3 (Entity Resolution & Vault Storage) — Feature 15

Implements RFC 8785 Canonical JSON Master Timeline Catalog generator with:
- Hierarchical 5-branch Merkle tree root hash aggregation
- Chronologically ordered timeline serialization
- Comprehensive metadata, entity aliases, and audit invariants
"""

from __future__ import annotations

import datetime
import hashlib
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Union

from config import DEFAULT_MASTER_CATALOG_PATH
from storage.vault_db import VaultDB

logger = logging.getLogger("osintneoai.storage.catalog_exporter")

EMPTY_SHA256: str = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"


# ============================================================================
# 1. RFC 8785 CANONICAL JSON HELPERS & MERKLE CALCULATOR
# ============================================================================

def canonical_json_dumps(data: Any) -> str:
    """
    Serializes data to RFC 8785 compliant canonical JSON string.
    Ensures UTF-8 encoding, deterministic key ordering, and minimal separators.
    """
    return json.dumps(
        data,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":")
    )


def canonical_json_bytes(data: Any) -> bytes:
    """Returns UTF-8 bytes for canonical JSON representation."""
    return canonical_json_dumps(data).encode("utf-8")


def canonical_json_sha256(data: Any) -> str:
    """Computes SHA-256 hex digest of RFC 8785 canonical JSON bytes."""
    return hashlib.sha256(canonical_json_bytes(data)).hexdigest().lower()


def compute_merkle_root(leaf_hashes: Sequence[str]) -> str:
    """
    Computes pairwise binary Merkle tree root hash for a sequence of leaf hashes.
    If the sequence is empty, returns the standard empty SHA-256 hash.
    If the sequence has an odd number of nodes at any level, duplicates the last node.
    """
    if not leaf_hashes:
        return EMPTY_SHA256

    current_level = [h.lower() for h in leaf_hashes]

    while len(current_level) > 1:
        next_level: List[str] = []
        if len(current_level) % 2 != 0:
            current_level.append(current_level[-1])

        for i in range(0, len(current_level), 2):
            left = current_level[i]
            right = current_level[i + 1]
            parent_hash = hashlib.sha256((left + right).encode("utf-8")).hexdigest().lower()
            next_level.append(parent_hash)

        current_level = next_level

    return current_level[0]


# ============================================================================
# 2. CATALOG EXPORTER CLASS
# ============================================================================

class CatalogExporter:
    """
    Exports normalized relational vault data to RFC 8785 Master JSON Catalog
    with cryptographic Merkle tree signatures.
    """

    def __init__(
        self,
        vault_db: Optional[VaultDB] = None,
        output_path: Union[str, Path] = DEFAULT_MASTER_CATALOG_PATH,
    ) -> None:
        self.vault_db = vault_db or VaultDB()
        self.output_path = Path(output_path)

    def build_catalog(
        self,
        vault_db: Optional[VaultDB] = None,
        integrity_mode: str = "development",
    ) -> Dict[str, Any]:
        """
        Builds the in-memory master catalog structure from the SQLite vault.
        """
        db = vault_db or self.vault_db

        # 1. Fetch normalized records
        raw_docs = db.get_all_documents()
        raw_ents = db.get_all_entities()
        raw_evts = db.get_timeline_events(chronological=True)
        raw_trx = db.get_financial_transactions()
        raw_rels = db.get_relationships()

        # 2. Clean & format documents
        documents: List[Dict[str, Any]] = []
        doc_hashes: List[str] = []
        for d in raw_docs:
            doc_item = {
                "document_id": d["document_id"],
                "source_uri": d["source_uri"],
                "file_name": d["file_name"],
                "file_path": d["file_path"],
                "file_size_bytes": d["file_size_bytes"],
                "mime_type": d["mime_type"],
                "file_sha256": d["file_sha256"],
                "content_sha256": d["content_sha256"],
                "ingestion_timestamp": d["ingestion_timestamp"],
                "document_date": d["document_date"],
                "page_count": d["page_count"],
                "ocr_confidence": d["ocr_confidence"],
            }
            documents.append(doc_item)
            doc_hashes.append(canonical_json_sha256(doc_item))

        # 3. Clean & format entities
        entities: List[Dict[str, Any]] = []
        ent_hashes: List[str] = []
        for e in raw_ents:
            try:
                aliases = json.loads(e["aliases_json"]) if isinstance(e["aliases_json"], str) else e["aliases_json"]
            except Exception:
                aliases = [e["canonical_name"]]

            try:
                meta = json.loads(e["metadata_json"]) if isinstance(e["metadata_json"], str) else e["metadata_json"]
            except Exception:
                meta = {}

            ent_item = {
                "entity_id": e["entity_id"],
                "canonical_name": e["canonical_name"],
                "entity_category": e["entity_category"],
                "role_or_title": e["role_or_title"],
                "primary_jurisdiction": e["primary_jurisdiction"],
                "aliases": sorted(list(set(aliases))),
                "metadata": meta,
            }
            entities.append(ent_item)
            ent_hashes.append(canonical_json_sha256(ent_item))

        # 4. Clean & format timeline events (strictly sorted)
        timeline_events: List[Dict[str, Any]] = []
        evt_hashes: List[str] = []
        for idx, ev in enumerate(raw_evts, start=1):
            evt_item = {
                "event_id": ev["event_id"],
                "document_id": ev["document_id"],
                "event_date_iso": ev["event_date_iso"],
                "event_type": ev["event_type"],
                "title": ev["title"],
                "description": ev["description"],
                "raw_snippet": ev["raw_snippet"],
                "primary_entity_id": ev["primary_entity_id"],
                "location": ev["location"],
                "jurisdiction": ev["jurisdiction"],
                "confidence_score": ev["confidence_score"],
                "chronological_rank": idx,
            }
            timeline_events.append(evt_item)
            evt_hashes.append(canonical_json_sha256(evt_item))

        # 5. Clean & format financial transactions
        financial_transactions: List[Dict[str, Any]] = []
        trx_hashes: List[str] = []
        for t in raw_trx:
            trx_item = {
                "transaction_id": t["transaction_id"],
                "document_id": t["document_id"],
                "event_id": t["event_id"],
                "transaction_date_iso": t["transaction_date_iso"],
                "amount": float(t["amount"]),
                "currency": t["currency"],
                "sender_entity_id": t["sender_entity_id"],
                "recipient_entity_id": t["recipient_entity_id"],
                "payment_method": t["payment_method"],
                "account_or_check_num": t["account_or_check_num"],
                "transaction_purpose": t["transaction_purpose"],
                "is_predicate_act": bool(t["is_predicate_act"]),
            }
            financial_transactions.append(trx_item)
            trx_hashes.append(canonical_json_sha256(trx_item))

        # 6. Clean & format relationships
        relationships: List[Dict[str, Any]] = []
        rel_hashes: List[str] = []
        for r in raw_rels:
            rel_item = {
                "relationship_id": r["relationship_id"],
                "source_entity_id": r["source_entity_id"],
                "target_entity_id": r["target_entity_id"],
                "relationship_type": r["relationship_type"],
                "direction": r["direction"],
                "confidence": r["confidence"],
                "evidence_summary": r["evidence_summary"],
            }
            relationships.append(rel_item)
            rel_hashes.append(canonical_json_sha256(rel_item))

        # 7. Compute individual branch Merkle roots
        docs_root = compute_merkle_root(doc_hashes)
        ents_root = compute_merkle_root(ent_hashes)
        evts_root = compute_merkle_root(evt_hashes)
        trx_root = compute_merkle_root(trx_hashes)
        rels_root = compute_merkle_root(rel_hashes)

        # 8. Hierarchical Composite Root: SHA256(docs || ents || evts || trx || rels)
        master_root = hashlib.sha256(
            (docs_root + ents_root + evts_root + trx_root + rels_root).encode("utf-8")
        ).hexdigest().lower()

        # Invariant checks
        fk_violations = len(db.check_foreign_keys())
        chrono_inversions = db.check_chronological_inversions()
        all_passed = (fk_violations == 0) and (chrono_inversions == 0)

        # Log audit entry to vault DB
        db.verify_invariants(tier_level="MASTER_CATALOG_EXPORT", merkle_root=master_root)

        now_utc = datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z")

        catalog = {
            "catalog_metadata": {
                "schema_version": "1.0.0",
                "generated_at": now_utc,
                "root_merkle_sha256": master_root,
                "total_documents": len(documents),
                "total_entities": len(entities),
                "total_events": len(timeline_events),
                "total_transactions": len(financial_transactions),
                "total_relationships": len(relationships),
                "integrity_mode": integrity_mode,
            },
            "documents": documents,
            "entities": entities,
            "timeline_events": timeline_events,
            "financial_transactions": financial_transactions,
            "relationships": relationships,
            "audit_invariants": {
                "documents_merkle_sha256": docs_root,
                "entities_merkle_sha256": ents_root,
                "events_merkle_sha256": evts_root,
                "transactions_merkle_sha256": trx_root,
                "relationships_merkle_sha256": rels_root,
                "foreign_key_violations": fk_violations,
                "chronological_inversions": chrono_inversions,
                "all_invariants_passed": all_passed,
            },
        }

        return catalog

    def export_to_file(
        self,
        output_path: Optional[Union[str, Path]] = None,
        vault_db: Optional[VaultDB] = None,
        integrity_mode: str = "development",
        indent: Optional[int] = 2,
    ) -> Path:
        """
        Exports the canonical master catalog JSON file to disk.
        """
        target_path = Path(output_path) if output_path else self.output_path
        target_path.parent.mkdir(parents=True, exist_ok=True)

        catalog_data = self.build_catalog(vault_db=vault_db, integrity_mode=integrity_mode)

        if indent is not None:
            formatted_json = json.dumps(catalog_data, indent=indent, ensure_ascii=False)
        else:
            formatted_json = canonical_json_dumps(catalog_data)

        target_path.write_text(formatted_json, encoding="utf-8")
        logger.info("Successfully exported Master Timeline Catalog to: %s", target_path)

        return target_path
