"""
Base collector class and registry for OSINT Independent Platform.
"""
import asyncio
import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Set, Type
from uuid import uuid4

from ..core.config import get_config
from ..core.database import get_database, CollectionJob, CollectionJobModel
from ..core.models import Entity, EntityType, Observation, Source, SourceType, ConfidenceLevel


@dataclass
class CollectorResult:
    """Result of a collection operation."""
    entities: List[Entity] = field(default_factory=list)
    observations: List[Observation] = field(default_factory=list)
    relationships: List[Dict[str, Any]] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    duration_ms: float = 0.0


class BaseCollector(ABC):
    """Base class for all collectors."""
    
    name: str = ""
    description: str = ""
    version: str = "1.0.0"
    supported_types: List[EntityType] = []
    rate_limit: int = 60
    rate_limit_window: int = 60
    timeout: int = 30
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = get_config()
        self.collector_config = self.config.collectors
        self.logger = logging.getLogger(f"collector.{self.name}")
        self._rate_limit_count = 0
        self._rate_limit_reset = 0
        self._job_id: Optional[str] = None
        
        # Override with provided config
        if config:
            for key, value in config.items():
                setattr(self, key, value)
    
    @abstractmethod
    async def collect(self, target: str, **kwargs) -> CollectorResult:
        """Collect intelligence on a target. Must be implemented by subclasses."""
        pass
    
    def can_collect(self, entity_type: EntityType) -> bool:
        """Check if this collector supports the entity type."""
        return entity_type in self.supported_types or not self.supported_types
    
    def _check_rate_limit(self) -> bool:
        """Check if we're within rate limits."""
        now = time.time()
        if now > self._rate_limit_reset:
            self._rate_limit_count = 0
            self._rate_limit_reset = now + self.rate_limit_window
        
        if self._rate_limit_count >= self.rate_limit:
            return False
        
        self._rate_limit_count += 1
        return True
    
    async def _wait_for_rate_limit(self) -> None:
        """Wait until rate limit allows another request."""
        while not self._check_rate_limit():
            await asyncio.sleep(1)
    
    def _create_entity(self, entity_type: EntityType, value: str, 
                      name: str = "", description: str = "",
                      tags: Optional[List[str]] = None,
                      attributes: Optional[Dict[str, Any]] = None,
                      source_name: str = "",
                      source_type: SourceType = SourceType.OTHER,
                      confidence: ConfidenceLevel = ConfidenceLevel.MEDIUM,
                      metadata: Optional[Dict[str, Any]] = None) -> Entity:
        """Create an entity with proper source attribution."""
        source = Source(
            type=source_type,
            name=source_name or self.name,
            confidence=confidence,
            metadata=metadata or {}
        )
        
        return Entity(
            id=str(uuid4()),
            type=entity_type,
            value=value,
            name=name,
            description=description,
            tags=tags or [],
            attributes=attributes or {},
            sources=[source]
        )
    
    def _create_observation(self, entity_id: str, data: Dict[str, Any],
                           raw_data: Optional[str] = None) -> Observation:
        """Create an observation linked to an entity."""
        return Observation(
            id=str(uuid4()),
            entity_id=entity_id,
            collector=self.name,
            data=data,
            raw_data=raw_data
        )
    
    def _start_job(self, target: str, parameters: Dict[str, Any]) -> CollectionJob:
        """Start a collection job for tracking."""
        db = get_database()
        job = CollectionJob(
            id=str(uuid4()),
            collector=self.name,
            target=target,
            parameters=parameters,
            status="running",
            started_at=datetime.utcnow()
        )
        db.upsert_collection_job(job)
        self._job_id = job.id
        return job
    
    def _complete_job(self, result: CollectorResult) -> None:
        """Complete the collection job."""
        if not self._job_id:
            return
        
        db = get_database()
        job = db.get_collection_job(self._job_id)
        if job:
            job.status = "completed" if not result.errors else "completed_with_errors"
            job.completed_at = datetime.utcnow()
            job.result_count = len(result.entities)
            job.error = "; ".join(result.errors) if result.errors else None
            job.metadata = result.metadata
            db.upsert_collection_job(job)
        self._job_id = None
    
    def _fail_job(self, error: str) -> None:
        """Mark job as failed."""
        if not self._job_id:
            return
        
        db = get_database()
        job = db.get_collection_job(self._job_id)
        if job:
            job.status = "failed"
            job.completed_at = datetime.utcnow()
            job.error = error
            db.upsert_collection_job(job)
        self._job_id = None


class CollectorRegistry:
    """Registry for managing collectors."""
    
    _collectors: Dict[str, Type[BaseCollector]] = {}
    _instances: Dict[str, BaseCollector] = {}
    
    @classmethod
    def register(cls, collector_class: Type[BaseCollector]) -> Type[BaseCollector]:
        """Register a collector class."""
        if not collector_class.name:
            raise ValueError("Collector must have a name")
        cls._collectors[collector_class.name] = collector_class
        return collector_class
    
    @classmethod
    def unregister(cls, name: str) -> None:
        """Unregister a collector."""
        cls._collectors.pop(name, None)
        cls._instances.pop(name, None)
    
    @classmethod
    def get_collector(cls, name: str, config: Optional[Dict[str, Any]] = None) -> BaseCollector:
        """Get a collector instance."""
        if name not in cls._collectors:
            raise ValueError(f"Collector '{name}' not registered")
        
        if name not in cls._instances:
            cls._instances[name] = cls._collectors[name](config)
        
        return cls._instances[name]
    
    @classmethod
    def get_collector_class(cls, name: str) -> Optional[Type[BaseCollector]]:
        """Get a collector class without instantiating."""
        return cls._collectors.get(name)
    
    @classmethod
    def list_collectors(cls) -> List[str]:
        """List all registered collector names."""
        return list(cls._collectors.keys())
    
    @classmethod
    def get_collectors_for_type(cls, entity_type: EntityType) -> List[Type[BaseCollector]]:
        """Get all collectors that support an entity type."""
        return [c for c in cls._collectors.values() if c.can_collect(entity_type)]
    
    @classmethod
    def clear_instances(cls) -> None:
        """Clear all cached instances."""
        cls._instances.clear()


def collector(name: str, description: str = "", 
              supported_types: Optional[List[EntityType]] = None,
              rate_limit: int = 60, timeout: int = 30):
    """Decorator to register a collector class."""
    def decorator(cls: Type[BaseCollector]) -> Type[BaseCollector]:
        cls.name = name
        cls.description = description
        cls.supported_types = supported_types or []
        cls.rate_limit = rate_limit
        cls.timeout = timeout
        return CollectorRegistry.register(cls)
    return decorator