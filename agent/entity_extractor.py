"""
entity_extractor.py — Dossier Parser & Entity Extractor
=========================================================
Extracts names, addresses, dollar amounts, case numbers, and organizations
from uploaded dossier files (.pdf, .docx, .md, .txt).
Uses regex-based extraction (no API key required).
"""

import re
import os
from typing import Dict, List


def extract_from_file(filepath: str) -> Dict[str, List[str]]:
    """
    Extract entities from a file. Supports .pdf, .docx, .md, .txt.
    Returns dict with keys: names, addresses, amounts, case_numbers, organizations, keywords
    """
    ext = os.path.splitext(filepath)[1].lower()
    
    if ext == '.pdf':
        text = extract_pdf(filepath)
    elif ext == '.docx':
        text = extract_docx(filepath)
    elif ext in ('.md', '.txt'):
        text = extract_text(filepath)
    else:
        text = extract_text(filepath)  # Fallback
    
    return extract_entities(text)


def extract_pdf(filepath: str) -> str:
    """Extract text from a PDF file."""
    try:
        from pypdf import PdfReader
        reader = PdfReader(filepath)
        pages = []
        for page in reader.pages:
            t = page.extract_text()
            if t:
                pages.append(t)
        return "\n".join(pages)
    except ImportError:
        # Fallback: try PyPDF2
        try:
            import PyPDF2
            with open(filepath, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                pages = []
                for page in reader.pages:
                    t = page.extract_text()
                    if t:
                        pages.append(t)
                return "\n".join(pages)
        except ImportError:
            return f"[PDF extraction unavailable — install pypdf: pip install pypdf]"


def extract_docx(filepath: str) -> str:
    """Extract text from a DOCX file."""
    try:
        import docx
        doc = docx.Document(filepath)
        return "\n".join(p.text for p in doc.paragraphs if p.text.strip())
    except ImportError:
        return f"[DOCX extraction unavailable — install python-docx: pip install python-docx]"


def extract_text(filepath: str) -> str:
    """Extract text from a plain text / markdown file."""
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        return f.read()


# ============================================================================
#  ENTITY EXTRACTION (Regex-based)
# ============================================================================

# Common name patterns (First Last, with optional middle initial)
NAME_PATTERN = re.compile(
    r'\b([A-Z][a-z]{1,20}\s+(?:[A-Z]\.?\s+)?[A-Z][a-z]{1,20}(?:\s+(?:Jr|Sr|III|II|IV)\.?)?)\b'
)

# Addresses (street number + street name + city/state patterns)
ADDRESS_PATTERN = re.compile(
    r'\b(\d{1,6}\s+(?:[NSEW]\.?\s+)?(?:[A-Z][a-zA-Z]+\s*){1,4}'
    r'(?:St|Street|Ave|Avenue|Blvd|Boulevard|Dr|Drive|Ln|Lane|Rd|Road|Way|Ct|Court|Pl|Place|Cir|Circle)'
    r'\.?(?:\s*,?\s*(?:Suite|Ste|Apt|Unit|#)\s*\w+)?)\b',
    re.IGNORECASE
)

# Dollar amounts ($X,XXX.XX or $X.XM/B)
AMOUNT_PATTERN = re.compile(
    r'\$[\d,]+(?:\.\d{1,2})?(?:\s*(?:million|billion|M|B|K))?',
    re.IGNORECASE
)

# Federal case numbers (e.g., 8:26-cv-00348, 2:25-cr-00123-ABC)
CASE_NUMBER_PATTERN = re.compile(
    r'\b\d{1,2}:\d{2}-(?:cv|cr|mc|mj|ml)-\d{3,6}(?:-[A-Z]{2,5}(?:-[A-Z]{2,5})?)?\b',
    re.IGNORECASE
)

# Organization patterns (Inc, LLC, Corp, Foundation, etc.)
ORG_PATTERN = re.compile(
    r'\b([A-Z][A-Za-z\s&,]{2,50}\s+(?:Inc|LLC|Corp|Corporation|Foundation|Association|Society|'
    r'Group|Partners|Services|Solutions|Center|Centre|Institute|Company|Co|LLP|LP|Ltd)\.?)\b'
)

# High-priority keywords for smoking gun classification
SMOKING_GUN_KEYWORDS = [
    'indictment', 'convicted', 'conviction', 'guilty', 'guilty plea',
    'fraud', 'embezzlement', 'money laundering', 'bribery', 'corruption',
    'restitution', 'forfeiture', 'rico', 'conspiracy', 'obstruction',
    'whistleblower', 'qui tam', 'false claims', 'kickback',
    'sealed', 'grand jury', 'superseding', 'arraignment',
    'trafficking', 'exploitation', 'abuse', 'negligence',
    'double-billing', 'overbilling', 'misappropriation',
    'pay-to-play', 'no-bid', 'sole-source',
    'hexavalent chromium', 'toxic', 'contamination', 'environmental',
    'ceqa', 'dtsc', 'superfund',
]


def extract_entities(text: str) -> Dict[str, List[str]]:
    """
    Extract structured entities from raw text using regex patterns.
    Returns deduplicated lists of each entity type.
    """
    if not text:
        return {}

    # Extract each entity type
    names = list(dict.fromkeys(NAME_PATTERN.findall(text)))[:50]
    addresses = list(dict.fromkeys(ADDRESS_PATTERN.findall(text)))[:30]
    amounts = list(dict.fromkeys(AMOUNT_PATTERN.findall(text)))[:30]
    case_numbers = list(dict.fromkeys(CASE_NUMBER_PATTERN.findall(text)))[:20]
    organizations = list(dict.fromkeys(ORG_PATTERN.findall(text)))[:30]
    
    # Extract matching keywords found in the text
    text_lower = text.lower()
    keywords = [kw for kw in SMOKING_GUN_KEYWORDS if kw in text_lower]

    result = {}
    if names:
        result['names'] = names
    if addresses:
        result['addresses'] = addresses
    if amounts:
        result['amounts'] = amounts
    if case_numbers:
        result['case_numbers'] = case_numbers
    if organizations:
        result['organizations'] = organizations
    if keywords:
        result['keywords'] = keywords

    return result


def build_search_queries(entities: Dict[str, List[str]]) -> List[str]:
    """
    Build effective search queries from extracted entities.
    Combines names with keywords, addresses with organizations, etc.
    """
    queries = []

    names = entities.get('names', [])
    orgs = entities.get('organizations', [])
    keywords = entities.get('keywords', [])
    case_numbers = entities.get('case_numbers', [])
    addresses = entities.get('addresses', [])

    # Name-based queries (top 5 names)
    for name in names[:5]:
        queries.append(name)
        if keywords:
            queries.append(f"{name} {keywords[0]}")

    # Organization-based queries (top 3)
    for org in orgs[:3]:
        queries.append(org)
        if keywords:
            queries.append(f"{org} {keywords[0]}")

    # Case number queries
    for cn in case_numbers[:5]:
        queries.append(cn)

    # Address queries (top 3)
    for addr in addresses[:3]:
        queries.append(f'"{addr}"')

    # Keyword combo queries
    if keywords and names:
        queries.append(f"{names[0]} {' '.join(keywords[:3])}")

    return list(dict.fromkeys(queries))  # Deduplicate, preserve order
