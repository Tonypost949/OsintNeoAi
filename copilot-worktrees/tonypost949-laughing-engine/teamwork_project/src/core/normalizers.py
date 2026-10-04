"""
Address and Entity Name Normalization Core Functions.
"""
import re
import hashlib
import functools
from typing import Tuple, Optional, Any, List
from src.core.schemas import NormalizedAddressDTO, NormalizedNameDTO

# Module-level import checks for metaphone / jellyfish to prevent sys.path overhead per call
try:
    from metaphone import doublemetaphone as _doublemetaphone
except ImportError:
    _doublemetaphone = None

try:
    import jellyfish as _jellyfish
except ImportError:
    _jellyfish = None


# USPS Standard Directional Map
DIRECTIONALS = {
    "NORTH": "N", "SOUTH": "S", "EAST": "E", "WEST": "W",
    "NORTHEAST": "NE", "NORTHWEST": "NW", "SOUTHEAST": "SE", "SOUTHWEST": "SW",
    "N.": "N", "S.": "S", "E.": "E", "W.": "W",
    "N.E.": "NE", "N.W.": "NW", "S.E.": "SE", "S.W.": "SW"
}

# USPS Standard Street Suffix Map
USPS_SUFFIXES = {
    "STREET": "ST", "STR": "ST", "ST.": "ST",
    "AVENUE": "AVE", "AV": "AVE", "AVE.": "AVE",
    "BOULEVARD": "BLVD", "BLVD.": "BLVD", "BOUL": "BLVD",
    "DRIVE": "DR", "DR.": "DR",
    "ROAD": "RD", "RD.": "RD",
    "LANE": "LN", "LN.": "LN",
    "COURT": "CT", "CT.": "CT",
    "CIRCLE": "CIR", "CIR.": "CIR",
    "PARKWAY": "PKWY", "PKWY.": "PKWY", "PARKWY": "PKWY",
    "WAY": "WAY",
    "HIGHWAY": "HWY", "HWY.": "HWY",
    "PLACE": "PL", "PL.": "PL",
    "TRAIL": "TRL", "TRL.": "TRL",
    "PLAZA": "PLZ", "PLZ.": "PLZ"
}

# Corporate Legal Entity Suffixes (Ordered strictly from longest multi-word pattern to shortest single-word pattern)
CORP_SUFFIX_PATTERNS = [
    r"\bPROFESSIONAL LIMITED LIABILITY COMPANY\b",
    r"\bLIMITED LIABILITY PARTNERSHIP\b",
    r"\bLIMITED LIABILITY COMPANY\b",
    r"\bPROFESSIONAL CORPORATION\b",
    r"\bPROFESSIONAL ASSOCIATION\b",
    r"\bNATIONAL ASSOCIATION\b",
    r"\bINCORPORATED\b",
    r"\bCORPORATION\b",
    r"\bP\.L\.L\.C\.", r"\bPLLC\b",
    r"\bL\.L\.P\.", r"\bLLP\b",
    r"\bL\.L\.C\.", r"\bLLC\b",
    r"\bLIMITED\b",
    r"\bCOMPANY\b",
    r"\bINC\.", r"\bINC\b",
    r"\bCORP\.", r"\bCORP\b",
    r"\bLTD\.", r"\bLTD\b",
    r"\bP\.C\.", r"\bPC\b",
    r"\bP\.A\.", r"\bPA\b",
    r"\bN\.A\.", r"\bNA\b",
    r"\bCO\.", r"\bCO\b",
]

# Stop Words for Core Key Generation
STOP_WORDS = {"THE", "AND", "&", "OF", "IN", "ON", "FOR", "AT", "BY"}

# ---------------------------------------------------------------------------
# Pre-Compiled Module-Level Regex Constants
# ---------------------------------------------------------------------------

COMPILED_CORP_PATTERNS: List[re.Pattern] = [
    re.compile(fr"(?:{p})(?:\s*[\.,;\s]*)$", flags=re.IGNORECASE)
    for p in CORP_SUFFIX_PATTERNS
]

COMPILED_UNIT_PATTERN: re.Pattern = re.compile(
    r"(?:#|\b(?:SUITE|STE|APT|APARTMENT|UNIT|BUILDING|BLDG|FLOOR|FL|ROOM|RM|DEPT|DEPARTMENT))\s*#?\s*([A-Z0-9\-]+)?",
    flags=re.IGNORECASE
)

COMPILED_SINGLE_LINE_STATE_ZIP: re.Pattern = re.compile(
    r"\b([A-Za-z]{2})\s+(\d{5}(?:-\d{4})?)\s*$",
    flags=re.IGNORECASE
)

COMPILED_NON_ALPHA: re.Pattern = re.compile(r"[^A-Z]")
COMPILED_NON_ALPHA_SPACE: re.Pattern = re.compile(r"[^A-Z\s]")
COMPILED_NON_DIGIT: re.Pattern = re.compile(r"[^\d]")
COMPILED_WORD_DOT_TOKENS: re.Pattern = re.compile(r"[A-Z0-9\.]+")
COMPILED_NON_WORD_AMP: re.Pattern = re.compile(r"[^\w\s&]")
COMPILED_MULTI_SPACE: re.Pattern = re.compile(r"\s+")


@functools.lru_cache(maxsize=32768)
def compute_soundex(name: Optional[str]) -> str:
    """Computes standard Soundex code for a string."""
    if not name:
        return "Z000"
    name_str = COMPILED_NON_ALPHA.sub("", str(name).upper())
    if not name_str:
        return "Z000"
    first_letter = name_str[0]
    char_map = {
        'B': '1', 'F': '1', 'P': '1', 'V': '1',
        'C': '2', 'G': '2', 'J': '2', 'K': '2', 'Q': '2', 'S': '2', 'X': '2', 'Z': '2',
        'D': '3', 'T': '3',
        'L': '4',
        'M': '5', 'N': '5',
        'R': '6'
    }
    encoded = []
    prev_code = char_map.get(first_letter, '')
    for char in name_str[1:]:
        code = char_map.get(char, '')
        if code and code != prev_code:
            encoded.append(code)
            prev_code = code
        elif not code:
            prev_code = ''
    digits = "".join(encoded) + "000"
    return (first_letter + digits[:3])


@functools.lru_cache(maxsize=32768)
def compute_double_metaphone(name: Optional[str]) -> Tuple[str, str]:
    """
    Computes Double Metaphone (Primary, Secondary) codes.
    Attempts using `metaphone` or `jellyfish` module,
    with robust pure-Python fallback.
    """
    if not name:
        return ("Z000", "Z000")
    name_str = str(name)
    if _doublemetaphone is not None:
        try:
            res = _doublemetaphone(name_str)
            return (res[0] or "Z000", res[1] or "Z000")
        except Exception:
            pass
    if _jellyfish is not None:
        try:
            dm = _jellyfish.metaphone(name_str)
            return (dm or "Z000", dm or "Z000")
        except Exception:
            pass
    soundex_val = compute_soundex(name_str)
    return (soundex_val, soundex_val)


@functools.lru_cache(maxsize=32768)
def normalize_address(
    street: Optional[str],
    city: Optional[str] = "",
    state: Optional[str] = "",
    zip_code: Optional[str] = ""
) -> NormalizedAddressDTO:
    """
    Normalizes raw address components according to USPS standards:
    - Robust null/None input handling
    - Single-line address parsing (with or without commas)
    - Uppercasing & punctuation cleaning
    - Unit / Suite / Apt extraction and stripping from street line using word-boundary agnostic regex
    - Suffix & directional standardization
    - 5-digit ZIP code zero-padding
    - SHA256 canonical address hash calculation
    """
    street_str = str(street or "").strip()
    city_str = str(city or "").strip()
    state_str = str(state or "").strip()
    zip_str = str(zip_code or "").strip()

    # Parse single combined address string if passed in street
    if not city_str and not state_str and not zip_str and street_str:
        if "," in street_str:
            parts = [p.strip() for p in street_str.split(",") if p.strip()]
            if len(parts) >= 3:
                state_zip = parts[-1].split()
                if len(state_zip) >= 2:
                    state_str = state_zip[0]
                    zip_str = state_zip[1]
                elif len(state_zip) == 1:
                    state_str = state_zip[0]
                city_str = parts[-2]
                street_str = ", ".join(parts[:-2])
            elif len(parts) == 2:
                street_str = parts[0]
                state_zip = parts[1].split()
                if len(state_zip) == 3:
                    city_str = state_zip[0]
                    state_str = state_zip[1]
                    zip_str = state_zip[2]
                elif len(state_zip) == 2:
                    state_str = state_zip[0]
                    zip_str = state_zip[1]
                elif len(state_zip) == 1:
                    city_str = state_zip[0]
        else:
            # Single-line address without commas: match State + Zip at end
            match = COMPILED_SINGLE_LINE_STATE_ZIP.search(street_str)
            if match:
                state_str = match.group(1)
                zip_str = match.group(2)
                remainder = street_str[:match.start()].strip()
                
                # Split remainder into street address and city using unit marker or last word
                unit_match = COMPILED_UNIT_PATTERN.search(remainder)
                if unit_match:
                    split_idx = unit_match.end()
                    street_part = remainder[:split_idx].strip()
                    city_part = remainder[split_idx:].strip()
                    if city_part:
                        street_str = street_part
                        city_str = city_part
                    else:
                        street_str = remainder
                else:
                    tokens = remainder.split()
                    if len(tokens) > 2:
                        street_str = " ".join(tokens[:-1])
                        city_str = tokens[-1]
                    else:
                        street_str = remainder

    # Clean & Uppercase
    raw_street = street_str.upper().strip()
    city_clean = COMPILED_NON_ALPHA_SPACE.sub("", city_str.upper().strip())
    state_clean = COMPILED_NON_ALPHA.sub("", state_str.upper().strip())[:2]
    
    # Pad & clean ZIP code
    zip_digits = COMPILED_NON_DIGIT.sub("", zip_str)
    if len(zip_digits) >= 5:
        zip_clean = zip_digits[:5]
    elif zip_digits:
        zip_clean = zip_digits.zfill(5)
    else:
        zip_clean = "00000"

    # Extract & Strip Unit / Suite / Apartment
    unit_match = COMPILED_UNIT_PATTERN.search(raw_street)
    extracted_unit = unit_match.group(0).strip() if unit_match else None
    
    street_no_unit = COMPILED_UNIT_PATTERN.sub("", raw_street).strip()
    street_no_unit = COMPILED_MULTI_SPACE.sub(" ", street_no_unit)

    # Tokenize street string
    tokens = COMPILED_WORD_DOT_TOKENS.findall(street_no_unit)
    norm_tokens = []
    for token in tokens:
        token_upper = token.upper()
        token_no_dot = token_upper.rstrip(".")
        if token_upper in DIRECTIONALS:
            norm_tokens.append(DIRECTIONALS[token_upper])
        elif token_no_dot in DIRECTIONALS:
            norm_tokens.append(DIRECTIONALS[token_no_dot])
        elif token_upper in USPS_SUFFIXES:
            norm_tokens.append(USPS_SUFFIXES[token_upper])
        elif token_no_dot in USPS_SUFFIXES:
            norm_tokens.append(USPS_SUFFIXES[token_no_dot])
        else:
            norm_tokens.append(token_no_dot if token_no_dot else token_upper)

    normalized_street = " ".join(norm_tokens)
    
    # Construct canonical single-line normalized address string
    normalized_str = f"{normalized_street}, {city_clean}, {state_clean} {zip_clean}".strip(", ")
    
    # Compute SHA256 hash
    address_hash = hashlib.sha256(normalized_str.encode("utf-8")).hexdigest()

    return NormalizedAddressDTO(
        street=normalized_street,
        city=city_clean,
        state=state_clean,
        zip_code=zip_clean,
        unit=extracted_unit,
        normalized_str=normalized_str,
        address_hash=address_hash
    )


@functools.lru_cache(maxsize=32768)
def normalize_entity_name(raw_name: Optional[str], is_business: bool = True) -> NormalizedNameDTO:
    """
    Normalizes business or individual entity names:
    - Robust null/None input handling
    - Business suffix stripping anchored at end-of-string
    - Pre-punctuation dotted corporate suffix handling
    - Core key generation with fallbacks for stop-word-only names
    - Soundex & Double Metaphone calculation
    """
    if raw_name is None:
        raw_name = ""
    raw_name_str = str(raw_name).strip()
    if not raw_name_str:
        return NormalizedNameDTO(
            raw_name="",
            clean_name="Unknown Entity",
            core_key="UNKNOWN_ENTITY",
            soundex="Z000",
            double_metaphone=("Z000", "Z000"),
            is_business=is_business
        )

    name_clean = raw_name_str.upper().strip()

    if is_business:
        # Strip corporate suffixes from the end of entity name
        changed = True
        while changed:
            changed = False
            for compiled_pattern in COMPILED_CORP_PATTERNS:
                new_name = compiled_pattern.sub("", name_clean).strip()
                if new_name != name_clean:
                    name_clean = new_name
                    changed = True
                    break

    # Strip non-alphanumeric chars except ampersand
    name_clean = COMPILED_NON_WORD_AMP.sub(" ", name_clean)
    name_clean = COMPILED_MULTI_SPACE.sub(" ", name_clean).strip()

    if not name_clean:
        name_clean = raw_name_str.upper().strip()
        name_clean = COMPILED_NON_WORD_AMP.sub(" ", name_clean)
        name_clean = COMPILED_MULTI_SPACE.sub(" ", name_clean).strip()

    clean_name = name_clean.title() if name_clean else raw_name_str.title()

    # Build core key with stop-word removal
    tokens = [t for t in name_clean.split() if t not in STOP_WORDS]
    if tokens:
        core_key = " ".join(tokens)
    else:
        core_key = name_clean if name_clean else raw_name_str.upper()
    
    # Phonetic codes
    soundex_code = compute_soundex(name_clean)
    dm_tuple = compute_double_metaphone(name_clean)

    return NormalizedNameDTO(
        raw_name=raw_name_str,
        clean_name=clean_name,
        core_key=core_key,
        soundex=soundex_code,
        double_metaphone=dm_tuple,
        is_business=is_business
    )
