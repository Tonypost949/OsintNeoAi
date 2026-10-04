import sqlite3
import json
from datetime import datetime
import os
import streamlit as st

DB_PATH = "data/osint_master.db"

def get_connection():
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    c = conn.cursor()
    c.executescript("""
        CREATE TABLE IF NOT EXISTS entities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entity_id TEXT UNIQUE,
            type TEXT,
            label TEXT,
            category TEXT,
            geo_location TEXT,
            risk_level TEXT DEFAULT 'Unknown',
            source TEXT,
            notes TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS relationships (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            relation_id TEXT UNIQUE,
            source_entity TEXT,
            target_entity TEXT,
            relationship_type TEXT,
            confidence TEXT,
            source TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id TEXT UNIQUE,
            timestamp TEXT,
            event_type TEXT,
            location TEXT,
            entities_involved TEXT,
            source TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS scan_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            target TEXT,
            scan_type TEXT,
            result_json TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS file_scan_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_path TEXT,
            file_type TEXT,
            file_size INTEGER,
            metadata_json TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()

    existing = c.execute("SELECT COUNT(*) FROM entities").fetchone()[0]
    if existing == 0:
        seed_entities = [
            ("ENT-001", "Person", "Subject_A", "Individual", "32.2570, -110.9230", "Unknown", "Public_Record", "Observed association"),
            ("ENT-002", "Location", "Residence_A", "Address", "32.2570, -110.9230", "Unknown", "Public_Record", "Residential building"),
            ("ENT-007", "Person", "Donnetta L. Wilburn", "Subject", "Santa Ana, CA", "High", "TruthFinder", "Multiple criminal records (1998-2023). High risk due to recent citations."),
            ("ENT-008", "Location", "501 E 5th St", "Primary Residence", "Santa Ana, CA 92701", "Medium", "TruthFinder", "Current address for Donnetta Wilburn. Proximity to sex offenders noted."),
            ("ENT-009", "Person", "Martin Raymond Beebe", "Subject", "Huntington Beach, CA", "Medium", "TruthFinder", "History of Bankruptcy (2011) and significant Federal Tax Liens."),
            ("ENT-010", "Location", "8211 Ridgefield Dr", "Primary Residence", "Huntington Beach, CA 92646", "Low", "TruthFinder", "Current address for Martin Beebe. Residential classification."),
            ("ENT-011", "Location", "205 Telegraph St", "Historical Loc", "Tennessee Ridge, TN 37178", "Unknown", "TruthFinder", "Shared location between Wilburn and Amber Beard."),
        ]
        c.executemany("INSERT OR IGNORE INTO entities (entity_id, type, label, category, geo_location, risk_level, source, notes) VALUES (?,?,?,?,?,?,?,?)", seed_entities)

        seed_rels = [
            ("REL-001", "ENT-001", "ENT-002", "Located_At", "Medium", "Public_Record"),
            ("REL-006", "ENT-007", "ENT-008", "Resides_At", "High", "TruthFinder"),
            ("REL-007", "ENT-007", "Alano Club of Santa Ana", "Employment", "High", "Employment History"),
            ("REL-008", "ENT-009", "ENT-010", "Resides_At", "High", "TruthFinder"),
            ("REL-009", "ENT-009", "4f Generate LLC", "Business Owner", "High", "Corporate Filings"),
            ("REL-010", "ENT-009", "Feel Anthropy Foundation", "Officer", "High", "Corporate Filings"),
            ("REL-011", "ENT-007", "ENT-011", "Shared_Address", "Medium", "Location History"),
        ]
        c.executemany("INSERT OR IGNORE INTO relationships (relation_id, source_entity, target_entity, relationship_type, confidence, source) VALUES (?,?,?,?,?,?)", seed_rels)

        seed_events = [
            ("EV-001", "02:28:00", "Signal_Loss", "Tucson_Area", "ENT-005", "Telemetry_Log"),
            ("EV-004", "2023-11-13", "Criminal Offense", "Orange, CA", "ENT-007", "Superior Court Record"),
            ("EV-005", "2020-12-18", "Criminal Offense", "Orange, CA", "ENT-007", "Superior Court Record"),
            ("EV-006", "2011-06-29", "Bankruptcy Discharge", "California", "ENT-009", "Court Case 1138021"),
            ("EV-007", "2016-03-31", "Federal Tax Lien", "Orange, CA", "ENT-009", "Recording #156608"),
            ("EV-008", "2010-05-10", "State Tax Lien", "Hall, GA", "Adrian Morfin", "Recording #14026"),
        ]
        c.executemany("INSERT OR IGNORE INTO events (event_id, timestamp, event_type, location, entities_involved, source) VALUES (?,?,?,?,?,?)", seed_events)

        conn.commit()
    conn.close()

def _clear_read_caches():
    """Call after any write so all cached reads reflect new data immediately."""
    get_stats.clear()
    get_all_entities.clear()
    get_all_events.clear()
    get_all_relationships.clear()
    get_all_scans.clear()
    get_all_file_scans.clear()

def add_entity(entity_id, etype, label, category, geo, risk, source, notes):
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO entities (entity_id, type, label, category, geo_location, risk_level, source, notes) VALUES (?,?,?,?,?,?,?,?)",
              (entity_id, etype, label, category, geo, risk, source, notes))
    conn.commit()
    conn.close()
    _clear_read_caches()

def add_relationship(rel_id, src, tgt, rel_type, confidence, source):
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO relationships (relation_id, source_entity, target_entity, relationship_type, confidence, source) VALUES (?,?,?,?,?,?)",
              (rel_id, src, tgt, rel_type, confidence, source))
    conn.commit()
    conn.close()
    _clear_read_caches()

def add_event(event_id, timestamp, event_type, location, entities, source):
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO events (event_id, timestamp, event_type, location, entities_involved, source) VALUES (?,?,?,?,?,?)",
              (event_id, timestamp, event_type, location, entities, source))
    conn.commit()
    conn.close()
    _clear_read_caches()

def save_scan_result(target, scan_type, result_dict):
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO scan_results (target, scan_type, result_json) VALUES (?,?,?)",
              (target, scan_type, json.dumps(result_dict)))
    conn.commit()
    conn.close()
    _clear_read_caches()

def save_file_scan(file_path, file_type, file_size, metadata):
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO file_scan_results (file_path, file_type, file_size, metadata_json) VALUES (?,?,?,?)",
              (file_path, file_type, file_size, json.dumps(metadata)))
    conn.commit()
    conn.close()
    _clear_read_caches()

@st.cache_data(ttl=60, show_spinner=False)
def get_all_entities():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM entities ORDER BY created_at DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]

@st.cache_data(ttl=60, show_spinner=False)
def get_all_relationships():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM relationships ORDER BY created_at DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]

@st.cache_data(ttl=60, show_spinner=False)
def get_all_events():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM events ORDER BY timestamp DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]

@st.cache_data(ttl=60, show_spinner=False)
def get_all_scans():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM scan_results ORDER BY created_at DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]

@st.cache_data(ttl=60, show_spinner=False)
def get_all_file_scans():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM file_scan_results ORDER BY created_at DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]

@st.cache_data(ttl=60, show_spinner=False)
def get_stats():
    conn = get_connection()
    cur = conn.cursor()
    stats = {
        "entities":      cur.execute("SELECT COUNT(*) FROM entities").fetchone()[0],
        "relationships": cur.execute("SELECT COUNT(*) FROM relationships").fetchone()[0],
        "events":        cur.execute("SELECT COUNT(*) FROM events").fetchone()[0],
        "scans":         cur.execute("SELECT COUNT(*) FROM scan_results").fetchone()[0],
        "file_scans":    cur.execute("SELECT COUNT(*) FROM file_scan_results").fetchone()[0],
        "high_risk":     cur.execute("SELECT COUNT(*) FROM file_scan_results WHERE risk_flag='High'").fetchone()[0],
    }
    conn.close()
    return stats
