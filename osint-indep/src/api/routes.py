"""API Routes for OSINT Independent Platform"""
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import uuid4

from src.core.config import get_config
from src.core.database import get_database, CollectionJob
from src.core.models import Entity, EntityType, Relationship, Investigation, Observation
from src.collectors.base import CollectorRegistry

router = APIRouter()
config = get_config()
db = get_database()


# ===== Pydantic Models =====

class EntityCreate(BaseModel):
    type: EntityType
    value: str = Field(..., min_length=1, max_length=512)
    name: str = ""
    description: str = ""
    tags: List[str] = Field(default_factory=list)
    attributes: Dict[str, Any] = Field(default_factory=dict)
    source_name: str = "api"
    confidence: int = Field(default=2, ge=1, le=4)  # ConfidenceLevel


class EntityResponse(BaseModel):
    id: str
    type: str
    value: str
    name: str
    description: str
    tags: List[str]
    attributes: Dict[str, Any]
    sources: List[Dict[str, Any]]
    created_at: str
    updated_at: str
    confidence: int
    is_malicious: bool
    risk_score: float


class EntitySearch(BaseModel):
    query: str = ""
    type: Optional[EntityType] = None
    tags: Optional[List[str]] = None
    is_malicious: Optional[bool] = None
    min_risk: float = 0.0
    limit: int = Field(default=100, le=1000)
    offset: int = 0


class CollectionJobCreate(BaseModel):
    collector: str
    target: str
    parameters: Dict[str, Any] = Field(default_factory=dict)


class CollectionJobResponse(BaseModel):
    id: str
    collector: str
    target: str
    parameters: Dict[str, Any]
    status: str
    started_at: Optional[str]
    completed_at: Optional[str]
    result_count: int
    error: Optional[str]
    metadata: Dict[str, Any]


class InvestigationCreate(BaseModel):
    name: str
    description: str = ""
    entity_ids: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    assignee: str = ""


class InvestigationResponse(BaseModel):
    id: str
    name: str
    description: str
    entity_ids: List[str]
    tags: List[str]
    status: str
    assignee: str
    created_at: str
    updated_at: str
    metadata: Dict[str, Any]


# ===== Entity Routes =====

@router.post("/entities", response_model=EntityResponse, status_code=201)
async def create_entity(entity: EntityCreate):
    """Create a new entity"""
    try:
        new_entity = Entity(
            id=str(uuid4()),
            type=entity.type,
            value=entity.value,
            name=entity.name,
            description=entity.description,
            tags=entity.tags,
            attributes=entity.attributes,
            confidence=entity.confidence
        )
        # Add source
        from src.core.models import Source, SourceType
        new_entity.add_source(Source(
            type=SourceType.MANUAL,
            name=entity.source_name,
            confidence=entity.confidence
        ))
        
        saved = db.upsert_entity(new_entity)
        return EntityResponse(**saved.to_dict())
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/entities", response_model=List[EntityResponse])
async def search_entities(
    query: str = "",
    type: Optional[str] = None,
    tags: Optional[str] = None,
    is_malicious: Optional[bool] = None,
    min_risk: float = 0.0,
    limit: int = Query(100, le=1000),
    offset: int = 0
):
    """Search entities with filters"""
    try:
        entity_type = EntityType(type) if type else None
        tag_list = tags.split(",") if tags else None
        
        entities = db.search_entities(
            entity_type=entity_type,
            tags=tag_list,
            is_malicious=is_malicious,
            min_risk=min_risk,
            limit=limit,
            offset=offset
        )
        
        # Filter by query if provided
        if query:
            query_lower = query.lower()
            entities = [e for e in entities if query_lower in e.value.lower() 
                       or query_lower in e.name.lower()
                       or query_lower in e.description.lower()]
        
        return [EntityResponse(**e.to_dict()) for e in entities]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/entities/{entity_id}", response_model=EntityResponse)
async def get_entity(entity_id: str):
    """Get entity by ID"""
    entity = db.get_entity(entity_id)
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")
    return EntityResponse(**entity.to_dict())


@router.get("/entities/{entity_id}/relationships")
async def get_entity_relationships(entity_id: str, direction: str = "both"):
    """Get relationships for an entity"""
    entity = db.get_entity(entity_id)
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")
    
    relationships = db.get_relationships(entity_id, direction)
    return [r.to_dict() for r in relationships]


@router.get("/entities/{entity_id}/observations")
async def get_entity_observations(entity_id: str, collector: Optional[str] = None):
    """Get observations for an entity"""
    entity = db.get_entity(entity_id)
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")
    
    observations = db.get_observations(entity_id, collector)
    return [obs.to_dict() for obs in observations]


# ===== Collector Routes =====

@router.get("/collectors")
async def list_collectors():
    """List all registered collectors"""
    collectors = CollectorRegistry.list_collectors()
    result = []
    for name in collectors:
        cls = CollectorRegistry.get_collector_class(name)
        result.append({
            "name": name,
            "description": cls.description,
            "version": cls.version,
            "supported_types": [t.value for t in cls.supported_types],
            "rate_limit": cls.rate_limit,
            "timeout": cls.timeout
        })
    return result


@router.get("/collectors/{collector_name}")
async def get_collector(collector_name: str):
    """Get collector details"""
    cls = CollectorRegistry.get_collector_class(collector_name)
    if not cls:
        raise HTTPException(status_code=404, detail="Collector not found")
    
    return {
        "name": name,
        "description": cls.description,
        "version": cls.version,
        "supported_types": [t.value for t in cls.supported_types],
        "rate_limit": cls.rate_limit,
        "timeout": cls.timeout
    }


@router.post("/collectors/{collector_name}/run", response_model=CollectionJobResponse)
async def run_collector(collector_name: str, job: CollectionJobCreate, background_tasks: BackgroundTasks):
    """Run a collector job"""
    cls = CollectorRegistry.get_collector_class(collector_name)
    if not cls:
        raise HTTPException(status_code=404, detail="Collector not found")
    
    # Create job record
    new_job = CollectionJob(
        id=str(uuid4()),
        collector=collector_name,
        target=job.target,
        parameters=job.parameters,
        status="pending"
    )
    db.upsert_collection_job(new_job)
    
    # Run in background
    async def run_collection():
        try:
            collector = cls()
            result = await collector.collect(job.target, **job.parameters)
            
            # Save entities
            for entity in result.entities:
                db.upsert_entity(entity)
            
            # Save observations
            for obs in result.observations:
                db.add_observation(obs)
            
            # Update job
            new_job.status = "completed" if not result.errors else "completed_with_errors"
            new_job.completed_at = datetime.utcnow()
            new_job.result_count = len(result.entities)
            new_job.error = "; ".join(result.errors) if result.errors else None
            new_job.metadata = result.metadata
            db.upsert_collection_job(new_job)
            
        except Exception as e:
            new_job.status = "failed"
            new_job.completed_at = datetime.utcnow()
            new_job.error = str(e)
            db.upsert_collection_job(new_job)
    
    background_tasks.add_task(run_collection)
    
    return CollectionJobResponse(**new_job.to_dict())


@router.get("/jobs/{job_id}", response_model=CollectionJobResponse)
async def get_job(job_id: str):
    """Get collection job status"""
    job = db.get_collection_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return CollectionJobResponse(**job.to_dict())


@router.get("/jobs")
async def list_jobs(
    collector: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
):
    """List collection jobs"""
    # TODO: Implement job listing with filters
    return []


# ===== Investigation Routes =====

@router.post("/investigations", response_model=InvestigationResponse, status_code=201)
async def create_investigation(inv: InvestigationCreate):
    """Create a new investigation"""
    investigation = Investigation(
        id=str(uuid4()),
        name=inv.name,
        description=inv.description,
        entity_ids=inv.entity_ids,
        tags=inv.tags,
        status="open",
        assignee=inv.assignee
    )
    saved = db.upsert_investigation(investigation)
    return InvestigationResponse(**saved.to_dict())


@router.get("/investigations", response_model=List[InvestigationResponse])
async def list_investigations(
    status: Optional[str] = None,
    assignee: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
):
    """List investigations"""
    # TODO: Implement with filters
    return []


@router.get("/investigations/{investigation_id}", response_model=InvestigationResponse)
async def get_investigation(investigation_id: str):
    """Get investigation by ID"""
    inv = db.get_investigation(investigation_id)
    if not inv:
        raise HTTPException(status_code=404, detail="Investigation not found")
    return InvestigationResponse(**inv.to_dict())


@router.post("/investigations/{investigation_id}/entities/{entity_id}")
async def add_entity_to_investigation(investigation_id: str, entity_id: str):
    """Add entity to investigation"""
    inv = db.get_investigation(investigation_id)
    if not inv:
        raise HTTPException(status_code=404, detail="Investigation not found")
    
    entity = db.get_entity(entity_id)
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")
    
    if entity_id not in inv.entity_ids:
        inv.entity_ids.append(entity_id)
        db.upsert_investigation(inv)
    
    return {"status": "added", "investigation_id": investigation_id, "entity_id": entity_id}


# ===== Analytics Routes =====

analytics_router = APIRouter(prefix="/analytics", tags=["analytics"])


@analytics_router.get("/stats")
async def get_stats():
    """Get platform statistics"""
    # TODO: Implement actual stats
    return {
        "entities_total": 0,
        "entities_by_type": {},
        "relationships_total": 0,
        "observations_total": 0,
        "investigations_open": 0,
        "investigations_closed": 0,
        "collectors_registered": len(CollectorRegistry.list_collectors())
    }


@analytics_router.get("/risk-distribution")
async def get_risk_distribution():
    """Get risk score distribution"""
    return {"bins": [], "counts": []}


@analytics_router.get("/timeline")
async def get_timeline(days: int = 30):
    """Get activity timeline"""
    return {"data": []}


# Include analytics router
router.include_router(analytics_router)