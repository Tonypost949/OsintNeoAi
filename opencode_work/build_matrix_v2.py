"""
build_matrix_v2.py — Authority-First OSINT Node Matrix
=======================================================
The correct build order:
  1. AUTHORITY SOURCE (what law/charter/regulation grants power)
  2. AUTHORITY TIMELINE (when granted, when expired, when exceeded)
  3. AUTHORITY STATUS (valid, exceeded, void, fraudulently obtained)
  4. NODES (entities derive their standing FROM their authority chain)
  5. RELATIONSHIPS (connections flow THROUGH the authority chain)

A claim without an authority source is not in the matrix.
"""
import sqlite3, os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "master_index.db")

SCHEMA_V2 = [
# -----------------------------------------------------------------------
# AUTHORITY SOURCES — the legal/regulatory foundations everything derives from
# -----------------------------------------------------------------------
"""CREATE TABLE IF NOT EXISTS authority_sources (
    auth_id       TEXT PRIMARY KEY,
    auth_type     TEXT,       -- FEDERAL_LAW, STATE_LAW, LOCAL_CODE, COURT_RULE, CONSTITUTION
    citation      TEXT,       -- e.g. "18 U.S.C. § 1961" or "CA PRC § 21000"
    description   TEXT,
    jurisdiction  TEXT        -- FEDERAL, STATE_CA, OC_COUNTY, CITY_HB
)""",

# -----------------------------------------------------------------------
# AUTHORITY GRANTS — who gave authority to whom, and when
# -----------------------------------------------------------------------
"""CREATE TABLE IF NOT EXISTS authority_grants (
    grant_id       TEXT PRIMARY KEY,
    auth_id        TEXT,       -- references authority_sources
    grantor_node   TEXT,       -- who gave the authority
    grantee_node   TEXT,       -- who received it
    granted_date   TEXT,       -- YYYY-MM-DD or YYYY
    expiry_date    TEXT,       -- NULL if indefinite
    grant_status   TEXT,       -- VALID, EXPIRED, EXCEEDED, VOID, FRAUDULENT
    exceeded_date  TEXT,       -- date authority was exceeded/abused
    exceeded_how   TEXT,       -- description of the violation
    FOREIGN KEY (auth_id) REFERENCES authority_sources(auth_id)
)""",

# -----------------------------------------------------------------------
# NODES — entities, people, orgs, cases, properties, evidence
# -----------------------------------------------------------------------
"""CREATE TABLE IF NOT EXISTS nodes (
    node_id       TEXT PRIMARY KEY,
    node_type     TEXT,   -- PERSON, ORG, CASE, CONTRACT, PROPERTY, FUNDING, CREDENTIAL, EVIDENCE
    label         TEXT,
    primary_auth  TEXT,   -- what authority_source governs this node
    status        TEXT,   -- ACTIVE, VOID, CONFIRMED, ALLEGED, HISTORICAL
    notes         TEXT
)""",

# -----------------------------------------------------------------------
# NODE TIMELINE — every event on a node anchored to a date + authority
# -----------------------------------------------------------------------
"""CREATE TABLE IF NOT EXISTS node_timeline (
    tl_id         INTEGER PRIMARY KEY AUTOINCREMENT,
    node_id       TEXT,
    event_date    TEXT,
    event_type    TEXT,   -- AUTHORITY_GRANTED, AUTHORITY_EXCEEDED, AUTHORITY_VOID,
                          -- ACTION, ATTACK, FILING, PAYMENT, CONSTRUCTION, EVIDENCE
    auth_id       TEXT,   -- which authority applies to this event (NULL if none)
    description   TEXT,
    source        TEXT,   -- document, case number, or Drive link
    verified      INTEGER DEFAULT 0,  -- 1 = verified with evidence
    FOREIGN KEY (node_id) REFERENCES nodes(node_id),
    FOREIGN KEY (auth_id) REFERENCES authority_sources(auth_id)
)""",

# -----------------------------------------------------------------------
# NODE RELATIONSHIPS — connections flow through authority grants
# -----------------------------------------------------------------------
"""CREATE TABLE IF NOT EXISTS node_relationships (
    rel_id        INTEGER PRIMARY KEY AUTOINCREMENT,
    from_node     TEXT,
    to_node       TEXT,
    relationship  TEXT,   -- FUNDS, EMPLOYS, CONTRACTS, ATTACKS, DEFRAUDS,
                          -- COVERS_UP, BUILT_ON, OPERATES, REFERS_TO
    auth_basis    TEXT,   -- grant_id that authorized this relationship (NULL = unauthorized)
    date_started  TEXT,
    date_ended    TEXT,
    strength      TEXT,   -- CONFIRMED, STRONG, ALLEGED
    notes         TEXT
)""",

# -----------------------------------------------------------------------
# EVIDENCE LINKS — every piece of evidence tied to a node + timeline event
# -----------------------------------------------------------------------
"""CREATE TABLE IF NOT EXISTS evidence (
    ev_id         INTEGER PRIMARY KEY AUTOINCREMENT,
    node_id       TEXT,
    tl_id         INTEGER,    -- which timeline event this evidence supports
    ev_type       TEXT,       -- DOCUMENT, AUDIO, IMAGE, PUBLIC_RECORD, DRIVE_FILE, DATABASE
    label         TEXT,
    drive_link    TEXT,
    local_path    TEXT,
    verified      INTEGER DEFAULT 0,
    FOREIGN KEY (node_id) REFERENCES nodes(node_id),
    FOREIGN KEY (tl_id)   REFERENCES node_timeline(tl_id)
)"""
]

# =======================================================================
# AUTHORITY SOURCES — the legal bedrock
# =======================================================================
AUTHORITY_SOURCES = [
    # Federal
    ("AUTH_RICO",    "FEDERAL_LAW", "18 U.S.C. § 1961-1968",
     "RICO — Racketeer Influenced and Corrupt Organizations Act", "FEDERAL"),
    ("AUTH_FCA",     "FEDERAL_LAW", "31 U.S.C. § 3729 (False Claims Act)",
     "Prohibits making false statements to obtain federal funds", "FEDERAL"),
    ("AUTH_1AMEND",  "CONSTITUTION", "U.S. Constitution, First Amendment",
     "Freedom of press. Activates CA Shield Law for journalist/publisher.", "FEDERAL"),
    ("AUTH_CFTC",    "FEDERAL_LAW", "7 U.S.C. § 1 (Commodities Exchange Act)",
     "Federal fiduciary standard for futures brokers. NFA oversight.", "FEDERAL"),
    ("AUTH_PATRIOT", "FEDERAL_LAW", "USA PATRIOT Act (2001)",
     "AML/compliance obligations for Series 3 brokers. Permanent professional imprint.", "FEDERAL"),
    ("AUTH_HUD",     "FEDERAL_LAW", "42 U.S.C. § 5301 (Housing Act / CARES Act / ARPA)",
     "Federal housing funds. Accepting these while bypassing NEPA/CEQA = FCA violation.", "FEDERAL"),

    # State — Environmental
    ("AUTH_CEQA",    "STATE_LAW", "CA Public Resources Code § 21000",
     "CEQA — California Environmental Quality Act. Requires environmental review before construction.", "STATE_CA"),
    ("AUTH_DTSC",    "STATE_LAW", "CA Health & Safety Code § 25300",
     "DTSC authority over toxic/hazardous waste sites.", "STATE_CA"),
    ("AUTH_T22",     "STATE_LAW", "CA Title 22 (Health & Safety)",
     "Healthcare facility regulations applicable to residential shelters.", "STATE_CA"),
    ("AUTH_T27",     "STATE_LAW", "CA Title 27 (Environmental Protection)",
     "Hazardous waste management standards.", "STATE_CA"),
    ("AUTH_HHAP",    "STATE_LAW", "CA Gov Code § 65583 (HHAP Program)",
     "Homeless Housing, Assistance and Prevention grants from Newsom administration.", "STATE_CA"),

    # State — Court / Legal Procedure
    ("AUTH_CCP170",  "STATE_LAW", "CA Code of Civil Procedure § 170.6",
     "Peremptory challenge to disqualify a judge. Filing is automatic and immediate. Judge loses jurisdiction instantly.", "STATE_CA"),
    ("AUTH_VOID",    "STATE_LAW", "CA Case Law — Christie v. City of El Centro",
     "Orders by disqualified judges are void ab initio. Can be attacked anywhere, anytime.", "STATE_CA"),
    ("AUTH_SHIELD",  "STATE_LAW", "CA Constitution Art. I § 2(b) — Reporter's Shield Law",
     "Immunizes journalists from contempt for refusing to disclose sources or unpublished data.", "STATE_CA"),
    ("AUTH_PFB",     "STATE_LAW", "CA Business & Professions Code § 6500 (Professional Fiduciaries Bureau)",
     "Regulates court-appointed conservators/guardians. Does NOT apply to federal compliance professionals.", "STATE_CA"),

    # Local
    ("AUTH_CITYCHARTER", "LOCAL_CODE", "Huntington Beach City Charter + CA Public Contract Code",
     "Authority to award municipal contracts. Requires valid CEQA clearance first.", "CITY_HB"),
    ("AUTH_HMIS",    "FEDERAL_LAW", "HUD 24 CFR Part 578 (HMIS Requirements)",
     "Federal mandate for HMIS data system. Administered by 211 OC in Orange County.", "OC_COUNTY"),
]

# =======================================================================
# NODES — now anchored to their authority source
# =======================================================================
NODES = [
    # --- THE ARCHITECT ---
    ("ARCH_001", "PERSON", "The Architect (Investigator/Fiduciary/Press)",
     "AUTH_CFTC", "ACTIVE",
     "NFA Associated Person (2011). Series 3. CA Real Estate. America Kids Magazine publisher. "
     "Pre-2021 record clean. Post-2021 record = fruit of void order (CASE_003)."),

    # --- CREDENTIALS (sub-nodes of ARCH_001) ---
    ("CRED_NFA",  "CREDENTIAL", "NFA Associated Person — Approved 2011",
     "AUTH_CFTC",    "HISTORICAL", "Federally vetted under CFTC/CEA. Fiduciary standard is permanent professional imprint."),
    ("CRED_RE",   "CREDENTIAL", "CA Real Estate License",
     "AUTH_PFB",     "HISTORICAL", "Active 2005-2014. Does not require renewal to reference historical fiduciary status."),
    ("CRED_PRESS","CREDENTIAL", "America Kids Magazine — Publisher",
     "AUTH_1AMEND",  "HISTORICAL", "Activates First Amendment press protection and CA Reporter's Shield Law."),

    # --- LEGAL CASES ---
    ("CASE_001", "CASE", "Case HBE00003868 (2016 infraction)",
     "AUTH_CCP170", "INACTIVE", "Unpursued civil infraction. Part of clean pre-2021 baseline."),
    ("CASE_002", "CASE", "Case 16P001799 (Child Support 2021)",
     "AUTH_CCP170", "INACTIVE", "Proactive filing by Architect. No criminal element."),
    ("CASE_003", "CASE", "Case 30-2021-01201327-CL-UD-CJC (Woodbridge Meadows Eviction)",
     "AUTH_VOID",   "VOID",
     "ROOT OF ATTACK. Architect filed timely CCP 170.6 challenge. Judge ignored it = lost jurisdiction. "
     "All orders VOID AB INITIO. Warrants derived from this = no valid legal authority."),
    ("CASE_004", "CASE", "Case 8:26-cv-00348 Knabb v. City of HB",
     "AUTH_RICO",   "ACTIVE", "Federal RICO/toxic endangerment case. USDC Central District CA."),

    # --- CORPORATE ENTITIES ---
    ("ORG_SHEA",  "ORG", "Shea Homes / Shea Homes Arizona",
     "AUTH_CITYCHARTER", "ALLEGED",
     "Extortion trigger. First attack on Architect's fiduciary status preceding void eviction."),
    ("ORG_WB",    "ORG", "Woodbridge Meadows Apartments LLC",
     "AUTH_CITYCHARTER", "ALLEGED", "Landlord in void 2021 eviction. Beneficiary of void order."),
    ("ORG_RPM",   "ORG", "RPM Modular",
     "AUTH_CITYCHARTER", "CONFIRMED",
     "$2.2M contract to build HBNC. Contract awarded AFTER fraudulent CEQA exemption = no valid construction authority."),
    ("ORG_MERCY", "ORG", "Mercy House",
     "AUTH_HUD",         "CONFIRMED",
     "HBNC operator. Named in EPA document: mercyhouse epa Bridges_Tower_HealthWatch_2017.pdf"),
    ("ORG_211",   "ORG", "211 OC / Orange County United Way",
     "AUTH_HMIS",        "CONFIRMED",
     "Administers HMIS database. Controls referral pipeline into HBNC. Acquired by OC United Way 2023."),
    ("ORG_HB",    "ORG", "City of Huntington Beach",
     "AUTH_CITYCHARTER", "CONFIRMED",
     "Issued fraudulent CEQA Class 1 Emergency Exemption. Awarded RPM Modular contract without valid environmental authority."),

    # --- FUNDING NODES ---
    ("FUND_HHAP", "FUNDING", "Newsom Administration — HHAP Grants",
     "AUTH_HHAP",  "CONFIRMED", "State funds flow: Newsom HHAP -> OC -> 211 OC -> HMIS -> HBNC referral pipeline."),
    ("FUND_HUD",  "FUNDING", "Federal HUD / CARES Act / ARPA",
     "AUTH_HUD",   "CONFIRMED",
     "Federal funds accepted by City of HB while submitting false CEQA compliance = False Claims Act violation."),

    # --- THE CRIME SCENE ---
    ("PROP_HBNC", "PROPERTY", "17631 Cameron Lane, Huntington Beach CA 92647 — HBNC Site",
     "AUTH_DTSC",  "CONFIRMED",
     "Hexavalent Chromium + Arsenic contamination. DTSC review bypassed via fraudulent CEQA exemption. "
     "Asphalt cap only. No mitigation. Vulnerable population placed on active toxic plume."),
    ("PROP_1994", "PROPERTY", "1994 Toxic Industrial Footprint (pre-encapsulation)",
     "AUTH_DTSC",  "CONFIRMED",
     "1994 HB GIS orthophoto proves industrial contamination zone existed before asphalt cap and construction."),

    # --- EVIDENCE NODES ---
    ("EVID_EPA",   "EVIDENCE", "mercyhouse epa Bridges_Tower_HealthWatch_2017_V2.pdf",
     "AUTH_DTSC",  "CONFIRMED", "EPA document naming Mercy House as operator of site with known contamination history."),
    ("EVID_ORTHO", "EVIDENCE", "HB 1994 Aerial Orthophoto",
     "AUTH_CEQA",  "CONFIRMED", "Pulled from official gis.huntingtonbeachca.gov. Shows 1994 footprint."),
    ("EVID_RICO",  "EVIDENCE", "RICO NETWORK ANALYSIS Presentation (Drive)",
     "AUTH_1AMEND","CONFIRMED", "Investigative journalism product. Protected under First Amendment + Shield Law."),
    ("EVID_CRIM",  "EVIDENCE", "Emergency_Criminal_Referral_HBNC.md (Drive)",
     "AUTH_RICO",  "CONFIRMED", "Draft criminal referral already prepared."),
    ("EVID_MP3",   "EVIDENCE", "California hides toxic waste under homeless shelters.mp3",
     "AUTH_1AMEND","CONFIRMED", "Audio evidence. Press product. Shield Law protected."),
    ("EVID_M4A",   "EVIDENCE", "Orange_County_Administrative_Attacks_and_Toxic_Shelters.m4a",
     "AUTH_1AMEND","CONFIRMED", "Audio recording of administrative attacks. Shield Law protected."),
]

# =======================================================================
# AUTHORITY GRANTS — who gave authority to whom and when
# =======================================================================
GRANTS = [
    # Federal grants authority to investigate via RICO
    ("GR_001", "AUTH_RICO",    "FEDERAL",   "ARCH_001", "1970-01-01", None,     "VALID",      None, None),
    # CFTC granted NFA AP status to Architect
    ("GR_002", "AUTH_CFTC",    "FEDERAL",   "CRED_NFA", "2011-08-12", None,     "VALID",      None, None),
    # CA gives HB City Charter authority
    ("GR_003", "AUTH_CITYCHARTER","STATE_CA","ORG_HB",  "1909-01-01", None,     "VALID",      None, None),
    # HB awards RPM Modular contract — but CEQA authority was fraudulently obtained
    ("GR_004", "AUTH_CITYCHARTER","ORG_HB",  "ORG_RPM", "2022-01-01", None, "FRAUDULENT",
     "2022-01-01", "CEQA Class 1 Emergency Exemption filed without valid environmental basis. DTSC review bypassed."),
    # Newsom HHAP -> OC -> 211 OC
    ("GR_005", "AUTH_HHAP",    "FUND_HHAP", "ORG_211",  "2020-01-01", None,     "VALID",      None, None),
    # Federal HUD funds to City of HB — exceeded because of false CEQA compliance claim
    ("GR_006", "AUTH_HUD",     "FUND_HUD",  "ORG_HB",   "2021-01-01", None, "EXCEEDED",
     "2022-01-01", "City accepted federal funds while submitting false environmental compliance certifications to HUD."),
    # CCP 170.6 — Architect filed challenge
    ("GR_007", "AUTH_CCP170",  "ARCH_001",  "CASE_003", "2021-01-01", None, "VOID",
     "2021-01-01", "Judge ignored timely CCP 170.6 challenge. Jurisdiction transferred by operation of law. All subsequent orders VOID."),
    # HMIS authority to 211 OC
    ("GR_008", "AUTH_HMIS",    "FUND_HUD",  "ORG_211",  "2015-01-01", None,     "VALID",      None, None),
    # First Amendment to Architect as press
    ("GR_009", "AUTH_1AMEND",  "FEDERAL",   "CRED_PRESS","2000-01-01", None,    "VALID",      None, None),
]

# =======================================================================
# TIMELINE EVENTS — every event anchored to date + authority
# =======================================================================
TIMELINE = [
    # Architect's authority chain established
    ("ARCH_001","2007-01-01","AUTHORITY_GRANTED","AUTH_CFTC",
     "Series 3 Futures Broker license active. Federally regulated fiduciary standard engaged.","NFA Records",1),
    ("ARCH_001","2011-08-12","AUTHORITY_GRANTED","AUTH_CFTC",
     "NFA Associated Person formally approved. CFTC/PATRIOT Act compliance obligations locked in.","NFA Screenshot in Drive",1),
    ("CRED_PRESS","2000-01-01","AUTHORITY_GRANTED","AUTH_1AMEND",
     "America Kids Magazine published. First Amendment press status established.","Self-documented",1),
    # Clean baseline
    ("ARCH_001","2016-06-07","ACTION","AUTH_CCP170",
     "Case HBE00003868 filed — civil infraction. Unpursued. Clean baseline record.","OC Court Screenshot in Drive",1),
    ("ARCH_001","2021-01-15","ACTION","AUTH_CCP170",
     "Child support hearing Case 16P001799. Proactive administrative filing. No criminal element.","OC Court Screenshot in Drive",1),
    # Attack sequence
    ("ORG_SHEA","2021-01-01","ATTACK",None,
     "Shea Homes extortion. First attack triggering Architect's legal defense actions.","Self-documented",0),
    ("CASE_003","2021-01-01","FILING","AUTH_CCP170",
     "Woodbridge Meadows eviction filed by ORG_WB against Architect.","OC Court",0),
    ("ARCH_001","2021-01-01","AUTHORITY_EXCEEDED","AUTH_CCP170",
     "Architect files timely peremptory challenge under CCP 170.6. By operation of law, judge loses jurisdiction at this moment.","Self-documented",1),
    ("CASE_003","2021-01-01","AUTHORITY_VOID","AUTH_VOID",
     "Judge proceeds despite challenge. ALL orders from this point VOID AB INITIO per Christie v. El Centro.","Legal analysis",1),
    ("ARCH_001","2021-06-01","ATTACK",None,
     "Retaliatory warrants cascade begins. Active in CLETS database. Automated administrative blocks trigger.","Self-documented",0),
    # HBNC fraud timeline
    ("ORG_HB","2022-01-01","AUTHORITY_EXCEEDED","AUTH_CEQA",
     "City of HB files fraudulent CEQA Class 1 Emergency Exemption. DTSC environmental review bypassed.","City public records",0),
    ("GR_006","2022-01-01","AUTHORITY_EXCEEDED","AUTH_HUD",
     "City of HB accepts federal HUD/CARES/ARPA funds while submitting false CEQA compliance certs. FCA violation triggered.","Federal funding records",0),
    ("ORG_RPM","2022-01-01","CONTRACT","AUTH_CITYCHARTER",
     "$2.2M contract awarded to RPM Modular. Contract has no valid environmental authority behind it.","City contract records",0),
    ("PROP_HBNC","2022-06-01","ACTION","AUTH_DTSC",
     "Asphalt cap installed over hex chromium + arsenic plume. No DTSC-approved mitigation plan.","Site analysis / orthophoto",0),
    ("PROP_HBNC","2022-12-01","ACTION","AUTH_T22",
     "Vulnerable population placed in HBNC on active toxic plume. Reckless endangerment. Title 22 violation.","EPA doc / site records",0),
    # Federal case
    ("CASE_004","2026-01-01","FILING","AUTH_RICO",
     "Knabb v. City of HB filed in USDC Central District CA. Federal RICO + toxic endangerment claims.","PACER",0),
]

# =======================================================================
# RELATIONSHIPS — every connection through its authority basis
# =======================================================================
RELATIONSHIPS = [
    ("ARCH_001","CRED_NFA",  "HOLDS",      "GR_002","2011-08-12",None,"CONFIRMED","NFA AP under CFTC"),
    ("ARCH_001","CRED_PRESS","HOLDS",      "GR_009","2000-01-01",None,"CONFIRMED","America Kids Magazine"),
    ("ORG_SHEA","ARCH_001",  "ATTACKS",    None,    "2021-01-01",None,"CONFIRMED","Extortion - first attack"),
    ("ORG_WB",  "ARCH_001",  "ATTACKS",    None,    "2021-01-01",None,"CONFIRMED","Void eviction case"),
    ("CASE_003","ARCH_001",  "ATTACKS",    "GR_007","2021-01-01",None,"VOID",     "Void order - no authority"),
    ("FUND_HHAP","ORG_211",  "FUNDS",      "GR_005","2020-01-01",None,"CONFIRMED","HHAP -> 211 OC pipeline"),
    ("FUND_HUD", "ORG_HB",   "FUNDS",      "GR_006","2021-01-01",None,"EXCEEDED", "Federal funds + false CEQA = FCA"),
    ("ORG_HB",  "ORG_RPM",   "CONTRACTS",  "GR_004","2022-01-01",None,"FRAUDULENT","No valid CEQA = no authority"),
    ("ORG_RPM", "PROP_HBNC", "BUILT_ON",   "GR_004","2022-01-01",None,"FRAUDULENT","Built on toxic land, fraudulent authority"),
    ("ORG_MERCY","PROP_HBNC","OPERATES",   None,    "2022-01-01",None,"CONFIRMED","Mercy House runs HBNC"),
    ("ORG_211", "PROP_HBNC", "REFERS_TO",  "GR_008","2020-01-01",None,"CONFIRMED","HMIS feeds referral pipeline"),
    ("EVID_EPA","ORG_MERCY", "DOCUMENTS",  None,    "2017-01-01",None,"CONFIRMED","EPA doc names Mercy House"),
    ("EVID_ORTHO","PROP_1994","DOCUMENTS", None,    "1994-01-01",None,"CONFIRMED","1994 orthophoto = toxic footprint"),
    ("PROP_1994","PROP_HBNC","BUILT_ON",   None,    "2022-01-01",None,"CONFIRMED","HBNC sits on 1994 toxic zone"),
    ("ORG_HB",  "PROP_HBNC", "DEFRAUDS",  "GR_004","2022-01-01",None,"CONFIRMED","Bypassed DTSC to build on toxic land"),
]

def build():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    for stmt in SCHEMA_V2:
        c.execute(stmt)
    print("[+] Schema v2 created.")

    c.executemany("INSERT OR REPLACE INTO authority_sources VALUES (?,?,?,?,?)", AUTHORITY_SOURCES)
    print(f"[+] {len(AUTHORITY_SOURCES)} authority sources loaded.")

    c.executemany("INSERT OR REPLACE INTO nodes VALUES (?,?,?,?,?,?)", NODES)
    print(f"[+] {len(NODES)} nodes loaded.")

    c.executemany("INSERT OR REPLACE INTO authority_grants VALUES (?,?,?,?,?,?,?,?,?)", GRANTS)
    print(f"[+] {len(GRANTS)} authority grants loaded.")

    c.executemany("""INSERT INTO node_timeline
        (node_id,event_date,event_type,auth_id,description,source,verified) VALUES (?,?,?,?,?,?,?)""", TIMELINE)
    print(f"[+] {len(TIMELINE)} timeline events loaded.")

    c.executemany("""INSERT INTO node_relationships
        (from_node,to_node,relationship,auth_basis,date_started,date_ended,strength,notes) VALUES (?,?,?,?,?,?,?,?)""", RELATIONSHIPS)
    print(f"[+] {len(RELATIONSHIPS)} relationships loaded.")

    conn.commit()
    conn.close()

    print("\n[DONE] Authority-first matrix v2 built in master_index.db")
    print("Tables: authority_sources, authority_grants, nodes, node_timeline, node_relationships, evidence")

if __name__ == "__main__":
    build()
