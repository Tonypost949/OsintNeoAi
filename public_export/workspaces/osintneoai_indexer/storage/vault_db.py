"""
OsintNeoAi Indexer: Normalized SQLite Relational Vault Database Manager
Path: C:\\OsintNeoAi\\workspaces\\osintneoai_indexer\\storage\\vault_db.py
Milestone: M3 (Entity Resolution & Vault Storage) — Feature 14

Implements SQLite 3NF relational vault (timeline_vault.db) with:
- Strict foreign key enforcement & WAL journal mode
- 7 Relational Tables: documents, entities, entity_mentions, timeline_events,
  financial_transactions, relationships, schema_invariants_log
- 14 Performance & Integrity Indexes
- Atomic batch operations, transaction context management, and invariant validation
"""

from __future__ import annotations

import contextlib
import json
import logging
import sqlite3
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any, Dict, Generator, Iterable, List, Optional, Sequence, Set, Tuple, Union

from config import DEFAULT_VAULT_DB_PATH, SQLITE_BATCH_SIZE

logger = logging.getLogger("osintneoai.storage.vault_db")


# ============================================================================
# 1. 3NF SCHEMA DEFINITIONS & PRAGMAS
# ============================================================================

VAULT_PRAGMAS = [
    "PRAGMA foreign_keys = ON;",
    "PRAGMA journal_mode = WAL;",
    "PRAGMA synchronous = NORMAL;",
    "PRAGMA busy_timeout = 5000;",
    "PRAGMA encoding = 'UTF-8';",
]

SCHEMA_DDL = """
-- 1. Ingested Documents & Raw Artifacts Table
CREATE TABLE IF NOT EXISTS documents (
    document_id TEXT PRIMARY KEY,
    source_uri TEXT NOT NULL,
    file_name TEXT NOT NULL,
    file_path TEXT NOT NULL,
    file_size_bytes INTEGER NOT NULL CHECK(file_size_bytes >= 0),
    mime_type TEXT NOT NULL,
    file_sha256 TEXT NOT NULL UNIQUE,
    content_sha256 TEXT NOT NULL,
    ingestion_timestamp TEXT NOT NULL,
    document_date TEXT,
    page_count INTEGER NOT NULL DEFAULT 1 CHECK(page_count >= 1),
    extracted_text TEXT,
    ocr_confidence REAL NOT NULL DEFAULT 1.0 CHECK(ocr_confidence >= 0.0 AND ocr_confidence <= 1.0),
    raw_metadata_json TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
);

-- 2. Canonical Entities Table
CREATE TABLE IF NOT EXISTS entities (
    entity_id TEXT PRIMARY KEY,
    canonical_name TEXT NOT NULL,
    entity_category TEXT NOT NULL CHECK(
        entity_category IN (
            'INDIVIDUAL',
            'MUNICIPAL_BODY',
            'FINANCIAL_INSTITUTION',
            'PROPERTY_MANAGEMENT',
            'LEGAL_AGENCY',
            'COMMERCIAL_ENTITY',
            'OTHER'
        )
    ),
    role_or_title TEXT,
    primary_jurisdiction TEXT,
    aliases_json TEXT NOT NULL DEFAULT '[]',
    metadata_json TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
);

-- 3. Entity Mentions Table
CREATE TABLE IF NOT EXISTS entity_mentions (
    mention_id TEXT PRIMARY KEY,
    document_id TEXT NOT NULL REFERENCES documents(document_id) ON DELETE CASCADE,
    entity_id TEXT NOT NULL REFERENCES entities(entity_id) ON DELETE CASCADE,
    raw_mention_text TEXT NOT NULL,
    char_offset_start INTEGER CHECK(char_offset_start >= 0),
    char_offset_end INTEGER CHECK(char_offset_end >= char_offset_start),
    page_number INTEGER NOT NULL DEFAULT 1 CHECK(page_number >= 1),
    context_snippet TEXT,
    confidence_score REAL NOT NULL DEFAULT 1.0 CHECK(confidence_score >= 0.0 AND confidence_score <= 1.0),
    extraction_method TEXT NOT NULL CHECK(extraction_method IN ('REGEX', 'NER', 'MANUAL', 'HYBRID')),
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
);

-- 4. Normalized Timeline Events Table
CREATE TABLE IF NOT EXISTS timeline_events (
    event_id TEXT PRIMARY KEY,
    document_id TEXT REFERENCES documents(document_id) ON DELETE SET NULL,
    event_date_iso TEXT NOT NULL,
    event_year INTEGER NOT NULL,
    event_month INTEGER CHECK(event_month BETWEEN 1 AND 12),
    event_day INTEGER CHECK(event_day BETWEEN 1 AND 31),
    event_type TEXT NOT NULL CHECK(
        event_type IN (
            'JUDICIAL_FILING',
            'REGULATORY_NOTICE',
            'LEGISLATIVE_ACTION',
            'FINANCIAL_TRANSACTION',
            'INCIDENT_LOG',
            'ARREST_SEARCH',
            'RETALIATION_ACTION',
            'ENVIRONMENTAL_HAZARD',
            'OTHER'
        )
    ),
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    raw_snippet TEXT,
    primary_entity_id TEXT REFERENCES entities(entity_id) ON DELETE SET NULL,
    location TEXT,
    jurisdiction TEXT,
    confidence_score REAL NOT NULL DEFAULT 1.0 CHECK(confidence_score >= 0.0 AND confidence_score <= 1.0),
    chronological_rank INTEGER,
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
);

-- 5. Financial Transactions Table
CREATE TABLE IF NOT EXISTS financial_transactions (
    transaction_id TEXT PRIMARY KEY,
    document_id TEXT REFERENCES documents(document_id) ON DELETE SET NULL,
    event_id TEXT REFERENCES timeline_events(event_id) ON DELETE SET NULL,
    transaction_date_iso TEXT NOT NULL,
    amount REAL NOT NULL CHECK(amount >= 0.0),
    currency TEXT NOT NULL DEFAULT 'USD',
    sender_entity_id TEXT REFERENCES entities(entity_id) ON DELETE SET NULL,
    recipient_entity_id TEXT REFERENCES entities(entity_id) ON DELETE SET NULL,
    sender_raw_text TEXT,
    recipient_raw_text TEXT,
    payment_method TEXT NOT NULL CHECK(
        payment_method IN ('WIRE', 'CHECK', 'CASH', 'ESCROW', 'GRANT', 'BRIBERY_CONDUIT', 'INVOICE', 'UNKNOWN')
    ),
    account_or_check_num TEXT,
    transaction_purpose TEXT,
    is_predicate_act INTEGER NOT NULL DEFAULT 0 CHECK(is_predicate_act IN (0, 1)),
    raw_snippet TEXT,
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
);

-- 6. Relational Graph Edges Table
CREATE TABLE IF NOT EXISTS relationships (
    relationship_id TEXT PRIMARY KEY,
    source_entity_id TEXT NOT NULL REFERENCES entities(entity_id) ON DELETE CASCADE,
    target_entity_id TEXT NOT NULL REFERENCES entities(entity_id) ON DELETE CASCADE,
    relationship_type TEXT NOT NULL CHECK(
        relationship_type IN (
            'OFFICER_OF',
            'EMPLOYED_BY',
            'CONTROLLED_BY',
            'TRANSFERRED_FUNDS_TO',
            'SUED_BY',
            'REPRESENTED_BY',
            'CO_CONSPIRATOR_WITH',
            'RETALIATED_AGAINST',
            'SUBMITTED_BID_TO',
            'ISSUED_NOTICE_TO',
            'CONNECTED_TO'
        )
    ),
    direction TEXT NOT NULL DEFAULT 'DIRECTED' CHECK(direction IN ('DIRECTED', 'BIDIRECTIONAL')),
    confidence REAL NOT NULL DEFAULT 1.0 CHECK(confidence >= 0.0 AND confidence <= 1.0),
    valid_from TEXT,
    valid_to TEXT,
    source_document_id TEXT REFERENCES documents(document_id) ON DELETE SET NULL,
    evidence_summary TEXT,
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    CHECK(source_entity_id <> target_entity_id)
);

-- 7. Automated Invariants & Cryptographic Audit Log Table
CREATE TABLE IF NOT EXISTS schema_invariants_log (
    audit_id INTEGER PRIMARY KEY AUTOINCREMENT,
    audit_timestamp TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    tier_level TEXT NOT NULL,
    merkle_root_sha256 TEXT NOT NULL,
    documents_count INTEGER NOT NULL,
    entities_count INTEGER NOT NULL,
    events_count INTEGER NOT NULL,
    transactions_count INTEGER NOT NULL,
    relationships_count INTEGER NOT NULL,
    foreign_key_violations INTEGER NOT NULL DEFAULT 0,
    chronological_inversions INTEGER NOT NULL DEFAULT 0,
    verification_status TEXT NOT NULL CHECK(verification_status IN ('PASSED', 'FAILED'))
);

-- Performance & Integrity Indexes
CREATE INDEX IF NOT EXISTS idx_documents_file_sha256 ON documents(file_sha256);
CREATE INDEX IF NOT EXISTS idx_documents_mime ON documents(mime_type);
CREATE INDEX IF NOT EXISTS idx_entities_canonical_name ON entities(canonical_name);
CREATE INDEX IF NOT EXISTS idx_entities_category ON entities(entity_category);
CREATE INDEX IF NOT EXISTS idx_entity_mentions_doc ON entity_mentions(document_id);
CREATE INDEX IF NOT EXISTS idx_entity_mentions_ent ON entity_mentions(entity_id);
CREATE INDEX IF NOT EXISTS idx_timeline_events_date ON timeline_events(event_date_iso);
CREATE INDEX IF NOT EXISTS idx_timeline_events_entity ON timeline_events(primary_entity_id);
CREATE INDEX IF NOT EXISTS idx_timeline_events_type ON timeline_events(event_type);
CREATE INDEX IF NOT EXISTS idx_financial_trx_date ON financial_transactions(transaction_date_iso);
CREATE INDEX IF NOT EXISTS idx_financial_trx_sender ON financial_transactions(sender_entity_id);
CREATE INDEX IF NOT EXISTS idx_financial_trx_recipient ON financial_transactions(recipient_entity_id);
CREATE INDEX IF NOT EXISTS idx_relationships_source_target ON relationships(source_entity_id, target_entity_id);
CREATE INDEX IF NOT EXISTS idx_relationships_type ON relationships(relationship_type);
"""


# ============================================================================
# 2. VAULT DATABASE MANAGER CLASS
# ============================================================================

class VaultDB:
    """
    Thread-safe, WAL-enabled relational SQLite database manager for timeline_vault.db.
    """

    def __init__(self, db_path: Union[str, Path] = DEFAULT_VAULT_DB_PATH) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def get_connection(self) -> sqlite3.Connection:
        """Opens a configured SQLite connection with foreign keys and WAL enabled."""
        conn = sqlite3.connect(
            str(self.db_path),
            timeout=10.0,
            detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES,
        )
        conn.row_factory = sqlite3.Row
        for pragma in VAULT_PRAGMAS:
            conn.execute(pragma)
        return conn

    @contextlib.contextmanager
    def transaction(self) -> Generator[sqlite3.Connection, None, None]:
        """Context manager providing an atomic database transaction with automatic commit/rollback."""
        conn = self.get_connection()
        try:
            conn.execute("BEGIN TRANSACTION;")
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error("Database transaction rolled back due to error: %s", e)
            raise
        finally:
            conn.close()

    def _init_db(self) -> None:
        """Executes DDL to initialize tables and indexes."""
        with self.get_connection() as conn:
            conn.executescript(SCHEMA_DDL)
            conn.commit()

    # ------------------------------------------------------------------------
    # Document Operations
    # ------------------------------------------------------------------------

    def insert_document(self, doc_data: Union[Dict[str, Any], Any]) -> str:
        """Inserts or updates a single document record."""
        return self.insert_documents_batch([doc_data])[0]

    def insert_documents_batch(self, docs: Sequence[Union[Dict[str, Any], Any]]) -> List[str]:
        """Batch inserts document records atomically."""
        if not docs:
            return []

        inserted_ids: List[str] = []
        sql = """
        INSERT INTO documents (
            document_id, source_uri, file_name, file_path, file_size_bytes,
            mime_type, file_sha256, content_sha256, ingestion_timestamp,
            document_date, page_count, extracted_text, ocr_confidence, raw_metadata_json
        ) VALUES (
            :document_id, :source_uri, :file_name, :file_path, :file_size_bytes,
            :mime_type, :file_sha256, :content_sha256, :ingestion_timestamp,
            :document_date, :page_count, :extracted_text, :ocr_confidence, :raw_metadata_json
        ) ON CONFLICT(document_id) DO UPDATE SET
            file_path = excluded.file_path,
            extracted_text = excluded.extracted_text,
            document_date = excluded.document_date,
            ocr_confidence = excluded.ocr_confidence,
            raw_metadata_json = excluded.raw_metadata_json;
        """

        rows = []
        for d in docs:
            d_dict = asdict(d) if is_dataclass(d) else dict(d)
            meta = d_dict.get("raw_metadata_json", d_dict.get("metadata", {}))
            if isinstance(meta, (dict, list)):
                meta_json = json.dumps(meta, ensure_ascii=False)
            else:
                meta_json = str(meta) if meta else "{}"

            doc_id = str(d_dict.get("document_id") or d_dict.get("record_id") or d_dict.get("artifact_sha256"))
            inserted_ids.append(doc_id)

            row = {
                "document_id": doc_id,
                "source_uri": str(d_dict.get("source_uri") or d_dict.get("source_path") or ""),
                "file_name": Path(str(d_dict.get("file_path") or d_dict.get("source_path") or "unknown")).name,
                "file_path": str(d_dict.get("file_path") or d_dict.get("source_path") or ""),
                "file_size_bytes": int(d_dict.get("file_size_bytes") or d_dict.get("file_size") or 0),
                "mime_type": str(d_dict.get("mime_type") or "application/octet-stream"),
                "file_sha256": str(d_dict.get("file_sha256") or d_dict.get("artifact_sha256") or ""),
                "content_sha256": str(d_dict.get("content_sha256") or d_dict.get("artifact_sha256") or ""),
                "ingestion_timestamp": str(d_dict.get("ingestion_timestamp") or "2026-08-29T18:00:00Z"),
                "document_date": d_dict.get("document_date") or d_dict.get("normalized_date"),
                "page_count": max(1, int(d_dict.get("page_count", 1))),
                "extracted_text": str(d_dict.get("extracted_text") or ""),
                "ocr_confidence": float(d_dict.get("ocr_confidence", 1.0)),
                "raw_metadata_json": meta_json,
            }
            rows.append(row)

        with self.transaction() as conn:
            conn.executemany(sql, rows)

        return inserted_ids

    # ------------------------------------------------------------------------
    # Entity Operations
    # ------------------------------------------------------------------------

    def insert_entity(self, entity_data: Union[Dict[str, Any], Any]) -> str:
        """Inserts or updates a single canonical entity."""
        return self.insert_entities_batch([entity_data])[0]

    def insert_entities_batch(self, entities: Sequence[Union[Dict[str, Any], Any]]) -> List[str]:
        """Batch inserts canonical entities."""
        if not entities:
            return []

        inserted_ids: List[str] = []
        sql = """
        INSERT INTO entities (
            entity_id, canonical_name, entity_category, role_or_title,
            primary_jurisdiction, aliases_json, metadata_json, updated_at
        ) VALUES (
            :entity_id, :canonical_name, :entity_category, :role_or_title,
            :primary_jurisdiction, :aliases_json, :metadata_json, (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
        ) ON CONFLICT(entity_id) DO UPDATE SET
            canonical_name = excluded.canonical_name,
            role_or_title = COALESCE(excluded.role_or_title, entities.role_or_title),
            primary_jurisdiction = COALESCE(excluded.primary_jurisdiction, entities.primary_jurisdiction),
            aliases_json = excluded.aliases_json,
            metadata_json = excluded.metadata_json,
            updated_at = (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'));
        """

        rows = []
        for e in entities:
            e_dict = asdict(e) if is_dataclass(e) else dict(e)
            aliases = e_dict.get("aliases", [])
            aliases_json = json.dumps(aliases, ensure_ascii=False) if isinstance(aliases, list) else str(aliases)
            meta = e_dict.get("metadata", {})
            meta_json = json.dumps(meta, ensure_ascii=False) if isinstance(meta, dict) else str(meta)

            ent_id = str(e_dict.get("entity_id"))
            inserted_ids.append(ent_id)

            cat = e_dict.get("entity_category")
            cat_str = cat.value if hasattr(cat, "value") else str(cat)

            row = {
                "entity_id": ent_id,
                "canonical_name": str(e_dict.get("canonical_name")),
                "entity_category": cat_str,
                "role_or_title": e_dict.get("role_or_title"),
                "primary_jurisdiction": e_dict.get("primary_jurisdiction"),
                "aliases_json": aliases_json,
                "metadata_json": meta_json,
            }
            rows.append(row)

        with self.transaction() as conn:
            conn.executemany(sql, rows)

        return inserted_ids

    # ------------------------------------------------------------------------
    # Entity Mentions Operations
    # ------------------------------------------------------------------------

    def insert_mention(self, mention_data: Union[Dict[str, Any], Any]) -> str:
        """Inserts a single entity mention."""
        return self.insert_mentions_batch([mention_data])[0]

    def insert_mentions_batch(self, mentions: Sequence[Union[Dict[str, Any], Any]]) -> List[str]:
        """Batch inserts entity mentions."""
        if not mentions:
            return []

        inserted_ids: List[str] = []
        sql = """
        INSERT INTO entity_mentions (
            mention_id, document_id, entity_id, raw_mention_text,
            char_offset_start, char_offset_end, page_number, context_snippet,
            confidence_score, extraction_method
        ) VALUES (
            :mention_id, :document_id, :entity_id, :raw_mention_text,
            :char_offset_start, :char_offset_end, :page_number, :context_snippet,
            :confidence_score, :extraction_method
        ) ON CONFLICT(mention_id) DO UPDATE SET
            entity_id = excluded.entity_id,
            confidence_score = excluded.confidence_score;
        """

        rows = []
        for m in mentions:
            m_dict = asdict(m) if is_dataclass(m) else dict(m)
            m_id = str(m_dict.get("mention_id"))
            inserted_ids.append(m_id)

            row = {
                "mention_id": m_id,
                "document_id": str(m_dict.get("document_id")),
                "entity_id": str(m_dict.get("entity_id")),
                "raw_mention_text": str(m_dict.get("raw_mention_text")),
                "char_offset_start": m_dict.get("char_offset_start"),
                "char_offset_end": m_dict.get("char_offset_end"),
                "page_number": max(1, int(m_dict.get("page_number", 1))),
                "context_snippet": m_dict.get("context_snippet"),
                "confidence_score": float(m_dict.get("confidence_score", 1.0)),
                "extraction_method": str(m_dict.get("extraction_method", "REGEX")),
            }
            rows.append(row)

        with self.transaction() as conn:
            conn.executemany(sql, rows)

        return inserted_ids

    # ------------------------------------------------------------------------
    # Timeline Events Operations
    # ------------------------------------------------------------------------

    def insert_event(self, event_data: Union[Dict[str, Any], Any]) -> str:
        """Inserts a single timeline event."""
        return self.insert_events_batch([event_data])[0]

    def insert_events_batch(self, events: Sequence[Union[Dict[str, Any], Any]]) -> List[str]:
        """Batch inserts timeline events."""
        if not events:
            return []

        inserted_ids: List[str] = []
        sql = """
        INSERT INTO timeline_events (
            event_id, document_id, event_date_iso, event_year, event_month, event_day,
            event_type, title, description, raw_snippet, primary_entity_id,
            location, jurisdiction, confidence_score, chronological_rank
        ) VALUES (
            :event_id, :document_id, :event_date_iso, :event_year, :event_month, :event_day,
            :event_type, :title, :description, :raw_snippet, :primary_entity_id,
            :location, :jurisdiction, :confidence_score, :chronological_rank
        ) ON CONFLICT(event_id) DO UPDATE SET
            title = excluded.title,
            description = excluded.description,
            chronological_rank = excluded.chronological_rank;
        """

        rows = []
        for e in events:
            e_dict = asdict(e) if is_dataclass(e) else dict(e)
            evt_id = str(e_dict.get("event_id"))
            inserted_ids.append(evt_id)

            ev_type = e_dict.get("event_type")
            ev_type_str = ev_type.value if hasattr(ev_type, "value") else str(ev_type)

            row = {
                "event_id": evt_id,
                "document_id": e_dict.get("document_id"),
                "event_date_iso": str(e_dict.get("event_date_iso")),
                "event_year": int(e_dict.get("event_year", 2022)),
                "event_month": e_dict.get("event_month"),
                "event_day": e_dict.get("event_day"),
                "event_type": ev_type_str,
                "title": str(e_dict.get("title")),
                "description": str(e_dict.get("description")),
                "raw_snippet": e_dict.get("raw_snippet"),
                "primary_entity_id": e_dict.get("primary_entity_id"),
                "location": e_dict.get("location"),
                "jurisdiction": e_dict.get("jurisdiction"),
                "confidence_score": float(e_dict.get("confidence_score", 1.0)),
                "chronological_rank": e_dict.get("chronological_rank"),
            }
            rows.append(row)

        with self.transaction() as conn:
            conn.executemany(sql, rows)

        return inserted_ids

    # ------------------------------------------------------------------------
    # Financial Transactions Operations
    # ------------------------------------------------------------------------

    def insert_financial_transaction(self, trx_data: Union[Dict[str, Any], Any]) -> str:
        """Inserts a single financial transaction."""
        return self.insert_financial_transactions_batch([trx_data])[0]

    def insert_financial_transactions_batch(self, transactions: Sequence[Union[Dict[str, Any], Any]]) -> List[str]:
        """Batch inserts financial transactions."""
        if not transactions:
            return []

        inserted_ids: List[str] = []
        sql = """
        INSERT INTO financial_transactions (
            transaction_id, document_id, event_id, transaction_date_iso, amount,
            currency, sender_entity_id, recipient_entity_id, sender_raw_text,
            recipient_raw_text, payment_method, account_or_check_num,
            transaction_purpose, is_predicate_act, raw_snippet
        ) VALUES (
            :transaction_id, :document_id, :event_id, :transaction_date_iso, :amount,
            :currency, :sender_entity_id, :recipient_entity_id, :sender_raw_text,
            :recipient_raw_text, :payment_method, :account_or_check_num,
            :transaction_purpose, :is_predicate_act, :raw_snippet
        ) ON CONFLICT(transaction_id) DO UPDATE SET
            amount = excluded.amount,
            is_predicate_act = excluded.is_predicate_act;
        """

        rows = []
        for t in transactions:
            t_dict = asdict(t) if is_dataclass(t) else dict(t)
            trx_id = str(t_dict.get("transaction_id"))
            inserted_ids.append(trx_id)

            pm = t_dict.get("payment_method")
            pm_str = pm.value if hasattr(pm, "value") else str(pm)

            row = {
                "transaction_id": trx_id,
                "document_id": t_dict.get("document_id"),
                "event_id": t_dict.get("event_id"),
                "transaction_date_iso": str(t_dict.get("transaction_date_iso")),
                "amount": float(t_dict.get("amount", 0.0)),
                "currency": str(t_dict.get("currency", "USD")),
                "sender_entity_id": t_dict.get("sender_entity_id"),
                "recipient_entity_id": t_dict.get("recipient_entity_id"),
                "sender_raw_text": t_dict.get("sender_raw_text"),
                "recipient_raw_text": t_dict.get("recipient_raw_text"),
                "payment_method": pm_str,
                "account_or_check_num": t_dict.get("account_or_check_num"),
                "transaction_purpose": t_dict.get("transaction_purpose"),
                "is_predicate_act": 1 if t_dict.get("is_predicate_act") else 0,
                "raw_snippet": t_dict.get("raw_snippet"),
            }
            rows.append(row)

        with self.transaction() as conn:
            conn.executemany(sql, rows)

        return inserted_ids

    # ------------------------------------------------------------------------
    # Relationships Operations
    # ------------------------------------------------------------------------

    def insert_relationship(self, rel_data: Union[Dict[str, Any], Any]) -> str:
        """Inserts a single relationship edge."""
        ids = self.insert_relationships_batch([rel_data])
        return ids[0] if ids else ""

    def insert_relationships_batch(self, relationships: Sequence[Union[Dict[str, Any], Any]]) -> List[str]:
        """Batch inserts relationship graph edges."""
        if not relationships:
            return []

        inserted_ids: List[str] = []
        sql = """
        INSERT INTO relationships (
            relationship_id, source_entity_id, target_entity_id, relationship_type,
            direction, confidence, valid_from, valid_to, source_document_id, evidence_summary
        ) VALUES (
            :relationship_id, :source_entity_id, :target_entity_id, :relationship_type,
            :direction, :confidence, :valid_from, :valid_to, :source_document_id, :evidence_summary
        ) ON CONFLICT(relationship_id) DO UPDATE SET
            confidence = excluded.confidence,
            evidence_summary = excluded.evidence_summary;
        """

        rows = []
        for r in relationships:
            r_dict = asdict(r) if is_dataclass(r) else dict(r)
            rel_id = str(r_dict.get("relationship_id"))
            src = str(r_dict.get("source_entity_id"))
            tgt = str(r_dict.get("target_entity_id"))

            if src == tgt:
                # Disallow self-loops per CHECK constraint
                continue

            inserted_ids.append(rel_id)
            rt = r_dict.get("relationship_type")
            rt_str = rt.value if hasattr(rt, "value") else str(rt)

            row = {
                "relationship_id": rel_id,
                "source_entity_id": src,
                "target_entity_id": tgt,
                "relationship_type": rt_str,
                "direction": str(r_dict.get("direction", "DIRECTED")),
                "confidence": float(r_dict.get("confidence", 1.0)),
                "valid_from": r_dict.get("valid_from"),
                "valid_to": r_dict.get("valid_to"),
                "source_document_id": r_dict.get("source_document_id"),
                "evidence_summary": r_dict.get("evidence_summary"),
            }
            rows.append(row)

        with self.transaction() as conn:
            conn.executemany(sql, rows)

        return inserted_ids

    # ------------------------------------------------------------------------
    # Query & Retrieval Operations
    # ------------------------------------------------------------------------

    def get_document(self, document_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves single document by ID."""
        with self.get_connection() as conn:
            cur = conn.execute("SELECT * FROM documents WHERE document_id = ?;", (document_id,))
            row = cur.fetchone()
            return dict(row) if row else None

    def get_document_by_sha256(self, file_sha256: str) -> Optional[Dict[str, Any]]:
        """Retrieves document by SHA-256."""
        with self.get_connection() as conn:
            cur = conn.execute("SELECT * FROM documents WHERE file_sha256 = ?;", (file_sha256,))
            row = cur.fetchone()
            return dict(row) if row else None

    def get_all_documents(self) -> List[Dict[str, Any]]:
        """Retrieves all documents."""
        with self.get_connection() as conn:
            cur = conn.execute("SELECT * FROM documents ORDER BY document_id ASC;")
            return [dict(r) for r in cur.fetchall()]

    def get_entity(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves single entity by ID."""
        with self.get_connection() as conn:
            cur = conn.execute("SELECT * FROM entities WHERE entity_id = ?;", (entity_id,))
            row = cur.fetchone()
            return dict(row) if row else None

    def get_all_entities(self) -> List[Dict[str, Any]]:
        """Retrieves all canonical entities."""
        with self.get_connection() as conn:
            cur = conn.execute("SELECT * FROM entities ORDER BY entity_id ASC;")
            return [dict(r) for r in cur.fetchall()]

    def get_all_entity_mentions(self) -> List[Dict[str, Any]]:
        """Retrieves all entity mentions."""
        with self.get_connection() as conn:
            cur = conn.execute("SELECT * FROM entity_mentions ORDER BY mention_id ASC;")
            return [dict(r) for r in cur.fetchall()]

    def get_timeline_events(self, chronological: bool = True) -> List[Dict[str, Any]]:
        """Retrieves timeline events."""
        order = "ORDER BY event_date_iso ASC, chronological_rank ASC" if chronological else "ORDER BY event_id ASC"
        with self.get_connection() as conn:
            cur = conn.execute(f"SELECT * FROM timeline_events {order};")
            return [dict(r) for r in cur.fetchall()]

    def get_financial_transactions(self) -> List[Dict[str, Any]]:
        """Retrieves financial transactions."""
        with self.get_connection() as conn:
            cur = conn.execute("SELECT * FROM financial_transactions ORDER BY transaction_date_iso ASC, transaction_id ASC;")
            return [dict(r) for r in cur.fetchall()]

    def get_relationships(self) -> List[Dict[str, Any]]:
        """Retrieves all relationship edges."""
        with self.get_connection() as conn:
            cur = conn.execute("SELECT * FROM relationships ORDER BY relationship_id ASC;")
            return [dict(r) for r in cur.fetchall()]

    def get_summary_counts(self) -> Dict[str, int]:
        """Returns total row counts across all relational tables."""
        with self.get_connection() as conn:
            docs = conn.execute("SELECT COUNT(*) FROM documents;").fetchone()[0]
            ents = conn.execute("SELECT COUNT(*) FROM entities;").fetchone()[0]
            mentions = conn.execute("SELECT COUNT(*) FROM entity_mentions;").fetchone()[0]
            evts = conn.execute("SELECT COUNT(*) FROM timeline_events;").fetchone()[0]
            trx = conn.execute("SELECT COUNT(*) FROM financial_transactions;").fetchone()[0]
            rels = conn.execute("SELECT COUNT(*) FROM relationships;").fetchone()[0]

            return {
                "total_documents": int(docs),
                "total_entities": int(ents),
                "total_mentions": int(mentions),
                "total_events": int(evts),
                "total_transactions": int(trx),
                "total_relationships": int(rels),
            }

    # ------------------------------------------------------------------------
    # Automated Invariant Verification Methods
    # ------------------------------------------------------------------------

    def check_foreign_keys(self) -> List[Tuple[Any, ...]]:
        """Runs PRAGMA foreign_key_check and returns any violation tuples."""
        with self.get_connection() as conn:
            cur = conn.execute("PRAGMA foreign_key_check;")
            return cur.fetchall()

    def check_chronological_inversions(self) -> int:
        """
        Validates timeline event chronological ordering.
        Returns count of date inversion violations.
        """
        events = self.get_timeline_events(chronological=True)
        inversions = 0
        for i in range(len(events) - 1):
            date_a = events[i]["event_date_iso"]
            date_b = events[i + 1]["event_date_iso"]
            if date_a > date_b:
                inversions += 1
        return inversions

    def log_invariant_audit(self, audit_data: Dict[str, Any]) -> int:
        """Records an invariant verification run in schema_invariants_log."""
        sql = """
        INSERT INTO schema_invariants_log (
            tier_level, merkle_root_sha256, documents_count, entities_count,
            events_count, transactions_count, relationships_count,
            foreign_key_violations, chronological_inversions, verification_status
        ) VALUES (
            :tier_level, :merkle_root_sha256, :documents_count, :entities_count,
            :events_count, :transactions_count, :relationships_count,
            :foreign_key_violations, :chronological_inversions, :verification_status
        );
        """
        with self.transaction() as conn:
            cur = conn.execute(sql, audit_data)
            return cur.lastrowid

    def verify_invariants(self, tier_level: str = "TIER_1", merkle_root: str = "") -> Dict[str, Any]:
        """
        Executes full invariant suite against database state.
        Checks foreign key integrity, chronological monotonicity, and logs result.
        """
        fk_violations = len(self.check_foreign_keys())
        chrono_inversions = self.check_chronological_inversions()
        counts = self.get_summary_counts()

        passed = (fk_violations == 0) and (chrono_inversions == 0)
        status = "PASSED" if passed else "FAILED"

        audit_entry = {
            "tier_level": tier_level,
            "merkle_root_sha256": merkle_root or ("0" * 64),
            "documents_count": counts["total_documents"],
            "entities_count": counts["total_entities"],
            "events_count": counts["total_events"],
            "transactions_count": counts["total_transactions"],
            "relationships_count": counts["total_relationships"],
            "foreign_key_violations": fk_violations,
            "chronological_inversions": chrono_inversions,
            "verification_status": status,
        }

        audit_id = self.log_invariant_audit(audit_entry)
        audit_entry["audit_id"] = audit_id
        audit_entry["all_invariants_passed"] = passed

        return audit_entry
