"""
OsintNeoAi Indexer: Entity Resolution Package
Path: C:\\OsintNeoAi\\workspaces\\osintneoai_indexer\\resolution\\__init__.py
Milestone: M3 (Entity Resolution & Vault Storage)
"""

from resolution.taxonomy import (
    CANONICAL_TARGETS,
    CanonicalEntity,
    EntityCategory,
    EntityMention,
    EventType,
    FinancialTransaction,
    PaymentMethod,
    Relationship,
    RelationshipType,
    TimelineEvent,
    calculate_confidence,
    get_category_prefix,
)
from resolution.entity_resolver import (
    DisjointSetUnion,
    EntityResolver,
    jaro_winkler_similarity,
    levenshtein_ratio,
)

__all__ = [
    "EntityCategory",
    "EventType",
    "PaymentMethod",
    "RelationshipType",
    "EntityMention",
    "CanonicalEntity",
    "TimelineEvent",
    "FinancialTransaction",
    "Relationship",
    "CANONICAL_TARGETS",
    "get_category_prefix",
    "calculate_confidence",
    "DisjointSetUnion",
    "EntityResolver",
    "jaro_winkler_similarity",
    "levenshtein_ratio",
]
