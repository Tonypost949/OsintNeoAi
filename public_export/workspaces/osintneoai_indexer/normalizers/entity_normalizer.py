"""
OsintNeoAi Indexer: Entity Normalizer & Phonetic Blocking Module
Path: C:\\OsintNeoAi\\workspaces\\osintneoai_indexer\\normalizers\\entity_normalizer.py
Milestone: M2 (Deep Text Extraction & OCR Engine) — Feature 11

Corporate legal suffix normalizer, Russell Soundex, and pure-Python Double Metaphone phonetic encoders.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Set, Tuple

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
      | Dr\.?
      | Mr\.?
      | Ms\.?
      | Mrs\.?
      | Esq\.?
    )
    \s+
    """,
    re.IGNORECASE
)

EMAIL_CLEAN_RE = re.compile(r"<[^>]+>|\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b")


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

    def substr(start: int, sub_len: int) -> str:
        return val[start:start + sub_len]

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
                else:
                    primary.append("K")
                    secondary.append("K")
                    pos += 2
                continue
            if substr(pos + 1, 1) == "N":
                if pos == 1 and is_vowel(0) and not (pos + 2 < length and val[pos + 2] == "Y"):
                    primary.append("KN")
                    secondary.append("N")
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
    """
    Immutable representation of a normalized entity with phonetic blocking codes.
    """
    raw_name: str                   # Original text
    cleaned_name: str               # Cleansed canonical string
    core_stem: str                  # Suffix-stripped stem
    canonical_suffix: Optional[str] # "LLC", "LLP", "INC", "CORP", "LP", etc.
    soundex: str                    # Russell Soundex code (e.g. "W316")
    metaphone_primary: str          # Double Metaphone primary key (e.g. "ATPR")
    metaphone_secondary: str        # Double Metaphone secondary key (e.g. "FTPR")
    entity_category: Optional[str]  # Entity category
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
    cleaned = HONORIFIC_PREFIX_RE.sub("", raw_clean).strip()

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


def extract_correspondence_parties(
    text: str,
    metadata: Optional[Dict[str, Any]] = None
) -> Tuple[Optional[str], List[str]]:
    """
    Extracts canonical sender and list of recipients from document headers, text bodies, or metadata.
    """
    meta = metadata or {}
    sender: Optional[str] = None
    recipients: List[str] = []

    # 1. Metadata extraction (e.g. email headers)
    if meta.get("From") or meta.get("from") or meta.get("sender") or meta.get("author"):
        raw_s = str(meta.get("From") or meta.get("from") or meta.get("sender") or meta.get("author"))
        cleaned_s = EMAIL_CLEAN_RE.sub("", raw_s).strip().strip("\"'")
        if cleaned_s:
            sender = cleaned_s

    if meta.get("To") or meta.get("to") or meta.get("recipients"):
        raw_to = meta.get("To") or meta.get("to") or meta.get("recipients")
        if isinstance(raw_to, list):
            for item in raw_to:
                c_to = EMAIL_CLEAN_RE.sub("", str(item)).strip().strip("\"'")
                if c_to and c_to not in recipients:
                    recipients.append(c_to)
        elif isinstance(raw_to, str):
            for part in raw_to.split(","):
                c_to = EMAIL_CLEAN_RE.sub("", part).strip().strip("\"'")
                if c_to and c_to not in recipients:
                    recipients.append(c_to)

    # 2. Text body header regexes (FROM: / TO: / MEMORANDUM FOR: / ATTN:)
    sample = text[:3000] if text else ""
    if not sender:
        from_match = re.search(r"^[ \t]*(?:FROM|SENDER|MEMORANDUM\s+FROM)\s*[:\s]+([^\n\r]+)", sample, re.MULTILINE | re.IGNORECASE)
        if from_match:
            cand = from_match.group(1).strip()
            cand_clean = EMAIL_CLEAN_RE.sub("", cand).strip().strip("\"'")
            if cand_clean:
                sender = cand_clean

    to_matches = re.finditer(r"^[ \t]*(?:TO|RECIPIENT|MEMORANDUM\s+FOR|ATTN(?:ENTION)?)\s*[:\s]+([^\n\r]+)", sample, re.MULTILINE | re.IGNORECASE)
    for tm in to_matches:
        cand_to = tm.group(1).strip()
        for item in cand_to.split(","):
            c_to = EMAIL_CLEAN_RE.sub("", item).strip().strip("\"'")
            if c_to and c_to not in recipients:
                recipients.append(c_to)

    return (sender, recipients)
