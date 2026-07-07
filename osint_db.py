#!/usr/bin/env python3
"""
OSINT Database Manager
======================
Handles all SQLite database operations for persisting OSINT data, including
people, connections, and enrichment results.
"""

import sqlite3
import json
from typing import List, Dict, Optional


class DatabaseManager:
    """Manages the SQLite database for OSINT data."""

    def __init__(self, db_path: str = "osint_data.db"):
        self.db_path = db_path
        self.conn: Optional[sqlite3.Connection] = None
        self._connect()
        self._create_tables()

    def _connect(self):
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
            print(f"Connected to SQLite DB: {self.db_path}")
        except sqlite3.Error as e:
            print(f"SQLite connection error: {e}")

    def _create_tables(self):
        if not self.conn:
            return
        with self.conn:
            self.conn.execute("""
            CREATE TABLE IF NOT EXISTS people (
                id TEXT PRIMARY KEY, name TEXT NOT NULL, phone TEXT, email TEXT,
                business TEXT, business_type TEXT, title TEXT, location TEXT,
                city TEXT, state TEXT, zip_code TEXT, ssn TEXT, dob TEXT,
                linkedin TEXT, twitter TEXT, instagram TEXT, website TEXT,
                notes TEXT, data_sources TEXT, confidence_score REAL, last_updated TEXT
            );
            """)
            self.conn.execute("""
            CREATE TABLE IF NOT EXISTS connections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                person_a_id TEXT, person_b_id TEXT, connection_type TEXT,
                strength REAL, shared_attributes TEXT, evidence TEXT, confidence REAL,
                FOREIGN KEY (person_a_id) REFERENCES people (id),
                FOREIGN KEY (person_b_id) REFERENCES people (id)
            );
            """)
            self.conn.execute("""
            CREATE TABLE IF NOT EXISTS search_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                person_id TEXT NOT NULL,
                results_json TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (person_id) REFERENCES people (id)
            );
            """)
            self.conn.execute("""
            CREATE TABLE IF NOT EXISTS enrichment_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                batch_id TEXT,
                entity_name TEXT,
                source TEXT,
                agent_name TEXT,
                agent_role TEXT,
                details TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );
            """)
        print("Database tables verified/created.")

    def save_people(self, people: List) -> int:
        if not self.conn or not people:
            return 0
        people_data = []
        for p in people:
            d = {}
            for field in ['id', 'name', 'phone', 'email', 'business', 'business_type',
                          'title', 'location', 'city', 'state', 'zip_code', 'ssn', 'dob',
                          'linkedin', 'twitter', 'instagram', 'website', 'notes',
                          'data_sources', 'confidence_score', 'last_updated']:
                val = getattr(p, field, None)
                if field == 'data_sources' and isinstance(val, list):
                    val = json.dumps(val)
                d[field] = val
            people_data.append(d)

        with self.conn:
            self.conn.executemany("""
            INSERT OR REPLACE INTO people (
                id, name, phone, email, business, business_type, title, location,
                city, state, zip_code, ssn, dob, linkedin, twitter, instagram,
                website, notes, data_sources, confidence_score, last_updated
            ) VALUES (
                :id, :name, :phone, :email, :business, :business_type, :title, :location,
                :city, :state, :zip_code, :ssn, :dob, :linkedin, :twitter, :instagram,
                :website, :notes, :data_sources, :confidence_score, :last_updated
            )
            """, people_data)
        return len(people_data)

    def save_connections(self, connections: List) -> int:
        if not self.conn or not connections:
            return 0
        conn_data = []
        for c in connections:
            d = {}
            for field in ['person_a_id', 'person_b_id', 'connection_type', 'strength',
                          'shared_attributes', 'evidence', 'confidence']:
                val = getattr(c, field, None)
                if field == 'shared_attributes' and isinstance(val, list):
                    val = json.dumps(val)
                d[field] = val
            conn_data.append(d)

        with self.conn:
            self.conn.executemany("""
            INSERT INTO connections (
                person_a_id, person_b_id, connection_type, strength,
                shared_attributes, evidence, confidence
            ) VALUES (
                :person_a_id, :person_b_id, :connection_type, :strength,
                :shared_attributes, :evidence, :confidence
            )
            """, conn_data)
        return len(conn_data)

    def save_search_results(self, search_results: Dict) -> int:
        if not self.conn or not search_results:
            return 0
        results_data = [
            {'person_id': pid, 'results_json': json.dumps(res)}
            for pid, res in search_results.items()
        ]
        with self.conn:
            self.conn.executemany("""
            INSERT INTO search_results (person_id, results_json) VALUES (:person_id, :results_json)
            """, results_data)
        return len(results_data)

    def save_enrichment_run(self, batch_id: str, entity_name: str, source: str,
                            agent_name: str, agent_role: str = "REGISTERED_AGENT",
                            details: str = ""):
        if not self.conn:
            return
        with self.conn:
            self.conn.execute("""
            INSERT INTO enrichment_runs (batch_id, entity_name, source, agent_name, agent_role, details)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (batch_id, entity_name, source, agent_name, agent_role, details))

    def get_people(self) -> List[sqlite3.Row]:
        if not self.conn:
            return []
        with self.conn:
            return self.conn.execute("SELECT * FROM people ORDER BY name").fetchall()

    def get_connections(self) -> List[sqlite3.Row]:
        if not self.conn:
            return []
        with self.conn:
            return self.conn.execute("SELECT * FROM connections").fetchall()

    def get_enrichment_runs(self) -> List[sqlite3.Row]:
        if not self.conn:
            return []
        with self.conn:
            return self.conn.execute("""
                SELECT * FROM enrichment_runs ORDER BY created_at DESC
            """).fetchall()

    def close(self):
        if self.conn:
            self.conn.close()
