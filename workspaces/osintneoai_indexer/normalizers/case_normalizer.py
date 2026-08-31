"""
OsintNeoAi Indexer: Legal Case & Statutory Citation Normalizer Module
Path: C:\\OsintNeoAi\\workspaces\\osintneoai_indexer\\normalizers\\case_normalizer.py
Milestone: M2 (Deep Text Extraction & OCR Engine) — Feature 10

Identifies, extracts, and canonicalizes federal court dockets, California Superior Court dockets,
law enforcement incident numbers, and statutory legal citations.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List, Optional, Set, Tuple

# ============================================================================
# 1. REGULAR EXPRESSIONS FOR DOCKETS AND CITATIONS
# ============================================================================

FEDERAL_DOCKET_RE = re.compile(
    r"""(?x)
    \b
    (?:Case\s*(?:No\.?|\#)?[:\s]*)?
    (?:(?P<district>\d{1,2}):)?
    (?P<year>\d{2})-
    (?P<type>cr|cv|mj|bk|mc|ap)-
    (?P<seq>\d{3,6})
    (?:-(?P<judge>[A-Za-z0-9\-]+))?
    \b
    """,
    re.IGNORECASE
)

CA_SUPERIOR_DOCKET_RE = re.compile(
    r"""(?x)
    \b
    (?:Case\s*(?:No\.?|\#)?[:\s]*)?
    (?P<county>30|\d{2})-
    (?P<year>\d{4})-
    (?P<seq>\d{6,8})-
    (?P<cat>[A-Za-z]{2})-
    (?P<subcat>[A-Za-z]{2})-
    (?P<dept>[A-Za-z0-9\-]+)
    \b
    """,
    re.IGNORECASE
)

POLICE_INCIDENT_RE = re.compile(
    r"""(?x)
    \b
    (?:
        (?:Case(?:\s*Number|\s*No\.?)?[:\s]*|[I1]-)
        (?P<police_case>[I1]?-\d{4}-\d{6}|\d{4}-\d{8})
      | (?:Summons\s*\#?[:\s]*)(?P<summons>\d{4}-\d{3,4}|\d{4}-S-\d{4}-\d{6})
      | (?:Levying\s*Officer\s*File\s*No\.?[:\s]*)(?P<levying>\d{10})
    )
    \b
    """,
    re.IGNORECASE
)

STATUTE_DEFINITIONS: List[Tuple[str, str, re.Pattern]] = [
    (
        "Cal. Gov. Code § 54220",
        "California",
        re.compile(r"Cal(?:ifornia)?\.?\s*Gov(?:ernment)?\.?\s*Code\s*§§?\s*54220(?:\s*et\s*seq\.?)?", re.IGNORECASE)
    ),
    (
        "Cal. Gov. Code § 54950",
        "California",
        re.compile(r"(?:Ralph\s*M\.\s*)?Brown\s*Act|Cal(?:ifornia)?\.?\s*Gov(?:ernment)?\.?\s*Code\s*§§?\s*54950", re.IGNORECASE)
    ),
    (
        "Cal. CCP § 170.6",
        "California",
        re.compile(r"Cal(?:ifornia)?\.?\s*C(?:ode\s*of\s*)?C(?:ivil)?\.?\s*P(?:roc(?:edure)?)?\.?\s*§§?\s*170\.6", re.IGNORECASE)
    ),
    (
        "Cal. Civil Code § 1946.2",
        "California",
        re.compile(r"Cal(?:ifornia)?\.?\s*Civ(?:il)?\.?\s*Code\s*§§?\s*1946\.2", re.IGNORECASE)
    ),
    (
        "18 U.S.C. § 1343",
        "Federal",
        re.compile(r"18\s*U\.?S\.?C\.?\s*§§?\s*1343", re.IGNORECASE)
    ),
    (
        "18 U.S.C. § 1346",
        "Federal",
        re.compile(r"18\s*U\.?S\.?C\.?\s*§§?\s*1346", re.IGNORECASE)
    ),
    (
        "18 U.S.C. § 1951",
        "Federal",
        re.compile(r"18\s*U\.?S\.?C\.?\s*§§?\s*1951", re.IGNORECASE)
    ),
    (
        "18 U.S.C. § 1961",
        "Federal",
        re.compile(r"18\s*U\.?S\.?C\.?\s*§§?\s*1961", re.IGNORECASE)
    ),
    (
        "18 U.S.C. § 1962",
        "Federal",
        re.compile(r"18\s*U\.?S\.?C\.?\s*§§?\s*1962(?:\([a-z0-9]+\))*", re.IGNORECASE)
    ),
    (
        "31 U.S.C. § 3729",
        "Federal",
        re.compile(r"31\s*U\.?S\.?C\.?\s*§§?\s*3729", re.IGNORECASE)
    ),
    (
        "42 U.S.C. § 1983",
        "Federal",
        re.compile(r"42\s*U\.?S\.?C\.?\s*§§?\s*1983", re.IGNORECASE)
    ),
    (
        "42 U.S.C. § 6901",
        "Federal",
        re.compile(r"42\s*U\.?S\.?C\.?\s*§§?\s*6901|RCRA", re.IGNORECASE)
    ),
    (
        "N.J.S.A. 2C:35-5",
        "New Jersey",
        re.compile(r"N\.?J\.?S\.?A\.?\s*2C:35-5", re.IGNORECASE)
    ),
    (
        "Anaheim City Council Resolution No. 2022-064",
        "City of Anaheim",
        re.compile(r"(?:Anaheim\s*(?:City\s*Council\s*)?)?Resolution\s*(?:No\.?)?\s*2022-064", re.IGNORECASE)
    ),
]


# ============================================================================
# 2. CORE NORMALIZATION & EXTRACTION ENGINE
# ============================================================================

@dataclass(frozen=True)
class NormalizedCaseCitation:
    """
    Immutable representation of an extracted court docket, police incident, or statutory citation.
    """
    raw_text: str                   # Original matched text
    canonical_id: str               # Normalized identifier (e.g. "8:23-cr-00108-CJC")
    citation_type: str              # "federal_docket", "state_docket", "police_incident", "statutory_citation", "municipal_resolution"
    jurisdiction: str               # "USDC CDCA (Santa Ana)", "California Superior Court (Orange County)", etc.
    case_type: Optional[str]        # "CRIMINAL", "CIVIL", "UNLAWFUL_DETAINER", etc.
    year: Optional[int]             # Filing year
    judge_initials: Optional[str]   # "CJC", "BAS", "TJB", "JWH-ADS"
    court_department: Optional[str] # "CJC", "C-32"
    confidence: float = 1.0
    start_char: int = 0
    end_char: int = 0

    @property
    def case_number(self) -> str:
        """Alias returning canonical_id."""
        return self.canonical_id


def extract_case_citations(text: str) -> List[NormalizedCaseCitation]:
    """
    Extracts all federal dockets, California Superior Court dockets, police incident numbers,
    and statutory citations from text.
    """
    if not text:
        return []

    citations: List[NormalizedCaseCitation] = []

    # 1. Federal Dockets
    for m in FEDERAL_DOCKET_RE.finditer(text):
        dist = m.group("district") or ""
        yr_short = int(m.group("year"))
        yr_full = 2000 + yr_short if yr_short < 50 else 1900 + yr_short
        case_type_raw = m.group("type").lower()
        seq = int(m.group("seq"))
        judge = m.group("judge") or ""

        type_mapping = {
            "cr": "CRIMINAL",
            "cv": "CIVIL",
            "mj": "MAGISTRATE",
            "bk": "BANKRUPTCY",
            "mc": "MISCELLANEOUS",
            "ap": "APPELLATE"
        }
        case_type = type_mapping.get(case_type_raw, "UNKNOWN")

        dist_prefix = f"{dist}:" if dist else ""
        judge_suffix = f"-{judge.upper()}" if judge else ""
        canonical = f"{dist_prefix}{yr_short:02d}-{case_type_raw}-{seq:05d}{judge_suffix}"

        if dist == "8":
            jurisdiction = "USDC CDCA (Santa Ana)"
        elif dist == "3":
            jurisdiction = "USDC DNJ (Trenton)"
        elif dist == "2":
            jurisdiction = "USDC CDCA (Los Angeles)"
        else:
            jurisdiction = "USDC"

        citations.append(
            NormalizedCaseCitation(
                raw_text=m.group(0).strip(),
                canonical_id=canonical,
                citation_type="federal_docket",
                jurisdiction=jurisdiction,
                case_type=case_type,
                year=yr_full,
                judge_initials=judge.upper() if judge else None,
                court_department=None,
                confidence=1.0,
                start_char=m.start(),
                end_char=m.end()
            )
        )

    # 2. California Superior Court Dockets
    for m in CA_SUPERIOR_DOCKET_RE.finditer(text):
        cnty = m.group("county")
        yr = int(m.group("year"))
        seq = int(m.group("seq"))
        cat = m.group("cat").upper()
        subcat = m.group("subcat").upper()
        dept = m.group("dept").upper()

        canonical = f"{cnty}-{yr:04d}-{seq:08d}-{cat}-{subcat}-{dept}"

        case_type_desc = "UNLAWFUL_DETAINER" if subcat == "UD" else f"{cat}_{subcat}"
        jurisdiction = "California Superior Court (Orange County)" if cnty == "30" else f"California Superior Court (County {cnty})"

        citations.append(
            NormalizedCaseCitation(
                raw_text=m.group(0).strip(),
                canonical_id=canonical,
                citation_type="state_docket",
                jurisdiction=jurisdiction,
                case_type=case_type_desc,
                year=yr,
                judge_initials=None,
                court_department=dept,
                confidence=1.0,
                start_char=m.start(),
                end_char=m.end()
            )
        )

    # 3. Police Incidents & Summons
    for m in POLICE_INCIDENT_RE.finditer(text):
        raw = m.group(0).strip()
        if m.group("police_case"):
            raw_case = m.group("police_case")
            canon = f"POLICE-CASE-{raw_case}"
            jurisdiction = "Ewing PD (NJ)" if "I-" in raw or "1-" in raw else "Hamilton Township PD (NJ)"
        elif m.group("summons"):
            canon = f"SUMMONS-{m.group('summons')}"
            jurisdiction = "Hamilton Township Municipal Court (NJ)"
        elif m.group("levying"):
            canon = f"OCSD-LEVY-{m.group('levying')}"
            jurisdiction = "Orange County Sheriff's Department"
        else:
            canon = raw
            jurisdiction = "Law Enforcement"

        citations.append(
            NormalizedCaseCitation(
                raw_text=raw,
                canonical_id=canon,
                citation_type="police_incident",
                jurisdiction=jurisdiction,
                case_type="INCIDENT_LOG",
                year=None,
                judge_initials=None,
                court_department=None,
                confidence=0.95,
                start_char=m.start(),
                end_char=m.end()
            )
        )

    # 4. Statutory Citations & Municipal Resolutions
    for canon_name, juris, pattern in STATUTE_DEFINITIONS:
        for m in pattern.finditer(text):
            is_res = "Resolution" in canon_name
            citations.append(
                NormalizedCaseCitation(
                    raw_text=m.group(0).strip(),
                    canonical_id=canon_name,
                    citation_type="municipal_resolution" if is_res else "statutory_citation",
                    jurisdiction=juris,
                    case_type="LEGISLATIVE" if is_res else "STATUTE",
                    year=2022 if "2022" in canon_name else None,
                    judge_initials=None,
                    court_department=None,
                    confidence=1.0,
                    start_char=m.start(),
                    end_char=m.end()
                )
            )

    return citations


def extract_case_numbers(text: str) -> List[str]:
    """
    Convenience helper extracting de-duplicated canonical case numbers and citations
    matching ExtractedRecord.case_numbers interface.
    """
    citations = extract_case_citations(text)
    output: List[str] = []
    seen: Set[str] = set()
    for cit in citations:
        if cit.canonical_id not in seen:
            seen.add(cit.canonical_id)
            output.append(cit.canonical_id)
    return output
