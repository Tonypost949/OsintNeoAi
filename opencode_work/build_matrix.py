"""
build_matrix.py — Master OSINT Node Matrix Builder
====================================================
Every entity is a node. Every node has: timeline, authority, evidence links, 
and relationships to other nodes. Sub-components are also nodes.
"""
import sqlite3
import json
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "master_index.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS nodes (
    node_id TEXT PRIMARY KEY,
    node_type TEXT,         -- PERSON, ORG, CASE, CONTRACT, PROPERTY, FUNDING, MEDIA, CREDENTIAL
    label TEXT,
    authority TEXT,         -- What legal/regulatory authority governs this node
    status TEXT,            -- ACTIVE, VOID, PENDING, CONFIRMED, ALLEGED
    notes TEXT,
    created_at TEXT
);

CREATE TABLE IF NOT EXISTS node_timeline (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    node_id TEXT,
    event_date TEXT,
    event_type TEXT,        -- CREATED, ACTION, ATTACK, EVIDENCE, FILING, PAYMENT
    description TEXT,
    source TEXT,
    FOREIGN KEY (node_id) REFERENCES nodes(node_id)
);

CREATE TABLE IF NOT EXISTS node_evidence (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    node_id TEXT,
    evidence_type TEXT,     -- DOCUMENT, AUDIO, IMAGE, DATABASE, PUBLIC_RECORD, DRIVE_FILE
    label TEXT,
    drive_link TEXT,
    local_path TEXT,
    verified INTEGER DEFAULT 0,
    FOREIGN KEY (node_id) REFERENCES nodes(node_id)
);

CREATE TABLE IF NOT EXISTS node_relationships (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    from_node TEXT,
    to_node TEXT,
    relationship TEXT,      -- FUNDS, EMPLOYS, OWNS, ATTACKS, CONTRACTS, REFERS_TO, COVERS_UP
    strength TEXT,          -- CONFIRMED, STRONG, MODERATE, ALLEGED
    notes TEXT,
    FOREIGN KEY (from_node) REFERENCES nodes(node_id),
    FOREIGN KEY (to_node) REFERENCES nodes(node_id)
);
"""

NODES = [
    # === THE ARCHITECT ===
    ("ARCH_001", "PERSON", "The Architect (Investigator)", 
     "Fiduciary / NFA Associated Person 2011 / Series 3 / Press (America Kids Magazine)",
     "ACTIVE", "Federally regulated compliance professional. Pre-2021 record clean."),

    # === CREDENTIALS ===
    ("CRED_001", "CREDENTIAL", "NFA Associated Person", "CFTC / National Futures Association", 
     "HISTORICAL", "Approved 2011. Series 3 Futures Broker. Federal fiduciary standard applies."),
    ("CRED_002", "CREDENTIAL", "California Real Estate License", "California DRE", 
     "HISTORICAL", "Active through ~2005-2014. Brokerage owner's assistant then independent."),
    ("CRED_003", "CREDENTIAL", "America Kids Magazine", "First Amendment / CA Shield Law", 
     "HISTORICAL", "Published media. Activates press protections and reporter's shield."),

    # === LEGAL CASES ===
    ("CASE_001", "CASE", "Case No. HBE00003868", "Orange County Superior Court", 
     "INACTIVE", "2016 civil infraction. Unpursued. Pre-attack baseline record."),
    ("CASE_002", "CASE", "Case No. 16P001799", "Orange County Family Law", 
     "INACTIVE", "Child support setup 2021. Proactive filing. No criminal element."),
    ("CASE_003", "CASE", "Case No. 30-2021-01201327-CL-UD-CJC", "Orange County Superior Court",
     "VOID", "Woodbridge Meadows eviction. Judge disqualified under CCP 170.6. Order VOID AB INITIO."),
    ("CASE_004", "CASE", "Case No. 8:26-cv-00348 (Knabb v. City of HB)", "USDC Central District CA",
     "ACTIVE", "Federal case: toxic endangerment and regulatory fraud at HBNC."),

    # === CORPORATE ENTITIES ===
    ("ORG_001", "ORG", "Shea Homes / Shea Homes Arizona", "California DRE / Corporate", 
     "ALLEGED", "First attack entity. Extortion trigger that preceded the void eviction."),
    ("ORG_002", "ORG", "Woodbridge Meadows Apartments LLC", "California Landlord-Tenant Law",
     "ALLEGED", "Landlord entity in the void 2021 eviction case."),
    ("ORG_003", "ORG", "RPM Modular", "City of Huntington Beach Contract",
     "CONFIRMED", "$2.2M contract to build HBNC on contaminated land."),
    ("ORG_004", "ORG", "Mercy House", "City of Huntington Beach / HUD",
     "CONFIRMED", "HBNC operator. EPA document found in Drive: mercyhouse epa Bridges_Tower_HealthWatch.pdf"),
    ("ORG_005", "ORG", "211 OC / Orange County United Way", "Federal HMIS / HUD",
     "CONFIRMED", "Administers HMIS database for OC. Controls referral pipeline into HBNC."),
    ("ORG_006", "ORG", "City of Huntington Beach", "California Municipal Code / HUD",
     "CONFIRMED", "Issued fraudulent CEQA emergency exemption. Awarded RPM Modular contract."),

    # === GOVERNMENT / FUNDING ===
    ("GOV_001", "FUNDING", "Governor Newsom / HHAP Program", "California DHCS / HCD",
     "CONFIRMED", "State funding pipeline: HHAP grants flow to OC → 211 → HBNC referral chain."),
    ("GOV_002", "FUNDING", "HUD / CARES Act / ARPA Federal Funds", "US HUD / False Claims Act",
     "CONFIRMED", "Federal funds accepted while bypassing CEQA/NEPA environmental review = FCA violation."),

    # === THE PROPERTY / CRIME SCENE ===
    ("PROP_001", "PROPERTY", "HBNC Site — 17631 Cameron Lane, HB CA 92647",
     "DTSC / CEQA / Title 27", "CONFIRMED",
     "Coordinates: 33.7142N -117.9945W. Hexavalent Chromium + Arsenic contamination confirmed."),
    ("PROP_002", "PROPERTY", "1994 Toxic Industrial Footprint", "DTSC Historical Record",
     "CONFIRMED", "1994 orthophoto from HB GIS server shows pre-asphalt industrial zone footprint."),

    # === EVIDENCE FILES IN DRIVE ===
    ("EVID_001", "MEDIA", "RICO_Network_Chart.md", "Investigative Journalism / Drive",
     "CONFIRMED", ""),
    ("EVID_002", "MEDIA", "Emergency_Criminal_Referral_HBNC.md", "Investigative Journalism / Drive",
     "CONFIRMED", ""),
    ("EVID_003", "MEDIA", "RICO NETWORK ANALYSIS Presentation", "Investigative Journalism / Drive",
     "CONFIRMED", ""),
    ("EVID_004", "MEDIA", "mercyhouse epa Bridges_Tower_HealthWatch_2017_V2.pdf",
     "EPA / Environmental Record", "CONFIRMED", "EPA document directly naming HBNC operator Mercy House."),
    ("EVID_005", "MEDIA", "California hides toxic waste under homeless shelters.mp3",
     "First Amendment / Press", "CONFIRMED", "Audio recording in Drive."),
    ("EVID_006", "MEDIA", "Orange_County_Administrative_Attacks_and_Toxic_Shelters.m4a",
     "First Amendment / Press", "CONFIRMED", "Audio recording in Drive."),
    ("EVID_007", "MEDIA", "Contamination-and-Toxic-Substances worksheets",
     "EPA / DTSC", "CONFIRMED", "Contamination documentation in Drive."),
    ("EVID_008", "MEDIA", "HB 1994 Aerial Orthophoto", "City of HB GIS Server",
     "CONFIRMED", "Pulled directly from gis.huntingtonbeachca.gov. Shows pre-encapsulation footprint."),
]

TIMELINE_EVENTS = [
    ("ARCH_001", "2011-08-12", "CREDENTIAL", "NFA Associated Person Approved under CFTC framework", "NFA Screenshot in Drive"),
    ("ARCH_001", "2005-01-01", "CREDENTIAL", "California Real Estate License active", "Resume in Drive"),
    ("ARCH_001", "2007-01-01", "CREDENTIAL", "Series 3 Futures Broker license active in California", "NFA Records"),
    ("ARCH_001", "2014-01-01", "ACTION", "Pursued further industry education. License no longer needed operationally.", "Self-documented"),
    ("CASE_001", "2016-06-07", "CREATED", "Case HBE00003868 filed - civil infraction, unpursued.", "OC Court Screenshot in Drive"),
    ("CASE_002", "2021-01-15", "CREATED", "Child support hearing scheduled - proactive filing.", "OC Court Screenshot in Drive"),
    ("ARCH_001", "2021-01-01", "ATTACK", "Shea Homes extortion — first attack against fiduciary status", "Self-documented / Drive"),
    ("CASE_003", "2021-01-01", "CREATED", "Woodbridge Meadows eviction filed against Architect", "OC Court Records"),
    ("CASE_003", "2021-01-01", "ACTION", "Architect files ex parte motion + peremptory challenge under CCP 170.6", "Self-documented"),
    ("CASE_003", "2021-01-01", "ACTION", "Disqualified judge ignores challenge and issues eviction order — VOID AB INITIO", "Legal analysis"),
    ("ARCH_001", "2021-06-01", "ATTACK", "Post-void-order retaliatory warrants cascade begins on CLETS database", "Self-documented"),
    ("ORG_006", "2022-01-01", "ACTION", "City of HB issues fraudulent CEQA Class 1 Emergency Exemption for HBNC", "Public records / Drive"),
    ("ORG_003", "2022-01-01", "CONTRACT", "$2.2M RPM Modular contract awarded to build HBNC on contaminated site", "City contract records"),
    ("PROP_001", "2022-01-01", "ACTION", "Asphalt cap installed over hex chromium/arsenic plume. No DTSC mitigation.", "Site analysis"),
    ("CASE_004", "2026-01-01", "FILING", "Federal case Knabb v. City of HB filed in USDC Central District CA", "PACER"),
]

RELATIONSHIPS = [
    ("ARCH_001", "CRED_001", "HOLDS", "CONFIRMED", "NFA AP 2011 under CFTC"),
    ("ARCH_001", "CRED_002", "HOLDS", "CONFIRMED", "CA Real Estate License 2005-2014"),
    ("ARCH_001", "CRED_003", "HOLDS", "CONFIRMED", "America Kids Magazine publisher - press status"),
    ("ORG_001", "ARCH_001", "ATTACKS", "CONFIRMED", "Shea Homes extortion triggered first attack on fiduciary"),
    ("ORG_002", "ARCH_001", "ATTACKS", "CONFIRMED", "Woodbridge Meadows eviction - void order"),
    ("CASE_003", "ARCH_001", "ATTACKS", "VOID", "Eviction case - void ab initio - root of retaliatory cascade"),
    ("ORG_006", "PROP_001", "OWNS", "CONFIRMED", "City of HB controls HBNC site"),
    ("ORG_006", "ORG_003", "CONTRACTS", "CONFIRMED", "$2.2M contract to build HBNC"),
    ("ORG_003", "PROP_001", "BUILT_ON", "CONFIRMED", "RPM Modular built shelter on contaminated land"),
    ("ORG_004", "PROP_001", "OPERATES", "CONFIRMED", "Mercy House operates HBNC at the site"),
    ("ORG_005", "PROP_001", "REFERS_TO", "CONFIRMED", "211 OC HMIS system feeds referral pipeline into HBNC"),
    ("GOV_001", "ORG_005", "FUNDS", "CONFIRMED", "HHAP grants flow through state to 211 OC / HMIS"),
    ("GOV_002", "ORG_006", "FUNDS", "CONFIRMED", "Federal HUD/CARES/ARPA funds to City of HB for HBNC"),
    ("ORG_006", "GOV_002", "DEFRAUDS", "CONFIRMED", "False CEQA compliance claims to draw down federal funds = FCA violation"),
    ("PROP_001", "PROP_002", "BUILT_ON", "CONFIRMED", "HBNC sits directly on 1994 toxic industrial footprint"),
    ("EVID_004", "ORG_004", "DOCUMENTS", "CONFIRMED", "EPA doc directly references Mercy House"),
    ("EVID_008", "PROP_002", "DOCUMENTS", "CONFIRMED", "1994 orthophoto shows pre-encapsulation footprint"),
]

def build_matrix():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Create tables
    for stmt in SCHEMA.strip().split(";"):
        stmt = stmt.strip()
        if stmt:
            c.execute(stmt)
    
    print("[+] Schema created/verified.")

    # Insert nodes
    for n in NODES:
        c.execute("""
            INSERT OR REPLACE INTO nodes (node_id, node_type, label, authority, status, notes, created_at)
            VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
        """, n)
    print(f"[+] {len(NODES)} nodes inserted.")

    # Insert timeline events
    for t in TIMELINE_EVENTS:
        c.execute("""
            INSERT INTO node_timeline (node_id, event_date, event_type, description, source)
            VALUES (?, ?, ?, ?, ?)
        """, t)
    print(f"[+] {len(TIMELINE_EVENTS)} timeline events inserted.")

    # Insert relationships
    for r in RELATIONSHIPS:
        c.execute("""
            INSERT INTO node_relationships (from_node, to_node, relationship, strength, notes)
            VALUES (?, ?, ?, ?, ?)
        """, r)
    print(f"[+] {len(RELATIONSHIPS)} relationships inserted.")

    conn.commit()
    conn.close()
    print("\n[DONE] Master matrix built. Query it with: SELECT * FROM nodes;")
    print(f"    Database: {DB_PATH}")

if __name__ == "__main__":
    build_matrix()
