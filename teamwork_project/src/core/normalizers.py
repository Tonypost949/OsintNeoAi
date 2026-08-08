"""
Address and Entity Name Normalization Core Functions.
"""
import re
import hashlib
from typing import Tuple, Optional
from src.core.schemas import NormalizedAddressDTO, NormalizedNameDTO

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

# Corporate Legal Entity Suffixes (regex patterns)
CORP_SUFFIX_PATTERNS = [
    r"\bLIMITED LIABILITY COMPANY\b",
    r"\bPROFESSIONAL LIMITED LIABILITY COMPANY\b",
    r"\bLIMITED LIABILITY PARTNERSHIP\b",
    r"\bPROFESSIONAL CORPORATION\b",
    r"\bPROFESSIONAL ASSOCIATION\b",
    r"\bNATIONAL ASSOCIATION\b",
    r"\bINCORPORATED\b",
    r"\bCORPORATION\b",
    r"\bLIMITED\b",
    r"\bCOMPANY\b",
    r"\bL\.L\.C\.\b", r"\bLLC\b",
    r"\bINC\.\b", r"\bINC\b",
    r"\bCORP\.\b", r"\bCORP\b",
    r"\bCO\.\b", r"\bCO\b",
    r"\bLTD\.\b", r"\bLTD\b",
    r"\bL\.L\.P\.\b", r"\bLLP\b",
    r"\bP\.L\.L\.C\.\b", r"\bPLLC\b",
    r"\bP\.C\.\b", r"\bPC\b",
    r"\bP\.A\.\b", r"\bPA\b",
    r"\bN\.A\.\b", r"\bNA\b",
]

# Stop Words for Core Key Generation
STOP_WORDS = {"THE", "AND", "&", "OF", "IN", "ON", "FOR", "AT", "BY"}


def compute_soundex(name: str) -> str:
    """Computes standard Soundex code for a string."""
    name = re.sub(r"[^A-Z]", "", name.upper())
    if not name:
        return "Z000"
    first_letter = name[0]
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
    for char in name[1:]:
        code = char_map.get(char, '')
        if code and code != prev_code:
            encoded.append(code)
            prev_code = code
        elif not code:
            prev_code = ''
    digits = "".join(encoded) + "000"
    return (first_letter + digits[:3])


def compute_double_metaphone(name: str) -> Tuple[str, str]:
    """
    Computes Double Metaphone (Primary, Secondary) codes.
    Attempts importing from `metaphone` or `jellyfish` module,
    with robust pure-Python fallback.
    """
    try:
        from metaphone import doublemetaphone
        return doublemetaphone(name)
    except ImportError:
        try:
            import jellyfish
            dm = jellyfish.metaphone(name)
            return (dm, dm)
        except (ImportError, AttributeError):
            # Fallback algorithm
            soundex_val = compute_soundex(name)
            return (soundex_val, soundex_val)


def normalize_address(
    street: str,
    city: str = "",
    state: str = "",
    zip_code: str = ""
) -> NormalizedAddressDTO:
    """
    Normalizes raw address components according to USPS standards:
    - Uppercasing & punctuation cleaning
    - Unit / Suite / Apt extraction and stripping from street line
    - Suffix & directional standardization
    - 5-digit ZIP code zero-padding
    - SHA256 canonical address hash calculation
    """
    # If a single combined address string was passed into street:
    if not city and not state and not zip_code and "," in street:
        parts = [p.strip() for p in street.split(",") if p.strip()]
        if len(parts) >= 3:
            state_zip = parts[-1].split()
            if len(state_zip) >= 2:
                state = state_zip[0]
                zip_code = state_zip[1]
            elif len(state_zip) == 1:
                state = state_zip[0]
            city = parts[-2]
            street = ", ".join(parts[:-2])
        elif len(parts) == 2:
            street = parts[0]
            state_zip = parts[1].split()
            if len(state_zip) == 3:
                city = state_zip[0]
                state = state_zip[1]
                zip_code = state_zip[2]
            elif len(state_zip) == 2:
                state = state_zip[0]
                zip_code = state_zip[1]
            elif len(state_zip) == 1:
                city = state_zip[0]

    # Clean & Uppercase
    raw_street = street.upper().strip()
    city_clean = re.sub(r"[^A-Z\s]", "", city.upper().strip())
    state_clean = re.sub(r"[^A-Z]", "", state.upper().strip())[:2]
    
    # Pad & clean ZIP code
    zip_digits = re.sub(r"[^\d]", "", zip_code)
    if len(zip_digits) >= 5:
        zip_clean = zip_digits[:5]
    elif zip_digits:
        zip_clean = zip_digits.zfill(5)
    else:
        zip_clean = "00000"

    # Extract & Strip Unit / Suite / Apartment
    unit_pattern = r"\b(SUITE|STE|APT|APARTMENT|UNIT|BUILDING|BLDG|FLOOR|FL|#)\s*([A-Z0-9\-]+)?\b"
    unit_match = re.search(unit_pattern, raw_street)
    extracted_unit = unit_match.group(0) if unit_match else None
    street_no_unit = re.sub(unit_pattern, "", raw_street).strip()
    street_no_unit = re.sub(r"\s+", " ", street_no_unit)

    # Tokenize street string
    tokens = re.findall(r"[A-Z0-9\.]+", street_no_unit)
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


def normalize_entity_name(raw_name: str, is_business: bool = True) -> NormalizedNameDTO:
    """
    Normalizes business or individual entity names:
    - Upper-casing & punctuation stripping
    - Business suffix stripping (LLC, INC, CORP, etc.)
    - Core key generation (stop-word removal)
    - Soundex & Double Metaphone calculation
    """
    name_clean = raw_name.upper().strip()
    # Strip punctuation except ampersand
    name_clean = re.sub(r"[^\w\s&]", " ", name_clean)
    name_clean = re.sub(r"\s+", " ", name_clean).strip()

    if is_business:
        for pattern in CORP_SUFFIX_PATTERNS:
            name_clean = re.sub(pattern, "", name_clean, flags=re.IGNORECASE).strip()
        name_clean = re.sub(r"\s+", " ", name_clean).strip()

    clean_name = name_clean.title() if name_clean else raw_name.title()

    # Build core key
    tokens = [t for t in name_clean.split() if t not in STOP_WORDS]
    core_key = " ".join(tokens) if tokens else name_clean

    # Phonetic codes
    soundex_code = compute_soundex(name_clean)
    dm_tuple = compute_double_metaphone(name_clean)

    return NormalizedNameDTO(
        raw_name=raw_name,
        clean_name=clean_name,
        core_key=core_key,
        soundex=soundex_code,
        double_metaphone=dm_tuple,
        is_business=is_business
    )
