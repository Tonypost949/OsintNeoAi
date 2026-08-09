import json
from google.cloud import bigquery

client = bigquery.Client(project="noble-beanbag-497411-m4")

# Create network map table
schema = [
    bigquery.SchemaField("node_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("node_type", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("node_name", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("layer", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("connected_to", "STRING", mode="REPEATED"),
    bigquery.SchemaField("connection_type", "STRING", mode="REPEATED"),
    bigquery.SchemaField("evidence_ref", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("ppp_total", "FLOAT64", mode="NULLABLE"),
    bigquery.SchemaField("risk_level", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("docket_number", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("notes", "STRING", mode="NULLABLE"),
]

table_id = "noble-beanbag-497411-m4.forensic_layers.rico_network_map"
try:
    client.delete_table(table_id)
except:
    pass
client.create_table(bigquery.Table(table_id, schema=schema))
print("Created forensic_layers.rico_network_map")

nodes = [
    # LAYER 1: FCA / QUI TAM
    {"node_id": "FCA-001", "node_type": "DOCKET", "node_name": "8:26-cv-00348 (Qui Tam)", "layer": "FCA_QUI_TAM",
     "connected_to": ["MERCY-001", "RICO-001", "WEAVER-003"],
     "connection_type": ["DEFENDANT", "RICO_PATTERN", "GRANT_FRAUD"],
     "evidence_ref": "fca_timeline FCA-HIT-001", "ppp_total": None, "risk_level": "CRITICAL", "docket_number": "8:26-cv-00348",
     "notes": "Federal qui tam docket against Mercy House, OC SSA, filed by DiMarcello/Knabb"},

    {"node_id": "FCA-002", "node_type": "FCA_NOTICE", "node_name": "DOJ Civil Fraud Unit Notification", "layer": "FCA_QUI_TAM",
     "connected_to": ["FCA-001", "MERCY-001", "ICWA-001"],
     "connection_type": ["SUPPLEMENTAL_DISCLOSURE"],
     "evidence_ref": "fca_timeline FCA-HIT-002", "ppp_total": None, "risk_level": "CRITICAL", "docket_number": None,
     "notes": "RICO Pattern: OC SSA / Mercy House / SPIN / Angulo NPI / ICWA-IIM Fraud"},

    {"node_id": "FCA-003", "node_type": "MANDATORY_REPORTER", "node_name": "UC System Mandatory Reporter Blast", "layer": "FCA_QUI_TAM",
     "connected_to": ["FCA-001", "ENV-001"],
     "connection_type": ["STATUTORY_NOTICE"],
     "evidence_ref": "fca_timeline FCA-HIT-011-015", "ppp_total": None, "risk_level": "CRITICAL", "docket_number": "8:2026cv00348",
     "notes": "May 6 2026: 6 UC campuses, 5 depts each — W&I 15630, PC 11165.7, RCRA 42 USC 6972"},

    {"node_id": "FCA-004", "node_type": "EPA_NOTICE", "node_name": "EPA OIG Confirmed Receipt", "layer": "FCA_QUI_TAM",
     "connected_to": ["FCA-001", "ENV-001", "ICWA-001"],
     "connection_type": ["FEDERAL_AGENCY_NOTICE"],
     "evidence_ref": "fca_timeline FCA-HIT-017", "ppp_total": None, "risk_level": "CRITICAL", "docket_number": None,
     "notes": "EPA OIG confirmed receipt of IIM tip + qui tam package on 04/14/2026"},

    # LAYER 2: MERCY HOUSE / PPP
    {"node_id": "MERCY-001", "node_type": "NONPROFIT", "node_name": "Mercy House Living Centers", "layer": "MERCY_HOUSE_PPP",
     "connected_to": ["FCA-001", "MERCY-002", "MERCY-003", "DO-001", "ENV-001", "MERCY-BOARD"],
     "connection_type": ["DEFENDANT", "PPP_RECIPIENT", "GRANT_RECIPIENT", "SITE_OPERATOR"],
     "evidence_ref": "ppp_rico.ppp_150k_plus (1.34M PPP)", "ppp_total": 1339000.0, "risk_level": "CRITICAL", "docket_number": None,
     "notes": "$54.5M FY2022 revenue, $51M govt grants, CEO Larry Haynes $186K, CMS-992-SHELTER billing fraud"},

    {"node_id": "MERCY-002", "node_type": "PPP_RECIPIENT", "node_name": "RBA Builders Inc (Bryan Pavalko)", "layer": "MERCY_HOUSE_PPP",
     "connected_to": ["MERCY-BOARD"],
     "connection_type": ["BOARD_VENDOR_CONFLICT"],
     "evidence_ref": "ppp_rico.ppp_150k_plus ($2.59M)", "ppp_total": 2590445.0, "risk_level": "HIGH", "docket_number": None,
     "notes": "Board member Bryan Pavalko — dual PPP ($1.29M x2), construction vendor for Mercy House"},

    {"node_id": "MERCY-003", "node_type": "PPP_RECIPIENT", "node_name": "Shopoff Realty Investments (Bergman/McCarty)", "layer": "MERCY_HOUSE_PPP",
     "connected_to": ["MERCY-BOARD"],
     "connection_type": ["BOARD_VENDOR_CONFLICT", "DUAL_BOARD_SEATS"],
     "evidence_ref": "ppp_rico.ppp_150k_plus ($2.3M)", "ppp_total": 2315294.0, "risk_level": "HIGH", "docket_number": None,
     "notes": "Mia Bergman + Natalie McCarty — dual board members, dual PPP, real estate firm on shelter board"},

    {"node_id": "MERCY-BOARD", "node_type": "GOVERNANCE", "node_name": "Mercy House Board (9 members, 5 self-dealing)", "layer": "MERCY_HOUSE_PPP",
     "connected_to": ["MERCY-001", "MERCY-002", "MERCY-003", "MERCY-004", "MERCY-005"],
     "connection_type": ["SELF_DEALING", "IRC_4941"],
     "evidence_ref": "meli-document-mercy-house-board-conflicts", "ppp_total": 6644596.0, "risk_level": "CRITICAL", "docket_number": None,
     "notes": "$6.6M PPP to board-connected vendors + $1.34M to Mercy House = $7.98M total"},

    {"node_id": "MERCY-004", "node_type": "PPP_RECIPIENT", "node_name": "Mladen Buntich Construction", "layer": "MERCY_HOUSE_PPP",
     "connected_to": ["MERCY-BOARD"], "connection_type": ["BOARD_VENDOR_CONFLICT"],
     "evidence_ref": "ppp_rico.ppp_150k_plus ($1.58M)", "ppp_total": 1582217.0, "risk_level": "HIGH", "docket_number": None,
     "notes": "Board member Mladen Buntich — water/sewer line construction, family holds board + advisory seats"},

    {"node_id": "MERCY-005", "node_type": "PPP_RECIPIENT", "node_name": "Cole Wealth Management (Daryl Cole)", "layer": "MERCY_HOUSE_PPP",
     "connected_to": ["MERCY-BOARD"], "connection_type": ["BOARD_VENDOR_CONFLICT", "OUT_OF_STATE"],
     "evidence_ref": "ppp_rico.ppp_150k_plus ($156K)", "ppp_total": 156640.0, "risk_level": "MEDIUM", "docket_number": None,
     "notes": "Scottsdale AZ — cross-state entity on CA nonprofit board, Exemption 4 status"},

    # LAYER 3: PPP PROPERTY CONVERSION
    {"node_id": "PPP-001", "node_type": "PPP_TO_PROPERTY", "node_name": "Stewart Industries LLC", "layer": "PPP_PROPERTY",
     "connected_to": ["PROP-001", "LENDER-BOA"],
     "connection_type": ["CROSS_STATE_PPP", "POST_PPP_ACQUISITION", "ZERO_TRANSFER"],
     "evidence_ref": "forensic_layers.ppp_property_bridge", "ppp_total": 1128327.5, "risk_level": "HIGH", "docket_number": None,
     "notes": "Battle Creek MI auto body → $1.1M PPP → 3311 BOUNTY CIR HB via $0 family transfer 05/2021"},

    {"node_id": "PPP-002", "node_type": "PPP_TO_PROPERTY", "node_name": "Triumvirate LLC", "layer": "PPP_PROPERTY",
     "connected_to": ["PROP-002", "LENDER-WY"],
     "connection_type": ["CROSS_STATE_PPP", "POST_PPP_ACQUISITION", "NAICS_MISMATCH"],
     "evidence_ref": "forensic_layers.ppp_property_bridge", "ppp_total": 1471840.0, "risk_level": "HIGH", "docket_number": None,
     "notes": "Anchorage AK hotels/skiing → $1.47M PPP → 21951 BROOKHURST ST HB $2.8M, lender Jackson WY"},

    {"node_id": "PPP-003", "node_type": "PPP_TO_PROPERTY", "node_name": "DRT Investments LLC", "layer": "PPP_PROPERTY",
     "connected_to": ["PROP-003", "ENV-001"],
     "connection_type": ["CROSS_STATE_PPP", "BEACH_BLVD_CORRIDOR"],
     "evidence_ref": "forensic_layers.ppp_property_bridge", "ppp_total": 24094.0, "risk_level": "MEDIUM", "docket_number": None,
     "notes": "AZ-based PPP → 19900 BEACH BLVD HB — directly on contamination corridor"},

    # LAYER 4: ANDREW DO / WEAVER AUDIT
    {"node_id": "DO-001", "node_type": "PUBLIC_OFFICIAL", "node_name": "Andrew Do (OC Supervisor)", "layer": "ANDREW_DO_WEAVER",
     "connected_to": ["WEAVER-001", "WEAVER-002", "WEAVER-003", "MERCY-001", "PROP-004"],
     "connection_type": ["GRANT_STEERING", "COVID_FRAUD", "POLITICAL_CORRUPTION"],
     "evidence_ref": "andrew-do-forensic-audit-phase-1.pdf", "ppp_total": None, "risk_level": "CRITICAL", "docket_number": None,
     "notes": "$8M COVID funds embezzlement, $2.2M fraudulent conveyance to Cheri Pham, decade-long alliance with Larry Haynes"},

    {"node_id": "WEAVER-001", "node_type": "PPP_RECIPIENT", "node_name": "L2T Media LLC (2T Media)", "layer": "ANDREW_DO_WEAVER",
     "connected_to": ["DO-001", "WEAVER-003", "LENDER-JPMC"],
     "connection_type": ["STEERED_GRANT", "CROSS_STATE_PPP", "OUT_OF_STATE_HUB"],
     "evidence_ref": "forensic_layers.ppp_property_bridge / Weaver Audit", "ppp_total": 1054297.0, "risk_level": "HIGH", "docket_number": None,
     "notes": "Evanston IL advertising → $1.05M PPP via JPMorgan → steered $100K ARPA via GGCF/Tam Nguyen"},

    {"node_id": "WEAVER-002", "node_type": "PPP_RECIPIENT", "node_name": "Premiere Entertainment Solutions (HB)", "layer": "ANDREW_DO_WEAVER",
     "connected_to": ["DO-001", "WEAVER-003", "PROP-004"],
     "connection_type": ["STEERED_GRANT", "TET_FESTIVAL"],
     "evidence_ref": "forensic_layers.ppp_property_bridge / Weaver Audit", "ppp_total": 41200.0, "risk_level": "MEDIUM", "docket_number": None,
     "notes": "Huntington Beach packaging → $41K PPP → Tet Festival booth sponsorships → Peter Pham/HD Ent"},

    {"node_id": "WEAVER-003", "node_type": "GRANT_INTERMEDIARY", "node_name": "Tam Nguyen / Garden Grove Community Foundation", "layer": "ANDREW_DO_WEAVER",
     "connected_to": ["DO-001", "WEAVER-001", "WEAVER-002", "PROP-CENTER"],
     "connection_type": ["GRANT_SIGNING", "PPP_INTERMEDIARY"],
     "evidence_ref": "Weaver Audit / ppp_rico (7561 Center Ave Ste 45)", "ppp_total": 1997.0, "risk_level": "HIGH", "docket_number": None,
     "notes": "Signed $100K ARPA grant to 2T Media at same office park as DNA Holdings + Brown Hubert NV shell"},

    {"node_id": "PROP-004", "node_type": "PROPERTY_SHELL", "node_name": "CP PREMIER CAPITAL LLC (Peter Pham/Cynthia Chau)", "layer": "ANDREW_DO_WEAVER",
     "connected_to": ["WEAVER-002", "PROP-CENTER"],
     "connection_type": ["ZERO_TRANSFER", "FAMILY_SHELL"],
     "evidence_ref": "rico_evidence_matrix.csv", "ppp_total": None, "risk_level": "MEDIUM", "docket_number": None,
     "notes": "Two $0 transfer properties (7100 CERRITOS, 13801 SHIRLEY) from Pham family, mail 2614 Orchard Tustin"},

    # LAYER 5: CONVERGENCE POINTS
    {"node_id": "PROP-CENTER", "node_type": "CONVERGENCE", "node_name": "7561 Center Ave Office Park", "layer": "CONVERGENCE",
     "connected_to": ["PROP-005", "PROP-006", "WEAVER-003", "DO-001"],
     "connection_type": ["PHYSICAL_CONVERGENCE", "SHELL_CLUSTER"],
     "evidence_ref": "ppp_rico.hb_llcs", "ppp_total": None, "risk_level": "HIGH", "docket_number": None,
     "notes": "DNA Holdings $725K (Unit J1), Brown Hubert NV shell (Unit D1, $0), Tam Nguyen PPP (Ste 45)"},

    {"node_id": "PROP-005", "node_type": "PROPERTY", "node_name": "DYLAN & ANDREW HOLDINGS LLC", "layer": "CONVERGENCE",
     "connected_to": ["PROP-CENTER"], "connection_type": ["OUT_OF_STATE_MAIL"],
     "evidence_ref": "ppp_rico.hb_llcs (7561 Center Ave #J1, $725K)", "ppp_total": None, "risk_level": "MEDIUM", "docket_number": None,
     "notes": "Mail at 15822 GARNET ST WESTMINSTER — purchased 05/2022 at same office park as Tam Nguyen PPP"},

    {"node_id": "PROP-006", "node_type": "PROPERTY_SHELL", "node_name": "BROWN HUBERT LLC (NV shell)", "layer": "CONVERGENCE",
     "connected_to": ["PROP-CENTER", "NV-HUB"],
     "connection_type": ["NV_SHELL", "ZERO_TRANSFER", "SAME_OFFICE_PARK"],
     "evidence_ref": "ppp_rico.hb_llcs (7561 Center Ave #D1, $0)", "ppp_total": None, "risk_level": "HIGH", "docket_number": None,
     "notes": "PO BOX 531604 HENDERSON NV, CORPORATE CREATIONS NETWORK INC, formed 03/15/2021"},

    # LAYER 6: ICWA/IIM
    {"node_id": "ICWA-001", "node_type": "TRIBAL_TRUST", "node_name": "ICWA/IIM Trust Fund Abuse ($200M)", "layer": "ICWA_IIM",
     "connected_to": ["FCA-002", "FCA-004", "OCSSA"],
     "connection_type": ["TRUST_MISAPPROPRIATION", "ICWA_NON_COMPLIANCE"],
     "evidence_ref": "gmail_index (IIM Account Misappropriation Tip)", "ppp_total": None, "risk_level": "CRITICAL", "docket_number": None,
     "notes": "OC SSA foster care trustee petitions, $200M IIM trust fund abuse, DOI/EPA/FBI/NARF notified"},

    {"node_id": "OCSSA", "node_type": "GOVERNMENT_AGENCY", "node_name": "Orange County Social Services Agency", "layer": "ICWA_IIM",
     "connected_to": ["ICWA-001", "FCA-001", "MERCY-001"],
     "connection_type": ["COMMON_FIDUCIARY"],
     "evidence_ref": "fca_timeline / gmail_index", "ppp_total": None, "risk_level": "CRITICAL", "docket_number": None,
     "notes": "Common fiduciary for both IIM trust accounts (Native foster children) and homeless shelter grants (Mercy House)"},

    # LAYER 7: ENVIRONMENTAL
    {"node_id": "ENV-001", "node_type": "ENVIRONMENTAL", "node_name": "HBNC Cr-VI Contamination (49x limit)", "layer": "ENVIRONMENTAL",
     "connected_to": ["FCA-001", "FCA-003", "MERCY-001", "PROP-007"],
     "connection_type": ["TOXIC_SITE", "CLOSURE_FRAUD"],
     "evidence_ref": "GeoTracker T10000018579 / HBNC_Formal_Complaint", "ppp_total": None, "risk_level": "CRITICAL", "docket_number": None,
     "notes": "17642 Beach Blvd closed as 'paved lot for tents' with ZERO cleanup 08/2020; must be reevaluated for land use change; 4 child deaths, 279 medical emergencies"},

    {"node_id": "PROP-007", "node_type": "ENVIRONMENTAL", "node_name": "G&M Oil Co #124 — 17472 Beach Blvd", "layer": "ENVIRONMENTAL",
     "connected_to": ["ENV-001"],
     "connection_type": ["ADJACENT_UST"],
     "evidence_ref": "forensic_layers.geotracker_ust", "ppp_total": None, "risk_level": "MEDIUM", "docket_number": None,
     "notes": "Active UST facility one block from contaminated Navigation Center footprint"},

    # LAYER 8: LENDERS
    {"node_id": "LENDER-BOA", "node_type": "LENDER", "node_name": "Bank of America NA", "layer": "LENDERS",
     "connected_to": ["PPP-001"], "connection_type": ["REPEAT_LENDER"],
     "evidence_ref": "ppp_rico", "ppp_total": None, "risk_level": "LOW", "docket_number": None,
     "notes": "Stewart Industries — 2 loans, same lender"},

    {"node_id": "LENDER-JPMC", "node_type": "LENDER", "node_name": "JPMorgan Chase Bank", "layer": "LENDERS",
     "connected_to": ["WEAVER-001", "BURNS-001"], "connection_type": ["REPEAT_LENDER"],
     "evidence_ref": "ppp_rico", "ppp_total": None, "risk_level": "LOW", "docket_number": None,
     "notes": "L2T Media + Burns Entertainment — Evanston IL hub"},

    {"node_id": "LENDER-WY", "node_type": "LENDER", "node_name": "Bank of Jackson Hole Trust (WY)", "layer": "LENDERS",
     "connected_to": ["PPP-002"], "connection_type": ["RESORT_HOSPITALITY"],
     "evidence_ref": "ppp_rico", "ppp_total": None, "risk_level": "LOW", "docket_number": None,
     "notes": "Triumvirate LLC — resort/hospitality banking nexus"},

    {"node_id": "NV-HUB", "node_type": "SHELL_FORMATION", "node_name": "Nevada Shell Formation Pipeline", "layer": "LENDERS",
     "connected_to": ["PROP-006", "PROP-CENTER"],
     "connection_type": ["CORPORATE_CREATIONS_NETWORK"],
     "evidence_ref": "ppp_rico.hb_llcs", "ppp_total": None, "risk_level": "HIGH", "docket_number": None,
     "notes": "42 NV shells at 3225 MCLEOD DR #777; same formation service used by Brown Hubert at 7561 Center Ave"},
]

errors = client.insert_rows_json(table_id, nodes)
if errors:
    print(f"Errors: {errors}")
else:
    print(f"Inserted {len(nodes)} nodes into rico_network_map")

# Verify by layer
for row in client.query(f"SELECT layer, COUNT(*) as cnt FROM {table_id} GROUP BY layer ORDER BY cnt DESC").result():
    print(f"  {row.layer}: {row.cnt} nodes")

total = list(client.query(f"SELECT COUNT(*) as c FROM {table_id}").result())[0].c
print(f"\nTotal network nodes: {total}")
