"""
Database layer for OSINT Independent Platform.
Supports SQLite, PostgreSQL, and MySQL via SQLAlchemy.
"""
import os
from contextlib import contextmanager
from datetime import datetime
from typing import Any, Dict, List, Optional, Generator, Type, TypeVar
from sqlalchemy import create_engine, Column, String, Text, DateTime, Integer, Float, Boolean, JSON, ForeignKey, Index, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from sqlalchemy.pool import StaticPool
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.dialects.sqlite import JSON as SQLiteJSON
import uuid

from .config import get_config
from .models import EntityType, SourceType, ConfidenceLevel, Source, Entity, Relationship, Observation, EnrichmentResult, Investigation, CollectionJob

Base = declarative_base()
T = TypeVar('T', bound=Base)


class EntityModel(Base):
    __tablename__ = 'entities'
    
    id = Column(String(36), primary_key=True)
    type = Column(SQLEnum(EntityType), nullable=False, index=True)
    value = Column(String(512), nullable=False, index=True)
    name = Column(String(256), default='')
    description = Column(Text, default='')
    tags = Column(JSON, default=list)
    attributes = Column(JSON, default=dict)
    sources = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    confidence = Column(Integer, default=2)
    is_malicious = Column(Boolean, default=False)
    risk_score = Column(Float, default=0.0)
    
    # Relationships
    observations = relationship("ObservationModel", back_populates="entity", cascade="all, delete-orphan")
    enrichments = relationship("EnrichmentModel", back_populates="entity", cascade="all, delete-orphan")
    relationships_from = relationship("RelationshipModel", foreign_keys="RelationshipModel.source_id", back_populates="source_entity", cascade="all, delete-orphan")
    relationships_to = relationship("RelationshipModel", foreign_keys="RelationshipModel.target_id", back_populates="target_entity", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('ix_entities_type_value', 'type', 'value', unique=True),
        Index('ix_entities_malicious', 'is_malicious'),
        Index('ix_entities_risk', 'risk_score'),
    )


class RelationshipModel(Base):
    __tablename__ = 'relationships'
    
    id = Column(String(36), primary_key=True)
    source_id = Column(String(36), ForeignKey('entities.id'), nullable=False, index=True)
    target_id = Column(String(36), ForeignKey('entities.id'), nullable=False, index=True)
    relationship_type = Column(String(64), nullable=False, index=True)
    description = Column(Text, default='')
    confidence = Column(Integer, default=2)
    sources = Column(JSON, default=list)
    metadata = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    source_entity = relationship("EntityModel", foreign_keys=[source_id], back_populates="relationships_from")
    target_entity = relationship("EntityModel", foreign_keys=[target_id], back_populates="relationships_to")
    
    __table_args__ = (
        Index('ix_rel_source_target', 'source_id', 'target_id'),
        Index('ix_rel_type', 'relationship_type'),
    )


class ObservationModel(Base):
    __tablename__ = 'observations'
    
    id = Column(String(36), primary_key=True)
    entity_id = Column(String(36), ForeignKey('entities.id'), nullable=False, index=True)
    collector = Column(String(64), nullable=False, index=True)
    data = Column(JSON, default=dict)
    raw_data = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    entity = relationship("EntityModel", back_populates="observations")


class EnrichmentModel(Base):
    __tablename__ = 'enrichments'
    
    id = Column(String(36), primary_key=True)
    entity_id = Column(String(36), ForeignKey('entities.id'), nullable=False, index=True)
    enricher = Column(String(64), nullable=False, index=True)
    success = Column(Boolean, default=False)
    data = Column(JSON, default=dict)
    error = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    duration_ms = Column(Float, default=0.0)
    
    entity = relationship("EntityModel", back_populates="enrichments")


class InvestigationModel(Base):
    __tablename__ = 'investigations'
    
    id = Column(String(36), primary_key=True)
    name = Column(String(256), nullable=False)
    description = Column(Text, default='')
    entity_ids = Column(JSON, default=list)
    tags = Column(JSON, default=list)
    status = Column(String(32), default='open')
    assignee = Column(String(64), default='')
    metadata = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class CollectionJobModel(Base):
    __tablename__ = 'collection_jobs'
    
    id = Column(String(36), primary_key=True)
    collector = Column(String(64), nullable=False, index=True)
    target = Column(String(512), nullable=False)
    parameters = Column(JSON, default=dict)
    status = Column(String(32), default='pending', index=True)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    result_count = Column(Integer, default=0)
    error = Column(Text)
    metadata = Column(JSON, default=dict)


class Database:
    """Database manager with connection pooling and session management."""
    
    def __init__(self, database_url: Optional[str] = None, echo: bool = False):
        config = get_config()
        self.database_url = database_url or config.database.url
        self.echo = echo or config.database.echo
        self._engine = None
        self._session_factory = None
        self._init_engine()
    
    def _init_engine(self) -> None:
        """Initialize database engine."""
        connect_args = {}
        
        if self.database_url.startswith('sqlite'):
            connect_args = {'check_same_thread': False}
            self._engine = create_engine(
                self.database_url,
                connect_args=connect_args,
                poolclass=StaticPool,
                echo=self.echo
            )
        else:
            self._engine = create_engine(
                self.database_url,
                pool_size=get_config().database.pool_size,
                max_overflow=get_config().database.max_overflow,
                echo=self.echo
            )
        
        self._session_factory = sessionmaker(bind=self._engine, expire_on_commit=False)
    
    def create_tables(self) -> None:
        """Create all tables."""
        Base.metadata.create_all(self._engine)
    
    def drop_tables(self) -> None:
        """Drop all tables."""
        Base.metadata.drop_all(self._engine)
    
    @contextmanager
    def session(self) -> Generator[Session, None, None]:
        """Get a database session with automatic commit/rollback."""
        session = self._session_factory()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    
    def get_session(self) -> Session:
        """Get a new session (caller responsible for closing)."""
        return self._session_factory()
    
    def close(self) -> None:
        """Close engine and connections."""
        if self._engine:
            self._engine.dispose()
    
    # Entity operations
    def upsert_entity(self, entity: Entity) -> Entity:
        """Insert or update an entity."""
        with self.session() as session:
            model = session.query(EntityModel).filter_by(id=entity.id).first()
            if model:
                model.type = entity.type
                model.value = entity.value
                model.name = entity.name
                model.description = entity.description
                model.tags = entity.tags
                model.attributes = entity.attributes
                model.sources = [s.__dict__ for s in entity.sources]
                model.updated_at = entity.updated_at
                model.confidence = entity.confidence.value
                model.is_malicious = entity.is_malicious
                model.risk_score = entity.risk_score
            else:
                model = EntityModel(
                    id=entity.id,
                    type=entity.type,
                    value=entity.value,
                    name=entity.name,
                    description=entity.description,
                    tags=entity.tags,
                    attributes=entity.attributes,
                    sources=[s.__dict__ for s in entity.sources],
                    created_at=entity.created_at,
                    updated_at=entity.updated_at,
                    confidence=entity.confidence.value,
                    is_malicious=entity.is_malicious,
                    risk_score=entity.risk_score
                )
                session.add(model)
            session.flush()
            return entity
    
    def get_entity(self, entity_id: str) -> Optional[Entity]:
        """Get entity by ID."""
        with self.session() as session:
            model = session.query(EntityModel).filter_by(id=entity_id).first()
            return self._model_to_entity(model) if model else None
    
    def get_entity_by_value(self, entity_type: EntityType, value: str) -> Optional[Entity]:
        """Get entity by type and value."""
        with self.session() as session:
            model = session.query(EntityModel).filter_by(type=entity_type, value=value).first()
            return self._model_to_entity(model) if model else None
    
    def search_entities(self, entity_type: Optional[EntityType] = None, 
                       tags: Optional[List[str]] = None,
                       is_malicious: Optional[bool] = None,
                       min_risk: float = 0.0,
                       limit: int = 100,
                       offset: int = 0) -> List[Entity]:
        """Search entities with filters."""
        with self.session() as session:
            query = session.query(EntityModel)
            
            if entity_type:
                query = query.filter(EntityModel.type == entity_type)
            if is_malicious is not None:
                query = query.filter(EntityModel.is_malicious == is_malicious)
            if min_risk > 0:
                query = query.filter(EntityModel.risk_score >= min_risk)
            if tags:
                for tag in tags:
                    query = query.filter(EntityModel.tags.contains([tag]))
            
            query = query.order_by(EntityModel.risk_score.desc(), EntityModel.updated_at.desc())
            query = query.limit(limit).offset(offset)
            
            return [self._model_to_entity(m) for m in query.all()]
    
    def upsert_relationship(self, relationship: Relationship) -> Relationship:
        """Insert or update a relationship."""
        with self.session() as session:
            model = session.query(RelationshipModel).filter_by(id=relationship.id).first()
            if model:
                model.source_id = relationship.source_id
                model.target_id = relationship.target_id
                model.relationship_type = relationship.relationship_type
                model.description = relationship.description
                model.confidence = relationship.confidence.value
                model.sources = [s.__dict__ for s in relationship.sources]
                model.metadata = relationship.metadata
            else:
                model = RelationshipModel(
                    id=relationship.id,
                    source_id=relationship.source_id,
                    target_id=relationship.target_id,
                    relationship_type=relationship.relationship_type,
                    description=relationship.description,
                    confidence=relationship.confidence.value,
                    sources=[s.__dict__ for s in relationship.sources],
                    metadata=relationship.metadata,
                    created_at=relationship.created_at
                )
                session.add(model)
            session.flush()
            return relationship
    
    def get_relationships(self, entity_id: str, direction: str = 'both') -> List[Relationship]:
        """Get relationships for an entity."""
        with self.session() as session:
            query = session.query(RelationshipModel)
            if direction == 'outgoing':
                query = query.filter(RelationshipModel.source_id == entity_id)
            elif direction == 'incoming':
                query = query.filter(RelationshipModel.target_id == entity_id)
            else:
                query = query.filter(
                    (RelationshipModel.source_id == entity_id) | 
                    (RelationshipModel.target_id == entity_id)
                )
            return [self._model_to_relationship(m) for m in query.all()]
    
    def add_observation(self, observation: Observation) -> Observation:
        """Add an observation."""
        with self.session() as session:
            model = ObservationModel(
                id=observation.id,
                entity_id=observation.entity_id,
                collector=observation.collector,
                data=observation.data,
                raw_data=observation.raw_data,
                timestamp=observation.timestamp
            )
            session.add(model)
            return observation
    
    def get_observations(self, entity_id: str, collector: Optional[str] = None) -> List[Observation]:
        """Get observations for an entity."""
        with self.session() as session:
            query = session.query(ObservationModel).filter(ObservationModel.entity_id == entity_id)
            if collector:
                query = query.filter(ObservationModel.collector == collector)
            query = query.order_by(ObservationModel.timestamp.desc())
            return [self._model_to_observation(m) for m in query.all()]
    
    def add_enrichment(self, enrichment: EnrichmentResult) -> EnrichmentResult:
        """Add an enrichment result."""
        with self.session() as session:
            model = EnrichmentModel(
                id=str(uuid.uuid4()),
                entity_id=enrichment.entity_id,
                enricher=enrichment.enricher,
                success=enrichment.success,
                data=enrichment.data,
                error=enrichment.error,
                timestamp=enrichment.timestamp,
                duration_ms=enrichment.duration_ms
            )
            session.add(model)
            return enrichment
    
    def get_enrichments(self, entity_id: str, enricher: Optional[str] = None) -> List[EnrichmentResult]:
        """Get enrichment results for an entity."""
        with self.session() as session:
            query = session.query(EnrichmentModel).filter(EnrichmentModel.entity_id == entity_id)
            if enricher:
                query = query.filter(EnrichmentModel.enricher == enricher)
            query = query.order_by(EnrichmentModel.timestamp.desc())
            return [self._model_to_enrichment(m) for m in query.all()]
    
    def upsert_investigation(self, investigation: Investigation) -> Investigation:
        """Insert or update an investigation."""
        with self.session() as session:
            model = session.query(InvestigationModel).filter_by(id=investigation.id).first()
            if model:
                model.name = investigation.name
                model.description = investigation.description
                model.entity_ids = investigation.entity_ids
                model.tags = investigation.tags
                model.status = investigation.status
                model.assignee = investigation.assignee
                model.metadata = investigation.metadata
                model.updated_at = investigation.updated_at
            else:
                model = InvestigationModel(
                    id=investigation.id,
                    name=investigation.name,
                    description=investigation.description,
                    entity_ids=investigation.entity_ids,
                    tags=investigation.tags,
                    status=investigation.status,
                    assignee=investigation.assignee,
                    metadata=investigation.metadata,
                    created_at=investigation.created_at,
                    updated_at=investigation.updated_at
                )
                session.add(model)
            session.flush()
            return investigation
    
    def get_investigation(self, investigation_id: str) -> Optional[Investigation]:
        """Get investigation by ID."""
        with self.session() as session:
            model = session.query(InvestigationModel).filter_by(id=investigation_id).first()
            if model:
                return Investigation(
                    id=model.id,
                    name=model.name,
                    description=model.description,
                    entity_ids=model.entity_ids,
                    tags=model.tags,
                    status=model.status,
                    assignee=model.assignee,
                    created_at=model.created_at,
                    updated_at=model.updated_at,
                    metadata=model.metadata
                )
            return None
    
    def upsert_collection_job(self, job: CollectionJob) -> CollectionJob:
        """Insert or update a collection job."""
        with self.session() as session:
            model = session.query(CollectionJobModel).filter_by(id=job.id).first()
            if model:
                model.collector = job.collector
                model.target = job.target
                model.parameters = job.parameters
                model.status = job.status
                model.started_at = job.started_at
                model.completed_at = job.completed_at
                model.result_count = job.result_count
                model.error = job.error
                model.metadata = job.metadata
            else:
                model = CollectionJobModel(
                    id=job.id,
                    collector=job.collector,
                    target=job.target,
                    parameters=job.parameters,
                    status=job.status,
                    started_at=job.started_at,
                    completed_at=job.completed_at,
                    result_count=job.result_count,
                    error=job.error,
                    metadata=job.metadata
                )
                session.add(model)
            session.flush()
            return job
    
    def get_collection_job(self, job_id: str) -> Optional[CollectionJob]:
        """Get collection job by ID."""
        with self.session() as session:
            model = session.query(CollectionJobModel).filter_by(id=job_id).first()
            if model:
                return CollectionJob(
                    id=model.id,
                    collector=model.collector,
                    target=model.target,
                    parameters=model.parameters,
                    status=model.status,
                    started_at=model.started_at,
                    completed_at=model.completed_at,
                    result_count=model.result_count,
                    error=model.error,
                    metadata=model.metadata
                )
            return None
    
    # Model conversion methods
    def _model_to_entity(self, model: EntityModel) -> Entity:
        sources = [Source(**s) for s in (model.sources or [])]
        return Entity(
            id=model.id,
            type=model.type,
            value=model.value,
            name=model.name,
            description=model.description,
            tags=model.tags or [],
            attributes=model.attributes or {},
            sources=sources,
            created_at=model.created_at,
            updated_at=model.updated_at,
            confidence=ConfidenceLevel(model.confidence),
            is_malicious=model.is_malicious,
            risk_score=model.risk_score
        )
    
    def _model_to_relationship(self, model: RelationshipModel) -> Relationship:
        sources = [Source(**s) for s in (model.sources or [])]
        return Relationship(
            id=model.id,
            source_id=model.source_id,
            target_id=model.target_id,
            relationship_type=model.relationship_type,
            description=model.description,
            confidence=ConfidenceLevel(model.confidence),
            sources=sources,
            created_at=model.created_at,
            metadata=model.metadata or {}
        )
    
    def _model_to_observation(self, model: ObservationModel) -> Observation:
        return Observation(
            id=model.id,
            entity_id=model.entity_id,
            collector=model.collector,
            data=model.data or {},
            raw_data=model.raw_data,
            timestamp=model.timestamp
        )
    
    def _model_to_enrichment(self, model: EnrichmentModel) -> EnrichmentResult:
        return EnrichmentResult(
            entity_id=model.entity_id,
            enricher=model.enricher,
            success=model.success,
            data=model.data or {},
            error=model.error,
            timestamp=model.timestamp,
            duration_ms=model.duration_ms
        )


# Global database instance
_db: Optional[Database] = None


def get_database() -> Database:
    """Get global database instance."""
    global _db
    if _db is None:
        _db = Database()
    return _db


def init_database(database_url: Optional[str] = None, echo: bool = False) -> Database:
    """Initialize global database."""
    global _db
    _db = Database(database_url, echo)
    _db.create_tables()
    return _db


def close_database() -> None:
    """Close global database."""
    global _db
    if _db:
        _db.close()
        _db = None