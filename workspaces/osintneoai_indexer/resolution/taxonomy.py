"""
OsintNeoAi Indexer: Entity Taxonomy & Classification Schemas
Path: C:\\OsintNeoAi\\workspaces\\osintneoai_indexer\\resolution\\taxonomy.py
Milestone: M3 (Entity Resolution & Vault Storage) — Feature 12

Defines the 6 primary domain entity categories, timeline event types, payment methods,
relationship types, core dataclasses, confidence scoring calculations, and canonical targets.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple


# ============================================================================
# 1. ENUMERATIONS & TAXONOMY CLASSES
# ============================================================================

class EntityCategory(str, Enum):
    """
    Primary 6-Category Domain Entity Taxonomy + Fallback.
    """
    INDIVIDUAL = "INDIVIDUAL"
    MUNICIPAL_BODY = "MUNICIPAL_BODY"
    FINANCIAL_INSTITUTION = "FINANCIAL_INSTITUTION"
    PROPERTY_MANAGEMENT = "PROPERTY_MANAGEMENT"
    LEGAL_AGENCY = "LEGAL_AGENCY"
    COMMERCIAL_ENTITY = "COMMERCIAL_ENTITY"
    OTHER = "OTHER"


class EventType(str, Enum):
    """
    Timeline Event Classification Types.
    """
    JUDICIAL_FILING = "JUDICIAL_FILING"
    REGULATORY_NOTICE = "REGULATORY_NOTICE"
    LEGISLATIVE_ACTION = "LEGISLATIVE_ACTION"
    FINANCIAL_TRANSACTION = "FINANCIAL_TRANSACTION"
    INCIDENT_LOG = "INCIDENT_LOG"
    ARREST_SEARCH = "ARREST_SEARCH"
    RETALIATION_ACTION = "RETALIATION_ACTION"
    ENVIRONMENTAL_HAZARD = "ENVIRONMENTAL_HAZARD"
    OTHER = "OTHER"


class PaymentMethod(str, Enum):
    """
    Financial Payment Methods & Conduits.
    """
    WIRE = "WIRE"
    CHECK = "CHECK"
    CASH = "CASH"
    ESCROW = "ESCROW"
    GRANT = "GRANT"
    BRIBERY_CONDUIT = "BRIBERY_CONDUIT"
    INVOICE = "INVOICE"
    UNKNOWN = "UNKNOWN"


class RelationshipType(str, Enum):
    """
    Relational Graph Edge Classification.
    """
    OFFICER_OF = "OFFICER_OF"
    EMPLOYED_BY = "EMPLOYED_BY"
    CONTROLLED_BY = "CONTROLLED_BY"
    TRANSFERRED_FUNDS_TO = "TRANSFERRED_FUNDS_TO"
    SUED_BY = "SUED_BY"
    REPRESENTED_BY = "REPRESENTED_BY"
    CO_CONSPIRATOR_WITH = "CO_CONSPIRATOR_WITH"
    RETALIATED_AGAINST = "RETALIATED_AGAINST"
    SUBMITTED_BID_TO = "SUBMITTED_BID_TO"
    ISSUED_NOTICE_TO = "ISSUED_NOTICE_TO"
    CONNECTED_TO = "CONNECTED_TO"


# ============================================================================
# 2. CORE INTERFACE DATACLASSES
# ============================================================================

@dataclass
class EntityMention:
    """
    Specific occurrence of an entity mention in an extracted source document.
    """
    mention_id: str
    document_id: str
    raw_text: str
    entity_category: EntityCategory = EntityCategory.OTHER
    entity_id: Optional[str] = None
    char_offset_start: Optional[int] = None
    char_offset_end: Optional[int] = None
    page_number: int = 1
    context_snippet: Optional[str] = None
    confidence_score: float = 1.0
    extraction_method: str = "REGEX"  # 'REGEX', 'NER', 'MANUAL', 'HYBRID'


@dataclass
class CanonicalEntity:
    """
    Deduplicated, resolved canonical entity with alias mapping and metadata.
    """
    entity_id: str
    canonical_name: str
    entity_category: EntityCategory
    role_or_title: Optional[str] = None
    primary_jurisdiction: Optional[str] = None
    aliases: List[str] = field(default_factory=list)
    confidence_score: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    master_sheet_id: Optional[str] = None
    master_prefix: Optional[str] = None


@dataclass
class TimelineEvent:
    """
    Normalized chronological event record extracted from primary documents.
    """
    event_id: str
    document_id: Optional[str] = None
    event_date_iso: str = ""
    event_year: int = 0
    event_month: Optional[int] = None
    event_day: Optional[int] = None
    event_type: EventType = EventType.OTHER
    title: str = ""
    description: str = ""
    raw_snippet: Optional[str] = None
    primary_entity_id: Optional[str] = None
    location: Optional[str] = None
    jurisdiction: Optional[str] = None
    confidence_score: float = 1.0
    chronological_rank: Optional[int] = None


@dataclass
class FinancialTransaction:
    """
    Structured monetary transaction or conduit disbursement record.
    """
    transaction_id: str
    document_id: Optional[str] = None
    event_id: Optional[str] = None
    transaction_date_iso: str = ""
    amount: float = 0.0
    currency: str = "USD"
    sender_entity_id: Optional[str] = None
    recipient_entity_id: Optional[str] = None
    sender_raw_text: Optional[str] = None
    recipient_raw_text: Optional[str] = None
    payment_method: PaymentMethod = PaymentMethod.UNKNOWN
    account_or_check_num: Optional[str] = None
    transaction_purpose: Optional[str] = None
    is_predicate_act: bool = False
    raw_snippet: Optional[str] = None


@dataclass
class Relationship:
    """
    Directed or bidirectional graph relationship edge between two canonical entities.
    """
    relationship_id: str
    source_entity_id: str
    target_entity_id: str
    relationship_type: RelationshipType
    direction: str = "DIRECTED"
    confidence: float = 1.0
    valid_from: Optional[str] = None
    valid_to: Optional[str] = None
    source_document_id: Optional[str] = None
    evidence_summary: Optional[str] = None


# ============================================================================
# 3. CONFIDENCE SCORING & PREFIX HELPERS
# ============================================================================

def get_category_prefix(category: EntityCategory) -> str:
    """Returns canonical prefix for entity IDs based on category (backward-compatible)."""
    prefix_map = {
        EntityCategory.INDIVIDUAL: "ENT-IND",
        EntityCategory.MUNICIPAL_BODY: "ENT-MUN",
        EntityCategory.FINANCIAL_INSTITUTION: "ENT-FIN",
        EntityCategory.PROPERTY_MANAGEMENT: "ENT-PRP",
        EntityCategory.LEGAL_AGENCY: "ENT-LEG",
        EntityCategory.COMMERCIAL_ENTITY: "ENT-COM",
        EntityCategory.OTHER: "ENT-OTH",
    }
    return prefix_map.get(category, "ENT-OTH")


# Master OSINT Sheet (40-Tab) Registry Prefix Mapping
MASTER_OSINT_PREFIX_MAP: Dict[Union[EntityCategory, EventType, str], str] = {
    EntityCategory.INDIVIDUAL: "PER",
    "INDIVIDUAL": "PER",
    "PERSON": "PER",
    "PEOPLE": "PER",
    "PER": "PER",
    EntityCategory.MUNICIPAL_BODY: "GOV",
    "MUNICIPAL_BODY": "GOV",
    "GOVERNMENT": "GOV",
    "GOV": "GOV",
    "CONTRACTOR": "CON",
    "CONSULTING": "CON",
    "CON": "CON",
    EntityCategory.PROPERTY_MANAGEMENT: "SHL",
    "PROPERTY_MANAGEMENT": "SHL",
    "SHELL_COMPANY": "SHL",
    "SHL": "SHL",
    EntityCategory.FINANCIAL_INSTITUTION: "FIN",
    "FINANCIAL_INSTITUTION": "FIN",
    "FIN": "FIN",
    EventType.JUDICIAL_FILING: "EV",
    EventType.REGULATORY_NOTICE: "EV",
    EventType.LEGISLATIVE_ACTION: "EV",
    "EVENT": "EV",
    "TIMELINE": "EV",
    "EV": "EV",
    "RICO": "RICO",
    "RICO_ENTERPRISE": "RICO",
    "TOXIC_SITE": "TOX",
    "ENVIRONMENTAL_HAZARD": "TOX",
    "TOX": "TOX",
    "UNKNOWN_PERSON": "UP",
    "UNIDENTIFIED": "UP",
    "UP": "UP",
    "NON_PROFIT": "NP",
    "NP": "NP",
    EntityCategory.LEGAL_AGENCY: "LEG",
    "LEGAL_AGENCY": "LEG",
    "LEG": "LEG",
    EntityCategory.COMMERCIAL_ENTITY: "COM",
    "COMMERCIAL_ENTITY": "COM",
    "COM": "COM",
    EntityCategory.OTHER: "ENT",
    "OTHER": "ENT",
}

VALID_MASTER_OSINT_PREFIXES: Set[str] = {
    "PER", "GOV", "CON", "SHL", "EV", "RICO", "TOX", "UP",
    "ADDR", "PHONE", "EMAIL", "LEG", "TL", "TRAF", "FIN", "FAC", "NP", "COM", "ENT"
}


def get_master_osint_prefix(category_or_type: Union[EntityCategory, EventType, str]) -> str:
    """
    Returns the normalized Master OSINT Sheet entity ID prefix
    (e.g., 'PER', 'GOV', 'CON', 'SHL', 'EV', 'RICO', 'TOX', 'UP').
    """
    if isinstance(category_or_type, (EntityCategory, EventType)):
        key = category_or_type
    else:
        key = str(category_or_type).upper().strip()
    return MASTER_OSINT_PREFIX_MAP.get(key, "ENT")


def format_master_osint_id(prefix_or_category: Union[EntityCategory, EventType, str], identifier: Union[int, str]) -> str:
    """
    Formats normalized Master OSINT Sheet entity ID (e.g. 'PER-001', 'GOV-002', 'SHL-012').
    """
    prefix = get_master_osint_prefix(prefix_or_category) if prefix_or_category not in VALID_MASTER_OSINT_PREFIXES else str(prefix_or_category)
    if isinstance(identifier, int):
        return f"{prefix}-{identifier:03d}"
    clean_id = str(identifier).strip()
    if clean_id.isdigit():
        return f"{prefix}-{int(clean_id):03d}"
    return f"{prefix}-{clean_id}"


def is_valid_master_osint_id(entity_id: str) -> bool:
    """
    Validates whether an entity ID matches Master OSINT Sheet registry format (e.g. 'PER-001', 'GOV-123', 'EV-048').
    """
    if not entity_id or "-" not in entity_id:
        return False
    parts = entity_id.split("-", 1)
    return parts[0].upper() in VALID_MASTER_OSINT_PREFIXES and len(parts[1]) > 0


def calculate_confidence(
    string_similarity: float,
    shared_docket: bool = False,
    shared_address: bool = False,
    shared_agency: bool = False,
    exact_match: bool = False,
) -> float:
    """
    Computes contextual entity resolution confidence score.
    Formula: Confidence = 0.50 * JaroWinkler + 0.20 * Docket + 0.15 * Address + 0.15 * Agency
    """
    if exact_match:
        return 1.0

    score = (
        0.50 * max(0.0, min(1.0, string_similarity))
        + 0.20 * (1.0 if shared_docket else 0.0)
        + 0.15 * (1.0 if shared_address else 0.0)
        + 0.15 * (1.0 if shared_agency else 0.0)
    )
    return round(min(1.0, max(0.0, score)), 4)


# ============================================================================
# 4. CANONICAL TARGETS & DOMAIN KNOWLEDGE BASE
# ============================================================================

CANONICAL_TARGETS: List[Dict[str, Any]] = [
    # 1. Individuals (PER-###)
    {
        "canonical_name": "Harry Sidhu",
        "entity_category": EntityCategory.INDIVIDUAL,
        "master_sheet_id": "PER-001",
        "master_prefix": "PER",
        "role_or_title": "Former Mayor of Anaheim",
        "primary_jurisdiction": "Anaheim / CDCA",
        "aliases": ["Harry Singh Sidhu", "Mayor Harry Sidhu", "Mayor Sidhu", "H. Sidhu", "Sidhu"],
        "metadata": {"case_numbers": ["8:23-cr-00108-CJC"]}
    },
    {
        "canonical_name": "Todd Ament",
        "entity_category": EntityCategory.INDIVIDUAL,
        "master_sheet_id": "PER-002",
        "master_prefix": "PER",
        "role_or_title": "Former CEO Anaheim Chamber of Commerce",
        "primary_jurisdiction": "Anaheim / CDCA",
        "aliases": ["Todd Stephen Ament", "Todd Ament", "T. Ament", "Ament"],
        "metadata": {"case_numbers": ["8:22-cr-00078-CJC"]}
    },
    {
        "canonical_name": "Melahat Rafiei",
        "entity_category": EntityCategory.INDIVIDUAL,
        "master_sheet_id": "PER-003",
        "master_prefix": "PER",
        "role_or_title": "Political Consultant & DNC Member",
        "primary_jurisdiction": "Anaheim / CDCA",
        "aliases": ["Melahat Rafiei", "M. Rafiei", "Rafiei"],
        "metadata": {"case_numbers": ["8:23-cr-00009-CJC"]}
    },
    {
        "canonical_name": "Jeffrey Flint",
        "entity_category": EntityCategory.INDIVIDUAL,
        "master_sheet_id": "PER-004",
        "master_prefix": "PER",
        "role_or_title": "Political Consultant / Lobbyist",
        "primary_jurisdiction": "Anaheim / CDCA",
        "aliases": ["Jeff Flint", "Jeffrey Flint", "J. Flint"],
        "metadata": {"firm": "FPS Strategies LLC"}
    },
    {
        "canonical_name": "Brian Adkins",
        "entity_category": EntityCategory.INDIVIDUAL,
        "master_sheet_id": "PER-005",
        "master_prefix": "PER",
        "role_or_title": "FBI Special Agent",
        "primary_jurisdiction": "CDCA",
        "aliases": ["Special Agent Brian Adkins", "SA Brian Adkins", "Brian Adkins"],
        "metadata": {"agency": "FBI CDCA"}
    },
    {
        "canonical_name": "Bradley H. Zartman",
        "entity_category": EntityCategory.INDIVIDUAL,
        "master_sheet_id": "PER-006",
        "master_prefix": "PER",
        "role_or_title": "FBI Special Agent",
        "primary_jurisdiction": "USDC D.N.J.",
        "aliases": ["Special Agent Bradley H. Zartman", "SA Bradley H. Zartman", "Bradley Zartman"],
        "metadata": {"agency": "FBI D.N.J.", "case_numbers": ["3:20-mj-05007-TJB"]}
    },
    {
        "canonical_name": "Carmen Luege",
        "entity_category": EntityCategory.INDIVIDUAL,
        "master_sheet_id": "PER-007",
        "master_prefix": "PER",
        "role_or_title": "Judge of California Superior Court",
        "primary_jurisdiction": "Orange County CJC",
        "aliases": ["Judge Carmen Luege", "Hon. Carmen Luege", "Carmen Luege"],
        "metadata": {"court": "California Superior Court Orange County CJC"}
    },
    {
        "canonical_name": "Richard S. Sontag",
        "entity_category": EntityCategory.INDIVIDUAL,
        "master_sheet_id": "PER-008",
        "master_prefix": "PER",
        "role_or_title": "Eviction Attorney",
        "primary_jurisdiction": "Orange County CJC",
        "aliases": ["Richard Sontag", "Richard S. Sontag, Esq.", "R. S. Sontag"],
        "metadata": {"firm": "Wallace, Richardson, Sontag & Le LLP"}
    },
    {
        "canonical_name": "Anthony DiMarcello",
        "entity_category": EntityCategory.INDIVIDUAL,
        "master_sheet_id": "PER-009",
        "master_prefix": "PER",
        "role_or_title": "Tenant / Defendant / Relator",
        "primary_jurisdiction": "Orange County / NJ",
        "aliases": ["Anthony DiMarcello", "Anthony C. DiMarcello", "A. DiMarcello", "DiMarcello"],
        "metadata": {"case_numbers": ["30-2021-01201327-CL-UD-CJC"]}
    },

    # 2. Municipal & Government Bodies (GOV-###)
    {
        "canonical_name": "City of Anaheim",
        "entity_category": EntityCategory.MUNICIPAL_BODY,
        "master_sheet_id": "GOV-001",
        "master_prefix": "GOV",
        "role_or_title": "Charter City / Municipal Corporation & City Council",
        "primary_jurisdiction": "Orange County, CA",
        "aliases": [
            "Anaheim",
            "City of Anaheim, California",
            "Anaheim City",
            "Anaheim City Council",
            "City Council of Anaheim",
            "Anaheim Council",
        ],
        "metadata": {"entity_type": "Municipality", "resolution": "Resolution No. 2022-064"}
    },
    {
        "canonical_name": "Anaheim Chamber of Commerce",
        "entity_category": EntityCategory.MUNICIPAL_BODY,
        "master_sheet_id": "GOV-002",
        "master_prefix": "GOV",
        "role_or_title": "Chamber of Commerce",
        "primary_jurisdiction": "Anaheim, CA",
        "aliases": ["Anaheim Chamber", "ACC"],
        "metadata": {"leader": "Todd Ament"}
    },
    {
        "canonical_name": "Visit Anaheim",
        "entity_category": EntityCategory.MUNICIPAL_BODY,
        "master_sheet_id": "GOV-003",
        "master_prefix": "GOV",
        "role_or_title": "Tourism Bureau / DMO",
        "primary_jurisdiction": "Anaheim, CA",
        "aliases": ["Anaheim Tourism Improvement District", "ATID", "Visit Anaheim Inc"],
        "metadata": {"funding": "ARPA grant conduit"}
    },

    # 3. Financial Institutions & Conduits (SHL-### / CON-###)
    {
        "canonical_name": "TA Group LLC",
        "entity_category": EntityCategory.FINANCIAL_INSTITUTION,
        "master_sheet_id": "SHL-001",
        "master_prefix": "SHL",
        "role_or_title": "Conduit Entity / Consulting Firm",
        "primary_jurisdiction": "California",
        "aliases": ["TA Group", "T.A. Group LLC", "TA Group L.L.C."],
        "metadata": {"owner": "Todd Ament"}
    },
    {
        "canonical_name": "FPS Strategies LLC",
        "entity_category": EntityCategory.FINANCIAL_INSTITUTION,
        "master_sheet_id": "CON-001",
        "master_prefix": "CON",
        "role_or_title": "Political Consulting / PAC Conduit",
        "primary_jurisdiction": "California",
        "aliases": ["FPS Strategies", "FPS Strategies L.L.C."],
        "metadata": {"owner": "Jeffrey Flint"}
    },
    {
        "canonical_name": "SRB Management Escrow",
        "entity_category": EntityCategory.FINANCIAL_INSTITUTION,
        "master_sheet_id": "SHL-002",
        "master_prefix": "SHL",
        "role_or_title": "Stadium Land Sale Escrow Depository",
        "primary_jurisdiction": "Anaheim / CA",
        "aliases": ["SRB Management LLC", "SRB Escrow", "SRB Management"],
        "metadata": {"deal_amount": "$320M"}
    },
    {
        "canonical_name": "Progressive Solutions Consulting",
        "entity_category": EntityCategory.FINANCIAL_INSTITUTION,
        "master_sheet_id": "CON-002",
        "master_prefix": "CON",
        "role_or_title": "Political Consulting Firm",
        "primary_jurisdiction": "California",
        "aliases": ["Progressive Solutions", "Progressive Solutions LLC"],
        "metadata": {"owner": "Melahat Rafiei"}
    },

    # 4. Property Management & Real Estate (SHL-### / NP-### / ADDR-### / FAC-###)
    {
        "canonical_name": "Woodbridge Meadows Apartments LLC",
        "entity_category": EntityCategory.PROPERTY_MANAGEMENT,
        "master_sheet_id": "SHL-003",
        "master_prefix": "SHL",
        "role_or_title": "Apartment Complex / Eviction Plaintiff",
        "primary_jurisdiction": "Irvine / Orange County",
        "aliases": ["Woodbridge Meadows", "Woodbridge Meadows Apts LLC", "Woodbridge Meadows Apartments"],
        "metadata": {"address": "8 Lakeview, Irvine, CA"}
    },
    {
        "canonical_name": "Mercy House Living Centers",
        "entity_category": EntityCategory.PROPERTY_MANAGEMENT,
        "master_sheet_id": "NP-001",
        "master_prefix": "NP",
        "role_or_title": "Homeless Shelter / Housing Non-Profit",
        "primary_jurisdiction": "Orange County, CA",
        "aliases": ["Mercy House", "Mercy House Living Centers Inc"],
        "metadata": {"facilities": ["17631 Cameron Lane", "3125 W 5th St Santa Ana"]}
    },
    {
        "canonical_name": "1456 Cedar Lane",
        "entity_category": EntityCategory.PROPERTY_MANAGEMENT,
        "master_sheet_id": "ADDR-001",
        "master_prefix": "ADDR",
        "role_or_title": "Residential Parcel / Search Target",
        "primary_jurisdiction": "Hamilton Township, NJ",
        "aliases": ["1456 Cedar Ln", "1456 Cedar Lane, Hamilton, NJ"],
        "metadata": {"incident_case": "2019-00053723"}
    },
    {
        "canonical_name": "Angel Stadium 150-Acre Parcel",
        "entity_category": EntityCategory.PROPERTY_MANAGEMENT,
        "master_sheet_id": "FAC-001",
        "master_prefix": "FAC",
        "role_or_title": "Municipal Stadium Land Asset",
        "primary_jurisdiction": "Anaheim, CA",
        "aliases": ["Angel Stadium Site", "2000 E Gene Autry Way", "Angel Stadium Land"],
        "metadata": {"statute": "Surplus Land Act (Gov. Code § 54220)"}
    },

    # 5. Legal & Regulatory Agencies (LEG-### / GOV-###)
    {
        "canonical_name": "USDC CDCA",
        "entity_category": EntityCategory.LEGAL_AGENCY,
        "master_sheet_id": "LEG-001",
        "master_prefix": "LEG",
        "role_or_title": "United States District Court Central District of California",
        "primary_jurisdiction": "Santa Ana / Los Angeles, CA",
        "aliases": ["United States District Court for the Central District of California", "CDCA", "U.S. District Court CDCA"],
        "metadata": {"federal_circuit": "9th Circuit"}
    },
    {
        "canonical_name": "USDC D.N.J.",
        "entity_category": EntityCategory.LEGAL_AGENCY,
        "master_sheet_id": "LEG-002",
        "master_prefix": "LEG",
        "role_or_title": "United States District Court District of New Jersey",
        "primary_jurisdiction": "Trenton, NJ",
        "aliases": ["United States District Court for the District of New Jersey", "DNJ", "U.S. District Court DNJ"],
        "metadata": {"federal_circuit": "3rd Circuit"}
    },
    {
        "canonical_name": "California Superior Court (Orange County CJC)",
        "entity_category": EntityCategory.LEGAL_AGENCY,
        "master_sheet_id": "LEG-003",
        "master_prefix": "LEG",
        "role_or_title": "Superior Court of California County of Orange Central Justice Center",
        "primary_jurisdiction": "Santa Ana, CA",
        "aliases": ["Orange County Superior Court", "OC Superior Court", "CJC", "Central Justice Center"],
        "metadata": {"county": "Orange County"}
    },
    {
        "canonical_name": "Federal Bureau of Investigation",
        "entity_category": EntityCategory.LEGAL_AGENCY,
        "master_sheet_id": "GOV-004",
        "master_prefix": "GOV",
        "role_or_title": "Federal Law Enforcement Agency",
        "primary_jurisdiction": "Federal / Multi-State",
        "aliases": ["FBI", "FBI CDCA", "FBI DNJ", "Federal Bureau of Investigation CDCA"],
        "metadata": {"squad": "Public Corruption / OC Squad"}
    },
    {
        "canonical_name": "California Department of Housing and Community Development",
        "entity_category": EntityCategory.LEGAL_AGENCY,
        "master_sheet_id": "GOV-005",
        "master_prefix": "GOV",
        "role_or_title": "State Housing Regulatory Agency",
        "primary_jurisdiction": "California",
        "aliases": ["California HCD", "HCD", "Dept of Housing and Community Development"],
        "metadata": {"enforcement": "Surplus Land Act Notice of Violation"}
    },
    {
        "canonical_name": "Hamilton Township Police Division",
        "entity_category": EntityCategory.LEGAL_AGENCY,
        "master_sheet_id": "GOV-006",
        "master_prefix": "GOV",
        "role_or_title": "Municipal Police Department",
        "primary_jurisdiction": "Hamilton Township, Mercer County, NJ",
        "aliases": ["Hamilton Police", "Hamilton Twp Police", "HTPD"],
        "metadata": {"cases": ["2019-00053723", "2020-00008897"]}
    },
    {
        "canonical_name": "Ewing Police Department",
        "entity_category": EntityCategory.LEGAL_AGENCY,
        "master_sheet_id": "GOV-007",
        "master_prefix": "GOV",
        "role_or_title": "Municipal Police Department",
        "primary_jurisdiction": "Ewing Township, Mercer County, NJ",
        "aliases": ["Ewing Police", "EPD", "Ewing Twp Police"],
        "metadata": {"cases": ["I-2019-001222"]}
    },

    # 6. Commercial Entities (CON-### / COM-###)
    {
        "canonical_name": "Wallace, Richardson, Sontag & Le LLP",
        "entity_category": EntityCategory.COMMERCIAL_ENTITY,
        "master_sheet_id": "CON-003",
        "master_prefix": "CON",
        "role_or_title": "Eviction Litigation Law Firm",
        "primary_jurisdiction": "California",
        "aliases": ["Wallace Richardson Sontag & Le", "WRSL", "Wallace Richardson", "Wallace, Richardson"],
        "metadata": {"practice": "Unlawful Detainer / Eviction"}
    },
    {
        "canonical_name": "JL Group LLC",
        "entity_category": EntityCategory.COMMERCIAL_ENTITY,
        "master_sheet_id": "CON-004",
        "master_prefix": "CON",
        "role_or_title": "Independent Forensic Investigative Firm",
        "primary_jurisdiction": "California",
        "aliases": ["JL Group", "JL Investigation", "JL Investigations LLC"],
        "metadata": {"deliverable": "Anaheim Corruption Forensic Audit Report"}
    },
    {
        "canonical_name": "Quantum Auto Dismantler",
        "entity_category": EntityCategory.COMMERCIAL_ENTITY,
        "master_sheet_id": "COM-001",
        "master_prefix": "COM",
        "role_or_title": "Automotive Dismantler & Parts Logistics",
        "primary_jurisdiction": "Santa Ana, CA / NJ",
        "aliases": ["Quantum Auto", "Quantum Dismantlers", "Quantum Auto Dismantlers"],
        "metadata": {"invoices": ["#14098"]}
    },
]
