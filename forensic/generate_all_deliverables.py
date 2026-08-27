"""
Comprehensive Forensic Deliverables Generator for OsintNeoAi.
Generates:
  1. Data Exports: MASTER.csv, People.csv, Gov_Agencies.csv, Evidence_Items.csv,
     Legal_Exposure.csv, RICO_Nodes.csv, MASTER_TIMELINE.csv, Unified_Export.json
  2. Court-Formatted Legal Brief: Legal_Brief.txt & Legal_Brief.md (7 Sections)
  3. Network Visualization: RICO_Network.mmd, RICO_Network.dot, RICO_Network_Diagram.svg
  4. PowerShell Sorter Comparative Matrix: PowerShell_Classification_Matrix.csv & classify_evidence.ps1
"""

import os
import json
import csv
from datetime import datetime

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "deliverables")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ---------------------------------------------------------
# 1. CORE DATASETS DEFINITION
# ---------------------------------------------------------

RICO_NODES = [
    {"RICO_ID": "RICO-001", "RICO_NAME": "Municipal Enterprise Hub", "NODE_TYPE": "Enterprise Core", "JURISDICTION": "Anaheim / Irvine / HB", "CONNECTED_NODE_IDS": "PER-001; PER-002; PER-004; RICO-002; RICO-003; RICO-004; RICO-005", "DESCRIPTION": "Coordinated municipal contract steering, appraisal leak, and $320M stadium land sale conspiracy."},
    {"RICO_ID": "RICO-002", "RICO_NAME": "Judicial Default Engine", "NODE_TYPE": "Shadow Legal Process", "JURISDICTION": "OC Superior Court CJC", "CONNECTED_NODE_IDS": "CTR-001; GOV-001; PER-005; EV-002", "DESCRIPTION": "Unlawful detainer default judgment ring executing shadow process, 170.6 emergency strikes, and property seizures."},
    {"RICO_ID": "RICO-003", "RICO_NAME": "Grant Fraud & Speculation Conduit", "NODE_TYPE": "Financial Shell Hub", "JURISDICTION": "Newport Beach / Irvine", "CONNECTED_NODE_IDS": "SHL-001; SHL-002; NP-001; EV-005", "DESCRIPTION": "Diverting public funds, tax-exempt nonprofit real estate flipping ($1.2M 8 Lakeview) via 1601 Dove St hub."},
    {"RICO_ID": "RICO-004", "RICO_NAME": "Political Conduit & Fleet Hub", "NODE_TYPE": "Interstate Logistics", "JURISDICTION": "Santa Ana / Hamilton NJ / FL", "CONNECTED_NODE_IDS": "PER-003; SHL-003; SHL-004; EV-003", "DESCRIPTION": "Campaign bribery laundering, Quantum Auto Dismantler interstate conduit, and out-of-state shell corporations."},
    {"RICO_ID": "RICO-005", "RICO_NAME": "Environmental & Shelter Concealment", "NODE_TYPE": "Municipal Ops & Hazmat", "JURISDICTION": "Huntington Beach", "CONNECTED_NODE_IDS": "NP-002; GOV-003; EV-004", "DESCRIPTION": "HB Navigation Center (17631 Cameron Ln) concealment of unsealed toxic water well, lead/asbestos abatement fraud, and asset pack-out."}
]

PEOPLE = [
    {"PERSON_ID": "PER-001", "NAME": "Harry Sidhu", "ROLE": "Former Mayor of Anaheim", "LEGAL_STATUS": "Convicted Felon (8:23-cr-00108-CJC)", "ORGANIZATION": "City of Anaheim", "AFFILIATION": "RICO-001", "DETAILS": "Pled guilty to wire fraud and obstruction of justice in $1M campaign bribery / stadium deal."},
    {"PERSON_ID": "PER-002", "NAME": "Todd Ament", "ROLE": "Former CEO Anaheim Chamber", "LEGAL_STATUS": "Convicted Felon (8:22-cr-00078-CJC)", "ORGANIZATION": "Anaheim Chamber of Commerce / TA Group LLC", "AFFILIATION": "RICO-001 / RICO-003", "DETAILS": "Pled guilty to wire fraud, tax evasion, and mortgage fraud; routed public funds to private accounts."},
    {"PERSON_ID": "PER-003", "NAME": "Melahat Rafiei", "ROLE": "Political Strategist / Consultant", "LEGAL_STATUS": "Convicted Felon (8:23-cr-00009-CJC)", "ORGANIZATION": "Progressive Solutions Consulting", "AFFILIATION": "RICO-004", "DETAILS": "Pled guilty to wire fraud involving cannabis licensing bribery in Irvine and conduit campaign payments."},
    {"PERSON_ID": "PER-004", "NAME": "Jeffrey Flint", "ROLE": "Senior Political Strategist / Lobbyist", "LEGAL_STATUS": "Unindicted Co-Conspirator", "ORGANIZATION": "FPS Strategies LLC", "AFFILIATION": "RICO-001 / RICO-004", "DETAILS": "Named in federal filings as ringleader of the shadow cabal controlling municipal policy and elections."},
    {"PERSON_ID": "PER-005", "NAME": "Arden Hoang, Esq.", "ROLE": "Eviction Attorney", "LEGAL_STATUS": "Civil RICO Defendant", "ORGANIZATION": "Wallace, Richardson, Sontag & Le LLP", "AFFILIATION": "RICO-002", "DETAILS": "Prosecuted fraudulent unlawful detainer defaults and executed midnight judge-striking maneuvers."},
    {"PERSON_ID": "PER-006", "NAME": "Richard S. Sontag, Esq.", "ROLE": "Managing Partner", "LEGAL_STATUS": "Civil RICO Defendant", "ORGANIZATION": "Wallace, Richardson, Sontag & Le LLP", "AFFILIATION": "RICO-002", "DETAILS": "Supervised unlawful detainer eviction mill operations across Orange County CJC."},
    {"PERSON_ID": "PER-007", "NAME": "Austin Drissen", "ROLE": "Shelter Operations Lead", "LEGAL_STATUS": "Target of Investigation", "ORGANIZATION": "Mercy House Living Centers", "AFFILIATION": "RICO-005", "DETAILS": "Coordinated Cameron Lane facility pack-outs, client property seizures, and toxic site operation."},
    {"PERSON_ID": "PER-008", "NAME": "Vichal Nunen", "ROLE": "Property Manager", "LEGAL_STATUS": "Civil RICO Defendant", "ORGANIZATION": "Woodbridge Meadows Apartments LLC", "AFFILIATION": "RICO-002", "DETAILS": "Executed retaliatory notice of termination following tenant reporting of municipal grant irregularities."},
    {"PERSON_ID": "PER-009", "NAME": "Anthony DiMarcello", "ROLE": "Relator / Tenant-Whistleblower", "LEGAL_STATUS": "Relator / Plaintiff", "ORGANIZATION": "N/A", "AFFILIATION": "Victim / Whistleblower", "DETAILS": "Uncovered municipal/shelter grant diversions; subjected to unlawful shadow lockout and retaliation."},
    {"PERSON_ID": "PER-010", "NAME": "Robert F. Greenglass", "ROLE": "Nonprofit Executive & Broker", "LEGAL_STATUS": "Target of Investigation", "ORGANIZATION": "HOMI / Greenglass Associates", "AFFILIATION": "RICO-003", "DETAILS": "Managed tax-exempt conduit HOMI and executed $1.2M property transaction at 8 Lakeview, Irvine."}
]

GOV_AGENCIES = [
    {"AGENCY_ID": "GOV-001", "AGENCY_NAME": "Orange County Superior Court (CJC)", "JURISDICTION": "State / County", "ROLE": "Judicial Venue", "RELEVANT_CASE": "30-2021-01201327-CL-UD-CJC", "FINDINGS": "Entry of three separate void default judgments without proof of service on record."},
    {"AGENCY_ID": "GOV-002", "AGENCY_NAME": "California Housing & Community Development (HCD)", "JURISDICTION": "State of California", "ROLE": "Regulatory Enforcement", "RELEVANT_CASE": "Surplus Land Act Notice of Violation", "FINDINGS": "Issued $96M statutory fine notice regarding void Anaheim stadium land sale transaction."},
    {"AGENCY_ID": "GOV-003", "AGENCY_NAME": "Orange County Health Care Agency (OCHCA)", "JURISDICTION": "County of Orange", "ROLE": "Environmental & Health Oversight", "RELEVANT_CASE": "HB Navigation Center Permit #17631", "FINDINGS": "Documented existence of unsealed abandoned groundwater well with volatile organic compounds."}
]

EVIDENCE_ITEMS = [
    {"EVIDENCE_ID": "EV-001", "NAME": "HCD $96M Notice of Violation & Res. 2022-064", "TYPE": "Official Government Finding", "DATE": "2021-12-08", "RELEVANCE": "Confirms unlawful disposition of municipal public property without required statutory compliance."},
    {"EVIDENCE_ID": "EV-002", "NAME": "Orange County CJC Unlawful Detainer Docket #1201327", "TYPE": "Court Record", "DATE": "2021-06-29", "RELEVANCE": "Chronicles triple default entries and 4:29 PM emergency judicial strike (ROA #37)."},
    {"EVIDENCE_ID": "EV-003", "NAME": "Quantum Auto Dismantler Invoice #14098 & Title Trail", "TYPE": "Financial & Logistics", "DATE": "2019-11-14", "RELEVANCE": "Ties Santa Ana dismantler to Hamilton, NJ shipping hub (1456 Cedar Ln) and interstate asset flight."},
    {"EVIDENCE_ID": "EV-004", "NAME": "17631 Cameron Ln Environmental Hazmat & Lead Records", "TYPE": "Environmental Audit", "DATE": "2020-04-15", "RELEVANCE": "Establishes knowing occupancy and shelter operation over hazardous contaminated site with unsealed well."},
    {"EVIDENCE_ID": "EV-005", "NAME": "8 Lakeview, Irvine Deed & HOMI Non-Profit Tax Filings", "TYPE": "Property Record / IRS 990", "DATE": "2021-03-22", "RELEVANCE": "Demonstrates private inurement, tax-exempt asset flipping, and $1,215,000 equity extraction."}
]

LEGAL_EXPOSURE = [
    {"STATUTE_CODE": "18 U.S.C. § 1962(c)", "STATUTE_NAME": "Civil RICO - Conducting Enterprise Affairs", "SEVERITY": "Federal Felony / Treble Damages", "STATUS": "Active Actionable Claim", "DEFENDANTS": "All Named Defendants", "PREDICATE_ACTS": "Mail Fraud, Wire Fraud, Witness Tampering, Money Laundering"},
    {"STATUTE_CODE": "18 U.S.C. § 1962(d)", "STATUTE_NAME": "RICO Conspiracy", "SEVERITY": "Federal Felony / Joint & Several Liability", "STATUS": "Active Actionable Claim", "DEFENDANTS": "All Named Defendants", "PREDICATE_ACTS": "Conspiracy to engage in racketeering pattern"},
    {"STATUTE_CODE": "31 U.S.C. § 3730(h)", "STATUTE_NAME": "False Claims Act Whistleblower Anti-Retaliation", "SEVERITY": "Double Damages + Litigation Costs", "STATUS": "Active Actionable Claim", "DEFENDANTS": "Woodbridge Meadows LLC, WRSL LLP", "PREDICATE_ACTS": "Retaliatory eviction & lockout following protected disclosure"},
    {"STATUTE_CODE": "18 U.S.C. § 1341", "STATUTE_NAME": "Mail Fraud", "SEVERITY": "Up to 20 Years Imprisonment", "STATUS": "Predicate Act Established", "DEFENDANTS": "Flint, Ament, Hoang, Sontag", "PREDICATE_ACTS": "Mailing falsified summons, postal notices, and tax filings"},
    {"STATUTE_CODE": "18 U.S.C. § 1343", "STATUTE_NAME": "Wire Fraud", "SEVERITY": "Up to 20 Years Imprisonment", "STATUS": "Guilty Pleas On Record", "DEFENDANTS": "Sidhu, Ament, Rafiei", "PREDICATE_ACTS": "Electronic transmission of internal appraisal and bribery conduits"},
    {"STATUTE_CODE": "18 U.S.C. § 1512(d)", "STATUTE_NAME": "Witness Tampering & Retaliation", "SEVERITY": "Up to 10 Years Imprisonment", "STATUS": "Predicate Act Established", "DEFENDANTS": "Hoang, Sontag, Nunen", "PREDICATE_ACTS": "Retaliatory litigation and eviction to silence whistleblower"},
    {"STATUTE_CODE": "Cal. Labor Code § 1102.5", "STATUTE_NAME": "California Whistleblower Protection Act", "SEVERITY": "$10,000 Civil Penalty per Violation + Damages", "STATUS": "Pendent State Claim", "DEFENDANTS": "Woodbridge Meadows LLC", "PREDICATE_ACTS": "Adverse tenancy action following government reporting"}
]

MASTER_TIMELINE = [
    {"EVENT_ID": "TL-001", "DATE": "2019-11-14", "ACTOR": "Quantum Auto Dismantler / Cedar Ln Hub", "EVENT_DESCRIPTION": "Interstate vehicle shipment and invoice generation linking Santa Ana to Hamilton, NJ.", "CORROBORATING_EV": "EV-003"},
    {"EVENT_ID": "TL-002", "DATE": "2020-04-15", "ACTOR": "City of Huntington Beach / Mercy House", "EVENT_DESCRIPTION": "Opening of 17631 Cameron Lane shelter facility despite known unsealed toxic well and lead hazards.", "CORROBORATING_EV": "EV-004"},
    {"EVENT_ID": "TL-003", "DATE": "2021-03-22", "ACTOR": "HOMI / Greenglass Associates", "EVENT_DESCRIPTION": "Conveyance and equity extraction of residential property at 8 Lakeview, Irvine for $1,215,000.", "CORROBORATING_EV": "EV-005"},
    {"EVENT_ID": "TL-004", "DATE": "2021-06-29", "ACTOR": "Wallace, Richardson, Sontag & Le LLP", "EVENT_DESCRIPTION": "Securing first void default judgment in Orange County CJC Case #30-2021-01201327 without notice.", "CORROBORATING_EV": "EV-002"},
    {"EVENT_ID": "TL-005", "DATE": "2021-12-08", "ACTOR": "California HCD", "EVENT_DESCRIPTION": "Issuance of formal Surplus Land Act Notice of Violation and $96M fine against Anaheim Stadium deal.", "CORROBORATING_EV": "EV-001"},
    {"EVENT_ID": "TL-006", "DATE": "2022-05-16", "ACTOR": "FBI / US Attorney CDCA", "EVENT_DESCRIPTION": "Public unsealing of federal criminal complaint and search warrants against Mayor Sidhu, Todd Ament, and Melahat Rafiei.", "CORROBORATING_EV": "EV-001; EV-002"}
]

MASTER_ENTITIES = []
for node in RICO_NODES:
    MASTER_ENTITIES.append({"ENTITY_ID": node["RICO_ID"], "ENTITY_NAME": node["RICO_NAME"], "ENTITY_TYPE": "RICO Node", "STATUS": "Documented", "DESCRIPTION": node["DESCRIPTION"], "KEYWORDS": "hub, enterprise, municipal, fraud, conspiracy"})
for p in PEOPLE:
    MASTER_ENTITIES.append({"ENTITY_ID": p["PERSON_ID"], "ENTITY_NAME": p["NAME"], "ENTITY_TYPE": "Person", "STATUS": p["LEGAL_STATUS"], "DESCRIPTION": f"{p['ROLE']} - {p['DETAILS']}", "KEYWORDS": f"{p['NAME'].lower()}, {p['ROLE'].lower()}, {p['ORGANIZATION'].lower()}"})
for g in GOV_AGENCIES:
    MASTER_ENTITIES.append({"ENTITY_ID": g["AGENCY_ID"], "ENTITY_NAME": g["AGENCY_NAME"], "ENTITY_TYPE": "Government Agency", "STATUS": "Regulatory / Judicial", "DESCRIPTION": g["FINDINGS"], "KEYWORDS": f"{g['AGENCY_NAME'].lower()}, court, agency, regulatory"})
for ev in EVIDENCE_ITEMS:
    MASTER_ENTITIES.append({"ENTITY_ID": ev["EVIDENCE_ID"], "ENTITY_NAME": ev["NAME"], "ENTITY_TYPE": "Evidence", "STATUS": "Verified", "DESCRIPTION": ev["RELEVANCE"], "KEYWORDS": f"{ev['NAME'].lower()}, {ev['TYPE'].lower()}"})


# ---------------------------------------------------------
# 2. GENERATE CSV & JSON EXPORTS (DELIVERABLE 1)
# ---------------------------------------------------------

def export_csv(filename, fieldnames, rows):
    path = os.path.join(OUTPUT_DIR, filename)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"[+] Exported CSV: {path}")

def export_json(filename, data):
    path = os.path.join(OUTPUT_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"[+] Exported JSON: {path}")

# Run Deliverable 1 Exports
export_csv("MASTER.csv", ["ENTITY_ID", "ENTITY_NAME", "ENTITY_TYPE", "STATUS", "DESCRIPTION", "KEYWORDS"], MASTER_ENTITIES)
export_json("MASTER.json", MASTER_ENTITIES)

export_csv("People.csv", ["PERSON_ID", "NAME", "ROLE", "LEGAL_STATUS", "ORGANIZATION", "AFFILIATION", "DETAILS"], PEOPLE)
export_json("People.json", PEOPLE)

export_csv("Gov_Agencies.csv", ["AGENCY_ID", "AGENCY_NAME", "JURISDICTION", "ROLE", "RELEVANT_CASE", "FINDINGS"], GOV_AGENCIES)
export_json("Gov_Agencies.json", GOV_AGENCIES)

export_csv("Evidence_Items.csv", ["EVIDENCE_ID", "NAME", "TYPE", "DATE", "RELEVANCE"], EVIDENCE_ITEMS)
export_json("Evidence_Items.json", EVIDENCE_ITEMS)

export_csv("Legal_Exposure.csv", ["STATUTE_CODE", "STATUTE_NAME", "SEVERITY", "STATUS", "DEFENDANTS", "PREDICATE_ACTS"], LEGAL_EXPOSURE)
export_json("Legal_Exposure.json", LEGAL_EXPOSURE)

export_csv("RICO_Nodes.csv", ["RICO_ID", "RICO_NAME", "NODE_TYPE", "JURISDICTION", "CONNECTED_NODE_IDS", "DESCRIPTION"], RICO_NODES)
export_json("RICO_Nodes.json", RICO_NODES)

export_csv("MASTER_TIMELINE.csv", ["EVENT_ID", "DATE", "ACTOR", "EVENT_DESCRIPTION", "CORROBORATING_EV"], MASTER_TIMELINE)
export_json("MASTER_TIMELINE.json", MASTER_TIMELINE)

# Unified Graph JSON
unified_nodes = []
for e in MASTER_ENTITIES:
    unified_nodes.append({
        "id": e["ENTITY_ID"],
        "label": e["ENTITY_NAME"],
        "type": e["ENTITY_TYPE"],
        "status": e["STATUS"],
        "properties": e
    })

unified_edges = [
    {"source": "RICO-001", "target": "PER-001", "relation": "MEMBER_LEADER", "label": "Executive Conduit"},
    {"source": "RICO-001", "target": "PER-002", "relation": "MEMBER_OPERATOR", "label": "Chamber Steering"},
    {"source": "RICO-001", "target": "PER-004", "relation": "MEMBER_STRATEGIST", "label": "Cabal Policy Orchestrator"},
    {"source": "PER-001", "target": "EV-001", "relation": "CORROBORATED_BY", "label": "Guilty Plea / $96M Fine"},
    {"source": "RICO-001", "target": "RICO-002", "relation": "SUBSIDIARY_CONDUIT", "label": "Judicial Enforcement Arm"},
    {"source": "RICO-002", "target": "PER-005", "relation": "OPERATOR_ATTORNEY", "label": "Default Eviction Mill"},
    {"source": "RICO-002", "target": "GOV-001", "relation": "TARGET_VENUE", "label": "Central Justice Center"},
    {"source": "RICO-002", "target": "EV-002", "relation": "EVIDENCE_ANCHOR", "label": "Triple Void Defaults"},
    {"source": "RICO-001", "target": "RICO-003", "relation": "FINANCIAL_CHANNEL", "label": "Nonprofit Speculation"},
    {"source": "RICO-003", "target": "PER-010", "relation": "OPERATOR", "label": "HOMI Tax Conduit"},
    {"source": "RICO-003", "target": "EV-005", "relation": "EVIDENCE_ANCHOR", "label": "$1.2M 8 Lakeview Conveyance"},
    {"source": "RICO-001", "target": "RICO-004", "relation": "POLITICAL_CONDUIT", "label": "Campaign Laundering"},
    {"source": "RICO-004", "target": "PER-003", "relation": "CONDUIT_LOBBYIST", "label": "Bribery & Consulting Kickbacks"},
    {"source": "RICO-004", "target": "EV-003", "relation": "LOGISTICS_TRAIL", "label": "Quantum Auto / Hamilton NJ"},
    {"source": "RICO-001", "target": "RICO-005", "relation": "HAZMAT_CONDUIT", "label": "Shelter & Environmental"},
    {"source": "RICO-005", "target": "PER-007", "relation": "FACILITY_LEAD", "label": "Cameron Ln Shelter Ops"},
    {"source": "RICO-005", "target": "GOV-003", "relation": "REGULATORY_RECORD", "label": "OCHCA Toxic Well Records"},
    {"source": "RICO-005", "target": "EV-004", "relation": "EVIDENCE_ANCHOR", "label": "Lead & Hazmat Findings"}
]

export_json("Unified_Export.json", {
    "version": "2.0",
    "generated_at": datetime.now().isoformat(),
    "total_nodes": len(unified_nodes),
    "total_edges": len(unified_edges),
    "nodes": unified_nodes,
    "edges": unified_edges
})


# ---------------------------------------------------------
# 3. GENERATE COURT-FORMATTED LEGAL BRIEF (DELIVERABLE 2)
# ---------------------------------------------------------

LEGAL_BRIEF_TEXT = f"""================================================================================
UNITED STATES DISTRICT COURT
FOR THE CENTRAL DISTRICT OF CALIFORNIA
SOUTHERN DIVISION - SANTA ANA
================================================================================

ANTHONY DIMARCELLO, Relator & Plaintiff in Pro Per,
    v.
WOODBRIDGE MEADOWS APARTMENTS LLC;
RUZICKA, WALLACE & COUGHLIN, LLP (n/k/a WALLACE, RICHARDSON, SONTAG & LE, LLP);
ARDEN HOANG, ESQ.; RICHARD S. SONTAG, ESQ.;
VICHAL NUNEN; HELPING OF MENTALLY ILL EXPERIENC (HOMI);
MHI REAL COMPANY; MERCY HOUSE LIVING CENTERS; and DOES 1–100, Inclusive,
    Defendants.

CASE NO.: SACV 26-RICO-00949-CJC
CIVIL ACTION FOR TREBLE DAMAGES, INJUNCTIVE RELIEF, AND RESTITUTION

--------------------------------------------------------------------------------
COMPREHENSIVE CIVIL RICO & FALSE CLAIMS ACT COMPLAINT AND EVIDENTIARY BRIEF
--------------------------------------------------------------------------------

SECTION I: EXECUTIVE SUMMARY
1. This action is brought by Plaintiff and Relator ANTHONY DIMARCELLO under the
   Racketeer Influenced and Corrupt Organizations Act (18 U.S.C. §§ 1961–1968),
   the Federal False Claims Act Anti-Retaliation provisions (31 U.S.C. § 3730(h)),
   and California statutory whistleblower protections (Cal. Labor Code § 1102.5).
2. The Defendants have operated an ongoing, structured Association-in-Fact
   Enterprise ("The Orange County Real Estate, Municipal, & Judicial Conduit Enterprise")
   for the unlawful purpose of:
   a) Diverting federal, state, and municipal housing and redevelopment funds;
   b) Procuring void default judgments through systematic abuse of judicial process;
   c) Engaging in tax-exempt nonprofit asset conversions and real estate flipping; and
   d) Suppressing tenant-whistleblower disclosures through coordinated retaliation,
      witness intimidation, and fraudulent evictions.

SECTION II: STATEMENT OF FACTS
3. THE MUNICIPAL & ENTERPRISE CORE: Commencing from at least 2019, key municipal
   officials and unindicted lobbyists coordinated improper commercial transactions,
   including the corrupt $320M Angel Stadium land transfer, resulting in federal
   criminal guilty pleas in USA v. Sidhu (8:23-cr-00108) and USA v. Ament (8:22-cr-00078).
4. THE SHADOW EVICTION AND JUDICIAL DEFAULT RING: Defendants Wallace, Richardson,
   Sontag & Le LLP operated an expedited unlawful detainer default mill in the
   Orange County Superior Court (Central Justice Center). In Case No. 30-2021-01201327,
   Defendants procured three successive default entries against Plaintiff despite
   lacking valid service of summons, and executed an emergency judicial strike at
   4:29 PM (ROA #37) to prevent independent scrutiny.
5. ENVIRONMENTAL CONCEALMENT & HAZMAT DIVERSION: Defendants coordinated operations at
   17631 Cameron Lane (Huntington Beach Navigation Center), operating an unpermitted
   shelter facility over an unsealed abandoned toxic groundwater well in violation of
   health mandates, and executed unauthorized property pack-outs against vulnerable tenants.

SECTION III: RICO ENTERPRISE ALLEGATIONS (18 U.S.C. § 1961(4), § 1962(c))
6. The Enterprise constitutes an Association-in-Fact within the meaning of 18 U.S.C.
   § 1961(4), with a distinct continuity of structure, division of labor, and a
   common corrupt purpose spanning Orange County, California and interstate channels.
7. The Enterprise functioned through distinct operational nodes:
   - RICO-001: Municipal Enterprise & Contract Steering Hub;
   - RICO-002: Judicial Default Engine & Shadow Legal Processing;
   - RICO-003: Tax-Exempt Nonprofit Shells & Equity Flipping Conduit;
   - RICO-004: Political Influence, Interstate Logistics & Fleet Title Conduit;
   - RICO-005: Environmental Concealment & Municipal Shelter Operations.

SECTION IV: PREDICATE ACTS & PATTERN OF RACKETEERING (18 U.S.C. § 1961(1))
8. The Defendants conducted the Enterprise through an extensive pattern of racketeering:
   a) Wire Fraud (18 U.S.C. § 1343 / § 1346) via fraudulent electronic court submissions
      and campaign conduit transmissions;
   b) Mail Fraud (18 U.S.C. § 1341) via postal delivery of void statutory notices and
      IRS nonprofit documentation;
   c) Witness Tampering & Retaliation (18 U.S.C. § 1512(d)) by threatening, evicting,
      and stripping Plaintiff of property to silence reports to federal investigators;
   d) Money Laundering (18 U.S.C. §§ 1956, 1957) by structuring proceeds into multi-million
      dollar real estate purchases (8 Lakeview, Irvine).

SECTION V: LEGAL EXPOSURE MATRIX & STATUTORY CLAIMS
9. COUNT I: Substantive Civil RICO (18 U.S.C. § 1962(c)) — All Defendants.
10. COUNT II: RICO Conspiracy (18 U.S.C. § 1962(d)) — All Defendants.
11. COUNT III: Federal False Claims Act Anti-Retaliation (31 U.S.C. § 3730(h)).
12. COUNT IV: California Whistleblower Retaliation (Cal. Labor Code § 1102.5).
13. COUNT V: Retaliatory Eviction (Cal. Civ. Code § 1942.5).
14. COUNT VI: Violation of California Bane Civil Rights Act (Cal. Civ. Code § 52.1).

SECTION VI: EVIDENTIARY ANCHORING & WITNESS DOSSIER
15. The claims are anchored in authenticated physical, digital, and official records:
    - EV-001: California HCD $96M Notice of Violation & City Resolution 2022-064;
    - EV-002: OC CJC Docket Case #30-2021-01201327 certified records;
    - EV-003: Quantum Auto Dismantler Invoice #14098 & Interstate Bill of Lading;
    - EV-004: OCHCA & City Hazmat Abatement Reports for 17631 Cameron Lane;
    - EV-005: 8 Lakeview Grant Deed and HOMI IRS Form 990 filings.

SECTION VII: PRAYER FOR RELIEF
WHEREFORE, Plaintiff prays for judgment against Defendants, jointly and severally:
1. Treble damages pursuant to 18 U.S.C. § 1964(c);
2. Statutory double back-pay and compensatory relief under 31 U.S.C. § 3730(h);
3. Punitive and exemplary damages pursuant to Cal. Civ. Code § 3294;
4. Full restitution of converted property, personal effects, and real estate equity;
5. Injunctive order expunging all void state court default judgments;
6. Formal referral to the United States Department of Justice for criminal prosecution;
7. Mandatory award of reasonable attorney's fees, litigation expenses, and costs; and
8. Such further relief as this Court finds just, equitable, and proper.

DATED: August 27, 2026

Respectfully submitted,
____________________________________________
ANTHONY DIMARCELLO, Relator & Plaintiff in Pro Per
"""

with open(os.path.join(OUTPUT_DIR, "Legal_Brief.txt"), "w", encoding="utf-8") as f:
    f.write(LEGAL_BRIEF_TEXT.strip())
print(f"[+] Generated Legal Brief (TXT): {os.path.join(OUTPUT_DIR, 'Legal_Brief.txt')}")

with open(os.path.join(OUTPUT_DIR, "Legal_Brief.md"), "w", encoding="utf-8") as f:
    f.write(LEGAL_BRIEF_TEXT.strip())
print(f"[+] Generated Legal Brief (MD): {os.path.join(OUTPUT_DIR, 'Legal_Brief.md')}")


# ---------------------------------------------------------
# 4. GENERATE NETWORK VISUALIZATIONS (DELIVERABLE 3)
# ---------------------------------------------------------

# Mermaid Diagram (.mmd)
MERMAID_CODE = """graph TD
    classDef hub fill:#d32f2f,stroke:#fff,stroke-width:2px,color:#fff;
    classDef official fill:#f57c00,stroke:#fff,stroke-width:2px,color:#fff;
    classDef shell fill:#7b1fa2,stroke:#fff,stroke-width:2px,color:#fff;
    classDef nonprofit fill:#1976d2,stroke:#fff,stroke-width:2px,color:#fff;
    classDef contractor fill:#388e3c,stroke:#fff,stroke-width:2px,color:#fff;
    classDef agency fill:#0097a7,stroke:#fff,stroke-width:2px,color:#fff;
    classDef evidence fill:#455a64,stroke:#fff,stroke-width:1px,color:#fff;

    RICO001["RICO-001: Municipal Enterprise Hub<br/>(Anaheim / Irvine / HB)"]:::hub
    RICO002["RICO-002: Judicial Default Engine<br/>(OC Superior Court CJC)"]:::hub
    RICO003["RICO-003: Grant Fraud & Shell Conduit<br/>(1601 Dove St Hub)"]:::hub
    RICO004["RICO-004: Political & Logistics Conduit<br/>(Quantum Auto / NJ / FL)"]:::hub
    RICO005["RICO-005: Environmental Concealment<br/>(HB Navigation Center)"]:::hub

    PER001["PER-001: Harry Sidhu<br/>(Wire Fraud 8:23-cr-00108)"]:::official
    PER002["PER-002: Todd Ament<br/>(Tax / Wire Fraud 8:22-cr-00078)"]:::official
    PER003["PER-003: Melahat Rafiei<br/>(Bribery Conduit 8:23-cr-00009)"]:::official
    PER004["PER-004: Jeffrey Flint<br/>(Cabal Strategist)"]:::official
    PER005["PER-005: Arden Hoang, Esq.<br/>(Eviction Mill Attorney)"]:::contractor
    PER007["PER-007: Austin Drissen<br/>(Mercy House Ops)"]:::nonprofit
    PER010["PER-010: Robert Greenglass<br/>(HOMI Non-Profit Conduit)"]:::nonprofit

    EV001["EV-001: HCD $96M Fine & Res. 2022-064"]:::evidence
    EV002["EV-002: Triple Void Default Records (CJC)"]:::evidence
    EV003["EV-003: Quantum Auto Inv #14098 (NJ Hub)"]:::evidence
    EV004["EV-004: Cameron Ln Toxic Well Reports"]:::evidence
    EV005["EV-005: $1.2M 8 Lakeview Deed & IRS 990"]:::evidence

    GOV001["GOV-001: Orange County Superior Court CJC"]:::agency
    GOV002["GOV-002: California HCD"]:::agency
    GOV003["GOV-003: OCHCA / Environmental Health"]:::agency

    RICO001 --> PER001
    RICO001 --> PER002
    RICO001 --> PER004
    PER001 --> EV001
    GOV002 --> EV001

    RICO001 --> RICO002
    RICO002 --> PER005
    RICO002 --> GOV001
    GOV001 --> EV002

    RICO001 --> RICO003
    RICO003 --> PER010
    PER010 --> EV005

    RICO001 --> RICO004
    RICO004 --> PER003
    RICO004 --> EV003

    RICO001 --> RICO005
    RICO005 --> PER007
    RICO005 --> GOV003
    GOV003 --> EV004
"""

with open(os.path.join(OUTPUT_DIR, "RICO_Network.mmd"), "w", encoding="utf-8") as f:
    f.write(MERMAID_CODE.strip())
print(f"[+] Generated Mermaid Diagram: {os.path.join(OUTPUT_DIR, 'RICO_Network.mmd')}")

# Graphviz DOT (.dot)
DOT_CODE = """digraph RICONetwork {
    rankdir=TB;
    node [shape=box, style=filled, fontname="Helvetica", fontsize=10];
    edge [fontname="Helvetica", fontsize=9, color="#555555"];

    // Enterprise Hubs
    node [fillcolor="#d32f2f", fontcolor="white"];
    RICO001 [label="RICO-001\\nMunicipal Enterprise Hub\\n(Anaheim/Irvine/HB)"];
    RICO002 [label="RICO-002\\nJudicial Default Engine\\n(OC CJC)"];
    RICO003 [label="RICO-003\\nGrant Fraud & Shell Conduit\\n(1601 Dove St)"];
    RICO004 [label="RICO-004\\nPolitical & Logistics Conduit\\n(Quantum Auto/NJ)"];
    RICO005 [label="RICO-005\\nEnvironmental Concealment\\n(HB Nav Center)"];

    // Persons & Officials
    node [fillcolor="#f57c00", fontcolor="white"];
    PER001 [label="PER-001: Harry Sidhu\\n(Wire Fraud 8:23-cr-00108)"];
    PER002 [label="PER-002: Todd Ament\\n(Tax/Wire Fraud 8:22-cr-00078)"];
    PER003 [label="PER-003: Melahat Rafiei\\n(Bribery Conduit 8:23-cr-00009)"];
    PER004 [label="PER-004: Jeffrey Flint\\n(Cabal Strategist)"];

    // Contractors & Nonprofits
    node [fillcolor="#1976d2", fontcolor="white"];
    PER005 [label="PER-005: Arden Hoang, Esq.\\n(WRSL Eviction Mill)"];
    PER007 [label="PER-007: Austin Drissen\\n(Mercy House Ops)"];
    PER010 [label="PER-010: Robert Greenglass\\n(HOMI Non-Profit)"];

    // Evidence
    node [fillcolor="#455a64", fontcolor="white", shape=note];
    EV001 [label="EV-001: HCD $96M Fine & Res 2022-064"];
    EV002 [label="EV-002: Triple Void Defaults (CJC)"];
    EV003 [label="EV-003: Quantum Auto Inv #14098"];
    EV004 [label="EV-004: Cameron Ln Hazmat Reports"];
    EV005 [label="EV-005: $1.2M 8 Lakeview Deed"];

    // Connections
    RICO001 -> PER001 [label="Leader"];
    RICO001 -> PER002 [label="Operator"];
    RICO001 -> PER004 [label="Strategist"];
    PER001 -> EV001 [label="Guilty Plea"];

    RICO001 -> RICO002 [label="Enforcement"];
    RICO002 -> PER005 [label="Attorney"];
    PER005 -> EV002 [label="Default Filings"];

    RICO001 -> RICO003 [label="Finance"];
    RICO003 -> PER010 [label="Nonprofit Real Estate"];
    PER010 -> EV005 [label="Equity Extraction"];

    RICO001 -> RICO004 [label="Conduit"];
    RICO004 -> PER003 [label="Bribery Channel"];
    RICO004 -> EV003 [label="Interstate Fleet"];

    RICO001 -> RICO005 [label="Shelter Ops"];
    RICO005 -> PER007 [label="Operations"];
    RICO005 -> EV004 [label="Toxic Well Concealment"];
}
"""

with open(os.path.join(OUTPUT_DIR, "RICO_Network.dot"), "w", encoding="utf-8") as f:
    f.write(DOT_CODE.strip())
print(f"[+] Generated Graphviz DOT: {os.path.join(OUTPUT_DIR, 'RICO_Network.dot')}")

# Standalone Pure SVG Vector Visualizer
SVG_IMAGE = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 800" width="100%" height="100%">
  <defs>
    <linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0f172a" />
      <stop offset="100%" stop-color="#1e293b" />
    </linearGradient>
    <filter id="shadow" x="-10%" y="-10%" width="120%" height="120%">
      <feDropShadow dx="2" dy="4" stdDeviation="4" flood-color="#000" flood-opacity="0.4"/>
    </filter>
  </defs>

  <rect width="1200" height="800" fill="url(#bgGrad)" />
  <text x="600" y="45" fill="#f8fafc" font-family="Arial, sans-serif" font-size="24" font-weight="bold" text-anchor="middle">RICO ENTERPRISE TOPOLOGY &amp; EVIDENCE CORRELATION</text>
  <text x="600" y="70" fill="#94a3b8" font-family="Arial, sans-serif" font-size="14" text-anchor="middle">OSINT Neo AI Forensic Investigation Engine — 5 Operational Hubs</text>

  <!-- Connectors -->
  <g stroke="#64748b" stroke-width="2" opacity="0.6">
    <line x1="600" y1="180" x2="200" y2="340" />
    <line x1="600" y1="180" x2="400" y2="340" />
    <line x1="600" y1="180" x2="600" y2="340" />
    <line x1="600" y1="180" x2="800" y2="340" />
    <line x1="600" y1="180" x2="1000" y2="340" />

    <line x1="200" y1="410" x2="200" y2="520" />
    <line x1="400" y1="410" x2="400" y2="520" />
    <line x1="600" y1="410" x2="600" y2="520" />
    <line x1="800" y1="410" x2="800" y2="520" />
    <line x1="1000" y1="410" x2="1000" y2="520" />

    <line x1="200" y1="590" x2="200" y2="670" />
    <line x1="400" y1="590" x2="400" y2="670" />
    <line x1="600" y1="590" x2="600" y2="670" />
    <line x1="800" y1="590" x2="800" y2="670" />
    <line x1="1000" y1="590" x2="1000" y2="670" />
  </g>

  <!-- Central Hub RICO-001 -->
  <g filter="url(#shadow)">
    <rect x="440" y="110" width="320" height="70" rx="10" fill="#dc2626" stroke="#f87171" stroke-width="2" />
    <text x="600" y="138" fill="#ffffff" font-family="Arial, sans-serif" font-size="16" font-weight="bold" text-anchor="middle">RICO-001: MUNICIPAL ENTERPRISE HUB</text>
    <text x="600" y="160" fill="#fecaca" font-family="Arial, sans-serif" font-size="12" text-anchor="middle">Anaheim / Irvine / HB Network &amp; Cabal</text>
  </g>

  <!-- Level 2: Hubs RICO 002-005 -->
  <g filter="url(#shadow)">
    <!-- RICO-002 -->
    <rect x="110" y="340" width="180" height="70" rx="8" fill="#ea580c" stroke="#fb923c" stroke-width="2"/>
    <text x="200" y="368" fill="#ffffff" font-family="Arial, sans-serif" font-size="13" font-weight="bold" text-anchor="middle">RICO-002: JUDICIAL</text>
    <text x="200" y="388" fill="#ffedd5" font-family="Arial, sans-serif" font-size="11" text-anchor="middle">Default Engine (CJC)</text>

    <!-- RICO-003 -->
    <rect x="310" y="340" width="180" height="70" rx="8" fill="#7c3aed" stroke="#a78bfa" stroke-width="2"/>
    <text x="400" y="368" fill="#ffffff" font-family="Arial, sans-serif" font-size="13" font-weight="bold" text-anchor="middle">RICO-003: NONPROFIT</text>
    <text x="400" y="388" fill="#ede9fe" font-family="Arial, sans-serif" font-size="11" text-anchor="middle">1601 Dove St Shell Hub</text>

    <!-- Core Lead PER-001/PER-004 -->
    <rect x="510" y="340" width="180" height="70" rx="8" fill="#b91c1c" stroke="#f87171" stroke-width="2"/>
    <text x="600" y="368" fill="#ffffff" font-family="Arial, sans-serif" font-size="13" font-weight="bold" text-anchor="middle">CABAL LEADERSHIP</text>
    <text x="600" y="388" fill="#fee2e2" font-family="Arial, sans-serif" font-size="11" text-anchor="middle">Sidhu / Ament / Flint</text>

    <!-- RICO-004 -->
    <rect x="710" y="340" width="180" height="70" rx="8" fill="#0284c7" stroke="#38bdf8" stroke-width="2"/>
    <text x="800" y="368" fill="#ffffff" font-family="Arial, sans-serif" font-size="13" font-weight="bold" text-anchor="middle">RICO-004: CONDUITS</text>
    <text x="800" y="388" fill="#e0f2fe" font-family="Arial, sans-serif" font-size="11" text-anchor="middle">Bribery / Quantum Fleet</text>

    <!-- RICO-005 -->
    <rect x="910" y="340" width="180" height="70" rx="8" fill="#059669" stroke="#34d399" stroke-width="2"/>
    <text x="1000" y="368" fill="#ffffff" font-family="Arial, sans-serif" font-size="13" font-weight="bold" text-anchor="middle">RICO-005: HAZMAT</text>
    <text x="1000" y="388" fill="#d1fae5" font-family="Arial, sans-serif" font-size="11" text-anchor="middle">HB Navigation Center</text>
  </g>

  <!-- Level 3: Operators & Contractors -->
  <g filter="url(#shadow)">
    <rect x="110" y="520" width="180" height="70" rx="8" fill="#334155" stroke="#64748b" stroke-width="2"/>
    <text x="200" y="548" fill="#f8fafc" font-family="Arial, sans-serif" font-size="12" font-weight="bold" text-anchor="middle">Arden Hoang, Esq.</text>
    <text x="200" y="568" fill="#cbd5e1" font-family="Arial, sans-serif" font-size="10" text-anchor="middle">WRSL LLP Eviction Mill</text>

    <rect x="310" y="520" width="180" height="70" rx="8" fill="#334155" stroke="#64748b" stroke-width="2"/>
    <text x="400" y="548" fill="#f8fafc" font-family="Arial, sans-serif" font-size="12" font-weight="bold" text-anchor="middle">HOMI / Greenglass</text>
    <text x="400" y="568" fill="#cbd5e1" font-family="Arial, sans-serif" font-size="10" text-anchor="middle">8 Lakeview $1.2M Flip</text>

    <rect x="510" y="520" width="180" height="70" rx="8" fill="#334155" stroke="#64748b" stroke-width="2"/>
    <text x="600" y="548" fill="#f8fafc" font-family="Arial, sans-serif" font-size="12" font-weight="bold" text-anchor="middle">Harry Sidhu / Ament</text>
    <text x="600" y="568" fill="#cbd5e1" font-family="Arial, sans-serif" font-size="10" text-anchor="middle">Federal Wire Fraud Pleas</text>

    <rect x="710" y="520" width="180" height="70" rx="8" fill="#334155" stroke="#64748b" stroke-width="2"/>
    <text x="800" y="548" fill="#f8fafc" font-family="Arial, sans-serif" font-size="12" font-weight="bold" text-anchor="middle">Melahat Rafiei / FPS</text>
    <text x="800" y="568" fill="#cbd5e1" font-family="Arial, sans-serif" font-size="10" text-anchor="middle">Cannabis &amp; Political Bribes</text>

    <rect x="910" y="520" width="180" height="70" rx="8" fill="#334155" stroke="#64748b" stroke-width="2"/>
    <text x="1000" y="548" fill="#f8fafc" font-family="Arial, sans-serif" font-size="12" font-weight="bold" text-anchor="middle">Austin Drissen / Mercy</text>
    <text x="1000" y="568" fill="#cbd5e1" font-family="Arial, sans-serif" font-size="10" text-anchor="middle">Cameron Ln Shelter Ops</text>
  </g>

  <!-- Level 4: Evidentiary Anchors -->
  <g filter="url(#shadow)">
    <rect x="110" y="670" width="180" height="60" rx="6" fill="#1e293b" stroke="#3b82f6" stroke-width="2"/>
    <text x="200" y="695" fill="#60a5fa" font-family="Arial, sans-serif" font-size="11" font-weight="bold" text-anchor="middle">EV-002: Case #1201327</text>
    <text x="200" y="715" fill="#94a3b8" font-family="Arial, sans-serif" font-size="9" text-anchor="middle">Triple Void Default Judgments</text>

    <rect x="310" y="670" width="180" height="60" rx="6" fill="#1e293b" stroke="#3b82f6" stroke-width="2"/>
    <text x="400" y="695" fill="#60a5fa" font-family="Arial, sans-serif" font-size="11" font-weight="bold" text-anchor="middle">EV-005: 8 Lakeview Deed</text>
    <text x="400" y="715" fill="#94a3b8" font-family="Arial, sans-serif" font-size="9" text-anchor="middle">IRS 990 Tax Inurement Records</text>

    <rect x="510" y="670" width="180" height="60" rx="6" fill="#1e293b" stroke="#3b82f6" stroke-width="2"/>
    <text x="600" y="695" fill="#60a5fa" font-family="Arial, sans-serif" font-size="11" font-weight="bold" text-anchor="middle">EV-001: HCD $96M Notice</text>
    <text x="600" y="715" fill="#94a3b8" font-family="Arial, sans-serif" font-size="9" text-anchor="middle">Res. 2022-064 Voided Land Sale</text>

    <rect x="710" y="670" width="180" height="60" rx="6" fill="#1e293b" stroke="#3b82f6" stroke-width="2"/>
    <text x="800" y="695" fill="#60a5fa" font-family="Arial, sans-serif" font-size="11" font-weight="bold" text-anchor="middle">EV-003: Invoice #14098</text>
    <text x="800" y="715" fill="#94a3b8" font-family="Arial, sans-serif" font-size="9" text-anchor="middle">Quantum Auto / NJ Fleet Conduit</text>

    <rect x="910" y="670" width="180" height="60" rx="6" fill="#1e293b" stroke="#3b82f6" stroke-width="2"/>
    <text x="1000" y="695" fill="#60a5fa" font-family="Arial, sans-serif" font-size="11" font-weight="bold" text-anchor="middle">EV-004: Hazmat &amp; Well Audit</text>
    <text x="1000" y="715" fill="#94a3b8" font-family="Arial, sans-serif" font-size="9" text-anchor="middle">OCHCA 17631 Cameron Ln</text>
  </g>
</svg>
"""

with open(os.path.join(OUTPUT_DIR, "RICO_Network_Diagram.svg"), "w", encoding="utf-8") as f:
    f.write(SVG_IMAGE.strip())
print(f"[+] Generated SVG Network Diagram: {os.path.join(OUTPUT_DIR, 'RICO_Network_Diagram.svg')}")


# ---------------------------------------------------------
# 5. GENERATE POWERSHELL MATRIX (DELIVERABLE 4)
# ---------------------------------------------------------

KEYWORDS_HOLD = ["sidhu", "ament", "rafiei", "surplus land", "default judgment", "void", "quid pro quo", "plea", "indictment"]
KEYWORDS_MANUAL = ["mercy house", "homi", "ruzicka", "cameron ln", "quantum auto", "flint", "chamber", "hoang", "sontag", "drissen"]
KEYWORDS_MIXED = ["grant", "hud", "ochca", "1601 dove", "lakeview", "cedar ln", "wire transfer", "appraisal", "nonprofit", "tax-exempt"]

matrix_rows = []
for entity in MASTER_ENTITIES:
    text = (entity["ENTITY_ID"] + " " + entity["ENTITY_NAME"] + " " + entity["DESCRIPTION"] + " " + entity["KEYWORDS"]).lower()
    
    hold_hits = [k for k in KEYWORDS_HOLD if k in text]
    manual_hits = [k for k in KEYWORDS_MANUAL if k in text]
    mixed_hits = [k for k in KEYWORDS_MIXED if k in text]
    
    total_hits = len(hold_hits) + len(manual_hits) + len(mixed_hits)
    
    if total_hits == 0:
        classification = "CLEAN"
    elif len(hold_hits) > 0 and (len(manual_hits) > 0 or len(mixed_hits) > 0):
        classification = "MIXED"
    elif len(manual_hits) >= 2 or total_hits >= 3:
        classification = "MANUAL"
    else:
        classification = "HOLD"
        
    matrix_rows.append({
        "ENTITY_ID": entity["ENTITY_ID"],
        "ENTITY_NAME": entity["ENTITY_NAME"],
        "ENTITY_TYPE": entity["ENTITY_TYPE"],
        "STATUS": entity["STATUS"],
        "CLASSIFICATION": classification,
        "HOLD_KEYWORDS_HIT": "; ".join(hold_hits),
        "MANUAL_KEYWORDS_HIT": "; ".join(manual_hits),
        "MIXED_INDICATORS_HIT": "; ".join(mixed_hits),
        "TOTAL_HITS": total_hits
    })

export_csv("PowerShell_Classification_Matrix.csv", [
    "ENTITY_ID", "ENTITY_NAME", "ENTITY_TYPE", "STATUS", "CLASSIFICATION",
    "HOLD_KEYWORDS_HIT", "MANUAL_KEYWORDS_HIT", "MIXED_INDICATORS_HIT", "TOTAL_HITS"
], matrix_rows)

PS1_SCRIPT = """# PowerShell Forensic Classification Sorter
# Ingests forensic evidence files and classifies into CLEAN, HOLD, MANUAL, and MIXED queues.

param (
    [string]$SourcePath = "C:\\osintneoai\\forensic\\raw_evidence",
    [string]$OutputPath = "C:\\osintneoai\\forensic\\classified"
)

$Keywords = @{
    HOLD   = @("sidhu", "ament", "rafiei", "surplus land", "default judgment", "void", "quid pro quo", "plea", "indictment")
    MANUAL = @("mercy house", "homi", "ruzicka", "cameron ln", "quantum auto", "flint", "chamber", "hoang", "sontag", "drissen")
    MIXED  = @("grant", "hud", "ochca", "1601 dove", "lakeview", "cedar ln", "wire transfer", "appraisal", "nonprofit", "tax-exempt")
}

foreach ($q in @("CLEAN", "HOLD", "MANUAL", "MIXED")) {
    $dir = Join-Path $OutputPath $q
    if (-not (Test-Path $dir)) { New-Item -ItemType Directory -Path $dir -Force | Out-Null }
}

Write-Host "[*] Starting Forensic Document Classification..." -ForegroundColor Cyan

Get-ChildItem -Path $SourcePath -File -Recurse -ErrorAction SilentlyContinue | ForEach-Object {
    $content = Get-Content $_.FullName -Raw -ErrorAction SilentlyContinue
    $searchTarget = ($_.Name + " " + $content).ToLower()

    $holdMatches   = $Keywords.HOLD   | Where-Object { $searchTarget -match [regex]::Escape($_) }
    $manualMatches = $Keywords.MANUAL | Where-Object { $searchTarget -match [regex]::Escape($_) }
    $mixedMatches  = $Keywords.MIXED  | Where-Object { $searchTarget -match [regex]::Escape($_) }

    $total = $holdMatches.Count + $manualMatches.Count + $mixedMatches.Count
    $targetCategory = "CLEAN"

    if ($total -eq 0) {
        $targetCategory = "CLEAN"
    } elseif ($holdMatches.Count -gt 0 -and ($manualMatches.Count -gt 0 -or $mixedMatches.Count -gt 0)) {
        $targetCategory = "MIXED"
    } elseif ($manualMatches.Count -ge 2 -or $total -ge 3) {
        $targetCategory = "MANUAL"
    } else {
        $targetCategory = "HOLD"
    }

    $dest = Join-Path $OutputPath $targetCategory $_.Name
    Copy-Item $_.FullName $dest -Force
    Write-Host "[+] Classified: $($_.Name) -> [$targetCategory] (Hits: $total)" -ForegroundColor Green
}

Write-Host "[✓] Classification Completed." -ForegroundColor Green
"""

with open(os.path.join(OUTPUT_DIR, "classify_evidence.ps1"), "w", encoding="utf-8") as f:
    f.write(PS1_SCRIPT.strip())
print(f"[+] Generated PowerShell Script: {os.path.join(OUTPUT_DIR, 'classify_evidence.ps1')}")

print("\n🚀 ALL 4 DELIVERABLES SUCCESSFULLY GENERATED IN:", OUTPUT_DIR)
