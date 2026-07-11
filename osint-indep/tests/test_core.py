"""Tests for OSINT Independent Platform"""
import pytest
import asyncio
from datetime import datetime
from uuid import uuid4

from src.core.models import (
    EntityType, SourceType, ConfidenceLevel,
    Source, Entity, Relationship, Observation,
    EnrichmentResult, Investigation, CollectionJob
)
from src.core.config import Config, DatabaseConfig, APIConfig


class TestModels:
    """Test core data models"""
    
    def test_source_creation(self):
        source = Source(
            type=SourceType.COLLECTOR,
            name="test_collector",
            confidence=ConfidenceLevel.HIGH
        )
        assert source.type == SourceType.COLLECTOR
        assert source.name == "test_collector"
        assert source.confidence == ConfidenceLevel.HIGH
    
    def test_entity_creation(self):
        entity = Entity(
            id=str(uuid4()),
            type=EntityType.DOMAIN,
            value="example.com",
            name="Example Domain",
            tags=["test", "example"],
            attributes={"registrar": "Example Inc"},
            confidence=ConfidenceLevel.MEDIUM
        )
        assert entity.type == EntityType.DOMAIN
        assert entity.value == "example.com"
        assert "test" in entity.tags
        assert entity.confidence == ConfidenceLevel.MEDIUM
    
    def test_entity_add_source(self):
        entity = Entity(
            id=str(uuid4()),
            type=EntityType.IP,
            value="192.168.1.1"
        )
        source = Source(
            type=SourceType.API,
            name="virustotal",
            confidence=ConfidenceLevel.HIGH
        )
        entity.add_source(source)
        assert len(entity.sources) == 1
        assert entity.sources[0].name == "virustotal"
    
    def test_entity_add_tag(self):
        entity = Entity(
            id=str(uuid4()),
            type=EntityType.EMAIL,
            value="test@example.com"
        )
        entity.add_tag("phishing")
        entity.add_tag("malicious")
        assert "phishing" in entity.tags
        assert "malicious" in entity.tags
        assert len(entity.tags) == 2
    
    def test_entity_set_attribute(self):
        entity = Entity(
            id=str(uuid4()),
            type=EntityType.DOMAIN,
            value="test.com"
        )
        entity.set_attribute("mx_records", ["mail.test.com"])
        assert entity.attributes["mx_records"] == ["mail.test.com"]
    
    def test_relationship_creation(self):
        rel = Relationship(
            id=str(uuid4()),
            source_id=str(uuid4()),
            target_id=str(uuid4()),
            relationship_type="resolves_to",
            description="Domain resolves to IP"
        )
        assert rel.relationship_type == "resolves_to"
    
    def test_observation_creation(self):
        obs = Observation(
            id=str(uuid4()),
            entity_id=str(uuid4()),
            collector="dns",
            data={"record_type": "A", "value": "192.168.1.1"}
        )
        assert obs.collector == "dns"
        assert obs.data["record_type"] == "A"
    
    def test_enrichment_result(self):
        result = EnrichmentResult(
            entity_id=str(uuid4()),
            enricher="virustotal",
            success=True,
            data={"malicious": False, "categories": ["legitimate"]}
        )
        assert result.enricher == "virustotal"
        assert result.success is True
    
    def test_investigation_creation(self):
        inv = Investigation(
            id=str(uuid4()),
            name="Test Investigation",
            description="Test description",
            entity_ids=[str(uuid4()), str(uuid4())],
            tags=["test", "investigation"]
        )
        assert inv.name == "Test Investigation"
        assert len(inv.entity_ids) == 2
    
    def test_collection_job_creation(self):
        job = CollectionJob(
            id=str(uuid4()),
            collector="dns",
            target="example.com",
            parameters={"record_types": ["A", "MX"]}
        )
        assert job.collector == "dns"
        assert job.target == "example.com"
        assert job.status == "pending"


class TestConfig:
    """Test configuration management"""
    
    def test_default_config(self):
        config = Config()
        assert config.database.type == "sqlite"
        assert config.api.host == "0.0.0.0"
        assert config.api.port == 8000
    
    def test_database_config_url(self):
        db = DatabaseConfig(type="sqlite", path="test.db")
        assert db.url == "sqlite:///test.db"
        
        db = DatabaseConfig(
            type="postgresql",
            host="localhost",
            port=5432,
            database="test",
            username="user",
            password="pass"
        )
        assert "postgresql://user:pass@localhost:5432/test" in db.url


class TestEntityTypes:
    """Test EntityType enum"""
    
    def test_all_types_exist(self):
        expected = {
            "IP", "DOMAIN", "EMAIL", "PHONE", "PERSON", "ORGANIZATION",
            "LOCATION", "CRYPTO_ADDRESS", "HASH", "URL", "FILE",
            "VULNERABILITY", "MALWARE", "THREAT_ACTOR", "CAMPAIGN",
            "INFRASTRUCTURE", "CERTIFICATE", "ASN", "NETBLOCK"
        }
        actual = {e.value for e in EntityType}
        assert actual == expected


class TestSourceTypes:
    """Test SourceType enum"""
    
    def test_all_types_exist(self):
        expected = {
            "COLLECTOR", "ENRICHMENT", "ANALYSIS", "MANUAL", "IMPORT", "FEED"
        }
        actual = {e.value for e in SourceType}
        assert actual == expected


class TestConfidenceLevels:
    """Test ConfidenceLevel enum"""
    
    def test_ordering(self):
        assert ConfidenceLevel.LOW.value < ConfidenceLevel.MEDIUM.value
        assert ConfidenceLevel.MEDIUM.value < ConfidenceLevel.HIGH.value
        assert ConfidenceLevel.HIGH.value < ConfidenceLevel.VERIFIED.value


if __name__ == "__main__":
    pytest.main([__file__, "-v"])