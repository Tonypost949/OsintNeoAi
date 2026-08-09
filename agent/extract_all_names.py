import os
import re
import csv
from google.cloud import bigquery

OUTPUT_CSV = 'MASTER_TARGET_NAMES.csv'
names_set = set()
data_rows = []

def add_name(name, source, context=""):
    name = name.strip().upper()
    # Filter out empty or obviously invalid names
    if len(name) < 4 or " LLC" in name or " INC" in name or name == "NAME":
        return
    if name not in names_set:
        names_set.add(name)
        data_rows.append({"Name": name, "Source": source, "Context": context})

# 1. Parse local TruthFinder text files
print("Parsing local files...")

# Parsing tf_output.txt
try:
    with open('tf_output.txt', 'r', encoding='utf-8') as f:
        content = f.read()
        
        # Look for "Name <Person>"
        name_matches = re.findall(r'Name\s+([A-Za-z\s]+)', content)
        for nm in name_matches:
            add_name(nm, 'tf_output.txt', 'TruthFinder Name field')
            
        # Look for "<Person> and <Person> may have"
        assoc_matches = re.findall(r'([A-Za-z\s]+)\s+and\s+([A-Za-z\s]+)\s+may\s+have', content)
        for p1, p2 in assoc_matches:
            add_name(p1, 'tf_output.txt', 'TruthFinder Association')
            add_name(p2, 'tf_output.txt', 'TruthFinder Association')
            
        # Look for file names like DonnettaLWilburn-TruthFinderReport.pdf
        file_matches = re.findall(r'([A-Za-z]+)-TruthFinderReport', content)
        for nm in file_matches:
            add_name(nm, 'tf_output.txt', 'TruthFinder Filename')

except FileNotFoundError:
    print("tf_output.txt not found.")

# Parsing downloaded_TruthFinder_Reports_for_Property_Residents.txt
try:
    with open('downloaded_TruthFinder_Reports_for_Property_Residents.txt', 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
        name_matches = re.findall(r'Name:\s*([A-Za-z\s]+)', content, re.IGNORECASE)
        for nm in name_matches:
            add_name(nm, 'downloaded_TruthFinder_Reports.txt', 'TruthFinder Name field')
except FileNotFoundError:
    print("downloaded_TruthFinder_Reports_for_Property_Residents.txt not found.")


# 2. Extract from BigQuery PPP Holes
print("Querying BigQuery for PPP names at high-density holes (>= 15 loans)...")
client = bigquery.Client()

query = """
SELECT BorrowerName, BorrowerAddress, BorrowerCity, BorrowerState, COUNT(*) OVER(PARTITION BY BorrowerAddress) as loan_count
FROM `project-743aab84-f9a5-4ec7-954.ppp_rico.ppp_up_to_150k`
WHERE BorrowerAddress IN (
    SELECT BorrowerAddress
    FROM `project-743aab84-f9a5-4ec7-954.ppp_rico.ppp_up_to_150k`
    WHERE BorrowerAddress IS NOT NULL AND BorrowerAddress != ''
    GROUP BY BorrowerAddress
    HAVING COUNT(*) >= 15
)
LIMIT 10000
"""

try:
    query_job = client.query(query)
    results = query_job.result()
    for row in results:
        b_name = str(row['BorrowerName']).upper().strip()
        if not any(b_name.endswith(x) for x in [' LLC', ' INC', ' CORP', ' CO', ' INC.', ' L.L.C.', ' LLC.']):
            context = f"PPP Loan at {row['BorrowerAddress']}, {row['BorrowerCity']} {row['BorrowerState']} (Cluster of {row['loan_count']})"
            add_name(b_name, 'BigQuery PPP', context)
except Exception as e:
    print(f"BigQuery error: {e}")


# 3. Write to CSV
print(f"Writing {len(data_rows)} names to {OUTPUT_CSV}...")
with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=["Name", "Source", "Context"])
    writer.writeheader()
    writer.writerows(data_rows)

print("Done!")
