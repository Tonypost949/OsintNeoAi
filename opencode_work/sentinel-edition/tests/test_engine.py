#!/usr/bin/env python3
"""Basic tests for the Sentinel OSINT Engine."""

import os
import sys
import tempfile
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.engine import (
    Entity, Relationship, InvestigationGraph, EntityExtractor,
    DocumentIngester, SentinelEngine, NetworkAnalyzer
)
from analyzers.text_analyzer import TextAnalyzer


def test_entity_creation():
    e = Entity("person", "John Doe", source="test", confidence=0.8)
    assert e.entity_type == "person"
    assert e.value == "John Doe"
    assert e.confidence == 0.8
    assert e.id
    d = e.to_dict()
    e2 = Entity.from_dict(d)
    assert e2.value == "John Doe"
    print("PASS: Entity creation")


def test_relationship():
    r = Relationship("src123", "tgt456", "works_at", weight=0.9)
    assert r.source_id == "src123"
    assert r.target_id == "tgt456"
    assert r.rel_type == "works_at"
    d = r.to_dict()
    r2 = Relationship.from_dict(d)
    assert r2.rel_type == "works_at"
    print("PASS: Relationship creation")


def test_graph():
    with tempfile.TemporaryDirectory() as tmpdir:
        db = os.path.join(tmpdir, "test.db")
        g = InvestigationGraph(db)
        e1 = Entity("person", "Alice", source="test")
        e2 = Entity("organization", "Acme Corp", source="test")
        g.add_entity(e1)
        g.add_entity(e2)
        r = Relationship(e1.id, e2.id, "works_at")
        g.add_relationship(r)
        assert len(g.entities) == 2
        assert len(g.relationships) == 1
        found = g.find_entity(value="Alice")
        assert len(found) == 1
        stats = g.get_stats()
        assert stats["total_entities"] == 2
        assert stats["total_relationships"] == 1
        neighbors = g.neighbors(e1.id)
        assert len(neighbors) == 1
        gjson = g.to_json()
        data = json.loads(gjson)
        assert len(data["entities"]) == 2
        g.export_gexf(os.path.join(tmpdir, "test.gexf"))
        g.export_markdown(os.path.join(tmpdir, "test.md"))
    print("PASS: Graph operations")


def test_entity_extractor():
    ext = EntityExtractor()
    text = "Contact admin@example.com or call 555-123-4567. Server at 192.168.1.1. Visit https://example.com"
    entities = ext.extract(text, source="test")
    types = {e.entity_type for e in entities}
    assert "email" in types
    assert "phone" in types
    assert "ip_address" in types
    assert "url" in types
    print("PASS: Entity extraction")


def test_text_analyzer():
    ta = TextAnalyzer()
    text = "The suspicious fraud transaction involved shell companies and offshore accounts. Discrepancies found in audit."
    risk = ta.risk_assessment(text)
    assert risk["risk_score"] > 0
    assert risk["risk_level"] in ("LOW", "MEDIUM", "HIGH", "CRITICAL")
    keywords = ta.extract_keywords(text, top_n=5)
    assert len(keywords) > 0
    dates = ta.extract_dates("Meeting on 2024-01-15 and 03/20/2024")
    assert len(dates) == 2
    figures = ta.extract_financial_figures("Budget was $1,500,000.00")
    assert len(figures) == 1
    print("PASS: Text analysis")


def test_network_analyzer():
    from core.engine import InvestigationGraph
    g = InvestigationGraph()
    entities = [Entity("person", f"Person-{i}") for i in range(5)]
    for e in entities:
        g.add_entity(e)
    for i in range(4):
        g.add_relationship(Relationship(entities[i].id, entities[i+1].id, "connected"))
    g.add_relationship(Relationship(entities[0].id, entities[4].id, "connected"))
    na = NetworkAnalyzer(g)
    centrality = na.degree_centrality()
    assert len(centrality) == 5
    clusters = na.find_clusters()
    assert len(clusters) == 1
    print("PASS: Network analysis")


def test_sentinel_engine():
    with tempfile.TemporaryDirectory() as tmpdir:
        engine = SentinelEngine(tmpdir)
        result = engine.investigate("test@example.com")
        assert result["type"] == "email"
        result = engine.ingest("Contact test@example.com for info about Acme Corp")
        assert result["entities_extracted"] > 0
        analysis = engine.analyze()
        assert "graph_stats" in analysis
        engine.report(os.path.join(tmpdir, "report.md"))
        engine.export_graph("json", os.path.join(tmpdir, "graph.json"))
    print("PASS: Sentinel engine integration")


def run_all():
    print("Running Sentinel OSINT Engine tests...\n")
    test_entity_creation()
    test_relationship()
    test_graph()
    test_entity_extractor()
    test_text_analyzer()
    test_network_analyzer()
    test_sentinel_engine()
    print("\nAll tests passed!")


if __name__ == "__main__":
    run_all()
