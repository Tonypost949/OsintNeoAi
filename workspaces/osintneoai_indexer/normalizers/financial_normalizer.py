"""
OsintNeoAi Indexer: Financial & Monetary Normalizer Module
Path: C:\\OsintNeoAi\\workspaces\\osintneoai_indexer\\normalizers\\financial_normalizer.py
Milestone: M2 (Deep Text Extraction & OCR Engine) — Feature 9

Extracts and standardizes monetary sums to dual float and exact integer cents using Decimal arithmetic.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
from typing import Any, Dict, List, Optional, Tuple

# ============================================================================
# 1. CURRENCY SYMBOL MAPPING & MULTIPLIERS
# ============================================================================

CURRENCY_SYMBOL_MAP: Dict[str, str] = {
    "$": "USD",
    "€": "EUR",
    "£": "GBP",
    "¥": "JPY",
    "₩": "KRW",
    "₹": "INR",
    "USD": "USD",
    "EUR": "EUR",
    "GBP": "GBP",
    "CAD": "CAD",
    "AUD": "AUD",
}

MULTIPLIER_VALUES: Dict[str, Decimal] = {
    "k": Decimal("1000"),
    "thousand": Decimal("1000"),
    "thousands": Decimal("1000"),
    "grand": Decimal("1000"),
    "m": Decimal("1000000"),
    "mil": Decimal("1000000"),
    "million": Decimal("1000000"),
    "millions": Decimal("1000000"),
    "b": Decimal("1000000000"),
    "bil": Decimal("1000000000"),
    "billion": Decimal("1000000000"),
    "billions": Decimal("1000000000"),
    "t": Decimal("1000000000000"),
    "trillion": Decimal("1000000000000"),
    "trillions": Decimal("1000000000000"),
}

# ============================================================================
# 2. FINANCIAL REGEX PATTERNS
# ============================================================================

# Multi-character multiplier names precede single character tokens (e.g. million before m)
FINANCIAL_REGEX = re.compile(
    r"""(?x)
    (?P<sign>[-–—+])?
    (?P<paren>\()?\s*
    (?:(?P<currency>[\$€£¥₩₹]|USD|EUR|GBP|CAD|AUD)\s*)?
    (?P<number>\d+(?:,\d{3})*(?:\.\d+)?|\d*\.\d+)\s*
    (?P<multiplier>trillions?|billions?|millions?|thousands?|grand|mil|(?:[kKmMgGbB]|t|T)(?![a-zA-Z]))?\s*
    (?P<close_paren>\))?
    (?:\s*(?P<trailing_currency>USD|EUR|GBP|CAD|AUD|dollars?|cents?))?
    """,
    re.IGNORECASE
)


# ============================================================================
# 3. EXTRACTION & NORMALIZATION ENGINE
# ============================================================================

@dataclass(frozen=True)
class NormalizedFinancial:
    """
    Immutable representation of an extracted monetary transaction.
    """
    raw_value: str                  # Original string, e.g. "$320M" or "($500.00)"
    amount_float: float             # Standard floating point, e.g. 320000000.0
    amount_cents: int               # Exact integer cents, e.g. 32000000000
    currency: str                   # 3-letter ISO code, e.g. "USD"
    is_negative: bool               # True if amount represents a debit/outflow
    multiplier: Optional[str]       # Matched multiplier, e.g. "M", "Million", "k"
    confidence: float = 1.0         # Extraction confidence (0.0 to 1.0)
    start_char: int = 0             # Character start offset in source text
    end_char: int = 0               # Character end offset in source text


def normalize_financial(raw_amount_str: str, default_currency: str = "USD") -> Optional[NormalizedFinancial]:
    """
    Parses a single monetary expression into a NormalizedFinancial record.
    Guarantees exact integer cents without IEEE-754 precision loss.
    """
    if not raw_amount_str or not raw_amount_str.strip():
        return None

    cleaned = raw_amount_str.strip()
    match = FINANCIAL_REGEX.search(cleaned)
    if not match:
        return None

    curr_raw = match.group("currency")
    trailing_curr = match.group("trailing_currency")
    mult_raw = match.group("multiplier")
    num_raw = match.group("number")

    # If neither currency symbol nor multiplier is present, require commas or decimals or trailing dollar
    if not curr_raw and not mult_raw and not trailing_curr:
        if "," not in num_raw and "." not in num_raw:
            return None

    try:
        num_str = num_raw.replace(",", "")
        base_val = Decimal(num_str)
    except (InvalidOperation, ValueError):
        return None

    # Apply multiplier
    mult_str = None
    if mult_raw:
        mult_str = mult_raw.strip()
        factor = MULTIPLIER_VALUES.get(mult_str.lower(), Decimal("1"))
        base_val *= factor

    # Handle negative sign or parenthetical accounting format
    has_sign = match.group("sign") in ("-", "–", "—")
    has_parens = bool(match.group("paren")) and bool(match.group("close_paren"))
    is_neg = has_sign or has_parens

    if is_neg:
        base_val = -abs(base_val)

    # Determine currency
    currency_code = default_currency
    if curr_raw:
        currency_code = CURRENCY_SYMBOL_MAP.get(curr_raw.upper(), default_currency)
    elif trailing_curr:
        tc_upper = trailing_curr.upper()
        if "DOLLAR" in tc_upper:
            currency_code = "USD"
        elif tc_upper in CURRENCY_SYMBOL_MAP:
            currency_code = CURRENCY_SYMBOL_MAP[tc_upper]

    # Compute integer cents using exact Decimal quantization
    cents_decimal = (base_val * Decimal("100")).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    amount_cents = int(cents_decimal)
    amount_float = float(base_val)

    return NormalizedFinancial(
        raw_value=cleaned,
        amount_float=amount_float,
        amount_cents=amount_cents,
        currency=currency_code,
        is_negative=is_neg,
        multiplier=mult_str,
        confidence=1.0,
        start_char=0,
        end_char=len(raw_amount_str)
    )


def extract_financials(text: str, default_currency: str = "USD") -> List[NormalizedFinancial]:
    """
    Extracts all monetary amounts from unstructured document text.
    Filters out phone numbers, years, docket numbers, and address numbers.
    """
    if not text:
        return []

    results: List[NormalizedFinancial] = []

    for match in FINANCIAL_REGEX.finditer(text):
        raw = match.group(0).strip()
        curr_raw = match.group("currency")
        trailing_curr = match.group("trailing_currency")
        mult_raw = match.group("multiplier")
        num_raw = match.group("number")

        # Discard false positives: standalone integer without currency or multiplier
        if not curr_raw and not mult_raw and not trailing_curr:
            if "," not in num_raw and "." not in num_raw:
                continue

        # Discard ordinals like 1st, 2nd, 3rd, 4th, 5th, 20th if without currency
        if not curr_raw and re.search(r"^\d+(?:st|nd|rd|th)\b", text[match.start():match.start() + len(num_raw) + 3], re.IGNORECASE):
            continue

        # Discard obvious phone number contexts e.g. (555) 123-4567
        start = match.start()
        end = match.end()
        surrounding = text[max(0, start - 10):min(len(text), end + 10)]
        if re.search(r"\(\d{3}\)\s*\d{3}-\d{4}", surrounding) or re.search(r"\b\d{3}-\d{3}-\d{4}\b", surrounding):
            continue

        # Discard docket numbers e.g. 8:23-cr-00108
        if re.search(r"\d+:\d+-(?:cr|cv|mj)-\d+", surrounding, re.IGNORECASE):
            continue

        # Discard standalone years e.g. 1999, 2021, 2026 if without currency
        if not curr_raw and not mult_raw and not trailing_curr and num_raw.isdigit():
            val_int = int(num_raw)
            if 1900 <= val_int <= 2050:
                continue

        norm = normalize_financial(raw, default_currency=default_currency)
        if norm and (abs(norm.amount_float) > 0.0 or norm.amount_cents != 0):
            results.append(
                NormalizedFinancial(
                    raw_value=raw,
                    amount_float=norm.amount_float,
                    amount_cents=norm.amount_cents,
                    currency=norm.currency,
                    is_negative=norm.is_negative,
                    multiplier=norm.multiplier,
                    confidence=norm.confidence,
                    start_char=start,
                    end_char=end
                )
            )

    return results


def extract_financial_amounts(text: str, default_currency: str = "USD") -> List[Dict[str, Any]]:
    """
    Convenience method returning canonical financial list matching ExtractedRecord interface:
    [{"raw": "$320M", "amount_float": 320000000.0, "amount_cents": 32000000000, "currency": "USD"}]
    """
    extracted = extract_financials(text, default_currency=default_currency)
    output: List[Dict[str, Any]] = []
    seen = set()
    for item in extracted:
        key = (item.amount_cents, item.currency, item.raw_value)
        if key not in seen:
            seen.add(key)
            output.append({
                "raw": item.raw_value,
                "amount_float": item.amount_float,
                "amount_cents": item.amount_cents,
                "currency": item.currency,
            })
    return output


def format_currency(amount_cents: int, currency: str = "USD") -> str:
    """Formats exact integer cents to canonical string representation."""
    is_neg = amount_cents < 0
    abs_cents = abs(amount_cents)
    dollars = abs_cents // 100
    cents = abs_cents % 100
    sign = "-" if is_neg else ""
    sym = "$" if currency == "USD" else (f"{currency} " if currency != "USD" else "$")
    return f"{sign}{sym}{dollars:,}.{cents:02d}"
