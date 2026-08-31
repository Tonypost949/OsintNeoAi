import re

entities = [
    "Woodbridge Meadows Apartments, LLC",
    "Woodbridge Meadows Apartments LLC",
    "Woodbridge Meadows Apartments, L.L.C.",
    "TA Group LLC",
    "FPS Strategies LLC",
    "Wallace, Richardson, Sontag & Le LLP",
    "Wallace, Richardson, Sontag & Le, L.L.P.",
    "JL Group LLC",
    "Advanced Real Estate Services, Inc.",
    "Advanced Real Estate Services Incorporated",
    "Shea Homes Limited Partnership",
    "Mercy House Living Centers",
    "Dog's Day Productions",
    "Anaheim Chamber of Commerce",
    "City of Anaheim",
    "Orange County Health Care Agency (OCHCA)",
    "Hon. Carmen Luege",
    "Judge Cynthia Bashant",
    "FBI SA Brian Adkins",
    "Special Agent Bradley H. Zartman",
    "Mayor Harry Sidhu",
    "Todd Ament"
]

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

HONORIFIC_RE = re.compile(
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

print("=== TESTING ENTITY CLEANING & SUFFIX CANONICALIZATION ===")
for raw in entities:
    # 1. Clean honorifics
    cleaned = HONORIFIC_RE.sub("", raw.strip())
    # 2. Check suffix
    m = CORP_SUFFIX_RE.search(cleaned)
    if m:
        # Find which group matched
        matched_group = [k for k, v in m.groupdict().items() if v is not None][0]
        canon_suffix = matched_group.upper()
        stem = cleaned[:m.start()].rstrip(" ,.")
        canonical_name = f"{stem} {canon_suffix}"
    else:
        stem = cleaned
        canon_suffix = None
        canonical_name = cleaned
        
    print(f"RAW   : {raw}")
    print(f"  CLEANED   : {cleaned}")
    print(f"  STEM      : {stem}")
    print(f"  CANONICAL : {canonical_name} (Suffix: {canon_suffix})")
