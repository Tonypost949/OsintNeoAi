"""
OsintNeoAi Indexer: Normalizers Package
Path: C:\\OsintNeoAi\\workspaces\\osintneoai_indexer\\normalizers\\__init__.py
Milestone: M2 (Deep Text Extraction & OCR Engine)

Exposes all normalizer dataclasses and conversion pipelines.
"""

from normalizers.date_normalizer import (
    NormalizedDate,
    normalize_date,
    extract_dates,
    normalize_dates_from_text,
)
from normalizers.financial_normalizer import (
    NormalizedFinancial,
    normalize_financial,
    extract_financials,
    extract_financial_amounts,
    format_currency,
)
from normalizers.case_normalizer import (
    NormalizedCaseCitation,
    extract_case_citations,
    extract_case_numbers,
)
from normalizers.entity_normalizer import (
    NormalizedEntity,
    normalize_entity,
    strip_corporate_suffix,
    soundex,
    double_metaphone,
    extract_correspondence_parties,
)

__all__ = [
    "NormalizedDate",
    "normalize_date",
    "extract_dates",
    "normalize_dates_from_text",
    "NormalizedFinancial",
    "normalize_financial",
    "extract_financials",
    "extract_financial_amounts",
    "format_currency",
    "NormalizedCaseCitation",
    "extract_case_citations",
    "extract_case_numbers",
    "NormalizedEntity",
    "normalize_entity",
    "strip_corporate_suffix",
    "soundex",
    "double_metaphone",
    "extract_correspondence_parties",
]
