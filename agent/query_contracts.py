from google.cloud import bigquery

client = bigquery.Client(project="project-743aab84-f9a5-4ec7-954")

contract_ids = [
    '23-12957', '311705', 
    '23-13250', '315722', 
    '23-13221', '318429', 
    '311710', '24-14460', '337694',
    'CDBG', 'HOME', 'NSP'
]

print("--- Searching rico_evidence_matrix for Contract IDs and Programs ---")

# We will search the narrative, entity_name, and any other relevant fields in the matrix
query = """
SELECT entity_id, entity_name, category, authority_source, nexus_narrative
FROM `project-743aab84-f9a5-4ec7-954.ppp_rico.rico_evidence_matrix`
WHERE 
"""

# Build the OR conditions dynamically
conditions = []
for cid in contract_ids:
    conditions.append(f"UPPER(nexus_narrative) LIKE '%{cid.upper()}%'")
    conditions.append(f"UPPER(authority_source) LIKE '%{cid.upper()}%'")

query += " OR ".join(conditions)

try:
    results = client.query(query).result()
    count = 0
    for row in results:
        count += 1
        print(f"Entity ID: {row.entity_id}")
        print(f"Entity Name: {row.entity_name}")
        print(f"Category: {row.category}")
        print(f"Authority: {row.authority_source}")
        print(f"Narrative: {row.nexus_narrative}")
        print("-" * 40)
    print(f"Total Matches Found: {count}")
except Exception as e:
    print(f"Error querying rico_evidence_matrix: {e}")

print("\n--- Searching rico_matches for Contract IDs and Programs ---")
query2 = """
SELECT Entity, Match_Reason, Confidence_Score
FROM `project-743aab84-f9a5-4ec7-954.ppp_rico.rico_matches`
WHERE 
"""

conditions2 = []
for cid in contract_ids:
    conditions2.append(f"UPPER(Match_Reason) LIKE '%{cid.upper()}%'")

query2 += " OR ".join(conditions2)

try:
    results2 = client.query(query2).result()
    count2 = 0
    for row in results2:
        count2 += 1
        print(f"Entity: {row.Entity}")
        print(f"Match Reason: {row.Match_Reason}")
        print(f"Score: {row.Confidence_Score}")
        print("-" * 40)
    print(f"Total Matches Found: {count2}")
except Exception as e:
    print(f"Error querying rico_matches: {e}")
