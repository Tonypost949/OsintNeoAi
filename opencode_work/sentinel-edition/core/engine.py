"""
Sentinel OSINT Engine - Independent Investigation Platform
===========================================================
A self-contained OSINT analysis engine built from scratch.
No external API dependencies required for core functionality.
Supports: Entity resolution, network mapping, timeline analysis,
          document ingestion, and multi-source correlation.
"""

import json
import hashlib
import os
import re
import sqlite3
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Optional


class Entity:
    """Represents any OSINT entity - person, org, address, phone, email, domain, etc."""

    TYPES = [
        "person", "organization", "address", "phone", "email",
        "domain", "ip_address", "vehicle", "property", "document",
        "financial_account", "social_profile", "alias", "url",
        "zip_code", "date", "currency", "hex_address"
    ]

    def __init__(self, entity_type: str, value: str, source: str = "", confidence: float = 0.5, metadata: dict = None):
        if entity_type not in self.TYPES:
            raise ValueError(f"Invalid entity type: {entity_type}. Must be one of {self.TYPES}")
        self.entity_type = entity_type
        self.value = value.strip()
        self.source = source
        self.confidence = min(max(confidence, 0.0), 1.0)
        self.metadata = metadata or {}
        self.id = self._generate_id()
        self.created_at = datetime.utcnow().isoformat()
        self.tags = []

    def _generate_id(self) -> str:
        raw = f"{self.entity_type}:{self.value.lower()}"
        return hashlib.sha256(raw.encode()).hexdigest()[:16]

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "type": self.entity_type,
            "value": self.value,
            "source": self.source,
            "confidence": self.confidence,
            "metadata": self.metadata,
            "created_at": self.created_at,
            "tags": self.tags,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Entity":
        e = cls(data["type"], data["value"], data.get("source", ""), data.get("confidence", 0.5), data.get("metadata", {}))
        e.id = data.get("id", e.id)
        e.created_at = data.get("created_at", e.created_at)
        e.tags = data.get("tags", [])
        return e

    def __repr__(self):
        return f"Entity({self.entity_type}, {self.value!r}, conf={self.confidence})"


class Relationship:
    """Links two entities with a typed, weighted edge."""

    def __init__(self, source_id: str, target_id: str, rel_type: str, weight: float = 1.0, metadata: dict = None):
        self.source_id = source_id
        self.target_id = target_id
        self.rel_type = rel_type
        self.weight = weight
        self.metadata = metadata or {}
        self.created_at = datetime.utcnow().isoformat()
        self.id = hashlib.sha256(f"{source_id}:{target_id}:{rel_type}".encode()).hexdigest()[:16]

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "source": self.source_id,
            "target": self.target_id,
            "type": self.rel_type,
            "weight": self.weight,
            "metadata": self.metadata,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Relationship":
        r = cls(data["source"], data["target"], data["type"], data.get("weight", 1.0), data.get("metadata", {}))
        r.id = data.get("id", r.id)
        r.created_at = data.get("created_at", r.created_at)
        return r


class InvestigationGraph:
    """
    In-memory graph of entities and relationships with SQLite persistence.
    Each Investigation gets its own graph that can be saved/loaded independently.
    """

    def __init__(self, db_path: str = None):
        self.entities: dict[str, Entity] = {}
        self.relationships: dict[str, Relationship] = {}
        self.db_path = db_path
        if db_path:
            self._init_db()

    def _init_db(self):
        os.makedirs(os.path.dirname(self.db_path) or ".", exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS entities (
                id TEXT PRIMARY KEY,
                type TEXT NOT NULL,
                value TEXT NOT NULL,
                source TEXT,
                confidence REAL,
                metadata TEXT,
                created_at TEXT,
                tags TEXT
            );
            CREATE TABLE IF NOT EXISTS relationships (
                id TEXT PRIMARY KEY,
                source_id TEXT NOT NULL,
                target_id TEXT NOT NULL,
                rel_type TEXT NOT NULL,
                weight REAL,
                metadata TEXT,
                created_at TEXT,
                FOREIGN KEY (source_id) REFERENCES entities(id),
                FOREIGN KEY (target_id) REFERENCES entities(id)
            );
            CREATE TABLE IF NOT EXISTS documents (
                id TEXT PRIMARY KEY,
                filename TEXT,
                content_hash TEXT,
                extracted_entities TEXT,
                ingested_at TEXT,
                metadata TEXT
            );
            CREATE INDEX IF NOT EXISTS idx_entities_type ON entities(type);
            CREATE INDEX IF NOT EXISTS idx_entities_value ON entities(value);
            CREATE INDEX IF NOT EXISTS idx_rels_source ON relationships(source_id);
            CREATE INDEX IF NOT EXISTS idx_rels_target ON relationships(target_id);
        """)
        conn.close()

    def add_entity(self, entity: Entity) -> str:
        self.entities[entity.id] = entity
        if self.db_path:
            conn = sqlite3.connect(self.db_path)
            conn.execute(
                "INSERT OR REPLACE INTO entities VALUES (?,?,?,?,?,?,?,?)",
                (entity.id, entity.entity_type, entity.value, entity.source,
                 entity.confidence, json.dumps(entity.metadata), entity.created_at, json.dumps(entity.tags))
            )
            conn.commit()
            conn.close()
        return entity.id

    def add_relationship(self, rel: Relationship) -> str:
        self.relationships[rel.id] = rel
        if self.db_path:
            conn = sqlite3.connect(self.db_path)
            conn.execute(
                "INSERT OR REPLACE INTO relationships VALUES (?,?,?,?,?,?,?)",
                (rel.id, rel.source_id, rel.target_id, rel.rel_type,
                 rel.weight, json.dumps(rel.metadata), rel.created_at)
            )
            conn.commit()
            conn.close()
        return rel.id

    def find_entity(self, value: str = None, entity_type: str = None) -> list[Entity]:
        results = list(self.entities.values())
        if value:
            results = [e for e in results if value.lower() in e.value.lower()]
        if entity_type:
            results = [e for e in results if e.entity_type == entity_type]
        return results

    def neighbors(self, entity_id: str, direction: str = "both") -> list[tuple[Entity, Relationship]]:
        """Get all entities connected to the given entity."""
        results = []
        for rel in self.relationships.values():
            if direction in ("both", "outgoing") and rel.source_id == entity_id:
                target = self.entities.get(rel.target_id)
                if target:
                    results.append((target, rel))
            if direction in ("both", "incoming") and rel.target_id == entity_id:
                source = self.entities.get(rel.source_id)
                if source:
                    results.append((source, rel))
        return results

    def get_stats(self) -> dict:
        type_counts = {}
        for e in self.entities.values():
            type_counts[e.entity_type] = type_counts.get(e.entity_type, 0) + 1
        rel_counts = {}
        for r in self.relationships.values():
            rel_counts[r.rel_type] = rel_counts.get(r.rel_type, 0) + 1
        return {
            "total_entities": len(self.entities),
            "total_relationships": len(self.relationships),
            "entity_types": type_counts,
            "relationship_types": rel_counts,
        }

    def to_json(self) -> str:
        return json.dumps({
            "entities": [e.to_dict() for e in self.entities.values()],
            "relationships": [r.to_dict() for r in self.relationships.values()],
            "stats": self.get_stats(),
        }, indent=2)

    def export_gexf(self, filepath: str):
        """Export graph to GEXF format for Gephi visualization."""
        lines = ['<?xml version="1.0" encoding="UTF-8"?>']
        lines.append('<gexf xmlns="http://www.gexf.net/1.2draft" version="1.2">')
        lines.append('<graph defaultedgetype="directed">')
        lines.append('<nodes>')
        for eid, e in self.entities.items():
            label = e.value.replace('"', '&quot;')
            lines.append(f'  <node id="{eid}" label="{label}" />')
        lines.append('</nodes>')
        lines.append('<edges>')
        for rid, r in self.relationships.items():
            lines.append(f'  <edge id="{rid}" source="{r.source_id}" target="{r.target_id}" label="{r.rel_type}" weight="{r.weight}" />')
        lines.append('</edges>')
        lines.append('</graph>')
        lines.append('</gexf>')
        os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)
        with open(filepath, "w") as f:
            f.write("\n".join(lines))

    def export_markdown(self, filepath: str, title: str = "Investigation Report"):
        """Export a readable markdown report of the graph."""
        lines = [f"# {title}", ""]
        lines.append(f"**Generated:** {datetime.utcnow().isoformat()}")
        stats = self.get_stats()
        lines.append(f"**Entities:** {stats['total_entities']} | **Relationships:** {stats['total_relationships']}")
        lines.append("")

        lines.append("## Entity Summary")
        for etype, count in sorted(stats["entity_types"].items()):
            lines.append(f"- **{etype.title()}:** {count}")
        lines.append("")

        lines.append("## Relationship Summary")
        for rtype, count in sorted(stats["relationship_types"].items()):
            lines.append(f"- **{rtype}:** {count}")
        lines.append("")

        lines.append("## Entities")
        for e in sorted(self.entities.values(), key=lambda x: (x.entity_type, x.value)):
            tags = f" [{', '.join(e.tags)}]" if e.tags else ""
            lines.append(f"- **{e.entity_type.title()}:** {e.value} (source: {e.source}, confidence: {e.confidence:.0%}){tags}")
            if e.metadata:
                for k, v in e.metadata.items():
                    lines.append(f"  - {k}: {v}")
        lines.append("")

        lines.append("## Relationships")
        for r in self.relationships.values():
            src = self.entities.get(r.source_id)
            tgt = self.entities.get(r.target_id)
            src_label = src.value if src else r.source_id
            tgt_label = tgt.value if tgt else r.target_id
            lines.append(f"- **{src_label}** --[{r.rel_type}]--> **{tgt_label}** (weight: {r.weight})")

        os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)
        with open(filepath, "w") as f:
            f.write("\n".join(lines))


class EntityExtractor:
    """
    Regex-based entity extractor. No external API needed.
    Extracts: emails, phone numbers, IPs, domains, SSNs, EINs, URLs, addresses.
    """

    PATTERNS = {
        "email": re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
        "phone": re.compile(r'(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'),
        "ip_address": re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b'),
        "domain": re.compile(r'\b(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}\b'),
        "url": re.compile(r'https?://[^\s<>\"\'\)]+'),
        "ein": re.compile(r'\b\d{2}-\d{7}\b'),
        "ssn": re.compile(r'\b\d{3}-\d{2}-\d{4}\b'),
        "zip_code": re.compile(r'\b\d{5}(?:-\d{4})?\b'),
        "date": re.compile(r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b'),
        "currency": re.compile(r'\$[\d,]+(?:\.\d{2})?'),
        "hex_address": re.compile(r'\b0x[0-9a-fA-F]{8,}\b'),
    }

    def extract(self, text: str, source: str = "") -> list[Entity]:
        entities = []
        for etype, pattern in self.PATTERNS.items():
            matches = pattern.findall(text)
            for match in matches:
                val = match.strip()
                if etype == "domain" and "." not in val:
                    continue
                if etype == "ip_address":
                    parts = val.split(".")
                    if not all(0 <= int(p) <= 255 for p in parts):
                        continue
                e = Entity(etype, val, source=source, confidence=0.7)
                entities.append(e)
        return entities

    def extract_people_names(self, text: str, source: str = "") -> list[Entity]:
        """Basic name extraction using capitalized word sequences."""
        name_pattern = re.compile(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,4})\b')
        matches = name_pattern.findall(text)
        stop_words = {"The", "This", "That", "What", "When", "Where", "How", "Why",
                       "January", "February", "March", "April", "June", "July",
                       "August", "September", "October", "November", "December",
                       "Monday", "Tuesday", "Wednesday", "Thursday", "Friday",
                       "Saturday", "Sunday", "United", "States", "America",
                       "California", "New", "York", "Texas", "Florida"}
        entities = []
        for match in matches:
            if not any(w in match for w in stop_words):
                e = Entity("person", match, source=source, confidence=0.4,
                           metadata={"method": "capitalized_word_sequence"})
                entities.append(e)
        return entities


class DocumentIngester:
    """Ingests text documents into the investigation graph."""

    def __init__(self, graph: InvestigationGraph):
        self.graph = graph
        self.extractor = EntityExtractor()

    def ingest_text(self, text: str, filename: str = "", metadata: dict = None) -> dict:
        doc_id = hashlib.sha256(text.encode()).hexdigest()[:16]
        entities = self.extractor.extract(text, source=filename)
        people = self.extractor.extract_people_names(text, source=filename)

        all_entities = entities + people
        added = 0
        entity_ids = []
        for e in all_entities:
            existing = self.graph.find_entity(value=e.value)
            if not existing:
                self.graph.add_entity(e)
                added += 1
            else:
                e = existing[0]
            entity_ids.append(e.id)

        relationships_found = 0
        for i in range(len(entity_ids)):
            for j in range(i + 1, min(i + 10, len(entity_ids))):
                if entity_ids[i] != entity_ids[j]:
                    rel = Relationship(entity_ids[i], entity_ids[j], "co-occurring", metadata={"document": filename})
                    self.graph.add_relationship(rel)
                    relationships_found += 1

        doc_hash = hashlib.sha256(text.encode()).hexdigest()
        if self.graph.db_path:
            conn = sqlite3.connect(self.graph.db_path)
            conn.execute(
                "INSERT OR REPLACE INTO documents VALUES (?,?,?,?,?,?)",
                (doc_id, filename, doc_hash, json.dumps([e.to_dict() for e in all_entities[:50]]),
                 datetime.utcnow().isoformat(), json.dumps(metadata or {}))
            )
            conn.commit()
            conn.close()

        return {
            "document_id": doc_id,
            "filename": filename,
            "entities_extracted": len(all_entities),
            "entities_added": added,
            "relationships_created": relationships_found,
        }

    def ingest_file(self, filepath: str) -> dict:
        path = Path(filepath)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {filepath}")

        text = path.read_text(encoding="utf-8", errors="ignore")
        return self.ingest_text(text, filename=path.name, metadata={"path": str(path.absolute())})

    def ingest_directory(self, dirpath: str, extensions: list[str] = None) -> list[dict]:
        if extensions is None:
            extensions = [".txt", ".md", ".csv", ".json", ".log", ".py", ".js", ".html"]
        results = []
        for f in Path(dirpath).rglob("*"):
            if f.is_file() and f.suffix.lower() in extensions:
                try:
                    result = self.ingest_file(str(f))
                    results.append(result)
                except Exception as ex:
                    results.append({"filename": f.name, "error": str(ex)})
        return results


class TimelineBuilder:
    """Builds chronological timelines from entity metadata and document dates."""

    def __init__(self, graph: InvestigationGraph):
        self.graph = graph

    def build_timeline(self) -> list[dict]:
        events = []
        for e in self.graph.entities.values():
            if "date" in e.metadata:
                events.append({
                    "date": e.metadata["date"],
                    "entity": e.value,
                    "type": e.entity_type,
                    "source": e.source,
                })
            events.append({
                "date": e.created_at,
                "entity": e.value,
                "type": e.entity_type,
                "source": e.source,
                "event": "entity_created",
            })
        for r in self.graph.relationships.values():
            events.append({
                "date": r.created_at,
                "relationship": r.rel_type,
                "source_entity": r.source_id,
                "target_entity": r.target_id,
                "event": "relationship_created",
            })
        events.sort(key=lambda x: x.get("date", ""))
        return events


class NetworkAnalyzer:
    """Basic network analysis without external dependencies."""

    def __init__(self, graph: InvestigationGraph):
        self.graph = graph

    def degree_centrality(self) -> dict[str, float]:
        n = len(self.graph.entities)
        if n <= 1:
            return {eid: 0.0 for eid in self.graph.entities}
        degrees = {eid: 0 for eid in self.graph.entities}
        for rel in self.graph.relationships.values():
            degrees[rel.source_id] = degrees.get(rel.source_id, 0) + 1
            degrees[rel.target_id] = degrees.get(rel.target_id, 0) + 1
        max_deg = max(degrees.values()) if degrees else 1
        return {eid: d / max_deg for eid, d in degrees.items()}

    def find_clusters(self) -> list[set[str]]:
        """Simple BFS-based connected component detection."""
        visited = set()
        clusters = []
        adj = {eid: set() for eid in self.graph.entities}
        for rel in self.graph.relationships.values():
            if rel.source_id in adj and rel.target_id in adj:
                adj[rel.source_id].add(rel.target_id)
                adj[rel.target_id].add(rel.source_id)
        for eid in self.graph.entities:
            if eid not in visited:
                cluster = set()
                queue = [eid]
                while queue:
                    node = queue.pop(0)
                    if node in visited:
                        continue
                    visited.add(node)
                    cluster.add(node)
                    queue.extend(adj.get(node, set()) - visited)
                clusters.append(cluster)
        return clusters

    def find_bridges(self) -> list[Relationship]:
        """Find relationships that are bridges (removing them disconnects the graph)."""
        adj = {eid: set() for eid in self.graph.entities}
        edge_map = {}
        for rel in self.graph.relationships.values():
            if rel.source_id in adj and rel.target_id in adj:
                adj[rel.source_id].add(rel.target_id)
                adj[rel.target_id].add(rel.source_id)
                edge_map[(rel.source_id, rel.target_id)] = rel

        def count_components(a):
            vis = set()
            comps = 0
            for node in a:
                if node not in vis:
                    comps += 1
                    q = [node]
                    while q:
                        n = q.pop(0)
                        if n in vis:
                            continue
                        vis.add(n)
                        q.extend(a[n] - vis)
            return comps

        orig = count_components(adj)
        bridges = []
        for (u, v), rel in edge_map.items():
            adj[u].discard(v)
            adj[v].discard(u)
            if count_components(adj) > orig:
                bridges.append(rel)
            adj[u].add(v)
            adj[v].add(u)
        return bridges

    def risk_score(self, entity_id: str) -> float:
        centrality = self.degree_centrality()
        c = centrality.get(entity_id, 0)
        neighbors = self.graph.neighbors(entity_id)
        risk = c * 0.4
        rel_types = set(r[1].rel_type for r in neighbors)
        risk += len(rel_types) * 0.05
        risk += min(len(neighbors) * 0.02, 0.3)
        for _, rel in neighbors:
            if rel.metadata.get("risk"):
                risk += 0.1
        return min(risk, 1.0)


class SentinelEngine:
    """
    Main entry point for the Sentinel OSINT Engine.
    Coordinates all subsystems.
    """

    def __init__(self, workspace: str = None):
        self.workspace = workspace or os.path.join(os.getcwd(), "sentinel-workspace")
        os.makedirs(self.workspace, exist_ok=True)
        db_path = os.path.join(self.workspace, "investigation.db")
        self.graph = InvestigationGraph(db_path)
        self.ingester = DocumentIngester(self.graph)
        self.timeline = TimelineBuilder(self.graph)
        self.network = NetworkAnalyzer(self.graph)
        self.extractor = EntityExtractor()
        self.created_at = datetime.utcnow().isoformat()

    def investigate(self, target: str, target_type: str = "auto") -> dict:
        if target_type == "auto":
            target_type = self._detect_type(target)
        e = Entity(target_type, target, source="manual_investigation", confidence=0.9)
        self.graph.add_entity(e)
        return {"entity": e.to_dict(), "type": target_type}

    def _detect_type(self, value: str) -> str:
        if re.match(r'^[\w.-]+@[\w.-]+\.\w+$', value):
            return "email"
        if re.match(r'^\+?\d[\d\s-]+$', value):
            return "phone"
        if re.match(r'^\d{1,3}(\.\d{1,3}){3}$', value):
            return "ip_address"
        if re.match(r'^https?://', value):
            return "domain"
        if re.match(r'^\d{2}-\d{7}$', value):
            return "financial_account"
        return "person"

    def ingest(self, source: str) -> dict:
        path = Path(source)
        if path.is_file():
            return self.ingester.ingest_file(source)
        elif path.is_dir():
            return {"files": self.ingester.ingest_directory(source)}
        else:
            return self.ingester.ingest_text(source, filename="direct_input")

    def link(self, source_id: str, target_id: str, rel_type: str, weight: float = 1.0) -> dict:
        rel = Relationship(source_id, target_id, rel_type, weight)
        self.graph.add_relationship(rel)
        return rel.to_dict()

    def search(self, query: str) -> list[dict]:
        results = self.graph.find_entity(value=query)
        return [e.to_dict() for e in results]

    def analyze(self) -> dict:
        centrality = self.network.degree_centrality()
        top_central = sorted(centrality.items(), key=lambda x: x[1], reverse=True)[:10]
        clusters = self.network.find_clusters()
        bridges = self.network.find_bridges()
        return {
            "graph_stats": self.graph.get_stats(),
            "top_central_entities": [
                {"entity_id": eid, "centrality": round(score, 4),
                 "value": self.graph.entities[eid].value if eid in self.graph.entities else "unknown"}
                for eid, score in top_central
            ],
            "clusters": len(clusters),
            "largest_cluster": max(len(c) for c in clusters) if clusters else 0,
            "bridges": len(bridges),
        }

    def timeline_view(self) -> list[dict]:
        return self.timeline.build_timeline()

    def report(self, output_path: str = None) -> str:
        if not output_path:
            output_path = os.path.join(self.workspace, "report.md")
        self.graph.export_markdown(output_path, title="Sentinel Investigation Report")
        return output_path

    def export_graph(self, fmt: str = "json", output_path: str = None) -> str:
        if fmt == "json":
            path = output_path or os.path.join(self.workspace, "graph.json")
            with open(path, "w") as f:
                f.write(self.graph.to_json())
        elif fmt == "gexf":
            path = output_path or os.path.join(self.workspace, "graph.gexf")
            self.graph.export_gexf(path)
        else:
            raise ValueError(f"Unsupported format: {fmt}")
        return path

    def save(self):
        if self.graph.db_path:
            self.graph.to_json()
