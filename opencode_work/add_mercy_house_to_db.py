import sqlite3

db = r'C:\Users\HP\OneDrive\Documents\opencode_work\master_index_v2.db'
conn = sqlite3.connect(db)
c = conn.cursor()

# Add Mercy House Living Centers
c.execute("""
INSERT OR IGNORE INTO nodes (node_id, node_type, label, primary_auth, status, notes)
VALUES (?, ?, ?, ?, ?, ?)
""", (
    'ORG_MERCY_HOUSE',
    'ORG',
    'Mercy House Living Centers',
    'AUTH_HUD',
    'ACTIVE',
    '501(c)(3) nonprofit homeless shelter operator. CEO Larry Haynes (since 1990). 600+ staff. FY2024 revenue: $74.2M, expenses: $69.6M, net assets: +$4.6M. County of Orange = 33% of contributions/grants. HUD CoC grants. CHDO entity EIN 20-4122028. ACLU 2020 lawsuit (sexual battery, negligence). Lost Costa Mesa $2.38M contract May 2026. Audit finding 2023-002: $1.5M revenue understated/liabilities overstated due to grant revenue misclassification.'
))

# Add Mercy House CHDO
c.execute("""
INSERT OR IGNORE INTO nodes (node_id, node_type, label, primary_auth, status, notes)
VALUES (?, ?, ?, ?, ?, ?)
""", (
    'ORG_MERCY_HOUSE_CHDO',
    'ORG',
    'Mercy House CHDO Inc',
    'AUTH_HUD',
    'ACTIVE',
    'Community Housing Development Organization (CHDO). EIN 20-4122028. CEO Larry Haynes draws additional compensation here. Routes real estate and LIHTC deals. Sold Vagabond Inn Oxnard to Casa Aliento LP for $15M Sep 2023 (loss $11,500). Seller carryback note $13.5M. May 2024 real estate sale $927K (gain $296K). Funded by government loans for property acquisition/rehabilitation.'
))

conn.commit()
print("Added Mercy House and CHDO nodes")

# Add relationships to node_relationships
rels = [
    ('ORG_MERCY_HOUSE', 'ORG_MERCY_HOUSE_CHDO', 'controls', None, 'VALID', 'Mercy House Living Centers controls CHDO entity; Haynes draws compensation from both'),
]

for from_node, to_node, relationship, auth_basis, strength, notes in rels:
    c.execute("""
    INSERT OR IGNORE INTO node_relationships (from_node, to_node, relationship, auth_basis, strength, notes)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (from_node, to_node, relationship, auth_basis, strength, notes))

conn.commit()
print(f"Added {len(rels)} relationships")

# Verify
c.execute("SELECT node_id, label, node_type FROM nodes WHERE node_id LIKE '%MERCY%'")
print("\nNodes added:")
for row in c.fetchall():
    print(f"  {row}")

conn.close()
print("\nDone!")
