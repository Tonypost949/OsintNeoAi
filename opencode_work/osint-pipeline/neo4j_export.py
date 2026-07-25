"""
neo4j_export.py — Export entities and relationships as timestamped JSONL batches.
For Neo4j LOAD CSV / batch import.
"""
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import config


def _timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def _write_jsonl(records: list[dict], path: Path):
    with open(path, "w", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, default=str) + "\n")


def export_entities(entities: list[dict], batch_id: str = None) -> Path:
    """Export entities as JSONL for Neo4j import."""
    if not entities:
        return config.EXPORT_DIR / "empty"

    ts = _timestamp()
    batch_id = batch_id or f"entities_{ts}"
    out_path = config.EXPORT_DIR / f"{batch_id}.jsonl"

    neo4j_records = []
    for e in entities:
        record = {
            "entity_id": e.get("entity_id", ""),
            "name": e.get("entity_name", e.get("name", "")),
            "type": e.get("entity_type", e.get("type", "UNKNOWN")),
            "number": e.get("entity_number", ""),
            "status": e.get("status", "UNKNOWN"),
            "state": e.get("state", ""),
            "filing_date": e.get("filing_date", ""),
            "registered_agent": e.get("registered_agent", ""),
            "agent_address": e.get("agent_address", ""),
            "source": e.get("source", "unknown"),
            "confidence": e.get("confidence_score", 0.0),
            "imported_at": ts,
        }
        neo4j_records.append(record)

    _write_jsonl(neo4j_records, out_path)
    return out_path


def export_relationships(relationships: list[dict], batch_id: str = None) -> Path:
    """Export relationships as JSONL for Neo4j import."""
    if not relationships:
        return config.EXPORT_DIR / "empty"

    ts = _timestamp()
    batch_id = batch_id or f"rels_{ts}"
    out_path = config.EXPORT_DIR / f"{batch_id}.jsonl"

    neo4j_records = []
    for r in relationships:
        record = {
            "source_id": r.get("source_entity_id", ""),
            "target_id": r.get("target_entity_id", ""),
            "type": r.get("relationship_type", "RELATED"),
            "weight": r.get("weight", 1.0),
            "evidence": json.dumps(r.get("evidence", {}), default=str),
            "imported_at": ts,
        }
        neo4j_records.append(record)

    _write_jsonl(neo4j_records, out_path)
    return out_path


def export_attorneys(attorneys: list[dict], batch_id: str = None) -> Path:
    """Export attorneys as JSONL for Neo4j import."""
    if not attorneys:
        return config.EXPORT_DIR / "empty"

    ts = _timestamp()
    batch_id = batch_id or f"attorneys_{ts}"
    out_path = config.EXPORT_DIR / f"{batch_id}.jsonl"

    neo4j_records = []
    for a in attorneys:
        record = {
            "attorney_id": a.get("attorney_id", ""),
            "name": a.get("name", ""),
            "bar_number": a.get("bar_number", ""),
            "firm": a.get("firm_name", ""),
            "entity_count": a.get("entity_count", 0),
            "imported_at": ts,
        }
        neo4j_records.append(record)

    _write_jsonl(neo4j_records, out_path)
    return out_path


def generate_cypher_load(batch_path: Path, label: str) -> str:
    """Generate Cypher LOAD CSV statement for a JSONL batch."""
    return f"""
LOAD CSV WITH HEADERS FROM 'file:///{batch_path.name}' AS row
CALL {{
    WITH row
    CREATE (n:{label} {{
        id: row.entity_id,
        name: row.name,
        type: row.type,
        number: row.number,
        status: row.status,
        state: row.state,
        source: row.source,
        confidence: toFloat(row.confidence),
        imported_at: datetime(row.imported_at)
    }})
}} IN TRANSACTIONS OF 1000 ROWS;
"""


def get_export_stats() -> dict:
    """Get stats on exported batches."""
    files = list(config.EXPORT_DIR.glob("*.jsonl"))
    total_records = 0
    for f in files:
        with open(f, "r") as fh:
            total_records += sum(1 for _ in fh)

    return {
        "batch_files": len(files),
        "total_records": total_records,
        "export_dir": str(config.EXPORT_DIR),
    }
