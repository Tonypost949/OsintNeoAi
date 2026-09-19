"""Evidence-first claim verification primitives for OSINTNeoAI.

This module is deterministic: it never promotes an AI-generated statement
to VERIFIED without explicit evidence records.
"""
from __future__ import annotations
from dataclasses import asdict, dataclass, field
from enum import Enum
from hashlib import sha256
from typing import Iterable, Optional

class ClaimStatus(str, Enum):
    OBSERVED = "OBSERVED"
    DERIVED = "DERIVED"
    SUPPORTED = "SUPPORTED"
    PARTIALLY_SUPPORTED = "PARTIALLY_SUPPORTED"
    CONTRADICTED = "CONTRADICTED"
    UNRESOLVED = "UNRESOLVED"
    UNSUPPORTED = "UNSUPPORTED"
    ALLEGATION = "ALLEGATION"
    HYPOTHESIS = "HYPOTHESIS"

@dataclass(frozen=True)
class Evidence:
    evidence_id: str
    source_title: str
    source_url: str = ""
    source_type: str = "unknown"
    page: Optional[int] = None
    quote: str = ""
    retrieved_at: str = ""
    content_sha256: str = ""
    supports: bool = True
    independent_source_id: str = ""

    def validate(self) -> None:
        if not self.evidence_id or not self.source_title:
            raise ValueError("Evidence requires evidence_id and source_title")
        if self.page is not None and self.page < 1:
            raise ValueError("page must be >= 1")
        if self.content_sha256 and len(self.content_sha256) != 64:
            raise ValueError("content_sha256 must be a SHA-256 hex digest")

    @staticmethod
    def hash_content(content: bytes) -> str:
        return sha256(content).hexdigest()

@dataclass
class Claim:
    claim_id: str
    text: str
    status: ClaimStatus = ClaimStatus.UNRESOLVED
    evidence: list[Evidence] = field(default_factory=list)
    what_source_establishes: list[str] = field(default_factory=list)
    what_source_does_not_establish: list[str] = field(default_factory=list)
    human_verified: bool = False
    reviewer: str = ""

    def add_evidence(self, item: Evidence) -> None:
        item.validate()
        self.evidence.append(item)

    def adjudicate(self) -> ClaimStatus:
        """Conservative evidence gate; it never invents evidence."""
        if not self.evidence:
            self.status = ClaimStatus.UNSUPPORTED
            return self.status
        supporting = [e for e in self.evidence if e.supports]
        contradicting = [e for e in self.evidence if not e.supports]
        if supporting and contradicting:
            self.status = ClaimStatus.UNRESOLVED
        elif supporting:
            self.status = ClaimStatus.SUPPORTED
        else:
            self.status = ClaimStatus.CONTRADICTED
        return self.status

    def can_be_presented_as_fact(self) -> bool:
        return self.status == ClaimStatus.SUPPORTED and self.human_verified

    def to_dict(self) -> dict:
        result = asdict(self)
        result["status"] = self.status.value
        result["evidence"] = [asdict(e) for e in self.evidence]
        return result

def verify_claims(claims: Iterable[Claim]) -> list[Claim]:
    for claim in claims:
        claim.adjudicate()
    return list(claims)