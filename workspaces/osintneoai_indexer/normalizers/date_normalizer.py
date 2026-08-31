"""
OsintNeoAi Indexer: Date & Timestamp Normalizer Module
Path: C:\\OsintNeoAi\\workspaces\\osintneoai_indexer\\normalizers\\date_normalizer.py
Milestone: M2 (Deep Text Extraction & OCR Engine) — Feature 8

Parses 15+ heterogeneous legal, judicial, email, and media timestamps into strict canonical ISO 8601 UTC.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional, Tuple, Union
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
    r"(?:IMG_|VID_|SCAN_|DOC_)?(?P<year>19\d{2}|20\d{2})(?P<month>0[1-9]|1[0-2])(?P<day>0[1-9]|[12]\d|3[01])_(?P<hour>[01]\d|2[0-3])(?P<min>[0-5]\d)(?P<sec>[0-5]\d)(?:\d{3})?(?:_[A-Za-z0-9]+)?",
    re.IGNORECASE
)

# Compact YYYYMMDD Date-Only: "20210629"
COMPACT_YYYYMMDD_RE = re.compile(
    r"\b(?P<year>19\d{2}|20\d{2})(?P<month>0[1-9]|1[0-2])(?P<day>0[1-9]|[12]\d|3[01])\b"
)

# Explicit ISO 8601 Pattern
ISO_8601_RE = re.compile(
    r"\b(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})(?:[T\s](?P<hour>\d{2}):(?P<min>\d{2}):(?P<sec>\d{2})(?:\.\d+)?(?P<tz>Z|[+-]\d{2}:?\d{2}|[A-Za-z]{3,4})?)?\b"
)

# Written Month Date: "December 8, 2021", "Dec 8 2021", "8 December 2021", "DATED this 29th day of June, 2021"
WRITTEN_DATE_RE = re.compile(
    r"\b(?:(?P<day_pre>\d{1,2})(?:st|nd|rd|th)?\s+(?:day\s+of\s+)?)?(?P<month>Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)[,\s]+(?:(?P<day_post>\d{1,2})(?:st|nd|rd|th)?[,\s]+)?(?P<year>\d{4})(?:\s+(?:at\s+)?(?P<hour>\d{1,2}):(?P<min>\d{2})(?::(?P<sec>\d{2}))?\s*(?P<meridiem>AM|PM)?)?(?:\s+(?P<tz>[A-Za-z]{3,4}))?\b",
    re.IGNORECASE
)

# Standard US Slash / Dash / Dot Date: "06/29/2021", "6/29/21", "12-22-2021", "02/04/2022", "2021.06.29"
US_NUMERIC_DATE_RE = re.compile(
    r"\b(?P<month>0?[1-9]|1[0-2])[\/\-\.](?P<day>0?[1-9]|[12]\d|3[01])[\/\-\.](?P<year>\d{4}|\d{2})(?:\s+(?:at\s+)?(?P<hour>0?[1-9]|1[0-2]|(?:[01]\d|2[0-3])):(?P<min>[0-5]\d)(?::(?P<sec>[0-5]\d))?\s*(?P<meridiem>AM|PM)?)?(?:\s+(?P<tz>[A-Za-z]{3,4}))?\b",
    re.IGNORECASE
)

DOT_LEGAL_DATE_RE = re.compile(
    r"\b(?P<year>\d{4})\.(?P<month>0?[1-9]|1[0-2])\.(?P<day>0?[1-9]|[12]\d|3[01])\b"
)

# RFC 2822 Email Header Date: "Tue, 21 May 2019 06:04:00 -0700"
RFC_2822_RE = re.compile(
    r"\b(?:[A-Za-z]{3},\s+)?(?P<day>\d{1,2})\s+(?P<month>[A-Za-z]{3})\s+(?P<year>\d{4})\s+(?P<hour>\d{2}):(?P<min>\d{2}):(?P<sec>\d{2})\s+(?P<tz>[+-]\d{4}|[A-Za-z]{3,4})\b"
)


# ============================================================================
# 3. CORE DATA STRUCTURES & CLEANING FUNCTIONS
# ============================================================================

@dataclass(frozen=True)
class NormalizedDate:
    """
    Immutable representation of an extracted and normalized date/timestamp.
    """
    iso_value: str                  # "2021-06-29T16:29:00Z" or "2021-06-29"
    raw_value: str                  # Original matched string
    year: int                       # Year (e.g. 2021)
    month: int                      # Month (1-12)
    day: int                        # Day (1-31)
    hour: Optional[int] = None      # Hour (0-23) in UTC, or None if date-only
    minute: Optional[int] = None    # Minute (0-59), or None
    second: Optional[int] = None    # Second (0-59), or None
    tz_offset_minutes: int = 0      # Offset from UTC in minutes
    is_date_only: bool = False      # True if no time component was in source
    confidence: float = 1.0         # Confidence score (0.0 to 1.0)
    start_char: int = 0             # Character start offset in source text
    end_char: int = 0               # Character end offset in source text


def _clean_date_string(raw: str) -> str:
    """Strips court prefixes, ordinal suffixes, and reorders inverted timestamps."""
    cleaned = PREFIX_STRIP_RE.sub("", raw.strip())
    # Convert "2021 JUN 29 PM 4:29" -> "2021 JUN 29 4:29 PM"
    cleaned = re.sub(
        r"\b(PM|AM)\s+(\d{1,2}:\d{2}(?::\d{2})?)\b",
        r"\2 \1",
        cleaned,
        flags=re.IGNORECASE
    )
    # Strip ordinal suffixes: 1st, 2nd, 3rd, 4th -> 1, 2, 3, 4
    cleaned = re.sub(r"\b(\d{1,2})(?:st|nd|rd|th)\b", r"\1", cleaned, flags=re.IGNORECASE)
    # OCR cleanups: '2O21' -> '2021'
    cleaned = re.sub(r"\b2O(\d{2})\b", r"20\1", cleaned)
    return cleaned.strip()


def normalize_date(raw_date_str: str, default_tz: str = "UTC") -> Optional[NormalizedDate]:
    """
    Parses a single raw date string into a canonical NormalizedDate in ISO 8601 UTC.
    Returns None if parsing fails or year is outside valid historical range (1900..2050).
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
        if 1900 <= yr <= 2050 and 1 <= mo <= 12 and 1 <= da <= 31 and 0 <= hr <= 23 and 0 <= mi <= 59 and 0 <= sc <= 59:
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

    # 2. Check Dot Legal Date: "2021.06.29"
    dot_match = DOT_LEGAL_DATE_RE.search(raw_cleaned)
    if dot_match:
        yr = int(dot_match.group("year"))
        mo = int(dot_match.group("month"))
        da = int(dot_match.group("day"))
        if 1900 <= yr <= 2050 and 1 <= mo <= 12 and 1 <= da <= 31:
            iso = f"{yr:04d}-{mo:02d}-{da:02d}"
            return NormalizedDate(
                iso_value=iso,
                raw_value=raw_date_str,
                year=yr, month=mo, day=da,
                hour=None, minute=None, second=None,
                tz_offset_minutes=0,
                is_date_only=True,
                confidence=0.98,
                start_char=0, end_char=len(raw_date_str)
            )

    # 3. Check Compact YYYYMMDD Date-Only: "20210629"
    compact_match = COMPACT_YYYYMMDD_RE.search(raw_cleaned)
    if compact_match and len(raw_cleaned.strip()) == 8:
        yr = int(compact_match.group("year"))
        mo = int(compact_match.group("month"))
        da = int(compact_match.group("day"))
        if 1900 <= yr <= 2050 and 1 <= mo <= 12 and 1 <= da <= 31:
            iso = f"{yr:04d}-{mo:02d}-{da:02d}"
            return NormalizedDate(
                iso_value=iso,
                raw_value=raw_date_str,
                year=yr, month=mo, day=da,
                hour=None, minute=None, second=None,
                tz_offset_minutes=0,
                is_date_only=True,
                confidence=0.95,
                start_char=0, end_char=len(raw_date_str)
            )

    # 4. General fuzzy parse with python-dateutil (dayfirst=False for US legal standard)
    try:
        tz_mapping = {k: dateutil.tz.tzoffset(k, v * 60) for k, v in TIMEZONE_OFFSETS.items()}
        dt = dateutil.parser.parse(raw_cleaned, fuzzy=True, dayfirst=False, tzinfos=tz_mapping)

        # Sanity check year
        if dt.year < 1900 or dt.year > 2050:
            return None

        # Determine if source contained explicit time component
        has_explicit_time = bool(
            re.search(r"\b\d{1,2}:\d{2}\b", raw_cleaned) or 
            re.search(r"\b(AM|PM)\b", raw_cleaned, re.IGNORECASE) or 
            ("T" in raw_cleaned and re.search(r"T\d{2}:", raw_cleaned))
        )

        if not has_explicit_time:
            iso = dt.strftime("%Y-%m-%d")
            return NormalizedDate(
                iso_value=iso,
                raw_value=raw_date_str,
                year=dt.year, month=dt.month, day=dt.day,
                hour=None, minute=None, second=None,
                tz_offset_minutes=0,
                is_date_only=True,
                confidence=0.95,
                start_char=0, end_char=len(raw_date_str)
            )
        else:
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
    for pattern in [
        CAMERA_FILENAME_RE,
        INVERTED_STAMP_RE,
        RFC_2822_RE,
        ISO_8601_RE,
        WRITTEN_DATE_RE,
        US_NUMERIC_DATE_RE,
        DOT_LEGAL_DATE_RE,
    ]:
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


def normalize_dates_from_text(
    text: str,
    metadata: Optional[Dict[str, Any]] = None,
    default_tz: str = "UTC"
) -> Tuple[Optional[str], Optional[str]]:
    """
    Infers the primary canonical date and raw date string for a document.
    Hierarchy:
    1. Metadata explicit fields ('Date', 'date', 'created', 'created_date', 'filing_date')
    2. Header stamps in text ('FILED ...', 'ENTERED ...', 'DATED ...')
    3. First extracted valid date from text body
    4. Metadata fallback ('file_mtime', 'modified')
    """
    meta = metadata or {}

    # 1. Direct metadata check
    for key in ("Date", "date", "created", "created_date", "filing_date", "timestamp"):
        if key in meta and meta[key]:
            val = str(meta[key]).strip()
            norm = normalize_date(val, default_tz=default_tz)
            if norm:
                return (norm.iso_value, val)

    # 2. Header stamp regex in first 2000 characters
    sample_text = text[:2000] if text else ""
    stamp_match = re.search(
        r"(?:FILED|ENTERED|DECIDED|DATED|RECORDED|ORDERED|SIGNED)\s*[:\s]*([^\n\r,]+(?:,\s*\d{4}|\/\d{2,4}))",
        sample_text,
        re.IGNORECASE
    )
    if stamp_match:
        stamp_raw = stamp_match.group(0).strip()
        norm = normalize_date(stamp_raw, default_tz=default_tz)
        if norm:
            return (norm.iso_value, stamp_raw)

    # 3. First extracted date in text
    extracted = extract_dates(text, default_tz=default_tz)
    if extracted:
        return (extracted[0].iso_value, extracted[0].raw_value)

    # 4. Metadata file modification date fallback
    for key in ("modified", "modified_date", "file_mtime", "mtime"):
        if key in meta and meta[key]:
            val = str(meta[key]).strip()
            norm = normalize_date(val, default_tz=default_tz)
            if norm:
                return (norm.iso_value, val)

    return (None, None)
