"""
Pydantic v2 DTO Data Models for OSINT Graph Correlation Engine.
"""
from typing import Dict, Any, List, Optional, Tuple
from pydantic import BaseModel, Field, ConfigDict


class BaseDTO(BaseModel):
    model_config = ConfigDict(
        frozen=False,
        extra="ignore",
        str_strip_whitespace=True
    )


class NormalizedAddressDTO(BaseDTO):
    street: str = Field(description="Normalized street address (USPS standardized, units stripped)")
    city: str = Field(description="Normalized city name in uppercase")
    state: str = Field(description="2-letter uppercase state code")
    zip_code: str = Field(description="5-digit padded ZIP code")
    unit: Optional[str] = Field(default=None, description="Extracted suite/unit/apt designation if present")
    normalized_str: str = Field(description="Canonical single-line normalized address string")
    address_hash: str = Field(description="SHA256 hex hash of normalized_str for graph node ID")


class NormalizedNameDTO(BaseDTO):
    raw_name: str = Field(description="Original uncleaned raw entity name")
    clean_name: str = Field(description="Title-cased clean entity name with corp suffixes stripped")
    core_key: str = Field(description="Uppercase core key with stop words stripped for candidate blocking")
    soundex: str = Field(description="Standard 4-character Soundex phonetic code")
    double_metaphone: Tuple[str, str] = Field(description="Tuple of (primary, secondary) Double Metaphone codes")
    is_business: bool = Field(default=True, description="Whether entity was processed as a business")


class NodeDTO(BaseDTO):
    node_id: str = Field(description="Unique node identifier (e.g. SHA256 hash or entity ID)")
    node_type: str = Field(description="Node category: BUSINESS, PERSON, ADDRESS, LOAN, PROPERTY, NONPROFIT")
    label: str = Field(description="Human-readable primary display label")
    normalized_label: str = Field(description="Normalized label string for searching and matching")
    address_id: Optional[str] = Field(default=None, description="Linked address node ID or SHA256 address hash")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Flexible metadata attributes")


class EdgeDTO(BaseDTO):
    edge_id: str = Field(description="Unique edge identifier")
    source_id: str = Field(description="Source node ID")
    target_id: str = Field(description="Target node ID")
    edge_type: str = Field(description="Relationship type: OWNS, REGISTERED_AT, APPLIED_FOR, ASSOCIATED_WITH, LOCATED_AT")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Link confidence score between 0.0 and 1.0")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Edge metadata attributes")


class ClusterDTO(BaseDTO):
    cluster_id: str = Field(description="Unique cluster identifier")
    node_ids: List[str] = Field(default_factory=list, description="List of node IDs in cluster")
    size: int = Field(default=0, description="Total node count in cluster")
    risk_score: float = Field(default=0.0, ge=0.0, description="Calculated cluster risk score")
    primary_address: Optional[str] = Field(default=None, description="Primary address hub label if applicable")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Summary analytics for cluster")


class MatchResultDTO(BaseDTO):
    node_a_id: str = Field(description="First candidate node ID")
    node_b_id: str = Field(description="Second candidate node ID")
    match_score: float = Field(..., ge=0.0, le=1.0, description="Fuzzy or exact similarity score")
    match_type: str = Field(description="Match mechanism: EXACT_NAME, FUZZY_NAME, EXACT_ADDRESS, PHONETIC")
    relationship_type: str = Field(default="ASSOCIATED_WITH", description="Suggested relationship edge type")
    details: Dict[str, Any] = Field(default_factory=dict, description="Match computation details")
