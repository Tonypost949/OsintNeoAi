# Technical Architecture & Implementation Blueprint: OsintNeoAi Normalizers Engine

**Document**: `analysis.md`  
**Milestone**: M2 (Deep Text Extraction & OCR Engine) — Features 8, 9, 10, 11  
**Agent**: Explorer M2.3 (`C:\OsintNeoAi\.agents\explorer_m2_3\`)  
**Target Package**: `C:\OsintNeoAi\workspaces\osintneoai_indexer\normalizers\`  
**Target Files**:
1. `normalizers\__init__.py`
2. `normalizers\date_normalizer.py`
3. `normalizers\financial_normalizer.py`
4. `normalizers\case_normalizer.py`
5. `normalizers\entity_normalizer.py`

---

## 1. Executive Summary & Normalizer Architecture

The **OsintNeoAi Multi-Tier Normalizer Engine** transforms raw, noisy, heterogeneous text extracted by native PDF decoders and neural OCR into strictly typed, cryptographically auditable, and canonical representations. 

In forensic and legal discovery pipelines, subtle string discrepancies—such as floating-point rounding errors in monetary sums, non-standard court filing stamps, varying corporate suffix abbreviations, and minor OCR misreadings—destroy relational joins and invalidate chronological monotonicity. 

The normalizer layer sits between **Document Extraction (PyMuPDF / RapidOCR ONNX)** and **Entity Resolution / Storage (DSU / SQLite Vault)**:

```
┌─────────────────────────────────────────────────────────────┐
│                 Document Extraction Output                  │
│       (Raw Extracted Text, OCR Glyphs, Document MTime)      │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│             OsintNeoAi Multi-Tier Normalizers               │
│                                                             │
│  ┌──────────────────────┐        ┌──────────────────────┐  │
│  │   Date Normalizer    │        │ Financial Normalizer │  │
│  │ (ISO 8601 UTC Parser)│        │ (Dual Float & Cents) │  │
│  └──────────┬───────────┘        └──────────┬───────────┘  │
│             │                               │              │
│  ┌──────────┴───────────┐        ┌──────────┴───────────┐  │
│  │    Case Normalizer   │        │   Entity Normalizer  │  │
│  │(Dockets & Citations) │        │ (Suffix, Soundex, DM)│  │
│  └──────────────────────┘        └──────────────────────┘  │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│            Normalized Records & Database Vault              │
│      (ExtractedRecord, timeline_vault.db, Catalog JSON)     │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Module 1: `normalizers/date_normalizer.py`

### 2.1 Problem Scope & 15+ Supported Date Formats

Legal filings, police incident logs, camera filenames, email RFC 2822 headers, and court register of actions contain diverse date/time representations. The `date_normalizer` parses these formats into standard **ISO 8601 UTC** strings (`YYYY-MM-DD` for date-only, `YYYY-MM-DDTHH:MM:SSZ` for date-time).

#### Supported Formats Matrix
| # | Format Category | Input String Example | Normalized ISO 8601 UTC Output |
|---|---|---|---|
| 1 | ISO 8601 Full UTC | `2021-08-04T16:29:00Z` | `2021-08-04T16:29:00Z` |
| 2 | ISO 8601 Date-Only | `2021-08-04` | `2021-08-04` |
| 3 | ISO 8601 Timezone Offset | `2021-08-04T09:29:00-07:00` | `2021-08-04T16:29:00Z` |
| 4 | Inverted Court Clerk Stamp | `2021 JUN 29 PM 4:29` | `2021-06-29T16:29:00Z` |
| 5 | Prefixed Filing Stamp | `FILED Apr 3, 2022` | `2022-04-03` |
| 6 | Prefixed Action Verb | `ENTERED 06/29/2021`, `DATED: Dec 8, 2021` | `2021-06-29`, `2021-12-08` |
| 7 | Full Written Month (US) | `December 8, 2021`, `July 24, 2026` | `2021-12-08`, `2026-07-24` |
| 8 | Day Month Year | `8 December 2021`, `24 July 2026` | `2021-12-08`, `2026-07-24` |
| 9 | US Slash Date (4-digit Year) | `06/29/2021`, `12/22/2021`, `02/04/2022` | `2021-06-29`, `2021-12-22`, `2022-02-04` |
| 10 | US Slash Date (2-digit Year) | `6/29/21`, `12/22/21`, `2/4/22` | `2021-06-29`, `2021-12-22`, `2022-02-04` |
| 11 | US Dash Date | `06-29-2021`, `12-22-2021` | `2021-06-29`, `2021-12-22` |
| 12 | US Date with 12h/24h Time | `06/29/2021 4:29 PM`, `01/14/2019 10:40` | `2021-06-29T16:29:00Z`, `2019-01-14T10:40:00Z` |
| 13 | RFC 2822 / RFC 822 Email | `Tue, 21 May 2019 06:04:00 -0700` | `2019-05-21T13:04:00Z` |
| 14 | RFC 2822 Named Timezone | `Mon, 16 Mar 2020 03:18:00 EDT` | `2020-03-16T07:18:00Z` |
| 15 | Media & Camera Filenames | `IMG_20260408_141546248_AE` | `2026-04-08T14:15:46Z` |
| 16 | Compact YYYYMMDD | `20210629`, `20210629_162900` | `2021-06-29`, `2021-06-29T16:29:00Z` |
| 17 | Dot-Separated Legal Date | `2021.06.29`, `06.29.2021` | `2021-06-29` |
| 18 | Contextual Date Phrase | `on or about August 4, 2021` | `2021-08-04` |

### 2.2 Data Contract: `NormalizedDate`

```python
from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class NormalizedDate:
    """
    Immutable representation of an extracted and normalized date/timestamp.
    """
    iso_value: str                  # "2021-06-29T16:29:00Z" or "2021-06-29"
    raw_value: str                  # Original matched string, e.g. "2021 JUN 29 PM 4:29"
    year: int                       # 2021
    month: int                      # 6
    day: int                        # 29
    hour: Optional[int] = None      # 16 (0-23) in UTC, or None if date-only
    minute: Optional[int] = None    # 29 (0-59), or None
    second: Optional[int] = None    # 0 (0-59), or None
    tz_offset_minutes: int = 0      # Timezone offset from UTC in minutes (0 for UTC)
    is_date_only: bool = False      # True if no time component was in source
    confidence: float = 1.0         # Confidence score (0.0 to 1.0)
    start_char: int = 0             # Character start offset in source text
    end_char: int = 0               # Character end offset in source text
```

### 2.3 Production Implementation Blueprint: `date_normalizer.py`

```python
"""
OsintNeoAi Indexer: Date & Timestamp Normalizer Module
Path: C:\\OsintNeoAi\\workspaces\\osintneoai_indexer\\normalizers\\date_normalizer.py

Standardizes heterogeneous legal, judicial, email, and media timestamps to ISO 8601 UTC.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Tuple, Union
import dateutil.parser
import dateutil.tz

# ============================================================================
# 1. TIMEZONE DEFINITIONS & LOOKUP TABLE
# ============================================================================

TIMEZONE_OFFSETS: Dict[str, int] = {
    "UTC": 0, "GMT": 0, "Z": 0,
    "EST": -300, "EDT": -240,  # Eastern: -5h / -4h
    "CST": -360, "CDT": -300,  # Central: -6h / -5h
    "MST": -420, "MDT": -360,  # Mountain: -7h / -6h
    "PST": -480, "PDT": -420,  # Pacific: -8h / -7h
    "AKST": -540, "AKDT": -480, # Alaska: -9h / -8h
    "HST": -600,                # Hawaii: -10h
}

# ============================================================================
# 2. COMPILED REGEX PATTERNS FOR DATE EXTRACTION & CLEANING
# ============================================================================

PREFIX_STRIP_RE = re.compile(
    r"^(?:FILED|ENTERED|DECIDED|DATED|RECORDED|ORDERED|SIGNED|RECEIVED|DATE|DOCKET\s+ENTRY|ON\s+OR\s+ABOUT)[:\s]*",
    re.IGNORECASE
)

# Inverted Court Timestamp: "2021 JUN 29 PM 4:29" -> reordered to "2021 JUN 29 4:29 PM"
INVERTED_STAMP_RE = re.compile(
    r"\b(?P<year>\d{4})\s+(?P<month>[A-Za-z]{3,9})\s+(?P<day>\d{1,2})\s+(?P<meridiem>AM|PM)\s+(?P<time>\d{1,2}:\d{2}(?::\d{2})?)\b",
    re.IGNORECASE
)

# Media/Camera Filename: "IMG_20260408_141546248_AE" or "20210629_162900"
CAMERA_FILENAME_RE = re.compile(
    r"\b(?:IMG_|VID_|SCAN_|DOC_)?(?P<year>\d{4})(?P<month>\d{2})(?P<day>\d{2})_(?P<hour>\d{2})(?P<min>\d{2})(?P<sec>\d{2})\b",
    re.IGNORECASE
)

# Explicit ISO 8601 Pattern
ISO_8601_RE = re.compile(
    r"\b(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})(?:[T\s](?P<hour>\d{2}):(?P<min>\d{2}):(?P<sec>\d{2})(?:\.\d+)?(?P<tz>Z|[+-]\d{2}:?\d{2}|[A-Za-z]{3,4})?)?\b"
)

# Written Month Date: "December 8, 2021", "Dec 8 2021", "8 December 2021"
WRITTEN_DATE_RE = re.compile(
    r"\b(?:(?P<day_pre>\d{1,2})\s+)?(?P<month>Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)[,\s]+(?:(?P<day_post>\d{1,2})[,\s]+)?(?P<year>\d{4})(?:\s+(?:at\s+)?(?P<hour>\d{1,2}):(?P<min>\d{2})(?::(?P<sec>\d{2}))?\s*(?P<meridiem>AM|PM)?)?(?:\s+(?P<tz>[A-Za-z]{3,4}))?\b",
    re.IGNORECASE
)

# Standard US Slash / Dash Date: "06/29/2021", "6/29/21", "12-22-2021", "02/04/2022"
US_NUMERIC_DATE_RE = re.compile(
    r"\b(?P<month>0?[1-9]|1[0-2])[\/\-\.](?P<day>0?[1-9]|[12]\d|3[01])[\/\-\.](?P<year>\d{4}|\d{2})(?:\s+(?:at\s+)?(?P<hour>0?[1-9]|1[0-2]|(?:[01]\d|2[0-3])):(?P<min>[0-5]\d)(?::(?P<sec>[0-5]\d))?\s*(?P<meridiem>AM|PM)?)?(?:\s+(?P<tz>[A-Za-z]{3,4}))?\b",
    re.IGNORECASE
)

# RFC 2822 Email Header Date: "Tue, 21 May 2019 06:04:00 -0700"
RFC_2822_RE = re.compile(
    r"\b(?:[A-Za-z]{3},\s+)?(?P<day>\d{1,2})\s+(?P<month>[A-Za-z]{3})\s+(?P<year>\d{4})\s+(?P<hour>\d{2}):(?P<min>\d{2}):(?P<sec>\d{2})\s+(?P<tz>[+-]\d{4}|[A-Za-z]{3,4})\b"
)


# ============================================================================
# 3. CORE NORMALIZATION FUNCTIONS
# ============================================================================

@dataclass(frozen=True)
class NormalizedDate:
    iso_value: str
    raw_value: str
    year: int
    month: int
    day: int
    hour: Optional[int] = None
    minute: Optional[int] = None
    second: Optional[int] = None
    tz_offset_minutes: int = 0
    is_date_only: bool = False
    confidence: float = 1.0
    start_char: int = 0
    end_char: int = 0


def _clean_date_string(raw: str) -> str:
    """Strips court prefixes and reorders inverted timestamps."""
    cleaned = PREFIX_STRIP_RE.sub("", raw.strip())
    # Convert "2021 JUN 29 PM 4:29" -> "2021 JUN 29 4:29 PM"
    cleaned = re.sub(
        r"\b(PM|AM)\s+(\d{1,2}:\d{2}(?::\d{2})?)\b",
        r"\2 \1",
        cleaned,
        flags=re.IGNORECASE
    )
    # OCR cleanups: '2O21' -> '2021'
    cleaned = re.sub(r"\b2O(\d{2})\b", r"20\1", cleaned)
    return cleaned.strip()


def normalize_date(raw_date_str: str, default_tz: str = "UTC") -> Optional[NormalizedDate]:
    """
    Parses a single raw date string into a canonical NormalizedDate.
    Returns None if parsing fails or result is outside valid historical range (1900..2050).
    """
    if not raw_date_str or not raw_date_str.strip():
        return None

    raw_cleaned = _clean_date_string(raw_date_str)

    # 1. Check Camera Filename pattern first
    cam_match = CAMERA_FILENAME_RE.search(raw_cleaned)
    if cam_match:
        yr = int(cam_match.group("year"))
        mo = int(cam_match.group("month"))
        da = int(cam_match.group("day"))
        hr = int(cam_match.group("hour"))
        mi = int(cam_match.group("min"))
        sc = int(cam_match.group("sec"))
        if 1900 <= yr <= 2050 and 1 <= mo <= 12 and 1 <= da <= 31:
            iso = f"{yr:04d}-{mo:02d}-{da:02d}T{hr:02d}:{mi:02d}:{sc:02d}Z"
            return NormalizedDate(
                iso_value=iso,
                raw_value=raw_date_str,
                year=yr, month=mo, day=da,
                hour=hr, minute=mi, second=sc,
                tz_offset_minutes=0,
                is_date_only=False,
                confidence=1.0,
                start_char=0, end_char=len(raw_date_str)
            )

    # 2. General fuzzy parse with python-dateutil (dayfirst=False for US legal standard)
    try:
        # Build tzinfos mapping
        tz_mapping = {k: dateutil.tz.tzoffset(k, v * 60) for k, v in TIMEZONE_OFFSETS.items()}
        dt = dateutil.parser.parse(raw_cleaned, fuzzy=True, dayfirst=False, tzinfos=tz_mapping)
        
        # Sanity check year
        if dt.year < 1900 or dt.year > 2050:
            return None

        # Determine if date-only
        has_explicit_time = bool(
            re.search(r"\b\d{1,2}:\d{2}\b", raw_cleaned) or 
            re.search(r"\b(AM|PM)\b", raw_cleaned, re.I) or 
            "T" in raw_cleaned
        )
        
        # Normalize to UTC
        tz_offset = 0
        if dt.tzinfo is not None:
            offset_delta = dt.utcoffset()
            if offset_delta is not None:
                tz_offset = int(offset_delta.total_seconds() / 60)
            dt_utc = dt.astimezone(timezone.utc)
        else:
            default_offset = TIMEZONE_OFFSETS.get(default_tz.upper(), 0)
            tz_offset = default_offset
            dt_utc = dt.replace(tzinfo=timezone.utc) - timedelta(minutes=default_offset)

        if not has_explicit_time:
            iso = dt.strftime("%Y-%m-%d")
            return NormalizedDate(
                iso_value=iso,
                raw_value=raw_date_str,
                year=dt.year, month=dt.month, day=dt.day,
                hour=None, minute=None, second=None,
                tz_offset_minutes=tz_offset,
                is_date_only=True,
                confidence=0.95,
                start_char=0, end_char=len(raw_date_str)
            )
        else:
            iso = dt_utc.strftime("%Y-%m-%dT%H:%M:%SZ")
            return NormalizedDate(
                iso_value=iso,
                raw_value=raw_date_str,
                year=dt_utc.year, month=dt_utc.month, day=dt_utc.day,
                hour=dt_utc.hour, minute=dt_utc.minute, second=dt_utc.second,
                tz_offset_minutes=tz_offset,
                is_date_only=False,
                confidence=1.0,
                start_char=0, end_char=len(raw_date_str)
            )
    except Exception:
        return None


def extract_dates(text: str, default_tz: str = "UTC") -> List[NormalizedDate]:
    """
    Scans a block of text and extracts all identifiable dates and timestamps.
    De-duplicates overlapping spans and returns a list sorted by occurrence position.
    """
    if not text:
        return []

    candidates: List[Tuple[int, int, str]] = []

    # Apply specialized regex finders
    for pattern in [CAMERA_FILENAME_RE, ISO_8601_RE, WRITTEN_DATE_RE, RFC_2822_RE, US_NUMERIC_DATE_RE, INVERTED_STAMP_RE]:
        for m in pattern.finditer(text):
            candidates.append((m.start(), m.end(), m.group(0)))

    # Sort by start_char ascending, length descending
    candidates.sort(key=lambda x: (x[0], -(x[1] - x[0])))

    # Non-overlapping filter
    merged: List[Tuple[int, int, str]] = []
    last_end = -1
    for start, end, raw in candidates:
        if start >= last_end:
            merged.append((start, end, raw))
            last_end = end

    results: List[NormalizedDate] = []
    for start, end, raw in merged:
        norm = normalize_date(raw, default_tz=default_tz)
        if norm:
            results.append(
                NormalizedDate(
                    iso_value=norm.iso_value,
                    raw_value=raw,
                    year=norm.year,
                    month=norm.month,
                    day=norm.day,
                    hour=norm.hour,
                    minute=norm.minute,
                    second=norm.second,
                    tz_offset_minutes=norm.tz_offset_minutes,
                    is_date_only=norm.is_date_only,
                    confidence=norm.confidence,
                    start_char=start,
                    end_char=end
                )
            )

    return results
```

---

## 3. Module 2: `normalizers/financial_normalizer.py`

### 3.1 Problem Scope & Integer Cents Guarantee

Monetary transactions in public records, court restitution orders, and settlement audits appear as:
- Suffix multipliers: `$320M`, `$96 Million`, `$1.5M`, `$250k`, `$6.1 million`
- Negative parenthetical accounting notations: `($500.00)`, `($96 Million)`, `($ 1.5 M)`
- Leading negative symbols: `-$500.00`, `-USD 4500`
- Formatted values: `$320,000,000.00`, `€1,500.50`, `£450,000`, `$0.49`

#### Elimination of IEEE 754 Floating-Point Drift
In standard Python floats, `19.99 * 100` evaluates to `1998.9999999999998`. If converted using `int()`, it truncates to `1998` cents ($19.98)—introducing financial corruption. 
The `financial_normalizer` strictly utilizes `decimal.Decimal` with `ROUND_HALF_UP` quantization:
```python
cents = int((val * Decimal(100)).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
```

### 3.2 Data Contract: `NormalizedFinancial`

```python
from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class NormalizedFinancial:
    """
    Immutable representation of an extracted monetary transaction.
    """
    raw_value: str                  # Original string, e.g. "$320M" or "($500.00)"
    amount_float: float             # Standard floating point, e.g. 320000000.0, -500.0
    amount_cents: int               # Exact integer cents, e.g. 32000000000, -50000
    currency: str                   # 3-letter ISO code, e.g. "USD", "EUR", "GBP"
    is_negative: bool               # True if amount represents a debit/outflow
    multiplier: Optional[str]       # Matched multiplier, e.g. "M", "Million", "k"
    confidence: float = 1.0         # Extraction confidence (0.0 to 1.0)
    start_char: int = 0             # Character start offset in source text
    end_char: int = 0               # Character end offset in source text
```

### 3.3 Production Implementation Blueprint: `financial_normalizer.py`

```python
"""
OsintNeoAi Indexer: Financial & Monetary Normalizer Module
Path: C:\\OsintNeoAi\\workspaces\\osintneoai_indexer\\normalizers\\financial_normalizer.py

Extracts and standardizes monetary sums to dual float and exact integer cents using Decimal arithmetic.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
from typing import Dict, List, Optional, Tuple

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
# 2. FINANCIAL REGEX PATTERN
# ============================================================================

# Multi-character words MUST precede single character tokens (e.g. million before m)
FINANCIAL_REGEX = re.compile(
    r"""(?x)
    (?P<sign>[-–—+])?
    (?P<paren>\()?\s*
    (?:(?P<currency>[\$€£¥₩₹]|USD|EUR|GBP|CAD|AUD)\s*)?
    (?P<number>\d+(?:,\d{3})*(?:\.\d+)?|\d*\.\d+)\s*
    (?P<multiplier>trillions?|billions?|millions?|thousands?|grand|mil|[kKmMgGbBtT])?\s*
    (?P<close_paren>\))?
    """,
    re.IGNORECASE
)


# ============================================================================
# 3. EXTRACTION & NORMALIZATION ENGINE
# ============================================================================

@dataclass(frozen=True)
class NormalizedFinancial:
    raw_value: str
    amount_float: float
    amount_cents: int
    currency: str
    is_negative: bool
    multiplier: Optional[str]
    confidence: float = 1.0
    start_char: int = 0
    end_char: int = 0


def normalize_financial(raw_amount_str: str, default_currency: str = "USD") -> Optional[NormalizedFinancial]:
    """
    Parses a single monetary expression into a NormalizedFinancial record.
    """
    if not raw_amount_str or not raw_amount_str.strip():
        return None

    cleaned = raw_amount_str.strip()
    match = FINANCIAL_REGEX.search(cleaned)
    if not match:
        return None

    curr_raw = match.group("currency")
    mult_raw = match.group("multiplier")
    num_raw = match.group("number")

    # If neither currency symbol nor multiplier is present, require commas or decimals to avoid plain integers
    if not curr_raw and not mult_raw:
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

    currency = CURRENCY_SYMBOL_MAP.get(curr_raw.upper() if curr_raw else "", default_currency)

    # Compute integer cents using exact Decimal quantization
    cents_decimal = (base_val * Decimal("100")).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    amount_cents = int(cents_decimal)
    amount_float = float(base_val)

    return NormalizedFinancial(
        raw_value=cleaned,
        amount_float=amount_float,
        amount_cents=amount_cents,
        currency=currency,
        is_negative=is_neg,
        multiplier=mult_str,
        confidence=1.0,
        start_char=0,
        end_char=len(raw_amount_str)
    )


def extract_financials(text: str, default_currency: str = "USD") -> List[NormalizedFinancial]:
    """
    Extracts all monetary amounts from unstructured document text.
    Filters out phone numbers, years, and address numbers.
    """
    if not text:
        return []

    results: List[NormalizedFinancial] = []

    for match in FINANCIAL_REGEX.finditer(text):
        raw = match.group(0).strip()
        curr_raw = match.group("currency")
        mult_raw = match.group("multiplier")
        num_raw = match.group("number")

        # Discard false positives: standalone integer without currency or multiplier
        if not curr_raw and not mult_raw:
            if "," not in num_raw and "." not in num_raw:
                continue

        # Discard obvious phone number contexts
        start = match.start()
        end = match.end()
        surrounding = text[max(0, start - 5):min(len(text), end + 5)]
        if re.search(r"\(\d{3}\)\s*\d{3}-\d{4}", surrounding):
            continue

        norm = normalize_financial(raw, default_currency=default_currency)
        if norm:
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


def format_currency(amount_cents: int, currency: str = "USD") -> str:
    """Formats exact integer cents to canonical string representation."""
    is_neg = amount_cents < 0
    abs_cents = abs(amount_cents)
    dollars = abs_cents // 100
    cents = abs_cents % 100
    sign = "-" if is_neg else ""
    sym = "$" if currency == "USD" else (f"{currency} " if currency != "USD" else "$")
    return f"{sign}{sym}{dollars:,}.{cents:02d}"
```

---

## 4. Module 3: `normalizers/case_normalizer.py`

### 4.1 Problem Scope & Multi-Jurisdictional Taxonomy

The investigation records span three distinct legal jurisdictions and statutory frameworks:
1. **Federal District Court Dockets (`USDC`)**:
   - Central District of California (CDCA): `8:23-cr-00108-CJC` (Harry Sidhu), `8:22-cr-00078-CJC` (Todd Ament), `8:23-cr-00009-CJC` (Melahat Rafiei), `8:26-cv-00348-JWH-ADS` (Jesse Knabb)
   - District of New Jersey (DNJ): `3:20-mj-05007-TJB` (Christopher Ryan)
   - Southern District of California (SDCA): `19-CR-1787-BAS` (Jeremy Shane Marble)
   - Short clerk citations: `Case No. 20-5007 (TJB)`, `8:23cr108`
2. **California Superior Court Dockets**:
   - Orange County Central Justice Center (CJC): `30-2021-01201327-CL-UD-CJC` (Woodbridge Meadows v. Dimarcello)
   - Structure: `[CountyPrefix]-[YYYY]-[8-digit Sequence]-[Category]-[Subcategory]-[Department/Judge]`
3. **Multi-State Law Enforcement Incident & Summons Numbers**:
   - Hamilton Township Police Division: `Case 2019-00053723`, `Case 2020-00008897`, `Summons #2020-613`
   - Ewing Police Department: `Case Number: I-2019-001222` / `1-2019-001222`
   - Orange County Sheriff's Eviction Notice: `Levying Officer File No. 2021102780`
4. **Statutory Violations & Legislative Instruments**:
   - California Government Code: `Cal. Gov. Code § 54220` (Surplus Land Act), `Cal. Gov. Code § 54950` (Ralph M. Brown Act)
   - California Code of Civil Procedure: `Cal. CCP § 170.6` (Peremptory Challenge against Judge Carmen Luege)
   - Federal Criminal Codes: `18 U.S.C. § 1343` (Wire Fraud), `18 U.S.C. § 1346` (Honest Services), `18 U.S.C. § 1951` (Hobbs Act Extortion), `18 U.S.C. § 1962` (RICO), `31 U.S.C. § 3729` (False Claims Act), `42 U.S.C. § 1983` (Civil Rights), `42 U.S.C. § 6901` (RCRA)
   - Municipal Acts: `Anaheim City Council Resolution No. 2022-064`

### 4.2 Data Contract: `NormalizedCaseCitation`

```python
from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class NormalizedCaseCitation:
    """
    Immutable representation of an extracted court docket, police incident, or statutory citation.
    """
    raw_text: str                   # Original matched text, e.g. "Case No. 8:23-cr-00108-CJC"
    canonical_id: str               # Normalized identifier, e.g. "8:23-cr-00108-CJC" or "Cal. Gov. Code § 54220"
    citation_type: str              # "federal_docket", "state_docket", "police_incident", "statutory_citation", "municipal_resolution"
    jurisdiction: str               # "USDC CDCA", "California Superior Court (Orange County)", "Federal", "California", "Hamilton Township NJ"
    case_type: Optional[str]        # "CRIMINAL", "CIVIL", "UNLAWFUL_DETAINER", "MAGISTRATE", etc.
    year: Optional[int]             # Filing year (e.g. 2023, 2021)
    judge_initials: Optional[str]   # "CJC", "BAS", "TJB", "JWH-ADS"
    court_department: Optional[str] # "CJC", "C-32"
    confidence: float = 1.0
    start_char: int = 0
    end_char: int = 0
```

### 4.3 Production Implementation Blueprint: `case_normalizer.py`

```python
"""
OsintNeoAi Indexer: Legal Case & Statutory Citation Normalizer Module
Path: C:\\OsintNeoAi\\workspaces\\osintneoai_indexer\\normalizers\\case_normalizer.py

Identifies, extracts, and canonicalizes federal court dockets, California Superior Court dockets,
law enforcement incident numbers, and statutory legal citations.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List, Optional, Tuple

# ============================================================================
# 1. REGULAR EXPRESSIONS FOR DOCKETS AND CITATIONS
# ============================================================================

FEDERAL_DOCKET_RE = re.compile(
    r"""(?x)
    \b
    (?:Case\s*(?:No\.?|#)?[:\s]*)?
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
    (?:Case\s*(?:No\.?|#)?[:\s]*)?
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
      | (?:Summons\s*#?[:\s]*)(?P<summons>\d{4}-\d{3,4}|\d{4}-S-\d{4}-\d{6})
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
        "Anaheim Resolution No. 2022-064",
        "City of Anaheim",
        re.compile(r"Resolution\s*(?:No\.?)?\s*2022-064", re.IGNORECASE)
    ),
]


# ============================================================================
# 2. CORE NORMALIZATION & EXTRACTION ENGINE
# ============================================================================

@dataclass(frozen=True)
class NormalizedCaseCitation:
    raw_text: str
    canonical_id: str
    citation_type: str
    jurisdiction: str
    case_type: Optional[str]
    year: Optional[int]
    judge_initials: Optional[str]
    court_department: Optional[str]
    confidence: float = 1.0
    start_char: int = 0
    end_char: int = 0


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
            canon = f"POLICE-CASE-{m.group('police_case')}"
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
```

---

## 5. Module 4: `normalizers/entity_normalizer.py`

### 5.1 Problem Scope & Pure-Python Phonetic Blocking

Entity resolution requires grouping mentions despite spelling variations (e.g. `Sidhu` vs `Sldhu`, `Smith` vs `Smyth`, `Schmidt`).
Because external C-extension phonetic libraries (such as `metaphone` or `soundex`) are not guaranteed across all environments, `entity_normalizer.py` provides:
1. **Longest-Match Corporate Legal Suffix Canonicalization & Stripping** (30+ legal entity suffixes).
2. **Pure-Python Russell Soundex Algorithm**.
3. **Pure-Python Lawrence Philips Double Metaphone Algorithm** (returning Primary & Secondary phonetic codes).
4. **Judicial & Public Official Honorific Cleaner**.

### 5.2 Data Contract: `NormalizedEntity`

```python
from dataclasses import dataclass
from typing import Optional, Tuple

@dataclass(frozen=True)
class NormalizedEntity:
    """
    Immutable representation of a normalized entity with phonetic blocking codes.
    """
    raw_name: str                   # Original text, e.g. "Woodbridge Meadows Apartments, L.L.C."
    cleaned_name: str               # Cleansed string, e.g. "Woodbridge Meadows Apartments LLC"
    core_stem: str                  # Suffix-stripped stem, e.g. "Woodbridge Meadows Apartments"
    canonical_suffix: Optional[str] # "LLC", "LLP", "INC", "CORP", "LP", etc.
    soundex: str                    # Russell Soundex code (e.g. "W316")
    metaphone_primary: str          # Double Metaphone primary key (e.g. "ATPR")
    metaphone_secondary: str        # Double Metaphone secondary key (e.g. "FTPR")
    entity_category: Optional[str]  # "INDIVIDUAL", "COMMERCIAL_ENTITY", "MUNICIPAL_BODY", etc.
    confidence: float = 1.0
```

### 5.3 Production Implementation Blueprint: `entity_normalizer.py`

```python
"""
OsintNeoAi Indexer: Entity Normalizer & Phonetic Blocking Module
Path: C:\\OsintNeoAi\\workspaces\\osintneoai_indexer\\normalizers\\entity_normalizer.py

Corporate legal suffix normalizer, Russell Soundex, and pure-Python Double Metaphone phonetic encoders.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

# ============================================================================
# 1. CORPORATE SUFFIX PATTERNS & CANONICAL MAPPINGS
# ============================================================================

CORP_SUFFIX_RE = re.compile(
    r"""(?x)
    [,\s]+
    (?:
        (?P<pllc>PROFESSIONAL\s+LIMITED\s+LIABILITY\s+COMPANY|P\.L\.L\.C\.|PLLC)
      | (?P<llp>LIMITED\s+LIABILITY\s+PARTNERSHIP|L\.L\.P\.|LLP)
      | (?P<llc>LIMITED\s+LIABILITY\s+COMPANY|L\.L\.C\.|LLC)
      | (?P<lp>LIMITED\s+PARTNERSHIP|L\.P\.|LP)
      | (?P<corp>PROFESSIONAL\s+CORPORATION|CORPORATION|CORP\.|CORP)
      | (?P<inc>INCORPORATED|INC\.|INC)
      | (?P<ltd>LIMITED|LTD\.|LTD)
      | (?P<pa>PROFESSIONAL\s+ASSOCIATION|P\.A\.|PA)
      | (?P<pc>PROFESSIONAL\s+CORPORATION|P\.C\.|PC)
      | (?P<na>NATIONAL\s+ASSOCIATION|N\.A\.|NA)
      | (?P<co>COMPANY|CO\.|CO)
    )
    $
    """,
    re.IGNORECASE
)

HONORIFIC_PREFIX_RE = re.compile(
    r"""(?x)
    ^
    (?:
        Hon(?:orable|\.)?
      | Judge
      | Mayor
      | Sheriff
      | Special\s+Agent
      | FBI\s+SA
      | SA
      | Dir(?:ector|\.)?
      | Councilmember
      | City\s+Attorney
      | Dr\.
      | Mr\.
      | Ms\.
      | Mrs\.
      | Esq\.
    )
    \s+
    """,
    re.IGNORECASE
)


# ============================================================================
# 2. PURE-PYTHON RUSSELL SOUNDEX ENCODER
# ============================================================================

SOUNDEX_MAP: Dict[str, str] = {
    "B": "1", "F": "1", "P": "1", "V": "1",
    "C": "2", "G": "2", "J": "2", "K": "2", "Q": "2", "S": "2", "X": "2", "Z": "2",
    "D": "3", "T": "3",
    "L": "4",
    "M": "5", "N": "5",
    "R": "6",
}

def soundex(name: str) -> str:
    """
    Computes standard Russell Soundex phonetic code for a name.
    Returns 4-character string (Letter + 3 digits), e.g. "S300" for Sidhu.
    """
    if not name:
        return "0000"

    norm = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode("ascii")
    letters = [c.upper() for c in norm if c.isalpha()]
    if not letters:
        return "0000"

    first_char = letters[0]
    encoded = [first_char]
    prev_code = SOUNDEX_MAP.get(first_char, "0")

    for c in letters[1:]:
        code = SOUNDEX_MAP.get(c, "0")
        if c in "HW":
            continue
        if c in "AEIOUY":
            prev_code = "0"
            continue
        if code != "0" and code != prev_code:
            encoded.append(code)
            prev_code = code

    digits = "".join(encoded[1:])
    digits = (digits + "000")[:3]
    return first_char + digits


# ============================================================================
# 3. PURE-PYTHON DOUBLE METAPHONE PHONETIC ENCODER
# ============================================================================

def double_metaphone(name: str, max_length: int = 4) -> Tuple[str, str]:
    """
    Computes Lawrence Philips' Double Metaphone phonetic representation.
    Returns (primary_code, secondary_code) tuple of length <= max_length.
    """
    if not name:
        return ("", "")

    norm = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode("ascii")
    val = "".join(c for c in norm.upper() if c.isalpha())
    if not val:
        return ("", "")

    length = len(val)
    pos = 0
    primary: List[str] = []
    secondary: List[str] = []

    def substr(start: int, length: int) -> str:
        return val[start:start + length]

    def is_vowel(idx: int) -> bool:
        return 0 <= idx < len(val) and val[idx] in "AEIOUY"

    # Initial silent letters
    if val.startswith(("GN", "KN", "PN", "WR", "PS")):
        pos += 1
    elif val.startswith("X"):
        primary.append("S")
        secondary.append("S")
        pos += 1

    while pos < length and (len(primary) < max_length or len(secondary) < max_length):
        c = val[pos]

        # Vowels at start of word
        if c in "AEIOUY":
            if pos == 0:
                primary.append("A")
                secondary.append("A")
            pos += 1
            continue

        # B
        if c == "B":
            primary.append("P")
            secondary.append("P")
            pos += 2 if substr(pos + 1, 1) == "B" else 1
            continue

        # C
        if c == "C":
            if pos > 1 and not is_vowel(pos - 2) and substr(pos - 1, 3) == "ACH" and \
               substr(pos + 2, 1) not in ["I", "E"] or \
               substr(pos - 2, 6) in ["BACHER", "MACHER"]:
                primary.append("K")
                secondary.append("K")
                pos += 2
                continue
            if pos == 0 and substr(pos, 6) == "CAESAR":
                primary.append("S")
                secondary.append("S")
                pos += 2
                continue
            if substr(pos, 2) == "CH":
                if pos > 0 and substr(pos, 4) == "CHAE":
                    primary.append("K")
                    secondary.append("X")
                    pos += 2
                elif pos == 0 and (substr(pos + 1, 5) in ["HARAC", "HARIS"] or \
                     substr(pos + 1, 3) in ["HOR", "HYM", "HIA", "HEM"]) and \
                     substr(0, 5) != "CHORE":
                    primary.append("K")
                    secondary.append("K")
                    pos += 2
                else:
                    if pos == 0:
                        primary.append("X")
                        secondary.append("K")
                    else:
                        primary.append("X")
                        secondary.append("X")
                    pos += 2
                continue
            if substr(pos, 2) == "CZ" and substr(pos - 2, 4) != "WICZ":
                primary.append("S")
                secondary.append("X")
                pos += 2
                continue
            if substr(pos + 1, 2) == "IA":
                primary.append("X")
                secondary.append("X")
                pos += 3
                continue
            if substr(pos, 2) in ["CC"] and not (pos == 1 and val[0] == "M"):
                if substr(pos + 2, 1) in ["I", "E", "H"] and substr(pos + 2, 2) != "HU":
                    if (pos == 1 and substr(pos - 1, 1) == "A") or \
                       substr(pos - 1, 5) in ["UCCEE", "UCCES"]:
                        primary.append("KS")
                        secondary.append("KS")
                    else:
                        primary.append("X")
                        secondary.append("X")
                    pos += 3
                    continue
                else:
                    primary.append("K")
                    secondary.append("K")
                    pos += 2
                    continue
            if substr(pos, 2) in ["CK", "CG", "CQ"]:
                primary.append("K")
                secondary.append("K")
                pos += 2
                continue
            if substr(pos, 2) in ["CI", "CE", "CY"]:
                if substr(pos, 3) in ["CIO", "CIE", "CIA"]:
                    primary.append("S")
                    secondary.append("X")
                else:
                    primary.append("S")
                    secondary.append("S")
                pos += 2
                continue
            primary.append("K")
            secondary.append("K")
            if substr(pos + 1, 2) in [" C", " Q", " G"]:
                pos += 3
            elif substr(pos + 1, 1) in ["C", "K", "Q"] and substr(pos + 1, 2) not in ["CE", "CI"]:
                pos += 2
            else:
                pos += 1
            continue

        # D
        if c == "D":
            if substr(pos, 2) == "DG":
                if substr(pos + 2, 1) in ["I", "E", "Y"]:
                    primary.append("J")
                    secondary.append("J")
                    pos += 3
                else:
                    primary.append("TK")
                    secondary.append("TK")
                    pos += 2
                continue
            if substr(pos, 2) in ["DT", "DD"]:
                primary.append("T")
                secondary.append("T")
                pos += 2
                continue
            primary.append("T")
            secondary.append("T")
            pos += 1
            continue

        # F
        if c == "F":
            primary.append("F")
            secondary.append("F")
            pos += 2 if substr(pos + 1, 1) == "F" else 1
            continue

        # G
        if c == "G":
            if substr(pos + 1, 1) == "H":
                if pos > 0 and not is_vowel(pos - 1):
                    primary.append("K")
                    secondary.append("K")
                    pos += 2
                elif pos == 0:
                    if substr(pos + 2, 1) == "I":
                        primary.append("J")
                        secondary.append("J")
                    else:
                        primary.append("K")
                        secondary.append("K")
                    pos += 2
                elif pos > 1 and substr(pos - 2, 1) in ["B", "H", "D"] or \
                     pos > 2 and substr(pos - 3, 1) in ["B", "H", "D"] or \
                     pos > 3 and substr(pos - 4, 1) in ["B", "H"]:
                    pos += 2
                else:
                    if pos > 2 and substr(pos - 1, 1) == "U" and substr(pos - 3, 1) in ["C", "G", "L", "R", "T"]:
                        primary.append("F")
                        secondary.append("F")
                    elif pos > 0 and substr(pos - 1, 1) != "I":
                        primary.append("K")
                        secondary.append("K")
                    pos += 2
                continue
            if substr(pos + 1, 1) == "N":
                if pos == 1 and is_vowel(0) and not (pos + 2 < length and val[pos + 2] == "Y"):
                    primary.append("KN")
                    secondary.append("N")
                elif substr(pos + 2, 2) != "EY" and substr(pos + 1, 1) != "Y" and not (pos + 1 < length and val[pos + 1] == "Y"):
                    primary.append("N")
                    secondary.append("KN")
                else:
                    primary.append("KN")
                    secondary.append("KN")
                pos += 2
                continue
            if substr(pos, 2) in ["GE", "GI", "GY"]:
                primary.append("K")
                secondary.append("J")
                pos += 2
                continue
            primary.append("K")
            secondary.append("K")
            pos += 2 if substr(pos + 1, 1) == "G" else 1
            continue

        # H
        if c == "H":
            if (pos == 0 or is_vowel(pos - 1)) and is_vowel(pos + 1):
                primary.append("H")
                secondary.append("H")
                pos += 2
            else:
                pos += 1
            continue

        # J
        if c == "J":
            primary.append("J")
            secondary.append("A")
            pos += 2 if substr(pos + 1, 1) == "J" else 1
            continue

        # K
        if c == "K":
            primary.append("K")
            secondary.append("K")
            pos += 2 if substr(pos + 1, 1) == "K" else 1
            continue

        # L
        if c == "L":
            if substr(pos + 1, 1) == "L":
                primary.append("L")
                pos += 2
                continue
            primary.append("L")
            secondary.append("L")
            pos += 1
            continue

        # M
        if c == "M":
            primary.append("M")
            secondary.append("M")
            pos += 2 if substr(pos + 1, 1) == "M" else 1
            continue

        # N
        if c == "N":
            primary.append("N")
            secondary.append("N")
            pos += 2 if substr(pos + 1, 1) == "N" else 1
            continue

        # P
        if c == "P":
            if substr(pos + 1, 1) == "H":
                primary.append("F")
                secondary.append("F")
                pos += 2
            else:
                primary.append("P")
                secondary.append("P")
                pos += 2 if substr(pos + 1, 1) == "P" else 1
            continue

        # Q
        if c == "Q":
            primary.append("K")
            secondary.append("K")
            pos += 2 if substr(pos + 1, 1) == "Q" else 1
            continue

        # R
        if c == "R":
            primary.append("R")
            secondary.append("R")
            pos += 2 if substr(pos + 1, 1) == "R" else 1
            continue

        # S
        if c == "S":
            if substr(pos, 2) == "SH":
                primary.append("X")
                secondary.append("X")
                pos += 2
            elif substr(pos, 3) in ["SIO", "SIA"]:
                primary.append("S")
                secondary.append("X")
                pos += 3
            else:
                primary.append("S")
                secondary.append("S")
                pos += 2 if substr(pos + 1, 1) == "S" else 1
            continue

        # T
        if c == "T":
            if substr(pos, 2) == "TH":
                primary.append("0")
                secondary.append("T")
                pos += 2
            elif substr(pos, 3) in ["TIA", "TIO"]:
                primary.append("X")
                secondary.append("X")
                pos += 3
            else:
                primary.append("T")
                secondary.append("T")
                pos += 2 if substr(pos + 1, 1) == "T" else 1
            continue

        # V
        if c == "V":
            primary.append("F")
            secondary.append("F")
            pos += 2 if substr(pos + 1, 1) == "V" else 1
            continue

        # W
        if c == "W":
            if substr(pos, 2) == "WR":
                primary.append("R")
                secondary.append("R")
                pos += 2
            elif pos == 0 and is_vowel(pos + 1):
                primary.append("A")
                secondary.append("F")
                pos += 1
            else:
                pos += 1
            continue

        # X
        if c == "X":
            primary.append("KS")
            secondary.append("KS")
            pos += 2 if substr(pos + 1, 1) == "X" else 1
            continue

        # Z
        if c == "Z":
            primary.append("S")
            secondary.append("TS")
            pos += 2 if substr(pos + 1, 1) == "Z" else 1
            continue

        pos += 1

    p_str = ("".join(primary))[:max_length]
    s_str = ("".join(secondary))[:max_length]
    return (p_str, s_str)


# ============================================================================
# 4. ENTITY CLEANING & NORMALIZATION API
# ============================================================================

@dataclass(frozen=True)
class NormalizedEntity:
    raw_name: str
    cleaned_name: str
    core_stem: str
    canonical_suffix: Optional[str]
    soundex: str
    metaphone_primary: str
    metaphone_secondary: str
    entity_category: Optional[str]
    confidence: float = 1.0


def strip_corporate_suffix(entity_name: str) -> str:
    """Removes trailing corporate legal suffixes."""
    if not entity_name:
        return ""
    cleaned = HONORIFIC_PREFIX_RE.sub("", entity_name.strip())
    match = CORP_SUFFIX_RE.search(cleaned)
    if match:
        return cleaned[:match.start()].rstrip(" ,.")
    return cleaned


def normalize_entity(entity_name: str, entity_category: Optional[str] = None) -> NormalizedEntity:
    """
    Standardizes an entity name, isolates corporate suffix, and generates phonetic blocking keys.
    """
    if not entity_name:
        return NormalizedEntity(
            raw_name="",
            cleaned_name="",
            core_stem="",
            canonical_suffix=None,
            soundex="0000",
            metaphone_primary="",
            metaphone_secondary="",
            entity_category=entity_category,
            confidence=0.0
        )

    raw_clean = entity_name.strip().strip("\"'").strip()
    cleaned = HONORIFIC_PREFIX_RE.sub("", raw_clean)

    match = CORP_SUFFIX_RE.search(cleaned)
    if match:
        matched_group = [k for k, v in match.groupdict().items() if v is not None][0]
        canon_suffix = matched_group.upper()
        stem = cleaned[:match.start()].rstrip(" ,.")
        canonical_name = f"{stem} {canon_suffix}"
    else:
        stem = cleaned
        canon_suffix = None
        canonical_name = cleaned

    sx = soundex(stem)
    dm_p, dm_s = double_metaphone(stem)

    return NormalizedEntity(
        raw_name=entity_name,
        cleaned_name=canonical_name,
        core_stem=stem,
        canonical_suffix=canon_suffix,
        soundex=sx,
        metaphone_primary=dm_p,
        metaphone_secondary=dm_s,
        entity_category=entity_category,
        confidence=1.0
    )
```

---

## 6. Package Root Blueprint: `normalizers/__init__.py`

```python
"""
OsintNeoAi Indexer: Normalizers Package
Path: C:\\OsintNeoAi\\workspaces\\osintneoai_indexer\\normalizers\\__init__.py

Exposes all normalizer dataclasses and conversion pipelines.
"""

from osintneoai_indexer.normalizers.date_normalizer import (
    NormalizedDate,
    normalize_date,
    extract_dates,
)
from osintneoai_indexer.normalizers.financial_normalizer import (
    NormalizedFinancial,
    normalize_financial,
    extract_financials,
    format_currency,
)
from osintneoai_indexer.normalizers.case_normalizer import (
    NormalizedCaseCitation,
    extract_case_citations,
)
from osintneoai_indexer.normalizers.entity_normalizer import (
    NormalizedEntity,
    normalize_entity,
    strip_corporate_suffix,
    soundex,
    double_metaphone,
)

__all__ = [
    "NormalizedDate",
    "normalize_date",
    "extract_dates",
    "NormalizedFinancial",
    "normalize_financial",
    "extract_financials",
    "format_currency",
    "NormalizedCaseCitation",
    "extract_case_citations",
    "NormalizedEntity",
    "normalize_entity",
    "strip_corporate_suffix",
    "soundex",
    "double_metaphone",
]
```

---

## 7. Comprehensive Pytest Test Suite Blueprints

To ensure 100% test coverage and compliance with invariant assertions, the builder will instantiate unit tests across four categories:
1. `tests/test_normalizers_date.py`: 20 unit tests covering ISO 8601, court stamps, RFC 2822, camera files, timezone shifts, and OCR errors.
2. `tests/test_normalizers_financial.py`: 20 unit tests covering exact cents quantization, multipliers, parenthetical accounting negatives, multi-currency parsing, and false positive filtration.
3. `tests/test_normalizers_case.py`: 20 unit tests covering federal USDC CDCA/DNJ, California Superior Court 30-series, police incident logs, and statutory citations.
4. `tests/test_normalizers_entity.py`: 20 unit tests covering corporate suffix stripping, canonicalization, Russell Soundex, and Double Metaphone matching.

---

## 8. Summary of Interface Compliance

| Interface / Component | PROJECT.md Requirement | Implementation Specification |
|---|---|---|
| Date Output | ISO 8601 UTC (`YYYY-MM-DD` / `YYYY-MM-DDTHH:MM:SSZ`) | Fully compliant via `date_normalizer.py` |
| Financial Output | `amount_float` + `amount_cents` integer | Fully compliant with Decimal quantization via `financial_normalizer.py` |
| Case Dockets | Federal + State dockets + Statutes | Fully compliant with zero-padded dockets via `case_normalizer.py` |
| Entity Phonetics | Soundex & Double Metaphone | Pure-Python zero-dependency implementation via `entity_normalizer.py` |
| Memory Complexity | $O(1)$ memory consumption | Linear streaming with pre-compiled regex engine |
