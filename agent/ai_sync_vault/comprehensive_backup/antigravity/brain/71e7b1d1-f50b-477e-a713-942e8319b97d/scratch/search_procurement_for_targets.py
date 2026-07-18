import pandas as pd
import re

csv_path = r"C:\Users\HP\OneDrive\Documents\opencode_work\oc_procurement_index.csv"
df = pd.read_csv(csv_path)

print(f"Total projects in index CSV: {len(df)}")

targets = {
    "Triumvirate": r"triumvirate",
    "Stewart Industries": r"stewart\s+industries",
    "L2T Media": r"l2t\s+media",
    "Shea Homes/Shay Holmes": r"shea\s+homes|shay\s+holmes|shea\s+properties",
    "Mercy House": r"mercy\s+house",
    "Century Housing": r"century\s+housing",
    "Gilbert": r"gilbert",
    "Barnes": r"barnes",
    "Conway": r"conway",
    "Nunez": r"nunez",
    "Katana": r"katana",
    "Kroll": r"kroll"
}

results = []
for name, pattern in targets.items():
    matches_title = df[df['title'].str.contains(pattern, case=False, na=False)]
    matches_desc = df[df['description'].str.contains(pattern, case=False, na=False)]
    
    combined_indices = set(matches_title.index).union(set(matches_desc.index))
    print(f"Target '{name}': {len(combined_indices)} matches")
    
    for idx in combined_indices:
        row = df.loc[idx]
        match_info = {
            "target": name,
            "numeric_id": row["numeric_id"],
            "project_id": row["project_id"],
            "title": row["title"],
            "status": row["status"],
            "release_date": row["release_date"],
            "url": row["url"],
            "description_snippet": row["description"][:300] if isinstance(row["description"], str) else ""
        }
        results.append(match_info)
        print(f"  - Match found: ID={row['project_id']} | Title={row['title']}")

# Save matches to a JSON file
output_path = r"C:\Users\HP\.gemini\antigravity\brain\71e7b1d1-f50b-477e-a713-942e8319b97d\scratch\procurement_target_matches.json"
import json
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2)

print(f"\nSaved {len(results)} matches to procurement_target_matches.json")
